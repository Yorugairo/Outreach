from __future__ import annotations

import json

import pytest

from content.video_engine.src.services import editor_studio as studio
from content.video_engine.src.services.editor_studio import (
    EditorStudioError,
    start,
    status,
    stop,
)


class FakeProcessTable:
    """A tiny process world: pids, names, listening ports."""

    def __init__(self):
        self.processes: dict[int, str] = {}
        self.ports: set[int] = set()
        self.next_pid = 4000
        self.spawned: list[list[str]] = []
        self.killed: list[int] = []

    def spawn(self, command, cwd, stderr_path):
        self.spawned.append(command)
        pid = self.next_pid
        self.next_pid += 1
        self.processes[pid] = "node.exe"
        return pid


@pytest.fixture()
def world(monkeypatch, tmp_path):
    table = FakeProcessTable()
    monkeypatch.setattr(studio, "STATE_DIR", tmp_path / "console-state")
    monkeypatch.setattr(studio, "STATE_FILE", tmp_path / "console-state" / "studio.pid.json")
    monkeypatch.setattr(studio, "STDERR_LOG", tmp_path / "console-state" / "studio.stderr.log")
    monkeypatch.setattr(studio, "EDITOR_DIR", tmp_path / "editor")
    (tmp_path / "editor").mkdir()
    monkeypatch.setattr(studio, "_spawn", table.spawn)
    monkeypatch.setattr(studio, "_process_alive", lambda pid: pid in table.processes)
    monkeypatch.setattr(studio, "_process_name", lambda pid: table.processes.get(pid))
    monkeypatch.setattr(
        studio, "_kill_tree",
        lambda pid: (table.killed.append(pid), table.processes.pop(pid, None)),
    )
    monkeypatch.setattr(studio, "_port_open", lambda port: port in table.ports)
    monkeypatch.setattr(studio.shutil, "which", lambda name: "C:/fake/npm.cmd")
    monkeypatch.setattr(studio.time, "sleep", lambda s: None)
    return table


def test_start_records_pid_port_and_identity(world):
    state = start(port=3000)

    assert state["state"] == "starting"
    record = json.loads(studio.STATE_FILE.read_text(encoding="utf-8"))
    assert record["pid"] == 4000
    assert record["port"] == 3000
    assert record["process_name"] == "node.exe"
    assert world.spawned[0][1:] == ["run", "start", "--", "--port", "3000"]


def test_status_reports_serving_once_the_port_answers(world):
    start()
    world.ports.add(3000)

    state = status()

    assert state["state"] == "serving"
    assert state["url"] == "http://127.0.0.1:3000"


def test_a_second_start_while_up_is_a_noop(world):
    start()
    world.ports.add(3000)

    again = start()

    assert again["state"] == "serving"
    assert len(world.spawned) == 1, "no second npm process"


def test_a_dead_pid_reads_failed_with_the_stderr_tail(world):
    start()
    world.processes.clear()
    studio.STDERR_LOG.write_text("Error: port already in use\n", encoding="utf-8")

    state = status()

    assert state["state"] == "failed"
    assert "port already in use" in state["stderr"]


def test_a_reused_pid_is_stale_never_serving(world):
    """The machine rebooted; something else now owns the recorded pid."""

    start()
    world.processes[4000] = "chrome.exe"
    world.ports.add(3000)

    state = status()

    assert state["state"] == "stale"
    assert "chrome.exe" in state["detail"]


def test_stop_kills_the_tree_and_proves_death(world):
    start()

    state = stop()

    assert state["state"] == "stopped"
    assert world.killed == [4000]
    assert not studio.STATE_FILE.exists()


def test_a_survivor_raises_rather_than_lying(world, monkeypatch):
    start()
    monkeypatch.setattr(studio, "_kill_tree", lambda pid: None)  # refuses to die
    # Bound the wait loop: monotonic jumps straight past the deadline.
    ticks = iter([0.0, 100.0, 200.0])
    monkeypatch.setattr(studio.time, "monotonic", lambda: next(ticks))

    with pytest.raises(EditorStudioError) as excinfo:
        stop()

    assert "survived" in " ".join(excinfo.value.errors)


def test_missing_npm_is_a_named_error_not_a_stack_trace(world, monkeypatch):
    monkeypatch.setattr(studio.shutil, "which", lambda name: None)

    with pytest.raises(EditorStudioError) as excinfo:
        start()

    assert "npm is not on PATH" in " ".join(excinfo.value.errors)


def test_status_never_spawns(world):
    status()
    status()

    assert world.spawned == []

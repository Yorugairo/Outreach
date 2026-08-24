"""Remotion Studio lifecycle: start, stop, status — and prove death.

The console and the editor stay two processes (P16: one *surface*, not one
program); this service owns the process half. Its rules:

- **Stop kills the process tree** and verifies the pid is gone before
  returning — an orphaned node.exe on Windows is the failure this module
  exists to prevent.
- **A pid file is a claim, not a fact.** Status matches the recorded process
  name against the live pid before believing it; a rebooted machine that
  reused the pid reads as ``stale``, never as ``serving``.
- **npm is the only interface.** No Studio internals are parsed; the editor
  package's own scripts do the work (`cli.py verify-editor` convention).

State lives at ``<engine>/runtime/console-state/studio.pid.json`` — runtime
class, disposable, never hand-edited. All process operations go through
module-level boundaries tests monkeypatch.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from content.video_engine.src.services import paths as _paths

_ENGINE_ROOT = Path(__file__).resolve().parents[2]
EDITOR_DIR = _ENGINE_ROOT / "editor"
STATE_DIR = _ENGINE_ROOT.joinpath(*_paths.CONSOLE_STATE_SUBPATH)
STATE_FILE = STATE_DIR / "studio.pid.json"
STDERR_LOG = STATE_DIR / "studio.stderr.log"

DEFAULT_PORT = 3000
_STOP_TIMEOUT_S = 10.0


class EditorStudioError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


# --- process boundaries (monkeypatched by tests) -----------------------------

def _spawn(command: list[str], cwd: Path, stderr_path: Path) -> int:
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    handle = stderr_path.open("ab")
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    process = subprocess.Popen(
        command, cwd=str(cwd), stdout=subprocess.DEVNULL, stderr=handle,
        creationflags=flags,
        start_new_session=(os.name != "nt"),
    )
    return process.pid


def _process_alive(pid: int) -> bool:
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=15,
        )
        return f'"{pid}"' in result.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _process_name(pid: int) -> str | None:
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=15,
        )
        line = result.stdout.strip().splitlines()
        if line and f'"{pid}"' in line[0]:
            return line[0].split('","')[0].strip('"')
        return None
    try:
        return Path(f"/proc/{pid}/comm").read_text().strip()
    except OSError:
        return None


def _kill_tree(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)],
                       capture_output=True, timeout=30)
    else:
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except OSError:
            pass


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.5)
        return probe.connect_ex(("127.0.0.1", port)) == 0


# --- lifecycle ---------------------------------------------------------------

def _read_state() -> dict[str, Any] | None:
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _stderr_tail(lines: int = 12) -> str:
    if not STDERR_LOG.exists():
        return ""
    text = STDERR_LOG.read_text(encoding="utf-8", errors="replace")
    return "\n".join(text.splitlines()[-lines:])


def status() -> dict[str, Any]:
    """Where Studio is, probing only — this never spawns anything."""

    record = _read_state()
    if record is None:
        return {"state": "stopped"}
    pid = int(record.get("pid") or 0)
    port = int(record.get("port") or DEFAULT_PORT)
    if not _process_alive(pid):
        return {"state": "failed", "pid": pid, "port": port,
                "stderr": _stderr_tail(),
                "detail": "the recorded pid is not running"}
    live_name = _process_name(pid)
    recorded_name = record.get("process_name")
    if recorded_name and live_name and live_name != recorded_name:
        return {"state": "stale", "pid": pid, "port": port,
                "detail": (
                    f"pid {pid} is now {live_name!r}, not the recorded "
                    f"{recorded_name!r} — a reused pid, not Studio"
                )}
    if _port_open(port):
        return {"state": "serving", "pid": pid, "port": port,
                "url": f"http://127.0.0.1:{port}",
                "started_at": record.get("started_at")}
    return {"state": "starting", "pid": pid, "port": port,
            "started_at": record.get("started_at")}


def start(port: int = DEFAULT_PORT) -> dict[str, Any]:
    """Launch ``npm run start`` in the editor; a second start is a no-op."""

    current = status()
    if current["state"] in ("serving", "starting"):
        return current

    npm = shutil.which("npm")
    if npm is None:
        raise EditorStudioError([
            "npm is not on PATH; install Node.js or open a shell where "
            "`npm --version` works"
        ])
    if not EDITOR_DIR.is_dir():
        raise EditorStudioError([f"no editor directory at {EDITOR_DIR}"])

    STDERR_LOG.unlink(missing_ok=True)
    pid = _spawn([npm, "run", "start", "--", "--port", str(port)], EDITOR_DIR, STDERR_LOG)
    record = {
        "pid": pid,
        "port": port,
        "process_name": _process_name(pid),
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return status()


def stop() -> dict[str, Any]:
    """Kill the process tree and prove the pid is gone before returning."""

    record = _read_state()
    if record is None:
        return {"state": "stopped"}
    pid = int(record.get("pid") or 0)
    if _process_alive(pid):
        _kill_tree(pid)
        deadline = time.monotonic() + _STOP_TIMEOUT_S
        while time.monotonic() < deadline:
            if not _process_alive(pid):
                break
            time.sleep(0.2)
        else:
            raise EditorStudioError([
                f"pid {pid} survived taskkill /T for {_STOP_TIMEOUT_S}s; "
                "check Task Manager before retrying"
            ])
    STATE_FILE.unlink(missing_ok=True)
    return {"state": "stopped"}

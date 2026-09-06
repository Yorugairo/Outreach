"""The bridge's environment and send path, pinned without ever touching the real CLI or the real IDE.

What is worth pinning is exactly what was hand-driven on 2026-09-06 and got guessed: which of the language
server's two ports the CLI accepts (the higher one - the lower refuses), that the CSRF token is read but
never rendered, that the same brief is the same packet folder, that registering the repository twice adds
nothing and preserves every other byte of the two `~/.gemini` files, that the conversation id is recovered
by mtime AND confirmed by title, that a packet advances by rename, and that a dry run resolves, writes and
prints without a single subprocess call.

Every process lookup is fed synthetic output or monkeypatched; no test starts a process, opens a network
connection, or reads the operator's real `~/.gemini` files.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import bridge_env as BE  # noqa: E402
import bridge_send as BS  # noqa: E402

TOKEN = "5df9d4a1c0b34e2fa1d47c2b8e6a09f3"

NETSTAT = """
Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       1240
  TCP    127.0.0.1:49634        0.0.0.0:0              LISTENING       38592
  TCP    127.0.0.1:49635        0.0.0.0:0              LISTENING       38592
  TCP    127.0.0.1:49633        0.0.0.0:0              LISTENING       7777
  TCP    127.0.0.1:52001        127.0.0.1:49635        ESTABLISHED     38592
  TCP    192.168.1.20:5040      0.0.0.0:0              LISTENING       38592
"""

TASKLIST = "\nlanguage_server.exe          38592 Console                    1    462,800 K\n"

COMMAND_LINE = (
    "C:\\Users\\Snipe\\AppData\\Local\\Programs\\antigravity\\resources\\bin\\language_server.exe "
    "--standalone --override_ide_name antigravity --https_server_port 0 "
    f"--csrf_token {TOKEN} --app_data_dir antigravity --enable_sidecars"
)


# --------------------------------------------------------------------------- ports


def test_grpc_port_is_the_higher_of_the_consecutive_pair():
    ports = BE.listening_ports(38592, netstat_output=NETSTAT)
    assert ports == [49634, 49635], "only this pid's LISTENING loopback ports"

    chosen = BE.select_grpc_port(ports)

    assert chosen["grpc"] == 49635, "the second port accepts the CLI; the first refuses"
    assert chosen["fallback"] == 49634, "the other port is exposed so a caller can fall back"
    assert chosen["consecutive"] is True


def test_port_selection_reports_when_no_consecutive_pair_exists():
    chosen = BE.select_grpc_port([49000, 51000])

    assert chosen["grpc"] == 51000
    assert chosen["fallback"] == 49000
    assert chosen["consecutive"] is False, "a guess must announce itself"


def test_single_port_has_no_fallback():
    assert BE.select_grpc_port([49635]) == {
        "grpc": 49635,
        "fallback": None,
        "ports": [49635],
        "consecutive": False,
    }


def test_pid_comes_from_the_tasklist_line():
    assert BE.find_language_server_pid(tasklist_output=TASKLIST) == 38592
    assert BE.find_language_server_pid(tasklist_output="INFO: No tasks are running.") is None


# --------------------------------------------------------------------------- the token


def test_token_is_read_from_the_command_line_and_never_rendered():
    token = BE.extract_csrf_token(COMMAND_LINE)
    assert token == TOKEN

    env = {
        "ANTIGRAVITY_LS_ADDRESS": "127.0.0.1:49635",
        "ANTIGRAVITY_CSRF_TOKEN": token,
        "ANTIGRAVITY_PROJECT_ID": "C:\\Users\\Snipe\\Downloads\\Outreach Program",
    }
    printable = BE.masked(env)

    assert printable["ANTIGRAVITY_CSRF_TOKEN"] == "<masked>"
    assert TOKEN not in str(printable), "the printed form must not carry the token"
    assert env["ANTIGRAVITY_CSRF_TOKEN"] == TOKEN, "masking returns a copy, it does not blank the env"


def test_mask_text_blanks_the_token_anywhere_in_a_line():
    line = f"agy.exe agentapi new-conversation --csrf_token={TOKEN} --title=x"

    assert TOKEN not in BE.mask_text(line, [TOKEN])
    assert BE.mask_text(line, [None, ""]) == line, "an absent secret leaves the line alone"


def test_ledger_refuses_a_secret_looking_key(tmp_path):
    with pytest.raises(ValueError):
        BE.ledger_append(tmp_path, {"lane": "gemini", "csrfToken": TOKEN})


# --------------------------------------------------------------------------- the packet


def test_packet_id_is_the_sha256_of_the_brief():
    brief = "# order\n\nDo the thing.\n"

    assert BE.packet_id(brief) == BE.packet_id(brief), "same brief, same id"
    assert len(BE.packet_id(brief)) == 64
    assert BE.packet_id(brief) != BE.packet_id(brief + " "), "a changed brief is a new packet"


def test_packet_dir_states(tmp_path):
    pid = BE.packet_id("x")

    assert BE.packet_dir(tmp_path, pid).parent.name == "queue"
    assert BE.packet_dir(tmp_path, pid, "done").parent.parent.name == "bridge"
    with pytest.raises(ValueError):
        BE.packet_dir(tmp_path, pid, "elsewhere")


def test_move_packet_renames_once_and_is_idempotent(tmp_path):
    pid = BE.packet_id("brief")
    BE.write_json(BE.packet_dir(tmp_path, pid) / "order.json", {"packetId": pid})

    moved = BE.move_packet(pid, "queue", "sent", repo=tmp_path)

    assert (moved / "order.json").exists()
    assert not BE.packet_dir(tmp_path, pid, "queue").exists(), "the rename moved it, it did not copy"
    assert BE.move_packet(pid, "queue", "sent", repo=tmp_path) == moved, "already moved is not an error"


def test_move_packet_refuses_to_clobber_a_destination(tmp_path):
    pid = BE.packet_id("brief")
    BE.write_json(BE.packet_dir(tmp_path, pid) / "order.json", {"packetId": pid})
    BE.write_json(BE.packet_dir(tmp_path, pid, "sent") / "order.json", {"packetId": pid})

    with pytest.raises(FileExistsError):
        BE.move_packet(pid, "queue", "sent", repo=tmp_path)


def test_ledger_writes_one_line_with_null_for_unknown_telemetry(tmp_path):
    BE.ledger_append(tmp_path, {"lane": "gemini", "packetId": "abc", "event": "sent"})
    BE.ledger_append(tmp_path, {"lane": "claude", "packetId": "def", "event": "replied", "secondsToReply": 12.5})

    lines = (tmp_path / "evals/BRIDGE-LOG.jsonl").read_text(encoding="utf-8").strip().splitlines()
    first, second = json.loads(lines[0]), json.loads(lines[1])

    assert len(lines) == 2
    assert first["secondsToReply"] is None, "unknown telemetry is null, never zero"
    assert first["inputTokens"] is None
    assert second["secondsToReply"] == 12.5
    assert first["ts"]


# --------------------------------------------------------------------------- registration


PROJECTS = '{\n  "projects": {\n    "c:\\\\users\\\\snipe": "snipe",\n    "c:\\\\dev": "dev"\n  },\n  "lastUsed": "snipe"\n}\n'
TRUSTED = '{\n  "c:/users/snipe": "TRUST_FOLDER",\n  "c:/dev": "TRUST_FOLDER"\n}\n'


def _gemini_home(tmp_path: Path) -> Path:
    home = tmp_path / "gemini"
    home.mkdir()
    (home / "projects.json").write_text(PROJECTS, encoding="utf-8")
    (home / "trustedFolders.json").write_text(TRUSTED, encoding="utf-8")
    return home


def test_registration_adds_both_keys_then_adds_nothing(tmp_path):
    home = _gemini_home(tmp_path)
    repo = tmp_path / "Outreach Program"
    repo.mkdir()

    first = BE.ensure_registered(repo, home)
    projects_after_first = (home / "projects.json").read_text(encoding="utf-8")
    trusted_after_first = (home / "trustedFolders.json").read_text(encoding="utf-8")
    second = BE.ensure_registered(repo, home)

    assert first["projects_added"] and first["trusted_added"]
    assert not second["projects_added"] and not second["trusted_added"], "idempotent"
    assert (home / "projects.json").read_text(encoding="utf-8") == projects_after_first, "byte-identical"
    assert (home / "trustedFolders.json").read_text(encoding="utf-8") == trusted_after_first


def test_registration_preserves_every_other_byte_and_the_key_forms(tmp_path):
    home = _gemini_home(tmp_path)
    repo = tmp_path / "Outreach Program"
    repo.mkdir()

    result = BE.ensure_registered(repo, home)

    projects = json.loads((home / "projects.json").read_text(encoding="utf-8"))
    trusted = json.loads((home / "trustedFolders.json").read_text(encoding="utf-8"))

    assert result["projects_key"].endswith("\\outreach program"), "projects.json keys are lowercase backslash paths"
    assert result["trusted_key"].endswith("/outreach program"), "trustedFolders keys are lowercase forward-slash"
    assert projects["projects"]["c:\\users\\snipe"] == "snipe", "the other entries survive"
    assert projects["lastUsed"] == "snipe", "keys beside the container survive"
    assert projects["projects"][result["projects_key"]] == "outreach-program"
    assert trusted[result["trusted_key"]] == "TRUST_FOLDER"
    assert trusted["c:/dev"] == "TRUST_FOLDER"

    raw = (home / "projects.json").read_text(encoding="utf-8")
    assert '"c:\\\\users\\\\snipe": "snipe",\n' in raw, "the untouched lines keep their exact text"


def test_registration_creates_the_files_when_absent(tmp_path):
    home = tmp_path / "fresh"
    repo = tmp_path / "Outreach Program"
    repo.mkdir()

    BE.ensure_registered(repo, home)

    assert json.loads((home / "projects.json").read_text(encoding="utf-8"))["projects"]
    assert json.loads((home / "trustedFolders.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- the conversation store


def _db(store: Path, name: str, body: bytes, mtime: float) -> Path:
    path = store / f"{name}.db"
    path.write_bytes(body)
    os.utime(path, (mtime, mtime))
    return path


def test_newest_conversation_prefers_mtime_and_confirms_the_title(tmp_path):
    store = tmp_path / "conversations"
    store.mkdir()
    _db(store, "11111111-1111-1111-1111-111111111111", b"SQLite format 3\x00dry run probe", 2_000.0)
    _db(store, "22222222-2222-2222-2222-222222222222", b"SQLite format 3\x00something else", 3_000.0)

    assert BE.newest_conversation(store=store, after_ts=1_000.0) == "22222222-2222-2222-2222-222222222222"
    assert BE.newest_conversation(store=store, after_ts=1_000.0, title="dry run probe").startswith("11111111")


def test_newest_conversation_ignores_files_older_than_the_call(tmp_path):
    store = tmp_path / "conversations"
    store.mkdir()
    _db(store, "33333333-3333-3333-3333-333333333333", b"title here", 1_000.0)

    assert BE.newest_conversation(store=store, after_ts=5_000.0) is None
    assert BE.newest_conversation(store=tmp_path / "absent", after_ts=0.0) is None


def test_newest_conversation_reads_the_write_ahead_log(tmp_path):
    store = tmp_path / "conversations"
    store.mkdir()
    db = _db(store, "44444444-4444-4444-4444-444444444444", b"SQLite format 3\x00", 4_000.0)
    db.with_suffix(".db-wal").write_bytes(b"\x00\x01wal bytes: the profile work order\x00")

    assert BE.newest_conversation(store=store, after_ts=0.0, title="the profile work order").startswith("44444444")
    assert BE.newest_conversation(store=store, after_ts=0.0, title="a title never used") is None


# --------------------------------------------------------------------------- the dry run


@pytest.fixture()
def fake_machine(monkeypatch, tmp_path):
    """The live machine, synthesised: a running language server and an untouched `~/.gemini`."""

    home = _gemini_home(tmp_path)
    monkeypatch.setattr(BE, "find_language_server_pid", lambda *a, **k: 38592)
    monkeypatch.setattr(BE, "process_command_line", lambda pid, powershell_output=None: COMMAND_LINE)
    monkeypatch.setattr(BE, "listening_ports", lambda pid, netstat_output=None, **k: [49634, 49635])
    monkeypatch.setattr(BE, "GEMINI_HOME", home)
    monkeypatch.setattr(BE, "agentapi_command", lambda env, args: ["agy.exe", "agentapi", *args])

    def _registered(repo, gemini_home=home):
        return {
            "projects_key": "k",
            "projects_added": False,
            "trusted_key": "k",
            "trusted_added": False,
        }

    monkeypatch.setattr(BE, "ensure_registered", _registered)

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("a dry run must not call any subprocess")

    monkeypatch.setattr(BS.subprocess, "run", _no_subprocess)
    return home


def _brief(tmp_path: Path) -> Path:
    path = tmp_path / "probe.md"
    path.write_text("# probe\n\nDry-run only.\n", encoding="utf-8")
    return path


def test_dry_run_prints_the_resolved_env_the_packet_and_the_command(fake_machine, tmp_path, capsys):
    brief_file = _brief(tmp_path)

    exit_code = BS.main(
        [
            "--lane", "gemini",
            "--brief-file", str(brief_file),
            "--title", "dry run",
            "--repo", str(tmp_path),
            "--dry-run",
        ]
    )
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "ANTIGRAVITY_LS_ADDRESS=127.0.0.1:49635" in out, "the higher port is the one printed"
    assert "ANTIGRAVITY_CSRF_TOKEN=<masked>" in out
    assert TOKEN not in out, "the token never reaches stdout"
    assert "ANTIGRAVITY_PROJECT_ID=" in out and str(tmp_path).replace("/", "\\") in out, "the project id is a path"
    assert "agentapi new-conversation" in out and "--title=dry run" in out
    assert f"{Path('bridge') / 'queue'}" in out, "the packet folder sits under queue/"
    assert "next:" in out


def test_dry_run_writes_the_order_and_nothing_else(fake_machine, tmp_path):
    brief_file = _brief(tmp_path)
    body = brief_file.read_text(encoding="utf-8")

    BS.main(["--lane", "gemini", "--brief-file", str(brief_file), "--title", "dry run",
             "--repo", str(tmp_path), "--dry-run", "--json"])

    folder = BE.packet_dir(tmp_path, BE.packet_id(body), "queue")
    order = json.loads((folder / "order.json").read_text(encoding="utf-8"))

    assert order["brief"] == body and order["lane"] == "gemini" and order["title"] == "dry run"
    assert order["replyShape"] == "free" and order["deadline"] > order["createdAt"]
    assert sorted(p.name for p in folder.iterdir()) == ["order.json"], "a dry run records the order only"
    assert not (tmp_path / "evals/BRIDGE-LOG.jsonl").exists(), "nothing was sent, so nothing is ledgered"
    assert TOKEN not in (folder / "order.json").read_text(encoding="utf-8")


def test_dry_run_json_shape(fake_machine, tmp_path, capsys):
    BS.main(["--lane", "gemini", "--brief-file", str(_brief(tmp_path)), "--title", "dry run",
             "--repo", str(tmp_path), "--reply-shape", "paths-written", "--model", "pro", "--dry-run", "--json"])

    payload = json.loads(capsys.readouterr().out.strip())

    assert payload["status"] == "dry-run" and payload["lane"] == "gemini"
    assert payload["conversationId"] is None and payload["packetId"]
    assert "queue" in payload["packetDir"]


def test_claude_dry_run_builds_the_packet_command(fake_machine, tmp_path, capsys):
    BS.main(["--lane", "claude", "--brief-file", str(_brief(tmp_path)), "--profile", "reviewer",
             "--repo", str(tmp_path), "--reply-shape", "review", "--dry-run"])
    out = capsys.readouterr().out

    argv = BS.claude_argv({"packetId": "abc", "brief": "body"}, "reviewer")

    assert argv[:6] == ["claude", "-p", "--output-format", "json", "--agent", "reviewer"]
    assert json.loads(argv[-1]) == {"packetId": "abc", "brief": "body"}
    assert "claude -p --output-format json --agent reviewer" in out


def test_gemini_argv_carries_model_profile_and_title():
    order = {"packetId": "x", "title": "the profile work order", "brief": "do it"}

    argv = BS.gemini_argv({"AGENTAPI": "agentapi.bat"}, order, "pro", "researcher")

    assert argv[-4:] == ["--model=pro", "--profile=researcher", "--title=the profile work order", "do it"]
    assert "new-conversation" in argv


class _Proc:
    def __init__(self, stdout: str = "", returncode: int = 0, stderr: str = ""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


BE_newest = BE.newest_conversation  # the real recovery, kept while the module attribute is patched


def test_a_real_send_records_the_conversation_moves_the_packet_and_ledgers(fake_machine, tmp_path, monkeypatch):
    """The send path with the CLI faked - the real one is the parent's live order, never a test's."""

    store = tmp_path / "conversations"
    store.mkdir()
    calls: list[list[str]] = []

    def _fake_run(argv, **kwargs):
        """Stand in for `agy.exe agentapi`: it echoes the prompt and leaves a new store entry behind."""
        calls.append(argv)
        _db(store, "55555555-5555-5555-5555-555555555555", b"SQLite\x00title: dry run", time.time())
        assert kwargs["env"]["ANTIGRAVITY_CSRF_TOKEN"] == TOKEN, "the token reaches the child by env only"
        return _Proc(stdout="prompt echoed")

    monkeypatch.setattr(BS.subprocess, "run", _fake_run)
    monkeypatch.setattr(BE, "CONVERSATION_STORE", store)
    monkeypatch.setattr(
        BE,
        "newest_conversation",
        lambda store=store, after_ts=0.0, title=None: BE_newest(store, after_ts, title),
    )

    brief_file = _brief(tmp_path)
    BS.main(["--lane", "gemini", "--brief-file", str(brief_file), "--title", "dry run", "--repo", str(tmp_path)])

    pid = BE.packet_id(brief_file.read_text(encoding="utf-8"))
    sent = BE.packet_dir(tmp_path, pid, "sent")
    record = json.loads((sent / "conversation.json").read_text(encoding="utf-8"))
    ledger = json.loads((tmp_path / "evals/BRIDGE-LOG.jsonl").read_text(encoding="utf-8").strip())

    assert len(calls) == 1, "one send, one call"
    assert not BE.packet_dir(tmp_path, pid, "queue").exists(), "the packet advanced to sent/"
    assert record["conversationId"] == "55555555-5555-5555-5555-555555555555"
    assert record["lsAddress"] == "127.0.0.1:49635"
    assert ledger["event"] == "sent" and ledger["lane"] == "gemini" and ledger["packetId"] == pid
    assert TOKEN not in (tmp_path / "evals/BRIDGE-LOG.jsonl").read_text(encoding="utf-8")
    assert TOKEN not in (sent / "conversation.json").read_text(encoding="utf-8")


def test_the_claude_lane_writes_the_reply_into_replied(fake_machine, tmp_path, monkeypatch):
    payload = {"result": "POSITION: agreed.\nDISAGREEMENTS: none.", "session_id": "abc-123",
               "usage": {"input_tokens": 1200, "output_tokens": 300}}
    monkeypatch.setattr(BS.subprocess, "run", lambda argv, **kw: _Proc(stdout=json.dumps(payload)))

    brief_file = _brief(tmp_path)
    BS.main(["--lane", "claude", "--brief-file", str(brief_file), "--repo", str(tmp_path), "--reply-shape", "review"])

    pid = BE.packet_id(brief_file.read_text(encoding="utf-8"))
    replied = BE.packet_dir(tmp_path, pid, "replied")
    ledger = json.loads((tmp_path / "evals/BRIDGE-LOG.jsonl").read_text(encoding="utf-8").strip())

    assert (replied / "reply.md").read_text(encoding="utf-8").startswith("POSITION:")
    assert json.loads((replied / "reply.json").read_text(encoding="utf-8"))["session_id"] == "abc-123"
    assert ledger["event"] == "replied" and ledger["inputTokens"] == 1200 and ledger["outputTokens"] == 300
    assert ledger["secondsToReply"] is not None


def test_a_failing_cli_leaves_the_packet_in_queue_and_reports_the_exit(fake_machine, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(BS.subprocess, "run", lambda argv, **kw: _Proc(returncode=1, stderr="connection forcibly closed"))

    brief_file = _brief(tmp_path)
    exit_code = BS.main(["--lane", "gemini", "--brief-file", str(brief_file), "--title", "dry run", "--repo", str(tmp_path)])
    out = capsys.readouterr().out

    pid = BE.packet_id(brief_file.read_text(encoding="utf-8"))

    assert exit_code == 1
    assert "agentapi exit 1" in out and "connection forcibly closed" in out
    assert BE.packet_dir(tmp_path, pid, "queue").exists(), "a failed send stays in queue/ for a retry"
    assert not (tmp_path / "evals/BRIDGE-LOG.jsonl").exists(), "nothing was sent, so nothing is ledgered"


def test_a_missing_brief_file_stops_the_send(tmp_path):
    with pytest.raises(SystemExit):
        BS.main(["--lane", "gemini", "--brief-file", str(tmp_path / "absent.md"), "--dry-run"])

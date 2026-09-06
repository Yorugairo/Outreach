"""The bridge's environment: what a lane needs before an order can be sent, discovered instead of typed.

The first Claude -> Gemini order (2026-09-06, conversation `7aaa9146`) was hand-driven: the sender read the
running Antigravity IDE's gRPC port and CSRF token off a process list, registered the repository by hand,
guessed the project-id form, and recovered the conversation id from the newest file in a store. This module
is that procedure as code, and nothing more - no model call, no agent, zero tokens (P46).

Five things live here:

  * `discover_gemini_env()` - the three `ANTIGRAVITY_*` variables plus the CLI path. The language server
    listens on two consecutive loopback ports and only the SECOND accepts the CLI (the first refuses with
    "connection forcibly closed"), so both are exposed and the caller can fall back. The CSRF token is read
    into the returned dict and is never printed, logged or written: `masked()` renders it as `<masked>` and
    is the only form that may be shown.
  * `ensure_registered()` - idempotently adds the repository to `~/.gemini/projects.json` and
    `~/.gemini/trustedFolders.json`. The insert is textual, so every other byte of those files survives.
  * `packet_id()` / `packet_dir()` / `move_packet()` - the queue is a folder state machine
    (`queue -> sent -> replied -> done`) under `docs/research/runs/bridge/`, moved by atomic rename. No
    broker, no database.
  * `ledger_append()` - one JSON line per bridge event in `evals/BRIDGE-LOG.jsonl`, mirroring
    `~/.claude/hooks/dispatch_ledger.py`: unknown telemetry is `null`, never zero, so the average of a
    column is not silently wrong.
  * `newest_conversation()` - the Antigravity CLI prints no id, so the id is the newest
    `~/.gemini/antigravity/conversations/<uuid>.db` modified after the call, confirmed by scanning the file
    (and its `-wal`) for the title bytes.

Standard library only. Windows is the measured host; the process lookups degrade to `None` elsewhere.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Iterable, Sequence

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]

GEMINI_HOME = Path.home() / ".gemini"
CONVERSATION_STORE = GEMINI_HOME / "antigravity" / "conversations"
BRAIN_ROOT = GEMINI_HOME / "antigravity" / "brain"   # brain/<id>/.system_generated/logs/transcript.jsonl - written before the .db
AGENTAPI_BAT = GEMINI_HOME / "antigravity-cli" / "bin" / "agentapi.bat"

LANGUAGE_SERVER = "language_server.exe"
MASK = "<masked>"
SECRET_KEYS = ("ANTIGRAVITY_CSRF_TOKEN",)
LOOPBACK = ("127.0.0.1", "[::1]")

BRIDGE_ROOT = Path("docs/research/runs/bridge")
STATES = ("queue", "sent", "replied", "done")
LEDGER = Path("evals/BRIDGE-LOG.jsonl")
LEDGER_EVENTS = ("sent", "replied", "followup", "tier0", "tier1", "timeout", "escalated")
TELEMETRY_KEYS = ("conversationId", "secondsToReply", "inputTokens", "outputTokens", "totalTokens")

_CSRF_RE = re.compile(r"--csrf_token[=\s]+(\S+)")
_NETSTAT_RE = re.compile(
    r"^\s*TCP\s+(?P<local>\S+):(?P<port>\d+)\s+\S+\s+LISTENING\s+(?P<pid>\d+)\s*$",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------- secrets


def masked(env: dict[str, Any], *, keys: Sequence[str] = SECRET_KEYS) -> dict[str, Any]:
    """A copy of ``env`` safe to print: every secret value replaced by ``<masked>``."""

    return {k: (MASK if k in keys and v else v) for k, v in env.items()}


def mask_text(text: str, secrets: Iterable[str | None]) -> str:
    """Blank every secret occurrence in ``text`` - used before a command line is shown."""

    out = text
    for secret in secrets:
        if secret and len(secret) >= 4:
            out = out.replace(secret, MASK)
    return out


# --------------------------------------------------------------------------- process discovery


def _run(cmd: Sequence[str]) -> str:
    try:
        done = subprocess.run(list(cmd), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return ""
    return done.stdout or ""


def find_language_server_pid(image: str = LANGUAGE_SERVER, tasklist_output: str | None = None) -> int | None:
    """The running Antigravity language server's pid, or None when it is not running."""

    text = tasklist_output
    if text is None:
        text = _run(["tasklist", "/FI", f"IMAGENAME eq {image}", "/NH"])
    pids = [int(m.group(1)) for m in re.finditer(rf"{re.escape(image)}\s+(\d+)\s", text or "")]
    return pids[0] if pids else None


def process_command_line(pid: int, powershell_output: str | None = None) -> str:
    """The full command line of ``pid`` (Win32_Process). It carries secrets - never print it raw."""

    if powershell_output is not None:
        return powershell_output.strip()
    script = f"(Get-CimInstance Win32_Process -Filter \"ProcessId={int(pid)}\").CommandLine"
    return _run(["powershell", "-NoProfile", "-Command", script]).strip()


def extract_csrf_token(command_line: str) -> str | None:
    """The `--csrf_token` value on the language server's command line."""

    match = _CSRF_RE.search(command_line or "")
    return match.group(1).strip('"') if match else None


def listening_ports(pid: int, netstat_output: str | None = None, *, loopback_only: bool = True) -> list[int]:
    """Every LISTENING TCP port held by ``pid``, ascending and de-duplicated."""

    text = netstat_output if netstat_output is not None else _run(["netstat", "-ano"])
    ports: set[int] = set()
    for line in (text or "").splitlines():
        match = _NETSTAT_RE.match(line)
        if not match or int(match.group("pid")) != int(pid):
            continue
        if loopback_only and match.group("local") not in LOOPBACK:
            continue
        ports.add(int(match.group("port")))
    return sorted(ports)


def select_grpc_port(ports: Sequence[int]) -> dict[str, Any]:
    """Pick the port the Antigravity CLI accepts.

    The language server binds two consecutive loopback ports; the higher one speaks gRPC and the lower one
    closes the connection. Both are returned so a caller can retry on the other. With no consecutive pair
    the highest port is the best guess and ``consecutive`` says so.
    """

    unique = sorted(set(int(p) for p in ports))
    if not unique:
        return {"grpc": None, "fallback": None, "ports": [], "consecutive": False}
    for lower in unique:
        if lower + 1 in unique:
            return {"grpc": lower + 1, "fallback": lower, "ports": unique, "consecutive": True}
    return {
        "grpc": unique[-1],
        "fallback": unique[-2] if len(unique) > 1 else None,
        "ports": unique,
        "consecutive": False,
    }


def project_id(repo_root: Path | str = REPO) -> str:
    """`ANTIGRAVITY_PROJECT_ID` is the repository PATH with backslashes; a project NAME fails."""

    return str(Path(repo_root).resolve()).replace("/", "\\")


def discover_gemini_env(pid: int | None = None, repo_root: Path | str = REPO) -> dict[str, Any]:
    """The environment an `agentapi` call needs, read off the running IDE.

    Every value is a string (or None when the IDE is not running) so the result can be merged straight into
    ``os.environ``. `ANTIGRAVITY_CSRF_TOKEN` is a secret: print `masked(env)`, never `env`.
    """

    server_pid = pid if pid is not None else find_language_server_pid()
    env: dict[str, Any] = {
        "ANTIGRAVITY_LS_ADDRESS": None,
        "ANTIGRAVITY_LS_ADDRESS_FALLBACK": None,
        "ANTIGRAVITY_CSRF_TOKEN": None,
        "ANTIGRAVITY_PROJECT_ID": project_id(repo_root),
        "AGENTAPI": str(AGENTAPI_BAT),
        "ANTIGRAVITY_LS_PID": str(server_pid) if server_pid else None,
    }
    if not server_pid:
        env["ANTIGRAVITY_LS_NOTE"] = f"{LANGUAGE_SERVER} not found where I looked (tasklist); start Antigravity"
        return env

    env["ANTIGRAVITY_CSRF_TOKEN"] = extract_csrf_token(process_command_line(server_pid))
    chosen = select_grpc_port(listening_ports(server_pid))
    if chosen["grpc"]:
        env["ANTIGRAVITY_LS_ADDRESS"] = f"127.0.0.1:{chosen['grpc']}"
    if chosen["fallback"]:
        env["ANTIGRAVITY_LS_ADDRESS_FALLBACK"] = f"127.0.0.1:{chosen['fallback']}"
    if not chosen["consecutive"]:
        env["ANTIGRAVITY_LS_NOTE"] = f"no consecutive port pair for pid {server_pid}; ports={chosen['ports']}"
    return env


def agentapi_command(env: dict[str, Any], args: Sequence[str]) -> list[str]:
    """Argv for the Antigravity CLI.

    `agentapi.bat` is a one-line wrapper around `agy.exe agentapi`. CreateProcess cannot execute a `.bat`
    directly, so the real executable is preferred when the wrapper names one and `cmd /c` is the fallback.
    """

    bat = Path(str(env.get("AGENTAPI") or AGENTAPI_BAT))
    exe = _agy_executable(bat)
    if exe:
        return [str(exe), "agentapi", *args]
    comspec = os.environ.get("COMSPEC", "cmd.exe")
    return [comspec, "/c", str(bat), *args]


def _agy_executable(bat: Path) -> Path | None:
    try:
        body = bat.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    match = re.search(r'"([^"]+agy\.exe)"', body) or re.search(r"(\S+agy\.exe)", body)
    if not match:
        return None
    exe = Path(match.group(1))
    return exe if exe.exists() else None


# --------------------------------------------------------------------------- registration


def ensure_registered(repo_root: Path | str = REPO, gemini_home: Path | str = GEMINI_HOME) -> dict[str, Any]:
    """Add the repository to `projects.json` and `trustedFolders.json` when absent. Idempotent.

    The insert is textual: only the new line appears in the diff, every other byte is preserved.
    """

    root = Path(repo_root).resolve()
    home = Path(gemini_home)
    slug = re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-")
    projects_key = str(root).replace("/", "\\").lower()
    trusted_key = str(root).replace("\\", "/").lower()

    added = {
        "projects": _add_key(home / "projects.json", projects_key, slug, container="projects"),
        "trustedFolders": _add_key(home / "trustedFolders.json", trusted_key, "TRUST_FOLDER"),
    }
    return {
        "projects_key": projects_key,
        "projects_added": added["projects"],
        "trusted_key": trusted_key,
        "trusted_added": added["trustedFolders"],
    }


def _add_key(path: Path, key: str, value: str, *, container: str | None = None) -> bool:
    """Insert ``key`` into the JSON object at ``container`` (or the root). True when the file changed."""

    if not path.exists():
        body = {container: {key: value}} if container else {key: value}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
        return True

    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    target = data.get(container, {}) if container else data
    if key in target:
        return False
    path.write_text(_insert_json_key(raw, key, value, container=container), encoding="utf-8")
    return True


def _insert_json_key(raw: str, key: str, value: str, *, container: str | None = None) -> str:
    """Textual insert before the closing brace of the target object; every other byte survives."""

    open_at = _object_open(raw, container)
    close_at = _matching_brace(raw, open_at)
    inner = raw[open_at + 1 : close_at]
    entry = f"{json.dumps(key)}: {json.dumps(value)}"
    indent = _entry_indent(inner)
    if inner.strip():
        head = inner.rstrip()
        tail = inner[len(head) :] or "\n"
        return f"{raw[: open_at + 1]}{head},\n{indent}{entry}{tail}{raw[close_at:]}"
    return f"{raw[: open_at + 1]}\n{indent}{entry}\n{raw[close_at:]}"


def _object_open(raw: str, container: str | None) -> int:
    if container is None:
        start = raw.find("{")
        if start < 0:
            raise ValueError("no JSON object in the file")
        return start
    marker = json.dumps(container)
    at = raw.find(marker)
    if at < 0:
        raise ValueError(f"container {container!r} not found where I looked")
    start = raw.find("{", at + len(marker))
    if start < 0:
        raise ValueError(f"container {container!r} is not an object")
    return start


def _matching_brace(raw: str, open_at: int) -> int:
    depth = 0
    in_string = False
    escaped = False
    for index in range(open_at, len(raw)):
        char = raw[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unbalanced JSON object")


def _entry_indent(inner: str, default: str = "  ") -> str:
    for line in inner.splitlines():
        if line.strip():
            return line[: len(line) - len(line.lstrip())] or default
    return default


# --------------------------------------------------------------------------- the packet queue


def packet_id(brief: str) -> str:
    """The packet id is the sha256 of the brief - the same order is the same folder, always."""

    return hashlib.sha256(brief.encode("utf-8")).hexdigest()


def packet_dir(repo: Path | str, pid: str, state: str = "queue") -> Path:
    """`docs/research/runs/bridge/<state>/<packetId>/`."""

    if state not in STATES:
        raise ValueError(f"unknown packet state {state!r}; expected one of {STATES}")
    return Path(repo) / BRIDGE_ROOT / state / pid


def move_packet(pid: str, from_state: str, to_state: str, repo: Path | str = REPO) -> Path:
    """Advance a packet by atomic rename. Idempotent: an already-moved packet returns its destination."""

    src = packet_dir(repo, pid, from_state)
    dst = packet_dir(repo, pid, to_state)
    if not src.exists():
        if dst.exists():
            return dst
        raise FileNotFoundError(f"packet {pid} not found where I looked: {src}")
    if dst.exists():
        raise FileExistsError(f"packet {pid} already in {to_state}: {dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.replace(src, dst)
    return dst


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    """Write one JSON document, parents created, newline-terminated."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


# --------------------------------------------------------------------------- the ledger


def _is_secret_key(key: str) -> bool:
    """`csrfToken` is a secret; `inputTokens` is telemetry. The plural is the tell."""

    lowered = key.lower()
    if any(word in lowered for word in ("csrf", "secret", "password", "apikey", "api_key")):
        return True
    return lowered.endswith("token") or lowered == "auth"


def ledger_append(repo: Path | str, record: dict[str, Any], ledger: Path | str = LEDGER) -> Path:
    """Append one bridge event to `evals/BRIDGE-LOG.jsonl`.

    Missing telemetry is written as ``null`` and never as zero, so a later average over the column cannot be
    quietly wrong. A secret-looking key is refused outright - the CSRF token belongs in no file. ``event`` is
    a closed vocabulary (`LEDGER_EVENTS`): a typo would split a column that the escape rate is measured on,
    so it is refused rather than written.
    """

    for key in record:
        if _is_secret_key(key):
            raise ValueError(f"refusing to ledger a secret-looking key: {key}")
    if record.get("event") not in LEDGER_EVENTS:
        raise ValueError(f"unknown ledger event {record.get('event')!r}; expected one of {LEDGER_EVENTS}")
    row: dict[str, Any] = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    row.update({key: None for key in TELEMETRY_KEYS})
    row.update(record)
    path = Path(repo) / ledger
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


# --------------------------------------------------------------------------- the conversation store


def newest_conversation(
    store: Path | str = CONVERSATION_STORE,
    after_ts: float = 0.0,
    title: str | None = None,
    brain: Path | str | None = None,
) -> str | None:
    """The conversation id the CLI just created: the newest `<uuid>.db` touched after ``after_ts``.

    The CLI echoes the prompt and prints no id, so recovery is by mtime; when a ``title`` was given it is
    confirmed by scanning the database (and its write-ahead log) for the title bytes before the id is
    accepted. Returns None when nothing matches - not found where I looked.
    """

    brain = BRAIN_ROOT if brain is None else brain
    root = Path(store)
    if not root.is_dir():
        return newest_brain_conversation(brain, after_ts, title)
    candidates = []
    for db in root.glob("*.db"):
        try:
            mtime = db.stat().st_mtime
        except OSError:
            continue
        if mtime >= after_ts:
            candidates.append((mtime, db))
    for _, db in sorted(candidates, reverse=True):
        if title and not _mentions(db, title):
            continue
        return db.stem
    return newest_brain_conversation(brain, after_ts, title)


def newest_brain_conversation(brain: Path | str = BRAIN_ROOT, after_ts: float = 0.0, title: str | None = None) -> str | None:
    """Fallback for the id: the newest `brain/<id>/.system_generated/logs/transcript.jsonl` touched after
    ``after_ts`` whose FIRST record carries the title (the CLI's prompt echo). The conversation database can
    lag the send by more than the sender waits (seen 2026-09-06: 503 databases, none matched, the transcript
    was already 7 records long), and the transcript is written first."""

    root = Path(brain)
    if not root.is_dir():
        return None
    found = []
    for tr in root.glob("*/.system_generated/logs/transcript.jsonl"):
        try:
            mtime = tr.stat().st_mtime
        except OSError:
            continue
        if mtime >= after_ts - 5:
            found.append((mtime, tr))
    for _, tr in sorted(found, reverse=True):
        try:
            with tr.open("r", encoding="utf-8") as handle:
                first = handle.readline()
        except OSError:
            continue
        if title and title not in first:
            continue
        return tr.parents[2].name
    return None


def _mentions(db: Path, title: str) -> bool:
    needle = title.encode("utf-8")
    for path in (db, db.with_suffix(".db-wal")):
        if path.exists() and _contains(path, needle):
            return True
    return False


def _contains(path: Path, needle: bytes, chunk: int = 1 << 20) -> bool:
    overlap = max(len(needle) - 1, 0)
    tail = b""
    try:
        with path.open("rb") as handle:
            while True:
                block = handle.read(chunk)
                if not block:
                    return False
                if needle in tail + block:
                    return True
                tail = (tail + block)[-overlap:] if overlap else b""
    except OSError:
        return False

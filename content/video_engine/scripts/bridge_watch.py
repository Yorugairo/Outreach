"""Wait for - or replay - one lane's reply and land it as a packet reply. No model call, zero tokens (P46).

    python content/video_engine/scripts/bridge_watch.py --lane gemini --id 7aaa9146-... --replay
    python content/video_engine/scripts/bridge_watch.py --lane gemini --id <conversationId> --packet <packetId>
    python content/video_engine/scripts/bridge_watch.py --lane claude --id <session.jsonl or uuid> --replay

`bridge_send.py` writes the order and makes the send; this is the other half - it reads the addressee's own
transcript (no polling of the CLI, no second harness) and writes three files:

  * `reply.md`    - the final text verbatim (the completion report / the last assistant message), one header
                    comment on top. Known secret values from the environment are masked; nothing else moves.
  * `steps.jsonl` - one compact line per transcript record: `step_index, type, source, created_at, tool,
                    head` (160 masked characters). A model's `thinking` is never read into any output.
  * `watch.json`  - `{lane, id, status, steps, landedAt, secondsToReply, positionLine}`.

With `--packet` the files land in the packet folder, a landed reply advances `sent -> replied` by rename,
and one `replied` or `timeout` line is appended to `evals/BRIDGE-LOG.jsonl`. Without a packet nothing is
ledgered: a replay is a read, not an event.

Reply detection, pinned against the 2026-09-06 worked example (conversation `7aaa9146`, 101 records, the
completion report at step 103):

  * gemini - the reply is the LAST `PLANNER_RESPONSE` with non-empty `content`, no `tool_calls` and status
    `DONE`, provided nothing after it is still pending (a record with `tool_calls` or a non-`DONE` status).
    An abstention that ends a turn is a reply, and the same rule catches it.
  * claude - the last `assistant` record's text blocks, joined. A `thinking` block carries no `text` key and
    is skipped by type, so it cannot reach a file.

Exit codes: 0 done, 2 timeout (the deadline passed with no reply), 3 still working (a replay of a live
conversation - outside the plan's three codes, and not an error), 1 error.

`--once` is `--replay` for a daemon (P46 T6): one read of the transcript, no polling, but the order's
deadline still binds, so a packet past it lands as `timeout` instead of `working`.

Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import bridge_env as env_mod  # noqa: E402

REPO = env_mod.REPO
LANES = ("gemini", "claude")
DEFAULT_POLL_S = 20
HEAD_CHARS = 160
DONE = "DONE"
REPLAY_ROOT = env_mod.BRIDGE_ROOT / "replay"
GEMINI_BRAIN = Path.home() / ".gemini" / "antigravity" / "brain"
CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"
CLAUDE_PROJECT_GLOB = "*agent-bridge-run-*"
STATUS_EXIT = {"done": 0, "timeout": 2, "working": 3}
SECRET_ENV_RE = re.compile(r"csrf|host_?bridge", re.IGNORECASE)
_SENDER_RE = re.compile(r"sender=(\S+)")
_POSITION = "POSITION:"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lane", choices=LANES, required=True)
    parser.add_argument("--id", required=True, help="conversation id, session uuid, or a transcript path")
    parser.add_argument("--packet", default=None, help="packetId; the packet is expected in sent/")
    parser.add_argument("--replay", action="store_true", help="read the transcript once, never poll")
    parser.add_argument("--once", action="store_true", help="one read like --replay, but the deadline still binds")
    parser.add_argument("--timeout-min", type=int, default=None, help="overrides the order's deadline")
    parser.add_argument("--poll-sec", type=int, default=DEFAULT_POLL_S)
    parser.add_argument("--out", type=Path, default=None, help="where a packet-less replay lands")
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--json", action="store_true", dest="as_json", help="print watch.json on stdout")
    return parser


# --------------------------------------------------------------------------- reading


def transcript_path(lane: str, ident: str, *, brain: Path = GEMINI_BRAIN, projects: Path = CLAUDE_PROJECTS) -> Path:
    """The file this lane writes its turn into. A path may be passed instead of an id."""

    direct = Path(ident)
    if direct.suffix == ".jsonl" or direct.is_file():
        return direct
    if lane == "gemini":
        return Path(brain) / ident / ".system_generated" / "logs" / "transcript.jsonl"
    matches = sorted(Path(projects).glob(f"{CLAUDE_PROJECT_GLOB}/{ident}.jsonl"))
    return matches[0] if matches else Path(projects) / CLAUDE_PROJECT_GLOB / f"{ident}.jsonl"


def read_records(path: Path | str) -> list[dict[str, Any]]:
    """Every JSON object in a JSONL transcript; a half-written tail line is skipped, not fatal."""

    target = Path(path)
    if not target.is_file():
        return []
    records: list[dict[str, Any]] = []
    with target.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict):
                records.append(record)
    return records


def environment_secrets(environ: dict[str, str] | None = None) -> list[str]:
    """Every csrf / host-bridge value in the environment - masked out of anything we write."""

    source = os.environ if environ is None else environ
    return [v for k, v in source.items() if SECRET_ENV_RE.search(k) and v and len(v) >= 8]


def head_text(content: str | None, secrets: Iterable[str | None] = ()) -> str:
    """A record's first HEAD_CHARS characters, whitespace collapsed and secrets masked before the cut."""

    text = " ".join((content or "").split())
    return env_mod.mask_text(text, secrets)[:HEAD_CHARS]


# --------------------------------------------------------------------------- the gemini lane


def _pending(record: dict[str, Any]) -> bool:
    """A record that says the turn is not over: a tool call, or a status other than DONE."""

    return bool(record.get("tool_calls")) or (record.get("status") or DONE) != DONE


# P46 T8 (2026-09-07 03:00): a turn can END on a placeholder while a background task runs - "Waiting for task-289." as a
# DONE planner record with no tool call. That is not a reply; the watcher landed two of them and the daemon repaired a reply
# that never was. A wait placeholder is pending, and so is everything before the task it waits on finishes.
_WAIT_PLACEHOLDER = re.compile(r"^\s*(?:please\s+)?wait(?:ing)?\s+(?:for|on)\s+task-\d+", re.IGNORECASE)


def _placeholder(record: dict[str, Any]) -> bool:
    return record.get("type") == "PLANNER_RESPONSE" and bool(_WAIT_PLACEHOLDER.match((record.get("content") or "").strip()))


def gemini_reply(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """The last completed PLANNER_RESPONSE with text and no tool call, if nothing after it is pending - and a
    "Waiting for task-N" placeholder is never that reply."""

    index = None
    for position, record in enumerate(records):
        if record.get("type") != "PLANNER_RESPONSE" or _pending(record) or _placeholder(record):
            continue
        if (record.get("content") or "").strip():
            index = position
    if index is None or any(_pending(r) or _placeholder(r) for r in records[index + 1 :]):
        return {"status": "working", "text": "", "record": None}
    return {"status": "done", "text": (records[index].get("content") or "").strip(), "record": records[index]}


def is_user_message(record: dict[str, Any]) -> bool:
    """A turn the operator sent.

    The first is `USER_INPUT`; a `send-message` correction arrives as a `SYSTEM_MESSAGE` whose envelope
    reads `sender=system`, where a tool result reads `sender=<conversationId>/task-NN`.
    """

    if record.get("type") == "USER_INPUT":
        return True
    if record.get("type") != "SYSTEM_MESSAGE":
        return False
    match = _SENDER_RE.search(record.get("content") or "")
    return bool(match) and match.group(1) == "system"


def _tool_names(tool_calls: Any) -> list[str]:
    if not isinstance(tool_calls, list):
        return []
    return [c.get("name") for c in tool_calls if isinstance(c, dict) and c.get("name")]


def gemini_steps(records: Sequence[dict[str, Any]], secrets: Iterable[str | None] = ()) -> list[dict[str, Any]]:
    """One compact line per record. `thinking` is not read; `user` marks the operator's own turns."""

    steps = []
    for position, record in enumerate(records):
        step: dict[str, Any] = {
            "step_index": record.get("step_index", position),
            "type": record.get("type"),
            "source": record.get("source"),
            "created_at": record.get("created_at"),
            "tool": _tool_names(record.get("tool_calls")),
            "head": head_text(record.get("content"), secrets),
        }
        if is_user_message(record):
            step["user"] = True
        steps.append(step)
    return steps


# --------------------------------------------------------------------------- the claude lane


def _blocks(record: dict[str, Any]) -> list[dict[str, Any]]:
    content = (record.get("message") or {}).get("content")
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def _texts(record: dict[str, Any]) -> list[str]:
    """Text blocks only - a `thinking` block carries no `text` key and is skipped by type."""

    return [b.get("text") or "" for b in _blocks(record) if b.get("type") == "text" and (b.get("text") or "").strip()]


def claude_reply(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """The last assistant record that actually said something."""

    for record in reversed(list(records)):
        if record.get("type") != "assistant":
            continue
        texts = _texts(record)
        if texts:
            return {"status": "done", "text": "\n\n".join(t.strip() for t in texts), "record": record}
    return {"status": "working", "text": "", "record": None}


def claude_steps(records: Sequence[dict[str, Any]], secrets: Iterable[str | None] = ()) -> list[dict[str, Any]]:
    """One compact line per session record, mirroring the gemini columns."""

    steps = []
    for position, record in enumerate(records):
        message = record.get("message") or {}
        content = message.get("content")
        text = content if isinstance(content, str) else " ".join(_texts(record))
        steps.append(
            {
                "step_index": position,
                "type": record.get("type"),
                "source": message.get("role") or record.get("userType"),
                "created_at": record.get("timestamp"),
                "tool": [b.get("name") for b in _blocks(record) if b.get("type") == "tool_use" and b.get("name")],
                "head": head_text(text, secrets),
            }
        )
    return steps


def claude_usage(record: dict[str, Any] | None) -> dict[str, Any]:
    """Tokens where the transcript exposes them; null, never zero, where it does not."""

    usage = ((record or {}).get("message") or {}).get("usage") or {}
    return {"inputTokens": usage.get("input_tokens"), "outputTokens": usage.get("output_tokens")}


READERS: dict[str, Callable[[Sequence[dict[str, Any]]], dict[str, Any]]] = {
    "gemini": gemini_reply,
    "claude": claude_reply,
}
STEPPERS: dict[str, Callable[..., list[dict[str, Any]]]] = {"gemini": gemini_steps, "claude": claude_steps}


# --------------------------------------------------------------------------- the reply's shape


def position_line(text: str, lane: str) -> str | None:
    """Astra's grammar: the POSITION line. On the gemini lane only when the reply opens with it."""

    if not text:
        return None
    if lane == "gemini" and not text.lstrip().upper().startswith(_POSITION):
        return None
    for line in text.splitlines():
        if line.strip().upper().startswith(_POSITION):
            return line.strip()
    return None


def render_reply(lane: str, conversation_id: str, text: str, landed_at: str) -> str:
    """The reply verbatim under one header comment naming the lane, the conversation and the landing."""

    header = f"<!-- lane: {lane}; conversationId: {conversation_id}; landedAt: {landed_at} -->"
    body = text if text.endswith("\n") else text + "\n"
    return f"{header}\n\n{body}"


def write_steps(path: Path, steps: Sequence[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for step in steps:
            handle.write(json.dumps(step, ensure_ascii=False, separators=(",", ":")) + "\n")
    return path


# --------------------------------------------------------------------------- the packet


def locate_packet(repo: Path | str, packet: str) -> tuple[Path, str]:
    """The packet folder and the state it sits in; `sent/` is where a watched packet belongs."""

    for state in ("sent", "queue", "replied", "done"):
        folder = env_mod.packet_dir(repo, packet, state)
        if folder.exists():
            return folder, state
    raise SystemExit(f"packet {packet} not found where I looked: {env_mod.packet_dir(repo, packet, 'sent')}")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def packet_sent_at(folder: Path) -> str | None:
    """When the order went out.

    `bridge_send.py` records `sentAt` in `conversation.json` on a real send, not in `order.json` - the
    order carries `createdAt` and `deadline`. Both are read, newest contract first.
    """

    conversation = _read_json(folder / "conversation.json")
    order = _read_json(folder / "order.json")
    return conversation.get("sentAt") or order.get("sentAt") or order.get("createdAt")


def parse_time(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        stamp = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return stamp if stamp.tzinfo else stamp.astimezone()


def seconds_to_reply(sent_at: str | None, landed_at: str) -> float | None:
    start, end = parse_time(sent_at), parse_time(landed_at)
    if not start or not end:
        return None
    return round((end - start).total_seconds(), 1)


def resolve_deadline(timeout_min: int | None, order: dict[str, Any], started: dt.datetime) -> dt.datetime | None:
    """`--timeout-min` counts from now and wins; otherwise the order's own `deadline` binds."""

    if timeout_min is not None:
        return started + dt.timedelta(minutes=max(timeout_min, 0))
    return parse_time(order.get("deadline"))


# --------------------------------------------------------------------------- the watch


def _poll(
    lane: str,
    path: Path,
    deadline: dt.datetime | None,
    poll_sec: int,
    replay: bool,
    once: bool = False,
) -> tuple[list, dict, str]:
    """Read until the reply lands, the deadline passes, or exactly once when replaying.

    `--replay` is a read of history and never times out; `--once` is one tick of a daemon, so a packet past
    its deadline is a `timeout` on the first read and nothing sleeps either way.
    """

    reader = READERS[lane]
    while True:
        records = read_records(path)
        reply = reader(records)
        if reply["status"] == "done" or (replay and not once):
            return records, reply, reply["status"]
        if deadline and dt.datetime.now().astimezone() >= deadline:
            return records, reply, "timeout"
        if once:
            return records, reply, reply["status"]
        time.sleep(max(int(poll_sec), 1))


def _out_dir(args: argparse.Namespace, folder: Path | None) -> Path:
    """The packet folder when there is one, else `--out`, else the gitignored replay folder."""

    if folder is not None:
        return folder
    if args.out:
        return Path(args.out)
    slug = Path(args.id).stem if Path(args.id).suffix else str(args.id)
    return Path(args.repo) / REPLAY_ROOT / slug


def _write_outputs(
    out_dir: Path,
    args: argparse.Namespace,
    reply: dict[str, Any],
    steps: Sequence[dict[str, Any]],
    watch: dict[str, Any],
    secrets: Sequence[str],
) -> dict[str, Path]:
    """`reply.md` only when there is a reply; `steps.jsonl` and `watch.json` always."""

    out_dir.mkdir(parents=True, exist_ok=True)
    written = {
        "steps": write_steps(out_dir / "steps.jsonl", steps),
        "watch": env_mod.write_json(out_dir / "watch.json", watch),
    }
    if reply["text"]:
        body = render_reply(args.lane, str(args.id), env_mod.mask_text(reply["text"], secrets), watch["landedAt"])
        (out_dir / "reply.md").write_text(body, encoding="utf-8")
        written["reply"] = out_dir / "reply.md"
    return written


def _ledger(args: argparse.Namespace, order: dict[str, Any], watch: dict[str, Any], usage: dict[str, Any]) -> None:
    """One line per watched packet; a replay without a packet is a read and appends nothing."""

    env_mod.ledger_append(
        args.repo,
        {
            "lane": args.lane,
            "packetId": args.packet,
            "conversationId": str(args.id),
            "event": "replied" if watch["status"] == "done" else "timeout",
            "replyShape": order.get("replyShape"),
            "secondsToReply": watch["secondsToReply"],
            "steps": watch["steps"],
            **usage,
        },
    )


def run_watch(args: argparse.Namespace) -> dict[str, Any]:
    """Poll (or replay) one conversation, write the three files, advance the packet, ledger the event."""

    path = transcript_path(args.lane, args.id)
    secrets = environment_secrets()
    started = dt.datetime.now().astimezone()
    folder: Path | None = None
    state = None
    order: dict[str, Any] = {}
    if args.packet:
        folder, state = locate_packet(args.repo, args.packet)
        order = _read_json(folder / "order.json")

    deadline = resolve_deadline(args.timeout_min, order, started)
    once = bool(getattr(args, "once", False))
    records, reply, status = _poll(args.lane, path, deadline, args.poll_sec, args.replay or once, once)
    landed_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    steps = STEPPERS[args.lane](records, secrets)
    watch = {
        "lane": args.lane,
        "id": str(args.id),
        "status": status,
        "steps": len(steps),
        "landedAt": landed_at,
        "secondsToReply": seconds_to_reply(packet_sent_at(folder), landed_at) if folder else None,
        "positionLine": position_line(reply["text"], args.lane),
    }

    written = _write_outputs(_out_dir(args, folder), args, reply, steps, watch, secrets)
    if folder is not None and status == "done" and state in ("sent", "queue"):
        folder = env_mod.move_packet(args.packet, state, "replied", repo=args.repo)
        written = {name: folder / target.name for name, target in written.items()}
    if args.packet and status != "working":
        # a `working` read is not an event: a daemon ticking every minute would otherwise write one
        # `timeout` line per tick for a lane that is simply still thinking.
        _ledger(args, order, watch, claude_usage(reply["record"]) if args.lane == "claude" else {})
    return {
        "watch": watch,
        "paths": {name: str(target) for name, target in written.items()},
        "packetDir": str(folder) if folder else None,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_watch(args)
    watch = result["watch"]
    if args.as_json:
        print(json.dumps(watch, ensure_ascii=False))
    else:
        print(f"status: {watch['status']} steps={watch['steps']} secondsToReply={watch['secondsToReply']}")
        print(f"reply: {result['paths'].get('reply', result['paths']['watch'])}")
    return STATUS_EXIT.get(watch["status"], 1)


if __name__ == "__main__":
    raise SystemExit(main())

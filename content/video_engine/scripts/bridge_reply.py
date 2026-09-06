"""Answer a landed reply on the SAME conversation - the correction, the missing source, the nudge.

    python content/video_engine/scripts/bridge_reply.py --packet <packetId> --text "the source is docs/x.md"
    python content/video_engine/scripts/bridge_reply.py --packet <packetId> --text-file correction.md --dry-run

The first Claude -> Gemini order (2026-09-06) only completed because a SECOND message told the lane where
the source lived. That message was hand-sent and left no trace. This is that message as a command: it
resumes the conversation recorded when the order went out (`send-message <id>` for Gemini, `claude -p
--resume <id>` for Claude), writes the follow-up into the packet folder as `followups/<n>.md`, and appends
one `followup` line to `evals/BRIDGE-LOG.jsonl`.

Only a packet in `replied/` (a reply being answered) or `sent/` (a nudge on an unanswered order) can be
replied to. A packet in `queue/` never went out - that is `bridge_send.py`'s job - and one in `done/` is
closed. A replied packet returns to `sent/`: a new round has started and the watcher lands the next reply.

`--dry-run` does everything except the send, the move and the ledger line: it prints the command with the
CSRF token masked and the follow-up path it would write. The token is never printed, written or ledgered.

Standard library only; no model call is made by this script (P46: the bridge is an adapter, not a harness).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import bridge_env as env_mod  # noqa: E402

REPO = env_mod.REPO
ANSWERABLE = ("replied", "sent")
NEXT_STATE = "sent"
GEMINI_REQUIRED = ("ANTIGRAVITY_LS_ADDRESS", "ANTIGRAVITY_CSRF_TOKEN")
FOLLOWUP_DIR = "followups"
DRY_RUN_NEXT = "next: send for real (drop --dry-run)"


class BridgeReplyError(RuntimeError):
    """A refusal the operator can act on: wrong state, no conversation, empty text, a failed send."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--packet", required=True, help="the packetId (the folder name under bridge/<state>/)")
    text = parser.add_mutually_exclusive_group(required=True)
    text.add_argument("--text", default=None, help="the follow-up, inline")
    text.add_argument("--text-file", default=None, type=Path, help="the follow-up, from a file")
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--dry-run", action="store_true", help="resolve and print, never call the CLI")
    parser.add_argument("--json", action="store_true", dest="as_json", help="one JSON object on stdout")
    return parser


# --------------------------------------------------------------------------- what we are answering


def read_text(args: argparse.Namespace) -> str:
    """The follow-up body, from `--text` or `--text-file`. An empty follow-up is not a message."""

    if args.text_file is not None:
        if not args.text_file.exists():
            raise BridgeReplyError(f"follow-up not found where I looked: {args.text_file}")
        body = args.text_file.read_text(encoding="utf-8")
    else:
        body = args.text or ""
    if not body.strip():
        raise BridgeReplyError("the follow-up is empty; say something or drop the send")
    return body


def locate_packet(repo: Path | str, packet: str) -> tuple[Path, str]:
    """The packet folder and its state, or a refusal naming where it actually sits."""

    found = {state: env_mod.packet_dir(repo, packet, state) for state in env_mod.STATES}
    for state in ANSWERABLE:
        if found[state].is_dir():
            return found[state], state
    for state in env_mod.STATES:
        if found[state].is_dir():
            raise BridgeReplyError(
                f"packet {packet} is in {state}/, which cannot be replied to; "
                f"{'send it with bridge_send.py' if state == 'queue' else 'it is closed'}"
            )
    looked = ", ".join(str(found[state]) for state in env_mod.STATES)
    raise BridgeReplyError(f"packet {packet} not found where I looked: {looked}")


def read_order(folder: Path) -> dict[str, Any]:
    path = folder / "order.json"
    if not path.exists():
        raise BridgeReplyError(f"order.json not found where I looked: {path}")
    try:
        order = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise BridgeReplyError(f"order.json is not readable JSON: {path} ({exc})") from exc
    if not isinstance(order, dict):
        raise BridgeReplyError(f"order.json is not an object: {path}")
    return order


def conversation_id(folder: Path, order: dict[str, Any]) -> str:
    """The conversation to resume: the order's, else the send record's (`bridge_send.py` writes it there)."""

    candidates: list[Any] = [order.get("conversationId")]
    for name, key in (("conversation.json", "conversationId"), ("reply.json", "session_id")):
        path = folder / name
        if path.exists():
            try:
                candidates.append(json.loads(path.read_text(encoding="utf-8")).get(key))
            except (ValueError, AttributeError):
                continue
    for candidate in candidates:
        if candidate:
            return str(candidate)
    raise BridgeReplyError(
        f"no conversationId in {folder / 'order.json'} (nor conversation.json/reply.json); "
        "a packet that never went out is sent with bridge_send.py, not replied to"
    )


def next_followup(folder: Path) -> int:
    """Follow-ups are numbered from 1 by what is already on disk, so a rerun cannot overwrite one."""

    existing = sorted((folder / FOLLOWUP_DIR).glob("*.md")) if (folder / FOLLOWUP_DIR).is_dir() else []
    return len(existing) + 1


def followup_path(folder: Path, number: int) -> Path:
    return folder / FOLLOWUP_DIR / f"{number:02d}.md"


# --------------------------------------------------------------------------- the send


def quote(argv: Sequence[str]) -> str:
    return " ".join(f'"{a}"' if (" " in a or not a) else a for a in argv)


def gemini_argv(env: dict[str, Any], conversation: str, text: str) -> list[str]:
    return env_mod.agentapi_command(env, ["send-message", conversation, text])


def claude_argv(conversation: str, text: str) -> list[str]:
    return ["claude", "-p", "--resume", conversation, "--output-format", "json", text]


def resolve(lane: str, conversation: str, text: str, repo: Path) -> tuple[list[str], dict[str, Any] | None, str]:
    """Argv, the environment it needs (gemini only) and the line that may be shown - masked."""

    if lane == "claude":
        argv = claude_argv(conversation, text)
        return argv, None, f"command: {quote(argv[:-1])} <text {len(text)} chars>"
    env = env_mod.discover_gemini_env(repo_root=repo)
    argv = gemini_argv(env, conversation, text)
    shown = env_mod.mask_text(quote(argv), [env.get("ANTIGRAVITY_CSRF_TOKEN")])
    return argv, env, f"command: {shown}"


def send(argv: Sequence[str], env: dict[str, Any] | None, repo: Path) -> None:
    """One send. A non-zero exit is a refusal, so nothing downstream records a message that never landed."""

    if env is not None:
        missing = [key for key in GEMINI_REQUIRED if not env.get(key)]
        if missing:
            raise BridgeReplyError(
                f"cannot send: {', '.join(missing)} not found where I looked (is Antigravity running?)"
            )
    proc = subprocess.run(
        list(argv),
        capture_output=True,
        text=True,
        env=_process_env(env) if env is not None else None,
        cwd=str(repo) if env is None else None,
    )
    if proc.returncode != 0:
        secrets = [env.get("ANTIGRAVITY_CSRF_TOKEN")] if env else []
        detail = env_mod.mask_text((proc.stderr or proc.stdout or "").strip(), secrets)
        raise BridgeReplyError(f"send exit {proc.returncode}: {detail[:400]}")


def _process_env(env: dict[str, Any]) -> dict[str, str]:
    merged = dict(os.environ)
    for key in ("ANTIGRAVITY_LS_ADDRESS", "ANTIGRAVITY_CSRF_TOKEN", "ANTIGRAVITY_PROJECT_ID"):
        value = env.get(key)
        if value:
            merged[key] = str(value)
    return merged


# --------------------------------------------------------------------------- the paper trail


def record_followup(
    folder: Path,
    order: dict[str, Any],
    number: int,
    lane: str,
    conversation: str,
    text: str,
    sent_at: str,
) -> None:
    """`followups/<n>.md` (header + the text verbatim) and the two counters on the order."""

    path = followup_path(folder, number)
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"<!-- sentAt: {sent_at}; lane: {lane}; conversationId: {conversation} -->"
    path.write_text(f"{header}\n{text}", encoding="utf-8")

    updated = dict(order)
    updated["followups"] = number
    updated["lastFollowupAt"] = sent_at
    env_mod.write_json(folder / "order.json", updated)


def ledger_followup(repo: Path, lane: str, packet: str, conversation: str, number: int, text: str, sent_at: str) -> None:
    env_mod.ledger_append(
        repo,
        {
            "lane": lane,
            "packetId": packet,
            "conversationId": conversation,
            "sentAt": sent_at,
            "event": "followup",
            "followup": number,
            "chars": len(text),
        },
    )


# --------------------------------------------------------------------------- entrypoint


def run(args: argparse.Namespace, lines: list[str]) -> dict[str, Any]:
    text = read_text(args)
    folder, state = locate_packet(args.repo, args.packet)
    order = read_order(folder)
    lane = order.get("lane") or "gemini"
    conversation = conversation_id(folder, order)
    number = next_followup(folder)

    lines.insert(0, f"packetId {args.packet[:12]} lane {lane} state {state} followup {number:02d}")
    argv, env, shown = resolve(lane, conversation, text, args.repo)
    lines.append(shown)

    landing = env_mod.packet_dir(args.repo, args.packet, NEXT_STATE)
    result = {
        "packetId": args.packet,
        "lane": lane,
        "conversationId": conversation,
        "followup": number,
        "path": str(followup_path(landing, number)),
        "sent": False,
    }
    if args.dry_run:
        lines.append(f"followup: {result['path']} ({len(text)} chars, not written)")
        return result

    send(argv, env, args.repo)
    sent_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    record_followup(folder, order, number, lane, conversation, text, sent_at)
    if state != NEXT_STATE:
        env_mod.move_packet(args.packet, state, NEXT_STATE, repo=args.repo)
    ledger_followup(args.repo, lane, args.packet, conversation, number, text, sent_at)

    result["sent"] = True
    lines.append(f"followup: {result['path']}")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    lines: list[str] = []
    try:
        result = run(args, lines)
    except BridgeReplyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False))
        return 0
    for line in lines:
        print(line)
    if args.dry_run:
        print(DRY_RUN_NEXT)
    else:
        print(f"next: bridge_watch.py --lane {result['lane']} --id {result['conversationId']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

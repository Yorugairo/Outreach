"""Send one order to one lane. An order is a file AND a send - this writes the file, then makes the send.

    python content/video_engine/scripts/bridge_send.py --lane gemini --brief-file order.md --title "profiles" --dry-run
    python content/video_engine/scripts/bridge_send.py --lane gemini --brief-file order.md --title "profiles" --model pro
    python content/video_engine/scripts/bridge_send.py --lane claude --brief-file review.md --reply-shape review --profile reviewer

The packet folder is `docs/research/runs/bridge/<state>/<packetId>/` and the packet id is the sha256 of the
brief, so re-sending the same brief lands in the same folder and a duplicate is visible rather than silent.
The queue is a folder state machine: `queue -> sent` for Gemini (the reply arrives later, `bridge_watch.py`
moves it on), `queue -> replied` for Claude (a headless `-p` run answers in the same call).

`--dry-run` does everything except the CLI call: it writes the order, resolves the environment, and prints
the environment with the CSRF token as `<masked>`, the packet path and the exact command line. The token is
never written to a file, never appended to the ledger and never printed - masked or nothing.

Standard library only; no model call is made by this script (P46: the bridge is an adapter, not a harness).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Sequence

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import bridge_env as env_mod  # noqa: E402

REPO = env_mod.REPO
LANES = ("gemini", "claude")
REPLY_SHAPES = ("paths-written", "contract-block", "report-landed", "review", "test-run", "free")
DEFAULT_DEADLINE_MIN = 60
BRIEF_CAP_BYTES = 6 * 1024
CLOCK_SLACK_S = 5.0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lane", choices=LANES, required=True)
    parser.add_argument("--brief-file", required=True, type=Path, help="the order body, markdown, <= 6 KB")
    parser.add_argument("--title", default=None, help="conversation title; also how the id is confirmed")
    parser.add_argument("--profile", default=None, help="gemini: --profile=<p>; claude: --agent <p>")
    parser.add_argument("--model", default=None, help="gemini model, e.g. pro")
    parser.add_argument("--reply-shape", choices=REPLY_SHAPES, default="free")
    parser.add_argument("--deadline-min", type=int, default=DEFAULT_DEADLINE_MIN)
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--dry-run", action="store_true", help="resolve and write, never call the CLI")
    parser.add_argument("--json", action="store_true", dest="as_json", help="one JSON object on stdout")
    return parser


def read_brief(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"brief not found where I looked: {path}")
    brief = path.read_text(encoding="utf-8")
    if not brief.strip():
        raise SystemExit(f"brief is empty: {path}")
    return brief


def build_order(args: argparse.Namespace, brief: str) -> dict[str, Any]:
    created = dt.datetime.now().astimezone()
    deadline = created + dt.timedelta(minutes=max(args.deadline_min, 0))
    return {
        "packetId": env_mod.packet_id(brief),
        "lane": args.lane,
        "title": args.title or args.brief_file.stem,
        "replyShape": args.reply_shape,
        "deadline": deadline.isoformat(timespec="seconds"),
        "brief": brief,
        "createdAt": created.isoformat(timespec="seconds"),
    }


def quote(argv: Sequence[str]) -> str:
    return " ".join(f'"{a}"' if (" " in a or not a) else a for a in argv)


# --------------------------------------------------------------------------- the gemini lane


def gemini_argv(env: dict[str, Any], order: dict[str, Any], model: str | None, profile: str | None) -> list[str]:
    args = ["new-conversation"]
    if model:
        args.append(f"--model={model}")
    if profile:
        args.append(f"--profile={profile}")
    args.append(f"--title={order['title']}")
    args.append(order["brief"])
    return env_mod.agentapi_command(env, args)


def resolve_gemini(args: argparse.Namespace, order: dict[str, Any], lines: list[str]) -> tuple[dict[str, Any], list[str]]:
    """Read the running IDE, register the repository, build the argv - and report all three, masked."""

    env = env_mod.discover_gemini_env(repo_root=args.repo)
    registration = env_mod.ensure_registered(args.repo)
    argv = gemini_argv(env, order, args.model, args.profile)

    lines.extend(f"{key}={value}" for key, value in env_mod.masked(env).items() if value)
    lines.append(
        "registered: projects={} trustedFolders={}".format(
            "added" if registration["projects_added"] else "already",
            "added" if registration["trusted_added"] else "already",
        )
    )
    lines.append(f"command: {env_mod.mask_text(quote(argv), [env.get('ANTIGRAVITY_CSRF_TOKEN')])}")
    return env, argv


def send_gemini(args: argparse.Namespace, order: dict[str, Any], folder: Path, lines: list[str]) -> dict[str, Any]:
    env, argv = resolve_gemini(args, order, lines)

    result: dict[str, Any] = {
        "packetId": order["packetId"],
        "lane": "gemini",
        "conversationId": None,
        "sentAt": None,
        "status": "dry-run" if args.dry_run else "sent",
        "packetDir": str(folder),
    }
    if args.dry_run:
        return result

    missing = [k for k in ("ANTIGRAVITY_LS_ADDRESS", "ANTIGRAVITY_CSRF_TOKEN") if not env.get(k)]
    if missing:
        raise SystemExit(f"cannot send: {', '.join(missing)} not found where I looked (is Antigravity running?)")

    before = time.time() - CLOCK_SLACK_S
    sent_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    proc = subprocess.run(argv, capture_output=True, text=True, env=_process_env(env))
    stdout = env_mod.mask_text(proc.stdout or "", [env.get("ANTIGRAVITY_CSRF_TOKEN")])
    stderr = env_mod.mask_text(proc.stderr or "", [env.get("ANTIGRAVITY_CSRF_TOKEN")])
    if proc.returncode != 0:
        lines.append(f"agentapi exit {proc.returncode}: {(stderr or stdout).strip()[:400]}")
        result["status"] = "failed"
        env_mod.write_json(folder / "send-error.json", {"returncode": proc.returncode, "stderr": stderr[:4000]})
        return result

    conversation_id = env_mod.newest_conversation(after_ts=before, title=order["title"])
    if not conversation_id:
        lines.append("conversation id not found where I looked (store mtime + title scan); sent anyway")
    result.update({"conversationId": conversation_id, "sentAt": sent_at})
    result["packetDir"] = str(_record_gemini_send(args, order, folder, env, conversation_id, sent_at, stdout))
    return result


def _record_gemini_send(
    args: argparse.Namespace,
    order: dict[str, Any],
    folder: Path,
    env: dict[str, Any],
    conversation_id: str | None,
    sent_at: str,
    stdout: str,
) -> Path:
    """The send's paper trail: the conversation record, the rename into `sent/`, one ledger line."""

    env_mod.write_json(
        folder / "conversation.json",
        {
            "packetId": order["packetId"],
            "conversationId": conversation_id,
            "sentAt": sent_at,
            "lsAddress": env.get("ANTIGRAVITY_LS_ADDRESS"),
            "model": args.model,
            "profile": args.profile,
            "stdout": stdout[:4000],
        },
    )
    moved = env_mod.move_packet(order["packetId"], "queue", "sent", repo=args.repo)
    env_mod.ledger_append(
        args.repo,
        {
            "lane": "gemini",
            "packetId": order["packetId"],
            "conversationId": conversation_id,
            "sentAt": sent_at,
            "event": "sent",
            "replyShape": order["replyShape"],
        },
    )
    return moved


def _process_env(env: dict[str, Any]) -> dict[str, str]:
    merged = dict(os.environ)
    for key in ("ANTIGRAVITY_LS_ADDRESS", "ANTIGRAVITY_CSRF_TOKEN", "ANTIGRAVITY_PROJECT_ID"):
        value = env.get(key)
        if value:
            merged[key] = str(value)
    return merged


# --------------------------------------------------------------------------- the claude lane


def claude_argv(order: dict[str, Any], profile: str | None) -> list[str]:
    packet = json.dumps({"packetId": order["packetId"], "brief": order["brief"]}, ensure_ascii=False)
    argv = ["claude", "-p", "--output-format", "json"]
    if profile:
        argv += ["--agent", profile]
    argv.append(packet)
    return argv


def send_claude(args: argparse.Namespace, order: dict[str, Any], folder: Path, lines: list[str]) -> dict[str, Any]:
    argv = claude_argv(order, args.profile)
    lines.append(f"command: {quote(argv[:-1])} <packet {len(argv[-1])} bytes>")
    result: dict[str, Any] = {
        "packetId": order["packetId"],
        "lane": "claude",
        "conversationId": None,
        "sentAt": None,
        "status": "dry-run" if args.dry_run else "replied",
        "packetDir": str(folder),
    }
    if args.dry_run:
        return result

    sent_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    started = time.time()
    proc = subprocess.run(argv, capture_output=True, text=True)
    seconds = round(time.time() - started, 1)
    payload = _parse_json(proc.stdout)
    reply_text = payload.get("result") if isinstance(payload, dict) else None
    if proc.returncode != 0 and reply_text is None:
        lines.append(f"claude exit {proc.returncode}: {(proc.stderr or '').strip()[:400]}")
        result["status"] = "failed"
        env_mod.write_json(folder / "send-error.json", {"returncode": proc.returncode, "stderr": (proc.stderr or "")[:4000]})
        return result

    moved = env_mod.move_packet(order["packetId"], "queue", "replied", repo=args.repo)
    result["packetDir"] = str(moved)
    result["sentAt"] = sent_at
    result["conversationId"] = payload.get("session_id") if isinstance(payload, dict) else None
    env_mod.write_json(moved / "reply.json", payload if isinstance(payload, dict) else {"raw": proc.stdout[:8000]})
    (moved / "reply.md").write_text(reply_text or (proc.stdout or ""), encoding="utf-8")
    usage = payload.get("usage") if isinstance(payload, dict) else {}
    env_mod.ledger_append(
        args.repo,
        {
            "lane": "claude",
            "packetId": order["packetId"],
            "conversationId": result["conversationId"],
            "sentAt": sent_at,
            "event": "replied",
            "replyShape": order["replyShape"],
            "secondsToReply": seconds,
            "inputTokens": (usage or {}).get("input_tokens"),
            "outputTokens": (usage or {}).get("output_tokens"),
        },
    )
    lines.append(f"reply: {moved / 'reply.md'}")
    return result


def _parse_json(text: str | None) -> Any:
    try:
        return json.loads(text or "")
    except (TypeError, ValueError):
        return {}


# --------------------------------------------------------------------------- entrypoint


def main(argv: Sequence[str] | None = None) -> int:
    # a brief may carry any Unicode (a ">=" sign, an em dash); the Windows console defaults to cp1252 and would raise mid-send
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    brief = read_brief(args.brief_file)
    order = build_order(args, brief)
    lines: list[str] = [f"packetId {order['packetId'][:12]} lane {order['lane']} shape {order['replyShape']}"]

    size = len(brief.encode("utf-8"))
    if size > BRIEF_CAP_BYTES:
        lines.append(f"warning: brief is {size} bytes, over the {BRIEF_CAP_BYTES}-byte packet cap")

    folder = env_mod.packet_dir(args.repo, order["packetId"], "queue")
    for state in ("sent", "replied", "done"):
        existing = env_mod.packet_dir(args.repo, order["packetId"], state)
        if existing.exists():
            lines.append(f"note: this brief was already sent; packet sits in {state}/")
    env_mod.write_json(folder / "order.json", order)
    lines.append(f"packet: {folder}")

    sender = send_gemini if args.lane == "gemini" else send_claude
    result = sender(args, order, folder, lines)

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        for line in lines:
            print(line)
        follow = "bridge_watch.py --lane {} --id <conversationId>".format(args.lane)
        print(f"next: {'send for real (drop --dry-run)' if args.dry_run else follow}")
    return 0 if result["status"] != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

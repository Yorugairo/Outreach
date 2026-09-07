"""Send one order to one lane. An order is a file AND a send - this writes the file, then makes the send.

    python content/video_engine/scripts/bridge_send.py --lane gemini --brief-file order.md --title "profiles" --dry-run
    python content/video_engine/scripts/bridge_send.py --lane gemini --brief-file order.md --title "profiles" --model flash
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
REPLY_SHAPES = ("paths-written", "contract-block", "report-landed", "review", "test-run", "free",
                "fetch", "measure", "watch", "intake-triage")   # P46 T8: the file shapes (docs/runbooks/BRIDGE-SHAPES.md)
SHAPE_SKILLS = {"watch": ["watch"]}   # a shape's skill, named on every order of that shape (operator 2026-09-07: an agent deploys a skill only when the order cites it)
DEFAULT_DEADLINE_MIN = 60
BRIEF_CAP_BYTES = 6 * 1024
CLOCK_SLACK_S = 5.0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lane", choices=LANES, required=True)
    parser.add_argument("--brief-file", required=True, type=Path, help="the order body, markdown, <= 6 KB")
    parser.add_argument("--title", default=None, help="conversation title; also how the id is confirmed")
    parser.add_argument("--profile", default=None, help="gemini: --profile=<p>; claude: --agent <p>")
    parser.add_argument("--model", default="flash",
                        help="gemini model TIER: flash_lite | flash | pro (default flash - operator 2026-09-06: the current flash, 3.8, is the stronger model; pro is 3.1)")
    parser.add_argument("--reply-shape", choices=REPLY_SHAPES, default="free")
    parser.add_argument("--deadline-min", type=int, default=DEFAULT_DEADLINE_MIN)
    parser.add_argument("--root", action="append", default=[], dest="roots",
                        help="P46 T7: an absolute root the order sends the addressee to; a relative path in the reply resolves under it too (repeatable)")
    parser.add_argument("--verify", default=None,
                        help="P46 T7: OUR verification command, run from the repo root once the reply passes on form; exit 0 closes the packet, else tier 1")
    parser.add_argument("--no-template", action="store_true", help="do not append the reply's fill-in grammar block to the brief")
    parser.add_argument("--skill", action="append", default=[], dest="skills", help="a skill the order must cite (`/watch`); repeatable; a watch order always cites /watch")
    parser.add_argument("--marker", default=None, help="paths-written: a string every written file must carry")
    parser.add_argument("--fetch-dir", default=None, help="fetch: the absolute dir the files and MANIFEST.json land in")
    parser.add_argument("--output", action="append", default=[], dest="outputs", help="measure: an absolute output path the tool writes (repeatable)")
    parser.add_argument("--csv", default=None, help="watch: the absolute CSV path")
    parser.add_argument("--schema", default=None, help="watch: the columns, comma-separated, in order")
    parser.add_argument("--required", default=None, help="watch: the columns that may not be blank, comma-separated")
    parser.add_argument("--min-rows", type=int, default=None, help="watch: the least rows the table must carry")
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


def build_order(args: argparse.Namespace, brief: str, packet_source: str | None = None) -> dict[str, Any]:
    """`packet_source` (P46 T7): the packet id is the hash of the brief AS WRITTEN (the file), never of the block the sender
    appends - so a packet keeps its identity whether or not the template rides along."""
    created = dt.datetime.now().astimezone()
    deadline = created + dt.timedelta(minutes=max(args.deadline_min, 0))
    return {
        "packetId": env_mod.packet_id(packet_source if packet_source is not None else brief),
        "lane": args.lane,
        "title": args.title or args.brief_file.stem,
        "replyShape": args.reply_shape,
        "deadline": deadline.isoformat(timespec="seconds"),
        "brief": brief,
        "createdAt": created.isoformat(timespec="seconds"),
        **({"roots": [str(Path(r).expanduser()) for r in args.roots]} if getattr(args, "roots", None) else {}),
        **({"verify": args.verify} if getattr(args, "verify", None) else {}),
        **({"skills": skills} if (skills := sorted(set([*getattr(args, "skills", []), *SHAPE_SKILLS.get(args.reply_shape, [])]))) else {}),
        **({"marker": args.marker} if getattr(args, "marker", None) else {}),
        **({"fetch_dir": str(Path(args.fetch_dir).expanduser())} if getattr(args, "fetch_dir", None) else {}),
        **({"outputs": [str(Path(o).expanduser()) for o in args.outputs]} if getattr(args, "outputs", None) else {}),
        **({"csv": str(Path(args.csv).expanduser())} if getattr(args, "csv", None) else {}),
        **({"schema": [c.strip() for c in args.schema.split(",") if c.strip()]} if getattr(args, "schema", None) else {}),
        **({"required": [c.strip() for c in args.required.split(",") if c.strip()]} if getattr(args, "required", None) else {}),
        **({"min_rows": args.min_rows} if getattr(args, "min_rows", None) else {}),
    }


def with_skills(brief: str, skills: list[str]) -> str:
    """P46 T8: the skills line at the TOP of the brief - an agent deploys a skill only when the order cites it (operator 2026-09-07)."""
    if not skills:
        return brief
    line = "**Skills:** " + ", ".join(f"use the `/{sk}` skill" for sk in skills) + " - name it in your reply.\n\n"
    return brief if line.strip() in brief else line + brief


def with_template(brief: str, shape: str) -> str:
    """P46 T7: the reply's fill-in grammar block, appended to the brief - a block to copy beats prose about format. The
    check CLI both sides can run is named beside it."""
    import bridge_handlers as handlers
    if "## Reply block" in brief or shape == "free":
        return brief
    return (brief.rstrip("\n") + "\n\n## Reply block (fill this in, verbatim, as the first thing in your reply)\n\n```\n"
            + handlers.template(shape) + "```\n"
            "Before replying, run `python content/video_engine/scripts/bridge_check.py --shape " + shape
            + " --reply <the file holding your reply>` from the repo root and paste its PASS line under the block.\n")


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

    conversation_id = env_mod.newest_conversation(after_ts=before, title=order["title"],
                                          needle=next((ln.strip() for ln in order["brief"].splitlines() if ln.strip()), None))
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
    raw = read_brief(args.brief_file)
    brief = raw if getattr(args, "no_template", False) else with_template(raw, args.reply_shape)   # P46 T7: the fill-in block rides every order
    brief = with_skills(brief, sorted(set([*args.skills, *SHAPE_SKILLS.get(args.reply_shape, [])])))   # P46 T8: the skill line
    order = build_order(args, brief, packet_source=raw)
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

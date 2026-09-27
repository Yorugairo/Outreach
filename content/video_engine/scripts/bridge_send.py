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
import re
import shutil
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
CLAIMS_GATE = "content/video_engine/scripts/verify_research_claims.py"   # THE RESEARCH CLAIMS GATE (2026-09-24)
RESEARCH_RUNS = "docs/research/runs"
CLAIMS_CONTRACT = "docs/runbooks/RESEARCH-REPLY-CONTRACT.md"


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
    parser.add_argument("--research-run", default=None,
                        help="THE RESEARCH CLAIMS GATE: the run dir the reply writes claims.jsonl + sources/ into (repo-relative); "
                             "on by default for --lane gemini --reply-shape report-landed, at docs/research/runs/<title slug>")
    parser.add_argument("--no-claims-gate", action="store_true",
                        help="a gemini report-landed order that is not research (say why in the brief); printed as a warning")
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
        **({"research_run": args.research_run} if getattr(args, "research_run", None) else {}),
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


def main_checkout(repo: Path | str) -> Path:
    """R26-340 F7: the MAIN checkout a repo path belongs to. A linked worktree's `.git` is a file naming
    `<main>/.git/worktrees/<name>`; the main checkout's `.git` is a directory. Anything else is its own root."""
    root = Path(repo)
    marker = root / ".git"
    if not marker.is_file():
        return root
    try:
        line = marker.read_text(encoding="utf-8").strip()
    except OSError:
        return root
    gitdir = Path(line.split(":", 1)[1].strip()) if line.lower().startswith("gitdir:") else None
    if gitdir is None or gitdir.parent.name != "worktrees" or gitdir.parent.parent.name != ".git":
        return root
    return gitdir.parent.parent.parent


def output_root_line(repo: Path | str) -> str:
    """The one line every templated order carries: where the files land, as an absolute main-checkout path
    (2026-09-25: two Gemini reviews were written into the Astra worktree instead)."""
    root = main_checkout(repo)
    return (f"Output root: write every file under `{root}` (the main checkout) and name each in the reply by its "
            "absolute path there - never under another worktree or checkout; tier 0 fails a path outside it.\n")


def with_template(brief: str, shape: str, repo: Path | str = REPO) -> str:
    """P46 T7: the reply's fill-in grammar block, appended to the brief - a block to copy beats prose about format. The
    check CLI both sides can run is named beside it, and the output root is stated as an absolute path (R26-340 F7)."""
    import bridge_handlers as handlers
    if "## Reply block" in brief or shape == "free":
        return brief
    return (brief.rstrip("\n") + "\n\n## Reply block (fill this in, verbatim, as the first thing in your reply)\n\n```\n"
            + handlers.template(shape) + "```\n"
            "Before replying, run `python content/video_engine/scripts/bridge_check.py --shape " + shape
            + " --reply <the file holding your reply>` from the repo root and paste its PASS line under the block.\n"
            + output_root_line(repo))


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "research"


def claims_gate(args: argparse.Namespace) -> str | None:
    """The research run dir (repo-relative, posix) when the order is research, else None. Research is any order naming
    `--research-run`, and BY DEFAULT every gemini `report-landed` order - the research lane's shape - unless it opts out
    with `--no-claims-gate`. Why a flag and not a new shape: report-landed's form checks stay as they are and the gate
    rides the existing `verify` hook (P46 T7), so the handlers, the daemon and every older order are untouched."""
    if getattr(args, "no_claims_gate", False):
        return None
    run = getattr(args, "research_run", None)
    if not run and not (args.lane == "gemini" and args.reply_shape == "report-landed"):
        return None
    if not run:
        return f"{RESEARCH_RUNS}/{_slug(args.title or args.brief_file.stem)}"
    path = Path(run).expanduser()
    if path.is_absolute():
        try:
            path = path.resolve().relative_to(Path(args.repo).resolve())
        except ValueError:
            pass
    return path.as_posix()


def gate_command(run: str) -> str:
    return f"python {CLAIMS_GATE} {quote([run])}"


def with_claims_contract(brief: str, run: str) -> str:
    """THE RESEARCH CLAIMS GATE's rules, at the top of the brief (about 1.3 KB, inside the 6 KB packet cap)."""
    return (
        f"## THE RESEARCH CLAIMS GATE (binding: `{CLAIMS_CONTRACT}`)\n\n"
        f"OUR script verifies your reply before it lands: `{gate_command(run)}`. It fetches every URL, resolves every DOI, "
        "finds every quote on the page AND in your saved copy, finds every value inside its quote, recomputes every derived "
        "figure and computes each claim's tier itself. A failing reply comes back to you as a revision order with the "
        "failure table (two rounds, then the operator); nothing reaches docs/research/markets until it passes.\n"
        f"- Write ONLY inside `{run}/`: `claims.jsonl` (one JSON object per figure: id, claim, value, unit, period, "
        "source_title, publisher, url, doi, retrieved_at, quote, sources_file, sha256, tier_declared, derived_from, formula, "
        "notes), `sources/` (every page you quote, saved, its sha256 in the claim), and the report `.md`.\n"
        "- Every number in the report has a claim. No URL you did not fetch this session; no DOI you did not resolve. The "
        "quote is copied verbatim (<= 300 chars), never paraphrased, and the value appears inside it.\n"
        "- Declare the tier honestly: CONFIRMED = the page fetched or saved and the quote and value on it; a secondary "
        "source = PLAUSIBLE; nothing retrievable = UNSOURCED (that passes). An overclaim fails the reply.\n"
        f"- Before replying run `{gate_command(run)}` and paste its last line.\n\n" + brief)


def apply_claims_gate(args: argparse.Namespace) -> str | None:
    """Attach the gate to the args in place: OUR verify command, the run dir, the report shape. Refuses a second verify."""
    run = claims_gate(args)
    if run is None:
        return None
    command = gate_command(run)
    if getattr(args, "verify", None) and args.verify != command:
        raise SystemExit(f"a research order carries the claims gate ({command}); --verify would replace it - "
                         "fold your check into the run, or pass --no-claims-gate and say why")
    args.verify, args.research_run = command, run
    if args.reply_shape == "free":
        args.reply_shape = "report-landed"
    return run


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

    # R26-340 F1: agentapi prints the id it created (`response.newConversation.conversationId`); the store scan by file
    # time is only the fallback for a stdout that does not carry it - six packets sat `conversationId: null` on the guess
    conversation_id, source = conversation_from_stdout(stdout), "stdout"
    if not conversation_id:
        conversation_id, source = env_mod.newest_conversation(
            after_ts=before, title=order["title"],
            needle=next((ln.strip() for ln in order["brief"].splitlines() if ln.strip()), None)), "store-scan"
    if not conversation_id:
        source = None
        lines.append("conversation id not found where I looked (agentapi stdout, then store mtime + title scan); sent anyway")
    result.update({"conversationId": conversation_id, "sentAt": sent_at})
    result["packetDir"] = str(_record_gemini_send(args, order, folder, env, conversation_id, sent_at, stdout, source))
    return result


_STDOUT_ID = re.compile(r'(?<!\\)"conversationId"\s*:\s*"([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})"')
STDOUT_HEAD, STDOUT_TAIL = 4000, 600


def conversation_from_stdout(stdout: str | None) -> str | None:
    """The id agentapi's `new-conversation` printed: the parsed `response.newConversation.conversationId`, else the
    last unescaped `"conversationId": "<uuid>"` in the text (a stored stdout may be cut). A half id is no id."""
    text = stdout or ""
    try:
        payload = json.loads(text)
    except ValueError:
        payload = None
    if isinstance(payload, dict):
        found = ((payload.get("response") or {}).get("newConversation") or {}).get("conversationId")
        if isinstance(found, str) and found.strip():
            return found.strip()
    matches = _STDOUT_ID.findall(text)
    return matches[-1] if matches else None


def _record_gemini_send(
    args: argparse.Namespace,
    order: dict[str, Any],
    folder: Path,
    env: dict[str, Any],
    conversation_id: str | None,
    sent_at: str,
    stdout: str,
    source: str | None = None,
) -> Path:
    """The send's paper trail: the conversation record, the rename into `sent/`, one ledger line. The stdout is kept
    head AND tail: agentapi prints the id after the echoed prompt, so a head alone loses it (R26-340 F1)."""

    env_mod.write_json(
        folder / "conversation.json",
        {
            "packetId": order["packetId"],
            "conversationId": conversation_id,
            "conversationIdSource": source,
            "sentAt": sent_at,
            "lsAddress": env.get("ANTIGRAVITY_LS_ADDRESS"),
            "model": args.model,
            "profile": args.profile,
            "stdout": stdout[:STDOUT_HEAD],
            **({"stdoutTail": stdout[-STDOUT_TAIL:]} if len(stdout) > STDOUT_HEAD else {}),
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


def claude_argv(profile: str | None) -> list[str]:
    claude_bin = shutil.which("claude") or "claude"
    argv = [claude_bin, "-p", "--output-format", "json"]
    if profile:
        argv += ["--agent", profile]
    return argv


def send_claude(args: argparse.Namespace, order: dict[str, Any], folder: Path, lines: list[str]) -> dict[str, Any]:
    argv = claude_argv(args.profile)
    packet = json.dumps({"packetId": order["packetId"], "brief": order["brief"]}, ensure_ascii=False)
    lines.append(f"command: {quote(argv)} <packet on stdin, {len(packet)} bytes>")
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
    # Keep packet text off the Windows command line: a .CMD launcher otherwise
    # interprets reply-template pipes and other metacharacters as shell syntax.
    proc = subprocess.run(argv, input=packet, capture_output=True, text=True, shell=False)
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
    run = apply_claims_gate(args)   # THE RESEARCH CLAIMS GATE: research orders carry OUR verifier by default
    brief = raw if getattr(args, "no_template", False) else with_template(raw, args.reply_shape, args.repo)   # P46 T7: the fill-in block rides every order
    brief = with_claims_contract(brief, run) if run else brief
    brief = with_skills(brief, sorted(set([*args.skills, *SHAPE_SKILLS.get(args.reply_shape, [])])))   # P46 T8: the skill line
    order = build_order(args, brief, packet_source=raw)
    lines: list[str] = [f"packetId {order['packetId'][:12]} lane {order['lane']} shape {order['replyShape']}"]
    if run:
        lines.append(f"claims gate: {order['verify']}")
    elif getattr(args, "no_claims_gate", False):
        lines.append("warning: --no-claims-gate - this order's figures are NOT verified by verify_research_claims.py")

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

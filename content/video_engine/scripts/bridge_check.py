"""bridge_check - tier 0 as a CLI both sides run (P46 T7).

The daemon closes a landed reply at zero tokens when it passes the checks its reply shape names (bridge_handlers). Two of
the three tier-1 runs of 2026-09-06 were the REPLY's form, not the work: a path list written as markdown links, absolute
paths under another root. The fix is to hand the addressee the same check before it replies - and to make it work whether
the order came through the bridge or the operator typed it, so it needs only the shape and the reply.

    python bridge_check.py --shape paths-written --reply reply.md          # order-less: the shape's checks alone
    python bridge_check.py --packet <packetId> --reply reply.md            # with the order (roots, marker, verify)
    python bridge_check.py --template report-landed                        # the fill-in block for that shape

Prints `PASS <shape> (<n> checks)` and the checks, exit 0; or `FAIL <class>: <first failing check>` with the block to fill,
exit 1. `--reply -` reads stdin. `--json` prints the classify() outcome instead.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import bridge_env as env_mod  # noqa: E402
import bridge_handlers as handlers  # noqa: E402

REPO = env_mod.REPO if hasattr(env_mod, "REPO") else HERE.parents[2]
STATES = ("sent", "replied", "done", "queue")


def find_order(repo: Path, packet: str) -> dict:
    for state in STATES:
        folder = env_mod.packet_dir(repo, packet, state)
        path = folder / "order.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise SystemExit(f"packet {packet[:12]} not found under {STATES} in {repo}")


def read_reply(spec: str) -> str:
    if spec == "-":
        return sys.stdin.read()
    p = Path(spec)
    if not p.exists():
        raise SystemExit(f"reply not found where I looked: {p}")
    return p.read_text(encoding="utf-8", errors="replace")


def report(outcome: dict) -> str:
    lines = []
    if outcome["pass"]:
        lines.append(f"PASS {outcome['shape']} ({len(outcome['checks'])} checks)")
    else:
        lines.append(f"FAIL {outcome.get('class') or '?'}: {outcome['reason']}")
    for c in outcome["checks"]:
        lines.append(f"  {'ok  ' if c['ok'] else 'FAIL'} {c['name']} - {c['detail']}")
    if not outcome["pass"]:
        lines.append("")
        lines.append("--- fill this block in, verbatim, as the first thing in your reply (restate what you did; add nothing new) ---")
        lines.append(handlers.template(outcome["shape"]).rstrip("\n"))
        if outcome.get("class") == handlers.CLASS_SUBSTANCE:
            lines.append("(this failure is about the WORK, not the block: the block alone will not close it)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--packet", help="the order's packet id (looked up under sent/replied/done/queue)")
    src.add_argument("--shape", choices=sorted(handlers.HANDLERS), help="order-less: check against this reply shape alone")
    src.add_argument("--template", choices=sorted(handlers.TEMPLATES), help="print the fill-in block for a shape and exit")
    ap.add_argument("--reply", help="the reply file, or - for stdin")
    ap.add_argument("--repo", type=Path, default=Path(REPO))
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if a.template:
        print(handlers.template(a.template).rstrip("\n"))
        return 0
    if not a.reply or not (a.packet or a.shape):
        ap.error("--reply and one of --packet / --shape are required (or --template)")
    order = find_order(a.repo, a.packet) if a.packet else {"replyShape": a.shape}
    outcome = handlers.classify(order, read_reply(a.reply), a.repo)
    print(json.dumps(outcome, indent=1) if a.as_json else report(outcome))
    return 0 if outcome["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

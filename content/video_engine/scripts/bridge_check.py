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

R26-340 F7: an absolute path under PATHS WRITTEN outside every root the order declared (the repo root by default, plus
`roots`, `fetch_dir`, the `outputs` / `csv` folders) is `FAIL outside-root`, whatever the shape's own checks said.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import bridge_env as env_mod  # noqa: E402
import bridge_handlers as handlers  # noqa: E402

REPO = env_mod.REPO if hasattr(env_mod, "REPO") else HERE.parents[2]
STATES = ("sent", "replied", "done", "queue")
CLASS_OUTSIDE_ROOT = "outside-root"   # R26-340 F7: a reply path outside every root the order declared (the repo root by default)
_MSYS_DRIVE = re.compile(r"^/([a-zA-Z])/")


# --------------------------------------------------------------------------- the roots a reply may write under (R26-340 F7)


def declared_roots(order: dict, repo: Path) -> list[str]:
    """The repo root, then every absolute location the ORDER named: `roots`, `fetch_dir`, each `outputs` file's folder,
    the `csv`'s folder. A declared root need not exist yet - the reply is what writes it."""
    raw: list[str] = [str(repo), *[str(r) for r in order.get("roots") or []]]
    if order.get("fetch_dir"):
        raw.append(str(order["fetch_dir"]))
    raw += [str(Path(str(o)).parent) for o in order.get("outputs") or []]
    if order.get("csv"):
        raw.append(str(Path(str(order["csv"])).parent))
    return [_norm(r) for r in raw if r]


def _norm(path: str) -> str:
    text = os.path.expanduser(str(path).strip())
    if os.name == "nt":
        text = _MSYS_DRIVE.sub(lambda m: f"{m.group(1)}:/", text)   # a Git Bash `/c/Users/...` is `C:/Users/...`
    return os.path.normcase(os.path.normpath(os.path.abspath(text)))


def _under(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip("\\/") + os.sep)


def outside_roots(order: dict, text: str, repo: Path) -> list[str]:
    """Every ABSOLUTE path under PATHS WRITTEN that sits under none of the declared roots. A relative path resolves under
    the repo, so it is inside by construction; a half-path left by a transcript cut is not a path and is skipped."""
    items = handlers.parse_reply(text).paths_written or []
    cut = handlers._TRUNCATED.search(text or "")
    roots = declared_roots(order, Path(repo))
    stray: list[str] = []
    for item in items:
        path = handlers._path_from_item(item)
        if not path or "<truncated" in path or (cut and not handlers._looks_whole(path)):
            continue
        if not (handlers._ABSOLUTE.match(path) or Path(path).is_absolute()):
            continue
        if not any(_under(_norm(path), root) for root in roots):
            stray.append(path)
    return stray


def classify(order: dict, text: str, repo: Path | str = REPO) -> dict:
    """Tier 0 as the daemon and this CLI run it: the shape's checks (`bridge_handlers.classify`), then the root check. A
    path outside the declared roots fails the reply with its own class, whatever the shape's checks said - a file
    written into another checkout is lost to this one even when it exists (2026-09-25: two Gemini reviews in the Astra
    worktree)."""
    outcome = handlers.classify(order, text, repo)
    stray = outside_roots(order, text, Path(repo))
    if not stray:
        return outcome
    reason = (f"{len(stray)} path(s) outside the order's roots ({', '.join(declared_roots(order, Path(repo))[:3])}): "
              + ", ".join(stray[:3]))
    entry = handlers.check("inside-root", False, reason)
    return {**outcome, "pass": False, "reason": entry["detail"], "checks": [entry, *outcome["checks"]],
            "class": CLASS_OUTSIDE_ROOT}


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
    outcome = classify(order, read_reply(a.reply), a.repo)
    print(json.dumps(outcome, indent=1) if a.as_json else report(outcome))
    return 0 if outcome["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

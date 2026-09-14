"""Name an effect, read its card (P55 T8).

    python content/video_engine/scripts/effects_card.py "evidence wall"
    python content/video_engine/scripts/effects_card.py "stack"            # 3 cards: exit 2, name one id
    python content/video_engine/scripts/effects_card.py "blur zoom" --json
    python content/video_engine/scripts/effects_card.py "stack" --all      # every matching card

One card prints in <= 40 lines: title, id, status, does, when, the authored example and its validator, the
numbered phases, blends, options, where it lives, its proof and whether it is callable today. Reads only
`docs/EFFECTS-CATALOG.jsonl` through `authoring.effects`.

A RECIPE (P56 T4) prints the same way and just as short: its acts, its ordered members as
`+<offset>s  <card> <option>  - <role>` with each member's title pulled from that card, the dials and where
they were measured, the instant that proves it with the member instants, its count and its doctrine cites.

    python content/video_engine/scripts/effects_card.py "badge ladder"    # recipe:badge-ladder

Exit codes: 0 printed, 1 no match (the nearest three are listed), 2 several matches (one line each).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from authoring import effects as E  # noqa: E402

MAX_LINES = 40
FRAMES_REL = "content/video_engine/tests/golden/frames"
EXIT_OK, EXIT_UNKNOWN, EXIT_AMBIGUOUS = 0, 1, 2


def _section(label: str, items: list, fmt, numbered: bool = False) -> list[str]:
    if not items:
        return [f"{label}: none"]
    marks = (f"{i}." if numbered else "-" for i in range(1, len(items) + 1))
    return [f"{label}:"] + [f"  {m} {fmt(x)}" for m, x in zip(marks, items)]


def _head(c: dict) -> list[str]:
    backlog = ", ".join(c.get("backlog") or [])
    author = c.get("author") or {}
    return [
        f"{c.get('title')}  [{c['id']}]",
        f"status: {c.get('status')}" + (f" (backlog {backlog})" if backlog else ""),
        f"does: {c.get('does') or '-'}",
        f"when: {c.get('when') or '-'}",
        f"example: {author.get('example') or '-'}",
        f"validator: {author.get('check') or '-'}",
        f"key: {author.get('key') or '-'}",
    ]


def _offset(value) -> str:
    """`+2.05s`, or `+2.05..6.65s` when the member fired at a range of offsets."""
    if isinstance(value, list):
        return f"+{float(value[0]):g}..{float(value[1]):g}s"
    return f"+{float(value or 0):g}s"


def _member(member: dict) -> str:
    card = member["card"] + (f" {member['option']}" if member.get("option") else "")
    title = f" ({member['title']})" if member.get("title") else " (no card of that id)"
    return (f"  {_offset(member.get('offset_s'))}  {card}{title} - {member.get('role')}"
            + (" [optional]" if member.get("optional") else ""))


def _recipe_proof(proof: dict | None) -> list[str]:
    if not proof:
        return ["proof: none (a candidate - no cut has carried it yet)"]
    at = ", ".join("-" if t is None else f"{float(t):g}" for t in proof.get("members_at") or [])
    return [f"proof: {proof.get('project')} / {proof.get('build')} / {float(proof.get('t', 0)):g}s",
            f"  members at: {at}",
            f"  timeline: {proof.get('timeline')}"]


def render_recipe(c: dict) -> list[str]:
    """One recipe as plain text: the combination, the dials as measured, and the instant that proves it."""
    count = c.get("count") or 0
    says = "a decoration" if count == 1 else ("unfired" if count < 1 else "a grammar")
    lines = [f"{c.get('title')}  [{c['id']}]",
             f"status: {c.get('status')} - count {count} ({says})",
             f"acts: {', '.join(c.get('acts') or []) or '-'} - window {float(c.get('window_s') or 0):g}s",
             f"does: {c.get('does') or '-'}",
             "members:", *[_member(m) for m in c.get("members") or []]]
    if c.get("dials"):
        lines.append("dials: " + ", ".join(f"{k}={v}" for k, v in c["dials"].items()))
        lines.append(f"  measured: {c.get('dials_source') or 'no source'}")
    lines += _recipe_proof(c.get("proof"))
    lines.append(f"source: {c.get('source') or '-'}")
    cites = [f"{d['ref']} -> " + (f"{d['path']}:{d['line']}" if d.get("path") else "unresolved")
             for d in c.get("doctrine") or []]
    lines.append("doctrine: " + ("; ".join(cites) if cites else "none"))
    names = [a.get("name") for a in c.get("aliases") or [] if a.get("name")]
    if names:
        lines.append("aliases: " + " / ".join(names))
    return lines


def _golden(name: str | None) -> str:
    if not name:
        return "none"
    frame = f"{FRAMES_REL}/{name}.png"
    return f"{name} ({frame})" if (REPO / frame).is_file() else f"{name} (frame not on disk)"


def _tail(c: dict) -> list[str]:
    lives = c.get("lives") or {}
    proof = c.get("proof") or {}
    use = proof.get("first_use") or {}
    at = f" @ {use['t']}s" if use.get("t") is not None else ""
    used = f"{use.get('project')} {use.get('build')}{at}" if use else "none"
    call = c.get("callable") or {}
    why = f" - {call['why']}" if call.get("why") else ""
    return [
        f"lives: {lives.get('form')} {lives.get('path')} :: {lives.get('symbol')}",
        "proof:",
        f"  golden: {_golden(proof.get('golden'))}",
        f"  test: {proof.get('test') or 'none'}",
        f"  first use: {used}",
        f"callable today: {'yes' if call.get('today') else 'no'}{why}",
    ]


def render(c: dict) -> str:
    """One card - or one recipe - as plain text, never more than MAX_LINES lines."""
    lines = render_recipe(c) if E.is_recipe(c) else (
        _head(c)
        + _section("phases", c.get("phases") or [],
                   lambda p: f"{p.get('name')} - {p.get('does')} - {p.get('trigger')}", numbered=True)
        + _section("blends", c.get("blends") or [], lambda b: f"{b.get('source')} -> {b.get('became')}")
        + _section("options", c.get("options") or [], lambda o: f"{o.get('token')} - {o.get('means')}")
        + _tail(c)
    )
    if len(lines) > MAX_LINES:
        extra = len(lines) - (MAX_LINES - 1)
        lines = lines[: MAX_LINES - 1] + [f"... {extra} more lines: --json prints the whole record"]
    return "\n".join(lines)


def _one_line(c: dict) -> str:
    return f"  {c['id']} - {c.get('title')} - {c.get('status')}"


def _safe_stdout() -> None:
    """A Windows console cannot encode every character: replace, never raise."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(errors="replace")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Print an effect's catalogue card.")
    ap.add_argument("name", help="an id, token, title or alias (hyphens and spaces ignored)")
    ap.add_argument("--json", action="store_true", help="print the record(s) as JSON")
    ap.add_argument("--all", action="store_true", help="print every matching card instead of refusing")
    args = ap.parse_args(argv)
    _safe_stdout()

    cards = E.load()
    hits = E.find(args.name, cards=cards)
    if not hits:
        print(f"no card for {args.name!r}; the nearest three:")
        print("\n".join(_one_line(c) for c in E.suggest(args.name, cards)))
        return EXIT_UNKNOWN
    if len(hits) > 1 and not args.all:
        print(f"{args.name!r} matches {len(hits)} cards - name one id (or pass --all):")
        print("\n".join(_one_line(c) for c in hits))
        return EXIT_AMBIGUOUS
    if args.json:
        print(json.dumps(hits if args.all else hits[0], indent=1, ensure_ascii=True))
    else:
        print("\n\n".join(render(c) for c in hits))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())

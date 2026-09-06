"""CRAFT MAP - one row per craft device: its scale, the gates that enforce it, where it is
defined, and one real exemplar.

Operator, 2026-09-05: "the map of both micro and macro literary and speech tips, easily
searched, referenced, and understood." The devices are spread across FULL-VIDEO-MAP,
KNOWLEDGE-GRAPH, the six phase guides, STRENGTH-LOOP, SENTENCE-STRENGTH-CHECK, VOICE-PACK,
DOCTRINE-CORE and docs 30-38 / 51. `docs/GATES-REGISTRY.jsonl` already lists what ENFORCES
them. Nothing joined the two, so a device could be doctrine in one file, gated under an id
in another, and demonstrated in a script nobody could find.

    python content/video_engine/scripts/build_craft_map.py [--write | --check]

`--write` regenerates `docs/CRAFT-MAP.jsonl` + `.md`; `--check` (the default) exits 1 with a
one-line diff summary when either artifact is stale.

WHERE EACH FIELD COMES FROM:

  device / scale / what / defined_in / exemplar
      the CURATED seed, `docs/content-video-engine/patterns/CRAFT-DEVICES.md` - a table a
      reader authored from the sources. This tool never invents a device or an exemplar.
  gates
      `docs/GATES-REGISTRY.jsonl`, joined two ways: the ALIASES map below (declared, because
      a gate rule that says "MAP sec 2" cannot be reached from the word "rehook"), and a
      PHRASE match of the device's own normalised name inside a gate's rule text or cite ref
      ("tricolon" reaches G12/G32 on its own). Union, de-duplicated, registry order.
  defined_in
      each `path#Heading` in the seed resolved against `docs/DOCS-INDEX.jsonl` to a line -
      exact heading first, then a heading prefix. An entry the index cannot reach keeps a
      null line rather than disappearing.
  exemplar.verified
      the quoted text is looked for IN the file it cites. Markdown noise is normalised away
      first (a leading `>`/`#`/emphasis run, backticks, curly quotes, dashes, and line wraps
      inside a blockquote), so a wrapped doc line still matches, and the line reported is the
      line the match STARTS on - the seed's own line number is only a hint. A row whose
      exemplar cannot be found is never dropped: it ships `verified: false`.
  judge_only
      no gate that is not a JUDGE row, and either a J-row joined or the seed said `judge`.
      These are the devices `CHECK-RESPONSIBILITIES.md` s3 leaves to the reader.

Standard library only; the output is deterministic (no timestamps, seed order preserved) and
written with LF endings.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

SEED_REL = "docs/content-video-engine/patterns/CRAFT-DEVICES.md"
GATES_REL = "docs/GATES-REGISTRY.jsonl"
DOCS_INDEX_REL = "docs/DOCS-INDEX.jsonl"
JSONL_REL = "docs/CRAFT-MAP.jsonl"
MD_REL = "docs/CRAFT-MAP.md"
BUILD_CMD = "python content/video_engine/scripts/build_craft_map.py --write"

MACRO_SCALES = ("L4", "L5", "L6")
MICRO_SCALES = ("L0", "L1", "L2", "L3")
SCALE_RE = re.compile(r"\bL[0-6]\b")

# The declared joins. A gate rule is written for the checker that emits it, not for this
# index: "MAP sec 2" enforces the rehook anchors and the CTA budget but contains neither
# word, and `audit:doc-35-rule-2` IS the falsifiable tell. Everything reachable from the
# device's own name is left to the phrase match instead of being restated here.
ALIASES: dict[str, tuple[str, ...]] = {
    "microhook": ("G01", "S01", "J03", "audit:doc-38-beat-1"),
    "pre-opener breath": ("G02", "M07"),
    "paradox": ("G03", "J05", "audit:doc-38-beat-2"),
    "the ban list": ("G04",),
    "direct address": ("G05", "audit:doc-38-beat-3"),
    "biography twist": ("G06",),
    "stakes": ("G07",),
    "mini-payoff": ("G08",),
    "promise": ("G09", "G11", "G26", "audit:doc-38-beat-4"),
    "tricolon": ("G12", "G32"),
    "rehook": ("G13", "G25", "G44", "S06", "lint:rehook", "audit:map-sec-2"),
    "opponent as mechanism": ("G14", "J01"),
    "ring": ("G15", "G15b", "G27", "S05", "lint:ring"),
    "ring echo": ("G15b", "S05", "lint:ring", "audit:doc-38-phase-6"),
    "the glass engine": ("G16", "G31"),
    "the story engine": ("G16", "G37"),
    "attribution-first": ("G17", "audit:doc-32-sec-1"),
    "the savor pause": ("G10", "G18", "G33", "G00", "lint:pause-ration",
                        "audit:doc-37-sec-1"),
    "the pause ration": ("G18", "G33", "G00", "lint:pause-ration",
                         "lint:unknown-mark", "audit:doc-37-sec-1", "audit:map-sec-2"),
    "the catalyst": ("G19", "G40", "S03"),
    "new-info cadence": ("G20", "G22", "V02", "V05"),
    "the loop": ("G21", "G28", "V03"),
    "but/therefore": ("G23", "G43"),
    "head-fake": ("G24", "J02"),
    "the foreshadow schedule": ("G09", "G26"),
    "loop-close": ("G28", "G29"),
    "the cta budget": ("G30", "lint:cta-count", "lint:cta-triple",
                       "audit:doc-38-phase-6", "audit:map-sec-2"),
    "the concession budget": ("G34", "G35"),
    "the retention clock": ("G36", "S06", "V02"),
    "archetype-in-a-setting": ("G37", "J09"),
    "map-not-territory": ("G39", "J10"),
    "the debate": ("G41",),
    "the signpost": ("G39", "G42"),
    "the thumbnail answer": ("G45", "J12"),
    "the tell": ("audit:doc-35-rule-2",),
    "the score": ("lint:sentence-mean", "lint:fragment-stack", "S08",
                  "audit:doc-32-sec-1"),
    "active subject": ("lint:passive-ratio", "audit:doc-32-sec-1"),
    "counterpoint": ("lint:tautology", "J06", "J07"),
    "terminal stress": ("J03",),
    "the phonetic anchor": ("J08",),
    "cashed concreteness": ("J04",),
    "the short's shape": ("S01", "S02", "S03", "S05", "S06", "S07", "S08", "J50", "J51"),
    "one mechanism": ("S02", "J50"),
    "the spine": ("S03", "J51"),
    "the brand line": ("S07",),
    "the midpoint pivot": ("audit:map-sec-1", "audit:doc-38-sec-3",
                           "audit:doc-38-sec-3-phase-4"),
    "the phase geometry": ("audit:map-sec-1", "audit:estimator"),
    "numerals spoken": ("audit:doc-37-sec-4",),
    "the beat recall test": ("V01", "V04"),
    "the precedence rule": ("V04",),
}

# ---- text normalisation -----------------------------------------------------

_CHAR_MAP = {
    "—": "-", "–": "-", "‒": "-", "‐": "-", "‑": "-",
    "−": "-", "‘": "'", "’": "'", "“": '"', "”": '"',
    "′": "'", " ": " ", "…": "...",
}
_MARKUP_RE = re.compile(r"\*\*|`|\*")
_LINE_LEAD_RE = re.compile(r"^\s*(?:>\s*)*(?:#{1,6}\s+)?")
_WS_RE = re.compile(r"\s+")


def _plain(text: str) -> str:
    """The comparison form: markdown emphasis gone, dashes and quotes unified, one space."""
    text = unicodedata.normalize("NFC", text)
    text = "".join(_CHAR_MAP.get(ch, ch) for ch in text)
    return _WS_RE.sub(" ", _MARKUP_RE.sub("", text)).strip()


def _flatten(text: str) -> tuple[str, list[int], list[int]]:
    """One space-joined string of the file's prose, plus the offset and line number of each
    joined line - so a quote that wraps across a blockquote still matches and still reports
    the line it starts on."""
    flat: list[str] = []
    offsets: list[int] = []
    lines: list[int] = []
    cursor = 0
    for number, raw in enumerate(text.splitlines(), start=1):
        piece = _plain(_LINE_LEAD_RE.sub("", raw))
        if not piece:
            continue
        offsets.append(cursor)
        lines.append(number)
        flat.append(piece)
        cursor += len(piece) + 1
    return " ".join(flat), offsets, lines


def find_line(text: str, needle: str) -> int | None:
    """The 1-based line `needle` starts on inside `text`, or None when it is not there."""
    target = _plain(needle)
    if not target:
        return None
    flat, offsets, lines = _flatten(text)
    at = flat.find(target)
    if at < 0:
        return None
    return lines[bisect_right(offsets, at) - 1]


# ---- the seed ---------------------------------------------------------------

@dataclass(frozen=True)
class SeedRow:
    device: str
    scales: tuple[str, ...]
    declared_judge: bool
    what: str
    defined_in: tuple[tuple[str, str], ...]     # (path, heading)
    exemplar_text: str | None                   # None = the seed found none
    exemplar_note: str                          # the verbatim cell when nothing was found
    exemplar_path: str | None
    exemplar_line: int | None


EXEMPLAR_RE = re.compile(r'^"(?P<text>.*)"\s*\((?P<path>[^:()]+):(?P<line>\d+)\)$')


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_seed(repo_root: Path = REPO) -> list[SeedRow]:
    """Every row of the seed's first `| device | scale | ... |` table, in authored order."""
    path = Path(repo_root) / SEED_REL
    if not path.is_file():
        raise FileNotFoundError(f"{SEED_REL} not found - the curated seed is the input")
    rows: list[SeedRow] = []
    in_table = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.lstrip().startswith("|"):
            in_table = False
            continue
        cells = _cells(raw)
        if not in_table:
            if len(cells) >= 5 and cells[0].lower() == "device":
                in_table = True
            continue
        if set("".join(cells)) <= set("-: "):        # the header underline
            continue
        if len(cells) < 5:
            continue
        rows.append(_seed_row(cells))
    if not rows:
        raise ValueError(f"{SEED_REL} carries no device rows")
    return rows


def _seed_row(cells: list[str]) -> SeedRow:
    device, scale_cell, what, defined_cell, exemplar_cell = cells[:5]
    scales = tuple(dict.fromkeys(SCALE_RE.findall(scale_cell)))
    defined = tuple(_split_defined(defined_cell))
    match = EXEMPLAR_RE.match(exemplar_cell)
    if match:
        return SeedRow(device, scales, "judge" in scale_cell.lower(), what, defined,
                       match["text"], "", match["path"].strip(), int(match["line"]))
    return SeedRow(device, scales, "judge" in scale_cell.lower(), what, defined,
                   None, exemplar_cell, None, None)


def _split_defined(cell: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for entry in (e.strip() for e in cell.split(";")):
        if not entry:
            continue
        path, _, heading = entry.partition("#")
        out.append((path.strip(), heading.strip()))
    return out


# ---- the joins --------------------------------------------------------------

def load_gates(repo_root: Path = REPO) -> list[dict]:
    path = Path(repo_root) / GATES_REL
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_index(repo_root: Path = REPO) -> list[dict]:
    path = Path(repo_root) / DOCS_INDEX_REL
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _phrase(device: str) -> str:
    return _WS_RE.sub(" ", re.sub(r"[^0-9a-z]+", " ", _plain(device).lower())).strip()


def _gate_haystack(gate: dict) -> str:
    parts = [gate.get("rule", "")] + [c.get("ref", "") for c in gate.get("cites", [])]
    return _WS_RE.sub(" ", re.sub(r"[^0-9a-z]+", " ", _plain(" ".join(parts)).lower())).strip()


def join_gates(device: str, gates: list[dict]) -> list[dict]:
    """Alias ids first, then a whole-phrase match of the device name in the rule or its cite.
    Registry order, de-duplicated on (id, rule) so G31's three rule texts all survive."""
    wanted = set(ALIASES.get(_plain(device).lower(), ()))
    phrase = _phrase(device)
    padded = f" {phrase} "
    out: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for gate in gates:
        hit = gate["id"] in wanted or (bool(phrase) and padded in f" {_gate_haystack(gate)} ")
        key = (gate["id"], gate.get("rule", ""))
        if hit and key not in seen:
            seen.add(key)
            out.append({"id": gate["id"], "family": gate.get("family"),
                        "levels": list(gate.get("levels", [])), "rule": gate.get("rule", "")})
    return out


def _norm_heading(text: str) -> str:
    return _plain(text).lower().rstrip(" .")


def resolve_defined(path: str, heading: str, index: list[dict]) -> dict:
    """`path#Heading` -> {path, line, heading}. Exact heading, then a heading prefix; a
    heading the index cannot reach keeps a null line and the seed's own words."""
    rows = [r for r in index if r.get("path") == path]
    want = _norm_heading(heading)
    for row in rows:
        if _norm_heading(row.get("heading", "")) == want:
            return {"path": path, "line": row["line"], "heading": row["heading"]}
    for row in rows:
        if want and _norm_heading(row.get("heading", "")).startswith(want):
            return {"path": path, "line": row["line"], "heading": row["heading"]}
    return {"path": path, "line": None, "heading": heading}


def verify_exemplar(row: SeedRow, repo_root: Path = REPO) -> dict:
    """The quote is looked for inside the file it cites. Never deleted - only flagged."""
    if row.exemplar_text is None:
        return {"text": row.exemplar_note, "path": None, "line": None, "verified": False}
    path = Path(repo_root) / row.exemplar_path
    if not path.is_file():
        return {"text": row.exemplar_text, "path": row.exemplar_path,
                "line": row.exemplar_line, "verified": False}
    found = find_line(path.read_text(encoding="utf-8"), row.exemplar_text)
    return {"text": row.exemplar_text, "path": row.exemplar_path,
            "line": found if found is not None else row.exemplar_line,
            "verified": found is not None}


def _macro_or_micro(scales: tuple[str, ...]) -> str:
    macro = any(s in MACRO_SCALES for s in scales)
    micro = any(s in MICRO_SCALES for s in scales)
    if macro and micro:
        return "both"          # the scale-free class - KNOWLEDGE-GRAPH s2; listed in both blocks
    return "macro" if macro else "micro"


def _judge_only(row: SeedRow, gates: list[dict]) -> bool:
    judge = [g for g in gates if g["id"].startswith("J") or g["levels"] == ["JUDGE"]]
    hard = [g for g in gates if g not in judge]
    return not hard and (bool(judge) or row.declared_judge)


def build(repo_root: Path = REPO) -> list[dict]:
    """One record per seed row, in the seed's authored order (the order walks the video)."""
    root = Path(repo_root)
    gates = load_gates(root)
    index = load_index(root)
    records: list[dict] = []
    for row in parse_seed(root):
        joined = join_gates(row.device, gates)
        records.append({
            "device": row.device,
            "scale": list(row.scales),
            "macro_or_micro": _macro_or_micro(row.scales),
            "what": row.what,
            "defined_in": [resolve_defined(p, h, index) for p, h in row.defined_in],
            "gates": joined,
            "judge_only": _judge_only(row, joined),
            "exemplar": verify_exemplar(row, root),
        })
    return records


# ---- rendering --------------------------------------------------------------

def render_jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)


def _gates_text(record: dict) -> str:
    ids = list(dict.fromkeys(g["id"] for g in record["gates"]))
    if not ids:
        return "judge" if record["judge_only"] else "none"
    return ", ".join(ids) + (" (judge only)" if record["judge_only"] else "")


def _defined_text(record: dict) -> str:
    if not record["defined_in"]:
        return "none"
    return " · ".join(f"{d['path']}:{d['line']}" if d["line"] else f"{d['path']}:?"
                      for d in record["defined_in"])


def _exemplar_text(record: dict) -> str:
    ex = record["exemplar"]
    if ex["path"] is None:
        return ex["text"]
    where = f'{ex["path"]}:{ex["line"]}' + ("" if ex["verified"] else " — UNVERIFIED")
    return f'"{ex["text"]}" ({where})'


def _line(record: dict) -> str:
    return (f"- **{record['device']}** [{'/'.join(record['scale']) or '-'}]"
            f" — {record['what']}"
            f" — gates: {_gates_text(record)}"
            f" — defined: {_defined_text(record)}"
            f" — e.g. {_exemplar_text(record)}")


def render_md(records: list[dict]) -> str:
    gated = sum(1 for r in records if r["gates"])
    judged = sum(1 for r in records if r["judge_only"])
    unverified = sum(1 for r in records if not r["exemplar"]["verified"])
    head = [
        "# CRAFT-MAP - every craft device, its scale, its gates, and one real line",
        "",
        f"Generated by `{BUILD_CMD}` from the curated seed `{SEED_REL}`,",
        f"joined to `{GATES_REL}` (what enforces it) and `{DOCS_INDEX_REL}`",
        "(where it is defined). Do not hand-edit it: `--check` fails when it drifts. Edit the",
        "seed instead - a device or an exemplar only ever enters there, by a reader.",
        "",
        "The recipe - one call:",
        "",
        "```bash",
        f'rg -i "<device>" {MD_REL}',
        "```",
        "",
        "Each line is: device - scale (L0-L6, the STRENGTH-LOOP ladder) - what it does, in the",
        "docs' words - the gate ids that enforce it (`judge` = no tool decides it; see",
        "`CHECK-RESPONSIBILITIES.md` s3) - where it is defined, resolved to `path:line` - and one",
        "verbatim exemplar with the `path:line` it was found at. An exemplar marked UNVERIFIED",
        "is a row whose quote could not be located in the file it cites: flagged, never dropped.",
        "",
        "A **scale-free** device (KNOWLEDGE-GRAPH s2 - terminal stress, the gap, the triad, the",
        "ring, attribution-first) carries both a micro and a macro scale, so it is listed in",
        "BOTH blocks below. That repetition is the point: one principle, several altitudes.",
        "",
        f"{len(records)} devices - {gated} carry at least one gate, {judged} are judge-only, "
        f"{unverified} exemplars unverified.",
        "",
    ]
    body: list[str] = []
    for title, keys in (("Macro (L4-L6)", ("macro", "both")), ("Micro (L0-L3)", ("micro", "both"))):
        rows = [r for r in records if r["macro_or_micro"] in keys]
        body += [f"## {title}", ""]
        body += [_line(r) for r in rows] or ["- (none)"]
        body.append("")
    return "\n".join(head + body)


def rendered(repo_root: Path = REPO) -> dict[str, str]:
    records = build(repo_root)
    return {JSONL_REL: render_jsonl(records), MD_REL: render_md(records)}


def write(repo_root: Path = REPO) -> int:
    for rel, text in rendered(repo_root).items():
        path = Path(repo_root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return len(build(repo_root))


def check(repo_root: Path = REPO) -> list[str]:
    """One entry per stale artifact: "<path> (+added/-removed lines)". Empty = in sync."""
    problems: list[str] = []
    for rel, want in rendered(repo_root).items():
        path = Path(repo_root) / rel
        if not path.is_file():
            problems.append(f"{rel} (missing)")
            continue
        if path.read_text(encoding="utf-8") == want:
            continue
        diff = list(difflib.ndiff(path.read_text(encoding="utf-8").splitlines(), want.splitlines()))
        added = sum(1 for d in diff if d.startswith("+ "))
        removed = sum(1 for d in diff if d.startswith("- "))
        problems.append(f"{rel} (+{added}/-{removed} lines)")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 when either artifact is stale (default)")
    ap.add_argument("--write", action="store_true", help="regenerate both artifacts")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    args = ap.parse_args(argv)
    root = args.repo.resolve()
    if args.write:
        count = write(root)
        print(f"build_craft_map: {count} device(s) -> {JSONL_REL} + {MD_REL}")
    stale = check(root)
    if stale:
        print("build_craft_map: STALE - " + "; ".join(stale) + " - run --write")
        return 1
    records = build(root)
    defined = [d for r in records for d in r["defined_in"]]
    print(f"build_craft_map: in sync ({len(records)} devices, "
          f"{sum(1 for r in records if r['gates'])} gated, "
          f"{sum(1 for r in records if r['judge_only'])} judge-only, "
          f"{sum(1 for d in defined if d['line'])}/{len(defined)} definitions resolved, "
          f"{sum(1 for r in records if not r['exemplar']['verified'])} unverified exemplar(s))")
    unresolved = sorted({d["path"] + "#" + d["heading"] for d in defined if not d["line"]})
    if unresolved:
        print("build_craft_map: unresolved definition(s) - " + "; ".join(unresolved))
    return 0


if __name__ == "__main__":
    sys.exit(main())

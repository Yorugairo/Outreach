"""THE SKELETON LIBRARY and the approved mix (P66 T2).

A skeleton is DATA: the approved shape of one beat, written as a template of the kit's row grammar
(`authoring/table.py:1-16`) with the named holes a build fills from its AUTHORED beat plan. These tests hold the
library to the four things T2 promised the parent:

  1. every file is a valid `shape_skeletons.v1` and its `source` RESOLVES - the file is opened at the cited line
     and grepped for the mechanism the skeleton claims, the way `effects_catalog_check.check_anchors` greps a
     card's `lives`; the cite must also sit INSIDE that table's `shot_table` function, so a skeleton cannot cite
     a line an approved cut never played;
  2. at least TWO skeletons carry every beat shape (the blueprint's rejected alternative was one per shape, and a
     compiler whose vocabulary is smaller than the sentence-shape vocabulary converges every cut);
  3. no skeleton emits what portrait forbids - a `badges` rail (R26-171) or a `chart_to park` (R26-172) - and no
     light lands before the page's build ends (E99 s67 Apply 1-2, `rules.light_after_build`);
  4. `approved-mix.json` is MEASURED and RE-DERIVABLE: re-running `derive_approved_mix.py` reproduces the file
     byte for byte, so the numbers M46 leans on can never drift from the cuts they were read off.

The grep's token per signature is this file's own table: the signature is "the ONE word M46 counts - the move a
viewer would name", so the line the skeleton cites must still say that word (a `card` skeleton may say `dock`,
the word the tables use for the same arrival; a `hold` may say `stays`, `held` or `stands`).
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_docs_index as BDI  # noqa: E402  (the DOCS-INDEX records of one file: a CAPABILITIES row is level 7)
import build_effects_catalog as BEC  # noqa: E402  (the cards' `doctrine` resolver - `CAPABILITIES <title words>`)
import derive_approved_mix as MIX  # noqa: E402
from authoring import shapes as SH, table as T  # noqa: E402

SKELETONS = ROOT / "content/video_engine/effects/skeletons"
SCHEMA = ROOT / "content/video_engine/configs/shape_skeleton.schema.json"
MIX_FILE = SKELETONS / "approved-mix.json"
DERIVER = ROOT / "content/video_engine/scripts/derive_approved_mix.py"

# The eight the plan's own table fixes (P66 T1, parent-owned); T2 adds a second for the shapes that had one.
PLAN_LIST = {"open-on-the-chart-axes", "open-page-mounts-the-world", "page-mounts-over-the-world",
             "page-enters-on-its-axes", "held-page-hosts-the-docks", "plate-carries-a-card",
             "page-to-page-no-cream", "spiral-return"}

# The beat shapes this library serves. P65's `effects/lab/beat-shapes.json` names the same six; the schema leaves
# `shape` a free string ON PURPOSE (two plans write the two files) and says a disagreement is caught HERE.
SHAPES = {"open-on-the-chart", "page-number-lands-at-n", "page-to-page-transform", "return",
          "plate-carries-a-card", "held-page-hosts-the-docks"}

PROJECTS = "content/video_engine/projects/systems-and-blowups"

# The three APPROVED tables a skeleton may cite (the plan's Mandatory Reads).
TABLES = {
    "tokyo-tea-break": f"{PROJECTS}/tokyo-tea-break/build_short.py",
    "japan-tariff-trick": f"{PROJECTS}/japan-tariff-trick/build_short.py",
    "memory-trades": f"{PROJECTS}/memory-trades-the-calendar/build_short.py",
}

# ... and the two PROOF tables (E99 s70 Apply 2: the vocabulary is rebuilt from the RECORD, and two of the
# mechanisms the operator named live in an operator-WATCHED proof cut rather than in one of the three approved
# shorts. Each is a real shot table on a real bed - never a fixture, never a golden (E99 s60: a proof is a scene).
PROOF_TABLES = {
    # E98 s7, the evidence door's first instance - the operator, 2026-09-14: "the door effect works well"
    "japan-door": f"{PROJECTS}/japan-tariff-trick/build_short_door.py",
    # P61 T3d, the planted morph on a real scene (CAPABILITIES[The morph: the object becomes the chart])
    "tokyo-planted": f"{PROJECTS}/tokyo-tea-break/build-p61-planted/build_planted.py",
}
ALL_TABLES = {**TABLES, **PROOF_TABLES}

# The grep token per signature - the word the cited line must still say. The vocabulary is
# `configs/shape_skeleton.schema.json` `$defs.signature`, rebuilt from the record by E99 s70 Apply 2.
SIGNATURE_TOKENS = {
    "axes": ("axes",),
    "mount": ("mount",),
    "spiral": ("spiral",),
    "suck": ("suck",),
    "cut": ("cut",),
    "dip": ("dip",),
    "card": ("card", "dock"),
    "hold": ("hold", "held", "holds", "stays", "stands"),
    "snap": ("snap",),
    "throw-then-zoom": ("snap", "throw"),
    "throw-then-push": ("camera", "throw"),
    "door": ("door",),
    "rescale": ("rescale", "window"),
    "recast": ("recast", "then="),
    "park": ("park",),
    "unpark": ("park", "1.0"),
    "melt": ("melt", "compare"),
    "morph": ("morph",),
    "remake": ("remake",),
    "object-becomes-chart": ("morph",),
}

# The words the record names that NO table on disk plays as a beat - they carry their word and their citations
# and NO skeleton, because a skeleton is transcribed, never invented (E99 s70 Apply 2).
WORDS_WITHOUT_A_SKELETON = {"morph", "remake"}

# The holes a build fills: the plan's five, plus the three a row cannot express without (the mount's own seconds,
# and the beat's datum / second dock). T3's compiler resolves exactly these.
HOLES = {"page", "plate", "dock", "dock_b", "t0", "t1", "mount_s", "datum", "datum_b", "ken"}
HOLE_RE = re.compile(r"\{([a-z0-9_]+)\}")

LIGHTS = {"spotlight", "callout", "focus_zoom", "ring", "relight"}
PAGE_BUILD_END_S = 7.4          # gate_motion_density.PAGE_BUILD_END_S - a mounted page's chart LANDS here
AXES_BUILD_END_S = 3.3          # a page that enters on its axes finishes drawing at LP.BUILD + 0.3 (memory's row 1)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def skeleton_files() -> list[Path]:
    return sorted(p for p in SKELETONS.glob("*.json") if p.name != MIX_FILE.name)


SKELETON_FILES = skeleton_files()
IDS = [p.stem for p in SKELETON_FILES]


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def shot_table_span(path: Path) -> tuple[int, int]:
    """The line span of a table's `shot_table` - a cite outside it is not a shape an approved cut played."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "shot_table")
    return fn.lineno, fn.end_lineno


def cited_text(source: str) -> tuple[Path, int, int, str]:
    """(path, first line, last line, the text at those lines) for a `path:line` or `path:lo-hi` cite."""
    rel, _, lines = source.rpartition(":")
    lo, _, hi = lines.partition("-")
    path = ROOT / rel
    body = path.read_text(encoding="utf-8").splitlines()
    first, last = int(lo), int(hi or lo)
    return path, first, last, "\n".join(body[first - 1:last])


# --------------------------------------------------------------------------- the library itself

def signature_vocabulary() -> dict:
    """The schema's `$defs.signature` as `{word: its description}` - the vocabulary, with its citations."""
    return {w["const"]: w["description"] for w in _load(SCHEMA)["$defs"]["signature"]["oneOf"]}


# --------------------------------------------------------------------------- a record cite names its ROW (P72 T29)
#
# R26-242 / R26-301: a `CAPABILITIES.md:<line>` cite broke on every inserted row, and four passed SILENTLY on a
# neighbouring row that happened to say the token. A record cite now names the row by its TITLE - a span of the
# row's bold title in square brackets after the document's name - and resolves the way the effects cards'
# `doctrine` cites do (`build_effects_catalog.resolve_cite` over the file's `docs/DOCS-INDEX.jsonl` records, built
# from the file's own text by `build_docs_index.file_records`, so a stale generated layer or a temp copy resolves
# the same). A ruling is named by its id (and sub-entry), `OPERATOR-RULINGS[E99 s67]` (the heading or bold
# paragraph that opens it). A `cut=` cite still names a shot-table LINE: the approved tables are the frozen record
# of a watched cut.

ROW_DOCS = {"CAPABILITIES": "docs/content-video-engine/CAPABILITIES.md",
            "OPERATOR-RULINGS": "docs/portable/OPERATOR-RULINGS.md"}
ROW_CITE_RE = re.compile(r"\b(CAPABILITIES|OPERATOR-RULINGS)\[([^\]\n]+)\]")
RECORD_RE = re.compile(r"\brecord=(CAPABILITIES|OPERATOR-RULINGS)\[([^\]\n]+)\]")
CUT_RE = re.compile(r"\bcut=([A-Za-z0-9_./-]+\.py):(\d+)(?:-(\d+))?")
LINE_CITE_RE = re.compile(r"(?:CAPABILITIES|OPERATOR-RULINGS)\.md:\d+")

# Every file that carries the vocabulary's or the kit's CAPABILITIES cites (R26-301's list).
KIT_CITE_FILES = ("content/video_engine/configs/shape_skeleton.schema.json",
                  "content/video_engine/scripts/authoring/shapes.py",
                  "content/video_engine/scripts/derive_approved_mix.py",
                  "content/video_engine/effects/skeletons/approved-mix.json",
                  "content/video_engine/tests/test_shape_skeletons.py",
                  "content/video_engine/tests/test_authoring_shapes.py")


def resolve_row(doc: str, span: str, root: Path = ROOT) -> tuple[list[int], int | None]:
    """(every line whose row title carries `span`, the line the resolver answers) for one title cite.

    A CAPABILITIES span goes through `build_effects_catalog.resolve_cite` as `CAPABILITIES <span>` - the cards'
    own lookup - over the file's level-7 row records; a ruling span is the heading (`## E67 ...`) or the bold
    paragraph (`**E99 s67 - ...`) that opens it. The caller asserts exactly ONE row carries the span and the
    resolver lands on it: a span two rows share is ambiguous, and an ambiguous cite is how a silent false pass
    comes back."""
    rel = ROW_DOCS[doc]
    text = (root / rel).read_text(encoding="utf-8")
    if doc == "CAPABILITIES":
        rows = [r for r in BDI.file_records(rel, text) if r["level"] == BDI.ROW_LEVEL]
        named = [r["line"] for r in rows if span.lower() in r["heading"].lower()]
        return named, BEC.resolve_cite(f"CAPABILITIES {span}", rows)["line"]
    opener = re.compile(r"^(?:\*\*|#+\s+)" + re.escape(span) + r"(?![\w.])")
    named = [n for n, line in enumerate(text.splitlines(), 1) if opener.match(line)]
    return named, (named[0] if named else None)


def row_text(doc: str, line: int, root: Path = ROOT) -> str:
    return (root / ROW_DOCS[doc]).read_text(encoding="utf-8").splitlines()[line - 1]


def vocabulary_record_cites() -> dict[str, tuple[str, str]]:
    """{word: (doc, span)} - each word's ONE `record=` title cite (an absent or doubled one is the test's to name)."""
    out: dict[str, tuple[str, str]] = {}
    for word, text in signature_vocabulary().items():
        found = RECORD_RE.findall(text)
        if len(found) == 1:
            out[word] = found[0]
    return out


def kit_row_cites() -> list[tuple[str, str, str]]:
    """(file, doc, span) for every title cite in the kit's files."""
    return [(rel, doc, span) for rel in KIT_CITE_FILES
            for doc, span in ROW_CITE_RE.findall((ROOT / rel).read_text(encoding="utf-8"))]


def _copy_docs(tmp: Path) -> Path:
    for rel in ROW_DOCS.values():
        (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp / rel).write_text((ROOT / rel).read_text(encoding="utf-8"), encoding="utf-8")
    return tmp


def _insert_row(root: Path, doc: str, before: int, row: str) -> None:
    path = root / ROW_DOCS[doc]
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    lines.insert(before - 1, row + "\n")
    path.write_text("".join(lines), encoding="utf-8")


# A row that says every signature's token - the decoy a by-line cite would read after a row moved under it.
DECOY_ROW = ("| **A DECOY ROW INSERTED BY THE TEST, WIRED** (P72 T29) - it says " +
             " ".join(sorted({tok for toks in SIGNATURE_TOKENS.values() for tok in toks})) +
             " | nowhere | WIRED | none |")


def test_the_library_is_not_empty():
    assert len(SKELETON_FILES) >= 12, IDS


@pytest.mark.parametrize("path", SKELETON_FILES, ids=IDS)
def test_every_skeleton_is_a_valid_shape_skeleton(path: Path, validator: Draft202012Validator):
    errors = sorted(validator.iter_errors(_load(path)), key=lambda e: list(e.path))
    assert not errors, [f"{list(e.path)}: {e.message}" for e in errors]


@pytest.mark.parametrize("path", SKELETON_FILES, ids=IDS)
def test_the_id_is_the_file_name(path: Path):
    assert _load(path)["id"] == path.stem


def test_the_plans_own_eight_are_all_there():
    assert PLAN_LIST <= set(IDS), sorted(PLAN_LIST - set(IDS))


def test_every_shape_is_one_of_the_named_beat_shapes():
    shapes = {_load(p)["shape"] for p in SKELETON_FILES}
    assert shapes <= SHAPES, sorted(shapes - SHAPES)


def test_two_skeletons_per_shape():
    """The floor the blueprint set: one skeleton per shape converges every cut (rejected alternative, :38-39)."""
    per_shape: dict[str, list[str]] = {}
    for path in SKELETON_FILES:
        rec = _load(path)
        per_shape.setdefault(rec["shape"], []).append(rec["id"])
    thin = {shape: ids for shape, ids in per_shape.items() if len(ids) < 2}
    assert not thin, thin
    assert set(per_shape) == SHAPES, sorted(SHAPES ^ set(per_shape))


# --------------------------------------------------------------------------- the source, opened and grepped

# --------------------------------------------------------------------------- the VOCABULARY (E99 s70 Apply 2)

def test_the_vocabulary_carries_every_word_the_record_names():
    """The operator's own list in E99 s70 Apply 2, plus the throw pair E99 s71 added - none may be missing."""
    owed = {"axes", "mount", "spiral", "suck", "cut", "dip", "card", "hold", "snap", "door", "morph", "remake",
            "recast", "park", "melt", "object-becomes-chart", "throw-then-zoom", "throw-then-push"}
    assert owed <= set(signature_vocabulary()), sorted(owed - set(signature_vocabulary()))


@pytest.mark.parametrize("word", sorted(signature_vocabulary()))
def test_every_word_cites_the_record_and_a_table_and_both_still_say_it(word: str):
    """A vocabulary written from memory is refused (E99 s70): every word opens its own two citations.

    `record=` is the CAPABILITIES row (or the ruling) that marks the mechanism LIVE or WIRED, named by its TITLE
    and resolved to its row (P72 T29); `cut=` the line of a real shot table that PLAYS it. Both are opened and
    grepped, as `effects_catalog_check.check_anchors` greps a card's `lives`.
    """
    text = signature_vocabulary()[word]
    records, cuts = RECORD_RE.findall(text), CUT_RE.findall(text)
    assert len(records) == 1 and len(cuts) == 1, (
        f"{word}: {len(records)} record=<DOC>[<title>] and {len(cuts)} cut=<table>.py:<line> - a word with no "
        f"citation is refused, and a record cite names its row by title, never by line (R26-242)")
    assert not LINE_CITE_RE.search(text), f"{word}: {LINE_CITE_RE.findall(text)} - a record cite by LINE (R26-242)"
    tokens = SIGNATURE_TOKENS[word]
    (doc, span), = records
    named, line = resolve_row(doc, span)
    assert len(named) == 1 and line == named[0], f"{word}: record={doc}[{span}] names rows {named}, resolves to {line}"
    assert any(tok in row_text(doc, line).lower() for tok in tokens), f"{word}: {doc}[{span}] no longer says {tokens}"
    (rel, lo, hi), = cuts
    body = (ROOT / rel).read_text(encoding="utf-8").splitlines()
    first, last = int(lo), int(hi or lo)
    assert last <= len(body), f"{word}: cut={rel}:{lo} is past the end of the file"
    cited = "\n".join(body[first - 1:last]).lower()
    assert any(tok in cited for tok in tokens), f"{word}: cut={rel}:{lo}-{hi} no longer says {tokens}"


def test_no_kit_file_cites_the_record_by_line():
    """R26-301: the stale cites lived in the schema, `authoring/shapes.py`, the deriver, the mix and both test
    files - none may cite CAPABILITIES (or the rulings) by line again."""
    by_line = {rel: LINE_CITE_RE.findall((ROOT / rel).read_text(encoding="utf-8")) for rel in KIT_CITE_FILES}
    assert not {rel: hits for rel, hits in by_line.items() if hits}, by_line


def test_every_title_cite_in_the_kit_names_exactly_one_row():
    """Every CAPABILITIES / OPERATOR-RULINGS title cite in the kit's files resolves through the index
    to ONE row whose title carries the span - the vocabulary's twenty and the compiler's refusal messages alike."""
    cites = kit_row_cites()
    assert len({rel for rel, _doc, _span in cites}) == len(KIT_CITE_FILES), sorted({r for r, _d, _s in cites})
    bad = {}
    for rel, doc, span in cites:
        named, line = resolve_row(doc, span)
        if len(named) != 1 or line != named[0]:
            bad[f"{rel}: {doc}[{span}]"] = (named, line)
    assert not bad, bad


def test_an_inserted_row_moves_no_cite(tmp_path: Path):
    """Acceptance (2): a row inserted ABOVE every cited row (in a temp copy of the record) leaves every title cite
    on its own row - each resolves one line lower, to the same title - and the vocabulary's tokens still read."""
    root = _copy_docs(tmp_path)
    cites = sorted({(doc, span) for _rel, doc, span in kit_row_cites()})
    assert len(cites) >= 19, cites
    before = {cite: resolve_row(*cite, root=root)[1] for cite in cites}
    for doc in ROW_DOCS:
        lines = [line for (d, _s), line in before.items() if d == doc and line]
        if lines:
            _insert_row(root, doc, min(lines), DECOY_ROW)
    moved = {}
    for (doc, span), was in before.items():
        named, line = resolve_row(doc, span, root=root)
        if named != [was + 1] or line != was + 1:
            moved[f"{doc}[{span}]"] = (was, named, line)
    assert not moved, moved
    for word, (doc, span) in vocabulary_record_cites().items():
        line = resolve_row(doc, span, root=root)[1]
        assert any(tok in row_text(doc, line, root).lower() for tok in SIGNATURE_TOKENS[word]), (word, span)


@pytest.mark.parametrize("word", ["cut", "card", "hold", "object-becomes-chart"])
def test_the_four_silent_false_passes_are_gone(word: str, tmp_path: Path):
    """Acceptance (3), R26-242's four: after the rows moved, `cut`, `card`, `hold` and `object-becomes-chart`
    still found their token on the line - a DIFFERENT row. The drift is replayed here: a decoy that says every
    token is inserted AT the cited row, so a by-line cite would now read the decoy and pass. The title cite reads
    the real row, one line down, and the decoy is never it."""
    root = _copy_docs(tmp_path)
    doc, span = vocabulary_record_cites()[word]
    assert doc == "CAPABILITIES", (word, doc)
    was = resolve_row(doc, span, root=root)[1]
    _insert_row(root, doc, was, DECOY_ROW)
    assert any(tok in row_text(doc, was, root).lower() for tok in SIGNATURE_TOKENS[word])   # the by-line false pass
    named, line = resolve_row(doc, span, root=root)
    assert named == [was + 1] and line == was + 1, (word, span, was, named, line)
    assert span.lower() in row_text(doc, line, root).lower() and "DECOY" not in row_text(doc, line, root)


def test_a_word_with_no_skeleton_says_so_in_its_own_description():
    """E99 s70: a mechanism the record marks LIVE that no table plays gets its WORD and no skeleton, and says so."""
    have = {_load(p)["signature"] for p in SKELETON_FILES}
    vocab = signature_vocabulary()
    for word, text in vocab.items():
        if word in have:
            continue
        assert word in WORDS_WITHOUT_A_SKELETON, f"{word} has no skeleton and is not declared as one that cannot"
        assert "NO SKELETON" in text, f"{word}: the description does not say it has no skeleton"
    assert WORDS_WITHOUT_A_SKELETON.isdisjoint(have), sorted(WORDS_WITHOUT_A_SKELETON & have)
    assert set(vocab) - have == WORDS_WITHOUT_A_SKELETON, sorted((set(vocab) - have) ^ WORDS_WITHOUT_A_SKELETON)


def test_every_word_the_record_names_and_a_table_plays_has_a_skeleton():
    have = {_load(p)["signature"] for p in SKELETON_FILES}
    assert set(signature_vocabulary()) - WORDS_WITHOUT_A_SKELETON == have, sorted(have)


def test_the_deriver_counts_exactly_the_schemas_vocabulary():
    """E99 s70 Apply 5: M46 counts the REBUILT vocabulary - the gate's word list is the schema's, not a second one."""
    assert set(MIX.SIGNATURES) == set(signature_vocabulary())
    assert set(MIX.ARRIVALS) | set(MIX.TRANSFORMS) == set(MIX.SIGNATURES)
    assert not set(MIX.ARRIVALS) & set(MIX.TRANSFORMS)


# --------------------------------------------------------------------------- the source, opened and grepped

@pytest.mark.parametrize("path", SKELETON_FILES, ids=IDS)
def test_the_source_resolves_to_an_approved_table(path: Path):
    rec = _load(path)
    rel = rec["source"].rpartition(":")[0]
    assert rel in ALL_TABLES.values(), rec["source"]
    cited, first, last, _text = cited_text(rec["source"])
    assert cited.exists(), cited
    lo, hi = shot_table_span(cited)
    assert lo <= first <= last <= hi, f"{rec['source']} is outside shot_table ({lo}-{hi})"


@pytest.mark.parametrize("path", SKELETON_FILES, ids=IDS)
def test_the_cited_line_still_says_the_mechanism(path: Path):
    """`effects_catalog_check.check_anchors`' habit: open the file at the line and grep it, never trust the cite."""
    rec = _load(path)
    _cited, _first, _last, text = cited_text(rec["source"])
    tokens = SIGNATURE_TOKENS[rec["signature"]]
    assert any(tok in text.lower() for tok in tokens), f"{rec['id']}: {rec['source']} no longer says {tokens}"


# --------------------------------------------------------------------------- what a skeleton may not emit

@pytest.mark.parametrize("path", SKELETON_FILES, ids=IDS)
def test_no_rail_and_no_park(path: Path):
    """R26-171: no `badges` rail is emitted at 9:16 - so none is written at all.

    R26-172 stood beside it ("no `chart_to park` at 9:16") and is WITHDRAWN (the parent, 2026-09-17, on the
    approved PORTRAIT cut's own 56.72 s frame: the page parks small at the top and the cards take the room
    below). A park in a skeleton is now ordinary, and the key is gone from `aspect_limits`."""
    rec = _load(path)
    raw = json.dumps(rec["rows"])
    assert "badge" not in raw.lower(), rec["id"]
    assert rec["aspect_limits"] == {"no_badge_rail_at_9_16": True}


def test_the_park_skeletons_are_offered_in_both_aspects():
    """R26-172 WITHDRAWN: the park and the un-park are how a page makes room, in portrait as in landscape."""
    lib = [_load(p) for p in SKELETON_FILES]
    for aspect in ("9:16", "16:9"):
        assert len(SH.usable_library(lib, aspect)) == len(lib)
        assert {"park", "unpark"} <= {s["signature"] for s in SH.usable_library(lib, aspect)}


@pytest.mark.parametrize("path", SKELETON_FILES, ids=IDS)
def test_the_rules_are_the_approved_clocks(path: Path):
    rec = _load(path)
    assert rec["rules"] == {"mount_at_or_after_s": 7.0, "plate_min_s": 6.0,
                            "event_gap_max_s": 2.5, "light_after_build": True}


@pytest.mark.parametrize("path", SKELETON_FILES, ids=IDS)
def test_no_light_before_the_pages_build_ends(path: Path):
    """E99 s67 Apply 1-2: a light is punctuation, never filler, and never lands over the charcoal build."""
    rec = _load(path)
    for row in rec["rows"]:
        plate = row["plate"]
        floor = PAGE_BUILD_END_S if "mount=" in plate else (AXES_BUILD_END_S if ":axes" in plate else 0.0)
        for sp in row.get("species") or []:
            if sp["kind"] not in LIGHTS:
                continue
            at = str(sp.get("at", "{t0}"))
            if at.startswith("{t0}"):
                offset = float(at[4:] or 0)
                assert offset >= floor - 0.05, f"{rec['id']}: {sp['kind']} at {at} under a {floor}s build"


@pytest.mark.parametrize("path", SKELETON_FILES, ids=IDS)
def test_only_the_named_holes(path: Path):
    rec = _load(path)
    used = set(HOLE_RE.findall(json.dumps(rec["rows"])))
    assert used <= HOLES, sorted(used - HOLES)


# --------------------------------------------------------------------------- the rows are rows the compiler takes

def _fill(value, clock: dict):
    """Resolve one template value to the literal the compiler reads (T3 does this for real, from the beat plan)."""
    if isinstance(value, str):
        def sub(m):
            return str(clock[m.group(1)])
        out = HOLE_RE.sub(sub, value)
        m = re.fullmatch(r"(-?[0-9]+(?:\.[0-9]+)?)(?:([+-])([0-9]+(?:\.[0-9]+)?))?", out)
        if not m:
            return out
        seconds = float(m.group(1))
        if m.group(2):
            seconds += float(m.group(3)) * (1 if m.group(2) == "+" else -1)
        return round(seconds, 2)
    return value


def _row_tuple(row: dict, clock: dict) -> tuple:
    docks = []
    for i, dock in enumerate(row["docks"]):
        spec = {"id": dock} if isinstance(dock, str) else dock
        opts = dict(spec.get("options") or {})
        for field in ("read_s", "park_s"):
            if field in spec:
                opts[field] = spec[field]
        docks.append((_fill(spec["id"], clock), i, _fill(spec.get("at", "{t0}"), clock),
                      _fill("{t1}", clock), opts))
    ken = row["ken"]
    ken = tuple(ken) if isinstance(ken, list) else (None if ken is None else _fill(ken, clock))
    species = [dict(sp, at=_fill(sp.get("at", "{t0}"), clock),
                    target={k: _fill(v, clock) for k, v in (sp.get("target") or {}).items()})
               for sp in (row.get("species") or [])]
    return (_fill(row["start"], clock), _fill(row["end"], clock), _fill(row["plate"], clock),
            ken, docks, _fill(row["exit"], clock), species or None)


@pytest.mark.parametrize("path", SKELETON_FILES, ids=IDS)
def test_the_rows_are_the_kits_row_grammar(path: Path, tmp_path: Path):
    """Filled, a template row is a TUPLE `table.write_shot_table` writes and `table.load_rows` reads back."""
    clock = {"t0": 10.0, "t1": 22.0, "page": "ev-a-v1:line:3:right", "plate": "plate-a",
             "dock": "dock-a", "dock_b": "dock-b", "mount_s": 0.7, "datum": 3, "datum_b": 1, "ken": (0.06, 6, -4)}
    rows = [_row_tuple(row, clock) for row in _load(path)["rows"]]
    for start, end, plate, _ken, _docks, _exit, _species in rows:
        assert end - start >= 6.0, (path.stem, start, end)   # M44, `rules.plate_min_s`
        assert isinstance(plate, str) and "{" not in plate
    written = T.write_shot_table(tmp_path / f"{path.stem}.py", rows, "# P66 T2 round trip\n")
    assert T.load_rows(written) == rows


# --------------------------------------------------------------------------- the approved mix, measured

def test_the_mix_names_the_two_approved_cuts_and_their_compiled_timelines():
    mix = _load(MIX_FILE)
    builds = [cut["build"] for cut in mix["approved"]]
    assert builds == ["content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short",
                      "content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short"]
    for cut in mix["approved"] + mix["beside"]:
        assert (ROOT / cut["timeline"]).exists(), cut["timeline"]
        assert cut["timeline"].endswith(".timeline.json") and not cut["timeline"].endswith("/timeline.json")
        assert sum(cut["counts"].values()) == cut["scenes"] == len(cut["per_scene"])
        assert set(cut["counts"]) <= set(mix["signatures"])
        for sig, count in cut["counts"].items():
            assert cut["shares"][sig] == pytest.approx(round(count / cut["scenes"], 4))


def test_the_maximum_share_is_the_one_M46_will_lean_on():
    mix = _load(MIX_FILE)
    top = max(share for cut in mix["approved"] for share in cut["shares"].values())
    assert mix["max_share"]["value"] == pytest.approx(top)
    for hit in mix["max_share"]["at"]:
        cut = next(c for c in mix["approved"] if c["build"] == hit["cut"])
        assert cut["counts"][hit["signature"]] == hit["count"]
        assert cut["scenes"] == hit["of"]


def test_the_reworked_one_shot_sits_beside_and_is_not_approved():
    mix = _load(MIX_FILE)
    assert [cut["build"] for cut in mix["beside"]] == [
        "content/video_engine/projects/systems-and-blowups/memory-trades-the-calendar/build-oneshot-3"]
    beside = mix["beside"][0]
    assert beside["approved"] is False
    assert beside["note"] == "reworked to E99 s67, on the queue"
    assert all("oneshot-3" not in cut["build"] for cut in mix["approved"])


def test_the_mix_is_measured_not_typed():
    """The counts on disk are what the walk reads off the timelines right now - not a remembered number."""
    mix = _load(MIX_FILE)
    for cut in mix["approved"] + mix["beside"]:
        timeline = json.loads((ROOT / cut["timeline"]).read_text(encoding="utf-8"))
        assert MIX.scene_signatures(timeline) == cut["per_scene"]


def test_the_mix_re_derives_byte_for_byte(tmp_path: Path):
    out = tmp_path / "approved-mix.json"
    run = subprocess.run([sys.executable, str(DERIVER), "--out", str(out)],
                         capture_output=True, text=True, cwd=str(ROOT))
    assert run.returncode == 0, run.stderr
    assert out.read_bytes() == MIX_FILE.read_bytes()


def test_the_deriver_says_the_file_on_disk_is_current():
    run = subprocess.run([sys.executable, str(DERIVER), "--check"], capture_output=True, text=True, cwd=str(ROOT))
    assert run.returncode == 0, run.stdout + run.stderr


def test_every_signature_a_skeleton_claims_is_one_M46_counts():
    mix = _load(MIX_FILE)
    for path in SKELETON_FILES:
        assert _load(path)["signature"] in mix["signatures"], path.stem

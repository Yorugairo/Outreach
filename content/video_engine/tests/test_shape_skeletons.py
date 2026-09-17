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
    # P61 T3d, the planted morph on a real scene: the object becomes the chart (CAPABILITIES.md:121)
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


CITE_RE = re.compile(r"(record|cut)=([A-Za-z0-9_./-]+\.(?:md|py)):(\d+)(?:-(\d+))?")


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

    `record=` is the CAPABILITIES row (or the ruling) that marks the mechanism LIVE or WIRED, `cut=` the line of a
    real shot table that PLAYS it - both are opened at the line and grepped, as `effects_catalog_check.check_anchors`
    greps a card's `lives`.
    """
    text = signature_vocabulary()[word]
    cites = {kind: (rel, int(lo), int(hi or lo)) for kind, rel, lo, hi in CITE_RE.findall(text)}
    assert set(cites) == {"record", "cut"}, f"{word}: {sorted(cites)} - a word with no citation is refused"
    tokens = SIGNATURE_TOKENS[word]
    for kind, (rel, lo, hi) in cites.items():
        body = (ROOT / rel).read_text(encoding="utf-8").splitlines()
        assert lo <= len(body), f"{word}: {kind}={rel}:{lo} is past the end of the file"
        cited = "\n".join(body[lo - 1:hi]).lower()
        assert any(tok in cited for tok in tokens), f"{word}: {kind}={rel}:{lo}-{hi} no longer says {tokens}"


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
    """R26-171 / R26-172: no `badges` rail and no `chart_to park` is emitted at 9:16 - so none is written at all."""
    rec = _load(path)
    raw = json.dumps(rec["rows"])
    assert "badge" not in raw.lower(), rec["id"]
    for row in rec["rows"]:
        for sp in row.get("species") or []:
            to = str((sp.get("options") or {}).get("to", ""))
            if sp["kind"] == "chart_to" and to == "park":
                # R26-172 is an ASPECT rule, not a ban: the park and the un-park are approved mechanisms
                # (CAPABILITIES.md:120) and E99 s70 put their words back in the vocabulary. A skeleton whose
                # whole signature is one of them carries it, and `shapes.usable_library` never offers it at 9:16.
                assert rec["signature"] in ("park", "unpark"), rec["id"]
    assert rec["aspect_limits"] == {"no_badge_rail_at_9_16": True, "no_park_at_9_16": True}


def test_no_park_skeleton_is_offered_in_portrait():
    """R26-172, enforced where it belongs: the compiler never offers a park skeleton at 9:16."""
    lib = [_load(p) for p in SKELETON_FILES]
    assert {s["signature"] for s in SH.usable_library(lib, "9:16")}.isdisjoint({"park", "unpark"})
    assert len(SH.usable_library(lib, "16:9")) == len(lib)


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

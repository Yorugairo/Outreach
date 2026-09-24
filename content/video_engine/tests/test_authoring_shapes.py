"""The shape compiler (P66 T3): the AUTHORED beat plan in, the approved skeleton out.

The rules asserted here are the plan's Acceptance 2, on the base the compiler emits from the TOKYO
bed's own read-back plan (P66 T7) at 9:16 - the open on the chart, the mount's clock, the axes
entry, the dip on a world change, the spiral return, the plate's six seconds, no rail and no park
in portrait, and a light only where the sentence points and only after the page's chart lands.

The Japan plan is compiled too, and only ONE thing is claimed of it: that it compiles and round
trips. Its rows are NOT the approved Japan cut's rows and this file never says they are (E99 s11:
the approved cuts are not rebuilt).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import gate_motion_density as MD  # noqa: E402  (the gates' own clocks, read by name - never re-typed)
from authoring import shapes as SH  # noqa: E402
from authoring import table as T  # noqa: E402

PROJECTS = ROOT / "content/video_engine/projects/systems-and-blowups"
TOKYO = PROJECTS / "tokyo-tea-break/build-short"
JAPAN = PROJECTS / "japan-tariff-trick/build-short"
# the one-shot's own plan and take (E99 s72 Apply 6: the compiler's base is judged on it, and the Tokyo
# read-back stays the regression test). READ ONLY - nothing in this suite writes to an approved build.
CALENDAR = PROJECTS / "memory-trades-the-calendar/build-oneshot-3"
# The rebuilt choreography vocabulary (E99 s70 Apply 2) - read from the schema, never typed twice
VOCABULARY = {w["const"] for w in json.loads(
    (ROOT / "content/video_engine/configs/shape_skeleton.schema.json").read_text(encoding="utf-8")
)["$defs"]["signature"]["oneOf"]}
LIGHTS = SH.LIGHT_KINDS
CLOCKED = SH.LIGHT_AFTER_BUILD_KINDS   # P66 T3c: the lights the "after the build" clock binds - and only those


def _words(build: Path) -> list[dict]:
    return json.loads((build / "timeline.json").read_text(encoding="utf-8"))["words"]


def _pages(build: Path):
    """The CLI's own page resolver, on this build's project - `shapes` reads a page's geometry only
    through the caller (`generate_base_table.page_resolver`; the kit names no episode)."""
    def pages(plate: str):
        C = SH.compiler()
        return (C.ledger_world(C.split_plate_opts(str(plate))[0], (0, 0, 0), build.parent) or {}).get("page")
    return pages


def _base(build: Path, aspect: str = "9:16"):
    """(the plan, the rows, the ROW records of `why`) - `SH.silent_why` reads the rest (P66 T3b)."""
    plan = SH.load_plan(build / "BEAT-PLAN.jsonl")
    rows, why = SH.compile(plan, _words(build), SH.DEFAULTS, aspect, pages=_pages(build))
    return plan, rows, SH.rows_why(why)


def _card_box(options: dict, aspect: str = "9:16") -> dict | None:
    """The stage rectangle a row's own placement puts a card in - the compiler's own arithmetic
    (`centred_place` with an authored centre: the width is `centre_w` of the stage, the height the
    card's 16:9 frame and its chrome)."""
    if not SH.placed(options):
        return None
    sw, sh = SH.pager().STAGE_PX[aspect]
    w = round(float(options["centre_w"]) * sw)
    h = round(w * float(options["card_aspect"])) if options.get("card_aspect") else SH.compiler().dock_card_h(w)
    return {"x": round(float(options["centre_x"]) * sw - w / 2), "y": round(float(options["centre_y"]) * sh - h / 2),
            "w": w, "h": h}


def _page(build: Path, plate: str):
    return _pages(build)(plate) if str(plate).startswith("ledger:") else None


@pytest.fixture(scope="module")
def tokyo():
    return _base(TOKYO)


@pytest.fixture(scope="module")
def japan():
    return _base(JAPAN)


def _land(plate: str) -> float:
    """The page's own landing offset, from the plate the compiler emitted."""
    return SH.page_land_offset(SH.entry_in(plate), SH._mount_s(plate))


def _rec(beat, t0, t1, plate, sentence="A sentence about it.", act=None, caps=(), recipe=None, row=None,
         moves=None):
    """One record in M41's schema - the shape a beat plan's line has on disk, with P66 T3b's
    optional `moves` (what the author says this sentence DOES)."""
    out = {"beat": beat, "t0": t0, "t1": t1, "sentence": sentence,
           "act": act if act is not None else "none of the 11 - it states the claim",
           "comparator": {"compared_to": "this against that"}, "capabilities": list(caps),
           "recipe": recipe, "why_none": None if recipe else "no proven recipe names this combination",
           "plate": plate, "source": "a fixture"}
    if row is not None:
        out["row"] = row
    if moves is not None:
        out["moves"] = list(moves)
    return out


def _take(plan, word_s: float = 0.35):
    """A take for a synthetic plan: each record's own sentence laid word by word across its window,
    so `at_word` resolves the way it does on a real take (`authoring/words.py`)."""
    ws = []
    for r in plan:
        toks = str(r["sentence"]).split()
        step = (float(r["t1"]) - float(r["t0"])) / max(len(toks), 1)
        for i, w in enumerate(toks):
            start = round(float(r["t0"]) + i * step, 2)
            ws.append({"w": w, "start": start, "end": round(start + min(step, word_s), 2)})
    return ws


# ---------------------------------------------------------------- the approved shape, on the Tokyo bed
def _first_page(rows):
    """The row the open's PAGE is on - rows[0] when the page is the first frame, rows[1] when it
    mounts over the hook's own world (the approved open's two rows)."""
    return next(i for i, r in enumerate(rows) if str(r[2]).startswith("ledger:"))


def test_the_open_is_the_chart(tokyo):
    """E99 s67 Apply 6: the open is the PAGE - on its axes from frame 0, or mounting over the hook's
    own world, which is what the Tokyo bed's clip hook asks for."""
    _, rows, why = tokyo
    p = _first_page(rows)
    assert rows[0][0] == 0.0
    assert SH.entry_in(rows[p][2]) in ("axes", "mount")
    assert why[p]["skeleton"] in ("open-on-the-chart-axes", "open-page-mounts-the-world")
    assert "the open IS the chart" in why[p]["rule"]
    # the Tokyo bed's hook is a clip, so the page MOUNTS over it - and `why` says exactly that
    assert SH.entry_in(rows[p][2]) == "mount" and "mounts the hook's world" in why[p]["rule"]


def test_the_open_keeps_the_hooks_world(tokyo):
    """THE FOURTH PASS, defect 1 (the parent, reading base v3 at 0.20 s beside the approved cut): the
    approved frame is the tea-break clip with the page mounting over it 2 s in; the base was BARE
    CREAM, because the compiler absorbed the hook's beats into the page that mounts over them. A
    mount with no world under it is a refusal - so the open is TWO rows, the hook's own world from
    frame 0 to the mount word and the page over it, exactly as the approved table writes the pair."""
    _, rows, why = tokyo
    world, page = rows[0], rows[1]
    assert not str(world[2]).startswith("ledger:") and world[0] == 0.0, world
    assert SH.world_of(world[2]) == "clip", "the Tokyo bed's hook is the counter clip"
    assert world[5] is None, "the mount IS the transition - the world under it carries no exit (E45)"
    assert page[0] == world[1] > 0.0 and "mount=" in page[2], (world, page)
    assert why[0]["signature"] == "hold" and "the hook's own world holds under the page" in why[0]["rule"]
    assert why[0]["group"] == why[1]["group"], "one group, two rows - the open's pair"
    # the mount lands on the hook's LAST sentence (the approved cut: `t_mount = at("left America")`)
    assert page[0] == pytest.approx(1.78, abs=0.01), page[0]


def test_a_mount_over_a_world_the_plan_names_is_always_two_rows():
    """The rule, on a synthetic plan: whatever skeleton the open takes, the world the hook is spoken
    over reaches the table. (Before the fourth pass the hook's beats were absorbed and the row began
    with the page.)"""
    page = "ledger:ev-a-v1:line:12:right"
    plan = [_rec(1, 0.0, 3.0, "plate-desk;idle=drift", caps=["the hook's plate world"]),
            _rec(2, 3.2, 6.0, "plate-desk;idle=drift", caps=["still the hook"]),
            _rec(3, 6.4, 20.0, page, caps=["the page draws to datum 12"])]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert [SH.world_of(r[2]) for r in rows] == ["plate", "page"], [r[2] for r in rows]
    assert rows[0][2].startswith("plate-desk") and rows[0][1] == pytest.approx(3.2), rows[0]
    assert rows[1][2].startswith("ledger:") and "mount=" in rows[1][2]
    assert SH.rows_why(why)[0]["signature"] == "hold"


def test_no_page_ever_arrives_built_and_the_clock_picks_the_entry(tokyo):
    """E99 s67 Apply 3: a page whose number lands 7 s or more after its entry mounts; every other
    page enters by its axes (a return by its spiral). `built` is never emitted.

    P66 T3b widened the list by ONE case and E99 s70 widened it to the rule it should always have
    been: a CONTINUITY entry the author wrote (`snap`, `camera`, `morph` - the entries that carry the
    world that was there into this one) STANDS. The clock chooses between a mount and an axes entry;
    it never overwrites the continuity transitions the operator said had been dropped."""
    _, rows, why = tokyo
    pages = [(r, w) for r, w in zip(rows, why) if r[2].startswith("ledger:")]
    assert pages, "the Tokyo bed is a page cut"
    for r, w in pages:
        entry = SH.entry_in(r[2])
        assert entry != "built" and ":built" not in r[2], r[2]
        assert entry in ("axes", "mount", "spiral") or entry in SH.CONTINUITY_ENTRIES, r[2]
        if entry in SH.CONTINUITY_ENTRIES:
            assert "the author's own" in w["rule"], w["rule"]
            continue
        if "the number lands at +" in w["rule"]:
            late = float(w["rule"].split("the number lands at +")[1].split("s")[0])
            assert (entry == "mount") == (late >= SH.MOUNT_AT_OR_AFTER_S), (late, r[2])
        if entry == "mount":
            assert "mount=" in r[2]


def test_the_return_comes_back_by_the_spiral(tokyo):
    """The bed's page has been on screen, and the beat plan says it returns.

    The SPIRAL is the entry (the clock's, enforced by construction). The row's SIGNATURE is the
    skeleton's, and since E99 s70 a skeleton whose signature is a mechanism the PLAN itself names -
    the recast, the park, the melt - is preferred on that beat (rung 0), so the signature word may
    be the transform the page plays rather than the arrival it made. Both are the return's.
    """
    _, rows, why = tokyo
    spirals = [(r, w) for r, w in zip(rows, why) if SH.entry_in(r[2] or "") == "spiral"]
    assert spirals, "the bed carries a return"
    for r, w in spirals:
        assert "returns" in w["rule"]
        assert w["signature"] in ("spiral",) or "rung 0" in w["rule"], w["rule"]


def test_the_exits_are_the_approved_ones(tokyo):
    """The transition INTO each row, read the way the engine reads it.

    CHANGED in the seventh pass (E99 s74), and every changed assertion carries its doctrine:

    1. `row[5]` is the transition INTO that row, not out of it - `build_scene_timeline_f.py:5030` (*"the
       row's EXIT (the transition INTO it, E47)"*), `:2185` (*"the boundary between scenes[i-1] and
       scenes[i] is scenes[i]['exit']"*), R26-60 `:2193` (*"the transition into scenes[i] TAKES the
       outgoing world, scenes[i-1]"*). So the row before a mount is no longer the one that must read
       `cut`: the MOUNTED row is.
    2. `never into a mount` (E45) is read on the row's own entry, which is what the approved cuts carry
       (their mount rows read `exit: cut`).
    3. a world change is no longer asserted to be a DIP: s74 Apply 1 makes the dip the last resort, so
       the assertion is that a dip appears only where the record's transforms for that pair were all
       refused - the chain is in `why[i]["transition"]`, and `test_a_dip_is_never_chosen_...` reads it.
    """
    _, rows, why = tokyo
    for i, r in enumerate(rows):
        exit_, prev = r[5], rows[i - 1] if i else None
        if prev is None:
            assert exit_ is None, "nothing precedes the first world, so it carries no transition (E47)"
            continue
        if exit_ is None:
            # the world a page MOUNTS over hands over by the mount itself (E45): the UNDER row of the
            # open's pair is the only row past the first that carries no token
            assert "mount=" in r[2] or "mount=" in rows[i + 1][2], (i, r[2])
            continue
        if "mount=" in r[2]:
            assert exit_ == "cut", f"row {i} is entered {exit_!r} INTO a mount (E45)"
        elif r[2].startswith("ledger:") and prev[2].startswith("ledger:"):
            assert exit_ == "cut" or exit_.split(":")[0] in ("suck", "melt"), f"page to page took {exit_!r}"
        elif SH.plate_of(r[2]) != SH.plate_of(prev[2]):
            assert exit_.split(":")[0] in ("cut", "dip", "suck", "melt", "door"),                 f"the world changes into row {i} on {exit_!r}, which is no transition the record carries (E99 s74)"
            assert why[i]["transition"]["exit"] == exit_, (i, why[i]["transition"])


def test_a_plate_row_under_m44s_floor_keeps_the_plans_window_and_is_named(tokyo):
    """RENAMED AND TURNED OVER (the eighth pass; this test read `>= PLATE_MIN_S` and so ASSERTED the
    steal). M44 / `PLATE_MIN_S` is the operator's question on the balloon dock - "why do we have a plate
    less than 6 seconds long?" - and the answer is a longer beat in the PLAN, never seconds taken from the
    row beside it: E99 s69 (*"a gate GUIDES, never dismisses; a short plate is diagnosed, never
    manufactured"*) and the parent's read of the one-shot's base, where the stretch cost the next page its
    card and its span move. So a plate under the floor keeps the plan's own window and SAYS SO."""
    _, rows, why = tokyo
    named = 0
    for n, r in enumerate(rows):
        if r[2].startswith("ledger:"):
            continue
        if r[5] is None:
            # the hook's own world under the page that mounts over it: both approved opens hold it
            # for about two seconds and mount on the hook's last sentence, and the row's `why` says
            # M44 reads it - the author's answer is a longer hook, never a later mount
            assert "under M44's six seconds" in why[n]["rule"], why[n]["rule"]
            continue
        if round(r[1] - r[0], 2) >= SH.PLATE_MIN_S:
            continue
        note = str(SH.rows_why(why)[n]["rule"])      # the row's notes are folded into its own rule
        assert f"under M44's {SH.PLATE_MIN_S:.1f} s floor" in note, (r, note)
        assert "the plan's window stands" in note and "E99 s69" in note, note
        named += 1
    assert named, "the regression bed carries a plate under the floor - it is what this test reads"


def test_an_arrival_keeps_its_lead_and_takes_it_from_the_narrative_plate_before_it():
    """THE PARENT'S RULING (2026-09-17): *"an arrival keeps its lead - a page entering by `spiral` starts
    early enough that its arrival LANDS by the sentence's `t0`; the lead is taken from the plate before it
    only where that plate is a narrative plate, and the `why` names it"*. Read on the ONE-SHOT's own plan
    (E99 s72 Apply 6 - the base is judged on it), at the beat the plan declares `:spiral` on: the approved
    cut plays that row from 67.82 s for a sentence at 68.96 s, a 1.14 s lead, and the base's row started
    at the sentence, so the page was still unwinding when "trade it" landed."""
    plan = SH.load_plan(CALENDAR / "BEAT-PLAN.jsonl")
    rows, why = SH.compile(plan, _words(CALENDAR), SH.DEFAULTS, "9:16", pages=_pages(CALENDAR))
    spiral = [b for b in plan if SH.entry_in(str(b["plate"])) == "spiral"]
    assert len(spiral) == 1, "the one-shot's plan declares exactly one spiral page"
    word_at = float(spiral[0]["t0"])
    mine = [(i, r) for i, r in enumerate(rows) if SH.entry_in(str(r[2])) == "spiral"]
    assert len(mine) == 1, [str(r[2]) for r in rows]
    i, row = mine[0]
    lead = SH.entry_unwind("spiral")
    assert lead == MD.LP_SPIRAL_IN_S and lead > 0
    assert round(row[0], 2) == round(word_at - lead, 2), (row[0], word_at, lead)
    assert SH.world_of(str(rows[i - 1][2])) == "plate", rows[i - 1][2]   # a NARRATIVE plate, not a page
    assert round(rows[i - 1][1], 2) == round(row[0], 2)                  # the seconds came out of its tail
    rule = str(SH.rows_why(why)[i]["rule"])
    assert "keeps its LEAD" in rule and "has LANDED by the sentence" in rule, rule
    assert "plate-customs" in rule, rule


def test_the_spirals_unwind_is_over_before_its_sentence_and_before_the_instants_the_parent_read():
    """NO BARE CREAM OVER A SPOKEN WORD (the parent's B3). The player drains a `spiral` page to its point
    at its row's own start (`spiralClocks`: `ui = (t - a) / LP_RETRACT.IN`, the field and the colours both
    fully down the drain at `t = a`), so the first ~0.25 s of such a row IS the bare ground - in the
    APPROVED cut too, measured: at its own boundary 67.82 s the approved frame's mean luminance is 220.49
    and the base's at its own boundary is 220.62, the same frame 0.46 s apart. What the base got wrong was
    WHERE that quarter-second fell: on the sentence. With the lead it is over before the first word, and
    before every instant the parent read (69.4 / 69.7 / 70.0 s)."""
    plan = SH.load_plan(CALENDAR / "BEAT-PLAN.jsonl")
    rows, _why = SH.compile(plan, _words(CALENDAR), SH.DEFAULTS, "9:16", pages=_pages(CALENDAR))
    i = next(n for n, r in enumerate(rows) if SH.entry_in(str(r[2])) == "spiral")
    beat = next(b for b in plan if SH.entry_in(str(b["plate"])) == "spiral")
    standing = round(rows[i][0] + MD.LP_SPIRAL_IN_S, 2)
    assert standing <= float(beat["t0"]) + 1e-9, (standing, beat["t0"])
    for t in (69.4, 69.7, 70.0):
        assert rows[i][0] <= t <= rows[i][1], (t, rows[i][:2])
        assert t >= standing, f"{t}s is inside the spiral's unwind ({rows[i][0]:.2f}-{standing:.2f}s)"


def test_a_lead_is_refused_where_the_world_before_the_page_is_not_a_narrative_plate():
    """The same ruling's second half: *"the lead is taken from the plate before it ONLY where that plate is
    a narrative plate"* - never from a page (its own words are running) and never from a clip. Refused by
    name on the row, never taken quietly."""
    plan = [_rec(1, 0.0, 8.0, "ledger:ev-a-v1:line:12:right", sentence="The page says a number.", row=1),
            _rec(2, 8.4, 16.4, "ledger:ev-b-v1:line:7:right:spiral:cut", sentence="A second page returns.", row=2)]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert SH.entry_in(str(rows[1][2])) == "spiral", rows[1][2]
    assert round(rows[1][0], 2) >= 8.2, rows[1]          # the cut point, not a lead out of the page
    rule = str(SH.rows_why(why)[1]["rule"])
    assert "owed its 1.60 s unwind and does NOT get it" in rule, rule
    assert "1.50 s before its own cut point" in rule, rule      # the cut point already gives it 0.10 s
    assert "is a page" in rule and "never from a clip" in rule, rule


def _short_plate_lead_plan():
    """The eighth pass' review, HIGH 2, measured: a 0.5 s narrative plate before a `:spiral:` page whose
    own cut point is 9.20 s. The plate cannot give a 1.60 s unwind and still be a beat."""
    return [_rec(1, 0.0, 8.4, "ledger:ev-a-v1:line:12:right", sentence="The page says a number here.", row=1),
            _rec(2, 8.4, 8.9, "plate-desk", sentence="July.", row=2),
            _rec(3, 9.3, 17.3, "ledger:ev-b-v1:line:7:right:spiral:cut",
                 sentence="A second page returns now.", row=3)]


def test_a_lead_is_never_taken_from_a_plate_with_nothing_to_spare_and_never_moves_a_page_LATER():
    """THE EIGHTH PASS' HIGH 2. The lead is `min(what the arrival wants, what the plate can spare above
    its own LEAD_FLOOR_S)` and never negative: *"an arrival keeps its lead, and that is the one thing that
    moves a start EARLIER"* - so where the plate before is shorter than the floor the page starts AT its
    own cut point (9.20 s here) and NOT 0.10 s later, and the row's `why` says the plate had nothing to
    spare instead of printing a `-0.10 s` lead that never happened."""
    plan = _short_plate_lead_plan()
    ws = _take(plan)
    cut = SH.W.cut_before(SH._norm_words(ws), "A second page returns", exit="cut")
    assert cut == pytest.approx(9.20), cut                 # the reviewer's measured cut point
    rows, why = SH.compile(plan, ws, SH.DEFAULTS, "9:16")
    assert SH.entry_in(str(rows[2][2])) == "spiral", rows[2][2]
    assert rows[2][0] == pytest.approx(9.20), rows[2]      # AT the cut point, never 9.30
    assert rows[1][1] == pytest.approx(rows[2][0]), (rows[1], rows[2])
    rule = str(SH.rows_why(why)[2]["rule"])
    assert "-0." not in rule, rule                         # no negative lead, anywhere in the evidence
    assert "nothing to spare" in rule and "plate-desk" in rule, rule
    assert "never moves a start LATER" in rule, rule
    assert "keeps its LEAD" not in rule, rule


def test_a_plate_that_can_only_spare_part_of_the_unwind_gives_exactly_that_and_the_why_says_so():
    """The same `min`, on the middle case: the plate is longer than `LEAD_FLOOR_S` but not by the whole
    unwind, so the arrival takes what is there, the plate is left standing at its floor, and the `why`
    names the seconds of unwind that still play over the sentence - never a lead the plate did not give."""
    plan = [_rec(1, 0.0, 8.0, "ledger:ev-a-v1:line:12:right", sentence="The page says a number here.", row=1),
            _rec(2, 8.0, 8.9, "plate-desk", sentence="July.", row=2),
            _rec(3, 9.3, 17.3, "ledger:ev-b-v1:line:7:right:spiral:cut",
                 sentence="A second page returns now.", row=3)]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    held_before = round(rows[1][1] - rows[1][0], 2)
    assert rows[1][0] + SH.LEAD_FLOOR_S == pytest.approx(rows[2][0]), (rows[1], rows[2])  # left AT its floor
    assert held_before == pytest.approx(SH.LEAD_FLOOR_S), held_before
    assert rows[2][0] > rows[1][0], rows                   # the page did move EARLIER, just not the whole way
    rule = str(SH.rows_why(why)[2]["rule"])
    assert "all the narrative plate before it (plate-desk) could spare" in rule, rule
    assert "still plays over" in rule, rule
    assert "-0." not in rule, rule


def test_the_compiler_never_steals_a_page_s_seconds_to_lengthen_a_plate():
    """THE PARENT'S RULING (2026-09-17, on `build-p66-cal` v2): *"the compiler never steals a page's
    seconds to lengthen a plate; the plan's windows stand"*. A 1.3 s plate followed by a page: both rows
    keep the plan's own `t0`s, the plate is NOT stretched to M44's floor, and the diagnosis is on its row.
    On the one-shot's own plan this one mechanism pushed the chip-price page 4.7 s late, squeezed it to
    3.2 s and cost it its docked card and its `span` move (M37's FAIL was that)."""
    plan = [_rec(1, 0.0, 8.0, "ledger:ev-a-v1:line:12:right", sentence="The page says a number.", row=1),
            _rec(2, 8.4, 9.7, "plate-desk", sentence="July.", row=2),
            _rec(3, 10.2, 18.2, "ledger:ev-b-v1:bars:3:right:axes:cut", sentence="The second page counts it.",
                 row=3)]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    # each row starts at the TAKE's own cut point before its first sentence (M13, `words.cut_before`) -
    # the plan's window, to the frame the cut point sits on, and nothing borrowed either way
    assert [round(r[0], 2) for r in rows] == [0.0, 8.3, 10.1], [(r[0], r[1]) for r in rows]
    for r, b in zip(rows, plan):
        assert abs(round(r[0], 2) - float(b["t0"])) <= 0.2, (r[0], b["t0"])
    assert round(rows[1][1] - rows[1][0], 2) == 1.8, rows[1]     # the plan's own window, floor or no floor
    note = str(SH.rows_why(why)[1]["rule"])
    assert "this plate is 1.80 s - under M44's 6.0 s floor" in note, note
    assert "a longer plate is the plan's to write" in note, note


def test_portrait_emits_no_rail(tokyo, japan):
    """R26-171: at 9:16 no `badges` rail leaves the compiler. (R26-172, which stood beside it - no
    `chart_to park` at 9:16 - is WITHDRAWN: see the park's own pin below.)"""
    for _, rows, _ in (tokyo, japan):
        for r in rows:
            assert all("badges" not in (d[4] or {}) for d in r[4] or [])
        assert "badges" not in repr(rows)


def test_the_parks_the_plan_names_are_emitted_in_portrait(tokyo):
    """THE FOURTH PASS, defect 3 (the parent, at 56.72 / 57.52 s): the APPROVED PORTRAIT cut parks its
    page small at the top and the clipping and the wafer card take the room below; base v3 left the
    page full size and dropped both cards over its ink, because R26-172 stripped every park at 9:16.
    The ruling is WITHDRAWN and the three parks the Tokyo plan names (beats 10, 16 and 17 - the park
    for the fingers, the park for the record and the fab, the UN-PARK as they leave) are on the base."""
    plan, rows, why = tokyo
    named = [(b["beat"], m["options"]["scale"]) for b in plan for m in SH.moves_of(b)
             if m.get("kind") == "chart_to" and (m.get("options") or {}).get("to") == "park"]
    assert [n for n, _ in named] == [10, 16, 17], named
    made = [(float(s["at"]), float(s["scale"])) for r in rows for s in r[6] or []
            if s.get("kind") == "chart_to" and s.get("to") == "park"]
    assert [s for _, s in made][:len(named)] == [s for _, s in named], (made, named)
    assert SH.UNPARK_SCALE in [s for _, s in made], "the un-park is the park to 1.0 (CAPABILITIES.md:120)"
    # ... and any park BEYOND the plan's own is the placer making a room for a card that has none
    # (P66 T3e, the last row's tea cup): the row's `why` names every one it makes.
    extra = [t for t, _ in made[len(named):]]
    for t in extra:
        assert any("PARKS to" in w["rule"] and f"at {t:.2f}s" in w["rule"] for w in why), t


def _is_page_build(sp: dict, row) -> bool:
    """The page's OWN build: a `build_to` whose cap lands with the page's chart (P47 T2). It belongs
    to the page's arrival, not to the sentence speaking at that instant."""
    return (sp.get("kind") == "build_to" and isinstance(sp.get("dur"), (int, float))
            and abs(float(sp["at"]) + float(sp["dur"]) - (row[0] + _land(row[2]))) <= SH.ANNOTATE_TOL_S)


def test_a_light_only_points_and_only_after_the_page_has_built(tokyo, japan):
    """E99 s67 Apply 1-2: a light is punctuation, not filler - it fires only on a sentence the plan
    says POINTS, and never before the page's own chart lands.

    P66 T3c narrowed WHICH species the clock binds: the LIGHT proper (the lamp that darkens the page
    around a point - `LIGHT_AFTER_BUILD_KINDS`). A `build_to` IS the build and a callout, a figure or
    a note is the sentence's own mark - both land on their word (M11 counts the build's cap)."""
    for plan, rows, why in (tokyo, japan):
        gs = SH.groups(plan)
        for r, w in zip(rows, why):
            g = gs[w["group"]]              # one group may play TWO rows (the open's world and page)
            for sp in r[6] or []:
                if r[2].startswith("ledger:") and sp["kind"] in CLOCKED:
                    assert sp["at"] + 1e-6 >= r[0] + _land(r[2]), (sp, r[2])
                if "target" in sp and not _is_page_build(sp, r):
                    assert SH.points(SH._beat_at(g, sp["at"])), (sp, r[2])


def test_the_first_chart_is_annotated_with_its_own_landing(tokyo):
    """M11, by the GATE's own rule (`gate_motion_density._first_chart_gate`): the first chart carries
    one of `ANNOTATED_KINDS` inside [the landing, the landing + `ANNOTATE_TOL_S`], **or** a `build_to`
    whose CAP lands there - the line ending ON the datum is the annotation (P47 T2)."""
    _, rows, _ = tokyo
    first = rows[_first_page(rows)]
    assert first[2].startswith("ledger:")
    land = first[0] + _land(first[2])
    marks = [s for s in first[6] or []
             if s["kind"] in SH.ANNOTATED_KINDS and land - 1e-6 <= s["at"] <= land + SH.ANNOTATE_TOL_S]
    caps = [s for s in first[6] or [] if _is_page_build(s, first)]
    assert marks or caps, first[6]


def test_the_opens_build_lands_with_the_page_and_not_on_its_own_word(tokyo):
    """P66 T3c: the plan's `build_to` on beat 3 is spoken at "climbed" (7.6 s) while the open's page
    lands at 5.5 s - three seconds of build AFTER the chart is there reads as a chart standing full
    and unannotated (M11 FAIL on the first generated base). The build is placed to END on the landing
    instead, and the row's `why` says so."""
    _, rows, why = tokyo
    p = _first_page(rows)
    land = rows[p][0] + _land(rows[p][2])
    build = next(s for s in rows[p][6] if s["kind"] == "build_to")
    assert abs(build["at"] + build["dur"] - land) <= 1e-6, build
    # ... which is the annotation M11 counts: the line ends ON the datum as the page lands (P47 T2)
    assert _is_page_build(build, rows[p]), (build, rows[p][2])


def test_no_held_light_the_compiler_would_drop_as_a_flash_is_emitted(tokyo, japan):
    """`build_scene_timeline_f` drops a held species with under `HOLD_MIN_S` before the next event -
    so a base that emits one describes a cut that will not have it (the open's held spotlight, 0.64 s
    before the build, was dropped at compile time and M11 then read the chart as unannotated)."""
    for _, rows, _ in (tokyo, japan):
        for r in rows:
            for sp in r[6] or []:
                assert not SH.flashes(sp, r[6], list(r[4] or []), r[1]), (sp, r[0])


# ---------------------------------------------------------------- E65: the card's room on the page
def test_every_card_on_a_page_is_placed_in_the_pages_own_room(tokyo):
    """E65 / R26-172 (*"parking is not a way to make room for a card on 9:16; the page's own empty
    room is"*): a card that does not place itself is given a rectangle of the page's own, and its box
    touches no line of the page's ink and none of its data. A bare `centre: True` - which reads at the
    STAGE's centre, over the chart - never leaves the compiler."""
    _, rows, _ = tokyo
    seen = 0
    for n, r in enumerate(rows):
        page = _page(TOKYO, r[2])
        if page is None:
            continue
        for d in r[4] or []:
            if not SH.placed(d[4]):
                # the one card that keeps its own throw is the card the NEXT page grows out of
                assert not d[4].get("centre") or d[4].get("arrive") == "throw", d
                continue
            # the room is the page AS IT STANDS when the card lands: under a park, the band the park
            # freed (the approved cut's own answer at 56.7 s - E65 + the park, R26-172 withdrawn)
            park = SH.park_scale_at(r[6] or [], float(d[2]))
            ink = SH.page_ink(page, "9:16", park)
            boxes = SH.parked_boxes(SH.pager().page_boxes(page, "9:16"), park)
            box = _card_box(d[4])
            seen += 1
            assert all(not SH._meets(box, b) for b in ink), (d[0], box, ink)
            assert SH.compiler().mask_is_clear(boxes, box) or not boxes.get("data_mask"), (d[0], box)
    assert seen >= 4, "the Tokyo bed docks five cards on its pages"


def test_a_card_with_no_room_parks_the_page_to_make_one():
    """THE FOURTH PASS, defect 3, the other half: when the page has no room of its own, the card is
    not dropped over its ink and does not fall back to the stage's centre - THE PAGE PARKS, the card
    takes the band the park frees, and the page UN-PARKS when the card leaves. The approved cut's own
    move (`page-parks-to-make-room-for-the-card` / `page-unparks-and-retakes-the-stage`)."""
    page = {"schema_version": "ledger_page.v1", "surface": "page", "builder": "story", "variant": "bars",
            "title": "A page with no room", "sub": "every cell of its plot carries ink",
            "source": "a fixture", "quiet_zone": "right",
            "labels": ["a", "b", "c", "d"], "values": [-47.7, 18.3, -66.8, -26.4],
            "colors": ["crimson", "teal", "crimson", "crimson"], "unit": "$"}
    boxes = SH.pager().page_boxes(page, "9:16")
    full = ["1" * len(boxes["data_mask"])] * len(boxes["data_mask"]) if boxes.get("data_mask") else None
    if full:
        page = {**page, "data_mask": full}
    docks, species, notes = [["dock-x", 0, 10.0, 16.0, {"centre": True}]], [], []
    out = SH.place_cards(docks, page, "9:16", notes, species, 30.0, SH.DEFAULTS)
    parks = [s for s in species if s.get("kind") == "chart_to" and s.get("to") == "park"]
    assert [s["to"] for s in parks] == ["park", "park"], species
    assert parks[0]["at"] == pytest.approx(10.0 - SH.PARK_LEAD_S) and parks[0]["scale"] < 1.0
    assert parks[1]["at"] == pytest.approx(16.0 + SH.UNPARK_LAG_S) and parks[1]["scale"] == SH.UNPARK_SCALE
    assert SH.placed(out[0][4]), "the card took the room the park made"
    assert any("PARKS" in n for n in notes) and any("UN-PARKS" in n for n in notes)


def test_two_cards_live_at_one_instant_never_share_a_box(tokyo):
    """The third pass: the record and the plant both read at the stage's centre on 0:56 - one box,
    two cards, and both over the page's sub. A card takes the first room no card beside it holds."""
    _, rows, _ = tokyo
    for r in rows:
        placed = [d for d in r[4] or [] if SH.placed(d[4])]
        for i, a in enumerate(placed):
            for b in placed[i + 1:]:
                if float(b[2]) >= float(a[3]) or float(a[2]) >= float(b[3]):
                    continue                          # never on screen together
                assert not SH._meets(_card_box(a[4]), _card_box(b[4])), (a[0], b[0])


def test_a_card_the_plan_placed_itself_is_kept_verbatim():
    """E99 s66: the plan is the intelligence. A move that names its own `centre_*` is not re-placed."""
    place = {"centre": True, "centre_w": 0.42, "centre_x": 0.76, "centre_y": 0.316}
    docks = [["dock-x", 0, 1.0, 9.0, dict(place)]]
    notes: list = []
    out = SH.place_cards(docks, {"schema_version": "ledger_page.v1", "surface": "page"}, "9:16", notes)
    assert out[0][4] == place and not notes


def test_a_card_leaves_when_the_chart_is_redrawn_under_it(tokyo):
    """E65: the room is the page's empty room AS THE PAGE STANDS. The panel card was parked in it at
    0:09 and read over the RESCALED line from 0:22 - nine of M25's twenty-nine faults."""
    _, rows, why = tokyo
    p = _first_page(rows)
    panel = next(d for d in rows[p][4] if d[0] == "dock-c-blue-ties-panel")
    rescale = next(s["at"] for s in rows[p][6] if s["kind"] == "chart_to")
    assert float(panel[3]) == pytest.approx(rescale), (panel, rescale)
    assert "leaves at the chart's state change" in why[p]["rule"]


# ---------------------------------------------------------------- the row grammar
def test_the_rows_round_trip_through_the_kit(tmp_path, tokyo):
    """The rows are the kit's own tuples: what `write_shot_table` takes and `load_rows` reads back."""
    _, rows, _ = tokyo
    path = T.write_shot_table(tmp_path / "SHOT-TABLE-SHORT.py", rows, '"""a base."""\n')
    back = T.load_rows(path)
    assert len(back) == len(rows)
    for a, b in zip(rows, back):
        assert tuple(a) == tuple(b)
    assert all(isinstance(r, tuple) and len(r) == 7 for r in back)


def test_a_second_compile_is_byte_identical(tokyo):
    """Acceptance 1: re-running on the same plan changes nothing - no clock, no set ordering, no
    dict iteration leaks into the output."""
    plan, rows, why = tokyo
    rows2, why2 = SH.compile(plan, _words(TOKYO), SH.DEFAULTS, "9:16", pages=_pages(TOKYO))
    assert repr(rows2) == repr(rows) and repr(SH.rows_why(why2)) == repr(why)


def test_every_row_carries_one_why_record(tokyo):
    _, rows, why = tokyo
    assert len(why) == len(rows)
    for w in why:
        # `transition` added by the seventh pass (E99 s74 Apply 1): every row names the transform that
        # carried the boundary INTO it, or the refusal chain that left a cut or a dip there
        assert sorted(w) == ["act", "beat", "group", "rule", "signature", "skeleton", "transition"]
        assert w["rule"] and w["skeleton"] and isinstance(w["beat"], int)
        assert w["signature"] in VOCABULARY, w["signature"]


# ---------------------------------------------------------------- the variety rule and the chooser
def test_no_two_rows_running_use_the_same_skeleton(tokyo, japan):
    """The variety rule, counted on SKELETON IDS (P66 T2: the approved cuts carry consecutive
    signature WORDS - Japan's throw -> snap pair reads card, card - so the word cannot be the rule)."""
    for _, _, why in (tokyo, japan):
        # one per GROUP: the open's two rows (the hook's world and the page over it) are one choice
        ids = [w["skeleton"] for i, w in enumerate(why) if not i or w["group"] != why[i - 1]["group"]]
        assert all(a != b for a, b in zip(ids, ids[1:])), ids


def test_choose_refuses_the_previous_skeleton_and_falls_back_in_the_documented_order():
    lib = SH.load_library()
    beat = {"shape": SH.SHAPE_PLATE, "act": "NAMES a flow", "docks": ["dock-a", "dock-b"]}
    first, rung = SH.choose(beat, [], lib)
    assert rung == "rung 1" and first["shape"] == SH.SHAPE_PLATE
    second, _ = SH.choose(beat, [first["id"]], lib)
    assert second["id"] != first["id"] and second["shape"] == SH.SHAPE_PLATE
    # rung 2: no skeleton of the shape carries this act, so the ACT filter is dropped
    _, rung2 = SH.choose({**beat, "act": "RETRACTS the announcement"}, [], lib)
    assert rung2 in ("rung 1", "rung 2")
    # the plan names no dock, so a skeleton that NEEDS one is not fillable - whichever rung answers,
    # the skeleton that comes back never asks for a card the plan does not have (E99 s70 widened the
    # library, so a dockless skeleton of this shape now answers on rung 1 where it once fell to 3)
    third, rung3 = SH.choose({**beat, "docks": []}, [], lib)
    assert rung3.startswith("rung")
    assert "{dock}" not in str(third["rows"])
    # rung 4: the shape has one skeleton and it was the last one used - the shape outranks variety
    one = [s for s in lib if s["id"] == first["id"]]
    again, rung4 = SH.choose(beat, [first["id"]], one)
    assert again["id"] == first["id"] and rung4.startswith("rung 4")


def test_a_shape_with_no_skeleton_is_refused_by_name():
    with pytest.raises(SH.Refused) as e:
        SH.choose({"shape": "no-such-shape", "beat": 3}, [], SH.load_library())
    assert "no-such-shape" in str(e.value) and "beat 3" in str(e.value)


# ---------------------------------------------------------------- the positional rule
def test_a_plan_whose_sentences_play_none_of_the_acts_still_compiles():
    """Twelve of the Tokyo bed's twenty-five records carry `act: "none of the 11 - ..."`. Such a beat
    is never refused: it is chosen by its SHAPE and its POSITION - the first beat is the open, a beat
    the plan calls a return is the return, a beat whose world is a page is a page beat, the rest are
    narrative plates."""
    page = "ledger:ev-a-v1:line:12:right"
    plan = [_rec(1, 0.0, 3.0, "clip:hook.mp4", caps=["the hook's clip world"]),
            _rec(2, 3.0, 12.0, page, caps=["the page draws to datum 12"]),
            _rec(3, 12.0, 20.0, "plate-desk;idle=drift", caps=["a still life on the desk"]),
            _rec(4, 20.0, 30.0, page, caps=["the page RETURNS by the spiral, datum 12 lit"])]
    assert all(SH.acts_of(r) == set() for r in plan), "the fixture plays none of the twelve acts"
    rows, why = SH.compile(plan, None, SH.DEFAULTS, "9:16")
    why = SH.rows_why(why)
    assert len(rows) == 4, [r[2] for r in rows]                 # the hook's world, then the page that mounts over it
    assert rows[0][2].startswith("clip:") and why[0]["signature"] == "hold"
    assert "the open IS the chart" in why[1]["rule"] and rows[1][2].startswith("ledger:")
    assert not rows[2][2].startswith("ledger:") and "narrative plate" in why[2]["rule"]
    assert SH.entry_in(rows[3][2]) == "spiral" and why[3]["signature"] == "spiral"


def test_a_page_the_cut_has_never_shown_cannot_return():
    """A spiral unwinds a page from its OWN point: a beat that talks like a return over a page the
    viewer has never met is an ordinary page beat."""
    plan = [_rec(1, 0.0, 8.0, "ledger:ev-a-v1:line:12:right", caps=["the page draws to datum 12"]),
            _rec(2, 8.0, 20.0, "ledger:ev-b-v1:bars:3:right", caps=["the ring returns, datum 3 lit"])]
    rows, why = SH.compile(plan, None, SH.DEFAULTS, "9:16")
    why = SH.rows_why(why)
    assert SH.entry_in(rows[1][2]) != "spiral" and why[1]["signature"] != "spiral"


# ---------------------------------------------------------------- the refusals
@pytest.mark.parametrize("break_it, says", [
    (lambda p: p.__setitem__(1, _rec(3, 8.0, 16.0, "plate-desk")), "beat 2 has no record"),
    (lambda p: p[1].__setitem__("comparator", {"compared_to": "  "}), "beat 2 compares to nothing"),
    (lambda p: p[1].update({"recipe": None, "why_none": ""}), "beat 2 has no recipe and no why_none"),
    (lambda p: p[1].__setitem__("plate", None), "beat 2 names no plate"),
])
def test_a_plan_m41_would_fail_is_refused_by_name(break_it, says):
    """`Not Building`: a beat with no plan record is a refusal, not a slot. The compiler's INPUT is
    AUTHORED (E99 s66) and it never invents a beat (`gate_one_shot_floor` SRC_M41)."""
    plan = [_rec(1, 0.0, 8.0, "ledger:ev-a-v1:line:12:right", caps=["datum 12"]),
            _rec(2, 8.0, 16.0, "plate-desk;idle=drift")]
    break_it(plan)
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, None, SH.DEFAULTS, "9:16")
    assert "M41" in str(e.value) and says in str(e.value)


def test_an_empty_plan_is_refused():
    with pytest.raises(SH.Refused) as e:
        SH.compile([], None, SH.DEFAULTS, "9:16")
    assert "AUTHORED" in str(e.value)


def test_a_hole_the_plan_cannot_fill_is_refused_naming_the_beat_the_skeleton_and_the_hole():
    """The sentence POINTS - the plan's capabilities name a region - but names no datum index, and
    the page id carries no emphasize either. The compiler will not make one up."""
    plan = [_rec(1, 0.0, 9.0, "ledger:ev-a-v1:line:12:right", caps=["the page draws to datum 12"]),
            _rec(2, 9.0, 20.0, "ledger:ev-b-v1:bars:right", caps=["a spotlight on the region of the lower half"])]
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, None, SH.DEFAULTS, "9:16")
    said = str(e.value)
    assert "beat 2" in said and "{datum}" in said and "never invents" in said
    assert any(s["id"] in said for s in SH.load_library())


def test_a_sentence_that_points_at_nothing_gets_no_light_and_why_says_so():
    """Not a refusal - a light is simply not emitted where the sentence does not point (Apply 1)."""
    plan = [_rec(1, 0.0, 9.0, "ledger:ev-a-v1:line:12:right", caps=["the page draws to datum 12"]),
            _rec(2, 9.0, 20.0, "ledger:ev-b-v1:bars:right", caps=["the page is the world and nothing is claimed"])]
    rows, why = SH.compile(plan, None, SH.DEFAULTS, "9:16")
    why = SH.rows_why(why)
    assert not rows[1][6]
    assert "points at nothing" in why[1]["rule"]


# ---------------------------------------------------------------- the Japan plan, and the module's own rule
def test_the_japan_plan_compiles_and_round_trips(tmp_path, japan):
    """ONLY that it compiles and round trips - these are NOT the approved Japan cut's rows."""
    _, rows, why = japan
    assert rows and len(why) == len(rows)
    back = T.load_rows(T.write_shot_table(tmp_path / "SHOT-TABLE-SHORT.py", rows, '"""a base."""\n'))
    assert [tuple(r) for r in back] == [tuple(r) for r in rows]


def test_m16_is_measured_and_never_filled():
    """`event_gaps` READS the pulse for the author; nothing in this module adds an event to close a
    gap, because a compiler that fills to a rate is an allocator (`recipes.py:1-20`)."""
    rows = [(0.0, 12.0, "plate-a", (0, 0, 0), [], "cut", [{"kind": "spotlight", "at": 1.0}])]
    assert SH.event_gaps(rows) == [(1.0, 11.0)]
    assert not [n for n in dir(SH) if "fill_to" in n or "densify" in n]


def test_the_module_names_no_episode():
    """The kit's own rule (`authoring/__init__.py:12-15`): no episode id, no crop, no quote, no file
    name, no absolute path - every episode fact arrives as an argument."""
    text = (ROOT / "content/video_engine/scripts/authoring/shapes.py").read_text(encoding="utf-8").lower()
    hits = [f"{i}: {bad!r}" for i, line in enumerate(text.splitlines(), start=1)
            for bad in ("tokyo", "tariff", "snipe", "c:/", "c:\\") if bad in line]
    assert not hits, "an episode fact leaked into the kit:\n" + "\n".join(hits)


# ---------------------------------------------------------------- the beat's named moves (P66 T3b)
def _moved_plan():
    """Two beats on one page: the second NAMES what it does, and the first says nothing at all."""
    page = "ledger:ev-a-v1:line:12:right"
    moves = [{"kind": "spotlight", "at_word": "one hundred", "dur": 1.0,
              "target": {"kind": "datum", "index": 12}},
             {"kind": "figure", "at_word": "billion", "dur": 1.2, "label": "$122.6B",
              "target": {"kind": "datum", "index": 12}, "options": {"dy": -0.9, "color": "neg"}}]
    return [_rec(1, 0.0, 10.0, page, sentence="The page draws its line to the January print.",
                 caps=["the page draws to datum 12"]),
            _rec(2, 10.0, 20.0, page, sentence="It sold one hundred and twenty two billion.",
                 caps=["datum 12"], moves=moves)]


def test_a_beats_named_moves_land_on_their_own_words_with_their_own_targets():
    """The plan is the intelligence (E99 s66): the sentence says what it does, and the compiler puts
    it on the row at the WORD it belongs to - the take is the clock, never a stopwatch."""
    plan = _moved_plan()
    ws = _take(plan)
    rows, why = SH.compile(plan, ws, SH.DEFAULTS, "9:16")
    assert len(rows) == 1, [r[2] for r in rows]
    norm = SH._norm_words(ws)
    spot = [e for e in rows[0][6] if e["kind"] == "spotlight"
            and e["at"] == SH.word_at(norm, "one hundred", 10.0, 20.0)]
    assert len(spot) == 1 and spot[0]["target"] == {"kind": "datum", "index": 12} and spot[0]["dur"] == 1.0
    figures = [e for e in rows[0][6] if e["kind"] == "figure"]
    assert len(figures) == 1
    # `label` is written into the field THAT KIND carries its words in - a figure's is `text` - and
    # `options` are the species' own remaining fields, copied and never translated
    assert figures[0]["text"] == "$122.6B" and figures[0]["dy"] == -0.9 and figures[0]["color"] == "neg"
    assert figures[0]["at"] == SH.word_at(norm, "billion", 10.0, 20.0)
    assert spot[0]["at"] < figures[0]["at"]


def test_a_phrase_that_is_not_in_the_beats_sentence_is_refused_by_name():
    """A move belongs to the sentence it punctuates. The compiler will not go hunting for the word
    elsewhere in the take, and it names the beat and the phrase."""
    plan = _moved_plan()
    plan[1]["moves"][0]["at_word"] = "the metronome"
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    said = str(e.value)
    assert "beat 2" in said and "the metronome" in said and "own sentence" in said


def test_a_light_asked_for_before_the_page_has_built_is_refused_and_never_moved():
    """E99 s67 Apply 1-2: a light is punctuation, not a cover for the build. The move is the
    AUTHOR's, so the compiler refuses it by name rather than quietly re-timing the beat."""
    plan = [_rec(1, 0.0, 12.0, "ledger:ev-a-v1:line:12:right",
                 sentence="The line lands on the January print.", caps=["datum 12"],
                 moves=[{"kind": "spotlight", "at_word": "The line", "dur": 1.0,
                         "target": {"kind": "datum", "index": 12}}])]
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    said = str(e.value)
    assert "beat 1" in said and "before this page" in said and "Apply 1-2" in said
    assert "rather than move the author" in said


def test_a_dock_move_lands_on_its_word_and_parks_in_the_pages_own_room():
    """E65 / `card_in_page_room`: the card reads on its word, then parks in the page's own room and
    holds to the row's end. Its lane and its options are the defaults when the plan names none."""
    page = "ledger:ev-a-v1:line:12:right"
    plan = [_rec(1, 0.0, 12.0, page, sentence="The page draws its line to the print.",
                 caps=["the page draws to datum 12"]),
            _rec(2, 12.0, 24.0, page, sentence="The record itself says so.", caps=["datum 12"],
                 moves=[{"kind": "dock", "at_word": "The record", "asset": "dock-k-pledge"}])]
    ws = _take(plan)
    rows, why = SH.compile(plan, ws, SH.DEFAULTS, "9:16")
    mine = [d for d in rows[0][4] if d[0] == "dock-k-pledge"]
    assert len(mine) == 1, rows[0][4]
    asset, lane, t_in, t_out, options = mine[0]
    assert lane == SH.DOCK_LANE and options == {}
    assert t_in == SH.word_at(SH._norm_words(ws), "The record", 12.0, 24.0)
    # ... and it LEAVES before the row does (the eighth pass; this line read `== rows[0][1]`): the player
    # retracts a card from its `exit` over `DOCK_LEAVE_S` and snaps an exit within `DOCK_SNAP_S` of a
    # boundary onto it, so a card that held to the row's end was still fading over the next world's title
    assert t_out == round(rows[0][1] - SH.DOCK_CLEAR_S, 2), (t_out, rows[0][1])
    assert t_out + SH.DOCK_LEAVE_S <= rows[0][1], (t_out, rows[0][1])


def test_a_card_completes_its_leave_before_the_boundary_and_never_rides_a_cut():
    """THE PARENT'S RULING (2026-09-17, on `build-p66-cal` v2): *"the coin-flip page's card is still on
    stage at 41.16 s over the next page's title; a dock's `leave` ends at or before its row's `t1`, and a
    card never rides a `cut`/`axes` boundary"*. The player's own two dials say what that costs: the
    retract runs FROM `exit` over `EXIT = 0.72` (`samples/scene-evidence-engine.mjs:5457`) and an `exit`
    inside 1.4 s of a boundary is SNAPPED onto it (`:6192-6201`), so the deliberate early clear is
    `DOCK_CLEAR_S` before the row's end."""
    page = "ledger:ev-a-v1:line:12:right"
    plan = [_rec(1, 0.0, 12.0, page, sentence="The page draws its line to the print.",
                 caps=["the page draws to datum 12"],
                 moves=[{"kind": "dock", "at_word": "draws its", "asset": "dock-k-pledge"}]),
            _rec(2, 12.4, 24.0, "ledger:ev-b-v1:bars:3:right:axes:cut", sentence="A second page counts it.")]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert rows[1][5] == SH.CUT_EXIT, rows[1][5]            # the boundary the card would have ridden
    card = [d for d in rows[0][4] if d[0] == "dock-k-pledge"][0]
    assert card[3] + SH.DOCK_LEAVE_S <= rows[0][1] + 1e-9, (card, rows[0][1])
    assert rows[0][1] - card[3] > SH.DOCK_SNAP_S, \
        "an exit inside the player's own 1.4 s snap window is moved back ONTO the boundary"
    for r in rows:                                          # no card on any row rides its own end
        for d in r[4] or []:
            assert float(d[3]) + SH.DOCK_LEAVE_S <= float(r[1]) + 1e-9, (r[0], d)


def test_every_beat_the_plan_leaves_silent_is_named_in_why():
    """E99 s68 - the base the agent MODIFIES: a beat the plan names no move for contributes nothing,
    and says so, so the agent reads where the base is a base and not a cut."""
    plan = _moved_plan()
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    silent = SH.silent_why(why)
    assert [w["beat"] for w in silent] == [1]
    assert sorted(silent[0]) == ["beat", "lights_only", "note", "sentence", "silent"]
    assert silent[0]["sentence"] == plan[0]["sentence"]
    assert silent[0]["lights_only"] is False
    assert "the author's to add or to leave" in silent[0]["note"]
    assert len(SH.rows_why(why)) == len(rows)


def test_a_beat_that_carries_only_a_light_is_SILENT():
    """E99 s71 (the operator, 2026-09-17): *a spotlight is never the move.* When a sentence names a
    thing, the THING ARRIVES - a badge or pill springing with its callout, a stamped prop or icon, a
    docked screenshot, a flight. A beat whose whole plan is one light is a hole in the base and the
    `why` says so, with the act and where the move it wants is written down."""
    plan = [_rec(1, 0.0, 12.0, "ledger:ev-a-v1:line:3:right:axes:cut",
                 sentence="The print that matters is the one they filed in February.", act="QUOTES a number",
                 caps=["spotlight on datum 3"],
                 moves=[{"kind": "spotlight", "at_word": "February", "target": {"kind": "datum", "index": 3},
                         "dur": 1.2}]),
            _rec(2, 12.5, 24.0, "plate-desk;idle=drift", sentence="And the desk it landed on.")]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    silent = {w["beat"]: w for w in SH.silent_why(why)}
    assert set(silent) == {1, 2}, sorted(silent)
    assert silent[1]["lights_only"] is True and "spotlight" in silent[1]["note"]
    assert "a light is never the move" in silent[1]["note"]
    assert "SPECIES-BY-SENTENCE.md" in silent[1]["note"] and "QUOTES" in silent[1]["note"]
    assert silent[2]["lights_only"] is False
    # and the light itself is still emitted - the rule names the hole, it never drops the author's move
    assert any(sp["kind"] == "spotlight" for sp in (rows[0][6] or []))


# ---------------------------------------------------------------- the page's own CHAIN (E99 s70 Apply 3)

def _chained(state: str = "ev-b-v1:bars:3", **moves):
    plate = f"ledger:ev-a-v1:line:3:right:axes:cut;then={state}" if state else "ledger:ev-a-v1:line:3:right:axes:cut"
    return [_rec(1, 0.0, 14.0, plate, sentence="The same data, month by month, is what it did.",
                 act="COMPARES two series", caps=["datum 3"], **moves),
            _rec(2, 14.5, 26.0, "plate-desk;idle=drift", sentence="And the desk it landed on.")]


def test_the_pages_then_chain_travels_onto_the_generated_row():
    """The bug E99 s70 names: `{page}` is the plate id with its `;options` tail stripped, so without
    `with_states` the base rebuilds the page WITHOUT the states its own chart_to moves travel to -
    and every transform renders nothing while the gates count the tokens and read PASS."""
    plan = _chained(moves=[{"kind": "chart_to", "at_word": "month", "dur": 1.4,
                            "options": {"to": "recast", "state": 1}}])
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert SH.states_of(rows[0][2]) == ["ev-b-v1:bars:3"], rows[0][2]
    assert any("`;then=` chain travels with it" in w["rule"] for w in SH.rows_why(why))
    assert [sp["to"] for sp in (rows[0][6] or []) if sp["kind"] == "chart_to"] == ["recast"]


def test_a_transform_that_would_render_nothing_is_refused_by_name():
    """E99 s70 Apply 3: never a silent no-op - the beat and the move are named."""
    plan = _chained(state="", moves=[{"kind": "chart_to", "at_word": "month", "dur": 1.4,
                                      "options": {"to": "recast", "state": 1}}])
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert "beat 1" in str(e.value) and "recast" in str(e.value)
    assert "declares 0 `;then=` state(s)" in str(e.value) and "redraw NOTHING" in str(e.value)


def test_a_transform_the_pages_form_does_not_admit_is_refused():
    """CAPABILITIES.md:118 - a morph hands one LINE's area to another's; a line -> bars pair is the recast."""
    plan = _chained(moves=[{"kind": "chart_to", "at_word": "month", "dur": 1.4,
                            "options": {"to": "morph", "state": 1}}])
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert "a morph hands ONE LINE's area" in str(e.value) and "'bars'" in str(e.value)


def test_a_rescale_with_no_domain_and_a_park_with_a_state_are_refused():
    for options, says in (({"to": "rescale"}, "names the target domain"),
                          ({"to": "park", "state": 1}, "`state` is not named on a park")):
        plan = _chained(moves=[{"kind": "chart_to", "at_word": "month", "dur": 1.4, "options": options}])
        with pytest.raises(SH.Refused) as e:
            SH.compile(plan, _take(plan), SH.DEFAULTS, "16:9")
        assert says in str(e.value), str(e.value)


def test_the_park_is_offered_in_both_aspects():
    """R26-172 WITHDRAWN (the parent, 2026-09-17, on the approved PORTRAIT cut's own 56.72 s frame):
    the park is how a page makes room for a card, in portrait as in landscape."""
    lib = SH.load_library()
    for aspect in ("9:16", "16:9"):
        assert {"park", "unpark"} <= {s["signature"] for s in SH.usable_library(lib, aspect)}


# ---------------------------------------------------------------- the thrown chart card (E99 s71)

def _thrown_card_plan(entry: str):
    """Three beats: the open on its chart, a plate the page's own CARD is thrown onto, and the page.

    Three and not two because the compiler's own open rule makes the hook and the page that mounts
    over it ONE row when the first beat's world is a plate - so the card's beat has to be the second.
    """
    return [_rec(1, 0.0, 10.0, "ledger:ev-open-v1:line:0:right:axes:cut", sentence="It opens on the chart."),
            _rec(2, 10.5, 20.0, "plate-desk;idle=drift", sentence="The desk it landed on.",
                 moves=[{"kind": "dock", "at_word": "desk", "asset": "dock-a-fed-rate",
                         "options": {"arrive": "throw", "mass": "paper"}}]),
            _rec(3, 20.5, 32.0, f"ledger:ev-fed-rate-v1:line:3:right:{entry}:cut",
                 sentence="And the rate it never moved.")]


def test_a_thrown_chart_card_that_nothing_takes_to_the_stage_is_refused():
    """E99 s71: a thrown full-page card ZOOMS or the camera PUSHES to it - it never floats over the
    world. The card is recognised without naming an episode: its name after the slot letter appears
    inside a ledger page id this same cut carries."""
    plan = _thrown_card_plan("axes")
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert "dock-a-fed-rate" in str(e.value) and "FULL CHART CARD" in str(e.value)
    assert ":snap=dock-a-fed-rate" in str(e.value) and ":camera=dock-a-fed-rate" in str(e.value)


def test_a_camera_entry_whose_card_no_row_carries_is_refused():
    """THE FOURTH PASS, defect 5 (the parent, at 77.80 s): the base played a blurred page and no card
    where the approved cut plays the Fed page with its ring. `camera=<dock>` is a read-back token and
    the compiler emitted it whatever the rows held, so the camera could push to a card nobody threw."""
    plan = _thrown_card_plan("camera=dock-a-fed-rate")
    plan[1]["moves"] = []                      # nobody throws the card the page arrives by
    with pytest.raises(SH.Refused) as e:
        SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert "arrives by `camera=dock-a-fed-rate`" in str(e.value), str(e.value)
    assert "no row carries" in str(e.value) and "never thrown" in str(e.value)


def test_a_camera_entry_carries_the_card_thrown_on_the_row_before(tokyo):
    """... and where the card IS thrown, the compiler keeps it: the card the next page grows out of
    takes no room of this page's (it is not evidence parked in a corner - it is the page to be), and
    the row it becomes STARTS WHEN THE CARD HAS BEEN READ, as the approved cut does (the card lands on
    "The Fed still" and the page arrives on "moved"). Base v3 started that row on the next beat, so
    the camera's 0.45 s arrival was still in flight at the instant the parent read."""
    _, rows, _ = tokyo
    page = rows[-1]
    head, _, card = str(SH.entry_token_in(page[2]) or "").partition("=")
    assert head == "camera" and card == "dock-h-fed-vs-yields", page[2]
    thrown = next(d for d in rows[-2][4] if str(d[0]) == card)
    assert not SH.placed(thrown[4]) and thrown[4].get("arrive") == "throw", thrown
    assert float(thrown[3]) >= float(page[0]) - 1e-6, "the card lives to the page's arrival"
    read_s = float(thrown[4].get("read_s") or SH.compiler().DOCK_READ_S)
    assert float(page[0]) == pytest.approx(float(thrown[2]) + read_s, abs=0.01), (page[0], thrown)
    # ... and the eye's arrival is over before the instant the parent read the base at
    assert float(page[0]) + SH.compiler().CAMERA_ARRIVAL_S < 77.8


def test_a_recast_arrives_building(tokyo):
    """THE FOURTH PASS, defect 2 (the parent, at 52.00 s): the approved recast grows its FIRST bar
    there; base v3 stood all four. E99 s67 Apply 2 - a chart never lands fully built - so a recast the
    author left un-keyed is emitted as the PLAIN hand-over the approved table writes (`keyed: false`,
    `build_scene_timeline_f.py:388`), and the arriving state draws on its own build envelope."""
    _, rows, why = tokyo
    casts = [(n, s) for n, r in enumerate(rows) for s in r[6] or []
             if s.get("kind") == "chart_to" and s.get("to") == "recast"]
    assert len(casts) == 2, casts
    for n, s in casts:
        assert s["keyed"] is False, s
        assert isinstance(s.get("dur"), (int, float)) and s["dur"] > 0, s
        assert "DRAWS ON ITS OWN BUILD ENVELOPE" in why[n]["rule"]


def test_a_recast_the_author_keys_keeps_its_key():
    """E64 stands where the AUTHOR asks for it: a keyed recast is the same data travelling, and the
    compiler never overwrites the key the plan names."""
    plan = _chained(moves=[{"kind": "chart_to", "at_word": "month", "dur": 1.4,
                            "options": {"to": "recast", "state": 1, "keyed": True}}])
    rows, _ = SH.compile(plan, _take(plan), SH.DEFAULTS, "16:9")
    cast = next(s for r in rows for s in r[6] or [] if s.get("kind") == "chart_to")
    assert cast["keyed"] is True, cast


def test_the_carried_retitle_reaches_the_returning_page(tokyo):
    """THE FOURTH PASS, defect 4 (the parent, at 50.30 s): the approved page reads "The opponent: a
    balance sheet" and the base still read the first title, because the deriver skipped the cut's
    CARRIED retitle - fired three seconds before its own scene, so the page ARRIVES retitled. The plan
    now names it on that scene's first word and the compiler realises it there."""
    plan, rows, _ = tokyo
    carried = [m for b in plan for m in SH.moves_of(b)
               if m.get("kind") == "retitle" and m.get("label") == "The opponent: a balance sheet"]
    assert len(carried) == 2, "the title is rewritten once on the page and carried onto its return"
    spiral = next(r for r in rows if SH.entry_in(r[2]) == "spiral")
    titles = [s for s in spiral[6] or [] if s.get("kind") == "retitle"]
    assert titles and titles[0]["text"] == "The opponent: a balance sheet", titles
    assert float(titles[0]["at"]) < 50.3, "the page reads the retitle by the instant the parent read"


def test_the_same_card_is_fine_once_the_page_snaps_up_out_of_it():
    plan = _thrown_card_plan("snap=dock-a-fed-rate")
    rows, _ = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert SH.entry_in(rows[-1][2]) == "snap", rows[-1][2]


def test_an_evidence_still_may_be_thrown_and_left_to_read():
    """E99 s67 Apply 5's other half: a DOCK is an evidence still, and a still is not a chart page."""
    plan = _thrown_card_plan("axes")
    plan[1]["moves"][0]["asset"] = "dock-c-blue-ties-panel"
    rows, _ = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert [str(d[0]) for d in rows[1][4]] == ["dock-c-blue-ties-panel"]


def test_a_move_kind_and_a_cards_options_are_the_compilers_own_vocabulary():
    """Never re-typed here: a move that is legal in the kit is legal in the compiler."""
    import build_scene_timeline_f as C
    assert set(SH.move_kinds()) == set(C.SPECIES_KINDS) | {SH.MOVE_DOCK}
    assert set(SH.dock_option_keys()) == set(C.DOCK_OPTS) | {SH.MOVE_SLOT}
    bad = [_rec(1, 0.0, 12.0, "plate-desk;idle=drift",
                moves=[{"kind": "glitter", "at_word": "A sentence"}])]
    with pytest.raises(SH.Refused) as e:
        SH.compile(bad, _take(bad), SH.DEFAULTS, "9:16")
    assert "beat 1" in str(e.value) and "glitter" in str(e.value)
    # The card's option: `place` was the unknown example until P69 T26d (5c6871c) made it a real option (a
    # PROP's authored box), and the plate-desk plan then failed earlier, on its opening skeleton's {page}.
    # So: a token the compiler still does not carry, on a plan that compiles without it (the control), so
    # the refusal is the option's own.
    unknown = "sparkle"
    assert unknown not in C.DOCK_OPTS, "pick another example: the compiler carries this option now"
    card = {"kind": "dock", "at_word": "month", "asset": "dock-x", "options": {"read_s": 1.2}}
    good = _chained(moves=[card])
    rows, _ = SH.compile(good, _take(good), SH.DEFAULTS, "9:16")
    assert [d[0] for d in rows[0][4]] == ["dock-x"], rows[0][4]
    worse = _chained(moves=[{**card, "options": {**card["options"], unknown: 1}}])
    with pytest.raises(SH.Refused) as e:
        SH.compile(worse, _take(worse), SH.DEFAULTS, "9:16")
    assert "beat 1" in str(e.value) and unknown in str(e.value) and "not the compiler's" in str(e.value)


def test_the_tokyo_beds_own_moves_close_the_base(tokyo):
    """The finding T3b answers (the parent, 2026-09-17): ONE skeleton row per authored group left
    the eleven-beat opening group with one event, and `event_gaps` read up to 32 s. The lever is the
    PLAN - the moves the approved cut actually carries - and never a looser gate. The ceiling here
    is a ceiling on the BASE, not M16's 2.5 s: the plan's density is the author's."""
    _, rows, _ = tokyo
    gaps = SH.event_gaps(rows)
    worst = max([g for _, g in gaps] or [0.0])
    assert worst < 10.0, gaps
    assert sum(len(r[6] or []) for r in rows) >= 20


def test_the_deriver_is_byte_stable_on_both_read_back_plans():
    """`derive_beat_moves.py --check` re-derives from the cut and exits 1 on drift: the plan and the
    approved cut it was read back from cannot quietly disagree."""
    import derive_beat_moves as D
    for build in (TOKYO, JAPAN):
        moves, skipped = D.derive(build)
        was, now = D.render(build, moves)
        assert was == now, f"{build.name}: the plan has drifted from its cut"
        assert D.main([str(build), "--check"]) == 0
        assert moves, "the approved cut carries species and cards, and the plan now names them"


def test_the_deriver_never_copies_a_compiled_place_back():
    """A compiled dock's `place` is the PIXEL BOX the placer chose ({x, y, w, h}). Since P69 T26d (5c6871c)
    `place` is also an authored option - a PROP's {x, y, w} in stage fractions - so the deriver's
    DOCK_OPTS copy began writing the box back into the read-back plans, a plan the compiler refuses
    ("place is a PROP's option"). The deriver transcribes what the author named, never what was derived."""
    import build_scene_timeline_f as C
    import derive_beat_moves as D
    assert "place" in SH.dock_option_keys() and "place" not in D.dock_option_fields()
    compiled = {"slide": "dock-x", "slot": 0, "enter": 1.0, "exit": 3.0, "read_s": 1.2, "park_s": 0.7,
                "place": {"x": 346, "y": 309, "w": 518, "h": 315}}
    move = D.dock_move(compiled, "A sentence", D.dock_option_fields())
    assert move["options"] == {"read_s": 1.2, "park_s": 0.7, SH.MOVE_SLOT: 0}, move
    C.dock_opts({k: v for k, v in move["options"].items() if k != SH.MOVE_SLOT})   # the compiler admits it
# ---------------------------------------------------------------- the fifth pass (P66 T3e)
def _tail_plan():
    """A page beat, then a second page beat: a plan whose cut ends on a PAGE, as the Tokyo bed's does."""
    page = "ledger:ev-a-v1:line:12:right"
    return [_rec(1, 0.0, 12.0, page, sentence="The page draws its line to the print.",
                 caps=["the page draws to datum 12"], row=1),
            _rec(2, 12.0, 20.0, page, sentence="And that is the number we live with.",
                 caps=["datum 12 holds"], row=1)]


def test_without_a_runtime_the_frozen_tail_is_named_in_why():
    """The v5 critic's tail row: the last row ends on the take's last word and the compiled scene
    runs to the build's runtime, so the seconds between play a still world no row admits to. With no
    runtime to hold to and no closing world in the plan, the compiler NAMES it and invents nothing."""
    plan = _tail_plan()
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert rows[-1][1] == pytest.approx(20.0), rows[-1]
    rule = SH.rows_why(why)[-1]["rule"]
    assert "the outro is the author's - the approved cut ends on its outro clip" in rule
    assert "build_scene_timeline_f.py:5162" in rule


def test_the_last_row_is_held_to_the_runtime_it_is_given_and_carries_an_idle():
    """The approved cut ends on an outro CLIP over exactly the seconds past the last word
    (`build_short.py:443-446`). A base whose plan names no outro at least says what will play: the
    last row is held to the build's own runtime and carries an idle (E49), rather than stopping at
    the last word while the timeline plays the world on to the runtime anyway."""
    plan = _tail_plan()
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16", runtime=26.2)
    assert rows[-1][1] == pytest.approx(26.2), rows[-1]
    assert SH.IDLE_OPT in rows[-1][2], rows[-1][2]
    rule = SH.rows_why(why)[-1]["rule"]
    assert "HELD to the build's own runtime (26.20s)" in rule and "6.20s of frozen world" in rule
    # ... and a runtime the row already reaches changes nothing
    same, _ = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16", runtime=20.0)
    assert same[-1][1] == pytest.approx(20.0), same[-1]


def test_a_closing_world_the_plan_names_is_the_cuts_last_row():
    """The mirror of the open: the hook's world reaches the table because the plan names it, and so
    does the outro's. Where the plan carries a closing world beat the row is the world, and the
    `why` says the cut ends on it - the compiler never invents one (the kit names no episode file)."""
    page = "ledger:ev-a-v1:line:12:right"
    plan = [_rec(1, 0.0, 12.0, page, sentence="The page draws its line to the print.",
                 caps=["the page draws to datum 12"], row=1),
            _rec(2, 12.0, 20.0, page, sentence="And that is the number we live with.", caps=["datum 12"], row=1),
            _rec(3, 20.0, 26.2, "clip:an-outro.mp4", sentence="It's not magic. It's mechanics.",
                 caps=["the outro card dissolves in"], row=2)]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert SH.world_of(rows[-1][2]) == "clip" and rows[-1][1] == pytest.approx(26.2), rows[-1]
    assert "the cut ends on the closing world the plan's last beat names" in SH.rows_why(why)[-1]["rule"]


def test_a_card_after_a_camera_push_keeps_the_pages_room(tokyo):
    """THE FIFTH PASS, the v5 critic's row 3 (79.50 s): `dock-j-tea-cup` parked INSIDE the Fed page's
    plot and covered the right half of the callout's own label *"3.97% - the February low"* - the one
    thing that beat exists to say. The page arrives by the camera pushing to a card
    (`camera=<dock>`), and after the push THE PAGE IS THE WORLD: the room rule binds exactly as it
    does on any page row. What the third pass missed is that a page's room is the page AS IT STANDS -
    and this row writes its own marks inside the plot while the card is up, none of which are in the
    page builder's measured ink. So the plot's holes are not room: the card takes a band outside it,
    or the page parks to make one (E65, the approved cut's own move)."""
    _, rows, why = tokyo
    row = rows[-1]
    assert SH.entry_in(row[2]).startswith("camera") or SH.entry_in(row[2]) == "camera", row[2]
    card = next(d for d in row[4] if d[0] == "dock-j-tea-cup")
    t_in = float(card[2])
    # the marks this row writes while the card is up, named - the callouts and the spread
    named = SH.marks_live(row[6] or [], t_in, float(card[3]))
    assert [n.split()[0] for n in named].count("callout") == 2 and any(n.startswith("spread") for n in named), named
    # ... so the page parks to make the room, and the card lands in the band the park frees
    park = [sp for sp in row[6] if sp.get("kind") == "chart_to" and sp.get("to") == "park"]
    assert park and float(park[0]["at"]) == pytest.approx(t_in - SH.PARK_LEAD_S, abs=0.01), park
    box = _card_box(card[4])
    page = _page(TOKYO, row[2])
    boxes = SH._boxes(page, "9:16", SH.park_scale_at(row[6], t_in))
    assert box and not SH._meets(box, boxes["plot"]), (box, boxes["plot"])
    for k in ("title", "sub", "source"):
        if boxes.get(k):
            assert not SH._meets(box, boxes[k]), (k, box, boxes[k])
    assert "takes no room inside the plot" in why[-1]["rule"]
    # ... and not on the page's HANDWRITING either: this row writes three notes in the quiet zone,
    # two of them still writing as the cup lands, and the fifth pass' first build landed the card on
    # all three of them (the probe at 79.50 s: 84 %, 45 % and 100 % of `page.note`).
    assert len(SH.quiet_live(row[6] or [], t_in, float(card[3]))) == 2, row[6]
    assert "takes no room in the page's quiet zone" in why[-1]["rule"]
    # the handwriting runs down the quiet zone beside the chart, so what is left is the band UNDER
    # the parked chart - and that is where the card lands (measured on the build at 79.50 s: the
    # probe reports no overlap between `dock-j-tea-cup` and `page.note`)
    assert box["y"] >= boxes["plot"]["y"] + boxes["plot"]["h"] - 1, (box, boxes["plot"])


def test_the_plots_holes_are_not_room_while_the_row_marks_them():
    """`rooms_of` itself: with a mark of the row's own live over the plot, the plot's empty rooms are
    off the table and only the bands outside it are offered (and a page with no free band then has
    no room at all, which is what sends the ladder to the park)."""
    page = _page(TOKYO, "ledger:ev-fed-vs-yields-v1:line:0:right")
    plain = SH.rooms_of(page, "9:16")
    marked = SH.rooms_of(page, "9:16", marked=True)
    assert plain and len(marked) < len(plain), (plain, marked)
    boxes = SH._boxes(page, "9:16")
    assert all(not SH._meets(r, boxes["plot"]) for r in marked), marked
    assert SH.marks_live([{"kind": "callout", "at": 1.0, "dur": 2.0}], 2.0, 4.0) == ["callout at 1.00s"]
    assert SH.marks_live([{"kind": "callout", "at": 1.0, "dur": 2.0}], 3.5, 6.0) == []
    assert SH.marks_live([{"kind": "retitle", "at": 1.0, "dur": 9.0}], 2.0, 4.0) == [], "a retitle is not a plot mark"
    # ... and the quiet zone is the note's while a note is up: that side's band is not offered
    note = [{"kind": "note", "at": 1.0, "dur": 2.0}]
    assert SH.quiet_live(note, 2.0, 4.0) == ["note at 1.00s"] and SH.quiet_live(note, 3.5, 6.0) == []
    hushed = SH.rooms_of(page, "9:16", marked=True, quiet_taken=True)
    band = next(b for b in SH.compiler().free_bands(boxes) if str(b.get("band")) == boxes["quiet_zone"])
    strips = SH.clear_strips(band, SH.page_ink(page, "9:16"))
    assert strips, "the quiet zone has room on this page when nothing is written in it"
    assert all(r in marked and r not in hushed for r in strips), (strips, hushed)


# --- THE INKS (E67 / E99 s72) -------------------------------------------------------------------
# The operator on base v7: *"the charts don't have their 'life' or Bravos lessons - we changed colors
# to be more visible on thumbnails if you recall."* MEASURED before these were written: a page's ink
# is a TOKEN in the episode's series file, resolved to a hex by the PLAYER's LP_INK table (E67's
# electric set), so the compiler cannot choose one - it reads what the page carries and says so.


def test_a_page_that_declares_no_ink_takes_e67s_electric_cycle():
    note = SH.ink_note({"series": [{"name": "a"}, {"name": "b"}]})
    assert note and not note.startswith("WARN")
    assert "ELECTRIC cycle" in note and "teal" in note and "grey is never a default" in note


def test_a_page_whose_inks_the_electric_table_cannot_resolve_is_WARNED_not_rewritten():
    note = SH.ink_note({"series": [{"color": "#c0392b"}, {"color": "teal"}]})
    assert note.startswith("WARN") and "predates E67" in note and "#c0392b" in note
    assert "never rewritten" in note, "the series file is the episode's (E99 s11)"


def test_a_page_that_is_all_deemph_is_WARNED_because_grey_is_never_a_default():
    note = SH.ink_note({"colors": ["deemph", "deemph"]})
    assert note.startswith("WARN") and "grey is never a default" in note


def test_a_page_that_names_its_own_e67_inks_is_named_and_passes():
    note = SH.ink_note({"colors": ["cobalt", "crimson"]})
    assert not note.startswith("WARN") and "cobalt, crimson" in note
    assert SH.ink_note(None) is None and SH.ink_note({}) is None


def test_page_inks_reads_every_list_a_page_spec_may_carry():
    assert SH.page_inks({"colors": ["teal"], "series": [{"color": "cobalt"}],
                         "bars": [{"color": "amber"}], "shares": [{"color": "crimson"}]}) == \
        ["teal", "cobalt", "amber", "crimson"]


def test_every_page_row_of_the_tokyo_base_names_its_inks_in_why():
    """The base the compiler emits carries E67's citation on every page row - the Tokyo bed's series
    declare `crimson` and `cobalt` (both E67 tokens: crimson is the Claude orange), so no row WARNs."""
    _plan, rows, why = _base(TOKYO)
    pages = [(r, w) for r, w in zip(rows, why) if str(r[2]).startswith("ledger:")]
    assert pages, "the Tokyo plan carries ledger pages"
    for row, w in pages:
        assert "E67, CAPABILITIES.md:34" in w["rule"], (row[2], w["rule"])
        assert "predates E67" not in w["rule"], (row[2], w["rule"])


# --- THE OUTRO ATTACHED (E41 / E99 s72) ---------------------------------------------------------
# *"You didn't attach the outro either."* The closing row is the PROJECT's outro row, and the row
# before it ends at `t_outro` - the approved cut's own shape (`build_short.py:443-446`).

OUTRO = {"world": "clip:outro-v2.mp4", "at": 82.62, "runtime": 88.82, "exit": "dip",
         "brand_line_at": 83.42, "source": "the test"}


def test_the_closing_row_is_the_projects_outro_and_the_row_before_it_ends_at_its_start():
    plan = SH.load_plan(TOKYO / "BEAT-PLAN.jsonl")
    rows, why = SH.compile(plan, _words(TOKYO), SH.DEFAULTS, "9:16",
                           pages=_pages(TOKYO), outro=OUTRO)
    recs = SH.rows_why(why)
    assert len(recs) == len(rows)
    last, before = rows[-1], rows[-2]
    assert (round(last[0], 2), round(last[1], 2)) == (82.62, 88.82)
    assert last[2] == "clip:outro-v2.mp4" and last[5] == "dip" and not last[4]
    assert last[6] == [{"kind": "life", "at": 82.62, "dur": 6.2}], "the clip's own seconds (M05)"
    assert round(before[1], 2) == 82.62, "the row before the outro ends on t_outro, not the last word"
    rule = recs[-1]["rule"]
    assert recs[-1]["skeleton"] == SH.OUTRO_SKELETON and recs[-1]["signature"] == "dip"
    assert "83.42s" in rule and "E41" in rule and "stitched" in rule, rule
    assert "the test" in rule, "the why names where the outro came from"


def test_without_an_outro_the_tail_is_the_runtime_hold_it_has_always_been():
    plan = SH.load_plan(TOKYO / "BEAT-PLAN.jsonl")
    rows, why = SH.compile(plan, _words(TOKYO), SH.DEFAULTS, "9:16",
                           pages=_pages(TOKYO), runtime=88.82)
    assert str(rows[-1][2]).startswith("ledger:") and round(rows[-1][1], 2) == 88.82
    assert SH.OUTRO_IS_THE_AUTHORS.split("(")[0].strip() in SH.rows_why(why)[-1]["rule"]


@pytest.mark.parametrize("outro, says", [
    ({"at": 1.0, "runtime": 2.0}, "names no world"),
    ({"world": "clip:x.mp4", "runtime": 2.0}, "names no at"),
    ({"world": "clip:x.mp4", "at": 1.0}, "names no runtime"),
    ({"world": "clip:x.mp4", "at": 5.0, "runtime": 5.0}, "is not past its start"),
])
def test_an_outro_the_caller_could_not_resolve_is_refused_by_name(outro, says):
    with pytest.raises(SH.Refused) as exc:
        SH.check_outro(outro)
    assert says in str(exc.value)


def test_an_outro_that_would_swallow_the_beat_before_it_is_refused():
    rows = [(0.0, 10.0, "ledger:x:line:0:right:axes:cut", (0, 0, 0), [], "cut", [])]
    why = [{"beat": 1, "skeleton": "s", "act": None, "rule": "r", "signature": "axes"}]
    with pytest.raises(SH.Refused) as exc:
        SH.close_the_cut(rows, why, None, {**OUTRO, "at": 0.0, "runtime": 6.0})
    assert "at or before the last row's own start" in str(exc.value)


# --- THE OUTRO NEVER TRUNCATES THE TAKE (the sixth pass' review, finding 4) ----------------------
# `close_the_cut(outro=)` read neither the caller's runtime nor the take's last word, so an outro
# resolved at 5 s for 12 s under a 40 s build silently cut 33 s of spoken take off the table and
# discarded the build's own runtime - with no refusal from the function whose job is refusals.

TRUNCATING = [(0.0, 3.0, "page:x", (0, 0, 0), [], "cut", []),
              (3.0, 38.0, "page:y", (0, 0, 0), [], "cut", [])]


def _tail_why(n: int) -> list[dict]:
    return [{"beat": i + 1, "skeleton": "s", "act": None, "rule": "r", "signature": "axes"} for i in range(n)]


def test_an_outro_whose_runtime_is_not_the_builds_is_refused_by_name():
    with pytest.raises(SH.Refused) as exc:
        SH.check_outro({**OUTRO, "at": 5.0, "runtime": 12.0}, runtime=40.0)
    assert "12.00s" in str(exc.value) and "40.00s" in str(exc.value), str(exc.value)
    SH.check_outro(OUTRO, runtime=OUTRO["runtime"])                    # the two agree: no refusal
    SH.check_outro(OUTRO, runtime=OUTRO["runtime"] + SH.EPS / 2)       # a rounding is not a disagreement


def test_an_outro_that_starts_before_the_takes_last_word_is_refused_and_the_rows_are_untouched():
    """The reviewer's input: rows to 38 s, an outro at 5 s - 33 s of spoken take under the card."""
    rows, why = [r for r in TRUNCATING], _tail_why(2)
    with pytest.raises(SH.Refused) as exc:
        SH.close_the_cut(rows, why, 12.0, {"world": "clip:o.mp4", "at": 5.0, "runtime": 12.0},
                         last_word_end=38.0)
    assert "5.00s" in str(exc.value) and "38.00s" in str(exc.value), str(exc.value)
    assert rows == TRUNCATING and len(why) == 2, "it REFUSES by name - it never truncates the take"


def test_the_approved_shape_is_not_refused_the_card_dissolves_in_over_the_last_word():
    """`audio.outro_clock`: `t_outro = t_vo_end - OUTRO_LEAD` (0.1 s on the approved cut) - the card
    begins its dissolve BEFORE the last word by design, so the guard is the dip's own length."""
    SH.check_outro(OUTRO, last_word_end=OUTRO["at"] + 0.1)
    SH.check_outro(OUTRO, last_word_end=OUTRO["at"] + SH.OUTRO_LEAD_MAX_S)
    with pytest.raises(SH.Refused):
        SH.check_outro(OUTRO, last_word_end=OUTRO["at"] + SH.OUTRO_LEAD_MAX_S + 0.5)


def test_the_generated_base_still_closes_on_the_outro_with_the_runtime_and_the_last_word_read():
    plan = SH.load_plan(TOKYO / "BEAT-PLAN.jsonl")
    ws = _words(TOKYO)
    last = max(float(w.get("end", w.get("end_s", 0)) or 0) for w in ws)
    rows, why = SH.compile(plan, ws, SH.DEFAULTS, "9:16", pages=_pages(TOKYO), outro=OUTRO,
                           runtime=OUTRO["runtime"], last_word_end=last)
    assert (round(rows[-1][0], 2), round(rows[-1][1], 2)) == (82.62, 88.82)
    assert round(rows[-2][1], 2) == 82.62


# --- A SERIES IN ITS SIGN COLOUR IS NOT PRE-E67 (the sixth pass' review, finding 8) --------------

def test_a_series_authored_in_its_sign_colour_is_not_warned_as_pre_e67():
    """E67 / CAPABILITIES.md:34 names the sign colours on the field (`#3DDC84` up, `#FF4D4D` down) and
    the engine resolves `var(--lp-neg)` / `var(--lp-pos)` like any other ink - so they are not the old
    palette. The raw hex still WARNs (the test above)."""
    for ink in SH.E67_SIGN:
        note = SH.ink_note({"series": [{"color": ink}, {"color": "teal"}]})
        assert note and "WARN" not in note, (ink, note)
        assert ink in note, note
    assert "WARN" in (SH.ink_note({"series": [{"color": "#c0392b"}]}) or ""), "a raw hex is still named"


# --- THE TRANSITION CHOOSER (P66 T3 seventh pass, E99 s74) ---------------------------------------
# The operator, 2026-09-17: *"the whole point of creating them was to improve our ability to live with
# less cuts and to be able to keep a directional flow"*. s74 Apply 1: between two worlds a cut or a dip
# is the LAST RESORT, taken only after every transform the record carries for that pair was refused BY
# NAME. These tests read the chain, not just the token.


OPEN_PAGE = "ledger:ev-open-v1:line:0:right"    # every plan opens on a page: the open IS the chart (E99 s67 Apply 6)
ACTS_BY_WORLD = {True: "QUOTES the figure", False: "EXPLAINS the mechanism"}


def _pair_plan(a: str, b: str):
    """A plan whose LAST boundary is the pair `a -> b`, and nothing else in the way.

    The open is always a page (the open skeletons fill `{page}` and refuse a plan that names none), and
    two beats on `a` keep it one row, so the boundary under test is the last one.
    """
    pre = [] if str(a).startswith("ledger:") else [_rec(1, 0.0, 8.0, OPEN_PAGE, sentence="The open is the chart.",
                                                        act="QUOTES the figure", row=0)]
    n = len(pre)
    beats = pre + [
        _rec(n + 1, 8.4 * (n + 0), 8.0 + 8.4 * n, a, sentence="The first world says a number.",
             act=ACTS_BY_WORLD[str(a).startswith("ledger:")], row=1),
        _rec(n + 2, 8.4 * (n + 1), 16.4 + 8.4 * n, b, sentence="And here is the other thing.",
             act=ACTS_BY_WORLD[str(b).startswith("ledger:")], row=2)]
    for i, r in enumerate(beats):      # one contiguous take, whatever the prefix
        r["t0"], r["t1"] = round(i * 8.4, 2), round(i * 8.4 + 8.0, 2)
    return beats


def _chain_of(plan, i: int | None = None) -> tuple[dict, list[str]]:
    """(the flow record of row i - the LAST row by default - and its refusal chain)."""
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    recs = SH.rows_why(why)
    t = recs[len(recs) - 1 if i is None else i]["transition"]
    return t, list(t["chain"])


def test_the_boundary_belongs_to_the_incoming_row(tokyo):
    """THE CONVENTION, `build_scene_timeline_f.py:2185`: *"`exit` names the transition INTO the scene it
    sits on - so the boundary between scenes[i-1] and scenes[i] is scenes[i]['exit']"*; `:5030` (*"the
    row's EXIT (the transition INTO it, E47)"*) and R26-60 `:2193` (*"the transition into scenes[i] TAKES
    the outgoing world, scenes[i-1]"*). Passes 1-6 wrote the token on the OUTGOING row, so every
    transition landed one boundary early (the base played a dip INTO its own mount). The row's `why` now
    names the pair it joins, and row 0 carries no token at all."""
    _, rows, why = tokyo
    assert rows[0][5] is None, "nothing precedes the first world, so it carries no transition"
    assert why[0]["transition"]["taken"] == "the open"
    for i, (r, w) in enumerate(zip(rows, why)):
        t = w["transition"]
        if i == 0:
            continue
        assert t["exit"] == r[5], (i, t, r[5])
        if t["taken"] != "the open":
            assert t["pair"].endswith(SH.pair_of({"world": SH.world_of(str(rows[i - 1][2])), "plate": rows[i - 1][2]},
                                                 {"world": SH.world_of(str(r[2])), "plate": r[2]}).split("->")[1]) \
                   or "outro" in t["pair"], (i, t["pair"])


# every transform the record carries for each pair, in the order the chain tries them - so a dip's own
# record can be read against the FULL set rather than against "at least one refusal" (the seventh pass'
# review M3: the old assertion passed on the very input that proved H1)
PAIR_TRANSFORMS = {
    "page->page": ("recast", "rescale", "morph", "melt-then-splash"),
    "page->plate": ("melt-then-splash", "the door", "the suck"),
    "plate->page": (),          # the arrivals carry this pair; the chain names each one it is not
    "plate->plate": (),         # the continuity three, named as one line (each is the plan's to name)
}


def test_a_dip_is_never_chosen_while_a_transform_is_available(tokyo, japan):
    """s74 Apply 1: the dip is the LAST RESORT, *"taken only after every transform the record carries for
    that pair was refused BY NAME"*. So every dip owes a `REFUSED` line for EACH transform of its pair -
    and a DEFERRED one (the variety rule's preference) is not a refusal: the chain that hits one goes on
    and cashes it rather than dipping (the eighth pass, the review's H1)."""
    for _, rows, why in (tokyo, japan):
        for w in SH.rows_why(why):
            t = w.get("transition") or {}
            if str(t.get("exit") or "").split(":")[0] != "dip":
                continue
            assert t["kind"] == SH.LAST_RESORT, t
            chain = list(t["chain"])
            assert not any("DEFERRED" in line for line in chain), \
                f"a dip was taken while a transform stood deferred by the variety rule: {chain}"
            for name in PAIR_TRANSFORMS[t["pair"]]:
                assert any(line.startswith(f"{name}: REFUSED") for line in chain), (name, chain)
            if not PAIR_TRANSFORMS[t["pair"]]:
                assert any("REFUSED" in line for line in chain), chain


def test_the_variety_rule_never_sends_an_admissible_transform_to_a_dip():
    """THE REVIEWER'S OWN FAILING INPUT (the seventh pass' review H1), as a test. Two page -> clip
    boundaries with a page between them: the melt is refused by name both times (a video is not painted)
    and the door has no card to open, so the suck is the only transform the record carries for the pair -
    and the variety rule refused it outright, which sent the second boundary to a DIP while the suck was
    admissible by every rule R26-60/E88 state. s74 Apply 1: *"a cut or a dip is the last resort"* - the
    answer to "do not play it twice" is never "then dip"."""
    plan = [_rec(1, 0.0, 8.0, "ledger:ev-a-v1:line:12:right", sentence="The page says a number.", row=1),
            _rec(2, 8.4, 16.4, "clip:c-one.mp4", sentence="And here is the first clip.", row=2),
            _rec(3, 16.8, 24.8, "ledger:ev-b-v1:bars:3:right:axes:cut", sentence="The second page counts it.", row=3),
            _rec(4, 25.2, 33.2, "clip:c-two.mp4", sentence="And here is the second clip.", row=4)]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    recs = [w["transition"] for w in SH.rows_why(why)]
    assert [r["taken"] for r in recs[1:]] == ["the suck", "the axes open", "the suck"], recs
    assert str(rows[3][5]).split(":")[0] == "suck", rows[3][5]
    for r in recs:
        assert str(r["exit"] or "") != SH.DIP_EXIT, r
    # ... and the deferral names the boundary it actually compares against - the world change that TOOK a
    # transform, by index and by instant. The seventh pass said "the boundary before this one" of a melt
    # five boundaries back (the review's H1.2); boundary 2 here was an arrival, not a suck.
    deferred = [c for c in recs[3]["chain"] if c.startswith("the suck: DEFERRED")]
    assert len(deferred) == 1, recs[3]["chain"]
    assert "the world change into world 2 at 8.40s" in deferred[0], deferred[0]
    assert "the boundary before this one" not in " ".join(recs[3]["chain"])
    assert any("the suck: TAKEN" in c and "the repeat stands" in c for c in recs[3]["chain"]), recs[3]["chain"]


def test_the_pair_of_pages_refuses_recast_rescale_and_morph_by_name():
    """s74 Apply 1 names the chain for a page-to-page boundary: recast, rescale, morph, then
    melt-then-splash. Each refusal is BY NAME with its own reason - CAPABILITIES.md:106 for the two
    chart verbs (they retarget or re-form ONE page, inside its row), and no approved skeleton for the
    morph (E99 s70 Apply 2)."""
    plan = _pair_plan("ledger:ev-a-v1:line:12:right", "ledger:ev-b-v1:bars:0:right")
    t, chain = _chain_of(plan)
    assert t["pair"] == "page->page", t
    assert [c.split(":")[0] for c in chain[:4]] == ["recast", "rescale", "morph", "melt-then-splash"], chain
    assert "REFUSED" in chain[0] and "CAPABILITIES.md:106" in chain[0]
    assert "REFUSED" in chain[1] and "CAPABILITIES.md:106" in chain[1]
    assert "REFUSED - no approved skeleton" in chain[2] and "CAPABILITIES.md:118" in chain[2]


def test_morph_is_refused_by_name_and_never_emitted(tokyo, japan):
    """E99 s70 Apply 2 (*"a vocabulary written from memory is refused"*) and the survivorship audit
    (2026-09-17: `morph` is in NO cut): `morph_to` is LIVE, has no approved skeleton and is therefore
    named in the chain and never written as a token.

    THE CALENDAR PLAN IS READ HERE TOO, and it is the bed that carries the claim (the ninth pass): an
    AUTHORED entry now stands on every page (E99 s66), and the mount, the snap, the camera arrival and
    the spiral are all rung 0 of `choose_transition` - the arrival IS the transition (E45, E99 s70), so a
    boundary between two of them never reaches the chain at all. Tokyo's and Japan's plans declare a
    continuity entry on every page, so the pair that owes the refusal chain is the calendar's own
    page-to-page (`:axes` to `:axes`), where the clock's entry and the plan's agree.
    """
    plan = SH.load_plan(CALENDAR / "BEAT-PLAN.jsonl")
    rows, raw = SH.compile(plan, _words(CALENDAR), SH.DEFAULTS, "9:16", pages=_pages(CALENDAR))
    calendar = (plan, rows, SH.rows_why(raw))
    seen = 0
    for _, rows, why in (tokyo, japan, calendar):
        for r in rows:
            assert str(r[5] or "").split(":")[0] != "morph", r
        for w in SH.rows_why(why):
            seen += sum(1 for c in (w.get("transition") or {}).get("chain", [])
                        if c.startswith("morph: REFUSED - no approved skeleton"))
    assert seen, "a page-to-page boundary owes the morph's refusal by name"


def test_the_melt_holds_onto_a_plate_and_is_refused_onto_a_clip():
    """E88 / CAPABILITIES.md:37: a `splash:plate` paints the next NARRATIVE PLATE up through its stains,
    so it holds page -> plate; a clip is not painted, and that refusal is by name."""
    t, chain = _chain_of(_pair_plan("ledger:ev-a-v1:line:12:right", "plate-desk"))
    assert t["pair"] == "page->plate" and t["exit"] == SH.MELT_PLATE, t
    assert t["kind"] == SH.TRANSFORM
    # ... and onto a CLIP the melt is refused by name and the chain falls through to the suck, which is
    # exactly what the approved cut plays there (its own `s03`: the page spins into a point and a CLIP is
    # standing behind it) - the boundary still costs no dip
    t2, chain2 = _chain_of(_pair_plan("ledger:ev-a-v1:line:12:right", "clip:a-clip.mp4"))
    assert t2["taken"] == "the suck" and t2["exit"].split(":")[0] == "suck", t2
    assert any("a video is not painted" in c for c in chain2), chain2
    assert any(c.startswith("the door: REFUSED") for c in chain2), chain2


def test_the_melt_into_a_chart_is_refused_where_the_plan_declares_the_page_s_own_arrival():
    """E88: a `splash:chart`'s page arrives out of the splatter, `built`. E99 s66: the plan is the
    intelligence - so where the plan DECLARES the incoming page's arrival the melt is refused by name
    rather than overwriting it, and where the plan declares none the compiler takes the melt and the
    page arrives `built` (the record says so on the row)."""
    declared = _pair_plan("ledger:ev-a-v1:line:12:right", "ledger:ev-b-v1:line:3:right:axes:cut")
    t, chain = _chain_of(declared)
    assert t["exit"] == SH.CUT_EXIT and t["taken"] == "the axes open", t
    assert any("declares the page's own arrival" in c for c in chain), chain
    plain = _pair_plan("ledger:ev-a-v1:line:12:right", "ledger:ev-b-v1:line:3:right")
    rows, why = SH.compile(plain, _take(plain), SH.DEFAULTS, "9:16")
    t2 = SH.rows_why(why)[1]["transition"]
    assert t2["exit"] == SH.MELT_CHART, t2
    assert t2["entry"] == SH.BUILT_ENTRY
    assert SH.entry_in(rows[1][2]) == "built", rows[1][2]


def test_a_plate_to_page_boundary_is_carried_by_the_arrival_and_never_by_a_dip():
    """s74 Apply 1-2 and the approved cuts themselves: every one of them CUTS into its pages (the mount,
    the snap, the camera push, the axes, the spiral), so a plate -> page boundary is the arrival's and a
    dip there is the compiler's own invention. The refusal chain names each arrival it is not."""
    t, chain = _chain_of(_pair_plan("plate-desk", "ledger:ev-b-v1:line:3:right:axes:cut"))
    assert t["pair"] == "plate->page" and t["exit"] == SH.CUT_EXIT and t["kind"] == SH.ARRIVAL, t
    assert t["taken"] == "the axes open"
    assert [c.split(":")[0] for c in chain] == ["the snap", "throw-then-zoom", "throw-then-push",
                                               "object-becomes-chart", "the spiral return", "the axes open"], chain
    assert all("REFUSED" in c for c in chain[:-1]) and "TAKEN" in chain[-1]


def test_a_plate_to_plate_boundary_keeps_the_dip_and_names_the_continuity_three():
    """E47 - the dip is the transition when the WORLD actually changes, and plate to plate is the pair it
    is for. CAPABILITIES.md:108 (HF-15/16/17, the continuity three) is what could carry one plate into
    another instead, and each of the three is the PLAN's to name (E99 s70 Apply 2) - so the dip's own
    record names them as refused rather than pretending none exist."""
    t, chain = _chain_of(_pair_plan("plate-desk", "plate-vault"))
    assert t["pair"] == "plate->plate" and t["exit"] == SH.DIP_EXIT and t["kind"] == SH.LAST_RESORT, t
    assert any("the continuity three: REFUSED" in c and "CAPABILITIES.md:108" in c for c in chain), chain


def test_the_variety_rule_defers_the_same_transform_twice_running_and_the_chain_goes_on():
    """E88's own use-when (*"never as a mechanical wipe"*) through P66 T2's variety rule: the transform
    that carried the last world change a transform carried is DEFERRED where another one holds, so a run
    of page -> plate boundaries alternates instead of melting every time. It defers rather than refuses
    (the eighth pass): a preference may reorder the chain, never end it at a dip."""
    plan = [_rec(1, 0.0, 8.0, "ledger:ev-a-v1:line:12:right", sentence="The page says a number.", row=1),
            _rec(2, 8.4, 16.4, "plate-desk", sentence="And here is the desk.", row=2),
            _rec(3, 16.8, 24.8, "ledger:ev-b-v1:line:3:right:axes:cut", sentence="The second page counts it.", row=3),
            _rec(4, 25.2, 33.2, "plate-vault", sentence="And here is the vault.", row=4)]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    taken = [(w["transition"]["taken"], w["transition"]["exit"]) for w in SH.rows_why(why)]
    assert taken[1][1] == SH.MELT_PLATE, taken
    assert taken[3][0] == "the suck", taken
    chain = SH.rows_why(why)[3]["transition"]["chain"]
    assert any(c.startswith("melt-then-splash: DEFERRED - a repeat of the transform that carried the world change "
                            "into world 2 at 8.40s") for c in chain), chain


def _engine_scenes(rows: list[tuple]) -> list[dict]:
    """The compiler's rows as the SCENE dicts `build_scene_timeline_f.door_boundary_error` reads - its
    span, its exit and its docks' own `enter`/`exit`, the three fields that rule touches. Built here
    rather than through `compile_table` so the assertion is on the engine's rule, not on a whole build."""
    return [{"span": [round(float(r[0]), 2), round(float(r[1]), 2)], "exit": r[5],
             "docks": [{"slide": d[0], "enter": round(float(d[2]), 2), "exit": round(float(d[3]), 2)}
                       for d in (r[4] or [])]} for r in rows]


def _door_plan():
    """A plan the door HOLDS on: a page, a plate that throws a card, the page that IS that card
    (`snap=`), then the plate the card swings open onto. The reference door cut has exactly this shape -
    its `s07 exit:door:right` sits on the PLATE row that consumes the page before it, and neither its
    s06 nor its s07 carries a dock (the evidence-free boundary, doc 29 Part 6)."""
    return [_rec(1, 0.0, 8.0, "ledger:ev-a-v1:line:12:right", sentence="The page says a number.", row=1),
            _rec(2, 8.4, 16.4, "plate-desk", sentence="And here is the desk in July.", row=2,
                 moves=[{"kind": "dock", "asset": "dock-x-receipt", "at_word": "July",
                         "options": {"arrive": "throw"}}]),
            _rec(3, 16.8, 24.8, "ledger:ev-b-v1:bars:3:right:snap=dock-x-receipt",
                 sentence="The second page counts it.", row=3),
            _rec(4, 25.2, 33.2, "plate-vault", sentence="Down in the vault it is counted.", row=4)]


def test_the_door_is_taken_on_the_plate_row_that_consumes_the_page_the_card_became():
    """E98 s7 / CAPABILITIES.md:38 and the reference cut's own `s07 exit:door:right`. The TAKEN branch was
    unexercised by every earlier pass (the seventh pass' review M1): the only door assertion was a
    refusal. Here the outgoing page arrived by a SNAP, so there is a card to swing, and the door lands on
    the PLATE row - the row that consumes the page - never on the page's own row."""
    plan = _door_plan()
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    recs = [w["transition"] for w in SH.rows_why(why)]
    assert [r["taken"] for r in recs] == ["the open", "melt-then-splash", "throw-then-zoom", "the door"], recs
    assert rows[3][5] == SH.DOOR_EXIT and SH.world_of(str(rows[3][2])) == "plate", rows[3]
    assert SH.entry_in(str(rows[2][2])) == "snap", rows[2][2]        # the page the door's card became
    assert recs[3]["kind"] == SH.TRANSFORM and recs[3]["pair"] == "page->plate"
    assert any(c.startswith("the door: TAKEN") and "swings open on its hinge" in c for c in recs[3]["chain"])
    # ... and the engine would ACCEPT it: its own `door_boundary_error` reads None on that boundary
    scenes = _engine_scenes(rows)
    assert SH.compiler().door_boundary_error(scenes[2], scenes[3]) is None, scenes[2:4]


def test_a_door_is_refused_by_name_where_the_engine_s_own_boundary_rule_would_refuse_it():
    """`build_scene_timeline_f.door_boundary_error` rule 2 (doc 29 Part 6): a door swings on an
    EVIDENCE-FREE boundary, and a card landing inside the swing is a `ValueError` - *"let the card leave
    by the boundary ... or land after the door has opened, or say dip"*. `shapes` places the cards itself,
    so a door it emitted onto such a boundary died inside `compile_table` as a `[FAIL] compile` with an
    engine message instead of standing in the chain as a named refusal (the review's M1). Now the chain
    refuses it in the engine's own words and falls through to the suck - the boundary still costs no dip."""
    plan = _door_plan()
    plan[3] = _rec(4, 25.2, 33.2, "plate-vault", sentence="Down in the vault it is counted.", row=4,
                   moves=[{"kind": "dock", "asset": "dock-y-ledger", "at_word": "Down"}])
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    t = SH.rows_why(why)[3]["transition"]
    assert t["taken"] == "the suck" and str(rows[3][5]).split(":")[0] == "suck", (t["taken"], rows[3][5])
    door = [c for c in t["chain"] if c.startswith("the door: REFUSED")]
    assert door and "EVIDENCE-FREE boundary (doc 29 Part 6" in door[0], t["chain"]
    assert "lands inside the swing" in door[0] and "dock-y-ledger" in door[0], door[0]
    assert "or say dip" in door[0], door[0]


def test_the_flow_read_counts_the_world_changes_by_what_carried_them(tokyo):
    """s74 Apply 3 (R26-189, a READ and no gate yet): the cut-and-dip share of the cut's world changes,
    each named with the transform that carried it or the refusal that left a cut. The line is what
    `generate_base_table.py` prints under the mix and `BASE-TABLE.md` carries."""
    _, rows, why = tokyo
    flow = SH.flow_count(why)
    assert flow["boundaries"] == len(rows) - 1, flow
    assert sum(flow["transforms"].values()) + sum(flow["arrivals"].values()) + sum(flow["last_resort"].values()) \
           == flow["boundaries"]
    assert sum(flow["tokens"].values()) == flow["boundaries"]
    assert flow["cuts_and_dips"] == flow["tokens"].get("cut", 0) + flow["tokens"].get("dip", 0)
    line = SH.flow_line(flow)
    assert line.startswith(f"flow: {flow['boundaries']} world changes - transforms ")
    assert "cuts+dips" in line and "tokens" in line


def test_the_read_back_base_carries_fewer_cuts_and_dips_than_it_did(tokyo, japan):
    """The measure s74 Apply 3 asks for, on the two regression beds: before this pass the compiler wrote
    a dip at every world change that was not a page pair (Tokyo 2, Japan 7) and one of them was a dip
    INTO a mount. The transforms and the arrivals now carry them."""
    tok = SH.flow_count(tokyo[2])
    jap = SH.flow_count(japan[2])
    assert tok["tokens"].get("dip", 0) == 0, tok
    assert jap["tokens"].get("dip", 0) == 1, jap          # the one plate -> plate pair: E47's own
    assert tok["tokens"].get("melt", 0) == 1 and jap["tokens"].get("melt", 0) == 2
    assert jap["tokens"].get("suck", 0) == 2


# ---------------------------------------------------------------- P66 T3 NINTH PASS: the authored entry
# stands, and a park never covers the plan's own transform (E99 s66; s74 Apply 4; E45; E76 / E99 s56)

def test_an_authored_entry_stands_over_the_clocks_own():
    """E99 s66 - the plan is the intelligence. The plan writes `mount=0.79` on a page whose number lands
    at +0.0 s, where the CLOCK would write the axes entry, and the mount stands: the page rises over the
    plate that was there (E45 - the mount IS the transition) and the row's `why` names what the clock
    would have written instead.

    This is the director-critic's world change 3 on the calendar base (16.90 s): *"the page replaces a
    room instead of rising over it"*, and its cause was the compiler's landing clock overwriting the
    plan's own token.
    """
    page = "ledger:ev-b-v1:bars:0:right:mount=0.79:cut"
    plan = [_rec(1, 0.0, 6.0, OPEN_PAGE, sentence="The open is the chart itself.", act="QUOTES the figure"),
            _rec(2, 6.4, 12.0, "plate-desk;idle=drift", caps=["the world the page mounts over"]),
            _rec(3, 12.4, 15.0, page, sentence="The number is right here now.", act="QUOTES the figure"),
            _rec(4, 15.4, 22.0, page, sentence="And it stands there for a while.", act="QUOTES the figure")]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert SH.entry_in(rows[2][2]) == "mount" and "mount=0.79" in rows[2][2], rows[2][2]
    rule = SH.rows_why(why)[2]["rule"]
    assert "the author's own `mount=0.79`" in rule and "the clock alone would have written axes" in rule
    assert SH.DEPARTURE_MARK not in rule, "the entry STOOD - a departure is owed only where it cannot"
    # E45: the mount IS the transition into that row, and it is never dipped into
    assert rows[2][5] == "cut", rows[2]
    assert SH.rows_why(why)[2]["transition"]["taken"] == "the mount"


def test_an_authored_axes_entry_stands_where_the_clock_wants_the_mount():
    """The same rule the other way round: the plan writes `:axes` on a page whose number lands 7 s or
    more after its entry, where the clock would write a mount, and the AUTHORED axes stands. The clock
    decides only where the plan declares nothing at all."""
    page = "ledger:ev-a-v1:bars:0:right:axes:cut"
    plan = [_rec(1, 0.0, 9.0, page, sentence="The page opens on nothing much at all.",
                 act="none of the 11 - it states the claim"),
            _rec(2, 9.4, 18.0, page, sentence="Now the number is twelve percent.", act="QUOTES the figure")]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    assert SH.entry_in(rows[0][2]) == "axes", rows[0][2]
    rule = SH.rows_why(why)[0]["rule"]
    assert "the author's own `axes`" in rule and "the clock alone would have written mount" in rule


def test_an_authored_mount_with_no_world_under_it_is_a_named_departure():
    """s74 Apply 4: where the authored entry's OWN rules refuse it the compiler writes the clock's and
    the row owes a `BASE DEPARTURE` line naming the plan's token and the reason - never a silent
    replacement. A mount rises over the world that was there (E45), and the cut's first frame has none."""
    page = "ledger:ev-a-v1:bars:0:right:mount=0.79:cut"
    plan = [_rec(1, 0.0, 9.0, page, sentence="The page opens on the chart itself.",
                 act="none of the 11 - it states the claim"),
            _rec(2, 9.4, 18.0, page, sentence="Now the number is twelve percent.", act="QUOTES the figure")]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    rec = SH.rows_why(why)[0]
    assert SH.entry_in(rows[0][2]) != "mount", rows[0][2]
    assert SH.DEPARTURE_MARK in rec["rule"] and "mount=0.79" in rec["rule"], rec["rule"]
    assert "none under it" in rec["rule"] and "E45" in rec["rule"]
    assert rec["departure"]["token"] == "mount=0.79" and rec["departure"]["beat"] == 1
    assert rec["departure"]["wrote"] in ("axes", "mount", "spiral")


def test_a_move_before_an_authored_entrys_landing_is_held_to_it():
    """The other half of the rule: the clock adjusts the MOVES around the author's entry, never the
    entry. A light or a number that would fire before the page's chart lands is HELD to the landing -
    a light is never fired over a build (E99 s67 Apply 2) and a number is never written on a chart that
    is not drawn (E50) - and the row's `why` says so."""
    page = "ledger:ev-a-v1:bars:0:right:mount=2.0:cut"
    plan = [_rec(1, 0.0, 6.0, "plate-desk;idle=drift", caps=["the world the page mounts over"]),
            _rec(2, 6.4, 20.0, page, sentence="The number here is worth a long look indeed.",
                 act="QUOTES the figure",
                 moves=[{"kind": "spotlight", "at_word": "number", "target": {"kind": "datum", "index": 0},
                         "dur": 1.1}])]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    t0, land = rows[1][0], SH.page_land_offset("mount", 2.0)
    lights = [s for s in rows[1][6] if s["kind"] == "spotlight"]
    assert lights, rows[1][6]
    assert min(float(s["at"]) for s in lights) >= round(t0 + land, 2) - 1e-6, (t0, land, lights)
    assert "is HELD from" in SH.rows_why(why)[1]["rule"]


def test_a_park_never_covers_the_transform_the_plan_named():
    """THE CRITIC's row 11 on the calendar base: the plan's `chart_to compare` (E76 / E99 s56 - the melt
    that splashes into 3x) compiled at its own instant and NOTHING PLAYED, because the placer had parked
    the page for a card and un-parked it 0.30 s after the transform began. A transform is the plan's own
    sentence and keeps its instant; the card's room moves around it (E99 s66), and the page stands full
    size for the whole of it - the un-park LANDS as the transform starts."""
    page = "ledger:ev-into-vs-after-v1:bars:0:right:axes:cut"   # a REAL page (the calendar's own), read-only
    plan = [_rec(1, 0.0, 9.0, page, sentence="The open is the chart and it says a number.",
                 act="QUOTES the figure"),
            _rec(2, 9.4, 24.0, page, sentence="The card lands here and the chart turns later on.",
                 act="TURNS on the reveal",
                 moves=[{"kind": "dock", "at_word": "card", "asset": "dock-a-thing",
                         "options": {"centre": True, "read_s": 1.2, "park_s": 0.7}},
                        {"kind": "chart_to", "at_word": "later", "dur": 0.9,
                         "options": {"to": "compare", "form": "melt", "then": "splash", "hold": "gone",
                                     "metric": {"value": 6.8, "text": "+6.8%", "label": "into it"},
                                     "comparator": {"value": 3.0909, "text": "3x", "label": "what it means"},
                                     "inputs": {"a": 6.8, "b": 2.2}, "derive": "a / b",
                                     "source": "[DERIVED: a fixture's own arithmetic, 6.8 / 2.2]"}}])]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16", pages=_pages(CALENDAR))
    row = next(r for r in rows if any(s.get("to") == "compare" for s in r[6]))
    melt = next(s for s in row[6] if s.get("to") == "compare")
    a, z = float(melt["at"]), round(float(melt["at"]) + float(melt["dur"]) + SH.chart_to_settle(melt), 2)
    parks = [s for s in row[6] if s.get("to") == "park"]
    assert parks, "the fixture's card has no room of its own, so the page parks to make one"
    assert not [s for s in parks if a - 1e-6 <= float(s["at"]) <= z + 1e-6], (a, z, parks)
    # ... and the page is back at full size BY the transform's own start
    assert SH.park_scale_at(row[6], a) == SH.UNPARK_SCALE, parks
    assert all(float(s["at"]) + SH.PARK_DUR_S <= a + 1e-6 for s in parks), parks


def test_the_engines_own_settle_is_read_and_never_re_typed():
    """`chart_to_settle` is the ENGINE's clock: a state change is still drawing its target's build after
    its window (`scene-evidence-engine.mjs` lpPaintStates, mirrored as `gate_motion_density.LP_BUILD_S`),
    and the two verbs that change no state land inside their own window."""
    assert SH.chart_to_settle({"to": "recast"}) == MD.LP_BUILD_S
    for kind in SH.CHART_TO_NO_STATE:
        assert SH.chart_to_settle({"to": kind}) == 0.0


# ------------------------------------------------------------- P66 T3 TENTH PASS: the entry the plan
# wrote stands at EVERY boundary, a held light never outlives its own sentence, and a park that cannot
# un-park is refused (the T3j review's two HIGH and four MEDIUM findings)

def test_the_splash_never_writes_over_the_entry_the_plan_wrote():
    """E88 asks a `splash:chart`'s page to arrive out of the splatter, `built`; E99 s66 says the entry the
    PLAN wrote is the plan's statement of how that world arrives. So the transform that DEMANDS an arrival
    is refused BY NAME where the plan already named one - the chain goes on - and where the plan named
    none the compiler takes `built` and marks it as the COMPILER's own, so the landing clock treats it as
    its own choice (a move before that landing is refused, never held to it).

    The T3j review's HIGH 1: the boundary wrote the owed entry over the row's on a comment that said *"and
    the plan declared none"* and never checked it - no departure line, and the landing clock then ran on a
    token the plan never wrote.
    """
    declared = _pair_plan("ledger:ev-a-v1:line:12:right", "ledger:ev-b-v1:line:3:right:axes:cut")
    rows, why = SH.compile(declared, _take(declared), SH.DEFAULTS, "9:16")
    rec = SH.rows_why(why)[-1]
    assert SH.entry_in(rows[-1][2]) == "axes", rows[-1][2]
    assert SH.BUILT_ENTRY not in str(rows[-1][2]), rows[-1][2]
    assert rec["transition"]["entry"] is None, rec["transition"]
    assert any("melt-then-splash: REFUSED" in c and "declares the page's own arrival" in c
               for c in rec["transition"]["chain"]), rec["transition"]["chain"]
    # ... and where the plan wrote NO entry the `built` is taken, and named as the COMPILER's
    plain = _pair_plan("ledger:ev-a-v1:line:12:right", "ledger:ev-b-v1:line:3:right")
    rows2, why2 = SH.compile(plain, _take(plain), SH.DEFAULTS, "9:16")
    assert SH.entry_in(rows2[-1][2]) == SH.BUILT_ENTRY, rows2[-1][2]
    assert "the COMPILER's own" in SH.rows_why(why2)[-1]["rule"], SH.rows_why(why2)[-1]["rule"]
    # the one reading both sides share: the landing clock holds a move only for an entry the PLAN wrote
    assert SH.entry_is_authored({"plate": "ledger:ev-b-v1:line:3:right:axes:cut"}) is True
    assert SH.entry_is_authored({"plate": "ledger:ev-b-v1:line:3:right"}) is False
    assert SH.entry_is_authored({"plate": "ledger:ev-b-v1:line:3:right",
                                 "entry": SH.BUILT_ENTRY, "entry_compiler": True}) is False


def test_a_light_held_to_the_landing_never_outlives_the_sentence_it_points_with():
    """E50 / E99 s67 Apply 1: a light lives with the SENTENCE it points with, and a figure is a number
    written at the instant it is spoken. So the hold to an authored entry's landing is bounded by the
    move's OWN BEAT, never by the row: where the entry lands after the sentence ends, the move is dropped
    BY NAME rather than fired at a word that has already gone by.

    The T3j review's HIGH 2, measured: a spotlight on beat 2 (6.4-8.6 s) held to 11.50 s - 2.9 s past its
    own sentence, inside beat 3's - on a `mount=2.0` page whose chart lands 5.5 s after the row's start.
    """
    page = "ledger:ev-a-v1:bars:0:right:mount=2.0:cut"
    plan = [_rec(1, 0.0, 6.0, "plate-desk;idle=drift", caps=["the world the page mounts over"]),
            _rec(2, 6.4, 8.6, page, sentence="The number is right here.", act="QUOTES the figure",
                 moves=[{"kind": "spotlight", "at_word": "number", "target": {"kind": "datum", "index": 0},
                         "dur": 1.1}]),
            _rec(3, 9.0, 20.0, page, sentence="And the rest of it takes a while to say indeed.",
                 act="QUOTES the figure")]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16")
    row = rows[_first_page(rows)]
    land = round(float(row[0]) + SH.page_land_offset("mount", 2.0), 2)
    assert land > 8.6, ("the fixture only bites where the landing is past the sentence", land)
    lights = [s for s in row[6] if s["kind"] in SH.LIGHT_KINDS]
    assert not [s for s in lights if float(s["at"]) >= 8.6], (land, lights)
    rule = SH.rows_why(why)[_first_page(rows)]["rule"]
    assert "its own sentence" in rule and "point at nothing" in rule, rule


def test_the_departure_is_keyed_by_the_beat_whose_own_plate_declared_the_entry():
    """One key on both sides (the T3j review's MEDIUM 3): the compiler records a departure on the beat
    whose OWN PLATE carried the token - which is the beat `gate_one_shot_floor`'s M45 owes the mechanism
    to and looks the reason up on (`base_departures`) - and never on the row's first beat, which on the
    absorbed open is the HOOK's beat and declares nothing."""
    absorbed = [_rec(1, 0.0, 6.0, "plate-desk;idle=drift", caps=["the world the page mounts over"]),
                _rec(2, 6.4, 14.0, "ledger:ev-a-v1:bars:0:right:mount=0.79:cut", act="QUOTES the figure")]
    g = SH.groups(absorbed)[0]
    assert [b["beat"] for b in g["beats"]] == [1, 2] and g.get("open_mounts")
    assert SH.entry_beat(g)["beat"] == 2, "the page's own beat declared the mount, not the hook's"
    # ... and on an ordinary row it is the row's own first beat, which is where the plate is read
    plain = [_rec(1, 0.0, 9.0, "ledger:ev-a-v1:bars:0:right:mount=0.79:cut", act="QUOTES the figure"),
             _rec(2, 9.4, 18.0, "ledger:ev-a-v1:bars:0:right:mount=0.79:cut", act="QUOTES the figure")]
    rows, why = SH.compile(plain, _take(plain), SH.DEFAULTS, "9:16")
    assert SH.rows_why(why)[0]["departure"]["beat"] == SH.entry_beat(SH.groups(plain)[0])["beat"] == 1


def test_two_cards_moved_onto_one_instant_never_share_a_room():
    """The placer's own docstring - *"never two of them in one box"* (E65) - AFTER a card moves. A card
    whose park would have covered the plan's transform is re-timed clear of it (the ninth pass), and the
    room index is *the first no card live at the same instant already holds*, so it is re-read on the
    windows the cards ENDED UP with: the T3j review's MEDIUM 4, the stale-slot case, on the calendar's own
    page (whose only room is the band a park frees, so both cards want it)."""
    page = _page(CALENDAR, "ledger:ev-into-vs-after-v1:bars:0:right")
    assert SH.card_rooms(page, "9:16", 3) == [] and len(SH.card_rooms(page, "9:16", 3, park=0.52)) == 1
    notes, species = [], [{"kind": "chart_to", "at": 8.6, "dur": 0.9, "to": "compare"}]
    cards = [["card-a", "lane", 8.0, 10.0, {"centre": True}], ["card-b", "lane", 11.0, 13.0, {"centre": True}]]
    out = SH.place_cards([list(c) for c in cards], page, "9:16", notes, species, 16.0, SH.DEFAULTS)

    a, b = out
    assert (float(a[2]), float(a[3])) == (9.9, 11.9), "card-a moved clear of the transform the plan named"
    assert float(a[3]) > float(b[2]), "... and now it is live while card-b is: one instant, two cards"
    assert SH.placed(a[4]) and not SH.placed(b[4]), (a[4], b[4])
    assert any("no 2th room" in n for n in notes), notes


def test_a_page_is_never_left_parked_at_the_end_of_its_row():
    """CAPABILITIES.md:120 - the un-park is how the chart RE-TAKES the stage; a page left at `park_scale`
    when its row ends plays the row's own exit on a stamp and hands the next world a parked chart. So the
    card LEAVES early enough for the un-park to land whole inside the row (it keeps its read and its park),
    and where even that does not fit the park is refused and the card is dropped BY NAME (the T3j review's
    MEDIUM 5, on arithmetic that clamped the card's exit to `t1` and then added the lag to it)."""
    page = "ledger:ev-into-vs-after-v1:bars:0:right:axes:cut"      # the calendar's own page, read-only
    plan = [_rec(1, 0.0, 7.0, page, sentence="The open is the chart and it says a number.",
                 act="QUOTES the figure"),
            _rec(2, 7.4, 13.0, page, sentence="It turns and then at the very end the card lands.",
                 act="TURNS on the reveal",
                 moves=[{"kind": "dock", "at_word": "card", "asset": "dock-a-thing",
                         "options": {"centre": True, "read_s": 1.2, "park_s": 0.7}}])]
    rows, why = SH.compile(plan, _take(plan), SH.DEFAULTS, "9:16", pages=_pages(CALENDAR))
    row, rule = rows[0], SH.rows_why(why)[0]["rule"]
    assert not row[4] and not [s for s in row[6] if s.get("to") == "park"], (row[4], row[6])
    assert "`dock-a-thing` is DROPPED" in rule and "could not UN-PARK inside the row" in rule, rule
    # ... and the arm that KEEPS the card: the un-park lands whole inside the row and the card still reads
    notes, card = [], ["card-a", "lane", 8.0, 16.0, {"read_s": 1.2, "park_s": 0.7}]
    at, out = SH.unpark_inside_the_row(card, 7.6, 16.3, [], 16.0, SH.DEFAULTS, notes)
    assert (at, out) == (7.6, round(16.0 - SH.PARK_DUR_S, 2)) and float(card[3]) == round(16.0 - 1.2, 2)
    assert out + SH.PARK_DUR_S <= 16.0 + 1e-9 and "lands whole inside the row" in notes[0], notes
    # ... and where the card cannot read inside what is left, the park is refused and the card goes
    late = ["card-b", "lane", 14.6, 16.0, {"read_s": 1.2, "park_s": 0.7}]
    assert SH.unpark_inside_the_row(late, 14.2, 16.3, [], 16.0, SH.DEFAULTS, notes) is None
    assert "is DROPPED" in notes[-1] and "hands the next world a stamp" in notes[-1], notes[-1]


def test_the_engines_own_default_species_duration_is_read_and_never_typed():
    """MEDIUM 6: the `chart_to` a plan gives no `dur` runs the ENGINE's own default, read by name
    (`scene-evidence-engine.mjs`: `const d = Math.max(0.001, sp.dur || 1)` in `lpPaintStates`) - the one
    typed number a pass that reads every other clock by name had left in `transform_guards`."""
    assert SH.SPECIES_DUR_S == 1.0
    (a, z, _sp), = SH.transform_guards([{"kind": "chart_to", "at": 4.0, "to": "recast"}])
    assert (a, z) == (4.0, round(4.0 + SH.SPECIES_DUR_S + MD.LP_BUILD_S, 2)), (a, z)
    (a2, z2, _sp2), = SH.transform_guards([{"kind": "chart_to", "at": 4.0, "to": "recast", "dur": 0.5}])
    assert (a2, z2) == (4.0, round(4.5 + MD.LP_BUILD_S, 2)), (a2, z2)


# ------------------------------------------------------------- R26-293: the kit admits the prop morphs the
# compiler admits (P69 T26e) - one registry of chart_to verbs, the compiler's, never a second copy here

PROP_MORPH_PROP = "prop-hyperscale-datacenter-v1"   # a catalogued cutout (test_prop_morph.py's own)
PROP_MORPH_PLATE = "ledger:ev-a-v1:line:3:right:axes:cut"


def test_the_kits_chart_to_verbs_are_the_compilers_own():
    """The kit's three families (travel to a state / derived / no state) partition EXACTLY the compiler's
    CHART_TO_KINDS: a verb the compiler adds or drops shows up here before a plan is refused for it."""
    families = (SH.CHART_TO_TO_STATE, SH.CHART_TO_DERIVED, SH.CHART_TO_NO_STATE)
    flat = [k for fam in families for k in fam]
    assert len(flat) == len(set(flat)), "a verb sits in two families"
    assert set(flat) == set(SH.compiler().CHART_TO_KINDS)
    assert set(SH.CHART_TO_KINDS) == set(SH.compiler().CHART_TO_KINDS)


@pytest.mark.parametrize("sp", [
    {"kind": "chart_to", "to": "prop", "prop": PROP_MORPH_PROP, "at": 4.0},
    {"kind": "chart_to", "to": "prop", "prop": PROP_MORPH_PROP, "at": 4.0, "mark": "b:1",
     "place": {"x": 0.7, "y": 0.4, "w": 0.2}},
    {"kind": "chart_to", "to": "morph", "from": f"prop:{PROP_MORPH_PROP}", "at": 4.0},
    {"kind": "chart_to", "to": "morph", "from": f"prop:{PROP_MORPH_PROP}", "at": 4.0, "mark": "b:2"},
])
def test_the_kit_admits_a_prop_morph_the_compiler_admits(sp):
    """`chart_to {to: "prop"}` and `chart_to {to: "morph", from: "prop:<id>"}` are the compiler's own verbs
    (build_scene_timeline_f `_prop_morph_way`); the kit refused both - the first as an unknown `to`, the
    second as a morph with no `state`."""
    assert SH.compiler()._prop_morph_way(sp) is not None, "the compiler reads this as a prop morph"
    assert SH.chart_to_error(sp, PROP_MORPH_PLATE, 1) is None


@pytest.mark.parametrize("sp, says", [
    ({"kind": "chart_to", "to": "prop", "at": 4.0}, "name the prop"),
    ({"kind": "chart_to", "to": "prop", "prop": "prop-no-such-thing-v9", "at": 4.0}, "not in the props catalogue"),
    ({"kind": "chart_to", "to": "prop", "prop": PROP_MORPH_PROP, "at": 4.0, "mark": "bar one"}, "mark"),
    ({"kind": "chart_to", "to": "morph", "from": f"prop:{PROP_MORPH_PROP}", "at": 4.0, "mark": "page"}, "mark"),
    ({"kind": "chart_to", "to": "morph", "from": "datacenter", "at": 4.0}, "is not `prop:<id>`"),
    ({"kind": "chart_to", "to": "morph", "from": f"prop:{PROP_MORPH_PROP}", "at": 4.0, "state": 1}, "names no chart state"),
])
def test_a_prop_morph_the_compiler_would_refuse_is_refused_by_the_kit_with_its_words(sp, says):
    err = SH.chart_to_error(sp, PROP_MORPH_PLATE, 1)
    assert err is not None and says in err, err
    assert err.startswith("beat 1: the chart_to "), err


def test_a_plan_naming_a_prop_morph_compiles_through_the_kit():
    """End to end: the move reaches the generated row as written, where it was a Refused before."""
    plan = _chained(moves=[{"kind": "chart_to", "at_word": "month", "dur": 1.4,
                            "options": {"to": "prop", "prop": PROP_MORPH_PROP}}])
    rows, _why = SH.compile(plan, _take(plan), SH.DEFAULTS, "16:9")
    got = [sp for sp in (rows[0][6] or []) if sp["kind"] == "chart_to"]
    assert [(sp["to"], sp.get("prop")) for sp in got] == [("prop", PROP_MORPH_PROP)], got

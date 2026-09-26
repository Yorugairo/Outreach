"""P70 T10 (was P69 T61, A44) - THE IN-PLACE BADGE SWAP ON THE CHAPTER PILL.

The Bravos harvest v2's A44 "In-place badge swap: the pill's text flips, the pill stays" (BRAVOS-USE-WHEN :771: "the same
period is renamed ('Dot-Com Bust' -> 'Lost Decade')"; the don't: "the rename changes the period (move the pill
instead)"). UNBLOCKED 2026-09-24 on BOOM's real frames (docs/research/runs/bravos-watch/jx3Ll-GJtMY/verify/VERIFY.md,
A44_A45_T37_swap1): measured again at BOOM's native 29.97 fps (the scratch record p70-t9/bravos/boom): the old box
CLOSES to a slot as its name is cut away, 146.47 -> 146.90 s (0.43 s), then OPENS to the new name's width as the new name
writes in, 146.93 -> 147.35 s (0.42 s); the pill never leaves its place.

The grammar - `swap: [{at, text}]` on a chapter - can rename the act and can never move it: a swap carries no `until`
(a new period is a new chapter), and it has to happen inside the act, after the pill has landed and with room for its
open before the act's leave. The engine calls the retitle's glyph law (lpGlyphs, eraseFactor, writeGlyphs) - it does
not edit it - and a chapter with no swap is T9's pill to the byte.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/species.json"
PLATE = "world-paper-and-steel-press-v1;use=reset"
# H's own sentence renames the act's subject in place: "The bubble isn't in the steel. It's in the PAPER wrapped around
# the steel." - the same period, named again (the harvest's don't: never a new period)
CH = {"kind": "chapter", "at": 363.38, "until": 431.01, "text": "The bubble", "swap": [{"at": 367.38, "text": "The paper"}]}
WORDS = [{"w": "It", "start": 363.38, "end": 363.49}, {"w": "paper", "start": 367.38, "end": 367.79},
         {"w": "wrapped", "start": 367.79, "end": 368.1}, {"w": "What", "start": 369.38, "end": 369.57},
         {"w": "Railway", "start": 431.01, "end": 431.38}]


def _errs(entries, plate=PLATE):
    return B.validate_species([json.loads(json.dumps(e)) for e in entries], (0, 0, 0), plate)


def _swap(*swaps, **patch):
    e = json.loads(json.dumps(CH))
    e["swap"] = list(swaps)
    e.update(patch)
    return e


def _plan(entry):
    return [(338.44, None, PLATE, (0, 0, 0), [], None, []), (363.38, None, PLATE, (0, 0, 0), [], None, [entry]),
            (384.12, None, PLATE, (0, 0, 0), [], None, [])]


# ---- the grammar -------------------------------------------------------------------------------------------------


def test_a_chapter_takes_a_swap():
    assert _errs([CH]) == []


def test_the_swap_s_clocks_are_boom_s_and_mirror_the_engine():
    src = ENGINE.read_text(encoding="utf-8")
    assert (B.CHAPTER_SWAP_CLOSE_S, B.CHAPTER_SWAP_OPEN_S) == (0.43, 0.42), "BOOM 146.47 -> 146.90 -> 147.35 (29.97 fps)"
    assert "SWAP_CLOSE_S: 0.43" in src and "SWAP_OPEN_S: 0.42" in src


@pytest.mark.parametrize("swap", [{"at": 367.38}, {"text": "The paper"}, {"at": 367.38, "text": ""},
                                  {"at": "367", "text": "The paper"}, {"at": 367.38, "text": "The\npaper"}])
def test_a_malformed_swap_is_refused(swap):
    errs = _errs([_swap(swap)])
    assert errs and any(e.startswith("chapter: swap") for e in errs), errs   # the swap's own refusal, never the unknown key


def test_a_swap_is_a_list():
    errs = _errs([_swap(swap={"at": 367.38, "text": "The paper"})])
    assert any("swap" in e and "list" in e for e in errs), errs


@pytest.mark.parametrize("key", ["until", "dur", "colour"])
def test_a_swap_never_moves_the_period(key):
    """The rename never changes the period: a swap has no `until` of its own - a new period is a new chapter."""
    errs = _errs([_swap({"at": 367.38, "text": "The paper", key: 400.0})])
    assert any(repr(key) in e and "new chapter" in e for e in errs), errs


def test_a_swap_to_the_same_name_is_no_swap():
    errs = _errs([_swap({"at": 367.38, "text": "The bubble"})])
    assert any("same" in e for e in errs), errs


def test_a_swap_waits_for_the_pill_to_land():
    errs = _errs([_swap({"at": CH["at"] + B.CHAPTER_LAND_S - 0.01, "text": "The paper"})])
    assert any("land" in e for e in errs), errs
    assert _errs([_swap({"at": CH["at"] + B.CHAPTER_LAND_S, "text": "The paper"})]) == []


def test_a_swap_finishes_before_the_act_leaves():
    late = CH["until"] - B.CHAPTER_SWAP_CLOSE_S - B.CHAPTER_SWAP_OPEN_S + 0.01
    errs = _errs([_swap({"at": late, "text": "The paper"})])
    assert any("until" in e for e in errs), errs


def test_two_swaps_never_run_into_each_other_and_keep_their_order():
    a = {"at": 367.38, "text": "The paper"}
    errs = _errs([_swap(a, {"at": 367.38 + B.CHAPTER_SWAP_CLOSE_S + B.CHAPTER_SWAP_OPEN_S - 0.01, "text": "The press"})])
    assert any("swap" in e and "0.85" in e for e in errs), errs
    errs = _errs([_swap({"at": 380.0, "text": "The press"}, a)])
    assert errs, "out of order"
    assert _errs([_swap(a, {"at": 369.38, "text": "The press"})]) == []


def test_each_swap_falls_on_a_word():
    plan = _plan(_swap({"at": 367.5, "text": "The paper"}))
    errs = B.chapter_errors(B.collect_chapters(plan, 811.78), WORDS, 811.78, "16:9")
    assert errs and "swap" in errs[0] and "word" in errs[0], errs
    assert B.chapter_errors(B.collect_chapters(_plan(dict(CH)), 811.78), WORDS, 811.78, "16:9") == []


def test_each_name_fits_the_ink_column():
    plan = _plan(_swap({"at": 367.38, "text": "The paper wrapped around the steel, the press, the certificates, again"}))
    errs = B.chapter_errors(B.collect_chapters(plan, 811.78), WORDS, 811.78, "16:9")
    assert errs and "column" in errs[0], errs


# ---- the lift, the box, the gate, the card ---------------------------------------------------------------------------


def test_the_timeline_carries_the_swaps_and_the_box_is_the_widest_name():
    wide = _swap({"at": 367.38, "text": "The paper wrapped"})
    got = B.timeline_chapters(B.collect_chapters(_plan(wide), 811.78))[0]
    assert got["swap"] == [{"at": 367.38, "text": "The paper wrapped"}]
    assert got["box"] == B.chapter_box("The paper wrapped")
    assert B.chapter_reserve(B.collect_chapters(_plan(wide), 811.78)) == [B.chapter_box("The paper wrapped")]
    plain = {k: v for k, v in CH.items() if k != "swap"}
    assert "swap" not in B.timeline_chapters(B.collect_chapters(_plan(plain), 811.78))[0]


def test_the_gate_credits_each_swap():
    assert G.SPECIES_EVENTS["chapter"] == ("at", "swaps")
    two = _swap({"at": 367.38, "text": "The paper"}, {"at": 369.38, "text": "The press"})
    scenes = [{"span": [363.38, 384.12], "species": [B.compiled_chapter(two)]}]
    assert G._species_events(scenes) == [363.38, 367.38, 369.38]


def test_a_swap_in_a_later_scene_is_still_the_pill_s_motion():
    """The pill holds across the cut, so its swap is motion wherever the act has got to (one copy, one credit)."""
    later = _swap({"at": 390.0, "text": "The paper"})
    scenes = [{"span": [363.38, 384.12], "species": [B.compiled_chapter(later)]}, {"span": [384.12, 408.6], "species": []}]
    assert G._species_events(scenes) == [363.38, 390.0]


def test_the_card_names_the_swap_option():
    cards = {c["token"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    assert [o["token"] for o in cards["chapter"]["options"]] == ["swap"]


def test_the_engine_calls_the_retitle_s_glyph_law_and_does_not_copy_it():
    src = ENGINE.read_text(encoding="utf-8")
    body = src[src.index("  const paintChapters = (t) => {"):src.index("  const render = (t) => {")]
    body += src[src.index("  const chapterMount = (list) => {"):src.index("  const paintChapters = (t) => {")]
    for name in ("lpGlyphs(", "eraseFactor(", "writeGlyphs("):
        assert name in body, name
    assert src.count("const eraseFactor = ") == 1 and src.count("const writeGlyphs = ") == 1


def test_a_chapter_without_a_swap_is_t9_s_pill_to_the_byte():
    import render_baseline as RB
    assert RB.check(["chapter-held"]) == []


# ---- the golden and the served player ------------------------------------------------------------------------------


def test_the_golden_is_registered_and_judged_mid_swap():
    import build_golden_sources as GS
    assert "chapter-swap" in GS.SURFACES and "chapter-swap" in GS.FRAME_T
    tl, _uris = GS.SURFACES["chapter-swap"]()
    ch = tl["chapters"][0]
    s = ch["swap"][0]["at"]
    assert (ch["text"], ch["swap"][0]["text"]) == ("The bubble", "The paper")
    assert s + B.CHAPTER_SWAP_CLOSE_S < GS.FRAME_T["chapter-swap"] < s + B.CHAPTER_SWAP_CLOSE_S + B.CHAPTER_SWAP_OPEN_S


PROBE = """() => {
  const stg = document.getElementById('stage').getBoundingClientRect();
  const p = document.querySelector('#chapters .lp-chpill');
  if (!p) return null;
  const r = p.getBoundingClientRect();
  const names = [...p.querySelectorAll('.lp-chname')].map((n) => ({
    text: [...n.querySelectorAll('.g')].map((g) => g.textContent).join('').replace(/\\u00a0/g, ' '),
    vis: getComputedStyle(n).visibility,
    w: [...n.querySelectorAll('.g')].map((g) => +(g.style.getPropertyValue('--w') || 0)) }));
  return { x: r.x - stg.x, y: r.y - stg.y, w: r.width, h: r.height, op: +getComputedStyle(p).opacity, names };
}"""


def _served(tl: dict, uris: dict, order: list[float]) -> dict[float, dict]:
    import render_baseline as RB
    import served_player as SPL
    w, h = RB.STAGE["16:9"]
    out: dict[float, dict] = {}
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "sw.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SPL.served(html, w, h) as (page, errs):
            for t in order:
                RB.frame_png(page, t, (w, h))
                out.setdefault(t, page.evaluate(PROBE))
            assert errs == [], errs
    return out


@pytest.fixture(scope="module")
def reads():
    import build_golden_sources as GS
    tl, uris = GS.SURFACES["chapter-swap"]()
    s = tl["chapters"][0]["swap"][0]["at"]
    c, o = B.CHAPTER_SWAP_CLOSE_S, B.CHAPTER_SWAP_OPEN_S
    times = [s - 0.2, s + 0.5 * c, s + c + 0.01, s + c + 0.5 * o, s + c + o + 0.05, s + c + o + 2.0]
    forward = _served(tl, uris, times)
    scrubbed = _served(tl, uris, [times[3] + 4.0, 1.0, times[3]])
    return times, forward, scrubbed


def _shown(r):
    return [n for n in r["names"] if n["vis"] != "hidden" and any(v > 0.02 for v in n["w"])]


def test_before_the_word_the_old_name_stands_whole(reads):
    times, f, _s = reads
    r = f[times[0]]
    assert [n["text"] for n in _shown(r)] == ["The bubble"] and all(v == 1 for v in _shown(r)[0]["w"]), r


def test_the_old_name_erases_as_the_box_closes_in_place(reads):
    times, f, _s = reads
    a, b = f[times[0]], f[times[1]]
    assert b["w"] < a["w"] - 20 and abs(b["x"] - a["x"]) < 1.5 and abs(b["y"] - a["y"]) < 3.0, (a, b)
    old = [n for n in b["names"] if n["text"] == "The bubble"][0]
    assert 0 < sum(old["w"]) < len(old["w"]), old   # part-erased, glyph after glyph


def test_at_the_turn_the_box_is_a_slot(reads):
    times, f, _s = reads
    r = f[times[2]]
    assert r["w"] <= r["h"] + 12, r   # the capsule closed to (about) a circle, BOOM's slot


def test_the_new_name_writes_as_the_box_springs_open(reads):
    times, f, _s = reads
    r = f[times[3]]
    new = [n for n in r["names"] if n["text"] == "The paper"][0]
    assert new["vis"] != "hidden" and 0 < sum(new["w"]) < len(new["w"]), new
    final = f[times[4]]["w"]
    assert r["h"] + 12 < r["w"] < final + 0.04 * final + 0.015 * final, r   # springPop's overshoot (Mp 0.04) + E49's breath


def test_after_the_swap_the_new_name_stands_whole_in_the_same_place(reads):
    times, f, _s = reads
    a, r = f[times[0]], f[times[5]]
    assert [n["text"] for n in _shown(r)] == ["The paper"] and all(v == 1 for v in _shown(r)[0]["w"]), r
    assert abs(r["x"] - a["x"]) < 1.5 and abs(r["y"] - a["y"]) < 3.0 and r["op"] == 1, (a, r)


def test_a_seek_is_the_play(reads):
    times, f, s = reads
    assert s[times[3]] == f[times[3]]

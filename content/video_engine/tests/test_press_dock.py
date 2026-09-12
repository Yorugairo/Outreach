"""THE PRESS CARD DOCK (P50 T3; doc 29 §9.27 "Push hand-off"; SPECIES-BY-SENTENCE row 1 QUOTES).

A dock whose 5th-element options carry ``press`` is a PRESS CARD: a headline cut from a screenshot
(``press_card.py``), carrying its source line and the box of the quoted phrase as fractions of the card.
``stack: True`` joins it to the scene's pile - the push hand-off - and the compiler numbers the pile in
ENTER order so the player can pose it from the timeline alone.

Every refusal names the option, the way every other dock option's does. Pure functions - no episode build.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402

PHRASE = {"x0": 0.12, "y0": 0.2, "x1": 0.66, "y1": 0.44}
WORDS = "the historic normal was never normal"        # R26-55: the phrase's own words, for the player's live type
META = {"kind": "press", "source": "The Herald, 4 Mar 2026", "phrase": PHRASE, "phrase_text": WORDS,
        "crop": [100, 200, 1180, 520], "card": [1056, 313],
        "screenshot": {"name": "shot.png", "sha256": "0" * 64}}
CARD_ASPECT = round(313 / 1056, 5)                    # ... and the crop's own aspect, so the strip needs no decode


def _press(**kw) -> dict:
    m = dict(META)
    m.update(kw)
    return {k: v for k, v in m.items() if v is not None}


# ------------------------------------------------------------------ the option and its refusals

def test_a_press_dock_carries_its_source_and_phrase_and_drops_the_provenance():
    opts = B.dock_opts({"press": _press()})
    assert opts["press"] == {"kind": "press", "source": "The Herald, 4 Mar 2026",
                             "phrase": {"x0": 0.12, "y0": 0.2, "x1": 0.66, "y1": 0.44},
                             "phrase_text": WORDS, "img": CARD_ASPECT}
    assert "crop" not in opts["press"] and "screenshot" not in opts["press"], "provenance stays on disk"
    assert "press" in B.DOCK_OPTS and "stack" in B.DOCK_OPTS


# ---- R26-55: the phrase's WORDS and the card's aspect reach the timeline --------------------------

def test_the_phrases_words_reach_the_timeline_beside_the_raster():
    """The player cannot re-line a crop, so the words travel too - and the card's own aspect with them, so the
    provenance strip is laid out without waiting for the picture to decode."""
    d = B.dock_entry("ev-press-herald", 0, 4.0, 18.0, 0, press=B.press_meta(META))
    assert d["phrase_text"] == WORDS and d["img"] == CARD_ASPECT
    assert d["phrase"] == {"x0": 0.12, "y0": 0.2, "x1": 0.66, "y1": 0.44}, "the crop's own region is still on record"


def test_a_card_cut_before_the_words_existed_compiles_exactly_as_it_did():
    """Every press card on disk was cut by the tool as it was. Neither key is invented for it: the card keeps its
    raster phrase and the entry is byte-for-byte the entry it was."""
    old = {k: v for k, v in META.items() if k not in ("phrase_text", "card")}
    meta = B.press_meta(old)
    assert meta == {"kind": "press", "source": META["source"], "phrase": PHRASE}
    d = B.dock_entry("ev-press-herald", 0, 4.0, 18.0, 0, press=meta)
    assert "phrase_text" not in d and "img" not in d


@pytest.mark.parametrize("words, needle", [
    ("normal", "two or more"),
    ("   ", "two or more"),
    (7, "two or more"),
    (["two", "words"], "two or more"),
])
def test_a_phrase_text_that_is_not_the_phrases_words_is_refused_by_name(words, needle):
    with pytest.raises(ValueError) as exc:
        B.dock_opts({"press": _press(phrase_text=words)})
    assert needle in str(exc.value) and "live type" in str(exc.value), str(exc.value)


def test_the_words_are_collapsed_and_a_malformed_card_size_is_simply_not_an_aspect():
    assert B.press_meta(dict(META, phrase_text="  the historic\n normal  was never normal "))["phrase_text"] == WORDS
    for bad in ([0, 100], [1056], "1056x313", None, [1056, -3], ["1056", "313"]):
        meta = B.press_meta(dict(META, card=bad))
        assert "img" not in meta, f"{bad}: a size that is not a size is no aspect, and never a guess"


def test_a_press_dock_without_a_source_is_refused_by_name():
    for bad in (None, "", "   ", 7):
        with pytest.raises(ValueError) as exc:
            B.dock_opts({"press": _press(source=bad)})
        assert "press needs a non-empty 'source'" in str(exc.value), bad


@pytest.mark.parametrize("phrase, needle", [
    (None, "must be {x0, y0, x1, y1}"),
    ({"x0": 0.1, "y0": 0.2, "x1": 0.5}, "must be {x0, y0, x1, y1}"),
    ({"x0": 0.1, "y0": 0.2, "x1": 1.4, "y1": 0.5}, "fractions of the CARD in 0..1"),
    ({"x0": 0.1, "y0": 0.2, "x1": "0.5", "y1": 0.5}, "fractions of the CARD in 0..1"),
    ({"x0": 0.6, "y0": 0.2, "x1": 0.5, "y1": 0.5}, "empty or inverted"),
    ({"x0": 0.1, "y0": 0.6, "x1": 0.5, "y1": 0.5}, "empty or inverted"),
])
def test_a_press_dock_with_a_bad_phrase_is_refused_by_name(phrase, needle):
    with pytest.raises(ValueError) as exc:
        B.dock_opts({"press": _press(phrase=phrase)})
    assert needle in str(exc.value), str(exc.value)


def test_the_press_meta_may_be_the_path_press_card_wrote(tmp_path: Path):
    p = tmp_path / "ev-press-herald.press.json"
    p.write_text(json.dumps(META), encoding="utf-8")
    assert B.dock_opts({"press": str(p)})["press"]["source"] == META["source"]
    with pytest.raises(ValueError) as exc:
        B.dock_opts({"press": str(tmp_path / "nope.json")})
    assert "is not a file" in str(exc.value)
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        B.dock_opts({"press": str(bad)})
    assert "is not JSON" in str(exc.value)


def test_stack_belongs_to_a_press_dock_and_is_a_flag():
    with pytest.raises(ValueError) as exc:
        B.dock_opts({"stack": True})
    assert "stack is the PRESS stack" in str(exc.value)
    with pytest.raises(ValueError) as exc:
        B.dock_opts({"press": _press(), "stack": "yes"})
    assert "stack must be True" in str(exc.value)
    assert B.dock_opts({"press": _press(), "stack": True})["stack"] is True


# ------------------------------------------------------------------ the dock entry and the pile

def test_the_dock_entry_declares_press_and_leaves_every_other_dock_untouched():
    d = B.dock_entry("ev-press-herald", 0, 4.0, 18.0, 0, press=B.press_meta(META))
    assert d["kind"] == B.DOCK_KIND_PRESS and d["source"] == META["source"]
    assert d["phrase"] == {"x0": 0.12, "y0": 0.2, "x1": 0.66, "y1": 0.44}
    assert "stack_index" not in d and "_stack" not in d, "a lone quotation is its own pile of one"
    plain = B.dock_entry("ev-card", 0, 4.0, 18.0, 2)
    assert "kind" not in plain and "source" not in plain and "phrase" not in plain


def test_the_stack_is_numbered_in_enter_order_and_the_marker_never_ships():
    mk = lambda aid, slot, enter: B.dock_entry(aid, slot, enter, 26.0, 0, press=B.press_meta(META), stack=True)
    docks = [mk("c", 0, 9.8), mk("a", 1, 5.0), mk("b", 0, 7.4), B.dock_entry("plain", 1, 2.0, 26.0, 1)]
    stacked = B.assign_press_stack(docks)
    assert [d["slide"] for d in stacked] == ["a", "b", "c"], "enter order, whatever order the rows were written in"
    assert [(d["stack_index"], d["stack_n"]) for d in stacked] == [(0, 3), (1, 3), (2, 3)]
    assert all("_stack" not in d for d in docks), "the marker is the compiler's own bookkeeping"
    assert "stack_index" not in docks[3], "a dock that did not ask to stack is untouched"


def test_a_press_dock_that_does_not_stack_takes_no_index():
    d = B.dock_entry("ev-press-solo", 0, 4.0, 18.0, 0, press=B.press_meta(META), stack=False)
    assert B.assign_press_stack([d]) == []
    assert d["kind"] == B.DOCK_KIND_PRESS and "stack_n" not in d


def test_a_press_card_is_refused_on_a_ledger_page_by_name():
    """E45 §1: the pile has ONE box and it is the stage's centre - on a page that is the plot. The refusal names
    the dock and the way out (the dock's read->park, or a plate of its own)."""
    err = B.press_plate_error("ledger:golden-series:line", "ev-press-herald")
    assert err and err.startswith("dock ev-press-herald:") and "E45" in err and "read" not in err.split("-")[0]
    assert "park" in err
    assert B.press_plate_error("world-spike-desk-v1", "ev-press-herald") is None
    assert B.press_plate_error("clip:x.mp4", "ev-press-herald") is None

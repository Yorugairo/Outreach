"""Opening-structure gate: red on the known-real case, green on a conforming
opening at the same geometry.

doc 40 MEDIA-TDD: a gate is validated against a known-real failure before it
is trusted. The known-real case is Steel and Paper as recorded: promise after
0:60, a proof hedged next-line at 2:44, a concession run 3:10-3:24, no visual
breath before the first word, and none of the declared classical beats
present.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

import gate_opening_structure as G   # noqa: E402
import audit_script_doctrine as A     # noqa: E402

EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
SCRIPT = EP / "SCRIPT-G-VO.txt"
TIMELINE = EP / "build-f/timeline.json"
needs_ep1 = pytest.mark.skipif(not (SCRIPT.exists() and TIMELINE.exists()),
                               reason="episode one artifacts not on disk")

FILLER = "The mechanism underneath moved and almost nobody on the desk looked at it. "


def _by_id(gates):
    return {g.id: g for g in gates}


def _pad_to(text: str, target_s: float) -> str:
    while A.secs(A.spoken(text)) < target_s:
        text += FILLER
    return text


# ---- RED: episode one, measured ------------------------------------------

@needs_ep1
def test_red_steel_and_paper_measured_failures():
    gates, stats = G.run(SCRIPT.read_text(encoding="utf-8"), G.load_timeline(TIMELINE),
                         counterparty="Bravos", ring="spike")
    g = _by_id(gates)
    assert stats["timing"].startswith("measured")
    assert g["G09"].level == "FAIL" and "AFTER" in g["G09"].message, g["G09"]    # promise after 0:60
    assert g["G02"].level == "FAIL", g["G02"]                                     # no visual breath
    assert g["G34"].level == "FAIL" and "3:1" in g["G34"].message, g["G34"]      # concession run
    assert g["G35"].level == "FAIL" and "2:4" in g["G35"].message, g["G35"]      # hedged proof
    assert g["G03"].level == "PASS", g["G03"]      # post-key at 5.57s IS on the 8s boundary
    assert g["G15"].level == "PASS", g["G15"]      # the spike IS planted in P1


# ---- GREEN: a conforming opening at episode-one geometry ------------------

def _conforming_opening() -> str:
    """Every doc-38 / P1 / P2 beat - classical and platform - declared where
    the text has no signature, placed by the kit's estimator so it lands in
    its window. Padded to ~13.4 min so the geometry matches a real episode
    (P1 ~1:10, beat 5 from 0:47, P2 ~1:10-2:46)."""
    s = ("The safest thing you own looks like this. "
         "An iron spike. `[post-key]` "
         "It ruined almost everyone who touched it, and you would have bought it too. ")
    s = _pad_to(s, 9.0)
    s += "[archetype] A banker in Manhattan is counting a bonus this morning, and a budtender in Denver is counting a till. "
    s += "[stakes] If you hold an index fund it is already holding you, and the bill is yours. "
    s = _pad_to(s, 31.0)
    s += "[payoff] Here is what the chart got right: the giants are the market now. "
    s += "`[pre-key]` [promise] [tricolon] It isn't a rebuttal, it isn't a victory lap, it isn't a panic: by the end you'll run one test yourself, thirty seconds a stock. "
    s = _pad_to(s, 50.0)
    s += "[reflect] The loss is not proof of failure; it is proof of participation. "
    s += "[desire] The goal is one sort: which of your holdings is steel and which is paper. "
    s += "[rehook] But here's where their own chart gets strange, and the strangeness is the story. "
    s += "[opponent] [map] The opponent is a machine, the hype cycle, capital arriving faster than the value it chases, and three questions will catch it. "
    # P2 (~1:10 -> ~2:46): catalyst as a closed loop, new info every <30s, head-fake early, debate mid-late
    s = _pad_to(s, 72.0)
    s += "[catalyst] [loop] [new] Memory, the builders inside the builders, is up six hundred percent, and that closes the first question. "
    s = _pad_to(s, 82.0)
    s += "[foreshadow] [rehook] And that's where the yardstick comes in, the one that pays the promise at the end. "
    s += "[head-fake] So the obvious move is the one every adviser would sign: take profits. "
    s = _pad_to(s, 100.0)
    s += "[new] [loop] But railways drew a quarter-billion pounds, then fell by two thirds, and the trains ran straight through it. "
    s += "[reflect] The spike outlived the paper. "
    s = _pad_to(s, 120.0)
    s += "[new] [debate] But watch the profit-taker first: he sold the chipmakers in March and the customers doubled again by June. "
    s = _pad_to(s, 138.0)
    s += "[new] [loop] So by their math AI spending just crossed eight, and that closes the second question. "
    s = _pad_to(s, 150.0)
    s += "[new] Because I pulled their yardstick myself and ran it all the way back: twenty-eight cents of every dollar. "
    s += "[loop-close] So the first answer is partial: the bubble is real and the address is wrong. `[post-key]` "
    s += "[dip] Sit with that for a second. "
    s += "[signpost] [new] Which is why the real question is who is paying for the steel. "
    for t in (190.0, 240.0, 290.0):
        s = _pad_to(s, t)
        s += "[new] [rehook] But look at what the filings say next, because the number moves again. "
    s = _pad_to(s, 805.0)
    return s


def test_green_declared_opening_passes_every_gate():
    gates, stats = G.run(_conforming_opening(), None, counterparty="Bravos", ring="spike")
    fails = [g for g in gates if g.level == "FAIL"]
    assert not fails, "\n".join(f"{g.id} {g.message}  <{g.src}>" for g in fails) + f"\n{stats}"
    ids = {g.id for g in gates}
    # the classical layer is present as NAMED gates, not implied
    for gid in ("G37", "G38", "G14", "G39", "G40", "G19", "G24", "G41", "G42", "G15", "G27", "G16", "G31", "G43"):
        assert gid in ids, gid
    assert any(g.level == "JUDGE" for g in gates)


def test_promise_after_60s_fails_even_when_declared():
    s = _pad_to("The safest thing you own looks like this. An iron spike. ", 75.0)
    s += "`[pre-key]` [promise] By the end you'll run one test yourself. "
    g = _by_id(G.run(_pad_to(s, 805.0), None)[0])
    assert g["G09"].level == "FAIL" and "AFTER" in g["G09"].message, g["G09"]


def test_undeclared_required_beats_fail():
    s = _pad_to("The safest thing you own looks like this. An iron spike. ", 805.0)
    g = _by_id(G.run(s, None, ring="spike")[0])
    for gid in ("G37", "G07", "G08", "G12", "G38", "G14", "G39", "G16", "G40", "G20", "G24", "G41", "G26", "G28", "G42"):
        assert g[gid].level == "FAIL", (gid, g[gid])


def test_concession_run_fails_and_turn_within_two_sentences_passes():
    base = "The safest thing you own looks like this. An iron spike. It ruined almost everyone who touched it. "
    long_run = base + ("Bravos is right about the cycle. Bravos is right about the threshold. "
                       "Credit where due, the most honest line all year. Bravos called it. ")
    assert _by_id(G.run(long_run, None, counterparty="Bravos")[0])["G34"].level == "FAIL"
    short_run = base + ("Bravos is right about the cycle. Bravos is right about the threshold. "
                        "And that is exactly where I went further and ran the yardstick myself. ")
    assert _by_id(G.run(short_run, None, counterparty="Bravos")[0])["G34"].level == "PASS"


def test_hedged_proof_fails():
    s = ("The safest thing you own looks like this. An iron spike. "
         "Today it's twenty-eight cents, the most it has ever been. "
         "The yardstick is a new instrument for this channel, no threshold on it yet. ")
    assert _by_id(G.run(s, None)[0])["G35"].level == "FAIL"


def test_geometry_scales_with_runtime():
    g30 = G.geometry(30 * 60); g16 = G.geometry(16 * 60); g8 = G.geometry(8 * 60)
    assert (g30["p1_end"], g30["p2_end"]) == (90.0, 300.0)
    assert (g16["p1_end"], g16["p2_end"]) == (75.0, 180.0)
    assert (g8["p1_end"], g8["p2_end"]) == (60.0, 135.0)
    assert g30["loops"] == (4, 6) and g30["new"] == (7, 14)

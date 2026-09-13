"""Opening-structure gate: red on the known-real case, green on a conforming
opening at the same geometry.

doc 40 MEDIA-TDD: a gate is validated against a known-real failure before it
is trusted. The known-real case is Steel and Paper as recorded: promise after
0:60, a proof hedged next-line at 2:44, a concession run 3:10-3:24, no visual
breath before the first word, and none of the declared classical beats
present.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

import gate_opening_structure as G   # noqa: E402
import audit_script_doctrine as A     # noqa: E402
import kit_spec                       # noqa: E402
import beat_tags                      # noqa: E402

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
    # G15b (P37 T4): the ring token is planted INSIDE the claim, so the close has an argument to
    # return to - "An iron spike." on its own carries one content stem, which is ep1's defect
    s = ("The safest thing you own looks like this. "
         "An iron spike ruined almost everyone who touched it, and you would have bought it too. `[post-key]` ")
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
    # E23: the cycle runs the whole video - an (untagged) rehook-family line every ~50s
    # keeps G36 under 60s x tol to the end and lands one in every P3/P5 unit window
    # (kit_spec.unit_windows at 805s: P3 2:16-4:09 / 4:09-6:02, P5 7:23-9:32 / 9:32-11:40).
    # Untagged: kept minimal for the opening-gate rows under test. (The audit's doc-37
    # break ration counts DELIVERY marks only since 2026-09-03 - beat tags no longer
    # count, see test_audit_break_ration.py - so tagging here would no longer trip it.)ars.
    for t in range(340, 800, 50):
        s = _pad_to(s, float(t))
        s += "But look at what the filings say next, because the number moves again. "
    # the close returns the claim, not just the word (G15b): iron / ruined / touched / bought recur
    s = _pad_to(s, 790.0)
    s += "So the iron spike is the thing that ruined everyone who touched it, and you would have bought it too. "
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


# ---- E23: the cycle runs the whole video; one rehook per unit window -------

def _gap_start_s(message: str) -> float:
    m = re.search(r"from (\d+):(\d+)", message)
    assert m, message
    return int(m.group(1)) * 60 + int(m.group(2))


@needs_ep1
def test_red_steel_and_paper_cycle_gap_measured_past_the_opening():
    text, tl = SCRIPT.read_text(encoding="utf-8"), G.load_timeline(TIMELINE)
    gates, stats = G.run(text, tl, counterparty="Bravos", ring="spike")        # cycle_s None = whole runtime
    g = _by_id(gates)
    assert g["G36"].level == "FAIL", g["G36"]
    assert _gap_start_s(g["G36"].message) >= 300, g["G36"].message           # the worst gap is PAST 5:00
    assert stats["cycle"].startswith(f"checked 0:00-{stats['runtime']}"), stats["cycle"]
    assert len(stats["unit_windows"]) == 2 * kit_spec.unit_count(_clock(stats["runtime"]) / 60)
    # Narrowed to the opening the gate says PASS - which is exactly why E23 widened it.
    # (Before the 2026-09-03 annotation this read FAIL-with-an-earlier-gap; the declared
    # beats gave the opening its cycle beats, so the first 5:00 now clears the 60s ceiling
    # and only the whole-runtime check still catches the real gap past 5:00.)
    g5 = _by_id(G.run(text, tl, counterparty="Bravos", ring="spike", cycle_s=300.0)[0])
    assert g5["G36"].level == "PASS", g5["G36"]
    assert g["G44"].level == "FAIL" and "unit " in g["G44"].message, g["G44"]  # no rehook in every unit window


def test_unit_window_without_rehook_fails_g44():
    s = _pad_to("The safest thing you own looks like this. An iron spike. ", 140.0)
    s += "[rehook] But here's where their own chart gets strange. "            # inside P3 unit 1 only
    g = _by_id(G.run(_pad_to(s, 805.0), None)[0])
    assert g["G44"].level == "FAIL", g["G44"]
    assert "unit 2 " in g["G44"].message and "unit 1 " not in g["G44"].message, g["G44"].message


def test_conforming_opening_rehooks_every_unit_and_cycles_to_the_end():
    gates, stats = G.run(_conforming_opening(), None, counterparty="Bravos", ring="spike")
    g = _by_id(gates)
    assert g["G44"].level == "PASS", g["G44"]
    assert g["G36"].level == "PASS", g["G36"]
    assert g["G25"].level == "PASS" and "1:2" in g["G25"].src, g["G25"]        # A3 at 10% of ~13.4 min
    assert "hard-codes" not in g["G25"].src
    assert len(stats["unit_windows"]) == 4 and stats["unit_windows"][0].startswith("P3 unit 1")


def _clock(mmss: str) -> float:
    m, _, s = mmss.partition(":")
    return int(m) * 60 + int(s)


# ---- E24: the opening-minute gates - G45 packaging echo + J12, G09 roadmap WARN ----

EP1_TITLE = "The AI Bubble Is Real. What Survives Is Steel."       # packaging/TITLE-CANDIDATES.md, LOCKED 2026-09-01
EP1_THUMB = "STEEL or PAPER?"                                        # thumbnail-FINAL-steelpaper.png, as recorded there
EP1_THUMB_FILE = EP / "packaging/thumbnail-FINAL-steelpaper.png"
OPEN = "The safest thing you own looks like this. An iron spike. "


@needs_ep1
def test_red_steel_and_paper_first_sentence_does_not_answer_the_packaging():
    gates, stats = G.run(SCRIPT.read_text(encoding="utf-8"), G.load_timeline(TIMELINE), counterparty="Bravos",
                         ring="spike", title=EP1_TITLE, thumb=EP1_THUMB, thumb_file=str(EP1_THUMB_FILE))
    g = _by_id(gates)
    assert g["G45"].level == "FAIL" and "'steel'" in g["G45"].message and "proxy" in g["G45"].message, g["G45"]
    assert "proxy" in g["G45"].src and "E24" in g["G45"].src
    assert g["J12"].level == "JUDGE" and str(EP1_THUMB_FILE) in g["J12"].message, g["J12"]
    assert g["G09"].level == "FAIL" and "AFTER" in g["G09"].message, g["G09"]   # 1:20 stays a FAIL, never the 0:45 WARN
    assert "title=" in stats["packaging"]


def test_packaging_words_and_the_g45_levels():
    assert G.packaging_words(EP1_TITLE, EP1_THUMB) == ["ai", "bubble", "real", "surviv", "steel", "paper"]
    assert G._stem_match("surviv", "survive") and G._stem("survived") == "surviv"
    s = _pad_to(OPEN, 805.0)
    assert _by_id(G.run(s, None)[0])["G45"].level == "INFO"                                         # no --title: not run
    g = _by_id(G.run(s, None, title="The Safest Thing You Own Is an Iron Spike")[0])
    assert g["G45"].level == "PASS" and "'safest'" in g["G45"].message, g["G45"]
    g = _by_id(G.run(s, None, title="Every AI Stock Is Steel or an Iron Spike")[0])
    assert g["G45"].level == "WARN" and "sentence 2" in g["G45"].message, g["G45"]                 # only the second echoes
    g = _by_id(G.run(s, None, title=EP1_TITLE, thumb=EP1_THUMB)[0])
    assert g["G45"].level == "FAIL" and "answer the thumbnail" in g["G45"].message, g["G45"]
    assert "no --thumb-file given" in g["J12"].message


def test_green_conforming_opening_answers_its_packaging():
    gates, _ = G.run(_conforming_opening(), None, counterparty="Bravos", ring="spike",
                     title="The Safest Thing You Own Is an Iron Spike", thumb="STEEL or PAPER?",
                     thumb_file="packaging/thumb.png")
    g = _by_id(gates)
    assert g["G45"].level == "PASS", g["G45"]
    assert "open packaging/thumb.png" in g["J12"].message, g["J12"]
    assert not [x for x in gates if x.level == "FAIL"]


def test_promise_after_45s_fails_e24_decided():
    # operator, 2026-09-03 (click): the roadmap lands by 0:45 - G09 FAILs past it, no WARN band
    s = _pad_to(OPEN, 50.0)
    s += "[payoff] Here is what the chart got right. `[pre-key]` [promise] By the end you'll run one test yourself. "
    g = _by_id(G.run(_pad_to(s, 805.0), None)[0])
    assert g["G09"].level == "FAIL" and "AFTER 0:45" in g["G09"].message, g["G09"]
    assert G.PROMISE_WIN == (30.0, 45.0) and G.ROADMAP_S == 45.0


def test_ring_claim_stems_exclude_every_word_of_a_multi_word_token():
    # a two-word ring ("tea break") must not count its own words as the argument (G15b, 2026-09-04)
    stems = G.ring_claim_stems("Tokyo is on a tea break from our debt.", "tea break")
    assert stems == {"tokyo", "debt"}, stems
    assert G.ring_claim_stems("An iron spike ruined everyone.", "spike") == {"iron", "ruin", "everyone"}


def test_g15b_needs_the_argument_not_the_two_word_token(monkeypatch):
    s = _pad_to("Tokyo is on a tea break from our debt. So is everyone. `[post-key]` ", 9.0)
    s = _pad_to(s, 780.0)
    s += "Tokyo is still on its tea break, and nothing else here returns. "
    s = _pad_to(s, 805.0)
    g = _by_id(G.run(s, None, ring="tea break")[0])
    assert g["G15b"].level == "FAIL", g["G15b"]


# ---- G2: the SHORT mode (doc 51 s51.2 the shape; backlog item 4, 2026-09-05) --------------------

def _conforming_short() -> str:
    return (
        "Tokyo took a tea break. And left you holding the tab. [post-key]\n\n"
        "[stakes] Your borrowing costs climbed anyway.\n\n"
        "[rehook] Here's what nobody is watching: the lender.\n\n"
        "[new] Japan holds a trillion dollars of the tab and is selling it.\n\n"
        "[rehook] Here's where it gets dangerous.\n\n"
        "[catalyst] [new] Since February they sold a tenth of the tab.\n\n"
        "[rehook] This is where most people miss it.\n\n"
        "[new] The auction sets the price of the tab, not the Fed.\n\n"
        "[ring] Tokyo is still on its tea break, and the tab is still yours.\n"
    )


def test_short_mode_green_passes_the_shape():
    gates, stats = G.run(_conforming_short(), None, ring="tea break", short=True)
    g = _by_id(gates)
    assert stats["mode"].startswith("short")
    for gid in ("S01", "S02", "S03", "S05", "S06", "S07"):
        assert g[gid].level == "PASS", (gid, g[gid].message)
    assert g["J50"].level == "JUDGE" and g["J51"].level == "JUDGE"
    # the long-form geometry is not asked of a short
    assert not {"G02", "G03", "G21", "G22", "G37", "G39"} & set(g)


def test_short_mode_red_fails_where_the_shape_breaks():
    s = _conforming_short()
    g = _by_id(G.run(s.replace("[new] ", ""), None, ring="tea break", short=True)[0])
    assert g["S03"].level == "FAIL", g["S03"].message                       # no instances
    g = _by_id(G.run(s.replace("Tokyo is still on its tea break, and", "And"), None, ring="tea break", short=True)[0])
    assert g["S05"].level == "FAIL", g["S05"].message                       # the ring never returns
    g = _by_id(G.run(s + "\nNot a panic. Not a plot. Mechanics.\n", None, ring="tea break", short=True)[0])
    assert g["S07"].level == "FAIL"                                          # the brand line belongs to the outro
    g = _by_id(G.run(s.replace(" [post-key]", ""), None, ring="tea break", short=True)[0])
    assert g["S02"].level == "FAIL"                                          # no mechanism declared


def test_short_mode_routes_only_on_a_measured_clock_or_the_flag():
    s = _conforming_short()
    ids = set(_by_id(G.run(s, None, ring="tea break")[0]))                    # estimated clock: long form as before
    assert "G01" in ids and "S01" not in ids
    ids = set(_by_id(G.run(s, None, ring="tea break", short=True)[0]))
    assert "S01" in ids and "G01" not in ids


TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
needs_tokyo = pytest.mark.skipif(not ((TOKYO / "SCRIPT-90S-VO.claude.txt").exists() and (TOKYO / "build-short/timeline.json").exists()),
                                 reason="the Tokyo take is not built here")


@needs_tokyo
def test_tokyo_short_is_judged_by_the_shape():
    """The take (82.7 s, measured) routes to the short mode by itself; the shape holds, and it is judged by the S gates only."""
    text = (TOKYO / "SCRIPT-90S-VO.claude.txt").read_text(encoding="utf-8")
    gates, stats = G.run(text, G.load_timeline(TOKYO / "build-short/timeline.json"), ring="tea break")
    g = _by_id(gates)
    assert stats["mode"].startswith("short") and stats["timing"] == "measured"
    assert g["S01"].level == "PASS" and g["S02"].level == "PASS" and g["S03"].level == "PASS" and g["S05"].level == "PASS"
    assert g["S06"].level == "PASS" and g["S07"].level == "PASS"
    assert not {"G02", "G21", "G22", "G37", "G39"} & set(g)


def _late_mechanism_short() -> str:
    """The conforming short with its [post-key] sentence pushed well past 0:10 (the estimated clock carries a tolerance) by a three-sentence archetype in front of it."""
    s = _conforming_short()
    key = next(l for l in s.split("\n") if "[post-key]" in l)
    return s.replace(key, "I ran risk at a bank for six years and watched this exact thing happen twice.\n\n"
                          "Nobody on the desk called it by its name, and nobody on the desk saw it coming either.\n\n"
                          "Here is the part they never say out loud on television.\n\n" + key, 1)


def test_s02_takes_the_first_ledger_page_as_the_mechanism_e44(tmp_path):
    """E44 / R26-4 (P52 T12): the chart IS the mechanism. A short whose [post-key] sentence ends after 0:10 FAILs S02 on its
    own - and PASSes when the build's scene timeline shows the first ledger page rolling out under the hook; an undeclared
    mechanism sentence still FAILs whatever the page does; a page that lands late does not rescue a late sentence."""
    s = _late_mechanism_short()
    g = _by_id(G.run(s, None, ring="tea break", short=True)[0])
    assert g["S02"].level == "FAIL", g["S02"].message                                  # the sentence alone is late
    assert "no scene timeline" in g["S02"].message
    g = _by_id(G.run(s, None, ring="tea break", short=True, pages=[1.99, 44.88])[0])
    assert g["S02"].level == "PASS" and "ON THE PAGE" in g["S02"].src, g["S02"].message
    assert "first ledger page lands at 1.99s" in g["S02"].message
    g = _by_id(G.run(s, None, ring="tea break", short=True, pages=[17.0])[0])
    assert g["S02"].level == "FAIL" and "first ledger page at 17.00s" in g["S02"].message   # Tokyo v1: the page at 0:17 (E44)
    g = _by_id(G.run(s.replace(" [post-key]", ""), None, ring="tea break", short=True, pages=[1.99])[0])
    assert g["S02"].level == "FAIL" and "not declared" in g["S02"].message             # the page never stands in for the declaration
    # the conforming short is unchanged by a page: the sentence carries it, the message is the old one
    g = _by_id(G.run(_conforming_short(), None, ring="tea break", short=True, pages=[1.99])[0])
    assert g["S02"].level == "PASS" and "ON THE PAGE" not in g["S02"].src
    # load_pages reads the compiler's scenes: a ledger world's span start; clips and plates are not pages
    import json
    scenes = {"scenes": [{"scene_id": "s01", "world": {"kind": "clip"}, "span": [0.0, 1.99]},
                         {"scene_id": "s02", "world": {"kind": "ledger", "page": {}}, "span": [1.99, 38.96]},
                         {"scene_id": "s03", "world": {"asset_id": "plate"}, "span": [38.96, 44.88]},
                         {"scene_id": "s04", "world": {"kind": "ledger"}, "span": [44.88, 61.76]}]}
    (tmp_path / "x-short.timeline.json").write_text(json.dumps(scenes), encoding="utf-8")
    (tmp_path / "timeline.json").write_text(json.dumps({"words": []}), encoding="utf-8")
    assert G.load_pages(tmp_path / "x-short.timeline.json") == [1.99, 44.88]
    assert G.find_scene_timeline(tmp_path / "timeline.json") == tmp_path / "x-short.timeline.json"


@needs_tokyo
def test_tokyo_s02_reads_its_first_page_under_two_seconds():
    """The two shipped shorts were built under E44: Tokyo's first ledger page lands at 1.99 s (the Japan short's at 1.82 s).
    Their S02 verdicts do not move - the sentence still carries them - and the stats name the page."""
    text = (TOKYO / "SCRIPT-90S-VO.claude.txt").read_text(encoding="utf-8")
    scenes = G.find_scene_timeline(TOKYO / "build-short/timeline.json")
    assert scenes is not None and scenes.name == "tokyo-short.timeline.json"
    pages = G.load_pages(scenes)
    assert pages and pages[0] < 2.5, pages
    gates, stats = G.run(text, G.load_timeline(TOKYO / "build-short/timeline.json"), ring="tea break", pages=pages)
    g = _by_id(gates)
    assert g["S02"].level == "PASS" and stats["first_page"] == f"{pages[0]:.2f}s"


def test_g46_long_form_floor_is_eight_minutes():
    """E74 (the operator, 2026-09-13): "longform should never be under 8 minutes". An estimated clock under 8:00 WARNs
    (it is not the take); padded past 8:00 it passes; the short mode never asks it."""
    s = _conforming_short()
    g = _by_id(G.run(s, None, ring="tea break", short=False)[0])
    assert g["G46"].level == "WARN" and "8:00" in g["G46"].message, g["G46"]
    g = _by_id(G.run(_pad_to(s, 500), None, ring="tea break", short=False)[0])
    assert g["G46"].level == "PASS", g["G46"]
    assert "G46" not in _by_id(G.run(s, None, ring="tea break", short=True)[0])


@needs_tokyo
def test_g46_a_measured_short_forced_long_fails_the_floor():
    """The Tokyo take is 82.7 s measured: judged as a long form it FAILs the floor, which is the point of E74."""
    text = (TOKYO / "SCRIPT-90S-VO.claude.txt").read_text(encoding="utf-8")
    g = _by_id(G.run(text, G.load_timeline(TOKYO / "build-short/timeline.json"), ring="tea break", short=False)[0])
    assert g["G46"].level == "FAIL" and "measured" in g["G46"].message, g["G46"]


# ---- G13 by function; G47 / G47b a script's promises about itself; G48 perishable anchors -----------

def _timed(lines):
    """[(start_s, sentence)] -> (text, a measured word timeline) so a sentence lands at an exact second."""
    text = " ".join(s for _, s in lines)
    tl = []
    for start, s in lines:
        for i, w in enumerate(re.findall(r"[A-Za-z0-9'%$]+", beat_tags.strip_marks(s))):
            tl.append({"w": w, "start": start + 0.3 * i, "end": start + 0.3 * i + 0.25})
    return text, tl


A2_TEMPLATE = (62.0, "But here's where their own chart gets strange.")
A1_DATED = (41.5, "By the end, you'll run it yourself: thirty seconds a stock.")


def _rehook_lines(a1=A1_DATED, a2=A2_TEMPLATE):
    lines = [(0.6, "The safest thing you own looks like this."), (3.0, "An iron spike ruined almost everyone who touched it.")]
    lines += [x for x in (a1, a2) if x is not None]
    return lines + [(800.0, "So the spike outlived the paper.")]


def test_g13_a1_is_the_dated_promise_at_41_5s():
    """C04-R016 (ledger b1f8c3fc2999): the template regex reported A1 missing while the dated promise sat at 41.5 s.
    The dated promise IS A1 by doctrine (MAP s3), so G13 passes on it and says which function it read."""
    text, tl = _timed(_rehook_lines())
    g = _by_id(G.run(text, tl, short=False)[0])
    assert g["G13"].level == "PASS", g["G13"]
    assert "A1 at 0:41 (dated promise)" in g["G13"].message and "A2 at 1:02" in g["G13"].message, g["G13"].message


def test_g13_fails_when_the_a1_slot_carries_no_rehook_function():
    text, tl = _timed(_rehook_lines(a1=(41.5, "The receipt was long and nobody read it.")))
    g = _by_id(G.run(text, tl, short=False)[0])
    assert g["G13"].level == "FAIL" and "A1" in g["G13"].message and "A2 at 1:02" in g["G13"].message, g["G13"]


def test_g13_a2_passes_on_a_forward_promise_with_a_time_anchor_not_a_template():
    """The five template families are one sufficient signal, not the definition (C07-R007, ledger cac24f02ea0a)."""
    fwd = (62.0, "In the next minute you'll see the second number the chart hides.")
    text, tl = _timed(_rehook_lines(a2=fwd))
    g = _by_id(G.run(text, tl, short=False)[0])
    assert g["G13"].level == "PASS" and "A2 at 1:02 (forward promise)" in g["G13"].message, g["G13"]
    text, tl = _timed(_rehook_lines(a2=(62.0, "The chart hides a second number.")))
    g = _by_id(G.run(text, tl, short=False)[0])
    assert g["G13"].level == "FAIL" and "A2" in g["G13"].message, g["G13"]


def test_g13_declared_rehook_tag_is_the_function():
    text, tl = _timed(_rehook_lines(a2=(62.0, "[rehook] The chart hides a second number.")))
    g = _by_id(G.run(text, tl, short=False)[0])
    assert g["G13"].level == "PASS" and "A2 at 1:02 ([rehook])" in g["G13"].message, g["G13"]


def _runtime_claim(line: str, at: float = 0.6, end: float = 740.0):
    return _timed([(at, line), (end, "So the spike outlived the paper.")])


def test_g47_span_runtime_promise_against_the_measured_clock():
    """C03-R011 (ledger e319a9d02fe4): 'The script promised eight minutes and ran twelve.' Measured: FAIL."""
    text, tl = _runtime_claim("Give me the next eight minutes and you will see the whole machine.")
    g = _by_id(G.run(text, tl, short=False)[0])
    assert g["G47"].level == "FAIL" and "eight" in g["G47"].message and "measured" in g["G47"].message, g["G47"]
    text, tl = _runtime_claim("Give me the next twelve minutes and you will see the whole machine.")
    g = _by_id(G.run(text, tl, short=False)[0])
    assert g["G47"].level == "PASS", g["G47"]


def test_g47_estimated_clock_warns_and_no_claim_passes():
    text, _ = _runtime_claim("Give me the next eight minutes and you will see the whole machine.")
    g = _by_id(G.run(text, None, short=False)[0])
    assert g["G47"].level == "WARN" and "estimated" in g["G47"].message, g["G47"]
    text, tl = _runtime_claim("The spike ruined almost everyone who touched it.")
    assert _by_id(G.run(text, tl, short=False)[0])["G47"].level == "PASS"


def test_g47_deadline_promise_only_fails_when_it_overshoots_the_clock():
    """'in the next three minutes, you'll calculate yours' (P1's own example) is a deadline inside the video, not its
    runtime; it can only break by pointing past the end."""
    text, tl = _runtime_claim("In the next three minutes, you'll calculate yours.", at=30.0)
    assert _by_id(G.run(text, tl, short=False)[0])["G47"].level == "PASS"
    text, tl = _runtime_claim("In the next 20 minutes, you'll calculate yours.", at=30.0)
    g = _by_id(G.run(text, tl, short=False)[0])
    assert g["G47"].level == "FAIL" and "20" in g["G47"].message, g["G47"]


def test_g47_this_n_minute_video_is_the_whole_runtime():
    text, tl = _runtime_claim("This 5-minute video is the whole map.")
    assert _by_id(G.run(text, tl, short=False)[0])["G47"].level == "FAIL"
    text, tl = _runtime_claim("This twelve-minute video is the whole map.")
    assert _by_id(G.run(text, tl, short=False)[0])["G47"].level == "PASS"


def test_g47b_bare_count_against_the_named_list():
    """C03-R011 (ledger e319a9d02fe4): 'A viewer counts four and then hears five.' Heuristic, so WARN."""
    base = "Nvidia, Microsoft, Apple and Amazon built the boom. The mechanism underneath moved. Now watch the {}. "
    g = _by_id(G.run(base.format("five"), None, short=False)[0])
    assert g["G47b"].level == "WARN" and "the five" in g["G47b"].message and "4" in g["G47b"].message, g["G47b"]
    assert _by_id(G.run(base.format("four"), None, short=False)[0])["G47b"].level == "PASS"


def test_g47b_counted_noun_against_the_ordinals_named():
    s = "Three questions will catch it. The first question is cost. The second question is time. "
    g = _by_id(G.run(s, None, short=False)[0])
    assert g["G47b"].level == "WARN" and "three question" in g["G47b"].message.lower(), g["G47b"]
    assert _by_id(G.run(s + "The third question is who pays. ", None, short=False)[0])["G47b"].level == "PASS"


def test_g48_lists_publication_relative_anchors_with_the_clock():
    """C09-R013 (ledger 8eb3d01c6196, 7e61f43b1162): a re-upload renews every relative anchor at today's date."""
    text, tl = _timed([(0.6, "Yields jumped again this week."), (5.0, "Two weeks ago nobody noticed, and right now nobody is.")])
    g = _by_id(G.run(text, tl, short=False)[0])
    assert g["G48"].level == "WARN", g["G48"]
    for bit in ("0:00 'this week'", "0:05 'Two weeks ago'", "'right now'", "re-upload"):
        assert bit in g["G48"].message, (bit, g["G48"].message)
    text, tl = _timed([(0.6, "Yields jumped again in March 2024."), (5.0, "Nobody noticed.")])
    assert _by_id(G.run(text, tl, short=False)[0])["G48"].level == "PASS"


def test_g47_g48_run_on_shorts_too():
    """The defects are the script's words, not the long-form geometry: a short that says 'this week' rots the same."""
    g = _by_id(G.run(_conforming_short() + "\nThis week the tab grew.\n", None, ring="tea break", short=True)[0])
    assert g["G48"].level == "WARN" and {"G47", "G47b"} <= set(g)

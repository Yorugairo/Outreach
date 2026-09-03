"""DECLARED section of <script>-SCREENS.md: one row per beat tag, the opening
gate's window verdict cited (R1), the verdict column left for the agent (R2).

CHECK-RESPONSIBILITIES R2 / s3a: a declared beat is a claim. The tool proves
the tag sits where the shape requires it; the agent proves the sentence IS
the beat. STRENGTH-LOOP s8a: a gate that emits no artifact is skipped, so
the enumeration is the deliverable and the strength log verdicts every row.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

import enumerate_strength_screens as E   # noqa: E402
import audit_script_doctrine as A         # noqa: E402
import beat_tags                          # noqa: E402
import gate_opening_structure as G        # noqa: E402

EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
SCRIPT = EP / "SCRIPT-G-VO.txt"
needs_ep1 = pytest.mark.skipif(not SCRIPT.exists(), reason="episode one script not on disk")

ROW = re.compile(r'^- \[([a-z-]+)\]@(\d+:\d{2})  window: (.+?)  "(.*)"  → verdict: (.*)$')
FILLER = "The mechanism underneath moved and almost nobody on the desk looked at it. "


def _pad_to(text: str, target_s: float) -> str:
    while A.secs(A.spoken(text)) < target_s:
        text += FILLER
    return text


def _conforming_opening() -> str:
    """Verbatim from tests/test_gate_opening_structure.py (a function there,
    not a module constant): every doc-38 / P1 / P2 beat declared where the
    text has no signature, padded to ~13.4 min so the geometry matches a real
    episode (P1 ~1:10, beat 5 from 0:47, P2 ~1:10-2:46)."""
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


def _build(tmp_path: Path, text: str, **kw) -> tuple[str, list[re.Match], dict]:
    src = tmp_path / "SCRIPT-T-VO.txt"
    src.write_text(text, encoding="utf-8")
    dest, counts = E.build_screens(src, **kw)
    assert dest == tmp_path / "SCRIPT-T-SCREENS.md" and dest.exists()
    body = dest.read_text(encoding="utf-8")
    declared = body.split("## DECLARED", 1)[1]
    rows = [m for m in (ROW.match(l) for l in declared.splitlines()) if m]
    return body, rows, counts


# ---- 1. episode one, the red baseline -------------------------------------

@needs_ep1
def test_red_steel_and_paper_lists_every_tag_the_parser_finds(tmp_path):
    src = tmp_path / SCRIPT.name
    shutil.copy(SCRIPT, src)
    dest, counts = E.build_screens(src, ring="spike", counterparty="Bravos")
    body = dest.read_text(encoding="utf-8")
    tags = beat_tags.find_beats(src.read_text(encoding="utf-8"))
    assert f"## DECLARED — beat tags ({len(tags)})" in body
    rows = [m for m in (ROW.match(l) for l in body.split("## DECLARED", 1)[1].splitlines()) if m]
    assert len(rows) == len(tags) == counts["declared"]
    for m in rows:
        assert re.fullmatch(r"\d+:\d{2}", m.group(2)) and m.group(3)
    if not tags:      # ep1 as recorded declares nothing - the absence is stated, never elided
        assert E.NO_BEATS_LINE in body
    # the earlier sections and the heading order are intact
    for h in ("## X1 —", "## P6 —", "## P1J —", "## P5A —", "## P4C —"):
        assert body.index(h) < body.index("## DECLARED")


# ---- 2. the conforming opening: the gate's own verdicts, cited -------------

def test_green_declared_rows_carry_the_gate_verdicts(tmp_path):
    text = _conforming_opening()
    body, rows, counts = _build(tmp_path, text, ring="spike", counterparty="Bravos")
    tags = beat_tags.find_beats(text)
    assert len(rows) == len(tags) == counts["declared"] == 34
    assert [m.group(1) for m in rows] == [t for t, _ in tags]        # script order
    verdicts = {m.group(1) + "@" + m.group(2): m.group(3) for m in rows}
    assert not any("FAIL" in v for v in verdicts.values()), verdicts
    geo = G.geometry(A.secs(A.spoken(text)))
    p1_end, p2_close = geo["p1_end"] * G.EST_TOL, geo["p2_end"] * G.EST_TOL
    for key, win in verdicts.items():
        tag, clock = key.split("@")
        mins, secs = clock.split(":")
        t = int(mins) * 60 + int(secs)
        if t > p2_close:                   # past the gate's in_p2 reach: no gate counts it
            assert win.startswith("n/a — outside opening window"), key
        elif tag == "reflect" and t > p1_end:  # the P2 dab: G31 WARNs "1 dabs for 3 loops" on this fixture
            assert win == "WARN — G31", key
        else:
            assert all(part.startswith("PASS — ") for part in win.split(", ")), (key, win)
    # phase-split tags resolve to ONE gate by clock; both P2 loop gates are cited
    assert verdicts["tricolon@0:37"] == "PASS — G12"
    assert verdicts["rehook@0:59"] == "PASS — G13" and verdicts["rehook@1:22"] == "PASS — G25"
    assert verdicts["loop@1:12"] == "PASS — G19, PASS — G21"
    # the quoted sentence is the beat's line with every mark stripped
    quotes = {m.group(1) + "@" + m.group(2): m.group(4) for m in rows}
    assert quotes["promise@0:37"].startswith("It isn't a rebuttal") and "[" not in quotes["promise@0:37"]
    assert all(len(q) <= E.QUOTE_MAX for q in quotes.values())


# ---- 3. no tags: the absence is a line, not a blank ------------------------

def test_untagged_script_states_no_declared_beats(tmp_path):
    body, rows, counts = _build(tmp_path, "The spike went in. The paper burned. The desk looked away.")
    assert counts["declared"] == 0 and not rows
    assert "## DECLARED — beat tags (0)" in body
    assert E.NO_BEATS_LINE in body


# ---- 4. the verdict column is the agent's - the tool never fills it --------

def test_verdict_column_is_blank_on_every_row(tmp_path):
    _, rows, _ = _build(tmp_path, _conforming_opening(), ring="spike", counterparty="Bravos")
    assert rows and all(m.group(5) == "____" for m in rows)

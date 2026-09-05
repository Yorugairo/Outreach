"""P37 T4 - G15b (47 s2 G-g). The ring closes on the mechanism: a script that echoes the P1
token while the argument has drifted fails the new half and passes the old one."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_opening_structure as G  # noqa: E402

RING = "spike"


def _script(close: str) -> str:
    """P1 plants the token inside a causal claim; the body is filler; the close is the variable."""
    body = "The next fact lands here. " * 60
    return (f"The spike in memory prices is the debt bill arriving early, and the builders pay it first. "
            + body + close)


def _g15(text: str) -> dict[str, G.Gate]:
    gates, _ = G.run(text, None, None, RING, 300.0, None)
    return {g.id: g for g in gates}


def test_a_close_that_returns_the_argument_passes_both_halves():
    g = _g15(_script("So the spike was never a price story. It was the debt bill, and the builders paid it first."))
    assert g["G15"].level == "PASS"
    assert g["G15b"].level == "PASS", g["G15b"].message


def test_a_close_that_echoes_the_token_with_a_drifted_argument_fails_the_new_half_only():
    g = _g15(_script("And that is why every spike on the chart is a chance to buy the dip."))
    assert g["G15"].level == "PASS"                       # the old token check still passes
    assert g["G15b"].level == G.RING_MECHANISM_LEVEL, g["G15b"].message
    assert "shares 0" in g["G15b"].message or "shares 1" in g["G15b"].message


def test_a_close_without_the_token_is_named():
    g = _g15(_script("And that is the whole story of memory prices."))
    assert g["G15b"].level == G.RING_MECHANISM_LEVEL and "never returns" in g["G15b"].message


def test_claim_stems_drop_the_token_and_stopwords():
    stems = G.ring_claim_stems("The spike in memory prices is the debt bill arriving early.", RING)
    assert "spike" not in stems and "the" not in stems
    assert {"memori", "debt", "bill"} <= stems or {"memory", "debt", "bill"} <= stems

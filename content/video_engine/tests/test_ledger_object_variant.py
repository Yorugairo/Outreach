"""The ledger page's `object` variant: a metaphor drawn in ink on the cream.

All five original variants are charts, so the page could only ever become evidence.
`object` is the other half of RULE-the-page-is-the-ground - a prop page on the same
clock and the same deckle, so a scene carries the argument and then transforms into the
proof without a plate change.

The contract differs from a chart's: there are no values, so no sign geometry and no
badge keying. What survives is the page's own discipline - a registered asset (never
inline art), one placement per asset, and a source line whenever a prop carries a
FIGURE, because a number drawn in ink is as much a claim as a number on an axis.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import ledger_page as LP  # noqa: E402

BASE = {"title": "The hedge is a toll gate", "src": "metaphor page - no figures asserted"}


def page(**over):
    d = dict(BASE); d.update(over); return d


def test_object_is_a_variant_and_the_chart_variants_are_unchanged():
    assert "object" in LP.VARIANTS
    assert LP.CHART_VARIANTS == ("line", "bars", "race", "decline", "progress")


def test_a_prop_page_validates_without_any_values():
    p = page(props=[{"asset": "prop-toll-gate-v1", "at": "centre"}])
    assert LP.validate(p, "object") == []
    spec = LP.build_spec(p, "object")
    assert spec["builder"] == "object"
    assert spec["values"] == [] and spec["labels"] == []
    assert spec["props"][0]["asset"] == "prop-toll-gate-v1"


def test_the_same_page_without_props_is_refused():
    assert any("props" in e for e in LP.validate(page(), "object"))


def test_props_must_be_registered_assets_not_inline_art():
    errs = LP.validate(page(props=[{"at": "centre"}]), "object")
    assert any("'asset'" in e for e in errs)


def test_one_asset_one_placement():
    errs = LP.validate(page(props=[{"asset": "prop-toll-gate-v1"},
                                   {"asset": "prop-toll-gate-v1", "at": "left"}]), "object")
    assert any("placed twice" in e for e in errs)


def test_a_datum_placement_needs_an_index():
    """`at: datum` is what lets a prop be positioned RELATIVE TO CHART DATA - the same
    resolveTarget the callout and spotlight species already use."""
    errs = LP.validate(page(props=[{"asset": "prop-arrow-v1", "at": "datum"}]), "object")
    assert any("index" in e for e in errs)
    ok = page(props=[{"asset": "prop-arrow-v1", "at": "datum", "index": 2}])
    assert LP.validate(ok, "object") == []
    assert LP.build_spec(ok, "object")["props"][0]["index"] == 2


def test_a_prop_carrying_a_figure_still_owes_a_source():
    """A number drawn in ink is as much a claim as a number on an axis."""
    no_src = {"title": "Paying for a box dated later",
              "props": [{"asset": "prop-crate-v1", "figure": "10 YEARS"}]}
    errs = LP.validate(no_src, "object")
    assert any("source" in e for e in errs)


def test_chart_validation_does_not_leak_into_object_pages():
    """A chart page with no chartable series is refused; an object page never is."""
    empty = page()
    assert any("props" in e for e in LP.validate(empty, "object"))
    # the same dict as a chart is refused for a DIFFERENT reason - it has no series
    chart_errs = LP.validate(empty, "bars")
    assert chart_errs and not any("props" in e for e in chart_errs)


@pytest.mark.parametrize("placement", LP.PROP_PLACEMENTS)
def test_every_declared_placement_is_accepted(placement):
    p = page(props=[{"asset": "prop-x-v1", "at": placement,
                     **({"index": 0} if placement == "datum" else {})}])
    assert LP.validate(p, "object") == []

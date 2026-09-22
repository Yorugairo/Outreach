"""R26-231: an authored page build must fit its row's actual page envelope.

The fixtures are deliberately synthetic: this slice checks the compiler clock,
not a finance claim.  Renderer constants are exercised through the compiler's
existing gate mirror, while intrinsic builder clocks are covered by the
builder-specific values the player owns.
"""
from __future__ import annotations

import math
import sys

import pytest

ROOT = __import__("pathlib").Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402


def _scene(
    *,
    builder: str = "story",
    span: float = 12.0,
    build_s: float | None = 2.0,
    build: str | None = None,
    enter: str | None = None,
    exit_: str | None = None,
    title: str | None = None,
    periods: list[str] | None = None,
    values: list[float] | None = None,
    axes: dict | None = None,
) -> dict:
    page = {"builder": builder, "title": title or f"synthetic {builder}"}
    if build_s is not None:
        page["build_s"] = build_s
    if build is not None:
        page["build"] = build
    if enter is not None:
        page["enter"] = enter
    if exit_ is not None:
        page["exit"] = exit_
    if periods is not None:
        page["periods"] = periods
    if values is not None:
        page["values"] = values
    if axes is not None:
        page["axes"] = axes
    return {
        "scene_id": "fed-row-07",
        "span": [0.0, float(span)],
        "world": {"kind": "ledger", "page": page},
    }


def _error(scene: dict) -> str | None:
    return B.page_build_span_error(scene)


def test_authored_build_that_overruns_names_the_row_and_page():
    scene = _scene(span=8.0, title="authored build row")
    need = B.page_build_envelope_s(scene)
    assert need is not None and need > scene["span"][1]
    err = _error(scene)
    assert err is not None
    assert "fed-row-07" in err and "authored build row" in err
    assert "entry/build/leave" in err


def test_authored_build_accepts_just_fit_without_mutating_the_span():
    scene = _scene()
    need = B.page_build_envelope_s(scene)
    assert need is not None
    scene["span"][1] = need
    before = list(scene["span"])
    assert _error(scene) is None
    assert scene["span"] == before


def test_short_authored_clock_is_not_padded_to_the_default_build():
    scene = _scene(build_s=2.0)
    assert math.isclose(B.page_build_envelope_s(scene), 4.4 + 2.0 + 2.0)
    scene["span"][1] = 8.39
    assert _error(scene) is not None
    scene["span"][1] = 8.4
    assert _error(scene) is None


def test_cut_exit_removes_only_the_page_retract_allowance():
    scene = _scene(build_s=2.0, exit_="cut")
    assert math.isclose(B.page_build_envelope_s(scene), 4.4 + 2.0)
    scene["span"][1] = 6.4
    assert _error(scene) is None


def test_transition_stamp_is_consumed_before_the_final_span_check():
    outgoing = _scene(span=6.4, build_s=2.0)
    outgoing["span"] = [1.0, 7.4]
    incoming = _scene(span=12.0, build_s=2.0)
    incoming["span"] = [7.4, 19.4]
    incoming["exit"] = "suck"
    assert _error(outgoing) is not None
    B.stamp_transition_pages([outgoing, incoming])
    assert outgoing["world"]["page"]["exit"] == "cut"
    assert _error(outgoing) is None


def test_per_line_build_total_is_checked_against_the_page_row():
    spec = B.page_build_spec("lines:2", "dense-line", 4, "synthetic row")
    scene = _scene(builder="dense-line", build=spec["mode"], build_s=spec["build_s"], span=14.39)
    need = B.page_build_envelope_s(scene)
    assert spec["build_s"] == 8.0
    assert need is not None and math.isclose(need, 14.4)
    assert _error(scene) is not None
    scene["span"][1] = need + 0.01
    assert _error(scene) is None


@pytest.mark.parametrize(
    ("enter", "kwargs", "expected"),
    [
        (None, {}, 4.4 + 2.0 + 2.0),
        ("axes", {}, 2.0 + 2.0),
        ("mount", {"mount_s": 2.0}, 2.0 + 0.5 + 2.0 + 2.0),
        ("morph", {"morph_s": 1.5}, 1.5 + 2.0 + 2.0),
        ("built", {}, 2.0),
        ("snap", {}, 2.0),
        ("camera", {}, 2.0),
        ("throw", {}, 2.0),
        ("drop", {}, 2.0),
        ("spiral", {}, 1.6 + 2.0),
    ],
)
def test_page_entry_clock_is_preserved(enter, kwargs, expected):
    page = _scene(enter=enter, **({} if enter is None else {}))
    page["world"]["page"].update(kwargs)
    assert math.isclose(B.page_build_envelope_s(page), expected)


@pytest.mark.parametrize(
    ("builder", "expected_build", "extra"),
    [
        ("dense-line", 2.0, {}),
        ("story", 2.0, {}),
        ("object", 2.0, {}),
        ("race", 0.6 + 2 * 1.2, {"periods": ["a", "b", "c"]}),
        ("decline", 3.6, {}),
        ("combo", 4.5, {}),
        ("share", 3.2, {}),
        ("tiers", 4.5, {}),
        ("treemap", 3.6, {}),
    ],
)
def test_applicable_builder_uses_the_player_clock(builder, expected_build, extra):
    scene = _scene(builder=builder, build_s=2.0, **extra)
    assert math.isclose(B.page_build_duration_s(scene["world"]["page"]), expected_build)
    need = B.page_build_envelope_s(scene)
    assert math.isclose(need, 4.4 + expected_build + 2.0)
    scene["span"][1] = need
    assert _error(scene) is None
    scene["span"][1] -= 0.01
    assert _error(scene) is not None


def test_breakthrough_bars_use_their_longer_renderer_envelope():
    scene = _scene(
        builder="story",
        build_s=2.0,
        values=[5.0, 15.0],
        axes={"overflow": "burst", "domain": [0.0, 10.0]},
    )
    # The bars player owns 2.0 + hold .5 + burst .6 + settle .3.
    assert math.isclose(B.page_build_duration_s(scene["world"]["page"]), 3.4)
    assert math.isclose(B.page_build_envelope_s(scene), 4.4 + 3.4 + 2.0)


@pytest.mark.parametrize(
    "axes",
    [
        {"overflow": "stack", "domain": [0.0, 5.0]},
        {"overflow": "stack", "domain": [-5.0, -1.0]},
    ],
)
def test_stack_breakthrough_rejects_nonpositive_domain_or_comparator(axes):
    scene = _scene(values=[0.0, 10.0], axes=axes, title="invalid stack")
    err = _error(scene)
    assert err is not None
    assert "fed-row-07" in err and "invalid stack" in err
    assert "stack breakthrough" in err


@pytest.mark.parametrize(
    "span",
    [
        [0.0, math.inf],
        [math.nan, 10.0],
        [1e308, -1e308],
    ],
)
def test_nonfinite_span_endpoint_or_delta_is_rejected(span):
    scene = _scene()
    scene["span"] = span
    err = _error(scene)
    assert err is not None
    assert "finite" in err


def test_unauthored_legacy_page_is_not_retimed_by_the_new_guard():
    scene = _scene(build_s=None, span=0.5)
    page = scene["world"]["page"]
    assert math.isclose(B.page_build_duration_s(page), 3.0)
    assert math.isclose(B._page_entry_build_s(page, 3.0), 7.4)
    assert B.page_build_envelope_s(scene) is None
    assert _error(scene) is None


def test_validate_page_build_spans_reports_the_first_overrun():
    scene = _scene(span=1.0, title="first overrun")
    with pytest.raises(ValueError, match="fed-row-07.*first overrun"):
        B.validate_page_build_spans([scene])

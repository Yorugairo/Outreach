"""P45 T8 - the motion-energy measurement, checked where it can be checked without a browser.

Three things are provable off-line and are proved here:
  1. the energy integral `E = integral |v|^2 dt` on a synthetic trajectory (exact for constant
     velocity at any fps; a damped spring agrees between two sample rates),
  2. the classification table - every class it names is a real class in the reviewed template
     (grep-grounded), and every class actually observed under `#stage` resolves to PRIMARY or
     SECONDARY rather than UNCLASSIFIED,
  3. the aggregation by scene window and the shape of the emitted report.

The headless run is a smoke test: it is the only part that needs Chromium, and it skips when
Playwright or its browser is unavailable rather than failing the suite.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "content/video_engine/scripts"))

import measure_motion_energy as mme  # noqa: E402

TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
TOKYO_SHORT = REPO / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short"

# Every distinct (class, key) pair seen under #stage by walking the built Tokyo short's live DOM at
# t = 1, 6, 10, 20, 30, 40, 55, 65, 75, 85 s (2026-09-05, depth <= 5). The KEY is part of the roster
# because classification falls back to the nearest classified ancestor: `span.g` (the depth-5
# per-glyph handwriting reveal) and the bare SVG nodes carry no class of their own and are only
# classifiable in place. This roster is the ground truth the table has to cover.
_LP = "/#wB/div.lp:0/div.lp-page:0"
_CHART = f"{_LP}/svg.lp-chart:6"
OBSERVED_STAGE_ELEMENTS = (
    ("world", "/#wA"),
    ("world ledger", "/#wB"),
    ("clipv", "/#wA/video.clipv:0"),
    ("lp", "/#wB/div.lp:0"),
    ("lp-page", _LP),
    ("lp-grain", f"{_LP}/svg.lp-grain:0"),
    ("lp-edge", f"{_LP}/div.lp-edge:1"),
    ("lp-field", f"{_LP}/div.lp-field:2"),
    ("lp-ink lp-title", f"{_LP}/div.lp-ink:3"),
    ("lp-ink lp-sub", f"{_LP}/div.lp-ink:4"),
    ("lp-ink lp-src", f"{_LP}/div.lp-ink:5"),
    ("lp-chart", _CHART),
    ("lp-rail", f"{_LP}/div.lp-rail:7"),
    ("w", f"{_LP}/div.lp-ink:3/span.w:0"),
    ("g", f"{_LP}/div.lp-ink:3/span.w:0/span.g:0"),
    ("ax", f"{_CHART}/line.ax:0"),
    ("grid", f"{_CHART}/line.grid:1"),
    ("lab", f"{_CHART}/text.lab:2"),
    ("ser", f"{_CHART}/path.ser:12"),
    ("ser muted", f"{_CHART}/path.ser:15"),
    ("bar pos", f"{_CHART}/rect.bar:3"),
    ("bar pos emph", f"{_CHART}/rect.bar:4"),
    ("val", f"{_CHART}/text.val:5"),
    ("sname", f"{_CHART}/text.sname:14"),
    ("cpill", f"{_CHART}/g:8/rect.cpill:0"),
    ("callout", f"{_CHART}/g:8/text.callout:1"),
    ("", f"{_CHART}/circle:13"),                       # an unclassed chart node
    ("pill lp-pill", f"{_LP}/div.lp-field:2/div.pill:3"),
    ("pill-label", f"{_LP}/div.lp-field:2/div.pill:3/span.pill-label:0"),
    ("pill-row", f"{_LP}/div.lp-field:2/div.pill:3/span.pill-row:1"),
    ("pill-num", f"{_LP}/div.lp-field:2/div.pill:3/span.pill-row:1/span.pill-num:0"),
    ("pill-tag", f"{_LP}/div.lp-field:2/div.pill:3/span.pill-row:1/span.pill-tag:1"),
    ("dock", "/#dock-1"),
    ("slide-frame", "/#dock-1/div.slide-frame:0"),
    ("rail", "/#dock-1/#r1"),
    ("stage phrase onpage", "/#caption"),
    ("cg", "/#caption/span.cg:0"),
    ("cw", "/#caption/span.cg:0/span.cw:0"),
    ("cw on", "/#caption/span.cg:0/span.cw:1"),
    ("cw ck", "/#caption/span.cg:0/span.cw:2"),
    ("cw ck lit", "/#caption/span.cg:0/span.cw:3"),
    ("", "/#species/g:0/path:3"),                      # species life draws unclassed SVG
    ("", "/#wash"), ("", "/#spot"), ("", "/#plife"), ("", "/#seam"), ("", "/#species"),
    ("", "/#dock-1/div.slide-frame:0/#i1"),
    ("", "/#dock-2/div.slide-frame:0/#i2"),
)


# --------------------------------------------------------------------------- the energy integral
def _track(fn, duration: float, fps: float):
    return [fn(i / fps) for i in range(int(round(duration * fps)) + 1)]


def test_constant_velocity_energy_is_exact_at_any_fps():
    # Arrange: x(t) = 120 t px over 2 s. The true integral is |v|^2 * T = 120^2 * 2.
    expected = 120.0**2 * 2.0
    # Act
    at_15 = mme.integrate_energy(_track(lambda t: 120.0 * t, 2.0, 15), 15)
    at_60 = mme.integrate_energy(_track(lambda t: 120.0 * t, 2.0, 60), 60)
    # Assert
    assert at_15 == pytest.approx(expected, rel=1e-9)
    assert at_60 == pytest.approx(expected, rel=1e-9)


def test_spring_settle_energy_agrees_between_two_sample_rates():
    # Arrange: the settle the template's analytic spring evaluator produces -
    # x(t) = A e^(-zeta w0 t) cos(wd t), zeta = 0.35, w0 = 12 rad/s (48 s48.6 "light metallic").
    zeta, w0, amp = 0.35, 12.0, 40.0
    wd = w0 * math.sqrt(1 - zeta**2)

    def x(t):
        return amp * math.exp(-zeta * w0 * t) * math.cos(wd * t)

    # Act: the same trajectory sampled at two rates
    coarse = mme.integrate_energy(_track(x, 1.5, 60), 60)
    fine = mme.integrate_energy(_track(x, 1.5, 120), 120)
    # Assert: the sum converges, so the two rates must agree to a few percent
    assert coarse > 0
    assert coarse == pytest.approx(fine, rel=0.05)


def test_two_dimensional_track_sums_its_components():
    xs = [(3.0 * i, 4.0 * i) for i in range(6)]
    assert mme.integrate_energy(xs, 10) == pytest.approx((3.0**2 + 4.0**2) * 5 * 10)


def test_a_track_shorter_than_two_samples_has_no_energy():
    assert mme.integrate_energy([], 15) == 0.0
    assert mme.integrate_energy([(1.0, 2.0)], 15) == 0.0


# --------------------------------------------------------------------------- classification table
def template_class_tokens(template: Path = TEMPLATE) -> set[str]:
    """Every class token the reviewed player can put on an element - the grep the table is held to."""
    import render_baseline as RB
    text = RB.player_text() if template is TEMPLATE else template.read_text(encoding="utf-8")
    tokens: set[str] = set()
    for pattern in (r'class\s*(?:=|:)\s*"([^"]*)"',
                    r"className\s*=\s*[\"']([^\"']*)[\"']",
                    r"classList\.(?:add|toggle|remove)\(\s*[\"']([^\"']*)[\"']"):
        for m in re.finditer(pattern, text):
            tokens |= set(m.group(1).split())
    for m in re.finditer(r"(?<![\w.#-])\.([a-zA-Z][\w-]*)(?=[\s,{:.>\[])", text):   # CSS selectors
        tokens.add(m.group(1))
    return tokens


def test_every_classified_class_is_a_real_template_class():
    tokens = template_class_tokens()
    assert len(tokens) > 50, "the class extractor found almost nothing - the template moved or changed shape"
    declared = [name for name, kind, _, _ in mme.CLASSIFICATION if kind == "class"]
    missing = sorted(n for n in declared if n not in tokens)
    assert missing == [], f"CLASSIFICATION names classes the template does not define: {missing}"


def test_every_element_observed_under_stage_is_classified():
    unresolved = [(cls, key) for cls, key in OBSERVED_STAGE_ELEMENTS
                  if mme.classify(cls, key)[0] == mme.UNCLASSIFIED]
    assert unresolved == [], f"unclassified elements observed under #stage: {unresolved}"


def test_the_observed_roster_splits_into_both_labels():
    labels = {mme.classify(cls, key)[0] for cls, key in OBSERVED_STAGE_ELEMENTS}
    assert labels == {mme.PRIMARY, mme.SECONDARY}
    assert mme.classify("world ledger", "/#wB")[0] == mme.PRIMARY
    assert mme.classify("cw ck lit", "/#caption/span.cg:0/span.cw:3")[0] == mme.SECONDARY
    # the page's ink write-on is part of the page build, so its glyphs are PRIMARY by inheritance
    assert mme.classify("g", f"{_LP}/div.lp-ink:3/span.w:0/span.g:0")[0] == mme.PRIMARY
    # a badge on the page is SECONDARY even though every one of its ancestors is PRIMARY
    assert mme.classify("pill lp-pill", f"{_LP}/div.lp-field:2/div.pill:3")[0] == mme.SECONDARY


def test_the_caption_block_is_classified_by_its_id_not_its_classes():
    # #caption carries `class="stage phrase onpage"`, none of which is a table name.
    label, why = mme.classify("stage phrase onpage", "/#caption")
    assert label == mme.SECONDARY
    assert "caption block" in why


def test_an_unclassed_child_inherits_from_the_nearest_classified_ancestor():
    label, why = mme.classify("", "/#species/g:0/path:3")
    assert label == mme.SECONDARY
    assert why.startswith("inherited from #species")
    label, why = mme.classify("", "/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:7/circle:5")
    assert label == mme.PRIMARY
    assert "inherited from svg.lp-chart:7" in why


def test_an_unknown_element_is_reported_not_dropped():
    label, why = mme.classify("brand-new-thing", "/div.brand-new-thing:0")
    assert label == mme.UNCLASSIFIED
    assert "no rule" in why


def test_primary_and_secondary_rosters_are_disjoint_and_complete():
    labels = {label for _, _, label, _ in mme.CLASSIFICATION}
    assert labels == {mme.PRIMARY, mme.SECONDARY}
    names = [(n, k) for n, k, _, _ in mme.CLASSIFICATION]
    assert len(names) == len(set(names)), "a name is declared twice in CLASSIFICATION"


# --------------------------------------------------------------------------- aggregation
def _el(key, cls, cx, cy, op=1.0, vis=True, sig="s", tag="div", depth=0):
    return {"key": key, "cls": cls, "tag": tag, "depth": depth, "vis": vis, "op": op,
            "sig": sig, "cx": cx, "cy": cy}


WINDOWS = [("s01", 0.0, 1.0), ("s02", 1.0, 2.0)]


def test_scene_windows_are_read_from_the_timeline_rows():
    timeline = {"scenes": [{"scene_id": "s01", "span": [0.0, 5.09]},
                           {"scene_id": "s02", "span": [5.09, 8.99]}]}
    assert mme.scene_windows(timeline) == [("s01", 0.0, 5.09), ("s02", 5.09, 8.99)]


def test_scene_windows_are_half_open_and_the_last_scene_owns_the_tail():
    assert mme.scene_for(0.0, WINDOWS) == "s01"
    assert mme.scene_for(0.999, WINDOWS) == "s01"
    assert mme.scene_for(1.0, WINDOWS) == "s02"      # half-open: the boundary belongs to s02
    assert mme.scene_for(2.5, WINDOWS) == "s02"      # past the end, not "(outside)"
    assert mme.scene_for(-1.0, WINDOWS) == "(outside)"


def test_energy_lands_in_the_scene_window_that_holds_its_frame():
    fps = 2.0
    # one PRIMARY element moving 10 px per frame throughout both scenes
    frames = [(t, [_el("/#wA", "world", 10.0 * i, 0.0)]) for i, t in enumerate([0.0, 0.5, 1.0, 1.5])]
    folded = mme.accumulate(frames, fps, WINDOWS)
    s01, s02 = folded["scenes"]["s01"], folded["scenes"]["s02"]
    # frames at 0.5 (s01) and at 1.0, 1.5 (s02) each carry one 10 px step: E = 100 * fps
    assert s01["e_trans"][mme.PRIMARY] == pytest.approx(100 * fps)
    assert s02["e_trans"][mme.PRIMARY] == pytest.approx(2 * 100 * fps)
    assert folded["pieces"]["/#wA"]["e_trans"] == pytest.approx(3 * 100 * fps)


def test_primary_and_secondary_are_kept_apart_per_scene():
    fps = 2.0
    frames = [(t, [_el("/#wA", "world", 10.0 * i, 0.0),
                   _el("/#caption/span.cg:0/span.cw:0", "cw", 2.0 * i, 0.0, tag="span", depth=2)])
              for i, t in enumerate([0.0, 0.5])]
    folded = mme.accumulate(frames, fps, WINDOWS)
    row = mme._scene_row(folded["scenes"]["s01"])
    assert row["e_primary"] == pytest.approx(100 * fps)
    assert row["e_secondary"] == pytest.approx(4 * fps)
    assert row["ratio"] == pytest.approx(0.04)


def test_a_content_swap_is_a_cut_not_a_velocity():
    fps = 2.0
    frames = [(0.0, [_el("/#caption/span.cw:0", "cw", 100.0, 0.0, sig="span|cw|Tokyo")]),
              (0.5, [_el("/#caption/span.cw:0", "cw", 900.0, 0.0, sig="span|cw|Osaka")])]
    folded = mme.accumulate(frames, fps, WINDOWS)
    assert folded["pieces"]["/#caption/span.cw:0"]["e_trans"] == 0.0


def test_translation_needs_visibility_in_both_frames_but_opacity_energy_does_not():
    fps = 2.0
    frames = [(0.0, [_el("/#spot", "", 0.0, 0.0, op=0.0, vis=False)]),
              (0.5, [_el("/#spot", "", 40.0, 0.0, op=0.5, vis=True)])]
    folded = mme.accumulate(frames, fps, WINDOWS)
    piece = folded["pieces"]["/#spot"]
    assert piece["e_trans"] == 0.0, "an element that was invisible last frame did not travel"
    assert piece["e_opacity"] == pytest.approx(0.25 * fps)
    assert folded["scenes"]["s01"]["e_opacity"][mme.SECONDARY] == pytest.approx(0.25 * fps)


def test_movers_are_counted_per_frame_for_the_cohesion_read():
    fps = 2.0
    still = _el("/#plife", "", 0.0, 0.0)
    frames = [(0.0, [_el("/#wA", "world", 0.0, 0.0), still]),
              (0.5, [_el("/#wA", "world", 30.0, 0.0), still])]
    row = mme._scene_row(mme.accumulate(frames, fps, WINDOWS)["scenes"]["s01"])
    assert row["max_movers"] == 1, "only #wA travelled; #plife held still"
    assert row["frames"] == 2
    assert row["mean_movers"] == pytest.approx(0.5)


def test_the_largest_single_frame_step_is_reported_so_a_relayout_is_visible():
    fps = 2.0
    # a steady 10 px/frame drift, then one 900 px jump: the jump is what the diagnostic must surface
    frames = [(t, [_el("/#wA", "world", x, 0.0)])
              for t, x in zip([0.0, 0.5, 1.0], [0.0, 10.0, 910.0])]
    folded = mme.accumulate(frames, fps, WINDOWS)
    assert folded["pieces"]["/#wA"]["max_step_px"] == pytest.approx(900.0)
    assert mme._scene_row(folded["scenes"]["s02"])["max_step_px"] == pytest.approx(900.0)
    assert mme._scene_row(folded["scenes"]["s01"])["max_step_px"] == pytest.approx(10.0)


def test_the_report_names_its_blind_spots_and_any_silent_scene():
    fps = 2.0
    # s01 has no primary translation at all - the case a video-carried scene produces
    frames = [(t, [_el("/#caption/span.cg:0/span.cw:0", "cw", 3.0 * i, 0.0, tag="span", depth=2)])
              for i, t in enumerate([0.0, 0.5])]
    folded = mme.accumulate(frames, fps, [("s01", 0.0, 1.0)])
    report = mme.build_report(Path("b"), {"scenes": [{"scene_id": "s01", "span": [0.0, 1.0]}]},
                              folded, fps, 0.0, 1.0, 0.1, 4)
    md = mme.markdown(report)
    assert "## 7. What this measurement cannot see" in md
    assert "Motion inside a `<video>`" in md
    assert "Scenes measuring `E_primary = 0` here: **s01**" in md
    assert "never as \"nothing moved\"" in md


def test_frame_times_are_deterministic_and_inclusive():
    assert mme.frame_times(0.0, 1.0, 5) == [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    assert mme.frame_times(2.0, 2.4, 5) == [2.0, 2.2, 2.4]
    assert mme.frame_times(0.0, 1.0, 15) == mme.frame_times(0.0, 1.0, 15)


def test_ratio_row_compares_against_the_declared_reference():
    row = mme.ratio_row(100.0, 30.0)
    assert row["ratio"] == pytest.approx(0.30)
    assert row["reference"] == mme.SECONDARY_REFERENCE_RATIO == 0.22
    assert row["difference"] == pytest.approx(0.08)
    assert row["over_reference"] is True
    assert mme.ratio_row(100.0, 10.0)["over_reference"] is False
    assert mme.ratio_row(0.0, 10.0)["ratio"] is None


# --------------------------------------------------------------------------- report shape
def _small_report():
    fps = 2.0
    frames = [(t, [_el("/#wA", "world", 10.0 * i, 0.0),
                   _el("/#caption/span.cg:0/span.cw:0", "cw", 3.0 * i, 0.0, tag="span", depth=2)])
              for i, t in enumerate([0.0, 0.5, 1.0, 1.5])]
    folded = mme.accumulate(frames, fps, WINDOWS)
    timeline = {"episode_id": "unit-test", "aspect": "9:16",
                "scenes": [{"scene_id": "s01", "span": [0.0, 1.0]},
                           {"scene_id": "s02", "span": [1.0, 2.0]}]}
    return mme.build_report(Path("build-x"), timeline, folded, fps, 0.0, 2.0, 1.25, 4)


def test_report_carries_the_three_granularities_and_the_reference():
    report = _small_report()
    assert set(report) >= {"whole_screen", "scenes", "pieces", "reference_ratio",
                           "classification_table", "unclassified", "fps", "frames", "elapsed_s"}
    assert report["reference_ratio"] == 0.22
    assert "47-FINDINGS-TO-CHECKS" in report["reference_source"]
    assert [s["scene_id"] for s in report["scenes"]] == ["s01", "s02"]
    assert report["whole_screen"]["ratio"] == pytest.approx(0.09)
    assert report["pieces"][0]["key"] == "/#wA", "pieces sort by translation energy, heaviest first"
    assert report["unclassified"] == []
    assert json.loads(json.dumps(report))["fps"] == 2.0, "the report must be JSON-serialisable"


def test_markdown_has_the_three_tables_the_read_and_the_declared_table():
    md = mme.markdown(_small_report())
    for heading in ("## 1. Whole screen", "## 2. Per scene", "## 3. Per piece",
                    "## 4. The read", "## 5. Classification table", "## 6. Unclassified"):
        assert heading in md, f"the report is missing {heading}"
    assert "| scene | span (s) | E_primary | E_secondary | ratio | vs 0.22 | movers mean/max |" in md
    assert "s01" in md and "s02" in md
    assert "`/#wA`" in md
    assert "0.22 reference" in md
    assert "None - every element" in md


def test_markdown_names_the_scenes_that_exceed_the_reference():
    fps = 2.0
    frames = [(t, [_el("/#wA", "world", 10.0 * i, 0.0),
                   _el("/#caption", "stage phrase onpage", 8.0 * i, 0.0)])
              for i, t in enumerate([0.0, 0.5])]
    folded = mme.accumulate(frames, fps, WINDOWS)
    report = mme.build_report(Path("b"), {"scenes": [{"scene_id": "s01", "span": [0.0, 1.0]}]},
                              folded, fps, 0.0, 1.0, 0.1, 4)
    assert report["scenes"][0]["over_reference"] is True
    assert "OVER" in mme.markdown(report)
    assert "s01 (0.640)" in mme.markdown(report)


# --------------------------------------------------------------------------- headless smoke test
def _playwright_ready() -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as pw:
            return Path(pw.chromium.executable_path).exists()
    except Exception:
        return False


@pytest.mark.skipif(not TOKYO_SHORT.exists(), reason="the Tokyo short build is not on disk")
@pytest.mark.skipif(not _playwright_ready(), reason="Playwright/Chromium unavailable")
def test_headless_sampling_returns_stage_elements_smoke():
    frames = mme.sample_build(TOKYO_SHORT, fps=5, t_from=25.0, t_to=25.4)
    assert [t for t, _ in frames] == [25.0, 25.2, 25.4]
    keys = {el["key"] for _, elements in frames for el in elements}
    assert any(k.startswith("/#wA") or k.startswith("/#wB") for k in keys)
    assert "/#caption" in keys
    labels = {mme.classify(el["cls"], el["key"])[0] for _, elements in frames for el in elements}
    assert mme.UNCLASSIFIED not in labels, "the live DOM produced a class the table does not cover"
    assert {mme.PRIMARY, mme.SECONDARY} <= labels

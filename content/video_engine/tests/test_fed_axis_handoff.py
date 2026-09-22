"""R26-222: a y-only rescale keeps one x-axis hand-over, not two copies.

The regression is intentionally served through the real scene-evidence player.
The compiler owns the two page states; the player owns the hand-over clock.
"""
from __future__ import annotations

import json
import math
import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

EP = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
PLATE = "ledger:ev-japan-holdings-v1:line"
AT, DUR = 11.0, 1.4
Y_DOMAIN = [0, 1600]
X_WINDOW = [2025.9, 2026.6]
ASPECT_CASES = [
    pytest.param("9:16", id="portrait"),
    pytest.param("16:9", id="landscape_full_stage"),
]

needs_objects = pytest.mark.skipif(
    not (EP / "evidence/objects/ev-japan-holdings-v1.series.json").exists(),
    reason="the Tokyo evidence object is not on disk",
)


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


AXIS_PROBE = r"""() => {
  const st = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')).__lp;
  const states = st.states || [st];
  const opacity = (e) => { const v = parseFloat(e && e.style.opacity); return Number.isFinite(v) ? v : 1; };
  const chartOpacity = (s) => { const v = parseFloat(s.chart && s.chart.style.opacity); return Number.isFinite(v) ? v : 1; };
  const ticks = (s, si) => (s.marks || []).filter(m => m.role === 'xtick').map(m => {
    const x = parseFloat(m.el.getAttribute('x') || 'NaN');
    const y = parseFloat(m.el.getAttribute('y') || 'NaN');
    const o = chartOpacity(s) * opacity(m.el);
    return { si, text: m.el.textContent || '', x, y, opacity: o, shown: o > 0.01 };
  });
  const all = states.flatMap((s, si) => ticks(s, si));
  const visible = all.filter(m => m.shown);
  const duplicatePairs = [];
  for (let i = 0; i < visible.length; i++) for (let j = i + 1; j < visible.length; j++) {
    const a = visible[i], b = visible[j];
    if (a.si !== b.si && a.text === b.text && Math.abs(a.x - b.x) < 0.5)
      duplicatePairs.push({ text: a.text, x: a.x, states: [a.si, b.si] });
  }
  return { active: st.active | 0, xf: st.xfNow || null, ticks: all, visible, duplicatePairs,
           stateCharts: states.map(s => chartOpacity(s)) };
}"""


def _assert_finite_tick_geometry(sample: dict) -> None:
    """Every sampled axis mark remains measurable, including hidden hand-over twins."""
    for tick in sample["ticks"]:
        assert isinstance(tick["si"], int) and tick["si"] in (0, 1), tick
        assert math.isfinite(tick["x"]) and math.isfinite(tick["y"]), tick
        assert math.isfinite(tick["opacity"]), tick


def _timeline_player(*, window: list[float] | None, aspect: str, relabel: bool = False):
    from playwright.sync_api import sync_playwright

    tl, uris, _text, _audio = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(PLATE, (0, 0, 0), EP)
    species = [{"kind": "chart_to", "at": AT, "dur": DUR, "to": "rescale"}]
    if window is None:
        species[0].update({"ymin": Y_DOMAIN[0], "ymax": Y_DOMAIN[1]})
    else:
        species[0]["window"] = window
    B.derive_rescale_states(world, species, PLATE, EP)
    if aspect == "16:9":
        # R26-205's existing compiler contract is a page stamp, not a new state shape. The
        # hand-over must carry it on both the standing page and the derived target before the
        # player reads either state, so this is an actual full-stage render rather than a
        # landscape viewport around the legacy page.
        pages = [world.get("page") or {}] + list(world.get("page_states") or [])
        for page in pages:
            B.stamp_full_stage(page)
        assert pages and all(page.get("full_stage") is True for page in pages)
    if relabel:
        target_ticks = world["page_states"][0]["axes"]["xticks"]
        world["page_states"][0]["axes"]["xticks"] = [[x, f"FY {label}"] for x, label in target_ticks]
    scene = dict(tl["scenes"][0], species=species, span=[0.0, 24.0],
                 world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect=aspect, runtime_s=24.0, scenes=[scene], caption_pages=[], captions=[])
    td = tempfile.TemporaryDirectory()
    aspect_slug = aspect.replace(":", "x")
    base_stem = "y-only-relabel" if relabel else ("y-only" if window is None else "x-window")
    stem = f"{aspect_slug}-{base_stem}"
    html = Path(td.name) / f"{stem}.html"
    html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    w, h = RB.STAGE[aspect]
    srv, port = RB.serve(html.parent)
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    page = br.new_context(viewport={"width": w, "height": h}).new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, w, h)

    proof_dir = ROOT / ".context/fed-t14-proof"
    write_proof = os.environ.get("FED_T14_PROOF") == "1"
    if write_proof:
        proof_dir.mkdir(parents=True, exist_ok=True)

    def at(t: float, label: str | None = None) -> dict:
        page.evaluate(
            "t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }",
            t,
        )
        result = page.evaluate(AXIS_PROBE)
        if write_proof and label:
            result["time"] = t
            (proof_dir / f"{html.stem}-{label}.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            page.screenshot(path=str(proof_dir / f"{html.stem}-{label}.png"), full_page=True)
        return result

    def close():
        br.close()
        pw.stop()
        srv.shutdown()
        td.cleanup()

    return at, errors, close


def _assert_reverse_seek(at, *, y_only: bool):
    before = at(AT - 0.5, "before")
    mid = at(AT + DUR * 0.5, "mid")
    after = at(AT + DUR + 0.3, "after")
    for sample in (before, mid, after):
        _assert_finite_tick_geometry(sample)
    # A cold seek back through the transition must reproduce the exact geometry.
    at(AT - 0.5, "rewind-before")
    reverse = at(AT + DUR * 0.5, "reverse-mid")
    _assert_finite_tick_geometry(reverse)
    assert reverse == mid, "reverse seeking must reproduce the same hand-over geometry"
    assert before["active"] == 0 and after["active"] == 1
    assert before["duplicatePairs"] == [] and after["duplicatePairs"] == []
    if y_only:
        assert mid["duplicatePairs"] == [], mid
        assert not any(t["si"] == 1 and t["shown"] for t in mid["visible"]), mid
        assert {t["text"] for t in mid["visible"] if t["si"] == 0} == {t["text"] for t in before["visible"] if t["si"] == 0}
        assert {t["text"] for t in after["visible"] if t["si"] == 1} == {t["text"] for t in before["visible"] if t["si"] == 0}
    else:
        assert mid["duplicatePairs"] == [], mid
        assert {tick["text"] for tick in mid["visible"]} != {tick["text"] for tick in before["visible"]}


@needs_objects
@needs_browser
@pytest.mark.parametrize("aspect", ASPECT_CASES)
def test_y_only_rescale_hands_unchanged_x_ticks_once_before_mid_after_and_reverse_seek(aspect):
    at, errors, close = _timeline_player(window=None, aspect=aspect)
    try:
        _assert_reverse_seek(at, y_only=True)
        assert not errors, errors
    finally:
        close()


@needs_objects
@needs_browser
@pytest.mark.parametrize("aspect", ASPECT_CASES)
def test_changed_x_domain_keeps_the_existing_tick_handover_and_reverse_seek(aspect):
    at, errors, close = _timeline_player(window=X_WINDOW, aspect=aspect)
    try:
        _assert_reverse_seek(at, y_only=False)
        assert not errors, errors
    finally:
        close()


@needs_objects
@needs_browser
@pytest.mark.parametrize("aspect", ASPECT_CASES)
def test_relabelled_same_coordinate_ticks_are_not_treated_as_unchanged(aspect):
    at, errors, close = _timeline_player(window=None, aspect=aspect, relabel=True)
    try:
        before = at(AT - 0.5, "before")
        mid = at(AT + DUR * 0.5, "mid")
        after = at(AT + DUR + 0.3, "after")
        for sample in (before, mid, after):
            _assert_finite_tick_geometry(sample)
        assert mid["duplicatePairs"] == [], mid
        source = {t["text"] for t in mid["visible"] if t["si"] == 0}
        target = {t["text"] for t in mid["visible"] if t["si"] == 1}
        assert target and source.isdisjoint(target), mid
        assert {t["text"] for t in after["visible"] if t["si"] == 1} != {t["text"] for t in before["visible"] if t["si"] == 0}
        at(AT - 0.5, "rewind-before")
        reverse = at(AT + DUR * 0.5, "reverse-mid")
        _assert_finite_tick_geometry(reverse)
        assert reverse == mid
        assert not errors, errors
    finally:
        close()

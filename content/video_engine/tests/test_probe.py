"""P51 T2 - the probe: the agent's eyes are numbers. The built Tokyo short, read from its own DOM at the
instants that matter (the fingers land beside the parked chart, the record parks beside the parked bars,
the burst), and the arithmetic the layout gate stands on - overlap area, cover, the phone scale.

The JSON for one instant is the contract: under 2 KB, so an agent can look at forty instants for the price
of one frame."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import probe as P  # noqa: E402

BUILD = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short"
TOKYO_TL = "tokyo-short.timeline.json"
UNPARKED, PARKED = 30.0, 58.6   # the line chart holding the page; the bar state parked beside two cards (E60)
JSON_MAX_B = 2048               # the acceptance: one instant costs a fraction of a frame


def _browser_ok() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="playwright chromium not installed")
needs_tokyo = pytest.mark.skipif(not (BUILD / "player.html").exists(), reason="the Tokyo short build is not on disk")
# R26-53's two sides: the APPROVED build (no lpFitValues) and the side build that carries the fit
VALS = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short-vals"
needs_vals = pytest.mark.skipif(not (VALS / "player.html").exists(), reason="the Tokyo values side build is not on disk")
META_FIXED, META_APPROVED = 70.0, 71.0     # the Meta page held on each build


def _in_its_own_thread(build: Path, t: float) -> dict:
    """One instant of a SECOND build. Playwright's sync API allows one running loop per thread and the
    module-scoped `tokyo` Probe owns this one, so the second player is read on a thread of its own."""
    import threading
    out: dict = {}

    def run() -> None:
        try:
            with P.Probe(build) as p:
                out["inst"] = p.at(t, "the second build")
        except BaseException as e:        # noqa: BLE001 - re-raised on the calling thread below
            out["err"] = e

    th = threading.Thread(target=run)
    th.start()
    th.join()
    if "err" in out:
        raise out["err"]
    return out["inst"]


@pytest.fixture(scope="module")
def tokyo():
    p = P.Probe(BUILD, TOKYO_TL)
    try:
        yield p
    finally:
        p.close()


# ---- the arithmetic (no browser) --------------------------------------------------------------------------------

def test_the_box_arithmetic_is_exact():
    a, b = [0, 0, 100, 100], [50, 50, 100, 100]
    assert P.intersect_px(a, b) == 2500 and P.intersect_px(a, [200, 0, 10, 10]) == 0
    assert P.gap_px(a, [150, 0, 10, 10]) == 50 and P.gap_px(a, b) == -50
    assert P.moved_px([0, 0, 10, 10], [3, 0, 10, 10]) == 3 and P.moved_px([0, 0, 10, 10], None) == 0
    # the data is many little boxes; two of them over one pixel count once
    assert P.cover_px([0, 0, 64, 64], [[0, 0, 32, 32], [0, 0, 32, 32]]) == 32 * 32
    assert P.cover_px([0, 0, 64, 64], []) == 0


def test_the_phone_scale_is_the_one_doc_49_states():
    # doc 49 s49.1: 12 CSS px on a 390 px phone IS 34 px on the 1080-wide stage
    assert round(P.phone_css(34, "9:16"), 1) == 12.3
    assert round(P.phone_css(59, "9:16"), 1) == 21.3     # primary text
    assert P.phone_css(1920, "16:9") == P.PHONE_CSS["16:9"]


@needs_tokyo
def test_the_gate_s_instants_are_the_landings_the_onsets_and_every_dock_s_life():
    tl = json.loads((BUILD / TOKYO_TL).read_text(encoding="utf-8"))
    inst = P.gate_instants(tl)
    ts = [t for t, _w in inst]
    assert ts == sorted(ts) and len(ts) == len(set(ts)) and all(0 <= t < tl["runtime_s"] for t in ts)
    why = {w for _t, w in inst}
    assert any("the chart's landing" in w for w in why) and any("chart_to park end" in w for w in why)
    # every dock's enter, its reading size and the box it parks in are all probed (two instants can land
    # in one 0.02 s slot - a spring arrival IS its enter - and the first name to claim the slot keeps it)
    for nm, enter, read_s, park_s in (("dock-k-pledge-record", 55.31, 1.41, 0.7), ("dock-i-fab-wafer", 56.72, 1.2, 0.7)):
        for want in (enter, enter + read_s, enter + read_s + park_s):
            assert any(abs(t - want) < 0.1 for t in ts), (nm, want)
    assert any(f"dock {nm} reading size" in w for nm in ("dock-i-fab-wafer",) for _t, w in inst)
    assert any(f"dock {nm} parked" in w for nm in ("dock-i-fab-wafer",) for _t, w in inst)


# ---- the probe on the built short -------------------------------------------------------------------------------

@needs_browser
@needs_tokyo
def test_the_burst_reads_two_parked_cards_a_page_and_a_camera(tokyo):
    """0:58.6 - E60's burst: the record parked top right, the fab card beneath, the bar state parked beside them."""
    inst = tokyo.at(PARKED, "the burst")
    assert {d["id"] for d in inst["docks"]} == {"dock-i-fab-wafer", "dock-k-pledge-record"}
    assert all(d["state"] == "parked" and d["rest"] == 1 for d in inst["docks"]), inst["docks"]
    assert all(len(d["box"]) == 4 and all(isinstance(v, int) for v in d["box"]) for d in inst["docks"])
    for k in ("title", "sub", "source", "plot", "data", "chart"):
        assert k in inst["page"], (k, inst["page"])
    assert isinstance(inst["overlaps"], list) and not [o for o in inst["overlaps"] if o["b"] == "page.data"]
    assert inst["camera"]["scene"] == "s04" and inst["camera"]["zoom"] == 1.0
    assert inst["caption"]["mode"] == "anchor" and inst["caption"]["text"]
    assert inst["clearances"]["caption_px"] > 0, "no card is in the strip"
    assert inst["marks"]["n"] > 0 and inst["marks"]["parked"] is True
    assert {x["k"] for x in inst["texts"]} >= {"title", "sub", "source", "caption"}


@needs_browser
@needs_tokyo
def test_one_instant_of_json_is_under_two_kilobytes(tokyo):
    for t in (9.2, 36.7, 54.5, 57.0, PARKED):
        inst = tokyo.at(t)
        n = len(json.dumps(inst, separators=(",", ":")).encode("utf-8"))
        assert n < JSON_MAX_B, (t, n)
        assert "data:image" not in json.dumps(inst)
        assert all(len(x.get("txt", "")) <= 40 for x in inst["texts"] if isinstance(x, dict))


@needs_browser
@needs_tokyo
def test_a_parked_chart_is_measured_as_it_is_DRAWN(tokyo):
    """The park is a transform: the layout box never moves, so a probe that read the layout would miss the
    defect the park exists to fix. Read on screen, the parked plot is a fraction of the standing one."""
    up = tokyo.at(UNPARKED, "the line chart holding the page")
    down = tokyo.at(PARKED, "parked to 0.52 beside the cards")
    a_up = up["page"]["plot"][2] * up["page"]["plot"][3]
    a_down = down["page"]["plot"][2] * down["page"]["plot"][3]
    assert a_down < a_up * 0.6, (up["page"]["plot"], down["page"]["plot"])
    assert up["marks"]["parked"] is False and down["marks"]["parked"] is True
    # ... and the citation rides it down (E52), which is why the type floor exempts a parked run
    src_up = next(x for x in up["texts"] if x["k"] == "source")
    src_down = next(x for x in down["texts"] if x["k"] == "source")
    assert src_down["px"] < src_up["px"] and src_down.get("pk") == 1 and not src_up.get("pk")


@needs_browser
@needs_tokyo
def test_a_seek_is_the_play_for_the_probe_too(tokyo):
    """The boxes at t must not depend on where the probe looked before. Both worlds can hold a page at
    once and the player's own `__lp` can point at the one underneath - so the probe reads the DOM."""
    cold = tokyo.at(PARKED)
    tokyo.at(UNPARKED)
    again = tokyo.at(PARKED)
    assert again["page"] == cold["page"] and again["docks"] == cold["docks"], (cold["page"], again["page"])


@needs_browser
@needs_tokyo
@needs_vals
def test_the_page_s_own_labels_are_boxes_and_the_value_row_s_air_is_measured(tokyo):
    """R26-53, both sides of it. M28 needs one thing from the probe: every label the page draws, as a box
    with a role, so two numbers sitting on each other are a NAMED pair. The Tokyo Meta page is the case -
    four values and the callout's pill on bar 4 - and the two builds answer differently:

      build-short-vals (lpFitValues / lpPillBand): values 122 px wide, 33 px between neighbours, the pill
        risen to its band 50 px clear of "$604"
      build-short (the approved cut, no fit): values 133 px wide, 23 px between neighbours, the pill 7 px
        off "$604" - the boxes CLEAR each other and the frame reads "$604$577"

    So the defect is the fit's own air, not an intersection: neither build has a label pair in `overlaps`,
    and M28 carries a WARN tier under its FAIL for exactly this frame."""
    def air(inst):
        """(half a figure at the page's value size, the labels by name)"""
        vpx = next(x["px"] for x in inst["texts"] if x["k"] == "chart.val")
        return 0.28 * vpx, {P.label_key(x): x["box"] for x in inst["labels"]}

    fixed = _in_its_own_thread(VALS, META_FIXED)
    approved = tokyo.at(META_APPROVED, "the Meta page as the operator watched it")
    for inst in (fixed, approved):
        assert {"val:$665", "val:$633", "val:$604", "pill:$577"} <= {P.label_key(x) for x in inst["labels"]}, inst["labels"]
        assert all(isinstance(v, int) for x in inst["labels"] for v in x["box"])
        # nothing TOUCHES on either build - the four values and the pill keep their boxes apart
        assert not [o for o in inst["overlaps"] if ":" in o["a"] and ":" in o["b"]], inst["overlaps"]

    half, lab = air(fixed)
    assert P.gap_px(lab["val:$604"], lab["pill:$577"]) > half, "the risen pill is clear of the value row"
    assert P.gap_px(lab["val:$665"], lab["val:$633"]) >= 2 * half, "a figure of air between neighbours"

    half, lab = air(approved)
    assert 0 < P.gap_px(lab["val:$604"], lab["pill:$577"]) < half, "the pill stands inside the value's own air"
    assert P.gap_px(lab["val:$665"], lab["val:$633"]) < 2 * half, "and the row itself is fitted too tight"


@needs_browser
def test_the_data_read_takes_a_treemap_s_tiles():
    """A treemap's tiles carry no class of their own (`g.lp-cell > rect`), so the DATA read names them by
    their cell. Before it did, the census page answered `page.data` None and `marks.n` 0 - a card parked
    over the whole treemap read as parked on nothing, and M25 / M27 had nothing to refuse."""
    import tempfile

    import render_baseline as RB

    assert "g.lp-cell rect" in P.READ_DOM
    tl, uris, t, _aspect = RB.load_surface("treemap-cross")
    with tempfile.TemporaryDirectory() as td:
        RB.write_split(Path(td), tl, uris, "treemap-cross.timeline.json")
        inst = _in_its_own_thread(Path(td), t)
    plot, data = inst["page"]["plot"], inst["page"]["data"]
    assert inst["marks"]["n"] >= 6, inst["marks"]            # one mark per tile
    assert P.intersect_px(data, plot) > 0.9 * plot[2] * plot[3], (data, plot)   # the tiles ARE the plot


@needs_browser
@needs_tokyo
def test_the_fingers_land_beside_the_parked_chart_and_touch_nothing(tokyo):
    """0:36.7 - the composition the park exists for: the card in the page's free space, the chart shrunk to
    its left, no overlap between them."""
    inst = tokyo.at(36.7, "the fingers land")
    assert [d["id"] for d in inst["docks"]] == ["dock-g-two-fingers"]
    assert not [o for o in inst["overlaps"] if o["b"] in ("page.data", "caption")], inst["overlaps"]

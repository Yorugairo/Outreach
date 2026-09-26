"""P70 T1b (E99 s121): A SEAL-TYPE STAMP IS A SEAL - the solid border, ring text on two half-arcs, the shockwave from the
impact frame, the ink easing back.

The operator, 2026-09-24, beside remotion-ui's badge stamp (its source on disk:
content/video_engine/remotion-ui/src/remotion/primitives/badge-stamp.tsx): "i think if we look at what a stamp actually
was in the references, the stamp needs to have a solid border" - and, asked which stamps take it, SEAL-TYPE STAMPS ONLY.
The painter's half (the rings, the arcs, the ink, the shockwave's clock) is pinned by tests/kinetics/chip.test.mjs and
tests/kinetics/stopaction-stamp.test.mjs. What this file pins:

  (1) the grammar: `ring_text` / `ring_text_bottom` are a STAMPED chip's (the stamp form landing by the stamp arrival);
      anywhere else they are refused by name, and a dock stamp asking for a seal is refused naming s87 / s121 - a bare
      prop stays bare, and a dock's verdict is a chart card's tile (P71 T19), never a seal (P72 T46b, R26-391 (b));
  (2) the seal is the room the AUTHORED mark reserves (`seal_r`) and the art GROWS to fill it by its painted pixels
      (THE MARK TAKES THE ROOM); the fit's ring and approach are read round the SEAL, where the impact ring is thrown from;
  (3) ring text is drawn at the SOURCE's proportion and never widens the seal - under the s90 floor a WARN with numbers;
      a line that runs past the side of the ring is a WARN with its numbers and is not drawn (s106) - never clipped;
  (4) the seal is GOLD (E99 s123), darkened on the cream until it holds 3:1;
  (5) the dials the compiler mirrors are chip.mjs's;
  (6) measured on the rendered frame: zero shockwave ink before the contact, on a dock stamp and on a stamped chip;
  (7) a seal does not squash;
  (8) P70 T1c (E99 s127 / s128), measured on the frame: a SEAL's shockwave is the seal's gold; a BARE PROP's ring
      picks chalk or charcoal by the measured ground under it and holds contrast on cream, the charcoal ledger, a
      charcoal plate and a photo plate; the seal is OPEN - the chart shows through it.
"""
from __future__ import annotations

import io
import json
import math
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as MG  # noqa: E402

CHIP_MJS = ROOT / "content/video_engine/scripts/species/chip.mjs"
PLATE, STILL = "world-spike-desk-v1", (0, 0, 0)
GPU = "prop-icon-gpu-ai-accelerator-v1"
CONTACT = MG.STAMP_CONTACT_S


def _stamp(**extra) -> dict:
    return {"kind": "chip", "form": "stamp", "at": 10.0, "dur": 6.0, "icon": GPU, "label": "NVIDIA",
            "target": {"kind": "point", "x": 0.5, "y": 0.5}, **extra}


def _paint() -> dict:
    return B.painted_box(B.catalogue_stamp_asset(GPU)["file"])


# ---- (1) the grammar ----------------------------------------------------------------------------------------------


def test_ring_text_is_a_STAMPED_chips_and_either_arc_is_optional():
    for extra in ({}, {"ring_text": "AI ACCELERATOR"}, {"ring_text_bottom": "GPU"},
                  {"ring_text": "AI ACCELERATOR", "ring_text_bottom": "GPU"}):
        assert B.validate_species([_stamp(arrive="stamp", **extra)], STILL, PLATE) == [], extra
    assert B.CHIP_SEAL_OPTS == ("ring_text", "ring_text_bottom")


@pytest.mark.parametrize("entry", [
    _stamp(ring_text="GPU"),                                                    # the stamp FORM on its spring
    {"kind": "chip", "at": 10.0, "dur": 6.0, "icon": "cpu", "label": "NVIDIA",  # a glyph chip
     "target": {"kind": "point", "x": 0.5, "y": 0.5}, "ring_text_bottom": "GPU"},
])
def test_ring_text_anywhere_else_is_REFUSED_by_name_citing_s121(entry):
    errs = B.validate_species([entry], STILL, PLATE)
    assert any("ring text is a seal's" in e and "E99 s121" in e for e in errs), errs


@pytest.mark.parametrize("value", ["", "   ", "TWO\nLINES", 7, None, True])
def test_ring_text_is_ONE_short_line_of_text(value):
    errs = B.validate_species([_stamp(arrive="stamp", ring_text=value)], STILL, PLATE)
    assert any("ring_text must be one line of text" in e and "s113" in e for e in errs), errs


@pytest.mark.parametrize("key", ["ring_text", "ring_text_bottom", "seal"])
@pytest.mark.parametrize("prop", [True, False])
def test_a_DOCK_stamp_asking_for_a_seal_is_REFUSED_by_name_citing_s87_and_s121(key, prop):
    opts = {"arrive": "stamp", "mass": "ink", key: "AUDITED" if key != "seal" else True}
    if prop:
        opts["prop"] = True
    with pytest.raises(ValueError) as exc:
        B.dock_opts(opts)
    msg = str(exc.value)
    assert f"dock option {key!r}" in msg and "E99 s87" in msg and "E99 s121" in msg, msg
    assert "a bare prop stays bare" in msg and "a chart card's `verdict` tile (P71 T19)" in msg, msg


# ---- (2) the seal is the room the authored mark reserves, and the mark grows to fill it -----------------------------


def _fit(entry: dict, world: dict | None = None, where: str = "chip stamp") -> tuple[dict, list[str]]:
    return B.chip_stamp_ring_fit(entry, world or {"asset_id": "plate-plain"}, "16:9", _paint(), where=where)


def test_the_seal_is_the_room_the_AUTHORED_mark_reserves_by_the_sources_own_ratios():
    e = _stamp(arrive="stamp")
    art = B.chip_stamp_art(e, "16:9", _paint())
    rc = 0.5 * math.hypot(*art["painted"])
    R = B.chip_stamp_seal_r(art)
    assert R == pytest.approx((rc + B.STAMP_RING_GAP_PX) * 50 / 44, abs=0.05), "the inner ring (r - 6 of 50) 12 px outside"
    out, _notes = _fit(e)
    assert out["seal_r"] == R
    seal = B.chip_stamp_seal(out, R)
    assert seal["r_in"] == pytest.approx(R * 44 / 50) and seal["size"] == pytest.approx(R * 7.4 / 50)
    assert seal["top_r"] == pytest.approx(R * 38 / 50) and seal["bottom_r"] == pytest.approx(R * 36 / 50)
    assert seal["bottom_dy"] == pytest.approx(R * 6.4 / 50) and seal["track"] == pytest.approx(R * 1.6 / 50)


def test_ring_text_NEVER_widens_the_seal():
    plain, _ = _fit(_stamp(arrive="stamp"))
    text, _ = _fit(_stamp(arrive="stamp", ring_text="AI ACCELERATOR", ring_text_bottom="GPU"))
    assert text["seal_r"] == plain["seal_r"], "the seal is the size it would be without text (the parent's fix 2)"


def test_THE_MARK_TAKES_THE_ROOM_the_art_grows_by_its_painted_pixels_to_the_seals_inner_ring():
    """The operator (2026-09-24): "if we're already reserving space for a thing, we should make the thing bigger within
    that space" - CAPABILITIES :79's rule, measured by the PAINTED pixels (the alpha), not the file's box."""
    e = _stamp(arrive="stamp")
    out, notes = _fit(e)
    seal = B.chip_stamp_seal(out, out["seal_r"])
    rim = B._alpha_rim(B.catalogue_stamp_asset(GPU)["file"])
    assert out["size"] > e.get("size", B.STAMP_SIZE_DEFAULT) * 1.2, f"the art grows: {out['size']} px from 260"
    reach = B.chip_seal_reach(out, "16:9", _paint(), rim, out["size"])
    assert reach <= seal["content_r"] + 1e-6, "every painted pixel and the name inside the inner ring by the gap"
    assert B.chip_seal_reach(out, "16:9", _paint(), rim, out["size"] + 0.5) > seal["content_r"], "... and no larger"
    assert e.get("size") is None, "the authored entry is never mutated"


def test_under_ring_text_the_mark_fits_INSIDE_the_texts_band():
    out, _ = _fit(_stamp(arrive="stamp", ring_text="AI ACCELERATOR", ring_text_bottom="GPU"))
    seal = B.chip_stamp_seal(out, out["seal_r"])
    rim = B._alpha_rim(B.catalogue_stamp_asset(GPU)["file"])
    band = min(seal["top_r"] - B.CHIP_SEAL_TEXT_DESC_EM * seal["size"],
               seal["bottom_r"] + seal["bottom_dy"] - B.CHIP_SEAL_TEXT_ASC_EM * seal["size"])
    assert seal["content_r"] == pytest.approx(band - B.CHIP_SEAL_GAP_PX)
    assert B.chip_seal_reach(out, "16:9", _paint(), rim, out["size"]) <= seal["content_r"] + 1e-6


def test_the_fit_reads_the_SEAL_at_the_grown_marks_centre():
    e = _stamp(arrive="stamp", size=180, target={"kind": "point", "x": 0.5, "y": 0.5})
    out, notes = _fit(e)
    art = B.chip_stamp_art(out, "16:9", _paint())
    (cx, cy), R = art["centre"], out["seal_r"]
    band = B.FRAME_BANDS["16:9"]["caption"]
    safe = B.FRAME_BANDS["16:9"]["safe"]
    clear = B.disc_clearance(cx, cy, [band], safe)
    assert out["ring_to"] == pytest.approx(min(B.STAMP_RING_TO, (clear - B.STAMP_RING_W_PX) / R), abs=1e-2)
    assert out["ring_to"] * R + B.STAMP_RING_W_PX <= clear + 1.0, "the impact ring's peak, round the seal, clears the room"
    assert out["from_to"] * R <= min(cy - safe["y"], band["y"] - cy) + 1.0, "the whole seal clears on the way down"
    assert notes == []


def test_where_the_seal_cannot_clear_its_floor_is_the_seals_and_it_is_a_WARN_never_a_refusal():
    e = _stamp(arrive="stamp", target={"kind": "point", "x": 0.5, "y": 0.86})
    out, notes = _fit(e, where="row 7 chip")
    R = out["seal_r"]
    assert any("the ring is drawn at its floor" in n for n in notes), notes
    assert all(n.startswith("row 7 chip (mark and label ") and f"seal of radius {R:.0f} px" in n
               for n in notes if "floor (" in n), notes
    assert out["ring_to"] == pytest.approx((R + B.STAMP_RING_GAP_PX) / R, abs=2e-3)


# ---- (3) ring text: its half-arc, the source's proportion, the s90 floor ------------------------------------------


def test_ring_text_that_fits_its_half_arc_is_kept_and_its_advance_is_the_measured_face():
    e = _stamp(arrive="stamp", ring_text="AI ACCELERATOR", ring_text_bottom="GPU")
    out, notes = _fit(e)
    assert out["ring_text"] == "AI ACCELERATOR" and out["ring_text_bottom"] == "GPU"
    assert not any("runs past the side" in n for n in notes), notes
    size, track = 36.0, 8.0
    want = sum(B.CHIP_STAMP_LABEL_ADVANCE_EM[c] for c in "GPU") * size + 2 * track
    assert B.chip_seal_text_advance("GPU", size, track) == pytest.approx(want), "the tracking sits BETWEEN glyphs"


def test_ring_text_is_drawn_at_the_SOURCES_proportion_and_under_the_s90_floor_that_is_a_WARN_with_numbers():
    out, notes = _fit(_stamp(arrive="stamp", ring_text="AI ACCELERATOR"), where="row 7 chip")
    R = out["seal_r"]
    size = R * 7.4 / 50
    assert size < B.CHIP_STAMP_LABEL_FLOOR
    hit = [n for n in notes if "under the E99 s90 phone floor" in n]
    assert len(hit) == 1, notes
    assert f"{size:.1f} px" in hit[0] and f"radius {R:.0f} px" in hit[0] and "59.08 px" in hit[0], hit[0]
    need = B.CHIP_STAMP_LABEL_FLOOR * 50 / 7.4
    assert f"{need:.0f} px or more" in hit[0] and "drawn at the seal's proportion" in hit[0] and "s106" in hit[0]
    assert out["ring_text"] == "AI ACCELERATOR", "advised, never dropped for its size"
    plain, plain_notes = _fit(_stamp(arrive="stamp"))
    assert not any("s90 phone floor" in n for n in plain_notes), "no ring text, no size advice"


def test_ring_text_that_RUNS_PAST_THE_SIDE_is_a_WARN_with_its_numbers_and_is_not_drawn():
    long_top = "THE LARGEST MAKER OF AI ACCELERATORS AND GRAPHICS"
    e = _stamp(arrive="stamp", size=180, ring_text=long_top, ring_text_bottom="GPU")
    out, notes = _fit(e, where="row 7 chip")
    assert "ring_text" not in out and out["ring_text_bottom"] == "GPU", "dropped, never clipped by the arc's end"
    assert e["ring_text"] == long_top, "the authored entry is never mutated"
    seal = B.chip_stamp_seal(e, out["seal_r"])
    adv = B.chip_seal_text_advance(long_top, seal["size"], seal["track"])
    arc = math.pi * seal["top_r"]
    hit = [n for n in notes if "runs past the side of the ring" in n]
    assert len(hit) == 1 and f"{adv:.0f} px" in hit[0] and f"{arc:.0f} px" in hit[0], notes
    assert "ring_text" in hit[0] and "E99 s121" in hit[0] and "not drawn" in hit[0]
    assert adv > arc


# ---- (4) the gold (E99 s123) ---------------------------------------------------------------------------------------


def test_the_seal_is_GOLD_on_the_dark_ground_and_darkened_on_the_cream_until_it_holds_3_to_1():
    assert B.CHIP_SEAL_GOLD == "#E8B86D", "badge-stamp.tsx:57 `color = \"#E8B86D\"` - the one dial"
    assert B.seal_gold({}) == ("#E8B86D", "#25313C")
    assert B.seal_contrast("#E8B86D", "#25313C") == pytest.approx(7.27, abs=0.01)
    ink, ground = B.seal_gold({"ink": "charcoal"})
    assert (ink, ground) == ("#A07F4B", "#F4E6C7"), "x0.69 of the gold's channels"
    assert B.seal_contrast(ink, ground) >= B.CHIP_SEAL_CONTRAST_MIN > B.seal_contrast("#E8B86D", "#F4E6C7")
    assert B.seal_gold({"ink": "charcoal"}, "#C79E5E")[0] == "#9F7E4B", "the other candidate, the docs' rendered gold"
    for e in (_stamp(arrive="stamp"), _stamp(arrive="stamp", ink="charcoal")):
        _out, notes = _fit(e)
        assert not any("under the 3:1 floor" in n for n in notes), "the darkened gold always reads"


# ---- (5) the mirrors -------------------------------------------------------------------------------------------------


def test_the_compilers_seal_dials_are_chip_mjs_CHIP_SEAL():
    src = CHIP_MJS.read_text(encoding="utf-8")
    block = re.search(r"export const CHIP_SEAL = Object\.freeze\(\{(.*?)\n\}\);", src, re.S)
    assert block, "chip.mjs exports CHIP_SEAL"
    body = block.group(1)

    def num(name: str) -> float:
        m = re.search(rf"\b{name}:\s*([0-9.]+)", body)
        assert m, name
        return float(m.group(1))

    assert (num("SRC_R"), num("INNER_R")) == (B.CHIP_SEAL_SRC_R, B.CHIP_SEAL_INNER_R)
    assert (num("TEXT_SIZE"), num("TEXT_TRACK")) == (B.CHIP_SEAL_TEXT_SIZE, B.CHIP_SEAL_TEXT_TRACK)
    assert (num("TOP_R"), num("BOTTOM_R"), num("BOTTOM_DY")) == (B.CHIP_SEAL_TOP_R, B.CHIP_SEAL_BOTTOM_R, B.CHIP_SEAL_BOTTOM_DY)
    assert num("GAP_PX") == B.CHIP_SEAL_GAP_PX == B.STAMP_RING_GAP_PX
    assert (num("TEXT_ASC_EM"), num("TEXT_DESC_EM")) == (B.CHIP_SEAL_TEXT_ASC_EM, B.CHIP_SEAL_TEXT_DESC_EM)
    assert num("CONTRAST_MIN") == B.CHIP_SEAL_CONTRAST_MIN
    assert re.search(r'GOLD:\s*"(#[0-9A-F]{6})"', body).group(1) == B.CHIP_SEAL_GOLD
    g = re.search(r'dark:\s*"(#[0-9A-F]{6})",\s*light:\s*"(#[0-9A-F]{6})"', body)
    assert g and {"dark": g.group(1), "light": g.group(2)} == B.CHIP_SEAL_GROUND
    adv = re.search(r"ADVANCE_EM: Object\.freeze\(\{(.*?)\}\),", body, re.S).group(1)
    table = {json.loads(k): float(v) for k, v in re.findall(r'("(?:\\.|[^"\\])*"):\s*([0-9.]+)', adv)}
    assert table == B.CHIP_STAMP_LABEL_ADVANCE_EM, "the measured Kalam table, written twice"
    assert num("ADVANCE_MAX_EM") == B.CHIP_STAMP_LABEL_ADVANCE_MAX_EM


# ---- (6) measured on the frame: zero shockwave ink before the contact ------------------------------------------------

_HIDE_RINGS = ".dock-ring, .chipstampring { display: none !important; }"


def _ring_pixels(surface: str, instants: list[float]) -> dict[float, int]:
    """For each instant: how many pixels the IMPACT RING alone puts on the frame - the frame as drawn against the same
    frame with the ring hidden (every other element identical), counted over the whole stage."""
    playwright = pytest.importorskip("playwright.sync_api")
    import numpy as np
    from PIL import Image
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface(surface)
    w, h = RB.STAGE[aspect or "16:9"]
    import tempfile
    out: dict[float, int] = {}
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "ring.html"
        html.write_text(RB.instantiate(tl, uris, RB.TEMPLATE), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with playwright.sync_playwright() as pw:
                try:
                    br = pw.chromium.launch(headless=True)
                except Exception as exc:   # noqa: BLE001 - no browser is a skip with its reason, never a pass
                    pytest.skip(f"playwright chromium not installed: {exc}")
                shots = {}
                for hide in (False, True):
                    page = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
                    page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                    RB.prepare_page(page, w, h)
                    if hide:
                        page.add_style_tag(content=_HIDE_RINGS)
                    for t in instants:
                        RB.frame_png(page, t, (w, h))
                        page.wait_for_timeout(120)
                        shots[(hide, t)] = np.asarray(Image.open(io.BytesIO(RB.frame_png(page, t, (w, h)))).convert("RGB"))
                    page.close()
                br.close()
        finally:
            srv.shutdown()
    for t in instants:
        out[t] = int((np.abs(shots[(False, t)].astype(int) - shots[(True, t)].astype(int)).max(axis=2) > 2).sum())
    return out


@pytest.mark.parametrize("surface,enter", [("prop-stamp", 10.0), ("chip-stamp-arrival", 10.0)])
def test_ZERO_shockwave_ink_before_the_contact_on_the_frame(surface, enter):
    before = [round(enter + CONTACT + d, 4) for d in (-0.10, -0.05, -0.01)]
    after = [round(enter + CONTACT + d, 4) for d in (0.05, 0.15)]
    px = _ring_pixels(surface, before + after)
    assert all(px[t] == 0 for t in before), f"{surface}: ring pixels before the contact {px}"
    assert all(px[t] > 500 for t in after), f"{surface}: the ring is out after the contact {px}"

# ---- (7) measured on the frame: a SEAL does not squash (the parent's round-3 change) ----------------------------------

def _seal_boxes(surface: str, instants: list[float]) -> dict[float, tuple[float, float]]:
    """For each instant: the drawn width and height of the seal's OUTER ring (its client box on the stage). A round
    seal, however it is turned, has a square box; the hit's squash frame makes it an oval (w != h)."""
    playwright = pytest.importorskip("playwright.sync_api")
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface(surface)
    w, h = RB.STAGE[aspect or "16:9"]
    import tempfile
    out: dict[float, tuple[float, float]] = {}
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "seal.html"
        html.write_text(RB.instantiate(tl, uris, RB.TEMPLATE), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with playwright.sync_playwright() as pw:
                try:
                    br = pw.chromium.launch(headless=True)
                except Exception as exc:   # noqa: BLE001 - no browser is a skip with its reason, never a pass
                    pytest.skip(f"playwright chromium not installed: {exc}")
                page = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
                page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                for t in instants:
                    RB.frame_png(page, t, (w, h))
                    box = page.evaluate("() => { const c = document.querySelector('circle.chipseal');"
                                        " if (!c) return null; const b = c.getBoundingClientRect(); return [b.width, b.height]; }")
                    assert box, f"{surface}: no seal drawn at {t}"
                    out[t] = (float(box[0]), float(box[1]))
                br.close()
        finally:
            srv.shutdown()
    return out


@pytest.mark.parametrize("surface,enter", [("chip-stamp-arrival", 10.0), ("chip-stamp-seal-text", 10.0)])
def test_a_SEAL_does_not_squash_its_width_and_height_stay_equal_from_the_contact_to_contact_plus_0_1s(surface, enter):
    # the 24 fps squash frame is contact + 0.021 .. + 0.063 s; sampled across it and either side
    instants = [round(enter + CONTACT + d, 4) for d in (0.0, 0.025, 0.035, 0.042, 0.055, 0.075, 0.1)]
    boxes = _seal_boxes(surface, instants)
    for t, (bw, bh) in boxes.items():
        assert abs(bw - bh) <= 0.5, f"{surface}: the seal is {bw:.1f} x {bh:.1f} px at {t} (contact + {t - enter - CONTACT:.3f} s) - squashed"


# ---- (8) P70 T1c (E99 s127 / s128): the seal's shockwave is gold; a bare prop's ring reads on any ground; the seal ----
# stays open. Measured on the rendered frame: the frame as drawn against the same frame with the rings (or the chip)
# hidden, every other element identical.

def _wcag(rgb):
    import numpy as np
    c = np.asarray(rgb, dtype=float) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722


_DOM_PROBE = """() => {
  const o = {}, st = document.getElementById('stage').getBoundingClientRect();
  const c = document.querySelector('circle.chipstampring'); if (c) o.chip = c.getAttribute('stroke');
  const r = document.querySelector('.dock-ring'); if (r) o.dock = getComputedStyle(r).borderTopColor;
  const s = document.querySelector('circle.chipsealin');
  if (s) { const b = s.getBoundingClientRect(); o.seal = [b.left + b.width / 2 - st.left, b.top + b.height / 2 - st.top, b.width / 2]; }
  return o; }"""


def frames(tl: dict, uris: dict, instants: list[float], hide_css: str) -> dict:
    """{(hidden, t): RGB array, ("dom", t): the probe} - one browser, the page drawn as is and with `hide_css` applied."""
    playwright = pytest.importorskip("playwright.sync_api")
    import tempfile
    import numpy as np
    from PIL import Image
    import render_baseline as RB
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    shots: dict = {}
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "t1c.html"
        html.write_text(RB.instantiate(tl, uris, RB.TEMPLATE), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with playwright.sync_playwright() as pw:
                try:
                    br = pw.chromium.launch(headless=True)
                except Exception as exc:   # noqa: BLE001 - no browser is a skip with its reason, never a pass
                    pytest.skip(f"playwright chromium not installed: {exc}")
                for hide in (False, True):
                    page = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
                    page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                    RB.prepare_page(page, w, h)
                    if hide:
                        page.add_style_tag(content=hide_css)
                    for t in instants:
                        RB.frame_png(page, t, (w, h))
                        page.wait_for_timeout(120)
                        shots[(hide, t)] = np.asarray(Image.open(io.BytesIO(RB.frame_png(page, t, (w, h)))).convert("RGB"))
                        if not hide:
                            shots[("dom", t)] = page.evaluate(_DOM_PROBE)
                    page.close()
                br.close()
        finally:
            srv.shutdown()
    return shots


def ring_measure(shown, hidden) -> dict:
    """The impact ring alone: the pixels it changes (> 2 in any channel), the WCAG contrast of each against the ground
    drawn under it (the hidden frame's pixel), their median, and the ring's median warmth R - B."""
    import numpy as np
    d = np.abs(shown.astype(int) - hidden.astype(int)).max(axis=2) > 2
    if not d.any():
        return {"px": 0, "contrast": 0.0, "warmth": 0.0, "ground": None}
    a, b = _wcag(shown[d]), _wcag(hidden[d])
    con = (np.maximum(a, b) + 0.05) / (np.minimum(a, b) + 0.05)
    warm = shown[d][:, 0].astype(int) - shown[d][:, 2].astype(int)
    return {"px": int(d.sum()), "contrast": float(np.median(con)), "warmth": float(np.median(warm)),
            "ground": "#%02X%02X%02X" % tuple(int(v) for v in np.median(hidden[d], axis=0))}


def photo_png() -> bytes:
    """A deterministic stand-in for a PHOTO plate: a dusk-toned gradient with grain (no gitignored input needed)."""
    import numpy as np
    from PIL import Image
    rng = np.random.default_rng(127)
    y, x = np.mgrid[0:180, 0:320]
    base = np.stack([40 + 50 * x / 320, 52 + 40 * y / 180, 70 + 30 * (1 - x / 320)], axis=2)
    img = np.clip(base + rng.normal(0, 14, base.shape), 0, 255).astype("uint8")
    buf = io.BytesIO()
    Image.fromarray(img, "RGB").save(buf, "PNG")
    return buf.getvalue()


def prop_on(ground: str, png: bytes | None = None) -> tuple[dict, dict]:
    """The prop-stamp golden's own bare-prop stamp on the named ground: its charcoal ledger page as committed, or the
    same dock (the same place, the same fit) on a cream plate, a charcoal plate or a photo plate."""
    import copy
    import render_baseline as RB
    import build_golden_sources as BGS
    tl, uris = RB.load_surface("prop-stamp")[:2]
    if ground == "charcoal ledger":
        return tl, uris
    tl, uris = copy.deepcopy(tl), dict(uris)
    if png is None:
        png = {"cream plate": lambda: BGS.png_solid(64, 36, BGS.CHIP_STAMP_CREAM),
               "charcoal plate": lambda: BGS.png_solid(64, 36, BGS.CHIP_STAMP_CHARCOAL),
               "photo plate": photo_png}[ground]()
    tl["scenes"][0]["world"] = {"asset_id": "plate-t1c", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    uris["plate-t1c"] = BGS.uri("image/png", png)
    return tl, uris


RING_FLOOR = 2.0   # the ring's median contrast on its ground at contact + 0.05 s, where its own alpha is 0.49 (RING_A 0.55 x
                   # (1 - life)): the better of the page's two inks reaches ~3-4:1 there, a ring inked like its ground ~1:1


@pytest.mark.parametrize("ground", ["cream plate", "charcoal ledger", "charcoal plate", "photo plate"])
def test_a_BARE_PROPS_ring_reads_on_any_ground_its_ink_picked_by_the_MEASURED_ground(ground):
    tl, uris = prop_on(ground)
    t = round(10.0 + CONTACT + 0.05, 4)
    f = frames(tl, uris, [t], _HIDE_RINGS)
    m = ring_measure(f[(False, t)], f[(True, t)])
    assert m["px"] > 500, f"{ground}: the ring is out ({m})"
    assert m["contrast"] >= RING_FLOOR, f"{ground}: the ring's median contrast {m['contrast']:.2f}:1 on {m['ground']} is under {RING_FLOOR}:1 ({m})"
    dock = f[("dom", t)].get("dock", "")
    want = "rgb(37, 49, 60)" if ground == "cream plate" else "rgb(242, 242, 242)"
    assert dock == want, f"{ground}: the ring inked {dock} - s87: the page's chalk or charcoal, never gold"


@pytest.mark.parametrize("surface,gold", [("chip-stamp-arrival", "#A07F4B"), ("chip-stamp-seal-text", "#E8B86D")])
def test_a_SEALS_shockwave_is_the_seals_gold_on_the_frame(surface, gold):
    import render_baseline as RB
    tl, uris = RB.load_surface(surface)[:2]
    t = round(10.0 + CONTACT + 0.05, 4)
    f = frames(tl, uris, [t], _HIDE_RINGS)
    assert f[("dom", t)].get("chip") == gold, f"{surface}: the shockwave's stroke {f[('dom', t)]}"
    m = ring_measure(f[(False, t)], f[(True, t)])
    assert m["px"] > 500 and m["warmth"] > 30, f"{surface}: the ring reads warm - gold, not chalk or charcoal ({m})"


def seal_over_chart() -> tuple[dict, dict]:
    """The committed stamped chip (chip-stamp-arrival's entry, ink cream) placed over the plot of the prop-stamp golden's
    charcoal ledger page, in place of the prop."""
    import copy
    import render_baseline as RB
    tl, uris = RB.load_surface("prop-stamp")[:2]
    ctl, curis = RB.load_surface("chip-stamp-arrival")[:2]
    tl, uris = copy.deepcopy(tl), dict(uris, **{k: v for k, v in curis.items() if k.startswith("prop:")})
    chip = dict(copy.deepcopy(ctl["scenes"][0]["species"][0]), ink="cream", target={"kind": "point", "x": 0.62, "y": 0.5})
    tl["scenes"][0]["docks"], tl["scenes"][0]["species"] = [], [chip]
    return tl, uris


def test_the_seal_is_OPEN_the_chart_shows_through_it():
    """E99 s128: 'i actually like the chart peeking through on the stamp' - a stamp is drawn OVER the world. Inside the
    seal's inner ring, the chart pixels the chip leaves uncovered (its picture and its name aside) are the chart exactly
    as drawn without the chip; a filled seal would leave none."""
    import numpy as np
    tl, uris = seal_over_chart()
    t = 11.30
    f = frames(tl, uris, [t], ".chipstamp { display: none !important; }")
    cx, cy, r = f[("dom", t)]["seal"]
    shown, hidden = f[(False, t)].astype(int), f[(True, t)].astype(int)
    yy, xx = np.mgrid[0:shown.shape[0], 0:shown.shape[1]]
    d2 = (xx - cx) ** 2 + (yy - cy) ** 2
    inside = d2 <= (0.97 * r) ** 2
    chart = inside & (hidden.max(axis=2) > 110)   # the chart's ink and grid on the charcoal field (~#25313C)
    same = np.abs(shown - hidden).max(axis=2) <= 2
    through = int((chart & same).sum())
    assert chart.sum() > 200, f"the chip must stand over the chart: {int(chart.sum())} chart px inside the seal"
    assert through > 100, f"the chart shows through the open seal at {through} of {int(chart.sum())} px - a filled seal shows none"

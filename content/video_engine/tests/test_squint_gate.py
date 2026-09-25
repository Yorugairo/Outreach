"""M48 - THE SQUINT GATE (P71 T7; E99 s120, s126). A held page and its caption, shrunk to thumbnail width, still say
what they are about.

s120: "bravos chart still reads with its text/font, ours really doesn't ... not clear what we're immediately talking
about/focusing on" - a page rendered to thumbnail width must (1) make its focus identifiable (the lit series carries most
of the plot's visible contrast), (2) keep the title and the one name the sentence is about legible, (3) carry few words
on the plot. s126: "m48 should probably be a block because we have this issue with our captions too" - it FAILs, and a
caption that does not read at the small size fails the same gate, at a floor measured off the reference.

  the band     the page thresholds are Bravos's five frames read by the SAME tool (E38), n >= 5, one-sided
  the floor    the caption floor is the reference's own strip (Wealth Logic's long-form captions); a lane with no
               reference caption on disk (the shorts' strip) is INFO "no reference floor measured", never a floor
               fitted to ours
  the tool     a caption's cap height (its fill, glyph by glyph) and its contrast at the gate's width; the words rule;
               the held states of a page off the timeline's own clocks
  the gate     FAIL with its numbers on a page or a caption outside; PASS inside; INFO with no squint.json, on a stale
               one, and for an unmeasured lane
"""
from __future__ import annotations

import hashlib
import re
import json
import os
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import gate_motion_density as G  # noqa: E402
import measure_line_bloom as M  # noqa: E402

BAND_FILE = ROOT / "content/video_engine/assets/bravos-line-bloom.v1.json"
FLOOR_FILE = ROOT / "content/video_engine/assets/caption-squint-floor.v1.json"


def _band() -> dict:
    return json.loads(BAND_FILE.read_text(encoding="utf-8"))["squint_band"]


def _floor() -> dict:
    return json.loads(FLOOR_FILE.read_text(encoding="utf-8"))


def _page(**kw) -> dict:
    """A page at the middle of the band on every number, unless told otherwise."""
    b = _band()
    mid = lambda k: round((b[k]["min"] + b[k]["max"]) / 2, 3)  # noqa: E731
    base = {"t": 12.0, "scene": "s01", "title": "The sharpest chart", "lit_share": mid("lit_share"),
            "title_cap_px": mid("title_cap_px"), "label": "MEMORY", "label_cap_px": mid("label_cap_px"),
            "plot_words": b["plot_words"]["max"], "words": []}
    return base | kw


def _caption(**kw) -> dict:
    f = _floor()["lanes"]["16:9"]
    base = {"t": 3.3, "scene": "s01", "text": "Just not in the steel.", "mode": "anchor",
            "cap_px": round(f["cap_px"]["min"] * 1.2, 2), "contrast": round(f["contrast"]["min"] * 1.2, 2)}
    return base | kw


def _doc(pages=(), captions=(), aspect="16:9") -> dict:
    return {"schema": M.SQUINT_SCHEMA, "aspect": aspect, "gate_width": M.SQUINT_W, "pages": list(pages),
            "captions": list(captions)}


# ---- the thresholds, measured off the reference -------------------------------------------------------------------

def test_the_page_band_is_bravos_five_frames_at_n_5_on_every_squint_number():
    b = _band()
    assert b["width"] == M.SQUINT_W == 320
    assert b["frames"] == ["jpn-0520", "jpn-0523", "ai-builders", "kospi-index", "kospi-retail"]
    for k in ("lit_share", "title_cap_px", "plot_words"):
        assert b[k]["n"] >= 5, (k, b[k])
        assert b[k]["min"] <= b[k]["max"], (k, b[k])
    # the named label reads glyph by glyph on the 1024 px frames; at 512 px JPN's "Japan" merges (J, a and p are one
    # blob whose height is the p's descender to the J's top) - the frame is REPORTED unread, never a number
    assert b["label_cap_px"]["n"] == 5 - len(b["unread"]) >= 3, b
    assert set(b["unread"]) == {"jpn-0520", "jpn-0523"} and all("512" in v for v in b["unread"].values()), b["unread"]
    frames = {f["id"]: f for f in json.loads(BAND_FILE.read_text(encoding="utf-8"))["frames"]}
    for fid in b["frames"]:
        sq = frames[fid]["squint_gate"]
        for k in ("lit_share", "title_cap_px", "plot_words") + (() if fid in b["unread"] else ("label_cap_px",)):
            assert sq[k] is not None, (fid, k)
        assert b["lit_share"]["min"] <= sq["lit_share"] <= b["lit_share"]["max"]


def test_the_caption_floor_is_the_references_strip_and_the_shorts_lane_is_unmeasured():
    f = _floor()
    assert f["schema"] == "caption-squint-floor.v1" and f["width"] == M.SQUINT_W
    lf = f["lanes"]["16:9"]
    assert lf["reference"].startswith("Wealth Logic")
    assert lf["cap_px"]["n"] >= 10 and lf["contrast"]["n"] == lf["cap_px"]["n"]
    assert len(lf["frames"]) == lf["cap_px"]["n"]
    for fr in lf["frames"]:
        assert fr["frame"].startswith("content/video_engine/sources/reference_analyses/"), fr
        assert fr["measured"]["cap_px"] >= lf["cap_px"]["min"] and fr["measured"]["contrast"] >= lf["contrast"]["min"]
    sh = f["lanes"]["9:16"]
    assert sh["cap_px"] is None and sh["contrast"] is None and "no reference" in sh["status"]


# ---- the tool -----------------------------------------------------------------------------------------------------

def _caption_frame(tmp: Path, *, size: int, fill=(255, 255, 255), outline=(10, 10, 10), ground=(250, 250, 250),
                   text="THE BOND FUND LOST") -> tuple[Path, list[int]]:
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arialbd.ttf", size)
    except OSError:
        pytest.skip("no Arial Bold on this machine to set a known cap")
    im = Image.new("RGB", (1920, 1080), ground)
    d = ImageDraw.Draw(im)
    d.text((500, 900), text, font=font, fill=fill, stroke_width=max(1, size // 12), stroke_fill=outline)
    x0, y0, x1, y1 = d.textbbox((500, 900), text, font=font, stroke_width=max(1, size // 12))
    p = tmp / f"cap-{size}-{fill[0]}-{outline[0]}.png"
    im.save(p)
    return p, [x0 - 6, y0 - 6, x1 + 6, y1 + 6]


ARIAL_BOLD_CAP_EM = 0.716      # Arial Bold's capHeight 1467 / unitsPerEm 2048


def test_a_caption_reads_its_fill_cap_at_the_gate_width_and_its_contrast(tmp_path):
    p, box = _caption_frame(tmp_path, size=60)
    got = M.caption_read(p, box, "THE BOND FUND LOST")
    want = 60 * ARIAL_BOLD_CAP_EM * M.SQUINT_W / 1920
    assert got["cap_px"] == pytest.approx(want, rel=0.08), got      # the fill's capitals, not the outline round them
    assert got["contrast"] > 8.0, got                                 # white letters in a black outline


def test_a_caption_in_its_grounds_own_tone_has_no_contrast(tmp_path):
    p, box = _caption_frame(tmp_path, size=60, fill=(235, 230, 215), outline=(215, 210, 196), ground=(238, 232, 218))
    got = M.caption_read(p, box, "THE BOND FUND LOST")
    assert got["contrast"] < 1.6, got


def _word_frame(tmp: Path, words: list[str], size: int = 44) -> tuple[Path, list]:
    """Cream words in a dark text-shadow-like halo on a dark page: ours, with each word's box as the DOM gives it."""
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arialbd.ttf", size)
    except OSError:
        pytest.skip("no Arial Bold on this machine to set a known cap")
    im = Image.new("RGB", (1920, 1080), (30, 36, 44))
    d = ImageDraw.Draw(im)
    x, boxes = 400, []
    for wd in words:
        d.text((x, 850), wd, font=font, fill=(245, 236, 214), stroke_width=2, stroke_fill=(5, 5, 8))
        bb = d.textbbox((x, 850), wd, font=font, stroke_width=2)
        boxes.append(([bb[0] - 3, bb[1] - 3, bb[2] + 3, bb[3] + 3], wd))
        x = bb[2] + size // 3
    p = tmp / ("words-" + "-".join(words)[:30] + ".png")
    im.save(p)
    return p, boxes


def test_our_caption_is_read_word_by_word_off_its_own_boxes(tmp_path):
    p, words = _word_frame(tmp_path, ["The", "paper", "just", "got", "heavier."])
    union = [min(b[0] for b, _ in words), min(b[1] for b, _ in words), max(b[2] for b, _ in words), max(b[3] for b, _ in words)]
    got = M.caption_read(p, union, "The paper just got heavier.", words=words)
    assert got["cap_px"] == pytest.approx(44 * ARIAL_BOLD_CAP_EM * M.SQUINT_W / 1920, rel=0.08), got
    assert got["method"].startswith("words 5/5"), got


def test_a_lowercase_caption_reads_its_cap_off_its_ascenders_and_one_with_none_has_no_cap(tmp_path):
    p, words = _word_frame(tmp_path, ["year", "held."])
    got = M.caption_read(p, words[0][0], "year held.", words=words)
    assert "ascenders" in got["method"] and got["cap_px"] is not None, got      # h, l stand at the cap
    p, words = _word_frame(tmp_path, ["on", "camera."])
    got = M.caption_read(p, words[0][0], "on camera.", words=words)
    assert got["cap_px"] is None and "no cap letter" in got["method"], got     # never its x-height
    assert got["contrast"] > 3.0, got                                          # the contrast is still read


def test_the_words_on_a_plot_are_tokens_with_two_letters():
    assert M.word_count(["MEMORY MAKERS (hynix+Micron)", "+64%", "S&P 500", "240%", "our layer"]) == 6
    assert M.word_count(["$1.2T", "Q2", "2000"]) == 0


def test_a_page_is_held_once_per_state_at_the_middle_of_its_hold():
    page = {"builder": "dense-line", "enter": "axes", "series": [{"name": "A", "pts": [[0, 1], [1, 2]]}]}
    tl = {"runtime_s": 40.0, "scenes": [
        {"scene_id": "p", "span": [0.0, 20.0], "world": {"kind": "ledger", "page": page}, "docks": [],
         "species": [{"kind": "chart_to", "at": 10.0, "dur": 1.0, "to": "recast"}]},
        {"scene_id": "plate", "span": [20.0, 40.0], "world": {"asset_id": "x"}, "species": [], "docks": []}]}
    held = M.held_instants(tl)
    assert [h["scene"] for h in held] == ["p", "p"], held
    land = G._page_land_offset(tl["scenes"][0])
    assert held[0]["t"] == pytest.approx((land + 10.0) / 2, abs=0.02)
    assert held[1]["t"] == pytest.approx((G._transition_land(tl["scenes"][0], tl["scenes"][0]["species"][0]) + 20.0) / 2,
                                         abs=0.02)


def test_a_write_on_the_page_splits_its_hold_and_a_held_solo_does_not():
    page = {"builder": "dense-line", "enter": "axes", "series": [{"name": "A", "pts": [[0, 1], [1, 2]]}]}
    sc = {"scene_id": "p", "span": [0.0, 20.0], "world": {"kind": "ledger", "page": page}, "docks": [],
          "species": [{"kind": "retitle", "at": 8.0, "dur": 2.0, "text": "New"},
                      {"kind": "solo", "at": 12.0, "dur": 8.0, "series": 0}]}
    held = M.held_instants({"runtime_s": 20.0, "scenes": [sc]})
    assert [h["hold"][1] for h in held] == [8.0, 20.0], held      # the retitle's write is not a held page; the solo is
    assert held[1]["hold"][0] == 10.0 and held[1]["t"] == 15.0, held


def test_a_caption_page_is_read_when_every_word_is_written():
    tl = {"caption_pages": [{"s": 0.3, "e": 1.94, "cap_mode": "anchor",
                             "t": [{"w": "The", "s": 0.3, "e": 0.44}, {"w": "AI", "s": 0.44, "e": 1.94}]}]}
    (c,) = M.caption_instants(tl)
    assert 0.44 < c["t"] < 1.94 and c["text"] == "The AI" and c["mode"] == "anchor"


# ---- the gate -----------------------------------------------------------------------------------------------------

def test_m48_fails_an_out_of_focus_page_with_its_numbers():
    b = _band()
    low = round(b["lit_share"]["min"] - 0.1, 3)
    g = G._squint_gate(_doc(pages=[_page(lit_share=low)]))
    assert g.id == "M48" and g.level == "FAIL", g
    assert f"lit share {low:.3f}" in g.message and "s01" in g.message, g.message


def test_a_page_with_thirty_words_passes_when_it_reads_and_the_count_is_info():
    """E99 s129: the plot's word count is not a gate - 30 words on a legible page PASS, the count is reported."""
    g = G._squint_gate(_doc(pages=[_page(plot_words=30, panel_words=[30])]))
    assert g.level == "PASS", g
    assert "words on the plot (INFO, s129) up to 30" in g.message, g.message


def test_a_panels_page_counts_its_words_per_plot_panel_and_the_nearest_takes_a_stray():
    plots = [[100, 100, 500, 400], [700, 100, 1100, 400]]
    texts = ["MEMORY MAKERS up", "DRAM", "HBM SHARE", "LEFT OUTSIDE"]
    boxes = [[150, 150, 300, 170], [720, 150, 780, 170], [800, 300, 900, 320], [510, 200, 560, 220]]
    assert M.panel_word_counts(texts, boxes, plots) == [5, 3]      # the stray at x 535 is 25 px from panel 1's edge


def test_m48_fails_a_page_whose_title_or_name_is_under_the_bravos_size():
    b = _band()
    g = G._squint_gate(_doc(pages=[_page(title_cap_px=round(b["title_cap_px"]["min"] * 0.8, 2))]))
    assert g.level == "FAIL" and "title" in g.message, g
    g = G._squint_gate(_doc(pages=[_page(label_cap_px=round(b["label_cap_px"]["min"] * 0.8, 2))]))
    assert g.level == "FAIL" and "MEMORY" in g.message, g


def test_m48_fails_an_under_floor_caption_with_its_numbers():
    f = _floor()["lanes"]["16:9"]
    small = round(f["cap_px"]["min"] * 0.7, 2)
    g = G._squint_gate(_doc(pages=[_page()], captions=[_caption(cap_px=small)]))
    assert g.level == "FAIL" and f"{small}" in g.message and "Just not in the steel." in g.message, g.message
    flat = round(f["contrast"]["min"] * 0.5, 2)
    g = G._squint_gate(_doc(captions=[_caption(contrast=flat)]))
    assert g.level == "FAIL" and "contrast" in g.message, g.message


def test_m48_passes_a_page_and_a_caption_inside():
    g = G._squint_gate(_doc(pages=[_page()], captions=[_caption()]))
    assert g.level == "PASS", g
    assert "1 page" in g.message and "1 caption" in g.message, g.message


def test_m48_is_info_for_the_shorts_strip_with_no_reference_floor_and_still_judges_the_page():
    g = G._squint_gate(_doc(pages=[_page()], captions=[_caption(cap_px=0.5, contrast=1.0)], aspect="9:16"))
    assert g.level == "PASS" and "no reference floor" in g.message, g.message
    g = G._squint_gate(_doc(pages=[_page(title_cap_px=1.0)], captions=[_caption()], aspect="9:16"))
    assert g.level == "FAIL", g
    g = G._squint_gate(_doc(captions=[_caption()], aspect="9:16"))
    assert g.level == "INFO" and "no reference floor" in g.message, g.message


def test_m48_is_info_with_no_file_and_names_the_command(tmp_path):
    assert G.load_squint(tmp_path) is None
    g = G._squint_gate(None, measured_in=tmp_path)
    assert g.level == "INFO" and "measure_line_bloom.py --build" in g.message, g


def test_m48_is_info_on_a_stale_file(tmp_path):
    (tmp_path / "player.html").write_text("<html>new</html>", encoding="utf-8")
    doc = _doc(pages=[_page(lit_share=0.01)]) | {"player_sha256": hashlib.sha256(b"<html>old</html>").hexdigest()}
    (tmp_path / M.SQUINT_NAME).write_text(json.dumps(doc), encoding="utf-8")
    assert G.load_squint(tmp_path) == "stale"
    g = G._squint_gate("stale", measured_in=tmp_path)
    assert g.level == "INFO" and "stale" in g.message, g


def test_run_carries_m48_and_the_verdict_counts_it():
    tl = {"runtime_s": 30.0, "scenes": [{"scene_id": "s01", "span": [0.0, 30.0], "species": [], "docks": [],
                                          "world": {"kind": "ledger", "page": {"builder": "dense-line", "series": []}}}]}
    gates, _ = G.run(tl, [], {"cues": []}, squint=_doc(pages=[_page(lit_share=0.01)]))
    m48 = [g for g in gates if g.id == "M48"]
    assert len(m48) == 1 and m48[0].level == "FAIL", m48
    assert G.fail_count(gates) >= 1


def test_the_row_is_documented_in_the_gate_docstring():
    assert "M48" in G.__doc__ and "squint" in G.__doc__.lower()


# ---- the reference, re-read (the gitignored research frames, when on disk) ---------------------------------------

def _refs_root() -> Path | None:
    cands = [os.environ.get("BRAVOS_FRAMES_ROOT"), str(ROOT)]
    if ".claude" in ROOT.parts:
        cands.append(str(Path(*ROOT.parts[:ROOT.parts.index(".claude")])))
    first = _floor()["lanes"]["16:9"]["frames"][0]["frame"]
    for c in cands:
        if c and (Path(c) / first).exists():
            return Path(c)
    return None


def test_the_tool_reproduces_the_caption_floor_and_the_squint_band():
    root = _refs_root()
    if root is None:
        pytest.skip("the reference frames are not on disk (gitignored): set BRAVOS_FRAMES_ROOT")
    assert M.check_caption_floor(FLOOR_FILE, root) == []
    assert M.check_squint_band(BAND_FILE, root) == []


# ---- the honest count, rendered (E99 s129 (3): axis ticks and axis titles are not words) ---------------------------

def _chromium() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


TICKISH = re.compile(r"^([A-Z][a-z]{2} '\d\d|\d{4}E?|[$\d.,%x+-]+)$")   # "Oct '25", "2026E", "640", "80%", "3x"


@pytest.mark.skipif(not _chromium(), reason="playwright chromium not installed")
@pytest.mark.parametrize("surface", ["solo-chipmakers", "page-rescale-follow"])
def test_a_single_chart_page_counts_no_tick_and_no_axis_title(tmp_path, surface):
    import render_baseline as RB
    tl, uris, t, _aspect = RB.load_surface(surface)
    (tmp_path / "player.html").write_text(RB.instantiate(tl, uris), encoding="utf-8")
    (tmp_path / f"{surface}.timeline.json").write_text(json.dumps(tl), encoding="utf-8")
    doc = json.loads(M.measure_build(tmp_path, at=[t]).read_text(encoding="utf-8"))
    (page,) = doc["pages"]
    ticks = [w for w in page["words"] if TICKISH.match(w.strip())]
    titles = [w for w in page["words"] if re.search(r"(?i)log scale|per year|index\b|= ?100", w)]
    assert not ticks and not titles, page["words"]

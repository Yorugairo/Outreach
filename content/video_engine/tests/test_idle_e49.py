"""P47 T5 - THE IDLE (ruling E49, 2026-09-06: "nothing ever goes truly still").

Every held thing - the page under a sentence, a parked dock, a pill, a caption, an image plate - carries a NAMED subtle
idle, a pure function of t behind `kinetics.idle`; Ken Burns and the parallax push go back to being camera moves. The
idle is not an event for the motion gate; the gate's new row M18 reads the per-frame hashes measure_frozen_frames.py
writes and WARNs on a run of bit-identical frames over FROZEN_MAX_S.

Static and compiler checks always run; the browser proof needs playwright + chromium and is skipped without them.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import measure_frozen_frames as MF  # noqa: E402
import render_baseline as RB  # noqa: E402

TEMPLATE = RB.TEMPLATE
SOURCES = RB.SOURCES
HOLD_T = 11.0          # the soak golden's page holds after its build (badges land ~9.5 s) until the retract near 30 s
HALF_S = 0.5           # E49's frozen ceiling: two frames this far apart must differ


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


# ---- the template ----------------------------------------------------------------------------


def test_the_flag_exists_defaults_off_and_the_module_is_inlined():
    html = RB.player_text()
    m = re.search(r"const KINETICS_DEFAULTS = Object\.freeze\(\{(.*?)\}\);", html, re.S)
    assert m and re.search(r"\bidle:\s*false", m.group(1)), "kinetics.idle must exist and default OFF (P39)"
    assert "/* KINETICS:BEGIN idle */" in html and "const IDLE_KINDS = Object.freeze" in html
    assert "const IDLE_CLASS = Object.freeze({ page: \"breath\", plate: \"breath\", dock: \"breath\", pill: \"breath\", caption: \"breath\" });" in html
    # every held class composes the idle onto its own transform, behind the flag, from t
    for cls in ("page", "pill", "dock", "caption"):
        assert f'idleCssFor("{cls}"' in html, cls
    assert 'idleOf("plate", scene.world.idle)' in html


def test_the_idle_is_a_named_kind_and_the_module_carries_its_tags():
    src = (ROOT / "content/video_engine/scripts/kinetics/idle.mjs").read_text(encoding="utf-8")
    assert '["none", "breath", "drift", "pulse", "figure"]' in src
    assert "[DERIVED: HyperFrames /prompting/motion" in src, "the 1-2 % amplitude is a starting reference, tagged"
    assert "48 s48.4" in src, "the figure's breath and the sway cite doc 48"


# ---- the compiler ----------------------------------------------------------------------------


def test_split_idle_reads_the_option_and_refuses_an_unknown_kind():
    assert B.split_idle("ledger:x:line") == ("ledger:x:line", None)
    assert B.split_idle("ledger:x:line;idle=none") == ("ledger:x:line", "none")
    assert B.split_idle("plate-07;idle=figure") == ("plate-07", "figure")
    with pytest.raises(ValueError, match="idle 'wobble' is not one of"):
        B.split_idle("plate-07;idle=wobble")
    assert B.IDLE_KINDS == ("none", "breath", "drift", "pulse", "figure")


def test_world_for_plate_carries_the_idle_and_strips_it_from_the_id(tmp_path: Path):
    clip = tmp_path / "c.mp4"
    clip.write_bytes(b"\x00" * 64)
    w = B.world_for_plate(f"clip:{clip};idle=none", (0.0, 0, 0), tmp_path)
    assert w["idle"] == "none" and w["asset_id"] == "c" and w["clip_path"] == str(clip)
    w2 = B.world_for_plate(f"clip:{clip}", (0.0, 0, 0), tmp_path)
    assert "idle" not in w2, "no option, no key - an old build compiles exactly as it did"


def test_every_compiled_timeline_turns_the_idle_on_unless_the_build_says_otherwise(monkeypatch):
    monkeypatch.setattr(B, "KINETICS", {})
    assert B.build_kinetics()["idle"] is True
    monkeypatch.setattr(B, "KINETICS", {"analytic_spring": True, "idle": False})
    k = B.build_kinetics()
    assert k["idle"] is False and k["analytic_spring"] is True, "stillness is explicit"


def test_golden_sources_carry_no_idle_flag_so_they_stay_byte_identical():
    for p in sorted(SOURCES.glob("*.timeline.json")):
        tl = json.loads(p.read_text(encoding="utf-8"))
        assert not (tl.get("kinetics") or {}).get("idle"), p.name


# ---- the gate: M18 frozen frames --------------------------------------------------------------


def _frames(hashes: list[str], fps: float = 12.0) -> list[dict]:
    return [{"t": round(i / fps, 4), "sha256": h} for i, h in enumerate(hashes)]


def test_frozen_runs_finds_only_runs_over_the_ceiling_and_both_copies_agree():
    a, b = "a" * 8, "b" * 8
    fr = _frames([a] * 3 + [b] * 12 + [a] * 2 + [b] * 7)   # 3 frames = 0.17 s, 12 = 0.92 s, 2, 7 = 0.5 s exactly
    runs = G.frozen_runs(fr)
    assert runs == MF.frozen_runs(fr)
    assert len(runs) == 1 and abs(runs[0][0] - 0.25) < 1e-3 and abs(runs[0][1] - 11 / 12) < 1e-3   # t is rounded to 4 places
    assert G.frozen_runs(_frames([a, b] * 30)) == []


def test_m18_is_info_until_measured_warn_on_a_freeze_and_pass_when_nothing_holds():
    assert G._frozen_gate(None).level == "INFO" and "measure_frozen_frames.py" in G._frozen_gate(None).message
    fr = _frames([f"{i:08x}" for i in range(40)])
    ok = G._frozen_gate(fr)
    assert ok.level == "PASS" and "12 fps" in ok.message
    frozen = _frames([f"{i:08x}" for i in range(10)] + ["deadbeef"] * 10 + [f"{i:08x}" for i in range(50, 60)])
    bad = G._frozen_gate(frozen)
    assert bad.level == "WARN" and "1 run(s)" in bad.message and "kinetics.idle" in bad.message


def test_run_reports_m18_and_the_idle_never_changes_the_event_count():
    tl = json.loads((SOURCES / "ledger-soak-page.timeline.json").read_text(encoding="utf-8"))
    gates_off, stats_off = G.run(tl, [], {})
    gates_on, stats_on = G.run(dict(tl, kinetics={"idle": True}), [], {}, frames=_frames([f"{i:08x}" for i in range(24)]))
    by = lambda gs: {g.id: g for g in gs}
    assert by(gates_off)["M18"].level == "INFO" and by(gates_on)["M18"].level == "PASS"
    assert stats_off["visual_events"] == stats_on["visual_events"], "an idle is not an event (E49 s3)"


def test_write_report_reads_frame_hashes_beside_the_timeline(tmp_path: Path):
    tl = json.loads((SOURCES / "ledger-soak-page.timeline.json").read_text(encoding="utf-8"))
    (tmp_path / "x.timeline.json").write_text(json.dumps(tl), encoding="utf-8")
    (tmp_path / "motion-plan.json").write_text("{}", encoding="utf-8")
    (tmp_path / G.FRAME_HASHES_NAME).write_text(json.dumps({"fps": 12, "frames": _frames(["f" * 8] * 30)}), encoding="utf-8")
    out, _ = G.write_report(tmp_path, "x.timeline.json")
    text = out.read_text(encoding="utf-8")
    assert "[WARN ] M18" in text and "2.42s" in text


# ---- the browser: the frozen frame, and the idle that removes it --------------------------------


def _hash(png: bytes) -> str:
    return hashlib.sha256(RB.rgb_bytes(png)[1]).hexdigest()


def _bare_hold() -> tuple[dict, dict, str]:
    """The soak golden's ledger scene with its caption pages removed: a page holding under nothing at all - the plan's
    'golden ledger scene with no species', where a frozen frame has nowhere to hide."""
    tl, uris, _t, aspect = RB.load_surface("ledger-soak-page")
    scenes = [dict(sc, world=dict(sc["world"], ken_burns={"scale": 0, "x": 0, "y": 0})) for sc in tl["scenes"]]   # no camera move: E49's point
    return dict(tl, caption_pages=[], captions=[], scenes=scenes), uris, aspect


def _render(tl: dict, uris: dict, aspect: str, t: float, kinetics: dict | None = None) -> bytes:
    if kinetics is not None:
        tl = dict(tl, kinetics=kinetics)
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "hold.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        return RB.render_frame(html, t, aspect)


@needs_browser
def test_two_hold_frames_are_identical_with_the_flag_off_and_differ_by_the_idle_alone_with_it_on():
    """The frozen frame E49 names, then its cure: the soak golden's page under a hold, 0.5 s apart."""
    tl, uris, aspect = _bare_hold()
    off_a, off_b = _render(tl, uris, aspect, HOLD_T), _render(tl, uris, aspect, HOLD_T + HALF_S)
    assert _hash(off_a) == _hash(off_b), "pre-E49 the held page is bit-identical half a second later - the freeze"
    on_a = _render(tl, uris, aspect, HOLD_T, kinetics={"idle": True})
    on_b = _render(tl, uris, aspect, HOLD_T + HALF_S, kinetics={"idle": True})
    assert _hash(on_a) != _hash(on_b), "with the idle on, no two frames half a second apart are the same"
    # the measured runs on the four frames say the same thing the gate will
    assert G.frozen_runs([{"t": HOLD_T, "sha256": _hash(off_a)}, {"t": HOLD_T + HALF_S, "sha256": _hash(off_b)}], max_s=0.4)
    assert not G.frozen_runs([{"t": HOLD_T, "sha256": _hash(on_a)}, {"t": HOLD_T + HALF_S, "sha256": _hash(on_b)}], max_s=0.4)


@needs_browser
def test_the_page_body_breathes_under_two_percent_and_nothing_else_moves():
    """Browser-measured: the page's box at rest and at the breath's peak differ by the dial (1.2 %), and the same seek
    twice gives the same box (a pure function of t)."""
    from playwright.sync_api import sync_playwright
    tl, uris, aspect = _bare_hold()
    tl = dict(tl, kinetics={"idle": True})
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "idle.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                seek = ("t => { const s = document.getElementById('scrub'); s.value = t;"
                        " s.dispatchEvent(new Event('input', {bubbles:true})); }")
                box = "() => { const r = document.querySelector('.lp-page').getBoundingClientRect(); return [r.width, r.height]; }"
                xf = "() => document.querySelector('.lp-page').style.transform"
                # breath period 4 s at 0.25 Hz with the page's own phase: sample a whole period at 1/8 s and take the extremes
                widths = []
                for i in range(33):
                    page.evaluate(seek, HOLD_T + i / 8)
                    widths.append(page.evaluate(box)[0])
                lo, hi = min(widths), max(widths)
                assert hi / lo > 1.008 and hi / lo < 1.02, f"breath {hi / lo:.4f}: E49 wants 1-2 % (dial 1.2 %)"
                page.evaluate(seek, HOLD_T + 1.0)
                a = page.evaluate(xf); wa = page.evaluate(box)
                page.evaluate(seek, HOLD_T + 2.0)
                page.evaluate(seek, HOLD_T + 1.0)
                assert page.evaluate(xf) == a and page.evaluate(box) == wa, "a seek is the play"
                assert re.search(r"translate\(0px, 0px\) scale\(1\.\d+\)$", a), f"the page's idle is the breath, scale only (browser-normalised): {a}"
                browser.close()
        finally:
            srv.shutdown()


def test_m18_refuses_frame_hashes_measured_on_another_player(tmp_path: Path):
    """A rebuilt player makes the hashes beside it stale: the row says so instead of passing on old evidence."""
    (tmp_path / "player.html").write_text("<html>rebuilt</html>", encoding="utf-8")
    (tmp_path / G.FRAME_HASHES_NAME).write_text(json.dumps({"fps": 12, "html_sha256": "0" * 64, "frames": _frames([f"{i:08x}" for i in range(30)])}), encoding="utf-8")
    assert G.load_frames(tmp_path) == "stale"
    g = G._frozen_gate("stale")
    assert g.level == "INFO" and "another player.html" in g.message
    good = hashlib.sha256((tmp_path / "player.html").read_bytes()).hexdigest()
    (tmp_path / G.FRAME_HASHES_NAME).write_text(json.dumps({"fps": 12, "html_sha256": good, "frames": _frames([f"{i:08x}" for i in range(30)])}), encoding="utf-8")
    assert isinstance(G.load_frames(tmp_path), list)

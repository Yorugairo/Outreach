"""P69 T49 - THE FREEZE BEAT: everything stops and one light comes on (E99 s99).

The operator, 2026-09-23: "Light can become motion when it's highlighting and moving along a length, blinking, or when
it actually stops motion when the light comes on I think. Bravos does this well." The ruling: "a light that comes on as
everything else STOPS is a punctuation beat - the freeze is the event". The token is a STAGE species:
`{"kind": "freeze", "at", "dur", "target"}` - on its word every idle, drift and ambient life on the stage holds for
`dur` (0.4-1.2 s) while ONE light comes on at the target (a datum, or the box of a mark or a prop); then life resumes.
The law and the painter are species/freeze.mjs (pinned by tests/kinetics/freeze.test.mjs); this file pins the
compiler's grammar, the gate (M18 reads the beat as punctuation, not a still run; the beat is ONE event), the frozen-
frames measurement, the engine's wiring, the card, and the beat read on the SERVED player (the golden `freeze-trough`).

Not `beat_freeze` (doc 29 s9.27): that is a BOUNDARY move - the chart's final state freezes as a hit, then a
directional cut into the next plate. This one is inside a scene, and life comes back.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import measure_frozen_frames as MF  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
MODULE = ROOT / "content/video_engine/scripts/species/freeze.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/species.json"
PAGE = "ledger:ev-railway-index-v1:line:139:right"
PLATE = "plate-desk"
FZ = {"kind": "freeze", "at": 12.0, "dur": 0.8, "target": {"kind": "datum", "index": 139, "series": 0}}


def _errs(entries, plate=PAGE, ken=(0, 0, 0)):
    return B.validate_species([dict(e) for e in entries], ken, plate)


def _frames(hashes: list[str], t0: float = 0.0, fps: float = 12.0) -> list[dict]:
    return [{"t": round(t0 + i / fps, 4), "sha256": h} for i, h in enumerate(hashes)]


# ---- the grammar -------------------------------------------------------------------------------------------------


def test_the_token_is_a_stage_species_the_compiler_accepts_on_a_page_and_on_a_plate():
    assert "freeze" in B.SPECIES_KINDS and "freeze" not in B.PAGE_SPECIES
    assert _errs([FZ]) == []
    assert _errs([dict(FZ, target={"kind": "point", "x": 0.4, "y": 0.5})], plate=PLATE) == [], "a plate's thing"
    assert _errs([dict(FZ, target={"kind": "region", "x0": 0.1, "y0": 0.2, "x1": 0.3, "y1": 0.6})], plate=PLATE) == [], \
        "a prop's or a mark's box"


@pytest.mark.parametrize("dur", [0.4, 0.8, 1.2])
def test_the_beat_is_the_dial_s_length(dur):
    assert _errs([dict(FZ, dur=dur)]) == []


@pytest.mark.parametrize("dur", [0.2, 0.39, 1.21, 3.0])
def test_a_beat_outside_the_dial_is_refused_by_name(dur):
    errs = _errs([dict(FZ, dur=dur)])
    assert any("freeze" in e and "0.4" in e and "1.2" in e for e in errs), errs


@pytest.mark.parametrize("patch, needle", [
    ({"target": None}, "target"),
    ({"target": {"kind": "span", "from_word": 0, "to_word": 1}}, "not allowed"),
    ({"label": "the trough"}, "writes nothing"),
    ({"idle": "breath"}, "writes nothing"),
])
def test_a_malformed_freeze_is_refused_by_name(patch, needle):
    entry = {k: v for k, v in dict(FZ, **patch).items() if v is not None}
    errs = _errs([entry])
    assert any(needle in e for e in errs), errs


def test_one_light_everything_else_stops_nothing_else_fires_inside_the_beat():
    """ONE light: a second species that starts, lands or leaves inside the beat is a second motion - refused by name.
    Before the beat and after it is the row's own business, and so is a mark that simply holds across it."""
    fig = {"kind": "figure", "at": 12.3, "dur": 1.0, "target": {"kind": "datum", "index": 139}, "text": "-64%"}
    errs = _errs([FZ, fig])
    assert any("freeze" in e and "figure" in e and "one light" in e for e in errs), errs
    ends_inside = dict(fig, at=11.0, dur=1.4)   # it lands at 12.4, inside the beat
    assert any("figure" in e for e in _errs([FZ, ends_inside])), "a mark that LANDS inside the beat moves in it"
    assert _errs([FZ, dict(fig, at=11.0, dur=1.0)]) == [], "a figure that landed on the word before"
    assert _errs([FZ, dict(fig, at=12.8)]) == [], "... or that is written as life resumes"
    assert _errs([FZ, {"kind": "spotlight", "at": 9.0, "dur": 6.0, "target": {"kind": "datum", "index": 139}}]) == [], \
        "a light that holds across the beat holds with it (its idle stops with the rest)"
    two = _errs([FZ, dict(FZ, at=12.5)])
    assert any("one light" in e for e in two), two


@pytest.mark.parametrize("kind", ["punch", "focus_zoom", "pull_back", "plate_life", "ticker", "life"])
def test_a_motion_the_player_cannot_hold_is_refused_across_the_beat(kind):
    """A camera move, stepped plate life, a ticker or a declared self-animating world keeps moving through any window
    it spans - the player has no hold for it - so a freeze inside one is refused, naming both."""
    other = {"kind": kind, "at": 10.0, "dur": 4.0,
             "target": {"kind": "region", "x0": 0.1, "y0": 0.1, "x1": 0.5, "y1": 0.5}}
    if kind in ("plate_life", "life"):
        other.pop("target")
    errs = _errs([dict(FZ, target={"kind": "point", "x": 0.4, "y": 0.5}), other], plate=PLATE)
    assert not any("kind must be one of" in e for e in errs), errs
    assert any(e.startswith(f"{PLATE}: freeze") and kind in e and "cannot hold" in e for e in errs), errs


def test_the_when_says_what_sentence_calls_for_it_and_when_not():
    w = B.SPECIES_WHEN["freeze"]
    assert "TURN" in w and "one" in w and "STOPS" in w
    assert "never" in w


# ---- the gate: the beat is punctuation, not stillness -----------------------------------------------------------


def test_the_freeze_is_one_event_at_its_word():
    assert G.SPECIES_EVENTS["freeze"] == ("at",)
    scenes = [{"scene_id": "s1", "span": [0.0, 30.0], "species": [dict(FZ)]}]
    assert G._species_events(scenes) == [12.0], "the freeze IS the event (s99); the light's resume earns nothing"
    assert "freeze" in G.POINTING_KINDS, "it declares a target, so M24 reads it"


def test_freeze_windows_are_read_from_the_timeline_and_both_copies_agree():
    scenes = [{"scene_id": "s1", "span": [0.0, 12.5], "species": [dict(FZ)]},
              {"scene_id": "s2", "span": [12.5, 30.0], "species": [dict(FZ, at=20.0, dur=1.2), {"kind": "figure", "at": 1}]}]
    assert G.freeze_windows(scenes) == [(12.0, 12.5), (20.0, 21.2)]
    assert MF.freeze_windows({"scenes": scenes}) == G.freeze_windows(scenes)
    assert G.freeze_windows([]) == []


def test_punctuate_splits_a_run_into_the_beat_and_what_lies_outside_it():
    wins = [(12.0, 13.0)]
    still, beats = G.punctuate([(12.05, 0.9)], wins)
    assert still == [] and beats == [(12.05, 0.9)], "a run inside the beat is punctuation"
    still, beats = G.punctuate([(11.0, 2.0)], wins)
    assert still == [(11.0, 1.0)] and beats == [(12.0, 1.0)], "the still stretch BEFORE the beat is still a still"
    still, beats = G.punctuate([(12.5, 1.1)], wins)
    assert still == [(13.0, 0.6)], "... and one that runs on after life should have resumed"
    assert G.punctuate([(3.0, 0.9)], wins) == ([(3.0, 0.9)], [])
    assert G.punctuate([(3.0, 0.9)], []) == ([(3.0, 0.9)], []), "no beat: the runs are what they were"
    assert MF.punctuate([(11.0, 2.0)], wins) == G.punctuate([(11.0, 2.0)], wins)


def test_m18_reads_a_frozen_run_over_a_freeze_as_punctuation_not_a_still():
    """The same frames, twice: a 0.92 s identical run is a WARN on a timeline with no beat there, and a PASS that names
    the beat on one whose freeze spans it (E49 still holds everywhere else)."""
    fr = _frames([f"{i:08x}" for i in range(144)] + ["deadbeef"] * 12 + [f"{i:08x}" for i in range(200, 240)])
    t0 = fr[144]["t"]
    assert G._frozen_gate(fr).level == "WARN"
    beat = [(t0 - 0.05, t0 + 1.0)]
    g = G._frozen_gate(fr, None, None, beat)
    assert g.level == "PASS", g.message
    assert "freeze" in g.message and "punctuation" in g.message and "E99 s99" in g.message
    late = _frames([f"{i:08x}" for i in range(144)] + ["deadbeef"] * 24 + [f"{i:08x}" for i in range(200, 240)])
    assert G._frozen_gate(late, None, None, beat).level == "WARN", "a still that outlives its beat is a still"


def test_m18_reads_the_page_layer_the_same_way():
    fr = _frames([f"{i:08x}" for i in range(144)] + ["deadbeef"] * 12 + [f"{i:08x}" for i in range(200, 240)])
    t0 = fr[144]["t"]
    beat = [(t0 - 0.05, t0 + 1.0)]
    whole = _frames([f"{i:08x}" for i in range(196)])
    assert G._frozen_gate(whole, {"page": fr}, {"docks": [], "captions": []}).level == "WARN"
    g = G._frozen_gate(whole, {"page": fr}, {"docks": [], "captions": []}, beat)
    assert g.level == "PASS" and "freeze" in g.message, g.message


def test_run_passes_the_timeline_s_beats_to_m18():
    tl = json.loads((ROOT / "content/video_engine/tests/golden/sources/ledger-soak-page.timeline.json").read_text(encoding="utf-8"))
    fr = _frames([f"{i:08x}" for i in range(144)] + ["deadbeef"] * 12 + [f"{i:08x}" for i in range(200, 240)])
    t0 = fr[144]["t"]
    by = lambda gs: {g.id: g for g in gs}
    gates, _ = G.run(tl, [], {}, frames=fr)
    assert by(gates)["M18"].level == "WARN"
    sc = dict(tl["scenes"][0], species=list(tl["scenes"][0].get("species") or [])
              + [{"kind": "freeze", "at": round(t0 - 0.05, 4), "dur": 1.1, "target": {"kind": "point", "x": 0.5, "y": 0.5}}])
    gates, stats = G.run(dict(tl, scenes=[sc] + tl["scenes"][1:]), [], {}, frames=fr)
    assert by(gates)["M18"].level == "PASS", by(gates)["M18"].message


def test_the_measurement_knows_the_beat_by_name(tmp_path: Path, monkeypatch):
    """measure_frozen_frames writes the beats it read beside the runs, and keeps them OUT of `frozen_runs`."""
    tl = {"aspect": "16:9", "runtime_s": 20.0, "scenes": [{"scene_id": "s1", "span": [0.0, 20.0],
                                                             "species": [dict(FZ, at=12.0, dur=1.0)]}]}
    (tmp_path / "x.timeline.json").write_text(json.dumps(tl), encoding="utf-8")
    (tmp_path / "player.html").write_text("<html></html>", encoding="utf-8")
    fr = _frames([f"{i:08x}" for i in range(145)] + ["deadbeef"] * 12 + [f"{i:08x}" for i in range(200, 240)])
    monkeypatch.setattr(MF, "hash_frames", lambda *a, **k: fr)
    out, runs = MF.measure(tmp_path)
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert runs == [] and doc["frozen_runs"] == []
    assert doc["freeze_beats"] and doc["freeze_windows"] == [[12.0, 13.0]]


# ---- the engine ---------------------------------------------------------------------------------------------------


def test_the_engine_carries_the_module_after_the_stage_registry_and_the_life_clock_after_it():
    src = ENGINE.read_text(encoding="utf-8")
    assert "/* KINETICS:BEGIN freeze */" in src
    assert src.index("const SPECIES_PAINTERS =") < src.index("/* KINETICS:BEGIN freeze */") < src.index("const paintSpecies =")
    assert src.index("/* KINETICS:BEGIN lit_stretch */") < src.index("/* KINETICS:BEGIN freeze */"), "it reads LIT"
    assert "const FREEZE_WS = freezeWindows(" in src


@pytest.mark.parametrize("needle, why", [
    ("idleCss(idleXf(k, lifeT(t),", "every class's idle (page, pills, docks, captions) reads the life clock"),
    ("idle: idleLive,", "a stage species' own idle (the ring's breath, a held light, a chip) stops with the rest"),
    ("breath(lifeT(t), sph, { BREATH_AMP: LP_LIFE.TIP_AMP", "the live page's spark (R26-228) stops"),
    ("breath(lifeT(t), sph, { BREATH_AMP: LP_LIFE.BLOOM_AMP", "... and its glow"),
    ('idleXf(idleOf("plate", scene.world.idle), lifeT(t),', "the plate's idle and drift stop"),
    ("clamp01((lifeFrom(scene.span[0], t) - scene.span[0])", "the Ken Burns push holds"),
    ("Math.max(0, lifeFrom(scene.span[0], t) - scene.span[0])", "an ambient clip holds its frame"),
    ("Math.floor(lifeT(t) * SP.LIFE_FPS)", "the caption's boil holds"),
])
def test_every_life_on_the_stage_reads_the_life_clock(needle, why):
    assert needle in ENGINE.read_text(encoding="utf-8"), why


def test_the_card_is_a_species_card_with_its_when_pulled_from_the_compiler():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    card = cards["species:freeze"]
    assert card["token"] == "freeze" and card["when"] is None and card["serves"] == ["TURNS"]
    assert card["lives"] == {"form": "module", "path": "content/video_engine/scripts/species/freeze.mjs",
                             "symbol": "paintFreeze"}
    assert card["dials"] == {"module": "content/video_engine/scripts/species/freeze.mjs", "object": "FREEZE"}
    assert len(card["does"]) <= 240 and len(card["title"]) <= 40 and card["proof"]["golden"] == "freeze-trough"
    assert "E99 s99" in card["doctrine"]
    assert cards["species:beat_freeze"]["status"] == "declared", "the boundary move stays its own, unbuilt"


# ---- the beat, read on the served player --------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _hash(png: bytes) -> str:
    import render_baseline as RB
    return hashlib.sha256(RB.rgb_bytes(png)[1]).hexdigest()


def _quiet(tl: dict) -> dict:
    """The golden with its test captions removed: the voice keeps going through a freeze and its words keep arriving -
    this reads the STAGE's life, with nothing on it that is not the page."""
    return dict(tl, caption_pages=[], captions=[])


def _renders(tl: dict, uris: dict, aspect: str, ts: list[float]) -> list[str]:
    """Hashes at each t, in ONE page scrubbed in the given order - so a seek from anywhere is the play."""
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "freeze.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True)
                page = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1.0).new_page()
                errs: list[str] = []
                page.on("pageerror", lambda e: errs.append(str(e)))
                page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                out = [_hash(RB.frame_png(page, t, (w, h))) for t in ts]
                br.close()
        finally:
            srv.shutdown()
    assert not errs, errs
    return out


@needs_browser
def test_the_stage_stops_the_light_comes_on_and_life_resumes():
    """The golden's own beat, read as frames: without the freeze the live page is never the same frame twice; with it,
    the page holds bit-identical across the held middle of the beat (the light on, two frames 0.5 s apart), and the
    frame after the beat moves
    again. Before the beat nothing is touched: the frame is the no-freeze frame to the bit."""
    import build_golden_sources as GS
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface("freeze-trough")
    tl = _quiet(tl)
    a, d = GS.FREEZE_AT, GS.FREEZE_DUR
    ts = [a - 0.5, a + 0.25, a + d - 0.25, a + d + 0.3]
    without = dict(tl, scenes=[dict(sc, species=[s for s in sc["species"] if s["kind"] != "freeze"]) for sc in tl["scenes"]])
    w = _renders(without, uris, aspect, ts)
    f = _renders(tl, uris, aspect, ts)
    assert w[1] != w[2], "the live page lives - the control"
    assert abs((ts[2] - ts[1]) - 0.5) < 1e-9, "the golden's beat is 1.0 s: the pair sits in its held middle"
    assert f[1] == f[2], "inside the beat everything holds: two frames 0.5 s apart are one frame"
    assert f[1] != w[1], "... and the light is on"
    assert f[3] != f[2], "life resumes after the beat"
    assert f[0] == w[0], "before the beat the frame is the frame it always was"


@needs_browser
def test_the_beat_is_seek_safe():
    """A pure function of t: the frame inside the beat is the same frame whether it was reached from before the beat,
    from after it, or cold."""
    import build_golden_sources as GS
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface("freeze-trough")
    t_in = GS.FREEZE_AT + GS.FREEZE_DUR / 2
    cold = _renders(tl, uris, aspect, [t_in])[0]
    back = _renders(tl, uris, aspect, [GS.FREEZE_AT + GS.FREEZE_DUR + 2.0, t_in])[1]
    fwd = _renders(tl, uris, aspect, [GS.FREEZE_AT - 3.0, t_in])[1]
    assert cold == back == fwd

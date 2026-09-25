"""P70 T8 (was P69 T69; the Bravos harvest v2 A35 "Poof arrival under a load", R16 "The rig") - THE POOF.

A prop APPEARS at its authored place inside a ring of seeded puffs: the puffs eject radially from the prop's painted
centre over two frames, cover it, open into a ring and disperse over twelve frames (Whitaker & Halas 1981 p. 74), while
the prop springs from 0.6 to 1 inside the cover (`kinetics/stopaction.mjs` `poofXf`, its dials read off Bravos BUB
11:58.0 at 10 fps before a line was written). What this file holds it to:

  (1) THE GRAMMAR       `arrive: "poof"` is an ARRIVAL (`ARRIVALS`) of a PROP only - a card is evidence and never poofs,
                        and a page's pills never do (`PLATE_ARRIVALS_REFUSED`); both refused by name.
  (2) THE CLOCK         the gate, the walk and the cue read ONE contact: the enter + `POOF.EJECT_S`, the instant the burst
                        has left the prop - mirrored in the gate (`POOF_CONTACT_S`) and read off the module in the kit
                        (`authoring.audio.poof_contact_s`), pinned equal here.
  (3) THE SOUND         the binder pairs a `landing <n> (poof, <mass>)` cue with the poof (`WEIGHTED_ARRIVALS`), and a
                        poof names its mass explicitly - its own `mass`, else `paper` (`POOF_MASS`).
  (4) THE RING RULE     a poofed prop is still a PROP (E99 s128): a ring or callout on it takes exactly the rule a STAMPED
                        prop takes (`_dock_ring_error` has no branch of its own for either - s110's number and pointing
                        phrase, the dock on the stage at the word). s106: only truth rules refuse, and the poof adds none.
  (5) THE CARD, THE RECIPE, THE GOLDEN   `arrival:poof` (wired), `recipe:the-rig` (candidate, it composes the poof),
                        and `prop-poof` - the I-beam poofing in on "The steel kept building" (Steel and Paper H row 17).
  (6) THE FRAME         through the served player on that golden: the puff layer lies under the prop only inside the
                        puff's life, in the ground's own ink; the prop is absent while the cloud forms, appears at 0.6
                        of its size and is 1 once the ring opens (Bravos 58.6 -> 58.7); no contact shadow and no impact
                        ring; the resting hatch comes in as the puff clears (E99 s128: a prop lives in the world, bare
                        but weighted).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import recipe_walk as RW  # noqa: E402
from authoring import audio as A  # noqa: E402

STOPACTION = ROOT / "content/video_engine/scripts/kinetics/stopaction.mjs"
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CARDS = ROOT / "content/video_engine/effects/cards"
RECIPES = ROOT / "content/video_engine/effects/recipes"
SURFACE = "prop-poof"


def _node(src: str):
    r = subprocess.run(["node", "--input-type=module", "-e", src], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


@pytest.fixture(scope="module")
def poof() -> dict:
    got = _node(f"""const m = await import({json.dumps(STOPACTION.as_uri())});
      console.log(JSON.stringify(m.POOF ?? null));""")
    assert got is not None, "stopaction.mjs exports no POOF dial block"
    return got


def _scene(docks, species=()):
    return {"scene_id": "s01", "span": [0.0, 30.0], "world": {"asset_id": "plate-plain"}, "docks": list(docks),
            "species": list(species), "exit": "cut"}


POOF_DOCK = {"slide": "prop-ibeam", "enter": 10.81, "exit": 20.0, "arrive": "poof", "kind": "prop"}


# ---------------------------------------------------------------- (1) the grammar

def test_poof_is_an_arrival():
    assert "poof" in B.ARRIVALS
    assert B.dock_opts({"prop": True, "arrive": "poof"}) == {"prop": True, "arrive": "poof"}
    assert B.dock_opts({"prop": True, "arrive": "poof", "mass": "metal", "place": {"x": 0.5, "y": 0.5, "w": 0.2}})["mass"] == "metal"


def test_a_card_never_poofs_the_poof_is_a_props_arrival():
    with pytest.raises(ValueError, match=r"arrive=poof is a PROP's arrival"):
        B.dock_opts({"arrive": "poof"})
    with pytest.raises(ValueError, match=r"arrive=poof is a PROP's arrival"):
        B.dock_opts({"arrive": "poof", "cutout": True})


def test_a_pages_pills_never_poof():
    assert "poof" in B.PLATE_ARRIVALS_REFUSED
    with pytest.raises(ValueError, match=r"arrive=poof is a DOCK's arrival"):
        B.split_plate_opts("ledger:ev-x:line;arrive=poof")
    assert B.split_plate_opts("ledger:ev-x:line;arrive=throw")[1] == {"arrive": "throw"}, "a thrown pill is untouched"


def test_the_engine_reads_the_poof_arrival_and_its_region_is_the_modules():
    src = ENGINE.read_text(encoding="utf-8")
    assert 'o.arrive === "poof"' in src, "arriveOf passes the poof through the stop-action switch"
    assert "const poofXf = " in src, "the stopaction region carries poofXf (sync_kinetics --write)"
    r = subprocess.run([sys.executable, str(ROOT / "content/video_engine/scripts/sync_kinetics.py"), "--check"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr


# ---------------------------------------------------------------- (2) one clock

def test_the_gate_mirrors_the_modules_contact(poof):
    assert G.POOF_CONTACT_S == round(poof["EJECT_S"], 4), "the gate's mirror IS the module's EJECT_S"
    assert A.poof_contact_s() == round(poof["EJECT_S"], 4), "the kit reads it off the module, as it reads the stamp's"


def test_the_gate_counts_the_poofs_contact_as_a_landing_and_an_arrival():
    s = _scene([POOF_DOCK])
    contact = POOF_DOCK["enter"] + G.POOF_CONTACT_S
    assert any(abs(t - contact) < 1e-9 and n == "dock prop-ibeam poof" for t, n in G._landings(s)), G._landings(s)
    arr = G._arrivals([s])
    assert arr == [(10.81, "prop-ibeam", "poof", pytest.approx(contact))]
    assert G._arrival_events([s]) == [round(contact, 2)]
    m20 = G._cadence_gate([s])
    assert m20 is not None and "prop-ibeam poof" in m20.message and f"{G.POOF_CONTACT_S:.2f}s after its enter" in m20.message


def test_the_walk_emits_arrival_poof():
    tl = {"scenes": [_scene([dict(POOF_DOCK, mass="paper")])], "evidence": {"prop-ibeam": {"kind": "prop"}}}
    evs = [e for e in RW.events(tl) if e.cls == "arrival"]
    assert [(e.card, e.option, e.t) for e in evs] == [("arrival:poof", "paper", 10.81)]


def test_a_camera_pull_never_reads_a_poof():
    """The plan's exclusion: a camera pull on a poof is not built - the attention arrivals stay throw | land | stamp."""
    assert "poof" not in B.CAMERA_ATTN_ARRIVALS


# ---------------------------------------------------------------- (3) the sound

def test_the_kit_times_a_poofs_cue_on_its_contact(poof):
    dials = A.stop_dials()
    assert A.landing_contact(10.81, "poof", dials) == pytest.approx(10.81 + round(poof["EJECT_S"], 4))
    assert A.landing_contact(10.81, "land", dials) == pytest.approx(10.81 + dials["ANTIC_S"] + dials["DROP_S"]), "a land is untouched"


def test_a_poof_is_a_weighted_arrival_with_its_mass_named():
    assert "poof" in A.WEIGHTED_ARRIVALS and A.POOF == "poof"
    assert A.POOF_MASS == "paper"
    assert A.arrival_mass({"arrive": "poof"}) == "paper"
    assert A.arrival_mass({"arrive": "poof", "mass": "metal"}) == "metal"
    assert A.arrival_mass({"arrive": "stamp"}) == "ink" and A.arrival_mass({"arrive": "throw"}) == "paper", "the others unchanged"


def test_the_poofs_cue_starts_at_e81s_reference_nine_db_under_the_voice():
    """E81 apply 1 (the starting reference for every video's foley and accents): 8-10 dB under the voice, measured to
    measured - the midpoint, 9 dB. The poof's whoosh (fs-whoosh-1-706679.mp3, -14.0 LUFS integrated) under the H take
    (-28.1 LUFS; logs/level.log) starts at gain 0.07; the shared landing gain (0.12) is not this function's."""
    assert A.E81_UNDER_DB == 9.0
    assert A.e81_gain(-28.1, -14.0) == 0.07
    import math
    for vo, cue in ((-28.1, -14.0), (-20.0, -14.4), (-16.0, -9.5)):
        assert 20 * math.log10(A.e81_gain(vo, cue)) + cue == pytest.approx(vo - 9.0, abs=0.01), (vo, cue)
    assert A.e81_gain(-28.1, -14.0, under_db=8.0) > A.e81_gain(-28.1, -14.0) > A.e81_gain(-28.1, -14.0, under_db=10.0)
    with pytest.raises(ValueError, match="8-10 dB"):
        A.e81_gain(-28.1, -14.0, under_db=4.3)


def test_fired_plays_the_poof_as_a_landing_on_its_contact():
    tl = {"scenes": [_scene([POOF_DOCK])], "evidence": {}}
    lands = [f for f in A.fired(tl) if f["kind"] == "landing"]
    assert lands == [{"kind": "landing", "what": "poof", "at": round(10.81 + A.poof_contact_s(), 2),
                      "until": round(10.81 + A.poof_contact_s(), 2), "scene": "s01", "ref": "prop-ibeam", "mass": "paper"}]


def test_a_row_names_its_poof_among_the_weighted_arrivals():
    row = (0.0, 30.0, "plate-plain", "", [("prop-ibeam", 0, 10.81, 20.0, {"prop": True, "arrive": "poof"})], "cut")
    assert [o["arrive"] for _d, o in A.row_arrivals(row)] == ["poof"]


# ---------------------------------------------------------------- (4) the truth rule

def _ring(label, **kw):
    return {"kind": "callout", "at": 10.9, "dur": 1.5, "label": label, "points": "The steel",
            "target": {"kind": "dock", "dock": "prop-ibeam"}, **kw}


WORDS = [{"w": "The", "start_s": 10.70, "end_s": 10.81}, {"w": "steel", "start_s": 10.81, "end_s": 11.20},
         {"w": "kept", "start_s": 11.20, "end_s": 11.51}, {"w": "building.", "start_s": 11.51, "end_s": 12.30}]


def _ring_on(arrive: str, label: str):
    """dock_ring_targets on ONE ring over the same prop arriving by `arrive`: (species, notes) or the refusal's text."""
    try:
        return B.dock_ring_targets([_ring(label)], [dict(POOF_DOCK, arrive=arrive)], {"words": WORDS}, "row 17")
    except ValueError as exc:
        return str(exc)


def test_a_ring_with_its_number_on_a_poofed_prop_plays_as_on_a_stamped_prop():
    """s106 / s128: the poof adds no refusal of its own - the ring that plays on a stamped prop plays on a poofed one."""
    got = _ring_on("poof", "$822B")
    assert got == _ring_on("stamp", "$822B"), got
    assert not isinstance(got, str) and got[0][0]["label"] == "$822B", got


def test_every_ring_on_a_poofed_prop_is_judged_as_on_a_stamped_prop():
    """... and every other case reads the same, word for word: a ring before the prop has arrived, after it has left,
    off its pointing phrase - `_dock_ring_error` has no branch for either arrival (s110's own number check is the entry's,
    `_validate_dock_ring`, which never sees the dock's arrival)."""
    for at, label in ((10.5, "$822B"), (25.0, "$822B"), (11.9, "$822B"), (10.9, "the steel")):
        rings = lambda arrive: _ring_on_at(arrive, label, at)  # noqa: E731
        assert rings("poof") == rings("stamp"), (at, label, rings("poof"))


def _ring_on_at(arrive: str, label: str, at: float):
    try:
        return B.dock_ring_targets([dict(_ring(label), at=at)], [dict(POOF_DOCK, arrive=arrive)], {"words": WORDS}, "row 17")
    except ValueError as exc:
        return str(exc)


# ---------------------------------------------------------------- (5) the card, the recipe, the golden

def _card(axis: str, cid: str) -> dict:
    return next(c for c in json.loads((CARDS / f"{axis}.json").read_text(encoding="utf-8"))["cards"] if c["id"] == cid)


def test_the_arrival_card_is_wired_on_the_module():
    c = _card("arrival", "arrival:poof")
    assert c["token"] == "poof" and c["status"] == "wired"
    assert c["lives"] == {**c["lives"], "form": "module", "path": "content/video_engine/scripts/kinetics/stopaction.mjs",
                          "symbol": "poofXf"}
    assert c["dials"] == {"module": "content/video_engine/scripts/kinetics/stopaction.mjs", "object": "POOF"}
    assert c["proof"]["golden"] == SURFACE and c["proof"]["test"] == "content/video_engine/tests/test_poof_arrival.py"
    for d in ("E99 s128", "E99 s106", "E99 s116", "E81"):
        assert d in c["doctrine"], d
    assert 10 <= len(c["does"]) <= 240


def test_the_rig_is_a_candidate_recipe_that_composes_the_poof():
    r = json.loads((RECIPES / "the-rig.json").read_text(encoding="utf-8"))
    assert r["id"] == "recipe:the-rig" and r["status"] == "candidate"
    cards = [m["card"] for m in r["members"]]
    assert "arrival:poof" in cards and "dock_kind:prop" in cards and "dock_option:place" in cards
    assert cards.index("arrival:poof") > min(cards.index(c) for c in ("arrival:land", "arrival:stamp") if c in cards), \
        "the support lands first, the load poofs onto it"


def test_the_golden_is_registered():
    import build_golden_sources as GS
    assert SURFACE in GS.SURFACES and SURFACE in GS.FRAME_T
    text = (ROOT / "content/video_engine/tests/test_golden_frames.py").read_text(encoding="utf-8")
    assert f'"{SURFACE}"' in text


# ---------------------------------------------------------------- (6) the frame, through the served player

PROBE = """() => {
  const el = document.querySelector('.dock[data-slide="ev-prop-ibeam"]');
  const pf = document.querySelector('.dock-poof');
  const ring = document.querySelector('.dock-ring');
  const contact = document.querySelector('.dock-contact');
  const hatch = document.querySelector('.dock-hatch');
  const circles = pf ? [...pf.querySelectorAll('circle')] : [];
  return {
    transform: el ? el.style.transform : null, opacity: el ? +el.style.opacity : null,
    puff: pf ? { shown: pf.style.display !== 'none' && +(pf.style.opacity || 1) > 0, n: circles.length,
                 under: !!(el && el.compareDocumentPosition(pf) & Node.DOCUMENT_POSITION_PRECEDING),
                 fills: [...new Set(circles.map((c) => c.getAttribute('fill')))],
                 alpha: +(pf.style.opacity || 0), circleAlpha: circles.some((c) => c.hasAttribute('fill-opacity')) } : null,
    ring: ring ? +ring.style.opacity : null, contact: contact ? +contact.style.opacity : null,
    hatch: hatch ? +hatch.style.opacity : null };
}"""


@pytest.fixture(scope="module")
def reads(poof):
    import render_baseline as RB
    import build_golden_sources as GS
    import served_player as SP  # R26-351 (P72 T9): the one guarded Playwright start
    import tempfile
    tl, uris, _t, aspect = RB.load_surface(SURFACE)
    enter = GS.POOF_ENTER
    ts = {"before": enter - 0.05, "burst": enter + 0.04, "cover": enter + poof["COVER_S"], "open": enter + poof["OPEN_S"] + 0.05,
          "late": enter + poof["LIFE_S"] - 0.05, "gone": enter + poof["LIFE_S"] + 0.1, "rest": enter + 1.6}
    out, errors = {}, []
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "p.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        w, h = RB.STAGE[aspect]
        with SP.served(html, w, h) as (page, errs):
            for k, t in ts.items():
                RB.frame_png(page, t, (w, h))
                out[k] = page.evaluate(PROBE)
            errors.extend(errs)
    out["errors"] = errors
    return out


def _scale(transform: str) -> float:
    import re
    m = re.search(r"scale\(([0-9.]+)\)", transform or "")
    return float(m.group(1)) if m else 1.0


def test_the_player_draws_the_puff_over_the_prop_only_inside_its_life(reads, poof):
    assert reads["errors"] == []
    assert reads["before"]["puff"] is None or not reads["before"]["puff"]["shown"], "nothing before the enter"
    for k in ("burst", "cover", "open", "late"):
        p = reads[k]["puff"]
        assert p and p["shown"] and p["n"] == 2 * poof["N"], (k, p)   # a shade and a body per lobe
        assert p["under"], "the puff is laid UNDER the prop: absent while the cloud forms, it stands in front as it opens"
    assert not reads["gone"]["puff"]["shown"] and not reads["rest"]["puff"]["shown"], "a puff is never held"


def test_the_cloud_fades_as_one_shape_never_circle_by_circle(reads):
    """Per-circle alpha stacks at every overlap and the lobes read as bubbles (the first frame read, 2026-09-25): the fade
    is the layer's opacity - full through the cover, falling after it."""
    assert not any(reads[k]["puff"]["circleAlpha"] for k in ("burst", "cover", "open", "late"))
    assert reads["cover"]["puff"]["alpha"] == 1.0
    assert 0 < reads["late"]["puff"]["alpha"] < reads["open"]["puff"]["alpha"] < 1.0


def test_the_puff_takes_the_grounds_ink_chalk_on_the_dark_plate(reads):
    """The impact ring's own rule (P70 T1c): the ink holding the more contrast on the MEASURED ground - chalk (the
    template's --lp-chalk, STAMP_RING_INK.CHALK) on the golden's charcoal plate, as Bravos's puff is white on its void."""
    fills = [f.upper() for f in reads["cover"]["puff"]["fills"]]
    assert "#F2F2F2" in fills, fills


def test_the_prop_is_absent_while_the_cloud_forms_then_springs_from_0_6_to_1(reads, poof):
    assert reads["burst"]["opacity"] == 0, "no prop while the cloud forms"
    assert _scale(reads["burst"]["transform"]) == pytest.approx(poof["POP_FROM"])
    assert _scale(reads["open"]["transform"]) == pytest.approx(1.0, abs=0.01)
    assert _scale(reads["rest"]["transform"]) == 1.0


def test_no_contact_shadow_and_no_impact_ring_a_poof_does_not_fall(reads):
    for k in ("burst", "cover", "open", "rest"):
        assert not reads[k]["contact"], (k, reads[k]["contact"])
        assert not reads[k]["ring"], (k, reads[k]["ring"])


def test_the_resting_hatch_comes_in_as_the_puff_clears(reads):
    """The hatch's full weight on a light-or-plate ground is PROP_SHADOW.ALPHA.ground (T6b's dial), read off the module."""
    full = _node(f"""const m = await import({json.dumps(STOPACTION.as_uri())});
      console.log(JSON.stringify(m.PROP_SHADOW.ALPHA.ground));""")
    assert (reads["burst"]["hatch"] or 0) < 0.2 * full, "no resting shadow under a thing that has just appeared"
    assert 0 < (reads["cover"]["hatch"] or 0) < (reads["late"]["hatch"] or 0) < full, "it comes in over the puff's life"
    assert reads["rest"]["hatch"] == pytest.approx(full, abs=1e-3), "E99 s128: bare but weighted, on its resting hatch"

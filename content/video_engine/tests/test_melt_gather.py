"""P61 T6 / E99 s2 - THE MELT GATHERS TO ONE DENSE, HEAVY, VIBRATING POINT.

The operator, `docs/portable/OPERATOR-RULINGS.md:2912-2920`:

    "that ball doesn't read as dense/heavy to me, and the melt and melt splash is ugly. for the melt,
    i expect almost like our swirl effect, i don't want the melt to be blur or a wipe, it should be
    closer to the swirl except for instead of a whirlpool, vortexing around a single point, it
    collects and amasses into a single point, that single point should be dense, heavy, and vibrating
    with energy, and when it splashes, it should splash into a scenic, high-resolution world plate or
    fully assembled chart."

What this file pins:

  1. THE TOKEN     `melt:gather` parses the same way on BOTH sides (`build_scene_timeline_f._melt_parts`
                   and `species/melt.mjs meltOpts`), composes with `weight`, its material, a depth, a
                   length and every ending, and an unknown token is refused BY NAME.
  2. THE DEFAULT   an exit string with no `gather` renders today's melt BYTE-IDENTICAL - the two flag-off
                   surfaces here, and every melt* golden in `test_golden_frames.py`.
  3. THE GATHER    the page vortex's own map (doc 29 s9.31, `species/spiral.mjs lpVortex`) aimed at ONE
                   point: a convergence that falls monotonically to the point, dial for dial the same
                   terms as `LP_RETRACT`, with the one difference the ruling asks for - the ink AMASSES
                   (`G_KEEP`) instead of draining to nothing.
  4. NO BLUR, NO   `meltBlur` is exactly 0 across the window, the run is 0, no mask is written - and on
     WIPE         the rendered frames the ink MOVES: its spread about the point shrinks while its peak
                   contrast does not fall. A blur or a wipe loses contrast in place; this does not.
  5. THE POINT     dense and heavy (T5's material rides it) and VIBRATING on drop.mjs's OWN idle - the
                   FLOOR its decay never takes (E49) - lifted by the amplitude dial `G_VIB`.
  6. THE SEEK      two seeks of the same instant are the same bytes.

E99 s34: `melt:gather` is authored on this slice's own golden and NOWHERE near the approved Japan short.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

MELT_MJS = ROOT / "content/video_engine/scripts/species/melt.mjs"
DROP_MJS = ROOT / "content/video_engine/scripts/kinetics/drop.mjs"
SPIRAL_MJS = ROOT / "content/video_engine/scripts/species/spiral.mjs"
FRAMES = ROOT / "content/video_engine/tests/golden/frames"

GATHER_EXIT = "melt:gather:weight:splash:plate"
# the melt surfaces that never ask for the gather: not one byte of these may move
FLAG_OFF_SURFACES = ["melt-page@proof-015", "melt-plate"]
# the caption band both gather frames carry identically - not the melt's ink, so the probe cuts it out
CAPTION_BAND = (415, 535)


def _node(expr: str):
    """Evaluate an expression against the three modules and return its JSON."""
    src = (
        f'import {{ MELT, meltOpts, meltBlur, meltState, meltGatherAt, meltGatherSpread, meltGatherCore, '
        f'meltGatherCss, meltGatherSvg, meltVibGain, meltVibFloor, meltBallRing }} '
        f'from {json.dumps(MELT_MJS.as_uri())};\n'
        f'import {{ DROP, dropRing }} from {json.dumps(DROP_MJS.as_uri())};\n'
        f'import {{ LP_RETRACT, lpVortex }} from {json.dumps(SPIRAL_MJS.as_uri())};\n'
        f'console.log(JSON.stringify(({expr})));\n'
    )
    out = subprocess.run([("node.exe" if sys.platform == "win32" else "node"), "--input-type=module", "-e", src],
                         capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


# ---- 1. THE TOKEN, on both sides -----------------------------------------------------------------

def test_the_compiler_reads_gather_beside_weight_and_every_ending() -> None:
    """A PHASE token, in any order after the name, composable with the endings, the material, a depth
    and a length. `melt_gather` is the one accessor, `_melt_parts` the one place it is read."""
    assert B.melt_gather("melt:gather") is True
    assert B.melt_gather("melt:gather:splash:plate") is True
    assert B.melt_gather("melt:splash:chart:gather") is True
    assert B.melt_gather(GATHER_EXIT) is True
    assert B.melt_gather("melt:weight:metal:gather:depth=1.15:2.4") is True
    assert B.melt_gather("melt") is False and B.melt_gather("melt:weight") is False
    assert B.melt_gather("dip") is False and B.melt_gather(None) is False
    # the phases do not change anything else about the exit
    assert B.melt_ending("melt:gather:splash:plate") == "splash:plate"
    assert B.melt_ending("melt:gather") == "throw"
    assert B.melt_depth("melt:gather:depth=1.15") == 1.15
    assert B.parse_exit("melt:gather:2.4") == ("melt:gather:2.4", 2.4)


def test_the_weight_lookahead_never_eats_the_gather_as_a_material() -> None:
    """`melt:weight:gather` is a weight phase AND a gather, not a ball made of `gather`."""
    assert B.melt_gather("melt:weight:gather") is True
    assert B.parse_exit("melt:weight:gather") == ("melt:weight:gather", None)
    player = _node('meltOpts("melt:weight:gather")')
    assert player["weight"] is True and player["gather"] is True and player["wmass"] == "metal"


def test_an_unknown_token_is_refused_by_name_on_both_sides() -> None:
    """A typo in a shot table is a refusal that names the token, never a silent default."""
    for bad in ("melt:gathers", "melt:gathering", "melt:vortex", "melt:swirl"):
        with pytest.raises(ValueError) as exc:
            B.parse_exit(bad)
        msg = str(exc.value)
        assert bad.split(":")[1] in msg, msg
        assert "phase (gather, weight)" in msg, "the refusal names the phases it does have"
    assert _node('(() => { try { meltOpts("melt:gathers"); return "no refusal"; } '
                 'catch (e) { return e.message; } })()').startswith("melt: gathers is neither")
    with pytest.raises(ValueError, match="is not a material"):
        B.parse_exit("melt:weight:gatherr")


def test_the_two_sides_agree_token_for_token() -> None:
    """The compiler and the player read ONE grammar; test_transitions_e47 pins the pair for the rest."""
    cases = ["melt", "melt:gather", "melt:gather:splash:plate", "melt:splash:chart:gather",
             GATHER_EXIT, "melt:gather:weight:ink:3.0", "melt:weight:gather:depth=1.15"]
    player = _node("%s.map((s) => { const o = meltOpts(s); return [o.gather, o.ending, o.weight]; })"
                   % json.dumps(cases))
    for s, (gather, ending, weight) in zip(cases, player):
        assert gather == B.melt_gather(s), s
        assert ending == B.melt_ending(s), s
        assert weight == ("weight" in s.split(":")), s


def test_the_gathers_own_length_is_one_dial_written_twice() -> None:
    """MELT.G_S and build_scene_timeline_f.MELT_G_S, as MELT.S / MELT_S are - and a row that declares
    its own length gets exactly that length, gather or not."""
    dials = _node("({ G_S: MELT.G_S, S: MELT.S, W_S: MELT.W_S, "
                  "plain: meltOpts('melt').secs, gathered: meltOpts('melt:gather').secs, "
                  "both: meltOpts('melt:gather:weight').secs, said: meltOpts('melt:gather:2.0').secs })")
    assert dials["G_S"] == B.MELT_G_S == 0.9
    assert dials["plain"] == B.MELT_S, "the default window is untouched"
    assert dials["gathered"] == pytest.approx(dials["S"] + dials["G_S"])
    assert dials["both"] == pytest.approx(dials["S"] + dials["W_S"] + dials["G_S"])
    assert dials["said"] == 2.0, "a declared length wins"


# ---- 2. THE DEFAULT is the melt that shipped ------------------------------------------------------

def test_a_melt_without_the_token_parses_to_the_tuple_it_always_did() -> None:
    """The plan's own test: `parse_exit` is unchanged for every melt on the record."""
    assert B.parse_exit("melt") == ("melt", None)
    assert B.parse_exit("melt:splash:chart") == ("melt:splash:chart", None)
    assert B.parse_exit("melt:throw") == ("melt:throw", None)
    assert B.parse_exit("melt:1.2:splash:plate") == ("melt:1.2:splash:plate", 1.2)
    assert B.parse_exit("melt:weight:metal") == ("melt:weight:metal", None)
    plain = _node('meltOpts("melt")')
    assert plain["gather"] is False and plain["secs"] == B.MELT_S


@pytest.mark.parametrize("surface", FLAG_OFF_SURFACES)
def test_a_melt_without_the_token_renders_byte_identical(surface: str) -> None:
    """E45 and the approved Japan short are protected by BYTE-IDENTITY, not by intent. The rest of the
    melt* goldens ride test_golden_frames.py; these two are the sag and the splash, this slice's own
    two windows, rendered here so the refusal is local to the change."""
    png = RB.render_surface(surface)
    assert png == (FRAMES / f"{surface}.png").read_bytes(), f"{surface} moved"


def test_no_gather_state_key_is_written_for_a_melt_that_did_not_ask() -> None:
    """`st.gather` is null for every melt on the record, which is what keeps the painter's DOM the one
    that shipped: no particles are measured, no transform is written, no mask is skipped."""
    st = _node('(() => { const o = meltOpts("melt"); const rect = { x: 100, y: 100, w: 800, h: 400 }; '
               'return [0.1, 0.4, 0.8].map((u) => { const s = meltState(0, u * o.secs, '
               'Object.assign({ rect }, o), (k) => 0.5); return [s.gather, s.mass, s.phase]; }); })()')
    assert st == [[None, False, "melt"], [None, False, "ball"], [None, False, "fly"]]


# ---- 3. THE GATHER is the page vortex, aimed at ONE point -----------------------------------------

VORTEX_PAIRS = [("G_TURNS", "TURNS"), ("G_LAG", "LAG"), ("G_ALPHA", "ALPHA"), ("G_R_FALL", "R_FALL"),
                ("G_CORE_BASE", "CORE_BASE"), ("G_CORE_GAIN", "CORE_GAIN"), ("G_CORE_FALL", "CORE_FALL"),
                ("G_SHRINK", "SHRINK")]


def test_every_gather_dial_is_the_page_vortexs_own_number() -> None:
    """melt.mjs cannot IMPORT spiral.mjs - sync_kinetics refuses an import whose region is later in the
    engine, and spiral's region is after melt's - so the terms are written twice and pinned here. Drift
    between them is what this test exists to catch."""
    pairs = _node("%s.map(([g, s]) => [MELT[g], LP_RETRACT[s]])" % json.dumps(VORTEX_PAIRS))
    for (gname, sname), (gv, sv) in zip(VORTEX_PAIRS, pairs):
        assert gv == sv, f"MELT.{gname} ({gv}) has drifted from LP_RETRACT.{sname} ({sv})"


def test_the_map_is_the_vortexs_five_terms_and_differs_only_in_the_ending() -> None:
    """At the same u, about the same point, the gather's pose IS the retract's - the same radius, the
    same angle - until the shrink, where a retract goes to nothing and a gather stops at G_KEEP."""
    got = _node("""(() => {
      const c = [900, 500], R = 700, out = [];
      for (const u of [0.1, 0.35, 0.6, 0.85]) for (const p of [[300, 260], [1400, 800], [905, 505]]) {
        const g = meltGatherAt(p[0], p[1], c, R, u), v = lpVortex(p[0], p[1], { x: c[0], y: c[1] }, R, u);
        out.push([g.x - v.x, g.y - v.y, g.th - v.th, g.sx, v.sx]);
      }
      return out; })()""")
    for dx, dy, dth, gsx, vsx in got:
        assert abs(dx) < 1e-6 and abs(dy) < 1e-6, "the gather's PATH is the vortex's path"
        assert abs(dth) < 1e-9, "and so is its whirl"
        assert gsx >= vsx - 1e-9, "the gather's particle never shrinks BELOW the retract's"


def test_the_particle_amasses_instead_of_vanishing() -> None:
    """The whole of the ruling, in one number: at u = 1 the retract's particle is gone (scale 0) and the
    gather's is still ink on the frame, at G_KEEP of itself, sitting ON the point."""
    got = _node("""(() => {
      const c = [900, 500], R = 700, p = [300, 260];
      const g = meltGatherAt(p[0], p[1], c, R, 1), v = lpVortex(p[0], p[1], { x: c[0], y: c[1] }, R, 1);
      return { gs: g.sx * g.sy, vs: v.sx * v.sy, keep: MELT.G_KEEP,
               gx: g.x - c[0], gy: g.y - c[1] }; })()""")
    assert got["vs"] == pytest.approx(0, abs=1e-9), "the retract drains to nothing"
    assert got["gs"] == pytest.approx(got["keep"] ** 2, rel=1e-6), "the gather keeps G_KEEP of itself"
    assert abs(got["gx"]) < 1e-6 and abs(got["gy"]) < 1e-6, "and it is ON the point"


def test_the_convergence_falls_monotonically_to_the_point() -> None:
    """"it collects and amasses into a single point" - measurable. The RMS distance of the marks from
    the point falls at every step of the window and reaches the point at the end. A blur cannot move
    this number; only travel can."""
    spread = _node("""(() => {
      const c = [900, 500], R = 700, homes = [];
      for (let i = 0; i < 60; i++) homes.push([900 + Math.cos(i * 0.7) * (120 + i * 9),
                                               500 + Math.sin(i * 1.3) * (80 + i * 6)]);
      const out = [];
      for (let i = 0; i <= 20; i++) out.push(meltGatherSpread(homes, c, R, i / 20));
      return out; })()""")
    assert spread[0] > 100, "the marks start spread across the page"
    for a, b in zip(spread, spread[1:]):
        assert b <= a + 1e-9, f"the spread rose: {a} -> {b}"
    assert spread[-1] == pytest.approx(0, abs=1e-6), "every mark is at the point at the end"
    assert spread[len(spread) // 2] < spread[0] * 0.9, "and it is well under way at the midpoint"


def test_the_drain_takes_the_nearest_ink_first_and_the_core_turns_more_than_the_rim() -> None:
    """s9.31's two signatures: the LAG by normalised radius, and the DIFFERENTIAL whirl that makes arms
    instead of a wheel (the core about four times the rim)."""
    got = _node("""(() => {
      const c = [0, 0], R = 1000, u = 0.4;
      const near = meltGatherAt(100, 0, c, R, u), far = meltGatherAt(1000, 0, c, R, u);
      return { nearUi: near.ui, farUi: far.ui, nearTh: near.th, farTh: far.th,
               ratio: near.th / Math.max(1e-9, far.th) }; })()""")
    assert got["nearUi"] > got["farUi"], "the point takes the ink nearest it first"
    assert got["farUi"] == pytest.approx(0.2, abs=1e-9), "(u - LAG) / (1 - LAG) at the rim"
    assert got["ratio"] > 3.5, "the core turns about four times the rim - arms, not a wheel"


# ---- 4. NO BLUR, NO WIPE --------------------------------------------------------------------------

def test_the_blur_and_the_run_are_exactly_zero_across_the_window() -> None:
    """"i don't want the melt to be blur or a wipe". The sag's gooey threshold existed to FUSE marks in
    place; a gather moves them, so there is nothing to fuse and nothing to blur."""
    got = _node("""(() => {
      const o = meltOpts("melt:gather"), rect = { x: 120, y: 120, w: 900, h: 460 }, out = [];
      for (let i = 0; i <= 40; i++) {
        const u = i / 40, st = meltState(0, u * o.secs, Object.assign({ rect }, o), (k) => 0.5);
        out.push([meltBlur(u, o), st.blur, st.inkBlur, st.run, st.phase]);
      }
      return out; })()""")
    for blur, stblur, inkblur, run, phase in got:
        assert blur == 0, f"meltBlur is not 0 in phase {phase}"
        assert stblur == 0 and inkblur == 0, f"a blur is written in phase {phase}"
        if phase == "melt":
            assert run == 0, "the sag's RUN is the smear the ruling refuses"
    plain = _node("[0.1, 0.4].map((u) => meltBlur(u, meltOpts('melt')))")
    assert plain[0] > 0, "a melt that did NOT ask for the gather still blurs exactly as it did"


def test_the_painter_writes_no_mask_and_no_squeeze_under_a_gather() -> None:
    """A mask would clip a mark where it no longer is; a squeeze is the compile, not the travel. Both
    are branched on `st.gather` in the ONE painter, and the else arm is the code that shipped."""
    src = MELT_MJS.read_text(encoding="utf-8")
    block = src[src.index("const ink = m.ink, gth = st.gather"):src.index("/* THE WORDS:")]
    assert "if (gth) {" in block and "meltGatherWrite(m.parts" in block
    assert 'ink.style.mask = "url(#" + id + "m)"' in block, "the else arm is unchanged"
    assert "st.scale !== 1 && !gth" in block, "no squeeze under a gather"
    assert re.search(r"if \(P\.gather\) return 0;", src), "meltBlur's own early-out"


def test_on_the_rendered_frames_the_ink_MOVES_and_does_not_lose_contrast_in_place() -> None:
    """THE PROBE the acceptance asks for, read off the pinned frames: between the gather's midpoint and
    the point, the ink's spread about the point SHRINKS (it travelled) while its peak contrast against
    the board does NOT fall (it did not fade or blur away where it stood)."""
    from PIL import Image
    mid = Image.open(FRAMES / "melt-gather.png").convert("RGB")
    pt = Image.open(FRAMES / "melt-gather@proof-point.png").convert("RGB")
    assert mid.size == pt.size

    def ink(img):
        """Every pixel far enough from the BOARD's own charcoal to be ink. The caption band both frames
        carry identically is cut out (it is not the melt's ink), and so is the stage's outer margin."""
        w, h = img.size
        q = img.load()
        board = q[1700, 200]            # empty board, top right - the melt never reaches it
        out = []
        for y in range(80, h - 80, 3):
            if CAPTION_BAND[0] <= y <= CAPTION_BAND[1]:
                continue
            for x in range(80, w - 80, 3):
                r, g, b = q[x, y]
                d = abs(r - board[0]) + abs(g - board[1]) + abs(b - board[2])
                if d > 60:
                    out.append((x, y, d))
        return out

    a, b = ink(mid), ink(pt)
    assert len(a) > 400 and len(b) > 400, "both frames carry ink"

    def spread(pts):
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        return math.sqrt(sum((p[0] - cx) ** 2 + (p[1] - cy) ** 2 for p in pts) / len(pts))

    sa, sb = spread(a), spread(b)
    assert sb < sa * 0.5, f"the ink did not travel: spread {sa:.1f} -> {sb:.1f} px"
    assert len(b) < len(a), "and it concentrated - a blur spreads ink over MORE pixels, never fewer"
    peak_a = sorted(p[2] for p in a)[int(len(a) * 0.995)]
    peak_b = sorted(p[2] for p in b)[int(len(b) * 0.995)]
    assert peak_b >= peak_a * 0.9, \
        f"the ink lost contrast in place (a blur or a fade): peak {peak_a} -> {peak_b}"


# ---- 5. THE POINT: dense, heavy, and vibrating ----------------------------------------------------

def test_the_point_opens_under_the_arriving_ink_and_wears_the_material() -> None:
    """It is T5's ball: `st.mass` is what the three material overlays ride, and a gather turns it on
    whether or not the row also asked for `weight` - the point IS the ball."""
    got = _node("""(() => {
      const o = meltOpts("melt:gather"), rect = { x: 120, y: 120, w: 900, h: 460 }, out = [];
      for (const k of [0.2, 0.5, MELT.G_CORE_AT + 0.01, 0.8, 0.99]) {
        const u = k * MELT.MELT_END, st = meltState(0, u * o.secs, Object.assign({ rect }, o), (x) => 0.5);
        out.push([st.phase, st.mass, st.bodyAlpha, st.body.length > 0, st.hl ? 1 : 0]);
      }
      return out; })()""")
    assert [g[0] for g in got] == ["melt"] * 5, "all five instants are inside the gather"
    assert got[0][1] is False and got[1][1] is False, "no point before G_CORE_AT"
    assert all(g[1] is True for g in got[2:]), "the point wears the material from the frame it exists"
    alphas = [g[2] for g in got]
    assert alphas[0] == 0 and alphas[-1] == pytest.approx(1, abs=5e-3), "opaque by the handover"
    assert all(b >= a - 1e-9 for a, b in zip(alphas, alphas[1:])), "it only ever grows"
    assert alphas[2] < alphas[3] < alphas[4], "it grows under the arriving ink"
    assert got[-1][3] is True and got[-1][4] == 1, "a ring and a specular spot"


def test_the_vibration_is_drops_own_idle_at_an_amplitude_dial() -> None:
    """E49, nothing ever goes truly still - and NOT a new motion law: the FLOOR kinetics/drop.mjs's decay
    can never take away, times G_VIB while the point collects, settling back to the resting floor over
    G_VIB_FALL of the ball phase."""
    got = _node("""({ floorOn: meltVibFloor(1), floorOff: meltVibFloor(0), base: DROP.FLOOR,
                      vib: MELT.G_VIB, fall: MELT.G_VIB_FALL,
                      gather: meltVibGain('melt', 0.5, { gather: true }),
                      ball0: meltVibGain('ball', 0, { gather: true }),
                      ballMid: meltVibGain('ball', MELT.G_VIB_FALL / 2, { gather: true }),
                      ballEnd: meltVibGain('ball', MELT.G_VIB_FALL, { gather: true }),
                      none: meltVibGain('melt', 0.5, {}) })""")
    assert got["vib"] > 1, "an amplitude dial, above the resting floor"
    assert got["floorOn"] == pytest.approx([v * got["vib"] for v in got["base"]])
    assert got["floorOff"] == pytest.approx(got["base"]), "off the gain it is drop.mjs's own floor"
    assert got["gather"] == 1 and got["ball0"] == 1
    assert 0 < got["ballMid"] < 1 and got["ballEnd"] == 0, "it settles across G_VIB_FALL"
    assert got["none"] == 0, "a melt that did not ask for a gather never lifts the floor"


def test_the_point_is_never_a_still_circle() -> None:
    """The ring is out of round at every instant, and it is a DIFFERENT ring a frame later: the point is
    wriggling to contain itself, which is what "vibrating with energy" asks for."""
    got = _node("""(() => {
      const o = Object.assign({}, meltOpts("melt:gather"), { vib: 1 });
      const ring = (t) => meltBallRing([0, 0], 60, Object.assign({}, o, { te: t }));
      const rad = (pts) => pts.map((p) => Math.hypot(p[0], p[1]));
      const a = rad(ring(0.20)), b = rad(ring(0.40));
      const dev = (r) => (Math.max(...r) - Math.min(...r)) / 60;
      const moved = a.reduce((s, v, i) => s + Math.abs(v - b[i]), 0) / a.length;
      const flat = rad(meltBallRing([0, 0], 60, Object.assign({}, meltOpts("melt"), { te: 0.2 })));
      return { devA: dev(a), devB: dev(b), moved, devFlat: dev(flat) }; })()""")
    assert got["devFlat"] == pytest.approx(0, abs=1e-9), "a melt without the token is still a plain circle"
    assert got["devA"] > 0.02 and got["devB"] > 0.02, "the gathered point is out of round at every instant"
    assert got["moved"] > 0.2, "and it is a different ring a frame later (E49)"


# ---- 6. THE SEEK ----------------------------------------------------------------------------------

def test_the_state_is_a_pure_function_of_t() -> None:
    """The same t twice is the same object - a scrubbed frame is the played frame, and the gather's map
    is closed-form because a seek renderer may not integrate."""
    got = _node("""(() => {
      const o = meltOpts("melt:gather:weight:splash:plate"), rect = { x: 120, y: 120, w: 900, h: 460 };
      const at = (t) => JSON.stringify(meltState(0, t, Object.assign({ rect }, o), (k) => 0.5));
      return [0.3, 1.1, 2.0, 3.2].map((t) => at(t) === at(t)); })()""")
    assert got == [True, True, True, True]


def test_two_seeks_of_the_same_instant_are_the_same_bytes() -> None:
    """The particles' homes are measured ONCE, at the boundary, and the map is pure - so a cold render
    of the gather's midpoint is the warm one, to the byte."""
    first = RB.render_surface("melt-gather")
    second = RB.render_surface("melt-gather")
    assert first == second
    assert first == (FRAMES / "melt-gather.png").read_bytes(), "and it is the pinned golden"


# ---- 7. THE SPLASH LANDS IN A SCENIC, HIGH-RESOLUTION WORLD PLATE (proof A) -----------------------

def test_the_golden_splashes_into_the_committed_dock_plate_with_no_cut() -> None:
    """"it should splash into a scenic, high-resolution world plate". The golden's incoming world is the
    committed Tokyo customs dock plate - not `melt-plate`'s 320x180 synthetic stand-in - and the exit IS
    the transition into it (E47): there is no cut anywhere in the window."""
    sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
    import build_golden_sources as G

    tl, uris = G.melt_gather()
    s1, s2 = tl["scenes"]
    assert s2["exit"] == GATHER_EXIT and B.melt_gather(s2["exit"]) is True
    assert B.melt_ending(s2["exit"]) == "splash:plate"
    assert s2["world"]["asset_id"] == "plate-dock", "the world the splash paints"
    assert uris["plate-dock"] == B.data_uri(G.DOCK_PLATE), "the committed plate, byte for byte"
    from PIL import Image
    # "scenic, high-resolution": the golden gets the SCENIC part whole and the RESOLUTION as far as a
    # golden may carry it. The full-size dock plate lives under `review/claims/p58-tokyo-dock-*`, which
    # `.gitignore:77` keeps out of the tree, so the committed copy is 480 px - the same reason the
    # newsreel golden commits a 480 px Bessent cutout instead of the episode's 1024 px one. What the
    # test pins is that this is the COMMITTED DOCK PLATE the depth goldens are built on (a drawn world
    # with a sky, a quay, containers and a crane) and not `melt-plate`'s 320x180 synthetic stand-in.
    assert G.DOCK_PLATE.name == "world-tokyo-customs-dock-v1.png"
    with Image.open(G.DOCK_PLATE) as plate:
        w, h = plate.size
    assert w * h >= 2 * 320 * 180, f"under the 320x180 stand-in it replaces: {w}x{h}"
    assert s1["exit"] == "cut" and s1["world"]["page"]["exit"] == "cut", \
        "R26-60: the page does not also retract - the melt is how this chart leaves"
    # E99 s34: the gather is nowhere near the approved short
    short = ROOT / "content/video_engine/projects/systems-and-blowups/japan-tariff-trick"
    hits = [p for p in short.rglob("*.py") if "gather" in p.read_text(encoding="utf-8", errors="ignore")]
    assert not hits, f"E99 s34: melt:gather must stay off the approved Japan short - {hits}"

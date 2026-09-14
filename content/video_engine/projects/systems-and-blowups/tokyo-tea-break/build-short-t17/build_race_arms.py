"""P52 T17 - the two ARMS of the race A/B (R26-3's open half). PRIVATE proof build, nothing shipped.

The question the row asks: the operator's "the race needs to be smoother, it feels a bit choppy"
(2026-09-06) - is that CURVATURE at the segment joins (the clothoid fitter's case,
`content/video_engine/scripts/kinetics/clothoid.mjs`, doc 42 s42.4) or TIMING (`LPX.RACE_PERIOD`)?

Two builds, one page, the same data, the same clock:

  arm-a/   the engine AS IS - `docs/content-video-engine/samples/scene-evidence-engine.mjs`, copied
           verbatim by `render_baseline.write_split`. Nothing is patched.
  arm-b/   THE SAME page against `engine-clothoid.mjs`: a copy of the engine with ONE substitution -
           a racing mark's path through (value, rank) is a chain of CLOTHOID segments fitted by
           `clothoidFit` (already inlined in the engine at the `KINETICS:BEGIN clothoid` region)
           through the period knots, instead of the coordinate-wise eased polyline that
           `valueAt` / `lpRankPos` trace. The PERIOD CLOCK is untouched: a segment is still traversed
           at tau = smoothstep(u - i), so the arclength-versus-time profile - the timing law, zero
           speed at every period join - is the same in both arms BY CONSTRUCTION. Only the shape the
           mark travels changes. That is what makes the A/B answer the row's question instead of
           confounding it.

The engine on disk is never written. The patch is textual, asserted against its anchors, and the
result is written into this private directory only.

    python build_race_arms.py            # writes arm-a/ and arm-b/ and engine-clothoid.mjs
"""
from __future__ import annotations

import base64
import io
import json
import sys
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

import ledger_page as LPG       # noqa: E402
import render_baseline as RB    # noqa: E402

RUNTIME = 14.0
TIMELINE_NAME = "race.timeline.json"
PLATE_BLANK = "world-ledger-blank-page-cream-v1"
PLATE_INKED = "world-ledger-inked-deckle-cream-v1"
DECKLE_EDGE = SCRIPTS / "proofs/ledger/deckle-edge.json"

# The page's own clock, read off the engine so the measurement window is not guessed:
#   LP.ROLL 0.7 + LP.SAVOR 0.8 + LP.FIELD 2.4 = 3.9 s before the build beat starts (engine :3654, :6342)
#   LPX.RACE_IN 0.6 s of grow-in, then LPX.RACE_PERIOD 1.2 s per period (engine :4439-4440)
PAGE_LEAD = 3.9
RACE_IN = 0.6
RACE_PERIOD = 1.2

# Synthetic, and said to be synthetic on the page itself: this build measures the MOTION LAW, and a
# figure about the world has no business in a test rig (research gate - UNSOURCED never ships).
PERIODS = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
ROWS = [
    ("ALPHA", [100, 118, 131, 140, 152, 168, 181]),
    ("BETA", [92, 108, 126, 148, 171, 190, 212]),      # passes ALPHA and CHI mid-run
    ("CHI", [118, 122, 125, 129, 133, 138, 142]),      # opens as the leader, is passed twice
    ("DELTA", [64, 79, 96, 118, 142, 149, 155]),
    ("EPS", [51, 57, 66, 78, 86, 95, 103]),
]


def race_window() -> tuple[float, float]:
    """[period 0 settled, the last period settled] - the RUNNING part of the race, in scene seconds."""
    t0 = PAGE_LEAD + RACE_IN
    return round(t0, 3), round(t0 + (len(PERIODS) - 1) * RACE_PERIOD, 3)


def race_joins() -> list[float]:
    """The period instants - the joins. Every one is a knot of the path AND a beat of the clock."""
    t0 = PAGE_LEAD + RACE_IN
    return [round(t0 + i * RACE_PERIOD, 3) for i in range(len(PERIODS))]


def series() -> dict:
    return {
        "title": "Five rows, seven periods",
        "sub": "a synthetic race - the motion law under test, not a figure about the world",
        "src": "Synthetic series built by build_race_arms.py for the P52 T17 A/B; not a claim",
        "periods": list(PERIODS),
        "series": [{"name": name, "values": list(values)} for name, values in ROWS],
    }


def silent_wav(seconds: float) -> bytes:
    """The player's clock IS the audio element (engine: t = vo.currentTime), so the track must run the whole
    timeline - the golden source's 2 s WAV stopped playback at 0:02."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
        w.writeframes(b"\x00\x00" * int(8000 * seconds))
    return buf.getvalue()


def plate_file(pid: str) -> Path:
    """The generated ledger plates are gitignored and live in the sweet-villani worktree, not the main checkout.
    READ only; they are encoded into the arm assets, never copied."""
    rel = Path("review/claims/steel-and-paper-ledger-page-v1/objects") / f"{pid}.png"
    for root in (REPO, REPO / ".claude/worktrees/sweet-villani-1c3a16"):
        if (root / rel).exists():
            return root / rel
    raise SystemExit(f"ledger plate not found in the checkout or the worktree: {rel}")


def plate_uri(path: Path) -> str:
    from PIL import Image
    im = Image.open(path).convert("RGB"); buf = io.BytesIO(); im.save(buf, "JPEG", quality=88, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def page_assets() -> dict:
    return {pid: plate_uri(plate_file(pid)) for pid in (PLATE_BLANK, PLATE_INKED)}


def timeline() -> dict:
    page = LPG.build_spec(series(), "race", None, "right")
    # the DECIDED field (E22, ledger-page-signature): the charcoal fills the generated cream page to its deckle
    # (field_plate cross-faded over the blank plate); the board is the deckle's innermost rectangle - never
    # the procedural scribble fallback
    page["plate"] = PLATE_BLANK
    page["field_plate"] = PLATE_INKED
    page["board"] = json.loads(DECKLE_EDGE.read_text(encoding="utf-8"))["inner"]
    scene = {"scene_id": "s01", "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": [],
             "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}}
    return {
        "schema_version": "scene_evidence_timeline.v1", "runtime_s": RUNTIME,
        "title": "P52 T17: the race A/B", "subtitle": "clothoid vs the engine as is",
        "episode_id": "p52-t17-race", "project_id": "p52-t17",
        "narration": {"canonical_hash": "0" * 64, "words_path": ""},
        # no captions and no ken burns: the only thing that moves on this page is the race
        "captions": [], "caption_pages": [], "caption_modes": ["stage"], "sound": [],
        "evidence": {}, "scenes": [scene],
    }


# --------------------------------------------------------------------------- the ONE substitution
# Each (anchor, replacement) is asserted to appear EXACTLY ONCE in the engine text. A patch that
# cannot find its anchor raises rather than writing a silently-unpatched arm B.
BUILD_ANCHOR = """    st.race = { G, periods, rows, T, N, unit, valueAt, ranks, swaps, ticks, items, period };"""
BUILD_PATCH = """    st.race = { G, periods, rows, T, N, unit, valueAt, ranks, swaps, ticks, items, period };
    /* P52 T17 ARM B - THE ONLY SUBSTITUTION. A racing mark's path through (value, rank) is fitted as a
       chain of CLOTHOID segments through the period knots (clothoidFit, the engine's inlined kinetics),
       with G1 tangents from the Catmull-Rom chords. The period CLOCK is untouched: the traversal
       parameter is still smoothstep(u - i), so the arclength-vs-time profile is arm A's. Only the
       SHAPE the mark travels changes - which is exactly the fitter's claim, and nothing else. */
    st.race.fitsByRow = (() => {
      const VMAX = Math.max(1e-6, ...rows.map((r) => Math.max(...r.map((v) => Math.abs(+v) || 0))));
      const KX = G.TRACK_W / VMAX, KY = G.PITCH;
      const knots = rows.map((_, j) => Array.from({ length: T }, (_, i) => ({ x: rows[j][i] * KX, y: ranks[i][j] * KY })));
      const tangentAt = (K, i) => {
        const a = K[Math.max(0, i - 1)], b = K[Math.min(K.length - 1, i + 1)];
        const dx = b.x - a.x, dy = b.y - a.y;
        if (Math.hypot(dx, dy) > 1e-9) return Math.atan2(dy, dx);
        return Math.atan2(K[Math.min(K.length - 1, i + 1)].y - K[i].y, K[Math.min(K.length - 1, i + 1)].x - K[i].x);
      };
      return { VMAX: VMAX, KX: KX, KY: KY, knots: knots,
        fits: knots.map((K) => Array.from({ length: Math.max(0, T - 1) }, (_, i) =>
          clothoidFit(K[i], tangentAt(K, i), K[i + 1], tangentAt(K, i + 1)))) };
    })();
    st.race.posAt = (u, j) => {
      const F = st.race.fitsByRow;
      if (T < 2) return { v: rows[j][0], r: ranks[0][j] };
      const uu = Math.min(Math.max(u, 0), T - 1), i = Math.min(Math.floor(uu), T - 2), fit = F.fits[j][i];
      const f = smoothstep(uu - i);
      if (!fit || !fit.ok) {   /* a degenerate pair keeps arm A's read for that segment, and says so */
        return { v: valueAt(u, j), r: ranks[i][j] + (ranks[i + 1][j] - ranks[i][j]) * f, fallback: true };
      }
      const q = clothoidAt(fit, f);
      return { v: q.x / F.KX, r: q.y / F.KY };
    };"""

PAINT_VALS_ANCHOR = """    const vals = R.items.map((_, j) => R.valueAt(u, j));"""
PAINT_VALS_PATCH = """    const racePos = R.items.map((_, j) => R.posAt(u, j));                        /* P52 T17 ARM B */
    const vals = racePos.map((p) => p.v);                                        /* P52 T17 ARM B */"""

PAINT_RANK_ANCHOR = """      it.g.setAttribute("transform", "translate(0 " + (G.TOP + lpRankPos(R, u, j) * G.PITCH).toFixed(2) + ")");"""
PAINT_RANK_PATCH = """      it.g.setAttribute("transform", "translate(0 " + (G.TOP + racePos[j].r * G.PITCH).toFixed(2) + ")");   /* P52 T17 ARM B */"""

PATCHES = ((BUILD_ANCHOR, BUILD_PATCH), (PAINT_VALS_ANCHOR, PAINT_VALS_PATCH),
           (PAINT_RANK_ANCHOR, PAINT_RANK_PATCH))


def patched_engine_text(engine: Path = RB.ENGINE) -> str:
    text = engine.read_text(encoding="utf-8")
    for anchor, patch in PATCHES:
        n = text.count(anchor)
        if n != 1:
            raise SystemExit(f"arm B's anchor appears {n} times, expected exactly 1:\n{anchor[:120]}")
        text = text.replace(anchor, patch)
    return text


def main() -> int:
    tl = timeline()
    uris = {**json.loads((RB.SOURCES / "ledger-page-mid-build.uris.json").read_text(encoding="utf-8")),
            **page_assets(),
            "__audio__": "data:audio/wav;base64," + base64.b64encode(silent_wav(RUNTIME)).decode()}
    arm_b_engine = HERE / "engine-clothoid.mjs"
    arm_b_engine.write_text(patched_engine_text(), encoding="utf-8")
    a = RB.write_split(HERE / "arm-a", tl, uris, TIMELINE_NAME)
    b = RB.write_split(HERE / "arm-b", tl, uris, TIMELINE_NAME, engine=arm_b_engine)
    t0, t1 = race_window()
    print(f"arm A: {a}")
    print(f"arm B: {b}  (engine {arm_b_engine.name})")
    print(f"race window: {t0} {t1}   joins: {', '.join(str(j) for j in race_joins())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

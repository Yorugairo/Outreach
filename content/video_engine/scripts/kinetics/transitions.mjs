/* kinetics/transitions.mjs - THE BOUNDARY CLOCK, AND THE DIP THAT RIDES IT (P57 T23 / R26-100; ruling E47 s1,
   operator 2026-09-06; doc 46 s46.5 + docs/research/motion/WEALTH_LOGIC_TRANSITIONS_MEASURED.md; CAPABILITIES.md
   "Dip and blur-zoom exits, WIRED"). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py
   between KINETICS:BEGIN transitions and KINETICS:END, where the engine used to declare exitName/exitSecs. The
   boundary clock is arithmetic on the timeline's own spans; only THE EVIDENCE DOOR (below, E98 s7) imports - minJerk
   from ease.mjs and the one projective path from homography.mjs, both regions earlier in the engine.

   A TRANSITION IS NOT A SPECIES, so this module lives in kinetics/ and not species/: it registers no painter and
   declares no SPACE. A species is a thing ON the stage with a kind, a target and an idle; a transition is a LAW
   ABOUT TIME AT A BOUNDARY that every layer obeys at once (E47 s1: "the veil sits above every layer, so the docks,
   the stage captions and the species ride the ramp down with the world"). The engine's render loop calls these by
   name, the way it calls verdict.mjs's, record.mjs's and spiral.mjs's painters - no registry.

   ------------------------------------------------------------------------------------------------------------
   THE DECISION (R26-100 proposed ONE `transitions` module for dip + blur-zoom + wipe + dissolve + suck + slide;
   this module makes it, on what the code SHARES and not on tidiness). There are two clocks in the engine's
   boundary block, not one, and they are the seam the grouping runs along:

     THE STRADDLE CLOCK - the transition owns half of the OUTGOING scene and half of the INCOMING one, so a scene
     must read its OWN exit for the half after its start and the NEXT scene's exit for the half before its end
     (E47: `exit` names the transition INTO the scene it sits on). Exactly two transitions ride it - the DIP and
     the BLUR-ZOOM - and they ride it through the same four lines. `straddleSecs` below IS those four lines, and
     both call it: that is one piece of code genuinely shared, and it lives here.

     THE ARRIVAL CLOCK - the transition arrives ON THE CUT and runs off the incoming scene's start alone:
     `clamp01((t - sc.span[0]) / S)`. The suck, the melt, the dissolve, the slide and the wipe all ride that, and
     what they share is `clamp01` and a division - the engine's own clamp, not a clock worth a module. They stay
     INLINE this slice (named, so the next reader knows this was decided and not missed):
       wipe      a clip-path front plus the seam element, rewritten on wA/wB every frame (doc 29 s9.15 ruling 1)
       dissolve  one opacity on wB (DISSOLVE_S)
       suck      a transform-origin, a spin and a scale on the OUTGOING world (SUCK_S / SUCK_TURN)
       slide     two clipped translates, one per world, in whole pixels (E87 s3 / R26-75; T13's own promotion)
       melt      already a module of its own - species/melt.mjs owns every number and every pixel
     Each of those is a PAINT on a world with its own dials and its own DOM surface; they have no line in common
     with each other beyond the clamp. Folding five painters into one file to make a tidy heading would produce a
     module that is five modules in a trench coat, and sync_kinetics.py's one-region-per-module rule would then
     make every future change to any one of them a change to the file all five live in.

     THE DIP'S RAMP lifts with the clock because it is the clock's only pure consumer: `dipAlpha` is a function of
     t and the two half-windows, and nothing else. The BLUR-ZOOM's paint stays inline: its state is a CSS scale on
     wB plus a backdrop-filter radius on the veil, its dials (BLURZOOM_S / _SCALE / _BLUR / _IN) are the engine's
     declared E47 block that `build_animation_registry.py` and `test_page_performs.py` read out of the engine's
     text, and it needs minJerk - so lifting it would move four dials for no shared line. It calls `straddleSecs`
     from here, which is the whole of what it shares.

   DIP_S ITSELF STAYS IN THE ENGINE, beside its derivation comment ([DERIVED: the reference, 14 frames at 30 fps,
   all 35 of its dips]) and beside the blur-zoom dials it was measured with. It is not this module's to move:
   `build_animation_registry.py:76` scrapes it from the engine's text, `test_page_performs.py:653` asserts on
   `DIP_S = <n>` there, and `gate_motion_density.py:348` carries its twin. The length is the CALLER's; the ramp
   and the clock are this module's. No value changed anywhere in the lift.
   ------------------------------------------------------------------------------------------------------------

   WHEN (CAPABILITIES.md, verbatim): "a dip when the WORLD actually changes at the boundary, a cut otherwise" -
   the dip between ideas (E61's reset), the blur-zoom into the next.

   THE LAW - THE DIP (E47 s1, operator 2026-09-06): "a plain LINEAR ramp to black over the last DIP_S/2 of the
   outgoing scene and back over the first DIP_S/2 of the incoming one. Both halves reach 1 at the boundary, so the
   boundary frame IS black and the cut happens inside it." LINEAR is the ruling and not a default: the reference's
   dip is linear to the frame (doc 46 s46.5, all 35 measured). No ease is applied here and none may be added
   without a ruling - `golden dip-boundary` (the black boundary frame) and `dip-boundary@proof-ramp` (the ramp at
   14.88 s, dipA 0.4894) are what would move. */

import { minJerk } from "./ease.mjs";
import { planeMatrix, cssMatrix3d } from "./homography.mjs";

export const DIP = Object.freeze({
  HALVES: 2,       /* the transition straddles the boundary: half its seconds in each scene, so each half's window is secs / this */
  OPACITY_DP: 4,   /* the veil's opacity as a string, to this many digits - an explicit numeric per frame, so a cold seek lands where a play does */
});

/* THE EXIT GRAMMAR. `dip`, `dip:<s>`, `blurzoom`, `blurzoom:<s>`, `suck:<x>,<y>`, `slide:<dir>[:<s>]`, `melt[:...]`,
   `cut`, `wipe`, `wipe_right`, `dissolve` - the name, and the seconds when the row declares them. Every transition
   in the engine reads its row through these two, which is why they sit with the clock rather than with any one of
   them. A form the player cannot read is the caller's to treat as a cut; the compiler is where an authored exit is
   refused (build_scene_timeline_f.parse_exit). */
export const exitName = (e) => (typeof e === "string" ? e.split(":")[0] : "");
export const exitSecs = (e, dflt) => {
  const v = parseFloat(typeof e === "string" ? (e.split(":")[1] || "") : "");
  return v > 0 ? v : dflt;
};

/* THE STRADDLE CLOCK. How many seconds of `name`'s transition this side of the boundary owns, or 0 when this side
   has no neighbour or the row names another transition. `has` is the neighbouring scene (prev for the half after
   this scene's start, nxt for the half before its end) and `exit` is the row that NAMES the transition - always
   the incoming scene's, since `exit` names the transition INTO the scene it sits on (E47). A missing neighbour
   gives 0, which is how the first and last scenes of a timeline take no half. */
export const straddleSecs = (has, exit, name, dflt) => (has && exitName(exit) === name ? exitSecs(exit, dflt) : 0);

/* the engine's clamp01, verbatim - so the module stands alone under `node --test` */
const tr01 = (v) => Math.min(1, Math.max(0, v));

/* THE DIP'S RAMP at t: 0 outside the transition, 1 on the boundary frame. LINEAR in t on both sides (E47 s1) and
   a pure function of t, the two half-windows and the two scene edges - no wall clock, no rAF state, so a cold seek
   into the dip lands exactly where a play does. Math.max, not a sum: a scene may own an outgoing half and an
   incoming one at once (a one-scene-long dip in and out), and the deeper black wins. */
export const dipAlpha = (t, sceneStart, nextStart, dipIn, dipOut, D = DIP) => {
  let dipA = 0;
  if (dipOut) dipA = Math.max(dipA, 1 - tr01((nextStart - t) / (dipOut / D.HALVES)));
  if (dipIn)  dipA = Math.max(dipA, 1 - tr01((t - sceneStart) / (dipIn / D.HALVES)));
  return dipA;
};

/* the veil's opacity as the painter sets it (the element is the caller's: #dipveil sits above every layer, so the
   docks, the stage captions and the species ride the ramp down with the world and rise with the next one) */
export const dipVeilOpacity = (dipA, D = DIP) => dipA.toFixed(D.OPACITY_DP);

/* ------------------------------------------------------------------------------------------------------------
   THE EVIDENCE DOOR (E98 s7, the operator 2026-09-14: *"a card's tilt is a MOTION, not a pose it jumps to"* - the
   card lands flat, fills the frame like a plate, "then we open that door and behind it is the vault plate"; BACKLOG
   R26-134; doc 29 Part 6's 3D book-flip, never built until now - TRANSITIONS-REVIEW-2026-09-06.md:82).

   `door[:<hinge>][:<s>]` names the transition INTO a scene (E47). It rides the ARRIVAL clock like the slide: over its
   window the OUTGOING world swings open on one stage edge, AWAY from the viewer, and the incoming world is already
   mounted underneath from the swing's first frame - so what the opening shows is the next world. It TAKES the world
   (the page swings away with its chart on it), so an outgoing page is stamped exit=cut by the compiler.

   THE ONE PROJECTIVE PATH. The swing is a rotation about the hinge edge, projected by ONE pinhole at the stage centre
   at PAGE_DEPTH.EYE stage widths (build_scene_timeline_f.page_plane_quad's own eye), evaluated at four corners and
   handed to homography.mjs's planeMatrix / cssMatrix3d - a rigid plane under a pinhole IS a homography, so four
   corners carry every pixel. No CSS perspective(), no second 3D mechanism. Unlike the page's tilt there is no fit:
   the hinge stays ON the stage edge, which is what makes it a door and not a card turning in space.

   THE END ANGLE - chosen so the card never shows its BACK (a flat card has no back side to paint). Under a centred
   eye a door at 90 deg is NOT edge-on: its far edge still hangs a wedge in from the hinge (on a 1080-wide stage,
   540 * (1 - 1.6/2.6) = 208 px). The card is edge-on - a line on the eye's own ray, zero projected width - where the
   eye lies IN its plane: with the hinge half a span h from the centre and the eye d in front, the front face's normal
   (sin t, -cos t) meets the eye direction (h, -d) at zero when tan t = -d/h, i.e.
       OPEN = 180 - atan(d / h)        (degrees; d = EYE * stage width, h = half the span across the hinge)
   - 107.4 deg for a left/right hinge at either aspect (d/h = 3.2), 119.1 deg for a top/bottom hinge on 9:16, 100.0 on
   16:9. Past it the face turns away and the back would show; before it the face is always the front. So the swing
   ends EXACTLY edge-on: u = 1 is zero width, nothing of the card is left, and the incoming world stands alone.

   THE SHADOW: none. Doc 29 s1.2 allows a hard-edge shadow only; a hinge shadow would be a new mark on the incoming
   plate with no evidence in it (E49), so the door adds no pixel that is not one of the two worlds. */
export const DOOR = Object.freeze({
  /* [DERIVED] the door's default length. The wipe is 0.62 s and the slide 0.6 s, and both move a picture by a
     translation. A door sweeps a heavier arc - 107 deg about an edge - and on min-jerk its peak angular speed is 1.875x
     the mean: at 0.6 s that is 335 deg/s, a page FLIPPED; at 0.9 s it is 223 deg/s, about 0.6 rev/s, a hinged panel
     with mass being opened. 0.9 = 1.5x the slide's own length, the least that reads as weight and still lands inside
     the reference's shot rhythm (doc 46: no shot under 1.7 s, so the swing is at most about half the shortest shot). */
  S: 0.9,
  S_MIN: 0.45,     /* [DERIVED] half of S, and the reference's shortest boundary (its dip, 14 frames = 0.47 s): a door shorter than that is a flick */
  S_MAX: 1.8,      /* [DERIVED] twice S: past it the boundary holds the viewer on a move with no evidence in it (E49 - no move for its own sake) */
  HINGES: Object.freeze(["left", "right", "top", "bottom"]),   /* build_scene_timeline_f.DOOR_HINGES - the edge the outgoing world swings open on */
  HINGE: "left",   /* build_scene_timeline_f.DOOR_HINGE - the default */
  EYE: 1.6,        /* build_scene_timeline_f.PAGE_DEPTH["EYE"] - the eye's distance in stage widths; one lens for the page's tilt and the door */
});

/* THE GRAMMAR, the player's side of build_scene_timeline_f._door_parts: `door`, `door:<hinge>`, `door:<s>`,
   `door:<hinge>:<s>`. Anything else - an unknown hinge, a length outside S_MIN..S_MAX, a third suffix - is null, and
   the caller treats a door it cannot read as a CUT (the compiler is where an authored exit is refused, by name). */
export const doorOpts = (e, D = DOOR) => {
  if (exitName(e) !== "door") return null;
  const bits = e.split(":").slice(1);
  let hinge = D.HINGE, secs = D.S;
  if (bits.length && D.HINGES.includes(bits[0])) hinge = bits.shift();
  if (bits.length > 1) return null;
  if (bits.length) {
    if (!/^(\d+\.?\d*|\.\d+)$/.test(bits[0])) return null;
    secs = parseFloat(bits[0]);
  }
  return secs >= D.S_MIN && secs <= D.S_MAX ? { hinge, secs } : null;
};

/* the end angle for this hinge on this stage (the derivation above), in degrees */
export const doorOpenDeg = (hinge, W, H, D = DOOR) => {
  const half = (hinge === "top" || hinge === "bottom" ? H : W) / 2;
  return 180 - (Math.atan((D.EYE * W) / half) * 180) / Math.PI;
};

/* THE CLOCK AND THE ANGLE: min-jerk u over the door's own window from the cut (the world-change shape the slide and
   the snap ride), and the angle linear in u. A pure function of t - a cold seek into the swing lands where a play does. */
export const doorU = (t, t0, secs) => minJerk(tr01((t - t0) / secs));
export const doorAngle = (u, openDeg) => openDeg * tr01(u);

/* THE QUAD: the rectangle `box` (stage pixels; the stage rect by default) rotated `deg` about the `hinge` edge OF THE
   STAGE and projected through the centred eye - four corners TL TR BR BL in stage pixels. At deg = 0 every corner is
   its own (z = 0, the projection is the identity). A point on the hinge line never moves. */
export const doorQuad = (deg, hinge, W, H, box = null, D = DOOR) => {
  const b = box || { x: 0, y: 0, w: W, h: H };
  const th = (deg * Math.PI) / 180, c = Math.cos(th), s = Math.sin(th);
  const cx = W / 2, cy = H / 2, d = D.EYE * W;
  const at = (px, py) => {
    let x = px, y = py, z = 0;
    if (hinge === "right") { const u = W - px; x = W - u * c; z = u * s; }
    else if (hinge === "top") { y = py * c; z = py * s; }
    else if (hinge === "bottom") { const v = H - py; y = H - v * c; z = v * s; }
    else { x = px * c; z = px * s; }
    const k = d / (d + z);
    return [cx + (x - cx) * k, cy + (y - cy) * k];
  };
  return [at(b.x, b.y), at(b.x + b.w, b.y), at(b.x + b.w, b.y + b.h), at(b.x, b.y + b.h)];
};

/* the projected span across the hinge - the door's visible width (left/right) or height (top/bottom) on the stage */
export const doorSpan = (quad, hinge) => {
  const i = hinge === "top" || hinge === "bottom" ? 1 : 0, vs = quad.map((p) => p[i]);
  return Math.max(...vs) - Math.min(...vs);
};

/* THE CSS the painter prepends to the outgoing world's own transform. `box` is the element's layout box in STAGE
   pixels (the world overhangs the stage by its Ken Burns room, so its origin sits at -inX, -inY), and (ox, oy) is its
   transform-origin from its own top left - planeMatrix composes under the CSS the element already carries, so the
   Ken Burns, the idle and the camera underneath are untouched and the door applies last, in stage space. */
export const doorCss = (deg, hinge, W, H, box, ox, oy, D = DOOR) => {
  const q = doorQuad(deg, hinge, W, H, box, D).map(([x, y]) => [x - box.x, y - box.y]);
  return cssMatrix3d(planeMatrix(q, box.w, box.h, ox, oy));
};

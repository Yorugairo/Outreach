/* kinetics/transitions.mjs - THE BOUNDARY CLOCK, AND THE DIP THAT RIDES IT (P57 T23 / R26-100; ruling E47 s1,
   operator 2026-09-06; doc 46 s46.5 + docs/research/motion/WEALTH_LOGIC_TRANSITIONS_MEASURED.md; CAPABILITIES.md
   "Dip and blur-zoom exits, WIRED"). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py
   between KINETICS:BEGIN transitions and KINETICS:END, where the engine used to declare exitName/exitSecs. It
   imports nothing - the boundary clock is arithmetic on the timeline's own spans.

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

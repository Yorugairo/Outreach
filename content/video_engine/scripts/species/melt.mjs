/* SPACE: stage */
/* species/melt.mjs - THE MELT EXIT (P52 T9; BACKLOG R26-15, reworked to E88 by R26-76). SOURCE OF TRUTH, inlined into
   the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN melt and KINETICS:END, AFTER ink, squash,
   stopaction, arap and morph_a - it imports all five, and the import order IS the region order.

   E88 (the operator, 2026-09-13): "i envisioned melting only the chart information on the page, and compiling that into
   a dense heavy ball akin to the reference, and then either throwing it off of the screen, and drawing a new chart or
   splattering that back onto the page to either form a new chart or a narrative plate springs up, reading as having been
   \"painted\" - i didn't imagine melting the whole charcoal board". P52 T9 melted the WORLD's area polygon, so the board
   left with the chart. Now THE CHART'S INK melts and the BOARD STAYS:
     the INK   a clone of the outgoing world with its board hidden (`.meltink`: the page's cream, grain, roll edge, field
               and field plate invisible) - the title, the series, the bars, the marks, the labels, the rail. It wears
               the melt's mask, its pixel filter and its squeeze.
     the BOARD the outgoing world itself with its ink hidden (`.meltboard`) - the cream ground, the deckle, the charcoal.
               It never moves; under a splash it wears the REVEAL mask the painting grows through.

   It registers NO painter: a melt is not a species kind, it is an EXIT law the engine's scene loop calls by name where
   it handles the suck. `exit` names the transition INTO the scene it sits on (E47), so `s05.exit = "melt"` melts s04's
   chart as s05 begins.

   FOUR PHASES over the exit's window u = clamp01((t - t_boundary) / secs), the shares fixed dials that sum to 1:
     melt   u 0    - 0.30   the ink SAGS and RUNS: its own pixels smear downward (RUN_COPIES offset copies merged) under
                            the GOOEY THRESHOLD (a Gaussian blur re-steepened by a linear alpha ramp - HyperFrames'
                            morph-text trick, our K-M chain's `feFuncA slope`), so neighbouring marks FUSE into one liquid
                            body; the ink box's outline sags over seeded drips as its mask.
     ball   u 0.30 - 0.55   the ink SQUEEZES toward its centroid while the outline MORPHS to a circle of BALL_R (morph_a,
                            the vertex method) on the STEPPED clock (stopaction `stepped`, hold 2 - on 2s), and a DENSE
                            ink body - the marks' own colours mixed by Kubelka-Munk and concentrated DENSITY times - comes
                            up opaque over it: the chart compiles into a heavy ball.
     end    u 0.55 - 1      one of three AUTHORED endings:
       throw          the ball lands in its own weight (stopaction impactSquash on MASS, SQUASH, on 2s) for ANTIC of the
                      phase, then is THROWN off the stage (throwXf run backwards: a landing played in reverse IS a launch),
                      a low arc and little tumble because it is heavy. The board is up until the launch; the next scene's
                      chart then draws on the same board (the engine delays that page's clock by meltDrawDelay).
       splash:chart   the ball SLAMS onto the board (the same squash), flattens, and bursts into droplets that LAND on the
                      board (soakStepped's staircase); the landed drops then grow as seeded stains through the board's
                      REVEAL mask with a wet ink rim, and the next page's chart - already built beneath - is what shows
                      through them: the chart arrives out of the splatter, not by its build.
       splash:plate   the same splatter, and what grows through the stains is the next scene's NARRATIVE PLATE, springing
                      up (a small scale settle) as if painted by that ink; the board is painted over from the drops out.
     gone   u >= 1          the outgoing world, its ink and the overlay are hidden, exactly as the suck ends.

   THE WEIGHT PHASE (R26-118, E88 s6 - the operator, 2026-09-14: "we need to make sure our ball has real density, and
   we should probably roll it around or manipulate it a bit for good measure to show that it has real mass & gravity,
   just like the hyperframes example did with their stop animation"), OPT-IN as `melt:weight[:<material>]`, sits
   BETWEEN the ball and the ending and takes W_S seconds out of the window (the other three phases keep their shares of
   what is left, so a melt without `weight` is the melt that shipped - every golden byte-identical). Its four beats are
   stopaction's own: LAND (the receiver's dip, the contact shadow tightening from FAR to NEAR, the material's impact
   squash, the board's three-frame answer), ROLL (rollXf: no slip, the turn angle IS the distance over the radius, a
   constant friction stopping it where the math says), NUDGE (one second impulse, sold BEFORE it moves - 48 s48.6) and
   SETTLE (the material's spring). E88 s7 widened it: with the weight phase the ball is a LIVING DROP - kinetics/
   drop.mjs's Rayleigh ring, excited by the compile and re-excited by every landing and nudge, its area renormalised
   every frame and never let go still (E49) - it is METAL by default (a dead stop that does not squash: the roll and
   the nudge carry the weight instead), it keeps a MARK of its own ink so the rotation is VISIBLE, and it wears a
   specular HIGHLIGHT pinned to the stage light, which counter-rotates against that mark. The compare verb (T12c) melts
   through the same state and inherits all of it.

   Everything above the painter is a pure function of (t0, t, the rect, the dials, rnd): the same t twice is the same
   object, so a scrubbed frame is the played frame and a cold render is the warm one. `rnd(k)` is the caller's seeded
   hash in [0, 1) - the engine passes lpHash bound to the scene, never Math.random.

   The AUTHORED FORM: `melt` | `melt:throw` | `melt:splash:chart` | `melt:splash:plate`, with `:<s>` (the length) and, on a
   throw only, `:<x>,<y>` (the exit point in STAGE fractions), in any order after the name. A bare `melt:splash` is
   REFUSED: since E88 a splash has two endings that need two different incoming worlds (a chart page, a plate), and an
   alias would pick one silently. build_scene_timeline_f.py's parse_exit reads the same grammar and refuses anything
   else, naming the row. Every number here is a starting dial (doc 42 s42.5); HG2 tunes them by eye on the proof frames. */
import { hexToLin, linToHex, ksFromR, soakStepped } from "../kinetics/ink.mjs";
import { squashMatrix, scaleBy } from "../kinetics/squash.mjs";
import { CADENCE, stepped, throwXf, impactSquash, rollXf, contactShadow, groundDip, groundShake, rebound, massImpact, MASS, STOP } from "../kinetics/stopaction.mjs";
import { DROP, dropRing, dropModes, dropSpecular, dropRimAlpha, dropBandAlpha, dropPitAlpha, dropDeepPoint, dropLightAxis } from "../kinetics/drop.mjs";
import { centroid } from "../kinetics/arap.mjs";
import { morphAPrepare, morphAAt, morphAPath } from "../kinetics/morph_a.mjs";

export const MELT = Object.freeze({
  S: 1.6,            /* the exit's default length [DERIVED: the suck's 0.3 s is one phase of collapse; a melt is three
                        (the sag, the ball, the ending) plus a throw's FLIGHT_S 0.45 - 3 x 0.38 + 0.45 ~ 1.6] */
  MELT_END: 0.30,    /* the phase shares as CUTS of u: melt [0, 0.30), ball [0.30, 0.55), ending [0.55, 1] */
  BALL_END: 0.55,
  /* THE SAG (the ink box's outline, the mask the melting ink wears) */
  DRIPS: 7,          /* how many drips the box's foot grows */
  SAG: 0.40,         /* the deepest drip's reach, as a share of the box's height */
  TOP_SAG: 0.42,     /* how far the TOP edge sinks by the end of the sag: a melting body loses height, its mass goes down */
  BASE_SAG: 0.10,    /* the whole foot slumps this much besides */
  DRIP_W: 0.11,      /* a drip's half-width as a share of the box's width */
  DRIP_JIT: 0.55,    /* how far a drip's centre wanders from its even place, as a share of the even spacing */
  DRIP_DELAY: 0.40,  /* the last drip starts this far into the melt phase: the drips open in a seeded order */
  N: 33, TOP_N: 13, SIDE_N: 7,   /* the ring's samples: foot, top, each side (even-ish spacing - see meltOutline) */
  /* THE GOOEY THRESHOLD */
  BLUR: 26,          /* the outline's blur at the melt's peak, px at 1920 */
  EDGE_SLOPE: 24,    /* the alpha ramp that re-steepens the outline's blur into a liquid edge */
  /* THE RUN (E88: the MARKS melt, not a rectangle) - the ink's own pixels, smeared down and fused */
  RUN: 0.22,         /* how far the ink runs at the sag's end, as a share of the ink box's height [DERIVED, HG2] */
  RUN_COPIES: 6,     /* offset copies merged into the run: enough that the gooey blur joins them into one trail (3 read as
                        stacked parallel copies of each line on the proof frames) */
  INK_BLUR: 4,       /* the marks' own blur at the melt's peak, px - a 3 px line blurred to 7 px and ramped by INK_SLOPE
                        comes back ~2.5x as thick, which is the swell of a wet line [DERIVED, HG2] */
  BALL_FUSE: 40,     /* the squeezed ink's extra blur through the ball phase, in the ink's OWN px (the squeeze shrinks it ~10x
                        on screen): without it the compacting chart read as stacked orange hatching, not one mass */
  INK_SLOPE: 9,      /* the marks' alpha ramp (the outline's EDGE_SLOPE is 24: a mark is thinner than a body) */
  /* THE BALL - dense and heavy (E88): smaller than P52 T9's 0.15, opaque, darker than its own marks */
  BALL_R: 0.085,     /* the ball's radius as a share of the ink box's height [was 0.15 of the whole PAGE's height] */
  CIRCLE_N: 96,      /* vertices on the circle = RING_N, so the morph's resample lands ON them (radius exact at the end) */
  RING_N: 96,
  HOLD: 2,           /* the stepped clock's hold: on 2s (stop-action, doc 42) */
  FPS: CADENCE.FPS,
  SQUEEZE: 1.15,     /* the ink box is squeezed until its longer side is SQUEEZE ball-diameters: the chart compiles INTO the
                        ball instead of being cropped by it */
  BODY_FROM: 0,      /* the ball is a CRISP opaque disc from the first frame of its phase (a ramp over the whole box read as
                        a jelly slab; one that waited for the squeeze read as a soft chart silhouette at 045 - the parent's
                        two reads, 2026-09-13) ... */
  BODY_TO: 0.15,     /* ... fully opaque from here */
  BODY_GROW: 0.4,    /* it GROWS from BODY_SEED of its radius to all of it by here of the ball phase, while ... */
  BODY_SEED: 0.25,
  INK_OUT: 0.45,     /* ... the squeezed ink fades into it, gone by here: at 045 there is only the round ball */
  TINT_MELT: 0,      /* how far the marks have turned to the ink by the sag's end (all the way by the ball's middle). 0: through
                        the sag every mark runs in its OWN colour - 0.6 turned the pale series and the grid salmon-pink */
  INK_DEEP: 3,       /* THE INK: the chart's DOMINANT stroke (its first series) concentrated this many times by K-M - the
                        same hue, deeper. Never a mix of every series: the golden page's four mixed land on green */
  CORE: 12,          /* the ball's shaded side, the same ink at this concentration (the weight read in the shading) */
  LIGHT: 1,          /* the ball's lit side: the stroke itself */
  TEXT_STREAK: 1.6,  /* the words' streak: its vertical blur is half the run, it hangs 0.6 of the run below the glyph, and its
                        spread alpha is lifted this much so it reads as ink trailing, not a haze */
  SHEEN: 0.5,        /* its ONE highlight: the stroke taken this far toward white, a small spot up and to the left */
  SPLAT_OUT: 3.5,    /* splash:chart - the landed splats fade this many times faster than the paint clock and ... */
  SPLAT_SHRINK: 0.5, /* ... shrink by this much as the chart shows through: they resolve INTO it and never sit over its
                        labels at full ink (they covered "Mega-cap" at 075 - the parent's read, 2026-09-13) */
  /* THE WEIGHT (stopaction's dials, named): the ball lands in its own weight before it goes anywhere */
  MASS: "liquid",    /* stopaction MASS for the squash: liquid holds its squash TWO frames (ink holds one) - a heavy wet body */
  SQUASH: 0.30,      /* impactSquash's IMPACT_SQUASH for the ball (stopaction's card default is 0.22) */
  ANTIC: 0.22,       /* the share of the throw phase the ball sits in that squash before the launch */
  /* THE THROW - heavy: a low arc, little tumble, out the bottom */
  TO: [1.02, 1.32],  /* the default exit point in STAGE fractions: off the bottom right [was 1.16, 1.22] */
  ARC: 0.06,         /* throwXf's ARC for the ball (stopaction 0.22: a card lifts; a heavy ball barely does) */
  SPIN_DEG: 4,       /* throwXf's SPIN_DEG for the ball (stopaction 9) */
  /* THE SPLASH */
  DROPS: 14,         /* droplets in the splatter */
  BURST_END: 0.40,   /* the share of the ending the burst takes; the rest is the PAINT (the stains growing) */
  SPLASH_SPREAD: 0.30,   /* the angular jitter (radians) on each droplet's ray */
  LAND_MIN: 0.25,    /* where a droplet lands along its ray, as a share of the distance to the ink box's edge ... */
  LAND_MAX: 0.92,    /* ... so the whole splatter lands ON the board */
  DROP_R: 0.035,     /* a droplet's radius as a share of the box's height */
  FLAT: 0.62,        /* how far the ball flattens as it bursts (1 - FLAT of its height) */
  REVEAL_R: 0.75,    /* a stain's reach as a share of the box's height (seeded 0.6x - 1.4x) */
  CORE_R: 0.70,      /* the stain under the ball's own impact */
  FLOOD_FROM: 0.70,  /* the board's last cover fades out from here of the paint clock, so the reveal is whole at u = 1 */
  TAIL: 2.2,         /* a landed splat's tail toward the impact, in its own radii (in flight it is longer: speed) */
  LOBES: 14,         /* a splat's seeded lobes */
  SPLAT_RAG: 16,     /* a splat's torn edge: the K-M soak's noise displacement, px */
  STAIN_RAG: 70,     /* a paint stain's torn edge, px - the ink-bloom's ragged front (INTAKE-INK-BLOOM-2026-09-08) */
  STAIN_BLUR: 6,     /* the stains' own gooey threshold: blur px ... */
  STAIN_SLOPE: 12,   /* ... and ramp */
  SPRING: 0.09,      /* splash:plate - the plate SPRINGS UP: from 1 - SPRING of its size, over its rest by ~2.5 %, settled at
                        the end (a damped cosine; 0.05 settling one way was invisible). 1 - 0.09 of a world that overhangs
                        the stage by 5 % still covers it */
  /* THE WEIGHT PHASE (R26-118), all of it opt-in behind `melt:weight` - not one of these is read by a melt that
     does not ask for it. The shares below are of the PHASE's own length, and the phase's length is W_S seconds. */
  W_S: 1.15,             /* how long the weight phase runs. A melt that asks for it and declares no length runs S + W_S
                            (1.6 + 1.15 = 2.75 s): the four beats need the time, and stealing it from the melt and the
                            ball would slow the compile the operator already approved [DERIVED, HG2] */
  W_MAX: 0.55,           /* and it may never take more than this share of a DECLARED window (a 1.2 s melt:weight gets 0.66 s) */
  W_MASS: "metal",       /* E88 s7: the ball is METAL unless `melt:weight:<material>` names another - MASS.metal is a
                            dead stop with no squash and no rebound, so the roll and the nudge carry the weight */
  W_DROP_PX: 34,         /* LAND: the last of its height, in the world's own px [DERIVED: STOP.DROP_PX 48 is a card's] */
  W_LAND: 0.20,          /* the beats, as shares of the phase: LAND ends here ... */
  W_ROLL: 0.50,          /* ... ROLL ends here (rollXf's own T at the dials below is 0.33 s, inside this 0.35 s) ... */
  W_SETTLE: 0.84,        /* ... NUDGE runs to here, and the material's spring settles what is left */
  W_ROLL_PX: 150,        /* the authored travel of the roll, in the world's own px */
  W_ROLL_FRICTION: 2800, /* the rolling deceleration, px/s^2 [DERIVED: sized so the roll STOPS inside its own beat -
                            v0 = sqrt(2 a D) = 916 px/s, T = 0.33 s; a slower friction rolls past the window] */
  W_ROLL_SQUASH: 0.05,   /* the squash along the travel at full speed - a deformable material only (metal: none) */
  W_NUDGE_PX: 46,        /* NUDGE: the second impulse, "manipulate it a bit" */
  W_NUDGE_K: 0.55,       /* how hard it re-excites the drop's modes, against a landing's kick */
  W_ANTIC_PX: 5,         /* 48 s48.6: weight is sold BEFORE the move - the ball leans back this far ... */
  W_ANTIC_S: 0.12,       /* ... over this long, before the nudge takes it [DERIVED: STOP.ANTIC_S 0.18 is a whole
                            landing's; a nudge's lean has to leave its own beat room to roll] */
  W_MARK_AT: 0.62,       /* THE MARK the roll turns: how far out it sits, as a share of the ball's radius */
  W_MARK_R: 0.30,        /* its own size, as a share of the radius ... */
  W_MARK_FLAT: 0.42,     /* ... flattened this much along its long axis: a streak the sag left, not a dot */
  W_MARK_PHI: 2.05,      /* where the sag left it on the ball (radians, before the roll turns it) */
  W_SHADOW_A: 0.5,       /* the contact shadow's ink at its darkest (contactShadow's own alpha scales it) */
  W_SHADOW_W: 1.15,      /* its width in ball radii (its height is a sixth of that: a slit on the board, doc 48) */
  /* P61 T5 / E99 s3 - THE BALL'S SHADOWS, the operator (OPERATOR-RULINGS.md:2922-2925): "We definitely need more
     shadows. The shadows are where the weight/mass largely come from i think, dark fresnel rim + metallic band and I
     imagine incorporating at least one point of deep shadow depth." The PROFILES are the material's (kinetics/
     drop.mjs DROP.RIM_* / BAND_* / PIT_*, each with its research-gate tier in that block); these are the ball's own
     PAINT - which K-M ink the profile is drawn in, and the contact shadow, which is the melt's alone. Every one is
     read ONLY under `melt:weight`: a melt that does not ask for weight mounts none of the three overlays and none of
     the two shadow ellipses, so its DOM and its strings are the ones that shipped. */
  W_OCCL_A: 0.85,        /* (a) MORE CAST/CONTACT SHADOW: the OCCLUSION CORE, a second, tighter, much darker patch
                            painted OVER the cast slit - the board the ball actually occludes. Its ink at the darkest
                            (contactShadow's own alpha and its nearness scale it). The cast slit alone reads as a ball
                            hovering over a grey smear; the core is what sets it ON the board [DERIVED] */
  W_OCCL_W: 0.55,        /* its width in ball radii - half the cast slit's 1.15, because an occluded patch is smaller
                            than a cast shadow, never larger [DERIVED] */
  W_OCCL_FLAT: 2.4,      /* how flat it is (rx / ry). The cast slit is 6; the core is rounder - it is the contact, seen
                            at the board's own grazing angle, not a shadow thrown across it [DERIVED] */
  W_OCCL_BLUR: 0.22,     /* its blur as a share of its OWN width, so it stays a tight patch at any ball size [DERIVED] */
  W_RIM_SHADE: 0.92,     /* (b) THE DARK GRAZING RIM ("dark fresnel rim"): how far the ball's own ink is taken toward
                            BLACK at the silhouette, in linear light (meltShade - the mirror of meltSheen).
                            MEASURED, and it is why this is a shade and not a K-M concentration: Kubelka-Munk mixing
                            SATURATES an orange stroke toward a bright red and never toward black - meltInkOf on the
                            golden's ink gives #fe3818 at INK_DEEP 3, #fd1a08 at CORE 12 and #fc0c03 at 34, all of
                            them at full luminance. A shadow is less light, not more pigment; the first build drew the
                            rim at K-M 34 and the silhouette stayed bright. 0.88 lands the outline near-black, which
                            is also what the blueprint's metal is (s3.3 :191-201, gate tier PLAUSIBLE: k_d = 0, so a
                            metal's unlit surface HAS no colour) [DERIVED from that finding] */
  W_RIM_STOPS: 10,       /* how many gradient stops carry DROP's grazing profile, distributed toward the silhouette
                            (the profile's last tenth of radius carries most of its rise) [DERIVED] */
  W_BAND_K: 0.55,        /* (c) THE METALLIC BAND: how far its ink is taken toward white. HL_SHEEN (the one specular
                            spot) is 0.82: the band is a sheen across the body, never a second highlight [DERIVED] */
  W_BAND_STOPS: 24,      /* the stops its Gaussian is sampled at along the light axis [DERIVED] */
  W_PIT_SHADE: 0.80,     /* (d) THE POINT OF DEEP SHADOW DEPTH: how far the ink is taken toward black at the well's
                            seat, the same way. Under the rim's 0.88, so the silhouette stays the darkest thing on the
                            ball and the well reads as depth inside it, not as a second outline [DERIVED] */
  W_PIT_STOPS: 6,        /* the stops its falloff is sampled at [DERIVED] */
  /* ---- P61 T5b / E99 s42 - THE PRIOR SURFACE BACK, THE DARKNESS KEPT ----------------------------------------------
     The operator on T5's ball (OPERATOR-RULINGS.md:3202): "This doesn't work, the ball is too blurred so the prior
     work is actually better. this slice is pixelated on the edges now, the darkness feels right, but the blur is
     wrong, and i think the rim is wrong." NAMED, from the frames, before these two dials were written:
       THE BLUR is the RIM'S RAMP, not a filter. There is no feGaussianBlur and no CSS blur on the ball anywhere -
       the only blur T5 added is on the occlusion ELLIPSE, on the board. `dropRimAlpha` runs from DROP.RIM_AT 0.42 to
       RIM_A 0.97 in near-black ink, so the outer 58 % of the radius is one continuous darkening. Measured across the
       silhouette at the settle (y=838): the prior ball goes board 37 -> 160 -> 254 and is FLAT, a 1 px edge; T5 goes
       37 -> 121 -> 122 -> 135 ... 239 and is still climbing 100 px in. A surface with no terminator anywhere is what
       soft focus looks like. The BAND is the second smear: a Gaussian stripe of half-width 0.055 over 24 stops.
       THE PIXELATED EDGE is four antialiased copies of the SAME path composited (body + band + pit + rim, each given
       `st.body` in paintMelt). A boundary pixel of coverage a ends at 1 - (1 - a)^4. Measured on one pixel: coverage
       0.567 on the prior ball, 0.988 on T5's - and 1 - (1 - 0.567)^4 = 0.965, the rest being RIM_A. The rim is the
       layer that carries alpha AT the silhouette, so it is the layer that destroys the antialiasing.
     So both refused things are OFF, and both keep every dial they had - the profiles are still right, still tested,
     and reachable through an option; NO authored token turns them on, because E99 s42 refused the look. What STAYS is
     the DARKNESS the operator kept: the occlusion core (W_OCCL_*, on the BOARD) and the point of deep shadow depth
     (W_PIT_*), whose gradient reaches 0.22 + 0.26 = 0.48 of the body's box against a silhouette at 0.5 - it carries
     NO alpha at the edge and so cannot harden it. */
  W_RIM_ON: false,       /* (b) THE DARK GRAZING RIM: OFF (E99 s42, "i think the rim is wrong" - and it is both
                            defects at once: the ramp is the blur, the alpha at the silhouette is the pixelation) */
  W_BAND_ON: false,      /* (c) THE METALLIC BAND: OFF (E99 s42, the second soft smear across the body) */
  /* ---- P61 T5b / E99 s42 - THE BALL'S BODY COLOUR (`melt:weight:...:body=<word>`) ---------------------------------
     The operator: "I would be interested in seeing it just melt to the slate gray or the reference color also to see
     what that looks like." So the body colour is an AUTHORED option on the weight token, read in exactly one place
     per side (`meltOpts` here, `_melt_parts` in build_scene_timeline_f.py), an unknown word refused BY NAME, and the
     DEFAULT - `chart`, no word at all - is the ball that always shipped, byte for byte. MELT_BODIES holds the targets;
     this is how far the ball's ink is taken toward the one it names. */
  W_BODY_SHADE: 1,       /* 1 = the named colour exactly, at each stop's OWN level: the stop's target is the body
                            colour scaled by that stop's share of the LIT stop's luminance, so the ball keeps its own
                            light-to-core ramp and only its hue and level change. Below 1 the chart's ink shows
                            through. 1 is the ruling's own word - "just melt to the slate gray" [DERIVED] */
  /* P58 T6 (b) / E98 s4: THE PLANE THE BALL MELTS AT (`melt:...:depth=<k>`) - kinetics/camera.mjs PARALLAX's own
     range, written here so this module stays self-contained, and build_scene_timeline_f.DOCK_DEPTH's the same three
     numbers (one dial written twice, as MELT.S and MELT_S are; test_transitions_e47 pins the pair). */
  DEPTH_MIN: 0,          /* pinned to the frame: the ball takes none of the camera's move */
  DEPTH_MAX: 4,          /* ... and the camera's own ceiling */
  DEPTH_FLAT: 1,         /* doc 24's far wall - the flat clone, so `depth=1` is the melt that always shipped */
  HL_SHEEN: 0.82,        /* the specular highlight: the ball's own lit ink taken this far toward white */
  INK_HEX: "#E9E2D2",    /* the marks' colour when the chart carries no stroke to read (a page of words) */
  /* ---- P61 T6 / E99 s2 - THE GATHER (`melt:gather`), all of it opt-in ---------------------------------------------
     The operator (OPERATOR-RULINGS.md:2912-2920): "for the melt, i expect almost like our swirl effect, i don't want
     the melt to be blur or a wipe, it should be closer to the swirl except for instead of a whirlpool, vortexing
     around a single point, it collects and amasses into a single point, that single point should be dense, heavy,
     and vibrating with energy". So for a melt that asks, the SAG is replaced by the PAGE VORTEX's own motion (doc 29
     s9.31, species/spiral.mjs `lpVortex`) aimed at the BALL'S CENTRE instead of at a drain: every mark on the page is
     a particle that TRAVELS to that point and AMASSES there - and the gooey blur, the ink's run and the words' streak
     are all 0 across the window, because a blur is the thing the ruling refuses.
     THE ONE DIFFERENCE from the retract, and it is the whole of the ruling: a retract's particle shrinks to NOTHING at
     the drain (spiral's SHRINK, `(1 - ui)^0.7`); a gather's particle shrinks only to G_KEEP of itself and lands ON the
     point, so what the eye reads is ink collected, not ink drained away.
     The terms below are s9.31's, to the digit where they carry the same meaning (LP_RETRACT TURNS 3.0, LAG 0.25,
     ALPHA 0.85, R_FALL 1.7, CORE_BASE 0.4, CORE_GAIN 1.6, CORE_FALL 1.5, SHRINK 0.7). This module cannot IMPORT
     spiral.mjs - sync_kinetics refuses an import whose region is later in the engine, and spiral's region is at
     scene-evidence-engine.mjs:8236 against melt's :2686 - so they are written here and `test_melt_gather.py` pins
     every one of them against species/spiral.mjs's own LP_RETRACT, which is what keeps the two from drifting. */
  G_TURNS: 3.0,          /* how many turns the RIM makes on its way in - s9.31's "a way tighter vortex, almost celestial" */
  G_LAG: 0.25,           /* the point takes the nearest ink first: a particle at the rim waits this share of the window */
  G_ALPHA: 0.85,         /* the area-preserving stretch along the flow at its peak (ui = 0.5): ink thins across its travel */
  G_R_FALL: 1.7,         /* the radius falls slowly, then fast: r * (1 - ui^this) */
  G_CORE_BASE: 0.4,      /* the rim's share of the whirl ... */
  G_CORE_GAIN: 1.6,      /* ... and what the core adds (the core turns ~4x the rim: arms, not a wheel) */
  G_CORE_FALL: 1.5,      /* how sharply that gain falls off with the normalised radius */
  G_SHRINK: 0.7,         /* the particle's own scale, (1 - ui)^this, floored at ... */
  G_KEEP: 0.10,          /* ... this, so it AMASSES on the point instead of vanishing into it [DERIVED: a tenth of
                            itself is still ink on the frame at the handover, and it is inside the ball's silhouette] */
  G_DEEP: 0.85,          /* how far the marks have turned to the ball's own INK by the gather's end: they arrive as one
                            colour, so what lands on the point reads as a mass and not as a heap of four series [DERIVED] */
  /* THE POINT, forming under the arriving ink */
  G_CORE_AT: 0.55,       /* the core opens at this share of the gather ... */
  G_CORE_SEED: 0.30,     /* ... at this share of the ball's radius, and grows to all of it by the gather's end [DERIVED] */
  /* THE VIBRATION (E49: nothing ever goes truly still). NOT a new law - it is kinetics/drop.mjs's OWN idle, the FLOOR
     amplitude its decay can never take away, with an amplitude dial over it, so the point wriggles to contain itself
     from the frame it exists. `melt:weight` then stacks the landing's and the nudge's kicks on top, as it always did. */
  G_VIB: 3.0,            /* the amplitude dial: the drop's FLOOR times this while the point gathers. 1 is the resting
                            wriggle a landed ball has; the ruling asks for "vibrating with energy", and 3 puts mode 2
                            at ~3.6 % of R - visible at the ball's size, well inside the ring's own area
                            renormalisation [DERIVED, HG6 tunes it by eye on the proof frames] */
  G_VIB_FALL: 0.45,      /* it falls back to the resting floor over this share of the BALL phase: the point stops
                            shaking once it has everything [DERIVED] */
  G_LINE_N: 160,         /* THE NOODLE (doc 29 s9.31: "the series line is redrawn point by point through the same
                            map, so it curls into the drain"): how many points a chart PATH is sampled at, once, at the
                            boundary. A path turned rigidly reads as a stick swung across the board - the first build's
                            own defect, read on the frame; 160 samples hold an area band's jagged top and a four-year
                            line's shape while they curl [DERIVED, read on melt-gather's midpoint] */
  /* P61 T3 / R26-117 - THE THIRD ENDING: THE BALL BECOMES THE NEXT FULL CHART. The ball is already a closed outline
     on the board; `page_enter:morph` (P47 T3) already deforms a named prop outline into the area under the arriving
     page's series by ARAP. R26-117 is the one sentence that joins them - "the ball is the prop it starts from" - so
     `melt:morph` ENDS the melt at the ball and hands its ONE ring to the next page as that page's prop outline. The
     two run on ONE clock: the melt's window is the sag, the ball and then the HAND, and the hand's seconds ARE the
     arriving page's morph seconds (`meltHandSecs`), so there is no cut and no gap between them to fill.
     What the ball's body does in the hand is the whole of the reading: it does NOT vanish and the page's area does
     NOT fade up over it. The body wears the MORPHING OUTLINE ITSELF (the engine hands it back through `hand`), so
     the thing the eye has been watching is the thing that deforms; over M_FADE its paint gives way to the page's
     own ink, which is the only cross-over in the window and it happens on ONE shape, in one place, mid-deformation.
     E99 s39's test - "a morph should be proof of form/function to the audience, that we're really manipulating the
     world they're watching" - is what that is for: nothing is formed magically, because the shape at every instant
     is the shape the frame before it was. The ball's BODY COLOUR (MELT_BODIES) never enters any of it: the ring is
     geometry and the paint is read off the ball as painted, whatever HG5b settles it to. */
  M_S: 1.3,              /* what the MORPH ending adds to the default window, the way W_S and G_S do: the hand's own
                            share of a 1.6 s melt is 0.72 s, and an ARAP deformation of a whole chart's area in 0.72 s
                            reads as a snap (MORPH.S, the page-enter morph's own default, is 2.0 s standing still).
                            With it a bare `melt:morph` runs 2.9 s - sag 0.87, ball 0.72, hand 1.31 - and the hand is
                            within a notch of the page morph's own pace [DERIVED, HG7 tunes it on the frames]. A row
                            that declares its own length gets exactly that length, here as everywhere */
  M_FADE: 0.85,          /* the share of the HAND over which the ball's paint gives way to the page's own ink, on the
                            shared deforming outline. LINEARLY, and across nearly the whole hand: the cross-over is
                            the only one in the window, so it is spread as thin as it will go - at the hand's midpoint
                            the ball is at 0.41 and the page's area at 0.59, and no single frame carries a swap. It
                            ends a little before the shape lands so the last stretch is unambiguously the page's own
                            area arriving on its series [DERIVED, read on melt-morph@proof-050] */
  G_S: 0.9,              /* how much a gather adds to the DEFAULT window, the way W_S does: the sag's own share of a
                            1.6 s melt is 0.48 s, and three turns in 0.48 s is a jump, not a swirl. With it the
                            gather runs MELT_END of (S + G_S) = 0.75 s [DERIVED, HG6]. A row that declares its own
                            length gets exactly that length, gather or not */
});

/* the authored endings - build_scene_timeline_f.MELT_ENDINGS is the same tuple, and test_melt_morph pins the pair.
   P61 T3 / R26-117 adds `morph`: the ball is handed to the next page's `page_enter:morph` as its prop outline. */
export const MELT_ENDINGS = Object.freeze(["throw", "splash:chart", "splash:plate", "morph"]);
/* P58 T6 (b): the suffix that names the plane a mechanism happens at - build_scene_timeline_f.DEPTH_SUFFIX */
const MELT_DEPTH = "depth=";
/* the materials `melt:weight:<material>` may name (stopaction MASS / drop DROP.MAT); metal is the default, E88 s7 */
export const MELT_MATERIALS = Object.freeze(["metal", "ink", "paper", "liquid"]);
/* P61 T5b: the suffix that names the ball's BODY COLOUR - build_scene_timeline_f.BODY_SUFFIX */
const MELT_BODY = "body=";
/* P61 T5b / E99 s42: the body colours `melt:weight:...:body=<word>` may name, and the target each one melts to.
   A MATERIAL is the ball's mass and its damping (MELT_MATERIALS, above); a BODY is only its colour, which is why it
   is a suffix of its own and not a fifth material - test_transitions_e47 pins MELT_MATERIALS at the four it has.
     chart      the ball carries the CHART's own ink, by Kubelka-Munk - the ball that always shipped, and the look
                E99 s42 called "the prior work ... better". No target: `meltBodyInk` returns `meltInkOf` untouched,
                so the default melt's every string is the string it was.
     slate      the BOARD's own ink: `--lp-char: #25313C` (docs/content-video-engine/samples/
                scene-evidence-player.template.html:50), the same charcoal the brand tokens carry as `color.charcoal`
                (content/video_engine/channel-assets/money-physics/brand-tokens.json:12, "ink: contours, wordmark,
                body text"). The operator's "slate gray" is that token and not a new colour.
     reference  the blueprint's near-black metal: LIVING_METALLIC_DROP_RESEARCH_BLUEPRINT.md s3.3 (:198-201, gate tier
                PLAUSIBLE) - "Zero Diffuse Reflectance (k_d = 0) ... The albedo base color is pure black" and "The
                droplet silhouette is near-black, illuminated strictly by intense, focused specular highlights". So
                the target IS pure black and what makes the rendered ball near-black rather than black is the body
                gradient's own sheen stop and the specular spot over it, exactly as the finding describes. */
export const MELT_BODIES = Object.freeze({ chart: null, slate: "#25313C", reference: "#000000" });

const mc01 = (v) => (v <= 0 ? 0 : v >= 1 ? 1 : v);   /* the engine inlines every module into ONE scope, so a
   private helper carries the module's own prefix - `c01` is ink.mjs's */
const mSlump = (u) => { const k = mc01(u); return k * k; };
const mEase = (u) => { const k = mc01(u); return k * k * (3 - 2 * k); };

/* ---- the authored form ------------------------------------------------------------------------------------------ */
/* `melt` | `melt:throw` | `melt:splash:chart` | `melt:splash:plate`, `:<s>`, and on a throw `:<x>,<y>`, in any order after
   the name. P61 T6 / E99 s2 adds `gather` - a PHASE token beside `weight`, composable with both of them and with every
   ending: the sag becomes the page vortex gathered to the ball's own centre. Throws on anything else, so a typo in a
   shot table is a refusal and not a silent default. */
export const meltOpts = (exit, o = {}) => {
  const P = Object.assign({}, MELT, o), bits = String(exit == null ? "" : exit).split(":");
  const out = { name: bits[0] || "", secs: P.S, ending: null, to: null, weight: false, wmass: P.W_MASS, depth: 0, gather: false,
                wbody: "chart" };   /* P61 T5b / E99 s42: the ball's body colour - `chart` is the ball that shipped */
  let said = false;   /* did the row declare its own length? a weight phase lengthens only the DEFAULT window */
  const setEnding = (e) => {
    if (out.ending) throw new Error("melt: two endings (" + out.ending + " and " + e + ") - a melt ends one way");
    out.ending = e;
  };
  for (let i = 1; i < bits.length; i++) {
    const b = bits[i].trim();
    if (b === "") continue;
    if (b === "throw") { setEnding("throw"); continue; }
    if (b === "morph") { setEnding("morph"); continue; }   /* P61 T3 / R26-117: the ball becomes the next page's prop outline */
    if (b.indexOf(MELT_DEPTH) === 0) {   /* P58 T6 (b): the PLANE the ball melts at - the compiler's own vocabulary, range and words */
      if (out.depth) throw new Error("melt: two depths - a melt happens at ONE plane");
      const v = Number(b.slice(MELT_DEPTH.length));
      if (!Number.isFinite(v)) throw new Error("melt: " + b.slice(MELT_DEPTH.length) + " is not a number - depth=<k>, the share of the camera's move the ball takes (" + P.DEPTH_MIN + " = pinned to the frame, 1 = the flat plate)");
      if (!(v >= P.DEPTH_MIN && v <= P.DEPTH_MAX)) throw new Error("melt: depth " + v + " is outside " + P.DEPTH_MIN + ".." + P.DEPTH_MAX + " - the parallax factor a plane may take of the camera's move (kinetics/camera.mjs PARALLAX)");
      out.depth = v; continue;
    }
    if (b === "gather") { out.gather = true; continue; }   /* P61 T6 / E99 s2: the sag becomes the vortex, gathered to one point */
    if (b.indexOf(MELT_BODY) === 0) {   /* P61 T5b / E99 s42: the ball's BODY COLOUR - the compiler's own vocabulary and words */
      const w = b.slice(MELT_BODY.length);
      if (!Object.prototype.hasOwnProperty.call(MELT_BODIES, w)) {
        throw new Error("melt: " + w + " is not a body colour - body= takes " + Object.keys(MELT_BODIES).join(", "));
      }
      out.wbody = w; continue;
    }
    if (b === "weight") {   /* R26-118: the weight phase, and the material it is made of (metal unless it says) */
      out.weight = true;
      const nx = (bits[i + 1] || "").trim();
      if (nx && nx.indexOf(",") < 0 && nx !== "throw" && nx !== "splash" && nx !== "gather" && nx !== "morph" && nx.indexOf(MELT_DEPTH) !== 0 && nx.indexOf(MELT_BODY) !== 0 && !Number.isFinite(Number(nx))) {
        if (MELT_MATERIALS.indexOf(nx) < 0) {
          throw new Error("melt: " + nx + " is not a material - melt:weight takes " + MELT_MATERIALS.join(", "));
        }
        out.wmass = nx; i++;
      }
      continue;
    }
    if (b === "splash") {
      const nx = (bits[i + 1] || "").trim();
      if (nx !== "chart" && nx !== "plate") {
        throw new Error("melt: splash names no ending since E88 - say splash:chart (the splatter forms the next chart) or splash:plate (a narrative plate springs up out of it)");
      }
      setEnding("splash:" + nx); i++; continue;
    }
    if (b === "chart" || b === "plate") throw new Error("melt: " + b + " is a splash's ending - say splash:" + b);
    if (b.indexOf(",") >= 0) {
      const xy = b.split(",").map(Number);
      if (xy.length !== 2 || !xy.every((v) => Number.isFinite(v))) throw new Error("melt: " + b + " is not an x,y point in stage fractions");
      out.to = xy; continue;
    }
    const v = Number(b);
    if (!(Number.isFinite(v) && v > 0)) throw new Error("melt: " + b + " is neither a length in seconds, nor an ending (throw, splash:chart, splash:plate, morph), nor a phase (gather, weight), nor an x,y point");
    out.secs = v; said = true;
  }
  out.ending = out.ending || "throw";
  if (!said) {   /* a row that declared its own length gets exactly it; a default window makes room for what was asked for */
    if (out.weight) out.secs = P.S + P.W_S;   /* the four beats need their own seconds, not the compile's */
    if (out.gather) out.secs += P.G_S;        /* P61 T6: and the travel needs its own - three turns in 0.48 s is a jump */
    if (out.ending === "morph") out.secs += P.M_S;   /* P61 T3: and so does the HAND - the arriving page's morph runs in it */
  }
  if (out.to && out.ending !== "throw") throw new Error("melt: an x,y point is where a THROW goes - a splash lands on the board");
  out.to = out.to || [P.TO[0], P.TO[1]];
  return out;
};

/* ---- the phases ------------------------------------------------------------------------------------------------- */
/* THE WEIGHT PHASE's share of the window (R26-118): W_S seconds of it, capped at W_MAX, and exactly 0 unless the
   exit asked for it - which is why every melt that shipped is byte-identical. */
export const meltWeightShare = (secs, o = {}) => {
  const P = Object.assign({}, MELT, o), s = Math.max(0.05, +secs || P.S);
  if (!P.weight) return 0;
  return mc01(Math.min(P.W_S, P.W_MAX * s) / s);
};
export const meltShares = (o = {}) => {
  const P = Object.assign({}, MELT, o), w = meltWeightShare(P.secs, P), r = 1 - w;
  return [P.MELT_END * r, (P.BALL_END - P.MELT_END) * r, w, (1 - P.BALL_END) * r];
};
export const meltPhase = (u, o = {}) => {
  const P = Object.assign({}, MELT, o), k = mc01(u);
  const w = meltWeightShare(P.secs, P), r = 1 - w, mEnd = P.MELT_END * r, bEnd = P.BALL_END * r, wEnd = bEnd + w;
  /* GONE takes the boundary itself: (t - t0) / secs cannot be trusted to reach exactly 1 in floating point */
  if (u >= 1 - 1e-9) return { name: "gone", k: 1, from: 1, span: 0 };
  if (k < mEnd) return { name: "melt", k: k / mEnd, from: 0, span: mEnd };
  if (k < bEnd) return { name: "ball", k: (k - mEnd) / (bEnd - mEnd), from: mEnd, span: bEnd - mEnd };
  if (k < wEnd) return { name: "weight", k: (k - bEnd) / Math.max(1e-6, w), from: bEnd, span: w };
  return { name: "fly", k: (k - wEnd) / Math.max(1e-6, 1 - wEnd), from: wEnd, span: 1 - wEnd };
};
/* the outline's blur in px: up over the melt, back to 0 by the end of the ball (a ball is solid, not a cloud) */
export const meltBlur = (u, o = {}) => {
  const P = Object.assign({}, MELT, o), ph = meltPhase(u, P);
  /* P61 T6 / E99 s2 ("i don't want the melt to be blur or a wipe"): a GATHER never blurs. The sag's gooey threshold
     existed to FUSE neighbouring marks in place; a gather moves them instead, so there is nothing to fuse and the
     stdDeviation the engine writes is 0 on every frame of the window. */
  if (P.gather) return 0;
  if (ph.name === "melt") return P.BLUR * mEase(ph.k);
  if (ph.name === "ball") return P.BLUR * (1 - mEase(ph.k));
  return 0;   /* the weight phase and the ending: a ball is solid, not a cloud */
};
/* the throw's launch as a share of the window: the board is up until here, and the next chart's clock starts here */
export const meltRelease = (o = {}) => {
  const P = Object.assign({}, MELT, o), w = meltWeightShare(P.secs, P), from = P.BALL_END * (1 - w) + w;
  return from + P.ANTIC * (1 - from);
};
/* how long the engine holds the NEXT page's clock under a throw: the new chart draws once the board is clear. A splash
   holds nothing (the chart arrives built, through the stains) and no melt holds a world that is not a page. */
export const meltDrawDelay = (opts, incomingIsPage, o = {}) =>
  /* the release is read through the EXIT's own options (R26-118: a `melt:weight` holds the board over its weight phase
     too, and its window is longer), so the caller need not know which phases this melt has */
  (opts && opts.ending === "throw" && incomingIsPage)
    ? meltRelease(Object.assign({}, opts, o)) * Math.max(0.05, +opts.secs || MELT.S) : 0;

/* ---- P61 T3 / R26-117: THE HAND-OVER ----------------------------------------------------------------------------- */
/* WHERE the ball is finished and the next page's morph begins, as a share of the window: the end of the ball phase,
   after the weight phase when there is one. It is `meltRelease` without the throw's ANTIC - a hand-over has no
   wind-up, because the thing that moves next is the shape itself. */
export const meltHandAt = (o = {}) => {
  const P = Object.assign({}, MELT, o), w = meltWeightShare(P.secs, P);
  return P.BALL_END * (1 - w) + w;
};
/* how long the engine holds the NEXT page's clock under a `melt:morph` - exactly to the hand-over, so the page's
   morph opens on the frame the ball is finished on. Mirrors meltDrawDelay and returns 0 for every other ending. */
export const meltHandDelay = (opts, incomingIsPage, o = {}) =>
  (opts && opts.ending === "morph" && incomingIsPage)
    ? meltHandAt(Object.assign({}, opts, o)) * Math.max(0.05, +opts.secs || MELT.S) : 0;
/* ... and the SECONDS that hand runs for, which are the arriving page's `morph_s`: one clock, no gap. */
export const meltHandSecs = (opts, o = {}) => {
  const P = Object.assign({}, MELT, opts, o);
  return (1 - meltHandAt(P)) * Math.max(0.05, +P.secs || MELT.S);
};
/* THE RING THE PAGE IS HANDED, in the melting world's own px: the ball as it stands at the hand-over - where it
   compiled, plus the distance a `melt:weight` rolled it. A pure function of the ink box, the options and the seed,
   computed by the caller BEFORE the arriving page paints, so the page's prop outline is the ball's own geometry on
   the frame the ball is finished on, never a copy taken from the DOM a frame late. */
export const meltHandRing = (o = {}, rnd) => {
  const P = Object.assign({}, MELT, o), rect = P.rect;
  if (!rect) return null;
  const b = ballAt(rect, 1, rnd, Object.assign({}, P, { weight: false }));
  const secs = Math.max(0.05, +P.secs || P.S), wSpan = meltWeightShare(secs, P) * secs;
  const rest = P.weight ? meltWeightAt(wSpan, wSpan, b.r, Object.assign({}, P, { dir: meltRollDir(b.centre, rect, P) })) : null;
  const c = [b.centre[0] + (rest ? rest.x : 0), b.centre[1]];
  return { c, r: b.r, ring: ballCircle(c, b.r, P.CIRCLE_N) };
};

/* ---- the sag ---------------------------------------------------------------------------------------------------- */
const dripBump = (dx, w) => { const k = mc01(Math.abs(dx) / Math.max(1e-6, w)); const c = Math.cos(k * Math.PI / 2); return c * c; };
export const meltDrips = (rect, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), n = Math.max(1, P.DRIPS | 0), step = rect.w / n, out = [];
  for (let i = 0; i < n; i++) {
    out.push({ c: rect.x + step * (i + 0.5) + P.DRIP_JIT * step * (rnd(i) - 0.5),
               amp: 0.45 + 0.55 * rnd(40 + i), delay: P.DRIP_DELAY * rnd(70 + i), w: P.DRIP_W * rect.w });
  }
  return out;
};
export const meltDepth = (x, k, rect, drips, o = {}) => {
  const P = Object.assign({}, MELT, o), u = mc01(k);
  let deepest = 0;
  for (const d of drips) {
    const own = mSlump(mc01((u - d.delay) / Math.max(1e-6, 1 - d.delay)));
    deepest = Math.max(deepest, dripBump(x - d.c, d.w) * d.amp * own);
  }
  return rect.h * (P.SAG * deepest + P.BASE_SAG * mSlump(u));
};
export const meltTop = (x, k, rect, drips, o = {}) => {
  const P = Object.assign({}, MELT, o), u = mc01(k);
  let over = 0;
  for (const d of drips) over = Math.max(over, dripBump(x - d.c, d.w * 1.15) * d.amp);
  return rect.y + rect.h * P.TOP_SAG * mSlump(u) * (0.55 + 0.45 * over);
};
/* THE MELTING OUTLINE: a closed ring walked clockwise from the top-left - the top edge, the right side, the foot sampled
   right to left with the drips hung from it, the left side back up. Sampled even-ish all the way round: the closed
   centripetal Catmull-Rom (morphAPath) bulges between two knots far apart next to two that are not. */
export const meltOutline = (rect, k, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), n = Math.max(3, P.N | 0), drips = meltDrips(rect, rnd, P);
  const top = Math.max(2, P.TOP_N | 0), side = Math.max(1, P.SIDE_N | 0), foot = rect.y + rect.h, pts = [];
  for (let j = 0; j < top; j++) { const x = rect.x + rect.w * (j / (top - 1)); pts.push([x, meltTop(x, k, rect, drips, P)]); }
  const tR = meltTop(rect.x + rect.w, k, rect, drips, P), tL = meltTop(rect.x, k, rect, drips, P);
  for (let j = 1; j <= side; j++) pts.push([rect.x + rect.w, tR + (foot - tR) * (j / (side + 1))]);
  for (let j = n - 1; j >= 0; j--) {
    const x = rect.x + rect.w * (j / (n - 1));
    pts.push([x, foot + meltDepth(x, k, rect, drips, P)]);
  }
  for (let j = side; j >= 1; j--) pts.push([rect.x, tL + (foot - tL) * (j / (side + 1))]);
  return pts;
};
/* THE RUN: how far the ink's pixels smear down (px). It grows with the sag and drains back into the ball as it forms. */
export const meltRun = (phase, k, rect, o = {}) => {
  const P = Object.assign({}, MELT, o);
  if (phase === "melt") return P.RUN * rect.h * mSlump(k);
  if (phase === "ball") return P.RUN * rect.h * (1 - mEase(k));
  return 0;
};

/* ---- the gather (P61 T6 / E99 s2) -------------------------------------------------------------------------------
   THE MAP. One particle's HOME (x, y) to where it stands at u, about the point c, with the space's own Rmax. The five
   terms are the page VORTEX's (doc 29 s9.31, species/spiral.mjs `lpVortex`) - the point takes the nearest ink first,
   the radius falls slowly then fast, the whirl is differential so the core turns about four times the rim (arms, not
   a wheel), the particle stretches along the flow with its area kept, and it shrinks as it goes. The SIXTH is the
   ruling's: `G_KEEP` floors that shrink, so the ink AMASSES on the point instead of draining out of the world.
   Pure and closed-form (a seek renderer may not integrate): the same u twice is the same pose. */
export const meltGatherAt = (x, y, c, Rmax, u, o = {}) => {
  const P = Object.assign({}, MELT, o);
  const dx = x - c[0], dy = y - c[1], r = Math.hypot(dx, dy) || 1e-6, phi = Math.atan2(dy, dx);
  const rn = Math.min(1, r / Math.max(1e-6, Rmax));
  const ui = mc01((mc01(u) - P.G_LAG * rn) / (1 - P.G_LAG));
  const rr = r * (1 - Math.pow(ui, P.G_R_FALL));
  const th = P.G_TURNS * 2 * Math.PI * ui * (P.G_CORE_BASE + P.G_CORE_GAIN * Math.pow(1 - rn, P.G_CORE_FALL));
  const a = P.G_ALPHA * 4 * ui * (1 - ui), s = Math.max(P.G_KEEP, Math.pow(1 - ui, P.G_SHRINK));
  const ang = phi + th, q = scaleBy(s, a);   /* the area-preserving stretch along the tangent - squash.mjs's own helper, 42 s42.3 */
  return { x: c[0] + rr * Math.cos(ang), y: c[1] + rr * Math.sin(ang), th: th * 180 / Math.PI,
           tan: ang * 180 / Math.PI + 90, sx: q.sx, sy: q.sy, ui };
};
/* the same pose as a CSS transform (an HTML particle, about its own home) and as an SVG one (user units) */
export const meltGatherCss = (v, hx, hy) =>
  "translate(" + (v.x - hx).toFixed(2) + "px," + (v.y - hy).toFixed(2) + "px) rotate(" + v.tan.toFixed(2)
  + "deg) scale(" + v.sx.toFixed(4) + "," + v.sy.toFixed(4) + ") rotate(" + (v.th - v.tan).toFixed(2) + "deg)";
export const meltGatherSvg = (v, hx, hy) =>
  "translate(" + v.x.toFixed(2) + " " + v.y.toFixed(2) + ") rotate(" + v.tan.toFixed(2) + ") scale("
  + v.sx.toFixed(4) + " " + v.sy.toFixed(4) + ") rotate(" + (v.th - v.tan).toFixed(2) + ") translate("
  + (-hx).toFixed(2) + " " + (-hy).toFixed(2) + ")";
/* THE CONVERGENCE, as ONE number: the RMS distance of the mapped particles from the point, in px. It is what the
   probe reads - "it collects and amasses into a single point" is a spread that falls, every step, to the ball's own
   radius. A blur cannot make this number move; only travel can. */
export const meltGatherSpread = (homes, c, Rmax, u, o = {}) => {
  const pts = homes || [];
  if (!pts.length) return 0;
  let s = 0;
  for (const h of pts) {
    const v = meltGatherAt(h[0], h[1], c, Rmax, u, o);
    s += (v.x - c[0]) * (v.x - c[0]) + (v.y - c[1]) * (v.y - c[1]);
  }
  return Math.sqrt(s / pts.length);
};
/* THE POINT forming under the arriving ink: its alpha and its radius through the gather (0 before G_CORE_AT). */
export const meltGatherCore = (k, o = {}) => {
  const P = Object.assign({}, MELT, o), g = mc01((mc01(k) - P.G_CORE_AT) / Math.max(1e-6, 1 - P.G_CORE_AT));
  return { alpha: mEase(g), grow: P.G_CORE_SEED + (1 - P.G_CORE_SEED) * mEase(g), k: g };
};
/* THE VIBRATION (E49). NOT a new law: kinetics/drop.mjs's own FLOOR - the amplitude its decay never takes - lifted by
   G_VIB while the point is collecting, and let back down to the resting floor over the ball phase. `gain` is 1 at the
   gather and falls to 0 across G_VIB_FALL of the ball; a melt that never asked for a gather never calls this. */
export const meltVibGain = (phase, k, o = {}) => {
  const P = Object.assign({}, MELT, o);
  if (!P.gather) return 0;
  if (phase === "melt") return 1;
  if (phase === "ball") return 1 - mc01(mc01(k) / Math.max(1e-6, P.G_VIB_FALL));
  return 0;
};
export const meltVibFloor = (gain, o = {}) => {
  const P = Object.assign({}, MELT, o), g = 1 + (P.G_VIB - 1) * mc01(gain);
  return DROP.FLOOR.map((v) => v * g);
};

/* ---- the ball --------------------------------------------------------------------------------------------------- */
export const ballCircle = (c, r, n) => {
  const out = [];
  for (let i = 0; i < n; i++) { const a = 2 * Math.PI * (i / n); out.push([c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)]); }
  return out;
};
export const ballAt = (rect, k, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), src = meltOutline(rect, 1, rnd, P);
  const c = centroid(src), r = P.BALL_R * rect.h;
  /* WITHOUT the weight phase the target is the circle it always was; WITH it the target is the LIVING DROP's ring at
     the window's own t (E88 s7) - the ball that forms is already wriggling to contain itself. */
  const prep = morphAPrepare(src, meltBallRing(c, r, P), { n: P.RING_N });
  return { outline: morphAAt(prep, mEase(k)).outline, centre: c, r, k: mc01(k) };
};
/* the ball's boundary: a plain circle, or - under `melt:weight` - drop.mjs's Rayleigh ring at `te` (the window's own
   stepped seconds), excited by `excite` and turned by `spin` (the roll). Area-renormalised there, so it never grows. */
export const meltBallRing = (c, r, o = {}) => {
  const P = Object.assign({}, MELT, o);
  if (!P.weight && !P.gather) return ballCircle(c, r, P.CIRCLE_N);
  /* P61 T6: a GATHERED point is the living drop whether or not the row asked for weight - it is the thing the ink
     amasses into, and E99 s2 asks for it "vibrating with energy". `vib` is the gain meltVibGain returned; absent (every
     melt on the record) no FLOOR key is written at all, so drop.mjs reads its own and the goldens do not move. */
  const ring = { N: P.CIRCLE_N, spin: +P.spin || 0 };
  if (+P.vib > 0) ring.FLOOR = meltVibFloor(+P.vib, P);
  return dropRing(c, r, +P.te || 0, meltWeightMass(P), P.excite || [], ring);
};
/* THE SQUEEZE: the ink's scale about the ball's centre at ball-phase progress k - 1 at the start, and at the end the ink
   box's longer side is SQUEEZE ball-diameters. Monotone in k. */
export const meltSqueeze = (rect, r, k, o = {}) => {
  const P = Object.assign({}, MELT, o), end = Math.min(1, P.SQUEEZE * 2 * r / Math.max(1e-6, rect.w, rect.h));
  return 1 + (end - 1) * mEase(k);
};
/* the ink body's opacity at ball-phase progress k: none, then up to solid before the ball moves */
export const meltBodyAlpha = (k, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return mEase(mc01((k - P.BODY_FROM) / Math.max(1e-6, P.BODY_TO - P.BODY_FROM)));
};
/* the ball's radius as a share of BALL_R at ball-phase progress k: from a seed to whole, monotone */
export const meltBodyGrow = (k, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return P.BODY_SEED + (1 - P.BODY_SEED) * mEase(mc01(k / Math.max(1e-6, P.BODY_GROW)));
};
export const ballFlat = (outline, c, k, o = {}) => {
  const P = Object.assign({}, MELT, o), f = 1 - P.FLAT * mEase(k), g = 1 + (1 / Math.max(0.05, f) - 1) * 0.5;
  return outline.map((p) => [c[0] + (p[0] - c[0]) * g, c[1] + (p[1] - c[1]) * f]);
};
/* THE WEIGHT: the ball's squash `ts` seconds after it has formed (or hit the board) - stopaction's impactSquash on the
   melt's material, on the melt's hold. 0 on the contact frame, SQUASH on the next hold, released by the material. */
export const meltSettle = (ts, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return impactSquash(ts, P.MASS, P.HOLD, P.FPS, { IMPACT_SQUASH: P.SQUASH });
};

/* ---- the weight phase (R26-118) --------------------------------------------------------------------------------- */
/* the material the ball is made of: `melt:weight:<material>`, else METAL (E88 s7) */
export const meltWeightMass = (o = {}) => {
  const P = Object.assign({}, MELT, o);
  return MASS[P.wmass] ? P.wmass : P.W_MASS;
};
/* WHICH WAY IT ROLLS: the ending's own direction - toward the point the throw is going, or toward the middle of the
   board a splash will paint. Never 0: a roll with no direction is a wobble. */
export const meltRollDir = (centre, rect, o = {}) => {
  const P = Object.assign({}, MELT, o), sb = P.stagebox || rect, to = P.to || P.TO;
  const target = P.ending && P.ending !== "throw" ? rect.x + rect.w / 2 : sb.x + to[0] * sb.w;
  return target - centre[0] >= 0 ? 1 : -1;
};
/* THE FOUR BEATS, a pure function of the phase's own seconds `tw` (the caller steps the clock) and the ball's radius:
     tw < W_LAND        FALL    the last of its height, easing IN (HF-6: impacts ease in), the contact shadow tightening
                                from FAR to NEAR as it nears the board
     .. < W_ROLL        ROLL    rollXf: NO SLIP (the turn IS the distance over the radius), a constant friction bringing
                                it to a stop where the math says; the receiver's dip and the board's three-frame answer
                                are the contact's, and the squash along the travel is the material's (metal: none)
     .. < W_SETTLE      NUDGE   the lean back first (48 s48.6), then the second, shorter roll
     .. <= 1            SETTLE  the material's spring (groundDip / rebound) brings it to rest
   Returns the ball's offset from its resting place, the angle it has turned, the squash, the board's shake, the contact
   shadow (and where the shadow is, LAG_FRAMES behind it - HF-2), and the impulses the drop's surface is re-excited by,
   in the PHASE's own seconds (meltState offsets them into the window's clock). */
export const meltWeightAt = (tw, wsecs, r, o = {}) => {
  const P = Object.assign({}, MELT, o), W = Math.max(0.05, wsecs), mass = meltWeightMass(P);
  const dir = P.dir || 1, imp = massImpact(mass), fric = P.W_ROLL_FRICTION, rr = Math.max(1e-6, r);
  const tLand = P.W_LAND * W, tRoll = P.W_ROLL * W, tSet = P.W_SETTLE * W;
  const soft = (MASS[mass] || MASS.paper).squash_frames > 0 ? 1 : 0, v0 = Math.sqrt(2 * fric * P.W_ROLL_PX);
  const kick = (k) => DROP.KICK.map((v) => v * imp * k);
  /* the signed distance rolled `ts` seconds after the contact, and the speed it is going */
  const travel = (ts) => {
    if (!(ts > 0)) return { d: 0, v: 0 };
    const roll = rollXf(P.W_ROLL_PX, rr, fric, ts), tn = ts - (tRoll - tLand);
    let d = roll.s, v = roll.v;
    if (tn > 0) {
      v = 0;
      if (tn < P.W_ANTIC_S) d -= P.W_ANTIC_PX * Math.sin(Math.PI * tn / P.W_ANTIC_S);   /* the weight, sold first */
      else { const n = rollXf(P.W_NUDGE_PX, rr, fric, tn - P.W_ANTIC_S); d += n.s; v = n.v; }
    }
    return { d, v };
  };
  const st = { beat: "fall", x: 0, y: 0, h: 0, turn: 0, squash: { a: 0, theta: 0 }, shake: { x: 0, y: 0 },
               shadow: null, shadowX: 0, kick: [] };
  if (tw < tLand) {
    const u = mc01(tw / Math.max(1e-6, tLand));
    st.h = P.W_DROP_PX * (1 - u * u * u);
    st.y = -st.h;
    st.shadow = contactShadow(st.h, 0);
    return st;
  }
  const ts = tw - tLand, tr = travel(ts);
  st.beat = tw < tRoll ? "roll" : (tw < tSet ? "nudge" : "settle");
  st.x = dir * tr.d;
  st.turn = dir * tr.d / rr;                                   /* NO SLIP: the turn IS the distance over the radius */
  st.y = groundDip(ts, mass) + rebound(ts, mass, P.W_DROP_PX);  /* it rides the surface's dip; metal does not hop */
  st.squash = { a: impactSquash(ts, mass, P.HOLD, P.FPS, { IMPACT_SQUASH: P.SQUASH })
                   + soft * P.W_ROLL_SQUASH * mc01(tr.v / v0), theta: 0 };   /* stretched ALONG the travel */
  st.shake = groundShake(ts, mass, P.FPS);
  st.shadow = contactShadow(0, Math.abs(st.squash.a));
  st.shadowX = dir * travel(ts - STOP.LAG_FRAMES / P.FPS).d;    /* what it drags settles a frame behind it (HF-2) */
  st.kick = [{ at: tLand, a: kick(1) }];
  if (tw >= tRoll + P.W_ANTIC_S) st.kick.push({ at: tRoll + P.W_ANTIC_S, a: kick(P.W_NUDGE_K) });
  return st;
};
/* THE MARK THE ROLL TURNS. The ball is compiled from the chart's OWN ink and the sag leaves a knot in it - a streak of
   that ink at CORE concentration, the darkest the ball has. It is kept ON THE BALL'S FACE: the ball is flat ink, so
   the mark turns with it the way a mark on a coin's face does, at W_MARK_AT of the radius, its long axis along the
   local tangent. Without it a plain disc rolling reads as a SLIDE, which is the whole point of the beat. */
export const meltMarkAt = (c, r, turn, o = {}) => {
  const P = Object.assign({}, MELT, o), a = P.W_MARK_PHI + turn;
  return { x: c[0] + r * P.W_MARK_AT * Math.cos(a), y: c[1] + r * P.W_MARK_AT * Math.sin(a),
           rx: r * P.W_MARK_R, ry: r * P.W_MARK_R * P.W_MARK_FLAT, deg: (a + Math.PI / 2) * 180 / Math.PI };
};

/* ---- the colour ------------------------------------------------------------------------------------------------- */
const meltRFromKs = (ks) => { const k = Math.max(0, ks); return 1 + k - Math.sqrt(k * k + 2 * k); };
/* THE INK THE BALL IS MADE OF: the marks' colours mixed by Kubelka-Munk (the mean K/S per channel - a subtractive mix, not
   an average of lights) and concentrated `density` times. density 1 is the marks' own mix; above it, darker and deeper. */
export const meltMixInk = (hexes, density = 1) => {
  const list = (hexes || []).filter((h) => /^#[0-9a-fA-F]{6}$/.test(h));
  const use = list.length ? list : [MELT.INK_HEX], ks = [0, 0, 0];
  for (const h of use) hexToLin(h).forEach((v, i) => { ks[i] += ksFromR(v) / use.length; });
  return linToHex(ks.map((k) => meltRFromKs(k * Math.max(0.01, density))));
};

/* THE INK the marks become and the ball is made of: the dominant stroke, concentrated */
export const meltInkOf = (hexes, density = 1) => meltMixInk(((hexes || []).filter((h) => /^#[0-9a-fA-F]{6}$/.test(h))).slice(0, 1), density);
/* how far the marks have turned into that ink */
export const meltTint = (phase, k, o = {}) => {
  const P = Object.assign({}, MELT, o);
  if (phase === "melt") return P.TINT_MELT * mEase(k);
  if (phase === "ball") return P.TINT_MELT + (1 - P.TINT_MELT) * mEase(mc01(2 * k));
  return 1;
};

/* ---- the splash ------------------------------------------------------------------------------------------------- */
/* A SPLAT: a seeded lobed blob with a tail pointing BACK along its ray to the impact (`back`, radians), drawn as a closed
   centripetal Catmull-Rom - the shape an ink drop makes when it hits paper at an angle */
export const meltSplatPath = (x, y, r, back, tail, rnd, salt, o = {}) => {
  const P = Object.assign({}, MELT, o), n = Math.max(6, P.LOBES | 0), pts = [];
  for (let j = 0; j < n; j++) {
    const f = 2 * Math.PI * (j / n), c = Math.cos(f), rr = r * (0.72 + 0.5 * rnd(salt * 31 + j)) + (c > 0 ? Math.pow(c, 8) * tail : 0);
    pts.push([x + Math.cos(back + f) * rr, y + Math.sin(back + f) * rr]);
  }
  return morphAPath(pts);
};
/* the satellite droplets thrown off behind each splat, along its ray */
export const splashSats = (drops) => {
  const out = [];
  for (const d of drops) {
    if (!(d.d > 0)) continue;
    const cx = Math.cos(d.a), cy = Math.sin(d.a), ox = d.x - cx * d.d, oy = d.y - cy * d.d;
    out.push({ x: ox + cx * d.d * 0.62, y: oy + cy * d.d * 0.62, r: d.r * 0.32 }, { x: ox + cx * d.d * 0.83, y: oy + cy * d.d * 0.83, r: d.r * 0.2 });
  }
  return out;
};
/* the plate's spring over the paint clock: up from 1 - SPRING, over its rest, settled at g = 1 (exactly 1 there) */
export const meltSpring = (g, o = {}) => {
  const P = Object.assign({}, MELT, o), k = mc01(g);
  return k >= 1 ? 1 : 1 - P.SPRING * Math.exp(-3 * k) * Math.cos(2.5 * Math.PI * k);
};
/* the distance from c along the unit ray (cx, cy) to the box's edge */
const meltRayToEdge = (c, cx, cy, rect) => {
  const tx = cx > 1e-9 ? (rect.x + rect.w - c[0]) / cx : cx < -1e-9 ? (rect.x - c[0]) / cx : Infinity;
  const ty = cy > 1e-9 ? (rect.y + rect.h - c[1]) / cy : cy < -1e-9 ? (rect.y - c[1]) / cy : Infinity;
  return Math.max(0, Math.min(tx, ty));
};
/* THE SPLATTER: DROPS droplets thrown out along seeded rays on the soak's own STEPPED clock (never contracting), each
   LANDING on the board - a share of the way to the ink box's edge - and spreading a little as it lands. `d` is the
   distance travelled along its ray: monotone in k and never past `land`. */
export const splashDrops = (c, rect, k, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), p = soakStepped(mc01(k), rnd), out = [];
  for (let i = 0; i < Math.max(0, P.DROPS | 0); i++) {
    const a = 2 * Math.PI * (i / P.DROPS) + P.SPLASH_SPREAD * (2 * rnd(300 + i) - 1), cx = Math.cos(a), cy = Math.sin(a);
    const land = meltRayToEdge(c, cx, cy, rect) * (P.LAND_MIN + (P.LAND_MAX - P.LAND_MIN) * rnd(400 + i)), d = land * p;
    const r = P.DROP_R * rect.h * (0.6 + 0.8 * rnd(500 + i)) * (1 + 0.6 * p);
    out.push({ x: c[0] + cx * d, y: c[1] + cy * d, r, d, a, land, tail: p > 0 ? r * (P.TAIL + 3 * (1 - p)) : 0 });
  }
  return out;
};
/* THE PAINT: every landed drop grows as a seeded stain (its own stepped staircase), and one grows under the ball's own
   impact. Radii are monotone in g. `cover` is the board's remaining opacity (whole until FLOOD_FROM, then out to exactly
   0), `rim` the wet ink at the fronts (drying as they spread). */
export const splashStains = (drops, c, r, rect, g, rnd, o = {}) => {
  const P = Object.assign({}, MELT, o), h = rect.h, gg = mc01(g);
  const grow = (salt) => (gg <= 0 ? 0 : soakStepped(gg, (k) => rnd(1000 + 37 * salt + k)));
  const stains = drops.map((d, i) => ({ x: d.x, y: d.y, r: d.r + (P.REVEAL_R * h * (0.6 + 0.8 * rnd(600 + i)) - d.r) * grow(i + 1) }));
  stains.push({ x: c[0], y: c[1], r: r + (P.CORE_R * h - r) * grow(0) });
  return { stains, cover: 1 - mEase(mc01((gg - P.FLOOD_FROM) / Math.max(1e-6, 1 - P.FLOOD_FROM))), rim: 1 - mEase(gg) };
};

/* ---- the throw -------------------------------------------------------------------------------------------------- */
/* THE FLIGHT, BACKWARDS: throwXf brings a thing FROM an offset TO its rest; a launch is that landing in reverse. t' = F(1 - k):
   at k = 0 the ball sits at rest and at k = 1 it is at `from`. The ball's ARC and SPIN_DEG are its own (heavy). */
export const meltThrowAt = (k, from, secs, o = {}) => {
  const P = Object.assign({}, MELT, o), F = Math.max(0.05, secs), kk = mc01(k);
  if (kk <= 0) return { x: 0, y: 0, rot: 0, alpha: 0, theta: Math.PI / 2, phase: "flight", u: 1, hold: 1, h: 0, ground: 0, shake: { x: 0, y: 0 } };
  return throwXf(from, P.MASS, F * (1 - kk), { FLIGHT_S: F, ARC: P.ARC, SPIN_DEG: P.SPIN_DEG });
};

/* ---- the frame -------------------------------------------------------------------------------------------------- */
/* EVERYTHING THE PAINTER NEEDS, in one object, from (t0, t, o, rnd) alone. o carries the geometry as well as any dial:
   `rect` (the INK box, in the outgoing world's own px), `stagebox` (the stage's box in those px), `secs`, `ending`, `to`.
     path     the ink's mask, in the ink's own (unsqueezed) px     body      the ball, in world px (null: no ball)
     scale    the ink's squeeze about `centre`                     bodyAlpha the ball's opacity
     run      the ink's smear, px; inkBlur its blur                 squash    { a, theta } on the ball, stopaction's tensor
     xf       the throw's offset and tumble                        drops     the splatter; stains / cover / rim the paint
     boardUp  the outgoing board is on screen                      reveal    it wears the reveal mask; spring the plate's scale
     weight   which beat of the weight phase (null: none)          turn      how far the ball has rolled, radians
     mark     the ink knot the roll turns (null: no weight)        hl        the specular highlight, pinned to the light
     shadow   the contact shadow's scale/alpha/blur                shadowX   where it is, a frame behind the ball */
export const meltState = (t0, t, o = {}, rnd) => {
  const P = Object.assign({}, MELT, o), rect = P.rect, sb = P.stagebox || rect, to = P.to || P.TO;
  const ending = MELT_ENDINGS.indexOf(P.ending) >= 0 ? P.ending : "throw";
  const secs = Math.max(0.05, +P.secs || P.S), u = mc01((t - t0) / secs), ph = meltPhase(u, P);
  const st = { u, secs, ending, phase: ph.name, k: ph.k, blur: meltBlur(u, P), inkBlur: 0, run: 0, scale: 1,
               inkOpacity: 1, path: "", outline: null, body: "", bodyOutline: null, bodyAlpha: 0, centre: null, r: 0,
               squash: { a: 0, theta: 0 }, xf: null, drops: [], stains: [], cover: 1, rim: 0, reveal: false,
               spring: 1, dropAlpha: 1, dropScale: 1, tint: 0, sats: [], textOpacity: 0, boardUp: true, gone: false,
               weight: null, turn: 0, mark: null, hl: null, shadow: null, shadowX: 0, shake: { x: 0, y: 0 },
               mass: false, occl: null, gather: null };   /* P61 T6: `gather` is the particles' clock and their
               point, and it is null for every melt that did not ask - the engine mounts no particles for those.
               P61 T5: `mass` is the one flag the three MATERIAL overlays ride - true
               exactly when a `melt:weight` has a ball on screen; `occl` is the contact shadow's own dark core */
  st.inkBlur = P.INK_BLUR * st.blur / Math.max(1e-6, P.BLUR);
  if (ph.name === "gone") { st.gone = true; st.boardUp = false; st.inkOpacity = 0; st.cover = 0; return st; }
  /* P61 T6 / E99 s2 - THE GATHER replaces the sag for a melt that asked for it: no outline, no mask, no blur and no
     run. The ink does not smear where it stands, it TRAVELS (the engine walks the particles through meltGatherAt),
     and the point it travels to is the ball's own centre - so the gather hands the ball phase a mass that is already
     where the ball forms. The point opens under the arriving ink at G_CORE_AT and vibrates from its first frame. */
  if (ph.name === "melt" && P.gather) {
    const b = ballAt(rect, 1, rnd, Object.assign({}, P, { weight: false, gather: false }));
    const core = meltGatherCore(ph.k, P), vib = meltVibGain("melt", ph.k, P);
    const tqw = stepped(Math.max(0, t - t0), P.HOLD, P.FPS);   /* the drop's clock is the WINDOW's, on 2s */
    st.blur = 0; st.inkBlur = 0; st.run = 0;
    st.centre = b.centre; st.r = b.r;
    st.tint = P.G_DEEP * mEase(ph.k);   /* the marks turn to the ball's own ink as they arrive: one mass, not four series */
    st.textOpacity = 1;                 /* the words TRAVEL - they do not drip and they do not fade in place */
    st.gather = { on: true, k: ph.k, c: b.centre, R: Math.hypot(rect.w, rect.h) / 2 };
    if (core.alpha > 0) {
      const r = b.r * core.grow, mass = meltWeightMass(P);
      st.bodyAlpha = core.alpha; st.mass = true;   /* the point wears T5's material from the frame it exists */
      st.bodyOutline = meltBallRing(b.centre, r, Object.assign({}, P, { te: tqw, vib }));
      st.body = morphAPath(st.bodyOutline);
      st.hl = dropSpecular(b.centre, r, dropModes(tqw, r, mass, [], { FLOOR: meltVibFloor(vib, P) }));
    }
    return st;
  }
  if (ph.name === "melt") {
    st.outline = meltOutline(rect, ph.k, rnd, P);
    st.path = morphAPath(st.outline);
    st.run = meltRun("melt", ph.k, rect, P);
    st.tint = meltTint("melt", ph.k, P);
    st.textOpacity = meltTextAlpha(ph.k);   /* the words run down as their own glyphs and are gone by the ball */
    return st;
  }
  /* the ball and the ending run on the STEPPED clock, each on its own phase-local seconds (a pure quantisation of t) */
  const tl = t - t0 - ph.from * secs, span = ph.span * secs, tq = stepped(Math.max(0, tl), P.HOLD, P.FPS);
  const kq = mc01(tq / Math.max(1e-6, span));
  /* THE DROP's own clock is the WINDOW's, not a phase's: the surface rings on across the boundaries, and the compile's
     and the landing's impulses are stamped in these seconds. `wShare` is 0 unless the exit asked for weight. */
  const tqw = stepped(Math.max(0, t - t0), P.HOLD, P.FPS);
  const wShare = meltWeightShare(secs, P), rest0 = 1 - wShare;
  const bStart = P.MELT_END * rest0 * secs, wStart = P.BALL_END * rest0 * secs, wSpan = wShare * secs;
  const wMass = meltWeightMass(P), born = [{ at: bStart, a: DROP.A }];   /* the compile's own excitation (E88 s7) */
  if (ph.name === "ball") {
    /* P61 T6: under a gather the point is ALREADY there and already alive - the ink amassed on it - so the ball phase
       only lets the vibration settle (meltVibGain falls to 0 across G_VIB_FALL) and the ink is gone, not squeezed. */
    const vib = meltVibGain("ball", kq, P);
    const b = ballAt(rect, kq, rnd, Object.assign({}, P, { te: tqw, excite: born, vib })), s = meltSqueeze(rect, b.r, kq, P);
    st.k = kq; st.centre = b.centre; st.r = b.r; st.scale = s;
    st.bodyOutline = b.outline; st.bodyAlpha = P.gather ? 1 : meltBodyAlpha(kq, P);
    /* the SOLID ball: a crisp circle, never the box - and under `melt:weight` (or a gather) the living drop's own ring */
    st.body = morphAPath(meltBallRing(b.centre, b.r * (P.gather ? 1 : meltBodyGrow(kq, P)), Object.assign({}, P, { te: tqw, excite: born, vib })));
    if (P.weight || P.gather) { st.mass = true; st.hl = dropSpecular(b.centre, b.r * (P.gather ? 1 : meltBodyGrow(kq, P)), dropModes(tqw, b.r, wMass, born, { FLOOR: meltVibFloor(vib, P) })); }
    st.tint = meltTint("ball", kq, P);
    st.inkBlur = P.gather ? 0 : st.inkBlur + P.BALL_FUSE * mEase(kq);   /* the marks FUSE into one body as they compact - a GATHER has no ink left to fuse, and writes no blur anywhere in its window */
    /* the mask is in the ink's own px, and the ink is squeezed by s about the centre: the same body, unsqueezed */
    st.outline = b.outline.map((p) => [b.centre[0] + (p[0] - b.centre[0]) / s, b.centre[1] + (p[1] - b.centre[1]) / s]);
    st.path = morphAPath(st.outline);
    st.run = meltRun("ball", kq, rect, P);
    st.inkOpacity = P.gather ? 0 : 1 - mEase(mc01(kq / Math.max(1e-6, P.INK_OUT)));
    return st;
  }
  /* the compiled ball: its centre and radius are the geometry's, whatever its surface is doing */
  const b = ballAt(rect, 1, rnd, Object.assign({}, P, { weight: false }));
  const dir = meltRollDir(b.centre, rect, P);
  if (ph.name === "weight") {
    const wst = meltWeightAt(tq, span, b.r, Object.assign({}, P, { dir }));
    const excite = born.concat(wst.kick.map((k) => ({ at: wStart + k.at, a: k.a })));
    st.k = kq; st.centre = b.centre; st.r = b.r; st.inkOpacity = 0; st.bodyAlpha = 1;
    st.weight = wst.beat; st.turn = wst.turn; st.squash = wst.squash; st.shake = wst.shake;
    st.shadow = wst.shadow; st.shadowX = wst.shadowX;
    st.occl = meltOcclusion(wst.shadow, b.r, P);   /* P61 T5 / E99 s3 (a): the board the ball OCCLUDES, over the cast slit */
    st.mass = true;
    st.bodyOutline = dropRing(b.centre, b.r, tqw, wMass, excite, { N: P.CIRCLE_N, spin: wst.turn });
    st.body = morphAPath(st.bodyOutline);
    st.xf = { x: wst.x, y: wst.y, rot: 0, alpha: wst.squash.a, theta: wst.squash.theta, phase: wst.beat, u: kq,
              hold: P.HOLD, h: wst.h, ground: 0, shake: wst.shake };
    st.mark = meltMarkAt(b.centre, b.r, wst.turn, P);
    st.hl = dropSpecular(b.centre, b.r, dropModes(tqw, b.r, wMass, excite, { spin: wst.turn }));
    return st;
  }
  /* THE ENDING. Under `melt:weight` it starts from where the roll left the ball - its offset, its turn and the
     impulses its surface still carries (the drop rings on into the flight or the splash). */
  const rest = P.weight ? meltWeightAt(wSpan, wSpan, b.r, Object.assign({}, P, { dir })) : null;
  const restX = rest ? rest.x : 0, spin = rest ? rest.turn : 0;
  const excite = rest ? born.concat(rest.kick.map((k) => ({ at: wStart + k.at, a: k.a }))) : born;
  const circle = P.weight ? dropRing(b.centre, b.r, tqw, wMass, excite, { N: P.CIRCLE_N, spin })
                          : ballCircle(b.centre, b.r, P.CIRCLE_N);
  st.k = kq; st.centre = b.centre; st.r = b.r; st.inkOpacity = 0; st.bodyAlpha = 1;
  if (P.weight) {
    st.turn = spin;
    st.mark = meltMarkAt(b.centre, b.r, spin, P);
    st.hl = dropSpecular(b.centre, b.r, dropModes(tqw, b.r, wMass, excite, { spin }));
    st.mass = true;
  }
  if (ending === "morph") {
    /* P61 T3 / R26-117 - THE HAND. The ball is finished; the arriving page's `page_enter:morph` opened on this very
       frame with the ball's ring as its prop (`meltHandRing` -> `world.morph.poly`), and from here the two are one
       shape on one clock. `P.hand` is that shape as the page has it THIS frame, carried back into this world's px by
       the caller: the ball's body wears it, so what deforms is the body the eye has been watching and not a copy of
       it. Its paint gives way to the page's own ink over M_FADE - the one cross-over in the window, on a single
       shape, mid-deformation, which is why no frame here is a cut in a costume (E99 s39).
       With no hand yet (the page not laid out, the flag off) the body stays the ball's own circle: a `melt:morph`
       that cannot find its page holds the ball and ends, and never invents a shape. */
    const hand = Array.isArray(P.hand) && P.hand.length >= 3 ? P.hand : null;
    st.bodyOutline = hand || circle;
    st.body = morphAPath(st.bodyOutline);
    st.bodyAlpha = 1 - mc01(kq / Math.max(1e-6, P.M_FADE));   /* LINEAR: an eased fade front-loads and the swap lands in a few frames */
    if (restX && !hand) st.xf = { x: restX, y: 0, rot: 0 };   /* a handed outline is already where it is */
    /* THE BOARD HANDS OVER HERE, exactly as a throw's does at its release: the arriving page's charcoal has been the
       ground under this world since its own first frame (a morph page skips the roll, the savor and the soak), so the
       outgoing board steps aside and the page's rising ink is no longer behind it. The ball rides on, in the overlay
       above both. */
    st.boardUp = false;
    return st;
  }
  if (ending === "throw") {
    st.bodyOutline = circle; st.body = morphAPath(circle);
    if (kq < P.ANTIC) {
      st.squash = { a: meltSettle(tq, P), theta: 0 };   /* stretched ACROSS, pressed down: the ball has weight before it moves */
      st.xf = meltThrowAt(0, { x: 0, y: 0 }, span, P);
    } else {
      const from = { x: sb.x + to[0] * sb.w - b.centre[0] - restX, y: sb.y + to[1] * sb.h - b.centre[1] };
      st.xf = meltThrowAt((kq - P.ANTIC) / Math.max(1e-6, 1 - P.ANTIC), from, span * (1 - P.ANTIC), P);
      st.squash = { a: st.xf.alpha || 0, theta: st.xf.theta || 0 };   /* stretched along the flight */
    }
    if (restX) st.xf = Object.assign({}, st.xf, { x: (st.xf.x || 0) + restX });
    st.boardUp = u < meltRelease(P);
    return st;
  }
  /* a SPLASH: the burst, then the paint. Its clock is measured to ONE HOLD before the window ends: the stepped clock's last
     pose lands a hold early, and a paint that was 0.8 done on that pose would pop the board's last cover at `gone`. */
  const ks = mc01(tq / Math.max(1e-6, span - P.HOLD / P.FPS));
  const kb = mc01(ks / Math.max(1e-6, P.BURST_END)), g = mc01((ks - P.BURST_END) / Math.max(1e-6, 1 - P.BURST_END));
  const sc = [b.centre[0] + restX, b.centre[1]];   /* it bursts where the roll left it */
  st.bodyOutline = ballFlat(circle, b.centre, kb, P); st.body = morphAPath(st.bodyOutline);
  st.bodyAlpha = 1 - mEase(mc01((kb - 0.5) / 0.5));   /* the ball holds its mass through the hit, then IS the splatter */
  st.squash = { a: meltSettle(tq, P), theta: 0 };
  if (restX) st.xf = { x: restX, y: 0, rot: 0 };
  st.drops = splashDrops(sc, rect, kb, rnd, P);
  st.sats = splashSats(st.drops);
  if (kq >= P.BURST_END) {
    const paint = splashStains(st.drops, sc, b.r, rect, g, rnd, P);
    st.stains = paint.stains; st.cover = paint.cover; st.rim = paint.rim; st.reveal = true;
    const rate = ending === "splash:chart" ? P.SPLAT_OUT : 2.5;
    st.dropAlpha = 1 - mEase(mc01(g * rate));   /* a drop IS its stain's first ink: it soaks away as the stain opens */
    if (ending === "splash:chart") st.dropScale = 1 - P.SPLAT_SHRINK * mEase(mc01(g * 2));
    if (ending === "splash:plate") st.spring = meltSpring(g, P);
  }
  return st;
};

/* ---- the markup the painter mounts once ------------------------------------------------------------------------- */
/* THE GOOEY THRESHOLD as SVG primitives: blur, then re-steepen the alpha. Blur FIRST, then the ramp - the other way round
   is a fade. The K-M colour stages are deliberately not here: they would flatten what they filter to one ink. */
export const meltFilterMarkup = (id, u, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return '<filter id="' + id + '" x="-40%" y="-40%" width="180%" height="180%" color-interpolation-filters="sRGB">'
    + '<feGaussianBlur stdDeviation="' + meltBlur(u, P).toFixed(2) + '"/>'
    + '<feComponentTransfer><feFuncA type="linear" slope="' + P.EDGE_SLOPE + '" intercept="0"/></feComponentTransfer>'
    + '</filter>';
};
/* the mask the melting ink wears: one path, filtered */
export const meltMaskMarkup = (id, filterId) =>
  '<mask id="' + id + '" maskUnits="objectBoundingBox" x="-0.4" y="-0.4" width="1.8" height="1.8">'
  + '<g filter="url(#' + filterId + ')"><path fill="#fff" d=""/></g></mask>';
/* THE RUN on the marks' own pixels: RUN_COPIES copies offset downward and merged over the original, then the gooey
   threshold - the lines swell, trail down and fuse. The region opens downward, where the ink goes. */
export const meltInkFilterMarkup = (id, o = {}) => {
  const P = Object.assign({}, MELT, o);
  /* the marks first lose every FAINT pixel (alpha under a quarter): a near-transparent wash on the page - a grain, a plot
     ground - would otherwise be ramped INK_SLOPE times into an opaque grey slab over the board (measured on the first
     proof frame, 2026-09-13). A mark's own core is opaque and passes untouched. */
  let offs = "", merge = '<feMergeNode in="' + id + 'k"/>';
  for (let j = 1; j <= Math.max(1, P.RUN_COPIES | 0); j++) {
    offs += '<feOffset in="' + id + 'k" dx="0" dy="0" result="' + id + "r" + j + '"/>';
    merge += '<feMergeNode in="' + id + "r" + j + '"/>';
  }
  return '<filter id="' + id + '" x="-5%" y="-5%" width="110%" height="150%" color-interpolation-filters="sRGB">'
    + '<feComponentTransfer in="SourceGraphic" result="' + id + 'k"><feFuncA type="table" tableValues="0 0 1 1 1"/></feComponentTransfer>'
    + offs + "<feMerge>" + merge + "</feMerge>"
    + '<feGaussianBlur stdDeviation="0"/>'
    + '<feComponentTransfer result="' + id + 'o"><feFuncA type="linear" slope="' + P.INK_SLOPE + '" intercept="0"/></feComponentTransfer>'
    /* THE TINT: the fused marks turned toward THE INK by k2 (the painter writes k2 = tint, k3 = 1 - tint each frame) */
    + '<feFlood flood-color="#000" result="' + id + 'c"/><feComposite in="' + id + 'c" in2="' + id + 'o" operator="in" result="' + id + 't"/>'
    + '<feComposite in="' + id + 't" in2="' + id + 'o" operator="arithmetic" k1="0" k2="0" k3="1" k4="0"/></filter>';
};
/* THE REVEAL: a luminance mask the BOARD wears under a splash - white everywhere, and the stains cut black through it,
   under their own gooey threshold, so two stains that meet run together */
export const meltRevealMarkup = (id, filterId) =>
  '<mask id="' + id + '" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="-10000" y="-10000" width="20000" height="20000">'
  + '<rect x="-10000" y="-10000" width="20000" height="20000" fill="#fff"/><g filter="url(#' + filterId + ')"></g></mask>';
export const meltStainFilterMarkup = (id, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return '<filter id="' + id + '" x="-50%" y="-50%" width="200%" height="200%" color-interpolation-filters="sRGB">'
    + '<feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="3" seed="11" result="' + id + 'n"/>'
    + '<feDisplacementMap in="SourceGraphic" in2="' + id + 'n" scale="' + P.STAIN_RAG + '" xChannelSelector="R" yChannelSelector="G"/>'
    + '<feGaussianBlur stdDeviation="' + P.STAIN_BLUR + '"/>'
    + '<feComponentTransfer><feFuncA type="linear" slope="' + P.STAIN_SLOPE + '" intercept="0"/></feComponentTransfer></filter>';
};
/* a SPLAT's torn edge: the soak's noise displacement and nothing else - no blur, so the ink stays opaque and crisp */
export const meltSplatFilterMarkup = (id, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return '<filter id="' + id + '" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
    + '<feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="5" result="' + id + 'n"/>'
    + '<feDisplacementMap in="SourceGraphic" in2="' + id + 'n" scale="' + P.SPLAT_RAG + '" xChannelSelector="R" yChannelSelector="G"/></filter>';
};
/* a colour taken toward white by `k` (linear light) - the ball's one sheen */
export const meltSheen = (hex, k) => linToHex(hexToLin(hex).map((v) => v + (1 - v) * mc01(k)));
/* P61 T5: and its MIRROR - a colour taken toward BLACK by `k` (linear light), the ball's shadows. It is a separate
   thing from meltInkOf's Kubelka-Munk concentration on purpose: K-M mixes PIGMENT, and more pigment on an orange
   stroke saturates toward a bright red (#fc0c03 at 34x) - it can never reach a shadow. A shadow is less light. */
export const meltShade = (hex, k) => linToHex(hexToLin(hex).map((v) => v * (1 - mc01(k))));
/* P61 T5b / E99 s42: THE BALL'S INK AT A DENSITY, IN THE BODY COLOUR IT WAS AUTHORED IN. `chart` (the default, and a
   melt that names no body at all) has NO target, so this returns `meltInkOf` itself and every default string is the
   string that shipped - that identity is what keeps the flag-off goldens byte-identical, and a test asserts it.
   A named body (slate, reference - MELT_BODIES) melts the ink toward its target AT THIS STOP'S OWN LEVEL: the target
   is scaled by the stop's share of the LIT stop's luminance, so the light-to-core ramp the K-M concentration built is
   kept and only the hue and the level move. The lerp is in LINEAR light, like meltSheen and meltShade. */
const mLum = (lin) => 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
export const meltBodyInk = (hexes, density, o = {}) => {
  const P = Object.assign({}, MELT, o), ink = meltInkOf(hexes, density);
  const to = MELT_BODIES[P.wbody || "chart"];
  if (!to) return ink;
  const a = hexToLin(ink), share = mLum(a) / Math.max(1e-6, mLum(hexToLin(meltInkOf(hexes, P.LIGHT))));
  const t = hexToLin(to).map((v) => v * share), k = mc01(P.W_BODY_SHADE);
  return linToHex(a.map((v, i) => v + (t[i] - v) * k));
};
/* the ball's body: THE INK, one small highlight up and to the left, the stroke, then concentrated toward its shaded side */
export const meltBodyGradientMarkup = (id, hexes, o = {}) => {
  const P = Object.assign({}, MELT, o), lit = meltBodyInk(hexes, P.LIGHT, P);
  return '<radialGradient id="' + id + '" cx="0.34" cy="0.3" r="0.8" fx="0.32" fy="0.26">'
    + '<stop offset="0" stop-color="' + meltSheen(lit, P.SHEEN) + '"/>'
    + '<stop offset="0.14" stop-color="' + lit + '"/>'
    + '<stop offset="0.55" stop-color="' + meltBodyInk(hexes, P.INK_DEEP, P) + '"/>'
    + '<stop offset="1" stop-color="' + meltBodyInk(hexes, P.CORE, P) + '"/></radialGradient>';
};
/* ---- P61 T5 / E99 s3: THE BALL'S SHADOWS - the three overlays' paint ---------------------------------------------
   Each of the three wears the BODY'S OWN path (`st.body`), so it is clipped to the living drop's silhouette exactly,
   at every t, with no clipPath and no second geometry to keep in step - and each is mounted the first frame a
   `melt:weight` asks for it, so a melt that never asks has the defs, the DOM and the strings it always had.
   The profiles are DROP's (kinetics/drop.mjs, with their gate tiers); the ink is the ball's own, by Kubelka-Munk. */

/* (b) THE DARK GRAZING RIM: a CONCENTRIC radial gradient over the body's box - transparent through the middle, then
   DROP's grazing term in the deepest ink, monotone to the silhouette. Its stops crowd the edge (1 - (1 - i/n)^2),
   because the profile does almost all of its rising in the last tenth of the radius. */
export const meltRimGradientMarkup = (id, hexes, o = {}) => {
  const P = Object.assign({}, MELT, o), deep = meltShade(meltInkOf(hexes, P.CORE), P.W_RIM_SHADE), n = Math.max(2, P.W_RIM_STOPS | 0);
  let s = '<radialGradient id="' + id + '" cx="0.5" cy="0.5" r="0.5">'
    + '<stop offset="0" stop-color="' + deep + '" stop-opacity="0"/>';
  for (let i = 0; i <= n; i++) {
    const u = i / n, off = DROP.RIM_AT + (1 - DROP.RIM_AT) * (1 - (1 - u) * (1 - u));
    s += '<stop offset="' + off.toFixed(4) + '" stop-color="' + deep + '" stop-opacity="' + dropRimAlpha(off, P).toFixed(4) + '"/>';
  }
  return s + '</radialGradient>';
};

/* (c) THE METALLIC BAND: a LINEAR gradient run along the light axis (dropLightAxis), so the stripe it paints is
   always NORMAL to the light - the anisotropic reflection a turned metal sphere carries, in the ball's lit ink taken
   W_BAND_K toward white. */
export const meltBandGradientMarkup = (id, hexes, o = {}) => {
  const P = Object.assign({}, MELT, o), ax = dropLightAxis(P), n = Math.max(2, P.W_BAND_STOPS | 0);
  const lit = meltSheen(meltInkOf(hexes, P.LIGHT), P.W_BAND_K);
  let s = '<linearGradient id="' + id + '" x1="' + ax.x1.toFixed(4) + '" y1="' + ax.y1.toFixed(4)
    + '" x2="' + ax.x2.toFixed(4) + '" y2="' + ax.y2.toFixed(4) + '">';
  for (let i = 0; i <= n; i++) {
    const p = i / n;
    s += '<stop offset="' + p.toFixed(4) + '" stop-color="' + lit + '" stop-opacity="' + dropBandAlpha(p, P).toFixed(4) + '"/>';
  }
  return s + '</linearGradient>';
};

/* (d) THE POINT OF DEEP SHADOW DEPTH: a small radial gradient seated OPPOSITE the light (dropDeepPoint, read in the
   body's box where the ball's radius is 0.5), falling off by DROP's PIT_GAMMA - one well of real depth on the ball. */
export const meltPitGradientMarkup = (id, hexes, o = {}) => {
  const P = Object.assign({}, MELT, o), deep = meltShade(meltBodyInk(hexes, P.CORE, P), P.W_PIT_SHADE), n = Math.max(2, P.W_PIT_STOPS | 0);
  const seat = dropDeepPoint([0.5, 0.5], 0.5, P);
  let s = '<radialGradient id="' + id + '" cx="' + seat.x.toFixed(4) + '" cy="' + seat.y.toFixed(4)
    + '" r="' + seat.r.toFixed(4) + '">';
  for (let i = 0; i <= n; i++) {
    const u = i / n;
    s += '<stop offset="' + u.toFixed(4) + '" stop-color="' + deep + '" stop-opacity="' + dropPitAlpha(u, P).toFixed(4) + '"/>';
  }
  return s + '</radialGradient>';
};

/* (a) MORE CAST/CONTACT SHADOW: the OCCLUSION CORE, from the cast slit's own contactShadow state. It is tight, dark
   and nearly crisp AT the board and gone in flight: its NEARNESS is read off the shadow's blur (STOP.SHADOW_NEAR 0.8
   px at rest, SHADOW_FAR 16 px at height), so the ball's mass arrives with it and leaves with it. Returns null when
   there is no shadow at all - a melt without weight never has one. */
export const meltOcclusion = (shadow, r, o = {}) => {
  const P = Object.assign({}, MELT, o);
  if (!shadow || !(r > 0)) return null;
  const near = mc01(1 - (shadow.blur - STOP.SHADOW_NEAR.blur) / Math.max(1e-6, STOP.SHADOW_FAR.blur - STOP.SHADOW_NEAR.blur));
  const rx = r * P.W_OCCL_W * (0.45 + 0.55 * near) * Math.max(0.2, shadow.scale);
  return { rx, ry: rx / P.W_OCCL_FLAT, alpha: P.W_OCCL_A * shadow.alpha * near, blur: P.W_OCCL_BLUR * rx };
};

/* a SPLAT's wet ink: the stroke at its core, the ball's ink, and a dark wet rim at its edge (per splat, its own box) */
export const meltSplatGradientMarkup = (id, hexes, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return '<radialGradient id="' + id + '" cx="0.5" cy="0.5" r="0.5">'
    + '<stop offset="0" stop-color="' + meltInkOf(hexes, P.LIGHT) + '"/>'
    + '<stop offset="0.55" stop-color="' + meltInkOf(hexes, P.INK_DEEP) + '"/>'
    + '<stop offset="0.85" stop-color="' + meltInkOf(hexes, P.CORE) + '"/>'
    + '<stop offset="1" stop-color="' + meltInkOf(hexes, P.CORE) + '"/></radialGradient>';
};
/* THE WORDS' RUN: ONE continuous streak under each glyph - its own ink blurred VERTICALLY only (stdDeviation "0 s", so a
   letter's columns stay apart and never swell sideways into its box), pushed down by the run and a little denser, with the
   crisp glyph drawn over it so its top edge stays legible. Merged offset copies read as six stacked echoes of each word
   (the parent's read of 015, 2026-09-13); a one-axis blur has no copies to count. */
export const meltTextFilterMarkup = (id, o = {}) => {
  const P = Object.assign({}, MELT, o);
  return '<filter id="' + id + '" x="-5%" y="-10%" width="110%" height="160%" color-interpolation-filters="sRGB">'
    + '<feGaussianBlur in="SourceGraphic" stdDeviation="0 0" result="' + id + 'b"/>'
    + '<feOffset in="' + id + 'b" dx="0" dy="0" result="' + id + 'd"/>'
    + '<feComponentTransfer in="' + id + 'd" result="' + id + 't"><feFuncA type="linear" slope="' + P.TEXT_STREAK + '" intercept="0"/></feComponentTransfer>'
    + '<feMerge><feMergeNode in="' + id + 't"/><feMergeNode in="SourceGraphic"/></feMerge></filter>';
};
/* THE TWO NUMBERS that filter is DRIVEN by, exactly as paintMelt has always written them: the vertical blur (half the
   run - "0 s", so a letter's columns stay apart) and how far the streak hangs below the glyph (0.6 of it). Exported for
   a caller that melts ONE text rather than a page of them - species/compare.mjs's `melt` form - so the streak is read
   off this module and never copied into another. paintMelt writes what it wrote before, to the character. */
export const meltTextStreak = (run) => ({ blur: "0 " + (Math.max(0, run) * 0.5).toFixed(2), dy: (Math.max(0, run) * 0.6).toFixed(1) });
/* THE WORDS' OWN INK over the sag: they run down as their own glyphs and are gone by the ball. meltState's
   `textOpacity` IS this, and calls it. */
export const meltTextAlpha = (k) => 1 - mEase(k);
/* the SVG transform of the ball: the flight's offset and tumble, and stopaction's area-preserving squash, about its centre */
export const meltBodyTransform = (st) => {
  if (!st.centre) return "";
  const cx = st.centre[0], cy = st.centre[1], xf = st.xf || { x: 0, y: 0, rot: 0 }, a = Math.abs(st.squash.a || 0);
  const th = (st.squash.a || 0) < 0 ? (st.squash.theta || 0) + Math.PI / 2 : (st.squash.theta || 0);
  const m = a > 1e-6 ? squashMatrix(th, a) : [1, 0, 0, 1];
  return "translate(" + (cx + (xf.x || 0)).toFixed(2) + " " + (cy + (xf.y || 0)).toFixed(2) + ") rotate(" + (xf.rot || 0).toFixed(2) + ") "
    + "matrix(" + m.map((v) => v.toFixed(4)).join(" ") + " 0 0) translate(" + (-cx).toFixed(2) + " " + (-cy).toFixed(2) + ")";
};

/* ---- the painter ------------------------------------------------------------------------------------------------ */
const MELT_BOARD_CLASSES = ["lp-grain", "lp-edge", "lp-field", "lp-fieldplate"];
export const meltIsBoard = (node) => !!(node && node.classList) && MELT_BOARD_CLASSES.some((c) => node.classList.contains(c));
/* the two halves of one page, by class: the INK clone hides the board, the BOARD world hides the ink */
export const MELT_CSS = ".world.meltink{background:transparent!important;pointer-events:none}"
  + ".meltink .lp-page{background:transparent!important}"
  + MELT_BOARD_CLASSES.map((c) => ".meltink ." + c).join(",") + "{visibility:hidden!important}"
  + ".meltboard .lp-page>" + MELT_BOARD_CLASSES.map((c) => ":not(." + c + ")").join("") + "{visibility:hidden!important}"
  /* the WORDS are not marks: the marks clone never draws them, and the text clone draws nothing else */
  + ".meltink .lp-ink,.meltink .lp-rail,.meltink .lp-chart line,.meltink .lp-chart text{visibility:hidden!important}"
  + ".world.melttext{background:transparent!important;pointer-events:none}"
  + ".melttext .lp-page{background:transparent!important}"
  + ".melttext .lp-page *{visibility:hidden!important}"
  + ".melttext .lp-ink,.melttext .lp-ink *,.melttext .lp-rail,.melttext .lp-rail *,.melttext .lp-chart line,.melttext .lp-chart text,.melttext .lp-chart text *{visibility:visible!important}";

/* the stage's box in the world's own px: `.world` overhangs the stage by 5% on every side */
export const meltStageBox = (wA) => ({ x: wA.offsetWidth / 22, y: wA.offsetHeight / 22,
                                       w: wA.offsetWidth * 10 / 11, h: wA.offsetHeight * 10 / 11 });
/* THE INK BOX in the world's own px: the union of the page's non-board children as laid out, clamped to the charcoal
   field (the ink lives on the board). Read through client rects so the punch's transform is in it, and mapped back into
   the world's px by the world's own scale. null when the world holds no page. */
export const meltInkRect = (wA) => {
  const page = wA.querySelector(".lp-page");
  if (!page) return null;
  const wr = wA.getBoundingClientRect(), kx = wA.offsetWidth / Math.max(1e-6, wr.width), ky = wA.offsetHeight / Math.max(1e-6, wr.height);
  const field = page.querySelector(".lp-field"), fr = field && field.getBoundingClientRect(), pr = page.getBoundingClientRect();
  const clip = fr && fr.width > 1 && fr.height > 1 ? fr : pr;
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const c of page.children) {
    if (meltIsBoard(c)) continue;
    const r = c.getBoundingClientRect();
    if (!(r.width >= 1 && r.height >= 1)) continue;
    x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom);
  }
  if (!(x1 > x0 && y1 > y0)) { x0 = clip.left; y0 = clip.top; x1 = clip.right; y1 = clip.bottom; }
  x0 = Math.max(x0, clip.left); y0 = Math.max(y0, clip.top); x1 = Math.min(x1, clip.right); y1 = Math.min(y1, clip.bottom);
  return { x: (x0 - wr.left) * kx, y: (y0 - wr.top) * ky, w: Math.max(1, (x1 - x0) * kx), h: Math.max(1, (y1 - y0) * ky) };
};
/* the marks' colours, as #rrggbb: every series stroke on the page's charts, as the browser computed it */
const meltHex = (css) => {
  const m = /rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)/.exec(String(css || ""));
  return m ? "#" + [m[1], m[2], m[3]].map((v) => (+v).toString(16).padStart(2, "0")).join("") : (/^#[0-9a-fA-F]{6}$/.test(css) ? css : null);
};
export const meltInkColours = (wA) => {
  const out = [];
  wA.querySelectorAll(".lp-chart .ser, .lp-chart rect[fill]").forEach((n) => {
    const cs = getComputedStyle(n), hx = meltHex(n.classList.contains("ser") ? cs.stroke : cs.fill);
    if (hx && out.indexOf(hx) < 0) out.push(hx);
  });
  return out;
};

/* P61 T6 / E99 s2 - THE PARTICLES A GATHER MOVES: every colour on the outgoing page, measured ONCE (nothing here
   reads time; the homes are the page as it stands at the boundary). TWO SPACES, exactly as the page vortex has
   (species/spiral.mjs `lpParticles`): the WORLD's own px for the page's own children, and each chart SVG's viewBox
   units for the chart's - a chart child's `transform` is written in ITS units, so the point and the reach are mapped
   into them by that chart's own meet scale. `root` is one of the melt's two clones; BOTH are walked, so the marks
   travel and the words travel with them. */
const meltGatherParts = (root, wA, c, Rmax) => {
  const page = root && root.querySelector(".lp-page");
  if (!page) return [];
  const wr = wA.getBoundingClientRect();
  if (!(wr.width > 1 && wr.height > 1)) return [];
  const kx = wA.offsetWidth / wr.width, ky = wA.offsetHeight / wr.height, out = [];
  for (const el of page.children) {
    if (meltIsBoard(el)) continue;
    if (el.classList && el.classList.contains("lp-chart")) continue;   /* a chart's CHILDREN are the particles, not the chart */
    const r = el.getBoundingClientRect();
    if (!(r.width >= 1 && r.height >= 1)) continue;
    out.push({ el, x: (r.left + r.width / 2 - wr.left) * kx, y: (r.top + r.height / 2 - wr.top) * ky, c, R: Rmax, svg: false });
  }
  for (const chart of page.querySelectorAll("svg.lp-chart")) {
    const vb = chart.viewBox && chart.viewBox.baseVal, cr = chart.getBoundingClientRect();
    if (!vb || !(vb.width > 0 && vb.height > 0) || !(cr.width > 1 && cr.height > 1)) continue;
    const cw = cr.width * kx, ch = cr.height * ky;                     /* the chart's box in the WORLD's own px */
    const x0 = (cr.left - wr.left) * kx, y0 = (cr.top - wr.top) * ky;
    const k = Math.min(cw / vb.width, ch / vb.height) || 1;            /* xMidYMid meet: world px per user unit */
    const cc = [(c[0] - x0 - (cw - vb.width * k) / 2) / k, (c[1] - y0 - (ch - vb.height * k) / 2) / k];
    for (const el of chart.children) {
      if (el.tagName === "defs") continue;
      let b = null;
      try { b = el.getBBox(); } catch (x) { b = null; }
      if (!b || !(b.width > 0 || b.height > 0)) continue;
      /* a PATH curls: it is sampled ONCE along its own length and redrawn point by point through the map every frame
         (s9.31's noodle). Everything else - a bar, a tick, a label - travels as one particle, as the retract's do. */
      const pts = el.tagName === "path" ? meltPathPoints(el, MELT.G_LINE_N) : null;
      if (pts && pts.length > 1) out.push({ el, pts, closed: /[zZ]\s*$/.test(el.getAttribute("d") || ""), c: cc, R: Rmax / k, svg: true, line: true });
      else out.push({ el, x: b.x + b.width / 2, y: b.y + b.height / 2, c: cc, R: Rmax / k, svg: true });
    }
  }
  return out;
};
/* A PATH's own points, in its chart's user units: n samples along its length, taken ONCE (getPointAtLength is the
   browser's; the samples are the homes, and the map is what runs every frame). Null when the element cannot be walked. */
const meltPathPoints = (el, n) => {
  let len = 0;
  try { len = el.getTotalLength(); } catch (x) { return null; }
  if (!(len > 1) || typeof el.getPointAtLength !== "function") return null;
  const m = Math.max(8, n | 0), pts = [];
  for (let i = 0; i <= m; i++) {
    const q = el.getPointAtLength(len * i / m);
    pts.push([q.x, q.y]);
  }
  return pts;
};
/* ONE frame of the travel: every particle to its pose at u. Pure per particle, so a seek writes what a play wrote. */
const meltGatherWrite = (parts, u, o) => {
  for (const p of parts || []) {
    if (p.line) {   /* the noodle: every sampled point through the same map, redrawn - it curls, it does not swing */
      let d = "";
      for (let i = 0; i < p.pts.length; i++) {
        const q = meltGatherAt(p.pts[i][0], p.pts[i][1], p.c, p.R, u, o);
        d += (i ? "L" : "M") + q.x.toFixed(1) + " " + q.y.toFixed(1) + " ";
      }
      p.el.setAttribute("d", d + (p.closed ? "Z" : ""));
      continue;
    }
    const v = meltGatherAt(p.x, p.y, p.c, p.R, u, o);
    if (p.svg) p.el.setAttribute("transform", meltGatherSvg(v, p.x, p.y));
    else p.el.style.transform = meltGatherCss(v, p.x, p.y);
  }
};

/* the overlay, mounted ONCE and kept on wA.__melt: the ink clone (a sibling right after the board, so it rides above
   it), and an svg sibling holding the filters, the masks, the stains' rims, the droplets and the ball. Nothing here reads
   time; the ink box and the colours are read once, from the page as it stands at the boundary. */
const meltMount = (wA, el, id, o = {}) => {   /* P61 T5b: `o` is the exit's own opts - the BODY COLOUR is read here, once, where the ball's one gradient is built */
  const doc = wA.ownerDocument;
  if (!doc.getElementById("meltcss")) { const s = doc.createElement("style"); s.id = "meltcss"; s.textContent = MELT_CSS; doc.head.appendChild(s); }
  const rect = meltInkRect(wA), hexes = meltInkColours(wA);
  const ink = wA.cloneNode(true);
  ink.removeAttribute("id"); ink.classList.add("meltink");
  ink.querySelectorAll("video").forEach((v) => v.remove());
  wA.parentNode.insertBefore(ink, wA.nextSibling);
  const txt = wA.cloneNode(true);
  txt.removeAttribute("id"); txt.classList.add("melttext");
  txt.querySelectorAll("video").forEach((v) => v.remove());
  wA.parentNode.insertBefore(txt, ink.nextSibling);
  wA.classList.add("meltboard");
  const svg = el("svg", "meltov", wA.parentNode, { "pointer-events": "none" });
  const defs = el("defs", "", svg, {});
  defs.innerHTML = meltFilterMarkup(id + "f", 0) + meltMaskMarkup(id + "m", id + "f") + meltInkFilterMarkup(id + "i")
    + meltStainFilterMarkup(id + "s") + meltRevealMarkup(id + "r", id + "s") + meltSplatFilterMarkup(id + "p") + meltBodyGradientMarkup(id + "g", hexes, o)
    + meltSplatGradientMarkup(id + "w", hexes) + meltTextFilterMarkup(id + "x");
  const ink0 = meltInkOf(hexes, MELT.INK_DEEP);
  defs.querySelector("#" + id + "i feFlood").setAttribute("flood-color", ink0);
  const comps = defs.querySelectorAll("#" + id + "i feComposite");
  const m = { id, svg, defs, ink, txt, rect, hexes, ink0, tintC: comps[comps.length - 1], toff: defs.querySelector("#" + id + "x feOffset"), tblur: defs.querySelector("#" + id + "x feGaussianBlur"),
              blur: defs.querySelector("#" + id + "f feGaussianBlur"), path: defs.querySelector("mask path"),
              iblur: defs.querySelector("#" + id + "i feGaussianBlur"), ioffs: [...defs.querySelectorAll("#" + id + "i feOffset")],
              stainG: defs.querySelector("#" + id + "r g"),
              drops: el("g", "meltdrops", svg, { filter: "url(#" + id + "p)" }),
              bodyG: el("g", "meltbody", svg, {}), splats: [], sats: [], holes: [], sprung: null, parts: null,
              band: null, rim: null, pit: null, occl: null };   /* P61 T5: the three MATERIAL overlays and the
                 occlusion core - mounted only when a `melt:weight` asks; null here is the melt that shipped */
  m.body = el("path", "", m.bodyG, { fill: "url(#" + id + "g)", d: "" });
  svg.style.position = "absolute"; svg.style.overflow = "visible"; svg.style.pointerEvents = "none"; svg.style.zIndex = "4";
  wA.__melt = m;
  return m;
};
/* keep n circles (or paths) in a group, created once and moved after that */
const meltDots = (pool, n, el, parent, attrs, tag = "circle") => { while (pool.length < n) pool.push(el(tag, "", parent, attrs)); return pool; };
const meltCircle = (dot, c) => {
  if (!c || c.r <= 0.2) { dot.setAttribute("r", "0"); return; }
  dot.setAttribute("cx", c.x.toFixed(1)); dot.setAttribute("cy", c.y.toFixed(1)); dot.setAttribute("r", c.r.toFixed(1));
};

/* PAINT ONE FRAME. ctx: { wA, wB, t, t0, opts, rnd, el, id }. The state is meltState's; this only writes it down. A world
   that holds no page is not melted (E88: the melt takes a chart's ink - there is no whole-world melt left to fall back
   to); the engine cuts instead, and so does this. */
export const paintMelt = (ctx) => {
  const { wA, wB, el, rnd } = ctx, id = ctx.id || "melt";
  /* P58 T6 (b) / E98 s4 - THE PLANE THE BALL MELTS AT. The melt's three elements (the ink clone, the words' clone and
     the overlay that carries the ball, its drips, its shadow and its ending) have always taken the OUTGOING world's
     own transform; a melt that authored `depth=<k>` takes the same string with the camera read at k instead
     (`camLayerCss`, the engine's `meltDepthCss` - the one place that knows the camera, exactly as the dock's own
     depth does). `ctx.worldCss` is undefined for every melt that named no depth, so the string is the one it always
     was and every melt golden is byte-identical. */
  const wCss = typeof ctx.worldCss === "string" ? ctx.worldCss : wA.style.transform;
  if (!wA.__melt && !wA.querySelector(".lp-page")) return null;
  if (wA.__melt && !(wA.__melt.svg && wA.__melt.svg.isConnected)) clearMelt(wA);   /* a stale mount: its clone and classes go first */
  const m = wA.__melt ? wA.__melt : meltMount(wA, el, id, ctx.opts);   /* P61 T5b: the exit's own opts, so the ball's gradient is built in its authored BODY colour */
  /* P61 T3: `ctx.hand` is the ARRIVING page's morph outline this frame, already in this world's px - the caller owns
     that carry because it is the one that knows both boxes. Undefined for every other melt, so `P.hand` is undefined
     and every string this painter writes is the string it wrote before. */
  const st = meltState(ctx.t0, ctx.t, Object.assign({ rect: m.rect, stagebox: meltStageBox(wA), hand: ctx.hand }, ctx.opts), rnd);
  m.svg.style.left = wA.offsetLeft + "px"; m.svg.style.top = wA.offsetTop + "px";
  m.svg.style.width = wA.offsetWidth + "px"; m.svg.style.height = wA.offsetHeight + "px";
  m.svg.setAttribute("viewBox", "0 0 " + wA.offsetWidth + " " + wA.offsetHeight);
  m.svg.style.opacity = st.gone ? "0" : "1";
  /* the BALL's own overlay rides the plane too (its box is wA's, so the same string about the same centre): the drops
     fall on it and the ending runs from it. Written ONLY at a depth - an overlay that carried no transform keeps none. */
  if (typeof ctx.worldCss === "string") { m.svg.style.transformOrigin = "50% 50%"; m.svg.style.transform = wCss; }
  else if (m.svg.style.transform) { m.svg.style.transform = ""; m.svg.style.transformOrigin = ""; }
  /* THE INK: masked, run, squeezed about the ball's centre - hidden once the ball is solid. P61 T6 / E99 s2: under a
     GATHER it is none of those. The marks and the words TRAVEL, one particle at a time, to the ball's own centre;
     there is no mask (a mask would clip a mark where it no longer is), no run and no squeeze, and the stdDeviation
     written on both filters is 0 on every frame of the window - "i don't want the melt to be blur or a wipe". */
  const ink = m.ink, gth = st.gather, showInk = !st.gone && st.inkOpacity > 0 && (st.path || !!gth);
  ink.style.visibility = showInk ? "" : "hidden";
  ink.style.zIndex = "3";
  if (showInk) {
    m.blur.setAttribute("stdDeviation", st.blur.toFixed(2));
    if (gth) {
      if (ink.style.mask) { ink.style.mask = ""; ink.style.webkitMaskImage = ""; }
      if (!m.parts) m.parts = meltGatherParts(ink, wA, gth.c, gth.R).concat(meltGatherParts(m.txt, wA, gth.c, gth.R));
      meltGatherWrite(m.parts, gth.k, ctx.opts);
    } else {
      m.path.setAttribute("d", st.path);
      ink.style.mask = "url(#" + id + "m)"; ink.style.webkitMaskImage = "url(#" + id + "m)";
    }
    m.iblur.setAttribute("stdDeviation", st.inkBlur.toFixed(2));   /* on for every frame the ink shows: its faint-pixel cut is part of the ink */
    m.ioffs.forEach((o, j) => o.setAttribute("dy", (st.run * (j + 1) / m.ioffs.length).toFixed(1)));
    ink.style.filter = "url(#" + id + "i)";
    m.tintC.setAttribute("k2", st.tint.toFixed(4)); m.tintC.setAttribute("k3", (1 - st.tint).toFixed(4));
    ink.style.transformOrigin = (st.centre && !gth) ? st.centre[0].toFixed(1) + "px " + st.centre[1].toFixed(1) + "px" : "";
    ink.style.transform = (st.scale !== 1 && !gth ? "scale(" + st.scale.toFixed(4) + ") " : "") + wCss;
  }
  /* THE WORDS: their own glyphs running down, fading out over the sag */
  const txt = m.txt, showTxt = !st.gone && st.textOpacity > 0.002;
  txt.style.display = showTxt ? "" : "none";   /* never `visibility`: the words' own !important visible would outrank it */
  txt.style.zIndex = "3";
  if (showTxt) {
    const streak = meltTextStreak(st.run);
    m.tblur.setAttribute("stdDeviation", streak.blur);
    m.toff.setAttribute("dy", streak.dy);
    txt.style.filter = "url(#" + id + "x)";
    txt.style.opacity = st.textOpacity.toFixed(4);
    txt.style.transform = wCss;
  }
  ink.style.opacity = showInk ? st.inkOpacity.toFixed(4) : "0";
  /* THE BALL */
  m.body.setAttribute("d", st.body || "");
  m.body.setAttribute("opacity", (st.body ? st.bodyAlpha : 0).toFixed(3));
  m.bodyG.setAttribute("transform", meltBodyTransform(st));
  /* P61 T5 / E99 s3 + P61 T5b / E99 s42 - THE BALL'S SHADOWS. What is left after the operator's read: the POINT OF
     DEEP SHADOW DEPTH, under the roll's mark and the specular spot. It wears the BODY'S OWN `d`, so it is clipped to
     the living drop's silhouette exactly at every t - no clipPath, no second geometry to keep in step - and its
     gradient reaches 0.48 of the body's box against a silhouette at 0.5, so it carries NO alpha at the edge.
     THE BAND AND THE RIM ARE OFF (MELT.W_RIM_ON / W_BAND_ON, both false - E99 s42). That is not a cosmetic choice:
     every one of these paths is antialiased on its own and then composited, so a boundary pixel of coverage `a` ends
     at 1 - (1 - a)^k for k paths. Measured on the settle frame, one pixel went from 0.567 covered to 0.988 with four
     paths, which is the "pixelated on the edges" the operator read; with the pit alone the edge is the body's own.
     Mounted (defs and paths together) the first frame `st.mass` is true, which only a `melt:weight` ever makes it:
     a melt without weight writes no gradient into its defs and no path into its body group, so its markup is the
     markup that shipped. `docs_find "Fresnel"` returns only clothoid.mjs's INTEGRAL - nothing here is named for it. */
  if (st.mass && !m.pit) {
    const W = Object.assign({}, MELT, ctx.opts);
    /* the order IS the physics: the BAND is a reflection, the PIT is a shadow and occludes it, and the RIM is the
       silhouette, which is under nothing. Each is written only if its own gate is on. */
    if (W.W_BAND_ON) {
      m.defs.insertAdjacentHTML("beforeend", meltBandGradientMarkup(id + "gb", m.hexes, W));
      m.band = el("path", "", m.bodyG, { fill: "url(#" + id + "gb)", d: "" });
    }
    m.defs.insertAdjacentHTML("beforeend", meltPitGradientMarkup(id + "gp", m.hexes, W));
    m.pit = el("path", "", m.bodyG, { fill: "url(#" + id + "gp)", d: "" });
    if (W.W_RIM_ON) {
      m.defs.insertAdjacentHTML("beforeend", meltRimGradientMarkup(id + "gr", m.hexes, W));
      m.rim = el("path", "", m.bodyG, { fill: "url(#" + id + "gr)", d: "" });
    }
  }
  if (m.pit) {
    const d = st.mass ? (st.body || "") : "", a = (d ? st.bodyAlpha : 0).toFixed(3);
    for (const p of [m.band, m.pit, m.rim]) { if (p) { p.setAttribute("d", d); p.setAttribute("opacity", a); } }
  }
  /* THE WEIGHT PHASE's three things (R26-118), each mounted the first frame it is asked for: a melt that never asked
     for weight never creates one, so its DOM is the DOM it always had - which is why the goldens are byte-identical. */
  if (st.shadow || m.shadow) {
    if (!m.shadow) { m.shadow = el("ellipse", "meltshadow", m.svg, { fill: "#000" }); m.svg.insertBefore(m.shadow, m.drops); }
    const sh = st.shadow, rx = sh ? st.r * MELT.W_SHADOW_W * sh.scale : 0;
    m.shadow.setAttribute("cx", sh ? (st.centre[0] + st.shadowX).toFixed(2) : "0");
    m.shadow.setAttribute("cy", sh ? (st.centre[1] + st.r).toFixed(2) : "0");
    m.shadow.setAttribute("rx", rx.toFixed(2)); m.shadow.setAttribute("ry", (rx / 6).toFixed(2));
    m.shadow.setAttribute("opacity", sh ? (sh.alpha * MELT.W_SHADOW_A).toFixed(3) : "0");
    m.shadow.style.filter = sh ? "blur(" + sh.blur.toFixed(2) + "px)" : "";
  }
  /* P61 T5 / E99 s3 (a): THE OCCLUSION CORE, over the cast slit - the patch of board the ball actually covers.
     Tight, dark and near-crisp at the contact, gone in flight (`meltOcclusion` reads its nearness off the cast
     shadow's own blur). Mounted the same way, so a melt without weight never has one. */
  if (st.occl || m.occl) {
    if (!m.occl) { m.occl = el("ellipse", "meltoccl", m.svg, { fill: "#000" }); m.svg.insertBefore(m.occl, m.drops); }
    const oc = st.occl;
    m.occl.setAttribute("cx", oc ? (st.centre[0] + st.shadowX).toFixed(2) : "0");
    m.occl.setAttribute("cy", oc ? (st.centre[1] + st.r).toFixed(2) : "0");
    m.occl.setAttribute("rx", oc ? oc.rx.toFixed(2) : "0"); m.occl.setAttribute("ry", oc ? oc.ry.toFixed(2) : "0");
    m.occl.setAttribute("opacity", oc ? oc.alpha.toFixed(3) : "0");
    m.occl.style.filter = oc ? "blur(" + oc.blur.toFixed(2) + "px)" : "";
  }
  if (st.mark || m.mark) {
    if (!m.mark) m.mark = el("ellipse", "meltmark", m.bodyG, { fill: meltBodyInk(m.hexes, MELT.CORE, ctx.opts) });   /* P61 T5b: the mark is the ball's own ink, so it follows its body colour */
    const k = st.mark;
    m.mark.setAttribute("cx", k ? k.x.toFixed(2) : "0"); m.mark.setAttribute("cy", k ? k.y.toFixed(2) : "0");
    m.mark.setAttribute("rx", k ? k.rx.toFixed(2) : "0"); m.mark.setAttribute("ry", k ? k.ry.toFixed(2) : "0");
    m.mark.setAttribute("transform", k ? "rotate(" + k.deg.toFixed(2) + " " + k.x.toFixed(2) + " " + k.y.toFixed(2) + ")" : "");
    m.mark.setAttribute("opacity", k ? (st.bodyAlpha * 0.9).toFixed(3) : "0");
  }
  if (st.hl || m.hl) {
    if (!m.hl) m.hl = el("ellipse", "melthl", m.bodyG, { fill: meltSheen(meltBodyInk(m.hexes, MELT.LIGHT, ctx.opts), MELT.HL_SHEEN) });   /* P61 T5b: and so does the one specular spot */
    const h = st.hl;
    m.hl.setAttribute("cx", h ? h.x.toFixed(2) : "0"); m.hl.setAttribute("cy", h ? h.y.toFixed(2) : "0");
    m.hl.setAttribute("rx", h ? h.r.toFixed(2) : "0"); m.hl.setAttribute("ry", h ? (h.r * 0.72).toFixed(2) : "0");
    m.hl.setAttribute("opacity", h ? (st.bodyAlpha * 0.85).toFixed(3) : "0");
  }
  /* THE SPLATTER: opaque ink splats with their tails and satellites, and the torn stains cut through the board */
  meltDots(m.splats, st.drops.length, el, m.drops, { fill: "url(#" + id + "w)" }, "path").forEach((p, i) => {
    const d = st.drops[i], k = st.dropScale;
    p.setAttribute("d", d && d.d > 0 ? meltSplatPath(d.x, d.y, d.r * k, d.a + Math.PI, d.tail * k, rnd, 500 + i) : "");
  });
  meltDots(m.sats, st.sats.length, el, m.drops, { fill: "url(#" + id + "w)" }).forEach((dot, i) => {
    const s = st.sats[i];
    meltCircle(dot, s ? { x: s.x, y: s.y, r: s.r * st.dropScale } : null);
  });
  m.sats.slice(st.sats.length).forEach((dot) => dot.setAttribute("r", "0"));
  meltDots(m.holes, st.stains.length, el, m.stainG, { fill: "#000" }, "path").forEach((p, i) => {
    const s = st.stains[i];
    p.setAttribute("d", s && s.r > 0.2 ? meltSplatPath(s.x, s.y, s.r, 0, 0, rnd, 700 + i) : "");
  });
  m.drops.setAttribute("opacity", st.dropAlpha.toFixed(3));
  /* THE BOARD: the outgoing world, its ink hidden - up, then painted through, then gone */
  wA.style.zIndex = 3;
  wA.style.opacity = st.boardUp ? st.cover.toFixed(4) : "0";
  /* the board's three-frame ANSWER to the hit (stopaction groundShake), on the CSS `translate` property - never on
     `transform`, which the clones copy off this world every frame */
  if (st.shake.x || st.shake.y || wA.style.translate) {
    wA.style.translate = (st.shake.x || st.shake.y) ? st.shake.x.toFixed(2) + "px " + st.shake.y.toFixed(2) + "px" : "";
  }
  const rev = st.reveal ? "url(#" + id + "r)" : "";
  wA.style.mask = rev; wA.style.webkitMaskImage = rev;
  /* THE PLATE springs up as it is painted */
  if (wB && st.spring !== 1) {
    wB.style.transformOrigin = "50% 50%";
    wB.style.transform = "scale(" + st.spring.toFixed(4) + ") " + wB.style.transform;
    m.sprung = wB;
  }
  return st;
};

/* the reset, called on every frame that is NOT a melt - it touches only what the painter set */
export const clearMelt = (wA) => {
  if (!wA.__melt) return;
  const m = wA.__melt;
  if (m.svg && m.svg.parentNode) m.svg.parentNode.removeChild(m.svg);
  if (m.ink && m.ink.parentNode) m.ink.parentNode.removeChild(m.ink);
  if (m.txt && m.txt.parentNode) m.txt.parentNode.removeChild(m.txt);
  if (m.sprung && m.sprung.style.transformOrigin) m.sprung.style.transformOrigin = "";
  wA.__melt = null;
  wA.classList.remove("meltboard");
  wA.style.mask = ""; wA.style.webkitMaskImage = "";
  if (wA.style.translate) wA.style.translate = "";   /* the weight phase's board shake */
  if (wA.style.zIndex) wA.style.zIndex = "";
  if (wA.style.opacity !== "") wA.style.opacity = "";
  if (wA.style.transformOrigin) wA.style.transformOrigin = "";
};

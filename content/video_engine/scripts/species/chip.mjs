/* species/chip.mjs - THE ICON CHIP (P50 T2; doc 29 s9.27's motion menu; the Bravos icon board, shots 26-28:
   predictions land as chips and are crossed out one by one). SOURCE OF TRUTH, inlined into the scene-evidence
   player by sync_kinetics.py between KINETICS:BEGIN chip and KINETICS:END, AFTER spring and idle - it imports
   both, and the import order IS the region order.
   THE MODULE RULE (the operator, 2026-09-11): a species is a module here, never a branch in the template's
   body. The last statement registers the painter in the template's SPECIES_PAINTERS registry; node, where no
   such registry exists, still imports the file for the pure math below.

   WHEN: the sentence names a THING as one of a SET (a prediction, an actor, a plant) - a chip lands on its
   word; a RETRACTS sentence ("none of this happened") crosses it out on a later word.

   THE LAW, all of it a pure function of t:
     land   - the badge spring (kinetics/spring.mjs springPop, the POP preset, Mp = 4 %) over LAND_S, from
              POP_FROM and DROP_PX above its place: R26-20's two-spring landing rides this one clock - the
              scale overshoots by Mp and settles, the drop rides the same x so the card never lands twice.
     hold   - opt-in `idle` (E49, one of IDLE_KINDS), applied exactly as the spotlight applies it: the idle's
              scale multiplies the landed scale, its offset moves the card, phased off the seed so two chips
              never breathe in step. Absent = declared stillness.
     cross  - `cross_at` draws a two-stroke X over the card by the template's drawOn (kinetics/stroke.mjs's
              curvature law when the flag is on, the species ease otherwise): the first stroke over the first
              half of CROSS_S, the second over the second, and the card dims to DIM as the X completes.
              `state: "crossed"` with no `cross_at` means the chip LANDS already crossed (the board is read
              back after the fact).
     P71 T12 (was P69 T42; Bravos A36 / F3 / A14 / A59), THE STATES - each lands on its word, each a pure function of t:
     lit    - `state: "lit"`: a HALO behind the card in the focus yellow (the ONE actor of a set the sentence is about,
              BUB #20). It comes up with the landing's fade and HOLDS - an annotation, 0 events (E99 s91). `pulse: true`
              BLINKS it PULSE_N times from the settle - motion, one event per blink onset (E99 s99).
     tick   - `tick_at` is the cross's sibling, drawn as Bravos draws it (HIS 06:13): a small DISC BADGE in the positive
              ink centred ON the card's top edge, springing in on tick_at (chipLand's clock), its charcoal check drawn in
              two strokes over CROSS_S (split by their length, one gesture). The card keeps its ink - a thing that held is
              not dimmed - and the icon is never covered. A chip is ticked or crossed, never both (the compiler refuses
              the pair), and a badge and a tab never share the top edge (refused too).
     tab    - `tab: "sell" | "buy"` is a state PILL centred ON the card's top edge, half above it and half on it (JPN 04:08
              / 05:34 - Bravos centres it on the tile): it lands on `tab_at` (else with the chip) on the badge spring,
              SELL in the negative ink and BUY in the positive (E28's sign inks), its word at the s90 floor and the pill
              hugging it. A tab names a MOVE, never a trade record: no number.
     None of the three is a stamped chip's: a seal carries its verdict in its ring text (E99 s121), and the compiler
     refuses a state on the stamp form by name. Absent, the chip paints exactly what it painted.
     P71 T18 (was P69 T53; Bravos A61), THE "?" - the open question as a TEXT mark in the page face (no icon: A2a):
     ?      - `glyph: "?"` on a chip: a "?" centred ABOVE the card in the glyph's chalk (HIS 01:48, the "?" over the ROI
              node), popping on `glyph_at` (else with the chip) and held - an annotation of the thing, which it rides.
              A chip carries one mark on its top edge (a "?", a check or a tab) and is asked or failed, never both.
     unknown - the `unknown` species (paintUnknown below): a LARGE "?" at a point or a region, in the neg crimson (BOOM
              08:52.5) or the chalk, on BOOM's pop (the one T17 measured off BOOM's failed-link disc), held (s91) or
              pulsing (`pulse: true`, s99), leaving on its own fade inside its window. The veil it may rise over
              (`under: "blur"`, F12) is the engine's (paintUnknownVeil), on T15's blur law.
   Nothing is stored: every visual reads from t, sp.at and sp.cross_at, so a scrubbed frame is the played
   frame. The glyph is a SOURCED icon (assets/icons, A2a provenance) carried in the asset map as `icon:<name>`;
   this module never invents geometry. The dials below are ours to tune (42 s42.5), not findings. */
import { springPop } from "../kinetics/spring.mjs";
import { idleXf } from "../kinetics/idle.mjs";
import { squashMatrix } from "../kinetics/squash.mjs";
import { STAMP_ARRIVAL, STAMP_LAND, stampXf, stampExit } from "../kinetics/stopaction.mjs";

export const CHIP = Object.freeze({
  SIZE: 168,        /* the card's side in STAGE px - a chip is read at a glance beside its neighbours, not studied */
  RX: 22,           /* the rounded corner (the dock card's 14px radius, scaled to the smaller card) */
  GLYPH: 92,        /* the glyph's box inside the card: a little over half the side, so the card reads as a card */
  LABEL_DY: 46,     /* the label's baseline below the card's bottom edge */
  PHONE_LABEL_SIZE: 45,      /* opt-in landscape-phone text, shared visually with flow's phone treatment */
  PHONE_LABEL_DY: 52,        /* the first phone baseline below the card */
  PHONE_LABEL_LINE_H: 48,    /* explicit newline-separated baseline step */
  PHONE_MAX_LINES: 3,        /* a chip label is a bounded caption, never a paragraph */
  LAND_S: 0.55,     /* the landing's wall clock - the dock's DOCK_POP_S 0.45 plus a beat: a chip is lighter than a card and travels further */
  POP_FROM: 0.82,   /* the scale it springs from (the dock's DOCK_POP_FROM is 0.85) */
  DROP_PX: 34,      /* ... and how far above its place it falls from, on the same spring */
  FADE_S: 0.14,     /* the opacity ramp, the dock's DOCK_FADE_S 0.12 - never a pop out of nothing */
  CROSS_S: 0.5,     /* the X's two strokes together */
  DIM: 0.55,        /* what a crossed chip dims to - struck through, still legible (it is still one of the set) */
  /* P71 T12: THE STATES' DIALS - ours to tune (42 s42.5), not findings, except where a line names its source */
  LIT_INK: "#F5B72E",   /* the halo's ink: the focus yellow, the template's .sq / .chiplab sunflower (pinned by a test) - never the seal's gold */
  LIT_PAD: 12,          /* the halo's outset from the card's edge, stage px */
  LIT_W: 5,             /* its stroke: the .sq hand's width */
  LIT_GLOW: 18,         /* its glow: a drop-shadow in the same ink (lpBloom's form, as flow's token halo), px */
  LIT_GLOW_A: 0.85,     /* ... at this alpha */
  PULSE_N: 3,           /* `pulse: true`: the halo blinks this many times ... */
  PULSE_S: 0.5,         /* ... each blink this long (a dip and back), the first from the settle (at + LAND_S) */
  PULSE_LOW: 0.2,       /* ... down to this share of the halo at the blink's middle */
  CHECK_D: 0.224,       /* the check badge's diameter in card sides [MEASURED: Bravos HIS 06:13, three tiles - disc 37 / 36 / 37 px on
                           tiles 164 / 163 / 165 px (0.226 / 0.221 / 0.224), each disc's centre ON the tile's top edge (-1 / 0 / 0 px)
                           and on its centre line (0.5 / 0.5 / 0 px) - scratchpad/p71-t12/logs/measure-his-badge.json] */
  TICK: Object.freeze([[-0.46, 0.02], [-0.14, 0.34], [0.46, -0.30]]),   /* the check's three points in the BADGE's radii, about its centre: the short down stroke, then the long up one */
  TICK_W: 0.2,          /* the check's stroke, in the badge's radius (3.8 px on the 168 px card) */
  TICK_INK: "#3DDC84",  /* the badge's fill: the template's --lp-pos (a thing that HELD reads at a glance; the X keeps the sunflower) */
  CHECK_MARK: "#25313C", /* the check on the badge: charcoal, 7.43:1 on the positive ink (white is 1.78:1 there) */
  TAB_TYPE: 59.08,      /* the tab's word: the s90 phone floor [DERIVED: ledger_page.CARD_TYPE_PX, 12 * 1920 / 390] */
  TAB_H: 70,            /* the pill's height: Bravos's pill over its caps (JPN 04:08: 26 px over 16 px caps, 1.625) x our caps (0.727 em
                           of 59.08 = 42.95 px), rounded [MEASURED: scratchpad/p71-t12/logs/measure-jpn-pill.json] */
  TAB_PAD: 14,          /* the room each side of the word, trimmed from Bravos's 0.27 of the height so the pill hugs its word: BUY
                           153 px on the 168 px card, SELL 179 px (5.5 px over each side); at 12 the L's foot ran into the capsule's end */
  TAB_INK: Object.freeze({ sell: "#FF4D4D", buy: "#3DDC84" }),   /* E28's sign inks: the template's --lp-neg / --lp-pos (pinned by a test) */
  TAB_TEXT: "#25313C",  /* the word on the tab: charcoal, the ink with the higher WCAG contrast on BOTH fills (pinned by a test) */
  TAB_EM: Object.freeze({ SELL: 2.56, BUY: 2.12 }),   /* the word's advance in em at weight 700 [MEASURED: getComputedTextLength in the golden's own page, SELL 151.0 / BUY 124.75 px at 59.08 px - scratchpad/p71-t12/logs/measure-tab-word.json] - sizes the tab */
});

/* P71 T18: THE "?" - one mark, two places. Sized by its INK height (the glyph's cap-to-baseline, what a frame shows), so
   a dial means what it measures: the font size is h / INK_EM. Measured off Bravos with one tool (scratchpad p71-t18
   scripts/measure_q.py, logs/measure-q.json) - E38, the reference first. */
export const QMARK = Object.freeze({
  FACE: "Inter, Arial, sans-serif",   /* the page face - the chip label's own stack (.chiplab) */
  WEIGHT: 800,          /* Bravos's "?" is a heavy geometric sans (BOOM 08:52.5; HIS 01:48) */
  INK_EM: 0.728,        /* the "?"'s ink from the baseline to its top, in em, centred on the anchor to 0.000 em [MEASURED: the player's
                           resolved Inter at 800, rasterised at 1000 px - scratchpad p71-t18 scripts/measure_qmark_em.py] */
  /* the `unknown` species - BOOM 08:52.5 (jx3Ll-GJtMY, 1920 x 1080) */
  SIZE: 122,            /* the ink height, stage px [MEASURED: BOOM 08:52.5, the settled "?" 122 px of 1080 (bbox 1550-1629 x 346-467)] */
  SIZE_MIN: 59.08,      /* the smallest "?" is a label at the s90 floor [DERIVED: ledger_page.CARD_TYPE_PX] */
  SIZE_MAX: 400,        /* ... and the largest a third of the stage [DERIVED: CHN 0:35's biggest "?" is 0.26 of the height, 285 px] */
  INKS: Object.freeze({ neg: "#FF4D4D", chalk: "#F2F2F2" }),   /* the template's --lp-neg (BOOM's crimson, rgb(201,30,62), is the ink
                           T17 matched to it - FLOW.FAIL_INK) and --lp-chalk (HIS's white); pinned by a test */
  POP_FROM: 0.3,        /* its first-seen size [MEASURED: BOOM 08:52.5, 42 px on its settled 122 (0.34) - T17's FLOW.FAIL_POP_FROM, the same pop] */
  MP: 0.3,              /* its overshoot [MEASURED: the peak 146 px, 1.197 x the settled size = 0.3 + 0.7 x (1 + Mp)] */
  POP_S: 0.83,          /* its spring's clock: at Mp 0.3 springPop peaks at u 0.201, so the peak lands 0.167 s in, BOOM's (FLOW.FAIL_POP_S) */
  SETTLE_S: 0.4,        /* when it stands [MEASURED: BOOM, 122 px from +0.4 s after the dip to 118] - a pulse's first blink starts here */
  PULSE_AMP: 0.12,      /* `pulse: true`: each blink swells the "?" by this share, on a sine square, CHIP.PULSE_N times of CHIP.PULSE_S
                           [DERIVED: no Bravos "?" pulses on disk (BOOM's holds 2.8 s) - HG1 reads it] */
  GLOW_K: 0.08,         /* the halo in its own ink, as a share of its height [DERIVED: CHN 0:35 / BOOM 13:52's soft rim, the frame read] */
  GLOW_A: 0.55,         /* ... at this alpha */
  LEAVE_S: 0.25,        /* it fades out over the last LEAVE_S of its window [DERIVED: BOOM's "?" leaves with its page, a cut we do not own] */
  /* the chip's "?" - HIS 01:48 (Jw8ykhoOVBQ, 1280 x 720) */
  CHIP_H: 0.38,         /* its ink height in card sides [MEASURED: 62-64 px on the 164 px node card] */
  CHIP_GAP: 0.146,      /* its ink's foot above the card's top edge, in card sides [MEASURED: 24 px] - centred on the card to 0.5 px */
  CHIP_FROM: 0.2,       /* its first-seen size [MEASURED: 13 px on its settled 64] */
  CHIP_MP: 0.04,        /* its overshoot: the house POP [MEASURED: the peak 64 on the settled 62, ~3 %] */
  CHIP_POP_S: 0.72,     /* its clock [MEASURED: 97 % at +0.23 s after first seen; springPop(u, 0.04) reaches 0.97 at u 0.372] */
  KEYLINE: "rgba(27,30,35,.85)",   /* the chip's "?" wears the chip label's keyline (.chiplab), so the chalk reads on any ground */
  KEYLINE_W: 6,
});

/* OPT-IN STAMP FORM (P62): an approved woodblock raster prop freely placed on a
   plate or ledger page. It keeps the chip's spring landing and authored `dur`,
   but has no card, generic glyph, border or constant boil. */
export const CHIP_STAMP = Object.freeze({
  SIZE: 260,         /* default art box in stage px */
  MIN_SIZE: 180,
  ICON_MAX_SIZE: 420, /* the compiler keeps sourced icon stamps at the original bound */
  MAX_SIZE: 700,     /* approved finance-prop cutouts may carry a full narrative beat */
  LABEL_SIZE: 48,
  LABEL_GAP: 28,
  LABEL_LINE_H: 52,
  /* P70 T1 (E99 s90): the label's size under `arrive: "stamp"` - the phone floor, 59.08 stage px [DERIVED:
     ledger_page.CARD_TYPE_PX, 12 * 1920 / 390 to two places]; LABEL_GAP and LABEL_LINE_H scale with it. A stamp-form
     chip WITHOUT the arrival keeps LABEL_SIZE (its bytes do not move) and the compiler WARNs that it is under the floor. */
  LABEL_FLOOR: 59.08,
  MAX_LINES: 3,
  INK: Object.freeze({ cream: "#F4E6C7", charcoal: "#25313C" }),
  /* P70 T1c (E99 s127 (2)): the stamp arrival's impact ring is no longer inked from the ground (T1's RING_INK, chalk on
     the ledger / charcoal elsewhere, is gone): a stamped chip is always a seal, and a seal's shockwave is the seal's gold
     - `chipSeal(...).ink`, see chipStampGroup */
  MASS: "ink",       /* the mass the stamp lands at: the engine's own default for a stamp (`stampXf(d.mass || "ink", ...)`) */
  /* P70 T1b (the parent's round 3): A SEAL DOES NOT SQUASH. At mass "ink" the hit's ONE squash frame (STOP.IMPACT_SQUASH 0.22,
     contact + 0.021 .. + 0.063 s at 24 fps) turned the full-size seal into a vertical oval - a coin flipping, not a stamp; the
     source (badge-stamp.tsx) has no squash at all. The seal lands rigid: this is the IMPACT_SQUASH it hands stampXf, and
     nothing else moves - MASS stays "ink", so the page's dip, a violent shake, the impact ring and the ink easing back are the
     ink stamp's. ("metal" has squash_frames 0 too, but its dip is 1.5x deeper on a slower spring - not only the squash.)
     A bare prop (the dock's stamp) keeps its squash frame. */
  SQUASH: 0,
});

/* P70 T1b (E99 s121 (1); E99 s123): A SEAL-TYPE STAMP IS A SEAL, AND A SEAL IS GOLD. The operator, beside remotion-ui's
   badge stamp: "the stamp needs to have a solid border" - and "part of the reason that stamp works is the color, we need
   that sort of yellow/gold accent". A stamped chip (the stamp FORM landing by the stamp arrival) carries the source's
   seal: a solid thick OUTER ring and a thin INNER ring in the MARK's own group, so they land with it, rest with it and
   leave on its exit (the impact ring radiates from the outer one and is gone), and, optionally, RING TEXT on two
   half-arcs, both reading left to right. Its geometry is the source's in its own units (badge-stamp.tsx, r = 50) scaled
   to the seal's outer radius R: the rings, their strokes and alphas, and the ring text's size, tracking and radii. R is
   the room the mark reserves (`seal_r`, written by the compiler: the inner ring 12 px outside the authored mark and its
   name); the compiler then GROWS the art to fill it (THE MARK TAKES THE ROOM, CAPABILITIES :79), so ring text never
   widens the seal. THE INK is ONE dial, GOLD - the source's own default `color` - on the rings, the ring text and the
   name; on a light ground (the row says `ink: "charcoal"`) it is darkened until it reads, CONTRAST_MIN against the
   cream. The picture keeps its own colours. The sunflower (#F5B72E) stays the callout / focus yellow: a separate token.
   The unstamped stamp form (the chip's spring) carries no seal - one spring "reads as a sticker being placed" (the
   component's docs); a bare prop stays bare (s87, s121 (2)). */
export const CHIP_SEAL = Object.freeze({
  SRC_R: 50,          /* badge-stamp.tsx:127 `const r = 50` - the seal's outer radius in the source's own units */
  INNER_R: 44,        /* :184 the inner ring at r - 6 */
  OUTER_W: 3.4,       /* :178 the outer ring's stroke - SOLID and thick */
  INNER_W: 1.2,       /* :187 the inner ring's stroke - thin */
  INNER_A: 0.7,       /* :188 the inner ring's opacity, ink x 0.7 */
  TEXT_A: 0.9,        /* :198 / :214 the ring text's opacity, ink x 0.9 */
  TEXT_SIZE: 7.4,     /* :194 / :209 the ring text's size - 0.148 of R; under the s90 floor the compiler WARNs, never resizes */
  TEXT_TRACK: 1.6,    /* :196 / :211 letterSpacing */
  TOP_R: 38,          /* :142 the top arc at r - 12, its baseline ON the arc, glyphs standing out */
  BOTTOM_R: 36,       /* :147 the bottom arc at r - 14 ... */
  BOTTOM_DY: 6.4,     /* :212 ... its baseline pushed out by dy, glyphs standing in */
  GAP_PX: 12,         /* the build's STAMP_RING_GAP_PX: the least page between the mark and the inner ring or the text */
  TEXT_ASC_EM: 0.81,  /* Kalam 700's ink above its baseline, MEASURED on the player's face (caps 0.767, ascenders 0.808 em;
                         scratchpad/p70-t1b/logs/probe-cap.json) - where the ring text's band starts inside the seal */
  TEXT_DESC_EM: 0.25, /* ... and below it (Q 0.167, descenders 0.250 em) */
  GOLD: "#E8B86D",    /* E99 s123: the seal's antique gold, badge-stamp.tsx:57 `color = "#E8B86D"` - THE dial */
  CONTRAST_MIN: 3.0,  /* the least contrast the seal's ink keeps on its ground [DERIVED: WCAG 2.x 1.4.11 non-text and 1.4.3
                         large text, 3:1] - the gold on the cream is 1.48:1, so there it is darkened until it reads */
  GROUND: Object.freeze({ dark: "#25313C", light: "#F4E6C7" }),   /* the grounds the name's ink names: charcoal, cream */
  /* P72 T11 (E99 s130 (2)): WHERE THE GROUND UNDER A SEAL IS MEASURED - GROUND_ANGLES samples round each of GROUND_RADII
     (fractions of the outer radius R): half-way in (the name's band under the art), the top arc (TOP_R / SRC_R), the inner
     ring (INNER_R / SRC_R) and the outer ring - where the gold is drawn. The count is the bare-prop ring's (stopaction's
     STAMP_RING_INK.ANGLES). Each is read on its own, ONCE, as the world stood at the seal's CONTACT (the engine's
     groundLumThen), and the gold holds at the WORST of them: one gold per seal, the darkest ground wins (sealGoldReport). */
  GROUND_ANGLES: 16,
  GROUND_RADII: Object.freeze([0.5, 38 / 50, 44 / 50, 1]),
  /* Kalam 700's glyph ADVANCES in em, MEASURED on the player's face (P70 T1: scratchpad/p70-t1/logs/advance-probe.json -
     no kerning, the sum is the drawn length to 0.02 px); the compiler's CHIP_STAMP_LABEL_ADVANCE_EM, held equal by
     test_stamp_is_a_seal. An unknown glyph takes the widest. */
  ADVANCE_EM: Object.freeze({
    " ": 0.385, "!": 0.478, "\"": 0.484, "#": 0.7799, "$": 0.5919, "%": 0.991, "&": 0.786, "'": 0.22, "(": 0.4779,
    ")": 0.53, "*": 0.375, "+": 0.5999, ",": 0.262, "-": 0.531, ".": 0.237, "/": 0.282, "0": 0.513, "1": 0.302,
    "2": 0.5829, "3": 0.547, "4": 0.545, "5": 0.506, "6": 0.542, "7": 0.472, "8": 0.59, "9": 0.5059, ":": 0.246,
    ";": 0.306, "<": 0.4749, "=": 0.672, ">": 0.6159, "?": 0.608, "@": 1.078, "A": 0.63, "B": 0.6239, "C": 0.617,
    "D": 0.6659, "E": 0.551, "F": 0.5419, "G": 0.597, "H": 0.6509, "I": 0.309, "J": 0.486, "K": 0.602, "L": 0.546,
    "M": 0.7559, "N": 0.631, "O": 0.6189, "P": 0.5489, "Q": 0.659, "R": 0.601, "S": 0.5519, "T": 0.544, "U": 0.5949,
    "V": 0.532, "W": 0.7849, "X": 0.5849, "Y": 0.561, "Z": 0.6459, "[": 0.463, "\\": 0.5999, "]": 0.521, "^": 0.422,
    "_": 0.6189, "`": 0.258, "a": 0.51, "b": 0.567, "c": 0.489, "d": 0.5389, "e": 0.4879, "f": 0.435, "g": 0.481,
    "h": 0.563, "i": 0.26, "j": 0.26, "k": 0.4929, "l": 0.266, "m": 0.819, "n": 0.5539, "o": 0.456, "p": 0.5379,
    "q": 0.519, "r": 0.3619, "s": 0.467, "t": 0.451, "u": 0.486, "v": 0.422, "w": 0.71, "x": 0.474, "y": 0.52,
    "z": 0.48, "{": 0.462, "|": 0.456, "}": 0.6259, "~": 0.586
  }),
  ADVANCE_MAX_EM: 1.078,
});

/* WCAG relative luminance and contrast of two #RRGGBB colours */
const sealLum = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
  .map((c) => (c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)))
  .reduce((a, c, i) => a + c * [0.2126, 0.7152, 0.0722][i], 0);
/* ... of a colour on a ground given as a luminance (a MEASURED ground is one) */
const sealOnLum = (hex, g) => { const l = sealLum(hex); return (Math.max(l, g) + 0.05) / (Math.min(l, g) + 0.05); };
export const sealContrast = (a, b) => sealOnLum(a, sealLum(b));
const sealHex = (rgb) => "#" + rgb.map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0").toUpperCase()).join("");
/* the measured luminances of a ground - one number or the samples under a seal - with every unmeasured one dropped */
const sealGrounds = (ground) => (Array.isArray(ground) ? ground : [ground])
  .filter((g) => g != null && Number.isFinite(+g)).map(Number);
/* P72 T11 (E99 s130 (2)): THE SEAL'S INK ON A MEASURED GROUND - `ground` a WCAG luminance (0..1) or the samples under the
   seal. ONE GOLD PER SEAL, THE DARKEST GROUND WINS (the plan's rule, the parent's reviews):
     1. a candidate counts if it holds CONTRAST_MIN against EVERY sample, so the WORST one binds - the darkest ground for
        a darkened gold, the lightest for a lightened one. GOLD as it is wherever it holds; else the LEAST change that
        holds, in 1 % steps up to 99 (never white or black): GOLD's channels scaled down (the cream's law: #A07F4B at the
        default GOLD, 3.02:1) or mixed toward white, whichever holds in fewer steps (a tie darkens);
     2. a spread NO ink can hold (a dark photo with one highlight, a seal across a horizon) takes the gold of the DARKEST
        sample alone - so a dark photo with one bright spot keeps #E8B86D, as the base did - and says so.
   The report: { ink, min, max, n (the measured samples), worst (the ink's ratio at its worst sample), holds }. */
const SEAL_STEPS = 99;
const sealGoldSteps = (gs, gold) => {
  const min = CHIP_SEAL.CONTRAST_MIN, worst = (hex) => Math.min(...gs.map((g) => sealOnLum(hex, g)));
  if (worst(gold) >= min) return gold;
  const rgb = [1, 3, 5].map((i) => parseInt(gold.slice(i, i + 2), 16));
  let best = gold;
  for (let s = 1; s <= SEAL_STEPS; s++) {
    const down = sealHex(rgb.map((v) => v * (100 - s) / 100));
    if (worst(down) >= min) return down;
    const up = sealHex(rgb.map((v) => v + (255 - v) * s / 100));
    if (worst(up) >= min) return up;
    if (s === SEAL_STEPS) best = worst(down) >= worst(up) ? down : up;
  }
  return gs.length === 1 ? best : null;   /* one ground always has an answer within the steps; a spread may have none */
};
export const sealGoldReport = (ground, gold = CHIP_SEAL.GOLD) => {
  const gs = sealGrounds(ground);
  if (!gs.length) return { ink: gold, min: null, max: null, n: 0, worst: null, holds: null };
  const lo = Math.min(...gs), hi = Math.max(...gs);
  const ink = sealGoldSteps(gs, gold) || sealGoldSteps([lo], gold);
  const worst = Math.min(...gs.map((g) => sealOnLum(ink, g)));
  return { ink, min: lo, max: hi, n: gs.length, worst, holds: worst >= CHIP_SEAL.CONTRAST_MIN };
};
export const sealGoldOn = (ground, gold = CHIP_SEAL.GOLD) => sealGoldReport(ground, gold).ink;
/* THE SEAL'S INK on its ground. P72 T11 (E99 s130 (2)): the ground MEASURED under the seal (`ground`, the luminances the
   engine's groundLumAt reads at sealGroundSamples - or one luminance) when anything was measured, the darkest ground
   winning; else the ground the row's `ink` names, as P70 T1b had it: GOLD on the dark ground as it is, darkened on the
   light one until it holds CONTRAST_MIN against the cream. */
export const sealGold = (sp, gold = CHIP_SEAL.GOLD, ground = null) => {
  if (sealGrounds(ground).length) return sealGoldOn(ground, gold);
  return sealGoldOn(sealLum(sp && sp.ink === "charcoal" ? CHIP_SEAL.GROUND.light : CHIP_SEAL.GROUND.dark), gold);
};
/* P72 T11: the ground's samples [[x, y], ...] about the seal's centre (cx, cy) at its outer radius R - GROUND_RADII x
   GROUND_ANGLES, in the caller's own px */
export const sealGroundSamples = (cx, cy, R) => {
  const S = CHIP_SEAL, out = [];
  for (const f of S.GROUND_RADII) {
    for (let i = 0; i < S.GROUND_ANGLES; i++) { const a = 2 * Math.PI * i / S.GROUND_ANGLES; out.push([cx + R * f * Math.cos(a), cy + R * f * Math.sin(a)]); }
  }
  return out;
};

/* RING TEXT, GLYPH BY GLYPH (the parent's frame read: a textPath bunched and drifted): each glyph's CENTRE sits at its
   arc length from the arc's middle, laid by the measured advances plus the source's tracking between glyphs, the whole
   line centred on the arc's axis (the top's at 12 o'clock, the bottom's at 6). `a` is the glyph's angle from that axis
   in radians, positive to the reader's right; `len` the line's length along the arc. */
export const sealGlyphs = (text, rho, size, track) => {
  const adv = [...String(text)].map((ch) => (CHIP_SEAL.ADVANCE_EM[ch] != null ? CHIP_SEAL.ADVANCE_EM[ch] : CHIP_SEAL.ADVANCE_MAX_EM) * size);
  const len = adv.reduce((a, v) => a + v, 0) + Math.max(0, adv.length - 1) * track;
  let s = -len / 2;
  const glyphs = [...String(text)].map((ch, i) => { const c = s + adv[i] / 2; s += adv[i] + track; return { ch, a: c / rho }; });
  return { len, glyphs };
};

const chip01 = (v) => Math.min(1, Math.max(0, v));

/* THE LANDING at t: the spring's normalised clock u, the scale it drives, the drop it rides and the fade. */
export const chipLand = (t, at, o = {}) => {
  const P = Object.assign({}, CHIP, o), u = chip01((t - at) / P.LAND_S), s = springPop(u);
  return { u, scale: P.POP_FROM + (1 - P.POP_FROM) * s, dy: (s - 1) * P.DROP_PX, fade: chip01((t - at) / P.FADE_S) };
};

/* THE CROSS at t in [0, 1]: 0 until cross_at, 1 CROSS_S later; a chip declared crossed is 1 from its landing. */
export const chipCrossF = (sp, t, o = {}) => {
  const P = Object.assign({}, CHIP, o);
  if (!Number.isFinite(+sp.cross_at)) return sp.state === "crossed" ? 1 : 0;
  return chip01((t - +sp.cross_at) / P.CROSS_S);
};

/* the two strokes of the X from the cross's fraction: the first over its first half, the second over the second */
export const chipStrokes = (f) => [chip01(f * 2), chip01(f * 2 - 1)];

/* P71 T12: THE TICK at t in [0, 1] - the cross's sibling on its own field: 0 until tick_at, 1 CROSS_S later, and 0 on a
   chip that names no tick_at (there is no "lands ticked" state). */
export const chipTickF = (sp, t, o = {}) => {
  const P = Object.assign({}, CHIP, o);
  if (sp.tick_at == null || !Number.isFinite(+sp.tick_at)) return 0;
  return chip01((t - +sp.tick_at) / P.CROSS_S);
};

/* the check's two strokes from the tick's fraction, split by their LENGTHS so the hand moves at one speed through the
   knee (the X's strokes are equal, so halves are the same law there) */
export const chipTickStrokes = (f, o = {}) => {
  const K = o.TICK || CHIP.TICK;
  const l1 = Math.hypot(K[1][0] - K[0][0], K[1][1] - K[0][1]), l2 = Math.hypot(K[2][0] - K[1][0], K[2][1] - K[1][1]);
  const d = chip01(f) * (l1 + l2);
  return [chip01(d / l1), chip01((d - l1) / l2)];
};

/* P71 T12: THE LIT HALO. The blink onsets of a `pulse: true` lit chip (none otherwise): PULSE_N of them, from the settle
   (at + LAND_S), PULSE_S apart - the gate credits one event at each (gate_motion_density, the chip's "pulse" edge). */
export const chipPulseOnsets = (sp, o = {}) => {
  const P = Object.assign({}, CHIP, o);
  if (!(sp && sp.state === "lit" && sp.pulse === true)) return [];
  return Array.from({ length: P.PULSE_N }, (_, k) => +sp.at + P.LAND_S + k * P.PULSE_S);
};
/* ... and its level at t in [0, 1]: 0 on a chip that is not `state: "lit"`; else the landing's fade, each blink dipping
   it to PULSE_LOW and back on a sine square, then holding at 1. */
export const chipLitF = (sp, t, o = {}) => {
  const P = Object.assign({}, CHIP, o);
  if (!(sp && sp.state === "lit")) return 0;
  const fade = chipLand(t, +sp.at, P).fade;
  const on = chipPulseOnsets(sp, P).find((a) => t >= a && t < a + P.PULSE_S);
  if (on === undefined) return fade;
  const w = Math.sin(Math.PI * (t - on) / P.PULSE_S);
  return fade * (1 - (1 - P.PULSE_LOW) * w * w);
};

/* P71 T12: THE CHECK BADGE's pose at t, or null without tick_at: the badge spring's landing (chipLand) on `tick_at`, its
   diameter (CHECK_D of the card) and the check's two strokes (chipTickStrokes of chipTickF). */
export const chipCheckPose = (sp, t, cardSize = CHIP.SIZE, o = {}) => {
  const P = Object.assign({}, CHIP, o);
  if (!sp || sp.tick_at == null || !Number.isFinite(+sp.tick_at)) return null;
  const land = chipLand(t, +sp.tick_at, P), f = chipTickF(sp, t, P);
  return { at: +sp.tick_at, u: land.u, scale: land.scale, dy: land.dy, fade: land.fade, d: P.CHECK_D * cardSize,
           strokes: chipTickStrokes(f, P) };
};

/* P71 T12: THE TAB's pose at t, or null: the badge spring's landing (chipLand) on `tab_at`, else on the chip's own `at`;
   its word (the move, upper-cased), its fill (the sign ink) and its width - the word's measured advance plus TAB_PAD
   each side, so the pill hugs its word. */
export const chipTabPose = (sp, t, cardSize = CHIP.SIZE, o = {}) => {
  const P = Object.assign({}, CHIP, o);
  if (!sp || typeof sp.tab !== "string" || !Object.prototype.hasOwnProperty.call(P.TAB_INK, sp.tab)) return null;
  const at = sp.tab_at != null && Number.isFinite(+sp.tab_at) ? +sp.tab_at : +sp.at;
  const land = chipLand(t, at, P), word = sp.tab.toUpperCase();   /* TAB_EM holds every word TAB_INK admits */
  return { at, u: land.u, scale: land.scale, dy: land.dy, fade: land.fade, word, fill: P.TAB_INK[sp.tab],
           w: P.TAB_EM[word] * P.TAB_TYPE + 2 * P.TAB_PAD, h: P.TAB_H };
};

/* P71 T12: the states at t, beside chipPose (which stays today's, field for field): the halo, the check and the tab. */
export const chipStates = (sp, t, cardSize = CHIP.SIZE, o = {}) =>
  ({ lit: chipLitF(sp, t, o), check: chipCheckPose(sp, t, cardSize, o), tab: chipTabPose(sp, t, cardSize, o) });

/* P71 T18: THE "?"'s POP at t for a mark whose word is `at`: the spring from `from` with overshoot `mp` over `popS`, the
   fade on the chip's FADE_S; nothing before its word. */
export const qmarkPop = (t, at, from, mp, popS) => {
  const u = chip01((t - at) / popS);
  return { u, scale: from + (1 - from) * springPop(u, mp), fade: chip01((t - at) / CHIP.FADE_S) };
};
const qNum = (v) => typeof v === "number" && Number.isFinite(v);

/* P71 T18: THE CHIP'S "?" at t, or null on a chip that names no `glyph: "?"`: HIS's pop on `glyph_at` (else the chip's own
   `at`), its ink height and its foot's gap above the card, both in the card's sides. */
export const chipQmarkPose = (sp, t, cardSize = CHIP.SIZE, o = {}) => {
  const Q = Object.assign({}, QMARK, o);
  if (!sp || sp.glyph !== "?") return null;
  const at = qNum(sp.glyph_at) ? sp.glyph_at : +sp.at, pop = qmarkPop(t, at, Q.CHIP_FROM, Q.CHIP_MP, Q.CHIP_POP_S);
  return { at, scale: pop.scale, fade: pop.fade, h: Q.CHIP_H * cardSize, gap: Q.CHIP_GAP * cardSize, ink: Q.INKS.chalk };
};

/* P71 T18: THE UNKNOWN's blink onsets (none unless `pulse: true`): CHIP.PULSE_N of them from the settle (at + SETTLE_S),
   CHIP.PULSE_S apart - the gate credits one event at each (gate_motion_density's "qpulse" edge, UNKNOWN_PULSE). */
export const unknownPulseOnsets = (sp, o = {}) => {
  const Q = Object.assign({}, QMARK, o);
  if (!(sp && sp.pulse === true)) return [];
  return Array.from({ length: CHIP.PULSE_N }, (_, k) => +sp.at + Q.SETTLE_S + k * CHIP.PULSE_S);
};

/* P71 T18: THE UNKNOWN at t - BOOM's pop, a blink's swell (pulse only), the leave inside its window; its ink height and
   ink. Everything from the declaration and t. */
export const unknownPose = (sp, t, o = {}) => {
  const Q = Object.assign({}, QMARK, o), at = +sp.at, end = at + (qNum(sp.dur) ? sp.dur : 0);
  const pop = qmarkPop(t, at, Q.POP_FROM, Q.MP, Q.POP_S);
  const on = unknownPulseOnsets(sp, Q).find((a) => t >= a && t < a + CHIP.PULSE_S && a < end);
  const w = on === undefined ? 0 : Math.sin(Math.PI * (t - on) / CHIP.PULSE_S);
  const leave = chip01((t - (end - Q.LEAVE_S)) / Q.LEAVE_S);
  return { at, scale: pop.scale * (1 + Q.PULSE_AMP * w * w), fade: pop.fade * (1 - leave), leave,
           h: qNum(sp.size) ? sp.size : Q.SIZE, ink: Q.INKS[sp.ink] || Q.INKS.neg };
};

/* P70 T1: does this chip LAND AS A STAMP? Only the stamp FORM takes the arrival (the compiler refuses it anywhere else,
   by name); a glyph chip, flow's node chips and the count array keep chipLand whatever they carry. */
export const chipStamped = (sp) => !!sp && sp.form === "stamp" && sp.arrive === "stamp";

/* THE STAMP ARRIVAL on a chip (P70 T1; E99 s87): the pose at t - at is `stampXf`'s, with no dial of the chip's own -
   the scale comes down from STAMP_ARRIVAL.FROM in area space and is exactly 1 from STAMP_LAND.tc (0.1542 s), the free
   rotation overshoots and rests at LAND_DEG, off-square, the ink runs INK [1, 0.86], the opacity rides FADE, and the
   impact ring is `stampRing` on its split curves (a multiplier of the chip's own radius, null before the contact and
   once its life is spent: never held). The ring's peak and the approach are the compiler's fit, the dock stamp's own
   law (`ring_to` / `from_to`: stamp_fit against ring_obstacles, round the mark AND its label), else the source's
   RING_TO / FROM - capped there, never clipped here. The exit the landed mark owes (E50) is `stampExit`, run INSIDE the
   chip's `dur` - it begins EXIT_S before the window closes, so the species leaves on its own curve and is gone at
   at + dur; the ring is never drawn once the exit has begun. P70 T1b (E99 s121): the ring is thrown from the CONTACT
   (stampXf) and from the SEAL's border (chipStampGroup); `ink` - heavy at the hit, easing back after it - is painted ON
   THE MARK, the seal's rings, its ring text and the name (paintChipSeal), never as a wash over the art. */
export const chipStampPose = (sp, t) => {
  const fit = Object.assign({}, Number.isFinite(+sp.ring_to) && +sp.ring_to > 0 ? { RING_TO: +sp.ring_to } : {},
    Number.isFinite(+sp.from_to) && +sp.from_to >= 1 ? { FROM: +sp.from_to } : {});   /* ... the approach it comes down from */
  const at = +sp.at, sx = stampXf(CHIP_STAMP.MASS, t - at, Object.assign({ IMPACT_SQUASH: CHIP_STAMP.SQUASH }, fit));   /* the seal is rigid */
  const out = at + (Number.isFinite(+sp.dur) ? +sp.dur : 0) - STAMP_ARRIVAL.EXIT_S, leaving = t > out;
  const ex = leaving ? stampExit(t - out) : 0;
  return { u: sx.u, scale: sx.scale, rot: sx.rot, off_deg: sx.off_deg, dx: sx.x, dy: sx.y, alpha: sx.alpha, theta: sx.theta,
           ink: sx.ink, fade: sx.opacity * (1 - ex), exit: ex, ring: leaving ? null : sx.ring, phase: sx.phase,
           cross: 0, strokes: [0, 0], dim: 1 };
};

/* P70 T1b: the seal's geometry for a stamped chip in its side x side square - null for any other chip. About the PAINTED
   centre (the group's origin): `R` the outer ring - the compiler's `seal_r` (the room the authored mark reserved), else
   the inner ring 12 px outside the mark and its name (`rc`, their half-diagonal) at the source's r - 6 of r = 50 - `rIn`
   the inner ring, and every other length the source's fraction of R: the strokes, the ring text's size and tracking,
   the top arc (baseline on it) and the bottom arc (baseline pushed out by dy). `ink` is the seal's gold on its ground -
   P72 T11: `ground` the luminances MEASURED under it (sealGold), null when nothing was. */
export const chipSeal = (sp, side, ground = null) => {
  if (!chipStamped(sp)) return null;
  const S = CHIP_SEAL, rc = chipStampPaint(sp, side).r;
  const R = Number.isFinite(+sp.seal_r) && +sp.seal_r > 0 ? +sp.seal_r : (rc + S.GAP_PX) * S.SRC_R / S.INNER_R;
  const u = R / S.SRC_R, size = S.TEXT_SIZE * u, track = S.TEXT_TRACK * u;
  const txt = (v) => (typeof v === "string" && v.trim() ? v : null);
  const top = txt(sp.ring_text), bot = txt(sp.ring_text_bottom);
  const measured = sealGrounds(ground).length ? sealGoldReport(ground) : null;   /* P72 T11: the spread it was read on */
  return { rc, R, rIn: S.INNER_R * u, outerW: S.OUTER_W * u, innerW: S.INNER_W * u, size, track, ink: sealGold(sp, CHIP_SEAL.GOLD, ground),
           ground: measured,
           top: top ? Object.assign({ text: top, r: S.TOP_R * u }, sealGlyphs(top, S.TOP_R * u, size, track)) : null,
           bottom: bot ? Object.assign({ text: bot, r: S.BOTTOM_R * u, dy: S.BOTTOM_DY * u }, sealGlyphs(bot, S.BOTTOM_R * u, size, track)) : null };
};

/* P72 T46b (R26-361 (a)): THE NAME'S KEYLINE READS THE GROUND THE GOLD LATCHED. The name is set in the seal's ink on a
   keyline in one of the two named grounds; the keyline followed the row's AUTHORED ink (charcoal under a cream row), so on
   a mid-tone photo, where the measured ground turns the gold bronze (#544227 on #9A9A9A), the bronze sat in a charcoal
   keyline at ~1.6:1 - mud. The keyline is the ground the ink was chosen AGAINST: where the seal's ink is darker than the
   darkest ground measured under it (the gold was darkened to read on a light ground) the keyline is the cream, else the
   charcoal - one read of the same latched spread (`seal.ground`, sealGoldReport's), fixed at the contact as the gold is.
   Nothing measured (node, a clip): the authored ink's keyline, byte for byte. */
export const sealKeyline = (sp, seal) => {
  const gr = seal && seal.ground;
  if (gr && gr.n > 0 && Number.isFinite(gr.min)) return sealLum(seal.ink) < gr.min ? CHIP_STAMP.INK.cream : CHIP_STAMP.INK.charcoal;
  return CHIP_STAMP.INK[sp && sp.ink === "charcoal" ? "cream" : "charcoal"];
};

/* ONE ENTRY: everything the painter draws at t, from the declaration alone. */
export const chipPose = (sp, t, o = {}) => {
  if (chipStamped(sp)) return chipStampPose(sp, t);
  const P = Object.assign({}, CHIP, o), land = chipLand(t, +sp.at, P), cross = chipCrossF(sp, t, P);
  return { u: land.u, scale: land.scale, dy: land.dy, fade: land.fade,
           cross, strokes: chipStrokes(cross), dim: 1 - (1 - P.DIM) * cross };
};

/* the sourced icon's geometry as the compiler embedded it: {vb: [x, y, w, h], el: [{t, a}]}, or null. */
export const chipGeometry = (raw) => {
  if (typeof raw !== "string" || !raw) return null;
  try { const g = JSON.parse(raw); return Array.isArray(g && g.el) && g.el.length ? g : null; } catch (e) { return null; }
};

/* Phone labels use authored newlines as real SVG lines. If a caller supplies more than the
   bounded caption can hold, preserve the words by joining the overflow into the final line;
   vertical overflow is never silently allowed. Legacy labels do not pass through this helper. */
export const chipLabelLines = (label, maxLines = CHIP.PHONE_MAX_LINES) => {
  const limit = Math.max(1, Math.floor(+maxLines || CHIP.PHONE_MAX_LINES));
  const lines = String(label == null ? "" : label).split(/\r?\n/);
  if (lines.length <= limit) return lines;
  return lines.slice(0, limit - 1).concat(lines.slice(limit - 1).join(" "));
};

/* Stamp labels are compiler-bounded to three authored lines; unlike the phone
   profile, this helper never joins or drops authored words. */
export const chipStampLabelLines = (label) => String(label == null ? "" : label).split(/\r?\n/);

const chipStampInk = (ink) => CHIP_STAMP.INK[ink] || CHIP_STAMP.INK.cream;
const chipStampSize = (size) => {
  const n = Number(size);
  return Number.isFinite(n) ? Math.max(CHIP_STAMP.MIN_SIZE, Math.min(CHIP_STAMP.MAX_SIZE, n)) : CHIP_STAMP.SIZE;
};

function paintChipStamp(ctx, b) {
  const { sp, t, svg, el, A, idle, hash, seed, si } = ctx;
  const icon = String(sp.icon || ""), catalogue = sp._catalogue;
  const badgeIcon = icon.startsWith("prop-badge-"), legacyIcon = badgeIcon || icon.startsWith("prop-icon-");
  if ((catalogue === "props" && !badgeIcon)
      || (catalogue == null && icon.startsWith("prop-") && !legacyIcon)) {
    throw new Error("chip stamp: " + sp.icon + " is a non-badge prop; E99 s87 requires a bare prop with arrive: stamp or throw");
  }
  const src = A && A["prop:" + sp.icon];
  if (!src) return; /* approved catalogue URI is mandatory; never fall back to a generic icon */
  const pose = chipPose(sp, t);
  const ix = sp.idle && sp.idle !== "none" ? idle(sp.idle, t, hash(seed | 0, si | 0, 997)) : { scale: 1, dx: 0, dy: 0 };
  const cx = b.x + b.w / 2, cy = b.y + b.h / 2;
  const requested = chipStampSize(sp.size);
  const side = Math.min(requested, b.w > 0 ? b.w : requested, b.h > 0 ? b.h : requested);
  const s = pose.scale * ix.scale;
  const stamped = chipStamped(sp);
  const seal = stamped ? chipStampSeal(ctx, cx, cy, side) : null;   /* P72 T11: its gold on the ground under it at its contact */
  const g = stamped ? chipStampGroup(ctx, pose, ix, cx, cy, side, s, seal)
    : el("g", "chipstamp", svg, { opacity: pose.fade.toFixed(3),
      transform: "translate(" + (cx + ix.dx).toFixed(1) + " " + (cy + pose.dy + ix.dy).toFixed(1) + ") scale(" + s.toFixed(4) + ")" });
  const off = stamped ? chipStampPaint(sp, side).off : [0, 0];   /* the art about its PAINTED centre, the group's origin */
  if (stamped) paintChipSeal(ctx, g, seal, pose.ink);   /* P70 T1b: the seal, under the art, in the mark's group */
  el("image", "chipstampart", g, {
    x: (-side / 2 - off[0]).toFixed(1), y: (-side / 2 - off[1]).toFixed(1), width: side.toFixed(1), height: side.toFixed(1),
    href: src, preserveAspectRatio: "xMidYMid meet",
  });
  if (sp.label) {
    const lines = chipStampLabelLines(sp.label);
    const L = chipStampLabelType(stamped);
    const labAt = {
      x: stamped ? (-off[0]).toFixed(1) : 0, y: (side / 2 - off[1] + L.gap).toFixed(1), "text-anchor": "middle",
      style: "font-family:Kalam,cursive;font-size:" + L.size + "px;font-weight:700;fill:" + chipStampInk(sp.ink)
        + ";paint-order:stroke;stroke:" + (stamped ? sealKeyline(sp, seal) : chipStampInk(sp.ink === "charcoal" ? "cream" : "charcoal"))   /* P72 T46b: a seal's keyline reads its latched ground */
        + ";stroke-width:4px;stroke-linejoin:round",
    };
    if (stamped) {   /* P70 T1b: the name is the SEAL's ink - gold (E99 s123) - and eases back with it (s121 (4)) */
      labAt.style = labAt.style.replace("fill:" + chipStampInk(sp.ink) + ";", "fill:" + seal.ink + ";");
      labAt.opacity = pose.ink.toFixed(3);
    }
    const lab = el("text", "chipstamplab", g, labAt);
    if (lines.length > 1) {
      lines.forEach((line, index) => {
        const ts = el("tspan", "", lab, { x: stamped ? (-off[0]).toFixed(1) : 0, dy: index ? L.line : 0 });
        ts.textContent = line;
      });
    } else lab.textContent = lines[0];
  }
}

/* P70 T1: the label's type - the floor under the stamp arrival (LABEL_FLOOR, the gap and the line step scaled with it),
   today's LABEL_SIZE otherwise, written exactly as before */
export const chipStampLabelType = (stamped) => {
  if (!stamped) return { size: CHIP_STAMP.LABEL_SIZE, gap: CHIP_STAMP.LABEL_GAP, line: CHIP_STAMP.LABEL_LINE_H };
  const k = CHIP_STAMP.LABEL_FLOOR / CHIP_STAMP.LABEL_SIZE;
  return { size: CHIP_STAMP.LABEL_FLOOR, gap: +(CHIP_STAMP.LABEL_GAP * k).toFixed(2), line: +(CHIP_STAMP.LABEL_LINE_H * k).toFixed(2) };
};

/* P70 T1: the stamped chip's PAINTED box in its side x side square - the compiler's `paint` [x0, y0, x1, y1] (fractions of
   the square: the UNION of the cutout's alpha box and the label's box, so it may run past [0, 1]), else the whole
   square. `off` is that box's centre offset from the square's centre - the group turns about it - and `r` its
   half-diagonal: the ring's base radius, as the dock's is, so the ring circles the mark and its name at every angle. */
export const chipStampPaint = (sp, side) => {
  const p = Array.isArray(sp.paint) && sp.paint.length === 4 && sp.paint.every((v) => Number.isFinite(+v)) ? sp.paint.map(Number) : [0, 0, 1, 1];
  return { off: [side * ((p[0] + p[2]) / 2 - 0.5), side * ((p[1] + p[3]) / 2 - 0.5)],
           r: 0.5 * Math.hypot(side * (p[2] - p[0]), side * (p[3] - p[1])) };
};

/* P72 T11 (E99 s130 (2)): THE SEAL, ITS GOLD ON THE GROUND MEASURED UNDER IT, FIXED ONCE AT ITS CONTACT (the parent's
   review): every frame of the seal's life - the approach, the squash, the rest, the exit - asks for the SAME ground, the
   one under the seal at `at + STAMP_LAND.tc` (the instant the mark is its own size, stampXf's scale exactly 1): the
   samples about the PAINTED centre at the contact's idle pose, at the seal's radius times the contact's scale, read by
   the engine's ctx.groundLumThen(pts, t0) as the world STOOD at t0 (its Ken Burns and camera at the contact, so a push
   or a slide under the seal never steps its gold). A pure function of the declaration, not a state: a seek is the play.
   Each sample is its own luminance (null unmeasured), so the worst binds - one gold per seal, the darkest ground wins.
   The rings, the ring text, the name and the shockwave all take it. Absent a reader (node): the row's authored ground. */
function chipStampSeal(ctx, cx, cy, side) {
  const { sp, groundLumThen, idle, hash, seed, si } = ctx, P = chipStampPaint(sp, side), R = chipSeal(sp, side).R;
  if (typeof groundLumThen !== "function") return chipSeal(sp, side, null);
  const tc = +sp.at + STAMP_LAND.tc;
  const ic = sp.idle && sp.idle !== "none" ? idle(sp.idle, tc, hash(seed | 0, si | 0, 997)) : { scale: 1, dx: 0, dy: 0 };
  const pts = sealGroundSamples(cx + P.off[0] + ic.dx, cy + P.off[1] + ic.dy, R * ic.scale);
  return chipSeal(sp, side, groundLumThen(pts, tc));
}

/* P70 T1: the stamped chip's group and its impact ring. The ring is drawn FIRST, in the species layer under the mark,
   radiating from the contact point (the painted centre on the surface) at the art's own radius x ring.r - it does not
   ride the mark's scale, turn or dip. The group carries the mark's pose as the dock's `stopCss` writes it: translate
   (the receiver's dip), the free rotation, the clamped scale, the hit's squash frame; about the painted centre. */
function chipStampGroup(ctx, pose, ix, cx, cy, side, s, seal) {
  const { sp, svg, el } = ctx;
  const P = chipStampPaint(sp, side), pcx = cx + P.off[0] + ix.dx, pcy = cy + P.off[1] + ix.dy;
  const r0 = seal ? seal.R : P.r;   /* P70 T1b: thrown from the SEAL's border, as the source's is (:156 r * (1 + shock)) */
  if (pose.ring) {
    /* P70 T1c (E99 s127 (2)): THE SHOCKWAVE IS THE SEAL'S GOLD, as the reference's is its seal's colour (badge-stamp.tsx:158
       strokes the shock circle in `color`, the seal's one ink) - the seal's own ink, so it takes the seal's contrast law
       (sealGold: P72 T11, on the ground measured under the seal) and is never the bare prop's chalk or charcoal. Its
       timing is T1b's, unchanged. */
    el("circle", "chipstampring", svg, { cx: pcx.toFixed(1), cy: pcy.toFixed(1), r: (r0 * pose.ring.r).toFixed(1), fill: "none",
      stroke: seal.ink, "stroke-width": pose.ring.width.toFixed(2),
      opacity: pose.ring.alpha.toFixed(3) });
  }
  const a = Math.abs(pose.alpha || 0), th = (pose.alpha || 0) < 0 ? (pose.theta || 0) + Math.PI / 2 : (pose.theta || 0);
  const sq = a > 1e-6 ? " matrix(" + squashMatrix(th, a).map((v) => v.toFixed(4)).join(" ") + " 0 0)" : "";
  return el("g", "chipstamp", svg, { opacity: pose.fade.toFixed(3),
    transform: "translate(" + pcx.toFixed(1) + " " + (pcy + (pose.dy || 0)).toFixed(1) + ") rotate(" + pose.rot.toFixed(2)
      + ") scale(" + s.toFixed(4) + ")" + sq });
}

/* P70 T1b: THE SEAL, drawn into the mark's group about its origin (the painted centre) - so it rides the pose (the dip,
   the free turn, the clamped scale, the squash) and the group's fade and exit, exactly as the art does. THE INK EASES
   BACK ON THE MARK (s121 (4)): the rings and the ring text take `ink` (1 at the hit -> 0.86 as the pressure comes off,
   stopaction's stampInk) at the source's own ratios (:179 ink, :188 ink x 0.7, :198 ink x 0.9); the PICTURE is the
   payload and is never washed. RING TEXT is laid glyph by glyph (sealGlyphs): the TOP's glyphs stand OUT from their arc,
   each turned by its angle; the BOTTOM's stand IN, each turned by minus its angle, so both read left to right - "a
   shared full-circle path would invert everything on the bottom half" (:137-139). A space is an advance, not a glyph. */
function paintChipSeal(ctx, g, seal, ink) {
  if (!seal) return;
  const { el } = ctx, S = CHIP_SEAL, col = seal.ink, k = Number.isFinite(+ink) ? +ink : 1;
  const gr = seal.ground, named = gr ? { "data-ground-min": gr.min.toFixed(4), "data-ground-max": gr.max.toFixed(4),
    "data-ground-worst": gr.worst.toFixed(3), "data-ground-holds": gr.holds ? "1" : "0" } : {};   /* P72 T11: the spread, for a probe */
  el("circle", "chipseal", g, Object.assign({ cx: 0, cy: 0, r: seal.R.toFixed(1), fill: "none", stroke: col,
    "stroke-width": seal.outerW.toFixed(2), opacity: k.toFixed(3) }, named));
  el("circle", "chipsealin", g, { cx: 0, cy: 0, r: seal.rIn.toFixed(1), fill: "none", stroke: col,
    "stroke-width": seal.innerW.toFixed(2), opacity: (k * S.INNER_A).toFixed(3) });
  [[seal.top, 1], [seal.bottom, -1]].forEach(([arc, side]) => {
    if (!arc) return;
    const tg = el("g", "chipsealtext", g, { opacity: (k * S.TEXT_A).toFixed(3),
      style: "font-family:Kalam,cursive;font-size:" + seal.size.toFixed(2) + "px;font-weight:700;fill:" + col });
    const rho = side > 0 ? arc.r : arc.r + arc.dy;   /* the BASELINE's radius */
    arc.glyphs.forEach((gl) => {
      if (!gl.ch.trim()) return;
      const x = rho * Math.sin(gl.a), y = side > 0 ? -rho * Math.cos(gl.a) : rho * Math.cos(gl.a);
      const deg = (side > 0 ? gl.a : -gl.a) * 180 / Math.PI;
      const t = el("text", "chipsealglyph", tg, { x: x.toFixed(2), y: y.toFixed(2), "text-anchor": "middle",
        transform: "rotate(" + deg.toFixed(3) + " " + x.toFixed(2) + " " + y.toFixed(2) + ")" });
      t.textContent = gl.ch;
    });
  });
}

/* THE PAINTER. ctx is the template's species context (see SPECIES_PAINTERS in the player): the declaration,
   the clock, the layer and the shared helpers by name. Draws into one group whose transform carries the
   landing and the idle, so every child is written in the card's own centred coordinates. */
export function paintChip(ctx) {
  const { sp, t, svg, el, A, resolveTarget, drawOn, hash, idle, seed, si } = ctx;
  const b = resolveTarget(sp.target);
  if (!b) return;   /* the targeting law: no resolved target, nothing painted */
  if (sp.form === "stamp") {
    paintChipStamp(ctx, b);
    return;
  }
  const phone = sp.readability === "landscape-phone";
  const pose = chipPose(sp, t);
  const ix = sp.idle && sp.idle !== "none" ? idle(sp.idle, t, hash(seed | 0, si | 0, 991)) : { scale: 1, dx: 0, dy: 0 };
  const cx = b.x + b.w / 2, cy = b.y + b.h / 2;   /* a point resolves to w = h = 0; a region centres the chip in it */
  const s = pose.scale * ix.scale;
  const g = el("g", "", svg, { opacity: pose.fade.toFixed(3),
                               transform: "translate(" + (cx + ix.dx).toFixed(1) + " " + (cy + pose.dy + ix.dy).toFixed(1) + ") scale(" + s.toFixed(4) + ")" });
  const body = el("g", "", g, { opacity: pose.dim.toFixed(3) });   /* the card dims under its own X; the X does not */
  const cardSize = phone ? 110 : CHIP.SIZE;
  const h = cardSize / 2;
  const st = chipStates(sp, t, cardSize);   /* P71 T12: the halo, the tick, the tab - zero / null on a chip without them */
  if (st.lit > 0) paintChipHalo(el, body, h, st.lit);
  const cardAttrs = { x: (-h).toFixed(1), y: (-h).toFixed(1), width: cardSize, height: cardSize, rx: CHIP.RX };
  if (phone) cardAttrs.style = "fill:#F4E6C7;stroke:#25313C;stroke-width:3";
  el("rect", "chipcard", body, cardAttrs);
  const geo = chipGeometry(A ? A["icon:" + sp.icon] : null);
  if (geo) {
    const glyphSize = phone ? 60 : CHIP.GLYPH;
    const vb = geo.vb || [0, 0, 24, 24], k = glyphSize / Math.max(vb[2] || 1, vb[3] || 1);
    const glyphAttrs = { transform: "translate(" + (-glyphSize / 2).toFixed(1) + " " + (-glyphSize / 2).toFixed(1) + ") scale(" + k.toFixed(4) + ") translate(" + (-vb[0]) + " " + (-vb[1]) + ")" };
    if (phone) glyphAttrs.style = "fill:none;stroke:#25313C;stroke-width:2;stroke-linecap:round;stroke-linejoin:round";
    const gg = el("g", "chipglyph", body, glyphAttrs);
    geo.el.forEach((n) => el(n.t, "", gg, phone
      ? Object.assign({}, n.a, { style: "fill:none;stroke:#25313C;stroke-width:2;stroke-linecap:round;stroke-linejoin:round" })
      : n.a));   /* the sourced geometry verbatim - the compiler already kept only shapes */
  }
  if (sp.label) {
    const lines = phone ? chipLabelLines(sp.label) : [sp.label];
    const labelAttrs = { x: 0, y: (h + (phone ? CHIP.PHONE_LABEL_DY : CHIP.LABEL_DY)).toFixed(1) };
    if (phone) labelAttrs.style = "font-size:" + CHIP.PHONE_LABEL_SIZE + "px;font-weight:700;font-family:Inter,Arial,sans-serif;fill:#25313C;paint-order:stroke;stroke:#F4E6C7;stroke-width:5px";
    const lab = el("text", "chiplab", body, labelAttrs);
    if (phone && lines.length > 1) {
      lines.forEach((line, index) => {
        const ts = el("tspan", "", lab, { x: 0, dy: index ? CHIP.PHONE_LABEL_LINE_H : 0 });
        ts.textContent = line;
      });
    } else lab.textContent = lines[0];
  }
  if (pose.cross > 0) {   /* the two-stroke X, drawn by the curvature stroke over the card's diagonals */
    const a = cardSize * 0.34;
    [["M" + (-a).toFixed(1) + " " + (-a).toFixed(1) + " L" + a.toFixed(1) + " " + a.toFixed(1), pose.strokes[0]],
     ["M" + a.toFixed(1) + " " + (-a).toFixed(1) + " L" + (-a).toFixed(1) + " " + a.toFixed(1), pose.strokes[1]]]
      .forEach(([d, f]) => { if (f > 0) drawOn(el("path", "sq", g, { d }), f); });
  }
  if (st.check && st.check.fade > 0) paintChipCheck(el, g, h, st.check, drawOn);   /* P71 T12: the badge; the card keeps its ink */
  if (st.tab && st.tab.fade > 0) paintChipTab(el, g, h, st.tab);
  const qm = chipQmarkPose(sp, t, cardSize);   /* P71 T18: the "?" above the card; null on a chip without it */
  if (qm && qm.fade > 0) paintChipQmark(el, g, h, qm);
}

/* P71 T18: THE "?" as a TEXT mark: its ink's centre at the group's origin (its baseline h / 2 below), so the pop scales
   it about its own middle. */
function qmarkText(el, g, h, style) {
  const q = el("text", "qmark", g, { x: 0, y: (h / 2).toFixed(1), "text-anchor": "middle",
    style: "font-family:" + QMARK.FACE + ";font-size:" + (h / QMARK.INK_EM).toFixed(2) + "px;font-weight:" + QMARK.WEIGHT + ";" + style });
  q.textContent = "?";
  return q;
}

/* P71 T18: THE CHIP'S "?" centred above the card (HIS 01:48), in the chip's group (it rides the landing and the idle). */
function paintChipQmark(el, g, h, qm) {
  const cy = -h - qm.gap - qm.h / 2;
  const qg = el("g", "chipqmark", g, { opacity: qm.fade.toFixed(3),
    transform: "translate(0 " + cy.toFixed(1) + ") scale(" + qm.scale.toFixed(4) + ")" });
  qmarkText(el, qg, qm.h, "fill:" + qm.ink + ";paint-order:stroke;stroke:" + QMARK.KEYLINE + ";stroke-width:" + QMARK.KEYLINE_W + "px");
}

/* P71 T18 - THE UNKNOWN's PAINTER (the module rule: registered below, beside the chip's). A large "?" centred on its
   point, or in its region; the idle a held thing owes (E49) is the chip's, applied the same way. It paints on the layer
   paintSpecies chose - a point or a region is #species, above the docks, so it stands over the collage it resolves. */
export function paintUnknown(ctx) {
  const { sp, t, svg, el, resolveTarget, hash, idle, seed, si } = ctx;
  const b = resolveTarget(sp.target);
  if (!b) return;   /* the targeting law: no resolved target, nothing painted */
  const p = unknownPose(sp, t);
  if (!(p.fade > 0)) return;
  const ix = sp.idle && sp.idle !== "none" ? idle(sp.idle, t, hash(seed | 0, si | 0, 991)) : { scale: 1, dx: 0, dy: 0 };
  const cx = b.x + b.w / 2 + ix.dx, cy = b.y + b.h / 2 + ix.dy;
  const g = el("g", "unknown", svg, { opacity: p.fade.toFixed(3),
    transform: "translate(" + cx.toFixed(1) + " " + cy.toFixed(1) + ") scale(" + (p.scale * ix.scale).toFixed(4) + ")" });
  const a = Math.round(QMARK.GLOW_A * 255).toString(16).padStart(2, "0");
  qmarkText(el, g, p.h, "fill:" + p.ink + ";filter:drop-shadow(0 0 " + (QMARK.GLOW_K * p.h).toFixed(1) + "px " + p.ink + a + ")");
}

/* P71 T12: THE CHECK BADGE centred ON the card's top edge (HIS 06:13), in the chip's group (it rides the landing and the
   idle): a disc in the positive ink, springing in about its centre, and its charcoal check drawn in two strokes. */
function paintChipCheck(el, g, h, ck, drawOn) {
  const r = ck.d / 2, f = (v) => v.toFixed(1);
  const cg = el("g", "chipcheck", g, { opacity: ck.fade.toFixed(3),
    transform: "translate(0 " + f(-h + ck.dy) + ") scale(" + ck.scale.toFixed(4) + ")" });
  el("circle", "chipcheckdisc", cg, { cx: 0, cy: 0, r: f(r), style: "fill:" + CHIP.TICK_INK + ";stroke:none" });
  const K = CHIP.TICK.map(([x, y]) => f(x * r) + " " + f(y * r));
  [["M" + K[0] + " L" + K[1], ck.strokes[0]], ["M" + K[1] + " L" + K[2], ck.strokes[1]]]
    .forEach(([d, k]) => { if (k > 0) drawOn(el("path", "chipcheckmark", cg, { d, style: "fill:none;stroke:" + CHIP.CHECK_MARK
      + ";stroke-width:" + f(CHIP.TICK_W * r) + ";stroke-linecap:round;stroke-linejoin:round" }), k); });
}

/* P71 T12: THE HALO, first in the card's body (so the card covers its inside and it dims with a cross): a rounded ring
   LIT_PAD outside the card in the focus yellow, glowing in its own ink, at the level chipLitF gives. */
function paintChipHalo(el, body, h, level) {
  const r = h + CHIP.LIT_PAD;
  el("rect", "chiphalo", body, { x: (-r).toFixed(1), y: (-r).toFixed(1), width: (2 * r).toFixed(1), height: (2 * r).toFixed(1),
    rx: CHIP.RX + CHIP.LIT_PAD, opacity: level.toFixed(3),
    style: "fill:none;stroke:" + CHIP.LIT_INK + ";stroke-width:" + CHIP.LIT_W + ";filter:drop-shadow(0 0 " + CHIP.LIT_GLOW
      + "px rgba(245,183,46," + CHIP.LIT_GLOW_A + "))" });
}

/* P71 T12: THE TAB, a rounded PILL centred ON the card's top edge - half above it, half on it - in the chip's group (it
   rides the landing and the idle); the spring scales it about its own centre; its word's caps centred in it. */
function paintChipTab(el, g, h, tab) {
  const w = tab.w, H = tab.h, f = (v) => v.toFixed(1);
  const tg = el("g", "chiptab", g, { opacity: tab.fade.toFixed(3),
    transform: "translate(0 " + f(-h + tab.dy) + ") scale(" + tab.scale.toFixed(4) + ")" });
  el("rect", "chiptabbody", tg, { x: f(-w / 2), y: f(-H / 2), width: f(w), height: f(H), rx: f(H / 2),
    style: "fill:" + tab.fill + ";stroke:none" });
  const lab = el("text", "chiptablab", tg, { x: 0, y: f(0.3635 * CHIP.TAB_TYPE), "text-anchor": "middle",
    style: "font-family:Inter,Arial,sans-serif;font-size:" + CHIP.TAB_TYPE + "px;font-weight:700;fill:" + CHIP.TAB_TEXT + ";stroke:none" });
  lab.textContent = tab.word;
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
   import this file for the math above without the template's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.chip = paintChip;
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.unknown = paintUnknown;   /* P71 T18: the large "?" shares the chip's mark */

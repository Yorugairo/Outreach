"""MOTION-DENSITY GATE - the screen never goes still (ruling E21, doc 29 s9.25).

Runs on a BUILT episode directory (stage 7/8 output): the compiled
`*.timeline.json` (scenes, docks, caption pages, runtime), `evidence-dock.json`
(scheduled docks - read ONLY when the timeline carries no docks: P35 T0 found
the dock file on an older clock than the timeline, divergence 26.4 vs 50.4)
and `motion-plan.json` (cues). It is the check the
hand-authored shot table never had: doc 29 s8.19's 12s gap-fill lived in the
five-minute cut builder and printed a number; Steel and Paper shipped with
23% of its runtime in stretches over 12s where nothing moved but the Ken
Burns and a lower-third caption, and its opening minute was the thinnest
minute of the video.

What counts as a VISUAL EVENT (doc 29 s9.25): a scene boundary, a dock
entering or leaving, a badge/pill reveal, captions in STAGE mode, or a
LEDGER PAGE building (s9.28 C5 / D1: roll-out, field, punch, build start,
build complete - the hold after that is still), or a TARGETED SPECIES
firing on a scene (s9.27 MOTION MENU "Gate treatment" column: a punch at
its punch, a focus zoom at departure and arrival, plate life stepping at
10 fps, ...), or a VIDEO DOCK holding the card (E44 / R26-7: a docked clip
is moving pictures, credited one event per second it is on screen - an
IMAGE dock is a still card and credits only its enter and exit). A page
START is an EVIDENCE ENTRY (D2). Ken Burns and lower-third (anchor-mode)
captions do NOT count - they are what a viewer reads as stillness.

  M01  no stretch > 12s without a visual event            FAIL   (s8.19 / s9.25)
  M02  stretches > 8s (working target)                    WARN
  M03  evidence enters at least every 45s, every phase    FAIL   ("evidence every 15-45s")
  M04  distinct plates >= runtime / 12s                   WARN   (s9.13)
  M05  no plate held > 20s with the frame DEAD             FAIL   (s9.13 + E69: live in the frame)
  M06  caption cadence: 4-6 words a page, >= 20 pages/min WARN   (s9.15 r7 / build_caption_pages)
  M07  the opening minute is not the thinnest minute      FAIL   (E21: P1 densest, never thinnest)
  M08  stage-mode captions declared on every still stretch FAIL once the timeline carries cap_mode;
       until then INFO listing where stage captions are REQUIRED + a JUDGE row
  M09  one camera move per window: no scene stacks two of   FAIL   (s9.27 precedence / s9.28 C3)
  M14  a camera move never overlaps an evidence build      FAIL   (47 s2 G-a / doc 07 Pillar 4; P49 T6: an authored
       key segment is a move too)
  M24  every pointing species' target is IN FRAME when     FAIL   (P49 T6: the camera's state at `at` from the scene's
       it fires (the camera track evaluated at the word)           keys; a datum's box is the page's plot; identity passes)
       punch | focus_zoom | pull_back, or one over Ken Burns
  M10  opening stillness: no still stretch > 6s begins      FAIL   (E24 / s9.29: 4-6s in the first 30-60s)
       in the first 60s
  M11  the first chart: enters 0:08-0:20 (long form) or     FAIL   (E24 / s9.29 long, E44 short;
       0:00-0:10 on a short, annotated by a                        sound cue absent = WARN)
       spotlight/callout/punch/focus_zoom within 1.5s
  M12  a chart is the proof, not the homework: a chart dock FAIL   (E25 / s9.30)
       never spans a scene boundary; hold <= 10s anywhere,
       <= 6s inside the opening minute (re-enter it instead)
  M18  frozen frames (E49): no run of bit-identical rendered  WARN   (E49 / P47 T5; INFO until
       frames longer than 0.5s, read from frame-hashes.json          measure_frozen_frames.py has run)
       AND from frame-hashes.<layer>.json per LAYER when the           (R26-13: a caption boiling over a frozen
       tool ran with --layers: the page, the docks and the                     page passes the whole-frame hash;
       captions each on their own, a dock and a caption read                   the page layer is the read that sees it;
       only inside their own windows; the whole frame is reported              an empty layer is not a held thing)
  M19  build_to holds (P47 T2): the line resting at a datum   INFO   (only when a build_to is declared)
       between two caps, listed by name
  M20  the cadence rule per arrival (P47 T1): a thrown card  INFO   (only when a dock arrives by throw|land)
       steps on 1s above 250 px/s, on 2s below
  M23  chart transitions (P48): every chart_to listed with  FAIL   (a page with two states and no transition;
       its clock; one inside the build beat or within 0.5s of        WARN inside the build / at the edge; ledger pages only)
       the exit WARNs; two states and no chart_to FAILs
  M21  the chart's deployed life (E50): from a page's LAST   WARN   (over 12s; INFO over 8s; ledger pages only)
       data mark to its exit or its undraw - 6-8s average, 12s at most
  M22  a push is tied to a landing (E51): every punch /     WARN   (an untied push is filler)
       focus_zoom has a landing on its scene inside (at - 1.5s, at + 0.3s)
  M17  the morph's match-cut invariants (P47 T3; per     WARN   (per MORPH - a page's enter morph and every morph_to;
       morph since P48 T5): centroid <= 6 % W, axis             INFO until measure_morph.py has run)
       <= 15 deg, area >= 60 %, det J > 0
  M25  layout (P51 T2): at every landing, a SETTLED card       FAIL   (E45 s1 / E52 / E60; a dock inside the safe
       over the chart's data, over a line of the page's ink            zone WARNs; INFO until probe.py <build> --gate
       or in the caption strip; type under 11 CSS px on a             has written layout-probe.json)
       phone. Read from layout-probe.json, never a browser
  M26  values (R26-40): every bar whose number is PRINTED       FAIL   (E28 / E53; INFO until probe.py <build>
       is drawn at that number on the scale the page prints            --gate has run, or when no value is printed)
       beside it. M25's sibling, from the same file
  M27  the read over a build (E63): a card that has not        FAIL   (E63; WARN when it is inside the plot's box
       parked sits on a ledger page's INK - the data, the               clear of the ink - E65 puts a card in the
       labels, the citation - drawing or finished. M25's                plot's own empty room; INFO until probe.py
       sibling                                                          <build> --gate has run)
  M28  text on text (R26-53): two of a page's OWN labels       FAIL   (E28; WARN when two of the VALUE row are
       - values, ticks, pills, series names, brackets and               closer than half a figure, the air
       figures - sit on each other at a probed instant.                 lpFitValues fits it with; INFO until
       M25's sibling, from the same file                                probe.py <build> --gate has run)
  M29  the cut's sound (E44 s2a / R26-5): no TRANSIENT cue   FAIL   (E44 s2a; only when a cue lands inside
       lands inside 0:05-0:12 unless a page lands with it              the window - the beds are exempt)
       (its arrival or its chart's landing, within 1.5s)
  M30  a returning character MOUNTS (E44 s2b / R26-6): a    FAIL   (E44 s2b; only when a scene DECLARES a
       `cut` into a scene whose first species is a character           character - world.character | a `character`
       an earlier scene already showed                                 species | an evidence species of `character`)
  J01  savor beats keep their picture (card up, badge lit) JUDGE

    python gate_motion_density.py <build-dir> [--timeline NAME.timeline.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys as _sys
from pathlib import Path as _P
_sys.path.insert(0, str(_P(__file__).resolve().parent))
import ledger_page as LPG  # noqa: E402  (P49 T6: a datum's in-frame box is the page's plot)
import statistics as st
import sys
from dataclasses import dataclass
from pathlib import Path

STILL_FAIL_S = 12.0        # doc 29 s8.19 MAX_BARE, s9.25 ceiling
FROZEN_MAX_S = 0.5         # E49: the longest run of bit-identical rendered frames [DERIVED: HyperFrames' "the final 1-2 seconds"; halved]
FRAME_HASHES_NAME = "frame-hashes.json"   # written by measure_frozen_frames.py beside the timeline
FRAME_LAYERS = ("page", "docks", "captions")   # R26-13: the shell's ?layers= switch - mirrored in measure_frozen_frames.LAYERS
MORPH_S = 2.0              # P47 T3 [DERIVED: the template MORPH.S] - a morph page's prop becomes the chart over this, then the build
MORPH_STEP_S = 0.5         # a morph is continuous motion: one event every half second of its window
MORPH_INVARIANTS_NAME = "morph-invariants.json"   # written by measure_morph.py beside the timeline
SRC_M17 = "P47 T3 / the brief B4 [DERIVED: :390-396]: a morph reads as one thing changing when its centroid moves <= 6 % of W, its dominant axis turns <= 15 deg and its bounding area keeps >= 60 % - measured in the player by measure_morph.py"
STOP_FLIGHT_S = 0.45       # P47 T1 [DERIVED: stopaction.mjs STOP.FLIGHT_S] - a thrown card lands this long after its enter
STOP_LAND_S = 0.32         # P47 T1 [DERIVED: STOP.ANTIC_S + STOP.DROP_S] - a landed card hits its spot this long after its enter
STOP_ON1_PX_S = 250        # P47 T1 [DERIVED: CADENCE.ON1_PX_S, the brief :185-193] - faster than this steps on 1s
STOP_THROW_DX, STOP_THROW_DY, CARD_W_DEFAULT = 240, 160, 864   # the template's throw offsets and the .dock width, mirrored
SRC_M20 = "P47 T1 (the brief :185-193, the cadence rule): a throw steps on 1s above 250 px/s, on 2s below - reported, not scored, until HG2 tunes it"
DEPLOY_AVG_S, DEPLOY_MAX_S = 8.0, 12.0   # E50 [OPERATOR 2026-09-07]: a chart's deployed life - 6-8 s from its LAST data mark on average, 12 s at most
DEPLOY_MIN_S = 6.0   # ... and 6 s is E50's own LOWER bound, enforced ONLY on a page that ARRIVES BUILT.
                     # E50's ceiling exists because a chart HELD static killed ep1. The floor exists for the opposite
                     # fault: a completed chart whipped away before it can be taken in (the tariff short's hook page
                     # scored 0.03 s). But the two only bite on the same page if the build is treated as dead time,
                     # and it is not - operator, 2026-09-08: "the builds are the art, it's the suspense and the proof
                     # that the work is real, and building/drawing the chart is what allows the user to follow,
                     # instead of seeing a full, busy chart and not knowing where to look."
                     # So: IF YOU WATCHED IT DRAW, YOU DO NOT NEED LONG TO READ IT - the pen led your eye in and the
                     # build WAS the reading. IF IT ARRIVED COMPLETE, you have to find your own way around it, and
                     # that is what the 6 s buys. A page that builds is exempt.
PUSH_TIE_BEFORE_S, PUSH_TIE_AFTER_S = 1.5, 0.3   # [DERIVED] a push is TIED when a landing on its scene falls inside (at - 1.5 s, at + 0.3 s)
SRC_M22 = "E51 (operator 2026-09-07): a push-in is only used tied to something - pushing into a newly landed badge or data series; a zoom on a thing that just sits there is filler"
SRC_M23 = "P48 (operator 2026-09-07): chart-to-chart transitions are a first-rate feature - a chart changes STATE and never cuts; E45/E50: never over a build, never inside the last 0.5 s of a page's life"
TRANSITION_EDGE_S = 0.5    # a transition that ends inside the last half second of its page is a cut wearing a verb [DERIVED: E50, P48 Patterns]
TRANSITION_DATA_KINDS = ("recast", "rescale", "extend", "morph")   # the verbs that change the chart's DATA state: their end is a data mark and a landing; a park moves the chart and changes nothing
SRC_M21 = "E50 (operator 2026-09-07): a chart's deployed life is 6-8 s from its last data mark on average, 12 s at most - then it un-draws or becomes the next thing"
SRC_M18 = ("E49 / P47 T5: nothing ever goes truly still - a run of identical rendered frames over 0.5 s is a freeze "
           "(measure_frozen_frames.py); R26-13: read PER LAYER too - the page, the docks and the captions each on "
           "their own (frame-hashes.<layer>.json, the shell's ?layers= switch), because a caption boiling over a "
           "frozen page passes the whole-frame hash (Tokyo v2: 1036 distinct frames of 1066, M18 PASS, the pages "
           "still). The whole-frame verdict is still reported.")
LAYOUT_PROBE_NAME = "layout-probe.json"   # written by probe.py --gate beside the timeline; M25 reads it and never opens a browser
SRC_M25 = ("E45 s1 (the compiler's `place`: a card parks in the page's quiet space, never over the plot, the title, the source line "
           "or the caption's anchor) / E52 (the page CITES: the citation rides the park) / E60 - the three defects of 2026-09-10, "
           "refused from the page's own DOM (probe.py --gate)")
# A SETTLED card only. What a card RESTS on is composition and the compiler's contract; what it flies over on its way in is
# choreography (the Tokyo Fed card crosses the whole page mid-throw, approved 2026-09-09). probe.py marks `rest` and `state`.
LAYOUT_SETTLED = ("parked", "reading")
DATA_OVER_SHARE = 0.02     # a settled card may cover this much of itself with the chart's DATA - the bars, the drawn series,
                           # the numbers - and no more (defect i: the fab card over the bars). A card in a chart's EMPTY
                           # corner is clean (the Tokyo cup, approved): the data is measured where it is drawn, not as a plot box.
INK_OVER_SHARE = 0.08      # ... and this much of a LINE of the page's ink - the citation, a note, the title, an axis label, a
                           # pill (defect ii: the source line left full-size under the cards). Below it is the glyph box's own
                           # padding brushing a card's edge, measured at 1-3 % where nothing touches on screen.
CAPTION_TOUCH_SHARE = 0.01  # any real intersection with the caption strip while a caption is showing (defect iii: the record's
                           # paper grew into the strip); a hundredth of the strip is the box's rounding, not the paper.
TYPE_FLOOR_CSS = 11.0      # doc 49 s49.1 reads the floor at 12 CSS px on a 390 px phone (34 px on the 1080 stage); 11 is the
                           # refusal line under it. Exempt: the citation (the operator's design pass 2026-09-07 - "cited sources
                           # should take up minimal space, not maximal" - put .lp-src.compact at 26 px = 9.4 CSS px on purpose)
                           # and any run a park has demoted (probe.py marks it `pk`): a parked chart is a thumbnail beside the
                           # card that holds the stage, not reading matter.
TYPE_FLOOR_EXEMPT = ("source",)
SRC_M26 = ("E28 (a chart reads right at a glance: a bar's height IS its value) / E53 (the scale and the value are printed at "
           "every instant) / R26-40 - the printed number and the DRAWN height, read against the scale the page itself prints, "
           "from the page's own DOM (probe.py --gate). R26-39 was exactly this mismatch: 303 px of bar at \"0.00 %\"")
SRC_M27 = ("E63 (operator 2026-09-11, on the Tokyo cut at 0:09.5-0:10.5: \"docking over the plate while it's drawing is not a good "
           "standard practice ... as a rule we should probably use better handling now that we can manipulate scale/depth/placement "
           "easier\"; widened the same evening, on the read that came back over the finished chart: \"im confused, because you just "
           "left the dock over the chart now too. something went backwards\"): a card that has not parked yet may not sit on a "
           "ledger page's INK, drawing or finished - the READ moves (the compiler's `read_moved` / `read_deferred`), never the "
           "word. The page's own INK is what the row scores (the data, the labels, the citation - M25's boxes): since E65 the "
           "placer may put a card in the plot's own empty ROOM on purpose, so the plot box is the WARN tier and the ink is the "
           "FAIL. A PARKED card is E45's contract and M25's row. Read from the page's own DOM (probe.py --gate)")
BUILD_OVER_SHARE = 0.05    # of the smaller box: the compiler's own line (READ_OVER_PLOT_SHARE), kept so the placer and the
                           # gate name the same number. Since E65 the row no longer SCORES it: a card in the plot's own empty
                           # room is what the placer now chooses, so the plot BOX is the WARN tier and the INK is the FAIL.
SRC_M28 = ("R26-53 (the operator, 2026-09-11: \"why are we now crashing text?\") - the Tokyo Meta page's four values "
           "\"$665 $633 $604 $577\" touched each other and the callout's pill on bar 4 covered bar 3's label, on the "
           "approved build and on every side build before f67c5ed, and no row saw it: M25 reads cards over ink, M26 the "
           "value's height, and the probe's `overlaps` carried card-vs-ink and pill-vs-rail only. E28 (a chart reads "
           "right at a glance): no two of a page's OWN labels may sit on each other, and the row that fits them "
           "(lpFitValues / lpPillBand) leaves half a figure of air between them. From the page's own DOM (probe.py --gate)")
LABEL_AIR_EM = 0.28        # HALF A FIGURE at the page's own value size - the air lpFitValues fits the value row with
                           # (max(12 px, 0.5 x the figure width) each side) and lpPillBand clears the pill of it by. Under
                           # it two numbers read as one crowded string even when their boxes have not met: measured at 6 px
                           # on the approved Tokyo build, where the law asks 17.
LABEL_TOUCH_EM = 0.14      # a QUARTER of a figure: under this the eye reads two labels as one string - the operator's word for the
                           # Meta page's 6 px (2 CSS px on a phone) was "crashing text"; the frame's own arithmetic (a met box) is
                           # not the only crash. FAIL under a quarter, WARN under half (LABEL_AIR_EM).
LABEL_AIR_ROLES = ("val", "pill")   # the VALUE ROW and its callout pill - the register the fit's air law binds. A tick under a
                           # negative bar's value, or two capsules on the page's rail, keep their own layer's gutter.
# THE BAND. A printed number and a drawn height never agree to the pixel, and two things account for the gap:
VALUE_TOL = 0.04           # (a) ROUNDING. A pill prints lpFmt's two decimals and a tick label lpTick's, and the height is
                           # measured off a rendered box - so a few hundredths of the TOP TICK is arithmetic, not a lie.
                           # Measured on the Tokyo short as built: the worst disagreement over its probed instants is far
                           # inside this (reported by the row itself, which prints the worst it saw).
VALUE_OVERSHOOT = 0.05     # (b) THE BURST'S OVERSHOOT (LPX.BT_OVER, mirrored here as the gate mirrors _breakthrough_run_s's
                           # dials): during the shoot a breaking bar is drawn this much PAST its own number on purpose (E60)
                           # and settles back. It is a share of the bar's own height, so the band is the sum: 4 % of the top
                           # tick plus 5 % of the number printed. Anything outside that is the page lying about its data.
LAYOUT_INK = ("page.source", "page.note", "page.title", "page.sub", "pill")   # a LINE of ink; `page.plot` / `page.chart` are
                           # rectangles the probe reports for context - a card beside a parked chart sits inside the plot box
                           # by design, and only the DATA in it is protected
SAFE_WARN_SHARE = 0.10     # a settled card with more than a tenth of itself inside a Shorts chrome band (top 12 %, bottom 20 %,
                           # outer 5 %) is at risk of the overlay; a sliver at the edge is not.
STILL_WARN_S = 8.0         # s9.25 working target
SHORT_PULSE_MAX_S = 2.5    # doc 49 s49.6: a short needs a visual event every 1.2-2.5 s. THE GATE IS THE PULSE (operator, 2026-09-05):
                           # a floor on motion, never a ceiling - 'we could have much more animation and it would be fine'
SRC_M16 = "doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling"
EVIDENCE_GAP_MAX_S = 45.0  # doc 29: evidence every 15-45s
PLATE_SECONDS = 12.0       # s9.13: runtime / 12s distinct plates
PLATE_HOLD_MAX_S = 20.0    # s9.13: past this a hold is READ for liveness (E69, 2026-09-12) - it was "unless two docks over it"
CAP_WORDS = (4, 6)         # build_caption_pages: MAX_WORDS 6, 4-6 target
CAP_PAGES_PER_MIN_MIN = 20.0
OPENING_S = 60.0           # E21: the opening minute
WINDOW_S = 60.0

# LEDGER PAGE beats (doc 29 s9.26, E22 addendum 6 / s9.28 C5, D1, D2; the template's
# `const LP = { ROLL: 0.7, SAVOR: 0.8, FIELD: 2.4, PUNCH: 0.5, INK: 2.0, BUILD: 3.0 }`,
# operator 2026-09-03): ROLL the cream unrolls, SAVOR the half-savor, FIELD the charcoal
# fills to the deckle (E22 addendum 7: no outline - the deckle is the edge), PUNCH the
# punch-in, BUILD the chart lands, and the FOCUS action fires at the build's end. Each
# boundary is a visual event from the scene start; the start itself is an evidence
# entry; the hold after the focus is still (C5) and needs a dock, plate life, or stage
# captions past 12s. Keep in step with the template's LP constants.
LP_ROLL_S, LP_SAVOR_S, LP_FIELD_S, LP_PUNCH_S, LP_BUILD_S = 0.7, 0.8, 2.4, 0.5, 3.0
PAGE_BEAT_OFFSETS = (0.0, LP_ROLL_S, LP_ROLL_S + LP_SAVOR_S,
                     LP_ROLL_S + LP_SAVOR_S + LP_FIELD_S,
                     LP_ROLL_S + LP_SAVOR_S + LP_FIELD_S + LP_PUNCH_S,
                     LP_ROLL_S + LP_SAVOR_S + LP_FIELD_S + LP_PUNCH_S + LP_BUILD_S)
# = (0.0, 0.7, 1.5, 3.9, 4.4, 7.4): roll-out, savor start, field start, punch, build start, build end + focus
PAGE_BUILD_END_S = PAGE_BEAT_OFFSETS[-1]   # a LEDGER PAGE's chart LANDS here (7.4s after the page enters): M11's annotation clock for a page - the
                                           # operator's ruling (2026-09-04) is no highlight over the charcoal build, so the species fires after the build, never with the roll-out
SHORT_FULL_MINUTES = 3                     # M07 ranks whole minutes; with fewer full minutes than this (a short) there is no distribution to rank in -
                                           # the row reports both rates as INFO (P41, 2026-09-05) instead of failing the opening against a 22s tail
ARRIVES_BUILT = ("spiral", "snap", "built", "throw", "drop", "camera")   # the enters whose page is DRAWN on its first frame: one beat, no roll-out (P53 T1 named the set the landing and the beats had each spelled out)
LP_SPIRAL_IN_S = 1.6                       # a page declared enter=spiral unwinds from its point over this (template LP_RETRACT.IN): one beat, then the species
LP_RETRACT_S = (1.0, 1.0)                  # every page LEAVES by the retract unless exit=cut: the colours go down the drain, then the charcoal (template LP_RETRACT.COLOURS / CHARCOAL)
SRC_M31 = ("R26-66 / P53 T2, measured with measure_stage_gaps.py: a transition that TAKES the world (a suck, a melt) "
           "left the stage with no world on it for 3.1 s while the narration was already on the next sentence - 8.9% of "
           "a 69 s short. The DIP is the one transition licensed to empty the stage (a dip is a world change); everything "
           "else hands off, and the page that follows an inked arrival (enter=axes / built) measures 0.")
SRC_M15 = "E40 #5 (operator, 2026-09-05): no spotlight on a spiral out - no species window overlaps a page's retract"
LP_BADGE0_S, LP_BADGE_STEP_S = 0.4, 0.9   # page badges spring in after the build: build end + 0.4 + 0.9k (template LP.BADGE0 / BADGE_STEP)
CAP_ARRIVE_FADE = "fade_up"    # P52 T10: the page's arrival kind (page.cap_arrive / timeline.caption_arrive); absent = the pop
CAP_STAGGER_S = 0.055          # kinetics/stagger.mjs FADE_UP.STAGGER_S - keep in step with the module, as the LP constants above are kept in step with the template


def _stagger_starts(onsets: list[float | None], origin: float, stagger: float = CAP_STAGGER_S) -> list[float]:
    """When each word of a `fade_up` page actually ARRIVES - the mirror of kinetics/stagger.mjs staggerStarts.

    M08 counts a stage page's words as visual events on their spoken onsets. Under the fade-up envelope a word
    whose onset crowds the word before it does not arrive then: it arrives one stagger later, because the
    envelope will not let two words share a start. So the gate reads the ENVELOPE, not the raw onset - otherwise
    it credits motion at an instant where nothing has moved yet. The law: the onset when it beats the stagger
    (E21's word clock survives), else the previous start plus the stagger; never before the page."""
    out: list[float] = []
    for i, o in enumerate(onsets):
        prev = out[i - 1] if i else None
        t = float(o) if o is not None else (origin if prev is None else prev + stagger)
        if prev is None:
            t = max(t, origin)
        else:
            t = max(t, prev + stagger)
        out.append(t)
    return out
DOCK_SOURCE_TIMELINE = "timeline"            # scenes[].docks enter/exit/badge_at - the player's own clock
DOCK_SOURCE_FILE = "evidence-dock.json"      # fallback only: a timeline that carries no docks at all

# TARGETED SPECIES events (doc 29 s9.27 MOTION MENU, "Gate treatment" column;
# P35 T7). A scene's `species` rows are {"kind", "at", "dur", "target"}; the
# table says which edges of each are visual events: "at" = one event at the
# firing, "end" = one at at+dur. Camera punch: "one event at the punch". Scribble
# callout: "event at draw". Focus zoom: "event at departure and arrival".
# Feathered spotlight: "events per glide" (each glide is a row). Pull-back
# reveal: "events across the pull" (departure and arrival). Beat-freeze exit:
# "events at hit and cut". Radial reveal: "scene event". Push hand-off: "event".
# "stepping" = plate life, "events while stepping": the stop-motion cadence is
# quantized to 10 fps, so one event every 1/10 s across its duration - plate
# life fills a bare plate. Squiggle marks "count as a caption event in stage
# mode only": the stage page under them already counts (M08), so they add no
# event of their own for now.
SPECIES_EVENTS = {"punch": ("at",), "callout": ("at",), "focus_zoom": ("at", "end"),
                  "spotlight": ("at", "end"), "squiggle": (), "pull_back": ("at", "end"),
                  "plate_life": "stepping", "beat_freeze": ("at", "end"),
                  "radial": ("at",), "push": ("at",),
                  "steam": "continuous", "trace": ("at", "end"), "ticker": "stepping",   # STILL LIFE (2026-09-05)
                  "life": "continuous",   # a DECLARED self-animating world (a rendered outro): the claim is the author's, verified by eye, credited here
                  "build_to": ("at", "end"), "bracket": ("at", "end"), "retitle": ("at", "end"), "relight": ("at",),   # P47 T2: the page performs on a word
                  "undraw": ("at", "end"), "figure": ("at", "end"), "note": ("at", "end"), "spread": ("at", "end"),
                  "peel": ("at", "end"),
                  "chart_to": ("at", "end")}   # P48: the chart leaving and the next one arriving are both motion, and the arrival is a landing (E51)   # P48 T4: the piece leaving is motion at both ends, and its landing is a push's tie (E51)   # E50 (P47 T6): the line unwinds; the figure writes; a note is handwriting
SPECIES_EVENTS["flow"] = ("at", "swap.at")   # P50 T4: the diagram DRAWS on its word (the box, the chips, the arrows - one
                                            # build) and ONE node SWAPS on a later one. "swap.at" is a DOTTED path: the edge
                                            # names a field inside a field, which _species_events walks.
SPECIES_EVENTS["span"] = ("at",)            # ... and a span shades in on its word; it holds after that, so it has no end event
# P50 T5: the VECTOR MAP's three. A light LANDS on its word (the country's fill rises: an event) and then holds -
# like a span, it has no end event, because a light that leaves is the next composition's business. An arc draws on
# its word AND is CUT on a later one ("crossed", a field edge like the chip's cross_at). A stamp lands once.
SPECIES_EVENTS["light"] = ("at",)
SPECIES_EVENTS["arc"] = ("at", "crossed")
SPECIES_EVENTS["stamp"] = ("at",)
SPECIES_EVENTS["cross"] = ("at",)   # P50 T6: the census's X marks strike on their word - the named cells are struck, dimmed
                                    # and their share written, all on one clock; like a span or a light it holds after that,
                                    # so it has no end event (what happens next is the park, which is its own row).
SPECIES_EVENTS["chip"] = ("at", "cross_at")   # P50 T2: a chip LANDS on its word (an event) and is CROSSED on a later one (another).
                                              # "cross_at" is neither an edge of the window nor its end: it names the row's own field,
                                              # and _species_events credits any such name at the instant that field holds.
# P52 T6: THE NEWSREEL BAND is a STANDING element with a LIFE. It arrives once (one event, on its word) and then
# CRAWLS - continuous motion for exactly as long as it stands, which is its `hold` plus the retreat when the author
# gave it one, else its whole window. It is credited like a `life` (one event per LIFE_CONTINUOUS_S), and never like
# `stepping`: a crawl is not an event per frame - reading it that way would let one band carry a whole scene's
# density and hide a still frame behind it.
NEWSREEL_CRAWL = "crawl"
NEWSREEL_EXIT_S = 0.38   # [DERIVED: species/newsreel.mjs NEWSREEL.BEATS.EXIT_FOR] the retreat is still motion
SPECIES_EVENTS["newsreel"] = NEWSREEL_CRAWL
# P52 T7 / T8, the last three Bravos species. Each one's events are the WORDS it lands on, and nothing else:
# the count array's icons arrive one per word ("arrivals" - the edge is computed from the row's own `count` and
# `step`, the way the chip's `cross_at` is read off its own field), the agenda's rows are revealed one per word
# ("rows" - each row's own `at`), and the dashed ring draws once on its word and then HOLDS at its idle, like a
# span or a light, so it has no end event. No idle is ever an event (E49); M18 is the idle's own check.
SPECIES_EVENTS["count_array"] = ("at", "arrivals")
SPECIES_EVENTS["agenda"] = ("at", "rows")
SPECIES_EVENTS["ring"] = ("at",)
COUNT_ARRAY_STEP = AGENDA_STEP = 0.34   # the default word pitch both kinds arrive on when the row names no `step`
                                        # - the same number the compiler holds (build_scene_timeline_f.COUNT_ARRAY_STEP /
                                        # AGENDA_STEP) and the modules' own dial (COUNT.STEP / AGENDA.STEP): 178 WPM.
LIFE_CONTINUOUS_S = 1.0    # a continuous life (steam) is one event per second of its window - it never lets the frame go still
# VIDEO DOCK (ruling E44 / backlog R26-7, 2026-09-06): a dock whose asset is a clip is moving pictures on
# the card, so the frame is never still while it is up - credited continuously, exactly like a "life"
# species. An IMAGE dock is a still card and keeps its enter/exit events only (today's behaviour).
DOCK_KIND_VIDEO = "video"
VIDEO_DOCK_STEP_S = LIFE_CONTINUOUS_S
PLATE_LIFE_STEP_S = 0.1    # s9.27 plate life: quantize t to 10 fps; each step is an event
# WORLD-CHANGE TRANSITIONS (ruling E47 #4, operator 2026-09-06): "a dip is a transition, not a still:
# M01/M10/M16 count its 14 frames as the boundary event, not as stillness; a blur-zoom's magnification
# is motion." Both straddle the boundary named by the scene's own `exit`, so the half before it is the
# OUTGOING scene's tail - crediting the window's start, the boundary and its end is what stops that
# tail reading as a hold. Lengths in seconds; a scene may override with `exit_s`.
DIP_S = 0.47          # [DERIVED: the reference, 14 frames at 30 fps, measured on all 35 of its dips, 2026-09-06 -
                      #  docs/research/motion/wealth_logic_transitions_measured.csv; doc 46 s46.5]
BLURZOOM_S = 0.27     # [DERIVED: the MEDIAN duration_frames of the reference's 28 blur-zooms, 8 frames at 30 fps]
TRANSITION_S = {"dip": DIP_S, "blurzoom": BLURZOOM_S}
# s9.27 precedence / s9.28 C3: punch, focus zoom, pull-back and Ken Burns are
# mutually exclusive per window. M09 mirrors the builder's validate_species so a
# hand-edited timeline is caught too.
CAMERA_MOVES = ("punch", "focus_zoom", "pull_back")

# OPENING-MINUTE gates (ruling E24 / doc 29 s9.29 - the analyst's drop-off review the
# operator verified against analytics) and the chart-hold rule (ruling E25 / s9.30).
OPENING_STILL_MAX_S = 6.0        # E24 / doc 29 s9.29: 4-6s in the first 30-60s - the opening's own stillness ceiling
PARADOX_S = 8.0                  # E24 / doc 29 s9.29: the first chart enters only after the 8s paradox is paid
FIRST_CHART_MAX_S = 20.0         # E24 / doc 29 s9.29: ... and no later than 0:20 (LONG FORM)
FIRST_CHART_SHORT = (0.0, 10.0)  # E44 (2026-09-06): on a SHORT the first ledger page rolls out ON THE HOOK line -
                                 # the chart IS the mechanism and lands by 0:10, so there is no paradox to pay first.
                                 # A short is the tool's own read (_is_short: 9:16, or runtime < SHORT_FULL_MINUTES *
                                 # WINDOW_S = 180s, mirrored from gate_opening_structure.SHORT_MAX_S = 180.0)
CHART_SPECIES = ("chart", "data")  # E24 / doc 29 s9.29: the evidence species that count as "the first chart"
ANNOTATED_KINDS = ("spotlight", "callout", "punch", "focus_zoom")  # E24 / doc 29 s9.29: the chart's divergence is pointed at
ANNOTATE_TOL_S = 1.5             # E24 / doc 29 s9.29: the targeted species fires with the enter, not later
CUE_TOL_S = 1.5                  # E24 / doc 29 s9.29: a sound cue lands with the enter (absent = WARN)
CHART_HOLD_MAX_S = 10.0          # E25 / doc 29 s9.30: the chart is the proof, not the homework - hold ceiling anywhere
OPENING_CHART_HOLD_MAX_S = 6.0   # E25 / doc 29 s9.30: ... and inside the opening minute
SRC_M10 = "E24 / doc 29 s9.29: stillness inside the opening minute - 4-6s in the first 30-60s"
SRC_M11 = "E24 / doc 29 s9.29 (long form) + E44 (short): the first chart enters 0:08-0:20, or 0:00-0:10 on a short, annotated on its divergence, with a sound cue"
SRC_M12 = "E25 / doc 29 s9.30: the chart is the proof, not the homework"
# THE CUT'S SOUND, and the DROP WINDOW (ruling E44 s2a / backlog R26-5, 2026-09-06, on the Tokyo read
# ANALYTICS-2026-09-06.md n = 8: the step at 0:11): "the press / flash cue at a cut is not a hook device; at 0:09 it
# is the last thing a viewer hears before leaving ... no transient cue lands inside 0:05-0:12 unless a page lands
# with it." A TRANSIENT is a hit with an attack - a press pack, a page accent, a landing; a BED is continuous
# sub-threshold music and is exempt, because a bed marks no instant. The row is reported only when a cue actually
# lands inside the window (the M19-M24 shape), so a build with nothing there carries no row.
DROP_WINDOW_S = (5.0, 12.0)      # E44 s2a: the window a transient may not mark on its own
BED_FADE_S = 1.0                 # a cue that fades in over a second or more is a bed, not a transient (the hook bed fades 1.5s)
BED_SLOT_TOKENS = ("bed",)       # ... and a cue whose slot says so is a bed whatever its fade
SRC_M29 = ("E44 s2a / R26-5 (operator 2026-09-06: \"the camera flash sound maybe shouldn't be as aggressive\"): the "
           "press / flash cue at a cut is not a hook device - at 0:09 it is the last thing a viewer hears before "
           "leaving, so no TRANSIENT cue lands inside 0:05-0:12 unless a PAGE lands with it (the page's own arrival "
           "or its chart's landing, within 1.5 s). The beds are exempt: a bed marks no instant")
# A RETURNING CHARACTER MOUNTS (ruling E44 s2b / backlog R26-6, 2026-09-06): "the character cuts on to the scene
# instead of smoothly entering like he did in scene 1" - a character already introduced re-enters the way he first
# entered (a dissolve on a word, doc 29 s9.15), never on a cut. A character is DECLARED, never guessed from an
# asset's name: the timeline carries no cast, and Tokyo's host rides `clip-a-counter-tab-v2`, a name no pattern
# could read. The three declarations M30 accepts: CHARACTER_KEYS on a scene's world, a species row of kind
# `character`, and an evidence entry whose species is `character`.
CHARACTER_SPECIES = ("character",)          # the species kind (a row) / the evidence species (an asset) of a cast member
CHARACTER_KEYS = ("character", "cast")      # the field a world or a species row names its cast member in
SRC_M30 = ("E44 s2b / R26-6 (operator 2026-09-06: \"the character cuts on to the scene instead of smoothly entering "
           "like he did in scene 1\"): a returning character MOUNTS the way he first mounted - a dissolve on a word "
           "(doc 29 s9.15) - so a scene whose entry transition is a `cut` and whose FIRST species is a character an "
           "earlier scene already showed is a defect, gated by the mount rule and not by hand")
DOCK_BUILD_S = 1.5               # 47 s2 G-a: a card's entrance - the wipe / fly-in - is a build the eye must be free to read
BADGE_SETTLE_S = 0.6             # ... and each badge reveal is one too, settling ~0.6s after badge_at
CAMERA_MOVE_S = 1.2              # a camera species with no declared dur is credited this long
SRC_M24 = "P49 T6 (operator 2026-09-08: 'our engine ... doesn't know what it's seeing until it's rendered back'): a pointing species whose target is out of the camera's frame when it fires points at nothing - checked from the track before render"
POINTING_KINDS = ("callout", "spotlight", "squiggle", "punch", "focus_zoom", "beat_freeze", "radial", "push", "figure", "spread", "bracket", "chip",
                  "flow", "span",
                  "count_array", "agenda", "ring",   # P52 T7 / T8: all three point at a DECLARED target (a region or a point for the field and the block, a datum for the ring), so M24 reads them like any other pointing species

                  "light", "arc", "stamp")   # P50 T5: the map's three point at a PLACE - a country or a map point, which is not a stage box, so _target_box skips them and M24 credits them without a frustum test   # P50 T4: a flow points at the region it draws itself inside; a span names data and carries no target dict, so M24 skips it   # the species that point at a declared target
ATTN_SCALE, ATTN_IN, ATTN_OUT = 1.06, 0.5, 0.6            # P49 T4: kinetics/camera.mjs ATTN, mirrored [DERIVED: Bravos #68]
STOP_FLIGHT_S, STOP_ANTIC_S, STOP_DROP_S = 0.45, 0.18, 0.14   # the stop-action clock (kinetics/stopaction.mjs STOP), mirrored: the contact frame of a throw / a landing
BT_HOLD_S, BT_RUN_S, BT_SETTLE_S, BT_STEP_S = 0.5, 0.6, 0.3, 0.06   # E60 the breakthrough's clock (the template's LPX.BT_*), mirrored: the run past the build


def _breakthrough_run_s(page: dict) -> float:
    """E60: seconds a breakthrough page's chart runs PAST its ordinary build (build_s or LP_BUILD_S): the hold at the
    comparator's level, then the burst + settle, or the stack's steps. 0 for a page with no overflow."""
    axes = (page or {}).get("axes") or {}
    mode = axes.get("overflow")
    if mode not in ("burst", "stack", "break"):
        return 0.0
    if mode == "stack":
        vals = [float(v) for v in (page.get("values") or []) if isinstance(v, (int, float))]
        dom = axes.get("domain") or [0, 0]
        try:
            hi = float(dom[1])
        except (TypeError, ValueError, IndexError):
            hi = 0.0
        honest = [v for v in vals if v <= hi]
        comp = max(honest) if honest else hi
        vmax = max(vals) if vals else 0.0
        import math
        steps = (math.ceil(vmax / comp - 1e-9) + 1) if comp > 0 else 1
        return BT_HOLD_S + BT_STEP_S * steps
    return BT_HOLD_S + BT_RUN_S + BT_SETTLE_S


def _transition_land(scene: dict, x: dict) -> float:
    """The instant a chart_to's target chart has LANDED: the transition's end, plus - when the target state is a breakthrough
    page (E60) - its own build and run (the state builds AFTER the standing chart has left)."""
    end = float(x.get("at", 0.0)) + float(x.get("dur", 0.0))
    idx = x.get("state")
    states = ((scene.get("world") or {}).get("page_states") or [])
    if isinstance(idx, int) and 1 <= idx <= len(states):
        target = states[idx - 1] or {}
        run = _breakthrough_run_s(target)
        if run > 0:
            return end + float(target.get("build_s") or LP_BUILD_S) + run
    return end
SRC_M14 = "47 s2 G-a / doc 07 Pillar 4 (saccadic suppression): a camera move may not overlap an evidence build - the eye is blind during the move"


@dataclass(frozen=True)
class Gate:
    id: str
    level: str
    message: str
    src: str


def _timeline_path(build: Path, timeline_name: str | None) -> Path:
    tl_path = build / timeline_name if timeline_name else next(iter(sorted(build.glob("*.timeline.json"))), None)
    if not tl_path or not tl_path.exists():
        raise SystemExit(f"no *.timeline.json in {build}")
    return tl_path


def _load(build: Path, timeline_name: str | None) -> tuple[dict, list[dict], dict]:
    BUILD_DIR[:] = [Path(build)]   # the rows that read a measurement file beside the timeline (M25, M31)
    tl_path = _timeline_path(build, timeline_name)
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    docks_p = build / "evidence-dock.json"
    docks = json.loads(docks_p.read_text(encoding="utf-8")) if docks_p.exists() else []
    mp_p = build / "motion-plan.json"
    mp = json.loads(mp_p.read_text(encoding="utf-8")) if mp_p.exists() else {"cues": []}
    return tl, docks, mp


def _dock_span(d: dict) -> tuple[float, float] | None:
    a = d.get("at", d.get("start", d.get("enter")))
    z = d.get("end", d.get("exit", d.get("until")))
    return (float(a), float(z)) if isinstance(a, (int, float)) and isinstance(z, (int, float)) else None


def _is_page(scene: dict) -> bool:
    return scene.get("world", {}).get("kind") == "ledger"


def _plate_id(scene: dict) -> str | None:
    """A plate's asset id; a ledger page is its own plate (s9.28 C5: a page holds like a plate)."""
    w = scene.get("world", {})
    return w.get("asset_id") or (f"ledger:{scene.get('scene_id', '?')}" if _is_page(scene) else None)


def _dock_clock(scenes: list[dict], docks: list[dict]) -> tuple[list[tuple[float, float]], list[float], str]:
    """(dock spans, badge reveal times, source). The TIMELINE's own docks win;
    `evidence-dock.json` is read only when no scene carries a dock (P35 T0)."""
    tl_docks = [d for s in scenes for d in s.get("docks", [])]
    if tl_docks:
        spans = [x for x in (_dock_span(d) for d in tl_docks) if x]
        badges = [float(b) for d in tl_docks for b in d.get("badge_at", [])]
        return spans, badges, DOCK_SOURCE_TIMELINE
    return [x for x in (_dock_span(d) for d in docks) if x], [], DOCK_SOURCE_FILE


def _page_events(scenes: list[dict]) -> tuple[list[float], list[float]]:
    """(visual events, evidence entries) contributed by ledger pages (s9.28 C5, D1, D2).
    A beat past the page's own scene end never happened - a short page credits only
    the beats it had time to play (never motion inside the scene after it)."""
    starts, beats = [], []
    for s in scenes:
        if not _is_page(s):
            continue
        a, z = float(s["span"][0]), float(s["span"][1])
        starts.append(a)
        page = (s.get("world", {}).get("page") or {})
        spiral = page.get("enter") == "spiral"
        if page.get("enter") == "morph":   # P47 T3: the morph is continuous motion, then the build starts and lands
            ms = float(page.get("morph_s") or MORPH_S)
            offs = [k * MORPH_STEP_S for k in range(int(ms // MORPH_STEP_S) + 1)] + [ms, ms + LP_BUILD_S]
            beats += [round(a + off, 2) for off in offs if a + off < z]
            continue
        # WHAT THE PAGE ACTUALLY PLAYS. A page that arrives BUILT plays no roll-out, no field and no build: its
        # arrival is its one beat (crediting the six roll-out beats to it made a still page read as motion, which
        # E69's M05 now decides on). `axes` plays the build alone: the page is there, the data draws. (P53 T1)
        enter = page.get("enter")
        offs = ((0.0, LP_SPIRAL_IN_S) if spiral else (0.0,) if enter in ARRIVES_BUILT
                else (0.0, LP_BUILD_S) if enter == "axes" else PAGE_BEAT_OFFSETS)
        beats += [round(a + off, 2) for off in offs if a + off < z]
        # the retract: the colours start winding in, then the charcoal - two beats at the page's end (none on exit=cut)
        if (s.get("world", {}).get("page") or {}).get("exit") != "cut":
            beats += [round(z - sum(LP_RETRACT_S), 2), round(z - LP_RETRACT_S[1], 2)]
        # inline badges ride their line's draw-complete (already a build event); only rail pills are extra reveals
        n_badges = sum(1 for b in ((s.get("world", {}).get("page") or {}).get("badges") or []) if not b.get("inline"))
        beats += [round(a + PAGE_BEAT_OFFSETS[-1] + LP_BADGE0_S + LP_BADGE_STEP_S * k, 2) for k in range(n_badges)
                  if a + PAGE_BEAT_OFFSETS[-1] + LP_BADGE0_S + LP_BADGE_STEP_S * k < z]
    return beats, starts


def _species_events(scenes: list[dict]) -> list[float]:
    """Visual events contributed by targeted species rows, per SPECIES_EVENTS (s9.27)."""
    out: list[float] = []
    for s in scenes:
        a, z = (float(s["span"][0]), float(s["span"][1])) if s.get("span") else (None, None)
        for sp in s.get("species", []):
            edges = SPECIES_EVENTS.get(sp.get("kind"), ())
            at, dur = float(sp.get("at", 0.0)), float(sp.get("dur", 0.0))
            # a species that runs past its scene stops with the scene: no event is credited beyond span end
            inside = a is not None and a <= at <= z
            # a species authored BEFORE its scene starts is a state the page arrives in (a retitle carried onto a returning page,
            # P47 T2), not an event in another scene's window: nothing before the span is credited
            keep = (lambda t: t <= z) if inside else ((lambda t: t >= a) if a is not None and at < a else (lambda t: True))
            if edges == NEWSREEL_CRAWL:   # P52 T6: the crawl stands for its `hold` (the LIFE) plus its retreat, else for the window
                hold = sp.get("hold")
                win = min(dur, float(hold) + NEWSREEL_EXIT_S) if isinstance(hold, (int, float)) and not isinstance(hold, bool) and hold > 0 else dur
                n_ev = int(win // LIFE_CONTINUOUS_S)
                out += [round(at + k * LIFE_CONTINUOUS_S, 2) for k in range(n_ev + 1) if keep(at + k * LIFE_CONTINUOUS_S)]
                continue
            if edges == "continuous":
                n_ev = int(dur // LIFE_CONTINUOUS_S)
                out += [round(at + k * LIFE_CONTINUOUS_S, 2) for k in range(n_ev + 1) if keep(at + k * LIFE_CONTINUOUS_S)]
                continue
            if edges == "stepping":
                steps = int(round(dur / PLATE_LIFE_STEP_S))
                out += [round(at + k * PLATE_LIFE_STEP_S, 2) for k in range(steps + 1) if keep(at + k * PLATE_LIFE_STEP_S)]
                continue
            if "at" in edges and keep(at):
                out.append(round(at, 2))
            if "end" in edges and keep(at + dur):
                out.append(round(at + dur, 2))
            for edge in edges:   # P50 T2: an edge that names a FIELD (the chip's cross_at) fires at that field's own instant
                if edge in ("at", "end"):
                    continue
                if edge == "arrivals":   # P52 T7: the count array's icons land one per word - each arrival its own event
                    n, gap = int(sp.get("count") or 0), float(sp.get("step") or COUNT_ARRAY_STEP)
                    if gap > 0:
                        out += [round(at + i * gap, 2) for i in range(1, n) if keep(at + i * gap)]
                    continue
                if edge == "rows":       # P52 T8: ... and the agenda's rows are revealed one per word, each on its own `at`
                    for i, row in enumerate(sp.get("rows") or []):
                        w = row.get("at") if isinstance(row, dict) else None
                        w = float(w) if isinstance(w, (int, float)) and not isinstance(w, bool) else at + i * AGENDA_STEP
                        if i and keep(w):
                            out.append(round(w, 2))
                    continue
                v = sp   # P50 T4: ... and a DOTTED edge names a field inside a field (the flow's swap.at), walked here
                for _part in edge.split("."):
                    v = v.get(_part) if isinstance(v, dict) else None
                if isinstance(v, (int, float)) and not isinstance(v, bool) and keep(float(v)):
                    out.append(round(float(v), 2))
    return out


def _video_dock_events(scenes: list[dict], docks: list[dict]) -> list[float]:
    """Visual events contributed by VIDEO docks (E44 / R26-7).

    A dock declaring ``kind: "video"`` carries a clip on the card: while it is on screen the frame
    is moving, so it is credited one event per second of its live span - the same treatment a
    "continuous" species gets (LIFE_CONTINUOUS_S), and the reason M10's opening stillness and
    M16's pulse no longer read a dock hold as a hold. A dock with no kind is a still card and
    adds nothing here. The timeline's own docks win; evidence-dock.json is the fallback (P35 T0)."""
    tl_docks = [d for s in scenes for d in s.get("docks", [])]
    out: list[float] = []
    for d in (tl_docks or docks):
        if d.get("kind") != DOCK_KIND_VIDEO:
            continue
        span = _dock_span(d)
        if not span:
            continue
        a, z = span
        n = int(max(0.0, z - a) // VIDEO_DOCK_STEP_S)
        out += [round(a + k * VIDEO_DOCK_STEP_S, 2) for k in range(n + 1)]
    return out


def _transition_events(scenes: list[dict]) -> list[float]:
    """Visual events contributed by a DIP or a BLURZOOM world change (E47 #4).

    `exit` names the transition INTO the scene it sits on (the player's law), so the window
    straddles that scene's start: half in the outgoing scene's tail, the switch on the boundary,
    half in the incoming scene. All three instants are events - the dip's black is the boundary
    EVENT, never stillness, and the blur-zoom's magnification is motion. The first scene has no
    boundary before it, so its exit credits nothing.

    Only TRANSITION_S's two straddle a boundary, and only they credit a window. The transitions that
    run FORWARD from the cut - the suck, and the melt (P52 T9) - credit nothing here on purpose: each
    is ONE world change (the melt's four phases are one event, not four), and the boundary it happens
    on is already an event, counted where every scene start is (`_collect_events`). Adding a name to
    TRANSITION_S credits it THREE, which is a claim about a transition that straddles nothing."""
    out: list[float] = []
    for i, s in enumerate(scenes):
        if i == 0 or not s.get("span"):
            continue
        name = str(s.get("exit") or "").split(":")[0]
        if name not in TRANSITION_S:
            continue
        try:
            dur = float(s.get("exit_s") or TRANSITION_S[name])
        except (TypeError, ValueError):
            dur = TRANSITION_S[name]
        b, half = float(s["span"][0]), dur / 2
        out += [round(b - half, 3), round(b, 3), round(b + half, 3)]
    return out


def _camera_clashes(scenes: list[dict]) -> list[tuple[str, str]]:
    """(scene_id, why) for every scene that stacks two camera moves, or one over
    a Ken Burns drift (scale > 0) - s9.27 precedence / s9.28 C3."""
    out = []
    for s in scenes:
        moves = [sp.get("kind") for sp in s.get("species", []) if sp.get("kind") in CAMERA_MOVES]
        scale = float(s.get("world", {}).get("ken_burns", {}).get("scale", 0) or 0)
        sid = s.get("scene_id", "?")
        keyed = bool(_camera_key_segments(s))   # P49 T6: an authored key segment is a camera move
        landings = (s.get("camera") or {}).get("attention") == "landings"   # P49 T4: the landing IS the move
        if len(moves) > 1:
            out.append((sid, " + ".join(moves)))
        elif moves and keyed:
            out.append((sid, f"camera keys + {moves[0]}"))
        elif moves and landings:
            out.append((sid, f"attention landings + {moves[0]}"))
        elif moves and scale > 0:
            out.append((sid, f"{moves[0]} over Ken Burns scale {scale:g}"))
        elif keyed and scale > 0:
            out.append((sid, f"camera keys over Ken Burns scale {scale:g}"))
    return out


def _attention_moves(s: dict) -> list[tuple[float, float, str]]:
    """P49 T4: (contact, contact + ATTN_IN, dock slide) for every arriving dock a landings-attention scene pulls toward."""
    if (s.get("camera") or {}).get("attention") != "landings":
        return []
    out: list[tuple[float, float, str]] = []
    for d in s.get("docks", []):
        if not d.get("place") or d.get("arrive") not in ("throw", "land"):
            continue
        tc = float(d.get("enter", 0.0)) + (STOP_FLIGHT_S if d.get("arrive") == "throw" else STOP_ANTIC_S + STOP_DROP_S)
        out.append((tc, tc + ATTN_IN, str(d.get("slide", d.get("asset", "?")))))
    return out


SNAP_S_MIRROR = 0.45   # the player's SNAP_S (the snap's and the camera arrival's clock), mirrored


def _arrival_moves(s: dict) -> list[tuple[float, float, str]]:
    """P49 T5: (start, start + SNAP_S, the card's slide) for a page that arrives by the eye going to its card."""
    pg = (s.get("world") or {}).get("page") or {}
    if pg.get("enter") != "camera" or not pg.get("snap_from") or not s.get("span"):
        return []
    a = float(s["span"][0])
    return [(a, a + SNAP_S_MIRROR, str(pg["snap_from"]))]


def _camera_key_segments(s: dict) -> list[tuple[float, float, str]]:
    """(start, end, why) for every segment of a scene's authored camera keys that MOVES the camera - zoom, look or at
    changes between two keys (a `hold` ease is a step at the arriving key, credited as a move of CAMERA_MOVE_S there)."""
    keys = ((s.get("camera") or {}).get("keys") or [])
    out: list[tuple[float, float, str]] = []
    prev = None
    for k in keys:
        if not isinstance(k, dict) or not isinstance(k.get("t"), (int, float)):
            continue
        cur = (float(k["t"]), float(k.get("zoom", 1) or 1), k.get("look"), k.get("at") if k.get("at") is not None else k.get("look"), k.get("ease", "cubic"))
        if prev is not None and (cur[1] != prev[1] or cur[2] != prev[2] or cur[3] != prev[3]):
            if cur[4] == "hold":
                out.append((cur[0], cur[0] + CAMERA_MOVE_S, f"camera key step at {cur[0]:.1f}s"))
            else:
                out.append((prev[0], cur[0], f"camera keys {prev[0]:.1f}-{cur[0]:.1f}s"))
        prev = cur
    return out


def _build_windows(scenes: list[dict], docks: list[dict]) -> list[tuple[str, float, float]]:
    """(slide, start, end) for every evidence BUILD: the card's entrance plus its badge reveals.
    The timeline's own docks win; the evidence-dock.json shape is the fallback (P35 T0)."""
    tl_docks = [d for s in scenes for d in s.get("docks", [])]
    out = []
    for d in (tl_docks or docks):
        span = _dock_span(d)
        if not span:
            continue
        a = span[0]
        z = max(a + DOCK_BUILD_S, *[float(b) + BADGE_SETTLE_S for b in d.get("badge_at", [])] or [a])
        out.append((str(d.get("slide", d.get("asset", "?"))), a, min(z, span[1])))
    return out


def _build_clashes(scenes: list[dict], docks: list[dict]) -> list[tuple[str, str]]:
    """(scene_id, why) for every camera move whose window intersects an evidence build window
    anywhere on the clock - M14 (47 s2 G-a). M09 is about stacking moves; this is about moving
    while the viewer is supposed to be reading a build."""
    builds = _build_windows(scenes, docks)
    out = []
    for s in scenes:
        moves = [(float(sp.get("at", 0.0)), float(sp.get("at", 0.0)) + float(sp.get("dur", CAMERA_MOVE_S) or CAMERA_MOVE_S), sp["kind"])
                 for sp in s.get("species", []) if sp.get("kind") in CAMERA_MOVES]
        moves += [(a, z, "camera keys") for a, z, _why in _camera_key_segments(s)]   # P49 T6: the track's own moves
        for at, end, kind in moves:
            for slide, a, z in builds:
                if at < z and a < end:
                    out.append((s.get("scene_id", "?"), f"{kind} {at:.1f}-{end:.1f}s over {slide} build {a:.1f}-{z:.1f}s"))
        for at, end, own in _attention_moves(s) + _arrival_moves(s):   # P49 T4/T5: the pull toward a landing, and the eye going to the card, are TIED to that dock (E51) - they clash only with another build
            for slide, a, z in builds:
                if slide != own and at < z and a < end:
                    out.append((s.get("scene_id", "?"), f"attention pull {at:.1f}-{end:.1f}s (toward {own}) over {slide} build {a:.1f}-{z:.1f}s"))
    return out


# ---- P49 T6: the camera's state from the track, the way the player evaluates it (kinetics/camera.mjs camKeyState) ----

def _cam_ease(name: str, k: float) -> float:
    k = max(0.0, min(1.0, k))
    if name == "inout":
        return 2 * k * k if k < 0.5 else 1 - ((-2 * k + 2) ** 2) / 2
    if name == "linear":
        return k
    if name == "hold":
        return 1.0 if k >= 1 else 0.0
    return 1 - (1 - k) ** 3   # cubic


def _cam_point(v, sw: float, sh: float, plot: dict | None) -> tuple[float, float] | None:
    """A key's look/at as stage px: [x, y] fractions, or a declared target's centre (a datum: the plot's centre)."""
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return (float(v[0]) * sw, float(v[1]) * sh)
    if isinstance(v, dict):
        b = _target_box(v, sw, sh, plot)
        return (b["x"] + b["w"] / 2, b["y"] + b["h"] / 2) if b else None
    return None


def _target_box(tg: dict, sw: float, sh: float, plot: dict | None) -> dict | None:
    """A declared target as a world box in stage px: point (w = h = 0), region, datum (the page's plot box); span: none."""
    kind = tg.get("kind") if isinstance(tg, dict) else None
    if kind == "point":
        return {"x": float(tg["x"]) * sw, "y": float(tg["y"]) * sh, "w": 0.0, "h": 0.0}
    if kind == "region":
        return {"x": float(tg["x0"]) * sw, "y": float(tg["y0"]) * sh, "w": (float(tg["x1"]) - float(tg["x0"])) * sw, "h": (float(tg["y1"]) - float(tg["y0"])) * sh}
    if kind == "datum" and plot:
        return dict(plot)
    return None


def camera_state_at(s: dict, t: float, sw: float, sh: float, plot: dict | None) -> dict:
    """{s, look, at} at t from the scene's authored keys - identity before the first, lerp by the arriving key's ease,
    hold after the last; species windows are the player's and are not evaluated here (their target is their centre)."""
    ident = {"s": 1.0, "look": (sw / 2, sh / 2), "at": (sw / 2, sh / 2)}
    keys = [k for k in ((s.get("camera") or {}).get("keys") or []) if isinstance(k, dict) and isinstance(k.get("t"), (int, float))]
    if not keys:
        st = ident
        if (s.get("camera") or {}).get("attention") == "landings":   # P49 T4: the pull toward a landing, as the player draws it
            for d in s.get("docks", []):
                if not d.get("place") or d.get("arrive") not in ("throw", "land"):
                    continue
                tc = float(d.get("enter", 0.0)) + (STOP_FLIGHT_S if d.get("arrive") == "throw" else STOP_ANTIC_S + STOP_DROP_S)
                exit_t = float(d.get("exit", tc)); out_t = exit_t - ATTN_OUT
                if not (tc <= t <= exit_t):
                    continue
                a = _cam_ease("inout", (t - tc) / ATTN_IN) * (1 - _cam_ease("inout", (t - out_t) / ATTN_OUT))
                c = (float(d["place"]["x"]) + float(d["place"]["w"]) / 2, float(d["place"]["y"]) + float(d["place"]["h"]) / 2)
                st = {"s": 1 + (ATTN_SCALE - 1) * a, "look": c, "at": c}
        return st
    K = []
    for k in keys:
        look = _cam_point(k.get("look"), sw, sh, plot) or (sw / 2, sh / 2)
        at = (_cam_point(k.get("at"), sw, sh, plot) or look) if k.get("at") is not None else look
        K.append({"t": float(k["t"]), "s": float(k.get("zoom", 1) or 1), "look": look, "at": at, "ease": k.get("ease", "cubic")})
    if t < K[0]["t"]:
        return ident
    i = 1
    while i < len(K) and t > K[i]["t"]:
        i += 1
    if i >= len(K):
        L = K[-1]; return {"s": L["s"], "look": L["look"], "at": L["at"]}
    a, b = K[i - 1], K[i]
    u = _cam_ease(b["ease"], (t - a["t"]) / max(1e-6, b["t"] - a["t"]))
    lerp = lambda p, q: p + (q - p) * u
    return {"s": lerp(a["s"], b["s"]), "look": (lerp(a["look"][0], b["look"][0]), lerp(a["look"][1], b["look"][1])), "at": (lerp(a["at"][0], b["at"][0]), lerp(a["at"][1], b["at"][1]))}


def camera_frustum(st: dict, sw: float, sh: float) -> dict:
    (lx, ly), (ax, ay), s = st["look"], st["at"], st["s"]
    return {"x0": lx + (0 - ax) / s, "y0": ly + (0 - ay) / s, "x1": lx + (sw - ax) / s, "y1": ly + (sh - ay) / s}


def _visible_share(fr: dict, box: dict) -> float:
    x0, y0 = max(fr["x0"], box["x"]), max(fr["y0"], box["y"]); x1, y1 = min(fr["x1"], box["x"] + box["w"]), min(fr["y1"], box["y"] + box["h"])
    area = max(0.0, box["w"]) * max(0.0, box["h"])
    if area > 0:
        return max(0.0, x1 - x0) * max(0.0, y1 - y0) / area
    return 1.0 if (x0 <= x1 and y0 <= y1) else 0.0


def _in_frame_faults(scenes: list[dict], aspect: str) -> list[str]:
    """P49 T6: every pointing species whose declared target is not (fully) in the camera's frame at its `at`."""
    sw, sh = (1080.0, 1920.0) if aspect == "9:16" else (1920.0, 1080.0)
    out: list[str] = []
    for s in scenes:
        cam = s.get("camera") or {}
        if not cam.get("keys") and cam.get("attention") != "landings":
            continue   # identity everywhere: nothing can leave the frame
        page = (s.get("world") or {}).get("page")
        plot = None
        if isinstance(page, dict):
            try:
                plot = LPG.page_boxes(page, aspect).get("plot")
            except Exception:   # a page the box model cannot place: the datum proxy is unavailable, the check skips it
                plot = None
        for sp in s.get("species", []):
            if sp.get("kind") not in POINTING_KINDS or not isinstance(sp.get("target"), dict):
                continue
            at = float(sp.get("at", 0.0))
            box = _target_box(sp["target"], sw, sh, plot)
            if box is None:
                continue
            st = camera_state_at(s, at, sw, sh, plot)
            share = _visible_share(camera_frustum(st, sw, sh), box)
            if share < 0.999:
                out.append(f"{s.get('scene_id', '?')} {sp['kind']} at {_mm(at)}: its {sp['target'].get('kind')} target is {100 * share:.0f}% in frame (zoom {st['s']:.2f})")
    return out


def _in_frame_gate(scenes: list[dict], aspect: str) -> Gate | None:
    """M24: no row unless a scene authors camera keys (the identity camera frames everything)."""
    if not any(((s.get("camera") or {}).get("keys")) or (s.get("camera") or {}).get("attention") == "landings" for s in scenes):
        return None
    faults = _in_frame_faults(scenes, aspect)
    if faults:
        return Gate("M24", "FAIL", "; ".join(faults[:8]) + (" ..." if len(faults) > 8 else "") + " - a species points at what the eye cannot see: move the key, or the species", SRC_M24)
    n = sum(1 for s in scenes for sp in s.get("species", []) if sp.get("kind") in POINTING_KINDS and isinstance(sp.get("target"), dict)
            and (((s.get("camera") or {}).get("keys")) or (s.get("camera") or {}).get("attention") == "landings"))
    return Gate("M24", "PASS", f"{n} pointing species on moving-camera scenes, every target in frame when it fires", SRC_M24)


def _build_gate(clashes: list[tuple[str, str]]) -> Gate:
    if clashes:
        msg = (f"{len(clashes)} camera moves land on an evidence build: " + ", ".join(f"{sid} ({why})" for sid, why in clashes[:12])
               + (" ..." if len(clashes) > 12 else ""))
    else:
        msg = "no camera move (punch | focus_zoom | pull_back) overlaps a card entrance or a badge reveal"
    return Gate("M14", "FAIL" if clashes else "PASS", msg, SRC_M14)


def _collect_events(tl: dict, mp: dict, spans: list, badges: list, page_beats: list, stage_rows: list,
                    species_events: list = (), video_dock_events: list = ()) -> set[float]:
    events: set[float] = set()
    events.update(video_dock_events)
    events.update(_transition_events(tl.get("scenes", [])))   # E47 #4: a dip / blur-zoom IS the boundary event
    for s in tl.get("scenes", []):
        events.add(float(s["span"][0])); events.add(float(s["span"][1]))
    for a, z in spans:
        events.add(a); events.add(z)
    events.update(badges); events.update(page_beats); events.update(species_events)
    for c in mp.get("cues", []):
        if c.get("kind") != "plate":
            events.add(float(c["in"])); events.add(float(c.get("out", c["in"])))
    for r in stage_rows:
        events.add(float(r["t"]))
    return events


def _per_minute(runtime: float, ev: list[float], entries: list[float]) -> list[tuple[float, float, float]]:
    dens = []
    for m in range(int(runtime // WINDOW_S) + 1):
        lo, hi = m * WINDOW_S, min((m + 1) * WINDOW_S, runtime)
        if hi - lo < 20:
            continue
        n = sum(1 for t in ev if lo <= t < hi) / ((hi - lo) / 60)
        nd = sum(1 for a in entries if lo <= a < hi) / ((hi - lo) / 60)
        dens.append((lo, n, nd))
    return dens


BUILD_DIR: list[Path] = []   # set by _load / main: the build being read, for the rows that consult a measurement file (M25, M31)


def analyse(tl: dict, docks: list[dict], mp: dict) -> dict:
    runtime = float(tl.get("runtime_s") or max(s["span"][1] for s in tl["scenes"]))
    scenes = tl.get("scenes", [])
    pages = tl.get("caption_pages", [])
    spans, badges, dock_source = _dock_clock(scenes, docks)
    page_beats, page_starts = _page_events(scenes)
    # stage-mode captions count as events when the timeline declares them
    tl_rows = tl.get("rows", tl.get("timeline", []))
    # P34 T5: the build declares the mode per caption page (cap_mode at the page's first word);
    # a stage page is a visual event at its start (s9.25 #1: "captions in stage mode")
    stage_rows = [r for r in tl_rows if isinstance(r, dict) and r.get("cap_mode") == "stage"]
    stage_rows += [{"t": pg["s"]} for pg in pages if isinstance(pg, dict) and pg.get("cap_mode") == "stage"]
    # a stage page's WORDS each pop in on their own spoken time (the golden set; E21: captions ARE the motion) - every word with a
    # clock is a visual event, not only the page's start (a sentence-sized page would otherwise read as a hold, 2026-09-05).
    # P52 T10: on a page that declares `fade_up` the arrival is ONE staggered envelope, so the event is the word's
    # envelope start (>= its onset), read by the module's own law - the gate credits motion when it happens, not when it was said.
    tl_arrive = tl.get("caption_arrive")
    for pg in pages:
        if not isinstance(pg, dict) or pg.get("cap_mode") != "stage":
            continue
        toks = [tok for tok in (pg.get("t") or []) if isinstance(tok, dict)]
        if (pg.get("cap_arrive") or tl_arrive) == CAP_ARRIVE_FADE:
            onsets = [float(tok["s"]) if tok.get("s") is not None else None for tok in toks]
            stage_rows += [{"t": t} for t in _stagger_starts(onsets, float(pg["s"]))]
        else:
            stage_rows += [{"t": float(tok["s"])} for tok in toks if tok.get("s") is not None]
    # P35 T7: targeted species fire as tabled in SPECIES_EVENTS (s9.27 gate column)
    events = _collect_events(tl, mp, spans, badges, page_beats, stage_rows, _species_events(scenes) + _arrival_events(scenes),   # P47 T1: a throw / a landing is motion
                             _video_dock_events(scenes, docks))   # E44: a live video dock is continuous motion
    ev = sorted(t for t in events if 0.0 <= t <= runtime)
    if not ev or ev[0] > 0:
        ev.insert(0, 0.0)
    if ev[-1] < runtime:
        ev.append(runtime)
    still = sorted(((a, b - a) for a, b in zip(ev, ev[1:])), key=lambda x: -x[1])
    # evidence entry gaps, whole runtime: a dock entering or a page starting (D2)
    entries = sorted([a for a, _ in spans] + page_starts)
    pts = [0.0] + entries + [runtime]
    ev_gaps = sorted(((a, b - a) for a, b in zip(pts, pts[1:])), key=lambda x: -x[1])
    # plates: a page is its own plate and holds like one (C5)
    plate_ids = [_plate_id(s) for s in scenes]
    holds = [(float(s["span"][0]), float(s["span"][1]) - float(s["span"][0]), _plate_id(s)) for s in scenes]
    # E69 (the operator, 2026-09-12: "the twenty second hold ceiling is a relic from when we coudln't live in the
    # frame"): every hold past the ceiling is reported WITH the longest gap between visual events inside it, and
    # M05 decides on that gap. The dock count rides along because two docks are one way to live in a frame, not
    # the way.
    over_hold = []
    for a, d, pid in holds:
        if d > PLATE_HOLD_MAX_S:
            n = sum(1 for x, z in spans if x < a + d and z > a)
            edges = [a] + [t for t in ev if a < t < a + d] + [a + d]
            gap, at = max(((b - x, x) for x, b in zip(edges, edges[1:])), default=(d, a))
            over_hold.append((a, d, pid, n, round(gap, 2), round(at, 2)))
    wc = [len(p.get("t", [])) for p in pages]
    return {"runtime": runtime, "events": ev, "still": still, "ev_gaps": ev_gaps, "plates": plate_ids,
            "over_hold": over_hold, "wc": wc, "pages": pages, "dens": _per_minute(runtime, ev, entries),
            "spans": spans, "dock_source": dock_source, "n_pages": len(page_starts),
            "camera_clashes": _camera_clashes(scenes),
            "cap_arrive": next((pg["cap_arrive"] for pg in pages if isinstance(pg, dict) and pg.get("cap_arrive")), tl_arrive),
            "has_cap_mode": bool(stage_rows) or any(isinstance(r, dict) and "cap_mode" in r for r in tl_rows)
                            or any(isinstance(pg, dict) and "cap_mode" in pg for pg in pages)}


def run(tl: dict, docks: list[dict], mp: dict, frames: list[dict] | str | None = None, morph: dict | str | None = None,
        layout: dict | str | None = None, frame_layers: dict[str, list[dict] | str] | None = None) -> tuple[list[Gate], dict]:
    A = analyse(tl, docks, mp)
    R = A["runtime"]
    mm = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
    g: list[Gate] = []
    add = lambda i, lvl, m, s: g.append(Gate(i, lvl, m, s))
    still_fail = [(a, d) for a, d in A["still"] if d > STILL_FAIL_S]
    still_warn = [(a, d) for a, d in A["still"] if d > STILL_WARN_S]
    tot = sum(d for _, d in still_fail)
    add("M01", "FAIL" if still_fail else "PASS",
        (f"{len(still_fail)} stretches > {STILL_FAIL_S:.0f}s with no visual event beyond Ken Burns/anchor captions "
         f"({tot:.0f}s = {100 * tot / R:.0f}% of runtime); worst {still_fail[0][1]:.1f}s at {mm(still_fail[0][0])}") if still_fail
        else f"longest still stretch {A['still'][0][1]:.1f}s at {mm(A['still'][0][0])}",
        "doc 29 s8.19 / s9.25 stillness ceiling")
    add("M02", "WARN" if still_warn else "PASS", f"{len(still_warn)} stretches > {STILL_WARN_S:.0f}s (working target)", "doc 29 s9.25")
    gap = A["ev_gaps"][0] if A["ev_gaps"] else (0.0, 0.0)
    add("M03", "FAIL" if gap[1] > EVIDENCE_GAP_MAX_S else "PASS",
        f"longest wait for evidence to enter: {gap[1]:.0f}s from {mm(gap[0])}" + (" (no docks at all)" if not A["spans"] else ""),
        "doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)")
    n_plates = len(set(p for p in A["plates"] if p))
    want = int(R / PLATE_SECONDS)
    add("M04", "WARN" if n_plates < want else "PASS", f"{n_plates} distinct plates; target runtime/12s = {want}", "doc 29 s9.13 plate density")
    oh = A["over_hold"]
    live_max = SHORT_PULSE_MAX_S if _is_short(tl, R) else STILL_WARN_S
    dead = sorted((h for h in oh if h[4] > live_max), key=lambda h: -h[4])
    add("M05", "FAIL" if dead else "PASS",
        (f"{len(dead)} plate(s) held > {PLATE_HOLD_MAX_S:.0f}s with the frame DEAD: worst {dead[0][2]} "
         f"{dead[0][1]:.0f}s at {mm(dead[0][0])} - {dead[0][4]:.1f}s with no visual event at {mm(dead[0][5])}, "
         f"over the {live_max:.1f}s liveness ceiling. Live in the frame (a species, a page beat, a card, "
         f"captions in stage mode) or cut it") if dead
        else (f"{len(oh)} plate(s) over the {PLATE_HOLD_MAX_S:.0f}s hold, every one LIVE across it "
              f"(worst gap {max(h[4] for h in oh):.1f}s of {live_max:.1f}s allowed)" if oh
              else f"no plate over the {PLATE_HOLD_MAX_S:.0f}s hold"),
        "doc 29 s9.13 as amended by E69 (2026-09-12): the hold is legal while the FRAME LIVES - the ceiling's "
        "two-dock condition was written when a world was a still and only a card could move on it")
    if A["wc"]:
        ppm = len(A["pages"]) / (R / 60)
        mean_w = st.mean(A["wc"])
        ok = CAP_WORDS[0] <= mean_w <= CAP_WORDS[1] and ppm >= CAP_PAGES_PER_MIN_MIN
        add("M06", "PASS" if ok else "WARN", f"{len(A['pages'])} caption pages = {ppm:.0f}/min, {mean_w:.1f} words/page", "s9.15 r7 / build_caption_pages 4-6 words")
    else:
        add("M06", "INFO", "no caption pages in the build - M06 not run (no silent skip: build caption-pages.json first)", "s9.15 r7")
    if dens := A["dens"]:
        opening = [d for d in dens if d[0] < OPENING_S][0]
        full = sum(1 for d in dens if d[0] + WINDOW_S <= R + 1e-6)
        if full < SHORT_FULL_MINUTES:
            # a SHORT (P41): one full minute and a tail is not a distribution - the opening's rate is stated beside
            # the tail's and the whole's for the judge, never ranked against a single scaled-up tail bucket
            tail = [d for d in dens if d[0] >= OPENING_S]
            whole = (len(A["events"]) - 2) / (R / 60)   # the 0 and runtime sentinels are not events
            add("M07", "INFO", f"short: {full} full minute(s) in {R:.0f}s - opening {opening[1]:.1f} events/min, {opening[2]:.1f} evidence entries/min"
                + (f"; tail from {mm(tail[0][0])} {tail[0][1]:.1f}/min" if tail else "") + f"; whole runtime {whole:.1f}/min - no minute distribution to rank in (E21 is judged on the whole)",
                "E21: the opening is the densest minute, never the thinnest")
        else:
            ranked = sorted(dens, key=lambda x: x[1])
            rank = [d[0] for d in ranked].index(opening[0]) + 1
            med = st.median(d[1] for d in dens)
            add("M07", "FAIL" if opening[1] < med else "PASS",
                f"opening minute: {opening[1]:.1f} events/min, {opening[2]:.1f} docks/min - rank {rank}/{len(dens)} from the bottom; episode median {med:.1f}/min",
                "E21: the opening is the densest minute, never the thinnest")
    else:
        add("M07", "INFO", f"runtime {R:.0f}s has no full minute to rank - M07 not run (no silent skip)", "E21")
    req = [(a, d) for a, d in A["still"] if d > STILL_WARN_S]
    if A["has_cap_mode"]:
        # ENFORCED (P34 T5): stage pages already count as events, so any stretch still over the
        # ceiling is one the captions did not take - the shot table must author stage rows there
        bare = [(a, d) for a, d in A["still"] if d > STILL_FAIL_S]
        add("M08", "FAIL" if bare else "PASS",
            (f"{len(bare)} still stretches > {STILL_FAIL_S:.0f}s carry no stage-mode caption: "
             + ", ".join(f"{mm(a)}+{d:.0f}s" for a, d in sorted(bare)[:12]) + (" ..." if len(bare) > 12 else "")) if bare
            else "timeline declares cap_mode; every stretch over the ceiling carries stage captions (counted as events above)"
                 + (f"; the words arrive on the {A['cap_arrive']} envelope, each on its own offset (P52 T10)" if A["cap_arrive"] else ""),
            "doc 29 s9.25 caption STAGE mode (E21: captions ARE the motion when nothing else moves)")
    else:
        add("M08", "INFO", f"timeline carries no cap_mode yet - stage captions REQUIRED on {len(req)} stretches: "
            + ", ".join(f"{mm(a)}+{d:.0f}s" for a, d in sorted(req)[:12]) + (" ..." if len(req) > 12 else ""),
            "doc 29 s9.25 caption STAGE mode (player template pending)")
        add("J02", "JUDGE", "captions on the still stretches above are centred, large, per-word explosive - not the lower-third anchor", "doc 29 s9.25 #2")
    g.append(_camera_gate(A["camera_clashes"]))
    g.append(_build_gate(_build_clashes(tl.get("scenes", []), docks)))   # M14 (P37 T1)
    g.append(_retract_gate(tl.get("scenes", [])))                         # M15 (E40 #5)
    g.append(_pulse_gate(tl, A))                                           # M16 (49 s49.6, shorts)
    # E24 / E25: the opening minute and the chart-as-proof rule
    g += [_opening_still_gate(A["still"]), _first_chart_gate(tl, docks, mp), _chart_hold_gate(tl, docks)]
    g.append(_frozen_gate(frames, frame_layers, layer_windows(A)))        # M18 (E49: nothing ever goes truly still; R26-13: per layer)
    if (sg := _drop_window_sound_gate(tl, mp)) is not None:
        g.append(sg)                                                      # M29 (E44 s2a / R26-5: a transient inside 0:05-0:12 needs a page landing)
    if (mo := _mount_gate(tl.get("scenes", []), tl.get("evidence") or {})) is not None:
        g.append(mo)                                                      # M30 (E44 s2b / R26-6: a returning character mounts, it never cuts on)
    g.append(_layout_gate(layout))                                        # M25 (P51 T2: the layout gate, from probe.py's boxes)
    g.append(_values_gate(layout))                                        # M26 (R26-40: the printed value against the drawn height)
    g.append(_over_build_gate(layout, tl.get("scenes", [])))              # M27 (E63/E65: no card reads over a ledger page's ink)
    g.append(_labels_gate(layout))                                        # M28 (R26-53: text on text among the page's own labels)
    if (bt := _build_to_gate(tl.get("scenes", []))) is not None:
        g.append(bt)                                                      # M19 (P47 T2: the build_to holds, INFO)
    if (cg := _cadence_gate(tl.get("scenes", []))) is not None:
        g.append(cg)                                                      # M20 (P47 T1: the cadence rule per arrival, INFO)
    if (dg := _deployed_gate(tl.get("scenes", []))) is not None:
        g.append(dg)                                                      # M21 (E50: the chart's deployed life per page)
    if (pg_ := _push_tie_gate(tl.get("scenes", []))) is not None:
        g.append(pg_)                                                     # M22 (E51: a push is tied to a landing)
    if (tg := _transition_gate(tl.get("scenes", []))) is not None:
        g.append(tg)                                                      # M23 (P48 T6: a chart changes state, never over a build, never at the edge)
    if (ifg := _in_frame_gate(tl.get("scenes", []), str(tl.get("aspect") or "16:9"))) is not None:
        g.append(ifg)                                                     # M24 (P49 T6: the target is in the camera's frame when the species fires)
    if (mg := _morph_gate(tl.get("scenes", []), morph)) is not None:
        g.append(mg)                                                      # M17 (P47 T3: the match-cut invariants per morph page)
    sg = _stage_gap_gate(BUILD_DIR[0] if BUILD_DIR else None)             # M31 (R26-66 / P53 T2: the empty stage, measured)
    if sg is not None:
        g.append(sg)
    add("J01", "JUDGE", "every savor beat holds its picture (card up, badge lit), never a bare plate with a drift", "doc 29 s9.25 #3")
    return g, _stats(A, tot)


def _mm(s: float) -> str:
    return f"{int(s // 60)}:{int(s % 60):02d}"


def _scene_at(scenes: list[dict], t: float) -> dict | None:
    return next((s for s in scenes if float(s["span"][0]) <= t < float(s["span"][1])), None)


def chart_docks(tl: dict, docks: list[dict]) -> tuple[list[dict], bool]:
    """Every CHART dock as {enter, exit, asset, scene}, by enter time, plus whether the
    species was known. The timeline's own docks win (P35 T0); the evidence map's species
    filters to CHART_SPECIES - a timeline with no evidence map treats EVERY dock as a
    chart candidate (E24 M11 says so in its message)."""
    scenes = tl.get("scenes", [])
    evidence = tl.get("evidence") or {}
    known = bool(evidence)
    # a card a later page SNAPS UP FROM (enter=snap=<dock>, the third watch) is that page's own preview, thrown onto the scene
    # before it - the page carries the annotation, so the card is not a first chart entering unannotated (2026-09-08: the
    # tariff hook page's card at 0.8 s read as one)
    snap_cards = {(s.get("world") or {}).get("page", {}).get("snap_from") for s in scenes}
    snap_cards.discard(None)
    tl_docks = [(d, s) for s in scenes for d in s.get("docks", []) if (d.get("slide") or d.get("asset") or d.get("asset_id")) not in snap_cards]
    pairs = tl_docks if tl_docks else [(d, None) for d in docks]
    out = []
    for d, s in pairs:
        span = _dock_span(d)
        if not span:
            continue
        asset = d.get("slide") or d.get("asset") or d.get("asset_id") or "?"
        if known and evidence.get(asset, {}).get("species") not in CHART_SPECIES:
            continue
        out.append({"enter": span[0], "exit": span[1], "asset": asset, "scene": s or _scene_at(scenes, span[0])})
    return sorted(out, key=lambda x: x["enter"]), known


def _cue_near(t: float, tl: dict, mp: dict) -> bool | None:
    """True/False: a non-plate motion-plan cue or a timeline `sound` entry within CUE_TOL_S;
    None when the build carries neither structure (E24 M11: 'no sound structure to check')."""
    if not mp.get("cues") and "sound" not in tl:
        return None
    ats = [float(c["in"]) for c in mp.get("cues", []) if c.get("kind") != "plate"]
    ats += [float(x["at"]) for x in tl.get("sound", []) or []
            if isinstance(x, dict) and isinstance(x.get("at"), (int, float))]
    return any(abs(a - t) <= CUE_TOL_S for a in ats)


def _opening_still_gate(still: list[tuple[float, float]]) -> Gate:
    """M10 (E24): no still stretch over OPENING_STILL_MAX_S begins inside the opening minute."""
    bad = sorted((a, d) for a, d in still if a < OPENING_S and d > OPENING_STILL_MAX_S)
    if bad:
        return Gate("M10", "FAIL", f"{len(bad)} still stretches > {OPENING_STILL_MAX_S:.0f}s begin in the first "
                    f"{OPENING_S:.0f}s: " + ", ".join(f"{_mm(a)}+{d:.0f}s" for a, d in bad), SRC_M10)
    return Gate("M10", "PASS", f"no still stretch > {OPENING_STILL_MAX_S:.0f}s begins in the first {OPENING_S:.0f}s", SRC_M10)



def _page_land_offset(scene: dict) -> float:
    """Seconds from a ledger page's enter to its chart landing: PAGE_BUILD_END_S on a roll-out; on a mount
    (R26-50, 2026-09-11: the mount is the SOAK on the page's own clock - the cream at once, the soak over mount_s, then ink
    -> punch -> build; a mount skips the roll, the savor and the field beat) mount_s + PAGE_BUILD_END_S - ROLL - SAVOR - FIELD
    (the player defaults mount_s to the FIELD beat when the spec carries none)."""
    page = ((scene or {}).get("world") or {}).get("page") or {}
    # a page may draw over its own seconds (page.build_s); the gate's landing must move with the player's, or the two
    # disagree about when the chart is finished and the deployed life is measured against the wrong mark
    extra = max(0.0, float(page.get("build_s") or LP_BUILD_S) - LP_BUILD_S)
    if page.get("enter") == "mount":
        mount_s = float(page.get("mount_s") or LP_FIELD_S)
        return mount_s + PAGE_BUILD_END_S - LP_ROLL_S - LP_SAVOR_S - LP_FIELD_S + extra   # R26-50: the soak on the page's clock, then ink
    if page.get("enter") == "morph":   # P47 T3: the morph replaces the roll, the savor, the soak and the punch; the build starts as it ends
        return float(page.get("morph_s") or MORPH_S) + LP_BUILD_S + extra
    if page.get("enter") in ARRIVES_BUILT:   # a returning page, a card become the world (P47 T7; P49 T5 by the eye), or a page that mounts with its chart already drawn: arrives built
        return 0.0
    if page.get("enter") == "axes":   # P53 T1: the page is there on frame 0 and the DATA is what builds - the chart lands one build later
        return LP_BUILD_S + extra
    return PAGE_BUILD_END_S + extra

def _first_chart_window(tl: dict) -> tuple[float, float, str]:
    """M11's window and the mode that set it: 0:00-0:10 on a SHORT (E44 - the first ledger page rolls
    out on the hook line, the chart IS the mechanism), 0:08-0:20 on long form (E24 / doc 29 s9.29).
    The short read is _is_short's, the tool's own (9:16 or runtime < 180s)."""
    runtime = float(tl.get("runtime_s") or max((float(s["span"][1]) for s in tl.get("scenes", [])), default=0.0))
    if _is_short(tl, runtime):
        return (*FIRST_CHART_SHORT, "E44 short: the page rolls out on the hook - the chart is the mechanism by 0:10")
    return PARADOX_S, FIRST_CHART_MAX_S, "E24 long form: the 8s paradox is paid before the chart enters"


def _first_chart_gate(tl: dict, docks: list[dict], mp: dict) -> Gate:
    """M11: the first chart (chart/data dock, or ledger page) enters inside its window - 8-20s on long
    form (E24), 0-10s on a short (E44) - carries a targeted species within ANNOTATE_TOL_S, and a sound
    cue within CUE_TOL_S (WARN). The row's message names the window and the ruling it applied."""
    charts, known = chart_docks(tl, docks)
    lo, hi, mode = _first_chart_window(tl)
    win = f"; window {lo:.0f}-{hi:.0f}s ({mode})"
    pages = [{"enter": float(s["span"][0]), "asset": f"ledger:{s.get('scene_id', '?')}", "scene": s}
             for s in tl.get("scenes", []) if _is_page(s)]
    cands = sorted(charts + pages, key=lambda x: x["enter"])
    if not cands:
        return Gate("M11", "FAIL", "no chart enters at all - no chart/data dock and no ledger page in the timeline" + win, SRC_M11)
    t, asset, scene = cands[0]["enter"], cands[0]["asset"], cands[0]["scene"]
    why = []
    if not lo <= t <= hi:
        why.append(f"first chart {asset} enters at {t:.1f}s - outside {lo:.0f}-{hi:.0f}s")
    # a LEDGER PAGE's chart lands at the build's end, not at the roll-out (the page is a bleed until then): its
    # annotation clock is the landing, and the species must fire AFTER it (no highlight over the build - operator, 2026-09-04)
    is_page = bool(scene) and _is_page(scene)
    # a MOUNTED page (E45 s2: "the mount IS the roll-out, and the savor stays") skips beat 1 only: the player's clock is
    # advanced by ROLL - mount_s (template `const tr = ... pg.enter === "mount" ? LP.ROLL - mountS`), so its chart lands at
    # enter + mount_s + (PAGE_BUILD_END_S - ROLL); a rolled-out page lands at enter + PAGE_BUILD_END_S.
    land = t + _page_land_offset(scene) if is_page else t
    hits = [sp for sp in (scene or {}).get("species", [])
            if sp.get("kind") in ANNOTATED_KINDS and (land - 1e-6 <= float(sp.get("at", -1e9)) <= land + ANNOTATE_TOL_S if is_page
                                                     else abs(float(sp.get("at", -1e9)) - t) <= ANNOTATE_TOL_S)]
    # P47 T2: a build_to whose cap LANDS with the build is the annotation itself - the line ends ON the datum and the nib rests
    # there (the page's build is spent on the first cap), which points at the divergence harder than a ring drawn around it
    if is_page:
        hits += [sp for sp in (scene or {}).get("species", []) if sp.get("kind") == "build_to"
                 and abs(float(sp.get("at", -1e9)) + float(sp.get("dur", 0.0)) - land) <= ANNOTATE_TOL_S]
    if not hits:
        why.append("first chart enters full and unannotated - declare a spotlight/callout/punch on its divergence"
                   + (f" within {ANNOTATE_TOL_S:.1f}s AFTER the page's build lands at {land:.1f}s (never over the build)" if is_page else ""))
    cue = _cue_near(t, tl, mp)
    sound = "" if cue else ("; WARN no sound structure to check" if cue is None
                            else f"; WARN no sound cue within {CUE_TOL_S:.1f}s of the enter at {t:.1f}s")
    note = "" if known else " (no evidence species in the timeline - every dock treated as a chart candidate)"
    if why:
        return Gate("M11", "FAIL", "; ".join(why) + sound + note + win, SRC_M11)
    h0 = hits[0]
    how = (f"build_to landing on datum {(h0.get('target') or {}).get('index')} at {float(h0.get('at', 0)) + float(h0.get('dur', 0)):.1f}s (the cap is the annotation: the line ends on the datum)"
           if h0.get("kind") == "build_to" else f"{h0['kind']} at {float(h0['at']):.1f}s")
    msg = f"first chart {asset} enters at {t:.1f}s" + (f", its build lands at {land:.1f}s," if is_page else "") + f" with {how}"
    return Gate("M11", "PASS" if cue else "WARN", msg + sound + note + win, SRC_M11)


def _is_short(tl: dict, runtime: float) -> bool:
    """A short: the build declares 9:16, or it runs under three full minutes (M07's short read)."""
    return str(tl.get("aspect") or "16:9") == "9:16" or runtime < SHORT_FULL_MINUTES * WINDOW_S


def _pulse_gate(tl: dict, A: dict) -> Gate:
    """M16: on a short the gate is the PULSE - the longest gap between visual events is a floor on motion (2.5 s), and
    there is no ceiling. Long-form builds report the pulse as INFO (their law is M01/M02's stillness)."""
    still = A["still"]
    if not still:
        return Gate("M16", "INFO", "no events to measure a pulse from", SRC_M16)
    at, gap = still[0]
    slow = sorted((a, d) for a, d in still if d > SHORT_PULSE_MAX_S)
    msg = f"longest gap between visual events {gap:.1f}s at {_mm(at)}; {len(slow)} gap(s) over {SHORT_PULSE_MAX_S:.1f}s"
    if not _is_short(tl, A["runtime"]):
        return Gate("M16", "INFO", msg + " - a long-form build; the pulse law binds shorts", SRC_M16)
    if slow:
        return Gate("M16", "FAIL", msg + ": " + ", ".join(f"{_mm(a)}+{d:.1f}s" for a, d in slow[:6]) + " - add motion there (a species, a caption pop, plate life); never cut motion to pass", SRC_M16)
    return Gate("M16", "PASS", msg, SRC_M16)


def _stage_gap_gate(build: Path | None) -> Gate | None:
    """M31: the empty stage, read off `<build>/stage-gaps.json` (measure_stage_gaps.py) exactly as M25 reads the
    layout probe - INFO until it is measured, because a gate may not invent a measurement it did not take."""
    if build is None:
        return None
    p = Path(build) / "stage-gaps.json"
    if not p.is_file():
        return Gate("M31", "INFO", "not measured - run measure_stage_gaps.py <build> to read the empty stage", SRC_M31)
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return Gate("M31", "INFO", f"stage-gaps.json unreadable ({exc})", SRC_M31)
    rows = [r for r in doc.get("boundaries", []) if not r.get("licensed") and float(r.get("gap_s") or 0) > 0]
    spoken = [r for r in rows if r.get("spoken")]
    share = f"{100 * float(doc.get('empty_share') or 0):.1f}% of the runtime empty"
    # INFO ONLY (2026-09-12): the probe reads the page's DOM boxes and cannot see a transition's own animation or a
    # page's cream roll-out, so "no page ink" is not "no world" - the operator: "I dont think suck and melt get less
    # screen time". A reading, never a verdict.
    if spoken:
        worst = max(spoken, key=lambda r: float(r["gap_s"]))
        return Gate("M31", "INFO",
                    f"{len(spoken)} transition(s) leave the stage empty UNDER A LIVE SENTENCE ({share}); worst "
                    f"{worst['scene']} exit={worst['exit']} {worst['gap_s']:.1f}s at {_mm(float(worst['at']))} over "
                    f"\"{' '.join(worst['spoken'][:6])}...\" - the page that follows takes an inked arrival "
                    f"(enter=axes or built) or the cut lands later", SRC_M31)
    if rows:
        worst = max(rows, key=lambda r: float(r["gap_s"]))
        return Gate("M31", "INFO", f"{len(rows)} silent stretch(es) with no page ink ({share}); worst {worst['scene']} "
                                   f"{worst['gap_s']:.1f}s at {_mm(float(worst['at']))}", SRC_M31)
    return Gate("M31", "PASS", f"no world-taking transition leaves the stage empty ({share})", SRC_M31)


def _retract_gate(scenes: list[dict]) -> Gate:
    """M15 (E40 #5): a targeted species may not run into a page's retract - the vortex is the picture there."""
    bad = []
    for s in scenes:
        if not _is_page(s) or not s.get("span") or (s.get("world", {}).get("page") or {}).get("exit") == "cut":
            continue
        z = float(s["span"][1]); r0 = z - sum(LP_RETRACT_S)
        for sp in s.get("species", []):
            at, dur = float(sp.get("at", 0.0)), float(sp.get("dur", 0.0))
            if at < z and at + dur > r0:
                bad.append(f"{s.get('scene_id', '?')} {sp.get('kind')} {at:.1f}-{at + dur:.1f}s over the retract from {r0:.1f}s")
    if bad:
        return Gate("M15", "FAIL", "; ".join(bad) + " - end the species before the retract, or declare exit=cut", SRC_M15)
    return Gate("M15", "PASS", "no species window overlaps a page's retract", SRC_M15)


def _chart_hold_offences(tl: dict, docks: list[dict]) -> list[str]:
    """E25 M12: a chart dock that straddles a later scene's start, or holds past the ceiling."""
    scenes = tl.get("scenes", [])
    out = []
    for d in chart_docks(tl, docks)[0]:
        enter, exit_, hold = d["enter"], d["exit"], d["exit"] - d["enter"]
        crossed = [s for s in scenes if enter < float(s["span"][0]) < exit_]
        ceiling = OPENING_CHART_HOLD_MAX_S if enter < OPENING_S else CHART_HOLD_MAX_S
        why = []
        if crossed:
            plates = [_plate_id(d["scene"]) or "?"] if d["scene"] else []
            plates += [_plate_id(s) or "?" for s in crossed]
            why.append(f"crosses {len(crossed)} scene boundaries ({' -> '.join(plates)})")
        if hold > ceiling:
            why.append(f"hold {hold:.1f}s > {ceiling:.0f}s" + (" (opening minute)" if enter < OPENING_S else ""))
        if why:
            out.append(f"{d['asset']} {_mm(enter)}-{_mm(exit_)} " + ", ".join(why))
    return out


def _chart_hold_gate(tl: dict, docks: list[dict]) -> Gate:
    bad = _chart_hold_offences(tl, docks)
    if bad:
        return Gate("M12", "FAIL", f"{len(bad)} chart docks held as homework: " + "; ".join(bad[:12])
                    + (" ..." if len(bad) > 12 else "") + " - re-enter the chart spotlit on the new datum rather than hold", SRC_M12)
    return Gate("M12", "PASS", f"no chart dock spans a scene boundary or holds past {CHART_HOLD_MAX_S:.0f}s "
                f"({OPENING_CHART_HOLD_MAX_S:.0f}s in the opening minute)", SRC_M12)


# ---- E44 s2a (R26-5): the cut's sound inside the drop window --------------------------------

def _is_bed(cue: dict) -> bool:
    """A BED is continuous sub-threshold music: its slot says so, it fades in over BED_FADE_S, or it carries the
    envelope it is ducked by. Everything else is a TRANSIENT - a hit with an attack, and an attack marks an instant."""
    if any(tok in str(cue.get("slot") or "").lower() for tok in BED_SLOT_TOKENS):
        return True
    try:
        if float(cue.get("fade_in") or 0.0) >= BED_FADE_S:
            return True
    except (TypeError, ValueError):
        pass
    return bool(cue.get("env"))


def _cues(tl: dict, mp: dict) -> list[dict]:
    """Every sound cue on the EPISODE clock as {at, slot, gain, bed}: the motion plan's non-plate cues and the
    timeline's own `sound` entries - the two structures _cue_near reads for M11, so the rows never disagree about
    what sound a build carries. A project's `page_cues` are RELATIVE to their page (P35 T9) and never here."""
    out: list[dict] = []
    for c in (mp or {}).get("cues", []) or []:
        if not isinstance(c, dict) or c.get("kind") == "plate" or not isinstance(c.get("in"), (int, float)):
            continue
        out.append({"at": float(c["in"]), "slot": str(c.get("slot") or c.get("kind") or "cue"),
                    "gain": c.get("gain"), "bed": _is_bed(c)})
    for x in tl.get("sound", []) or []:
        if not isinstance(x, dict) or not isinstance(x.get("at"), (int, float)):
            continue
        out.append({"at": float(x["at"]), "slot": str(x.get("slot") or "cue"),
                    "gain": x.get("gain"), "bed": _is_bed(x)})
    return sorted(out, key=lambda c: c["at"])


def _page_landings(scenes: list[dict]) -> list[tuple[float, str]]:
    """(instant, what) for every way a LEDGER PAGE lands: its own arrival (the scene's start - where it mounts,
    rolls out or spirals in) and its chart's landing (_page_land_offset, the build end the player draws to).
    E44 s2a's "unless a page lands with it" is either of the two."""
    out: list[tuple[float, str]] = []
    for s in scenes:
        if not _is_page(s) or not s.get("span"):
            continue
        a = float(s["span"][0])
        sid = s.get("scene_id", "?")
        out += [(a, f"{sid} page arrives"), (round(a + _page_land_offset(s), 2), f"{sid} chart lands")]
    return out


def _drop_window_transients(tl: dict, mp: dict) -> tuple[list[str], list[str]]:
    """(unpaired, paired): every TRANSIENT cue inside DROP_WINDOW_S, split by whether a page lands with it -
    within CUE_TOL_S, the tolerance M11 already gives the first chart's own cue."""
    lo, hi = DROP_WINDOW_S
    lands = _page_landings(tl.get("scenes", []))
    unpaired, paired = [], []
    for c in _cues(tl, mp):
        if c["bed"] or not (lo <= c["at"] <= hi):
            continue
        near = sorted((abs(t - c["at"]), t, what) for t, what in lands)
        gain = f" gain {c['gain']}" if isinstance(c["gain"], (int, float)) else ""
        head = f"{c['slot']} at {c['at']:.2f}s{gain}"
        if near and near[0][0] <= CUE_TOL_S:
            paired.append(f"{head} with {near[0][2]} at {near[0][1]:.2f}s")
        else:
            unpaired.append(head + (f"; nearest page landing {near[0][2]} at {near[0][1]:.2f}s" if near
                                    else "; no page lands anywhere in the build"))
    return unpaired, paired


def _drop_window_sound_gate(tl: dict, mp: dict) -> Gate | None:
    """M29 (E44 s2a / R26-5): no TRANSIENT sound cue lands inside 0:05-0:12 unless a page lands with it. Reported
    only when a cue lands in the window at all - the M19-M24 shape: a row for what the build actually carries."""
    unpaired, paired = _drop_window_transients(tl, mp)
    if not unpaired and not paired:
        return None
    lo, hi = DROP_WINDOW_S
    win = f" (window {_mm(lo)}-{_mm(hi)}, E44 s2a: the press cue at a cut is not a hook device)"
    if unpaired:
        return Gate("M29", "FAIL", f"{len(unpaired)} transient cue(s) marking nothing inside the drop window: "
                    + "; ".join(unpaired[:6]) + (" ..." if len(unpaired) > 6 else "")
                    + " - drop the cue, or move it onto the page that lands" + win, SRC_M29)
    return Gate("M29", "PASS", f"{len(paired)} transient cue(s) inside the drop window, each with a page landing on "
                "it: " + "; ".join(paired[:6]) + (" ..." if len(paired) > 6 else "") + win, SRC_M29)


# ---- E44 s2b (R26-6): a returning character mounts, it never cuts on ------------------------

def _declared_character(obj: dict | None, evidence: dict) -> str | None:
    """The cast id a world or a species row DECLARES: `character` / `cast` on it, an asset whose evidence species
    is `character`, or a species row of kind `character`. None when nothing declares one - the gate never guesses
    a character from an asset's name (Tokyo's host rides `clip-a-counter-tab-v2`)."""
    if not isinstance(obj, dict):
        return None
    for k in CHARACTER_KEYS:
        if isinstance(obj.get(k), str) and obj[k].strip():
            return obj[k].strip()
    aid = obj.get("asset_id") or obj.get("asset")
    if isinstance(aid, str) and (evidence.get(aid) or {}).get("species") in CHARACTER_SPECIES:
        return aid
    if obj.get("kind") in CHARACTER_SPECIES:
        return str(aid or "character")
    return None


def _scene_entries(s: dict, evidence: dict) -> list[tuple[float, str | None]]:
    """(at, character or None) for everything the scene shows, earliest first: the WORLD at the scene's start - it
    is on screen in the first frame, and the compiler lists it first in timeline["species"] - then every species
    row at its own `at`. The head of this list is the scene's FIRST species."""
    a = float(s["span"][0]) if s.get("span") else 0.0
    out = [(a, _declared_character(s.get("world"), evidence))]
    for sp in s.get("species", []) or []:
        if not isinstance(sp, dict):
            continue
        try:
            at = max(float(sp.get("at", a)), a)
        except (TypeError, ValueError):
            at = a
        out.append((at, _declared_character(sp, evidence)))
    return sorted(out, key=lambda x: x[0])


def _first_character(s: dict, evidence: dict) -> str | None:
    """The character the scene shows FIRST, or None when its first species is not one."""
    entries = _scene_entries(s, evidence)
    return entries[0][1] if entries else None


def _cut_on_returning(scenes: list[dict], evidence: dict) -> tuple[list[str], list[str]]:
    """(offences, entries). A scene's own `exit` names the transition INTO it (the player's law - see
    _transition_events), so R26-6's defect is a scene whose exit is a `cut` (declared, or absent: the default
    boundary is a hard cut) and whose FIRST species is a character an earlier scene already showed."""
    seen: dict[str, float] = {}
    bad, entries = [], []
    for i, s in enumerate(scenes):
        who = _first_character(s, evidence)
        was = seen.get(who) if who else None
        cut = str(s.get("exit") or "cut").split(":")[0] == "cut"
        if i and who and was is not None and cut:
            at = float(s["span"][0]) if s.get("span") else 0.0
            bad.append(f"{s.get('scene_id', '?')} cuts onto {who} at {_mm(at)} - he entered first at {_mm(was)}")
        for at, cid in _scene_entries(s, evidence):
            if cid and cid not in seen:
                seen[cid] = at
                entries.append(f"{cid} enters at {_mm(at)} ({s.get('scene_id', '?')})")
    return bad, entries


def _mount_gate(scenes: list[dict], evidence: dict) -> Gate | None:
    """M30 (E44 s2b / R26-6): a returning character MOUNTS, never cuts on. Reported only when a scene declares a
    character (the M19-M24 shape): the timeline carries no cast of its own, so a build that declares none has
    nothing to measure and says so by carrying no row."""
    bad, entries = _cut_on_returning(scenes, evidence)
    if not entries:
        return None
    if bad:
        return Gate("M30", "FAIL", f"{len(bad)} returning character(s) cut on: " + "; ".join(bad[:6])
                    + (" ..." if len(bad) > 6 else "") + " - a re-entry MOUNTS the way he first mounted (a dissolve "
                    "on a word, doc 29 s9.15): declare the scene's entry transition, never a cut", SRC_M30)
    return Gate("M30", "PASS", f"{len(entries)} character entry/entries, no cut onto a character already seen: "
                + "; ".join(entries[:6]) + (" ..." if len(entries) > 6 else ""), SRC_M30)


def _camera_gate(clashes: list[tuple[str, str]]) -> Gate:
    """M09 (P35 T7): one camera move per window - mirrors build_scene_timeline_f.validate_species
    so a hand-edited timeline (two moves on a scene, or a move over Ken Burns) is caught too."""
    if clashes:
        msg = (f"{len(clashes)} scenes stack camera moves: " + ", ".join(f"{sid} ({why})" for sid, why in clashes[:12])
               + (" ..." if len(clashes) > 12 else ""))
    else:
        msg = "no scene stacks two camera moves (punch | focus_zoom | pull_back) or a camera move over Ken Burns"
    return Gate("M09", "FAIL" if clashes else "PASS", msg, "doc 29 s9.27 precedence / s9.28 C3: one camera move per window")


def _load_hash_file(build: Path, name: str) -> list[dict] | str | None:
    """One frame-hashes file's frames, "stale" when it measured another player.html, None when it is not there."""
    p = Path(build) / name
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(doc, dict) and doc.get("html_sha256"):
        html = Path(build) / "player.html"   # the hashes are keyed to the player they measured: a rebuilt player makes them stale
        if html.exists() and hashlib.sha256(html.read_bytes()).hexdigest() != doc["html_sha256"]:
            return "stale"
    return list(doc.get("frames") or []) if isinstance(doc, dict) else list(doc)


def load_frames(build: Path) -> list[dict] | str | None:
    """The per-frame hashes measure_frozen_frames.py wrote beside the timeline, or None when it has not run."""
    return _load_hash_file(build, FRAME_HASHES_NAME)


def frame_layer_name(layer: str) -> str:
    """`frame-hashes.page.json` - mirrors measure_frozen_frames.layer_hashes_name."""
    return f"frame-hashes.{layer}.json"


def load_frame_layers(build: Path) -> dict[str, list[dict] | str]:
    """The PER-LAYER hashes (R26-13): `{layer: frames}` for every `frame-hashes.<layer>.json` beside the whole-frame
    file, "stale" for one measured on another player. `{}` when the tool has not run with --layers - M18 then reads
    the whole frame exactly as it did before, and says which layers it has."""
    out: dict[str, list[dict] | str] = {}
    for layer in FRAME_LAYERS:
        got = _load_hash_file(build, frame_layer_name(layer))
        if got is not None:
            out[layer] = got
    return out


def load_layout(build: Path) -> dict | str | None:
    """The layout probe.py --gate wrote beside the timeline, or None when it has not run (M18's pattern)."""
    p = Path(build) / LAYOUT_PROBE_NAME
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(doc, dict) and doc.get("player_sha256"):
        html = Path(build) / "player.html"   # the boxes are keyed to the player they were read from
        if html.exists() and hashlib.sha256(html.read_bytes()).hexdigest() != doc["player_sha256"]:
            return "stale"
    return doc if isinstance(doc, dict) else None


def frozen_runs(frames: list[dict], max_s: float = FROZEN_MAX_S) -> list[tuple[float, float]]:
    """(start t, frozen seconds) of every run of identical consecutive hashes longer than max_s - the seconds between
    the run's first and last identical frame. Mirrors measure_frozen_frames.frozen_runs."""
    fs = sorted((float(f["t"]), str(f["sha256"])) for f in frames)
    out: list[tuple[float, float]] = []
    i = 0
    while i < len(fs):
        j = i
        while j + 1 < len(fs) and fs[j + 1][1] == fs[i][1]:
            j += 1
        dur = fs[j][0] - fs[i][0]
        if j > i and dur > max_s:
            out.append((fs[i][0], dur))
        i = j + 1
    return out


LEVEL_RANK = {"PASS": 1, "INFO": 2, "WARN": 3, "FAIL": 4}   # the worst of several reads is the row's level


def layer_windows(A: dict) -> dict[str, list[tuple[float, float]]]:
    """When each layer has something PAINTED on it, from the timeline the gate already parsed (R26-13).

    An unpainted layer is bit-identical to the stage's bare ground, and that is not a held thing going still - the
    first 1.92 s of the Tokyo short carries no dock at all. So the docks are read inside their own dock spans and the
    captions inside their caption pages; the PAGE layer has no window because a world is painted the whole runtime
    (a clip scene's world is the video)."""
    return {"docks": [(float(a), float(b)) for a, b in (A.get("spans") or []) if float(b) > float(a)],
            "captions": [(float(p["s"]), float(p["e"])) for p in (A.get("pages") or [])
                         if isinstance(p, dict) and p.get("e") is not None and float(p["e"]) > float(p.get("s", 0.0))]}


def _frames_in(frames: list[dict], windows: list[tuple[float, float]] | None) -> list[list[dict]]:
    """One list of frames per window, never concatenated: two windows' identical frames are not one run - the layer
    went away in between. `None` (the page) reads the whole measurement as one segment."""
    if windows is None:
        return [frames] if len(frames) >= 2 else []
    segs = []
    for a, b in sorted(windows):
        seg = [f for f in frames if a - 1e-9 <= float(f["t"]) <= b + 1e-9]
        if len(seg) >= 2:
            segs.append(seg)
    return segs


def frozen_layer_verdicts(layers: dict[str, list[dict] | str] | None,
                          windows: dict[str, list[tuple[float, float]]] | None = None) -> list[tuple[str, str, str]]:
    """(layer, level, fragment) for every MEASURED layer, in the shell's order (R26-13).

    The PAGE layer is the read the row exists for: a page held still under a boiling caption is bit-identical here
    while the whole frame is not. A layer nobody measured is absent - it is never a silent PASS. `windows` (from
    layer_windows) restricts a layer to the instants something is painted on it."""
    out: list[tuple[str, str, str]] = []
    for layer in FRAME_LAYERS:
        got = (layers or {}).get(layer)
        if got is None:
            continue
        if got == "stale":
            out.append((layer, "INFO", f"{layer} INFO ({frame_layer_name(layer)} measured another player.html - re-run --layers)"))
            continue
        if len(got) < 2:
            out.append((layer, "INFO", f"{layer} INFO ({len(got)} frame(s) - nothing to compare)"))
            continue
        win = (windows or {}).get(layer)
        segs = _frames_in(got, win)
        read = f", {len(segs)} window(s)" if win is not None else ""
        if not segs:
            out.append((layer, "INFO", f"{layer} INFO (the timeline paints nothing on it{read})"))
            continue
        runs = sorted(r for seg in segs for r in frozen_runs(seg))
        if runs:
            worst = max(runs, key=lambda r: r[1])
            out.append((layer, "WARN", f"{layer} WARN {len(runs)} run(s) over {FROZEN_MAX_S:.2f}s, worst {worst[1]:.2f}s at {_mm(worst[0])}{read}"
                                       + (f" (first {_mm(runs[0][0])}+{runs[0][1]:.2f}s)" if runs[0] != worst else "")))
        else:
            longest = max((r for seg in segs for r in frozen_runs(seg, -1.0)), key=lambda r: r[1], default=(0.0, 0.0))
            out.append((layer, "PASS", f"{layer} PASS (longest {longest[1]:.2f}s at {_mm(longest[0])}{read})"))
    return out


def _frozen_gate(frames: list[dict] | str | None, layers: dict[str, list[dict] | str] | None = None,
                 windows: dict[str, list[tuple[float, float]]] | None = None) -> Gate:
    """M18 (E49): the idle is not an event - it is the absence of a frozen frame. Measured, never inferred: without
    frame-hashes.json the row is INFO and says what to run (no silent skip).

    R26-13: when measure_frozen_frames.py ran with --layers, the page, the docks and the captions are ALSO read each
    on their own (frame-hashes.<layer>.json), because the whole-frame hash cannot see a frozen page beneath a boiling
    caption or a moving dock - Tokyo v2 measured 1036 distinct frames of 1066, M18 PASS, and its pages were still.
    The row's level is the WORST of the whole frame and the layers; the whole-frame verdict is always reported first.
    `windows` (layer_windows) keeps a layer's read to the instants the timeline paints something on it: an empty layer
    is bit-identical to the stage's bare ground, and that is not a held thing going still (the Tokyo short's first
    1.92 s carries no dock)."""
    whole = _frozen_whole(frames)
    per = frozen_layer_verdicts(layers, windows)
    if not per:
        return whole
    level = max([whole.level] + [lvl for _, lvl, _ in per], key=lambda x: LEVEL_RANK.get(x, 0))
    msg = f"whole frame {whole.level}: {whole.message} | per layer (R26-13): " + "; ".join(f for _, _, f in per)
    page = next((lvl for lay, lvl, _ in per if lay == "page"), None)
    if page == "WARN" and whole.level == "PASS":
        msg += " - THE PAGE IS FROZEN under a layer that moves: the whole frame cannot see it (E49: give the held page its idle, kinetics.idle)"
    return Gate("M18", level, msg, SRC_M18)


def _frozen_whole(frames: list[dict] | str | None) -> Gate:
    """M18's whole-frame read, unchanged (P47 T5) - the layers ride on top of it."""
    if frames is None:
        return Gate("M18", "INFO", f"frozen frames not measured - run measure_frozen_frames.py <build> (writes {FRAME_HASHES_NAME})", SRC_M18)
    if frames == "stale":
        return Gate("M18", "INFO", f"{FRAME_HASHES_NAME} measured another player.html (the build was rebuilt since) - re-run measure_frozen_frames.py <build>", SRC_M18)
    if len(frames) < 2:
        return Gate("M18", "INFO", f"{FRAME_HASHES_NAME} carries {len(frames)} frame(s) - nothing to compare", SRC_M18)
    ts = sorted(float(f["t"]) for f in frames)
    step = min((b - a for a, b in zip(ts, ts[1:]) if b > a), default=0.0)
    fps = (1 / step) if step > 0 else 0.0
    runs = frozen_runs(frames)
    span = f"{len(frames)} frames at {fps:.0f} fps, {_mm(ts[0])}-{_mm(ts[-1])}"
    if runs:
        worst = max(runs, key=lambda r: r[1])
        return Gate("M18", "WARN", f"{len(runs)} run(s) of bit-identical frames over {FROZEN_MAX_S:.2f}s ({span}); worst {worst[1]:.2f}s at {_mm(worst[0])}: "
                    + ", ".join(f"{_mm(a)}+{d:.2f}s" for a, d in runs[:8]) + (" ..." if len(runs) > 8 else "")
                    + " - give the held thing its idle (kinetics.idle; E49), never a plate move", SRC_M18)
    # the longest run that stayed under the ceiling, for the record
    longest = max(frozen_runs(frames, -1.0), key=lambda r: r[1], default=(0.0, 0.0))
    return Gate("M18", "PASS", f"no run of bit-identical frames over {FROZEN_MAX_S:.2f}s ({span}); longest {longest[1]:.2f}s at {_mm(longest[0])}", SRC_M18)


def _parked_type(doc: dict) -> list[str]:
    """The runs under the floor that the row LISTS and never scores: the citation by the operator's design pass,
    and anything a park has demoted (E58: the park makes room - a parked chart is a shape, not a read)."""
    smallest: dict[str, float] = {}
    for inst in doc.get("instants") or []:
        for x in inst.get("texts") or []:
            if x["css"] >= TYPE_FLOOR_CSS or not (x.get("pk") or x["k"] in TYPE_FLOOR_EXEMPT):
                continue
            k = x["k"] + (" parked" if x.get("pk") else " (the citation)")
            smallest[k] = min(smallest.get(k, 99.0), x["css"])
    return [f"{k} {v:.1f}" for k, v in sorted(smallest.items(), key=lambda kv: kv[1])]


def _layout_faults(doc: dict) -> tuple[list[str], list[str]]:
    """(FAIL lines, WARN lines) over every probed instant. Each names the two boxes, the instant and the area."""
    fails: list[str] = []
    warns: list[str] = []
    portrait = str(doc.get("aspect") or "16:9") == "9:16"
    for inst in doc.get("instants") or []:
        t = float(inst.get("t", 0.0))
        settled = {d["id"] for d in inst.get("docks") or [] if d.get("rest") and d.get("state") in LAYOUT_SETTLED}
        for o in inst.get("overlaps") or []:
            if o["a"] not in settled:
                continue
            share, px = o["share_of_smaller"] / 100.0, o["area_px"]
            where = f"at {_mm(t)}, {px:,} px, {o['share_of_smaller']} %"
            if o["b"] == "page.data" and share > DATA_OVER_SHARE:
                fails.append(f"{o['a']} over the chart's data {where} of the card")
            elif o["b"] == "caption" and share > CAPTION_TOUCH_SHARE:
                fails.append(f"{o['a']} in the caption strip {where} of the smaller")
            elif (o["b"] in LAYOUT_INK or o["b"].startswith("chart.")) and share > INK_OVER_SHARE:
                fails.append(f"{_ink_name(o['b'])} under {o['a']} {where} of the ink")
        if portrait:
            for x in inst.get("texts") or []:
                if x.get("pk") or x["k"] in TYPE_FLOOR_EXEMPT or x["css"] >= TYPE_FLOOR_CSS:
                    continue
                fails.append(f"{x['k']} type at {x['css']:.1f} CSS px on a phone at {_mm(t)} (floor {TYPE_FLOOR_CSS:.0f}, {x['px']} stage px)")
        for band, pct in (inst.get("clearances") or {}).get("safe_pct", {}).items():
            if pct / 100.0 > SAFE_WARN_SHARE and settled:
                warns.append(f"a card is {pct} % inside the {band} safe-zone band at {_mm(t)}")
    return _dedupe(fails), _dedupe(warns)


def _ink_name(key: str) -> str:
    return {"page.source": "the page's source line", "page.note": "a note", "page.title": "the title", "page.sub": "the sub",
            "pill": "a pill", "chart.lab": "an axis label", "chart.val": "a value", "chart.callout": "a callout",
            "chart.sname": "a series name", "chart.bklab": "a bracket label", "chart.bksub": "a bracket's sub line",
            "chart.spanlab": "a span's label", "chart.wlab": "a wedge label"}.get(key, key)


def _dedupe(lines: list[str]) -> list[str]:
    seen, out = set(), []
    for line in lines:
        key = line.split(" at ")[0]
        if key in seen:
            continue
        seen.add(key)
        out.append(line)
    return out


def _layout_gate(doc: dict | str | None) -> Gate:
    """M25 (P51 T2): the layout gate. Browser-free, exactly as M18 is - it reads the boxes probe.py measured in the
    page's own DOM at the instants that matter, and refuses the three defects of 2026-09-10 by name."""
    if doc is None:
        return Gate("M25", "INFO", f"layout not measured - run probe.py <build> --gate (writes {LAYOUT_PROBE_NAME})", SRC_M25)
    if doc == "stale":
        return Gate("M25", "INFO", f"{LAYOUT_PROBE_NAME} measured another player.html (the build was rebuilt since) - re-run probe.py <build> --gate", SRC_M25)
    instants = (doc or {}).get("instants") or []
    if not instants:
        return Gate("M25", "INFO", f"{LAYOUT_PROBE_NAME} carries no instants - re-run probe.py <build> --gate", SRC_M25)
    fails, warns = _layout_faults(doc)
    span = f"{len(instants)} instants probed"
    parked = _parked_type(doc)
    listed = (" | INFO, listed not scored (CSS px on a phone): " + ", ".join(parked[:4])) if parked else ""
    if fails:
        return Gate("M25", "FAIL", f"{len(fails)} layout fault(s) over {span}: " + "; ".join(fails[:6]) + (" ..." if len(fails) > 6 else "") + listed, SRC_M25)
    if warns:
        return Gate("M25", "WARN", f"{len(warns)} safe-zone intrusion(s) over {span}: " + "; ".join(warns[:4]) + (" ..." if len(warns) > 4 else "") + listed, SRC_M25)
    small = min((x["css"] for i in instants for x in (i.get("texts") or [])
                 if not x.get("pk") and x["k"] not in TYPE_FLOOR_EXEMPT), default=0.0)
    return Gate("M25", "PASS", f"no settled card on the chart's data, on a line of the page's ink or in the caption strip over {span}; "
                f"smallest type read {small:.1f} CSS px on a phone (floor {TYPE_FLOOR_CSS:.0f})" + listed, SRC_M25)


def _printed_number(text: str) -> float | None:
    """The number a page printed, out of the string it printed it in ("36.59%", "-$66.8", "1,405").
    The unit and the separators are dropped; the sign is not (E28: a drop is a negative number)."""
    try:
        return float("".join(c for c in str(text) if c.isdigit() or c in ".-"))
    except (TypeError, ValueError):
        return None


def _value_faults(doc: dict) -> tuple[list[str], int, tuple[float, str]]:
    """(FAIL lines, how many printed values were read, the worst disagreement as a share of the top tick).

    The arithmetic is the chart's own: a bar's value is its height as a share of the distance from the zero
    line to a tick, times that tick's value. Both come from the page as DRAWN, so a parked chart, a rescale
    mid-flight and a burst rewriting its own scale are all read on whatever the viewer is looking at."""
    fails: list[str] = []
    read = 0
    worst = (0.0, "")
    for inst in doc.get("instants") or []:
        t = float(inst.get("t", 0.0))
        bars = (inst.get("page") or {}).get("bars") or {}
        tick = bars.get("tick") or []
        if not bars.get("b") or len(tick) != 2:
            continue
        base, (tv, ty) = float(bars["base"]), (float(tick[0]), float(tick[1]))
        span = base - ty
        if not (span > 1) or not tv:
            continue
        for b in bars["b"]:
            printed = _printed_number(b.get("v")) if b.get("v") else None
            if printed is None:
                continue
            read += 1
            # a bar hangs BELOW the zero line for a negative value (E28): the sign is geometry, so read it there
            sign = 1 if b["y"] + b["h"] <= base + 1 else -1
            drawn = sign * b["h"] / span * tv
            gap = abs(drawn - printed)
            share = gap / abs(tv)
            if share > worst[0]:
                worst = (share, f"{b['l'] or 'a bar'} at {_mm(t)}")
            if gap > VALUE_TOL * abs(tv) + VALUE_OVERSHOOT * abs(printed):
                fails.append(f"{b['l'] or 'a bar'} prints {b['v']} and draws {drawn:.2f} at {_mm(t)} "
                             f"({b['h']} px against {span:.0f} px to the {tv:g} tick)")
    return _dedupe(fails), read, worst


def _values_gate(doc: dict | str | None) -> Gate:
    """M26 (R26-40): the value gate, M25's sibling. Browser-free, from the same layout-probe.json - the page
    prints its scale and its numbers at every instant (E28/E53), and this is the row that reads them against
    the geometry they are printed on."""
    if doc is None:
        return Gate("M26", "INFO", f"values not measured - run probe.py <build> --gate (writes {LAYOUT_PROBE_NAME})", SRC_M26)
    if doc == "stale":
        return Gate("M26", "INFO", f"{LAYOUT_PROBE_NAME} measured another player.html (the build was rebuilt since) - re-run probe.py <build> --gate", SRC_M26)
    instants = (doc or {}).get("instants") or []
    if not instants:
        return Gate("M26", "INFO", f"{LAYOUT_PROBE_NAME} carries no instants - re-run probe.py <build> --gate", SRC_M26)
    fails, read, worst = _value_faults(doc)
    span = f"{len(instants)} instants probed"
    if not read:
        return Gate("M26", "INFO", f"no bars page printed a value at any of the {span} - nothing to check "
                    "(a line page's numbers are its tags, not a height)", SRC_M26)
    band = f"{VALUE_TOL:.0%} of the top tick + the burst's {VALUE_OVERSHOOT:.0%} overshoot"
    if fails:
        return Gate("M26", "FAIL", f"{len(fails)} bar(s) drawn at a height their own printed value does not carry, over {span} "
                    f"(band {band}): " + "; ".join(fails[:6]) + (" ..." if len(fails) > 6 else ""), SRC_M26)
    return Gate("M26", "PASS", f"{read} printed value(s) over {span} agree with the height drawn on the scale the page prints "
                f"(band {band}); worst {worst[0]:.1%} of the top tick" + (f" - {worst[1]}" if worst[1] else ""), SRC_M26)


def _in_build_window(t: float, scenes: list[dict]) -> bool:
    """Was the chart drawing at t - inside one of the scene's compiled `build_windows` (E63)?

    Since the widening this only chooses which WORDS the row uses ("while the chart draws" /
    "on the finished chart"); a card on the plot counts either way."""
    for s in scenes or []:
        a, b = (s.get("span") or [0.0, 0.0])[:2]
        if not (float(a) <= t < float(b)):
            continue
        return any(float(x) <= t <= float(y) for x, y in (s.get("build_windows") or []))
    return False


def _over_build_faults(doc: dict, scenes: list[dict]) -> tuple[list[str], list[str], int]:
    """(FAIL lines, WARN lines, how many not-parked card readings were measured) over every instant.

    E63 WIDENED (the same evening): an instant counts whenever a card that has NOT parked meets the
    page's plot - drawing or finished. The scene's compiled `build_windows` decide nothing any more;
    they only let the row SAY which it was, because that is what the author needs to hear. `marks.drawn`
    is reported, never decisive: it averages every drawn path and reads 0.52 on Tokyo's finished line,
    whose second path is a stub by design. A PARKED card is E45's contract and M25's row. A card the
    compiler already answered for (E63's `read_moved` / `read_deferred`) is still measured, and still
    fails if it is on the ink: the entry is a record of the decision, never an exemption from the frame.

    E65 (2026-09-11): the placer's own fall-through now puts a card in the plot's EMPTY ROOM when the page
    leaves no band outside it - over the plot BOX and over no mark the chart drew. So the row scores what
    M25 scores, the page's INK: the data by DATA_OVER_SHARE, a line of its labels or its citation by
    INK_OVER_SHARE. The plot box on its own is the WARN tier, and the row says the card is clear of the ink."""
    handled = {str(d.get("slide")): ("moved" if d.get("read_moved") else "deferred")
               for s in (scenes or []) for d in (s.get("docks") or []) if d.get("read_moved") or d.get("read_deferred")}
    fails: list[str] = []
    warns: list[str] = []
    measured = 0
    for inst in doc.get("instants") or []:
        t = float(inst.get("t", 0.0))
        drawn = (inst.get("marks") or {}).get("drawn")
        when = "while the chart draws" if _in_build_window(t, scenes) else "on the finished chart"
        state = {d["id"]: d.get("state") for d in inst.get("docks") or []}
        measured += sum(1 for st in state.values() if st not in (None, "parked"))

        def line(o: dict) -> str:
            note = f" - the compiler {handled[o['a']]} this read (E63) and it still lands here" if o["a"] in handled else ""
            return (f"at {_mm(t)}, {o['area_px']:,} px, {o['share_of_smaller']} % of the smaller box"
                    + (f" (marks {float(drawn):.0%} drawn)" if drawn is not None else "") + note)

        on_ink: set[str] = set()
        box_only: list[tuple[str, str]] = []
        for o in inst.get("overlaps") or []:
            card, hit = str(o.get("a")), str(o.get("b"))
            if state.get(card) in (None, "parked"):
                continue                              # a PARKED card is E45's contract and M25's row; this one is the READ
            share = o["share_of_smaller"] / 100.0
            if hit == "page.data" and share > DATA_OVER_SHARE:
                on_ink.add(card)
                fails.append(f"{card} reads on the chart's data {when}, {line(o)}")
            elif (hit in LAYOUT_INK or hit.startswith("chart.")) and share > INK_OVER_SHARE:
                on_ink.add(card)
                fails.append(f"{card} reads on {_ink_name(hit)} {when}, {line(o)}")
            elif hit == "page.plot":
                box_only.append((card, f"{card} is inside the plot's box, clear of the ink, {when}, {line(o)}"))
        for card, msg in box_only:
            if card not in on_ink:                    # E65: the plot's empty room is a PLACE, not a fault
                warns.append(msg)
    return _dedupe(fails), _dedupe(warns), measured


def _over_build_gate(doc: dict | str | None, scenes: list[dict]) -> Gate:
    """M27 (E63, widened): no card READS over a ledger page's plot - drawing or finished. M25's
    sibling, from the same layout-probe.json - M25 scores a SETTLED card's composition, this row
    scores the card's READ against the page's evidence, which is the half the operator caught on
    the Tokyo cut twice: first over the building line, then over the finished one."""
    if doc is None:
        return Gate("M27", "INFO", f"the read over a build not measured - run probe.py <build> --gate (writes {LAYOUT_PROBE_NAME})", SRC_M27)
    if doc == "stale":
        return Gate("M27", "INFO", f"{LAYOUT_PROBE_NAME} measured another player.html (the build was rebuilt since) - re-run probe.py <build> --gate", SRC_M27)
    instants = (doc or {}).get("instants") or []
    if not instants:
        return Gate("M27", "INFO", f"{LAYOUT_PROBE_NAME} carries no instants - re-run probe.py <build> --gate", SRC_M27)
    fails, warns, measured = _over_build_faults(doc, scenes)
    span = f"{len(instants)} instants probed"
    if fails:
        return Gate("M27", "FAIL", f"{len(fails)} card(s) reading over a ledger page's ink over {span}: " + "; ".join(fails[:6])
                    + (" ..." if len(fails) > 6 else "") + f" - move the READ, never the word (E63): a free band at the "
                    f"reading scale, else the plot's own empty room (E65), else the scale that fits", SRC_M27)
    if warns:
        return Gate("M27", "WARN", f"{len(warns)} card(s) inside the plot's box, clear of its ink, over {span}: "
                    + "; ".join(warns[:4]) + (" ..." if len(warns) > 4 else "")
                    + " - E65's own placement; listed so the author sees where the read landed", SRC_M27)
    return Gate("M27", "PASS", f"no card reads over a ledger page's ink over {span} "
                f"({measured} not-parked card reading(s) measured)", SRC_M27)


def _box_gap(a: list[float], b: list[float]) -> float:
    """The shortest distance between two boxes, 0 when they meet (probe.gap_px, browser-free)."""
    dx = max(b[0] - (a[0] + a[2]), a[0] - (b[0] + b[2]), 0.0)
    dy = max(b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]), 0.0)
    return (dx * dx + dy * dy) ** 0.5


def _label_key(label: dict) -> str:
    """How probe.label_key names a label in an overlap pair - "val:$604". The two must agree; the gate
    never rebuilds a pair, it matches the names the probe wrote against the ones on `labels`."""
    return f"{label['role']}:{label['text']}"


def _label_faults(doc: dict) -> tuple[list[str], list[str], int]:
    """(FAIL lines, WARN lines, how many label pairs were checked) over every probed instant.

    FAIL is the frame's own arithmetic - two of the page's labels whose boxes MEET (probe.py wrote the pair
    into `overlaps` when they met by more than a hairline on both axes and by more than the text box's own
    leading) - and the eye's: two of the VALUE row under a QUARTER of a figure apart (the R26-53 frame, where
    the pill's edge stood 6 px off "$604" and read as one string - the operator's "crashing text"). WARN is
    the fit's own law: under half a figure without touching."""
    fails: list[str] = []
    warns: list[str] = []
    pairs = 0
    for inst in doc.get("instants") or []:
        labels = [x for x in (inst.get("labels") or []) if isinstance(x, dict) and x.get("box")]
        if len(labels) < 2:
            continue
        t = float(inst.get("t", 0.0))
        scene = str((inst.get("camera") or {}).get("scene") or "?")
        pairs += len(labels) * (len(labels) - 1) // 2
        named = {_label_key(x) for x in labels}
        touched: set[frozenset] = set()
        for o in inst.get("overlaps") or []:
            a, b = str(o.get("a")), str(o.get("b"))
            if a not in named or b not in named:
                continue                              # a card over the page's ink is M25's row, not this one
            touched.add(frozenset((a, b)))
            fails.append(f"{a} on {b} at {_mm(t)} ({scene}), {o['area_px']:,} px, "
                         f"{o['share_of_smaller']} % of the smaller label")
        # THE FIT'S OWN AIR. The value size the page is drawing at, from the same instant's type table.
        vpx = next((float(x["px"]) for x in inst.get("texts") or [] if x.get("k") == "chart.val"), 0.0)
        air = LABEL_AIR_EM * vpx
        if air <= 0:
            continue
        row = [x for x in labels if x["role"] in LABEL_AIR_ROLES]
        for n, la in enumerate(row):
            for lb in row[n + 1:]:
                ka, kb = _label_key(la), _label_key(lb)
                if frozenset((ka, kb)) in touched:
                    continue
                gap = _box_gap(la["box"], lb["box"])
                if gap < LABEL_TOUCH_EM * vpx:
                    fails.append(f"{ka} and {kb} at {_mm(t)} ({scene}), {gap:.0f} px of air - under a quarter of a figure "
                                 f"({LABEL_TOUCH_EM * vpx:.0f} at {vpx:.0f} px): the eye reads one string (R26-53)")
                elif gap < air:
                    warns.append(f"{ka} and {kb} at {_mm(t)} ({scene}), {gap:.0f} px of air where the row "
                                 f"is fitted with {air:.0f} (half a figure at {vpx:.0f} px)")
    return _dedupe(fails), _dedupe(warns), pairs


def _labels_gate(doc: dict | str | None) -> Gate:
    """M28 (R26-53): text on text among a ledger page's OWN labels. M25's sibling, from the same
    layout-probe.json - M25 refuses a CARD over the page's ink; this row refuses the page's ink over
    itself, which is the half the operator caught on the Meta page: four values touching and the
    callout's pill on the fourth bar sitting on the third bar's number."""
    if doc is None:
        return Gate("M28", "INFO", f"text on text not measured - run probe.py <build> --gate (writes {LAYOUT_PROBE_NAME})", SRC_M28)
    if doc == "stale":
        return Gate("M28", "INFO", f"{LAYOUT_PROBE_NAME} measured another player.html (the build was rebuilt since) - re-run probe.py <build> --gate", SRC_M28)
    instants = (doc or {}).get("instants") or []
    if not instants:
        return Gate("M28", "INFO", f"{LAYOUT_PROBE_NAME} carries no instants - re-run probe.py <build> --gate", SRC_M28)
    fails, warns, pairs = _label_faults(doc)
    span = f"{len(instants)} instants probed"
    if not pairs:
        return Gate("M28", "INFO", f"no page showed two labels at once at any of the {span} - nothing to check "
                    "(a plate has no labels of its own)", SRC_M28)
    if fails:
        return Gate("M28", "FAIL", f"{len(fails)} pair(s) of a page's own labels sitting on each other over {span}: "
                    + "; ".join(fails[:6]) + (" ..." if len(fails) > 6 else "")
                    + " - fit the row (lpFitValues), raise the pill to its band (lpPillBand) or move the label; "
                    "a number on a number is not a number", SRC_M28)
    if warns:
        return Gate("M28", "WARN", f"{len(warns)} pair(s) of the value row closer than half a figure over {span}: "
                    + "; ".join(warns[:4]) + (" ..." if len(warns) > 4 else "")
                    + " - the boxes clear each other and the eye does not (R26-53); the fit's air law is "
                    "lpFitValues' own", SRC_M28)
    return Gate("M28", "PASS", f"no two of a page's own labels touch, and the value row keeps half a figure of air, "
                f"over {span} ({pairs:,} label pair(s) checked)", SRC_M28)


def _build_to_holds(scenes: list[dict]) -> list[tuple[float, float]]:
    """P47 T2: between one build_to's landing and the next one's word the line HOLDS at a datum - the pen resting on the
    cap is not stillness the author forgot, it is the hold the sentence asked for. Listed for the judge, never scored."""
    out: list[tuple[float, float]] = []
    for s in scenes:
        caps = sorted((float(sp["at"]), float(sp.get("dur", 0.0))) for sp in s.get("species", []) if sp.get("kind") == "build_to")
        for (a, d), (b, _) in zip(caps, caps[1:]):
            if b > a + d:
                out.append((round(a + d, 2), round(b - a - d, 2)))
    return out


def _deployed_lives(scenes: list[dict]) -> list[tuple[str, float, float, float]]:
    """E50: per ledger page, (scene_id, last data mark, end, deployed). The data marks are the build's landing on the page's
    own clock (a returning page arrives drawn: its entry) and the end of every build_to and bracket inside the span; the
    life ends at the first undraw after the last mark, else at the page's exit. Annotations (spotlight, callout, retitle,
    relight, figure) add no data and neither restart nor end the clock."""
    out: list[tuple[str, float, float, float]] = []
    for s in scenes:
        if not _is_page(s) or not s.get("span"):
            continue
        a, z = float(s["span"][0]), float(s["span"][1])
        sp = s.get("species", [])
        page = ((s.get("world") or {}).get("page") or {})
        marks = [a + _page_land_offset(s)]
        marks += [float(x["at"]) + float(x.get("dur", 0.0)) for x in sp if x.get("kind") in ("build_to", "bracket") and a <= float(x.get("at", -1e9)) <= z]
        # P48 T6: a chart that changes its data state is a new chart's life - E50's clock restarts at the transition's end
        marks += [_transition_land(s, x) for x in sp if x.get("kind") == "chart_to" and x.get("to") in TRANSITION_DATA_KINDS and a <= float(x.get("at", -1e9)) <= z]   # E60: a breakthrough state's run is its last mark
        last = max(m for m in marks if m <= z + 1e-6) if any(m <= z + 1e-6 for m in marks) else a
        uds = sorted(float(x["at"]) for x in sp if x.get("kind") == "undraw" and last - 1e-6 <= float(x.get("at", -1e9)) <= z)
        end = uds[0] if uds else z
        out.append((str(s.get("scene_id", "?")), round(last, 2), round(end, 2), round(max(0.0, end - last), 2)))
    return out


def _landings(s: dict) -> list[tuple[float, str]]:
    """Every LANDING on a scene: the page's chart landing, each build_to / bracket / figure / note end, each dock's arrival
    (its enter, plus a throw's flight or a land's anticipation + drop), each badge landing on a page."""
    a = float(s["span"][0]) if s.get("span") else 0.0
    out: list[tuple[float, str]] = []
    if _is_page(s):
        out.append((a + _page_land_offset(s), "the chart's landing"))
        page = ((s.get("world") or {}).get("page") or {})
        for k, bat in enumerate(((s.get("world") or {}).get("badge_at") or [])):
            out.append((float(bat), f"badge {k}"))
    for sp in s.get("species", []):
        if sp.get("kind") in ("build_to", "bracket", "figure", "note"):
            out.append((float(sp.get("at", 0.0)) + float(sp.get("dur", 0.0)), f"{sp['kind']} landing"))
        if sp.get("kind") == "chart_to" and sp.get("to") in TRANSITION_DATA_KINDS:   # P48 T6: the chart that arrives by a transition has LANDED (E51)
            out.append((_transition_land(s, sp), f"chart_to {sp.get('to')} landing"))   # E60: a breakthrough state lands when its run ends
    for d in s.get("docks", []):
        arr = d.get("arrive")
        contact = float(d.get("enter", 0.0)) + (0.46 if arr == "throw" else 0.32 if arr == "land" else 0.0)
        out.append((contact, f"dock {d.get('slide', '?')} {arr or 'spring'}"))
    return out


def _untied_pushes(scenes: list[dict]) -> list[tuple[str, str, float]]:
    """E51: every punch / focus_zoom with no landing on its scene inside (at - PUSH_TIE_BEFORE_S, at + PUSH_TIE_AFTER_S)."""
    out: list[tuple[str, str, float]] = []
    for s in scenes:
        lands = [t for t, _n in _landings(s)]
        for sp in s.get("species", []):
            if sp.get("kind") not in ("punch", "focus_zoom"):
                continue
            at = float(sp.get("at", 0.0))
            if not any(at - PUSH_TIE_BEFORE_S <= t <= at + PUSH_TIE_AFTER_S for t in lands):
                out.append((str(s.get("scene_id", "?")), sp["kind"], round(at, 2)))
    return out


def _push_tie_gate(scenes: list[dict]) -> Gate | None:
    """M22 (E51): a push that is not tied to a landing is filler - WARN, naming each."""
    if not any(sp.get("kind") in ("punch", "focus_zoom") for s in scenes for sp in s.get("species", [])):
        return None
    bad = _untied_pushes(scenes)
    if bad:
        return Gate("M22", "WARN", f"{len(bad)} push(es) tied to nothing: " + "; ".join(f"{sid} {k} at {_mm(t)}" for sid, k, t in bad[:8])
                    + " - a push lands ON a thing that just landed (a badge, a datum, a bracket, a card) or it is cut", SRC_M22)
    return Gate("M22", "PASS", "every push is tied to a landing on its scene", SRC_M22)


def _transitions(scenes: list[dict]) -> list[dict]:
    """Every declared chart_to on a ledger page: scene, verb, at, dur, end, and the two faults M23 names."""
    out: list[dict] = []
    for s in scenes:
        if not _is_page(s) or not s.get("span"):
            continue
        a, z = float(s["span"][0]), float(s["span"][1])
        land = a + _page_land_offset(s)
        for sp in s.get("species", []):
            if sp.get("kind") != "chart_to":
                continue
            at, dur = float(sp.get("at", 0.0)), float(sp.get("dur", 0.0))
            out.append({"scene": str(s.get("scene_id", "?")), "to": sp.get("to"), "at": round(at, 2), "dur": round(dur, 2), "end": round(at + dur, 2),
                        "in_build": at < land - 1e-6, "at_edge": at + dur > z - TRANSITION_EDGE_S + 1e-6})
    return out


def _states_without_a_transition(scenes: list[dict]) -> list[str]:
    """A page built with two (or three) chart states that no chart_to ever moves between: a state built for nothing."""
    out: list[str] = []
    for s in scenes:
        if not _is_page(s):
            continue
        n_states = 1 + len(((s.get("world") or {}).get("page_states") or []))
        moves = [sp for sp in s.get("species", []) if sp.get("kind") == "chart_to" and sp.get("to") in TRANSITION_DATA_KINDS]
        if n_states > 1 and not moves:
            out.append(f"{s.get('scene_id', '?')} carries {n_states} chart states and no transition")
    return out


def _transition_gate(scenes: list[dict]) -> Gate | None:
    """M23 (P48 T6): the transitions, listed; a transition over the build or at the edge WARNs; states with no transition FAIL."""
    xs = _transitions(scenes)
    orphans = _states_without_a_transition(scenes)
    if not xs and not orphans:
        return None
    if orphans:
        return Gate("M23", "FAIL", "; ".join(orphans) + " - a second chart state is built to be moved to (chart_to recast|rescale|extend), or it is a card", SRC_M23)
    bad = [x for x in xs if x["in_build"] or x["at_edge"]]
    listing = ", ".join(f"{x['scene']} {x['to']} {_mm(x['at'])}+{x['dur']:.1f}s" for x in xs[:10]) + (" ..." if len(xs) > 10 else "")
    if bad:
        why = "; ".join(f"{x['scene']} {x['to']} at {_mm(x['at'])}" + (" fires inside the page's build beat" if x["in_build"] else "") + (" ends inside the last 0.5 s of its page" if x["at_edge"] else "") for x in bad[:6])
        return Gate("M23", "WARN", f"{len(xs)} transition(s): {listing} - {why} (E45: never over a build; E50: a transition is how a chart leaves, not a cut wearing a verb)", SRC_M23)
    return Gate("M23", "PASS", f"{len(xs)} transition(s), each on a built chart and clear of its page's edge: {listing}", SRC_M23)


def _end_of(scenes: list[dict], scene_id: str) -> float:
    for s in scenes:
        if str(s.get("scene_id", "?")) == scene_id and s.get("span"):
            return float(s["span"][1])
    return 0.0


def _span_of(scenes: list[dict], scene_id: str) -> float:
    for s in scenes:
        if str(s.get("scene_id", "?")) == scene_id and s.get("span"):
            return round(float(s["span"][1]) - float(s["span"][0]), 2)
    return 0.0


def _arrive_of(scenes: list[dict], scene_id: str) -> float:
    """Arrival + build for one page - the part of the span that is NOT deployed life."""
    for s in scenes:
        if str(s.get("scene_id", "?")) == scene_id:
            return round(_page_land_offset(s), 2)
    return 0.0


def _deployed_gate(scenes: list[dict]) -> Gate | None:
    """M21 (E50): the chart's deployed life per ledger page - over DEPLOY_MAX_S WARN, over DEPLOY_AVG_S INFO, else PASS."""
    lives = _deployed_lives(scenes)
    if not lives:
        return None
    row = lambda l: f"{l[0]} {l[3]:.1f}s ({_mm(l[1])} -> {_mm(l[2])})"
    # the SPLIT the author needs: a span is arrival + build + deployed, and only the last of the three is E50's clock
    split = lambda l: (f"{l[0]} {l[3]:.1f}s deployed of a {_span_of(scenes, l[0]):.1f}s span "
                       f"(arrive+build {_arrive_of(scenes, l[0]):.1f}s), {DEPLOY_MIN_S - l[3]:.1f}s short")
    # the floor applies only to a page CUT short. A page that ends its own life with an undraw is LEAVING on purpose -
    # E50's "then it un-draws or becomes the next thing" - and a deliberate exit is not a rushed chart.
    short = [l for l in lives if l[3] < DEPLOY_MIN_S and l[2] >= _end_of(scenes, l[0]) - 1e-6
             and _arrive_of(scenes, l[0]) < 1.0]   # only a page that ARRIVES BUILT: a page that draws was read as it drew
    over = [l for l in lives if l[3] > DEPLOY_MAX_S]
    long = [l for l in lives if DEPLOY_AVG_S < l[3] <= DEPLOY_MAX_S]
    if short and not over:
        return Gate("M21", "WARN", f"{len(short)} page(s) deployed under {DEPLOY_MIN_S:.0f}s after the last data mark: "
                    + "; ".join(split(l) for l in short[:8])
                    + " - it ARRIVES BUILT and is cut before it can be read. A page that draws is exempt (the build leads"
                      " the eye and IS the reading); this one asks the viewer to find their own way around a finished"
                      " chart, so give the span the seconds", SRC_M21)
    if over:
        return Gate("M21", "WARN", f"{len(over)} page(s) deployed past {DEPLOY_MAX_S:.0f}s after the last data mark: " + "; ".join(row(l) for l in over[:8])
                    + " - un-draw it (undraw) or let it become the next thing (figure, another display, the morph)", SRC_M21)
    if long:
        return Gate("M21", "INFO", f"{len(long)} page(s) deployed {DEPLOY_AVG_S:.0f}-{DEPLOY_MAX_S:.0f}s after the last data mark (a dock's clip may hold it): " + "; ".join(row(l) for l in long[:8]), SRC_M21)
    return Gate("M21", "PASS", f"every ledger page leaves or un-draws within {DEPLOY_AVG_S:.0f}s of its last data mark: " + "; ".join(row(l) for l in lives[:8]), SRC_M21)


def _build_to_gate(scenes: list[dict]) -> Gate | None:
    """M19 (INFO): the build_to holds, by name, so M01/M02's still stretches can be read against them."""
    if not any(sp.get("kind") == "build_to" for s in scenes for sp in s.get("species", [])):
        return None
    holds = _build_to_holds(scenes)
    msg = (f"{len(holds)} build_to hold(s) - the line rests at a datum until the next word: " + ", ".join(f"{_mm(a)}+{d:.1f}s" for a, d in holds[:8])) if holds else "build_to caps declared; none holds between caps"
    return Gate("M19", "INFO", msg, "P47 T2 (SHOT-TABLE-V3-PROPOSAL part B): a cap is a hold the sentence asked for, not stillness")


def _arrivals(scenes: list[dict]) -> list[tuple[float, str, str, float]]:
    """(enter, slide, arrive, landing time) for every dock that arrives by a throw or a landing (P47 T1)."""
    out = []
    for sc in scenes:
        for d in sc.get("docks", []):
            arr = d.get("arrive")
            if arr in ("throw", "land"):
                out.append((float(d["enter"]), str(d.get("slide", "?")), arr, float(d["enter"]) + (STOP_FLIGHT_S if arr == "throw" else STOP_LAND_S)))
    return out


def _arrival_events(scenes: list[dict]) -> list[float]:
    """A throw or a landing is motion: its enter and its impact are events (the pop's enter is already the dock's)."""
    return [round(t, 2) for e, _s, _a, t in _arrivals(scenes)]


def _cadence_gate(scenes: list[dict]) -> Gate | None:
    """M20 (INFO): the cadence rule per thrown card - the flight's speed and the hold it steps on."""
    arr = _arrivals(scenes)
    if not arr:
        return None
    rows = []
    for sc in scenes:
        for d in sc.get("docks", []):
            if d.get("arrive") == "throw":
                w = float((d.get("place") or {}).get("w") or CARD_W_DEFAULT)
                v = ((w + STOP_THROW_DX) ** 2 + STOP_THROW_DY ** 2) ** 0.5 / STOP_FLIGHT_S
                rows.append(f"{d.get('slide', '?')} throw ~{v:.0f} px/s -> on {1 if v > STOP_ON1_PX_S else 2}s")
            elif d.get("arrive") == "land":
                rows.append(f"{d.get('slide', '?')} land ({d.get('mass', 'paper')}) - weight sold {STOP_LAND_S:.2f}s before the impact")
    return Gate("M20", "INFO", f"{len(arr)} arrival(s): " + "; ".join(rows[:8]), SRC_M20)


def load_morph_invariants(build: Path) -> dict | str | None:
    """The per-scene invariants measure_morph.py wrote beside the timeline; None when it has not run; "stale" when the
    player was rebuilt since."""
    p = Path(build) / MORPH_INVARIANTS_NAME
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    html = Path(build) / "player.html"
    if doc.get("html_sha256") and html.exists() and hashlib.sha256(html.read_bytes()).hexdigest() != doc["html_sha256"]:
        return "stale"
    return doc


def _morph_events(sc: dict) -> list[dict]:
    """P48 T5: the `chart_to morph` species on a page, each with the state it starts from (the active state at its word)."""
    out, cur = [], 0
    for sp in sorted((e for e in sc.get("species", []) if isinstance(e, dict) and e.get("kind") == "chart_to"), key=lambda e: float(e.get("at", 0.0))):
        if sp.get("to") == "park":
            continue
        k = int(sp.get("state", 0) or 0)
        if sp.get("to") == "morph":
            out.append({"at": float(sp.get("at", 0.0)), "dur": float(sp.get("dur", 1.0)), "from": cur, "to": k, "key": f"{sc.get('scene_id', '?')}@{float(sp.get('at', 0.0)):.2f}"})
        cur = k
    return out


def _morphs(scenes: list[dict]) -> list[tuple[str, str]]:
    """Every morph on the timeline as (measurement key, label): a page that ENTERS by morph (keyed by its scene id, as
    measure_morph.py has always written it) and every morph_to on a page (keyed scene@at) - M17 is measured PER MORPH."""
    out: list[tuple[str, str]] = []
    for s in scenes:
        if not _is_page(s):
            continue
        if ((s.get("world") or {}).get("page") or {}).get("enter") == "morph":
            out.append((str(s.get("scene_id", "?")), str(s.get("scene_id", "?"))))
        for ev in _morph_events(s):
            out.append((ev["key"], f"{s.get('scene_id', '?')} morph_to at {_mm(ev['at'])}"))
    return out


def _morph_gate(scenes: list[dict], inv: dict | str | None) -> Gate | None:
    """M17 (P47 T3; P48 T5 per morph): the three match-cut invariants per MORPH - a page's enter morph and every morph_to -
    measured in the player - INFO until measured (no silent skip), WARN naming the invariant that failed, PASS with the
    numbers. No morph, no row."""
    morphs = _morphs(scenes)
    if not morphs:
        return None
    if inv is None:
        return Gate("M17", "INFO", f"{len(morphs)} morph(s), invariants not measured - run measure_morph.py <build> (writes {MORPH_INVARIANTS_NAME})", SRC_M17)
    if inv == "stale":
        return Gate("M17", "INFO", f"{MORPH_INVARIANTS_NAME} measured another player.html - re-run measure_morph.py <build>", SRC_M17)
    rows, bad = [], []
    for key, label in morphs:
        r = (inv.get("scenes") or {}).get(key)
        sc = {"scene_id": label}   # the row names the morph, not only its page
        if not r:
            bad.append(f"{label}: not in the measurement"); continue
        fails = [n for n, ok in (("centroid", r.get("centroid_ok")), ("axis", r.get("axis_ok")), ("area", r.get("area_ok"))) if not ok]
        if r.get("min_det", 1) <= 0:
            fails.append("det J <= 0")
        # P50 T12: WHICH METHOD ran is part of the reading - Method A's det is a measurement, Method B's is a guarantee
        txt = (f"{sc.get('scene_id')}: method {str(r.get('method') or 'arap')}, centroid {100 * float(r.get('centroid_shift', 0)):.1f} % W, "
               f"axis {float(r.get('axis_deg', 0)):.1f} deg, area {float(r.get('area_ratio', 0)):.2f}, min det {float(r.get('min_det', 0)):.3f}")
        (bad if fails else rows).append(txt + (" - FAILS " + ", ".join(fails) if fails else ""))
    if bad:
        return Gate("M17", "WARN", "; ".join(bad + rows) + " - the morph does not read as one thing changing (move the prop onto the chart's box, keep its axis, keep its area)", SRC_M17)
    return Gate("M17", "PASS", "; ".join(rows), SRC_M17)


def _stats(A: dict, still_total: float) -> dict:
    R = A["runtime"]
    mm = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
    return {"runtime": mm(R), "visual_events": f"{len(A['events'])} ({len(A['events']) / (R / 60):.1f}/min)",
            "docks": len(A["spans"]), "dock_source": A["dock_source"], "ledger_pages": A["n_pages"],
            "still_over_12s_share": f"{100 * still_total / R:.0f}%",
            "per_minute": " ".join(f"{mm(lo)}:{n:.0f}/{nd:.0f}" for lo, n, nd in A["dens"])}


REPORT_NAME = "GATES-MOTION.md"  # written beside the timeline by the build (P34 T4); consulted by render_episode.py
LEVEL_ORDER = {"FAIL": 0, "WARN": 1, "PASS": 2, "INFO": 3, "JUDGE": 4}


def fail_count(gates: list[Gate]) -> int:
    return sum(1 for x in gates if x.level == "FAIL")


def report_text(gates: list[Gate], stats: dict, build_dir: Path) -> str:
    """The gate's stdout, verbatim: header, stats, gates sorted by level, RESULT line."""
    lines = [f"=== MOTION DENSITY GATE: {build_dir} ==="]
    lines += [f"  {k:>20}: {v}" for k, v in stats.items()]
    lines.append("")
    for x in sorted(gates, key=lambda x: (LEVEL_ORDER[x.level], x.id)):
        lines.append(f"  [{x.level:5}] {x.id} {x.message}\n          {x.src}")
    n = lambda lvl: sum(1 for x in gates if x.level == lvl)
    lines.append(f"\nRESULT: {n('FAIL')} FAIL / {n('WARN')} WARN / {n('PASS')} PASS / {n('JUDGE')} JUDGE / {n('INFO')} INFO")
    return "\n".join(lines)


def write_report(build_dir: Path, timeline_name: str | None = None) -> tuple[Path, int]:
    """Run the gate on a build dir and write `<build_dir>/GATES-MOTION.md`.

    The report is the gate's stdout inside a fenced block, headed by the
    build dir name and closed by a `VERDICT: PASS|FAIL (<n> FAIL)` line that
    `render_episode.py` reads before a full render (E21 / doc 29 s9.25).
    Returns the report path and the FAIL count.
    """
    build_dir = Path(build_dir)
    tl, docks, mp = _load(build_dir, timeline_name)
    tl_path = _timeline_path(build_dir, timeline_name)
    gates, stats = run(tl, docks, mp, load_frames(build_dir), load_morph_invariants(build_dir), load_layout(build_dir),
                       load_frame_layers(build_dir))
    n_fail = fail_count(gates)
    verdict = "FAIL" if n_fail else "PASS"
    # the timeline hash keys the report to the build it measured; render_episode refuses a
    # full render when the timeline on disk no longer hashes to it (a stale report is no report)
    digest = hashlib.sha256(tl_path.read_bytes()).hexdigest()
    body = (f"# MOTION GATE — {build_dir.name}\n\n```text\n{report_text(gates, stats, build_dir)}\n```\n\n"
            f"TIMELINE: {tl_path.name} sha256:{digest}\n"
            f"VERDICT: {verdict} ({n_fail} FAIL)\n")
    out = build_dir / REPORT_NAME
    out.write_text(body, encoding="utf-8")
    return out, n_fail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("build", type=Path, help="episode build dir (build-f)")
    ap.add_argument("--timeline", help="timeline file name inside the build dir")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tl, docks, mp = _load(args.build, args.timeline)
    gates, stats = run(tl, docks, mp, load_frames(args.build), load_morph_invariants(args.build), load_layout(args.build),
                       load_frame_layers(args.build))
    print(report_text(gates, stats, args.build))
    return 1 if fail_count(gates) else 0


if __name__ == "__main__":
    raise SystemExit(main())

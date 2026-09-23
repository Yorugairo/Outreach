"""Steel and Paper — convert the Script F build into `scene_evidence_timeline.v1`
and render through the established player.

There is already a player: `samples/scene-evidence-player.template.html`.
This script feeds it. It does NOT write a new one — a bespoke player was
built and discarded once already, and it rendered black because it
referenced assets by path instead of embedding them.

The schema encodes things a flat cue list does not: a scene OWNS its world
plate and that plate's Ken Burns move; docks carry a semantic SLOT so
evidence roams while the caption anchor never moves; evidence carries badges
and a source line.

A shot-table plate id of the form ``ledger:<series-id>:<variant>[:<emphasize>
[:<quiet_zone>]]`` is a LEDGER PAGE world (doc 29 s9.26 / s9.28, P35 T4): the
world is DRAWN by the player from ``world.page`` (the ``ledger_page.v1`` spec
built from ``evidence/objects/<series-id>.series.json``), so the scene carries
no ``asset_id`` / ``sha256`` and embeds no plate PNG. The compiled timeline
lists every species present in ``species`` (``["ledger"]`` or ``[]``).

A shot-table row may carry an optional 7th element: a ``species`` list of
TARGETED SPECIES (doc 29 s9.27 MOTION MENU, P35 T7). The targeting law is
code here: every pointing species carries a DECLARED target (datum, point,
region or word span) or the build fails naming the row and the kind - a
species with no declared target does not fire, and we fail rather than drop
it silently. ``validate_species`` is the pure rule; the list is emitted
verbatim onto the compiled scene as ``scene["species"]`` and the kinds
present extend the timeline's top-level ``species`` list.
"""
from __future__ import annotations

import ast
import base64
import io
import hashlib
import copy
import functools
import json
import math
import re
import mimetypes
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
BUILD = EP / "build-f"
TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
sys.path.insert(0, str(Path(__file__).parent))
import build_render_f as R  # noqa: E402  (asset resolver + doc-29 durations)
import gate_motion_density as MG  # noqa: E402  (E21 motion gate -> GATES-MOTION.md)
import ledger_page as LPG  # noqa: E402  (series.json -> ledger_page.v1 spec, doc 29 s9.26)

LEDGER_PREFIX = "ledger:"          # shot-table plate id prefix for a LEDGER PAGE world (s9.28 surface = page)
LEDGER_ID_PARTS = (3, 7)           # ledger:<series>:<variant>[:<emphasize>[:<quiet_zone>[:<enter>[:<exit>]]]]  enter = spiral | mount=<seconds>; exit = cut
LEDGER_ENTERS = ("spiral", "mount", "morph", "snap", "built", "throw", "drop", "camera", "axes", "surface")   # enter=axes (P53 T1, the operator 2026-09-12): the charcoal page lands with its ground, its ruled line, its title, its labels and its AXES already drawn, and the CHART draws from the first frame - "that gives us the first initial frame of motion". `built` is its still sibling: the whole page, data included, at frame 0.   # enter=camera=<dock>: P49 T5 - the page arrives BUILT and the EYE goes to the landed card (the camera zooms the outgoing world and the card until the card fills the stage, then the world is the page) - the snap's opposite number, opt-in until HG2   # enter=drop: the page FALLS into the frame from above and lands as the world (the dock's landXf) - "is falling down into the frame easier?" (operator, 2026-09-08)   # enter=throw (2026-09-08): the whole page is THROWN onto the world and arrives built - the transition IS the plate entering the world   # enter=built: the page ARRIVES with its chart already drawn, by the row's own transition - it NEVER mounts (operator, 2026-09-08: mount is cream coming through over the scene, then drawing). `surface=<paper>,<lead_s>` is the registered paper handoff; the binder supplies its destination spec and native-wide geometry.
# The build is a device, not an obligation - five builds in one short is repetition, and a page that arrives complete spends
# its whole span being read instead of being drawn (operator, 2026-09-08: "maybe chart 1 doesn't actually need a build, it
# could enter built, the deconstruction/transformation is its own thing"). E49 keeps it alive; the transformation is the
# motion. Unlike `spiral` this carries no RETURN meaning - it is for a chart's first appearance.   # enter=snap=<dock asset>: the page arrives BUILT, grown from that landed card's rectangle to the stage (the third watch, 2026-09-07)   # enter=morph[=<s>]: the page's prop outline (world.morph) becomes the chart by ARAP (P47 T3); enter=spiral: the page RETURNS - unwinds from its point, no roll/soak/ink/build (E25; 2026-09-05)
                                      # enter=mount: no roll-out - the outgoing scene fades while the cream plate MOUNTS over it, then the page draws (operator, 2026-09-05)
KINETICS: dict = {}                # timeline.kinetics - the template's capability flags a build turns on (P39 kill switch; default all off)
CAPTION_STYLE: str | None = None   # timeline.caption_style - "phrase" on a short: the page lands as one readable phrase, only k-words punctuated (2026-09-05)
CAPTION_ARRIVE: str | None = None   # timeline.caption_arrive + page.cap_arrive - HOW a stage page's words arrive (P52 T10). None = the pop
                                    # every build shipped before the slice, and NO field is written, so every golden and both shorts compile byte-identical.
CAPTION_ARRIVALS = ("pop", "fade_up")   # "fade_up" [DERIVED: HyperFrames staggered-fade-up]: ONE envelope, per-word offsets - y 22 px -> 0, scale 0.92 -> 1,
                                        # blur 5 px -> 0, stagger 0.055 s (kinetics/stagger.mjs) - the quiet register, "more caption motion without overcrowding"
CAPTION_LIFE: str | None = None     # timeline.caption_life + page.cap_life - the caption's LIFE (E90, P57 T14). None = the caption Steel and
                                    # Paper shipped; no field is written, so every golden and both approved shorts compile byte-identical.
CAPTION_LIVES = ("pop", "stagger", "blend")   # "pop" = the shipped pop one notch stronger (kinetics/stagger.mjs LIFE.POP_LEAD 1.22 against the base's
                                    # 1.16); "stagger" = P52 T10's envelope alone; "blend" = the pop's scale and tilt riding ON TOP of the stagger's
                                    # 22 px rise, no blur (E90 s2 "a blend, not a switch"), the held page breathing under it (E49). All three renderable
                                    # so the operator's eye rules at HG2 (E90 s3) - the slice ships the dial, not one baked answer.
LEDGER_EXITS = ("cut",)            # exit=cut: no retract - the page leaves on the cut (for a beat that must land on the last line, E40 #5)
SPECIES_LEDGER = "ledger"          # timeline["species"] entry; the player keys on world.kind == "ledger"

# SCENE EXITS (ruling E47, operator 2026-09-06). `exit` names the transition INTO the scene it
# sits on - the player's law for the wipe, the suck and the dissolve alike. The two world-change
# transitions off the measured reference (doc 46 s46.5) join the kit and take the mechanical
# default; the carried-light cross-reveal stays reachable BY NAME as an effect and is the default
# nowhere ("we made it the default because it worked, but we need a better default, and it can be
# an effect at that point"). dip and blurzoom may carry their own length: `dip:<s>`, `blurzoom:<s>`.
SCENE_EXITS = ("cut", "dip", "blurzoom", "dissolve", "wipe", "wipe_right", "suck", "melt", "slide", "door")   # door (E98 s7, R26-134): the EVIDENCE DOOR - the outgoing world swings open on one stage edge, away from the viewer, onto the incoming world mounted beneath it - `door[:<left|right|top|bottom>][:<s>]`, refused out of a page at a depth or on a plane and across a live dock   # slide (R26-75, E87 s3): the incoming frame pushes the outgoing one off along one axis, both moving together - `slide:<left|right|up|down>[:<s>]`, the direction never defaulted   # melt (P52 T9, R26-15): the outgoing world sags into drips, balls up on 2s and is thrown off the stage or splashed - `melt`, `melt:<s>`, `melt:splash`, `melt:<x>,<y>` (the exit point in stage fractions), the suffixes in any order
IDLE_KINDS = ("none", "breath", "drift", "pulse", "figure", "live")   # live (2026-09-08): breath + drift - the breath has a fixed point at the centre, so a chart at the page centre read as still; the drift moves every pixel   # E49 / P47 T5: the player's named idles; `;idle=<kind>` on any plate id (`none` is explicit stillness)
IDLE_OPT = ";idle="
# E99 s55 (R26-133 closed; the operator, 2026-09-16: "maybe we need a slightly smaller drift (maybe 30 px?) AND the
# alive water ... for youtube the 40 px drift would be too much motion for a long form, but it looks like it might
# work really well for shorts and certain scenes"), AMENDED the same day by E99 s63 on the watch: "also 30 px drift
# might still be too much, maybe 20 px drift" - so the named LONG-FORM setting is 20 and 30-40 is the shorts range.
# The drift's AMPLITUDE, authored PER SCENE on the plate id:
# `;idle=drift;drift=20`. `kinetics/idle.mjs` IDLE.DRIFT_PX (2.0) is the FLOOR, not a default to go under - it is
# E49's "nothing ever goes truly still", which E99 s38 found invisible and which no dial may switch off - so a
# smaller number is a REFUSAL by name here, and the player raises one to the floor rather than disagree.
# `test_kinetics_flags.py` reads the module's own constant and holds the two to each other.
PLATE_DRIFT_OPT = "drift"
PLATE_DRIFT_FLOOR = 2.0     # kinetics/idle.mjs IDLE.DRIFT_PX - E49's floor
PLATE_DRIFT_LONG = 20.0     # E99 s63: the named LONG-FORM setting ("maybe 20 px drift"; s55's 30 was the first try)
PLATE_DRIFT_SHORTS = 40.0   # E99 s55: "it might work really well for shorts and certain scenes" (the shorts range is 30-40)
# the geometric ceiling: `.world` is inset -5 %, so past ~96 px of x (and 0.6 * that in y) the plate's own EDGE
# walks onto the stage. 90 keeps the whole walk inside the overhang at 16:9 - measured on the drift lane's own
# three-way proof (`review/assembly/r26-133-drift-idle-paints-nothing/`).
PLATE_DRIFT_MAX = 90.0
DRIFT_IDLES = ("drift", "live")   # the two idle kinds whose pose HAS a dx/dy for an amplitude to size
ARRIVALS = ("spring", "throw", "land", "stamp")   # P47 T1: how a dock or a page's pills ARRIVE (spring = E45's pop, the default)   # R26-20 / E99 s87: `stamp` is remotion-ui RU-2's badge-stamp, PORTED (kinetics/stopaction.mjs `stampXf`) - a clamped scale spring landing while a FREE trailing rotation spring is still unwinding, so the mark rests slightly OFF-SQUARE, with the impact ring on its split shock curves and the exit E50 owes it. It is a MOTION and says nothing about what it carries: a card, a badge or a bare prop may each be stamped. The vector map's `stamp` SPECIES (`SPECIES_STAMP` in `VECMAP_SPECIES`, "and of no other world") keeps its own name: one is an `arrive:` value, the other a species kind, and `test_the_stamp_arrival.py` pins that they never meet
MASSES = ("paper", "metal", "liquid", "ink")      # P47 T1: the material presets (stopaction.mjs MASS) a throw or a landing settles by
DOCK_INKS = ("own", "page")   # E99 s87, OPEN ON THE OPERATOR'S EYE: how a stamped PROP's art is laid down - `own` is the woodblock as it was generated, `page` lays it down in the page's own ink the way a real impression would (the page's ground decides which ink that is: chalk on the charcoal page, charcoal on cream). Both render; neither is the default until the frame is judged - a row that names none gets `own`, the art untouched
MORPH_SHAPES = ("tab", "plate", "card")           # P47 T3: the named prop outline a morph page starts from (`;morph=<shape>`; tab is the default)
PLATE_USES = ("landing", "bridge", "reset")   # E61: the three things a plate is - a landing surface, a bridge, a reset; `;use=<one>` names it on the row
RACE_PATHS = ("eased", "clothoid")   # E91 s1 (R26-78): the path a racing mark takes BETWEEN two period knots - `eased` is the engine as it is (each coordinate on its own easing), `clothoid` is the fit through the SAME knots (P52 T17 arm B). The period clock, the knots and the ranks are identical in both: this names the SHAPE of the move and never its timing, and the operator chose it where the beat wants energy rather than smoothness
PLATE_OPTS = ("idle", "drift", "arrive", "mass", "morph", "then", "card", "use", "pill", "thread", "path", "depth", "plane", "form", "field", "room", "domain", "build", "readability")   # P69 T8 (E99 s97): readability=longform[:bravos|middle|phone]|landscape-phone - the PAGE PROFILE a ledger page is drawn in, and a long form's type preset, the row's word (it wins over the series file's own field); legal on the builders ledger_page.READABILITY_BUILDERS names, refused by name elsewhere   # R26-226 (E99 s82): build=lines[:<s>] - a MULTI-LINE page's series draw one at a time, each whole, its end tag and inline badge landing as it lands (the operator: "draw the first line completely, label it, badge it, draw the 2nd line completely, badge it"); `lines:<s>` names ONE series' seconds, so the page's whole build is N x s   # R26-221 (E99 s81): room=<x>,<y>,<w>,<h> - the rectangle of a PICTURE PLATE a card may stand in, fractions of the stage; a plate's answer to a page's quiet_zone, and what lets `read` then `park` work on a plate   # R26-223 (E99 s81): domain=<ymin>,<ymax> - the y scale a LEDGER PAGE is BORN on, so a hook opens on the two lines' own scale instead of standing four seconds on the object's and rescaling; the object's own domain stays the default   # E99 s55 + s63: drift=<px> - the AMPLITUDE of the plate idle's walk, per scene (20 long form, 30-40 shorts; PLATE_DRIFT_FLOOR 2.0 is the floor, PLATE_DRIFT_MAX 90 the geometric ceiling), refused beside an idle that has no dx/dy   # E99 s35: field=soak|plates|scribble - which GROUND the page's charcoal arrives on, chosen by the sentence's JOB: the two-plate cross-fade for continuity (connecting ideas, speaking across plates), the soak for a new idea or a separator, the scribble as the opt-in back-up   # P58 T5 / E98 s3: form=extruded_bar | tilted_line[:<deg>] - the two 2.5D CHART FORMS, how the page's marks are drawn (a prism per bar; the line on a tilted plane). Opt-in, refused by name when the page's builder cannot draw it, and refused beside plane= (one plane per page)   # P58 T4 / E98 s3: depth=<k> - the page is a card at a DEPTH, taking that share of the camera's move (kinetics/camera.mjs PARALLAX); plane=tilt:<deg>[,<axis>]|quad:<8 numbers> - the surface it is drawn on, projected by the embed grammar's own homography. Both opt-in; the flat page is the reading form   # path=eased|clothoid: E91 s1 - the RACE page's path setting, both shipped, neither discarded (P57 T15)   # thread=<mark key>: HF-16 - ONE mark of the page before this one survives the cut and is the arriving page's ground (P50 T15)   # pill=yes|no|<datum index>: R26-34's tip-riding pill on a dense-line page, popping at that datum (P50 T11)   # card=yes|no: a ledger page keeps the card's rounded corners and a hard-edge shadow at full size (2026-09-08; a snapped page is a card by default)  # the `;key=value` options a plate id may carry
# P48 T4: `;then=<series>:<variant>[:<emphasize>]` names ANOTHER chart the same page can become - a second full
# ledger_page.v1 spec on `world.page_states`, built at load and hidden until a `chart_to` reaches it. Repeat the
# option for a third. STATE_MAX bounds it: a fourth chart is a new page or a card, and the reader's memory says so.
STATE_MAX = 3
DOCK_OPTS = ("arrive", "mass", "centre", "card_aspect", "centre_w", "centre_band", "centre_y", "centre_x", "read", "read_s", "park_s",
             "press", "stack", "behind", "embed", "cutout", "fit", "depth", "prop", "ink")   # R26-246 (b) / E99 s87: prop=True - the payload is a catalogued cutout ADDED TO THE WORLD, bare (no card, no frame, no shadow, no rail); ink=own|page - whether that art keeps its own colour or is laid down in the page's own ink, as a real impression would be (the operator picks on the frame)   # P58 T6 / E98 s4: depth=<k> - the card stands on a LAYER'S plane and takes that share of the one camera's move (kinetics/camera.mjs PARALLAX - the page's own vocabulary and the same range); it composes with behind= and the pair is refused by name when they disagree   # P50 T7: embed=<name> - the card lands ON a surface the plate declares (a poster, a screen, a paper), projected onto its four measured corners   # P50 T15 / HF-17: behind=<layer> - the world plate's foreground cutout paints OVER this card (the depth cue by occlusion, not blur)   # P50 T3: press = the card meta press_card.py wrote (or its path) - the dock is a PRESS CARD; stack = it joins the scene's press pile (the push hand-off, doc 29 s9.27)   # the optional 5th element of a shot row's dock tuple: a dict of these; centre: True parks the card centred on the page; card_aspect: the card's h / w (a chart card), so the centred box is the card's own
CENTRE_MAX_H = 0.58                                 # a centred card takes at most this share of the stage height (the page's title and source stay in view)
CENTRE_W = 0.74                                     # a centred card's width as a share of the stage - the reading size, not the parked card's
CENTRE_BAND = 0.64                                  # ... and is centred in the band ABOVE the caption strip (which sits at ~0.64-0.70 of a portrait stage), never under it
TIMED_EXITS = ("dip", "blurzoom", "melt", "slide", "door")   # (the door's length follows its optional hinge, `door:left:0.9` or `door:0.9` - parse_exit reads it apart, as the slide's is) ... and only these read a suffix as SECONDS (the slide's is its SECOND suffix - the first is the direction, `slide:left:0.8` - so parse_exit reads it apart, as the melt's is) (suck's is a point); the melt's may be its length, `splash`, or its exit point, so parse_exit reads it apart
MELT_S = 1.6            # P52 T9: a melt's default length, species/melt.mjs MELT.S - the two are one dial written twice (as DIP_S is, in the engine and in gate_motion_density), and test_transitions_e47 pins them together
MELT_W_S = 1.15         # R26-118 / E88 s6: the WEIGHT phase's own length, species/melt.mjs MELT.W_S - a `melt:weight` that declares no length runs MELT_S + MELT_W_S (the four beats need their own seconds), and test_transitions_e47 pins that pair too
SLIDE_DIRECTIONS = ("left", "right", "up", "down")   # R26-75 / E87 s3: WHICH WAY the incoming frame pushes the outgoing one off
MELT_G_S = 0.9          # P61 T6 / E99 s2: what the GATHER adds to a melt's default window, species/melt.mjs MELT.G_S - a `melt:gather` that declares no length runs its window plus this (three turns in the sag's own 0.48 s is a jump, not a swirl), and test_melt_gather pins the pair
SLIDE_S = 0.6           # a slide's default length, the player's SLIDE_S - the two are one dial written twice (as DIP_S and MELT_S are)
DOOR_HINGES = ("left", "right", "top", "bottom")   # E98 s7 / R26-134: the stage edge the outgoing world swings open on (kinetics/transitions.mjs DOOR.HINGES)
DOOR_HINGE = "left"     # the default hinge (DOOR.HINGE)
DOOR_S = 0.9            # the door's default length - kinetics/transitions.mjs DOOR.S, one dial written twice (as SLIDE_S is); the derivation lives there
DOOR_S_MIN = 0.45       # DOOR.S_MIN: shorter is a flick, not a door
DOOR_S_MAX = 1.8        # DOOR.S_MAX: longer holds the boundary on a move with no evidence in it (E49)
DOOR_DOCK_TOL = 0.35    # the wipe's own boundary tolerance (the engine's allOut: a card leaving within this of the boundary belongs to the outgoing page)
DEFAULT_EXIT_CHANGE = "dip"         # E47 #3 corrected 2026-09-12 (the operator: "the dip is supposed to be used as an actual transition when the
                                    # scene ACTUALLY changes ... what you said is that the dip was associated with any DOCK, not the dip being
                                    # associated to the scene change"): the natural default when the WORLD changes at the boundary - never for a
                                    # dock, never in front of a signature enter. Was docks -> dip 2026-09-06 -> 09-12, wipe_right before that.
DEFAULT_EXIT_DOCKS = DEFAULT_EXIT_CHANGE   # kept for the record of the old name; docks decide nothing now
DEFAULT_EXIT_BARE = "cut"
SIGNATURE_ENTERS = ("mount", "spiral", "morph")   # E47 #2 (amended 2026-09-12): a page arriving by a signature IS the world change - no dip
                                                  # in front of it by default (the operator: "the dark frame happens at 1:01 on the scene
                                                  # change, the mount starts at 1:02" - the 0.47 s of black before the cream)

TIMELINE_NAME = "steel-and-paper.timeline.json"  # the compiled scene_evidence_timeline.v1 the gate reads
# Per-episode overrides (Tokyo, 2026-09-04): another episode's build script imports this module,
# sets these, and calls main() - the compiler stays ONE thing rather than a fork per episode.
SHOT_TABLE_FILE = "SHOT-TABLE-F.py"
TITLE, SUBTITLE, EPISODE_ID = "Steel and Paper", "Money Physics · answer to Bravos Research", "steel-and-paper"
CONTENT_FORM = None  # Explicit long-form prefixes must not be classified by their short review runtime.
ASPECT = None                      # "9:16" for a short: the template reads timeline.aspect (html[data-aspect])
CLIP_PREFIX = "clip:"              # shot-table plate id for a CLIP world: clip:<path to a silent mp4>
# THE VECTOR MAP (P50 T5; the Bravos world map, shots 57-80). A shot-table plate id `vecmap[:<A3 list>]` is a
# world that is DRAWN, not embedded - the same relation a ledger page has to a plate: 177 country outlines from
# content/video_engine/assets/maps/world-110m.paths.json (Natural Earth 110m, public domain, ids by ISO A3,
# already projected onto a 1000 x 500 equirectangular box by build_world_map.py) painted by
# scripts/species/vecmap.mjs. The id's optional list is the FOCUS SET: the countries this composition frames.
# The FIT is not compiled: the player carries one file for both aspects (render_baseline instantiates the same
# timeline at 16:9 and at 9:16, and test_portrait_parity flips a golden's aspect), so the framing is computed at
# load from the focus set's own bboxes and the live stage - mapFit, one similarity per composition, tested in
# tests/kinetics/vecmap.test.mjs for both aspects. What the compiler owns is what the player must not guess:
# which countries are framed, that every name is real, and that the map data reaches the player ONCE.
VECMAP_KIND = "vecmap"
VECMAP_PREFIX = re.compile(r"^vecmap(?::|;|$)")   # `vecmap`, `vecmap:IRN,USA,CHN`, `vecmap;idle=drift` - never a plate called `vecmap-desk`
WORLD_MAP = "world-110m"                          # the one map on disk; the id names it so a second one is a new name, never a new branch
MAP_PREFIX = "map:"                               # ... and its key in the asset map: `map:world-110m`, written once however many scenes use it
MAPS_DIR = REPO / "content/video_engine/assets/maps"
VECMAP_FOCUS_MAX = 6                              # a focus set of seven countries is the whole world: drop the list (E59: a composition frames its places)
SPECIES_CLIP = "clip"              # world.kind for a clip; the player seeks a <video> to the scene clock
# VIDEO DOCK (ruling E44 / backlog R26-7, operator 2026-09-06: "use the chart plate/ledger AND THEN DOCK
# the animation videos"): a dock asset may be a clip. It embeds raw like a clip world and the player seeks
# it on the same code path (seekVideo); the dock entry declares its kind so the motion gate can credit it.
VIDEO_SUFFIXES = (".mp4", ".webm")
DOCK_KIND_VIDEO = "video"          # written onto the dock entry and the evidence map for a clip asset
DOCK_KIND_IMAGE = "image"          # the default - never written, so an all-image build compiles byte-identically
DOCK_KIND_CUTOUT = "cutout"        # P53 T7 / R26-59: the dock is a CUTOUT - no card, no paper, no border (a head above the crawl is a person, not a document; the chrome is the template's `.dock.cutout`)
DOCK_KIND_PROP = "prop"            # R26-246 owed (b) / E99 s87: the dock is a PROP - a catalogued cutout added to the WORLD as art,
                                   # not evidence in a card. The operator, 2026-09-22: "for props, it doesnt make sense to put them in a
                                   # card, the whole point of a prop is for it to get added to the world; we would either stamp it or throw
                                   # it on." So a prop is BARE - the cutout's chrome-down (no paper, no border, no radius, no padding, no
                                   # backdrop blur, no rail, no card shadow) and NOT its foot mask, which dissolves a bust into its band and
                                   # would fade the base off a building. It arrives by `stamp` or by `throw`, never in a box.
DOCK_KIND_PRESS = "press"          # P50 T3: the card is a HEADLINE cut from a screenshot - it carries its source line and its quoted phrase,
                                   # and the player paints it in the press pass (a fanned stack), never in the two-slot dock loop

# THE ICON SET (P50 T2, rule A2a: sourced, with provenance, never generated). A `chip` names a glyph by file
# stem under content/video_engine/assets/icons/; the provenance of every file - the set, its version, the upstream
# URL and the license - is assets/icons/SOURCES.md. The compiler reads the file, KEEPS ONLY GEOMETRY (the tags and
# attributes below, everything else in the file dropped) and embeds that as the asset map's `icon:<name>`, exactly
# the route a plate or a dock still takes through `data_uri` - so the player stays one self-contained file and the
# painter never receives markup it has to trust.
ICONS_DIR = REPO / "content/video_engine/assets/icons"
ICON_PREFIX = "icon:"
ICON_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ICON_TAGS = ("path", "circle", "rect", "line", "polyline", "polygon", "ellipse")
ICON_ATTRS = ("d", "cx", "cy", "r", "rx", "ry", "x", "y", "width", "height", "x1", "y1", "x2", "y2", "points")
CHIP_STATES = ("on", "crossed")   # a chip lands lit, or lands already crossed (a board read back after the fact)
CHIP_FORMS = ("stamp",)            # opt-in raster prop form; absent keeps the sourced SVG chip contract
STAMP_INKS = ("cream", "charcoal")
STAMP_SIZE_MIN, STAMP_SIZE_MAX, STAMP_SIZE_DEFAULT = 180, 420, 260  # stage px
STAMP_PROP_SIZE_MAX = 700  # approved finance-prop cutouts can occupy a full narrative beat
STAMP_MAX_LINES = 3

# P61 T8 (E93 / E94): THE OPERATOR'S OWN ICON CATALOGUE - the 44 woodblock cutouts, `review_state:
# operator_approved`, `render_eligible: true`. A catalogued cutout is a PICTURE, not geometry, so it rides the
# asset map as `prop:<asset_id>` (a data URI of the file on disk) rather than the `icon:` geometry the chip and
# the count array carry. The engine reads the same key by name (species/agenda.mjs AGENDA.PROP_KEY).
PROP_PREFIX = "prop:"
ICON_CATALOG = ICONS_DIR / "finance_icons_catalog.v1.json"
PROPS_DIR = REPO / "content/video_engine/assets/props"
PROP_CATALOG = PROPS_DIR / "manifest.json"
PROP_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_CATALOG_CACHE: dict[str, dict] | None = None
_PROP_CATALOG_CACHE: dict[str, dict] | None = None


def icon_file(name: str) -> Path:
    """The sourced SVG behind one icon name (existence is the caller's check)."""
    return ICONS_DIR / f"{name}.svg"


def icon_geometry(name: str) -> str:
    """One icon as the asset map carries it: ``{"vb": [x, y, w, h], "el": [{"t", "a"}]}`` as JSON.

    ValueError names the icon when the name is not a file stem we accept, when no file is there
    (source it - never generate one), or when nothing of the file survives the geometry filter."""
    if not (isinstance(name, str) and ICON_NAME.match(name)):
        raise ValueError(f"icon {name!r}: an icon name is lowercase letters, digits and hyphens")
    p = icon_file(name)
    if not p.is_file():
        raise ValueError(f"icon {name!r}: no file at {p} - source one per assets/icons/SOURCES.md, never generate it")
    root = ET.fromstring(p.read_text(encoding="utf-8"))
    box = (root.get("viewBox") or "0 0 24 24").replace(",", " ").split()
    vb = [int(float(v)) if float(v) == int(float(v)) else float(v) for v in box[:4]]
    els = [{"t": tag, "a": attrs} for node in root.iter()
           for tag in [node.tag.split("}")[-1]] if tag in ICON_TAGS
           for attrs in [{k: v for k, v in node.attrib.items() if k in ICON_ATTRS}] if attrs]
    if not els:
        raise ValueError(f"icon {name!r}: {p.name} carries no geometry the player accepts ({'|'.join(ICON_TAGS)})")
    return json.dumps({"vb": vb, "el": els}, separators=(",", ":"))


def icon_catalog() -> dict[str, dict]:
    """The operator's icon catalogue, keyed by `asset_id` (read once). A missing catalogue is a ValueError the
    first caller raises with the path - never a silent empty set."""
    global _CATALOG_CACHE
    if _CATALOG_CACHE is None:
        if not ICON_CATALOG.is_file():
            raise ValueError(f"the icon catalogue is not on disk at {ICON_CATALOG} - E94's 44 cutouts are what a row may name")
        data = json.loads(ICON_CATALOG.read_text(encoding="utf-8"))
        _CATALOG_CACHE = {a["asset_id"]: a for a in data.get("assets", []) if isinstance(a, dict) and a.get("asset_id")}
    return _CATALOG_CACHE


def catalogue_icon(asset_id: str) -> dict:
    """One catalogued cutout's entry, or a ValueError naming the id AND the reason (E93 / E94):

    an id that is not in the catalogue (never invent an image), an entry that is not an `icon`, one the operator
    has not approved (`review_state`), one that is not `render_eligible`, a file that is not on disk, or a file
    whose bytes no longer hash to the sha the catalogue recorded - the record is what makes the picture citable.
    """
    if not (isinstance(asset_id, str) and PROP_ID.match(asset_id)):
        raise ValueError(f"icon {asset_id!r}: an icon id is lowercase letters, digits and hyphens")
    entry = icon_catalog().get(asset_id)
    if entry is None:
        raise ValueError(f"icon {asset_id!r}: not in {ICON_CATALOG.name} - name one of the operator's own cutouts, never invent an image")
    if entry.get("kind") != "icon":
        raise ValueError(f"icon {asset_id!r}: the catalogue calls it a {entry.get('kind')!r}, not an icon")
    if entry.get("review_state") != "operator_approved":
        raise ValueError(f"icon {asset_id!r}: review_state {entry.get('review_state')!r} - only an operator-approved cutout renders (E94)")
    if entry.get("render_eligible") is not True:
        raise ValueError(f"icon {asset_id!r}: render_eligible is {entry.get('render_eligible')!r} - E93: the icons render once the operator approves them")
    p = REPO / (json.loads(ICON_CATALOG.read_text(encoding="utf-8")).get("project_root") or "content/video_engine") / str(entry.get("path") or "")
    if not p.is_file():
        raise ValueError(f"icon {asset_id!r}: the catalogue's path {entry.get('path')!r} is not on disk at {p}")
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    if entry.get("sha256") and sha != entry["sha256"]:
        raise ValueError(f"icon {asset_id!r}: {p.name} hashes {sha[:12]} and the catalogue recorded {str(entry['sha256'])[:12]} - the record and the file disagree")
    return dict(entry, file=p, sha256_measured=sha, _catalogue="icons")


def catalogue_icon_uri(asset_id: str) -> str:
    """One catalogued cutout as the asset map carries it: a data URI of the FILE ON DISK, byte for byte (a
    cutout carries alpha, so it is never re-encoded down a JPEG path the way a plate is)."""
    return data_uri(catalogue_icon(asset_id)["file"])


def prop_catalog() -> dict[str, dict]:
    """The approved 24-cutout ``finance_props_catalog.v1`` registry, keyed by id.

    E99 s31 approves this catalog as a whole; unlike the icon catalog it has no
    per-entry review flags. The committed manifest is the approval record, while
    ``catalogue_prop`` still refuses malformed IDs, paths, missing files and
    byte/hash drift before a prop reaches the asset map.
    """
    global _PROP_CATALOG_CACHE
    if _PROP_CATALOG_CACHE is None:
        if not PROP_CATALOG.is_file():
            raise ValueError(f"the props catalogue is not on disk at {PROP_CATALOG} - E99 s31's approved cutouts are what a stamp may name")
        try:
            data = json.loads(PROP_CATALOG.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"the props catalogue at {PROP_CATALOG} is not readable JSON: {exc}") from exc
        if data.get("schema") != "finance_props_catalog.v1" or not isinstance(data.get("props"), list):
            raise ValueError(f"the props catalogue at {PROP_CATALOG} is not finance_props_catalog.v1")
        rows = {}
        for entry in data["props"]:
            if isinstance(entry, dict) and entry.get("id"):
                rows[entry["id"]] = entry
        _PROP_CATALOG_CACHE = rows
    return _PROP_CATALOG_CACHE


def catalogue_prop(asset_id: str) -> dict:
    """One approved finance prop from ``assets/props/manifest.json``.

    The manifest's path must remain inside the registered cutout directory and
    its recorded SHA-256 must match the on-disk cutout. E99 s31 is the
    catalog-level operator approval; no unrecorded per-entry approval is
    invented here.
    """
    if not (isinstance(asset_id, str) and PROP_ID.match(asset_id)):
        raise ValueError(f"prop {asset_id!r}: a prop id is lowercase letters, digits and hyphens")
    entry = prop_catalog().get(asset_id)
    if entry is None:
        raise ValueError(f"prop {asset_id!r}: not in {PROP_CATALOG.name} - name one of E99 s31's approved cutouts, never invent an image")
    if entry.get("tier") not in ("prop", "mechanism"):
        raise ValueError(f"prop {asset_id!r}: tier {entry.get('tier')!r} is not a registered prop/mechanism cutout")
    raw_path = entry.get("path")
    filename = entry.get("filename")
    if not isinstance(raw_path, str) or not raw_path.startswith("assets/props/cutouts/"):
        raise ValueError(f"prop {asset_id!r}: catalogue path {raw_path!r} is not under assets/props/cutouts")
    if not isinstance(filename, str) or Path(raw_path).name != filename:
        raise ValueError(f"prop {asset_id!r}: catalogue filename {filename!r} does not match path {raw_path!r}")
    # The manifest paths are rooted at content/video_engine (the same
    # resolution used by build_asset_index), not at the repository root.
    p = (REPO / "content/video_engine" / raw_path).resolve()
    root = (PROPS_DIR / "cutouts").resolve()
    try:
        p.relative_to(root)
    except ValueError:
        raise ValueError(f"prop {asset_id!r}: catalogue path {raw_path!r} escapes {root}") from None
    if not p.is_file():
        raise ValueError(f"prop {asset_id!r}: the catalogue's path {raw_path!r} is not on disk at {p}")
    recorded = entry.get("sha256")
    if not isinstance(recorded, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", recorded):
        raise ValueError(f"prop {asset_id!r}: the catalogue must record a 64-character sha256")
    measured = hashlib.sha256(p.read_bytes()).hexdigest()
    if measured.lower() != recorded.lower():
        raise ValueError(f"prop {asset_id!r}: {p.name} hashes {measured[:12]} and the catalogue recorded {recorded[:12]} - the record and file disagree")
    return dict(entry, file=p, sha256_measured=measured, _catalogue="props")


def catalogue_stamp_asset(asset_id: str) -> dict:
    """Resolve a stamp asset from the approved icon or finance-prop catalog."""
    if not (isinstance(asset_id, str) and PROP_ID.match(asset_id)):
        return catalogue_icon(asset_id)  # preserve the legacy icon error wording for malformed IDs
    icons = icon_catalog()
    if asset_id in icons:
        return catalogue_icon(asset_id)
    props = prop_catalog()
    if asset_id in props:
        return catalogue_prop(asset_id)
    # Preserve the established error for an unknown icon/asset (and avoid a
    # generic fallback), while the prop loader remains explicit above.
    return catalogue_icon(asset_id)


def catalogue_stamp_uri(asset_id: str) -> str:
    """Embed an approved icon or finance prop as the stamp's raw image URI."""
    return data_uri(catalogue_stamp_asset(asset_id)["file"])


def _with_stamp_catalogue(entry: dict) -> tuple[dict, dict | None]:
    """Carry the resolver's source catalogue into a compiled chip-stamp species.

    The player only sees the compiled species and its asset URI map. Preserve the
    resolver's distinction there so both runtime guards can apply the same prop
    refusal without guessing from an asset id.
    """
    if entry.get("kind") == "chip" and entry.get("form") == "stamp":
        asset = catalogue_stamp_asset(entry.get("icon"))
        return {**entry, "_catalogue": asset["_catalogue"]}, asset
    return entry, None


def species_props(entry) -> list[str]:
    """Every CATALOGUED raster prop a species carries, in declaration order.

    Agenda-page rows and the opt-in chip ``form: \"stamp\"`` both use the
    operator-approved catalogue; the asset map is keyed ``prop:<asset_id>``.
    """
    if not isinstance(entry, dict):
        return []
    if entry.get("kind") == SPECIES_CHIP and entry.get("form") == "stamp":
        return [entry["icon"]] if isinstance(entry.get("icon"), str) else []
    if entry.get("kind") == SPECIES_AGENDA and entry.get("form") in AGENDA_FORMS:
        return [r["icon"] for r in (entry.get("rows") or []) if isinstance(r, dict) and isinstance(r.get("icon"), str)]
    return []


# Ken Burns: doc 29 §1.4 — the world plate drifts while evidence holds locked,
# so the eye separates narrative world from evidence data with no labelling.
KEN = {"scale": 0.04, "x": 14, "y": -10}

# TARGETED SPECIES (doc 29 s9.27 MOTION MENU, P35 T7). A shot-table row's
# optional 7th element is a list of {"kind", "at", "dur", "target"} dicts;
# `at` and `dur` are episode seconds on the same clock as dock enter/exit.
SPECIES_KINDS = ("punch", "callout", "focus_zoom", "spotlight", "squiggle",
                 "pull_back", "plate_life", "beat_freeze", "radial", "push",
                 "steam", "trace", "ticker",   # STILL LIFE on an approved still (2026-09-05): a region each
                 "life",                       # a DECLARED claim: this world animates on its own for the window (a Remotion render, a
                                               # rendered outro) - the template draws nothing for it; the motion gate credits it as continuous;
                                               # the agent verifies the claim by eye before declaring it (CHECK-RESPONSIBILITIES: declared)
                 "build_to", "bracket", "retitle", "relight",   # PAGE species (P47 T2, build-on): the page performs on a word - a ledger
                                               # page only; build_to caps the drawn series at a datum, bracket spans two data, retitle
                                               # rewrites the title, relight re-fires a bracket or the title (SHOT-TABLE-V3-PROPOSAL part B)
                 "undraw", "figure",           # E50 (P47 T6)
                 "note",                       # the third watch (P47 T7): a line of handwriting in the page's quiet zone, on a word
                 "chart_to",                   # P48: the page's chart BECOMES another chart - the standing state runs its own build
                                               # law backwards (that is what an un-draw is) and the named state then draws on by its
                                               # own law, on the same page, under a title a retitle carries across. Never a cut.
                 "peel",                       # P48 T4: the piece of a share page's named slice leaves the pie on its word, and goes blood red
                 "spread")                     # the fifth watch: the region between two drawn series, bled full of ink on a word (the divergence IS the argument): a chart's deployed life is 6-8 s from its last data mark, 12 s at most - then it
                                               # UN-DRAWS (the line unwinds from where it stands back to a datum, index 0 = to nothing) or BECOMES
                                               # the next thing: a FIGURE the hand writes at a datum's spot (the treasury number the sentence turns to)
SPECIES_FLOW = "flow"     # P50 T4: THE FLOW DIAGRAM (the Bravos flow diagram, shots 82-86) - 2-6 named things inside a dashed
SPECIES_SPAN = "span"     # box, the CLOTHOID arrows between them, and ONE node that swaps on a later word while the rest stands
                          # (the rhyme). SPECIES_SPAN: a shaded stretch of TIME behind a ledger page's chart with its NAME above
                          # it (R26-25, the intake's Archetype 5; Bravos 107-110's "Decades") - a PAGE species, painted by the
                          # page's own perform layer. Both painters are modules: species/flow.mjs and species/span.mjs.
SPECIES_CHIP = "chip"
SPECIES_KINDS += (SPECIES_CHIP,)   # P50 T2: THE ICON CHIP (the Bravos icon board, shots 26-28) - a card with one SOURCED glyph and a
                                   # label, landing on its word and crossed out on a later one. The first species built under the
                                   # operator's module rule (2026-09-11): the painter is scripts/species/chip.mjs, not a branch in the
                                   # template's body; this file still owns its grammar, its targets and its glyph's provenance.
SPECIES_KINDS += (SPECIES_FLOW, SPECIES_SPAN)   # P50 T4 (2026-09-11), both under the module rule
FLOW_NODES = (2, 6)   # a mechanism with ONE part is a chip; with seven it is a diagram nobody reads at phone size
SPECIES_LIGHT, SPECIES_ARC, SPECIES_STAMP = "light", "arc", "stamp"
SPECIES_KINDS += (SPECIES_LIGHT, SPECIES_ARC, SPECIES_STAMP)   # P50 T5: the three species of the VECTOR MAP world, and of no other world.
VECMAP_SPECIES = (SPECIES_LIGHT, SPECIES_ARC, SPECIES_STAMP)   # light: the country's fill rises to the accent and holds (the spotlight's cousin -
                          # a FILL, never a ring: E56). arc: a clothoid from one centroid to another, drawn by length with the nib, an X struck at
                          # its midpoint when the flow is CUT. stamp: a figure written at a place, or a YEAR at the smaller size - `year` is not a
                          # fourth kind, it is `size: "year"` on a stamp (one act - a number put on a place - is one kind, one `when`, one event edge).
STAMP_SIZES = ("figure", "year")
SPECIES_CROSS = "cross"       # P50 T6: the CENSUS's X marks on a TREEMAP page (E53 s1's second amendment, 2026-09-10;
SPECIES_KINDS += (SPECIES_CROSS,)   # Bravos shots 89-91). ONE species carries both halves of the exception - the named
                              # cells take an X (a), and the share they add up to is WRITTEN on the page as a number (b) -
                              # because they are one act, and a subset marked without its share is the area comparison the
                              # ruling refuses. The painter's math is scripts/species/treemap.mjs; the page's perform layer
                              # draws it, as it draws every page species.
TIER_SPECIES = ("build_to", "undraw", "figure", "bracket")   # P50 T9: the page species that may name a TIER - which on a
                              # tiers page IS a series index. One resolution, not two: `tier` is the word the author writes
                              # (a band, not a line), `series` is what the player reads, and the two may not disagree.
BRACKET_FORMS = ("span", "bar")   # P50 T9 / Bravos shot 36: the same measured span drawn as a hairline with ticks, or as a
                              # BAR in the accent - the drop of one tier. A form, not a kind (P50 T3's precedent, the underline).
UNDERLINE_FORM = "underline"   # P50 T3: a callout's FORM - the hand-drawn underline under a press card's quoted phrase (E56's one
                               # exception, the squiggle law s9.27). Not a species kind: the grammar gains a form and a target, not a kind.
SPECIES_COUNT_ARRAY, SPECIES_AGENDA, SPECIES_RING = "count_array", "agenda", "ring"
SPECIES_KINDS += (SPECIES_COUNT_ARRAY, SPECIES_AGENDA, SPECIES_RING)   # P52 T7 / T8, the last three Bravos species
# (EXPLORATION-REVIEW-2026-09-10.md:57 #5, :58 #9, :59 at 7:43), all three under the operator's module rule -
# species/countarray.mjs, species/agenda.mjs, species/ring.mjs, never a branch in the engine's body.
#   count_array  N identical SOURCED icons on a 2:1 rhombus lattice (no perspective cheat, nothing spins), arriving
#                in reading order one per word on the chip's two-spring landing, the COUNT written as the claim.
#   agenda       2-4 numbered rows, each revealed on its own word and holding at a named idle - the review's
#                "`figure` + `note` could compose it", made ONE declaration so the rows cannot drift from the count.
#   ring         the RING'S DASHED-ELLIPSE FORM with an optional flag chip beside it. A FORM, not a new use: E56 is
#                re-stated verbatim below in _validate_ring (a datum, or a label with a digit - else refused), and
#                the hand's closed circle is still the `callout` kind, painted by the engine's own calloutPath.
COUNT_ARRAY_N = (2, 12)   # a count of one is a chip; past a dozen the number is read, not the field (species/countarray.mjs COUNT.MIN/MAX)
COUNT_ARRAY_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
                     10: "ten", 11: "eleven", 12: "twelve"}   # ... and the count may be written in words: "six plants" IS the number
AGENDA_ROWS = (2, 4)      # one row is a note; five is a checklist nobody holds at phone size (species/agenda.mjs)
AGENDA_FORMS = ("page",)  # P61 T8 (E99 s16): the agenda's ONE named form - the plate version of the list; absent = the dock form
AGENDA_PAGE_COVER = 0.55  # ... and what "the page fills its own plate" means: a page form's region takes at least this
                          # share of the frame on BOTH axes, so the corner block R26-80 found can never be called a page
RING_FORMS = ("dashed",)  # the one form the module paints - the closed circle stays the callout's (E56 unchanged)
# the three clocks the grammar has to know to refuse a row that cannot FIT its window. Mirrored from the modules'
# own dials (species/countarray.mjs COUNT.STEP / LAND_S, species/agenda.mjs AGENDA.STEP / NUM_LEAD + ROW_S), which
# stay the source of truth for the motion; these are the compiler's copy of the numbers, and the only thing they
# are used for is arithmetic on the author's `dur`.
COUNT_ARRAY_STEP, COUNT_ARRAY_LAND_S = 0.34, 0.45
AGENDA_STEP, AGENDA_ROW_S = 0.34, 0.54
HOLD_MIN_S = 1.0   # a held species with less room than this before the next event is dropped, not flashed (2026-09-08) [DERIVED: E25 - a light that cannot hold its sentence has nothing to prove]
PAGE_SPECIES = ("build_to", "bracket", "retitle", "relight", "undraw", "figure", "note", "spread", "peel", "chart_to",
                 SPECIES_SPAN, SPECIES_CROSS)   # P50 T4: a span is a page species - it is shaded behind the page's own chart, on the page's own clock and live scale (R26-28)
# ---- R26-219: A NOTE OR FIGURE THE PAGE WROTE LEAVES WITH THE PAGE (2026-09-18, the Steel and Paper H unit) ----
# Measured on the H unit: the railway page's two `note`s and its `-64%` `figure` were still standing on the GDP page
# eight seconds after the recast. A note, a figure, a retitle, a bracket and a spread are PAGE-BOUND - the hand wrote
# them on one page, about that page's marks - so a `chart_to` that REPLACES the page takes them with it. The verbs
# that replace it are the three that re-write the chart into another state; a rescale (the axes retarget), an extend
# (the window grows), a park (the chart makes room) and a compare (a figure the page already wrote becomes the number
# the viewer feels) all keep the SAME page, and nothing leaves on them. The leave is the page's own - PAGE_LEAVE_S,
# the 1.0 s of the vortex's first phase (the engine's LP_RETRACT.COLOURS; CAPABILITIES, the page VORTEX row) - so
# nothing pops. `keep: true` on the species refuses the leave: the note is about the argument, not the page.
PAGE_BOUND_SPECIES = ("note", "figure", "retitle", "bracket", "spread")
PAGE_REPLACING_VERBS = ("recast", "morph", "remake")
PAGE_LEAVE_S = 1.0
CHART_TO_KINDS = ("recast", "rescale", "extend", "park", "morph", "compare", "remake")   # P48: recast (T4, a hand-over; keyed: T4b), rescale (T2), extend (T3), park (T2b: the chart makes room by one affine transform), morph (T5: the area under the line becomes the target's by ARAP); compare (P57 T11 / R26-70: the quoted metric becomes the comparator, E76); remake (P61 T2 / E99 s34: the WHOLE chart becomes the whole chart - the seventh verb, and the only one under which every series, datum, axis, label and the title transform on one clock)
# P61 T2 - THE WHOLE-CHART REMAKE. The six verbs above each transform PART of a chart: a rescale moves its scale, an
# extend its window, a recast hands its axes over while its series are re-written, a morph moves the area under ONE
# line, a park moves the whole thing without changing it, a compare morphs a written figure. E99 s34 asked for the
# one that moves ALL of it, and it needs a correspondence the compiler can see for itself - so a remake is admitted
# on a LINE <-> BARS pair only, and only when the bars ARE the line's own data: its VALUES (bar k is datum i) or,
# failing that, its CHANGES (E64's data key, re-used whole rather than re-derived). Anything else is refused by name
# and told which verb can do it. Figures are never fabricated: a bar merely CLOSE to a datum is a refusal.
REMAKE_PAIRS = (("dense-line", "story"), ("story", "dense-line"))
REMAKE_KEYS = ("level", "change")   # the two honest correspondences: the bar IS the datum, or the bar IS the step into it
MORPH_BUILDERS = ("dense-line",)                     # P48 T5: the shape a morph moves is the AREA UNDER A LINE - both sides of a morph_to are line pages
MORPH_METHODS = ("a", "arap")                        # doc 43 s43.5: A = vertex-based (ring-normalise, resample, rotational alignment, lerp, cubic), B = triangle-based ARAP
# The decision rule (doc 43 s43.5): "outline-to-outline with modest rotation -> Method A ... anything where the prop
# deforms into a chart with real rotation -> Method B", and "start on A; escalate when a shape actually collapses".
# The doc's own number for "real" is 90 deg (where the vertex lerp collapses to zero area); the number the ENGINE can
# act on is TR-7's, 15 deg, because a pair past it is refused outright (below) - so every pair the compiler admits is
# "modest" and defaults to A, and B is reached by naming `method: "arap"` on the row. That is doc 43's escalation,
# written down: the refusal is what makes the default safe.
METHOD_A_MAX_DEG = 15.0   # [DERIVED: arap.mjs ARAP.AXIS_MAX_DEG / the brief B4 - the same limit the refusal enforces]
PARK_ANCHORS = ("top", "bottom", "left", "right")   # the corner of its own box the parked chart shrinks toward (top = Bravos 91: up, the room opens below)
RECAST_PAIRS = (("dense-line", "story"),)             # P48 T4b: the legal KEYED pairs - n lines <-> n bars by series (Bravos 99-105); everything else recasts by the hand-over
RECAST_TAG_PAIRS = (("dense-line", "story"),)        # P50 T11: the legal pairs for `keyed: "tags"` - each series' TERMINAL TAG is the mark that becomes its bar (Bravos 104-105), so the source must be a page that names its lines at their ends
RECAST_KEYS = (True, "tags")                         # P50 T11: `keyed: true` keys the DATUM (the line's end -> the bar's top), `keyed: "tags"` keys the TAG (the name at the end -> the bar's own number); false / absent is the hand-over
# E64 / R26-49 (the operator on Tokyo at 0:50: "it basically just cuts a new chart"): the THIRD key - the DATA. The two
# keys above key a MARK the source page draws (a line's end, the tag at it) and the correspondence IS the series index;
# this one keys a RELATION between two data - bar k is the line's own change from one datum to the next - so it is the
# only key that writes a `key_map`, and the only one that cannot be looked up in a list of builder pairs: Tokyo's pair
# is (dense-line, story), the same builders the series key uses, and only the DATA tell them apart. Hence a RULE
# (`recast_data_key`), not a RECAST_DATA_PAIRS list.
RECAST_DATA_KEY = "data"
RECAST_KEYS_ALL = RECAST_KEYS + (RECAST_DATA_KEY,)   # every legal value of `keyed`: the two MARK keys, and the DATA key
RECAST_DATA_TOL = 0.005                              # 0.5 % of the larger magnitude: a bar and the line's own difference are the SAME
                                                     # number or the pair is not keyed on data - a near-miss is a refusal, never a tween
# P57 T11 / R26-70, E76 (the operator, 2026-09-13: *"showing the P/E and then morphing it to a more visual number would be
# a great repeatable mechanism"*): the METRIC-TO-COMPARATOR morph. The row names the figure the market quotes
# (`metric`), the number the viewer feels (`comparator`), the authored `inputs` and the `derive` arithmetic that turns
# the one into the other - so the comparator is DERIVED in the open and never invented by the engine (E77: figures are
# never fabricated; the `source` string is the row's provenance). Compiler-only in this slice: the engine paints nothing
# for this verb yet.
COMPARE_TOL = 0.005        # 0.5 % of the larger magnitude, RECAST_DATA_TOL's spirit: the derived number and the authored
                           # comparator are the SAME number or the row is refused - a near-miss is a refusal, never a tween
COMPARE_HOLDS = ("metric", "gone")   # after the morph the quoted metric stays legible beside the comparator, or it is gone
# P57 T12b + T12c, the operator's two corrections of T12's counter: HOW the quoted figure leaves before the comparator
# stands at the same datum. `melt` is the DEFAULT and is E76 s5's own words (2026-09-14: "melt it into a ball, then we
# either throw it off the page, splatter it back on to the canvas and build the chart/graph from that, or morph it from
# the ball into the chart") - the figure's outlines sag and BALL UP, and `then` says what becomes of the ball. `streak`
# is T12b's text melt (the glyphs drip where they stand under their own streak filter), kept whole; `collapse` is the
# hand taking the ink back (the undraw law); `count` is T12's counter. Refused by name here and in species/compare.mjs,
# so a typo in a shot table is a refusal, never a silent default.
COMPARE_FORMS = ("melt", "streak", "collapse", "count")
# ... and the ball's ENDING, the three the operator named. Only a form that MAKES a ball has one: `then` on any other
# form is a row about nothing, and is refused rather than ignored.
COMPARE_THENS = ("morph", "splash", "throw")
COMPARE_BALL_FORM = "melt"
COMPARE_SOURCE_TAGS = ("[DERIVED:", "[SOURCE:")   # E77's provenance label, required on the row
PARK_SCALE = (0.3, 0.95)                             # a parked chart is still a chart: never below 0.3 of itself, and 0.95 is not a park; exactly 1.0 is an UN-PARK (2026-09-10)
# SPECIES BY SENTENCE (P50 T1, 2026-09-11; the operator: "do we already have an understanding mapped in docs to how/where to
# know when to use these capabilities?"). One line per kind: WHICH SENTENCE calls for it. The map is
# docs/content-video-engine/SPECIES-BY-SENTENCE.md (its s4 is generated from these two dicts by lint_species_choice.py
# --when --write-doc; the test keeps them equal); the lint reads a shot table against it. Data, not behaviour.
SPECIES_WHEN = {
    "punch": "the sentence lands on ONE named object already on stage (the ring token, a datum, a plate object) and the eye must hit it - punctuation tied to a landing (E51), never filler",
    "callout": "the sentence names a NUMBER or a POINT on a chart to ring (E56: a ring's one use); the label is the sentence's figure",
    "focus_zoom": "after a chart or document has entered, the sentence turns to ONE region of it and holds there dead still",
    "spotlight": "the sentence's focus is a PICTURE or a datum and the rest may dim - the light lands on it and holds until the sentence has a reason to leave (dur 'hold', E25 amended)",
    "squiggle": "a caption WORD span the sentence stresses or strikes, stage mode only - drawn under the word as it is said",
    "pull_back": "a hook that opens on ONE large number, then recontextualizes it - the detail holds, one pull-back reveals the headline around it",
    "plate_life": "a bare world plate with no evidence must live (E21) - our cutouts stepped at 10 fps for the window",
    "beat_freeze": "leaving a chart as a HIT - the final state freezes, then a directional cut (declared in 29 s9.27, NOT built)",
    "radial": "revealing the ring token or a callback object FROM the point the narration names (declared in 29 s9.27, NOT built)",
    "push": "dock A hands off to dock B on the sentence - the evidence hand-off SHIPPED as the press STACK (a dock kind: `press` + `stack`, P50 T3, 2026-09-11): declare a press stack; the `push` species itself stays unbuilt",
    "steam": "STILL LIFE: a named region of an approved still breathes (steam, smoke) so the plate never goes still (E49)",
    "trace": "the sentence NAMES places and flows on a still - a route draws with hops between named points, stamps stack at them",
    "ticker": "STILL LIFE: a tape of figures ticks across a named region of an approved still",
    "life": "a DECLARED claim that this world animates on its own (a rendered clip, the outro) - the gate credits it; the agent verifies by eye",
    "build_to": "the sentence turns to a DATUM before the series' end - the line draws to it and stops (the peak now, the drop on the next sentence)",
    "bracket": "the sentence SPANS two data ('from the peak to June', 'a tenth of the pile') - the hand draws the span, the number is its label, the second thing its sub",
    "retitle": "the sentence renames what the page is about ('The opponent isn't the Fed') - the title rewrites by the hand; a returning page arrives retitled",
    "relight": "the sentence RETURNS to a number already on the page (the ring's echo) - the bracket or the title re-fires",
    "undraw": "the sentence has LEFT the chart's argument (E50) and the next thing is not a chart - the line unwinds to a datum or to nothing",
    "figure": "the sentence TURNS on a number - the hand writes it at its datum's spot (a note when the datum has no room)",
    "note": "the sentence adds a side fact the chart cannot show - a line of handwriting in the page's quiet zone",
    "spread": "the sentence's argument IS the gap between two series (or a series and a rule) - the region bleeds full of ink",
    "peel": "the sentence names a slice of a whole that LEAVES - the share page's slice peels off and goes blood red",
    SPECIES_CHIP: "the sentence names a THING as one of a set (a prediction, an actor, a plant) - a chip lands on its word; RETRACTS crosses it out on a later word (Bravos's icon board)",
    SPECIES_FLOW: "the sentence EXPLAINS a mechanism - A causes B via C - as named things and the arrows between them; a later word SWAPS one node and the rest stands (Bravos's rhyme)",
    SPECIES_LIGHT: "the sentence NAMES a place - the country lights on the word, the spotlight's cousin (a fill, never a ring)",
    SPECIES_ARC: "the sentence NAMES a flow between two places - the arc draws from one to the other on the word; crossed when the flow is cut",
    SPECIES_STAMP: "the sentence puts a NUMBER or a name on a place - the figure writes at the country's centroid",
    SPECIES_CROSS: "the sentence names a SUBSET of a census and what it adds up to - the named cells of a treemap page take an X on the word and the crossed share is written on the page (E53 s1's census exception)",
    SPECIES_SPAN: "the sentence SPANS a period on a chart - a regime, an epoch, 'the decade' - shaded behind the line with its name; a bracket measures two data, a span names a stretch of time",
    SPECIES_COUNT_ARRAY: "the sentence COUNTS a set and the count IS the claim ('six plants', 'twelve refineries') - N identical icons arrive in reading order on an isometric field and the number is written under them",
    SPECIES_AGENDA: "the sentence SETS an agenda ('two numbers', 'three things') - 2 to 4 numbered rows, each revealed on its own word, holding at a named idle until the sentence that takes them one by one",
    SPECIES_RING: "the sentence TURNS on a number and wants the ring as a MARKER - the dashed ellipse round the datum, with an optional flag chip naming it (E56's use unchanged: a number or a point on a chart)",
    "chart_to": "the sentence needs the SAME data at another scale / with more of it / in another form / beside a card - the page changes state (E58; CHART_TO_WHEN names the verb); never a cut to a second chart of it",
}
CHART_TO_WHEN = {
    "recast": "the same data in another form: keyed (n lines -> n bars by series, 'where the four stand today'; RECAST_PAIRS) or the hand-over (a line into the monthly bars, into a pie of the holders)",
    "rescale": "the same series at another scale - 'since February', 'at full width': the window the story is about; never a window that drops the sentence's point",
    "extend": "more of the same series ('and then May') or a later series of the same file ('then consumption') - drawn on at the pen",
    "park": "room for the next thing beside the chart (a card, a second diagram); scale 1.0 is the UN-PARK when the cards leave; it moves no data and restarts no clock",
    "compare": "the sentence quotes the market's figure and then says what it MEANS - the quoted number morphs into the number the viewer feels (E76); the arithmetic is authored, never invented",
    "morph": "a different LINE series in the same frame ('what the Fed charges against what America pays') - the area under the line becomes the target's by ARAP",
    "remake": "the sentence turns the SAME data into the other whole chart ('month by month, this is what it did') - every series, datum, axis, label and the title transform on one clock, line <-> bars; when only the scale, the window or the form changes, the verb is rescale, extend or recast",
}
# P52 T6: THE NEWSREEL BAND (the operator, 2026-09-12: "run the newsreel and then above it we can have either a
# talking news head, actual news footage, or a narrative plate, we don't always have to fill the whole thing with
# text"). A STAGE species on a declared REGION in the lower 40 % of the frame: the band crawls the episode's OWN
# sourced headlines (E68: a clip's label is its on-screen headline; else the dossier's Sources) UNDER whatever
# surface the row docks above it - a head cutout, a clip on E45's springs, or the plate itself. The painter is
# scripts/species/newsreel.mjs (the module rule); this file owns its grammar, its region's law, and the bottom
# STRIP it shares with the caption's E62 band.
SPECIES_NEWSREEL = "newsreel"
SPECIES_KINDS += (SPECIES_NEWSREEL,)
SPECIES_WHEN[SPECIES_NEWSREEL] = ("the sentence reports WHAT WAS SAID OR PRINTED - the wire, the headlines, the tape - the "
                                  "band crawls the sourced headlines under a surface that shows who said it (a head, a clip, "
                                  "the plate); never the whole frame as text")
NEWSREEL_HEADLINE_MAX = 90     # characters: a headline longer than this is a paragraph, and the tape is read at a glance
NEWSREEL_LOW = 0.60            # the band's region sits in the LOWER 40 % of the stage - higher than that it IS the composition
NEWSREEL_BAND_H = 0.14         # [DERIVED: species/newsreel.mjs NEWSREEL.BAND_H] the band's recommended height, as a share of the stage
NEWSREEL_EXIT_S = 0.38         # [DERIVED: species/newsreel.mjs NEWSREEL.BEATS.EXIT_FOR] the retreat, so `hold` + the retreat must fit the window
NEWSREEL_CAP_ABOVE = "above"   # `cap_band: "above"` on the row - the operator's alternative: the crawl takes the caption's own
                               # strip and the caption moves ABOVE the crawl. Absent = this slice's default (the band goes below).
assert set(SPECIES_WHEN) == set(SPECIES_KINDS) and set(CHART_TO_WHEN) == set(CHART_TO_KINDS), "every kind carries a when (P50 T1)"
RESCALE_KEYS = ("ymin", "ymax", "window")   # a rescale names the target DOMAIN: y bounds and/or an x window [from, to]; the state is DERIVED from the page's own series
PATH_SELECTORS = ("all", "tail", "history")   # P47 T9: which strokes a build_to / undraw touches - the highlighted tail (k0 > 0), the history, or all   # a page species whose `at` is BEFORE its scene starts is a STATE: the page arrives in that state
                                                                # (a returning page keeps its retitle, its bracket standing); the gate credits no event before the span
RELIGHT_REFS = ("bracket", "title")
BRACKET_COLORS = ("crimson", "teal", "cobalt", "amber", "deemph", "neg", "pos")
# s9.27 precedence / s9.28 C3: punch, focus zoom, pull-back and Ken Burns are
# mutually exclusive per window - one camera move, never over a Ken Burns drift.
CAMERA_MOVES = ("punch", "focus_zoom", "pull_back")
# P49 T1: THE CAMERA on the timeline - one persistent 2D similarity per scene. A shot row may carry, as its optional 8th
# element, {"keys": [{t, zoom, look, at?, ease?}, ...], "attention": "locked"|"landings"}: `look` is the world point the
# camera looks at and `at` the screen point it lands on ([x, y] stage fractions, or a declared target the player resolves
# at load); a key with no `at` zooms in place. Nothing authored -> identity (Bravos, measured 2026-09-10: LOCKED is the
# default). Keys and a camera species never share a row (s9.28 C3: one camera per window).
CAMERA_EASES = ("cubic", "inout", "linear", "hold")
CAMERA_ARRIVAL_S = 0.45   # the player's SNAP_S: the camera arrival's clock (enter=camera=<dock>), mirrored


def extend_camera_cards(scenes: list[dict]) -> list[str]:
    """P49 T5: a page that arrives by the eye going to its card (enter=camera=<dock>) needs that card ON SCREEN until the
    match - a card whose authored exit is the page's start left the dock list 5 ms before the match (one frame of bare
    world). The card's exit is extended to the arrival's end here, in the timeline, so the player reads a plain span.
    Returns a note per card it moved."""
    notes: list[str] = []
    for i, sc in enumerate(scenes):
        pg = (sc.get("world") or {}).get("page") or {}
        if pg.get("enter") != "camera" or not pg.get("snap_from") or i == 0:
            continue
        end = float(sc["span"][0]) + CAMERA_ARRIVAL_S
        for d in scenes[i - 1].get("docks", []):
            if d.get("slide") == pg["snap_from"] and float(d.get("exit", 0.0)) < end:
                notes.append(f"{d['slide']}: exit {d['exit']} -> {round(end, 2)} (the eye's arrival on {sc.get('scene_id')})")
                d["exit"] = round(end, 2)
    return notes
CAMERA_ATTENTION = ("locked", "landings")


def camera_identity() -> dict:
    return {"keys": [], "attention": "locked"}


def _cam_key_box(look, sw: float, sh: float) -> dict | None:
    """A key's `look` as a WORLD box in stage px: a declared point/region target, a bare [x, y] as a
    point, and None for anything this function cannot place on its own (a `datum` names a spot on a
    page it has not been handed - M24 checks those against the page's real plot at gate time)."""
    if isinstance(look, (list, tuple)) and len(look) == 2:
        return {"x": float(look[0]) * sw, "y": float(look[1]) * sh, "w": 0.0, "h": 0.0}
    if isinstance(look, dict):
        return MG._target_box(look, sw, sh, None)
    return None


def _off_frame_by(fr: dict, box: dict) -> tuple[float, str]:
    """How far outside the frame the box is, and which edge it is past: the shortest push that would
    bring any part of it back on screen."""
    gaps = ((fr["x0"] - (box["x"] + box["w"]), "left"), (box["x"] - fr["x1"], "right"),
            (fr["y0"] - (box["y"] + box["h"]), "top"), (box["y"] - fr["y1"], "bottom"))
    worst = max(gaps, key=lambda g: g[0])
    return max(0.0, worst[0]), worst[1]


def camera_edge_errors(cam, plate_id: str, aspect: str | None = None) -> list[str]:
    """HF-15 / E59 reason 2: the next region is VISIBLE AT THE FRAME'S EDGE before the camera moves.

    E59 gives the camera exactly one reason to pan: "between focal points on a stage wider than the
    frame - a map, a wide diagram: ONE move per composition, then still". The intake's HF-15 names
    what makes such a move read as a move at all: regions ARRIVE. The eye goes to something it can
    already see a piece of, and the thing it leaves goes out by parallax. A key whose target is
    WHOLLY outside the frame the previous key holds is a cut wearing a pan's clothes - for the whole
    length of the move the viewer watches empty stage, and the subject appears from nowhere.

    The frustum is the camera's own: `kinetics/camera.mjs` `camFrustum`, mirrored for Python in the
    motion gate as `camera_frustum`, evaluated at the PREVIOUS key's t - the last frame before the
    move begins. The first key is never refused: before it the camera is the identity, which frames
    the whole stage, so anything a key can name is already on screen.

    Refused only when NOTHING of the target is in frame (`visible == 0`). How much of it has to show
    is a judgement the operator has not made; that nothing at all does is not a judgement."""
    if not isinstance(cam, dict):
        return []
    sw, sh = (1080.0, 1920.0) if (aspect or "16:9") == "9:16" else (1920.0, 1080.0)
    keys = [k for k in (cam.get("keys") or []) if isinstance(k, dict) and isinstance(k.get("t"), (int, float))]
    if len(keys) < 2 or any(k["t"] <= keys[i]["t"] for i, k in enumerate(keys[1:])):
        return []           # unsorted or single-key lists are `validate_camera`'s to refuse first
    errs: list[str] = []
    for i in range(1, len(keys)):
        box = _cam_key_box(keys[i].get("look"), sw, sh)
        if box is None or any(_cam_key_box(k.get("look"), sw, sh) is None and k.get("look") is not None for k in keys[:i]):
            continue        # a look this function cannot place: the frame before it is unknown, so nothing is claimed
        prev = keys[i - 1]
        st = MG.camera_state_at({"camera": {"keys": keys}}, float(prev["t"]), sw, sh, None)
        fr = MG.camera_frustum(st, sw, sh)
        if MG._visible_share(fr, box) > 0:
            continue
        gap, edge = _off_frame_by(fr, box)
        errs.append(
            f"{plate_id}: camera key {i} (t={float(keys[i]['t']):.2f}s) moves to a target that is wholly off-frame at "
            f"key {i - 1} (t={float(prev['t']):.2f}s): that frame shows x[{fr['x0']:.0f}..{fr['x1']:.0f}] "
            f"y[{fr['y0']:.0f}..{fr['y1']:.0f}] at zoom {st['s']:.2f}, and the target sits at "
            f"x[{box['x']:.0f}..{box['x'] + box['w']:.0f}] y[{box['y']:.0f}..{box['y'] + box['h']:.0f}] - "
            f"{gap:.0f}px past the {edge} edge. E59 reason 2 / HF-15: the next region ARRIVES from the frame's "
            "edge; a target the frame cannot show is a cut wearing a pan's clothes")
    return errs


def validate_camera(cam, plate_id: str, aspect: str | None = None) -> list[str]:
    """An authored camera, validated by name: keys in ascending t, zoom > 0, an ease from the set, look/at as stage
    fractions or a declared target, attention from the set. None or the identity pass.

    And, once the names check out, E59 reason 2's own law: every key after the first moves to something
    the frame before it already SHOWS (`camera_edge_errors`, HF-15)."""
    if cam is None:
        return []
    if not isinstance(cam, dict):
        return [f"{plate_id}: camera must be a dict {{keys: [...], attention: locked|landings}}"]
    errs: list[str] = []
    if cam.get("attention", "locked") not in CAMERA_ATTENTION:
        errs.append(f"{plate_id}: camera attention must be one of {'|'.join(CAMERA_ATTENTION)}")
    keys = cam.get("keys", [])
    if not isinstance(keys, list):
        return errs + [f"{plate_id}: camera keys must be a list of {{t, zoom, look, at?, ease?}}"]
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    last = None
    for i, k in enumerate(keys):
        if not isinstance(k, dict) or not num(k.get("t")):
            errs.append(f"{plate_id}: camera key {i}: 't' must be a number (timeline seconds)"); continue
        if last is not None and k["t"] <= last:
            errs.append(f"{plate_id}: camera key {i}: keys must be in ascending t")
        last = k["t"]
        z = k.get("zoom", 1)
        if not num(z) or z <= 0:
            errs.append(f"{plate_id}: camera key {i}: zoom must be a number > 0")
        if k.get("ease", "cubic") not in CAMERA_EASES:
            errs.append(f"{plate_id}: camera key {i}: ease must be one of {'|'.join(CAMERA_EASES)}")
        for fld in ("look", "at"):
            v = k.get(fld)
            if v is None:
                continue
            if isinstance(v, dict):
                errs += [f"{plate_id}: camera key {i}: {fld}: {e}" for e in _validate_target("camera", v, TARGET_KINDS)]
            elif not (isinstance(v, (list, tuple)) and len(v) == 2 and all(num(c) and 0 <= c <= 1 for c in v)):
                errs.append(f"{plate_id}: camera key {i}: {fld} must be [x, y] as stage fractions 0..1 or a declared target")
    # the names are right: now the MOVE itself (E59 reason 2). Only on a clean key list - an unsorted or
    # malformed one has nothing to say about framing until it says what its keys are.
    return errs + (camera_edge_errors(cam, plate_id, aspect) if not errs else [])


def validate_camera_row(cam, row_species, plate_id: str, aspect: str | None = None) -> list[str]:
    """The row's camera against its species: authored keys and a camera species cannot both drive one window,
    and (HF-15) no key moves to a region the frame before it cannot show - which is an ASPECT's question, so
    the build hands its own down."""
    errs = validate_camera(cam, plate_id, aspect)
    moves = [e["kind"] for e in (row_species or []) if isinstance(e, dict) and e.get("kind") in CAMERA_MOVES]
    if isinstance(cam, dict) and cam.get("keys") and moves:
        errs.append(f"{plate_id}: camera keys and a {moves[0]} species on one row - one camera per window (s9.28 C3)")
    elif isinstance(cam, dict) and cam.get("attention") == "landings" and moves:
        errs.append(f"{plate_id}: attention landings and a {moves[0]} species on one row - the landing IS the camera's move (E51, s9.28 C3)")
    return errs


# ---- R26-220 / R26-201: THE REACHABLE ZOOM ON A PAGE (E99 s80 (2), 2026-09-18) -----------------
# `focus_zoom` was a FIXED 1.32 (`kinetics/camera.mjs` CAM.FOCUS_SCALE) and at 16:9 that zoom cut the
# Steel and Paper H page's own title and pushed its y tick column off the frame, so the unit authored a
# 1.06 camera KEY pair instead of the move it wanted. The dial is now the author's (`zoom` on the
# species; a key has always carried its own) and THIS is what bounds it.
#
# THE LAW, and why it is arithmetic and not taste. E99 s80 (2): *"a punch or a camera move may crop the
# page; its crop line falls between elements - each of the title, sub, cite, axis, pill row fully in or
# fully out of the stage at every instant - never through a glyph"*. A zoom is continuous, so an element
# that starts ON the stage cannot reach "fully out" without straddling the edge on the way: "at every
# instant" reduces to EVERY GLYPH WHOLLY ON THE STAGE at the move's deepest zoom. What may be cropped is
# the page's field - the cream, the board, the chart's own ink - which is the thing a punch moves INTO.
# So the ceiling is per element, and one element binds it:
#     screen = at + s * (p - look)      (the camera's own similarity, kinetics/camera.mjs)
#   left   s <= at_x / (look_x - box.x)         right   s <= (W - at_x) / (box.right - look_x)
#   top    s <= at_y / (look_y - box.y)         bottom  s <= (H - at_y) / (box.bottom - look_y)
# A glyph already off the stage at rest cannot be the move's fault and does not bind (the ESTIMATED tag
# column of a dense-line page runs past the frame - `LAND_TAG_REACH` is an upper bound by construction);
# the page's own geometry is R26-205's row, never the camera's.
#
# MEASURED, the H unit's page at 16:9 (`build-h-frozen-g` s01, read read-only; the estimate's boxes,
# looking at the datum's proxy 624,538): the TITLE's top edge binds at 1.089, the y tick column's left
# edge at 1.102, the sub / source / x ticks at 1.120 - so the reachable zoom is 1.08, the authored 1.06
# holds, and the engine's own 1.32 is refused by name. Tokyo v3b measured the same law off the DOM by
# hand (`build_short_v3.py:194-197`: "the left edge binds at S_MAX 1.110 / 1.106"); this is that
# measurement as a compile-time refusal, so no build has to find it on a frame again.
CAMERA_GLYPH_KEYS = ("title", "sub", "source", "rail", "tags")   # the page's own type; `plot` is the field a punch moves INTO
FOCUS_ZOOM_DEFAULT = 1.32   # the engine's own CAM.FOCUS_SCALE (`kinetics/camera.mjs`), mirrored so a refusal can name it and
                            # so `zoom` absent means EXACTLY what every build on disk already renders (test_camera pins the pair)
CAMERA_MOVE_FLOOR = 1.06   # E99 s80 (3): "a zoom under ~1.06 is not a move and stays out" - said in the refusal, never enforced as taste


def page_glyph_boxes(page: dict, aspect: str) -> dict[str, dict]:
    """The page's GLYPH boxes in stage px - what E99 s80 (2) names, and nothing else.

    `page_boxes` reports the page's ink; the chart's two label banks live inside its `plot` box (the y
    tick column left of the data, the x tick labels under it - `_portrait_boxes` and
    `_landscape_full_boxes` both run the plot from the y label down to the tick foot), so they are cut
    back out here by the two constants the box model itself uses. The DATA is not a glyph."""
    boxes = LPG.page_boxes(page, aspect)
    out = {k: dict(boxes[k]) for k in CAMERA_GLYPH_KEYS
           if isinstance(boxes.get(k), dict) and boxes[k]["w"] > 0 and boxes[k]["h"] > 0}
    plot, chart = boxes.get("plot"), boxes.get("chart")
    if plot and chart and plot["x"] > chart["x"]:
        out["y tick column"] = {"x": chart["x"], "y": plot["y"], "w": plot["x"] - chart["x"], "h": plot["h"]}
    if plot and plot["h"] > LPG.XTICK_H:
        out["x tick labels"] = {"x": plot["x"], "y": plot["y"] + plot["h"] - LPG.XTICK_H,
                                "w": plot["w"], "h": LPG.XTICK_H}
    return out


def zoom_ceiling(box: dict, look, at, sw: float, sh: float) -> tuple[float, str]:
    """The largest zoom that keeps `box` WHOLLY on the stage under a camera looking at `look` and landing
    that point at `at` (both stage px; `at == look` is a zoom in place), and the edge that binds it.
    `inf` when no edge does; a box already off the stage returns its own number below 1."""
    lx, ly = float(look[0]), float(look[1])
    ax, ay = float(at[0]), float(at[1])
    caps: list[tuple[float, str]] = []
    if lx > box["x"]:
        caps.append((ax / (lx - box["x"]), "left"))
    if box["x"] + box["w"] > lx:
        caps.append(((sw - ax) / (box["x"] + box["w"] - lx), "right"))
    if ly > box["y"]:
        caps.append((ay / (ly - box["y"]), "top"))
    if box["y"] + box["h"] > ly:
        caps.append(((sh - ay) / (box["y"] + box["h"] - ly), "bottom"))
    return min(caps) if caps else (math.inf, "-")


def page_zoom_ceiling(page: dict, aspect: str, look, at=None) -> tuple[float, str, str, list]:
    """The reachable zoom for a camera move on this page: (zoom, the element that binds it, its edge, the
    whole table). A glyph already off the stage at rest is carried in the table with `at_rest` False and
    does not bind - what the page already does with no camera is not the move's doing."""
    sw, sh = LPG.STAGE_PX[aspect]
    at = tuple(at) if at is not None else tuple(look)
    table = []
    for name, box in page_glyph_boxes(page, aspect).items():
        z, edge = zoom_ceiling(box, look, at, sw, sh)
        table.append({"element": name, "zoom": z, "edge": edge, "box": box, "at_rest": z >= 1.0})
    live = [r for r in table if r["at_rest"]]
    table.sort(key=lambda r: r["zoom"])
    if not live:
        return math.inf, "-", "-", table
    best = min(live, key=lambda r: r["zoom"])
    return best["zoom"], best["element"], best["edge"], table


def page_crop_line_ceiling(page: dict, aspect: str, look, at=None) -> tuple[float, str]:
    """E99 s80 (3) at 16:9: the largest zoom before the page's own CROP LINE lands in the anchored strip.

    At 9:16 the caption YIELDS under the move (`stamp_camera_caption_bands`, E62 for the camera), so the
    strip is not a ceiling there - it moves. At 16:9 the strip is already out of the plot and the caption
    has nowhere to go, so the rule is the page's own: the bottom edge of its drawn extent may sit ABOVE
    the strip (the caption reads under the page) or BELOW its foot (the page covers the strip, which is
    what a full-stage page does), never INSIDE it, where a deckle edge cuts the caption's own band. A page
    whose edge is already in the strip with no camera at all is not the move's fault."""
    if aspect != "16:9":
        return math.inf, "-"
    boxes = LPG.page_boxes(page, aspect)
    strip = boxes["caption_anchor"]
    inked = [boxes.get(k) for k in CAMERA_GLYPH_KEYS + ("chart", "plot")]
    inked = [b for b in inked if isinstance(b, dict) and b["w"] > 0 and b["h"] > 0]
    if not inked:
        return math.inf, "-"
    bottom = max(b["y"] + b["h"] for b in inked)
    ly = float(look[1])
    ay = float(at[1]) if at is not None else ly
    if bottom <= ly or bottom > strip["y"]:
        return math.inf, "-"          # above the look (a zoom cannot walk it down), or already at the strip
    cap = (strip["y"] - ay) / (bottom - ly)
    return (cap, "the page's own bottom edge") if cap >= 1.0 else (math.inf, "-")


def camera_zoom_errors(world, row_species, cam, plate_id: str, aspect: str | None = None) -> list[str]:
    """R26-220: every zoom authored on a LEDGER PAGE row - the `focus_zoom`'s own dial and each camera
    key's - against the reachable zoom, refused BY NAME with the number (E99 s80 (2) and, at 16:9, (3)).

    Nothing is claimed where the compiler cannot place the look (a `span` target, a page the box model
    cannot estimate): the rule `camera_edge_errors` already keeps. A DATUM is placed by the plot's centre,
    the motion gate's own proxy for it (`_cam_point`), so the number is the PAGE's and the refusal prints
    the anchor it read - the engine's resolved mark can only be read off a frame (`window.__camera`)."""
    if not isinstance(world, dict) or world.get("kind") != SPECIES_LEDGER:
        return []
    page = world.get("page")
    if not isinstance(page, dict):
        return []
    asp = aspect or "16:9"
    if asp not in LPG.STAGE_PX:
        return []
    sw, sh = LPG.STAGE_PX[asp]
    try:
        plot = LPG.page_boxes(page, asp).get("plot")
    except Exception:       # a page the box model cannot place: there is nothing to measure a zoom against
        return []
    errs: list[str] = []

    def _check(zoom: float, look, at, door: str) -> None:
        if not (zoom > 1.0):
            return
        z_glyph, element, edge, _table = page_zoom_ceiling(page, asp, look, at)
        z_crop, crop_name = page_crop_line_ceiling(page, asp, look, at)
        z, name = ((z_glyph, f"the {element}'s {edge} edge") if z_glyph <= z_crop else (z_crop, crop_name))
        if z == math.inf or zoom <= z + 1e-9:
            return
        reach = math.floor(z * 100) / 100
        landed = "" if tuple(at) == tuple(look) else f", landed at ({float(at[0]):.0f}, {float(at[1]):.0f})"
        errs.append(
            f"{plate_id}: {door} is past the reachable zoom {reach:.2f} on this page at {asp} - {name} leaves the "
            f"stage at {z:.3f}, looking at ({float(look[0]):.0f}, {float(look[1]):.0f}){landed}. E99 s80 (2): a move "
            "may crop the page - its crop line falls between elements, never through a glyph"
            + (f"; and {reach:.2f} is under the ~{CAMERA_MOVE_FLOOR:.2f} floor, so this page carries no move at this "
               "anchor - park it (E61), or look at something the page has room around"
               if reach < CAMERA_MOVE_FLOOR else ""))

    for e in row_species or []:
        if not isinstance(e, dict) or e.get("kind") != "focus_zoom":
            continue
        z = e.get("zoom")
        if isinstance(z, bool) or not isinstance(z, (int, float)):
            continue        # the dial's own shape is `_validate_entry`'s; an absent dial is the engine's 1.32
        c = MG._cam_point(e.get("target"), sw, sh, plot)
        if c is None:
            continue
        _check(float(z), c, c, f"focus_zoom zoom {float(z):.4g}")
    if isinstance(cam, dict):
        for i, k in enumerate(cam.get("keys") or []):
            if not isinstance(k, dict):
                continue
            z = k.get("zoom", 1)
            if isinstance(z, bool) or not isinstance(z, (int, float)):
                continue
            look = MG._cam_point(k.get("look"), sw, sh, plot)
            if look is None:
                continue
            at = MG._cam_point(k.get("at"), sw, sh, plot) if k.get("at") is not None else look
            _check(float(z), look, at or look, f"camera key {i} (t={float(k.get('t', 0.0)):.2f}s) zoom {float(z):.4g}")
    return errs


TARGET_KINDS = ("datum", "point", "region", "span")
COUNTRY_TARGET, MAPPOINT_TARGET = "country", "mappoint"   # P50 T5: a place on the VECTOR MAP - {"kind": "country", "id": "IRN"} (the
MAP_TARGETS = (COUNTRY_TARGET, MAPPOINT_TARGET)           # outline's own centroid) or {"kind": "mappoint", "x": 640, "y": 165} in MAP BOX
                                                          # units, never stage fractions: the map is the coordinate system, so a declared
                                                          # point stays on the Gulf at either aspect and under any framing. Admitted for the
                                                          # three vecmap species alone - every other species names a stage coordinate.
EMBED_TARGET = "embed"                        # P50 T7 / E59 reason 4: a declared SURFACE of the scene's plate -
                                              # {"kind": "embed", "name": "poster"}; the compiler writes the plate's own
                                              # quad onto it, so the camera punches into the poster BY NAME
# s9.27 targeting law: the target kinds each species may take. () = the species
# needs no target (plate life's target is the plate itself); everything else
# fires only on a declared coordinate - datum index / series point on a page or
# dock, a plate point or region the author names, a caption word span.
SPECIES_TARGETS = {
    "punch": TARGET_KINDS + (EMBED_TARGET,), "callout": TARGET_KINDS + ("phrase",), "focus_zoom": TARGET_KINDS + (EMBED_TARGET,),   # P50 T3: the callout alone may point INSIDE a press card; P50 T7: the CAMERA alone may take a declared surface (E59 reason 4)
    "spotlight": TARGET_KINDS, "squiggle": TARGET_KINDS, "pull_back": TARGET_KINDS + (EMBED_TARGET,),
    "plate_life": (),
    "beat_freeze": ("point", "region"), "radial": ("point", "region"), "push": ("point", "region"),
    "steam": ("region",), "trace": ("region",), "ticker": ("region",),
    "life": (),
    SPECIES_CHIP: ("point", "region"),   # P50 T2: a chip lands where the author declared it - a point, or centred in a region;
                                         # E56 does not reach it (a chip is a card with a glyph, never a ring around a picture)
    SPECIES_FLOW: ("region",),   # P50 T4: a diagram needs its ROOM declared - the box it draws itself inside; a point would leave its size to the painter
    SPECIES_LIGHT: (COUNTRY_TARGET,),                  # P50 T5: a COUNTRY lights - a point cannot (the light is the outline's own fill)
    SPECIES_STAMP: MAP_TARGETS,                        # ... a stamp writes at a country's centroid or at a declared point (a year over the Gulf)
    SPECIES_ARC: (),                                   # ... and an arc names its two ENDS (`from` / `to`), not one target
    SPECIES_SPAN: (),            # ... and a span names its two edges as data, not as a coordinate: the chart owns where they are
    SPECIES_CROSS: (),           # ... and a cross names CELLS, by their labels: the page laid them out, so the page knows where they are
    SPECIES_COUNT_ARRAY: ("point", "region"),   # P52 T7: a field needs its ROOM declared (a region it is centred and scaled inside), or the point it is centred on
    SPECIES_AGENDA: ("point", "region"),        # ... the same for the agenda's block: the rows are laid out inside the box the author gave them
    SPECIES_RING: ("datum", "point", "region"),   # P52 T8: E56's own targets and no others - a datum IS a point on a chart; a point or a region
                                                  # only when the label carries a digit (a stamp whose label is the number); never a caption word
                                                  # span, and never a phrase inside a press card (that is the callout's underline, P50 T3)
    "build_to": ("datum",), "bracket": (), "retitle": (), "relight": (),   # P47 T2: the datum is the cap; the others carry their own fields
    "undraw": ("datum",), "figure": ("datum",), "note": (), "spread": (), "peel": (), "chart_to": (),   # E50; peel names no datum: the slice it pulls is the one the PAGE declared (page.peel.index), so the chart and the claim cannot disagree; spread names its two series, not a datum: the datum the line unwinds back to (0 = nothing); the datum the figure is pinned to
}
SPECIES_TARGETS[SPECIES_NEWSREEL] = ("region",)   # P52 T6: a band needs its STRIP declared - the box it crawls inside; a
                                                  # point would leave the strip's height to the painter, and the strip is the
                                                  # thing the caption has to be reconciled with (the strip law below)
PHRASE_TARGET = "phrase"                      # P50 T3: a region INSIDE a press card - {"kind": "phrase", "dock": "<the press dock's asset id>"}.
TARGET_KINDS_ALL = TARGET_KINDS + (PHRASE_TARGET, EMBED_TARGET) + MAP_TARGETS   # ... admitted for a CALLOUT alone, and only as the underline (E56's one exception); the
                                                     # compiler resolves it to the dock's declared phrase box, the player to stage px through
                                                     # the card's LIVE geometry (a parked or stacked card moves, and the underline moves with it)
TARGET_FIELDS = {"datum": ("index",), "point": ("x", "y"),
                 "region": ("x0", "y0", "x1", "y1"), "span": ("from_word", "to_word"),
                 PHRASE_TARGET: (),   # its one field is `dock`, a name - checked in _validate_callout, where the row's press docks are known
                 EMBED_TARGET: (),    # ... and its one field is `name`, checked below and resolved to the plate's quad at the row
                 COUNTRY_TARGET: (), MAPPOINT_TARGET: ()}   # ... and a map target's fields are MAP units, not 0..1 fractions: _validate_map_target checks them against the map's own box
FRACTION_FIELDS = ("x", "y", "x0", "y0", "x1", "y1")   # plate coordinates as fractions of the frame, 0..1


def _follow_set(v) -> bool:
    """R26-233: is `follow` authored? `0` is a series index, so never `v not in (None, False)` - in Python `0 in
    (None, False)` is True and that form silently dropped the commonest target (the R26-232 lane's finding)."""
    return v is not None and v is not False


def _validate_target(kind: str, target, allowed: tuple) -> list[str]:
    """Errors for one species' target against the kinds it may take (s9.27 targeting law)."""
    if not isinstance(target, dict) or target.get("kind") not in TARGET_KINDS_ALL:
        return [f"{kind}: target must be a dict of kind {'|'.join(TARGET_KINDS)}"]   # `phrase` is a callout's alone (P50 T3) and is named by its own error below
    tk = target["kind"]
    if tk not in allowed:
        return [f"{kind}: target kind {tk!r} not allowed (takes {'|'.join(allowed)})"]
    errs = []
    for f in TARGET_FIELDS[tk]:
        v = target.get(f)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            errs.append(f"{kind}: target {tk} needs numeric {f!r}")
        elif f in FRACTION_FIELDS and not 0.0 <= v <= 1.0:
            errs.append(f"{kind}: target {tk} {f}={v} is not a 0..1 fraction of the frame")
        elif f not in FRACTION_FIELDS and (not isinstance(v, int) or v < 0):
            errs.append(f"{kind}: target {tk} {f}={v!r} is not a non-negative integer index")
    if tk == EMBED_TARGET and not (isinstance(target.get("name"), str) and target["name"].strip()):
        errs.append(f"{kind}: target embed must NAME one of the plate's surfaces ({{'kind': 'embed', 'name': 'poster'}})")
    if tk == "datum" and "series" in target and (isinstance(target["series"], bool)
                                                 or not isinstance(target["series"], int) or target["series"] < 0):
        # R26-218: `not isinstance(v, int)` let `True` through (a bool IS an int in python) and let a negative
        # index through as well. The UPPER bound needs the page's own series count, which this function has not
        # read - that is `check_target_series`, run from `derive_rescale_states` where the page spec is in hand.
        errs.append(f"{kind}: target datum 'series' must be a non-negative integer series index")
    if tk == "span" and not errs and target["from_word"] > target["to_word"]:
        errs.append(f"{kind}: target span from_word > to_word")
    return errs


DERIVE_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Name, ast.Load, ast.Constant,
                ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd)


def derive_compare(expr: str, inputs: dict) -> tuple[float | None, str | None]:
    """P57 T11: the row's `derive` arithmetic over its own authored `inputs` -> (value, error).

    Plain arithmetic and nothing else: + - * / parentheses, unary minus, numbers and the input NAMES. The string is
    parsed and WALKED (ast), never `eval`'d - a call, an attribute, a subscript, a comparison or a name the row did not
    author is refused by name, because the one thing this verb may not do is invent a figure (E77)."""
    if not isinstance(expr, str) or not expr.strip():
        return None, "the arithmetic is empty"
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        return None, f"it does not parse ({exc.msg})"
    for node in ast.walk(tree):
        if not isinstance(node, DERIVE_NODES):
            return None, f"{type(node).__name__} is not plain arithmetic (+ - * / parentheses, unary minus, numbers, the input names)"
        if isinstance(node, ast.Constant) and (isinstance(node.value, bool) or not isinstance(node.value, (int, float))):
            return None, f"the constant {node.value!r} is not a number"
        if isinstance(node, ast.Name) and node.id not in inputs:
            return None, f"it names {node.id!r}, which is not one of the inputs ({', '.join(sorted(inputs)) or 'none authored'})"

    def val(node):
        if isinstance(node, ast.Expression):
            return val(node.body)
        if isinstance(node, ast.Constant):
            return float(node.value)
        if isinstance(node, ast.Name):
            return float(inputs[node.id])
        if isinstance(node, ast.UnaryOp):
            v = val(node.operand)
            return -v if isinstance(node.op, ast.USub) else v
        a, b = val(node.left), val(node.right)
        if isinstance(node.op, ast.Add):
            return a + b
        if isinstance(node.op, ast.Sub):
            return a - b
        if isinstance(node.op, ast.Mult):
            return a * b
        return a / b

    try:
        return float(val(tree)), None
    except ZeroDivisionError:
        return None, "it divides by zero"
    except (TypeError, ValueError, OverflowError) as exc:
        return None, f"it does not evaluate to a number ({exc})"


def _validate_metric_comparator(entry: dict) -> list[str]:
    """P57 T11 / R26-70: the `chart_to compare` row - E76's mechanism as a grammar.

    `metric` is the figure the market quotes, `comparator` the number the viewer feels, `inputs` + `derive` the
    arithmetic between them, `source` the provenance (E77), `form` HOW the quoted figure leaves before the hand
    re-writes the comparator (P57 T12b/T12c: melt - the default ball - streak, collapse, or T12's count; `then` is the
    ball's ending: morph, splash or throw), `hold` what becomes of the
    metric after the morph. Every
    refusal here is a figure the row could not stand behind: a number with no arithmetic, an arithmetic that does not
    reproduce it, a comparator nobody named, a provenance nobody wrote."""
    errs: list[str] = []
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    met, cmp_ = entry.get("metric"), entry.get("comparator")
    if not isinstance(met, dict):
        errs.append("chart_to compare: 'metric' must be {value: <number>, text: '<as quoted, e.g. \'24.8x\'>', "
                    "label: '<what it is>'} - the figure the market quotes (E76)")
        met = {}
    if not isinstance(cmp_, dict):
        errs.append("chart_to compare: 'comparator' must be {value: <number>, text: '<as felt>', label: '<what it "
                    "means>'} - the number the viewer feels (E76)")
        cmp_ = {}
    if not num(met.get("value")):
        errs.append("chart_to compare: metric.value must be a number - the figure the market quotes (E76: a P/E of 24.8x)")
    if not num(cmp_.get("value")):
        errs.append("chart_to compare: comparator.value must be a number - the number the viewer feels (E76: '15 % dearer than its own history')")
    if not isinstance(met.get("text"), str) or not met["text"].strip():
        errs.append("chart_to compare: metric.text must be the figure AS QUOTED ('24.8x') - the string the page's own "
                    "`figure` species writes at its datum before it can morph (E50)")
    if not isinstance(cmp_.get("label"), str) or not cmp_["label"].strip():
        errs.append("chart_to compare: a morph with no comparator label - comparator.label says what the number MEANS, "
                    "and a number nobody named is the multiple this verb exists to retire (E76)")
    for who, d in (("metric", met), ("comparator", cmp_)):
        for f in ("text", "label"):
            if f in d and (not isinstance(d[f], str) or not d[f].strip()):
                errs.append(f"chart_to compare: {who}.{f} must be a non-empty string")
    inputs = entry.get("inputs")
    if not isinstance(inputs, dict) or not inputs:
        errs.append("chart_to compare: 'inputs' must be a non-empty dict of name -> number - the authored figures the "
                    "arithmetic reads (E77: a derived figure says what it was derived FROM)")
        inputs = {}
    else:
        for k, v in inputs.items():
            if not isinstance(k, str) or not k.isidentifier():
                errs.append(f"chart_to compare: input name {k!r} is not a plain name the arithmetic can read")
            if not num(v):
                errs.append(f"chart_to compare: input {k!r} must be a number")
    clean = {k: v for k, v in inputs.items() if isinstance(k, str) and k.isidentifier() and num(v)}
    expr = entry.get("derive")
    if not isinstance(expr, str) or not expr.strip():
        errs.append("chart_to compare: 'derive' must be the arithmetic that turns the inputs into the comparator "
                    "(e.g. \"pe / hist - 1\") - a comparator the row cannot derive is a fabricated figure (E77)")
    elif len(clean) == len(inputs):
        got, why = derive_compare(expr, clean)
        if why:
            errs.append(f"chart_to compare: derive {expr!r} is refused - {why}")
        elif num(cmp_.get("value")):
            want = float(cmp_["value"])
            tol = COMPARE_TOL * max(abs(want), abs(got), 1e-12)
            if abs(got - want) > tol:
                errs.append(f"chart_to compare: derive {expr!r} gives {got:.6g} where comparator.value is {want:.6g} - "
                            f"the arithmetic must reproduce the comparator within {COMPARE_TOL:.1%} of the larger "
                            "magnitude; a near-miss is a refusal, never a tween")
    src_ = entry.get("source")
    if not isinstance(src_, str) or not src_.strip().startswith(COMPARE_SOURCE_TAGS):
        errs.append("chart_to compare: 'source' is required and starts with "
                    f"{' or '.join(COMPARE_SOURCE_TAGS)} - the provenance string E77 asks of a derived figure "
                    "(\"[DERIVED: from <sources>, <how>]\"); figures are never fabricated")
    form = entry.get("form", COMPARE_FORMS[0])
    if form not in COMPARE_FORMS:
        errs.append(f"chart_to compare: form must be one of {'|'.join(COMPARE_FORMS)} (default \"{COMPARE_FORMS[0]}\": the "
                    "quoted figure's outlines SAG and BALL UP, and `then` says what becomes of the ball; \"streak\": P57 "
                    "T12b's text melt, the glyphs dripping where they stand before the hand re-writes the comparator; "
                    "\"collapse\": the hand takes the ink back first; \"count\": E60's counter, T12's form) - P57 T12b + "
                    "T12c, the operator's correction")
    if "then" in entry:
        if form != COMPARE_BALL_FORM:
            errs.append(f"chart_to compare: 'then' is the BALL's ending and only form \"{COMPARE_BALL_FORM}\" makes a ball - "
                        f"this row is form \"{form}\", which has nothing to end (P57 T12c)")
        elif entry.get("then") not in COMPARE_THENS:
            errs.append(f"chart_to compare: then must be one of {'|'.join(COMPARE_THENS)} (default \"{COMPARE_THENS[0]}\": the "
                        "ball becomes the comparator's own glyphs, one ring carried into N by morph_a; \"splash\": it bursts "
                        "onto the page and the hand writes through the splatter; \"throw\": it is thrown off the page and the "
                        "hand writes after it) - E76 s5, the operator's three endings")
    if entry.get("hold", "metric") not in COMPARE_HOLDS:
        errs.append(f"chart_to compare: hold must be one of {'|'.join(COMPARE_HOLDS)} (default \"metric\": the quoted "
                    "figure stays legible beside the comparator; \"gone\": the comparator has the stage)")
    if "state" in entry:
        errs.append("chart_to compare: 'state' is not named - the two numbers ARE the states (the quoted metric and the "
                    "comparator it derives)")
    return errs


def stamp_page_leave(row_species: list, leave_s: float = PAGE_LEAVE_S) -> tuple[list, list, list]:
    """R26-219: stamp the LEAVE of every page-bound species whose page the row's own `chart_to` replaces.

    A `note`, `figure`, `retitle`, `bracket` or `spread` is written on ONE page. The first `chart_to` at or after
    its word whose verb is in `PAGE_REPLACING_VERBS` re-writes that page into another state, so what the hand put
    on the old one retracts with it: the species takes `leave_at` (that row's `at`) and `leave_s` (the page's own
    1.0 s leave), and the player fades it over that clock - one law, decided here, run there.

    Three things happen HERE and not in the player, because a player clock no gate can read is a lie in the
    timeline (the shot table, `gate_motion_density` and M21's deployed life all credit a species for its `dur`):

      * the DUR IS CLAMPED to `page_species_end(e) - at`, so an authored duration never outlasts the page. A note
        authored `dur: 10` under a recast 1.0 s later reads 2.0 s - its 1.0 s on the page plus the page's own
        leave - and the hand writes it inside that.
      * a species whose replacing verb fires on its OWN WORD is DROPPED, not written-then-retracted, the way
        `HOLD_MIN_S` refuses a flash (2026-09-08): the page is gone on the frame the hand would start writing.
      * `keep: true` refuses the whole thing (an authored note that is about the argument, not the page).

    A species already stamped is left alone, and the FIRST replacing verb wins - a second recast cannot revive
    what the first one took. Mutates `row_species` in place (a dropped entry is REMOVED from it) and returns
    ``(stamped, clamped, dropped)``: the entries that took a leave, one ``(kind, authored dur, clamped dur)`` per
    duration the leave shortened, and the entries the page went out from under.
    """
    verbs = [e for e in row_species
             if isinstance(e, dict) and e.get("kind") == "chart_to" and e.get("to") in PAGE_REPLACING_VERBS
             and isinstance(e.get("at"), (int, float)) and not isinstance(e.get("at"), bool)]
    stamped: list = []
    clamped: list = []
    dropped: list = []
    if not verbs:
        return stamped, clamped, dropped
    verbs.sort(key=lambda e: float(e["at"]))

    def is_num(v) -> bool:
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    for e in row_species:
        if not isinstance(e, dict) or e.get("kind") not in PAGE_BOUND_SPECIES or e.get("keep") is True:
            continue
        if "leave_at" in e or not is_num(e.get("at")):
            continue
        ct = next((v for v in verbs if float(v["at"]) >= float(e["at"]) - 1e-9), None)
        if ct is None:
            continue
        if float(ct["at"]) <= float(e["at"]) + 1e-9:   # the page goes on the species' own word: nothing to write
            dropped.append(e)
            continue
        e["leave_at"] = round(float(ct["at"]), 3)
        e["leave_s"] = round(float(leave_s), 3)
        end = page_species_end(e)
        room = None if end is None else end - float(e["at"])
        if is_num(e.get("dur")) and room is not None and float(e["dur"]) > room + 1e-9:
            was, now = float(e["dur"]), round(room, 2)
            e["dur"] = now
            e["leave_clamped"] = True   # the record of why the duration is what it is (the hold pass's `held`)
            clamped.append((e.get("kind"), was, now))
        stamped.append(e)
    for e in dropped:
        row_species.remove(e)
    return stamped, clamped, dropped


def page_series_count(spec: dict) -> int:
    """How many SERIES a ledger page spec draws - what a `series`, a `tier` or a datum target's `series` may name.
    A line page's `series`, a tiers page's `tiers` (P50 T9: a tier IS a series index). 0 means this function cannot
    bound the page - a bars or share page's marks are not series - and nothing is refused on it."""
    if not isinstance(spec, dict):
        return 0
    for key in ("series", "tiers"):
        v = spec.get(key)
        if isinstance(v, list):   # `tiers: true` is the two-band combo's bool key, never a band list
            return len(v)
    return 0


TARGET_SERIES_FIELDS = ("series", "tier")   # the species' own words for the index; the third is target.series
# ... and the kinds whose `series` / `tier` IS a mark index. `chart_to` is the counter-example that earned this set:
# `chart_to extend {series: n, later: true}` names a series the page has NOT drawn yet - the verb reveals it from the
# evidence object - so its `series` is a verb argument, not an index into the page's standing marks.
SERIES_NAMING_SPECIES = TIER_SPECIES + (SPECIES_SPAN,)   # build_to, undraw, figure, bracket + the span


def check_target_series(world: dict, row_species: list) -> None:
    """R26-218: a species may only name a series the PAGE HAS - refused here, where the page's series are known.

    Since R26-218 the player resolves a datum on the series the target NAMES, on the page's active state, and a
    series the page does not have resolves to nothing: the species draws no pixel. That is the right player
    behaviour (never the wrong point - P48 T2) and the wrong build behaviour, because an off-by-one `series` used
    to land on the first line and now lands nowhere at all, silently. So the bound is a build error naming the
    number, the way `chart_to extend`'s `to_index` is.

    The bound is the WIDEST of the page's own chart states, so a recast into a page with more series is not
    refused. A page this function cannot count (a bars or a share page) bounds nothing."""
    if (world or {}).get("kind") != SPECIES_LEDGER:
        return
    states = [(world.get("page") or {})] + list(world.get("page_states") or [])
    n = max([page_series_count(s) for s in states] or [0])
    if n <= 0:
        return
    for sp in (row_species or []):
        if not isinstance(sp, dict):
            continue
        named = ([(f, sp.get(f)) for f in TARGET_SERIES_FIELDS if f in sp]
                 if sp.get("kind") in SERIES_NAMING_SPECIES else [])
        tgt = sp.get("target")
        if isinstance(tgt, dict) and tgt.get("kind") == "datum" and "series" in tgt:
            named.append(("target series", tgt["series"]))
        for field, v in named:
            if isinstance(v, bool) or not isinstance(v, int) or v < 0:
                raise ValueError(f"{sp.get('kind')}: {field} {v!r} is not a non-negative integer series index")
            if v >= n:
                raise ValueError(f"{sp.get('kind')}: {field} {v} is past the page's last series ({n - 1}) - the "
                                 f"page draws {n} series, and since R26-218 a series the page does not have "
                                 "resolves to nothing at all rather than to the first line")


def page_species_end(entry: dict) -> float | None:
    """R26-219: when a page-bound species is off the page, in seconds - `leave_at` plus the page's leave, or None
    for one that stands (nothing replaced its page, or it carries `keep: true`). The number a gate or a test reads."""
    if not isinstance(entry, dict) or not isinstance(entry.get("leave_at"), (int, float)) or isinstance(entry.get("leave_at"), bool):
        return None
    s = entry.get("leave_s")
    return round(float(entry["leave_at"]) + (float(s) if isinstance(s, (int, float)) and not isinstance(s, bool) else PAGE_LEAVE_S), 3)


def _validate_page_fields(kind: str, entry: dict) -> list[str]:
    """P47 T2: the page species' own fields. bracket: integer `from`/`to` (data indices), a `label`, optional `sub`,
    `series`, `color`; retitle: a non-empty `text`; relight: `ref` bracket|title, optional `index`."""
    errs: list[str] = []
    is_idx = lambda v: isinstance(v, int) and not isinstance(v, bool) and v >= 0
    if "keep" in entry:   # R26-219: the opt-out of the page's leave, and only a page-bound species has one
        if not isinstance(entry["keep"], bool):
            errs.append(f"{kind}: keep must be true or false (R26-219: true holds the species through a chart_to that replaces its page)")
        elif kind not in PAGE_BOUND_SPECIES:
            errs.append(f"{kind}: keep is only for a page-bound species ({'|'.join(PAGE_BOUND_SPECIES)}) - nothing else leaves with the page")
    if kind == "bracket":
        for f in ("from", "to"):
            if not is_idx(entry.get(f)):
                errs.append(f"bracket: {f!r} must be a non-negative integer datum index")
        if not isinstance(entry.get("label"), str) or not entry["label"].strip():
            errs.append("bracket: needs a non-empty string label (the measured span says what it measures)")
        if "sub" in entry and not isinstance(entry["sub"], str):
            errs.append("bracket: sub must be a string")
        if "series" in entry and not is_idx(entry["series"]):
            errs.append("bracket: series must be a non-negative integer series index")
        if "color" in entry and entry["color"] not in BRACKET_COLORS:
            errs.append(f"bracket: color must be one of {'|'.join(BRACKET_COLORS)}")
        if "form" in entry and entry["form"] not in BRACKET_FORMS:
            errs.append(f"bracket: form must be one of {'|'.join(BRACKET_FORMS)} (P50 T9: `bar` draws the same measured span as a bar in the accent - the drop of one tier)")
    elif kind == "retitle":
        if not isinstance(entry.get("text"), str) or not entry["text"].strip():
            errs.append("retitle: needs a non-empty string text")
    elif kind == "relight":
        if entry.get("ref") not in RELIGHT_REFS:
            errs.append(f"relight: ref must be one of {'|'.join(RELIGHT_REFS)}")
        if "index" in entry and not is_idx(entry["index"]):
            errs.append("relight: index must be a non-negative integer (which bracket)")
    elif kind == "figure":   # E50: the number the sentence turns to, written by the hand where the line was
        if not isinstance(entry.get("text"), str) or not entry["text"].strip():
            errs.append("figure: needs a non-empty string text (the figure, with its unit - never a bare number)")
        if "sub" in entry and not isinstance(entry["sub"], str):
            errs.append("figure: sub must be a string")
        if "series" in entry and not is_idx(entry["series"]):
            errs.append("figure: series must be a non-negative integer series index")
        if "color" in entry and entry["color"] not in BRACKET_COLORS:
            errs.append(f"figure: color must be one of {'|'.join(BRACKET_COLORS)}")
        if "dy" in entry and (isinstance(entry["dy"], bool) or not isinstance(entry["dy"], (int, float))):
            errs.append("figure: dy must be a number (lines of the figure's own size, negative = up)")
    elif kind == SPECIES_SPAN:   # P50 T4 / R26-25: a stretch of TIME, named. Both edges the same way: two datum
        edges = {}               # indices (integers, the page's own) or two x-fractions of the drawn series (0..1)
        for f in ("from", "to"):
            v = entry.get(f)
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                errs.append(f"span: {f!r} must be a datum index (an integer) or an x-fraction of the series (0..1)")
            elif isinstance(v, int) and v < 0:
                errs.append(f"span: {f}={v} is not a non-negative datum index")
            elif isinstance(v, float) and not 0.0 <= v <= 1.0:
                errs.append(f"span: {f}={v} is not a 0..1 fraction of the drawn series' x extent")
            else:
                edges[f] = v
        if len(edges) == 2:
            if isinstance(edges["from"], int) != isinstance(edges["to"], int):
                errs.append("span: name BOTH edges the same way - two datum indices, or two 0..1 fractions")
            elif not edges["from"] < edges["to"]:
                errs.append(f"span: from {edges['from']} is not before to {edges['to']} - a span names a stretch, not a point")
        if not isinstance(entry.get("label"), str) or not entry["label"].strip():
            errs.append("span: needs a non-empty string label - a span NAMES a stretch of time (a bracket MEASURES two data)")
        if "color" in entry and entry["color"] not in BRACKET_COLORS:
            errs.append(f"span: color must be one of {'|'.join(BRACKET_COLORS)}")
        if "series" in entry and not is_idx(entry["series"]):
            errs.append("span: series must be a non-negative integer series index")
    elif kind == SPECIES_CROSS:   # P50 T6: the census exception's two halves, checked rather than trusted
        cells = entry.get("cells")
        if not isinstance(cells, list) or not cells or not all(isinstance(c, str) and c.strip() for c in cells):
            errs.append("cross: 'cells' must be a non-empty list of cell LABELS - the named subset the sentence crosses out")
        elif len(set(cells)) != len(cells):
            errs.append(f"cross: a cell is named twice in {cells}")
        if not isinstance(entry.get("text"), str) or not entry["text"].strip():
            errs.append("cross: needs 'text' - the crossed SHARE written on the page as a number (E53 s1's census exception (b): "
                        "'3 partners, 41 % of exports'). The X's alone would ask the viewer to compare areas, which is the one "
                        "thing a treemap may not do")
        elif not re.search(r"\d", entry["text"]):
            errs.append(f"cross: text {entry['text']!r} carries no number - the share the crossing adds up to is WRITTEN, so no area has to be estimated (E52)")
        if "color" in entry and entry["color"] not in BRACKET_COLORS:
            errs.append(f"cross: color must be one of {'|'.join(BRACKET_COLORS)}")
    elif kind == "undraw":
        if "series" in entry and not is_idx(entry["series"]):
            errs.append("undraw: series must be a non-negative integer series index")
    if "tier" in entry:   # P50 T9: a TIER is a series index on a tiers page - the author's word for a band
        if not is_idx(entry.get("tier")):
            errs.append(f"{kind}: tier must be a non-negative integer band index (a tier IS a series index on a tiers page)")
        elif kind not in TIER_SPECIES:
            errs.append(f"{kind}: 'tier' belongs to the page species that name a series ({'|'.join(TIER_SPECIES)})")
        elif "series" in entry and is_idx(entry.get("series")) and entry["series"] != entry["tier"]:
            errs.append(f"{kind}: tier {entry['tier']} and series {entry['series']} disagree - a tier IS the series index on a tiers page; name one of them")
    if kind in ("build_to", "undraw") and "paths" in entry and entry["paths"] not in PATH_SELECTORS:
        errs.append(f"{kind}: paths must be one of {'|'.join(PATH_SELECTORS)} (the highlighted tail, the history, or all)")
    elif kind == "chart_to":
        if entry.get("to") not in CHART_TO_KINDS:
            errs.append(f"chart_to: 'to' must be one of {'|'.join(CHART_TO_KINDS)} (the verb the chart changes state by)")
        if entry.get("keyed") not in (None, False) and entry.get("keyed") not in RECAST_KEYS_ALL:
            errs.append("chart_to recast: keyed must be true (the DATUM hands over: the line's end becomes the bar's top), "
                        "\"tags\" (the TERMINAL TAG hands over: the name at the line's end becomes the bar's number, "
                        "P50 T11) or \"data\" (the line's own CHANGE between two consecutive data becomes the bar, E64) - "
                        "absent, the compiler derives the key it can see and the row keeps the plain recast only when the "
                        "two states share nothing (E64)")
        elif entry.get("keyed") not in (None, False) and entry.get("to") != "recast":
            errs.append(f"chart_to {entry.get('to')}: 'keyed' belongs to the RECAST - the verb that shows the same data in another form")
        if entry.get("method") is not None:   # P50 T12: doc 43 s43.5's two methods, named only where there are two
            if entry.get("to") != "morph":
                errs.append(f"chart_to {entry.get('to')}: 'method' belongs to the MORPH (doc 43 s43.5) - no other verb has two")
            elif entry["method"] not in MORPH_METHODS:
                errs.append(f"chart_to morph: method must be one of {'|'.join(MORPH_METHODS)} "
                            "(a = the vertex lerp of doc 43 s43.5 Method A, arap = Method B's triangle solve); "
                            "absent, the compiler chooses by the pair's measured rotation")
        if _follow_set(entry.get("follow")) and entry.get("to") != "rescale":
            errs.append(f"chart_to {entry.get('to')}: 'follow' belongs to the RESCALE - the verb that moves the page's "
                        "own SCALE, and the only one whose clock a drawing line can be (R26-233)")
        if entry.get("to") == "compare":
            # P57 T11: E76's mechanism. Nothing is derived into a page state - the metric and the comparator are the
            # two states, and the arithmetic between them is the author's, checked here rather than trusted (E77).
            errs += _validate_metric_comparator(entry)
            return errs
        if entry.get("to") == "park":
            # P48 T2b: no state is derived - the ACTIVE chart is transformed as one piece; the row names how small and toward which side
            sc = entry.get("scale", 0.72)
            if not isinstance(sc, (int, float)) or isinstance(sc, bool) or not (PARK_SCALE[0] <= sc <= PARK_SCALE[1] or sc == 1.0):
                errs.append(f"chart_to park: scale must be a number in [{PARK_SCALE[0]}, {PARK_SCALE[1]}] (default 0.72) - or exactly 1.0, the UN-PARK that grows the chart back from the standing park")
            if entry.get("anchor", "top") not in PARK_ANCHORS:
                errs.append(f"chart_to park: anchor must be one of {'|'.join(PARK_ANCHORS)} (the side the chart keeps)")
            if "state" in entry:
                errs.append("chart_to park: 'state' is not named - the active chart parks")
            return errs
        if entry.get("to") == "extend":
            # P48 T3: the target carries points the standing chart did not - `to_index` (the page's series-0 index the window
            # grows to) or `series` (a `later: true` series in the file that draws on from its first point); the state is derived
            named = [k for k in ("to_index", "series") if entry.get(k) is not None]
            if len(named) != 1:
                errs.append("chart_to extend: name exactly one of to_index (the datum the window grows to) or series (a later: true series to draw on)")
            if entry.get("to_index") is not None and not (is_idx(entry["to_index"]) and entry["to_index"] > 0):
                errs.append("chart_to extend: to_index must be a positive datum index of the page's first series")
            if entry.get("series") is not None and not (is_idx(entry["series"]) and entry["series"] > 0):
                errs.append("chart_to extend: series must be the index (>= 1) of a later: true series in the page's file")
            if "state" in entry:
                errs.append("chart_to extend: 'state' is derived, not named")
            return errs
        if entry.get("to") == "rescale":
            # P48 T2: a rescale keeps the page's own chart and moves its SCALE - the target state is derived by the compiler
            # from the page's series (window sliced, domain set), never authored as a `then=`; so the row names the domain,
            # not a state index
            named = [k for k in RESCALE_KEYS if entry.get(k) is not None]
            if not named:
                errs.append("chart_to rescale: name the target domain - ymin and/or ymax (numbers) and/or window [from_x, to_x]")
            for k in ("ymin", "ymax"):
                if entry.get(k) is not None and not isinstance(entry[k], (int, float)):
                    errs.append(f"chart_to rescale: {k} must be a number")
            w = entry.get("window")
            if w is not None and not (isinstance(w, (list, tuple)) and len(w) == 2 and all(isinstance(v, (int, float)) for v in w) and w[0] < w[1]):
                errs.append("chart_to rescale: window must be [from_x, to_x] with from < to (the page's own x units)")
            fol = entry.get("follow")
            if _follow_set(fol):
                # R26-233: WHICH line the domain follows. `true` is resolved where the page and the row's own species
                # are in hand (`rescale_follow_series`), exactly as a keyed recast's key is; the grammar here is the
                # shape of the word and the two keys it cannot be written without.
                if fol is not True and not (isinstance(fol, int) and not isinstance(fol, bool) and fol >= 0) \
                        and not (isinstance(fol, str) and fol.strip()):
                    errs.append("chart_to rescale: follow must be true (the series this row's build_to draws), the "
                                "series' NAME, or its non-negative index - the line whose drawn extremum the y "
                                "domain's top tracks frame by frame (R26-233)")
                if entry.get("ymax") is None:
                    errs.append("chart_to rescale: follow needs ymax - the domain's TOP is the end the line pushes "
                                "the scale to, and without it there is nothing for the climb to reach (R26-233)")
                if entry.get("window") is not None:
                    errs.append("chart_to rescale: follow and window on ONE verb - a followed rescale's clock is the "
                                "line's own climb, so an x window would open on that clock for a reason nothing said. "
                                "Move the window to its own rescale (R26-233)")
            if "state" in entry:
                errs.append("chart_to rescale: 'state' is derived from the domain, not named")
            return errs
        idx = entry.get("state")
        if not is_idx(idx) or idx == 0:
            errs.append("chart_to: 'state' must be the index of one of the page's OTHER chart states (1..STATE_MAX-1, "
                        "declared on the plate id as ';then=<series>:<variant>'); 0 is the page's own chart")
        elif idx >= STATE_MAX:
            errs.append(f"chart_to: state {idx} is past STATE_MAX ({STATE_MAX}): a fourth chart is a new page or a card")
    elif kind == "peel":
        pass   # P48 T4: no fields of its own. WHICH piece leaves and what it is worth are the PAGE's (page.peel), validated
               # by ledger_page against E53 s1's bounds; the species only says WHEN. A peel on a page with no peel is inert.
    elif kind == "note":
        if not isinstance(entry.get("text"), str) or not entry["text"].strip():
            errs.append("note: needs a non-empty string text (a line the page writes in its quiet zone)")
    elif kind == "spread":
        if not is_idx(entry.get("from")):
            errs.append("spread: 'from' must be a non-negative integer SERIES index (the drawn line the gap starts at)")
        has_to, has_rule = is_idx(entry.get("to")), is_idx(entry.get("to_rule"))
        if has_to == has_rule:
            errs.append("spread: name exactly one of 'to' (a second series) or 'to_rule' (a reference rule's index) - a gap has two edges")
        if has_to and entry.get("from") == entry.get("to"):
            errs.append("spread: from and to must be different series (a gap needs two lines)")
        if "color" in entry and entry["color"] not in BRACKET_COLORS:
            errs.append(f"spread: color must be one of {'|'.join(BRACKET_COLORS)}")
        if "from_index" in entry and not is_idx(entry["from_index"]):
            errs.append("spread: from_index must be a non-negative integer datum index (where the fill begins)")
    return errs


def _validate_map_target(kind: str, field: str, tg, countries: dict, box: list) -> list[str]:
    """P50 T5: a place on the map, by NAME. A country id that is not in the data and a point outside the
    map's own box are the two ways an author can aim at nothing, and both are named here rather than
    resolving to a silent no-paint in the player."""
    if not isinstance(tg, dict) or tg.get("kind") not in MAP_TARGETS:
        return [f"{kind}: {field} must be a place on the map - {{'kind': 'country', 'id': '<ISO A3>'}} or "
                f"{{'kind': 'mappoint', 'x': <0..{int(box[0])}>, 'y': <0..{int(box[1])}>}}"]
    if tg["kind"] == COUNTRY_TARGET:
        a3 = tg.get("id")
        if not isinstance(a3, str) or a3 not in countries:
            return [f"{kind}: {field} country {a3!r} is not in {WORLD_MAP} (ids are ISO A3, uppercase - assets/maps/SOURCES.md)"]
        return []
    errs = []
    for f, hi in (("x", box[0]), ("y", box[1])):
        v = tg.get(f)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            errs.append(f"{kind}: {field} mappoint needs numeric {f!r} (map units, not a stage fraction)")
        elif not 0 <= v <= hi:
            errs.append(f"{kind}: {field} mappoint {f}={v} is outside the map's {int(box[0])} x {int(box[1])} box")
    return errs


def _validate_vecmap_species(entry: dict) -> list[str]:
    """P50 T5: the three species of the map. The kinds themselves are refused off a vecmap world in
    validate_species, where the row's plate id is known; here each one's own fields are checked by name."""
    kind = entry["kind"]
    try:
        data = world_map()
    except ValueError as exc:   # no map on disk: say so once, against the species that needs it
        return [f"{kind}: {exc}"]
    countries, box = data["countries"], data["box"]
    errs: list[str] = []
    if kind == SPECIES_ARC:
        for f in ("from", "to"):
            if f not in entry:
                errs.append(f"arc: no {f!r} - an arc names the two places it runs between (a flow has an origin and a destination)")
            else:
                errs += _validate_map_target("arc", f, entry[f], countries, box)
        crossed = entry.get("crossed")
        if crossed is not None:
            at, dur = entry.get("at"), entry.get("dur")
            num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
            if not num(crossed):
                errs.append("arc: 'crossed' must be a number (episode seconds, the word the flow is cut on)")
            elif num(at) and crossed <= at:
                errs.append(f"arc: crossed {crossed} is not after at {at} - the flow draws first and is cut on a LATER word")
            elif num(at) and num(dur) and crossed >= at + dur:
                errs.append(f"arc: crossed {crossed} falls outside the arc's window ({at}-{round(at + dur, 3)}s) - it would never fire")
    if kind == SPECIES_STAMP:
        if not isinstance(entry.get("text"), str) or not entry["text"].strip():
            errs.append("stamp: 'text' must be a non-empty string - a stamp puts a FIGURE (or a year) on a place")
        if "size" in entry and entry["size"] not in STAMP_SIZES:
            errs.append(f"stamp: size must be one of {'|'.join(STAMP_SIZES)} (a year is a stamp at the smaller size, not a fourth species)")
    if kind in (SPECIES_LIGHT, SPECIES_STAMP) and isinstance(entry.get("target"), dict) and entry["target"].get("kind") in MAP_TARGETS:
        errs += _validate_map_target(kind, "target", entry["target"], countries, box)
    return errs


def _validate_chip(entry: dict) -> list[str]:
    """P50 T2 chip grammar plus the opt-in approved raster ``stamp`` form."""
    errs: list[str] = []
    form = entry.get("form")
    if form is not None and form not in CHIP_FORMS:
        errs.append(f"chip: form {form!r} is not one of {' | '.join(CHIP_FORMS)} (absent is the sourced SVG chip)")
    if form == "stamp":
        icon = entry.get("icon")
        asset = None
        try:
            asset = catalogue_stamp_asset(icon)
        except (TypeError, ValueError) as exc:
            errs.append(f"chip stamp: {exc}")
        if (asset and asset.get("_catalogue") == "props"
                and not (isinstance(icon, str) and icon.startswith("prop-badge-"))):
            errs.append(f"chip stamp: {icon!r} is a non-badge prop; E99 s87 requires a bare prop "
                        "with arrive: stamp or throw, not the chip form")
        label = entry.get("label")
        if not isinstance(label, str) or not label.strip():
            errs.append("chip stamp: 'label' must be a non-empty string - the prop names the thing it stands for")
        elif len(label.splitlines()) > STAMP_MAX_LINES:
            errs.append(f"chip stamp: 'label' must be at most {STAMP_MAX_LINES} lines")
        size = entry.get("size", STAMP_SIZE_DEFAULT)
        size_max = STAMP_PROP_SIZE_MAX if asset and asset.get("_catalogue") == "props" else STAMP_SIZE_MAX
        if isinstance(size, bool) or not isinstance(size, (int, float)) or not math.isfinite(size) \
                or not STAMP_SIZE_MIN <= size <= size_max:
            errs.append(f"chip stamp: 'size' must be stage px in [{STAMP_SIZE_MIN}, {size_max}]")
        ink = entry.get("ink")
        if ink is not None and ink not in STAMP_INKS:
            errs.append(f"chip stamp: 'ink' must be one of {' | '.join(STAMP_INKS)}")
        if "readability" in entry:
            errs.append("chip stamp: 'readability' is not supported - use ink: 'cream' or 'charcoal'")
        if "state" in entry or "cross_at" in entry:
            errs.append("chip stamp: state/cross_at are not supported - the prop leaves with its authored dur")
        return errs
    if "readability" in entry and entry["readability"] != "landscape-phone":
        errs.append("chip: readability must be 'landscape-phone'")
    icon = entry.get("icon")
    if not isinstance(icon, str) or not ICON_NAME.match(icon):
        errs.append("chip: 'icon' names a sourced glyph under content/video_engine/assets/icons "
                    "(lowercase letters, digits, hyphens) - a chip with no glyph is a blank card")
    elif not icon_file(icon).is_file():
        errs.append(f"chip: icon {icon!r} is not in content/video_engine/assets/icons - "
                    "source it and record it in SOURCES.md (A2a), never generate one")
    if not isinstance(entry.get("label"), str) or not entry["label"].strip():
        errs.append("chip: 'label' must be a non-empty string - a chip names the thing it stands for")
    if "state" in entry and entry["state"] not in CHIP_STATES:
        errs.append(f"chip: state must be one of {'|'.join(CHIP_STATES)}")
    ca = entry.get("cross_at")
    if ca is not None:
        if isinstance(ca, bool) or not isinstance(ca, (int, float)):
            errs.append("chip: 'cross_at' must be a number (episode seconds, the word the claim is retracted on)")
        elif isinstance(entry.get("at"), (int, float)) and not isinstance(entry.get("at"), bool) and ca <= entry["at"]:
            errs.append(f"chip: cross_at {ca} is not after at {entry['at']} - a chip is crossed out on a LATER word")
    return errs


def _validate_icon(where: str, name) -> list[str]:
    """One SOURCED glyph, by name and on disk (A2a). Shared by the chip and by every node of a flow."""
    if not isinstance(name, str) or not ICON_NAME.match(name):
        return [f"{where}: 'icon' names a sourced glyph under content/video_engine/assets/icons "
                "(lowercase letters, digits, hyphens) - a card with no glyph is a blank card"]
    if not icon_file(name).is_file():
        return [f"{where}: icon {name!r} is not in content/video_engine/assets/icons - "
                "source it and record it in SOURCES.md (A2a), never generate one"]
    return []


def _validate_flow(entry: dict) -> list[str]:
    """P50 T4: a flow diagram names 2-6 things by SOURCED glyph, the arrows between them BY NAME, and - at most
    once - the node that SWAPS on a later word while the rest stands (Bravos's rhyme, shots 82-86). Everything
    is checked by name, so a typo in an edge is a build error and never a diagram missing an arrow."""
    errs: list[str] = []
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    nodes, lo, hi = entry.get("nodes"), *FLOW_NODES
    if not isinstance(nodes, list) or not lo <= len(nodes) <= hi:
        return [f"flow: 'nodes' must be a list of {lo}-{hi} {{id, icon, label}} - one thing is a chip, seven is a diagram nobody reads"]
    ids: list[str] = []
    for i, n in enumerate(nodes):
        if not isinstance(n, dict):
            errs.append(f"flow: node {i} must be a dict {{id, icon, label}}")
            continue
        nid = n.get("id")
        if not isinstance(nid, str) or not nid.strip():
            errs.append(f"flow: node {i}: 'id' must be a non-empty string - the edges name it")
        elif nid in ids:
            errs.append(f"flow: node {i}: id {nid!r} is already a node of this diagram - every id is its own")
        else:
            ids.append(nid)
        errs += _validate_icon(f"flow: node {i}", n.get("icon"))
        if not isinstance(n.get("label"), str) or not n["label"].strip():
            errs.append(f"flow: node {i}: 'label' must be a non-empty string - a node names the thing it stands for")
    edges = entry.get("edges")
    if not isinstance(edges, list) or not edges:
        errs.append("flow: 'edges' must be a non-empty list of [from, to] node ids - a diagram with no arrows is a chip board")
    else:
        for j, e in enumerate(edges):
            if not (isinstance(e, (list, tuple)) and len(e) == 2):
                errs.append(f"flow: edge {j} must be [from, to] node ids")
                continue
            for end in e:
                if end not in ids:
                    errs.append(f"flow: edge {j} names {end!r}, which is not one of this diagram's nodes ({', '.join(ids) or 'none'})")
            if e[0] == e[1]:
                errs.append(f"flow: edge {j} runs from {e[0]!r} to itself")
    if "tag" in entry and (not isinstance(entry["tag"], str) or not entry["tag"].strip()):
        errs.append("flow: 'tag' must be a non-empty string - the year the diagram is stamped with")
    errs += _validate_flow_extensions(entry, ids)
    sw = entry.get("swap")
    if sw is None:
        return errs
    if not isinstance(sw, dict):
        return errs + ["flow: 'swap' must be a dict {at, node, icon, label}"]
    at, sat, dur = entry.get("at"), sw.get("at"), entry.get("dur")
    if not num(sat):
        errs.append("flow: swap 'at' must be a number (episode seconds - the word one part of the mechanism changes on)")
    elif num(at) and sat <= at:
        errs.append(f"flow: swap at {sat} is not after at {at} - a node swaps on a LATER word (Bravos's rhyme)")
    elif num(at) and num(dur) and sat >= at + dur:
        errs.append(f"flow: swap at {sat} falls outside the diagram's window ({at}-{round(at + dur, 3)}s) - it would never fire")
    if sw.get("node") not in ids:
        errs.append(f"flow: swap names node {sw.get('node')!r}, which is not one of this diagram's nodes ({', '.join(ids) or 'none'})")
    errs += _validate_icon("flow: swap", sw.get("icon"))
    if not isinstance(sw.get("label"), str) or not sw["label"].strip():
        errs.append("flow: swap 'label' must be a non-empty string - the new part names itself")
    return errs


def _validate_flow_extensions(entry: dict, ids: list[str]) -> list[str]:
    """Opt-in formula/connectivity clocks; absent fields retain legacy behavior.

    Timing mirrors species/flow.mjs: initial tag must finish before a change;
    each change retracts for .30s then draws each new edge for .34s.
    """
    errs: list[str] = []
    finite = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
    if "readability" in entry and entry["readability"] != "landscape-phone":
        errs.append("flow: readability must be 'landscape-phone'")
    edges = entry.get("edges")
    if "operators" in entry:
        ops = entry["operators"]
        if not isinstance(ops, list) or not isinstance(edges, list) or len(ops) != len(edges) or not ops or any(op != "-" for op in ops):
            errs.append("flow: operators must contain one '-' per edge")
        ordered = [[a, b] for a, b in zip(ids, ids[1:])]
        if edges != ordered:
            errs.append("flow: formula edges must join adjacent nodes in declared order")
        if "edge_states" in entry:
            errs.append("flow: operators and edge_states are mutually exclusive")
    if "edge_states" not in entry:
        return errs
    states = entry["edge_states"]
    if not isinstance(states, list) or not states:
        return errs + ["flow: edge_states must be a non-empty list of {at, edges}"]
    at, dur = entry.get("at"), entry.get("dur")
    if not finite(at) or not finite(dur) or dur <= 0:
        return errs + ["flow: edge_states requires finite at and positive finite dur"]
    # flowClock.tagEnd, including CHIP.LAND_S=.55 and the optional tag's clock.
    previous_end = at + .9 * .55 + (len(entry["nodes"]) - 1) * .2 + .55 + .1 + (len(edges) if isinstance(edges, list) else 0) * .34 + .12 + .5
    for i, state in enumerate(states):
        prefix = f"flow: edge_states[{i}]"
        if not isinstance(state, dict):
            errs.append(f"{prefix} must be a dict {{at, edges}}")
            continue
        stamp, changed = state.get("at"), state.get("edges")
        valid_edges = isinstance(changed, list) and bool(changed)
        if not valid_edges:
            errs.append(f"{prefix} edges must be a non-empty list of [from, to]")
        else:
            for j, edge in enumerate(changed):
                if not isinstance(edge, (list, tuple)) or len(edge) != 2:
                    errs.append(f"{prefix} edge {j} must be [from, to]")
                elif any(endpoint not in ids for endpoint in edge) or edge[0] == edge[1]:
                    errs.append(f"{prefix} edge {j} must connect two distinct known node ids")
        if not finite(stamp):
            errs.append(f"{prefix} at must be finite episode seconds")
            continue
        if stamp < previous_end:
            errs.append(f"{prefix} must follow the previous build/change (earliest {previous_end:.3f}s)")
        end = stamp + .30 + (len(changed) if valid_edges else 0) * .34
        if stamp <= at or end > at + dur:
            errs.append(f"{prefix} complete change must fit inside the diagram window")
        previous_end = end
    return errs


@functools.lru_cache(maxsize=2)
def world_map(name: str = WORLD_MAP) -> dict:
    """The committed map as data: ``{"box": [w, h], "countries": {A3: {name, centroid, bbox, paths}}}``.

    Read once per build (the file is 187 KB and the same for every scene). ValueError names the map when
    the file is not there - it is built by scripts/build_world_map.py, which is the only thing allowed to
    fetch, and the contract it writes is pinned by tests/test_world_map.py."""
    p = MAPS_DIR / f"{name}.paths.json"
    if not p.is_file():
        raise ValueError(f"map {name!r}: no file at {p} - run scripts/build_world_map.py")
    return json.loads(p.read_text(encoding="utf-8"))


def world_map_json(name: str = WORLD_MAP) -> str:
    """The map as the asset map carries it: the file's own bytes as text, under ``map:<name>``. The player
    parses it once (species/vecmap.mjs memoises by the string), so the whole world costs one asset."""
    return json.dumps(world_map(name), separators=(",", ":"))


def parse_vecmap_id(plate_id: str) -> list[str]:
    """``vecmap[:<A3>[,<A3>...]]`` -> the FOCUS SET, in the order the author wrote it (may be empty: the
    whole world). ValueError names the id; the caller names the row."""
    body = plate_id.split(":", 1)[1] if ":" in plate_id else ""
    ids = [p.strip() for p in body.split(",") if p.strip()] if body.strip() else []
    if len(ids) > VECMAP_FOCUS_MAX:
        raise ValueError(f"{plate_id!r}: {len(ids)} countries in focus is past VECMAP_FOCUS_MAX ({VECMAP_FOCUS_MAX}) - "
                         "a composition frames its places; for the whole world write `vecmap`")
    known = world_map()["countries"]
    for i, a3 in enumerate(ids):
        if a3 not in known:
            raise ValueError(f"{plate_id!r}: focus {a3!r} is not a country in {WORLD_MAP} "
                             "(ids are ISO A3, uppercase - see assets/maps/SOURCES.md)")
        if a3 in ids[:i]:
            raise ValueError(f"{plate_id!r}: focus {a3!r} is named twice")
    return ids


def species_icons(entry) -> list[str]:
    """Every SOURCED glyph one species entry carries, in declaration order: the chip's one (P50 T2), a flow's
    nodes and its swap (T4). The asset map is keyed ``icon:<name>`` - the geometry travels in the player,
    never a path to a file on disk."""
    if not isinstance(entry, dict):
        return []
    if entry.get("kind") == SPECIES_CHIP and entry.get("form") != "stamp":
        return [entry["icon"]] if isinstance(entry.get("icon"), str) else []
    if entry.get("kind") == SPECIES_COUNT_ARRAY:   # P52 T7: the field's ONE glyph, drawn N times
        return [entry["icon"]] if isinstance(entry.get("icon"), str) else []
    if entry.get("kind") == SPECIES_RING:          # P52 T8: the flag chip's glyph, when the ring carries a flag
        return [entry["flag_icon"]] if entry.get("flag") and isinstance(entry.get("flag_icon"), str) else []
    if entry.get("kind") == SPECIES_FLOW:
        out = [n["icon"] for n in (entry.get("nodes") or []) if isinstance(n, dict) and isinstance(n.get("icon"), str)]
        sw = entry.get("swap")
        if isinstance(sw, dict) and isinstance(sw.get("icon"), str):
            out.append(sw["icon"])
        return out
    return []


CALLOUT_FORMS = (UNDERLINE_FORM,)   # P50 T3: the one form a callout takes besides the ring


def _validate_callout(entry: dict, press_docks: dict | None) -> list[str]:
    """E56 as code, with P50 T3's single exception.

    E56 (the operator, 2026-09-09): a ring circles a NUMBER or a POINT ON A CHART; a picture's focus is
    a light. The exception the plan opens is an UNDERLINE on a QUOTED PHRASE - the squiggle law (doc 29
    s9.27 "Squiggle marks") - declared as ``{"kind": "phrase", "dock": "<press dock id>"}`` with
    ``form: "underline"``. A callout on a press card with no form is a ring around a picture, and E56
    still refuses it by name. ``press_docks`` is the row's press docks by asset id; without it a phrase
    target names nothing and is refused, which is the safe direction."""
    tgt, form = entry.get("target"), entry.get("form")
    if form is not None and form not in CALLOUT_FORMS:
        return [f"callout: form {form!r} is not one of {'|'.join(CALLOUT_FORMS)}"]
    if not isinstance(tgt, dict):
        return []
    if tgt.get("kind") == PHRASE_TARGET:
        errs = []
        dock = tgt.get("dock")
        if not isinstance(dock, str) or not dock.strip():
            errs.append("callout: target phrase must name its card - {'kind': 'phrase', 'dock': '<the press dock's asset id>'}")
        elif not (press_docks or {}).get(dock):
            errs.append(f"callout: target phrase names dock {dock!r}, which is not a PRESS dock on this row - "
                        "a phrase is a region of a press card (P50 T3)")
        if form != UNDERLINE_FORM:
            errs.append("callout: a ring circles a NUMBER or a POINT ON A CHART (E56) - on a press card the one exception is "
                        f'form: "{UNDERLINE_FORM}" on the quoted phrase (the squiggle law, s9.27); a ring on a card is refused')
        return errs
    if form is not None:
        return [f"callout: form {form!r} is the press card's underline (P50 T3) - it takes a phrase target, "
                f"not a {tgt.get('kind')}"]
    if tgt.get("kind") != "datum" and not re.search(r"\d", str(entry.get("label", ""))):
        # a datum target IS a point on a chart; a stamp whose label is a number IS the number; a ring
        # around a picture's point or region is the cheap call-out the ruling refuses - the focus there is a light
        return [f"callout: a ring circles a NUMBER or a POINT ON A CHART (E56) - this one targets a {tgt.get('kind')} "
                f"with no numeric label; use a spotlight (the light) on a picture"]
    return []


def _validate_newsreel(entry: dict) -> list[str]:
    """P52 T6: the newsreel row's own grammar.

    `headlines` is the crawl and it is SOURCED - a non-empty list of non-empty strings, each short enough to be
    read as one line of tape (the author reads them off the dossier's Sources or the clips' `candidates.json`;
    nothing here invents one). `strap` and `dateline` are strings the author wrote - a dateline is never a clock
    this build reads, because a rendered frame would then say a different day every time it is rendered. `hold`
    is the LIFE (the band stands, then retreats) and must leave its retreat inside the window. `cap_band` names
    the one way out of the strip clash (`NEWSREEL_CAP_ABOVE`), and the region must sit low."""
    errs: list[str] = []
    heads = entry.get("headlines")
    if not isinstance(heads, (list, tuple)) or not heads:
        errs.append("newsreel: `headlines` must be a non-empty list of the episode's own SOURCED headlines "
                    "(the dossier's Sources, or a clip's on-screen headline - never invented)")
    else:
        for n, h in enumerate(heads):
            if not isinstance(h, str) or not h.strip():
                errs.append(f"newsreel: headline {n} is {h!r} - every headline is a non-empty string")
            elif len(h.strip()) > NEWSREEL_HEADLINE_MAX:
                errs.append(f"newsreel: headline {n} is {len(h.strip())} characters - the tape is read at a glance, "
                            f"{NEWSREEL_HEADLINE_MAX} at most (cut it to its claim, or give the band a second row)")
    for f in ("strap", "dateline"):
        v = entry.get(f)
        if v is not None and (not isinstance(v, str) or not v.strip()):
            errs.append(f"newsreel: `{f}` is {v!r} - a string the AUTHOR wrote, or absent (no clock is invented)")
    if "speed_px_s" in entry:
        v = entry["speed_px_s"]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
            errs.append(f"newsreel: speed_px_s {entry['speed_px_s']!r} must be a positive number of stage px per second")
    if entry.get("hold") is not None:
        v = entry["hold"]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
            errs.append(f"newsreel: hold {v!r} must be a positive number of seconds (the band's LIFE), or absent")
        elif isinstance(entry.get("dur"), (int, float)) and not isinstance(entry.get("dur"), bool) \
                and v + NEWSREEL_EXIT_S > float(entry["dur"]) + 1e-9:
            errs.append(f"newsreel: hold {v}s + the retreat {NEWSREEL_EXIT_S}s does not fit the window dur {entry['dur']}s - "
                        "the band would be cut off mid-retreat; shorten the hold or lengthen the row")
    if entry.get("cap_band") is not None and entry["cap_band"] != NEWSREEL_CAP_ABOVE:
        errs.append(f"newsreel: cap_band {entry['cap_band']!r} is not {NEWSREEL_CAP_ABOVE!r} - the one way out of the strip "
                    "clash is to give the caption its band ABOVE the crawl")
    tgt = entry.get("target")
    if isinstance(tgt, dict) and tgt.get("kind") == "region" and isinstance(tgt.get("y0"), (int, float)) \
            and not isinstance(tgt.get("y0"), bool) and tgt["y0"] < NEWSREEL_LOW:
        errs.append(f"newsreel: the band's region starts at y0={tgt['y0']} - a band is a STRIP in the lower "
                    f"{round((1 - NEWSREEL_LOW) * 100)} % of the frame (y0 >= {NEWSREEL_LOW}); the surface above it is the composition")
    return errs


def _count_in_claim(count: int, claim: str) -> bool:
    """Is the COUNT actually in the claim's own words - as a numeral, or as the word for it? P52 T7's whole
    refusal: a field of six icons under the words "the plants" is a picture of a number nobody said."""
    if re.search(r"(?<!\d)" + str(count) + r"(?!\d)", claim):
        return True
    word = COUNT_ARRAY_WORDS.get(count)
    return bool(word and re.search(r"\b" + word + r"\b", claim, re.I))


def _validate_count_array(entry: dict) -> list[str]:
    """P52 T7: the isometric count array. A SOURCED glyph, a count inside the bound, a claim that CARRIES the
    count, and a field whose last icon lands before the window ends.

    The refusal the plan names - "a count with no number in the sentence is refused" - is enforced against the
    row's own claim, because that is the only sentence text the compiler has at this point: `validate_species`
    is a pure check on ONE shot-table row (the take's `sentences` live in the build's timeline.json, and the
    lint - lint_species_choice.py - is what reads a row against the sentence it falls in). The claim is written
    on the field by the painter, so a claim that carries the count is a number the viewer both hears and reads."""
    errs: list[str] = []
    n = entry.get("count")
    lo, hi = COUNT_ARRAY_N
    if isinstance(n, bool) or not isinstance(n, int):
        errs.append(f"count_array: 'count' must be an integer ({lo}-{hi}) - the count IS the claim")
        n = None
    elif not lo <= n <= hi:
        errs.append(f"count_array: count {n} is outside {lo}-{hi} - one icon is a chip, and past {hi} nobody counts a field")
    errs += _validate_icon("count_array", entry.get("icon"))
    claim = entry.get("claim")
    if not isinstance(claim, str) or not claim.strip():
        errs.append("count_array: 'claim' must be a non-empty string - the count is written under the field as the claim")
    elif isinstance(n, int) and not _count_in_claim(n, claim):
        errs.append(f"count_array: the claim {claim!r} does not say {n} - a count with no number in the sentence is "
                    f"refused (P52 T7): write the count as a numeral or as the word for it")
    step = entry.get("step")
    if step is not None and (isinstance(step, bool) or not isinstance(step, (int, float)) or step <= 0):
        errs.append("count_array: 'step' must be a positive number (the seconds between two icons' words)")
    elif isinstance(n, int) and isinstance(entry.get("dur"), (int, float)) and not isinstance(entry.get("dur"), bool):
        gap = step if isinstance(step, (int, float)) and not isinstance(step, bool) else COUNT_ARRAY_STEP
        need = (n - 1) * gap + COUNT_ARRAY_LAND_S
        if need > entry["dur"]:
            errs.append(f"count_array: {n} icons {gap}s apart need {need:.2f}s but the window is {entry['dur']}s - "
                        "the last icon would land after the field has gone")
    return errs


def _agenda_page_errors(entry: dict, rows: list) -> list[str]:
    """P61 T8 - THE PAGE FORM's own rules (E99 s16, E93, E94), and the dock form's refusals of its words.

    A form word that is not `page` is refused BY NAME; a page form parked in a corner is refused with the box it
    was given (E99 s16: the page fills its own plate); a page row's `icon` must be a catalogued cutout the
    operator approved and the engine may render (E93 / E94), and the dock form has no icon and no title to give.
    """
    errs: list[str] = []
    form = entry.get("form")
    if form is not None and (not isinstance(form, str) or form not in AGENDA_FORMS):
        return [f"agenda: form {form!r} is not one the agenda has - {' | '.join(AGENDA_FORMS)} (absent is the dock form)"]
    page = form in AGENDA_FORMS
    if not page:
        if entry.get("title") is not None:
            errs.append("agenda: 'title' belongs to the page form - a docked block has no title's room (form: \"page\")")
        for i, row in enumerate(rows):
            if isinstance(row, dict) and row.get("icon") is not None:
                errs.append(f"agenda: row {i + 1} names an icon, which is the page form's stamp (E93) - write form: \"page\"")
        return errs
    tgt = entry.get("target") or {}
    if tgt.get("kind") == "region":
        try:
            w = float(tgt["x1"]) - float(tgt["x0"])
            h = float(tgt["y1"]) - float(tgt["y0"])
        except (KeyError, TypeError, ValueError):
            w = h = None
        if w is not None and (w < AGENDA_PAGE_COVER or h < AGENDA_PAGE_COVER):
            errs.append(f"agenda: the page form's region is {w:.2f} x {h:.2f} of the frame and the page fills its own "
                        f"plate - at least {AGENDA_PAGE_COVER:.2f} on both axes (E99 s16), or drop `form` and dock it")
    else:
        errs.append("agenda: the page form is laid out inside a REGION - a point gives the page no box to fill")
    if entry.get("title") is not None and (not isinstance(entry["title"], str) or not entry["title"].strip()):
        errs.append("agenda: 'title' must be a non-empty string - the title says what the list IS (the test card's own lesson)")
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        icon = row.get("icon")
        if icon is None:
            errs.append(f"agenda: row {i + 1} carries no icon - E93: an agenda row carries an icon, stamped on once its sentence has been read")
            continue
        try:
            catalogue_icon(icon)
        except ValueError as exc:
            errs.append(f"agenda: row {i + 1}: {exc}")
    return errs


def _validate_agenda(entry: dict) -> list[str]:
    """P52 T8: the numbered agenda. 2-4 rows, each with words of its own, revealed in order and inside the window.

    P61 T8: and its PAGE form (`form: "page"`) - the plate version of the list, whose own rules are next door."""
    errs: list[str] = []
    rows = entry.get("rows")
    lo, hi = AGENDA_ROWS
    if not isinstance(rows, (list, tuple)) or not lo <= len(rows) <= hi:
        return [f"agenda: 'rows' must be a list of {lo} to {hi} rows - one row is a note, {hi + 1} is a checklist"]
    step = entry.get("step")
    if step is not None and (isinstance(step, bool) or not isinstance(step, (int, float)) or step <= 0):
        errs.append("agenda: 'step' must be a positive number (the seconds between two rows' words)")
    at = entry.get("at") if isinstance(entry.get("at"), (int, float)) and not isinstance(entry.get("at"), bool) else None
    gap = step if isinstance(step, (int, float)) and not isinstance(step, bool) else AGENDA_STEP
    prev = None
    for i, row in enumerate(rows):
        where = f"agenda: row {i + 1}"
        if not isinstance(row, dict):
            errs.append(f"{where} must be a dict {{text, n?, sub?, at?}}")
            continue
        if not isinstance(row.get("text"), str) or not row["text"].strip():
            errs.append(f"{where}: 'text' must be a non-empty string - a numbered row says something")
        if "sub" in row and not isinstance(row["sub"], str):
            errs.append(f"{where}: 'sub' must be a string")
        if "n" in row and (isinstance(row["n"], bool) or not isinstance(row["n"], int) or row["n"] < 1):
            errs.append(f"{where}: 'n' must be a positive integer (the number the sentence gave the row)")
        r_at = row.get("at")
        if r_at is not None and (isinstance(r_at, bool) or not isinstance(r_at, (int, float))):
            errs.append(f"{where}: 'at' must be a number (episode seconds, the word the row is revealed on)")
            continue
        when = r_at if isinstance(r_at, (int, float)) else (at + i * gap if at is not None else None)
        if when is None:
            continue
        if at is not None and when < at:
            errs.append(f"{where}: revealed at {when} - before the agenda's own at {at}")
        if prev is not None and when <= prev:
            errs.append(f"{where}: revealed at {when}, not after row {i} at {prev} - one row per word, in order")
        prev = when
    if at is not None and prev is not None and isinstance(entry.get("dur"), (int, float)) and not isinstance(entry.get("dur"), bool):
        if prev + AGENDA_ROW_S > at + entry["dur"]:
            errs.append(f"agenda: the last row is revealed at {prev} and the window ends at {at + entry['dur']} - "
                        "a row that cannot finish arriving is not revealed, it flashes")
    return errs + _agenda_page_errors(entry, list(rows))


def _validate_ring(entry: dict) -> list[str]:
    """P52 T8: the ring's DASHED-ELLIPSE form, and its optional flag chip.

    E56 IS NOT WIDENED HERE. The rule is `_validate_callout`'s own, re-stated for this kind word for word (the
    operator, 2026-09-09: *"it has a specific use: circling a number or a point on a chart"*): a datum target IS
    a point on a chart, a label with a digit in it IS the number, and a ring round a picture's point or region is
    the cheap call-out the ruling refuses - the focus there is a LIGHT (the spotlight species). What this kind
    adds is the FORM (`form: "dashed"`) and the FLAG beside it; the hand's closed circle is still `callout`."""
    errs: list[str] = []
    if entry.get("form") not in RING_FORMS:
        errs.append(f"ring: 'form' must be one of {'|'.join(RING_FORMS)} - the ring's dashed form is what this kind is "
                    "(the hand's closed circle is a `callout`, E56's ring, unchanged)")
    tgt = entry.get("target")
    if isinstance(tgt, dict) and tgt.get("kind") != "datum" and not re.search(r"\d", str(entry.get("label", ""))):
        errs.append(f"ring: a ring circles a NUMBER or a POINT ON A CHART (E56) - this one targets a {tgt.get('kind')} "
                    f"with no numeric label; use a spotlight (the light) on a picture")
    flag = entry.get("flag")
    if flag is not None:
        if not isinstance(flag, str) or not flag.strip():
            errs.append('ring: \'flag\' is the flag chip\'s label, or "on" for a flag with no words')
        errs += _validate_icon("ring: flag", entry.get("flag_icon"))
        if "flag_side" in entry and entry["flag_side"] not in ("left", "right"):
            errs.append("ring: 'flag_side' must be left or right (absent = the side with the room)")
    elif entry.get("flag_icon") is not None:
        errs.append("ring: 'flag_icon' with no 'flag' - a glyph with no card is nothing on the stage")
    return errs


def _validate_entry(entry, press_docks: dict | None = None) -> list[str]:
    """Errors for one species entry: known kind, numeric at/dur, a target where the law requires one."""
    if not isinstance(entry, dict) or entry.get("kind") not in SPECIES_KINDS:
        return [f"species entry {entry!r}: kind must be one of {'|'.join(SPECIES_KINDS)}"]
    kind = entry["kind"]
    errs = [f"{kind}: {f!r} must be a number (episode seconds)" for f in ("at", "dur")
            if isinstance(entry.get(f), bool) or not isinstance(entry.get(f), (int, float))]
    if not errs and entry["dur"] <= 0:
        errs.append(f"{kind}: dur must be > 0 (a species that lasts 0s does not fire)")
    errs += _validate_page_fields(kind, entry)
    if kind == SPECIES_CHIP:
        errs += _validate_chip(entry)
    if kind == SPECIES_FLOW:
        errs += _validate_flow(entry)
    if kind == SPECIES_COUNT_ARRAY:   # P52 T7
        errs += _validate_count_array(entry)
    if kind == SPECIES_AGENDA:        # P52 T8
        errs += _validate_agenda(entry)
    if kind == SPECIES_RING:          # P52 T8: E56 re-stated, never widened
        errs += _validate_ring(entry)
    if kind == SPECIES_NEWSREEL:
        errs += _validate_newsreel(entry)
    if kind in VECMAP_SPECIES:
        errs += _validate_vecmap_species(entry)
    if kind == "trace" and "hop" in entry:   # opt-in (2026-09-08): ONE bowed hop point-to-point, drawn once and held - a crossing
        hop = entry["hop"]
        if not isinstance(hop, dict):
            errs.append("trace: hop must be a dict {from: [x, y], to: [x, y], bow?, draw_s?, width?}")
        else:
            for f in ("from", "to"):
                v = hop.get(f)
                if not (isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(c, (int, float)) and not isinstance(c, bool) and 0 <= c <= 1 for c in v)):
                    errs.append(f"trace: hop.{f} must be [x, y] as stage fractions 0..1")
            for f in ("bow", "draw_s", "width"):
                if f in hop and (isinstance(hop[f], bool) or not isinstance(hop[f], (int, float))):
                    errs.append(f"trace: hop.{f} must be a number")
            if isinstance(hop.get("draw_s"), (int, float)) and hop["draw_s"] <= 0:
                errs.append("trace: hop.draw_s must be > 0")
    if "idle" in entry and entry["idle"] not in IDLE_KINDS:   # a held light's idle (E49 on the spotlight, 2026-09-09)
        errs.append(f"{kind}: idle {entry['idle']!r} is not one of {'|'.join(IDLE_KINDS)}")
    if "zoom" in entry:   # R26-220: the FOCUS ZOOM's own dial - the magnification the move lands on (E99 s80 (2))
        z = entry["zoom"]
        if kind != "focus_zoom":
            errs.append(f"{kind}: 'zoom' is the focus zoom's dial - a {kind}'s scale is the engine's own "
                        "(CAM.PUNCH_SCALE / CAM.PULL_FROM), and a dial that does nothing is worse than no dial")
        elif isinstance(z, bool) or not isinstance(z, (int, float)):
            errs.append("focus_zoom: 'zoom' must be a number - the magnification the move lands on "
                        f"(absent = the engine's {FOCUS_ZOOM_DEFAULT})")
        elif z <= 1.0:
            errs.append(f"focus_zoom: zoom {z:g} does not zoom - a camera move magnifies (> 1.0); absent = the "
                        f"engine's {FOCUS_ZOOM_DEFAULT}, and what this page can take is `page_zoom_ceiling`")
    if kind == "callout":   # E56 and P50 T3's one exception - see _validate_callout
        errs += _validate_callout(entry, press_docks)
    allowed = SPECIES_TARGETS[kind]
    if not allowed:
        return errs
    if "target" not in entry:
        errs.append(f"{kind}: no declared target - a species with no declared target does not fire (s9.27)")
    else:
        errs += _validate_target(kind, entry["target"], allowed)
    return errs


def validate_species(row_species, ken, plate_id: str, pivot_span: tuple | None = None,
                     press_docks: dict | None = None) -> list[str]:
    """The targeting law as a pure check on one shot-table row's species list
    (doc 29 s9.27, s9.28 C3/C4). Returns the errors; the caller names the row.

    - every pointing species carries a declared target of an allowed kind;
    - at most one camera move (punch | focus_zoom | pull_back) per row, and
      none over an authored Ken Burns (``ken[0] > 0``) - one camera move per window;
    - no species fires inside ``pivot_span`` (the pivot's reversal takes no
      species; the parent wires the span from the ledger, the build passes None).
    """
    if row_species is None:
        return []
    if not isinstance(row_species, (list, tuple)):
        return [f"{plate_id}: species must be a list of species dicts"]
    errs = [e for entry in row_species for e in _validate_entry(entry, press_docks)]
    if not str(plate_id).startswith(LEDGER_PREFIX):   # P47 T2: the page species perform on a ledger page only
        errs += [f"{plate_id}: {e['kind']} is a page species - it performs on a ledger page, not on {plate_id!r}"
                 for e in row_species if isinstance(e, dict) and e.get("kind") in PAGE_SPECIES]
    if not VECMAP_PREFIX.match(str(plate_id)):   # P50 T5: the three map species perform ON a map, the way a page species performs on a page
        errs += [f"{plate_id}: {e['kind']} is a vecmap species - it performs on a vector map world "
                 f"(`vecmap[:<ISO A3 list>]`), not on {plate_id!r}"
                 for e in row_species if isinstance(e, dict) and e.get("kind") in VECMAP_SPECIES]
    for e in row_species:   # P57 T11 / E50: a compare morphs a figure the page has already WRITTEN at its datum -
        # the check lands here, where the row's whole species list is known (a single entry cannot see its page's others)
        if not (isinstance(e, dict) and e.get("kind") == "chart_to" and e.get("to") == "compare"):
            continue
        quoted = (e.get("metric") or {}).get("text") if isinstance(e.get("metric"), dict) else None
        if not isinstance(quoted, str) or not quoted.strip():
            continue
        if not any(isinstance(f, dict) and f.get("kind") == "figure" and isinstance(f.get("text"), str)
                   and f["text"].strip() == quoted.strip() for f in row_species):
            errs.append(f"{plate_id}: chart_to compare quotes {quoted!r} and the page writes no `figure` species with "
                        "that text - the number the sentence turns on is WRITTEN at its datum before it can morph (E50)")
    moves = [e["kind"] for e in row_species if isinstance(e, dict) and e.get("kind") in CAMERA_MOVES]
    if len(moves) > 1:
        errs.append(f"{plate_id}: {' + '.join(moves)} on one row - one camera move per window (s9.28 C3)")
    elif moves and ken and ken[0] > 0:
        errs.append(f"{plate_id}: {moves[0]} over Ken Burns scale {ken[0]} - a camera move and Ken Burns never share a window (s9.28 C3)")
    if pivot_span:
        p0, p1 = pivot_span
        for e in row_species:
            if not isinstance(e, dict) or not isinstance(e.get("at"), (int, float)):
                continue
            end = e["at"] + (e["dur"] if isinstance(e.get("dur"), (int, float)) else 0)
            if e["at"] < p1 and end > p0:
                errs.append(f"{plate_id}: {e['kind']} at {e['at']}s fires inside the pivot's reversal {p0}-{p1}s (s9.28 C4)")
    return errs


def timeline_species(scenes: list) -> list[str]:
    """Every species present, for the timeline's top-level ``species``: ``ledger``
    first when any page is drawn, then the targeted kinds in first-appearance order."""
    out = [SPECIES_LEDGER] if any(s["world"].get("kind") == SPECIES_LEDGER for s in scenes) else []
    for s in scenes:
        for e in s.get("species", []):
            if e["kind"] not in out:
                out.append(e["kind"])
    return out


def _dock_live_at(scenes: list, t: float) -> bool:
    """A dock holds the stage at t -> the caption takes the anchor (s9.25 #2)."""
    return any(d["enter"] <= t < d["exit"] for sc in scenes for d in sc.get("docks", []))


def _readable_species_during(scenes: list, start: float, end: float) -> bool:
    """Opt-in phone-sized labels reserve the caption rail for the whole phrase.

    Legacy species retain their old caption treatment. A raster chip stamp has
    no landscape-phone profile (its label is part of the prop contract), but a
    non-empty stamp label is still readable evidence and reserves the same
    quiet bottom rail. Testing interval overlap, not only the first word,
    prevents a label entering underneath stage captions.
    """
    return any(
        (
            (sp.get("readability") == "landscape-phone" and sp.get("kind") in ("chip", "flow"))
            or (sp.get("kind") == "chip" and sp.get("form") == "stamp"
                and isinstance(sp.get("label"), str) and bool(sp["label"].strip()))
        )
        and max(start, float(sc["span"][0]), float(sp["at"]))
        < min(end, float(sc["span"][1]), float(sp["at"]) + float(sp["dur"]))
        for sc in scenes for sp in sc.get("species", [])
    )


def _caption_display_end(pages: list, index: int) -> float:
    """Match the player's held phrase: next onset, or final word plus 0.4s."""
    return float(pages[index + 1]["s"]) if index + 1 < len(pages) else float(pages[index]["e"]) + 0.4


def _full_stage_page_at(scenes: list, t: float, aspect: str | None) -> bool:
    """R26-205: a 16:9 LEDGER PAGE holds the stage at t -> the caption takes the anchor too.

    The page's chart is the whole stage at 16:9 (`stamp_full_stage`), so the quiet zone the stage
    caption used to sit in is the plot. A plate row is untouched - it has no plot - and so is every
    9:16 build, where a portrait page's stage caption has its own strip under the page."""
    return any(float(sc["span"][0]) <= t < float(sc["span"][1]) for sc in scenes
               if sc.get("span") and page_is_full_stage(sc.get("world"), aspect))


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _parse_surface_entry(enter: str, plate_id: str, series_id: str, variant: str, path: Path) -> dict:
    """Parse the one cross-row page handoff form and bind it to its source file."""
    payload = enter[len("surface="):] if enter.startswith("surface=") else ""
    parts = payload.split(",")
    if len(parts) != 2 or not parts[0] or parts[0].strip() != parts[0]:
        raise ValueError(f"{plate_id!r}: surface= must be <paper-name>,<lead-seconds>")
    surface = parts[0]
    try:
        lead_s = float(parts[1])
    except (TypeError, ValueError, OverflowError):
        raise ValueError(f"{plate_id!r}: surface lead {parts[1]!r} must be a finite positive number of seconds") from None
    if not math.isfinite(lead_s) or lead_s <= 0:
        raise ValueError(f"{plate_id!r}: surface lead {parts[1]!r} must be a finite positive number of seconds")
    return {"surface": surface, "lead_s": lead_s,
            "source_ref": {"series_id": series_id, "variant": variant, "sha256": sha(path)}}


def parse_ledger_id(plate_id: str) -> tuple[str, str, int | None, str, str | None, str | None]:
    """``ledger:<series>:<variant>[:<emphasize>[:<quiet_zone>[:<enter>[:<exit>]]]]`` -> its parts.
    enter: ``spiral`` (the page returns by the vortex) or ``mount=<seconds>`` (the world fades above the page while its
    cream builds beneath, for that long, then the page draws - doc 29 s9.31), or
    ``surface=<paper-name>,<lead-seconds>`` (a registered paper handoff); exit: ``cut`` (no retract).
    ValueError names the id; the caller names the row."""
    parts = plate_id.split(":")
    lo, hi = LEDGER_ID_PARTS
    if parts[0] != LEDGER_PREFIX[:-1] or not (lo <= len(parts) <= hi) or not parts[1]:
        raise ValueError(f"{plate_id!r}: expected ledger:<series-id>:<variant>[:<emphasize>[:<quiet_zone>[:spiral|mount=<s>|surface=<paper>,<lead_s>[:cut]]]]")
    series_id, variant = parts[1], parts[2]
    if variant not in LPG.VARIANTS:
        raise ValueError(f"{plate_id!r}: variant {variant!r} is not one of {'|'.join(LPG.VARIANTS)}")
    emphasize: int | None = None
    if len(parts) > 3 and parts[3] != "":
        if not parts[3].lstrip("-").isdigit():
            raise ValueError(f"{plate_id!r}: emphasize {parts[3]!r} is not an integer index")
        emphasize = int(parts[3])
    quiet_zone = parts[4] if len(parts) > 4 else "right"
    if quiet_zone not in LPG.QUIET_ZONES:
        raise ValueError(f"{plate_id!r}: quiet_zone {quiet_zone!r} is not one of {'|'.join(LPG.QUIET_ZONES)}")
    enter = parts[5] if len(parts) > 5 and parts[5] != "" else None
    if enter is not None and enter.split("=")[0] not in LEDGER_ENTERS:   # mount may carry its length: mount=<seconds>
        raise ValueError(f"{plate_id!r}: enter {enter!r} is not one of {'|'.join(LEDGER_ENTERS)}")
    exit_ = parts[6] if len(parts) > 6 and parts[6] != "" else None
    if exit_ is not None and exit_ not in LEDGER_EXITS:
        raise ValueError(f"{plate_id!r}: exit {exit_!r} is not one of {'|'.join(LEDGER_EXITS)}")
    return series_id, variant, emphasize, quiet_zone, enter, exit_


MELT_ENDINGS = ("throw", "splash:chart", "splash:plate", "morph")   # E88 / R26-76: the authored endings - species/melt.mjs MELT_ENDINGS   # P61 T3 / R26-117: `morph` is the fourth - the melt ends AT the ball and hands its one ring to the next page's `page_enter:morph` as that page's prop outline, on one clock (`melt_morph_error` refuses a row whose next page does not enter by morph)
MELT_MATERIALS = ("metal", "ink", "paper", "liquid")       # R26-118 / E88 s7: what `melt:weight:<material>` may name - species/melt.mjs MELT_MATERIALS
DEPTH_SUFFIX = "depth="   # P58 T6 (b) / E98 s4: the plane a MECHANISM happens at, as an exit suffix - `melt:...:depth=<k>` and `slide:<dir>[:<s>]:depth=<k_out>,<k_in>` (P58 T6 (c)); species/melt.mjs and the engine's slideOpts read the same string on the player's side
BODY_SUFFIX = "body="     # P61 T5b / E99 s42: the ball's BODY COLOUR - `melt:weight:...:body=<word>`; species/melt.mjs MELT_BODY
MELT_BODIES = ("chart", "slate", "reference")   # P61 T5b / E99 s42, default `reference` since P61 T5c / E99 s49: chart (the ball that shipped - the chart's own ink), slate (the BOARD's ink, `--lp-char: #25313C`, docs/content-video-engine/samples/scene-evidence-player.template.html:50), reference (the blueprint's near-black metal, LIVING_METALLIC_DROP_RESEARCH_BLUEPRINT.md s3.3 :198-201 "the albedo base color is pure black", gate tier PLAUSIBLE); species/melt.mjs MELT_BODIES


def _is_number(bit: str) -> bool:
    try:
        float(bit)
    except ValueError:
        return False
    return True


def _melt_parts(exit_id: str) -> tuple[str, float | None, float | None, bool, str]:
    """A melt's suffixes, in any order (E88, R26-76): an ENDING - ``throw`` (the default), ``splash:chart`` or
    ``splash:plate`` - a bare number, its LENGTH, and on a throw only an ``x,y`` pair, the point it is thrown to in
    stage fractions. A bare ``splash`` is REFUSED: since E88 a splash has two endings that need two different incoming
    worlds, and an alias would pick one silently.

    P58 T6 (b) / E98 s4 adds ``depth=<k>`` - the PLANE the ball melts at: the clone takes that share of the one
    camera's move (`camLayerCss`), so the ball, its drips and its ending happen at a depth in the plate's space
    instead of on the glass. It is the dock's own vocabulary, range and refusal (`depth_k`), and a melt names at
    most one - a melt happens at one plane.

    R26-118 / E88 s6 adds ``weight``, optionally followed by a MATERIAL (``metal`` - the default, E88 s7 - ``ink``,
    ``paper`` or ``liquid``): the ball lands, rolls, is nudged and settles before the ending, and its surface is the
    living drop. It is opt-in, and a `melt:weight` that declares no length of its own runs MELT_S + MELT_W_S.
    A material this engine does not have is refused BY NAME, never painted as the default.

    P61 T6 / E99 s2 adds ``gather`` - a PHASE token beside ``weight``, composable with it and with every ending: the
    SAG becomes the page vortex (doc 29 s9.31) gathered to the ball's own centre, every mark travelling to one point
    and amassing on it, no blur and no wipe anywhere in the window. It is opt-in the same way, and a `melt:gather`
    that declares no length of its own runs its window plus MELT_G_S. E99 s34: it stays OFF the approved Japan short.

    P61 T5b / E99 s42 adds ``body=<word>`` - the ball's BODY COLOUR (``chart``, the ball that always shipped;
    ``slate``, the board's own ink; ``reference``, the blueprint's near-black metal). It is a suffix of its
    own and NOT a fifth material, because a material is the ball's mass and damping and a body is only its colour.
    A ball is one colour, so a row names at most one, and a word this engine does not have is refused BY NAME.
    P61 T5c / E99 s49 ("I like the reference") makes ``reference`` the DEFAULT for a WEIGHT ball that names no word;
    a melt with no ``weight`` token has no ball surface to shade and stays ``chart``, so its frames cannot move.

    species/melt.mjs ``meltOpts`` reads exactly this grammar on the player's side; the two have to agree, and
    test_transitions_e47 pins the pair. Returns (ending, the declared length or None for MELT_S, the declared
    depth or None for the flat clone, whether the row asked for the gather, the body colour)."""
    secs: float | None = None
    ending: str | None = None
    depth: float | None = None   # P58 T6 (b): validated here, carried to the player on the exit string itself
    gather = False               # P61 T6 / E99 s2: the phase token, carried to the player on the exit string too
    body: str | None = None      # P61 T5b / E99 s42: the ball's body colour, validated here and carried on the string
    weight = False               # P61 T5c / E99 s49: did the row ask for the ball? only a WEIGHT ball has a body to shade
    point = False
    bits = str(exit_id).split(":")[1:]
    i = 0
    while i < len(bits):
        bit = bits[i].strip()
        i += 1
        if bit == "":
            continue
        if bit == "morph":   # P61 T3 / R26-117: the ball becomes the next page's prop outline
            if ending is not None:
                raise ValueError(f"exit {exit_id!r}: two endings ({ending} and morph) - a melt ends one way")
            ending = "morph"
            continue
        if bit in ("throw", "splash"):
            end = bit
            if bit == "splash":
                nxt = bits[i].strip() if i < len(bits) else ""
                if nxt not in ("chart", "plate"):
                    raise ValueError(f"exit {exit_id!r}: splash names no ending since E88 - say splash:chart (the splatter "
                                     "forms the next chart) or splash:plate (a narrative plate springs up out of it)")
                end, i = f"splash:{nxt}", i + 1
            if ending is not None:
                raise ValueError(f"exit {exit_id!r}: two endings ({ending} and {end}) - a melt ends one way")
            ending = end
            continue
        if bit.startswith(DEPTH_SUFFIX):   # P58 T6 (b): the PLANE the ball melts at - the dock's own vocabulary and range
            if depth is not None:
                raise ValueError(f"exit {exit_id!r}: two depths - a melt happens at ONE plane")
            depth = depth_k(bit[len(DEPTH_SUFFIX):], f"exit {exit_id!r}", "ball")
            continue
        if bit == "gather":   # P61 T6 / E99 s2: the sag becomes the vortex, gathered to ONE point
            gather = True
            continue
        if bit.startswith(BODY_SUFFIX):   # P61 T5b / E99 s42: the ball's BODY COLOUR - species/melt.mjs meltOpts reads the same word
            if body is not None:
                raise ValueError(f"exit {exit_id!r}: two body colours - a ball is one colour")
            body = bit[len(BODY_SUFFIX):]
            if body not in MELT_BODIES:
                raise ValueError(f"exit {exit_id!r}: {body!r} is not a body colour - body= takes " + ", ".join(MELT_BODIES))
            continue
        if bit == "weight":   # R26-118: the weight phase, and the material the ball is made of
            weight = True
            nxt = bits[i].strip() if i < len(bits) else ""
            if nxt and "," not in nxt and nxt not in ("throw", "splash", "gather", "morph") and not nxt.startswith(DEPTH_SUFFIX) and not nxt.startswith(BODY_SUFFIX) and not _is_number(nxt):
                if nxt not in MELT_MATERIALS:
                    raise ValueError(f"exit {exit_id!r}: {nxt!r} is not a material - melt:weight takes "
                                     + ", ".join(MELT_MATERIALS))
                i += 1
            continue
        if bit in ("chart", "plate"):
            raise ValueError(f"exit {exit_id!r}: {bit!r} is a splash's ending - say splash:{bit}")
        if "," in bit:
            xy = bit.split(",")
            try:
                if len(xy) != 2:
                    raise ValueError
                [float(v) for v in xy]
            except ValueError:
                raise ValueError(f"exit {exit_id!r}: {bit!r} is not an x,y point in stage fractions") from None
            point = True
            continue
        try:
            secs = float(bit)
        except ValueError:
            raise ValueError(f"exit {exit_id!r}: {bit!r} is neither a length in seconds, nor an ending "
                             "(throw, splash:chart, splash:plate, morph), nor a phase (gather, weight), nor an "
                             "x,y point") from None
        if secs <= 0:
            raise ValueError(f"exit {exit_id!r}: a length must be positive")
    ending = ending or "throw"
    if point and ending != "throw":
        raise ValueError(f"exit {exit_id!r}: an x,y point is where a THROW goes - a splash lands on the board")
    # P61 T5c / E99 s49: the DEFAULT body, resolved in ONE place on this side (species/melt.mjs `meltOpts` resolves
    # the same one on the player's) - a WEIGHT ball with no word wears `reference`, everything else stays `chart`.
    return ending, secs, depth, gather, body or ("reference" if weight else "chart")


def melt_depth(exit_id: str | None) -> float | None:
    """The PLANE a melt happens at (`melt:...:depth=<k>`), or None - absent is the flat clone the melt always had."""
    if not exit_id or str(exit_id).split(":")[0] != "melt":
        return None
    return _melt_parts(str(exit_id))[2]


def melt_gather(exit_id: str | None) -> bool:
    """P61 T6 / E99 s2: did this melt ask for the GATHER? False for every other exit and for every melt on the
    record - the sag is what a melt that does not ask for it still renders, to the byte."""
    if not exit_id or str(exit_id).split(":")[0] != "melt":
        return False
    return _melt_parts(str(exit_id))[3]


def melt_body(exit_id: str | None) -> str:
    """P61 T5b / E99 s42 + T5c / E99 s49: which BODY COLOUR this melt's ball wears - `reference` (the blueprint's
    near-black metal) for a `melt:weight` that names no word, and whatever `body=chart|slate|reference` says when the
    row says one. `chart` for a melt with no weight token and for every other exit - there is no ball surface to
    shade there, which is why the default melt's frames are byte-identical."""
    if not exit_id or str(exit_id).split(":")[0] != "melt":
        return "chart"
    return _melt_parts(str(exit_id))[4]


def page_camera_k(page: dict | None) -> float:
    """The depth at which a ledger page took the camera onto its own plane, or 0 for a flat page - the player's
    `pageDepthOf` exactly (a page at depth 1 IS the flat page, so it keeps the camera on its element)."""
    try:
        k = float((page or {}).get("depth") or 0)
    except (TypeError, ValueError):
        return 0.0
    return k if k > 0 and k != 1 else 0.0


def melt_depth_page_error(exit_id: str | None, page: dict | None) -> str | None:
    """P58 T6 / R26-132 (1): does a melt's `depth=` meet a page that already stands at a depth? The message, or None."""
    k_page, k_ball = page_camera_k(page), melt_depth(exit_id)
    if k_ball is None or not k_page:
        return None
    return (f"exit {exit_id!r}: a melt at a depth on a page that already stands at depth={k_page:g} - the page took the "
            "camera onto its own plane, so the ball would melt flat; drop one")


def melt_ending(exit_id: str | None) -> str | None:
    """The authored ending of a melt exit (``throw`` | ``splash:chart`` | ``splash:plate``), or None for any other exit."""
    if not exit_id or str(exit_id).split(":")[0] != "melt":
        return None
    return _melt_parts(str(exit_id))[0]


# ---- P48 T5b / R26-16: THE PLANTED SOURCE a page-enter morph starts from -----------------------------------------
# `world.morph` names the PROP OUTLINE the arriving page's `page_enter:morph` deforms into the area under its series
# (P47 T3). It was three NAMED shapes and nothing else (MORPH_SHAPES: tab, plate, card - `morphProp` builds them as
# strips about the target's own centroid). P48 T5b adds the form R26-16's tie asks for: `{"poly": [[x, y], ...]}`, a
# real element's own silhouette - "a real element of the outgoing world at its last frame, never a shape conjured
# over the clip". The tracer that produces one from a still is `kinetics/contour.mjs` (`contourSilhouette`: the
# element's own pixels rastered, thresholded, walked with marching squares, the largest non-hole ring simplified) -
# ours, no library - and the player re-expresses whatever it is handed as a strip of columns (`arap.mjs polyStrip`).
# THE UNITS ARE STAGE FRACTIONS, the melt's own vocabulary for a point on the board (`melt:...:<x>,<y>`), so a poly
# is read the same on either aspect and against neither page's viewBox.
# THE THREE REFUSALS, each BY NAME, because a bad poly is a silent bad morph the render only shows afterwards:
# fewer than three points is not an outline; a self-intersecting ring has no inside for a mesh to carry (arapPrepare's
# Laplacian is not positive definite on the flipped triangles it makes); a point off the stage is a prop the frame
# never held, which is the exact thing R26-16 refuses.
MORPH_POLY_MIN = 3


def _seg_cross(a, b, c, d) -> bool:
    """Do the open segments ab and cd properly cross? (Orientation signs, strict - a shared endpoint is not a crossing.)"""
    def side(p, q, r) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    d1, d2, d3, d4 = side(a, b, c), side(a, b, d), side(c, d, a), side(c, d, b)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def morph_poly_error(poly, where: str) -> str | None:
    """A `world.morph` poly's message, or None. The units are STAGE FRACTIONS (0..1 on each axis)."""
    if not isinstance(poly, (list, tuple)):
        return f"{where}: morph poly is {type(poly).__name__}, not a list of [x, y] points in stage fractions"
    pts: list[tuple[float, float]] = []
    for i, p in enumerate(poly):
        if not (isinstance(p, (list, tuple)) and len(p) == 2):
            return f"{where}: morph poly point {i} is {p!r} - each point is a pair [x, y] in stage fractions"
        try:
            pts.append((float(p[0]), float(p[1])))
        except (TypeError, ValueError):
            return f"{where}: morph poly point {i} is {p!r} - each point is a pair of numbers"
    if len(pts) < MORPH_POLY_MIN:
        return (f"{where}: morph poly has {len(pts)} point(s) - an outline needs at least {MORPH_POLY_MIN}; "
                "kinetics/contour.mjs contourSilhouette traces one off a planted element's own pixels")
    for i, (x, y) in enumerate(pts):
        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            return (f"{where}: morph poly point {i} is ({x:g}, {y:g}), outside the stage - a planted source is a shape "
                    "the frame actually held (R26-16); the units are stage fractions, 0..1 on each axis")
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        for j in range(i + 1, n):
            if j == i or (j + 1) % n == i or (i + 1) % n == j:
                continue
            if _seg_cross(a, b, pts[j], pts[(j + 1) % n]):
                return (f"{where}: morph poly crosses itself (edge {i}-{(i + 1) % n} through edge {j}-{(j + 1) % n}) - "
                        "a ring with no inside cannot be carried by a strip mesh (arap.mjs polyStrip / arapPrepareMesh)")
    return None


def morph_source_error(world: dict | None, where: str) -> str | None:
    """`world.morph`: a NAMED prop (MORPH_SHAPES), a traced poly (P48 T5b), or absent (the tab, the default)."""
    src = (world or {}).get("morph") if isinstance(world, dict) else None
    if src is None:
        return None
    if isinstance(src, str):
        return None if src in MORPH_SHAPES else (f"{where}: morph={src!r} is not one of {'|'.join(MORPH_SHAPES)} - "
                                                 "or a planted element's own outline, {\"poly\": [[x, y], ...]}")
    if isinstance(src, dict) and "poly" in src:
        return morph_poly_error(src.get("poly"), where)
    return (f"{where}: world.morph is {src!r} - a named prop ({'|'.join(MORPH_SHAPES)}) or a planted element's own "
            "outline, {\"poly\": [[x, y], ...]} in stage fractions (P48 T5b / R26-16)")


def _melt_exit(exit_id: str) -> float | None:
    """The declared length of a melt, or None for MELT_S (the grammar is ``_melt_parts``)."""
    return _melt_parts(exit_id)[1]


def _slide_depths(exit_id: str, raw: str) -> tuple[float, float]:
    """``depth=<k_out>,<k_in>`` on a slide -> the two planes (P58 T6 (c)). TWO, always: the plane the outgoing frame
    leaves at and the plane the incoming frame arrives from - one number would pick the other frame's plane silently."""
    ks = raw.split(",")
    if len(ks) != 2:
        raise ValueError(f"exit {exit_id!r}: a slide names TWO depths - depth=<k_out>,<k_in>, the plane the outgoing "
                         f"frame leaves at and the plane the incoming frame arrives from; {raw!r} names "
                         f"{'one' if len(ks) == 1 else len(ks)}")
    where = f"exit {exit_id!r}"
    return depth_k(ks[0].strip(), where, "outgoing frame"), depth_k(ks[1].strip(), where, "incoming frame")


def _slide_parts(exit_id: str) -> tuple[str, float | None, tuple[float, float] | None]:
    """A slide's suffixes (E87 s3, R26-75): the DIRECTION first - `left`, `right`, `up` or `down`, which way the
    incoming frame pushes the outgoing one off - and then, optionally, its LENGTH in seconds.

    P58 T6 (c) / E98 s4 adds ``depth=<k_out>,<k_in>`` after them - the slide THROUGH the depth: the outgoing frame
    goes from the flat plate to the camera read at k_out as it leaves, and the incoming one from k_in to the flat
    plate as it lands, so both ends of the slide are the frames a flat slide paints. The dock's and the melt's own
    vocabulary and range (`depth_k`), and absent is the flat slide every row on the record already is.

    The direction is never defaulted: the whole point is the axis and the sign the scene chose, and a silent default
    would paint a hand-off nobody authored. `push` is refused by name: it is OUR camera push-in (E87 s3, "Named
    `slide` in our grammar, because `push` is already the camera push-in"), never a direction.

    The player's `slideOpts` (scene-evidence-engine.mjs, THE SLIDE) reads exactly this grammar on its side; the two
    have to agree, and test_transition_stamps pins the pair. Returns (direction, the declared length or None for
    SLIDE_S, the two declared depths or None for the flat slide)."""
    bits = str(exit_id).split(":")[1:]
    direction = bits[0].strip() if bits else ""
    if direction == "":
        raise ValueError(f"exit {exit_id!r}: a slide names no direction - say slide:left|right|up|down[:<s>] "
                         "(which way the incoming frame pushes the outgoing one off)")
    if direction == "push":
        raise ValueError(f"exit {exit_id!r}: `push` is the camera push-in, never a slide's direction (E87 s3) - "
                         "say slide:left|right|up|down")
    if direction not in SLIDE_DIRECTIONS:
        raise ValueError(f"exit {exit_id!r}: {direction!r} is not one of {'|'.join(SLIDE_DIRECTIONS)}")
    rest = [b.strip() for b in bits[1:]]
    depths: tuple[float, float] | None = None
    if rest and rest[-1].startswith(DEPTH_SUFFIX):   # P58 T6 (c): the two planes, LAST
        depths = _slide_depths(exit_id, rest.pop()[len(DEPTH_SUFFIX):])
    if any(b.startswith(DEPTH_SUFFIX) for b in rest):
        raise ValueError(f"exit {exit_id!r}: depth= comes last and once - slide:<dir>[:<s>]:depth=<k_out>,<k_in>")
    if len(rest) > 1:
        raise ValueError(f"exit {exit_id!r}: a slide carries a direction and at most a length - {bits[2:]!r} is neither")
    if not rest or rest[0] == "":
        return direction, None, depths
    try:
        secs = float(rest[0])
    except ValueError:
        raise ValueError(f"exit {exit_id!r}: {rest[0]!r} is not a length in seconds") from None
    if secs <= 0:
        raise ValueError(f"exit {exit_id!r}: a length must be positive")
    return direction, secs, depths


def slide_depth(exit_id: str | None) -> tuple[float, float] | None:
    """The two planes a slide moves through (`slide:...:depth=<k_out>,<k_in>`), or None - absent is the flat slide."""
    if not exit_id or str(exit_id).split(":")[0] != "slide":
        return None
    return _slide_parts(str(exit_id))[2]


def slide_depth_world_error(exit_id: str | None, world: dict | None, side: str) -> str | None:
    """P58 T6 (c): may this side's world take a slide's depth? A page at a depth or a LAYERED plate already took the
    camera onto its own plane(s) - the player's camDepthSwap finds no flat camera there, so that frame would slide
    flat and say nothing. The message, or None."""
    if slide_depth(exit_id) is None or not isinstance(world, dict):
        return None
    k_page = page_camera_k(world.get("page") if world.get("kind") == SPECIES_LEDGER else None)
    if k_page:
        return (f"exit {exit_id!r}: a slide at a depth on {side} page that already stands at depth={k_page:g} - the "
                "page took the camera onto its own plane, so that frame would slide flat; drop one")
    if world.get("kind") != SPECIES_LEDGER and world.get("layers"):
        return (f"exit {exit_id!r}: a slide at a depth on {side} layered plate - the plate took the camera onto its "
                "own planes, so that frame would slide flat; drop one")
    return None


def slide_direction(exit_id: str | None) -> str | None:
    """The authored direction of a slide exit (``left`` | ``right`` | ``up`` | ``down``), or None for any other exit."""
    if not exit_id or str(exit_id).split(":")[0] != "slide":
        return None
    return _slide_parts(str(exit_id))[0]


def _door_parts(exit_id: str) -> tuple[str, float | None]:
    """THE EVIDENCE DOOR's suffixes (E98 s7, R26-134): ``door[:<hinge>][:<s>]`` - the HINGE first, one of DOOR_HINGES
    (the stage edge the outgoing world swings open on, DOOR_HINGE when absent), then optionally its LENGTH in seconds,
    inside DOOR_S_MIN..DOOR_S_MAX. The player's `doorOpts` (kinetics/transitions.mjs) reads exactly this grammar and
    treats anything it cannot read as a cut, so every refusal is HERE, by name, with the fix in the message.
    Returns (hinge, the declared length or None for DOOR_S)."""
    bits = [b.strip() for b in str(exit_id).split(":")[1:]]
    hinge = DOOR_HINGE
    if bits and bits[0] in DOOR_HINGES:
        hinge = bits.pop(0)
    elif bits and not _is_number(bits[0]):
        raise ValueError(f"exit {exit_id!r}: {bits[0]!r} is not a hinge - say door[:{'|'.join(DOOR_HINGES)}][:<s>] "
                         "(the stage edge the outgoing world swings open on)")
    if len(bits) > 1:
        raise ValueError(f"exit {exit_id!r}: a door carries a hinge and at most a length, in that order - {bits[1:]!r} "
                         "is neither; say door[:<hinge>][:<s>]")
    if not bits:
        return hinge, None
    secs = float(bits[0])
    if not DOOR_S_MIN <= secs <= DOOR_S_MAX:
        raise ValueError(f"exit {exit_id!r}: a door of {secs:g} s is outside {DOOR_S_MIN:g}..{DOOR_S_MAX:g} s - shorter "
                         "is a flick, longer holds the boundary on a move with no evidence in it (E49); say "
                         f"door:{hinge}:<s> inside the range, or drop the length for {DOOR_S:g} s")
    return hinge, secs


def door_hinge(exit_id: str | None) -> str | None:
    """The hinge a door exit swings on (``left`` | ``right`` | ``top`` | ``bottom``), or None for any other exit."""
    if not exit_id or str(exit_id).split(":")[0] != "door":
        return None
    return _door_parts(str(exit_id))[0]


def door_boundary_error(prev: dict, sc: dict) -> str | None:
    """May the door INTO `sc` open here? The message, or None.

    1. A door opens a card that LANDED FLAT (E98 s7: "a card's tilt is a MOTION, not a pose it jumps to"): an outgoing
       page that already stands at `;depth=` or on `;plane=` is refused - the door IS that plane's motion.
    2. Doc 29 Part 6: a decorated transition happens on an EVIDENCE-FREE boundary (documents exit -> cards retract ->
       then the move). The rule mirrored is the WIPE's own at its boundary (the engine's `allOut`): a card belongs to the
       outgoing page when it leaves within DOOR_DOCK_TOL of the boundary, and anything else up across the swing - an
       outgoing card that stays, an incoming card that lands mid-swing, a coalesced document held through the
       boundary - would float over a world turning in space, so it is refused by name."""
    exit_id = sc.get("exit")
    if str(exit_id or "").split(":")[0] != "door":
        return None
    secs = _door_parts(str(exit_id))[1] or DOOR_S
    ppg = _page_of(prev)
    if ppg is not None and (ppg.get("depth") is not None or ppg.get("plane")):
        return f"exit {exit_id!r}: a door opens a card that landed flat - drop depth=/plane=, the door is the plane's motion"
    b = float((sc.get("span") or [0.0])[0])
    for side, s in (("outgoing", prev), ("incoming", sc)):
        for d in s.get("docks") or []:
            enter, leave = float(d.get("enter", b)), float(d.get("exit", b))
            if enter < b + secs and leave > b + DOOR_DOCK_TOL:
                return (f"exit {exit_id!r}: a door swings on an evidence-free boundary (doc 29 Part 6) - the {side} dock "
                        f"{d.get('slide', '?')!r} is up across it ({enter:g}-{leave:g} s against the swing {b:g}-"
                        f"{b + secs:g} s); let the card leave by the boundary (within {DOOR_DOCK_TOL:g} s, the wipe's "
                        "own rule) or land after the door has opened, or say dip")
    return None


def parse_exit(exit_id: str) -> tuple[str, float | None]:
    """``cut`` | ``dip[:<s>]`` | ``blurzoom[:<s>]`` | ``wipe_right`` | ``suck:<x>,<y>`` |
    ``melt[:throw|:splash:chart|:splash:plate][:gather][:weight[:<material>]][:<s>][:<x>,<y>]`` | ``slide:<left|right|up|down>[:<s>][:depth=<k_out>,<k_in>]``
    -> (name, seconds or None).

    Only dip, blurzoom, melt and slide read a suffix as a length; the suck's is the point it collapses
    into, the melt's may be a length AND an ending AND a point (``_melt_parts``), the slide's length
    follows its direction (``_slide_parts``), and every other exit is a bare name. ValueError names the
    exit; the caller names the row."""
    name = str(exit_id).split(":")[0]
    if name not in SCENE_EXITS:
        raise ValueError(f"exit {exit_id!r} is not one of {'|'.join(SCENE_EXITS)}")
    if name == "melt":
        return exit_id, _melt_exit(exit_id)
    if name == "slide":
        return exit_id, _slide_parts(exit_id)[1]   # the depths ride the exit string itself (slide_depth)
    if name == "door":
        return exit_id, _door_parts(exit_id)[1]    # the hinge rides the exit string itself (door_hinge)
    arg = str(exit_id).split(":")[1] if ":" in str(exit_id) else ""
    if name not in TIMED_EXITS or arg == "":
        return exit_id, None
    try:
        secs = float(arg)
    except ValueError:
        raise ValueError(f"exit {exit_id!r}: {arg!r} is not a length in seconds") from None
    if secs <= 0:
        raise ValueError(f"exit {exit_id!r}: a length must be positive")
    return exit_id, secs


def world_key(world: dict | None) -> tuple:
    """What makes a row's world THIS world: a plate or a clip by its asset, a ledger page by its builder and title
    (a page returning by the spiral is the same world; a different chart is a different one)."""
    if not isinstance(world, dict):
        return ("none",)
    page = world.get("page") if isinstance(world.get("page"), dict) else None
    if page is not None:
        return ("page", str(page.get("builder") or ""), str(page.get("title") or ""), str(page.get("ink") or page.get("series_id") or ""))
    return (str(world.get("kind") or "plate"), str(world.get("asset_id") or ""))


def scene_exit(authored_exit: str | None, has_docks: bool, page_enter: str | None = None,
               world_changed: bool | None = None) -> tuple[str, float | None]:
    """The HYBRID exit rule (operator 2026-08-29), E47's default corrected 2026-09-12: an authored exit wins;
    otherwise the dip is the natural transition WHEN THE WORLD ACTUALLY CHANGES at the boundary (`world_changed`:
    the incoming row's world is not the outgoing row's - a different plate, clip or page), EXCEPT in front of a
    signature enter (the mount, the spiral, the morph carry the change on their own clock - a dip there paints
    black seconds before the plate actually changes, the black flash of Tokyo s04 -> s05); the same world, or a
    signature, cuts. A DOCK decides nothing ("the dip was associated with any DOCK, not the dip being associated
    to the scene change. That's 2 very different things"); `has_docks` stays in the signature for the record.

    An authored 6th shot-table element wins - doc 29 s9.16 #3's override stands, and a row that
    wants the carried-light cross-reveal still asks for it by name. Otherwise the MECHANICAL
    default is ``dip`` when the scene carries docks and ``cut`` when it is bare (it was
    ``wipe_right``/``cut``: the wipe is retired as the default world change, E47 #3).
    Returns the exit as the timeline carries it and the seconds it declares, if any."""
    if authored_exit is not None:
        return parse_exit(authored_exit)
    if page_enter in SIGNATURE_ENTERS or not world_changed:
        return parse_exit(DEFAULT_EXIT_BARE)
    return parse_exit(DEFAULT_EXIT_CHANGE)


def _melt_boundary(prev: dict, sc: dict, ppg: dict | None, pg: dict | None) -> list[str]:
    """E88's three boundary rules for the melt INTO `sc` (see stamp_transition_pages). Returns the stamp it made, if any."""
    ending = melt_ending(sc.get("exit"))
    if ending is None:
        return []
    row = f"{prev.get('scene_id', '?')} -> {sc.get('scene_id', '?')} ({sc.get('exit')})"
    if ppg is None:
        raise ValueError(f"{row}: a melt takes a chart's ink and leaves the board (E88) - the outgoing world is not a ledger page; "
                         "the whole-world melt is retired")
    # P58 T6 / R26-132 (1): a melt at a depth on a page that already TOOK the camera onto its own plane. The player's
    # camDepthSwap finds no flat camera on that world to swap (`data-world-pose`), so the ball would melt flat and say
    # nothing - refused here by name. (A LAYERED plate never reaches
    # this: a melt's outgoing world must be a ledger page, refused just above, and a page carries no plate planes.)
    _err = melt_depth_page_error(sc.get("exit"), ppg)
    if _err:
        raise ValueError(f"{row}: {_err}")
    if ending in ("throw", "splash:chart", "morph") and pg is None:
        raise ValueError(f"{row}: a {ending} hands the same board to the next chart (E88) - the incoming world is not a ledger page; "
                         "say melt:splash:plate to paint a plate")
    # P61 T3 / R26-117 - THE HAND-OVER's two ends must both be there, or the row is refused by name. The melt ends AT
    # the ball and the ball IS the next page's prop outline, so the next page must be a page that enters BY MORPH and
    # whose morph has an area to land on (MORPH_BUILDERS: the area under a LINE). A row that declares no enter gets
    # `morph` stamped, exactly as a splash:chart's page gets `built` - the transition names the arrival.
    if ending == "morph":
        if ((sc.get("world") or {}).get("morph")) is not None:
            raise ValueError(f"{row}: a melt:morph's page names no prop - the BALL is the prop it starts from (R26-117), "
                             "and world.morph is what the engine hands it; drop world.morph, or drop the morph ending")
        if not pg.get("enter"):
            pg["enter"] = "morph"
            if pg.get("builder") not in MORPH_BUILDERS:
                raise ValueError(f"{row}: a melt:morph hands the ball to the next page's page_enter:morph, which deforms it into "
                                 f"the AREA UNDER A LINE ({'|'.join(MORPH_BUILDERS)}) - the incoming page's builder is "
                                 f"{pg.get('builder')!r}; melt:splash:chart arrives on any builder")
            return [f"{sc.get('scene_id', '?')}: enter=morph stamped - a melt:morph's page IS the ball's morph, not a build under it (R26-117)"]
        if pg.get("enter") != "morph":
            raise ValueError(f"{row}: a melt:morph's page arrives BY the morph (R26-117: the ball is the prop it starts from) - "
                             f"enter={pg.get('enter')} would cut from the ball to a build; drop the enter or say morph")
        if pg.get("builder") not in MORPH_BUILDERS:
            raise ValueError(f"{row}: a melt:morph hands the ball to the next page's page_enter:morph, which deforms it into "
                             f"the AREA UNDER A LINE ({'|'.join(MORPH_BUILDERS)}) - the incoming page's builder is "
                             f"{pg.get('builder')!r}; melt:splash:chart arrives on any builder")
    if ending == "splash:plate" and pg is not None:
        raise ValueError(f"{row}: a splash:plate paints a narrative plate (E88) - the incoming world is a ledger page; "
                         "say melt:splash:chart")
    if ending == "splash:chart":
        if not pg.get("enter"):
            pg["enter"] = "built"
            return [f"{sc.get('scene_id', '?')}: enter=built stamped - a splash:chart's page arrives out of the splatter, not by its build (E88)"]
        if pg.get("enter") != "built":
            raise ValueError(f"{row}: a splash:chart's page arrives out of the splatter (E88) - enter={pg.get('enter')} would build "
                             "under the stains; drop the enter or say built")
    return []


WORLD_TAKING_EXITS = ("suck", "melt", "door")   # E98 s7: the door takes the world too - the page swings away with its chart on it, so it must not retract first   # P53 T2 / R26-60: a transition that TAKES the world - the page goes into a point or drips away


def _page_of(sc: dict | None) -> dict | None:
    w = (sc or {}).get("world") or {}
    return w.get("page") if isinstance(w.get("page"), dict) else None


def stamp_transition_pages(scenes: list[dict]) -> list[str]:
    """The defaults the transitions imply, stamped where both sides of every boundary are visible.

    THE CONVENTION (E47, SCENE_EXITS above; the engine): `exit` names the transition INTO the scene it sits on - so the
    boundary between scenes[i-1] and scenes[i] is scenes[i]["exit"]. (P53 T6 and the first P54 cut read it as the exit
    OUT of the scene; the seam measure of P54 T9 caught it, 2026-09-13.)

    UNDER a suck or a melt (R26-60): the transition into scenes[i] TAKES the outgoing world, scenes[i-1]. A ledger page
    there that does not declare `:cut` runs its own RETRACT first and has emptied the sheet before the boundary, so the
    suck spins a blank cream page into its point. The OUTGOING page is stamped `exit=cut`.

    CHART TO CHART (the operator, 2026-09-12: "The empty cream stage isnt supposed to be on stage during the exits ...
    It doesnt make sense to do that when transitioning from chart-to-chart, that is used for mounting a ledger plate to
    a narrative plate"): a ledger page that follows a ledger page and declares no enter arrives on its axes, whatever
    the transition - the empty cream roll-out is the MOUNT's register. A page after a plate keeps its own arrival.

    THE HOOK (the operator, 2026-09-12): the first scene's ledger page with no declared enter opens on `axes`.

    THE MELT (E88, R26-76): a melt takes a CHART's ink and the board stays, so the outgoing world must be a ledger page;
    a throw and a chart splash hand the SAME board to a chart, so the incoming world must be a page; a plate splash
    paints a narrative plate, so the incoming world must not be one. A chart splash's page arrives out of the splatter,
    built - its row gets `enter=built` stamped, and a row that declares another enter is refused (it would build under
    the stains). Refusals raise ValueError naming both scenes.

    A row that declares its own enter or exit is never touched. Returns one line per stamp, for the build to print."""
    notes: list[str] = []
    for sc in scenes:   # P48 T5b / R26-16: the planted source a page-enter morph starts from, checked wherever it is authored
        _err = morph_source_error(sc.get("world"), f"{sc.get('scene_id', '?')}: world.morph")
        if _err:
            raise ValueError(_err)
    for i in range(1, len(scenes)):
        prev, sc = scenes[i - 1], scenes[i]
        kind = str(sc.get("exit") or "").split(":")[0]
        ppg, pg = _page_of(prev), _page_of(sc)
        notes += _melt_boundary(prev, sc, ppg, pg)
        for _w, _side in ((prev.get("world"), "the outgoing"), (sc.get("world"), "the incoming")):   # P58 T6 (c)
            _err = slide_depth_world_error(sc.get("exit"), _w, _side)
            if _err:
                raise ValueError(f"{prev.get('scene_id', '?')} -> {sc.get('scene_id', '?')} ({sc.get('exit')}): {_err}")
        _err = door_boundary_error(prev, sc)   # E98 s7: a flat card, an evidence-free boundary
        if _err:
            raise ValueError(f"{prev.get('scene_id', '?')} -> {sc.get('scene_id', '?')} ({sc.get('exit')}): {_err}")
        if kind in WORLD_TAKING_EXITS and ppg is not None and not ppg.get("exit"):
            ppg["exit"] = "cut"
            notes.append(f"{prev.get('scene_id', '?')}: exit=cut stamped - the page a {kind} takes must not retract first (R26-60)")
        if ppg is not None and pg is not None and not pg.get("enter"):
            pg["enter"] = "axes"
            notes.append(f"{sc.get('scene_id', '?')}: enter=axes stamped - chart to chart ({kind or 'cut'}), the page is on its axes, never empty cream")
    if scenes:
        first = scenes[0]
        fpg = _page_of(first)
        if fpg is not None and not fpg.get("enter") and float((first.get("span") or [1.0])[0]) <= 0.05:
            fpg["enter"] = "axes"
            notes.append(f"{first.get('scene_id', '?')}: enter=axes stamped - the hook opens on the axes register and is answered on the ledger")
    notes += _stamp_morph_page_fields(scenes)   # E99 s52, LAST: every enter=morph is stamped by now (the hand-over's above)
    return notes


MORPH_PAGE_FIELD = "soak"   # E99 s52 / E99 s35: the ground a MORPH page arrives on when its row names none


def _stamp_morph_page_fields(scenes: list[dict]) -> list[str]:
    """E99 s52 - A MORPH PAGE'S GROUND HAS TO ARRIVE, so it must name the entry it arrives by.

    The operator, 2026-09-16, on the planted morph: *"going from the ink splotch to the full fill on the board
    instantly around it is the problem here."* The engine now runs a morph page's field on its own clock under the
    morph (MORPH.GROUND), which means the page needs a field, and the DEFAULT for a morph page is the SOAK: the prop
    is already ink, so the ink spreads out from it (E99 s35's soak, seeded on the splotch - the player's
    `lpMorphSeedPoint`). A row that names its own `;field=` is never touched: `field=plates` on a morph page is the
    cross-fade for continuity, exactly as s35 wrote it, and `field=scribble` is still the opt-in back-up.

    Returns one line per stamp. Run after every other stamp, so a page whose `enter=morph` was stamped by the
    melt's own boundary rule (`_melt_boundary`) is seen here too."""
    notes: list[str] = []
    for sc in scenes:
        pg = _page_of(sc)
        if pg is None or pg.get("enter") != "morph" or pg.get("field"):
            continue
        pg["field"] = MORPH_PAGE_FIELD
        notes.append(f"{sc.get('scene_id', '?')}: field={MORPH_PAGE_FIELD} stamped - a morph page's ground ARRIVES, "
                     "and the soak is the entry a prop that is already ink spreads out of (E99 s52)")
    return notes


TIP_MARK_KINDS = ("ring", "callout")   # the species that draw an ellipse round their datum


def stamp_tip_marks(scenes: list[dict]) -> list[str]:
    """A ledger page whose ring or callout lands on a line's LAST datum is stamped `tip_mark: [series, ...]`.

    The line's terminal name is written just left of its tip, and the ellipse round that tip is at least RING.MIN_RX
    wide - so on normal-for-which-bridge review-v1 (0:57) the dashed ring sat on "x3.9 Federal debt". A stage painter
    cannot read the page's labels; the PAGE can keep the room, if it is told the tip will be marked. The engine's line
    builder reads `tip_mark` and ends the name clear of the ring's reach. Within the last two data counts as the tip.
    A page that declares its own `tip_mark` is not touched. Returns one line per stamp."""
    notes: list[str] = []
    for sc in scenes:
        pg = ((sc.get("world") or {}).get("page")) if isinstance((sc.get("world") or {}).get("page"), dict) else None
        if pg is None or "tip_mark" in pg:
            continue
        ser = pg.get("series") or []
        marked: set[int] = set()
        for sp in sc.get("species") or []:
            tg = sp.get("target") or {}
            if sp.get("kind") not in TIP_MARK_KINDS or tg.get("kind") != "datum":
                continue
            si = int(tg.get("series") or 0)
            if 0 <= si < len(ser) and int(tg.get("index") or 0) >= len(ser[si].get("pts") or []) - 2:
                marked.add(si)
        if marked:
            pg["tip_mark"] = sorted(marked)
            notes.append(f"{sc.get('scene_id', '?')}: tip_mark={sorted(marked)} stamped - a ring or callout marks the line's last datum, so its name keeps clear")
    return notes


def _page_state(spec_id: str, ep_dir: Path, where: str) -> dict:
    """`<series>:<variant>[:<emphasize>]` -> a second ledger_page.v1 spec, validated like the page's own."""
    bits = spec_id.split(":")
    if not 2 <= len(bits) <= 3:
        raise ValueError(f"{where}: then={spec_id!r} must be <series>:<variant>[:<emphasize>]")
    series_id, variant = bits[0], bits[1]
    emph = int(bits[2]) if len(bits) == 3 and bits[2] else None
    path = Path(ep_dir) / "evidence/objects" / f"{series_id}.series.json"
    if not path.exists():
        raise ValueError(f"{where}: then={spec_id!r}: series file missing: {path}")
    series = LPG.load_series(path)
    errors = LPG.validate(series, variant)
    if errors:
        raise ValueError(f"{where}: then={spec_id!r} is not a page ({variant}): " + "; ".join(errors))
    # R26-205: a chart STATE is drawn in the first state's own <svg> box (the engine copies its cssText),
    # so it is the same plate and carries the same stamp - otherwise `page_boxes` would read one geometry
    # for the page and another for the chart it becomes.
    return stamp_full_stage(LPG.build_spec(series, variant, emph))


def rescale_state(plate_id: str, ep_dir: Path, sp: dict, reveal: int | None = None) -> dict:
    """P48 T2: the page's OWN series re-specified for a target domain - the x window sliced to [from, to] (a point on
    the edge kept; a highlight_from outside the window dropped), the y bounds carried as `axes.domain` and the window
    as `axes.xdomain`, which the player's line builder honours exactly (opt-in keys: a page that names neither draws as
    it always has). Every mark keeps its key, so the transition is a pure interpolation of positions."""
    series_id, variant, emphasize, quiet_zone, _enter, _exit = parse_ledger_id(split_plate_opts(plate_id)[0])
    path = Path(ep_dir) / "evidence/objects" / f"{series_id}.series.json"
    series = copy.deepcopy(LPG.load_series(path))
    if reveal is not None:   # P48 T3: the named later series joins this state
        ser_list = series.get("series") or []
        if not (0 < reveal < len(ser_list)) or not ser_list[reveal].get("later"):
            raise ValueError(f"chart_to extend: series {reveal} is not a later: true series of {path.name}")
        ser_list[reveal].pop("later", None)
    builder = LPG.pick_builder(series, variant)   # the PAGE's builder - a windowed series must not re-decide it by its point count
    if builder not in DOMAIN_BUILDERS:   # R26-223: ONE tuple - the builders a rescale admits are the builders a born domain admits
        raise ValueError(f"chart_to rescale: only a line or a bars page rescales (this page is {builder}); recast or cut")
    window = sp.get("window")
    axes = {}
    if window is not None:
        lo, hi = float(window[0]), float(window[1])
        offsets = []
        for ser in series.get("series") or []:
            if ser.get("later"):
                offsets.append(0); continue   # not on this state: no index to map
            pts = ser.get("pts", [])
            kept = [pt for pt in pts if lo - 1e-9 <= float(pt[0]) <= hi + 1e-9]
            if len(kept) < 2:
                raise ValueError(f"chart_to rescale: the window [{lo}, {hi}] keeps {len(kept)} point(s) of {ser.get('name') or 'the series'}: nothing to draw")
            offsets.append(next(i for i, pt in enumerate(pts) if lo - 1e-9 <= float(pt[0])))   # a datum index on the page maps to index - offset on this state
            ser["pts"] = kept
        axes["window_offsets"] = offsets
        hf = series.get("highlight_from")
        if hf is not None and hf != "" and not (lo <= float(hf) <= hi):
            series.pop("highlight_from", None)
        axes["xdomain"] = [lo, hi]
        # the page's own x ticks (years) fall outside a months-wide window: the derived state labels every kept point instead,
        # in the series' own token (a decimal year reads as "Feb '26"); a window that still holds the page's ticks keeps them
        own = [t for t in (series.get("xticks") or []) if isinstance(t, (list, tuple)) and lo <= float(t[0]) <= hi]
        if not own:
            first = (series.get("series") or [{}])[0].get("pts", [])
            labelled = [[float(x), LPG.decimal_year_label(x) or str(x)] for x, _ in first]
            step = max(1, -(-len(labelled) // 3))   # at most three labels across the window: a month label is ~110 px at the portrait size and four touched (the frames, 2026-09-10)
            series["xticks"] = labelled[::step]
    if sp.get("ymin") is not None or sp.get("ymax") is not None:
        axes["domain"] = [sp.get("ymin"), sp.get("ymax")]
    for k, v in axes.items():
        series[k] = v
    spec = LPG.build_spec(series, variant, emphasize, quiet_zone or "right", builder=builder)
    spec.setdefault("axes", {}).update(axes)
    spec["derived"] = "rescale"
    if axes.get("window_offsets"):
        spec["window_offsets"] = axes.pop("window_offsets")
        spec["axes"].pop("window_offsets", None)
    return stamp_full_stage(spec)   # R26-205: a derived state is the same plate as the page it comes from


MONTH_ABBR = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def month_of_x(x: float) -> str | None:
    """The month a fractional-year x names (2026.1667 -> 'Mar'), or None when x is not a month of a year - the page's
    own x units are years, so a monthly series' datum names a month and a bar's category can be checked against it."""
    x = float(x)
    frac = (x - (x // 1.0)) * 12.0
    k = int(round(frac))
    return MONTH_ABBR[k] if 0 <= k <= 11 and abs(frac - k) < 0.02 else None


def recast_data_key(A: dict, Bs: dict, tol: float = RECAST_DATA_TOL) -> tuple[list | None, str]:
    """E64 / R26-49 - THE DATA KEY, checked as a rule rather than looked up as a pair: a page that draws ONE line,
    whose named state is a bars page of n bars, is keyed on data when the bars ARE the line's own consecutive
    changes - bar k is the change from the line's datum (m - n + k) to (m - n + k + 1), m its last index - over the
    line's last n + 1 data, which must be consecutive periods, and the bars' categories (when they are months) must
    be those data's own months.

    Returns ``([{datum, bar, from}, ...], "")`` when the pair keys - the datum that travels, the bar it becomes, the
    datum it is measured from, so the engine never re-derives the correspondence - and ``(None, <the reason>)`` when
    it does not. The reason is the refusal's sentence and names the numbers that disagree: figures are never
    fabricated, so a bar that is merely CLOSE to the line's change is not that change."""
    lines = [s for s in (A.get("series") or []) if not s.get("later")]
    vals = list(Bs.get("values") or [])
    n = len(vals)
    if len(lines) != 1:
        return None, f"the data key reads ONE line's own data and this page draws {len(lines)} series"
    if not n:
        return None, "the named state has no bars - the data key hands each of n bars the line's own change"
    pts = list(lines[0].get("pts") or [])
    if len(pts) < n + 1:
        return None, f"{n} bar(s) need the line's last {n + 1} data and it carries {len(pts)}"
    tail = pts[len(pts) - n - 1:]
    steps = [float(tail[i + 1][0]) - float(tail[i][0]) for i in range(n)]
    if min(steps) <= 0 or (max(steps) - min(steps)) > 0.1 * max(steps):
        return None, "the line's last data are not consecutive periods - a change bar measures one step of the line"
    labels = [str(v or "").strip()[:3].title() for v in (Bs.get("labels") or [])]
    key_map, off = [], []
    for k, v in enumerate(vals):
        i = len(pts) - n + k
        d = float(pts[i][1]) - float(pts[i - 1][1])
        v = float(v)
        if abs(d - v) > tol * max(abs(d), abs(v), 1e-9):
            named = f" ({labels[k]})" if k < len(labels) and labels[k] else ""
            off.append(f"bar {k}{named} is {v:g} and the line's own change into datum {i} is {d:g}")
        month = month_of_x(pts[i][0])
        if month and k < len(labels) and labels[k] in MONTH_ABBR and labels[k] != month:
            off.append(f"bar {k} is labelled {labels[k]!r} and datum {i} is {month}")
        key_map.append({"datum": i, "bar": k, "from": i - 1})
    return (None, "; ".join(off)) if off else (key_map, "")


def remake_mark_map(line: dict, bars: dict, tol: float = RECAST_DATA_TOL) -> tuple[list | None, str, str]:
    """P61 T2 - THE WHOLE-CHART REMAKE's correspondence, derived and never authored: which datum of the line becomes
    which bar. Two keys, in order, and both are the bars' own numbers checked against the line's own:

      level   bar k IS the line's datum (its last n data, in order) - "month by month, this is what it stood at"
      change  bar k IS the line's own step into that datum - E64's data key, re-used whole (`recast_data_key`), so
              there is ONE rule for "a bar is a change" on this page and the remake does not re-derive it

    Returns ``([{datum, bar}, ...], <key>, "")`` or ``(None, "", <the reason>)``. The reason names the numbers that
    disagree: a bar that is merely close to a datum is not that datum (E77 - figures are never fabricated)."""
    lines = [s for s in (line.get("series") or []) if not s.get("later")]
    vals = list(bars.get("values") or [])
    n = len(vals)
    if len(lines) != 1:
        return None, "", f"a remake carries ONE line's own data into n bars and the line page draws {len(lines)} series"
    if not n:
        return None, "", "the bars page has no bars - a remake hands every bar a datum of the line"
    pts = list(lines[0].get("pts") or [])
    if len(pts) < n:
        return None, "", f"{n} bar(s) need the line's last {n} data and it carries {len(pts)}"
    tail = pts[len(pts) - n:]
    off = []
    for k, v in enumerate(vals):
        d, v = float(tail[k][1]), float(v)
        if abs(d - v) > tol * max(abs(d), abs(v), 1e-9):
            off.append(f"bar {k} is {v:g} and the line's datum {len(pts) - n + k} is {d:g}")
    if not off:
        return [{"datum": len(pts) - n + k, "bar": k} for k in range(n)], "level", ""
    key_map, why = recast_data_key(line, bars, tol)
    if key_map:
        return [{"datum": m["datum"], "bar": m["bar"]} for m in key_map], "change", ""
    return None, "", ("the bars are neither the line's own VALUES (" + "; ".join(off[:3])
                      + ") nor its own CHANGES (" + why + ")")


def derive_recast_key(A: dict, Bs: dict) -> tuple[object, list | None, str]:
    """E64: the key the COMPILER can see for itself, so a recast whose two states share their data is never the
    un-draw-then-draw the operator read as a cut. In order: by SERIES (the datum, `true`), by the terminal TAGS
    (`"tags"`, when every line is named at its end), by the DATA (`"data"`, with its key map). Returns
    ``(keyed, key_map, why)``; `keyed` is None when the two states share nothing the compiler can key, and `why` is
    the data key's reason - the last thing tried."""
    pair = (A.get("builder"), Bs.get("builder"))
    lines = [s for s in (A.get("series") or []) if not s.get("later")]
    n_bars = len(Bs.get("values") or [])
    if n_bars and len(lines) == n_bars:
        if pair in RECAST_PAIRS:
            return True, None, ""
        if pair in RECAST_TAG_PAIRS and all(str(s.get("name") or s.get("label") or "").strip() for s in lines):
            return "tags", None, ""
    key_map, why = recast_data_key(A, Bs)
    return (RECAST_DATA_KEY, key_map, "") if key_map else (None, None, why)


def derive_rescale_states(world: dict, row_species: list, plate_id: str, ep_dir: Path, sid: str | None = None) -> None:
    """Append one derived page state per `chart_to rescale` / `extend` on the row, in time order, and point each species
    at its state. An extend grows the CURRENT window (the page's whole series, or the last rescale's window) to
    `to_index`, or reveals a `later: true` series; the species carries `from_index` (the last shared datum) so the
    player caps the draw there."""
    check_target_series(world, row_species)   # R26-218: a series the page does not have, refused before it draws nothing
    for sp in (row_species or []):   # P48 T5: a morph moves the area under a line into another - both sides are line pages, or the refusal names the verb to use
        if isinstance(sp, dict) and sp.get("kind") == "chart_to" and sp.get("to") == "morph":
            if world.get("kind") != SPECIES_LEDGER:
                raise ValueError("chart_to morph: only a LEDGER PAGE has chart states")
            states = [world.get("page") or {}] + list(world.get("page_states") or [])
            k = int(sp.get("state", 0))
            if not (0 < k < len(states)):
                raise ValueError(f"chart_to morph: state {k} is not one of the page's other chart states")
            pair = (states[0].get("builder"), states[k].get("builder"))
            if pair[0] not in MORPH_BUILDERS or pair[1] not in MORPH_BUILDERS:
                raise ValueError(f"chart_to morph: {pair[0]} -> {pair[1]}: a morph moves the AREA UNDER A LINE into another ({'|'.join(MORPH_BUILDERS)} on both sides); "
                                 "n lines -> n bars is the keyed recast (keyed: true); anything else is the recast (the hand-over) or a cut")
            # P50 T12 (TR-7): the three match-cut invariants are measured on the PAIR ITSELF, here, before a player
            # exists - a bad match is a build error naming the number it missed by, never a silent bad morph that
            # M17 reports after the render. The same measurement the player makes (measure_morph.py's port of
            # arap.mjs), on the two strips the two pages would hand each other.
            import measure_morph as MM   # local: the gate's module chain, paid only by a page that morphs
            inv = MM.pair_invariants(states[0], states[k])
            if inv is None:
                raise ValueError(f"chart_to morph: state {k} - neither state carries a series to read a shape from; "
                                 "a morph moves the area under a LINE")
            if not (inv["centroid_ok"] and inv["axis_ok"] and inv["area_ok"]):
                raise ValueError(f"chart_to morph: state {k} - the pair fails the match-cut invariants (TR-7 / the brief B4, "
                                 f"measured on the two shapes by measure_morph.py): {MM.invariant_line(inv)}. A morph reads "
                                 "as ONE thing changing or it is a cut (E58: a morph's source is real or it is a cut) - use "
                                 "the recast (the hand-over), or cut")
            # doc 43 s43.5's decision rule, on the measured rotation; the row may name the method and override it
            sp["method"] = sp.get("method") or ("a" if inv["axis_deg"] <= METHOD_A_MAX_DEG else "arap")
            sp["invariants"] = {k2: round(inv[k2], 4) for k2 in ("centroid_shift", "axis_deg", "area_ratio")}
    for sp in (row_species or []):   # P61 T2 / E99 s34: the WHOLE-chart remake - the pair and its correspondence, checked before a frame exists
        if not (isinstance(sp, dict) and sp.get("kind") == "chart_to" and sp.get("to") == "remake"):
            continue
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError("chart_to remake: only a LEDGER PAGE has chart states")
        states = [world.get("page") or {}] + list(world.get("page_states") or [])
        k = int(sp.get("state", 0))
        if not (0 < k < len(states)):
            raise ValueError(f"chart_to remake: state {k} is not one of the page's other chart states")
        A, Bs = states[0], states[k]
        pair = (A.get("builder"), Bs.get("builder"))
        if pair not in REMAKE_PAIRS:
            if pair[0] == pair[1] == "dense-line":
                raise ValueError("chart_to remake: dense-line -> dense-line - the same form at another scale is the RESCALE, "
                                 "more of it is the EXTEND, and one line's area becoming another's is chart_to morph. A remake "
                                 "turns a chart into the OTHER form (line <-> bars)")
            raise ValueError(f"chart_to remake: {pair[0]} -> {pair[1]} is not a pair a remake can key ("
                             + ", ".join(f"{a} -> {b}" for a, b in REMAKE_PAIRS) + "); the same data in another form with no "
                             "datum correspondence is the recast (the hand-over, E64), n lines -> n bars is the keyed recast "
                             "(keyed: true), and a pair neither can honestly key is a cut")
        line_at = "from" if pair[0] == "dense-line" else "to"
        line_spec, bars_spec = (A, Bs) if line_at == "from" else (Bs, A)
        mark_map, key, why = remake_mark_map(line_spec, bars_spec)
        if not mark_map:
            raise ValueError(f"chart_to remake: state {k} - {why}. A remake carries every datum to its own bar, so the "
                             "correspondence must be the data themselves (E64's rule, not a guess); use the recast (the "
                             "hand-over), keyed: true / \"tags\" (the series key), or a cut")
        if any(isinstance(e, dict) and e.get("kind") == "retitle" for e in (row_species or [])):
            raise ValueError("chart_to remake: the remake re-writes the page's TITLE itself (E99 s34: the entire chart "
                             "transforms) - a retitle on the same row would write that one string twice. Drop the retitle, "
                             "or use the recast, which leaves the title alone")
        sp["mark_map"], sp["line_at"], sp["keyed_on"] = mark_map, line_at, key
        print(f"  {sid or 'row'} chart_to remake at {sp.get('at')}: {len(mark_map)} mark(s) keyed on {key} ({pair[0]} -> {pair[1]})")
    for sp in (row_species or []):   # P50 T6: a cross names CELLS - of a treemap page, and only labels that page carries
        if isinstance(sp, dict) and sp.get("kind") == SPECIES_CROSS:
            page = (world or {}).get("page") or {}
            if world.get("kind") != SPECIES_LEDGER or page.get("builder") != "treemap":
                raise ValueError("cross: the census's X marks land on a TREEMAP page (`ledger:<series>:treemap`); "
                                 f"this world is {page.get('builder') or world.get('kind') or 'a plate'!r}")
            labels = [str(x) for x in (page.get("labels") or [])]
            unknown = [str(c) for c in (sp.get("cells") or []) if str(c) not in labels]
            if unknown:
                raise ValueError(f"cross: the page has no cell named {', '.join(repr(u) for u in unknown)} - its parts are: "
                                 + ", ".join(labels[:8]) + (", ..." if len(labels) > 8 else ""))
            # E53 s1's census exception (c): no UNLABELLED cell is ever the argument. A cell whose name the
            # research floors culled (too small, or too long a name for its width) may not be crossed - on
            # either stage, because the page is read on both.
            for aspect, lay in sorted((page.get("layout") or {}).items()):
                tiers = {str(c.get("label")): int(c.get("tier") or 0) for c in (lay.get("cells") or [])}
                bare = [c for c in (sp.get("cells") or []) if tiers.get(str(c), 0) < 1]
                if bare:
                    raise ValueError(f"cross: {', '.join(repr(b) for b in bare)} - the page could not fit a label in that cell at "
                                     f"{aspect} (the research's floors: nothing under 80 x 36 px, no type under 18 px), and E53 s1's "
                                     "census exception (c) says no unlabelled cell is ever the argument. Give the part a shorter "
                                     "name on the page, or cross one the page can name")
    for sp in (row_species or []):   # P48 T4b: a keyed recast is admitted only on a legal pair, and the refusal names the
        # reason. E64/R26-49: and a recast the author left plain is KEYED BY THE COMPILER when the two states share their
        # data - the un-draw-then-draw the operator read as a cut at 0:50 was never a choice anyone made, it was a key
        # nobody had asked for. What the compiler cannot key it names, and the hand-over stays the author's to own.
        if not (isinstance(sp, dict) and sp.get("kind") == "chart_to" and sp.get("to") == "recast"):
            continue
        keyed = sp.get("keyed") or None
        if keyed and world.get("kind") != SPECIES_LEDGER:
            raise ValueError("chart_to recast keyed: only a LEDGER PAGE has chart states")
        states = [world.get("page") or {}] + list(world.get("page_states") or [])
        k = sp.get("state", 0)
        k = int(k) if isinstance(k, (int, float)) and not isinstance(k, bool) else 0
        if not (0 < k < len(states)):
            if not keyed:
                continue   # a plain recast's state index is the grammar's to refuse (validate_species), not the key's
            raise ValueError(f"chart_to recast keyed: state {k} is not one of the page's other chart states")
        A, Bs = states[0], states[k]
        if keyed == RECAST_DATA_KEY:   # E64: the DATA key, checked against the two specs' own numbers
            key_map, why = recast_data_key(A, Bs)
            if not key_map:
                raise ValueError(f'chart_to recast keyed "data": the bars are not the line\'s own changes - {why}. The data '
                                 "key hands each bar the difference between two consecutive data of the line (E64); use "
                                 "keyed: true / \"tags\" (the series key), the plain recast, or a cut")
            sp["key_map"] = key_map
        elif keyed:
            tags = keyed == "tags"   # P50 T11: the TAG form - each series' end tag is the mark that becomes its bar
            legal = RECAST_TAG_PAIRS if tags else RECAST_PAIRS
            pair = (A.get("builder"), Bs.get("builder"))
            if pair not in legal:
                raise ValueError(f"chart_to recast keyed{' tags' if tags else ''}: {pair[0]} -> {pair[1]} has no honest key correspondence (the legal pairs: "
                                 + ", ".join(f"{a} -> {b}" for a, b in legal) + "); use the plain recast (the hand-over), morph_to or a cut")
            lines = [s for s in (A.get("series") or []) if not s.get("later")]
            n_lines, n_bars = len(lines), len(Bs.get("values") or [])
            if n_lines != n_bars:
                raise ValueError(f"chart_to recast keyed: {n_lines} line(s) and {n_bars} bar(s) - a keyed recast needs one bar per series; a {n_lines}-line page has no {n_bars}-bar correspondence")
            if tags:
                # the tag IS the hand-over: a line the page never named has nothing to hand its bar, and a silent
                # cross-fade is the cut this verb exists to avoid (E53 s8: the name lives at the line's END)
                bare = [i for i, s in enumerate(lines) if not str(s.get("name") or s.get("label") or "").strip()]
                if bare:
                    raise ValueError(f"chart_to recast keyed: \"tags\" hands each line's TERMINAL TAG to its bar, and series "
                                     + ", ".join(str(i) for i in bare) + f" of {n_lines} carries no name or label to hand over - "
                                     "name every line at its end (E53 s8), or use keyed: true (the datum hands over instead)")
        elif world.get("kind") == SPECIES_LEDGER:   # E64: no key asked for - derive the one the data already say
            where = f"{sid or 'row'} chart_to recast at {sp.get('at')}"
            if "keyed" in sp:
                # P66 T3 (the parent, 2026-09-17), with E99 s67 Apply 2 (a chart never lands fully built): an AUTHORED
                # `keyed: false` is the author's EXPLICIT hand-over, in the grammar's own word above ("false / absent is
                # the hand-over"), and it is RESPECTED - the arriving state draws on its own build envelope. E64 derives
                # the key NOBODY asked for, so the derivation runs only where the key is ABSENT from the species.
                print(f"  {where}: no key - the plain recast (authored: keyed false)")
                continue
            derived, key_map, _why = derive_recast_key(A, Bs)
            sp["keyed"] = derived
            if derived:
                sp["keyed_derived"] = True
                if key_map:
                    sp["key_map"] = key_map
                print(f"  {where}: keyed {json.dumps(derived)} (derived - E64)")
            else:
                print(f"  {where}: no key - the plain recast (E64: a hand-over to name)")
    cur_window = None
    for sp in sorted((e for e in (row_species or []) if isinstance(e, dict) and e.get("kind") == "chart_to" and e.get("to") in ("rescale", "extend")), key=lambda e: e["at"]):
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError(f"chart_to {sp['to']}: only a LEDGER PAGE has chart states")
        states = world.setdefault("page_states", [])
        if len(states) + 1 >= STATE_MAX:
            raise ValueError(f"chart_to {sp['to']}: {len(states) + 2} chart states is past STATE_MAX ({STATE_MAX}): a fourth chart is a new page or a card")
        if sp["to"] == "rescale":
            if _follow_set(sp.get("follow")):   # R26-233: the LINE the domain's top tracks, resolved to its index
                sp["follow"] = rescale_follow_series(world, sp, row_species,
                                                     f"{sid or 'row'} chart_to rescale at {sp.get('at')}")
            states.append(rescale_state(plate_id, ep_dir, sp))
            if sp.get("window") is not None:
                cur_window = [float(sp["window"][0]), float(sp["window"][1])]
        else:
            first = (world["page"].get("series") or [{}])[0].get("pts") or []
            if not first:
                raise ValueError("chart_to extend: the page has no series to extend")
            if sp.get("to_index") is not None:
                idx = int(sp["to_index"])
                full = (LPG.load_series(Path(ep_dir) / "evidence/objects" / f"{parse_ledger_id(split_plate_opts(plate_id)[0])[0]}.series.json").get("series") or [{}])[0].get("pts") or []
                if idx >= len(full):
                    raise ValueError(f"chart_to extend: to_index {idx} is past the series' last datum ({len(full) - 1})")
                lo = cur_window[0] if cur_window else float(full[0][0])
                cur_hi = cur_window[1] if cur_window else float(full[-1][0])
                hi = float(full[idx][0])
                if hi <= cur_hi + 1e-9:
                    raise ValueError(f"chart_to extend: to_index {idx} (x={hi}) adds nothing past the standing window's end (x={cur_hi})")
                shared = max(i for i, pt in enumerate(full) if float(pt[0]) <= cur_hi + 1e-9)
                spec = rescale_state(plate_id, ep_dir, {"window": [lo, hi]})
                spec["derived"] = "extend"
                sp["from_index"] = shared
                cur_window = [lo, hi]
            else:
                spec = rescale_state(plate_id, ep_dir, {"window": cur_window} if cur_window else {}, reveal=int(sp["series"]))
                spec["derived"] = "extend"
                sp["from_series"] = int(sp["series"])
            states.append(spec)
        sp["state"] = len(states)


# ---- R26-205 / E99 s82: THE PAGE IS THE PLATE AT 16:9 ------------------------------------------
# The operator, on a bare frame of the H unit's copy d: *"why is the ledger being used at like 20%
# size? the whole point of a ledger plate is that the chart IS the world, you have it restricted to
# this square even when bare, it should be the whole plate."* Measured: the bare page's plot ran
# `[180, 236, 403, 244]` of a 1920x1080 stage. TWO reservations made that square, and the ruling
# closes both:
#   (a) THE CAPTION'S COLUMN. A landscape page's chart box is `(0.6 if quiet_zone else 0.9) * cb.w`
#       because the STAGE caption sits in the page's declared quiet zone (`caption_strip_x`, the
#       engine's `cap.style.left = qz === "right" ? "58%"`). At 16:9 a page row's caption goes to the
#       ANCHORED strip instead (`ledger_page.CAPTION_ANCHOR["16:9"]`, x[145,1775] y[878,960]) - the
#       strip that has existed since E62 and that only a live dock ever demoted a caption to - so no
#       column is needed and the chart takes the stage (`ledger_page.LAND_FULL`).
#   (b) THE CARD'S COLUMN. E65's placer gives a card the plot's own room, so a page never needed one
#       kept empty either; `page_place` is unchanged by this row.
# STAGE mode is untouched everywhere else: a PLATE row keeps it at both aspects (a plate has no plot
# to be in the column of), and a 9:16 page keeps it because a portrait page's caption already sits in
# its own strip under the page (`#caption.stage.onpage`, the template's `left: 80 / right: 200`).
#
# WHY `caption: "anchor"` AND NOT A NEW KEY: the engine has read `page.caption === "anchor"` since the
# host-plate proof (C5) - it is the one door that puts the caption in the anchored strip and keeps it
# there under a card. This row makes a 16:9 page row take that door by default. `full_stage` is the
# geometry half and is separate on purpose: a host plate is anchored and is NOT full stage.
def stamp_full_stage(page: dict) -> dict:
    """R26-205: at 16:9, stamp this page as the plate - the chart on the whole stage, the caption in
    the anchored strip. In place, and the page is returned for chaining.

    Nothing is written at 9:16 (the page already fills the frame) nor on a HOST PLATE (a page that
    declares its own `board` / `chart_box` / `punch: False` had its board measured around a hand), so
    a portrait build and the host-plate proof compile the bytes they compiled before this row. A page
    that already declares `caption` keeps what it declared."""
    if ASPECT not in (None, "16:9"):
        return page
    if page.get("board") or page.get("chart_box") or page.get("punch") is False:
        return page
    page["full_stage"] = True
    page.setdefault("caption", "anchor")
    return page


def page_is_full_stage(world: dict | None, aspect: str | None) -> bool:
    """Is this scene's world a page whose chart is the whole stage (R26-205)? One reader for the
    caption pass and the band stamp, so neither can disagree with `ledger_page.full_stage`."""
    if not isinstance(world, dict) or world.get("kind") != SPECIES_LEDGER:
        return False
    page = world.get("page")
    return isinstance(page, dict) and LPG.full_stage(page, aspect or "16:9")


def ledger_world(plate_id: str, ken: tuple, ep_dir: Path, dock_badges: list | None = None) -> dict:
    """The LEDGER PAGE world for a ``ledger:`` plate id: ``world.page`` is the
    ``ledger_page.v1`` spec from ``<ep_dir>/evidence/objects/<series>.series.json``
    (doc 29 s9.26: data only from a series.json; s9.28: surface x builder are
    two axes). No asset_id / sha256 - the player draws the page."""
    series_id, variant, emphasize, quiet_zone, enter, exit_ = parse_ledger_id(plate_id)
    path = Path(ep_dir) / "evidence/objects" / f"{series_id}.series.json"
    if not path.exists():
        raise ValueError(f"{plate_id!r}: series file missing: {path}")
    try:
        series = LPG.load_series(path)
    except (OSError, ValueError) as exc:
        raise ValueError(f"{plate_id!r}: cannot read {path}: {exc}") from exc
    errors = LPG.validate(series, variant)
    if errors:
        raise ValueError(f"{plate_id!r}: {path.name} is not a page ({variant}): " + "; ".join(errors))
    page = LPG.build_spec(series, variant, emphasize, quiet_zone)
    if enter:
        if enter == "surface":
            raise ValueError(f"{plate_id!r}: surface= must name a paper surface and positive lead seconds")
        if enter.startswith("surface="):
            if page.get("builder") != "dense-line":
                raise ValueError(f"{plate_id!r}: surface= is only allowed on a dense-line page (this page is "
                                 f"{page.get('builder')!r})")
            # Parse the handoff before checking the build aspect.  The lead is
            # part of the surface grammar and must retain its established
            # refusal when a previous compile left the module-level ASPECT at
            # 9:16.  A valid surface still receives the 16:9-only refusal.
            surface_meta = _parse_surface_entry(enter, plate_id, series_id, variant, path)
            if ASPECT not in (None, "16:9"):
                raise ValueError(f"{plate_id!r}: surface= is 16:9-only; portrait page surfaces need an explicit "
                                 "aspect-specific registration")
            page["enter"] = "surface"
            page["surface_from"] = surface_meta
            # Keep the destination's source binding independent of the public handoff
            # record; the binder removes this private check key before serialization.
            page["_surface_source_ref"] = copy.deepcopy(surface_meta["source_ref"])
        else:
            page["enter"] = enter.split("=")[0]   # the player: a returning page unwinds from its point (LP_RETRACT.IN); a mount builds its cream first
        if "=" in enter and (enter.startswith("snap") or enter.startswith("camera")):
            page["snap_from"] = enter.split("=", 1)[1]   # the dock asset the page grows from - or, for enter=camera, the card the eye goes to (P49 T5)
        elif "=" in enter and enter.startswith("throw"):   # throw=<grow>[,<from>[,<s>]] - the growth law (snap | growth), the side, the flight
            grow, *rest = enter.split("=", 1)[1].split(",")
            if grow == "depth":   # E99 s25: renamed - growth and depth are two different things
                raise ValueError(f"{plate_id!r}: throw=depth was renamed throw={PAGE_THROW_GROW_GROWTH} (E99 s25): the "
                                 f"growth law is not a depth - say throw={PAGE_THROW_GROW_GROWTH}, or depth=<k> for a real plane")
            if grow not in ("snap", PAGE_THROW_GROW_GROWTH):
                raise ValueError(f"{plate_id!r}: throw grow {grow!r} is not snap|{PAGE_THROW_GROW_GROWTH}")
            page["throw_grow"] = grow
            if rest and rest[0]:
                if rest[0] not in ("below", "above", "left", "right"):
                    raise ValueError(f"{plate_id!r}: throw side {rest[0]!r} is not below|above|left|right")
                page["throw_from"] = rest[0]
            if len(rest) > 1 and rest[1]:
                page["throw_s"] = float(rest[1])
        elif "=" in enter and not enter.startswith("surface="):
            key = "morph_s" if enter.startswith("morph") else "mount_s"   # the mount phase (world fades, cream builds) before the page's own clock starts; a morph's seconds
            page[key] = float(enter.split("=", 1)[1])
    if exit_:
        page["exit"] = exit_    # the player: no retract, the page leaves on the cut
    # the evidence dock's authored badges for this asset land on the page too (the key for the
    # viewer), synced to the series' own labels - never a second copy of the numbers
    if dock_badges:
        conflicts = LPG.badge_key_conflicts(series, dock_badges)
        if conflicts:
            raise ValueError(f"{plate_id!r}: " + "; ".join(conflicts))
        page["badges"] = LPG.badges_for(series, dock_badges)
    stamp_full_stage(page)
    return {"kind": SPECIES_LEDGER, "page": page,
            "ken_burns": {"scale": ken[0], "x": ken[1], "y": ken[2]}}


# HF-16 (P50 T15) - THE WIRE: `;thread=<mark key>` on the ARRIVING page's plate id names one mark of the page
# BEFORE it that survives the cut - the holdings baseline still lying under the Meta bars. The intake's HF-16
# ("the three threads ... one continuous line as the film's spine") against our own persistence rule (s9.15):
# ours persists the PAGE, and a thread persists one element across a page CHANGE.
#
# WHY THE PLATE ID AND NOT `chart_to extend`. A species lives on ONE scene and addresses that scene's own
# `world.page_states`, every one of which is built from the SAME series file by `derive_rescale_states`; an
# `extend` names `to_index` INTO the page's own points. Nothing in that grammar can name a mark on the world
# before it, and teaching species to reach across a scene boundary is a far larger mechanism than the thing it
# buys. Declared on the plate id, the thread is what it actually is - a property of the arriving PAGE ("this
# page starts with that mark already on it") - it needs no new species, and it survives every entry a page can
# make (a cut, a mount, a spiral). The carry math is `scripts/species/thread.mjs`; the player draws it as
# GROUND under the new page's own ink and it is an ordinary keyed mark from that frame on.
#
# E50's CLOCK DOES NOT RESTART. The wire arrives already drawn, on the page's first frame, so it can never be
# the page's LAST data mark - which is what E50 dates a page by and what M21 measures the deployed life from.
# It is one more data mark on the second page (M21 counts it), never the latest one, so the deployed clock the
# gate reads is the new page's own build, unchanged.
THREAD_KEYS = ("s<n>", "b:<n>", "rule:<n>")   # the mark keys the compiler can check against the page before it: a series, a bar, an hline
THREAD_KEY_RE = re.compile(r"^(?:s(\d+)|b:(\d+)|rule:(\d+))$")


def thread_mark_error(prev_world: dict | None, key: str, where: str) -> str | None:
    """Can the scene BEFORE this one hand over a mark called `key`? The message, or None.

    The player's mark keys are the template's own (`lpMark`); these three are the ones a page spec can be read
    for without running a builder, which is the whole of what a compiler may honestly claim."""
    m = THREAD_KEY_RE.match(str(key or ""))
    if not m:
        return (f"{where}: thread={key!r} is not a mark key this build can check - one of {'|'.join(THREAD_KEYS)} "
                "(a series, a bar, an hline of the page before this one)")
    page = (prev_world or {}).get("page") if isinstance(prev_world, dict) else None
    if not page or (prev_world or {}).get("kind") != SPECIES_LEDGER:
        return (f"{where}: thread={key!r} carries one mark across a page boundary, and the scene before this one is "
                "not a ledger page - there is no page to hand it over (HF-16)")
    axes = page.get("axes") or {}
    have = {"s": len(page.get("series") or []),
            "b": len(page.get("values") or []),
            "rule": len(axes.get("hlines") or ([axes["hline"]] if axes.get("hline") is not None else []))}
    kind = "s" if key.startswith("s") else "b" if key.startswith("b:") else "rule"
    index = int(next(g for g in m.groups() if g is not None))
    one, many = {"s": ("series", "series"), "b": ("bar", "bars"), "rule": ("rule", "hlines")}[kind]
    if index >= have[kind]:
        return (f"{where}: thread={key!r} names {one} {index} of {str(page.get('title'))[:40]!r}, which draws "
                f"{have[kind]} {many} - the page before this one never drew that mark")
    return None


def plate_drift_px(value, where: str) -> float:
    """E99 s55, amended s63: ``;drift=<px>`` - the plate idle walk's half-width in stage px, for THIS scene. ValueError names the
    floor, the ceiling and the two ruled settings; the caller names the row. The floor is
    ``kinetics/idle.mjs`` IDLE.DRIFT_PX itself (E49: nothing ever goes truly still), so a number under it is not a
    quieter drift, it is an attempt to switch E49 off - refused here rather than silently raised."""
    try:
        px = float(str(value).strip())
    except ValueError:
        raise ValueError(f"{where}: drift {value!r} is not a number of stage px "
                         f"({PLATE_DRIFT_LONG:g} = the long-form setting, {PLATE_DRIFT_SHORTS:g} = shorts; E99 s63)") from None
    if px < PLATE_DRIFT_FLOOR:
        raise ValueError(f"{where}: drift {px:g} px is under the floor {PLATE_DRIFT_FLOOR:g} px - that floor is "
                         f"kinetics/idle.mjs IDLE.DRIFT_PX, E49's 'nothing ever goes truly still', and it is not a "
                         f"dial to go under. Name {PLATE_DRIFT_LONG:g} (long form) or {PLATE_DRIFT_SHORTS:g} "
                         f"(shorts), or drop drift= and take the floor (E99 s63)")
    if px > PLATE_DRIFT_MAX:
        raise ValueError(f"{where}: drift {px:g} px is past the ceiling {PLATE_DRIFT_MAX:g} px - `.world` is inset "
                         f"-5 %, so a wider walk carries the plate's own EDGE onto the stage. A move bigger than "
                         f"this is a CAMERA move (E49: a camera move is a camera move; a hold holds at its idle)")
    return px


PLATE_ROOM_KEYS = ("x", "y", "w", "h")   # the four fractions a plate's declared room is written in, in this order


def plate_room_spec(value, where: str) -> list[float]:
    """``;room=<x>,<y>,<w>,<h>`` -> the four fractions, validated (R26-221).

    A PICTURE PLATE's answer to a page's `quiet_zone`: the rectangle of THIS plate a card may stand in. Fractions
    of the stage rather than pixels, because a world is authored once and the compiler instantiates the same
    timeline at either aspect - the same reason a species' `target` is written in fractions. ValueError names the
    option; the caller names the row."""
    parts = [v.strip() for v in str(value).split(",")]
    if len(parts) != 4 or not all(parts):
        raise ValueError(f"{where}: room {str(value)!r} is not {','.join(PLATE_ROOM_KEYS)} - four fractions of the "
                         "stage (0..1) naming the rectangle of this plate a card may stand in, the way a page "
                         "declares its quiet zone (R26-221)")
    try:
        box = [float(v) for v in parts]
    except ValueError:
        raise ValueError(f"{where}: room {str(value)!r} is not four numbers - "
                         f"{','.join(PLATE_ROOM_KEYS)} as fractions of the stage (0..1)") from None
    if not all(math.isfinite(v) for v in box):   # `float("nan")` passes every `>` guard below and `float("inf")`
        # passes three of them; both then reach `plate_room_px` and die there with no row named. A fraction is finite.
        raise ValueError(f"{where}: room {str(value)!r} is not four numbers - "
                         f"{','.join(PLATE_ROOM_KEYS)} as fractions of the stage (0..1)")
    x, y, w, h = box
    if not (w > 0 and h > 0):
        raise ValueError(f"{where}: room {str(value)!r} is empty - w and h are fractions of the stage and both must "
                         "be greater than 0")
    if min(x, y) < 0 or x + w > 1 + 1e-9 or y + h > 1 + 1e-9:
        raise ValueError(f"{where}: room {str(value)!r} runs off the stage - x, y, w, h are fractions in 0..1 and "
                         "x+w and y+h are at most 1")
    return box


def _check_opt(key: str, value, where: str) -> None:
    if key == "thread":   # HF-16: the shape here, the page before it in `thread_mark_error` (which needs that page)
        if THREAD_KEY_RE.match(str(value)):
            return
        raise ValueError(f"{where}: thread {value!r} is not a mark key - one of "
                         f"{'|'.join(THREAD_KEYS)} (a series, a bar or an hline of the page before this one)")
    if key == "pill":   # P50 T11 / R26-34: yes | no | the datum index the pill POPS at (springPop, Mp 0.05)
        if value in ("yes", "no") or (value.isdigit() and int(value) >= 0):
            return
        raise ValueError(f"{where}: pill {value!r} is not yes|no|<datum index> (the milestone the pill pops at - "
                         "a non-negative index of the page's first series)")
    if key == "depth":   # P58 T4: the page's own parallax factor - the range is the camera's, not a second one
        page_depth_k(str(value), where)
        return
    if key == "plane":   # P58 T4: the surface the page is drawn on - the quad is resolved and checked here
        err = page_plane_error(page_plane_spec(str(value), where), where)
        if err:
            raise ValueError(err)
        return
    if key == PLATE_DRIFT_OPT:   # E99 s55: the plate idle drift's half-width in stage px, authored per scene
        plate_drift_px(value, where)
        return
    if key == "form":   # P58 T5: the NAME and the tilt are the row's own grammar; the fit to the page's builder
        page_form_geom(str(value), where)   # needs the page, and is checked where the page is read (ledger_world)
        return
    if key == "field":   # E99 s35: the NAME is the row's own grammar; whether `plates` HAS its two plates needs the
        page_field_spec(str(value), None, where)   # page, and is checked where the page is read (ledger_world)
        return
    if key == "room":   # R26-221: the four fractions are the row's own grammar; that the world IS a picture plate
        plate_room_spec(value, where)   # needs the world, and is checked where the world is read (world_for_plate)
        return
    if key == "domain":   # R26-223: the pair is the row's own grammar; the fit to the page's BUILDER needs the page,
        page_domain_spec(value, None, where)   # and is checked where the page is read (world_for_plate), as form='s is
        return
    if key == "readability":   # P69 T8: the NAME (and a long form's preset) is the row's own grammar; the fit to the
        if LPG.parse_readability(value) is None:   # page's builder needs the page, and is checked in world_for_plate
            raise ValueError(f"{where}: readability {value!r} is not one of {LPG.LANDSCAPE_PHONE}|{LPG.LONGFORM}"
                             f"[:{'|'.join(LPG.LONGFORM_PRESETS)}]")
        return
    if key == "build":   # R26-226: the mode and its seconds are the row's own grammar; the fit to the page's BUILDER
        page_build_spec(value, None, None, where)   # and to its SERIES COUNT needs the page, and is checked where the
        return                                      # page is read (world_for_plate), as domain='s is
    allowed = {"idle": IDLE_KINDS, "arrive": ARRIVALS, "mass": MASSES, "morph": MORPH_SHAPES,
               "card": ("yes", "no"), "use": PLATE_USES, "path": RACE_PATHS}[key]
    if value not in allowed:
        raise ValueError(f"{where}: {key} {value!r} is not one of {'|'.join(allowed)}")


# P69 T8 / R26-259 - THE LONG FORM'S FACE. The template NAMES Inter and never loads it (the spec found every
# "Inter" on the page rendering as Arial), so a longform page carries the tracked, OFL Inter it is set in: the
# variable font rides the ASSET MAP (as every plate does) under this key, only when a scene's page asks for the
# profile, and the engine registers it as its own family (`LP_LONGFORM.FACE`) so nothing outside the profiled
# page changes face. A build with no longform page carries no font and is byte-identical.
LONGFORM_FONT_ASSET = "font:inter-longform"
LONGFORM_FONT_FILE = REPO / "content/video_engine/src/assets/fonts/Inter-Variable.ttf"


def longform_assets(timeline: dict) -> dict:
    """``{LONGFORM_FONT_ASSET: data uri}`` when any scene's page (or chart state) is drawn under the
    `longform` profile, else ``{}``. Pure apart from reading the tracked font file. A 9:16 timeline carries
    none (REVIEW-P69-LANE-B-MERGE-2 N4): the player never draws the profile in portrait, so the 1.17 MB face
    would ride a build that never sets a word in it."""
    if (timeline.get("aspect") or "16:9") == "9:16":
        return {}
    for sc in timeline.get("scenes") or []:
        world = sc.get("world") or {}
        pages = [world.get("page")] + list(world.get("page_states") or [])
        if any(isinstance(p, dict) and (p.get("axes") or {}).get("readability") == LPG.LONGFORM for p in pages):
            return {LONGFORM_FONT_ASSET: "data:font/ttf;base64," + base64.b64encode(LONGFORM_FONT_FILE.read_bytes()).decode()}
    return {}


PLATE_ARRIVALS_REFUSED = ("stamp",)   # R26-20 send-back #2 (M1): the page's PILLS land or are thrown; no pill painter stamps, and a stamped pill rendered silently as a landing


def split_plate_opts(plate_id: str) -> tuple[str, dict]:
    """``<plate id>[;idle=<kind>][;arrive=<how>][;mass=<material>]`` -> (the bare plate id, the options). E49's idle and
    P47 T1's arrivals are NAMED per plate on the shot row; ValueError names the option, the caller names the row."""
    if ";" not in plate_id:
        return plate_id, {}
    bare, *parts = plate_id.split(";")
    opts: dict = {}
    for part in parts:
        if "=" not in part or part.split("=", 1)[0] not in PLATE_OPTS:
            raise ValueError(f"{plate_id!r}: plate option {part!r} is not one of {'|'.join(k + '=' for k in PLATE_OPTS)}")
        k, v = part.split("=", 1)
        if k == "then":   # P48 T4: names another object, so it is checked by loading it, not against an enum; may repeat
            opts.setdefault("then", []).append(v)
            continue
        _check_opt(k, v, repr(plate_id))
        if k == "arrive" and v in PLATE_ARRIVALS_REFUSED:   # M1: refused by name rather than painted as another arrival
            raise ValueError(f"{plate_id!r}: arrive={v} is a DOCK's arrival - a page's pills land or are thrown, and no "
                             "pill painter stamps (put the stamp on a dock: `arrive: stamp` in the row's dock options)")
        opts[k] = v
    return bare, opts


def split_idle(plate_id: str) -> tuple[str, str | None]:
    """The idle option alone (E49) - see split_plate_opts."""
    bare, opts = split_plate_opts(plate_id)
    return bare, opts.get("idle")


PHRASE_KEYS = ("x0", "y0", "x1", "y1")


def press_meta(raw) -> dict:
    """A PRESS dock's card meta: the dict ``press_card.py`` wrote, or the path to that JSON.

    Returns only what the player needs - the kind, the source line, the phrase box, the phrase's
    WORDS (R26-55: the player sets them as live type, re-lined to the surface the card lands on) and
    the card's own aspect (from the crop's size, so the provenance strip needs no decode) - so the
    provenance keys the tool also writes (the crop rectangle, the screenshot's sha256) stay on disk
    and out of the timeline. The words and the aspect are OPTIONAL: a card cut before R26-55 carries
    neither, keeps its raster phrase, and compiles byte-for-byte as it did.
    ValueError names the option; the caller names the row and the dock."""
    meta = raw
    if isinstance(raw, (str, Path)):
        p = Path(raw)
        if not p.is_file():
            raise ValueError(f"dock: press {str(raw)!r} is not a file - press_card.py writes the card's meta JSON beside its PNG")
        try:
            meta = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"dock: press {p.name} is not JSON ({exc})") from exc
    if not isinstance(meta, dict):
        raise ValueError("dock: press must be the card meta dict press_card.py writes, or the path to it")
    src = meta.get("source")
    if not isinstance(src, str) or not src.strip():
        # B1 / A2a: their claim is a card, and the card says whose claim it is
        raise ValueError("dock: press needs a non-empty 'source' (the masthead and the date) - a press card without its source is not evidence")
    ph = meta.get("phrase")
    if not isinstance(ph, dict) or any(isinstance(ph.get(k), bool) or not isinstance(ph.get(k), (int, float))
                                       or not 0.0 <= float(ph[k]) <= 1.0 for k in PHRASE_KEYS):
        raise ValueError(f"dock: press 'phrase' must be {{{', '.join(PHRASE_KEYS)}}} as fractions of the CARD in 0..1")
    if not (float(ph["x0"]) < float(ph["x1"]) and float(ph["y0"]) < float(ph["y1"])):
        raise ValueError("dock: press 'phrase' is empty or inverted - x0 < x1 and y0 < y1 (the region of the headline the sentence turns on)")
    words = meta.get("phrase_text")
    if words is not None and (not isinstance(words, str) or len(words.split()) < 2):
        raise ValueError("dock: press 'phrase_text' must be the quoted phrase's own words (two or more) - "
                         "it is what the player sets as live type over the provenance strip (R26-55)")
    card = meta.get("card")
    aspect = None
    if isinstance(card, (list, tuple)) and len(card) == 2:
        cw, chh = card
        if isinstance(cw, (int, float)) and isinstance(chh, (int, float)) and cw > 0 and chh > 0:
            aspect = round(float(chh) / float(cw), 5)
    return {"kind": DOCK_KIND_PRESS, "source": src.strip(),
            "phrase": {k: round(float(ph[k]), 5) for k in PHRASE_KEYS},
            # R26-55, written ONLY when the card carries them, so a card cut before it compiles unchanged
            **({"phrase_text": " ".join(words.split())} if words else {}),
            **({"img": aspect} if aspect else {})}


# HF-17 (P50 T15) - THE FOREGROUND OCCLUDER. "Occlusion beats blur as the depth cue" (the intake, against doc
# 29's open focus-rack proposal; the operator has preferred the wash to a rack since 2026-09-06). A world plate
# may declare cutouts that belong IN FRONT of whatever lands on it - the desk edge the card slides behind, the
# lamp it passes under - and a dock names one: `behind: "<layer>"` on the row's dock options.
#
# WHERE THE LAYER IS DECLARED. Beside the plate, in `<plate>.layers.json`:
#     {"foreground": {"<layer name>": "<png beside the plate, with alpha>"}}
# A sidecar, not a new asset id: the layer is not a plate of its own (it can never be a world), it is part of
# THIS plate, and it travels with it. The compiler refuses a `behind` the plate does not declare and a declared
# file that is not on disk - the two ways this goes wrong silently, which would be a card that simply never got
# occluded and a frame nobody could explain. The PNG is embedded RAW (`data_uri` with no cap): the cap path
# re-encodes through RGB and would throw the alpha away, which is the whole layer.
FG_PREFIX = "fg:"          # the asset-map key a foreground layer rides: `fg:<plate asset id>:<layer>`
FG_LAYERS_SUFFIX = ".layers.json"


def plate_layers(path: Path | None) -> dict:
    """The FOREGROUND layers a plate declares, `{name: Path}`. No sidecar, or a malformed one, is no layers -
    a plate is not required to have a front, and only a row that NAMES one gets an error."""
    if path is None:
        return {}
    side = Path(path).with_suffix(FG_LAYERS_SUFFIX)
    try:
        data = json.loads(side.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    fg = (data or {}).get("foreground") if isinstance(data, dict) else None
    if not isinstance(fg, dict):
        return {}
    return {str(k): Path(path).parent / str(v) for k, v in fg.items() if isinstance(v, str) and v}


def behind_error(world: dict, layers: dict, layer: str, where: str) -> str | None:
    """Can this scene's world paint `layer` over a card? The message, or None."""
    if not isinstance(world, dict) or not world.get("asset_id") or world.get("kind") in (SPECIES_LEDGER, VECMAP_KIND, SPECIES_CLIP):
        return (f"{where}: behind={layer!r} needs a world PLATE with a foreground layer - this scene's world is "
                f"{(world or {}).get('kind') or 'a drawn page'}, which has no front to hide a card behind (HF-17)")
    if layer not in layers:
        named = ", ".join(sorted(layers)) if layers else "none"
        return (f"{where}: behind={layer!r} is not a foreground layer of {world['asset_id']!r} - it declares {named}. "
                f"Name it in <plate>{FG_LAYERS_SUFFIX} as {{\"foreground\": {{\"{layer}\": \"<png with alpha>\"}}}}")
    if not layers[layer].is_file():
        return (f"{where}: behind={layer!r} of {world['asset_id']!r} points at {layers[layer].name}, which is not on disk")
    return None




# P58 T3 - THE DEPTH PLANES A WORLD CARRIES. HF-17's `fg:` route, one depth down: a plate that ships in PLANES
# declares them in the SAME sidecar (`<plate>.layers.json`, `{"layers": [{path, role, depth, alpha, generator}]}`,
# back to front - P58 T2 / doc 24 "2.5D depth planes"), and the compiler hands the player one element's worth of
# information per plane: the asset key it rides, its parallax factor k, and its role.
#
#     world["layers"] = [{"key": "ly:<plate asset id>:<role>", "k": <doc 24's parallax factor>, "role": "<plane>"}]
#
# A FLAT plate's world is UNCHANGED - no key is added at all, so every timeline that compiled before this slice
# compiles byte-identically. The PNG is embedded RAW, exactly as `fg:` is: the capped path re-encodes through RGB
# and would throw the alpha away, which on a depth plane is the whole plane.
#
# THE REFUSALS ARE THE INDEXER'S, RUN AGAIN AT BUILD TIME (HF-17's rule: the two ways this goes wrong silently -
# a plane the sidecar does not declare and a file that is not on disk - would each resolve to a frame nobody could
# explain, a plate that simply never separated). build_plate_library.plate_depth_layers owns the vocabulary, the
# role -> k table and every message, so there is ONE table; the library indexes, the compiler refuses again.
LY_PREFIX = "ly:"          # the asset-map key a depth plane rides: `ly:<plate asset id>:<role>`


def plate_depth_planes(path: Path | None) -> list[dict]:
    """The DEPTH planes this plate declares, back to front, or [] when it ships flat. Raises ValueError, named,
    when the sidecar declares planes that do not hold (the indexer's own refusals, at build time)."""
    if path is None:
        return []
    import build_plate_library as BPL
    return BPL.plate_depth_layers(Path(path)) or []


# P50 T7 - THE ART-EMBED SURFACE. Bravos has the chart world and the TV world (their claims on a monitor in a lit
# studio); we have the chart world (the ledger page) and the ART world - our own narrative plates. E33's objection to
# docking anything to a generated plate is that it has no addressable coordinate space: a diffusion model decided
# where the wall is. The answer is to MEASURE one flat surface in the painting and declare it by name, beside the
# plate, in the SAME sidecar the foreground layers use:
#
#     {"foreground": {...}, "embed": {"poster": {"quad": [[x, y] x 4], "darken": "<word>"}, "tv": {...}}}
#
# A NAMED SET, not one quad (the approved order, 2026-09-11: "we have multiple surfaces we can work with, and
# punch/project into") - `poster`, `tv`, `laptop`, `paper` are names an author picks, not a fixed vocabulary. The
# corners are STAGE FRACTIONS in TL TR BR BL order, read off the still itself. A dock names the one it lands on
# (`embed: "poster"`), and the camera can take the same surface as a target (E59 reason 4).
#
# The compiler's whole job is that the surface EXISTS and can be read: the four ways this goes wrong silently are a
# name the plate does not declare, a quad that is not a quad (folded, wound the wrong way, off the stage), a surface
# too small for a card to read on a phone, and a CHART landing on a wall - which B1 forbids outright (their claim on
# their surface, ours on the page). All four are refused by name here rather than resolving to a frame nobody can
# explain. The surface itself stays BLANK in the painting (E33 / doc 15 s4): the information layer is composited.
EMBED_KEY = "embed"
EMBED_MIN_W = 0.25         # the surface's width as a share of the stage: under this a projected card cannot be read on a phone
                           # (the plate ORDER asks for 40 %; the compiler's floor is the hard one - a quarter of the frame)
EMBED_REFUSED_SPECIES = ("chart",)   # B1: the argument's own charts never embed
EMBED_FITS = ("cover", "contain")    # 2026-09-13: how a PICTURE (a still or a clip) takes its surface - `fit` on the row
EMBED_FIT_DEFAULT = "cover"          # E95: a still or a clip on a surface fills it, whole, unless the row says contain


def plate_embeds(path: Path | None) -> dict:
    """The SURFACES a plate declares, `{name: {"quad": [...], "darken": ...}}`. No sidecar, or a malformed one, is no
    surfaces - a plate is not required to carry one, and only a row that NAMES one gets an error (plate_layers' rule)."""
    if path is None:
        return {}
    side = Path(path).with_suffix(FG_LAYERS_SUFFIX)
    try:
        data = json.loads(side.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    emb = (data or {}).get(EMBED_KEY) if isinstance(data, dict) else None
    if not isinstance(emb, dict):
        return {}
    return {str(k): v for k, v in emb.items() if isinstance(v, dict)}


def _quad_points(quad) -> list[tuple[float, float]] | None:
    if not isinstance(quad, (list, tuple)) or len(quad) != 4:
        return None
    out = []
    for p in quad:
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            return None
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in p):
            return None
        out.append((float(p[0]), float(p[1])))
    return out


def embed_quad_error(name: str, spec, where: str) -> str | None:
    """Is this a surface a card can be projected onto? The message, or None.

    The law: four points, each ON the stage (0..1 fractions); CONVEX and in TL TR BR BL order (every turn the same
    way round - a folded or mis-ordered quad maps the card onto itself and reads as a tear); and at least
    EMBED_MIN_W of the stage wide, measured as the mean of its two horizontal edges."""
    if not isinstance(spec, dict):
        return f"{where}: embed {name!r} must be an object with a 'quad' of four [x, y] corners"
    pts = _quad_points(spec.get("quad"))
    if pts is None:
        return (f"{where}: embed {name!r} 'quad' must be four [x, y] corners in TL TR BR BL order "
                "(stage fractions, the corners read off the plate's own still)")
    if any(not 0.0 <= v <= 1.0 for p in pts for v in p):
        return f"{where}: embed {name!r} has a corner off the stage - every [x, y] is a 0..1 fraction of the frame"
    signs = []
    for i in range(4):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % 4]
        cx, cy = pts[(i + 2) % 4]
        signs.append((bx - ax) * (cy - by) - (by - ay) * (cx - bx))
    if any(s <= 0 for s in signs):
        return (f"{where}: embed {name!r} is not a convex quad in TL TR BR BL order (the corners turn "
                f"{'both ways' if any(s > 0 for s in signs) else 'the wrong way'}) - read them clockwise from the "
                "top left of the surface")
    width = ((pts[1][0] - pts[0][0]) + (pts[2][0] - pts[3][0])) / 2
    if width < EMBED_MIN_W:
        return (f"{where}: embed {name!r} is {width:.0%} of the stage wide, under the {EMBED_MIN_W:.0%} floor - "
                "a card projected onto it cannot be read on a phone (the plate order asks for 40 %)")
    dk = spec.get("darken")
    if dk is not None and not ((isinstance(dk, str) and dk.strip())
                               or (isinstance(dk, (int, float)) and not isinstance(dk, bool) and dk >= 0)):
        return (f"{where}: embed {name!r} 'darken' must be the WORD the room dims on (a phrase from the take) "
                "or a second on the timeline")
    return None


def embed_error(world: dict, embeds: dict, name: str, where: str, species: str | None = None) -> str | None:
    """Can this dock land on that surface? The message, or None."""
    if species in EMBED_REFUSED_SPECIES:
        return (f"{where}: embed={name!r} on a {species} card - the argument's own charts never embed (B1: their "
                "claim on their surface, ours on the page). A press card or a still card lands on a painted surface")
    if not isinstance(world, dict) or not world.get("asset_id") or world.get("kind") in (SPECIES_LEDGER, VECMAP_KIND, SPECIES_CLIP):
        kind = (world or {}).get("kind") or "a drawn page"
        return (f"{where}: embed={name!r} needs a world PLATE that declares the surface - this scene's world is "
                f"{kind}, which has no painted surface to land on (B1: a chart page never embeds)")
    if name not in embeds:
        named = ", ".join(sorted(embeds)) if embeds else "none"
        return (f"{where}: embed={name!r} is not a surface of {world['asset_id']!r} - it declares {named}. "
                f"Name it in <plate>{FG_LAYERS_SUFFIX} as {{\"embed\": {{\"{name}\": {{\"quad\": [[x, y] x 4]}}}}}}")
    return embed_quad_error(name, embeds[name], where)


# ---- P58 T4: THE LEDGER PAGE AS A CARD AT A DEPTH -----------------------------------------------------------
# E98 s3: *"the ledger page is a card at a depth ... the flat page stays the default reading form"*. Two opt-in
# page options and nothing else: `;depth=<k>` - the page takes the share k of the ONE camera's move (the parallax
# factor kinetics/camera.mjs already implements, P58 T3) - and `;plane=tilt:<deg>[,<axis>]|quad:<8 numbers>` - the
# SURFACE it is drawn on, four corners in the same TL TR BR BL stage fractions the ART-embed grammar authors
# (P50 T7), projected by the SAME homography (kinetics/homography.mjs). Neither is a default and neither adds a
# move: a page that names neither compiles byte-for-byte as it did, and E50-E53 hold - the flat page is the
# reading form, the chart still proves one sentence and leaves.
PAGE_DEPTH = {
    "K_MIN": 0.0,        # kinetics/camera.mjs PARALLAX.K_MIN - a page pinned to the frame, taking none of the move
    "K_MAX": 4.0,        # PARALLAX.K_MAX, and build_plate_library's own ceiling for a plane's depth: one range, three files
    "TILT_MAX": 89.0,    # a page turned further is edge-on: there is no quad left, only a line
    "EYE": 1.6,          # the eye's distance from the page in STAGE WIDTHS [DERIVED: a 1920 stage at CSS's default 1000 px perspective is 0.52; 1.6 is the gentler lens a reading page wants - a card on a desk, not a wide-angle wall]
    "AXES": ("y", "x"),  # `y`: the page turns about its own VERTICAL axis (its ruled lines converge left or right); `x`: about its horizontal one (it lies back)
    "NAME": "page",      # the name the quad's refusals carry into embed_quad_error
}
PAGE_PLANE_KINDS = ("tilt", "quad")
PAGE_THROW_GROW_GROWTH = "growth"   # the growth law on `throw=growth` (E99 s25: renamed from throw=depth; it may meet a real depth=)


def page_stage_aspect() -> float:
    """The stage's height over its width for the aspect this build declares. The quad is written in FRACTIONS, as
    every embed quad is, so it travels with the timeline into either aspect (the player carries one file for both)."""
    return 16 / 9 if ASPECT == "9:16" else 9 / 16


def page_plane_quad(deg: float, axis: str, aspect: float | None = None) -> list[list[float]]:
    """A page TILTED about its own centre by ``deg`` degrees, as four corners TL TR BR BL in stage fractions.

    One pinhole, closed form, no fitting: the page's corners in stage widths, rotated about its own centre axis
    (``y``: x' = u cos, z = u sin; ``x``: the same in y), divided by the eye's distance (PAGE_DEPTH["EYE"]), then
    scaled UNIFORMLY about the centre so the whole projected page sits back inside the stage - a tilt pushes the
    near edge past the frame otherwise, and a page whose ink leaves the frame is not a reading form (E28). Exactly
    the flat page at deg = 0."""
    a = page_stage_aspect() if aspect is None else aspect
    th, d = math.radians(deg), PAGE_DEPTH["EYE"]
    cos, sin = math.cos(th), math.sin(th)
    pts = []
    for u, v in ((-0.5, -0.5 * a), (0.5, -0.5 * a), (0.5, 0.5 * a), (-0.5, 0.5 * a)):
        x, y, z = (u * cos, v, u * sin) if axis == "y" else (u, v * cos, v * sin)
        k = d / (d + z)
        pts.append((x * k, y * k))
    fit = min(1.0, 0.5 / max(abs(p[0]) for p in pts), 0.5 * a / max(abs(p[1]) for p in pts))
    return [[round(min(1.0, max(0.0, 0.5 + x * fit)), 6), round(min(1.0, max(0.0, 0.5 + y * fit / a)), 6)]
            for x, y in pts]


def page_plane_spec(value: str, where: str) -> dict:
    """``tilt:<deg>[,<axis>]`` or ``quad:<x0,y0 ... x3,y3>`` -> the plane the page is drawn on, its four corners
    resolved HERE so the player keeps one projective path: the compiler owns the tilt's geometry exactly as it owns
    the role -> k table (P58 T2/T3), and kinetics/homography.mjs only ever consumes a quad. ValueError names the
    option; the caller names the row."""
    kind, _, rest = value.partition(":")
    if kind not in PAGE_PLANE_KINDS:
        raise ValueError(f"{where}: plane {value!r} is not tilt:<deg>[,<axis>] or quad:<x0,y0,x1,y1,x2,y2,x3,y3> "
                         "(the surface the page is drawn on: a tilt about its own centre, or its four corners)")
    if kind == "tilt":
        deg_s, _, axis = rest.partition(",")
        axis = axis or PAGE_DEPTH["AXES"][0]
        if not _is_number(deg_s):
            raise ValueError(f"{where}: plane tilt {deg_s!r} is not a number of degrees "
                             f"(plane=tilt:<deg>[,<axis {'|'.join(PAGE_DEPTH['AXES'])}>])")
        if axis not in PAGE_DEPTH["AXES"]:
            raise ValueError(f"{where}: plane tilt axis {axis!r} is not one of {'|'.join(PAGE_DEPTH['AXES'])} "
                             "(y: the page turns about its own vertical axis; x: it lies back)")
        deg = float(deg_s)
        if not abs(deg) < PAGE_DEPTH["TILT_MAX"]:
            raise ValueError(f"{where}: plane tilt {deg:g} deg is past the {PAGE_DEPTH['TILT_MAX']:g} deg limit - "
                             "a page turned that far is edge-on and has no page left to read")
        return {"kind": "tilt", "deg": deg, "axis": axis, "quad": page_plane_quad(deg, axis)}
    bits = [b for b in rest.split(",") if b != ""]
    if len(bits) != 8 or not all(_is_number(b) for b in bits):
        raise ValueError(f"{where}: plane quad {rest!r} is not eight numbers - x0,y0,x1,y1,x2,y2,x3,y3, the four "
                         "corners TL TR BR BL in stage fractions, authored the way an embed surface's corners are "
                         "read off the plate")
    v = [float(b) for b in bits]
    return {"kind": "quad", "quad": [[v[0], v[1]], [v[2], v[3]], [v[4], v[5]], [v[6], v[7]]]}


def page_plane_error(plane: dict, where: str) -> str | None:
    """Is this a surface a PAGE can be read on? The message, or None - ``embed_quad_error``'s own law (four corners
    on the stage, convex and in TL TR BR BL order, and at least EMBED_MIN_W of the stage wide), so a tilted page and
    a card on a painted wall are refused by ONE rule and one floor rather than by two."""
    err = embed_quad_error(PAGE_DEPTH["NAME"], {"quad": plane.get("quad")}, where)
    if not err:
        return None
    tilt = f" (plane=tilt:{plane['deg']:g},{plane['axis']})" if plane.get("kind") == "tilt" else ""
    return (err.replace(f"embed '{PAGE_DEPTH['NAME']}'", "the page's plane" + tilt)
               .replace("a card projected onto it", "a page projected onto it"))


def surface_plot_geometry(quad, stage_size, view_h=560) -> dict:
    """Derive a native-wide dense-line viewBox from the registered surface quad."""
    pts = _quad_points(quad)
    if pts is None:
        raise ValueError("surface quad must be four [x, y] corners")
    if not isinstance(stage_size, (list, tuple)) or len(stage_size) != 2:
        raise ValueError("surface stage_size must be [width, height]")
    try:
        stage_w, stage_h = float(stage_size[0]), float(stage_size[1])
        height = float(view_h)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("surface stage_size and view_h must be finite positive numbers") from None
    if not (math.isfinite(stage_w) and math.isfinite(stage_h) and stage_w > 0 and stage_h > 0
            and math.isfinite(height) and height > 0):
        raise ValueError("surface stage_size and view_h must be finite positive numbers")
    def edge(a, b):
        return math.hypot((b[0] - a[0]) * stage_w, (b[1] - a[1]) * stage_h)
    horizontal = (edge(pts[0], pts[1]) + edge(pts[3], pts[2])) / 2.0
    vertical = (edge(pts[0], pts[3]) + edge(pts[1], pts[2])) / 2.0
    if not (math.isfinite(horizontal) and math.isfinite(vertical) and horizontal > 0 and vertical > 0):
        raise ValueError("surface quad must have positive horizontal and vertical spans")
    return {"kind": "wide-dense-line", "view_w": height * horizontal / vertical, "view_h": height}


def surface_page_error(previous_world: dict, surface: dict, page: dict, lead_s, camera: dict | None,
                       where: str) -> str | None:
    """Return the first refusal for a page surface handoff, or ``None``."""
    if not isinstance(surface, dict) or surface.get("kind") != "paper":
        return f"{where}: surface must be a registered paper surface (kind='paper')"
    if not isinstance(page, dict) or page.get("enter") != "surface":
        return f"{where}: surface handoff page must enter with surface="
    if page.get("builder") != "dense-line":
        return f"{where}: surface= requires a dense-line page (this page is {page.get('builder')!r})"
    try:
        lead = float(lead_s)
    except (TypeError, ValueError, OverflowError):
        return f"{where}: surface lead must be a finite positive number of seconds"
    if not math.isfinite(lead) or lead <= 0:
        return f"{where}: surface lead must be a finite positive number of seconds"
    points = _quad_points(surface.get("quad"))
    if points is None or any(not math.isfinite(value) for point in points for value in point):
        return f"{where}: surface quad must contain finite [x, y] corners"
    quad_error = embed_quad_error(str((page.get("surface_from") or {}).get("surface") or "surface"), surface, where)
    if quad_error:
        return quad_error
    if not isinstance(previous_world, dict) or not previous_world.get("asset_id") \
            or previous_world.get("kind") in (SPECIES_LEDGER, VECMAP_KIND, SPECIES_CLIP):
        return f"{where}: surface handoff needs the immediately preceding world to be a static image plate"
    ken = previous_world.get("ken_burns") or {}
    if not isinstance(ken, dict):
        return f"{where}: preceding image plate Ken Burns must be identity for surface="
    for key in ("scale", "x", "y"):
        try:
            value = float(ken.get(key, 0.0))
        except (TypeError, ValueError, OverflowError):
            return f"{where}: preceding image plate Ken Burns must be finite and identity for surface="
        if not math.isfinite(value) or abs(value) > 1e-9:
            return f"{where}: preceding image plate must have zero Ken Burns for surface="
    idle = previous_world.get("idle")
    try:
        idle_drift = float(previous_world.get("idle_drift_px", 0.0) or 0.0)
    except (TypeError, ValueError, OverflowError):
        return f"{where}: preceding image plate must have no idle drift for surface="
    if idle not in (None, "none") or not math.isfinite(idle_drift) or abs(idle_drift) > 1e-9:
        return f"{where}: preceding image plate must have no idle drift for surface="
    if camera is not None:
        if not isinstance(camera, dict) or camera.get("keys"):
            return f"{where}: preceding camera must be identity for surface="
        if camera.get("attention") not in (None, "locked"):
            return f"{where}: preceding camera must be identity for surface="
    competing = ("plane", "depth", "form", "snap_from", "throw_grow", "throw_from", "throw_s",
                 "morph_s", "mount_s", "arrival")
    names = [key for key in competing if key in page]
    if names:
        return f"{where}: surface= cannot combine with {', '.join(names)} - the handoff has one arrival"
    return None


def _surface_sidecar_spec(path: Path | None, name: str, where: str) -> tuple[dict | None, str | None]:
    """Resolve and gate one registered paper surface without changing the sidecar."""
    if path is None or not Path(path).is_file():
        return None, f"{where}: surface plate asset is missing"
    side = Path(path).with_suffix(FG_LAYERS_SUFFIX)
    try:
        data = json.loads(side.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, f"{where}: surface sidecar is missing or invalid: {side.name}"
    if not isinstance(data, dict):
        return None, f"{where}: surface sidecar is not an object: {side.name}"
    status = str(data.get("status") or "")
    if data.get("render_eligible") is not True or "quarant" in status.lower():
        return None, f"{where}: surface sidecar is quarantined or not render-eligible ({status or 'render_eligible=false'})"
    embeds = plate_embeds(Path(path))
    if name not in embeds:
        named = ", ".join(sorted(embeds)) if embeds else "none"
        return None, f"{where}: surface={name!r} is not registered on {Path(path).name!r} (declares {named})"
    surface = embeds[name]
    if surface.get("kind") != "paper":
        return None, f"{where}: surface={name!r} must be a registered paper surface (kind='paper')"
    error = embed_quad_error(name, surface, where)
    if error:
        return None, error
    plane_error = page_plane_error({"kind": "quad", "quad": surface.get("quad")}, where)
    if plane_error:
        return None, plane_error
    return surface, None


def _surface_grow_camera_error(camera: dict | None, boundary: float, grow_s: float, where: str) -> str | None:
    """Reject authored camera motion that would move the page during its grow."""
    if camera is None:
        return None
    if not isinstance(camera, dict):
        return f"{where}: incoming camera must be identity during surface grow"
    if camera.get("attention") not in (None, "locked"):
        return f"{where}: incoming camera must be identity during surface grow"
    keys = camera.get("keys")
    if not isinstance(keys, list):
        return f"{where}: incoming camera must be identity during surface grow"
    until = boundary + grow_s
    for key in keys:
        if not isinstance(key, dict):
            return f"{where}: incoming camera must be identity during surface grow"
        try:
            at = float(key.get("t"))
        except (TypeError, ValueError, OverflowError):
            return f"{where}: incoming camera must be identity during surface grow"
        if not math.isfinite(at) or at <= until + 1e-9:
            return f"{where}: incoming camera must be identity during surface grow"
    return None


def _surface_idle_error(world: dict | None, where: str) -> str | None:
    if not isinstance(world, dict):
        return f"{where}: surface grow needs a ledger world"
    idle = world.get("idle")
    drift = world.get("idle_drift_px", 0.0)
    try:
        drift_value = float(drift or 0.0)
    except (TypeError, ValueError, OverflowError):
        return f"{where}: world must have no idle drift during surface grow"
    if idle not in (None, "none") or not math.isfinite(drift_value) or abs(drift_value) > 1e-9:
        return f"{where}: world must have no idle drift during surface grow"
    return None


def bind_surface_page_arrivals(scenes: list[dict], ep_dir: Path) -> list[str]:
    """Bind each surface page to its immediately preceding static plate."""
    bindings: list[tuple[dict, dict, dict, dict, float, dict, dict, dict]] = []
    notes: list[str] = []
    for index, scene in enumerate(scenes):
        world = scene.get("world") if isinstance(scene, dict) else None
        page = world.get("page") if isinstance(world, dict) else None
        if not isinstance(page, dict) or page.get("enter") != "surface":
            continue
        where = f"scene {scene.get('scene_id', f'row-{index + 1}')!r} surface="
        if index == 0:
            raise ValueError(f"{where}: no immediately preceding static image plate")
        previous = scenes[index - 1]
        previous_world = previous.get("world") if isinstance(previous, dict) else None
        meta = page.get("surface_from")
        if not isinstance(meta, dict):
            raise ValueError(f"{where}: missing surface handoff metadata")
        name = meta.get("surface")
        if not isinstance(name, str) or not name:
            raise ValueError(f"{where}: surface name is missing")
        try:
            lead_s = float(meta.get("lead_s"))
        except (TypeError, ValueError, OverflowError):
            raise ValueError(f"{where}: surface lead must be a finite positive number of seconds") from None
        if not math.isfinite(lead_s) or lead_s <= 0:
            raise ValueError(f"{where}: surface lead must be a finite positive number of seconds")
        try:
            prev_start, prev_end = (float(value) for value in previous.get("span", ()))
            boundary, current_end = (float(value) for value in scene.get("span", ()))
        except (TypeError, ValueError, OverflowError):
            raise ValueError(f"{where}: preceding and incoming spans must have two finite numbers") from None
        if not all(math.isfinite(value) for value in (prev_start, prev_end, boundary, current_end)):
            raise ValueError(f"{where}: preceding and incoming spans must have two finite numbers")
        if prev_end - prev_start + 1e-9 < lead_s or prev_end + 1e-9 < boundary \
                or prev_start > boundary - lead_s + 1e-9:
            raise ValueError(f"{where}: insufficient incoming span for lead {lead_s:g}s")
        grow_s = CAMERA_ARRIVAL_S
        if current_end - boundary + 1e-9 < grow_s:
            raise ValueError(f"{where}: insufficient incoming span for the {grow_s:g}s surface grow")
        source_ref = meta.get("source_ref")
        if not isinstance(source_ref, dict) or set(source_ref) != {"series_id", "variant", "sha256"}:
            raise ValueError(f"{where}: source_ref must preserve series_id, variant, and series file sha256")
        bound_ref = page.get("_surface_source_ref")
        if bound_ref is not None and (not isinstance(bound_ref, dict) or bound_ref != source_ref):
            raise ValueError(f"{where}: source_ref was changed after ledger_world bound the destination page")
        series_id = source_ref.get("series_id")
        variant = source_ref.get("variant")
        if not isinstance(series_id, str) or not series_id or not isinstance(variant, str) or not variant:
            raise ValueError(f"{where}: source_ref must preserve series_id and variant")
        series_path = Path(ep_dir) / "evidence/objects" / f"{series_id}.series.json"
        if not series_path.is_file():
            raise ValueError(f"{where}: source series file missing: {series_path}")
        expected_ref = {"series_id": series_id, "variant": variant, "sha256": sha(series_path)}
        if source_ref != expected_ref or page.get("variant") != variant:
            raise ValueError(f"{where}: source_ref does not match the destination page's registered series file")
        if "scene" in meta and meta.get("scene") != previous.get("scene_id"):
            raise ValueError(f"{where}: surface_from.scene does not name the immediately preceding scene")
        existing_surface = previous.get("surface_page") if isinstance(previous, dict) else None
        if isinstance(existing_surface, dict) and existing_surface.get("to_scene") != scene.get("scene_id"):
            raise ValueError(f"{where}: surface_page.to_scene does not name the destination scene")
        plate_id = previous_world.get("asset_id") if isinstance(previous_world, dict) else None
        plate_path = R.find_asset(plate_id) if plate_id else None
        surface, error = _surface_sidecar_spec(plate_path, name, where)
        if error:
            raise ValueError(error)
        motion_error = surface_page_error(previous_world, surface, page, lead_s, previous.get("camera"), where)
        if motion_error:
            raise ValueError(motion_error)
        grow_camera_error = _surface_grow_camera_error(scene.get("camera"), boundary, grow_s, where)
        if grow_camera_error:
            raise ValueError(grow_camera_error)
        grow_ken = world.get("ken_burns") or {}
        if not isinstance(grow_ken, dict):
            raise ValueError(f"{where}: incoming page must have zero Ken Burns during surface grow")
        for key in ("scale", "x", "y"):
            try:
                value = float(grow_ken.get(key, 0.0))
            except (TypeError, ValueError, OverflowError):
                raise ValueError(f"{where}: incoming page must have zero Ken Burns during surface grow") from None
            if not math.isfinite(value) or abs(value) > 1e-9:
                raise ValueError(f"{where}: incoming page must have zero Ken Burns during surface grow")
        idle_error = _surface_idle_error(world, where)
        if idle_error:
            raise ValueError(idle_error)
        if isinstance(previous_world, dict) and previous_world.get("sha256") and plate_path is not None \
                and previous_world["sha256"] != sha(plate_path):
            raise ValueError(f"{where}: preceding plate sha256 does not match the resolved static image")
        try:
            layout = surface_plot_geometry(surface.get("quad"), (STAGE_W, 1080), view_h=560)
        except ValueError as exc:
            raise ValueError(f"{where}: {exc}") from None
        quad = copy.deepcopy(surface["quad"])
        ref = copy.deepcopy(expected_ref)
        establish = {"to_scene": scene.get("scene_id"), "surface": name, "quad": quad,
                     "surface_layout": copy.deepcopy(layout),
                     "span": [round(boundary - lead_s, 2), round(boundary, 2)],
                     "presentation": "establish", "source_ref": ref}
        incoming = {"scene": previous.get("scene_id"), "surface": name, "quad": copy.deepcopy(quad),
                    "surface_layout": copy.deepcopy(layout), "lead_s": lead_s, "grow_s": grow_s,
                    "source_ref": copy.deepcopy(ref)}
        bindings.append((previous, scene, page, establish, lead_s, incoming, layout, ref))
        notes.append(f"{previous.get('scene_id', '?')}: surface {name} -> {scene.get('scene_id', '?')} "
                     f"({lead_s:g}s lead, {layout['view_w']:g}x{layout['view_h']:g})")
    for previous, scene, page, establish, _lead_s, incoming, _layout, _ref in bindings:
        previous["surface_page"] = establish
        page.pop("_surface_source_ref", None)
        page["surface_from"] = incoming
    return notes


def page_depth_k(value: str, where: str) -> float:
    """``depth=<k>`` -> the page's parallax factor, refused BY NAME outside the camera's own range."""
    if not _is_number(value):
        raise ValueError(f"{where}: depth {value!r} is not a number - depth=<k>, the share of the camera's move the "
                         f"page takes ({PAGE_DEPTH['K_MIN']:g} = pinned to the frame, 1 = the flat plate)")
    k = float(value)
    if not PAGE_DEPTH["K_MIN"] <= k <= PAGE_DEPTH["K_MAX"]:
        raise ValueError(f"{where}: depth {k:g} is outside {PAGE_DEPTH['K_MIN']:g}..{PAGE_DEPTH['K_MAX']:g} - the "
                         "parallax factor a plane may take of the camera's move (kinetics/camera.mjs PARALLAX)")
    return k



# ---- P58 T6 (a): THE DOCK AT A DEPTH --------------------------------------------------------------------------
# E98 s4: *"the docks, the ball and the slide move THROUGH the depth"*. ONE dock option, `depth=<k>`, written in the
# page's own vocabulary (PAGE_DEPTH's range IS the camera's, and this slice adds no second one): the card stands on
# a LAYER'S plane and takes that share of the one camera's move (kinetics/camera.mjs `camLayerCss`) instead of
# standing in screen space, as every dock has. Nothing else about the card changes - E45's arrival, its reading box,
# its park and M25's settled card are the choreography they were, composed INSIDE the depth - and a dock that names
# no depth compiles byte-for-byte as it did.
#   IT COMPOSES WITH `behind=` (HF-17, P50 T15) RATHER THAN DUPLICATING IT. Occlusion is the depth CUE; the parallax
# is the depth itself, and one card may carry both - but only if the two agree. `behind` puts the card UNDER the
# plate's foreground cutout, which is the plane doc 24 calls `-near` and build_plate_library indexes at k 1.40, so a
# card behind that front cannot also sit nearer than it. The pair is refused BY NAME rather than painted as a card
# that occludes the very thing it is behind.
DOCK_DEPTH = {
    "K_MIN": PAGE_DEPTH["K_MIN"],   # ONE range for every depth in this slice - the camera's own (PARALLAX.K_MIN)
    "K_MAX": PAGE_DEPTH["K_MAX"],   # ... and PARALLAX.K_MAX
    "BEHIND_K": 1.40,   # build_plate_library.LAYER_PLANES["occluder"] - doc 24's `-near` foreground cutout, the plane `behind=` puts a card under. One dial written twice (as MELT_S and SLIDE_S are), and test_dock_depth pins the pair
}


def depth_k(value, where: str, what: str = "card") -> float:
    """``depth=<k>`` -> the parallax factor of the thing named by `what`, refused BY NAME outside the camera's own
    range - `page_depth_k`'s range and `page_depth_k`'s message with that noun in the page's place, because there is
    ONE depth vocabulary in this engine and not one per thing that can stand on a plane (P58 T6: the card, the ball
    and each of the slide's two frames all come through here)."""
    if isinstance(value, bool) or not (isinstance(value, (int, float)) or _is_number(str(value))):
        raise ValueError(f"{where}: depth {value!r} is not a number - depth=<k>, the share of the camera's move the "
                         f"{what} takes ({DOCK_DEPTH['K_MIN']:g} = pinned to the frame, 1 = the flat plate)")
    k = float(value)
    if not DOCK_DEPTH["K_MIN"] <= k <= DOCK_DEPTH["K_MAX"]:
        raise ValueError(f"{where}: depth {k:g} is outside {DOCK_DEPTH['K_MIN']:g}..{DOCK_DEPTH['K_MAX']:g} - the "
                         "parallax factor a plane may take of the camera's move (kinetics/camera.mjs PARALLAX)")
    return k


def dock_depth_k(value, where: str) -> float:
    """``depth=<k>`` on a DOCK row -> the card's parallax factor (`depth_k`'s one law, the card's noun)."""
    return depth_k(value, where, "card")


def dock_depth_behind_error(k: float, layer: str, where: str) -> str | None:
    """Do a card's `depth=` and its `behind=` agree? The message, or None (HF-17's occluder plane is the ceiling)."""
    if k <= DOCK_DEPTH["BEHIND_K"]:
        return None
    return (f"{where}: depth={k:g} with behind={layer!r} - a card behind the plate's front cannot sit nearer than "
            f"it: depth <= {DOCK_DEPTH['BEHIND_K']:g} with behind=, or drop one")


# ---- P58 T5: THE TWO CHART FORMS IN 2.5D ---------------------------------------------------------------------
# E98 s3: *"bars with extrusion, a line on a tilted plane - the flat page stays the default"*. ONE page option,
# `;form=<name>[:<deg>]`, and nothing else. What a form changes is how the page's marks are DRAWN; the spec, the
# scale, the value capsule, the axis rule and every label stay the flat page's, so E50-E53 hold literally - the
# chart still proves one sentence and leaves, the axis rule still states itself, and sign is still geometry.
#   Which form a page may take is `ledger_page.form_error`'s (one rule, and the object file is held to it too).
# The tilted line's PLANE is resolved here, exactly as `plane=` is: the compiler owns the tilt's geometry and the
# player consumes one projective form (the quad) - a second tilt path would be a second geometry to get wrong.
CHART_FORM_TILT = "tilted_line"


def page_form_geom(value: str, where: str) -> dict:
    """``<name>[:<deg>]`` -> the form and its plane, WITHOUT the fit to a builder (the row's own grammar). The
    tilt's four corners are `page_plane_quad`'s - the same closed form, the same eye, the same fit inside the
    frame - and they are refused by `page_plane_error`'s one law, so a plane too narrow to read on a phone is
    refused by the SAME message here as under `plane=` (EMBED_MIN_W)."""
    name, _, rest = value.partition(":")
    if name not in LPG.CHART_FORMS:
        raise ValueError(f"{where}: form {name!r} is not one of {'|'.join(LPG.CHART_FORMS)} "
                         "(the two 2.5D chart forms; the flat page is the reading form and names none)")
    if name != CHART_FORM_TILT:
        if rest:
            raise ValueError(f"{where}: form={value!r} takes no setting - form={name} is the whole option "
                             f"(its depth and its light are the engine's dials, not the row's)")
        return {"kind": name}
    if rest and not _is_number(rest):
        raise ValueError(f"{where}: form tilt {rest!r} is not a number of degrees - form={CHART_FORM_TILT}[:<deg>], "
                         f"the turn of the line's own plane ({LPG.TILT_DEG:g} deg when the option names none)")
    deg = float(rest) if rest else LPG.TILT_DEG
    if not abs(deg) < PAGE_DEPTH["TILT_MAX"]:
        raise ValueError(f"{where}: form tilt {deg:g} deg is past the {PAGE_DEPTH['TILT_MAX']:g} deg limit - "
                         "a plane turned that far is edge-on and has no plot left to draw on")
    axis = PAGE_DEPTH["AXES"][0]
    plane = {"kind": "tilt", "deg": deg, "axis": axis, "quad": page_plane_quad(deg, axis)}
    err = page_plane_error(plane, where)
    if err:
        raise ValueError(err.replace("the page's plane", "the line's plane")
                            .replace(f"plane=tilt:{deg:g},{axis}", f"form={CHART_FORM_TILT}:{deg:g}"))
    return {"kind": name, "deg": deg, "axis": axis, "quad": plane["quad"]}


# ---- E99 s35 - THE PAGE'S FIELD: the soak, the two-plate cross-fade, and the scribble as the back-up ----------
# The operator, 2026-09-15, shown one formed page rendered three ways: *"I think they should both be first class
# effects. When we are trying to maintain continuity, connecting ideas, speaking across plates i think the cross-fade
# is the answer, when we are building an idea or introducing a new idea or looking to fill space to separate ideas,
# the soak is the transition."* So the field is authored by the sentence's JOB, on the row, and is not a property of
# the page's form or its builder. `soak` is what a page with no `field` has always taken (the engine's own default),
# `plates` is doc 41's decided signature (the charcoal-filled deckle cross-faded over the cream page), and `scribble`
# is the opt-in back-up, never a default and never built on. The LEAVE is the soak's recede for all three (the engine
# `lpPlateRecede`), which is why the field names an ARRIVAL and nothing else.
PAGE_FIELDS = ("soak", "plates", "scribble")
# the two generated plates the record uses (E22 / doc 41's ledger-page signature; the claim
# `steel-and-paper-ledger-page-v1`). A row may only ASK for the cross-fade - the ids are the page's, put there by the
# build that owns the assets, because an image never enters the compiler (E99 s31).
PAGE_FIELD_PLATES = ("world-ledger-blank-page-cream-v1", "world-ledger-inked-deckle-cream-v1")


def page_field_spec(value: str, page: dict | None, where: str) -> str:
    """The `;field=` option's name, refused BY NAME - and, once the page is in hand (`page` not None), `plates`
    refused unless that page carries both plates. The row's grammar is checked without a page (`_check_opt`); the
    fit to the page is checked where the page is read, exactly as `form=`'s is."""
    name = str(value).strip()
    if name not in PAGE_FIELDS:
        raise ValueError(f"{where}: field={name!r} is not one of {'|'.join(PAGE_FIELDS)} - the soak (a new idea, or "
                         "space between two), the two-plate cross-fade (continuity: connecting ideas, speaking "
                         "across plates) or the scribble (the opt-in back-up). E99 s35")
    if name == "plates" and page is not None:
        missing = [k for k in ("plate", "field_plate") if not page.get(k)]
        if missing:
            raise ValueError(f"{where}: field=plates is the TWO-PLATE CROSS-FADE and this page carries no "
                             f"{' and no '.join(missing)}. The page needs BOTH: plate={PAGE_FIELD_PLATES[0]!r} (the "
                             f"generated cream page) and field_plate={PAGE_FIELD_PLATES[1]!r} (the charcoal filled "
                             "to the deckle, cross-faded over it), with `board` the deckle's inner rectangle - the "
                             "build that owns the assets writes all three (E99 s31: no image reaches the compiler). "
                             "Without them, name field=soak")
    return name


# ---- R26-223: A PAGE IS BORN WITH ITS DOMAIN (2026-09-18, the Steel and Paper H unit) ---------------
# A page's OPENING state was built from the evidence object alone (`ledger_world` -> `LPG.build_spec`), so the
# only way to open on a subset of a series' range was to let the page arrive on the object's own scale and
# `chart_to rescale` off it - and a rescale may not fire at 0.00 (M23: never over a build, never at a page's
# edge), so the H unit's hook stood four seconds on the wrong scale before the first word after the build.
#
# THE TOKEN IS `;domain=<ymin>,<ymax>`, and that form for three reasons:
#   * it names the key it WRITES. `axes.domain` is what the page spec carries, what a derived rescale state
#     carries (`rescale_state`: `axes["domain"] = [ymin, ymax]`) and what the player reads - so the born state
#     and the derived state are described by ONE word instead of two spellings of one idea.
#   * a domain is an indivisible PAIR. `;ymin=..;ymax=..` is two plate options for one scale, and a
#     half-declared scale is a new ambiguity nobody asked for; the plate-option grammar already spells a
#     compound value as a comma list inside one token (`plane=quad:<8 numbers>`, `throw=<grow>,<from>,<s>`).
#   * BOTH ends are required. The line builder tolerates a null end; the bars builder does not
#     (`scene-evidence-engine.mjs:8445` reads `dom[0]` and `dom[1]` straight into its scale), so a one-sided
#     born domain would be a silent NaN on a bars page. It is refused by name here instead.
# The OBJECT's own domain stays the default: a row that names none writes nothing, and every page that named
# none compiles to exactly the bytes it did.
DOMAIN_BUILDERS = ("dense-line", "story")   # the two builders that read `axes.domain` ON PURPOSE - the line
    # (`scene-evidence-engine.mjs:8679`) and the bars (`:8431`) - and the two `rescale_state` admits, so the born
    # domain and the rescale that moves off it are one door answering to one set.
    #   This is the CONSERVATIVE bound, not an exhaustive one: the engine's builder dispatch falls back to the bars
    # builder for a kind it has no painter mapped for, so a page whose builder is (say) `object` would in fact read
    # the domain through that fall-back. Refusing it here is the choice, and the reason is legibility of intent: a
    # scale honoured by accident, on a page whose own builder never asked for one, is a number the author cannot
    # predict and a gate cannot read. A third builder joins this tuple when its OWN painter reads the key - never
    # because a fall-back happened to.


def page_domain_spec(value, builder: str | None, where: str) -> list[float]:
    """``;domain=<ymin>,<ymax>`` -> ``[ymin, ymax]``, the y scale the page is BORN on (R26-223).

    The row's GRAMMAR is checked with no page in hand (`builder` None, from `_check_opt`); the fit to this page's
    builder is checked where the page is read, exactly as `form=`'s and `field=`'s are. ValueError names the
    option; the caller names the row."""
    parts = [p.strip() for p in str(value).split(",")]
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"{where}: domain {str(value)!r} is not <ymin>,<ymax> - the two ends of the y scale this "
                         "page OPENS on, in the series' own unit. Both ends: a bars page's scale reads them both, "
                         "so a half-declared domain is a scale with a hole in it (R26-223)")
    try:
        lo, hi = float(parts[0]), float(parts[1])
    except ValueError:
        raise ValueError(f"{where}: domain {str(value)!r} is not two numbers - <ymin>,<ymax> in the series' own "
                         "unit (the same pair a `chart_to rescale` names as ymin / ymax)") from None
    if not (math.isfinite(lo) and math.isfinite(hi)):   # `nan` passes `hi > lo` and `inf` satisfies it, and either
        # would be written onto the page's own axes for the player to divide by. A scale has two FINITE ends.
        raise ValueError(f"{where}: domain {str(value)!r} is not two numbers - <ymin>,<ymax> in the series' own "
                         "unit (the same pair a `chart_to rescale` names as ymin / ymax)")
    if not hi > lo:
        raise ValueError(f"{where}: domain {str(value)!r} is empty or inverted - ymin < ymax")
    if builder is not None and builder not in DOMAIN_BUILDERS:
        raise ValueError(f"{where}: domain= is a LINE or BARS page's y scale and this page is {builder!r} - the two "
                         f"builders that read it are {' and '.join(DOMAIN_BUILDERS)}, which are the two a "
                         "`chart_to rescale` admits for the same reason (R26-223)")
    return [lo, hi]


# ---- R26-226: A MULTI-LINE PAGE BUILDS LINE BY LINE (2026-09-18, E99 s82) ---------------------------
# The operator, on frozen copy d of the Steel and Paper H unit: *"the crawl drawing on the chart looks weird.
# The lines draw well while we're moving them, but drawing the first few years then stopping for seemingly no
# reason is weird - it would be different if we were stopping to talk about each section but that's not what
# the chart does. A better way to do this is to draw the first line completely, label it, badge it, draw the
# 2nd line completely, badge it, draw the 3rd line completely, badge it, draw the 4th line completely, badge
# it. Everything can be purposeful, and with rhythm and direction without having to completely stop."*
#
# A dense-line page draws every series TOGETHER on the page's one build clock (the engine's
# `fr = clamp01((c - pp.stagger * 0.3) / 0.7)`), so N lines crawl side by side and all N land at once. The
# only way to put one line before another was a `build_to` per spoken phrase, which is the crawl that stops.
#
# THE TOKEN IS `;build=lines`, or `;build=lines:<s>`, and that form for three reasons:
#   * it names a page-level BUILD MODE, not a species. The sequence is how this page draws at all - not a
#     thing that happens on a word - so it belongs on the plate id beside `;domain=` and `;form=`, and a
#     `build_to` stays what it is: the authored stop the ruling allows ("if we were stopping to talk about
#     each section"), which still caps its own series inside that series' own window.
#   * the optional setting is ONE series' seconds, not the page's total, because the author is timing a
#     LINE against a sentence; the page's total is arithmetic (N x s) and the compiler does it, writing it
#     to `build_s` - the key the engine's `buildDur` and the motion gate's landing already read. One truth.
#   * the mode is a WORD, so a second mode (a bars page's own order, say) joins `PAGE_BUILD_MODES` without
#     a second token, and anything else is refused by name here.
# A row that names none writes nothing: every page compiled before this row is byte-identical.
PAGE_BUILD_MODES = ("lines",)
LINE_BUILD_BUILDERS = ("dense-line",)   # the ONE builder whose `st.paths` ARE the page's series, so a sequence
    # over them is a sequence over the lines the operator counted (the engine's `buildLedgerLine`,
    # `scene-evidence-engine.mjs:8769`).
    #   This is the CONSERVATIVE bound, not an exhaustive one, and for the reason R26-223's `DOMAIN_BUILDERS`
    # states: `tiers` draws line BANDS and `combo` draws a line over its bars, so both have paths a sequence could
    # technically run, and the engine's builder dispatch falls back to the bars builder for a kind it has no painter
    # mapped for. Refusing them is the choice - a build clock honoured by accident, on a page whose own painter never
    # asked for one, is a rhythm the author cannot predict and a gate cannot read. A builder joins this tuple when
    # its OWN paint step reads the mode.
PAGE_BUILD_LINE_MIN_S = 0.25   # a series' draw, floored: 0.25 s is 6 frames at the 24 fps we render, the
                               # fewest a pen can be seen moving through. Under it a line pops, and the
                               # ruling is about a line DRAWING ("the lines draw well while we're moving them")
PAGE_BUILD_LINES_MIN_N = 2     # "a MULTI-LINE page": one line has no sequence in it


def page_build_spec(value, builder: str | None, n_series: int | None, where: str,
                    page_build_s: float | None = None) -> dict:
    """``;build=lines[:<s>]`` -> ``{"mode": "lines"[, "series_s", "build_s"]}`` (R26-226).

    The row's GRAMMAR is checked with no page in hand (`builder` and `n_series` None, from `_check_opt`); the
    fit to this page's builder, its series COUNT and - for the bare mode, which divides a window it did not
    choose - the window it would be dividing (`page_build_s`) is checked where the page is read, exactly as
    `form=`'s and `domain=`'s are. ValueError names the option; the caller names the row."""
    text = str(value).strip()
    mode, sep, rest = text.partition(":")
    if mode not in PAGE_BUILD_MODES:
        raise ValueError(f"{where}: build={text!r} is not one of {'|'.join(PAGE_BUILD_MODES)} - `lines` is the "
                         "page's series drawn ONE AT A TIME, each whole, its end tag and badge landing as it "
                         "lands (E99 s82). `lines:<s>` names one series' seconds (R26-226)")
    if sep and ":" in rest:
        raise ValueError(f"{where}: build={text!r} takes one setting - build={mode}:<s>, the seconds ONE series "
                         "draws over (the page's whole build is that times the number of series)")
    out: dict = {"mode": mode}
    if sep:
        try:
            s = float(rest)
        except ValueError:
            raise ValueError(f"{where}: build={text!r} is not a number of seconds - build={mode}:<s>, the seconds "
                             "ONE series draws over") from None
        if not (math.isfinite(s) and s > 0):   # `inf` and `nan` pass every `>` guard below and would reach the
            # page's own `build_s` for the player to divide the clock by. A length is a finite number of seconds.
            raise ValueError(f"{where}: build={text!r} is not a number of seconds - build={mode}:<s>, the seconds "
                             "ONE series draws over")
        if s < PAGE_BUILD_LINE_MIN_S:
            raise ValueError(f"{where}: build={mode}:{s:g} gives one line {s:g} s to draw, under the floor "
                             f"{PAGE_BUILD_LINE_MIN_S:g} s - which is 6 frames at 24 fps, the fewest a pen can be "
                             "seen moving through. Under it a line pops instead of drawing, and the ruling is about "
                             'a line DRAWING ("the lines draw well while we\'re moving them", E99 s82)')
        out["series_s"] = s
    if builder is not None and builder not in LINE_BUILD_BUILDERS:
        raise ValueError(f"{where}: build={mode} draws a page's SERIES line by line and this page is {builder!r} - "
                         f"the builder whose paths are its series is {' and '.join(LINE_BUILD_BUILDERS)} "
                         "(a bars, share or story page has no lines to put in turn; R26-226)")
    if n_series is not None:
        if int(n_series) < PAGE_BUILD_LINES_MIN_N:
            raise ValueError(f"{where}: build={mode} is the MULTI-LINE page's build and this page draws "
                             f"{int(n_series)} series - there is no sequence in one line, and the mode would "
                             "silently re-time its draw. Drop build=, or name the page's other series (R26-226)")
        if "series_s" in out:
            out["build_s"] = round(out["series_s"] * int(n_series), 3)
        elif page_build_s:
            # THE BARE MODE divides a window it did not choose - the page's own `build_s`, or LP.BUILD - so the
            # floor has to be checked on the SHARE, not only on a length the row named. Without this a page of
            # many lines (or a short authored `build_s`) would give each line a draw nobody can see, and the
            # token would be the cause with nothing said about it.
            share = float(page_build_s) / int(n_series)
            if share < PAGE_BUILD_LINE_MIN_S:
                raise ValueError(f"{where}: build={out['mode']} shares this page's {float(page_build_s):g} s build "
                                 f"between {int(n_series)} series - {share:.3g} s each, under the floor "
                                 f"{PAGE_BUILD_LINE_MIN_S:g} s (6 frames at 24 fps). Name the seconds a line draws "
                                 f"over instead - build={out['mode']}:<s> - or give the page a longer build")
    return out


PAGE_INTRINSIC_BUILDERS = {
    "decline": 3.6,
    "combo": 4.5,
    "share": 3.2,
    "tiers": 4.5,
    "treemap": 3.6,
}
# These are the player's LPX clocks (`scene-evidence-engine.mjs:8985-9014`).  The
# compiler cannot import the browser module, so the intrinsic builders' clocks
# are mirrored here; dense/story/object use the authored page build instead.
PAGE_RACE_IN_S, PAGE_RACE_PERIOD_S = 0.6, 1.2
PAGE_BREAK_HOLD_S, PAGE_BREAK_RUN_S, PAGE_BREAK_SETTLE_S = 0.5, 0.6, 0.3
PAGE_BREAK_STEP_S = 0.06


def _positive_page_seconds(value) -> float | None:
    """Return a finite authored duration, excluding bools and non-positive values."""
    if isinstance(value, bool):
        return None
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return None
    return seconds if math.isfinite(seconds) and seconds > 0 else None


def _page_build_is_authored(page: dict) -> bool:
    """Whether this page opted into the row-span check (R26-231).

    Unauthored pages keep the shipped default timing.  A page that names
    `build=lines` is authored even when the bare mode leaves its default
    `build_s` implicit; a source `build_s` opts in for every applicable builder.
    """
    return "build_s" in page or page.get("build") in PAGE_BUILD_MODES


def _breakthrough_build_duration(page: dict, base: float) -> float:
    """Mirror the bars player's optional breakthrough envelope when it exists.

    The bars painter is the fallback for story/object pages.  Ordinary bars
    still use `base`; only an overflow mode with a value above its declared
    domain gets the hold/run/settle clock written by the player.
    """
    axes = page.get("axes") if isinstance(page.get("axes"), dict) else {}
    mode = axes.get("overflow")
    domain = axes.get("domain")
    values = page.get("values")
    if mode not in ("burst", "break", "stack"):
        return base
    if not (isinstance(domain, list) and len(domain) == 2):
        if mode == "stack":
            raise ValueError("stack breakthrough requires a two-number domain")
        return base
    hi = _positive_page_seconds(domain[1])
    if hi is None:
        try:
            hi = float(domain[1])
        except (TypeError, ValueError, OverflowError):
            if mode == "stack":
                raise ValueError("stack breakthrough domain upper bound must be a finite positive number") from None
            return base
        if not math.isfinite(hi) or (mode == "stack" and hi <= 0):
            if mode == "stack":
                raise ValueError("stack breakthrough domain upper bound must be a finite positive number")
            return base
    if not isinstance(values, list):
        return base
    vals = []
    for value in values:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return base
        if not math.isfinite(number):
            return base
        vals.append(number)
    over = [value for value in vals if value > hi]
    if not over:
        return base
    honest = [value for value in vals if value <= hi]
    comparator = max(honest) if honest else hi
    if mode in ("burst", "break"):
        return base + PAGE_BREAK_HOLD_S + PAGE_BREAK_RUN_S + PAGE_BREAK_SETTLE_S
    if comparator <= 0:
        raise ValueError("stack breakthrough comparator must be positive")
    return base + PAGE_BREAK_HOLD_S + PAGE_BREAK_STEP_S * (math.ceil(max(vals) / comparator - 1e-9) + 1)


def page_build_duration_s(page: dict) -> float:
    """The player's actual chart-build clock for an authored page.

    Intrinsic builders own their `st.buildDur` and ignore `pg.build_s`; the
    line/story/object family reads `pg.build_s` (or LP.BUILD).  Keeping that
    distinction here prevents the motion-gate mirror from treating a short
    authored clock as the three-second default or inventing a longer race.
    """
    builder = str(page.get("builder") or "story")
    if builder == "race":
        periods = page.get("periods")
        count = len(periods) if isinstance(periods, list) else 0
        return PAGE_RACE_IN_S + max(0, count - 1) * PAGE_RACE_PERIOD_S
    if builder in PAGE_INTRINSIC_BUILDERS:
        return PAGE_INTRINSIC_BUILDERS[builder]
    base = _positive_page_seconds(page.get("build_s")) or float(MG.LP_BUILD_S)
    return _breakthrough_build_duration(page, base) if builder in ("story", "object") else base


def _page_entry_build_s(page: dict, build_s: float) -> float:
    """Return the gate's entry-to-build landing using the actual player clock."""
    enter = page.get("enter")
    if enter in (None, "axes", "mount", "morph"):
        # MG owns mount/morph/axes offsets and the default page beats.  Its
        # `extra` intentionally floors short authored builds at LP.BUILD, so
        # apply the actual renderer delta explicitly for those entry modes.
        baseline = dict(page)
        baseline["build_s"] = float(MG.LP_BUILD_S)
        return float(MG._page_land_offset({"world": {"page": baseline}})) + build_s - float(MG.LP_BUILD_S)
    # Arrives-built entries (including spiral's 1.6s unwind) have no chart
    # build to add; MG already returns the entry's own clock for them.
    return float(MG._page_land_offset({"world": {"page": dict(page)}}))


def page_build_envelope_s(scene: dict) -> float | None:
    """The authored page's required row span: entry + actual build + leave."""
    world = scene.get("world") if isinstance(scene, dict) else None
    page = world.get("page") if isinstance(world, dict) else None
    if not isinstance(page, dict) or world.get("kind") != SPECIES_LEDGER or not _page_build_is_authored(page):
        return None
    build_s = page_build_duration_s(page)
    entry_build = _page_entry_build_s(page, build_s)
    no_leave = str(page.get("exit") or "").split(":", 1)[0] == "cut"
    leave_s = 0.0 if no_leave else sum(float(value) for value in MG.LP_RETRACT_S)
    return entry_build + leave_s


def page_build_span_error(scene: dict) -> str | None:
    """Return a named R26-231 row error, or ``None`` when the row fits."""
    try:
        need = page_build_envelope_s(scene)
    except ValueError as exc:
        world = scene.get("world") if isinstance(scene, dict) else None
        page = world.get("page") if isinstance(world, dict) else None
        title = page.get("title") if isinstance(page, dict) else None
        return (f"{scene.get('scene_id', '?')}: page {title or 'ledger page'!r} "
                f"has an invalid build clock: {exc}")
    if need is None:
        return None
    span = scene.get("span") if isinstance(scene, dict) else None
    if not (isinstance(span, (list, tuple)) and len(span) == 2):
        return f"{scene.get('scene_id', '?')}: page build has no two-number row span"
    try:
        start_s, end_s = float(span[0]), float(span[1])
    except (TypeError, ValueError, OverflowError):
        return f"{scene.get('scene_id', '?')}: page build row span is not numeric"
    if not (math.isfinite(start_s) and math.isfinite(end_s)):
        return f"{scene.get('scene_id', '?')}: page build row span endpoints must be finite numbers"
    row_s = end_s - start_s
    if not math.isfinite(row_s):
        return f"{scene.get('scene_id', '?')}: page build row span delta must be finite"
    if row_s < 0:
        return f"{scene.get('scene_id', '?')}: page build row span delta must be non-negative"
    if row_s + 1e-9 >= need:
        return None
    page = (scene.get("world") or {}).get("page") or {}
    title = page.get("title") or page.get("builder") or "ledger page"
    return (f"{scene.get('scene_id', '?')}: page {title!r} build envelope is {need:g}s "
            f"(entry/build/leave), but its row span is {row_s:g}s")


def validate_page_build_spans(scenes: list[dict]) -> None:
    """Reject the first authored page build that overruns its finalized row."""
    for index, scene in enumerate(scenes):
        error = page_build_span_error(scene)
        if error:
            sid = scene.get("scene_id", f"row-{index + 1}")
            raise ValueError(f"shot row {index + 1} ({sid}): {error}")


def page_builds_lines(world: dict | None) -> bool:
    """Is this world a ledger page that draws its series one at a time (R26-226)?"""
    if not isinstance(world, dict) or world.get("kind") != SPECIES_LEDGER:
        return False
    return ((world.get("page") or {}).get("build")) in PAGE_BUILD_MODES


def line_build_first_cap(species: list[dict] | None, si: int) -> int | None:
    """The datum index the EARLIEST `build_to` caps series `si` at, or None when none does (R26-226).

    The player's own reading, written once here so the stamped windows and the painted ones cannot disagree: a
    cap naming no series applies to every one (the paint's `forMe`), and the first one by `at` is the cap the
    build beat is spent on."""
    best = None
    for sp in species or []:
        if sp.get("kind") != "build_to" or not isinstance(sp.get("target"), dict):
            continue
        ss = sp.get("series", sp.get("tier", (sp.get("target") or {}).get("series")))
        if ss is not None and int(ss) != int(si):
            continue
        if best is None or float(sp.get("at") or 0.0) < float(best.get("at") or 0.0):
            best = sp
    return int((best["target"] or {}).get("index") or 0) if best else None


def page_line_windows(world: dict | None, species: list[dict] | None,
                      scene_start: float) -> list[tuple[float, float]]:
    """Every DRAWING series' own turn - (from, to) in seconds - on a page that builds line by line; empty for
    every other page and every plate (R26-226).

    The page's build ends where the motion gate says its chart lands (`MG._page_land_offset`, which reads the
    same `build_s` the engine's `buildDur` does) and opens one build length before it; a turn is that build over
    the page's series COUNT, and the turns are taken back to back in the page's own series order. A series a
    `build_to` HOLDS AT INDEX 0 takes no turn - it would draw nothing through a whole one (`capFrac` at index 0
    is 0), which is a dead beat at the open - so the lines that do draw come earlier and the build ends earlier.
    Stamped on the scene as `build_lines` so a gate reads the clocks the player paints rather than deriving a
    second copy of them."""
    if not page_builds_lines(world):
        return []
    page = world["page"]
    n = len(page.get("series") or [])
    if n < PAGE_BUILD_LINES_MIN_N:
        return []
    draws = [i for i in range(n) if line_build_first_cap(species, i) != 0] or list(range(n))
    total = float(page.get("build_s") or MG.LP_BUILD_S)
    end = float(scene_start) + MG._page_land_offset({"world": world})
    start, share = end - total, total / n
    return [(start + k * share, start + (k + 1) * share) for k, _si in enumerate(draws)]


# ---- R26-233 / E99 s82: THE AXIS YIELDS TO THE LINE THAT PUSHES IT -----------------------------
# Measured by the critic on the H unit's copy e (`build-h-frozen-f/BUILD-NOTES-H.md` s8c): the reveal's
# `chart_to rescale` opened the y domain 80..277 -> 640 over its OWN eased clock while the memory line was
# still drawing, so the three LANDED lines slid 253 px down beside it and the low ticks went with them -
# the class of move the operator refused at 0:05 (E99 s82: *"the movement on screen drags down the values
# somehow at 0:05, that can't happen"*; INK NEVER MOVES UNLESS THE SENTENCE MOVES IT). The words DO name
# the reveal, so the rescale belongs; what was wrong was its CLOCK.
#   `follow: <series>` (or `follow: true` - the series this row's own `build_to` draws) puts the domain on
# the LINE's clock: frame by frame the top is that series' DRAWN extremum with the page's own air above it,
# and the landed ink yields exactly as the new line climbs past the old top - never before it, and never
# after it lands. It is the BREAKTHROUGH bars' shape (CAPABILITIES:88, the bar shoots WHILE the axis
# rescales) on a line page. A rescale that names no `follow` is exactly the rescale it was.
FOLLOW_HEADROOM = 1.06   # the air the climbing tip keeps above the domain's top, as a FACTOR on the value: the
                         # 6 % the LINE BUILDER itself pads a page's data by (`scene-evidence-engine.mjs:8821`,
                         # `pad = (y1 - y0) * 0.06`). A factor rather than a share of the range because the
                         # compiler has to answer "does this line ever reach that ymax?" from the series' own
                         # numbers, and the player applies it as one offset in log space (`XF_FOLLOW.HEAD`).
FOLLOW_BUILDERS = ("dense-line",)   # the CONSERVATIVE bound R26-223's `DOMAIN_BUILDERS` and R26-226's
    # `LINE_BUILD_BUILDERS` state, for the same reason: this is the one builder whose `st.paths` ARE the page's
    # series, so "the followed series' drawn extremum" is a thing the player can read off the ink. `story`
    # rescales (it is in DOMAIN_BUILDERS) but draws no series to follow, and a bars page's own version of this
    # move is the breakthrough. A builder joins this tuple when its OWN paint step reads the key.


def series_caps(species: list[dict] | None, si: int) -> list[dict]:
    """Every `build_to` that applies to series `si`, in time order (R26-233).

    A cap naming no series applies to every one - the paint's own `forMe` - which is the reading
    `line_build_first_cap` already writes once for R26-226."""
    out = []
    for sp in species or []:
        if sp.get("kind") != "build_to" or not isinstance(sp.get("target"), dict):
            continue
        ss = sp.get("series", sp.get("tier", (sp.get("target") or {}).get("series")))
        if ss is not None and int(ss) != int(si):
            continue
        out.append(sp)
    return sorted(out, key=lambda sp: float(sp.get("at") or 0.0))


def follow_draw_windows(species: list[dict] | None, si: int) -> list[tuple[float, float]]:
    """Every window in which series `si` is DRAWING while a transition is on it (R26-233).

    Not every clock a line draws on survives a rescale, and this is the measurement the row turns on: a
    rescale paints the standing chart FULLY BUILT (`lpPaintRescale`'s own `lpPaintChart(A, 1, ...)`), so the
    page's build fraction - and with it `;build=lines`' turn - is 1 for the whole transition. What still
    moves under it is the CAP SEQUENCE, which runs on absolute t (`scene-evidence-engine.mjs:11587`), and
    the FIRST cap by `at` is the level the build LANDS at (`f = f * capFrac(first)`, a constant while c is
    1), never a draw. So the windows a domain can follow are the caps AFTER the first, each over its own
    `at` -> `at + dur`."""
    return [(float(sp.get("at") or 0.0), float(sp.get("at") or 0.0) + max(0.001, float(sp.get("dur") or 1.0)))
            for sp in series_caps(species, si)[1:]]


def rescale_follow_series(world: dict, sp: dict, species: list[dict] | None, where: str) -> int:
    """`follow` on a `chart_to rescale` -> the SERIES INDEX whose drawn extremum the y domain's top tracks.

    Resolves `true` (the series this row's own `build_to` draws), a series NAME, or an index - and refuses,
    by name and with the numbers, every shape in which the domain would not in fact be following the line:
    a page with no line to read, a series that is not drawing over the rescale's own window, a rescale that
    ends before the line does (the domain would be handed over mid-climb - a snap), a target top the series'
    own numbers never reach (the last of the move would happen after the line stopped, which is the drag
    this row exists to end), and a target that does not OPEN the domain upward at all."""
    page = (world or {}).get("page") or {}
    builder = page.get("builder")
    if builder not in FOLLOW_BUILDERS:
        raise ValueError(f"{where}: follow tracks a DRAWING LINE and this page is {builder!r} - the builder whose "
                         f"paths are its series is {' and '.join(FOLLOW_BUILDERS)}. A bars page's own version of this "
                         "move is the BREAKTHROUGH: the bar shoots while the axis rescales (E60)")
    sers = list(page.get("series") or [])
    names = [str(s.get("name") or s.get("label") or "").strip() for s in sers]
    want = sp.get("follow")
    if want is True:
        caps = [e for e in (species or []) if e.get("kind") == "build_to" and isinstance(e.get("target"), dict)]
        if not caps:
            raise ValueError(f"{where}: follow: true is \"the series this row's build_to draws\" and the row has no "
                             "build_to at all. Name the line (follow: <name|index>), or stage it with a build_to on "
                             "the word that draws it - which is also the only clock a rescale leaves running (R26-233)")
        named = {e.get("series", e.get("tier", (e.get("target") or {}).get("series"))) for e in caps}
        if None in named:
            raise ValueError(f"{where}: follow: true - a build_to that names no series applies to EVERY series (the "
                             "paint's own `forMe`), so it names no ONE line to follow. Write follow: <name|index>")
        if len(named) != 1:
            raise ValueError(f"{where}: follow: true - this row's build_to species name {len(named)} different series "
                             f"({', '.join(str(int(v)) for v in sorted(named))}), so which line the domain follows is "
                             "the row's to say. Write follow: <name|index>")
        idx = int(next(iter(named)))
    elif isinstance(want, str):
        hits = [i for i, nm in enumerate(names) if nm.lower() == want.strip().lower()]
        if not hits:
            raise ValueError(f"{where}: follow={want!r} - the page has no series by that name. Its series are "
                             + ", ".join(f"{i}: {nm or '(unnamed)'}" for i, nm in enumerate(names)))
        if len(hits) > 1:
            raise ValueError(f"{where}: follow={want!r} names {len(hits)} of the page's series - name the index instead")
        idx = hits[0]
    else:
        idx = int(want)
    if not 0 <= idx < len(sers):
        raise ValueError(f"{where}: follow={want!r}: the page draws {len(sers)} series "
                         f"({'0..%d' % (len(sers) - 1) if sers else 'none'})")
    # A `later: true` series needs no check here and that is worth writing down: `LPG.build_spec` leaves it OUT of
    # the page's series list altogether (it arrives by `chart_to extend`), so a follow that names one is refused
    # above as a name - or an index - the page does not have. Measured in
    # `test_a_later_series_is_not_on_the_page_to_follow`.
    vals = [float(v) for _x, v in (sers[idx].get("pts") or [])]
    if not vals:
        raise ValueError(f"{where}: follow={want!r}: series {idx} ({names[idx] or 'unnamed'}) carries no data")
    ymax = float(sp["ymax"])
    dom = (page.get("axes") or {}).get("domain") or []
    standing = dom[1] if len(dom) == 2 and isinstance(dom[1], (int, float)) else None
    if standing is not None and ymax <= float(standing):
        raise ValueError(f"{where}: follow={want!r}: the page stands on a domain whose top is {float(standing):g} and "
                         f"ymax is {ymax:g} - a followed rescale OPENS the domain upward (the landed ink yields as the "
                         "line climbs PAST the old top). Name a higher ymax, or drop follow")
    top = max(vals)
    if top <= 0:
        raise ValueError(f"{where}: follow={want!r}: series {idx} ({names[idx] or 'unnamed'}) tops out at {top:g} and "
                         f"the air above the tip is a FACTOR on the value (x{FOLLOW_HEADROOM:g}) - a factor holds no "
                         "air above a number at or below zero. Follow a series that climbs in positive values")
    reach = top * FOLLOW_HEADROOM
    if reach < ymax - 1e-9:
        raise ValueError(f"{where}: follow={want!r}: series {idx} ({names[idx] or 'unnamed'}) tops out at {top:g}, so "
                         f"with the page's own air (x{FOLLOW_HEADROOM:g}) it pushes the domain to {reach:.6g} and no "
                         f"further - ymax {ymax:g} would be reached after the line had stopped, which is the drag this "
                         f"row exists to end. Name ymax at or under {reach:.6g}, or follow the line that does reach it")
    wins = follow_draw_windows(species, idx)
    rs_at = float(sp.get("at") or 0.0)
    rs_to = rs_at + max(0.001, float(sp.get("dur") or 1.0))
    over = [w for w in wins if w[1] > rs_at + 1e-6 and w[0] < rs_to - 1e-6]
    if not over:
        drawn = ", ".join(f"[{a:g}, {b:g}]" for a, b in wins) or "none"
        raise ValueError(f"{where}: follow={want!r}: series {idx} ({names[idx] or 'unnamed'}) is not DRAWING over the "
                         f"rescale's own window [{rs_at:g}, {rs_to:g}] - the windows a domain can follow on this row "
                         f"are {drawn}. A rescale paints the standing chart fully built, so what draws under it is the "
                         "cap sequence: a build_to AFTER the first (the first is the level the build lands at). Stage "
                         "the line with a build_to on the word that climbs, and give the rescale that window")
    draw_end = max(b for _a, b in over)
    if rs_to < draw_end - 1e-6:
        raise ValueError(f"{where}: follow={want!r}: the rescale ends at {rs_to:g} and series {idx} "
                         f"({names[idx] or 'unnamed'}) draws until {draw_end:g} - the domain would be handed to the "
                         f"target state while the line was still climbing, which is a snap. Give the rescale the "
                         f"line's own clock (dur {draw_end - rs_at:g})")
    return idx


def page_form_spec(value: str, builder: str, where: str) -> dict:
    """The row's form, refused BY NAME when this page's builder cannot draw it (`ledger_page.form_error`)."""
    name = str(value).partition(":")[0]
    err = LPG.form_error(name, builder, where)
    if err:
        raise ValueError(err)
    return page_form_geom(str(value), where)


def image_aspect(p: Path) -> float | None:
    """A picture's height over its width, or None for anything that is not a still. The PLAYER cannot ask this
    question in time - an <img> has no height until it decodes, the player paints once per seek, and a card
    measured mid-decode is a card laid out on the wrong box - so the compiler, which has the file, answers it."""
    try:
        if is_video_asset(p):
            return None
        from PIL import Image
        with Image.open(p) as im:
            return round(im.height / im.width, 5) if im.width else None
    except (OSError, ValueError):
        return None


EMBED_CARD_PAYLOADS = ("record", "chart", "stack")   # evidence that makes a dock a CARD: the engine paints a `fit` entry as a bare picture


def embed_card_reason(evidence: dict | None) -> str | None:
    """Why a dock's evidence is a CARD, not a picture - its badge rail, record, chart or stack - else None."""
    ev = evidence or {}
    if ev.get("badges"):
        return "badges"
    return next((k for k in EMBED_CARD_PAYLOADS if ev.get(k)), None)


def embed_fit(dopt: dict, asset: Path | None, evidence: dict | None = None) -> str | None:
    """How a dock's picture takes its surface (the operator, 2026-09-13: "the tv surface should definitely be prepared
    to hold video and images"; E95: "stills should probably fill the tv surface"). `cover` is for a PICTURE only - the
    engine draws any entry carrying `fit` as "not a card: no paper, no masthead, no rail" (the parent, 2026-09-13):
    (1) the row's own `fit` - refused on a card; (2) None for a PRESS card, which REFLOWS to its surface (E66);
    (3) None - the reflowed CARD it always was - when the dock's `evidence` carries badges, a record, a chart or a
    stack; (4) else `cover`, a bare still or a clip. `asset` is kept for the call site; the default ignores its kind."""
    if not (dopt or {}).get(EMBED_KEY):
        return None
    card = embed_card_reason(evidence)
    if dopt.get("fit") is not None:
        if card:
            raise ValueError(f"fit={dopt['fit']!r} on a dock whose evidence carries {card}: a card is not a picture - "
                             "a `fit` entry is painted with no paper, masthead or rail, so drop `fit` and it reflows onto the surface")
        return dopt["fit"]
    if dopt.get("press") or card:
        return None
    return EMBED_FIT_DEFAULT


def embed_entry(name: str, spec: dict, words=None, card_aspect: float | None = None, fit: str | None = None) -> dict:
    """What the dock carries onto the timeline: the surface's name, its quad, the SECOND the room dims on, and
    the card PICTURE's aspect (so the player can letterbox the card on the surface without measuring it).

    `darken` is authored as the word (the plate's manifest speaks the script's language, as every shot row does) and
    resolved here against the build's own words, so the player never has to find a word at render time."""
    quad = [[round(float(x), 5), round(float(y), 5)] for x, y in spec["quad"]]
    out = {"name": name, "quad": quad}
    for key in ("kind", "sheen"):      # E66: the surface's own treatment as the plate declares it (screen | paper; the sheen's strength)
        if spec.get(key) is not None:
            out[key] = spec[key]
    if fit is not None:   # 2026-09-13: a PICTURE on the surface (cover | contain); absent, the entry is what it always was
        if fit not in EMBED_FITS:
            raise ValueError(f"embed {name!r}: fit={fit!r} is not one of {'|'.join(EMBED_FITS)}")
        out["fit"] = fit
    if card_aspect is not None and float(card_aspect) > 0:
        out["img"] = round(float(card_aspect), 5)
    dk = spec.get("darken")
    if dk is None:
        return out
    if isinstance(dk, (int, float)) and not isinstance(dk, bool):
        out["darken"] = round(float(dk), 2)
        return out
    ws = _override_words(words)
    if not ws:
        raise ValueError(f"embed {name!r}: darken={dk!r} is a WORD and this build has no words to date it by")
    from authoring import words as KW
    try:
        out["darken"] = KW.at(ws, dk)
    except SystemExit as exc:
        raise ValueError(f"embed {name!r}: darken={dk!r} - {exc}") from None
    return out


def resolve_embed_targets(row_species, embeds: dict, where: str) -> None:
    """E59 reason 4: a camera move may take a declared SURFACE as its target. The quad is written onto the target
    here - the player resolves a region, never a plate's manifest. Raises ValueError naming the surface."""
    for sp in row_species or []:
        tg = sp.get("target") if isinstance(sp, dict) else None
        if not isinstance(tg, dict) or tg.get("kind") != EMBED_TARGET:
            continue
        name = tg.get("name")
        if name not in embeds:
            named = ", ".join(sorted(embeds)) if embeds else "none"
            raise ValueError(f"{where}: {sp.get('kind')} target embed {name!r} is not a surface of this plate "
                             f"- it declares {named}")
        err = embed_quad_error(name, embeds[name], where)
        if err:
            raise ValueError(err)
        tg["quad"] = [[round(float(x), 5), round(float(y), 5)] for x, y in embeds[name]["quad"]]


def dock_opts(raw) -> dict:
    """The optional 5th element of a dock tuple: ``{"arrive": spring|throw|land, "mass": paper|metal|liquid|ink}`` (P47 T1).
    ValueError names the key; the caller names the row."""
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"dock options must be a dict of {'|'.join(DOCK_OPTS)}, not {raw!r}")
    for k, v in raw.items():
        if k not in DOCK_OPTS:
            raise ValueError(f"dock option {k!r} is not one of {'|'.join(DOCK_OPTS)}")
        if k == "behind":   # HF-17: the plate's foreground layer this card goes behind; the plate is checked at the row
            if not isinstance(v, str) or not v.strip():
                raise ValueError("dock: behind must name a foreground layer of the scene's plate (<plate>.layers.json)")
            continue
        if k == "depth":   # P58 T6 (a): the plane the card stands on - the camera's own range, checked against `behind` below
            dock_depth_k(v, "dock")
            continue
        if k == EMBED_KEY:   # P50 T7: the plate's surface this card lands ON; the plate and the quad are checked at the row
            if not isinstance(v, str) or not v.strip():
                raise ValueError("dock: embed must NAME a surface the scene's plate declares (<plate>.layers.json)")
            continue
        if k == "fit":   # 2026-09-13: a picture on a surface - checked against the row's embed and press below
            if v not in EMBED_FITS:
                raise ValueError(f"dock: fit must be {'|'.join(EMBED_FITS)} - how a picture takes its surface, not {v!r}")
            continue
        if k == "centre":
            if v is not True:
                raise ValueError("dock: centre must be True (the card parks centred on the page)")
            continue
        if k == "cutout":   # P53 T7 / R26-94: the dock is a person, not a document - checked against press/stack/embed/fit below
            if v is not True:
                raise ValueError("dock: cutout must be True - the dock is a cutout, no card")
            continue
        if k == "prop":   # R26-246 (b) / E99 s87: the dock is a PROP added to the world - checked against press/stack/embed/fit/cutout below
            if v is not True:
                raise ValueError("dock: prop must be True - the dock is a prop added to the world, no card")
            continue
        if k == "ink":   # ... and how its art is laid down: its own colour, or the page's own ink (E99 s87, open on the operator's eye)
            if v not in DOCK_INKS:
                raise ValueError(f"dock: ink must be {'|'.join(DOCK_INKS)} - the prop's own colour, or the page's own ink")
            if not raw.get("prop"):
                raise ValueError("dock: ink is a PROP's option - a card in a frame is evidence and is never re-inked")
            continue
        if k == "card_aspect":
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
                raise ValueError("dock: card_aspect must be a positive number (the card's height over its width)")
            continue
        if k == "centre_w":
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0.05 <= v <= 1.0:
                raise ValueError("dock: centre_w must be a share of the stage width between 0.05 and 1.0")
            continue
        if k == "centre_band":
            if v not in DOCK_BAND_ORDER:
                raise ValueError(f"dock: centre_band must be one of {'|'.join(DOCK_BAND_ORDER)}")
            continue
        if k in ("centre_y", "centre_x"):
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0.0 <= v <= 1.0:
                raise ValueError(f"dock: {k} must be the card's centre as a share of the stage, 0..1")
            continue
        if k == "read":   # the READING box of a centred card that then parks (2026-09-10): the same centre keys, its own
            if not isinstance(v, dict) or not v or any(rk not in ("centre_w", "centre_x", "centre_y", "card_aspect") for rk in v):
                raise ValueError("dock: read must be a dict of centre_w|centre_x|centre_y|card_aspect - the box the card pops at before it parks to its place")
            if not raw.get("centre"):
                raise ValueError("dock: read is a CENTRED card's option (the park target is its centred place)")
            for rk, rv in v.items():
                if isinstance(rv, bool) or not isinstance(rv, (int, float)) or rv <= 0 or (rk != "card_aspect" and rv > 1.0):
                    raise ValueError(f"dock: read.{rk} must be a positive share of the stage (card_aspect: height over width)")
            continue
        if k in ("read_s", "park_s"):   # the dock's own clock: the hold at the reading box, the park's length (the compiler's defaults otherwise)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
                raise ValueError(f"dock: {k} must be seconds > 0")
            continue
        if k == "press":   # P50 T3: the card is a headline cut from a screenshot - press_meta validates it
            continue
        if k == "stack":
            if v is not True:
                raise ValueError("dock: stack must be True (the card joins the scene's press pile)")
            continue
        _check_opt(k, v, "dock")
    if raw.get("cutout"):   # R26-94: a cutout is neither a card nor a picture on a surface (the painter's `.dock.cutout`)
        for other, why in (("press", "a press card's kind overwrites the cutout's and the pile keys on it"),
                           ("stack", "the press stack is a pile of cards"),
                           ("embed", "the surface's projection repaints a card's shadow, vignette and lift over it"),
                           ("fit", "fit is how a picture takes a surface")):
            if other in raw:
                raise ValueError(f"dock: cutout and {other} cannot be combined - a cutout has no card ({why})")
    if raw.get("arrive") == "stamp":   # R26-20 send-back #2: a stamp lands at ONE fitted box, and only a dock's own painter stamps
        for other, why in (("read", "a stamp lands where its ring is fitted - it never pops at a reading size and slides to a park"),
                           ("read_s", "a stamp has no reading hold: it lands at its fitted box"),
                           ("park_s", "a stamp has no park: it lands at its fitted box"),
                           ("centre_band", "a stamp's room is searched for its ring, not chosen by a card's band"),
                           ("embed", "the surface's projection repaints the dock over the stamp's own transform, and its ring would be drawn round the unprojected box")):
            if other in raw:
                raise ValueError(f"dock: arrive=stamp and {other} cannot be combined ({why})")
    if raw.get("prop"):   # E99 s87: a PROP is art in the world - it is not a document, not a person above a crawl, and not on a surface
        for other, why in (("press", "a press card's kind overwrites the prop's and the pile keys on it"),
                           ("stack", "the press stack is a pile of cards"),
                           ("embed", "a prop joins the world, it is not projected onto a poster in it"),
                           ("fit", "fit is how a picture takes a surface"),
                           ("cutout", "both stand the chrome down and only one kind reaches the evidence map - "
                                      "a prop keeps its whole picture, a cutout dissolves its foot into the band")):
            if other in raw:
                raise ValueError(f"dock: prop and {other} cannot be combined - a prop is art added to the world ({why})")
    out = dict(raw)
    if "press" in out:
        out["press"] = press_meta(out["press"])   # a path resolves here, so every caller downstream sees the dict
    elif out.get("stack"):
        raise ValueError("dock: stack is the PRESS stack - it belongs to a dock that carries `press` (the push hand-off, doc 29 s9.27)")
    if out.get(EMBED_KEY) and out.get("stack"):   # P50 T7: a card on a surface has no pile - the surface is the park
        raise ValueError("dock: embed and stack are two different arrivals - a card that lands ON a surface is not "
                         "pushed into a pile (E45's park is the surface itself)")
    if out.get("fit") is not None and not out.get(EMBED_KEY):
        raise ValueError("dock: fit is how a picture takes a SURFACE - it needs the row's embed=<surface>")
    if out.get("fit") is not None and out.get("press"):
        raise ValueError("dock: fit is a picture's option - a press card REFLOWS to its surface (E66), it is never cropped to it")
    if out.get("depth") is not None:   # P58 T6 (a): the plane the card stands on - resolved here, so every caller downstream sees the number
        out["depth"] = dock_depth_k(out["depth"], "dock")
        if out.get(EMBED_KEY):   # a card ON a declared surface already stands in the plate's space: the surface IS its plane
            raise ValueError("dock: embed and depth are two names for one thing - a card that lands on a declared "
                             "surface stands on that surface's own plane (P50 T7), so it takes the camera's move "
                             "through the world it is part of: drop depth= or drop embed=")
        if out.get("behind"):   # HF-17's occluder plane is the ceiling: a card behind the front is never nearer than it
            _derr = dock_depth_behind_error(out["depth"], out["behind"], "dock")
            if _derr:
                raise ValueError(_derr)
    return out


def world_for_plate(plate_id: str, ken: tuple, ep_dir: Path, meta: dict | None = None) -> dict:
    """A scene's ``world`` for a shot-table plate id, with E49's ``;idle=<kind>`` option stripped off and carried
    as ``world["idle"]`` (the player reads it for the page or the plate; absent = the class default)."""
    bare, opts = split_plate_opts(plate_id)
    # Check the authored surface handoff's mutually exclusive options before
    # loading the world.  This preserves the option refusal when a prior
    # compile left ASPECT at 9:16; a valid surface still reaches ledger_world's
    # 16:9-only guard below.
    if bare.startswith(LEDGER_PREFIX):
        _surface_enter = parse_ledger_id(bare)[4]
        if isinstance(_surface_enter, str) and _surface_enter.startswith("surface="):
            competing = [key for key in ("depth", "plane", "form", "arrive") if key in opts]
            if competing:
                raise ValueError(f"{plate_id!r}: surface= cannot combine with "
                                 f"{', '.join(key + '=' for key in competing)} - the handoff has one registered "
                                 "paper plane and one arrival")
    world = _world_for_bare_plate(bare, ken, ep_dir, meta)
    page = world.get("page") if isinstance(world, dict) else None
    if isinstance(page, dict) and page.get("enter") == "surface":
        competing = [key for key in ("depth", "plane", "form", "arrive") if key in opts]
        if competing:
            raise ValueError(f"{plate_id!r}: surface= cannot combine with "
                             f"{', '.join(key + '=' for key in competing)} - the handoff has one registered "
                             "paper plane and one arrival")
    thens = opts.pop("then", [])
    card = opts.pop("card", None)
    if card is not None:   # card=yes|no is a LEDGER PAGE option: the page keeps the card's rounded corners and a hard-edge shadow at full size
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError(f"{plate_id!r}: card= is a LEDGER PAGE option")
        world["page"]["card"] = card == "yes"
    thread = opts.pop("thread", None)
    if thread is not None:   # HF-16: the arriving PAGE starts with one mark of the page before it already on it
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError(f"{plate_id!r}: thread= is a LEDGER PAGE option - a wire is one mark of a page, carried onto the next page")
        world["page"]["thread"] = {"key": thread}   # `from` is the scene before this one: the build loop fills it, and checks it
    path = opts.pop("path", None)
    if path is not None:
        # E91 s1 (R26-78): the path between the period knots is a RACE PAGE's setting and it is the ROW's word,
        # not the object's - the series file carries the data, how this shot moves through it is the plate id's,
        # as `card=` and `pill=` are. `eased` is the default and names the engine as it is; `clothoid` fits the
        # same knots on the same clock. `_check_opt` has already refused any other word by name.
        if world.get("kind") != SPECIES_LEDGER or (world.get("page") or {}).get("builder") != "race":
            raise ValueError(f"{plate_id!r}: path= is a RACE page option - it is the path a racing mark takes between "
                             f"two periods (this page is {((world.get('page') or {}).get('builder') or world.get('kind') or 'a plate')!r})")
        world["page"]["path"] = path
    pill = opts.pop("pill", None)
    if pill is not None and pill != "no":
        # P50 T11 (R26-34): the tip-riding pill is a LINE PAGE's option and it is the ROW's word, not the object's -
        # the evidence object carries the data (AXES_KEYS); how this shot draws it is the plate id's, as `card=` is.
        # It rides the DRAW, and the beats that drive the draw (build_to) are declared on the same row.
        if world.get("kind") != SPECIES_LEDGER or (world.get("page") or {}).get("builder") not in MORPH_BUILDERS:
            raise ValueError(f"{plate_id!r}: pill= is a DENSE-LINE page option - the pill rides a line's drawing tip "
                             f"(this page is {((world.get('page') or {}).get('builder') or world.get('kind') or 'a plate')!r})")
        world["page"]["tip_pill"] = True if pill == "yes" else {"milestone": int(pill)}
    depth = opts.pop("depth", None)
    plane = opts.pop("plane", None)
    if depth is not None or plane is not None:
        # P58 T4 / E98 s3: the page as a CARD AT A DEPTH. Both are LEDGER PAGE options - a plate is a world and
        # takes its depth from its own sidecar's planes (P58 T2), never from a row - and both are written on the
        # page only when the row names them, so an unauthored page's timeline entry is byte-identical.
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError(f"{plate_id!r}: {'depth' if depth is not None else 'plane'}= is a LEDGER PAGE option - "
                             "a plate declares its depth planes in its own <plate>.layers.json (P58 T2), not on the row")
        page = world["page"]
        if depth is not None:
            page["depth"] = page_depth_k(str(depth), repr(plate_id))
        if plane is not None:
            page["plane"] = page_plane_spec(str(plane), repr(plate_id))
    form = opts.pop("form", None)
    if form is not None:
        # P58 T5 / E98 s3: the two 2.5D CHART FORMS. A LEDGER PAGE option, like depth= and plane= - a plate is a
        # picture and declares its planes in its own sidecar (P58 T2) - and written on the page only when the row
        # names it, so an unformed page's timeline entry is byte-identical.
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError(f"{plate_id!r}: form= is a LEDGER PAGE option - it is how a page's CHART is drawn "
                             "(a plate is a picture: its own depth is its <plate>.layers.json's, P58 T2)")
        page = world["page"]
        spec = page_form_spec(str(form), str(page.get("builder") or "?"), repr(plate_id))
        if page.get("plane"):
            raise ValueError(f"{plate_id!r}: form={spec['kind']} and plane= on one page are two surfaces - ONE "
                             "plane per page. A form draws the chart on its own plane; plane= turns the whole "
                             "page as a card (P58 T4). Keep one: drop plane=, or drop form=")
        page["form"] = spec
    fld = opts.pop("field", None)
    if fld is not None:
        # E99 s35: the page's GROUND, authored by the sentence's job. A LEDGER PAGE option - a plate is a picture and
        # IS its own ground - and written on the page only when the row names it, so a page that names none is
        # byte-identical (and a `field` key that reached the page from elsewhere, as a golden fixture's does, stands).
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError(f"{plate_id!r}: field= is a LEDGER PAGE option - it names the GROUND a page's charcoal "
                             "arrives on (E99 s35); a plate is a picture and is its own ground")
        world["page"]["field"] = page_field_spec(str(fld), world["page"], repr(plate_id))
    dom = opts.pop("domain", None)
    if dom is not None:
        # R26-223: the y scale the page is BORN on. A LEDGER PAGE option - a plate is a picture and has no scale -
        # and written onto the page's own `axes` only when the row names one, so a page that names none is
        # byte-identical and the OBJECT's domain stays the default. The player needs nothing new: `axes.domain` is
        # the key a derived rescale state already carries and the line and bars builders already read.
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError(f"{plate_id!r}: domain= is a LEDGER PAGE option - it is the y scale a page OPENS on "
                             "(R26-223); a plate is a picture and carries no scale")
        page = world["page"]
        page.setdefault("axes", {})["domain"] = page_domain_spec(dom, str(page.get("builder") or "?"), repr(plate_id))
    bld = opts.pop("build", None)
    if bld is not None:
        # R26-226: HOW this page's chart builds - its series one at a time, each whole. A LEDGER PAGE option
        # (a plate is a picture and has nothing to build), and the ROW's word rather than the object's: the
        # data is the object's, the rhythm this shot draws it at is the row's, exactly as `;domain=` is. The
        # seconds are one SERIES' - the compiler turns them into the page's own `build_s`, the single key the
        # engine's `buildDur` and the motion gate's landing both read, so the row's clock outranks the
        # object's. A row that names none writes nothing.
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError(f"{plate_id!r}: build= is a LEDGER PAGE option - it is how a page's CHART BUILDS "
                             "(R26-226); a plate is a picture and has no series to draw")
        page = world["page"]
        spec = page_build_spec(bld, str(page.get("builder") or "?"), len(page.get("series") or []), repr(plate_id),
                               page_build_s=float(page.get("build_s") or MG.LP_BUILD_S))
        page["build"] = spec["mode"]
        if "build_s" in spec:
            page["build_s"] = spec["build_s"]
    rd = opts.pop("readability", None)
    if rd is not None:
        # P69 T8 (E99 s97): the PAGE PROFILE this shot draws the page in - `longform` (the measured Bravos page) or
        # T17's `landscape-phone`. A LEDGER PAGE option and the ROW's word, as `;domain=` is: the object carries the
        # data, the row says how this shot draws it, so the row's profile wins over the series file's own field.
        # Written onto the page's own `axes` only when the row names one - a row that names none is byte-identical.
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError(f"{plate_id!r}: readability= is a LEDGER PAGE option - it is the profile a page's chart "
                             "is drawn in (P69 T8); a plate is a picture")
        page = world["page"]
        err = LPG.readability_error(page, rd, str(page.get("builder") or "?"))
        if err:
            raise ValueError(f"{plate_id!r}: {err}")
        profile, preset = LPG.parse_readability(rd)
        if profile == LPG.LONGFORM and ASPECT == "9:16":   # REVIEW-P69-LANE-B-MERGE-2 N4: never accepted and ignored
            raise ValueError(f"{plate_id!r}: readability={rd!r} is the long form's 16:9 page profile - the player never "
                             "draws it in portrait (a 9:16 page keeps its own layout, P41), so a 9:16 row may not name it")
        if profile == LPG.LONGFORM:   # the preset and, on a line page, the end-tag form that keeps every tag on the stage
            LPG.apply_longform(page, preset)
        else:
            axes = page.setdefault("axes", {})
            axes["readability"] = profile
            for key in ("type_scale", "tag_form", "tag_room"):   # a series file's long form, overruled by the row
                axes.pop(key, None)
    elif isinstance(world.get("page"), dict) and (world["page"].get("axes") or {}).get("readability") == LPG.LONGFORM:
        LPG.apply_longform(world["page"])   # the series file's own long form, re-fitted to the badges the row's dock gave it
    room = opts.pop("room", None)
    if room is not None:
        # R26-221: the rectangle of this PICTURE PLATE a card may stand in - the plate's answer to a page's
        # quiet zone. A PLATE option, the mirror of the ledger page's own `field=` / `form=`: a page's room is
        # computed from its own ink (`page_place`), so a page naming one would be two truths about one space.
        # Kept as FRACTIONS on the world (the compiler turns them into stage px for the aspect it is building),
        # and written only when the row names one.
        kind = world.get("kind")
        if kind in (SPECIES_LEDGER, VECMAP_KIND, SPECIES_CLIP):
            raise ValueError(f"{plate_id!r}: room= is a PICTURE PLATE option - it declares the rectangle a card may "
                             f"stand in (R26-221). A {kind} world computes its own room from its own ink "
                             "(page_place / E65), so declaring one here would be two truths about one space")
        world["room"] = plate_room_spec(room, repr(plate_id))
    drift_px = opts.pop(PLATE_DRIFT_OPT, None)
    if drift_px is not None:
        # E99 s55: the AMPLITUDE of this scene's plate idle walk. A PLATE option, the mirror of the ledger page's
        # own `depth=` / `form=` / `field=`: the player's idle pose is read for a PLATE alone (a page, a vector map
        # and a clip each carry their own motion and take the identity pose there), so the row is refused by name
        # rather than writing a number nothing will read. `;idle=` must already name a kind whose pose HAS a dx/dy.
        kind = world.get("kind")
        if kind in (SPECIES_LEDGER, VECMAP_KIND, SPECIES_CLIP):
            raise ValueError(f"{plate_id!r}: drift= is a PLATE option - it sizes the idle WALK of a picture plate "
                             f"(E99 s55). A {kind} world carries its own motion and takes no plate idle pose")
        if opts.get("idle") not in DRIFT_IDLES:
            raise ValueError(f"{plate_id!r}: drift= sizes the walk of an idle that HAS one - name "
                             f"{' or '.join(';idle=' + k for k in DRIFT_IDLES)} on the same plate id "
                             f"(this row's idle is {opts.get('idle') or 'unset'!r})")
        world["idle_drift_px"] = plate_drift_px(drift_px, repr(plate_id))
    world.update(opts)   # idle (E49), arrive / mass (P47 T1), use (E61) - written only when the row names them
    if thens:   # P48 T4: the other charts this page can become, each a full spec built at load
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError(f"{plate_id!r}: then= is a LEDGER PAGE option: only a page has chart states")
        if len(thens) > STATE_MAX - 1:
            raise ValueError(f"{plate_id!r}: {len(thens) + 1} chart states is past STATE_MAX ({STATE_MAX}): "
                             "a fourth chart is a new page or a card")
        world["page_states"] = [_page_state(t, ep_dir, repr(plate_id)) for t in thens]
        if (world["page"].get("axes") or {}).get("readability") == LPG.LONGFORM:
            # REVIEW-P69-LANE-B-MERGE-2 N2: every state is drawn in the page's box, viewBox and preset - so each takes
            # the profile and its OWN fitted end-tag form, and a line page's viewBox makes room for the widest of them
            err = LPG.apply_longform_states(world["page"], world["page_states"])
            if err:
                raise ValueError(f"{plate_id!r}: {err}")
    return world


def _world_for_bare_plate(plate_id: str, ken: tuple, ep_dir: Path, meta: dict | None = None) -> dict:
    """A scene's ``world`` for a shot-table plate id: a ledger page (``ledger:``
    prefix) or an image plate resolved by the asset resolver. Pure apart from
    reading the series / plate file; ValueError on a bad or missing id."""
    if plate_id.startswith(LEDGER_PREFIX):
        return ledger_world(plate_id, ken, ep_dir, ((meta or {}).get(parse_ledger_id(plate_id)[0]) or {}).get("badges"))
    if VECMAP_PREFIX.match(plate_id):   # P50 T5: the VECTOR MAP world - drawn from data, like a page, never an embedded plate
        if ken and ken[0]:
            raise ValueError(f"{plate_id!r}: a vector map takes no Ken Burns - the camera moves between focal points on the "
                             "map and then holds (E59 reason 2), and a drifting map would move under the lights on it")
        return {"kind": VECMAP_KIND, "map": WORLD_MAP, "focus": parse_vecmap_id(plate_id), "box": world_map()["box"],
                "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    if plate_id.startswith(CLIP_PREFIX):
        cp = Path(plate_id[len(CLIP_PREFIX):])
        cp = cp if cp.is_absolute() else Path(ep_dir) / cp
        if not cp.exists():
            raise ValueError(f"{plate_id!r}: clip missing: {cp}")
        return {"kind": SPECIES_CLIP, "asset_id": cp.stem, "clip_path": str(cp), "sha256": sha(cp),
                "ken_burns": {"scale": ken[0], "x": ken[1], "y": ken[2]}}
    wp = R.find_asset(plate_id)
    if wp is None:
        raise ValueError(f"{plate_id!r}: no plate asset found")
    return {"asset_id": plate_id, "sha256": sha(wp),
            "ken_burns": {"scale": ken[0], "x": ken[1], "y": ken[2]}}


# Embedding source PNGs verbatim produced a 366 MB player that no browser
# would open. The stage is 1920x1080 and a world plate never draws larger
# than that, so anything beyond it is bytes the viewer cannot see. Evidence
# caps at 1400 (drawn at most 880 wide, so still ~1.6x for crisp text).
STAGE_W, CARD_W, Q = 1920, 1400, 90


def data_uri(p: Path, cap: int | None = None) -> str:
    """Embed an asset, downscaled to what the stage can actually show."""
    if cap is None:
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"
    from PIL import Image
    im = Image.open(p).convert("RGB")
    if im.width > cap:
        im = im.resize((cap, round(im.height * cap / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=Q, optimize=True, progressive=True)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"


def is_video_asset(p: Path) -> bool:
    """True for a dock asset that is a clip rather than a still (E44 / R26-7)."""
    return p.suffix.lower() in VIDEO_SUFFIXES


def dock_asset_path(aid: str, ep_dir: Path) -> Path:
    """The file behind one dock asset id.

    ``clip:<path>`` names a video file outright - the same form a CLIP WORLD takes, relative to
    the episode unless absolute - so a generated clip docks without first being catalogued as a
    plate. Every other id goes through the asset resolver, which already reaches an
    ``evidence/objects/<id>.mp4``. ValueError names the id when the file is not there."""
    if aid.startswith(CLIP_PREFIX):
        p = Path(aid[len(CLIP_PREFIX):])
        p = p if p.is_absolute() else Path(ep_dir) / p
        if not p.exists():
            raise ValueError(f"{aid!r}: dock clip missing: {p}")
        return p
    p = R.find_asset(aid)
    if p is None:
        raise ValueError(f"{aid!r}: no dock asset found")
    return p


def dock_uri(p: Path) -> str:
    """Embed one dock asset. A VIDEO embeds raw with its own mime - byte for byte what a clip
    world does - because re-encoding it as a still JPEG is exactly the motion we are docking it
    for; anything else is downscaled to the card width."""
    return data_uri(p) if is_video_asset(p) else data_uri(p, CARD_W)


# ---- DOCK PLACEMENT ON A PAGE (ruling E45 §1, 2026-09-06) -------------------------------------
# "A dock never covers the chart ... the dock is a small card - about half the stage width, not the
# 800px solo card - and it sits in the page's least busy space ... never over the plot, the title
# or the source line, and never in the caption's anchor. The placement is computed from the page's
# own geometry by the compiler, not hand-placed per shot. A dock on a plain plate keeps the solo card."
#
# E45 (2026-09-06), the choreography: "springing the dock, then shrinking it while we slide it to
# the corner OR OVER THE TITLE, so that the graph gains its readability back". The title block is
# therefore ALLOWED under the parked card - the heading has been read by the time the card parks -
# and so is the sub. What stays forbidden is the evidence itself: the plot (which page_boxes
# already widens to cover the basis label above it and the x tick labels below it), the source
# line, the badge rail and the anchored caption's strip.
#
# THE RULE. LPG.page_boxes reports the page's own ink in stage pixels. Subtract the forbidden
# boxes from the mobile safe box and what is left is five candidate bands: `above` (the safe box's
# head -> the plot's head, across the title and the sub), `below` (plot foot -> source), `foot`
# (under the source/rail, above the anchored caption) and the two side columns beside the plot.
# Each band yields the widest card it can hold at 16:9 - capped at DOCK_ON_PAGE_W of the stage,
# floored at DOCK_ON_PAGE_MIN_W - and the band that yields the widest card wins, the declared quiet
# zone breaking ties and DOCK_BAND_ORDER (top band first, then the corners) breaking those. In the
# band the card is pushed to the quiet-zone end and parked against the PLOT (bottom-aligned in a
# horizontal band), so the estimator's one risk - a title that wraps one line off the model - eats
# into the title block the ruling hands us, never the chart.
#
# THE MOBILE SAFE BOX IS NOT NEGOTIABLE (doc 49 s49.1 / 50): the band still starts at the safe
# box's head, not at the title's own top. On a 9:16 page the title is drawn at y=150, above the
# safe box's 280, so "over the title" buys only the part of the title that is on-screen anyway.
#
# THE CALLOUT/BADGE SPECIES STILL LAND (E45 review point): the emphasized datum's callout is drawn
# INSIDE the chart's viewBox, on the datum, and the badge rail is drawn under the source line -
# both inside boxes this search already forbids, so no placement can ever cross them. The quiet
# zone only chooses WHICH free band and which end of it, never whether the plot is fair game.
DOCK_ON_PAGE_W = 0.48        # the small card, as a fraction of the stage width (9:16 -> 518, 16:9 -> 922)
DOCK_ON_PAGE_MIN_W = 240     # a card narrower than this is not evidence any more: stop shrinking
DOCK_PLACE_PAD = 16          # clear air between the card and the ink; also absorbs the page's Ken Burns drift
DOCK_CARD_CHROME_W = 38      # card width - frame width (padding 15+15 + border 4+4), measured
DOCK_CARD_CHROME_H = 45      # card height - frame height (padding 13+13 + border 4+4 + rail gap), measured
DOCK_BAND_ORDER = ("above", "right", "left", "below", "foot")   # ties break in this order, always
# THE TWO-PHASE DOCK (E45, the choreography). A placed dock does not cut in at its parked size: it
# SPRINGS in at reading size, holds DOCK_READ_S so the card can actually be read, then shrinks and
# slides to `place` over DOCK_PARK_S along a minimum-jerk path. The player owns the motion; the
# compiler only states the clock, per dock, so a gate or a test can read it off the timeline.
DOCK_READ_S = 1.2      # the hold at reading size [DERIVED: one caption page, doc 51]
DOCK_PARK_S = 0.7      # the shrink-and-slide to `place` [DERIVED: the roll-out's 0.7]


def dock_card_h(width: int) -> int:
    """A video card's stage height at `width`: a 16:9 slide-frame plus the card's chrome."""
    return round((width - DOCK_CARD_CHROME_W) * 9 / 16) + DOCK_CARD_CHROME_H


def _card_w_for(height: float) -> int:
    """The widest card whose 16:9 frame plus chrome fits `height`."""
    return int((height - DOCK_CARD_CHROME_H) * 16 / 9) + DOCK_CARD_CHROME_W


def free_bands(boxes: dict, reserve: list[dict] | None = None) -> list[dict]:
    """The rectangles inside the safe box that the page's own ink leaves free (E45).

    ONE PLACEMENT TRUTH (P50 T16): the bands are cut out of whatever `page_boxes` handed us - the
    PLAYER's own boxes when the fixture has measured this page's ink, `ledger_page`'s estimate of
    them when it has not (`boxes["measured"]` says which). Every placer - `page_place`,
    `centred_place`, the solo card's E50 centring - cuts its bands here, so no two of them can
    disagree about where a page's free space is.

    The title and the sub are NOT ink for this purpose - E45 parks the card "over the title" once
    the heading has been read - so the head of the `above` band is the safe box's own head."""
    safe, plot = boxes["safe"], boxes["plot"]
    src, rail, cap = boxes["source"], boxes["rail"], boxes["caption_anchor"]
    left, right = safe["x"], safe["x"] + safe["w"]
    head = safe["y"]
    # P52 T6: a NEWSREEL band is one more strip a card may never sit in - exactly the role the anchored
    # caption's strip already plays here (`CAPTION_ANCHOR`, ledger_page.py: "a dock may never sit there") - so
    # it clips the same foot, by name. `reserve` absent (every caller before this slice) changes nothing.
    floor_y = min([cap["y"]] + [r["y"] for r in (reserve or []) if isinstance(r, dict)])
    foot = min(safe["y"] + safe["h"], floor_y)
    ink_foot = max(src["y"] + src["h"], rail["y"] + rail["h"])
    # R26-205: the species' INLINE END NAMES are ink, and on a full-stage page they are the only thing
    # between the plot and the frame - so the `right` band starts after them, not after the plot. A page
    # that reports no `tags` box (every page compiled before this row, and every 9:16 page) is unchanged.
    tags = boxes.get(LPG.TAGS_KEY)
    plot_r = max(plot["x"] + plot["w"], tags["x"] + tags["w"] if tags else 0)
    bands = {
        "above": (left, head, right - left, plot["y"] - head),
        "below": (left, plot["y"] + plot["h"], right - left, src["y"] - plot["y"] - plot["h"]),
        "foot": (left, ink_foot, right - left, foot - ink_foot),
        "left": (left, head, plot["x"] - left, foot - head),
        "right": (plot_r, head, right - plot_r, foot - head),
    }
    return [{"band": name, "x": x, "y": y, "w": w, "h": h}
            for name, (x, y, w, h) in bands.items() if w > 0 and h > 0]


# ---- E65: THE PLACER ALWAYS FINDS A PLACE (ruling E65, 2026-09-11) ---------------------------
# The measured boxes (P50 T16) said what the estimate had hidden: Tokyo's real pages leave NO band
# outside the plot wide enough for a card - the title is one line where the model says two, so the
# chart starts 76 px higher and runs 89 px taller - and `page_place` answered None, which the engine
# painted as the big centred solo card over the chart. The operator: *"inside of the empty data would
# be good, but it can also land underneath partially over-lapping the axis, it's going to be adjusted
# up to the corner right anyways. Remember that we have complete control over the scale and placement
# on the page."*
#
# THE ORDER, and the placer never returns nothing:
#   (1) `outside` - a band outside the plot at the card's size (E45 §1, unchanged: every page that
#       had a band before E65 compiles to exactly the bytes it did);
#   (2) `empty`   - the largest rectangle the DATA's ink does not touch, read off the measured
#       `data_mask`, on the declared quiet side when that side is empty, else the emptiest corner;
#   (3) `axis`    - underneath: the band between the data's foot and the source line, where the card
#       may partially overlap the x tick labels (furniture), never the data;
#   (4) `corner`  - the last resort: the emptiest corner at the legibility floor, and the build
#       WARNS, naming the page. "No place" is not an outcome.
# The card's SCALE gives ground before its place does, down to PLACE_FLOOR_H; the room taken is
# recorded on the entry as `place_room` so the report, the gate and a reader can all see it.
PLACE_FLOOR_H = {"9:16": 120, "16:9": 80}   # the legibility floor: a card shorter than this has stopped being evidence
PLACE_ROOMS = ("outside", "empty", "axis", "corner")


def _floor_h(aspect: str | None) -> int:
    return PLACE_FLOOR_H.get(aspect or "16:9", PLACE_FLOOR_H["16:9"])


def _fit_in(room: dict, want_w: float, floor_h: int, card_aspect: float | None = None) -> tuple[int, int] | None:
    """The card's (w, h) inside `room` - at `want_w` if it fits, else the widest that does - or None
    when even the floor card does not. The room is taken with `DOCK_PLACE_PAD` of air on every side."""
    room_w, room_h = room["w"] - 2 * DOCK_PLACE_PAD, room["h"] - 2 * DOCK_PLACE_PAD
    if room_w <= 0 or room_h <= 0:
        return None
    w = min(float(want_w), room_w, (room_h / card_aspect) if card_aspect else float(_card_w_for(room_h)))
    w = int(w)
    h = round(w * card_aspect) if card_aspect else dock_card_h(w)
    if w < 1 or h > room_h or h < floor_h:
        return None
    return w, h


def _corner_box(room: dict, w: int, h: int, quiet: str | None, centre: tuple[float, float]) -> dict:
    """`w` x `h` pushed into the corner of `room` that is furthest from `centre` - the quiet side
    horizontally when the page declares one, the far end vertically. E65: "it's going to be adjusted
    up to the corner right anyways"."""
    pad = DOCK_PLACE_PAD
    left, right = room["x"] + pad, room["x"] + room["w"] - pad - w
    top, bottom = room["y"] + pad, room["y"] + room["h"] - pad - h
    room_cx, room_cy = room["x"] + room["w"] / 2, room["y"] + room["h"] / 2
    x = right if (quiet == "right" or (quiet is None and room_cx >= centre[0])) else left
    y = top if room_cy <= centre[1] else bottom
    return {"x": round(min(max(x, room["x"]), room["x"] + room["w"] - w)),
            "y": round(min(max(y, room["y"]), room["y"] + room["h"] - h)), "w": w, "h": h}


def _clear_of_axis(box: dict, room: dict, boxes: dict) -> dict:
    """`box` slid up off the x tick labels when its own room has the height to spare (E65 allows a
    card to overlap the axis band; it does not ask it to). Unchanged when the room is that tight."""
    ax = (boxes.get("axis") or {}).get("x")
    if not ax or box["y"] + box["h"] <= ax["y"]:
        return box
    y = ax["y"] - box["h"] - DOCK_PLACE_PAD
    return dict(box, y=round(y)) if y >= room["y"] + DOCK_PLACE_PAD else box


def mask_rooms(boxes: dict) -> list[dict]:
    """Every rectangle of the plot the DATA's ink does not touch, in stage pixels, from the measured
    `data_mask` (E65). Empty when the page carries no mask - an unmeasured page has no room to read.

    Maximal in width for each span of rows, which is every rectangle a card can be put in; the caller
    scores them. The mask's cell is ~40 px on a 9:16 page, so the rectangle is the data's own shape at
    the scale a card is placed at, and a card inside one touches no ink."""
    mask = boxes.get("data_mask")
    plot = boxes.get("plot")
    if not mask or not plot:
        return []
    n = len(mask)
    cw, ch = plot["w"] / n, plot["h"] / n
    out = []
    for r0 in range(n):
        for r1 in range(r0, n):
            run = 0
            for c in range(n + 1):
                clear = c < n and all(mask[r][c] == "0" for r in range(r0, r1 + 1))
                if clear:
                    run += 1
                    continue
                if run:
                    c0 = c - run
                    out.append({"x": plot["x"] + c0 * cw, "y": plot["y"] + r0 * ch,
                                "w": run * cw, "h": (r1 - r0 + 1) * ch,
                                "cells": [r0, c0, r1, c - 1]})
                run = 0
    return out


def mask_is_clear(boxes: dict, box: dict) -> bool:
    """True when `box` touches no cell the DATA's ink is in (E65's own test for "never on the data").
    A page with no mask answers False: nothing is known, so nothing is claimed."""
    mask, plot = boxes.get("data_mask"), boxes.get("plot")
    if not mask or not plot:
        return False
    n = len(mask)
    cw, ch = plot["w"] / n, plot["h"] / n
    for r in range(n):
        y0, y1 = plot["y"] + r * ch, plot["y"] + (r + 1) * ch
        if box["y"] >= y1 or box["y"] + box["h"] <= y0:
            continue
        for c in range(n):
            if mask[r][c] != "1":
                continue
            x0, x1 = plot["x"] + c * cw, plot["x"] + (c + 1) * cw
            if box["x"] < x1 and box["x"] + box["w"] > x0:
                return False
    return True


def axis_room(boxes: dict) -> dict | None:
    """E65 (3): the band UNDER the data - from the foot of the lowest ink in the plot to the source
    line - which a card may take even though the x tick labels live in it. None when the page is not
    measured or the data runs to the plot's foot with nothing under it."""
    mask, plot = boxes.get("data_mask"), boxes.get("plot")
    if not mask or not plot:
        return None
    n = len(mask)
    rows = [r for r in range(n) if "1" in mask[r]]
    top = plot["y"] + ((max(rows) + 1) * plot["h"] / n if rows else 0)
    limit = min(boxes["source"]["y"], boxes["caption_anchor"]["y"])
    axis = (boxes.get("axis") or {}).get("x")
    if axis:                                    # the labels are furniture: the room runs past them
        top = min(top, axis["y"]) if axis["y"] + axis["h"] <= limit else top
    return {"x": plot["x"], "y": top, "w": plot["w"], "h": limit - top} if limit - top > 0 else None


def emptiest_corner(boxes: dict) -> dict:
    """E65 (4): the quadrant of the plot the data touches least, as a rectangle. The quiet side breaks
    a tie; a page with no mask answers with the quiet side's own half, which is all it knows."""
    plot = boxes["plot"]
    quiet = boxes.get("quiet_zone")
    half_w, half_h = plot["w"] / 2, plot["h"] / 2
    mask = boxes.get("data_mask")
    best, best_key = None, None
    for qy in (0, 1):
        for qx in (0, 1):
            if mask:
                n = len(mask)
                r0, r1 = (0, n // 2) if qy == 0 else (n // 2, n)
                c0, c1 = (0, n // 2) if qx == 0 else (n // 2, n)
                ink = sum(mask[r][c] == "1" for r in range(r0, r1) for c in range(c0, c1))
            else:
                ink = 0
            key = (-ink, 1 if (quiet == "right" and qx == 1) or (quiet == "left" and qx == 0) else 0)
            if best_key is None or key > best_key:
                best_key = key
                best = {"x": plot["x"] + qx * half_w, "y": plot["y"] + qy * half_h, "w": half_w, "h": half_h}
    return best


def _pieces_clear_of(room: dict, taken: list[dict]) -> list[dict]:
    """`room` minus every rectangle in `taken`: the maximal pieces left of, right of, above and below each one that cuts
    it (they overlap - every one is a room a card may be fitted into), each keeping the room's other keys (`band`).
    A room nothing cuts is returned as itself. Pure."""
    pieces = [room]
    for t in taken:
        tx1, ty1 = t["x"] + t["w"], t["y"] + t["h"]
        nxt = []
        for p in pieces:
            px1, py1 = p["x"] + p["w"], p["y"] + p["h"]
            if t["x"] >= px1 or tx1 <= p["x"] or t["y"] >= py1 or ty1 <= p["y"]:
                nxt.append(p)
                continue
            for x, y, w, h in ((p["x"], p["y"], t["x"] - p["x"], p["h"]), (tx1, p["y"], px1 - tx1, p["h"]),
                               (p["x"], p["y"], p["w"], t["y"] - p["y"]), (p["x"], ty1, p["w"], py1 - ty1)):
                if w > 0 and h > 0:
                    nxt.append({**p, "x": x, "y": y, "w": w, "h": h})
        pieces = nxt
    return pieces


def page_place(page: dict, aspect: str, reserve: list[dict] | None = None, clear_of: list[dict] | None = None) -> dict:
    """The parked rectangle for a dock on this ledger page, in stage pixels (E45 §1, E65).

    ``{"x", "y", "w", "h", "room"}`` - ALWAYS: `room` is which of E65's four rooms it came from
    (`outside` | `empty` | `axis` | `corner`). Pure: the page spec is never mutated.
    `clear_of` (P69 T5): rectangles the card may not touch anywhere - a stamp's fitted box, the mark and its ring's
    peak. Every room is cut round them (`_pieces_clear_of`) before it is scored, so the order and the scale-before-
    place rule are E65's own; only the last resort can still land on one, and the row loop refuses that by name
    (`stamp_clash_error`). Absent or empty, every room is the room it always was, to the byte."""
    boxes = LPG.page_boxes(page, aspect)
    stage_w = boxes["stage"]["w"]
    want = round(DOCK_ON_PAGE_W * stage_w)
    quiet = boxes.get("quiet_zone")
    floor_h = _floor_h(aspect)
    taken = [t for t in (clear_of or []) if isinstance(t, dict)]

    def cut(rooms: list[dict]) -> list[dict]:
        return [p for r in rooms for p in _pieces_clear_of(r, taken)] if taken else rooms

    # (1) OUTSIDE: a band the page's ink leaves free - E45 §1, unchanged
    best = None
    for band in cut(free_bands(boxes, reserve)):   # P52 T6: `reserve` keeps the card out of a newsreel band's strip
        room_w, room_h = band["w"] - 2 * DOCK_PLACE_PAD, band["h"] - 2 * DOCK_PLACE_PAD
        width = max(DOCK_ON_PAGE_MIN_W, min(want, room_w, _card_w_for(room_h)))
        if width > band["w"] - 2 or dock_card_h(width) > band["h"] - 2:
            continue                       # even the floor card does not fit this band
        key = (width, band["band"] == quiet, -DOCK_BAND_ORDER.index(band["band"]))
        if best is None or key > best[0]:
            best = (key, band, width)
    if best is not None:
        _, band, width = best
        height = dock_card_h(width)
        if band["band"] in ("left", "right"):   # a side column: hug the page's margin, centre vertically
            x = band["x"] + DOCK_PLACE_PAD if band["band"] == "left" else band["x"] + band["w"] - DOCK_PLACE_PAD - width
            y = band["y"] + (band["h"] - height) / 2
        else:                                   # a horizontal band: park against the plot, quiet-zone end
            x = band["x"] + DOCK_PLACE_PAD if quiet == "left" else band["x"] + band["w"] - DOCK_PLACE_PAD - width
            y = band["y"] + band["h"] - DOCK_PLACE_PAD - height if band["band"] == "above" else band["y"] + DOCK_PLACE_PAD
        x = min(max(x, band["x"]), band["x"] + band["w"] - width)
        y = min(max(y, band["y"]), band["y"] + band["h"] - height)
        return {"x": round(x), "y": round(y), "w": width, "h": height, "room": "outside"}
    plot = boxes["plot"]
    centre = (plot["x"] + plot["w"] / 2, plot["y"] + plot["h"] / 2)
    # (2) EMPTY: the largest rectangle the data does not touch, the quiet side first
    cands = []
    for room in cut(mask_rooms(boxes)):
        fit = _fit_in(room, want, floor_h)
        if fit is None:
            continue
        w, h = fit
        box = _clear_of_axis(_corner_box(room, w, h, quiet, centre), room, boxes)
        room_cx = room["x"] + room["w"] / 2
        on_quiet = 1 if (quiet == "right" and room_cx >= centre[0]) or (quiet == "left" and room_cx <= centre[0]) else 0
        corner = abs(room_cx - centre[0]) + abs(room["y"] + room["h"] / 2 - centre[1])
        ax = (boxes.get("axis") or {}).get("x")
        over_axis = bool(ax and box["y"] + box["h"] > ax["y"])   # allowed (E65), still second best: a card that
        cands.append(((on_quiet, w * (0.9 if over_axis else 1.0), corner), box))   # keeps the labels legible wins a near tie
    if cands:
        return {**max(cands, key=lambda c: c[0])[1], "room": "empty"}
    # (3) AXIS: underneath, over the x tick labels - never on the data
    under = axis_room(boxes)
    for piece in (cut([under]) if under else []):
        fit = _fit_in(piece, want, floor_h)
        if fit:
            w, h = fit
            box = _corner_box(piece, w, h, quiet, centre)
            if mask_is_clear(boxes, box):
                return {**box, "room": "axis"}
    # (4) THE CORNER, at the floor - and the build warns (the caller reads `room`)
    corner = emptiest_corner(boxes)
    w = _card_w_for(floor_h)
    h = dock_card_h(w)
    held = [p for p in cut([corner]) if p["w"] >= w and p["h"] >= h]   # P69 T5: the corner's clear pieces, the largest first
    if held:
        corner = max(held, key=lambda p: p["w"] * p["h"])
    return {**_corner_box(corner, w, h, quiet, centre), "room": "corner"}


def dock_place(world: dict, aspect: str | None, reserve: list[dict] | None = None,
               clear_of: list[dict] | None = None) -> dict | None:
    """The placement every dock on this scene takes, or None on a plain plate (E45: "a dock on a
    plain plate keeps the solo card"). One rectangle per scene, from the page's geometry alone -
    and on a ledger page there is ALWAYS one (E65); the rectangle carries the `room` it came from.
    `clear_of`: the row's stamps' fitted boxes, which the card is placed round (P69 T5, `page_place`)."""
    if not isinstance(world, dict) or world.get("kind") != SPECIES_LEDGER or not world.get("page"):
        return None
    return page_place(world["page"], aspect or "16:9", reserve, clear_of)


# ---- R26-20 (2026-09-22): A STAMP IS INK ON THE PAGE - THE MARK TAKES THE ROOM, THE RING HUGS THE MARK ----------
# Three rounds on the record. (1) The parent's frame read: the ring ran through the "+613%" end name while the mark sat
# clear of it - the ring and the approach are ink too (R26-191: a collision is fixed before a card, never named).
# (2) The reviewer: through the real row loop the fit was blind to the end names and fitted a box the engine did not
# draw - one door (`stamp_dock_place`), every stamp, the page's measured names, one fitted box. (3) THE OPERATOR, on
# the committed goldens: *"if the ring is going to be that big the image should be stamped bigger, we're just wasting
# space. The fed reads small. Use the space. ... There's no reason a bigger prop needs a sparser chart. look how much
# room is inside of the stamp."* The fit's PRIORITY was backwards - it protected the ring (a 1.6x floor of our own) and
# shrank the mark to make it fit. Now:
#   THE MARK FIRST: the largest mark at the picture's own aspect the page holds - measured by its PAINTED pixels (the
#     cutout's alpha box), turned through the whole arrival's rotation, at rest AND coming down from its approach -
#     searched over EVERY free place on the page (the plot's empty area, the bands round it), chosen by painted area.
#   THE RING YIELDS: its peak is the largest the room allows up to the source's 2x, down to a floor just OUTSIDE the
#     mark's painted edge (its painted half-diagonal + STAMP_RING_GAP_PX); that floor is reserved when the mark is
#     sized, so the ring can never be refused. The 1.6x floor and the mark-shrink step are DELETED.
#   The only refusal left: a place too small for the mark at a legible size (STAMP_MARK_FLOOR_PX, painted).
# Only a dock that arrives by `stamp` is fitted, so every other build compiles byte-for-byte what it was.
STAMP_FROM = 2.1           # kinetics/stopaction.mjs STAMP_ARRIVAL.FROM (badge-stamp.tsx:88-91): the scale the mark comes DOWN from - its hull at that scale is ink on the page too
STAMP_RING_TO = 2.0        # kinetics/stopaction.mjs STAMP_ARRIVAL.RING_TO (badge-stamp.tsx:156) - one dial written twice; test_the_stamp_arrival holds the pair
STAMP_RING_W_PX = 4.8      # ... STAMP_ARRIVAL.RING_W_PX, the stroke at its widest (life 0) - counted OUTSIDE the radius, which over-counts (the engine draws it inside)
STAMP_RING_GAP_PX = 12     # the ring's FLOOR: this far outside the mark's painted half-diagonal, before the stroke. 12 px is 2.5 stroke widths - the least page between a mark's corner and the ring at which the ring reads as its own line rather than a border drawn on the mark (the operator's "just outside the painted edge"; ~4 CSS px on a 360 px phone)
STAMP_APPROACH_MIN = 1.2   # the least the approach may be capped to: the source comes down from 2.1x and the DESCENT is the weight cue (the clamped scale spring); at 1.2x the mark still falls a tenth of its size on each side, the least that reads as coming down onto the page rather than fading in [DERIVED, a dial]
STAMP_TURN_RANGE = (-11.6, 7.0)   # degrees the mark turns through over its arrival: it starts at LAND_DEG + WIND_DEG = +7 and the FREE spring overshoots its -9 landing to -11.58 (stopaction-stamp.test.mjs); the mark is fitted at every angle in it
STAMP_MARK_FLOOR_PX = 120  # the least a stamped mark's PAINTED long side may be [DERIVED: three quarters of the agenda page's drawn stamp, ~159 px at rest - below it a prop stops reading as an object]. Against painted pixels it still holds: every one of the 24 cutouts is trimmed to its alpha box with a 1 px margin (measured 2026-09-22), so painted and canvas differ by 2 px
STAMP_SEARCH_PX = (16, 4)  # the centre is searched on a 16 px grid over every free place, then on a 4 px grid round the best
STAMP_ALPHA_MIN = 8        # a pixel is PAINTED above this alpha (of 255) - the cutouts' anti-aliased fringe starts at 1


# THE FRAME'S OWN BANDS where no page reports them (a picture plate): the ledger page's `safe` and `caption_anchor`,
# which `page_boxes` documents as "the frame's own bands" - the same rectangles on every page of an aspect, so a stamp
# on a plate is held to exactly what a stamp on a page is. test_the_stamp_arrival pins the two against page_boxes.
FRAME_BANDS = {
    "16:9": {"safe": {"x": 64, "y": 64, "w": 1792, "h": 814}, "caption": {"x": 145, "y": 878, "w": 1630, "h": 82}},
}


def ring_obstacles(page: dict | None, aspect: str | None, extra: list[dict] | None = None) -> tuple[list[dict], dict]:
    """(everything a stamp may not cross, the bounds it must stay inside), in stage px. ValueError when it cannot
    be known - a stamp is never fitted blind (R26-20 send-back #2).

    On a LEDGER PAGE: the title, the sub, the source line, the badge rail, both axis bands, every INK cell of the
    page's data mask (the plot itself when the page has no mask), the anchored caption's band, and the page's INLINE
    END NAMES - which `page_boxes` measures as its `tags` box on a full-stage 16:9 page (R26-205; the compiler stamps
    every 16:9 row full-stage, `stamp_full_stage`). A page that WRITES end names (`ledger_page.tag_units` > 0) but
    reports no box for them is REFUSED by name: the first cut fitted such a page silently and its ring ran through
    all four names. Unlike `free_bands`, the title and the sub are obstacles: E45 lets a CARD park over a heading
    once read, but a ring through it is a mark drawn through its words. The bounds are the safe box.
    Anywhere else (a picture plate): the frame's own caption band and `extra`, inside the frame's safe box.
    `extra` is a band the caller measured and the boxes do not carry (a newsreel strip)."""
    if not page:
        bands = FRAME_BANDS.get(aspect or "16:9")
        if bands is None:
            raise ValueError(f"a stamp off a ledger page at {aspect}: the frame's safe box and caption band are not "
                             "recorded for this aspect (FRAME_BANDS) - its ring cannot be fitted")
        return [bands["caption"], *(extra or [])], dict(bands["safe"])
    boxes = LPG.page_boxes(page, aspect or "16:9")
    if not boxes.get(LPG.TAGS_KEY) and LPG.tag_units(page) > 0:
        raise ValueError(f"this page writes inline end names (tag_units {LPG.tag_units(page):g}) but reports no "
                         f"measured `{LPG.TAGS_KEY}` box (R26-205 measures one on a full-stage 16:9 page) - a stamp's "
                         "ring cannot be fitted blind against names it cannot see")
    out = [boxes[k] for k in ("title", "sub", "source", "rail", "caption_anchor")
           if isinstance(boxes.get(k), dict) and boxes[k].get("w", 0) > 0 and boxes[k].get("h", 0) > 0]
    axis = boxes.get("axis") or {}
    out += [axis[k] for k in ("x", "y") if isinstance(axis.get(k), dict)]
    if boxes.get(LPG.TAGS_KEY):
        out.append(boxes[LPG.TAGS_KEY])
    plot, mask = boxes["plot"], boxes.get("data_mask")
    # THE BASIS LABEL (`axes.ylabel`, "index - 100 = Aug 2025, log scale"): `page_boxes` folds it into `plot`'s own top
    # ("plot is the DATA box plus the ink that lives inside it - the basis label above it"), so it has no box of its
    # own and the data mask does not carry it. It is written in the tick labels' own `lab` face, so it is taken as the
    # plot's top strip, one tick-label line high (the page's measured `axis.x` height), across the plot's width -
    # measured on the served full-stage page 2026-09-22: the label at (151, 208, 435 x 33) inside that strip
    # (151, 208, 947 x 36). Without it the send-back #2 fit put the ring straight through it.
    if (page.get("axes") or {}).get("ylabel"):
        out.append({"x": plot["x"], "y": plot["y"], "w": plot["w"], "h": (axis.get("x") or {}).get("h") or 36})
    if mask:
        rows, cols = len(mask), len(mask[0])
        cw, ch = plot["w"] / cols, plot["h"] / rows
        out += [{"x": plot["x"] + c * cw, "y": plot["y"] + r * ch, "w": cw, "h": ch}
                for r in range(rows) for c in range(cols) if mask[r][c] == "1"]
    else:
        out.append(plot)
    return out + list(extra or []), boxes["safe"]


def disc_clearance(cx: float, cy: float, obstacles: list[dict], bounds: dict) -> float:
    """The radius of the largest DISC centred on (cx, cy) that touches no obstacle and stays inside the bounds: the
    Euclidean distance to the nearest obstacle rectangle, and to the bounds' edges. This is the ring's own test - over
    its life the stroke SWEEPS every radius from the mark out to its peak, so the whole peak disc (the mark aside) must
    be clear, and a disc is exact where a square would over-count its corners."""
    d = min(cx - bounds["x"], bounds["x"] + bounds["w"] - cx, cy - bounds["y"], bounds["y"] + bounds["h"] - cy)
    for o in obstacles:
        dx = max(o["x"] - cx, 0.0, cx - (o["x"] + o["w"]))
        dy = max(o["y"] - cy, 0.0, cy - (o["y"] + o["h"]))
        d = min(d, math.hypot(dx, dy))
    return d


def rect_scale(cx: float, cy: float, hx: float, hy: float, obstacles: list[dict], bounds: dict) -> float:
    """The largest k for which the axis-aligned box of half-extents (k hx, k hy) centred on (cx, cy) touches no obstacle
    and stays inside the bounds. Closed form: a box collides with a rectangle only when it overlaps it on BOTH axes, so
    each obstacle allows k up to max(dx / hx, dy / hy)."""
    k = min((cx - bounds["x"]) / hx, (bounds["x"] + bounds["w"] - cx) / hx,
            (cy - bounds["y"]) / hy, (bounds["y"] + bounds["h"] - cy) / hy)
    for o in obstacles:
        dx = max(o["x"] - cx, 0.0, cx - (o["x"] + o["w"]))
        dy = max(o["y"] - cy, 0.0, cy - (o["y"] + o["h"]))
        k = min(k, max(dx / hx, dy / hy))
    return k


def turned_half_extents(w: float, h: float, turns: tuple[float, float] = STAMP_TURN_RANGE) -> tuple[float, float]:
    """The half-extents of a w x h box's axis-aligned hull over EVERY angle it turns through (sampled each 0.25 deg)."""
    lo, hi = turns
    n = max(1, int((hi - lo) / 0.25))
    hx = hy = 0.0
    for i in range(n + 1):
        t = math.radians(lo + (hi - lo) * i / n)
        c, sn = abs(math.cos(t)), abs(math.sin(t))
        hx, hy = max(hx, w / 2 * c + h / 2 * sn), max(hy, w / 2 * sn + h / 2 * c)
    return hx, hy


_PAINTED: dict = {}


def painted_box(src: Path | None, card_aspect: float | None = None) -> dict:
    """What a mark PAINTS, as fractions of its own canvas plus the canvas aspect: ``{aspect, x0, y0, x1, y1}``.

    A PROP's picture is measured by its alpha (STAMP_ALPHA_MIN) - the ring's radius and every overlap test use the
    painted extent, not the file's canvas. A card (no picture to read, or a framed document) paints its whole box, at
    `card_aspect` or the dock card's own shape."""
    if src is not None:
        key = str(src)
        if key not in _PAINTED:
            from PIL import Image
            with Image.open(src) as im:
                im = im.convert("RGBA")
                W, H = im.size
                bb = im.getchannel("A").point(lambda v: 255 if v > STAMP_ALPHA_MIN else 0).getbbox() or (0, 0, W, H)
            _PAINTED[key] = {"aspect": H / W, "x0": bb[0] / W, "y0": bb[1] / H, "x1": bb[2] / W, "y1": bb[3] / H,
                             "canvas": [W, H], "painted": [bb[2] - bb[0], bb[3] - bb[1]]}
        return dict(_PAINTED[key])
    a = card_aspect or dock_card_h(1000) / 1000
    return {"aspect": a, "x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 1.0}


def _floor4(v: float) -> float:
    """Round DOWN to 4 places - a fitted peak written to the timeline can never be larger than the one fitted (L3)."""
    return math.floor(v * 1e4) / 1e4


def _stamp_scale(cx: float, cy: float, pw: float, ph: float, obstacles: list[dict], bounds: dict) -> float:
    """The largest PAINTED size (as a multiple of pw x ph) a mark centred on (cx, cy) may take: its turned hull clear
    at its least approach (STAMP_APPROACH_MIN, which contains it at rest), and the ring's floor disc - the painted
    half-diagonal + STAMP_RING_GAP_PX + the stroke - clear, so the ring can always be drawn."""
    hx, hy = turned_half_extents(pw, ph)
    k_mark = rect_scale(cx, cy, hx * STAMP_APPROACH_MIN, hy * STAMP_APPROACH_MIN, obstacles, bounds)
    k_ring = (disc_clearance(cx, cy, obstacles, bounds) - STAMP_RING_GAP_PX - STAMP_RING_W_PX) / (0.5 * math.hypot(pw, ph))
    return min(k_mark, k_ring)


def stamp_fit(cx: float, cy: float, k: float, paint: dict, obstacles: list[dict], bounds: dict) -> dict:
    """The stamp at painted scale `k` about the painted centre (cx, cy), written as the engine draws it: the CANVAS box
    (rounded), the painted fractions, and the ring and approach fitted to what the room leaves AT THAT ROUNDED BOX -
    `ring_to` = min(2, disc / painted half-diagonal), `from_to` = min(2.1, what the turned hull allows). Both rounded
    DOWN (L3). Pure."""
    fw, fh = paint["x1"] - paint["x0"], paint["y1"] - paint["y0"]
    cw = k / fw                                   # canvas px per unit width: painted width = k, canvas width = k / fw
    W, H = cw, cw * paint["aspect"]
    box = {"x": round(cx - W * (paint["x0"] + fw / 2)), "y": round(cy - H * (paint["y0"] + fh / 2)),
           "w": round(W), "h": round(H)}
    pcx = box["x"] + box["w"] * (paint["x0"] + fw / 2)          # the drawn painted centre and size, off the rounded box
    pcy = box["y"] + box["h"] * (paint["y0"] + fh / 2)
    pw, ph = box["w"] * fw, box["h"] * fh
    rp = 0.5 * math.hypot(pw, ph)
    hx, hy = turned_half_extents(pw, ph)
    ring = _floor4(min(STAMP_RING_TO, (disc_clearance(pcx, pcy, obstacles, bounds) - STAMP_RING_W_PX) / rp))
    frm = _floor4(min(STAMP_FROM, rect_scale(pcx, pcy, hx, hy, obstacles, bounds)))
    return {**box, "paint": [round(paint["x0"], 4), round(paint["y0"], 4), round(paint["x1"], 4), round(paint["y1"], 4)],
            "painted": [round(pw, 1), round(ph, 1)], "centre": [round(pcx, 1), round(pcy, 1)],
            "ring_to": ring, "ring_capped": ring < STAMP_RING_TO - 1e-9, "ring_floor": _floor4((rp + STAMP_RING_GAP_PX) / rp),
            "from_to": frm, "from_capped": frm < STAMP_FROM - 1e-9}


def _stamp_room_name(cx: float, cy: float, page: dict | None, aspect: str | None) -> str:
    """Which of the page's places the chosen centre stands in: E65's `empty` room inside the plot, else the free band
    (`free_bands`) it lies in - named on the entry for the record, never used to decide."""
    if not page:
        return "plate"
    boxes = LPG.page_boxes(page, aspect or "16:9")
    pl = boxes["plot"]
    if pl["x"] <= cx <= pl["x"] + pl["w"] and pl["y"] <= cy <= pl["y"] + pl["h"]:
        return "empty"
    for b in free_bands(boxes):
        if b["x"] <= cx <= b["x"] + b["w"] and b["y"] <= cy <= b["y"] + b["h"]:
            return b["band"]
    return "outside"


def stamp_dock_place(world: dict | None, aspect: str | None, dopt: dict, paint: dict | float | None,
                     plate_room: dict | None = None, reserve: list[dict] | None = None, where: str = "stamp",
                     clear_of: list[dict] | None = None) -> dict:
    """WHERE A STAMP LANDS AND HOW BIG: the door every `arrive: stamp` dock goes through (the row loop calls it before
    the slot rule; R26-20). THE MARK TAKES THE ROOM, THE RING HUGS THE MARK (the operator's round):

    ONE BOX FOR THE WHOLE ARRIVAL: the entry is written `centre: True` - the engine's own "box from the first frame"
    switch (`dockGeom`) - and `read` / `read_s` / `park_s` / `centre_band` are refused on a stamp, so the fitted, rung
    and landed rect is one rect.
    WHERE: the row's own centre (`centre_x` / `centre_y`) when it names one; else EVERY free place the world offers -
    on a ledger page the whole safe box against its ink (the plot's empty area, the bands round it: E65's rooms, all of
    them at once), on a picture plate its declared `room` - searched for the centre that holds the LARGEST PAINTED
    MARK (`_stamp_scale`), the page's own E65 answer breaking a tie. A plate stamp with neither room nor centre is
    refused by name.
    SIZE: the largest the place holds (`centre_w` caps it when the row names one). Refused only when that largest is
    under STAMP_MARK_FLOOR_PX on its painted long side.
    `paint`: the mark's painted box (`painted_box`), or a bare aspect for a framed card. Returns `stamp_fit` + `room`
    + `why`; ValueError names the row.
    `clear_of` (P69 T5): the row's EARLIER stamps' fitted boxes (`stamp_reserved_box`) - obstacles to this mark and its
    ring like the page's own ink, and cut out of E65's tie-break room too. Absent, the fit is what it always was."""
    sw, sh = (1080, 1920) if (aspect or "16:9") == "9:16" else (1920, 1080)
    page = (world or {}).get("page") if (world or {}).get("kind") == SPECIES_LEDGER else None
    if not isinstance(paint, dict):
        paint = painted_box(None, paint)
    taken = [t for t in (clear_of or []) if isinstance(t, dict)]
    try:
        obs, bounds = ring_obstacles(page, aspect, list(reserve or []) + taken if taken else reserve)
    except ValueError as exc:
        raise ValueError(f"{where}: {exc}") from None
    if not page and plate_room:   # a picture plate's declared room IS where a card may stand: the mark and its ring stay inside it
        x0, y0 = max(bounds["x"], plate_room["x"]), max(bounds["y"], plate_room["y"])
        x1 = min(bounds["x"] + bounds["w"], plate_room["x"] + plate_room["w"])
        y1 = min(bounds["y"] + bounds["h"], plate_room["y"] + plate_room["h"])
        bounds = {"x": x0, "y": y0, "w": max(0, x1 - x0), "h": max(0, y1 - y0)}
    unit = (1.0, paint["aspect"] * (paint["y1"] - paint["y0"]) / (paint["x1"] - paint["x0"]))   # painted w : h
    cap = (dopt.get("centre_w") or 0) * sw * (paint["x1"] - paint["x0"]) or math.inf               # a named width caps it
    if dopt.get("centre_x") is not None or dopt.get("centre_y") is not None:
        cx = dopt["centre_x"] * sw if dopt.get("centre_x") is not None else sw / 2
        cy = dopt["centre_y"] * sh if dopt.get("centre_y") is not None else sh / 2
        k = _stamp_scale(cx, cy, *unit, obs, bounds)
    else:
        region = bounds if (page or plate_room) else None
        if not region:
            raise ValueError(f"{where}: a stamp on a picture plate needs the plate's `room` or the row's own "
                             "centre_x / centre_y - there is nowhere to fit it")
        e65 = dock_place(world, aspect, reserve, taken) if page else region
        ecx, ecy = e65["x"] + e65["w"] / 2, e65["y"] + e65["h"] / 2
        best = None
        coarse, fine = STAMP_SEARCH_PX
        pts = [(gx, gy) for gx in range(int(region["x"]), int(region["x"] + region["w"]) + 1, coarse)
               for gy in range(int(region["y"]), int(region["y"] + region["h"]) + 1, coarse)]
        for _pass in (0, 1):
            for gx, gy in pts:
                key = (min(_stamp_scale(gx, gy, *unit, obs, bounds), cap), -math.hypot(gx - ecx, gy - ecy))
                if best is None or key > best[0]:
                    best = (key, gx, gy)
            pts = [(best[1] + dx, best[2] + dy) for dx in range(-coarse, coarse + 1, fine) for dy in range(-coarse, coarse + 1, fine)]
        (k, _tie), cx, cy = best
    k = min(k, cap)
    long_side = max(k, k * unit[1])
    if long_side < STAMP_MARK_FLOOR_PX:
        raise ValueError(f"{where}: the largest mark this {'place' if page else 'room'} holds at ({cx:.0f}, {cy:.0f}) paints "
                         f"{long_side:.0f} px on its long side, under the {STAMP_MARK_FLOOR_PX} px mark floor - name "
                         "another room for it (R26-191: a collision is fixed, never shipped)")
    fit = None
    for _ in range(12):   # L3: the ROUNDED box must still hold the mark; step down a pixel until it does
        fit = stamp_fit(cx, cy, k, paint, obs, bounds)
        pw, ph = fit["painted"]
        if (_stamp_scale(fit["centre"][0], fit["centre"][1], pw, ph, obs, bounds) >= 1.0
                and fit["from_to"] >= STAMP_APPROACH_MIN and fit["ring_to"] >= fit["ring_floor"]):
            break
        k -= 1.0
    fw = fit["painted"][0]
    why = (f"mark {fit['painted'][0]:.0f}x{fit['painted'][1]:.0f} painted px ({100 * fw / sw:.1f}% of the stage width); "
           f"ring {'capped at ' + format(fit['ring_to'], '.2f') + 'x by the room' if fit['ring_capped'] else 'reaches 2.00x'}"
           f" (floor {fit['ring_floor']:.2f}x, just outside the painted edge); "
           f"approach {'capped ' + format(STAMP_FROM, '.2f') + 'x -> ' + format(fit['from_to'], '.2f') + 'x' if fit['from_capped'] else 'from 2.10x'}")
    return {**fit, "room": "authored" if (dopt.get("centre_x") is not None or dopt.get("centre_y") is not None)
            else _stamp_room_name(cx, cy, page, aspect), "why": why}


# ---- P69 T5 (R26-247 L2; E99 s88 (3)): THE STAMP TAKES THE ROOM FIRST; THE ROW'S OTHER DOCKS GO ROUND IT ----------
# The R26-20 review's L2: a scene's OTHER dock was no obstacle to a stamp - two stamps, or a stamp and a card, were
# fitted independently, so on the golden page the card's E65 room and the stamp's biggest-mark room were the same
# corner of the plot (measured before this row: 41 605 px^2 of card over the turned mark, the ring 159.5 px into it).
# s88 (3) says the room chosen is the one that gives the biggest MARK, so the order is: the row's stamps first, in row
# order, each fitted round the earlier ones' boxes; then the row's other docks, placed by E65 round every stamp.
def stamp_reserved_box(fit: dict) -> dict:
    """The rectangle a fitted stamp takes on the page, in whole stage px: its canvas box and the square round the
    ring's widest disc (the fitted peak plus the stroke), which holds the turned mark at rest as well. Pure."""
    cx, cy = fit["centre"]
    r = fit["ring_to"] * 0.5 * math.hypot(*fit["painted"]) + STAMP_RING_W_PX
    x0, y0 = math.floor(min(fit["x"], cx - r)), math.floor(min(fit["y"], cy - r))
    x1, y1 = math.ceil(max(fit["x"] + fit["w"], cx + r)), math.ceil(max(fit["y"] + fit["h"], cy + r))
    return {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}


def row_stamp_fits(world: dict | None, aspect: str | None, docks: list[tuple[str, dict, dict]],
                   plate_room: dict | None, reserve: list[dict] | None, where: str) -> tuple[dict, list[dict]]:
    """Every STAMP in a row, fitted before any other dock is placed: ({index in the row: its `stamp_dock_place` fit},
    [their `stamp_reserved_box`es, in row order]). `docks` is the row's (aid, dock options, painted box) in row order;
    each stamp is fitted `clear_of` the earlier stamps' boxes, so the first takes the room exactly as it would alone.
    ValueError (from the door) names the row and the dock."""
    fits, taken = {}, []
    for n, (aid, dopt, paint) in enumerate(docks):
        if dopt.get("arrive") != "stamp":
            continue
        fits[n] = stamp_dock_place(world, aspect, dopt, paint, plate_room, reserve, f"{where} dock {aid}", taken)
        taken = [*taken, stamp_reserved_box(fits[n])]
    return fits, taken


def stamp_clash_error(where: str, box: dict | None, stamps: list[dict]) -> str | None:
    """Why a row's OTHER dock may not ship beside its stamps, or None: its parked box touches a stamp's fitted box (an
    authored box, or E65's last resort), or it has no box the compiler can measure (a paired slot's template layout,
    the solo card on a plain plate). A row with no stamp is never refused here."""
    if not stamps:
        return None
    if not isinstance(box, dict):
        return (f"{where}: shares the row with a stamp but is parked by the template's own slot, which the compiler "
                "cannot measure against the stamp's mark and ring - put it on slot 0, or name its box "
                "(centre_x / centre_y), or the plate's room (P69 T5)")
    for s in stamps:
        if box["x"] < s["x"] + s["w"] and s["x"] < box["x"] + box["w"] and box["y"] < s["y"] + s["h"] and s["y"] < box["y"] + box["h"]:
            return (f"{where}: its box [{box['x']}, {box['y']}, {box['w']}, {box['h']}] lands over a stamp's mark or "
                    f"ring [{s['x']}, {s['y']}, {s['w']}, {s['h']}] - the stamp takes the room first; move the card "
                    "(R26-191: a collision is fixed, never shipped)")
    return None

# ---- R26-221: A CARD TAKES AN AUTHORED SLOT ON A PICTURE PLATE (2026-09-18, the Steel and Paper H unit) ----
# `dock_place` answers None for a plate - E45's "a dock on a plain plate keeps the solo card" - and that one answer
# was also swallowing the ROW's own box: `centre / centre_w / centre_x / centre_y / read / read_s / park_s` are all
# gated behind `place`, so the unit's solo card on the studio plate landed at the template's `.dock.solo` rectangle
# ([758, 167, 1068, 515] on a 1920x1080 stage), straight across the host's face, and "never over the host" could
# only be obeyed by docking nothing at all.
#
# THE PLAYER NEEDS NOTHING. `dockGeom` and `dockReadRect` read `d.place` and `d.read_place` for any world, and the
# `camera-layers` / `dock-depth` goldens have handed a hand-written place to a card on a PLATE since P58 T3
# (`build_golden_sources.py` CAMERA_LAYERS_PLACE = {"x": 1160, "y": 600, "w": 640, "h": 400}). The shut door is the
# compiler's alone - which is why this row moves no engine line, no mirrored module and no golden pixel.
#
# TWO WAYS A CARD IS PLACED ON A PLATE:
#   (a) THE ROW'S OWN BOX - the same fields a page row takes (E99 s80: a card takes the outgoing card's box, and the
#       H unit's page rows are authored exactly this way): `centre_x` / `centre_y` place the card's CENTRE as a
#       fraction of the stage, `centre_w` its width, `card_aspect` its shape; `centre: True` alone is the stage's
#       own centre. One function decides it for a page and for a plate - `centred_place` with no page - so the two
#       can never drift apart.
#   (b) THE PLATE'S DECLARED ROOM - `;room=x,y,w,h` (`plate_room_spec`), the plate's answer to a page's quiet zone:
#       the card takes the reading width the room holds, centred in it, with `DOCK_PLACE_PAD` of air on every side
#       through `_fit_in` - the same fitter `page_place` uses on a page's free band. The host plates were generated
#       with a clear third for exactly this.
# The row's own box outranks the declared room (the author has named the slot; the room is where the compiler is
# asked to find one), and a row that authors neither on a plate that declares neither gets None - E45's solo card,
# to the byte.
PLATE_PLACE_FIELDS = ("centre", "centre_x", "centre_y", "centre_w")   # the dock fields that SAY "place this card";
                              # `card_aspect` is the shape of a box, never the reason for one, so it triggers nothing
PLATE_PLACE_POINT = ("centre", "centre_x", "centre_y")   # ... and the ones that say WHERE, which is what outranks a
                              # plate's declared room (E99 s80: the author names the slot). `centre_w` and
                              # `card_aspect` SIZE a card rather than place one, so a room honours them inside itself
PLATE_BOX_PLACED = "plate-box"     # `place_room` on the entry: the ROW named the box
PLATE_ROOM_PLACED = "plate-room"   # ... the PLATE declared the room and the card was fitted into it


def plate_room_px(room: list | None, aspect: str | None) -> dict | None:
    """A plate's declared room (four fractions, `plate_room_spec`) as a rectangle in stage px, or None."""
    if not room:
        return None
    sw, sh = LPG.STAGE_PX.get(aspect or "16:9", LPG.STAGE_PX["16:9"])
    x, y, w, h = (float(v) for v in room)
    return {"x": round(x * sw), "y": round(y * sh), "w": round(w * sw), "h": round(h * sh)}


def plate_dock_place(room: dict | None, aspect: str | None, dopt: dict, where: str = "dock") -> dict | None:
    """The parked rectangle for a card on a PICTURE PLATE, in stage px, or None when nothing placed it (R26-221).

    `{"x", "y", "w", "h", "room"}` - `room` is which of the two placed it (`plate-box` | `plate-room`), the way a
    page's card records which of E65's four rooms it took. ValueError when the plate's declared room cannot hold a
    legible card: a room that has been named and cannot be used is an authoring fault, not a silent fall-back (the
    same call `;drift=` under E49's floor makes). Pure: nothing is mutated.

    THE ORDER, pinned: a row that names WHERE - `centre`, `centre_x`, `centre_y` (`PLATE_PLACE_POINT`) - outranks
    the plate's declared room, INCLUDING a bare `centre: True`, which is the stage's own centre and not the room's.
    E99 s80: the author names the slot, and a room is where the compiler is asked to FIND one. `centre_w` and
    `card_aspect` name no place - they SIZE a card - so on a room-declaring plate they are honoured inside the room,
    and on a plate without one they size the stage-centred box."""
    authored = any(dopt.get(k) is not None for k in PLATE_PLACE_FIELDS)
    if not room and not authored:
        return None
    card_aspect = dopt.get("card_aspect")
    named_place = any(dopt.get(k) is not None for k in PLATE_PLACE_POINT)
    if not room or named_place:
        # the row placed the card itself: the page's own door, with no page - `centred_place` falls through to the
        # stage's centre for a `centre: True` that names no point, which is what a picture plate's centre is
        box = centred_place(None, aspect, card_aspect, None, dopt.get("centre_w"), None,
                            dopt.get("centre_y"), dopt.get("centre_x"))
        return {**box, "room": PLATE_BOX_PLACED}
    sw = LPG.STAGE_PX.get(aspect or "16:9", LPG.STAGE_PX["16:9"])[0]
    want = round(float(dopt.get("centre_w") or DOCK_ON_PAGE_W) * sw)
    fit = _fit_in(room, want, _floor_h(aspect), card_aspect)
    if fit is None:
        raise ValueError(f"{where}: the plate's declared room [{room['x']}, {room['y']}, {room['w']}, {room['h']}] "
                         f"cannot hold a card {want} px wide at the legibility floor ({_floor_h(aspect)} px tall, "
                         f"{DOCK_PLACE_PAD} px of air on every side) - widen `;room=`, or name a smaller "
                         "`centre_w` on the dock (R26-221)")
    w, h = fit
    return {"x": round(room["x"] + (room["w"] - w) / 2), "y": round(room["y"] + (room["h"] - h) / 2),
            "w": w, "h": h, "room": PLATE_ROOM_PLACED}


def centred_place(place: dict, aspect: str | None, card_aspect: float | None = None, page: dict | None = None,
                  centre_w: float | None = None, band_name: str | None = None, centre_y: float | None = None,
                  centre_x: float | None = None, reserve: list[dict] | None = None) -> dict:
    """The same card at the READING width, centred - horizontally on the stage, vertically in the page's own FREE space.

    The third watch asked for a centred dock ("center dock then retract the host on that chart page"); the macro-chart intake
    found the cost of centring on the STAGE instead of the PAGE - a two-tier chart occupies the upper half, so a stage-centred
    card lands on the plot. The card is centred in the tallest band the page's ink leaves (`free_bands`: below the plot, or
    the foot), and falls back to the caption-band centre only when the page reports no room."""
    sw, sh = (1080, 1920) if (aspect or "16:9") == "9:16" else (1920, 1080)
    w = round((centre_w or CENTRE_W) * sw); h = round(w * card_aspect) if card_aspect else dock_card_h(w)   # the READING width unless the row names a smaller card
    if h > CENTRE_MAX_H * sh:
        h = round(CENTRE_MAX_H * sh); w = round(h / card_aspect) if card_aspect else w
    if centre_y is not None or centre_x is not None:   # the row places the card itself: page_boxes models a page's bands, and
        # on a portrait page with a tall chart its model and the player's layout disagree (R26-27) - an author may name it
        cx = centre_x * sw if centre_x is not None else sw / 2
        cy = centre_y * sh if centre_y is not None else sh / 2
        return {"x": round(max(0, cx - w / 2)), "y": round(max(0, cy - h / 2)), "w": w, "h": h}
    # P53 T7 / R26-59: the newsreel band's strip is RESERVED here too - a centred card (the head above the crawl is one)
    # may not be centred in a band that runs through the crawl; `dock_place` already honoured it, this door did not
    bands = [bd for bd in free_bands(LPG.page_boxes(page, aspect or "16:9"), reserve) if page and bd["band"] in ("below", "foot", "above")] if page else []
    if band_name:   # the row names the band itself (the sixth watch: the cup belongs between the source line and the caption)
        bands = [bd for bd in bands if bd["band"] == band_name]
    room = max(bands, key=lambda bd: bd["h"], default=None)
    floor_h = _floor_h(aspect)
    if room and room["h"] >= max(40, floor_h):
        if h > room["h"]:                                     # a tall card shrinks to the band rather than covering the page
            h = round(room["h"]); w = round(h / card_aspect) if card_aspect else w
        return {"x": round((sw - w) / 2), "y": round(room["y"] + (room["h"] - h) / 2), "w": w, "h": h}
    # E65: no band outside the plot is tall enough to read a card in - take the page's own room
    # (the plot's empty rectangle, the axis band, the corner) rather than the stage's middle, which
    # is the chart. The card keeps the centred WIDTH it can, and the room decides where it sits.
    if page:
        got = page_place(page, aspect or "16:9", reserve)
        if got.get("room") != "corner" or not room:
            gw = min(w, got["w"]) if card_aspect else got["w"]
            gh = round(gw * card_aspect) if card_aspect else dock_card_h(gw)
            return {"x": got["x"], "y": got["y"], "w": gw, "h": gh}
    band = CENTRE_BAND * sh if (aspect or "16:9") == "9:16" else sh   # portrait: the caption strip is below the band
    return {"x": round((sw - w) / 2), "y": round(max(0, (band - h) / 2)), "w": w, "h": h}


# ---- A CARD NEVER READS OVER A LEDGER PAGE'S PLOT (ruling E63, widened 2026-09-11) ------------
# The operator, on the Tokyo cut at 0:09.5-0:10.5: *"docking over the plate while it's drawing is not
# a good standard practice, it's somewhat okay here because of timing, but as a rule we should
# probably use better handling now that we can manipulate scale/depth/placement easier."* The panel
# card enters on its word at 9.09, pops to reading size (its solo CSS box, which the probe reads at
# 801x474) over the middle of the plot, and the line the page is still drawing - `build_to` at 7.69
# for 3.0 s, landing on datum 311 at 10.69 - runs on UNDERNEATH it. E45 s1 already forbids a card
# PARKED on the plot and M25 scores it; this is the other half of the choreography, the READ.
#
# THE QUALIFIER IS DROPPED (the operator, the third self-watch, the same evening). E63 as first wired
# moved the read only WHILE THE CHART WAS DRAWING. The cut's build beat was then re-fitted to the mount
# clock - the line lands at 7.49 and the panel card enters at 9.1 - so the rule stopped firing and the
# pop came back centred over the FINISHED chart at 9.5-11.0: *"im confused, because you just left the
# dock over the chart now too. something went backwards."* So: a card never READS over a ledger page's
# plot, drawing or finished. The drawing windows are still compiled and still stamped on the scene
# (`build_windows`) - they are what lets the entry and the gate SAY whether the chart was drawing at
# the time - but they no longer decide anything. E45's PARK is untouched: a parked card on the page is
# E45's contract and M25's row; only the READ moves.
#
# THE RULE. The word is never moved - the card still enters when the sentence says so - the READ is:
#   (a) the reading box is re-placed in a free band the page leaves (`free_bands`): `above`, across
#       the title exactly as E45 parks a card there, then `below`, then the `foot`; at the reading
#       scale when the band holds it, else at the widest scale that does, and never narrower than the
#       card's own parked width (E45's floor - below it the card is not evidence any more);
#   (b) when no band holds even that, the read is DEFERRED: the card enters at its PARKED place and
#       never pops (`read_deferred`, which the player already renders - a card with `centre` and no
#       reading box takes its box from its first frame).
# The entry records the decision so the build report and the gate can say what happened. A dock whose
# read is already clear of the plot is untouched, and so is a dock on a plain plate - every row without
# the case compiles to exactly the bytes it did before.
DOCK_READ_CSS = {   # the template's `.dock.solo` geometry, mirrored (the box `dockReadRect` measures when nothing is forced):
    "9:16": {"x": 80, "y": 553, "w": 800},     # html[data-aspect="9:16"] #dock-1.solo { width: 800px; left: 80px; top: 553px }
    "16:9": {"x": 764, "y": 172, "w": 1056},   # #dock-1.solo { width: 1056px; top: 172px } + .side-r (side-l is its mirror at 100)
}
READ_BAND_ORDER = ("above", "below", "foot")   # the read moves the way E45's card parks: over the title first
READ_OVER_PLOT_SHARE = 0.05   # the read MEETS the plot at this share of the smaller box - M27's own line, so the gate and the compiler agree
READ_PLOT_PAD = 48            # ... and the air the MOVED read keeps from the plot on a page placed by ESTIMATE: `ledger_page`'s
                              # model of the Tokyo page puts the plot 24 px below where the player draws it (P50 T16), and the
                              # camera's push moves the page under a card that does not move with it (+3 px at zoom 1.06). Both,
                              # doubled. A band that cannot give the card this much air has not got room for a read, and the read
                              # is DEFERRED instead - which is what the Tokyo page's 208 px band does.
READ_PLOT_PAD_MEASURED = DOCK_PLACE_PAD   # ... and on a page the fixture HAS measured the estimate's error is gone: the player's
                              # own boxes, with the card's usual clear air for the camera's push (E45's own pad).


def dock_read_box(aspect: str | None, read_place: dict | None = None, card_aspect: float | None = None) -> dict:
    """The rectangle a placed card READS at, in stage pixels.

    The row's own `read_place` when it named one (`dock_opts`'s `read`), else the card's solo CSS
    geometry with its height from `dock_card_h` - which the probe confirms to the pixel: the Tokyo
    panel card reads at [79, 552, 801, 474] against this box's [80, 553, 800, 474]."""
    if read_place:
        return {k: read_place[k] for k in ("x", "y", "w", "h")}
    css = DOCK_READ_CSS.get(aspect or "16:9", DOCK_READ_CSS["16:9"])
    h = round(css["w"] * card_aspect) if card_aspect else dock_card_h(css["w"])
    return {"x": css["x"], "y": css["y"], "w": css["w"], "h": h}


def _overlap_share(a: dict, b: dict) -> float:
    """The area two rectangles share, as a share of the SMALLER of them (the probe's own measure)."""
    w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    h = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    if w <= 0 or h <= 0:
        return 0.0
    return (w * h) / max(1.0, min(a["w"] * a["h"], b["w"] * b["h"]))


def page_build_windows(world: dict | None, species: list[dict] | None, scene_start: float) -> list[tuple[float, float]]:
    """Every stretch in which this scene's chart is DRAWING - (from, to) in build seconds, empty when
    the scene is not a ledger page or its chart never draws.

    Two sources, and they are separate windows rather than one span: the page's own clock, dated by the
    motion gate's `MG._page_land_offset` (the roll-out, the mount, the morph, a page that arrives
    built), and each `build_to`, which draws the line to a datum on its own word. Tokyo s02 declares
    two caps - 7.69 + 3.0 and 18.95 + 1.2 - and between them the line RESTS on its cap (M19's hold):
    a card that reads in the gap is reading beside a finished chart, not over a build."""
    if not isinstance(world, dict) or world.get("kind") != SPECIES_LEDGER or not world.get("page"):
        return []
    out: list[tuple[float, float]] = []
    land = float(scene_start) + MG._page_land_offset({"world": world})
    if land > float(scene_start) + 1e-6:
        out.append((float(scene_start), land))
    out += [(float(sp["at"]), float(sp["at"]) + float(sp.get("dur") or 0.0))
            for sp in (species or []) if sp.get("kind") == "build_to" and float(sp.get("dur") or 0.0) > 0]
    return sorted(out)


def _read_card_h(w: float, card_aspect: float | None) -> int:
    """A card of width `w` is this tall: the row's own aspect when it named one, else the card's own
    build - a 16:9 slide frame plus the chrome (`dock_card_h`), which does NOT scale with the width."""
    return round(w * card_aspect) if card_aspect else dock_card_h(round(w))


def _read_fit(band: dict, box: dict, floor_w: float, aspect: str | None, card_aspect: float | None,
              plot: dict | None, pad_plot: float = READ_PLOT_PAD) -> dict | None:
    """`box` re-placed inside `band` at the same width if it fits, else the widest that does.

    None when the band cannot hold the card at its parked width - E45's floor, under which the card
    stops being evidence - or when what fits would still crowd the plot. Centred on the stage
    horizontally (clamped into the band) and in the band vertically, so the card reads where the eye
    already is and the park is a short slide away."""
    pad = DOCK_PLACE_PAD
    room_w, room_h = band["w"] - 2 * pad, band["h"] - 2 * pad
    w = min(float(box["w"]), room_w,
            (room_h / card_aspect) if card_aspect else float(_card_w_for(room_h)))
    if w < max(floor_w, DOCK_ON_PAGE_MIN_W) - 0.5:
        return None
    w = round(w)
    h = _read_card_h(w, card_aspect)
    if h > room_h:
        return None
    sw = 1080 if (aspect or "16:9") == "9:16" else 1920
    x = min(max(round((sw - w) / 2), band["x"] + pad), band["x"] + band["w"] - pad - w)
    fit = {"x": round(x), "y": round(band["y"] + (band["h"] - h) / 2), "w": w, "h": h}
    return fit if not plot or _overlap_share(fit, _grown(plot, pad_plot)) <= 0 else None


def _grown(box: dict, pad: float) -> dict:
    """`box` with `pad` of clear air on every side."""
    return {"x": box["x"] - pad, "y": box["y"] - pad, "w": box["w"] + 2 * pad, "h": box["h"] + 2 * pad}


def read_over_build(place: dict | None, read_box: dict | None, page: dict | None, aspect: str | None,
                    read_from: float, read_to: float, windows: list[tuple[float, float]] | None,
                    card_aspect: float | None = None) -> dict | None:
    """E63's decision for one placed dock: where its READ goes, or None when there is nothing to move.

    Returns ``{"read_place": {...}, "read_moved": {"from": [...], "to": [...], "why": "..."}}`` when a
    band holds the card, ``{"read_deferred": True}`` when none does, and None when the dock is not on a
    ledger page, has no reading pop at all (a centred card takes its parked box from its first frame),
    or reads clear of the plot. The chart's state does NOT enter the decision (the widening): a read on
    the plot moves whether the line is drawing or finished. `windows` stays for the RECORD only - it is
    what lets `why` say the read fell while the chart was drawing. Pure: nothing is mutated."""
    if not place or not read_box or not page:
        return None
    boxes = LPG.page_boxes(page, aspect or "16:9")
    plot = boxes.get("plot")
    if not plot or _overlap_share(read_box, plot) <= READ_OVER_PLOT_SHARE:
        return None                                   # the card already reads clear of the plot
    hit = [(a, b) for a, b in (windows or []) if read_from < b - 1e-6 and read_to > a + 1e-6]
    why = "a card never reads over the plot (E63)"
    if hit:                                           # the record, never the reason: which it was, for the report and the gate
        why += f" - while the chart draws, until {max(b for _a, b in hit):.2f}s"
    bands = {bd["band"]: bd for bd in free_bands(boxes)}
    for name in READ_BAND_ORDER:
        band = bands.get(name)
        if band is None:
            continue
        moved = _read_fit(band, read_box, float(place["w"]), aspect, card_aspect, plot,
                          READ_PLOT_PAD_MEASURED if boxes.get("measured") else READ_PLOT_PAD)
        if moved is None:
            continue
        return {"read_place": moved,
                "read_moved": {"from": [read_box["x"], read_box["y"], read_box["w"], read_box["h"]],
                               "to": [moved["x"], moved["y"], moved["w"], moved["h"]], "why": why}}
    # E65: no band outside the plot holds the read - take the room the PARK took, enlarged toward the
    # axis (the card may overlap the tick labels, never the data), at the reading scale or scaled down
    # to the legibility floor. The park is the corner the card adjusts up into afterwards.
    moved = read_in_room(boxes, place, read_box, aspect, card_aspect)
    if moved:
        return {"read_place": moved,
                "read_moved": {"from": [read_box["x"], read_box["y"], read_box["w"], read_box["h"]],
                               "to": [moved["x"], moved["y"], moved["w"], moved["h"]],
                               "why": why + " - E65: the plot's own empty room"}}
    return {"read_deferred": True}


def read_in_room(boxes: dict, place: dict, read_box: dict, aspect: str | None,
                 card_aspect: float | None = None) -> dict | None:
    """E65's READ: the parked card's own room, grown toward the axis, at the reading scale.

    The room is the largest rectangle the data does not touch that CONTAINS the park (so the read and
    the park are one move apart), grown down to the source line where the x tick labels are - they are
    furniture. The card takes the reading width if it fits, else the widest that does, never under the
    legibility floor, and never over a cell the data's ink is in. None when the page has no mask."""
    if not boxes.get("data_mask") or not place:
        return None
    floor_h = _floor_h(aspect)
    under = axis_room(boxes)
    rooms = mask_rooms(boxes)
    if under:
        rooms = rooms + [under]
    holds = [r for r in rooms
             if r["x"] - 1 <= place["x"] and r["y"] - 1 <= place["y"]
             and r["x"] + r["w"] + 1 >= place["x"] + place["w"] and r["y"] + r["h"] + 1 >= place["y"] + place["h"]]
    grown = []
    for r in (holds or rooms):
        room = dict(r)
        if under and abs(room["y"] + room["h"] - under["y"]) < 2:   # the room ends where the axis band starts: join them
            room["h"] = under["y"] + under["h"] - room["y"]
        grown.append(room)
    best = None
    for room in sorted(grown, key=lambda r: -(r["w"] * r["h"])):
        fit = _fit_in(room, float(read_box["w"]), floor_h, card_aspect)
        if fit is None:
            continue
        w, h = fit
        sw = 1080 if (aspect or "16:9") == "9:16" else 1920
        x = min(max(round((sw - w) / 2), room["x"] + DOCK_PLACE_PAD), room["x"] + room["w"] - DOCK_PLACE_PAD - w)
        box = {"x": round(x), "y": round(room["y"] + (room["h"] - h) / 2), "w": w, "h": h}
        box = _clear_of_axis(box, room, boxes)
        if not mask_is_clear(boxes, box):
            continue
        if best is None or w > best["w"]:
            best = box
    return best


# ---- THE CAPTION'S BAND UNDER A CARD (ruling E62, 2026-09-11) ---------------------------------
# "Under a card the caption keeps its size and MOVES; it shrinks only when no band fits." The
# demotion s9.25 #2 ruled on 2026-09-02 was a demotion in SIZE (64 px / 800 -> 33 px / 600), and the
# gate-1 read of the Tokyo cut caught what that costs: at 0:38, under the two-fingers card, "money
# went: a Treasury page," read 33 stage px = 12.1 CSS px on a phone. E62: the demotion is in
# POSITION. The compiler states, per dock, the band the PAGE leaves free of the card and of the data
# for a two-line strip at the stage size; the player puts the strip there and keeps `.stage`. Only
# when no band holds the strip does the caption fall back to the quiet anchor (48 px / 800 on a short).
#
# THE RULE. The strip is two lines at the stage size (a short's caption pages are cut to 25-28 chars
# a line at 64 px - build_caption_pages.py). The candidates are tried in this order:
#   1. `below` - the free band under the plot (the page's own room above its source line);
#   2. `above` - the free band over the plot (across the title, exactly as E45 parks a card there);
#   3. `quiet` - the strip's HOME, where the stage caption already sits when no card is up.
# A candidate wins when the strip fits inside it CLEAR of the plot's data box and clear of every card
# live in that dock's window by a margin of one line. None fits -> `caption_band: null`, and the
# player takes the quiet anchor. The bands come from `free_bands` / `page_boxes` - the measured
# fixture when the page is on file, `ledger_page`'s estimate when it is not (P50 T16) - so the
# caption is placed against the same one truth every card is placed against.
CAPTION_STAGE_PX = 64          # the stage caption's type, both aspects (the template's `#caption.stage`)
CAPTION_LINE_H = 1.12          # its line box (the template's `#caption.stage` line-height)
CAPTION_LINES = 2              # a caption page is cut to two lines on a short (build_caption_pages.py)
CAPTION_BAND_ORDER = ("below", "above", "quiet")
# R26-201: the page boxes a CAMERA moves - the page's own ink, and nothing the frame owns (`stage`, `safe`,
# `caption_anchor` are the stage's; `quiet_zone` / `measured` are words). `free_bands` reads both kinds, which is
# why the list is named rather than inferred: a transformed safe box would move the band's own walls with the page.
CAPTION_PAGE_INK_KEYS = ("title", "sub", "chart", "plot", "source", "rail", LPG.TAGS_KEY)
CAPTION_HOME_BOTTOM = 480      # 9:16: the strip sits on `bottom: 480px` (G-l, y 1297-1440)
CAPTION_HOME_TOP = 0.40        # 16:9: the stage caption's own 40% band
CAPTION_SIDE_PAD = 120         # the stage caption's near margin beside a declared quiet zone
CAPTION_QZ_SPLIT = 0.58        # ... and the far one, as a share of the stage width


def caption_strip_h() -> int:
    """The stage caption's own height: two lines at the stage size, in stage pixels."""
    return round(CAPTION_STAGE_PX * CAPTION_LINE_H * CAPTION_LINES)


def _caption_arrive() -> str | None:
    """P52 T10: the arrival a stage page's words take, or None for the pop.

    None and "pop" both mean the shipped behaviour and both write NOTHING: a build that does not ask
    compiles exactly the bytes it compiled before the slice. Anything else must be a named kind - a typo
    silently falling back to the pop is the failure mode this refuses (the same rule the kinetics kill
    switch has: an unknown flag turns nothing on, but here the build ASKED for a register and must get it)."""
    a = (CAPTION_ARRIVE or "").strip() or None
    if a is None or a == "pop":
        return None
    if a not in CAPTION_ARRIVALS:
        raise SystemExit(f"caption arrival {a!r} is not one of {CAPTION_ARRIVALS} (build_scene_timeline_f.CAPTION_ARRIVE)")
    return a


def _caption_life() -> str | None:
    """P57 T14 / E90: the LIFE a stage page's words carry, or None for the caption as it shipped.

    Unlike the arrival, "pop" is a REAL setting here and is written: it is the shipped pop made a notch stronger
    (E90 s2 "maybe add more pop effect"), so a build that asks for it must get it. Only silence means the base -
    and silence is what every build on disk says, which is the byte-identity of the goldens and of both approved
    shorts. An unknown setting is refused by name: a typo silently shipping the base is the failure mode this
    exists to stop (the same rule `_caption_arrive` has)."""
    a = (CAPTION_LIFE or "").strip() or None
    if a is None:
        return None
    if a not in CAPTION_LIVES:
        raise SystemExit(f"caption life {a!r} is not one of {CAPTION_LIVES} (build_scene_timeline_f.CAPTION_LIFE)")
    return a


def stage_px_w(aspect: str) -> int:
    return LPG.STAGE_PX[aspect][0]


def caption_strip_x(aspect: str, quiet_zone: str | None) -> tuple[int, int]:
    """(x, w) of the stage caption's box - the template's own left/right for this aspect and zone."""
    sw = stage_px_w(aspect)
    if aspect == "9:16":                       # `#caption.stage.onpage`: left 80, right 200 (the safe box)
        return 80, sw - 200 - 80
    if quiet_zone == "right":                  # the caption keeps the LEFT of the stage
        x = round(CAPTION_QZ_SPLIT * sw)
        return x, sw - CAPTION_SIDE_PAD - x
    if quiet_zone == "left":
        return CAPTION_SIDE_PAD, round(CAPTION_QZ_SPLIT * sw) - CAPTION_SIDE_PAD
    return 200, sw - 400                       # `#caption.stage`: left 200, right 200


def caption_home_y(aspect: str) -> int:
    """Where the stage caption sits with no card up - the third candidate, and the one to beat."""
    sh = LPG.STAGE_PX[aspect][1]
    if aspect == "9:16":
        return sh - CAPTION_HOME_BOTTOM - caption_strip_h()
    return round(CAPTION_HOME_TOP * sh)


def _rects_meet(a: dict, b: dict, pad: float = 0.0) -> bool:
    """Do these two rectangles meet, with `b` grown by `pad` on every side?"""
    return (a["x"] < b["x"] + b["w"] + pad and a["x"] + a["w"] > b["x"] - pad
            and a["y"] < b["y"] + b["h"] + pad and a["y"] + a["h"] > b["y"] - pad)


def caption_band(page: dict, aspect: str, cards: list[dict] | None, xf=None) -> dict | None:
    """The band this page leaves free for the caption under `cards` (E62), or None.

    ``{"y", "h", "band"}`` in stage pixels - the strip's own rectangle and the candidate it came
    from. `cards` is every card box live in the dock's window (its parked `place`, and the reading
    box when the row named one); None means a card whose box the compiler does not know, and the
    answer is None - the caption takes the quiet anchor rather than guess. Pure: nothing is mutated.

    R26-201 / E99 s80 (3): `xf` is the CAMERA, as a map from a page box to where the frame puts it -
    the caption is the viewer's layer and never rides the camera (E59), so under a move the page's ink
    is somewhere else and the band has to be cut against WHAT THE FRAME HOLDS. Absent (every caller
    before that row) nothing is transformed and the bytes are the bytes. The STAGE, the safe box and
    the anchored strip are never mapped: they are the frame's own, not the page's."""
    if cards is None:
        return None
    boxes = LPG.page_boxes(page, aspect)
    if xf is not None:
        boxes = {**boxes, **{k: xf(boxes[k]) for k in CAPTION_PAGE_INK_KEYS if isinstance(boxes.get(k), dict)}}
    h = caption_strip_h()
    x, w = caption_strip_x(aspect, boxes.get("quiet_zone"))
    margin = round(CAPTION_STAGE_PX * CAPTION_LINE_H)         # one line of clear air beside a card
    stage = boxes["stage"]
    # the strip clears the page's DATA and the page's own INK. `free_bands` hands E45's card the
    # title and the sub ("over the title", the card being opaque and the heading read); a caption is
    # white type with a shadow, so a strip on the title is two texts in one place - it is not free.
    ink = [boxes[k] for k in ("plot", "title", "sub", "source", "rail") if boxes.get(k) and boxes[k]["h"] > 0]
    bands = {bd["band"]: bd for bd in free_bands(boxes)}
    for name in CAPTION_BAND_ORDER:
        if name == "quiet":
            ys = [caption_home_y(aspect)]
        else:
            bd = bands.get(name)
            if bd is None or bd["h"] < h:
                continue
            top, bottom = bd["y"], bd["y"] + bd["h"] - h      # flush to the band's two edges ...
            ys = [bottom, top] if name == "above" else [top, bottom]   # ... the edge by the plot first (E45's park)
            for c in cards:                                   # ... then flush above and below each card
                ys += [c["y"] - margin - h, c["y"] + c["h"] + margin]
            ys = [y for y in ys if bd["y"] <= y <= bd["y"] + bd["h"] - h]
        for y in ys:
            strip = {"x": x, "y": round(y), "w": w, "h": h}
            if strip["y"] < 0 or strip["y"] + h > stage["h"]:
                continue
            if any(_rects_meet(strip, b) for b in ink):       # never over the data or the page's ink
                continue
            if any(_rects_meet(strip, c, margin) for c in cards):
                continue
            return {"y": strip["y"], "h": h, "band": name}
    return None


# ---- THE STRIP LAW: the caption's E62 band and the NEWSREEL band (P52 T6, gate 1) -------------
# On a short the caption's strip and a newsreel band want the same bottom strip. The compiler REFUSES a row
# where the two boxes meet and names both, with the two ways out; it does not silently move either, because
# which one gives way is the operator's call on the frame, not the compiler's:
#   (1) the DEFAULT this slice ships - the caption keeps its E62 band (its home on a short) and the band goes
#       BELOW it (`y >= caption home + strip h`); or the band goes entirely ABOVE the caption's home;
#   (2) `cap_band: "above"` on the newsreel row - the crawl takes the caption's own strip and the caption is
#       stamped one strip HIGHER, above the crawl (`newsreel_caption_band`).
# On 16:9 there is no clash to rule: the caption sits at 40 % (432-575) and a band's region is in the lower
# 40 % (>= 648), so every landscape row takes (1) without saying anything.
NEWSREEL_STRIP_PAD = 8   # the air between the two strips: a pixel of contact is not "the same strip", 8 px is


def newsreel_region_box(entry: dict, aspect: str | None) -> dict | None:
    """The band's own rectangle in STAGE pixels, from the region the author declared (0..1 fractions)."""
    tgt = (entry or {}).get("target") or {}
    if tgt.get("kind") != "region":
        return None
    sw, sh = LPG.STAGE_PX[aspect or "16:9"]
    try:
        x0, y0, x1, y1 = (float(tgt[k]) for k in ("x0", "y0", "x1", "y1"))
    except (KeyError, TypeError, ValueError):
        return None
    return {"x": round(x0 * sw), "y": round(y0 * sh), "w": round((x1 - x0) * sw), "h": round((y1 - y0) * sh)}


def newsreel_rows(row_species) -> list[dict]:
    """Every newsreel row in this shot row's species list (usually one; two is a second band, not a second line)."""
    return [e for e in (row_species or []) if isinstance(e, dict) and e.get("kind") == SPECIES_NEWSREEL]


def newsreel_boxes(row_species, aspect: str | None) -> list[dict]:
    """The bands' rectangles - what a card may not cover (handed to the placer as one more reserved strip)."""
    return [b for b in (newsreel_region_box(e, aspect) for e in newsreel_rows(row_species)) if b]


def caption_home_box(aspect: str | None) -> dict:
    """The caption strip's HOME rectangle in stage pixels - the box the band has to be reconciled with."""
    asp = aspect or "16:9"
    x, w = caption_strip_x(asp, None)
    return {"x": x, "y": caption_home_y(asp), "w": w, "h": caption_strip_h()}


def newsreel_strip_clash(entry: dict, aspect: str | None) -> tuple[dict, dict] | None:
    """(the band's box, the caption's home box) when the two want the same strip, else None."""
    band = newsreel_region_box(entry, aspect)
    if band is None:
        return None
    home = caption_home_box(aspect)
    if band["y"] >= home["y"] + home["h"] - NEWSREEL_STRIP_PAD:      # the band is BELOW the caption's strip (the default)
        return None
    if band["y"] + band["h"] <= home["y"] + NEWSREEL_STRIP_PAD:      # ... or entirely above it
        return None
    return band, home


def validate_newsreel_strip(row_species, aspect: str | None, row_docks: bool | None = None) -> list[str]:
    """The strip law as a pure check on one row (gate 1). Returns the errors; the caller names the row.

    `row_docks` is whether this row docks anything at all: today the player moves the caption's strip only
    under a CARD (E62's band is written on the dock entry, and the engine reads it there), so a row that asks
    for `cap_band: "above"` with nothing docked above the band is refused rather than shipped with the caption
    sitting on the crawl. That is also the composition the operator described - the band runs UNDER a surface."""
    errs: list[str] = []
    for e in newsreel_rows(row_species):
        above = e.get("cap_band") == NEWSREEL_CAP_ABOVE
        clash = newsreel_strip_clash(e, aspect)
        if clash and not above:
            band, home = clash
            errs.append(
                f"newsreel: the band's region [{band['y']}-{band['y'] + band['h']}] and the caption's E62 strip "
                f"[{home['y']}-{home['y'] + home['h']}] want the same strip on {aspect or '16:9'}. Two ways out: move the "
                f"band's region BELOW the caption's home (y0 >= {round((home['y'] + home['h']) / LPG.STAGE_PX[aspect or '16:9'][1], 4)}) "
                f"or above it, or give the caption its band above the crawl with cap_band: \"{NEWSREEL_CAP_ABOVE}\"")
        if above and not clash:
            errs.append(f'newsreel: cap_band "{NEWSREEL_CAP_ABOVE}" moves the caption above a crawl that is already clear of '
                        "its strip - drop it, the default places the band below the caption's own band")
        if above and row_docks is False:
            errs.append(f'newsreel: cap_band "{NEWSREEL_CAP_ABOVE}" needs a surface docked above the band - the caption\'s strip '
                        "moves under a CARD (E62 writes the band on the dock entry). Dock the head or the clip, or let the band "
                        "sit below the caption's home")
    return errs


def newsreel_caption_band(band: dict | None, row_species, aspect: str | None,
                          enter: float, exitt: float) -> dict | None:
    """Where the caption's strip goes when a crawl is live in this dock's window (P52 T6).

    `cap_band: "above"` is the operator's alternative: the crawl owns the caption's own strip, so the caption
    is stamped one strip higher - ABOVE the crawl, clear of it by `NEWSREEL_STRIP_PAD`. Every other row keeps
    whatever E62 gave it (`band`), which is what every timeline compiled before this slice carries."""
    h = caption_strip_h()
    for e in newsreel_rows(row_species):
        if e.get("cap_band") != NEWSREEL_CAP_ABOVE:
            continue
        at, dur = float(e.get("at", 0.0)), float(e.get("dur", 0.0))
        if at >= exitt or at + dur <= enter:          # the band is not up in this card's window
            continue
        box = newsreel_region_box(e, aspect)
        if box is None:
            continue
        y = box["y"] - NEWSREEL_STRIP_PAD - h
        if y < 0:
            continue                                   # no room above the crawl: the row keeps E62's answer
        return {"y": int(y), "h": h, "band": "newsreel-above"}
    # ... and when a crawl is up and E62 found no band at all, the caption may NOT fall back to the quiet
    # ANCHOR: that strip is the bottom of the frame, which is where the crawl is. It takes its own HOME
    # (the stage band) whenever the home is clear of every live band; only if even that is covered does the
    # row keep None, and then the strip law's refusal above has already named the two boxes.
    if band is None:
        live = [b for b in (newsreel_region_box(e, aspect) for e in newsreel_rows(row_species)
                            if float(e.get("at", 0.0)) < exitt and float(e.get("at", 0.0)) + float(e.get("dur", 0.0)) > enter) if b]
        if live:
            home = caption_home_box(aspect)
            if all(home["y"] + h + NEWSREEL_STRIP_PAD <= b["y"] or home["y"] >= b["y"] + b["h"] + NEWSREEL_STRIP_PAD for b in live):
                return {"y": home["y"], "h": h, "band": "quiet"}
    return band


def dock_card_boxes(docks: list[dict], enter: float, exitt: float) -> list[dict] | None:
    """Every card box on stage during [enter, exit), or None when one of them is not on the timeline.

    A dock's box is its parked `place` plus the reading box when the row named one (`read_place`);
    a dock with neither - a card on its solo CSS geometry - is a box the compiler cannot state, and
    the caller then writes no band at all. The window is read against EVERY dock on the scene, so a
    band that clears this card also clears the ones beside it and the strip does not dance when the
    second card enters."""
    boxes: list[dict] = []
    for d in docks:
        if d["exit"] <= enter or d["enter"] >= exitt:
            continue
        if not d.get("place"):
            return None
        boxes.append(dict(d["place"]))
        if d.get("read_place"):
            boxes.append(dict(d["read_place"]))
    return boxes


def _caption_in_window(pages: list[dict], enter: float, exitt: float) -> bool:
    """Is a caption page on screen at any point of this dock's window? (E62 writes a band only then.)"""
    return any(pg["s"] < exitt and pg.get("e", pg["s"]) >= enter for pg in pages)


def stamp_caption_bands(scenes: list[dict], pages: list[dict], aspect: str | None) -> int:
    """E62: write `caption_band` onto every dock entry whose window carries a caption. In place.

    Returns how many entries took a band (the rest are stamped `null` and keep the quiet anchor).
    A dock on a plain plate has no page to read bands off, so it is stamped `null` too - which is
    exactly the behaviour every build had before this rule."""
    asp = aspect or "16:9"
    placed = 0
    for sc in scenes:
        world = sc.get("world")
        page = world.get("page") if isinstance(world, dict) and world.get("kind") == SPECIES_LEDGER else None
        for d in sc.get("docks", []):
            if not _caption_in_window(pages, d["enter"], d["exit"]):
                continue
            # R26-205: a FULL-STAGE page's caption is pinned to the anchored strip (`page.caption`), so there
            # is no band to choose - E62 moves a STAGE caption out of a card's way, and this one never held the
            # stage. Stamped `null` like a dock on a plain plate, which is what the engine already reads as
            # "keep the anchor".
            band = (caption_band(page, asp, dock_card_boxes(sc.get("docks", []), d["enter"], d["exit"]))
                    if page and not page_is_full_stage(world, asp) else None)
            band = newsreel_caption_band(band, sc.get("species"), asp, d["enter"], d["exit"])   # P52 T6: a crawl in this window may own the strip
            d["caption_band"] = band
            placed += bool(band)
    return placed


# ---- R26-201: THE CAPTION YIELDS UNDER A CAMERA MOVE (E62 for the camera; E99 s80 (3)) ---------
# Tokyo v3's two punches were DROPPED because of this hole: E62's demotion is written on DOCK entries
# only (`stamp_caption_bands`, `_dock_live_at`), so a page punch had no way to move the caption and the
# page's own cite and pill row were pushed into the strip - measured at 34 px and 23 px deep at zoom
# 1.08, with the shipped cut already touching it by 2 px at zoom 1.00. The operator, E99 s80: *"the
# CAPTION YIELDS under a camera move as it yields under a card (E62: the demotion is in position, not
# size) so no page element lands in the strip"*.
#
# THE MECHANISM IS E62's, UNCHANGED - the below / above / quiet ladder off `free_bands`, the strip two
# lines at the stage size, the first candidate that holds clear wins, `null` meaning "keep the anchor".
# ONE thing is new: the page's ink is read WHERE THE FRAME PUTS IT. The caption is the viewer's layer and
# never rides the camera (E59), so under a zoom of s about `look`, landed at `at`, a page box is
# `at + s * (p - look)` - the camera's own similarity (`kinetics/camera.mjs`), and `caption_band`'s `xf`.
# The band is cut at the move's DEEPEST zoom and held for the whole window: a band that moved with the
# zoom would be a caption sliding under a camera, which is exactly what E62 refused ("a layout move on
# the dock's enter clock, no transition").
#
# WHOSE CAPTION YIELDS: a caption that HOLDS THE STAGE. A 16:9 page row's caption is already in the
# anchored strip (R26-205), out of the plot and with nowhere to go, so at that aspect the rule is the
# page's instead - `page_crop_line_ceiling` refuses a zoom whose crop line lands in the strip, and
# `page_zoom_ceiling` refuses one that cuts a glyph. A 9:16 page's stage caption is the one that moves.
CAPTION_YIELD_KEY = "caption_yield"
# the three camera SPECIES' own zooms, mirrored from `kinetics/camera.mjs` CAM so the compiler can read the
# frame a species will draw (test_camera_zoom_and_caption_yield pins the three against the module itself)
CAMERA_SPECIES_ZOOM = {"punch": 1.14, "focus_zoom": FOCUS_ZOOM_DEFAULT, "pull_back": 1.9}


def camera_move_windows(scene: dict, aspect: str) -> list[dict]:
    """Every window of this scene in which the camera MAGNIFIES the world, with the deepest state in it.

    ``[{"from", "to", "zoom", "look", "at", "move"}]`` in timeline seconds and stage px. Keys: the window
    runs from the first key to the last, and on to the scene's end when the last key still holds a zoom
    (`camKeyState` holds after the last key). A species: its own `at` .. `at + dur`, at the zoom the
    engine draws it with - the authored `zoom` for a focus zoom, the engine's dial for the other two
    (a pull-back is deepest at its FIRST frame, which is where its look is read).

    A window whose look the compiler cannot place is left out - the same rule `camera_edge_errors` keeps."""
    sw, sh = LPG.STAGE_PX[aspect]
    page = (scene.get("world") or {}).get("page") if isinstance(scene.get("world"), dict) else None
    plot = None
    if isinstance(page, dict):
        try:
            plot = LPG.page_boxes(page, aspect).get("plot")
        except Exception:
            plot = None
    out: list[dict] = []
    keys = [k for k in ((scene.get("camera") or {}).get("keys") or []) if isinstance(k, dict)]
    if keys:
        deep = max(keys, key=lambda k: float(k.get("zoom", 1) or 1))
        if float(deep.get("zoom", 1) or 1) > 1.0:
            look = MG._cam_point(deep.get("look"), sw, sh, plot)
            at = MG._cam_point(deep.get("at"), sw, sh, plot) if deep.get("at") is not None else look
            end = float(keys[-1].get("t", 0.0))
            if float(keys[-1].get("zoom", 1) or 1) > 1.0:
                end = float((scene.get("span") or [0.0, end])[1])
            if look is not None and end > float(keys[0].get("t", 0.0)):
                out.append({"from": float(keys[0]["t"]), "to": end, "zoom": float(deep["zoom"]),
                            "look": look, "at": at or look, "move": f"camera keys (zoom {float(deep['zoom']):.4g})"})
    for e in scene.get("species", []):
        if not isinstance(e, dict) or e.get("kind") not in CAMERA_MOVES:
            continue
        z = e.get("zoom") if isinstance(e.get("zoom"), (int, float)) and not isinstance(e.get("zoom"), bool) \
            else CAMERA_SPECIES_ZOOM.get(e["kind"], 1.0)
        c = MG._cam_point(e.get("target"), sw, sh, plot)
        if c is None or not (float(z) > 1.0) or not isinstance(e.get("at"), (int, float)):
            continue
        out.append({"from": float(e["at"]), "to": float(e["at"]) + float(e.get("dur") or 0.0), "zoom": float(z),
                    "look": c, "at": c, "move": f"{e['kind']} (zoom {float(z):.4g})"})
    return [w for w in out if w["to"] > w["from"]]


def camera_frame_xf(win: dict):
    """The camera of `win` as a map from a page box to WHERE THE FRAME PUTS IT: `at + s * (p - look)`.

    Rounded to whole pixels because `page_boxes` is (`ledger_page._box`): the band ladder cuts its
    candidates flush to a box's edge and then asks whether they meet, so a fractional box makes a strip
    0.4 px into the plot and the caption falls to the anchor for a pixel it cannot see."""
    z = float(win["zoom"])
    lx, ly = float(win["look"][0]), float(win["look"][1])
    ax, ay = float(win["at"][0]), float(win["at"][1])
    return lambda b: LPG._box(ax + z * (b["x"] - lx), ay + z * (b["y"] - ly), b["w"] * z, b["h"] * z)


def camera_caption_band(page: dict, aspect: str, win: dict, cards: list[dict] | None) -> dict | None:
    """E62's band, cut against the page AS THE FRAME HOLDS IT under `win` (R26-201)."""
    return caption_band(page, aspect, cards if cards is not None else [], xf=camera_frame_xf(win))


def caption_live_box(band: dict | None, aspect: str) -> dict:
    """Where the caption's strip actually IS under this window - the band it took, or the quiet anchor."""
    x, y, w, h = LPG.CAPTION_ANCHOR[aspect]
    if band is None:
        return {"x": x, "y": y, "w": w, "h": h}
    bx, bw = caption_strip_x(aspect, None)
    return {"x": bx, "y": band["y"], "w": bw, "h": band["h"]}


def caption_strip_intrusion(page: dict, aspect: str, win: dict, band: dict | None) -> dict | None:
    """The page element that reads INSIDE the caption's strip under this move, and how deep (E99 s80 (3)).

    The yield is the door; this is what is left when the page has no band to give. A 9:16 page whose
    chart fills the frame leaves 44 px under its plot and 136 px over it - neither holds a two-line
    strip - so the caption stays at its anchor and the page's own cite is pushed into it (Tokyo,
    measured: 34 px at zoom 1.08). The compiler says so with the number; the ways out are the ruling's
    own - ANCHOR the move (a key's `at`, lifting the look so the foot clears) or PARK the page (E61) -
    and both are the author's, not the compiler's."""
    strip = caption_live_box(band, aspect)
    xf = camera_frame_xf(win)
    worst = None
    for name, box in page_glyph_boxes(page, aspect).items():
        b = xf(box)
        deep = min(b["y"] + b["h"], strip["y"] + strip["h"]) - max(b["y"], strip["y"])
        wide = min(b["x"] + b["w"], strip["x"] + strip["w"]) - max(b["x"], strip["x"])
        if deep <= 0 or wide <= 0:
            continue
        if worst is None or deep > worst["px"]:
            worst = {"element": name, "px": round(deep), "box": b}
    return worst


def page_caption_holds_the_stage(world: dict | None, aspect: str | None) -> bool:
    """Is this page's caption the one that HOLDS THE STAGE - the caption E62 moves rather than shrinks?

    False for an anchored caption (a 16:9 full-stage page row, R26-205, or a page that declares
    `caption: "anchor"` itself - a host plate's, C5): there is no band for it to take, the engine reads
    a null band as "keep the anchor", and at 16:9 the ceiling is the page's instead."""
    if not isinstance(world, dict) or world.get("kind") != SPECIES_LEDGER:
        return False
    page = world.get("page")
    if not isinstance(page, dict) or page.get("caption") == "anchor":
        return False
    return not page_is_full_stage(world, aspect)


def stamp_camera_caption_bands(scenes: list[dict], pages: list[dict], aspect: str | None) -> int:
    """R26-201: write `caption_yield` onto every page scene whose CAMERA moves under a caption. In place.

    One entry per camera window - `{from, to, caption_band, move}` - and the band is E62's own (`null`
    when no band holds a two-line strip clear of the page as the frame holds it, which the engine reads
    as the quiet anchor, exactly as it reads a card with no band). Returns how many windows took a band.

    Nothing is written where nothing yields: a plate row, an anchored caption, a window with no caption
    page on screen, a locked camera. A timeline compiled before this row carries no such key, so every
    committed golden and both approved shorts paint precisely what they painted."""
    asp = aspect or "16:9"
    if asp not in LPG.STAGE_PX:
        return 0
    placed = 0
    for sc in scenes:
        if not page_caption_holds_the_stage(sc.get("world"), asp):
            continue
        page = sc["world"]["page"]
        out = []
        for win in camera_move_windows(sc, asp):
            if not _caption_in_window(pages, win["from"], win["to"]):
                continue
            cards = dock_card_boxes(sc.get("docks", []), win["from"], win["to"])
            band = camera_caption_band(page, asp, win, cards)
            entry = {"from": round(win["from"], 2), "to": round(win["to"], 2),
                     "caption_band": band, "move": win["move"]}
            intruder = caption_strip_intrusion(page, asp, win, band)
            if intruder:   # the yield had no band to give: named with its number, never shipped in silence
                entry["in_strip"] = {"element": intruder["element"], "px": intruder["px"]}
            out.append(entry)
            placed += bool(band)
        if out:
            sc[CAPTION_YIELD_KEY] = out
    return placed


def page_is_measured(world: dict | None, aspect: str | None) -> bool:
    """True when the fixture holds the PLAYER's own boxes for this scene's page (P50 T16).

    `assets/page-boxes.v1.json` carries what `measure_page_boxes.py` read off the rendered page; a
    page whose ink is on file is placed against the player's numbers, a page that is not keeps
    `ledger_page`'s estimate of them. Everything that PLACES - `free_bands`, `page_place`,
    `centred_place` - reads the same `page_boxes`, so a scene is measured or estimated as a whole."""
    if not isinstance(world, dict) or world.get("kind") != SPECIES_LEDGER or not world.get("page"):
        return False
    return bool(LPG.page_boxes(world["page"], aspect or "16:9").get("measured"))


def solo_centre_by_clock(world: dict | None, aspect: str | None, n_docks: int, slot: int,
                         enter: float, scene_start: float, dopt: dict) -> bool:
    """R26-22: a SOLO card that arrives after the page's own clock has finished is CENTRED in the
    band the fixture says is free - not parked at the reading rect over the title.

    E50 dates a page by its last data mark: once the chart has landed the page is being read, not
    built, and the card is the thing to look at. `_page_land_offset` is the motion gate's own reading
    of that clock (the roll-out, the mount, a page that arrives built), so the compiler and the gate
    date the page the same way. Three conditions, and all three are the ruling's:

      * the card is ALONE on the scene - a pair keeps the layout its two slots declare (E45);
      * the page's chart has LANDED by the card's enter - before that the card would cover a build;
      * the page's bands are MEASURED - centring against an ESTIMATE of the bands is what put the tea
        cup on the chart in the sixth watch (R26-27), so a page the fixture has never seen keeps
        today's parked rectangle and the build says so.

    An authored `centre` (with or without `centre_y`) outranks all of it: it is handled by the caller
    and this returns False for it, so an authored row compiles to exactly the bytes it did before."""
    if n_docks != 1 or slot != 0 or dopt.get("centre") or dopt.get("press") or dopt.get("stack"):
        return False
    if not page_is_measured(world, aspect):
        return False
    land = float(scene_start) + MG._page_land_offset({"world": world})
    return float(enter) >= land - 1e-6


# ---- THE VERDICT STACK's payload and its host dock's WINDOW, from ONE set of times (P61 T7; doc 29 s9.24) --------
# s9.24's own lesson: "the stack's beat times lived in evidence-dock.json while its dock window, which carries the
# background dimming, lived in the shot table; a re-clock moved one and not the other and the dimming drifted 0.77 s
# from its content". `stack_entry` derives the window FROM the beats, so the two cannot shift separately.
# The dials mirror species/verdict.mjs - a module the compiler cannot import, so the three it needs are named here
# and `test_verdict_stack.py` pins them against the module's own frozen object.
STACK_FORMS = ("16:9", "9:16")   # which layout of the five phases: full-frame, or the SHORT's (VERDICT / VERDICT_9X16)
STACK_ENTER_LEAD = 0.5           # the host dock enters this long before the first proof's beat (verdict.mjs MOUNT_LEAD)
STACK_HOLD_AFTER = 1.0           # doc 29 s9.24: its window runs ~1 s past clear_at so the burst finishes ticking
STACK_RECEDE_LEAD = 0.9          # verdict.mjs LAST_RECEDE_LEAD - the last proof hands the focus back this early
STACK_BURST_STAGGER = 0.06       # verdict.mjs BURST_STAGGER - card i is thrown this long after card i-1
STACK_BURST_S = 0.5              # verdict.mjs BURST_S - each card's own throw


def stack_window(items: list[dict], clear_at: float) -> tuple[float, float]:
    """(enter, exit) for the stack's host dock - a lifecycle anchor whose window has to cover the whole choreography.

    It opens STACK_ENTER_LEAD before the first proof's beat (the stackbox mounts then) and closes once the LAST card's
    throw has finished: the stagger pushes card n-1's start to (n - 1) x STACK_BURST_STAGGER after clear_at, and each
    throw runs STACK_BURST_S - never less than doc 29's own ~1 s."""
    hold = max(STACK_HOLD_AFTER, (len(items) - 1) * STACK_BURST_STAGGER + STACK_BURST_S)
    return round(float(items[0]["at"]) - STACK_ENTER_LEAD, 2), round(float(clear_at) + hold, 2)


def stack_entry(items, clear_at: float, form: str | None = None,
                enter: float | None = None, exitt: float | None = None) -> tuple[dict, float, float]:
    """The `stack` evidence payload AND its host dock's window, derived from one set of times.

    ``items`` is [{id, at}] on the authoring clock, one per verbatim phrase, in the order they are spoken; ``clear_at``
    is the pivot line the wall bursts on. ``form`` names the layout when the stage cannot say it (the player defaults
    to the stage's own shape). An explicit ``enter`` / ``exitt`` is honoured but refused when it would cut the
    choreography: a window that opens after the first beat, or closes before the last card has been thrown.

    Returns (payload, enter, exit) - hand the last two straight to ``dock_entry``."""
    rows = [dict(it) for it in items]
    if len(rows) < 2:
        raise ValueError(f"stack: {len(rows)} item(s) - the verdict stack re-presents a LIST of proofs (2 or more)")
    for n, it in enumerate(rows, 1):
        if not it.get("id") or it.get("at") is None:
            raise ValueError(f"stack: item {n} needs an `id` (a document docked earlier) and an `at` (its verbatim beat)")
        it["at"] = round(float(it["at"]), 2)
    for a, b in zip(rows, rows[1:]):
        if b["at"] <= a["at"]:
            raise ValueError(f"stack: {b['id']} lands at {b['at']} s, not after {a['id']} at {a['at']} s - the cards "
                             "enter ONE AT A TIME, each on its own phrase (doc 29 s9.24)")
    clear_at = round(float(clear_at), 2)
    if clear_at < rows[-1]["at"] + STACK_RECEDE_LEAD:
        raise ValueError(f"stack: clear_at {clear_at} s is {round(clear_at - rows[-1]['at'], 2)} s after the last "
                         f"proof's beat ({rows[-1]['at']} s) - the last card holds the focus until "
                         f"clear_at - {STACK_RECEDE_LEAD} s, so it would never be read")
    if form is not None and form not in STACK_FORMS:
        raise ValueError(f"stack: form={form!r} is not one of {'|'.join(STACK_FORMS)}")
    want_enter, want_exit = stack_window(rows, clear_at)
    enter = want_enter if enter is None else round(float(enter), 2)
    exitt = want_exit if exitt is None else round(float(exitt), 2)
    if enter > rows[0]["at"]:
        raise ValueError(f"stack: the host dock enters at {enter} s, after the first proof's beat ({rows[0]['at']} s) - "
                         "the stack mounts with its dock, so the first card would be missed")
    if exitt < want_exit:
        raise ValueError(f"stack: the host dock leaves at {exitt} s, before the burst finishes at {want_exit} s "
                         f"({len(rows)} cards, {STACK_BURST_STAGGER} s apart, {STACK_BURST_S} s each) - doc 29 s9.24: "
                         "the window runs past clear_at so the burst finishes ticking")
    payload = {"items": [{"id": it["id"], "at": it["at"]} for it in rows], "clear_at": clear_at}
    if form is not None:
        payload["form"] = form
    return payload, enter, exitt


def dock_entry(aid: str, slot: int, enter: float, exitt: float, n_badges: int,
               kind: str = DOCK_KIND_IMAGE, place: dict | None = None, arrive: str | None = None, mass: str | None = None,
               centre: bool = False, read_place: dict | None = None, read_s: float | None = None, park_s: float | None = None,
               press: dict | None = None, stack: bool = False, behind: str | None = None, fg: str | None = None,
               prop: bool = False, ink: str | None = None, ring_to: float | None = None, from_to: float | None = None,
               paint: list | None = None,
               rid: str | None = None, read_moved: dict | None = None, read_deferred: bool = False,
               embed: dict | None = None, cutout: bool = False, depth: float | None = None) -> dict:
    """One dock on a compiled scene.

    Spans come from the dock: evidence enters before its claim and holds through the whole
    discussion. A flat hold drops the document mid-argument, which is what left 42% of claims
    naked. ``kind`` is written ONLY for a video dock - the motion gate credits a live video dock
    as continuous motion (M10 / M16) and an image dock's shape stays exactly as it was. ``place``
    is written ONLY for a dock on a ledger page (E45), so a plain-plate build compiles unchanged;
    with it come the two phases of the choreography - ``read_s`` at reading size, ``park_s`` for
    the shrink-and-slide - and ``park``, which is False when the dock's own span is too short to
    hold both (the card then simply stays at reading size for its whole life)."""
    span = round(exitt - enter, 2)
    rs, ps = (float(read_s) if read_s else DOCK_READ_S), (float(park_s) if park_s else DOCK_PARK_S)   # the dock's own clock, else the defaults
    room = place.get("room") if isinstance(place, dict) else None   # E65: which room the placer took
    place = {k: place[k] for k in ("x", "y", "w", "h")} if isinstance(place, dict) else place
    return {
        # P51 T5: the DERIVED row id - `<scene>.dock.<slide>` - the key a human or a flash agent edits this
        # card by in `<build>/overrides.json`. Written only when the compiler hands one down, so every other
        # caller's entry is byte-for-byte what it was.
        **({"id": rid} if rid else {}),
        "slide": aid, "slot": slot,
        # HF-17: the plate's foreground layer this card is behind, and the asset-map key it rides. Written ONLY when
        # the row asks, so every build that does not is byte-for-byte what it was.
        **({"behind": behind, "fg": fg} if behind and fg else {}),
        # P50 T7: the SURFACE this card lands on - its name, its four corners and the second the room dims. Written
        # ONLY when the row asks, so every build that does not is byte-for-byte what it was.
        **({EMBED_KEY: embed} if embed else {}),
        # P58 T6 (a): the PLANE this card stands on - the share of the camera's move it takes (kinetics/camera.mjs
        # PARALLAX). Written ONLY when the row asks, so every build that does not is byte-for-byte what it was.
        **({"depth": float(depth)} if depth else {}),
        "enter": round(enter, 2), "exit": round(exitt, 2),
        "badge_at": [round(enter + 0.75 + 1.3 * (n + 1), 2) for n in range(n_badges)],
        **({"kind": DOCK_KIND_VIDEO} if kind == DOCK_KIND_VIDEO else {}),
        # P53 T7 / R26-59: a CUTOUT dock - the card's chrome stands down. Written only when the row asks, so every
        # build that docks a document is byte-for-byte what it was.
        **({"kind": DOCK_KIND_CUTOUT} if cutout else {}),
        # R26-246 (b) / E99 s87: a PROP dock - the payload is art added to the world, bare, and `ink` says whether it
        # keeps its own colour. Written only when the row asks, so every build that docks a card is byte-for-byte what it was.
        **({"kind": DOCK_KIND_PROP} if prop else {}), **({"ink": ink} if (prop and ink) else {}),
        # R26-20 send-back: a STAMP's ring peak as the room allows it (stamp_ring_fit). Written only for a stamp that was
        # fitted, so every other entry is byte-for-byte what it was.
        **({"ring_to": ring_to} if (ring_to is not None and arrive == "stamp") else {}),
        **({"from_to": from_to} if (from_to is not None and arrive == "stamp") else {}),   # ... and its approach
        **({"paint": paint} if (paint is not None and arrive == "stamp") else {}),   # ... and the part of its box the mark PAINTS (fractions): the ring's centre, radius and the turn's pivot
        # P50 T3: a PRESS card carries its source line and its quoted phrase onto the stage; `_stack` is the
        # scene's own bookkeeping and is replaced by stack_index / stack_n once every dock on the scene is known.
        # R26-55: and the phrase's WORDS and the card's own aspect when the card was cut with them - the player
        # sets the words as live type re-lined to the card's box and keeps the crop as the provenance strip; a card
        # cut before R26-55 carries neither key and its entry is byte-for-byte what it was.
        **({"kind": DOCK_KIND_PRESS, "source": press["source"], "phrase": press["phrase"],
            **({"phrase_text": press["phrase_text"]} if press.get("phrase_text") else {}),
            **({"img": press["img"]} if press.get("img") else {}),
            **({"_stack": True} if stack else {})} if press else {}),
        **({"place": place, "read_s": rs, "park_s": ps,
            "park": span >= rs + ps} if place else {}),
        # E65: the room the card was placed in - outside the plot, the plot's empty room, the axis
        # band or the corner. Written only when the placer decided one, so every other entry is
        # byte-for-byte what it was.
        **({"place_room": room} if (place and room) else {}),
        **({"read_place": read_place} if (place and read_place) else {}),   # a centred card that pops here, then parks to its place (2026-09-10)
        # E63 (2026-09-11): the read the compiler MOVED off a chart that was still drawing, and where it moved it
        # from; or the read it DEFERRED entirely (the card enters at its parked place). Written only when the rule
        # fired, so every other entry is byte-for-byte what it was.
        **({"read_moved": read_moved} if (place and read_moved) else {}),
        **({"read_deferred": True} if (place and read_deferred) else {}),
        **({"arrive": arrive} if arrive else {}), **({"mass": mass} if mass else {}),   # P47 T1: only when the row names them
        **({"centre": True} if (centre or (read_deferred and place)) and place else {}),   # the design pass: a centred card sits at its box from its first frame - no reading size, no park
    }


def press_plate_error(plate_id: str, aid: str) -> str | None:
    """E45 §1 as code for the press card: the pile takes the STAGE's own centre box (the player's `.dock.press`
    placement), which on a LEDGER PAGE would sit over the plot. A quotation beside a chart is the dock's
    read->park, not the stack. Returns the error naming the dock, or None."""
    if str(plate_id).startswith(LEDGER_PREFIX):
        return (f"dock {aid}: a PRESS card stacks in the stage's centre box, which on a ledger page covers the "
                "plot (E45 §1) - put the quotation on its own plate, or dock the card as a still and let it park")
    return None


def assign_press_stack(docks: list[dict]) -> list[dict]:
    """THE PRESS STACK (P50 T3; doc 29 s9.27's push hand-off) on one scene's docks, in place.

    Every dock the row marked ``stack: True`` takes its index in ENTER order and the size of the pile, so the
    player poses the whole stack from the timeline alone (species/press.mjs ``pressStack``) - the newest lit,
    each older one a step back and a step dimmer. The marker itself never reaches the timeline. Returns the
    stacked docks, oldest first."""
    stacked = sorted([d for d in docks if d.pop("_stack", False)], key=lambda d: (d["enter"], d["slot"]))
    for i, d in enumerate(stacked):
        d["stack_index"], d["stack_n"] = i, len(stacked)
    return stacked


def title_for(asset: str) -> tuple[str, str]:
    """Human title and source line for an evidence asset."""
    if asset.startswith("ev-"):
        return asset[3:].replace("-", " ").replace(" v1", "").replace(" v2", "") \
            .replace(" v3", "").title(), "Money Physics — built evidence"
    stamped = json.loads((BUILD / "stamped-index.json").read_text(encoding="utf-8"))
    if asset in stamped:
        deck = asset.split("-s")[0].replace("-", " ").title()
        return asset.replace("-teacher-stamped", "").split("-")[-1].upper(), deck
    return asset.replace("-", " ").title(), "Research deck"


def narration_key_delays(chart: dict, dock_enter: float, tl: dict) -> dict:
    """NARRATION-KEYED DRAW: a delayed series erupts at its claim's word
    time, not at a hard-coded offset (doc 29 - the deferred item; the
    tempo field made every static offset stale by construction)."""
    import re as _re
    norm = lambda x: _re.sub(r"[^a-z0-9' ]", " ", x.lower()).split()
    wt = [(t, w) for w in tl["words"] for t in norm(w["w"])]
    wtoks = [t for t, _ in wt]
    targets = list(chart.get("series", []))         + list(chart.get("checklist", {}).get("rows", []))
    for sr in targets:
        anc = sr.get("delay_anchor")
        if not anc:
            continue
        toks = norm(anc)
        n = len(toks)
        for i in range(len(wtoks) - n + 1):
            if (wtoks[i:i + n - 1] == toks[:-1]
                    and wtoks[i + n - 1].startswith(toks[-1])):
                at = wt[i][1]["start"]
                if at >= dock_enter - 1.0:
                    sr["delay"] = round(max(0.0, at - dock_enter - 0.2), 2)
                    break
    return chart


# E99 s46, the operator on `r26-68-span-darker`: *"yes"* - the span reads as a DARKER region behind the line, at
# `span_alpha` 0.30. THE COMPILER'S HALF of that default: every timeline this compiler writes carries the two dials
# by name, so a build is dark whichever player it is mounted in - including a player frozen before the dials could
# default (E45: an approved cut renders through its OWN frozen copy and does not move). THE PLAYER'S half is
# `species/span.mjs` SPAN.TONE / SPAN.ALPHA_DARK, which is where a timeline that names neither dial gets the same
# answer; `test_kinetics_flags.py` holds the two numbers to each other, so neither side can drift alone.
SPAN_DIAL_DEFAULTS: dict = {"span_tone": "dark", "span_alpha": 0.30}


def build_kinetics() -> dict:
    """The flags a compiled timeline carries. P39: every capability defaults OFF in the template. E49 (P47 T5): the
    IDLE is on for every timeline this compiler writes - a build that wants stillness says so (``KINETICS["idle"] =
    False``); the goldens' frozen sources carry no flag and stay byte-identical. E99 s46: the span's two DIALS ride
    with them at the ruled default (``KINETICS["span_tone"] = "light"`` puts one build back to the chalk wash)."""
    k = {"idle": True, "stop_action": True, "arap_morph": True, "camera": True,
         **SPAN_DIAL_DEFAULTS, **KINETICS}   # P47 T1: an authored `arrive` is the switch; the flag only guards the goldens; P49 T2: the camera is one state per frame (the species pixel-identical)
    if "first_quant_claim_at" in k:
        claim_at = k["first_quant_claim_at"]
        if (isinstance(claim_at, bool) or not isinstance(claim_at, (int, float))
                or claim_at < 0 or claim_at > 60 or not math.isfinite(claim_at)):
            raise ValueError(
                "KINETICS['first_quant_claim_at'] must be a finite number from 0 through 60 seconds (opening minute)"
            )
    # E99 s55: the drift's amplitude has NO global default here on purpose - unset, the player takes
    # kinetics/idle.mjs IDLE.DRIFT_PX, which is the string every approved cut was rendered with (E45). A build that
    # names one is checked by the SAME refusal a row's `;drift=` gets, so the two ways of asking cannot disagree.
    if "plate_idle_drift_px" in k:
        k["plate_idle_drift_px"] = plate_drift_px(k["plate_idle_drift_px"], "KINETICS['plate_idle_drift_px']")
    return k


# ------------------------------------------------------------------ P51 T5: THE OVERRIDE SIDECAR
# The grill, 2026-09-11: "a human's or a flash agent's edit is a sidecar of overrides keyed by row
# id and field, layered over the shot table the agent authors". The agent AUTHORS; an editor
# TUNES. So an edit never rewrites the table - it lands in `<build>/overrides.json`:
#
#     {"s04.dock.dock-k-pledge-record": {"centre_y": 0.32},
#      "s04.species.3": {"at": {"word": "pledged"}},
#      "s02.camera": null,
#      "s04.plate": {"idle": "drift"},
#      "s04.exit": "dip"}
#
# The key is a ROW ID and a FIELD. The ids are DERIVED from the compiled order - `s01`.. exactly as
# `main` writes them, a dock by its slide, a species by its INDEX in the row's authored list,
# `.camera` / `.plate` / `.exit` for the row's own - never random and never stored in the table, so
# two sidecars written a week apart diff line by line and a rebuild renumbers nothing. Every value
# goes through the SAME validator the shot table's own does (`dock_opts`, `validate_species` /
# `_validate_page_fields`, `split_plate_opts`, `validate_camera_row`, `parse_exit`); an unknown id,
# an unknown field or a bad value is REFUSED naming both, never quietly dropped. `null` puts a
# field back to the row's default (the camera off, an option unset). The layering is PURE - the
# authored rows are never mutated - and idempotent: the same rows plus the same sidecar give the
# same rows, whatever order the keys arrive in.
OVERRIDES_NAME = "overrides.json"
OVERRIDE_KEY_FORM = ("<scene>.plate | <scene>.exit | <scene>.camera | <scene>.dock.<slide> | "
                     "<scene>.species.<index>")
IDX_PLATE, IDX_KEN, IDX_DOCKS, IDX_EXIT, IDX_SPECIES, IDX_CAMERA = 2, 3, 4, 5, 6, 7
SPECIES_OPEN_FIELDS = ("at", "dur", "until", "idle")   # every species may take these, authored on the row or not
SPECIES_CLOSED_FIELDS = ("kind", "id")                 # ... and these are AUTHORING: a sidecar never changes what a species IS


def scene_row_id(n: int) -> str:
    """The nth row IN COMPILE ORDER, as the compiled scene names itself (`s01`..)."""
    return f"s{n + 1:02d}"


def dock_row_id(scene_id: str, slide: str) -> str:
    """A dock's stable key: its SLIDE, which is the one thing about a card the row already names."""
    return f"{scene_id}.dock.{slide}"


def species_row_id(scene_id: str, n: int) -> str:
    """A species' stable key: its INDEX in the row's authored list (a held light dropped for want of
    room keeps its number, so the key survives the compiler's own edits)."""
    return f"{scene_id}.species.{n}"


def camera_row_id(scene_id: str) -> str:
    return f"{scene_id}.camera"


def compile_order(rows) -> list[int]:
    """The row indices in the order `main` compiles them - it sorts the table on the start time - so
    a sidecar's `s04` names the row the compiled timeline's `s04` is."""
    starts = [float(r[0]) for r in rows]
    if len(set(starts)) != len(starts):
        dup = next(s for s in starts if starts.count(s) > 1)
        raise ValueError(f"two shot rows open at {dup}s - the compiler sorts the table and a sidecar keys rows "
                         "by that order, so every row has to open at its own second")
    return sorted(range(len(rows)), key=lambda i: starts[i])


def row_ids(rows) -> dict[str, int]:
    """Every scene id of a shot table -> that row's index in the AUTHORED list."""
    return {scene_row_id(n): i for n, i in enumerate(compile_order(rows))}


def _override_words(words) -> list[dict] | None:
    """The build's words in the shape `authoring.words` reads: `timeline.json` writes start/end, a
    take writes start_s/end_s, and a sidecar resolves against either."""
    if not words:
        return None
    if isinstance(words, dict):
        words = words.get("words") or []
    return [{"w": w["w"], "start_s": w.get("start_s", w.get("start")), "end_s": w.get("end_s", w.get("end"))}
            for w in words]


def _word_at(form: dict, ws, key: str) -> float:
    """`{"word": "<phrase>"}` - the second the take says it, read through `authoring.words.at`, so a
    hand edit anchors on the SCRIPT the way the shot table does instead of on a stopwatch."""
    if set(form) != {"word"} or not isinstance(form.get("word"), str) or not form["word"].strip():
        raise ValueError(f"{key}: field 'at': the word form is {{\"word\": \"<phrase>\"}}, not {form!r}")
    if not ws:
        raise ValueError(f"{key}: field 'at': {form['word']!r} needs the build's words - pass words= "
                         "(the build's timeline.json words) to apply_overrides")
    from authoring import words as KW
    try:
        return KW.at(ws, form["word"])
    except SystemExit as exc:
        raise ValueError(f"{key}: field 'at': {exc}") from None


def _patched(base: dict, patch: dict, key: str, allowed, check) -> dict:
    """One field at a time onto `base`, each checked by the shot table's own validator the moment it
    lands - so the field that breaks is the field the refusal names. `None` unsets a field."""
    out = dict(base)
    for field in sorted(patch):
        if allowed is not None and field not in allowed:
            raise ValueError(f"{key}: field {field!r} is not one of {'|'.join(allowed)}")
        trial = dict(out)
        if patch[field] is None:
            trial.pop(field, None)
        else:
            trial[field] = patch[field]
        try:
            check(trial)
        except ValueError as exc:
            raise ValueError(f"{key}: field {field!r}: {exc}") from None
        out = trial
    return out


def _grow(row: list, i: int) -> None:
    while len(row) <= i:
        row.append(None)


def _row_press(row) -> dict:
    """The row's PRESS docks, read the way `main` reads them before the species are validated - a
    callout's `phrase` target names one, and the law cannot check a name it has not read."""
    out = {}
    for d in (row[IDX_DOCKS] or []) if len(row) > IDX_DOCKS else []:
        try:
            o = dock_opts(d[4] if len(d) > 4 else None)
        except (ValueError, IndexError, TypeError):
            continue
        if o.get("press"):
            out[d[0]] = o["press"]
    return out


def _override_dock(row: list, key: str, slide: str, patch) -> None:
    """A dock's OPTION fields (the tuple's optional 5th element), validated by `dock_opts`."""
    ds = list(row[IDX_DOCKS] or []) if len(row) > IDX_DOCKS else []
    hit = next((j for j, d in enumerate(ds) if str(d[0]) == slide), None)
    if hit is None:
        raise ValueError(f"{key}: no dock {slide!r} on this row - its docks are "
                         f"{', '.join(str(d[0]) for d in ds) or 'none'}")
    if not isinstance(patch, dict):
        raise ValueError(f"{key}: a dock override is a dict of {'|'.join(DOCK_OPTS)}, not {patch!r}")
    d = list(ds[hit])
    base = dict(d[4]) if len(d) > 4 and isinstance(d[4], dict) else {}
    opts = _patched(base, patch, key, DOCK_OPTS, dock_opts)   # `dock_opts` CHECKS; the row keeps the raw options
    if opts or len(d) > 4:
        _grow(d, 4)
        d[4] = opts or None
    ds[hit] = tuple(d) if isinstance(ds[hit], tuple) else d
    row[IDX_DOCKS] = tuple(ds) if isinstance(row[IDX_DOCKS], tuple) else ds


def _override_species(row: list, key: str, sel: str, patch, ws) -> None:
    """A species' own fields, validated by the targeting law (`validate_species` ->
    `_validate_page_fields`) with the patched entry back in its row. `at` may arrive as a number or
    as `{"word": "<phrase>"}`."""
    sp = list(row[IDX_SPECIES] or []) if len(row) > IDX_SPECIES else []
    if not sel.isdigit():
        raise ValueError(f"{key}: a species is keyed by its INDEX in the row's authored list "
                         f"(`<scene>.species.<index>`), not {sel!r}")
    n = int(sel)
    if n >= len(sp) or not isinstance(sp[n], dict):
        raise ValueError(f"{key}: no species {n} on this row - it carries {len(sp)} "
                         f"({f'0..{len(sp) - 1}' if sp else 'none'})")
    if not isinstance(patch, dict):
        raise ValueError(f"{key}: a species override is a dict of the species' own fields, not {patch!r}")
    entry = sp[n]
    patch = dict(patch)
    if isinstance(patch.get("at"), dict):
        patch["at"] = _word_at(patch["at"], ws, key)
    for f in patch:
        if f in SPECIES_CLOSED_FIELDS:
            raise ValueError(f"{key}: field {f!r} is AUTHORING, not an edit - a sidecar tunes a species, "
                             "it does not change what it is")
    allowed = tuple(dict.fromkeys(tuple(f for f in entry if f not in SPECIES_CLOSED_FIELDS) + SPECIES_OPEN_FIELDS))
    plate, ken, press = str(row[IDX_PLATE]), row[IDX_KEN], _row_press(row)

    def check(entry_trial: dict) -> None:
        errs = validate_species(sp[:n] + [entry_trial] + sp[n + 1:], ken, plate, press_docks=press)
        if errs:
            raise ValueError("; ".join(errs))

    sp[n] = _patched(entry, patch, key, allowed, check)
    row[IDX_SPECIES] = tuple(sp) if isinstance(row[IDX_SPECIES], tuple) else sp


def _override_plate(row: list, key: str, patch) -> None:
    """The row's PLATE options - the `;key=value` suffixes `split_plate_opts` admits. The bare id is
    never touched: a different world is a different row, not an edit."""
    if not isinstance(patch, dict):
        raise ValueError(f"{key}: a plate override is a dict of {'|'.join(PLATE_OPTS)} "
                         f"(the `;key=value` options a plate id carries), not {patch!r}")
    pid = str(row[IDX_PLATE])
    for field in sorted(patch):
        if field not in PLATE_OPTS:
            raise ValueError(f"{key}: field {field!r} is not one of {'|'.join(PLATE_OPTS)}")
        bare, *parts = pid.split(";")
        kept = [p for p in parts if p.split("=", 1)[0] != field]
        trial = ";".join([bare] + kept + ([] if patch[field] is None else [f"{field}={patch[field]}"]))
        try:
            split_plate_opts(trial)
        except ValueError as exc:
            raise ValueError(f"{key}: field {field!r}: {exc}") from None
        pid = trial
    row[IDX_PLATE] = pid


def _override_exit(row: list, key: str, value) -> None:
    """The row's EXIT (the transition INTO it, E47), validated by `parse_exit`; null = the
    mechanical default."""
    if value is not None and not isinstance(value, str):
        raise ValueError(f"{key}: field 'exit': an exit is one of {'|'.join(SCENE_EXITS)} (dip and blurzoom may "
                         f"carry their length, `dip:0.4`) or null for the mechanical default, not {value!r}")
    if value is not None:
        try:
            parse_exit(value)
        except ValueError as exc:
            raise ValueError(f"{key}: field 'exit': {exc}") from None
    _grow(row, IDX_EXIT)
    row[IDX_EXIT] = value


def _override_camera(row: list, key: str, value, aspect) -> None:
    """The row's CAMERA (the 8th element): null turns it off, a dict is the keys/attention form
    `validate_camera_row` admits - against this row's own species, as the compiler checks it."""
    if value is not None and not isinstance(value, dict):
        raise ValueError(f"{key}: field 'camera': a camera is null (the camera off) or a dict "
                         f"{{keys: [...], attention: {'|'.join(CAMERA_ATTENTION)}}}, not {value!r}")
    sp = list(row[IDX_SPECIES] or []) if len(row) > IDX_SPECIES else []
    errs = validate_camera_row(value, sp, str(row[IDX_PLATE]), aspect)
    if errs:
        raise ValueError(f"{key}: field 'camera': " + "; ".join(errs))
    _grow(row, IDX_CAMERA)
    row[IDX_CAMERA] = value


def apply_overrides(rows, overrides, words=None, aspect=None) -> list[tuple]:
    """The sidecar layered over the AUTHORED rows, BEFORE anything is compiled - the one place a
    hand edit enters the build.

    `rows` are shot-table rows, `overrides` the parsed `<build>/overrides.json` keyed
    ``<row id>.<field>`` (see OVERRIDE_KEY_FORM), `words` the build's `timeline.json` words (or a
    take's) so a species' `at` may be named by its phrase. Returns NEW rows in the same authored
    order; the input is never mutated, and with an empty sidecar the rows come back as they went in.
    A ValueError names the row id and the field - the caller names the file."""
    out = [tuple(r) for r in rows]
    if not overrides:
        return out
    if not isinstance(overrides, dict):
        raise ValueError(f"the sidecar is a JSON object keyed by row id and field ({OVERRIDE_KEY_FORM}), "
                         f"not a {type(overrides).__name__}")
    ids = row_ids(rows)
    ws = _override_words(words)
    edited: dict[int, list] = {}
    for key in sorted(overrides):
        scene, _, rest = str(key).partition(".")
        if scene not in ids:
            raise ValueError(f"{key!r} names no row - this shot table is "
                             f"{scene_row_id(0)}..{scene_row_id(len(out) - 1)}")
        if not rest:
            raise ValueError(f"{key!r} names a scene but no field - a sidecar key is {OVERRIDE_KEY_FORM}")
        row = edited.setdefault(ids[scene], list(out[ids[scene]]))
        field, _, sel = rest.partition(".")
        value = overrides[key]
        if field == "dock" and sel:
            _override_dock(row, key, sel, value)
        elif field == "species" and sel:
            _override_species(row, key, sel, value, ws)
        elif field == "plate" and not sel:
            _override_plate(row, key, value)
        elif field == "exit" and not sel:
            _override_exit(row, key, value)
        elif field == "camera" and not sel:
            _override_camera(row, key, value, aspect)
        else:
            raise ValueError(f"{key!r}: {rest!r} is not a field of a row - a sidecar key is {OVERRIDE_KEY_FORM}")
    for i, row in edited.items():
        out[i] = tuple(row)
    return out


def main() -> int:
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    # THE AUTHORED SHOT TABLE is the source. Not an allocator.
    import importlib.util
    sp = importlib.util.spec_from_file_location("shot", EP / SHOT_TABLE_FILE)
    shot = importlib.util.module_from_spec(sp); sp.loader.exec_module(shot)
    plan = sorted(shot.W)
    # P51 T5: a human's or a flash agent's edit is a SIDECAR over the authored table, never a rewrite of it.
    # The kit lays it over the literal before the compiler is pointed here (`authoring.table.apply_sidecar`),
    # so this pass is a no-op on a kit build; it is the whole mechanism when the compiler is run on its own.
    applied: list[str] = []
    ov_path = BUILD / OVERRIDES_NAME
    if ov_path.is_file():
        overrides = json.loads(ov_path.read_text(encoding="utf-8"))
        try:
            plan = apply_overrides(plan, overrides, words=tl.get("words"), aspect=ASPECT)
        except ValueError as exc:
            raise SystemExit(f"FAIL: {ov_path.name}: {exc}") from None
        applied = sorted(overrides)
        print(f"  overrides   : {len(applied)} from {ov_path.name} - {', '.join(applied)}")
    # a PAGES-ONLY short writes no dock metadata: absent is "this table docks nothing", not a broken build
    # (the first such build, normal-for-which-bridge 2026-09-12, died here with FileNotFoundError)
    dock_meta = BUILD / "evidence-dock.json"
    dock = json.loads(dock_meta.read_text(encoding="utf-8")) if dock_meta.is_file() else []
    META = {d["asset"]: d for d in dock}
    pages = json.loads((BUILD / "caption-pages.json").read_text(encoding="utf-8"))
    # the timeline names its own audio: after insert_edit_pauses.py it is
    # the PAUSED file - embedding the unpaused one desyncs every word
    audio = BUILD / tl.get("paused_audio", "audio/episode.mp3")         if tl.get("edit_pauses_applied") else BUILD / "audio/episode.mp3"
    if not audio.exists():
        print(f"FAIL: {audio} missing — join the chained parts first")
        return 1
    print(f"  audio: {audio.name}")

    evidence, uris, scenes, estimated_pages = {}, {}, [], []   # P50 T16: the pages this build placed by ESTIMATE, for the report below
    read_moves: list[str] = []      # E63: the docks whose READ the rule moved off a building chart ...
    read_defers: list[str] = []     # ... and the ones with no band to move it to, deferred to the parked box
    card_rooms: list[tuple] = []    # E65: (dock row id, room, box, page title) for every card the placer placed
    ledger_rows: list[int] = []     # the rows carrying a ledger page, so the report can say how many were MEASURED
    prev_world = None   # E47 corrected: the outgoing row's world, for `world_changed`
    for i, row in enumerate(plan):
        # exit style is HYBRID (operator, 2026-08-29): mechanical default
        # (E47, 2026-09-06: docks -> DIP, bare -> cut; it was docks -> wipe),
        # with an optional authored 6th element per window for boundaries where
        # the MEANING differs - doc 29 Part 6: cut = contrast/correction, wipe =
        # process continuation. The rule itself is `scene_exit` above.
        a, b, plate, ken, ds = row[:5]
        sid = scene_row_id(i)   # P51 T5: the scene's own id, derived here and written onto every part an editor keys by
        authored_exit = row[5] if len(row) > 5 else None
        # TARGETED SPECIES (doc 29 s9.27, P35 T7): the optional 7th element.
        # The targeting law is a hard build error naming the row; the pivot
        # span is None until the parent wires it from the ledger (s9.28 C4).
        row_species = list(row[6]) if len(row) > 6 and row[6] is not None else []
        # P51 T5: every species carries `<scene>.species.<n>`, n its index in the row's AUTHORED list - so the key
        # survives the hold/drop pass below, and a chart_to is keyed exactly as a spotlight is.
        row_species = [{**e, "id": species_row_id(sid, n)} if isinstance(e, dict) else e
                       for n, e in enumerate(row_species)]
        row_camera = row[7] if len(row) > 7 and row[7] is not None else None   # P49 T1: the optional 8th element
        # each window runs to the next so the world layer never drops out
        b = plan[i + 1][0] if i + 1 < len(plan) else tl["runtime_s"]
        # dur: "hold" (operator, 2026-09-08, on the spotlight: "right now we flash it on, and really, it should hold until it
        # has a reason not to") - a species held until the NEXT event on its row (the next species' `at`) or the row's end.
        # Resolved here so the player and the gates see plain seconds; an authored number is never touched.
        ats = sorted([float(e["at"]) for e in row_species if isinstance(e, dict) and isinstance(e.get("at"), (int, float))]
                     + [float(d[2]) for d in (ds or []) if isinstance(d, (list, tuple)) and len(d) > 2 and isinstance(d[2], (int, float))])   # a card ARRIVING is an event too
        for e in row_species:
            if isinstance(e, dict) and e.get("dur") == "hold":
                nxt = next((x for x in ats if x > float(e["at"]) + 1e-6), None)
                end = nxt if nxt is not None else float(b)
                # `until` (E25, 2026-09-08: the light follows the SENTENCE the chart proves - it releases on the first word of the
                # next sentence; the shot table writes it from the take's punctuation, so it is a rule read off the words, not a number)
                if isinstance(e.get("until"), (int, float)) and not isinstance(e.get("until"), bool):
                    end = min(end, float(e["until"]))
                e["dur"] = round(max(0.05, end - float(e["at"])), 2)
                e["held"] = True   # the record of why the duration is what it is
        # a held light with no room is a FLASH, and a flash is a glitch (operator, 2026-09-08: "the spotlight on a black card that
        # flashes briefly" - 0.61 s between the bars landing and the card arriving). Below HOLD_MIN_S the species is dropped, and
        # the drop is written into the timeline so the choreography ledger can see it.
        dropped = [e for e in row_species if isinstance(e, dict) and e.get("held") and e["dur"] < HOLD_MIN_S]
        for e in dropped:
            row_species.remove(e)
        if dropped:
            print(f"  hold: dropped {len(dropped)} {'/'.join(e['kind'] for e in dropped)} on row {i + 1} - under {HOLD_MIN_S}s of room before the next event")
        # R26-219: a page-bound species LEAVES with the page it was written on. Stamped here, beside the hold pass
        # that decides the other end of a species' life, so the player and the gates see plain seconds either way.
        left, clamped, page_dropped = stamp_page_leave(row_species)
        if left:
            print(f"  page leave: {len(left)} page-bound species retract with their page on row {i + 1} "
                  f"({'/'.join(sorted({e['kind'] for e in left}))}) - R26-219")
        if clamped:
            print(f"  page leave: dur clamped to the leave on row {i + 1}: "
                  + ", ".join(f"{k} {was:g}s -> {now:g}s" for k, was, now in clamped))
        if page_dropped:
            print(f"  page leave: dropped {len(page_dropped)} "
                  f"{'/'.join(sorted({e['kind'] for e in page_dropped}))} on row {i + 1} - the chart_to that "
                  "replaces the page fires on the species' own word, so there is nothing to write")
        # P50 T3: the row's PRESS docks, read BEFORE the species are validated - a callout's `phrase` target
        # names one of them, and the targeting law cannot check a name it has not read yet. A malformed option
        # is ignored here and raised by the dock pass below, which names the dock in its error.
        row_press = {}
        for _d in (ds or []):
            try:
                _o = dock_opts(_d[4] if len(_d) > 4 else None)
            except (ValueError, IndexError, TypeError):
                continue
            if _o.get("press"):
                row_press[_d[0]] = _o["press"]
        species_errors = (validate_species(row_species, ken, plate, pivot_span=None, press_docks=row_press)
                          + validate_camera_row(row_camera, row_species, plate, ASPECT)
                          + validate_newsreel_strip(row_species, ASPECT, bool(ds)))   # P52 T6: the strip law (gate 1)
        if species_errors:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): " + "; ".join(species_errors))
        resolved_chip_stamps = {}
        for n, e in enumerate(row_species):
            if isinstance(e, dict) and e.get("kind") == SPECIES_CHIP and e.get("form") == "stamp":
                try:
                    row_species[n], stamp_asset = _with_stamp_catalogue(e)
                except (TypeError, ValueError) as exc:
                    raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): chip stamp: {exc}") from exc
                resolved_chip_stamps[e["icon"]] = stamp_asset
        # P50 T2: a chip's SOURCED glyph rides the asset map exactly as a plate or a dock still does,
        # keyed `icon:<name>` - the geometry travels in the player, never a path to a file on disk.
        for e in row_species:
            for _icon in species_icons(e):   # P50 T4: a flow's nodes and its swap ride the same route as the chip's one
                try:
                    uris[ICON_PREFIX + _icon] = icon_geometry(_icon)
                except ValueError as exc:
                    raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
            for _prop in species_props(e):   # P61 T8 / E93: the page-form agenda's stamped cutouts, the same route
                try:
                    stamp_asset = resolved_chip_stamps.get(_prop)
                    uris[PROP_PREFIX + _prop] = data_uri(stamp_asset["file"]) if stamp_asset else catalogue_stamp_uri(_prop)
                except ValueError as exc:
                    raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
        # a ledger page is drawn, not embedded (doc 29 s9.26); a bad or
        # missing series is a hard build error naming the row
        try:
            world = world_for_plate(plate, ken, EP, META)
        except ValueError as exc:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
        try:
            derive_rescale_states(world, row_species, plate, EP, sid=sid)   # P48 T2: each `chart_to rescale` gets its own derived page state; E64: and each recast its derived KEY
        except ValueError as exc:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
        # R26-220 / E99 s80 (2): the row's ZOOMS against what this page can take. It lands here and not beside
        # `validate_species` because the ceiling is the PAGE's, and the page only exists once `world_for_plate`
        # has read its series and `stamp_full_stage` has said which geometry it takes at this aspect.
        zoom_errors = camera_zoom_errors(world, row_species, row_camera, plate, ASPECT)
        if zoom_errors:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): " + "; ".join(zoom_errors))
        _thread = ((world.get("page") or {}).get("thread") or {}) if world.get("kind") == SPECIES_LEDGER else {}
        if _thread:   # HF-16: the wire names the scene BEFORE this one, and that scene has to own the mark
            _prev = scenes[-1] if scenes else None
            _terr = thread_mark_error((_prev or {}).get("world"), _thread["key"], f"shot row {i + 1} ({a}-{b}s) {plate!r}")
            if _terr:
                raise SystemExit(f"FAIL: {_terr}")
            _thread["from"] = _prev["scene_id"]
        if world.get("kind") == VECMAP_KIND:
            uris[MAP_PREFIX + world["map"]] = world_map_json(world["map"])   # ONCE: the same key for every vecmap scene in the build
        elif world.get("kind") == SPECIES_CLIP:
            uris[world["asset_id"]] = data_uri(Path(world.pop("clip_path")))   # raw mp4, keyed by the clip's stem
        elif "asset_id" in world:
            uris[world["asset_id"]] = data_uri(R.find_asset(world["asset_id"]), STAGE_W)   # the bare id (E49's `;idle=` is not part of it)
        # P58 T3: the plate's own DEPTH PLANES, if it ships in planes - one asset key per plane, RAW (the alpha
        # IS the plane), and {key, k, role} on the world so the camera can give each plane its share of the move.
        # A flat plate adds nothing here, so its world is the world it has always been.
        if world.get("asset_id") and world.get("kind") not in (SPECIES_CLIP, VECMAP_KIND):
            _plate_path = R.find_asset(world["asset_id"])
            try:
                _planes = plate_depth_planes(_plate_path)
            except ValueError as exc:
                raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s) world {world['asset_id']!r}: {exc}") from exc
            if _planes:
                # E99 s55: a plane whose file is a CLIP is ALIVE - the ambient lane's generated life as the
                # background wall. The only thing the player needs beyond the still case is that it IS one
                # (`clip: true`), so it mounts a <video> instead of a background image; `data_uri` already embeds
                # an mp4 raw, keyed the same way. A plate with no alive plane writes the key it always wrote.
                world["layers"] = [{"key": f"{LY_PREFIX}{world['asset_id']}:{p['role']}",
                                    "k": p["depth"], "role": p["role"],
                                    **({"clip": True} if p.get("clip") else {})} for p in _planes]
                for _p, _ly in zip(_planes, world["layers"]):
                    uris[_ly["key"]] = data_uri(Path(_p["file"]))   # RAW: the capped path would drop the alpha
        # P50 T7: the SURFACES this plate declares, read once - the docks below land on them and the camera aims at
        # them by name. A world that is not a plate has none, and only a row that names one gets an error.
        _embeds = (plate_embeds(R.find_asset(world["asset_id"]))
                   if world.get("asset_id") and world.get("kind") not in (SPECIES_CLIP, VECMAP_KIND) else {})
        try:
            resolve_embed_targets(row_species, _embeds, f"shot row {i + 1} ({a}-{b}s)")
        except ValueError as exc:
            raise SystemExit(f"FAIL: {exc}") from exc
        docks = []
        if world.get("kind") == SPECIES_LEDGER and world.get("page"):
            ledger_rows.append(i + 1)
            if not page_is_measured(world, ASPECT):
                estimated_pages.append(f"row {i + 1} {str(world['page'].get('title') or plate)[:44]!r}")
        # E45 §1: on a ledger page every dock parks in the same rectangle, computed from the
        # page's own geometry. Only the SOLO card (slot 0) is placed - a paired/stacked dock keeps
        # the layout its slot declares, and a plain plate keeps the solo card entirely.
        plate_room = plate_room_px(world.get("room"), ASPECT)   # R26-221: the rectangle THIS picture plate declares a card may stand in
        # P69 T5 (R26-247 L2; E99 s88 (3)): the row's STAMPS take the room first - fitted in row order, each round the
        # earlier ones' mark and ring, so the first is the stamp alone - and only then is the page's place taken for the
        # row's other docks, clear of every stamp's fitted box (a row with no stamp places exactly as it always did)
        row_opts = []
        for aid, _slot, _enter, _exitt, *dextra in ds:   # P47 T1: an optional 5th element names how the card arrives
            try:
                _dopt = dock_opts(dextra[0] if dextra else None)
                _paint = ((painted_box(dock_asset_path(aid, EP)) if _dopt.get("prop") else painted_box(None, _dopt.get("card_aspect")))
                          if _dopt.get("arrive") == "stamp" else None)   # the PAINTED mark: a prop's alpha box, a card's whole box
            except ValueError as exc:
                raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s) dock {aid}: {exc}") from exc
            row_opts.append((aid, _dopt, _paint))
        try:   # R26-20 send-back #2: every stamp is fitted to the box the engine draws, or the row fails
            stamp_fits, stamp_boxes = row_stamp_fits(world, ASPECT, row_opts, plate_room, newsreel_boxes(row_species, ASPECT),
                                                     f"shot row {i + 1} ({a}-{b}s)")
        except ValueError as exc:
            raise SystemExit(f"FAIL: {exc}") from exc
        place = dock_place(world, ASPECT, newsreel_boxes(row_species, ASPECT), clear_of=stamp_boxes)   # P52 T6: the band's strip is reserved - a card parks ABOVE the crawl
        for n_dock, (aid, slot, enter, exitt, *dextra) in enumerate(ds):
            dopt = row_opts[n_dock][1]
            d = META.get(aid, {"title": aid, "source": "", "species": "deck",
                               "badges": []})
            auto_centre = solo_centre_by_clock(world, ASPECT, len(ds), slot, enter, a, dopt)   # R26-22: E50's clock centres a solo card on a MEASURED page
            centred = bool(dopt.get("centre")) or auto_centre
            dplace = centred_place(place, ASPECT, dopt.get("card_aspect"), (world or {}).get("page"), dopt.get("centre_w"), dopt.get("centre_band"), dopt.get("centre_y"), dopt.get("centre_x"), newsreel_boxes(row_species, ASPECT)) if (place and centred) else place   # the third watch: a card centred on the page
            if place is None:   # R26-221: a PICTURE PLATE - the row's own box, or the room the plate declared (None = E45's solo card)
                try:
                    dplace = plate_dock_place(plate_room, ASPECT, dopt, f"shot row {i + 1} ({a}-{b}s) dock {aid}")
                except ValueError as exc:
                    raise SystemExit(f"FAIL: {exc}") from exc
            stamp_fit = stamp_fits.get(n_dock)   # fitted above, before the row's other docks, whatever its slot
            if stamp_fit:
                dplace, centred = {k: stamp_fit[k] for k in ("x", "y", "w", "h", "room")}, True
                print(f"  stamp: {sid}.{aid} - {stamp_fit['room']}: {stamp_fit['why']}")
            if centred and isinstance(dplace, dict) and isinstance(place, dict) and "room" not in dplace:
                dplace = dict(dplace, room=place.get("room"))   # E65: the room the PAGE offered travels with the centred box
            if dopt.get("press"):   # P50 T3: E45 - the pile has one box, and it is the stage's centre
                _perr = press_plate_error(plate, aid)
                if _perr:
                    raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s) {_perr}")
            fg_key = None
            if dopt.get("behind"):   # HF-17: the card goes behind the plate's own front
                _layers = plate_layers(R.find_asset(world["asset_id"]) if world.get("asset_id") else None)
                _berr = behind_error(world, _layers, dopt["behind"], f"shot row {i + 1} ({a}-{b}s) dock {aid}")
                if _berr:
                    raise SystemExit(f"FAIL: {_berr}")
                fg_key = f"{FG_PREFIX}{world['asset_id']}:{dopt['behind']}"
                uris[fg_key] = data_uri(_layers[dopt["behind"]])   # RAW: the capped path re-encodes through RGB and would drop the alpha
            embed = None
            if dopt.get(EMBED_KEY):   # P50 T7: the card lands ON one of the plate's declared surfaces
                _eerr = embed_error(world, _embeds, dopt[EMBED_KEY], f"shot row {i + 1} ({a}-{b}s) dock {aid}", d.get("species"))
                if _eerr:
                    raise SystemExit(f"FAIL: {_eerr}")
                try:
                    _eap = dock_asset_path(aid, EP)
                    embed = embed_entry(dopt[EMBED_KEY], _embeds[dopt[EMBED_KEY]], tl.get("words"),
                                        dopt.get("card_aspect") or image_aspect(_eap), fit=embed_fit(dopt, _eap, d))
                except ValueError as exc:
                    raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s) dock {aid}: {exc}") from exc
            rd = dopt.get("read") or {}   # the box a centred card POPS at before it parks to dplace (2026-09-10)
            # R26-221: `dplace` rather than `place` is the test - a card on a picture plate is placed by its own box
            # (the page's `place` is None there), and a read the compiler drops is a card that never pops
            rplace = None if stamp_fit else centred_place(place, ASPECT, rd.get("card_aspect", dopt.get("card_aspect")), (world or {}).get("page"), rd.get("centre_w"), None, rd.get("centre_y"), rd.get("centre_x"), newsreel_boxes(row_species, ASPECT)) if (dplace and rd) else None
            # E63 (widened): a card never READS over the page's plot, drawing or finished. The read box is the row's
            # own when it named one, the card's solo CSS box otherwise; a centred card with no `read` has no pop at all
            # (it takes its parked box from its first frame), so there is nothing to move and the entry is untouched.
            # The build windows are still handed over - for the RECORD in `why`, never for the decision.
            # R26-221: ... and on a picture plate the BOX is the slot - a row that authored one (or a plate that
            # declared the room) has already said where this card goes, on either slot, so it is never dropped here
            eplace = dplace if (slot == 0 or centred or (place is None and dplace)) else None
            if not stamp_fit:   # P69 T5: a row's other dock never parks on a stamp's mark or its ring - refused, by row
                _clash = stamp_clash_error(f"shot row {i + 1} ({a}-{b}s) dock {aid}", eplace, stamp_boxes)
                if _clash:
                    raise SystemExit(f"FAIL: {_clash}")
            _rs = float(dopt["read_s"]) if dopt.get("read_s") else DOCK_READ_S
            _ps = float(dopt["park_s"]) if dopt.get("park_s") else DOCK_PARK_S
            _aspect_of_card = rd.get("card_aspect", dopt.get("card_aspect")) if rd else dopt.get("card_aspect")
            _read_box = (dock_read_box(ASPECT, rplace, _aspect_of_card)
                         if (rplace or not centred) else None)
            e63 = read_over_build(eplace, _read_box, (world or {}).get("page"), ASPECT, float(enter),
                                  float(enter) + (_rs if exitt - enter >= _rs + _ps else exitt - enter),
                                  page_build_windows(world, row_species, a), _aspect_of_card) or {}
            if e63.get("read_place"):
                rplace = e63["read_place"]
                read_moves.append(f"{sid}.{aid} -> {e63['read_moved']['to']}")
            elif e63.get("read_deferred"):
                read_defers.append(f"{sid}.{aid}")
            ring_fit = stamp_fit   # the fit above; a stamp with no place never reaches here (it failed the row)
            if isinstance(eplace, dict) and eplace.get("room"):   # E65: the room every placed card took
                card_rooms.append((f"{sid}.{aid}", eplace["room"],
                                   [eplace["x"], eplace["y"], eplace["w"], eplace["h"]],
                                   str((world or {}).get("page", {}).get("title") or "")[:44]))
            if True:
                if aid not in evidence:
                    try:
                        ap = dock_asset_path(aid, EP)
                    except ValueError as exc:
                        raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
                    evidence[aid] = {
                        # a VIDEO dock (E44 / R26-7): the card carries moving pictures, seeked to
                        # the scene clock by the player's one seek. Declared here so the player
                        # mounts a <video> instead of an <img> and the gate can see it.
                        **({"kind": DOCK_KIND_PROP} if dopt.get("prop")   # E99 s87: a prop is art in the world, and the row says so
                           else {"kind": DOCK_KIND_CUTOUT} if dopt.get("cutout")
                           else {"kind": DOCK_KIND_VIDEO} if is_video_asset(ap) else {}),   # P53 T7: the row's intent, not the asset's nature
                        # Authored in the dock - a machine-mangled asset id is
                        # not a title, and empty badges leave the card's whole
                        # information layer blank (ruling B3: a badge numeral
                        # must appear verbatim in the document behind it).
                        "title": d["title"], "source": d["source"],
                        "species": d["species"],
                        "document": {"path": str(ap.relative_to(ap.anchor)),
                                     "sha256": sha(ap)},
                        "badges": d["badges"],
                        # a record document carries its typed-word payload;
                        # the player renders it as live type + highlighter
                        # instead of a static image (doc 29 record species)
                        **({"record": d["record"]} if "record" in d else {}),
                        # a STACK payload: the verdict pile-up - member
                        # ids resolve against the asset-data map in the
                        # player (every member is docked elsewhere)
                        **({"stack": d["stack"]} if "stack" in d else {}),
                        # a LIVE CHART payload: series emitted by the chart
                        # builder from the same data as the PNG. The player
                        # DRAWS the line; the PNG stays the static fallback.
                        **({"chart": narration_key_delays(json.loads(
                            ap.with_suffix(".series.json").read_text(
                                encoding="utf-8")), enter, tl)}
                           if ap.with_suffix(".series.json").exists() else {}),
                    }
                    # BADGE-CHART SYNC: chart data refetches on rebuild, so
                    # an authored badge value can silently drift from the end
                    # label on the document behind it (caught 2026-08-30:
                    # badges said +601% while a fresh fetch drew +613%). A
                    # badge whose accent maps to a series color takes the
                    # series' CURRENT label - B3 by construction.
                    ch = evidence[aid].get("chart")
                    if ch and ch.get("series"):
                        amap = {"coral": "crimson", "teal": "teal",
                                "cobalt": "cobalt", "ink": "deemph",
                                "sunflower": "amber"}
                        for bd in evidence[aid]["badges"]:
                            sc_col = amap.get(bd.get("accent", ""))
                            for sr in ch["series"]:
                                if sr.get("color") == sc_col and sr.get("label"):
                                    bd["value"] = sr["label"]
                    uris[aid] = dock_uri(ap)
                docks.append(dock_entry(aid, slot, enter, exitt, len(d["badges"]),
                                        evidence[aid].get("kind", DOCK_KIND_IMAGE),
                                        eplace, dopt.get("arrive"), dopt.get("mass"), centred,   # a centred card is placed on either slot (2026-09-10: two cards up at once)
                                        read_place=rplace, read_s=dopt.get("read_s"), park_s=dopt.get("park_s"),
                                        press=dopt.get("press"), stack=bool(dopt.get("stack")),
                                        behind=dopt.get("behind"), fg=fg_key, embed=embed, rid=dock_row_id(sid, aid),
                                        depth=dopt.get("depth"),   # P58 T6 (a): the plane the card stands on
                                        read_moved=e63.get("read_moved"), read_deferred=bool(e63.get("read_deferred")),
                                        cutout=bool(dopt.get("cutout")),
                                        prop=bool(dopt.get("prop")), ink=dopt.get("ink"),   # E99 s87: the bare payload and how its art is laid down
                                        ring_to=ring_fit["ring_to"] if ring_fit else None,   # R26-20 send-back: the ring as the room holds it
                                        from_to=ring_fit["from_to"] if ring_fit else None,   # ... and the approach
                                        paint=ring_fit["paint"] if ring_fit else None))   # ... and its painted extent
        assign_press_stack(docks)   # P50 T3: the scene's press pile, in enter order
        try:
            _pg = (world or {}).get("page") if isinstance((world or {}).get("page"), dict) else None
            _changed = world_key(world) != world_key(prev_world) if i > 0 else False   # the first row has no boundary
            exit_id, exit_s = scene_exit(authored_exit, bool(docks), (_pg or {}).get("enter"), _changed)
            prev_world = world
        except ValueError as exc:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
        camera = dict(row_camera) if row_camera is not None else camera_identity()   # a COPY: one CAM_ROW dict is shared by many rows
        camera["id"] = camera_row_id(sid)   # P51 T5: `<scene>.camera` - the key a null in the sidecar turns this camera off by
        scene = {
            "scene_id": sid,
            # Ken Burns is AUTHORED per shot in the table, not one constant.
            "world": world,
            "exit": exit_id,
            "span": [round(a, 2), round(b, 2)],
            "docks": docks,
            # the row's targeted species, verbatim: the player resolves each
            # declared target to pixels at render time (resolveTarget), the
            # motion gate counts their events per the s9.27 gate column
            "species": row_species,
            "camera": camera,   # P49 T1: identity unless the row authored keys
        }
        # E47: a timed exit publishes its length so the motion gate credits the right
        # window without re-parsing the name; a bare `dip` leaves the gate on DIP_S.
        if exit_s is not None:
            scene["exit_s"] = exit_s
        # E63: the windows the chart DRAWS in (the page's own build, each build_to). Since the widening they decide
        # nothing - a card never reads over the plot, drawing or finished - but they are still published, because
        # they are how M27 and the compiled entry SAY which frame it was, against the compiler's own clock rather
        # than a DOM proxy (the probe's marks.drawn averages every drawn path and reads 0.52 on a finished line
        # whose second path is a stub by design). Absent on a row with nothing to draw.
        bw = page_build_windows(world, row_species, a)
        if bw:
            scene["build_windows"] = [[round(x, 2), round(y, 2)] for x, y in bw]
        lw = page_line_windows(world, row_species, a)   # R26-226: one window per DRAWING series (a series a build_to holds at index 0 takes no turn)
        if lw:
            scene["build_lines"] = [[round(x, 2), round(y, 2)] for x, y in lw]
        scenes.append(scene)

    # P53 T2 / R26-60: the two defaults a world-taking transition implies, stamped now that both sides of every
    # boundary are visible - and printed, because a default nobody can see is a default nobody can argue with
    for _note in stamp_transition_pages(scenes) + stamp_tip_marks(scenes):
        print(f"  transition  : {_note}")
    # R26-231: page exits and chart-to-chart continuity are final only after the
    # transition pass.  Reject an authored page clock here, before anything is
    # written, so an exit=cut stamp can legitimately remove the retract only.
    try:
        validate_page_build_spans(scenes)
    except ValueError as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
    # T19: a surface page is bound only after every row has its finalized span and
    # camera. Ordinary pages take the empty path and remain byte-identical.
    try:
        for _note in bind_surface_page_arrivals(scenes, EP):
            print(f"  surface    : {_note}")
    except ValueError as exc:
        raise SystemExit(f"FAIL: {exc}") from exc

    # P50 T16: the build says whose numbers it placed by. A page the fixture has not measured is placed
    # by `ledger_page`'s ESTIMATE of the player's layout - good enough to park a card against the plot's
    # edge (E45 parks from the title side), never good enough to centre one in a band (R26-27).
    if read_moves or read_defers:
        # E63: the reads the rule re-placed, and the ones it deferred to the parked box. Named, never silent.
        print(f"  dock read   : {len(read_moves)} read(s) moved off a building chart"
              + (f" ({'; '.join(read_moves[:4])})" if read_moves else "")
              + (f", {len(read_defers)} deferred to the parked box ({'; '.join(read_defers[:4])})" if read_defers else "")
              + " (E63)")
    if estimated_pages:
        print(f"  page boxes  : {len(estimated_pages)} page(s) ESTIMATED, not measured - "
              f"{'; '.join(estimated_pages)}. Measure them into assets/page-boxes.v1.json "
              "(measure_page_boxes.py) to place them by the player's own boxes.")
    elif ledger_rows:
        print(f"  page boxes  : {len(ledger_rows)} page(s) MEASURED - every card placed by the player's own boxes")
    if card_rooms:
        # E65: the room every card took - outside the plot, the plot's own empty room, the axis band
        # underneath, or the corner at the legibility floor (which warns).
        print("  card place  : " + "; ".join(f"{rid} {room} {box}" for rid, room, box, _t in card_rooms))
        floored = [(rid, title) for rid, room, _b, title in card_rooms if room == "corner"]
        if floored:
            print(f"  [WARN] E65: {len(floored)} card(s) found no room on the page and took the emptiest corner at "
                  "the legibility floor - " + "; ".join(f"{rid} on {title!r}" for rid, title in floored)
                  + ". Give the page room (a shorter title, a parked chart) or place the card by hand.")

    # caption STAGE mode: stamp each page with the mode it takes at its first word (after the scenes exist).
    # R26-205: a dock holding the stage anchors it as it always has, and at 16:9 so does a LEDGER PAGE row -
    # the page's chart is the whole stage there, so there is no column left to put a stage caption in.
    pages = [{**pg, "cap_mode": "anchor" if (_dock_live_at(scenes, pg["s"])
                                             or _full_stage_page_at(scenes, pg["s"], ASPECT)
                                             or (ASPECT == "16:9" and _readable_species_during(scenes, pg["s"], _caption_display_end(pages, i)))) else "stage"}
             for i, pg in enumerate(pages)]
    pages = [{**pg, **({"cap_reserve": "readable-species"}
                      if ASPECT == "16:9" and _readable_species_during(scenes, pg["s"], _caption_display_end(pages, i))
                      else {})} for i, pg in enumerate(pages)]
    # P52 T10: and the ARRIVAL each page's words take, beside the mode - absent when the build says nothing,
    # which is the pop (the field cannot appear in a timeline compiled before this slice, nor in one after it
    # that never asks; that absence is the byte-identity of every golden and both shorts)
    if _caption_arrive():
        pages = [{**pg, "cap_arrive": _caption_arrive()} for pg in pages]
    # P57 T14 / E90: and the LIFE each page's words carry, beside the arrival - written only when the build asks,
    # for exactly the same reason (an absent field is the shipped caption, and no build on disk carries one)
    if _caption_life():
        pages = [{**pg, "cap_life": _caption_life()} for pg in pages]
    # E62: and the BAND each card leaves the caption free - the demotion under a card is in position,
    # not in size. A dock whose window carries a caption takes `caption_band`; null means no band
    # holds a two-line strip clear of the card and of the data, and the player takes the quiet anchor.
    banded = stamp_caption_bands(scenes, pages, ASPECT)
    stamped = [d for sc in scenes for d in sc.get("docks", []) if "caption_band" in d]
    if stamped:
        chosen: dict[str, int] = {}
        for d in stamped:
            key = d["caption_band"]["band"] if d.get("caption_band") else "quiet-anchor"
            chosen[key] = chosen.get(key, 0) + 1
        print(f"  caption band: {banded}/{len(stamped)} dock window(s) keep the stage caption "
              f"({', '.join(f'{k} x{v}' for k, v in sorted(chosen.items()))})")
    # R26-201 / E99 s80 (3): and the band a CAMERA MOVE leaves the caption free - the same demotion, for the
    # move. A 16:9 page row's caption is already anchored (R26-205), so this speaks on a 9:16 page's stage
    # caption; at 16:9 the ceiling is the page's (`camera_zoom_errors`, refused at the row).
    yielded = stamp_camera_caption_bands(scenes, pages, ASPECT)
    yield_windows = [w for sc in scenes for w in sc.get(CAPTION_YIELD_KEY, [])]
    if yield_windows:
        print(f"  caption yield: {yielded}/{len(yield_windows)} camera window(s) move the caption rather than shrink it - "
              + "; ".join(f"{w['move']} {w['from']}-{w['to']}s -> "
                          + (f"band {w['caption_band']['band']} y{w['caption_band']['y']}" if w["caption_band"]
                             else "the quiet anchor (no band holds)") for w in yield_windows[:4]))
        intruded = [w for w in yield_windows if w.get("in_strip")]
        if intruded:
            print(f"  [WARN] E99 s80 (3): {len(intruded)} camera window(s) still push a page element into the caption's "
                  "strip - " + "; ".join(f"{w['move']} at {w['from']}s: the {w['in_strip']['element']} "
                                         f"{w['in_strip']['px']}px in" for w in intruded[:4])
                  + ". The caption has no band to yield to on this page: ANCHOR the move (a key's `at`, lifting the "
                  "look until the foot clears) or PARK the page (E61) - or the move stays out.")
    uris["__audio__"] = data_uri(audio)

    # SOUND REVIEW LAYER (operator, 2026-08-31: "i can't judge the audio
    # without also seeing what actions are happening on the screen") -
    # cues from sound/SOUND-PLAN.json embed as data URIs; the player
    # schedules them on the master clock with live A/B variant toggles.
    sound_cues = []
    sp_path = EP / "sound/SOUND-PLAN.json"
    if sp_path.exists():
        plan = json.loads(sp_path.read_text(encoding="utf-8"))
        for ci, cue in enumerate(plan.get("cues", [])):
            variants = {}
            for vk, fname in cue.get("variants", {}).items():
                fp = EP / "sound" / fname
                if fp.exists():
                    key = f"__snd_{ci}_{vk}__"
                    uris[key] = data_uri(fp)
                    variants[vk] = key
            if variants:
                sound_cues.append({"slot": cue["slot"], "at": cue["at"],
                                   "gain": cue.get("gain", 0.5),
                                   "fade_in": cue.get("fade_in", 0),
                                   "env": cue.get("env", []),   # [[t, dB], ...] against the cue's gain - the bed breathes (rule 3 of the bed blueprint)
                                   "variants": variants})
        print(f"  sound cues  : {len(sound_cues)} embedded from SOUND-PLAN.json")

    timeline = {
        "schema_version": "scene_evidence_timeline.v1",
        "runtime_s": tl["runtime_s"],
        "title": TITLE,
        "subtitle": SUBTITLE,
        "episode_id": EPISODE_ID, "project_id": "systems-and-blowups",
        **({"form": CONTENT_FORM} if CONTENT_FORM is not None else {}),
        **({"aspect": ASPECT} if ASPECT else {}),
        "narration": {"canonical_hash": sha(audio),
                      "words_path": f"{BUILD.name}/timeline.json"},
        # Block captions for the template's own layer; the kinetic layer reads
        # caption_pages. Both carry CANONICAL timings — never resampled onto
        # beat boundaries (doc 29 Part 5, and the standing correction).
        "captions": [{"at": p["s"], "until": p["e"],
                      "text": " ".join(t["w"] for t in p["t"])} for p in pages],
        "caption_pages": pages,
        # caption STAGE mode (doc 29 s9.25 #2, P34 T5): the player centres and pops
        # the caption whenever no dock is up; each page declares the mode it will
        # take at its first word so the motion gate can count stage pages as events
        # and FAIL a still stretch that carries none.
        "caption_modes": ["stage", "anchor"],
        # P52 T10: the ARRIVAL the stage words take, for a player reading the timeline rather than a page
        # (a page's own `cap_arrive` wins). Omitted entirely when the build does not ask - see CAPTION_ARRIVE.
        **({"caption_arrive": _caption_arrive()} if _caption_arrive() else {}),
        # P57 T14 / E90: the LIFE the stage words carry (a page's own `cap_life` wins). Omitted entirely when the
        # build does not ask - see CAPTION_LIFE.
        **({"caption_life": _caption_life()} if _caption_life() else {}),
        "sound": sound_cues,
        "evidence": evidence,
        "scenes": (extend_camera_cards(scenes) and scenes) or scenes,   # P49 T5: a camera page's card stays up to the match
        # every species present (the ledger world + the targeted kinds), so
        # downstream (gate, render) can see it
        "species": timeline_species(scenes),
        "kinetics": build_kinetics(),   # the template's capability flags this build turns on (P39: default all off; E49: the idle on)
        # P51 T5: the sidecar's own receipt - which row ids a human or a flash agent edited into this build.
        # Absent when nothing was layered, so a build with no sidecar is byte-for-byte what it was.
        **({"overrides_applied": applied} if applied else {}),
        **({"caption_style": CAPTION_STYLE} if CAPTION_STYLE else {}),
    }
    # P51 T1: the SPLIT form. write_split writes the compiled timeline (byte for byte what this
    # line always wrote), assets.json, a copy of the engine module and the shell that fetches them,
    # plus player.json naming the engine's sha - so a build dir holds a ~46 KB page, not a 32 MB one,
    # and a served build says which engine it is running.
    import render_baseline as _RB
    uris = {**uris, **longform_assets(timeline)}   # P69 T8: the long form's face, only when a page asks for it
    out = _RB.write_split(BUILD, timeline, uris, TIMELINE_NAME, template=TEMPLATE)

    dur = float(subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio)], capture_output=True, text=True).stdout or 0)
    print(f"scene_evidence_timeline.v1")
    print(f"  scenes      : {len(scenes)}  (one per world plate)")
    print(f"  species     : {timeline['species'] or 'none'}  "
          f"({sum(1 for s in scenes if s['world'].get('kind') == SPECIES_LEDGER)} ledger pages)")
    print(f"  docks       : {sum(len(s['docks']) for s in scenes)} across "
          f"{sum(1 for s in scenes if s['docks'])} scenes")
    print(f"  evidence    : {len(evidence)} assets")
    print(f"  captions    : {len(timeline['captions'])} lines / "
          f"{sum(len(p['t']) for p in pages)} tokens")
    print(f"  audio       : {dur:.2f}s embedded as __audio__")
    print(f"  URIs        : {len(uris)} fetched from {(BUILD / _RB.ASSETS_NAME).stat().st_size/1e6:.0f} MB "
          f"{_RB.ASSETS_NAME}, {out.stat().st_size/1e3:.0f} KB player + {(BUILD / _RB.ENGINE.name).stat().st_size/1e3:.0f} KB engine")
    print(f"  wrote {out}")

    # THE PLATE CADENCE, measured. Two pieces per plate with two badges each,
    # or one big piece - never a pair padded out to make a count. This reports
    # against the pattern; it does not author it.
    thin = [(s["span"][0], round(s["span"][1] - s["span"][0], 1),
             len({d["slide"] for d in s["docks"]}))
            for s in scenes if s["span"][1] - s["span"][0] >= 12.0]
    off = [x for x in thin if x[2] == 1]
    nb = [a for a, e in evidence.items() if not e["badges"]]
    per = [len({d["slide"] for d in s["docks"]}) for s in scenes]
    print("")
    print(f"  CADENCE  {per.count(2)} plates carry a pair, "
          f"{per.count(1)} carry one, {per.count(0)} carry none")
    if off:
        print(f"  [WARN] {len(off)} plates hold >=12s on a single piece - pair "
              f"them or let the solo card go wide:")
        for a, d, _ in off[:6]:
            print(f"           {int(a//60)}:{int(a%60):02d}  {d}s")
    if nb:
        print(f"  [WARN] {len(nb)} evidence cards carry no badges - their whole "
              f"information layer is blank: {', '.join(nb[:4])}"
              f"{' ...' if len(nb) > 4 else ''}")
    motion_gate_report()
    return 0


def motion_gate_report() -> int:
    """E21 / doc 29 s9.25: every compiled timeline gets the motion-density
    gate run on it and the verdict written to build-f/GATES-MOTION.md. The
    build still completes on FAIL - the shot table is authored against the
    report - and render_episode.py refuses a full render while it says FAIL."""
    path, n_fail = MG.write_report(BUILD, TIMELINE_NAME)
    print("")
    print(f"  motion gate : {path}")
    if n_fail:
        print(f"MOTION GATE: {n_fail} FAIL - see {MG.REPORT_NAME}")
    else:
        print("MOTION GATE: PASS")
    return n_fail


if __name__ == "__main__":
    raise SystemExit(main())

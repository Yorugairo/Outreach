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

import base64
import io
import hashlib
import copy
import functools
import json
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
LEDGER_ENTERS = ("spiral", "mount", "morph", "snap", "built", "throw", "drop", "camera")   # enter=camera=<dock>: P49 T5 - the page arrives BUILT and the EYE goes to the landed card (the camera zooms the outgoing world and the card until the card fills the stage, then the world is the page) - the snap's opposite number, opt-in until HG2   # enter=drop: the page FALLS into the frame from above and lands as the world (the dock's landXf) - "is falling down into the frame easier?" (operator, 2026-09-08)   # enter=throw (2026-09-08): the whole page is THROWN onto the world and arrives built - the transition IS the plate entering the world   # enter=built: the page ARRIVES with its chart already drawn, by the row's own transition - it NEVER mounts (operator, 2026-09-08: mount is cream coming through over the scene, then drawing).
# The build is a device, not an obligation - five builds in one short is repetition, and a page that arrives complete spends
# its whole span being read instead of being drawn (operator, 2026-09-08: "maybe chart 1 doesn't actually need a build, it
# could enter built, the deconstruction/transformation is its own thing"). E49 keeps it alive; the transformation is the
# motion. Unlike `spiral` this carries no RETURN meaning - it is for a chart's first appearance.   # enter=snap=<dock asset>: the page arrives BUILT, grown from that landed card's rectangle to the stage (the third watch, 2026-09-07)   # enter=morph[=<s>]: the page's prop outline (world.morph) becomes the chart by ARAP (P47 T3); enter=spiral: the page RETURNS - unwinds from its point, no roll/soak/ink/build (E25; 2026-09-05)
                                      # enter=mount: no roll-out - the outgoing scene fades while the cream plate MOUNTS over it, then the page draws (operator, 2026-09-05)
KINETICS: dict = {}                # timeline.kinetics - the template's capability flags a build turns on (P39 kill switch; default all off)
CAPTION_STYLE: str | None = None   # timeline.caption_style - "phrase" on a short: the page lands as one readable phrase, only k-words punctuated (2026-09-05)
LEDGER_EXITS = ("cut",)            # exit=cut: no retract - the page leaves on the cut (for a beat that must land on the last line, E40 #5)
SPECIES_LEDGER = "ledger"          # timeline["species"] entry; the player keys on world.kind == "ledger"

# SCENE EXITS (ruling E47, operator 2026-09-06). `exit` names the transition INTO the scene it
# sits on - the player's law for the wipe, the suck and the dissolve alike. The two world-change
# transitions off the measured reference (doc 46 s46.5) join the kit and take the mechanical
# default; the carried-light cross-reveal stays reachable BY NAME as an effect and is the default
# nowhere ("we made it the default because it worked, but we need a better default, and it can be
# an effect at that point"). dip and blurzoom may carry their own length: `dip:<s>`, `blurzoom:<s>`.
SCENE_EXITS = ("cut", "dip", "blurzoom", "dissolve", "wipe", "wipe_right", "suck")
IDLE_KINDS = ("none", "breath", "drift", "pulse", "figure", "live")   # live (2026-09-08): breath + drift - the breath has a fixed point at the centre, so a chart at the page centre read as still; the drift moves every pixel   # E49 / P47 T5: the player's named idles; `;idle=<kind>` on any plate id (`none` is explicit stillness)
IDLE_OPT = ";idle="
ARRIVALS = ("spring", "throw", "land")            # P47 T1: how a dock or a page's pills ARRIVE (spring = E45's pop, the default)
MASSES = ("paper", "metal", "liquid", "ink")      # P47 T1: the material presets (stopaction.mjs MASS) a throw or a landing settles by
MORPH_SHAPES = ("tab", "plate", "card")           # P47 T3: the named prop outline a morph page starts from (`;morph=<shape>`; tab is the default)
PLATE_USES = ("landing", "bridge", "reset")   # E61: the three things a plate is - a landing surface, a bridge, a reset; `;use=<one>` names it on the row
PLATE_OPTS = ("idle", "arrive", "mass", "morph", "then", "card", "use", "pill", "thread")   # thread=<mark key>: HF-16 - ONE mark of the page before this one survives the cut and is the arriving page's ground (P50 T15)   # pill=yes|no|<datum index>: R26-34's tip-riding pill on a dense-line page, popping at that datum (P50 T11)   # card=yes|no: a ledger page keeps the card's rounded corners and a hard-edge shadow at full size (2026-09-08; a snapped page is a card by default)  # the `;key=value` options a plate id may carry
# P48 T4: `;then=<series>:<variant>[:<emphasize>]` names ANOTHER chart the same page can become - a second full
# ledger_page.v1 spec on `world.page_states`, built at load and hidden until a `chart_to` reaches it. Repeat the
# option for a third. STATE_MAX bounds it: a fourth chart is a new page or a card, and the reader's memory says so.
STATE_MAX = 3
DOCK_OPTS = ("arrive", "mass", "centre", "card_aspect", "centre_w", "centre_band", "centre_y", "centre_x", "read", "read_s", "park_s",
             "press", "stack", "behind", "embed")   # P50 T7: embed=<name> - the card lands ON a surface the plate declares (a poster, a screen, a paper), projected onto its four measured corners   # P50 T15 / HF-17: behind=<layer> - the world plate's foreground cutout paints OVER this card (the depth cue by occlusion, not blur)   # P50 T3: press = the card meta press_card.py wrote (or its path) - the dock is a PRESS CARD; stack = it joins the scene's press pile (the push hand-off, doc 29 s9.27)   # the optional 5th element of a shot row's dock tuple: a dict of these; centre: True parks the card centred on the page; card_aspect: the card's h / w (a chart card), so the centred box is the card's own
CENTRE_MAX_H = 0.58                                 # a centred card takes at most this share of the stage height (the page's title and source stay in view)
CENTRE_W = 0.74                                     # a centred card's width as a share of the stage - the reading size, not the parked card's
CENTRE_BAND = 0.64                                  # ... and is centred in the band ABOVE the caption strip (which sits at ~0.64-0.70 of a portrait stage), never under it
TIMED_EXITS = ("dip", "blurzoom")   # ... and only these two read the suffix as SECONDS (suck's is a point)
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
HOLD_MIN_S = 1.0   # a held species with less room than this before the next event is dropped, not flashed (2026-09-08) [DERIVED: E25 - a light that cannot hold its sentence has nothing to prove]
PAGE_SPECIES = ("build_to", "bracket", "retitle", "relight", "undraw", "figure", "note", "spread", "peel", "chart_to",
                 SPECIES_SPAN, SPECIES_CROSS)   # P50 T4: a span is a page species - it is shaded behind the page's own chart, on the page's own clock and live scale (R26-28)
CHART_TO_KINDS = ("recast", "rescale", "extend", "park", "morph")   # P48: recast (T4, a hand-over; keyed: T4b), rescale (T2), extend (T3), park (T2b: the chart makes room by one affine transform), morph (T5: the area under the line becomes the target's by ARAP)
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
    "chart_to": "the sentence needs the SAME data at another scale / with more of it / in another form / beside a card - the page changes state (E58; CHART_TO_WHEN names the verb); never a cut to a second chart of it",
}
CHART_TO_WHEN = {
    "recast": "the same data in another form: keyed (n lines -> n bars by series, 'where the four stand today'; RECAST_PAIRS) or the hand-over (a line into the monthly bars, into a pie of the holders)",
    "rescale": "the same series at another scale - 'since February', 'at full width': the window the story is about; never a window that drops the sentence's point",
    "extend": "more of the same series ('and then May') or a later series of the same file ('then consumption') - drawn on at the pen",
    "park": "room for the next thing beside the chart (a card, a second diagram); scale 1.0 is the UN-PARK when the cards leave; it moves no data and restarts no clock",
    "morph": "a different LINE series in the same frame ('what the Fed charges against what America pays') - the area under the line becomes the target's by ARAP",
}
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
    "build_to": ("datum",), "bracket": (), "retitle": (), "relight": (),   # P47 T2: the datum is the cap; the others carry their own fields
    "undraw": ("datum",), "figure": ("datum",), "note": (), "spread": (), "peel": (), "chart_to": (),   # E50; peel names no datum: the slice it pulls is the one the PAGE declared (page.peel.index), so the chart and the claim cannot disagree; spread names its two series, not a datum: the datum the line unwinds back to (0 = nothing); the datum the figure is pinned to
}
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
    if tk == "datum" and "series" in target and not isinstance(target["series"], int):
        errs.append(f"{kind}: target datum 'series' must be an integer series index")
    if tk == "span" and not errs and target["from_word"] > target["to_word"]:
        errs.append(f"{kind}: target span from_word > to_word")
    return errs


def _validate_page_fields(kind: str, entry: dict) -> list[str]:
    """P47 T2: the page species' own fields. bracket: integer `from`/`to` (data indices), a `label`, optional `sub`,
    `series`, `color`; retitle: a non-empty `text`; relight: `ref` bracket|title, optional `index`."""
    errs: list[str] = []
    is_idx = lambda v: isinstance(v, int) and not isinstance(v, bool) and v >= 0
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
    """P50 T2: a chip carries a SOURCED glyph and a label, and its cross falls on a LATER word."""
    errs: list[str] = []
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
    if entry.get("kind") == SPECIES_CHIP:
        return [entry["icon"]] if isinstance(entry.get("icon"), str) else []
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


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def parse_ledger_id(plate_id: str) -> tuple[str, str, int | None, str, str | None, str | None]:
    """``ledger:<series>:<variant>[:<emphasize>[:<quiet_zone>[:<enter>[:<exit>]]]]`` -> its parts.
    enter: ``spiral`` (the page returns by the vortex) or ``mount=<seconds>`` (the world fades above the page while its
    cream builds beneath, for that long, then the page draws - doc 29 s9.31); exit: ``cut`` (no retract).
    ValueError names the id; the caller names the row."""
    parts = plate_id.split(":")
    lo, hi = LEDGER_ID_PARTS
    if parts[0] != LEDGER_PREFIX[:-1] or not (lo <= len(parts) <= hi) or not parts[1]:
        raise ValueError(f"{plate_id!r}: expected ledger:<series-id>:<variant>[:<emphasize>[:<quiet_zone>[:spiral|mount=<s>[:cut]]]]")
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


def parse_exit(exit_id: str) -> tuple[str, float | None]:
    """``cut`` | ``dip[:<s>]`` | ``blurzoom[:<s>]`` | ``wipe_right`` | ``suck:<x>,<y>`` -> (name, seconds or None).

    Only dip and blurzoom read the suffix as a length; the suck's is the point it collapses into,
    and every other exit is a bare name. ValueError names the exit; the caller names the row."""
    name = str(exit_id).split(":")[0]
    if name not in SCENE_EXITS:
        raise ValueError(f"exit {exit_id!r} is not one of {'|'.join(SCENE_EXITS)}")
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
    return LPG.build_spec(series, variant, emph)


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
    if builder not in ("dense-line", "story"):
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
    return spec


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
            derived, key_map, _why = derive_recast_key(A, Bs)
            sp["keyed"] = derived
            where = f"{sid or 'row'} chart_to recast at {sp.get('at')}"
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
        page["enter"] = enter.split("=")[0]   # the player: a returning page unwinds from its point (LP_RETRACT.IN); a mount builds its cream first
        if "=" in enter and (enter.startswith("snap") or enter.startswith("camera")):
            page["snap_from"] = enter.split("=", 1)[1]   # the dock asset the page grows from - or, for enter=camera, the card the eye goes to (P49 T5)
        elif "=" in enter and enter.startswith("throw"):   # throw=<grow>[,<from>[,<s>]] - the growth law (snap | depth), the side, the flight
            grow, *rest = enter.split("=", 1)[1].split(",")
            if grow not in ("snap", "depth"):
                raise ValueError(f"{plate_id!r}: throw grow {grow!r} is not snap|depth")
            page["throw_grow"] = grow
            if rest and rest[0]:
                if rest[0] not in ("below", "above", "left", "right"):
                    raise ValueError(f"{plate_id!r}: throw side {rest[0]!r} is not below|above|left|right")
                page["throw_from"] = rest[0]
            if len(rest) > 1 and rest[1]:
                page["throw_s"] = float(rest[1])
        elif "=" in enter:
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
    allowed = {"idle": IDLE_KINDS, "arrive": ARRIVALS, "mass": MASSES, "morph": MORPH_SHAPES,
               "card": ("yes", "no"), "use": PLATE_USES}[key]
    if value not in allowed:
        raise ValueError(f"{where}: {key} {value!r} is not one of {'|'.join(allowed)}")


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
        opts[k] = v
    return bare, opts


def split_idle(plate_id: str) -> tuple[str, str | None]:
    """The idle option alone (E49) - see split_plate_opts."""
    bare, opts = split_plate_opts(plate_id)
    return bare, opts.get("idle")


PHRASE_KEYS = ("x0", "y0", "x1", "y1")


def press_meta(raw) -> dict:
    """A PRESS dock's card meta: the dict ``press_card.py`` wrote, or the path to that JSON.

    Returns only what the player needs - the kind, the source line and the phrase box - so the
    provenance keys the tool also writes (the crop rectangle, the screenshot's sha256) stay on disk
    and out of the timeline. ValueError names the option; the caller names the row and the dock."""
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
    return {"kind": DOCK_KIND_PRESS, "source": src.strip(),
            "phrase": {k: round(float(ph[k]), 5) for k in PHRASE_KEYS}}


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


def embed_entry(name: str, spec: dict, words=None, card_aspect: float | None = None) -> dict:
    """What the dock carries onto the timeline: the surface's name, its quad, the SECOND the room dims on, and
    the card PICTURE's aspect (so the player can letterbox the card on the surface without measuring it).

    `darken` is authored as the word (the plate's manifest speaks the script's language, as every shot row does) and
    resolved here against the build's own words, so the player never has to find a word at render time."""
    quad = [[round(float(x), 5), round(float(y), 5)] for x, y in spec["quad"]]
    out = {"name": name, "quad": quad}
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
        if k == EMBED_KEY:   # P50 T7: the plate's surface this card lands ON; the plate and the quad are checked at the row
            if not isinstance(v, str) or not v.strip():
                raise ValueError("dock: embed must NAME a surface the scene's plate declares (<plate>.layers.json)")
            continue
        if k == "centre":
            if v is not True:
                raise ValueError("dock: centre must be True (the card parks centred on the page)")
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
    out = dict(raw)
    if "press" in out:
        out["press"] = press_meta(out["press"])   # a path resolves here, so every caller downstream sees the dict
    elif out.get("stack"):
        raise ValueError("dock: stack is the PRESS stack - it belongs to a dock that carries `press` (the push hand-off, doc 29 s9.27)")
    if out.get(EMBED_KEY) and out.get("stack"):   # P50 T7: a card on a surface has no pile - the surface is the park
        raise ValueError("dock: embed and stack are two different arrivals - a card that lands ON a surface is not "
                         "pushed into a pile (E45's park is the surface itself)")
    return out


def world_for_plate(plate_id: str, ken: tuple, ep_dir: Path, meta: dict | None = None) -> dict:
    """A scene's ``world`` for a shot-table plate id, with E49's ``;idle=<kind>`` option stripped off and carried
    as ``world["idle"]`` (the player reads it for the page or the plate; absent = the class default)."""
    bare, opts = split_plate_opts(plate_id)
    world = _world_for_bare_plate(bare, ken, ep_dir, meta)
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
    pill = opts.pop("pill", None)
    if pill is not None and pill != "no":
        # P50 T11 (R26-34): the tip-riding pill is a LINE PAGE's option and it is the ROW's word, not the object's -
        # the evidence object carries the data (AXES_KEYS); how this shot draws it is the plate id's, as `card=` is.
        # It rides the DRAW, and the beats that drive the draw (build_to) are declared on the same row.
        if world.get("kind") != SPECIES_LEDGER or (world.get("page") or {}).get("builder") not in MORPH_BUILDERS:
            raise ValueError(f"{plate_id!r}: pill= is a DENSE-LINE page option - the pill rides a line's drawing tip "
                             f"(this page is {((world.get('page') or {}).get('builder') or world.get('kind') or 'a plate')!r})")
        world["page"]["tip_pill"] = True if pill == "yes" else {"milestone": int(pill)}
    world.update(opts)   # idle (E49), arrive / mass (P47 T1), use (E61) - written only when the row names them
    if thens:   # P48 T4: the other charts this page can become, each a full spec built at load
        if world.get("kind") != SPECIES_LEDGER:
            raise ValueError(f"{plate_id!r}: then= is a LEDGER PAGE option: only a page has chart states")
        if len(thens) > STATE_MAX - 1:
            raise ValueError(f"{plate_id!r}: {len(thens) + 1} chart states is past STATE_MAX ({STATE_MAX}): "
                             "a fourth chart is a new page or a card")
        world["page_states"] = [_page_state(t, ep_dir, repr(plate_id)) for t in thens]
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


def free_bands(boxes: dict) -> list[dict]:
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
    foot = min(safe["y"] + safe["h"], cap["y"])
    ink_foot = max(src["y"] + src["h"], rail["y"] + rail["h"])
    bands = {
        "above": (left, head, right - left, plot["y"] - head),
        "below": (left, plot["y"] + plot["h"], right - left, src["y"] - plot["y"] - plot["h"]),
        "foot": (left, ink_foot, right - left, foot - ink_foot),
        "left": (left, head, plot["x"] - left, foot - head),
        "right": (plot["x"] + plot["w"], head, right - plot["x"] - plot["w"], foot - head),
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


def page_place(page: dict, aspect: str) -> dict:
    """The parked rectangle for a dock on this ledger page, in stage pixels (E45 §1, E65).

    ``{"x", "y", "w", "h", "room"}`` - ALWAYS: `room` is which of E65's four rooms it came from
    (`outside` | `empty` | `axis` | `corner`). Pure: the page spec is never mutated."""
    boxes = LPG.page_boxes(page, aspect)
    stage_w = boxes["stage"]["w"]
    want = round(DOCK_ON_PAGE_W * stage_w)
    quiet = boxes.get("quiet_zone")
    floor_h = _floor_h(aspect)
    # (1) OUTSIDE: a band the page's ink leaves free - E45 §1, unchanged
    best = None
    for band in free_bands(boxes):
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
    for room in mask_rooms(boxes):
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
    if under:
        fit = _fit_in(under, want, floor_h)
        if fit:
            w, h = fit
            box = _corner_box(under, w, h, quiet, centre)
            if mask_is_clear(boxes, box):
                return {**box, "room": "axis"}
    # (4) THE CORNER, at the floor - and the build warns (the caller reads `room`)
    corner = emptiest_corner(boxes)
    w = _card_w_for(floor_h)
    h = dock_card_h(w)
    return {**_corner_box(corner, w, h, quiet, centre), "room": "corner"}


def dock_place(world: dict, aspect: str | None) -> dict | None:
    """The placement every dock on this scene takes, or None on a plain plate (E45: "a dock on a
    plain plate keeps the solo card"). One rectangle per scene, from the page's geometry alone -
    and on a ledger page there is ALWAYS one (E65); the rectangle carries the `room` it came from."""
    if not isinstance(world, dict) or world.get("kind") != SPECIES_LEDGER or not world.get("page"):
        return None
    return page_place(world["page"], aspect or "16:9")


def centred_place(place: dict, aspect: str | None, card_aspect: float | None = None, page: dict | None = None,
                  centre_w: float | None = None, band_name: str | None = None, centre_y: float | None = None,
                  centre_x: float | None = None) -> dict:
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
    bands = [bd for bd in free_bands(LPG.page_boxes(page, aspect or "16:9")) if page and bd["band"] in ("below", "foot", "above")] if page else []
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
        got = page_place(page, aspect or "16:9")
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
CAPTION_HOME_BOTTOM = 480      # 9:16: the strip sits on `bottom: 480px` (G-l, y 1297-1440)
CAPTION_HOME_TOP = 0.40        # 16:9: the stage caption's own 40% band
CAPTION_SIDE_PAD = 120         # the stage caption's near margin beside a declared quiet zone
CAPTION_QZ_SPLIT = 0.58        # ... and the far one, as a share of the stage width


def caption_strip_h() -> int:
    """The stage caption's own height: two lines at the stage size, in stage pixels."""
    return round(CAPTION_STAGE_PX * CAPTION_LINE_H * CAPTION_LINES)


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


def caption_band(page: dict, aspect: str, cards: list[dict] | None) -> dict | None:
    """The band this page leaves free for the caption under `cards` (E62), or None.

    ``{"y", "h", "band"}`` in stage pixels - the strip's own rectangle and the candidate it came
    from. `cards` is every card box live in the dock's window (its parked `place`, and the reading
    box when the row named one); None means a card whose box the compiler does not know, and the
    answer is None - the caption takes the quiet anchor rather than guess. Pure: nothing is mutated."""
    if cards is None:
        return None
    boxes = LPG.page_boxes(page, aspect)
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
            band = caption_band(page, asp, dock_card_boxes(sc.get("docks", []), d["enter"], d["exit"])) if page else None
            d["caption_band"] = band
            placed += bool(band)
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


def dock_entry(aid: str, slot: int, enter: float, exitt: float, n_badges: int,
               kind: str = DOCK_KIND_IMAGE, place: dict | None = None, arrive: str | None = None, mass: str | None = None,
               centre: bool = False, read_place: dict | None = None, read_s: float | None = None, park_s: float | None = None,
               press: dict | None = None, stack: bool = False, behind: str | None = None, fg: str | None = None,
               rid: str | None = None, read_moved: dict | None = None, read_deferred: bool = False,
               embed: dict | None = None) -> dict:
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
        "enter": round(enter, 2), "exit": round(exitt, 2),
        "badge_at": [round(enter + 0.75 + 1.3 * (n + 1), 2) for n in range(n_badges)],
        **({"kind": DOCK_KIND_VIDEO} if kind == DOCK_KIND_VIDEO else {}),
        # P50 T3: a PRESS card carries its source line and its quoted phrase onto the stage; `_stack` is the
        # scene's own bookkeeping and is replaced by stack_index / stack_n once every dock on the scene is known
        **({"kind": DOCK_KIND_PRESS, "source": press["source"], "phrase": press["phrase"],
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


def build_kinetics() -> dict:
    """The flags a compiled timeline carries. P39: every capability defaults OFF in the template. E49 (P47 T5): the
    IDLE is on for every timeline this compiler writes - a build that wants stillness says so (``KINETICS["idle"] =
    False``); the goldens' frozen sources carry no flag and stay byte-identical."""
    return {"idle": True, "stop_action": True, "arap_morph": True, "camera": True, **KINETICS}   # P47 T1: an authored `arrive` is the switch; the flag only guards the goldens; P49 T2: the camera is one state per frame (the species pixel-identical)


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
    dock = json.loads((BUILD / "evidence-dock.json").read_text(encoding="utf-8"))
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
        species_errors = validate_species(row_species, ken, plate, pivot_span=None, press_docks=row_press) + validate_camera_row(row_camera, row_species, plate, ASPECT)
        if species_errors:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): " + "; ".join(species_errors))
        # P50 T2: a chip's SOURCED glyph rides the asset map exactly as a plate or a dock still does,
        # keyed `icon:<name>` - the geometry travels in the player, never a path to a file on disk.
        for e in row_species:
            for _icon in species_icons(e):   # P50 T4: a flow's nodes and its swap ride the same route as the chip's one
                try:
                    uris[ICON_PREFIX + _icon] = icon_geometry(_icon)
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
        place = dock_place(world, ASPECT)
        for aid, slot, enter, exitt, *dextra in ds:   # P47 T1: an optional 5th element names how the card arrives
            try:
                dopt = dock_opts(dextra[0] if dextra else None)
            except ValueError as exc:
                raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s) dock {aid}: {exc}") from exc
            d = META.get(aid, {"title": aid, "source": "", "species": "deck",
                               "badges": []})
            auto_centre = solo_centre_by_clock(world, ASPECT, len(ds), slot, enter, a, dopt)   # R26-22: E50's clock centres a solo card on a MEASURED page
            centred = bool(dopt.get("centre")) or auto_centre
            dplace = centred_place(place, ASPECT, dopt.get("card_aspect"), (world or {}).get("page"), dopt.get("centre_w"), dopt.get("centre_band"), dopt.get("centre_y"), dopt.get("centre_x")) if (place and centred) else place   # the third watch: a card centred on the page
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
                    embed = embed_entry(dopt[EMBED_KEY], _embeds[dopt[EMBED_KEY]], tl.get("words"),
                                        dopt.get("card_aspect") or image_aspect(dock_asset_path(aid, EP)))
                except ValueError as exc:
                    raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s) dock {aid}: {exc}") from exc
            rd = dopt.get("read") or {}   # the box a centred card POPS at before it parks to dplace (2026-09-10)
            rplace = centred_place(place, ASPECT, rd.get("card_aspect", dopt.get("card_aspect")), (world or {}).get("page"), rd.get("centre_w"), None, rd.get("centre_y"), rd.get("centre_x")) if (place and rd) else None
            # E63 (widened): a card never READS over the page's plot, drawing or finished. The read box is the row's
            # own when it named one, the card's solo CSS box otherwise; a centred card with no `read` has no pop at all
            # (it takes its parked box from its first frame), so there is nothing to move and the entry is untouched.
            # The build windows are still handed over - for the RECORD in `why`, never for the decision.
            eplace = dplace if (slot == 0 or centred) else None
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
                        **({"kind": DOCK_KIND_VIDEO} if is_video_asset(ap) else {}),
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
                                        read_moved=e63.get("read_moved"), read_deferred=bool(e63.get("read_deferred"))))
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
        scenes.append(scene)

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

    # caption STAGE mode: stamp each page with the mode it takes at its first word (after the scenes exist)
    pages = [{**pg, "cap_mode": "anchor" if _dock_live_at(scenes, pg["s"]) else "stage"} for pg in pages]
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

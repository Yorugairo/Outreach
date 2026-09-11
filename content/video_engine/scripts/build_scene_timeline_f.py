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
PLATE_OPTS = ("idle", "arrive", "mass", "morph", "then", "card", "use")   # card=yes|no: a ledger page keeps the card's rounded corners and a hard-edge shadow at full size (2026-09-08; a snapped page is a card by default)  # the `;key=value` options a plate id may carry
# P48 T4: `;then=<series>:<variant>[:<emphasize>]` names ANOTHER chart the same page can become - a second full
# ledger_page.v1 spec on `world.page_states`, built at load and hidden until a `chart_to` reaches it. Repeat the
# option for a third. STATE_MAX bounds it: a fourth chart is a new page or a card, and the reader's memory says so.
STATE_MAX = 3
DOCK_OPTS = ("arrive", "mass", "centre", "card_aspect", "centre_w", "centre_band", "centre_y", "centre_x", "read", "read_s", "park_s",
             "press", "stack")   # P50 T3: press = the card meta press_card.py wrote (or its path) - the dock is a PRESS CARD; stack = it joins the scene's press pile (the push hand-off, doc 29 s9.27)   # the optional 5th element of a shot row's dock tuple: a dict of these; centre: True parks the card centred on the page; card_aspect: the card's h / w (a chart card), so the centred box is the card's own
CENTRE_MAX_H = 0.58                                 # a centred card takes at most this share of the stage height (the page's title and source stay in view)
CENTRE_W = 0.74                                     # a centred card's width as a share of the stage - the reading size, not the parked card's
CENTRE_BAND = 0.64                                  # ... and is centred in the band ABOVE the caption strip (which sits at ~0.64-0.70 of a portrait stage), never under it
TIMED_EXITS = ("dip", "blurzoom")   # ... and only these two read the suffix as SECONDS (suck's is a point)
DEFAULT_EXIT_DOCKS = "dip"          # E47 #3: was "wipe_right" until 2026-09-06
DEFAULT_EXIT_BARE = "cut"

TIMELINE_NAME = "steel-and-paper.timeline.json"  # the compiled scene_evidence_timeline.v1 the gate reads
# Per-episode overrides (Tokyo, 2026-09-04): another episode's build script imports this module,
# sets these, and calls main() - the compiler stays ONE thing rather than a fork per episode.
SHOT_TABLE_FILE = "SHOT-TABLE-F.py"
TITLE, SUBTITLE, EPISODE_ID = "Steel and Paper", "Money Physics · answer to Bravos Research", "steel-and-paper"
ASPECT = None                      # "9:16" for a short: the template reads timeline.aspect (html[data-aspect])
CLIP_PREFIX = "clip:"              # shot-table plate id for a CLIP world: clip:<path to a silent mp4>
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
SPECIES_CHIP = "chip"
SPECIES_KINDS += (SPECIES_CHIP,)   # P50 T2: THE ICON CHIP (the Bravos icon board, shots 26-28) - a card with one SOURCED glyph and a
                                   # label, landing on its word and crossed out on a later one. The first species built under the
                                   # operator's module rule (2026-09-11): the painter is scripts/species/chip.mjs, not a branch in the
                                   # template's body; this file still owns its grammar, its targets and its glyph's provenance.
UNDERLINE_FORM = "underline"   # P50 T3: a callout's FORM - the hand-drawn underline under a press card's quoted phrase (E56's one
                               # exception, the squiggle law s9.27). Not a species kind: the grammar gains a form and a target, not a kind.
HOLD_MIN_S = 1.0   # a held species with less room than this before the next event is dropped, not flashed (2026-09-08) [DERIVED: E25 - a light that cannot hold its sentence has nothing to prove]
PAGE_SPECIES = ("build_to", "bracket", "retitle", "relight", "undraw", "figure", "note", "spread", "peel", "chart_to")
CHART_TO_KINDS = ("recast", "rescale", "extend", "park", "morph")   # P48: recast (T4, a hand-over; keyed: T4b), rescale (T2), extend (T3), park (T2b: the chart makes room by one affine transform), morph (T5: the area under the line becomes the target's by ARAP)
MORPH_BUILDERS = ("dense-line",)                     # P48 T5: the shape a morph moves is the AREA UNDER A LINE - both sides of a morph_to are line pages
PARK_ANCHORS = ("top", "bottom", "left", "right")   # the corner of its own box the parked chart shrinks toward (top = Bravos 91: up, the room opens below)
RECAST_PAIRS = (("dense-line", "story"),)             # P48 T4b: the legal KEYED pairs - n lines <-> n bars by series (Bravos 99-105); everything else recasts by the hand-over
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


def validate_camera(cam, plate_id: str) -> list[str]:
    """An authored camera, validated by name: keys in ascending t, zoom > 0, an ease from the set, look/at as stage
    fractions or a declared target, attention from the set. None or the identity pass."""
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
    return errs


def validate_camera_row(cam, row_species, plate_id: str) -> list[str]:
    """The row's camera against its species: authored keys and a camera species cannot both drive one window."""
    errs = validate_camera(cam, plate_id)
    moves = [e["kind"] for e in (row_species or []) if isinstance(e, dict) and e.get("kind") in CAMERA_MOVES]
    if isinstance(cam, dict) and cam.get("keys") and moves:
        errs.append(f"{plate_id}: camera keys and a {moves[0]} species on one row - one camera per window (s9.28 C3)")
    elif isinstance(cam, dict) and cam.get("attention") == "landings" and moves:
        errs.append(f"{plate_id}: attention landings and a {moves[0]} species on one row - the landing IS the camera's move (E51, s9.28 C3)")
    return errs
TARGET_KINDS = ("datum", "point", "region", "span")
# s9.27 targeting law: the target kinds each species may take. () = the species
# needs no target (plate life's target is the plate itself); everything else
# fires only on a declared coordinate - datum index / series point on a page or
# dock, a plate point or region the author names, a caption word span.
SPECIES_TARGETS = {
    "punch": TARGET_KINDS, "callout": TARGET_KINDS + ("phrase",), "focus_zoom": TARGET_KINDS,   # P50 T3: the callout alone may point INSIDE a press card
    "spotlight": TARGET_KINDS, "squiggle": TARGET_KINDS, "pull_back": TARGET_KINDS,
    "plate_life": (),
    "beat_freeze": ("point", "region"), "radial": ("point", "region"), "push": ("point", "region"),
    "steam": ("region",), "trace": ("region",), "ticker": ("region",),
    "life": (),
    SPECIES_CHIP: ("point", "region"),   # P50 T2: a chip lands where the author declared it - a point, or centred in a region;
                                         # E56 does not reach it (a chip is a card with a glyph, never a ring around a picture)
    "build_to": ("datum",), "bracket": (), "retitle": (), "relight": (),   # P47 T2: the datum is the cap; the others carry their own fields
    "undraw": ("datum",), "figure": ("datum",), "note": (), "spread": (), "peel": (), "chart_to": (),   # E50; peel names no datum: the slice it pulls is the one the PAGE declared (page.peel.index), so the chart and the claim cannot disagree; spread names its two series, not a datum: the datum the line unwinds back to (0 = nothing); the datum the figure is pinned to
}
PHRASE_TARGET = "phrase"                      # P50 T3: a region INSIDE a press card - {"kind": "phrase", "dock": "<the press dock's asset id>"}.
TARGET_KINDS_ALL = TARGET_KINDS + (PHRASE_TARGET,)   # ... admitted for a CALLOUT alone, and only as the underline (E56's one exception); the
                                                     # compiler resolves it to the dock's declared phrase box, the player to stage px through
                                                     # the card's LIVE geometry (a parked or stacked card moves, and the underline moves with it)
TARGET_FIELDS = {"datum": ("index",), "point": ("x", "y"),
                 "region": ("x0", "y0", "x1", "y1"), "span": ("from_word", "to_word"),
                 PHRASE_TARGET: ()}   # its one field is `dock`, a name - checked in _validate_callout, where the row's press docks are known
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
    elif kind == "undraw":
        if "series" in entry and not is_idx(entry["series"]):
            errs.append("undraw: series must be a non-negative integer series index")
    if kind in ("build_to", "undraw") and "paths" in entry and entry["paths"] not in PATH_SELECTORS:
        errs.append(f"{kind}: paths must be one of {'|'.join(PATH_SELECTORS)} (the highlighted tail, the history, or all)")
    elif kind == "chart_to":
        if entry.get("to") not in CHART_TO_KINDS:
            errs.append(f"chart_to: 'to' must be one of {'|'.join(CHART_TO_KINDS)} (the verb the chart changes state by)")
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


def scene_exit(authored_exit: str | None, has_docks: bool) -> tuple[str, float | None]:
    """The HYBRID exit rule (operator 2026-08-29), with E47's default (2026-09-06).

    An authored 6th shot-table element wins - doc 29 s9.16 #3's override stands, and a row that
    wants the carried-light cross-reveal still asks for it by name. Otherwise the MECHANICAL
    default is ``dip`` when the scene carries docks and ``cut`` when it is bare (it was
    ``wipe_right``/``cut``: the wipe is retired as the default world change, E47 #3).
    Returns the exit as the timeline carries it and the seconds it declares, if any."""
    return parse_exit(authored_exit or (DEFAULT_EXIT_DOCKS if has_docks else DEFAULT_EXIT_BARE))


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


def derive_rescale_states(world: dict, row_species: list, plate_id: str, ep_dir: Path) -> None:
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
    for sp in (row_species or []):   # P48 T4b: a keyed recast is admitted only on a legal pair, and the refusal names the reason
        if isinstance(sp, dict) and sp.get("kind") == "chart_to" and sp.get("to") == "recast" and sp.get("keyed"):
            if world.get("kind") != SPECIES_LEDGER:
                raise ValueError("chart_to recast keyed: only a LEDGER PAGE has chart states")
            states = [world.get("page") or {}] + list(world.get("page_states") or [])
            k = int(sp.get("state", 0))
            if not (0 < k < len(states)):
                raise ValueError(f"chart_to recast keyed: state {k} is not one of the page's other chart states")
            A, Bs = states[0], states[k]
            pair = (A.get("builder"), Bs.get("builder"))
            if pair not in RECAST_PAIRS:
                raise ValueError(f"chart_to recast keyed: {pair[0]} -> {pair[1]} has no honest key correspondence (the legal pairs: "
                                 + ", ".join(f"{a} -> {b}" for a, b in RECAST_PAIRS) + "); use the plain recast (the hand-over), morph_to or a cut")
            n_lines = len([s for s in (A.get("series") or []) if not s.get("later")])
            n_bars = len(Bs.get("values") or [])
            if n_lines != n_bars:
                raise ValueError(f"chart_to recast keyed: {n_lines} line(s) and {n_bars} bar(s) - a keyed recast needs one bar per series; a {n_lines}-line page has no {n_bars}-bar correspondence")
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


def _check_opt(key: str, value, where: str) -> None:
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


def page_place(page: dict, aspect: str) -> dict | None:
    """The parked rectangle for a dock on this ledger page, in stage pixels (E45 §1).

    ``{"x", "y", "w", "h"}``, or None when the page reports no band wide enough for a card -
    the caller then leaves the dock on its solo geometry. Pure: the page spec is never mutated."""
    boxes = LPG.page_boxes(page, aspect)
    stage_w = boxes["stage"]["w"]
    want = round(DOCK_ON_PAGE_W * stage_w)
    quiet = boxes.get("quiet_zone")
    best = None
    for band in free_bands(boxes):
        room_w, room_h = band["w"] - 2 * DOCK_PLACE_PAD, band["h"] - 2 * DOCK_PLACE_PAD
        width = max(DOCK_ON_PAGE_MIN_W, min(want, room_w, _card_w_for(room_h)))
        if width > band["w"] - 2 or dock_card_h(width) > band["h"] - 2:
            continue                       # even the floor card does not fit this band
        key = (width, band["band"] == quiet, -DOCK_BAND_ORDER.index(band["band"]))
        if best is None or key > best[0]:
            best = (key, band, width)
    if best is None:
        return None
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
    return {"x": round(x), "y": round(y), "w": width, "h": height}


def dock_place(world: dict, aspect: str | None) -> dict | None:
    """The placement every dock on this scene takes, or None on a plain plate (E45: "a dock on a
    plain plate keeps the solo card"). One rectangle per scene, from the page's geometry alone."""
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
    if room and room["h"] >= 40:
        if h > room["h"]:                                     # a tall card shrinks to the band rather than covering the page
            h = round(room["h"]); w = round(h / card_aspect) if card_aspect else w
        return {"x": round((sw - w) / 2), "y": round(room["y"] + (room["h"] - h) / 2), "w": w, "h": h}
    band = CENTRE_BAND * sh if (aspect or "16:9") == "9:16" else sh   # portrait: the caption strip is below the band
    return {"x": round((sw - w) / 2), "y": round(max(0, (band - h) / 2)), "w": w, "h": h}


def dock_entry(aid: str, slot: int, enter: float, exitt: float, n_badges: int,
               kind: str = DOCK_KIND_IMAGE, place: dict | None = None, arrive: str | None = None, mass: str | None = None,
               centre: bool = False, read_place: dict | None = None, read_s: float | None = None, park_s: float | None = None,
               press: dict | None = None, stack: bool = False) -> dict:
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
    return {
        "slide": aid, "slot": slot,
        "enter": round(enter, 2), "exit": round(exitt, 2),
        "badge_at": [round(enter + 0.75 + 1.3 * (n + 1), 2) for n in range(n_badges)],
        **({"kind": DOCK_KIND_VIDEO} if kind == DOCK_KIND_VIDEO else {}),
        # P50 T3: a PRESS card carries its source line and its quoted phrase onto the stage; `_stack` is the
        # scene's own bookkeeping and is replaced by stack_index / stack_n once every dock on the scene is known
        **({"kind": DOCK_KIND_PRESS, "source": press["source"], "phrase": press["phrase"],
            **({"_stack": True} if stack else {})} if press else {}),
        **({"place": place, "read_s": rs, "park_s": ps,
            "park": span >= rs + ps} if place else {}),
        **({"read_place": read_place} if (place and read_place) else {}),   # a centred card that pops here, then parks to its place (2026-09-10)
        **({"arrive": arrive} if arrive else {}), **({"mass": mass} if mass else {}),   # P47 T1: only when the row names them
        **({"centre": True} if centre and place else {}),   # the design pass: a centred card sits at its box from its first frame - no reading size, no park
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


def main() -> int:
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    # THE AUTHORED SHOT TABLE is the source. Not an allocator.
    import importlib.util
    sp = importlib.util.spec_from_file_location("shot", EP / SHOT_TABLE_FILE)
    shot = importlib.util.module_from_spec(sp); sp.loader.exec_module(shot)
    plan = sorted(shot.W)
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

    evidence, uris, scenes = {}, {}, []
    for i, row in enumerate(plan):
        # exit style is HYBRID (operator, 2026-08-29): mechanical default
        # (E47, 2026-09-06: docks -> DIP, bare -> cut; it was docks -> wipe),
        # with an optional authored 6th element per window for boundaries where
        # the MEANING differs - doc 29 Part 6: cut = contrast/correction, wipe =
        # process continuation. The rule itself is `scene_exit` above.
        a, b, plate, ken, ds = row[:5]
        authored_exit = row[5] if len(row) > 5 else None
        # TARGETED SPECIES (doc 29 s9.27, P35 T7): the optional 7th element.
        # The targeting law is a hard build error naming the row; the pivot
        # span is None until the parent wires it from the ledger (s9.28 C4).
        row_species = list(row[6]) if len(row) > 6 and row[6] is not None else []
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
        species_errors = validate_species(row_species, ken, plate, pivot_span=None, press_docks=row_press) + validate_camera_row(row_camera, row_species, plate)
        if species_errors:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): " + "; ".join(species_errors))
        # P50 T2: a chip's SOURCED glyph rides the asset map exactly as a plate or a dock still does,
        # keyed `icon:<name>` - the geometry travels in the player, never a path to a file on disk.
        for e in row_species:
            if isinstance(e, dict) and e.get("kind") == SPECIES_CHIP:
                try:
                    uris[ICON_PREFIX + e["icon"]] = icon_geometry(e["icon"])
                except ValueError as exc:
                    raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
        # a ledger page is drawn, not embedded (doc 29 s9.26); a bad or
        # missing series is a hard build error naming the row
        try:
            world = world_for_plate(plate, ken, EP, META)
        except ValueError as exc:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
        try:
            derive_rescale_states(world, row_species, plate, EP)   # P48 T2: each `chart_to rescale` gets its own derived page state
        except ValueError as exc:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
        if world.get("kind") == SPECIES_CLIP:
            uris[world["asset_id"]] = data_uri(Path(world.pop("clip_path")))   # raw mp4, keyed by the clip's stem
        elif "asset_id" in world:
            uris[world["asset_id"]] = data_uri(R.find_asset(world["asset_id"]), STAGE_W)   # the bare id (E49's `;idle=` is not part of it)
        docks = []
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
            dplace = centred_place(place, ASPECT, dopt.get("card_aspect"), (world or {}).get("page"), dopt.get("centre_w"), dopt.get("centre_band"), dopt.get("centre_y"), dopt.get("centre_x")) if (place and dopt.get("centre")) else place   # the third watch: a card centred on the page
            if dopt.get("press"):   # P50 T3: E45 - the pile has one box, and it is the stage's centre
                _perr = press_plate_error(plate, aid)
                if _perr:
                    raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s) {_perr}")
            rd = dopt.get("read") or {}   # the box a centred card POPS at before it parks to dplace (2026-09-10)
            rplace = centred_place(place, ASPECT, rd.get("card_aspect", dopt.get("card_aspect")), (world or {}).get("page"), rd.get("centre_w"), None, rd.get("centre_y"), rd.get("centre_x")) if (place and rd) else None
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
                                        dplace if (slot == 0 or dopt.get("centre")) else None, dopt.get("arrive"), dopt.get("mass"), bool(dopt.get("centre")),   # a centred card is placed on either slot (2026-09-10: two cards up at once)
                                        read_place=rplace, read_s=dopt.get("read_s"), park_s=dopt.get("park_s"),
                                        press=dopt.get("press"), stack=bool(dopt.get("stack"))))
        assign_press_stack(docks)   # P50 T3: the scene's press pile, in enter order
        try:
            exit_id, exit_s = scene_exit(authored_exit, bool(docks))
        except ValueError as exc:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
        scene = {
            "scene_id": f"s{i+1:02d}",
            # Ken Burns is AUTHORED per shot in the table, not one constant.
            "world": world,
            "exit": exit_id,
            "span": [round(a, 2), round(b, 2)],
            "docks": docks,
            # the row's targeted species, verbatim: the player resolves each
            # declared target to pixels at render time (resolveTarget), the
            # motion gate counts their events per the s9.27 gate column
            "species": row_species,
            "camera": row_camera if row_camera is not None else camera_identity(),   # P49 T1: identity unless the row authored keys
        }
        # E47: a timed exit publishes its length so the motion gate credits the right
        # window without re-parsing the name; a bare `dip` leaves the gate on DIP_S.
        if exit_s is not None:
            scene["exit_s"] = exit_s
        scenes.append(scene)

    # caption STAGE mode: stamp each page with the mode it takes at its first word (after the scenes exist)
    pages = [{**pg, "cap_mode": "anchor" if _dock_live_at(scenes, pg["s"]) else "stage"} for pg in pages]
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
        **({"caption_style": CAPTION_STYLE} if CAPTION_STYLE else {}),
    }
    (BUILD / TIMELINE_NAME).write_text(
        json.dumps(timeline, indent=1), encoding="utf-8")

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("{{TIMELINE}}", json.dumps(timeline, separators=(",", ":")))
    html = html.replace("{{URIS}}", json.dumps(uris, separators=(",", ":")))
    out = BUILD / "player.html"
    out.write_text(html, encoding="utf-8")

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
    print(f"  URIs        : {len(uris)} embedded, {out.stat().st_size/1e6:.0f} MB player")
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

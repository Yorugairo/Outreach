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
import json
import mimetypes
import subprocess
import sys
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
LEDGER_ENTERS = ("spiral", "mount")   # enter=spiral: the page RETURNS - unwinds from its point, no roll/soak/ink/build (E25; 2026-09-05)
                                      # enter=mount: no roll-out - the outgoing scene fades while the cream plate MOUNTS over it, then the page draws (operator, 2026-09-05)
KINETICS: dict = {}                # timeline.kinetics - the template's capability flags a build turns on (P39 kill switch; default all off)
CAPTION_STYLE: str | None = None   # timeline.caption_style - "phrase" on a short: the page lands as one readable phrase, only k-words punctuated (2026-09-05)
LEDGER_EXITS = ("cut",)            # exit=cut: no retract - the page leaves on the cut (for a beat that must land on the last line, E40 #5)
SPECIES_LEDGER = "ledger"          # timeline["species"] entry; the player keys on world.kind == "ledger"

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

# Ken Burns: doc 29 §1.4 — the world plate drifts while evidence holds locked,
# so the eye separates narrative world from evidence data with no labelling.
KEN = {"scale": 0.04, "x": 14, "y": -10}

# TARGETED SPECIES (doc 29 s9.27 MOTION MENU, P35 T7). A shot-table row's
# optional 7th element is a list of {"kind", "at", "dur", "target"} dicts;
# `at` and `dur` are episode seconds on the same clock as dock enter/exit.
SPECIES_KINDS = ("punch", "callout", "focus_zoom", "spotlight", "squiggle",
                 "pull_back", "plate_life", "beat_freeze", "radial", "push",
                 "steam", "trace", "ticker",   # STILL LIFE on an approved still (2026-09-05): a region each
                 "life")                       # a DECLARED claim: this world animates on its own for the window (a Remotion render, a
                                               # rendered outro) - the template draws nothing for it; the motion gate credits it as continuous;
                                               # the agent verifies the claim by eye before declaring it (CHECK-RESPONSIBILITIES: declared)
# s9.27 precedence / s9.28 C3: punch, focus zoom, pull-back and Ken Burns are
# mutually exclusive per window - one camera move, never over a Ken Burns drift.
CAMERA_MOVES = ("punch", "focus_zoom", "pull_back")
TARGET_KINDS = ("datum", "point", "region", "span")
# s9.27 targeting law: the target kinds each species may take. () = the species
# needs no target (plate life's target is the plate itself); everything else
# fires only on a declared coordinate - datum index / series point on a page or
# dock, a plate point or region the author names, a caption word span.
SPECIES_TARGETS = {
    "punch": TARGET_KINDS, "callout": TARGET_KINDS, "focus_zoom": TARGET_KINDS,
    "spotlight": TARGET_KINDS, "squiggle": TARGET_KINDS, "pull_back": TARGET_KINDS,
    "plate_life": (),
    "beat_freeze": ("point", "region"), "radial": ("point", "region"), "push": ("point", "region"),
    "steam": ("region",), "trace": ("region",), "ticker": ("region",),
    "life": (),
}
TARGET_FIELDS = {"datum": ("index",), "point": ("x", "y"),
                 "region": ("x0", "y0", "x1", "y1"), "span": ("from_word", "to_word")}
FRACTION_FIELDS = ("x", "y", "x0", "y0", "x1", "y1")   # plate coordinates as fractions of the frame, 0..1


def _validate_target(kind: str, target, allowed: tuple) -> list[str]:
    """Errors for one species' target against the kinds it may take (s9.27 targeting law)."""
    if not isinstance(target, dict) or target.get("kind") not in TARGET_KINDS:
        return [f"{kind}: target must be a dict of kind {'|'.join(TARGET_KINDS)}"]
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


def _validate_entry(entry) -> list[str]:
    """Errors for one species entry: known kind, numeric at/dur, a target where the law requires one."""
    if not isinstance(entry, dict) or entry.get("kind") not in SPECIES_KINDS:
        return [f"species entry {entry!r}: kind must be one of {'|'.join(SPECIES_KINDS)}"]
    kind = entry["kind"]
    errs = [f"{kind}: {f!r} must be a number (episode seconds)" for f in ("at", "dur")
            if isinstance(entry.get(f), bool) or not isinstance(entry.get(f), (int, float))]
    if not errs and entry["dur"] <= 0:
        errs.append(f"{kind}: dur must be > 0 (a species that lasts 0s does not fire)")
    allowed = SPECIES_TARGETS[kind]
    if not allowed:
        return errs
    if "target" not in entry:
        errs.append(f"{kind}: no declared target - a species with no declared target does not fire (s9.27)")
    else:
        errs += _validate_target(kind, entry["target"], allowed)
    return errs


def validate_species(row_species, ken, plate_id: str, pivot_span: tuple | None = None) -> list[str]:
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
    errs = [e for entry in row_species for e in _validate_entry(entry)]
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
        if "=" in enter:
            page["mount_s"] = float(enter.split("=", 1)[1])   # the mount phase (world fades, cream builds) before the page's own clock starts
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


def world_for_plate(plate_id: str, ken: tuple, ep_dir: Path, meta: dict | None = None) -> dict:
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
# THE RULE. LPG.page_boxes reports the page's own ink in stage pixels. Subtract the four forbidden
# boxes from the mobile safe box and what is left is five candidate bands: `above` (title foot ->
# plot head), `below` (plot foot -> source), `foot` (under the source/rail, above the anchored
# caption) and the two side columns beside the plot. Each band yields the widest card it can hold
# at 16:9 - capped at DOCK_ON_PAGE_W of the stage, floored at DOCK_ON_PAGE_MIN_W - and the band
# that yields the widest card wins, the declared quiet zone breaking ties. In the band the card is
# pushed to the quiet-zone side and parked against the PLOT (bottom-aligned in a horizontal band),
# so the estimator's one risk - a title that wraps one line off the model - eats into the title
# block E45's own choreography offers ("slide it to the corner or over the title"), never the chart.
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


def dock_card_h(width: int) -> int:
    """A video card's stage height at `width`: a 16:9 slide-frame plus the card's chrome."""
    return round((width - DOCK_CARD_CHROME_W) * 9 / 16) + DOCK_CARD_CHROME_H


def _card_w_for(height: float) -> int:
    """The widest card whose 16:9 frame plus chrome fits `height`."""
    return int((height - DOCK_CARD_CHROME_H) * 16 / 9) + DOCK_CARD_CHROME_W


def free_bands(boxes: dict) -> list[dict]:
    """The rectangles inside the safe box that the page's own ink leaves free (E45)."""
    safe, plot, title = boxes["safe"], boxes["plot"], boxes["title"]
    src, rail, cap = boxes["source"], boxes["rail"], boxes["caption_anchor"]
    left, right = safe["x"], safe["x"] + safe["w"]
    head = max(safe["y"], title["y"] + title["h"])
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


def dock_entry(aid: str, slot: int, enter: float, exitt: float, n_badges: int,
               kind: str = DOCK_KIND_IMAGE, place: dict | None = None) -> dict:
    """One dock on a compiled scene.

    Spans come from the dock: evidence enters before its claim and holds through the whole
    discussion. A flat hold drops the document mid-argument, which is what left 42% of claims
    naked. ``kind`` is written ONLY for a video dock - the motion gate credits a live video dock
    as continuous motion (M10 / M16) and an image dock's shape stays exactly as it was. ``place``
    is written ONLY for a dock on a ledger page (E45), so a plain-plate build compiles unchanged."""
    return {
        "slide": aid, "slot": slot,
        "enter": round(enter, 2), "exit": round(exitt, 2),
        "badge_at": [round(enter + 0.75 + 1.3 * (n + 1), 2) for n in range(n_badges)],
        **({"kind": DOCK_KIND_VIDEO} if kind == DOCK_KIND_VIDEO else {}),
        **({"place": place} if place else {}),
    }


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
        # (docks -> wipe, bare -> cut), with an optional authored 6th element
        # per window for boundaries where the MEANING differs - doc 29 Part 6:
        # cut = contrast/correction, wipe = process continuation.
        a, b, plate, ken, ds = row[:5]
        authored_exit = row[5] if len(row) > 5 else None
        # TARGETED SPECIES (doc 29 s9.27, P35 T7): the optional 7th element.
        # The targeting law is a hard build error naming the row; the pivot
        # span is None until the parent wires it from the ledger (s9.28 C4).
        row_species = list(row[6]) if len(row) > 6 and row[6] is not None else []
        species_errors = validate_species(row_species, ken, plate, pivot_span=None)
        if species_errors:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): " + "; ".join(species_errors))
        # each window runs to the next so the world layer never drops out
        b = plan[i + 1][0] if i + 1 < len(plan) else tl["runtime_s"]
        # a ledger page is drawn, not embedded (doc 29 s9.26); a bad or
        # missing series is a hard build error naming the row
        try:
            world = world_for_plate(plate, ken, EP, META)
        except ValueError as exc:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
        if world.get("kind") == SPECIES_CLIP:
            uris[world["asset_id"]] = data_uri(Path(world.pop("clip_path")))   # raw mp4, keyed by the clip's stem
        elif "asset_id" in world:
            uris[plate] = data_uri(R.find_asset(plate), STAGE_W)
        docks = []
        # E45 §1: on a ledger page every dock parks in the same rectangle, computed from the
        # page's own geometry. Only the SOLO card (slot 0) is placed - a paired/stacked dock keeps
        # the layout its slot declares, and a plain plate keeps the solo card entirely.
        place = dock_place(world, ASPECT)
        for aid, slot, enter, exitt in ds:
            d = META.get(aid, {"title": aid, "source": "", "species": "deck",
                               "badges": []})
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
                                        place if slot == 0 else None))
        scenes.append({
            "scene_id": f"s{i+1:02d}",
            # Ken Burns is AUTHORED per shot in the table, not one constant.
            "world": world,
            "exit": authored_exit or ("wipe_right" if docks else "cut"),
            "span": [round(a, 2), round(b, 2)],
            "docks": docks,
            # the row's targeted species, verbatim: the player resolves each
            # declared target to pixels at render time (resolveTarget), the
            # motion gate counts their events per the s9.27 gate column
            "species": row_species,
        })

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
        "scenes": scenes,
        # every species present (the ledger world + the targeted kinds), so
        # downstream (gate, render) can see it
        "species": timeline_species(scenes),
        "kinetics": dict(KINETICS),   # the template's capability flags this build turns on (P39: default all off)
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

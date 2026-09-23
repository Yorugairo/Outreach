"""The authoring kit - AUDIO: the runtime the outro makes, the bed that breathes, the cue clock.

The episode owns its files, its levels and its slot names. The kit owns the arithmetic that must
not drift between two shorts: the stitch, the bed gain, the swell keyed to a thrown card, and the
contact frame a landing cue is timed to (read from the kinetics module, so the sound cannot drift
from the motion).
"""
from __future__ import annotations

import math
import re
import subprocess
import sys
from pathlib import Path

STOP_MODULE = Path(__file__).resolve().parents[1] / "kinetics/stopaction.mjs"
STOP_DIALS = ("FLIGHT_S", "ANTIC_S", "DROP_S")
FPS = 24


def probe_duration(path: Path) -> float:
    """The stream's duration in seconds (ffprobe). 0.0 when ffprobe says nothing."""
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout
    return float(out or 0)


def outro_clock(t_vo_end: float, line_s: float, *, outro_lead: float, outro_s: float,
                brand_gap: float, brand_tail: float) -> tuple[float, float, float]:
    """(t_outro, t_line, runtime_s). The card's fade begins `outro_lead` before the last word ends
    and DISSOLVES in (M16); the brand line plays `brand_gap` after it, under the card; the runtime
    is whichever of the two finishes last."""
    t_outro = round(t_vo_end - outro_lead, 3)
    t_line = round(t_vo_end + brand_gap, 3)
    return t_outro, t_line, round(max(t_outro + outro_s, t_line + line_s + brand_tail), 3)


def stitch_brand_line(audio: Path, brand_line: Path, brand_gap: float, runtime_s: float) -> Path:
    """The take, `brand_gap` of silence, the brand line, then silence to the runtime - one stream at
    the take's own sample rate, written OVER `audio` (the player plays to the end of the card)."""
    stitched = audio.with_name(audio.stem + "-stitched.mp3")
    fc = ("[0:a]aresample=44100,aformat=channel_layouts=mono[a];"
          "[1:a]aresample=44100,aformat=channel_layouts=mono[g];"
          "[2:a]aresample=44100,aformat=channel_layouts=mono[l];"
          f"[a][g][l]concat=n=3:v=0:a=1,apad=whole_dur={runtime_s}[out]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(audio), "-f", "lavfi", "-t", str(brand_gap),
                    "-i", "anullsrc=r=44100:cl=mono", "-i", str(brand_line),
                    "-filter_complex", fc, "-map", "[out]", "-c:a", "libmp3lame", "-q:a", "2", str(stitched)], check=True)
    stitched.replace(audio)
    return audio


VO_TONE = ("highpass=f=70:poles=2",
           "equalizer=f=280:t=q:w=0.9:g=-3.2",
           "equalizer=f=800:t=q:w=2.2:g=5",
           "equalizer=f=1400:t=q:w=1.3:g=-4",     # cancels the sum of its two neighbours - see WHY
           "equalizer=f=2600:t=q:w=3.0:g=6",
           "equalizer=f=11000:t=q:w=1.0:g=5",
           "treble=f=7000:g=2")


VO_TP_TARGET_DBTP = -1.5


def vo_tone_filter(makeup_db: float | None = None, stages: tuple[str, ...] = VO_TONE) -> str:
    """The APPROVED VO tone chain as one ffmpeg -af string (the operator's A/B, chain G, 2026-09-16 -
    E99 s54, which amends s48's chain C), plus the per-file makeup trim when the caller has measured one.

    WHY these seven. Measured in 1/3-octave bands against two shipped references, the take is hot through
    200-350 Hz and scooped at 800 Hz, at 2.5-3.2 kHz and above 6 kHz: boxy in the chest, short of the
    consonant that carries a word on a phone speaker. The rumble cut at 70 Hz is below anything the
    voice uses.

    WHY NOT JUST MORE OF CHAIN C. s48 shipped a half-correction and the obvious next step was to turn it
    up. Measured, that barely moved: the mean distance from the reference shape went 4.51 -> 4.25 dB from
    half to full strength, while 2 kHz went from +5.7 to +7.2 dB OVER the reference. The fault was never
    gain, it was BELL WIDTH - C's 800 Hz and 2700 Hz bells are wide enough that their skirts SUM in the
    gap between them, putting 1-2 kHz +4 to +6 dB over a region the raw take already had right. G narrows
    both bells and spends one stage, the -4 dB at 1400 Hz, cancelling what is left of that sum. Result
    over 200 Hz-13 kHz: mean error 3.26 -> 2.05 dB, worst band 9.6 -> 4.6 dB, and it holds on a passage
    it was not fitted to (hook 2.04, held-out mid 2.28). The 11 kHz bell is the air the shelf could not
    reach on its own; the shelf drops to +2 because the bell now carries the top.

    NOTE the nominal gains are not what a 1/3-octave band reads: +5 at 800 Hz measures +3.2 and +6 at
    2600 Hz measures +4.5, because a narrow bell is averaged across a band wider than itself. The gate's
    expectations are the MEASURED numbers, not these.

    WHY A TRIM FOLLOWS IT. The A/B was judged at MATCHED loudness (every variant went through loudnorm
    before the operator heard it), so the ruling is on TONE and sets no level - and the chain as ruled is
    not level-neutral: the 280 Hz bell is nearly an octave wide and sits on the take's densest speech
    energy, so it takes out about a decibel more than the lifts put back, while the peaks rise until the
    take clips. `vo_makeup_db` sizes ONE flat gain that lands the written take on VO_TP_TARGET_DBTP. Flat
    is the point: it moves every band by the same number, so it cannot touch the ruled tone, and the
    headroom is not decoration - `insert_edit_pauses.py` and `compress_dead_space.py` re-encode this take
    at 192k, and an intermediate sitting at 0 dBTP clips on the re-encode.

    WHAT MUST NOT BE HERE. No loudnorm, no limiter, no compression, no saturation - the finished mix is
    normalised once, in the compositor, and anything that shapes level dynamically would re-shape the
    tone the operator ruled on. Nothing that retimes either (no atempo): the word timeline comes from the
    provider's timestamps, so an equal-length chain is the whole permitted vocabulary.

    The level a bed is hung from moves with the trim, so it is RE-MEASURED, not frozen: `bed_gain` reads
    an episode's `VO_LUFS` literal, and `master_vo_tone.py --verify` G2 fails when that literal no longer
    matches the toned take, naming the file and line to correct."""
    return ",".join((*stages, f"volume={makeup_db:.2f}dB") if makeup_db is not None else stages)


def vo_makeup_db(tp_dbtp: float, target: float = VO_TP_TARGET_DBTP) -> float:
    """The flat trim, in dB, that puts a post-chain take's measured true peak on `target`. One
    subtraction, kept here so the stage and its gate cannot disagree about what the trim should be."""
    return round(target - tp_dbtp, 2)


def bed_gain(vo_lufs: float, bed_lu: float, bed_lufs: float) -> float:
    """gain = 10^((VO_I - LU - bed_I) / 20): the bed sits `bed_lu` under the voice, measured to
    measured (the sub-threshold blueprint s2; the level itself is the episode's ruling)."""
    return round(10 ** ((vo_lufs + bed_lu - bed_lufs) / 20), 4)


def stop_dials(src: Path | None = None) -> dict:
    """The stop-action module's timing dials (FLIGHT_S, ANTIC_S, DROP_S), read from the source so a
    landing cue and the landing itself share one clock. The module is the truth; this is a regex
    over its STOP block."""
    text = Path(src or STOP_MODULE).read_text(encoding="utf-8")
    block = text.split("export const STOP", 1)[1].split("});", 1)[0]
    out = {k: float(v) for k, v in re.findall(r"^\s*([A-Z_]+):\s*([0-9.]+)", block, flags=re.M)}
    for k in STOP_DIALS:
        assert k in out, f"stopaction.mjs no longer names {k}"
    return out


STAMP = "stamp"
STAMP_SPRING = ("m", "k", "c")
STAMP_CONTACT_DP = 4           # gate_motion_density.STAMP_CONTACT_S's own precision (0.1542): the cue and the gate read ONE instant
STAMP_MASS = "ink"             # scene-evidence-engine.mjs:16969 `stampXf(d.mass || "ink", ...)` - the engine's own default, stamps only
LANDING_MASS = "paper"         # a throw or a land that names no mass (the shipped cue plans' `opts.get("mass", "paper")`)
WEIGHTED_ARRIVALS = ("throw", "land", STAMP)


def stamp_spring(src: Path | None = None) -> dict:
    """The stamp's CLAMPED scale spring (`STAMP_ARRIVAL.LAND`: m, k, c), read from the module like
    `stop_dials` - a regex over the STAMP_ARRIVAL block, so the cue cannot drift from the mark."""
    text = Path(src or STOP_MODULE).read_text(encoding="utf-8")
    block = text.split("export const STAMP_ARRIVAL", 1)[1].split("});", 1)[0]
    land = re.search(r"^\s*LAND:\s*\{([^}]*)\}", block, flags=re.M)
    assert land, "stopaction.mjs STAMP_ARRIVAL no longer names LAND"
    out = {k: float(v) for k, v in re.findall(r"([a-z]+):\s*([0-9.]+)", land.group(1))}
    for k in STAMP_SPRING:
        assert k in out, f"stopaction.mjs STAMP_ARRIVAL.LAND no longer names {k}"
    return out


def stamp_contact_s(src: Path | None = None) -> float:
    """A stamp's CONTACT after its enter: `STAMP_LAND.tc`, the first instant the clamped scale spring's
    0 -> 1 step response reaches 1 (stopaction.mjs:305-312, wd t = pi - atan(wd / (z w))) - the mark at
    its own size. Rounded to the motion gate's mirror (`STAMP_CONTACT_S`), so the two agree to the byte."""
    g = stamp_spring(src)
    z = g["c"] / (2 * math.sqrt(g["k"] * g["m"]))
    w = math.sqrt(g["k"] / g["m"])
    assert z < 1, f"STAMP_ARRIVAL.LAND is not underdamped (zeta {z:.4f}) - it never crosses 1"
    wd = w * math.sqrt(1 - z * z)
    return round((math.pi - math.atan2(wd, z * w)) / wd, STAMP_CONTACT_DP)


def landing_contact(t_enter: float, arrive: str, dials: dict, fps: int = FPS) -> float:
    """The frame the card touches down on. A THROW flies on the stepped clock (round(t * fps)), so
    its contact is the first frame at or past FLIGHT_S; a LAND is continuous - anticipation plus
    drop; a STAMP is continuous too - its clamped scale spring's crossing (`stamp_contact_s`, P69 T3).
    The cue goes ON that frame or one early, never two ahead (the weight report Q5)."""
    if arrive == "throw":
        return t_enter + math.ceil(dials["FLIGHT_S"] * fps - 1e-9) / fps
    if arrive == STAMP:
        return t_enter + stamp_contact_s()
    return t_enter + dials["ANTIC_S"] + dials["DROP_S"]


def arrival_mass(opts: dict) -> str:
    """The mass a weighted arrival lands at: its own `mass`, else the default for its kind - `ink` for a
    stamp (the engine's own), `paper` for a throw or a land."""
    return (opts or {}).get("mass") or (STAMP_MASS if (opts or {}).get("arrive") == STAMP else LANDING_MASS)


def row_arrivals(row, kinds: tuple[str, ...] = WEIGHTED_ARRIVALS):
    """The docks of ONE row that arrive with weight: (dock tuple, its options). Per row, so a cue
    list keeps the order the shot table reads in."""
    for d in (row[4] or []):
        opts = d[4] if len(d) > 4 and isinstance(d[4], dict) else {}
        if opts.get("arrive") in kinds:
            yield d, opts


def page_transitions(plate_id: str) -> dict:
    """How a row's world ARRIVES and LEAVES, as the sound map asks it: `ledger` (a page at all),
    `spiral` / `mount` / `snap` / `camera` (the entry), `cut` (no retract - the page leaves on the
    cut). NOTE `cut` is the literal `:cut` SUFFIX, so a row that appends `;then=` or `;idle=` after
    it does not read as a cut here; that is the behaviour the shipped cue plans were built on and
    it is preserved deliberately. Any OTHER page option (`;form=`, `;depth=`, ...) is stripped first,
    by the compiler's own split (build_scene_timeline_f.split_plate_opts: `bare, *parts = id.split(";")`),
    so `...:cut;form=extruded_bar` still reads as a cut (P58 T7)."""
    bare, *parts = plate_id.split(";")
    keeps_suffix_reading = any(p.split("=", 1)[0] in LEGACY_SUFFIX_OPTS for p in parts)
    return {"ledger": plate_id.startswith("ledger:"),
            "spiral": ":spiral" in plate_id,
            "mount": ":mount" in plate_id,
            "snap": ":snap=" in plate_id,
            "camera": ":camera=" in plate_id,
            "cut": (plate_id if keeps_suffix_reading else bare).endswith(":cut")}


LEGACY_SUFFIX_OPTS = ("then", "idle")   # the options whose rows the shipped cue plans read on the raw suffix


def bed_envelope(rows, swell_db: float, snap_s: float, fallback_end, *,
                 snap_keys: tuple[str, ...] = (":snap=", ":camera="),
                 lead_s: float = 0.3, fall_s: float = 0.8) -> list[list[float]]:
    """The bed BREATHES with the structure (the blueprint rule 3): up over `lead_s` before a card is
    thrown, held through the landing and the snap that makes it the world, down over `fall_s`.
    Returns [[t, dB against the bed's own gain], ...] - the player and the render apply it as a pure
    function of t. `fallback_end(dock)` gives the end when no row snaps this card up."""
    env: list[list[float]] = []
    for r in rows:
        for d in (r[4] or []):
            if len(d) > 4 and isinstance(d[4], dict) and d[4].get("arrive") == "throw":
                t_throw = float(d[2])
                t_snap = next((q[0] for q in rows if any(f"{k}{d[0]}" in q[2] for k in snap_keys)), None)
                t_end = (t_snap + snap_s) if t_snap is not None else float(fallback_end(d))
                env += [[round(t_throw - lead_s, 2), 0.0], [round(t_throw, 2), swell_db],
                        [round(t_end, 2), swell_db], [round(t_end + fall_s, 2), 0.0]]
    return env


# --- THE CUE IS BOUND TO WHAT FIRES (E99 s72, BACKLOG R26-187) ----------------------------------
#
# The operator, on the first generated base (v7, 2026-09-17): *"Sound effects are way off, we're
# playing spiral and whirls when there's no spiral or whirl effect."* He was right twice over, and
# both faults are one fault - a cue keyed on the ROW TOKEN instead of on the frame:
#
#   * `page_transitions` above reads `:cut` off the RAW plate id, and a page carrying a `;then=` or
#     `;idle=` tail no longer ENDS with `:cut` (`LEGACY_SUFFIX_OPTS` - the reading the shipped cue
#     plans were built on, which must not move under them). So a page that leaves ON THE CUT was
#     given a WHIRL, the retract's own sound, at every scene the base carries a chained page.
#   * the map plays its page-ROLL at any entry that is not a mount or a spiral, and three of the
#     base's four pages enter by `axes`, `snap` or `camera` - entries with no cream roll-out at all
#     (`gate_motion_density.ARRIVES_BUILT`; P53 T1: the axes page LANDS with its ground drawn).
#
# The COMPILED timeline knows, because the PLAYER's own clocks read it: `spiralClocks` in
# `scene-evidence-engine.mjs` retracts a page only when `world.page.exit !== "cut"`, over the scene's
# last `LP_RETRACT.COLOURS + CHARCOAL` seconds, and unwinds one in only when `enter === "spiral"`.
# So the truth stream is the compiled timeline's, walked by `recipe_walk.events` - the same walk the
# drift gate and the one-shot floor already read - and a cue whose effect DOES NOT FIRE at its instant
# is DROPPED and named.
#
# NOTHING IS INVENTED HERE. No file is chosen, no gain is set, no cue is added: the episode's own map
# still says WHICH sound and how loud (E99 s37 - no sound is invented for an instant that has none),
# and an instant the map leaves silent is NAMED by `unsounded`, as `lab_build.cue_notes` names one.
# This binder only ever removes a cue the frame does not play, and says why.
#
# It is a KIT function, not the bed's: `build_short.sound_cues` is an APPROVED cut's cue map and is
# never edited to fix a base (E99 s11). The approved cuts keep the plans they shipped with.

ROLL_OUT = "roll-out"          # a page with NO declared entry rolls its cream out - the ONLY entry the page-roll cue belongs to
SPIRAL = "spiral"
NO_RETRACT = "cut"             # build_scene_timeline_f.LEDGER_EXITS: `exit=cut` is the only no-retract page exit
WHIRL, FLIP = "whirl", "flip"  # the bed's own map: a page that arrived by spiral drains as a WHIRL, any other as a FLIP
SUCK = "suck"
BOUND_KINDS = ("page enter", "page retract", "landing", SUCK)   # the cue kinds this binder has a truth for
CUE_SLOT = re.compile(r"^(?P<kind>page enter|page retract|landing|suck|press)"
                      r"(?:\s+(?P<n>\d+))?(?:\s*\((?P<what>[^)]*)\))?\s*$")
CUE_ROW_ID = "s{n:02d}"        # `build_scene_timeline_f.scene_row_id`: the nth ROW names its scene `s01`, `s02`, ...
                               # and a slot is numbered by its row (`build_short.sound_cues`) - the one handle a cue
                               # has on WHERE it belongs, and the difference between row 5's landing and row 2's


def _scripts_on_path() -> None:
    root = str(Path(__file__).resolve().parents[1])
    if root not in sys.path:
        sys.path.insert(0, root)


def walk():
    """`recipe_walk`, imported lazily - the ONE walk of a compiled timeline both gates already read."""
    _scripts_on_path()
    import recipe_walk
    return recipe_walk


def gates():
    """`gate_motion_density`, imported lazily - the retract's own seconds and the cue tolerance, by
    name (`LP_RETRACT_S`, `CUE_TOL_S`), never re-typed here."""
    _scripts_on_path()
    import gate_motion_density
    return gate_motion_density


def scene_page(scene) -> dict | None:
    page = ((scene or {}).get("world") or {}).get("page")
    return page if isinstance(page, dict) else None


def page_entry(page: dict) -> str:
    """A page's entry AS THE SOUND MAP MUST READ IT: an absent `enter` is the cream ROLL-OUT.

    `recipe_walk` writes `page_enter:mount` for an absent entry (its own default), and a mount is the
    one entry with no page turn at all - so the walk's card cannot be the cue's key and the page block
    is read instead. Everything else is the compiler's own vocabulary (`LEDGER_ENTERS`)."""
    return str(page.get("enter") or ROLL_OUT).split("=", 1)[0]


def fired(timeline, dials: dict | None = None) -> list[dict]:
    """Every transition and arrival the COMPILED timeline actually PLAYS, as the cue map names them.

    `[{kind, what, at, until, scene, ref}]` in time order: a page ENTER at the scene's start (its
    `what` the page's own entry, `roll-out` when it declares none), a page RETRACT over the scene's
    last `LP_RETRACT_S` where the page does not leave on the cut (`whirl` when it arrived by spiral,
    `flip` otherwise - the bed's own map), a LANDING at each weighted dock's CONTACT frame
    (`landing_contact`, so the sound cannot drift from the motion), and a SUCK at a scene that ends
    on one. These are the instants a cue may be bound to; every other instant is silence the map
    never mapped."""
    W, G = walk(), gates()
    scenes = list((timeline or {}).get("scenes") or [])
    by_id = {str(s.get("scene_id") or i): s for i, s in enumerate(scenes)}
    dials = dials or stop_dials()
    out: list[dict] = []
    for e in W.events(timeline):
        scene = by_id.get(e.scene) or {}
        span = list(scene.get("span") or [e.t, e.t])
        t1 = float(span[1] if len(span) > 1 else span[0])
        if e.cls == "page_enter":
            page = scene_page(scene) or {}
            enter = page_entry(page)
            out.append({"kind": "page enter", "what": enter, "at": e.t, "until": e.t,
                        "scene": e.scene, "ref": e.ref})
            if str(page.get("exit") or "") != NO_RETRACT:
                out.append({"kind": "page retract", "what": WHIRL if enter == SPIRAL else FLIP,
                            "at": round(t1 - sum(G.LP_RETRACT_S), 2), "until": round(t1, 2),
                            "scene": e.scene, "ref": e.ref})
        elif e.cls == "arrival":
            arrive = str(e.card).split(":", 1)[1]
            contact = round(landing_contact(e.t, arrive, dials), 2)
            out.append({"kind": "landing", "what": arrive, "at": contact, "until": contact,
                        "scene": e.scene, "ref": e.ref, "mass": arrival_mass({"arrive": arrive, "mass": e.option})})
        elif e.cls == "exit" and str(e.ref or "").split(":", 1)[0] == SUCK:
            out.append({"kind": SUCK, "what": SUCK, "at": round(t1, 2), "until": round(t1, 2),
                        "scene": e.scene, "ref": e.ref})
    return sorted(out, key=lambda r: (r["at"], r["kind"], r["what"]))


def cue_key(cue: dict) -> dict | None:
    """What a cue CLAIMS fires, read off its slot: `{kind, what, mass, n}` - or None when the slot names
    nothing this binder has a truth for (a bed, a press pack, a slot a later map invents). A cue the
    binder cannot judge is never dropped. `n` is the slot's own ROW number, KEPT (`cue_scene` turns it
    into the scene that row compiled to) - it is the difference between a cue for row 5's landing and
    row 2's, which are the same kind and the same `what` one tolerance apart."""
    m = CUE_SLOT.match(str(cue.get("slot") or "").strip())
    if m is None or m.group("kind") not in BOUND_KINDS:
        return None
    kind, what = m.group("kind"), (m.group("what") or "").strip()
    n = int(m.group("n")) if m.group("n") else None
    parts = [p.strip() for p in what.split(",")] if what else []
    if kind == "page enter":
        return {"kind": kind, "what": parts[0] if parts else ROLL_OUT, "mass": None, "n": n}
    if kind == "page retract":
        return {"kind": kind, "what": parts[0] if parts else FLIP, "mass": None, "n": n}
    if kind == "landing":
        return {"kind": kind, "what": parts[0] if parts else "",
                "mass": parts[1] if len(parts) > 1 else None, "n": n}
    return {"kind": kind, "what": SUCK, "mass": None, "n": n}


def cue_scene(key: dict, timeline) -> str | None:
    """The SCENE a cue's slot number names, or None when this timeline does not carry that row.

    A slot is numbered by its ROW (`build_short.sound_cues`: `f"landing {i + 1} ({arr}, {mass})"`) and
    the compiler names the nth row's scene `s{n:02d}` (`build_scene_timeline_f.scene_row_id`), so the
    two meet on that id and nowhere else. A timeline whose scenes do not carry it (a hand-written one,
    a row that compiled to no scene of its own) resolves to None and the cue is bound BY TIME ALONE:
    a row that cannot be resolved must never narrow the match, because a wrong narrowing DROPS a cue
    and this binder's every failure has to fall on the side of keeping one."""
    n = (key or {}).get("n")
    if not n:
        return None
    want = CUE_ROW_ID.format(n=int(n))
    ids = {str(s.get("scene_id") or "") for s in (timeline or {}).get("scenes") or []}
    return want if want in ids else None


def fire_matches(key: dict, at: float, f: dict, tol: float, scene: str | None = None) -> bool:
    """Whether this cue MAY be bound to this fire: the same kind and `what`, at an instant inside the
    effect's own span widened by `tol` (the gate's own `CUE_TOL_S` - a cue lands WITH the thing it
    marks, never two beats from it), the same MASS where both sides carry one (a `metal` cue does not
    play over a `paper` landing), and on the scene the slot's row names where that row resolves."""
    if f["kind"] != key["kind"] or f["what"] != key["what"]:
        return False
    if not (f["at"] - tol <= at <= f["until"] + tol):
        return False
    if key.get("mass") and f.get("mass") and str(key["mass"]) != str(f["mass"]):
        return False
    return not (scene is not None and str(f.get("scene") or "") != scene)


def fire_distance(at: float, f: dict) -> float:
    """How far a cue's instant sits from the effect's own span - 0 anywhere inside it."""
    return round(max(f["at"] - at, at - f["until"], 0.0), 6)


def cue_fires(key: dict, at: float, fires: list[dict], tol: float, scene: str | None = None,
              taken: set | None = None) -> dict | None:
    """The NEAREST firing effect this cue may be bound to, or None - skipping any fire already taken
    by another cue. One cue, read alone; `bind_report` is the whole list, where the nearest pair wins
    first and every fire is consumed exactly once."""
    cands = [f for i, f in enumerate(fires)
             if i not in (taken or set()) and fire_matches(key, at, f, tol, scene)]
    return min(cands, key=lambda f: (fire_distance(at, f), f["at"])) if cands else None


def drop_why(key: dict, at: float, scene: str | None, fires: list[dict], tol: float) -> str:
    """Why this cue is not bound, in the frame's own terms - and which of the four reasons it is."""
    claim = f"{key['kind']} ({key['what']})"
    near = [f for f in fires if f["at"] - tol <= at <= f["until"] + tol]
    same = [f for f in near if f["kind"] == key["kind"] and f["what"] == key["what"]]
    plays = ", ".join(sorted({f"{f['kind']} ({f['what']})" for f in near})) or "nothing"
    if not same:
        return (f"no `{claim}` fires within {tol:.1f}s of {at:.2f}s - the compiled timeline plays "
                f"{plays} there")
    masses = sorted({str(f["mass"]) for f in same if f.get("mass")})
    if key.get("mass") and masses and str(key["mass"]) not in masses:
        return (f"the `{claim}` within {tol:.1f}s of {at:.2f}s lands {'/'.join(masses)}, not "
                f"`{key['mass']}` - a cue plays the weight the frame plays")
    on = sorted({str(f.get("scene") or "?") for f in same})
    if scene is not None and scene not in on:
        return (f"the `{claim}` within {tol:.1f}s of {at:.2f}s fires on {', '.join(on)}, not on "
                f"`{scene}` - the slot's own row ({key['n']}) is that scene "
                "(`build_scene_timeline_f.scene_row_id`)")
    return (f"every `{claim}` within {tol:.1f}s of {at:.2f}s is already bound to a NEARER cue - one "
            "fire sounds once, and this cue is the one left over")


def bind_report(cues: list[dict], timeline, tol: float | None = None) -> dict:
    """The ONE pairing of cues to fires every reader here shares: NEAREST-FIRST and CONSUMED.

    `{fires, tol, cues: [{cue, key, at, scene, fire, why}], silent: [the fires no cue took]}`. Each
    cue binds to at most one fire and each fire to at most one cue: every admissible pair is scored by
    its distance and the nearest is taken first, so two arrivals of one kind inside the tolerance -
    ordinary in a dense beat - take a cue each, and the one the map leaves out is NAMED rather than
    silenced by its neighbour's cue (E99 s37: an instant the map has no sound for stays silent, and
    says so). A cue the binder has no truth for carries `key is None` and is never dropped."""
    fires = fired(timeline)
    tol = gates().CUE_TOL_S if tol is None else float(tol)
    keys = [cue_key(c) for c in cues]
    ats = [float(c.get("at") or 0.0) for c in cues]
    scenes = [cue_scene(k, timeline) if k is not None else None for k in keys]
    pairs = sorted((fire_distance(ats[ci], f), ci, fi)
                   for ci, key in enumerate(keys) if key is not None
                   for fi, f in enumerate(fires) if fire_matches(key, ats[ci], f, tol, scenes[ci]))
    bound: dict[int, int] = {}
    taken: set[int] = set()
    for _d, ci, fi in pairs:
        if ci not in bound and fi not in taken:
            bound[ci] = fi
            taken.add(fi)
    rows = [{"cue": cue, "key": keys[ci], "at": ats[ci], "scene": scenes[ci],
             "fire": fires[bound[ci]] if ci in bound else None,
             "why": None if keys[ci] is None or ci in bound
                    else drop_why(keys[ci], ats[ci], scenes[ci], fires, tol)}
            for ci, cue in enumerate(cues)]
    return {"fires": fires, "tol": tol, "cues": rows,
            "silent": [f for fi, f in enumerate(fires) if fi not in taken]}


def bind_cues(cues: list[dict], timeline, tol: float | None = None) -> tuple[list[dict], list[dict]]:
    """`(the cues the frame plays, the cues dropped)` - the whole of E99 s72's second fault.

    Every dropped record carries the cue and a `why` naming the effect it claimed and what the
    compiled timeline plays on that instant instead. The kept list keeps the cues' own order, their
    files, their gains and their envelopes: this function chooses no sound."""
    kept, dropped = [], []
    for r in bind_report(cues, timeline, tol)["cues"]:
        if r["key"] is None or r["fire"] is not None:
            kept.append(r["cue"])
        else:
            dropped.append({"cue": r["cue"], "at": r["at"], "slot": r["cue"].get("slot"), "why": r["why"]})
    return kept, dropped


def unsounded(cues: list[dict], timeline, tol: float | None = None) -> list[str]:
    """Every firing effect the cue list leaves SILENT, named - never filled (E99 s37: no sound is
    invented for an instant the episode's map has none for). The shape `lab_build.cue_notes` prints.

    Read off the SAME pairing the binder uses, so the two can never disagree: a fire one cue took is
    sounded, and a second fire of the same kind one tolerance away is not - it is named here."""
    out: list[str] = []
    for f in bind_report(cues, timeline, tol)["silent"]:
        note = f"no cue mapped for {f['kind']} ({f['what']}) at {f['at']:.2f}s on {f['scene']}"
        if note not in out:
            out.append(note)
    return out

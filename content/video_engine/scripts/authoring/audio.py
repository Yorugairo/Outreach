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


def landing_contact(t_enter: float, arrive: str, dials: dict, fps: int = FPS) -> float:
    """The frame the card touches down on. A THROW flies on the stepped clock (round(t * fps)), so
    its contact is the first frame at or past FLIGHT_S; a LAND is continuous - anticipation plus
    drop. The cue goes ON that frame or one early, never two ahead (the weight report Q5)."""
    if arrive == "throw":
        return t_enter + math.ceil(dials["FLIGHT_S"] * fps - 1e-9) / fps
    return t_enter + dials["ANTIC_S"] + dials["DROP_S"]


def row_arrivals(row, kinds: tuple[str, ...] = ("throw", "land")):
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

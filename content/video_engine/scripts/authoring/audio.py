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
    it is preserved deliberately."""
    return {"ledger": plate_id.startswith("ledger:"),
            "spiral": ":spiral" in plate_id,
            "mount": ":mount" in plate_id,
            "snap": ":snap=" in plate_id,
            "camera": ":camera=" in plate_id,
            "cut": plate_id.endswith(":cut")}


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

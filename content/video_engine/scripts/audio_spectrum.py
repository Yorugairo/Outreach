"""The average SPEECH spectrum of a take, in 1/3-octave bands - the measurement a tone ruling is made on.

Why it exists. "The take sounds boxy" is not a finding; "the take is +3 dB over the reference at 280 Hz
and -3 dB under it at 2.7 kHz" is, and it survives being handed to another agent. Every tone decision in
this engine (the VO tone chain in `authoring/audio.py`, the A/B that chose it) is made by measuring our
take and a SHIPPED reference in the same bands and reading the difference.

Two things make two files comparable:

- the SPEECH GATE. A take is mostly not speech - breaths, room, the pauses the editor inserted. Frames
  below the median frame RMS are dropped, so the average is of the voice and not of the silence between
  words. Two files with different amounts of silence still land on the same shape.
- the NORMALISATION. `shape=True` (the default) returns each band relative to the file's own broadband
  power, so a reference mastered 6 dB hotter than our take does not read as 6 dB brighter everywhere.
  Ask for `shape=False` when you are comparing ONE file before and after a filter - there the absolute
  band level is the point, and normalising would smear the filter's own gain across every band.

Importable:

    from audio_spectrum import decode_mono, band_levels, band_deltas
    x = decode_mono(take)                             # mono float32 at SR, the first `dur` seconds
    before = band_levels(x, shape=False)              # {centre Hz: dB}
    band_deltas(before, band_levels(decode_mono(toned), shape=False))   # {centre Hz: dB out - in}

or from the command line, one band per line:

    python audio_spectrum.py <path> [--start S] [--dur S] [--absolute]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000          # decode rate: a 1/3-octave grid to 16 kHz needs room above 16 kHz
FRAME = 8192        # ~171 ms at SR - long enough to resolve the 25 Hz band, short enough to gate on
HOP = FRAME // 2
DEFAULT_DUR = 180.0
ISO_LO, ISO_HI = 25.0, 17000.0
EPS = 1e-30


def iso_third_octave_centres(lo: float = ISO_LO, hi: float = ISO_HI) -> list[float]:
    """The ISO 1/3-octave centres from `lo` up to (not past) `hi` - each a factor 2^(1/3) above the last."""
    out, f = [], float(lo)
    while f < hi:
        out.append(f)
        f *= 2 ** (1 / 3)
    return out


def decode_mono(path: Path | str, start: float = 0.0, dur: float = DEFAULT_DUR, sr: int = SR) -> np.ndarray:
    """`dur` seconds of `path` from `start`, decoded to mono float32 at `sr` (ffmpeg, never in place)."""
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(start), "-t", str(dur),
                          "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def speech_frames(x: np.ndarray, n: int = FRAME, hop: int = HOP) -> np.ndarray:
    """The frames of `x` whose RMS is above the MEDIAN frame RMS - the half of the file that is voice.

    The gate is what makes two files comparable: without it the average is dominated by however much
    silence each one happens to carry. Raises when the clip is shorter than one frame."""
    if x.size < n:
        raise ValueError(f"clip is {x.size} samples, shorter than one {n}-sample frame")
    frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hop]
    rms = np.sqrt((frames.astype(np.float64) ** 2).mean(axis=1) + EPS)
    keep = frames[rms > np.median(rms)]
    return keep if keep.size else frames


def band_levels(x: np.ndarray, *, sr: int = SR, centres: list[float] | None = None,
                shape: bool = True, n: int = FRAME, hop: int = HOP) -> dict[float, float]:
    """{centre Hz: dB} - the mean power in each 1/3-octave band over the file's speech frames.

    `shape=True` measures each band against the file's own broadband power (comparable ACROSS files);
    `shape=False` leaves the band level absolute (comparable BEFORE and AFTER a filter on one file)."""
    frames = speech_frames(x, n, hop).astype(np.float64)
    power = (np.abs(np.fft.rfft(frames * np.hanning(n), axis=1)) ** 2).mean(axis=0)
    freqs = np.fft.rfftfreq(n, 1 / sr)
    ref = 10 * np.log10(power.sum() + EPS) if shape else 0.0
    out: dict[float, float] = {}
    for fc in (centres if centres is not None else iso_third_octave_centres()):
        edge = 2 ** (1 / 6)
        in_band = (freqs >= fc / edge) & (freqs < fc * edge)
        out[fc] = round(10 * np.log10(power[in_band].sum() + EPS) - ref, 3)
    return out


def band_deltas(before: dict[float, float], after: dict[float, float]) -> dict[float, float]:
    """{centre Hz: dB after - before} over the centres both measurements share."""
    return {fc: round(after[fc] - before[fc], 3) for fc in before if fc in after}


def measure(path: Path | str, *, start: float = 0.0, dur: float = DEFAULT_DUR,
            centres: list[float] | None = None, shape: bool = True) -> dict[float, float]:
    """Decode and measure in one call - the shorthand a caller that holds only a path wants."""
    return band_levels(decode_mono(path, start, dur), centres=centres, shape=shape)


def to_json(levels: dict[float, float]) -> dict[str, float]:
    """A receipt-safe copy: float centres become strings, so the dict round-trips through JSON."""
    return {f"{fc:.1f}": v for fc, v in levels.items()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", type=Path, help="audio file to measure")
    ap.add_argument("--start", type=float, default=0.0, help="seconds into the file (default 0)")
    ap.add_argument("--dur", type=float, default=DEFAULT_DUR, help=f"seconds to read (default {DEFAULT_DUR:.0f})")
    ap.add_argument("--absolute", action="store_true", help="absolute band dB instead of dB re broadband")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(f"# {args.path.name}  {'absolute' if args.absolute else 'dB re broadband'}")
    for fc, db in measure(args.path, start=args.start, dur=args.dur, shape=not args.absolute).items():
        print(f"{fc:8.0f} {db:7.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

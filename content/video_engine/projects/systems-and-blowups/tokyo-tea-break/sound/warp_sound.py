"""Warp an accent to a transition (operator, 2026-09-05: "stretch/warp the sound to match the transition - the distortion
would work in our favour, as if it's actually being sucked down the drain").

A time-varying resample: the output is read from the source at a rate r(tau) that follows the transition's own easing, so
pitch and speed glide together - tape-style, which is the distortion wanted. The rate curve is normalised so the whole
source is consumed over exactly the output length D:

    suck        D = SUCK_S + tail   rate RISES (minJerk) from r0 to RATIO*r0 - pulled into the point
    spiral in   D = LP_RETRACT.IN   rate FALLS from RATIO*r0 to r0 - it arrives fast out of the drain and settles
    drain out   D = 2.2 s           rate RISES from r0 to RATIO*r0 - accelerating into the drain, ending on the cut

    python warp_sound.py            # writes fs-whoosh-3-suck.mp3, fs-whoosh-3-spiral-in.mp3, fs-whoosh-3-drain.mp3 beside itself
Derived from fs-whoosh-3-648729.mp3 (CC0, sound/SOURCES.md) - the ledger row covers the derivations.
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE / "fs-whoosh-3-648729.mp3"
SR = 44100
WARPS = {   # name: (output seconds, rate ratio end/start, direction)
    "suck": (0.55, 6.0, "up"),        # SUCK_S 0.3 in the template + a short tail
    "spiral-in": (1.6, 3.0, "down"),  # LP_RETRACT.IN
    "drain": (2.2, 4.0, "up"),        # the retract: colours 1.0 + charcoal 1.0, timed to end on the cut
}


def min_jerk(u: np.ndarray) -> np.ndarray:
    u = np.clip(u, 0, 1)
    return u * u * u * (10 - 15 * u + 6 * u * u)


def decode(path: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def warp(x: np.ndarray, out_s: float, ratio: float, direction: str) -> np.ndarray:
    n_out = int(round(out_s * SR))
    tau = np.arange(n_out) / n_out
    shape = min_jerk(tau) if direction == "up" else 1 - min_jerk(tau)
    rate = 1 + (ratio - 1) * shape                       # relative read speed, r0 = 1 at the slow end
    pos = np.cumsum(rate)
    pos = pos / pos[-1] * (len(x) - 1)                   # normalised: the whole source over exactly n_out samples
    y = np.interp(pos, np.arange(len(x)), x)
    fade = int(0.02 * SR)
    y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
    return y


TARGET_I = -14.0   # the ledger's accent level (sound/SOURCES.md); the cue gain 0.22 then puts it ~9 dB under the -17.9 LUFS voice


def measure_i(path: Path) -> float:
    out = subprocess.run(["ffmpeg", "-i", str(path), "-af", "apad=whole_dur=3,loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    i = out.rfind("{"); import json; return float(json.loads(out[i:out.index("}", i) + 1])["input_i"])


def write_mp3(y: np.ndarray, out: Path) -> None:
    peak = np.max(np.abs(y)) or 1.0
    y = y / peak * 0.891                                 # -1 dBFS peak first
    tmp = out.with_suffix(".wav")
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    gain = TARGET_I - measure_i(tmp)                     # then loudness-matched to the ledger, limited at -1 dBFS like every accent
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-af", f"volume={gain:.2f}dB,alimiter=limit=0.891", "-c:a", "libmp3lame", "-q:a", "2", str(out)], check=True)
    tmp.unlink()
    print(f"  {out.name}: gain {gain:+.1f} dB -> {measure_i(out):.1f} LUFS")


def main() -> int:
    x = decode(SRC)
    for name, (out_s, ratio, direction) in WARPS.items():
        out = HERE / f"fs-whoosh-3-{name}.mp3"
        write_mp3(warp(x, out_s, ratio, direction), out)
        print(f"{out.name}: {out_s:.2f}s, rate {direction} x{ratio:g} on the min-jerk curve, from {SRC.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

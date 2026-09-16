"""Master the VO TONE of a take: the approved chain, a measured trim, a receipt and a gate.

The provider's take went straight into the timeline - the engine had no tone stage at all, and the only
loudness stage in the pipeline is the finished mix's `loudnorm` in the compositor. Measured in 1/3-octave
bands against two shipped references, our take is hot through 200-350 Hz and scooped at 800 Hz, at
2.5-3.2 kHz and above 6 kHz. This is the stage that answers that, with the chain the operator chose off
an A/B (chain G, 2026-09-16 - E99 s54, amending s48's chain C) and nothing else:
`authoring.audio.vo_tone_filter()` is the ruling, and this script never composes its own tone.

TONE IS RULED, LEVEL IS COMPUTED. The A/B was judged at matched loudness, so it settled tone and set no
level - and the chain as ruled is not level-neutral: on the Steel and Paper take it costs about a
decibel of integrated loudness while pushing the true peak to roughly 0 dBTP, which clips on the next
192k re-encode. So the stage measures the post-chain true peak and appends ONE flat `volume=` trim that
lands the written take on `VO_TP_TARGET_DBTP`. A flat gain moves every band by the same number: it
cannot change the tone the operator ruled on. No limiter, no loudnorm, no saturation, ever.

WHAT THE STAGE MUST NOT DO:

- it must not RETIME. The word timeline comes from the provider's timestamps; a take one frame longer
  than its timeline desynchronises captions, docks and choreography together (G1).
- it must not leave a STALE BED. `bed_gain(VO_LUFS, ...)` reads a hand-measured literal out of the
  episode's build script. Toning a take moves that number, and nothing else in the pipeline notices -
  the bed just sits at the wrong level under every cue. G2 re-measures and names the line to correct;
  the stage prints it paste-ready.

    python master_vo_tone.py [TAKE.mp3 ...]            # back up, tone, trim, write the receipt
    python master_vo_tone.py --verify [TAKE.mp3 ...]   # re-measure what is on disk, PASS/FAIL per check

With no paths it works on the episode's own takes. Another episode's build sets EP / TAKE_DIR, then
calls main(). The original is kept as `<name>.mp3.pretone` (the `.pre-cnbc` / `.prerepair` convention)
and the measurements land in `<name>.tone.json`.

Idempotence: refuses to run twice - a receipt recording this same chain means the take on disk is
already toned, and toning it again would double every dB of it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import audio_spectrum as S
from authoring import audio as A

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
TAKE_DIR = EP / "vo-f/audio"     # another episode's build sets EP / TAKE_DIR, then calls main()
TAKE_GLOB = "scene_*.mp3"

BACKUP_SUFFIX = ".pretone"
RECEIPT_SUFFIX = ".tone.json"
PROBE_BANDS = (280.0, 800.0, 1400.0, 2600.0, 8000.0, 11000.0)  # the chain's own corners, measured 1/3-octave wide

DUR_TOL_S = 0.005          # G1: the word timeline is the take's clock
VO_LUFS_TOL = 0.3          # G2: the bed hangs off a literal that has to still be true
TP_CEIL_DBTP = -1.0        # G3: headroom for the 192k re-encodes downstream
# G5: the computed trim actually landed. Wider than it looks it should be, on purpose: the trim is sized
# on the DECODED signal and the take is then written as 192k mp3, and a lossy encode moves the true peak
# by a couple of tenths either way (-1.77 dBTP for a -1.50 target on the Steel and Paper take). G3 is the
# requirement; this row only catches a trim that was never applied, which is off by a whole decibel.
TP_LAND_TOL = 0.5
# G4: (dB the chain should move the band, tolerance). Loose on purpose - this proves the chain LANDED,
# it is not a precision EQ check, and a 1/3-octave band is wider than any one of the chain's corners.
# The 8 kHz row is the +2 shelf and the skirt of the 11 kHz bell together, which is why it expects more
# than the shelf alone would give: under chain C the same row read +2.06 off a +3 shelf with no bell
# above it. Expectations are MEASURED off the ruled chain, not read off its nominal gains: a narrow bell is
# averaged across a 1/3-octave band wider than itself, so +5 at 800 Hz reads +3.2 and +6 at 2600 Hz
# reads +4.5.  The 11 kHz row is looser because encoder behaviour up there varies between takes.
BAND_TOL = {280.0: (-3.2, 1.0), 800.0: (3.2, 1.5), 1400.0: (-2.8, 1.5),
            2600.0: (4.5, 1.5), 8000.0: (3.8, 1.5), 11000.0: (7.0, 2.0)}
LOUDNORM_JSON = re.compile(r"\{[^{}]*\}")
VO_LUFS_DECL = re.compile(r"^\s*(VO_LUFS\b[^=]*)=([^#\n]+)")
SEARCH_DEPTH = 4           # ancestors of the take to read for a VO_LUFS literal: audio/ -> vo-f/ -> the episode
PASS, FAIL, NA = "PASS", "FAIL", "n/a "


def measure_loudness(path: Path, chain: str | None = None) -> dict[str, float]:
    """(integrated LUFS, true peak dBTP), from ffmpeg's own loudnorm MEASURING pass - to null, never to
    a file. `chain` measures what the file WOULD be after that filter, which is how the trim is sized."""
    prefix = f"{chain}," if chain else ""
    err = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(path), "-af",
                          f"{prefix}loudnorm=I=-14:LRA=11:TP=-1.5:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    blocks = LOUDNORM_JSON.findall(err)
    if not blocks:
        raise ValueError(f"ffmpeg loudnorm measured nothing on {path.name}")
    j = json.loads(blocks[-1])
    return {"lufs": float(j["input_i"]), "tp_dbtp": float(j["input_tp"])}


def mp3_format(path: Path) -> dict[str, str]:
    """The take's own codec, rate, channels and bitrate - re-encoded in ANY other shape it is a new
    master, not a toned one. Refuses by name anything that is not the mp3 the provider writes."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                          "stream=codec_name,sample_rate,channels,bit_rate", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    st = json.loads(out)["streams"][0]
    if st["codec_name"] != "mp3":
        raise ValueError(f"{path.name} is {st['codec_name']}, not mp3 - this stage masters provider takes")
    return {"rate": str(st["sample_rate"]), "channels": str(st["channels"]),
            "bitrate": f"{round(int(st.get('bit_rate') or 192000) / 1000)}k"}


def measure(path: Path) -> dict:
    """Everything the receipt and the gate read off one file: clock, level, and the band shape."""
    x = S.decode_mono(path)
    return {"duration_s": round(A.probe_duration(path), 6), **measure_loudness(path),
            "bands_db": S.to_json(S.band_levels(x, centres=list(PROBE_BANDS), shape=False)),
            "bands_third_octave_db_re_broadband": S.to_json(S.band_levels(x))}


def apply_tone(src: Path, dst: Path, fmt: dict[str, str], applied: str) -> None:
    """One ffmpeg pass, the take's own format out, written to a temp file first so a failure never
    leaves half a master on disk."""
    tmp = dst.with_name(dst.stem + ".part" + dst.suffix)   # ffmpeg picks the muxer off the extension
    subprocess.run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-i", str(src), "-af", applied,
                    "-c:a", "libmp3lame", "-b:a", fmt["bitrate"], "-ar", fmt["rate"],
                    "-ac", fmt["channels"], str(tmp)], check=True)
    tmp.replace(dst)


def episode_vo_lufs(take: Path) -> tuple[Path, int, float] | None:
    """(file, line, value) of the `VO_LUFS` literal the take's episode hangs its bed from, or None when
    the episode wires no bed (the long-form cut declares none). Read off the source, because that
    literal IS the contract: `bed_gain` has no way to know the take under it was re-mastered."""
    for folder in take.resolve().parents[:SEARCH_DEPTH]:
        for src in sorted(folder.glob("*.py")):
            for n, line in enumerate(src.read_text(encoding="utf-8").splitlines(), start=1):
                m = VO_LUFS_DECL.match(line)
                if m:
                    names = [t.strip() for t in m.group(1).split(",")]
                    return src, n, float(m.group(2).split(",")[names.index("VO_LUFS")])
        if folder == REPO:
            break
    return None


def repo_path(p: Path) -> str:
    """Repo-relative when it can be (the form an agent pastes into a grep), absolute when it cannot -
    a take mastered in a scratch directory still has to name its file."""
    try:
        return p.relative_to(REPO).as_posix()
    except ValueError:
        return p.as_posix()


def vo_lufs_line(take: Path, lufs: float) -> str:
    """The literal to paste, so correcting the bed is mechanical rather than remembered."""
    return f"VO_LUFS = {lufs:.1f}   # {take}, post-tone, measured {dt.date.today().isoformat()}"


def band_row(name: str, fc: float, delta: float) -> tuple[str, str, str]:
    """One band of G4. The flat trim is already removed by the caller: it is level, not tone."""
    want, tol = BAND_TOL[fc]
    return (f"{name}  {fc:>6.0f} Hz  {want:+.1f} dB +/-{tol:.1f}",
            PASS if abs(delta - want) <= tol else FAIL, f"{delta:+.2f} dB")


def vo_lufs_row(take: Path, lufs: float) -> tuple[str, str, str]:
    """G2. The failure this catches: a take is toned, the literal is not, and the bed sits at the wrong
    level under every cue with nothing to say so. An episode with no literal wires no bed."""
    label = f"G2  VO_LUFS literal is the toned take (+/-{VO_LUFS_TOL:.1f} LU)"
    found = episode_vo_lufs(take)
    if found is None:
        return label, NA, "this episode wires no bed"
    src, n, declared = found
    d = lufs - declared
    return (label, PASS if abs(d) <= VO_LUFS_TOL else FAIL,
            f"{declared:.1f} declared vs {lufs:.2f} measured ({d:+.2f} LU) - {repo_path(src)}:{n}")


def gate_rows(take: Path, before: dict, after: dict, makeup_db: float) -> list[tuple[str, str, str]]:
    """One named row per check: (label, PASS|FAIL|n/a, the measured number). G1 clock, G2 the bed's
    literal, G3 headroom, G4a-d the chain's own corners, G5 the computed trim."""
    d_ms = (after["duration_s"] - before["duration_s"]) * 1000
    target, landed = A.VO_TP_TARGET_DBTP, after["tp_dbtp"]
    rows = [(f"G1  duration unchanged (+/-{DUR_TOL_S * 1000:.0f} ms)",
             PASS if abs(d_ms) <= DUR_TOL_S * 1000 else FAIL,
             f"{before['duration_s']:.3f} -> {after['duration_s']:.3f} s ({d_ms:+.1f} ms)"),
            vo_lufs_row(take, after["lufs"]),
            (f"G3  true peak <= {TP_CEIL_DBTP:.1f} dBTP", PASS if landed <= TP_CEIL_DBTP else FAIL,
             f"{before['tp_dbtp']:.2f} -> {landed:.2f} dBTP")]
    deltas = S.band_deltas({float(k): v for k, v in before["bands_db"].items()},
                           {float(k): v for k, v in after["bands_db"].items()})
    rows += [band_row(f"G4{c}", fc, deltas[fc] - makeup_db) for c, fc in zip("abcdef", PROBE_BANDS)]
    rows.append((f"G5  the trim landed on {target:.1f} dBTP (+/-{TP_LAND_TOL:.1f})",
                 PASS if abs(landed - target) <= TP_LAND_TOL else FAIL, f"{makeup_db:+.2f} dB applied"))
    return rows


def report_text(take: Path, rows: list[tuple[str, str, str]]) -> str:
    n_fail = sum(1 for _, status, _ in rows if status == FAIL)
    body = "\n".join(f"  {label:<49} {status}   {value}" for label, status, value in rows)
    return (f"VO TONE GATE - {take.name}\n{body}\n"
            f"VERDICT: {'FAIL' if n_fail else 'PASS'} ({n_fail} FAIL)")


def tone_one(take: Path, chain: str) -> int:
    """Back up, size the trim, tone in place, write the receipt. Refuses a take already toned."""
    backup, receipt = take.with_suffix(take.suffix + BACKUP_SUFFIX), take.with_name(take.stem + RECEIPT_SUFFIX)
    if receipt.exists() and json.loads(receipt.read_text(encoding="utf-8")).get("filter") == chain:
        print(f"{take.name}: {receipt.name} already records this chain - the take on disk is toned. "
              f"Refusing to tone it twice (it would double every dB). "
              f"Restore {backup.name} over it to start again.")
        return 1
    if backup.exists():
        print(f"{take.name}: {backup.name} exists without a matching receipt - refusing to overwrite "
              f"the only untoned copy. Sort the backup out by hand first.")
        return 1
    fmt, before = mp3_format(take), measure(take)
    shutil.copy2(take, backup)
    # the same measuring pass that sizes the trim also records what the RULED chain alone did to the
    # level: the operator ruled on tone, so the level effect is reported, not hidden inside the trim
    chain_only = measure_loudness(backup, chain)
    makeup_db = A.vo_makeup_db(chain_only["tp_dbtp"])
    applied = A.vo_tone_filter(makeup_db)
    try:
        apply_tone(backup, take, fmt, applied)
    except (subprocess.CalledProcessError, OSError) as e:
        backup.unlink(missing_ok=True)   # the take is untouched; leave no backup to block the retry
        print(f"{take.name}: ffmpeg refused the chain - {e}")
        return 1
    after = measure(take)
    receipt.write_text(json.dumps({"take": take.name, "filter": chain, "applied": applied,
                                   "makeup_db": makeup_db, "target_tp_dbtp": A.VO_TP_TARGET_DBTP,
                                   "measured_on": dt.date.today().isoformat(), "source": backup.name,
                                   "format": fmt, "input": before, "chain_only": chain_only,
                                   "output": after}, indent=1),
                       encoding="utf-8")
    print(f"{take.name}: toned ({backup.name} kept); {before['lufs']:.2f} -> {after['lufs']:.2f} LUFS, "
          f"peak {before['tp_dbtp']:.2f} -> {after['tp_dbtp']:.2f} dBTP on a {makeup_db:+.2f} dB trim, "
          f"{after['duration_s']:.3f} s -> {receipt.name}")
    print(f"  the ruled chain alone, before the trim: {chain_only['lufs']:.2f} LUFS, "
          f"{chain_only['tp_dbtp']:.2f} dBTP")
    print(f"  the bed hangs off this - paste it over the episode's literal:\n    {vo_lufs_line(take, after['lufs'])}")
    return 0


def verify_one(take: Path, chain: str) -> int:
    """Re-measure the backup AND the take as they sit on disk - the receipt's own numbers are not
    evidence - and print a PASS/FAIL row per check. Non-zero on any FAIL."""
    backup, receipt = take.with_suffix(take.suffix + BACKUP_SUFFIX), take.with_name(take.stem + RECEIPT_SUFFIX)
    for p in (backup, receipt):
        if not p.exists():
            print(f"{take.name}: no {p.name} - nothing to verify; run the stage first.")
            return 1
    rec = json.loads(receipt.read_text(encoding="utf-8"))
    rows = [("G0  the receipt records the approved chain", PASS if rec.get("filter") == chain else FAIL,
             "the ruling, verbatim" if rec.get("filter") == chain else str(rec.get("filter")))]
    after = measure(take)
    rows += gate_rows(take, measure(backup), after, float(rec.get("makeup_db") or 0.0))
    print(report_text(take, rows))
    failed = [label for label, status, _ in rows if status == FAIL]
    if any(label.startswith("G2") for label in failed):
        print(f"  G2 fixes itself by one edit:\n    {vo_lufs_line(take, after['lufs'])}")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("takes", nargs="*", type=Path, help=f"take mp3s (default {TAKE_GLOB} in the episode)")
    ap.add_argument("--verify", action="store_true", help="re-measure what is on disk and gate it")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    takes = list(args.takes) or sorted(TAKE_DIR.glob(TAKE_GLOB))
    if not takes:
        print(f"no takes: nothing matched {TAKE_GLOB} in {TAKE_DIR}")
        return 1
    chain = A.vo_tone_filter()
    run = verify_one if args.verify else tone_one
    return max(run(t, chain) for t in takes)


if __name__ == "__main__":
    raise SystemExit(main())

"""Deterministic frame-capture render of the scene-evidence player.

Remotion's method, our engine: headless Chromium seeks the player to
t = frame/fps (the template law says render(t) fully resolves from t),
screenshots #stage at deviceScaleFactor 4/3 (1920x1080 stage -> exact
2560x1440 pixels), pipes PNGs into ffmpeg/libx264, then muxes the
separately-mixed audio (VO master + SOUND-PLAN cues, loudnorm to
YouTube -14 LUFS / -1 dBTP).

    python render_episode.py --test          # 8s proof slice at the verdict stack
    python render_episode.py                 # full episode
    python render_episode.py --t0 0 --t1 30  # arbitrary slice
    python render_episode.py --force         # full episode past a motion-gate FAIL

A full render first reads build-f/GATES-MOTION.md (written by
build_scene_timeline_f.py) and refuses with exit 2 while it says FAIL
(ruling E21 / doc 29 s9.25). Slices, --test and shard workers never block.

Requires the episode-player server on :8731 (preview harness).
"""
import argparse, hashlib, json, re, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # render_baseline.prepare_page (P39 T6)

REPO = Path(__file__).resolve().parents[3]
import os
# Another episode renders by setting these (env, Tokyo 2026-09-04): RENDER_BUILD=<build dir>,
# RENDER_URL=<player url on its own preview server>, RENDER_NAME=<output stem>.
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
BUILD = Path(os.environ.get("RENDER_BUILD") or (EP / "build-f"))
OUT = BUILD / "render"
FPS = 30
URL = os.environ.get("RENDER_URL") or "http://127.0.0.1:8731/player.html"
NAME = os.environ.get("RENDER_NAME") or "steel-and-paper"
GATE_REPORT = "GATES-MOTION.md"  # gate_motion_density.write_report output; last line VERDICT: PASS|FAIL
GATE_REFUSED = 2                 # exit code: the gate refused, nothing was captured
FORCE_RECORD = "FORCED-RENDER.md"  # render/FORCED-RENDER.md: every --force with its reason


def _env_volume(c: dict) -> str:
    """The cue's `volume=` argument: its gain, times its ENVELOPE (`env` = [[t, dB], ...] against the gain, linear between
    keys, flat outside them) as a per-frame ffmpeg expression in the CLIP's own time (the cue is delayed by `at` after this
    filter, so every key shifts by -at). The same function the player runs (`envGain`) - the render must carry what the
    strip played (the bed breathes over a thrown card's landing; the bed blueprint, rule 3; 2026-09-08)."""
    env = c.get("env") or []
    if not env:
        return str(c["gain"])
    at = float(c["at"])
    keys = [(float(t) - at, float(db)) for t, db in env]
    expr = str(keys[-1][1])
    for (t0, d0), (t1, d1) in reversed(list(zip(keys, keys[1:]))):
        seg = f"({d0}+({d1}-{d0})*(t-{t0})/{t1 - t0})" if t1 > t0 else str(d1)
        expr = f"if(lt(t,{t1}),{seg},{expr})"
    expr = f"if(lt(t,{keys[0][0]}),{keys[0][1]},{expr})"
    return f"'{c['gain']}*pow(10,({expr})/20)':eval=frame"


def mix_audio(dur: float) -> Path:
    OUT.mkdir(exist_ok=True)
    # the episode is the build's parent, its VO is the file the timeline names (Tokyo, 2026-09-04:
    # this read ep1's plan and ep1's take for every episode - the wrong audio under the short)
    ep = BUILD.parent
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    vo = BUILD / (tl.get("paused_audio", "audio/episode-paused.mp3") if tl.get("edit_pauses_applied") else "audio/episode.mp3")
    plan_p = ep / "sound/SOUND-PLAN.json"
    plan = json.loads(plan_p.read_text(encoding="utf-8")) if plan_p.exists() else {"cues": []}
    inputs = ["-i", str(vo)]
    chains, mix = [], ["[0:a]"]
    for i, c in enumerate(plan["cues"], start=1):
        clip = ep / "sound" / c["variants"]["A"]
        inputs += ["-i", str(clip)]
        fade = f",afade=t=in:d={c['fade_in']}" if c.get("fade_in") else ""
        delay = int(round(c["at"] * 1000))
        chains.append(f"[{i}:a]volume={_env_volume(c)}{fade},adelay={delay}|{delay}[c{i}]")
        mix.append(f"[c{i}]")
    fc = (";".join(chains) + ";" + "".join(mix)
          + f"amix=inputs={len(mix)}:duration=first:normalize=0,"
          + "loudnorm=I=-14:TP=-1:LRA=11,aresample=48000[out]")
    out = OUT / "episode-mix.m4a"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs,
                    "-filter_complex", fc, "-map", "[out]", "-t", f"{dur:.3f}",
                    "-c:a", "aac", "-b:a", "320k", str(out)], check=True)
    return out


# the stage: 1920x1080 (16:9) or 1080x1920 (RENDER_ASPECT=9:16, a short) - captured at device scale 4/3
STAGE_W, STAGE_H = (1080, 1920) if os.environ.get("RENDER_ASPECT") == "9:16" else (1920, 1080)
RAW_W, RAW_H = STAGE_W * 4 // 3, STAGE_H * 4 // 3  # #stage at device_scale_factor 4/3 (2560x1440 / 1440x2560)


def capture(t0: float, t1: float, video_out: Path) -> None:
    from playwright.sync_api import sync_playwright
    n = int(round((t1 - t0) * FPS))
    # RAW RGB pipe, not PNG: a PNG can survive PIL validation in-process yet
    # be corrupted in the pipe under concurrent memory pressure, and ffmpeg's
    # deflate parser then dies with "inflate error -3". Raw pixels have no
    # deflate stream, so that failure mode cannot exist. PIL decodes the
    # (validated) screenshot to pixels; we ship pixels.
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{RAW_W}x{RAW_H}", "-framerate", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", str(video_out)], stdin=subprocess.PIPE)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_context(
            viewport={"width": STAGE_W, "height": STAGE_H},
            device_scale_factor=4 / 3).new_page()
        page.goto(URL, wait_until="networkidle", timeout=120000)
        # P39 T6: the one capture path. prepare_page kills the review chrome, mutes VO,
        # awaits fonts, switches wall-clock transitions off and sizes #fit to the stage so
        # the stage is captured at 1920x1080 CSS px = 2560x1440 device px. Before this the
        # stage was fit-scaled to ~1398px and every frame was LANCZOS-upscaled (B8).
        from render_baseline import prepare_page, frame_png
        prepare_page(page, STAGE_W, STAGE_H)
        t_start = time.time()
        import io as _io
        from PIL import Image as _Img

        def frame_rgb(buf: bytes):
            # decode screenshot -> exact-size RGB pixel bytes; returns None if
            # the screenshot itself came back corrupt (then we re-shoot). A wrong
            # size is a geometry regression, not corruption - it raises, it is
            # never resized away (that resize hid B8 for the whole of ep1).
            try:
                im = _Img.open(_io.BytesIO(buf)).convert("RGB")
            except Exception:
                return None
            if im.size != (RAW_W, RAW_H):
                raise RuntimeError(f"stage captured at {im.size}, expected {(RAW_W, RAW_H)} - fitStage is scaling again")
            return im.tobytes()

        for i in range(n):
            t = t0 + i / FPS
            rgb = frame_rgb(frame_png(page, t, (STAGE_W, STAGE_H)))
            tries = 0
            while rgb is None:
                tries += 1
                if tries > 8:
                    raise RuntimeError(f"corrupt frame at t={t:.3f} after 8 retries")
                time.sleep(0.15)
                rgb = frame_rgb(frame_png(page, t, (STAGE_W, STAGE_H)))
            try:
                enc.stdin.write(rgb)
            except OSError as e:
                raise RuntimeError(f"encoder pipe closed at t={t:.3f}: {e}")
            if i and i % 300 == 0:
                rate = i / (time.time() - t_start)
                eta = (n - i) / rate / 60
                print(f"  frame {i}/{n}  {rate:.1f} fps  eta {eta:.0f} min", flush=True)
        browser.close()
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("ffmpeg encode failed")


def capture_frames(f0: int, f1: int, video_out: Path) -> None:
    """Worker entry: capture global frames [f0, f1) to one x264 segment."""
    capture(f0 / FPS, f1 / FPS, video_out)


def parallel_render(n_frames: int, workers: int, video_out: Path) -> None:
    """Remotion's speed trick: shard the timeline across concurrent
    headless browsers, one x264 segment each, concat losslessly."""
    chunk = -(-n_frames // workers)
    parts, procs = [], []
    for w in range(workers):
        a, b = w * chunk, min((w + 1) * chunk, n_frames)
        if a >= b:
            break
        part = OUT / f"part-{w:02d}.mp4"
        parts.append(part)
        procs.append(subprocess.Popen(
            [sys.executable, __file__, "--frames", str(a), str(b),
             "--part", str(part)]))
    fails = [p.wait() for p in procs]
    if any(fails):
        raise RuntimeError(f"shard exit codes: {fails}")
    lst = OUT / "parts.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts),
                   encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c", "copy", str(video_out)], check=True)


def _report_timeline_hash(lines: list[str]) -> tuple[str, str] | None:
    """(timeline file name, sha256) from the report's `TIMELINE: <name> sha256:<hex>` line, if written."""
    for line in lines:
        m = re.match(r"TIMELINE: (\S+) sha256:([0-9a-f]{64})", line)
        if m:
            return m.group(1), m.group(2)
    return None


def _record_force(reason: str, why: str) -> None:
    """The override goes on the record beside the renders, like the recorder's manifest (P34 HG3)."""
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with (OUT / FORCE_RECORD).open("a", encoding="utf-8") as fh:
        fh.write(f"- {stamp} forced full render over `{why}` - reason: {reason}\n")


def motion_gate_verdict(force: str | None) -> int | None:
    """E21 / doc 29 s9.25: consult build-f/GATES-MOTION.md before a FULL render.

    Returns an exit code to stop on, or None to proceed. Missing report ->
    the build never ran the gate; STALE (the report's timeline hash no longer
    matches the timeline on disk) or FAIL -> refuse unless `--force "<reason>"`,
    which is printed and appended to render/FORCED-RENDER.md so the override
    is on the record. A bare --force (no reason) is refused."""
    report = BUILD / GATE_REPORT
    if not report.exists():
        print("MOTION GATE: no report - run build_scene_timeline_f.py first")
        return GATE_REFUSED
    lines = report.read_text(encoding="utf-8").splitlines()
    verdict = next((l for l in reversed(lines) if l.startswith("VERDICT:")), None)
    if verdict is None:
        print(f"MOTION GATE: {report} carries no VERDICT line - rebuild")
        return GATE_REFUSED
    why = None
    hashed = _report_timeline_hash(lines)
    if hashed:
        name, want = hashed
        tl_path = BUILD / name
        have = hashlib.sha256(tl_path.read_bytes()).hexdigest() if tl_path.exists() else "missing"
        if have != want:
            why = f"STALE report: {name} on disk is not the timeline the gate measured (rebuild)"
    if why is None and verdict.startswith("VERDICT: FAIL"):
        why = verdict
    if why is None:
        return None
    if force is not None:
        if not force.strip():
            print("MOTION GATE: --force needs a reason - `--force \"<why this render ships over the gate>\"`")
            return GATE_REFUSED
        print(f"[FORCED] motion gate FAIL overridden ({why}) - reason: {force.strip()}")
        _record_force(force.strip(), why)
        return None
    print(f"MOTION GATE: {report}")
    print(f"MOTION GATE: {why} - refusing full render (E21); re-run with --force \"<reason>\" to override")
    return GATE_REFUSED


def is_full_render(args: argparse.Namespace, dur: float) -> bool:
    """Full = the whole runtime from 0, whether --t1 is omitted or names the
    runtime (or past it); --test and true slices never block."""
    return not args.test and args.t0 == 0.0 and (args.t1 is None or args.t1 >= dur)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=None)
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--force", nargs="?", const="", default=None, metavar="REASON",
                    help="full render even when GATES-MOTION.md is FAIL or stale; the reason is required and recorded")
    ap.add_argument("--workers", type=int, default=4)  # 4 for memory headroom; full PIL decode-verify guards the rest
    ap.add_argument("--frames", type=int, nargs=2, help="worker mode: global frame range")
    ap.add_argument("--part", type=str, help="worker mode: segment output path")
    args = ap.parse_args()
    if args.frames:  # shard worker
        capture_frames(args.frames[0], args.frames[1], Path(args.part))
        return 0
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    dur = float(tl["runtime_s"])
    if is_full_render(args, dur):
        stop = motion_gate_verdict(args.force)
        if stop is not None:
            return stop
    if args.test:
        t0, t1 = 699.0, 707.0
    else:
        t0, t1 = args.t0, (args.t1 if args.t1 is not None else dur)
    OUT.mkdir(exist_ok=True)
    tag = "test" if args.test else ("full" if (t0, t1) == (0.0, dur) else f"{t0:.0f}-{t1:.0f}")
    video = OUT / f"video-{tag}.mp4"
    final = OUT / f"{NAME}-{tag}-1440p.mp4"
    n = int(round((t1 - t0) * FPS))
    print(f"capture {t0:.2f}-{t1:.2f}s @ {FPS}fps x{args.workers} workers -> {video.name}")
    if args.workers > 1 and t0 == 0.0:
        parallel_render(n, args.workers, video)
    else:
        capture(t0, t1, video)
    print("mixing audio...")
    audio = mix_audio(dur)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video),
                    "-ss", f"{t0:.3f}", "-i", str(audio), "-t", f"{t1 - t0:.3f}",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy",
                    str(final)], check=True)
    print("done:", final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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

Requires the episode-player server on :8731 (preview harness).
"""
import argparse, json, re, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
OUT = EP / "build-f/render"
FPS = 30
URL = "http://127.0.0.1:8731/player.html"


def mix_audio(dur: float) -> Path:
    OUT.mkdir(exist_ok=True)
    plan = json.loads((EP / "sound/SOUND-PLAN.json").read_text(encoding="utf-8"))
    inputs = ["-i", str(EP / "build-f/audio/episode-paused.mp3")]
    chains, mix = [], ["[0:a]"]
    for i, c in enumerate(plan["cues"], start=1):
        clip = EP / "sound" / c["variants"]["A"]
        inputs += ["-i", str(clip)]
        fade = f",afade=t=in:d={c['fade_in']}" if c.get("fade_in") else ""
        delay = int(round(c["at"] * 1000))
        chains.append(f"[{i}:a]volume={c['gain']}{fade},adelay={delay}|{delay}[c{i}]")
        mix.append(f"[c{i}]")
    fc = (";".join(chains) + ";" + "".join(mix)
          + f"amix=inputs={len(mix)}:duration=first:normalize=0,"
          + "loudnorm=I=-14:TP=-1:LRA=11,aresample=48000[out]")
    out = OUT / "episode-mix.m4a"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs,
                    "-filter_complex", fc, "-map", "[out]", "-t", f"{dur:.3f}",
                    "-c:a", "aac", "-b:a", "320k", str(out)], check=True)
    return out


def capture(t0: float, t1: float, video_out: Path) -> None:
    from playwright.sync_api import sync_playwright
    n = int(round((t1 - t0) * FPS))
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS),
         "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", "-vf", "scale=2560:1440:flags=lanczos",
         str(video_out)], stdin=subprocess.PIPE)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=4 / 3).new_page()
        page.goto(URL, wait_until="networkidle", timeout=120000)
        page.wait_for_selector("#stage", timeout=60000)
        page.evaluate("document.fonts.ready.then(()=>1)")
        page.evaluate("document.getElementById('vo').muted = true")
        # kill the review chrome so it never bleeds into a capture
        page.evaluate("for (const id of ['sndbar']) { const e=document.getElementById(id); if (e) e.style.display='none'; }")
        stage = page.locator("#stage")
        t_start = time.time()
        PNG_SIG = b"\x89PNG\r\n\x1a\n"
        IEND = b"\x49\x45\x4e\x44\xae\x42\x60\x82"
        for i in range(n):
            t = t0 + i / FPS
            page.evaluate(
                "t => { const s = document.getElementById('scrub');"
                " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
            # validate each frame is a complete PNG (sig + IEND terminator);
            # under heavy worker concurrency a screenshot can come back
            # truncated and ffmpeg's inflate dies mid-render. Re-shoot.
            png = stage.screenshot(type="png")
            tries = 0
            while not (png[:8] == PNG_SIG and png[-8:] == IEND):
                tries += 1
                if tries > 5:
                    raise RuntimeError(f"corrupt frame at t={t:.3f} after 5 retries")
                time.sleep(0.1)
                png = stage.screenshot(type="png")
            enc.stdin.write(png)
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=None)
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--workers", type=int, default=6)  # 6 << 8 contention; retry guard covers the rest
    ap.add_argument("--frames", type=int, nargs=2, help="worker mode: global frame range")
    ap.add_argument("--part", type=str, help="worker mode: segment output path")
    args = ap.parse_args()
    if args.frames:  # shard worker
        capture_frames(args.frames[0], args.frames[1], Path(args.part))
        return 0
    tl = json.loads((EP / "build-f/timeline.json").read_text(encoding="utf-8"))
    dur = float(tl["runtime_s"])
    if args.test:
        t0, t1 = 699.0, 707.0
    else:
        t0, t1 = args.t0, (args.t1 if args.t1 is not None else dur)
    OUT.mkdir(exist_ok=True)
    tag = "test" if args.test else ("full" if (t0, t1) == (0.0, dur) else f"{t0:.0f}-{t1:.0f}")
    video = OUT / f"video-{tag}.mp4"
    final = OUT / f"steel-and-paper-{tag}-1440p.mp4"
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

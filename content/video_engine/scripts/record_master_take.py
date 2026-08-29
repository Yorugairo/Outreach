"""Steel and Paper — Script C MASTER TAKE.

Doc 37 section 8: one request, no splicing. Every precondition is checked
BEFORE the paid call; the call is skipped entirely unless all pass.
Run with --go to actually spend credits; without it, preflight only.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

REPO = Path(r"C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16")
ENV_FILE = Path(r"C:\Users\Snipe\Downloads\Outreach Program\docs\local.env")
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
VO_TEXT = EP / "SCRIPT-C-VO.txt"
OUT = EP / "vo-c"
AUDIO_DIR = OUT / "audio"
CACHE_DIR = OUT / "cache"
SEED = "4242"
# A master take renders ~8 min of audio; the library defaults (60s timeout,
# 3 attempts) were sized for ~1k-char scene segments. On a long request the
# client gives up mid-generation and RETRIES — and every retry is charged.
# One attempt, generous timeout. A retry here is a cost multiplier, not a
# safety net.
TIMEOUT_S = "900"
MAX_ATTEMPTS = "1"
SETTINGS = {"stability": 0.40, "similarity_boost": 0.75, "style": 0.20,
            "use_speaker_boost": True}
MV2_CAP = 10000

sys.path.insert(0, str(REPO))


def load_env(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def credits_remaining(api_key: str) -> tuple[int, int] | None:
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/user/subscription",
        headers={"xi-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read().decode())
        return d.get("character_count"), d.get("character_limit")
    except Exception as e:
        print(f"    (could not read subscription: {type(e).__name__})")
        return None


def main() -> int:
    go = "--go" in sys.argv
    fails: list[str] = []

    print("=== PREFLIGHT ===")

    # 1. env + key
    if not ENV_FILE.exists():
        fails.append(f"env file missing: {ENV_FILE}")
    else:
        load_env(ENV_FILE)
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    voice = os.environ.get("ELEVENLABS_VOICE_ID", "")
    print(f"  [{'ok' if key else 'FAIL'}] API key present ({len(key)} chars, not shown)")
    print(f"  [{'ok' if voice else 'FAIL'}] voice id present")
    if not key:
        fails.append("ELEVENLABS_API_KEY missing")
    if not voice:
        fails.append("ELEVENLABS_VOICE_ID missing")

    # 2. script text
    if not VO_TEXT.exists():
        fails.append(f"VO text missing: {VO_TEXT}")
        text = ""
    else:
        text = VO_TEXT.read_text(encoding="utf-8").strip()
    spoken = re.sub(r"`?\[(?:pre|post)-key\]`?", "", text)
    spoken = re.sub(r"\s+", " ", spoken).strip()
    n = len(spoken)
    print(f"  [{'ok' if 0 < n <= MV2_CAP else 'FAIL'}] spoken chars {n:,} (mv2 cap {MV2_CAP:,})")
    if not (0 < n <= MV2_CAP):
        fails.append(f"character count {n} outside 1..{MV2_CAP} — master take impossible")

    # 3. no stray editorial flags reaching the voice
    stray = set(re.findall(r"\[([a-z][a-z-]*)\]", text)) - {"pre-key", "post-key"}
    print(f"  [{'ok' if not stray else 'FAIL'}] no stray editorial flags {sorted(stray) if stray else ''}")
    if stray:
        fails.append(f"stray flags would be spoken: {sorted(stray)}")

    # 4. break ration
    breaks = len(re.findall(r"\[(?:pre|post)-key\]", text))
    ration = breaks / (n / 1000) if n else 99
    print(f"  [{'ok' if ration <= 3 else 'FAIL'}] break ration {ration:.2f}/1k (limit 3.0, {breaks} tags)")
    if ration > 3:
        fails.append(f"break ration {ration:.2f} exceeds 3.0 — causes audible speed-ups")

    # 5. directories exist BEFORE the paid call (this is what cost credits last time)
    for d in (AUDIO_DIR, CACHE_DIR):
        d.mkdir(parents=True, exist_ok=True)
    print(f"  [{'ok' if AUDIO_DIR.is_dir() and CACHE_DIR.is_dir() else 'FAIL'}] "
          f"audio + cache dirs exist")
    if not (AUDIO_DIR.is_dir() and CACHE_DIR.is_dir()):
        fails.append("output dirs could not be created")

    # 6. pause compilation round-trips
    try:
        from content.video_engine.src.services.audio_synth import compile_pause_marks
        compiled = compile_pause_marks(text)
        ok_compile = "[pre-key]" not in compiled and "[post-key]" not in compiled
        print(f"  [{'ok' if ok_compile else 'FAIL'}] pause marks compile to break tags")
        if not ok_compile:
            fails.append("pause marks did not compile")
    except Exception as e:
        print(f"  [FAIL] compile_pause_marks: {type(e).__name__}: {e}")
        fails.append("compile_pause_marks raised")

    # 7. credits
    if key:
        c = credits_remaining(key)
        if c and c[0] is not None and c[1] is not None:
            used, limit = c
            left = limit - used
            enough = left >= n
            print(f"  [{'ok' if enough else 'FAIL'}] credits: {left:,} remaining, "
                  f"need {n:,}")
            if not enough:
                fails.append(f"insufficient credits: {left} < {n}")

    # 8. timeout must fit the generation, or retries will burn credits for nothing
    need_s = n / 20.0                      # ~20 chars/sec generation, conservative
    t = float(TIMEOUT_S)
    print(f"  [{'ok' if t >= need_s else 'FAIL'}] timeout {t:.0f}s vs "
          f"~{need_s:.0f}s needed to render {n:,} chars; attempts={MAX_ATTEMPTS}")
    if t < need_s:
        fails.append(f"timeout {t}s too short for {n} chars — retries would be charged")

    print()
    if fails:
        print("PREFLIGHT FAILED — nothing spent:")
        for f in fails:
            print("   -", f)
        return 1
    print("PREFLIGHT CLEAN.")

    if not go:
        print("\nDry run. Re-run with --go to record the master take.")
        return 0

    # ---- the single paid call -------------------------------------------
    os.environ["ELEVENLABS_SEED"] = SEED
    os.environ["ELEVENLABS_TIMEOUT_S"] = TIMEOUT_S
    os.environ["ELEVENLABS_MAX_ATTEMPTS"] = MAX_ATTEMPTS
    from content.video_engine.src.services.audio_synth import (
        AudioSynthService, ElevenLabsConfig)
    config = ElevenLabsConfig.from_env()
    service = AudioSynthService(config=config)
    print(f"\n=== MASTER TAKE === model={config.model_id} seed={SEED} "
          f"voice={config.voice_id[:6]}… chars={n:,}")
    result = service.synthesize_scene(
        1, text, voice_id=config.voice_id, settings=SETTINGS,
        audio_dir=AUDIO_DIR, cache_dir=CACHE_DIR, config=config)
    print(f"  duration     : {result.duration_s:.1f}s ({result.duration_s/60:.1f} min)")
    print(f"  characters   : {result.character_count:,}")
    print(f"  request id   : {result.request_id}")
    print(f"  audio        : {result.audio_path}")
    words = getattr(result, "words", None) or getattr(result, "word_timings", None)
    if words:
        print(f"  word timings : {len(words)} words")
    manifest = OUT / "master-take.json"
    manifest.write_text(json.dumps({
        "script": VO_TEXT.name, "seed": SEED, "model": config.model_id,
        "characters": result.character_count, "duration_s": result.duration_s,
        "request_id": result.request_id, "audio": str(result.audio_path),
        "settings": SETTINGS, "single_request": True,
    }, indent=2), encoding="utf-8")
    print(f"  manifest     : {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

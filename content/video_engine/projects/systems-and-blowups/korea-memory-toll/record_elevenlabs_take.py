"""Korea Memory Toll — ElevenLabs Master Take Runner.

Doc 37 §8: Single take, no splicing. Preconditions checked before the paid call.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

# Paths
REPO = Path(r"C:\Users\Snipe\Downloads\Outreach Program")
ENV_FILE = REPO / "docs/local.env"
EP = REPO / "content/video_engine/projects/systems-and-blowups/korea-memory-toll"
VO_TEXT = EP / "SCRIPT-90S-VO.txt"
OUT = EP / "audio/master"
AUDIO_DIR = OUT
CACHE_DIR = OUT / ".cache"

SEED = os.environ.get("RECORD_SEED_OVERRIDE", "4242")
TIMEOUT_S = "900"
MAX_ATTEMPTS = "1"
SETTINGS = {
    "stability": 0.40,
    "similarity_boost": 0.75,
    "style": 0.20,
    "use_speaker_boost": True,
}
MV2_CAP = 10_000

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
        headers={"xi-api-key": api_key},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read().decode())
        return d.get("character_count"), d.get("character_limit")
    except Exception as e:
        print(f"    (could not read subscription: {type(e).__name__}: {e})")
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

    os.environ["ELEVENLABS_NO_BREAK_TAGS"] = "1"
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    voice = os.environ.get("ELEVENLABS_VOICE_ID", "")
    print(f"  [{'ok' if key else 'FAIL'}] API key present ({len(key)} chars)")
    print(f"  [{'ok' if voice else 'FAIL'}] Voice ID present: {voice}")
    if not key:
        fails.append("ELEVENLABS_API_KEY missing")
    if not voice:
        fails.append("ELEVENLABS_VOICE_ID missing")

    # 2. script text
    if not VO_TEXT.exists():
        fails.append(f"VO text missing: {VO_TEXT}")
        raw_text = ""
    else:
        raw_text = VO_TEXT.read_text(encoding="utf-8").strip()

    # Clean structural beat tags ([ring], [payoff], etc.)
    text = re.sub(r"\[[a-z0-9_-]+\]", "", raw_text)
    spoken = re.sub(r"\s+", " ", text).strip()
    n = len(spoken)
    words_count = len(spoken.split())
    print(f"  [{'ok' if 0 < n <= MV2_CAP else 'FAIL'}] spoken chars {n:,}, {words_count} words")
    if not (0 < n <= MV2_CAP):
        fails.append(f"character count {n} outside 1..{MV2_CAP}")

    # Check for stray brackets
    stray = set(re.findall(r"\[([a-z][a-z-]*)\]", text))
    print(f"  [{'ok' if not stray else 'FAIL'}] no stray editorial flags {sorted(stray) if stray else ''}")
    if stray:
        fails.append(f"stray flags would be spoken: {sorted(stray)}")

    # 3. directories exist
    for d in (AUDIO_DIR, CACHE_DIR):
        d.mkdir(parents=True, exist_ok=True)
    print(f"  [{'ok' if AUDIO_DIR.is_dir() and CACHE_DIR.is_dir() else 'FAIL'}] output dirs exist")

    # 4. credits
    if key:
        c = credits_remaining(key)
        if c and c[0] is not None and c[1] is not None:
            used, limit = c
            left = limit - used
            enough = left >= n
            print(f"  [{'ok' if enough else 'FAIL'}] credits: {left:,} remaining ({used:,}/{limit:,} used), need {n:,}")
            if not enough:
                fails.append(f"insufficient credits: {left} < {n}")

    print()
    if fails:
        print("PREFLIGHT FAILED — nothing spent:")
        for f in fails:
            print("   -", f)
        return 1

    print("PREFLIGHT CLEAN.")

    if not go:
        print("\nDry run passed. Run with --go to execute the ElevenLabs paid take.")
        return 0

    # ---- THE SINGLE PAID CALL -------------------------------------------
    os.environ["ELEVENLABS_SEED"] = SEED
    os.environ["ELEVENLABS_TIMEOUT_S"] = TIMEOUT_S
    os.environ["ELEVENLABS_MAX_ATTEMPTS"] = MAX_ATTEMPTS
    from content.video_engine.src.services.audio_synth import (
        AudioSynthService,
        ElevenLabsConfig,
    )

    config = ElevenLabsConfig.from_env()
    service = AudioSynthService(config=config)
    print(f"\n=== RECORDING ELEVENLABS MASTER TAKE ===")
    print(f"Model: {config.model_id} | Voice: {config.voice_id} | Chars: {n:,}")

    result = service.synthesize_scene(
        1,
        text,
        voice_id=config.voice_id,
        settings=SETTINGS,
        audio_dir=AUDIO_DIR,
        cache_dir=CACHE_DIR,
        config=config,
    )

    # Rename canonical output
    master_mp3 = OUT / "elevenlabs-master.mp3"
    master_words = OUT / "elevenlabs-master.words.json"
    if result.audio_path.exists():
        if master_mp3.exists():
            master_mp3.unlink()
        result.audio_path.rename(master_mp3)
    if result.words_path.exists():
        if master_words.exists():
            master_words.unlink()
        result.words_path.rename(master_words)

    wpm = (words_count / result.duration_s) * 60
    print(f"  duration     : {result.duration_s:.2f}s ({result.duration_s/60:.2f} min)")
    print(f"  measured WPM : {wpm:.1f} WPM")
    print(f"  characters   : {result.character_count:,}")
    print(f"  request id   : {result.request_id}")
    print(f"  audio        : {master_mp3}")
    print(f"  words timing : {master_words}")

    manifest = OUT / "master-take-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "script": VO_TEXT.name,
                "seed": SEED,
                "model": config.model_id,
                "voice_id": config.voice_id,
                "characters": result.character_count,
                "words_count": words_count,
                "duration_s": result.duration_s,
                "measured_wpm": round(wpm, 1),
                "request_id": result.request_id,
                "audio": str(master_mp3),
                "words": str(master_words),
                "settings": SETTINGS,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  manifest     : {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""A SHORT's master take: one ElevenLabs request, one part, no chain, no splice.

Doc 37 s8 applies unchanged (every precondition before the paid call; one attempt; the
gates report beside the script must be current - a FAIL refuses unless `--force "<reason>"`
records the reason into the take manifest). Built for Tokyo on 2026-09-04 because
`record_chained_take.py` and `record_master_take.py` are hardcoded to episode one and the
short is a single request well under the mv2 cap.

    python record_short_take.py <script.txt> [--out <dir>] [--force "<reason>"] [--go]

Without --go: preflight only, nothing spent. Writes <out>/audio/scene_1.mp3 + .words.json
(the take's word clock) and <out>/short-take.json (the manifest).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ENV_FILE = REPO / "docs" / "local.env"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

SEED = os.environ.get("RECORD_SEED_OVERRIDE", "4242")
TIMEOUT_S = "600"
MAX_ATTEMPTS = "1"
SETTINGS = {"stability": 0.40, "similarity_boost": 0.75, "style": 0.20, "use_speaker_boost": True}
MV2_CAP = 10_000


def load_env(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def spoken(text: str) -> str:
    return re.sub(r"`?\[[a-z-]+\]`?", "", text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path)
    ap.add_argument("--out", type=Path, default=None, help="take dir (default <script dir>/vo-short)")
    ap.add_argument("--force", default=None, help="record despite a failing / stale gates report - the reason lands in the manifest")
    ap.add_argument("--go", action="store_true", help="spend credits; without it, preflight only")
    args = ap.parse_args()

    import beat_tags
    import run_script_gates as RG

    fails: list[str] = []
    print("=== PREFLIGHT (short take, one part) ===")
    if not ENV_FILE.exists():
        fails.append(f"env file missing: {ENV_FILE}")
    else:
        load_env(ENV_FILE)
    os.environ["ELEVENLABS_NO_BREAK_TAGS"] = "1"
    key, voice = os.environ.get("ELEVENLABS_API_KEY", ""), os.environ.get("ELEVENLABS_VOICE_ID", "")
    print(f"  [{'ok' if key else 'FAIL'}] API key present ({len(key)} chars, not shown)")
    print(f"  [{'ok' if voice else 'FAIL'}] voice id present")
    if not key:
        fails.append("ELEVENLABS_API_KEY missing")
    if not voice:
        fails.append("ELEVENLABS_VOICE_ID missing")
    if not args.script.exists():
        fails.append(f"script missing: {args.script}")
        return _report(fails)

    # the same refusal the long-form recorders use: a current, passing gates report, or a reason
    argv = list(sys.argv) if args.force is None else [*sys.argv, "--force", args.force]
    gates_meta = RG.recording_preflight(args.script, argv, fails)
    if gates_meta is None:
        return _report(fails)

    text = beat_tags.strip_beat_tags(args.script.read_text(encoding="utf-8")).strip()
    stray = sorted(set(re.findall(r"\[([a-z][a-z-]*)\]", text)) - {"pre-key", "post-key"})
    print(f"  [{'ok' if not stray else 'FAIL'}] no stray marks would be spoken ({stray or 'none'})")
    if stray:
        fails.append(f"stray marks would be spoken: {stray}")
    n = len(spoken(text))
    print(f"  [{'ok' if 0 < n <= MV2_CAP else 'FAIL'}] {n:,} spoken chars (mv2 cap {MV2_CAP:,}, one part)")
    if not 0 < n <= MV2_CAP:
        fails.append(f"character count {n} outside 1..{MV2_CAP}")
    if fails:
        return _report(fails)
    print("PREFLIGHT CLEAN.")
    if not args.go:
        print("\nDry run. Re-run with --go to record the short take.")
        return 0

    out = args.out or (args.script.parent / "vo-short")
    audio_dir, cache_dir = out / "audio", out / "cache"
    audio_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["ELEVENLABS_SEED"] = SEED
    os.environ["ELEVENLABS_TIMEOUT_S"] = TIMEOUT_S
    os.environ["ELEVENLABS_MAX_ATTEMPTS"] = MAX_ATTEMPTS
    from content.video_engine.src.services.audio_synth import AudioSynthService, ElevenLabsConfig
    config = ElevenLabsConfig.from_env()
    service = AudioSynthService(config=config)
    r = service.synthesize_scene(1, text, voice_id=config.voice_id, settings=SETTINGS,
                                 audio_dir=audio_dir, cache_dir=cache_dir, config=config)
    print(f"\n  duration   : {r.duration_s:.1f}s")
    print(f"  request id : {r.request_id}")
    print(f"  audio      : {r.audio_path}")
    print(f"  words      : {r.words_path}")
    manifest = out / "short-take.json"
    manifest.write_text(json.dumps({
        "script": args.script.name, "parts": 1, "seed": SEED, "model": config.model_id,
        "settings": SETTINGS, "characters": r.character_count, "duration_s": r.duration_s,
        "request_id": r.request_id, "audio": str(r.audio_path), "words": str(r.words_path),
        "cache_hit": r.cache_hit, **(gates_meta or {}),
    }, indent=2), encoding="utf-8")
    print(f"  manifest   : {manifest}")
    print("\n  Next: whisper-gate it (verify_take_whisper.py), LISTEN, then build the timeline.")
    return 0


def _report(fails: list[str]) -> int:
    print("\nPREFLIGHT FAILED - nothing spent:")
    for f in fails:
        print("   -", f)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

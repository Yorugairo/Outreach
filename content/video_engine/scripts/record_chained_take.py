"""Steel and Paper — Script F, two-part CHAINED master take.

Doc 37 §8: one take per part, no splicing. §8.1: a long paid generation gets
a generous timeout and exactly one attempt, because a retry on an 11-minute
request is a cost multiplier and a timeout is not evidence the request was
free (13,746 characters were burned that way for zero audio).

Chaining is not splice-repair. Part two is conditioned on part one's
`previous_request_ids`, which is the provider's supported long-form path and
carries prosody across the join. The ban is on concatenating independently
generated segments.

THE SPLIT MUST LAND ON A SCRIPTED PAUSE. Part one has to end inside a
`[post-key]` settle so the join sits in silence rather than between two
words. Preflight refuses to spend if it does not.

Run without --go for preflight only.
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
VO_TEXT = EP / "SCRIPT-G-VO.txt"
OUT = EP / "vo-f"
AUDIO_DIR = OUT / "audio"
CACHE_DIR = OUT / "cache"

# Part two opens here. Chosen because the sentence before it ends on a
# [post-key] settle AND it opens a new unit with an imperative, so any
# prosody shift across the join reads as a deliberate gear change rather
# than a seam. See the ledger for the alternatives considered.
SPLIT_ANCHOR = "And that's the part everyone repeating this chart missed"

SEED = os.environ.get("RECORD_SEED_OVERRIDE", "4242")
TIMEOUT_S = "900"
MAX_ATTEMPTS = "1"
SETTINGS = {"stability": 0.40, "similarity_boost": 0.75, "style": 0.20,
            "use_speaker_boost": True}
MV2_CAP = 10_000
GEN_CHARS_PER_SEC = 20.0        # conservative generation rate

sys.path.insert(0, str(REPO))


def load_env(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def spoken(text: str) -> str:
    t = re.sub(r"`?\[(?:pre|post)-key\]`?", "", text)
    return re.sub(r"\s+", " ", t).strip()


def credits_remaining(api_key: str) -> tuple[int, int] | None:
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/user/subscription",
        headers={"xi-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read().decode())
        return d.get("character_count"), d.get("character_limit")
    except Exception as e:                                  # noqa: BLE001
        print(f"    (could not read subscription: {type(e).__name__})")
        return None


def main() -> int:
    go = "--go" in sys.argv
    fails: list[str] = []
    print("=== PREFLIGHT (chained take) ===")

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

    if not VO_TEXT.exists():
        fails.append(f"VO text missing: {VO_TEXT}")
        return _report(fails, go)
    text = VO_TEXT.read_text(encoding="utf-8").strip()

    # --- the split ---------------------------------------------------------
    hits = text.count(SPLIT_ANCHOR)
    print(f"  [{'ok' if hits == 1 else 'FAIL'}] split anchor is unique ({hits} hits)")
    if hits != 1:
        fails.append(f"split anchor found {hits} times; must be exactly 1")
        return _report(fails, go)
    i = text.index(SPLIT_ANCHOR)
    part1, part2 = text[:i].rstrip(), text[i:].strip()

    # Part one must END on a settle, or the join lands between two words.
    tail = part1[-24:]
    on_pause = bool(re.search(r"\[post-key\]`?\s*$", tail))
    print(f"  [{'ok' if on_pause else 'FAIL'}] part one ends on a [post-key] settle")
    if not on_pause:
        fails.append(f"split does not land on a scripted pause; part one ends "
                     f"{tail!r} — the join would be audible")

    n1, n2 = len(spoken(part1)), len(spoken(part2))
    for label, n in (("part 1", n1), ("part 2", n2)):
        ok = 0 < n <= MV2_CAP
        print(f"  [{'ok' if ok else 'FAIL'}] {label} {n:,} chars (mv2 cap {MV2_CAP:,})")
        if not ok:
            fails.append(f"{label} character count {n} outside 1..{MV2_CAP}")

    # Paragraphs are pause marks (doc 37): the provider introduces "a clear
    # pause and reset in intonation" at every blank line. A payload that
    # keeps the display script's beat-per-paragraph formatting resets the
    # voice every sentence or two - and a break tag stacked on a paragraph
    # boundary is a double pause. Both block recording.
    paras = len([x for x in text.split("\n\n") if x.strip()])
    dense = paras > max(10, len(text) // 700)
    print(f"  [{'FAIL' if dense else 'ok'}] paragraph density: {paras} paragraphs "
          f"in {len(text)} chars (reset every ~{len(text)//max(1,paras)} chars)")
    if dense:
        fails.append(f"{paras} paragraphs - the payload was not reflowed; "
                     f"paragraph breaks survive only at section seams")
    # Checked PER PART PAYLOAD, not on the joined text: the split-seam
    # [post-key] that X5 requires at part one's end sits against the part
    # boundary's blank line, but that break never renders as silence - the
    # join replaces it. Only stacks INSIDE a part's flow double-pause.
    stacked = []
    for _part in (part1, part2):
        stacked += re.findall(
            r"`?\[(?:pre|post)-key\]`?[ \t]*\n[ \t]*\n"
            r"|\n[ \t]*\n[ \t]*`?\[(?:pre|post)-key\]`?", _part.strip())
    print(f"  [{'FAIL' if stacked else 'ok'}] stacked pauses (tag on a paragraph seam): {len(stacked)}")
    if stacked:
        fails.append(f"{len(stacked)} break tags stacked on paragraph breaks - "
                     f"at a seam the paragraph IS the settle; drop the tag")
    stray = set(re.findall(r"\[([a-z][a-z-]*)\]", text)) - {"pre-key", "post-key"}
    print(f"  [{'ok' if not stray else 'FAIL'}] no stray editorial flags "
          f"{sorted(stray) if stray else ''}")
    if stray:
        fails.append(f"stray flags would be spoken: {sorted(stray)}")

    total = n1 + n2
    marks = len(re.findall(r"\[(?:pre|post)-key\]", text))
    ration = marks / (total / 1000)
    print(f"  [{'ok' if ration <= 3 else 'FAIL'}] break ration {ration:.2f}/1k "
          f"({marks} tags, limit 3.0)")
    if ration > 3:
        fails.append(f"break ration {ration:.2f} exceeds 3.0")

    # Doc 37 §8.3 caps a master at 12 tags REGARDLESS of ration — a long take
    # can sit well inside 3/1k and still overload the provider. §1's "≈3 per
    # generated segment" was written when a segment was a scene; §8 governs
    # master takes and supersedes it here. Each chained part is its own
    # generation, so each carries its own cap.
    for label, part in (("part 1", part1), ("part 2", part2)):
        k = len(re.findall(r"\[(?:pre|post)-key\]", part))
        ok = k <= 12
        print(f"  [{'ok' if ok else 'FAIL'}] {label} {k} break tags "
              f"(doc 37 §8.3 cap: 12 per master)")
        if not ok:
            fails.append(
                f"{label} carries {k} break tags against a cap of 12; move "
                f"section-boundary savors to editor-placed timeline gaps — "
                f"any silence over 1.2s belongs there anyway")

    # the settles cut from TTS must be RECORDED for the timeline edit -
    # a payload at ~3 tags/generation without an edit-pause plan has lost
    # its savor beats, not rationed them
    plan = EP / "SCRIPT-G-EDIT-PAUSES.json"
    print(f"  [{'ok' if plan.exists() else 'FAIL'}] edit-pause plan present ({plan.name})")
    if not plan.exists():
        fails.append("edit-pause plan missing - the dropped settles are owed "
                     "to the timeline and must be recorded before the take")

    for d in (AUDIO_DIR, CACHE_DIR):
        d.mkdir(parents=True, exist_ok=True)
    print(f"  [ok] output dirs exist")

    try:
        from content.video_engine.src.services.audio_synth import compile_pause_marks
        compiled = compile_pause_marks(text)
        ok_c = "[pre-key]" not in compiled and "[post-key]" not in compiled
        print(f"  [{'ok' if ok_c else 'FAIL'}] pause marks compile to break tags")
        if not ok_c:
            fails.append("pause marks did not compile")
    except Exception as e:                                  # noqa: BLE001
        print(f"  [FAIL] compile_pause_marks: {type(e).__name__}: {e}")
        fails.append("compile_pause_marks raised")

    # Credits must cover BOTH parts. Charging part one and failing part two
    # leaves a half-episode and a spent balance.
    if key:
        c = credits_remaining(key)
        if c and c[0] is not None and c[1] is not None:
            left = c[1] - c[0]
            enough = left >= total
            print(f"  [{'ok' if enough else 'FAIL'}] credits: {left:,} remaining, "
                  f"need {total:,} for BOTH parts")
            if not enough:
                fails.append(f"insufficient credits for the whole take: "
                             f"{left} < {total}")

    need = max(n1, n2) / GEN_CHARS_PER_SEC
    t = float(TIMEOUT_S)
    print(f"  [{'ok' if t >= need else 'FAIL'}] timeout {t:.0f}s vs ~{need:.0f}s "
          f"for the longer part ({max(n1, n2):,} chars); attempts={MAX_ATTEMPTS}")
    if t < need:
        fails.append(f"timeout {t}s too short — retries would be charged")

    print(f"\n  split at {n1 / total:.1%} of the script")
    print(f"  part 1 ends : ...{spoken(part1)[-58:]}")
    print(f"  part 2 opens: {spoken(part2)[:58]}...")

    return _report(fails, go, text, part1, part2, n1, n2)




PROBE_SPEECH_S = 120.0    # doc 37 s13: 90s macro section + 30s of the next
CHARS_PER_S = 16.05


def run_probe(go: bool) -> int:
    """Record the 2:00 probe at IDENTICAL settings/seed, so provider
    behavior on the probe predicts the master. ~2k credits."""
    import re as _re
    load_env(ENV_FILE)
    text = VO_TEXT.read_text(encoding="utf-8")
    est = int(PROBE_SPEECH_S * CHARS_PER_S)
    cut = len(text)
    for m in _re.finditer(r"[.!?][\"”]?(?=\s)", text):
        if m.end() >= est:
            cut = m.end(); break
    body = text[:cut].rstrip()
    n = len(body)
    print(f"PROBE: {n:,} chars (~{n / CHARS_PER_S:.0f}s speech) - the full "
          f"first macro section + the shift into the next")
    if not go:
        print("dry run - re-run with --probe --go (~{:,} credits)".format(n))
        return 0
    os.environ["ELEVENLABS_SEED"] = SEED
    os.environ["ELEVENLABS_TIMEOUT_S"] = TIMEOUT_S
    os.environ["ELEVENLABS_MAX_ATTEMPTS"] = MAX_ATTEMPTS
    from content.video_engine.src.services.audio_synth import (
        AudioSynthService, ElevenLabsConfig)
    config = ElevenLabsConfig.from_env()
    service = AudioSynthService(config=config)
    # scene_id is numeric in the synth service; 99 = the probe slot
    r = service.synthesize_scene(
        99, body, voice_id=config.voice_id, settings=SETTINGS,
        audio_dir=AUDIO_DIR, cache_dir=CACHE_DIR, config=config)
    print(f"  duration : {r.duration_s:.1f}s")
    print(f"  audio    : {r.audio_path}")
    print("Now: whisper-gate it (verify_take_whisper.py --probe), LISTEN "
          "to it, and only then record the master.")
    return 0


def _report(fails, go, text=None, part1=None, part2=None, n1=0, n2=0) -> int:
    print()
    if fails:
        print("PREFLIGHT FAILED — nothing spent:")
        for f in fails:
            print("   -", f)
        return 1
    print("PREFLIGHT CLEAN.")
    if not go:
        print("\nDry run. Re-run with --go to record the chained take.")
        return 0

    os.environ["ELEVENLABS_SEED"] = SEED
    os.environ["ELEVENLABS_TIMEOUT_S"] = TIMEOUT_S
    os.environ["ELEVENLABS_MAX_ATTEMPTS"] = MAX_ATTEMPTS
    from content.video_engine.src.services.audio_synth import (
        AudioSynthService, ElevenLabsConfig)
    config = ElevenLabsConfig.from_env()
    service = AudioSynthService(config=config)

    results = []
    chain: tuple[str, ...] = ()
    for idx, (label, body, n) in enumerate(
            ((1, part1, n1), (2, part2, n2)), start=0):
        print(f"\n=== PART {label} === chars={n:,} "
              f"previous_request_ids={list(chain) or 'none'}")
        r = service.synthesize_scene(
            label, body, voice_id=config.voice_id, settings=SETTINGS,
            audio_dir=AUDIO_DIR, cache_dir=CACHE_DIR, config=config,
            previous_request_ids=chain)
        print(f"  duration   : {r.duration_s:.1f}s ({r.duration_s / 60:.1f} min)")
        print(f"  request id : {r.request_id}")
        print(f"  audio      : {r.audio_path}")
        results.append(r)
        if not r.request_id:
            print("  WARNING: no request id returned — part two cannot chain, "
                  "and an unchained part two will drift in prosody. Stopping.")
            break
        chain = (r.request_id,)

    manifest = OUT / "chained-take.json"
    manifest.write_text(json.dumps({
        "script": VO_TEXT.name,
        "split_anchor": SPLIT_ANCHOR,
        "split_lands_on_pause": True,
        "seed": SEED, "model": config.model_id, "settings": SETTINGS,
        "parts": [{
            "part": i + 1, "characters": r.character_count,
            "duration_s": r.duration_s, "request_id": r.request_id,
            "audio": str(r.audio_path),
            "chained_from": None if i == 0 else results[0].request_id,
        } for i, r in enumerate(results)],
        "total_duration_s": sum(r.duration_s for r in results),
    }, indent=2), encoding="utf-8")
    print(f"\n  manifest   : {manifest}")
    print(f"  TOTAL      : {sum(r.duration_s for r in results) / 60:.2f} min")
    print("\n  LISTEN TO THE JOIN FIRST — doc 37 §8.")
    return 0


if __name__ == "__main__":
    if "--probe" in sys.argv:
        raise SystemExit(run_probe("--go" in sys.argv))
    raise SystemExit(main())

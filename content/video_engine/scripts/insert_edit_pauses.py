"""Insert the OWED silences (edit_pauses.v1) into the joined take.

The ~3-tags-per-generation practice moved settles out of TTS and into the
editor's timeline; this is the editor. Reads the episode's edit-pause plan
and the merged word timeline, resolves each verbatim anchor to a word
boundary, then rebuilds the audio with ffmpeg silence insertions and
emits a SHIFTED timeline.json so every downstream consumer (captions,
docks, choreography) sees the final clock.

Run AFTER build_timeline_f.py, BEFORE the dock retime:

    python insert_edit_pauses.py

Idempotence: writes episode-paused.mp3 + timeline.json with
`edit_pauses_applied: true`; refuses to run twice on a shifted timeline.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
BUILD = EP / "build-f"


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def main() -> int:
    tl_path = BUILD / "timeline.json"
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    if tl.get("edit_pauses_applied"):
        print("timeline already carries the edit pauses - refusing to double-insert")
        return 1
    if not tl.get("dead_space_compressed") and "--skip-tighten-check" not in sys.argv:
        print("ORDER: kill the dead space FIRST (compress_dead_space.py), "
              "THEN add our breaks (operator, 2026-08-30). "
              "--skip-tighten-check to override.")
        return 1
    plan = json.loads((EP / "SCRIPT-G-EDIT-PAUSES.json")
                      .read_text(encoding="utf-8"))["pauses"]
    words = tl["words"]
    joined = " ".join(w["w"] for w in words)
    njoined = norm(joined)

    # resolve each anchor to the word index its pause follows (or precedes)
    def find_boundary(p) -> float | None:
        anc = norm(p.get("after") or p.get("before"))
        toks = anc.split()
        # a lone em-dash word normalizes to "" and would sever the
        # consecutive match - index only the words that survive norm
        wt = [(norm(w["w"]), w) for w in words]
        wt = [(t, w) for t, w in wt if t]
        wtoks = [t for t, _ in wt]
        for i in range(len(wtoks) - len(toks) + 1):
            if wtoks[i:i + len(toks)] == toks:
                if "after" in p:
                    return wt[i + len(toks) - 1][1]["end"]
                return wt[i][1]["start"]
        return None

    inserts = []
    for p in plan:
        at = find_boundary(p)
        if at is None:
            print(f"  [FAIL] anchor not found in take: "
                  f"{(p.get('after') or p.get('before'))[:60]!r}")
            return 1
        inserts.append((at, p["s"], p["kind"]))
    inserts.sort()
    print(f"{len(inserts)} pauses resolved to word boundaries "
          f"({sum(s for _, s, _ in inserts):.1f}s total)")

    # rebuild audio: split at boundaries, concat with silences (one re-encode)
    audio = BUILD / "audio/episode.mp3"
    seg_dir = BUILD / "audio/_pauses"
    seg_dir.mkdir(parents=True, exist_ok=True)
    points = [0.0] + [t for t, _, _ in inserts]
    parts = []
    for i, (t, dur, _) in enumerate(inserts + [(None, None, None)]):
        a = points[i]
        b = t if t is not None else None
        seg = seg_dir / f"seg{i:02d}.mp3"
        cmd = ["ffmpeg", "-y", "-v", "quiet", "-i", str(audio), "-ss", f"{a}"]
        if b is not None:
            cmd += ["-to", f"{b}"]
        cmd += ["-c:a", "libmp3lame", "-b:a", "192k", str(seg)]
        subprocess.run(cmd, check=True)
        parts.append(seg)
        if b is not None:
            sil = seg_dir / f"sil{i:02d}.mp3"
            subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-f", "lavfi",
                            "-i", "anullsrc=r=44100:cl=mono", "-t", f"{dur}",
                            "-c:a", "libmp3lame", "-b:a", "192k", str(sil)],
                           check=True)
            parts.append(sil)
    lst = seg_dir / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts),
                   encoding="utf-8")
    out_audio = BUILD / "audio/episode-paused.mp3"
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-f", "concat",
                    "-safe", "0", "-i", str(lst), "-c:a", "libmp3lame",
                    "-b:a", "192k", str(out_audio)], check=True, cwd=seg_dir)

    # shift the word timeline past each insertion
    for w in words:
        shift = sum(s for t, s, _ in inserts if t <= w["start"] + 1e-6)
        w["start"] = round(w["start"] + shift, 3)
        w["end"] = round(w["end"] + shift, 3)
    for sen in tl.get("sentences", []):
        shift_s = sum(s for t, s, _ in inserts if t <= sen["start"] + 1e-6)
        shift_e = sum(s for t, s, _ in inserts if t <= sen["end"] + 1e-6)
        sen["start"] = round(sen["start"] + shift_s, 3)
        sen["end"] = round(sen["end"] + shift_e, 3)
    tl["runtime_s"] = round(tl["runtime_s"] + sum(s for _, s, _ in inserts), 3)
    tl["edit_pauses_applied"] = True
    tl["paused_audio"] = "audio/episode-paused.mp3"
    tl_path.write_text(json.dumps(tl, indent=1), encoding="utf-8")
    print(f"audio -> {out_audio.name}; timeline shifted; "
          f"runtime {tl['runtime_s']:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

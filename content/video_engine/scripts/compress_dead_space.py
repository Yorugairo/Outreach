"""KILL THE DEAD SPACE - then add our breaks (operator, 2026-08-30).

YouTube pacing: the raw take carries dead air the model produced, and
stacking our deliberate pauses ON TOP of it made delivery drag. So the
chain now runs this pass on the JOINED take, before insert_edit_pauses:

  intra-sentence gaps  > 0.40s  ->  0.30s   (mid-sentence holes)
  inter-sentence gaps  > 0.65s  ->  0.50s   (slow settles)

PRESERVED, never compressed: the six break-tag sites (authored pauses
rendered by the provider - located via the pause marks in the VO text)
and the part-1/part-2 join settle. Deliberate silence is authored;
everything else above the caps is dead air.

Run order: join_chained_take -> build_timeline_f -> THIS ->
insert_edit_pauses. Refuses to run after edit pauses (order violation)
or twice (flag: dead_space_compressed).

    python compress_dead_space.py            # report only
    python compress_dead_space.py --write
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

INTRA_CAP, INTRA_TGT = 0.40, 0.30
INTER_CAP, INTER_TGT = 0.65, 0.50
# an authored break tag renders as tag + provider settle (~1.5s measured on
# the probe's [post-key] after "touched it") - the authored INTENT is one
# full beat, so tag sites are capped, not preserved untouched
TAG_CAP = 1.00


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", s.lower())


def preserved_boundaries(words) -> set[float]:
    """Word-end times whose following gap is AUTHORED (break-tag sites +
    the join seam)."""
    keep: set[float] = set()
    vo = (EP / "SCRIPT-G-VO.txt").read_text(encoding="utf-8")
    wt = [(t, w) for w in words for t in norm(w["w"]).split()]
    wtoks = [t for t, _ in wt]
    for m in re.finditer(r"`\[[a-z-]+\]`", vo):
        pre = norm(vo[:m.start()]).split()[-4:]
        n = len(pre)
        for i in range(len(wtoks) - n + 1):
            if wtoks[i:i + n] == pre:
                keep.add(round(wt[i + n - 1][1]["end"], 3))
    # join seam: last part-1 word
    parts = [w.get("part") for w in words]
    for a, b in zip(words, words[1:]):
        if a.get("part") == 1 and b.get("part") == 2:
            keep.add(round(a["end"], 3))
    return keep


def main() -> int:
    write = "--write" in sys.argv
    tl_path = BUILD / "timeline.json"
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    if tl.get("edit_pauses_applied"):
        print("REFUSED: edit pauses already applied - dead-space kill runs "
              "BEFORE insert_edit_pauses (rebuild the timeline first)")
        return 1
    if tl.get("dead_space_compressed"):
        print("REFUSED: already compressed")
        return 1
    words = tl["words"]
    sent_ends = {round(s["end"], 3) for s in tl.get("sentences", [])}
    keep = preserved_boundaries(words)
    print(f"{len(keep)} authored tag/seam boundaries (capped at {TAG_CAP}s, "
          f"not preserved raw)")
    # resolve the plan's tighten runs to time spans
    runs = []
    try:
        plan = json.loads((EP / "SCRIPT-G-EDIT-PAUSES.json")
                          .read_text(encoding="utf-8"))
        wt = [(t, w) for w in words for t in norm(w["w"]).split()]
        wtoks = [t for t, _ in wt]
        def anchor_end(txt):
            toks = norm(txt).split(); n = len(toks)
            for i in range(len(wtoks) - n + 1):
                if wtoks[i:i + n] == toks:
                    return wt[i + n - 1][1]["end"]
        def anchor_start(txt):
            toks = norm(txt).split(); n = len(toks)
            for i in range(len(wtoks) - n + 1):
                if wtoks[i:i + n] == toks:
                    return wt[i][1]["start"]
        for r in plan.get("tighten_runs", []):
            a2, b2 = anchor_end(r["start_after"]), anchor_start(r["end_before"])
            if a2 and b2:
                runs.append({"a": a2, "b": b2, **{k: r[k] for k in
                    ("inter_cap", "inter_tgt", "intra_cap", "intra_tgt")}})
                print(f"  fluid run {a2:.1f}-{b2:.1f}s")
    except FileNotFoundError:
        pass

    cuts = []   # (gap_start, gap_end, new_len)
    for a, b in zip(words, words[1:]):
        g = b["start"] - a["end"]
        at = round(a["end"], 3)
        if g <= 0:
            continue
        if at in keep:
            if g > TAG_CAP:
                cuts.append((a["end"], b["start"], TAG_CAP))
            continue
        cap, tgt = ((INTER_CAP, INTER_TGT) if at in sent_ends
                    else (INTRA_CAP, INTRA_TGT))
        # fluid runs (declared in the edit-pause plan): descriptions flow,
        # so caps drop; the deliberate beats get re-inserted afterwards
        for run in runs:
            if run["a"] <= at <= run["b"]:
                cap, tgt = ((run["inter_cap"], run["inter_tgt"])
                            if at in sent_ends
                            else (run["intra_cap"], run["intra_tgt"]))
        if g > cap:
            cuts.append((a["end"], b["start"], tgt))
    saved = sum((b - a) - t for a, b, t in cuts)
    print(f"{len(cuts)} gaps compressed, {saved:.1f}s of dead air removed")
    for a, b, t in cuts[:12]:
        print(f"   {a:7.2f}  {b - a:.2f}s -> {t:.2f}s")
    if not write:
        print("report only - re-run with --write")
        return 0

    audio = BUILD / "audio/episode.mp3"
    raw = BUILD / "audio/episode-raw.mp3"
    if not raw.exists():
        audio.replace(raw)
    seg_dir = BUILD / "audio/_tight"
    seg_dir.mkdir(parents=True, exist_ok=True)
    parts, prev = [], 0.0
    for i, (a, b, t) in enumerate(cuts):
        seg = seg_dir / f"s{i:03d}.mp3"
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(raw),
                        "-ss", f"{prev}", "-to", f"{a + t}",
                        "-c:a", "libmp3lame", "-b:a", "192k", str(seg)],
                       check=True)
        parts.append(seg); prev = b
    tail = seg_dir / "tail.mp3"
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(raw),
                    "-ss", f"{prev}", "-c:a", "libmp3lame", "-b:a", "192k",
                    str(tail)], check=True)
    parts.append(tail)
    lst = seg_dir / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts),
                   encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-f", "concat", "-safe",
                    "0", "-i", str(lst), "-c:a", "libmp3lame", "-b:a",
                    "192k", str(audio)], check=True, cwd=seg_dir)

    # shift the timeline back by the removed time before each word
    def shift_at(t0: float) -> float:
        return sum((b - a) - t for a, b, t in cuts if b <= t0 + 1e-6)
    for w in words:
        d = shift_at(w["start"])
        w["start"] = round(w["start"] - d, 3)
        w["end"] = round(w["end"] - shift_at(w["end"] - 0.001), 3)
    for s2 in tl.get("sentences", []):
        s2["start"] = round(s2["start"] - shift_at(s2["start"]), 3)
        s2["end"] = round(s2["end"] - shift_at(s2["end"] - 0.001), 3)
    tl["runtime_s"] = round(tl["runtime_s"] - saved, 3)
    tl["dead_space_compressed"] = True
    tl_path.write_text(json.dumps(tl, indent=1), encoding="utf-8")
    print(f"episode.mp3 tightened ({saved:.1f}s removed); raw kept as "
          f"episode-raw.mp3; runtime {tl['runtime_s']:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

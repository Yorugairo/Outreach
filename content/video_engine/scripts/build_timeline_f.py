"""Steel and Paper — Script F timeline, built from the recorded take.

Merges the two chained parts into one continuous word timeline, then binds
plates and evidence to real seconds.

The join: part one's audio carries 5.18s of trailing silence after its last
word. Doc 37 caps a scripted settle at 1.2s and puts anything longer in the
editor's timeline, so the tail is TRIMMED to 1.2s and part two is offset by
that. The join therefore lands inside a designed settle, not an inherited
one.

Plate density is the operator's rule, not doctrine's: one plate per 12s of
runtime, 20s absolute maximum, and a 20s hold requires two strong evidence
pieces of DIFFERENT species covering it (ruling B6).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
TAKE = EP / "vo-f/audio"
CLAIMS = REPO / "content/video_engine/projects/systems-and-blowups/review/claims"
OUT = EP / "build-f"

SETTLE_S = 1.20          # doc 37: break tags cap at 1.2s
PLATE_TARGET_S = 12.0    # operator: one plate per 12s at least
PLATE_MAX_S = 20.0       # operator: 20s absolute max, needs 2 evidence pieces


@dataclass
class Word:
    w: str
    start: float
    end: float
    part: int


def load_take() -> tuple[list[Word], float, float]:
    a = json.loads((TAKE / "scene_1.words.json").read_text(encoding="utf-8"))
    b = json.loads((TAKE / "scene_2.words.json").read_text(encoding="utf-8"))
    offset = a["words"][-1]["end_s"] + SETTLE_S
    words = [Word(w["w"], w["start_s"], w["end_s"], 1) for w in a["words"]]
    words += [Word(w["w"], w["start_s"] + offset, w["end_s"] + offset, 2)
              for w in b["words"]]
    return words, offset, words[-1].end


def plate_inventory() -> list[str]:
    """Every operator-approved plate, newest wave first so v2s win."""
    waves = ["steel-and-paper-plates-wave-7b", "steel-and-paper-plates-wave-7",
             "steel-and-paper-plates-wave-6", "steel-and-paper-plates-wave-5",
             "steel-and-paper-plates-wave-4", "steel-and-paper-plates-wave-3",
             "steel-and-paper-plates-wave-1b", "steel-and-paper-plates-wave-1",
             "finance-episodes-plates-wave-1"]
    # Superseded or operator-rejected — recorded here so the reason survives.
    RETIRED = {
        "world-spike-certificate-ring-v1": "superseded by wave-1b v2",
        "world-spike-rest-v1": "superseded by wave-1b v2",
        "world-broadcast-set-v1": "ghost bleed; superseded by wave-4 v2",
        "world-index-weights-v1": "operator rejected",
        "world-price-board-wiped-v1": "operator rejected",
        "world-molten-pour-v1": "superseded by wave-5 v2",
        "world-hype-machine-v1": "output was paper; superseded by 7b v2",
        "world-unwind-desk-v1": "reduction illegible, cards read as playing cards; superseded by 7b v2",
    }
    # finance-episodes-wave-1 holds plates for other episodes too.
    REUSABLE = {"world-dram-terrain-v1", "world-korea-port-v1",
                "world-memory-fab-floor-v1", "world-seoul-fab-skyline-v1"}
    seen, plates = set(), []
    for wave in waves:
        d = CLAIMS / wave / "objects"
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.png")):
            name = p.stem
            if name in RETIRED or name in seen:
                continue
            if wave.startswith("finance-") and name not in REUSABLE:
                continue
            seen.add(name)
            plates.append(name)
    return plates


def sentences(words: list[Word]) -> list[dict]:
    """Sentence spans with real start/end seconds."""
    out, cur = [], []
    for w in words:
        cur.append(w)
        if w.w.endswith((".", "!", "?")):
            out.append({"text": " ".join(x.w for x in cur),
                        "start": cur[0].start, "end": cur[-1].end,
                        "part": cur[0].part})
            cur = []
    if cur:
        out.append({"text": " ".join(x.w for x in cur),
                    "start": cur[0].start, "end": cur[-1].end,
                    "part": cur[0].part})
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    words, offset, total = load_take()
    sents = sentences(words)
    plates = plate_inventory()

    need_target = int(total / PLATE_TARGET_S) + 1
    need_max = int(total / PLATE_MAX_S) + 1

    print(f"TIMELINE — Script G")
    print(f"  runtime      : {total:.2f}s ({total/60:.2f} min)")
    print(f"  join offset  : {offset:.2f}s (part 1 tail trimmed to {SETTLE_S}s)")
    print(f"  words        : {len(words):,}   sentences: {len(sents)}")
    print(f"\nPLATES")
    print(f"  available    : {len(plates)}")
    print(f"  need @{PLATE_TARGET_S:.0f}s target : {need_target}")
    print(f"  need @{PLATE_MAX_S:.0f}s ceiling: {need_max}")
    print(f"  -> {total/len(plates):.1f}s per plate if evenly spread "
          f"({'INSIDE' if total/len(plates) <= PLATE_MAX_S else 'OVER'} the ceiling, "
          f"{'at' if total/len(plates) <= PLATE_TARGET_S else 'over'} target)")

    (OUT / "timeline.json").write_text(json.dumps({
        "episode": "steel-and-paper", "script": "SCRIPT-G-VO.txt",
        "take": "vo-f", "runtime_s": round(total, 3),
        "join": {"offset_s": round(offset, 3), "settle_s": SETTLE_S,
                 "part1_speech_end_s": round(offset - SETTLE_S, 3)},
        "words": [asdict(w) for w in words],
        "sentences": sents,
        "plates_available": plates,
    }, indent=1), encoding="utf-8")
    print(f"\n  wrote {OUT / 'timeline.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

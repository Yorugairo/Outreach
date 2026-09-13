"""NARRATION THAT POINTS AT A VISUAL NOT ON SCREEN, measured (P54 follow-up, operator 2026-09-13).

The operator: "gating for narration without the chart on screen is probably valid." A sentence that says "look at
this chart" over a plate points the viewer's eye at nothing. From the build's timeline alone (no browser): every
word run that POINTS at a visual must have something to point at on stage at that word's time.

POINTING PHRASES (closed, small on purpose). Each one either NAMES a chart element ("the chart", "this line", "the
spike", "the bar") or DIRECTS the eye ("look at", "see the", "watch the", "on screen", "here's the"). A longer list
drifts into ordinary speech ("the rate", "that number") and would fault every sentence; widening it is a ruling,
not a tuning.

WHAT COUNTS AS ON STAGE at t (the fields gate_motion_density reads):
  page   the scene holding t has a ledger page world (`world.kind == "ledger"`) - the chart
  dock   a paper dock whose [enter, exit) holds t (a scene's `docks`, gate_motion_density._dock_span)
  card   a species that paints its own card/diagram (CARD_SPECIES) whose [at, at + dur) holds t, inside its scene
A plate or a clip is a picture, not a chart: a pointing phrase over one alone is UNCOVERED.

    python measure_spoken_visuals.py <build> [--json] [--out <path>]

Writes `<build>/spoken-visuals.json` (or --out) and prints one line per pointing phrase.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = Path(os.environ.get("VIDEO_ENGINE_SCRIPTS") or HERE)
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

POINTING_PHRASES = ("this chart", "the chart", "this line", "the line", "look at", "see the", "watch the",
                    "the spike", "the bar", "on screen", "here's the")
CARD_SPECIES = ("flow", "count_array", "agenda", "newsreel", "chip")   # species that ARE a visual, not a mark on one
PAGE_KIND = "ledger"
_PUNCT = re.compile(r"[^a-z0-9']+")


def norm(word: str) -> str:
    """`Chart,` -> chart; `Here’s` -> here's."""
    return _PUNCT.sub("", str(word).lower().replace("’", "'"))


def words_of(tl: dict) -> list[dict]:
    """The spoken words in time order, from the timeline's caption pages ({w, s})."""
    seen, out = set(), []
    for pg in tl.get("caption_pages") or []:
        for tok in pg.get("t") or []:
            s = tok.get("s")
            if s is None:
                continue
            key = (round(float(s), 3), str(tok.get("w", "")))
            if key not in seen:
                seen.add(key)
                out.append({"w": key[1], "s": key[0]})
    return sorted(out, key=lambda x: x["s"])


def find_pointers(words: list[dict], phrases: tuple[str, ...] = POINTING_PHRASES) -> list[dict]:
    """Every pointing phrase in the word stream, timed at its first word."""
    toks = [norm(w["w"]) for w in words]
    hits = []
    for phrase in phrases:
        parts = phrase.split()
        for i in range(len(toks) - len(parts) + 1):
            if toks[i:i + len(parts)] == parts:
                said = " ".join(w["w"] for w in words[max(0, i - 3):i + len(parts) + 3])
                hits.append({"phrase": phrase, "t": words[i]["s"], "context": said})
    return sorted(hits, key=lambda h: h["t"])


def _dock_span(d: dict) -> tuple[float, float] | None:
    a = d.get("at", d.get("start", d.get("enter")))
    z = d.get("end", d.get("exit", d.get("until")))
    return (float(a), float(z)) if isinstance(a, (int, float)) and isinstance(z, (int, float)) else None


def on_stage_at(tl: dict, t: float) -> dict:
    """What the timeline puts on stage at t: the world kind, and the page / docks / cards that can be pointed at."""
    for s in tl.get("scenes") or []:
        a, z = float(s["span"][0]), float(s["span"][1])
        if not a <= t < z:
            continue
        world = s.get("world") or {}
        kind = world.get("kind") or ("plate" if world.get("asset_id") else "none")
        docks = [str(d.get("slide") or d.get("asset") or "?") for d in s.get("docks") or []
                 if (sp := _dock_span(d)) and sp[0] <= t < sp[1]]
        cards = [str(sp.get("kind")) for sp in s.get("species") or [] if sp.get("kind") in CARD_SPECIES
                 and float(sp.get("at", -1)) <= t < min(z, float(sp.get("at", -1)) + float(sp.get("dur", 0)))]
        return {"scene": str(s.get("scene_id", "?")), "world": kind, "page": kind == PAGE_KIND,
                "docks": docks, "cards": cards}
    return {"scene": None, "world": "none", "page": False, "docks": [], "cards": []}


def analyse(tl: dict) -> dict:
    rows = []
    for hit in find_pointers(words_of(tl)):
        stage = on_stage_at(tl, hit["t"])
        rows.append({**hit, "on_stage": stage,
                     "uncovered": not (stage["page"] or stage["docks"] or stage["cards"])})
    return {"phrases": list(POINTING_PHRASES), "pointers": rows,
            "n_pointers": len(rows), "n_uncovered": sum(r["uncovered"] for r in rows)}


def measure(build: Path) -> dict:
    tl_path = next(iter(sorted(Path(build).glob("*.timeline.json"))), None)
    if not tl_path:
        raise SystemExit(f"no *.timeline.json in {build}")
    doc = analyse(json.loads(tl_path.read_text(encoding="utf-8")))
    return {"build": Path(build).name, "timeline": tl_path.name, **doc}


def summary_lines(doc: dict) -> list[str]:
    out = [f"spoken visuals: {doc['n_pointers']} pointing phrases, {doc['n_uncovered']} uncovered ({doc['timeline']})"]
    for r in doc["pointers"]:
        st = r["on_stage"]
        what = "page" if st["page"] else ", ".join(st["docks"] + st["cards"]) or f"only a {st['world']}"
        out.append(f"  {r['t']:7.2f}  \"{r['phrase']}\"  {st['scene']}: {what}  "
                   f"{'UNCOVERED' if r['uncovered'] else 'covered'}  ...{r['context']}...")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="narration that points at a visual not on screen")
    ap.add_argument("build", type=Path)
    ap.add_argument("--json", action="store_true", help="print the document instead of the summary")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    doc = measure(a.build)
    out = a.out or (a.build / "spoken-visuals.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(doc, indent=1) if a.json else "\n".join(summary_lines(doc) + [f"-> {out}"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

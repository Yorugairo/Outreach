"""Compile the Fed episode's small, evidence-only visual diagnostic.

This is a visual proof of the two source-bound ledger objects, not a bed,
pilot, or release cut.  The compiler still needs a real take, so the first
18 seconds of the measured r1337 take provide the unchanged word clock and
audio stream; no narration timings are authored or re-timed here.

    python build_evidence_proof.py

The proof gets its own episode directory under ``build-evidence-proof``.
Its local object copies add only the two authored visual build clocks (four
seconds for the signed bars and six seconds for the retained line), leaving
the source-bound objects beside the episode untouched.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

from authoring import Project  # noqa: E402
from authoring import table as T, words as W  # noqa: E402


BUILD = HERE / "build-evidence-proof"
TAKE = HERE / "vo-scratch-r1337"
TAKE_STEM = "scratch-kokoro"
RUNTIME_S = 18.0
TIMELINE_NAME = "fed-evidence-proof.timeline.json"
SHOT_TABLE_FILE = "SHOT-TABLE-EVIDENCE.py"
ASSETS = HERE / "evidence/objects"
PROOF_OBJECTS = BUILD / "evidence/objects"

BAR_SOURCE = ASSETS / "fed-assets-reserves-change.series.json"
RRP_SOURCE = ASSETS / "fed-on-rrp-history.series.json"
BAR_OBJECT = PROOF_OBJECTS / BAR_SOURCE.name
RRP_OBJECT = PROOF_OBJECTS / RRP_SOURCE.name
BAR_DOMAIN = (-2238, 2238)

DIAGNOSTIC_TITLE = "FED LIQUIDITY PRESSURE — VISUAL EVIDENCE DIAGNOSTIC"
DIAGNOSTIC_SUBTITLE = "TIMING EXCERPT · NOT FINAL NARRATION CHOREOGRAPHY / PILOT"


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: source object must be a JSON object")
    return value


def prepare_proof_objects() -> dict[str, dict[str, Any]]:
    """Copy source-bound objects into the proof and add only proof clocks."""
    if not BAR_SOURCE.is_file() or not RRP_SOURCE.is_file():
        raise SystemExit("evidence proof: source objects are missing; run the source-bound object builder first")
    PROOF_OBJECTS.mkdir(parents=True, exist_ok=True)
    bars = _load_object(BAR_SOURCE)
    rrp = _load_object(RRP_SOURCE)
    # The bars player's ordinary envelope is four seconds in this diagnostic;
    # the line's retained history draws over the authored six-second envelope.
    bars["build_s"] = 4.0
    rrp["build_s"] = 6.0
    # Units remain explicit in ylabel/sub/source. Repeating the long unit
    # after every tick pushes negative tick numerals outside the frame.
    bars["unit"] = ""
    for line in rrp.get("series", []):
        line.pop("name", None)  # label already identifies ON RRP once.
    BAR_OBJECT.write_text(json.dumps(bars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    RRP_OBJECT.write_text(json.dumps(rrp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"bars": bars, "rrp": rrp}


def _reserve_callout(bars: dict[str, Any]) -> dict[str, Any]:
    values = bars.get("bars")
    if not isinstance(values, list):
        raise ValueError("evidence proof: bars object has no bars list")
    reserve = next((row for row in values if isinstance(row, dict) and row.get("label") == "Reserve balances"), None)
    if reserve is None or not isinstance(reserve.get("value"), (int, float)) or isinstance(reserve["value"], bool):
        raise ValueError("evidence proof: reserve datum is missing or non-numeric")
    value = float(reserve["value"])
    label = f"{value:+g} USD billions"
    return {
        "kind": "callout",
        "at": 4.5,
        "dur": 2.0,
        "target": {"kind": "datum", "index": 1},
        "label": label,
        "pad": 24,
    }


def build_rows(objects: dict[str, dict[str, Any]] | None = None) -> list[tuple]:
    """Return the two authored diagnostic windows.

    ``slide:right`` is on the arriving row because the compiler's contract
    names the boundary transition on the incoming scene.  With no docks and
    no camera keys, the proof has no authored camera motion or card layer.
    """
    objects = objects or {"bars": _load_object(BAR_SOURCE), "rrp": _load_object(RRP_SOURCE)}
    bars_plate = "ledger:fed-assets-reserves-change:bars:0:right:axes:cut;idle=none;domain=-2238,2238"
    rrp_plate = "ledger:fed-on-rrp-history:line:0:right:axes:cut;idle=live"
    return [
        (0.0, 8.0, bars_plate, (0, 0, 0), [], None, [_reserve_callout(objects["bars"])]),
        (8.0, RUNTIME_S, rrp_plate, (0, 0, 0), [], "slide:right", []),
    ]


def _real_words(project: Project) -> list[dict[str, Any]]:
    """Keep only real r1337 words fully inside this diagnostic's clock."""
    words = W.take_words(project)
    selected = [
        dict(word)
        for word in words
        if isinstance(word, dict)
        and isinstance(word.get("start_s"), (int, float))
        and isinstance(word.get("end_s"), (int, float))
        and 0 <= float(word["start_s"]) <= float(word["end_s"]) <= RUNTIME_S
    ]
    if not selected:
        raise SystemExit("evidence proof: r1337 take has no measured words in the 0-18s proof window")
    return selected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="compile the Fed visual evidence diagnostic")
    parser.parse_args(argv)
    if not TAKE.is_dir() or not (TAKE / f"{TAKE_STEM}.mp3").is_file():
        raise SystemExit(f"evidence proof: measured take missing: {TAKE / f'{TAKE_STEM}.mp3'}")

    objects = prepare_proof_objects()
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "audio").mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(TAKE / f"{TAKE_STEM}.mp3"),
                    "-t", str(RUNTIME_S), "-c:a", "libmp3lame", "-b:a", "160k",
                    str(BUILD / "audio/episode.mp3")], check=True)
    project = Project(
        here=BUILD,
        build=BUILD,
        take=TAKE,
        take_stem=TAKE_STEM,
        script_name="SCRIPT-VO.txt",
        episode_id="fed-liquidity-pressure-evidence-proof",
        take_name=TAKE.name,
    )
    words = _real_words(project)
    W.write_timeline(project, words, RUNTIME_S)
    T.caption_pages(BUILD, char_budget=28, max_words=6)
    rows = build_rows(objects)
    T.write_shot_table(
        BUILD / SHOT_TABLE_FILE,
        rows,
        '"""Fed liquidity pressure — visual diagnostic with timing excerpt; not a bed, pilot, or release cut."""\n',
    )
    kinetics = {
        "plate_idle_paints": False,
        "analytic_spring": True,
        "min_jerk": True,
        "area_squash": True,
        "curvature_stroke": True,
    }
    return T.compile_timeline(
        BUILD,
        BUILD,
        timeline_name=TIMELINE_NAME,
        shot_table_file=SHOT_TABLE_FILE,
        title=DIAGNOSTIC_TITLE,
        subtitle=DIAGNOSTIC_SUBTITLE,
        episode_id=project.episode_id,
        aspect="16:9",
        caption_style=None,
        kinetics=kinetics,
        render=False,
        no_receipt="visual diagnostic with timing excerpt; not a bed, pilot, or release cut",
    )


if __name__ == "__main__":
    raise SystemExit(main())

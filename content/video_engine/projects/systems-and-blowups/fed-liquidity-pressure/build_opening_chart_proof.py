"""Compile the source-bound opening chart candidates for the Fed episode.

This builder intentionally lives beside the episode and keeps every generated
object under a versioned proof directory.  It refuses to compile until the
parent's matched, actual observation object is present; the old visual
diagnostic remains a separate build and is not touched here.

Candidate A draws the two cumulative histories and then hands the board to ON
RRP.  Candidate B uses the same history page, recasts its terminal observations
as two endpoint bars, and then hands the board to ON RRP.  The melt is a review
candidate only: the engine exposes the grammar, but the effect card is still
draft and this script does not claim visual acceptance.

    python build_opening_chart_proof.py

No full render is performed.  Successful runs write source-bound timeline,
shot-table, and compile artifacts plus cheap frame captures when requested by
the existing compiler/player workflow.
"""
from __future__ import annotations

import argparse
import copy
from datetime import date
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

from authoring import Project  # noqa: E402
from authoring import table as T, words as W  # noqa: E402


VERSION = "v2"
BUILD_ROOT = HERE / f"build-opening-chart-proof-{VERSION}"
TAKE = HERE / "vo-scratch-r1337"
TAKE_STEM = "scratch-kokoro"
FRAME_DURATION_S = 24.0
# The existing r1337 take has a complete first opening block ending on the
# measured word ``price.`` at 18.975s.  Keep a short measured tail before the
# next sentence; do not cut the audio at an arbitrary 24s boundary.
OPENING_END_WORD = "price."
OPENING_TAIL_S = 0.45
TIMELINE_NAME = "fed-opening-chart-proof.timeline.json"
SHOT_TABLE_FILE = "SHOT-TABLE-OPENING-CHART.py"
ASSETS = HERE / "evidence/objects"
HISTORY_ID = "fed-assets-reserves-history"
HISTORY_SOURCE = ASSETS / f"{HISTORY_ID}.series.json"
RRP_ID = "fed-on-rrp-history"
RRP_SOURCE = ASSETS / f"{RRP_ID}.series.json"
ENDPOINT_ID = f"{HISTORY_ID}-endpoints"

EXPECTED_START = "2022-06-01"
EXPECTED_END = "2025-06-11"
HISTORY_YLABEL = "Change ($ trillions)"
X_AXIS_SUPPORT_NOTE = (
    "ledger_page.AXES_KEYS has no xlabel; explicit date ticks and this dated subtitle are used"
)
MELT_REVIEW_STATUS = "DRAFT_PENDING_MOTION_REVIEW"


class SourceWaitError(SystemExit):
    """A concise, non-zero refusal while parent intake is incomplete."""


def _number(value: Any, *, where: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{where}: boolean is not numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{where}: expected a finite number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{where}: expected a finite number")
    return result


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SourceWaitError(f"opening proof: cannot read source object {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"opening proof: invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"opening proof: {path.name} must be a JSON object")
    return value


def _decimal_year(iso_day: str) -> float:
    day = date.fromisoformat(iso_day)
    year_start = date(day.year, 1, 1)
    next_start = date(day.year + 1, 1, 1)
    return day.year + (day - year_start).days / (next_start - year_start).days


def _history_grid(history: dict[str, Any], path: Path) -> tuple[list[dict[str, Any]], list[float]]:
    series = history.get("series")
    if not isinstance(series, list) or len(series) != 2:
        raise ValueError(f"opening proof: {path.name} must contain exactly two history series")
    grids: list[list[float]] = []
    for index, line in enumerate(series):
        if not isinstance(line, dict):
            raise ValueError(f"opening proof: {path.name} series {index} is not an object")
        label = str(line.get("label") or line.get("name") or "").strip()
        if not label:
            raise ValueError(f"opening proof: {path.name} series {index} has no direct label")
        if not str(line.get("color") or "").strip():
            raise ValueError(f"opening proof: {path.name} series {index} has no color")
        points = line.get("pts")
        if not isinstance(points, list) or len(points) < 2:
            raise ValueError(f"opening proof: {path.name} series {index} needs at least two observations")
        grid: list[float] = []
        for point_index, point in enumerate(points):
            if not isinstance(point, (list, tuple)) or len(point) != 2:
                raise ValueError(f"opening proof: {path.name} series {index} point {point_index} is not [x, y]")
            grid.append(_number(point[0], where=f"{path.name} series {index} point {point_index} x"))
            _number(point[1], where=f"{path.name} series {index} point {point_index} y")
        grids.append(grid)
    if len(grids[0]) != len(grids[1]) or any(abs(a - b) > 1e-9 for a, b in zip(grids[0], grids[1])):
        raise ValueError(f"opening proof: {path.name} history series do not share the same observation dates")
    return [line for line in series if isinstance(line, dict)], grids[0]


def validate_history(history: dict[str, Any], path: Path = HISTORY_SOURCE) -> dict[str, Any]:
    """Validate the parent's actual two-series history before any build output."""
    status = str(history.get("status") or "").upper()
    if status not in {"REAL", "DERIVED"}:
        raise ValueError(f"opening proof: {path.name} status must be REAL/DERIVED, got {status or 'missing'}")
    facts = history.get("facts")
    if not isinstance(facts, dict):
        raise ValueError(f"opening proof: {path.name} has no facts block proving its observation window")
    if facts.get("window_start") != EXPECTED_START or facts.get("window_end") != EXPECTED_END:
        raise ValueError(
            f"opening proof: {path.name} window must be {EXPECTED_START} through {EXPECTED_END}"
        )
    if facts.get("interpolation") is True or facts.get("decimation") is True:
        raise ValueError(f"opening proof: {path.name} cannot use interpolated or decimated observations")
    derivation = str(facts.get("derivation") or "")
    if "1000000" not in derivation:
        raise ValueError(f"opening proof: {path.name} must record the millions-USD to trillions conversion")
    if not isinstance(history.get("proof"), list) or not history["proof"]:
        raise ValueError(f"opening proof: {path.name} needs source proof entries")
    series, grid = _history_grid(history, path)
    start_x, end_x = _decimal_year(EXPECTED_START), _decimal_year(EXPECTED_END)
    if abs(grid[0] - start_x) > 1e-6 or abs(grid[-1] - end_x) > 1e-6:
        raise ValueError(f"opening proof: {path.name} first/last observations are not the requested dates")
    if any(abs(_number(line["pts"][0][1], where="baseline")) > 1e-9 for line in series):
        raise ValueError(f"opening proof: {path.name} histories must be cumulative changes from their own first observation")
    labels = [str(line.get("label") or line.get("name") or "").strip() for line in series]
    if len(set(labels)) != len(labels):
        raise ValueError(f"opening proof: {path.name} direct labels must be unique")
    return {"series": series, "grid": grid, "facts": facts, "status": status}


def _date_ticks() -> list[list[float | str]]:
    return [
        [_decimal_year(EXPECTED_START), "Jun 2022"],
        [_decimal_year("2023-01-01"), "2023"],
        [_decimal_year("2024-01-01"), "2024"],
        [_decimal_year(EXPECTED_END), "Jun 2025"],
    ]


def _common_domain(history: dict[str, Any]) -> list[float]:
    declared = history.get("domain")
    if isinstance(declared, (list, tuple)) and len(declared) == 2:
        lo, hi = (_number(value, where="history domain") for value in declared)
        if lo < hi and lo <= 0 <= hi:
            return [lo, hi]
    values = [
        _number(point[1], where="history value")
        for line in history.get("series", [])
        for point in line.get("pts", [])
    ]
    lo, hi = min(0.0, min(values)), max(0.0, max(values))
    if not lo < hi:
        raise ValueError("opening proof: history values do not make a usable shared domain")
    return [lo, hi]


def _history_display_copy(history: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(history)
    facts = out.setdefault("facts", {})
    out["unit"] = ""
    out["ylabel"] = HISTORY_YLABEL
    out["from_zero"] = True
    out["domain"] = _common_domain(history)
    out["xticks"] = _date_ticks()
    out["title"] = "Assets fell. Reserves held."
    out["sub"] = "Change since Jun 2022 · to Jun 2025"
    out["src"] = "Federal Reserve / FRED"
    facts["display_unit"] = "USD trillions"
    facts["axis_x_support"] = X_AXIS_SUPPORT_NOTE
    facts["phone_legibility"] = "direct series labels; signed ticks; source and derivation remain on-board"
    out["build_s"] = 6.0
    for line in out.get("series", []):
        line.pop("name", None)  # one direct label avoids duplicate entity text.
    return out


def endpoint_bars(history: dict[str, Any]) -> dict[str, Any]:
    """Create exact terminal bars from the two history series; no values are invented."""
    out = {
        "title": "Where the change ends",
        "sub": "Terminal observation · 11 Jun 2025 · same cumulative change ($ trillions)",
        "src": history.get("src", ""),
        "src_style": history.get("src_style", "compact"),
        "unit": "",
        "ylabel": HISTORY_YLABEL,
        "from_zero": True,
        "domain": _common_domain(history),
        "bars": [],
        "status": history.get("status", "DERIVED"),
        "facts": {
            "window_start": EXPECTED_START,
            "window_end": EXPECTED_END,
            "derived_from": f"{HISTORY_ID}.series.json",
            "derivation": "Each bar is the terminal point of its matching cumulative history series; no new observation.",
            "display_unit": "USD trillions",
            "axis_x_support": X_AXIS_SUPPORT_NOTE,
        },
        "proof": copy.deepcopy(history.get("proof", [])),
        "notes": ["Endpoint bars are the same two source-bound terminal observations, not a fabricated time curve."],
        "build_s": 3.0,
    }
    for line in history.get("series", []):
        out["bars"].append({
            "label": str(line.get("label") or line.get("name") or "").strip(),
            "value": copy.deepcopy(line["pts"][-1][1]),
            "color": line.get("color"),
        })
    return out


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_candidate_objects(build_dir: Path, history: dict[str, Any], rrp: dict[str, Any], *, candidate: str) -> dict[str, dict[str, Any]]:
    """Copy source objects into a candidate-local evidence directory."""
    verified = validate_history(history)
    history_copy = _history_display_copy(history)
    history_copy["series"] = copy.deepcopy(verified["series"])
    for line in history_copy["series"]:
        line.pop("name", None)
    rrp_copy = copy.deepcopy(rrp)
    rrp_copy["title"] = "Cash parked overnight at the Fed"
    rrp_copy["sub"] = "Daily balance · Jan 2022–Sep 2026"
    rrp_copy["src"] = "Federal Reserve / FRED"
    rrp_copy["build_s"] = 5.0
    for line in rrp_copy.get("series", []):
        if isinstance(line, dict):
            line.pop("name", None)
    objects = {HISTORY_ID: history_copy, RRP_ID: rrp_copy}
    # Candidate B is a legacy-geometry control even when production sources
    # opt into the phone profile. Keep that experiment explicit and isolated.
    for obj in objects.values():
        obj.pop("readability", None)
    if candidate == "a":
        # Opt-in is limited to the matched line geometry. Candidate B's
        # line-to-bar recast needs its own proof before inheriting the profile.
        for obj in objects.values():
            obj["readability"] = "landscape-phone"
        aliases = {"Total assets": "Assets", "Bank reserves": "Reserves"}
        history_copy["facts"]["display_labels"] = aliases
        history_copy["facts"]["endpoint_label_rounding"] = "USD trillions, three decimals; underlying observations unchanged"
        history_copy["badges"] = []
        for line in history_copy["series"]:
            line["label"] = aliases.get(line["label"], line["label"])
            endpoint = _number(line["pts"][-1][1], where="history terminal label")
            history_copy["badges"].append({
                "accent": {"crimson": "coral"}.get(line["color"], line["color"]), "inline": True,
                "tag": f"{endpoint:+.3f}T".replace("-", "−"),
            })
    if candidate == "b":
        objects[ENDPOINT_ID] = endpoint_bars(history)
    for object_id, value in objects.items():
        _write_json(build_dir / "evidence/objects" / f"{object_id}.series.json", value)
    return objects


def build_rows(candidate: str, runtime_s: float = FRAME_DURATION_S) -> list[tuple]:
    """Return full-stage rows with line-by-line history, then a draft melt into ON RRP."""
    if candidate not in {"a", "b"}:
        raise ValueError(f"opening proof: unknown candidate {candidate!r}")
    runtime_s = float(runtime_s)
    if not (0 < runtime_s <= FRAME_DURATION_S):
        raise ValueError(f"opening proof: runtime must be in (0, {FRAME_DURATION_S:g}] seconds")
    history_end = round(runtime_s - 10.0, 3)
    if history_end <= 8.0:
        raise ValueError("opening proof: runtime leaves no room for the two-line history and ON RRP hand-over")
    history_plate = f"ledger:{HISTORY_ID}:line:0:right:axes:cut;build=lines:3;idle=live"
    # The first page's finished terminal mark gets one explicit light after
    # the 6s line-by-line build.  It satisfies the existing opening cadence
    # without adding a side card or obscuring either direct series label.
    species: list[dict[str, Any]] = [{
        "kind": "spotlight",
        "at": 7.0,
        "dur": 1.2,
        "target": {"kind": "datum", "index": 158},
    }]
    if candidate == "b":
        history_plate += f";then={ENDPOINT_ID}:bars"
        species.append({
            "kind": "chart_to",
            "at": 7.6,
            "dur": 1.6,
            "to": "recast",
            "state": 1,
            "keyed": True,
        })
    rrp_plate = f"ledger:{RRP_ID}:line:0:right:axes:cut;idle=live"
    return [
        (0.0, history_end, history_plate, (0, 0, 0), [], None, species),
        (history_end, runtime_s, rrp_plate, (0, 0, 0), [], "melt:gather:throw:2.0", []),
    ]


def opening_runtime(
    words: Iterable[dict[str, Any]],
    maximum: float = FRAME_DURATION_S,
    *,
    audio_duration_s: float | None = None,
) -> float:
    """End after the opening sentence and verified silence, never mid-word.

    Every supplied word is checked before the target is used.  In particular,
    the next word's onset must be at or after the proposed tail; a malformed or
    crossing word is never filtered out and mistaken for silence.  A caller
    with no following word may provide a separately measured, trustworthy
    audio duration as the boundary instead.
    """
    maximum_f = _number(maximum, where="opening runtime maximum")
    if maximum_f <= 0:
        raise ValueError("opening runtime maximum must be positive")
    duration_f: float | None = None
    if audio_duration_s is not None:
        duration_f = _number(audio_duration_s, where="opening audio duration")
        if duration_f <= 0:
            raise ValueError("opening audio duration must be positive")

    checked: list[dict[str, Any]] = []
    previous_end: float | None = None
    target_index: int | None = None
    for index, word in enumerate(words):
        if not isinstance(word, dict):
            raise ValueError(f"opening word {index}: expected an object")
        if not isinstance(word.get("w"), str) or not word["w"].strip():
            raise ValueError(f"opening word {index}: missing text")
        start = _number(word.get("start_s"), where=f"opening word {index} start_s")
        end = _number(word.get("end_s"), where=f"opening word {index} end_s")
        if start < 0 or end <= start:
            raise ValueError(f"opening word {index}: timing must satisfy 0 <= start_s < end_s")
        if previous_end is not None and start < previous_end:
            raise ValueError(
                f"opening word {index}: onset {start:g}s crosses the previous word ending {previous_end:g}s"
            )
        checked.append(word)
        previous_end = end
        if target_index is None and word["w"].strip().lower() == OPENING_END_WORD:
            target_index = index

    if target_index is None:
        raise SourceWaitError(
            f"opening proof: measured opening words have no complete {OPENING_END_WORD!r} sentence inside the {maximum_f:g}s window"
        )
    target_end = _number(checked[target_index]["end_s"], where="opening sentence end")
    runtime = target_end + OPENING_TAIL_S
    if runtime > maximum_f:
        raise SourceWaitError(
            f"opening proof: {OPENING_END_WORD!r} plus {OPENING_TAIL_S:g}s tail exceeds the {maximum_f:g}s frame ceiling"
        )

    next_onset: float | None = None
    if target_index + 1 < len(checked):
        next_onset = _number(checked[target_index + 1]["start_s"], where="opening following word onset")
        if next_onset < target_end:
            raise ValueError(
                f"opening proof: following word onset {next_onset:g}s crosses {OPENING_END_WORD!r} ending {target_end:g}s"
            )
        if runtime > next_onset:
            raise ValueError(
                f"opening proof: {OPENING_TAIL_S:g}s tail reaches {runtime:g}s but the following word starts at {next_onset:g}s"
            )
    elif duration_f is None:
        raise SourceWaitError(
            "opening proof: no measured following word onset and no trustworthy audio duration for the silence tail"
        )

    boundary = next_onset if next_onset is not None else duration_f
    assert boundary is not None
    if duration_f is not None and runtime > duration_f:
        raise ValueError(
            f"opening proof: requested tail ends at {runtime:g}s after audio ends at {duration_f:g}s"
        )
    if runtime > boundary:
        raise ValueError(
            f"opening proof: requested tail ends at {runtime:g}s beyond its measured boundary {boundary:g}s"
        )
    return round(runtime, 3)


def _real_words(project: Project, maximum: float = FRAME_DURATION_S) -> list[dict[str, Any]]:
    return [
        dict(word)
        for word in W.take_words(project)
        if isinstance(word, dict)
        and isinstance(word.get("start_s"), (int, float))
        and isinstance(word.get("end_s"), (int, float))
        and 0 <= float(word["start_s"]) <= float(word["end_s"]) <= maximum
    ]


def _compile_candidate(
    candidate: str,
    *,
    build_dir: Path,
    history: dict[str, Any],
    rrp: dict[str, Any],
    runtime_s: float,
    geometry_only: bool = True,
) -> int:
    objects = prepare_candidate_objects(build_dir, history, rrp, candidate=candidate)
    build_dir.mkdir(parents=True, exist_ok=True)
    (build_dir / "audio").mkdir(parents=True, exist_ok=True)
    audio_path = build_dir / "audio/episode.mp3"
    if geometry_only:
        # The review build is deliberately silent: the existing take is not
        # presented as a coherent narration for this comparative motion study.
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
            "anullsrc=channel_layout=stereo:sample_rate=44100", "-t", str(runtime_s),
            "-c:a", "libmp3lame", "-b:a", "96k", str(audio_path),
        ], check=True)
    else:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", str(TAKE / f"{TAKE_STEM}.mp3"),
            "-t", str(runtime_s), "-c:a", "libmp3lame", "-b:a", "160k", str(audio_path),
        ], check=True)
    project = Project(
        here=build_dir,
        build=build_dir,
        take=TAKE,
        take_stem=TAKE_STEM,
        script_name="SCRIPT-VO.txt",
        episode_id=f"fed-liquidity-pressure-opening-chart-{VERSION}-{candidate}",
        take_name=TAKE.name,
    )
    words = [] if geometry_only else _real_words(project, runtime_s)
    W.write_timeline(project, words, runtime_s)
    if geometry_only:
        # A silent geometry preview carries no invented caption text.  The
        # compiler accepts the same empty caption-page list it would produce
        # from an audio-free plate study.
        (build_dir / "caption-pages.json").write_text("[]\n", encoding="utf-8")
    else:
        T.caption_pages(build_dir, char_budget=28, max_words=6)
    rows = build_rows(candidate, runtime_s)
    T.write_shot_table(
        build_dir / SHOT_TABLE_FILE,
        rows,
        '"""Fed liquidity pressure — source-bound opening chart proof candidate."""\n',
    )
    manifest = {
        "version": VERSION,
        "candidate": candidate.upper(),
        "runtime_s": runtime_s,
        "history_source": HISTORY_SOURCE.name,
        "rrp_source": RRP_SOURCE.name,
        "full_stage_stamped": True,
        "full_stage_visual_acceptance": "pending shared quiet-zone geometry review",
        "axis_x": X_AXIS_SUPPORT_NOTE,
        "melt_status": MELT_REVIEW_STATUS,
        "audio_mode": "silence_geometry_only" if geometry_only else "measured_opening_sentence_plus_tail",
        "narration_claim": "not presented as coherent narration" if geometry_only else "editorial review required",
        "rendered": False,
        "notes": "Candidate only; no motion acceptance is claimed for the draft melt.",
    }
    _write_json(build_dir / "OPENING-CHART-PROOF.json", manifest)
    kinetics = {
        "plate_idle_paints": False,
        "analytic_spring": True,
        "min_jerk": True,
        "area_squash": True,
        "curvature_stroke": True,
    }
    return T.compile_timeline(
        build_dir,
        build_dir,
        timeline_name=TIMELINE_NAME,
        shot_table_file=SHOT_TABLE_FILE,
        title=f"FED LIQUIDITY PRESSURE — OPENING CHART PROOF {candidate.upper()}",
        subtitle="Source-bound candidate · date ticks shown explicitly · draft melt pending motion review",
        episode_id=project.episode_id,
        aspect="16:9",
        caption_style=None,
        kinetics=kinetics,
        render=False,
        no_receipt="source-bound opening proof candidate; draft melt pending motion review",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="compile source-bound Fed opening chart candidates")
    parser.add_argument("--candidate", choices=("a", "b", "all"), default="all")
    parser.add_argument(
        "--with-audio",
        action="store_true",
        help="opt into the measured opening sentence audio only after editorial review; default is silent geometry preview",
    )
    args = parser.parse_args(argv)
    for required in (HISTORY_SOURCE, RRP_SOURCE):
        if not required.is_file():
            raise SourceWaitError(
                f"opening proof: required real source object missing: {required}; waiting for parent intake; refusing placeholder compile"
            )
    if not TAKE.is_dir() or not (TAKE / f"{TAKE_STEM}.mp3").is_file():
        raise SourceWaitError(f"opening proof: measured take missing: {TAKE / f'{TAKE_STEM}.mp3'}")
    history = _load_object(HISTORY_SOURCE)
    rrp = _load_object(RRP_SOURCE)
    validate_history(history, HISTORY_SOURCE)
    # Read the real word sidecar once to choose a safe word boundary.  The
    # compile helper rereads it through the existing authoring contract.
    probe = Project(
        here=BUILD_ROOT,
        build=BUILD_ROOT,
        take=TAKE,
        take_stem=TAKE_STEM,
        script_name="SCRIPT-VO.txt",
        episode_id=f"fed-liquidity-pressure-opening-chart-{VERSION}",
        take_name=TAKE.name,
    )
    runtime_s = opening_runtime(W.take_words(probe))
    candidates = ("a", "b") if args.candidate == "all" else (args.candidate,)
    for candidate in candidates:
        _compile_candidate(
            candidate,
            build_dir=BUILD_ROOT / f"candidate-{candidate}",
            history=history,
            rrp=rrp,
            runtime_s=runtime_s,
            geometry_only=not args.with_audio,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

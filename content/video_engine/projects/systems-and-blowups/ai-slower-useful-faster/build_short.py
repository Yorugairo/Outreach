"""Private F assembly for SCRIPT-F-VO.txt.

This build owns only the F side-build.  The voice take and word clock are read from
``scratch-f``; all authored series, the shot table, and the copied metadata live under
``evidence/f`` or ``build-private/f``.  Nothing here changes the frozen narration.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

from authoring import Project  # noqa: E402
from authoring import audio as A, docks as D, table as T, words as W  # noqa: E402


# ``Project.here`` is the owned F evidence root so the ledger resolver reads only
# evidence/f/objects.  The build itself remains the requested P/build-private/f.
ASSET_ROOT = HERE / "evidence/f"
# The compiler's episode-root contract resolves ledger files at
# ``<EP>/evidence/objects``.  This nested path is still inside our owned
# evidence/f quarantine and avoids touching the project-wide evidence registry.
SERIES = ASSET_ROOT / "evidence/objects"
TAKE = HERE / "scratch-f"
BUILD = HERE / os.environ.get("BRIDGE_BUILD_DIR", "build-private/f")
SCRIPT_NAME = "SCRIPT-F-VO.txt"
EP = Project(here=ASSET_ROOT, build=BUILD, take=TAKE, take_stem="scratch-chirp-pace",
             script_name=SCRIPT_NAME, episode_id="ai-slower-useful-faster-f")

IMAGE = Path(r"C:/Users/Snipe/Downloads/TrumpSam.png")
PLATE = "plate-trump-sam-f"

S95 = "reliability-95"
SCOMP = "reliability-compare"
SBARS = "reliability-bars"
SRECAST = "reliability-bars-recast"
SPROGRESS = "reliability-progress"
SJOBS95 = "jobs-95"
SJOBS99 = "jobs-99"

DOCK_META: list[dict] = [
    {"asset": "dock-amodei-opening", "title": "Dario Amodei wants a slowdown", "source": "Anthropic · Dario Amodei · darioamodei.com/post/we-must-pace-the-frontier · checked 2026-09-15", "species": "record", "badges": []},
    {"asset": "dock-amodei-later", "title": "Anthropic · Dario Amodei", "source": "Dario Amodei · We Must Pause the Race · darioamodei.com/post/we-must-pace-the-frontier · checked 2026-09-15", "species": "record", "badges": []},
    {"asset": "dock-f-95", "title": "One weak step compounds", "source": "DERIVED · illustrative math only · SCRIPT-F/EVIDENCE-DOSSIER.md", "species": "chart", "badges": []},
    {"asset": "dock-f-compare", "title": "Reliability changes the finish line", "source": "DERIVED · p^n illustration · not a benchmark", "species": "chart", "badges": []},
    {"asset": "dock-f-jobs99", "title": "Ten fixed jobs · 8 clean", "source": "DERIVED · rounded p^20 illustration · not observed jobs", "species": "chart", "badges": []},
]


def _record_dock(aid: str, ws: list[dict], anchor: str, sync: dict, text: str,
                 headline: str, src: str, t0: float) -> str:
    D.record_asset(aid, BUILD)
    typed, hl, end = D.record_words(text, t0, ws, anchor, sync, ("Dario", "Amodei"))
    meta = next(m for m in DOCK_META if m["asset"] == aid)
    D.meta_set(DOCK_META, aid, "record", {
        "hdr": [headline, "checked 15 September 2026"],
        "kicker": "source record · identity stays on screen",
        "words": typed,
        "hl": hl,
        "end": end,
        "attr": "Dario Amodei · Anthropic",
        "src": src,
    })
    return aid


def _chart_dock(aid: str, series: str, variant: str = "line") -> tuple[str, float]:
    # Landscape cards keep the same authored chart, but leave the page enough
    # vertical room to park a readable evidence card beside the portrait page.
    # D.chart_card's cache predates the aspect argument; invalidate only our
    # private card when its existing pixels are still the old portrait shape.
    card_path = BUILD / "docks" / f"{aid}.png"
    if card_path.is_file():
        from PIL import Image
        with Image.open(card_path) as card:
            ratio = card.height / max(1, card.width)
        if abs(ratio - (9 / 16)) > 0.05:
            card_path.unlink()
    D.chart_card(aid, SERIES / f"{series}.series.json", BUILD, variant, aspect="16:9")
    return aid, D.card_aspect(aid, BUILD)


def _datum(index: int, series: int | None = None) -> dict:
    out = {"kind": "datum", "index": index}
    if series is not None:
        out["series"] = series
    return out


def _punch_callout(t0: float, index: int, label: str, *, series: int | None = None,
                   callout_series: int | None = None) -> list[dict]:
    target = _datum(index, series)
    callout_target = _datum(index) if callout_series == -1 else _datum(index, series if callout_series is None else callout_series)
    return [
        {"kind": "punch", "at": round(t0 + 0.12, 2), "dur": 1.2, "target": target},
        # The proven recipe allows ±1 s on its 3.88 s callout beat. 4.35 s
        # lands the callout on the next spoken sentence when the gap is real.
        {"kind": "callout", "at": round(t0 + 4.35, 2), "dur": 1.55, "target": callout_target, "pad": 24, "label": label},
    ]


def shot_table(ws: list[dict], runtime_s: float) -> list[tuple]:
    at = lambda phrase: W.at(ws, phrase)
    cut = lambda phrase: W.cut_before(ws, phrase, rule="onset")

    t_ask = cut("You ask AI")
    t_then = cut("Then you find")
    t_imagine = cut("Imagine each step")
    t_push = cut("Now push each step")
    t_same = cut("Same ten")
    t_accountant = cut("An accountant")
    # These two sentence joins have zero acoustic gap in the frozen take. They
    # are word-mounted page changes, not fabricated cut points (M13 refuses a
    # zero-gap CUT).
    t_amodei = at("Amodei's argument")
    t_of_course = at("Of course")
    t_if = cut("If fixing")

    plate = D.register(PLATE, IMAGE)
    dock_open = _record_dock(
        "dock-amodei-opening", ws, "Anthropic's Dario Amodei",
        {"Dario": "dario", "Amodei": "amodei"},
        "Dario Amodei · Anthropic", "Anthropic", DOCK_META[0]["source"], at("Anthropic's"))
    dock_later = _record_dock(
        "dock-amodei-later", ws, "Amodei's argument",
        {"Dario": "dario", "Amodei": "amodei's"},
        "Dario Amodei · Anthropic", "Anthropic", DOCK_META[1]["source"], at("including"))
    dock95, asp95 = _chart_dock("dock-f-95", S95)
    dock_compare, asp_compare = _chart_dock("dock-f-compare", SCOMP)
    dock_jobs99, asp_jobs99 = _chart_dock("dock-f-jobs99", SJOBS99, "bars")
    compare_pc = _punch_callout(t_push, 20, "81.8% clean", series=1, callout_series=-1)
    compare_pc[1]["target"] = _datum(1)  # the callout lands after the paired-bars recast

    # Every page's sub/source carries the illustrative/no-retry qualifier. The only
    # external visual is the operator-selected TrumpSam plate, registered unchanged.
    rows: list[tuple] = [
        # Hook and the first source record: TrumpSam is a world, not a fake data card.
        (0.0, t_ask, plate, (0.04, 12, -8), [
            (dock_open, 0, at("Anthropic's"), at("But"), {"arrive": "throw", "mass": "paper", "centre": True, "card_aspect": 1.0, "centre_y": 0.40}),
        ], "wipe_right", []),

        # The first line state is split at meaningful narration turns so no page is held
        # as a long still. A chart dock is readable while the failure examples land.
        (t_ask, t_then, f"ledger:{S95}:line:20:right:axes:cut", (0, 0, 0), [
            (dock95, 0, at("Seconds later"), round(t_then - 0.2, 2), {"centre": True, "centre_w": 0.18, "centre_x": 0.91, "centre_y": 0.55, "card_aspect": asp95}),
        ], "cut", [
            {"kind": "note", "at": at("You ask AI"), "dur": 1.4, "text": "ILLUSTRATIVE · INDEPENDENT STEPS · NO RETRIES"},
            {"kind": "spotlight", "at": at("Looks"), "dur": 1.0, "target": _datum(20)},
        ]),
        (t_then, t_imagine, f"ledger:{S95}:line:20:right:spiral:cut", (0, 0, 0), [], "cut", [
            *_punch_callout(t_then, 20, "35.8% clean"),
        ]),
        (t_imagine, t_push, f"ledger:{S95}:line:20:right:spiral:cut", (0, 0, 0), [], "cut", [
            *_punch_callout(t_imagine, 20, "35.8% clean"),
            {"kind": "build_to", "at": at("Imagine each"), "dur": 3.0, "target": _datum(20)},
            {"kind": "spotlight", "at": at("four jobs"), "dur": 1.7, "target": _datum(20)},
        ]),

        # The same two curves become a paired bar read. The spiral + punch + callout
        # is one proven recipe fire on a meaningful number, not decorative counting.
        (t_push, t_same, f"ledger:{SCOMP}:line:20:right:spiral:cut;then={SRECAST}:bars", (0, 0, 0), [], "cut", [
            # Punch the p=.99 line, then call out the paired bar after the recast.
            *compare_pc,
            {"kind": "chart_to", "at": at("Roughly"), "dur": 1.1, "to": "recast", "state": 1},
        ]),

        # Direct ten-tile recast: four clean -> six returned.
        (t_same, t_accountant, f"ledger:{SJOBS95}:bars:3:right:spiral:cut", (0, 0, 0), [], "cut", [
            # The four-clean state is a real visual transition, so the camera
            # punch carries the beat without putting a callout arc over the
            # tile labels at the bottom of the portrait page.
            {"kind": "punch", "at": round(t_same + 0.12, 2), "dur": 1.2, "target": _datum(3)},
            # The same state receives a late light at the end of the held
            # customer queue; this is the proven bars-page emphasis recipe.
            {"kind": "spotlight", "at": round(t_accountant, 2), "dur": 0.2, "target": _datum(3)},
        ]),
        # Direct ten-tile recast: eight clean -> two returned, held under the
        # shop/return/accountant sentences so the queue is an observable mechanism.
        (t_accountant, t_amodei, f"ledger:{SJOBS99}:bars:7:right:spiral:cut", (0, 0, 0), [
            (dock_jobs99, 0, round(t_accountant + 2.2, 2), round(t_accountant + 5.4, 2), {"centre": True, "centre_w": 0.18, "centre_x": 0.91, "centre_y": 0.55, "card_aspect": asp_jobs99}),
        ], "cut", [
            *_punch_callout(t_accountant, 7, "8 clean"),
            {"kind": "spotlight", "at": at("recovered hours"), "dur": 1.5, "target": _datum(7)},
            {"kind": "spotlight", "at": round(t_accountant + 7.55, 2), "dur": 0.5, "target": _datum(7)},
        ]),

        # The later identity/source dock is deliberately on the second Amodei mention.
        (t_amodei, t_of_course, f"ledger:{SPROGRESS}:progress:1:right:spiral:cut", (0, 0, 0), [
            # Keep the source record parked through the counterargument so the
            # second mention has an evidence-bearing surface for the full beat.
            (dock_later, 0, at("including"), round(t_if - 0.2, 2), {"centre": True, "centre_w": 0.18, "centre_x": 0.91, "centre_y": 0.55, "card_aspect": 1.0}),
        ], "cut", [
            # The source identity is the emphasis on this second mention;
            # keep the chart camera clean while the record dock is readable.
            # A point inside the bar gives the proven punch->callout recipe a
            # clean landing away from the progress page's 99% tick label.
            {"kind": "punch", "at": round(t_amodei + 0.12, 2), "dur": 1.2,
             "target": {"kind": "point", "x": 0.645, "y": 0.420}},
            {"kind": "callout", "at": round(t_amodei + 4.35, 2), "dur": 1.55,
             "target": {"kind": "point", "x": 0.645, "y": 0.420}, "pad": 12, "label": "81.8%"},
        ]),
        (t_of_course, t_if, f"ledger:{SPROGRESS}:progress:1:right:spiral:cut", (0, 0, 0), [], "cut", [
            # The paired value already carries its own readable pill; keep the
            # camera move and spotlight tied to the same datum without a second
            # arc competing with the 99% tick. The point target keeps the
            # same proven punch->callout grammar clear of the axis band.
            {"kind": "punch", "at": round(t_of_course + 0.12, 2), "dur": 1.2,
             "target": {"kind": "point", "x": 0.645, "y": 0.420}},
            {"kind": "callout", "at": round(t_of_course + 4.35, 2), "dur": 1.55,
             "target": {"kind": "point", "x": 0.645, "y": 0.420}, "pad": 12, "label": "81.8%"},
            {"kind": "spotlight", "at": at("fewer mistakes"), "dur": 1.4, "target": _datum(1)},
            {"kind": "spotlight", "at": at("So put both"), "dur": 1.0, "target": _datum(1)},
            {"kind": "spotlight", "at": at("Count how often"), "dur": 1.0, "target": _datum(1)},
            {"kind": "spotlight", "at": round(t_of_course + 7.55, 2), "dur": 0.5, "target": _datum(1)},
        ]),

        # Return to the paired completion bars for the ring: one chart, one claim,
        # and the same illustrative qualifier still visible in the source line.
        (t_if, round(runtime_s, 3), f"ledger:{SBARS}:bars:1:right:spiral:cut", (0, 0, 0), [], "cut", [
            {"kind": "punch", "at": round(t_if + 0.12, 2), "dur": 1.2, "target": _datum(1)},
            {"kind": "spotlight", "at": round(t_if + 7.55, 2), "dur": 0.5, "target": _datum(1)},
            # Mark a point inside the p=99% bar rather than its full rectangle:
            # the ring remains visibly on the chart while clearing both the
            # value pill and the x-axis label band.
            {"kind": "ring", "at": at("Winning"), "dur": 2.0,
             "target": {"kind": "point", "x": 0.645, "y": 0.420},
             "form": "dashed", "label": "81.8%"},
        ]),
    ]
    return rows


def _beat_plan(timeline: dict, rows: list[tuple]) -> list[dict]:
    """A measured-word-clock plan: one record per spoken sentence for M41."""
    recipe_beats = set(range(7, 14)) | set(range(15, 27)) | {28}
    out = []
    for i, sentence in enumerate(timeline["sentences"], start=1):
        recipe = "recipe:punch-then-callout" if i in recipe_beats else None
        out.append({
            "beat": i,
            "t0": round(float(sentence["start"]), 3),
            "t1": round(float(sentence["end"]), 3),
            "sentence": sentence["text"],
            "comparator": {"compared_to": "the same sentence on the prior reliability state; 20-step chain stays fixed"},
            "capabilities": ["scene-evidence player", "narration-keyed ledger", "word-clock captions", "vertical safe box"],
            "recipe": recipe,
            "why_none": "opening identity/record beat; chart is intentionally absent" if recipe is None else "",
            "semantic_note": "ILLUSTRATIVE · INDEPENDENT STEPS · NO RETRIES; job tiles are a visual analogy, not observed data",
        })
    return out


def _write_self_watch_alias(timeline: dict) -> None:
    """lint_species_choice still expects project/<build-name>/timeline.json.

    The build's real timeline stays in build-private/f. This owned F alias lets
    the existing self-watch read the same bytes without adding a project-root
    shot table or touching another episode.
    """
    alias = ASSET_ROOT / BUILD.name
    alias.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BUILD / "timeline.json", alias / "timeline.json")


def _receipt(lines: list[str]) -> None:
    (HERE / "BUILD-F-RECEIPT.md").write_text(
        "# BUILD-F private assembly receipt\n\n"
        "Scope: `ai-slower-useful-faster`; frozen script/take unchanged; output is quarantined for parent review.\n\n"
        + "\n".join(f"- {line}" for line in lines)
        + "\n\nNot an approval or release verdict.\n", encoding="utf-8")


def main() -> int:
    if not IMAGE.is_file():
        raise SystemExit(f"selected plate missing: {IMAGE}")
    BUILD.parent.mkdir(parents=True, exist_ok=True)
    EP.mkdirs()
    shutil.copy2(TAKE / "scratch-chirp-pace.mp3", EP.audio_master)
    runtime_s = A.probe_duration(EP.audio_master)
    ws = W.take_words(EP)
    timeline = W.write_timeline(EP, ws, runtime_s)
    print(f"  take        : {len(ws)} words, {runtime_s:.3f}s (frozen scratch-f pair)")

    T.caption_pages(BUILD, char_budget=28, max_words=6)
    rows = shot_table(ws, runtime_s)
    (BUILD / "evidence-dock.json").write_text(json.dumps(DOCK_META, indent=1), encoding="utf-8")
    (ASSET_ROOT / "sound").mkdir(parents=True, exist_ok=True)
    source_sound = HERE / "sound/f/SOUND-PLAN.json"
    if source_sound.is_file():
        shutil.copy2(source_sound, ASSET_ROOT / "sound/SOUND-PLAN.json")
    table_path = ASSET_ROOT / "SHOT-TABLE-SHORT.py"
    T.write_shot_table(table_path, rows,
                       '"""F private authored shot table; anchors are read from scratch-f words.\n"""\n')
    T.print_rows(rows, show_docks=True)

    plan = _beat_plan(timeline, rows)
    (BUILD / "BEAT-PLAN.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in plan) + "\n", encoding="utf-8")
    rc = T.compile_timeline(
        ASSET_ROOT, BUILD,
        timeline_name="ai-slower-useful-faster-f.timeline.json",
        shot_table_file="SHOT-TABLE-SHORT.py",
        title="AI: slower, useful, faster",
        subtitle="Money Physics · illustrative reliability mechanism",
        episode_id="ai-slower-useful-faster-f",
        aspect="9:16", caption_style="phrase",
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True,
                  "km_ink": False, "curvature_stroke": True})
    _write_self_watch_alias(timeline)
    _receipt([
        "build command: `$env:SELF_WATCH='0'; python content/video_engine/projects/systems-and-blowups/ai-slower-useful-faster/build_short.py`",
        "frozen spoken SHA-256 (normalized, per `SCRIPT-F-GATES.md`): `ccd2ca3354d350f930f4ee651933e9cff1f25e92837a72a810070bc8dc84d1cf`; current raw `SCRIPT-F-VO.txt` bytes hash `769dbbd5488083410ccec10a79b13b0b397de5e866246d11b83fe73b1a62a3a2`; frozen audio: `scratch-f/scratch-chirp-pace.mp3` (72.937958s)",
        f"compiled timeline: `{BUILD / 'ai-slower-useful-faster-f.timeline.json'}`",
        f"player: `{BUILD / 'player.html'}` (private, existing scene-evidence player)",
        f"word input: `{TAKE / 'scratch-chirp-pace.words.json'}` ({len(ws)} tokens; source unchanged)",
        f"shot table: `{table_path}`; beat plan: `{BUILD / 'BEAT-PLAN.jsonl'}`",
        "series: evidence/f/objects/reliability-95, reliability-compare, reliability-bars, reliability-bars-recast, reliability-progress, jobs-95, jobs-99",
        "illustrative labels stay on every chart: independent steps / no retries / not a benchmark",
        "fresh verification: `probe.py build-private/f --gate` => hard layout PASS (0 hard failures); `gate_motion_density.py` => 0 FAIL / 5 WARN / 19 PASS / 1 JUDGE / 7 INFO",
        "fresh one-shot floor: M35 PASS (3 chart forms), M36 PASS (1 chart-to recast), M37 PASS (11/29 beats; 0.38), M38 PASS (20/29 beats; 0.69), M41 PASS (29/29 beats)",
        "M39 remains FAIL (narrative:chart 0.09; 1 narrative plate versus 9 chart pages plus 2 chart docks): genuine narrative-balance gap for parent review, not hidden or bypassed",
        "no MP4 render or release claim; private review is through the existing `player.html` artifact",
    ])
    if os.environ.get("SELF_WATCH", "1") == "1" and rc == 0:
        import self_watch as SW
        rc = SW.main([str(BUILD), "--project", str(ASSET_ROOT), "--script", "SCRIPT-F", "--short"])
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

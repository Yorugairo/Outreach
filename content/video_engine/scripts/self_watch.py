"""SELF-WATCH - the one-shot bar as a build artifact (P51 T3, 2026-09-11).

The operator's watch begins only when this file is clean (the grill of 2026-09-11: "we don't come close enough to a
first pass, then we spend a lot of time improving and iterating"). The runner is a pure function of the build: it runs
the numbers first - the layout probe (M25's input), the motion gate, the ONE-SHOT FLOOR (M35-M42, P56 T6), the
species-by-sentence lint, the viewer's and the script gates' last verdicts - then grabs the OPENING as contact sheets
(0:60 on a short, 3:00 on a long, at 2 s steps, 12 tiles a sheet) and the RECIPE AUDIT SHEETS (one per beat that
carries a proven recipe) and writes `<build>/SELF-WATCH.md`:

  section 1  the mechanical rows, every verdict filled by the tools (a FAIL here ends the report: NOT CLEAN)
  section 2  the eleven O-rows the AGENT fills by reading the sheets (Read on the PNGs, one sheet at a time) - the
             runner writes them as TODO with the tile list; it never fills a read it did not do
  section 3  ONE verdict line: `NOT CLEAN - <the first failing row>`, or `TODO - the agent reads the sheets and fills
             O1-O11`. CLEAN is the agent's word, written after the read; a build handed to the operator carries CLEAN.

The floor rides as one row per id (E96, P56: a cut under a floor is never offered for a watch), measured by ONE
subprocess of `gate_one_shot_floor.py` and parsed - the bar re-computes nothing, and a FAIL there reads
`NOT CLEAN - the one-shot floor (M3x): ...`. M40 (the parity table) is JUDGE and M42 (the rates) is INFO: they ride as
rows and never end the report; a floor gate that is missing or crashes is a WARN row naming it. The recipe audit sheet
is the critic's raw material, never a judge: `<build>/self-watch/recipes/<beat>-<recipe>.png`, this cut's frames at the
fire's member instants over the PROOF cut's frames at its own `members_at` - the proof build is read READ-ONLY through
`probe.Probe` and never rebuilt (`review-link-frozen-copy`); a proof cut that is not on disk WARNs and is named. The
doctrine page is `docs/content-video-engine/SELF-WATCH.md`.

The bar also writes the POSTING side of the build, since a cut nobody can post is not one-shot: `publish_package.py`
puts `<build>/publish/` on disk (the two descriptions, the pinned comment, the tags, the first frame, the checklist -
R26-8) and the folder rides section 1 as its own row. It never ends the watch: a package that cannot be written WARNs.

and `<build>/SELF-WATCH.html`, the operator's copy (gate 1's first read: "I'd have to see the video and have a better
writeup of what I'm looking for"): the same rows as one plain question each, what PASS and FAIL look like, the
agent's read, and the frame at every instant the read names - each frame a link to the served player at that
second. `--html` regenerates it from the .md after the agent has filled the rows (the tiles need the player).

    python content/video_engine/scripts/self_watch.py <build> --project <project dir> --script <report stem> [--long|--short] [--step 2] [--tile 360]
    python content/video_engine/scripts/self_watch.py <build> --html [--player-url http://127.0.0.1:8738/player.html]

Exit 1 when section 1 carries a FAIL (the report is still written), 0 otherwise. The checklist itself is the parent's
(SELF-WATCH-CHECKLIST, P51 T3); human gate 1 is the operator's first read of a real report.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint_species_choice as L  # noqa: E402
import gate_motion_density as G  # noqa: E402
import probe as P  # noqa: E402
import publish_package as PP  # noqa: E402
try:                                            # the floor's own loaders (the recipes, the beats, the walk) - P56 T6
    import gate_one_shot_floor as F  # noqa: E402
    import recipe_walk as RW  # noqa: E402
except Exception:                               # a checkout without the floor gate: the rows WARN, no sheet is drawn
    F = RW = None

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
GATE = HERE / "gate_motion_density.py"
FLOOR = HERE / "gate_one_shot_floor.py"           # the one-shot floor (M35-M42), run as a subprocess like the gate
FLOOR_ID_RE = re.compile(r"^M(?:3[5-9]|4[0-6])$")  # the ids the floor prints (M45/M46 since P66 T5); the M40 table lines are not rows
FLOOR_NAME = "the one-shot floor"                  # the section-1 row name, and what the verdict says
REPORT_NAME = "SELF-WATCH.md"
SHEET_DIR = "self-watch"
RECIPE_DIR = "recipes"                             # <build>/self-watch/recipes/<beat>-<recipe>.png (the audit sheets)
MAX_RECIPE_SHEETS = 24                             # sheets are frames: bounded, and the row says when it capped
FIRST_FRAME = "frame-0000.0.png"          # the 0:00 frame the publish package copies (R26-8); `*-0000.0.png` is its glob
LONG_FORM_S = 180.0                       # the script gates' route: a measured clock under 3:00 is a short
OPENING_S = {"short": 60.0, "long": 180.0}   # the operator: "the first 3 minutes on long format, first 60 seconds on shorts"
STEP_S, TILE_PX, PER_SHEET = 2.0, 360, 12
ROW_RE = re.compile(r"^\s*\[(PASS |FAIL |WARN |INFO |JUDGE)\]\s*(\S+)\s*(.*)$")
DETAIL_W = 420

# The O-rows (the checklist, verbatim): the agent's read of the sheets. The runner writes them as TODO.
O_ROWS = (
    ("O1", "the package is answered on sentence 1 (E24 / E27): the first frame and the first sentence deliver the title's claim"),
    ("O2", "the promise lands by 0:45 (G09; a short: the mechanism by 0:10)"),
    ("O3", "the first chart enters 0:08-0:20 lit (M11) and reads at a glance (E28: sign is geometry, the scale printed)"),
    ("O4", "every sentence-act with an available species has a row, or the bridge is deliberate (each `no row` line answered: bridge / the light holds / cut)"),
    ("O5", "no dead band: no 2 s tile pair identical to the eye inside the opening; nothing held still past its sentence (E21, E49)"),
    ("O6", "no overlap the probe could not see: a card over ink, a label under a card, paper in the strip (M25 read against the tiles)"),
    ("O7", "the citations readable at the phone scale (>= 11 CSS px; the source line clear of every card)"),
    ("O8", "the captions read as phrases, never chased (shorts: PHRASE captions; the strip never covers a figure; E62: under a card the caption keeps its size and MOVES to the free band - a shrink is a FAIL unless no band fits)"),
    ("O9", "every card lands on its word and leaves at the turn (E25 / E50): the landing tile and the exit tile named"),
    ("O10", "the chart is the world (E61): every plate row in the opening names its use; a plate that proves nothing and docks nothing is a bridge, said so"),
    ("O11", "the recipe fired as its proof does: the members in order, at their offsets - name the beat where it did not"),
)


# ---------------------------------------------------------------- the numbers
def parse_gate(text: str) -> dict:
    """The motion gate's rows and RESULT line -> {rows, fails, warns, m25, result, verdict}."""
    rows: list[dict] = []
    result = ""
    for line in text.splitlines():
        m = ROW_RE.match(line)
        if m:
            rows.append({"level": m.group(1).strip(), "id": m.group(2), "text": m.group(3).strip()})
        elif line.startswith("RESULT:"):
            result = line.strip()
    fails = [r for r in rows if r["level"] == "FAIL"]
    warns = [r for r in rows if r["level"] == "WARN"]
    m25 = next((r for r in rows if r["id"] == "M25"), None)
    return {"rows": rows, "fails": fails, "warns": warns, "m25": m25, "result": result,
            "verdict": "FAIL" if fails else ("WARN" if warns else ("PASS" if rows else "absent"))}


def run_gate(build: Path) -> dict:
    r = subprocess.run([sys.executable, str(GATE), str(build)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return parse_gate((r.stdout or "") + "\n" + (r.stderr or ""))


def run_floor(build: Path, project: Path | None = None) -> list[dict]:
    """The one-shot floor's rows (M35-M42), from ONE subprocess of `gate_one_shot_floor.py` - nothing re-computed.

    The gate prints `[LEVEL] M3x text` rows (plus M40's parity table and a `RESULT:` line, which `ROW_RE` ignores);
    a gate that is not on disk, dies, or prints no row is ONE WARN row naming it - the bar never crashes on it."""
    cmd = [sys.executable, str(FLOOR), str(build)] + (["--project", str(project)] if project else [])
    def missing(why: str) -> list[dict]:
        return [{"level": "WARN", "id": "M35-M42", "text": f"not measured - {why} ({FLOOR.name})"}]
    if not FLOOR.is_file():
        return missing("the floor gate is not on disk")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except Exception as e:                                   # no interpreter, no permission: say so, do not die
        return missing(f"the floor gate could not be run: {type(e).__name__}: {trim(str(e), 160)}")
    out = (r.stdout or "") + "\n" + (r.stderr or "")
    rows = [row for row in parse_gate(out)["rows"] if FLOOR_ID_RE.match(row["id"])]
    if not rows:
        last = next((l.strip() for l in reversed(out.splitlines()) if l.strip()), "no output")
        return missing(f"the floor gate printed no row (exit {r.returncode}): {trim(last, 200)}")
    return rows


def verdict_line(path: Path) -> str:
    """The LAST verdict line of a report (`VERDICT: PASS`, `**Verdict** ...`), `absent` when there is no file."""
    if not path.is_file():
        return "absent"
    lines = [l.strip() for l in path.read_text(encoding="utf-8", errors="replace").splitlines()]
    for l in reversed(lines):
        if re.match(r"^\W*verdict\b", l, re.I):
            return re.sub(r"\*+", "", l).strip("# ").strip()
    return "present, no verdict line"


def level_of(line: str) -> str:
    u = line.upper()
    if line == "absent":
        return "absent"
    for lv in ("FAIL", "WARN", "PASS"):
        if lv in u:
            return lv
    return "INFO"


def trim(s: str, w: int = DETAIL_W) -> str:
    s = " ".join(s.split())
    return s if len(s) <= w else s[:w - 1] + "…"


def cell(s: str) -> str:
    return s.replace("|", "\\|")


# ---------------------------------------------------------------- the sheets
def opening_instants(runtime_s: float, fmt: str, step: float) -> list[float]:
    end = min(OPENING_S[fmt], runtime_s)
    return [round(i * step, 2) for i in range(int(end / step + 1e-9))]


def opening_sheets(p: P.Probe, out_dir: Path, ts: list[float], tile: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("opening*.png"):
        old.unlink()
    return P.contact_sheet([(t, p.png(t)) for t in ts], out_dir / "opening.png", tile, PER_SHEET)


# ---------------------------------------------------------------- the recipe audit sheets (P56 T7, O11)
def beat_of(beats: list[dict], t: float) -> int:
    """The 1-based beat an instant lands in: the last beat that has started by then (a fire in a gap belongs to it)."""
    n = 0
    for i, b in enumerate(beats):
        if float(b["start"]) - 0.005 <= t:
            n = i + 1
        else:
            break
    return n


def proof_dir(proof: dict) -> Path | None:
    """The PROOF cut's build dir: the parent of `proof.timeline` (repo-relative), or None when it is not on disk."""
    rel = str((proof or {}).get("timeline") or "").replace("\\", "/")
    if not rel:
        return None
    path = Path(rel) if Path(rel).is_absolute() else REPO / rel
    return path.parent if path.is_file() else None


def recipe_shots(build: Path, project: Path | None = None, catalog: Path | None = None,
                 timeline_name: str | None = None, limit: int = MAX_RECIPE_SHEETS) -> tuple[list[dict], list[str]]:
    """One shot per (beat, proven recipe) this cut fires: the fire's member instants, and the proof cut's own.

    The fires are `recipe_walk.match` over this build's compiled timeline through the floor gate's loaders (the same
    catalogue, the same beats file) - one shot per recipe per beat the fire STARTS in. Returns (shots, misses): a
    recipe whose proof cut is not on disk is a miss, named, and draws no sheet (`review-link-frozen-copy`: the proof
    is read where it lies, never rebuilt)."""
    build = Path(build)
    if F is None or RW is None:
        return [], ["the floor gate is not importable - no recipe audit sheet was drawn"]
    try:
        tl_path = F.timeline_path(build, timeline_name)
        timeline = json.loads(tl_path.read_text(encoding="utf-8"))
        cat = Path(catalog or REPO / F.CATALOG_REL)
        recipes = {str(r.get("id")): r for r in F.load_recipes(cat)}
        beats = L.load_sentences(F.beats_path(build, timeline, project))
        fires = F.recipe_fires(RW.events(timeline, F.card_options(cat)), list(recipes.values()))
    except (Exception, SystemExit) as e:                     # a build mid-edit, a catalogue absent: say so, do not die
        return [], [f"the fires could not be walked: {type(e).__name__}: {trim(str(e), 200)}"]
    shots: list[dict] = []
    misses: list[str] = []
    seen: set[tuple] = set()
    for rid in sorted(fires):
        recipe = recipes[rid]
        proof = recipe.get("proof") or {}
        pdir = proof_dir(proof)
        proof_at = [float(t) for t in (proof.get("members_at") or []) if t is not None]
        if pdir is None or not proof_at:
            misses.append(f"{rid}: the proof cut is not on disk ({proof.get('timeline') or 'no proof timeline'})")
            continue
        slug = rid.split(":", 1)[-1]
        for fire in fires[rid]:
            beat = beat_of(beats, fire.t)
            key = (beat, rid)
            if key in seen:
                continue
            seen.add(key)
            shots.append({"key": key, "beat": beat, "recipe": rid, "slug": slug, "scene": fire.scene,
                          "t": fire.t, "at": [float(t) for t in fire.members_at if t is not None],
                          "proof_dir": pdir, "proof_name": f"{pdir.parent.name}/{pdir.name}",
                          "proof_at": proof_at, "png": f"beat{beat:02d}-{slug}.png"})
    shots.sort(key=lambda s: (s["beat"], s["recipe"]))
    if len(shots) > limit:
        misses.append(f"{len(shots)} (beat, recipe) pairs fire - the first {limit} are drawn (frames are bounded)")
        shots = shots[:limit]
    return shots, misses


def recipe_frames(probe, shots: list[dict], build: Path) -> tuple[dict, dict, list[str]]:
    """This cut's frames at every fire's member instants, in the session already open on this build.

    A recipe whose PROOF cut is this same build is grabbed here too: playwright's sync API allows one session per
    thread, so the proof cuts that live elsewhere are read afterwards by `proof_frames`."""
    here: dict = {}
    proof: dict = {}
    warns: list[str] = []
    build = Path(build).resolve()
    for s in shots:
        try:
            here[s["key"]] = [(t, probe.png(t)) for t in s["at"]]
            if Path(s["proof_dir"]).resolve() == build and s["recipe"] not in proof:
                proof[s["recipe"]] = [(t, probe.png(t)) for t in s["proof_at"]]
        except (Exception, SystemExit) as e:
            warns.append(f"{s['recipe']} at beat {s['beat']}: {type(e).__name__}: {trim(str(e), 160)}")
    return here, proof, warns


def proof_frames(shots: list[dict], have: dict | None = None, open_probe=None) -> tuple[dict, list[str]]:
    """{recipe id -> the PROOF cut's frames at its own `members_at`}: one READ-ONLY session per proof build.

    The proof build is served and read where it lies - never rebuilt, never re-compiled (`review-link-frozen-copy`).
    A proof cut that cannot be probed is a WARN naming it, never a crash."""
    out = dict(have or {})
    warns: list[str] = []
    opener = open_probe or (P.Probe if hasattr(P, "Probe") else None)
    by_dir: dict = {}
    for s in shots:
        if s["recipe"] in out:
            continue
        by_dir.setdefault(Path(s["proof_dir"]), {})[s["recipe"]] = s
    for pdir, group in sorted(by_dir.items()):
        try:
            with opener(pdir) as q:                          # served and read where it lies; never rebuilt
                for rid, s in sorted(group.items()):
                    out[rid] = [(t, q.png(t)) for t in s["proof_at"]]
        except (Exception, SystemExit) as e:
            warns.append(f"the proof cut {pdir.name} could not be read: {type(e).__name__}: {trim(str(e), 160)}")
    return out, warns


def recipe_sheet(top: list, bottom: list, out: Path, tile: int, head: str,
                 labels: tuple = ("this cut", "the proof")) -> Path | None:
    """One sheet, two labelled rows of frames (change_report's two-frames-at-an-instant layout, a row per cut)."""
    import io
    from PIL import Image, ImageDraw
    rows = [[(t, Image.open(io.BytesIO(b)).convert("RGB")) for t, b in r] for r in (top, bottom)]
    ims = [im for r in rows for _t, im in r]
    if not ims:
        return None
    th = max(round(tile * im.height / im.width) for im in ims)
    cols = max(len(r) for r in rows)
    head_h, pad = 26, 20
    sheet = Image.new("RGB", (cols * tile, head_h + len(rows) * (th + pad)), (13, 15, 18))
    d = ImageDraw.Draw(sheet)
    d.text((8, 7), head, fill=(220, 227, 234))
    for j, r in enumerate(rows):
        y = head_h + j * (th + pad)
        for i, (t, im) in enumerate(r):
            sheet.paste(im.resize((tile, th)), (i * tile, y + pad))
            label = f"{labels[j]} \u00b7 {t:.2f}s" if i == 0 else f"{t:.2f}s"
            d.text((i * tile + 8, y + 4), label, fill=(220, 227, 234))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, "PNG")
    return out


def write_recipe_sheets(build: Path, shots: list[dict], here: dict, proof: dict,
                        tile: int = TILE_PX) -> tuple[list[Path], list[str]]:
    """`<build>/self-watch/recipes/<beat>-<recipe>.png` per shot: this cut's members over the proof cut's own."""
    out_dir = Path(build) / SHEET_DIR / RECIPE_DIR
    paths: list[Path] = []
    warns: list[str] = []
    if not shots:
        return paths, warns
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.png"):
        old.unlink()
    for s in shots:
        top, bottom = here.get(s["key"]) or [], proof.get(s["recipe"]) or []
        if not top or not bottom:
            warns.append(f"{s['recipe']} at beat {s['beat']}: no frames for "
                         f"{'this cut' if not top else 'the proof cut ' + s['proof_name']}")
            continue
        head = (f"beat {s['beat']} ({s['t']:.2f}s, {s['scene'] or 'no scene'}) \u00b7 {s['recipe']} \u00b7 "
                f"this cut over {s['proof_name']} (the proof, read-only)")
        p = recipe_sheet(top, bottom, out_dir / s["png"], tile, head)
        if p is not None:
            paths.append(p)
    return paths, warns


def recipe_row(sheets: list[Path], shots: list[dict], warns: list[str]) -> tuple[str, str, str]:
    """The audit sheets as a section-1 row: INFO naming them (O11 is the agent's read), WARN when one is missing.

    It can never FAIL: the sheets are the critic's raw material, and no judge rides in this plan (E96)."""
    names = ", ".join(p.name for p in sheets)
    beats = sorted({s["beat"] for s in shots})
    detail = (f"{len(sheets)} sheet(s) in {SHEET_DIR}/{RECIPE_DIR}/ over {len(beats)} beat(s) carrying a recipe"
              f"{': ' + names if names else ''}") if sheets else "no sheet: no proven recipe fires in this cut"
    if warns:
        detail += " \u00b7 " + "; ".join(warns)
    return ("the recipe audit sheets (O11)", "WARN" if warns else "INFO", trim(detail, 1200))


# ---------------------------------------------------------------- the report
def section1(gate: dict, lint_lines: list[str], lint_counts: dict, viewer: str, sgates: str, fmt: str,
             floor: "list[dict] | tuple" = ()) -> list[tuple[str, str, str]]:
    """(row, verdict, detail) - every verdict filled by a tool. `floor` is `run_floor`'s rows, one row each."""
    g_detail = "; ".join(f"[{r['level']}] {r['id']} {trim(r['text'], 200)}" for r in gate["fails"] + gate["warns"]) or "no FAIL, no WARN"
    rows = [("motion gate (M01-M24)", gate["verdict"], trim(g_detail + " · " + gate["result"], 900))]
    m25 = gate["m25"]
    rows.append(("M25 layout", m25["level"] if m25 else "absent", trim(m25["text"], 600) if m25 else "the gate printed no M25 row"))
    no_row = [l for l in lint_lines if l.endswith("· no row")]
    counts = (f"{lint_counts['sentences']} sentences · {lint_counts['with_act']} carry an act · {lint_counts['with_row']} have a row firing"
              f" · {lint_counts['no_row']} have an available species and no row")
    rows.append(("species by sentence", "INFO", trim(counts + (" · " + " ‖ ".join(trim(l[5:], 160) for l in no_row) if no_row else ""), 1400)))
    if fmt == "long":
        warns = [l for l in lint_lines if l.startswith("WARN")]
        rows.append(("E61 plates (long)", "WARN" if warns else "PASS",
                     trim(" ‖ ".join(trim(l[5:], 160) for l in warns) if warns else f"{lint_counts.get('plates', 0)} plate row(s), every one names its use", 900)))
    else:
        rows.append(("E61 plates (long only)", "n/a", "a short"))
    rows.append(("the viewer (P36)", level_of(viewer), trim(viewer)))
    rows.append(("the script gates", level_of(sgates), trim(sgates)))
    # the one-shot floor (E96, P56 T6): one row per id, the gate's own level - M40 JUDGE and M42 INFO ride, they never end it
    rows += [(f"{FLOOR_NAME} ({r['id']})", r["level"], trim(r["text"], 900)) for r in floor]
    return rows


def publish_row(build: Path, project: Path) -> tuple[str, str, str]:
    """The posting side of the one-shot bar (R26-8): write `<build>/publish/` from the build's own artifacts and report
    the folder as a section-1 row. A package that cannot be written WARNs and names the reason - the watch is the cut,
    so a missing description never says NOT CLEAN."""
    try:
        out = PP.write_package(build, project)
        names = ", ".join(sorted(p.name for p in out.iterdir()))
        missing = json.loads((out / "MANIFEST.json").read_text(encoding="utf-8"))["missing"]
        level = "WARN" if missing else "PASS"
        detail = f"{out.name}/: {names}" + (" · not on disk: " + "; ".join(missing) if missing else "")
        return ("the publish package (R26-8)", level, trim(detail, 900))
    except Exception as e:                                  # a build with no timeline, a dossier mid-edit: say so, do not die
        return ("the publish package (R26-8)", "WARN", f"not written: {type(e).__name__}: {trim(str(e), 240)}")


def floor_id(name: str) -> str:
    """`the one-shot floor (M37)` -> `M37` (the row name carries the id, so the verdict can name it)."""
    m = re.search(r"\(([^)]+)\)\s*$", name)
    return m.group(1) if m else name


def verdict(rows: list[tuple[str, str, str]]) -> str:
    """ONE line: the FIRST failing section-1 row, or TODO. A floor FAIL names its id and lists the others after it."""
    bad = next(((name, detail) for name, lv, detail in rows if lv == "FAIL"), None)
    if bad:
        line = f"NOT CLEAN - {bad[0]}: {trim(bad[1], 240)}"
        if bad[0].startswith(FLOOR_NAME):
            others = [floor_id(n) for n, lv, _d in rows if lv == "FAIL" and n.startswith(FLOOR_NAME) and n != bad[0]]
            if others:
                line += " \u00b7 also under the floor: " + ", ".join(others)
        return line
    return "TODO - the agent reads the sheets and fills O1-O11; CLEAN is written after the read"


def render(build: Path, project: Path, stem: str, fmt: str, sha: str, tl_name: str, runtime_s: float, aspect: str,
           rows: list[tuple[str, str, str]], sheets: list[Path], ts: list[float], date: str) -> str:
    m, s = divmod(int(round(runtime_s)), 60)
    out = [f"# SELF-WATCH - {project.name} - {build.name} - {date} - {fmt} ({OPENING_S[fmt] / 60:g} min opening)",
           f"player.html sha256 {sha} - timeline {tl_name} - runtime {m}:{s:02d} - aspect {aspect} - script {stem}",
           "",
           "## 1. The gates (mechanical - a FAIL here ends the report)",
           "",
           "| row | verdict | detail |", "|---|---|---|"]
    out += [f"| {cell(n)} | {lv} | {cell(d)} |" for n, lv, d in rows]
    names = ", ".join(p.name for p in sheets)
    out += ["",
            "## 2. The opening, read (the agent fills these by reading the sheets - never by the gates alone)",
            "",
            f"sheets: {SHEET_DIR}/ {names} ({len(ts)} tiles at {STEP_S:g} s steps from 0:00 to {int(ts[-1] // 60)}:{int(ts[-1] % 60):02d}, {TILE_PX} px, {PER_SHEET} per sheet)",
            "",
            f"the operator's copy: {HTML_NAME} - one plain question per row, the frames at the instants named here, each a link to the served player (`--html` after the read)",
            "",
            "| # | check | verdict | evidence (t, what the tile shows) |", "|---|---|---|---|"]
    out += [f"| {k} | {cell(text)} | TODO | {cell(names)} |" for k, text in O_ROWS]
    out += ["", "## 3. Verdict", "", verdict(rows), ""]
    return "\n".join(out)


# ---------------------------------------------------------------- the HTML (the operator's copy)
HTML_NAME = "SELF-WATCH.html"
TILE_W = {"9:16": 220, "16:9": 320}

# The plain question each O-row asks a VIEWER, and what PASS and FAIL look like on the tiles. Gate 1's first read
# (the operator, 2026-09-11): "I can't really tell by reading how to pass/fail the video, I'd have to see the video
# and have a better writeup of what I'm looking for." The rule stays in O_ROWS; this is the same row in the words a
# person uses while watching.
PLAIN = {
    "O1": ("Do the first frame and the first sentence deliver what the title promised?",
           "you could say the title back from the first two seconds",
           "the opening is a mood; the title's claim arrives later"),
    "O2": ("By 0:10 on a short (0:45 on a long) do you know what the video is going to show you?",
           "the mechanism is said and on screen by then",
           "still setting the scene"),
    "O3": ("When the first chart appears, can you read it in one look: what is measured, the unit, which way is bad?",
           "the title, the unit on the axis and the direction of the move are obvious without searching",
           "a bare line, a scale you have to hunt for, a drop that goes sideways"),
    "O4": ("Does each sentence that names a number, a rank, a comparison or a turn get a move on screen, or does the screen just hold?",
           "the move lands on the word that names it; a hold is a decision, said so",
           "the words move and the screen does not"),
    "O5": ("Is there any two-second stretch where nothing changes but the caption?",
           "no two tiles you could not tell apart",
           "a held frame you could screenshot twice"),
    "O6": ("Does anything sit on top of something you are meant to read: a card over the line, a label under a card, paper in the caption strip?",
           "nothing covered at any tile",
           "a covered figure, a covered line, a label you cannot read"),
    "O7": ("Can you read the source line and the small labels at phone size?",
           "legible without zooming on the phone-scale tile",
           "you squint"),
    "O8": ("Do the captions read as whole phrases at ONE size and weight the whole way through, and stay off the figures?",
           "two to four words a page, the same punch everywhere; under a card the caption MOVES to the free band (E62)",
           "a caption that shrinks under a card, or a caption sitting on a number"),
    "O9": ("Does every card arrive on the word that names it and leave when the sentence turns?",
           "you can name the word each card lands on and the word it leaves on",
           "a card early, late, or lingering after its sentence"),
    "O10": ("Is the chart the world? When a picture is on screen instead, is it clearly a landing, a bridge or a reset?",
            "every picture has a job you can name",
            "a picture that proves nothing and docks nothing"),
    "O11": ("On each recipe sheet, does the top row (this cut) do what the bottom row (the proof) does: the same "
            "members, in order, at the same offsets?",
            "the two rows read as the same move, beat by beat",
            "a member missing, out of order, or arriving so late the combination reads as two unrelated things"),
}

# The instants an evidence cell names: `t=38`, `t=24-32`, `t=57.5 and 57.65`, `0:39-0:45`, `(9.1)`, `(48-50)`, a bare
# decimal `25.6` that is not a size (`11.6 CSS px`), a share (`36.6%`) or a duration (`7.6 s`).
_N = r"\d+(?:\.\d+)?"
_MS = r"\d+:\d\d"
T_FORMS = (
    re.compile(rf"\bt\s*=\s*(?P<a>{_N})(?:\s*(?:-|–|to|and)\s*(?P<b>{_N}))?"),
    re.compile(rf"(?<![\w:.])(?P<a>{_MS})(?:\s*-\s*(?P<b>{_MS}))?(?![\d:])"),
    re.compile(rf"\((?P<a>{_N})(?:\s*-\s*(?P<b>{_N}))?\)"),
    re.compile(rf"(?<![\w.:-])(?P<a>\d+\.\d+)(?!\d)(?:\s*-\s*(?P<b>\d+\.\d+)(?!\d))?(?!\s*(?:%|px|css|s\b|x\b|-|\.\d))", re.I),
)
TILES_PER_ROW = 8


def _sec(s: str) -> float:
    if ":" in s:
        m, ss = s.split(":")
        return int(m) * 60 + float(ss)
    return float(s)


def instants_in(text: str, runtime_s: float, cap: int = TILES_PER_ROW) -> list[float]:
    """The instants an O-row's evidence names, on a 0.5 s grid inside the runtime, at most `cap` spread evenly."""
    pts: list[float] = []
    for rx in T_FORMS:
        for m in rx.finditer(text):
            a = _sec(m.group("a"))
            if m.group("b"):
                b = _sec(m.group("b"))
                pts += [a, b] + ([(a + b) / 2] if b - a > 6 else [])
            else:
                pts.append(a)
    ok = sorted({round(t * 2) / 2 for t in pts if 0 <= t <= runtime_s})
    if len(ok) > cap:
        ok = [ok[round(i * (len(ok) - 1) / (cap - 1))] for i in range(cap)]
    return ok


def _cells(line: str) -> list[str]:
    parts = re.split(r"(?<!\\)\|", line.strip())
    return [c.strip().replace("\\|", "|") for c in parts[1:-1]]


def parse_report(md: str) -> dict:
    """SELF-WATCH.md -> {title, meta, gates: [(row, level, detail)], sheets: [names], o_rows: [(k, check, level,
    evidence)], verdict, notes: [lines]} - the .md the agent filled is the source; the HTML is a view of it."""
    lines = md.splitlines()
    out = {"title": (lines[0] if lines else "").lstrip("# ").strip(), "meta": lines[1].strip() if len(lines) > 1 else "",
           "gates": [], "sheets": [], "o_rows": [], "verdict": "", "notes": []}
    sec = 0
    for l in lines[2:]:
        if l.startswith("## "):
            sec = int(l[3]) if l[3].isdigit() else 0
            continue
        if sec in (1, 2) and l.startswith("|") and not l.startswith("|---"):
            c = _cells(l)
            if sec == 1 and len(c) == 3 and c[0] != "row":
                out["gates"].append(tuple(c))
            elif sec == 2 and len(c) == 4 and c[0] != "#":
                out["o_rows"].append(tuple(c))
        elif sec == 2 and l.startswith("sheets:"):
            m = re.search(r"sheets:\s*(\S+)/\s*(.*?)\s*\(", l)
            out["sheets"] = [n.strip() for n in (m.group(2) if m else "").split(",") if n.strip()]
        elif sec == 3 and l.strip():
            if out["verdict"]:
                out["notes"].append(l.strip())
            else:
                out["verdict"] = l.strip()
    return out


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _mmss(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:04.1f}"


def _data_uri(png: bytes) -> str:
    import base64
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


def _tile_png(png: bytes, width: int) -> bytes:
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGB")
    im = im.resize((width, max(1, round(width * im.height / im.width))))
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def row_tiles(p, build: Path, k: str, ts: list[float], width: int) -> list[tuple[float, Path]]:
    """The frame at each instant an O-row names, `width` px wide, written beside the sheets as <k>-<t>.png."""
    out_dir = build / SHEET_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob(f"{k}-*.png"):
        old.unlink()
    paths = []
    for t in ts:
        path = out_dir / f"{k}-{t:06.1f}.png"
        path.write_bytes(_tile_png(p.png(t), width))
        paths.append((t, path))
    return paths


def _level_class(lv: str) -> str:
    u = lv.upper()
    for x in ("PASS", "WARN", "FAIL", "INFO", "JUDGE", "TODO"):
        if x in u:
            return x
    return "INFO"


HTML_CSS = """
body{margin:0;background:#0d0f12;color:#dce3ea;font:15px/1.45 system-ui,'Segoe UI',Roboto,sans-serif}
main{max-width:1500px;margin:0 auto;padding:24px 28px 60px}
h1{font-size:22px;margin:0 0 4px} h2{font-size:18px;margin:34px 0 10px;color:#aab4bf}
.meta,.mono{color:#8a97a5;font-family:ui-monospace,Consolas,monospace;font-size:13px}
.verdict{margin:18px 0 22px;padding:14px 18px;border-radius:8px;font-size:18px;font-weight:700}
.verdict.FAIL{background:#3a1216;color:#ffb3b8;border:1px solid #7a2a30}
.verdict.TODO{background:#3a2e10;color:#ffd98a;border:1px solid #7a6020}
.verdict.CLEAN{background:#10331a;color:#a8f0b8;border:1px solid #2a7a40}
.verdict .note{color:#c5ccd4;font-size:13px;margin-top:6px;font-weight:400}
.how{color:#aab4bf;font-size:14px;margin:0 0 8px;max-width:1100px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid #232830} th{color:#8a97a5;font-weight:600}
.lv{display:inline-block;padding:2px 8px;border-radius:4px;font-family:ui-monospace,Consolas,monospace;font-size:12px;font-weight:700;white-space:nowrap}
.lv.PASS{background:#153a22;color:#8fe3a6} .lv.WARN{background:#3d3210;color:#ffd57a} .lv.FAIL{background:#3d1216;color:#ff9ea5}
.lv.INFO,.lv.TODO{background:#20262e;color:#aab4bf} .lv.JUDGE{background:#2a2040;color:#cdb8ff}
.row{margin:22px 0;padding:18px 20px;border:1px solid #232830;border-radius:10px;background:#12151a}
.row h3{margin:0 0 8px;font-size:17px;line-height:1.35} .row h3 .k{color:#8a97a5;font-family:ui-monospace,Consolas,monospace;margin-right:10px;font-size:14px}
.looks{color:#aab4bf;font-size:14px;margin:0 0 6px} .looks b{color:#dce3ea}
.rule{color:#6f7c8a;font-size:13px;margin:0 0 10px}
.ev{margin:8px 0 12px;font-size:14px;max-width:1200px}
.tiles{display:flex;flex-wrap:wrap;gap:10px} .tile{display:block;text-decoration:none;color:#dce3ea}
.tile img{display:block;border-radius:6px;border:1px solid #2a3038} .tile:hover img{border-color:#8fb4ff}
.tile .t{font-family:ui-monospace,Consolas,monospace;font-size:12px;color:#8a97a5;margin:4px 0 0}
.sheets img{max-width:100%;display:block;margin:10px 0;border-radius:6px}
a{color:#8fb4ff}
"""


# A tile's click opens the player in one named window and seeks it from here once its scrub exists (same origin): the
# split player also seeks itself from `?t=`; the single-file player (a watched build, never rebuilt under review) has no
# URL seek, so the report does it.
SEEK_JS = """
document.querySelectorAll('a.tile').forEach(a => a.addEventListener('click', ev => {
  ev.preventDefault();
  const t = parseFloat(a.dataset.t), w = window.open(a.href, 'mp-player');
  const seek = () => { try { const s = w.document.getElementById('scrub');
    if (s && w.document.readyState === 'complete') { s.value = t; s.dispatchEvent(new w.Event('input', {bubbles: true})); return true; } }
    catch (e) {} return false; };
  let n = 0; const id = setInterval(() => { if (seek() || ++n > 240) clearInterval(id); }, 250);
}));
"""


def write_html(build: Path, p=None, player_url: str = "player.html", tile: int | None = None,
               runtime_s: float | None = None) -> Path:
    """`<build>/SELF-WATCH.html` from the .md as it stands: the verdict first, the gates table, then each O-row as
    the plain question with what PASS and FAIL look like, the agent's verdict and evidence, and the frame at every
    instant the evidence names - each frame a link to `<player_url>?t=<s>` so the operator clicks and watches the
    beat. Images are inlined (one file, sendable). With no probe the rows carry no tiles (the runner's first pass:
    every row is TODO and names no instant)."""
    md_path = build / REPORT_NAME
    rep = parse_report(md_path.read_text(encoding="utf-8"))
    words = json.loads((build / "timeline.json").read_text(encoding="utf-8"))
    runtime_s = float(runtime_s or words.get("runtime_s") or 0.0)
    aspect = p.aspect if p is not None else str(json.loads(G._timeline_path(build, None).read_text(encoding="utf-8")).get("aspect") or "16:9")
    tile = tile or TILE_W.get(aspect, 320)
    v = rep["verdict"]
    vcls = "FAIL" if v.startswith("NOT CLEAN") else ("CLEAN" if v.startswith("CLEAN") else "TODO")
    h = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{_esc(rep['title'])}</title>",
         f"<style>{HTML_CSS}</style></head><body><main>",
         f"<h1>{_esc(rep['title'])}</h1><div class='meta'>{_esc(rep['meta'])}</div>",
         f"<div class='verdict {vcls}'>{_esc(v)}" + "".join(f"<div class='note'>{_esc(n)}</div>" for n in rep["notes"]) + "</div>",
         "<p class='how'>How to read this: section 1 is the tools' verdicts (a FAIL there ends it). Each row below is one question "
         "a viewer can answer; under it, what a PASS and a FAIL look like, then the agent's read and the frame at every instant it "
         "names. Click a frame to open the player at that second (serve the build first: "
         "<span class='mono'>python content/video_engine/scripts/serve_player.py &lt;build&gt; --port &lt;port&gt;</span>). "
         "The whole opening at 2 s steps is at the bottom.</p>",
         "<h2>1. The gates (mechanical)</h2><table><tr><th>row</th><th>verdict</th><th>detail</th></tr>"]
    h += [f"<tr><td>{_esc(r)}</td><td><span class='lv {_level_class(lv)}'>{_esc(lv)}</span></td><td>{_esc(d)}</td></tr>" for r, lv, d in rep["gates"]]
    h.append("</table><h2>2. The opening, read</h2>")
    for k, check, lv, ev in rep["o_rows"]:
        q, ok, bad = PLAIN.get(k, (check, "", ""))
        ts = instants_in(ev, runtime_s) if lv.upper() != "TODO" else []
        tiles = row_tiles(p, build, k, ts, tile) if (p is not None and ts) else []
        h.append(f"<section class='row' id='{k}'><h3><span class='k'>{k}</span>{_esc(q)} <span class='lv {_level_class(lv)}'>{_esc(lv)}</span></h3>")
        if ok or bad:
            h.append(f"<p class='looks'><b>PASS looks like:</b> {_esc(ok)}. <b>FAIL looks like:</b> {_esc(bad)}.</p>")
        h.append(f"<p class='rule'>the rule: {_esc(check)}</p><p class='ev'>{_esc(ev)}</p>")
        if tiles:
            h.append("<div class='tiles'>")
            for t, path in tiles:
                h.append(f"<a class='tile' href='{_esc(player_url)}?t={t:g}' data-t='{t:g}' target='_blank' title='open the player at {_mmss(t)}'>"
                         f"<img src='{_data_uri(path.read_bytes())}' width='{tile}' alt='{k} at {t:g}s'><div class='t'>{_mmss(t)} · watch</div></a>")
            h.append("</div>")
        elif ts:
            h.append("<p class='mono'>instants named: " + ", ".join(_mmss(t) for t in ts) + " (run with --html to grab the frames)</p>")
        h.append("</section>")
    sheets = [build / SHEET_DIR / n for n in rep["sheets"]]
    h.append("<h2>3. The opening at 2 s steps</h2><div class='sheets'>")
    h += [f"<img src='{_data_uri(s.read_bytes())}' alt='{_esc(s.name)}'>" for s in sheets if s.is_file()]
    h.append(f"</div></main><script>{SEEK_JS}</script></body></html>")
    out = build / HTML_NAME
    out.write_text("\n".join(h), encoding="utf-8")
    return out


# ---------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("build", type=Path)
    ap.add_argument("--project", type=Path, help="the episode dir (SHOT-TABLE-SHORT.py, the script reports)")
    ap.add_argument("--script", help="the script report stem: <stem>-VIEWER.md and <stem>-GATES.md in the project dir")
    ap.add_argument("--html", action="store_true", help="only regenerate SELF-WATCH.html from the filled SELF-WATCH.md (grabs the frames the rows name)")
    ap.add_argument("--player-url", default="player.html", help="the served player the tiles link to (default: relative, for a report served from the build)")
    ap.add_argument("--long", action="store_true")
    ap.add_argument("--short", action="store_true")
    ap.add_argument("--step", type=float, default=STEP_S)
    ap.add_argument("--tile", type=int, default=TILE_PX)
    ap.add_argument("--timeline", default=None, help="the compiled timeline's file name inside the build")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    build = args.build.resolve()
    if args.html:
        if not (build / REPORT_NAME).is_file():
            raise SystemExit(f"no {REPORT_NAME} in {build} - run the bar first")
        with P.Probe(build, args.timeline) as p:
            out = write_html(build, p, args.player_url)
        print(out)
        return 0
    if not (args.project and args.script):
        ap.error("--project and --script are required (or --html)")
    project = args.project.resolve()
    words = json.loads((build / "timeline.json").read_text(encoding="utf-8"))
    runtime_s = float(words.get("runtime_s") or 0.0)
    fmt = "long" if args.long else ("short" if args.short or runtime_s < LONG_FORM_S else "long")
    ts = opening_instants(runtime_s, fmt, args.step)
    shots, r_warns = recipe_shots(build, project, timeline_name=args.timeline)   # the fires, before any browser
    with P.Probe(build, args.timeline) as p:
        P.write_gate(build, args.timeline, probe=p)                       # M25's input, keyed to this player
        sheets = opening_sheets(p, build / SHEET_DIR, ts, args.tile)
        # the frame at 0:00 at full stage size: the publish package's `first-frame.png` (R26-8 - what a platform picks
        # on its own when nobody uploads a thumbnail), and the tile O1 is read against
        (build / SHEET_DIR / FIRST_FRAME).write_bytes(p.png(0.0))
        here, proof, w = recipe_frames(p, shots, build)                   # this cut's member frames, in this session
        r_warns += w
        sha, tl_name, aspect = hashlib.sha256(p.html.read_bytes()).hexdigest()[:12], p.tl_path.name, p.aspect
    proof, w = proof_frames(shots, proof)          # the proof cuts, one read-only session each, after this build's
    r_warns += w
    r_sheets, w = write_recipe_sheets(build, shots, here, proof, args.tile)
    r_warns += w
    gate = run_gate(build)
    floor = run_floor(build, project)              # ONE subprocess of the floor gate; its rows are parsed, not redone
    lint_lines, lint_counts = L.report(project, build=str(build), long=(fmt == "long"))   # the full path: a nested private build (the recipe lab's build-lab-*/<id>/) resolves as it stands (lint_species_choice.build_dir)
    viewer = verdict_line(project / f"{args.script}-VIEWER.md")
    sgates = verdict_line(project / f"{args.script}-GATES.md")
    rows = section1(gate, lint_lines, lint_counts, viewer, sgates, fmt, floor)
    rows.append(recipe_row(r_sheets, shots, r_warns))   # the audit sheets: O11's material, never a gate
    rows.append(publish_row(build, project))       # the posting side rides last: it reads the build, it never gates it
    text = render(build, project, args.script, fmt, sha, tl_name, runtime_s, aspect, rows, sheets, ts,
                  _dt.date.today().isoformat())
    (build / REPORT_NAME).write_text(text, encoding="utf-8")
    write_html(build, None, args.player_url)                                # the operator's copy, TODO rows, the sheets inline
    print(f"{build / REPORT_NAME}")
    for n, lv, d in rows:
        print(f"  {lv:6s} {n}: {trim(d, 160)}")
    print(f"  {verdict(rows)}")
    return 1 if verdict(rows).startswith("NOT CLEAN") else 0


if __name__ == "__main__":
    raise SystemExit(main())

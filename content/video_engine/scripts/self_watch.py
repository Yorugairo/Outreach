"""SELF-WATCH - the one-shot bar as a build artifact (P51 T3, 2026-09-11).

The operator's watch begins only when this file is clean (the grill of 2026-09-11: "we don't come close enough to a
first pass, then we spend a lot of time improving and iterating"). The runner is a pure function of the build: it runs
the numbers first - the layout probe (M25's input), the motion gate, the species-by-sentence lint, the viewer's and the
script gates' last verdicts - then grabs the OPENING as contact sheets (0:60 on a short, 3:00 on a long, at 2 s steps,
12 tiles a sheet) and writes `<build>/SELF-WATCH.md`:

  section 1  the mechanical rows, every verdict filled by the tools (a FAIL here ends the report: NOT CLEAN)
  section 2  the ten O-rows the AGENT fills by reading the sheets (Read on the PNGs, one sheet at a time) - the runner
             writes them as TODO with the tile list; it never fills a read it did not do
  section 3  ONE verdict line: `NOT CLEAN - <the first failing row>`, or `TODO - the agent reads the sheets and fills
             O1-O10`. CLEAN is the agent's word, written after the read; a build handed to the operator carries CLEAN.

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

HERE = Path(__file__).resolve().parent
GATE = HERE / "gate_motion_density.py"
REPORT_NAME = "SELF-WATCH.md"
SHEET_DIR = "self-watch"
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


# ---------------------------------------------------------------- the report
def section1(gate: dict, lint_lines: list[str], lint_counts: dict, viewer: str, sgates: str, fmt: str) -> list[tuple[str, str, str]]:
    """(row, verdict, detail) - every verdict filled by a tool."""
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
    return rows


def verdict(rows: list[tuple[str, str, str]]) -> str:
    bad = next(((name, detail) for name, lv, detail in rows if lv == "FAIL"), None)
    if bad:
        return f"NOT CLEAN - {bad[0]}: {trim(bad[1], 240)}"
    return "TODO - the agent reads the sheets and fills O1-O10; CLEAN is written after the read"


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
    with P.Probe(build, args.timeline) as p:
        P.write_gate(build, args.timeline, probe=p)                       # M25's input, keyed to this player
        sheets = opening_sheets(p, build / SHEET_DIR, ts, args.tile)
        sha, tl_name, aspect = hashlib.sha256(p.html.read_bytes()).hexdigest()[:12], p.tl_path.name, p.aspect
    gate = run_gate(build)
    lint_lines, lint_counts = L.report(project, build=build.name, long=(fmt == "long"))
    viewer = verdict_line(project / f"{args.script}-VIEWER.md")
    sgates = verdict_line(project / f"{args.script}-GATES.md")
    rows = section1(gate, lint_lines, lint_counts, viewer, sgates, fmt)
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

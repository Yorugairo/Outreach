"""The viewer's windows: a script cut into blind 15-second reads (PRP P36 T1).

The viewer is the third role beside the gates and the judge: an agent that
knows NOTHING - no doctrine, no ledger, no tags - and reads the script cold,
one window at a time, carrying only the previous two windows as memory. This
module cuts those windows. It never judges and it never calls a model.

Two rules the cut exists to keep:

* **Word boundaries.** A word belongs to the window its ``start`` falls in, so
  no word is ever split across two reads. On a recorded take the boundaries are
  the take's own word times (``audit_script_doctrine.load_timings`` or a
  ``--timeline`` build file); before a take they are estimated from the kit's
  speech rate (``kit_spec.CHARS_PER_SEC``) over the spoken characters, and the
  output says which (``timing_source``).
* **No doctrine leaks.** What the viewer sees is SPOKEN TEXT ONLY:
  ``beat_tags.strip_marks`` removes every structural tag and delivery mark, and
  page furniture (headings, table rules, fences) is dropped with it. If the
  viewer can see the tags the test is void (P36 "Not Building").
* **The screens, when the build is on disk** (R26-0, ruling E43: on a short the
  chart carries the number, and a reader of words alone cannot see it). Each
  window ends in one ``[screen]`` line per screen that is up during it: what
  kind of thing it is, its title, and the figures it shows - a page's own
  labels and values, plus every number or phrase the engine paints on it inside
  that window. The screens come from the BUILD: the scene-evidence
  ``*.timeline.json`` beside the ``--timeline`` word file, or ``--screens``.
  Nothing doctrinal travels with them - no species names, no ``judge`` block,
  no beat tags. ``<script>-SCREENS.md`` is NOT a source: it is the
  strength-screen enumeration (the declared beat tags and the craft screens),
  and folding it in would hand the reader exactly what P36 keeps from it.

    python viewer_windows.py <script.txt> [--timeline build-f/timeline.json]
                             [--screens <build dir | scene timeline>]
                             [--no-screens] [--window 15] [--memory 2]
                             [--out <path>]

Writes ``<script>-VIEWER-WINDOWS.json`` beside the script - the ``-VO`` stem
suffix dropped exactly as ``run_script_gates.report_path`` drops it - in the
``viewer_windows.v1`` shape the runner and the scorer bind to:

    {schema_version, script, window_s, memory_windows, timing_source,
     screens_source, runtime_s,
     windows: [{i, start_s, end_s, span, text, memory,
                screens: [{kind, title, figures}]}]}

Pure and deterministic: same script + same timings -> byte-identical JSON.
Exit 0 on success, 2 when the script holds no spoken words.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_script_doctrine as A          # noqa: E402
import beat_tags                            # noqa: E402
import kit_spec                             # noqa: E402

# P36 click 2026-09-03; doc 31 retention clock (new information every 15-30s).
WINDOW_S = 15.0
# P36 click 2026-09-03: rolling memory - "that makes us have to argue it if
# we're really going 30 seconds without value" (2 x 15s).
MEMORY_WINDOWS = 2
SCHEMA_VERSION = "viewer_windows.v1"
# CHECK-RESPONSIBILITIES s5 naming rule, as run_script_gates.report_path applies it.
VO_SUFFIX = "-VO"
WINDOWS_SUFFIX = "-VIEWER-WINDOWS.json"
# kit_spec s: the speech rate the whole engine estimates with (16.29 chars/sec).
CHARS_PER_SEC = kit_spec.CHARS_PER_SEC
ROUND_S = 3          # seconds are rounded here so the JSON is byte-stable
TOKEN_RE = re.compile(r"\S+")

# ---- the screens (R26-0, ruling E43) --------------------------------------
# The line that carries what is ON SCREEN into the blind read. One per screen.
SCREEN_PREFIX = "[screen]"
# A build's scene-evidence timeline: `<episode>.timeline.json` beside the word
# `timeline.json` (which carries word times only and no screens).
SCENE_TIMELINE_GLOB = "*.timeline.json"
# How a screen is named to someone who has never heard of our species: plain
# nouns. The engine's own word for the thing (`deck`, `record`, `chart`) is a
# key here and never reaches the reader.
KIND_WORDS = {"chart": "a chart", "record": "a news clipping", "deck": "a picture",
              "photo": "a picture", "still": "a picture", "page": "a page"}
# A ledger page in this engine IS the chart it draws (doc 29 world plate).
PAGE_KIND = "a chart"
# The keys a species paints as WORDS on the page - the figure's text, the
# bracket's label and sub, the callout's label, the note, the retitle.
SPECIES_TEXT_KEYS = ("text", "label", "sub")
FIGURE_LIMIT = 12    # the line stays readable; the window's own clock picks which


# ---- naming and formatting ----------------------------------------------

def windows_path(script: Path) -> Path:
    """`<script>-VIEWER-WINDOWS.json` beside the script (report_path's rule)."""
    return script.with_name(script.stem.replace(VO_SUFFIX, "") + WINDOWS_SUFFIX)


def mmss(seconds: float) -> str:
    """m:ss - the clock every gate report prints."""
    total = int(seconds)
    return f"{total // 60}:{total % 60:02d}"


def spoken(text: str) -> str:
    """What the viewer may see: no tags, no marks, no page furniture.

    `audit_script_doctrine.spoken` is that rule (it calls
    `beat_tags.strip_marks` first); one definition, not two.
    """
    return A.spoken(text)


# ---- the screens the viewer can see -------------------------------------

def is_scene_timeline(path: Path) -> bool:
    """True for a scene-evidence timeline (it has `scenes`), false for anything else."""
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(doc, dict) and bool(doc.get("scenes"))


def scene_timeline_path(source: Path | str | None) -> Path | None:
    """The build's SCENE timeline, from a file, a build directory, or a word timeline.

    `--timeline build-x/timeline.json` names the word times; the screens sit
    beside it in `<episode>.timeline.json`. Deterministic: sorted by name, and
    the first file that actually holds scenes wins.
    """
    if source is None:
        return None
    p = Path(source)
    folder = p if p.is_dir() else p.parent
    for cand in ([p] if p.is_file() else []) + sorted(folder.glob(SCENE_TIMELINE_GLOB)):
        if is_scene_timeline(cand):
            return cand
    return None


def clean_screen_text(text: object) -> str:
    """Any screen text, marks stripped - a title must not smuggle a tag either."""
    return " ".join(beat_tags.strip_marks(str(text or "")).split()).strip()


def page_figures(page: dict) -> list[str]:
    """The figures a page shows standing: its axis labels, its values, its series.

    Read only from what is DRAWN (`labels`, `value_strings`/`values`, each
    series' own label). The page's `judge` block and its badges are ours, not
    the viewer's, and stay behind.
    """
    out = [clean_screen_text(x) for x in (page.get("labels") or [])]
    strings = page.get("value_strings") or []
    out += [clean_screen_text(x) for x in (strings or page.get("values") or [])]
    out += [clean_screen_text(sr.get("label")) for sr in (page.get("series") or [])
            if isinstance(sr, dict)]
    return [x for x in dict.fromkeys(out) if x]


def record_text(record: dict) -> str:
    """The clipping's own words - the line it holds up, as printed."""
    words = " ".join(clean_screen_text(w[0]) for w in (record.get("words") or [])
                     if isinstance(w, (list, tuple)) and w)
    return clean_screen_text(words)


def species_text(spec: dict) -> str:
    """What one species paints as words, or "" when it paints none."""
    parts = [clean_screen_text(spec.get(k)) for k in SPECIES_TEXT_KEYS]
    return " ".join(x for x in parts if x).strip()


def screen_records(scene_doc: dict) -> list[dict]:
    """Every screen a build puts up, in clock order.

    `[{start_s, end_s, kind, title, sub, standing, timed:[{at, text}]}]` -
    `standing` is what the screen shows for as long as it is up, `timed` is what
    the engine paints on it at an instant. Pure: a dict in, a list out.
    """
    evidence = scene_doc.get("evidence") or {}
    out: list[dict] = []
    for scene in scene_doc.get("scenes") or []:
        span = scene.get("span") or [0.0, 0.0]
        start, end = float(span[0]), float(span[-1])
        page = (scene.get("world") or {}).get("page") or {}
        stage = None
        if page:
            stage = {"start_s": start, "end_s": end, "kind": PAGE_KIND,
                     "title": clean_screen_text(page.get("title")),
                     "sub": clean_screen_text(page.get("sub")),
                     "standing": page_figures(page), "timed": []}
            out.append(stage)
        for spec in scene.get("species") or []:
            text = species_text(spec)
            if not text:
                continue
            if stage is None:            # a world with no page still shows the words
                stage = {"start_s": start, "end_s": end, "kind": "a page", "title": "",
                         "sub": "", "standing": [], "timed": []}
                out.append(stage)
            stage["timed"].append({"at": float(spec.get("at", start)), "text": text})
        for dock in scene.get("docks") or []:
            ev = evidence.get(dock.get("slide") or dock.get("asset") or "") or {}
            standing = [x for x in (record_text(ev.get("record") or {}),) if x]
            out.append({"start_s": float(dock.get("enter", start)),
                        "end_s": float(dock.get("exit", end)),
                        "kind": KIND_WORDS.get(str(ev.get("species") or ""), "a picture"),
                        "title": clean_screen_text(ev.get("title")), "sub": "",
                        "standing": standing, "timed": []})
    return out


def resolve_screens(timeline: Path | None = None, screens: Path | None = None,
                    no_screens: bool = False) -> tuple[list[dict], str]:
    """(screens, screens_source) - the build's screens, or why there are none.

    No silent skips (AGENTS.md s8): the source is recorded either way.
    """
    if no_screens:
        return [], "none (--no-screens)"
    asked = screens if screens is not None else timeline
    if asked is None:
        return [], "none (no build given)"
    path = scene_timeline_path(asked)
    if path is None:
        return [], f"none found beside {Path(asked).name}"
    try:
        return screen_records(json.loads(path.read_text(encoding="utf-8"))), path.name
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"  warning: screens unreadable in {path.name} ({exc}); reading words only",
              file=sys.stderr)
        return [], f"none (unreadable {path.name})"


def window_screens(screens: list[dict], start_s: float, end_s: float) -> list[dict]:
    """The screens up during [start_s, end_s), each with the figures it shows then.

    Two scenes that hold the SAME page across a boundary read as one screen: the
    viewer saw one thing, so the window says it once.
    """
    out, seen = [], set()
    for sc in screens or []:
        if float(sc["end_s"]) <= start_s or float(sc["start_s"]) >= end_s:
            continue
        timed = [f["text"] for f in sc.get("timed") or [] if start_s <= float(f["at"]) < end_s]
        figures = [x for x in dict.fromkeys(list(sc.get("standing") or []) + timed) if x]
        if not (sc["title"] or sc["sub"] or figures):
            continue
        shown = {"kind": sc["kind"], "title": sc["title"], "sub": sc["sub"],
                 "figures": figures[:FIGURE_LIMIT]}
        key = (shown["kind"], shown["title"], shown["sub"], tuple(shown["figures"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(shown)
    return out


def screen_line(screen: dict) -> str:
    """One `[screen]` line: what it is, what it is called, what it shows."""
    head = screen["kind"] + (f': "{screen["title"]}"' if screen["title"] else "")
    parts = [head]
    if screen.get("sub"):
        parts.append(screen["sub"])
    if screen.get("figures"):
        parts.append("showing " + "; ".join(screen["figures"]))
    return f"{SCREEN_PREFIX} " + " - ".join(parts)


# ---- words in, windows out ----------------------------------------------

def clean_words(words: list[dict]) -> list[dict]:
    """New word records with every mark stripped; mark-only tokens dropped.

    Defensive: a take's transcript should never contain `[promise]`, but the
    viewer must not see one if it does.
    """
    out = []
    for w in words:
        token = beat_tags.strip_marks(str(w["w"])).strip()
        if token:
            out.append({"w": token, "start": float(w["start"]), "end": float(w["end"])})
    return out


def estimated_words(text: str) -> list[dict]:
    """Word times from the kit rate over the SPOKEN characters (no take yet).

    Cumulative character position / CHARS_PER_SEC, so the cut still lands on
    word boundaries - only the boundaries themselves are estimated.
    """
    body = spoken(text)
    return [{"w": m.group(0),
             "start": m.start() / CHARS_PER_SEC,
             "end": m.end() / CHARS_PER_SEC}
            for m in TOKEN_RE.finditer(body)]


def load_timeline(path: Path) -> list[dict]:
    """A build timeline's word list - `gate_opening_structure.load_timeline`."""
    d = json.loads(path.read_text(encoding="utf-8"))
    return d["words"] if isinstance(d, dict) and "words" in d else d


def resolve_words(script: Path, text: str, timeline: Path | None = None) -> tuple[list[dict], str]:
    """(words, 'measured'|'estimated') - a take's times beat any estimate.

    `--timeline` wins when it is readable, then the episode's own take
    (`load_timings` matches the take to THIS text by its opening words), then
    the kit rate.
    """
    if timeline is not None:
        try:
            words = clean_words(load_timeline(Path(timeline)))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"  warning: --timeline unreadable ({exc}); falling back", file=sys.stderr)
        else:
            if words:
                return words, "measured"
    first = A.sentences(spoken(text))
    timings = A.load_timings(script, first[0] if first else "")
    if timings:
        words = clean_words(timings)
        if words:
            return words, "measured"
    return clean_words(estimated_words(text)), "estimated"


def build_windows(words: list[dict], window_s: float = WINDOW_S,
                  memory_windows: int = MEMORY_WINDOWS,
                  screens: list[dict] | None = None) -> list[dict]:
    """Cut `words` into `window_s` windows on word boundaries, with memory.

    A word belongs to the window its START falls in, so no word is split. A
    window whose last word runs past the boundary reports the word's real
    `end_s`; the `span` is always the window's own clock. Windows with no
    words (a silence) are kept, so index i always means the same clock time.
    Marks are stripped here too - every path into the viewer goes through
    this function, so this is where the no-leak rule is guaranteed.

    `screens` (R26-0) adds one `[screen]` line per screen that is up during the
    window, AFTER the words: what it is, its title, and the figures it shows.
    The memory stays the words alone - what the reader HEARD just before.
    """
    if window_s <= 0:
        raise ValueError("window_s must be positive")
    if memory_windows < 0:
        raise ValueError("memory_windows must not be negative")
    words = clean_words(words)
    if not words:
        return []
    buckets: dict[int, list[dict]] = {}
    for w in words:
        buckets.setdefault(int(w["start"] // window_s), []).append(w)
    texts = [" ".join(x["w"] for x in buckets.get(i, []))
             for i in range(max(buckets) + 1)]
    out = []
    for i, body in enumerate(texts):
        held = buckets.get(i, [])
        nominal_end = (i + 1) * window_s
        memory = " ".join(t for t in texts[max(0, i - memory_windows):i] if t)
        shown = window_screens(screens or [], i * window_s, nominal_end)
        lines = [screen_line(sc) for sc in shown]
        out.append({
            "i": i,
            "start_s": round(i * window_s, ROUND_S),
            "end_s": round(held[-1]["end"] if held else nominal_end, ROUND_S),
            "span": f"{mmss(i * window_s)}-{mmss(nominal_end)}",
            "text": "\n".join([body] + lines).strip() if lines else body,
            "memory": memory,
            "screens": shown,
        })
    return out


def build_document(script: Path, text: str, timeline: Path | None = None,
                   window_s: float = WINDOW_S,
                   memory_windows: int = MEMORY_WINDOWS,
                   screens: Path | None = None,
                   no_screens: bool = False) -> dict:
    """The whole `viewer_windows.v1` payload for one script."""
    words, source = resolve_words(script, text, timeline)
    shown, screens_source = resolve_screens(timeline, screens, no_screens)
    windows = build_windows(words, window_s, memory_windows, shown)
    runtime = max((w["end"] for w in words), default=0.0)
    return {
        "schema_version": SCHEMA_VERSION,
        "script": script.name,
        "window_s": float(window_s),
        "memory_windows": int(memory_windows),
        "timing_source": source,
        "screens_source": screens_source,
        "runtime_s": round(runtime, ROUND_S),
        "windows": windows,
    }


def write_windows(doc: dict, path: Path) -> Path:
    """Write the payload as stable UTF-8 JSON (no clock, no ordering drift)."""
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


# ---- CLI ------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Cut a script into blind viewer windows (P36).")
    ap.add_argument("script", type=Path)
    ap.add_argument("--timeline", type=Path, help="build-f/timeline.json (measured word times)")
    ap.add_argument("--screens", type=Path, default=None,
                    help="the build's scene timeline or build dir (default: beside --timeline)")
    ap.add_argument("--no-screens", action="store_true",
                    help="read the words only - no [screen] lines (the pre-R26-0 read)")
    ap.add_argument("--window", type=float, default=WINDOW_S, help=f"window seconds (default {WINDOW_S:g})")
    ap.add_argument("--memory", type=int, default=MEMORY_WINDOWS,
                    help=f"windows of rolling memory (default {MEMORY_WINDOWS})")
    ap.add_argument("--out", type=Path, help="output path (default <script>-VIEWER-WINDOWS.json)")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    text = args.script.read_text(encoding="utf-8")
    doc = build_document(args.script, text, args.timeline, args.window, args.memory,
                         args.screens, args.no_screens)
    if not doc["windows"]:
        print(f"=== VIEWER WINDOWS: {args.script.name} ===")
        print("  no spoken words in this script - nothing to show a viewer")
        return 2
    out = write_windows(doc, args.out or windows_path(args.script))

    print(f"=== VIEWER WINDOWS: {args.script.name} ===")
    for key in ("window_s", "memory_windows", "timing_source", "screens_source"):
        print(f"  {key:>14}: {doc[key]}")
    print(f"  {'runtime':>14}: {mmss(doc['runtime_s'])}")
    print(f"  {'out':>14}: {out}")
    print()
    for w in doc["windows"][:2]:
        print(f"  [{w['i']:>3}] {w['span']}  {w['text']}")
    screened = sum(1 for w in doc["windows"] if w.get("screens"))
    print(f"\nRESULT: {len(doc['windows'])} windows / {doc['timing_source']} timings "
          f"/ {doc['memory_windows']}-window memory / {screened} with screens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

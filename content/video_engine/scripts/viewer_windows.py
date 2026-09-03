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

    python viewer_windows.py <script.txt> [--timeline build-f/timeline.json]
                             [--window 15] [--memory 2] [--out <path>]

Writes ``<script>-VIEWER-WINDOWS.json`` beside the script - the ``-VO`` stem
suffix dropped exactly as ``run_script_gates.report_path`` drops it - in the
``viewer_windows.v1`` shape the runner and the scorer bind to:

    {schema_version, script, window_s, memory_windows, timing_source,
     runtime_s, windows: [{i, start_s, end_s, span, text, memory}]}

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
                  memory_windows: int = MEMORY_WINDOWS) -> list[dict]:
    """Cut `words` into `window_s` windows on word boundaries, with memory.

    A word belongs to the window its START falls in, so no word is split. A
    window whose last word runs past the boundary reports the word's real
    `end_s`; the `span` is always the window's own clock. Windows with no
    words (a silence) are kept, so index i always means the same clock time.
    Marks are stripped here too - every path into the viewer goes through
    this function, so this is where the no-leak rule is guaranteed.
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
        out.append({
            "i": i,
            "start_s": round(i * window_s, ROUND_S),
            "end_s": round(held[-1]["end"] if held else nominal_end, ROUND_S),
            "span": f"{mmss(i * window_s)}-{mmss(nominal_end)}",
            "text": body,
            "memory": memory,
        })
    return out


def build_document(script: Path, text: str, timeline: Path | None = None,
                   window_s: float = WINDOW_S,
                   memory_windows: int = MEMORY_WINDOWS) -> dict:
    """The whole `viewer_windows.v1` payload for one script."""
    words, source = resolve_words(script, text, timeline)
    windows = build_windows(words, window_s, memory_windows)
    runtime = max((w["end"] for w in words), default=0.0)
    return {
        "schema_version": SCHEMA_VERSION,
        "script": script.name,
        "window_s": float(window_s),
        "memory_windows": int(memory_windows),
        "timing_source": source,
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
    ap.add_argument("--window", type=float, default=WINDOW_S, help=f"window seconds (default {WINDOW_S:g})")
    ap.add_argument("--memory", type=int, default=MEMORY_WINDOWS,
                    help=f"windows of rolling memory (default {MEMORY_WINDOWS})")
    ap.add_argument("--out", type=Path, help="output path (default <script>-VIEWER-WINDOWS.json)")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    text = args.script.read_text(encoding="utf-8")
    doc = build_document(args.script, text, args.timeline, args.window, args.memory)
    if not doc["windows"]:
        print(f"=== VIEWER WINDOWS: {args.script.name} ===")
        print("  no spoken words in this script - nothing to show a viewer")
        return 2
    out = write_windows(doc, args.out or windows_path(args.script))

    print(f"=== VIEWER WINDOWS: {args.script.name} ===")
    for key in ("window_s", "memory_windows", "timing_source"):
        print(f"  {key:>14}: {doc[key]}")
    print(f"  {'runtime':>14}: {mmss(doc['runtime_s'])}")
    print(f"  {'out':>14}: {out}")
    print()
    for w in doc["windows"][:2]:
        print(f"  [{w['i']:>3}] {w['span']}  {w['text']}")
    print(f"\nRESULT: {len(doc['windows'])} windows / {doc['timing_source']} timings "
          f"/ {doc['memory_windows']}-window memory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

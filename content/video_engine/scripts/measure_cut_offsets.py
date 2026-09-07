"""TR-2, the J-cut / L-cut question: where does each picture change sit relative to the
narration? Before the sentence boundary (picture leads, L-cut-like), after it (audio leads,
J-cut-like), or on it - and by how much? The DISTRIBUTION, not the mean.

`measure_cut_gaps.py` (P40 T1) answered "does the cut land in an acoustic gap"; it owns the
gap definition and this script imports it rather than restating it. What is new here is the
SIGNED offset when the cut does *not* land in the gap, and the sign convention that turns
that offset into an edit-grammar verdict:

    t < gap_start   the picture changed before the speech paused   -> PICTURE LEADS (L-cut-like)
    gap_start <= t <= gap_end                                      -> ON THE PAUSE
    t > gap_end     the speech had already resumed                 -> AUDIO LEADS  (J-cut-like)

Two sentence-boundary rules are reported side by side because the reference's transcript is
not reliably punctuated: (a) Delta t >= 0.30 s between consecutive words (doc 46 sec 46.3's
settled threshold) and (b) Delta t >= 0.45 s (the floor 46.3 overturned). Plus the offset to
the nearest word edge, which needs no pause rule at all.

Word timing comes from either source on file for the same audio:

  * a YouTube auto-caption `.vtt` - inline `<00:00:01.234><c> word</c>` ONSETS only, no word
    ends, so a "gap" is the onset-to-onset interval and is an UPPER BOUND on the silence;
  * a Whisper `.words.json` (`{"words": [{"w","s","e"}]}`) - real word ends, so a gap is the
    true silence. This is the timeline TR-2 and doc 46 sec 46.3 both name.

    python measure_cut_offsets.py --boundaries <measured.csv> --words <x.vtt | x.words.json>
                                  [--csv out.csv] [--fps 30] [--md]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from measure_cut_gaps import gaps as silences  # the P40 gap definition, not a second copy

RULE_A = 0.30
RULE_B = 0.45
FPS = 30.0

PICTURE_LEADS = "picture-leads"
AUDIO_LEADS = "audio-leads"
ON_PAUSE = "on-pause"
NO_GAP = "no-gap"

FIELDS = [
    "boundary", "t_s", "kind",
    "gap_a_start", "gap_a_end", "off_a_start_ms", "off_a_end_ms", "in_gap_a", "pos_in_gap_a",
    "gap_b_start", "gap_b_end", "off_b_start_ms", "in_gap_b", "nearest_word_edge_ms",
    # beyond the brief's schema, because the verdict is the answer and rule (b) needs the same pair
    "verdict_a", "off_b_end_ms", "pos_in_gap_b", "verdict_b",
]

_TS = re.compile(r"<(\d\d):(\d\d):(\d\d\.\d\d\d)>")
_TAG = re.compile(r"</?c[^>]*>|</?[ib]>")
_CUE = re.compile(r"^(\d\d):(\d\d):(\d\d\.\d\d\d)\s+-->")


# --- word timing ------------------------------------------------------------------------

def _hms(h: str, m: str, s: str) -> float:
    return int(h) * 3600 + int(m) * 60 + float(s)


def parse_vtt_words(path: Path) -> list[tuple[str, float]]:
    """Every word with an inline timestamp, in order. YouTube's rolling captions repeat the
    previous cue's text as a context line and emit zero-width roll-up cues; only lines that
    carry `<c>` markers are live, and their leading segment starts at the cue start."""
    out: list[tuple[str, float]] = []
    seen: set[tuple[str, float]] = set()
    cue_start = 0.0
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        cue = _CUE.match(line.strip())
        if cue:
            cue_start = _hms(*cue.groups())
            continue
        if "<c" not in line:
            continue
        parts = _TS.split(line)
        chunks = [(cue_start, parts[0])]
        for i in range(1, len(parts), 4):
            chunks.append((_hms(parts[i], parts[i + 1], parts[i + 2]), parts[i + 3]))
        for t, text in chunks:
            for word in _TAG.sub(" ", text).split():
                key = (word, round(t, 3))
                if key in seen or (out and t < out[-1][1]):
                    continue
                seen.add(key)
                out.append((word, t))
    return out


def parse_whisper_words(path: Path) -> tuple[list[tuple[str, float]], list[float]]:
    """(word, start) pairs plus the parallel list of word END times."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    raw = d["words"] if isinstance(d, dict) else d
    rows = sorted(
        (float(w.get("s", w.get("start"))), float(w.get("e", w.get("end"))), str(w.get("w", w.get("word", ""))))
        for w in raw
        if w.get("s", w.get("start")) is not None and w.get("e", w.get("end")) is not None
    )
    return [(w, s) for s, _, w in rows], [e for _, e, _ in rows]


def load_words(path: Path) -> tuple[list[tuple[str, float]], list[float] | None]:
    if Path(path).suffix.lower() == ".vtt":
        return parse_vtt_words(path), None
    return parse_whisper_words(path)


def onset_gaps(onsets: list[float], threshold: float) -> list[tuple[float, float]]:
    """Gaps from onsets alone (VTT): the interval between consecutive word starts."""
    return spans_gaps([(t, t) for t in onsets], threshold)


def spans_gaps(spans: list[tuple[float, float]], threshold: float) -> list[tuple[float, float]]:
    """Gaps from (start, end) word spans, via measure_cut_gaps' own definition."""
    return [(a, b) for a, b in silences(spans) if b - a >= threshold]


def word_edges(*series: list[float]) -> list[float]:
    return sorted({round(t, 6) for s in series for t in s})


# --- one boundary against one rule ------------------------------------------------------

def offset(t: float, gaps: list[tuple[float, float]]) -> dict:
    """The nearest gap and the signed offsets to its two edges."""
    if not gaps:
        return {"gap_start": None, "gap_end": None, "off_start_ms": None,
                "off_end_ms": None, "in_gap": False, "pos_in_gap": None, "verdict": NO_GAP}
    a, b = min(gaps, key=lambda g: 0.0 if g[0] <= t <= g[1] else min(abs(t - g[0]), abs(t - g[1])))
    in_gap = a <= t <= b
    if in_gap:
        verdict = ON_PAUSE
    elif t < a:
        verdict = PICTURE_LEADS
    else:
        verdict = AUDIO_LEADS
    width = b - a
    return {
        "gap_start": a, "gap_end": b,
        "off_start_ms": (t - a) * 1000.0, "off_end_ms": (t - b) * 1000.0,
        "in_gap": in_gap,
        "pos_in_gap": ((t - a) / width) if (in_gap and width > 0) else None,
        "verdict": verdict,
    }


def nearest_word_edge_ms(t: float, edges: list[float]) -> float | None:
    if not edges:
        return None
    return (t - min(edges, key=lambda e: abs(t - e))) * 1000.0


# --- the pass ---------------------------------------------------------------------------

def load_boundaries(path: Path) -> list[dict]:
    rows = list(csv.DictReader(Path(path).read_text(encoding="utf-8").splitlines()))
    return [{"boundary": r["boundary"], "t_s": float(r["t_s"]), "kind": r.get("kind", "")} for r in rows]


def build_rows(boundaries: list[dict], words: list[tuple[str, float]],
               ends: list[float] | None = None) -> list[dict]:
    onsets = [t for _, t in words]
    spans = list(zip(onsets, ends if ends is not None else onsets))
    gaps_a = spans_gaps(spans, RULE_A)
    gaps_b = spans_gaps(spans, RULE_B)
    edges = word_edges(onsets, ends if ends is not None else [])
    rows = []
    for b in boundaries:
        t = b["t_s"]
        a, bb = offset(t, gaps_a), offset(t, gaps_b)
        rows.append({
            "boundary": b["boundary"], "t_s": t, "kind": b["kind"],
            "gap_a_start": a["gap_start"], "gap_a_end": a["gap_end"],
            "off_a_start_ms": a["off_start_ms"], "off_a_end_ms": a["off_end_ms"],
            "in_gap_a": a["in_gap"], "pos_in_gap_a": a["pos_in_gap"], "verdict_a": a["verdict"],
            "gap_b_start": bb["gap_start"], "gap_b_end": bb["gap_end"],
            "off_b_start_ms": bb["off_start_ms"], "off_b_end_ms": bb["off_end_ms"],
            "in_gap_b": bb["in_gap"], "pos_in_gap_b": bb["pos_in_gap"], "verdict_b": bb["verdict"],
            "nearest_word_edge_ms": nearest_word_edge_ms(t, edges),
        })
    return rows


def _fmt(key: str, v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:.3f}" if key.startswith(("gap_", "pos_", "t_")) else f"{v:.1f}"
    return str(v)


def write_csv(rows: list[dict], out: Path) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(FIELDS)
        for r in rows:
            w.writerow([_fmt(k, r.get(k)) for k in FIELDS])
    return out


# --- the distribution -------------------------------------------------------------------

def pct(xs: list[float], p: float) -> float | None:
    if not xs:
        return None
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    i = p * (len(s) - 1)
    lo = int(i)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (i - lo)


def _dist(xs: list[float], fps: float) -> dict:
    ms = {f"p{int(p * 100)}": pct(xs, p) for p in (0.10, 0.25, 0.50, 0.75, 0.90)}
    frames = {k: (None if v is None else v / (1000.0 / fps)) for k, v in ms.items()}
    return ms, frames


def summarise(rows: list[dict], rule: str = "a", fps: float = FPS) -> dict:
    v, ss, se = f"verdict_{rule}", f"off_{rule}_start_ms", f"off_{rule}_end_ms"
    n = max(1, len(rows))
    starts = [r[ss] for r in rows if r[ss] is not None]
    ends = [r[se] for r in rows if r[se] is not None]
    lead = [-r[ss] for r in rows if r[v] == PICTURE_LEADS]
    trail = [r[se] for r in rows if r[v] == AUDIO_LEADS]
    pos = [r[f"pos_in_gap_{rule}"] for r in rows if r[f"pos_in_gap_{rule}"] is not None]
    s_ms, s_fr = _dist(starts, fps)
    e_ms, e_fr = _dist(ends, fps)
    l_ms, l_fr = _dist(lead, fps)
    t_ms, t_fr = _dist(trail, fps)
    w_ms, w_fr = _dist([r["nearest_word_edge_ms"] for r in rows if r["nearest_word_edge_ms"] is not None], fps)
    return {
        "n": len(rows),
        "in_gap": sum(1 for r in rows if r[v] == ON_PAUSE),
        "picture_leads": sum(1 for r in rows if r[v] == PICTURE_LEADS),
        "audio_leads": sum(1 for r in rows if r[v] == AUDIO_LEADS),
        "share_in_gap": sum(1 for r in rows if r[v] == ON_PAUSE) / n,
        "share_picture_leads": sum(1 for r in rows if r[v] == PICTURE_LEADS) / n,
        "share_audio_leads": sum(1 for r in rows if r[v] == AUDIO_LEADS) / n,
        "off_start_ms": s_ms, "off_start_frames": s_fr,
        "off_end_ms": e_ms, "off_end_frames": e_fr,
        "lead_ms": l_ms, "lead_frames": l_fr,
        "trail_ms": t_ms, "trail_frames": t_fr,
        "word_edge_ms": w_ms, "word_edge_frames": w_fr,
        "pos_in_gap": _dist(pos, fps)[0],
    }


def summarise_by_kind(rows: list[dict], rule: str = "a", fps: float = FPS) -> dict[str, dict]:
    kinds = sorted({r["kind"] for r in rows})
    return {k: summarise([r for r in rows if r["kind"] == k], rule, fps) for k in kinds}


def _cells(d: dict, fmt: str) -> str:
    return " | ".join("-" if d[k] is None else format(d[k], fmt) for k in ("p10", "p25", "p50", "p75", "p90"))


def markdown(rows: list[dict], rule: str, fps: float, label: str) -> str:
    s = summarise(rows, rule, fps)
    out = [f"**{label}** - n = {s['n']}; on the pause {s['in_gap']} ({s['share_in_gap']:.0%}), "
           f"picture leads {s['picture_leads']} ({s['share_picture_leads']:.0%}), "
           f"audio leads {s['audio_leads']} ({s['share_audio_leads']:.0%})", "",
           "| series | p10 | p25 | median | p75 | p90 |", "|---|---|---|---|---|---|"]
    for name, key in (("t - gap_start (ms)", "off_start_ms"), ("t - gap_start (frames @30)", "off_start_frames"),
                      ("t - gap_end (ms)", "off_end_ms"), ("t - gap_end (frames @30)", "off_end_frames"),
                      ("nearest word edge (ms)", "word_edge_ms"), ("nearest word edge (frames @30)", "word_edge_frames"),
                      ("position in gap (0 = onset, 1 = next word)", "pos_in_gap")):
        out.append(f"| {name} | {_cells(s[key], '.2f' if 'position' in name else ('.0f' if 'ms' in name else '.1f'))} |")
    out += ["", "| by kind | n | on pause | picture leads | audio leads | median t - gap_end (ms) | median pos in gap |",
            "|---|---|---|---|---|---|---|"]
    for kind, k in summarise_by_kind(rows, rule, fps).items():
        med = k["off_end_ms"]["p50"]
        pos = k["pos_in_gap"]["p50"]
        out.append(f"| {kind} | {k['n']} | {k['in_gap']} ({k['share_in_gap']:.0%}) | "
                   f"{k['picture_leads']} ({k['share_picture_leads']:.0%}) | "
                   f"{k['audio_leads']} ({k['share_audio_leads']:.0%}) | "
                   f"{'-' if med is None else f'{med:+.0f}'} | {'-' if pos is None else f'{pos:.2f}'} |")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--boundaries", required=True)
    ap.add_argument("--words", required=True)
    ap.add_argument("--csv")
    ap.add_argument("--fps", type=float, default=FPS)
    ap.add_argument("--label", default="")
    ap.add_argument("--md", action="store_true")
    args = ap.parse_args()

    words, ends = load_words(Path(args.words))
    rows = build_rows(load_boundaries(Path(args.boundaries)), words, ends)
    print(f"== {args.label or args.words}: {len(words)} words, {len(rows)} boundaries")
    if args.csv:
        print(f"   csv -> {write_csv(rows, Path(args.csv))}")
    for rule, name in (("a", f"rule (a) gap >= {RULE_A:.2f} s"), ("b", f"rule (b) gap >= {RULE_B:.2f} s")):
        print()
        print(markdown(rows, rule, args.fps, name) if args.md else json.dumps(summarise(rows, rule, args.fps), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

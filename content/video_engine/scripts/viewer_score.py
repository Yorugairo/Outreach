"""The viewer's scorer - turns blind perception reports into two measures (P36 T3).

The viewer (`viewer_run.py`) reads the script cold, 15s at a time, with a rolling
two-window memory, and answers four perception questions per window. It is never
asked when it would drop: an LLM's patience is not a human's. The judging happens
HERE, deterministically, so the same reports always produce the same verdict.

Two measures, per the P36 plan:

  BEAT RECALL - rule R2's laundering, measured from the outside. Every beat the
  writer DECLARED (`beat_tags.find_beats`) must show up in what the blind reader
  felt - in its new information or the question it was holding - within +-1
  window of where the beat actually sits. A beat the writer declared and the
  reader never felt was laundered: tagged, not delivered.

  INFORMATION GAIN - the retention clock (doc 31: something genuinely new every
  15-30s) measured as the count of CONCRETE new things per window. The
  concreteness rule is crude on purpose and stated in CONCRETE_RULE below, so a
  disagreement is about the rule and not about a model's mood.

Plus three cheap reads that fall out of the same reports: OPEN-LOOP coverage (is
the reader ever holding a question), DEAD windows and dead-runs, and CONFUSION.

The scorer always computes the true levels. Whether they bind is the RUNNER's
decision (`run_script_gates.py --viewer-gate`), which stays advisory until the
ep1 calibration passes Human Gate 1. One place decides promotion; this file just
measures.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import beat_tags  # noqa: E402

SCHEMA = "viewer_score.v1"

# ---- constants, each with the rule it comes from ---------------------------
RECALL_SLACK_WINDOWS = 1      # a beat may be felt one window early or late (P36 plan: "within +-1 window")
OVERLAP_MIN_TOKENS = 2        # content tokens shared before a viewer line counts as the beat's echo
OVERLAP_MIN_RATIO = 0.20      # ...and this share of a LONG beat sentence's content tokens (the floor still binds)
DEAD_RUN_LEN = 2              # two dead windows in a row = 30s with nothing new (P36 click: the two-window memory
                              # exists so a 30s gap has to be argued for)
OPEN_LOOP_MIN = 0.50          # doc 31 retention clock: an open loop should be live in at least half the windows
CONCRETE_RULE = ("a new thing is CONCRETE when it carries a numeral, or a capitalised name, or a word this "
                 "window introduced that the memory did not already hold - crude on purpose, and constant-cited")

STOP = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "for", "with", "by", "from", "as",
    "is", "are", "was", "were", "be", "been", "being", "it", "its", "this", "that", "these", "those", "there",
    "here", "you", "your", "we", "our", "they", "their", "he", "she", "his", "her", "i", "me", "my", "not",
    "no", "so", "if", "then", "than", "what", "which", "who", "when", "where", "how", "why", "all", "any",
    "some", "one", "two", "up", "down", "out", "over", "into", "about", "more", "most", "just", "now", "still",
    "can", "could", "will", "would", "should", "do", "does", "did", "has", "have", "had", "get", "got", "make",
    "made", "like", "same", "own", "every", "each", "very", "much", "many", "s", "t", "re", "ve", "ll", "d", "m",
}

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*|\d[\d.,%$]*")
SENT_END_RE = re.compile(r"[.!?](?=\s|$)")


# ---- pure helpers ----------------------------------------------------------
def tokens(text: str) -> list[str]:
    """Lowercased word/number tokens, punctuation dropped."""
    return [m.group(0).lower().strip("'’-") for m in WORD_RE.finditer(text or "")]


def content_tokens(text: str) -> set[str]:
    """Tokens that carry meaning: stopwords and one-character noise removed."""
    return {t for t in tokens(text) if t and t not in STOP and len(t) > 1}


def overlap_hit(beat_sentence: str, viewer_line: str) -> bool:
    """True when a viewer's line echoes the beat's own sentence.

    At least OVERLAP_MIN_TOKENS content tokens shared, and for a long beat sentence at
    least OVERLAP_MIN_RATIO of it. The floor is absolute on purpose: one shared word
    from the episode's own vocabulary ("steel") is not evidence that a beat was felt,
    and a short beat sentence would otherwise clear the ratio on a single token.
    """
    beat, seen = content_tokens(beat_sentence), content_tokens(viewer_line)
    if not beat or not seen:
        return False
    need = max(OVERLAP_MIN_TOKENS, round(OVERLAP_MIN_RATIO * len(beat)))
    return len(beat & seen) >= min(need, len(beat))


def sentence_at(text: str, offset: int) -> str:
    """The sentence beginning at `offset` - a beat tag sits immediately before the
    sentence that IS the beat (beat_tags module docstring)."""
    tail = text[offset:]
    tail = beat_tags.strip_marks(tail).lstrip()
    end = SENT_END_RE.search(tail)
    return (tail[: end.end()] if end else tail[:240]).strip()


def declared_beats(script_text: str) -> list[dict]:
    """[{tag, sentence}] in script order, from the writer's own declarations."""
    out = []
    for tag, offset in beat_tags.find_beats(script_text):
        sentence = sentence_at(script_text, offset)
        if sentence:
            out.append({"tag": tag, "sentence": sentence})
    return out


def window_of_sentence(windows: list[dict], sentence: str) -> int | None:
    """The window whose spoken text carries this sentence, by best content overlap.

    Matching on TEXT rather than recomputing a clock keeps one source of truth: the
    windower already placed every word on the take's own timings.
    """
    beat = content_tokens(sentence)
    if not beat:
        return None
    best, best_score = None, 0.0
    for w in windows:
        shared = beat & content_tokens(w.get("text", ""))
        score = len(shared) / len(beat)
        if score > best_score:
            best, best_score = int(w["i"]), score
    return best if best_score >= OVERLAP_MIN_RATIO else None


def is_concrete(thing: str, window_text: str, memory_text: str) -> bool:
    """CONCRETE_RULE, applied. Crude and deterministic by design."""
    if not (thing or "").strip():
        return False
    if any(ch.isdigit() for ch in thing):
        return True
    raw = [m.group(0) for m in WORD_RE.finditer(thing)]
    if any(w[:1].isupper() for w in raw[1:]):          # a name mid-phrase, not just the leading capital
        return True
    fresh = content_tokens(thing) & content_tokens(window_text)
    return bool(fresh - content_tokens(memory_text))


@dataclass(frozen=True)
class Row:
    id: str
    level: str          # PASS | WARN | FAIL | INFO
    message: str
    src: str


LEVEL_ORDER = {"FAIL": 0, "WARN": 1, "PASS": 2, "INFO": 3}


# ---- the score -------------------------------------------------------------
def score(windows_doc: dict, reports_doc: dict, script_text: str) -> dict:
    """Join the blind reports with the writer's declarations. Pure."""
    windows = list(windows_doc.get("windows") or [])
    reports = {int(r["i"]): r for r in (reports_doc.get("reports") or []) if "i" in r}

    # --- per-window gain, loops, confusion
    per_window = []
    for w in windows:
        i = int(w["i"])
        rep = reports.get(i) or {}
        things = [t for t in (rep.get("new_things") or []) if isinstance(t, str)]
        concrete = [t for t in things if is_concrete(t, w.get("text", ""), w.get("memory", ""))]
        per_window.append({
            "i": i, "span": w.get("span", ""),
            "reported": bool(rep) and "error" not in rep,
            "gain": len(concrete), "concrete": concrete,
            "held_question": (rep.get("held_question") or "").strip(),
            "asked_of_me": (rep.get("asked_of_me") or "").strip(),
            "could_not_follow": [c for c in (rep.get("could_not_follow") or []) if isinstance(c, str) and c.strip()],
            "error": rep.get("error", ""),
        })

    dead = [p["i"] for p in per_window if p["reported"] and p["gain"] == 0]
    dead_runs = []
    run = []
    for p in per_window:
        if p["reported"] and p["gain"] == 0:
            run.append(p["i"])
        else:
            if len(run) >= DEAD_RUN_LEN:
                dead_runs.append(list(run))
            run = []
    if len(run) >= DEAD_RUN_LEN:
        dead_runs.append(list(run))

    answered = [p for p in per_window if p["reported"]]
    loops = [p for p in answered if p["held_question"]]
    loop_share = len(loops) / len(answered) if answered else 0.0
    confusion = [p for p in per_window if p["could_not_follow"]]

    # --- beat recall
    beats = declared_beats(script_text)
    recall = []
    for b in beats:
        wi = window_of_sentence(windows, b["sentence"])
        matched, where = "", None
        if wi is not None:
            for j in range(wi - RECALL_SLACK_WINDOWS, wi + RECALL_SLACK_WINDOWS + 1):
                rep = reports.get(j)
                if not rep or "error" in rep:
                    continue
                lines = list(rep.get("new_things") or []) + [rep.get("held_question") or ""]
                for line in lines:
                    if isinstance(line, str) and overlap_hit(b["sentence"], line):
                        matched, where = line.strip(), j
                        break
                if matched:
                    break
        recall.append({"tag": b["tag"], "sentence": b["sentence"], "window": wi,
                       "perceived": bool(matched), "matched": matched, "matched_window": where})

    scored = [r for r in recall if r["window"] is not None]
    perceived = [r for r in scored if r["perceived"]]
    pct = 100.0 * len(perceived) / len(scored) if scored else 0.0

    rows: list[Row] = []
    if not scored:
        rows.append(Row("V01", "INFO", "the script declares no beats inside any window - recall not measurable",
                        "P36 beat recall (rule R2 laundering, measured from the outside)"))
    else:
        missed = [r for r in scored if not r["perceived"]]
        rows.append(Row("V01", "PASS" if not missed else "FAIL",
                        f"{len(perceived)}/{len(scored)} declared beats perceived ({pct:.0f}%)"
                        + ("" if not missed else "; unperceived: "
                           + ", ".join(f"[{r['tag']}] w{r['window']}" for r in missed[:8])
                           + ("" if len(missed) <= 8 else f" +{len(missed) - 8} more")),
                        "P36 beat recall (rule R2 laundering, measured from the outside)"))
    rows.append(Row("V02", "WARN" if dead_runs else "PASS",
                    (f"{len(dead_runs)} dead-run(s) of {DEAD_RUN_LEN}+ windows: "
                     + "; ".join("w" + "-".join(str(i) for i in (r[0], r[-1])) for r in dead_runs[:6]))
                    if dead_runs else f"no run of {DEAD_RUN_LEN}+ windows without a concrete new thing",
                    "doc 31 retention clock: something genuinely new every 15-30s"))
    rows.append(Row("V03", "PASS" if loop_share >= OPEN_LOOP_MIN else "WARN",
                    f"open loop live in {len(loops)}/{len(answered)} windows ({100 * loop_share:.0f}%)",
                    f"open-loop coverage floor {100 * OPEN_LOOP_MIN:.0f}% (doc 31)"))
    rows.append(Row("V04", "INFO" if not confusion else "WARN",
                    "nothing the reader could not follow" if not confusion else
                    f"{len(confusion)} window(s) with something unfollowable: "
                    + "; ".join(f"{p['span']} {p['could_not_follow'][0][:60]}" for p in confusion[:4]),
                    "comprehension outranks structure (STRENGTH-LOOP precedence)"))
    gains = [p["gain"] for p in answered]
    rows.append(Row("V05", "INFO",
                    (f"gain per window: median {sorted(gains)[len(gains) // 2]}, "
                     f"{len(dead)} dead of {len(answered)} reported") if gains else "no reports",
                    CONCRETE_RULE))

    return {"schema_version": SCHEMA, "windows": len(windows), "reported": len(answered),
            "timing_source": windows_doc.get("timing_source", "unknown"),
            "prompt_version": reports_doc.get("prompt_version", ""), "model": reports_doc.get("model", ""),
            "recall": recall, "recall_pct": pct, "per_window": per_window,
            "dead": dead, "dead_runs": dead_runs, "loop_share": loop_share,
            "rows": [r.__dict__ for r in rows]}


def result_line(res: dict) -> str:
    n = lambda lvl: sum(1 for r in res["rows"] if r["level"] == lvl)
    return (f"RESULT: {n('FAIL')} FAIL / {n('WARN')} WARN / {n('PASS')} PASS / {n('INFO')} INFO")


def render(res: dict, script_name: str) -> str:
    """`<script>-VIEWER.md` - the blind read, and what it did and did not reach."""
    out = [f"# VIEWER — {script_name}", "",
           f"A blind reader, {res['windows']} windows, two-window memory, "
           f"{res['reported']} reported ({res['timing_source']} timings"
           + (f", model {res['model']}, prompt {res['prompt_version']}" if res.get("model") else "") + ").",
           "It was never asked when it would leave. The judging is this file's, and it is deterministic.", "",
           "```text"]
    for r in sorted(res["rows"], key=lambda r: (LEVEL_ORDER[r["level"]], r["id"])):
        out.append(f"  [{r['level']:5}] {r['id']} {r['message']}")
        out.append(f"          {r['src']}")
    out += ["", result_line(res), "```", "", "## Beat recall — did the blind reader feel what the writer declared?", ""]
    scored = [r for r in res["recall"] if r["window"] is not None]
    if not scored:
        out.append("No declared beat landed inside a window; the script declares none, or none could be placed.")
    else:
        out += ["| beat | window | perceived | the reader's line |", "|---|---|---|---|"]
        for r in scored:
            line = (r["matched"][:70] + "…") if len(r["matched"]) > 70 else r["matched"]
            out.append(f"| `[{r['tag']}]` | w{r['window']} | {'yes' if r['perceived'] else '**NO**'} "
                       f"| {line or '—'} |")
    out += ["", "## Per window", "", "| w | span | gain | holding a question | could not follow |", "|---|---|---|---|---|"]
    for p in res["per_window"]:
        q = (p["held_question"][:54] + "…") if len(p["held_question"]) > 54 else p["held_question"]
        cf = "; ".join(p["could_not_follow"])[:40]
        mark = "" if p["reported"] else " *(no report)*"
        out.append(f"| {p['i']} | {p['span']} | {p['gain'] if p['reported'] else '—'}{mark} | {q or '—'} | {cf or '—'} |")
    out += ["", f"Concreteness rule: {CONCRETE_RULE}.", ""]
    return "\n".join(out)


# ---- io --------------------------------------------------------------------
def paths_for(script: Path) -> tuple[Path, Path, Path]:
    stem = script.stem[:-3] if script.stem.endswith("-VO") else script.stem
    return (script.with_name(stem + "-VIEWER-WINDOWS.json"),
            script.with_name(stem + "-VIEWER-REPORTS.json"),
            script.with_name(stem + "-VIEWER.md"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="score the viewer's blind reports (P36)")
    ap.add_argument("script", type=Path)
    ap.add_argument("--windows", type=Path, default=None)
    ap.add_argument("--reports", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    wp, rp, op = paths_for(args.script)
    wp, rp, op = args.windows or wp, args.reports or rp, args.out or op
    for p, how in ((wp, "viewer_windows.py"), (rp, "viewer_run.py")):
        if not p.exists():
            print(f"viewer_score: missing {p.name} - run {how} first", file=sys.stderr)
            return 2
    res = score(json.loads(wp.read_text(encoding="utf-8")),
                json.loads(rp.read_text(encoding="utf-8")),
                args.script.read_text(encoding="utf-8"))
    op.write_text(render(res, args.script.name), encoding="utf-8")
    print(render(res, args.script.name).split("```text")[1].split("```")[0].strip())
    print(f"\nreport: {op}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

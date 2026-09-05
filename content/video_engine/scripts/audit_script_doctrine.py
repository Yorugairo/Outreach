"""Doctrine audit for a VO script — the checks the pattern linter cannot make.

`lint_script_pattern.py` covers the kit hard-gate tier: sentence stats,
passive scan, fragment stacks, CTA budget, pause-mark ration, tautology,
ring. This covers what only reads against the DOCS and a RUNTIME:

  doc 32  ear mechanics (sentence mean, SPREAD and long-tail share against
          the 10-15 speech band; attribution position; signposting)
  doc 33  voice profile calibration
  doc 35  answer-format rules (falsifiable tell, one answer, steelman)
  doc 37  TTS delivery (mv2 cap, break ration, spoken numerals)
  doc 38  phase QC line (timed beats), pivot pin, CTA placement

No audio is required to check a timed gate. Doctrine supplies the rate, so
positional beats are checked from the text itself, two ways (chars/sec and
words/min, both measured off a real take). Where a take DOES exist on disk,
its word timings override the estimate for the tight gates — an 8% estimate
error is the difference between a pass and a fail on a 3-second cap.

Exit 0 = no FAILs. Warnings do not fail the run.
"""
from __future__ import annotations

import argparse
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import json
import math
import re
import statistics
from dataclasses import dataclass
from pathlib import Path

import kit_spec

# Two independent estimators, both measured off the Steel and Paper take
# (1,231 words / 7,161 chars / 446.1s). No audio is needed to check a timed
# gate — doctrine supplies the rate. They are kept as a PAIR because they
# fail differently: chars/sec under-reads numeral-dense lines (a year is 4
# characters and about a second of speech), words/min under-reads long words.
# When they disagree by more than TIMING_SPREAD_WARN the estimate is soft and
# the audit says so rather than pretending to a precision it does not have.
# MEASURED (a fact about the voice, not doctrine) — see kit_spec.
CHARS_PER_SEC = kit_spec.CHARS_PER_SEC
WORDS_PER_MIN = kit_spec.WORDS_PER_MIN
TIMING_SPREAD_WARN = 0.08    # 8%
MV2_CAP = 10_000             # eleven_multilingual_v2
# doc 32 sec 1 (corrected 2026-08-29): speech wants 10-15 words average, not
# the 15-16 the doc carried — that was a written-prose figure, and 15-20 is
# where listener comprehension falls off rather than where it peaks.
SENTENCE_MEAN_TARGET = kit_spec.sentence_band()
# The mean alone does not hear anything: a flat 12-word script and one mixing
# 5-word punches with 15-word carries score identically. Doctrine asks for
# deliberate variation, so the spread and the tail are gates too.
SENTENCE_STDEV_MIN = 3.5
LONG_SENTENCE_WORDS = 20        # comprehension drop-off
LONG_SENTENCE_SHARE_MAX = 0.12
PIVOT_PIN = kit_spec.pivot_pin()          # kit geometry
BREAK_RATION_MAX = 3.0       # doc 37 sec 1
import beat_tags  # noqa: E402  - the one owner of the mark/tag set
MARKS = beat_tags.ALL_MARKS   # delivery marks + structural beat tags (gate_opening_structure)

# doc 38 beat 2 ban list + VOICE-PACK anti-pattern 1
GREETINGS = (r"\bhey (?:guys|everyone|folks)\b", r"\bwelcome back\b",
             r"\bin (?:this|today's) video\b", r"\bwhat's up\b",
             r"\bbefore we (?:start|begin|dive)\b", r"\blet's dive in\b",
             r"\btoday (?:we're|we are) going to\b")
# doc 32 sec 1: attribution first, not trailing
TRAILING_ATTR = (r",\s*according to\b", r",\s*(?:per|says)\s+[A-Z]",
                 r",\s*(?:he|she|they) said\b")
CTA = (r"\bsubscribe\b", r"\blike button\b", r"\bhit (?:the )?like\b",
       r"\bin the comments\b", r"\bcomments? below\b", r"\bshare this\b")
# doc 37 sec 4: narration takes words, badges take digits
DIGIT_NUMERAL = re.compile(r"(?<![\w.$-])\d[\d,]*(?:\.\d+)?\s*(?:%|percent)?")
YEAR = re.compile(r"^(?:1[5-9]|20)\d\d$")
# FULL-VIDEO-MAP sec 1 — the scaling law. P1 and P6 are pinned in ABSOLUTE
# seconds at every runtime ("the attention ladder is physics, not
# proportion"); everything between them is a share of runtime.
P1_OPEN_S = kit_spec.open_close_seconds()   # absolute, both ends
# P2's end is FITTED to the map's authored columns (300s@30m, 180s@16m,
# 135s@8m), not taken from its "~17%" label. That label only reproduces the
# @30:00 column: the authored @8:00 column ends P2 at 28%, and applying a
# flat 17% below ~15 minutes squeezes P2 under a minute — short enough that
# the A3 anchor at 3:00 would land past the end of the phase it belongs to.
# See FULL-VIDEO-MAP sec 1, "P2 boundary".
P2_ENGINE_SLOPE, P2_ENGINE_INTERCEPT_S = 0.125, 75.0
P3_GAP_PCT = (17.0, 45.0)
P4_PIVOT_PCT = (45.0, 55.0)
P5_REFLECTION_PCT = (55.0, 87.0)
P6_CLOSE_S = kit_spec.open_close_seconds()  # absolute, from the end
# sec 2 — rehook anchors A1..A4. A4 is the pivot itself, checked separately.
# A1/A2 are absolute (the attention ladder is physics); A3 is 10% of runtime
# (P2.md; ruling E23 2026-09-02) and is computed per script in audit() via
# kit_spec.a3_anchor_s — the same function the opening gate uses. The 3:00
# that used to sit here was the @30:00 column of that rule, not a constant.
REHOOK_ANCHORS = {"A1": 30.0, "A2": 60.0}
REHOOK_TOLERANCE_S = 45.0
# doc 38: rehook slots at ~0:30, ~1:00, ~10% and mid-video
# MAP sec 3: the 0:30-0:60 dated promise IS A1 ("A1 + F1 + macro-loop-1
# setup in one line"), so it counts as an anchor even though it is not one of
# the five template families.
A1_PROMISE = r"by the end,? you'?ll|you'?ll run it yourself|thirty seconds a"
REHOOKS = (r"but here's where", r"here's where it gets",
           r"this is where most people", r"what nobody", r"fast-?forward",
           r"but the real question", r"which flips the question",
           r"and that's where", r"but look at what", r"and this is where")


@dataclass(frozen=True)
class Finding:
    level: str          # FAIL | WARN | INFO
    rule: str           # doc reference
    message: str


def spoken(text: str) -> str:
    t = beat_tags.strip_marks(text)   # every known mark AND beat tag is silent
    t = re.sub(r"^\s*(?:#|\||>|---|```).*$", "", t, flags=re.M)
    return re.sub(r"\s+", " ", t).strip()


def sentences(s: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", s) if x.strip()]


def secs(fragment: str) -> float:
    """Spoken seconds for a fragment, averaging the two estimators."""
    words = len(re.findall(r"[A-Za-z0-9'%$]+", fragment))
    return (len(fragment) / CHARS_PER_SEC + words / WORDS_PER_MIN * 60) / 2


def spread(fragment: str) -> float:
    """Relative disagreement between the estimators — high means numerals."""
    words = len(re.findall(r"[A-Za-z0-9'%$]+", fragment))
    a, b = len(fragment) / CHARS_PER_SEC, words / WORDS_PER_MIN * 60
    return abs(a - b) / max(a, b, 1e-9)


def _norm(s: str) -> str:
    """Compare words, not punctuation — a take carries commas the text may not."""
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def load_timings(script: Path, first_sentence: str = "") -> list[dict] | None:
    """Real word timings for this episode, if a take has been recorded.

    Ground truth beats any estimate, and the timed gates are exactly where
    a 9% estimate error changes a verdict — BUT only if the take is of THIS
    text. An episode folder holds one `vo/`, and a revised script sits next
    to the previous script's recording. Reporting a measured hook length for
    a hook that was never recorded is worse than estimating it, so the
    opening words must match before any timing is trusted.
    """
    # An episode accumulates take directories (vo/, vo-c/, vo-f/ ...). Search
    # them all and use the one whose opening words match THIS script — the
    # directory name is a convention, the text match is the actual proof.
    cands = []
    for vo in sorted(script.parent.glob("vo*")):
        if not vo.is_dir():
            continue
        files = sorted(vo.rglob("scene_*.words.json"),
                       key=lambda p: int(re.search(r"\d+", p.name).group()))
        if files:
            cands.append(files)
    if not cands:
        return None
    files = None
    if first_sentence:
        wanted = _norm(" ".join(first_sentence.split()[:6]))
        for group in cands:
            head = json.loads(group[0].read_text(encoding="utf-8")).get("words", [])
            if _norm(" ".join(w["w"] for w in head[:6])) == wanted:
                files = group
                break
        if files is None:
            return None
    else:
        files = cands[0]
    words, offset = [], 0.0
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        for w in d.get("words", []):
            words.append({"w": w["w"], "start": w["start_s"] + offset,
                          "end": w["end_s"] + offset})
        offset += d.get("duration_s", 0.0)
    return words or None


def gate_report(script_path: Path | None) -> Path | None:
    """The `<script>-GATES.md` the runner writes beside the script, if any.

    CHECK-RESPONSIBILITIES R1 (one row, one verdict): once the opening gate
    has ruled on doc 38 beats 1-4, the audit does not restate them.
    """
    if script_path is None:
        return None
    import run_script_gates  # lazy: run_script_gates imports this module
    path = run_script_gates.report_path(Path(script_path))
    return path if path.exists() else None


def _discard(level: str, rule: str, msg: str) -> None:
    """Sink for rows another tool owns - stats are still computed."""


def _doc38_opening(sp: str, sents: list[str], stats: dict, add) -> None:
    """doc 38 beats 1-4 (hook 3s + properties, greetings, paradox 8s, 'you'
    by 0:30, promise in 60s). `add` is `_discard` when the gate owns them."""
    first = sents[0] if sents else ""
    t_first = secs(first)
    # Beat 1 names FOUR properties; two are mechanically decidable. Concreteness
    # is a judgement (a regex proxy returns confident wrong verdicts), so it
    # stays with the reader and is named in the message instead.
    past = re.search(r"\b(?:was|were|had|did|used to)\b", first, re.I)
    viewer = re.search(r"\b(?:you|your|yours|you\'?re|you\'?ll)\b",
                       first, re.I)
    stats["hook_properties"] = (
        f"present-tense={'n' if past else 'y'}, "
        f"viewer-facing={'y' if viewer else 'n'}")
    lacks = ([f"present tense ({past.group()!r})"] if past else []) + (
        [] if viewer else ["direct address"])
    if lacks:
        add("WARN", "doc 38 beat 1",
            f"the microhook lacks {' and '.join(lacks)}. The beat asks for a "
            f"present-tense, viewer-facing, concrete grab - duration is only "
            f"one of four. Concreteness is yours to judge: {first!r}")
    if t_first > 3.0:
        add("FAIL", "doc 38 beat 1",
            f"first sentence runs {t_first:.1f}s (limit 3.0s): {first!r}")
    for pat in GREETINGS:
        m = re.search(pat, sp, re.I)
        if m:
            add("FAIL", "doc 38 beat 2",
                f"banned opener construction: {m.group()!r}")
    # Beat 2: the paradox lands by 0:08 (the decision boundary), measured as
    # the end of sentence two - where the microhook is paid (and paid wrong).
    if len(sents) >= 2:
        t_paradox = secs(" ".join(sents[:2]))
        stats["paradox_s"] = round(t_paradox, 1)
        if t_paradox > 8.0:
            add("FAIL", "doc 38 beat 2",
                f"the microhook is not paid until {t_paradox:.1f}s — the "
                f"viewer decides at 0:08")
    m = re.search(r"\byou\b|\byour\b|\byou'll\b|\byou're\b", sp, re.I)
    t_you = secs(sp[:m.start()]) if m else float("inf")
    if t_you > 30:
        add("FAIL", "doc 38 beat 3",
            f"direct address ('you') first appears at {t_you:.0f}s "
            f"(must land by 0:30)")
    stats["first_you_s"] = round(t_you, 1) if m else None
    head = sp[:int(60 * CHARS_PER_SEC)]  # generous window; a miss here is a WARN
    if not re.search(r"\bby the end\b|\byou'll\b|\bthirty seconds\b"
                     r"|\brun (?:it|your)\b", head, re.I):
        add("WARN", "doc 38 beat 4",
            "no dated/checkable promise detected inside the first 60s")


def audit(text: str, script_path: Path | None = None, short: bool = False) -> tuple[list[Finding], dict]:
    """short=True (G2, 2026-09-05): the shorts shape - doc 35 rule 2's flip block and the MAP sec 1 P1 pin are long-form
    draw-outs and do not bind (operator 2026-09-04 on the Tokyo short: 'a short has no late-stage flip')."""
    out: list[Finding] = []
    sp = spoken(text)
    n = len(sp)
    runtime = secs(sp)
    sents = sentences(sp)
    words = [len(re.findall(r"[A-Za-z']+", s)) for s in sents]
    mean = sum(words) / len(words) if words else 0.0

    stats = {"chars": n, "runtime_s": round(runtime, 1),
             "runtime": f"{int(runtime // 60)}m {int(runtime % 60):02d}s",
             "sentences": len(sents), "sentence_mean": round(mean, 1)}

    def add(level: str, rule: str, msg: str) -> None:
        out.append(Finding(level, rule, msg))

    # ---- doc 37: delivery -------------------------------------------------
    if n > MV2_CAP:
        add("INFO", "doc 37 sec 8",
            f"{n:,} chars exceeds the mv2 {MV2_CAP:,} cap — chained take "
            f"required, split at a phase boundary")
    marks = re.findall(r"\[([a-z][a-z-]*)\]", text)
    unknown = sorted(set(marks) - MARKS)
    if unknown:
        add("FAIL", "doc 37 sec 1", f"unknown marks would be spoken: {unknown}")
    # Only DELIVERY marks compile into TTS <break> tags (doc 37 sec 1); beat tags are
    # authoring metadata stripped before synthesis (beat_tags.strip_beat_tags) and
    # never reach the voice. Counting them here failed every well-annotated short by
    # arithmetic while Script G slid under at 2.8/1k on length alone (2026-09-03).
    breaks = [m for m in marks if m in beat_tags.DELIVERY_MARKS]
    ration = len(breaks) / (n / 1000) if n else 0.0
    if ration > BREAK_RATION_MAX:
        add("FAIL", "doc 37 sec 1",
            f"break ration {ration:.2f}/1k exceeds {BREAK_RATION_MAX} — "
            f"causes audible speed-ups")
    stats["break_ration"] = round(ration, 2)

    # Years stay in digits — TTS reads "1845" as eighteen forty-five, and
    # spelling them out is worse for the ear, not better.
    digits = [m.group().strip() for m in DIGIT_NUMERAL.finditer(sp)
              if not YEAR.match(m.group().strip(" ,.;:—-"))]
    if digits:
        add("FAIL", "doc 37 sec 4",
            f"narration carries digit numerals (badges take digits, "
            f"narration takes words): {digits[:6]}")

    # ---- doc 32 / 33: ear mechanics --------------------------------------
    lo, hi = SENTENCE_MEAN_TARGET
    # Two gates disagree unless the short figures are held out. S5 of the
    # strength check LICENSES sentences under five words when they are
    # deliberate figures — anaphora pairs, enumerations, snaps, chart-reads —
    # and a script that uses them well is dragged under the band by its own
    # good practice. So gate the mean of the carrying sentences and report
    # the raw mean beside it. Unlicensed short sentences are S5's job, not
    # this one's.
    carrying = [w for w in words if w >= 5]
    mean_carrying = sum(carrying) / len(carrying) if carrying else 0.0
    stats["sentence_mean_carrying"] = round(mean_carrying, 1)
    stats["short_figure_share"] = f"{1 - len(carrying) / len(words):.1%}"         if words else "0%"
    if not (lo <= mean_carrying <= hi):
        add("WARN", "doc 32 sec 1 / doc 33",
            f"sentence mean {mean_carrying:.1f} words (excluding sub-5-word "
            f"figures) is outside the {lo:g}-{hi:g} band for speech; raw "
            f"mean {mean:.1f}")
    stdev = statistics.pstdev(words) if len(words) > 1 else 0.0
    stats["sentence_stdev"] = round(stdev, 1)
    if stdev < SENTENCE_STDEV_MIN:
        add("WARN", "doc 32 sec 1",
            f"sentence-length spread {stdev:.1f} is flat (min "
            f"{SENTENCE_STDEV_MIN}) — doctrine wants 5-word punches mixed "
            f"with 15-word carries, not an even cadence")
    long_share = (sum(1 for w in words if w > LONG_SENTENCE_WORDS)
                  / len(words) if words else 0.0)
    stats["over_20_share"] = f"{long_share:.1%}"
    if long_share > LONG_SENTENCE_SHARE_MAX:
        add("WARN", "doc 32 sec 1",
            f"{long_share:.0%} of sentences run past {LONG_SENTENCE_WORDS} "
            f"words (max {LONG_SENTENCE_SHARE_MAX:.0%}) — the range where "
            f"listener comprehension drops")
    for pat in TRAILING_ATTR:
        for m in re.finditer(pat, sp):
            add("WARN", "doc 32 sec 1",
                "trailing attribution — frame before assertion: ..."
                + sp[max(0, m.start() - 45):m.end() + 15] + "...")

    # ---- doc 38 phase 1 QC line ------------------------------------------
    first = sents[0] if sents else ""
    stats["hook_spread"] = f"{spread(first):.0%}"
    if spread(first) > TIMING_SPREAD_WARN:
        add("INFO", "estimator",
            f"the two rate estimates disagree by {spread(first):.0%} on the "
            f"first sentence (numerals read longer than they look) — record "
            f"a take to settle it")
    # R1: one row, one verdict. With a gates report beside the script the
    # opening gate owns beats 1-4; the audit points at it instead.
    report = gate_report(script_path)
    if report is not None:
        add("INFO", "doc 38 B1-B4",
            f"owned by gate_opening_structure - see {report}")
    _doc38_opening(sp, sents, stats, _discard if report is not None else add)

    # ---- doc 38 phase 6: the close ---------------------------------------
    hits = [m for pat in CTA for m in re.finditer(pat, sp, re.I)]
    if len(hits) > 1:
        add("FAIL", "doc 38 phase 6",
            f"{len(hits)} CTA constructions — doctrine allows ONE")
    for m in hits:
        t_cta = secs(sp[:m.start()])
        if runtime - t_cta > 90:
            add("WARN", "doc 38 phase 6",
                f"CTA at {t_cta:.0f}s sits {runtime - t_cta:.0f}s before the "
                f"end — the action window is the final 90s, after the payoff")
    stats["cta_count"] = len(hits)

    # ---- doc 38: rehook slots --------------------------------------------
    # The two most retention-critical slots are the earliest ones, and they
    # are the easiest to lose to a steelman that ran long.
    rehooks = sorted({m.start() for pat in REHOOKS
                      for m in re.finditer(pat, sp, re.I)})
    times = [secs(sp[:i]) for i in rehooks]
    stats["rehooks"] = [f"{t / 60:.1f}m" for t in times]
    # ---- FULL-VIDEO-MAP: the documented shape ----------------------------
    # Phase geometry, derived from THIS script's runtime by the scaling law.
    p1_end = min(P1_OPEN_S[1], runtime * 0.13)
    phases = {
        "P1 OPEN": (0.0, p1_end),
        "P2 ENGINE": (p1_end,
                      runtime * P2_ENGINE_SLOPE + P2_ENGINE_INTERCEPT_S),
        "P3 GAP": (runtime * P3_GAP_PCT[0] / 100, runtime * P3_GAP_PCT[1] / 100),
        "P4 PIVOT": (runtime * P4_PIVOT_PCT[0] / 100,
                     runtime * P4_PIVOT_PCT[1] / 100),
        "P5 REFLECTION": (runtime * P5_REFLECTION_PCT[0] / 100,
                          runtime * P5_REFLECTION_PCT[1] / 100),
        "P6 CLOSE": (runtime - P6_CLOSE_S[1], runtime),
    }
    stats["phase_map"] = {k: f"{a / 60:.1f}-{b / 60:.1f}m"
                          for k, (a, b) in phases.items()}
    if short:
        add("INFO", "MAP sec 1", f"short (G2): P1 computes to {p1_end:.0f}s; the 60-90s open is long-form geometry and does not bind")
    elif not (P1_OPEN_S[0] <= p1_end <= P1_OPEN_S[1]):
        add("WARN", "MAP sec 1",
            f"P1 computes to {p1_end:.0f}s; the open is pinned 60-90s at "
            f"every runtime")

    # sec 1 — the elastic knob: how many P3 pattern units this runtime wants.
    want_units = kit_spec.unit_count(runtime / 60)
    stats["p3_units_expected"] = want_units

    # sec 2 — rehook anchors A1/A2/A3 (A4 is the pivot, pinned separately).
    a1 = [secs(sp[:m.start()]) for m in re.finditer(A1_PROMISE, sp, re.I)]
    anchor_hits = sorted(set(times) | set(a1))
    a3_s = kit_spec.a3_anchor_s(runtime)           # E23: 10% of THIS runtime
    mmss = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"  # noqa: E731
    stats["a3_anchor"] = mmss(a3_s)
    anchors = {**REHOOK_ANCHORS, "A3": a3_s}
    missing = [name for name, target in anchors.items()
               if not any(abs(t_ - target) <= REHOOK_TOLERANCE_S
                          for t_ in anchor_hits)]
    if missing:
        add("WARN", "MAP sec 2",
            f"no rehook construction within {REHOOK_TOLERANCE_S:.0f}s of "
            f"anchor(s) {', '.join(missing)} "
            f"(A1 ~0:30, A2 ~1:00, A3 ~{mmss(a3_s)} at {mmss(runtime)} = "
            f"10% of runtime) — found at "
            f"{[f'{t_ / 60:.1f}m' for t_ in times] or 'none'}")

    # sec 2 — CTA budget: at most one micro-CTA in the P2 tail, exactly one
    # outro CTA inside P6. Anything outside those windows is unbudgeted.
    p6_start = phases["P6 CLOSE"][0]
    for m in hits:
        t_cta = secs(sp[:m.start()])
        in_p6 = t_cta >= p6_start
        in_p2_tail = phases["P2 ENGINE"][0] <= t_cta <= phases["P2 ENGINE"][1]
        if not (in_p6 or in_p2_tail):
            add("WARN", "MAP sec 2",
                f"CTA at {t_cta / 60:.1f}m sits outside both budgeted "
                f"windows (P2 tail, or P6 from {p6_start / 60:.1f}m)")

    # sec 2 — ceiling: no TTS segment carries more than three break tags.
    paras = [x for x in re.split(r"\n\s*\n", text) if x.strip()]
    for i, para in enumerate(paras, start=1):
        k = len(re.findall(r"\[(?:pre|post)-key\]", para))
        if k > 3:
            add("FAIL", "MAP sec 2",
                f"paragraph {i} carries {k} break tags (ceiling 3)")

    # ---- doc 35: answer format -------------------------------------------
    if short:   # G2: the threshold / where-we-sit / flip block is a long-form draw-out; a short is hook -> mechanism -> ring
        add("INFO", "doc 35 rule 2", "short (G2): no late-stage flip is asked of a short - the long form carries the tell")
    elif not re.search(r"\bthreshold\b|\btripwire\b|\bthe flip\b", sp, re.I):
        add("FAIL", "doc 35 rule 2",
            "no falsifiable tell — an answer video must name one variable, "
            "one threshold, where we sit, and what flips us")
    if not short and not re.search(r"\bwrong\b|\bso am I\b", sp, re.I):
        add("WARN", "doc 35 rule 2",
            "the tell does not state what being wrong looks like")

    stats["pivot_pct"] = None
    return out, stats


def _sentence_span(words) -> list[dict]:
    """Take words off the iterator up to and including the sentence end."""
    out: list[dict] = []
    for w in words:
        out.append(w)
        if w["w"].endswith((".", "!", "?")):
            break
    return out


def _measured_opening(findings: list[Finding], stats: dict, timings: list[dict],
                      deferred: bool) -> list[Finding]:
    """Swap the estimated hook / paradox rows for the recorded ones. When the
    opening gate owns beats 1-4 (`deferred`) only the stats are recorded."""
    rest = iter(timings)
    hook = _sentence_span(rest)
    if hook:
        t_hook = hook[-1]["end"] - hook[0]["start"]
        stats["hook_measured_s"] = round(t_hook, 2)
        if not deferred:
            findings = [f for f in findings if "doc 38 beat 1" not in f.rule]
            if t_hook > 3.0:
                findings = findings + [Finding(
                    "FAIL", "doc 38 beat 1",
                    f"first sentence is {t_hook:.2f}s AS RECORDED "
                    f"(limit 3.0s) — measured, not estimated")]
    paradox = hook + _sentence_span(rest)
    if len(paradox) > len(hook):
        t_par = paradox[-1]["end"] - paradox[0]["start"]
        stats["paradox_measured_s"] = round(t_par, 2)
        if not deferred:
            findings = [f for f in findings if "doc 38 beat 2" not in f.rule
                        or "banned opener" in f.message]
            if t_par > 8.0:
                findings = findings + [Finding(
                    "FAIL", "doc 38 beat 2",
                    f"microhook not paid until {t_par:.2f}s AS RECORDED "
                    f"(gate 8.0s)")]
    return findings


def _pivot_pin(findings: list[Finding], stats: dict, text: str,
               pivot: str) -> list[Finding]:
    """doc 38 sec 3: the verbatim P4 anchor is unique and sits in the pin."""
    hits = text.count(pivot)
    if hits != 1:
        return findings + [Finding("FAIL", "doc 38 sec 3",
                                   f"pivot anchor not unique ({hits} hits)")]
    i = text.index(pivot)
    pct = len(spoken(text[:i])) / len(spoken(text)) * 100
    stats["pivot_pct"] = round(pct, 1)
    lo, hi = PIVOT_PIN
    if lo <= pct <= hi:
        return findings
    return findings + [Finding(
        "FAIL", "doc 38 sec 3 phase 4",
        f"pivot at {pct:.1f}% breaks the {lo:g}-{hi:g}% pin")]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path)
    ap.add_argument("--pivot", help="verbatim anchor for the phase-4 pivot")
    ap.add_argument("--short", action="store_true", help="G2: the shorts shape - doc 35 rule 2 and the P1 pin do not bind")
    args = ap.parse_args()

    text = args.script.read_text(encoding="utf-8")
    findings, stats = audit(text, script_path=args.script, short=args.short)
    if args.short:
        stats["mode"] = "short (G2)"
    deferred = gate_report(args.script) is not None

    # If a take exists, measure the tight gates instead of estimating them.
    first = sentences(spoken(text))[0] if sentences(spoken(text)) else ""
    timings = load_timings(args.script, first)
    if timings:
        stats["timing_source"] = f"measured ({len(timings)} words on disk)"
        findings = _measured_opening(findings, stats, timings, deferred)
    else:
        vo = args.script.parent / "vo"
        stale = any(vo.glob("scene_*.words.json"))
        stats["timing_source"] = (
            "estimated (a take exists but is of DIFFERENT text — not used)"
            if stale else "estimated (no take on disk)")

    if args.pivot:
        findings = _pivot_pin(findings, stats, text, args.pivot)

    print(f"=== {args.script.name} ===")
    for key, val in stats.items():
        print(f"  {key:>16}: {val}")
    print()
    order = {"FAIL": 0, "WARN": 1, "INFO": 2}
    for f in sorted(findings, key=lambda f: order[f.level]):
        print(f"  [{f.level}] {f.rule}: {f.message}")
    fails = sum(1 for f in findings if f.level == "FAIL")
    warns = sum(1 for f in findings if f.level == "WARN")
    print(f"\nRESULT: {fails} FAIL, {warns} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

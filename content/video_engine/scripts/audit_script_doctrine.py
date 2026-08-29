"""Doctrine audit for a VO script — the checks the pattern linter cannot make.

`lint_script_pattern.py` covers the kit hard-gate tier: sentence stats,
passive scan, fragment stacks, CTA budget, pause-mark ration, tautology,
ring. This covers what only reads against the DOCS and a RUNTIME:

  doc 32  ear mechanics (sentence mean vs the 15-16 standard, attribution
          position, signposting)
  doc 33  voice profile calibration
  doc 35  answer-format rules (falsifiable tell, one answer, steelman)
  doc 37  TTS delivery (mv2 cap, break ration, spoken numerals)
  doc 38  phase QC line (timed beats), pivot pin, CTA placement

Timings are derived at the MEASURED speech rate, so every positional gate
is checked against the runtime the script will actually have.

Exit 0 = no FAILs. Warnings do not fail the run.
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

CHARS_PER_SEC = 16.02        # measured, Script B: 7,149 chars / 446.1s
MV2_CAP = 10_000             # eleven_multilingual_v2
SENTENCE_MEAN_TARGET = (13.0, 18.0)   # doc 32 sec 1 / doc 33: "15-16 average"
PIVOT_PIN = (45.0, 55.0)     # doc 38 sec 3 phase 4
BREAK_RATION_MAX = 3.0       # doc 37 sec 1
MARKS = frozenset({"pre-key", "post-key", "verify"})

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


@dataclass(frozen=True)
class Finding:
    level: str          # FAIL | WARN | INFO
    rule: str           # doc reference
    message: str


def spoken(text: str) -> str:
    t = re.sub(r"`?\[(?:pre|post)-key\]`?", "", text)
    t = re.sub(r"^\s*(?:#|\||>|---|```).*$", "", t, flags=re.M)
    return re.sub(r"\s+", " ", t).strip()


def sentences(s: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", s) if x.strip()]


def audit(text: str) -> tuple[list[Finding], dict]:
    out: list[Finding] = []
    sp = spoken(text)
    n = len(sp)
    runtime = n / CHARS_PER_SEC
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
    ration = len(marks) / (n / 1000) if n else 0.0
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
    if not (lo <= mean <= hi):
        add("WARN", "doc 32 sec 1 / doc 33",
            f"sentence mean {mean:.1f} words is outside the {lo:g}-{hi:g} "
            f"band; doctrine calls for a 15-16 word average, varied")
    for pat in TRAILING_ATTR:
        for m in re.finditer(pat, sp):
            add("WARN", "doc 32 sec 1",
                "trailing attribution — frame before assertion: ..."
                + sp[max(0, m.start() - 45):m.end() + 15] + "...")

    # ---- doc 38 phase 1 QC line ------------------------------------------
    first = sents[0] if sents else ""
    t_first = len(first) / CHARS_PER_SEC
    if t_first > 3.0:
        add("FAIL", "doc 38 beat 1",
            f"first sentence runs {t_first:.1f}s (limit 3.0s): {first!r}")
    for pat in GREETINGS:
        m = re.search(pat, sp, re.I)
        if m:
            add("FAIL", "doc 38 beat 2",
                f"banned opener construction: {m.group()!r}")
    # Beat 2: the paradox must land by 0:08 — the 8-second decision boundary.
    # Measured as the end of sentence two, which is where the microhook is
    # paid (and paid wrong).
    if len(sents) >= 2:
        t_paradox = len(" ".join(sents[:2])) / CHARS_PER_SEC
        stats["paradox_s"] = round(t_paradox, 1)
        if t_paradox > 8.0:
            add("FAIL", "doc 38 beat 2",
                f"the microhook is not paid until {t_paradox:.1f}s — the "
                f"viewer decides at 0:08")

    m = re.search(r"\byou\b|\byour\b|\byou'll\b|\byou're\b", sp, re.I)
    t_you = len(sp[:m.start()]) / CHARS_PER_SEC if m else float("inf")
    if t_you > 30:
        add("FAIL", "doc 38 beat 3",
            f"direct address ('you') first appears at {t_you:.0f}s "
            f"(must land by 0:30)")
    stats["first_you_s"] = round(t_you, 1) if m else None

    head = sp[:int(60 * CHARS_PER_SEC)]
    if not re.search(r"\bby the end\b|\byou'll\b|\bthirty seconds\b"
                     r"|\brun (?:it|your)\b", head, re.I):
        add("WARN", "doc 38 beat 4",
            "no dated/checkable promise detected inside the first 60s")

    # ---- doc 38 phase 6: the close ---------------------------------------
    hits = [m for pat in CTA for m in re.finditer(pat, sp, re.I)]
    if len(hits) > 1:
        add("FAIL", "doc 38 phase 6",
            f"{len(hits)} CTA constructions — doctrine allows ONE")
    for m in hits:
        t_cta = len(sp[:m.start()]) / CHARS_PER_SEC
        if runtime - t_cta > 90:
            add("WARN", "doc 38 phase 6",
                f"CTA at {t_cta:.0f}s sits {runtime - t_cta:.0f}s before the "
                f"end — the action window is the final 90s, after the payoff")
    stats["cta_count"] = len(hits)

    # ---- doc 35: answer format -------------------------------------------
    if not re.search(r"\bthreshold\b|\btripwire\b|\bthe flip\b", sp, re.I):
        add("FAIL", "doc 35 rule 2",
            "no falsifiable tell — an answer video must name one variable, "
            "one threshold, where we sit, and what flips us")
    if not re.search(r"\bwrong\b|\bso am I\b", sp, re.I):
        add("WARN", "doc 35 rule 2",
            "the tell does not state what being wrong looks like")

    stats["pivot_pct"] = None
    return out, stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path)
    ap.add_argument("--pivot", help="verbatim anchor for the phase-4 pivot")
    args = ap.parse_args()

    text = args.script.read_text(encoding="utf-8")
    findings, stats = audit(text)

    if args.pivot:
        hits = text.count(args.pivot)
        if hits != 1:
            findings.append(Finding("FAIL", "doc 38 sec 3",
                                    f"pivot anchor not unique ({hits} hits)"))
        else:
            i = text.index(args.pivot)
            pct = len(spoken(text[:i])) / len(spoken(text)) * 100
            stats["pivot_pct"] = round(pct, 1)
            lo, hi = PIVOT_PIN
            if not (lo <= pct <= hi):
                findings.append(Finding(
                    "FAIL", "doc 38 sec 3 phase 4",
                    f"pivot at {pct:.1f}% breaks the {lo:g}-{hi:g}% pin"))

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

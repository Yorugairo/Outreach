"""ALIGN A TAKE: local Whisper word-timestamps for an engine that ships none.

E70 (docs/portable/VOICE-PACK.md, OPERATOR-RULINGS.md): Chirp does not ship
on YouTube and does fine on Facebook, so a one-shot renders BOTH takes for
the data. Kokoro carries its own word timestamps out of the pipeline
(scratch_take.py:run_kokoro); Chirp carries none, so a Chirp clock has to be
ALIGNED after the fact. Whisper runs LOCALLY - never a cloud STT call, never
a paid API, per the operator's standing constraint (see MEMORY.md
"Local Whisper, no paid STT"). This tool is that local aligner.

Output schema matches a take's own words.json exactly (scratch_take.py
run_kokoro, ~line 170-173; consumed by authoring/words.py:take_words):
    {"engine": str, "voice": str, "duration_s": float,
     "words": [{"w": str, "start_s": float, "end_s": float}, ...]}
With --script the payload also carries
    "aligned": {"matched": int, "interpolated": int, "script_tokens": int}

A stop belongs to its word ("once." is ONE token, not "once" + "."):
reused from scratch_take.merge_punct rather than re-implemented (the
docstring there already promises this is every consumer's shape).

Usage:
    align_take.py <audio> --out <words.json> [--script <txt>]
                  [--model small.en] [--engine <name>]

THE LIMIT, measured on the day it was written (2026-09-12): free-form ASR is
not an authoring clock. On the same audio, faster-whisper `small.en` returned
141 words where kokoro's own tokenizer had 155, and the last word's end lagged
by 0.84 s. A shot table anchors its rows on PHRASES (`authoring/words.at`), so
a clock missing one word in eleven cannot carry them.

THE FIX (R26-69): FORCED ALIGNMENT TO THE SCRIPT. With --script the output's
words ARE the script's spoken tokens, in order, exactly (beat marks stripped
the way scratch_take.load_script strips them, split on whitespace, a stop kept
on its word); only their TIMES come from the recogniser:
  1. Both sides are expanded to normalised UNITS: lowercase, hyphens and dashes
     split, punctuation dropped, and digits spelled as the script spells them
     (`word_units`): a decimal reads digit by digit after "point" ("4.83" ->
     four point eight three), a plain four-digit number in 1100-2099 reads as
     a YEAR ("1981" -> nineteen eighty one, "1905" -> nineteen oh five,
     2000-2009 -> two thousand five), any other integer reads as a cardinal
     without "and" ("123" -> one hundred twenty three, "1,200" -> one
     thousand two hundred), "%" -> percent, and "$" -> dollars, spoken after
     a following scale word ("$1.2 trillion" -> one point two trillion
     dollars). faster-whisper often splits a number into fragments ("4"
     ".66", "5" "%", "$1" ".2" "trillion"); a ".66" fragment reads as point
     six six, a lone "%" as percent, and a "$" carries its "dollars" past its
     fraction fragments to the scale word. A recogniser word's span is split
     across its units by character length.
  2. The two unit sequences are aligned globally (Needleman-Wunsch). A pair
     counts as a MATCH when the units are equal, or share their first four
     letters (an inflection the recogniser misheard: "defaulting" for
     "defaulted"). A script token with any matched unit takes the span of its
     matched units.
  3. A run of script tokens with no match takes times INTERPOLATED across the
     gap between its matched neighbours, split by character length; a gap too
     short to hold the run borrows its neighbours' spans and re-splits them
     with it. A leading or trailing run is sized by the take's own seconds per
     character. The result is monotone and never overlaps.
Without --script the tool behaves exactly as before (raw recognition).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scratch_take import merge_punct  # noqa: E402  (local import, see sys.path above)

BEAT_MARK = re.compile(r"`?\[[a-z0-9_-]+\]`?")   # mirrors scratch_take.load_script (a test pins the parity)
NUMBER = re.compile(r"^(\$?)(\d[\d,]*)(?:\.(\d+))?(%?)$")
FRACTION = re.compile(r"^\.(\d+)(%?)$")         # a recogniser fragment: "4" ".66" is four point six six
SPLITTERS = re.compile(r"[-‐-―/]+")
NON_WORD = re.compile(r"[^a-z0-9$%.,]")
SCALES = ("thousand", "million", "billion", "trillion")
ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
        "sixteen seventeen eighteen nineteen").split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()

MATCH_SCORE = 2
NEAR_SCORE = 1
MISMATCH_SCORE = -1
GAP_SCORE = -1
NEAR_PREFIX = 4          # units sharing this many leading letters count as a (near) match
MIN_WORD_S = 0.06        # an interpolated word shorter than this means the gap cannot hold its run
FALLBACK_S_PER_CHAR = 0.07


# ---- the script's tokens ---------------------------------------------------------------------------------

def strip_beat_marks(text: str) -> str:
    return BEAT_MARK.sub("", text)


def script_tokens(text: str) -> list[str]:
    """The spoken tokens, in order: beat marks off, split on whitespace, a stop kept on its word."""
    dummy = [{"w": t, "start_s": 0.0, "end_s": 0.0} for t in strip_beat_marks(text).split()]
    return [w["w"] for w in merge_punct(dummy)]


# ---- digits to words -------------------------------------------------------------------------------------

def _under_thousand(n: int) -> list[str]:
    out: list[str] = []
    if n >= 100:
        out += [ONES[n // 100], "hundred"]
        n %= 100
    if n >= 20:
        out.append(TENS[n // 10])
        n %= 10
        if n:
            out.append(ONES[n])
    elif n or not out:
        out.append(ONES[n])
    return out


def cardinal(n: int) -> list[str]:
    if n < 1000:
        return _under_thousand(n)
    out: list[str] = []
    for power, name in zip((12, 9, 6, 3), reversed(SCALES)):
        chunk = (n // 10 ** power) % 1000
        if chunk:
            out += _under_thousand(chunk) + [name]
    rest = n % 1000
    return out + (_under_thousand(rest) if rest else [])


def year_words(n: int) -> list[str]:
    hi, lo = divmod(n, 100)
    if lo == 0:
        return _under_thousand(hi) + ["hundred"]
    return _under_thousand(hi) + (["oh", ONES[lo]] if lo < 10 else _under_thousand(lo))


def number_units(text: str) -> list[str] | None:
    """Digits as the script writes them, or None when `text` is not a number (see the module docstring)."""
    m = NUMBER.match(text)
    if not m:
        return None
    dollar, whole, frac, pct = m.groups()
    n = int(whole.replace(",", ""))
    is_year = "," not in whole and len(whole) == 4 and 1100 <= n <= 2099 and not 2000 <= n <= 2009
    units = year_words(n) if (is_year and frac is None and not dollar and not pct) else cardinal(n)
    if frac is not None:
        units += ["point"] + [ONES[int(d)] for d in frac]
    return units + (["percent"] if pct else []) + (["dollars"] if dollar else [])


def word_units(word: str) -> list[str]:
    """A token's normalised units: lowercase, split on hyphens, punctuation off, digits spelled out.
    A FRAGMENT of a number the recogniser split off ("4" ".66", "5" "%") reads as its spoken tail:
    ".66" -> point six six, "%" -> percent."""
    units: list[str] = []
    for piece in SPLITTERS.split(word.lower()):
        piece = NON_WORD.sub("", piece).rstrip(".,")
        tail = FRACTION.match(piece)
        if tail:
            units += ["point"] + [ONES[int(d)] for d in tail.group(1)] + (["percent"] if tail.group(2) else [])
            continue
        if piece == "%":
            units.append("percent")
            continue
        spelled = number_units(piece.lstrip(".,"))
        if spelled is not None:
            units += spelled
            continue
        piece = re.sub(r"[^a-z0-9]", "", piece)
        if piece:
            units.append(piece)
    return units


def recognised_units(words: list[dict]) -> list[tuple[str, float, float]]:
    """The recogniser's words as (unit, start_s, end_s): each word's span split across its units by length.
    A "$" amount says "dollars" after its fraction fragments and after a following scale word."""
    per_word = [word_units(w["w"]) for w in words]
    for i, w in enumerate(words):
        if "$" not in w["w"] or per_word[i][-1:] != ["dollars"]:
            continue
        j = i + 1
        while j < len(words) and per_word[j][:1] == ["point"]:
            j += 1
        home = j if j < len(words) and per_word[j][:1] and per_word[j][0] in SCALES else j - 1
        if home != i:
            per_word[i] = per_word[i][:-1]
            per_word[home] = per_word[home] + ["dollars"]
    out: list[tuple[str, float, float]] = []
    for w, units in zip(words, per_word):
        out += _split_span(units, w["start_s"], w["end_s"])
    return out


def _split_span(units: list[str], start: float, end: float) -> list[tuple[str, float, float]]:
    total = sum(len(u) for u in units) or 1
    out, t = [], start
    for u in units:
        nxt = t + (end - start) * len(u) / total
        out.append((u, t, nxt))
        t = nxt
    return out


# ---- the alignment ---------------------------------------------------------------------------------------

def _pair_score(a: str, b: str) -> tuple[int, bool]:
    if a == b:
        return MATCH_SCORE, True
    if len(a) >= NEAR_PREFIX and len(b) >= NEAR_PREFIX and a[:NEAR_PREFIX] == b[:NEAR_PREFIX]:
        return NEAR_SCORE, True
    return MISMATCH_SCORE, False


def align_units(a: list[str], b: list[str]) -> list[tuple[int, int]]:
    """Needleman-Wunsch over two unit sequences; the (i, j) pairs that MATCH, in order."""
    n, m = len(a), len(b)
    score = [[j * GAP_SCORE for j in range(m + 1)]]
    move = [[2] * (m + 1)]                       # 0 diagonal, 1 up (gap in b), 2 left (gap in a)
    for i in range(1, n + 1):
        row, mv = [i * GAP_SCORE], [1]
        prev = score[i - 1]
        for j in range(1, m + 1):
            diag = prev[j - 1] + _pair_score(a[i - 1], b[j - 1])[0]
            up, left = prev[j] + GAP_SCORE, row[j - 1] + GAP_SCORE
            best = max(diag, up, left)
            row.append(best)
            mv.append(0 if best == diag else (1 if best == up else 2))
        score.append(row)
        move.append(mv)
    pairs: list[tuple[int, int]] = []
    i, j = n, m
    while i > 0 and j > 0:
        step = move[i][j]
        if step == 0:
            if _pair_score(a[i - 1], b[j - 1])[1]:
                pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif step == 1:
            i -= 1
        else:
            j -= 1
    return pairs[::-1]


def _matched_spans(tokens: list[str], rec: list[tuple[str, float, float]]) -> list[list[float] | None]:
    owners, units = [], []
    for k, tok in enumerate(tokens):
        for u in word_units(tok):
            owners.append(k)
            units.append(u)
    spans: list[list[float] | None] = [None] * len(tokens)
    for i, j in align_units(units, [u for u, _, _ in rec]):
        k, (_, s, e) = owners[i], rec[j]
        spans[k] = [s, e] if spans[k] is None else [min(spans[k][0], s), max(spans[k][1], e)]
    return spans


def _char_len(token: str) -> int:
    return max(1, sum(len(u) for u in word_units(token)) or len(token))


def _seconds_per_char(tokens: list[str], spans, duration_s: float) -> float:
    done = [(k, sp) for k, sp in enumerate(spans) if sp is not None]
    chars = sum(_char_len(tokens[k]) for k, _ in done)
    if chars and sum(sp[1] - sp[0] for _, sp in done) > 0:
        return sum(sp[1] - sp[0] for _, sp in done) / chars
    total = sum(_char_len(t) for t in tokens)
    return duration_s / total if duration_s > 0 and total else FALLBACK_S_PER_CHAR


def _fill(spans, lens: list[int], a: int, b: int, lo: float, hi: float) -> None:
    total, t = sum(lens[a:b]), lo
    for k in range(a, b):
        nxt = t + (hi - lo) * lens[k] / total
        spans[k] = [t, nxt]
        t = nxt
    spans[b - 1][1] = hi


def _interpolate(tokens: list[str], spans, duration_s: float) -> None:
    lens = [_char_len(t) for t in tokens]
    rate = _seconds_per_char(tokens, spans, duration_s)
    n, k = len(tokens), 0
    while k < n:
        if spans[k] is not None:
            k += 1
            continue
        a = k
        while k < n and spans[k] is None:
            k += 1
        b, need = k, sum(lens[a:k]) * rate
        left = spans[a - 1][1] if a > 0 else None
        right = spans[b][0] if b < n else None
        if left is None and right is None:
            _fill(spans, lens, a, b, 0.0, duration_s if duration_s > 0 else need)
        elif left is None:
            _fill(spans, lens, a, b, max(0.0, right - need), right)
        elif right is None:
            hi = left + need if duration_s <= left else min(left + need, duration_s)
            _fill(spans, lens, a, b, left, hi)
        elif right - left >= MIN_WORD_S * (b - a):
            _fill(spans, lens, a, b, left, right)
        else:                                    # no room: re-split the neighbours' spans with the run
            _fill(spans, lens, a - 1, b + 1, spans[a - 1][0], spans[b][1])


def force_align(tokens: list[str], rec_words: list[dict], duration_s: float) -> tuple[list[dict], dict]:
    """The script's tokens with the recogniser's times; (words, {"matched", "interpolated", "script_tokens"})."""
    spans = _matched_spans(tokens, recognised_units(rec_words))
    matched = sum(sp is not None for sp in spans)
    _interpolate(tokens, spans, duration_s)
    words, prev_end = [], 0.0
    for tok, (s, e) in zip(tokens, spans):
        s = max(s, prev_end)
        e = max(e, s)
        words.append({"w": tok, "start_s": round(s, 3), "end_s": round(e, 3)})
        prev_end = e
    stats = {"matched": matched, "interpolated": len(tokens) - matched, "script_tokens": len(tokens)}
    return words, stats


def build_payload(engine: str, duration_s: float, words: list[dict], stats: dict) -> dict:
    return {"engine": f"{engine}-aligned", "voice": "aligned/faster-whisper", "duration_s": duration_s,
            "words": words, "aligned": stats}


# ---- the recogniser (local only) -------------------------------------------------------------------------

def _load_whisper():
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise SystemExit(
            "align_take.py needs faster-whisper for local word-level "
            "timestamps and it is not installed in this interpreter. "
            "Install it with: pip install faster-whisper "
            "(no cloud STT call is ever made by this tool)."
        ) from e
    return WhisperModel


def transcribe(audio_path: Path, model_name: str) -> tuple[list[dict], float]:
    """Run local faster-whisper with word_timestamps=True; return
    (words, duration_s) in the take schema's word shape (pre-merge_punct)."""
    WhisperModel = _load_whisper()
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(audio_path), word_timestamps=True, beam_size=5,
    )
    words: list[dict] = []
    duration_s = 0.0
    for seg in segments:
        for w in seg.words or []:
            words.append({
                "w": w.word.strip(),
                "start_s": round(w.start, 3),
                "end_s": round(w.end, 3),
            })
            duration_s = max(duration_s, w.end)
    return words, round(duration_s, 2)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("audio", type=Path, help="mp3/wav of the take")
    ap.add_argument("--out", type=Path, required=True,
                     help="words.json to write")
    ap.add_argument("--script", type=Path, default=None,
                     help="the take's own script text: force-align the output's words to its tokens")
    ap.add_argument("--model", default="small.en",
                     help="faster-whisper model name (default small.en)")
    ap.add_argument("--engine", default=None,
                     help="engine name to record (default: the audio stem)")
    args = ap.parse_args()

    if not args.audio.exists():
        raise SystemExit(f"audio not found: {args.audio}")
    if args.script is not None and not args.script.exists():
        raise SystemExit(f"script not found: {args.script}")

    words, duration_s = transcribe(args.audio, args.model)
    words = merge_punct(words)
    engine = args.engine or args.audio.stem
    n_recognised = len(words)

    if args.script is None:
        payload = {"engine": engine, "voice": "aligned/faster-whisper",
                   "duration_s": duration_s, "words": words}
    else:
        tokens = script_tokens(args.script.read_text(encoding="utf-8"))
        words, stats = force_align(tokens, words, duration_s)
        payload = build_payload(engine, duration_s, words, stats)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"{args.out} written: {len(words)} words, duration_s={duration_s}")
    if args.script is not None:
        a = payload["aligned"]
        print(f"forced to the script: {a['script_tokens']} script tokens | recogniser heard "
              f"{n_recognised} | matched {a['matched']} | interpolated {a['interpolated']}")


if __name__ == "__main__":
    main()

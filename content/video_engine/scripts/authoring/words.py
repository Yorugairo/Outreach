"""The authoring kit - WORDS: the take is the clock, and every row is anchored on a PHRASE.

A shot row is never typed from a stopwatch: it names the words it belongs to and the kit reads
their times out of the take. M13 is the law for a cut - it lands at CUT_AT of the gap before the
next phrase, and a gap under MIN_GAP is not a cut point at all.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CUT_AT = 0.8          # M13: the cut sits at 0.8 of the gap before the next phrase
MIN_GAP = 0.30        # M13: a gap shorter than this is not a cut point
SENTENCE_ENDS = (".", "!", "?", ":")   # what closes a caption sentence in `timeline.json`
HARD_STOPS = ".?!"                     # ... and what closes a SPOKEN sentence (a colon runs on)
QUOTE_TAIL = "\"”"                # a closing quote may sit after the stop


def take_words(project) -> list[dict]:
    """The take's words (start_s / end_s) - a list, or a dict with a `words` key."""
    d = json.loads((project.take / f"{project.take_stem}.words.json").read_text(encoding="utf-8"))
    return d["words"] if isinstance(d, dict) else d


def shifted_words(project) -> list[dict]:
    """The words AFTER the edit pauses (`<build>/timeline.json`, start / end) in the take's shape."""
    tl = json.loads((project.build / "timeline.json").read_text(encoding="utf-8"))
    return [{"w": w["w"], "start_s": w["start"], "end_s": w["end"]} for w in tl["words"]]


def _norm(s: str) -> str:
    return s.strip(".,:;!?\"'").lower()


def phrase_start(ws: list[dict], phrase: str) -> tuple[int, float]:
    """Index and start time of the word that opens `phrase` (punctuation-insensitive)."""
    toks = [_norm(x) for x in phrase.split()]
    for i in range(len(ws) - len(toks) + 1):
        if [_norm(x["w"]) for x in ws[i:i + len(toks)]] == toks:
            return i, ws[i]["start_s"]
    raise SystemExit(f"phrase not in the take: {phrase!r}")


def word_time(ws: list[dict], phrase: str) -> float:
    """The raw start of the word that opens `phrase`."""
    return phrase_start(ws, phrase)[1]


def at(ws: list[dict], phrase: str) -> float:
    """A row anchor: the start of `phrase`, rounded the way a shot table writes it."""
    return round(word_time(ws, phrase), 2)


def word_in(ws: list[dict], phrase: str, word: str, window: int = 10) -> float:
    """The start of `word` inside the `window` words that open at `phrase` - for a beat that lands
    mid-phrase (a snap on the verb, a dock on the noun)."""
    i0 = phrase_start(ws, phrase)[0]
    return next(round(w["start_s"], 2) for w in ws[i0:][:window] if w["w"].strip(".,;:!?").lower() == word)


def cut_before(ws: list[dict], phrase: str, cut_at: float = CUT_AT, min_gap: float = MIN_GAP) -> float:
    """The cut time before `phrase`: `cut_at` of the gap after the previous word (M13). A gap under
    `min_gap` is refused by name - the beat has to move, never the words (the gate-fit ruling)."""
    i, start = phrase_start(ws, phrase)
    if i == 0:
        return 0.0
    prev_end = ws[i - 1]["end_s"]
    gap = start - prev_end
    if gap < min_gap:
        raise SystemExit(f"no cut point before {phrase!r}: gap {gap:.2f}s < {min_gap}s (M13)")
    return round(prev_end + cut_at * gap, 2)


def next_sentence_start(ws: list[dict], t: float) -> float | None:
    """The start of the first word of the NEXT sentence after t - the take's own punctuation is the
    boundary. E25: a chart proves ONE sentence, so a held light releases on the first word of the
    next one. None = no sentence ends after t."""
    seen_end = False
    for w in ws:
        if w["start_s"] < t:
            continue
        if seen_end:
            return round(w["start_s"], 2)
        if w["w"].rstrip()[-1:] in HARD_STOPS:
            seen_end = True
    return None


def split_sentences(out_words: list[dict], part: int = 1) -> list[dict]:
    """The caption builder's sentences: a word that closes on `. ! ? :` closes the sentence."""
    sents: list[dict] = []
    cur: list[dict] = []
    for w in out_words:
        cur.append(w)
        if w["w"].rstrip(QUOTE_TAIL).endswith(SENTENCE_ENDS):
            sents.append({"text": " ".join(x["w"] for x in cur), "start": cur[0]["start"], "end": cur[-1]["end"], "part": part})
            cur = []
    if cur:
        sents.append({"text": " ".join(x["w"] for x in cur), "start": cur[0]["start"], "end": cur[-1]["end"], "part": part})
    return sents


def write_timeline(project, ws: list[dict], runtime_s: float) -> dict:
    """`<build>/timeline.json` in the shape the caption-page builder and the compiler read (one part)."""
    out_words = [{"w": w["w"], "start": round(w["start_s"], 3), "end": round(w["end_s"], 3), "part": 1} for w in ws]
    tl = {"episode": project.episode_id, "script": project.script_name, "take": project.take_name,
          "runtime_s": runtime_s, "words": out_words, "sentences": split_sentences(out_words),
          "edit_pauses_applied": False}
    (project.build / "timeline.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")
    return tl


def read_timeline(project) -> dict:
    return json.loads((project.build / "timeline.json").read_text(encoding="utf-8"))


def save_timeline(project, tl: dict) -> dict:
    (project.build / "timeline.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")
    return tl


def apply_edit_pauses(project, plan_file: Path) -> dict:
    """The OWED room at the cut points (doc 37: silence over the settle lives in the editor's
    timeline). `insert_edit_pauses` rewrites `timeline.json` and names the paused audio on it;
    the take is raw on purpose, so the tighten check is skipped."""
    import insert_edit_pauses as IP
    IP.EP, IP.BUILD, IP.PLAN_FILE = project.here, project.build, plan_file
    sys.argv = [sys.argv[0], "--skip-tighten-check"]
    if IP.main() != 0:
        raise SystemExit("edit pauses failed")
    return read_timeline(project)

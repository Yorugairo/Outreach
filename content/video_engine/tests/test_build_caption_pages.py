"""THE CAPTION PAGES BREAK AT THE PUNCTUATION (E41 #3; one-shot #3, 2026-09-16 - the operator: "the captions are wrong").

The pins: a page never runs past a word that ends a sentence, whatever the gap after it (a retimed take caps its gaps under the
builder's GAP_BREAK); a page breaks at a clause mark once it holds three words; the budget and the word cap still hold.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import build_caption_pages as CP  # noqa: E402


def _words(text: str, step: float = 0.3, gap: float = 0.05) -> list[dict]:
    out, t = [], 0.0
    for w in text.split():
        out.append({"w": w, "start": round(t, 2), "end": round(t + step, 2)})
        t += step + gap            # every gap far under GAP_BREAK: only the punctuation can break a page
    return out


def _pages(tmp_path: Path, text: str, budget: int = 28, max_words: int = 6) -> list[list[str]]:
    (tmp_path / "timeline.json").write_text(json.dumps({"words": _words(text)}), encoding="utf-8")
    CP.BUILD, CP.CHAR_BUDGET, CP.MAX_WORDS = tmp_path, budget, max_words
    CP.main()
    return [[t["w"] for t in p["t"]] for p in json.loads((tmp_path / "caption-pages.json").read_text(encoding="utf-8"))]


def test_a_page_never_runs_past_a_sentence_end(tmp_path: Path) -> None:
    pages = _pages(tmp_path, "Memory stocks don't trade the news. They trade the calendar. Around the fifteenth of every month, it lands.")
    for page in pages:
        assert not any(w.endswith(CP.SENTENCE_END) for w in page[:-1]), page   # a sentence end is always the page's last word
    assert pages[0] == ["Memory", "stocks", "don't", "trade"]   # the 28-char budget breaks first ...
    assert pages[1] == ["the", "news."]                          # ... and the sentence end closes the next page
    assert pages[2] == ["They", "trade", "the", "calendar."]


def test_a_page_breaks_at_a_clause_once_it_holds_a_phrase(tmp_path: Path) -> None:
    pages = _pages(tmp_path, "In the half-month after: plus two point two. The move is front-run.")
    assert pages[0] == ["In", "the", "half-month", "after:"]
    assert ["plus", "two", "point", "two."] in pages


def test_the_budget_and_the_word_cap_still_break(tmp_path: Path) -> None:
    pages = _pages(tmp_path, "one two three four five six seven eight nine ten", budget=100, max_words=4)
    assert [len(p) for p in pages] == [4, 4, 2]


# ---- R26-278 (P72 T14): a quote belongs to the word it OPENS, not the one before it ---------------------------
# The take's aligner writes every straight quote onto the word BEFORE it (H's `And"` `don't` ... `top"`; `of"` `the`
# `market."`; `target-date,"` `the` `market"—`), so the page read `And" don't try to call the` (237 s) - a typo on
# screen. The quote's side is the stream's own parity: a straight quote that OPENS (none is open) rides the word
# after it; one that CLOSES stays on the word it ends. Only the character moves - every word keeps its own clock.


def _page_words(tmp_path: Path, words: list[str]) -> list[list[str]]:
    ws = [{"w": w, "start": round(0.3 * i, 2), "end": round(0.3 * i + 0.25, 2)} for i, w in enumerate(words)]
    (tmp_path / "timeline.json").write_text(json.dumps({"words": ws}), encoding="utf-8")
    CP.BUILD, CP.CHAR_BUDGET, CP.MAX_WORDS = tmp_path, 34, 6
    CP.main()
    return [[t["w"] for t in p["t"]] for p in json.loads((tmp_path / "caption-pages.json").read_text(encoding="utf-8"))]


def test_an_opening_quote_rides_the_word_it_opens(tmp_path: Path) -> None:
    pages = _page_words(tmp_path, ['theirs.', 'And"', "don't", 'try', 'to', 'call', 'the', 'top"', 'is', 'the',
                                   'most', 'honest'])
    assert pages[1][:3] == ["And", '"don\'t', "try"], pages     # `And "don't try` on screen, never `And" don't`
    assert 'top"' in [w for p in pages for w in p], pages        # the closing quote stays on the word it ends


def test_the_quote_parity_runs_through_a_closing_mark_after_punctuation(tmp_path: Path) -> None:
    flat = [w for p in _page_words(tmp_path, ["erases", "ten", "percent", 'of"', "the", 'market."', "The", "other",
                                              'target-date,"', "the", 'market"—', "but"]) for w in p]
    assert flat == ["erases", "ten", "percent", "of", '"the', 'market."', "The", "other", "target-date,", '"the',
                    'market"—', "but"], flat


def test_a_curly_quote_already_on_its_word_is_untouched_and_the_clock_never_moves(tmp_path: Path) -> None:
    words = ["he", "said", "“stop”", "and", "left."]
    assert [w for p in _page_words(tmp_path, words) for w in p] == words
    ws = [{"w": w, "start": round(0.3 * i, 2), "end": round(0.3 * i + 0.25, 2)} for i, w in enumerate(['a', 'b"', 'c', 'd"'])]
    (tmp_path / "timeline.json").write_text(json.dumps({"words": ws}), encoding="utf-8")
    CP.main()
    got = [t for p in json.loads((tmp_path / "caption-pages.json").read_text(encoding="utf-8")) for t in p["t"]]
    assert [(t["w"], t["s"], t["e"]) for t in got] == [("a", 0.0, 0.25), ("b", 0.3, 0.55), ('"c', 0.6, 0.85),
                                                        ('d"', 0.9, 1.15)]

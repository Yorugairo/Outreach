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

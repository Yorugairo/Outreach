from __future__ import annotations

from pathlib import Path

from content.video_engine.scripts.lint_script_pattern import lint_script, main


CONFORMANT = """
**[till plate, drawer sounds under]**

She counts the drawer while the bank across the street counts its bonus.
`[post-key]` The difference between them fits on a single receipt, and
tonight you will calculate yours.

**[the apartment, morning light]**

But here's where it gets weird. The receipt shows one price, and the
second price hides underneath it. According to the landlord's own ledger,
the machine costs forty dollars a month in rent.

So the receipt closes this story where it opened it. Read the second line
of the receipt tonight.
"""


def _codes(report):
    return {finding.code for finding in report.failures}


def test_conformant_script_passes_all_gates():
    report = lint_script(CONFORMANT)

    assert report.failures == ()
    assert report.ok


def test_sentence_mean_gate_fails_on_run_ons():
    long_sentence = (
        "The banker walked into the apartment and looked at the television "
        "and the espresso machine and the rowing machine and the suit rack "
        "and the watch box and wondered where all of the money had gone "
        "over the last several years of his career in finance."
    )
    text = " ".join([long_sentence] * 4) + " The receipt stays. " + long_sentence

    report = lint_script(text + " The receipt returns here.")

    assert "SENTENCE_MEAN" in _codes(report)


def test_passive_ratio_gate_flags_passive_stacks():
    text = (
        "The receipt was printed by the register. "
        "The apartment was filled with boxes. "
        "The bonus was decided by a committee. "
        "The lease was signed in a good year. "
        "The receipt was kept in the drawer."
    )

    report = lint_script(text)

    assert "PASSIVE_RATIO" in _codes(report)


def test_fragment_stack_detected():
    text = (
        "The receipt tells the story of the apartment in a single line. "
        "He pays. She saves. It grows. They wait. "
        "The receipt returns at the end of the story for the close."
    )

    report = lint_script(text)

    assert "FRAGMENT_STACK" in _codes(report)


def test_cta_count_gate_fails_on_three_asks():
    text = (
        "The receipt opens the story with a single number on the table. "
        "Subscribe for the next rule in the series. "
        "Tell me in the comments what your number was yesterday. "
        "And hit the like button on your way past the receipt."
    )

    report = lint_script(text)

    assert "CTA_COUNT" in _codes(report)


def test_triple_ask_fails_even_in_one_sentence():
    text = (
        "The receipt opens this story with one number on the kitchen table. "
        "Like, comment, and subscribe before the receipt closes the story."
    )

    report = lint_script(text)

    assert "CTA_TRIPLE" in _codes(report)


def test_pause_mark_ration_enforced():
    text = (
        "The receipt lands. [post-key] The drawer opens. [post-key] "
        "The bonus clears. [pre-key] The lease renews. [post-key] "
        "The receipt stays on the table. [post-key]"
    )

    report = lint_script(text)

    assert "PAUSE_RATION" in _codes(report)


def test_unknown_mark_rejected():
    text = (
        "The receipt opens the story with one number on the table. "
        "[pause] The receipt closes the story with the same number."
    )

    report = lint_script(text)

    assert "UNKNOWN_MARK" in _codes(report)


def test_markdown_links_are_not_marks():
    text = (
        "The receipt opens the story with a single number on the table. "
        "See [the ledger](https://example.com) for the receipt arithmetic."
    )

    report = lint_script(text)

    assert "UNKNOWN_MARK" not in _codes(report)


def test_tautology_gate_flags_captioned_visuals():
    text = """
**[the banker counts his bonus at the trading desk]**

The banker counts his bonus at the trading desk in lower Manhattan today.
The receipt sits beside the terminal while the banker counts the bonus.

The receipt closes the story tonight.
"""

    report = lint_script(text)

    assert "TAUTOLOGY" in _codes(report)


def test_ring_gate_fails_without_shared_token():
    text = (
        "The banker counts a bonus at a trading desk in lower Manhattan.\n\n"
        "Something else happens in the middle of the video for a while.\n\n"
        "Buy index funds quietly and patiently forever without any drama."
    )

    report = lint_script(text)

    assert "RING" in _codes(report)


def test_rehook_positions_reported_in_stats():
    report = lint_script(CONFORMANT)

    assert report.stats["rehook_positions_pct"], "expected at least one rehook"
    assert all(0 <= p <= 100 for p in report.stats["rehook_positions_pct"])


def test_main_returns_zero_on_clean_and_one_on_findings(tmp_path: Path, capsys):
    clean = tmp_path / "clean.md"
    clean.write_text(CONFORMANT, encoding="utf-8")
    dirty = tmp_path / "dirty.md"
    dirty.write_text(
        "The receipt opens the story. [pause] The receipt closes the story.",
        encoding="utf-8",
    )

    assert main([str(clean)]) == 0
    assert main([str(dirty)]) == 1
    output = capsys.readouterr().out
    assert "UNKNOWN_MARK" in output

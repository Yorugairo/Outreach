"""The recall receipt, P67 T3: the mechanism list, the two line forms, and the span re-read off disk.

Every case is a real event. The 2026-09-16 caption fix changed how every caption page is built and the hook
printed "no mechanism touched"; P67's own grammar is the staged `Recall(<stage>):` line, which the 2026-09-08
regex refused; and CITATION IS NOT GROUNDING - a `path:line` with a quoted span is re-read through
`recall_verify`, while a line with no span keeps the old path-exists check so older commits still pass.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("recall_receipt", REPO / "scripts/hooks/recall_receipt.py")
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

CAPTIONS = "content/video_engine/scripts/build_caption_pages.py"
AUTHORING = "content/video_engine/scripts/authoring/table.py"
A_DOC = "docs/runbooks/RECALL-RECEIPT.md"
SPAN = "the exact words here"


def a_repo(tmp_path: Path) -> Path:
    """A tiny repo whose `docs/x.md` carries the span on line 3, and nowhere else."""
    doc = tmp_path / "docs" / "x.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("# a title\n\n" + SPAN + " and more\n\nthe tail\n", encoding="utf-8")
    return tmp_path


def test_the_caption_fix_with_no_recall_line_is_refused():
    """2026-09-16: the caption builder changed and the hook said "no mechanism touched"."""
    ok, why = H.check("fix(captions): the page builder stops clipping the last word", [CAPTIONS])
    assert not ok
    assert CAPTIONS in why and "no `Recall:` line" in why


def test_the_caption_fix_with_a_path_only_recall_line_passes():
    ok, why = H.check("fix(captions): the page builder\n\nRecall: " + A_DOC, [CAPTIONS])
    assert ok and "receipt ok" in why


def test_an_authoring_kit_path_is_a_mechanism():
    ok, why = H.check("feat(kit): the table grows a column", [AUTHORING])
    assert not ok and AUTHORING in why


def test_a_non_mechanism_path_passes_with_no_mechanism_touched():
    ok, why = H.check("docs: a note", [A_DOC])
    assert ok and why == "no mechanism touched"


def test_the_staged_form_with_the_span_on_the_cited_line_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(H, "REPO", a_repo(tmp_path))
    msg = 'fix(captions): the page builder\n\nRecall(motion): docs/x.md:3 "' + SPAN + '" (the line)\n'
    ok, why = H.check(msg, [CAPTIONS])
    assert ok, why
    assert "1 span(s) re-read off disk" in why


def test_a_wrong_span_is_refused_naming_the_cited_line(tmp_path, monkeypatch):
    monkeypatch.setattr(H, "REPO", a_repo(tmp_path))
    msg = 'fix(captions): x\n\nRecall(motion): docs/x.md:3 "words that were never written"\n'
    ok, why = H.check(msg, [CAPTIONS])
    assert not ok
    assert "line 3" in why and "REFUSED" in why


def test_a_span_cited_at_the_wrong_line_names_where_it_moved_to(tmp_path, monkeypatch):
    monkeypatch.setattr(H, "REPO", a_repo(tmp_path))
    msg = 'fix(captions): x\n\nRecall(motion): docs/x.md:1 "' + SPAN + '"\n'
    ok, why = H.check(msg, [CAPTIONS])
    assert not ok
    assert "line 1" in why and "moved to docs/x.md:3" in why


def test_a_spanless_line_keeps_the_path_exists_check(tmp_path, monkeypatch):
    """Backward compatible: the pre-P67 commits carry no span, and a quote in the NOTE is not a span."""
    ok, why = H.check("fix(captions): x\n\nRecall: " + A_DOC + ':12 (the "second receipt" section)\n', [CAPTIONS])
    assert ok and "re-read off disk" not in why
    ok, why = H.check("fix(captions): x\n\nRecall: docs/nope/missing.md:4\n", [CAPTIONS])
    assert not ok and "does not exist in the record" in why


def test_the_zero_hit_form_still_passes():
    ok, why = H.check("fix(captions): x\n\nRecall: docs_find 0 hits for caption-gutter\n", [CAPTIONS])
    assert ok and "receipt ok" in why
    ok, why = H.check('fix(captions): x\n\nRecall(world): docs_find 0 hits for "caption-gutter"\n', [CAPTIONS])
    assert ok and "receipt ok" in why


def test_a_broken_verifier_never_blocks_a_commit(tmp_path, monkeypatch):
    """The hook is not allowed to refuse a commit over its own plumbing - one notice, then the old check."""
    monkeypatch.setattr(H, "REPO", a_repo(tmp_path))

    def boom():
        raise ImportError("recall_verify.py is not in this checkout")

    monkeypatch.setattr(H, "_load_verifier", boom)
    msg = 'fix(captions): x\n\nRecall(motion): docs/x.md:3 "' + SPAN + '"\n'
    ok, why = H.check(msg, [CAPTIONS])
    assert ok, why
    assert why.count("span check skipped") == 1 and "recall_verify.py is not in this checkout" in why
    assert why.splitlines()[0].startswith("note:") and "receipt ok" in why


def run_hook(message: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "scripts/hooks/recall_receipt.py", "--message", message, CAPTIONS],
                          cwd=str(REPO), capture_output=True, text=True)


def test_the_hook_end_to_end_refuses_the_caption_fix_without_a_receipt():
    out = run_hook("fix(captions): the page builder stops clipping the last word")
    assert out.returncode == 1, out.stdout
    assert "REFUSED" in out.stdout and CAPTIONS in out.stdout


def test_the_hook_end_to_end_passes_with_a_receipt():
    out = run_hook("fix(captions): the page builder\n\nRecall: " + A_DOC)
    assert out.returncode == 0, out.stdout
    assert "receipt ok" in out.stdout

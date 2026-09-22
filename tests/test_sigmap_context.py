from __future__ import annotations

from scripts import sigmap_context


def test_generated_context_headers_use_portable_path_separators(
    tmp_path, monkeypatch
) -> None:
    github = tmp_path / ".github"
    github.mkdir()
    context = github / "context-content.md"
    context.write_text(
        "## content\n\n"
        "### content\\video_engine\\scripts\\measure_page_boxes.py\n"
        "```\n"
        "def measure()  :1-2\n"
        "```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(sigmap_context, "PROJECT_ROOT", tmp_path)

    sigmap_context._normalize_generated_context_paths()

    assert (
        "### content/video_engine/scripts/measure_page_boxes.py"
        in context.read_text(encoding="utf-8")
    )

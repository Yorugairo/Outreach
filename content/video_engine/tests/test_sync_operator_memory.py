"""Tests for sync_operator_memory.py (P54 T4): link transform, idempotency, check, prune, secret scan."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import sync_operator_memory as som  # noqa: E402


def _memory(name: str, body: str) -> str:
    return f"---\r\nname: {name}\r\ndescription: test\r\n---\r\n\r\n{body}\r\n"


def _seed(src: Path) -> None:
    src.mkdir()
    (src / "MEMORY.md").write_bytes(b"- [Alpha](alpha-file.md) - index line\r\n")
    (src / "alpha-file.md").write_bytes(_memory("alpha", "See [[beta]] and [[ghost]].").encode("utf-8"))
    (src / "beta-file.md").write_bytes(_memory("beta", "Back to [[alpha]].").encode("utf-8"))


def _run(src: Path, dst: Path, *flags: str) -> int:
    return som.main(["--src", str(src), "--dst", str(dst), *flags])


def test_link_transform_existing_and_missing_slug(tmp_path: Path) -> None:
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed(src)

    assert _run(src, dst, "--export") == 0

    alpha = (dst / "alpha-file.md").read_bytes().decode("utf-8")
    assert "See [beta](beta-file.md) and `ghost` (not yet written)." in alpha
    assert alpha.startswith("---\r\nname: alpha\r\n")  # frontmatter and CRLF kept
    assert (dst / "MEMORY.md").read_bytes() == (src / "MEMORY.md").read_bytes()


def test_export_is_idempotent(tmp_path: Path) -> None:
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed(src)
    _run(src, dst, "--export")
    first = {p.name: p.read_bytes() for p in dst.iterdir()}

    assert _run(src, dst, "--export") == 0

    assert {p.name: p.read_bytes() for p in dst.iterdir()} == first


def test_check_passes_then_fails_after_source_edit(tmp_path: Path, capsys) -> None:
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed(src)
    _run(src, dst, "--export")

    assert _run(src, dst, "--check") == 0
    assert "in sync (3 files)" in capsys.readouterr().out

    (src / "beta-file.md").write_bytes(_memory("beta", "Edited.").encode("utf-8"))
    assert _run(src, dst, "--check") == 1
    assert "drifted: beta-file.md" in capsys.readouterr().out


def test_extra_destination_file_reported_not_deleted_unless_prune(tmp_path: Path, capsys) -> None:
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed(src)
    _run(src, dst, "--export")
    (dst / "stale.md").write_text("old", encoding="utf-8")
    (dst / "README.md").write_text("readme", encoding="utf-8")
    capsys.readouterr()

    _run(src, dst, "--export")
    out = capsys.readouterr().out
    assert "extra: stale.md" in out
    assert "README.md" not in out
    assert (dst / "stale.md").exists()
    assert _run(src, dst, "--check") == 1

    _run(src, dst, "--export", "--prune")
    assert not (dst / "stale.md").exists()
    assert (dst / "README.md").exists()
    assert _run(src, dst, "--check") == 0


def test_secret_scan_blocks_file_and_never_prints_value(tmp_path: Path, capsys) -> None:
    src, dst = tmp_path / "src", tmp_path / "dst"
    _seed(src)
    fake = "sk-" + "A1b2C3d4E5f6G7h8I9j0K1l2"
    (src / "leaky.md").write_text(_memory("leaky", f"key {fake}"), encoding="utf-8")

    code = _run(src, dst, "--export")

    captured = capsys.readouterr()
    assert code == 2
    assert not (dst / "leaky.md").exists()
    assert (dst / "alpha-file.md").exists()
    assert "leaky.md" in captured.out
    assert "openai_key" in captured.out
    assert fake not in captured.out + captured.err

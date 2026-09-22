from __future__ import annotations

from pathlib import Path

from scripts import configure_codex_skill_allowlist as allowlist


def _skill(root: Path, body: str, extra: str | None = None) -> Path:
    root.mkdir(parents=True)
    (root / "SKILL.md").write_text(body, encoding="utf-8")
    if extra is not None:
        (root / "references").mkdir()
        (root / "references" / "guide.md").write_text(extra, encoding="utf-8")
    return root


def test_prefers_shared_copy_when_duplicate_skills_are_identical(tmp_path, monkeypatch) -> None:
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", lambda: home)
    shared = _skill(home / ".agents" / "skills" / "same", "---\nname: same\n---\n")
    project = _skill(tmp_path / "repo" / ".agents" / "skills" / "same", "---\nname: same\n---\n")
    monkeypatch.setattr(allowlist, "REPO_ROOT", tmp_path / "repo")

    assert allowlist.preferred_active("same", [project, shared]) == shared


def test_prefers_project_variant_when_it_has_distinct_references(tmp_path, monkeypatch) -> None:
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", lambda: home)
    shared = _skill(home / ".agents" / "skills" / "variant", "---\nname: variant\n---\n")
    project = _skill(
        tmp_path / "repo" / ".agents" / "skills" / "variant",
        "---\nname: variant\n---\n",
        "project-specific guidance",
    )
    monkeypatch.setattr(allowlist, "REPO_ROOT", tmp_path / "repo")

    assert allowlist.preferred_active("variant", [shared, project]) == project


def test_prefers_richer_curated_hyperframes_root_when_variants_differ(tmp_path, monkeypatch) -> None:
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", lambda: home)
    project = _skill(tmp_path / "repo" / ".agents" / "skills" / "hyperframes", "project")
    plugin = _skill(home / ".codex" / "plugins" / "cache" / "hyperframes", "curated", "full guide")
    monkeypatch.setattr(allowlist, "REPO_ROOT", tmp_path / "repo")

    assert allowlist.preferred_active("hyperframes", [project, plugin]) == plugin

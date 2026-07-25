from pathlib import Path

from scripts.prp_validate import validate


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_prp_template_satisfies_current_contract() -> None:
    template = REPO_ROOT / ".claude" / "PRPs" / "templates" / "prp-template.md"

    assert validate(template) == []


def test_prp_validator_rejects_missing_contract(tmp_path: Path) -> None:
    incomplete = tmp_path / "incomplete.plan.md"
    incomplete.write_text("# Incomplete\n\n## Summary\n", encoding="utf-8")

    errors = validate(incomplete)

    assert any(error.startswith("missing frontmatter:") for error in errors)
    assert "missing task slices" in errors

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

def test_prp_validator_accepts_a_retired_plan(tmp_path: Path) -> None:
    """E99 s27: a plan withdrawn by the operator carries `status: retired`, not a false `complete`."""
    template = (REPO_ROOT / ".claude" / "PRPs" / "templates" / "prp-template.md").read_text(encoding="utf-8")
    retired = tmp_path / "retired.plan.md"
    retired.write_text(template.replace("status: draft", "status: retired", 1), encoding="utf-8")

    assert validate(retired) == []

    unknown = tmp_path / "unknown.plan.md"
    unknown.write_text(template.replace("status: draft", "status: shelved", 1), encoding="utf-8")

    assert "invalid status: shelved" in validate(unknown)

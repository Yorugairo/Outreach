from __future__ import annotations

from pathlib import Path

import pytest

from content.video_engine.src.services.paths import (
    DURABILITY_CLASSES,
    EXPORT_SUBPATH,
    QUARANTINE_DIR,
    PathContractError,
    canonical_dir,
    class_of,
    is_runtime_path,
    review_dir,
    runtime_dir,
)


def test_the_three_classes_are_fixed_and_ordered_by_durability():
    """canonical must survive hardware death; runtime is allowed to vanish."""

    assert DURABILITY_CLASSES == ("canonical", "review", "runtime")


def test_each_resolver_returns_an_absolute_path_under_its_class_root(tmp_path):
    assert canonical_dir(tmp_path) == tmp_path.resolve() / "canonical"
    assert review_dir(tmp_path, "batch-1") == tmp_path.resolve() / "review" / "batch-1"
    assert runtime_dir(tmp_path, "previews", "job-9") == (
        tmp_path.resolve() / "runtime" / "previews" / "job-9"
    )


def test_nested_parts_may_use_forward_slashes(tmp_path):
    assert review_dir(tmp_path, "claims/claim-1") == (
        tmp_path.resolve() / "review" / "claims" / "claim-1"
    )


@pytest.mark.parametrize("bad", ["..", "a/../b", "/absolute", "C:/drive", "back\\slash", ""])
def test_escape_attempts_are_named_errors_not_paths(tmp_path, bad):
    with pytest.raises(PathContractError) as excinfo:
        runtime_dir(tmp_path, bad)

    # The error names the offending part (repr may escape it) — never a path.
    assert "path part" in " ".join(excinfo.value.errors) or "empty" in " ".join(excinfo.value.errors)


def test_resolvers_do_no_io_unless_ensure_is_asked_for(tmp_path):
    target = runtime_dir(tmp_path, "quiet")
    assert not target.exists()

    ensured = runtime_dir(tmp_path, "made", ensure=True)
    assert ensured.is_dir()


def test_class_of_reads_the_class_from_the_path_alone(tmp_path):
    assert class_of("runtime/previews/x.png", tmp_path) == "runtime"
    assert class_of("review/batch-1/a.png", tmp_path) == "review"
    assert class_of(tmp_path / "canonical" / "plate.png", tmp_path) == "canonical"


def test_an_unclassified_path_is_refused_by_name(tmp_path):
    with pytest.raises(PathContractError) as excinfo:
        class_of("assets/generated/thing.png", tmp_path)

    joined = " ".join(excinfo.value.errors)
    assert "assets" in joined
    assert "durability class" in joined


def test_a_path_outside_the_project_is_refused(tmp_path):
    outside = tmp_path.parent / "elsewhere" / "runtime" / "x.png"

    with pytest.raises(PathContractError) as excinfo:
        class_of(outside, tmp_path)

    assert "outside" in " ".join(excinfo.value.errors)


def test_a_dotdot_escape_cannot_launder_itself_into_a_class(tmp_path):
    with pytest.raises(PathContractError):
        class_of("runtime/../../etc/passwd", tmp_path)


def test_is_runtime_path_generalises_the_preview_guard():
    """The rule composite_preview enforced locally, now owned centrally."""

    assert is_runtime_path(Path("engine/runtime/previews/x.png"))
    assert not is_runtime_path(Path("engine/canonical/x.png"))


def test_the_contract_owns_the_shared_subpath_literals():
    """Other modules import these; the strings live in exactly one place."""

    assert QUARANTINE_DIR == "renders/quarantine"
    assert EXPORT_SUBPATH == ("runtime", "generation-requests")

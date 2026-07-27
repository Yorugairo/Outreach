from src.services.ai_readiness_service import (
    AIReadinessV3Service,
    COHORT_WEIGHTS,
    DIMENSION_WEIGHTS,
)


def test_v3_preserves_frozen_dimension_and_cohort_weights():
    assert DIMENSION_WEIGHTS == {"aeo": 40.0, "geo": 35.0, "aio": 25.0}
    assert COHORT_WEIGHTS == {"core": 60.0, "supporting": 40.0}


def test_unknown_values_are_removed_from_score_arithmetic():
    service = AIReadinessV3Service()

    assert service._weighted_known(
        {"known": 80.0},
        {"known": 40.0, "unknown": 60.0},
    ) == 80.0
    assert service._weighted_known(
        {"known": 80.0},
        {"known": 40.0, "unknown": 60.0},
        missing_as_zero=True,
    ) == 32.0


def test_score_bands_are_stable_at_boundaries():
    service = AIReadinessV3Service()

    assert service._band(39.99) == "Needs foundational work"
    assert service._band(40) == "Developing"
    assert service._band(60) == "Solid"
    assert service._band(80) == "Strong"

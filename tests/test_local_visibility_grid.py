from src.models import LocalVisibilityGridDefinition
from src.services.local_visibility_service import LocalVisibilityService


def _grid(size=3):
    terms = [f"term-{i}" for i in range(3 if size == 3 else 5)]
    return LocalVisibilityGridDefinition(
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        location_code=1027773,
        center_latitude=47.2529,
        center_longitude=-122.4443,
        rows=size,
        columns=size,
        spacing_meters=1600,
        keyword_target_ids=terms,
        place_id="place-nova",
        approved_by="operator",
    ), terms


def test_teaser_and_premium_preflight_have_exact_call_ceilings():
    service = LocalVisibilityService()
    teaser, teaser_terms = _grid(3)
    premium, premium_terms = _grid(5)
    assert service.preflight(teaser, keywords=teaser_terms, snapshot_date="2026-07-26")["planned_calls"] == 27
    assert service.preflight(teaser, keywords=teaser_terms, snapshot_date="2026-07-26")["call_cap"] == 27
    assert service.preflight(premium, keywords=premium_terms, snapshot_date="2026-07-26")["planned_calls"] == 125
    assert service.preflight(premium, keywords=premium_terms, snapshot_date="2026-07-26")["call_cap"] == 125


def test_coordinates_are_deterministic_and_centered():
    grid, terms = _grid(3)
    points = LocalVisibilityService().coordinates(grid)
    assert [point["point_id"] for point in points] == ["r1c1", "r1c2", "r1c3", "r2c1", "r2c2", "r2c3", "r3c1", "r3c2", "r3c3"]
    center = next(point for point in points if point["point_id"] == "r2c2")
    assert center["latitude"] == grid.center_latitude
    assert center["longitude"] == grid.center_longitude


class FakeMaps:
    def __init__(self):
        self.calls = []

    def collect_maps_serp(self, keyword, **kwargs):
        self.calls.append((keyword, kwargs["latitude"], kwargs["longitude"]))
        return {
            "status": "complete",
            "snapshot_date": "2026-07-26",
            "results": [{"place_id": "place-nova", "rank": 2}],
            "provider_cost_usd": 0.01,
        }


def test_grid_collects_heatmap_cost_and_reuses_exact_evidence():
    grid, terms = _grid(3)
    provider = FakeMaps()
    service = LocalVisibilityService()
    first = service.collect(grid, provider, keywords=terms, snapshot_date="2026-07-26")
    assert first.status == "complete"
    assert len(provider.calls) == 27
    assert first.metrics["cost_usd"] == 0.27
    second = service.collect(grid, provider, keywords=terms, existing_evidence=first.checks, snapshot_date="2026-07-26")
    assert second.status == "complete"
    assert len(provider.calls) == 27
    assert second.metrics["reused_calls"] == 27
    assert second.metrics["cost_usd"] == 0


def test_grid_rejects_wrong_term_count():
    grid, _ = _grid(3)
    try:
        LocalVisibilityService().preflight(
            grid,
            keywords=["one", "two"],
            snapshot_date="2026-07-26",
        )
    except ValueError as exc:
        assert "exactly 3" in str(exc)
    else:
        raise AssertionError("grid accepted an unapproved term count")

"""Deterministic, geographically distributed Maps visibility grids."""

from __future__ import annotations

import math
from statistics import median
from typing import Any, Iterable, Mapping

from src.models import LocalVisibilityGridDefinition, PRODUCT_SURFACE_VERSIONS, ProductSurfaceResult


class LocalVisibilityService:
    """Collect and summarize approved 3x3/5x5 Maps grids.

    The service is provider-neutral and performs no call during ``preflight``.
    A teaser grid is three terms × nine points (27 calls); premium is five terms
    × twenty-five points (125 calls).  Existing evidence is reused only when
    every grid/context/place identity field matches exactly.
    """

    VERSION = PRODUCT_SURFACE_VERSIONS["local_visibility"]
    CALL_CAPS = {(3, 3): 27, (5, 5): 125}
    METERS_PER_LATITUDE_DEGREE = 111_320.0

    def __init__(self, provider: Any = None, repository: Any = None) -> None:
        self.provider = provider
        self.repository = repository

    def preflight(
        self,
        grid: LocalVisibilityGridDefinition | Mapping[str, Any],
        *,
        keywords: Iterable[str] | None = None,
        keyword_target_ids: Iterable[str] | None = None,
        reusable_evidence: Iterable[Mapping[str, Any]] | None = None,
        existing_evidence: Iterable[Mapping[str, Any]] | None = None,
        device: str | None = "desktop",
        language_code: str | None = "en",
        snapshot_date: str | None = None,
    ) -> dict[str, Any]:
        definition = self._grid(grid)
        if not snapshot_date:
            raise ValueError("local visibility preflight requires a snapshot date")
        if not device or not language_code:
            raise ValueError("local visibility preflight requires device and language")
        ids = list(keyword_target_ids or definition.keyword_target_ids)
        terms = [str(item).strip() for item in (keywords or ids) if str(item).strip()]
        expected_terms = 3 if definition.rows == 3 else 5
        if len(terms) != expected_terms:
            raise ValueError(f"{definition.rows}x{definition.columns} local grids require exactly {expected_terms} approved terms")
        cells = self.coordinates(definition)
        total = len(cells) * len(terms)
        evidence = [*(reusable_evidence or []), *(existing_evidence or [])]
        reusable = sum(1 for cell in cells for term in terms if self._find_reusable(evidence, definition, cell, term, device=device, language_code=language_code, snapshot_date=snapshot_date) is not None)
        return {
            "contract_version": self.VERSION,
            "grid_id": definition.id,
            "grid_identity_sha256": definition.identity_sha256,
            "rows": definition.rows,
            "columns": definition.columns,
            "grid_cells": len(cells),
            "keyword_count": len(terms),
            "planned_calls": total,
            "new_calls": total - reusable,
            "reusable_calls": reusable,
            "call_cap": self.CALL_CAPS[(definition.rows, definition.columns)],
            "conservative_max_cost_usd": round(total * 0.02, 6),
            "coordinates": cells,
        }

    def coordinates(self, grid: LocalVisibilityGridDefinition | Mapping[str, Any]) -> list[dict[str, Any]]:
        definition = self._grid(grid)
        center_row = (definition.rows + 1) / 2
        center_col = (definition.columns + 1) / 2
        cos_lat = max(0.01, math.cos(math.radians(definition.center_latitude)))
        lat_step = definition.spacing_meters / self.METERS_PER_LATITUDE_DEGREE
        lon_step = definition.spacing_meters / (self.METERS_PER_LATITUDE_DEGREE * cos_lat)
        output: list[dict[str, Any]] = []
        for row in range(1, definition.rows + 1):
            for column in range(1, definition.columns + 1):
                latitude = definition.center_latitude + (center_row - row) * lat_step
                longitude = definition.center_longitude + (column - center_col) * lon_step
                output.append({
                    "point_id": f"r{row}c{column}",
                    "row": row,
                    "column": column,
                    "latitude": round(latitude, 7),
                    "longitude": round(longitude, 7),
                })
        return output

    grid_coordinates = coordinates

    def collect(
        self,
        grid: LocalVisibilityGridDefinition | Mapping[str, Any],
        provider: Any = None,
        *,
        keywords: Iterable[str] | None = None,
        keyword_target_ids: Iterable[str] | None = None,
        existing_evidence: Iterable[Mapping[str, Any]] | None = None,
        evidence: Iterable[Mapping[str, Any]] | None = None,
        market_run: Any = None,
        device: str = "desktop",
        language_code: str = "en",
        snapshot_date: str | None = None,
    ) -> ProductSurfaceResult:
        provider = provider or self.provider
        if provider is None:
            raise ValueError("local visibility collection requires a provider")
        coordinate_collector = getattr(
            provider,
            "collect_maps_serp_at_coordinate",
            None,
        )
        if coordinate_collector is None:
            coordinate_collector = getattr(provider, "collect_maps_serp", None)
        if not callable(coordinate_collector):
            raise ValueError(
                "local visibility provider lacks coordinate-bound Maps collection"
            )
        definition = self._grid(grid)
        terms = [str(item).strip() for item in (keywords or keyword_target_ids or definition.keyword_target_ids) if str(item).strip()]
        target_ids = list(keyword_target_ids) if keyword_target_ids is not None else list(definition.keyword_target_ids)
        plan = self.preflight(definition, keywords=terms, keyword_target_ids=target_ids, reusable_evidence=[*(existing_evidence or []), *(evidence or [])], device=device, language_code=language_code, snapshot_date=snapshot_date)
        prior = [dict(item) for item in [*(existing_evidence or []), *(evidence or [])] if isinstance(item, Mapping)]
        cells: list[dict[str, Any]] = []
        actual_cost = 0.0
        reusable_count = 0
        provider_calls = 0
        for point in self.coordinates(definition):
            for index, term in enumerate(terms):
                target_id = target_ids[index] if index < len(target_ids) else term
                old = self._find_reusable(prior, definition, point, term, device=device, language_code=language_code, snapshot_date=snapshot_date)
                if old is not None:
                    cell = {**old, "status": "reused", "reused": True, "point_id": point["point_id"], "keyword": term, "keyword_target_id": target_id}
                    reusable_count += 1
                else:
                    provider_calls += 1
                    try:
                        response = coordinate_collector(
                            term,
                            location_code=definition.location_code,
                            language_code=language_code,
                            device=device,
                            latitude=point["latitude"],
                            longitude=point["longitude"],
                            depth=20,
                        )
                        response = dict(response or {})
                        status = "complete" if response.get("status", "complete") in {"complete", "success", "completed"} else "unknown"
                        cost = self._cost(response.get("provider_cost_usd"))
                        actual_cost += cost
                        cell = {
                            "status": status,
                            "reused": False,
                            "grid_id": definition.id,
                            "grid_identity_sha256": definition.identity_sha256,
                            "point_id": point["point_id"],
                            "row": point["row"],
                            "column": point["column"],
                            "latitude": point["latitude"],
                            "longitude": point["longitude"],
                            "keyword": term,
                            "keyword_target_id": target_id,
                            "place_id": definition.place_id,
                            "market": definition.market,
                            "location_code": definition.location_code,
                            "language_code": language_code,
                            "device": device,
                            "snapshot_date": response.get("snapshot_date") or snapshot_date,
                            "rank": self._rank(response, definition.place_id),
                            "results": response.get("results", []),
                            "provider_cost_usd": cost,
                            "raw_artifact_ref": response.get("raw_artifact_ref"),
                        }
                    except TypeError as exc:
                        raise ValueError(
                            "local visibility provider rejected coordinate-bound arguments"
                        ) from exc
                    except Exception as exc:  # provider failures remain unknown evidence
                        cell = {
                            "status": "unknown",
                            "reused": False,
                            "grid_id": definition.id,
                            "grid_identity_sha256": definition.identity_sha256,
                            "point_id": point["point_id"],
                            "row": point["row"],
                            "column": point["column"],
                            "latitude": point["latitude"],
                            "longitude": point["longitude"],
                            "keyword": term,
                            "keyword_target_id": target_id,
                            "place_id": definition.place_id,
                            "market": definition.market,
                            "location_code": definition.location_code,
                            "language_code": language_code,
                            "device": device,
                            "snapshot_date": snapshot_date,
                            "rank": None,
                            "provider_cost_usd": 0.0,
                            "error": f"{type(exc).__name__}: {str(exc)[:240]}",
                        }
                cells.append(cell)

        expected = len(cells)
        complete = sum(1 for item in cells if item.get("status") == "complete" or item.get("status") == "reused")
        completeness = complete / expected * 100 if expected else 0.0
        status = "complete" if complete == expected else "partial" if complete else "unknown"
        ranks = [int(item["rank"]) for item in cells if isinstance(item.get("rank"), int | float)]
        top3 = sum(1 for rank in ranks if rank <= 3)
        top10 = sum(1 for rank in ranks if rank <= 10)
        metrics = {
            "contract_version": self.VERSION,
            "grid_id": definition.id,
            "grid_identity_sha256": definition.identity_sha256,
            "grid_definition": definition.to_dict(),
            "coordinates": self.coordinates(definition),
            "keyword_count": len(terms),
            "cell_count": len(cells),
            "top_3_coverage_percent": round(top3 / expected * 100, 4) if expected else 0.0,
            "top_10_coverage_percent": round(top10 / expected * 100, 4) if expected else 0.0,
            "top_3_coverage": round(top3 / expected * 100, 4) if expected else 0.0,
            "top_10_coverage": round(top10 / expected * 100, 4) if expected else 0.0,
            "median_observed_rank": float(median(ranks)) if ranks else None,
            "median_rank": float(median(ranks)) if ranks else None,
            "heatmap": [{"point_id": item["point_id"], "keyword": item["keyword"], "rank": item.get("rank"), "status": item["status"]} for item in cells],
            "heatmap_cells": [{"point_id": item["point_id"], "keyword": item["keyword"], "rank": item.get("rank"), "status": item["status"]} for item in cells],
            "cost_usd": round(actual_cost, 6),
            "provider_cost_usd": round(actual_cost, 6),
            "provider_calls": provider_calls,
            "reused_calls": reusable_count,
            "planned_calls": expected,
            "call_cap": plan["call_cap"],
            "completeness": {"expected": expected, "successful": complete, "unresolved": expected - complete, "reused": reusable_count},
            "completeness_percent": round(completeness, 4),
            "scoring_separation": "Local Visibility evidence never mutates Technical SEO Health, AI Readiness, or Conversion Readiness.",
        }
        result = ProductSurfaceResult(surface="local_visibility", version=self.VERSION, status=status, score=None, completeness_percent=round(completeness, 4), evidence_confidence=round(completeness, 4), metrics=metrics, checks=cells, warnings=[] if status == "complete" else ["One or more Maps grid cells are unresolved; local visibility remains partial or unknown."])
        if market_run is not None:
            market_run.maps_evidence.extend(cells)
            market_run.actual_provider_cost = round(float(getattr(market_run, "actual_provider_cost", 0.0)) + actual_cost, 6)
            market_run.artifact_refs.append({"kind": "local_visibility", "contract_version": self.VERSION, "grid_id": definition.id, "grid_identity_sha256": definition.identity_sha256, "metrics": metrics})
            repository = getattr(self, "repository", None)
            if repository is not None:
                repository.save_market_evidence_run(market_run)
        return result

    run = collect
    collect_grid = collect

    @staticmethod
    def _grid(value: LocalVisibilityGridDefinition | Mapping[str, Any]) -> LocalVisibilityGridDefinition:
        if isinstance(value, LocalVisibilityGridDefinition):
            return value
        return LocalVisibilityGridDefinition(**dict(value))

    @staticmethod
    def _cost(value: Any) -> float:
        return 0.0 if isinstance(value, bool) or not isinstance(value, int | float) else max(0.0, float(value))

    @staticmethod
    def _rank(response: Mapping[str, Any], place_id: str) -> int | None:
        rows = response.get("results") if isinstance(response.get("results"), list) else []
        ranks = [int(item.get("rank") or item.get("rank_group") or item.get("rank_absolute")) for item in rows if isinstance(item, Mapping) and item.get("place_id") == place_id and isinstance(item.get("rank") or item.get("rank_group") or item.get("rank_absolute"), int | float)]
        return min(ranks) if ranks else None

    @staticmethod
    def _find_reusable(evidence: Iterable[Mapping[str, Any]], grid: LocalVisibilityGridDefinition, point: Mapping[str, Any], keyword: str, *, device: str | None = None, language_code: str | None = None, snapshot_date: str | None = None) -> dict[str, Any] | None:
        for item in evidence:
            if not isinstance(item, Mapping):
                continue
            if item.get("grid_identity_sha256") != grid.identity_sha256 or item.get("place_id") != grid.place_id:
                continue
            if str(item.get("keyword") or "").casefold() != keyword.casefold() or item.get("point_id") != point.get("point_id"):
                continue
            if item.get("latitude") != point.get("latitude") or item.get("longitude") != point.get("longitude"):
                continue
            if device is not None and item.get("device") != device:
                continue
            if language_code is not None and item.get("language_code") != language_code:
                continue
            if snapshot_date is not None and item.get("snapshot_date") != snapshot_date:
                continue
            if item.get("status") not in {"complete", "success", "completed", "reused"}:
                continue
            return dict(item)
        return None


def local_grid_preflight(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return LocalVisibilityService().preflight(*args, **kwargs)


LocalVisibilityGridService = LocalVisibilityService


__all__ = ["LocalVisibilityService", "LocalVisibilityGridService", "local_grid_preflight"]

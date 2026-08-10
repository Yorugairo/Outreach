from __future__ import annotations

import copy
from datetime import UTC, date, datetime

import pytest

from content.video_engine.src.services.finance_channel import FinanceChannelValidationError, validate_artifact
from content.video_engine.src.services.finance_market_data import (
    FinanceMarketDataError,
    collect_market_data_packet,
    default_current_bubble_instruments,
    validate_market_bound_numeric_evidence,
)


def _fetcher(ticker: str, _start: date, _end: date, _basis: str):
    prices = {"MU": (10.0, 85.8), "^GSPC": (100.0, 124.0), "^KS11": (100.0, 195.0)}
    first, last = prices[ticker]
    return [{"date": "2025-12-31", "close": first}, {"date": "2026-08-07", "close": last}]


def test_market_data_packet_calculates_returns_from_stored_observations() -> None:
    packet = collect_market_data_packet(
        episode_id="current-bubble-mechanism",
        instruments=default_current_bubble_instruments(),
        start=date(2025, 12, 31),
        end=date(2026, 8, 7),
        fetcher=_fetcher,
        retrieved_at=datetime(2026, 8, 7, 18, 0, tzinfo=UTC),
    )
    assert [row["return_pct"] for row in packet["instruments"]] == [758.0, 24.0, 95.0]
    assert packet["price_basis"] == "adjusted_close"
    assert validate_artifact(packet)["schema_version"] == "finance_market_data_packet.v1"


def test_market_data_packet_rejects_tampered_return() -> None:
    packet = collect_market_data_packet(
        episode_id="current-bubble-mechanism",
        instruments=default_current_bubble_instruments()[:1],
        start=date(2025, 12, 31),
        end=date(2026, 8, 7),
        fetcher=_fetcher,
        retrieved_at=datetime(2026, 8, 7, 18, 0, tzinfo=UTC),
    )
    tampered = copy.deepcopy(packet)
    tampered["instruments"][0]["return_pct"] = 999.0
    with pytest.raises(FinanceChannelValidationError, match="stale|does not match"):
        validate_artifact(tampered)


def test_market_data_packet_rejects_invalid_window() -> None:
    with pytest.raises(FinanceMarketDataError, match="end date"):
        collect_market_data_packet(
            episode_id="fixture",
            instruments=default_current_bubble_instruments()[:1],
            start=date(2026, 8, 8),
            end=date(2026, 8, 7),
            fetcher=_fetcher,
        )


def test_market_bound_numeric_evidence_rejects_display_drift() -> None:
    packet = collect_market_data_packet(
        episode_id="current-bubble-mechanism",
        instruments=default_current_bubble_instruments()[:1],
        start=date(2025, 12, 31),
        end=date(2026, 8, 7),
        fetcher=_fetcher,
        retrieved_at=datetime(2026, 8, 7, 18, 0, tzinfo=UTC),
    )
    register = {
        "items": [{
            "display_value": 758.0,
            "market_data_binding": {
                "packet_hash": packet["artifact_hash"], "instrument_id": "micron",
                "metric": "return_pct", "rounding_decimals": 1,
            },
        }]
    }
    validate_market_bound_numeric_evidence(register, packet)
    register["items"][0]["display_value"] = 757.9
    with pytest.raises(FinanceChannelValidationError, match="does not match"):
        validate_market_bound_numeric_evidence(register, packet)

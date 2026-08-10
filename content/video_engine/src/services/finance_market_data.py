"""Reproducible, provider-bound market-data packets for finance videos.

The service stores the observations used to calculate a return.  It does not
turn a live quote into editorial fact automatically: YFinance is an operational
snapshot provider, and material public claims still require the episode's
normal source/review gate.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime, timedelta
from typing import Any, Callable, Iterable, Mapping, Sequence

from content.video_engine.src.services.finance_channel import FinanceChannelValidationError, canonical_sha256, with_artifact_hash


class FinanceMarketDataError(ValueError):
    """Raised when a requested price window cannot form an auditable return."""


MarketHistoryFetcher = Callable[[str, date, date, str], Sequence[Mapping[str, Any]]]


def default_current_bubble_instruments() -> tuple[dict[str, str], ...]:
    """The episode's timely comparison set; no return is hard-coded here."""

    return (
        {"instrument_id": "micron", "ticker": "MU", "label": "Micron Technology", "market": "NASDAQ", "calendar": "NYSE/NASDAQ", "currency": "USD"},
        {"instrument_id": "sp500", "ticker": "^GSPC", "label": "S&P 500 Price Index", "market": "United States", "calendar": "NYSE", "currency": "USD"},
        {"instrument_id": "kospi", "ticker": "^KS11", "label": "KOSPI Composite Index", "market": "Korea", "calendar": "KRX", "currency": "KRW"},
    )


def yfinance_history_fetcher(ticker: str, start: date, end: date, price_basis: str) -> Sequence[Mapping[str, Any]]:
    """Fetch an inclusive date range while keeping yfinance an optional import."""

    try:
        import yfinance as yf
    except ImportError as exc:  # pragma: no cover - environment integration
        raise FinanceMarketDataError(
            "yfinance is not installed; install requirements before collecting live market data"
        ) from exc
    field = "Close" if price_basis == "close" else "Close"
    frame = yf.Ticker(ticker).history(
        start=start.isoformat(),
        end=(end + timedelta(days=1)).isoformat(),
        auto_adjust=price_basis == "adjusted_close",
        actions=False,
    )
    if frame is None or frame.empty:
        raise FinanceMarketDataError(f"yfinance returned no price history for {ticker}")
    return [
        {"date": index.date().isoformat(), "close": float(row[field])}
        for index, row in frame.iterrows()
        if float(row[field]) > 0
    ]


def _series_hash(observations: Iterable[Mapping[str, Any]]) -> str:
    canonical = json.dumps(list(observations), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def collect_market_data_packet(
    *,
    episode_id: str,
    instruments: Sequence[Mapping[str, str]],
    start: date,
    end: date,
    price_basis: str = "adjusted_close",
    fetcher: MarketHistoryFetcher = yfinance_history_fetcher,
    retrieved_at: datetime | None = None,
) -> dict[str, Any]:
    """Return an immutable calculation packet from stored start/end prices."""

    if end < start:
        raise FinanceMarketDataError("end date must be on or after start date")
    if price_basis not in {"adjusted_close", "close"}:
        raise FinanceMarketDataError("price_basis must be adjusted_close or close")
    rows: list[dict[str, Any]] = []
    for instrument in instruments:
        ticker = str(instrument["ticker"])
        observations = list(fetcher(ticker, start, end, price_basis))
        if len(observations) < 2:
            raise FinanceMarketDataError(f"{ticker} requires at least two observations")
        first, last = observations[0], observations[-1]
        start_price, end_price = float(first["close"]), float(last["close"])
        if start_price <= 0 or end_price <= 0:
            raise FinanceMarketDataError(f"{ticker} has a non-positive price")
        rows.append(
            {
                "instrument_id": str(instrument["instrument_id"]), "ticker": ticker,
                "label": str(instrument["label"]), "market": str(instrument["market"]),
                "calendar": str(instrument["calendar"]), "period_start": str(first["date"]), "period_end": str(last["date"]),
                "start_price": round(start_price, 8), "end_price": round(end_price, 8),
                "return_pct": round(((end_price / start_price) - 1) * 100, 6),
                "currency": str(instrument["currency"]), "observation_count": len(observations), "observations": observations,
                "raw_series_sha256": _series_hash(observations), "review_state": "snapshot_only",
                "secondary_source_note": "YFinance snapshot; confirm material public figures against the identified market-data or exchange source before promotion.",
            }
        )
    timestamp = retrieved_at or datetime.now(UTC)
    return with_artifact_hash(
        {
            "schema_version": "finance_market_data_packet.v1", "episode_id": episode_id, "provider": "yfinance",
            "retrieved_at": timestamp.isoformat().replace("+00:00", "Z"), "price_basis": price_basis, "instruments": rows,
        }
    )


def validate_market_data_packet(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate arithmetic and detect a price/return mismatch before a graphic uses it."""

    errors: list[str] = []
    ids: set[str] = set()
    for index, item in enumerate(payload.get("instruments", [])):
        if not isinstance(item, Mapping):
            continue
        label = f"instruments[{index}]"
        instrument_id = str(item.get("instrument_id"))
        if instrument_id in ids:
            errors.append(f"{label} instrument_id must be unique")
        ids.add(instrument_id)
        try:
            expected = round(((float(item["end_price"]) / float(item["start_price"])) - 1) * 100, 6)
            if abs(expected - float(item["return_pct"])) > 0.000001:
                errors.append(f"{label} return_pct does not match stored start/end prices")
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            errors.append(f"{label} cannot calculate a valid return")
        observations = item.get("observations", [])
        if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes, bytearray)):
            errors.append(f"{label} observations must be a series")
        else:
            if len(observations) != int(item.get("observation_count", -1)):
                errors.append(f"{label} observation_count does not match stored observations")
            elif _series_hash(observations) != str(item.get("raw_series_sha256") or ""):
                errors.append(f"{label} raw_series_sha256 does not match stored observations")
        if str(item.get("period_start")) > str(item.get("period_end")):
            errors.append(f"{label} period_start must precede period_end")
    declared = str(payload.get("artifact_hash") or "")
    if declared != canonical_sha256(payload):
        errors.append("artifact_hash is stale")
    if errors:
        raise FinanceChannelValidationError(errors)
    return dict(payload)


def validate_market_bound_numeric_evidence(
    numeric_register: Mapping[str, Any], market_packet: Mapping[str, Any]
) -> None:
    """Verify each market-bound display number against its immutable price packet."""

    validate_market_data_packet(market_packet)
    packet_hash = str(market_packet.get("artifact_hash") or "")
    instruments = {
        str(item.get("instrument_id")): item
        for item in market_packet.get("instruments", [])
        if isinstance(item, Mapping)
    }
    errors: list[str] = []
    for index, item in enumerate(numeric_register.get("items", [])):
        if not isinstance(item, Mapping):
            continue
        binding = item.get("market_data_binding")
        if not isinstance(binding, Mapping):
            continue
        label = f"items[{index}]"
        if str(binding.get("packet_hash") or "") != packet_hash:
            errors.append(f"{label} market packet hash does not match")
            continue
        instrument = instruments.get(str(binding.get("instrument_id") or ""))
        if instrument is None:
            errors.append(f"{label} market instrument is absent from packet")
            continue
        if binding.get("metric") != "return_pct":
            errors.append(f"{label} market metric is unsupported")
            continue
        decimals = binding.get("rounding_decimals")
        if not isinstance(decimals, int):
            errors.append(f"{label} rounding_decimals must be an integer")
            continue
        expected = round(float(instrument["return_pct"]), decimals)
        try:
            displayed = float(item.get("display_value"))
        except (TypeError, ValueError):
            errors.append(f"{label} market display value must be numeric")
            continue
        if displayed != expected:
            errors.append(f"{label} display value does not match packet return")
    if errors:
        raise FinanceChannelValidationError(errors)


__all__ = [
    "FinanceMarketDataError",
    "collect_market_data_packet",
    "default_current_bubble_instruments",
    "validate_market_bound_numeric_evidence",
    "validate_market_data_packet",
    "yfinance_history_fetcher",
]

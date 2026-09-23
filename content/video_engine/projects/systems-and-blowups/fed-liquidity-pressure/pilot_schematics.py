"""Episode-owned schematic declarations for the existing native flow painter.

No narration is generated, no data is invented, no asset is approved here.
The caller supplies the current validated take. Review diagnostics may explicitly
use estimated words; production may not. Carrier selection remains separate.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from authoring import words as W
import build_scene_timeline_f as B

HERE = Path(__file__).resolve().parent
REGION = {"kind": "region", "x0": .06, "y0": .23, "x1": .94, "y1": .78}


def _clock(words: list[dict], diagnostic: bool) -> None:
    if not words or (W.is_estimated(words) and not diagnostic):
        raise ValueError("schematics require current take words; estimates are diagnostic-only")
    previous = -1.
    for word in words:
        start, end = word.get("start_s"), word.get("end_s")
        if any(isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t)
               for t in (start, end)) or start < previous or start < 0 or end <= start:
            raise ValueError("invalid/non-monotonic word clock")
        previous = end


def _at(words: list[dict], phrase: str) -> float:
    # A repeated phrase must not silently resolve to the first occurrence.
    def norm(value: str) -> str:
        return (value.strip(".,:;!?\"'”’�")
                .replace("’", "").replace("'", "").replace("�", "")
                .replace("–", "-").lower())

    terms = [norm(token) for token in phrase.split() if norm(token)]
    normalized = [(token, index) for index, word in enumerate(words)
                  if (token := norm(str(word["w"]))) != ""]
    hits = [position for position in range(len(normalized) - len(terms) + 1)
            if [token for token, _ in normalized[position:position + len(terms)]] == terms]
    if len(hits) != 1:
        raise ValueError(f"schematic anchor must occur once: {phrase!r} ({len(hits)} matches)")
    return round(float(words[normalized[hits[0]][1]]["start_s"]), 3)


def _binding(claim_id: str) -> dict:
    path = HERE / "claims.v1.json"
    raw = path.read_bytes()
    document = json.loads(raw)
    claim = next(
        (
            claim
            for section in ("claims", "qualitative_claims")
            for claim in document.get(section, [])
            if claim.get("id") == claim_id
        ),
        None,
    )
    if claim is None:
        raise ValueError(f"missing schematic claim {claim_id}")
    binding = {"claim_id": claim_id, "claims_path": "claims.v1.json",
               "claims_sha256": hashlib.sha256(raw).hexdigest(),
               "constraints": list(claim["constraints"])}
    if "source" in claim:
        source = claim["source"]
        source_path = (HERE / source["path"]).resolve()
        if not source_path.is_relative_to(HERE.resolve()):
            raise ValueError("claim source escapes episode")
        if hashlib.sha256(source_path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"{claim_id} source digest mismatch")
        binding["source"] = dict(source)
    return binding


def _checked(spec: dict, span: list[float], **metadata) -> dict:
    return _checked_species([spec], span, "fed-schematic-review", **metadata)


def _checked_species(species: list[dict], span: list[float], plate: str, **metadata) -> dict:
    """Validate a sentence-earned collection against its native page grammar."""
    errors = B.validate_species(species, (0, 0, 0), plate)
    if errors:
        raise ValueError("; ".join(errors))
    for spec in species:
        if spec["at"] < span[0] or spec["at"] + spec["dur"] > span[1] + 1e-6:
            raise ValueError("schematic must fit its spoken scene; do not pad the take")
        if "swap" in spec and spec["swap"]["at"] + .75 > span[1]:
            raise ValueError("beneficiary swap does not finish before the owner callback")
    return {"status": "review_only", "span": span, "species": species, **metadata}


def formula(words: list[dict], *, diagnostic: bool = False) -> dict:
    """Establish the full expression, then retain it across its spoken terms."""
    _clock(words, diagnostic)
    start = _at(words, "One popular chart tries to compress")
    end = _at(words, "The Fed's June twenty twenty-five numbers show the difference.")
    if end - start < 3.0:
        raise ValueError("formula build has insufficient spoken room")
    return _checked({
        "kind": "flow", "at": start, "dur": end - start,
        "target": dict(REGION), "readability": "landscape-phone",
        "nodes": [{"id": "assets", "icon": "landmark", "label": "FED\nASSETS"},
                  {"id": "government", "icon": "coins", "label": "GOVERNMENT\nCASH"},
                  {"id": "overnight", "icon": "coins", "label": "MONEY-FUND\nOVERNIGHT CASH"}],
        "edges": [["assets", "government"], ["government", "overnight"]],
        "operators": ["-", "-"], "tag": "ANALYST PROXY",
    }, [start, end], title="THE NET-LIQUIDITY SHORTCUT",
        footer="Not an official Fed series · Not bank reserves",
        binding=_binding("C7"), clock_kind="diagnostic" if diagnostic else "caller_validated_take")


def accounts(words: list[dict], *, diagnostic: bool = False) -> dict:
    """Separate commercial deposits from Fed accounts; reverse only settlement.

    The deposit has no arrow to a Fed account. Its label changes beneficiary on
    the contractor sentence; the existing swap law is used, not a new scene.
    """
    _clock(words, diagnostic)
    start = _at(words, "Take a tax payment.")
    # First chip lands at the spoken deposit line (flow BOX_S * BOX_LEAD).
    draw_at = _at(words, "Your deposit falls.") - .9 * .55
    reverse_at = _at(words, "The government's account falls.")
    beneficiary_at = _at(words, "The contractor gets a deposit.")
    end = _at(words, "Our workshop owner's machine hasn't changed through any of this.")
    return _checked({
        "kind": "flow", "at": draw_at, "dur": end - draw_at,
        "target": dict(REGION), "readability": "landscape-phone",
        "nodes": [{"id": "deposit", "icon": "coins", "label": "YOUR DEPOSIT\nAT YOUR BANK\nFALLS"},
                  {"id": "reserves", "icon": "landmark", "label": "BANK RESERVES\nAT THE FED"},
                  {"id": "government", "icon": "landmark", "label": "GOV’T ACCOUNT\nAT THE FED"}],
        "edges": [["reserves", "government"]],
        "edge_states": [{"at": reverse_at, "edges": [["government", "reserves"]]}],
        "swap": {"at": beneficiary_at, "node": "deposit", "icon": "coins",
                 "label": "CONTRACTOR DEPOSIT\nAT THEIR BANK\nRISES"},
        "tag": "ILLUSTRATION · OTHER BALANCES FIXED",
    }, [start, end], title="FED ASSETS STAY UNCHANGED",
        footer="Accounting illustration · Federal Reserve, FEDS Note, Jan 14, 2026",
        binding=_binding("C6"), clock_kind="diagnostic" if diagnostic else "caller_validated_take")


def overnight_alternatives(words: list[dict], *, diagnostic: bool = False) -> dict:
    """Name the actual alternatives to ON RRP without inventing a yield series."""
    _clock(words, diagnostic)
    start = _at(words, "But money funds can earn money elsewhere, too.")
    end = _at(words, "Those withdrawals helped banks hold their ground while the Fed cut its own investments.")
    dur = end - start - .40
    if dur < 3.0:
        raise ValueError("alternative-destinations flow has insufficient spoken room")
    binding = _binding("C5-mechanism")
    return _checked({
        "kind": "flow", "at": start, "dur": dur,
        "target": dict(REGION), "readability": "landscape-phone",
        "nodes": [
            {"id": "funds", "icon": "coins", "label": "MONEY\nFUNDS"},
            {"id": "overnight", "icon": "landmark", "label": "ON RRP"},
            {"id": "treasuries", "icon": "coins", "label": "TREASURY\nBILLS"},
            {"id": "private", "icon": "coins", "label": "PRIVATE\nMARKETS"},
        ],
        # Every branch starts at the money-fund root. These are alternatives,
        # not a sequential path from ON RRP through bills into private markets.
        "edges": [["funds", "overnight"], ["funds", "treasuries"], ["funds", "private"]],
        "tag": "NAMED ALTERNATIVES · NO ALLOCATION",
        "alternative_destinations": ["ON RRP", "Treasury bills", "private markets"],
        "source_quote": "Dealer financing demand and money-fund ON RRP substitution affect repo funding.",
        "source_custody": {
            "binding": binding,
            "source_quote": "Dealer financing demand and money-fund ON RRP substitution affect repo funding.",
            "status": "source_verified",
            "no_allocation_inferred": True,
        },
    }, [start, end], title="WHERE MONEY FUNDS CAN GO",
        footer="Named alternatives · no yield, route, or volume inferred",
        binding=binding,
        clock_kind="diagnostic" if diagnostic else "caller_validated_take")


def opening_contrast(words: list[dict], *, diagnostic: bool = False) -> dict:
    """Open on the actual contrast before the first full-stage ON RRP page."""
    _clock(words, diagnostic)
    start = _at(words, "The Fed’s balance fell by trillions.")
    end = _at(words, "By September eighteenth, that parking lot was almost empty.")
    dur = end - start - .40
    if dur < 3.0:
        raise ValueError("opening contrast has insufficient spoken room")
    return _checked({
        "kind": "flow", "at": start, "dur": dur,
        "target": dict(REGION), "readability": "landscape-phone",
        "nodes": [
            {"id": "contrast", "icon": "landmark", "label": "ACTUAL\nCONTRAST"},
            {"id": "assets", "icon": "landmark", "label": "FED ASSETS\nFELL"},
            {"id": "reserves", "icon": "landmark", "label": "BANK RESERVES\nBARELY MOVED"},
            {"id": "overnight", "icon": "coins", "label": "ON RRP\nPARKING LOT"},
        ],
        "edges": [["contrast", "assets"], ["contrast", "reserves"], ["contrast", "overnight"]],
        "tag": "ACTUAL CONTRAST · C3 / C1-C2",
        "source_quote": "Selected rows are not an exhaustive reconciliation.",
    }, [start, end], title="THE CONTRAST TO WATCH",
        footer="Actual observations · dates and account names stay visible",
        binding={"claims": [_binding("C3"), _binding("C1-C2")]},
        window={"start": "2022-06-01", "end": "2025-06-11"},
        clock_kind="diagnostic" if diagnostic else "caller_validated_take")


def _rrp_endpoint_binding() -> tuple[int, str, dict]:
    """Return the retained latest datum's index and byte identity for a spotlight."""
    path = HERE / "evidence/objects/fed-on-rrp-history.series.json"
    raw = path.read_bytes()
    record = json.loads(raw)
    points = record["series"][0]["pts"]
    index, point = len(points) - 1, points[-1]
    facts = record.get("facts", {})
    if facts.get("latest_value") != point[1]:
        raise ValueError("RRP spotlight endpoint does not match the retained object facts")
    return index, hashlib.sha256(raw).hexdigest(), facts


def opening_rrp_flags(words: list[dict], *, diagnostic: bool = False) -> dict:
    """Flag the retained current endpoint when the first ON RRP page enters."""
    _clock(words, diagnostic)
    start = _at(words, "that parking lot was almost empty.")
    end = _at(words, "Meanwhile, companies face a debt wall.")
    endpoint_index, object_sha256, facts = _rrp_endpoint_binding()
    species = [{
        "kind": "spotlight", "at": _at(words, "lot was almost empty."), "dur": 1.2,
        "target": {"kind": "datum", "index": endpoint_index},
    }]
    return _checked_species(
        species, [start, end], "ledger:fed-on-rrp-history:line:0:right:axes:cut",
        title="PEAK TO CURRENT", footer="RRPONTSYD daily observations · current endpoint flagged",
        binding=_binding("C1-C2"), object_path="evidence/objects/fed-on-rrp-history.series.json",
        object_sha256=object_sha256, endpoint_index=endpoint_index,
        endpoint_facts={key: facts[key] for key in ("peak_date", "peak_value", "latest_date", "latest_value")},
        clock_kind="diagnostic" if diagnostic else "caller_validated_take")


def historical_comparison(words: list[dict], *, diagnostic: bool = False) -> dict:
    """Refuse the superseded two-series recast until the parent-owned C3 object lands.

    The former implementation ended at the TGA sentence and pointed a history
    page at a different two-bar source. Keeping that path callable would make
    a wrong-source recast easy to select accidentally. The parent will wire the
    five-row ``fed-runoff-offsets`` object and its complete narration window.
    """
    raise ValueError(
        "historical_comparison disabled: use the parent-owned fed-runoff-offsets C3 object"
    )


def paired_100bn(words: list[dict], *, diagnostic: bool = False) -> dict:
    """Author the approved $100bn thought experiment as a C7-bound flow.

    Every dollar amount here is explicitly illustrative. The function never
    reads a historical series, and its source binding carries C7's prohibition
    on treating the proxy as official Fed data or bank reserves.
    """
    _clock(words, diagnostic)
    start = _at(words, "The Fed’s assets fall by a hundred billion dollars.")
    # Hold the paired accounting through the complete conclusion sentence;
    # the next authored sentence is the handoff into the actual C3 record.
    end = _at(words, "The Fed’s own figures show how large those offsetting movements became.")
    dur = end - start - .40
    if dur < 3.0:
        raise ValueError("paired $100bn flow has insufficient spoken room")
    binding = _binding("C7")
    return _checked({
        "kind": "flow", "at": start, "dur": dur,
        "target": dict(REGION), "readability": "landscape-phone",
        "nodes": [
            {"id": "assets", "icon": "landmark", "label": "Δ ASSETS\n−$100BN"},
            {"id": "tga", "icon": "landmark", "label": "Δ TGA\n$0"},
            {"id": "overnight", "icon": "coins", "label": "Δ ON RRP\n−$100BN"},
        ],
        # Formula operators make these paired changes, not cash-transfer
        # arrows. The unchanged bank-account result is visible in the tag and
        # explicit metadata rather than being a fourth subtraction operand.
        "edges": [["assets", "tga"], ["tga", "overnight"]],
        "operators": ["-", "-"],
        "equation": "−100 − 0 − (−100) = 0",
        "paired_changes": [
            {"account": "Fed assets", "delta_usd_billions": -100},
            {"account": "Treasury General Account", "delta_usd_billions": 0},
            {"account": "domestic ON RRP", "delta_usd_billions": -100},
        ],
        "result": {"account": "bank Fed accounts", "delta_usd_billions": 0,
                   "label": "BANK ACCOUNTS: Δ $0"},
        "no_transfer_claim": True,
        "source_custody": {
            "binding": binding,
            "source_quote": "Explicit hypothetical example",
            "status": "illustrative_derivation",
            "not_historical": True,
        },
        "tag": "ILLUSTRATION · BANK ACCOUNTS: Δ $0 · OTHER BALANCES FIXED",
    }, [start, end], title="A $100 BILLION OFFSET",
        footer="Hypothetical accounting · not observed data or reserves",
        binding=binding, amounts_are_illustrative=True,
        clock_kind="diagnostic" if diagnostic else "caller_validated_take")

"""Word-anchored pilot treatment for the approved Fed-liquidity prefix.

The records in this file are semantic handoffs, not a six-shot storyboard.
``build_rows`` resolves every boundary from the selected take's word clock and
returns the tuple shape consumed by the existing episode compiler. Evidence
objects remain episode-owned source records; this module only chooses when a
record is on screen.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from authoring import words as W


HISTORY = "fed-assets-reserves-history"
RRP = "fed-on-rrp-history"
DEBT_WALL = "debt-wall-2025-2027"

WORKSHOP_WORLD = "w2-owner-workshop-world-v1;idle=none"
FINANCE_EVIDENCE_HALL = "w4-finance-evidence-hall-v1;idle=none"
LOAN_FOLIO = "p2-owner-loan-folio-v1"

PLATE_KEN = (0.04, 12, -5)
NO_KEN = (0, 0, 0)

# This is a treatment status, not a release or approval verdict. The parent
# owns current-take selection, watch review, and all protected actions.
AUTHORING_STATUS = "DRAFT_CURRENT_TAKE_PENDING_RENDERED_REVIEW"


def history_plate() -> str:
    """Full-stage actual line chart; the chart object owns its axes and source."""
    return f"ledger:{HISTORY}:line:0:right:axes:cut;build=lines:3;idle=live"


def rrp_plate() -> str:
    """Full-stage actual ON RRP line chart."""
    return f"ledger:{RRP}:line:0:right:axes:cut;idle=live"


def debt_wall_plate() -> str:
    """Full-stage vertical-bar evidence object for the S&P maturity snapshot."""
    return f"ledger:{DEBT_WALL}:bars:0:right:axes:cut;idle=none"


@dataclass(frozen=True)
class ShotSpec:
    """A semantic onset; timing is deliberately absent until a take is supplied."""

    group: str
    start: str
    plate: str
    ken: tuple[float, float, float]
    incoming: str | None = None
    species: tuple[dict[str, Any], ...] = ()
    docks: tuple[Any, ...] = ()
    purpose: str = ""
    # New treatment rows may continue a world across a semantic group. The
    # default remains false for compatibility with older synthetic row tests.
    continuous: bool = False
    covered_groups: tuple[str, ...] = ()


def _flow(name: str) -> dict[str, str]:
    return {"kind": "flow_ref", "name": name}


def _folio_dock() -> dict[str, Any]:
    # ``build_rows`` resolves the enter anchor and exits the dock at the row's
    # measured end. It is a dock over the workshop, never a full-stage plate.
    return {"asset": LOAN_FOLIO, "slot": 0,
            "at_phrase": "Your two-percent loan is coming due",
            "options": {"centre": True, "centre_w": .32, "centre_x": .69,
                        "centre_y": .48, "card_aspect": 1.01}}


def _chip(phrase: str, label: str, x: float, y: float, dur: float = 3.0,
          icon: str = "coins") -> dict[str, Any]:
    return {"kind": "chip", "at_phrase": phrase, "dur": dur,
            "icon": icon, "label": label, "readability": "landscape-phone",
            "target": {"kind": "point", "x": x, "y": y}}


# The prefix is intentionally contiguous through the approved reflection line.
# P06/S09 is retained only as the adapter-facing group identifier.
SHOT_SPECS: tuple[ShotSpec, ...] = (
    # P01 — matched historical hook, current ON RRP, new debt wall, then the
    # approved workshop/folio stake. P01 closes on the complete tripling-
    # interest sentence, not on a planning timestamp.
    ShotSpec("P01", "The Fed’s balance fell by trillions.", FINANCE_EVIDENCE_HALL, NO_KEN,
             species=(
                 _chip("The Fed’s balance fell by trillions.", "FED ASSETS\nFELL", .40, .26, 2.8, "landmark"),
                 _chip("Bank reserves barely budged.", "BANK BALANCES\nBARELY MOVED", .60, .26, 2.8, "landmark"),
             ), purpose="spoken contrast on the hall's cream board", continuous=True),
    ShotSpec("P01", "that parking lot was almost empty.",
             f"ledger:{RRP}:line::right:surface=center-paper,1.20:cut;idle=none;then={DEBT_WALL}:bars", NO_KEN,
             species=(
                 _flow("opening_rrp_flags"),
                 {"kind": "chart_to", "at_phrase": "Meanwhile, companies face a debt wall.", "dur": 1.2, "to": "recast", "state": 1, "keyed": False},
                 {"kind": "retitle", "at_phrase": "S&P tallied more than three trillion dollars", "dur": 1.2, "text": "THE CORPORATE DEBT WALL"},
                 {"kind": "spotlight", "at_phrase": "S&P tallied more than three trillion dollars", "dur": 1.2, "target": {"kind": "datum", "index": 2}},
             ), purpose="surface grows; chart erases and rebuilds with the separately titled S&P source, not a keyed data morph", continuous=True),
    ShotSpec("P01", "Imagine you own a workshop.", WORKSHOP_WORLD, PLATE_KEN,
             "melt:splash:plate:1.2", docks=(_folio_dock(),), species=(
                 _chip("Your two-percent loan is coming due", "OLD LOAN\n2%", .61, .32, 1.7),
                 _chip("and replacing it at seven percent", "RENEWAL\n7%", .77, .32, 2.3),
                 _chip("more than triples your interest", "ANNUAL INTEREST\n3.5× · SAME DEBT", .69, .57, 3.0),
             ), purpose="owner stays visible; illustrative annual-interest comparison", continuous=True),

    # P02 — remain in the workshop while the bill, promise, biography, and
    # problem are spoken. The three-check agenda is deliberately not a card.
    ShotSpec("P02", "Your machine still works. Your customers still need their orders.", WORKSHOP_WORLD, PLATE_KEN,
             species=(_chip("But the bigger bill leaves less for wages", "LESS FOR WAGES\nMATERIALS\nTHE NEXT HIRE", .66, .42, 4.0),),
             purpose="human consequences beside the owner, not a detached checklist", continuous=True),
    ShotSpec("P02", "I worked in business risk at JPMorgan", FINANCE_EVIDENCE_HALL, NO_KEN,
             "door:left:0.9", purpose="open from the owner's workshop into the financing system", continuous=True),
    ShotSpec("P02", "Here’s the problem: stable bank balances can hide a shrinking buffer.",
             f"ledger:{RRP}:line::right:surface=center-paper,1.2:cut;idle=none", NO_KEN,
             purpose="return to the actual shrinking account behind the argument", continuous=True),

    # P03 — the approved hall carries the ON RRP definition and alternatives.
    ShotSpec("P03", "Money funds can park cash at the Fed overnight and earn a return.",
             FINANCE_EVIDENCE_HALL, NO_KEN, "melt:splash:plate:1.2",
             purpose="ON RRP definition in evidence hall", continuous=True),
    ShotSpec("P03", "The Fed calls this arrangement overnight reverse repo.",
             FINANCE_EVIDENCE_HALL, NO_KEN,
             species=(_chip("The Fed calls this arrangement overnight reverse repo.", "OVERNIGHT\nREVERSE REPO", .50, .29, 3.0, "landmark"),), purpose="named account", continuous=True),
    ShotSpec("P03", "But money funds can earn money elsewhere, too.",
             FINANCE_EVIDENCE_HALL, NO_KEN,
             species=(_flow("overnight_alternatives"),),
             purpose="alternative destinations", continuous=True),
    ShotSpec("P03", "Those withdrawals helped banks hold their ground while the Fed cut its own investments.",
             FINANCE_EVIDENCE_HALL, NO_KEN,
             purpose="actual account effect; no invented amount", continuous=True),

    # P04 — one purposeful handoff into the paired hypothetical. The flow is
    # explicitly bound to C7 and is not a historical series or a reused chart.
    ShotSpec("P04", "The Fed owns Treasury securities and mortgage-backed securities.",
             f"ledger:{HISTORY}:line::right:surface=center-paper,1.2:cut;build=lines:3;idle=none", NO_KEN,
             species=(
                 {"kind": "note", "at_phrase": "That process is called quantitative tightening.", "dur": 1.5, "text": "Quantitative tightening: assets run off"},
             ), purpose="name what matures before illustrating the paired declines", continuous=True),
    ShotSpec("P04", "Here’s a simplified example.", FINANCE_EVIDENCE_HALL, NO_KEN,
             "melt:splash:plate:1.2", species=(_flow("paired_100bn"),),
             purpose="$100bn hypothetical, all other balances fixed", continuous=True),

    # P05/P06 — return to the actual June 2022–June 2025 history and hold it
    # through the approved reflection endpoint. No separately rounded bar
    # object is substituted for the selected history record.
    ShotSpec("P05", "The Fed’s own figures show how large those offsetting movements became.",
             f"ledger:{HISTORY}:line::right:surface=center-paper,1.2:cut;build=lines:3;idle=none", NO_KEN,
             purpose="actual June 2022–June 2025 comparison", continuous=True),
    ShotSpec("P05", "Reverse repos outside the foreign-official accounts fell about one point eight trillion.",
             "ledger:fed-runoff-offsets:bars:0:right:axes:cut;idle=none", NO_KEN,
             "melt:gather:throw:1.2", species=(
                 {"kind": "spotlight", "at_phrase": "Reverse repos outside the foreign-official accounts fell about one point eight trillion.", "dur": 2.5, "target": {"kind": "datum", "index": 2}},
                 {"kind": "spotlight", "at_phrase": "Banks’ balances at the Fed rose by just seventy-two billion dollars.", "dur": 2.5, "target": {"kind": "datum", "index": 1}},
                 {"kind": "spotlight", "at_phrase": "The government’s cash account also fell, helping offset the drain on banks.", "dur": 2.5, "target": {"kind": "datum", "index": 3}},
                 {"kind": "spotlight", "at_phrase": "Trillions of dollars of withdrawals barely helped them hold their ground.", "dur": 2.5, "target": {"kind": "datum", "index": 1}},
             ), purpose="all named C3 rows visible; comparison, not an exhaustive reconciliation", continuous=True,
             covered_groups=("P05", "P06")),
)


GROUPS = ("P01", "P02", "P03", "P04", "P05", "P06")
SEGMENT_GROUPS = {"bed": GROUPS[:1], "unit": GROUPS[:3], "pilot": GROUPS}

GROUP_CLOSING_PHRASES = {
    "P01": "Your two-percent loan is coming due, and replacing it at seven percent more than triples your interest bill—without borrowing another dollar.",
    "P02": "We’ll follow where that support went, then bring the risk back to your renewal offer.",
    "P03": "Those withdrawals helped banks hold their ground while the Fed cut its own investments.",
    "P04": "Banks avoid that cash drain because another account shrinks instead.",
    "P05": "The government’s cash account also fell, helping offset the drain on banks.",
    "P06": "Trillions of dollars of withdrawals barely helped them hold their ground.",
}


def semantic_specs_for(segment: str) -> tuple[ShotSpec, ...]:
    groups = SEGMENT_GROUPS.get(segment)
    if groups is None:
        raise ValueError(f"unsupported assembly segment {segment!r}; choose bed, unit, or pilot")
    return tuple(spec for spec in SHOT_SPECS if spec.group in groups)


def _can_coalesce(previous: ShotSpec, current: ShotSpec) -> bool:
    """Merge only state-free identical worlds; never merge a transition/state."""
    group_ok = previous.group == current.group or (previous.continuous and current.continuous)
    return (
        group_ok
        and current.incoming is None
        and previous.plate == current.plate
        and previous.ken == current.ken
        and not previous.species
        and not current.species
        and not previous.docks
        and not current.docks
    )


def _covered(spec: ShotSpec) -> tuple[str, ...]:
    return spec.covered_groups or (spec.group,)


def _coalesce_render_specs(specs: tuple[ShotSpec, ...]) -> tuple[ShotSpec, ...]:
    rendered: list[ShotSpec] = []
    for spec in specs:
        if rendered and _can_coalesce(rendered[-1], spec):
            previous = rendered[-1]
            groups = tuple(dict.fromkeys(_covered(previous) + _covered(spec)))
            rendered[-1] = ShotSpec(
                group=previous.group, start=previous.start, plate=previous.plate,
                ken=previous.ken, incoming=previous.incoming, species=previous.species,
                docks=previous.docks, purpose=previous.purpose,
                continuous=previous.continuous, covered_groups=groups,
            )
        else:
            rendered.append(spec)
    return tuple(rendered)


def render_specs_for(segment: str) -> tuple[ShotSpec, ...]:
    return _coalesce_render_specs(semantic_specs_for(segment))


def specs_for(segment: str) -> tuple[ShotSpec, ...]:
    return render_specs_for(segment)


def group_end_phrase(group: str) -> str:
    if group not in GROUPS:
        raise ValueError(f"unknown production group {group!r}")
    return GROUP_CLOSING_PHRASES[group]


def _token_norm(value: str) -> str:
    # Kokoro may emit an apostrophe as U+FFFD in the same token, or as its own
    # punctuation token. Canonicalising only punctuation preserves a measured
    # index mapping while letting SCRIPT-VO's curly typography match the take.
    return (value.strip(".,:;!?\"'”’�")
            .replace("’", "").replace("'", "").replace("�", "")
            .replace("–", "-").lower())


def _normalized_word_tokens(words: list[dict[str, Any]]) -> list[tuple[str, int]]:
    return [(token, index) for index, word in enumerate(words)
            if (token := _token_norm(str(word["w"]))) != ""]


def _phrase_index(words: list[dict[str, Any]], phrase: str) -> int:
    terms = [_token_norm(token) for token in phrase.split() if _token_norm(token)]
    normalized = _normalized_word_tokens(words)
    hits = [position for position in range(len(normalized) - len(terms) + 1)
            if [token for token, _ in normalized[position:position + len(terms)]] == terms]
    if len(hits) != 1:
        raise ValueError(f"pilot anchor must occur once: {phrase!r} ({len(hits)} matches)")
    return normalized[hits[0]][1]


def _anchor(words: list[dict[str, Any]], phrase: str) -> float:
    return round(float(words[_phrase_index(words, phrase)]["start_s"]), 3)


def _cut_before(words: list[dict[str, Any]], phrase: str, exit_name: str) -> float:
    """Use the native measured/gap rule after resolving a punctuation-safe anchor."""
    _phrase_index(words, phrase)  # Reject ambiguity even when the native helper would pick its first hit.
    try:
        return W.cut_before(words, phrase, exit=exit_name)
    except (SystemExit, ValueError):
        index = _phrase_index(words, phrase)
        if index == 0:
            return 0.0
        start = float(words[index]["start_s"])
        previous_end = float(words[index - 1]["end_s"])
        gap = start - previous_end
        if gap < W.MIN_GAP:
            raise ValueError(f"no cut point before {phrase!r}: gap {gap:.2f}s < {W.MIN_GAP}s")
        if W.cut_rule(words) == "gap":
            return round(previous_end + W.CUT_AT * gap, 2)
        lead = 0.0 if exit_name == "dip" else W.CUT_LEAD_S
        return round(max(previous_end, start - lead), 2)


def _resolve_docks(docks: tuple[Any, ...], words: list[dict[str, Any]], row_end: float) -> list[Any]:
    resolved: list[Any] = []
    for dock in docks:
        if not isinstance(dock, dict) or "at_phrase" not in dock:
            resolved.append(dock)
            continue
        resolved.append([
            dock["asset"], dock.get("slot", 0), _anchor(words, dock["at_phrase"]),
            round(row_end, 2),
            dock.get("options", {}),
        ])
    return resolved


def _resolve_species(species: tuple[dict[str, Any], ...], words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    resolved: list[dict[str, Any]] = []
    for item in species:
        if item.get("kind") == "flow_ref":
            # Lazy import avoids creating a second engine path and keeps the
            # table importable by the existing builder.
            from pilot_schematics import (  # pylint: disable=import-outside-toplevel
                overnight_alternatives,
                paired_100bn,
                opening_rrp_flags,
            )
            factory = {"overnight_alternatives": overnight_alternatives,
                       "paired_100bn": paired_100bn,
                       "opening_rrp_flags": opening_rrp_flags}.get(item["name"])
            if factory is None:
                raise ValueError(f"unknown pilot flow reference {item['name']!r}")
            checked = factory(words)
            metadata = {key: value for key, value in checked.items() if key != "species"}
            resolved.extend({**value, "authoring_evidence": metadata} for value in checked["species"])
            continue
        value = dict(item)
        anchor_phrase = value.pop("at_phrase", None)
        if anchor_phrase is not None:
            value["at"] = _anchor(words, anchor_phrase)
        resolved.append(value)
    return resolved


def build_rows(words: list[dict[str, Any]], runtime_s: float, segment: str) -> list[tuple]:
    """Resolve semantic rows against the caller's measured take clock."""
    specs = specs_for(segment)
    if not specs:
        raise ValueError(f"no rows for assembly segment {segment!r}")
    if isinstance(runtime_s, bool) or not isinstance(runtime_s, (int, float)) or not math.isfinite(runtime_s):
        raise ValueError("runtime_s must be a finite positive number")
    runtime = float(runtime_s)
    if runtime <= 0:
        raise ValueError("runtime_s must be a finite positive number")
    rows: list[tuple] = []
    for index, spec in enumerate(specs):
        start = 0.0 if index == 0 else rows[-1][1]
        if index + 1 < len(specs):
            next_spec = specs[index + 1]
            if ":surface=" in next_spec.plate:
                # The same registered evidence is continuously projected from
                # the previous world, not a hard cut requiring a silent gap.
                boundary = _anchor(words, next_spec.start)
            elif (spec.continuous and next_spec.continuous and next_spec.plate == spec.plate
                  and next_spec.ken == NO_KEN and not next_spec.incoming):
                boundary = _anchor(words, next_spec.start)
            else:
                boundary = _cut_before(words, next_spec.start, next_spec.incoming or "cut")
        else:
            boundary = round(runtime, 3)
        if boundary <= start:
            raise ValueError(f"{spec.group} row {spec.start!r} has non-positive span {start}..{boundary}")
        rows.append((
            round(start, 2), round(boundary, 2), spec.plate, spec.ken,
            _resolve_docks(spec.docks, words, boundary), spec.incoming,
            _resolve_species(spec.species, words),
        ))
    return rows


def group_ranges(rows: list[tuple], segment: str = "pilot") -> dict[str, tuple[float, float]]:
    """Return receipt spans, including semantic groups coalesced into one row."""
    out: dict[str, tuple[float, float]] = {}
    specs = list(specs_for(segment))
    for index, spec in enumerate(specs):
        if index >= len(rows):
            break
        span = (float(rows[index][0]), float(rows[index][1]))
        for group in _covered(spec):
            if group in out:
                out[group] = (out[group][0], span[1])
            else:
                out[group] = span
    return {group: out[group] for group in SEGMENT_GROUPS[segment] if group in out}

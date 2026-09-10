"""Ledger page spec: a ``series.json`` -> the page spec the plate-chart species consumes.

Doctrine: doc 29 s9.26 (data only from a series.json; the source line is written
on the page; exact values never re-rounded; a declared quiet zone; variants
line|bars|race|decline|progress) and s9.28 (surface x builder are two axes). P35 T2.

    ledger_page.py <series.json> --variant line|bars|race|decline|progress
                   [--emphasize n] [--quiet-zone left|right] [--out spec.json]

``--out`` defaults to ``<name>.page.json`` beside the input. Exit 0 on success,
2 when the series is not a page (the message names the file and every failing rule).
Input shapes (every one needs ``title`` and a non-empty ``src``):
  story    {"bars": [{"label", "value", "color", "note"?}]}   <= STORY_MAX_VALUES
  dense    {"series": [{"label"|"name", "color", "pts": [[x, y], ...]}], + AXES_KEYS}
           or {"panels": [{"sub", "series": [...]}]}
  race     {"periods": [...], "series": [{"name", "values": [...], "color"?}]}
           (or dense series sharing one x grid of >= RACE_MIN_PERIODS points)
  decline  exactly one metric (a single dense series, or bars of >= DECLINE_MIN_VALUES);
           first and last are the endpoints
  progress story values in 0..PROGRESS_MAX, or non-negative with a numeric "denominator"
Rejected clearly: "checklist" (a table). "shares" (a donut) is rejected for every variant EXCEPT
  `share`, which E53 s1 as amended (2026-09-07) allows inside four bounds - see SHARE_BOUNDS.
Builder (``pick_builder``): race/decline follow the variant; bars + a pts series ->
combo; > STORY_MAX_VALUES points or > 1 pts series -> dense-line; else story.
Output ``ledger_page.v1`` (ink/paper colours are NOT here - the template owns the
register; ``color`` token names pass through verbatim):
  schema_version, surface "page", builder, variant, title, sub, source, quiet_zone,
  emphasize (index clamped into labels, or null)
  labels / values / value_strings / colors   per datum (story); per series (race, values
           as one list per series); dense carries labels only. value_strings are the
           tokens EXACTLY as the file wrote them (parse_float=str: 3.90 stays "3.90")
  series, axes   dense-line and combo only, verbatim      periods   race only, verbatim
  start, end     decline only: {"label", "value", "value_string"} - label is the datum's token verbatim
  display_labels decline only: {"start", "end", "series"} - the READABLE x labels (s9.22: never a
           raw float): an exact ``xticks`` match, else a top-level ``labels`` list, else a decimal
           year as "Mon 'YY", else the token; ``series`` is the metric's name for the inline label
           (s9.23b; null for bars). A dense-series decline also carries ``axes`` verbatim.
  denominator    progress only, when the file carries one (verbatim token)
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

STORY_MAX_VALUES = 12    # s9.26 / chart-story: 4-8 values, our ceiling 12
RACE_MIN_PERIODS = 2     # s9.26: ranked bars overtaking ACROSS periods
DECLINE_MIN_VALUES = 2   # s9.26: one metric, a start and an end
PROGRESS_MAX = 100       # s9.26 progress: a share of a whole unless a denominator is given
EXIT_INVALID = 2
SCHEMA_VERSION = "ledger_page.v1"
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
YEAR_RANGE = (1900, 2100)   # a decimal x outside this is a number, not a date
VARIANTS = ("line", "bars", "race", "decline", "progress", "share", "object")
CHART_VARIANTS = ("line", "bars", "race", "decline", "progress", "share")
# `object` is the page as a WORKING surface rather than an evidence surface: it draws
# a registered prop in ink on the cream instead of a chart. Same page clock, same
# deckle, same focus - so an object page can transform into a chart page without a
# plate change (RULE-the-page-is-the-ground, 2026-09-04).
PROP_PLACEMENTS = ("centre", "left", "right", "datum")
QUIET_ZONES = ("left", "right")
AXES_KEYS = ("log", "ylabel", "xticks", "from_zero", "highlight_from", "hlines", "hline", "marks", "eventbars",
             "name_clear",   # lift the inline series name clear of the data it would otherwise be written across
             "ymin", "ymax", "yfmt", "yunit", "panels",
             "domain", "xdomain")   # P48 T2: a derived rescale state names its exact y domain and x window
UNCHARTABLE = {
    "checklist": "no chartable values: 'checklist' is a table, not a chart (keep it a dock)",
    "shares": ("'shares' is a donut, and E53 s1 ranks angle and area at the bottom of the perception hierarchy: "
               "it is refused for every variant except --variant share, which the ruling's amendment (2026-09-07) "
               "allows only inside its four bounds - a part-to-whole claim about ONE named slice, that slice "
               "highlighted and the rest muted, the figure WRITTEN on the page, and five slices or fewer"),
}
# E53 s1 as amended (2026-09-07). The hierarchy's objection is to COMPARING many encoded angles; a claim about one
# highlighted slice is not that. These are the amendment's bounds, enforced here so the exception cannot widen by use.
SHARE_MAX_SLICES = 5
SHARE_BOUNDS = (
    "a part-to-whole claim about ONE named slice, never a ranking or a comparison across slices",
    "that slice highlighted, every other slice muted context",
    "the figure the claim turns on WRITTEN on the page, so no angle has to be estimated",
    f"{SHARE_MAX_SLICES} slices or fewer",
)
UNCHARTABLE_DEFAULT = "no chartable values: expected bars[], series[].pts, panels[], or periods + series[].values"


def to_number(value: Any) -> float | None:
    """A numeric token -> float; bool, None and non-numeric text -> None."""
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def value_string(value: Any) -> str:
    """The token as written (strings are already verbatim under parse_float=str)."""
    return value if isinstance(value, str) else repr(value)


def decimal_year_label(value: Any) -> str | None:
    """A decimal year (2026.6489) -> "Aug '26"; None when the token is not a plausible year."""
    year = to_number(value)
    if year is None or not (YEAR_RANGE[0] <= year < YEAR_RANGE[1]):
        return None
    whole = int(year)
    month = min(11, int((year - whole) * 12 + 0.01))   # 2026.0833 is February: a four-decimal year puts 0.0833 * 12 at 0.9996, which truncates to January without a hundredth of a month's tolerance (P48 T2)
    return f"{MONTHS[month]} '{whole % 100:02d}"


def display_label(token: Any, index: int, xticks: list | None = None, labels: list | None = None) -> str:
    """The readable label for an x token: an exact xtick, else labels[index], else the year, else the token."""
    x = to_number(token)
    if x is not None:
        for tick in xticks or []:
            if isinstance(tick, (list, tuple)) and len(tick) == 2 and to_number(tick[0]) == x:
                return str(tick[1])
    if isinstance(labels, list) and 0 <= index < len(labels) and _text(labels[index]):
        return str(labels[index])
    return decimal_year_label(token) or str(token)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _points(entry: dict) -> list:
    return [p for p in entry.get("pts") or [] if isinstance(p, (list, tuple)) and len(p) == 2]


def _bars(series: dict) -> list[dict]:
    return [b for b in series.get("bars") or [] if isinstance(b, dict)]


def dense_series(series: dict) -> list[dict]:
    """Every pts-bearing series in the file, panels flattened in."""
    own = [s for s in series.get("series") or [] if isinstance(s, dict) and "pts" in s]
    panels = [s for p in series.get("panels") or [] if isinstance(p, dict)
              for s in p.get("series") or [] if isinstance(s, dict) and "pts" in s]
    return own + panels


def story_data(series: dict) -> tuple[list, list, list]:
    """(labels, raw values, colors) from bars, or from a single series read as one."""
    bars, dense = _bars(series), dense_series(series)
    if bars:
        return ([b.get("label") for b in bars], [b.get("value") for b in bars], [b.get("color") for b in bars])
    if len(dense) == 1:
        pts = _points(dense[0])
        return ([value_string(p[0]) for p in pts], [p[1] for p in pts], [dense[0].get("color")] * len(pts))
    return [], [], []


def race_periods(series: dict) -> list:
    """Declared ``periods``, else the x grid every pts series shares."""
    if series.get("periods"):
        return list(series["periods"])
    grids = [[p[0] for p in _points(s)] for s in dense_series(series)]
    if grids and all(g == grids[0] for g in grids) and len(grids[0]) >= RACE_MIN_PERIODS:
        return grids[0]
    return []


def race_rows(series: dict) -> list[dict]:
    """Race rows {name, values, color}; values from ``values`` or the pts y column."""
    rows = []
    for entry in (s for s in series.get("series") or [] if isinstance(s, dict)):
        values = entry["values"] if "values" in entry else [p[1] for p in _points(entry)]
        rows.append({"name": entry.get("name") or entry.get("label"),
                     "values": list(values or []), "color": entry.get("color")})
    return rows


def pick_builder(series: dict, variant: str) -> str:
    if variant == "object":
        return "object"
    if variant == "share":
        return "share"
    """Builder from the data shape and the variant (P35 Builder Architecture)."""
    if variant in ("race", "decline"):
        return variant
    dense = dense_series(series)
    if _bars(series) and dense:
        return "combo"
    if len(dense) > 1 or any(len(_points(s)) > STORY_MAX_VALUES for s in dense):
        return "dense-line"
    return "story"


def validate(series: dict, variant: str) -> list[str]:
    """Error strings; empty means the series is a page for this variant. Pure."""
    errors: list[str] = []
    if variant not in VARIANTS:
        errors.append(f"variant {variant!r} is not one of {'|'.join(VARIANTS)}")
    if not _text(series.get("title")):
        errors.append("missing title")
    if not _text(series.get("src")):
        errors.append("missing source line: 'src' is required and is written on the page (s9.26)")
    if series.get("placeholder") is True:   # AGENTS.md: figures are never fabricated - a placeholder never renders
        errors.append("placeholder figures: 'placeholder': true marks values still under SOURCES-TO-VERIFY; a page never renders them")
    if variant == "object":
        return errors + _validate_object(series)
    if variant == "share":
        return errors + _validate_share(series)
    has_race = any(r["values"] for r in race_rows(series))
    if variant != "share" and "shares" in series and not (_bars(series) or dense_series(series)):
        return errors + [UNCHARTABLE["shares"]]
    if not (_bars(series) or dense_series(series) or has_race):
        return errors + [next((v for k, v in UNCHARTABLE.items() if k in series), UNCHARTABLE_DEFAULT)]
    if variant in CHART_VARIANTS:
        errors += _validate_shape_for_variant(series, variant)
    errors += _validate_sign_in_geometry(series)
    errors += badge_key_conflicts(series)
    return errors + _validate_values(series, variant) + _validate_variant(series, variant)


SIGNED_NOTE_RE = re.compile(r"^\s*[+\u2212-]\s*\d")
MONTH_LABEL_RE = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*'?(\d{2}|\d{4})$")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _validate_share(series: dict) -> list[str]:
    """A share page's contract - E53 s1's amendment, checked rather than trusted. Every failure names the bound it
    broke, because the whole point of writing the exception down was that it not widen by use."""
    errors: list[str] = []
    shares = series.get("shares")
    if not isinstance(shares, list) or len(shares) < 2:
        return ["a share page needs 'shares': at least two slices, the whole they add up to being the page's subject"]
    if len(shares) > SHARE_MAX_SLICES:
        errors.append(f"{len(shares)} slices: E53 s1 allows {SHARE_MAX_SLICES} or fewer ({SHARE_BOUNDS[3]})")
    for i, sh in enumerate(shares):
        if not isinstance(sh, dict):
            errors.append(f"shares[{i}] is not an object"); continue
        if not _text(sh.get("label")):
            errors.append(f"shares[{i}] has no label: a slice is named at its own edge, never in a legend (E53 s8)")
        v = to_number(sh.get("value"))
        if v is None or v <= 0:
            errors.append(f"shares[{i}] value {sh.get('value')!r} is not a positive number: a part of a whole cannot be negative")
    emph = series.get("emphasize")
    if not isinstance(emph, int) or isinstance(emph, bool) or not 0 <= emph < len(shares):
        errors.append(f"a share page must declare 'emphasize': the index of the ONE slice the claim is about ({SHARE_BOUNDS[0]}; {SHARE_BOUNDS[1]})")
    peel = series.get("peel")
    if not isinstance(peel, dict):
        errors.append(f"a share page must declare 'peel': the piece of the named slice the claim is about, with its figure ({SHARE_BOUNDS[2]})")
    else:
        if not _text(peel.get("value_string")):
            errors.append(f"peel.value_string is required: {SHARE_BOUNDS[2]}")
        pv = to_number(peel.get("value"))
        if pv is None:
            errors.append("peel.value must be a number: the size of the piece, signed (a sale is negative - E28)")
        pi = peel.get("index")
        if not isinstance(pi, int) or isinstance(pi, bool) or not 0 <= pi < len(shares):
            errors.append("peel.index must name one of the slices")
        elif isinstance(emph, int) and not isinstance(emph, bool) and pi != emph:
            errors.append(f"peel.index {pi} is not the emphasised slice {emph}: {SHARE_BOUNDS[0]}")
        elif pv is not None:
            whole = to_number(shares[pi].get("value")) or 0.0
            if abs(pv) > whole:
                errors.append(f"peel {pv} is larger than the slice it comes out of ({whole}): a piece cannot exceed its part")
    return errors


def _validate_object(series: dict) -> list[str]:
    """An object page's contract. No values, so no sign geometry and no badge keying -
    but a prop that carries a FIGURE still owes a source, because a number drawn in ink
    is as much a claim as a number on an axis."""
    errors: list[str] = []
    props = series.get("props")
    if not isinstance(props, list) or not props:
        return ["an object page needs 'props': a non-empty list of registered prop assets"]
    seen: set[str] = set()
    for i, p in enumerate(props):
        if not isinstance(p, dict):
            errors.append(f"props[{i}] is not an object"); continue
        pid = p.get("asset")
        if not _text(pid):
            errors.append(f"props[{i}] missing 'asset': props are registered, never inline art")
        elif pid in seen:
            errors.append(f"props[{i}] '{pid}' is placed twice; one asset, one placement")
        else:
            seen.add(pid)
        place = p.get("at", "centre")
        if place not in PROP_PLACEMENTS:
            errors.append(f"props[{i}] 'at' {place!r} is not one of {'|'.join(PROP_PLACEMENTS)}")
        if place == "datum" and not isinstance(p.get("index"), int):
            errors.append(f"props[{i}] placed at a datum needs an integer 'index' - "
                          "that is how a prop is positioned RELATIVE TO CHART DATA")
        if _text(p.get("figure")) and not _text(series.get("src")):
            errors.append(f"props[{i}] carries the figure {p['figure']!r} but the page has no source line")
    return errors


def _validate_sign_in_geometry(series: dict) -> list[str]:
    """E28 (operator, 2026-09-03): a chart must read right at a glance - a drop is a bar
    going DOWN. A bar whose value is an unsigned magnitude while its note carries the
    minus sign draws every drop as a rise (the trim proof read as seven rises)."""
    errors = []
    for i, bar in enumerate(_bars(series)):
        note, value = str(bar.get("note") or ""), to_number(bar.get("value"))
        if value is not None and value > 0 and SIGNED_NOTE_RE.match(note) and note.strip()[0] in "-\u2212":
            errors.append(f"bars[{i}] {bar.get('label')!r}: the sign lives in the note ({note.strip()}) while the value "
                          f"({value_string(bar.get('value'))}) is an unsigned magnitude - sign the value so the bar goes down (E28)")
    return errors


def _month_index(label: str) -> int | None:
    m = MONTH_LABEL_RE.match(str(label).strip())
    if not m:
        return None
    year = int(m.group(2))
    year = year + (2000 if year < 100 else 0)
    return year * 12 + MONTHS.index(m.group(1))


def review_notes(series: dict) -> list[str]:
    """JUDGE rows for the operator (CHECK-RESPONSIBILITIES: not a tool's verdict). E28: an
    axis of dates with uneven gaps reads as noise unless the page states the selection
    rule - `selection` in the file, written into the sub. Pure."""
    notes = []
    labels = [b.get("label") for b in _bars(series)]
    idx = [_month_index(x) for x in labels]
    if len(idx) >= 3 and all(i is not None for i in idx):
        gaps = [b - a for a, b in zip(idx, idx[1:])]
        if len(set(gaps)) > 1:
            rule = _text(series.get("selection"))
            notes.append("date axis with uneven gaps (months apart: " + ", ".join(str(g) for g in gaps) + ") - "
                         + (f"selection rule declared: {series['selection']!r}; check the sub says it on the page" if rule
                            else "no `selection` rule in the file: the reader sees noise unless the sub says which dates and why (E28)"))
    return notes


BADGE_ACCENT_TO_SERIES = {"coral": "crimson", "teal": "teal", "cobalt": "cobalt", "ink": "deemph", "sunflower": "amber"}


KEY_STOP = {"THE", "OF", "A", "AND", "STOCKS", "STOCK", "SHARE", "PRICE", "PRICES", "INDEX", "MARKET"}


def _key_tokens(text: str) -> set[str]:
    return {w.strip("()+,:;.'\"").upper() for w in str(text or "").split()} - KEY_STOP - {""}


def badge_key_conflicts(series: dict, extra: list | None = None) -> list[str]:
    """E28 addendum (operator, 2026-09-03: the +613% line was labelled MEGA-CAP TECH while
    its badge said MEMORY BUILDERS): a badge's label must name the line its accent keys.
    A badge word that appears in ANOTHER series' name and not in the keyed one is a swap."""
    errors = []
    dense = dense_series(series)
    for b in (series.get("badges") or []) + list(extra or []):
        col = BADGE_ACCENT_TO_SERIES.get(str(b.get("accent") or ""))
        keyed = [s for s in dense if s.get("color") == col]
        if not col or not keyed:
            continue
        words = _key_tokens(b.get("label"))
        mine = _key_tokens(keyed[0].get("name"))
        for other in dense:
            if other is keyed[0]:
                continue
            hit = (words & _key_tokens(other.get("name"))) - mine
            if hit:
                errors.append(f"badge {b.get('label')!r} ({b.get('accent')}) keys the {col} line {keyed[0].get('name')!r} "
                              f"but names the {other.get('color')} line {other.get('name')!r} ({', '.join(sorted(hit))}) - a swapped label (E28)")
    return errors


def badges_for(series: dict, extra: list | None = None) -> list[dict]:
    """The page's badges (operator, 2026-09-03: 'we need the badges back - that's how we were
    quickly conveying information and applying a key for the viewer'): the file's own
    ``badges`` plus any handed in from the evidence dock, each {label, value, tag, accent}.
    BADGE-CHART SYNC (build_scene_timeline_f, 2026-08-30): a badge whose accent maps to a
    series colour takes that series' CURRENT label as its value, so the pill never drifts
    from the line it keys. Pure."""
    raw = [b for b in (series.get("badges") or []) + list(extra or []) if isinstance(b, dict)]
    out = []
    for b in raw:
        bd = {"label": str(b.get("label") or ""), "value": str(b.get("value") or ""),
              "tag": str(b.get("tag") or ""), "accent": str(b.get("accent") or "sunflower")}
        col = BADGE_ACCENT_TO_SERIES.get(bd["accent"])
        for entry in dense_series(series):
            if col and entry.get("color") == col and _text(entry.get("label")):
                bd["value"] = str(entry["label"]).split()[0]
        # a badge that keys a dense series becomes that line's DYNAMIC LABEL (operator, 2026-09-03:
        # 'grouped below the chart, or dynamic labels - not label + pill + captions on one real estate')
        bd["inline"] = bool(col) and any(e.get("color") == col for e in dense_series(series))
        out.append(bd)
    return out


def _validate_shape_for_variant(series: dict, variant: str) -> list[str]:
    """The REQUESTED variant must have data of its own shape: a chartable file is not
    a page for every variant (a race file asked for bars would build an empty page)."""
    builder = pick_builder(series, variant)
    if builder in ("story", "decline", "progress") and not story_data(series)[1]:
        return [f"variant {variant!r} needs story values (bars, or one short series); this file has none - pick the variant its shape supports"]
    if builder == "dense-line" and not dense_series(series):
        return [f"variant {variant!r} needs a dense series ([x, y] points); this file has none"]
    if builder == "combo" and not (_bars(series) and dense_series(series)):
        return ["combo needs both bars and a dense series"]
    return []


def _validate_values(series: dict, variant: str) -> list[str]:
    """Numeric values, one label per datum, named series, [x, y] pairs, story ceiling."""
    errors, bars = [], _bars(series)
    for i, bar in enumerate(bars):
        if to_number(bar.get("value")) is None:
            errors.append(f"bars[{i}] value {bar.get('value')!r} is not numeric")
        if not _text(bar.get("label")):
            errors.append(f"bars[{i}] has no label (one label per datum)")
    if bars and pick_builder(series, variant) == "story" and len(bars) > STORY_MAX_VALUES:
        errors.append(f"story shape carries {len(bars)} values; the ceiling is {STORY_MAX_VALUES}")
    for i, entry in enumerate(dense_series(series)):
        if not (_text(entry.get("label")) or _text(entry.get("name"))):
            errors.append(f"series[{i}] has neither label nor name (s9.23b: series are named inline)")
        raw = entry.get("pts") or []
        bad = [p for p in raw if not (isinstance(p, (list, tuple)) and len(p) == 2
                                      and to_number(p[0]) is not None and to_number(p[1]) is not None)]
        if bad or not raw:
            errors.append(f"series[{i}] pts must be [x, y] numeric pairs ({len(bad)} bad of {len(raw)})")
    return errors


def _validate_variant(series: dict, variant: str) -> list[str]:
    """Race needs periods; decline one metric with two ends; progress a bounded share."""
    errors: list[str] = []
    if variant == "race":
        periods = race_periods(series)
        if len(periods) < RACE_MIN_PERIODS:
            return [f"race needs periods: a 'periods' list of >= {RACE_MIN_PERIODS}, or series sharing one x grid"]
        for i, row in enumerate(race_rows(series)):
            if not _text(row["name"]):
                errors.append(f"series[{i}] has no name for the race")
            if len(row["values"]) != len(periods):
                errors.append(f"series[{i}] has {len(row['values'])} values for {len(periods)} periods")
            if any(to_number(v) is None for v in row["values"]):
                errors.append(f"series[{i}] race values must all be numeric")
    if variant == "decline":
        metrics = (1 if _bars(series) else 0) + len(dense_series(series))
        if metrics != 1:
            return [f"decline takes exactly one metric (a single series or one bars list); found {metrics}"]
        if len(story_data(series)[1]) < DECLINE_MIN_VALUES:
            return [f"decline needs a start and an end (>= {DECLINE_MIN_VALUES} values); found {len(story_data(series)[1])}"]
    if variant == "progress":
        labels, raw, _colors = story_data(series)
        if not raw:
            return ["progress needs story values (bars or one short series)"]
        denominator = to_number(series.get("denominator"))
        ceiling = denominator if denominator and denominator > 0 else PROGRESS_MAX
        bound = (f"0..{value_string(series['denominator'])} (denominator)" if denominator
                 else f"0..{PROGRESS_MAX} and no denominator is given")
        for label, value in zip(labels, raw):
            number = to_number(value)
            if number is None or number < 0 or number > ceiling:
                errors.append(f"progress value {value_string(value)} at {label!r} is outside {bound}")
    return errors


def build_spec(series: dict, variant: str, emphasize: int | None = None,
               quiet_zone: str = "right", builder: str | None = None) -> dict:
    """The page spec; pure and deterministic - the input dict is never mutated. `builder` forces the page's builder
    (P48 T2: a derived rescale state keeps the PAGE's builder even when its window holds too few points to read as dense)."""
    if quiet_zone not in QUIET_ZONES:
        raise ValueError(f"quiet_zone must be one of {'|'.join(QUIET_ZONES)}")
    builder = builder or pick_builder(series, variant)
    spec: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "surface": "page", "builder": builder,
        "variant": variant, "title": series.get("title"), "sub": series.get("sub", ""),
        "source": series.get("src"), "quiet_zone": quiet_zone,
        **({"src_style": series["src_style"]} if series.get("src_style") in ("compact",) else {}),   # the design pass (2026-09-07): a citation takes minimal space
        **({"line_unit": series["line_unit"]} if isinstance(series.get("line_unit"), str) else {}),   # P47 T9: a combo's lines take their own right axis in this unit
        **({"legend_in_sub": True} if series.get("legend_in_sub") else {}),   # the sub names the lines by colour: no inline name (it would repeat and collide)
        **({"tiers": True} if series.get("tiers") else {}),   # the macro-chart intake: bars and lines in two bands sharing one x, each on its own scale
        **({"build_s": float(series["build_s"])} if isinstance(series.get("build_s"), (int, float)) and not isinstance(series.get("build_s"), bool) and series["build_s"] > 0 else {}),   # the page draws over its own seconds
        "labels": [], "values": [], "value_strings": [], "colors": [],
    }
    if builder == "object":
        spec.update(_object_block(series))
        spec["unit"] = ""
        spec["judge"] = review_notes(series)
        spec["badges"] = badges_for(series)
        spec["emphasize"] = None
        return spec
    if builder == "share":
        spec.update(_share_block(series))
        spec["unit"] = str(series["unit"]) if _text(series.get("unit")) else ""
        spec["judge"] = review_notes(series)
        spec["badges"] = badges_for(series)
        spec["emphasize"] = int(series.get("emphasize") if emphasize is None else emphasize)
        return spec
    if builder == "race":
        spec.update(_race_block(series))
    elif builder == "dense-line":
        spec.update(_dense_block(series))
    else:
        spec.update(_story_block(series))
    if builder == "combo":
        spec.update({k: v for k, v in _dense_block(series).items() if k != "labels"})
    if builder == "decline":
        spec.update(_decline_block(series, spec))
    if variant == "progress" and "denominator" in series:
        spec["denominator"] = value_string(series["denominator"])
    spec["unit"] = str(series["unit"]) if _text(series.get("unit")) else ""
    spec["judge"] = review_notes(series)
    spec["badges"] = badges_for(series)
    count = len(spec["labels"])
    spec["emphasize"] = None if emphasize is None or not count else max(0, min(int(emphasize), count - 1))
    return spec


def _object_block(series: dict) -> dict:
    """Props, normalised. `at: "datum"` keeps its index so the renderer can resolve the
    prop against a chart datum - the same resolveTarget the callout and spotlight species
    already use, which is what lets an object be manipulated in relation to data."""
    props = []
    for p in series.get("props") or []:
        if not isinstance(p, dict):
            continue
        entry = {"asset": p.get("asset"), "at": p.get("at", "centre")}
        for k in ("index", "figure", "label", "scale", "draw_s", "enters_at"):
            if p.get(k) is not None:
                entry[k] = p[k]
        props.append(entry)
    return {"props": props, "labels": [], "values": [], "value_strings": [], "colors": []}


def _share_block(series: dict) -> dict:
    """The slices verbatim, plus the peel. E53 s1(b): every slice but the claim's is muted context, so a slice that
    declares no colour takes the de-emphasis token rather than a series accent it did not ask for."""
    shares = series.get("shares") or []
    emph = series.get("emphasize")
    peel = dict(series.get("peel") or {})
    return {"labels": [str(s.get("label")) for s in shares],
            # a wedge is narrow: a slice may name itself short for the page and keep its full name for the record
            "short_labels": [str(s.get("short") or s.get("label")) for s in shares],
            "values": [to_number(s.get("value")) for s in shares],
            "value_strings": [value_string(s.get("value_string", s.get("value"))) for s in shares],
            "colors": [str(s.get("color") or ("crimson" if i == emph else "deemph")) for i, s in enumerate(shares)],
            "peel": peel}


def _decline_block(series: dict, spec: dict) -> dict:
    """start/end verbatim, display_labels readable; a dense-series decline keeps its axes."""
    dense = dense_series(series)
    axes = _dense_block(series)["axes"] if dense else {}
    labels = series.get("labels") if isinstance(series.get("labels"), list) else None
    ends, displays = {}, {}
    for key, i in (("start", 0), ("end", len(spec["labels"]) - 1)):
        token = spec["labels"][i]
        ends[key] = {"label": token, "value": spec["values"][i], "value_string": spec["value_strings"][i]}
        displays[key] = display_label(token, i, axes.get("xticks"), labels) if dense else str(token)
    displays["series"] = (dense[0].get("name") or dense[0].get("label")) if dense else None
    return {**ends, "display_labels": displays, **({"axes": axes} if dense else {})}


def _story_block(series: dict) -> dict:
    labels, raw, colors = story_data(series)
    # a BARS page carries its axes too, so it can declare a comparator rule (`hlines`) - the device that lets the
    # GAP between a reference and a taller bar be drawn instead of subtracted (E53 s6, operator 2026-09-08)
    axes = {k: copy.deepcopy(series[k]) for k in AXES_KEYS if k in series}
    return {"labels": list(labels), "values": [to_number(v) for v in raw],
            "value_strings": [value_string(v) for v in raw], "colors": list(colors),
            **({"axes": axes} if axes else {})}


def _dense_block(series: dict) -> dict:
    # P48 T3: a series marked `later: true` waits off the page - an `extend` derives the state that draws it on
    return {"labels": [s.get("name") or s.get("label") for s in dense_series(series) if not s.get("later")],
            "series": copy.deepcopy([s for s in (series.get("series") or []) if not (isinstance(s, dict) and s.get("later"))]),
            "axes": {k: copy.deepcopy(series[k]) for k in AXES_KEYS if k in series}}


def _race_block(series: dict) -> dict:
    rows = race_rows(series)
    return {"periods": copy.deepcopy(race_periods(series)), "labels": [r["name"] for r in rows],
            "values": [[to_number(v) for v in r["values"]] for r in rows],
            "value_strings": [[value_string(v) for v in r["values"]] for r in rows],
            "colors": [r["color"] for r in rows]}


# ---- PAGE GEOMETRY (ruling E45 §1, 2026-09-06) ------------------------------------------------
# "The placement is computed from the page's own geometry by the compiler, not hand-placed per
# shot." The page's boxes live in the PLAYER (the template lays a portrait page out top-down in
# stage px and a landscape page in fractions of the board), so this is a READ-ONLY MIRROR of that
# layout: the same constants, the same order of operations, reported in stage pixels so the
# compiler can park a dock clear of the ink. It adds an accessor and changes no existing output -
# `build_spec` is untouched and the golden frames stay pinned.
#
# The one thing the template does that Python cannot is MEASURE the handwriting. Title, sub and
# source wrap at run time in Kalam; here they are wrapped greedily with an average advance
# calibrated against the rendered golden page (bold 0.52 em, regular 0.44 em - the golden's
# 3-line title, 2-line sub and 1-line source all reproduce). A page whose ink lands one line off
# the estimate shifts these boxes by one line height, which is why the dock placement leaves a pad
# and parks against the PLOT's edge (protecting the chart, per E45) rather than the title's.
STAGE_PX = {"16:9": (1920, 1080), "9:16": (1080, 1920)}
# doc 49 §49.1 / doc 50: platform chrome covers the top 280, the bottom 480 and the right 200 of a
# 1080x1920 short; everything that must be read lives in x[80,880] y[280,1340].
SAFE_BOX = {"9:16": (80, 280, 800, 1060), "16:9": (64, 64, 1792, 814)}
# the anchored caption's strip - a dock demotes the caption to it, so a dock may never sit there
CAPTION_ANCHOR = {"9:16": (80, 1290, 800, 150), "16:9": (145, 878, 1630, 82)}
PORTRAIT_LAYOUT = {"TOP": 150, "X": 80, "W": 800, "TITLE_W": 920, "BOTTOM": 1280, "GAP": 24, "CHART_MIN": 320}
PORTRAIT_INK = {"title": (68, 1.12, 0.52, 920), "sub": (40, 1.25, 0.44, 800), "src": (40, 1.25, 0.44, 800)}
PORTRAIT_PLOT = {"L": 150, "R": 70, "T": 90, "B": 80}
PORTRAIT_PILL_H, PORTRAIT_PILLS_PER_ROW = 132, 3   # the badge rail's row height and how many fit 800px
YLABEL_H = 52          # axes.ylabel floats top-left INSIDE the plot (template: lpYLabel at T-12)
XTICK_H = 62           # the x tick labels hang below the axis line (y = B + 52, 40px type)
LAND_BOARD = (0.06, 0.08, 0.88, 0.84)   # s9.26 default board; the punch crops to 1/PUNCH_SCALE
PUNCH_SCALE = 1.16
LAND_PLOT = {"L": 0.070, "R": 0.220, "T": 0.071, "B": 0.839}   # dense-line margins / the 1000x560 viewBox


def _ink_lines(text: str, size_px: float, box_w: float, advance: float) -> int:
    """Greedy word wrap at `advance` ems per character - the line count the page will write."""
    words = str(text or "").split()
    if not words:
        return 0
    char, lines, run = size_px * advance, 1, 0.0
    for word in words:
        want = len(word) * char
        if run and run + char + want > box_w:
            lines, run = lines + 1, want
        else:
            run = run + char + want if run else want
    return lines


def _ink_height(text: str, key: str) -> float:
    size, line_h, advance, box_w = PORTRAIT_INK[key]
    return _ink_lines(text, size, box_w, advance) * size * line_h


def first_clause(text: str, sentence: bool) -> str:
    """The portrait copy rule, mirrored: the sub keeps its first clause (to ';' or the first
    sentence end), the source its first clause (to ';') - one column has no room for the rest."""
    value = str(text or "")
    cuts = [i for i in (value.find(";"), value.find(". ") if sentence else -1) if i > 0]
    if not cuts:
        return value
    i = min(cuts)
    return value[: i + (1 if value[i] == "." else 0)].strip()


def _box(x: float, y: float, w: float, h: float) -> dict:
    return {"x": round(x), "y": round(y), "w": round(w), "h": round(h)}


def _portrait_boxes(spec: dict, w_s: int, h_s: int) -> dict:
    P, PL = PORTRAIT_LAYOUT, PORTRAIT_PLOT
    title_h = _ink_height(spec.get("title"), "title")
    sub_h = _ink_height(first_clause(spec.get("sub"), True), "sub")
    src_h = _ink_height(first_clause(spec.get("source"), False), "src")
    rail = [b for b in spec.get("badges") or [] if not b.get("inline")]
    rail_h = PORTRAIT_PILL_H * -(-len(rail) // PORTRAIT_PILLS_PER_ROW) if rail else 0
    sub_top = P["TOP"] + title_h + 16
    chart_top = sub_top + sub_h + P["GAP"] + 8
    chart_h = max(P["CHART_MIN"], P["BOTTOM"] - chart_top
                  - (src_h + P["GAP"] if src_h else 0) - (rail_h + P["GAP"] if rail_h else 0))
    src_top = chart_top + chart_h + P["GAP"]
    plot_top = chart_top + PL["T"] - (YLABEL_H if (spec.get("axes") or {}).get("ylabel") else 0)
    plot_bot = chart_top + chart_h - PL["B"] + XTICK_H
    return {
        "title": _box(P["X"], P["TOP"], P["TITLE_W"], title_h),
        "sub": _box(P["X"], sub_top, P["W"], sub_h),
        "chart": _box(P["X"], chart_top, P["W"], chart_h),
        "plot": _box(P["X"] + PL["L"], plot_top, P["W"] - PL["L"] - PL["R"], plot_bot - plot_top),
        "source": _box(P["X"], src_top, P["W"], src_h),
        "rail": _box(P["X"], src_top + (src_h + P["GAP"] if src_h else 0), P["W"], rail_h),
    }


def _landscape_boxes(spec: dict, w_s: int, h_s: int) -> dict:
    bx, by, bw, bh = LAND_BOARD
    half = 0.5 / PUNCH_SCALE
    vx, vy = bx + bw / 2 - half, by + bh / 2 - half
    rx, ry = max(bx, vx), max(by, vy)
    rw, rh = min(bx + bw, vx + 2 * half) - rx, min(by + bh, vy + 2 * half) - ry
    cx, cy, cw, ch = rx + 0.03 * rw, ry + 0.15 * rh, 0.94 * rw, 0.74 * rh
    qz = spec.get("quiet_zone")
    chart_w = (0.6 if qz else 0.9) * cw
    chart_x = cx + (0.4 if qz == "left" else 0.05) * cw
    L = LAND_PLOT
    return {
        "title": _box(max(bx + 0.027, vx + 0.03) * w_s, max(by + 0.024, vy + 0.035) * h_s, chart_w * w_s, 46),
        "sub": _box(chart_x * w_s, (max(by + 0.024, vy + 0.035) + 0.056) * h_s, chart_w * w_s, 54),
        "chart": _box(chart_x * w_s, cy * h_s, chart_w * w_s, ch * h_s),
        "plot": _box((chart_x + L["L"] * chart_w) * w_s, (cy + L["T"] * ch) * h_s,
                     (1 - L["L"] - L["R"]) * chart_w * w_s, (L["B"] - L["T"]) * ch * h_s + 40),
        "source": _box(chart_x * w_s, (cy + ch + 0.012) * h_s, chart_w * w_s, 32),
        "rail": _box(chart_x * w_s, (cy + ch + 0.044) * h_s, chart_w * w_s, 48),
    }


def page_boxes(spec: dict, aspect: str = "16:9") -> dict:
    """Where this page puts its ink, in STAGE pixels (E45 §1).

    Keys: ``stage``/``safe``/``caption_anchor`` (the frame's own bands) and ``title``/``sub``/
    ``chart``/``plot``/``source``/``rail`` (the page's), each ``{x, y, w, h}``; ``quiet_zone``
    passes the spec's declared side through. ``plot`` is the DATA box plus the ink that lives
    inside it - the basis label above it (``axes.ylabel``) and the x tick labels below the axis -
    because a card over either of them covers the chart just as surely.

    Pure and deterministic; the spec is never mutated. An `object` page (no chart) reports the
    prop's field as its chart and an empty plot."""
    if aspect not in STAGE_PX:
        raise ValueError(f"aspect must be one of {'|'.join(STAGE_PX)}")
    w_s, h_s = STAGE_PX[aspect]
    boxes = (_portrait_boxes if aspect == "9:16" else _landscape_boxes)(spec, w_s, h_s)
    if spec.get("builder") == "object":
        boxes["plot"] = _box(boxes["chart"]["x"], boxes["chart"]["y"], 0, 0)
    sx, sy, sw, sh = SAFE_BOX[aspect]
    cx, cy, cw, ch = CAPTION_ANCHOR[aspect]
    return {"aspect": aspect, "stage": _box(0, 0, w_s, h_s), "safe": _box(sx, sy, sw, sh),
            "caption_anchor": _box(cx, cy, cw, ch), "quiet_zone": spec.get("quiet_zone"), **boxes}


def load_series(path: Path) -> dict:
    """Decode with parse_float=str so every float stays the file's own token."""
    data = json.loads(path.read_text(encoding="utf-8"), parse_float=str)
    if not isinstance(data, dict):
        raise ValueError("top level must be a JSON object")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="series.json -> ledger page spec (doc 29 s9.26)")
    parser.add_argument("series", help="the ev-*.series.json beside the asset")
    parser.add_argument("--variant", required=True, choices=VARIANTS)   # `share` is the donut exception; see SHARE_BOUNDS
    parser.add_argument("--emphasize", type=int, default=None, help="index of the emphasized datum")
    parser.add_argument("--quiet-zone", default="right", choices=QUIET_ZONES, help="where docks land (s9.28 B3)")
    parser.add_argument("--out", default=None, help="spec path; default <name>.page.json beside the input")
    args = parser.parse_args(argv)
    path = Path(args.series)
    try:
        series = load_series(path)
    except (OSError, ValueError) as exc:
        print(f"ledger_page: cannot read {path}: {exc}", file=sys.stderr)
        return EXIT_INVALID
    errors = validate(series, args.variant)
    if errors:
        print(f"ledger_page: {path} is not a page ({args.variant}):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return EXIT_INVALID
    spec = build_spec(series, args.variant, args.emphasize, args.quiet_zone)
    for note in spec.get("judge", []):
        print(f"  [JUDGE] {note}")
    stem = path.name[: -len(".series.json")] if path.name.endswith(".series.json") else path.stem
    out = Path(args.out) if args.out else path.with_name(f"{stem}.page.json")
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    count = (sum(len(_points(s)) for s in spec.get("series", []))
             + sum(len(v) if isinstance(v, list) else 1 for v in spec["values"]))
    print(f"{spec['builder']} {spec['variant']} {count} values source={spec['source']!r} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

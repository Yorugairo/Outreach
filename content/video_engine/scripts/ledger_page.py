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
Rejected clearly: "checklist" (a table) and "shares" (a donut; no page variant).
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
VARIANTS = ("line", "bars", "race", "decline", "progress")
QUIET_ZONES = ("left", "right")
AXES_KEYS = ("log", "ylabel", "xticks", "hlines", "hline", "marks", "eventbars",
             "ymin", "ymax", "yfmt", "yunit", "panels")
UNCHARTABLE = {
    "checklist": "no chartable values: 'checklist' is a table, not a chart (keep it a dock)",
    "shares": f"no chartable values: 'shares' is a donut; no page variant takes it ({'|'.join(VARIANTS)})",
}
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
    month = min(11, int((year - whole) * 12))
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
    has_race = any(r["values"] for r in race_rows(series))
    if not (_bars(series) or dense_series(series) or has_race):
        return errors + [next((v for k, v in UNCHARTABLE.items() if k in series), UNCHARTABLE_DEFAULT)]
    if variant in VARIANTS:
        errors += _validate_shape_for_variant(series, variant)
    errors += _validate_sign_in_geometry(series)
    return errors + _validate_values(series, variant) + _validate_variant(series, variant)


SIGNED_NOTE_RE = re.compile(r"^\s*[+\u2212-]\s*\d")
MONTH_LABEL_RE = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*'?(\d{2}|\d{4})$")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


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
               quiet_zone: str = "right") -> dict:
    """The page spec; pure and deterministic - the input dict is never mutated."""
    if quiet_zone not in QUIET_ZONES:
        raise ValueError(f"quiet_zone must be one of {'|'.join(QUIET_ZONES)}")
    builder = pick_builder(series, variant)
    spec: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "surface": "page", "builder": builder,
        "variant": variant, "title": series.get("title"), "sub": series.get("sub", ""),
        "source": series.get("src"), "quiet_zone": quiet_zone,
        "labels": [], "values": [], "value_strings": [], "colors": [],
    }
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
    return {"labels": list(labels), "values": [to_number(v) for v in raw],
            "value_strings": [value_string(v) for v in raw], "colors": list(colors)}


def _dense_block(series: dict) -> dict:
    return {"labels": [s.get("name") or s.get("label") for s in dense_series(series)],
            "series": copy.deepcopy(series.get("series") or []),
            "axes": {k: copy.deepcopy(series[k]) for k in AXES_KEYS if k in series}}


def _race_block(series: dict) -> dict:
    rows = race_rows(series)
    return {"periods": copy.deepcopy(race_periods(series)), "labels": [r["name"] for r in rows],
            "values": [[to_number(v) for v in r["values"]] for r in rows],
            "value_strings": [[value_string(v) for v in r["values"]] for r in rows],
            "colors": [r["color"] for r in rows]}


def load_series(path: Path) -> dict:
    """Decode with parse_float=str so every float stays the file's own token."""
    data = json.loads(path.read_text(encoding="utf-8"), parse_float=str)
    if not isinstance(data, dict):
        raise ValueError("top level must be a JSON object")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="series.json -> ledger page spec (doc 29 s9.26)")
    parser.add_argument("series", help="the ev-*.series.json beside the asset")
    parser.add_argument("--variant", required=True, choices=VARIANTS)
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

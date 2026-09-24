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
  tiers    {"tiers": [{"name", "unit", "series"|"pts"|"bars", + AXES_KEYS}], + AXES_KEYS}
           E79: same-unit tiers share ONE scale by default; ``independent: true`` (on the page, or on
           one tier) declares unrelated measures on their own scales. Undeclared same-unit tiers on
           different y-domains are a WARN (``spec["warnings"]``, printed ``[WARN]``) - see scale_warnings.
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
import functools
import hashlib
import json
import math
import re
import sys
from numbers import Real
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
VARIANTS = ("line", "bars", "race", "decline", "progress", "share", "object", "tiers", "treemap")
CHART_VARIANTS = ("line", "bars", "race", "decline", "progress", "share")
# `tiers` (P50 T9, R26-24; Bravos shots 35-36): N SMALL MULTIPLES on one page - N series, each in its
# own band with its own y-scale and its own honest zero (E53 s4), sharing ONE x. Two metrics whose
# units or magnitudes differ cannot share a y without one of them lying; what they CAN honestly share
# is the time axis, which is the comparison the sentence is making. `tiers: true` (a bool) stays what
# it was - the two-band combo's key - and builds byte-identically; `tiers: [...]` is this builder.
TIERS_MIN, TIERS_MAX = 2, 4
# P69 T8b (E99 s104, amended twice): a `panels` object - the format the card's `chart_dock:panels` already draws - is
# a PAGE of 2-4 plots, each its own chart (its sub, its axes, its end tags), one scale across them by default (E79;
# `independent: true` gives each its own). The builder is `panels`; each panel is drawn by the dense-line builder
# inside its own box, and the boxes move by FOCUS STATES (`panel_focus`, the compiler's) - see `panel_layout`.
PANELS = "panels"
PANELS_MIN, PANELS_MAX = 2, 4
# `treemap` (P50 T6): the CENSUS page, under E53 s1's second amendment (ruled 2026-09-10).
# `object` is the page as a WORKING surface rather than an evidence surface: it draws
# a registered prop in ink on the cream instead of a chart. Same page clock, same
# deckle, same focus - so an object page can transform into a chart page without a
# plate change (RULE-the-page-is-the-ground, 2026-09-04).
PROP_PLACEMENTS = ("centre", "left", "right", "datum")
QUIET_ZONES = ("left", "right")
LANDSCAPE_PHONE = "landscape-phone"
# P69 T8 (E99 s97): the LONG FORM's page, measured off Bravos's frames (`docs/research/bravos-style/
# BRAVOS-LONGFORM-CHART-SPEC.md` (b)) - a flat ground, a framed plot panel, no gridlines, Inter - set in one of
# three named type presets (`longform:bravos|middle|phone`, LONGFORM_TYPE_SCALE below); on a dense-line page it
# widens the chart the way T17 does, for its own end tags.
LONGFORM = "longform"
READABILITY_PROFILES = (LANDSCAPE_PHONE, LONGFORM)
# the builders each profile is legal on (T14's inventory: the body's pages are dense-line and bars/`story`)
READABILITY_BUILDERS = {LANDSCAPE_PHONE: ("dense-line",), LONGFORM: ("dense-line", "story", PANELS)}   # P69 T8b: a panels page, each panel framed
AXES_KEYS = ("overflow", "log", "ylabel", "xticks", "from_zero", "highlight_from", "hlines", "hline", "marks", "eventbars",
             "name_clear",   # lift the inline series name clear of the data it would otherwise be written across
             "readability",  # R26-? closed, page-scoped chart typography/geometry profile
             "left_gutter",  # native story-bars y-axis reservation; absent preserves legacy geometry
             "ymin", "ymax", "yfmt", "yunit", "panels",
             "domain", "xdomain",   # P48 T2: a derived rescale state names its exact y domain and x window
             "overflow_placeholder", "overflow_capsule", "break_cadence",   # P50 T10 / T13: the breakthrough's furniture (E60)
             "independent")   # E79: this page (or this tier) carries unrelated measures, each on its own scale - nothing implies one
UNCHARTABLE = {
    "checklist": "no chartable values: 'checklist' is a table, not a chart (keep it a dock)",
    "shares": ("'shares' is a donut, and E53 s1 ranks angle and area at the bottom of the perception hierarchy: "
               "it is refused for every variant except --variant share, which the ruling's amendment (2026-09-07) "
               "allows only inside its four bounds - a part-to-whole claim about ONE named slice, that slice "
               "highlighted and the rest muted, the figure WRITTEN on the page, and five slices or fewer. "
               "A whole with MANY parts is a census: --variant treemap (E53 s1's second amendment, 2026-09-10)"),
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
    if variant in ("tiers", "treemap"):   # P50 T9 / T6: the file's shape is the variant's own - there is nothing to infer
        return variant
    if variant == "line" and isinstance(series.get("panels"), list):   # P69 T8b: a PANELS object is a page of 2-4 plots
        return PANELS
    """Builder from the data shape and the variant (P35 Builder Architecture)."""
    if variant in ("race", "decline"):
        return variant
    dense = dense_series(series)
    if _bars(series) and dense:
        return "combo"
    if len(dense) > 1 or any(len(_points(s)) > STORY_MAX_VALUES for s in dense):
        return "dense-line"
    return "story"


# ---- P58 T5: THE TWO 2.5D CHART FORMS ----------------------------------------------------------------------
# E98 s3: *"bars with extrusion, a line on a tilted plane - the flat page stays the default"*. A FORM is how a
# page's chart is DRAWN, never what it says: the spec, the scale, the labels, the value capsule and the clock
# stay the flat page's, and the only thing that changes is the surface the marks stand on. Both are opt-in
# (`;form=<name>` on the shot row), and a page that names none compiles and paints byte-for-byte as it did.
#   The fit is a BUILDER's, not a variant's, because the builder is what owns the painter: `pick_builder` already
# turns a variant and a data shape into one of nine, and a form its builder cannot draw is refused BY NAME here -
# ONE rule, read by the compiler (which authors the row) and by `validate` (which reads an object naming one).
CHART_FORMS = ("extruded_bar", "tilted_line")
FORM_BUILDERS = {"extruded_bar": ("story",), "tilted_line": ("dense-line",)}
FORM_READS = {"extruded_bar": "a BARS page - every bar is drawn as a prism",
              "tilted_line": "a LINE page - the line is drawn on a tilted plane"}
TILT_DEG = 14.0        # the tilted plane's default turn about the page's own vertical axis, in degrees (E98 s3)
TILT_DEG_MAX = 89.0    # build_scene_timeline_f.PAGE_DEPTH["TILT_MAX"] - one limit, and the compiler checks it


def form_error(form: str, builder: str, where: str) -> str | None:
    """Is ``form`` a form THIS page's builder can draw? The message, or None. Pure."""
    if form not in CHART_FORMS:
        return (f"{where}: form {form!r} is not one of {'|'.join(CHART_FORMS)} "
                "(the two 2.5D chart forms; the flat page is the reading form and names none)")
    fits = FORM_BUILDERS[form]
    if builder not in fits:
        return (f"{where}: form={form} is {FORM_READS[form]}, and this page is built by {builder!r} "
                f"(the form is drawn by {'|'.join(fits)}). The flat page is the reading form - drop the option")
    return None


def _validate_readability(series: dict, variant: str) -> list[str]:
    """Validate the closed chart-readability profile before it can enter ``page.axes``.

    The profile is intentionally a source-level option, like ``ylabel`` and ``name_clear``;
    the renderer narrows its effect to the stamped 16:9 full-stage dense-line route.  Rejecting
    unknown values here keeps a typo from silently selecting legacy geometry or typography.
    """
    value = series.get("readability")
    if value is None:
        return []
    err = readability_error(series, value, pick_builder(series, variant))
    return [err] if err else []


def readability_error(page: dict, value: Any, builder: str) -> str | None:
    """Is ``value`` a profile THIS page can take? The message, or None. Pure.

    ONE rule, read by the series file's own field (`_validate_readability`) and by the shot row's
    ``;readability=<profile>`` (the compiler, P69 T8): the profile is closed, each is legal only on the
    builders `READABILITY_BUILDERS` names (refused by name elsewhere), never on a host plate (whose board
    was measured around a hand), and a dense-line page must fit its enlarged end tags on the stage."""
    parsed = parse_readability(value)
    if parsed is None:
        return (f"readability {value!r} is not one of {LANDSCAPE_PHONE}|{LONGFORM}"
                f"[:{'|'.join(LONGFORM_PRESETS)}]")
    value, preset = parsed
    legal = READABILITY_BUILDERS[value]
    if builder not in legal:
        if value == LANDSCAPE_PHONE:
            return f"readability={value!r} is only supported by the dense-line builder; this page uses {builder!r}"
        return (f"readability={value!r} is only supported by the {' and '.join(legal)} builders "
                f"(a line page and a bars page); this page uses {builder!r}")
    # `full_stage` is a compiler stamp, not a series-file field: the normal 16:9 page route adds it
    # after this source validation, while portrait leaves it absent.  Explicit host-plate geometry
    # is nevertheless incompatible and must not silently accept an option the renderer ignores.
    if page.get("board") or page.get("chart_box") or page.get("punch") is False:
        if value == LANDSCAPE_PHONE:
            return "readability='landscape-phone' is only supported by a 16:9 full_stage dense-line page"
        return f"readability={value!r} is only supported by a 16:9 full_stage page (a host plate keeps its own board)"
    if builder == "dense-line" and value == LANDSCAPE_PHONE:
        return _readability_fit_error(dict(page, readability=value))
    if builder == "dense-line" and longform_tag_form(page, preset) is None:
        return (f"readability={LONGFORM}:{preset} cannot keep even its end values inside the 16:9 stage "
                "(a value alone is the shortest end tag there is)")
    return None


# P69 T10b (the operator, 2026-09-22, on the T6 frames: "I think it should also have some sort of rounded edges, maybe
# shadows"; AMENDED the same day: the shadow is the prop's own cross-hatch, T6b v2): `;bar_style=soft` - every bar of a
# bars page gets ROUNDED SHOULDERS (its two corners away from zero; the two on zero stay square, so a bar still stands
# on its baseline) and a HATCHED SHADOW cast from the one stage light (the player's `LPBAR_SOFT` and `PROP_SHADOW`).
# A row option, legal on the bars (`story`) builder only, and never beside `;form=extruded_bar` - the prism is the 3D
# bar; soft is weight on the flat one. Absent, a page is byte-identical.
BAR_STYLES = ("soft",)
BAR_STYLE_BUILDERS = ("story",)


def bar_style_error(page: dict, value: Any, builder: str) -> str | None:
    """Is ``value`` a bar style THIS page can take? The message, or None. Pure."""
    if value not in BAR_STYLES:
        return f"bar_style {value!r} is not one of {'|'.join(BAR_STYLES)}"
    if builder not in BAR_STYLE_BUILDERS:
        return (f"bar_style={value} is how a BARS page draws its bars (the {'|'.join(BAR_STYLE_BUILDERS)} builder); "
                f"this page uses {builder!r}")
    if ((page.get("form") or {}).get("kind")) == "extruded_bar":
        return (f"bar_style={value} and form=extruded_bar are two bars on one page - the prism is the 3D bar, soft is "
                "weight on the flat one. Keep one")
    return None


def validate(series: dict, variant: str) -> list[str]:
    """Error strings; empty means the series is a page for this variant. Pure."""
    errors: list[str] = []
    errors += _validate_readability(series, variant)
    if "left_gutter" in series:
        gutter = series["left_gutter"]
        if isinstance(gutter, bool) or not isinstance(gutter, int) or not 60 <= gutter <= 300:
            errors.append("left_gutter must be an integer from 60 to 300 SVG units")
        if not series.get("bars") or pick_builder(series, variant) != "story":
            errors.append("left_gutter requires a story/bar chart")
    if series.get("form") is not None:   # P58 T5: an OBJECT naming a form is held to the same one rule the row is
        err = form_error(str(series["form"]), pick_builder(series, variant), "form")
        if err:
            errors.append(err)
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
    if variant == "tiers":
        return errors + _validate_tiers(series)
    if pick_builder(series, variant) == PANELS:   # P69 T8b
        return errors + _validate_panels(series)
    if variant == "treemap":
        return errors + _validate_treemap(series)
    has_race = any(r["values"] for r in race_rows(series))
    if variant != "share" and "shares" in series and not (_bars(series) or dense_series(series)):
        return errors + [UNCHARTABLE["shares"]]
    if not (_bars(series) or dense_series(series) or has_race):
        return errors + [next((v for k, v in UNCHARTABLE.items() if k in series), UNCHARTABLE_DEFAULT)]
    if variant in CHART_VARIANTS:
        errors += _validate_shape_for_variant(series, variant)
    errors += _validate_overflow(series, variant)
    errors += _validate_sign_in_geometry(series)
    errors += badge_key_conflicts(series)
    return errors + _validate_values(series, variant) + _validate_variant(series, variant)


OVERFLOW_MODES = ("burst", "stack", "break")   # E60: burst is THE breakthrough (the rescale), stack an option; "break" is burst's alias
BURST_MODES = ("burst", "break")               # the rescale itself; the stack already steps, so the blend has nothing to add to it
CAPSULE_MODES = ("axis",)                      # P50 T10: the value capsule mounted ON THE AXIS under the bar's end (Bravos 8:02.6);
                                               # absent = the pill above the tip, which stays the default
BREAK_CADENCES = ("stop",)                     # P50 T13 / R26-30 (E60, the operator's blend): the shoot stepped on stopaction's
                                               # cadence rule; absent = the continuous burst, which is the ruled default
PLACEHOLDER_MAX = 3                            # a placeholder is a MARK, not a caption: "?" is the one Bravos uses.
                                               # NOT `placeholder`, which since the intake has meant "these figures are
                                               # still SOURCES-TO-VERIFY and this page never renders" (AGENTS.md: figures
                                               # are never fabricated) - hence the sibling naming, after the mechanic each furnishes


def _validate_overflow(series: dict, variant: str) -> list[str]:
    """E60 (the operator, 2026-09-10: "the re-scale is the way"): a bars page may STATE a scale (`domain`) that ONE value cannot
    fit and name how that bar breaks it (`overflow`). Checked, not trusted: the mechanic is one we have; the scale is stated;
    one bar breaks it; one bar reads on it - a stated scale no bar needs is a lie of the other kind."""
    ovf = series.get("overflow")
    errors: list[str] = []
    # P50 T10 / T13: every piece of furniture belongs to a breakthrough. Declared without one it is a dial nothing
    # reads, which is worse than an error - so it IS one, and it names the key.
    furniture = [k for k in ("overflow_placeholder", "overflow_capsule", "break_cadence") if series.get(k) is not None]
    if ovf is None:
        return errors + [f"{k} is the breakthrough's furniture and this page declares no 'overflow' (E60, P50 T10/T13)"
                         for k in furniture]
    if ovf not in OVERFLOW_MODES:
        errors.append(f"overflow {ovf!r} is not one of {'|'.join(OVERFLOW_MODES)} (E60: burst is the breakthrough, stack an option)")
    if variant != "bars":
        errors.append(f"overflow is a BARS page's device (E60); this page is {variant!r}")
    dom = series.get("domain")
    dom = [to_number(x) for x in dom] if isinstance(dom, list) else None   # floats arrive as their own tokens (load_series parse_float=str)
    if not (isinstance(dom, list) and len(dom) == 2 and all(x is not None for x in dom) and dom[1] > dom[0]):
        errors.append("overflow needs a stated scale: 'domain': [lo, hi] with hi > lo - the scale the honest bar reads on (E60)")
        return errors
    vals = [to_number(b.get("value")) for b in _bars(series)]
    vals = [v for v in vals if v is not None]
    if vals and not any(v > dom[1] for v in vals):
        errors.append(f"overflow declares a breakthrough no bar makes: no value is above the stated scale's top {dom[1]}")
    if vals and not any(v <= dom[1] for v in vals):
        errors.append(f"every bar is above the stated scale's top {dom[1]}: a stated scale no bar reads on is a lie of the other kind (E60)")
    return errors + _validate_burst_furniture(series, ovf)


def _validate_burst_furniture(series: dict, ovf: str) -> list[str]:
    """P50 T10 / T13 - the burst's three options, each off unless the object names it and each checked when it does.
    `overflow_placeholder` is the mark the breaking bar prints until its number is spoken (Bravos 8:01.8: a "?" track);
    `overflow_capsule` mounts the value capsule on the axis with a dotted leader; `break_cadence` steps the shoot on
    stopaction's cadence (E60's blend, R26-30)."""
    errors: list[str] = []
    ph = series.get("overflow_placeholder")
    if ph is not None and ph is not True:
        if not isinstance(ph, str) or not ph.strip():
            errors.append("overflow_placeholder is the MARK the breaking bar prints until its number is spoken: a short string, or true for '?'")
        elif len(ph.strip()) > PLACEHOLDER_MAX:
            errors.append(f"overflow_placeholder {ph!r} is {len(ph.strip())} characters: a placeholder is a mark, not a caption "
                          f"(<= {PLACEHOLDER_MAX}; Bravos stamps '?')")
    cap = series.get("overflow_capsule")
    if cap is not None and cap not in CAPSULE_MODES:
        errors.append(f"overflow_capsule {cap!r} is not one of {'|'.join(CAPSULE_MODES)} (P50 T10: the capsule mounts on the "
                      "AXIS under the bar's end; leave it out for the pill that rides the tip)")
    cad = series.get("break_cadence")
    if cad is not None:
        if cad not in BREAK_CADENCES:
            errors.append(f"break_cadence {cad!r} is not one of {'|'.join(BREAK_CADENCES)} (P50 T13: 'stop' is the blend; "
                          "leave it out for the continuous burst, which E60 ruled the default)")
        elif ovf not in BURST_MODES:
            errors.append(f"break_cadence is the BURST's cadence (E60's blend); this page's overflow is {ovf!r}, which already steps")
    return errors


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


# ---- TIERS (P50 T9, R26-24; Bravos shots 35-36) -------------------------------------------------
# N small multiples on ONE page: N bands stacked, each with its own y-scale and its own honest zero
# (E53 s4), sharing ONE x. The tier titles are the series' own names; the page's title stays the
# argument. Two metrics that differ in unit or in magnitude cannot share a y without one of them
# lying; what they can honestly share is the TIME AXIS, which is the comparison being made.
def _tier_entries(series: dict) -> list:
    """The declared tiers, verbatim (an entry that is not an object is kept so the error can name it)."""
    return list(series["tiers"]) if isinstance(series.get("tiers"), list) else []


def _tier_lines(tier: dict) -> list[dict]:
    """A tier's line series: its own ``series`` list, or the ``pts`` shorthand read as one series."""
    if not isinstance(tier, dict):
        return []
    own = [s for s in (tier.get("series") or []) if isinstance(s, dict) and "pts" in s]
    if not own and isinstance(tier.get("pts"), list):
        own = [{k: v for k, v in tier.items() if k not in ("series", "bars", "unit")}]
    return own


def _tier_x(tier: dict) -> tuple | None:
    """This tier's x signature: ``("num", lo, hi)`` for points (or bars carrying their own x),
    ``("cat", labels)`` for category bars. None when the tier has no data to span."""
    xs = [to_number(p[0]) for s in _tier_lines(tier) for p in _points(s)]
    xs += [to_number(b.get("x")) for b in _bars(tier) if b.get("x") is not None]
    xs = [x for x in xs if x is not None]
    if xs:
        return ("num", min(xs), max(xs))
    labels = [str(b.get("label")) for b in _bars(tier)]
    return ("cat", tuple(labels)) if labels else None


def _x_same(a: tuple, b: tuple) -> bool:
    if a[0] != b[0]:
        return False
    if a[0] == "cat":
        return a[1] == b[1]
    span = max(1.0, abs(a[2] - a[1]), abs(b[2] - b[1]))
    return abs(a[1] - b[1]) <= 1e-9 * span and abs(a[2] - b[2]) <= 1e-9 * span


def _x_text(sig: tuple | None) -> str:
    if sig is None:
        return "nothing"
    return f"{sig[1]:g}..{sig[2]:g}" if sig[0] == "num" else "|".join(sig[1])


def _validate_tiers(series: dict) -> list[str]:
    """A tiers page's contract: N in [TIERS_MIN, TIERS_MAX], every band named, united and fed, one
    shared x. Every failure names the band it came from - a page of small multiples is only honest
    while the x is the same x, so that check is the whole point of the builder."""
    tiers = _tier_entries(series)
    if not isinstance(series.get("tiers"), list) or len(tiers) < TIERS_MIN:
        return [f"a tiers page needs 'tiers': a list of at least {TIERS_MIN} bands, each {{name, unit, "
                "series|pts|bars}} - one band is a line page, and `tiers: true` is the two-band COMBO's key, not this"]
    errors: list[str] = []
    if len(tiers) > TIERS_MAX:
        errors.append(f"{len(tiers)} tiers: the ceiling is {TIERS_MAX}. On a 9:16 stage the plot is ~1060 px tall, so "
                      f"{TIERS_MAX} bands leave each about a quarter of it (~250 px) - a band under that cannot carry "
                      "its own scale, its name and a readable line at once. Split the page.")
    sigs: list[tuple] = []
    for i, tier in enumerate(tiers):
        where = f"tiers[{i}]"
        if not isinstance(tier, dict):
            errors.append(f"{where} is not an object"); continue
        name = tier.get("name") or tier.get("title")
        if not _text(name):
            errors.append(f"{where} has no 'name': the tier titles ARE the series' names on a tiers page (the page's title stays the argument)")
        else:
            where = f"tiers[{i}] {name!r}"
        if not _text(tier.get("unit")):
            errors.append(f"{where} has no 'unit': each band carries its own scale, and a scale with no unit is a number with no meaning (E53 s4)")
        lines, bars = _tier_lines(tier), _bars(tier)
        if not lines and not bars:
            errors.append(f"{where} has no data: a band takes 'series'/'pts' ([x, y] pairs) or 'bars'")
        for j, entry in enumerate(lines):
            raw = entry.get("pts") or []
            bad = [p for p in raw if not (isinstance(p, (list, tuple)) and len(p) == 2
                                          and to_number(p[0]) is not None and to_number(p[1]) is not None)]
            if bad or len(raw) < 2:
                errors.append(f"{where} series[{j}] pts must be at least two [x, y] numeric pairs ({len(bad)} bad of {len(raw)})")
        for j, bar in enumerate(bars):
            if to_number(bar.get("value")) is None:
                errors.append(f"{where} bars[{j}] value {bar.get('value')!r} is not numeric")
            if not _text(bar.get("label")):
                errors.append(f"{where} bars[{j}] has no label (one label per datum)")
        sig = _tier_x(tier)
        sigs.append(sig)
        if sig and sigs[0] and not _x_same(sigs[0], sig):
            errors.append(f"{where} spans x {_x_text(sig)} while tiers[0] spans {_x_text(sigs[0])} - N tiers share ONE x "
                          "(that is what makes them small multiples, and the only thing the page claims across bands); "
                          "window the file to one x, or draw two pages")
    return errors


def _tiers_block(series: dict) -> dict:
    """The bands, normalised: one object per tier with its own data, its own unit and its own x span.
    The page's ``labels`` are the tier NAMES, so every count, emphasis and mark keyed off labels reads
    the bands - a tier is the tiers page's datum."""
    out = []
    for tier in _tier_entries(series):
        lines, bars = _tier_lines(tier), _bars(tier)
        sig = _tier_x(tier)
        band: dict[str, Any] = {
            "name": str(tier.get("name") or tier.get("title") or ""),
            "unit": str(tier.get("unit") or ""),
            "kind": "line" if lines else "bars",
            "axes": {k: copy.deepcopy(tier[k]) for k in AXES_KEYS if k in tier},
        }
        if lines:
            band["series"] = copy.deepcopy(lines)
        else:
            band.update({"labels": [b.get("label") for b in bars],
                         "values": [to_number(b.get("value")) for b in bars],
                         "value_strings": [value_string(b.get("value")) for b in bars],
                         "colors": [b.get("color") for b in bars]})
        if tier.get("color") is not None:
            band["color"] = tier["color"]
        if sig and sig[0] == "num":
            band["x"] = [sig[1], sig[2]]
        elif sig:
            band["x_labels"] = list(sig[1])
        out.append(band)
    axes = {k: copy.deepcopy(series[k]) for k in AXES_KEYS if k in series}
    return {"tiers": out, "labels": [b["name"] for b in out],
            # the page's OWN axes ride at the top level: the x is shared, so its ticks belong to the page
            # and not to any one band (a band that named the x would be claiming the page's only shared scale)
            **({"axes": axes} if axes else {}),
            "values": [], "value_strings": [], "colors": []}


# ---- E79: side-by-side panels of the same measure share one scale (the operator, 2026-09-13) ------
# The defect: each panel computed its own y-range from its own data, so 4.7% drew above 5.0% under a
# subtitle promising one scale. The `panels` form already shares one scale in the engine; a `tiers`
# band computes its own (tierDomain), so this is where same-unit panels can disagree. The compiler
# WARNs; it does not set the domain, because the engine's band reads only its own data.
TIERS_PAD = 0.08   # mirror of TIERS.PAD in scripts/species/tiers.mjs (proportional, so equal raw domains stay equal)


def _declared_domain(axes: dict) -> tuple[float, float] | None:
    dom = axes.get("domain")
    if isinstance(dom, (list, tuple)) and len(dom) == 2:
        lo, hi = to_number(dom[0]), to_number(dom[1])
        if lo is not None and hi is not None and hi > lo:
            return (lo, hi)
    return None


def tier_domain(tier: dict) -> tuple[float, float] | None:
    """One tier's y-domain before padding: its stated `domain`, else its values with the zero kept
    unless `from_zero: false` (tierDomain's rule), widened by any `ymin`/`ymax`. None without data."""
    if not isinstance(tier, dict):
        return None
    stated = _declared_domain(tier)
    if stated:
        return stated
    vals = [to_number(p[1]) for s in _tier_lines(tier) for p in _points(s)]
    vals += [to_number(b.get("value")) for b in _bars(tier)]
    vals += [to_number(tier.get(k)) for k in ("ymin", "ymax") if tier.get(k) is not None]
    nums = [v for v in vals if v is not None]
    if not nums:
        return None
    lo, hi = min(nums), max(nums)
    if tier.get("from_zero") is not False:
        lo, hi = min(0.0, lo), max(0.0, hi)
    return (lo, hi)


def _same_unit_groups(series: dict) -> dict[str, list[tuple[str, tuple[float, float]]]]:
    """unit -> [(tier name, domain)] for every tier that shares a scale: none when the page declares
    `independent`, and a tier that declares it leaves its group."""
    if series.get("independent") is True:
        return {}
    groups: dict[str, list] = {}
    for i, tier in enumerate(_tier_entries(series)):
        if not isinstance(tier, dict) or tier.get("independent") is True or not _text(tier.get("unit")):
            continue
        dom = tier_domain(tier)
        if dom is not None:
            groups.setdefault(str(tier["unit"]), []).append((str(tier.get("name") or tier.get("title") or f"tiers[{i}]"), dom))
    return {u: g for u, g in groups.items() if len(g) >= 2}


def shared_tier_domains(series: dict) -> dict[str, tuple[float, float]]:
    """E79's standard: the ONE domain each same-unit group should share - min and max across its panels. Pure."""
    return {u: (min(d[0] for _, d in g), max(d[1] for _, d in g)) for u, g in _same_unit_groups(series).items()}


def _dom_text(dom: tuple[float, float]) -> str:
    return f"[{dom[0]:g}, {dom[1]:g}]"


def scale_warnings(series: dict) -> list[str]:
    """E79 WARN rows: same-unit panels on different y-domains with no `independent` declared. Pure."""
    page = series.get("id") or series.get("title") or "page"
    shared = shared_tier_domains(series)
    out = []
    for unit, group in _same_unit_groups(series).items():
        if len({(round(lo, 9), round(hi, 9)) for _, (lo, hi) in group}) < 2:
            continue
        panels = "; ".join(f"{name} {_dom_text(dom)}" for name, dom in group)
        out.append(f"E79 {page!s}: panels in {unit!r} carry different y-domains ({panels}) - panels of the same measure "
                   f"share one scale (shared: {_dom_text(shared[unit])}); if these are unrelated measures, declare "
                   "`independent: true` on the page or the tier")
    return out


# ---- PANELS (P69 T8b; E99 s104, amended twice) ---------------------------------------------------
# The operator: "no reason it shouldn't be able to, we already handle 2 evidence docks on world plates, it rhymes to
# have 2 data panels/charts on ledger plates when needed" - and, for row 21's four charts, "whatever is less important
# to be held on background/off-focus and brought back up at relevant times". The page is 2-4 LINE plots, each its own
# chart; the SCALE is E79's: panels of one measure share ONE y domain (the card's own rule - min and max over every
# panel, the reference rules and a declared ymin / ymax, the air on top and on the bottom unless ymin names the floor -
# `shared_panel_domain`), written onto each panel's axes so the engine's line builder draws it verbatim; `independent:
# true` on the page gives every panel its own, on a panel takes that one out of the group. A panel that DECLARES its
# own `domain` keeps it (the author places, the engine advises - E99 s106) and, if it shares a unit with the group, the
# build says so as E79's WARN (`panel_scale_warnings`), never a refusal.
PANEL_Y_PAD = 0.06   # the card's own air on the shared scale (scene-evidence-engine's chart_dock: `pad = (gy1 - gy0) * 0.06`)
PANEL_TICK_EDGE = 0.02   # a page x tick this share of a panel's span outside its data still belongs to it (1998 on a series from 1998.0027)


def _panel_entries(series: dict) -> list:
    """The declared panels, verbatim (a non-object entry is kept so the error can name it)."""
    return list(series["panels"]) if isinstance(series.get("panels"), list) else []


def _panel_lines(panel: dict) -> list[dict]:
    """A panel's line series (its `series` list; a `later` series waits off the page, as on a line page)."""
    return [s for s in (panel.get("series") or []) if isinstance(s, dict) and "pts" in s and not s.get("later")]


def _validate_panels(series: dict) -> list[str]:
    """A panels page's contract: 2-4 panels, each a named plot fed by line series. Every failure names its panel."""
    panels = _panel_entries(series)
    if len(panels) < PANELS_MIN:
        return [f"a panels page needs 'panels': a list of at least {PANELS_MIN} plots, each {{sub, series}} - one plot "
                "is a line page"]
    errors: list[str] = []
    if len(panels) > PANELS_MAX:
        errors.append(f"{len(panels)} panels: the ceiling is {PANELS_MAX} (E99 s104 amended: up to FOUR on a page, the "
                      "rest held in focus states - a fifth chart is a new page)")
    for i, panel in enumerate(panels):
        where = f"panels[{i}]"
        if not isinstance(panel, dict):
            errors.append(f"{where} is not an object")
            continue
        if not _text(panel.get("sub")):
            errors.append(f"{where} has no 'sub': a panel's sub IS its title line - two plots side by side must say "
                          "which is which")
        if not _panel_lines(panel):
            errors.append(f"{where} {panel.get('sub')!r} has no line series ('series': [{{name, pts}}])")
        if "independent" in panel and not isinstance(panel["independent"], bool):
            errors.append(f"{where}: independent must be true or false (E79)")
    return errors + _validate_values(series, "line") + badge_key_conflicts(series)


def panel_unit(series: dict, panel: dict) -> str:
    """The unit a panel's y axis measures: its own `yunit` / `unit`, else the page's."""
    for src in (panel, series):
        for key in ("yunit", "unit"):
            if _text(src.get(key)):
                return str(src[key])
    return ""


def _panel_raw_extent(series: dict, panel: dict) -> tuple[float, float] | None:
    """A panel's data extent, the page's reference rules and any declared ymin / ymax - the card's own inputs."""
    vals = [to_number(p[1]) for s in _panel_lines(panel) for p in _points(s)]
    rules = series.get("hlines") or ([series["hline"]] if isinstance(series.get("hline"), dict) else [])
    vals += [to_number(h.get("y")) for h in rules if isinstance(h, dict)]
    vals += [to_number(src.get(k)) for src in (series, panel) for k in ("ymin", "ymax") if src.get(k) is not None]
    nums = [v for v in vals if v is not None]
    return (min(nums), max(nums)) if nums else None


def _padded(lo: float, hi: float, floor_named: bool) -> list[float]:
    pad = (hi - lo) * PANEL_Y_PAD or 1.0
    return [lo if floor_named else lo - pad, hi + pad]


def shared_panel_domain(series: dict) -> list[float] | None:
    """E79: the ONE y domain every non-independent panel of this page draws on - the card's own rule, verbatim (min
    and max over the group's data, the reference rules and a declared ymin / ymax, padded 6 % unless ymin names the
    floor). None when every panel is independent. Pure."""
    group = [p for p in _panel_entries(series) if isinstance(p, dict) and not _panel_own_scale(series, p)]
    ext = [e for e in (_panel_raw_extent(series, p) for p in group) if e]
    if not ext:
        return None
    lo, hi = min(e[0] for e in ext), max(e[1] for e in ext)
    return _padded(lo, hi, series.get("ymin") is not None)


def _panel_own_scale(series: dict, panel: dict) -> bool:
    return series.get("independent") is True or panel.get("independent") is True or _declared_domain(panel) is not None


def _panel_domain(series: dict, panel: dict, shared: list[float] | None) -> list[float] | None:
    """The domain one panel is drawn on: its declared one, else (independent) its own padded extent, else the shared."""
    own = _declared_domain(panel)
    if own:
        return [own[0], own[1]]
    if not _panel_own_scale(series, panel):
        return shared
    ext = _panel_raw_extent(series, panel)
    return _padded(ext[0], ext[1], panel.get("ymin", series.get("ymin")) is not None) if ext else None


def panel_scale_warnings(series: dict) -> list[str]:
    """E79 on a panels page: a panel that DECLARES a domain of its own while it shares a unit with the grouped panels
    (no `independent`) - the author's domain stands (E99 s106), and the build says so. Pure."""
    shared = shared_panel_domain(series)
    if series.get("independent") is True or shared is None:
        return []
    page = series.get("id") or series.get("title") or "page"
    units = {panel_unit(series, p) for p in _panel_entries(series) if isinstance(p, dict) and not _panel_own_scale(series, p)}
    out = []
    for i, p in enumerate(_panel_entries(series)):
        own = _declared_domain(p) if isinstance(p, dict) else None
        if own is None or p.get("independent") is True or panel_unit(series, p) not in units:
            continue
        if (round(own[0], 9), round(own[1], 9)) != (round(shared[0], 9), round(shared[1], 9)):
            out.append(f"E79 {page!s}: panels[{i}] {str(p.get('sub') or '')!r} declares y-domain {_dom_text(own)} while the "
                       f"other panels in {panel_unit(series, p)!r} share {_dom_text(tuple(shared))} - panels of the same "
                       "measure share one scale; if this is an unrelated measure, declare `independent: true` on it")
    return out


def _panel_xticks(series: dict, panel: dict) -> list:
    """The page's x ticks that fall inside THIS panel's own x span (the card's rule: a tick outside it is not drawn),
    or the panel's own when it declares them."""
    if isinstance(panel.get("xticks"), list):
        return copy.deepcopy(panel["xticks"])
    xs = [to_number(p[0]) for s in _panel_lines(panel) for p in _points(s)]
    xs = [x for x in xs if x is not None]
    if not xs:
        return []
    lo, hi = min(xs), max(xs)
    edge = (hi - lo) * PANEL_TICK_EDGE   # a tick a hair outside the data's first or last x still states the span (E28)
    return [copy.deepcopy(t) for t in (series.get("xticks") or [])
            if isinstance(t, (list, tuple)) and len(t) == 2 and to_number(t[0]) is not None
            and lo - edge <= to_number(t[0]) <= hi + edge]


PANEL_PAGE_AXES = ("log", "from_zero", "name_clear", "yfmt")   # the page's axes every panel draws with
PANEL_RULE_TAIL = 0.4   # the share of a panel's own x span, at its right end, a rule's name is written over


def _panel_rule_home(series: dict) -> int:
    """Which panel NAMES the page's reference rules (a rule is named once - the card's rule): the one whose data stand
    LOWEST over the right end of its span, where the line builder writes a rule's name (right-aligned over the rule) -
    so the name reads on the panel's own ground, not across a line. The first panel on a tie."""
    best, where = None, 0
    for i, panel in enumerate(_panel_entries(series)):
        pts = [(to_number(p[0]), to_number(p[1])) for s in _panel_lines(panel) if isinstance(panel, dict) for p in _points(s)]
        pts = [(x, y) for x, y in pts if x is not None and y is not None]
        if not pts:
            continue
        lo, hi = min(x for x, _ in pts), max(x for x, _ in pts)
        tail = [y for x, y in pts if x >= hi - (hi - lo) * PANEL_RULE_TAIL]
        top = max(tail) if tail else max(y for _, y in pts)
        if best is None or top < best:
            best, where = top, i
    return where


def plain_panel_tag_form(series: dict, panel: dict) -> str:
    """A PLAIN (not long-form) panel's end-tag form: the fullest whose widest tag stands inside the panel's own right
    margin (the line builder's 220 units, less its tag gap) - a tag past it runs into the next panel or off the stage.
    `badge` keeps the value and the badge's chip, `value` the value alone."""
    room = LAND_PLOT["R"] * LAND_VIEWBOX[0] - LAND_TAG_GAP
    lines = _panel_lines(panel)
    for form in ("full", "badge", "value"):
        view = [dict(s, name="") if form != "full" and str(s.get("label") or "").strip() else s for s in lines]
        badges = [b for b in series.get("badges") or [] if isinstance(b, dict)] if form != "value" else []
        if tag_units({"builder": "dense-line", "series": view, "badges": badges}) <= room:
            return form
    return "value"


def _panels_block(series: dict) -> dict:
    """The panels, normalised - each a dense-line chart of its own: its `sub` (its title line), its live series, and
    its `axes` (the page's shared ones, its x ticks cut to its own span, the reference rules with their NAMES on the
    first panel only - the card's rule, a rule is named once - its unit on the tick labels, and the domain E79 gives
    it). The page's `labels` are the panels' subs: a panel is this page's datum, as a band is a tiers page's."""
    shared = shared_panel_domain(series)
    rules = series.get("hlines") or ([series["hline"]] if isinstance(series.get("hline"), dict) else [])
    named = _panel_rule_home(series)
    out = []
    for i, panel in enumerate(_panel_entries(series)):
        if not isinstance(panel, dict):
            continue
        axes = {k: copy.deepcopy(series[k]) for k in PANEL_PAGE_AXES if k in series}
        axes.update({k: copy.deepcopy(panel[k]) for k in AXES_KEYS if k in panel and k not in ("xticks", "domain")})
        axes["xticks"] = _panel_xticks(series, panel)
        if rules and "hlines" not in panel:
            axes["hlines"] = [dict(h) for h in copy.deepcopy(rules) if isinstance(h, dict)]   # every panel can name them; the
            # engine shows the names on ONE visible panel per focus state - `panel_rule_home` when it is in focus
        unit = panel_unit(series, panel)
        if unit:
            axes["unit"] = unit
        dom = _panel_domain(series, panel, shared)
        if dom is not None:
            axes["domain"] = [round(dom[0], 6), round(dom[1], 6)]
        axes["tag_form"] = plain_panel_tag_form(series, panel)   # the long form re-fits it at its preset (apply_longform)
        entry = {"sub": str(panel.get("sub") or ""), "series": copy.deepcopy(_panel_lines(panel)), "axes": axes}
        if panel.get("independent") is True:
            entry["independent"] = True
        out.append(entry)
    axes = {k: copy.deepcopy(series[k]) for k in AXES_KEYS if k in series and k != "panels"}   # the panels are the spec's own key
    return {"panels": out, "labels": [p["sub"] for p in out],
            **({"panel_rule_home": named} if rules else {}),
            **({"axes": axes} if axes else {}),
            "values": [], "value_strings": [], "colors": []}


# ---- TREEMAP (P50 T6; E53 s1's second amendment, the CENSUS exception, ruled 2026-09-10) ---------
# A whole broken into its parts by AREA. Area is the bottom of Cleveland & McGill's hierarchy, which
# is exactly why the exception is narrow: the page shows BREADTH (how many parts there are, and that
# a few of them are most of it) or marks a NAMED SUBSET and WRITES its share - it never asks anyone to
# compare two areas. A size claim takes its bar, and the builder refuses the file that carries one.
TREEMAP_ASPECT = 1.5        # the aspect the squarify tunes toward: 3:2, never 1:1 (Heer & Bostock 2010's square penalty - a square cell reads as a block, a 3:2 cell as a labelled thing)
TREEMAP_MIN_CELL = (80, 36)     # research s1 (ISO 9241-303 at a 30-40 cm handheld distance): under this, NO text - illegible ink blobs overlap and the mosaic reads as noise
TREEMAP_TWO_LINE = (110, 64)    # ... and the floor for two lines (label + value)
TREEMAP_VALUE_FONT = 18         # the absolute legible floor on a 1080x1920 stage; a value that would be written smaller is not written
TREEMAP_LABEL_FONT = (18, 32)   # the label's clamp
TREEMAP_PAD = 6                 # the cell's inner padding at 1080x1920 (research s2: glyph stems never touch a cell edge)
TREEMAP_CHAR_W = 0.72           # the advance the font clamp assumes. The research's own figure is 0.65 em; our cell labels are BOLD, and at 0.65 "Japan" touched its cell's right edge in the rendered frame (2026-09-11)
TREEMAP_LINE_H = {1: 1.5, 2: 2.2}   # the cell height one line of type needs, and two. The research's clamp divides by 2.2 whatever the line count, which contradicts the same document's 36 px single-line floor: at 2.2 a 44 px cell could never carry 18 px type. 2.2 is the TWO-line allowance; one line takes a line and a half
TREEMAP_MIN_SHARES = 3          # two parts of a whole is a share page (one named slice, the rest muted); a census starts at three
# E53 s1: a SIZE CLAIM takes its bar. The page that says "bigger than" is asking for exactly the
# comparison area cannot carry - the refusal names the bars page rather than silently drawing it.
SIZE_CLAIM_RE = re.compile(
    r"\b(bigger|larger|smaller|biggest|largest|smallest|dwarfs?|outweighs?|twice|thrice|triple|tripled|doubles?|doubled"
    r"|more than|less than|(?:\d+(?:\.\d+)?|two|three|four|five|six|seven|eight|nine|ten)\s*(?:x\b|times))\b", re.I)
SIZE_CLAIM_FIELDS = ("title", "sub", "claim")


def _size_claim(series: dict) -> tuple[str, str] | None:
    """(field, phrase) of the first size comparison the page's own words make, or None."""
    for field in SIZE_CLAIM_FIELDS:
        text = series.get(field)
        if not _text(text):
            continue
        hit = SIZE_CLAIM_RE.search(text)
        if hit:
            return field, hit.group(0)
    return None


def _treemap_shares(series: dict) -> list[dict]:
    return [s for s in (series.get("shares") or []) if isinstance(s, dict)]


def _validate_treemap(series: dict) -> list[str]:
    """A treemap page's contract. The census exception's own bounds, checked rather than trusted."""
    shares = series.get("shares")
    if not isinstance(shares, list) or len(shares) < TREEMAP_MIN_SHARES:
        return [f"a treemap page needs 'shares': at least {TREEMAP_MIN_SHARES} parts of one whole "
                "({label, value}) - two parts of a whole is a share page (--variant share), not a census"]
    errors: list[str] = []
    claim = _size_claim(series)
    if claim:
        errors.append(f"the page's {claim[0]} says {claim[1]!r}: a SIZE CLAIM takes its BAR (E53 s1) - area is the bottom of the "
                      "perception hierarchy and two cells of a treemap cannot be compared by eye. Draw the named values as "
                      "--variant bars, and keep the treemap for what it is good at: the census (how many parts, and which "
                      "named ones are struck out with their share written)")
    seen: set[str] = set()
    for i, sh in enumerate(_treemap_shares(series)):
        if not _text(sh.get("label")):
            errors.append(f"shares[{i}] has no label: a cell is named on itself, and an unnamed cell is counted in the legend")
        elif sh["label"] in seen:
            errors.append(f"shares[{i}] {sh['label']!r} is listed twice; one part, one cell")
        else:
            seen.add(sh["label"])
        v = to_number(sh.get("value"))
        if v is None or v <= 0:
            errors.append(f"shares[{i}] value {sh.get('value')!r} is not a positive number: a part of a whole has an area, and an area is positive")
    if len(_treemap_shares(series)) != len(shares):
        errors.append("every entry of 'shares' must be an object {label, value}")
    total = to_number(series.get("total"))
    if series.get("total") is not None and (total is None or total <= 0):
        errors.append(f"total {series.get('total')!r} is not a positive number (the whole the parts are parts of)")
    if total is not None and total > 0:
        summed = sum(to_number(s.get("value")) or 0.0 for s in _treemap_shares(series))
        if summed - total > 1e-6 * max(1.0, total):
            errors.append(f"the parts add up to {summed:g}, more than the declared total {total:g}: a part cannot exceed its whole")
    return errors


def _cost(w: float, h: float, target: float) -> float:
    """A cell's aspect COST against the target (Bruls 2000 s2 with the target left free): 1 at the
    target, growing either side of it. The paper minimises toward a SQUARE; Heer & Bostock 2010 found
    the square penalised in reading tasks and 3:2 the sweet spot, so the target is ours to set."""
    if w <= 0 or h <= 0:
        return float("inf")
    r = (w / h) / target
    return max(r, 1 / r)


def _layout_row(row: list[float], x: float, y: float, dx: float, dy: float) -> list[dict]:
    """One row of cells laid along the rectangle's shorter side, in order (Bruls 2000's `layoutrow`)."""
    covered = sum(row)
    out = []
    if covered <= 0 or dx <= 0 or dy <= 0:
        return out
    if dx >= dy:                      # a wide rectangle: the row stands as a COLUMN down its left edge
        w = covered / dy
        yy = y
        for v in row:
            h = v / w
            out.append({"x": x, "y": yy, "w": w, "h": h}); yy += h
    else:                             # a tall rectangle: the row lies along its top edge
        h = covered / dx
        xx = x
        for v in row:
            w = v / h
            out.append({"x": xx, "y": y, "w": w, "h": h}); xx += w
    return out


def _row_cost(row: list[float], x: float, y: float, dx: float, dy: float, target: float) -> float:
    cells = _layout_row(row, x, y, dx, dy)
    return max((_cost(c["w"], c["h"], target) for c in cells), default=float("inf"))


def squarify(areas: list[float], x: float, y: float, dx: float, dy: float,
             target: float = TREEMAP_ASPECT) -> list[dict]:
    """The squarified treemap (Bruls, Huizing & van Wijk 2000) of `areas` - already scaled to fill
    dx*dy and sorted descending - inside the rectangle. Pure, deterministic, order-preserving: cell i
    is areas[i]. The only departure from the paper is the aspect the rows are tuned toward (3:2)."""
    cells: list[dict] = []
    rest = list(areas)
    row: list[float] = []
    while rest:
        v = rest[0]
        if not row or _row_cost(row + [v], x, y, dx, dy, target) <= _row_cost(row, x, y, dx, dy, target):
            row.append(v); rest.pop(0)
            continue
        cells.extend(_layout_row(row, x, y, dx, dy))
        covered = sum(row)
        if dx >= dy:
            w = covered / dy if dy else 0.0
            x += w; dx -= w
        else:
            h = covered / dx if dx else 0.0
            y += h; dy -= h
        row = []
    cells.extend(_layout_row(row, x, y, dx, dy))
    return cells


def _clamp_font(w: float, h: float, chars: int, lines: int) -> float:
    """The research's dynamic font clamp (findings s2.3), for `lines` lines of `chars` characters."""
    inner_w, inner_h = w - 2 * TREEMAP_PAD, h - 2 * TREEMAP_PAD
    lo, hi = TREEMAP_LABEL_FONT
    return max(0.0, min(hi, inner_w / max(1, chars) / TREEMAP_CHAR_W,
                        inner_h / TREEMAP_LINE_H.get(lines, 2.2 * lines / 2))) if inner_w > 0 and inner_h > 0 else 0.0


def label_tier(w: float, h: float, label: str, value_text: str) -> dict:
    """The three-tier label degradation (research s1 and s5's teardown of Bravos 89-91):
      2 - two lines, the label and its value, both at or above the legible floor;
      1 - ONE stacked line: the label alone;
      0 - none. The cell is a tile and the part is counted in the legend instead.
    The floors are the cell's own size in STAGE pixels; the font clamp is what refuses a long name in
    a cell that is wide enough for a short one."""
    lo = TREEMAP_LABEL_FONT[0]
    if w >= TREEMAP_TWO_LINE[0] and h >= TREEMAP_TWO_LINE[1]:
        chars = max(len(label), len(value_text))
        font = _clamp_font(w, h, chars, 2)
        value_font = max(TREEMAP_VALUE_FONT, round(font * 0.72))
        if font >= lo and value_font >= TREEMAP_VALUE_FONT and (font + value_font) * 1.15 <= h - 2 * TREEMAP_PAD:
            return {"tier": 2, "font": round(font, 1), "value_font": round(float(value_font), 1)}
    if w >= TREEMAP_MIN_CELL[0] and h >= TREEMAP_MIN_CELL[1]:
        font = _clamp_font(w, h, len(label), 1)
        if font >= lo:
            return {"tier": 1, "font": round(font, 1), "value_font": 0.0}
    return {"tier": 0, "font": 0.0, "value_font": 0.0}


def treemap_cells(spec: dict, aspect: str) -> dict:
    """The page's cells inside `page_boxes`'s PLOT for this aspect - never a research doc's container.

    Each cell carries its place as a FRACTION of the plot (so the player maps it into its own viewBox
    without re-deriving the layout - E58: a park is an affine transform, never a re-layout) and the
    stage pixels the label tier was decided on. Pure."""
    plot = page_boxes(spec, aspect)["plot"]
    values = [float(v or 0.0) for v in spec.get("values") or []]
    total = float(spec.get("total") or sum(values) or 1.0)
    area = max(1.0, plot["w"]) * max(1.0, plot["h"])
    order = sorted(range(len(values)), key=lambda i: (-values[i], i))   # squarify takes them largest first; `order` keeps the file's own index
    rects = squarify([values[i] / max(1e-12, sum(values)) * area for i in order],
                     0.0, 0.0, float(plot["w"]), float(plot["h"]))
    cells = []
    for k, i in enumerate(order):
        r = rects[k] if k < len(rects) else {"x": 0.0, "y": 0.0, "w": 0.0, "h": 0.0}
        label = str((spec.get("labels") or [None] * len(values))[i] or "")
        vs = str((spec.get("value_strings") or [None] * len(values))[i] or "")
        share = values[i] / total if total else 0.0
        tier = label_tier(r["w"], r["h"], label, vs)
        cells.append({"index": i, "label": label, "value": values[i], "value_string": vs,
                      "share": round(share, 6),
                      "fx": round(r["x"] / max(1e-9, plot["w"]), 6), "fy": round(r["y"] / max(1e-9, plot["h"]), 6),
                      "fw": round(r["w"] / max(1e-9, plot["w"]), 6), "fh": round(r["h"] / max(1e-9, plot["h"]), 6),
                      "w_px": round(r["w"], 1), "h_px": round(r["h"], 1), **tier})
    unnamed = sum(1 for c in cells if c["tier"] == 0)
    return {"plot": plot, "cells": cells, "unnamed": unnamed,
            # the parts the page could not name are COUNTED, never dropped: the census says how many there were
            "legend": f"and {unnamed} others" if unnamed else ""}


def _treemap_block(series: dict) -> dict:
    """The parts verbatim, in the file's own order; the layout is added per aspect by `build_spec`."""
    shares = _treemap_shares(series)
    total = to_number(series.get("total"))
    summed = sum(to_number(s.get("value")) or 0.0 for s in shares)
    return {"labels": [str(s.get("label")) for s in shares],
            "values": [to_number(s.get("value")) for s in shares],
            "value_strings": [value_string(s.get("value_string", s.get("value"))) for s in shares],
            # a part that names no colour takes NONE: the page's own ramp tiles the mosaic in layout
            # order, which is what gives a census its cell boundaries (a whole map in one token is a blob)
            "colors": [str(s["color"]) if s.get("color") else "" for s in shares],
            "total": total if total is not None else summed,
            **({"total_string": value_string(series["total"])} if series.get("total") is not None else {})}


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
        **({"tiers": True} if series.get("tiers") is True else {}),   # the macro-chart intake: bars and lines in two bands sharing one x, each on its own scale (a `tiers` LIST is the N-tier builder below, not this key)
        **({"build_s": float(to_number(series["build_s"]))} if to_number(series.get("build_s")) is not None and to_number(series["build_s"]) > 0 else {}),   # load_series decodes floats as their own tokens (parse_float=str): 1.2 arrives as "1.2", so the number is read, not the type   # the page draws over its own seconds
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
    if builder in ("tiers", "treemap"):
        spec.update(_tiers_block(series) if builder == "tiers" else _treemap_block(series))
        warnings = scale_warnings(series) if builder == "tiers" else []
        if warnings:   # only when there is one: an untroubled page's spec stays byte-identical
            spec["warnings"] = warnings
        spec["unit"] = str(series["unit"]) if _text(series.get("unit")) else ""
        spec["judge"] = review_notes(series)
        spec["badges"] = badges_for(series)
        count = len(spec["labels"])
        spec["emphasize"] = None if emphasize is None or not count else max(0, min(int(emphasize), count - 1))
        if builder == "treemap":
            # the layout is computed HERE, at build time, in page_boxes' own plot - both aspects, because the
            # page does not know which stage it will be read on and a treemap laid out at paint time is a
            # re-layout waiting to happen (E58 / Sondag 2018: a park is one affine transform)
            spec["layout"] = {aspect: treemap_cells(spec, aspect) for aspect in STAGE_PX}
        return spec
    if builder == PANELS:   # P69 T8b: 2-4 line plots on one page, one scale by default (E79)
        spec.update(_panels_block(series))
        warnings = panel_scale_warnings(series)
        if warnings:
            spec["warnings"] = warnings
        spec["unit"] = str(series["unit"]) if _text(series.get("unit")) else ""
        spec["judge"] = review_notes(series)
        spec["badges"] = badges_for(series)
        spec["emphasize"] = None
        parsed = parse_readability((spec.get("axes") or {}).get("readability"))
        if parsed and parsed[0] == LONGFORM:
            apply_longform(spec, parsed[1])
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
    parsed = parse_readability((spec.get("axes") or {}).get("readability"))
    if parsed and parsed[0] == LONGFORM:   # P69 T8: the series file's own `readability: longform[:<preset>]`
        apply_longform(spec, parsed[1])
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
FULL_STAGE_BANDS_KEY = "full_stage_bands"
PORTRAIT_LAYOUT = {"TOP": 150, "X": 80, "W": 800, "TITLE_W": 920, "BOTTOM": 1280, "GAP": 24, "CHART_MIN": 320}
PORTRAIT_INK = {"title": (68, 1.12, 0.52, 920), "sub": (40, 1.25, 0.44, 800), "src": (40, 1.25, 0.44, 800)}
PORTRAIT_PLOT = {"L": 150, "R": 70, "T": 90, "B": 80}
PORTRAIT_PILL_H, PORTRAIT_PILLS_PER_ROW = 132, 3   # the badge rail's row height and how many fit 800px
YLABEL_H = 52          # axes.ylabel floats top-left INSIDE the plot (template: lpYLabel at T-12)
XTICK_H = 62           # the x tick labels hang below the axis line (y = B + 52, 40px type)
LAND_BOARD = (0.06, 0.08, 0.88, 0.84)   # s9.26 default board; the punch crops to 1/PUNCH_SCALE
PUNCH_SCALE = 1.16
LAND_PLOT = {"L": 0.070, "R": 0.220, "T": 0.071, "B": 0.839}   # dense-line margins / the 1000x560 viewBox

# ---- THE PAGE IS THE PLATE AT 16:9 (R26-205 / E99 s82, 2026-09-18) ----------------------------
# The operator, on a bare frame of the H unit's copy d: *"why is the ledger being used at like 20%
# size? the whole point of a ledger plate is that the chart IS the world, you have it restricted to
# this square even when bare, it should be the whole plate."* Measured: the bare page's plot was
# `[180, 236, 403, 244]` of a 1920x1080 stage - 21 % of the stage's width - because the landscape
# chart box is `(0.6 if quiet_zone else 0.9) * cb.w`: a COLUMN was kept for the stage caption
# (`build_scene_timeline_f.caption_strip_x`) and for the card that lands in the quiet zone.
#
# At 16:9 a page that carries `full_stage` takes this box instead, and its caption goes to the
# anchored strip (`CAPTION_ANCHOR["16:9"]`), where it can never be in the plot's column. The numbers
# are in RENDERED stage fractions - the punch is already in them - because every one of them was
# read off a frame:
# THE BOX CARRIES THE viewBox's OWN ASPECT (1000:560), so the chart is drawn at the box's size with
# no letterbox and this estimate is exact. Its four numbers are the largest box whose THREE feet all
# land on the stage - each measured on the served player, not reasoned about:
#   (1) THE END TAGS. The dense-line species writes each series' name BESIDE its last point, inside
#       the chart's own units, so the tag grows with the chart. Measured on the `ledger-page-mid-build`
#       golden (the longest names and tags in the repo - "+613% MEMORY MAKERS (hynix+Micron) our
#       layer"): the widest ends `LAND_TAG_REACH` of the chart's own width from its left edge. The
#       first pass put the box on the whole stage and those tags ran 305 px off the right of the
#       frame (measured). So `X + LAND_TAG_REACH * W <= 0.979` - the stage less a hair - which is what
#       caps W at 1334 px. X is not free either: at X = 0.010 the y tick column landed 36 px outside
#       the 16:9 SAFE_BOX, and every pixel X gains costs `LAND_TAG_REACH` of W.
#   (2) THE X TICK LABELS clear the anchored caption. Their foot is `LAND_TICK_B` of the box's own
#       height, so 197 + 0.911 * 747 = 878 - level with `CAPTION_ANCHOR["16:9"]`'s top, and 39 px
#       clear of the caption's own one-line box, which sits at the strip's FOOT (measured: y 919-960).
#   (3) THE SOURCE LINE clears the strip's foot. Written `LAND_SRC_GAP` under the box, it runs
#       959-1000, under the strip's 960 - which is where the landscape source line sits today.
# (2) and (3) pull against each other (a taller box drops the ticks into the strip, a shorter one
# lifts the source into it): together they hold the box's height inside 4 px, and Y is the value that
# satisfies both. Nothing here is free to be rounded.
#
# MEASURED on the `ledger-page-mid-build` golden at 16:9, t = 20 s (the served player, the probe
# `measure_page_boxes.READ_BOXES`): the plot goes 784 -> 966 px, 40.8 % -> 50.3 % of the stage width;
# the widest end tag ends at 1896 of 1920; the y tick column starts at x 67, inside the safe box; the
# x ticks' foot is 880 against the caption's box at 919; the source line runs 967-1008, under it.
#
# WHAT THIS DOES NOT REACH, and the arithmetic, because the row asked for 70 % of the stage: the plot
# is `(1 - L - R) = 0.710` of the chart, so 1344 px of plot needs a chart 1893 px wide and - at this
# aspect - 1060 px tall, which is the whole stage. Two things stand in the way and neither is this
# row's: the inline END TAG would need portrait's treatment (right-anchored above the line's end,
# `buildLedgerLine`'s `P` branch) instead of its own column, and the chart's viewBox would have to
# follow the box's aspect rather than letterbox inside it, which is seven landscape builders' own
# absolute margins. R26-205-NOTE.md carries the table.
LAND_FULL = {"X": 0.0300, "Y": 0.1824, "W": 0.6948, "H": 0.6917}
LAND_TAG_REACH = 1.365   # how far past the chart's own left edge the widest end tag reaches, in chart widths [MEASURED: ledger-page-mid-build at 16:9, the tag at x 1006-1638 with the chart drawn 1105 wide from x 131]
# THE END TAG COLUMN, per page. `LAND_TAG_REACH` is the RENDERED worst case and sizes the BOX; this
# sizes the page's OWN column, so a card is refused the room this page's names actually take and no
# other.
#
# TWO ADVANCES, because the element is TWO type sizes: the series' NAME in the big bold, then the
# badge's tag in its own smaller type (E22's dynamic label - one reveal, one real estate). One advance
# cannot bound both: fitted on a short mixed-case name alone it is 14.8 units a glyph, on an all-caps
# name 18.8, and on a name diluted by a long badge tag 13.0 - so a single number either puts a card on
# a name or keeps it off half the stage. These two are an UPPER BOUND on every tag measured, which is
# the side to be wrong on [MEASURED at 16:9 on the dense-line golden's own four tags and on a short-name
# page: (34 name, 9 tag) 561 units, (26, 16) 554, (25, 18) 560, (25, 10) 411, (12, 0) 178; this model
# gives 691, 574, 565, 525, 228]. The column starts `LAND_TAG_GAP` past the last datum
# (`buildLedgerLine` writes the name at `mx(last) + 12`). Only the builders that write an inline end
# name have a column at all.
LAND_TAG_NAME_U, LAND_TAG_BADGE_U, LAND_TAG_GAP = 19.0, 5.0, 12
LAND_TAG_BUILDERS = ("dense-line", "combo")
BADGE_ACCENT_COL = {"coral": "crimson", "teal": "teal", "cobalt": "cobalt", "ink": "deemph", "sunflower": "amber"}
"""A badge's accent -> the SERIES COLOUR it keys: the mirror of the engine's `LP_BADGE_COL`, one law in
two languages. An inline badge rides that series' end name inside the same element (the dynamic label,
E22: one reveal, one real estate), so the compiler cannot size the tag column without it."""


def tag_units(spec: dict) -> float:
    """The widest inline end name this page will write, in the chart's own 1000 units.

    Per series: `<label> <name>` as `buildLedgerLine` composes it, at `LAND_TAG_NAME_U` a glyph, plus
    the tag of the INLINE BADGE that keys it (matched by `BADGE_ACCENT_COL`, as the player matches it)
    at `LAND_TAG_BADGE_U`. 0 when this page's builder writes no inline name, or when every series is
    muted history (which carries none)."""
    if str(spec.get("builder")) not in LAND_TAG_BUILDERS:
        return 0.0
    rides = {BADGE_ACCENT_COL.get(str(b.get("accent"))): str(b.get("tag") or "")
             for b in spec.get("badges") or [] if b.get("inline")}
    out = 0.0
    for s in spec.get("series") or []:
        if s.get("muted"):
            continue
        tag = rides.get(str(s.get("color")), "")
        name = ((s.get("label") or "") + " " + (s.get("name") or "")).strip()
        out = max(out, len(name) * LAND_TAG_NAME_U + (len(tag) + 1) * LAND_TAG_BADGE_U if tag
                  else len(name) * LAND_TAG_NAME_U)
    return out
# the x tick labels' FOOT as a fraction of the chart's viewBox height: the line builder writes them
# at `B + 52` of its 560 units and they are 40 px type, so 510/560 - read off the dense-line entry
# (plot bottom 806 with the chart drawn from y 258.5 at scale 1.083: (806 - 258.5) / 1.083 = 506).
LAND_TICK_B = 0.911
# the RENDERED heights of the landscape page's ink, off the dense-line entry's measured boxes (the
# type is the template's and does not move with the chart box): a one-line title, sub and source,
# and one badge row. `_landscape_boxes` models the CSS box and leaves the punch to the player; the
# full-stage branch reports what the FRAME holds, so these are the punched numbers.
LAND_FULL_INK = {"title": 63, "sub": 30, "src": 41, "pill": 56}
LAND_SRC_GAP, LAND_RAIL_GAP = 0.012, 0.044   # the source / rail tops under the chart box (the engine's own 1.2 % / 4.4 %)


def _punch_pt(f: float) -> float:
    """A point's RENDERED stage fraction from its CSS one.

    The punch (E22 addendum 6) scales the page by `PUNCH_SCALE` about the BOARD's centre, which for
    the s9.26 default board is the stage's own centre - so a page that declares its own `board` or
    `chart_box` (a host plate) is never a full-stage page and never comes through here."""
    return 0.5 + (f - 0.5) * PUNCH_SCALE


def full_stage(spec: dict, aspect: str) -> bool:
    """Does this page's chart fill the STAGE (R26-205)? 16:9 only, and never a HOST PLATE.

    The compiler stamps `full_stage` on a 16:9 ledger page row; a page that declares its own
    `board`, `chart_box` or `punch: False` is a host plate whose board was measured around a hand
    (`proofs/ledger/derive_host_boards.py`), so its chart box is the host's and not the stage's."""
    return bool(spec.get("full_stage")) and aspect == "16:9" and not (
        spec.get("board") or spec.get("chart_box") or spec.get("punch") is False)


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


def _full_stage_bands(w_s: int, h_s: int) -> dict:
    """R26-230's explicit 16:9 bands, derived from the page and caption constants.

    The evidence rectangle is the vertical area in which the page's PLOT ink may live. The chart
    box itself can extend below it for SVG letterbox air; the boundary protects the ink, not an
    empty chart canvas. The top and bottom bands are full-stage strips so a long-form page can be
    re-staged as a 9:16 layout instead of cropped into one.
    """
    safe_x, _safe_y, safe_w, _safe_h = SAFE_BOX["16:9"]
    caption_top = CAPTION_ANCHOR["16:9"][1]
    evidence_top = LAND_FULL["Y"] * h_s
    return {
        "top": _box(0, 0, w_s, evidence_top),
        "bottom": _box(0, caption_top, w_s, h_s - caption_top),
        "evidence_safe": _box(safe_x, evidence_top, safe_w, caption_top - evidence_top),
    }


TIER_GAP = 0.20   # the gutter between two bands, as a share of a band's own height [DERIVED, read off the first frame: at 0.10 a band's NAME sat on the floor tick label of the band above it; 0.20 is one line of type between them and still leaves four bands ~230 px each on a 9:16 plot]


def tier_bands(plot: dict, n: int) -> list[dict]:
    """The N band boxes inside a tiers page's plot, top to bottom, in stage pixels.

    The MIRROR of `tierBands` in scripts/species/tiers.mjs - one law in two languages, the same two
    dials, pinned on both sides (test_ledger_page and tests/kinetics/tiers.test.mjs). The compiler
    needs it to park a dock clear of a band; the player needs it to draw one."""
    if n < 1:
        return []
    h = plot["h"] / (n + (n - 1) * TIER_GAP)
    return [_box(plot["x"], plot["y"] + i * h * (1 + TIER_GAP), plot["w"], h) for i in range(n)]


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


def _landscape_full_boxes(spec: dict, w_s: int, h_s: int) -> dict:
    """R26-205: the 16:9 page whose CHART IS THE WORLD - its boxes in RENDERED stage pixels.

    `_landscape_boxes` models the page's CSS box and leaves the punch to the player, which is why its
    estimate of a chart box is `PUNCH_SCALE` short of the frame's. Every number here is where the
    FRAME puts it: the chart box is declared in rendered fractions (`LAND_FULL`) and the page's ink
    is carried through `_punch_pt`, so these boxes can be read straight against a probe.

    The plot is a fraction of the DRAWN chart, not of the box. Legacy pages use the 1000x560 SVG
    under the default preserveAspectRatio and retain its measured letterbox law. T17's opt-in
    changes both the chart width and the SVG viewBox width, so the matched profile has no spare
    horizontal air and the actual plot grows."""
    if _readability_profile(spec) == LONGFORM:   # P69 T8: the long form lays its own page out (the engine measures it)
        return _longform_full_boxes(spec, w_s, h_s)
    bx, by, bw, bh = LAND_BOARD
    half = 0.5 / PUNCH_SCALE
    vx, vy = bx + bw / 2 - half, by + bh / 2 - half
    F, L, I = LAND_FULL, LAND_PLOT, LAND_FULL_INK
    profile = _landscape_profile_geometry(spec, w_s, h_s)
    cx, cy = F["X"] * w_s, F["Y"] * h_s
    if profile:
        cw, ch = profile["w"], profile["h"]
        vw, vh, s = profile["vw"], profile["vh"], profile["scale"]
        ox, oy = cx, cy
    else:
        cw, ch = F["W"] * w_s, F["H"] * h_s
        vw, vh = LAND_VIEWBOX
        s = min(cw / vw, ch / vh)
        ox, oy = cx + (cw - vw * s) / 2, cy + (ch - vh * s) / 2
    # the title and the sub keep the places they have always had at 16:9 - the same two CSS
    # expressions the engine writes - read through the punch. The ink's own column is the title's,
    # as the 9:16 page's one column is (`PORTRAIT_LAYOUT["X"]`): nothing is aligned to the chart's
    # letterbox, which moves with the data's shape.
    ink_x = _punch_pt(max(bx + 0.027, vx + 0.03)) * w_s
    title_y = _punch_pt(max(by + 0.024, vy + 0.035)) * h_s
    sub_y = _punch_pt(max(by + 0.024, vy + 0.035) + 0.056) * h_s
    ink_w = cx + cw - ink_x
    src_y = cy + ch + LAND_SRC_GAP * PUNCH_SCALE * h_s
    rail = [b for b in spec.get("badges") or [] if not b.get("inline")]
    # The phone profile increases the SVG label face, so mirror the renderer's local face
    # height and its slightly lifted baseline here.  Legacy pages keep the measured values.
    ylab = (LAND_PHONE_FONT_PX * s if profile else YLABEL_H) if (spec.get("axes") or {}).get("ylabel") else 0
    tick_b = LAND_PHONE_TICK_B if profile else LAND_TICK_B
    tag_b = profile["B"] if profile else L["B"]
    title_h = I["title"] * LAND_PHONE_TEXT_PX / 34 if profile else I["title"]
    sub_h = I["sub"] * LAND_PHONE_TEXT_PX / 21 if profile else I["sub"]
    src_h = I["src"] * LAND_PHONE_TEXT_PX / 22 if profile else I["src"]
    # The native dense-line margins are SVG units, not fractions of the variable
    # phone viewBox. Multiplying legacy fractions by vw misplaces both plot/tags.
    plot_left = LAND_PHONE_PLOT_L if profile else L["L"] * vw
    if spec.get("builder") == "story" and "left_gutter" in (spec.get("axes") or {}):
        plot_left = max(plot_left, float(spec["axes"]["left_gutter"]))
    plot_right = LAND_PLOT["R"] * LAND_VIEWBOX[0] if profile else L["R"] * vw
    return {
        "title": _box(ink_x, title_y, ink_w, title_h),
        "sub": _box(ink_x, sub_y, ink_w, sub_h),
        "chart": _box(cx, cy, cw, ch),
        "plot": _box(ox + plot_left * s, oy + L["T"] * vh * s - ylab,
                     (vw - plot_left - plot_right) * s, (tick_b - L["T"]) * vh * s + ylab),
        "source": _box(ink_x, src_y, ink_w, src_h),
        "rail": _box(ink_x, cy + ch + LAND_RAIL_GAP * PUNCH_SCALE * h_s, ink_w,
                     I["pill"] * -(-len(rail) // PORTRAIT_PILLS_PER_ROW) if rail else 0),
        # the END TAG COLUMN: the page's own inline names, beside the plot and part of the chart's ink.
        # It was air while a quiet zone kept the chart to 60 % of its board; at full stage it is the
        # only thing between the plot and the frame, so `free_bands` has to know it is there.
        "tags": _box(ox + (vw - plot_right + LAND_TAG_GAP) * s, oy + L["T"] * vh * s,
                     (profile["tag_units"] if profile else tag_units(spec)) * s,
                     (tag_b - L["T"]) * vh * s),
    }


LAND_VIEWBOX = (1000, 560)   # the landscape chart's viewBox; a portrait chart's viewBox IS its pixel box (the template: "builders draw in stage px")

# T17: this is deliberately a geometry profile, not a global type dial. The chart keeps the
# existing 560-unit vertical viewBox and fixed line-builder margins; only its horizontal user
# extent follows the page's safe rendered width. `sname` and its inline `tagchip` are 46px in the
# opt-in renderer (44px was the starting point; the browser floor required a two-pixel margin),
# so both advances are scaled from the existing 24px/18px bounds.
LAND_PHONE_VIEWBOX_H = LAND_VIEWBOX[1]
LAND_PHONE_NAME_U = LAND_TAG_NAME_U * 46.0 / 24.0
LAND_PHONE_BADGE_U = LAND_TAG_BADGE_U * 46.0 / 18.0
LAND_PHONE_MIN_VIEWBOX_W = LAND_VIEWBOX[0]
LAND_PHONE_SAFE_RIGHT = 0.979
LAND_PHONE_FONT_PX = 46
LAND_PHONE_PLOT_L = 120
LAND_PHONE_TEXT_PX = 52
LAND_PHONE_B = 458
LAND_PHONE_TICK_B = (LAND_PHONE_B + 32) / LAND_PHONE_VIEWBOX_H
# P69 T8 - THE LONG FORM'S TYPE SCALE (the parent's frame read, 2026-09-23: the look is right, the SCALE is the
# operator's call). E99 s90 (B's roughly 12.5 px phone type) and E99 s97 (Bravos's measured 15-18 px ticks) pull
# the page's type opposite ways, so the profile carries THREE named presets and the row picks one -
# `;readability=longform:bravos|middle|phone` (plain `longform` is `middle`) - for P69-HG3 to rule on. Every size is
# a FONT SIZE in px as RENDERED on the 1920 x 1080 stage (the page ink through the punch, the chart's through its
# own rest scale); the engine's `LP_LONGFORM.TYPE_SCALE` is the same table.
#   bravos  [DERIVED: BRAVOS-LONGFORM-CHART-SPEC.md (a)/(b), a cap or digit height / Inter's 0.727 cap ratio] - the
#           title cap 28 (t530) -> 38.5; the tick digit 16.5 (t170 15 / t530 18) -> 22.7; the line badge's 14 px
#           digits (t170) -> 19.3 for an end tag, its chip at 0.8 of it; the value beside a bar, 31.5 (t1088) ->
#           43.3; the source cap 10.5 (t170/t530) -> 14.4; the sub, unmeasured on a chart page, sits at 24.
#   middle  the working default (the parent, 2026-09-23): title 44, sub 26, ticks 26, end tags 30, source 20.
#   phone   E99 s90's floor, T17's own render: the page ink 52 CSS px x the 1.16 punch = 60.3, the chart's 46 units
#           x its 1.334 rest scale = 61.4 (~12.5 px on a 390 px phone).
LONGFORM_PRESETS = ("bravos", "middle", "phone")
LONGFORM_DEFAULT_PRESET = "middle"
LONGFORM_TYPE_SCALE = {
    "bravos": {"title": 38.5, "sub": 24.0, "tick": 22.7, "tag": 19.3, "chip": 15.4, "value": 43.3, "src": 14.4},
    "middle": {"title": 44.0, "sub": 26.0, "tick": 26.0, "tag": 30.0, "chip": 24.0, "value": 34.0, "src": 20.0},
    "phone": {"title": 60.3, "sub": 60.3, "tick": 61.4, "tag": 61.4, "chip": 61.4, "value": 61.4, "src": 60.3},
}
# The layout the engine MEASURES and this module ESTIMATES (the fixture outranks the estimate, as `PORTRAIT_INK`'s):
# the title, sub and source wrap in one ink column (to the stage's safe right edge) at a 1.1 leading, the sub
# LONGFORM_SUB_GAP CSS px under the title's last line. The chart box then takes the room that is left: its plot
# top stands M28's half-figure of air (half the tick size) plus the ink it carries above the plot (the y label,
# LONGFORM_YLAB_GAP_PX over the plot; a rule's name; half the top tick) under the sub - the chart moves DOWN,
# never onto the sub - and its foot rises only when the wrapped source would leave the stage (LONGFORM_EDGE_PX).
# Advances are Inter's in ems per character (Bold title and end tag, Regular sub and source, the 600 chip).
LONGFORM_LINE_H = 1.1
LONGFORM_SUB_GAP = 8
LONGFORM_TAG_EM = {"name": 0.68, "chip": 0.64}
LONGFORM_CHIP_DX_PX = 12
LONGFORM_YLAB_GAP_PX = 14
LONGFORM_EDGE_PX = 16
LONGFORM_PLOT_T = {"dense-line": 40.0, "story": 90.0, PANELS: 0.0}   # each builder's own plot top, in chart units (P69 T8b: a panels page's region IS its top - each panel carries its own plot top inside its box)
# REVIEW-P69-LANE-B-MERGE-2 N3 - THE PAGE INK'S ADVANCES, READ OFF THE FACE ITSELF. The first estimate wrapped the
# title, sub and source at a flat 0.56 / 0.5 em a character, and a one-line miscount moved every box under it (the
# long page at `phone`: the chart 73 px below the engine's). The page writes each glyph as its own inline-block
# (`lpGlyphsWrap`: no kerning, no shaping across glyphs) and each word as an unbreakable run, so a line's width IS the
# sum of the glyphs' advances - exactly computable from Inter's `hmtx`. The face is VARIABLE on two axes (wght 100-900,
# opsz 14-32) and the browser sets opsz to the CSS font size (font-optical-sizing: auto), so the advances are stored
# at the weight each role is set in (the title 700; the sub and the source 400) at opsz 14 and 32, in font units of
# 2048 per em, and interpolated linearly in opsz between them [MEASURED 2026-09-23 on the tracked
# `src/assets/fonts/Inter-Variable.ttf` with fontTools' instancer; the linear interpolation is within 0.5 units of
# the instanced advance at opsz 20.69 for every character - `test_longform_profile` regenerates the table].
# A character outside the table takes its weight's mean advance.
LONGFORM_ADV_CHARS = (" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
                      "‘’“”–—·•…é€£¥×→°½")
LONGFORM_ADV_UPM = 2048
LONGFORM_OPSZ = (14.0, 32.0)
LONGFORM_WEIGHT = {"title": 700, "sub": 400, "source": 400, "key": 500}   # P69 T10: the key pill's name is Inter Medium (the spec's pill)
LONGFORM_ADVANCES = {   # (weight, opsz) -> the advance of each LONGFORM_ADV_CHARS character, in font units
    (400, 14): tuple(int(v) for v in (
        "576 589 954 1297 1314 2011 1319 614 747 747 1026 1355 590 942 590 738 1292 833 1249 1265 1323 1215 1270 1159 1267 1270 590 618 1355 1355 1355 1047 "
        "1978 1413 1340 1496 1478 1231 1209 1528 1522 550 1169 1376 1158 1850 1543 1566 1308 1566 1318 1314 1322 1524 1413 2018 1397 1390 1288 747 738 747 965 934 "
        "661 1150 1254 1170 1254 1194 758 1256 1211 496 496 1124 496 1794 1210 1228 1254 1254 771 1081 670 1211 1151 1676 1118 1151 1131 873 681 873 1355 534 "
        "534 902 902 1024 2048 590 1152 1770 1194 1365 1251 1126 1355 1954 933 1735").split()),
    (400, 32): tuple(int(v) for v in (
        "512 450 826 1228 1258 1728 1246 520 612 612 960 1286 450 878 450 666 1256 742 1149 1226 1265 1181 1196 1056 1192 1196 450 456 1286 1286 1286 1073 "
        "1994 1338 1307 1479 1412 1187 1135 1496 1450 476 1095 1299 1096 1756 1454 1534 1253 1534 1295 1258 1250 1440 1338 1944 1322 1316 1256 612 666 612 896 930 "
        "494 1060 1158 1071 1158 1098 627 1158 1120 422 422 1039 422 1718 1120 1124 1158 1158 660 972 637 1120 1048 1540 1038 1048 980 788 606 788 1286 390 "
        "390 694 696 1024 2048 450 1024 1350 1098 1298 1192 1058 1286 1890 866 1548").split()),
    (700, 14): tuple(int(v) for v in (
        "485 692 1129 1329 1341 2080 1376 694 772 772 1145 1390 684 958 684 795 1381 883 1289 1322 1385 1274 1330 1191 1333 1330 684 702 1390 1390 1390 1146 "
        "2081 1529 1355 1515 1479 1244 1202 1537 1530 575 1197 1473 1158 1908 1561 1578 1327 1591 1345 1341 1367 1499 1529 2125 1512 1497 1360 772 795 772 997 975 "
        "748 1189 1291 1205 1291 1220 815 1294 1275 555 555 1188 555 1869 1275 1256 1291 1291 834 1147 750 1275 1228 1741 1188 1233 1173 960 761 960 1390 636 "
        "636 1106 1089 1024 2048 684 971 2052 1220 1402 1308 1168 1390 1954 941 1805").split()),
    (500, 14): tuple(int(v) for v in (   # P69 T10: the key pill's Medium, read the same way
        "546 623 1012 1308 1323 2034 1338 641 755 755 1066 1367 621 947 621 757 1322 850 1262 1284 1344 1235 1290 1170 1289 1290 621 646 1367 1367 1367 1080 "
        "2012 1452 1345 1502 1478 1235 1207 1531 1525 558 1178 1408 1158 1869 1549 1570 1314 1574 1327 1323 1337 1516 1452 2054 1435 1426 1312 755 757 755 976 948 "
        "690 1163 1266 1182 1266 1203 777 1269 1232 516 516 1145 516 1819 1232 1237 1266 1266 792 1103 697 1232 1177 1698 1141 1178 1145 902 708 902 1367 568 "
        "568 970 964 1024 2048 621 1092 1864 1203 1377 1270 1140 1367 1954 936 1758").split()),
    (500, 32): tuple(int(v) for v in (
        "488 468 873 1245 1284 1792 1272 532 634 634 1006 1304 467 889 467 692 1281 761 1175 1240 1292 1197 1219 1079 1214 1219 467 472 1304 1304 1304 1103 "
        "2017 1379 1311 1482 1420 1206 1154 1500 1457 494 1114 1334 1111 1781 1464 1533 1266 1533 1307 1284 1267 1441 1374 1976 1357 1348 1270 634 692 634 913 944 "
        "531 1084 1180 1093 1180 1115 671 1180 1146 449 449 1068 449 1749 1146 1146 1180 1180 695 1003 676 1146 1077 1585 1059 1077 1010 825 641 825 1304 415 "
        "415 758 754 1024 2048 467 975 1401 1115 1317 1211 1079 1304 1896 875 1592").split()),
    (700, 32): tuple(int(v) for v in (
        "439 505 967 1280 1336 1920 1325 556 679 679 1097 1341 501 911 501 745 1332 798 1226 1269 1345 1229 1264 1126 1258 1264 501 505 1341 1341 1341 1162 "
        "2062 1461 1320 1487 1436 1245 1191 1507 1471 530 1151 1404 1140 1831 1485 1531 1293 1531 1332 1336 1301 1442 1445 2041 1428 1413 1299 679 745 679 948 973 "
        "604 1132 1224 1137 1224 1150 759 1224 1199 503 504 1127 503 1810 1199 1189 1224 1224 764 1065 755 1199 1134 1676 1100 1134 1071 900 710 900 1341 464 "
        "464 887 871 1024 2048 501 877 1502 1150 1354 1250 1120 1341 1907 893 1680").split()),
}
# N1 - WHAT STANDS UNDER THE CHART, and where. The anchored caption's STRIP runs from `full_stage_bands`' bottom band's
# top to the one-line caption's own foot (CAPTION_ANCHOR: 878-960 at 1920 x 1080). The source line and the key rail
# NEVER stand in it: each writes under the chart (the source LAND_SRC_GAP under it, the rail LAND_RAIL_GAP under it or
# LONGFORM_STACK_GAP_PX under the source's last line), and one that would meet the strip moves under its foot; when
# that leaves the stage (LONGFORM_EDGE_PX), the chart's foot rises until the source - then the rail - stands above
# the strip instead. The rail's pills are the template's own (a 41 CSS px row at 16:9 - 47.56 px rendered - 6 CSS px
# apart) [MEASURED: the `rail` fixture's one pill, 2026-09-23].
LONGFORM_STRIP = (CAPTION_ANCHOR["16:9"][1], CAPTION_ANCHOR["16:9"][1] + CAPTION_ANCHOR["16:9"][3])
LONGFORM_STACK_GAP_PX = 8
LONGFORM_PILL_PX = 41 * PUNCH_SCALE
LONGFORM_PILL_GAP_PX = 6 * PUNCH_SCALE
LONGFORM_PILLS_PER_ROW = 4
# the face's own line box: a chart label's box reaches its ascent above its baseline and its descent below it
# [MEASURED: Inter-Variable.ttf hhea 1984 / -494 of 2048 units per em]
LONGFORM_ASCENT, LONGFORM_DESCENT = 1984 / 2048, 494 / 2048
# An END TAG that will not fit the stage at its preset gives up its long name for its badge (the value and the short
# chip), then for its value alone - never a refusal (the parent, 2026-09-23). The long names belong in a key: that is
# P69 T10's badge key (below); the spec keeps every name for it.
LONGFORM_TAG_FORMS = ("full", "badge", "value")
# P69 T9 (3) (E99 s90: "x-tick labels must clear the axis line (main measured 18 px, T17 measured 0 px)"): a longform
# page's x labels - a line page's ticks, a bars page's names - stand with their box's top this far under the panel's
# foot line (its border, LONGFORM_BORDER_PX, the engine's LP_LONGFORM.BORDER_PX) [DERIVED: main's measured 18 px and
# two for the rendered box's rounding; T8's page measured 7].
LONGFORM_XLAB_CLEAR_PX = 20.0
LONGFORM_BORDER_PX = 1.5
# P69 T10 (E99 s90 "apply badges as the key"; E99 s84 "prefer to land on even pills (2 or 4)") - THE KEY RAIL. A line
# page whose end tags gave up their long names (`tag_form` badge or value) writes those names on a KEY: one pill per
# series, the Bravos category pill (BRAVOS-LONGFORM-CHART-SPEC.md (b) `category_pill`, t1088: a white capsule 40 px
# tall, r = h/2, a 15 px cap in #1E1F22 Inter 500, a 10 px dot on its left end) with the dot in the SERIES' own line
# colour, scaled to the preset. It stands in the page's TOP BAND - Bravos's own legend band (t170 / t1078), between the
# sub and the plot - hugging the chart's top ink with M28's half-figure of air, and when that band is too short the
# chart moves down to make it (the right margin is the end tags', and the stack under the chart is N1's source and
# rail over the caption strip). The key is ONE ROW, as Bravos's legend band is: set at the preset's size when its pills
# fit one row of the ink column, else at the largest size that does (the compiler fits it, as it fits the end tags:
# `axes.key_px`) - never under the spec's own pill (LONGFORM_KEY_MIN_PX), where a longer key wraps, greedily, as the
# browser's flex row does. At `phone` a key of long names therefore sets under s90's floor (the stage has no room for
# four of them at 61 px and a readable plot: the P69-HG3 card says so).
#   LONGFORM_KEY_PX  the pill's type, a FONT SIZE in rendered px [DERIVED: bravos, the spec's 15 px cap / Inter's 0.727
#                    cap ratio; middle, the preset's own chip (24); phone, E99 s90's floor at the preset's own 61.4].
#   LONGFORM_KEY_EM  the pill's box in ems of that size: h and the dot from the spec (40 / 20.6, 10 / 20.6), the pads
#                    and gaps [DERIVED: t1088's pill read at x5 - the dot a half-dot in from the left end, the name a
#                    dot's width after it].
# Every pill springs on recipe:badge-ladder's own clock (FIRST_BADGE_S 2.05 s after the chart has built, then
# BADGE_GAP_S 1.30 apart - the engine's LP_LONGFORM.KEY_FIRST / KEY_STEP). The key lands on an EVEN pill count where
# the series allow: an odd key takes one more of the page's lines, one whose end tag kept its own name - never an
# invented pill, so three shortened lines and nothing else to key stay three.
LONGFORM_KEY_PX = {"bravos": 20.6, "middle": 24.0, "phone": 61.4}
LONGFORM_KEY_EM = {"h": 40 / 20.6, "dot": 10 / 20.6, "pad_l": 0.55, "dot_gap": 0.4, "pad_r": 0.7, "gap": 0.5,
                   "row_gap": 0.35}
LONGFORM_KEY_MIN_PX = LONGFORM_KEY_PX["bravos"]   # the spec's measured pill: the key never sets smaller
LONGFORM_KEY_FIT_PX = 2.0   # the one-row fit's margin inside the column [DERIVED: the browser's sub-pixel layout]
LONGFORM_KEY_CLOCK = (2.05, 1.30)   # recipe:badge-ladder: FIRST_BADGE_S, BADGE_GAP_S
KEY_BOX = "key"   # page_boxes' key for the key rail's box (a longform page with a key only)


def longform_key(spec: dict) -> list[dict]:
    """The key rail's pills for a longform dense-line page: ``[{"series": i, "name": full name}]`` in the series' own
    order - every live series whose end tag gave up its name (`tag_form` badge or value, a label AND a name), then, if
    that is an odd count, the first other live series that names itself (the even pill count, E99 s84). ``[]`` when the
    tags keep their names."""
    axes = spec.get("axes") or {}
    if spec.get("builder") != "dense-line" or axes.get("tag_form") in (None, "full"):
        return []
    live = [(i, s) for i, s in enumerate(spec.get("series") or []) if isinstance(s, dict) and not s.get("muted")]

    def text(s: dict) -> str:
        return str(s.get("name") or s.get("label") or "").strip()

    keyed = {i for i, s in live if str(s.get("label") or "").strip() and str(s.get("name") or "").strip()}
    if len(keyed) % 2:
        extra = next((i for i, s in live if i not in keyed and text(s)), None)
        if extra is not None:
            keyed.add(extra)
    return [{"series": i, "name": text(s)} for i, s in live if i in keyed]


def longform_key_pill_w(name: str, px: float) -> float:
    """One key pill's width in rendered px at the key's size `px`: its pads, its dot and its name's Medium advances (the
    engine sets the pill with no kerning or ligatures, so the name's width IS the sum of its advances)."""
    em = LONGFORM_KEY_EM
    return longform_text_px(name, "key", px) + (em["pad_l"] + em["dot"] + em["dot_gap"] + em["pad_r"]) * px


def _longform_key_row(key: list, px: float) -> float:
    """The key's pills in one row at `px`, rendered px wide."""
    return sum(longform_key_pill_w(k["name"], px) for k in key) + LONGFORM_KEY_EM["gap"] * px * (len(key) - 1)


def longform_key_px(spec: dict, w_s: int = 1920) -> float:
    """The size the key is set in: the preset's own when its pills fit one row of the ink column, else the largest
    size (to the tenth of a px) at which they do, never under LONGFORM_KEY_MIN_PX."""
    key = (spec.get("axes") or {}).get("key") or []
    px0, room = LONGFORM_KEY_PX[longform_preset(spec)], _longform_ink_col(w_s)[1] - LONGFORM_KEY_FIT_PX
    if not key or _longform_key_row(key, px0) <= room:
        return px0
    lo, hi = min(LONGFORM_KEY_MIN_PX, px0), px0
    if _longform_key_row(key, lo) > room:
        return lo
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _longform_key_row(key, mid) <= room else (lo, mid)
    return math.floor(lo * 10) / 10


def longform_key_box(spec: dict, col_w: float) -> tuple[float, float]:
    """The key rail's (w, h) in rendered px in an ink column `col_w` wide: the pills wrapped greedily into rows (the
    browser's flex-wrap), the box as wide as its one row or the column. (0, 0) when the page has no key.
    REVIEW-P69-LANE-B-MERGE-3 M1: a page whose `then=` states key more than it does carries the band they need
    (`axes.key_w` / `key_h`, apply_longform_states) - its key box is the larger of the two."""
    axes = spec.get("axes") or {}
    w, h = _longform_key_own(spec, col_w)
    return max(w, float(axes.get("key_w") or 0.0)), max(h, float(axes.get("key_h") or 0.0))


def _longform_key_own(spec: dict, col_w: float) -> tuple[float, float]:
    """The (w, h) of this spec's OWN key, wrapped in the column; (0, 0) when it has none."""
    axes = spec.get("axes") or {}
    key = axes.get("key") or []
    if not key:
        return 0.0, 0.0
    px, em = float(axes.get("key_px") or LONGFORM_KEY_PX[longform_preset(spec)]), LONGFORM_KEY_EM
    gap = em["gap"] * px
    rows, run = 1, 0.0
    for k in key:
        w = longform_key_pill_w(k["name"], px)
        if run and run + gap + w > col_w + 0.5:
            rows, run = rows + 1, w
        else:
            run = run + gap + w if run else w
    one_row = sum(longform_key_pill_w(k["name"], px) for k in key) + gap * (len(key) - 1)
    return min(one_row, col_w), rows * em["h"] * px + (rows - 1) * em["row_gap"] * px


def parse_readability(value: Any) -> tuple[str, str | None] | None:
    """``landscape-phone`` | ``longform`` | ``longform:<preset>`` -> (profile, preset), or None when not one."""
    if not isinstance(value, str):
        return None
    profile, colon, preset = value.partition(":")
    if profile == LANDSCAPE_PHONE and not colon:
        return profile, None
    if profile == LONGFORM and (not colon or preset in LONGFORM_PRESETS):
        return profile, preset or LONGFORM_DEFAULT_PRESET
    return None


def longform_preset(spec: dict) -> str:
    """The preset a longform page is set in."""
    preset = (spec.get("axes") or {}).get("type_scale")
    return preset if preset in LONGFORM_TYPE_SCALE else LONGFORM_DEFAULT_PRESET


def longform_type(spec: dict) -> dict:
    """The preset's sizes (rendered px) a longform page is set in."""
    return LONGFORM_TYPE_SCALE[longform_preset(spec)]


def longform_geom(t: dict, top: float, bot: float, floor: float | None = None) -> dict:
    """The chart-unit geometry a longform chart is drawn in, for a chart box from `top` to `bot` (rendered px): the
    engine's `lpLongformGeom`, line for line. The x ticks and the bar names hang under the plot with their box's top
    LONGFORM_XLAB_CLEAR_PX clear of the panel's foot line (P69 T9 (3), E99 s90: "x-tick labels must clear the axis
    line" - main measured 18 px, T17 0, T8's page 7), and the plot's floor rises until they clear `floor` - the anchored
    caption's strip, or (N1) the source line when the stack under the chart stands above the strip (`longform_stack`)."""
    s = (bot - top) / LAND_VIEWBOX[1]
    tick, cap_u = t["tick"] / s, ((LONGFORM_STRIP[0] if floor is None else floor) - top) / s
    xlab = LONGFORM_ASCENT * tick + (LONGFORM_XLAB_CLEAR_PX + LONGFORM_BORDER_PX / 2) / s   # T9 (3): the label's box top
    return {"scale": s, "tick": tick, "plot_l": max(70.0, 12 + 2.3 * tick),                  # clears the panel's foot
            "line_b": min(458.0, cap_u - 5 - xlab - LONGFORM_DESCENT * tick), "xtick_dy": xlab,
            "gutter": max(60.0, 40 + 2.6 * tick), "xlab_dy": xlab,
            "bars_b": min(440.0, cap_u - 5 - xlab - 1.4 * tick),
            "ylab_gap": LONGFORM_YLAB_GAP_PX / s, "rule_dy": (8 + 0.25 * t["tag"]) / s}


def longform_scale0(h_s: int = 1080) -> float:
    """One chart unit in rendered px on the UNSHIFTED longform chart box (LAND_FULL's height over the viewBox's): the
    scale every end-tag form is fitted at, because a chart the layout moves down only shrinks it."""
    return LAND_FULL["H"] * h_s / LAND_VIEWBOX[1]


def longform_tag_px(spec: dict, t: dict, form: str) -> float:
    """The widest end tag of a longform dense-line page in `form`, in rendered px (estimated at LONGFORM_TAG_EM)."""
    rides = {BADGE_ACCENT_COL.get(str(b.get("accent"))): str(b.get("tag") or "")
             for b in spec.get("badges") or [] if isinstance(b, dict) and b.get("inline")}
    out = 0.0
    for s in spec.get("series") or []:
        if not isinstance(s, dict) or s.get("muted"):
            continue
        label, name = str(s.get("label") or ""), str(s.get("name") or "")
        text = (label + " " + name).strip() if form == "full" else (label or name)
        px = len(text) * LONGFORM_TAG_EM["name"] * t["tag"]
        chip = rides.get(str(s.get("color")), "")
        if chip and form != "value":
            px += LONGFORM_CHIP_DX_PX + len(chip) * LONGFORM_TAG_EM["chip"] * t["chip"]
        out = max(out, px)
    return out


def longform_tag_units(spec: dict, t: dict, form: str, scale: float) -> float:
    """The widest end tag of a longform dense-line page in `form`, in chart units at `scale` (estimated)."""
    return longform_tag_px(spec, t, form) / scale


def _longform_max_vw(tags_u: float, scale: float, w_s: int = 1920) -> float:
    return ((LAND_PHONE_SAFE_RIGHT - LAND_FULL["X"]) * w_s / scale
            + LAND_PLOT["R"] * LAND_VIEWBOX[0] - LAND_TAG_GAP - tags_u)


def longform_tag_form(spec: dict, preset: str) -> str | None:
    """The fullest end-tag form that keeps every tag on the stage at the unshifted chart scale (a chart the layout
    moves down only shrinks its scale, which gives the tags more room), or None when not even the values fit."""
    t, scale = LONGFORM_TYPE_SCALE[preset], longform_scale0()
    for form in LONGFORM_TAG_FORMS:
        if _longform_max_vw(longform_tag_units(spec, t, form, scale), scale) >= LAND_PHONE_MIN_VIEWBOX_W:
            return form
    return None


def longform_page_vw(spec: dict, scale: float | None = None, w_s: int = 1920) -> float:
    """The viewBox width a longform chart is drawn in (the engine's `lpLongformVW`): a dense-line page's is narrowed
    until its widest end tag - its own, in its own form, or (N2) the widest its `then=` states write, carried as
    `axes.tag_room` - ends inside the stage's safe right edge; a bars page keeps the legacy 1000."""
    if spec.get("builder") != "dense-line":
        return float(LAND_VIEWBOX[0])
    scale = longform_scale0() if scale is None else scale
    axes = spec.get("axes") or {}
    px = max(longform_tag_px(spec, longform_type(spec), axes.get("tag_form") or "full"), float(axes.get("tag_room") or 0))
    return max(float(LAND_PHONE_MIN_VIEWBOX_W), _longform_max_vw(px / scale, scale, w_s))


def apply_longform(page: dict, preset: str | None = None) -> dict:
    """Stamp a page with the long form's profile: `axes.readability`, the preset it is set in (`type_scale`) and, on a
    dense-line page, the end-tag form that fits (`tag_form`). In place; the page is returned."""
    axes = page.setdefault("axes", {})
    axes["readability"] = LONGFORM
    axes["type_scale"] = preset if preset in LONGFORM_PRESETS else (
        axes.get("type_scale") if axes.get("type_scale") in LONGFORM_PRESETS else LONGFORM_DEFAULT_PRESET)
    if page.get("builder") == "dense-line":
        axes["tag_form"] = longform_tag_form(page, axes["type_scale"]) or "value"
    else:
        axes.pop("tag_form", None)
    if page.get("builder") == PANELS:   # P69 T8b: each panel's end tags fitted to ITS box; one key for the page
        return _apply_longform_panels(page)
    key = longform_key(page)   # P69 T10: the names the end tags gave up, and the size their one row is set in
    axes.pop("key_px", None)
    if key:
        axes["key"] = key
        axes["key_px"] = longform_key_px(page)
    else:
        axes.pop("key", None)
    return page


def apply_longform_states(page: dict, states: list) -> str | None:
    """REVIEW-P69-LANE-B-MERGE-2 N2: a longform page's `then=` states are drawn in ITS chart box, viewBox and preset,
    so each is stamped with the page's profile and preset and fitted its OWN end-tag form; and a dense-line page's
    viewBox makes room for the widest tag any line state writes (`axes.tag_room`, rendered px - written only when a
    state's tags are wider than the page's own, so a page whose states fit carries nothing new). In place. The
    refusal (a message) when a state cannot keep even its values on the stage, else None."""
    axes = page.get("axes") or {}
    preset = axes.get("type_scale") if axes.get("type_scale") in LONGFORM_PRESETS else LONGFORM_DEFAULT_PRESET
    t, room = LONGFORM_TYPE_SCALE[preset], 0.0
    for i, state in enumerate(states):
        if not isinstance(state, dict):
            continue
        if state.get("builder") == "dense-line" and longform_tag_form(state, preset) is None:
            return (f"then= state {i + 1} cannot keep even its end values inside the 16:9 stage at "
                    f"readability={LONGFORM}:{preset} (a value alone is the shortest end tag there is)")
        apply_longform(state, preset)   # REVIEW-P69-LANE-B-MERGE-3 M1: a state keeps ITS key - the names ITS tags gave up
        if state.get("builder") == "dense-line":
            room = max(room, longform_tag_px(state, t, state["axes"]["tag_form"]))
    if page.get("builder") == "dense-line" and room > longform_tag_px(page, t, axes.get("tag_form") or "full"):
        page["axes"]["tag_room"] = math.ceil(room * 10) / 10   # up to the tenth: the page's viewBox never grows past a state's fit
    # ... and every key stands in ONE band over the chart (the recast swaps the key, never the chart's box): the page
    # reserves the tallest - written only when a state's key needs more than the page's own, so every other page is
    # the page it was
    page["axes"].pop("key_w", None)
    page["axes"].pop("key_h", None)
    page["axes"].pop("state_ink", None)
    col = _longform_ink_col()[1]
    own_w, own_h = _longform_key_own(page, col)
    band = [(own_w, own_h)] + [_longform_key_own(s, col) for s in states if isinstance(s, dict)]
    band_w, band_h = max(b[0] for b in band), max(b[1] for b in band)
    if band_h > own_h + 1e-9:
        page["axes"]["key_w"] = math.ceil(band_w * 10) / 10
        page["axes"]["key_h"] = math.ceil(band_h * 10) / 10
    # ... and the key stands over EVERY chart's top ink, not only the page's own: a state that writes higher (a line's
    # plot over a bars page's, a y label) carries what it writes, so the band clears it (a keyed page only)
    if band_h > 0:
        own_ink = longform_state_ink(page)
        extra = [longform_state_ink(s) for s in states if isinstance(s, dict)]
        extra = [i for i in extra if i != own_ink]
        if extra:
            page["axes"]["state_ink"] = extra
    return None


def _longform_panel_scale(page: dict) -> float:
    """P69 T8b: the SMALLEST rendered scale (px per chart unit) a longform panels page draws a panel at in its home
    layout - the page's own estimated region (its ink, its key band) cut by the default layout. The end tags are fitted
    at it, so every panel's tags hold."""
    n = len(page.get(PANELS_KEY) or [])
    if not n:
        return longform_scale0()
    chart = _longform_full_boxes(page, *STAGE_PX["16:9"])["chart"]
    region = (chart["x"], chart["y"], LAND_PHONE_SAFE_RIGHT * STAGE_PX["16:9"][0] - chart["x"], chart["h"])
    return min(b[3] for b in panel_home_boxes(n, region)) / (LAND_VIEWBOX[1] + PANEL_SUB_U)


def longform_panel_tag_form(page: dict, panel: dict, preset: str, scale: float) -> str:
    """The fullest end-tag form whose widest tag fits a panel's OWN right margin (the line builder's 220 units, less
    its tag gap) at `scale`; `value` when none does - the name then rides the page's key (never a refusal)."""
    t, room = LONGFORM_TYPE_SCALE[preset], LAND_PLOT["R"] * LAND_VIEWBOX[0] - LAND_TAG_GAP
    view = {"series": panel.get("series") or [], "badges": page.get("badges") or []}
    for form in LONGFORM_TAG_FORMS:
        if longform_tag_units(view, t, form, scale) <= room:
            return form
    return "value"


def longform_panel_key(page: dict) -> list[dict]:
    """The page's ONE key rail: every name a panel's end tag gave up, once - `[{"panel", "series", "name"}]` in panel
    order, a name and colour two panels share keyed by the first (E53 s8: one name, in one place)."""
    out, seen = [], set()
    for pi, panel in enumerate(page.get(PANELS_KEY) or []):
        if ((panel.get("axes") or {}).get("tag_form") or "full") == "full":
            continue
        for si, s in enumerate(panel.get("series") or []):
            if not isinstance(s, dict) or s.get("muted"):
                continue
            name = str(s.get("name") or "").strip()
            if not (name and str(s.get("label") or "").strip()) or (name, s.get("color")) in seen:
                continue
            seen.add((name, s.get("color")))
            out.append({"panel": pi, "series": si, "name": name})
    return out


def _apply_longform_panels(page: dict) -> dict:
    """The long form on a panels page: each panel's tag form at the page's home scale (fitted with no key, then again
    under the key those forms give up, which moves the region down), and the page's one key rail. In place."""
    axes = page["axes"]
    for key in ("key", "key_px"):
        axes.pop(key, None)
    for _ in range(2):
        scale = _longform_panel_scale(page)
        for panel in page.get(PANELS_KEY) or []:
            panel.setdefault("axes", {})["tag_form"] = longform_panel_tag_form(page, panel, axes["type_scale"], scale)
        key = longform_panel_key(page)
        axes.pop("key", None)
        axes.pop("key_px", None)
        if key:
            axes["key"] = key
            axes["key_px"] = longform_key_px(page)
    return page


def _longform_place(y: float, h: float) -> float:
    """Where an item `h` tall that would stand at `y` does stand: at `y`, or under the caption strip's foot if it
    would meet the strip (N1)."""
    return LONGFORM_STRIP[1] if h > 0 and y + h > LONGFORM_STRIP[0] and y < LONGFORM_STRIP[1] else y


def longform_stack(bot: float, src_h: float, rail_h: float, h_s: int = 1080) -> dict:
    """The source's and the key rail's tops under a chart whose foot is `bot` (rendered px), and whether both stay on
    the stage: the engine's `lpLongformStack`, line for line (N1)."""
    g_src, g_rail = LAND_SRC_GAP * PUNCH_SCALE * h_s, LAND_RAIL_GAP * PUNCH_SCALE * h_s
    src_y = _longform_place(bot + g_src, src_h)
    rail_y = _longform_place(max(bot + g_rail, src_y + src_h + LONGFORM_STACK_GAP_PX if src_h > 0 else bot + g_rail), rail_h)
    end = max(src_y + src_h if src_h > 0 else 0.0, rail_y + rail_h if rail_h > 0 else 0.0)
    first = src_y if src_h > 0 else rail_y if rail_h > 0 else float(h_s)
    return {"bot": bot, "src_y": src_y, "rail_y": rail_y, "floor": min(float(LONGFORM_STRIP[0]), first),
            "fits": end <= h_s - LONGFORM_EDGE_PX}


def longform_chart_box(spec: dict, t: dict, sub_bottom: float, src_h: float, rail_h: float = 0.0,
                       h_s: int = 1080, key_h: float = 0.0) -> dict:
    """The longform chart box in rendered px - `top`, `bot` - and what stands under it (`src_y`, `rail_y`, the `floor`
    its ticks clear): the engine's `lpLongformBox`, line for line. The foot is the full-stage box's, raised (N1) to the
    first of: the source standing above the caption strip, then the source and the rail both above it. P69 T10: a key
    `key_h` tall stands in the top band (`key_y`), M28's air under the sub and over the chart's top ink - the chart
    moves down to make that room, never the key onto the sub."""
    top0, bot0 = LAND_FULL["Y"] * h_s, (LAND_FULL["Y"] + LAND_FULL["H"]) * h_s
    g_src, g_rail = LAND_SRC_GAP * PUNCH_SCALE * h_s, LAND_RAIL_GAP * PUNCH_SCALE * h_s
    cands = (bot0, LONGFORM_STRIP[0] - g_src - src_h,
             LONGFORM_STRIP[0] - rail_h - max(g_rail, g_src + src_h + LONGFORM_STACK_GAP_PX))
    stack: dict = {}
    for cand in cands:
        stack = longform_stack(min(bot0, cand), src_h, rail_h, h_s)
        if stack["fits"]:
            break
    bot = stack["bot"]
    tu, vh = LONGFORM_PLOT_T.get(str(spec.get("builder")), LONGFORM_PLOT_T["story"]), LAND_VIEWBOX[1]
    axes = spec.get("axes") or {}
    band = key_h + 0.5 * t["tick"] if key_h > 0 else 0.0   # P69 T10: the key and M28's air under it
    base = sub_bottom + 0.5 * t["tick"] + band
    # REVIEW-P69-LANE-B-MERGE-3 M1: every chart the page can become stands in this box, each with its OWN plot top and
    # the ink above it (`axes.state_ink`) - the box clears the highest of them, and the key stands over that one
    reach = _longform_reaches(spec, t)
    top = max([top0] + [(base + above - tu_i * bot / vh) / (1 - tu_i / vh) for tu_i, above in reach])
    key_y = top + min(tu_i * (bot - top) / vh - above for tu_i, above in reach) - 0.5 * t["tick"] - key_h
    return dict(stack, top=top, key_y=key_y)


def _longform_above(t: dict, ylabel: bool, rules: bool) -> float:
    """The ink a chart carries above its plot top, rendered px: half a tick, the y label's row, a rule's name."""
    return max(0.5 * t["tick"], LONGFORM_YLAB_GAP_PX + t["tick"] if ylabel else 0.0,   # a label's box
               8 + 1.25 * t["tag"] if rules else 0.0)                                    # reaches ~1 em up


def longform_state_ink(spec: dict) -> dict:
    """What moves a chart's top ink: its builder's plot top (viewBox units) and whether it writes a y label or a named
    rule above the plot. The shape `axes.state_ink` carries per `then=` state (M1)."""
    axes = spec.get("axes") or {}
    if spec.get("builder") == PANELS:   # P69 T8b: the region's top is the panels' own - their y labels and rules are inside their boxes
        return {"tu": LONGFORM_PLOT_T[PANELS], "ylabel": False, "rules": False}
    rules = any(isinstance(h, dict) and h.get("label") for h in (axes.get("hlines") or ([axes["hline"]] if axes.get("hline") else [])))
    return {"tu": float(LONGFORM_PLOT_T.get(str(spec.get("builder")), LONGFORM_PLOT_T["story"])),
            "ylabel": bool(axes.get("ylabel")), "rules": rules}


def _longform_reaches(spec: dict, t: dict) -> list[tuple[float, float]]:
    """(plot top in viewBox units, ink above it in rendered px) for the page and each state it names."""
    own = longform_state_ink(spec)
    inks = [own] + [s for s in ((spec.get("axes") or {}).get("state_ink") or []) if isinstance(s, dict)]
    return [(float(i["tu"]), _longform_above(t, bool(i.get("ylabel")), bool(i.get("rules")))) for i in inks]


def longform_text_px(text: str, role: str, px: float) -> float:
    """The rendered width of `text` in a longform page role (`title` | `sub` | `source`) set at `px` rendered: its
    glyphs' Inter advances at the role's weight and at the opsz the browser picks (the CSS size, px / the punch)."""
    weight = LONGFORM_WEIGHT[role]
    lo, hi = LONGFORM_ADVANCES[(weight, 14)], LONGFORM_ADVANCES[(weight, 32)]
    k = (min(LONGFORM_OPSZ[1], max(LONGFORM_OPSZ[0], px / PUNCH_SCALE)) - LONGFORM_OPSZ[0]) / (LONGFORM_OPSZ[1] - LONGFORM_OPSZ[0])
    mean = (sum(lo) + (sum(hi) - sum(lo)) * k) / len(lo)
    units = 0.0
    for ch in str(text):
        i = LONGFORM_ADV_CHARS.find(ch)
        units += mean if i < 0 else lo[i] + (hi[i] - lo[i]) * k
    return units * px / LONGFORM_ADV_UPM


def longform_lines(text: str, role: str, px: float, box_w: float) -> int:
    """The lines a longform page role writes `text` in, `box_w` px wide: the browser's greedy break at the spaces
    between words (a word is one unbreakable run - `lpGlyphsWrap`), measured at the face's own advances."""
    words = str(text or "").split()
    if not words:
        return 0
    space = longform_text_px(" ", role, px)
    lines, run = 1, 0.0
    for word in words:
        want = longform_text_px(word, role, px)
        if run and run + space + want > box_w + 0.5:
            lines, run = lines + 1, want
        else:
            run = run + space + want if run else want
    return lines


def _longform_rail_h(spec: dict) -> float:
    n = len([b for b in spec.get("badges") or [] if isinstance(b, dict) and not b.get("inline")])
    rows = -(-n // LONGFORM_PILLS_PER_ROW)
    return rows * LONGFORM_PILL_PX + max(0, rows - 1) * LONGFORM_PILL_GAP_PX


def _longform_ink_col(w_s: int = 1920) -> tuple[float, float]:
    """The longform page's ink column in rendered px: its left edge (the title's) and its width (to the stage's safe
    right edge) - the column the title, sub and source wrap in and the key rail's row fills."""
    bx, by, bw, _bh = LAND_BOARD
    vx = bx + bw / 2 - 0.5 / PUNCH_SCALE
    ink_x = _punch_pt(max(bx + 0.027, vx + 0.03)) * w_s
    return ink_x, LAND_PHONE_SAFE_RIGHT * w_s - ink_x


def _longform_full_boxes(spec: dict, w_s: int, h_s: int) -> dict:
    """A longform page's boxes, ESTIMATED the way the engine lays it out (the fixture measures and outranks it; N3:
    held to the engine's own boxes at every preset by `test_longform_profile` and `test_page_boxes`)."""
    t, dense = longform_type(spec), spec.get("builder") == "dense-line"
    bx, by, bw, bh = LAND_BOARD
    half = 0.5 / PUNCH_SCALE
    vx, vy = bx + bw / 2 - half, by + bh / 2 - half
    ink_x = _longform_ink_col(w_s)[0]
    title_frac = round(max(by + 0.024, vy + 0.035) * 100, 2) / 100   # the engine writes the title's top toFixed(2) %
    title_y = _punch_pt(title_frac) * h_s
    ink_w = LAND_PHONE_SAFE_RIGHT * w_s - ink_x
    # the engine lays the ink out in the page's own CSS px and READS it back whole (offsetTop / offsetHeight), so the
    # layout's heights are snapped to whole CSS px here too; the boxes report the ink's own (unsnapped) extent
    lines = {role: (max(1, longform_lines(spec.get(key), role, t[size], ink_w)) if str(spec.get(key) or "").strip() else 0)
             for role, key, size in (("title", "title", "title"), ("sub", "sub", "sub"), ("source", "source", "src"))}
    css_h = {role: lines[role] * round(t[size] / PUNCH_SCALE, 3) * LONGFORM_LINE_H
             for role, size in (("title", "title"), ("sub", "sub"), ("source", "src"))}
    whole = lambda v: math.floor(v + 0.5)  # noqa: E731
    rend = lambda css_y: h_s / 2 + (css_y - h_s / 2) * PUNCH_SCALE  # noqa: E731
    title_top = whole(title_frac * h_s)
    sub_top = title_top + whole(css_h["title"]) + LONGFORM_SUB_GAP
    title_h, sub_h, src_h = (css_h[r] * PUNCH_SCALE for r in ("title", "sub", "source"))
    sub_y = rend(sub_top)
    sub_bottom = rend(sub_top + whole(css_h["sub"])) if lines["sub"] else rend(title_top + whole(css_h["title"]))
    rail_h = _longform_rail_h(spec)
    key_w, key_h = longform_key_box(spec, ink_w)   # P69 T10: the key rail, measured by the engine off its whole CSS px
    key_h = whole(key_h / PUNCH_SCALE) * PUNCH_SCALE
    box = longform_chart_box(spec, t, sub_bottom, whole(css_h["source"]) * PUNCH_SCALE,
                             whole(rail_h / PUNCH_SCALE) * PUNCH_SCALE, h_s, key_h)
    top, bot = box["top"], box["bot"]
    g = longform_geom(t, top, bot, box["floor"])
    s, cx, tu = g["scale"], LAND_FULL["X"] * w_s, LONGFORM_PLOT_T["dense-line" if dense else "story"]
    if dense:
        tags_u = longform_tag_units(spec, t, (spec.get("axes") or {}).get("tag_form") or "full", s)
        vw, left, right = longform_page_vw(spec, s, w_s), g["plot_l"], LAND_PLOT["R"] * LAND_VIEWBOX[0]
        floor, foot = g["line_b"], g["line_b"] + g["xtick_dy"] + LONGFORM_DESCENT * g["tick"]
    else:   # the bars page's plot is its PANEL (the tick rules' own extent, x0 - 20 to x1 + 20) over its names
        tags_u, vw, right = 0.0, float(LAND_VIEWBOX[0]), 0.0
        left = max(g["gutter"], float((spec.get("axes") or {}).get("left_gutter") or 0)) - 20
        floor, foot = g["bars_b"], g["bars_b"] + g["xlab_dy"] + 1.4 * g["tick"]
    ylab = LONGFORM_YLAB_GAP_PX + LONGFORM_ASCENT * t["tick"] if (spec.get("axes") or {}).get("ylabel") else 0.0
    out = {
        "title": _box(ink_x, title_y, ink_w, title_h),
        "sub": _box(ink_x, sub_y, ink_w, sub_h),
        "chart": _box(cx, top, vw * s, bot - top),
        "plot": _box(cx + left * s, top + tu * s - ylab, (vw - left - right) * s, (foot - tu) * s + ylab),
        "source": _box(ink_x, box["src_y"], ink_w, src_h),
        "rail": _box(ink_x, box["rail_y"], ink_w, rail_h),
        "tags": _box(cx + (vw - LAND_PLOT["R"] * LAND_VIEWBOX[0] + LAND_TAG_GAP) * s, top + tu * s, tags_u * s, (floor - tu) * s),
    }
    if key_h > 0:
        out[KEY_BOX] = _box(ink_x, box["key_y"], key_w, key_h)
    if spec.get("builder") == PANELS:   # P69 T8b: the floor its panels stop over (page_boxes pops it)
        out["_floor"] = box["floor"]
    return out

def _readability_profile(spec: dict) -> str | None:
    """The page-scoped profile carried by the dense page's axes, if any."""
    value = (spec.get("axes") or {}).get("readability")
    return value if value in READABILITY_PROFILES else None


def _profile_tag_units(spec: dict, profile: str | None = None) -> float:
    """Inline end-tag width in the profile's chart user units.

    ``spec`` may be the normalized page or the source series passed through validation. The
    profile is only called for a dense-line page; an absent builder on source is therefore valid.
    """
    if profile != "landscape-phone":
        return tag_units(spec)
    builder = spec.get("builder")
    if builder is not None and str(builder) not in LAND_TAG_BUILDERS:
        return 0.0
    raw = spec.get("series") or []
    if not isinstance(raw, list):
        return 0.0
    rides = {BADGE_ACCENT_COL.get(str(b.get("accent"))): str(b.get("tag") or "")
             for b in spec.get("badges") or [] if isinstance(b, dict) and b.get("inline")}
    out = 0.0
    for s in raw:
        if not isinstance(s, dict) or s.get("muted"):
            continue
        tag = rides.get(str(s.get("color")), "")
        name = ((s.get("label") or "") + " " + (s.get("name") or "")).strip()
        out = max(out, len(name) * LAND_PHONE_NAME_U
                  + ((len(tag) + 1) * LAND_PHONE_BADGE_U if tag else 0.0))
    return out


def _readability_fit_error(series: dict) -> str | None:
    """Refuse a profile whose enlarged end tags cannot fit without stage clipping."""
    value = series.get("readability") or (series.get("axes") or {}).get("readability")
    if value != "landscape-phone":
        return None
    stage_w, stage_h = STAGE_PX["16:9"]
    scale = LAND_FULL["H"] * stage_h / LAND_PHONE_VIEWBOX_H
    max_vw = ((LAND_PHONE_SAFE_RIGHT * stage_w - LAND_FULL["X"] * stage_w) / scale
              + LAND_PLOT["R"] * LAND_VIEWBOX[0] - LAND_TAG_GAP
              - _profile_tag_units(series, "landscape-phone"))
    if max_vw < LAND_PHONE_MIN_VIEWBOX_W:
        return ("readability='landscape-phone' cannot fit its enlarged inline end tags inside the "
                f"16:9 stage (maximum viewBox width {max_vw:.1f} < {LAND_PHONE_MIN_VIEWBOX_W})")
    return None


def _landscape_profile_geometry(spec: dict, w_s: int, h_s: int) -> dict | None:
    """Return the rendered chart/viewBox geometry for T17, or None for legacy geometry."""
    if _readability_profile(spec) != "landscape-phone" or not full_stage(spec, "16:9"):
        return None
    cx, cy = LAND_FULL["X"] * w_s, LAND_FULL["Y"] * h_s
    ch = LAND_FULL["H"] * h_s
    scale = ch / LAND_PHONE_VIEWBOX_H
    max_vw = ((LAND_PHONE_SAFE_RIGHT * w_s - cx) / scale
              + LAND_PLOT["R"] * LAND_VIEWBOX[0] - LAND_TAG_GAP
              - _profile_tag_units(spec, "landscape-phone"))
    vw = max(LAND_PHONE_MIN_VIEWBOX_W, round(max_vw, 3))
    return {"vw": vw, "vh": LAND_PHONE_VIEWBOX_H, "scale": scale, "B": LAND_PHONE_B / LAND_PHONE_VIEWBOX_H,
            "x": cx, "y": cy, "w": vw * scale, "h": ch,
            "tag_units": _profile_tag_units(spec, "landscape-phone")}


def treemap_plot(chart: dict, aspect: str) -> dict:
    """The rect a TREEMAP's cells are laid out in: the page's own plot margins inside the chart box,
    with the landscape viewBox's LETTERBOX applied.

    Every other builder can live with this module's estimate of where the ink lands, because being a
    line out is a line out. A treemap cannot: its layout is tuned to the plot's ASPECT, and a plot
    estimated at 1.19 when the player will draw at 1.65 turns every squarified cell into a strip and
    scales its label with it (read off the first rendered frame, 2026-09-11). The landscape chart's
    viewBox is 1000x560 with the default preserveAspectRatio, so it is scaled to FIT the chart box and
    centred in it; the page's plot margins are then the line builder's own."""
    if aspect == "9:16":
        P = PORTRAIT_PLOT
        return _box(chart["x"] + P["L"], chart["y"] + P["T"], chart["w"] - P["L"] - P["R"], chart["h"] - P["T"] - P["B"])
    vw, vh = LAND_VIEWBOX
    s = min(chart["w"] / vw, chart["h"] / vh)
    ox, oy = chart["x"] + (chart["w"] - vw * s) / 2, chart["y"] + (chart["h"] - vh * s) / 2
    L = LAND_PLOT
    return _box(ox + L["L"] * vw * s, oy + L["T"] * vh * s,
                (1 - L["L"] - L["R"]) * vw * s, (L["B"] - L["T"]) * vh * s)


# ---- P69 T8b: WHERE THE PANELS STAND - the layout law, and the focus states that move it ----------------------------
# E99 s104 amended again: "focus is a COMPOSABLE state, not a fixed mode". A FOCUS STATE names (a) a LAYOUT - `row`
# (side by side), `stack`, `quad` (a 2 x 2 grid: two active take a row, one takes the page) or `free` (a box per panel,
# stage fractions) - laid over the ACTIVE panels, and (b) per panel a ROLE: `active` (sharp, full ink, its species
# live), `receded` (at its HOME box, scaled back, dimmed and blurred behind the active ones - each a dial with a
# default, PANEL_RECEDE), or `hidden`. The page's HOME is its default layout with every panel active; a change of
# state on a word is ONE transition - every panel's box, ink and blur on the transition's own clock (the engine's
# `lpPanelPoses`). Every panel keeps its own viewBox's aspect in every box (the fit is `meet`, centred - the chart is
# the same chart at another size, never a stretched one), and a layout is packed to the region's left edge and centred
# on its height, so ONE active panel stands exactly where a single-chart page's chart stands (the resize from a
# standing chart into its slot is a move between two boxes of that one aspect). This is the engine's law, mirrored.
PANEL_LAYOUTS = ("row", "stack", "quad", "free")
PANEL_ROLES = ("active", "receded", "hidden")
PANEL_RECEDE = {"scale": 0.86, "dim": 0.55, "blur": 5.0}   # the engine's LP_PANELS.RECEDE: scale-back about the home box's
# centre, the share of the panel's ink taken away, and the depth-of-field blur in stage px (the blur-zoom's own backdrop
# blur is 18 px - a rack focus keeps the receded chart READABLE as a chart, only soft) [DERIVED: the rack-focus frames]
PANEL_RECEDE_BOUNDS = {"scale": (0.3, 1.0), "dim": (0.0, 0.95), "blur": (0.0, 24.0)}
PANEL_GAP = 0.03   # the gutter between two cells, a share of the region's WIDTH, both ways (the card's 44 of 1056 units)
PANELS_KEY = "panels"   # page_boxes' per-panel boxes (a panels page only)
# a landscape panel's SUB BAND: its viewBox reaches this many units ABOVE the line builder's own 0 (the builder keeps 40
# over its plot - a y label's row, never a title's), so the panel's sub stands inside its own box at any size
PANEL_SUB_U = 56.0
PANEL_FLOOR_AIR = 6.0   # rendered px a full-stage panels region stops over its FLOOR (a panel's x ticks are inside its box)


def default_panel_layout(n: int, aspect: str = "16:9") -> str:
    """The page's HOME layout: stacked on a 9:16 stage, a quad for four on 16:9, else side by side."""
    if aspect == "9:16":
        return "stack"
    return "quad" if n >= 4 else "row"


def panel_grid(layout: str, k: int) -> tuple[int, int]:
    """(columns, rows) of `layout` for `k` panels: a quad's two take a row and its one takes the page."""
    return ((1, k) if layout == "stack" else (2, 2) if layout == "quad" and k >= 3
            else (2, 1) if layout == "quad" and k == 2 else (k, 1))


def panel_cells(layout: str, k: int, region: tuple) -> list[tuple]:
    """`k` cells of `layout` over `region` (x, y, w, h), in reading order."""
    x, y, w, h = region
    if k <= 0:
        return []
    cols, rows = panel_grid(layout, k)
    g = PANEL_GAP * w
    cw, ch = (w - g * (cols - 1)) / cols, (h - g * (rows - 1)) / rows
    return [(x + (i % cols) * (cw + g), y + (i // cols) * (ch + g), cw, ch) for i in range(k)]


def panel_fit(cell: tuple, aspect: float, fill: bool = True) -> tuple:
    """A panel's box inside `cell`, centred. P69 T8c: a landscape panel (`fill`) takes the cell's WHOLE WIDTH - the line
    builder re-lays its plot out at any viewBox width - and the cell's height, or the aspect's when the cell is taller
    (its plot is a fixed height). `fill=False` is T8b's: the largest box of `aspect` (w / h), the svg's own `meet`."""
    x, y, w, h = cell
    if fill:
        fh = min(h, w / aspect)
        return (x, y + (h - fh) / 2, w, fh)
    fw, fh = (h * aspect, h) if w / h > aspect else (w, w / aspect)
    return (x + (w - fw) / 2, y + (h - fh) / 2, fw, fh)


def panel_layout(layout: str, k: int, region: tuple, aspect: float, fill: bool = True) -> list[tuple]:
    """`k` panel boxes laid out as `layout` in `region`: ONE box size for the grid, hung from the region's TOP (the page
    reads title, sub, charts). P69 T8c (`fill`, every landscape page): a box is its CELL's full width - a lone panel
    spans the whole region, as a single-chart page's chart does - and its cell's height, or `aspect`'s when the cell is
    taller (the line builder's landscape plot is a fixed height; a quad panel growing to the page keeps T8b's box).
    `fill=False` (portrait) is T8b's law: boxes of `aspect`, the largest the tighter axis allows, a group centred
    across the region and a lone panel on its left edge. Pure."""
    if k <= 0:
        return []
    x, y, w, h = region
    cols, rows = panel_grid(layout, k)
    g = PANEL_GAP * w
    if fill:
        cw, ch = (w - g * (cols - 1)) / cols, (h - g * (rows - 1)) / rows
        bh = min(ch, cw / aspect)
        return [(x + (i % cols) * (cw + g), y + (i // cols) * (bh + g), cw, bh) for i in range(k)]
    bw = min((w - g * (cols - 1)) / cols, aspect * (h - g * (rows - 1)) / rows)
    bh = bw / aspect
    x0 = x if k == 1 else x + (w - (cols * bw + (cols - 1) * g)) / 2
    return [(x0 + (i % cols) * (bw + g), y + (i // cols) * (bh + g), bw, bh) for i in range(k)]


def panel_aspect(n: int, region: tuple, aspect: str = "16:9") -> float:
    """A panel's viewBox aspect: its HOME CELL's (the page's default layout over its region), so the home layout FILLS
    the region - the line builder draws at any viewBox width (its plot runs L..W-R), and the panel's viewBox is
    `panel_view_w` x (560 + its sub band). A quad's cell and the whole region have nearly one aspect, so a quad
    panel growing to the page fills it too. A row's cell is narrower than the region: since P69 T8c a landscape box of
    another aspect is the same chart RE-LAID OUT at that width (`panel_layout`'s `fill`), so a lone panel spans it."""
    cell = panel_cells(default_panel_layout(n, aspect), n, region)[0]
    return cell[2] / cell[3]


def panel_view_w(a: float) -> float:
    """A landscape panel's viewBox width for aspect `a`: its height is the line builder's 560 plus its sub band."""
    return a * (LAND_VIEWBOX[1] + PANEL_SUB_U)


def panel_home_boxes(n: int, region: tuple, aspect: str = "16:9") -> list[tuple]:
    """Every panel's HOME box: the default layout, every panel active."""
    # the home cells ARE of the panel aspect, so both laws agree; the engine keeps T8b's arithmetic for them, to the bit
    return panel_layout(default_panel_layout(n, aspect), n, region, panel_aspect(n, region, aspect), fill=False)


def _panels_region(spec: dict, chart: dict, aspect: str, floor: float | None = None) -> tuple:
    """The region a panels page lays its panels in, stage px: its chart box - which a FULL-STAGE 16:9 page widens to
    the stage's safe right edge (a panels page keeps no end-tag margin of its own: every panel carries its own) and
    stops PANEL_FLOOR_AIR over its `floor` (the anchored caption's strip, or the long form's first ink under the
    chart): a line page raises its ticks over that strip, and a panel's ticks are inside its box."""
    w, h = chart["w"], chart["h"]
    if aspect == "16:9" and full_stage(spec, aspect):
        w = LAND_PHONE_SAFE_RIGHT * STAGE_PX["16:9"][0] - chart["x"]
        f = CAPTION_ANCHOR["16:9"][1] if floor is None else floor
        h = min(h, f - PANEL_FLOOR_AIR - chart["y"])
    return (chart["x"], chart["y"], w, h)


def _panel_plot(box: tuple, spec_panel: dict) -> dict:
    """One panel's plot in stage px: the line builder's own margins inside the panel's box (its viewBox fills it)."""
    x, y, w, h = box
    s = h / (LAND_VIEWBOX[1] + PANEL_SUB_U)   # px per unit: the viewBox is the box's own aspect
    vw, l_u, r_u = w / s, LAND_PLOT["L"] * LAND_VIEWBOX[0], LAND_PLOT["R"] * LAND_VIEWBOX[0]
    return _box(x + l_u * s, y + (PANEL_SUB_U + LAND_PLOT["T"] * LAND_VIEWBOX[1]) * s,
                (vw - l_u - r_u) * s, (LAND_PLOT["B"] - LAND_PLOT["T"]) * LAND_VIEWBOX[1] * s)


def panel_boxes(spec: dict, chart: dict, aspect: str, floor: float | None = None) -> list[dict]:
    """Each panel's HOME box and its plot, stage px, estimated from the page's chart box."""
    panels = spec.get(PANELS_KEY) or []
    region = _panels_region(spec, chart, aspect, floor)
    out = []
    for p, b in zip(panels, panel_home_boxes(len(panels), region, aspect)):
        out.append({"box": _box(*b), "plot": _panel_plot(b, p) if aspect == "16:9" else
                    _box(b[0] + PORTRAIT_PLOT["L"], b[1] + PORTRAIT_PLOT["T"], b[2] - PORTRAIT_PLOT["L"] - PORTRAIT_PLOT["R"],
                         b[3] - PORTRAIT_PLOT["T"] - PORTRAIT_PLOT["B"])})
    return out


def _union(boxes: list[dict]) -> dict:
    x0, y0 = min(b["x"] for b in boxes), min(b["y"] for b in boxes)
    x1, y1 = max(b["x"] + b["w"] for b in boxes), max(b["y"] + b["h"] for b in boxes)
    return _box(x0, y0, x1 - x0, y1 - y0)


# ---- ONE PLACEMENT TRUTH (P50 T16, R26-27) -------------------------------------------------
# Everything above this line is an ESTIMATE of where the player will put the page's ink. The layout
# LAW in `_portrait_boxes` is the template's own, line for line (measured 2026-09-11: given the ink
# heights, the chart's top, the plot's L/R/T/B and the source line all land on the player's pixel).
# What Python cannot see is the INK: `_ink_lines` wraps at an average advance, and a title the
# player writes in ONE line is estimated at two - which moves every box under it by 76 px on a 9:16
# page. That is R26-27 exactly ("the x maths is exact, only y is off").
#
# THE FIXTURE. `measure_page_boxes.py` renders a representative page per builder per aspect in the
# headless player and writes what it MEASURES to `assets/page-boxes.v1.json`. A page's boxes are a
# pure function of its INK - the builder, the title, the sub's and the source's first clause, the
# rail's badge count, the basis label and the quiet zone are the ONLY inputs `_portrait_boxes` and
# `_landscape_boxes` read - so `page_ink_key` hashes exactly that, and a measured entry is valid for
# any page carrying the same ink, and for no other page at all. A page whose ink is not on file
# keeps today's estimate and SAYS so: `boxes["measured"]` is False and the compiler writes one line
# per estimated page into the build's report. The truth is never guessed - either the player's own
# numbers are on file for this ink, or the caller knows it is holding an estimate.
_REPO = Path(__file__).resolve().parents[3]
PAGE_BOXES_FIXTURE = _REPO / "content/video_engine/assets/page-boxes.v1.json"
PAGE_BOXES_SCHEMA = "page_boxes.v1"
BOX_KEYS = ("title", "sub", "chart", "plot", "source", "rail")
TAGS_KEY = "tags"   # R26-205: the end tag column, on a full-stage page only (the fixture measures the six above)
TAG_BOXES_KEY = "tag_boxes"   # P69 T6d: on a MEASURED full-stage page, each end tag at its drawn rect (the fixture's own)
TAG_INK_KEY = "tag_ink"       # REVIEW-P69-LANE-B-MERGE-4 MN3: ... and, on the entry, the tags those rects were measured for (`tag_ink`)
INK_KEYS = ("builder", "title", "sub", "source", "quiet_zone")
# Kept as a descriptive alias for callers that name the variant.  The fixture's
# actual key is the main lane's geometry key, ``16:9|full_stage``.
FULL_STAGE_VARIANT = "full_stage"
_PLAYER_TEMPLATE = _REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
_PLAYER_ENGINE = _REPO / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
_PLAYER_SHA_CACHE: tuple[tuple[int, int, int, int], str] | None = None
# R26-235: a page's boxes are a function of its ink AND of the geometry that ink is drawn in. The ink
# is the entry's key (`page_ink_key`); the geometry is the ASPECT, which is the level the fixture has
# always been keyed at - and at 16:9 there are now TWO geometries, because a page the compiler stamps
# `full_stage` puts the same ink in `_landscape_full_boxes` instead of `_landscape_boxes`. So the
# geometry key gains the flag rather than the ink key: `16:9` and `16:9|full_stage` are measured
# separately and a page is served the one it is drawn in. (The flag stays OUT of `page_ink_key` for
# the reason R26-205 found the hard way: the key does not know the aspect, so a caller that stamps a
# page with the compiler's `ASPECT` unset and then asks at 9:16 would re-key every portrait page it
# has - `test_dock_over_build.py` caught exactly that. A KEY the aspect is already in cannot.)
FULL_STAGE_SUFFIX = f"|{FULL_STAGE_VARIANT}"


def box_key(spec: dict, aspect: str) -> str:
    """The fixture key this page's boxes are measured under: the aspect, plus the full-stage flag when
    this page takes the whole stage at it (R26-235). `9:16` and an unstamped 16:9 page are unchanged,
    so every entry measured before this row still answers for the page it measured."""
    return f"{aspect}{FULL_STAGE_SUFFIX}" if full_stage(spec, aspect) else aspect


def page_ink_key(spec: dict) -> str:
    """The fingerprint of everything about `spec` that moves a box: its ink, its rail and its zone.

    Two pages with the same key lay out identically at a given aspect - the DATA never moves a box,
    it is drawn inside the plot - so one measurement serves both. Stable across runs and machines."""
    rail = [b for b in spec.get("badges") or [] if not b.get("inline")]
    ink = {
        **{k: spec.get(k) for k in INK_KEYS},
        "sub_clause": first_clause(spec.get("sub"), True),
        "src_clause": first_clause(spec.get("source"), False),
        "rail_n": len(rail),
        "ylabel": (spec.get("axes") or {}).get("ylabel"),
        "tiers_n": len(spec.get("tiers")) if isinstance(spec.get("tiers"), list) else 0,
    }
    if spec.get("builder") == PANELS:   # P69 T8b: the panel count lays the boxes out (keyed only here: every other key stands)
        ink["panels_n"] = len(spec.get(PANELS_KEY) or [])
    # Keep the absent-profile fingerprint byte-compatible; only an opted-in geometry is a new ink
    # variant.  A profile's value must still be keyed because it changes the chart/viewBox and boxes.
    readability = (spec.get("axes") or {}).get("readability")
    if readability is not None:
        ink["readability"] = readability
    for key in ("type_scale", "tag_form", "tag_room", "key", "key_px", "key_w", "key_h", "state_ink"):   # P69 T8: the long form's preset, end-tag form and (N2) its states' tag room move its boxes; T10: its key's names; M1: its states' key band
        if (spec.get("axes") or {}).get(key) is not None:
            ink[key] = spec["axes"][key]
    if "left_gutter" in (spec.get("axes") or {}):
        ink["left_gutter"] = spec["axes"]["left_gutter"]
    blob = json.dumps(ink, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def tag_ink(spec: dict) -> list[list]:
    """REVIEW-P69-LANE-B-MERGE-4 MN3: the fingerprint of a page's END TAGS - `[label, name, last value]` for every live
    series that writes one, in the spec's order. The one measured thing the DATA moves: an end tag stands at its line's
    last value and reads its label, so `tag_boxes` (P69 T6d) are served only to a page whose tags match the ones they
    were measured for; `page_ink_key` stays the key for every other box. Pure.

    P69 fixture-H: a tag stands at its last value IN THE PAGE'S Y DOMAIN, so a DECLARED `axes.domain` is part of
    where it lands - Steel and Paper H draws the golden's own ink at `domain=80,277` (the born domain, held until its
    rescale), at `[95, 1138.74]` and at the auto domain, three tag geometries under one ink. A declared domain joins
    each tag's fingerprint as a fourth member; a page that declares none keeps the three-member fingerprint, so every
    entry measured before this row still answers for the page it measured."""
    domain = (spec.get("axes") or {}).get("domain")
    try:
        scale = [round(float(v), 6) for v in domain] if isinstance(domain, (list, tuple)) and len(domain) == 2 else None
    except (TypeError, ValueError):
        scale = [str(v) for v in domain]   # an unreadable declared domain still keys the tags apart; never dropped
    out = []
    for s in spec.get("series") or []:
        if not isinstance(s, dict) or s.get("muted"):
            continue
        label, name = str(s.get("label") or "").strip(), str(s.get("name") or "").strip()
        if not (label or name):
            continue
        pts = s.get("pts") or []
        last = pts[-1][1] if pts and isinstance(pts[-1], (list, tuple)) and len(pts[-1]) > 1 else None
        try:
            last = round(float(last), 6)
        except (TypeError, ValueError):
            last = None if last is None else str(last)
        out.append([label, name, last] + ([scale] if scale is not None else []))
    return out


@functools.lru_cache(maxsize=4)
def _doc(path: str, mtime: float) -> dict:
    """The whole fixture document. A missing or malformed file reads as empty: the fixture is a
    measurement the compiler may not have, never a dependency it fails on. `mtime` is in the cache
    key so a re-measurement inside one process is seen."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get("schema") != PAGE_BOXES_SCHEMA:
        return {}
    return data


def _section(name: str, path: Path | None = None) -> dict:
    p = Path(path or PAGE_BOXES_FIXTURE)
    try:
        mtime = p.stat().st_mtime
    except OSError:
        return {}
    section = _doc(str(p), mtime).get(name)
    return section if isinstance(section, dict) else {}


def _fixture_document(path: Path | None = None) -> dict:
    """The decoded fixture document, including its player freshness marker."""
    p = Path(path or PAGE_BOXES_FIXTURE)
    try:
        mtime = p.stat().st_mtime
    except OSError:
        return {}
    return _doc(str(p), mtime)


def _player_sha256() -> str | None:
    """Hash both player files once per file-mtime tuple, ignoring checkout line endings."""
    global _PLAYER_SHA_CACHE
    try:
        template = _PLAYER_TEMPLATE.stat()
        engine = _PLAYER_ENGINE.stat()
    except OSError:
        return None
    key = (template.st_mtime_ns, template.st_size, engine.st_mtime_ns, engine.st_size)
    if _PLAYER_SHA_CACHE is not None and _PLAYER_SHA_CACHE[0] == key:
        return _PLAYER_SHA_CACHE[1]
    try:
        template = _PLAYER_TEMPLATE.read_bytes().replace(b"\r\n", b"\n")
        engine = _PLAYER_ENGINE.read_bytes().replace(b"\r\n", b"\n")
        digest = hashlib.sha256(template + engine).hexdigest()
    except OSError:
        return None
    _PLAYER_SHA_CACHE = (key, digest)
    return digest


def _full_stage_fixture_is_fresh(path: Path | None = None) -> bool:
    marker = _fixture_document(path).get("player_sha256")
    current = _player_sha256()
    return isinstance(marker, str) and current is not None and marker == current


def _valid_full_stage_entry(entry: object, ink: str) -> bool:
    boxes = entry.get("boxes") if isinstance(entry, dict) else None

    def finite_real(value: object) -> bool:
        if not isinstance(value, Real) or isinstance(value, bool):
            return False
        try:
            return math.isfinite(value)
        except (OverflowError, TypeError):
            return False

    def valid_box(value: object) -> bool:
        if not isinstance(value, dict):
            return False
        if not all(dimension in value for dimension in ("x", "y", "w", "h")):
            return False
        return (finite_real(value["x"]) and finite_real(value["y"])
                and finite_real(value["w"]) and value["w"] >= 0
                and finite_real(value["h"]) and value["h"] >= 0)

    return (isinstance(entry, dict) and entry.get("ink") == ink
            and entry.get("full_stage") is True
            and isinstance(boxes, dict)
            and all(valid_box(boxes.get(key)) for key in BOX_KEYS))


def fixture(path: Path | None = None) -> dict:
    """builder -> aspect -> entry, from `assets/page-boxes.v1.json` (or `path`): ONE representative
    page per builder, the fallback for any page carrying that representative's ink."""
    return _section("builders", path)


def measured_pages(path: Path | None = None) -> dict:
    """ink key -> aspect -> entry: the pages a PROJECT's compiled timeline named, measured one by
    one (`measure_page_boxes.py --project`). A builder has one representative but an episode has as
    many pages as it writes titles, so the pages an episode actually compiles are keyed by ink."""
    return _section("pages", path)


def measured_profiles(path: Path | None = None) -> dict:
    """`<builder>|longform:<preset>` -> geometry -> entry: each profiled builder's representative measured under the
    long form at every preset (REVIEW-P69-LANE-B-MERGE-2 N3, `measure_page_boxes.build_profiles`)."""
    return _section("profiles", path)


def _profile_entry(ink: str, geometry: str) -> dict | None:
    """The `profiles` entry whose ink is this page's own in this geometry, or None."""
    for by_geometry in measured_profiles().values():
        got = by_geometry.get(geometry) if isinstance(by_geometry, dict) else None
        if isinstance(got, dict) and got.get("ink") == ink:
            return got
    return None


def _serves_other_tags(entry: dict, other: dict | None, spec: dict) -> bool:
    """True when `entry` measured end tags that are not this page's (`tag_ink`) while `other` - the same ink in the
    same geometry - measured exactly this page's. Pure."""
    if not isinstance(other, dict) or other is entry:
        return False
    own = tag_ink(spec)
    return entry.get(TAG_INK_KEY) is not None and entry.get(TAG_INK_KEY) != own and other.get(TAG_INK_KEY) == own


def measured_entry(spec: dict, aspect: str) -> dict | None:
    """The fixture entry that measured THIS page's ink at this aspect, or None.

    The ink-keyed project page is tried first, then its builder representative. The entry is used
    only when its `ink` is this page's own, and only
    when it was measured in the GEOMETRY this page is drawn in (`box_key`: R26-235, a full-stage 16:9
    page lays out nothing like the same ink in the old landscape box, so the two are measured apart).
    An entry is also refused when its own `full_stage` flag disagrees with the key it is filed under -
    the fixture is a measurement, and a measurement that has to be reinterpreted is not one."""
    key = page_ink_key(spec)
    full = full_stage(spec, aspect)
    geometry = box_key(spec, aspect)
    page_entries = measured_pages().get(key)
    entry = page_entries.get(geometry) if isinstance(page_entries, dict) else None
    builder_entries = fixture().get(str(spec.get("builder")))
    builder_entry = builder_entries.get(geometry) if isinstance(builder_entries, dict) else None
    if not (isinstance(builder_entry, dict) and builder_entry.get("ink") == key):
        builder_entry = _profile_entry(key, geometry) or builder_entry   # N3: a longform representative, by its ink
    if not isinstance(entry, dict):
        entry = builder_entry
    elif _serves_other_tags(entry, builder_entry, spec):
        # P69 fixture-H: a project page and the builder's representative can share an INK and still draw their tags
        # (and their data) apart - H draws the golden's own ink in a declared domain. The entry measured on THIS
        # page's own tags is the one that measured this page; the other one's rects are another page's.
        entry = builder_entry
    if full and not _valid_full_stage_entry(entry, key):
        # A project-specific page may be malformed while its builder
        # representative is still a valid measured fallback.  Validate both
        # candidates before serving either one.
        entry = builder_entry
        if not _valid_full_stage_entry(entry, key):
            return None
    if not isinstance(entry, dict) or entry.get("ink") != key or bool(entry.get("full_stage")) != full:
        return None
    return entry


def measured_boxes(spec: dict, aspect: str) -> dict | None:
    """The player's own boxes for THIS page's ink, or None when nothing on file measured it."""
    entry = measured_entry(spec, aspect)
    boxes = (entry or {}).get("boxes")
    if not isinstance(boxes, dict) or not all(k in boxes for k in BOX_KEYS):
        return None
    out = {k: dict(boxes[k]) for k in BOX_KEYS}
    if isinstance(boxes.get(KEY_BOX), dict):   # P69 T10: a longform page's key rail, when it was measured with one
        out[KEY_BOX] = dict(boxes[KEY_BOX])
    if (isinstance(boxes.get(TAG_BOXES_KEY), list) and boxes[TAG_BOXES_KEY]   # P69 T6d: its end tags, each as drawn -
            and entry.get(TAG_INK_KEY) == tag_ink(spec)):                      # MN3: only for the tags they were drawn for
        out[TAG_BOXES_KEY] = [dict(b) for b in boxes[TAG_BOXES_KEY] if isinstance(b, dict)]
    if isinstance(entry.get(PANELS_KEY), list) and entry[PANELS_KEY]:   # P69 T8b: each panel's home box and plot, as drawn
        out[PANELS_KEY] = [{k: dict(v) for k, v in p.items() if isinstance(v, dict)} for p in entry[PANELS_KEY] if isinstance(p, dict)]
    return out


def measured_room(spec: dict, aspect: str) -> dict:
    """E65's room, for a page the fixture has measured: ``data_mask`` (16 rows of 16 characters over
    the PLOT, `1` where the data's ink touches the cell) and ``axis`` (the x tick labels' band under
    the plot, the y tick column beside it - furniture a card MAY partially overlap, unlike the data).

    ``{}`` when this page is not measured or was measured before E65: the placer then has boxes but
    no room, and falls back to the bands outside the plot exactly as it did before."""
    entry = measured_entry(spec, aspect) or {}
    mask = entry.get("data_mask")
    axis = entry.get("axis")
    out: dict = {}
    if isinstance(mask, list) and mask and all(isinstance(r, str) and len(r) == len(mask) for r in mask):
        out["data_mask"] = list(mask)
    if isinstance(axis, dict):
        out["axis"] = {k: (dict(v) if isinstance(v, dict) else None) for k, v in axis.items() if k in ("x", "y")}
    return out


def page_boxes(spec: dict, aspect: str = "16:9") -> dict:
    """Where this page puts its ink, in STAGE pixels (E45 §1).

    Keys: ``stage``/``safe``/``caption_anchor`` (the frame's own bands) and ``title``/``sub``/
    ``chart``/``plot``/``source``/``rail`` (the page's), each ``{x, y, w, h}``; ``quiet_zone``
    passes the spec's declared side through. ``plot`` is the DATA box plus the ink that lives
    inside it - the basis label above it (``axes.ylabel``) and the x tick labels below the axis -
    because a card over either of them covers the chart just as surely.

    ``measured`` says whose numbers these are (P50 T16): True when the fixture holds the player's
    own boxes for this page's INK (`measured_boxes`), False when this is `_portrait_boxes`' estimate.
    A measured page also carries ``data_mask`` and ``axis`` - E65's room INSIDE the plot.
    A caller that PLACES something by these boxes - `free_bands`, `page_place`, `centred_place` - is
    reading one truth or the other, and the compiler reports which for every page it compiles.

    Pure and deterministic; the spec is never mutated. An `object` page (no chart) reports the
    prop's field as its chart and an empty plot."""
    if aspect not in STAGE_PX:
        raise ValueError(f"aspect must be one of {'|'.join(STAGE_PX)}")
    w_s, h_s = STAGE_PX[aspect]
    # R26-205: at 16:9 a page stamped `full_stage` puts its chart on the whole stage, so its boxes
    # come from the full-stage law rather than from the board's inner box with a column kept out
    boxes = (_portrait_boxes if aspect == "9:16" else
             _landscape_full_boxes if full_stage(spec, aspect) else _landscape_boxes)(spec, w_s, h_s)
    if spec.get("builder") == "object":
        boxes["plot"] = _box(boxes["chart"]["x"], boxes["chart"]["y"], 0, 0)
    if spec.get("builder") == "tiers":
        boxes["bands"] = tier_bands(boxes["plot"], len(spec.get("tiers") or []))
    if spec.get("builder") == "treemap":
        boxes["plot"] = treemap_plot(boxes["chart"], aspect)
    floor = boxes.pop("_floor", None)
    if spec.get("builder") == PANELS:   # P69 T8b: the chart is the panels' box (to the safe edge); the plot every panel's box
        rx, ry, rw, _rh = _panels_region(spec, boxes["chart"], aspect)
        boxes["chart"] = _box(rx, ry, rw, boxes["chart"]["h"])
        boxes[PANELS_KEY] = panel_boxes(spec, boxes["chart"], aspect, floor)
        boxes["plot"] = _union([p["box"] for p in boxes[PANELS_KEY]])
        boxes.pop(TAGS_KEY, None)   # no page-wide end-tag column: every panel's tags stand inside its own box
    measured = measured_boxes(spec, aspect)
    if measured:                      # the player's own numbers for this ink win over every estimate above
        tags = boxes.get(TAGS_KEY)    # ... except the end tag column, which the fixture does not measure as a column
        boxes.update(measured)
        drawn = boxes.pop(TAG_BOXES_KEY, None)
        if tags is not None:
            boxes[TAGS_KEY] = tags
            if drawn:   # P69 T6d: ... and beside it the tags AS DRAWN, each at its rect (the stamp's ring fits around these)
                boxes[TAG_BOXES_KEY] = drawn
        boxes.update(measured_room(spec, aspect))   # E65: the plot's empty room and the axis bands travel with them
        if spec.get("builder") == "tiers":   # the tier bands are a law over the PLOT: re-cut them on the measured one
            boxes["bands"] = tier_bands(boxes["plot"], len(spec.get("tiers") or []))
        if spec.get("builder") == PANELS and not measured.get(PANELS_KEY):   # the panels re-cut on the measured chart
            boxes[PANELS_KEY] = panel_boxes(spec, boxes["chart"], aspect, floor)
    sx, sy, sw, sh = SAFE_BOX[aspect]
    cx, cy, cw, ch = CAPTION_ANCHOR[aspect]
    out = {"aspect": aspect, "stage": _box(0, 0, w_s, h_s), "safe": _box(sx, sy, sw, sh),
           "caption_anchor": _box(cx, cy, cw, ch), "quiet_zone": spec.get("quiet_zone"),
           "measured": bool(measured), **boxes}
    if full_stage(spec, aspect):
        out[FULL_STAGE_BANDS_KEY] = _full_stage_bands(w_s, h_s)
    return out


def load_series(path: Path) -> dict:
    """Decode with parse_float=str so every float stays the file's own token."""
    data = json.loads(path.read_text(encoding="utf-8"), parse_float=str)
    if not isinstance(data, dict):
        raise ValueError("top level must be a JSON object")
    return data


def infer_variant(series: dict) -> str | None:
    """The variant this file's SHAPE names, or None when it is the author's call (`--check` alone).

    Only the unambiguous shapes: a `tiers` LIST is a tiers page, `props` an object page, `shares` the
    census (treemap) unless the file declares the donut's `peel`. A bars/pts file is a line page, a
    bars page, a decline or a progress page depending on what the SENTENCE does with it - which is
    not in the file, so it is never guessed."""
    if isinstance(series.get("tiers"), list):
        return "tiers"
    if isinstance(series.get("props"), list) and series["props"]:
        return "object"
    if isinstance(series.get("shares"), list):
        return "share" if series.get("peel") is not None else "treemap"
    return None


# P69 T10c (the operator, 2026-09-22, on row 7's thrown Bravos card: "Those charts still seem tough to read to me" and
# "Evidence cards that are using charts need to use the whole card and use bigger fonts and thicker lines"): the CARD
# profile. `chart_card.render_card` rendered the FULL ledger page and shrank it to the dock's width, so every word
# shrank with the card (a 26 px tick read at 9 px on row 7's 653-px card). Under `readability: card` the page is laid
# out FOR THE CARD'S OWN DISPLAYED BOX (`axes.card_w` x `axes.card_h`, stage px) - drawn on the stage at the card's
# scale (CARD K = stage width / card width) so that, shown at the card's size, every size below is what it says:
#   CARD_TYPE_PX   every word (title, ticks, end badges, values, the source) at this many DISPLAYED px, the E99 s90
#                  phone floor at the card's size: 12 phone px on a 16:9 frame played 390 px wide is 12 x 1920 / 390 =
#                  59.08 stage px (test_longform_profile.PHONE_FLOOR / PHONE_W) - the floor itself (at 60 the title of
#                  row 7's card wraps by 4 px, and a second title line costs the plot a fifth of the card);
#   CARD_STROKE_X  every line and its tip at this many times the full page's own stroke, as displayed;
#   CARD_PAD_PX    the card's only margin (displayed px): the plot runs edge to edge inside it - no page margins, no
#                  caption bands, no sub, no y label, no badge rail, no key;
# end tags reduced to their short badge (the value, in its line's ink), the x ticks to the two ends (the minor ones
# dropped), the source to its first clause on one line - or none, when it will not fit, or when the plot would keep less
# than its room (the engine's LP_CARD.PLOT_MIN, or a line card's end badges stacked a line apart). The card keeps its
# TITLE and its NUMBER.
# It is the long form's look (the flat ground, the panel, Inter) - a card of a long-form page. NOT a row option: only
# `chart_card` sets it, and a row that names `readability=card` is refused as an unknown profile.
CARD = "card"
CARD_BUILDERS = ("dense-line", "story")
CARD_PHONE_FLOOR, CARD_PHONE_W = 12.0, 390   # E99 s90's floor, measured the T17 way (phone px = stage px x 390 / 1920)
CARD_TYPE_PX = CARD_PHONE_FLOOR * 1920 / CARD_PHONE_W   # 59.08: the floor itself (the engine's LP_CARD.TYPE_PX)
CARD_STROKE_X = 2.0
CARD_PAD_PX = 8.0   # the engine's LP_CARD.PAD_PX
CARD_SOURCE_CUTS = (" - ", "; ", ", ", " (")   # the source's first clause ends at the first of these
# THE NAMES A VALUE CANNOT CARRY (the parent's frame read of the first card, 2026-09-23: "+21%" grey and "+21%" blue
# "are indistinguishable except by colour - a viewer cannot tell the S&P from mega-cap"). On a card the end-tag
# shortening stops at the BADGE for every tag whose value another tag also shows: the value keeps the floor and a SHORT
# NAME rides it as the badge's chip - the series' own inline badge label (the page's key word for that line: E99 s90),
# cut to its first word when the first words still tell the lines apart. Never an invented word. The name's size is
# FITTED so the widest named tag takes at most CARD_TAG_ROOM of the card (the plot keeps the rest), never under
# CARD_NAME_MIN of the floor; a value no other tag shows names its line already (with its ink) and stays a value.
CARD_TAG_ROOM = 0.5
CARD_NAME_MIN = 0.5
CARD_TAG_EM = (0.68, 0.64)   # the engine's LP_LONGFORM.TAG_EM (NAME, CHIP): ems per character of a value / a chip
CARD_CHIP_DX_PX = 4.0        # the chip's gap after its value, displayed px (the engine's CHIP_DX_PX 12 at the card's ~3x)


def card_names(page: dict) -> dict[int, str]:
    """{series index: short name} for every live line whose end value another line's also shows. Pure."""
    live = [(i, s) for i, s in enumerate(page.get("series") or []) if isinstance(s, dict) and not s.get("muted")]
    vals = [str(s.get("label") or "").strip() for _i, s in live]
    dup = {v for v in vals if v and vals.count(v) > 1}
    if not dup:
        return {}
    by_col = {BADGE_ACCENT_COL.get(b.get("accent")): str(b.get("label") or "").strip()
              for b in page.get("badges") or [] if isinstance(b, dict) and b.get("inline")}
    full = {i: (by_col.get(s.get("color")) or str(s.get("name") or "").strip()) for i, s in live
            if str(s.get("label") or "").strip() in dup}
    out = {}
    for v in dup:
        group = {i: n for i, n in full.items() if str(page["series"][i].get("label") or "").strip() == v}
        first = {i: (n.split() or [""])[0] for i, n in group.items()}
        use = first if len(set(first.values())) == len(first) and all(first.values()) else group
        out.update(use)
    return {i: n for i, n in out.items() if n}


def card_chip_px(page: dict, names: dict[int, str], card_w: float) -> float:
    """The short names' size in DISPLAYED px: the floor, or less so the widest named tag fits CARD_TAG_ROOM of the
    card - never under CARD_NAME_MIN of the floor."""
    ev, ec = CARD_TAG_EM
    room = CARD_TAG_ROOM * float(card_w)
    fit = min((room - len(str(page["series"][i].get("label") or "")) * ev * CARD_TYPE_PX - CARD_CHIP_DX_PX) / (len(n) * ec)
              for i, n in names.items())
    return round(max(CARD_NAME_MIN * CARD_TYPE_PX, min(CARD_TYPE_PX, fit)), 2)


def card_floor_px(stage_w: int = 1920) -> float:
    """E99 s90's phone floor in DISPLAYED stage px: the size that reads 12 px on a 390-px-wide phone."""
    return CARD_PHONE_FLOOR * stage_w / CARD_PHONE_W


def card_error(page: dict, card_w: float, card_h: float, aspect: str | None = "16:9") -> str | None:
    """Can THIS page be drawn as a card of this displayed box? The message, or None. Pure."""
    builder = str(page.get("builder") or "?")
    if builder not in CARD_BUILDERS:
        return (f"readability={CARD!r} is drawn by the {' and '.join(CARD_BUILDERS)} builders (a line card and a bars "
                f"card); this page uses {builder!r}")
    if aspect not in (None, "16:9"):
        return f"readability={CARD!r} is a 16:9 page's card (the long form's); a {aspect} card keeps its own page"
    if not (float(card_w) > 0 and float(card_h) > 0):
        return f"readability={CARD!r} needs the card's displayed box in stage px (card_w, card_h); got {card_w!r} x {card_h!r}"
    return None


def card_source(source: str, card_w: float, stage_w: int = 1920) -> str:
    """The card's one short source line: the source's first clause, when it fits one line inside the card's margins at
    CARD_TYPE_PX - else nothing (the page the card becomes carries the whole citation)."""
    text = str(source or "").strip()
    for cut in CARD_SOURCE_CUTS:
        if cut in text:
            text = text.split(cut, 1)[0].strip()
    k = stage_w / float(card_w)
    room = stage_w - 2 * CARD_PAD_PX * k
    return text if text and longform_text_px(text, "source", CARD_TYPE_PX * k) <= room else ""


def apply_card(page: dict, card_w: float, card_h: float, stage_w: int = 1920) -> dict:
    """Stamp the CARD profile on a page spec, in place (returned for chaining): the displayed box, the value-only end
    tags, the two end x ticks, no sub / y label / badges / key, the short source. ValueError when it cannot be one."""
    err = card_error(page, card_w, card_h)
    if err:
        raise ValueError(err)
    axes = page.setdefault("axes", {})
    for key in ("type_scale", "tag_form", "tag_room", "key", "key_px", "ylabel", "card_chip_px"):
        axes.pop(key, None)
    axes.update({"readability": CARD, "card_w": round(float(card_w), 2), "card_h": round(float(card_h), 2)})
    names = card_names(page) if page.get("builder") == "dense-line" else {}   # read before the badges are cleared
    if page.get("builder") == "dense-line":
        axes["tag_form"] = "value"
    if names:   # the shortening stops at the badge: the value and its short name
        axes["tag_form"] = "badge"
        axes["card_chip_px"] = card_chip_px(page, names, card_w)
        for i, n in names.items():
            page["series"][i]["card_name"] = n
    xt = axes.get("xticks")
    if isinstance(xt, list) and len(xt) > 2:
        axes["xticks"] = [xt[0], xt[-1]]
    page["sub"] = ""
    page["badges"] = []
    page["source"] = card_source(page.get("source") or "", card_w, stage_w)
    return page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="series.json -> ledger page spec (doc 29 s9.26)")
    parser.add_argument("series", help="the ev-*.series.json beside the asset")
    parser.add_argument("--variant", default=None, choices=VARIANTS)   # `share` is the donut exception; see SHARE_BOUNDS
    parser.add_argument("--check", action="store_true",
                        help="validate only - nothing is written, and the variant may be left to the file's own shape")
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
    variant = args.variant or infer_variant(series)
    if variant is None:
        print(f"ledger_page: {path}: name the variant (--variant {'|'.join(VARIANTS)}) - "
              "this file's shape does not name one on its own", file=sys.stderr)
        return EXIT_INVALID
    errors = validate(series, variant)
    if errors:
        print(f"ledger_page: {path} is not a page ({variant}):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return EXIT_INVALID
    spec = build_spec(series, variant, args.emphasize, args.quiet_zone)
    for note in spec.get("judge", []):
        print(f"  [JUDGE] {note}")
    for warning in spec.get("warnings", []):
        print(f"  [WARN] {warning}")
    if args.check:   # a check writes nothing: it says what the file IS a page of, and what the page will carry
        extra = (f" {len(spec['tiers'])} tiers sharing x" if spec["builder"] == "tiers" else
                 f" {len(spec['labels'])} cells, {spec['layout']['16:9']['unnamed']} unnamed (16:9)" if spec["builder"] == "treemap" else
                 f" {len(spec['labels'])} values")
        print(f"OK {path.name}: {spec['builder']} {variant}{extra} source={spec['source']!r}")
        return 0
    stem = path.name[: -len(".series.json")] if path.name.endswith(".series.json") else path.stem
    out = Path(args.out) if args.out else path.with_name(f"{stem}.page.json")
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    count = (sum(len(_points(s)) for s in spec.get("series", []))
             + sum(len(v) if isinstance(v, list) else 1 for v in spec["values"]))
    print(f"{spec['builder']} {spec['variant']} {count} values source={spec['source']!r} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

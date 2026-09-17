"""ONE-SHOT FLOOR GATE - the floors E96 ruled, measured on a COMPILED timeline (P56 T6).

The operator, 2026-09-13 (E96), on the thin one-shot: *"there was minimal motion/transformation, and mixing of
narrative panels and charts. You mostly changed words and used only 2 charts."* It was offered for a watch at 0 FAIL
/ 1 WARN because no gate measured the WHOLE cut: the motion gate counts events per window and the thin cut ran 17.9
events/min - as busy as Tokyo. So the floors are not a rate. They are whole-cut aggregates, and this gate is where
they live:

    python content/video_engine/scripts/gate_one_shot_floor.py <build-dir> [--project <dir>]
                        [--reference <build-dir>] [--catalog docs/EFFECTS-CATALOG.jsonl] [--timeline <name>]

  M35  distinct chart forms >= 3                            FAIL / PASS  (INFO on a PREDATES_E96 build)
  M36  chart-to-chart transforms >= 1                       FAIL / PASS  (INFO on a PREDATES_E96 build)
  M37  docks on >= max(1/3, the reference's own) of beats    FAIL / PASS  (HG1: the ON-SCREEN reading)
  M38  proven-recipe coverage >= 0.60 of beats              FAIL / PASS  (both readings printed; the floor spans)
  M39  narrative : chart >= max(1.0, the reference's own)    FAIL / PASS
       M37-M39 print WARN instead of PASS when the reference is not readable: the run goes on, the floor held at the
       rule's own number (the P56 review - a missing or unreadable reference used to kill the whole gate)
  M40  parity with the best approved short + Bravos          JUDGE        (never FAIL - E96)
  M41  the beat plan covers every beat                      FAIL / PASS  (WARN when there is no plan on disk)
  M42  events/min, compositions/min, builds:compositions    INFO         (never a floor - E96 (3))
  M45  parity by MECHANISM, read against the beat plan       FAIL / WARN / PASS  (INFO with no plan on disk)
  M46  the signature mix beside the approved cuts' own       WARN / PASS  (variety never FAILs - E96)

The catalogue M38 reads is BUILD OUTPUT (P63): `run` ensures `docs/EFFECTS-CATALOG.jsonl` (by the digest of the
cards, the recipes and the modules behind them) before it reads it, so a recipe added since the last build is in
the coverage. A `--catalog` that is not this repository's own artifact is read exactly as given, never rebuilt.

HOW IT MEASURES (definitions from `scene_evidence_timeline.v1`, identical to T2's `derive_seeds.py`, so the numbers
in `docs/research/runs/p56-recipe-seeds/measures.md` are reproduced by this tool):

  a BEAT          one `sentences[]` window of the build's `timeline.json` (`lint_species_choice.load_sentences`);
                  `narration.words_path` resolved against the PROJECT dir is the fallback when the build holds none.
  a CHART FORM    a ledger page's `(world.page.builder, world.page.variant)` pair, plus each chart dock's own
                  `evidence[slide].chart` discriminator (series / bars / shares / checklist / panels).
  a CHART-TO-CHART TRANSFORM   a `species[].kind == "chart_to"` (any verb), OR a ledger page whose `page.enter` is
                  `morph` or `stamped` AND whose PREVIOUS scene's world is also a ledger page. NOT counted:
                  `enter: snap` with a `snap_from` naming a dock (that is the card->chart hand-off, Japan's two),
                  `spiral`, `mount`, `axes`.
  a beat CARRIES A DOCK        a dock's `[enter, exit]` intersects the beat, CLOSED at both ends (HG1's on-screen
                  reading: a held dock is Bravos' "builds inside a held frame"). The enters-during reading is
                  printed beside it, never gated on.
  a beat CARRIES A RECIPE      a `proven` recipe of `docs/EFFECTS-CATALOG.jsonl` fires (its ordered members all
                  inside its `window_s` - `recipe_walk.match` over `recipe_walk.events`, a `recipe:` member spliced
                  from the catalogue's own registry) with the fire's [first member, last member] span overlapping the
                  beat. M38 also prints the STRICTER reading beside it - the share of beats a fire STARTS in - so the
                  operator sees both at HG2; the floor stays on the spanning number (HG1/HG2 as ruled).
  NARRATIVE : CHART            (plate scenes + clip scenes) / (ledger pages + chart docks), a chart dock being a
                  dock whose `evidence[slide].species` is a chart surface (`recipe_walk.CHART_SPECIES`).
  an EVENT        a cut + a build, Bravos' own definitions: a composition is a scene whose world SIGNATURE differs
                  from the previous scene's; a build is a dock enter, a badge (dock or page), or a species start.

HG1's four exempt cuts are pinned by (project, build) AND by the sha256 of the compiled timeline (the P56 review):
the exemption is the operator's ruling about those BYTES, so re-authoring a cut in the same directory ends it.

HG1 ANSWERED 2026-09-13, recommendation (A): the floors bind on everything authored from now on and the four cuts on
disk are NOT re-judged - on them the two never-shipped rows (M35, M36) print `INFO ... predates E96` with the
measured number. M37-M39 still PASS/FAIL there (the thin one-shot FAILs two of them). The parity floors are
additionally held to the reference's OWN numbers, measured at RUN TIME from its timeline with these same functions
(`thresholds-from-the-reference`) - never a hard-coded number. Bravos' numbers are the one QUOTED column.

The rows are the `[LEVEL] id text` protocol of `gate_motion_density.py`; `self_watch.py` runs this as a subprocess
and parses them (T7). Stdlib only; nothing here writes, renders or re-authors anything.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, NamedTuple, Sequence

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import docs_layers as DL  # noqa: E402  (the catalogue is build output; this gate ensures it, P63 T2)
import lint_species_choice as LSC  # noqa: E402  (`load_sentences` - the sentence shape lives once, there)
import recipe_walk as RW  # noqa: E402  (the walk and the co-occurrence matcher live once, there)
import derive_approved_mix as MIX  # noqa: E402  (M46's classifier is the DERIVER's own - P66 T2, never a second one)

CATALOG_REL = "docs/EFFECTS-CATALOG.jsonl"
CATALOG_LAYER = "effects-catalog"      # docs_layers' name for the builder that writes CATALOG_REL
PROJECTS_REL = "content/video_engine/projects/systems-and-blowups"
REFERENCE_REL = f"{PROJECTS_REL}/japan-tariff-trick/build-short"   # the best approved short (09-09), the reference
BEAT_PLAN_NAME = "BEAT-PLAN.jsonl"
WORDS_NAME = "timeline.json"

MIN_FORMS = 3                  # E96: at least three distinct chart forms in one cut
MIN_CHART_TO = 1               # E96: at least one chart-to-chart transform
MIN_DOCKS_PER_BEAT = 1 / 3     # E96: docks on at least a third of the beats
MIN_RECIPE_COVERAGE = 0.60     # E96 + HG1: kept as the new reference's target, Japan's own printed beside it
M38_INTERIM_WARN = True        # R26-168 - the fifteen proven recipes are being re-proved on today's clocks
                               # by the recipe lab, P65 HG2 flips this back to False
MIN_NARR_CHART = 1.0           # E96: the narrative surfaces at least match the chart surfaces
EPS = 0.005                    # the closed-interval slack
BEAT_T_TOL = 0.05              # how near a beat's start a beat-plan record's `t0` must sit to BE that beat

# HG1 (A), answered by the operator 2026-09-13: the four cuts on disk predate E96 and are never re-judged.
# ADDING A BUILD TO THIS TABLE NEEDS A RULING - it is an exemption from the floors, not a configuration knob.
# {(project, build): the sha256 of that build's compiled timeline, computed 2026-09-13}. The pair alone was a NAME:
# a re-authored timeline in the same directory inherited the exemption. The sha ties it to the bytes the ruling was
# about - re-author the cut and it is judged by the floors like anything else.
PREDATES_E96 = {
    ("japan-tariff-trick", "build-short"): "dbac920575b5f151907f441f47f93681324a0ed603d5f8122f0ad5475aadfd41",
    ("tokyo-tea-break", "build-short.v2"): "fe3569ee7e99d912a1d136f055ec8581c3bfbad091219d8b02ba698df397ada5",
    ("steel-and-paper", "build-f"): "0a9ba6d8bcc66365ec02d11c9d25d7abbe263465331f8c4d779f4d6d10b56492",
    ("normal-for-which-bridge", "review-v1"): "a0d4c505a26ce49a12220af9e4ccdc66614cb9ea669706b3ad2f26567ae802d9",
}

# The one QUOTED column (never measured here): `docs/agent-memory/operator/bravos-reference.md` carries 6.0
# events/min and 2.5 compositions/min verbatim; the forms and the card count come from the dossier that memory
# names, as quoted by T2 (`docs/research/runs/p56-recipe-seeds/measures.md` s1).
BRAVOS = {"events_min": "6.0", "comps_min": "2.5", "builds_per_comp": "1.40", "forms": "~6",
          "chart_to": "-", "docks_beat": "-", "coverage": "-",
          "narr_chart": "0.16 (own-stage/external mix)"}
BRAVOS_SRC = ("docs/agent-memory/operator/bravos-reference.md (6.0 events/min, 2.5 compositions/min); ~6 forms + 50 "
              "press/TV cards via docs/research/runs/p56-recipe-seeds/measures.md s1")

SRC_M35 = "E96 (2026-09-13): a cut carries at least 3 DISTINCT chart forms - the thin one-shot shipped 1 (\"you mostly changed words and used only 2 charts\"); a form is a ledger page's (builder, variant) or a chart dock's own discriminator"
SRC_M36 = "E96: at least 1 chart-to-chart TRANSFORM - a chart changes state instead of being replaced (E50, E45); a snap from a dock is a card-to-chart hand-off, not a transform"
SRC_M37 = "E96 + P56 HG1 (A): docks on at least 1/3 of the beats, ON SCREEN (a dock's [enter, exit] intersects the beat) and never under the reference's own share - Bravos' lesson is builds inside a HELD frame (bravos-reference)"
SRC_M38 = "E96: a beat is a RECIPE - at least 0.60 of the beats carry a proven combination from docs/EFFECTS-CATALOG.jsonl; HG1 keeps 0.60 as the new reference's target with the reference's own coverage printed beside it; INTERIM (R26-168, P65 T7): while the proven set is re-proved on today's clocks by the recipe lab this row WARNs instead of FAILing below 0.60 - it does not stop a cut until P65 HG2 restores the floor, and M45 (parity by mechanism) is the floor meanwhile"
SRC_M39 = "E96: narrative : chart at least 1:1 - \"mixing of narrative panels and charts\"; held to the reference's own ratio too (thresholds-from-the-reference)"
SRC_M40 = "E96: JUDGE keeps sequence and taste, read against the best approved short, never against the gates - the reference measured at run time, Bravos quoted"
SRC_M41 = "P56 (E96): the comparator + capability + recipe plan per beat is written BEFORE the rows; a beat with no record, an empty comparator.compared_to, or a null recipe with no why_none is a gap"
SRC_M45 = "E99 s67 Apply 7 + R26-177: the cut is read MECHANISM by mechanism against its OWN beat plan (the list of 2026-09-16, docs/content-video-engine/CRITIC-REPORT.md) - present / absent / replaced by <mechanism> / not owed; a mechanism is owed only where a beat's shape calls for it, and an absence with nothing in its place is the E99 s67 regression"
SRC_M46 = "P66 T2 + E96: the cut's signature mix beside the approved shorts' MEASURED mix (effects/skeletons/approved-mix.json) - no signature over 0.34 of the scenes and no two consecutive scenes on a signature the approved cuts do not themselves repeat; variety is JUDGE-adjacent and never FAILs"
SRC_M42 = "E96 (3): events per minute is NOT a floor - the thin cut would have passed it (17.9/min, as busy as Tokyo's 18.2); it is reported beside compositions/min and builds:compositions and can never FAIL"

ROW_ORDER = ("M35", "M36", "M37", "M38", "M39", "M40", "M41", "M42", "M45", "M46")


@dataclass(frozen=True)
class Gate:
    """One printed row: the id, the level, the measured message, the rule it enforces."""
    id: str
    level: str
    message: str
    src: str


@dataclass
class Measures:
    """Every number the rows read, measured from ONE build - the same functions on the cut and on the reference."""
    build: Path
    timeline_path: Path
    beats_path: Path
    runtime_s: float
    beats: list = field(default_factory=list)
    forms: dict = field(default_factory=dict)
    chart_to: list = field(default_factory=list)
    docks: list = field(default_factory=list)
    dock_beats: int = 0
    enter_beats: int = 0
    pages: int = 0
    plates: int = 0
    clips: int = 0
    chart_docks: int = 0
    fires: dict = field(default_factory=dict)
    recipe_beats: set = field(default_factory=set)          # a fire SPANS the beat (HG1's reading - the floor)
    recipe_start_beats: set = field(default_factory=set)    # a fire STARTS in the beat (the stricter reading)
    compositions: int = 0
    builds: int = 0
    ref_warn: str | None = None                             # the reference this run could not read, if any
    layers_note: str | None = None                          # the catalogue's staleness, for the header (P64 T1)

    @property
    def name(self) -> str:
        return "/".join(self.build.resolve().parts[-2:])

    @property
    def n_beats(self) -> int:
        return len(self.beats)

    @property
    def n_forms(self) -> int:
        return len(self.forms)

    @property
    def docks_per_beat(self) -> float:
        return round(self.dock_beats / self.n_beats, 2) if self.n_beats else 0.0

    @property
    def enters_per_beat(self) -> float:
        return round(self.enter_beats / self.n_beats, 2) if self.n_beats else 0.0

    @property
    def coverage(self) -> float:
        return round(len(self.recipe_beats) / self.n_beats, 2) if self.n_beats else 0.0

    @property
    def coverage_start(self) -> float:
        """The share of beats a fire STARTS in - printed beside `coverage`, never the floor (HG1/HG2 as ruled)."""
        return round(len(self.recipe_start_beats) / self.n_beats, 2) if self.n_beats else 0.0

    @property
    def narrative(self) -> int:
        return self.plates + self.clips

    @property
    def chart_surfaces(self) -> int:
        return self.pages + self.chart_docks

    @property
    def narr_chart(self) -> float:
        return round(self.narrative / self.chart_surfaces, 2) if self.chart_surfaces else 0.0

    @property
    def events(self) -> int:
        return self.compositions + self.builds

    @property
    def minutes(self) -> float:
        return self.runtime_s / 60.0 if self.runtime_s else 0.0

    @property
    def events_min(self) -> float:
        return round(self.events / self.minutes, 1) if self.minutes else 0.0

    @property
    def comps_min(self) -> float:
        return round(self.compositions / self.minutes, 2) if self.minutes else 0.0

    @property
    def builds_per_comp(self) -> float:
        return round(self.builds / self.compositions, 2) if self.compositions else 0.0


# --------------------------------------------------------------------------- the inputs

def timeline_path(build: Path, name: str | None = None) -> Path:
    """The compiled `*.timeline.json` of a build dir (`--timeline` names one when a build holds two)."""
    path = build / name if name else next(iter(sorted(p for p in build.glob("*.timeline.json")
                                                      if p.name != WORDS_NAME)), None)
    if not path or not path.is_file():
        raise SystemExit(f"no *.timeline.json in {build}")
    return path


def beats_path(build: Path, timeline: Mapping[str, Any], project: Path | None = None) -> Path:
    """The words timeline the beats come from: the build's own `timeline.json`, else `narration.words_path`.

    `lint_species_choice.resolve_inputs` is NOT used: it also demands the project's `SHOT-TABLE-SHORT.py`, which a
    long form (steel-and-paper/build-f) does not have, and it resolves `--build` under the project rather than from
    the compiled timeline's own pointer. That pointer is stale on two of the four cuts on disk (tokyo's
    build-short.v2 says `build-short/timeline.json`), so the build's own file is read first.
    """
    own = build / WORDS_NAME
    if own.is_file():
        return own
    rel = ((timeline.get("narration") or {}).get("words_path") or "").replace("\\", "/")
    named = (project or build.parent) / rel if rel else None
    if named and named.is_file():
        return named
    raise SystemExit(f"no {WORDS_NAME} in {build} and no readable narration.words_path ({rel or 'absent'})")


def load_recipes(catalog: Path) -> list:
    """The `proven` recipe records of the generated effects catalogue, in id order (`axis == "recipe"`)."""
    if not catalog.is_file():
        return []
    out = []
    for line in catalog.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("axis") == "recipe" and record.get("status") == "proven":
            out.append(record)
    return sorted(out, key=lambda r: str(r.get("id")))


def recipe_registry(catalog: Path) -> dict:
    """{recipe id -> record} for EVERY recipe in the catalogue (proven or candidate): what a `recipe:` member names.

    `load_recipes` returns the proven ones the floor measures; a proven recipe may still name a candidate child, so
    the splice registry is the whole set (`recipe_walk.flatten`)."""
    if not catalog.is_file():
        return {}
    out: dict = {}
    for line in catalog.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("axis") == "recipe" and record.get("id"):
            out[str(record["id"])] = record
    return out


def card_options(catalog: Path) -> dict:
    """{option token -> its card}, so a scene `exit: wipe_right` resolves to `exit:wipe` plus the option."""
    if not catalog.is_file():
        return {}
    cards = [json.loads(l) for l in catalog.read_text(encoding="utf-8").splitlines() if l.strip()]
    return RW.option_owner([c for c in cards if c.get("axis") != "recipe"])


# --------------------------------------------------------------------------- the measures

def form_labels(timeline: Mapping[str, Any]) -> dict:
    """{form label -> how many surfaces carry it}: a page's `builder/variant` pair, a chart dock's discriminator."""
    evidence = timeline.get("evidence") or {}
    counts: collections.Counter = collections.Counter()
    for scene in timeline.get("scenes") or []:
        page = (scene.get("world") or {}).get("page")
        if page:
            counts[f"{page.get('builder')}/{page.get('variant')}"] += 1
        for dock in scene.get("docks") or []:
            form = RW.chart_form(evidence.get(dock.get("slide")) or {})
            if form:
                counts[form] += 1
    return dict(sorted(counts.items()))


def chart_to_transforms(timeline: Mapping[str, Any]) -> list:
    """Every chart-to-chart transform: a `chart_to` species, or a morph/stamped page ON another page."""
    scenes = list(timeline.get("scenes") or [])
    out: list = []
    for i, scene in enumerate(scenes):
        sid = str(scene.get("scene_id") or i)
        for sp in scene.get("species") or []:
            if sp.get("kind") == "chart_to":
                out.append((sid, f"species chart_to -> {sp.get('to') or '?'}"))
        page = (scene.get("world") or {}).get("page") or {}
        if page.get("enter") in ("morph", "stamped") and i > 0 and ((scenes[i - 1].get("world") or {}).get("page")):
            out.append((sid, f"page enter {page['enter']} after a ledger page"))
    return out


def dock_rows(timeline: Mapping[str, Any]) -> list:
    """Every dock with the window it is ON SCREEN and whether its payload is a chart surface.

    A partial timeline is read with the schema's own defaults (`recipe_walk`'s reads): a dock that states no window
    is on screen for its whole scene, a scene with no span sits at 0."""
    evidence = timeline.get("evidence") or {}
    out: list = []
    for i, scene in enumerate(timeline.get("scenes") or []):
        span = list(scene.get("span") or [0.0, 0.0])
        start = float(span[0] if span else 0.0)
        end = float(span[1] if len(span) > 1 else start)
        for dock in scene.get("docks") or []:
            block = evidence.get(dock.get("slide")) or {}
            out.append({"scene": str(scene.get("scene_id") or i), "slide": dock.get("slide"),
                        "enter": float(start if dock.get("enter") is None else dock["enter"]),
                        "exit": float(end if dock.get("exit") is None else dock["exit"]),
                        "chart": block.get("species") in RW.CHART_SPECIES})
    return out


def overlaps(beat: Mapping[str, Any], t0: float, t1: float) -> bool:
    """A window intersects a beat, CLOSED at both ends (a dock landing on a boundary is carried by both beats)."""
    return t0 <= float(beat["end"]) + EPS and t1 >= float(beat["start"]) - EPS


def beats_with_dock(docks: Sequence[Mapping[str, Any]], beats: Sequence[Mapping[str, Any]]) -> tuple:
    """(beats a dock is on screen during, beats a dock ENTERS during) - the gate reads the first (HG1)."""
    on = sum(1 for b in beats if any(overlaps(b, d["enter"], d["exit"]) for d in docks))
    enters = sum(1 for b in beats if any(overlaps(b, d["enter"], d["enter"]) for d in docks))
    return on, enters


def recipe_fires(events: Sequence, recipes: Iterable[Mapping[str, Any]], registry: Mapping | None = None) -> dict:
    """{recipe id -> its fires in this cut}, empty entries dropped: what the ordered members actually did here.

    `registry` is the catalogue's {id: recipe}: a member naming another recipe is spliced before the walk."""
    out: dict = {}
    for recipe in recipes:
        members = recipe.get("members") or []
        if len(members) < 2:
            continue
        fires = RW.match(events, members, float(recipe.get("window_s") or RW.DEFAULT_WINDOW_S), recipes=registry)
        if fires:
            out[str(recipe.get("id"))] = fires
    return out


def beats_with_recipe(fires: Mapping[str, list], beats: Sequence[Mapping[str, Any]]) -> set:
    """The indices of every beat a proven recipe's fire overlaps (a fire spans its first to its last member)."""
    covered: set = set()
    for instances in fires.values():
        for fire in instances:
            for i, beat in enumerate(beats):
                if overlaps(beat, fire.t, fire.t_end):
                    covered.add(i)
    return covered


def beats_a_recipe_starts_in(fires: Mapping[str, list], beats: Sequence[Mapping[str, Any]]) -> set:
    """The indices of every beat a fire OPENS in - the stricter reading, printed beside the floor's own (M38)."""
    covered: set = set()
    for instances in fires.values():
        for fire in instances:
            for i, beat in enumerate(beats):
                if overlaps(beat, fire.t, fire.t):
                    covered.add(i)
    return covered


def walk_counts(events: Sequence) -> tuple:
    """(compositions, builds) from the walk: a cut is a composition; a dock enter, a badge or a species is a build.

    A dock enter emits one event per CARD it performs, so the docks are counted through their exits - exactly one
    per dock - which is what reproduces T2's 28 / 19 / 124 / 11 builds on the four cuts.
    """
    compositions = sum(1 for e in events if e.cls == "cut")
    builds = sum(1 for e in events if e.cls in ("dock_exit", "badge", "species", "page_species"))
    return compositions, builds


def measure(build: Path, project: Path | None = None, recipes: Sequence[Mapping[str, Any]] = (),
            options: Mapping[str, str] | None = None, timeline_name: str | None = None,
            registry: Mapping | None = None) -> Measures:
    """Every floor number of one build, from its compiled timeline and its own beats."""
    build = Path(build)
    tl_path = timeline_path(build, timeline_name)
    timeline = json.loads(tl_path.read_text(encoding="utf-8"))
    words = beats_path(build, timeline, project)
    beats = LSC.load_sentences(words)
    scenes = list(timeline.get("scenes") or [])
    docks = dock_rows(timeline)
    events = RW.events(timeline, options or {})
    on, enters = beats_with_dock(docks, beats)
    fires = recipe_fires(events, recipes, registry)
    compositions, builds = walk_counts(events)
    return Measures(
        build=build, timeline_path=tl_path, beats_path=words, runtime_s=float(timeline.get("runtime_s") or 0.0),
        beats=beats, forms=form_labels(timeline), chart_to=chart_to_transforms(timeline), docks=docks,
        dock_beats=on, enter_beats=enters,
        pages=sum(1 for s in scenes if (s.get("world") or {}).get("page")),
        plates=sum(1 for s in scenes if not (s.get("world") or {}).get("page")
                   and (s.get("world") or {}).get("kind") != "clip"),
        clips=sum(1 for s in scenes if not (s.get("world") or {}).get("page")
                  and (s.get("world") or {}).get("kind") == "clip"),
        chart_docks=sum(1 for d in docks if d["chart"]),
        fires=fires, recipe_beats=beats_with_recipe(fires, beats),
        recipe_start_beats=beats_a_recipe_starts_in(fires, beats),
        compositions=compositions, builds=builds)


def predates_e96(build: Path, timeline: Path | None = None) -> bool:
    """True for the four cuts HG1 (A) enumerates: the (project, build) pair AND the sha256 of the compiled timeline.

    A build whose timeline is absent, unreadable or re-authored is NOT exempt - it is judged by the floors.
    """
    said = PREDATES_E96.get(tuple(Path(build).resolve().parts[-2:]))
    if not said:
        return False
    try:
        path = Path(timeline) if timeline is not None else timeline_path(Path(build))
        return hashlib.sha256(path.read_bytes()).hexdigest() == said
    except (SystemExit, OSError):
        return False


# --------------------------------------------------------------------------- the beat plan (M41)

def beat_plan(build: Path) -> list | None:
    """`<build>/BEAT-PLAN.jsonl` as records, or None when there is no plan on disk (a predating build has none)."""
    path = Path(build) / BEAT_PLAN_NAME
    if not path.is_file():
        return None
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def plan_gaps(records: Sequence[Mapping[str, Any]], beats: Sequence[Mapping[str, Any]]) -> list:
    """Every gap, named: a beat with no record, an empty `comparator.compared_to`, a null recipe with no why_none.

    A record is matched to a beat by its `t0` landing on that beat's own start (+- BEAT_T_TOL) - the unambiguous
    anchor - and only then by its `beat` number read 1-based, so a plan numbered from either end is read the same.
    """
    by_beat: dict = {}
    for record in records:
        index = next((i for i, b in enumerate(beats)
                      if record.get("t0") is not None
                      and abs(float(record["t0"]) - float(b["start"])) <= BEAT_T_TOL), None)
        if index is None:
            number = record.get("beat")
            index = int(number) - 1 if isinstance(number, (int, float)) else None
            if index is not None and not 0 <= index < len(beats):
                index = None
        if index is not None:
            by_beat.setdefault(index, record)
    gaps: list = []
    for i in range(len(beats)):
        record = by_beat.get(i)
        if record is None:
            gaps.append(f"beat {i + 1} has no record")
            continue
        comparator = record.get("comparator") or {}
        if not str(comparator.get("compared_to") or "").strip():
            gaps.append(f"beat {i + 1} compares to nothing")
        if not record.get("recipe") and not str(record.get("why_none") or "").strip():
            gaps.append(f"beat {i + 1} has no recipe and no why_none")
    return gaps


# --------------------------------------------------------------------------- the rows

def _forms_text(m: Measures) -> str:
    return ", ".join(f"{k}·{v}" for k, v in m.forms.items()) or "none"


def row_m35(m: Measures, predates: bool) -> Gate:
    text = f"{m.n_forms} chart forms ({_forms_text(m)}) on {m.chart_surfaces} chart surfaces"
    if predates:
        return Gate("M35", "INFO", f"{text} - predates E96 (measured {m.n_forms}), not re-judged", SRC_M35)
    ok = m.n_forms >= MIN_FORMS
    return Gate("M35", "PASS" if ok else "FAIL", f"{text} - the floor is {MIN_FORMS} distinct forms", SRC_M35)


def row_m36(m: Measures, predates: bool) -> Gate:
    named = "; ".join(f"{sid}: {what}" for sid, what in m.chart_to) or "none"
    text = f"{len(m.chart_to)} chart-to-chart transforms ({named})"
    if predates:
        return Gate("M36", "INFO", f"{text} - predates E96 (measured {len(m.chart_to)}), not re-judged", SRC_M36)
    ok = len(m.chart_to) >= MIN_CHART_TO
    return Gate("M36", "PASS" if ok else "FAIL",
                f"{text} - the floor is {MIN_CHART_TO} (a chart changes state; a snap from a dock is not one)",
                SRC_M36)


def _ref_text(warn: str | None, absent: str) -> str:
    """What a reference-dependent row says about the reference: its measure, this WARN, or plainly absent."""
    return f"reference {warn} not readable - floor held at the rule's own number" if warn else absent


def row_m37(m: Measures, ref: Measures | None, warn: str | None = None) -> Gate:
    floor = max(MIN_DOCKS_PER_BEAT, ref.docks_per_beat if ref else 0.0)
    ok = m.docks_per_beat + EPS >= floor
    ref_text = (f"the reference {ref.name} measures {ref.docks_per_beat:.2f}" if ref
                else _ref_text(warn, "the reference is not on disk - only E96's 1/3 binds"))
    return Gate("M37", "FAIL" if not ok else "WARN" if warn else "PASS",
                f"docks on {m.docks_per_beat:.2f} of {m.n_beats} beats ({m.dock_beats} on screen, "
                f"{m.enter_beats} entering) - the floor is {floor:.2f} = max(1/3, the reference's own); {ref_text}",
                SRC_M37)


def _recipe_text(m: Measures) -> str:
    if not m.fires:
        return "no proven recipe fires"
    parts = []
    for rid in sorted(m.fires, key=lambda r: (-len(m.fires[r]), r)):
        n = len(m.fires[rid])
        parts.append(f"{rid} x{n}" + (" (a decoration)" if n == 1 else ""))
    return ", ".join(parts)


def row_m38(m: Measures, ref: Measures | None, warn: str | None = None) -> Gate:
    """Both readings in the one row: the floor is the SPANNING share, the beat a fire starts in prints beside it."""
    ok = m.coverage + EPS >= MIN_RECIPE_COVERAGE
    ref_text = (f"the reference {ref.name} measures {ref.coverage:.2f}" if ref
                else _ref_text(warn, "the reference is not on disk"))
    interim = "" if ok or not M38_INTERIM_WARN else (
        " - interim (R26-168): the proven set is being re-proved on today's clocks by the recipe lab; "
        "this row does not stop a cut until P65 HG2, and M45 (parity by mechanism) is the floor meanwhile")
    return Gate("M38", "PASS" if ok and not warn else "WARN" if ok or M38_INTERIM_WARN else "FAIL",
                f"proven-recipe coverage {m.coverage:.2f} spanning / {m.coverage_start:.2f} by the beat a fire "
                f"starts in, of {m.n_beats} beats ({len(m.recipe_beats)} carry a recipe, "
                f"{len(m.recipe_start_beats)} open one) - the floor is {MIN_RECIPE_COVERAGE:.2f} on the spanning "
                f"number; {ref_text} - {_recipe_text(m)}{interim}", SRC_M38)


def row_m39(m: Measures, ref: Measures | None, warn: str | None = None) -> Gate:
    floor = max(MIN_NARR_CHART, ref.narr_chart if ref else 0.0)
    ok = m.narr_chart + EPS >= floor
    ref_text = (f"the reference {ref.name} measures {ref.narr_chart:.2f}" if ref
                else _ref_text(warn, "the reference is not on disk - only E96's 1:1 binds"))
    return Gate("M39", "FAIL" if not ok else "WARN" if warn else "PASS",
                f"narrative : chart {m.narr_chart:.2f} ({m.narrative} narrative = {m.plates} plates + {m.clips} "
                f"clips / {m.chart_surfaces} chart = {m.pages} pages + {m.chart_docks} chart docks) - the floor is "
                f"{floor:.2f} = max(1.0, the reference's own); {ref_text}", SRC_M39)


def _parity_rows(m: Measures, ref: Measures | None) -> list:
    fmt = lambda fn, spec: (spec % fn(ref)) if ref else "-"
    return [("distinct chart forms", str(m.n_forms), fmt(lambda x: x.n_forms, "%d"), BRAVOS["forms"]),
            ("chart-to-chart transforms", str(len(m.chart_to)), fmt(lambda x: len(x.chart_to), "%d"),
             BRAVOS["chart_to"]),
            ("docks / beat (on screen)", f"{m.docks_per_beat:.2f}", fmt(lambda x: x.docks_per_beat, "%.2f"),
             BRAVOS["docks_beat"]),
            ("proven-recipe coverage", f"{m.coverage:.2f}", fmt(lambda x: x.coverage, "%.2f"), BRAVOS["coverage"]),
            ("narrative : chart", f"{m.narr_chart:.2f}", fmt(lambda x: x.narr_chart, "%.2f"), BRAVOS["narr_chart"]),
            ("events / min", f"{m.events_min:.1f}", fmt(lambda x: x.events_min, "%.1f"), BRAVOS["events_min"]),
            ("compositions / min", f"{m.comps_min:.2f}", fmt(lambda x: x.comps_min, "%.2f"), BRAVOS["comps_min"]),
            ("builds : compositions", f"{m.builds_per_comp:.2f}", fmt(lambda x: x.builds_per_comp, "%.2f"),
             BRAVOS["builds_per_comp"])]


def row_m40(m: Measures, ref: Measures | None) -> Gate:
    head = (f"parity: this cut | {ref.name} measured at run time | Bravos quoted" if ref
            else "parity: this cut | the reference is NOT on disk | Bravos quoted")
    table = _parity_rows(m, ref)
    width = max(len(row[0]) for row in table)
    body = "\n".join(f"          | {name:<{width}} | {mine:>9} | {theirs:>9} | {bravos}"
                     for name, mine, theirs, bravos in table)
    return Gate("M40", "JUDGE", f"{head}\n{body}\n          Bravos source: {BRAVOS_SRC}", SRC_M40)


def row_m41(m: Measures) -> Gate:
    records = beat_plan(m.build)
    if records is None:
        return Gate("M41", "WARN", f"no beat plan on disk ({BEAT_PLAN_NAME} absent in {m.build.name}) - "
                                   f"{m.n_beats} beats unplanned", SRC_M41)
    gaps = plan_gaps(records, m.beats)
    if gaps:
        shown = "; ".join(gaps[:12]) + (f"; +{len(gaps) - 12} more" if len(gaps) > 12 else "")
        return Gate("M41", "FAIL", f"the beat plan has {len(gaps)} gaps over {m.n_beats} beats "
                                   f"({len(records)} records): {shown}", SRC_M41)
    return Gate("M41", "PASS", f"the beat plan covers all {m.n_beats} beats ({len(records)} records), each with a "
                               f"comparator and a recipe or a why_none", SRC_M41)


def row_m42(m: Measures) -> Gate:
    return Gate("M42", "INFO",
                f"{m.events_min:.1f} events/min ({m.events} = {m.compositions} compositions + {m.builds} builds "
                f"over {m.runtime_s:.2f} s), {m.comps_min:.2f} compositions/min, "
                f"builds:compositions {m.builds_per_comp:.2f} - reported, never a floor", SRC_M42)


# --------------------------------------------------------------------------- M45 / M46: the approved shape (P66 T5)
#
# M45 is PARITY BY MECHANISM and M46 is SIGNATURE VARIETY. Both read the cut the way the critic does, and neither
# invents a checklist: **the list is read against the cut's own beat plan**. A mechanism is OWED only where a beat's
# SHAPE calls for it - the plan's `plate` row token names the entry the beat intends (`mount=`, `:axes`, `:spiral`,
# `snap=`, `camera=`), so the PLAN says what is owed and the COMPILED timeline says what was done. A mechanism no
# beat calls for prints `not owed`; it is never a FAIL for a shape the cut never promised (the parent, P66 T5).
#
# Measured on the reference first (`thresholds-from-the-reference`): the approved Japan and Tokyo cuts read `present`
# or `not owed` on every line, and `test_gate_one_shot_floor.py` pins both rows' text on both cuts.


class Mechanism(NamedTuple):
    """One row of the mechanism list of 2026-09-16 (`docs/content-video-engine/CRITIC-REPORT.md`, table 1).

    The field is `says`, not `rule`: `build_gates_registry.ROLE_FIELDS` reads a class with a `rule` field as a ROW
    TYPE, and every entry of this list would then land in the registry as a gate of its own. This is data.
    """
    n: int
    name: str
    says: str


# The list the CRITIC and the GATE share, by its date - the critic cites it as `list of 2026-09-16`. Adding a row
# here changes what every cut is read against: it is a ruling (E99 s67 Apply 7), not a configuration knob.
MECHANISMS_2026_09_16 = (
    Mechanism(1, "the open on the chart", "the ledger page is the first frame, on its axes or mounting the world, "
                                          "drawing under the hook (s67 Apply 6; P53 T1)"),
    Mechanism(2, "the page builds", "a page BUILDS with the effects and holds built while its number is spoken; "
                                    "enter=built is not an answer (s67 Apply 2)"),
    Mechanism(3, "the mount", "a page whose number lands 7 s or more after its entry MOUNTS over the world and "
                              "builds under the setup sentence (s67 Apply 5-6; E45)"),
    Mechanism(4, "the axes entry", "a page enters by its own signature (:axes), never zoomed up from a card "
                                   "(s67 Apply 5)"),
    Mechanism(5, "the dip", "the dip only on a WORLD change - never a dock's transition (E47)"),
    Mechanism(6, "the page-to-page transform", "page to page by suck or cut with no empty cream between (E96 M36)"),
    Mechanism(7, "the spiral return", "the return by the SPIRAL, the page unwound, the ring on the chart (E40 s4; "
                                      "E56)"),
    Mechanism(8, "the dock that reads and parks", "a dock is an evidence still that READS then PARKS in the page's "
                                                  "own room (s67 Apply 5; E65)"),
    Mechanism(9, "the plate that carries a card", "a plate carries its card with directional life, never a bare "
                                                  "still (M44; E99 s65)"),
    Mechanism(10, "the light as punctuation", "a light lands on a sentence that POINTS, after the page's build - "
                                              "never filler for M16 (s67 Apply 1, 3)"),
    Mechanism(11, "old and new blend", "a NEW mechanism sits inside the approved shape and does not replace it "
                                       "(s67 Apply 8)"),
)

APPROVED_MIX_REL = "content/video_engine/effects/skeletons/approved-mix.json"
MOUNT_LANDS_S = 7.0        # E99 s67 Apply 5-6: a number landing this far after the page's entry owes the MOUNT
M46_MAX_SHARE = 0.34       # approved-mix.json `max_share.value` (0.3333 - Japan's card and cut) rounded up; HG1
                           # confirms it. Over this share of the scenes, one signature is the cut's only move.

PAGE_PREFIX, CLIP_PREFIX = "ledger:", "clip:"
# What a plan record's `plate` row token says the beat's page DOES - the plan's own statement of the mechanism.
ENTRY_TOKENS = (("mount", "mount="), ("axes", ":axes"), ("spiral", ":spiral"), ("snap", "snap="),
                ("camera", "camera="), ("throw", "throw="), ("built", ":built"))
LIGHT_CARDS = ("species:spotlight", "species:relight")
RETURN_CARDS = ("page_enter:spiral", "species:ring")
PAGE_TO_PAGE_CARDS = ("exit:suck", "exit:cut")
NUMBER_LANDS_CARDS = ("page_species:build_to", "page_species:figure", "species:callout", "species:ring",
                      "species:spotlight")     # where a page's NUMBER lands (the mount's 7 s clock, mechanism 3)
NEW_MECHANISM_MARK = "new mechanism"           # what a plan record says when it brings one (mechanism 11)
# What may stand in a missing mechanism's PLACE: a move the cut made instead. 1 is bound to the first beat (a
# position, not a move) and 11 is the blend marker, so neither can replace anything - the other nine can.
REPLACEMENT_CANDIDATES = (2, 3, 4, 5, 6, 7, 8, 9, 10)


@dataclass(frozen=True)
class Shape:
    """One beat as its PLAN record describes it, tied to the scene the compiled cut plays under it."""
    beat: int                 # 1-based - what a row names
    start: float
    end: float
    plate: str                # the plan's `plate`: the row token, which NAMES the entry (mount=, :axes, :spiral)
    caps: str                 # the record's `capabilities`, joined and lowercased
    scene: int | None         # the index of the scene the beat's middle sits in

    @property
    def page(self) -> bool:
        return self.plate.startswith(PAGE_PREFIX)

    @property
    def clip(self) -> bool:
        return self.plate.startswith(CLIP_PREFIX)

    @property
    def still(self) -> bool:
        """A PLATE beat - neither a ledger page nor a clip (M44 owns its six seconds)."""
        return bool(self.plate) and not self.page and not self.clip

    @property
    def entry(self) -> str | None:
        """The entry this beat's row token names: mount, axes, spiral, snap, camera, throw or built."""
        return next((name for name, token in ENTRY_TOKENS if token in self.plate), None)

    @property
    def page_id(self) -> str | None:
        """The evidence id of the page the beat plays on (`ledger:ev-x-v1:line:315:right:...` -> `ev-x-v1`)."""
        parts = self.plate.split(":")
        return parts[1] if self.page and len(parts) > 1 else None


@dataclass(frozen=True)
class Parity:
    """What M45 read for ONE mechanism: the verdict, the instant it was read at, and the beat it was read on."""
    n: int
    name: str
    verdict: str                  # present | absent | replaced | not owed
    detail: str

    @property
    def text(self) -> str:
        return f"{self.n:>2} {self.name:<30} {self.verdict:<9} {self.detail}"


def plan_records_by_beat(records: Sequence[Mapping[str, Any]], beats: Sequence[Mapping[str, Any]]) -> dict:
    """{beat index -> its plan record}, matched on `t0` (+- BEAT_T_TOL) and then on the 1-based `beat` number.

    M41's `plan_gaps` matches the same way inline and stays untouched (P66 T5 changes nothing in M35-M42); this is
    M45's own reader. A beat with no record is simply not a shape - M41 is the row that names that gap.
    """
    by_beat: dict = {}
    for record in records:
        index = next((i for i, b in enumerate(beats)
                      if record.get("t0") is not None
                      and abs(float(record["t0"]) - float(b["start"])) <= BEAT_T_TOL), None)
        if index is None:
            number = record.get("beat")
            index = int(number) - 1 if isinstance(number, (int, float)) else None
            if index is not None and not 0 <= index < len(beats):
                index = None
        if index is not None:
            by_beat.setdefault(index, record)
    return by_beat


def scene_span(scene: Mapping[str, Any]) -> tuple:
    """A scene's [start, end], read with the timeline schema's own defaults (a partial timeline still reads)."""
    span = list(scene.get("span") or [0.0, 0.0])
    start = float(span[0] if span else 0.0)
    return start, float(span[1] if len(span) > 1 else start)


# --- the evidence: what the COMPILED timeline must show for a mechanism to read `present` ---------------------

def _ev_open(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    """The page lands under the hook - on its axes or mounting the world in scene 1, or arriving inside beat 1."""
    return ev.cls == "page_enter"


def _ev_build(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    """The page BUILDS: a page species (build_to, the bracket, the recast, the figure) or the axes entry's draw."""
    return ev.cls == "page_species" or ev.card == "page_enter:axes"


def _ev_mount(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    return ev.card == "page_enter:mount"


def _ev_axes(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    return ev.card == "page_enter:axes"


def _ev_dip(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    return ev.card == "exit:dip"


def _ev_page_to_page(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    """A suck or a cut AT the boundary this beat's world arrives on - no empty cream between the two pages."""
    if ev.card not in PAGE_TO_PAGE_CARDS or s.scene is None:
        return False
    return abs(ev.t - scene_span(r.scenes[s.scene])[0]) <= EPS


def _ev_return(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    return ev.card in RETURN_CARDS


def _ev_dock_enters(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    return ev.cls == "dock_enter"


def _ev_dock_reads(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    """The dock READS then PARKS: `read_s` / `park_s` on the dock, not a card thrown and cut away."""
    return ev.card == "dock_option:read"


def _ev_plate_life(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    """The plate is not a bare still: a named idle, the Ken Burns move, the CARD it carries, or a living species.

    E99 s65 (plate life is directional) and the two approved cuts read together: Japan's plates carry `idle=drift`
    and a docked card, Tokyo's viewer's desk carries the steam, the ticker and the trace over a still whose
    `ken_burns.scale` is 0. Both are the mechanism; M44 owns the six-second clock, not this row.
    """
    return ev.cls in ("idle", "species", "dock_enter") or ev.card == RW.KEN_CARD


def _ev_light(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    return ev.card in LIGHT_CARDS


def _ev_light_after_build(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    """A light that is PUNCTUATION: after its own page's build, or on a world with no build to wait for."""
    if ev.card not in LIGHT_CARDS:
        return False
    built = r.first_build(ev.i)
    return built is None or ev.t + EPS >= built


def _ev_new_mechanism(r: "ShapeReader", ev: RW.Event, s: Shape) -> bool:
    return ev.cls in ("species", "page_species")


class ShapeReader:
    """M45's reader: what each beat's PLAN owes against what the COMPILED timeline did.

    OWED comes from the plan (the `plate` row token and the record's capabilities), PRESENT from
    `recipe_walk.events` - never the other way round. A mechanism reads `present` when it fires inside ANY beat that
    owes it: the window searched is the beat's own [t0, t1] UNION the span of the scene the beat plays under, because
    the transition that brings a world (the mount over the outgoing shot, the dip, the suck) lands a breath before
    the sentence that stands on it - Tokyo's holdings page mounts at 1.99 under beat 2 and is the shape of beats 3-11.
    """

    def __init__(self, m: Measures, records: Sequence[Mapping[str, Any]]) -> None:
        self.timeline = json.loads(m.timeline_path.read_text(encoding="utf-8"))
        self.scenes = list(self.timeline.get("scenes") or [])
        self.events = RW.events(self.timeline)
        by_beat = plan_records_by_beat(records, m.beats)
        self.shapes: list = []
        for i, beat in enumerate(m.beats):
            record = by_beat.get(i)
            if record is None:
                continue
            start, end = float(beat["start"]), float(beat["end"])
            self.shapes.append(Shape(
                beat=i + 1, start=start, end=end, plate=str(record.get("plate") or ""),
                caps=" ".join(str(c) for c in (record.get("capabilities") or [])).lower(),
                scene=self._scene_at((start + end) / 2.0)))

    # --- the cut's own geometry ----------------------------------------------------------------------------

    def _scene_at(self, t: float) -> int | None:
        for i, scene in enumerate(self.scenes):
            start, end = scene_span(scene)
            if start - EPS <= t <= end + EPS:
                return i
        return None

    def windows(self, shape: Shape) -> list:
        """The beat's own window UNION its scene's span - the class docstring says why the scene is in it."""
        out = [(shape.start, shape.end)]
        if shape.scene is not None:
            out.append(scene_span(self.scenes[shape.scene]))
        return out

    def first(self, want, shapes: Sequence[Shape]) -> tuple | None:
        """(the instant, the beat) the first event `want` accepts fires at, inside one of those beats' windows."""
        for shape in shapes:
            spans = self.windows(shape)
            for ev in self.events:
                if any(a - EPS <= ev.t <= b + EPS for a, b in spans) and want(self, ev, shape):
                    return ev.t, shape.beat
        return None

    def shapes_with(self, want) -> list:
        """Every beat whose window carries such an event - what the CUT puts on a beat (docks, lights, rings)."""
        return [s for s in self.shapes if self.first(want, [s])]

    def first_build(self, scene: int) -> float | None:
        """When the page in this scene first builds - what a light has to land after to be punctuation."""
        return next((ev.t for ev in self.events if ev.i == scene and ev.cls == "page_species"), None)

    def late_number_shapes(self) -> list:
        """Every beat a page's NUMBER lands on 7 s or more after that page entered - E99 s67's mount rule."""
        out: list = []
        for i, scene in enumerate(self.scenes):
            if not ((scene.get("world") or {}).get("page")):
                continue
            entered = next((ev.t for ev in self.events if ev.i == i and ev.cls == "page_enter"),
                           scene_span(scene)[0])
            landed = next((ev.t for ev in self.events if ev.i == i and ev.card in NUMBER_LANDS_CARDS), None)
            if landed is None or landed - entered < MOUNT_LANDS_S:
                continue
            out += [s for s in self.shapes if s.start - EPS <= landed <= s.end + EPS]
        return out

    def world_changes(self, shape: Shape) -> bool:
        """The plan says the WORLD changes at this beat: its row token is not the one the beat before stood on."""
        index = self.shapes.index(shape)
        return index > 0 and self.shapes[index - 1].plate != shape.plate

    # --- what each mechanism is OWED by --------------------------------------------------------------------

    def owed(self, n: int) -> list:
        """The beats whose SHAPE calls for mechanism `n` - read from the plan, never from what the cut did."""
        if n == 1:
            first = self.shapes[0] if self.shapes else None
            return [first] if first is not None and (first.page or self.first(_ev_open, [first])) else []
        if n == 2:
            return [s for s in self.shapes if s.page]
        if n == 3:
            declared = [s for s in self.shapes if s.page and s.entry == "mount"]
            late = [s for s in self.late_number_shapes() if s not in declared]
            return sorted(declared + late, key=lambda s: s.beat)
        if n == 4:
            return [s for s in self.shapes if s.page and s.entry == "axes"]
        if n == 5:
            return [s for s in self.shapes if self.world_changes(s)]
        if n == 6:
            return [b for a, b in zip(self.shapes, self.shapes[1:])
                    if a.page and b.page and a.page_id != b.page_id]
        if n == 7:
            declared = [s for s in self.shapes if s.page and s.entry == "spiral"]
            return declared or self.shapes_with(_ev_return)
        if n == 8:
            return self.shapes_with(_ev_dock_enters)
        if n == 9:
            return [s for s in self.shapes if s.still]
        if n == 10:
            return self.shapes_with(_ev_light)
        return [s for s in self.shapes if NEW_MECHANISM_MARK in s.caps]

    def evidence(self, n: int):
        """The event that shows mechanism `n` was actually performed."""
        return {1: _ev_open, 2: _ev_build, 3: _ev_mount, 4: _ev_axes, 5: _ev_dip, 6: _ev_page_to_page,
                7: _ev_return, 8: _ev_dock_reads, 9: _ev_plate_life, 10: _ev_light_after_build,
                11: _ev_new_mechanism}[n]

    def why_not_owed(self, n: int) -> str:
        """Why no beat calls for it - the sentence a `not owed` line owes the reader."""
        first = self.shapes[0] if self.shapes else None
        return {
            1: (f"beat 1 stands on `{first.plate}`, not a page, and no page lands under the hook"
                if first is not None else "the plan names no beat this gate can read"),
            2: "no beat stands on a ledger page",
            3: f"no beat's row token mounts, and no page's number lands {MOUNT_LANDS_S:.0f} s after its entry",
            4: "no beat's row token enters on its axes",
            5: "no beat changes the world the beat before stood on",
            6: "no two consecutive beats stand on different pages",
            7: "no beat's row token returns by the spiral, and no ring fires",
            8: "no beat carries a dock",
            9: "the plan holds no plate beat",
            10: "no light fires in this cut",
            11: "no beat names a new mechanism to blend",
        }[n]

    # --- the verdict ---------------------------------------------------------------------------------------

    def parity(self, mech: Mechanism) -> Parity:
        """`present` / `absent` / `replaced by <mechanism>` / `not owed`, for one mechanism, on this cut."""
        owed = self.owed(mech.n)
        if not owed:
            return Parity(mech.n, mech.name, "not owed", f"- {self.why_not_owed(mech.n)}")
        hit = self.first(self.evidence(mech.n), owed)
        if hit:
            return Parity(mech.n, mech.name, "present",
                          f"at {hit[0]:.2f} s (beat {hit[1]}), owed by {len(owed)} beat(s)")
        owed_at = ", ".join(str(s.beat) for s in owed[:6]) + ("..." if len(owed) > 6 else "")
        for other in MECHANISMS_2026_09_16:
            if other.n == mech.n or other.n not in REPLACEMENT_CANDIDATES:
                continue
            found = self.first(self.evidence(other.n), [owed[0]])
            if found and self.owed(other.n):
                return Parity(mech.n, mech.name, "replaced",
                              f"by {other.n} {other.name} at {found[0]:.2f} s on beat {owed[0].beat} "
                              f"- owed by beat(s) {owed_at}")
        return Parity(mech.n, mech.name, "absent",
                      f"- owed by beat(s) {owed_at}, nothing stands in its place - {mech.says}")

    def census(self) -> str:
        """Which shapes the plan holds - what every `not owed` line is read against."""
        pages = [s for s in self.shapes if s.page]
        entries = collections.Counter(s.entry or "no entry named" for s in pages)
        return (f"the plan holds {len(pages)} page beats ("
                + (", ".join(f"{k} x{v}" for k, v in sorted(entries.items())) or "none") + "), "
                f"{sum(1 for s in self.shapes if s.still)} plate beats, "
                f"{sum(1 for s in self.shapes if s.clip)} clip beats")


def row_m45(m: Measures) -> Gate:
    """One line per mechanism of the list of 2026-09-16, read against THIS cut's own beat plan."""
    records = beat_plan(m.build)
    if records is None:
        return Gate("M45", "INFO", f"no beat plan on disk ({BEAT_PLAN_NAME} absent in {m.build.name}) - a mechanism "
                                   f"is owed by a BEAT, so nothing is read here; M41 carries the missing plan",
                    SRC_M45)
    reader = ShapeReader(m, records)
    read = [reader.parity(mech) for mech in MECHANISMS_2026_09_16]
    counts = collections.Counter(p.verdict for p in read)
    absent = [f"{p.n} {p.name}" for p in read if p.verdict == "absent"]
    replaced = [f"{p.n} {p.name}" for p in read if p.verdict == "replaced"]
    head = (f"{len(read)} mechanisms read against the plan's {len(reader.shapes)} beats: {counts['present']} "
            f"present, {counts['not owed']} not owed, {len(replaced)} replaced, {len(absent)} absent"
            + (f" - ABSENT: {'; '.join(absent)}" if absent else "")
            + (f" - REPLACED: {'; '.join(replaced)}" if replaced else "")
            + f" - {reader.census()}")
    body = "\n".join(f"          | {p.text}" for p in read)
    return Gate("M45", "FAIL" if absent else "WARN" if replaced else "PASS", f"{head}\n{body}", SRC_M45)


def approved_mix(path: Path | None = None) -> dict | None:
    """The MEASURED mix of the approved cuts (`derive_approved_mix.py`'s artifact), or None when it is not on disk."""
    try:
        return json.loads(Path(path or REPO / APPROVED_MIX_REL).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def exempt_repeats(mix: Mapping[str, Any]) -> set:
    """The signatures the APPROVED cuts repeat back to back - Japan's throw -> snap pair reads card, card.

    M46 exempts exactly those pairs: the approved mix is the evidence, never a typed exception.
    """
    return {str(sig) for cut in (mix.get("approved") or []) for _, sig in (cut.get("consecutive_repeats") or [])}


def row_m46(m: Measures) -> Gate:
    """The cut's signature mix beside the approved shorts' MEASURED mix - JUDGE-adjacent, so it never FAILs.

    The classifier is `derive_approved_mix.scene_signatures` itself (one signature per scene, the rung order in its
    docstring): the target and the reading come out of the same function, so they cannot drift apart.
    """
    sigs = MIX.scene_signatures(json.loads(m.timeline_path.read_text(encoding="utf-8")))
    if not sigs:
        return Gate("M46", "PASS", "no scene carries a signature - nothing to read against the approved mix",
                    SRC_M46)
    mix = approved_mix()
    counts = collections.Counter(sigs)
    shares = {sig: n / len(sigs) for sig, n in counts.items()}
    mine = ", ".join(f"{sig} {shares[sig]:.2f}" for sig, _ in counts.most_common())
    target = (mix or {}).get("target") or {}
    theirs = ", ".join(f"{sig} {share:.2f}" for sig, share in
                       sorted((target.get("shares") or {}).items(), key=lambda kv: -kv[1])) or "not on disk"
    exempt = exempt_repeats(mix) if mix else set()
    over = [f"{sig} {shares[sig]:.2f}" for sig, _ in counts.most_common() if shares[sig] > M46_MAX_SHARE]
    repeats = [f"scenes {i}-{i + 1} {sigs[i]}" for i in range(1, len(sigs))
               if sigs[i] == sigs[i - 1] and sigs[i] not in exempt]
    note = "; ".join(([f"OVER {M46_MAX_SHARE:.2f}: {', '.join(over)}"] if over else [])
                     + ([f"CONSECUTIVE: {', '.join(repeats)} - the approved cuts repeat only "
                         + (", ".join(sorted(exempt)) or "nothing")] if repeats else []))
    return Gate("M46", "WARN" if over or repeats else "PASS",
                f"signature mix over {len(sigs)} scenes: {mine} - the approved cuts measure {theirs} "
                f"(approved-mix.json, {target.get('scenes', '-')} scenes); the ceiling is "
                f"{M46_MAX_SHARE:.2f} a signature" + (f" - {note}" if note else "")
                + "\n          | scenes: " + ", ".join(sigs), SRC_M46)


def rows(m: Measures, ref: Measures | None = None, predates: bool | None = None,
         ref_warn: str | None = None) -> list:
    """The ten rows of one build, in id order. `predates` defaults to the enumerated HG1 (A) set; `ref_warn` to the
    reference this run could not read (`m.ref_warn`), which turns the three reference rows from PASS to WARN."""
    old = predates_e96(m.build, m.timeline_path) if predates is None else predates
    warn = None if ref is not None else (m.ref_warn if ref_warn is None else ref_warn)
    return [row_m35(m, old), row_m36(m, old), row_m37(m, ref, warn), row_m38(m, ref, warn),
            row_m39(m, ref, warn), row_m40(m, ref), row_m41(m), row_m42(m), row_m45(m), row_m46(m)]


# --------------------------------------------------------------------------- the report

def report_text(gates: Sequence[Gate], m: Measures, ref: Measures | None) -> str:
    """The gate's stdout, verbatim: the header, the inputs it read, the rows in id order, the RESULT line."""
    lines = [f"=== ONE-SHOT FLOOR: {m.name} ===",
             f"  {'timeline':>20}: {m.timeline_path.name} ({m.runtime_s:.2f} s, {len(m.docks)} docks)",
             f"  {'beats':>20}: {m.n_beats} sentences ({m.beats_path.name})",
             f"  {'reference':>20}: " + (f"{ref.name} ({ref.n_beats} beats, measured at run time)" if ref
                                         else f"{m.ref_warn} NOT readable - E96's own numbers only" if m.ref_warn
                                         else "not on disk - E96's own numbers only"),
             f"  {'predates E96':>20}: " + ("yes (M35, M36 INFO - HG1 A)"
                                            if predates_e96(m.build, m.timeline_path) else "no"),
             *([f"  {'catalogue':>20}: {m.layers_note}"] if m.layers_note else []),
             ""]
    order = {rid: i for i, rid in enumerate(ROW_ORDER)}
    for g in sorted(gates, key=lambda g: order.get(g.id, 99)):
        lines.append(f"  [{g.level:5}] {g.id} {g.message}\n          {g.src}")
    n = lambda level: sum(1 for g in gates if g.level == level)
    lines.append(f"\nRESULT: {n('FAIL')} FAIL / {n('WARN')} WARN / {n('PASS')} PASS / {n('JUDGE')} JUDGE / "
                 f"{n('INFO')} INFO")
    return "\n".join(lines)


def fail_count(gates: Sequence[Gate]) -> int:
    return sum(1 for g in gates if g.level == "FAIL")


def is_own_catalog(catalog: Path) -> bool:
    """Is this the repo's own generated artifact, or a `--catalog` the caller pointed somewhere else?

    Anything else is the caller's file, read exactly as given - never checked, never rebuilt."""
    try:
        return catalog.resolve() == (REPO / CATALOG_REL).resolve()
    except OSError:
        return False


def catalog_note(catalog: Path) -> str | None:
    """The staleness line for the report HEADER - this gate's verdict depends on a current catalogue,
    so the reader is told, in the report, exactly how current the catalogue behind it was (P64 T1).

    It still RUNS on what is on disk: the operator's rule is that nothing blocks. `--wait` is there
    for the run that must be current."""
    return DL.stale_note(DL.status(REPO, [CATALOG_LAYER])) if is_own_catalog(catalog) else None


def ensure_catalog(catalog: Path, *, wait: bool = False) -> list[str]:
    """With `wait`, rebuild THIS repository's catalogue iff its inputs moved before the gate reads it.

    The DEFAULT builds nothing (P64 T1) - `catalog_note` puts the staleness in the report header and
    the gate runs on the catalogue as it sits. A builder that fails is named on stderr and the gate
    runs anyway - a broken card must not take the floor's other seven rows down."""
    if not wait or not is_own_catalog(catalog):
        return []
    try:
        return DL.ensure([CATALOG_LAYER], REPO)
    except DL.LayerError as exc:
        print(f"[layers] {exc.layer} failed to rebuild: {exc.detail}", file=sys.stderr)
        return []


def run(build: Path, project: Path | None = None, reference: Path | None = None, catalog: Path | None = None,
        timeline_name: str | None = None, wait: bool = False) -> tuple:
    """Measure the build (and the reference, with the same functions) and return (rows, the cut, the reference).

    A reference that is absent, holds no compiled timeline or cannot be parsed never kills the run (the P56 review):
    `m.ref_warn` carries the path and the three reference rows say so while holding the rule's own number.
    """
    catalog = Path(catalog or REPO / CATALOG_REL)
    ensure_catalog(catalog, wait=wait)
    note = catalog_note(catalog)
    recipes, options = load_recipes(catalog), card_options(catalog)
    registry = recipe_registry(catalog)
    m = measure(Path(build), project, recipes, options, timeline_name, registry)
    m.layers_note = note
    ref_dir = Path(reference) if reference else REPO / REFERENCE_REL
    ref: Measures | None = None
    if ref_dir.resolve() == Path(build).resolve():
        ref = m
    else:
        try:
            ref = measure(ref_dir, None, recipes, options, registry=registry)
        except (SystemExit, OSError, ValueError, KeyError, TypeError):
            m.ref_warn = str(ref_dir)
    return rows(m, ref), m, ref


def main() -> int:
    ap = argparse.ArgumentParser(description="the one-shot floor (M35-M42, M45-M46) on a compiled build (P56, P66, E96)")
    ap.add_argument("build", type=Path, help="the build dir holding the compiled *.timeline.json")
    ap.add_argument("--project", type=Path, help="the project dir (only to resolve narration.words_path)")
    ap.add_argument("--reference", type=Path, help=f"the reference build (default {REFERENCE_REL})")
    ap.add_argument("--catalog", type=Path, help=f"the effects catalogue (default {CATALOG_REL})")
    ap.add_argument("--timeline", help="the compiled timeline's file name inside the build dir")
    ap.add_argument("--wait", action="store_true",
                    help="rebuild a stale catalogue and block on it first (the default runs on what is "
                         "on disk and names its staleness in the header)")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gates, m, ref = run(args.build, args.project, args.reference, args.catalog, args.timeline, args.wait)
    print(report_text(gates, m, ref))
    return 1 if fail_count(gates) else 0


if __name__ == "__main__":
    raise SystemExit(main())

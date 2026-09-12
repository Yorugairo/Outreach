"""Species by sentence - the lint (P50 T1, 2026-09-11). INFO only; it never blocks a build.

The map is docs/content-video-engine/SPECIES-BY-SENTENCE.md: ten sentence ACTS (QUOTES, RANKS, COMPARES, DIVIDES, NAMES,
EXPLAINS, TURNS, BREAKS, SPANS, SETS, RETRACTS) each pointing at the species or verb a shot row should carry. This reads a
project's written shot table (`SHOT-TABLE-SHORT.py`, the `W` literal the build writes) and the build's `timeline.json`
(the take's `sentences` on the clock the docks and captions use), classifies every sentence by a keyword table - crude on
purpose, like V05 - and prints one line per sentence:

    t0-t1 · "the sentence" · ACTS · available: <built species for those acts> · row has: <what fires in the window, or none>

A sentence with an act, an available species and nothing firing is marked `· no row` (INFO, the author's eye). For a
long-form table (runtime >= LONG_FORM_S or --long) it lists every plate row with its `;use=` and WARNs one without (E61:
a plate is a landing surface, a bridge or a reset, and says which; the compiler's PLATE_OPTS learns the token with P51 T0).

    python content/video_engine/scripts/lint_species_choice.py <project dir> [--build <dir>] [--table <py>] [--words <timeline.json>] [--long]
    python content/video_engine/scripts/lint_species_choice.py <project dir> [--build <dir>] --propose
    python content/video_engine/scripts/lint_species_choice.py --when [--md] [--write-doc | --check-doc]

`--propose` (P53 T8) adds a PROPOSAL block after the report: for every sentence with an act, an available species and NO row
firing, one DRAFT ROW per available species - anchored on a PHRASE, targeted off the series' own `facts` - for the author to
keep or delete. A PROPOSER, never an allocator: it writes no shot table, and nothing in it was chosen by count.

`--when` prints the compiler's `when` on every kind (SPECIES_WHEN / CHART_TO_WHEN); `--write-doc` regenerates the map's
s4 block between the SPECIES_WHEN markers, `--check-doc` exits 1 when the block is stale. Exit 0 otherwise; 2 on usage.

THE PROPOSER'S LIMIT (P53 T8, found by the agent that built it, 2026-09-12): `--propose` reads the WORLD UNDER a
sentence, never the sentence's REFERENT. On the bridge short it offered the federal-load page's last datum (123%
of GDP) for "Five percent was normal once." - a sentence about a YIELD, whose series was not on stage - and all four
candidates put the wrong number on the wrong page. It also cannot see a species firing just outside the sentence's
own window, so "no row fires here" is weaker than "this beat is unmarked". So the sheet offers several candidates
per sentence and the author's work is DELETION. That ratio is the honest signal: tune it toward "the best one" and
this is an allocator again (PIPELINE.md).
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # bare-module import works from any cwd / test runner
import build_scene_timeline_f as B  # noqa: E402
from build_scene_timeline_f import PLATE_USES  # noqa: E402,F401  E61: the compiler owns the tuple; `L.PLATE_USES` still reads

ROOT = Path(__file__).resolve().parents[3]
MAP_DOC = ROOT / "docs/content-video-engine/SPECIES-BY-SENTENCE.md"
DOC_BEGIN, DOC_END = "<!-- SPECIES_WHEN:BEGIN -->", "<!-- SPECIES_WHEN:END -->"
LONG_FORM_S = 180.0          # the script gates' route: a measured clock under 3:00 is a short (E35 / G2)
TABLE_NAME = "SHOT-TABLE-SHORT.py"
DEFAULT_BUILD = "build-short"
TEXT_W = 74

# The keyword table. Crude on purpose (V05's lesson: a classifier the author can read beats one they cannot argue with).
ACT_RE = {
    "QUOTES": r"\b(said|says|saying|announced|pledg\w*|promis\w*|told|wrote|reported|according to|claim\w*|we call this|quot\w+)\b",
    "RANKS": r"\b(biggest|largest|smallest|top|highest|lowest|most|least|number one|rank\w*|the first|the second|the third)\b",
    "COMPARES": r"\b(since|over the (?:last|same|past)|monthly|month by month|a year at a time|each month|every month|climbed|fell|rose|dropped|went up|went down|selling|sold|trend\w*|decade|years?)\b",
    "DIVIDES": r"\b(share of|a tenth|a third|a quarter|half of|percent of|out of every|slice|portion|split|of the pile)\b",
    "NAMES": r"\b(cross\w*|across|through|route|border|port|strait|ship\w*|flow\w*|export\w*|import\w*|went home|brought .* home|from \w+ to \w+)\b",
    "EXPLAINS": r"\b(because|so that|which means|that's why|therefore|when you\w*|when your|works? like|mechanism|the reason|forces?|causes?|compound\w*|discounts?|we call this|funded)\b",
    "BREAKS": r"\b(beats?|dwarfs?|blows? past|breaks|breaks? (?:through|past)|off the chart|times bigger|many times|outgrows?)\b",   # `breaks` the verb only: "tea break" is a noun
    "SPANS": r"\b(between|from .+ to|the gap|distance|spread|over the period|the same months)\b",
    "SETS": r"\b(two numbers|two things|three things|two reasons|here's what|here's where|both numbers|the second number|the first number|second lever)\b",
    "RETRACTS": r"\b(none of this|didn't happen|never happened|isn't the|not the|wasn't|instead|nobody (?:explained|says|on)|not a penny|wrong|myth)\b",
}
TURNS_RE = r"\b(\d[\d,.]*|hundred|thousand|million|billion|trillion|percent|per cent|dollars?|yen|multiple)\b"
ACTS = ("QUOTES", "RANKS", "COMPARES", "DIVIDES", "NAMES", "EXPLAINS", "TURNS", "BREAKS", "SPANS", "SETS", "RETRACTS")
_ACT_RE = {k: re.compile(v, re.I) for k, v in ACT_RE.items()}
_TURNS = re.compile(TURNS_RE, re.I)

# What the map lists as BUILT for each act (SPECIES-BY-SENTENCE.md s1-s2) ...
ACT_SPECIES = {
    "QUOTES": ("record dock", "read->park"),
    "RANKS": ("bars page", "callout", "burst"),
    "COMPARES": ("line page", "tiers page", "build_to", "chart_to:rescale", "chart_to:extend", "figure"),   # P50 T9: N small multiples on one shared x - the same quantity across two, three or four subjects
    "DIVIDES": ("share page", "peel", "treemap page", "cross"),   # P50 T6: the census, and the X's on its named subset
    "NAMES": ("trace", "light", "arc", "stamp"),   # P50 T5: the vector map ships - a country lights, an arc crosses, a figure stamps
    "EXPLAINS": ("note", "plate use=bridge", "chip", "flow"),
    "TURNS": ("figure", "spotlight", "callout", "note"),
    "BREAKS": ("burst", "stack", "burst:stop", "placeholder", "axis capsule"),
    "SPANS": ("bracket", "spread", "relight", "span"),
    "SETS": ("chart_to:park", "figure", "retitle"),
    "RETRACTS": ("retitle", "squiggle"),
}
# ... and what it names as pending, by task (s5), so the line says where the better species is.
ACT_PENDING = {
    # every act has its species now (2026-09-11): QUOTES the press card (T3), EXPLAINS the chip (T2) + the flow diagram (T4), NAMES the vector map (T5),
}                                # DIVIDES closed: the treemap page and its X marks (T6), COMPARES widened by the tiers page (T9); RETRACTS closed: the chip crosses out (T2)


# ---------------------------------------------------------------- the inputs
def load_table(path: Path) -> list[tuple]:
    """The `W = [...]` literal the build writes (`SHOT-TABLE-SHORT.py`): rows of (start, end, plate, ken, docks, exit[, species[, camera]])."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^W = (.*)$", text, re.S | re.M)
    if not match:
        raise ValueError(f"{path}: no `W = [...]` literal")
    rows = ast.literal_eval(match.group(1).strip())
    return [tuple(r) for r in rows]


def load_sentences(path: Path) -> list[dict]:
    """The build's timeline.json (`write_timeline`): `sentences` [{text, start, end}] on the take's clock."""
    data = json.loads(path.read_text(encoding="utf-8"))
    sents = data.get("sentences") or []
    if not sents:
        raise ValueError(f"{path}: no `sentences` (the build writes them from the take's words)")
    return [{"text": s["text"], "start": float(s["start"]), "end": float(s["end"])} for s in sents]


def plate_opts(plate_id: str) -> tuple[str, dict]:
    """`<plate>[;k=v...]` -> (bare, opts). The lint's own parser: it reads `;use=` (E61) before the compiler learns it."""
    bare, *parts = plate_id.split(";")
    opts: dict = {}
    for part in parts:
        if "=" in part:
            k, v = part.split("=", 1)
            opts.setdefault(k, []).append(v) if k == "then" else opts.__setitem__(k, v)
    return bare, opts


def world_of(plate_id: str) -> dict:
    """kind (ledger | clip | plate), the object id and the `;then=` state objects of a ledger row, the plate's `use`."""
    bare, opts = plate_opts(plate_id)
    if bare.startswith(B.LEDGER_PREFIX):
        obj = bare[len(B.LEDGER_PREFIX):].split(":")[0]
        states = [t.split(":")[0] for t in opts.get("then", [])]
        return {"kind": "ledger", "object": obj, "states": states, "use": opts.get("use")}
    if bare.startswith("clip:"):
        return {"kind": "clip", "object": Path(bare[5:]).name, "states": [], "use": opts.get("use")}
    return {"kind": "plate", "object": bare, "states": [], "use": opts.get("use")}


def overflow_of(project: Path, obj: str) -> str | None:
    """`overflow` on the object (E60: burst | stack), or None."""
    p = project / "evidence/objects" / f"{obj}.series.json"
    if not p.is_file():
        return None
    try:
        mode = json.loads(p.read_text(encoding="utf-8")).get("overflow")
    except (OSError, ValueError):
        return None
    return mode if isinstance(mode, str) else None


# ---------------------------------------------------------------- the classifier
def classify(text: str) -> list[str]:
    """The acts a sentence carries, in the map's order. Crude keyword hits; a sentence may carry several."""
    out = [act for act in ACTS if act != "TURNS" and _ACT_RE[act].search(text)]
    if _TURNS.search(text):
        out.append("TURNS")
    return [a for a in ACTS if a in out]


def available(acts: list[str]) -> list[str]:
    out: list[str] = []
    for act in acts:
        for sp in ACT_SPECIES.get(act, ()):
            if sp not in out:
                out.append(sp)
    return out


def pending(acts: list[str]) -> list[str]:
    return [f"{ACT_PENDING[a]} ({a})" for a in acts if a in ACT_PENDING]


# ---------------------------------------------------------------- what the table does in a window
def _in(t, s0: float, s1: float) -> bool:
    return isinstance(t, (int, float)) and s0 <= float(t) < s1


def row_events(rows: list[tuple], s0: float, s1: float, project: Path) -> list[str]:
    """Everything the table fires inside [s0, s1): species (with the chart_to verb and its state's overflow), docks
    entering, worlds starting (with the page's overflow)."""
    out: list[str] = []
    for row in rows:
        start, end, plate = float(row[0]), float(row[1]), row[2]
        world = world_of(plate)
        if _in(start, s0, s1):
            tag = f"world {world['kind']}:{world['object']}"
            if world["kind"] == "ledger":
                mode = overflow_of(project, world["object"])
                if mode:
                    tag += f" ({mode})"
            if world["kind"] == "plate" and world["use"]:
                tag += f" use={world['use']}"
            out.append(tag)
        if end <= s0 or start >= s1:
            continue
        for dock in (row[4] or []):
            if len(dock) >= 3 and _in(dock[2], s0, s1):
                opts = dock[4] if len(dock) > 4 and isinstance(dock[4], dict) else {}
                out.append(f"dock {dock[0]}" + (" (read->park)" if opts.get("read") else "") + (" centred" if opts.get("centre") and not opts.get("read") else ""))
        for sp in (row[6] if len(row) > 6 and row[6] else []):
            if not isinstance(sp, dict) or not _in(sp.get("at"), s0, s1):
                continue
            kind = sp.get("kind")
            if kind == "chart_to":
                verb = sp.get("to")
                tag = f"chart_to:{verb}"
                if verb == "park":
                    tag += f" {sp.get('scale')}" + (" (un-park)" if sp.get("scale") == 1.0 else "")
                if verb in ("recast", "morph") and isinstance(sp.get("state"), int):
                    idx = sp["state"] - 1
                    if 0 <= idx < len(world["states"]):
                        obj = world["states"][idx]
                        mode = overflow_of(project, obj)
                        tag += f" -> {obj}" + (f" ({mode})" if mode else "")
                out.append(tag)
            else:
                out.append(kind + (" hold" if sp.get("dur") == "hold" else ""))
    return out


# ---------------------------------------------------------------- the proposer (P53 T8, --propose)
# NOT AN ALLOCATOR, and it cannot become one. PIPELINE.md "Stage 7 is AUTHORED. There is no allocator": a loop that
# fills slots by count answers "how many fit" instead of "which one belongs", and no quality of tuning fixes that.
# So this mode counts nothing, chooses nothing and writes no shot table. For a sentence that DOES something (an act),
# whose act has a built species, and whose window fires nothing, it prints EVERY available species as a draft row -
# the sentence above them - for the author to keep or delete. A sentence with no act, or with a row already firing,
# is not proposed for at all.
PROPOSE_WORDS = 4     # the anchor is the sentence's own first words, as a PHRASE call: the take stays the clock (authoring/words.py `at`)
FILL = "FILL: "       # a field only the author can write; pasted as-is it FAILS the compiler's validator, which is the point
PROPOSE_HEADER = ("PROPOSE · draft rows only - every one is a CANDIDATE for the author to keep or delete, nothing was chosen by "
                  "count and no shot table was written (Stage 7 is AUTHORED: PIPELINE.md, \"There is no allocator\")")

# What the map lists for an act that is NOT a row's species dict - the world, a dock or a page choice. Named here so a
# new label in ACT_SPECIES cannot be dropped in silence (the test holds every label against this or a real kind).
NOT_A_SPECIES = {
    "record dock": "a DOCK (the record card), registered on the row - not a species",
    "read->park": "the record dock's `read` option (it pops centred, then parks)",
    "bars page": "the PAGE's own builder (`ledger:<obj>:story`)",
    "line page": "the PAGE's own builder (`ledger:<obj>:line`)",
    "tiers page": "the PAGE's own builder (the small multiples, P50 T9)",
    "share page": "the PAGE's own builder (the share/pie)",
    "treemap page": "the PAGE's own builder (the census, P50 T6)",
    "plate use=bridge": "the plate row's `;use=bridge` token (E61)",
    "burst": "the object's `overflow` in its own series file (E60)",
    "stack": "the object's `overflow` in its own series file (E60)",
    "burst:stop": "the object's `overflow` - the stopped burst (E60)",
    "placeholder": "a page option (the empty slot the number lands in)",
    "axis capsule": "a page option (the axis capsule the figure breaks)",
}

# The ONLY kind whose own `when` names a duration: SPECIES_WHEN["spotlight"] (E25 amended - the light holds until the
# sentence has a reason to leave; the compiler resolves "hold" against the next event). Every other kind is printed
# WITHOUT `dur`, and the row's comment says so - `_validate_entry` requires a number, so the author writes it.
DUR_DEFAULT = {"spotlight": "hold"}

# The fields a kind cannot be READ without: the compiler's own validators (`_validate_page_fields`, `_validate_chip`,
# `_validate_flow`, `_validate_vecmap_species`), plus the label E56 requires of a ring. Prompts, never values.
_EDGE = "a datum index (the page's own) or an x-fraction 0..1 - both edges the same way"
PROPOSE_FILL = {
    "callout": (("label", "the sentence's figure, as it is said (E56: a ring carries the number)"),),
    "figure": (("text", "the figure with its unit - never a bare number"),),
    "note": (("text", "the side fact the chart cannot show, in one line"),),
    "retitle": (("text", "what the page is about now"),),
    "relight": (("ref", "bracket | title - which mark re-fires"),),
    "bracket": (("from", _EDGE), ("to", _EDGE), ("label", "what the two data measure")),
    "spread": (("from", "the series index the gap starts at"), ("to", "the second series' index (or `to_rule`)")),
    B.SPECIES_SPAN: (("from", _EDGE), ("to", _EDGE), ("label", "the stretch of time's own name")),
    B.SPECIES_CHIP: (("icon", "a SOURCED glyph under assets/icons"), ("label", "the thing the chip stands for")),
    B.SPECIES_FLOW: (("nodes", "2-6 {id, icon, label}"), ("edges", "the arrows, by node id")),
    B.SPECIES_CROSS: (("cells", "the treemap cells' own labels"), ("text", "the crossed share, written as a number")),
    B.SPECIES_STAMP: (("text", "the number or the name written at the place"),),
    B.SPECIES_ARC: (("from", "the origin (a country id or a map point)"), ("to", "the destination")),
}


def proposable(label: str) -> tuple[str, dict] | None:
    """(kind, the fields the label itself fixes) for a map label that CAN be a row's species dict; None otherwise."""
    if label in B.SPECIES_KINDS:
        return label, {}
    kind, _, verb = label.partition(":")
    if kind == "chart_to" and verb in B.CHART_TO_KINDS:
        return kind, {"to": verb}
    return None


def when_of(kind: str, fixed: dict) -> str:
    """The compiler's own `when` for the thing being proposed - the verb's `when` for a chart_to."""
    return B.CHART_TO_WHEN[fixed["to"]] if kind == "chart_to" and "to" in fixed else B.SPECIES_WHEN[kind]


def candidates(acts: list[str]) -> list[tuple[str, str]]:
    """(label, the act that proposed it) for every species the acts make available, in the map's order, once each."""
    out, seen = [], set()
    for act in acts:
        for label in ACT_SPECIES.get(act, ()):
            if label not in seen:
                seen.add(label)
                out.append((label, act))
    return out


# ---------------------------------------------------------------- the anchor: a PHRASE, never a number
def _norm_w(s: str) -> str:
    return s.strip(".,:;!?\"'").lower()       # authoring/words.py `_norm`, mirrored so the lint imports none of the kit


def _phrase_hits(words: list[dict], phrase: str) -> int:
    toks = [_norm_w(t) for t in phrase.split()]
    ws = [_norm_w(w.get("w", "")) for w in words]
    return sum(1 for i in range(len(ws) - len(toks) + 1) if ws[i:i + len(toks)] == toks) if toks else 0


def anchor_phrase(text: str, words: list[dict] | None, n: int = PROPOSE_WORDS) -> tuple[str, bool]:
    """The sentence's first `n` words as the row's anchor, and whether the take carries them exactly once. Falls back
    to n-1 words when n are not in the take; the caller says so when neither is."""
    toks = text.split()
    for k in (n, n - 1):
        phrase = " ".join(toks[:k])
        if k <= 0 or not phrase:
            continue
        if words is None or _phrase_hits(words, phrase) == 1:
            return phrase, True
    return " ".join(toks[:n]) or text, False


def take_words_of(words_file: Path) -> list[dict] | None:
    """The build's own words (`timeline.json` "words"), for checking an anchor resolves; None when it carries none."""
    try:
        data = json.loads(words_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    ws = data.get("words")
    return ws if isinstance(ws, list) and ws else None


# ---------------------------------------------------------------- the target: the series' own facts, by NAME
def facts_of(project: Path, obj: str) -> dict:
    """The `facts` block of `evidence/objects/<obj>.series.json`, or {}."""
    p = project / "evidence/objects" / f"{obj}.series.json"
    if not p.is_file():
        return {}
    try:
        facts = json.loads(p.read_text(encoding="utf-8")).get("facts")
    except (OSError, ValueError):
        return {}
    return facts if isinstance(facts, dict) else {}


def index_keys(facts: dict) -> list[str]:
    """The facts that NAME a datum index (`last_idx`, `peak_idx`, `idx_1981q4` ...), `last_idx` first."""
    keys = [k for k, v in facts.items() if isinstance(v, int) and not isinstance(v, bool)
            and (k.endswith("_idx") or k.startswith("idx_"))]
    return sorted(keys, key=lambda k: (k != "last_idx", keys.index(k)))


def world_at(rows: list[tuple], t: float) -> dict | None:
    """The world the table has on stage at `t` - the sentence's own page, so a page species is proposed onto a page."""
    for row in rows:
        if float(row[0]) <= t < float(row[1]):
            return world_of(row[2])
    return None


def world_refuses(kind: str, world: dict | None) -> str | None:
    """Why this world cannot carry this kind - the compiler's own two refusals (`validate_species`), so a proposal is
    never one the build would throw out: a page species performs on a ledger page, a map species on a vector map."""
    where = f"{world['kind']}:{world['object']}" if world else "no world on stage"
    if kind in B.PAGE_SPECIES and (not world or world["kind"] != "ledger"):
        return f"a page species performs on a ledger page, not on {where}"
    if kind in B.VECMAP_SPECIES and (not world or not B.VECMAP_PREFIX.match(world["object"])):
        return f"a vecmap species performs on a vector map world, not on {where}"
    return None


def propose_target(kind: str, world: dict | None, project: Path) -> tuple[str | None, list[str]]:
    """The rendered `target` value and the notes it carries: a datum read off the series' own facts BY NAME where the
    sentence's page has them, else a FILL prompt naming that target kind's fields. Nothing is invented."""
    allowed = B.SPECIES_TARGETS.get(kind, ())
    if not allowed:
        return None, []
    facts = facts_of(project, world["object"]) if world and world["kind"] == "ledger" else {}
    keys = index_keys(facts)
    if "datum" in allowed and keys:
        code = f'{{"kind": "datum", "index": facts({json.dumps(world["object"])})[{json.dumps(keys[0])}]}}'
        rest = ", ".join(keys[1:])
        note = f"target: the series' own facts, by name (this one is {keys[0]}; the other data the sentence may mean: {rest})"
        return code, [note] if rest else []
    tk = next((k for k in ("datum", "region", "point") if k in allowed), allowed[0])
    fields = ", ".join(B.TARGET_FIELDS.get(tk, ())) or "the target kind's own fields"
    return json.dumps(f"{FILL}a {tk} target ({fields})"), []


# ---------------------------------------------------------------- the draft row
def draft_row(kind: str, fixed: dict, act: str, phrase: str, anchored: bool,
              world: dict | None, project: Path) -> str:
    """One draft row: a python dict literal whose `at` is a PHRASE call, with one trailing comment naming the ACT,
    what the author still owes, and the `when` sentence that proposed it (last, verbatim)."""
    fields = [f'"kind": {json.dumps(kind)}', f'"at": at({json.dumps(phrase)})']
    notes: list[str] = []
    if kind in DUR_DEFAULT:
        fields.append(f'"dur": {json.dumps(DUR_DEFAULT[kind])}')
    else:
        notes.append("no default dur - the compiler requires a number (give it the words' own length)")
    fields += [f'"{k}": {json.dumps(v)}' for k, v in fixed.items()]
    target, tnotes = propose_target(kind, world, project)
    if target:
        fields.append(f'"target": {target}')
    notes += tnotes
    fields += [f'"{k}": {json.dumps(FILL + prompt)}' for k, prompt in PROPOSE_FILL.get(kind, ())]
    if kind == "chart_to":
        notes.append("the verb's own fields are the compiler's (`_validate_chart_to`)")
    if not anchored:
        notes.append("the take does not carry these words exactly once - lengthen the phrase by hand")
    return ("    {" + ", ".join(fields) + "},   # " + act
            + (" · " + " · ".join(notes) if notes else "") + " · when: " + when_of(kind, fixed))


def sentence_proposal(sent: dict, acts: list[str], rows: list[tuple], project: Path,
                      take: list[dict] | None) -> list[str]:
    """The PROPOSAL block for one sentence: the sentence itself, a draft row per available species, and what its acts
    offer that is not a species row at all (a page, a dock, an overflow - said, never proposed)."""
    world = world_at(rows, sent["start"])
    phrase, anchored = anchor_phrase(sent["text"], take)
    drafts, refused, not_species = [], [], []
    for label, act in candidates(acts):
        pair = proposable(label)
        if pair is None:
            not_species.append(f"{label} ({NOT_A_SPECIES.get(label, 'not a species row')})")
            continue
        kind, fixed = pair
        why = world_refuses(kind, world)
        if why:
            refused.append(f"{label} ({why})")
        else:
            drafts.append(draft_row(kind, fixed, act, phrase, anchored, world, project))
    if not drafts and not refused and not not_species:
        return []
    head = (f"PROPOSAL {sent['start']:6.2f}-{sent['end']:6.2f} · \"{sent['text']}\" · {'+'.join(acts)}"
            f" · on {world['kind'] + ':' + world['object'] if world else 'no world'}")
    tail = [f"    # not proposable on this world: {'; '.join(refused)}"] if refused else []
    tail += [f"    # not a species row (the world, a dock or a page): {'; '.join(not_species)}"] if not_species else []
    return [head] + drafts + tail


def propose(project: Path, build: str | None = None, table: Path | None = None,
            words: Path | None = None) -> tuple[list[str], dict]:
    """The proposal sheet. It writes nothing, counts nothing and chooses nothing: it offers what each sentence's own
    act makes available, and the author keeps or deletes."""
    table_p, words_p = resolve_inputs(project, build, table, words)
    rows, sents = load_table(table_p), load_sentences(words_p)
    take = take_words_of(words_p)
    lines = [PROPOSE_HEADER,
             f"PROPOSE · {project.name} · {table_p.name} + {_rel(words_p, project)} · anchors are PHRASE"
             f" calls (authoring/words.py `at` reads the time out of the take) · every {FILL.strip()} field is the author's"
             + ("" if take else " · no words in the build's timeline - anchors are unchecked")]
    counts = {"proposed_for": 0, "rows": 0, "has_row": 0, "no_act": 0}
    for sent in sents:
        acts = classify(sent["text"])
        if not acts or not available(acts):
            counts["no_act"] += 1
            continue
        if [e for e in row_events(rows, sent["start"], sent["end"], project) if not e.startswith("world ")]:
            counts["has_row"] += 1
            continue
        block = sentence_proposal(sent, acts, rows, project, take)
        if not block:
            continue
        counts["proposed_for"] += 1
        counts["rows"] += sum(1 for line in block if line.strip().startswith("{"))
        lines += block
    lines.append(f"PROPOSE · {counts['proposed_for']} sentences proposed for · {counts['rows']} draft rows · "
                 f"{counts['has_row']} already have a row firing · {counts['no_act']} carry no act or no built species (never proposed for)"
                 + ("" if counts["proposed_for"] else " · nothing to propose"))
    return lines, counts

# ---------------------------------------------------------------- the report
def _rel(path: Path, project: Path) -> str:
    """The words file as the header names it: under the project when it is, else as given."""
    try:
        return path.relative_to(project).as_posix()
    except ValueError:
        return path.as_posix()


def build_dir(project: Path, build: str | None) -> Path:
    """`--build` names a build dir UNDER the project; a path that already points at one (tab-completed from the repo
    root) is taken as it stands, so the same argument works from either place."""
    named = Path(build or DEFAULT_BUILD)
    return named if named.is_dir() and (named / "timeline.json").is_file() else project / named


def resolve_inputs(project: Path, build: str | None, table: Path | None, words: Path | None) -> tuple[Path, Path]:
    table = table or project / TABLE_NAME
    words = words or build_dir(project, build) / "timeline.json"
    if not table.is_file():
        raise FileNotFoundError(f"no shot table at {table} (the build writes {TABLE_NAME}; --table names another)")
    if not words.is_file():
        raise FileNotFoundError(f"no timeline.json at {words} (--build names the build dir; --words names the file)")
    return table, words


def report(project: Path, build: str | None = None, table: Path | None = None, words: Path | None = None,
           long: bool = False) -> tuple[list[str], dict]:
    table, words = resolve_inputs(project, build, table, words)
    rows, sents = load_table(table), load_sentences(words)
    runtime = max(float(r[1]) for r in rows) if rows else 0.0
    lines = [f"species by sentence · {project.name} · {table.name} + {_rel(words, project)} · {len(sents)} sentences · {len(rows)} rows · {runtime:.1f} s"]
    counts = {"sentences": len(sents), "with_act": 0, "with_row": 0, "no_row": 0, "plates": 0, "plates_unnamed": 0}
    for s in sents:
        acts = classify(s["text"])
        avail, pend, has = available(acts), pending(acts), row_events(rows, s["start"], s["end"], project)
        text = s["text"] if len(s["text"]) <= TEXT_W else s["text"][:TEXT_W - 1] + "…"
        fired = [e for e in has if not e.startswith("world ")]   # a world starting is context, not a species row
        no_row = bool(acts) and bool(avail) and not fired
        counts["with_act"] += bool(acts)
        counts["with_row"] += bool(has)
        counts["no_row"] += no_row
        line = (f"INFO {s['start']:6.2f}-{s['end']:6.2f} · \"{text}\" · {'+'.join(acts) or 'bridge'}"
                f" · available: {', '.join(avail) or '-'}" + (f" (pending: {'; '.join(pend)})" if pend else "")
                + f" · row has: {', '.join(has) or 'none'}" + (" · no row" if no_row else ""))
        lines.append(line)
    lines.append(f"INFO {counts['sentences']} sentences · {counts['with_act']} carry an act · {counts['with_row']} have a row firing"
                 f" · {counts['no_row']} have an available species and no row")
    if long or runtime >= LONG_FORM_S:
        lines.append(f"INFO long form ({runtime:.0f} s): E61 - every plate names its use (;use={'|'.join(PLATE_USES)})")
        for row in rows:
            world = world_of(row[2])
            if world["kind"] != "plate":
                continue
            counts["plates"] += 1
            if world["use"] in PLATE_USES:
                lines.append(f"INFO {float(row[0]):6.2f}-{float(row[1]):6.2f} · plate {world['object']} · use={world['use']}")
            else:
                counts["plates_unnamed"] += 1
                lines.append(f"WARN {float(row[0]):6.2f}-{float(row[1]):6.2f} · plate {world['object']} · no named use"
                             f" (E61: a plate is a landing surface, a bridge or a reset, and says which)")
    return lines, counts


# ---------------------------------------------------------------- the compiler's `when`
def render_when_md() -> str:
    out = ["| kind | when (the sentence that calls for it) |", "|---|---|"]
    for kind in B.SPECIES_KINDS:
        out.append(f"| `{kind}` | {B.SPECIES_WHEN[kind]} |")
    for verb in B.CHART_TO_KINDS:
        out.append(f"| `chart_to` -> `{verb}` | {B.CHART_TO_WHEN[verb]} |")
    return "\n".join(out) + "\n"


def doc_block(text: str) -> tuple[int, int]:
    a, b = text.index(DOC_BEGIN) + len(DOC_BEGIN), text.index(DOC_END)
    return a, b


def sync_doc(write: bool) -> bool:
    """True when the map's s4 block equals the compiler's rendering (after writing, when asked)."""
    text = MAP_DOC.read_text(encoding="utf-8")
    a, b = doc_block(text)
    want = "\n" + render_when_md()
    if text[a:b] == want:
        return True
    if write:
        MAP_DOC.write_text(text[:a] + want + text[b:], encoding="utf-8")
        return True
    return False


# ---------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("project", nargs="?", type=Path, help="the project dir (SHOT-TABLE-SHORT.py + <build>/timeline.json)")
    ap.add_argument("--build", default=None, help=f"the build dir under the project (default {DEFAULT_BUILD})")
    ap.add_argument("--table", type=Path, default=None)
    ap.add_argument("--words", type=Path, default=None, help="a timeline.json with `sentences`")
    ap.add_argument("--long", action="store_true", help="apply E61's plate-use check regardless of runtime")
    ap.add_argument("--propose", action="store_true",
                    help="after the report, a DRAFT ROW per available species for every sentence with an act and no "
                         "row - candidates for the author to keep or delete; it writes no table and chooses nothing")
    ap.add_argument("--when", action="store_true", help="print the compiler's `when` on every kind")
    ap.add_argument("--md", action="store_true", help="with --when: as a Markdown table")
    ap.add_argument("--write-doc", action="store_true", help="regenerate SPECIES-BY-SENTENCE.md s4 from the compiler")
    ap.add_argument("--check-doc", action="store_true", help="exit 1 when SPECIES-BY-SENTENCE.md s4 is stale")
    args = ap.parse_args(argv)
    if args.write_doc or args.check_doc:
        ok = sync_doc(write=args.write_doc)
        print(f"{MAP_DOC.name}: SPECIES_WHEN block {'written' if args.write_doc else ('in sync' if ok else 'STALE - run --write-doc')}")
        return 0 if ok else 1
    if args.when:
        if args.md:
            print(render_when_md(), end="")
        else:
            for kind in B.SPECIES_KINDS:
                print(f"{kind:12s} {B.SPECIES_WHEN[kind]}")
            for verb in B.CHART_TO_KINDS:
                print(f"chart_to:{verb:8s} {B.CHART_TO_WHEN[verb]}")
        return 0
    if args.project is None:
        ap.print_usage()
        return 2
    try:
        lines, _ = report(args.project, args.build, args.table, args.words, args.long)
        if args.propose:      # P53 T8: APPENDED - the report above stays byte for byte what it was
            lines += propose(args.project, args.build, args.table, args.words)[0]
    except (FileNotFoundError, ValueError) as exc:
        print(f"lint_species_choice: {exc}", file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

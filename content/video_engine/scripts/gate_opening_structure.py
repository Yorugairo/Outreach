"""OPENING-STRUCTURE GATE - the first ~5 minutes, every required beat of the
doc-38 / P1 / P2 shape, as a real gate (exit 1), not a "by hand" row.

Operator ruling 2026-09-02, after the Steel and Paper retention read: "the
structure of the first 1-2 minutes is going to matter more than anything.
Every single pattern that our document says is required in the structure for
those first ~5 minutes needs to hit." The audit checked A1-A3, CTAs, marks and
the tell; the rest of the P1/P2 roster was "by hand", and by hand the promise
landed after 0:60 with nothing to stop it.

TWO LAYERS, FUSED (FULL-VIDEO-MAP: "the classical six-phase architecture,
the integral, fused with the platform micro-rules, the differentials"):

  CLASSICAL (doc 32 s4-s6, LLM-CONTEXT-CLASSICAL, doc 38 s2) - the nodes that
  fall inside the opening:
    Truby      Weakness/Need planted AS PEOPLE (P1 B3) -> Desire + Opponent
               named (P1 B5) -> Plan v1 = the head-fake, planted straight
               (P2) -> Plan v1 tried and FAILS = the Debate (P2, as a gap)
    McKee      the gap opens at the microhook (line 2 violates line 1);
               BUT/THEREFORE is the gap's sentence-level shadow; archetype
               not stereotype; antagonism = a mechanism; inciting incident
    Snyder     Catalyst (P2 start, as a closed micro loop) + Debate
    Glass      anecdote <-> reflection alternation (80/20 P1, 70/30 P2)
    Humes      pre-opener (visual breath), post-key on the 8s boundary,
               pre-key before the promise
    Rhetoric   one tricolon on the thesis line; anaphora debut/recurrence
    Ring       token planted (P1), touched once unresolved (P2)
    A/V        irony counterpoint (P1), contextual mapping (P2) - JUDGE rows
  Truby Battle / Self-Revelation / New Equilibrium, Snyder's midpoint, the
  chiastic center and the ring CLOSE belong to P4-P6 and are NOT gated here.

  PLATFORM (doc 31 via the map): 3s microhook, 8s decision, "you" by 0:30,
  One Minute Wall (payoff 30-60 then the promise), rehooks A1/A2/A3, new info
  every 15-30s, density bands, the dip, the one CTA slot, the retention
  clock's repeating cycle (memory youtube-retention-clock).

THREE KINDS OF CHECK, reported honestly:
  mechanical - from text + timing (a take's word times via --timeline or the
               episode's vo*/ dirs; else the kit's measured speech rate)
  declared   - the writer tags the beat (beat_tags.py) because the text has
               no signature; an undeclared required beat FAILS
  JUDGE      - only a reader can decide; printed, never silently passed
  The contract for who owns which verdict - and what the runtime agent must
  verdict by name that this gate cannot reach - is
  docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md.

GEOMETRY: P1/P2 ends and P2 density bands are read from the phase guides'
runtime tables and interpolated (P1 ~1:10, P2 ~1:10-2:46 at 13.4 min). The
platform timings inside P1 (3s, 8s, 0:30, 0:30-0:60) are absolute - "the
attention ladder is physics, not proportion" (MAP s1); beat 5 (desire /
opponent / map / A2 / ring) runs from 0:60 to P1's end and MERGES into beat 4
when P1 ends before 0:60 (P1.md: "compress beats, never drop them").

DOCTRINE CONFLICT RESOLVED (ruling E23, 2026-09-02): P2.md and MAP s4 put A3
at ~10% of runtime; the audit used to hard-code 180s absolute. Both tools now
take A3 from kit_spec.a3_anchor_s (10% of runtime; 3:00 is the @30:00 column,
not a constant). The operator's rider - "the next microhook and the cycle
continues ... should already be self-healing regardless of when the hook
lands" - is made mechanical past the opening: G36 runs the cycle check over
the whole runtime (--cycle-s, default = runtime) and G44 requires one
rehook-family line or [rehook] inside every P3/P5 unit window
(kit_spec.unit_windows).

OPENING-MINUTE GATES (ruling E24, doc 29 s9.29 - an analyst's drop-off review the
operator verified against analytics): G45 the packaging echo - the first spoken
sentence must ANSWER THE THUMBNAIL; the title's content words are the mechanical
proxy (the title ships with the thumbnail), J12 prints the thumbnail path so the
agent reads sentence 1 against it; G09 WARNs a promise after 0:45 (DECISION R7
against doc 38's window to 0:60). The screen-side rows M10/M11 live in
gate_motion_density.py.

    python gate_opening_structure.py SCRIPT.txt [--timeline build-f/timeline.json]
           [--counterparty Bravos] [--ring spike] [--opening-s 300] [--cycle-s 805]
           [--title "<locked title>"] [--thumb "<thumbnail words>"] [--thumb-file <png>]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_script_doctrine as A          # noqa: E402  (shared helpers/regexes)
import beat_tags                            # noqa: E402
import kit_spec                             # noqa: E402  (A3 anchor, unit windows - one owner)

DOCS = Path(__file__).resolve().parents[3] / "docs/content-video-engine"
P1_GUIDE = DOCS / "patterns/phase-guides/P1.md"
P2_GUIDE = DOCS / "patterns/phase-guides/P2.md"

# ---- constants quoted from the docs ---------------------------------------
GRAB_S = 3.0                    # 38 B1 / P1 QC
BREATH_S = (0.5, 0.8)           # 38 B1: plate breathes before the first word (Humes pre-opener, bent visual)
BREATH_TOL = 0.2
PARADOX_BY_S = 8.0              # 38 B2: [post-key] ON the 8-second boundary
ARCHETYPE_WIN = (8.0, 30.0)     # 38 B3: the world opens 0:08-0:30; W&N as people
YOU_BY_S = 30.0                 # 38 B3 / P1 QC
STAKES_BY_S = 30.0              # 38 B3: stakes named by ~0:25 (tolerance to 0:30)
PROMISE_WIN = (30.0, 45.0)      # 38 B4 / MAP s3 / CLK: mini-payoff FIRST, then the promise - by 0:45 (E24 DECIDED 2026-09-03: the
                                # analyst's roadmap-by-0:45 wins over doc 38's 0:60; the analytics drop lands 0:45-1:00)
ROADMAP_S = PROMISE_WIN[1]      # kept as a name for the report text
BEAT5_START = 60.0              # 38 B5: the map, desire, opponent, A2, ring - 0:60 to P1 end
A2_ANCHOR = 60.0                # 38 B5 / P1 QC
# A3 = kit_spec.a3_anchor_s(runtime): P2.md / MAP s4 QC, A3 + F2 at ~10% of runtime (E23; shared with the audit)
REHOOK_TOL = A.REHOOK_TOLERANCE_S
NEW_INFO_MAX_GAP_S = 30.0       # P2: something genuinely new every 15-30s
CATALYST_WITHIN_S = 60.0        # P2: catalyst lands in the phase's first ~60s, closed inside 30-60s
DEBATE_FROM = 0.40              # P2: "the debate (mid-late phase)"
SIGNPOST_FROM = 0.75            # P2: "exit on a transition signpost into the gap phase"
DIP_WITHIN_S = 15.0             # P2: "Immediately after" the macro close
DIP_MIN_GAP_S = 2.0             # P2: "2-3 beats of visual room tone, no narration push"
CTA_WINDOW_S = 30.0             # P2: "inside the 15-30 seconds after the macro payoff"
MARKS_PER_MIN_MAX = A.BREAK_RATION_MAX
P2_MARKS_MAX = 3                # P2: "Ration: <=3 marks in this phase"
CYCLE_MAX_GAP_S = 60.0          # CLK: the cycle repeats per beat (roster: 30-60s cadence)
CONCESSION_MAX_S = 10.0         # U6
CONCESSION_MAX_SENTS = 2        # U6
EST_TOL = 1.0 + A.TIMING_SPREAD_WARN

AGREEMENT = re.compile(
    r"\b(agree|agreement|on the record|credit where due|is real\b|they'?re right|"
    r"the most honest|sharpest|rightly|fair point|to be fair|can'?t argue)\b", re.I)
HEDGE = re.compile(
    r"\b(no threshold|not yet|for this channel|reading it together|too early|"
    r"hard to say|we'?ll see|remains to be seen|one quarter at a time|"
    r"no way to know|time will tell)\b", re.I)
OUR_CLAIM = re.compile(r"\b(I|we)\s+(ran|pulled|checked|drew|measured|counted|"
                       r"found|traced|underwrote|disagree|went further)\b", re.I)
NUMBER = re.compile(r"\b(\d[\d,.]*%?|one|two|three|four|five|six|seven|eight|nine|"
                    r"ten|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
                    r"hundred|thousand|million|billion|trillion|percent|cents?|"
                    r"half|third|quarter)\b", re.I)
CALCULABLE = re.compile(r"\b(by the end|in the next|minutes?|seconds?|thirty seconds|"
                        r"calculate|run it yourself|check(?: it)? yourself|your own)\b", re.I)
AND_THEN = re.compile(r"^(and then|then)\b", re.I)
# McKee: BUT/THEREFORE - the connectors that mark a gap opening or a consequence
TURN_CONNECTOR = re.compile(r"^(but|so|because|which is why|therefore|yet|instead|"
                            r"except|and that'?s (?:where|why)|and here'?s)\b", re.I)
CHANNEL_TALK = re.compile(r"\b(this channel|my channel|the channel|on this channel)\b", re.I)
BIO = re.compile(r"\b(I worked (?:at|in)|I used to|JPMorgan|I own(?:ed)?|my dispensary|risk-scor)\w*", re.I)
# E24 / doc 29 s9.29 (G45): the packaging's CONTENT words - title + thumbnail text minus these -
# must be echoed by the first spoken sentence (the confirmation gap: the sentence states the thesis
# the packaging implied). Function words carry no thesis, so they never count as an echo.
PACKAGING_STOPWORDS = frozenset(
    "the a an is are was were be been am of and or but not no nor what who why how when where which "
    "that this these those it its in on at to for from by with as into than then so if you your yours "
    "we our i my me he she they them their his her do does did done has have had can could will would "
    "should may might just only also very there here about over under out up down off all any some "
    "every each more most much many still yet again ever never now".split())
PACKAGING_MIN_STEM = 2          # E24 G45: "AI" is a two-letter content word
PACKAGING_PREFIX_MIN = 4        # E24 G45: crude stems match by prefix ("surviv" / "survive") from four letters
SRC_G45 = ("E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - "
           "the title is the words packaged with it")
SRC_J12 = "E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it"


@dataclass(frozen=True)
class Gate:
    id: str
    src: str          # classical node + doc reference
    level: str        # FAIL | WARN | PASS | JUDGE | INFO
    message: str


# ---- geometry from the phase guides ---------------------------------------
def _clock(s: str) -> float:
    m, _, sec = s.strip().partition(":")
    return int(m) * 60 + int(sec or 0)


def _phase_table(path: Path) -> list[tuple[float, float, float, str]]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*<?\s*(\d+)\s*min\s*\|\s*~?(\d+:\d+)\s*[–-]\s*(\d+:\d+)[^|]*\|(.*)", line)
        if m:
            rows.append((float(m.group(1)), _clock(m.group(2)), _clock(m.group(3)), m.group(4)))
    return rows


def _interp(points: list[tuple[float, float]], x: float) -> float:
    pts = sorted(points)
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def geometry(runtime_s: float) -> dict:
    mins = runtime_s / 60.0
    p1 = _phase_table(P1_GUIDE) or [(30, 0, 90, ""), (16, 0, 75, ""), (8, 0, 60, ""), (5, 0, 35, "")]
    p2 = _phase_table(P2_GUIDE) or [(30, 90, 300, "4–6 · 7–14"), (16, 75, 180, "3–4 · 5–8"),
                                    (8, 60, 135, "2–3 · 4–6"), (5, 35, 65, "")]
    p1_end = _interp([(r, e) for r, _, e, _ in p1], mins)
    p2_end = _interp([(r, e) for r, _, e, _ in p2], mins)
    bands = {}
    for r, _, _, extra in p2:
        m = re.search(r"(\d+)\s*[–-]\s*(\d+)\D+(\d+)\s*[–-]\s*(\d+)", extra)
        if m:
            bands[r] = tuple(int(g) for g in m.groups())
    def band(i):
        pts = [(r, v[i]) for r, v in bands.items()]
        return round(_interp(pts, mins)) if pts else None
    return {"p1_end": p1_end, "p2_end": max(p2_end, p1_end + 30.0),
            "loops": (band(0), band(1)), "new": (band(2), band(3)),
            "source": "phase guides" if _phase_table(P1_GUIDE) else "fallback constants"}


# ---- text -> timed sentences + marks -------------------------------------
def _sentences_timed(text: str, timeline: list[dict] | None):
    bounds = []
    for m in re.finditer(r"[^.!?]*[.!?]+(?:\s+|$)", text, re.S):
        clean = beat_tags.strip_marks(m.group(0))
        clean = re.sub(r"^\s*(?:#|\||>|---|```).*$", "", clean, flags=re.M)
        clean = re.sub(r"\s+", " ", clean).strip()
        if clean:
            bounds.append((m.start(), clean))
    out = []
    if timeline:
        words = [w for w in timeline if re.search(r"[A-Za-z0-9]", w["w"])]
        wi = 0
        for off, s in bounds:
            n = len(re.findall(r"[A-Za-z0-9'%$]+", s))
            seg = words[wi:wi + n]
            if not seg:
                break
            out.append((seg[0]["start"], seg[-1]["end"], s, off))
            wi += n
        return out
    t = 0.0
    for off, s in bounds:
        d = A.secs(s)
        out.append((t, t + d, s, off))
        t += d
    return out


def _time_of(off: int, sents) -> float | None:
    host = None
    for st, en, s, o in sents:
        if o <= off:
            host = (st, en, s, o)
        else:
            if host is None:
                host = (st, en, s, o)
            break
    return host[0] if host else None


def _sentence_index_of(off: int, sents) -> int:
    idx = 0
    for i, (_, _, _, o) in enumerate(sents):
        if o <= off:
            idx = i
    return idx


def _first_alnum(text: str, chunk_off: int) -> int:
    lead = re.search(r"[A-Za-z0-9]", text[chunk_off:])
    return chunk_off + (lead.start() if lead else 0)


# ---- E24 G45: packaging echo -------------------------------------------------
def _stem(word: str) -> str:
    """Crude stem (E24 G45): strip one trailing ing / ed / es / s, never below three letters."""
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _stems(text: str) -> list[str]:
    return [_stem(t.replace("'", "")) for t in re.findall(r"[a-z][a-z']*", text.lower())]


def _stem_match(a: str, b: str) -> bool:
    if a == b:
        return True
    return min(len(a), len(b)) >= PACKAGING_PREFIX_MIN and (a.startswith(b) or b.startswith(a))


def packaging_words(title: str | None, thumb: str | None) -> list[str]:
    """The packaging's content-word stems, in order, deduplicated (E24 G45)."""
    out: list[str] = []
    for raw in re.findall(r"[a-z][a-z']*", f"{title or ''} {thumb or ''}".lower()):
        word = raw.replace("'", "")
        stem = _stem(word)
        if word in PACKAGING_STOPWORDS or len(stem) < PACKAGING_MIN_STEM or stem in out:
            continue
        out.append(stem)
    return out


def _echoed(sentence: str, words: list[str]) -> list[str]:
    toks = _stems(sentence)
    return [w for w in words if any(_stem_match(w, t) for t in toks)]


def _packaging_gates(sents, title: str | None, thumb: str | None, thumb_file: str | None) -> list[Gate]:
    """G45 (mechanical proxy) + J12 (JUDGE): the first sentence answers the thumbnail (E24 / doc 29 s9.29)."""
    out: list[Gate] = []
    if not (title or thumb):
        out.append(Gate("G45", SRC_G45, "INFO", "no --title given, G45 not run"))
    else:
        words = packaging_words(title, thumb)
        first = _echoed(sents[0][2], words) if sents else []
        second = _echoed(sents[1][2], words) if len(sents) > 1 else []
        if first:
            out.append(Gate("G45", SRC_G45, "PASS", f"title-word proxy: {first} echoed in sentence 1"))
        elif second:
            out.append(Gate("G45", SRC_G45, "WARN", f"title-word proxy: {second} only in sentence 2 - "
                            "the first sentence should state the thesis the packaging implied"))
        else:
            out.append(Gate("G45", SRC_G45, "FAIL", f"title-word proxy: none of {words} in the first two sentences - "
                            "the first sentence must answer the thumbnail"))
    where = f"open {thumb_file}" if thumb_file else "no --thumb-file given - open the FINAL thumbnail"
    line = f"; sentence 1: '{sents[0][2][:80]}'" if sents else ""
    out.append(Gate("J12", SRC_J12, "JUDGE", where + line))
    return out


# ---- the gate ---------------------------------------------------------------
def run(text: str, timeline: list[dict] | None = None, counterparty: str | None = None,
        ring: str | None = None, opening_s: float = 300.0,
        cycle_s: float | None = None, title: str | None = None, thumb: str | None = None,
        thumb_file: str | None = None) -> tuple[list[Gate], dict]:
    """cycle_s: how far G36's cycle check runs; None = the whole runtime (E23).
    title / thumb: the packaging's words for G45; thumb_file: the thumbnail path J12 prints (E24)."""
    sents = _sentences_timed(text, timeline)
    marks = beat_tags.find_marks(text)
    beats: dict[str, list[tuple[float, int]]] = {}
    for tag, off in marks:
        if tag in beat_tags.BEAT_TAGS:
            t = _time_of(off, sents)
            if t is not None:
                beats.setdefault(tag, []).append((t, _sentence_index_of(off, sents)))
    runtime = sents[-1][1] if sents else 0.0
    geo = geometry(runtime)
    p1_end, p2_end = geo["p1_end"], geo["p2_end"]
    tol = 1.0 if timeline else EST_TOL
    beat5_lo = min(BEAT5_START, p1_end * 0.67)          # merge rule below 8 min
    g: list[Gate] = []
    add = lambda i, src, lvl, m: g.append(Gate(i, src, lvl, m))
    mmss = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
    in_p1 = lambda t: t <= p1_end * tol
    in_p2 = lambda t: p1_end / tol <= t <= p2_end * tol
    first_beat = lambda tag: (beats.get(tag) or [(None, None)])[0][0]
    tag_times = lambda tag: [t for t, _ in beats.get(tag, [])]
    tag_idx = lambda tag: [i for _, i in beats.get(tag, [])]
    rehook_hits = lambda lo, hi: sorted(set(
        [st for st, _, s, _ in sents if lo <= st <= hi and re.search("|".join(A.REHOOKS), s, re.I)]
        + [t for t in tag_times("rehook") if lo <= t <= hi]))

    # ================= P1 - THE OPEN =================
    if sents:
        d = sents[0][1] - sents[0][0]
        add("G01", "PLATFORM 3s microhook (38 B1 / P1 QC)", "FAIL" if d > GRAB_S * tol else "PASS", f"first sentence {d:.2f}s")
        add("J03", "Rhetoric: microhook concrete, terminal stress on the surprising word (38 B1)", "JUDGE", f"'{sents[0][2][:80]}'")
    g += _packaging_gates(sents, title, thumb, thumb_file)      # E24: G45 proxy + J12
    if timeline:
        t0 = sents[0][0] if sents else 0.0
        ok = BREATH_S[0] - BREATH_TOL <= t0 <= BREATH_S[1] + BREATH_TOL
        add("G02", "Humes pre-opener, bent visual: the plate breathes 0.5-0.8s before the first word (38 B1 / doc 32 s7)",
            "PASS" if ok else "FAIL", f"first word at {t0:.2f}s in the edit clock")
    else:
        add("G02", "Humes pre-opener, bent visual: plate breathes 0.5-0.8s before the first word", "INFO", "edit-clock property - checked with --timeline")
    if len(sents) > 1:
        e = sents[1][1]
        pk_by_boundary = []
        for m, o in marks:
            if m != "post-key":
                continue
            k = _sentence_index_of(o, sents)
            if k >= 1 and o < _first_alnum(text, sents[k][3]):
                k -= 1                      # a mark leading chunk k settles sentence k-1
            host_end = sents[k][1] if k < len(sents) else 1e9
            if k >= 1 and host_end <= PARADOX_BY_S * tol:
                pk_by_boundary.append(host_end)
        lvl = "PASS" if (e <= PARADOX_BY_S * tol and pk_by_boundary) else "FAIL"
        why = [] if e <= PARADOX_BY_S * tol else [f"paid at {e:.2f}s (> 8s)"]
        if not pk_by_boundary:
            why.append("no [post-key] settle by the 8s boundary")
        add("G03", "McKee gap paid WRONG by 0:08 + Humes post-key ON the boundary (38 B2)", lvl,
            "; ".join(why) or f"paid at {e:.2f}s, settle at {pk_by_boundary[0]:.2f}s")
        add("J05", "McKee: the gap opens - line 2 violates line 1's expected consequence (38 B1-B2)", "JUDGE",
            f"'{sents[0][2][:50]}' -> '{sents[1][2][:50]}'")
    ban = [st for st, _, s, _ in sents if st <= YOU_BY_S and (re.search("|".join(A.GREETINGS), s, re.I) or CHANNEL_TALK.search(s))]
    add("G04", "PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)", "FAIL" if ban else "PASS",
        f"banned construction at {mmss(ban[0])}" if ban else "clean")
    ty = next((st for st, _, s, _ in sents if st <= YOU_BY_S * tol and re.search(r"\byou(?:r|'ll|'re|'ve)?\b", s, re.I)), None)
    add("G05", "Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)", "PASS" if ty is not None else "FAIL",
        f"'you' at {mmss(ty)}" if ty is not None else "no 'you' before 0:30")
    par_end = sents[1][1] if len(sents) > 1 else 0.0
    early_bio = [st for st, _, s, _ in sents if st < par_end and BIO.search(s)]
    add("G06", "Biography as the twist - AFTER the paradox, never before (38 B3)", "FAIL" if early_bio else "PASS",
        f"biography at {mmss(early_bio[0])} precedes the paradox" if early_bio else "clean")
    # Truby Weakness/Need planted AS PEOPLE - McKee archetype in a specific setting
    ta = [t for t in tag_times("archetype") if ARCHETYPE_WIN[0] / tol <= t <= ARCHETYPE_WIN[1] * tol]
    add("G37", "Truby Weakness/Need planted AS PEOPLE: an archetype-in-a-setting enters 0:08-0:30 (38 B3 / MAP s3)",
        "PASS" if ta else "FAIL", f"[archetype] at {mmss(ta[0])}" if ta else "no [archetype] declared in 0:08-0:30")
    if ta:
        add("J09", "McKee archetype, not stereotype: a universal experience in a specific setting (doc 32 s4)", "JUDGE", f"read the line at {mmss(ta[0])}")
    ts = first_beat("stakes")
    add("G07", "Hook anatomy: stakes named by ~0:25 (38 B3)", "PASS" if ts is not None and ts <= STAKES_BY_S * tol else "FAIL",
        f"[stakes] at {mmss(ts)}" if ts is not None else "no [stakes] declared by 0:30")
    t_pr_tag = first_beat("promise")
    t_pr_rx = next((st for st, _, s, _ in sents if re.search(A.A1_PROMISE, s, re.I)), None)
    t_pr = t_pr_tag if t_pr_tag is not None else t_pr_rx
    pr_sent = next(((st, en, s, o) for st, en, s, o in sents if st == t_pr), None) if t_pr is not None else None
    t_po = first_beat("payoff")
    if t_po is None:
        add("G08", "One Minute Wall: real value FIRST, before the ask (38 B4)", "FAIL", "no [payoff] declared before the promise")
    elif t_pr is not None and t_po > t_pr:
        add("G08", "One Minute Wall: real value FIRST, before the ask (38 B4)", "FAIL", f"[payoff] at {mmss(t_po)} comes AFTER the promise at {mmss(t_pr)}")
    else:
        add("G08", "One Minute Wall: real value FIRST, before the ask (38 B4)", "PASS", f"[payoff] at {mmss(t_po)}")
    src9 = "F1 + A1 + macro-loop-1 SETUP: the dated promise in 0:30-0:45 (38 B4 / MAP s3 / CLK; E24 roadmap by 0:45)"
    if t_pr is None:
        add("G09", src9, "FAIL", "no promise found (tag [promise] or a 'by the end you'll...' line)")
    elif t_pr > PROMISE_WIN[1] * tol:
        add("G09", src9, "FAIL", f"promise at {mmss(t_pr)} - AFTER 0:45 (E24, decided 2026-09-03; Steel and Paper as recorded: 1:20)")
    elif t_pr < PROMISE_WIN[0] / tol:
        add("G09", src9, "WARN", f"promise at {mmss(t_pr)} - before the mini-payoff window opens")
    else:
        add("G09", src9, "PASS", f"promise at {mmss(t_pr)}")
    if pr_sent:
        has_prekey = any(m == "pre-key" and pr_sent[3] - 20 <= o < _first_alnum(text, pr_sent[3]) for m, o in marks)
        add("G10", "Humes pre-key immediately before the promise (P1 pause marks)", "PASS" if has_prekey else "FAIL", "placed" if has_prekey else "missing")
        calc = bool(NUMBER.search(pr_sent[2]) or CALCULABLE.search(pr_sent[2]))
        add("G11", "The promise carries a date or number and is calculable (38 B4 / doc 35)", "PASS" if calc else "FAIL", f"'{pr_sent[2][:70]}'")
    tri1 = [t for t in tag_times("tricolon") if in_p1(t)]
    add("G12", "Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1 (P1 B4 / doc 32 s3)", "PASS" if len(tri1) == 1 else "FAIL", f"{len(tri1)} declared in P1")
    add("J08", "Rhetoric: phonetic anchor only on the promise/payoff/tell (doc 32 s3)", "JUDGE", "read the promise line")
    a2 = rehook_hits(A2_ANCHOR - 5, max(p1_end, A2_ANCHOR) * tol + 5)
    add("G13", "PLATFORM rehook A2 ~1:00, template family (38 B5 / P1 QC)", "PASS" if a2 else "FAIL",
        f"A2 at {mmss(a2[0])}" if a2 else f"no rehook construction in 0:55-{mmss(p1_end)}")
    # Truby Desire + Opponent, the map signpost - beat 5
    tdes = [t for t in tag_times("desire") if beat5_lo / tol <= t <= p1_end * tol]
    add("G38", "Truby Desire named: the goal the video pursues (38 B5)", "PASS" if tdes else "FAIL",
        f"[desire] at {mmss(tdes[0])}" if tdes else f"no [desire] declared in {mmss(beat5_lo)}-{mmss(p1_end)}")
    top = [t for t in tag_times("opponent") if in_p1(t)]
    if not top:
        add("G14", "Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)", "FAIL", "no [opponent] declared in P1")
    else:
        add("G14", "Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)", "PASS", f"[opponent] at {mmss(top[0])}")
        add("J01", "McKee antagonism: the opponent is a mechanism, not a villain", "JUDGE", f"read the [opponent] line at {mmss(top[0])}")
    tmap = [t for t in tag_times("map") if beat5_lo / tol <= t <= p1_end * tol]
    add("G39", "Auditory handrail: map-not-territory signpost - tease the WHAT, hold the HOW (38 B5 / doc 32 s1)",
        "PASS" if tmap else "FAIL", f"[map] at {mmss(tmap[0])}" if tmap else "no [map] declared in beat 5")
    if tmap:
        add("J10", "38 B5: the map is a journey tease, never a table of contents", "JUDGE", f"read the line at {mmss(tmap[0])}")
    if ring:
        rx = re.compile(r"\b" + re.escape(ring) + r"s?\b", re.I)
        r1 = [st for st, _, s, _ in sents if in_p1(st) and rx.search(s)]
        add("G15", "Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)", "PASS" if r1 else "FAIL",
            f"'{ring}' planted at {mmss(r1[0])}" if r1 else f"'{ring}' never mentioned in P1")
    else:
        rg = [t for t in tag_times("ring") if in_p1(t)]
        add("G15", "Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)", "PASS" if rg else "FAIL",
            f"[ring] at {mmss(rg[0])}" if rg else "no ring token (pass --ring <object> or tag [ring])")
    rf1 = [t for t in tag_times("reflect") if in_p1(t)]
    add("G16", "Glass alternation, P1 80/20: exactly ONE reflection dab (P1)", "PASS" if len(rf1) == 1 else "FAIL", f"{len(rf1)} [reflect] in P1")
    trail = [st for st, _, s, _ in sents if st <= opening_s and re.search("|".join(A.TRAILING_ATTR), s)]
    vf_bad = [o for m, o in marks if m == "verify" and (_sentence_index_of(o, sents) == 0 or (pr_sent and _sentence_index_of(o, sents) == sents.index(pr_sent)))]
    add("G17", "HARD GATE attribution-first; [verify] never in hook/promise (P1/P2 / doc 32 s1)", "FAIL" if (trail or vf_bad) else "PASS",
        ((f"trailing attribution at {mmss(trail[0])}" if trail else "") + ("; [verify] in hook/promise" if vf_bad else "")) or "clean")
    n1 = sum(1 for m, o in marks if m in ("pre-key", "post-key") and (_time_of(o, sents) or 0) <= p1_end)
    per_min = n1 / max(p1_end / 60.0, 1e-9)
    add("G18", "Humes pauses rationed: ~three per minute maximum (P1)", "FAIL" if per_min > MARKS_PER_MIN_MAX else "PASS", f"{n1} marks in P1 ({per_min:.1f}/min)")
    add("J06", "A/V irony counterpoint: the image TENSIONS the line, never illustrates it (38 B1 / doc 32 s6) - check the plate plan", "JUDGE", "P1")

    # ================= P2 - THE ENGINE =================
    loops = [t for t in tag_times("loop") if in_p2(t)]
    news = [t for t in tag_times("new") if in_p2(t)]
    tcat = [t for t in tag_times("catalyst") if p1_end / tol <= t <= (p1_end + CATALYST_WITHIN_S) * tol]
    if not tcat:
        add("G40", "Snyder Catalyst / McKee inciting incident: the fact that makes the question urgent lands as a story beat in P2's first ~60s (P2)", "FAIL",
            "no [catalyst] declared in the phase's first 60s")
    else:
        closed = [t for t in loops if tcat[0] <= t <= (tcat[0] + CATALYST_WITHIN_S) * tol]
        add("G40", "Snyder Catalyst / McKee inciting incident: lands as a story beat in P2's first ~60s (P2)", "PASS", f"[catalyst] at {mmss(tcat[0])}")
        add("G19", "The catalyst is a micro loop CLOSED inside 30-60s, not exposition (P2)", "PASS" if closed else "FAIL",
            f"closed by [loop] at {mmss(closed[0])}" if closed else f"no [loop] within 60s of the catalyst at {mmss(tcat[0])}")
    if news:
        pts = [p1_end] + news
        worst = max(b - a for a, b in zip(pts, pts[1:]))
        add("G20", "PLATFORM new-info cadence: something genuinely new every 15-30s (P2)", "FAIL" if worst > NEW_INFO_MAX_GAP_S * tol else "PASS", f"longest gap {worst:.0f}s")
    else:
        add("G20", "PLATFORM new-info cadence: something genuinely new every 15-30s (P2)", "FAIL", "no [new] beats declared in P2")
    lo_l, hi_l = geo["loops"]; lo_n, hi_n = geo["new"]
    if lo_l is not None:
        add("G21", f"L2 loops: {lo_l}-{hi_l} micro-loop closes at this runtime (P2 geometry / MAP s0)", "PASS" if lo_l <= len(loops) <= hi_l else "FAIL", f"{len(loops)} [loop] in P2")
    if lo_n is not None:
        add("G22", f"PLATFORM density: {lo_n}-{hi_n} new-info beats at this runtime (P2 geometry)", "PASS" if lo_n <= len(news) <= hi_n else "FAIL", f"{len(news)} [new] in P2")
    p2s = [(st, s) for st, _, s, _ in sents if in_p2(st)]
    chain = any(AND_THEN.match(a[1]) and AND_THEN.match(b[1]) for a, b in zip(p2s, p2s[1:]))
    add("G23", "McKee gap, sentence-level: BUT/THEREFORE only - zero AND-THEN chains (P2 / doc 32 s4)", "FAIL" if chain else "PASS", "chain found" if chain else "clean")
    # McKee: each loop/new beat should TURN on a gap or consequence connector
    beat_idx = sorted(set(tag_idx("loop") + tag_idx("new") + tag_idx("catalyst")))
    beat_idx = [i for i in beat_idx if i < len(sents) and in_p2(sents[i][0])]
    turned = [i for i in beat_idx if TURN_CONNECTOR.match(sents[i][2]) or (i + 1 < len(sents) and TURN_CONNECTOR.match(sents[i + 1][2]))]
    if beat_idx:
        share = len(turned) / len(beat_idx)
        add("G43", "McKee gap: beats connect by BUT/THEREFORE - a beat that could swap places is filler (P2 / doc 32 s4)",
            "WARN" if share < 0.5 else "PASS", f"{len(turned)}/{len(beat_idx)} declared beats open on a gap/consequence connector")
    hf = [t for t in tag_times("head-fake") if in_p2(t)]
    early = p1_end + 0.6 * (p2_end - p1_end)
    if not hf:
        add("G24", "Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)", "FAIL", "no [head-fake] declared in P2")
    elif hf[0] > early * tol:
        add("G24", "Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)", "FAIL", f"[head-fake] at {mmss(hf[0])} - late (by {mmss(early)})")
    else:
        add("G24", "Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)", "PASS", f"[head-fake] at {mmss(hf[0])}")
        add("J02", "P2: the head-fake is offered STRAIGHT, no wink; demolition reserved for the pivot", "JUDGE", f"read the line at {mmss(hf[0])}")
    # Snyder Debate / Truby Plan v1 FAILS - shown as a gap
    deb_lo = p1_end + DEBATE_FROM * (p2_end - p1_end)
    tdeb = [t for t in tag_times("debate") if deb_lo / tol <= t <= p2_end * tol and (not hf or t > hf[0])]
    add("G41", "Snyder Debate / Truby Plan v1 FAILS: the obvious answer tried and found wanting, after the head-fake, mid-late P2 (P2 / MAP s4)",
        "PASS" if tdeb else "FAIL", f"[debate] at {mmss(tdeb[0])}" if tdeb else "no [debate] declared after the head-fake in mid-late P2")
    if tdeb:
        add("J11", "McKee: the plan fails as a GAP (an action whose result violates expectation), never as a lecture", "JUDGE", f"read the line at {mmss(tdeb[0])}")
    a3c = kit_spec.a3_anchor_s(runtime)
    a3 = rehook_hits(a3c - REHOOK_TOL, a3c + REHOOK_TOL)
    add("G25", f"PLATFORM rehook A3 at ~10% of runtime = {mmss(a3c)} (P2 / MAP s4 QC; audit and gate share kit_spec.a3_anchor_s, E23)",
        "PASS" if a3 else "FAIL", f"A3 at {mmss(a3[0])}" if a3 else f"no rehook within {REHOOK_TOL:.0f}s of {mmss(a3c)}")
    f2 = [t for t in tag_times("foreshadow") if a3c - REHOOK_TOL <= t <= a3c + REHOOK_TOL]
    add("G26", "Foreshadow schedule F2 at ~10%: the promise sighted again, none of it delivered (P2 / MAP s2)", "PASS" if f2 else "FAIL",
        f"[foreshadow] at {mmss(f2[0])}" if f2 else "no [foreshadow] near 10%")
    if ring:
        r2 = [st for st, _, s, _ in sents if in_p2(st) and rx.search(s)]
        add("G27", "Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)", "PASS" if len(r2) == 1 else "FAIL", f"'{ring}' {len(r2)}x in P2")
    else:
        r2 = [t for t in tag_times("ring") if in_p2(t)]
        add("G27", "Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)", "PASS" if len(r2) == 1 else "FAIL", f"[ring] {len(r2)}x in P2")
    lc = [t for t in tag_times("loop-close") if in_p2(t) or t <= (p2_end + REHOOK_TOL)]
    add("G28", "Macro loop 1 CLOSES on a partial answer that opens the bigger question (P2 / MAP s4, LIFO ledger)", "PASS" if lc else "FAIL",
        f"[loop-close] at {mmss(lc[0])}" if lc else "no [loop-close] declared")
    if lc:
        t_lc = lc[0]; dip_ok, how = False, ""
        if timeline:
            ws = [w for w in timeline if re.search(r"[A-Za-z0-9]", w["w"])]
            for a, b in zip(ws, ws[1:]):
                if t_lc <= a["end"] <= t_lc + DIP_WITHIN_S and b["start"] - a["end"] >= DIP_MIN_GAP_S:
                    dip_ok, how = True, f"{b['start'] - a['end']:.1f}s of room tone at {mmss(a['end'])}"; break
        if not dip_ok:
            dd = [t for t in tag_times("dip") if t_lc <= t <= t_lc + DIP_WITHIN_S * tol]
            if dd:
                dip_ok, how = True, f"[dip] at {mmss(dd[0])}"
        add("G29", "PLATFORM breathing dip IMMEDIATELY after the macro close - 2-3 beats of room tone (P2)", "PASS" if dip_ok else "FAIL",
            how or f"no dip within {DIP_WITHIN_S:.0f}s of the macro close at {mmss(t_lc)}")
    else:
        add("G29", "PLATFORM breathing dip after the macro close (P2)", "WARN", "cannot place - macro close not declared")
    ctas = [st for st, _, s, _ in sents if st <= opening_s and re.search("|".join(A.CTA), s, re.I)]
    bad_cta = [t for t in ctas if not (lc and lc[0] <= t <= lc[0] + CTA_WINDOW_S)]
    add("G30", "PLATFORM: the ONLY mid-video CTA slot is the 15-30s after the macro payoff (P2)", "FAIL" if bad_cta else "PASS",
        f"CTA at {mmss(bad_cta[0])} outside the slot" if bad_cta else ("none" if not ctas else f"one inside the slot at {mmss(ctas[0])}"))
    tsp = [t for t in tag_times("signpost") if (p1_end + SIGNPOST_FROM * (p2_end - p1_end)) / tol <= t <= (p2_end + REHOOK_TOL)]
    add("G42", "Auditory handrail: exit P2 on a transition signpost into the Gap (P2 / doc 32 s1)", "PASS" if tsp else "FAIL",
        f"[signpost] at {mmss(tsp[0])}" if tsp else "no [signpost] declared at the end of P2")
    rf2 = sorted(i for t, i in beats.get("reflect", []) if in_p2(t))
    adj = any(b - a == 1 for a, b in zip(rf2, rf2[1:]))
    if adj:
        add("G31", "Glass alternation, P2 70/30: two consecutive reflection sentences = lecturing (P2)", "FAIL", "adjacent [reflect] dabs")
    elif loops and len(rf2) * 2 < len(loops):
        add("G31", "Glass alternation, P2 70/30: two loops with no reflection = listing (P2)", "WARN", f"{len(rf2)} dabs for {len(loops)} loops")
    else:
        add("G31", "Glass alternation, P2 70/30: dabs marked, never consecutive (P2)", "PASS", f"{len(rf2)} dabs, {len(loops)} loops")
    tri2 = [t for t in tag_times("tricolon") if in_p2(t)]
    an1 = [t for t in tag_times("anaphora") if in_p1(t)]
    an2 = [t for t in tag_times("anaphora") if in_p2(t)]
    bad = len(tri2) > 1 or (an1 and len(an2) != 1)
    add("G32", "Rhetoric: ONE momentum tricolon max in P2; anaphora (if debuted in P1) recurs exactly once (P2 / doc 32 s3)", "FAIL" if bad else "PASS",
        f"tricolon {len(tri2)}, anaphora P1 {len(an1)} / P2 {len(an2)}")
    hf_offs = [o for m, o in marks if m == "head-fake"]
    pk_before_hf = any(m == "pre-key" and any(0 <= ho - o <= 20 for ho in hf_offs) for m, o in marks)
    n2 = sum(1 for m, o in marks if m in ("pre-key", "post-key") and in_p2(_time_of(o, sents) or -1))
    add("G33", "Humes pauses in P2: no [pre-key] before the head-fake (that pause belongs to the pivot); <=3 marks in the phase", "FAIL" if (pk_before_hf or n2 > P2_MARKS_MAX) else "PASS",
        ("[pre-key] sits before the head-fake; " if pk_before_hf else "") + f"{n2} marks in P2")
    add("J07", "A/V contextual mapping: plates carry the archive, the voice carries motive and cost; a line that captions its visual fails (P2 / doc 32 s6) - check the plate plan", "JUDGE", "P2")

    # ================= cross-cutting =================
    cp = counterparty
    if not cp:
        from collections import Counter
        caps = Counter(re.findall(r"\b([A-Z][a-z]{3,})\b", " ".join(s for _, _, s, _ in sents)))
        stop = {"The", "And", "But", "That", "This", "Here", "There", "What", "When", "Then", "Today", "Count", "Nothing", "Every"}
        common = [w for w, c in caps.most_common(8) if c >= 5 and w not in stop]
        cp = common[0] if common else None
    worst, run_ = None, []
    def _flush(run_, worst):
        if run_ and (len(run_) > CONCESSION_MAX_SENTS or run_[-1][1] - run_[0][0] > CONCESSION_MAX_S):
            if worst is None or (run_[-1][1] - run_[0][0]) > (worst[-1][1] - worst[0][0]):
                return run_
        return worst
    for st, en, s, _ in sents:
        if st > opening_s:
            break
        agree = bool(AGREEMENT.search(s)) or (cp is not None and cp.lower() in s.lower())
        if agree and not OUR_CLAIM.search(s):
            run_.append((st, en, s))
        else:
            worst = _flush(run_, worst); run_ = []
    worst = _flush(run_, worst)
    add("G34", "U6 / E20 concession budget: an agreement run never exceeds 2 sentences or 10s without a claim of ours", "FAIL" if worst else "PASS",
        f"{len(worst)} sentences, {mmss(worst[0][0])}-{mmss(worst[-1][1])} ({worst[-1][1] - worst[0][0]:.0f}s): '{worst[0][2][:60]}...'" if worst else "clean")
    hedged = next(((a, b) for a, b in zip(sents, sents[1:]) if b[0] <= opening_s and NUMBER.search(a[2]) and HEDGE.search(b[2])), None)
    add("G35", "U6 / E20: a delivered proof is never hedged in the next sentence", "FAIL" if hedged else "PASS",
        f"proof at {mmss(hedged[0][0])} hedged at {mmss(hedged[1][0])}: '{hedged[1][2][:70]}'" if hedged else "clean")
    # E23: the cycle check runs the WHOLE video by default - every declared beat tag, the
    # promise, and the rehook family anywhere in the runtime is a cycle beat.
    cycle_end = min(runtime, cycle_s) if cycle_s is not None else runtime
    all_tags = [t for v in beats.values() for t, _ in v]
    cycle = sorted(set(([t_pr] if t_pr is not None else []) + loops + news + lc + rehook_hits(0, cycle_end) + all_tags
                       + tag_times("head-fake") + tag_times("catalyst") + tag_times("debate")))
    cycle = [t for t in cycle if t <= cycle_end]
    pts = [0.0] + cycle + [cycle_end]
    gaps = [(a, b - a) for a, b in zip(pts, pts[1:])]
    wg = max(gaps, key=lambda x: x[1]) if gaps else (0, 0)
    add("G36", f"CLK the cycle repeats per beat - hook / show it's worth it / promise more / deliver; no >60s without a cycle beat, 0:00-{mmss(cycle_end)} (E23: whole runtime)",
        "FAIL" if wg[1] > CYCLE_MAX_GAP_S * tol else "PASS",
        f"longest stretch without a cycle beat: {wg[1]:.0f}s from {mmss(wg[0])}")
    # E23 / P3.md u5 / MAP s9 "1/unit": every P3 and P5 unit window rehooks out
    windows = kit_spec.unit_windows(runtime)
    n_p3 = kit_spec.unit_count(runtime / 60)
    empty = [k for k, (lo, hi) in enumerate(windows, start=1) if not rehook_hits(lo / tol, hi * tol)]
    add("G44", "PLATFORM rehook per unit: one template-family line or [rehook] inside every P3/P5 unit window (P3.md u5 / P5 / MAP s9 '1 per unit'; E23)",
        "FAIL" if empty else "PASS",
        ("no rehook in " + ", ".join(f"unit {k} {mmss(windows[k - 1][0])}-{mmss(windows[k - 1][1])}" for k in empty)) if empty
        else f"all {len(windows)} unit windows rehook out")
    add("J04", "38 B5 context-dump ban: every abstraction cashed into an object or number within one sentence", "JUDGE", "read P1 B5 and the P2 catalyst")

    stats = {"runtime": mmss(runtime), "timing": "measured (take)" if timeline else "estimated (kit rate, 8% band)",
             "geometry": f"P1 0:00-{mmss(p1_end)} (beat 5 from {mmss(beat5_lo)}), P2 -{mmss(p2_end)} ({geo['source']})",
             "density_bands": f"loops {geo['loops']}, new-info {geo['new']}",
             "a3_anchor": mmss(a3c),
             "cycle": f"checked 0:00-{mmss(cycle_end)}; longest gap {wg[1]:.0f}s from {mmss(wg[0])}",
             "unit_windows": [f"{'P3' if k <= n_p3 else 'P5'} unit {k} {mmss(lo)}-{mmss(hi)}"
                              for k, (lo, hi) in enumerate(windows, start=1)],
             "counterparty": cp, "ring": ring,
             "packaging": f"title={title!r} thumb={thumb!r} thumb_file={thumb_file}",
             "not_gated_here": "Truby Battle / Self-Revelation / New Equilibrium, Snyder midpoint, chiastic center, ring CLOSE (P4-P6)",
             "beats_declared": {k: [mmss(t) for t, _ in v] for k, v in beats.items()}}
    return g, stats


def load_timeline(path: Path) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    return d["words"] if isinstance(d, dict) and "words" in d else d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path)
    ap.add_argument("--timeline", type=Path, help="build-f/timeline.json (measured word times)")
    ap.add_argument("--counterparty", help="named counterparty, e.g. Bravos")
    ap.add_argument("--ring", help="the ring token object, e.g. spike")
    ap.add_argument("--opening-s", type=float, default=300.0)
    ap.add_argument("--cycle-s", type=float, default=None,
                    help="how far G36's cycle check runs (default: the whole runtime, E23)")
    ap.add_argument("--title", help="the locked title - G45 packaging echo (E24)")
    ap.add_argument("--thumb", help="the thumbnail's words, when recorded in text (E24 G45)")
    ap.add_argument("--thumb-file", help="the FINAL thumbnail path J12 prints for the agent to open (E24)")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    text = args.script.read_text(encoding="utf-8")
    unknown = beat_tags.unknown_marks(text)
    tl = load_timeline(args.timeline) if args.timeline else A.load_timings(args.script)
    gates, stats = run(text, tl, args.counterparty, args.ring, args.opening_s, args.cycle_s,
                       args.title, args.thumb, args.thumb_file)
    if unknown:
        gates.insert(0, Gate("G00", "doc 37 marks", "FAIL", f"unknown marks would be spoken: {sorted(unknown)}"))
    print(f"=== OPENING STRUCTURE GATE: {args.script.name} ===")
    for k, v in stats.items():
        print(f"  {k:>16}: {v}")
    print()
    order = {"FAIL": 0, "WARN": 1, "PASS": 2, "INFO": 3, "JUDGE": 4}
    for x in sorted(gates, key=lambda x: (order[x.level], x.id)):
        print(f"  [{x.level:5}] {x.id} {x.message}\n          {x.src}")
    n = lambda lvl: sum(1 for x in gates if x.level == lvl)
    print(f"\nRESULT: {n('FAIL')} FAIL / {n('WARN')} WARN / {n('PASS')} PASS / {n('JUDGE')} JUDGE (read these) / {n('INFO')} INFO")
    return 1 if n("FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())

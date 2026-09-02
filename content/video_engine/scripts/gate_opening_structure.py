"""OPENING-STRUCTURE GATE - the first ~5 minutes, every required beat of the
doc-38 / P1 / P2 shape, as a real gate (exit 1), not a "by hand" row.

Operator ruling 2026-09-02, after the Steel and Paper retention read: "the
structure of the first 1-2 minutes is going to matter more than anything.
Every single pattern that our document says is required in the structure for
those first ~5 minutes needs to hit." The audit checked A1-A3, CTAs, marks and
the tell; the rest of the P1/P2 roster was "by hand", and by hand the promise
landed after 0:60 with nothing to stop it.

SOURCES (every gate quotes its line):
  38   docs/content-video-engine/38-SCRIPT-ARCHITECTURE.md s2 (beats 1-5)
  P1   docs/content-video-engine/patterns/phase-guides/P1.md
  P2   docs/content-video-engine/patterns/phase-guides/P2.md
  MAP  docs/content-video-engine/patterns/FULL-VIDEO-MAP.md s3/s4
  U6   patterns/STRENGTH-LOOP.md U6 / docs/portable/OPERATOR-RULINGS.md E20
  CLK  memory: youtube-retention-clock (3s hook / 10s answer / 30s promise /
       then the cycle repeats per beat)

THREE KINDS OF CHECK, reported honestly:
  mechanical - from text + timing (a take's word times via --timeline or
               the episode's vo*/ dirs; else the kit's measured speech rate)
  declared   - the writer tags the beat (beat_tags.py) because the text has
               no signature; an undeclared required beat FAILS
  JUDGE      - only a reader can decide (opponent = mechanism, terminal
               stress); printed, never silently passed, never counted as PASS

GEOMETRY is read from the phase guides' runtime tables and interpolated:
P1 and P2 shrink with runtime (1:30/5:00 @30m -> 1:15/3:00 @16m -> 1:00/2:15
@8m). At Steel and Paper's 13.4 min that is P1 ~1:10 and P2 ~1:10-2:46.

DOCTRINE CONFLICT SURFACED (not resolved here): P2.md and MAP s4 put A3 at
~10% of runtime; audit_script_doctrine.py hard-codes 180s absolute. This
gate follows the docs (10%) and says so in its output.

    python gate_opening_structure.py SCRIPT.txt [--timeline build-f/timeline.json]
           [--counterparty Bravos] [--ring spike] [--opening-s 300]
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

DOCS = Path(__file__).resolve().parents[3] / "docs/content-video-engine"
P1_GUIDE = DOCS / "patterns/phase-guides/P1.md"
P2_GUIDE = DOCS / "patterns/phase-guides/P2.md"

# ---- constants quoted from the docs ---------------------------------------
GRAB_S = 3.0                    # 38 B1 / P1 QC: first sentence <= 3s
BREATH_S = (0.5, 0.8)           # 38 B1: plate breathes 0.5-0.8s before the first word
BREATH_TOL = 0.2
PARADOX_BY_S = 8.0              # 38 B2: [post-key] ON the 8-second boundary
YOU_BY_S = 30.0                 # 38 B3 / P1 QC
STAKES_BY_S = 30.0              # 38 B3: stakes named by ~0:25 (tolerance to 0:30)
PROMISE_WIN = (30.0, 60.0)      # 38 B4 / MAP s3: mini-payoff FIRST, then the promise
A2_ANCHOR = 60.0                # 38 B5 / P1 QC: rehook ~1:00
A3_PCT = 0.10                   # P2.md / MAP s4 QC: A3 + F2 at ~10% of runtime
REHOOK_TOL = A.REHOOK_TOLERANCE_S
NEW_INFO_MAX_GAP_S = 30.0       # P2: something genuinely new every 15-30s
CATALYST_WITHIN_S = 60.0        # P2: first micro loop closed inside 30-60s of the phase
DIP_WITHIN_S = 15.0             # P2: "Immediately after" the macro close
DIP_MIN_GAP_S = 2.0             # P2: "2-3 beats of visual room tone, no narration push"
CTA_WINDOW_S = 30.0             # P2: "inside the 15-30 seconds after the macro payoff"
MARKS_PER_MIN_MAX = A.BREAK_RATION_MAX  # P1: ~three per minute maximum
P2_MARKS_MAX = 3                # P2: "Ration: <=3 marks in this phase"
CYCLE_MAX_GAP_S = 60.0          # CLK: the cycle repeats per beat (roster: 30-60s cadence)
CONCESSION_MAX_S = 10.0         # U6
CONCESSION_MAX_SENTS = 2        # U6
EST_TOL = 1.0 + A.TIMING_SPREAD_WARN   # estimates carry an 8% band (audit convention)

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
CHANNEL_TALK = re.compile(r"\b(this channel|my channel|the channel|on this channel)\b", re.I)
BIO = re.compile(r"\b(I worked (?:at|in)|I used to|JPMorgan|I own(?:ed)?|my dispensary|"
                 r"risk-scor)\w*", re.I)


@dataclass(frozen=True)
class Gate:
    id: str
    src: str          # doc reference
    level: str        # FAIL | WARN | PASS | JUDGE | INFO
    message: str


# ---- geometry from the phase guides ---------------------------------------
def _clock(s: str) -> float:
    m, _, sec = s.strip().partition(":")
    return int(m) * 60 + int(sec or 0)


def _phase_table(path: Path) -> list[tuple[float, float, float, str]]:
    """[(runtime_min, start_s, end_s, extra_cell)] from a guide's Geometry table."""
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
    """[(start_s, end_s, clean_sentence, char_offset_in_original)]."""
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
    """The start time of the sentence a char offset belongs to (or precedes)."""
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


# ---- the gate ---------------------------------------------------------------
def run(text: str, timeline: list[dict] | None = None, counterparty: str | None = None,
        ring: str | None = None, opening_s: float = 300.0) -> tuple[list[Gate], dict]:
    sents = _sentences_timed(text, timeline)
    marks = beat_tags.find_marks(text)                       # (mark, offset)
    beats: dict[str, list[tuple[float, int]]] = {}           # tag -> [(time, sentence idx)]
    for tag, off in marks:
        if tag in beat_tags.BEAT_TAGS:
            t = _time_of(off, sents)
            if t is not None:
                beats.setdefault(tag, []).append((t, _sentence_index_of(off, sents)))
    runtime = sents[-1][1] if sents else 0.0
    geo = geometry(runtime)
    p1_end, p2_end = geo["p1_end"], geo["p2_end"]
    tol = 1.0 if timeline else EST_TOL
    g: list[Gate] = []
    add = lambda i, src, lvl, m: g.append(Gate(i, src, lvl, m))
    mmss = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
    in_p1 = lambda t: t <= p1_end * tol
    in_p2 = lambda t: p1_end / tol <= t <= p2_end * tol
    first_beat = lambda tag: (beats.get(tag) or [(None, None)])[0][0]
    tag_times = lambda tag: [t for t, _ in beats.get(tag, [])]
    rehook_hits = lambda lo, hi: sorted(set(
        [st for st, _, s, _ in sents if lo <= st <= hi and re.search("|".join(A.REHOOKS), s, re.I)]
        + [t for t in tag_times("rehook") if lo <= t <= hi]))

    # ================= P1 =================
    # G01 microhook
    if sents:
        d = sents[0][1] - sents[0][0]
        add("G01", "38 s2 B1 / P1 QC: first sentence <= 3s", "FAIL" if d > GRAB_S * tol else "PASS",
            f"first sentence {d:.2f}s")
    # G02 visual breath before the first word (edit clock)
    if timeline:
        t0 = sents[0][0] if sents else 0.0
        ok = BREATH_S[0] - BREATH_TOL <= t0 <= BREATH_S[1] + BREATH_TOL
        add("G02", "38 s2 B1: plate breathes 0.5-0.8s before the first word; no cold silence",
            "PASS" if ok else "FAIL", f"first word at {t0:.2f}s in the edit clock")
    else:
        add("G02", "38 s2 B1: plate breathes 0.5-0.8s before the first word", "INFO",
            "edit-clock property - checked when a timeline is supplied")
    # G03 quick return by 8s + [post-key] on the boundary
    if len(sents) > 1:
        e = sents[1][1]
        # "the settle pause lands ON the 8-second decision boundary": a
        # [post-key] whose host line ENDS by 0:08, after the paradox is paid.
        # (Not "adjacent to sentence two" - ep1's mark after "touched it" at
        # ~6s is exactly the doc's beat.)
        pk_by_boundary = []
        for m, o in marks:
            if m != "post-key":
                continue
            k = _sentence_index_of(o, sents)
            # a mark written at the HEAD of a chunk ("touched it. `[post-key]`
            # That was 1845.") settles the sentence BEFORE it, not the one it
            # leads - attribute it to k-1 when it precedes chunk k's first letter
            lead = re.search(r"[A-Za-z0-9]", text[sents[k][3]:]) if k < len(sents) else None
            first_alnum = (sents[k][3] + lead.start()) if lead else -1
            if k >= 1 and o < first_alnum:
                k -= 1
            host_end = sents[k][1] if k < len(sents) else 1e9
            if k >= 1 and host_end <= PARADOX_BY_S * tol:
                pk_by_boundary.append(host_end)
        lvl = "PASS" if (e <= PARADOX_BY_S * tol and pk_by_boundary) else "FAIL"
        why = [] if e <= PARADOX_BY_S * tol else [f"paid at {e:.2f}s (> 8s)"]
        if not pk_by_boundary:
            why.append("no [post-key] settle by the 8s boundary")
        add("G03", "38 s2 B2: pay the microhook wrong by 0:08; [post-key] ON the 8s boundary", lvl,
            "; ".join(why) or f"paid at {e:.2f}s, settle at {pk_by_boundary[0]:.2f}s")
    # G04 ban list (greetings, announcements, channel talk) in the first 30s
    ban = [st for st, _, s, _ in sents if st <= YOU_BY_S and (re.search("|".join(A.GREETINGS), s, re.I) or CHANNEL_TALK.search(s))]
    add("G04", "38 s2 B2: no greeting, no 'in this video', no channel talk", "FAIL" if ban else "PASS",
        f"banned construction at {mmss(ban[0])}" if ban else "clean")
    # G05 "you" by 0:30
    ty = next((st for st, _, s, _ in sents if st <= YOU_BY_S * tol and re.search(r"\byou(?:r|'ll|'re|'ve)?\b", s, re.I)), None)
    add("G05", "38 s2 B3 / P1 QC: 'you' appears by 0:30", "PASS" if ty is not None else "FAIL",
        f"'you' at {mmss(ty)}" if ty is not None else "no 'you' before 0:30")
    # G06 biography only after the paradox
    par_end = sents[1][1] if len(sents) > 1 else 0.0
    early_bio = [st for st, _, s, _ in sents if st < par_end and BIO.search(s)]
    add("G06", "38 s2 B3: biography as the twist - AFTER the paradox, never before", "FAIL" if early_bio else "PASS",
        f"biography at {mmss(early_bio[0])} precedes the paradox" if early_bio else "clean")
    # G07 stakes by ~0:25 (declared)
    ts = first_beat("stakes")
    add("G07", "38 s2 B3: stakes named by ~0:25 (target + transformation + what's at risk)",
        "PASS" if ts is not None and ts <= STAKES_BY_S * tol else "FAIL",
        f"[stakes] at {mmss(ts)}" if ts is not None else "no [stakes] declared by 0:30")
    # G08/G09/G10/G11 promise cluster
    t_pr_tag = first_beat("promise")
    t_pr_rx = next((st for st, _, s, _ in sents if re.search(A.A1_PROMISE, s, re.I)), None)
    t_pr = t_pr_tag if t_pr_tag is not None else t_pr_rx
    pr_sent = next(((st, en, s, o) for st, en, s, o in sents if st == t_pr), None) if t_pr is not None else None
    t_po = first_beat("payoff")
    if t_po is None:
        add("G08", "38 s2 B4: deliver real value FIRST, before the ask", "FAIL", "no [payoff] declared before the promise")
    elif t_pr is not None and t_po > t_pr:
        add("G08", "38 s2 B4: deliver real value FIRST, before the ask", "FAIL", f"[payoff] at {mmss(t_po)} comes AFTER the promise at {mmss(t_pr)}")
    else:
        add("G08", "38 s2 B4: deliver real value FIRST, before the ask", "PASS", f"[payoff] at {mmss(t_po)}")
    if t_pr is None:
        add("G09", "38 s2 B4 / MAP s3 / CLK: the dated promise, 0:30-0:60", "FAIL", "no promise found (tag [promise] or a 'by the end you'll...' line)")
    elif t_pr > PROMISE_WIN[1] * tol:
        add("G09", "38 s2 B4 / MAP s3 / CLK: the dated promise, 0:30-0:60", "FAIL", f"promise at {mmss(t_pr)} - AFTER 0:60 (Steel and Paper as recorded: 1:20)")
    elif t_pr < PROMISE_WIN[0] / tol:
        add("G09", "38 s2 B4 / MAP s3 / CLK: the dated promise, 0:30-0:60", "WARN", f"promise at {mmss(t_pr)} - before the mini-payoff window opens")
    else:
        add("G09", "38 s2 B4 / MAP s3 / CLK: the dated promise, 0:30-0:60", "PASS", f"promise at {mmss(t_pr)}")
    if pr_sent:
        # "immediately before the promise": the mark sits in the promise
        # chunk's leading zone (before its first letter) or just ahead of it -
        # `[pre-key]` with backticks and spacing is up to ~20 chars.
        lead = re.search(r"[A-Za-z0-9]", text[pr_sent[3]:])
        first_alnum = pr_sent[3] + (lead.start() if lead else 0)
        has_prekey = any(m == "pre-key" and pr_sent[3] - 20 <= o < first_alnum for m, o in marks)
        add("G10", "P1 pause marks: [pre-key] immediately before the promise", "PASS" if has_prekey else "FAIL",
            "placed" if has_prekey else "missing")
        calc = bool(NUMBER.search(pr_sent[2]) or CALCULABLE.search(pr_sent[2]))
        add("G11", "38 s2 B4: the promise carries a date or number and is calculable", "PASS" if calc else "FAIL",
            f"'{pr_sent[2][:70]}'")
    # G12 tricolon exactly one in P1
    tri1 = [t for t in tag_times("tricolon") if in_p1(t)]
    add("G12", "P1 B4: tricolon on the thesis line - exactly one in the phase", "PASS" if len(tri1) == 1 else "FAIL",
        f"{len(tri1)} declared in P1")
    # G13 A2 ~1:00
    a2 = rehook_hits(A2_ANCHOR - 5, max(p1_end, A2_ANCHOR) * tol + 5)
    add("G13", "38 s2 B5 / P1 QC: rehook A2 ~1:00 (template family)", "PASS" if a2 else "FAIL",
        f"A2 at {mmss(a2[0])}" if a2 else f"no rehook construction in 0:55-{mmss(p1_end)}")
    # G14 opponent named as mechanism (declared + JUDGE)
    top = first_beat("opponent")
    if top is None or not in_p1(top):
        add("G14", "38 s2 B5: Desire and the Opponent named - a MECHANISM, never a villain", "FAIL", "no [opponent] declared in P1")
    else:
        add("G14", "38 s2 B5: Desire and the Opponent named - a MECHANISM, never a villain", "PASS", f"[opponent] at {mmss(top)}")
        add("J01", "38 s2 B5: opponent is a mechanism, not a villain", "JUDGE", f"read the [opponent] line at {mmss(top)}")
    # G15 ring token planted in P1
    if ring:
        rx = re.compile(r"\b" + re.escape(ring) + r"s?\b", re.I)
        r1 = [st for st, _, s, _ in sents if in_p1(st) and rx.search(s)]
        add("G15", "38 s2 B5 / P1: the ring token planted by the end of P1", "PASS" if r1 else "FAIL",
            f"'{ring}' planted at {mmss(r1[0])}" if r1 else f"'{ring}' never mentioned in P1")
    else:
        rg = [t for t in tag_times("ring") if in_p1(t)]
        add("G15", "38 s2 B5 / P1: the ring token planted by the end of P1", "PASS" if rg else "FAIL",
            f"[ring] at {mmss(rg[0])}" if rg else "no ring token (pass --ring <object> or tag [ring])")
    # G16 exactly one reflection dab in P1
    rf1 = [t for t in tag_times("reflect") if in_p1(t)]
    add("G16", "P1 Glass 80/20: exactly ONE reflection dab", "PASS" if len(rf1) == 1 else "FAIL", f"{len(rf1)} [reflect] in P1")
    # G17 attribution-first (hard gate) + [verify] placement
    trail = [st for st, _, s, _ in sents if st <= opening_s and re.search("|".join(A.TRAILING_ATTR), s)]
    vf_bad = [o for m, o in marks if m == "verify" and (_sentence_index_of(o, sents) == 0 or (pr_sent and _sentence_index_of(o, sents) == sents.index(pr_sent)))]
    if trail or vf_bad:
        add("G17", "P1/P2 HARD GATE: attribution-first; [verify] never in hook/promise", "FAIL",
            (f"trailing attribution at {mmss(trail[0])}" if trail else "") + ("; [verify] in hook/promise" if vf_bad else ""))
    else:
        add("G17", "P1/P2 HARD GATE: attribution-first; [verify] never in hook/promise", "PASS", "clean")
    # G18 pause ration P1
    n1 = sum(1 for m, o in marks if m in ("pre-key", "post-key") and (_time_of(o, sents) or 0) <= p1_end)
    per_min = n1 / max(p1_end / 60.0, 1e-9)
    add("G18", "P1 pause marks: roughly three per minute maximum", "FAIL" if per_min > MARKS_PER_MIN_MAX else "PASS",
        f"{n1} marks in P1 ({per_min:.1f}/min)")

    # ================= P2 =================
    loops = [t for t in tag_times("loop") if in_p2(t)]
    news = [t for t in tag_times("new") if in_p2(t)]
    # G19 catalyst closes inside the first 60s of P2
    add("G19", "P2: the catalyst lands as a micro loop CLOSED inside 30-60s of the phase", "PASS" if loops and loops[0] <= (p1_end + CATALYST_WITHIN_S) * tol else "FAIL",
        f"first [loop] at {mmss(loops[0])}" if loops else "no [loop] declared in P2")
    # G20 new-info cadence
    if news:
        pts = [p1_end] + news
        gaps = [b - a for a, b in zip(pts, pts[1:])]
        worst = max(gaps)
        add("G20", "P2: something genuinely new every 15-30s", "FAIL" if worst > NEW_INFO_MAX_GAP_S * tol else "PASS",
            f"longest gap between new-info beats {worst:.0f}s")
    else:
        add("G20", "P2: something genuinely new every 15-30s", "FAIL", "no [new] beats declared in P2")
    # G21 density bands
    lo_l, hi_l = geo["loops"]; lo_n, hi_n = geo["new"]
    if lo_l is not None:
        okl = lo_l <= len(loops) <= hi_l
        add("G21", f"P2 density: {lo_l}-{hi_l} micro-loop closes at this runtime", "PASS" if okl else "FAIL", f"{len(loops)} [loop] in P2")
    if lo_n is not None:
        okn = lo_n <= len(news) <= hi_n
        add("G22", f"P2 density: {lo_n}-{hi_n} new-info beats at this runtime", "PASS" if okn else "FAIL", f"{len(news)} [new] in P2")
    # G23 no AND-THEN chains
    p2s = [(st, s) for st, _, s, _ in sents if in_p2(st)]
    chain = any(AND_THEN.match(a[1]) and AND_THEN.match(b[1]) for a, b in zip(p2s, p2s[1:]))
    add("G23", "P2 / MAP s4 QC: BUT/THEREFORE only - zero AND-THEN chains", "FAIL" if chain else "PASS", "chain found" if chain else "clean")
    # G24 head-fake early-mid P2
    hf = [t for t in tag_times("head-fake") if in_p2(t)]
    early = p1_end + 0.6 * (p2_end - p1_end)
    if not hf:
        add("G24", "P2 MANDATORY: head-fake #1 planted straight, early-mid phase", "FAIL", "no [head-fake] declared in P2")
    elif hf[0] > early * tol:
        add("G24", "P2 MANDATORY: head-fake #1 planted straight, early-mid phase", "FAIL", f"[head-fake] at {mmss(hf[0])} - late in the phase (by {mmss(early)})")
    else:
        add("G24", "P2 MANDATORY: head-fake #1 planted straight, early-mid phase", "PASS", f"[head-fake] at {mmss(hf[0])}")
        add("J02", "P2: head-fake offered STRAIGHT, demolition reserved for the pivot", "JUDGE", f"read the line at {mmss(hf[0])}")
    # G25 A3 + F2 at ~10% of runtime (docs), conflict with audit's 180s noted
    a3c = runtime * A3_PCT
    a3 = rehook_hits(a3c - REHOOK_TOL, a3c + REHOOK_TOL)
    add("G25", f"P2 / MAP s4: A3 rehook at ~10% of runtime ({mmss(a3c)}) [audit hard-codes 3:00 absolute - docs win here]",
        "PASS" if a3 else "FAIL", f"A3 at {mmss(a3[0])}" if a3 else f"no rehook within {REHOOK_TOL:.0f}s of {mmss(a3c)}")
    f2 = [t for t in tag_times("foreshadow") if a3c - REHOOK_TOL <= t <= a3c + REHOOK_TOL]
    add("G26", "P2: F2 - the promise sighted again at ~10%, delivering none of it (may share the A3 line)", "PASS" if f2 else "FAIL",
        f"[foreshadow] at {mmss(f2[0])}" if f2 else "no [foreshadow] near 10%")
    # G27 ring touched exactly once in P2
    if ring:
        r2 = [st for st, _, s, _ in sents if in_p2(st) and rx.search(s)]
        add("G27", "P2: ring token touched exactly ONCE, unresolved", "PASS" if len(r2) == 1 else "FAIL", f"'{ring}' mentioned {len(r2)}x in P2")
    else:
        r2 = [t for t in tag_times("ring") if in_p2(t)]
        add("G27", "P2: ring token touched exactly ONCE, unresolved", "PASS" if len(r2) == 1 else "FAIL", f"[ring] {len(r2)}x in P2")
    # G28 macro loop 1 closes
    lc = [t for t in tag_times("loop-close") if in_p2(t) or t <= (p2_end + REHOOK_TOL)]
    add("G28", "P2 / MAP s4: macro loop 1 closes on a partial answer that opens the bigger question", "PASS" if lc else "FAIL",
        f"[loop-close] at {mmss(lc[0])}" if lc else "no [loop-close] declared")
    # G29 dip immediately after (timeline gap or declared)
    if lc:
        t_lc = lc[0]
        dip_ok, how = False, ""
        if timeline:
            ws = [w for w in timeline if re.search(r"[A-Za-z0-9]", w["w"])]
            for a, b in zip(ws, ws[1:]):
                if t_lc <= a["end"] <= t_lc + DIP_WITHIN_S and b["start"] - a["end"] >= DIP_MIN_GAP_S:
                    dip_ok, how = True, f"{b['start'] - a['end']:.1f}s of room tone at {mmss(a['end'])}"; break
        if not dip_ok:
            dd = [t for t in tag_times("dip") if t_lc <= t <= t_lc + DIP_WITHIN_S * tol]
            if dd:
                dip_ok, how = True, f"[dip] at {mmss(dd[0])}"
        add("G29", "P2: IMMEDIATELY after the macro close, one breathing dip (2-3 beats of room tone)", "PASS" if dip_ok else "FAIL",
            how or f"no dip within {DIP_WITHIN_S:.0f}s of the macro close at {mmss(t_lc)}")
    else:
        add("G29", "P2: breathing dip after the macro close", "WARN", "cannot place - macro close not declared")
    # G30 CTA only in the post-payoff window
    ctas = [st for st, _, s, _ in sents if st <= opening_s and re.search("|".join(A.CTA), s, re.I)]
    bad_cta = [t for t in ctas if not (lc and lc[0] <= t <= lc[0] + CTA_WINDOW_S)]
    add("G30", "P2: the ONLY mid-video CTA slot is the 15-30s after the macro payoff", "FAIL" if bad_cta else "PASS",
        f"CTA at {mmss(bad_cta[0])} outside the slot" if bad_cta else ("none" if not ctas else f"one inside the slot at {mmss(ctas[0])}"))
    # G31 Glass 70/30 in P2: reflection dabs never consecutive; not listing
    rf2 = sorted(i for t, i in beats.get("reflect", []) if in_p2(t))
    adj = any(b - a == 1 for a, b in zip(rf2, rf2[1:]))
    if adj:
        add("G31", "P2 Glass 70/30: two consecutive reflection sentences = lecturing", "FAIL", "adjacent [reflect] dabs")
    elif loops and len(rf2) * 2 < len(loops):
        add("G31", "P2 Glass 70/30: two loops with no reflection = listing", "WARN", f"{len(rf2)} dabs for {len(loops)} loops")
    else:
        add("G31", "P2 Glass 70/30: reflection dabs marked, never consecutive", "PASS", f"{len(rf2)} dabs, {len(loops)} loops")
    # G32 tricolon <=1 in P2; anaphora recurs once if debuted in P1
    tri2 = [t for t in tag_times("tricolon") if in_p2(t)]
    an1 = [t for t in tag_times("anaphora") if in_p1(t)]
    an2 = [t for t in tag_times("anaphora") if in_p2(t)]
    bad = len(tri2) > 1 or (an1 and len(an2) != 1)
    add("G32", "P2: ONE momentum tricolon max; anaphora (if debuted in P1) recurs exactly once", "FAIL" if bad else "PASS",
        f"tricolon {len(tri2)}, anaphora P1 {len(an1)} / P2 {len(an2)}")
    # G33 no [pre-key] immediately before the head-fake; P2 mark ration
    hf_offs = [o for m, o in marks if m == "head-fake"]
    # "`[pre-key]` [head-fake]" spans ~11-16 chars between the two marks' starts
    pk_before_hf = any(m == "pre-key" and any(0 <= ho - o <= 20 for ho in hf_offs) for m, o in marks)
    n2 = sum(1 for m, o in marks if m in ("pre-key", "post-key") and in_p2(_time_of(o, sents) or -1))
    lvl = "FAIL" if (pk_before_hf or n2 > P2_MARKS_MAX) else "PASS"
    add("G33", "P2 pause marks: no [pre-key] before the head-fake; <=3 marks in the phase", lvl,
        ("[pre-key] sits before the head-fake; " if pk_before_hf else "") + f"{n2} marks in P2")

    # ================= cross-cutting =================
    # G34 concession budget (U6 / E20)
    cp = counterparty
    if not cp:
        from collections import Counter
        caps = Counter(re.findall(r"\b([A-Z][a-z]{3,})\b", " ".join(s for _, _, s, _ in sents)))
        stop = {"The", "And", "But", "That", "This", "Here", "There", "What", "When", "Then", "Today", "Count", "Nothing", "Every", "Every"}
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
    if worst:
        add("G34", "U6 / E20: a counterparty/agreement run never exceeds 2 sentences or 10s without a claim of ours", "FAIL",
            f"{len(worst)} sentences, {mmss(worst[0][0])}-{mmss(worst[-1][1])} ({worst[-1][1] - worst[0][0]:.0f}s): '{worst[0][2][:60]}...'")
    else:
        add("G34", "U6 / E20: a counterparty/agreement run never exceeds 2 sentences or 10s without a claim of ours", "PASS", "clean")
    # G35 a delivered proof is never hedged next-line (U6 / E20)
    hedged = next(((a, b) for a, b in zip(sents, sents[1:]) if b[0] <= opening_s and NUMBER.search(a[2]) and HEDGE.search(b[2])), None)
    add("G35", "U6 / E20: a delivered proof is never hedged in the next sentence", "FAIL" if hedged else "PASS",
        f"proof at {mmss(hedged[0][0])} hedged at {mmss(hedged[1][0])}: '{hedged[1][2][:70]}'" if hedged else "clean")
    # G36 the cycle repeats (CLK): no >60s stretch of the opening without a cycle beat
    cycle = sorted(set(([t_pr] if t_pr is not None else []) + loops + news + lc + rehook_hits(0, opening_s) + tag_times("head-fake")))
    cycle = [t for t in cycle if t <= opening_s]
    pts = [0.0] + cycle + [min(opening_s, runtime)]
    gaps = [(a, b - a) for a, b in zip(pts, pts[1:])]
    wg = max(gaps, key=lambda x: x[1]) if gaps else (0, 0)
    add("G36", "CLK: hook / show it's worth it / promise more / deliver - the cycle repeats per beat (no >60s without one)",
        "FAIL" if wg[1] > CYCLE_MAX_GAP_S * tol else "PASS", f"longest stretch without a cycle beat: {wg[1]:.0f}s from {mmss(wg[0])}")
    # JUDGE-only rows the docs require and no machine can read
    add("J03", "38 s2 B1: microhook is concrete with terminal stress on the surprising word", "JUDGE", f"'{sents[0][2][:80]}'" if sents else "")
    add("J04", "38 s2 B5: context-dump ban - every abstraction cashed into an object or number within one sentence", "JUDGE", "read P1 B5")

    stats = {"runtime": mmss(runtime), "timing": "measured (take)" if timeline else "estimated (kit rate, 8% band)",
             "geometry": f"P1 0:00-{mmss(p1_end)}, P2 -{mmss(p2_end)} ({geo['source']})",
             "density_bands": f"loops {geo['loops']}, new-info {geo['new']}",
             "counterparty": cp, "ring": ring,
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
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    text = args.script.read_text(encoding="utf-8")
    unknown = beat_tags.unknown_marks(text)
    tl = load_timeline(args.timeline) if args.timeline else A.load_timings(args.script)
    gates, stats = run(text, tl, args.counterparty, args.ring, args.opening_s)
    if unknown:
        gates.insert(0, Gate("G00", "doc 37 marks", "FAIL", f"unknown marks would be spoken: {sorted(unknown)}"))
    print(f"=== OPENING STRUCTURE GATE: {args.script.name} ===")
    for k, v in stats.items():
        print(f"  {k:>16}: {v}")
    print()
    for x in gates:
        print(f"  [{x.level:5}] {x.id} {x.message}\n          {x.src}")
    n = lambda lvl: sum(1 for x in gates if x.level == lvl)
    print(f"\nRESULT: {n('FAIL')} FAIL / {n('WARN')} WARN / {n('PASS')} PASS / {n('JUDGE')} JUDGE (read these) / {n('INFO')} INFO")
    return 1 if n("FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())

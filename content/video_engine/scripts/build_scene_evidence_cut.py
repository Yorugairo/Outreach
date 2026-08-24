"""Five-minute demo v4 generator (scene-evidence lane, doc 29 Part 8).

Reads the v3 semantic spine for its world beats and canonical word-timed
captions, then selects evidence from the APPROVED teacher-stamped slide
catalogue (86 render-eligible slides) by semantic match against what is
actually being said inside each scene window.

Three rules this generator enforces, each a correction of the first pass:

1. Captions are their own track at their own canonical timings. They are
   never resampled onto beat boundaries (doc 29 Part 5).
2. Evidence comes only from teacher-stamped slides — never a cropped or
   unstamped one-off — and no slide repeats inside the cut.
3. A badge is emitted only where the numeral has been read off the bound
   slide. Everything else ships with no rail; the stamped slide already
   carries its own typeset figures, and inventing one to fill the layout
   is the failure this rule exists to prevent.
"""
from __future__ import annotations

import base64
import json
import math
import re
import subprocess
from collections import Counter
from pathlib import Path

FPS = 30
CUT_SECONDS = 300.0
CUES: list = []

P29 = Path(r"C:/Users/Snipe/.codex/worktrees/p29-remotion-console/Outreach Program")
PUBLIC = P29 / "content/video_engine/editor/public"
PROJ = P29 / "content/video_engine/projects/systems-and-blowups"
DECKS = PROJ / "sources/decks/teacher-stamped-production-visuals"
PILOT = PROJ / "pilots/current-bubble-mechanism"
V3_PROPS = PILOT / "five-minute-semantic-demo-v3/render/current-bubble-five-minute-v3.props.json"
COVERAGE = PILOT / "edit/evidence-coverage-v1/full-episode-evidence-coverage.v1.json"
OUT = Path(__file__).parent
ASSETS = OUT / "assets"

# Choreographic rhythm, matched to the reference cut:
#   world intro -> card 1 -> badge -> badge -> SETTLE -> card 2 -> badge ->
#   badge -> SAVOR (whole board) -> wipe
# A document is still a guest, not a tenant. A solo card caps at 7s. A paired
# build runs longer so both proofs can sit together for the savour beat --
# without it the first card leaves before the second finishes building and the
# viewer never sees the pair.
INTRO = 1.7          # world plate alone before any evidence
BADGE_1 = 1.3        # first badge, after the card settles
BADGE_2 = 2.6        # second badge
SETTLE = 1.1         # beat to read card 1 before card 2 arrives
SAVOR = 2.2          # whole board held after the last badge
DOCK_HOLD_SOLO = 7.0
DOCK_EXIT = 0.72

# The plate is the hero, but a plate with nothing happening on it stops being
# cinema and becomes a screensaver. Long scenes run repeated build cycles
# separated by a short breathing gap; no stretch of bare plate may exceed
# MAX_BARE anywhere in the cut.
MAX_BARE = 12.0      # hard ceiling on plate-with-no-evidence
GAP = 3.4            # intended breathing gap between build cycles
CYCLE_PAIR = BADGE_2 + SETTLE + BADGE_2 + SAVOR
CYCLE_SOLO = BADGE_2 + SAVOR

KB_CYCLE = [
    {"scale": 0.085, "x": -22, "y": -10},
    {"scale": 0.105, "x": 18, "y": -13},
    {"scale": 0.075, "x": 14, "y": 12},
    {"scale": 0.115, "x": -16, "y": 11},
    {"scale": 0.090, "x": 20, "y": -8},
]

# Numerals read directly off these slides during review.
VERIFIED_BADGES = {
    "memory-supercycle-s03": [
        {"label": "HBM WAFER SHARE", "value": "18% \u2192 23%", "tag": "2025\u20132026", "accent": "sunflower"},
        {"label": "WAFERS EJECTED", "value": "2 to 3", "tag": "PER HBM WAFER", "accent": "coral"},
    ],
    "memory-supercycle-s05": [
        {"label": "CXMT GROWTH", "value": "716%", "tag": "YoY", "accent": "coral"},
        {"label": "STUCK ON LEGACY", "value": "70%", "tag": "LPDDR4(X)", "accent": "teal"},
    ],
    "silicon-value-software-bubble-s04": [
        {"label": "SAMSUNG COMMITMENT", "value": "$400M", "tag": "1983", "accent": "sunflower"},
        {"label": "SK HYNIX DEBT", "value": "11T won", "tag": "IMF MERGER", "accent": "coral"},
    ],
    "sovereign-memory-infrastructure-s03": [
        {"label": "HBM POSITION", "value": "Layer 2", "tag": "BELOW SILICON", "accent": "cobalt"},
        {"label": "THERMAL ENVELOPE", "value": "1500W", "tag": "LIQUID COOLED", "accent": "sunflower"},
    ],
}

STOP = set("""a an the and or but of to in on for with as is are was were be been being that this those these
it its by from at into than then so such not no if we you they our their there here what which who how why
about over under more most less least can may might will would should could have has had do does did just
own same other another each any all some one two three now still even because""".split())


def tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP and len(w) > 2]


def load_spine() -> dict:
    props = json.loads(V3_PROPS.read_text(encoding="utf-8"))
    items = props["items"]

    def inside(x):
        return x["from"] / FPS < CUT_SECONDS

    return {
        "worlds": sorted((x for x in items if x["type"] == "world_plate" and inside(x)), key=lambda x: x["from"]),
        "captions": sorted((x for x in items if x["type"] == "caption" and inside(x)), key=lambda x: x["from"]),
        "assetMap": props["assetMap"],
    }


# Narration-side semantics are registered: every cue carries claim_refs from an
# 18-term controlled vocabulary plus the plate's semantic_action. Those are far
# stronger query signal than transcript prose, which is mostly connective
# tissue. (The evidence side carries no claim_refs -- see the protocol note in
# doc 29 -- so this is a one-sided join for now.)
CLAIM_WEIGHT = 3.0
ACTION_WEIGHT = 2.0


def load_cues() -> list[dict]:
    if not COVERAGE.is_file():
        return []
    d = json.loads(COVERAGE.read_text(encoding="utf-8"))
    out = []
    for c in d.get("cues", []):
        if c["start_s"] >= CUT_SECONDS:
            continue
        out.append({
            "a": c["start_s"], "b": c["end_s"],
            "claims": c.get("claim_refs", []),
            "action": (c.get("active_world_plate") or {}).get("semantic_action", ""),
        })
    return out


def semantic_query(cues: list[dict], a: float, b: float, said: str) -> Counter:
    """Weighted query: registered claims and semantic actions dominate; the
    spoken excerpt fills in around them."""
    q = Counter(tokens(said))
    for c in cues:
        if c["a"] < b and c["b"] > a:
            for claim in c["claims"]:
                for w in tokens(claim.replace("-", " ")):
                    q[w] += CLAIM_WEIGHT
            for w in tokens(c["action"].replace("≠", " ")):
                q[w] += ACTION_WEIGHT
    return q


def load_catalogue() -> list[dict]:
    m = json.loads((DECKS / "teacher-stamped-production-visuals-manifest.v1.json").read_text(encoding="utf-8"))
    cat = []
    for v in m["visuals"]:
        if not v.get("evidence_render_eligible"):
            continue
        ctx = v["context"]
        cat.append({
            "slide_id": v["slide_id"],
            "label": ctx["label"],
            "path": v["extracted_path"],
            "sha256": v["sha256"],
            "deck": v["deck_id"],
            "tokens": Counter(tokens(ctx["label"] + " " + ctx["summary"])),
            "label_tokens": set(tokens(ctx["label"])),
        })
    return cat


def idf_weights(cat: list[dict]) -> dict[str, float]:
    n = len(cat)
    df = Counter()
    for s in cat:
        df.update(set(s["tokens"]))
    return {w: math.log(n / (1 + c)) + 1.0 for w, c in df.items()}


LABEL_BOOST = 2.2    # a hit in the curated title means more than one in prose
MIN_DISTINCT = 2     # a single common word is a coincidence, not a match
RARE_IDF = 3.4       # ...unless the one shared word is genuinely rare
MIN_SCORE = 0.14
FLOOR_SCORE = 0.06   # coverage pass: better a weak match than a bare scene


def score_pair(q: Counter, weights, s: dict) -> float:
    """IDF-weighted cosine, with hits in the slide's curated label boosted.

    Cosine (rather than raw overlap) stops long summaries and short titles
    from being scored on different scales, which is what let two generic
    hits beat one specific one.
    """
    shared = [w for w in q if w in s["tokens"]]
    if len(shared) < MIN_DISTINCT:
        # one shared word only counts when it is a rare, specific term
        if not (shared and weights.get(shared[0], 1.0) >= RARE_IDF):
            return 0.0
    dot = 0.0
    for w in shared:
        boost = LABEL_BOOST if w in s["label_tokens"] else 1.0
        iw = weights.get(w, 1.0)
        dot += (q[w] * iw) * (s["tokens"][w] * iw * boost)
    qn = math.sqrt(sum((c * weights.get(w, 1.0)) ** 2 for w, c in q.items()))
    sn = math.sqrt(sum((c * weights.get(w, 1.0)) ** 2 for w, c in s["tokens"].items()))
    return dot / (qn * sn) if qn and sn else 0.0


def assign(slots: list[dict], cat, weights) -> dict[int, dict]:
    """Global strongest-unused-match assignment.

    Every (slot, slide) pair is scored, then pairs are consumed in descending
    score order. The strongest match anywhere in the episode is placed first,
    so an early scene can no longer take a slide a later scene needed more.
    """
    pairs = []
    for i, slot in enumerate(slots):
        q = semantic_query(CUES, slot.get("a", 0), slot.get("b", 0), slot["said"])
        if not q:
            continue
        for s in cat:
            sc = score_pair(q, weights, s)
            if sc >= MIN_SCORE:
                pairs.append((sc, i, s))
    pairs.sort(key=lambda x: (-x[0], x[1], x[2]["slide_id"]))

    out: dict[int, dict] = {}
    used_slides: set[str] = set()
    used_decks: dict[int, set[str]] = {}

    def place(sc, i, s) -> bool:
        scene = slots[i]["scene"]
        if i in out or s["slide_id"] in used_slides:
            return False
        if s["deck"] in used_decks.get(scene, set()):
            return False  # never pair two slides from one deck in the same scene
        out[i] = dict(s, _score=round(sc, 3))
        used_slides.add(s["slide_id"])
        used_decks.setdefault(scene, set()).add(s["deck"])
        return True

    for sc, i, s in pairs:
        place(sc, i, s)

    # coverage pass — a scene left with no evidence at all takes its best
    # remaining slide above a lower floor. Scenes whose narration matches
    # nothing stay bare rather than getting a misleading document.
    covered = {slots[i]["scene"] for i in out}
    for i, slot in enumerate(slots):
        if slot["scene"] in covered:
            continue
        q = semantic_query(CUES, slot.get("a", 0), slot.get("b", 0), slot["said"])
        if not q:
            continue
        best = sorted(
            ((score_pair(q, weights, s), s) for s in cat if s["slide_id"] not in used_slides),
            key=lambda x: (-x[0], x[1]["slide_id"]))
        if best and best[0][0] >= FLOOR_SCORE and place(best[0][0], i, best[0][1]):
            covered.add(slot["scene"])
    return out


def _cycle_docks(picks, e1, e2, board_end, evidence) -> list[dict]:
    """Emit one build cycle: card(s) enter staggered, badges fire, board clears
    together after the savour."""
    out = []
    for slot, s in enumerate(picks):
        badges = VERIFIED_BADGES.get(s["slide_id"], [])
        evidence[s["slide_id"]] = {
            "title": s["label"],
            "document": {"path": s["path"], "sha256": s["sha256"]},
            "source": f'{s["deck"].replace("-", " ").title()} &middot; slide {s["slide_id"].rsplit("-s", 1)[-1]}',
            "badges": [dict(b, verbatim_in_document=True) for b in badges],
            "match_score": s.get("_score"),
        }
        enter = e1 if slot == 0 else e2
        if board_end - enter < 2.4:
            continue
        out.append({
            "slide": s["slide_id"], "slot": slot,
            "enter": round(enter, 2), "exit": round(board_end, 2),
            "badge_at": [round(enter + b, 2)
                         for b in (BADGE_1, BADGE_2)[:min(2, len(badges))]
                         if enter + b < board_end - 0.6],
        })
    return out


def fill_gaps(tl, caps, cat, weights, evidence) -> int:
    """Insert solo builds into any bare stretch longer than MAX_BARE."""
    used = set(evidence)
    added = 0
    for _pass in range(4):                       # a fill can leave a smaller gap
        spans = sorted((d["enter"], d["exit"]) for sc in tl["scenes"] for d in sc["docks"])
        gaps, cursor = [], 0.0
        for a, b in spans:
            if a - cursor > MAX_BARE:
                gaps.append((cursor, a))
            cursor = max(cursor, b)
        if CUT_SECONDS - cursor > MAX_BARE:
            gaps.append((cursor, CUT_SECONDS))
        if not gaps:
            break

        for g0, g1 in gaps:
            at = g0 + GAP
            board_end = min(at + CYCLE_SOLO, g1 - 0.8)
            if board_end - at < 2.4:
                continue
            # A gap can straddle a scene boundary: the scene holding `at` may
            # end before a cycle fits. Take whichever scene overlapping the gap
            # offers the most room, and start the cycle inside it.
            best_sc, best_at, best_end = None, at, 0.0
            for x in tl["scenes"]:
                s0, s1 = max(x["span"][0], g0), min(x["span"][1], g1)
                if s1 - s0 < 2.4:
                    continue
                cand_at = max(at, s0 + 0.6)
                cand_end = min(cand_at + CYCLE_SOLO, s1 - 0.8)
                if cand_end - cand_at > best_end - best_at:
                    best_sc, best_at, best_end = x, cand_at, cand_end
            if best_sc is None or best_end - best_at < 2.4:
                continue
            sc, at, board_end = best_sc, best_at, best_end

            said = " ".join(t for x, y, t in caps if x < board_end and y > at)
            q = semantic_query(CUES, at, board_end, said)
            best = sorted(((score_pair(q, weights, c), c) for c in cat
                           if c["slide_id"] not in used),
                          key=lambda z: (-z[0], z[1]["slide_id"]))
            if not best:
                continue
            if best[0][0] < FLOOR_SCORE:
                # Nothing scores here, but a long dead stretch is worse than a
                # loose match. Prefer a slide from a deck this scene already
                # draws on (topical adjacency), and record the real score so
                # review can catch it.
                sibling = {d["slide"].rsplit("-s", 1)[0] for d in sc["docks"]}
                near = [z for z in best if z[1]["deck"] in sibling]
                best = near or best
            pick = dict(best[0][1], _score=round(best[0][0], 3))
            used.add(pick["slide_id"])
            sc["docks"].extend(_cycle_docks([pick], at, at, board_end, evidence))
            sc["docks"].sort(key=lambda d: d["enter"])
            added += 1
    return added


def build(spine, cat, weights) -> dict:
    caps = [(c["from"] / FPS,
             min(c["from"] / FPS + c["durationInFrames"] / FPS, CUT_SECONDS),
             c.get("text", ""))
            for c in spine["captions"]]

    # pass 1 — every dock slot declares the narration it must illustrate.
    # A two-dock scene splits its window so each slot matches what is being
    # said while THAT dock is on screen, not a blob of the whole scene.
    slots: list[dict] = []
    windows: list[tuple] = []
    for wi, w in enumerate(spine["worlds"]):
        start = w["from"] / FPS
        end = min(start + w["durationInFrames"] / FPS, CUT_SECONDS)
        if end - start < 4.0:
            continue

        # lay out as many build cycles as fit, pairs first while there is room
        cycles, cursor = [], start + INTRO
        while end - cursor > CYCLE_SOLO * 0.8:
            paired = (end - cursor) >= CYCLE_PAIR + 0.8
            length = CYCLE_PAIR if paired else CYCLE_SOLO
            cycles.append({"at": cursor, "pair": paired,
                           "end": min(cursor + length, end - 0.8)})
            cursor += length + GAP
        if not cycles:
            cycles = [{"at": start + INTRO, "pair": False, "end": end - 0.8}]

        base = len(slots)
        for cy in cycles:
            for k in range(2 if cy["pair"] else 1):
                a, b = cy["at"], cy["end"]
                slots.append({"scene": wi, "a": a, "b": b,
                              "said": " ".join(t for x, y, t in caps if x < b and y > a)})
        windows.append((wi, w, start, end, cycles, base))

    placed = assign(slots, cat, weights)

    scenes: list[dict] = []
    evidence: dict[str, dict] = {}

    for wi, w, start, end, cycles, base in windows:
        docks = []
        idx = base
        for cy in cycles:
            width = 2 if cy["pair"] else 1
            picks = [placed[idx + k] for k in range(width) if idx + k in placed]
            idx += width
            if not picks:
                continue

            e1 = cy["at"]
            e2 = e1 + BADGE_2 + SETTLE
            last_badge = (e2 if len(picks) > 1 else e1) + BADGE_2
            board_end = min(last_badge + SAVOR, end - 0.8)
            if len(picks) == 1:
                board_end = min(board_end, e1 + DOCK_HOLD_SOLO)
            docks.extend(_cycle_docks(picks, e1, e2, board_end, evidence))

        if not docks:
            continue
        span = end - start
        for _unused in ():
            badges = None

        scenes.append({
            "scene_id": f"s{len(scenes) + 1:02d}",
            "world": {"asset_id": w["assetId"], "sha256": "0" * 64,
                      "ken_burns": KB_CYCLE[len(scenes) % len(KB_CYCLE)]},
            "exit": "wipe_left" if len(scenes) % 2 == 0 else "wipe_right",
            "span": [round(start, 2), round(end, 2)],
            "docks": docks,
        })

    return {
        "schema_version": "scene_evidence_timeline.v1",
        "episode_id": "current-bubble-five-minute-v4",
        "project_id": "systems-and-blowups",
        "narration": {"canonical_hash": "0" * 64, "words_path": "edit/semantic-v2/words.json"},
        "captions": [{"at": round(a, 2), "until": round(b, 2), "text": t} for a, b, t in caps],
        "evidence": evidence,
        "scenes": scenes,
    }


def media(tl, spine) -> dict:
    ASSETS.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    uris: dict[str, str] = {}

    def enc(name: str, src: Path, width: int, q: int) -> str:
        dst = ASSETS / f"{name}.jpg"
        im = Image.open(src).convert("RGB")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(dst, quality=q, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(dst.read_bytes()).decode()

    for aid in {sc["world"]["asset_id"] for sc in tl["scenes"]}:
        uris[aid] = enc(aid, PUBLIC / spine["assetMap"][aid], 1150, 58)
    for sid, ev in tl["evidence"].items():
        uris[sid] = enc(sid, DECKS / ev["document"]["path"], 700, 74)

    hand = ASSETS / "draw-hand.png"
    if hand.is_file():
        uris["__hand__"] = "data:image/png;base64," + base64.b64encode(hand.read_bytes()).decode()

    dst = ASSETS / "narration.m4a"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i",
                    str(PUBLIC / "current-bubble-fresh-60s-v1/history_episode_1_master.mp3"),
                    "-t", str(CUT_SECONDS), "-ac", "1", "-ar", "32000",
                    "-c:a", "aac", "-b:a", "40k", str(dst)], capture_output=True)
    uris["__audio__"] = "data:audio/mp4;base64," + base64.b64encode(dst.read_bytes()).decode()
    return uris


if __name__ == "__main__":
    spine = load_spine()
    cat = load_catalogue()
    globals()["CUES"] = load_cues()
    CUES = globals()["CUES"]
    print(f"registered cues loaded: {len(CUES)} (claim_refs + semantic_action)")
    weights = idf_weights(cat)
    tl = build(spine, cat, weights)
    caps_t = [(c["at"], c["until"], c["text"]) for c in tl["captions"]]
    filled = fill_gaps(tl, caps_t, cat, weights, tl["evidence"])
    print(f"gap-fill inserted {filled} solo build(s)")
    (OUT / "timeline.v4.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")

    ev = tl["evidence"]
    docks = [d for sc in tl["scenes"] for d in sc["docks"]]
    print(f"scenes={len(tl['scenes'])} docks={len(docks)} "
          f"avg_hold={sum(d['exit']-d['enter'] for d in docks)/max(1,len(docks)):.1f}s "
          f"max_hold={max((d['exit']-d['enter'] for d in docks), default=0):.1f}s")
    print(f"evidence={len(ev)} slides, {len(set(e['document']['path'] for e in ev.values()))} distinct files")
    print(f"captions={len(tl['captions'])} at canonical timings")
    print(f"badged={sum(1 for e in ev.values() if e['badges'])} (verified numerals only)")
    spans = sorted((d["enter"], d["exit"]) for sc in tl["scenes"] for d in sc["docks"])
    bare, cursor, worst = [], 0.0, 0.0
    for a, b in spans:
        if a > cursor:
            bare.append((round(cursor, 1), round(a, 1), round(a - cursor, 1)))
            worst = max(worst, a - cursor)
        cursor = max(cursor, b)
    if CUT_SECONDS > cursor:
        bare.append((round(cursor, 1), CUT_SECONDS, round(CUT_SECONDS - cursor, 1)))
        worst = max(worst, CUT_SECONDS - cursor)
    over = [g for g in bare if g[2] > MAX_BARE]
    print(f"longest bare plate: {worst:.1f}s  (ceiling {MAX_BARE}s) "
          f"| stretches over ceiling: {len(over)}")
    for g in over:
        print(f"    {g[0]}s -> {g[1]}s  ({g[2]}s bare)")
    for sc in tl["scenes"]:
        ids = [f'{d["slide"]}({d["enter"]:.0f}-{d["exit"]:.0f})' for d in sc["docks"]]
        print(f"  {sc['scene_id']} {sc['span'][0]:6.1f}-{sc['span'][1]:6.1f}  {', '.join(ids) or '(none)'}")
    uris = media(tl, spine)
    (OUT / "uris.json").write_text(json.dumps(uris), encoding="utf-8")
    print(f"payload {sum(len(v) for v in uris.values()) / 1024 / 1024:.1f} MB")

"""THE RECIPE LAB - the batch cards: one queue record per beat shape, a bit and a reason per candidate (P65 T4).

    python content/video_engine/scripts/lab_batch.py --batch smoke-r2 --write
    python content/video_engine/scripts/lab_batch.py --batch smoke-r2 --check

THE RECONCILIATION, and this module's only licence (`authoring/recipes.py:1-20`, `PIPELINE.md:33`): **the lab presents
CANDIDATES built on a TEST BED for the operator's judgement; it authors no episode, it fills no slot by count, and
nothing it cards reaches a cut except as a `proven` recipe or a tracked DEFAULT an author may still refuse.** This
tool JUDGES NOTHING and RANKS NOTHING (E99 s68 Q5 = B, arXiv 2411.04991): it reads `effects/lab/batches/<batch>.jsonl`,
keeps the SURVIVORS the gates and the probe left standing, groups them by beat shape, and writes one `batch` card per
shape into `docs/content-video-engine/review-queue.v1.json`. The page then renders the card's one plain question -

    "which of these beats earns its place, and why not the others?"

- once, with an approve / deny + reason control per candidate, each POSTing `{item: "<card>#<candidate>", choice,
note: "<reason>: <free text>"}` through the existing `/answer` door (the queue's grammar, P65 T4).

TWO THINGS RIDE ALONG, and the card says why (Gao et al. 2022: optimising an imperfect proxy at small N hurts the
thing you actually wanted):

  - EXPLORATION. About a quarter of each shape's candidates are marked `exploration: true` by a SEEDED draw made with
    NO reference to any learner - no approval-rate table, no predicted bit, no ordering. The seed is written into the
    record (`draw.seed`), so the draw is reproducible and auditable, and `--check` re-derives it.
  - CALIBRATION. When `effects/lab/judgements.jsonl` holds an approval older than CALIBRATION_MIN_AGE_DAYS, the
    oldest such candidate is attached to a card again as `calibration: true`, carrying the reason it was judged with
    last time. It is the drift probe: the same beat, judged twice, months apart. The log does not exist until P65 T5
    derives it, so today this branch is dormant and says so.

Nothing here is hand-typed: every label, one line, clip window, build and sheet comes from the run record and from
`effects/lab/candidates.jsonl` (the members are the candidate's own). A candidate with no run record, no clip window,
or no entry in candidates.jsonl is REFUSED BY NAME.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

BATCHES_REL = "content/video_engine/effects/lab/batches"
CANDIDATES_REL = "content/video_engine/effects/lab/candidates.jsonl"
JUDGEMENTS_REL = "content/video_engine/effects/lab/judgements.jsonl"
QUEUE_REL = "docs/content-video-engine/review-queue.v1.json"
PLAN_REL = ".claude/PRPs/plans/P65-THE-RECIPE-LAB.plan.md"

EXPLORATION_SHARE = 0.25          # "about a quarter of each batch" - R26-176 / the blueprint's decision 4
CALIBRATION_MIN_AGE_DAYS = 14     # an approval younger than this is not a drift probe, it is a memory test
QUESTION = "Which of these beats earns its place, and why not the others?"
CARD_PREFIX = "lab-"
CLIP_ROUTE = ("review_queue_proofs.py --clips: the lab's PRIVATE build served read-only, one headless browser seeking "
              "#scrub, 15 fps, ffmpeg H.264 (silent) - the candidate planted into the approved Tokyo cut, which is "
              "never rebuilt (E45, memory review-link-frozen-copy)")
DRAW_WHY = ("drawn with random.Random(seed) over the sorted survivor ids and NO reference to any learner - no "
            "approval-rate table, no predicted bit, no ordering (Gao et al. 2022: a quarter of each batch is watched "
            "whatever the table expects, or the table only ever learns what it already believed)")


class BatchError(ValueError):
    """A run record, a candidate or a queue file the tool refuses; the message names it."""


# ---------------------------------------------------------------- reading

def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise BatchError(f"{path} is not on disk")
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError as exc:
                raise BatchError(f"{path.name} line {n} is not JSON: {exc}") from exc
    return out


def survivors(records: list[dict]) -> list[dict]:
    """The candidates the gates and the probe left standing, sorted by id (the order the cards are written in)."""
    return sorted((r for r in records if r.get("survivor")), key=lambda r: r["id"])


def by_shape(records: list[dict]) -> dict[str, list[dict]]:
    """One card per beat shape: the survivors grouped, shapes in sorted order."""
    groups: dict[str, list[dict]] = {}
    for rec in records:
        if not rec.get("shape"):
            raise BatchError(f"{rec.get('id')}: the run record names no shape")
        groups.setdefault(rec["shape"], []).append(rec)
    return {shape: groups[shape] for shape in sorted(groups)}


def load_members(path: Path) -> dict[str, list[dict]]:
    """Each enumerated candidate's members, by id - the one line on a card is the candidate's OWN members."""
    return {rec["id"]: rec.get("members") or [] for rec in read_jsonl(path)}


def one_line(members: list[dict]) -> str:
    return ", ".join(f"{m['card']} +{float(m['offset_s']):g}s" for m in members)


def digest(candidate_id: str) -> str:
    return candidate_id.rsplit(":", 1)[-1]


def build_aspect(root: Path, build_rel: str) -> str:
    """The aspect the build's own timeline is authored at (the clip is captured at that stage size)."""
    for tl in sorted((root / build_rel).glob("*.timeline.json")):
        try:
            return str(json.loads(tl.read_text(encoding="utf-8")).get("aspect") or "16:9")
        except (OSError, ValueError):
            continue
    return "16:9"


# ---------------------------------------------------------------- the candidates on a card

def clip_proof(rec: dict, root: Path) -> dict:
    """The clip a card shows for one candidate: its OWN window of its OWN private build (E99 s60, a proof is a scene)."""
    clip = rec.get("clip") or {}
    if "t0" not in clip or "t1" not in clip:
        raise BatchError(f"{rec['id']}: the run record carries no clip window - re-run lab_build.py --batch")
    if not rec.get("build"):
        raise BatchError(f"{rec['id']}: the run record names no build dir - re-run lab_build.py --batch")
    beat = rec.get("beat") or {}
    label = f"{rec['shape']} {digest(rec['id'])}"
    if beat.get("sentence"):
        label += f' - the beat on "{beat["sentence"]}"'
    return {"type": "clip", "label": label, "t0": round(float(clip["t0"]), 2), "t1": round(float(clip["t1"]), 2),
            "build": rec["build"], "page": "player.html", "aspect": build_aspect(root, rec["build"]),
            "route": CLIP_ROUTE}


def candidate(rec: dict, members: dict[str, list[dict]], root: Path, explored: set[str]) -> dict:
    if rec["id"] not in members:
        raise BatchError(f"{rec['id']}: not in {CANDIDATES_REL} - run lab_enumerate.py --write first "
                         "(a card's one line is the candidate's own members, never typed here)")
    cand = {"id": rec["id"], "label": f"{digest(rec['id'])} - {rec['shape']}",
            "one_line": one_line(members[rec["id"]]) or "no members on the enumerated record",
            "proof": clip_proof(rec, root)}
    if rec["id"] in explored:
        cand["exploration"] = True
    return cand


def exploration_draw(batch: str, shape: str, ids: list[str], share: float = EXPLORATION_SHARE) -> dict:
    """About `share` of the shape's candidates, drawn with a SEEDED rng and no reference to any learner."""
    seed = f"{batch}:{shape}"
    k = int(len(ids) * share + 0.5)
    drawn = sorted(random.Random(seed).sample(sorted(ids), k)) if k else []
    return {"seed": seed, "share": share, "n": len(ids), "k": k, "drawn": drawn, "why": DRAW_WHY}


# ---------------------------------------------------------------- the calibration probe

def load_judgements(path: Path) -> list[dict]:
    return read_jsonl(path) if path.is_file() else []


def calibration_pick(judgements: list[dict], now: datetime, min_age_days: int = CALIBRATION_MIN_AGE_DAYS) -> dict | None:
    """The OLDEST approval older than `min_age_days`, or None. A drift probe is a beat the operator already approved,
    asked again after enough time that the answer is a judgement and not a memory."""
    cutoff = now - timedelta(days=min_age_days)
    old = []
    for j in judgements:
        if j.get("bit") != "approve" or j.get("superseded"):
            continue
        try:
            at = datetime.fromisoformat(str(j.get("answer_at") or j.get("at")))
        except ValueError:
            continue
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        if at <= cutoff:
            old.append((at, j.get("candidate"), j))
    if not old:
        return None
    at, _cid, j = min(old, key=lambda row: (row[0], row[1] or ""))
    return {"judgement": j, "at": at}


def calibration_candidate(pick: dict, batches_dir: Path, members: dict[str, list[dict]], root: Path) -> dict | None:
    """The approved candidate's own run record, found in any batch on disk, carded again with its prior reason."""
    cid = pick["judgement"].get("candidate")
    for path in sorted(batches_dir.glob("*.jsonl")):
        for rec in read_jsonl(path):
            if rec.get("id") == cid and rec.get("survivor"):
                cand = candidate(rec, members, root, set())
                cand["calibration"] = True
                cand["reason"] = pick["judgement"].get("reason")
                cand["label"] += f" (approved {pick['at'].date().isoformat()}, asked again)"
                return cand
    return None


# ---------------------------------------------------------------- the card

def card_id(batch: str, shape: str) -> str:
    return f"{CARD_PREFIX}{batch}-{shape}"


def card(batch: str, shape: str, recs: list[dict], members: dict[str, list[dict]], root: Path, built: int,
         hg1: bool = False) -> dict:
    ids = [r["id"] for r in recs]
    draw = exploration_draw(batch, shape, ids)
    cands = [candidate(r, members, root, set(draw["drawn"])) for r in recs]
    proofs = [c["proof"] for c in cands]
    where = [{"label": f"the probe sheet for {digest(r['id'])} - the candidate's own instants", "path": r["sheet"]}
             for r in recs if r.get("sheet")]
    where.append({"label": f"the run record: every gate row that decided each candidate of batch {batch}",
                  "path": f"{BATCHES_REL}/{batch}.jsonl"})
    where.append({"label": "the enumerated space these candidates were drawn from (members, offsets, clocks)",
                  "path": CANDIDATES_REL})
    where.append({"label": "the plan, its Human Gates and the batch's queue grammar", "path": PLAN_REL})
    judge = (f"{QUESTION} Each candidate below is ONE beat - the shape `{shape}` - built on the Tokyo bed inside the "
             f"approved cut and left standing by the gates and the probe ({len(recs)} of {built} built for this shape "
             f"survived). Give each its own bit and its own reason: an approve carries `good`, a deny carries the one "
             f"of the eight that killed it. The gates FILTERED; nothing here is judged, ranked or scored by an agent.")
    if hg1:
        judge += (" AND THE GRAMMAR ITSELF IS ON TRIAL: one card per beat shape with a bit + a reason per candidate - "
                  "does this work for you, or do you want one card per candidate at a lower rate? Answer that on the "
                  "card's own control below.")
    recommendation = ("None on which beat wins - that is your bit, not the agent's (E99 s68). The agent recommends "
                      "only what the record shows: " + ("no candidate is marked exploration here (the draw is "
                      f"{EXPLORATION_SHARE:.0%} of {draw['n']}, which rounds to none)" if not draw["k"] else
                      f"{draw['k']} of {draw['n']} are marked exploration and are in front of you whatever a learner "
                      "would predict") + ".")
    if hg1:
        recommendation += (" On the grammar: keep one card per beat shape - it is the only form in which a denial "
                           "carries a reason, which is what E99 s68 asked for. The agent's recommendation, not a ruling.")
    return {
        "id": card_id(batch, shape),
        "status": "open",
        "kind": "batch",
        "title": (f"P65 HG1 - the first batch: " if hg1 else "The recipe lab - ")
                 + f"{shape}, {len(cands)} candidate(s) side by side (batch {batch})",
        "ids": (["P65 HG1"] if hg1 else ["P65 T4"]) + ["E99 s68", "R26-176"],
        "judge": judge,
        "where": where,
        "proofs": proofs,
        "candidates": cands,
        "options": (["the batch grammar works - keep one card per beat shape",
                     "one card per candidate instead, at a lower rate"] if hg1 else []),
        "recommendation": recommendation,
        "blocks": ("P65 T5 (the approval log has nothing to derive until an answer exists) and every later batch"
                   if hg1 else "the promotion of these candidates (P65 T6): nothing becomes a proven recipe or a "
                               "tracked default without your bit"),
        "sources": [f"{PLAN_REL} (T4, the batch's queue grammar)",
                    "docs/portable/OPERATOR-RULINGS.md (E99 s68: present as batches, track approvals AND denials)",
                    "docs/content-video-engine/BACKLOG.md (R26-176: the space is finite; the lab enumerates it)",
                    f"{BATCHES_REL}/{batch}.jsonl (the gate rows behind every survivor)"],
        "ruling": "",
        "was_kind": "",
        "owed": "",
        "draw": draw,
    }


def cards(batch: str, records: list[dict], members: dict[str, list[dict]], root: Path, judgements: list[dict],
          now: datetime, hg1: bool = False, batches_dir: Path | None = None) -> list[dict]:
    kept = survivors(records)
    if not kept:
        raise BatchError(f"batch {batch}: no survivor in the run record - a batch with nothing standing is not a card "
                         "(every candidate is recorded with the row that killed it; read it before re-running)")
    built = {}
    for rec in records:
        built[rec.get("shape")] = built.get(rec.get("shape"), 0) + 1
    out = [card(batch, shape, recs, members, root, built.get(shape, len(recs)), hg1=hg1)
           for shape, recs in by_shape(kept).items()]
    pick = calibration_pick(judgements, now)
    if pick:
        cand = calibration_candidate(pick, batches_dir or (root / BATCHES_REL), members, root)
        if cand is None:
            print(f"calibration: {pick['judgement'].get('candidate')} was approved on "
                  f"{pick['at'].date().isoformat()} but no batch record on disk carries it as a survivor - "
                  "no probe attached", file=sys.stderr)
        else:
            shape = cand["id"].split(":")[1] if cand["id"].count(":") >= 2 else None
            host = next((c for c in out if c["id"] == card_id(batch, shape)), out[0])
            host["candidates"].append(cand)
            host["proofs"].append(cand["proof"])
            host["judge"] += (f" One candidate here is a CALIBRATION PROBE: you approved it on "
                              f"{pick['at'].date().isoformat()} and it is asked again, unchanged, to measure drift.")
    return out


# ---------------------------------------------------------------- the queue file

def load_queue(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise BatchError(f"{path.name}: the queue is one object with an 'items' list")
    return data


def queue_newline(path: Path) -> str:
    """The line ending the queue file already uses: a card is added to it, never a re-encoding of the whole file."""
    return "\r\n" if b"\r\n" in path.read_bytes() else "\n"


def dump_queue(path: Path, data: dict) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_bytes(text.replace("\n", queue_newline(path)).encode("utf-8"))


def merge(data: dict, new: list[dict]) -> dict:
    """Replace each card in place when it is already there, append the rest in order. Nothing else is touched."""
    items = list(data["items"])
    by_id = {rec["id"]: n for n, rec in enumerate(items)}
    for rec in new:
        if rec["id"] in by_id:
            items[by_id[rec["id"]]] = rec
        else:
            items.append(rec)
    return {**data, "items": items}


def stale(data: dict, new: list[dict]) -> list[str]:
    by_id = {rec["id"]: rec for rec in data["items"]}
    return [rec["id"] for rec in new if by_id.get(rec["id"]) != rec]


# ---------------------------------------------------------------- cli

def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the batch's cards into the review queue")
    mode.add_argument("--check", action="store_true", help="exit 1 when a card on the queue is not what this batch says")
    ap.add_argument("--batch", required=True, help="the batch id: effects/lab/batches/<batch>.jsonl")
    ap.add_argument("--hg1", action="store_true", help="frame these cards as P65 HG1 (the grammar is on trial too)")
    ap.add_argument("--record", type=Path, help=f"the run record (default {BATCHES_REL}/<batch>.jsonl)")
    ap.add_argument("--candidates", type=Path, default=ROOT / CANDIDATES_REL)
    ap.add_argument("--judgements", type=Path, default=ROOT / JUDGEMENTS_REL)
    ap.add_argument("--batches-dir", type=Path, default=ROOT / BATCHES_REL)
    ap.add_argument("--queue", type=Path, default=ROOT / QUEUE_REL)
    ap.add_argument("--root", type=Path, default=ROOT, help="where a build dir and a sheet path resolve")
    ap.add_argument("--now", help="the instant the calibration age is measured from (ISO 8601; tests)")
    return ap.parse_args(argv)


def build_cards(args: argparse.Namespace) -> list[dict]:
    record = args.record or (args.batches_dir / f"{args.batch}.jsonl")
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return cards(args.batch, read_jsonl(record), load_members(args.candidates), args.root,
                 load_judgements(args.judgements), now, hg1=args.hg1, batches_dir=args.batches_dir)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        new = build_cards(args)
        data = load_queue(args.queue)
    except (OSError, ValueError) as exc:
        print(f"lab batch refused: {exc}", file=sys.stderr)
        return 2
    if args.check:
        bad = stale(data, new)
        if bad:
            print(f"STALE: {', '.join(bad)} in {args.queue.name} is not what batch {args.batch} says - "
                  f"run lab_batch.py --batch {args.batch} --write", file=sys.stderr)
            return 1
        print(f"ok: {len(new)} card(s) of batch {args.batch} are current in {args.queue.name}")
        return 0
    dump_queue(args.queue, merge(data, new))
    for rec in new:
        marks = sum(1 for c in rec["candidates"] if c.get("exploration"))
        cal = sum(1 for c in rec["candidates"] if c.get("calibration"))
        print(f"{rec['id']}: {len(rec['candidates'])} candidate(s), {marks} exploration, {cal} calibration "
              f"(seed {rec['draw']['seed']})")
    print(f"{args.queue} - now run: python content/video_engine/scripts/review_queue_proofs.py --clips --only "
          f"{new[0]['id']} && python content/video_engine/scripts/build_review_queue.py --write")
    return 0


if __name__ == "__main__":
    sys.exit(main())

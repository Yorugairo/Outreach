"""THE RECIPE LAB - the approval log and the learner (P65 T5).

    python content/video_engine/scripts/lab_log.py --write    # judgements.jsonl, derived from the answers ONLY
    python content/video_engine/scripts/lab_log.py --table    # approval-rates.json + approval-rates.md
    python content/video_engine/scripts/lab_log.py --check    # derive and compare; write nothing

NOTHING HERE IS HAND-TYPED. The one and only input is `docs/content-video-engine/review-answers.jsonl` - the
operator's own answers, appended by `serve_review_queue.py` and never edited. Each answer whose `item` carries the
batch separator (`<card-id>#<candidate-id>`, P65 T4) becomes ONE `lab_judgements.v1` record: the bit, the reason
category the note opens with, the instant of proof (the clip the card showed and the second inside it the note names,
defaulting to the clip's t0), the operator, the answer's timestamp. A candidate the card does not carry, a reason off
the fixed nine, a candidate with no clip - REFUSED BY NAME, and nothing is written.

THIS MODULE JUDGES NOTHING AND RANKS NOTHING (E99 s68 Q5 = B). `--table` is a COUNTING table: for every feature a
candidate carries - its beat shape, each of its member cards, the clock it was built against - how many judgements
that feature has seen, how many were approvals, the raw share, and that share pulled toward the batch's own prior by
a small Beta(a, b). No ranking model and no head-to-head preference model is fitted here, and none will be until the
log is in the HUNDREDS of judgements (arXiv 2411.04991: a preference model fitted on a handful of comparisons is
noise wearing a number). The reason categories ride beside every rate and are never collapsed into it (Gao et al.
2022: optimising an imperfect proxy at small N costs you the thing you actually wanted - the reason is the part a
human can act on).

A judgement's candidate is resolved through the CARD (`docs/content-video-engine/review-queue.v1.json`) and then
through the run record of the batch that card names (`effects/lab/batches/<batch>.jsonl`), so the clip, the build and
the beat shape are the lab's own record of what was actually on the screen, not this module's invention.

THE CANDIDATE FORMS: `lab_judgement.schema.json` `$defs.candidate_id` admits the enumerated form `lab:<shape>:<8 hex>`
and the re-proof form `recipe:<name>` (widened 2026-09-17 when the HG2 card's six answers landed); this module asserts the
schema's pattern is the one it expects and never rewrites it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_review_queue as BRQ  # noqa: E402  (the queue's own loader, reason list and batch separator)

ANSWERS_REL = "docs/content-video-engine/review-answers.jsonl"
QUEUE_REL = "docs/content-video-engine/review-queue.v1.json"
BATCHES_REL = "content/video_engine/effects/lab/batches"
CANDIDATES_REL = "content/video_engine/effects/lab/candidates.jsonl"
RECIPES_REL = "content/video_engine/effects/recipes"
JUDGEMENTS_REL = "content/video_engine/effects/lab/judgements.jsonl"
TABLE_JSON_REL = "content/video_engine/effects/lab/approval-rates.json"
TABLE_MD_REL = "content/video_engine/effects/lab/approval-rates.md"
SCHEMA_REL = "content/video_engine/configs/lab_judgement.schema.json"

SCHEMA_VERSION = "lab_judgements.v1"
TABLE_VERSION = "lab_approval_rates.v1"
CANDIDATE_PATTERN = r"^(lab:[a-z0-9-]+:[0-9a-f]{8}|recipe:[a-z0-9-]+)$"
PRIOR_STRENGTH = 2.0      # "a small prior": two pseudo-judgements, so a single real observation cannot reach 0 or 1
PRIOR_FLOOR = 0.10        # the prior rate is held off the ends, or an all-approve batch would print 1.00 at n=1
PRIOR_CEIL = 0.90
BIG_ENOUGH_FOR_A_MODEL = 300   # arXiv 2411.04991: the table stays a table until the log is in the hundreds

FEATURE_KINDS = ("shape", "member", "clock")
LIMIT = ("THE LEARNER IS A TABLE, NOT A MODEL. Every cell is a count and a shrunk share; no ranking model and no "
         "head-to-head preference model is fitted anywhere in lab_log.py, and none will be until this log holds "
         f"{BIG_ENOUGH_FOR_A_MODEL}+ judgements (arXiv 2411.04991). The reason categories are carried beside every "
         "rate and never collapsed into it (Gao et al. 2022): the rate says how often, only the reason says why, and "
         "the reason is the part an agent can act on. A cell's rate is its count shrunk toward the log's own prior, "
         "so a feature seen once never reads 1.00 or 0.00 - read the n before the rate.")
CITATIONS = ("arXiv 2411.04991 (a preference model fitted at small N is noise wearing a number)",
             "Gao et al. 2022 (optimising an imperfect proxy at small N costs the thing you wanted)")

TIME_AT = re.compile(r"\bat\s+(\d+(?:\.\d+)?)\s*s(?:ec(?:onds?)?)?\b", re.I)
TIME_CLOCK = re.compile(r"\b(\d{1,2}):(\d{2}(?:\.\d+)?)\b")


class LogError(ValueError):
    """A refusal; the message names the answer, the candidate and what was wrong with it."""


# ---------------------------------------------------------------- loading


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except ValueError as exc:
            raise LogError(f"{path.name} line {n} is not JSON: {exc}") from exc
    return out


def load_schema(root: Path) -> dict:
    """The judgement schema as the file carries it; its candidate pattern must be the two forms this module reads."""
    schema = json.loads((root / SCHEMA_REL).read_text(encoding="utf-8"))
    found = schema["$defs"]["candidate_id"]["pattern"]
    if found != CANDIDATE_PATTERN:
        raise SystemExit(f"FAIL: {SCHEMA_REL} candidate pattern {found!r} is not the two forms lab_log.py reads")
    return schema


def load_cards(root: Path) -> dict:
    queue = json.loads((root / QUEUE_REL).read_text(encoding="utf-8"))
    return {rec["id"]: rec for rec in queue.get("items", []) if isinstance(rec, dict) and "id" in rec}


def card_batch(card: dict) -> str:
    """The batch whose run record the card names - the one file the lab wrote the candidates' builds into."""
    hay = json.dumps(card)
    names = re.findall(r"effects/lab/batches/([A-Za-z0-9._-]+)\.jsonl", hay)
    return names[0] if names else ""


def load_runs(root: Path, batch: str) -> dict:
    path = root / BATCHES_REL / f"{batch}.jsonl"
    return {r["id"]: r for r in read_jsonl(path) if isinstance(r, dict) and "id" in r}


def load_enumerated(root: Path) -> dict:
    return {r["id"]: r for r in read_jsonl(root / CANDIDATES_REL) if isinstance(r, dict) and "id" in r}


# ---------------------------------------------------------------- derivation


def note_parts(note: object) -> tuple[str, str]:
    """(reason, free text) - the note opens with a category from the fixed list and qualifies it after the colon."""
    text = note if isinstance(note, str) else ""
    head, _, rest = text.partition(":")
    return head.strip(), rest.strip()


def instant(note: str, t0: float, t1: float) -> float:
    """The second inside the clip the note names ('at 4.57 s', '0:55'), else the clip's own t0."""
    for raw in TIME_AT.findall(note or ""):
        t = float(raw)
        if t0 <= t <= t1:
            return round(t, 3)
    for mins, secs in TIME_CLOCK.findall(note or ""):
        t = int(mins) * 60 + float(secs)
        if t0 <= t <= t1:
            return round(t, 3)
    return round(float(t0), 3)


def candidate_clip(card: dict, candidate: str, run: dict) -> tuple[str, float, float]:
    """The clip the card showed this candidate on: its path or the private build, and the window it played."""
    entry = next((c for c in card.get("candidates", []) if c.get("id") == candidate), None)
    proof = (entry or {}).get("proof") or {}
    clip = proof.get("path") or proof.get("clip") or proof.get("build") or (run or {}).get("build") or ""
    window = proof if "t0" in proof else (run or {}).get("clip") or {}
    if not clip or "t0" not in window:
        raise LogError(f"candidate {candidate} on card {card.get('id')}: no clip proof - a judgement's proof is a "
                       f"scene (E99 s60) and there is no instant to point at")
    return str(clip), float(window["t0"]), float(window.get("t1", window["t0"]))


def derive(root: Path, now: str | None = None) -> tuple[list[dict], list[str]]:
    """One judgement per candidate answer, in the answers' own order; refusals collected and named, never dropped."""
    reasons = BRQ.load_reasons(root)
    cards = load_cards(root)
    runs_cache: dict[str, dict] = {}
    kept: list[dict] = []
    refusals: list[str] = []
    stamp = now or datetime.now(timezone.utc).isoformat(timespec="seconds")
    known_at = {(r.get("candidate"), r.get("answer_at")): r.get("at")
                for r in read_jsonl(root / JUDGEMENTS_REL)}

    for answer in read_jsonl(root / ANSWERS_REL):
        item = answer.get("item", "")
        if BRQ.BATCH_SEP not in item:
            continue
        card_id, _, candidate = item.partition(BRQ.BATCH_SEP)
        card = cards.get(card_id)
        if card is None or card.get("kind") != "batch":
            refusals.append(f"{item}: card {card_id!r} is not a batch card on the queue")
            continue
        if not any(c.get("id") == candidate for c in card.get("candidates", [])):
            refusals.append(f"{item}: unknown candidate {candidate!r} - card {card_id} carries "
                            f"{[c.get('id') for c in card.get('candidates', [])]}")
            continue
        choice = answer.get("choice")
        if choice not in BRQ.BATCH_CHOICES:
            refusals.append(f"{item}: choice {choice!r} is not one of {list(BRQ.BATCH_CHOICES)}")
            continue
        reason, free = note_parts(answer.get("note"))
        if reason not in reasons:
            refusals.append(f"{item}: the note opens with {reason!r}, which is not one of the nine reasons "
                            f"{list(reasons)}")
            continue
        batch = card_batch(card)
        if not batch:
            refusals.append(f"{item}: card {card_id} names no effects/lab/batches/<batch>.jsonl run record")
            continue
        if batch not in runs_cache:
            runs_cache[batch] = load_runs(root, batch)
        run = runs_cache[batch].get(candidate)
        if run is None:
            refusals.append(f"{item}: candidate {candidate!r} has no run record in {batch}.jsonl")
            continue
        try:
            clip, t0, t1 = candidate_clip(card, candidate, run)
        except LogError as exc:
            refusals.append(f"{item}: {exc}")
            continue
        answer_at = str(answer.get("at", ""))
        record = {
            "candidate": candidate,
            "bit": choice,
            "reason": reason,
            "proof": {"clip": clip, "t": instant(free, t0, t1)},
            "at": known_at.get((candidate, answer_at)) or stamp,
            "by": str(answer.get("by") or "operator"),
            "answer_at": answer_at,
        }
        if free:
            record["note"] = free
        kept.append(record)

    latest: dict[str, int] = {}
    for i, rec in enumerate(kept):
        cid = rec["candidate"]
        if cid not in latest or (rec["answer_at"], i) >= (kept[latest[cid]]["answer_at"], latest[cid]):
            latest[cid] = i
    for i, rec in enumerate(kept):
        rec.pop("superseded", None)
        if latest[rec["candidate"]] != i:
            rec["superseded"] = True
    return kept, refusals


def validate(records: list[dict], schema: dict) -> None:
    """Every record against `lab_judgements.v1` (additionalProperties: false) - the schema is the contract."""
    validator = jsonschema.Draft202012Validator(schema)
    for rec in records:
        errors = sorted(validator.iter_errors(rec), key=lambda e: list(e.path))
        if errors:
            raise LogError(f"judgement for {rec.get('candidate')!r} is not {SCHEMA_VERSION}: "
                           f"{'; '.join(e.message for e in errors)}")
        for field in ("at", "answer_at"):
            try:
                datetime.fromisoformat(rec[field])
            except ValueError as exc:
                raise LogError(f"judgement for {rec['candidate']!r} has a {field} that is not "
                               f"ISO 8601: {exc}") from exc


def dumps(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)


# ---------------------------------------------------------------- the table


def features(root: Path, candidate: str, run: dict) -> list[str]:
    """Every feature the candidate carries: its beat shape, each member card once, and the clock it was built to."""
    out: list[str] = []
    shape = (run or {}).get("shape")
    if shape:
        out.append(f"shape:{shape}")
    members: list[str] = []
    clocks: dict = {}
    if candidate.startswith("recipe:"):
        path = root / RECIPES_REL / f"{candidate.split(':', 1)[1]}.json"
        if path.exists():
            recipe = json.loads(path.read_text(encoding="utf-8"))
            members = [m.get("card", "") for m in recipe.get("members", [])]
            if recipe.get("window_s") is not None:
                clocks = {"window_s": recipe["window_s"]}
    else:
        rec = load_enumerated(root).get(candidate, {})
        members = [m.get("card", "") for m in rec.get("members", [])]
        clocks = rec.get("clocks", {}) or {}
    for card in sorted({m for m in members if m}):
        out.append(f"member:{card}")
    for name in sorted(clocks):
        out.append(f"clock:{name}={clocks[name]}")
    return out


def shrunk(approvals: int, n: int, prior_rate: float, strength: float = PRIOR_STRENGTH) -> float:
    """The cell's rate pulled toward the prior: (k + a) / (n + a + b), a = strength * prior, b = strength - a."""
    a = strength * prior_rate
    b = strength * (1.0 - prior_rate)
    return (approvals + a) / (n + a + b)


def batch_runs(root: Path) -> dict:
    """Every run record any batch card on the queue names - the candidates' own shapes and builds."""
    runs: dict[str, dict] = {}
    for card in load_cards(root).values():
        if card.get("kind") != "batch":
            continue
        batch = card_batch(card)
        if batch:
            runs.update(load_runs(root, batch))
    return runs


def table(root: Path, records: list[dict], now: str | None = None) -> dict:
    """The per-feature counting table: n, the bits, the raw share and the share shrunk toward the log's own prior."""
    live = [r for r in records if not r.get("superseded")]
    runs = batch_runs(root)
    total = len(live)
    approvals = sum(1 for r in live if r["bit"] == "approve")
    raw_prior = (approvals / total) if total else 0.5
    prior_rate = min(max(raw_prior, PRIOR_FLOOR), PRIOR_CEIL)
    cells: dict[str, dict] = {}
    for rec in live:
        for feature in features(root, rec["candidate"], runs.get(rec["candidate"], {})):
            cell = cells.setdefault(feature, {"feature": feature, "kind": feature.split(":", 1)[0], "n": 0,
                                              "approve": 0, "deny": 0, "reasons": {}, "candidates": []})
            cell["n"] += 1
            cell["approve" if rec["bit"] == "approve" else "deny"] += 1
            cell["reasons"][rec["reason"]] = cell["reasons"].get(rec["reason"], 0) + 1
            if rec["candidate"] not in cell["candidates"]:
                cell["candidates"].append(rec["candidate"])
    rows = []
    for cell in cells.values():
        cell["raw_rate"] = round(cell["approve"] / cell["n"], 4) if cell["n"] else None
        cell["rate"] = round(shrunk(cell["approve"], cell["n"], prior_rate), 4)
        cell["reasons"] = dict(sorted(cell["reasons"].items(), key=lambda kv: (-kv[1], kv[0])))
        cell["candidates"] = sorted(cell["candidates"])
        rows.append(cell)
    rows.sort(key=lambda c: (FEATURE_KINDS.index(c["kind"]) if c["kind"] in FEATURE_KINDS else 9,
                             -c["n"], c["feature"]))
    return {
        "schema_version": TABLE_VERSION,
        "at": now or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": f"{JUDGEMENTS_REL} (derived from {ANSWERS_REL} by lab_log.py --write; nothing hand-typed)",
        "limit": LIMIT,
        "citations": list(CITATIONS),
        "judgements": {"live": total, "approve": approvals, "deny": total - approvals,
                       "superseded": len(records) - total, "candidates": len({r["candidate"] for r in live})},
        "prior": {"family": "Beta", "strength": PRIOR_STRENGTH, "rate": round(prior_rate, 4),
                  "observed_rate": round(raw_prior, 4), "a": round(PRIOR_STRENGTH * prior_rate, 4),
                  "b": round(PRIOR_STRENGTH * (1.0 - prior_rate), 4),
                  "held_off_the_ends": [PRIOR_FLOOR, PRIOR_CEIL],
                  "rule": "rate = (approvals + a) / (n + a + b)"},
        "features": rows,
    }


def table_md(data: dict) -> str:
    p = data["prior"]
    j = data["judgements"]
    lines = ["# The recipe lab - approval rate per feature", "",
             f"_Derived {data['at']} from `{JUDGEMENTS_REL}`, itself derived from `{ANSWERS_REL}` only "
             f"(P65 T5). Never hand-edited._", "",
             f"**The limit.** {data['limit']}", "",
             "Citations: " + "; ".join(data["citations"]) + ".", "",
             f"**The numbers.** {j['live']} live judgements over {j['candidates']} candidates "
             f"({j['approve']} approve / {j['deny']} deny; {j['superseded']} superseded and kept). The prior is "
             f"Beta(a={p['a']}, b={p['b']}) - strength {p['strength']} pseudo-judgements at the log's own approval "
             f"rate {p['observed_rate']}, held inside [{p['held_off_the_ends'][0]}, {p['held_off_the_ends'][1]}] so "
             f"no cell can read 1.00 or 0.00 on one observation. Every cell: {p['rule']}.", "",
             "| feature | kind | n | approve | deny | raw | shrunk | reasons (carried, never collapsed) |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for row in data["features"]:
        reasons = "; ".join(f"{k} x{v}" for k, v in row["reasons"].items())
        lines.append(f"| `{row['feature']}` | {row['kind']} | {row['n']} | {row['approve']} | {row['deny']} | "
                     f"{row['raw_rate']:.2f} | {row['rate']:.2f} | {reasons} |")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- cli


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="The recipe lab's approval log and its per-feature table (P65 T5).")
    ap.add_argument("--write", action="store_true", help="derive judgements.jsonl from the answers")
    ap.add_argument("--table", action="store_true", help="write approval-rates.json and approval-rates.md")
    ap.add_argument("--check", action="store_true", help="derive and compare; write nothing")
    ap.add_argument("--root", default=str(ROOT))
    args = ap.parse_args(argv)
    root = Path(args.root)
    if not (args.write or args.table or args.check):
        ap.error("say --write, --table or --check")

    records, refusals = derive(root)
    if refusals:
        for line in refusals:
            print(f"[REFUSED] {line}")
        print(f"[FAIL] {len(refusals)} answer(s) refused by name; nothing written")
        return 2
    validate(records, load_schema(root))
    text = dumps(records)
    path = root / JUDGEMENTS_REL

    if args.write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        live = [r for r in records if not r.get("superseded")]
        print(f"[ok] {len(records)} judgement(s) -> {JUDGEMENTS_REL} "
              f"({len(live)} live, {len(records) - len(live)} superseded and kept)")
        for rec in records:
            flag = " (superseded)" if rec.get("superseded") else ""
            print(f"  {rec['candidate']}  {rec['bit']}  {rec['reason']}  @ t={rec['proof']['t']}{flag}")
    if args.check:
        on_disk = path.read_text(encoding="utf-8") if path.exists() else ""
        if on_disk != text:
            print(f"[FAIL] {JUDGEMENTS_REL} is not what the answers derive to - run --write")
            return 1
        print(f"[ok] {JUDGEMENTS_REL} is exactly what {len(records)} answer(s) derive to")
    if args.table:
        data = table(root, records)
        (root / TABLE_JSON_REL).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (root / TABLE_MD_REL).write_text(table_md(data), encoding="utf-8")
        print(f"[ok] {len(data['features'])} feature(s) -> {TABLE_JSON_REL} + {TABLE_MD_REL}; prior Beta("
              f"a={data['prior']['a']}, b={data['prior']['b']}) at rate {data['prior']['rate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

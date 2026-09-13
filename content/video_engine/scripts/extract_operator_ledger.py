"""P54 T1 - the operator ledger: every message the OPERATOR typed into the Claude transcripts for this repo, with what
the agent said next and how much work followed. Deterministic, read-only on the transcripts, streams multi-GB files
line by line. Ported from the session-45114c3b scratchpad prototype (census 185 files, 1,639 messages).

    python extract_operator_ledger.py                  # incremental: append messages newer than the ledger's last ts
    python extract_operator_ledger.py --full           # rebuild LEDGER.jsonl from scratch
    python extract_operator_ledger.py --check          # write nothing; exit 1 when newer operator messages exist
    python extract_operator_ledger.py --md <path>      # also write the day-grouped markdown (on demand, never in docs/)
    python extract_operator_ledger.py --triage-check   # every correction/rule row has one valid TRIAGE.jsonl verdict

Writes <out>/LEDGER.jsonl only (one row per message, sorted by ts). The markdown is opt-in: docs_find indexes
docs/**/*.md, and a section per chat message would flood every search. Cue tags are cheap substring hints for triage.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROJECTS = str(Path.home() / ".claude" / "projects" / "*Outreach-Program*" / "**" / "*.jsonl")
DEFAULT_OUT = ROOT / "docs" / "operator-ledger"
SKIP_PREFIXES = ("<local-command", "<command-name>", "<command-message>", "Caveat:", "[Request interrupted",
                 "This session is being continued", "<task-notification>", "[SYSTEM NOTIFICATION")
REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
CUES = {
    "correction": re.compile(r"\b(not|don'?t|dont|wrong|misinterpret\w*|instead|isn'?t|never|stop|backwards|broke|lost)\b", re.I),
    "rule": re.compile(r"\b(always|never|as a rule|should|must|the answer is|standard)\b", re.I),
    "approval": re.compile(r"\b(approved?|looks good|works|awesome|perfect|beats|love|great|real capability)\b", re.I),
    "question": re.compile(r"\?"),
    "why": re.compile(r"\b(why|what caused|how come|reason)\b", re.I),
}
FILTERED_SLASH = ("/model",)          # their args are model names, not the operator's words
NEAR_DUP_SECONDS = 600
REPLY_CHARS = 600
MD_REPLY_CHARS = 400
MD_PASTED_CHARS = 200
PASTED_CHARS = 3000
VERDICTS = ("recorded", "ruling-candidate", "gate-candidate", "craft", "memory", "episode", "noise", "conflict",
            "superseded")
TRIAGE_CUES = ("correction", "rule")
ROW_ID = re.compile(r"^[0-9a-f]{12}$")
RULING_ID = re.compile(r"^[A-E]\d+[a-z]?$")   # E73, and the older series: D1, B2


def text_of(content) -> tuple[str, int]:
    """(the typed text, number of images) of a user message; tool results are not typed text."""
    if isinstance(content, str):
        return content, 0
    parts, images = [], 0
    for b in content or []:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "text":
            parts.append(b.get("text") or "")
        elif b.get("type") == "image":
            images += 1
    return "\n".join(parts), images


def clean(t: str) -> str:
    return REMINDER.sub("", t).strip()


def row_id(ts, text: str) -> str:
    return hashlib.sha1((str(ts) + text).encode("utf-8")).hexdigest()[:12]


def parse_ts(ts) -> datetime | None:
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None


def operator_text(rec: dict, att: dict | None) -> tuple[str, int, str, str]:
    """(text, images, via, slash) of an operator record; slash commands yield the words in <command-args>."""
    if att is not None:
        txt, imgs = text_of(att.get("prompt"))
        via = "mid-turn"
    else:
        txt, imgs = text_of((rec.get("message") or {}).get("content"))
        via = "typed"
    txt, slash = clean(txt), ""
    if "<command-args>" in txt:
        m_name = re.search(r"<command-name>(.*?)</command-name>", txt, re.S)
        m_args = re.search(r"<command-args>(.*?)</command-args>", txt, re.S)
        slash = m_name.group(1).strip() if m_name else ""
        txt = m_args.group(1).strip() if m_args else ""
        via = "slash"
    return txt, imgs, via, slash


def skip_reason(rec: dict, sidechain_file: bool, txt: str, imgs: int, slash: str) -> str:
    """Why a user/queued record is not an operator message ('' when it is one)."""
    if sidechain_file or rec.get("isSidechain"):
        return "sidechain"
    if rec.get("isMeta") or rec.get("isCompactSummary") or rec.get("isVisibleInTranscriptOnly"):
        return "meta/compact"
    if slash in FILTERED_SLASH:
        return "model-slash"
    if not txt and not imgs:
        return "tool_result/empty"
    if txt.startswith(SKIP_PREFIXES) or txt.lstrip().startswith('{"packetId"'):
        return "harness"
    return ""


def make_row(rec: dict, fp: str, txt: str, imgs: int, via: str, slash: str) -> dict:
    ts = rec.get("timestamp")
    return {"id": row_id(ts, txt), "ts": ts, "session": rec.get("sessionId"), "cwd": rec.get("cwd"),
            "file": Path(fp).parent.name, "text": txt, "images": imgs, "reply": "", "tool_calls": 0,
            "via": via, "slash": slash,
            "pasted": bool("Traceback (most recent call last)" in txt or txt.startswith('@"') or len(txt) > PASTED_CHARS),
            "cues": sorted(k for k, rx in CUES.items() if rx.search(txt))}


def absorb_assistant(rec: dict, pending: dict) -> None:
    for b in (rec.get("message") or {}).get("content") or []:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "tool_use":
            pending["tool_calls"] += 1
        elif b.get("type") == "text" and not pending["reply"]:
            pending["reply"] = (b.get("text") or "").strip()[:REPLY_CHARS]


def scan_file(fp: str, shapes: Counter, seen: set[str]) -> list[dict]:
    rows: list[dict] = []
    sidechain_file = "subagents" in Path(fp).parts
    pending: dict | None = None
    with open(fp, "rb") as fh:
        for raw in fh:
            # byte pre-filter: most lines of a multi-GB transcript are tool output
            if not (b'"type":"user"' in raw or b'"type":"assistant"' in raw or b'"queued_command"' in raw):
                continue
            try:
                rec = json.loads(raw)
            except ValueError:
                shapes["unparseable"] += 1
                continue
            kind = rec.get("type")
            if kind == "assistant":
                if pending is not None:
                    absorb_assistant(rec, pending)
                continue
            att = rec.get("attachment") if kind == "attachment" else None
            if not (kind == "user" or (isinstance(att, dict) and att.get("type") == "queued_command")):
                continue
            txt, imgs, via, slash = operator_text(rec, att)
            reason = skip_reason(rec, sidechain_file, txt, imgs, slash)
            if reason:
                shapes[reason] += 1
                continue
            key = hashlib.sha1((str(rec.get("timestamp")) + txt).encode("utf-8")).hexdigest()
            if key in seen:
                shapes["duplicate"] += 1
                continue
            seen.add(key)
            pending = make_row(rec, fp, txt, imgs, via, slash)
            rows.append(pending)
    return rows


def collect(pattern: str) -> tuple[list[dict], Counter, int]:
    shapes: Counter = Counter()
    seen: set[str] = set()
    rows: list[dict] = []
    files = sorted(glob.glob(pattern, recursive=True), key=lambda p: Path(p).stat().st_size)
    for fp in files:
        rows.extend(scan_file(fp, shapes, seen))
    rows.sort(key=lambda r: str(r["ts"]))
    return rows, shapes, len(files)


def norm(text: str) -> str:
    return " ".join(text.split()).lower()


def drop_near_duplicates(rows: list[dict], seed: list[dict] = ()) -> tuple[list[dict], int]:
    """Keep the first of the same normalised text within NEAR_DUP_SECONDS of an earlier KEPT row (seed rows count)."""
    last_kept: dict[str, datetime] = {}
    for r in seed:
        t = parse_ts(r["ts"])
        if t is not None and norm(r["text"]):
            last_kept[norm(r["text"])] = t
    kept, dropped = [], 0
    for r in rows:
        key, t = norm(r["text"]), parse_ts(r["ts"])
        prev = last_kept.get(key)
        if key and t is not None and prev is not None and 0 <= (t - prev).total_seconds() <= NEAR_DUP_SECONDS:
            dropped += 1
            continue
        if key and t is not None:
            last_kept[key] = t
        kept.append(r)
    return kept, dropped


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def md_entry(r: dict) -> str:
    hhmm = str(r["ts"])[11:16]
    img = f" [+{r['images']} image]" if r["images"] else ""
    via = r["via"] + (f" {r['slash']}" if r.get("slash") else "")
    head = f"### {hhmm} `{r['id']}` {via} `{','.join(r['cues']) or '-'}` - {r['tool_calls']} tool calls after{img}\n\n"
    if r["pasted"]:
        body = r["text"][:MD_PASTED_CHARS] + f" [pasted, {len(r['text'].split())} words - full text in LEDGER.jsonl]"
    else:
        body = r["text"]
    out = head + "> " + body.replace("\n", "\n> ") + "\n\n"
    if r["reply"]:
        out += "**Agent, first words after:** " + r["reply"].replace("\n", " ")[:MD_REPLY_CHARS] + "\n\n"
    return out


def render_md(path: Path, rows: list[dict]) -> None:
    by_day: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_day[str(r["ts"])[:10]].append(r)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Operator ledger - {len(rows)} messages\n\n"
                "Generated on demand from LEDGER.jsonl by `content/video_engine/scripts/extract_operator_ledger.py "
                "--md`; do not edit or commit under docs/.\n\n")
        for day in sorted(by_day):
            f.write(f"## {day} ({len(by_day[day])})\n\n")
            for r in by_day[day]:
                f.write(md_entry(r))


def anchor_exists(anchor: str, repo_root: Path) -> bool:
    path = (anchor or "").strip().split(":", 1)[0].strip()
    return bool(path) and not Path(path).is_absolute() and (repo_root / path).exists()


def superseded_anchor_ok(anchor: str, ledger_ids: set[str], repo_root: Path) -> bool:
    """A superseded correction names what overturned it: a later ledger row id, a ruling id (E73, D1), or a doc
    section that retired it (`path:heading`, the path must exist - P54 T2 met doc 37 section 21)."""
    a = (anchor or "").strip()
    return (bool(RULING_ID.match(a)) or (bool(ROW_ID.match(a)) and a in ledger_ids)
            or (":" in a and anchor_exists(a, repo_root)) or (a.endswith(".md") and anchor_exists(a, repo_root)))


def verdict_failure(t: dict, repo_root: Path, ledger_ids: set[str]) -> str:
    verdict, anchor = t.get("verdict"), t.get("anchor", "")
    if verdict not in VERDICTS:
        return f"bad verdict {verdict!r}"
    if verdict == "recorded" and not anchor_exists(anchor, repo_root):
        return f"recorded anchor {anchor!r} is not an existing repo path"
    if verdict == "superseded" and not superseded_anchor_ok(anchor, ledger_ids, repo_root):
        return f"superseded anchor {anchor!r} is not a ledger row id, a ruling id ([A-E]<n>) or an existing path"
    return ""


def triage_failures(ledger: list[dict], triage: list[dict], repo_root: Path) -> tuple[list[str], int]:
    by_id: dict[str, list[dict]] = defaultdict(list)
    for t in triage:
        by_id[str(t.get("id"))].append(t)
    ledger_ids = {r["id"] for r in ledger}
    needed = [r for r in ledger if not r["pasted"] and any(c in r["cues"] for c in TRIAGE_CUES)]
    fails: list[str] = []
    for r in needed:
        rows = by_id.get(r["id"], [])
        why = (f"{len(rows)} triage rows (need exactly 1)" if len(rows) != 1
               else verdict_failure(rows[0], repo_root, ledger_ids))
        if why:
            fails.append(f"{r['id']} {r['ts']}: {why}")
    return fails, len(needed)


def run_triage_check(out: Path, repo_root: Path) -> int:
    triage_path = out / "TRIAGE.jsonl"
    if not triage_path.exists():
        print(f"no triage yet: {triage_path} is missing")
        return 1
    fails, needed = triage_failures(read_jsonl(out / "LEDGER.jsonl"), read_jsonl(triage_path), repo_root)
    for line in fails:
        print("FAIL", line)
    if fails:
        print(f"triage-check: {len(fails)} failure(s) over {needed} correction/rule row(s)")
        return 1
    print(f"triage-check: clean - {needed} correction/rule row(s) each carry one valid verdict")
    return 0


def print_census(rows: list[dict], shapes: Counter, n_files: int, dropped: int, total: int) -> None:
    words = sum(len(r["text"].split()) for r in rows)
    via = Counter(r["via"] for r in rows)
    print(f"files {n_files} | operator messages {len(rows)} | {words} words | via {dict(via)} | "
          f"pasted {sum(1 for r in rows if r['pasted'])}")
    print(f"skipped shapes: {dict(shapes)} | near-duplicates dropped {dropped}")
    print("cues:", dict(Counter(c for r in rows for c in r["cues"])))
    print(f"appended {len(rows)} | ledger rows {total}")


def parse_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--projects", default=DEFAULT_PROJECTS, help="glob of transcript .jsonl files (recursive **)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--md", type=Path, default=None, help="also write the day-grouped markdown to this path")
    ap.add_argument("--repo-root", type=Path, default=ROOT, help="root that recorded triage anchors resolve against")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--full", action="store_true", help="rebuild the ledger from scratch")
    mode.add_argument("--check", action="store_true", help="write nothing; exit 1 when newer messages exist")
    mode.add_argument("--triage-check", action="store_true", help="validate TRIAGE.jsonl against the ledger")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    a = parse_args(argv)
    if a.triage_check:
        return run_triage_check(a.out, a.repo_root)
    ledger_path = a.out / "LEDGER.jsonl"
    existing = [] if a.full else read_jsonl(ledger_path)
    max_ts = max((str(r["ts"]) for r in existing), default="")
    scanned, shapes, n_files = collect(a.projects)
    new_rows, dropped = drop_near_duplicates([r for r in scanned if str(r["ts"]) > max_ts], seed=existing)
    if a.check:
        print(f"{len(new_rows)} newer operator message(s) not in the ledger (ledger last ts {max_ts or 'none'})")
        return 1 if new_rows else 0
    a.out.mkdir(parents=True, exist_ok=True)
    rows = sorted(existing + new_rows, key=lambda r: str(r["ts"]))
    write_jsonl(ledger_path, rows)
    print_census(new_rows, shapes, n_files, dropped, len(rows))
    print("wrote", ledger_path)
    if a.md is not None:
        render_md(a.md, rows)
        print("wrote", a.md)
    return 0


if __name__ == "__main__":
    sys.exit(main())

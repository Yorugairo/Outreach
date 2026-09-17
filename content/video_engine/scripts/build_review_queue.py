"""THE REVIEW QUEUE - one page of what the operator can judge now, built from review-queue.v1.json only.

The data (`docs/content-video-engine/review-queue.v1.json`, tracked) holds one record per item. This builder writes:
  (a) `docs/content-video-engine/REVIEW-QUEUE.md` - the readable record (tracked): Watch, Look, Rule, Approve, then
      "Owed by the agent before it comes back to you", then "Ruled since the last pass";
  (b) `content/video_engine/review/queue/index.html` - the interactive page (gitignored), with every frame it shows
      COPIED into `frames/`, every before / after crop written into `crops/`, and every clip shown from `clips/`.
E99 s14: an item reaches the operator only with a proof framed for a viewer - a clip that plays in the page, a player
link that answers, or a crop on what changes. An open watch or look item with no proof is refused by name; an item
the agent still owes a proof or a rebuild is kind `owed`, listed collapsed at the end with no answer controls. Clips are
rendered by `review_queue_proofs.py --clips` (slow); crops are computed here (cheap, deterministic).
The page saves answers only through `serve_review_queue.py` (POST /answer, appended to review-answers.jsonl). Applying
an answer - a ruling, its backlog row, `status: ruled` - stays the parent's; neither the page nor the server rules.

E99 s68 (P67 T5): an OPEN `watch` card whose proof shows the WHOLE cut - a player link, or a clip at least
`WHOLE_CUT_S` long - owes a director-critic report (`<build>/CRITIC.md`, `docs/content-video-engine/CRITIC-REPORT.md`):
a whole cut reaches the operator only after a DIFFERENT reader has read it. The rule lands in two steps - while
`CRITIC_REQUIRED` is False it WARNs by name (both `--write` and `--check` still exit 0); P67 T7 flips it to True in the
commit that gives the live card its `critic` path, and then `validate` refuses by name. `critic` is not a REQUIRED
field; that the named report EXISTS and lives under the proof's build is the writer's check, not `validate`'s.

A `batch` card (P65 T4, the recipe lab) is the one card that asks about MORE THAN ONE thing: it carries `candidates`,
each with its own clip proof, asks the card's single plain question once, and gives every candidate an approve / deny
+ reason control of its own. Each of those controls POSTs through the SAME /answer door as
`{item: "<card-id>#<candidate-id>", choice: "approve"|"deny", note: "<reason>: <free text>"}` - the answers file
already carries repeated `item` keys, so nothing downstream changes shape. The nine reason categories are NOT written
here: they are read from `content/video_engine/configs/lab_judgement.schema.json` (P65 T1), the one place they live.

    python content/video_engine/scripts/build_review_queue.py --write | --check | --answers
        [--data PATH] [--md PATH] [--out DIR] [--answers-file PATH] [--root DIR]

Deterministic: the same data, frames and clips give byte-identical outputs (a --write probes each player link and a link
that does not answer is shown as not answering, never as a link). `--check` compares only the TRACKED markdown and exits 1
naming it when stale.
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import quote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import review_queue_proofs as RQP  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA_REL = "docs/content-video-engine/review-queue.v1.json"
MD_REL = "docs/content-video-engine/REVIEW-QUEUE.md"
OUT_REL = "content/video_engine/review/queue"
ANSWERS_REL = "docs/content-video-engine/review-answers.jsonl"
FRAMES_SUBDIR = "frames"
CROPS_SUBDIR = "crops"
CLIPS_SUBDIR = "clips"
NO_PROOF_MARKER = "no proof yet"
OTHER = "other"
ANSWERABLE_KINDS = ("watch", "look", "rule", "approve", "batch")
KINDS = (*ANSWERABLE_KINDS, "owed")
PROOF_KINDS = ("watch", "look")        # E99 s14: these reach the operator only with a proof
PROOF_TYPES = ("clip", "player", "crop")
KIND_TITLES = {"watch": "Watch", "look": "Look", "rule": "Rule", "approve": "Approve / push",
               "batch": "Batches - candidate by candidate", "owed": "Owed by the agent before it comes back to you"}
BATCH_SEP = "#"                        # one candidate's answer is item <card-id>#<candidate-id> (P65 T4)
BATCH_CHOICES = ("approve", "deny")    # a candidate takes a BIT; the reason carries the why (P65 T1)
CANDIDATE_REQUIRED = ("id", "label", "one_line", "proof")
REASON_SCHEMA_REL = "content/video_engine/configs/lab_judgement.schema.json"
STATUSES = ("open", "ruled")
REQUIRED = ("id", "ids", "kind", "title", "judge", "where", "options", "recommendation", "blocks", "sources", "status",
            "ruling")
PROOF_FIELDS = {"clip": ("label", "t0", "t1", "route"), "player": ("label", "url", "build", "confirmed"),
                "crop": ("label", "before", "after")}
WHOLE_CUT_S = 30.0          # P67 T5: a clip this long or longer shows the whole cut, not a beat (one-shot #3: 77.6 s)
CRITIC_REQUIRED = False     # P67 T5 ships the critic rule as a WARN; P67 T7 flips it to True with the live card's path
CRITIC_REPORT_NAME = "CRITIC.md"       # what the director-critic writes into the build it read (CRITIC-REPORT.md)
WARNINGS: list[str] = []               # what validate() warned about on the last load; the cli prints it by name
WHERE_TARGETS = ("path", "url", "missing", "command")
SERVE_CMD = "python content/video_engine/scripts/serve_player.py {build} --port {port}"
RULED_HEADING = "Ruled since the last pass"
OWED_HEADING = KIND_TITLES["owed"]


class QueueError(ValueError):
    """A record the schema refuses; the message names the record and the field."""


def load_reasons(root: Path = ROOT) -> tuple[str, ...]:
    """The fixed reason categories a batch's candidate control offers, read from `lab_judgement.schema.json`: P65 T1
    put them in the schema ONCE and every tool reads them from there rather than restating the list."""
    path = root / REASON_SCHEMA_REL
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
        return tuple(schema["$defs"]["judgement"]["properties"]["reason"]["enum"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise QueueError(f"the reason list is {REASON_SCHEMA_REL} $defs.judgement.properties.reason.enum "
                         f"and it did not load: {exc}") from exc


REASONS = load_reasons()


def note_reason(note: object) -> str:
    """The reason a candidate's note opens with (the text before the first ':'), or '' when it opens with none."""
    head = note.split(":", 1)[0].strip() if isinstance(note, str) else ""
    return head if head in REASONS else ""


# ---------------------------------------------------------------- data

def validate_proof(name: str, proof: object) -> None:
    if not isinstance(proof, dict) or proof.get("type") not in PROOF_TYPES:
        raise QueueError(f"{name}: a proof is an object with a type in {', '.join(PROOF_TYPES)}")
    missing = [k for k in PROOF_FIELDS[proof["type"]] if k not in proof]
    if missing:
        raise QueueError(f"{name}: a {proof['type']} proof is missing {', '.join(missing)}")
    if proof["type"] == "clip" and not (proof.get("surface") or proof.get("build") or proof.get("mp4")):
        raise QueueError(f"{name}: a clip proof names its surface, its build, or an mp4 already on disk")


def whole_cut_proof(rec: dict) -> dict | None:
    """The proof that shows the WHOLE cut rather than one beat: a player link (the operator watches it end to end) or
    a clip at least `WHOLE_CUT_S` long. The first such proof, or None when every proof is a beat."""
    for proof in rec.get("proofs") or []:
        if not isinstance(proof, dict):
            continue
        if proof.get("type") == "player":
            return proof
        if proof.get("type") == "clip":
            try:
                if float(proof["t1"]) - float(proof["t0"]) >= WHOLE_CUT_S:
                    return proof
            except (KeyError, TypeError, ValueError):
                continue
    return None


def critic_owed(name: str, rec: dict) -> None:
    """E99 s68: an OPEN watch card carrying a whole-cut proof owes a director-critic report - a whole cut reaches the
    operator after a DIFFERENT reader has read it (one-shot #3 was CLEAN by its own builder's read and refused in four
    messages). A present `critic` is checked here only as a repo-relative name; that the file EXISTS and lives under
    the proof's build is the writer's check (`check_critic_files`), so the fixtures keep working."""
    critic = rec.get("critic")
    if critic is not None:
        if not isinstance(critic, str) or not critic.strip() or Path(critic).is_absolute():
            raise QueueError(f"{name}: 'critic' names the director-critic report repo-relative "
                             f"(e.g. <build>/{CRITIC_REPORT_NAME}), not {critic!r}")
        return
    if rec["status"] != "open" or rec["kind"] != "watch":
        return
    proof = whole_cut_proof(rec)
    if proof is None:
        return
    build = str(proof.get("build") or "<build>").rstrip("/")
    message = (f"{name}: a whole-cut watch owes a critic report ({build}/{CRITIC_REPORT_NAME}) - E99 s68; "
               f"run the director-critic pass or make the proof a clip of the beat")
    if CRITIC_REQUIRED:
        raise QueueError(message)
    WARNINGS.append(f"WARN {message}")


def validate_candidate(name: str, cand: object, n: int, seen: set[str]) -> None:
    """One candidate of a batch card: an id the item grammar can carry, a label, its one line, and a CLIP proof - a
    beat a short could carry (E99 s60), never a player link or a crop."""
    if not isinstance(cand, dict):
        raise QueueError(f"{name}: candidate {n} is not an object")
    missing = [k for k in CANDIDATE_REQUIRED if k not in cand]
    if missing:
        raise QueueError(f"{name}: candidate {n} is missing {', '.join(missing)}")
    cid = cand["id"]
    if not isinstance(cid, str) or not cid.strip() or BATCH_SEP in cid:
        raise QueueError(f"{name}: a candidate id is a non-empty string with no {BATCH_SEP!r} in it (an answer's item "
                         f"is <card-id>{BATCH_SEP}<candidate-id>): {cid!r}")
    if cid in seen:
        raise QueueError(f"{name}: duplicate candidate id {cid!r}")
    seen.add(cid)
    validate_proof(f"{name} candidate {cid}", cand["proof"])
    if cand["proof"]["type"] != "clip":
        raise QueueError(f"{name}: candidate {cid} needs a CLIP proof - a beat a short could carry (E99 s60) - "
                         f"not a {cand['proof']['type']} proof")
    if cand.get("reason") is not None and cand["reason"] not in REASONS:
        raise QueueError(f"{name}: candidate {cid} carries a reason off the list: {cand['reason']!r} "
                         f"(one of {', '.join(REASONS)})")


def validate_batch(name: str, rec: dict) -> None:
    """A batch card carries its candidates side by side, and its `proofs` MIRRORS them in order: the page and
    `review_queue_proofs.py --clips` both name a clip by its index, so the two lists may never drift apart."""
    cands = rec.get("candidates")
    if not isinstance(cands, list) or not cands:
        raise QueueError(f"{name}: a batch card has no candidates - 'candidates' is a non-empty list "
                         "(one record per beat shape, its survivors side by side)")
    seen: set[str] = set()
    for n, cand in enumerate(cands):
        validate_candidate(name, cand, n, seen)
    if list(rec.get("proofs") or []) != [c["proof"] for c in cands]:
        raise QueueError(f"{name}: a batch's 'proofs' mirrors its candidates' clips in order (the page and "
                         "review_queue_proofs.py --clips name a clip by its index) - write it with lab_batch.py")


def validate_record(rec: object, n: int, seen: set[str]) -> None:
    if not isinstance(rec, dict):
        raise QueueError(f"record {n} is not an object")
    name = rec.get("id") or f"record {n}"
    missing = [k for k in REQUIRED if k not in rec]
    if missing:
        raise QueueError(f"{name}: missing field(s) {', '.join(missing)}")
    if rec["kind"] not in KINDS:
        raise QueueError(f"{name}: unknown kind {rec['kind']!r} (one of {', '.join(KINDS)})")
    if rec["status"] not in STATUSES:
        raise QueueError(f"{name}: unknown status {rec['status']!r} (one of {', '.join(STATUSES)})")
    if rec["id"] in seen:
        raise QueueError(f"duplicate id {rec['id']!r}")
    if rec["status"] == "ruled" and not rec["ruling"]:
        raise QueueError(f"{name}: status ruled needs a ruling")
    if OTHER in rec["options"]:
        raise QueueError(f"{name}: {OTHER!r} is always offered; do not list it in options")
    if rec["kind"] == "owed" and not (isinstance(rec.get("owed"), str) and rec["owed"].strip()):
        raise QueueError(f"{name}: an owed item says what it owes (its E99 section or its missing proof) in 'owed'")
    for proof in rec.get("proofs") or []:
        validate_proof(name, proof)
    if rec["kind"] == "batch":
        validate_batch(name, rec)
    elif rec.get("candidates"):
        raise QueueError(f"{name}: only a batch card carries candidates (this one is kind {rec['kind']!r})")
    if rec["status"] == "open" and rec["kind"] in PROOF_KINDS and not rec.get("proofs"):
        raise QueueError(f"{name}: an open {rec['kind']} item has no proof entry (E99 s14) - "
                         "give it a clip, a player or a crop, or move it to kind owed")
    critic_owed(name, rec)
    for w in rec["where"]:
        if not isinstance(w, dict) or "label" not in w or not any(t in w for t in WHERE_TARGETS):
            raise QueueError(f"{name}: a where entry needs a label and one of {', '.join(WHERE_TARGETS)}")


def validate(items: list) -> list[dict]:
    """Refuse by name: a missing field, an unknown kind or status, a duplicate id, a where entry with no target, an
    open watch / look item with no proof, an owed item that does not say what it owes, a batch with no candidates, a
    candidate with no clip proof, a duplicate candidate id, a candidate reason off the fixed list, and (once
    `CRITIC_REQUIRED` is True) an open whole-cut watch with no critic report. WARNINGS carries what only warned."""
    if not isinstance(items, list):
        raise QueueError("the queue's items must be a list of records")
    WARNINGS.clear()
    seen: set[str] = set()
    for n, rec in enumerate(items):
        validate_record(rec, n, seen)
        seen.add(rec["id"])
    return items


def load_data(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "items" not in data:
        raise QueueError(f"{path.name}: the data is one object with an 'items' list")
    validate(data["items"])
    return data


def open_items(data: dict) -> list[dict]:
    return [i for i in data["items"] if i["status"] == "open"]


def answerable_items(data: dict) -> list[dict]:
    """The open items the operator can answer now: every open item that is not owed by the agent."""
    return [i for i in open_items(data) if i["kind"] != "owed"]


def owed_items(data: dict) -> list[dict]:
    return [i for i in open_items(data) if i["kind"] == "owed"]


def ruled_items(data: dict) -> list[dict]:
    return [i for i in data["items"] if i["status"] == "ruled"]


def latest_answers(path: Path) -> dict[str, dict]:
    """The latest line per item in the append-only answers file (a missing file is no answers)."""
    latest: dict[str, dict] = {}
    if not path.is_file():
        return latest
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            latest[rec["item"]] = rec
    return latest


def serve_hint(entry: dict) -> str:
    port = urlparse(entry["url"]).port or 80
    return SERVE_CMD.format(build=entry.get("build") or "<build>", port=port)


def probe_players(data: dict) -> dict[str, bool]:
    """Whether each player proof's URL answers right now (a link that does not answer is never shown as a link)."""
    return {url: RQP.url_answers(url) for url in RQP.player_urls(data)}


# ---------------------------------------------------------------- markdown

def cell(text: object) -> str:
    return str("" if text is None else text).replace("|", "\\|").replace("\n", " ")


def md_where(entry: dict) -> str:
    label = entry["label"]
    if entry.get("missing"):
        return f"**{NO_PROOF_MARKER}**: {label}"
    if "command" in entry:
        return f"{label}: `{entry['command']}`"
    if "url" in entry:
        return f"~~{entry['url']}~~ **stale** ({label}; serve with `{serve_hint(entry)}`)"
    note = f" - {entry['note']}" if entry.get("note") else ""
    return f"{label}: `{entry['path']}`{note}"


def md_proof(item_id: str, n: int, p: dict) -> str:
    if p["type"] == "clip":
        src = (f"golden `{p['surface']}`" if p.get("surface") else f"build `{p['build']}`" if p.get("build")
               else f"mp4 `{p['mp4']}`")
        return f"clip `{RQP.clip_name(item_id, n)}` - {p['label']} ({src}, {p['t0']}-{p['t1']} s)"
    if p["type"] == "player":
        return f"player {p['url']} - {p['label']} (build `{p['build']}`; {p['confirmed']})"
    return f"crop - {p['label']}: `{p['before']}` vs `{p['after']}`"


def md_candidate(item_id: str, n: int, cand: dict) -> str:
    tags = " ".join(f"**{t}**" for t in ("exploration", "calibration") if cand.get(t))
    prior = f" (judged before: {cand['reason']})" if cand.get("reason") else ""
    return (f"`{cand['id']}` {tags} {cand['label']} - {cand['one_line']}{prior} - "
            f"{md_proof(item_id, n, cand['proof'])}")


def md_row(rec: dict) -> str:
    if rec["kind"] == "batch":
        proofs = "<br>".join(md_candidate(rec["id"], n, c) for n, c in enumerate(rec["candidates"]))
    else:
        proofs = "<br>".join(md_proof(rec["id"], n, p) for n, p in enumerate(rec.get("proofs") or [])) or "the documents below"
    where = "<br>".join(md_where(w) for w in rec["where"])
    options = " / ".join(rec["options"]) or "free answer"
    if rec["kind"] == "batch":
        options = f"per candidate: {' / '.join(BATCH_CHOICES)} + a reason; on the card: {options}"
    rec_text = rec["recommendation"] if rec["recommendation"] is not None else "none recorded"
    answer = f" Answer so far ({rec['answer']['ruling']}): \"{rec['answer']['quote']}\"" if rec.get("answer") else ""
    return "| " + " | ".join(cell(c) for c in (
        f"`{rec['id']}`", f"**{rec['title']}** ({', '.join(rec['ids'])})", rec["judge"] + answer, proofs, where,
        options, rec_text, rec["blocks"], "<br>".join(rec["sources"]))) + " |"


def md_header(data: dict) -> list[str]:
    counts = ", ".join(f"{sum(i['kind'] == k for i in answerable_items(data))} {k}" for k in ANSWERABLE_KINDS)
    return [
        "# REVIEW QUEUE - what the operator can judge now",
        "",
        "Generated from [`review-queue.v1.json`](review-queue.v1.json) by "
        "`content/video_engine/scripts/build_review_queue.py --write`; do not edit this file by hand. It supersedes "
        "[`OPEN-GATES-AND-QUESTIONS-2026-09-12.md`](OPEN-GATES-AND-QUESTIONS-2026-09-12.md).",
        "",
        f"- **As of** {data.get('as_of')} at `{data.get('head')}`; {len(answerable_items(data))} answerable ({counts}), "
        f"{len(owed_items(data))} owed by the agent, {len(ruled_items(data))} ruled since the last pass.",
        "- **E99 s14:** an item reaches the operator only with a proof framed for a viewer - a clip that plays in the "
        "page, a player link that answers, or a crop on what changes. An item without one is the agent's work, listed "
        "under \"Owed\", never asked.",
        "- **`approved` is the operator's word.** The agent's recommendation is labelled as the agent's; it is never a ruling.",
        "- **Answer in the page:** `python content/video_engine/scripts/serve_review_queue.py` (http://127.0.0.1:8766/) "
        "appends each saved answer to `review-answers.jsonl`. **Agents read the answers** with "
        "`build_review_queue.py --answers`; the parent applies them. Clips: `review_queue_proofs.py --clips`.",
        "",
    ]


def render_markdown(data: dict) -> str:
    items = answerable_items(data)
    lines = md_header(data)
    header = ["| id | item | what to judge | proof | documents | options | agent's recommendation | blocks | sources |",
              "|---|---|---|---|---|---|---|---|---|"]
    for kind in ANSWERABLE_KINDS:
        rows = [md_row(r) for r in items if r["kind"] == kind]
        lines += [f"## {KIND_TITLES[kind]} ({len(rows)})", ""]
        lines += (header + rows) if rows else ["Nothing open."]
        lines.append("")
    lines += [f"## {OWED_HEADING} ({len(owed_items(data))})", "", "| id | item | what the agent owes | blocks |",
              "|---|---|---|---|"]
    for r in owed_items(data):
        lines.append("| " + " | ".join(cell(c) for c in (
            f"`{r['id']}`", f"**{r['title']}** ({', '.join(r['ids'])})", r["owed"], r["blocks"])) + " |")
    lines += ["", f"## {RULED_HEADING}", "", "| id | item | ruling / evidence | sources |", "|---|---|---|---|"]
    for r in ruled_items(data):
        lines.append("| " + " | ".join(cell(c) for c in (
            f"`{r['id']}`", f"**{r['title']}** ({', '.join(r['ids'])})", r["ruling"], "<br>".join(r["sources"]))) + " |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- page

def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def is_frame(entry: dict) -> bool:
    return str(entry.get("path", "")).lower().endswith(".png")


def frame_name(rel: str) -> str:
    return rel.replace("/", "__")


def frames_to_copy(data: dict, root: Path) -> list[str]:
    paths = {w["path"] for i in answerable_items(data) for w in i["where"] if is_frame(w)}   # only cards show frames
    paths |= {p[k] for i in answerable_items(data) for p in i.get("proofs") or [] if p["type"] == "crop"
              for k in ("before", "after")}
    return sorted(p for p in paths if (root / p).is_file())


def clips_named(data: dict) -> list[str]:
    return sorted(RQP.clip_name(i["id"], n) for i in answerable_items(data)
                  for n, p in enumerate(i.get("proofs") or []) if p["type"] == "clip")


def page_note(entry: dict) -> str:
    return f'<br><span class="small">{esc(entry["note"])}</span>' if entry.get("note") else ""


def page_frame(entry: dict, label: str, root: Path) -> str:
    if not (root / entry["path"]).is_file():
        return (f'<li class="none"><span class="noproof">{NO_PROOF_MARKER}</span> {label} '
                f'(not found: <code>{esc(entry["path"])}</code>){page_note(entry)}</li>')
    src = f"{FRAMES_SUBDIR}/{quote(frame_name(entry['path']))}"
    return (f'<li class="frame"><a href="{src}" target="_blank" rel="noopener"><img loading="lazy" src="{src}" '
            f'alt="{label}"></a><span class="small">{label}<br><code>{esc(entry["path"])}</code></span>{page_note(entry)}</li>')


def page_where(entry: dict, root: Path) -> str:
    label = esc(entry["label"])
    if entry.get("missing"):
        return f'<li class="none"><span class="noproof">{NO_PROOF_MARKER}</span> {label}</li>'
    if "command" in entry:
        return f'<li>{label}: <code>{esc(entry["command"])}</code></li>'
    if "url" in entry:
        return (f'<li class="stale"><span class="flag">not served</span> {label}: <code>{esc(serve_hint(entry))}</code>'
                f'{page_note(entry)}</li>')
    if is_frame(entry):
        return page_frame(entry, label, root)
    return f'<li>{label}: <code>{esc(entry["path"])}</code>{page_note(entry)}</li>'


def proof_clip(rec: dict, n: int, p: dict, root: Path) -> str:
    name = RQP.clip_name(rec["id"], n)
    source = (f"golden {p['surface']}" if p.get("surface") else f"build {p['build']}" if p.get("build")
              else f"mp4 {p['mp4']}")
    caption = (f'<p class="plabel"><b>{esc(p["label"])}</b><br><span class="small">{esc(source)} - '
               f'{p["t0"]:g} to {p["t1"]:g} s - silent, loops</span></p>')
    if not (root / OUT_REL / CLIPS_SUBDIR / name).is_file():
        return (f'<div class="proof clip missing">{caption}<p class="noproof">clip not rendered yet - '
                f'<code>python content/video_engine/scripts/review_queue_proofs.py --clips --only {esc(rec["id"])}</code></p></div>')
    return (f'<div class="proof clip">{caption}<video controls muted loop playsinline preload="metadata" '
            f'src="{CLIPS_SUBDIR}/{quote(name)}"></video></div>')


def proof_player(p: dict, live: dict | None) -> str:
    caption = f'<b>{esc(p["label"])}</b><br><span class="small">build <code>{esc(p["build"])}</code></span>'
    if live is not None and not live.get(p["url"], False):
        return (f'<div class="proof player dead"><p class="plabel">{caption}</p><p class="noproof">not answering when this '
                f'page was built - serve it with <code>{esc(serve_hint(p))}</code></p></div>')
    return (f'<div class="proof player"><p class="plabel">{caption}</p><p><a class="open" href="{esc(p["url"])}" '
            f'target="_blank" rel="noopener">Open the player: {esc(p["url"])}</a></p>'
            f'<p class="small">{esc(p["confirmed"])}</p></div>')


def proof_crop(rec: dict, n: int, p: dict, root: Path) -> str:
    try:
        box = RQP.crop_box(p, root)
    except RQP.NoVisibleChange as exc:
        raise QueueError(f"{rec['id']}: its crop '{p['label']}' is not a proof ({exc}) - move the item to owed") from exc
    before, after = RQP.crop_names(rec["id"], n)
    full = [f"{FRAMES_SUBDIR}/{quote(frame_name(p[k]))}" for k in ("before", "after")]
    sides = "".join(
        f'<figure><img src="{CROPS_SUBDIR}/{quote(name)}" alt="{esc(tag)}"><figcaption><b>{esc(tag)}</b> - '
        f'<a href="{src}" target="_blank" rel="noopener">full frame</a></figcaption></figure>'
        for name, tag, src in ((before, p.get("before_label", "before"), full[0]),
                               (after, p.get("after_label", "after"), full[1])))
    return (f'<div class="proof crop"><p class="plabel"><b>{esc(p["label"])}</b><br><span class="small">cropped to what '
            f'changes: x {box[0]}-{box[2]}, y {box[1]}-{box[3]}</span></p><div class="pair">{sides}</div></div>')


def page_proofs(rec: dict, root: Path, live: dict | None) -> str:
    parts = []
    for n, p in enumerate(rec.get("proofs") or []):
        if p["type"] == "clip":
            parts.append(proof_clip(rec, n, p, root))
        elif p["type"] == "player":
            parts.append(proof_player(p, live))
        else:
            parts.append(proof_crop(rec, n, p, root))
    return f'<h4>The proof</h4><div class="proofs">{"".join(parts)}</div>' if parts else ""


def candidate_tags(cand: dict) -> str:
    """Why this candidate is in front of you when the table did not ask for it - the card says so (Gao et al. 2022)."""
    return "".join(f'<span class="tag {t}">{t}</span>' for t in ("exploration", "calibration") if cand.get(t))


def page_candidate(rec: dict, n: int, c: int, cand: dict, root: Path) -> str:
    """One candidate: its clip, its one line, and its own approve / deny + reason control. The control POSTs
    {item: "<card>#<candidate>", choice, note: "<reason>: <free text>"} through the SAME /answer door."""
    item = f'{rec["id"]}{BATCH_SEP}{cand["id"]}'
    radios = "".join(f'<label><input type="radio" name="b{n}-{c}" value="{esc(ch)}"> {esc(ch)}</label>'
                     for ch in BATCH_CHOICES)
    reasons = "".join(f'<option value="{esc(r)}">{esc(r)}</option>' for r in REASONS)
    prior = f'<p class="small">judged before: <b>{esc(cand["reason"])}</b></p>' if cand.get("reason") else ""
    return (
        f'<div class="cand" data-cand="{esc(cand["id"])}">'
        f'<p class="plabel"><b>{esc(cand["label"])}</b> {candidate_tags(cand)}<br>'
        f'<span class="small">{esc(cand["one_line"])}</span><br><code>{esc(cand["id"])}</code></p>'
        f'{proof_clip(rec, c, cand["proof"], root)}{prior}'
        f'<form class="cand" data-item="{esc(item)}"><fieldset><legend>Your bit on this one</legend>{radios}</fieldset>'
        f'<label class="notelabel" for="r{n}-{c}">Why</label>'
        f'<select class="reason" id="r{n}-{c}"><option value="" disabled selected>choose a reason</option>{reasons}</select>'
        f'<textarea rows="2" placeholder="in your words (optional)"></textarea>'
        f'<div class="row"><button type="submit">Save</button><span class="saved" role="status"></span></div>'
        f'</form></div>')


def page_candidates(rec: dict, n: int, root: Path) -> str:
    cands = "".join(page_candidate(rec, n, c, cand, root) for c, cand in enumerate(rec["candidates"]))
    return (f'<h4>The candidates ({len(rec["candidates"])}) - a bit and a reason on each</h4>'
            f'<div class="cands">{cands}</div>')


def page_controls(rec: dict, n: int) -> str:
    choices = [*rec["options"], OTHER]
    radios = "".join(
        f'<label><input type="radio" name="c{n}" value="{esc(c)}"> {esc(c)}</label>' for c in choices)
    legend = "Your answer on the card itself" if rec["kind"] == "batch" else "Your answer"
    return (f'<form class="answer" data-item="{esc(rec["id"])}"><fieldset><legend>{legend}</legend>{radios}</fieldset>'
            f'<label class="notelabel" for="note{n}">Note</label><textarea id="note{n}" rows="3"></textarea>'
            f'<div class="row"><button type="submit">Save</button><span class="saved" role="status"></span></div></form>')


def page_card(rec: dict, n: int, root: Path, live: dict | None) -> str:
    recommendation = esc(rec["recommendation"]) if rec["recommendation"] is not None else "<i>none recorded</i>"
    where = "".join(page_where(w, root) for w in rec["where"])
    sources = "".join(f"<li><code>{esc(s)}</code></li>" for s in rec["sources"])
    answer = (f'<p class="sofar"><b>Your answer so far ({esc(rec["answer"]["ruling"])}):</b> '
              f'<q>{esc(rec["answer"]["quote"])}</q></p>' if rec.get("answer") else "")
    return (
        f'<article class="card" data-id="{esc(rec["id"])}" data-kind="{esc(rec["kind"])}"'
        + (f' data-applied-at="{esc(rec["answer"]["at"])}"' if rec.get("answer") else "") + '>'
        f'<h3>{esc(rec["title"])}</h3><p class="ids">{esc(" / ".join(rec["ids"]))}</p>'
        f'{answer}<p class="q">{esc(rec["judge"])}</p>'
        + (page_candidates(rec, n, root) if rec["kind"] == "batch" else page_proofs(rec, root, live)) +
        f'<p class="agent"><b>The agent\'s recommendation:</b> {recommendation}</p>'
        + (f'<h4>Documents</h4><ul class="where">{where}</ul>' if where else "") +
        f'<p><b>Blocks:</b> {esc(rec["blocks"])}</p>'
        f'<details><summary>Sources</summary><ul class="src">{sources}</ul></details>'
        f'{page_controls(rec, n)}</article>')


CSS = """
*{box-sizing:border-box}body{background:#F4E6C7;color:#25313C;font-family:system-ui,"Segoe UI",sans-serif;margin:0;
padding:20px 28px;line-height:1.45}h1{margin:0 0 4px}h2{border-top:3px solid #25313C;padding-top:14px;margin-top:32px}
h3{margin:0 0 2px}h4{margin:10px 0 4px}.progress{font-size:1.1em;font-weight:600}
.bar{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;background:#fbf3e1;border:1px solid #25313C;
padding:8px 12px;position:sticky;top:0;z-index:5}select,textarea,button{font:inherit;color:#25313C}
select,textarea{border:1px solid #25313C;background:#fff;padding:4px 6px}textarea{width:100%}
button{background:#25313C;color:#F4E6C7;border:0;padding:6px 16px;border-radius:4px;cursor:pointer}
:focus-visible{outline:3px solid #B8402A;outline-offset:2px}
.card{background:#fbf3e1;border:1px solid #25313C;border-radius:4px;padding:12px 14px;margin:12px 0}
.card.answered{border-left:8px solid #2f6b3a}.ids{margin:0;font-size:.85em;opacity:.8}.q{font-size:1.08em;font-weight:600}
.sofar{background:#fff;border-left:6px solid #2f6b3a;padding:6px 10px}
.agent{background:#25313C;color:#F4E6C7;padding:8px 12px;border-radius:4px}
.proofs,.cands{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;align-items:start}
.cand{background:#fff;border:2px solid #25313C;padding:8px}.cand .proof{border:1px solid #c9b58f;padding:0}
.cand form{margin-top:6px}.cand select.reason{width:100%;margin-bottom:4px}
.tag{background:#25313C;color:#F4E6C7;padding:0 6px;border-radius:8px;font-size:.78em}
.tag.exploration{background:#B8402A}.tag.calibration{background:#2f6b3a}
form.answered fieldset{border-left:6px solid #2f6b3a}
.proof{background:#fff;border:2px solid #25313C;padding:8px}.proof video{display:block;width:100%;max-height:70vh;
background:#000}.plabel{margin:0 0 6px}.pair{display:flex;gap:8px;flex-wrap:wrap}.pair figure{margin:0;flex:1 1 140px}
.pair img{display:block;width:100%;height:auto;border:1px solid #25313C}.proof.crop{grid-column:1/-1}
a.open{font-weight:700;font-size:1.05em}
ul.where{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px}
ul.where li{background:#fff;border:1px solid #c9b58f;padding:6px;word-break:break-word}
ul.where img{display:block;width:100%;height:auto;border:1px solid #25313C}
.small{font-size:.82em}code{font-family:ui-monospace,Consolas,monospace;font-size:.9em}
li.stale{border:2px dashed #B8402A!important}.flag{background:#B8402A;color:#fff;padding:0 6px;border-radius:8px;font-size:.8em}
li.none{border:2px dashed #c33!important;background:#fff6f6!important}.noproof{color:#a11;font-weight:700}
fieldset{border:1px solid #25313C;margin:10px 0 6px}fieldset label{display:inline-block;margin:2px 14px 2px 0}
.row{display:flex;gap:12px;align-items:center;margin-top:6px}.saved{font-size:.9em}.err{color:#a11;font-weight:600}
.banner{background:#B8402A;color:#fff;padding:8px 12px;margin:8px 0}.hidden{display:none}
ul.owed{padding-left:18px}ul.owed li{margin:6px 0}
table.ruled{border-collapse:collapse;width:100%;background:#fbf3e1}table.ruled td,table.ruled th{border:1px solid #25313C;
padding:6px 8px;vertical-align:top;text-align:left}
@media (max-width:640px){body{padding:10px}.bar{position:static}ul.where,.proofs{grid-template-columns:1fr}
table.ruled,table.ruled tbody,table.ruled tr,table.ruled td{display:block}}
"""

JS = """
(function(){
var answers={},cards=[].slice.call(document.querySelectorAll('article.card'));
function forms(card){return [].slice.call(card.querySelectorAll('form[data-item]'));}
function showForm(form){var a=answers[form.dataset.item],s=form.querySelector('.saved');
form.classList.toggle('answered',!!a);
if(!a){s.textContent='';return;}s.className='saved';s.textContent='saved '+a.at+' - '+a.choice;
form.querySelectorAll('input[type=radio]').forEach(function(r){r.checked=(r.value===a.choice);});
var sel=form.querySelector('select.reason'),ta=form.querySelector('textarea'),note=a.note||'';
if(sel){var i=note.indexOf(': ');if(i>0){sel.value=note.slice(0,i);note=note.slice(i+2);}}
if(ta)ta.value=note;}
function show(card){card.classList.toggle('answered',!!answers[card.dataset.id]);forms(card).forEach(showForm);}
function progress(){var n=cards.filter(function(c){return answers[c.dataset.id];}).length;
document.getElementById('progress').textContent=n+' of '+cards.length+' answered';}
function filter(){var k=document.getElementById('fkind').value,st=document.getElementById('fstate').value;
cards.forEach(function(c){var a=!!answers[c.dataset.id];var hit=(k==='all'||c.dataset.kind===k)&&
(st==='all'||(st==='answered')===a);c.classList.toggle('hidden',!hit);});
document.querySelectorAll('section.kind').forEach(function(s){s.classList.toggle('hidden',
!s.querySelector('article.card:not(.hidden)'));});}
function refresh(){cards.forEach(show);progress();filter();}
document.getElementById('fkind').addEventListener('change',filter);
document.getElementById('fstate').addEventListener('change',filter);
cards.forEach(function(card){forms(card).forEach(function(form){form.addEventListener('submit',function(ev){
ev.preventDefault();
var r=form.querySelector('input[type=radio]:checked'),s=form.querySelector('.saved'),
sel=form.querySelector('select.reason'),ta=form.querySelector('textarea');
if(!r){s.className='saved err';s.textContent='pick a choice first';return;}
if(sel&&!sel.value){s.className='saved err';s.textContent='pick a reason first';return;}
var note=ta?ta.value:'';if(sel)note=sel.value+': '+note;
var body=JSON.stringify({item:form.dataset.item,choice:r.value,note:note});
s.className='saved';s.textContent='saving...';
fetch('answer',{method:'POST',headers:{'Content-Type':'application/json'},body:body}).then(function(res){
return res.json().then(function(j){if(!res.ok||!j.ok)throw new Error(j.error||res.status);answers[j.answer.item]=j.answer;
refresh();});}).catch(function(e){s.className='saved err';s.textContent='not saved: '+e.message;});});});});
fetch('answers',{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error(r.status);return r.json();})
.then(function(j){answers={};Object.keys(j).forEach(function(k){var id=k.split('#')[0],c=null;
cards.forEach(function(x){if(x.dataset.id===id)c=x;});
if(c&&!(c.dataset.appliedAt&&j[k].at<=c.dataset.appliedAt))answers[k]=j[k];});refresh();})
.catch(function(){document.getElementById('offline').classList.remove('hidden');progress();});
progress();
})();
"""


def page_sections(data: dict, root: Path, live: dict | None) -> str:
    items, sections, n = answerable_items(data), [], 0
    for kind in ANSWERABLE_KINDS:
        rows = [r for r in items if r["kind"] == kind]
        cards = []
        for r in rows:
            cards.append(page_card(r, n, root, live))
            n += 1
        sections.append(f'<section class="kind" id="kind-{kind}"><h2>{KIND_TITLES[kind]} ({len(rows)})</h2>'
                        f'{"".join(cards)}</section>')
    return "".join(sections)


def page_owed(data: dict) -> str:
    rows = "".join(
        f'<li data-owed-id="{esc(r["id"])}"><b>{esc(r["title"])}</b> <span class="small">({esc(" / ".join(r["ids"]))})'
        f'</span><br>{esc(r["owed"])}</li>' for r in owed_items(data))
    return (f'<section id="owed"><h2>{esc(OWED_HEADING)} ({len(owed_items(data))})</h2>'
            f'<details><summary>Not for you yet: each needs a proof or a rebuild first ({len(owed_items(data))})</summary>'
            f'<ul class="owed">{rows}</ul></details></section>')


def page_ruled(data: dict, root: Path) -> str:
    rows = "".join(
        f'<tr><td><b>{esc(r["title"])}</b><br><span class="small">{esc(" / ".join(r["ids"]))}</span></td>'
        f'<td class="ruling">{esc(r["ruling"])}</td></tr>'
        for r in ruled_items(data))
    return (f'<section id="ruled"><h2>{RULED_HEADING} ({len(ruled_items(data))})</h2>'
            f'<table class="ruled"><thead><tr><th>item</th><th>ruling / evidence</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></section>')


def render_page(data: dict, root: Path, live: dict | None = None) -> str:
    """The page. `live` maps each player URL to whether it answered at build time (None: not probed)."""
    kind_opts = "".join(f'<option value="{k}">{KIND_TITLES[k]}</option>' for k in ANSWERABLE_KINDS)
    total = len(answerable_items(data))
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Review queue - {esc(data.get("as_of"))}</title><style>{CSS}</style></head><body>'
        f'<h1>Review queue</h1><p>What you can judge now, as of {esc(data.get("as_of"))} '
        f'(<code>{esc(data.get("head"))}</code>). Every item below carries its proof: a clip that plays here, a player '
        f'link that answered when this page was built, or a crop on what changes. <b>approved</b> is your word; the '
        f'recommendation on each card is the agent\'s. What the agent still owes you is listed, collapsed, at the end.</p>'
        '<p id="offline" class="banner hidden">Not served: answers cannot be read or saved. Start '
        '<code>python content/video_engine/scripts/serve_review_queue.py</code> and open http://127.0.0.1:8766/</p>'
        f'<div class="bar"><span id="progress" class="progress" data-total="{total}" aria-live="polite">'
        f'0 of {total} answered</span>'
        f'<label>Kind <select id="fkind"><option value="all">all</option>{kind_opts}</select></label>'
        '<label>State <select id="fstate"><option value="all">all</option><option value="open">open</option>'
        '<option value="answered">answered</option></select></label></div>'
        f'{page_sections(data, root, live)}{page_owed(data)}{page_ruled(data, root)}<script>{JS}</script></body></html>\n')


def _sync_dir(target: Path, wanted: dict[str, Path]) -> None:
    """Make `target` hold exactly the wanted files (the builder's own output folder)."""
    target.mkdir(parents=True, exist_ok=True)
    for old in target.iterdir():
        if old.is_file() and old.name not in wanted:
            old.unlink()
    for name, src in wanted.items():
        if src.resolve() != (target / name).resolve():
            shutil.copyfile(src, target / name)


def check_critic_files(data: dict, root: Path) -> None:
    """The DISK half of the critic rule, the writer's alone (P67 T5): a named report exists and lives under the build
    its whole-cut proof names - a card may not ship a path to a report nobody wrote, nor to one written about another
    cut. `validate` never touches the disk, so the fixtures and the schema tests stay path-free."""
    for rec in open_items(data):
        critic = rec.get("critic")
        if not critic:
            continue
        path = root / critic
        if not path.is_file():
            raise QueueError(f"{rec['id']}: the critic report {critic} is not on disk - run the director-critic pass "
                             f"(docs/content-video-engine/CRITIC-REPORT.md) before the card reaches the operator")
        build = (whole_cut_proof(rec) or {}).get("build")
        if build:
            build_dir = (root / str(build).rstrip("/")).resolve()
            if not path.resolve().is_relative_to(build_dir):
                raise QueueError(f"{rec['id']}: the critic report {critic} lives outside the proof's build {build} - "
                                 f"the report rides with the cut it read")


def build_page(data: dict, root: Path, out_dir: Path, live: dict | None = None) -> Path:
    check_critic_files(data, root)
    out_dir.mkdir(parents=True, exist_ok=True)
    _sync_dir(out_dir / FRAMES_SUBDIR, {frame_name(p): root / p for p in frames_to_copy(data, root)})
    crops = out_dir / CROPS_SUBDIR
    crops.mkdir(exist_ok=True)
    names: set[str] = set()
    for rec in answerable_items(data):
        for n, p in enumerate(rec.get("proofs") or []):
            if p["type"] == "crop":
                RQP.write_crop(p, rec["id"], n, root, crops)
                names.update(RQP.crop_names(rec["id"], n))
    for old in crops.iterdir():
        if old.is_file() and old.name not in names:
            old.unlink()
    source_clips = root / OUT_REL / CLIPS_SUBDIR
    if source_clips.resolve() != (out_dir / CLIPS_SUBDIR).resolve():   # a page written elsewhere carries its clips
        present = {c: source_clips / c for c in clips_named(data) if (source_clips / c).is_file()}
        if present:
            _sync_dir(out_dir / CLIPS_SUBDIR, present)
    index = out_dir / "index.html"
    index.write_bytes(render_page(data, root, live).encode("utf-8"))
    return index


# ---------------------------------------------------------------- cli

def print_answers(data: dict, answers_path: Path) -> None:
    latest = latest_answers(answers_path)
    for rec in data["items"]:
        a = latest.get(rec["id"])
        if a is None:
            if rec["status"] == "open":
                print(f"{rec['id']}: {'owed by the agent' if rec['kind'] == 'owed' else 'open'}, no answer")
            continue
        if rec["status"] == "ruled":
            applied = f"applied ({rec['ruling']})"
        elif rec["kind"] == "owed":
            applied = "applied (owed by the agent)"
        elif rec.get("answer"):
            applied = f"applied in part ({rec['answer']['ruling']}; still open)"
        else:
            applied = "NOT APPLIED (still open)"
        print(f"{rec['id']}: {a['choice']!r} at {a['at']} - {applied}; note: {a.get('note') or '-'}")
    for item_id in sorted(set(latest) - {r["id"] for r in data["items"]}):
        print(f"{item_id}: answered but not in the data")
    print(f"{len(latest)} answered | {len(answerable_items(data))} answerable, {len(owed_items(data))} owed, "
          f"{len(ruled_items(data))} ruled ({len(data['items'])} records) - {answers_path}")


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the markdown, the page, its frames and crops")
    mode.add_argument("--check", action="store_true", help="exit 1 when the tracked markdown is stale")
    mode.add_argument("--answers", action="store_true", help="print the latest answer per item")
    ap.add_argument("--data", type=Path, default=ROOT / DATA_REL)
    ap.add_argument("--md", type=Path, default=ROOT / MD_REL)
    ap.add_argument("--out", type=Path, default=ROOT / OUT_REL)
    ap.add_argument("--answers-file", type=Path, default=ROOT / ANSWERS_REL)
    ap.add_argument("--root", type=Path, default=ROOT, help="where the where-to-look paths resolve")
    ap.add_argument("--no-probe", action="store_true", help="do not GET the player links (tests)")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        data = load_data(args.data)
    except (OSError, ValueError) as exc:
        print(f"review queue data refused: {exc}", file=sys.stderr)
        return 2
    for line in WARNINGS:                                  # P67 T5: named, not fatal, until CRITIC_REQUIRED flips
        print(line)
    if args.answers:
        print_answers(data, args.answers_file)
        return 0
    text = render_markdown(data)
    if args.check:
        current = args.md.read_text(encoding="utf-8") if args.md.is_file() else None
        if current != text:
            print(f"STALE: {args.md.name} does not match {args.data.name} - run build_review_queue.py --write",
                  file=sys.stderr)
            return 1
        print(f"ok: {args.md.name} is current ({len(answerable_items(data))} answerable, {len(owed_items(data))} owed, "
              f"{len(ruled_items(data))} ruled)")
        return 0
    live = None if args.no_probe else probe_players(data)
    try:
        index = build_page(data, args.root, args.out, live)
    except QueueError as exc:
        print(f"review queue page refused: {exc}", file=sys.stderr)
        return 2
    args.md.write_bytes(text.encode("utf-8"))
    counts = " | ".join(f"{k} {sum(i['kind'] == k for i in answerable_items(data))}" for k in ANSWERABLE_KINDS)
    clips_dir = args.root / OUT_REL / CLIPS_SUBDIR
    missing = [c for c in clips_named(data) if not (clips_dir / c).is_file()]
    dead = sorted(u for u, ok in (live or {}).items() if not ok)
    print(args.md)
    print(index)
    print(f"{len(answerable_items(data))} answerable ({counts}) | {len(owed_items(data))} owed | "
          f"{len(ruled_items(data))} ruled | {len(frames_to_copy(data, args.root))} frames copied | "
          f"{len(clips_named(data)) - len(missing)} of {len(clips_named(data))} clips on disk | "
          f"players not answering: {', '.join(dead) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

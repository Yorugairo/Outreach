"""THE REVIEW QUEUE - one page of everything waiting on the operator, built from review-queue.v1.json only.

The data (`docs/content-video-engine/review-queue.v1.json`, tracked) holds one record per item. This builder writes:
  (a) `docs/content-video-engine/REVIEW-QUEUE.md` - the readable record (tracked): a header, one table per kind, then
      "Ruled since the last pass";
  (b) `content/video_engine/review/queue/index.html` - the interactive page (gitignored, `.gitignore:77`), with every
      frame it shows COPIED into `frames/` beside it (a served review link is a frozen copy). A where-to-look entry
      whose proof does not exist shows the explicit "no proof yet" marker, so the gap stays visible.
The page saves answers only through `serve_review_queue.py` (POST /answer, appended to review-answers.jsonl). Applying
an answer - a ruling, its backlog row, `status: ruled` - stays the parent's; neither the page nor the server rules.

    python content/video_engine/scripts/build_review_queue.py --write | --check | --answers
        [--data PATH] [--md PATH] [--out DIR] [--answers-file PATH] [--root DIR]

Deterministic: the same data and frames give byte-identical outputs. `--check` compares only the TRACKED markdown (a
clean checkout has no page) and exits 1 naming it when stale. Stdlib only.
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parents[3]
DATA_REL = "docs/content-video-engine/review-queue.v1.json"
MD_REL = "docs/content-video-engine/REVIEW-QUEUE.md"
OUT_REL = "content/video_engine/review/queue"
ANSWERS_REL = "docs/content-video-engine/review-answers.jsonl"
FRAMES_SUBDIR = "frames"
NO_PROOF_MARKER = "no proof yet"
OTHER = "other"
KINDS = ("watch", "look", "rule", "approve")
KIND_TITLES = {"watch": "Watch", "look": "Look", "rule": "Rule", "approve": "Approve / push"}
STATUSES = ("open", "ruled")
REQUIRED = ("id", "ids", "kind", "title", "judge", "where", "options", "recommendation", "blocks", "sources", "status",
            "ruling")
WHERE_TARGETS = ("path", "url", "missing", "command")
SERVE_CMD = "python content/video_engine/scripts/serve_player.py {build} --port {port}"
RULED_HEADING = "Ruled since the last pass"


class QueueError(ValueError):
    """A record the schema refuses; the message names the record and the field."""


# ---------------------------------------------------------------- data

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
    for w in rec["where"]:
        if not isinstance(w, dict) or "label" not in w or not any(t in w for t in WHERE_TARGETS):
            raise QueueError(f"{name}: a where entry needs a label and one of {', '.join(WHERE_TARGETS)}")


def validate(items: list) -> list[dict]:
    """Refuse by name: a missing field, an unknown kind or status, a duplicate id, a where entry with no target."""
    if not isinstance(items, list):
        raise QueueError("the queue's items must be a list of records")
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
        if entry.get("stale"):
            return f"~~{entry['url']}~~ **stale** ({label}; serve with `{serve_hint(entry)}`)"
        return f"{label}: {entry['url']} (build `{entry.get('build')}`)"
    note = f" - {entry['note']}" if entry.get("note") else ""
    stale = " **stale**" if entry.get("stale") else ""
    return f"{label}: `{entry['path']}`{stale}{note}"


def md_row(rec: dict) -> str:
    where = "<br>".join(md_where(w) for w in rec["where"])
    options = " / ".join(rec["options"]) or "free answer"
    rec_text = rec["recommendation"] if rec["recommendation"] is not None else "none recorded"
    return "| " + " | ".join(cell(c) for c in (
        f"`{rec['id']}`", f"**{rec['title']}** ({', '.join(rec['ids'])})", rec["judge"], where, options, rec_text,
        rec["blocks"], "<br>".join(rec["sources"]))) + " |"


def md_header(data: dict) -> list[str]:
    return [
        "# REVIEW QUEUE - everything waiting on the operator",
        "",
        "One record of every open operator judgement (watch, look, rule, approve), generated from "
        "[`review-queue.v1.json`](review-queue.v1.json) by `content/video_engine/scripts/build_review_queue.py --write`; "
        "do not edit this file by hand. It supersedes "
        "[`OPEN-GATES-AND-QUESTIONS-2026-09-12.md`](OPEN-GATES-AND-QUESTIONS-2026-09-12.md).",
        "",
        f"- **As of** {data.get('as_of')} at `{data.get('head')}`; {len(open_items(data))} open, "
        f"{len(ruled_items(data))} ruled since the last pass.",
        "- **`approved` is the operator's word.** The agent's recommendation is labelled as the agent's; it is never a ruling.",
        "- **How an item enters and leaves** (`docs/runbooks/PRP_EXECUTION.md`): every human gate a plan names gets a row "
        "here in the same change that frames it, and a backlog row whose status waits on the operator gets one the same "
        "way; it leaves only with the operator's ruling, written to `docs/portable/OPERATOR-RULINGS.md` and to the plan.",
        "- **Answer in the page:** `python content/video_engine/scripts/serve_review_queue.py` (http://127.0.0.1:8766/) "
        "appends each saved answer to `review-answers.jsonl`. **Agents read the answers** with "
        "`build_review_queue.py --answers`; the parent applies them.",
        "- Paths are repo-relative in the main checkout. A **stale** link names a port nothing reliable serves and the "
        "command that serves its build; **no proof yet** marks a proof that does not exist.",
        "",
    ]


def render_markdown(data: dict) -> str:
    items = open_items(data)
    lines = md_header(data)
    header = ["| id | item | what to judge | where to look | options | agent's recommendation | blocks | sources |",
              "|---|---|---|---|---|---|---|---|"]
    for kind in KINDS:
        rows = [md_row(r) for r in items if r["kind"] == kind]
        lines += [f"## {KIND_TITLES[kind]} ({len(rows)})", ""]
        lines += (header + rows) if rows else ["Nothing open."]
        lines.append("")
    lines += [f"## {RULED_HEADING}", "", "| id | item | ruling / evidence | sources |", "|---|---|---|---|"]
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
    return sorted({w["path"] for i in data["items"] for w in i["where"] if is_frame(w) and (root / w["path"]).is_file()})


def page_note(entry: dict) -> str:
    return f'<br><span class="small">{esc(entry["note"])}</span>' if entry.get("note") else ""


def page_url(entry: dict, label: str) -> str:
    if entry.get("stale"):
        return (f'<li class="stale"><span class="flag">stale</span> {label}: <s>{esc(entry["url"])}</s> - serve it with '
                f'<code>{esc(serve_hint(entry))}</code>{page_note(entry)}</li>')
    return (f'<li><a href="{esc(entry["url"])}" target="_blank" rel="noopener">{label}</a> '
            f'<span class="small">(served; build <code>{esc(entry.get("build"))}</code>)</span></li>')


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
        return page_url(entry, label)
    if is_frame(entry):
        return page_frame(entry, label, root)
    stale = '<span class="flag">stale</span> ' if entry.get("stale") else ""
    return f'<li>{stale}{label}: <code>{esc(entry["path"])}</code>{page_note(entry)}</li>'


def page_controls(rec: dict, n: int) -> str:
    choices = [*rec["options"], OTHER]
    radios = "".join(
        f'<label><input type="radio" name="c{n}" value="{esc(c)}"> {esc(c)}</label>' for c in choices)
    return (f'<form class="answer"><fieldset><legend>Your answer</legend>{radios}</fieldset>'
            f'<label class="notelabel" for="note{n}">Note</label><textarea id="note{n}" rows="3"></textarea>'
            f'<div class="row"><button type="submit">Save</button><span class="saved" role="status"></span></div></form>')


def page_card(rec: dict, n: int, root: Path) -> str:
    recommendation = esc(rec["recommendation"]) if rec["recommendation"] is not None else "<i>none recorded</i>"
    where = "".join(page_where(w, root) for w in rec["where"])
    sources = "".join(f"<li><code>{esc(s)}</code></li>" for s in rec["sources"])
    return (
        f'<article class="card" data-id="{esc(rec["id"])}" data-kind="{esc(rec["kind"])}">'
        f'<h3>{esc(rec["title"])}</h3><p class="ids">{esc(" / ".join(rec["ids"]))}</p>'
        f'<p class="q">{esc(rec["judge"])}</p>'
        f'<p class="agent"><b>The agent\'s recommendation:</b> {recommendation}</p>'
        f'<h4>Where to look</h4><ul class="where">{where}</ul>'
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
.agent{background:#25313C;color:#F4E6C7;padding:8px 12px;border-radius:4px}
ul.where{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px}
ul.where li{background:#fff;border:1px solid #c9b58f;padding:6px;word-break:break-word}
ul.where img{display:block;width:100%;height:auto;border:1px solid #25313C}
.small{font-size:.82em}code{font-family:ui-monospace,Consolas,monospace;font-size:.9em}
li.stale{border:2px dashed #B8402A!important}.flag{background:#B8402A;color:#fff;padding:0 6px;border-radius:8px;font-size:.8em}
li.none{border:2px dashed #c33!important;background:#fff6f6!important}.noproof{color:#a11;font-weight:700}
fieldset{border:1px solid #25313C;margin:10px 0 6px}fieldset label{display:inline-block;margin:2px 14px 2px 0}
.row{display:flex;gap:12px;align-items:center;margin-top:6px}.saved{font-size:.9em}.err{color:#a11;font-weight:600}
.banner{background:#B8402A;color:#fff;padding:8px 12px;margin:8px 0}.hidden{display:none}
table.ruled{border-collapse:collapse;width:100%;background:#fbf3e1}table.ruled td,table.ruled th{border:1px solid #25313C;
padding:6px 8px;vertical-align:top;text-align:left}
@media (max-width:640px){body{padding:10px}.bar{position:static}ul.where{grid-template-columns:1fr}
table.ruled,table.ruled tbody,table.ruled tr,table.ruled td{display:block}}
"""

JS = """
(function(){
var answers={},cards=[].slice.call(document.querySelectorAll('article.card'));
function show(card){var a=answers[card.dataset.id],s=card.querySelector('.saved');card.classList.toggle('answered',!!a);
if(!a){s.textContent='';return;}s.className='saved';s.textContent='saved '+a.at+' - '+a.choice;
card.querySelectorAll('input[type=radio]').forEach(function(r){r.checked=(r.value===a.choice);});
card.querySelector('textarea').value=a.note||'';}
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
cards.forEach(function(card){card.querySelector('form').addEventListener('submit',function(ev){ev.preventDefault();
var r=card.querySelector('input[type=radio]:checked'),s=card.querySelector('.saved');
if(!r){s.className='saved err';s.textContent='pick a choice first';return;}
var body=JSON.stringify({item:card.dataset.id,choice:r.value,note:card.querySelector('textarea').value});
s.className='saved';s.textContent='saving...';
fetch('answer',{method:'POST',headers:{'Content-Type':'application/json'},body:body}).then(function(res){
return res.json().then(function(j){if(!res.ok||!j.ok)throw new Error(j.error||res.status);answers[j.answer.item]=j.answer;
refresh();});}).catch(function(e){s.className='saved err';s.textContent='not saved: '+e.message;});});});
fetch('answers',{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error(r.status);return r.json();})
.then(function(j){answers=j;refresh();})
.catch(function(){document.getElementById('offline').classList.remove('hidden');progress();});
progress();
})();
"""


def page_sections(data: dict, root: Path) -> str:
    items, sections, n = open_items(data), [], 0
    for kind in KINDS:
        rows = [r for r in items if r["kind"] == kind]
        cards = []
        for r in rows:
            cards.append(page_card(r, n, root))
            n += 1
        sections.append(f'<section class="kind" id="kind-{kind}"><h2>{KIND_TITLES[kind]} ({len(rows)})</h2>'
                        f'{"".join(cards)}</section>')
    return "".join(sections)


def page_ruled(data: dict, root: Path) -> str:
    rows = "".join(
        f'<tr><td><b>{esc(r["title"])}</b><br><span class="small">{esc(" / ".join(r["ids"]))}</span></td>'
        f'<td>{esc(r["ruling"])}</td><td><ul class="where">{"".join(page_where(w, root) for w in r["where"])}</ul></td></tr>'
        for r in ruled_items(data))
    return (f'<section id="ruled"><h2>{RULED_HEADING} ({len(ruled_items(data))})</h2>'
            f'<table class="ruled"><thead><tr><th>item</th><th>ruling / evidence</th><th>where</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></section>')


def render_page(data: dict, root: Path) -> str:
    kind_opts = "".join(f'<option value="{k}">{KIND_TITLES[k]}</option>' for k in KINDS)
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Review queue - {esc(data.get("as_of"))}</title><style>{CSS}</style></head><body>'
        f'<h1>Review queue</h1><p>Everything waiting on the operator, as of {esc(data.get("as_of"))} '
        f'(<code>{esc(data.get("head"))}</code>). <b>approved</b> is your word; the recommendation on each card is the '
        f'agent\'s. Saving records your answer; the parent applies it as a ruling.</p>'
        '<p id="offline" class="banner hidden">Not served: answers cannot be read or saved. Start '
        '<code>python content/video_engine/scripts/serve_review_queue.py</code> and open http://127.0.0.1:8766/</p>'
        '<div class="bar"><span id="progress" class="progress" aria-live="polite"></span>'
        f'<label>Kind <select id="fkind"><option value="all">all</option>{kind_opts}</select></label>'
        '<label>State <select id="fstate"><option value="all">all</option><option value="open">open</option>'
        '<option value="answered">answered</option></select></label></div>'
        f'{page_sections(data, root)}{page_ruled(data, root)}<script>{JS}</script></body></html>\n')


def build_page(data: dict, root: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = out_dir / FRAMES_SUBDIR
    frames.mkdir(exist_ok=True)
    wanted = {frame_name(p): p for p in frames_to_copy(data, root)}
    for old in frames.iterdir():   # this folder is the builder's own output; drop frames the data no longer names
        if old.is_file() and old.name not in wanted:
            old.unlink()
    for name, rel in wanted.items():
        shutil.copyfile(root / rel, frames / name)
    index = out_dir / "index.html"
    index.write_bytes(render_page(data, root).encode("utf-8"))
    return index


# ---------------------------------------------------------------- cli

def print_answers(data: dict, answers_path: Path) -> None:
    latest = latest_answers(answers_path)
    for rec in data["items"]:
        a = latest.get(rec["id"])
        if a is None:
            if rec["status"] == "open":
                print(f"{rec['id']}: open, no answer")
            continue
        applied = "NOT APPLIED (still open)" if rec["status"] == "open" else "applied (ruled)"
        print(f"{rec['id']}: {a['choice']!r} at {a['at']} - {applied}; note: {a.get('note') or '-'}")
    for item_id in sorted(set(latest) - {r["id"] for r in data["items"]}):
        print(f"{item_id}: answered but not in the data")
    print(f"{len(latest)} answered of {len(open_items(data))} open items ({len(data['items'])} records) - {answers_path}")


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the markdown, the page and its frames")
    mode.add_argument("--check", action="store_true", help="exit 1 when the tracked markdown is stale")
    mode.add_argument("--answers", action="store_true", help="print the latest answer per item")
    ap.add_argument("--data", type=Path, default=ROOT / DATA_REL)
    ap.add_argument("--md", type=Path, default=ROOT / MD_REL)
    ap.add_argument("--out", type=Path, default=ROOT / OUT_REL)
    ap.add_argument("--answers-file", type=Path, default=ROOT / ANSWERS_REL)
    ap.add_argument("--root", type=Path, default=ROOT, help="where the where-to-look paths resolve")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        data = load_data(args.data)
    except (OSError, ValueError) as exc:
        print(f"review queue data refused: {exc}", file=sys.stderr)
        return 2
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
        print(f"ok: {args.md.name} is current ({len(open_items(data))} open, {len(ruled_items(data))} ruled)")
        return 0
    args.md.write_bytes(text.encode("utf-8"))
    index = build_page(data, args.root, args.out)
    counts = " | ".join(f"{k} {sum(i['kind'] == k for i in open_items(data))}" for k in KINDS)
    print(args.md)
    print(index)
    print(f"{len(open_items(data))} open ({counts}) | {len(ruled_items(data))} ruled | "
          f"{len(frames_to_copy(data, args.root))} frames copied")
    return 0


if __name__ == "__main__":
    sys.exit(main())

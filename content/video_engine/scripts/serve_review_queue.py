"""THE REVIEW QUEUE SERVER - the operator marks answers in the page; each saved answer is one appended line.

    python content/video_engine/scripts/serve_review_queue.py [--port 8766] [--no-open]

At start it FIRST regenerates the page, its frames and crops from review-queue.v1.json (build_review_queue.build_page),
probing every player link so one that does not answer is never shown as a link, then serves the page folder on 127.0.0.1 only with `Cache-Control: no-store`.

    GET  /answers  ->  200 {"<item id>": {item, choice, note, at, by}, ...}   the latest line per item
    POST /answer   <-  one JSON object {item, choice, note}
                   ->  200 {"ok": true, "answer": {...}} and ONE line appended to review-answers.jsonl
                   ->  400 {"ok": false, "error": "..."} naming the refusal; nothing appended (an item owed by the
                           agent, a ruled item and an unknown id are all refused by name)

Mirrors serve_player.py's write door: one POST route, a validated body, a JSON answer, a named refusal. The answers
file is append-only - never rewritten, never truncated; the latest line per item is its answer. The server never
writes a ruling. Stdlib only.

ONE item grammar beyond a record id (P65 T4): `<batch-card-id>#<candidate-id>` answers ONE candidate of a `batch`
card - its choices are approve / deny and its note opens with a reason from the fixed list (P65 T1, read from
`lab_judgement.schema.json` through build_review_queue.REASONS). Everything else is unchanged: one POST route, the
same append-only file, repeated `item` keys already a tested shape, and the server still rules nothing.

The item index is RE-READ whenever review-queue.v1.json changes on disk (its mtime), so a card the assembly pass
converts from owed to watch while the server runs is answerable at once - on 2026-09-15 the operator's Save on
r26-133 was refused as 'owed by the agent' by a server started the day before, on a copy read once at start.
"""
from __future__ import annotations

import argparse
import functools
import json
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_review_queue as BRQ  # noqa: E402

DEFAULT_PORT = 8766
NOTE_MAX = 4000          # characters in one answer's note
BODY_MAX = 64_000        # bytes in one POST body
ANSWER_KEYS = {"item", "choice", "note"}


def refuse_candidate(item: str, body: object, items_by_id: dict[str, dict]) -> str | None:
    """The named reason ONE candidate's answer is refused (P65 T4). The item is `<batch-card-id>#<candidate-id>`: the
    card resolves to an OPEN batch, the candidate to one of its `candidates`, the choice is approve or deny, and the
    note opens with a reason from the fixed nine (the free text after it qualifies the reason, never replaces it)."""
    card_id, _, cand_id = item.partition(BRQ.BATCH_SEP)
    rec = items_by_id.get(card_id)
    if rec is None or rec["kind"] != "batch":
        return (f"unknown batch {card_id!r} in item {item!r}: an item with {BRQ.BATCH_SEP!r} answers one candidate "
                "of an open batch card in review-queue.v1.json")
    cands = [c["id"] for c in rec.get("candidates") or []]
    if cand_id not in cands:
        return f"unknown candidate {cand_id!r} for {card_id}: one of {', '.join(cands)}"
    choice = body.get("choice")
    if choice not in BRQ.BATCH_CHOICES:
        return f"invalid choice {choice!r} for {item}: one of {', '.join(BRQ.BATCH_CHOICES)}"
    note = body.get("note")
    if not isinstance(note, str) or not BRQ.note_reason(note):
        return (f"the note for {item} opens with a reason from the list and a colon "
                f"(\"<reason>: <free text>\"): one of {', '.join(BRQ.REASONS)}")
    return None


def refuse_reason(body: object, items_by_id: dict[str, dict], owed_by_id: dict[str, dict] | None = None) -> str | None:
    """The named reason a POST /answer body is refused, or None when it is a valid answer. `items_by_id` holds only the
    answerable items; an owed item is refused by name (E99 s14: it is the agent's work, never the operator's). An item
    carrying BATCH_SEP is one candidate of a batch card and takes the branch above."""
    if not isinstance(body, dict):
        return "the body is not one JSON object: send {\"item\": ..., \"choice\": ..., \"note\": ...}"
    extra = sorted(set(body) - ANSWER_KEYS)
    if extra:
        return f"unknown field(s) {', '.join(extra)}: an answer is {{item, choice, note}}"
    item = body.get("item")
    if isinstance(item, str) and item in (owed_by_id or {}):
        return f"{item} is owed by the agent, not open for an answer: {owed_by_id[item]['owed']}"
    if isinstance(item, str) and BRQ.BATCH_SEP in item:
        refusal = refuse_candidate(item, body, items_by_id)
        if refusal:
            return refusal
    else:
        if not isinstance(item, str) or item not in items_by_id:
            return f"unknown item {item!r}: not an id in review-queue.v1.json"
        choices = [*items_by_id[item]["options"], BRQ.OTHER]
        choice = body.get("choice")
        if choice not in choices:
            return f"invalid choice {choice!r} for {item}: one of {', '.join(choices)}"
    note = "" if body.get("note") is None else body.get("note")
    if not isinstance(note, str):
        return "the note is not a string"
    if len(note) > NOTE_MAX:
        return f"the note is {len(note)} characters, over NOTE_MAX {NOTE_MAX}"
    return None


class QueueIndex:
    """The answerable and the owed items, keyed by id, re-read from the data file whenever its mtime changes. One
    lock guards the re-read; a read that fails (a half-written file) keeps the last good index and says so."""

    def __init__(self, data_path: Path, lock: threading.Lock):
        self.data_path = Path(data_path)
        self.lock = lock
        self.mtime_ns: int | None = None
        self.items_by_id: dict[str, dict] = {}
        self.owed_by_id: dict[str, dict] = {}
        self.reloads = 0

    def current(self) -> tuple[dict[str, dict], dict[str, dict]]:
        with self.lock:
            try:
                m = self.data_path.stat().st_mtime_ns
            except OSError:
                return self.items_by_id, self.owed_by_id
            if m != self.mtime_ns:
                try:
                    data = BRQ.load_data(self.data_path)
                except (OSError, ValueError) as exc:
                    print(f"review queue: {self.data_path.name} changed but did not load ({exc}); keeping the last index",
                          file=sys.stderr, flush=True)
                    return self.items_by_id, self.owed_by_id
                self.items_by_id = {i["id"]: i for i in BRQ.answerable_items(data)}   # a ruled or an owed item takes no answer
                self.owed_by_id = {i["id"]: i for i in BRQ.owed_items(data)}
                self.mtime_ns = m
                self.reloads += 1
            return self.items_by_id, self.owed_by_id


class QueueHandler(SimpleHTTPRequestHandler):
    def __init__(self, *a, index=None, answers_path=None, lock=None, quiet=False, **kw):
        self.index = index
        self.answers_path = answers_path
        self.lock = lock
        self.quiet = quiet
        super().__init__(*a, **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")   # the page is regenerated at every start; never a cached copy
        super().end_headers()

    def log_message(self, *a):
        if not self.quiet:
            super().log_message(*a)

    def do_GET(self):
        if urlparse(self.path).path.rstrip("/") == "/answers":
            with self.lock:
                latest = BRQ.latest_answers(self.answers_path)
            return self._json(200, latest)
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path.rstrip("/") == "/answer":
            return self._answer()
        return self._json(404, {"ok": False, "error": "the only POST this server takes is /answer"})

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> tuple[object, str | None]:
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return None, "a Content-Length that is not a number"
        if n > BODY_MAX:
            return None, f"the body is {n} bytes, over {BODY_MAX}"
        try:
            return json.loads(self.rfile.read(n).decode("utf-8")), None
        except (ValueError, UnicodeDecodeError) as exc:
            return None, f"the body is not one JSON object: {exc}"

    def _answer(self):
        body, error = self._read_body()
        items_by_id, owed_by_id = self.index.current()   # the data file re-read if it changed since the last answer
        reason = error or refuse_reason(body, items_by_id, owed_by_id)
        if reason:
            return self._json(400, {"ok": False, "error": reason})
        answer = {"item": body["item"], "choice": body["choice"], "note": body.get("note") or "",
                  "at": datetime.now().astimezone().isoformat(timespec="seconds"), "by": "operator"}
        line = json.dumps(answer, ensure_ascii=False) + "\n"
        with self.lock:
            self.answers_path.parent.mkdir(parents=True, exist_ok=True)
            with self.answers_path.open("a", encoding="utf-8", newline="\n") as fh:   # append-only
                fh.write(line)
        return self._json(200, {"ok": True, "answer": answer})


def make_server(port: int, data_path: Path, out_dir: Path, answers_path: Path, root: Path = BRQ.ROOT,
                quiet: bool = False, probe: bool = True) -> ThreadingHTTPServer:
    """Regenerate the page from the data, then bind 127.0.0.1:port (0 = a free port). Not yet serving."""
    data = BRQ.load_data(data_path)
    BRQ.build_page(data, root, out_dir, BRQ.probe_players(data) if probe else None)
    lock = threading.Lock()
    index = QueueIndex(data_path, lock)
    index.current()   # the first read happens now, so a data file that does not load refuses the start by name
    handler = functools.partial(QueueHandler, directory=str(out_dir), index=index,
                                answers_path=answers_path, lock=lock, quiet=quiet)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    httpd.queue_index = index   # type: ignore[attr-defined]  (tests read the reload count)
    return httpd


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--no-open", action="store_true", help="do not open the browser")
    ap.add_argument("--data", type=Path, default=BRQ.ROOT / BRQ.DATA_REL)
    ap.add_argument("--out", type=Path, default=BRQ.ROOT / BRQ.OUT_REL)
    ap.add_argument("--answers-file", type=Path, default=BRQ.ROOT / BRQ.ANSWERS_REL)
    args = ap.parse_args(argv)
    try:
        httpd = make_server(args.port, args.data, args.out, args.answers_file)
    except (OSError, ValueError) as exc:
        print(f"review queue server refused to start: {exc}", file=sys.stderr)
        return 2
    url = f"http://127.0.0.1:{httpd.server_address[1]}/"
    print(f"review queue: {url} (answers -> {args.answers_file})", flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

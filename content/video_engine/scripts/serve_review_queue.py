"""THE REVIEW QUEUE SERVER - the operator marks answers in the page; each saved answer is one appended line.

    python content/video_engine/scripts/serve_review_queue.py [--port 8766] [--no-open]

At start it FIRST regenerates the page and its frames from review-queue.v1.json (build_review_queue.build_page), so the
operator never opens a stale page, then serves the page folder on 127.0.0.1 only with `Cache-Control: no-store`.

    GET  /answers  ->  200 {"<item id>": {item, choice, note, at, by}, ...}   the latest line per item
    POST /answer   <-  one JSON object {item, choice, note}
                   ->  200 {"ok": true, "answer": {...}} and ONE line appended to review-answers.jsonl
                   ->  400 {"ok": false, "error": "..."} naming the refusal; nothing appended

Mirrors serve_player.py's write door: one POST route, a validated body, a JSON answer, a named refusal. The answers
file is append-only - never rewritten, never truncated; the latest line per item is its answer. The server never
writes a ruling. Stdlib only.
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


def refuse_reason(body: object, items_by_id: dict[str, dict]) -> str | None:
    """The named reason a POST /answer body is refused, or None when it is a valid answer."""
    if not isinstance(body, dict):
        return "the body is not one JSON object: send {\"item\": ..., \"choice\": ..., \"note\": ...}"
    extra = sorted(set(body) - ANSWER_KEYS)
    if extra:
        return f"unknown field(s) {', '.join(extra)}: an answer is {{item, choice, note}}"
    item = body.get("item")
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


class QueueHandler(SimpleHTTPRequestHandler):
    def __init__(self, *a, items_by_id=None, answers_path=None, lock=None, quiet=False, **kw):
        self.items_by_id = items_by_id or {}
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
        reason = error or refuse_reason(body, self.items_by_id)
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
                quiet: bool = False) -> ThreadingHTTPServer:
    """Regenerate the page from the data, then bind 127.0.0.1:port (0 = a free port). Not yet serving."""
    data = BRQ.load_data(data_path)
    BRQ.build_page(data, root, out_dir)
    items_by_id = {i["id"]: i for i in BRQ.open_items(data)}   # a ruled item takes no new answer
    handler = functools.partial(QueueHandler, directory=str(out_dir), items_by_id=items_by_id,
                                answers_path=answers_path, lock=threading.Lock(), quiet=quiet)
    return ThreadingHTTPServer(("127.0.0.1", port), handler)


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

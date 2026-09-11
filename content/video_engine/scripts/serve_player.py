"""THE REVIEW SERVER - one server for every project, with the hot-reload loop (P51 T4).

    python serve_player.py <build dir> [--port N] [--watch] [--no-check]

Without --watch it is the no-store range server the two projects have served every review on: a
rebuilt player.html is always the one served (2026-09-05), `.mjs` goes out as text/javascript (a
module served as application/octet-stream is refused by the browser's strict MIME check, so a
split build would show its shell and mount nothing - P51 T1), and Range/seek works so the audio
element can scrub. The projects' own `serve_player.py` are thin wrappers on this file and keep
their CLI (`[port] [dir]`) and their default port.

With --watch it is the animator's loop. Every 0.25 s it stats three files - the project's shot
table, `<build>/overrides.json` (the sidecar; watched whether or not its consumer has landed) and
the build's own compiled timeline. When one moves:

  1. the COMPILER is re-run in process for the shot table and the sidecar (never a subprocess:
     the re-compile reads `<build>/player.json`'s `compile` block, which `authoring.table`
     writes at build time, so the server never guesses an episode's facts); the compiled timeline
     is rewritten, and `assets.json` only when the asset map actually moved;
  2. the generation counter moves, and every held `GET /reload?since=<gen>` is answered;
  3. the DETERMINISM CHECK runs on the instants the diff named (warm and cold, hashed) and its
     verdict is published as a second generation the page does not re-mount for.

    GET /reload?since=<gen>  ->  200 application/json, Cache-Control: no-store
      {"gen": 7,                       the server's generation now
       "reload": true,                 whether the page should re-fetch the timeline and reload()
       "changed": [55.31, 59.57],      the instants the change touched (the timeline diff's)
       "why": ["s04 dock ... enter"],  one reason per instant, in the same order
       "reason": "overrides.json",     the file that moved
       "timeline": "tokyo-short.timeline.json",
       "determinism": "ok" | "ok (1 known R26-21 at 43.20)" | "mismatch at 55.31" | "not run",
       "compile_ms": 812,              null when nothing was compiled
       "timeout": false}               true when the 25 s hold expired with the generation still
    The server answers at once when gen > since; otherwise it HOLDS the request up to 25 s and
    answers the moment the generation moves. The page's client (render_baseline.WATCH_CLIENT,
    in the split shell) only runs when `?watch=1` is on the URL - a served build without the flag
    is exactly the page it was before this file.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SCRIPTS = Path(__file__).resolve().parent
POLL_S = 0.25          # the watcher's tick: no third-party watcher, just os.stat
HOLD_S = 25.0          # how long /reload holds a request before answering on the timeout
MANIFEST_NAME = "player.json"
OVERRIDES_NAME = "overrides.json"
CHECK_MAX = 6          # instants the server's own determinism check renders (the CLI checks all)


# ---- the static side (what the two projects' servers always were) ------------------------------------------------

class RangeFileWrapper:
    def __init__(self, f, length):
        self.f = f
        self.remaining = length

    def read(self, size=-1):
        if self.remaining <= 0:
            return b""
        to_read = self.remaining if (size == -1 or size > self.remaining) else size
        data = self.f.read(to_read)
        self.remaining -= len(data)
        return data

    def close(self):
        self.f.close()


class ReviewHandler(SimpleHTTPRequestHandler):
    # .mjs is not in Python's mimetypes table on Windows, and a module served as
    # application/octet-stream is refused by the browser's strict MIME check (P51 T1).
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".mjs": "text/javascript"}

    def __init__(self, *a, watch=None, quiet=False, **kw):
        self.watch = watch
        self.quiet = quiet
        super().__init__(*a, **kw)

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")   # a rebuilt player.html is always the one served (2026-09-05)
        super().end_headers()

    def log_message(self, *a):
        if not self.quiet:
            super().log_message(*a)

    def do_GET(self):
        if urlparse(self.path).path.rstrip("/") == "/reload":
            return self._reload()
        return super().do_GET()

    def _reload(self):
        q = parse_qs(urlparse(self.path).query)
        try:
            since = int(float(q.get("since", ["0"])[0]))
        except ValueError:
            since = 0
        if self.watch:
            answer = self.watch.wait(since, HOLD_S)
        else:
            time.sleep(HOLD_S)   # a generation that never moves still HOLDS: a page served without
            answer = {"gen": 0, "reload": False, "changed": [], "why": [],   # --watch must not spin
                      "reason": "not watching", "timeline": None,
                      "determinism": "not run", "compile_ms": None, "timeout": True}
        body = json.dumps(answer).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()
        range_header = self.headers.get("Range")
        if not range_header:
            return super().send_head()
        total_size = os.path.getsize(path)
        m = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if not m:
            return super().send_head()
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else total_size - 1
        if start >= total_size:
            self.send_error(416, "Requested Range Not Satisfiable")
            return None
        end = min(end, total_size - 1)
        length = end - start + 1
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{total_size}")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        f = open(path, "rb")
        f.seek(start)
        return RangeFileWrapper(f, length)


# ---- the loop ----------------------------------------------------------------------------------------------------

def _stamp(p: Path):
    try:
        st = p.stat()
        return (st.st_mtime_ns, st.st_size)
    except OSError:
        return None


def _incremental_write_split(orig):
    """The re-compile's write. The compiled timeline is rewritten every time, byte for byte as
    `render_baseline.write_split` writes it; assets.json, the page, the engine copy and the
    manifest only when the asset map actually moved - Tokyo's map is 31 MB, and rewriting it on
    every edit is the difference between a loop and a wait."""
    import render_baseline as RB

    def write(build_dir, timeline, uris, timeline_name, *a, **kw):
        build_dir = Path(build_dir)
        page, assets = build_dir / "player.html", build_dir / RB.ASSETS_NAME
        new = json.dumps(uris, separators=(",", ":"))
        if not page.exists() or not assets.exists() or assets.read_text(encoding="utf-8") != new:
            return orig(build_dir, timeline, uris, timeline_name, *a, **kw)
        (build_dir / timeline_name).write_text(json.dumps(timeline, indent=1), encoding="utf-8")
        return page

    return write


class Watch:
    """The watcher and the generation counter behind /reload."""

    def __init__(self, build: Path, check: bool = True, log=print):
        sys.path.insert(0, str(SCRIPTS))   # the server can be imported from anywhere; its siblings are here
        import gate_motion_density as G
        self.build = Path(build).resolve()
        self.check = check
        self.log = log
        self.cv = threading.Condition()
        self.gen = 1   # the build as served IS generation 1, so a client that opens at 0 is answered
        self.stop = threading.Event()   # at once with what it is looking at instead of waiting 25 s
        self.manifest = self._manifest()
        name = (self.manifest.get("compile") or {}).get("timeline_name") or self.manifest.get("timeline")
        self.tl_path = G._timeline_path(self.build, name)
        self.tl_prev = json.loads(self.tl_path.read_text(encoding="utf-8"))
        self.answer = {"gen": self.gen, "reload": False, "changed": [], "why": [], "reason": "start",
                       "timeline": self.tl_path.name, "determinism": "not run", "compile_ms": None,
                       "timeout": False}
        self.stamps = {p: _stamp(p) for p in self.targets()}

    # -- what is watched
    def _manifest(self) -> dict:
        p = self.build / MANIFEST_NAME
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def compile_block(self) -> dict | None:
        return self._manifest().get("compile")

    def shot_table(self) -> Path | None:
        c = self.compile_block()
        if c:
            return (self.build / c["episode_dir"] / c["shot_table_file"]).resolve()
        found = sorted(self.build.parent.glob("SHOT-TABLE*.py"))
        return found[0] if found else None

    def targets(self) -> dict[Path, str]:
        out: dict[Path, str] = {self.tl_path: "timeline", self.build / OVERRIDES_NAME: "overrides"}
        st = self.shot_table()
        if st:
            out[st] = "shot table"
        return out

    # -- the counter
    def wait(self, since: int, hold: float) -> dict:
        with self.cv:
            if self.gen > since:
                return dict(self.answer, timeout=False)
            self.cv.wait_for(lambda: self.gen > since, timeout=hold)
            return dict(self.answer, gen=self.gen, timeout=self.gen <= since)

    def bump(self, **fields) -> int:
        with self.cv:
            self.gen += 1
            self.answer = {**self.answer, **fields, "gen": self.gen, "timeout": False}
            self.cv.notify_all()
            return self.gen

    # -- the re-compile
    def recompile(self) -> tuple[bool, str, int]:
        c = self.compile_block()
        if not c:
            return False, "no compile block in player.json - the timeline is watched, not rebuilt", 0
        import render_baseline as RB
        sys.path.insert(0, str(SCRIPTS))
        import authoring.table as T
        import build_render_f as R
        R.STAMPED.update(c.get("stamped") or {})   # the episode's dock assets: registered in memory by the
        # build script while it authored the rows, recorded in the manifest by the compile that used them
        ep = (self.build / c["episode_dir"]).resolve()
        t0 = time.perf_counter()
        buf = io.StringIO()
        orig, RB.write_split = RB.write_split, _incremental_write_split(RB.write_split)
        try:
            with contextlib.redirect_stdout(buf):
                rc = T.compile_timeline(
                    ep, self.build,
                    timeline_name=c["timeline_name"], shot_table_file=c["shot_table_file"],
                    title=c["title"], subtitle=c["subtitle"], episode_id=c["episode_id"],
                    aspect=c["aspect"], caption_style=c["caption_style"], kinetics=dict(c["kinetics"]),
                    render=bool(c.get("render")))
        except (Exception, SystemExit) as e:   # a bad sidecar or a broken row must not kill the server -
            # and the compiler refuses a bad sidecar with SystemExit, which threading swallows in silence
            return False, f"{type(e).__name__}: {e}", int((time.perf_counter() - t0) * 1000)
        finally:
            RB.write_split = orig
        ms = int((time.perf_counter() - t0) * 1000)
        if rc != 0:
            tail = (buf.getvalue().strip().splitlines() or ["(no output)"])[-1]
            return False, f"the compiler exited {rc}: {tail}", ms
        return True, "", ms

    # -- one change
    def on_change(self, moved: list[tuple[Path, str]]) -> None:
        reason = ", ".join(sorted({p.name for p, _why in moved}))
        kinds = {why for _p, why in moved}
        compile_ms, err = None, ""
        if kinds & {"overrides", "shot table"}:
            ok, err, compile_ms = self.recompile()
            # THE COMPILE'S OWN WRITES ARE NOT THE NEXT ROUND'S CHANGE. The sidecar pass rewrites the
            # shot table with the effective rows (P51 T5), so a watcher that did not re-stamp every
            # target here would re-compile on its own output, for ever, 0.25 s apart.
            for p in self.targets():
                self.stamps[p] = _stamp(p)
            if not ok:
                self.log(f"  reload: {reason} -> COMPILE FAILED after {compile_ms} ms: {err}")
                self.bump(reload=False, changed=[], why=[], reason=reason,
                          determinism=f"not run (compile failed: {err})", compile_ms=compile_ms)
                self.stamps[self.tl_path] = _stamp(self.tl_path)
                return
        import determinism_check as DC
        new = json.loads(self.tl_path.read_text(encoding="utf-8"))
        self.stamps[self.tl_path] = _stamp(self.tl_path)   # our own write is not the next round's change
        changed = DC.changed_instants(self.tl_prev, new)
        same = new == self.tl_prev
        self.tl_prev = new
        gen = self.bump(reload=not same, changed=[t for t, _w in changed], why=[w for _t, w in changed],
                        reason=reason, determinism="running" if (self.check and changed) else "not run",
                        compile_ms=compile_ms)
        self.log(f"  reload: {reason} -> gen {gen}, {len(changed)} instant(s)"
                 + (f", compiled in {compile_ms} ms" if compile_ms is not None else "")
                 + ("" if not same else ", the timeline did not move"))
        if self.check and changed:
            try:
                rep = DC.run(self.build, changed, self.tl_path.name, max_instants=CHECK_MAX,
                             log=lambda s: self.log("  " + str(s)))
                verdict = rep["summary"]
            except (Exception, SystemExit) as e:
                verdict = f"error: {type(e).__name__}: {e}"
            self.bump(reload=False, determinism=verdict)
            self.log(f"  determinism: {verdict}")

    def run(self) -> None:
        while not self.stop.wait(POLL_S):
            try:
                targets = self.targets()
                moved = [(p, why) for p, why in targets.items() if _stamp(p) != self.stamps.get(p)]
                if not moved:
                    continue
                for p, _why in moved:
                    self.stamps[p] = _stamp(p)
                self.on_change(moved)
            except (Exception, SystemExit) as e:   # the watcher outlives a bad edit (SystemExit included:
                # threading's excepthook drops it silently, which is a watcher that stops for no visible reason)
                self.log(f"  watch error: {type(e).__name__}: {e}")

    def start(self) -> "Watch":
        threading.Thread(target=self.run, daemon=True, name="watch").start()
        return self

    def close(self) -> None:
        self.stop.set()


# ---- the doors ---------------------------------------------------------------------------------------------------

def start(directory: Path, port: int = 0, watch: bool = False, check: bool = True, quiet: bool = False):
    """Start the server (and the watcher when asked) without blocking. Returns (httpd, port, watch)."""
    import functools
    directory = Path(directory).resolve()
    if not directory.is_dir():
        raise SystemExit(f"{directory} is not a directory")
    w = Watch(directory, check=check, log=(lambda *_a: None) if quiet else print).start() if watch else None
    handler = functools.partial(ReviewHandler, directory=str(directory), watch=w, quiet=quiet)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True, name="serve").start()
    return httpd, httpd.server_address[1], w


def run(directory: Path, port: int, watch: bool = False, check: bool = True, banner: str = "") -> int:
    httpd, port, w = start(directory, port, watch=watch, check=check)
    print(f"Serving {banner or Path(directory).name} review player on "
          f"http://127.0.0.1:{port}/player.html with full Range/seek support...")
    if w:
        print(f"  watching {', '.join(sorted(p.name for p in w.targets()))} "
              f"- open http://127.0.0.1:{port}/player.html?watch=1 to follow the edits"
              + ("" if check else " (determinism check off)"))
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        return 0
    finally:
        if w:
            w.close()
        httpd.shutdown()


def legacy_main(here: Path, default_port: int, banner: str, argv: list[str] | None = None) -> int:
    """The CLI the two projects have always had: `serve_player.py [port] [build dir]`, the dir
    relative to the project. --watch / --no-check ride along."""
    args = list(sys.argv[1:] if argv is None else argv)
    watch = "--watch" in args
    check = "--no-check" not in args
    pos = [a for a in args if not a.startswith("-")]
    port = int(pos[0]) if pos else default_port
    directory = (Path(here) / pos[1]) if len(pos) > 1 else Path(here)
    return run(directory, port, watch=watch, check=check, banner=banner)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="the shared review server, with hot reload (P51 T4)")
    ap.add_argument("build", type=Path, help="the build dir to serve")
    ap.add_argument("--port", type=int, default=8731)
    ap.add_argument("--watch", action="store_true", help="re-compile and push on a shot-table or sidecar edit")
    ap.add_argument("--no-check", action="store_true", help="skip the determinism check after a re-compile")
    a = ap.parse_args(argv)
    return run(a.build, a.port, watch=a.watch, check=not a.no_check, banner=Path(a.build).name)


if __name__ == "__main__":
    raise SystemExit(main())

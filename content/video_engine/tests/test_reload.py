"""P51 T4 - hot reload, and the determinism check that makes it safe to trust.

Four things are proven here, on a split build written the way `build_scene_timeline_f` writes one:

  (a) the shared review server serves a split build and answers `/reload?since=<gen>` at once with
      the generation the client is looking at (the hold is for the generations that have not
      happened yet);
  (b) an edit lands: the sidecar `<build>/overrides.json` and the compiled timeline are both
      watched, a change is a new generation inside a second, and a page opened with `?watch=1`
      re-fetches the timeline and shows the moved box WITHOUT a page load;
  (c) the determinism check on an unchanged build says ok at three instants;
  (d) a deliberate stateful bug - a fixture that caches the dock's top across seeks, injected as a
      tiny <script> into a COPY of the shell and never into the engine - is caught as a warm/cold
      mismatch at the instant, with the two PNGs written beside the build.

The surface is the golden `occluder-dock`: one PLACED dock (place x 620 y 300 w 900 h 560) that
pops at its reading size, parks over 0.7 s from 5.2 s, and then holds - so there is a box to move
and an instant where the box is still moving.
"""
from __future__ import annotations

import json
import shutil
import sys
import time
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as C  # noqa: E402
import determinism_check as DC  # noqa: E402
import render_baseline as RB  # noqa: E402
import serve_player as SP  # noqa: E402

SURFACE = "occluder-dock"
TL_NAME = f"{SURFACE}.timeline.json"
DOCK = "ev-occluded-card"
PARKED, PARKING = 12.0, 5.5     # the box held at its place; the box still sliding into it
ENTER, READING = 4.0, 5.0


def _browser_ok() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="playwright chromium not installed")


def _build(dirpath: Path) -> Path:
    """A split build of the golden surface: player.html + the compiled timeline + assets.json +
    the engine copy + player.json - exactly what a build writes (P51 T1)."""
    tl, uris, _t, _aspect = RB.load_surface(SURFACE)
    dirpath.mkdir(parents=True, exist_ok=True)
    RB.write_split(dirpath, tl, uris, TL_NAME)
    return dirpath


def _timeline(build: Path) -> dict:
    return json.loads((build / TL_NAME).read_text(encoding="utf-8"))


def _write_timeline(build: Path, tl: dict) -> None:
    (build / TL_NAME).write_text(json.dumps(tl, indent=1), encoding="utf-8")


SIDECAR = {f"s01.dock.{DOCK}": {"centre_y": 0.30}}   # the operator's own example key (P51 T5's grammar)


def _moved_dock(tl: dict, dy: float) -> dict:
    """The compiled form of the sidecar's `centre_y`: the resolved `place.y` on the dock entry.

    The page-side test below writes THIS rather than running the sidecar end to end, for one
    reason: a golden surface has no episode behind it (no shot table, no words, no compile block in
    player.json), so there is nothing for `apply_sidecar` to layer over. The sidecar's own grammar
    is proven against the compiler just below, the watcher is proven on the real file, and the
    whole path - sidecar write -> re-compile -> moved box on the page - is measured on the Tokyo
    test bed in the slice's evidence."""
    tl = json.loads(json.dumps(tl))
    for sc in tl["scenes"]:
        for d in sc.get("docks") or []:
            if d.get("slide") == DOCK:
                d["place"]["y"] = d["place"]["y"] + dy
    return tl


def _get(port: int, path: str, timeout: float = 30.0):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
        return r.status, r.headers, r.read()   # the headers object, not a dict: http.server sends `Content-type`


def _reload(port: int, since: int, timeout: float = 30.0) -> dict:
    return json.loads(_get(port, f"/reload?since={since}", timeout)[2].decode("utf-8"))


class _Server:
    def __init__(self, build: Path, watch: bool = True, check: bool = False):
        self.httpd, self.port, self.watch = SP.start(build, 0, watch=watch, check=check, quiet=True)

    def close(self):
        if self.watch:
            self.watch.close()
        self.httpd.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()


def _wait_for_gen(port: int, since: int, deadline_s: float) -> tuple[dict, float]:
    """Poll /reload until the generation moves past `since`; returns the answer and the seconds it
    took. (The long poll does the waiting - this only bounds the test.)"""
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < deadline_s:
        m = _reload(port, since, timeout=deadline_s)
        if m["gen"] > since:
            return m, time.perf_counter() - t0
    raise AssertionError(f"no generation past {since} within {deadline_s} s")


# ---- (a) the server ----------------------------------------------------------------------------------------------

def test_the_shared_server_serves_a_split_build_and_answers_reload_at_once(tmp_path):
    build = _build(tmp_path / "build")
    with _Server(build) as s:
        t0 = time.perf_counter()
        m = _reload(s.port, 0)
        dt = time.perf_counter() - t0
        assert dt < 1.0, f"the current generation must not be held: {dt:.2f}s"
        assert m["gen"] == 1 and m["reload"] is False and m["timeline"] == TL_NAME, m
        assert m["determinism"] == "not run" and m["timeout"] is False, m
        # and the static side is the server the two projects have always had
        status, headers, body = _get(s.port, "/player.html")
        assert status == 200 and headers.get("Cache-Control") == "no-store"
        assert b"watch=1" in body, "the split shell carries the watch client"
        status, headers, _ = _get(s.port, "/" + RB.ENGINE.name)
        assert status == 200 and headers.get_content_type() == "text/javascript", headers.items()


def test_the_sidecar_and_the_shot_table_are_what_is_watched(tmp_path):
    build = _build(tmp_path / "build")
    (build.parent / "SHOT-TABLE-SHORT.py").write_text("W = []\n", encoding="utf-8")
    with _Server(build) as s:
        names = {p.name for p in s.watch.targets()}
        assert names == {TL_NAME, "overrides.json", "SHOT-TABLE-SHORT.py"}, names


# ---- (b) an edit lands -------------------------------------------------------------------------------------------

def test_the_sidecar_this_watcher_watches_is_one_the_compiler_takes():
    """The file the test below writes is not a dead string: `apply_overrides` (P51 T5) takes this
    exact key and field and moves the authored row - which is what a re-compile then compiles."""
    rows = [(0.0, 30.0, "plate-x", (0, 0, 0), [(DOCK, 0, 4.0, 30.0, {"centre": True})], None)]
    out = C.apply_overrides(rows, SIDECAR)
    assert out[0][4][0][4] == {"centre": True, "centre_y": 0.30}, out[0][4]
    assert rows[0][4][0][4] == {"centre": True}, "the authored rows are never mutated"
    with pytest.raises(ValueError, match="names no row"):
        C.apply_overrides(rows, {"s09.dock.x": {"centre_y": 0.1}})


def test_a_sidecar_write_is_a_new_generation_within_a_second(tmp_path):
    """`<build>/overrides.json` is watched, and the write is a generation inside a second. This
    build is a golden surface with no episode behind it, so there is nothing to re-compile and the
    answer says exactly that - `reload` false - instead of re-mounting the page for nothing."""
    build = _build(tmp_path / "build")
    with _Server(build) as s:
        t0 = time.perf_counter()
        (build / "overrides.json").write_text(json.dumps(SIDECAR, indent=1), encoding="utf-8")
        m, _ = _wait_for_gen(s.port, 1, 5.0)
        dt = time.perf_counter() - t0
        assert dt < 1.0, f"the sidecar took {dt:.2f}s to reach a generation"
        assert m["gen"] == 2 and m["reason"] == "overrides.json", m
        assert m["reload"] is False and m["changed"] == [], m


@needs_browser
def test_a_moved_box_reaches_the_watched_page_without_a_page_load(tmp_path):
    from playwright.sync_api import sync_playwright
    build = _build(tmp_path / "build")
    dy = -120.0
    with _Server(build) as s, sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        w, h = RB.STAGE["16:9"]
        page = br.new_context(viewport={"width": w, "height": h}).new_page()
        errs: list[str] = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        # `load`, never `networkidle`: a watched page holds a long poll open for 25 s at a time, so
        # the network is never idle. prepare_page waits for the mount, which is the real ready line.
        page.goto(f"http://127.0.0.1:{s.port}/player.html?watch=1", wait_until="load", timeout=120000)
        RB.prepare_page(page, w, h)
        page.evaluate("t => { const c = document.getElementById('scrub'); c.value = t;"
                      " c.dispatchEvent(new Event('input', {bubbles:true})); }", PARKED)
        read = ("() => { const d = document.querySelector('.dock'); const b = d.getBoundingClientRect();"
                " return [Math.round(b.x), Math.round(b.y), Math.round(b.width)]; }")
        before = page.evaluate(read)
        page.wait_for_function("() => window.__watch && window.__watch.applied >= 1", timeout=30000)

        t0 = time.perf_counter()
        _write_timeline(build, _moved_dock(_timeline(build), dy))
        page.wait_for_function("() => window.__watch && window.__watch.reloads >= 1", timeout=30000)
        after = page.evaluate(read)
        dt = time.perf_counter() - t0

        m = _reload(s.port, 1)
        assert m["reload"] is True and m["reason"] == TL_NAME, m
        assert m["changed"] == [ENTER, 30.0 - 0.01], m["changed"]   # the changed dock's enter and its exit
        assert after[0] == before[0] and after[2] == before[2], (before, after)
        assert after[1] - before[1] == pytest.approx(dy, abs=2), (before, after)
        assert page.evaluate("() => window.__reloads") == 1, "the engine re-mounted exactly once"
        assert page.evaluate("() => +document.getElementById('scrub').value") == PARKED, "the scrub position is kept"
        assert dt < 3.0, f"the edit took {dt:.2f}s to reach the page"
        assert not errs, errs
        br.close()


@needs_browser
def test_the_url_can_name_the_instant_the_page_opens_at(tmp_path):
    """?t=<seconds>: the engine seeks there after mounting, through the scrub's own input event, so
    a report can link the frame it is talking about."""
    from playwright.sync_api import sync_playwright
    build = _build(tmp_path / "build")
    with _Server(build, watch=False) as s, sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        w, h = RB.STAGE["16:9"]
        page = br.new_context(viewport={"width": w, "height": h}).new_page()
        page.goto(f"http://127.0.0.1:{s.port}/player.html?t={PARKED}", wait_until="load", timeout=120000)
        RB.prepare_page(page, w, h)
        assert page.evaluate("() => +document.getElementById('scrub').value") == PARKED
        assert page.evaluate("() => document.getElementById('clock').textContent").startswith("0:12")
        page.goto(f"http://127.0.0.1:{s.port}/player.html", wait_until="load", timeout=120000)
        RB.prepare_page(page, w, h)
        assert page.evaluate("() => +document.getElementById('scrub').value") == 0, "no ?t=, no seek"
        br.close()


# ---- (c) and (d) the determinism check ---------------------------------------------------------------------------

@needs_browser
def test_the_determinism_check_says_ok_on_an_unchanged_build(tmp_path):
    build = _build(tmp_path / "build")
    rep = DC.run(build, [(ENTER + 0.3, "dock enter"), (READING, "reading size"), (PARKED, "parked")],
                 TL_NAME, log=lambda *_a: None)
    assert rep["ok"] and rep["summary"] == "ok" and rep["mismatches"] == 0, rep["summary"]
    assert [r["t"] for r in rep["instants"]] == [ENTER + 0.3, READING, PARKED]
    assert all(r["warm"] == r["cold"] for r in rep["instants"]), rep["instants"]
    assert not (build / DC.OUT_DIR).exists(), "nothing to write when every instant agrees"


CACHING_BUG = """<script>
/* THE FIXTURE'S BUG (test only, never the engine): the dock's top is remembered from the FIRST
   frame this page ever painted and forced on every frame after it, so the card's box becomes a
   function of how the page arrived. The listener is on the bubble phase, so it runs after the
   engine's own scrub handler has laid the frame out. */
window.__cache = {};
document.addEventListener("input", () => {
  const d = document.querySelector(".dock");
  if (!d) return;
  if (window.__cache.top === undefined) window.__cache.top = d.style.top;
  else d.style.top = window.__cache.top;
});
</script>
"""


@needs_browser
def test_a_stateful_bug_is_caught_as_a_warm_cold_mismatch(tmp_path):
    build = _build(tmp_path / "build")
    html = (build / "player.html").read_text(encoding="utf-8")
    anchor = '<script type="module">'
    assert anchor in html, "the split shell's module script is the injection anchor"
    (build / "player.html").write_text(html.replace(anchor, CACHING_BUG + anchor, 1), encoding="utf-8")

    rep = DC.run(build, [(PARKING, "the card mid-park")], TL_NAME, log=lambda *_a: None)
    assert not rep["ok"] and rep["mismatches"] == 1, rep["summary"]
    row = rep["instants"][0]
    assert row["warm"] != row["cold"] and row["known"] is None, row
    assert rep["summary"] == f"mismatch at {PARKING:.2f}", rep["summary"]
    warm, cold = (build / DC.OUT_DIR / f"{PARKING:.2f}-warm.png"), (build / DC.OUT_DIR / f"{PARKING:.2f}-cold.png")
    assert warm.exists() and cold.exists() and warm.read_bytes() != cold.read_bytes()


# ---- the diff that names the instants ----------------------------------------------------------------------------

def test_the_diff_names_the_instants_a_change_touched(tmp_path):
    build = _build(tmp_path / "build")
    tl = _timeline(build)
    assert DC.changed_instants(tl, tl) == [], "an unchanged timeline touches no instant"
    moved = _moved_dock(tl, -120.0)
    assert DC.changed_instants(tl, moved) == [(ENTER, f"s01 dock {DOCK} enter"), (29.99, f"s01 dock {DOCK} exit")]
    grown = json.loads(json.dumps(tl))
    grown["scenes"][0]["species"] = [{"kind": "callout", "at": 9.0, "dur": 1.5}]
    assert DC.changed_instants(tl, grown) == [(9.0, "s01 species callout"), (10.5, "s01 species callout")]
    flagged = dict(tl, kinetics={"idle": True})
    assert DC.changed_instants(tl, flagged) == [(0.0, "s01 kinetics changed")]


def test_the_known_class_is_named_not_hidden():
    """R26-21: a cold seek into the 0.45 s snap window reads the page full for one frame. The check
    must call that mismatch by its name - and only inside the window it belongs to."""
    tl = {"runtime_s": 20.0, "scenes": [
        {"scene_id": "s01", "span": [0.0, 10.0], "world": {"page": {"enter": "snap", "snap_from": "ev-a"}}},
        {"scene_id": "s02", "span": [10.0, 20.0], "world": {"page": {"enter": "mount"}}}]}
    assert DC.snap_windows(tl) == [(0.0, DC.SNAP_S, "s01")]
    assert "KNOWN R26-21" in (DC.known_class(0.2, DC.snap_windows(tl)) or "")
    assert DC.known_class(0.6, DC.snap_windows(tl)) is None
    assert DC.known_class(10.2, DC.snap_windows(tl)) is None

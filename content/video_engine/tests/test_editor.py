"""P51 T7 - the editor, thin: a CLIENT of a served build that writes the sidecar and nothing else.

Five things are proven here, on a PRIVATE copy of Tokyo's side build (`build-short-t7`, or
`build-short-t0` read-only if that is all there is - never `build-short`, the approved cut):

  (a) the page is served on the BUILD's origin from the scripts tree (`GET /editor.html` is the file
      on disk, byte for byte) and it loads over the served build: the seven scenes and s04's two
      docks are listed, with the shipped player.html mounted in the frame;
  (b) a POST of the operator's own example key writes `<build>/overrides.json` and the next
      `/reload` reports the instants the change touched - the dock's enter among them - and the
      re-compiled timeline carries the moved box;
  (c) a bad value is REFUSED with the row and the field named, and the sidecar is not written;
  (d) a drag on the overlay moves the GHOST ONLY - the player's own dock box does not move while
      the hand does - and the release writes the stage-share centre the drop point means;
  (e) the two nulls: a null takes a line back, `?literal=1` writes the null the camera's OFF is.

The build is restored after every test that writes: the sidecar deleted and the compiler re-run
through the same `compile` block the server re-compiles with. Nothing outside the copy is touched -
the fixture asserts the episode's own shot table came out byte-identical.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import serve_player as SP  # noqa: E402

EPISODE = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
# The SIDE build, never `build-short` (the approved cut). `build-short-t7` is this slice's private
# copy of it; `build-short-t0` is the fallback and is only ever READ (it is another lane's bench).
SOURCES = [EPISODE / "build-short-t7", EPISODE / "build-short-t0"]
TABLE = EPISODE / "SHOT-TABLE-SHORT.py"
EDITOR = ROOT / "content/video_engine/editor/editor.html"
TL_NAME = "tokyo-short.timeline.json"
DOCK = "dock-k-pledge-record"                # s04's record card: centred, so a drag binds
DOCK_KEY = f"s04.dock.{DOCK}"
AT = 57.0                                    # both s04 cards on the page, the camera at its landing
HEAVY = {"determinism", "self-watch"}        # a test's copy needs the build, not its reports


def _source() -> Path | None:
    return next((p for p in SOURCES if (p / "player.json").is_file()), None)


def _repointed(text: str, build: Path) -> str:
    """Every clip path a shot table names, re-pointed into `build`. A table names its clips by
    absolute path into whichever build dir wrote them, so a copy that kept them would read another
    lane's build - and on a busy episode that build is being rewritten while this test runs."""
    for sep, dst in (("/", str(build).replace("\\", "/")), ("\\\\", str(build).replace("\\", "\\\\"))):
        text = re.sub(rf"[A-Za-z]:{sep}(?:[^'\"]*?{sep})?tokyo-tea-break{sep}build-short[^{sep}'\"]*{sep}",
                      dst + sep, text)
    return text


needs_tokyo = pytest.mark.skipif(_source() is None,
                                 reason="no Tokyo side build (build-short-t7 / build-short-t0) on disk")


def _browser_ok() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="playwright chromium not installed")


# ---- the served copy ----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def served(tmp_path_factory):
    """A PRIVATE copy of the side build, served with --watch, that re-compiles onto itself alone.

    Three re-pointings in the copy's own `player.json` compile block make it private - the same
    three the slice's `build-short-t7` carries, and they are the point: a re-compile rewrites the
    shot table with the effective rows (P51 T5), so a test that named the episode's own table would
    edit the table another agent is holding.
      - `episode_dir` absolute, so the build can live outside the episode tree (tmp_path);
      - `shot_table_file` a COPY of the table, beside it, deleted with the fixture, with the clip
        paths it names (absolute, into whichever build wrote them) re-pointed into this copy;
      - `stamped`'s four dock/clip assets re-pointed into this copy."""
    source = _source()
    if source is None:
        pytest.skip("no Tokyo side build on disk")
    build = tmp_path_factory.mktemp("editor-build") / "build"
    build.mkdir(parents=True)
    for p in source.iterdir():
        if p.name in HEAVY:
            continue
        (shutil.copytree if p.is_dir() else shutil.copyfile)(p, build / p.name)
    table = EPISODE / "SHOT-TABLE-SHORT.t7test.py"
    table.write_text(_repointed(TABLE.read_text(encoding="utf-8"), build), encoding="utf-8")
    manifest = build / "player.json"
    m = json.loads(manifest.read_text(encoding="utf-8"))
    c = m["compile"]
    c["episode_dir"] = str(EPISODE)
    c["shot_table_file"] = table.name
    c["stamped"] = {k: v.replace(str(source), str(build)).replace(str(source).replace("\\", "/"), str(build))
                    for k, v in c["stamped"].items()}
    manifest.write_text(json.dumps(m, indent=1), encoding="utf-8")
    table_before = TABLE.read_bytes()
    httpd, port, watch = SP.start(build, 0, watch=True, check=False, quiet=True)
    try:
        yield build, port, watch
    finally:
        watch.close()
        httpd.shutdown()
        assert TABLE.read_bytes() == table_before, "the episode's own shot table was written to"
        table.unlink(missing_ok=True)
        shutil.rmtree(build, ignore_errors=True)


def _restore(build: Path, watch) -> None:
    """The build as it was: the sidecar gone and the compiler re-run the way the server runs it."""
    (build / SP.OVERRIDES_NAME).unlink(missing_ok=True)
    ok, err, _ms = watch.recompile()
    assert ok, err


def _get(port: int, path: str, timeout: float = 60.0):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
        return r.status, r.read()


def _reload(port: int, since: int) -> dict:
    return json.loads(_get(port, f"/reload?since={since}")[1].decode("utf-8"))


def _post(port: int, body: dict, literal: bool = False) -> tuple[int, dict]:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/overrides" + ("?literal=1" if literal else ""),
        data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def _timeline(build: Path) -> dict:
    return json.loads((build / TL_NAME).read_text(encoding="utf-8"))


def _dock(build: Path, slide: str = DOCK) -> dict:
    for sc in _timeline(build)["scenes"]:
        for d in sc.get("docks") or []:
            if d.get("slide") == slide:
                return d
    raise AssertionError(f"no dock {slide} in the compiled timeline")


def _wait_reload(port: int, since: int, deadline_s: float = 40.0) -> dict:
    end = time.time() + deadline_s
    while time.time() < end:
        m = _reload(port, since)
        if m["gen"] > since and m.get("reload"):
            return m
        if m["gen"] > since:
            since = m["gen"]        # a generation that only carries a verdict: keep waiting
    raise AssertionError("no reload generation inside the deadline")


# ---- (a) the page -------------------------------------------------------------------------------

@needs_tokyo
def test_editor_is_served_from_the_scripts_tree_not_the_build(served):
    build, port, _watch = served
    status, body = _get(port, "/editor.html")
    assert status == 200
    assert body == EDITOR.read_bytes()                      # the file on disk, never a copy in the build
    assert not (build / "editor.html").exists()             # a build stays data only


@needs_tokyo
@needs_browser
def test_the_editor_lists_the_scenes_and_the_docks_over_the_served_build(served):
    from playwright.sync_api import sync_playwright
    build, port, _watch = served
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        page = br.new_page(viewport={"width": 1600, "height": 1000})
        page.goto(f"http://127.0.0.1:{port}/editor.html")
        page.wait_for_function("window.__editorReady === true", timeout=120000)
        chips = page.locator("#scenes .chip").all_text_contents()
        assert len(chips) == len(_timeline(build)["scenes"]) == 7
        assert chips[0].startswith("s01") and "clip" in chips[0]
        assert any(c.startswith("s04") and "ledger" in c for c in chips)

        page.locator("#scenes .chip", has_text="s04").first.click()
        docks = page.locator("#docks").inner_text()
        assert DOCK in docks and "dock-i-fab-wafer" in docks
        species = page.locator("#species").inner_text()
        assert "bracket" in species and "retitle" in species
        assert page.locator(f'.ghost[data-slide="{DOCK}"]').count() == 1

        frame = page.frame_locator("#player")                # the SHIPPED player, mounted, in the frame
        page.wait_for_function("(() => { const f = document.getElementById('player');"
                               " return f.contentWindow && f.contentWindow.__mounted === true; })()",
                               timeout=120000)
        page.evaluate("t => seek(t)", AT)
        assert frame.locator("#stage").count() == 1
        br.close()


# ---- (b) the write ------------------------------------------------------------------------------

@needs_tokyo
def test_a_post_writes_the_sidecar_and_the_next_reload_reports_the_instant(served):
    build, port, watch = served
    try:
        before = _dock(build)["place"]["y"]
        gen = _reload(port, 0)["gen"]
        status, m = _post(port, {DOCK_KEY: {"centre_y": 0.30}})
        assert status == 200 and m["ok"], m
        assert json.loads((build / SP.OVERRIDES_NAME).read_text(encoding="utf-8")) == {DOCK_KEY: {"centre_y": 0.30}}

        answer = _wait_reload(port, gen)
        assert answer["reason"] == SP.OVERRIDES_NAME
        assert 55.31 in answer["changed"], answer["changed"]   # the record's enter: the instant it touches
        assert any(DOCK in w for w in answer["why"]), answer["why"]

        d = _dock(build)
        assert d["place"]["y"] != before
        assert abs((d["place"]["y"] + d["place"]["h"] / 2) / 1920 - 0.30) < 0.002   # the share, as compiled
    finally:
        _restore(build, watch)


@needs_tokyo
def test_a_bad_value_is_refused_with_the_row_and_the_field_named_and_nothing_is_written(served):
    build, port, _watch = served
    sidecar = build / SP.OVERRIDES_NAME
    assert not sidecar.exists()
    status, m = _post(port, {DOCK_KEY: {"centre_y": 9.0}})
    assert status == 400 and m["ok"] is False
    assert DOCK_KEY in m["error"] and "centre_y" in m["error"]
    assert not sidecar.exists()                               # refused is NOT written

    status, m = _post(port, {"s09.dock.nope": {"centre_y": 0.3}})
    assert status == 400 and "s09" in m["error"] and "s01..s07" in m["error"]
    assert not sidecar.exists()


@needs_tokyo
def test_a_null_takes_a_line_back_and_literal_writes_the_camera_off(served):
    build, port, watch = served
    sidecar = build / SP.OVERRIDES_NAME
    try:
        status, m = _post(port, {"s06.camera": None}, literal=True)     # the OFF state that IS a null
        assert status == 200 and m["overrides"] == {"s06.camera": None}
        assert json.loads(sidecar.read_text(encoding="utf-8")) == {"s06.camera": None}

        status, m = _post(port, {"s06.camera": None})                   # the same value, taken back
        assert status == 200 and m["overrides"] == {}
        assert not sidecar.exists()
    finally:
        _restore(build, watch)


# ---- (d) the ghost ------------------------------------------------------------------------------

@needs_tokyo
@needs_browser
def test_a_drag_moves_the_ghost_only_and_the_release_writes_the_stage_share(served):
    from playwright.sync_api import sync_playwright
    build, port, watch = served
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            page = br.new_page(viewport={"width": 1600, "height": 1000})
            page.goto(f"http://127.0.0.1:{port}/editor.html")
            page.wait_for_function("window.__editorReady === true", timeout=120000)
            page.wait_for_function("(() => { const f = document.getElementById('player');"
                                   " return f.contentWindow && f.contentWindow.__mounted === true; })()",
                                   timeout=120000)
            page.locator("#scenes .chip", has_text="s04").first.click()
            page.evaluate("t => seek(t)", AT)
            page.wait_for_timeout(300)

            read_card = ("() => { const d = document.getElementById('player').contentDocument"
                         f".querySelector('.dock[data-slide=\"{DOCK}\"]');"
                         " if (!d) return null; const r = d.getBoundingClientRect();"
                         " return [r.x, r.y, r.width, r.height]; }")
            card_before = page.evaluate(read_card)
            assert card_before, "the record card is not on the stage at 57.0"

            place = _dock(build)["place"]                         # the box the drag starts from
            ghost = page.locator(f'.ghost[data-slide="{DOCK}"]')
            box = ghost.bounding_box()
            k = page.evaluate("() => { const f = document.getElementById('player');"
                              " const r = f.contentDocument.getElementById('stage').getBoundingClientRect();"
                              " return r.width / 1080; }")
            dy = 90.0                                            # the hand, in editor px
            page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            page.mouse.down()
            page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2 + dy, steps=6)
            page.wait_for_timeout(120)

            moved = ghost.bounding_box()                          # the GHOST followed the hand
            assert abs(moved["y"] - box["y"] - dy) < 4, (box, moved)
            assert page.evaluate(read_card) == card_before        # ... and the FRAME did not

            gen = _reload(port, 0)["gen"]
            page.mouse.up()
            page.wait_for_function("() => !document.querySelector('.ghost.dragging')", timeout=30000)
            page.wait_for_timeout(400)

            written = json.loads((build / SP.OVERRIDES_NAME).read_text(encoding="utf-8"))
            assert set(written) == {DOCK_KEY}
            expect_y = (place["y"] + dy / k + place["h"] / 2) / 1920
            assert abs(written[DOCK_KEY]["centre_y"] - expect_y) < 0.004, (written, expect_y)
            assert abs(written[DOCK_KEY]["centre_x"] - (place["x"] + place["w"] / 2) / 1080) < 0.004

            answer = _wait_reload(port, gen)                      # the REAL frame arrives by the T4 loop
            assert answer["reload"] and any(DOCK in w for w in answer["why"])
            br.close()
    finally:
        _restore(build, watch)

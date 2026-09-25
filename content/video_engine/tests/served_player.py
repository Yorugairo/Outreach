"""The ONE guarded way a test starts Playwright (R26-351, P72 T9; the pattern P72 T2 gave `test_chart_transitions`).

R26-145 found the leak and R26-351 found it in 38 more files: a helper that runs `sync_playwright().start()` and
stops the driver only in the `close()` it RETURNS leaves the driver's event loop running whenever the setup between
the two raises (a launch, a `goto`, a `prepare_page` that times out). Every later `sync_playwright()` in the same
pytest process then fails with "It looks like you are using Playwright Sync API inside the asyncio loop", so one
failure reads as a cascade of unrelated ones. Here the setup that raises closes what it opened and re-raises, and a
close runs every step even when an earlier one raises - the driver is always stopped.

    page, errs, close = open_served(html, w, h, cleanup=td.cleanup)   # a helper that hands back its close
    with served(html, w, h) as (page, errs): ...                      # a block that closes itself
    with browser() as br: ...                                         # a browser shared by several pages
    pw, br = launch()                                                 # a class that keeps the pair itself
    close = closer(pw, br, srv.shutdown, td.cleanup)                  # ... and the close it owes

Test code only: nothing under `scripts/` imports it.
"""
from __future__ import annotations

import contextlib
import sys
from pathlib import Path
from typing import Callable

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

Step = Callable[[], object] | None


def run_all(*steps: Step) -> None:
    """Run every step in order; a step that raises never skips the ones after it. The first error is re-raised."""
    first: BaseException | None = None
    for step in steps:
        if step is None:
            continue
        try:
            step()
        except BaseException as e:  # noqa: BLE001 - re-raised below, after the remaining steps have run
            if first is None:
                first = e
    if first is not None:
        raise first


def launch(headless: bool = True):
    """(driver, browser): Playwright started and Chromium launched. A launch that raises stops the driver first."""
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    try:
        return pw, pw.chromium.launch(headless=headless)
    except BaseException:
        with contextlib.suppress(Exception):
            pw.stop()
        raise


def closer(pw, br, *more: Step) -> Callable[[], None]:
    """The close a launched pair owes: the browser, then ALWAYS the driver, then each of `more` (a server's
    shutdown, a temp dir's cleanup), every step run even when one before it raises."""
    return lambda: run_all(br.close if br is not None else None, pw.stop if pw is not None else None, *more)


@contextlib.contextmanager
def browser(headless: bool = True):
    """One browser for a block of pages; the driver is stopped however the block ends."""
    pw, br = launch(headless)
    try:
        yield br
    finally:
        closer(pw, br)()


def open_served(html: Path, w: int, h: int, *, cleanup: Step = None, prepare: bool = True):
    """Serve `html`'s directory, open `html` at w x h in a fresh driver, make it a pure function of t
    (`render_baseline.prepare_page`) unless `prepare=False`, and return (page, errs, close).

    `errs` collects the page's uncaught errors. `close()` closes the browser, stops the driver, shuts the server
    down and runs `cleanup`. A setup that raises runs the same close before it re-raises, so no failure leaves
    Playwright's loop running for the next test."""
    import render_baseline as RB
    srv, port = RB.serve(html.parent)
    pw = br = None

    def close() -> None:
        run_all(br.close if br is not None else None, pw.stop if pw is not None else None, srv.shutdown, cleanup)

    try:
        pw, br = launch()
        page = br.new_context(viewport={"width": w, "height": h}).new_page()
        errs: list[str] = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
        if prepare:
            RB.prepare_page(page, w, h)
    except BaseException:
        with contextlib.suppress(Exception):
            close()
        raise
    return page, errs, close


@contextlib.contextmanager
def served(html: Path, w: int, h: int, *, cleanup: Step = None, prepare: bool = True):
    """`open_served` as a block: yields (page, errs) and closes however the block ends."""
    page, errs, close = open_served(html, w, h, cleanup=cleanup, prepare=prepare)
    try:
        yield page, errs
    finally:
        close()

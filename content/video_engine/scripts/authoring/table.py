"""The authoring kit - TABLE: the rows as data, and the hand-off to the compiler.

A row is a TUPLE and stays one - it is the compiled form the compiler, the gates and the lint all
read:

    (start, end, plate_id, ken_burns, [docks], exit[, species[, camera]])

The kit writes that literal out, prints it for the operator, resolves the held-light rule, and
hands the build to `build_scene_timeline_f`. It never authors a row.
"""
from __future__ import annotations

import json
from pathlib import Path

ROW_SPECIES = 6      # the row's 7th element: the species list
SHOT_TABLE_VAR = "W"
OVERRIDES_NAME = "overrides.json"   # P51 T5: the edit sidecar, beside the build it belongs to


def at(ws: list[dict], phrase: str) -> float:
    """A row anchor read off the take - `words.at`, re-exported so a shot table needs one import."""
    from . import words as W
    return W.at(ws, phrase)


def write_shot_table(path: Path, rows: list[tuple], header: str) -> Path:
    """The authored rows as a python literal the compiler loads. `header` is the whole prefix the
    episode wants above it (its docstring, and anything else that identifies the build)."""
    path.write_text(header + f"{SHOT_TABLE_VAR} = " + repr(rows).replace("), (", "),\n     (") + "\n", encoding="utf-8")
    return path


def load_rows(path: Path) -> list[tuple]:
    """The rows back out of a written shot table - the compiler loads the file the same way."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("shot_rows", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(getattr(mod, SHOT_TABLE_VAR))


def apply_sidecar(ep: Path, build: Path, shot_table_file: str) -> list[str]:
    """P51 T5: `<build>/overrides.json` layered over the AUTHORED table before the compiler reads it.

    A human's or a flash agent's edit lands in the sidecar, keyed by row id and field
    (`build_scene_timeline_f.apply_overrides` is the grammar and the refusals); the table stays the
    agent's. The literal is REWRITTEN here with the effective rows - so `SHOT-TABLE-SHORT.py` shows
    what was compiled and the compiled timeline matches it - which makes the compiler's own pass
    over the same sidecar a no-op (the layering is idempotent). Returns the ids layered on; `[]`
    when there is no sidecar, and then nothing at all is read, written or changed."""
    path = Path(build) / OVERRIDES_NAME
    if not path.is_file():
        return []
    import build_scene_timeline_f as C
    overrides = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(overrides, dict):
        raise SystemExit(f"FAIL: {path}: the sidecar is a JSON object keyed by row id and field")
    table = Path(ep) / shot_table_file
    header, sep, _ = table.read_text(encoding="utf-8").partition(f"{SHOT_TABLE_VAR} = ")
    if not sep:
        raise SystemExit(f"FAIL: {table}: no `{SHOT_TABLE_VAR} = ` - a sidecar layers over a table this kit wrote")
    words_path = Path(build) / "timeline.json"
    words = json.loads(words_path.read_text(encoding="utf-8")).get("words") if words_path.is_file() else None
    try:
        rows = C.apply_overrides(load_rows(table), overrides, words=words, aspect=C.ASPECT)
    except ValueError as exc:
        raise SystemExit(f"FAIL: {path.name}: {exc}") from None
    write_shot_table(table, rows, header)
    return sorted(overrides)


def row_line(row, show_docks: bool = False) -> str:
    """One printed row: the window, the world, and what fires on it."""
    plate = row[2]
    name = plate.split("/")[-1] if plate.startswith("clip:") else plate
    docks = row[4] if len(row) > 4 else None
    species = row[ROW_SPECIES] if len(row) > ROW_SPECIES else None
    extra = (f"  docks {[d[0] for d in docks]}" if show_docks and docks else "")
    extra += (f"  species {[s['kind'] for s in species]}" if species else "")
    return f"  {row[0]:6.2f}-{row[1]:6.2f}  {name}{extra}"


def print_rows(rows: list[tuple], show_docks: bool = False) -> None:
    for r in rows:
        print(row_line(r, show_docks))


def hold_until(rows: list[tuple], ws: list[dict]) -> list[tuple]:
    """E25: a held light follows its SENTENCE. Every ``dur: "hold"`` species gets `until` = the
    first word of the next sentence (from the take's punctuation), unless the row already names
    one; the compiler then takes the earliest of that, the next event on the row, a card arriving,
    and the cut. The rows are mutated in place and given back."""
    from . import words as W
    for r in rows:
        for e in (r[ROW_SPECIES] or []) if len(r) > ROW_SPECIES else []:
            if isinstance(e, dict) and e.get("dur") == "hold" and "until" not in e:
                u = W.next_sentence_start(ws, float(e["at"]))
                if u is not None:
                    e["until"] = u
    return rows


def caption_pages(build: Path, char_budget: int, max_words: int) -> None:
    """The caption pages for the build. A page holds a phrase on TWO lines at most: the budget is
    measured off the stage's own type size, never guessed."""
    import build_caption_pages as CP
    CP.BUILD = build
    CP.CHAR_BUDGET, CP.MAX_WORDS = char_budget, max_words
    CP.main()


def compile_timeline(ep: Path, build: Path, *, timeline_name: str, shot_table_file: str,
                     title: str, subtitle: str, episode_id: str, aspect: str,
                     caption_style: str | None, kinetics: dict, render: bool = False) -> int:
    """Stage 6-8's hand-off: point the compiler at this episode's build and run it. `render` also
    points the render door at the same pair (a build whose assets are resolved by id)."""
    import build_scene_timeline_f as C
    if render:
        import build_render_f as R
        R.EP, R.BUILD = ep, build
    C.EP, C.BUILD = ep, build
    C.TIMELINE_NAME = timeline_name
    C.SHOT_TABLE_FILE = shot_table_file
    C.TITLE, C.SUBTITLE, C.EPISODE_ID = title, subtitle, episode_id
    C.ASPECT = aspect
    C.CAPTION_STYLE = caption_style
    C.KINETICS = dict(kinetics)
    apply_sidecar(ep, build, shot_table_file)   # P51 T5: the edit sidecar, over the literal, before the compiler reads it
    rc = C.main()
    if rc == 0:
        write_compile_manifest(ep, build, timeline_name=timeline_name, shot_table_file=shot_table_file,
                               title=title, subtitle=subtitle, episode_id=episode_id, aspect=aspect,
                               caption_style=caption_style, kinetics=dict(kinetics), render=render)
    return rc


MANIFEST_NAME = "player.json"   # written by render_baseline.write_split; this adds the compile block


def write_compile_manifest(ep: Path, build: Path, **fields) -> Path:
    """P51 T4: the re-compile, recorded by the only door that compiles.

    `serve_player --watch` re-runs the compiler in-process when the shot table or the sidecar
    moves; it reads THIS block instead of guessing an episode's facts. Written after a green
    compile, beside the engine's sha in the same manifest, with the episode dir relative to the
    build (a build folder stays movable).

    `stamped` is the other half of what a re-compile needs and the half that is easy to miss: the
    episode's own dock assets are registered with the render resolver IN MEMORY while the rows are
    authored (`docks.register` -> `build_render_f.STAMPED`), so a compiler run in a process that
    never ran the build script cannot find one. Recorded here, the server restores it."""
    import json
    import os
    import build_render_f as R
    p = Path(build) / MANIFEST_NAME
    m = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    m["compile"] = {"episode_dir": os.path.relpath(Path(ep), Path(build)).replace("\\", "/"),
                    "stamped": {k: str(v) for k, v in sorted(R.STAMPED.items())}, **fields}
    p.write_text(json.dumps(m, indent=1), encoding="utf-8")
    return p

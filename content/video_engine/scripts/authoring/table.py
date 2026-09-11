"""The authoring kit - TABLE: the rows as data, and the hand-off to the compiler.

A row is a TUPLE and stays one - it is the compiled form the compiler, the gates and the lint all
read:

    (start, end, plate_id, ken_burns, [docks], exit[, species[, camera]])

The kit writes that literal out, prints it for the operator, resolves the held-light rule, and
hands the build to `build_scene_timeline_f`. It never authors a row.
"""
from __future__ import annotations

from pathlib import Path

ROW_SPECIES = 6      # the row's 7th element: the species list
SHOT_TABLE_VAR = "W"


def at(ws: list[dict], phrase: str) -> float:
    """A row anchor read off the take - `words.at`, re-exported so a shot table needs one import."""
    from . import words as W
    return W.at(ws, phrase)


def write_shot_table(path: Path, rows: list[tuple], header: str) -> Path:
    """The authored rows as a python literal the compiler loads. `header` is the whole prefix the
    episode wants above it (its docstring, and anything else that identifies the build)."""
    path.write_text(header + f"{SHOT_TABLE_VAR} = " + repr(rows).replace("), (", "),\n     (") + "\n", encoding="utf-8")
    return path


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
    return C.main()

"""The authoring kit - TABLE: the rows as data, and the hand-off to the compiler.

A row is a TUPLE and stays one - it is the compiled form the compiler, the gates and the lint all
read:

    (start, end, plate_id, ken_burns, [docks], exit[, species[, camera]])

The kit writes that literal out, prints it for the operator, resolves the held-light rule, and
hands the build to `build_scene_timeline_f`. It never authors a row.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROW_SPECIES = 6      # the row's 7th element: the species list
ROW_KEN = 3          # the row's 4th element: the ken-burns push (scale, dx, dy)
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


def life_tokens(rows: list[tuple]) -> list[tuple[int, str]]:
    """R26-245 (E49, E99 s84): which rows carry LIFE - and by WHAT, never a bare count.

    A row's life is either the painted idle it names in its world options (`;idle=live` on a page,
    `;idle=drift` on a plate) or its KEN PUSH. Under E99 s84 the ken is the WHOLE of a long-form
    plate's life - the operator withdrew the painted drift ("the drift is too random, i think we
    should use ken burns instead of drift"), so a plate row now carries `;use=landing`, a ken tuple
    and no `;idle=` token at all. A counter that reads only the `;idle=` token therefore reads a
    Ken-Burns plate as still and contradicts E49 on a row that is correct.

    Returns (1-based row number, what carries it) for every row that carries any. A ken of all
    zeros is no push and no life; the gate's own M18 reads this from the rendered frames instead
    (`gate_motion_density._frozen_gate`) and needs no change - a ken moves pixels.
    """
    out: list[tuple[int, str]] = []
    for i, r in enumerate(rows):
        carries: list[str] = []
        opts = str(r[2]).partition(";")[2]
        for tok in opts.split(";"):
            if tok.startswith("idle="):
                carries.append(tok)
        ken = r[ROW_KEN] if len(r) > ROW_KEN else None
        try:
            pushes = any(float(v) for v in (ken or ()))
        except (TypeError, ValueError):
            pushes = False
        if pushes:
            carries.append("ken " + "/".join("%g" % float(v) for v in ken))
        if carries:
            out.append((i + 1, " + ".join(carries)))
    return out


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
                     caption_style: str | None, kinetics: dict, render: bool = False,
                     no_receipt: str | None = None) -> int:
    """Stage 6-8's hand-off: point the compiler at this episode's build and run it. `render` also
    points the render door at the same pair (a build whose assets are resolved by id).

    P67 T2: the receipt is decided BEFORE the compiler is touched - a first compile without a
    passing `## Recall` block (and without a named `no_receipt` reason) raises and writes nothing."""
    receipt = recall_receipt_block(ep, build, no_receipt)
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
                               caption_style=caption_style, kinetics=dict(kinetics), render=render,
                               **{RECEIPT_KEY: receipt})
    return rc


MANIFEST_NAME = "player.json"   # written by render_baseline.write_split; this adds the compile block
RECEIPT_KEY = "recall_receipt"            # P67 T2: which receipt this cut compiled under, kept in the manifest
LEGACY_REASON = "legacy build (pre-P67)"  # a build dir that first compiled before the door existed


def _manifest_receipt(build: Path) -> tuple[bool, dict | None]:
    """Has this build dir compiled before, and under which receipt? -> (a compile block exists, its receipt block)."""
    path = Path(build) / MANIFEST_NAME
    if not path.is_file():
        return False, None
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True, None
    block = manifest.get("compile") if isinstance(manifest, dict) else None
    if not isinstance(block, dict):
        # the manifest exists but no compile has written it (render_baseline writes player.json first): the FIRST
        # compile is still ahead, so the door runs - "compiled before" means the compile block, not the file
        return False, None
    carried = block.get(RECEIPT_KEY)
    return True, carried if isinstance(carried, dict) else None


def recall_receipt_block(ep: Path, build: Path, no_receipt: str | None = None) -> dict:
    """THE COMPILE DOOR (P67 T2): the receipt block this compile goes in under - or SystemExit, and no timeline.

    The door binds the FIRST compile of a build dir only, because `serve_player --watch` and
    `change_report.py` re-compile EXISTING builds and must keep working:

      * a manifest that already carries a receipt -> that block, unchanged (the recompile is the same cut);
      * a manifest with no receipt (every build made before P67) -> `legacy build (pre-P67)`, stamped;
      * no manifest at all -> the first compile, and the door runs.

    On that first compile the project's `## Recall` block is re-read off disk line by line
    (`recall_verify.verify`) - citation is not grounding (arXiv 2606.04990) - and a refusal stops the
    build with the verifier's text VERBATIM. The escape is a NAMED reason, never a silent flag: it is
    written into the manifest word for word and stays with the cut for the rest of its life."""
    seen, carried = _manifest_receipt(build)
    if seen:
        return dict(carried) if carried is not None else {"skipped_reason": LEGACY_REASON}
    if no_receipt is not None:
        if not isinstance(no_receipt, str) or not no_receipt.strip():
            raise SystemExit(f"FAIL: no_receipt={no_receipt!r} is not a reason - the escape is a NAMED reason "
                             "(a non-empty string, e.g. \"recipe lab candidate 12\"), written verbatim into "
                             "the compile manifest")
        return {"skipped_reason": no_receipt}
    import recall_verify as RV
    ok, lines = RV.verify(RV.REPO, Path(ep))
    if not ok:
        raise SystemExit("\n".join(lines))
    ledger = RV.resolve_ledger(Path(ep))
    block = RV.parse_block(ledger.read_text(encoding="utf-8", errors="replace"))
    return {"ledger": os.path.relpath(ledger, Path(build)).replace("\\", "/"),
            "sha256": block.sha256(),
            "stages": block.stage_counts(),
            "verdict": "pass",
            "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


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

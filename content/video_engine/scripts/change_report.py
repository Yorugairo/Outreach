"""THE CHANGE REPORT - what a human or a flash agent changed, as the agent sees it (P51 T6).

The grill ledger, 2026-09-11: "the agent sees a change as the diff line, the two frames at the
affected instant and the gate delta". A hand edit lands in the sidecar (`<build>/overrides.json`,
P51 T5); the agent that is summoned afterwards must not have to guess what moved, re-derive it
from a screenshot, or re-render the episode to find out. It reads ONE file:

    python change_report.py <build>                             # the build as it stands vs the authored rows
    python change_report.py <build> --against <overrides.json>   # ... vs the build compiled with THAT sidecar
    python change_report.py <build> --before <old>.timeline.json # ... vs an old compiled timeline
    python change_report.py <build> --since <git sha>            # ... vs the compiled timeline at that sha

    -> <build>/CHANGE-REPORT.md  and  <build>/change-report/ (the crops)

The BEFORE build is produced, never guessed:

  default / --against   the build COPIED to a temp dir and re-compiled in process through
                        `player.json`'s `compile` block - the same door `serve_player --watch`
                        uses - with no sidecar (default) or with the named one. The copy is what
                        is compiled: the build on disk is never written, and the episode's shot
                        table is never rewritten (`authoring.table.apply_sidecar` is held off for
                        the run; the compiler's own sidecar pass does the layering instead).
  --before / --since    the build copied and the old compiled timeline dropped into the copy (with
                        --since it is read with `git show <sha>:<path>` - the only git this file
                        runs, and it is read-only).

The AFTER is the build as it stands. Nothing else is re-implemented: the instants come from the
determinism check's own timeline diff (P51 T4), the boxes and the frames from the probe (P51 T2),
the rows from the motion gate (M01-M26), the verdict at those instants from `determinism_check`.

The report is a pure function of its inputs - the same build, the same sidecar, the same report
text - except the date in the header. Exit 0 always (a gate FAIL on the after build is STATED, not
an exit code); 2 for a usage error.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import build_scene_timeline_f as C  # noqa: E402
import determinism_check as DC  # noqa: E402
import gate_motion_density as G  # noqa: E402
import probe as P  # noqa: E402
import serve_player as SP  # noqa: E402

REPORT_NAME = "CHANGE-REPORT.md"
CROP_DIR = "change-report"          # <build>/change-report/<key>-<t>-before.png, -after.png, -pair.png
OVERRIDES_NAME = "overrides.json"
CROP_PAD = 0.10                     # the changed element's box, padded by 10 % on every side
MAX_CROPS = 12                      # crops are frames: bounded, and spread over the keys (round robin)
CHECK_MAX = 6                       # instants the determinism check renders warm and cold
SKIP_DIRS = ("determinism", CROP_DIR, "self-watch", "frames", "__pycache__")
KIND_ORDER = {"dock": 0, "species": 1, "plate": 2, "exit": 3, "camera": 4}
UNSET = "(unset)"


# ---- the keys ----------------------------------------------------------------------------------------------------

def split_key(key: str) -> tuple[str, str, str]:
    """`s04.dock.dock-k-pledge-record.centre_y` -> (`s04`, `dock`, `dock-k-pledge-record.centre_y`)."""
    scene, _, rest = str(key).partition(".")
    kind, _, sel = rest.partition(".")
    return scene, kind, sel


def row_key(leaf: str) -> str:
    """The SIDECAR key a leaf field belongs to (`s04.dock.<slide>.centre_y` -> `s04.dock.<slide>`)."""
    scene, kind, sel = split_key(leaf)
    if kind in ("dock", "species"):
        return f"{scene}.{kind}.{sel.partition('.')[0]}"
    return f"{scene}.{kind}"


def key_order(leaf: str) -> tuple:
    """Row order: the scene as the compiler numbers it, then dock / species / plate / exit / camera,
    then the dock's slide or the species' index, then the field."""
    scene, kind, sel = split_key(leaf)
    head, _, field = sel.partition(".") if kind in ("dock", "species") else ("", "", sel)
    num = int(scene[1:]) if scene[1:].isdigit() else 999
    idx = int(head) if head.isdigit() else 0
    return (num, KIND_ORDER.get(kind, 9), "" if head.isdigit() else head, idx, field)


def sidecar_fields(sidecar: dict) -> dict[str, object]:
    """The sidecar flattened to ONE LINE PER FIELD: a dock / species / plate patch becomes its
    fields; an exit or a camera is one value of its own."""
    out: dict[str, object] = {}
    for key, patch in (sidecar or {}).items():
        if isinstance(patch, dict) and split_key(key)[1] in ("dock", "species", "plate"):
            for field, value in patch.items():
                out[f"{key}.{field}"] = value
        else:
            out[str(key)] = patch
    return out


# ---- the effective value of a field, off the rows ------------------------------------------------------------------

def _dock_opts(row: list, slide: str) -> dict:
    for d in (row[C.IDX_DOCKS] or []) if len(row) > C.IDX_DOCKS else []:
        if str(d[0]) == slide:
            return dict(d[4]) if len(d) > 4 and isinstance(d[4], dict) else {}
    return {}


def _plate_opts(row: list) -> dict:
    parts = str(row[C.IDX_PLATE]).split(";")[1:]
    return dict(p.split("=", 1) for p in parts if "=" in p)


def effective(rows, ids: dict[str, int], leaf: str) -> tuple[bool, object]:
    """(is the field set, its value) on the EFFECTIVE rows - the authored table with a sidecar
    already layered over it. This is what the compile actually saw, which is what the diff's two
    sides have to be: `centre_y: 0.335 -> 0.30` reads the authored 0.335 off the table, never off a
    sidecar that does not carry it."""
    scene, kind, sel = split_key(leaf)
    i = ids.get(scene)
    if i is None:
        return (False, None)
    row = list(rows[i])
    head, _, field = sel.partition(".")
    if kind == "dock":
        opts = _dock_opts(row, head)
        return (field in opts, opts.get(field))
    if kind == "species":
        sp = (row[C.IDX_SPECIES] or []) if len(row) > C.IDX_SPECIES else []
        if not head.isdigit() or int(head) >= len(sp) or not isinstance(sp[int(head)], dict):
            return (False, None)
        entry = sp[int(head)]
        return (field in entry, entry.get(field))
    if kind == "plate":
        opts = _plate_opts(row)
        return (sel in opts, opts.get(sel))
    if kind == "exit":
        v = row[C.IDX_EXIT] if len(row) > C.IDX_EXIT else None
        return (v is not None, v)
    if kind == "camera":
        v = row[C.IDX_CAMERA] if len(row) > C.IDX_CAMERA else None
        return (v is not None, v)
    return (False, None)


# ---- the diff, line by line ----------------------------------------------------------------------------------------

def _show(present: bool, value) -> str:
    if not present:
        return UNSET
    try:
        return json.dumps(value)
    except TypeError:
        return repr(value)


def diff_line(leaf: str, before: tuple[bool, object], after: tuple[bool, object], state: str,
              word: str | None = None) -> str:
    """One field, one line - the formatter, on its own so it can be read and tested alone.

    `s04.dock.dock-k-pledge-record.centre_y: 0.335 -> 0.3 [added]`; a word-form `at` carries both
    the word and the second it resolved to."""
    tail = f' ("{word}")' if word else ""
    return f"- {leaf}: {_show(*before)} -> {_show(*after)}{tail} [{state}]"


def _word_of(value) -> str | None:
    return value["word"] if isinstance(value, dict) and set(value) == {"word"} else None


def sidecar_diff(before_sc: dict, after_sc: dict, resolve_before, resolve_after) -> list[dict]:
    """Every key of the after sidecar that differs from the before one - added, removed or changed -
    with the two EFFECTIVE values, in row order. `resolve_*` are `effective`, bound to each side's
    rows; when there are no rows they report the raw sidecar value instead."""
    before, after = sidecar_fields(before_sc), sidecar_fields(after_sc)
    rows: list[dict] = []
    for leaf in sorted(set(before) | set(after), key=key_order):
        b, a = resolve_before(leaf), resolve_after(leaf)
        in_b, in_a = leaf in before, leaf in after
        # an explicit `null` is an EDIT (the camera off, an option unset), not an absence: say so
        b = (True, None) if (in_b and before[leaf] is None and not b[0]) else b
        a = (True, None) if (in_a and after[leaf] is None and not a[0]) else a
        if b == a and in_b == in_a:
            continue
        state = "added" if (in_a and not in_b) else ("removed" if (in_b and not in_a) else "changed")
        rows.append({"leaf": leaf, "key": row_key(leaf), "state": state,
                     "line": diff_line(leaf, b, a, state, _word_of(after.get(leaf)))})
    return rows


# ---- the before build ------------------------------------------------------------------------------------------------

def load_json(path: Path, default=None):
    p = Path(path)
    if not p.is_file():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def compile_block(build: Path) -> dict | None:
    return (load_json(Path(build) / SP.MANIFEST_NAME, {}) or {}).get("compile")


def copy_build(build: Path, dest: Path) -> Path:
    """The build, copied whole but for its own output folders - the crops, the determinism frames
    and the self-watch sheets are products, not inputs."""
    shutil.copytree(build, dest, ignore=shutil.ignore_patterns(*SKIP_DIRS))
    return dest


def compiled_with(build: Path, sidecar: dict | None, dest: Path, log=print) -> Path:
    """A COPY of the build, re-compiled in process with `sidecar` in place of its own - the door
    `serve_player --watch` uses (`player.json`'s compile block, `build_render_f.STAMPED` restored,
    `render_baseline.write_split` made incremental so a 31 MB asset map is not rewritten).

    `authoring.table.apply_sidecar` is held off for the run: it rewrites the EPISODE's shot table
    with the effective rows, and a report must not touch the agent's table. The compiler's own
    sidecar pass (`build_scene_timeline_f.main`) layers the copy's `overrides.json` instead, which
    is the same `apply_overrides` over the same authored rows."""
    block = compile_block(build)
    if not block:
        raise SystemExit(f"no `compile` block in {build / SP.MANIFEST_NAME} - a before build cannot be compiled; "
                         "pass --before <old compiled timeline> instead")
    ep = (Path(build) / block["episode_dir"]).resolve()
    out = copy_build(Path(build), Path(dest))
    ov = out / OVERRIDES_NAME
    if sidecar:
        ov.write_text(json.dumps(sidecar, indent=1), encoding="utf-8")
    elif ov.exists():
        ov.unlink()
    import authoring.table as T
    import build_render_f as R
    import render_baseline as RB
    R.STAMPED.update(block.get("stamped") or {})
    fields = {k: v for k, v in block.items() if k not in ("episode_dir", "stamped")}
    fields["kinetics"] = dict(fields.get("kinetics") or {})
    keep_sidecar, keep_split = T.apply_sidecar, RB.write_split
    T.apply_sidecar = lambda *_a, **_k: []
    RB.write_split = SP._incremental_write_split(RB.write_split)
    try:
        rc = _quiet_compile(T, ep, out, fields)
    finally:
        T.apply_sidecar, RB.write_split = keep_sidecar, keep_split
    if rc != 0:
        raise SystemExit(f"the before build did not compile (exit {rc}) - see the compiler's output above")
    log(f"  before: compiled with {len(sidecar or {})} override key(s)")
    return out


def _quiet_compile(T, ep: Path, out: Path, fields: dict) -> int:
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = T.compile_timeline(ep, out, **fields)
    return rc


def build_with_timeline(build: Path, timeline_doc: dict, tl_name: str, dest: Path) -> Path:
    """A copy of the build carrying an OLD compiled timeline - the before of `--before` / `--since`.
    Nothing is compiled: the timeline is the whole of what changed."""
    out = copy_build(Path(build), Path(dest))
    (out / tl_name).write_text(json.dumps(timeline_doc, indent=1), encoding="utf-8")
    return out


def git_show(repo: Path, sha: str, rel: str) -> str | None:
    """`git show <sha>:<path>` - read-only, and the only git this file runs."""
    r = subprocess.run(["git", "-C", str(repo), "show", f"{sha}:{rel}"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout if r.returncode == 0 else None


def repo_rel(repo: Path, path: Path) -> str:
    return str(Path(path).resolve().relative_to(Path(repo).resolve())).replace("\\", "/")


def git_root(build: Path) -> Path:
    r = subprocess.run(["git", "-C", str(build), "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"{build} is not inside a git work tree - --since needs one")
    return Path(r.stdout.strip())


# ---- the instants each key touches ---------------------------------------------------------------------------------

def _picture(tl: dict) -> dict:
    """The compiled timeline minus its own bookkeeping, so the diff is about the PICTURE.

    `overrides_applied` is the list of keys the compile layered (P51 T5): it changes on every
    sidecar edit and moves no frame. `narration.words_path` names the build DIRECTORY, and the
    before build is a copy of it. Without both, the diff calls every scene's first instant changed
    on the strength of a path and a list of key names."""
    out = {k: v for k, v in (tl or {}).items() if k != "overrides_applied"}
    nar = out.get("narration")
    if isinstance(nar, dict):
        out["narration"] = {k: v for k, v in nar.items() if k != "words_path"}
    return out


def species_kinds(tl: dict) -> dict[str, str]:
    """The compiled species' derived ids -> their kind, so a `s04.species.3` key can be matched to
    the diff's `s04 species chart_to`."""
    return {str(sp.get("id")): str(sp.get("kind")) for s in tl.get("scenes") or []
            for sp in s.get("species") or [] if sp.get("id")}


def touches(key: str, why: str, kinds: dict[str, str]) -> bool:
    scene, kind, sel = split_key(key)
    if not why.startswith(scene + " "):
        return False
    rest = why[len(scene) + 1:]
    if kind == "dock":
        return rest.startswith(f"dock {sel} ")
    if kind == "species":
        k = kinds.get(key)
        return bool(k) and rest.startswith(f"species {k}")
    return not rest.startswith("dock ") and not rest.startswith("species ")


def instants_by_key(keys: list[str], changed: list[tuple[float, str]], kinds: dict[str, str]
                    ) -> tuple[dict[str, list[tuple[float, str]]], list[tuple[float, str]]]:
    """The determinism check's diff, attributed to the keys that explain it; what no key explains is
    reported as such rather than dropped."""
    out = {k: [] for k in keys}
    claimed: set[int] = set()
    for n, (t, why) in enumerate(changed):
        for k in keys:
            if touches(k, why, kinds):
                out[k].append((t, why))
                claimed.add(n)
    return out, [row for n, row in enumerate(changed) if n not in claimed]


def crop_plan(by_key: dict[str, list[tuple[float, str]]], limit: int) -> list[tuple[str, float, str]]:
    """Round robin over the keys, so every changed key gets its first instant before any key gets a
    second - the frames are bounded and the order is the same on every run."""
    plan: list[tuple[str, float, str]] = []
    depth = 0
    while len(plan) < limit and any(len(v) > depth for v in by_key.values()):
        for key in sorted(by_key, key=key_order):
            rows = by_key[key]
            if depth < len(rows) and len(plan) < limit:
                plan.append((key, rows[depth][0], rows[depth][1]))
        depth += 1
    return plan


# ---- the crops -------------------------------------------------------------------------------------------------------

def element_box(key: str, insts: list[dict], stage: tuple[int, int]) -> tuple[int, int, int, int]:
    """The changed element's box across the two builds, padded by 10 % and clamped to the stage -
    ONE box for both frames, so the eye compares like with like. A key the probe names no box for
    (a camera, a plate, a species) is shown as the whole frame: that is what it changes."""
    scene, kind, sel = split_key(key)
    slide = sel.partition(".")[0]
    boxes = [d["box"] for inst in insts if inst for d in inst.get("docks") or []
             if kind == "dock" and d.get("id") == slide]
    sw, sh = stage
    if not boxes:
        return (0, 0, sw, sh)
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes); y1 = max(b[1] + b[3] for b in boxes)
    px, py = CROP_PAD * (x1 - x0), CROP_PAD * (y1 - y0)
    return (int(max(0, x0 - px)), int(max(0, y0 - py)), int(min(sw, x1 + px)), int(min(sh, y1 + py)))


def write_crops(png_before: bytes, png_after: bytes, box: tuple[int, int, int, int], stem: Path,
                t: float) -> dict[str, Path]:
    """The two frames cropped to the same box, and one 2-up for the instant."""
    from PIL import Image, ImageDraw
    stem.parent.mkdir(parents=True, exist_ok=True)
    ims = []
    out: dict[str, Path] = {}
    for name, png in (("before", png_before), ("after", png_after)):
        im = Image.open(io.BytesIO(png)).convert("RGB").crop(box)
        p = stem.with_name(f"{stem.name}-{name}.png")
        im.save(p, "PNG")
        ims.append(im)
        out[name] = p
    pad, gap = 26, 12
    sheet = Image.new("RGB", (ims[0].width + ims[1].width + gap, max(i.height for i in ims) + pad), (13, 15, 18))
    sheet.paste(ims[0], (0, pad))
    sheet.paste(ims[1], (ims[0].width + gap, pad))
    d = ImageDraw.Draw(sheet)
    d.text((6, 6), f"before {t:.2f}s", fill=(220, 227, 234))
    d.text((ims[0].width + gap + 6, 6), f"after {t:.2f}s", fill=(220, 227, 234))
    p = stem.with_name(f"{stem.name}-pair.png")
    sheet.save(p, "PNG")
    out["pair"] = p
    return out


def probe_pass(build: Path, tl_name: str, plan: list[tuple[str, float, str]]) -> tuple[dict, tuple[int, int]]:
    """One build, one probe session: the DOM and the frame at every planned instant. The two builds
    are read one AFTER the other - playwright's sync API allows one session per thread."""
    out: dict[tuple[str, float], tuple[dict, bytes]] = {}
    with P.Probe(build, tl_name) as p:
        for key, t, why in plan:
            out[(key, round(t, 2))] = (p.at(t, why), p.png(t))
        return out, (p.w, p.h)


def crops_for(plan: list[tuple[str, float, str]], before_build: Path, after_build: Path,
              tl_name: str, out_dir: Path) -> list[dict]:
    """The instant read on both builds, the crop box taken from the element the key names, the two
    frames cut to that one box."""
    if not plan:
        return []
    before, _ = probe_pass(before_build, tl_name, plan)
    after, stage = probe_pass(after_build, tl_name, plan)
    rows: list[dict] = []
    for key, t, why in plan:
        ib, pb = before[(key, round(t, 2))]
        ia, pa = after[(key, round(t, 2))]
        box = element_box(key, [ib, ia], stage)
        files = write_crops(pb, pa, box, out_dir / f"{key}-{t:.2f}", t)
        rows.append({"key": key, "t": t, "why": why, "box": list(box),
                     "files": {k: v.name for k, v in files.items()}})
    return rows


# ---- the gate delta --------------------------------------------------------------------------------------------------

def gate_rows(build: Path, tl_name: str) -> dict[str, G.Gate]:
    """The motion gate on one build, with its layout probe written first so M25 / M26 are MEASURED
    on this build and not read off a stale file."""
    P.write_gate(build, tl_name)
    tl, docks, mp = G._load(Path(build), tl_name)
    gates, _stats = G.run(tl, docks, mp, G.load_frames(build), G.load_morph_invariants(build), G.load_layout(build))
    return {g.id: g for g in gates}


def gate_delta(before: dict[str, G.Gate], after: dict[str, G.Gate], width: int = 220) -> tuple[list[str], int]:
    """Every row whose LEVEL or TEXT moved, as `M12: PASS -> WARN (...)`; the rest are counted."""
    moved: list[str] = []
    same = 0
    for gid in sorted(set(before) | set(after)):
        b, a = before.get(gid), after.get(gid)
        if b is not None and a is not None and b.level == a.level and b.message == a.message:
            same += 1
            continue
        if b is None:
            moved.append(f"{gid}: (absent) -> {a.level} ({_trim(a.message, width)})")
        elif a is None:
            moved.append(f"{gid}: {b.level} -> (gone)")
        elif b.level != a.level:
            moved.append(f"{gid}: {b.level} -> {a.level} ({_trim(a.message, width)})")
        else:   # the same verdict on different numbers: the delta IS the two texts, not one of them
            moved.append(f"{gid}: {b.level} -> {a.level}, the reading moved - before: {_trim(b.message, width)}"
                         f" - after: {_trim(a.message, width)}")
    return moved, same


def _trim(s: str, w: int) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= w else s[:w - 1] + "..."


# ---- the report --------------------------------------------------------------------------------------------------------

def _cell(s: str) -> str:
    return str(s).replace("|", "\\|")


def section_diff(diff: list[dict]) -> list[str]:
    out = ["## 1. The sidecar, field by field", ""]
    out += [d["line"] for d in diff] or ["- nothing: the two sidecars resolve to the same rows"]
    return out + [""]


def section_instants(by_key: dict[str, list[tuple[float, str]]], crops: list[dict], other: list[tuple[float, str]],
                     diff_keys: list[str]) -> list[str]:
    by_pair = {(c["key"], round(c["t"], 2)): c for c in crops}
    out = ["## 2. The instants each key touches, before and after", "",
           "(the determinism check's own diff of the two compiled timelines names these; instants are "
           "deduped to 1/50 s, so one reason stands for every key that moved at the same instant)", ""]
    for key in sorted(diff_keys, key=key_order):
        rows = by_key.get(key) or []
        out += [f"### {key} - {len(rows)} instant(s)", ""]
        if not rows:
            out += ["the timeline did not move at any instant this key names (the field is layered, "
                    "the compiled form is the same)", ""]
            continue
        out += ["| t | why | before | after | pair |", "|---|---|---|---|---|"]
        for t, why in rows:
            c = by_pair.get((key, round(t, 2)))
            f = (lambda n: f"{CROP_DIR}/{c['files'][n]}") if c else (lambda _n: "-")
            out.append(f"| {t:.2f} | {_cell(why)} | {f('before')} | {f('after')} | {f('pair')} |")
        out.append("")
    if other:
        out += [f"### instants no key explains - {len(other)}", ""]
        out += [f"- {t:.2f}  {why}" for t, why in other] + [""]
    return out


def section_gate(moved: list[str], same: int) -> list[str]:
    out = ["## 3. The gate delta (M01-M26, before -> after)", ""]
    out += [f"- {r}" for r in moved] or ["- no row moved"]
    return out + ["", f"{same} row(s) unchanged.", ""]


def section_determinism(rep: dict | None, note: str) -> list[str]:
    out = ["## 4. The determinism check on the after build, at the changed instants", ""]
    if rep is None:
        return out + [note, ""]
    out += ["| t | why | warm vs cold |", "|---|---|---|"]
    for r in rep["instants"]:
        verdict = "ok" if r["match"] else ("MISMATCH" + (f" - {r['known']}" if r.get("known") else ""))
        out.append(f"| {r['t']:.2f} | {_cell(r['why'])} | {verdict} |")
    return out + ["", f"verdict: {rep['summary']}", ""]


def verdict_line(diff: list[dict], instants: int, moved: list[str], determinism: str) -> str:
    keys = {d["key"] for d in diff}
    gate = ", ".join(r.split(":", 1)[0] for r in moved) if moved else "none"
    return (f"{len(diff)} field(s) changed on {len(keys)} row(s); {instants} instant(s); "
            f"gate delta: {gate}; determinism: {determinism}")


def render(head: dict, diff: list[dict], by_key: dict, crops: list[dict], other: list,
           moved: list[str], same: int, det: dict | None, det_note: str, verdict: str) -> str:
    out = [f"# CHANGE REPORT - {head['build']} - {head['date']}", "",
           f"before: {head['before']}",
           f"after: {head['after']}",
           f"timeline: {head['timeline']} - aspect {head['aspect']} - runtime {head['runtime']:.1f} s", ""]
    out += section_diff(diff)
    out += section_instants(by_key, crops, other, [d["key"] for d in diff])
    out += section_gate(moved, same)
    out += section_determinism(det, det_note)
    out += ["## 5. Verdict", "", verdict, ""]
    return "\n".join(out)


# ---- the run ------------------------------------------------------------------------------------------------------------

def _resolvers(build: Path, before_sc: dict, after_sc: dict, note: list[str]):
    """`effective` bound to each side's rows - the authored shot table with each sidecar layered
    over it. Without an episode behind the build (a golden surface), or when a sidecar the report
    is only DESCRIBING is refused by the compiler's validator, the raw sidecar value stands in and
    the report says so."""
    block = compile_block(build)
    if not block:
        note.append("no compile block: the values below are the sidecars' own, not the compiled rows")
        return ((lambda leaf, sc=before_sc: (leaf in sidecar_fields(sc), sidecar_fields(sc).get(leaf))),
                (lambda leaf, sc=after_sc: (leaf in sidecar_fields(sc), sidecar_fields(sc).get(leaf))))
    import authoring.table as T
    table = (Path(build) / block["episode_dir"] / block["shot_table_file"]).resolve()
    rows = T.load_rows(table)
    words = (load_json(Path(build) / "timeline.json", {}) or {}).get("words")
    out = []
    for sc in (before_sc, after_sc):
        try:
            eff = C.apply_overrides(rows, sc, words=words, aspect=block.get("aspect"))
        except ValueError as exc:
            note.append(f"a sidecar could not be layered ({exc}) - its raw values are shown")
            eff = rows
        ids = C.row_ids(eff)
        out.append(lambda leaf, r=eff, i=ids: effective(r, i, leaf))
    return out[0], out[1]


def _before_build(build: Path, mode: str, ref, tl_name: str, work: Path, log) -> tuple[Path, dict, str]:
    """(the before build, its sidecar, the line the header states it with)."""
    if mode == "against":
        sc = load_json(Path(ref), None)
        if not isinstance(sc, dict):
            raise SystemExit(f"{ref} is not a sidecar (a JSON object keyed by row id and field)")
        return compiled_with(build, sc, work / "before", log), sc, f"the build re-compiled with {Path(ref).name}"
    if mode == "before":
        doc = load_json(Path(ref), None)
        if not isinstance(doc, dict) or "scenes" not in doc:
            raise SystemExit(f"{ref} is not a compiled timeline")
        beside = load_json(Path(ref).parent / OVERRIDES_NAME, {}) or {}
        return (build_with_timeline(build, doc, tl_name, work / "before"), beside,
                f"the compiled timeline {Path(ref).name}")
    if mode == "since":
        repo = git_root(build)
        text = git_show(repo, str(ref), repo_rel(repo, Path(build) / tl_name))
        if text is None:
            raise SystemExit(f"no {tl_name} at {ref} - `git show {ref}:<the build's timeline>` found nothing")
        sc_text = git_show(repo, str(ref), repo_rel(repo, Path(build) / OVERRIDES_NAME))
        sc = json.loads(sc_text) if sc_text else {}
        return (build_with_timeline(build, json.loads(text), tl_name, work / "before"), sc,
                f"the compiled timeline at {ref}")
    return (compiled_with(build, {}, work / "before", log), {},
            "the build re-compiled with no sidecar (the agent's authored rows)")


def run(build: Path, mode: str = "authored", ref=None, timeline: str | None = None, max_crops: int = MAX_CROPS,
        check_max: int = CHECK_MAX, check: bool = True, work: Path | None = None, log=print) -> dict:
    """The whole report. Returns {path, text, verdict, diff, crops, gate_delta, determinism}."""
    build = Path(build).resolve()
    tl_name = G._timeline_path(build, timeline).name
    after_sc = load_json(build / OVERRIDES_NAME, {}) or {}
    tmp = None
    if work is None:
        tmp = tempfile.TemporaryDirectory(prefix="change-report-")
        work = Path(tmp.name)
    try:
        before_build, before_sc, before_line = _before_build(build, mode, ref, tl_name, Path(work), log)
        note: list[str] = []
        rb, ra = _resolvers(build, before_sc, after_sc, note)
        diff = sidecar_diff(before_sc, after_sc, rb, ra)
        before_tl = load_json(before_build / tl_name)
        after_tl = load_json(build / tl_name)
        changed = DC.changed_instants(_picture(before_tl), _picture(after_tl))
        by_key, other = instants_by_key([d["key"] for d in diff], changed, species_kinds(after_tl))
        log(f"  {len(diff)} field(s), {len(changed)} instant(s) - crops")
        crops = crops_for(crop_plan(by_key, max_crops), before_build, build, tl_name, build / CROP_DIR)
        log("  the gate, on both builds")
        moved, same = gate_delta(gate_rows(before_build, tl_name), gate_rows(build, tl_name))
        det, det_note = None, "not run (no changed instant)" if not changed else "not run (--no-check)"
        if check and changed:
            log("  the determinism check, on the after build")
            det = DC.run(build, changed, tl_name, max_instants=check_max, log=lambda *_a: None)
            det_note = ""
        summary = det["summary"] if det else det_note
        verdict = verdict_line(diff, len(changed), moved, summary)
        head = {"build": f"{build.parent.name}/{build.name}", "date": _dt.date.today().isoformat(),
                "before": before_line + ("; " + "; ".join(note) if note else ""),
                "after": f"the build as it stands ({OVERRIDES_NAME}, {len(after_sc)} key(s))",
                "timeline": tl_name, "aspect": str(after_tl.get("aspect") or "16:9"),
                "runtime": float(after_tl.get("runtime_s") or 0.0)}
        text = render(head, diff, by_key, crops, other, moved, same, det, det_note, verdict)
        out = build / REPORT_NAME
        out.write_text(text, encoding="utf-8")
        return {"path": out, "text": text, "verdict": verdict, "diff": diff, "crops": crops,
                "gate_delta": moved, "determinism": summary, "instants": changed}
    finally:
        if tmp is not None:
            tmp.cleanup()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="what a human or a flash agent changed, as the agent sees it (P51 T6)")
    ap.add_argument("build", type=Path)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--against", type=Path, help="an overrides.json: the before is the build compiled with IT")
    g.add_argument("--before", type=Path, help="an older compiled timeline: the before is the build carrying it")
    g.add_argument("--since", help="a git sha: the before is the compiled timeline at that sha (read-only)")
    ap.add_argument("--timeline", help="the compiled timeline's file name (default: the only one in the build)")
    ap.add_argument("--max-crops", type=int, default=MAX_CROPS, help="how many before/after crop pairs to write")
    ap.add_argument("--max-instants", type=int, default=CHECK_MAX, help="instants the determinism check renders")
    ap.add_argument("--no-check", action="store_true", help="skip the determinism check")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    mode, ref = "authored", None
    for name in ("against", "before", "since"):
        if getattr(a, name):
            mode, ref = name, getattr(a, name)
    try:
        rep = run(a.build, mode, ref, timeline=a.timeline, max_crops=a.max_crops,
                  check_max=a.max_instants, check=not a.no_check)
    except SystemExit as exc:
        print(f"change_report: {exc}", file=sys.stderr)
        return 2
    print(rep["path"])
    for d in rep["diff"]:
        print("  " + d["line"])
    print("  " + rep["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""P55 T9: the effects gallery - one static review page generated from EFFECTS-CATALOG.jsonl only.

One tile per card, grouped by axis in the catalogue's order: title, id, status pill + backlog ids, aliases, does, the
phases, the blends, the authoring example with its validator, where it lives, callable-today, and the proof. A last
section holds the RECIPES (P56 T4): one tile each, the ordered members with their offsets and roles, and the proof
frame of every member whose card has one - so a combination can be read as the sequence of stills it plays. The
golden frames are COPIED beside the page (a served review link is a frozen copy); a card whose golden does not resolve
shows an explicit "no proof yet" marker so the gap stays visible. No external requests: system fonts, inline CSS/JS.

P61 T9: the build is half its old wall clock (ONE directory listing instead of ~300 globs, no re-copy of unchanged
frames, one tally, no import a build does not need); the page carries three golden frames of its own so "faster" can
never mean "renders less" (--pin, checked by tests/test_effects_gallery.py); and a card whose effect a still cannot
show carries its rendered clip as a <video> when one is beside the page (`frames/<card-id>.mp4`, rendered by
review_queue_proofs.py's clip path).

    python content/video_engine/scripts/build_effects_gallery.py [--out DIR] [--catalog PATH] [--frames DIR]
    python content/video_engine/scripts/build_effects_gallery.py --pin        # re-take the three golden frames

Deterministic: the same catalogue and frames give byte-identical index.html. Stdlib only (playwright only for --pin).
"""
from __future__ import annotations

import html
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parent
CATALOG_REL = "docs/EFFECTS-CATALOG.jsonl"
CATALOG_LAYER = "effects-catalog"      # docs_layers' name for the builder that writes CATALOG_REL
FRAMES_REL = "content/video_engine/tests/golden/frames"
OUT_REL = "content/video_engine/effects/gallery"
FRAMES_SUBDIR = "frames"
CLIP_SUFFIX = ".mp4"      # P61 T9 (c): a motion example, rendered by review_queue_proofs' clip path
STATUSES = ("live", "wired", "draft", "declared", "planned")
RECIPE_AXIS = "recipe"
NO_PROOF_MARKER = "no proof yet"


def ensure_catalog(catalog: Path, *, wait: bool = False) -> list[str]:
    """Say whether the catalogue behind the page is behind - and with `wait`, rebuild it first.

    The gallery is itself build output (`.gitignore`, P55 T9). Since P64 T1 the DEFAULT builds
    nothing: it prints one `[layers] stale: ...` line and generates the page from the catalogue as it
    sits, because the write to a card is what starts the refresh. `--wait` is for the pass that must
    carry this morning's card. Only the repo's own artifact - a `--catalog` pointing anywhere else is
    the caller's file. `docs_layers` is imported here rather than at the top for the same reason
    `argparse` is (the flagless build pays 23 ms less to start). A builder that fails is named on
    stderr and the page is built from the catalogue as it sits."""
    if catalog.resolve() != (ROOT / CATALOG_REL).resolve():
        return []
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import docs_layers as DL
    if not wait:
        DL.report_stale(ROOT, [CATALOG_LAYER])
        return []
    try:
        return DL.ensure([CATALOG_LAYER], ROOT)
    except DL.LayerError as exc:
        print(f"[layers] {exc.layer} failed to rebuild: {exc.detail}", file=sys.stderr)
        return []


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def load_cards(catalog: Path) -> list[dict]:
    lines = catalog.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def axes_in_order(cards: list[dict]) -> list[str]:
    seen: list[str] = []
    for c in cards:
        if c["axis"] not in seen and c["axis"] != RECIPE_AXIS:
            seen.append(c["axis"])
    return seen


def split_recipes(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """(cards, recipes) - a recipe is a combination of cards and never counts as one."""
    return ([r for r in records if r.get("axis") != RECIPE_AXIS],
            [r for r in records if r.get("axis") == RECIPE_AXIS])


def names_ending(directory: Path | None, suffix: str) -> list[str]:
    """One `scandir`: the file names in `directory` ending in `suffix` (empty when it is not there)."""
    try:
        return [e.name for e in os.scandir(directory) if e.name.endswith(suffix) and e.is_file()]
    except (FileNotFoundError, NotADirectoryError, TypeError):
        return []


def clip_name(card_id: str) -> str:
    """`dock_payload:stack` -> `dock_payload-stack.mp4`; a colon is not a file name on Windows."""
    return f"{card_id.replace(':', '-')}{CLIP_SUFFIX}"


class FrameIndex:
    """ONE listing of the golden frames, reused by every card (P61 T9 (a): the build's dominant stage).

    `resolve_proof` used to glob the frames directory once per card, once per counted card and once
    per recipe member - some 300 scans of a 99-file directory. The same answers come from a single
    `scandir`, and the strip is grouped exactly as the old glob matched: `<surface>@proof-*` only,
    never `<surface>@something@proof-*`.
    """
    __slots__ = ("directory", "stems", "strips", "clips")

    def __init__(self, directory: Path, clips_dir: Path | None = None) -> None:
        self.directory = Path(directory)
        self.stems: set[str] = set()
        self.strips: dict[str, list[str]] = {}
        # P61 T9 (c): the motion examples that live BESIDE the page, not among the goldens
        self.clips: set[str] = set(names_ending(clips_dir, CLIP_SUFFIX)) if clips_dir else set()
        for name in names_ending(self.directory, ".png"):
            stem = name[: -len(".png")]
            self.stems.add(stem)
            surface, _, rest = stem.partition("@")
            if rest.startswith("proof-"):
                self.strips.setdefault(surface, []).append(stem)
        for strip in self.strips.values():
            strip.sort()

    def resolve(self, golden: str | None) -> tuple[str | None, list[str]]:
        """(the main frame stem or None, the sorted @proof-* stems of the same surface)."""
        if not golden or golden not in self.stems:
            return None, []
        return golden, [s for s in self.strips.get(golden.partition("@")[0], ()) if s != golden]

    def clip_of(self, card_id: str) -> str | None:
        """The motion example rendered for this card, when one is beside the page (P61 T9 (c))."""
        name = clip_name(card_id)
        return name if name in self.clips else None


def frame_index(frames: "FrameIndex | Path") -> FrameIndex:
    """Take the index or the directory it was built from - a caller holding a plain path still works."""
    return frames if isinstance(frames, FrameIndex) else FrameIndex(frames)


def resolve_proof(golden: str | None, frames: "FrameIndex | Path") -> tuple[str | None, list[str]]:
    """Return (main frame stem or None, sorted @proof-* stems of the same surface)."""
    return frame_index(frames).resolve(golden)


SAFE = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-~/")


def pct(stem: str) -> str:
    """`urllib.parse.quote` for a frame stem, without paying for the urllib import on every build.

    `@` -> `%40` is the only escape a committed stem has ever needed; test_effects_gallery checks
    this against urllib itself over every stem on disk, so the page's bytes cannot drift.
    """
    return "".join(c if c in SAFE else "".join(f"%{b:02X}" for b in c.encode("utf-8")) for c in stem)


def img_src(stem: str) -> str:
    return f"{FRAMES_SUBDIR}/{pct(stem)}.png"


def render_aliases(card: dict) -> str:
    names = [a.get("name") for a in card.get("aliases") or [] if a.get("name")]
    if not names:
        return ""
    return f'<p class="aliases">aka {esc(" / ".join(names))}</p>'


def render_phases(card: dict) -> str:
    phases = card.get("phases") or []
    if not phases:
        return ""
    items = "".join(
        f'<li class="phase"><b>{esc(p.get("name"))}</b> - {esc(p.get("trigger"))}</li>' for p in phases)
    return f'<h4>Phases</h4><ol class="phases">{items}</ol>'


def render_blends(card: dict) -> str:
    blends = card.get("blends") or []
    if not blends:
        return ""
    items = "".join(
        f'<li class="blend">{esc(b.get("source"))} -&gt; {esc(b.get("became"))}</li>' for b in blends)
    return f'<h4>Blends</h4><ul class="blends">{items}</ul>'


def render_author(card: dict) -> str:
    author = card.get("author") or {}
    parts = []
    if author.get("key"):
        parts.append(f'<p class="key">{esc(author["key"])}</p>')
    if author.get("example"):
        parts.append(f'<pre class="example">{esc(author["example"])}</pre>')
    parts.append(f'<p class="check">validator: <code>{esc(author.get("check") or "none")}</code></p>')
    return "<h4>Author</h4>" + "".join(parts)


def render_lives(card: dict) -> str:
    lives = card.get("lives") or {}
    return (f'<p class="lives">lives: <span class="form">{esc(lives.get("form"))}</span> '
            f'<code>{esc(lives.get("path"))}</code> <code>{esc(lives.get("symbol"))}</code></p>')


def render_callable(card: dict) -> str:
    call = card.get("callable") or {}
    if call.get("today") is False:
        return f'<p class="warn">not callable today: {esc(call.get("why"))}</p>'
    if call.get("why"):
        return f'<p class="note">{esc(call["why"])}</p>'
    return ""


def render_motion(card: dict, frames: FrameIndex) -> str:
    """The clip of an effect a still cannot show (P61 T9 (c)): a composite of more than one phase
    whose golden already needed extra `@proof-*` instants pinned beside it. Rendered by
    `review_queue_proofs.render_clip` - the review queue's own headless-Chromium -> ffmpeg path."""
    name = frames.clip_of(card["id"])
    if not name:
        return ""
    return (f'<video class="motion" src="{FRAMES_SUBDIR}/{pct(name)}" controls muted loop playsinline '
            f'preload="metadata"></video><p class="cap">motion: the phases a still cannot show</p>')


def render_proof(card: dict, frames: FrameIndex) -> str:
    proof = card.get("proof") or {}
    main, strip = resolve_proof(proof.get("golden"), frames)
    motion = render_motion(card, frames)
    test = proof.get("test")
    test_html = f'<p class="test">test: <code>{esc(test)}</code></p>' if test else ""
    if main is None:
        missing = f" (golden {esc(proof['golden'])} not found)" if proof.get("golden") else ""
        return (f'<div class="proof none"><p class="noproof">{NO_PROOF_MARKER}{missing}</p>'
                f'{motion}{test_html}</div>')
    thumbs = "".join(
        f'<a href="{img_src(s)}" title="{esc(s)}"><img loading="lazy" src="{img_src(s)}" alt="{esc(s)}"></a>'
        for s in strip)
    strip_html = f'<div class="strip">{thumbs}</div>' if thumbs else ""
    return (f'<div class="proof"><a href="{img_src(main)}"><img class="golden" loading="lazy" '
            f'src="{img_src(main)}" alt="{esc(main)}"></a><p class="cap">{esc(main)}</p>'
            f'{strip_html}{motion}{test_html}</div>')


def search_text(card: dict) -> str:
    names = [a.get("name") or "" for a in card.get("aliases") or []]
    fields = [card.get("title"), card.get("id"), card.get("token"), card.get("does"), *names]
    return " ".join(str(f) for f in fields if f).lower()


def render_card(card: dict, frames: "FrameIndex | Path") -> str:
    frames = frame_index(frames)
    status = card.get("status") or "unknown"
    backlog = "".join(f'<span class="backlog">{esc(b)}</span>' for b in card.get("backlog") or [])
    return (
        f'<article class="tile" data-id="{esc(card["id"])}" data-search="{esc(search_text(card))}">'
        f'<h3>{esc(card.get("title"))}</h3>'
        f'<p class="meta"><code class="id">{esc(card["id"])}</code> '
        f'<span class="pill s-{esc(status)}">{esc(status)}</span>{backlog}</p>'
        f'{render_aliases(card)}<p class="does">{esc(card.get("does"))}</p>'
        f'{render_proof(card, frames)}{render_phases(card)}{render_blends(card)}'
        f'{render_author(card)}{render_lives(card)}{render_callable(card)}</article>'
    )


def offset_text(value) -> str:
    """`+2.05s`, or `+2.05..6.65s` when the member fired at a range of offsets."""
    if isinstance(value, list):
        return f"+{float(value[0]):g}..{float(value[1]):g}s"
    return f"+{float(value or 0):g}s"


def member_frame(member: dict, by_id: dict, frames: "FrameIndex | Path") -> str:
    """The member card's own proof frame, where it has one - the combination read as stills."""
    card = by_id.get(member.get("card")) or {}
    main, _ = resolve_proof((card.get("proof") or {}).get("golden"), frames)
    if not main:
        return ""
    return (f'<a href="{img_src(main)}" title="{esc(main)}">'
            f'<img class="member-frame" loading="lazy" src="{img_src(main)}" alt="{esc(main)}"></a>')


def render_members(recipe: dict, by_id: dict, frames: "FrameIndex | Path") -> str:
    items = []
    for member in recipe.get("members") or []:
        option = f' <span class="opt">{esc(member["option"])}</span>' if member.get("option") else ""
        title = esc(member.get("title") or "no card of that id")
        optional = '<span class="backlog">optional</span>' if member.get("optional") else ""
        items.append(f'<li class="member"><b>{esc(offset_text(member.get("offset_s")))}</b> '
                     f'<code>{esc(member.get("card"))}</code>{option} - {title}{optional}'
                     f'<span class="role">{esc(member.get("role"))}</span>'
                     f'{member_frame(member, by_id, frames)}</li>')
    return f'<h4>Members</h4><ol class="members">{"".join(items)}</ol>'


def render_recipe_proof(recipe: dict) -> str:
    proof = recipe.get("proof")
    if not proof:
        return f'<div class="proof none"><p class="noproof">{NO_PROOF_MARKER} (a candidate)</p></div>'
    at = ", ".join("-" if t is None else f"{float(t):g}" for t in proof.get("members_at") or [])
    when = f'{float(proof.get("t") or 0):g}'
    return (f'<p class="test">proof: {esc(proof.get("project"))} / {esc(proof.get("build"))} @ {esc(when)}s'
            f' - members at {esc(at)}</p>'
            f'<p class="check"><code>{esc(proof.get("timeline"))}</code></p>')


def render_recipe(recipe: dict, by_id: dict, frames: "FrameIndex | Path") -> str:
    status = recipe.get("status") or "unknown"
    count = recipe.get("count") or 0
    says = "a decoration" if count == 1 else ("unfired" if count < 1 else "a grammar")
    dials = ", ".join(f"{k}={v}" for k, v in (recipe.get("dials") or {}).items())
    dial_html = (f'<p class="key">dials: {esc(dials)}</p>'
                 f'<p class="check">measured: {esc(recipe.get("dials_source"))}</p>') if dials else ""
    window = f'{float(recipe.get("window_s") or 0):g}'
    return (
        f'<article class="tile recipe" data-id="{esc(recipe["id"])}" data-search="{esc(search_text(recipe))}">'
        f'<h3>{esc(recipe.get("title"))}</h3>'
        f'<p class="meta"><code class="id">{esc(recipe["id"])}</code> '
        f'<span class="pill s-{esc(status)}">{esc(status)}</span>'
        f'<span class="backlog">count {esc(count)} ({esc(says)})</span></p>'
        f'{render_aliases(recipe)}<p class="does">{esc(recipe.get("does"))}</p>'
        f'<p class="check">acts: {esc(", ".join(recipe.get("acts") or []))} - window {esc(window)}s</p>'
        f'{render_members(recipe, by_id, frames)}{render_recipe_proof(recipe)}{dial_html}</article>'
    )


def compute_counts(cards: list[dict], frames: "FrameIndex | Path") -> dict:
    cards, recipes = split_recipes(cards)
    counts = {"cards": len(cards), **{s: 0 for s in STATUSES}, "with golden": 0, "with test": 0, "no proof": 0,
              "recipes": len(recipes)}
    for c in cards:
        counts[c.get("status")] = counts.get(c.get("status"), 0) + 1
        has_golden = resolve_proof((c.get("proof") or {}).get("golden"), frames)[0] is not None
        has_test = bool((c.get("proof") or {}).get("test"))
        counts["with golden"] += has_golden
        counts["with test"] += has_test
        counts["no proof"] += not (has_golden or has_test)
    return counts


def counts_line(counts: dict) -> str:
    parts = [f"{counts['cards']} cards"]
    parts += [f"{k} {v}" for k, v in counts.items() if k != "cards"]
    return " | ".join(parts)


CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
background:#f6f3ec;color:#222}header{padding:12px 16px;background:#222;color:#f6f3ec}
header h1{margin:0 0 4px;font-size:20px}.counts{margin:0;font-size:13px;opacity:.9}
nav{position:sticky;top:0;z-index:5;background:#fffdf8;border-bottom:1px solid #ccc;padding:8px 16px;
display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center}nav a{font-size:13px;color:#224;text-decoration:none}
nav input{flex:1 1 220px;padding:6px 8px;font:inherit;border:1px solid #999;border-radius:4px}
section{padding:8px 16px}section h2{margin:18px 0 8px;font-size:18px;scroll-margin-top:90px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:12px}
@media (max-width:640px){.grid{grid-template-columns:1fr}nav{position:static}}
.tile{background:#fff;border:1px solid #ddd;border-radius:6px;padding:10px 12px;min-width:0}
.tile h3{margin:0 0 4px;font-size:16px}.tile h4{margin:10px 0 2px;font-size:13px;color:#555}
.meta{margin:0 0 4px}.id{font-size:12px}code,pre{font-family:ui-monospace,Consolas,"Courier New",monospace}
.pill,.backlog{display:inline-block;font-size:11px;padding:1px 7px;border-radius:9px;margin-left:4px;color:#fff}
.backlog{background:#666}.s-live{background:#1b7a3a}.s-wired{background:#2459a8}.s-draft{background:#8a6d00}
.s-declared{background:#7a3c9a}.s-planned{background:#888}.aliases{margin:0;font-size:12px;color:#666}
.s-proven{background:#1b7a3a}.s-candidate{background:#8a6d00}
.members{font-size:13px}.member{margin-bottom:6px}.member .opt{font-size:11px;color:#555}
.member .role{display:block;color:#555;font-size:12px}
.member img.member-frame{display:block;max-width:100%;height:auto;margin-top:3px;border:1px solid #ccc}
.does{margin:6px 0}ol,ul{margin:0;padding-left:20px;font-size:13px}
pre.example{background:#f2f2f2;padding:6px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;font-size:12px;margin:4px 0}
.key,.check,.lives,.test,.note,.cap{font-size:12px;margin:2px 0;word-break:break-word}
.warn{background:#fff1d6;border-left:4px solid #d08a00;padding:4px 8px;font-size:13px}
.note{color:#666}.proof img.golden{display:block;max-width:100%;height:auto;border:1px solid #ccc}
.strip{display:flex;gap:4px;overflow-x:auto;margin-top:4px}.strip img{height:64px;width:auto;border:1px solid #ccc}
.proof.none{border:2px dashed #c33;padding:8px;background:#fff6f6}.noproof{margin:0;color:#a11;font-weight:600}
video.motion{display:block;width:100%;height:auto;border:1px solid #ccc;margin-top:4px;background:#222}
.hidden{display:none}
"""

JS = """
(function(){var box=document.getElementById('filter');box.addEventListener('input',function(){
var q=box.value.trim().toLowerCase();document.querySelectorAll('section.axis').forEach(function(sec){
var shown=0;sec.querySelectorAll('.tile').forEach(function(t){var hit=!q||t.dataset.search.indexOf(q)>=0||
t.dataset.id.toLowerCase().indexOf(q)>=0;t.classList.toggle('hidden',!hit);if(hit)shown++;});
sec.classList.toggle('hidden',shown===0);});});})();
"""


def render_page(records: list[dict], frames: "FrameIndex | Path", line: str | None = None) -> str:
    """`line` is the counts line when the caller already has it - build() did the same tally twice."""
    frames = frame_index(frames)
    cards, recipes = split_recipes(records)
    by_id = {c["id"]: c for c in cards}
    axes = axes_in_order(cards)
    line = counts_line(compute_counts(records, frames)) if line is None else line
    nav = "".join(
        f'<a href="#axis-{esc(a)}">{esc(a)} ({sum(c["axis"] == a for c in cards)})</a>' for a in axes)
    if recipes:
        nav += f'<a href="#axis-recipe">recipes ({len(recipes)})</a>'
    sections = []
    for a in axes:
        tiles = "".join(render_card(c, frames) for c in cards if c["axis"] == a)
        sections.append(f'<section class="axis" id="axis-{esc(a)}"><h2>{esc(a)}</h2><div class="grid">{tiles}</div></section>')
    if recipes:
        tiles = "".join(render_recipe(r, by_id, frames) for r in recipes)
        sections.append(f'<section class="axis" id="axis-recipe"><h2>recipes</h2>'
                        f'<div class="grid">{tiles}</div></section>')
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Effects gallery</title><style>{CSS}</style></head><body>'
        f'<header><h1>Effects gallery</h1><p class="counts">{esc(line)}</p></header>'
        f'<nav>{nav}<input id="filter" type="search" placeholder="filter: title, alias, id, token, does"></nav>'
        f'{"".join(sections)}<script>{JS}</script></body></html>\n'
    )


def frames_to_copy(cards: list[dict], frames: "FrameIndex | Path") -> list[str]:
    stems: set[str] = set()
    for c in split_recipes(cards)[0]:
        main, strip = resolve_proof((c.get("proof") or {}).get("golden"), frames)
        if main:
            stems.update([main, *strip])
    return sorted(stems)


def copy_if_stale(src: Path, dst: Path) -> bool:
    """Copy one frame only when the copy beside the page is not already it - the gallery re-copied
    19.3 MB of unchanged PNGs on every build. True when it wrote."""
    source = src.stat()
    try:
        have = dst.stat()
    except FileNotFoundError:
        pass
    else:
        if have.st_size == source.st_size and have.st_mtime_ns >= source.st_mtime_ns:
            return False
    dst.write_bytes(src.read_bytes())
    return True


def build(catalog: Path, frames_dir: Path, out_dir: Path) -> tuple[Path, str]:
    cards = load_cards(catalog)
    out_dir.mkdir(parents=True, exist_ok=True)
    target_frames = out_dir / FRAMES_SUBDIR
    target_frames.mkdir(exist_ok=True)
    frames = FrameIndex(frames_dir, clips_dir=target_frames)
    for stem in frames_to_copy(cards, frames):
        copy_if_stale(frames_dir / f"{stem}.png", target_frames / f"{stem}.png")
    line = counts_line(compute_counts(cards, frames))
    index = out_dir / "index.html"
    index.write_bytes(render_page(cards, frames, line).encode("utf-8"))
    return index, line


# ---------------------------------------------------------------- the pinned page (P61 T9 (b))
# "Faster" must never be allowed to mean "renders less", so the built page carries golden frames of
# its own: ONE fixed viewport, three anchors - the top, one mid-page axis section, the foot. They are
# served and captured through render_baseline's own local server (reused, never re-implemented) and
# checked by content/video_engine/tests/test_effects_gallery.py. Refresh deliberately, never by
# accident, the way render_baseline.py --update is run:
#     python content/video_engine/scripts/build_effects_gallery.py --pin
PIN_VIEWPORT = (1280, 900)
PIN_FRAMES = {
    # the header, its counts line and the nav - what the page promises before a card is read
    "gallery-top": "() => window.scrollTo(0, 0)",
    # a mid-page axis section: `kinetics` is the 11th of the 18 axes and 17 cards deep, so the frame
    # holds tiles, their copied golden proofs and the sticky nav over them
    "gallery-axis-kinetics": "() => document.getElementById('axis-kinetics').scrollIntoView(true)",
    # the foot: the end of the recipes section - the last tile the page has to draw
    "gallery-foot": "() => window.scrollTo(0, document.body.scrollHeight)",
}
PIN_SETTLE_MS = 200


def _render_baseline():
    """The golden harness itself - its local server serves the page the frames are captured from."""
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    import render_baseline
    return render_baseline


def capture_frames(page_dir: Path, out_dir: Path, names: list[str] | None = None) -> list[Path]:
    """Screenshot the built page at PIN_VIEWPORT at every anchor of PIN_FRAMES; return what was written.

    Playwright is imported HERE, never at module scope: a build must not pay for the pinning path.
    """
    from playwright.sync_api import sync_playwright
    width, height = PIN_VIEWPORT
    wanted = [n for n in PIN_FRAMES if not names or n in names]
    out_dir.mkdir(parents=True, exist_ok=True)
    srv, port = _render_baseline().serve(page_dir)
    written: list[Path] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": width, "height": height},
                                       device_scale_factor=1).new_page()
            page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle", timeout=180000)
            # the tiles' thumbnails are loading="lazy", so a frame below the fold would screenshot
            # their empty boxes: make every image eager, then wait for all of them and for the fonts
            page.add_style_tag(content="*,*::before,*::after{transition:none!important;animation:none!important}")
            page.evaluate("() => { for (const i of document.images) i.loading = 'eager'; }")
            page.wait_for_function("() => Array.from(document.images).every(i => i.complete)", timeout=180000)
            page.evaluate("document.fonts.ready")
            for name in wanted:
                page.evaluate(PIN_FRAMES[name])
                page.wait_for_timeout(PIN_SETTLE_MS)
                target = out_dir / f"{name}.png"
                target.write_bytes(page.screenshot(type="png"))
                written.append(target)
            browser.close()
    finally:
        srv.shutdown()
    return written


def parse_args(argv: list[str] | None) -> SimpleNamespace:
    """A build with no flags - the one the gallery is rebuilt with - never constructs a parser.

    `argparse` pulls in `shutil`, `gettext` and `locale` the moment a parser is built: 11 ms of a
    111 ms build, and the plain `python build_effects_gallery.py` has nothing to parse. Every
    invocation that does carry a flag still goes through argparse itself, so `--help` stays true.
    """
    flags = sys.argv[1:] if argv is None else argv
    if not flags:
        return SimpleNamespace(catalog=ROOT / CATALOG_REL, frames=ROOT / FRAMES_REL,
                               out=ROOT / OUT_REL, pin=False, pin_into=None)
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--catalog", type=Path, default=ROOT / CATALOG_REL)
    ap.add_argument("--frames", type=Path, default=ROOT / FRAMES_REL)
    ap.add_argument("--out", type=Path, default=ROOT / OUT_REL)
    ap.add_argument("--pin", action="store_true",
                    help="re-capture the page's three golden frames into tests/golden/frames/")
    ap.add_argument("--pin-into", type=Path, help="write the pinned frames here instead (to compare a pair)")
    ap.add_argument("--wait", action="store_true",
                    help="rebuild a stale catalogue and block on it first (P64 T1: the default "
                         "builds the page from what is on disk and names the staleness on stderr)")
    return ap.parse_args(flags)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ensure_catalog(args.catalog, wait=args.wait)
    if not args.catalog.is_file():
        print(f"catalogue not found: {args.catalog}", file=sys.stderr)
        return 2
    index, line = build(args.catalog, args.frames, args.out)
    print(index)
    print(line)
    if args.pin or args.pin_into:
        for path in capture_frames(index.parent, args.pin_into or (ROOT / FRAMES_REL)):
            print(f"pinned {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

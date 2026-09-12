"""PUBLISH PACKAGE - the folder a posting pass reads, written by the build (R26-8, P52 T16).

The row (`docs/content-video-engine/BACKLOG.md:429`): ONE 1440x2560 master per short serves YouTube, Facebook and
Instagram, plus "a publish package per short: the YouTube description, the Facebook description with the link in the
first comment, the pinned-comment text, the tags, the first frame; a `publish/` folder written by the build and a
checklist so a post is one pass across platforms. Scheduling/API posting is out of scope until the package is routine."

    python content/video_engine/scripts/publish_package.py <build> [--project <dir>] [--out <dir>]

Two laws hold this file honest:

1. **No hand text.** Every sentence of copy in the package is a string the build already owns - the spoken sentences
   (`<build>/timeline.json`), the title, the aspect and the on-screen source lines (the compiled `*.timeline.json`),
   the dossier's Sources table and its fetch date (`<project>/EVIDENCE-DOSSIER.md`), the URLs the fetched sources
   carry in their own headers (`<project>/evidence/sources/*`), and the channel's closing line and keywords
   (`channel-assets/<slug>/CHANNEL-DESCRIPTION.md`). What this file contributes is LABELS and order. A hand-written
   description (Tokyo's `SCRIPT-90S-DESCRIPTION.md`) is the fixture this one is measured against and outranks it; the
   tool never reads it and never writes it.
2. **No second render.** The master stays the one the render path already writes (`scripts/render_episode.py`,
   `RENDER_ASPECT=9:16` for a short). The package NAMES that file; it never makes one, and there is no ffmpeg here.

The package regenerates byte-identically: nothing inside a file is dated or timed except from the build's own data
(the dossier's fetch date, the take's runtime), no absolute paths, LF newlines, sorted where the order is not the
script's.

Written by the one-shot bar (`self_watch.py`, stage 8) and runnable on its own against any build; `--out` writes the
package elsewhere so a frozen review build is never touched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHANNEL_ASSETS = HERE.parent / "channel-assets"
PUBLISH_DIR = "publish"
SCHEMA = "publish_package.v1"

HOOK_S = 5.0          # the retention clock: 3 s hook / 10 s answer - the sentences that BEGIN in the first 5 s are the grab
MAX_FIGURES = 6       # the description carries the numbers a viewer can check (E43), not the whole script
MAX_CLOSE = 2         # the ring
MAX_HASHTAGS = 3      # beyond the channel tag and the format tag; Tokyo's hand fixture runs five tags in total
TAGS_CHARS = 500      # YouTube Studio's keyword field
LABEL_CHARS = 100     # a source file's title line is short; its prose header is not
# A spoken figure arrives as WORDS ("a hundred and twenty-two billion", "a tenth of the pile"), so the digit and
# currency classes alone read a VO as figureless. The words below are the recorded take's own vocabulary, not copy.
FIGURE_RE = re.compile(r"[0-9$%¥£€]"
                       r"|\b(?:hundred|thousand|million|billion|trillion|percent|half|tenth|third|quarter|double|twice)\b",
                       re.I)
FORMAT_TAG = {"9:16": ("Shorts", "Reels")}   # (YouTube, Facebook) by aspect; a 16:9 long form carries neither


# ---------------------------------------------------------------- the build's own artifacts
def compiled_timeline(build: Path) -> Path:
    """The compiled `*.timeline.json` (the word timeline is `timeline.json`, which this glob cannot match)."""
    path = next(iter(sorted(build.glob("*.timeline.json"))), None)
    if path is None:
        raise SystemExit(f"no *.timeline.json in {build} - compile the timeline first")
    return path


def _sentences(words_tl: dict) -> list[dict]:
    return [s for s in (words_tl.get("sentences") or []) if str(s.get("text") or "").strip()]


def hook(sents: list[dict]) -> list[str]:
    """The sentences that BEGIN inside the hook window - at least the first one."""
    out = [s["text"].strip() for s in sents if float(s.get("start") or 0.0) < HOOK_S]
    return out or ([sents[0]["text"].strip()] if sents else [])


def figures(sents: list[dict], skip: list[str]) -> list[str]:
    """The spoken sentences that carry a number - the ones a description owes the viewer a source for (E43)."""
    out = [s["text"].strip() for s in sents if FIGURE_RE.search(s["text"]) and s["text"].strip() not in skip]
    return out[:MAX_FIGURES]


def close(sents: list[dict], skip: list[str]) -> list[str]:
    """The ring: the last sentences of the take, unless the hook or the figures already said them."""
    return [s["text"].strip() for s in sents[-MAX_CLOSE:] if s["text"].strip() not in skip]


def onscreen_sources(tl: dict, channel: str = "") -> list[str]:
    """Every CITATION the cut prints: the docks' and the pages' own `source` fields, in first-seen order. Our own
    illustration credit (`@StickMike · Money Physics`) is not a citation, so a line naming the channel is dropped."""
    seen: list[str] = []

    def add(v) -> None:
        s = str(v or "").strip()
        if s and s not in seen and not (channel and channel.lower() in s.lower()):
            seen.append(s)

    for ev in (tl.get("evidence") or {}).values():
        add((ev or {}).get("source"))
    for sc in tl.get("scenes") or []:
        world = (sc or {}).get("world") or {}
        add((world.get("page") or {}).get("source"))
        for st in world.get("page_states") or []:
            add((st or {}).get("source"))
    return seen


# ---------------------------------------------------------------- the dossier and the fetched sources
def dossier_rows(md: str) -> list[dict]:
    """The `## Sources` table of an evidence dossier -> [{id, what, cadence}] (the row IS the citation)."""
    rows: list[dict] = []
    inside = False
    for line in md.splitlines():
        if re.match(r"^#{2,}\s+Sources\b", line.strip()):
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if inside and line.strip().startswith("|"):
            cells = [c.replace("`", "").strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and not cells[0].startswith("---") and cells[0].lower() != "id":
                rows.append({"id": cells[0], "what": cells[1], "cadence": cells[2]})
    return rows


def dossier_fetched(md: str) -> str | None:
    """The dossier's own fetch date - the one date in the package, and it is the build's data, not the clock."""
    m = re.search(r"[Ff]etched\s+(\d{4}-\d{2}-\d{2})", md)
    return m.group(1) if m else None


def _label(head: str, path: Path) -> str:
    """A fetched source's own name: its `Title:` header, else its first title-shaped line - short, not a header, not a
    table row, and not the end of a sentence (a fetch note wraps into lines that close on punctuation; a title does
    not) - else the file stem."""
    t = re.search(r"^Title:\s*(.+)$", head, re.M | re.I)
    if t:
        return " ".join(t.group(1).split())
    for line in head.splitlines():
        s = " ".join(line.split())
        if not s or len(s) > LABEL_CHARS or s.startswith("|") or s.endswith((".", ",", ";", ":")):
            continue
        if not re.match(r"^(URL|Link|Title|Byline|SOURCE)\b", s, re.I):
            return s
    return path.stem


def fetched_links(project: Path) -> list[dict]:
    """[{label, url}] from the fetched sources' OWN headers (`URL:` / `Link:`, `Title:`) - never a scraped link."""
    src = project / "evidence" / "sources"
    out: list[dict] = []
    urls: set[str] = set()
    for path in sorted(src.glob("*")) if src.is_dir() else []:
        if not path.is_file():
            continue
        head = path.read_text(encoding="utf-8", errors="replace")[:4096]
        m = re.search(r"^(?:URL|Link):\s*(\S+)", head, re.M | re.I)
        if not m or m.group(1) in urls:
            continue
        urls.add(m.group(1))
        out.append({"label": _label(head, path), "url": m.group(1)})
    return out


# ---------------------------------------------------------------- the channel's own words
def channel_name(subtitle: str, episode_id: str) -> str:
    """`Money Physics - short` -> `Money Physics` (the compiled timeline's subtitle names the channel)."""
    return re.split(r"[·|•]", subtitle or "")[0].strip() or episode_id


def channel_slug(subtitle: str, episode_id: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", channel_name(subtitle, episode_id).lower()).strip("-")


def _fenced(md: str, heading_re: str) -> str | None:
    """The first fenced block after a heading that matches (the house pattern: `## X (paste ...)` then a fence)."""
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if re.match(heading_re, line.strip(), re.I):
            block: list[str] = []
            open_ = False
            for l in lines[i + 1:]:
                if l.startswith("```"):
                    if open_:
                        return "\n".join(block).strip()
                    open_ = True
                    continue
                if open_:
                    block.append(l)
            break
    return None


def channel_text(slug: str) -> dict:
    """The channel's closing line (the last line of its About paste) and its keyword list - its own file or nothing."""
    path = CHANNEL_ASSETS / slug / "CHANNEL-DESCRIPTION.md"
    if not path.is_file():
        return {"path": None, "line": None, "keywords": []}
    md = path.read_text(encoding="utf-8")
    about = _fenced(md, r"^#{2,}\s+Description\b") or ""
    line = next((l.strip() for l in reversed(about.splitlines()) if l.strip()), None)
    kw = _fenced(md, r"^#{2,}\s+Channel keywords\b") or ""
    keywords = [k.strip() for k in kw.replace("\n", " ").split(",") if k.strip()]
    return {"path": "channel-assets/" + slug + "/CHANNEL-DESCRIPTION.md", "line": line, "keywords": keywords}


def camel(s: str) -> str:
    return "".join(w[:1].upper() + w[1:] for w in re.split(r"[^A-Za-z0-9]+", s) if w)


def hashtags(facts: dict) -> list[str]:
    """#Channel + #Title + the channel keywords the episode's OWN text uses + the format tag. Nothing invented."""
    body = " ".join([*facts.get("spoken", []), *facts["onscreen"],
                     *(r["what"] for r in facts["dossier"])]).lower()
    tags = ["#" + camel(facts["channel"]), "#" + camel(facts["title"])]
    for k in facts["channel_keywords"]:
        if len(tags) > MAX_HASHTAGS:
            break
        tag = "#" + camel(k)
        if k.lower() in body and tag not in tags:
            tags.append(tag)
    fmt = FORMAT_TAG.get(facts["aspect"])
    return tags + (["#" + fmt[0]] if fmt else [])


def keyword_line(facts: dict) -> str:
    """The Studio keyword field: the episode's own title first, then the channel's keywords, to the field's limit."""
    out: list[str] = []
    for w in [facts["title"].lower(), *facts["channel_keywords"]]:
        if w not in out and len(", ".join([*out, w])) <= TAGS_CHARS:
            out.append(w)
    return ", ".join(out)


# ---------------------------------------------------------------- the facts (every file below is a view of this)
def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _first_frame(build: Path) -> Path | None:
    """The 0:00 frame the self-watch already grabbed (`self-watch/<row>-0000.0.png`) - never a new capture."""
    tiles = sorted((build / "self-watch").glob("*-0000.0.png")) if (build / "self-watch").is_dir() else []
    return tiles[0] if tiles else None


def _thumbnail(build: Path, project: Path) -> Path | None:
    cands = [p for d in (build, project / "packaging", project) if d.is_dir()
             for p in sorted(d.glob("*thumb*.png")) if p.is_file()]
    return cands[0] if cands else None


def _master(build: Path) -> Path | None:
    """The rendered master already on disk: the full-length 1440p file the render path writes. Never rendered here."""
    render = build / "render"
    mp4s = sorted(render.glob("*.mp4")) if render.is_dir() else []
    for pick in ([p for p in mp4s if "full" in p.name and "1440" in p.name],
                 [p for p in mp4s if "full" in p.name]):
        if pick:
            return pick[0]
    return None


def read_build(build: Path, project: Path | None = None) -> dict:
    """Every string the package is written from, and what was missing when it was written."""
    build = Path(build).resolve()
    project = Path(project).resolve() if project else build.parent
    words_tl = json.loads((build / "timeline.json").read_text(encoding="utf-8"))
    tl_path = compiled_timeline(build)
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    sents = _sentences(words_tl)
    h = hook(sents)
    f = figures(sents, skip=h)
    subtitle = str(tl.get("subtitle") or "")
    episode = str(tl.get("episode_id") or words_tl.get("episode") or project.name)
    channel = channel_name(subtitle, episode)
    slug = channel_slug(subtitle, episode)
    ch = channel_text(slug)
    dossier_path = project / "EVIDENCE-DOSSIER.md"
    dossier_md = dossier_path.read_text(encoding="utf-8") if dossier_path.is_file() else ""
    master, frame, thumb = _master(build), _first_frame(build), _thumbnail(build, project)
    facts = {
        "schema": SCHEMA,
        "episode": episode, "project": project.name, "build": build.name,
        "title": str(tl.get("title") or episode), "subtitle": subtitle,
        "channel": channel, "channel_slug": slug,
        "channel_line": ch["line"], "channel_keywords": ch["keywords"], "channel_path": ch["path"],
        "aspect": str(tl.get("aspect") or "16:9"), "runtime_s": round(float(words_tl.get("runtime_s") or 0.0), 3),
        "script": str(words_tl.get("script") or ""), "take": str(words_tl.get("take") or ""),
        "hook": h, "figures": f, "close": close(sents, skip=h + f),
        "spoken": [s["text"].strip() for s in sents],
        "onscreen": onscreen_sources(tl, channel),
        "dossier": dossier_rows(dossier_md), "fetched": dossier_fetched(dossier_md),
        "links": fetched_links(project),
        "master": master.name if master else None,
        "master_bytes": master.stat().st_size if master else None,
        "first_frame": frame.name if frame else None,
        "thumbnail": thumb.name if thumb else None,
        "inputs": {"build:timeline.json": _sha(build / "timeline.json"), "build:" + tl_path.name: _sha(tl_path)},
        "_paths": {"frame": frame, "thumb": thumb},
    }
    if dossier_md:
        facts["inputs"]["project:EVIDENCE-DOSSIER.md"] = _sha(dossier_path)
    if ch["path"]:
        facts["inputs"]["repo:" + ch["path"]] = _sha(CHANNEL_ASSETS / slug / "CHANNEL-DESCRIPTION.md")
    facts["missing"] = [name for name, got in (
        ("the evidence dossier (EVIDENCE-DOSSIER.md)", dossier_md),
        ("the channel's own words (channel-assets/" + slug + "/CHANNEL-DESCRIPTION.md)", ch["line"]),
        ("the fetched sources' links (evidence/sources/*)", facts["links"]),
        ("the 1440p master (render/)", master),
        ("the first frame (self-watch/*-0000.0.png)", frame),
        ("the thumbnail (*thumb*.png)", thumb)) if not got]
    facts["tags"] = hashtags(facts)
    facts["keywords"] = keyword_line(facts)
    return facts


# ---------------------------------------------------------------- the copy (labels and order; the strings are the build's)
def _fetched_suffix(facts: dict) -> str:
    return " (fetched " + facts["fetched"] + ")" if facts["fetched"] else ""


def _rows(facts: dict) -> list[str]:
    return [f"- {r['what']} ({r['cadence']}) - {r['id']}" for r in facts["dossier"]]


def _links(facts: dict) -> list[str]:
    return [f"- {l['label']}: {l['url']}" for l in facts["links"]]


def sources_block(facts: dict) -> list[str]:
    """The citations block both descriptions carry: the dossier's rows, the URLs on disk, the lines the cut printed."""
    out: list[str] = []
    if facts["dossier"]:
        out += ["Sources" + _fetched_suffix(facts) + ":"] + _rows(facts)
    if facts["links"]:
        out += ([""] if out else []) + ["Read them yourself:"] + _links(facts)
    if facts["onscreen"]:
        out += ([""] if out else []) + ["On screen: " + "; ".join(facts["onscreen"])]
    return out


def _paras(facts: dict) -> list[str]:
    return [p for p in (" ".join(facts["hook"]), " ".join(facts["figures"]), " ".join(facts["close"])) if p]


def youtube_description(facts: dict) -> str:
    blocks = ["\n\n".join(_paras(facts))]
    src = sources_block(facts)
    if src:
        blocks.append("\n".join(src))
    if facts["channel_line"]:
        blocks.append(facts["channel_line"])
    blocks.append(" ".join(facts["tags"]))
    return "\n\n".join(blocks) + "\n"


def facebook_description(facts: dict) -> str:
    """The same body; the links move to the first comment (a feed post buries a link in the caption)."""
    blocks = ["\n\n".join(_paras(facts))]
    src: list[str] = []
    if facts["dossier"]:
        src += ["Sources" + _fetched_suffix(facts) + ":"] + _rows(facts)
    if facts["onscreen"]:
        src += ([""] if src else []) + ["On screen: " + "; ".join(facts["onscreen"])]
    if src:
        blocks.append("\n".join(src))
    if facts["links"]:
        blocks.append("Links in the first comment.")
    if facts["channel_line"]:
        blocks.append(facts["channel_line"])
    fmt = FORMAT_TAG.get(facts["aspect"])
    tags = [t for t in facts["tags"] if not (fmt and t == "#" + fmt[0])] + (["#" + fmt[1]] if fmt else [])
    blocks.append(" ".join(tags))
    return "\n\n".join(blocks) + "\n"


def first_comment(facts: dict) -> str:
    return "\n".join(f"{l['label']}: {l['url']}" for l in facts["links"]) + "\n" if facts["links"] else ""


def pinned_comment(facts: dict) -> str:
    """The source note: every figure's source, its cadence and the date it was fetched - the rows, nothing added."""
    out = ["Every figure in this video, with its source" + _fetched_suffix(facts) + ":"]
    out += _rows(facts) or [f"- {s}" for s in facts["onscreen"]]
    if facts["links"]:
        out += ["", "Read them yourself:"] + _links(facts)
    return "\n".join(out) + "\n"


def _header(facts: dict, what: str) -> list[str]:
    m, s = divmod(int(round(facts["runtime_s"])), 60)
    return [f"# {facts['title']} - {what} ({facts['channel']})", "",
            "Written by `publish_package.py` from `" + facts["build"] + "`'s own artifacts - the take's sentences, "
            "the compiled timeline's title, aspect and source lines, the dossier's Sources table, the fetched "
            "sources' own URL headers, the channel's About paste. No hand text: every line inside the block below is "
            "a build artifact. A hand-written description for this episode outranks this one.", "",
            f"`{facts['episode']}` - {facts['aspect']} - {m}:{s:02d} - script `{facts['script']}` - take "
            f"`{facts['take']}`", ""]


def youtube_doc(facts: dict) -> str:
    return "\n".join(_header(facts, "the YouTube description") +
                     ["## Title (paste into the title field)", "", "```", facts["title"], "```", "",
                      "## Description (paste as-is)", "", "```", youtube_description(facts).rstrip("\n"), "```", ""])


def facebook_doc(facts: dict) -> str:
    out = _header(facts, "the Facebook / Instagram description")
    out += ["## Description (paste as-is)", "", "```", facebook_description(facts).rstrip("\n"), "```", ""]
    if facts["links"]:
        out += ["## First comment (post it immediately - the link lives here, not in the caption)", "",
                "```", first_comment(facts).rstrip("\n"), "```", ""]
    return "\n".join(out)


def pinned_doc(facts: dict) -> str:
    return "\n".join(_header(facts, "the pinned comment") +
                     ["## Pinned comment (post right after publishing, then pin it)", "",
                      "```", pinned_comment(facts).rstrip("\n"), "```", ""])


def sources_doc(facts: dict) -> str:
    block = "\n".join(sources_block(facts)) or "(no dossier, no fetched link, no on-screen source line)"
    return "\n".join(_header(facts, "the sources block") +
                     ["## The block both descriptions carry", "", "```", block, "```", ""])


def tags_text(facts: dict) -> str:
    return "\n".join([f"keywords (YouTube Studio -> Settings -> Tags; {len(facts['keywords'])}/{TAGS_CHARS} chars)",
                      facts["keywords"], "",
                      "hashtags (the description's last line)",
                      " ".join(facts["tags"]), ""])


CHECKLIST_STEPS = (
    "Upload the master to the channel: the title from `DESCRIPTION-YOUTUBE.md` (`## Title`), the description from its "
    "paste block.",
    "Upload the thumbnail (`thumbnail.png` here when the build carries one). `first-frame.png` is what the platform "
    "would pick on its own - it is evidence, not a thumbnail.",
    "Set the keywords from `TAGS.txt`, the playlist, the audience ('not made for kids') and the language.",
    "Publish, or set the schedule yourself - this tool never schedules and never posts (R26-8 draws the line there).",
    "Post `PINNED-COMMENT.md` as a comment and pin it. A Short's links are not clickable, so the URL rides as text.",
    "Facebook and Instagram: the SAME master file, the caption from `DESCRIPTION-FACEBOOK.md`, and the link as the "
    "FIRST COMMENT (`## First comment`).",
    "Read the description once against the episode's hand-written one, if it has one, and against the dossier: this "
    "package copies figures, it does not check them.",
)


def checklist(facts: dict) -> str:
    """One page: what a human still does. The tool's line is drawn at scheduling and API posting (R26-8)."""
    m, s = divmod(int(round(facts["runtime_s"])), 60)
    master = ("`render/" + facts["master"] + f"` ({facts['master_bytes'] / 1e6:.1f} MB)" if facts["master"]
              else "NOT RENDERED YET - `RENDER_ASPECT=9:16 python content/video_engine/scripts/render_episode.py` "
                   "(the existing path; one master, no second size)")
    out = [f"# Publish checklist - {facts['title']} ({facts['channel']}) - `{facts['build']}`", "",
           f"{facts['aspect']} - {m}:{s:02d} - every step below is a HUMAN's. The package is written from the build's "
           "own artifacts; scheduling and API posting are out of scope (R26-8).", "",
           "**The master:** " + master + " - ONE file serves YouTube, Facebook and Instagram (R26-8: the platform "
           "assigns the better codec at 1440p+ and the same upload travels). Never render a per-platform size.", ""]
    out += [f"- [ ] {i}. {step}" for i, step in enumerate(CHECKLIST_STEPS, start=1)]
    out += ["", "**In this folder:** `DESCRIPTION-YOUTUBE.md`, `DESCRIPTION-FACEBOOK.md`, `PINNED-COMMENT.md`, "
            "`SOURCES.md`, `TAGS.txt`, `MANIFEST.json`"
            + (", `first-frame.png`" if facts["first_frame"] else "")
            + (", `thumbnail.png`" if facts["thumbnail"] else "") + ".", ""]
    if facts["missing"]:
        out += ["**Not on disk when this was written** (the package is thinner for it):"]
        out += [f"- {name}" for name in facts["missing"]] + [""]
    return "\n".join(out)


def manifest(facts: dict) -> str:
    """What the package was written from - relative labels and short hashes only, so it is byte-stable anywhere."""
    keep = ("schema", "episode", "project", "build", "title", "subtitle", "channel", "channel_slug", "channel_line",
            "channel_path", "aspect", "runtime_s", "script", "take", "master", "master_bytes", "first_frame",
            "thumbnail", "fetched", "keywords", "tags", "inputs", "missing")
    data = {k: facts[k] for k in keep}
    data["counts"] = {"hook": len(facts["hook"]), "figures": len(facts["figures"]), "close": len(facts["close"]),
                      "dossier_sources": len(facts["dossier"]), "links": len(facts["links"]),
                      "onscreen_sources": len(facts["onscreen"])}
    return json.dumps(data, indent=1, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------- the folder
FILES = ("DESCRIPTION-YOUTUBE.md", "DESCRIPTION-FACEBOOK.md", "PINNED-COMMENT.md", "SOURCES.md", "TAGS.txt",
         "CHECKLIST.md", "MANIFEST.json")


def write_package(build: Path, project: Path | None = None, out: Path | None = None) -> Path:
    """Write `<build>/publish/` (or `<out>/`) from the build's own artifacts. Returns the folder."""
    build = Path(build).resolve()
    facts = read_build(build, project)
    dest = Path(out).resolve() if out else build / PUBLISH_DIR
    dest.mkdir(parents=True, exist_ok=True)
    for name, text in (("DESCRIPTION-YOUTUBE.md", youtube_doc(facts)),
                       ("DESCRIPTION-FACEBOOK.md", facebook_doc(facts)),
                       ("PINNED-COMMENT.md", pinned_doc(facts)),
                       ("SOURCES.md", sources_doc(facts)),
                       ("TAGS.txt", tags_text(facts)),
                       ("CHECKLIST.md", checklist(facts)),
                       ("MANIFEST.json", manifest(facts))):
        (dest / name).write_bytes(text.encode("utf-8"))            # bytes, not write_text: LF on every platform
    for name, src in (("first-frame.png", facts["_paths"]["frame"]), ("thumbnail.png", facts["_paths"]["thumb"])):
        if src is not None:
            shutil.copyfile(src, dest / name)
        elif (dest / name).exists():
            (dest / name).unlink()                                  # a stale copy is a lie about this build
    return dest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("build", type=Path)
    ap.add_argument("--project", type=Path, default=None, help="the episode dir (default: the build's parent)")
    ap.add_argument("--out", type=Path, default=None,
                    help="write the package here instead of <build>/publish (a frozen build stays untouched)")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    dest = write_package(args.build, args.project, args.out)
    print(dest)
    for p in sorted(dest.iterdir()):
        print(f"  {p.name:24s} {p.stat().st_size:>8d} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

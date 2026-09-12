"""THE PRESS CARD (P50 T3; doc 29 §9.27 "Push hand-off"; SPECIES-BY-SENTENCE row 1 QUOTES).

A screenshot of a published page is not a card. This tool crops one to its HEADLINE, sizes the
crop to the dock's own width, and declares two things the card cannot carry in its pixels:

  * the SOURCE line - the masthead and the date, stamped on the card by the player in the record
    document's header type (B1: their claim is a card, and the card says whose claim it is);
  * the PHRASE box - the region of the quoted headline the sentence turns on, re-expressed as
    FRACTIONS of the card so it survives every scale the card is drawn at. It is what a
    `callout` with `form: "underline"` underlines (E56's one exception: an underline on a quoted
    phrase is the squiggle law, never a ring);
  * the PHRASE'S WORDS (R26-55) - the same phrase as TEXT, so the player can set it as LIVE TYPE
    re-lined to whatever surface the card lands on. A raster cannot re-line: on a tall poster the
    crop keeps the source page's own line breaks and the phrase reads at 13.4 CSS px on a phone
    against E62's 17 (E66's own recorded limit). With the words on the card the player fits them
    to the box and the CROP STAYS as the provenance strip beneath them - still visible, still the
    file whose sha256 is recorded here, still cited by the source line.

    python press_card.py shot.png --headline-box 120,340,1680,520 --source "Reuters, 12 Mar 2026" \\
        --phrase-box 610,360,1180,505 --out evidence/objects/ev-press-reuters.png \\
        --phrase-text "the historic normal was never normal" \\
        --meta evidence/objects/ev-press-reuters.press.json

Boxes are SOURCE-PIXEL coordinates (x0, y0, x1, y1) read off the screenshot. The crop is the
headline box grown by `--margin` on every side and clamped to the image, so the headline keeps
its paper around it. Pure PIL and the standard library: nothing here reaches the network, and the
screenshot is never modified.

The meta JSON is what a shot row hands the compiler as a dock's ``press`` option:

    {"kind": "press", "source": "...", "phrase": {"x0": .., "y0": .., "x1": .., "y1": ..},
     "phrase_text": "...", "crop": [x0, y0, x1, y1], "card": [w, h],
     "screenshot": {"name": "...", "sha256": "..."}}

The provenance keys (`crop`, `screenshot`) are the A2a habit - the card names the file it was cut
from and the rectangle it was cut at; the compiler reads `kind`, `source`, `phrase`, `phrase_text`
and the card's own aspect (from `card`) only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# THE CARD'S WIDTH IS THE DOCK'S. The player's solo card is 1056 px on a 1920 stage (.dock.solo)
# and 800 px on a 1080 one (html[data-aspect="9:16"] .dock); the frame's border and the dock's
# padding take ~40 px back inside that, so a card written at these widths is never UPSCALED on
# stage - the one direction that costs a headline its legibility.
CARD_W = {"16:9": 1056, "9:16": 800}
MARGIN_DEFAULT = 16       # source px of paper kept around the headline: enough to read as a cutting, not a crop
PHRASE_ROUND = 5          # fractions to five places - a card is at most ~1100 px wide, so this is sub-pixel
PHRASE_WORDS_MIN = 2      # R26-55: a pulled phrase is words, not a label - one word is a ring's job (E56), not a headline's


def parse_box(raw: str, name: str) -> tuple[int, int, int, int]:
    """``"x0,y0,x1,y1"`` -> four ints. ValueError names the flag."""
    parts = [p.strip() for p in str(raw).split(",")]
    if len(parts) != 4:
        raise ValueError(f"{name} must be x0,y0,x1,y1 in source pixels, not {raw!r}")
    try:
        x0, y0, x1, y1 = (int(round(float(p))) for p in parts)
    except ValueError as exc:
        raise ValueError(f"{name} must be four numbers in source pixels, not {raw!r}") from exc
    if x1 <= x0 or y1 <= y0:
        raise ValueError(f"{name} is empty or inverted: x0<x1 and y0<y1 required, got {x0},{y0},{x1},{y1}")
    return x0, y0, x1, y1


def crop_box(headline: tuple[int, int, int, int], margin: int, size: tuple[int, int]) -> tuple[int, int, int, int]:
    """The headline box grown by `margin` and clamped to the screenshot - the paper around the words."""
    w, h = size
    x0, y0, x1, y1 = headline
    return (max(0, x0 - margin), max(0, y0 - margin), min(w, x1 + margin), min(h, y1 + margin))


def phrase_fractions(phrase: tuple[int, int, int, int], crop: tuple[int, int, int, int]) -> dict:
    """The phrase box re-expressed as fractions OF THE CARD. Refuses a phrase outside the crop:
    an underline drawn off the card is a bug the compiler cannot see."""
    cx0, cy0, cx1, cy1 = crop
    px0, py0, px1, py1 = phrase
    if not (cx0 <= px0 and cy0 <= py0 and px1 <= cx1 and py1 <= cy1):
        raise ValueError(f"--phrase-box {px0},{py0},{px1},{py1} is not inside the cropped card "
                         f"{cx0},{cy0},{cx1},{cy1} - the phrase is a region OF the headline")
    w, h = cx1 - cx0, cy1 - cy0
    return {"x0": round((px0 - cx0) / w, PHRASE_ROUND), "y0": round((py0 - cy0) / h, PHRASE_ROUND),
            "x1": round((px1 - cx0) / w, PHRASE_ROUND), "y1": round((py1 - cy0) / h, PHRASE_ROUND)}


def phrase_words(text) -> str:
    """The phrase's WORDS as the card carries them (R26-55): whitespace collapsed, nothing else touched - the
    words are the operator's, and the player re-lines them at whatever size the surface allows. Refuses a phrase
    of fewer than PHRASE_WORDS_MIN words, which is the mistake this flag invites (a label, not a headline)."""
    words = str("" if text is None else text).split()
    if len(words) < PHRASE_WORDS_MIN:
        raise ValueError(f"--phrase-text must be the quoted phrase's own words ({PHRASE_WORDS_MIN} or more), "
                         f"not {str(text)!r} - it is what the player sets as live type over the provenance strip")
    return " ".join(words)


def build_card(shot: Path, headline: tuple[int, int, int, int], phrase: tuple[int, int, int, int],
               source: str, aspect: str = "16:9", margin: int = MARGIN_DEFAULT, text: str | None = None):
    """(the card image, the meta dict). Pure: nothing is written here."""
    from PIL import Image   # imported here so `--help` and the box parsers run without PIL

    if not str(source).strip():
        raise ValueError("--source must name the masthead and the date - a press card without its source is not evidence")
    if aspect not in CARD_W:
        raise ValueError(f"--aspect must be one of {'|'.join(sorted(CARD_W))}")
    with Image.open(shot) as im:
        im = im.convert("RGB")
        box = crop_box(headline, margin, im.size)
        card = im.crop(box)
    frac = phrase_fractions(phrase, box)
    target_w = CARD_W[aspect]
    if card.width != target_w:                      # LANCZOS both ways: a headline is type, and type is what ringing shows on
        card = card.resize((target_w, max(1, round(card.height * target_w / card.width))), Image.LANCZOS)
    meta = {"kind": "press", "source": str(source).strip(), "phrase": frac,
            "phrase_text": phrase_words(text),   # R26-55: the words beside the raster, for the player's live type
            "crop": list(box), "card": [card.width, card.height],
            "screenshot": {"name": shot.name, "sha256": hashlib.sha256(shot.read_bytes()).hexdigest()}}
    return card, meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Crop a screenshot to its headline: the press card and its meta (P50 T3)")
    ap.add_argument("screenshot", type=Path)
    ap.add_argument("--headline-box", required=True, help="x0,y0,x1,y1 of the headline in SOURCE pixels")
    ap.add_argument("--phrase-box", required=True, help="x0,y0,x1,y1 of the quoted phrase, inside the headline box")
    ap.add_argument("--phrase-text", required=True,
                    help="the quoted phrase's own WORDS - set as live type on the card, re-lined to its surface (R26-55)")
    ap.add_argument("--source", required=True, help='the masthead and the date, e.g. "Reuters, 12 Mar 2026"')
    ap.add_argument("--out", required=True, type=Path, help="the card PNG")
    ap.add_argument("--meta", required=True, type=Path, help="the card's meta JSON (the dock's `press` option)")
    ap.add_argument("--aspect", default="16:9", choices=sorted(CARD_W))
    ap.add_argument("--margin", type=int, default=MARGIN_DEFAULT, help="source px of paper kept around the headline")
    a = ap.parse_args(argv)
    try:
        if not a.screenshot.exists():
            raise ValueError(f"{a.screenshot} does not exist")
        if a.margin < 0:
            raise ValueError("--margin must be >= 0")
        card, meta = build_card(a.screenshot, parse_box(a.headline_box, "--headline-box"),
                                parse_box(a.phrase_box, "--phrase-box"), a.source, a.aspect, a.margin,
                                a.phrase_text)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.meta.parent.mkdir(parents=True, exist_ok=True)
    card.save(a.out, "PNG")
    a.meta.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"card  {a.out}  {meta['card'][0]}x{meta['card'][1]}")
    print(f"meta  {a.meta}  phrase {meta['phrase']}")
    print(f"words {meta['phrase_text']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

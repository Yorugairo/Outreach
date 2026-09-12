"""THE PRESS CARD CROP TOOL (P50 T3): a screenshot in, a card at the dock's width and its meta out.

The tool is the authoring half of the press dock - the compiler reads the meta it writes (test_press_dock)
and the player paints the card and underlines the phrase box it declares. These tests run the CLI itself on a
synthetic page: the geometry it computes, the widths it writes, and every refusal by name.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import press_card as PC  # noqa: E402

PIL = pytest.importorskip("PIL.Image", reason="PIL is the tool's one dependency")

PAGE = (1600, 900)
HEADLINE = (200, 300, 1400, 520)     # the headline block on the synthetic page
PHRASE = (500, 340, 1000, 500)       # the quoted phrase inside it
WORDS = "the historic normal was never normal"   # R26-55: the same phrase as words, for the player's live type
PAPER, INK, CHROME = (250, 247, 240), (28, 34, 42), (180, 40, 40)


@pytest.fixture()
def shot(tmp_path: Path) -> Path:
    """A synthetic published page: red chrome everywhere, paper under the headline, ink on the phrase."""
    from PIL import Image, ImageDraw
    im = Image.new("RGB", PAGE, CHROME)
    d = ImageDraw.Draw(im)
    d.rectangle([HEADLINE[0] - 40, HEADLINE[1] - 40, HEADLINE[2] + 40, HEADLINE[3] + 40], fill=PAPER)
    d.rectangle(list(PHRASE), fill=INK)
    p = tmp_path / "shot.png"
    im.save(p, "PNG")
    return p


def _run(shot: Path, tmp_path: Path, **kw) -> tuple[int, dict | None, Path]:
    out, meta = tmp_path / "card.png", tmp_path / "card.json"
    argv = [str(shot), "--headline-box", kw.get("headline", "200,300,1400,520"),
            "--phrase-box", kw.get("phrase", "500,340,1000,500"),
            "--source", kw.get("source", "The Herald, 4 Mar 2026"),
            "--phrase-text", kw.get("text", WORDS),
            "--out", str(out), "--meta", str(meta)]
    if "aspect" in kw:
        argv += ["--aspect", kw["aspect"]]
    if "margin" in kw:
        argv += ["--margin", str(kw["margin"])]
    code = PC.main(argv)
    return code, (json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else None), out


def test_the_card_is_cropped_to_the_headline_at_the_landscape_docks_width(shot: Path, tmp_path: Path):
    from PIL import Image
    code, meta, out = _run(shot, tmp_path)
    assert code == 0
    assert meta["kind"] == "press" and meta["source"] == "The Herald, 4 Mar 2026"
    with Image.open(out) as card:
        assert card.width == PC.CARD_W["16:9"] == 1056, "the card is written at the solo dock's width"
        w, h = HEADLINE[2] - HEADLINE[0] + 2 * PC.MARGIN_DEFAULT, HEADLINE[3] - HEADLINE[1] + 2 * PC.MARGIN_DEFAULT
        assert card.height == round(h * card.width / w), "the crop keeps its aspect"
        assert card.getpixel((6, 6))[0] > 200, "the paper around the headline came with it - not the page's chrome"
    assert meta["crop"] == [HEADLINE[0] - PC.MARGIN_DEFAULT, HEADLINE[1] - PC.MARGIN_DEFAULT,
                            HEADLINE[2] + PC.MARGIN_DEFAULT, HEADLINE[3] + PC.MARGIN_DEFAULT]


def test_the_phrase_is_written_as_fractions_of_the_card(shot: Path, tmp_path: Path):
    _code, meta, _out = _run(shot, tmp_path)
    x0, y0, x1, y1 = meta["crop"]
    want = {"x0": (PHRASE[0] - x0) / (x1 - x0), "y0": (PHRASE[1] - y0) / (y1 - y0),
            "x1": (PHRASE[2] - x0) / (x1 - x0), "y1": (PHRASE[3] - y0) / (y1 - y0)}
    for k, v in want.items():
        assert meta["phrase"][k] == pytest.approx(v, abs=1e-5), k
        assert 0.0 <= meta["phrase"][k] <= 1.0
    assert meta["phrase"]["x0"] < meta["phrase"]["x1"] and meta["phrase"]["y0"] < meta["phrase"]["y1"]


def test_the_portrait_card_is_written_at_the_portrait_docks_width(shot: Path, tmp_path: Path):
    from PIL import Image
    code, meta, out = _run(shot, tmp_path, aspect="9:16")
    assert code == 0 and meta["card"][0] == PC.CARD_W["9:16"] == 800
    with Image.open(out) as card:
        assert card.width == 800
    # the phrase is the SAME region of the card either way: fractions do not care how wide the card is
    _c, land, _o = _run(shot, tmp_path)
    assert meta["phrase"] == land["phrase"]


def test_a_phrase_outside_the_headline_is_refused_by_name(shot: Path, tmp_path: Path, capsys):
    code, meta, _out = _run(shot, tmp_path, phrase="500,340,1500,500")
    assert code == 2 and meta is None
    err = capsys.readouterr().err
    assert "is not inside the cropped card" in err and "region OF the headline" in err


def test_a_card_without_a_source_is_refused_by_name(shot: Path, tmp_path: Path, capsys):
    code, _meta, _out = _run(shot, tmp_path, source="   ")
    assert code == 2 and "a press card without its source is not evidence" in capsys.readouterr().err


@pytest.mark.parametrize("box, needle", [
    ("200,300,1400", "must be x0,y0,x1,y1 in source pixels"),
    ("200,300,1400,x", "must be four numbers in source pixels"),
    ("1400,300,200,520", "empty or inverted"),
    ("200,520,1400,300", "empty or inverted"),
])
def test_a_malformed_box_is_refused_by_name(shot: Path, tmp_path: Path, capsys, box, needle):
    code, _meta, _out = _run(shot, tmp_path, headline=box)
    assert code == 2 and needle in capsys.readouterr().err


def test_a_missing_screenshot_is_refused_and_nothing_is_written(tmp_path: Path, capsys):
    code, meta, out = _run(tmp_path / "nope.png", tmp_path)
    assert code == 2 and meta is None and not out.exists()
    assert "does not exist" in capsys.readouterr().err


def test_the_crop_clamps_to_the_page_and_the_screenshot_is_recorded(shot: Path, tmp_path: Path):
    code, meta, _out = _run(shot, tmp_path, headline="0,0,1600,900", phrase="10,10,200,200", margin=64)
    assert code == 0 and meta["crop"] == [0, 0, PAGE[0], PAGE[1]], "the margin never runs off the page"
    assert meta["screenshot"]["name"] == "shot.png" and len(meta["screenshot"]["sha256"]) == 64


def test_the_geometry_is_a_pure_function_the_tests_can_call_without_pixels():
    assert PC.crop_box((100, 100, 200, 200), 20, (1000, 1000)) == (80, 80, 220, 220)
    assert PC.crop_box((10, 10, 200, 200), 20, (150, 150)) == (0, 0, 150, 150)
    assert PC.phrase_fractions((50, 100, 150, 200), (0, 0, 200, 400)) == {"x0": 0.25, "y0": 0.25, "x1": 0.75, "y1": 0.5}
    with pytest.raises(ValueError):
        PC.phrase_fractions((50, 100, 250, 200), (0, 0, 200, 400))


# ---- R26-55: THE PHRASE'S WORDS BESIDE THE RASTER ------------------------------------------------
# A crop cannot re-line, so the card carries the phrase as TEXT as well as pixels: the player sets the words
# at the size the surface allows and keeps the crop as the provenance strip under them. The tool's half of that
# is one field and two refusals.


def test_the_card_carries_the_phrases_words_beside_the_raster(shot: Path, tmp_path: Path):
    code, meta, out = _run(shot, tmp_path)
    assert code == 0 and meta["phrase_text"] == WORDS, "the words travel as data, in the operator's own order"
    assert out.exists(), "and the crop is still written - the raster is the provenance strip, not a discard"
    assert meta["screenshot"]["sha256"] and meta["crop"], "which is still the file and rectangle it was cut at"
    assert meta["card"] == [PC.CARD_W["16:9"], meta["card"][1]], "the card's own size is on record for the strip's aspect"


def test_the_words_are_collapsed_and_never_otherwise_touched(shot: Path, tmp_path: Path):
    _code, meta, _out = _run(shot, tmp_path, text="  the historic\n  normal   was  never normal ")
    assert meta["phrase_text"] == WORDS, "whitespace collapsed; the words themselves are the operator's"
    assert PC.phrase_words("A B") == "A B" and PC.phrase_words("  two words  ") == "two words"


@pytest.mark.parametrize("text", ["", "   ", "normal", "\n"])
def test_a_phrase_with_no_words_is_refused_by_name(shot: Path, tmp_path: Path, capsys, text):
    code, meta, _out = _run(shot, tmp_path, text=text)
    err = capsys.readouterr().err
    assert code == 2 and meta is None, text
    assert "--phrase-text must be the quoted phrase's own words" in err and "live type" in err


def test_the_words_are_required_so_a_new_card_is_never_raster_only(shot: Path, tmp_path: Path):
    out, meta = tmp_path / "card.png", tmp_path / "card.json"
    argv = [str(shot), "--headline-box", "200,300,1400,520", "--phrase-box", "500,340,1000,500",
            "--source", "The Herald, 4 Mar 2026", "--out", str(out), "--meta", str(meta)]
    with pytest.raises(SystemExit) as exc:
        PC.main(argv)
    assert exc.value.code == 2, "argparse refuses the card outright: R26-55 is the card's shape now, not an option"
    assert not meta.exists()

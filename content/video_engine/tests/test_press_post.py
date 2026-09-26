"""THE POST CARD (P73 T3): a press card whose header is a SOCIAL POST, not a newspaper masthead.

The press card (P50 T3, CAPABILITIES "The PRESS CARD dock") crops any screenshot under a masthead strip that carries
the card's source line. A quotation from a post on a social platform is the same evidence - a docked crop of the real
post - framed by the header a post has: the author's display name, the handle, the date and time it was posted, and
(optional) a count such as its views, each typed by the AUTHOR from the source record and never fetched. The press
meta's `style: "post"` selects it; the masthead stays the default, and a card that names no style compiles and paints
byte for byte as it did.

We QUOTE the post; we do not impersonate the platform: the header draws no logo, no brand mark, no verification badge
and no avatar - those keys are refused by name. A count is a snapshot, so it carries the date it was read (`as_of`),
which can never be before the post. The citation and the header must agree: the source line names the handle.

The golden (`press-post`) is proved on the AMD RFSoC story's post (research sources/01: Dylan Patel, @dylan522p,
2026-09-19 16:41 UTC, 392,513 views at retrieval 2026-09-26, "AMD needs to be investigated for treason.") with a
stand-in crop DRAWN by the golden builder (no real screenshot is committed - generated images stay out of git), and
AMD's reply as the `record` card composing after it (`press-post@proof-reply`, the two on stage together).
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
GOLDEN = ROOT / "content/video_engine/tests/golden"
for p in (SCRIPTS, GOLDEN, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import build_scene_timeline_f as B  # noqa: E402

PHRASE = {"x0": 0.06, "y0": 0.1, "x1": 0.94, "y1": 0.42}
POST = {"name": "Dylan Patel", "handle": "@dylan522p", "posted": "2026-09-19T16:41Z",
        "counts": [{"label": "views", "value": 392513, "as_of": "2026-09-26"}]}
META = {"kind": "press", "source": "X / @dylan522p, 19 Sep 2026", "phrase": PHRASE,
        "phrase_text": "AMD needs to be investigated for treason.", "card": [528, 160],
        "style": "post", "post": POST}
HEADER = {"name": "Dylan Patel", "handle": "@dylan522p", "when": "19 Sep 2026, 16:41 UTC",
          "counts": "392,513 views as of 26 Sep 2026"}


def _meta(**kw) -> dict:
    m = json.loads(json.dumps(META))
    m.update(kw)
    return {k: v for k, v in m.items() if v is not None}


def _post(**kw) -> dict:
    p = json.loads(json.dumps(POST))
    p.update(kw)
    return {k: v for k, v in p.items() if v is not None}


def _refused(meta: dict, *needles: str) -> str:
    with pytest.raises(ValueError) as exc:
        B.dock_opts({"press": meta})
    msg = str(exc.value)
    for n in needles:
        assert n in msg, msg
    return msg


# ------------------------------------------------------------------ the header reaches the timeline

def test_a_post_card_carries_its_header_as_the_author_typed_it():
    press = B.dock_opts({"press": _meta()})["press"]
    assert press["style"] == "post"
    assert press["post"] == HEADER, "the display strings are the compiler's, from the author's fields - nothing fetched"
    assert press["source"] == "X / @dylan522p, 19 Sep 2026" and press["phrase_text"] == META["phrase_text"]


def test_the_dock_entry_writes_the_style_and_the_header_beside_the_press_keys():
    d = B.dock_entry("ev-post-patel", 0, 5.0, 20.0, 0, press=B.press_meta(_meta()))
    assert d["kind"] == "press" and d["style"] == "post" and d["post"] == HEADER


def test_the_masthead_is_the_default_and_a_card_with_no_style_is_the_entry_it_was():
    plain = {k: v for k, v in META.items() if k not in ("style", "post")}
    meta = B.press_meta(plain)
    assert "style" not in meta and "post" not in meta
    d = B.dock_entry("ev-press", 0, 5.0, 20.0, 0, press=meta)
    assert "style" not in d and "post" not in d
    assert B.press_meta(dict(plain, style="masthead")) == meta, "naming the default writes nothing"


def test_a_date_only_post_and_several_counts_read_in_order():
    press = B.press_meta(_meta(post=_post(posted="2026-09-19", counts=[
        {"label": "views", "value": 392513, "as_of": "2026-09-26"},
        {"label": "reposts", "value": 62, "as_of": "2026-09-26"}])))
    assert press["post"]["when"] == "19 Sep 2026"
    assert press["post"]["counts"] == "392,513 views, 62 reposts as of 26 Sep 2026"


def test_counts_are_optional_and_a_post_without_them_writes_no_counts_key():
    press = B.press_meta(_meta(post=_post(counts=None)))
    assert press["post"] == {k: v for k, v in HEADER.items() if k != "counts"}


def test_the_posts_url_is_provenance_and_stays_off_the_timeline():
    press = B.press_meta(_meta(post=_post(url="https://x.com/dylan522p/status/2101350877932212621")))
    assert "url" not in press["post"]


# ------------------------------------------------------------------ the refusals, each by name

def test_an_unknown_style_is_refused_by_name():
    _refused(_meta(style="tweet"), "style", "post", "masthead")


def test_a_post_style_needs_its_post_fields_and_the_fields_need_the_style():
    _refused(_meta(post=None), "style: post", "name", "handle", "posted")
    _refused(_meta(style=None), "post", "style")


@pytest.mark.parametrize("field, value, needle", [
    ("name", "", "name"),
    ("name", 7, "name"),
    ("name", "x" * 61, "name"),
    ("handle", "dylan522p", "@"),
    ("handle", "@dylan 522p", "@"),
    ("handle", None, "handle"),
    ("posted", "Sep 19 2026", "posted"),
    ("posted", "2026-09-19 16:41", "UTC"),
    ("posted", "2026-02-30", "posted"),
    ("posted", None, "posted"),
])
def test_a_bad_header_field_is_refused_by_name(field, value, needle):
    p = _post()
    if value is None:
        p.pop(field)
    else:
        p[field] = value
    _refused(_meta(post=p), needle)


@pytest.mark.parametrize("count, needle", [
    ({"label": "views", "value": -1, "as_of": "2026-09-26"}, "value"),
    ({"label": "views", "value": True, "as_of": "2026-09-26"}, "value"),
    ({"label": "views", "value": "392,513", "as_of": "2026-09-26"}, "value"),
    ({"label": "", "value": 1, "as_of": "2026-09-26"}, "label"),
    ({"label": "views", "value": 1}, "as_of"),
    ({"label": "views", "value": 1, "as_of": "2026-09-18"}, "before"),
    ({"label": "views", "value": 1, "as_of": "2026-09-26", "trend": "up"}, "trend"),
])
def test_a_count_is_a_dated_snapshot_or_it_is_refused(count, needle):
    _refused(_meta(post=_post(counts=[count])), needle)


def test_more_than_three_counts_is_refused():
    c = {"label": "views", "value": 1, "as_of": "2026-09-26"}
    _refused(_meta(post=_post(counts=[c, c, c, c])), "counts")


@pytest.mark.parametrize("key", ["logo", "avatar", "verified", "platform_mark", "icon", "badge"])
def test_the_card_quotes_the_post_and_never_impersonates_the_platform(key):
    _refused(_meta(post=_post(**{key: "x"})), key, "impersonate")


def test_an_unknown_post_field_is_refused_by_name():
    _refused(_meta(post=_post(likes_text="1k")), "likes_text")


def test_the_citation_and_the_header_must_agree_on_the_handle():
    _refused(_meta(source="X, 19 Sep 2026"), "@dylan522p", "source")


def test_a_post_card_on_a_surface_is_refused_until_the_reflow_knows_the_header():
    with pytest.raises(ValueError) as exc:
        B.dock_opts({"press": _meta(), "embed": "tv"})
    assert "post" in str(exc.value) and "embed" in str(exc.value), str(exc.value)


def test_a_post_card_may_join_the_press_pile():
    opts = B.dock_opts({"press": _meta(), "stack": True})
    assert opts["stack"] is True and opts["press"]["style"] == "post"


# ------------------------------------------------------------------ the golden: the story's post, a drawn stand-in

def test_the_golden_is_listed_with_its_reply_instant():
    import render_baseline as RB
    import test_golden_frames as TG
    assert "press-post" in TG.SURFACES
    surface, flags, t = RB.PROOF_FRAMES["press-post@proof-reply"]
    assert surface == "press-post" and flags == {}


def test_the_golden_quotes_the_story_verbatim_on_drawn_stand_ins():
    import build_golden_sources as G
    tl, uris = G.press_post()
    docks = tl["scenes"][0]["docks"]
    post = next(d for d in docks if d["slide"] == G.POST_SLIDE)
    reply = next(d for d in docks if d["slide"] == G.REPLY_SLIDE)
    assert post["style"] == "post" and post["post"] == HEADER
    # sources/01: the post's own words, verbatim; sources/04: the spokesperson's, as Tom's Hardware printed them
    assert post["phrase_text"] == "AMD needs to be investigated for treason."
    assert post["source"] == "X / @dylan522p, 19 Sep 2026"
    assert reply["phrase_text"] == "This recent instance is unrelated to any direct AMD sales or shipments."
    assert reply["source"] == "Tom's Hardware, 24 Sep 2026" and "style" not in reply, "the reply wears the masthead"
    # the crops are DRAWN (the bars writer, stdlib-only), never a real screenshot
    assert uris[post["slide"]] == G.uri("image/png", G.png_bars(G.POST_CROP[0], G.POST_CROP[1], G.POST_PAPER, G.POST_BARS))
    # the reply is the pile's second card, landing AFTER the post: the base frame is the post alone, the proof has both
    assert (post["stack_index"], reply["stack_index"], post["stack_n"]) == (0, 1, 2)
    assert G.FRAME_T["press-post"] < reply["enter"] < _proof_t()


def _proof_t() -> float:
    import render_baseline as RB
    return RB.PROOF_FRAMES["press-post@proof-reply"][2]


def test_the_committed_source_is_the_builders_output():
    import build_golden_sources as G
    tl, uris = G.press_post()
    assert json.loads((GOLDEN / "sources/press-post.timeline.json").read_text(encoding="utf-8")) == json.loads(json.dumps(tl))
    assert json.loads((GOLDEN / "sources/press-post.uris.json").read_text(encoding="utf-8")) == uris


# ------------------------------------------------------------------ the painter: what the frame carries

PROBE = """(slide) => {
  const el = document.getElementById('press-' + slide);
  if (!el) return null;
  const q = (s) => { const n = el.querySelector(s); return n ? n.textContent : null; };
  const r = (s) => { const n = s ? el.querySelector(s) : el; if (!n) return null; const b = n.getBoundingClientRect(); return [b.x, b.y, b.width, b.height]; };
  return { post: el.classList.contains('post'), name: q('.ppost .pname'), handle: q('.ppost .phandle'),
           when: q('.pmast .pwhen'), counts: q('.pmast .pcount'), mast: q('.pmast span'),
           imgs: el.querySelectorAll('img').length, svgs: el.querySelectorAll('svg').length,
           opacity: +getComputedStyle(el).opacity, box: r(null), header: [r('.ppost .pname'), r('.ppost .phandle'), r('.pmast .pwhen'), r('.pmast .pcount')],
           type: (window.__pressType ? window.__pressType()[slide] : null) };
}"""
SEEK = "t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }"
COVER = """(pressId) => {
  const r = [...document.querySelectorAll('.dock.record')].find((n) => +getComputedStyle(n).opacity > 0.5);
  const p = document.getElementById(pressId);
  if (!r || !p) return null;
  const a = r.getBoundingClientRect(), b = p.getBoundingClientRect();
  return Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left))
       * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
}"""


def _served_eval(tl: dict, uris: dict, t: float, script: str, args: list, aspect: str = "16:9") -> list:
    import render_baseline as RB
    import served_player as SP
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "post.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SP.served(html, w, h) as (page, errs):
            page.evaluate(SEEK, t)
            out = [page.evaluate(script, a) for a in args]
            assert not errs, errs
            return out


def _probe(tl: dict, uris: dict, t: float, *slides: str) -> list:
    return _served_eval(tl, uris, t, PROBE, list(slides))


def test_the_painted_header_is_the_post_and_carries_no_mark_of_the_platform():
    import build_golden_sources as G
    tl, uris = G.press_post()
    card, = _probe(tl, uris, G.FRAME_T["press-post"], G.POST_SLIDE)
    assert card["post"] and card["opacity"] > 0.99
    assert (card["name"], card["handle"], card["when"], card["counts"]) == (
        "Dylan Patel", "@dylan522p", "19 Sep 2026, 16:41 UTC", "392,513 views as of 26 Sep 2026")
    assert card["imgs"] == 1 and card["svgs"] == 0, "the crop is the only picture: no logo, no avatar, no badge"


def test_a_post_is_set_in_the_house_face_whatever_the_press_face_dial_says():
    """E89 ruled the serif 'for the news'; a post is not the news, so its pulled phrase keeps the house sans
    (species/press.mjs PRESS.POST_FACE) while the masthead card beside it follows the dial."""
    import build_golden_sources as G
    tl, uris = G.press_post()
    tl = dict(tl, kinetics=dict(tl.get("kinetics") or {}, press_face="serif"))
    post, reply = _probe(tl, uris, _proof_t(), G.POST_SLIDE, G.REPLY_SLIDE)
    assert post["type"]["face"] == "house" and reply["type"]["face"] == "serif"


def test_a_masthead_card_paints_exactly_the_strip_it_did():
    import build_golden_sources as G
    tl, uris = G.press_stack()
    card, = _probe(tl, uris, G.FRAME_T["press-stack"], G.PRESS_CARDS[-1][0])
    assert not card["post"] and card["name"] is None and card["mast"] == G.PRESS_CARDS[-1][2]


@pytest.mark.parametrize("aspect", ["16:9", "9:16"])
def test_the_reply_stacks_on_the_post_and_the_post_header_is_still_read_above_it(aspect):
    """The pile's own law (species/press.mjs pressStack): the newest lit in front, the older one pushed a step back,
    higher and dimmer. The post's WHOLE header - the poster's row and the date/counts row - must stand clear above the
    reply's top edge (every one of its four texts; a row's own bottom padding may tuck under), so a viewer still reads
    whose post it was while the reply is read. At 9:16 the fan's own step (STEP_H of the card) cleared only the first
    row - the post's step takes pressHeadStep, so the date and the counts are read on a phone too."""
    import build_golden_sources as G
    tl, uris = G.press_post()
    post, reply = _served_eval(dict(tl, aspect=aspect), uris, _proof_t(), PROBE, [G.POST_SLIDE, G.REPLY_SLIDE], aspect)
    assert reply["opacity"] > 0.99 and 0.5 < post["opacity"] < 0.9, "the newest lit, the post dimmed one step"
    reply_top = reply["box"][1]
    for row in post["header"]:
        assert row is not None and row[1] + row[3] <= reply_top + 0.5, (row, reply_top)


def test_a_record_dock_beside_a_press_card_is_covered_which_is_why_the_reply_stacks():
    """P73 T3's finding, pinned so a change to the dock geometry (T46c's) says so: a record reply docked in a slot
    while the post card holds the stage's centre is painted UNDER the press card at 16:9 - the reply's words are cut.
    The golden therefore stacks the reply as a press card; a slot that clears the press box retires this test."""
    import build_scene_timeline_f as BST
    import build_golden_sources as G
    tl, uris = G.press_post()
    sc = tl["scenes"][0]
    rec = "ev-record-probe"
    tl["evidence"][rec] = {"title": "probe", "source": "golden", "species": "record", "badges": [],
                           "document": {"path": "golden", "sha256": "0" * 64},
                           "record": {"hdr": ["A", "B"], "kicker": "k", "words": [["one", 11.6], ["two", 11.9]],
                                      "hl": [0, 0], "end": 12.2, "attr": "a", "src": "s"}}
    uris[rec] = G.uri("image/png", G.png_solid(64, 29, (22, 24, 28)))
    post = {k: v for k, v in next(d for d in sc["docks"] if d["slide"] == G.POST_SLIDE).items()
            if k not in ("stack_index", "stack_n")}
    sc["docks"] = [post, BST.dock_entry(rec, 0, 11.0, G.RUNTIME, 0)]
    covered, = _served_eval(tl, uris, _proof_t(), COVER, ["press-" + G.POST_SLIDE])
    assert covered is not None and covered > 0, "the record slot and the press box intersect at 16:9"

"""THE REVIEW QUEUE: the data's schema, the deterministic builder, the proofs, and the answer server's one write door.

The pins: the schema refuses a missing field, an unknown kind, a duplicate id, and an open watch / look item with no
proof (E99 s14) by name; --write then --check passes and a one-word data edit makes --check fail naming REVIEW-QUEUE.md;
the markdown and the page are byte-identical across two writes; every answerable id appears once as a card, an owed id
only in the collapsed owed list with no answer controls, a ruled id only under "Ruled since the last pass" with its ruling
id; the progress line counts only answerable items; a player link that did not answer is never a link; the crop helper's
box holds every differing pixel and a caption-only pair is refused; the server appends exactly one operator line per
valid answer, refuses the bad bodies and an owed item with a named 400 and appends nothing, and GET /answers returns the
latest line per item. Every write goes to a temp path.
"""
from __future__ import annotations

import copy
import json
import re
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_review_queue as BRQ  # noqa: E402
import review_queue_proofs as RQP  # noqa: E402
import serve_review_queue as SRQ  # noqa: E402

DATA = ROOT / BRQ.DATA_REL
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "review-queue.fixture.json"
OWED_ID = "r26-76-melt-endings-in-motion"
RULED_ID = "r26-123-caption-default"


@pytest.fixture(scope="module")
def data() -> dict:
    return BRQ.load_data(FIXTURE)


@pytest.fixture(scope="module")
def page(data) -> str:
    return BRQ.render_page(data, ROOT)


def write_data(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def run_cli(tmp: Path, data_path: Path, *mode: str) -> int:
    extra = ["--no-probe"] if "--write" in mode else []
    return BRQ.main([*mode, *extra, "--data", str(data_path), "--md", str(tmp / "REVIEW-QUEUE.md"),
                     "--out", str(tmp / "page")])


def card_of(page: str, item_id: str) -> str:
    return re.search(rf'<article class="card" data-id="{re.escape(item_id)}".*?</article>', page, re.S).group(0)


# ---------------------------------------------------------------- schema

def test_schema_refuses_a_missing_field_by_name(data):
    items = copy.deepcopy(data["items"])
    del items[0]["blocks"]
    with pytest.raises(BRQ.QueueError, match=rf"{items[0]['id']}: missing field\(s\) blocks"):
        BRQ.validate(items)


def test_schema_refuses_an_unknown_kind_by_name(data):
    items = copy.deepcopy(data["items"])
    items[1]["kind"] = "ponder"
    with pytest.raises(BRQ.QueueError, match=rf"{items[1]['id']}: unknown kind 'ponder'"):
        BRQ.validate(items)


def test_schema_refuses_a_duplicate_id_by_name(data):
    items = copy.deepcopy(data["items"])
    items[2]["id"] = items[0]["id"]
    with pytest.raises(BRQ.QueueError, match=rf"duplicate id '{items[0]['id']}'"):
        BRQ.validate(items)


@pytest.mark.parametrize("kind", ["watch", "look"])
def test_the_builder_refuses_an_open_watch_or_look_item_with_no_proof(data, kind):
    items = copy.deepcopy(data["items"])
    rec = next(i for i in items if i["status"] == "open" and i["kind"] in BRQ.PROOF_KINDS)
    rec["kind"], rec["proofs"] = kind, []
    with pytest.raises(BRQ.QueueError, match=rf"{rec['id']}: an open {kind} item has no proof entry \(E99 s14\)"):
        BRQ.validate(items)


def test_an_owed_item_must_say_what_it_owes(data):
    items = copy.deepcopy(data["items"])
    rec = next(i for i in items if i["id"] == OWED_ID)
    rec["owed"] = ""
    with pytest.raises(BRQ.QueueError, match=rf"{OWED_ID}: an owed item says what it owes"):
        BRQ.validate(items)


def test_the_fixture_passes_and_every_kind_has_open_items(data):
    kinds = {i["kind"] for i in BRQ.open_items(data)}
    assert kinds == set(BRQ.KINDS)
    for rec in BRQ.answerable_items(data):
        if rec["kind"] in BRQ.PROOF_KINDS:
            assert rec["proofs"], rec["id"]


def test_the_live_queue_data_validates_and_every_open_proof_kind_has_a_proof():
    live = BRQ.load_data(DATA)
    for rec in BRQ.answerable_items(live):
        if rec["kind"] in BRQ.PROOF_KINDS:
            assert rec["proofs"], rec["id"]


# ---------------------------------------------------------------- builder

def test_write_then_check_passes_and_a_one_word_edit_fails_naming_the_markdown(tmp_path, data, capsys):
    data_path = write_data(tmp_path / "queue.json", data)
    assert run_cli(tmp_path, data_path, "--write") == 0
    assert run_cli(tmp_path, data_path, "--check") == 0
    edited = copy.deepcopy(data)
    edited["items"][0]["title"] = edited["items"][0]["title"] + " again"
    write_data(data_path, edited)
    capsys.readouterr()
    assert run_cli(tmp_path, data_path, "--check") == 1
    assert "REVIEW-QUEUE.md" in capsys.readouterr().err


def test_the_markdown_and_the_page_are_byte_identical_across_two_writes(tmp_path, data):
    data_path = write_data(tmp_path / "queue.json", data)
    assert run_cli(tmp_path, data_path, "--write") == 0
    md1 = (tmp_path / "REVIEW-QUEUE.md").read_bytes()
    page1 = (tmp_path / "page/index.html").read_bytes()
    crops1 = {p.name: p.read_bytes() for p in (tmp_path / "page/crops").iterdir()}
    frames1 = sorted(p.name for p in (tmp_path / "page/frames").iterdir())
    assert run_cli(tmp_path, data_path, "--write") == 0
    assert (tmp_path / "REVIEW-QUEUE.md").read_bytes() == md1
    assert (tmp_path / "page/index.html").read_bytes() == page1
    assert {p.name: p.read_bytes() for p in (tmp_path / "page/crops").iterdir()} == crops1
    assert sorted(p.name for p in (tmp_path / "page/frames").iterdir()) == frames1


def test_answerable_ids_are_cards_owed_ids_are_listed_and_ruled_ids_carry_their_ruling(data, page):
    md = BRQ.render_markdown(data)
    md_open, md_rest = md.split(f"## {BRQ.OWED_HEADING}")
    md_owed, md_ruled = md_rest.split(f"## {BRQ.RULED_HEADING}")
    page_open, page_rest = page.split('<section id="owed">')
    page_owed, page_ruled = page_rest.split('<section id="ruled">')
    for rec in BRQ.answerable_items(data):
        assert page_open.count(f'data-id="{rec["id"]}"') == 1, rec["id"]
        assert md_open.count(f"| `{rec['id']}` |") == 1, rec["id"]
    for rec in BRQ.owed_items(data):
        assert f'data-id="{rec["id"]}"' not in page and f'data-owed-id="{rec["id"]}"' in page_owed, rec["id"]
        assert f"| `{rec['id']}` |" in md_owed and f"`{rec['id']}`" not in md_open, rec["id"]
    ruled = BRQ.ruled_items(data)
    assert ruled, "the tracked data carries the ruled-since-the-last-pass records"
    for rec in ruled:
        assert f"`{rec['id']}`" not in md_open + md_owed and f"| `{rec['id']}` |" in md_ruled, rec["id"]
        assert f'data-id="{rec["id"]}"' not in page
        assert BRQ.esc(rec["ruling"]) in page_ruled and BRQ.esc(rec["ruling"]) not in page_open, rec["id"]


def test_a_ruled_item_shows_its_ruling_id(data, page):
    rec = next(i for i in BRQ.ruled_items(data) if i["id"] == RULED_ID)
    assert rec["ruling"] == "E99 s6"
    row = re.search(rf"<tr><td><b>{re.escape(BRQ.esc(rec['title']))}</b>.*?</tr>", page, re.S).group(0)
    assert '<td class="ruling">E99 s6</td>' in row
    assert f"| `{RULED_ID}` |" in BRQ.render_markdown(data) and "| E99 s6 |" in BRQ.render_markdown(data)


def test_an_owed_item_renders_without_answer_controls(page):
    owed = page.split('<section id="owed">')[1].split('<section id="ruled">')[0]
    li = re.search(rf'<li data-owed-id="{OWED_ID}">.*?</li>', owed, re.S).group(0)
    assert "E99 s2" in li
    assert "<form" not in owed and "<input" not in owed and "<textarea" not in owed and "<button" not in owed
    assert "<details>" in owed


def test_the_progress_line_counts_only_answerable_items(data, page):
    total = len(BRQ.answerable_items(data))
    assert total < len(BRQ.open_items(data))
    assert f'data-total="{total}"' in page and f">0 of {total} answered<" in page
    assert page.count('<article class="card"') == total == page.count("<form class=\"answer\">")


def test_a_player_link_that_did_not_answer_is_never_a_link(data):
    rec = next(i for i in BRQ.answerable_items(data) if any(p["type"] == "player" for p in i.get("proofs") or []))
    url = next(p["url"] for p in rec["proofs"] if p["type"] == "player")
    dead = card_of(BRQ.render_page(data, ROOT, {url: False}), rec["id"])
    assert f'href="{url}"' not in dead and "not answering when this page was built" in dead and "serve_player.py" in dead
    alive = card_of(BRQ.render_page(data, ROOT, {url: True}), rec["id"])
    assert f'href="{url}"' in alive


def test_a_clip_whose_proof_changed_is_rendered_again_not_served_by_name(tmp_path, monkeypatch, data):
    """2026-09-16: the bars -> line card's proofs were rewritten and the operator watched the OLD clip under the same
    name. A clip is current only when its sidecar carries the proof's source and window."""
    item, n, proof = RQP.clip_proofs(data, None)[0]
    out = tmp_path / RQP.clip_name(item["id"], n)
    out.write_bytes(b"old clip")
    assert not RQP.clip_is_current(proof, out), "no sidecar - never trusted by name alone"
    RQP.clip_sidecar(out).write_text(json.dumps(RQP.clip_key(proof)), encoding="utf-8")
    assert RQP.clip_is_current(proof, out)
    changed = dict(proof, t0=proof["t0"] + 1.0)
    assert not RQP.clip_is_current(changed, out), "a different window is a different clip"
    other = dict(proof, surface="some-other-surface")
    assert not RQP.clip_is_current(other, out), "a different source is a different clip"
    rendered = []
    monkeypatch.setattr(RQP, "render_clip", lambda p, o: rendered.append(o) or o.write_bytes(b"new clip"))
    live = tmp_path / "queue.json"
    d2 = copy.deepcopy(data)
    for it in d2["items"]:
        if it["id"] == item["id"]:
            it["proofs"][n]["t0"] = proof["t0"] + 1.0
    live.write_text(json.dumps(d2), encoding="utf-8")
    assert RQP.main(["--clips", "--only", item["id"], "--data", str(live), "--clips-dir", str(tmp_path)]) == 0
    assert out in rendered and out.read_bytes() == b"new clip"
    assert json.loads(RQP.clip_sidecar(out).read_text(encoding="utf-8"))["t0"] == proof["t0"] + 1.0


def test_a_clip_proof_names_its_build_and_time_range(data, page):
    rec, n, proof = RQP.clip_proofs(data, "p58-hg3-chart-forms")[0]
    card = card_of(page, rec["id"])
    assert f"golden {proof['surface']} - {proof['t0']:g} to {proof['t1']:g} s" in card
    assert f"clips/{RQP.clip_name(rec['id'], n)}" in card or "clip not rendered yet" in card


def test_the_page_makes_no_external_request(page):
    assert not re.search(r'(src|href)="https?://(?!127\.0\.0\.1)', page)
    assert "<link" not in page and "@import" not in page


# ---------------------------------------------------------------- crops

def _pair(size=(200, 120)):
    from PIL import Image, ImageDraw
    a = Image.new("RGB", size, (244, 230, 199))
    b = a.copy()
    return a, b, ImageDraw.Draw(b)


def test_the_crop_box_contains_every_differing_pixel():
    from PIL import ImageChops
    a, b, draw = _pair()
    draw.rectangle([40, 30, 59, 44], fill=(37, 49, 60))
    draw.point((150, 100), fill=(184, 64, 42))
    box = RQP.diff_box(a, b, margin=4)
    diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v >= RQP.DIFF_THRESHOLD else 0)
    changed = [(x, y) for y in range(a.height) for x in range(a.width) if diff.getpixel((x, y))]
    assert changed and all(box[0] <= x < box[2] and box[1] <= y < box[3] for x, y in changed)
    assert box == (36, 26, 155, 105)


def test_the_crop_refuses_a_pair_that_differs_only_inside_the_caption_box():
    a, b, draw = _pair()
    draw.rectangle([20, 95, 180, 110], fill=(240, 180, 40))    # a caption word changed, nothing else
    with pytest.raises(RQP.NoVisibleChange, match="outside the caption box"):
        RQP.diff_box(a, b, caption_box=[0, 90, 200, 120])
    draw.rectangle([10, 10, 20, 20], fill=(37, 49, 60))         # now the stage changes too
    box = RQP.diff_box(a, b, caption_box=[0, 90, 200, 120], margin=0)
    assert box == (10, 10, 21, 21)


def test_the_tracked_crop_differs_outside_its_caption(data):
    crops = [(i, p) for i in BRQ.answerable_items(data) for p in i.get("proofs") or [] if p["type"] == "crop"]
    assert crops
    for rec, proof in crops:
        x0, y0, x1, y1 = RQP.crop_box(proof, ROOT)
        cap = proof.get("caption_box")
        assert not cap or y1 <= cap[1] or y0 >= cap[3] or x1 <= cap[0] or x0 >= cap[2], rec["id"]


# ---------------------------------------------------------------- server

@pytest.fixture()
def server(tmp_path):
    answers = tmp_path / "answers.jsonl"
    answers.write_text("", encoding="utf-8")
    httpd = SRQ.make_server(0, FIXTURE, tmp_path / "page", answers, quiet=True, probe=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}", answers
    httpd.shutdown()
    httpd.server_close()


def request(url: str, body: bytes | None = None) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, data=body, method="POST" if body is not None else "GET",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            raw, code, headers = res.read(), res.status, res.headers
    except urllib.error.HTTPError as err:
        raw, code, headers = err.read(), err.code, err.headers
    assert headers.get("Cache-Control") == "no-store"
    text = raw.decode("utf-8")
    return code, json.loads(text) if headers.get("Content-Type", "").startswith("application/json") else text


def post(base: str, payload) -> tuple[int, dict]:
    return request(f"{base}/answer", json.dumps(payload).encode("utf-8"))


def lines_of(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_the_server_regenerates_and_serves_the_page(server):
    base, _ = server
    code, body = request(f"{base}/")
    assert code == 200 and 'data-id="r26-126-push-word"' in body and f'data-owed-id="{OWED_ID}"' in body


def test_a_valid_answer_appends_exactly_one_operator_line(server):
    base, answers = server
    code, body = post(base, {"item": "r26-126-push-word", "choice": "hold", "note": "not yet"})
    assert code == 200 and body["ok"] is True
    rows = lines_of(answers)
    assert len(rows) == 1
    assert rows[0]["by"] == "operator" and rows[0]["item"] == "r26-126-push-word" and rows[0]["choice"] == "hold"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", rows[0]["at"])


@pytest.mark.parametrize("payload, reason", [
    ({"item": "no-such-item", "choice": "other", "note": ""}, "unknown item 'no-such-item'"),
    ({"item": "r26-126-push-word", "choice": "maybe", "note": ""}, "invalid choice 'maybe' for r26-126-push-word"),
    ({"item": "r26-126-push-word", "choice": "other", "note": "x" * (SRQ.NOTE_MAX + 1)}, "over NOTE_MAX"),
    (["r26-126-push-word", "hold"], "the body is not one JSON object"),
    ({"item": OWED_ID, "choice": "other", "note": ""}, f"{OWED_ID} is owed by the agent, not open for an answer"),
    ({"item": RULED_ID, "choice": "other", "note": ""}, f"unknown item '{RULED_ID}'"),
])
def test_a_bad_answer_is_refused_by_name_and_appends_nothing(server, payload, reason):
    base, answers = server
    code, body = post(base, payload)
    assert code == 400 and body["ok"] is False and reason in body["error"]
    assert answers.read_text(encoding="utf-8") == ""


def test_a_body_that_is_not_json_is_refused(server):
    base, answers = server
    code, body = request(f"{base}/answer", b"choice=hold")
    assert code == 400 and "the body is not one JSON object" in body["error"]
    assert answers.read_text(encoding="utf-8") == ""


def test_a_card_converted_from_owed_while_the_server_runs_is_answerable_without_a_restart(tmp_path):
    """2026-09-15: the operator's Save on r26-133 was refused as 'owed' by a server started the day before - it had read
    the queue once. The index now follows the data file's mtime."""
    import os
    import time
    live = tmp_path / "queue.json"
    live.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    answers = tmp_path / "answers.jsonl"
    answers.write_text("", encoding="utf-8")
    httpd = SRQ.make_server(0, live, tmp_path / "page", answers, quiet=True, probe=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    try:
        code, body = post(base, {"item": OWED_ID, "choice": "other", "note": ""})
        assert code == 400 and "owed by the agent" in body["error"]
        assert httpd.queue_index.reloads == 1
        # the assembly pass converts the owed card into an answerable one: the same shape as the fixture's rule card
        data = json.loads(live.read_text(encoding="utf-8"))
        model = next(i for i in data["items"] if i["id"] == "r26-126-push-word")
        for k, i in enumerate(data["items"]):
            if i["id"] == OWED_ID:
                data["items"][k] = dict(copy.deepcopy(model), id=OWED_ID, title=i["title"], was_kind="owed")
        live.write_text(json.dumps(data, indent=2), encoding="utf-8")
        st = live.stat()
        os.utime(live, ns=(st.st_atime_ns, st.st_mtime_ns + 2_000_000_000))   # a coarse-mtime filesystem still sees a change
        time.sleep(0.05)
        code, body = post(base, {"item": OWED_ID, "choice": model["options"][0], "note": "answered after the conversion"})
        assert code == 200 and body["ok"] is True, body
        assert httpd.queue_index.reloads == 2
        rows = lines_of(answers)
        assert len(rows) == 1 and rows[0]["item"] == OWED_ID and rows[0]["choice"] == model["options"][0]
        # an unchanged file is not re-read
        post(base, {"item": "r26-126-push-word", "choice": "hold", "note": ""})
        assert httpd.queue_index.reloads == 2
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_get_answers_returns_the_latest_line_per_item(server):
    base, answers = server
    code, body = request(f"{base}/answers")
    assert code == 200 and body == {}
    post(base, {"item": "r26-126-push-word", "choice": "hold", "note": "first"})
    post(base, {"item": "r26-126-push-word", "choice": "push", "note": "second"})
    post(base, {"item": "p55-hg2-effects-gallery", "choice": "it does", "note": ""})
    code, body = request(f"{base}/answers")
    assert code == 200 and set(body) == {"r26-126-push-word", "p55-hg2-effects-gallery"}
    assert body["r26-126-push-word"]["choice"] == "push" and body["r26-126-push-word"]["note"] == "second"
    assert len(lines_of(answers)) == 3


def test_answers_cli_names_an_answered_but_open_item(tmp_path, data, capsys):
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps({"item": "r26-126-push-word", "choice": "hold", "note": "", "at": "2026-09-14T10:00:00+09:00",
                                   "by": "operator"}) + "\n", encoding="utf-8")
    assert BRQ.main(["--answers", "--data", str(FIXTURE), "--answers-file", str(answers)]) == 0
    out = capsys.readouterr().out
    assert "r26-126-push-word: 'hold' at 2026-09-14T10:00:00+09:00 - NOT APPLIED (still open)" in out

"""THE REVIEW QUEUE: the data's schema, the deterministic builder, and the answer server's one write door.

The pins: the schema refuses a missing field, an unknown kind and a duplicate id by name; --write then --check passes
and a one-word data edit makes --check fail naming REVIEW-QUEUE.md; the markdown and the page are byte-identical
across two writes; every open id appears once in the page and once in the markdown, a ruled id only under "Ruled since
the last pass"; the server appends exactly one operator line per valid answer, refuses the four bad bodies with a named
400 and appends nothing, and GET /answers returns the latest line per item. Every write goes to a temp path.
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
import serve_review_queue as SRQ  # noqa: E402

DATA = ROOT / BRQ.DATA_REL


@pytest.fixture(scope="module")
def data() -> dict:
    return BRQ.load_data(DATA)


def write_data(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def run_cli(tmp: Path, data_path: Path, *mode: str) -> int:
    return BRQ.main([*mode, "--data", str(data_path), "--md", str(tmp / "REVIEW-QUEUE.md"), "--out", str(tmp / "page")])


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


def test_the_tracked_data_passes_and_every_kind_has_open_items(data):
    kinds = {i["kind"] for i in BRQ.open_items(data)}
    assert kinds == set(BRQ.KINDS)


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
    frames1 = sorted(p.name for p in (tmp_path / "page/frames").iterdir())
    assert run_cli(tmp_path, data_path, "--write") == 0
    assert (tmp_path / "REVIEW-QUEUE.md").read_bytes() == md1
    assert (tmp_path / "page/index.html").read_bytes() == page1
    assert sorted(p.name for p in (tmp_path / "page/frames").iterdir()) == frames1


def test_every_open_id_appears_once_and_a_ruled_id_only_under_the_ruled_section(data):
    page = BRQ.render_page(data, ROOT)
    md = BRQ.render_markdown(data)
    md_open, md_ruled = md.split(f"## {BRQ.RULED_HEADING}")
    page_open, page_ruled = page.split('<section id="ruled">')
    for rec in BRQ.open_items(data):
        assert page.count(f'data-id="{rec["id"]}"') == 1, rec["id"]
        assert md.count(f"| `{rec['id']}` |") == 1, rec["id"]
    ruled = BRQ.ruled_items(data)
    assert ruled, "the tracked data carries the ruled-since-the-last-pass records"
    for rec in ruled:
        assert f"`{rec['id']}`" not in md_open and f"| `{rec['id']}` |" in md_ruled, rec["id"]
        assert f'data-id="{rec["id"]}"' not in page
        assert esc_in(rec["ruling"], page_ruled) and not esc_in(rec["ruling"], page_open), rec["id"]


def esc_in(text: str, blob: str) -> bool:
    return BRQ.esc(text) in blob


def test_a_missing_proof_shows_the_marker_and_a_stale_port_its_serve_command(data):
    page = BRQ.render_page(data, ROOT)
    card = re.search(r'<article class="card" data-id="r26-133-drift-idle-paints-nothing".*?</article>', page, re.S).group(0)
    assert BRQ.NO_PROOF_MARKER in card
    card = re.search(r'<article class="card" data-id="p52-gate3-species-proof-motion".*?</article>', page, re.S).group(0)
    assert 'class="stale"' in card and "serve_player.py content/video_engine/review/gates-2026-09-13/species-proof-player/ --port 8756" in card
    assert 'href="http://127.0.0.1:8756' not in card


def test_the_page_makes_no_external_request(data):
    page = BRQ.render_page(data, ROOT)
    assert not re.search(r'(src|href)="https?://(?!127\.0\.0\.1)', page)
    assert "<link" not in page and "@import" not in page


# ---------------------------------------------------------------- server

@pytest.fixture()
def server(tmp_path):
    answers = tmp_path / "answers.jsonl"
    answers.write_text("", encoding="utf-8")
    httpd = SRQ.make_server(0, DATA, tmp_path / "page", answers, quiet=True)
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
    code, page = request(f"{base}/")
    assert code == 200 and 'data-id="r26-126-push-word"' in page


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


def test_get_answers_returns_the_latest_line_per_item(server):
    base, answers = server
    code, body = request(f"{base}/answers")
    assert code == 200 and body == {}
    post(base, {"item": "r26-126-push-word", "choice": "hold", "note": "first"})
    post(base, {"item": "r26-126-push-word", "choice": "push", "note": "second"})
    post(base, {"item": "p55-hg2-effects-gallery", "choice": "keep", "note": ""})
    code, body = request(f"{base}/answers")
    assert code == 200 and set(body) == {"r26-126-push-word", "p55-hg2-effects-gallery"}
    assert body["r26-126-push-word"]["choice"] == "push" and body["r26-126-push-word"]["note"] == "second"
    assert len(lines_of(answers)) == 3


def test_answers_cli_names_an_answered_but_open_item(tmp_path, data, capsys):
    answers = tmp_path / "answers.jsonl"
    answers.write_text(json.dumps({"item": "r26-126-push-word", "choice": "hold", "note": "", "at": "2026-09-14T10:00:00+09:00",
                                   "by": "operator"}) + "\n", encoding="utf-8")
    assert BRQ.main(["--answers", "--answers-file", str(answers)]) == 0
    out = capsys.readouterr().out
    assert "r26-126-push-word: 'hold' at 2026-09-14T10:00:00+09:00 - NOT APPLIED (still open)" in out

"""THE REVIEW QUEUE: the data's schema, the deterministic builder, the proofs, and the answer server's one write door.

The pins: the schema refuses a missing field, an unknown kind, a duplicate id, and an open watch / look item with no
proof (E99 s14) by name; --write then --check passes and a one-word data edit makes --check fail naming REVIEW-QUEUE.md;
the markdown and the page are byte-identical across two writes; every answerable id appears once as a card, an owed id
only in the collapsed owed list with no answer controls, a ruled id only under "Ruled since the last pass" with its ruling
id; the progress line counts only answerable items; a player link that did not answer is never a link; the crop helper's
box holds every differing pixel and a caption-only pair is refused; the server appends exactly one operator line per
valid answer, refuses the bad bodies and an owed item with a named 400 and appends nothing, and GET /answers returns the
latest line per item. Every write goes to a temp path.

P65 T4 adds the `batch` kind: a card that carries `candidates` side by side, renders ONE plain question plus an
approve / deny + reason control per candidate, and answers each through the same POST /answer as
`{item: "<card>#<candidate>", choice, note: "<reason>: <free text>"}`. Its refusals are pinned by name (no candidates,
a candidate with no clip proof, a duplicate candidate id, a reason off the fixed nine, a proofs list that has drifted
from the candidates) and the nine reasons are proved to be the SCHEMA's, not a copy.

P67 T5 adds the critic rule (E99 s68): an OPEN `watch` card whose proof shows the WHOLE cut - a player link, or a clip
at least `WHOLE_CUT_S` = 30 s long - owes a `<build>/CRITIC.md`. Pinned here: the WARN by name on both shapes while
`CRITIC_REQUIRED` is False, the refusal by name once P67 T7 flips it, a beat clip and a `ruled` record untouched, a
present `critic` taken by `validate` as a repo-relative name only, the WRITER refusing a report that is not on disk or
lives outside the proof's build, and the live queue warning on exactly its two whole-cut watches while `--check` still
exits 0.
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
    """The fixture predates the batch kind (P65 T4) and is not this slice's to rewrite: `batch` is proved below on a
    record built here, and on the live queue's own HG1 card."""
    kinds = {i["kind"] for i in BRQ.open_items(data)}
    assert kinds == set(BRQ.KINDS) - {"batch"}
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
    assert page.count('<article class="card"') == total == page.count('<form class="answer"')


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
    # 2026-09-16, the second defect: the SAME surface re-rendered by an engine change is a different clip - the key
    # carries the golden's sha256, so a golden that moves invalidates every clip cut from it
    golden = tmp_path / "golden" / "content" / "video_engine" / "tests" / "golden" / "frames"
    golden.mkdir(parents=True)
    (golden / f"{proof['surface']}.png").write_bytes(b"frame v1")
    key1 = RQP.clip_key(proof, tmp_path / "golden")
    assert key1["source_sha256"] and key1 != RQP.clip_key(proof), "a source on disk is part of the key"
    (golden / f"{proof['surface']}.png").write_bytes(b"frame v2 - the engine re-laid it")
    assert RQP.clip_key(proof, tmp_path / "golden") != key1, "the same window over a moved golden is a different clip"
    # the third defect (T7c, the gather): the base frame unchanged, the ENGINE changed - the motion is the engine's
    engine = tmp_path / "golden" / "docs" / "content-video-engine" / "samples" / "scene-evidence-engine.mjs"
    engine.parent.mkdir(parents=True)
    engine.write_bytes(b"engine v1")
    key2 = RQP.clip_key(proof, tmp_path / "golden")
    engine.write_bytes(b"engine v2 - a gather phase")
    assert RQP.clip_key(proof, tmp_path / "golden") != key2, "the same golden under a changed engine is a different clip"
    # the fourth defect (T14b): a BUILD route's page loads its timeline by name - the same player.html over a rebuilt timeline
    bdir = tmp_path / "golden" / "some-build"; bdir.mkdir()
    (bdir / "player.html").write_bytes(b"<html>"); (bdir / "x.timeline.json").write_bytes(b"{\"drift\": 30}")
    bproof = {"type": "clip", "label": "b", "t0": 0.0, "t1": 1.0, "build": "some-build", "page": "player.html"}
    key3 = RQP.clip_key(bproof, tmp_path / "golden")
    (bdir / "x.timeline.json").write_bytes(b"{\"drift\": 20}")
    assert RQP.clip_key(bproof, tmp_path / "golden") != key3, "the same page over a rebuilt timeline is a different clip"
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


def test_a_clip_proof_may_be_an_mp4_already_on_disk(tmp_path, monkeypatch) -> None:
    """E99 s38's three-way drift proof and an ambient-lane render are mp4s no browser can re-render: a clip proof may
    name `mp4`, the render step copies it, and the sidecar pins the file's own sha256."""
    src = tmp_path / "proof.mp4"
    src.write_bytes(b"mp4 bytes v1")
    monkeypatch.setattr(RQP, "ROOT", tmp_path)
    proof = {"type": "clip", "label": "x", "t0": 0.0, "t1": 4.0, "mp4": "proof.mp4", "route": "composed"}
    out = tmp_path / "clips" / "item-0.mp4"
    assert RQP.render_clip(proof, out) == out and out.read_bytes() == b"mp4 bytes v1"
    key = RQP.clip_key(proof, tmp_path)
    assert key["mp4"] == "proof.mp4" and key["source_sha256"]
    src.write_bytes(b"mp4 bytes v2")
    assert RQP.clip_key(proof, tmp_path)["source_sha256"] != key["source_sha256"], "a changed file is a different clip"
    BRQ.validate_proof("item", proof)   # a clip with an mp4 and no surface / build is a valid proof


def test_a_clip_proof_names_its_build_and_time_range(data, page):
    rec, n, proof = RQP.clip_proofs(data, "p58-hg3-chart-forms")[0]
    card = card_of(page, rec["id"])
    assert f"golden {proof['surface']} - {proof['t0']:g} to {proof['t1']:g} s" in card
    assert f"clips/{RQP.clip_name(rec['id'], n)}" in card or "clip not rendered yet" in card


def test_the_page_makes_no_external_request(page):
    assert not re.search(r'(src|href)="https?://(?!127\.0\.0\.1)', page)
    assert "<link" not in page and "@import" not in page


# ---------------------------------------------------------------- the batch kind (P65 T4)

BATCH_ID = "lab-test-r1-plate-carries-a-card"


def a_candidate(n: int) -> dict:
    return {"id": f"lab:plate-carries-a-card:0000000{n}", "label": f"candidate {n}",
            "one_line": "plate_option:ken +0s, dock_kind:image +2.5s, exit:cut +6s",
            "proof": {"type": "clip", "label": f"the beat {n} carries the card", "t0": 0.0, "t1": 6.0,
                      "build": "some-build-lab-r1/cand", "page": "player.html", "aspect": "9:16",
                      "route": "review_queue_proofs.py --clips: the lab's private build served read-only"}}


def a_batch(n: int = 2, **over) -> dict:
    cands = [a_candidate(i) for i in range(n)]
    rec = {"id": BATCH_ID, "status": "open", "kind": "batch",
           "title": "the recipe lab - plate-carries-a-card, 2 candidates side by side",
           "ids": ["P65 T4", "E99 s68"],
           "judge": "Which of these beats earns its place, and why not the others?",
           "where": [{"label": "the run record", "path": "content/video_engine/effects/lab/batches/smoke-r2.jsonl"}],
           "proofs": [c["proof"] for c in cands], "candidates": cands,
           "options": [], "recommendation": "none - the bit is yours", "blocks": "P65 T5",
           "sources": [".claude/PRPs/plans/P65-THE-RECIPE-LAB.plan.md"], "ruling": "", "was_kind": "", "owed": ""}
    rec.update(over)
    return rec


def with_batch(data: dict, rec: dict | None = None) -> dict:
    out = copy.deepcopy(data)
    out["items"].append(rec if rec is not None else a_batch())
    return out


@pytest.fixture()
def batch_data(data) -> dict:
    return with_batch(data)


def test_the_nine_reasons_are_the_schemas_and_never_a_copy():
    schema = json.loads((ROOT / BRQ.REASON_SCHEMA_REL).read_text(encoding="utf-8"))
    assert BRQ.REASONS == tuple(schema["$defs"]["judgement"]["properties"]["reason"]["enum"])
    assert len(BRQ.REASONS) == 9 and "good" in BRQ.REASONS
    source = (ROOT / "content/video_engine/scripts/build_review_queue.py").read_text(encoding="utf-8")
    for reason in BRQ.REASONS:
        if reason != "good":
            assert reason not in source, f"{reason} is written into the builder; it belongs to the schema only"


def test_a_batch_is_answerable_and_carries_its_own_heading(batch_data):
    assert "batch" in BRQ.KINDS and "batch" in BRQ.ANSWERABLE_KINDS and BRQ.KIND_TITLES["batch"]
    assert BATCH_ID in {i["id"] for i in BRQ.answerable_items(batch_data)}


def test_a_batch_with_no_candidates_is_refused_by_name(data):
    items = with_batch(data, a_batch(candidates=[], proofs=[]))["items"]
    with pytest.raises(BRQ.QueueError, match=rf"{BATCH_ID}: a batch card has no candidates"):
        BRQ.validate(items)


def test_a_batch_candidate_needs_a_clip_proof(data):
    rec = a_batch()
    player = {"type": "player", "label": "the built player", "url": "http://127.0.0.1:8766/player.html",
              "build": "some-build", "confirmed": "it answered"}
    rec["candidates"][1]["proof"] = player
    rec["proofs"] = [c["proof"] for c in rec["candidates"]]
    with pytest.raises(BRQ.QueueError, match=r"needs a CLIP proof - a beat a short could carry \(E99 s60\)"):
        BRQ.validate(with_batch(data, rec)["items"])


def test_a_batch_refuses_a_duplicate_candidate_id(data):
    rec = a_batch()
    rec["candidates"][1]["id"] = rec["candidates"][0]["id"]
    rec["proofs"] = [c["proof"] for c in rec["candidates"]]
    with pytest.raises(BRQ.QueueError, match=rf"{BATCH_ID}: duplicate candidate id"):
        BRQ.validate(with_batch(data, rec)["items"])


def test_a_batch_refuses_a_candidate_id_carrying_the_item_separator(data):
    rec = a_batch()
    rec["candidates"][0]["id"] = f"lab:plate{BRQ.BATCH_SEP}00000000"
    with pytest.raises(BRQ.QueueError, match=r"a candidate id is a non-empty string with no"):
        BRQ.validate(with_batch(data, rec)["items"])


def test_a_batch_refuses_a_stored_reason_off_the_list(data):
    rec = a_batch()
    rec["candidates"][0]["reason"] = "i-did-not-like-it"
    with pytest.raises(BRQ.QueueError, match=r"carries a reason off the list: 'i-did-not-like-it'"):
        BRQ.validate(with_batch(data, rec)["items"])
    rec["candidates"][0]["reason"] = BRQ.REASONS[0]
    BRQ.validate(with_batch(data, rec)["items"])


def test_a_batch_refuses_a_missing_candidate_field(data):
    rec = a_batch()
    del rec["candidates"][0]["one_line"]
    with pytest.raises(BRQ.QueueError, match=rf"{BATCH_ID}: candidate 0 is missing one_line"):
        BRQ.validate(with_batch(data, rec)["items"])


def test_a_batchs_proofs_mirror_its_candidates_so_the_clip_names_line_up(data):
    rec = a_batch()
    rec["proofs"] = list(reversed(rec["proofs"]))
    with pytest.raises(BRQ.QueueError, match=r"mirrors its candidates' clips in order"):
        BRQ.validate(with_batch(data, rec)["items"])


def test_only_a_batch_card_carries_candidates(data):
    items = copy.deepcopy(data["items"])
    rec = next(i for i in items if i["kind"] == "rule")
    rec["candidates"] = a_batch()["candidates"]
    with pytest.raises(BRQ.QueueError, match=r"only a batch card carries candidates \(this one is kind 'rule'\)"):
        BRQ.validate(items)


def test_a_batch_card_asks_one_question_and_gives_every_candidate_its_own_control(batch_data):
    card = card_of(BRQ.render_page(batch_data, ROOT), BATCH_ID)
    assert card.count('<p class="q">') == 1
    assert "Which of these beats earns its place, and why not the others?" in card
    assert card.count('<form class="answer"') == 1, "one card, one plain question, one card-level answer"
    for cand in a_batch()["candidates"]:
        item = f"{BATCH_ID}{BRQ.BATCH_SEP}{cand['id']}"
        assert f'data-item="{item}"' in card, item
        assert BRQ.esc(cand["one_line"]) in card
    assert card.count('<form class="cand"') == 2
    for choice in BRQ.BATCH_CHOICES:
        assert card.count(f'value="{choice}"') == 2
    for reason in BRQ.REASONS:
        assert card.count(f'<option value="{reason}">') == 2
    assert card.count('<option value="" disabled selected>choose a reason</option>') == 2


def test_a_batch_cards_candidates_each_show_their_own_clip(batch_data):
    card = card_of(BRQ.render_page(batch_data, ROOT), BATCH_ID)
    for n, cand in enumerate(a_batch()["candidates"]):
        assert BRQ.esc(cand["proof"]["label"]) in card
        assert f"clips/{RQP.clip_name(BATCH_ID, n)}" in card or "clip not rendered yet" in card
    assert card.count('class="proof clip') == 2


def test_the_markdown_row_lists_every_candidate_with_its_reason_controls(batch_data):
    md = BRQ.render_markdown(batch_data)
    row = next(line for line in md.splitlines() if line.startswith(f"| `{BATCH_ID}` |"))
    for cand in a_batch()["candidates"]:
        assert f"`{cand['id']}`" in row and cand["one_line"] in row
    assert "approve / deny" in row
    assert f"## {BRQ.KIND_TITLES['batch']} (1)" in md


def test_an_exploration_or_calibration_candidate_says_so_on_the_card(data):
    rec = a_batch()
    rec["candidates"][0]["exploration"] = True
    rec["candidates"][1]["calibration"] = True
    rec["candidates"][1]["reason"] = "good"
    page_card = card_of(BRQ.render_page(with_batch(data, rec), ROOT), BATCH_ID)
    assert '<span class="tag exploration">exploration</span>' in page_card
    assert '<span class="tag calibration">calibration</span>' in page_card
    assert "judged before" in page_card
    row = next(line for line in BRQ.render_markdown(with_batch(data, rec)).splitlines()
               if line.startswith(f"| `{BATCH_ID}` |"))
    assert "**exploration**" in row and "**calibration**" in row


def test_the_live_queue_carries_both_of_p65s_human_gate_rows():
    """T4's own evidence: HG1 is a real batch card with a clip, HG2 is owed until T8's re-proof run lands."""
    live = {i["id"]: i for i in BRQ.load_data(DATA)["items"]}
    hg1 = live["lab-smoke-r2-plate-carries-a-card"]
    assert hg1["kind"] == "batch" and hg1["status"] == "open" and "P65 HG1" in hg1["ids"]
    assert hg1["candidates"] and all(c["proof"]["type"] == "clip" for c in hg1["candidates"])
    hg2 = live["p65-hg2-the-reproved-set-and-m38"]
    assert hg2["kind"] in ("owed", "batch") and "P65 HG2" in hg2["ids"]
    if hg2["kind"] == "owed":
        assert "reproof-r1" in hg2["owed"]


def test_a_candidates_answer_posts_through_the_same_door(tmp_path):
    """The server's ONE new branch, end to end: a good candidate answer appends one line; a bad reason, an unknown
    candidate and a choice off approve / deny are refused by name and append nothing."""
    live = tmp_path / "queue.json"
    live.write_text(json.dumps(with_batch(BRQ.load_data(FIXTURE))), encoding="utf-8")
    answers = tmp_path / "answers.jsonl"
    answers.write_text("", encoding="utf-8")
    httpd = SRQ.make_server(0, live, tmp_path / "page", answers, quiet=True, probe=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    item = f"{BATCH_ID}{BRQ.BATCH_SEP}{a_candidate(0)['id']}"
    try:
        code, body = post(base, {"item": item, "choice": "approve", "note": "good: the plate holds its six seconds"})
        assert code == 200 and body["ok"] is True, body
        rows = lines_of(answers)
        assert len(rows) == 1 and rows[0]["item"] == item and rows[0]["choice"] == "approve"
        for payload, reason in (
                ({"item": item, "choice": "approve", "note": "it felt nice"}, "opens with a reason from the list"),
                ({"item": item, "choice": "hold", "note": "good: x"}, "invalid choice 'hold'"),
                ({"item": f"{BATCH_ID}#lab:plate-carries-a-card:deadbeef", "choice": "deny", "note": "too-fast: x"},
                 "unknown candidate 'lab:plate-carries-a-card:deadbeef'"),
                ({"item": f"r26-126-push-word#lab:x:00000000", "choice": "deny", "note": "too-fast: x"},
                 "unknown batch 'r26-126-push-word'")):
            code, body = post(base, payload)
            assert code == 400 and body["ok"] is False and reason in body["error"], body
        assert len(lines_of(answers)) == 1, "a refused candidate answer appends nothing"
        # the second answer on the same candidate supersedes it in GET /answers, the file keeping both
        post(base, {"item": item, "choice": "deny", "note": "too-slow: on a second watch it sits"})
        code, latest = request(f"{base}/answers")
        assert latest[item]["choice"] == "deny" and len(lines_of(answers)) == 2
    finally:
        httpd.shutdown()
        httpd.server_close()


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
# ---------------------------------------------------------------- the critic (P67 T5, E99 s68)

PLAYER_PROOF = {"type": "player", "label": "the whole cut", "url": "http://127.0.0.1:8760/",
                "build": "build-x", "confirmed": "served 2026-09-17"}
WHOLE_CUT_CLIP = {"type": "clip", "label": "the whole cut", "t0": 0.0, "t1": 77.6, "route": "player",
                  "build": "build-x"}
BEAT_CLIP = {"type": "clip", "label": "the calendar beat", "t0": 12.0, "t1": 20.5, "route": "player",
             "build": "build-x"}
OWES_A_CRITIC = (r"a whole-cut watch owes a critic report \(build-x/CRITIC\.md\) - E99 s68; "
                 r"run the director-critic pass or make the proof a clip of the beat")
A_REPORT = "# CRITIC - mechanism correctness 6/14, rows attributed 19/32"


def one_watch(data: dict, proof: dict, **over) -> dict:
    """One OPEN watch record off the fixture, carrying exactly the proof under test (it is validated ALONE, so the
    fixture's own whole-cut players never warn or raise first)."""
    rec = copy.deepcopy(next(i for i in data["items"] if i["status"] == "open" and i["kind"] == "watch"))
    rec["proofs"] = [proof]
    rec.pop("critic", None)
    rec.update(over)
    return rec


def run_write(tmp: Path, data_path: Path, root: Path) -> int:
    return BRQ.main(["--write", "--no-probe", "--data", str(data_path), "--md", str(tmp / "REVIEW-QUEUE.md"),
                     "--out", str(tmp / "page"), "--root", str(root)])


def test_the_constants_are_the_calibrated_whole_cut_and_the_warn_first_switch():
    """P67 T5 ships the rule as a WARN; P67 T7 flips CRITIC_REQUIRED to True in the commit that gives the live card
    its critic path. 30 s sits between one-shot #3's 77.6 s whole cut and every beat clip in the live data."""
    assert BRQ.WHOLE_CUT_S == 30.0
    assert BRQ.CRITIC_REQUIRED is False
    live = BRQ.load_data(DATA)
    beats = [p["t1"] - p["t0"] for i in BRQ.open_items(live) for p in i.get("proofs") or []
             if p["type"] == "clip" and p["t1"] - p["t0"] < BRQ.WHOLE_CUT_S]
    assert beats and max(beats) < BRQ.WHOLE_CUT_S


@pytest.mark.parametrize("proof", [PLAYER_PROOF, WHOLE_CUT_CLIP], ids=["player", "77.6s-clip"])
def test_a_whole_cut_watch_with_no_critic_warns_by_name_while_the_constant_is_false(data, monkeypatch, proof):
    monkeypatch.setattr(BRQ, "CRITIC_REQUIRED", False)
    rec = one_watch(data, proof)
    BRQ.validate([rec])
    assert len(BRQ.WARNINGS) == 1
    assert re.fullmatch(rf"WARN {re.escape(rec['id'])}: {OWES_A_CRITIC}", BRQ.WARNINGS[0])


@pytest.mark.parametrize("proof", [PLAYER_PROOF, WHOLE_CUT_CLIP], ids=["player", "77.6s-clip"])
def test_a_whole_cut_watch_with_no_critic_is_refused_by_name_once_the_constant_flips(data, monkeypatch, proof):
    monkeypatch.setattr(BRQ, "CRITIC_REQUIRED", True)
    rec = one_watch(data, proof)
    with pytest.raises(BRQ.QueueError, match=rf"{re.escape(rec['id'])}: {OWES_A_CRITIC}"):
        BRQ.validate([rec])


def test_a_beat_clip_and_a_ruled_record_owe_no_critic(data, monkeypatch):
    monkeypatch.setattr(BRQ, "CRITIC_REQUIRED", True)
    BRQ.validate([one_watch(data, BEAT_CLIP)])
    assert BRQ.WARNINGS == []
    ruled = copy.deepcopy(next(i for i in data["items"] if i["id"] == RULED_ID))
    ruled["kind"], ruled["proofs"] = "watch", [PLAYER_PROOF]
    BRQ.validate([ruled])
    assert BRQ.WARNINGS == []


def test_a_present_critic_is_accepted_by_validate_without_touching_the_disk(data, monkeypatch):
    """The DISK check is the writer's (a fixture names no report on disk), so validate takes a repo-relative name."""
    monkeypatch.setattr(BRQ, "CRITIC_REQUIRED", True)
    BRQ.validate([one_watch(data, PLAYER_PROOF, critic="build-x/CRITIC.md")])
    assert BRQ.WARNINGS == []
    for bad in ["", "   ", str(ROOT / "build-x" / "CRITIC.md")]:
        with pytest.raises(BRQ.QueueError, match="'critic' names the director-critic report repo-relative"):
            BRQ.validate([one_watch(data, PLAYER_PROOF, critic=bad)])


def test_the_writer_refuses_a_critic_path_that_is_not_on_disk_or_not_under_the_build(tmp_path, data, capsys):
    rec = one_watch(data, PLAYER_PROOF, critic="build-x/CRITIC.md")
    data_path = write_data(tmp_path / "queue.json", {"items": [rec]})
    assert run_write(tmp_path, data_path, tmp_path) == 2
    assert f"{rec['id']}: the critic report build-x/CRITIC.md is not on disk" in capsys.readouterr().err
    (tmp_path / "build-x").mkdir()
    (tmp_path / "build-x" / "CRITIC.md").write_text(A_REPORT, encoding="utf-8")
    assert run_write(tmp_path, data_path, tmp_path) == 0, "a report on disk under the build passes"
    rec["critic"] = "CRITIC.md"
    (tmp_path / "CRITIC.md").write_text(A_REPORT, encoding="utf-8")
    write_data(data_path, {"items": [rec]})
    capsys.readouterr()
    assert run_write(tmp_path, data_path, tmp_path) == 2
    assert (f"{rec['id']}: the critic report CRITIC.md lives outside the proof's build build-x"
            in capsys.readouterr().err)


def test_the_live_queue_still_validates_and_warns_on_exactly_its_two_whole_cut_watches(capsys):
    BRQ.load_data(DATA)
    assert ([line.split(":", 1)[0].removeprefix("WARN ") for line in BRQ.WARNINGS]
            == ["one-shot-3-fable-memory-calendar", "p66-hg1-the-first-generated-base"])
    assert all("CRITIC.md) - E99 s68" in line for line in BRQ.WARNINGS)
    assert BRQ.main(["--check"]) == 0, "a WARN never fails the check while CRITIC_REQUIRED is False"
    out = capsys.readouterr().out
    assert out.count("WARN ") == 2 and "one-shot-3-fable-memory-calendar" in out

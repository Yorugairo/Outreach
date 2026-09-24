"""THE RESEARCH CLAIMS GATE, pinned (operator 2026-09-24: "gemini hallucinates a lot, so we need some sort of force system
in place to actually enforce its checks/gates").

R26-306 is the case: two fabricated TrendForce URLs (404), four DOIs unregistered or resolving to other books, a mis-typed
filing figure ($115,173M against the filing's $115,186M) and rows self-marked CONFIRMED with nothing on disk. Every test
here builds a run folder in `tmp_path` and serves its "web" from a localhost `http.server` - the fetch path is the real one,
the network is not. The DOI resolvers are the same fixture server (the verifier's `--doi-api` / `--crossref-api`).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import verify_research_claims as VR  # noqa: E402

PAGE = ("<html><head><title>NVIDIA 10-K</title><script>var x = 'Data Center $ 999';</script></head><body>"
        "<p>Revenue by end market.</p><table><tr><td>Data Center</td><td>$</td><td>115,186</td>"
        "<td>$</td><td>47,525</td></tr></table>"
        "<p>In 2024, NVIDIA vastly led the data center GPU market, holding 92% of the market share, with AMD at 4%.</p>"
        "<p>The company raised $1.2 billion in its Series C round &#8212; the largest to date.</p>"
        + "<p>filler text to make the page a real page.</p>" * 20 + "</body></html>")


# --------------------------------------------------------------------------- the fixture web


class _Web(BaseHTTPRequestHandler):
    routes: dict[str, tuple[int, str, bytes]] = {}

    def do_GET(self):  # noqa: N802 - http.server's name
        status, ctype, body = self.routes.get(self.path, (404, "text/html", b"<html>not found</html>"))
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # the test output stays clean
        pass


@pytest.fixture()
def web():
    routes: dict[str, tuple[int, str, bytes]] = {}
    handler = type("Web", (_Web,), {"routes": routes})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        yield base, routes
    finally:
        server.shutdown()
        server.server_close()


def html(text: str) -> tuple[int, str, bytes]:
    return 200, "text/html; charset=utf-8", text.encode("utf-8")


def doi_routes(routes: dict, doi: str, *, registered: bool, title: str | None = None, authors: tuple[str, ...] = ()) -> None:
    handle = {"responseCode": 1, "handle": doi} if registered else {"responseCode": 100, "handle": doi}
    routes[f"/api/handles/{doi}"] = (200 if registered else 404, "application/json", json.dumps(handle).encode())
    if title is not None:
        msg = {"message": {"title": [title], "author": [{"family": a} for a in authors], "DOI": doi}}
        routes[f"/works/{doi}"] = (200, "application/json", json.dumps(msg).encode())


# --------------------------------------------------------------------------- the run folder


def claim(cid: str, **over) -> dict:
    base = {"id": cid, "claim": "NVIDIA Data Center revenue, FY2025", "value": "115,186", "unit": "USD million",
            "period": "FY2025", "source_title": "NVIDIA Form 10-K FY2025", "publisher": "NVIDIA / SEC", "url": None,
            "retrieved_at": "2026-09-24", "quote": "Data Center $ 115,186", "sources_file": None, "sha256": None,
            "tier_declared": "CONFIRMED", "notes": ""}
    base.update(over)
    return base


def run(tmp_path: Path, claims: list[dict], files: dict[str, str | bytes] | None = None) -> Path:
    folder = tmp_path / "run"
    (folder / "sources").mkdir(parents=True, exist_ok=True)
    for name, body in (files or {}).items():
        data = body.encode("utf-8") if isinstance(body, str) else body
        (folder / "sources" / name).write_bytes(data)
    (folder / "claims.jsonl").write_text("".join(json.dumps(c) + "\n" for c in claims), encoding="utf-8")
    return folder


def sha(body: str | bytes) -> str:
    return hashlib.sha256(body.encode("utf-8") if isinstance(body, str) else body).hexdigest()


def verify(folder: Path, base: str | None = None, *extra: str) -> tuple[int, dict]:
    argv = [str(folder), "--delay", "0", "--timeout", "5", "--retries", "0", *extra]
    if base:
        argv += ["--doi-api", f"{base}/api/handles/", "--crossref-api", f"{base}/works/"]
    code = VR.main(argv)
    return code, json.loads((folder / "VERIFY.json").read_text(encoding="utf-8"))


def by_id(report: dict, cid: str) -> dict:
    return next(c for c in report["claims"] if c["id"] == cid)


# --------------------------------------------------------------------------- URL


def test_a_fabricated_url_that_404s_fails_the_claim_and_the_reply(tmp_path, web):
    base, routes = web
    folder = run(tmp_path, [claim("c1", url=f"{base}/presscenter/news/20241018-12345.html")])

    code, report = verify(folder, base)

    c1 = by_id(report, "c1")
    assert code == 1 and report["verdict"] == "FAIL"
    assert c1["checks"]["url"]["status"] == "FAIL" and c1["checks"]["url"]["http"] == 404
    assert c1["tier_earned"] == "REJECTED"
    assert (folder / "VERIFY.md").read_text(encoding="utf-8").count("c1") >= 1


def test_a_live_page_carrying_the_quote_and_the_value_is_confirmed(tmp_path, web):
    base, routes = web
    routes["/10k.htm"] = html(PAGE)
    folder = run(tmp_path, [claim("c1", url=f"{base}/10k.htm")])

    code, report = verify(folder, base)

    c1 = by_id(report, "c1")
    assert code == 0 and report["verdict"] == "PASS", report["fails"]
    assert c1["checks"]["url"]["status"] == "PASS" and c1["checks"]["url"]["final_url"].endswith("/10k.htm")
    assert c1["checks"]["quote_web"]["status"] == "PASS" and c1["checks"]["value"]["status"] == "PASS"
    assert c1["tier_earned"] == "CONFIRMED" and not c1["overclaim"]


def test_a_quote_that_is_not_on_the_page_fails(tmp_path, web):
    base, routes = web
    routes["/10k.htm"] = html(PAGE)
    folder = run(tmp_path, [claim("c1", url=f"{base}/10k.htm", quote="Data Center revenue grew to $115,186 million")])

    code, report = verify(folder, base)

    assert code == 1 and by_id(report, "c1")["checks"]["quote_web"]["status"] == "FAIL"


def test_text_inside_a_script_tag_is_not_page_text(tmp_path, web):
    base, routes = web
    routes["/10k.htm"] = html(PAGE)
    folder = run(tmp_path, [claim("c1", url=f"{base}/10k.htm", quote="Data Center $ 999", value="999")])

    code, report = verify(folder, base)

    assert code == 1 and by_id(report, "c1")["checks"]["quote_web"]["status"] == "FAIL"


def test_a_value_that_is_not_in_the_quote_fails_the_mis_typed_filing_figure(tmp_path, web):
    base, routes = web
    routes["/10k.htm"] = html(PAGE)
    folder = run(tmp_path, [claim("c1", url=f"{base}/10k.htm", value="115,173")])   # the R26-306 typo

    code, report = verify(folder, base)

    c1 = by_id(report, "c1")
    assert code == 1 and c1["checks"]["quote_web"]["status"] == "PASS"
    assert c1["checks"]["value"]["status"] == "FAIL" and c1["tier_earned"] == "REJECTED"


def test_a_paywalled_403_page_declared_confirmed_is_an_overclaim(tmp_path, web):
    base, routes = web
    routes["/idc.htm"] = (403, "text/html", b"<html>login required</html>")
    folder = run(tmp_path, [claim("c1", url=f"{base}/idc.htm")])

    code, report = verify(folder, base)

    c1 = by_id(report, "c1")
    assert c1["checks"]["url"]["status"] == "UNVERIFIABLE" and c1["checks"]["url"]["http"] == 403
    assert c1["tier_earned"] == "UNSOURCED" and c1["overclaim"] is True
    assert code == 1 and any("overclaim" in f for f in report["fails"])


def test_the_same_403_page_declared_unsourced_honestly_passes(tmp_path, web):
    base, routes = web
    routes["/idc.htm"] = (403, "text/html", b"<html>login required</html>")
    folder = run(tmp_path, [claim("c1", url=f"{base}/idc.htm", tier_declared="UNSOURCED")])

    code, report = verify(folder, base)

    assert code == 0, report["fails"]
    assert by_id(report, "c1")["tier_earned"] == "UNSOURCED" and not by_id(report, "c1")["overclaim"]


def test_a_secondary_source_earns_plausible_not_confirmed(tmp_path, web):
    base, routes = web
    routes["/dcd.htm"] = html(PAGE)
    folder = run(tmp_path, [claim("c1", url=f"{base}/dcd.htm", source_kind="secondary")])

    code, report = verify(folder, base)

    c1 = by_id(report, "c1")
    assert c1["tier_earned"] == "PLAUSIBLE" and c1["overclaim"] is True and code == 1


# --------------------------------------------------------------------------- DOI


def test_an_unregistered_doi_fails(tmp_path, web):
    base, routes = web
    doi_routes(routes, "10.1017/S002205070006041X", registered=False)
    folder = run(tmp_path, [claim("r1", doi="10.1017/S002205070006041X", source_title="The coming of the railway",
                                  quote="", value="44", unit="GBP million", tier_declared="PLAUSIBLE")])

    code, report = verify(folder, base)

    r1 = by_id(report, "r1")
    assert code == 1 and r1["checks"]["doi"]["status"] == "FAIL" and "not registered" in r1["checks"]["doi"]["detail"]


def test_a_doi_that_resolves_to_another_book_is_misattributed(tmp_path, web):
    base, routes = web
    doi_routes(routes, "10.1017/CBO9780511561085", registered=True, title="Durham Priory 1400-1450",
               authors=("Dobson",))
    folder = run(tmp_path, [claim("r1", doi="10.1017/CBO9780511561085", source_title="British Historical Statistics",
                                  author="Mitchell", quote="", value="44", unit="GBP million", tier_declared="PLAUSIBLE")])

    code, report = verify(folder, base)

    r1 = by_id(report, "r1")
    assert code == 1 and r1["checks"]["doi"]["status"] == "FAIL" and "misattributed" in r1["checks"]["doi"]["detail"]


def test_a_registered_doi_with_its_own_title_passes_the_doi_check(tmp_path, web):
    base, routes = web
    doi_routes(routes, "10.2307/2552228", registered=True, title="Railway Investment in Britain, 1825-1875",
               authors=("Kenwood",))
    folder = run(tmp_path, [claim("r1", doi="10.2307/2552228", source_title="Railway investment in Britain 1825-1875",
                                  author="Kenwood", quote="railway investment", value=None, unit=None,
                                  tier_declared="PLAUSIBLE")])

    code, report = verify(folder, base)

    r1 = by_id(report, "r1")
    assert r1["checks"]["doi"]["status"] == "PASS" and r1["tier_earned"] == "PLAUSIBLE"
    assert code == 0, report["fails"]


# --------------------------------------------------------------------------- the source on disk


def test_a_source_on_disk_confirms_offline(tmp_path):
    folder = run(tmp_path, [claim("c1", sources_file="sources/10k.htm", sha256=sha(PAGE))], {"10k.htm": PAGE})

    code, report = verify(folder, None, "--offline")

    c1 = by_id(report, "c1")
    assert code == 0, report["fails"]
    assert c1["checks"]["disk"]["status"] == "PASS" and c1["tier_earned"] == "CONFIRMED"
    assert report["offline"] is True and "url" not in c1["checks"]


def test_a_sha256_mismatch_fails(tmp_path):
    folder = run(tmp_path, [claim("c1", sources_file="sources/10k.htm", sha256="0" * 64)], {"10k.htm": PAGE})

    code, report = verify(folder, None, "--offline")

    c1 = by_id(report, "c1")
    assert code == 1 and c1["checks"]["disk"]["status"] == "FAIL" and "sha256" in c1["checks"]["disk"]["detail"]


def test_a_named_source_file_that_is_absent_fails(tmp_path):
    folder = run(tmp_path, [claim("c1", sources_file="sources/ghost.htm", sha256="0" * 64)])

    code, report = verify(folder, None, "--offline")

    assert code == 1 and by_id(report, "c1")["checks"]["disk"]["status"] == "FAIL"


def test_the_quote_must_be_in_the_saved_file_too(tmp_path):
    body = "<html><body><p>Something else entirely.</p></body></html>"
    folder = run(tmp_path, [claim("c1", sources_file="sources/10k.htm", sha256=sha(body))], {"10k.htm": body})

    code, report = verify(folder, None, "--offline")

    assert code == 1 and "quote" in by_id(report, "c1")["checks"]["disk"]["detail"]


def test_offline_a_web_only_confirmed_claim_is_an_overclaim(tmp_path):
    folder = run(tmp_path, [claim("c1", url="https://example.invalid/10k.htm")])

    code, report = verify(folder, None, "--offline")

    assert code == 1 and by_id(report, "c1")["tier_earned"] == "UNSOURCED" and by_id(report, "c1")["overclaim"]


def test_a_pdf_on_disk_is_read_as_text(tmp_path):
    pdf = minimal_pdf("Railway investment reached 44 million pounds in 1847")
    folder = run(tmp_path, [claim("r1", sources_file="sources/o.pdf", sha256=sha(pdf), value="44", unit="GBP million",
                                  quote="investment reached 44 million pounds")], {"o.pdf": pdf})

    code, report = verify(folder, None, "--offline")

    assert code == 0, report["fails"]
    assert by_id(report, "r1")["checks"]["disk"]["status"] == "PASS"


def minimal_pdf(text: str) -> bytes:
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin-1")
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
            b"/Resources << /Font << /F1 5 0 R >> >> >>",
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for n, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{n} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{o:010d} 00000 n \n".encode() for o in offsets)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


# --------------------------------------------------------------------------- DERIVED


def test_a_derived_value_recomputes_from_its_inputs(tmp_path):
    ocf = claim("ocf", value="64,089", quote="operating activities 64,089", sources_file="sources/cf.htm")
    capex = claim("capex", value="3,236", quote="property and equipment (3,236)", sources_file="sources/cf.htm")
    body = "<p>Net cash provided by operating activities 64,089</p><p>Purchases of property and equipment (3,236)</p>"
    for c in (ocf, capex):
        c["sha256"] = sha(body)
    fcf = claim("fcf", value="60,853", quote="", derived_from=["ocf", "capex"], formula="{ocf} - {capex}")
    folder = run(tmp_path, [ocf, capex, fcf], {"cf.htm": body})

    code, report = verify(folder, None, "--offline")

    f = by_id(report, "fcf")
    assert code == 0, report["fails"]
    assert f["checks"]["derived"]["status"] == "PASS" and f["tier_earned"] == "CONFIRMED"


def test_a_derived_value_that_does_not_recompute_fails(tmp_path):
    a = claim("a", value="48,710", quote="Hyperscale 48,710", sources_file="sources/s.htm")
    b = claim("b", value="89,023", quote="Data Center 89,023", sources_file="sources/s.htm")
    body = "<p>Hyperscale 48,710</p><p>Data Center 89,023</p>"
    for c in (a, b):
        c["sha256"] = sha(body)
    good = claim("share", value="54.7", unit="%", quote="", derived_from=["a", "b"], formula="{a} / {b} * 100")
    bad = claim("bad", value="56.1", unit="%", quote="", derived_from=["a", "b"], formula="{a} / {b} * 100")
    folder = run(tmp_path, [a, b, good, bad], {"s.htm": body})

    code, report = verify(folder, None, "--offline")

    assert by_id(report, "share")["checks"]["derived"]["status"] == "PASS"
    assert by_id(report, "bad")["checks"]["derived"]["status"] == "FAIL" and code == 1


def test_a_formula_may_not_call_anything(tmp_path):
    a = claim("a", value="1", quote="1", sources_file=None)
    evil = claim("e", value="1", quote="", derived_from=["a"], formula="__import__('os').system('echo hi')")
    folder = run(tmp_path, [a, evil])

    code, report = verify(folder, None, "--offline")

    assert code == 1 and by_id(report, "e")["checks"]["derived"]["status"] == "FAIL"


# --------------------------------------------------------------------------- the reply as a whole


def test_a_run_with_no_claims_file_fails(tmp_path):
    folder = tmp_path / "run"
    folder.mkdir()

    assert VR.main([str(folder), "--offline"]) == 1


def test_a_claim_missing_a_required_field_or_a_duplicate_id_fails(tmp_path):
    c = claim("c1", sources_file="sources/10k.htm", sha256=sha(PAGE))
    no_quote = {k: v for k, v in claim("c2").items() if k != "quote"}
    folder = run(tmp_path, [c, dict(c), no_quote], {"10k.htm": PAGE})

    code, report = verify(folder, None, "--offline")

    assert code == 1
    assert any("duplicate" in f for f in report["fails"]) and any("c2" in f and "quote" in f for f in report["fails"])


def test_a_claim_declared_rejected_discloses_and_does_not_fail_the_reply(tmp_path, web):
    base, routes = web
    folder = run(tmp_path, [claim("c1", url=f"{base}/dead.html", tier_declared="REJECTED")])

    code, report = verify(folder, base)

    assert code == 0, report["fails"]
    assert by_id(report, "c1")["checks"]["url"]["status"] == "FAIL"


def test_require_pass_refuses_a_claims_file_edited_after_the_gate(tmp_path):
    folder = run(tmp_path, [claim("c1", sources_file="sources/10k.htm", sha256=sha(PAGE))], {"10k.htm": PAGE})
    assert verify(folder, None, "--offline")[0] == 0
    assert VR.main([str(folder), "--require-pass"]) == 0

    with (folder / "claims.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(claim("c9", value="1")) + "\n")

    assert VR.main([str(folder), "--require-pass"]) == 1


# --------------------------------------------------------------------------- number and text normalisation


@pytest.mark.parametrize("value, unit, quote, ok", [
    ("1,234.5", "", "grew to 1234.5 units", True),
    ("1234.5", "", "grew to 1,234.5 units", True),
    ("1200000000", "USD", "raised $1.2 billion", True),
    ("1.2", "USD billion", "raised $1.2 billion", True),
    ("1.2", "USD billion", "raised $1,200 million", True),
    ("1.2", "USD billion", "raised $1.23 billion", True),       # the claim rounds the source: allowed
    ("1.23", "USD billion", "raised $1.2 billion", False),      # the claim invents a digit: refused
    ("115,173", "USD million", "Data Center $ 115,186", False),
    ("92", "%", "holding 92% of the market", True),
    ("98", "%", "a 98 percent market share", True),
    ("3.76", "million", "shipped 3.76m GPUs", True),
    ("-3,236", "USD million", "equipment (3,236)", True),
    ("44", "GBP million", "about £44M in 1847", True),
    ("465", "GBP million", "GDP was 628.3", False),
])
def test_value_in_quote(value, unit, quote, ok):
    assert VR.value_in_quote(value, unit, quote)[0] is ok


def test_quote_matching_folds_case_dashes_quotes_and_spacing_and_honours_an_ellipsis():
    page = VR.normalise("In 2024, NVIDIA “vastly” led the data‑center GPU market,\n holding 92%")
    assert VR.quote_in("in 2024 … nvidia \"vastly\" led the data-center gpu market, holding 92%", page)
    assert not VR.quote_in("in 2025 … nvidia", page)


# --------------------------------------------------------------------------- the enforcement: bridge_send attaches the gate

import bridge_daemon as BD  # noqa: E402
import bridge_env as BE  # noqa: E402
import bridge_send as BS  # noqa: E402

GATE = "python content/video_engine/scripts/verify_research_claims.py"


@pytest.fixture()
def no_ide(monkeypatch):
    """A dry-run send without the live IDE: the gemini resolver is stubbed, nothing else is."""
    monkeypatch.setattr(BS, "resolve_gemini", lambda args, order, lines: ({}, ["agy.exe", "agentapi"]))


def send(tmp_path: Path, *extra: str) -> dict:
    brief = tmp_path / "order.md"
    brief.write_text("# R26-999 research\n\nFind NVIDIA's share.\n", encoding="utf-8")
    assert BS.main(["--lane", "gemini", "--brief-file", str(brief), "--title", "NVDA share R26-999",
                    "--repo", str(tmp_path), "--dry-run", "--json", *extra]) == 0
    return json.loads((BE.packet_dir(tmp_path, BE.packet_id(brief.read_text(encoding="utf-8")), "queue")
                       / "order.json").read_text(encoding="utf-8"))


def test_a_gemini_report_landed_order_carries_the_claims_gate_by_default(tmp_path, no_ide):
    order = send(tmp_path, "--reply-shape", "report-landed")

    assert order["research_run"] == "docs/research/runs/nvda-share-r26-999"
    assert order["verify"] == f"{GATE} docs/research/runs/nvda-share-r26-999"
    assert "THE RESEARCH CLAIMS GATE" in order["brief"] and "docs/research/runs/nvda-share-r26-999/" in order["brief"]
    assert len(order["brief"].encode("utf-8")) <= BS.BRIEF_CAP_BYTES


def test_a_named_research_run_makes_any_order_a_gated_report(tmp_path, no_ide):
    order = send(tmp_path, "--research-run", "docs/research/runs/r26-999")

    assert order["replyShape"] == "report-landed" and order["research_run"] == "docs/research/runs/r26-999"
    assert order["verify"] == f"{GATE} docs/research/runs/r26-999"


def test_the_gate_is_refused_only_out_loud(tmp_path, no_ide, capsys):
    order = send(tmp_path, "--reply-shape", "report-landed", "--no-claims-gate")

    assert "verify" not in order and "research_run" not in order
    assert "THE RESEARCH CLAIMS GATE" not in order["brief"]


def test_a_second_verify_command_cannot_replace_the_gate(tmp_path, no_ide):
    with pytest.raises(SystemExit):
        send(tmp_path, "--reply-shape", "report-landed", "--verify", "python other.py")


def test_a_non_research_shape_is_left_alone(tmp_path, no_ide):
    order = send(tmp_path, "--reply-shape", "paths-written")

    assert "research_run" not in order and "verify" not in order


# --------------------------------------------------------------------------- the enforcement: the daemon's revision loop


@pytest.fixture()
def quiet(monkeypatch):
    seen: list = []
    monkeypatch.setattr(BD, "toast", lambda title, body: bool(seen.append((title, body))))
    monkeypatch.setattr(BD, "run_tier1", lambda repo, folder: pytest.fail("a research gate failure never goes to tier 1"))
    monkeypatch.setattr(BD, "send_packet", lambda tick, folder, order: pytest.fail("no test sends to a live lane"))
    return seen


def research_repo(tmp_path: Path, monkeypatch, verify_exit: int) -> Path:
    for state in BE.STATES:
        (tmp_path / BE.BRIDGE_ROOT / state).mkdir(parents=True, exist_ok=True)
    run_dir = tmp_path / "docs/research/runs/r1"
    run_dir.mkdir(parents=True)
    (run_dir / "REPORT.md").write_text("report\n", encoding="utf-8")
    (run_dir / "VERIFY.json").write_text(json.dumps({"verdict": "FAIL", "fails": [
        "c1: url: HTTP 404", "c2: overclaim: declared CONFIRMED, earned UNSOURCED"]}), encoding="utf-8")
    monkeypatch.setattr(BD.handlers, "run_command", lambda command, repo: (verify_exit, "verify_research_claims: FAIL"))
    return tmp_path


def research_reply(repo: Path, packet: str, minutes_ago: float = 45, **order_extra) -> Path:
    folder = BE.packet_dir(repo, packet, "replied")
    order = {"packetId": packet, "lane": "gemini", "replyShape": "paths-written", "title": "NVDA share",
             "verify": f"{GATE} docs/research/runs/r1", "research_run": "docs/research/runs/r1", **order_extra}
    BE.write_json(folder / "order.json", order)
    BE.write_json(folder / "conversation.json", {"conversationId": "c-77"})
    when = (dt.datetime.now().astimezone() - dt.timedelta(minutes=minutes_ago)).isoformat(timespec="seconds")
    (folder / "reply.md").write_text(f"<!-- lane: gemini; conversationId: c-77; landedAt: {when} -->\n\n"
                                     f"PATHS WRITTEN: docs/research/runs/r1/REPORT.md\n", encoding="utf-8")
    return folder


def queued_orders(repo: Path) -> list[dict]:
    return [json.loads((f / "order.json").read_text(encoding="utf-8")) for f in (repo / BE.BRIDGE_ROOT / "queue").iterdir()]


def test_a_failed_research_verify_goes_back_to_the_lane_as_a_revision_order(tmp_path, monkeypatch, quiet):
    repo = research_repo(tmp_path, monkeypatch, verify_exit=1)
    folder = research_reply(repo, "p-research")

    BD.tick_once(repo, dict(BD.DEFAULTS))

    [rev] = queued_orders(repo)
    assert rev["conversationId"] == "c-77" and rev["revises"] == "p-research" and rev["revisionRound"] == 1
    assert rev["revisionChain"] == ["p-research"] and rev["research_run"] == "docs/research/runs/r1"
    assert rev["verify"].startswith(GATE) and "c1: url: HTTP 404" in rev["brief"] and "Revision 1 of 2" in rev["brief"]
    assert (folder / BD.REVISION_MARKER).exists() and quiet == []
    monkeypatch.setattr(BD, "send_packet", lambda tick, folder, order: {"status": "sent"})   # the queued revision, not sent
    BD.tick_once(repo, dict(BD.DEFAULTS))   # the original waits: no tier 1, no second revision
    assert len(queued_orders(repo)) == 1


def test_a_revision_that_passes_closes_the_original(tmp_path, monkeypatch, quiet):
    repo = research_repo(tmp_path, monkeypatch, verify_exit=1)
    research_reply(repo, "p-research")
    BD.tick_once(repo, dict(BD.DEFAULTS))
    [rev] = queued_orders(repo)
    BE.move_packet(rev["packetId"], "queue", "replied", repo=repo)
    research_reply(repo, rev["packetId"], **{k: rev[k] for k in ("revises", "revisionRound", "revisionChain")})
    monkeypatch.setattr(BD.handlers, "run_command", lambda command, repo: (0, "verify_research_claims: PASS"))

    BD.tick_once(repo, dict(BD.DEFAULTS))

    assert BE.packet_dir(repo, rev["packetId"], "done").is_dir()
    assert BE.packet_dir(repo, "p-research", "done").is_dir(), "the gated original closes with its revision"


def test_two_failed_revisions_escalate_and_never_queue_a_third(tmp_path, monkeypatch, quiet):
    repo = research_repo(tmp_path, monkeypatch, verify_exit=1)
    folder = research_reply(repo, "p-rev2", revises="p-research", revisionRound=2, revisionChain=["p-research", "p-rev1"])

    BD.tick_once(repo, dict(BD.DEFAULTS))

    assert queued_orders(repo) == []
    assert "research-gate" in json.loads((folder / "escalated.json").read_text(encoding="utf-8"))["reasons"]
    assert len(quiet) == 1 and "VERIFY.md" in quiet[0][1]


def test_a_non_research_verify_failure_keeps_the_old_path_to_tier_1(tmp_path, monkeypatch):
    repo = research_repo(tmp_path, monkeypatch, verify_exit=1)
    calls: list = []
    monkeypatch.setattr(BD, "run_tier1", lambda repo, folder: calls.append(folder) or {"exit": 0, "payload": {}})
    monkeypatch.setattr(BD, "send_packet", lambda tick, folder, order: pytest.fail("no test sends to a live lane"))
    folder = BE.packet_dir(repo, "p-plain", "replied")
    research_reply(repo, "p-plain", research_run=None)

    BD.tick_once(repo, dict(BD.DEFAULTS))

    assert queued_orders(repo) == [] and len(calls) == 1 and not (folder / BD.REVISION_MARKER).exists()


def test_the_sec_inline_viewer_is_fetched_as_the_document_it_wraps():
    viewer = "https://www.sec.gov/ix?doc=/Archives/edgar/data/1045810/000104581025000023/nvda-20250126.htm"
    assert VR.canonical_url(viewer) == "https://www.sec.gov/Archives/edgar/data/1045810/000104581025000023/nvda-20250126.htm"
    assert VR.canonical_url("https://example.com/ix?doc=/x") == "https://example.com/ix?doc=/x"

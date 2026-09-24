"""THE RESEARCH CLAIMS GATE: every research reply's claims, verified on OUR side before it lands (2026-09-24).

The operator: "gemini hallucinates a lot, so we need some sort of force system in place to actually enforce its
checks/gates." R26-306 (`docs/research/markets/r26-306-nvda-share-railway-gdp-VERIFY-2026-09-24.md`) is the case this
answers: fabricated URLs that 404, DOIs unregistered or resolving to other books, a mis-typed filing figure, and rows
self-marked CONFIRMED with nothing on disk. The reply's own checks are never trusted; this script recomputes every one.

    python content/video_engine/scripts/verify_research_claims.py <run dir>              # online: URLs, DOIs, disk
    python content/video_engine/scripts/verify_research_claims.py <run dir> --offline    # the on-disk sources only (CI)
    python content/video_engine/scripts/verify_research_claims.py <run dir> --require-pass   # promotion check

The run dir holds `claims.jsonl` (the contract: `docs/runbooks/RESEARCH-REPLY-CONTRACT.md`) and `sources/`. Per claim:
URL fetched (generic User-Agent, retries; 4xx/5xx/DNS = FAIL, 401/402/403/429/451 or a timeout = UNVERIFIABLE); DOI
resolved at the handle API and Crossref (unregistered = FAIL, a registered title that does not match = FAIL
misattributed); the QUOTE found in the fetched page text; the VALUE found inside the quote; the SOURCE ON DISK present,
its sha256 equal, the quote in it too; a DERIVED value recomputed from its inputs. The TIER is computed, never read: a
self-declared tier above the earned one is an OVERCLAIM and fails the reply. A claim declared REJECTED is a disclosure:
its checks are reported and never fail the reply. Writes `VERIFY.json` + `VERIFY.md`; exit 0 only when nothing FAILs.

`--offline` never touches the network, so a claim earns CONFIRMED only from its saved source. `--require-pass` exits 0
only when `VERIFY.json` says PASS for the claims file as it is now (its sha256) - the check a promotion into
`docs/research/markets/` or an evidence object runs first. Standard library, plus pypdf (or pdftotext) for PDFs.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import difflib
import html.parser
import io
import json
import operator
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from audit_research_provenance import compute_sha256  # noqa: E402  (the one sha256 the research layer uses)

VERSION = "verify_research_claims.v1"
USER_AGENT = "MoneyPhysics-research-verifier (research@localhost)"   # generic by rule: never a personal address
DOI_API = "https://doi.org/api/handles/"
CROSSREF_API = "https://api.crossref.org/works/"
TIERS = ("REJECTED", "UNSOURCED", "PLAUSIBLE", "CONFIRMED")   # ascending
REQUIRED = ("id", "claim", "value", "unit", "period", "source_title", "quote", "tier_declared")
QUOTE_MAX = 300
MAX_BYTES = 30 * 1024 * 1024
MIN_PAGE_TEXT = 200            # fewer visible characters than this is a script shell or a block page, not a page
UNVERIFIABLE_HTTP = {401, 402, 403, 407, 429, 451}
PASS, FAIL, UNVERIFIABLE, SKIP = "PASS", "FAIL", "UNVERIFIABLE", "SKIP"
SCALES = {"thousand": 1e3, "k": 1e3, "million": 1e6, "mn": 1e6, "mm": 1e6, "m": 1e6,
          "billion": 1e9, "bn": 1e9, "b": 1e9, "trillion": 1e12, "tn": 1e12, "t": 1e12}
DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−﹘﹣－"), "-")
QUOTES = {**dict.fromkeys(map(ord, "‘’‚‛′"), "'"),
          **dict.fromkeys(map(ord, "“”„‟″«»"), '"')}
_NUMBER = re.compile(
    r"(?:(?<![\w.])(?P<neg>[-−]))?(?P<open>\()?\s*[$£€¥]?\s*"
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)\s*(?P<close>\))?\s*"
    r"(?P<scale>trillion|billion|million|thousand|tn|bn|mn|mm|m|b|k|t)?(?![a-z])", re.IGNORECASE)
_STOP = {"the", "and", "for", "from", "with", "into", "its", "their", "a", "an", "of", "in", "on", "to", "by"}


# --------------------------------------------------------------------------- text: normalise, extract, match


def normalise(text: str) -> str:
    """NFKC (so '…' is '...', a no-break space is a space), one dash, two quote marks, case-folded, spaces collapsed."""
    folded = unicodedata.normalize("NFKC", str(text or "")).translate(DASHES).translate(QUOTES)
    return re.sub(r"\s+", " ", folded).strip().casefold()


def quote_in(quote: str, page_norm: str) -> bool:
    """The quote's fragments (an ellipsis marks an elision) occur in order in the normalised page; a second pass ignores
    whitespace entirely, because a table's cells or a PDF's line breaks split what a reader copies as one line."""
    fragments = [f.strip(" ,;:") for f in normalise(quote).split("...") if f.strip(" ,;:")]
    if not fragments:
        return False
    for page, frags in ((page_norm, fragments), (re.sub(r"\s", "", page_norm), [re.sub(r"\s", "", f) for f in fragments])):
        pos, ok = 0, True
        for frag in frags:
            hit = page.find(frag, pos)
            if hit < 0:
                ok = False
                break
            pos = hit + len(frag)
        if ok:
            return True
    return False


class _Text(html.parser.HTMLParser):
    SKIP_TAGS = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skipping = 0

    def handle_starttag(self, tag, attrs):
        self.skipping += tag in self.SKIP_TAGS
        self.parts.append(" ")

    def handle_endtag(self, tag):
        self.skipping -= tag in self.SKIP_TAGS and self.skipping > 0
        self.parts.append(" ")

    def handle_data(self, data):
        if not self.skipping:
            self.parts.append(data)


def html_text(raw: str) -> str:
    parser = _Text()
    parser.feed(raw)
    parser.close()
    return "".join(parser.parts)


def pdf_text(data: bytes) -> str | None:
    """pypdf when installed, else poppler's pdftotext; None when neither can read it."""
    try:
        import pypdf  # noqa: PLC0415 - optional
        reader = pypdf.PdfReader(io.BytesIO(data))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    except ImportError:
        text = _pdftotext(data)
    except Exception:  # noqa: BLE001 - a PDF pypdf cannot parse may still be read by poppler
        text = _pdftotext(data)
    return None if text is None else re.sub(r"-\s*\n\s*", "", text)


def _pdftotext(data: bytes) -> str | None:
    exe = shutil.which("pdftotext")
    if not exe:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "in.pdf"
        src.write_bytes(data)
        proc = subprocess.run([exe, "-enc", "UTF-8", str(src), "-"], capture_output=True)
    return proc.stdout.decode("utf-8", "replace") if proc.returncode == 0 else None


def body_text(data: bytes, name: str = "", content_type: str = "") -> str | None:
    """The readable text of a page or a file: HTML stripped, a PDF extracted, anything else decoded."""
    if data[:5] == b"%PDF-" or "pdf" in content_type.lower() or name.lower().endswith(".pdf"):
        return pdf_text(data)
    raw = data.decode(_charset(content_type) or "utf-8", "replace")
    if "html" in content_type.lower() or name.lower().endswith((".htm", ".html", ".xhtml")) or "<html" in raw[:2000].lower():
        return html_text(raw)
    return raw


def _charset(content_type: str) -> str | None:
    m = re.search(r"charset=([\w-]+)", content_type or "", re.IGNORECASE)
    return m.group(1) if m else None


# --------------------------------------------------------------------------- numbers


def parse_number(text: Any) -> tuple[float, int, float | None] | None:
    """A printed value as (number, decimals printed, its own scale or None): '$1.2 billion' -> (1.2, 1, 1e9)."""
    s = unicodedata.normalize("NFKC", str(text)).translate(DASHES).strip().lstrip("~≈<>≤≥ ")
    m = re.fullmatch(r"(?P<neg>-)?\s*[$£€¥]?\s*(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)"
                     r"\s*(?P<scale>[a-zA-Z]+)?\s*%?", s)
    if not m:
        return None
    scale = m.group("scale")
    if scale and scale.lower() not in SCALES:
        return None
    num = m.group("num").replace(",", "")
    decimals = len(num.split(".", 1)[1]) if "." in num else 0
    value = -float(num) if m.group("neg") else float(num)
    return value, decimals, SCALES[scale.lower()] if scale else None


def unit_scale(unit: Any) -> float | None:
    """The scale a unit states: 'USD million' / '£M' / '$bn' -> 1e6 / 1e6 / 1e9; '%' or 'shares' -> None."""
    for word in re.findall(r"[a-zA-Z]+", str(unit or "")):
        if word.lower() in SCALES and (len(word) > 1 or word.isupper() or len(str(unit).strip(" $£€¥")) == 1):
            return SCALES[word.lower()]
    return None


def quote_numbers(quote: str) -> list[tuple[float, float | None]]:
    """Every number in the quote with its scale word; a parenthesised figure (an accounts outflow) counts either sign."""
    out: list[tuple[float, float | None]] = []
    for m in _NUMBER.finditer(unicodedata.normalize("NFKC", quote or "")):
        value = float(m.group("num").replace(",", ""))
        scale = SCALES[m.group("scale").lower()] if m.group("scale") else None
        if m.group("open") and m.group("close"):
            out += [(value, scale), (-value, scale)]
        else:
            out.append((-value if m.group("neg") else value, scale))
    return out


def value_in_quote(value: Any, unit: Any, quote: str) -> tuple[bool, str]:
    """The claim's value, as printed, is a number the quote prints - to the claim's own precision (a claim may round
    its source, never add a digit to it); a non-numeric value must occur in the quote as text."""
    parsed = parse_number(value)
    if parsed is None:
        ok = bool(str(value).strip()) and normalise(str(value)) in normalise(quote)
        return ok, "as text" if ok else f"{value!r} is not a number and not in the quote"
    number, decimals, own_scale = parsed
    scale = own_scale or unit_scale(unit)
    tol_raw = 0.5 * 10 ** -decimals + 1e-9
    for q, q_scale in quote_numbers(quote):
        if q_scale is None and abs(q - number) <= tol_raw:
            return True, f"{q:g} in the quote"
        if abs(q * (q_scale or 1) - number * (scale or 1)) <= tol_raw * (scale or 1):
            return True, f"{q:g}{'x%g' % q_scale if q_scale else ''} in the quote"
    return False, f"{value} ({unit or 'no unit'}) is not a number the quote prints"


_OPS: dict[type, Callable[..., float]] = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                                          ast.Div: operator.truediv, ast.USub: operator.neg, ast.UAdd: operator.pos}


def safe_eval(formula: str, values: dict[str, float]) -> float:
    """Arithmetic over `{claim id}` placeholders: numbers, + - * / and brackets. Nothing else parses."""
    names: dict[str, float] = {}

    def sub(m: re.Match) -> str:
        key = f"v{len(names)}"
        if m.group(1) not in values:
            raise ValueError(f"unknown input {m.group(1)!r}")
        names[key] = values[m.group(1)]
        return key

    tree = ast.parse(re.sub(r"\{([^{}]+)\}", sub, formula), mode="eval")

    def ev(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name) and node.id in names:
            return names[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        raise ValueError(f"not arithmetic: {ast.dump(node)[:60]}")

    return ev(tree)


# --------------------------------------------------------------------------- the network


class Web:
    """One fetch per URL per run (cached), a politeness delay, retries on 5xx and timeouts, a generic User-Agent."""

    def __init__(self, timeout: float = 20.0, retries: int = 2, delay: float = 0.5) -> None:
        self.timeout, self.retries, self.delay = timeout, retries, delay
        self.cache: dict[str, tuple[dict[str, Any], bytes]] = {}

    def get(self, url: str, accept: str = "*/*") -> tuple[dict[str, Any], bytes]:
        if url not in self.cache:
            self.cache[url] = self._get(url, accept)
        return self.cache[url]

    def _get(self, url: str, accept: str) -> tuple[dict[str, Any], bytes]:
        info: dict[str, Any] = {}
        for attempt in range(self.retries + 1):
            if self.delay:
                time.sleep(self.delay * (attempt + 1))
            info, body = self._once(url, accept)
            retry = info.get("http") in (500, 502, 503, 504) or info.get("error") == "timeout"
            if not retry:
                return info, body
        return info, b""

    def _once(self, url: str, accept: str) -> tuple[dict[str, Any], bytes]:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                body = res.read(MAX_BYTES)
                return {"status": PASS, "http": res.status, "final_url": res.geturl(),
                        "content_type": res.headers.get("Content-Type", ""), "bytes": len(body)}, body
        except urllib.error.HTTPError as exc:
            status = UNVERIFIABLE if exc.code in UNVERIFIABLE_HTTP else FAIL
            return {"status": status, "http": exc.code, "final_url": exc.geturl() or url,
                    "detail": f"HTTP {exc.code}"}, b""
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, socket.gaierror):
                return {"status": FAIL, "http": None, "final_url": url, "error": "dns",
                        "detail": f"DNS: {exc.reason}"}, b""
            if isinstance(exc.reason, (socket.timeout, TimeoutError)):
                return {"status": UNVERIFIABLE, "http": None, "final_url": url, "error": "timeout", "detail": "timeout"}, b""
            return {"status": UNVERIFIABLE, "http": None, "final_url": url, "detail": f"network: {exc.reason}"}, b""
        except (TimeoutError, socket.timeout):
            return {"status": UNVERIFIABLE, "http": None, "final_url": url, "error": "timeout", "detail": "timeout"}, b""


# --------------------------------------------------------------------------- the per-claim checks


def canonical_url(url: str) -> str:
    """A script viewer fetched as the document it wraps: SEC's inline-XBRL viewer (`/ix?doc=/Archives/...`) is a
    JavaScript shell whose HTML carries no filing text; the document at the `doc` path is the filing itself."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc.lower().endswith("sec.gov") and parts.path.rstrip("/") in ("/ix", "/cgi-bin/viewer"):
        doc = urllib.parse.parse_qs(parts.query).get("doc", [""])[0]
        if doc.startswith("/"):
            return f"{parts.scheme}://{parts.netloc}{doc}"
    return url


def check_url(c: dict[str, Any], web: Web) -> tuple[dict[str, Any], str | None]:
    """The fetch, and the page's text when it has any; a 200 with no readable text cannot carry a quote."""
    fetched = canonical_url(str(c["url"]))
    info, body = web.get(fetched)
    info = {k: v for k, v in info.items() if k != "error"} | ({"fetched_as": fetched} if fetched != c["url"] else {})
    if info["status"] != PASS:
        return info, None
    text = body_text(body, urllib.parse.urlparse(info["final_url"]).path, info.get("content_type", ""))
    info["detail"] = f"HTTP {info['http']}, {info.get('bytes')} bytes"
    return info, text


def check_quote_web(c: dict[str, Any], text: str | None) -> dict[str, Any]:
    if text is None:
        return {"status": UNVERIFIABLE, "detail": "the fetched page has no readable text (a PDF no tool could read?)"}
    page = normalise(text)
    if len(page) < MIN_PAGE_TEXT:
        return {"status": UNVERIFIABLE, "detail": f"the page carries {len(page)} characters of text (a script shell or a block page)"}
    ok = quote_in(c.get("quote") or "", page)
    return {"status": PASS if ok else FAIL, "detail": "quote found on the live page" if ok else "quote NOT on the live page"}


def check_disk(c: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    rel = str(c["sources_file"]).replace("\\", "/")
    path = (run_dir / rel).resolve()
    if run_dir.resolve() not in path.parents:
        return {"status": FAIL, "detail": f"{rel} is outside the run dir"}
    if not path.is_file():
        return {"status": FAIL, "detail": f"{rel} is not on disk"}
    digest = compute_sha256(path)
    if digest != str(c.get("sha256") or "").strip().lower():
        return {"status": FAIL, "detail": f"sha256 mismatch: file {digest[:12]}, claim {str(c.get('sha256'))[:12]}"}
    text = body_text(path.read_bytes(), path.name)
    if text is None:
        return {"status": UNVERIFIABLE, "detail": f"{rel}: no tool here reads it as text"}
    ok = quote_in(c.get("quote") or "", normalise(text))
    return {"status": PASS if ok else FAIL, "detail": f"{rel}: sha256 ok, quote {'found' if ok else 'NOT found'}"}


def check_doi(c: dict[str, Any], web: Web, doi_api: str, crossref_api: str) -> dict[str, Any]:
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", str(c["doi"]).strip(), flags=re.IGNORECASE)
    info, body = web.get(doi_api + urllib.parse.quote(doi, safe="/"), "application/json")
    handle = _json(body)
    if info.get("http") == 404 or (handle and handle.get("responseCode") != 1):
        return {"status": FAIL, "doi": doi, "detail": f"{doi}: not registered (handle API)"}
    if info["status"] != PASS:
        return {"status": UNVERIFIABLE, "doi": doi, "detail": f"{doi}: the handle API said {info.get('detail')}"}
    info, body = web.get(crossref_api + urllib.parse.quote(doi, safe="/"), "application/json")
    msg = (_json(body) or {}).get("message") or {}
    if info["status"] != PASS or not msg:
        return {"status": UNVERIFIABLE, "doi": doi, "detail": f"{doi}: registered, but Crossref has no record; title unchecked"}
    return _doi_match(c, doi, msg)


def _doi_match(c: dict[str, Any], doi: str, msg: dict[str, Any]) -> dict[str, Any]:
    titles = [t for key in ("title", "subtitle", "container-title") for t in (msg.get(key) or [])]
    families = [str(a.get("family") or a.get("name") or "") for a in (msg.get("author") or msg.get("editor") or [])]
    registered = "; ".join(titles[:2]) or "(no title)"
    if not _title_match(str(c.get("source_title") or ""), titles):
        return {"status": FAIL, "doi": doi, "registered_title": registered,
                "detail": f"{doi}: misattributed - registered to {registered!r}, cited as {c.get('source_title')!r}"}
    author = str(c.get("author") or "").casefold()
    if author and families and not any(f.casefold() in author for f in families if f):
        return {"status": FAIL, "doi": doi, "registered_title": registered,
                "detail": f"{doi}: misattributed - authors {families[:3]}, cited as {c.get('author')!r}"}
    return {"status": PASS, "doi": doi, "registered_title": registered, "detail": f"{doi}: registered to {registered!r}"}


def _title_match(cited: str, titles: list[str]) -> bool:
    words = [w for w in re.findall(r"[a-z0-9]+", normalise(cited)) if w not in _STOP and len(w) > 1]
    if not words or not titles:
        return False
    pool = set(re.findall(r"[a-z0-9]+", normalise(" ".join(titles))))
    if sum(w in pool for w in words) / len(words) >= 0.6:
        return True
    return any(difflib.SequenceMatcher(None, normalise(cited), normalise(t)).ratio() >= 0.75 for t in titles)


def _json(body: bytes) -> dict[str, Any] | None:
    try:
        payload = json.loads(body.decode("utf-8", "replace")) if body else None
    except ValueError:
        return None
    return payload if isinstance(payload, dict) else None


def check_value(c: dict[str, Any]) -> dict[str, Any]:
    if c.get("value") in (None, ""):
        return {"status": SKIP, "detail": "no value"}
    if not str(c.get("quote") or "").strip():
        return {"status": FAIL, "detail": "a value with no quote to carry it"}
    ok, why = value_in_quote(c["value"], c.get("unit"), c["quote"])
    return {"status": PASS if ok else FAIL, "detail": why}


def schema_errors(c: dict[str, Any]) -> list[str]:
    errs = [f"missing field {k!r}" for k in REQUIRED if k not in c]
    if str(c.get("tier_declared") or "").upper() not in TIERS:
        errs.append(f"tier_declared {c.get('tier_declared')!r} is not one of {'/'.join(TIERS)}")
    if len(str(c.get("quote") or "")) > QUOTE_MAX:
        errs.append(f"quote is {len(str(c.get('quote')))} chars (max {QUOTE_MAX})")
    if not c.get("derived_from") and "quote" in c and not str(c.get("quote") or "").strip() and not c.get("doi"):
        errs.append("no quote (every sourced claim quotes its source verbatim)")
    if c.get("sources_file") and not c.get("sha256"):
        errs.append("sources_file with no sha256")
    if c.get("derived_from") and not c.get("formula"):
        errs.append("derived_from with no formula")
    return errs


# --------------------------------------------------------------------------- the tier, earned


def earned_tier(c: dict[str, Any], checks: dict[str, dict[str, Any]]) -> str:
    """REJECTED on any FAIL; CONFIRMED when a live page or the saved source carries the quote and the value (a secondary
    source caps at PLAUSIBLE); PLAUSIBLE on a DOI that resolves to the cited work; otherwise UNSOURCED."""
    if any(v["status"] == FAIL for v in checks.values()):
        return "REJECTED"
    page = (checks.get("url", {}).get("status") == PASS and checks.get("quote_web", {}).get("status") == PASS) \
        or checks.get("disk", {}).get("status") == PASS
    if page and checks["value"]["status"] in (PASS, SKIP):
        return "PLAUSIBLE" if str(c.get("source_kind") or "primary").lower() == "secondary" else "CONFIRMED"
    if checks.get("doi", {}).get("status") == PASS and checks["value"]["status"] in (PASS, SKIP):
        return "PLAUSIBLE"
    return "UNSOURCED"


def verify_claim(c: dict[str, Any], run_dir: Path, web: Web | None, apis: tuple[str, str]) -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}
    if c.get("url") and web is not None:
        checks["url"], text = check_url(c, web)
        if checks["url"]["status"] == PASS and str(c.get("quote") or "").strip():
            checks["quote_web"] = check_quote_web(c, text)
    if c.get("doi") and web is not None:
        checks["doi"] = check_doi(c, web, *apis)
    if c.get("sources_file"):
        checks["disk"] = check_disk(c, run_dir)
    checks["value"] = check_value(c) if not c.get("derived_from") else {"status": SKIP, "detail": "derived"}
    return {"id": c.get("id"), "checks": checks, "schema": schema_errors(c)}


def resolve_derived(rows: dict[str, dict[str, Any]], claims: dict[str, dict[str, Any]], cid: str, seen: tuple = ()) -> str:
    """The derived claim's value recomputed from its inputs; its tier is the weakest input's, or REJECTED."""
    row, c = rows[cid], claims[cid]
    if row.get("tier_earned"):
        return row["tier_earned"]
    if not c.get("derived_from"):
        row["tier_earned"] = earned_tier(c, row["checks"])
        return row["tier_earned"]
    inputs = [str(i) for i in c.get("derived_from") or []]
    bad = [i for i in inputs if i not in claims or i in seen or i == cid]
    if bad:
        row["checks"]["derived"] = {"status": FAIL, "detail": f"inputs missing or circular: {bad}"}
    else:
        tiers = [resolve_derived(rows, claims, i, (*seen, cid)) for i in inputs]
        row["checks"]["derived"] = _recompute(c, {i: claims[i] for i in inputs})
        row["inputs_tier"] = min(tiers, key=TIERS.index)
    failed = any(v["status"] == FAIL for v in row["checks"].values())
    row["tier_earned"] = "REJECTED" if failed else row["inputs_tier"]
    return row["tier_earned"]


def _recompute(c: dict[str, Any], inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    target = parse_number(c.get("value"))
    values = {}
    for i, ic in inputs.items():
        p = parse_number(ic.get("value"))
        if p is None:
            return {"status": FAIL, "detail": f"input {i} has no numeric value"}
        values[i] = p[0]
    if target is None:
        return {"status": FAIL, "detail": "the derived value is not a number"}
    try:
        got = safe_eval(str(c.get("formula") or ""), values)
    except (ValueError, SyntaxError, ZeroDivisionError) as exc:
        return {"status": FAIL, "detail": f"formula refused: {exc}"}
    tol = 0.5 * 10 ** -target[1] + 1e-9
    ok = abs(got - target[0]) <= tol
    return {"status": PASS if ok else FAIL, "detail": f"{c.get('formula')} = {got:.6g}; claimed {c.get('value')}"}


# --------------------------------------------------------------------------- the run


def load_claims(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    claims, errs = [], []
    if not path.is_file():
        return [], [f"{path.name} not found in the run dir - a research reply with no claims file cannot pass"]
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            errs.append(f"line {n}: not JSON ({exc})")
            continue
        (claims.append(row) if isinstance(row, dict) else errs.append(f"line {n}: not an object"))
    if not claims and not errs:
        errs.append("claims.jsonl carries no claims")
    ids = [str(c.get("id")) for c in claims]
    errs += [f"duplicate claim id {i!r}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    return claims, errs


def verify_run(run_dir: Path, claims_path: Path, *, offline: bool, web: Web, apis: tuple[str, str]) -> dict[str, Any]:
    claims, fails = load_claims(claims_path)
    by_id = {str(c.get("id")): c for c in claims}
    rows = {cid: verify_claim(c, run_dir, None if offline else web, apis) for cid, c in by_id.items()}
    out = []
    for cid, c in by_id.items():
        resolve_derived(rows, by_id, cid)
        out.append(_finish(rows[cid], c, fails))
    counts = {t: sum(1 for r in out if r["tier_earned"] == t) for t in TIERS}
    return {"verifier": VERSION, "run_dir": str(run_dir), "claims_file": str(claims_path),
            "claims_sha256": compute_sha256(claims_path) if claims_path.is_file() else None,
            "checked_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "offline": offline,
            "verdict": FAIL if fails else PASS, "counts": counts, "fails": fails, "claims": out}


def _finish(row: dict[str, Any], c: dict[str, Any], fails: list[str]) -> dict[str, Any]:
    declared = str(c.get("tier_declared") or "").upper()
    earned = row["tier_earned"]
    over = declared in TIERS and TIERS.index(declared) > TIERS.index(earned)
    reasons = [f"{k}: {v['detail']}" for k, v in row["checks"].items() if v["status"] == FAIL] + row["schema"]
    if over:
        reasons.append(f"overclaim: declared {declared}, earned {earned}")
    disclosed = declared == "REJECTED" and not row["schema"]
    verdict = "DISCLOSED" if disclosed else (FAIL if reasons else PASS)
    if verdict == FAIL:
        fails.extend(f"{row['id']}: {r}" for r in reasons)
    return {"id": row["id"], "claim": c.get("claim"), "value": c.get("value"), "unit": c.get("unit"),
            "tier_declared": declared, "tier_earned": earned, "overclaim": over, "verdict": verdict,
            "reasons": reasons, "checks": row["checks"]}


# --------------------------------------------------------------------------- the report


def _cell(check: dict[str, Any] | None) -> str:
    if not check:
        return "-"
    http = f" {check['http']}" if check.get("http") else ""
    return f"{check['status']}{http}"


def _esc(text: Any) -> str:
    return str(text if text is not None else "").replace("|", r"\|").replace("\n", " ")[:220]


def render_md(report: dict[str, Any]) -> str:
    claims = report["claims"]
    failed = [c for c in claims if c["verdict"] == FAIL]
    lines = [
        "# VERIFY - the research claims gate (`verify_research_claims.py`)",
        "",
        f"**Verdict: {report['verdict']}** - {len(claims)} claim(s), {len(failed)} failing; "
        f"mode {'offline (disk only)' if report['offline'] else 'online'}; checked {report['checked_at']}.",
        f"Claims file sha256 `{report['claims_sha256']}` - a promotion runs `--require-pass` against it.",
        "Earned tiers: " + ", ".join(f"{t} {n}" for t, n in report["counts"].items()) + ".",
        "",
        "## Failures (the revision table)",
        "",
    ]
    if report["fails"]:
        lines += ["| id | declared | earned | why |", "|---|---|---|---|"]
        known = {c["id"] for c in failed}
        lines += [f"| {_esc(c['id'])} | {c['tier_declared']} | {c['tier_earned']} | {_esc('; '.join(c['reasons']))} |"
                  for c in failed]
        lines += [f"| - | - | - | {_esc(f)} |" for f in report["fails"] if f.split(":", 1)[0] not in known]
    else:
        lines.append("- none")
    lines += ["", "## Every claim", "",
              "| id | value | declared | earned | verdict | url | doi | quote on page | value in quote | disk | derived |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in claims:
        ch = c["checks"]
        lines.append(f"| {_esc(c['id'])} | {_esc(c['value'])} {_esc(c['unit'] or '')} | {c['tier_declared']} | "
                     f"{c['tier_earned']} | {c['verdict']} | {_cell(ch.get('url'))} | {_cell(ch.get('doi'))} | "
                     f"{_cell(ch.get('quote_web'))} | {_cell(ch.get('value'))} | {_cell(ch.get('disk'))} | "
                     f"{_cell(ch.get('derived'))} |")
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "VERIFY.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "VERIFY.md").write_text(render_md(report), encoding="utf-8")


def require_pass(claims_path: Path, out_dir: Path) -> tuple[bool, str]:
    """The promotion check: VERIFY.json says PASS, for the claims file exactly as it is now."""
    try:
        report = json.loads((out_dir / "VERIFY.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False, f"no readable VERIFY.json in {out_dir}"
    if report.get("verdict") != PASS:
        return False, f"VERIFY.json verdict is {report.get('verdict')}"
    current = compute_sha256(claims_path) if claims_path.is_file() else None
    if current != report.get("claims_sha256"):
        return False, "claims.jsonl changed since the gate ran - run the verifier again"
    return True, f"PASS on {report.get('checked_at')} ({'offline' if report.get('offline') else 'online'})"


# --------------------------------------------------------------------------- the CLI


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run_dir", type=Path, help="the research run folder (claims.jsonl + sources/)")
    ap.add_argument("--claims", type=Path, default=None, help="the claims file (default <run dir>/claims.jsonl)")
    ap.add_argument("--out-dir", type=Path, default=None, help="where VERIFY.json/.md land (default the run dir)")
    ap.add_argument("--offline", action="store_true", help="no network: the on-disk sources only")
    ap.add_argument("--require-pass", action="store_true", help="exit 0 only if VERIFY.json passed this claims file")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--delay", type=float, default=0.5, help="seconds before each request (politeness)")
    ap.add_argument("--doi-api", default=DOI_API)
    ap.add_argument("--crossref-api", default=CROSSREF_API)
    return ap


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    a = build_parser().parse_args(argv)
    run_dir = a.run_dir.resolve()
    claims_path = (a.claims or run_dir / "claims.jsonl").resolve()
    out_dir = (a.out_dir or run_dir).resolve()
    if a.require_pass:
        ok, why = require_pass(claims_path, out_dir)
        print(f"verify_research_claims --require-pass: {'PASS' if ok else 'FAIL'} - {why}")
        return 0 if ok else 1
    if not run_dir.is_dir():
        print(f"verify_research_claims: FAIL - run dir not found: {run_dir}")
        return 1
    web = Web(timeout=a.timeout, retries=a.retries, delay=a.delay)
    report = verify_run(run_dir, claims_path, offline=a.offline, web=web, apis=(a.doi_api, a.crossref_api))
    write_report(report, out_dir)
    for line in report["fails"][:40]:
        print("FAIL", line)
    tiers = ", ".join(f"{t} {n}" for t, n in report["counts"].items())
    print(f"verify_research_claims: {report['verdict']} - {len(report['claims'])} claim(s); earned {tiers}; "
          f"{len(report['fails'])} failure(s); {out_dir / 'VERIFY.md'}")
    return 0 if report["verdict"] == PASS else 1


if __name__ == "__main__":
    sys.exit(main())

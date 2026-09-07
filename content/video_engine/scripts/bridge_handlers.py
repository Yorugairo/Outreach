"""Tier 0: close a landed bridge reply with Python, or say precisely why a model has to look (P46 T6).

    python content/video_engine/scripts/bridge_handlers.py --packet <packetId>
    python content/video_engine/scripts/bridge_handlers.py --replay 7aaa9146-88f1-4f03-b004-d5bdf18a5492

`bridge_daemon.py` calls `classify()`; this CLI is the same check by hand, printing the result as JSON and
moving nothing, ledgering nothing. Exit 0 when tier 0 closes the reply, 2 when it cannot, 1 on a refusal.

A handler is chosen by the order's `replyShape` and answers one question - *does the disk agree with the
reply* - with zero tokens:

  * `paths-written`  every path the reply names exists (and carries the order's `marker` when it named one)
  * `contract-block` the order's `block` is present at the source and at every copy the order named
  * `report-landed`  the report is under `docs/research/<area>/`, carries a proof line and the NOT FOUND
                     block, and `build_docs_layers.py --write` then `--check` exit 0
  * `review`         the reply parses with a POSITION line and is `done` with no disagreements, no prerequisites
  * `test-run`       the order's `command` exits 0 from the repo root
  * `free`           never closes here; a shapeless reply is judgment by definition

The reply grammar (BRIDGE-PACKET.md §2) is parsed where it is there and is NOT required: Gemini's completion
report of 2026-09-06 (`7aaa9146`) used bold headings and backticked paths, so backticked absolute paths and
`.md` names are a fallback path source, and a bare name is resolved against the repo root and against any
directory the same reply named. Standard library only; no model call is made by this module.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import bridge_env as env_mod  # noqa: E402

REPO = env_mod.REPO
LAYERS_SCRIPT = "content/video_engine/scripts/build_docs_layers.py"
RESEARCH_ROOT = "docs/research/"
NOT_FOUND_BLOCK = "## NOT FOUND WHERE I LOOKED"
PROOF_LINE = re.compile(r"\[[^\]\n]*\|\s*URL:\s*https://[^|\]\n]+\|\s*Verified\s+20\d\d")
REPLAY_DIR = "replay"
# P46 T7: a tier-0 failure is one of two CLASSES. FORM - the reply's shape (no grammar, a mangled or missing path list, no
# NOT FOUND block, stale docs layers, a truncated reply): the addressee can restate what it did in one follow-up at zero Claude
# tokens - the REPAIR ROUND. SUBSTANCE - the work itself (a marker absent from a file, no proof line, an [UNVERIFIED] verdict, a
# failed command, a failed verify): a follow-up would only invite invention (the operator, 2026-09-07: an evidence quota "gets
# Gemini to write us bad numbers"), so it goes to tier 1. A repair is asked for FORM only, never for evidence.
FORM_CHECKS = ("paths-named", "reply-whole", "report-named", "not-found-block", "docs-layers", "command-named", "shape", "exists",
               "fetch-dir-named", "manifest", "manifest-parses", "entries", "entry", "outputs-named", "verify-named", "csv-named",
               "intake-named", "section")   # P46 T8: the file shapes' FORM checks; sha256 / schema / rows / required-cells / claims-* / dedupe-* are substance
CLASS_FORM, CLASS_SUBSTANCE = "form", "substance"
DETAIL_CHARS = 400

_HEADER_COMMENT = re.compile(r"^<!--.*?-->", re.DOTALL)
_BACKTICKED = re.compile(r"`([^`\n]+)`")
_ABSOLUTE = re.compile(r"^([a-zA-Z]:[\\/]|[\\/]|~[\\/])")
_BULLET = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
_TRUNCATED = re.compile(r"<truncated (\d+) bytes>")   # Antigravity's transcript writer cuts long fields in place
_GRAMMAR_HEADER = re.compile(
    r"^\s*(?:[-*]\s*)?\*{0,2}(POSITION|PATHS WRITTEN|DISAGREEMENTS|PREREQUISITES|NOT FOUND WHERE I LOOKED)"
    r"\*{0,2}\s*:\s*(.*)$",
    re.IGNORECASE,
)
# the same header as a markdown heading (`### POSITION`, Gemini 2026-09-06): the colon is optional ONLY in this form,
# so a bold prose label like `**Synced:**` never becomes a section
_GRAMMAR_HEADING = re.compile(
    r"^\s*#{1,6}\s*\*{0,2}(POSITION|PATHS WRITTEN|DISAGREEMENTS|PREREQUISITES|NOT FOUND WHERE I LOOKED)\*{0,2}\s*:?\s*(.*)$",
    re.IGNORECASE,
)
NONE_WORDS = {"none", "(none)", "none.", "n/a", "-", "nothing"}
PATH_SUFFIXES = {
    ".md", ".py", ".json", ".jsonl", ".yaml", ".yml", ".txt", ".ts", ".tsx", ".js", ".html", ".css",
    ".toml", ".ini", ".csv", ".sh", ".ps1", ".sql", ".png", ".svg",
}

Tier0Result = dict[str, Any]


# --------------------------------------------------------------------------- the reply grammar


@dataclass
class Grammar:
    """BRIDGE-PACKET.md §2. ``None`` means the header was absent; ``[]`` means it said `none`."""

    position: str | None = None
    paths_written: list[str] | None = None
    disagreements: list[str] | None = None
    prerequisites: list[str] | None = None
    not_found: str | None = None


def _clean(text: str) -> str:
    """One named path, stripped of the bullet, the quotes, the backticks and a trailing separator."""

    stripped = _BULLET.sub("", (text or "").strip()).strip()
    stripped = stripped.strip("`").strip().strip('"').strip("'")
    return stripped.rstrip("\\/") if len(stripped) > 3 else stripped


def _is_none_word(text: str) -> bool:
    return _clean(text).lower() in NONE_WORDS


def _collect(body: str) -> dict[str, list[str]]:
    """Every grammar section's raw lines. A blank line continues a section; free prose closes it."""

    buckets: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        match = _GRAMMAR_HEADER.match(line) or _GRAMMAR_HEADING.match(line)
        if match:
            current = match.group(1).upper()
            buckets.setdefault(current, [])
            if match.group(2).strip():
                buckets[current].append(match.group(2).strip())
            continue
        if current is None or not line.strip():
            continue
        if current == "POSITION" and not buckets[current]:
            # a heading-form POSITION carries its value on the next line (`### POSITION` / `done ...`)
            buckets[current].append(line.strip())
            continue
        bare_path = current == "PATHS WRITTEN" and (_ABSOLUTE.match(line.strip()) is not None or _looks_like_path(line.strip()))
        # P46 T7: a RELATIVE path is a list item too - it resolves under the order's `roots` (a file in another repo the order named)
        if _BULLET.match(line) or bare_path or current == "NOT FOUND WHERE I LOOKED":
            # a PATHS WRITTEN list may be bare absolute paths, one per line, no bullet (Gemini, 2026-09-06 18:26):
            # that is a list, not prose, and must not close the section
            buckets[current].append(line.strip())
        else:
            current = None
    return buckets


def _list_section(lines: list[str] | None, *, split_commas: bool = False) -> list[str] | None:
    if lines is None:
        return None
    items: list[str] = []
    for line in lines:
        if _is_none_word(line):
            continue
        chunks = [c for c in line.split(",")] if split_commas else [line]
        items.extend(_clean(chunk) for chunk in chunks if _clean(chunk))
    return items


def parse_reply(text: str) -> Grammar:
    """The grammar as far as the reply carries it. An absent header is ``None``, never an error."""

    buckets = _collect(_HEADER_COMMENT.sub("", text or "", count=1))
    position = buckets.get("POSITION")
    not_found = " ".join(buckets.get("NOT FOUND WHERE I LOOKED") or []).strip()
    return Grammar(
        position=_clean(position[0]).lower() if position else None,
        paths_written=_list_section(buckets.get("PATHS WRITTEN"), split_commas=True),
        disagreements=_list_section(buckets.get("DISAGREEMENTS")),
        prerequisites=_list_section(buckets.get("PREREQUISITES")),
        not_found=not_found or None,
    )


# --------------------------------------------------------------------------- paths named in free text


def _looks_like_path(text: str) -> bool:
    """A backticked token that is a path, not a command: absolute, or a relative name with an extension."""

    if not text or text.startswith("-"):
        return False
    if _ABSOLUTE.match(text):
        return True
    if any(ws in text for ws in (" ", "\t")):
        return False
    return "/" in text or "\\" in text or Path(text).suffix.lower() in PATH_SUFFIXES


def extract_paths(text: str) -> list[str]:
    """Backticked paths in a reply that ignored the grammar - the 7aaa9146 completion report's shape."""

    seen: list[str] = []
    for raw in _BACKTICKED.findall(text or ""):
        candidate = _clean(raw)
        if _looks_like_path(candidate) and candidate not in seen:
            seen.append(candidate)
    return seen


def locate(raw: str, repo: Path, extra_dirs: Sequence[Path] = ()) -> tuple[Path, bool]:
    """Where a named path actually is: absolute as given, else under the repo root, else under a named dir."""

    text = _clean(raw)
    if not text:
        return Path(repo), False
    direct = Path(text).expanduser()
    if _ABSOLUTE.match(text) or direct.is_absolute():
        return direct, direct.exists()
    for base in (Path(repo), *extra_dirs):
        candidate = base / text
        if candidate.exists():
            return candidate, True
    return Path(repo) / text, False


def named_paths(order: dict[str, Any], text: str) -> list[str]:
    """The reply's PATHS WRITTEN when it used the grammar, the backticked paths when it did not."""

    grammar = parse_reply(text)
    if grammar.paths_written:
        return [_path_from_item(item) for item in grammar.paths_written]
    return extract_paths(text)


def _path_from_item(item: str) -> str:
    """A PATHS WRITTEN item may be a bare path, a backticked path, a markdown link `[`path`](file:///...)`, or a
    path followed by a note in parentheses. Return the path alone."""
    from urllib.parse import unquote, urlparse
    m = _BACKTICKED.search(item)
    if m:
        return m.group(1).strip()
    m = re.search(r"\]\((file:///[^)]+)\)", item)
    if m:
        return unquote(urlparse(m.group(1)).path).lstrip("/")
    return re.sub(r"\s+\([^)]*\)\s*$", "", item).strip()


def _looks_whole(path: str) -> bool:
    """A path item that ends in a file suffix or a directory separator; a half-path cut mid-name does not."""
    tail = path.rstrip(")").rstrip()
    return bool(re.search(r"\.[A-Za-z0-9]{1,6}$", tail)) or tail.endswith(("/", "\\"))


def _named_dirs(paths: Sequence[str], repo: Path) -> list[Path]:
    """Every directory the reply itself named - a bare filename is resolved against these too."""

    dirs = []
    for raw in paths:
        found, ok = locate(raw, repo)
        if ok and found.is_dir():
            dirs.append(found)
    return dirs


# --------------------------------------------------------------------------- results


def check(name: str, ok: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "detail": detail[:DETAIL_CHARS]}


def result(passed: bool, reason: str, checks: list[dict[str, Any]]) -> Tier0Result:
    return {"pass": bool(passed), "reason": reason, "checks": checks}


def failure_class(checks: list[dict[str, Any]]) -> str | None:
    """`form` when the FIRST failing check is about the reply's shape, `substance` when it is about the work, None on a pass."""
    for entry in checks:
        if not entry["ok"]:
            head = str(entry["name"]).split(":", 1)[0]
            return CLASS_FORM if head in FORM_CHECKS else CLASS_SUBSTANCE
    return None


def order_roots(order: dict[str, Any], repo: Path | str) -> list[Path]:
    """The roots the ORDER named (`roots`: absolute paths) - a relative path in the reply resolves under each; a path in another
    repo the order sent the addressee to is never 'not found' for living outside ours (P46 T7, the second tier-1 run of 2026-09-06)."""
    out: list[Path] = []
    for raw in order.get("roots") or []:
        p = Path(str(raw)).expanduser()
        if p.exists():
            out.append(p)
    return out


TEMPLATES: dict[str, str] = {
    "paths-written": (
        "POSITION: done | conditional | blocked\n"
        "PATHS WRITTEN:\n"
        "<one bare absolute path per line - no links, no backticks, no bullets, no prose>\n"
        "DISAGREEMENTS:\n- none\n"
        "PREREQUISITES:\n- none\n"
        "NOT FOUND WHERE I LOOKED:\n- <the roots you searched, or none>\n"),
    "report-landed": (
        "POSITION: done | conditional | blocked\n"
        "PATHS WRITTEN:\n"
        "<the report's absolute path under docs/research/<area>/ first, then any other, one bare path per line>\n"
        "DISAGREEMENTS:\n- none\n"
        "PREREQUISITES:\n- none\n"
        "NOT FOUND WHERE I LOOKED:\n- <the roots you searched>\n"
        "(the report itself must carry `## Verdict up front`, proof lines of the form "
        "`[Metric | value | authority | URL: https://... | Verified 2026-..]`, and a `## NOT FOUND WHERE I LOOKED` block)\n"),
    "contract-block": (
        "POSITION: done | conditional | blocked\n"
        "PATHS WRITTEN:\n<one bare absolute path per line - every file that carries the block>\n"
        "DISAGREEMENTS:\n- none\n"
        "PREREQUISITES:\n- none\n"
        "NOT FOUND WHERE I LOOKED:\n- none\n"),
    "review": (
        "POSITION: done | conditional | blocked\n"
        "PATHS WRITTEN:\n- none\n"
        "DISAGREEMENTS:\n- <each disagreement on its own line, or none>\n"
        "PREREQUISITES:\n- <each, or none>\n"
        "NOT FOUND WHERE I LOOKED:\n- <the files you could not open, or none>\n"),
    "test-run": (
        "POSITION: done | conditional | blocked\n"
        "PATHS WRITTEN:\n<one bare absolute path per line, or none>\n"
        "DISAGREEMENTS:\n- none\n"
        "PREREQUISITES:\n- none\n"
        "NOT FOUND WHERE I LOOKED:\n- none\n"),
}


def template(shape: str) -> str:
    """The fill-in grammar block for a reply shape - what an order appends and what a repair asks for."""
    return TEMPLATES.get(shape, TEMPLATES["paths-written"]).replace("\\n", "\n")


def _first_failure(checks: list[dict[str, Any]]) -> str | None:
    for entry in checks:
        if not entry["ok"]:
            return entry["detail"]
    return None


# --------------------------------------------------------------------------- the handlers


def check_paths_written(order: dict[str, Any], text: str, repo: Path) -> Tier0Result:
    """Every path the reply names exists; when the order named a `marker`, every file carries it."""

    paths = named_paths(order, text)
    if not paths:
        return result(False, "no paths named", [check("paths-named", False, "the reply names no path")])
    cut = _TRUNCATED.search(text or "")
    if cut:
        # the list is partial and one item is a half-path: verify what survived, then fail on the truncation itself
        paths = [p for p in paths if "<truncated" not in p and not text.count(p) == 0]
        paths = [p for p in paths if _looks_whole(p)]
    dirs = [*_named_dirs(paths, repo), *order_roots(order, repo)]   # P46 T7: the order's roots resolve a relative path too
    marker = order.get("marker")
    checks: list[dict[str, Any]] = []
    if cut:
        checks.append(check("reply-whole", False,
                            f"reply truncated by the transcript ({cut.group(1)} bytes cut): {len(paths)} listed path(s) verified below, the rest unseen - tier 1 or the full reply"))
    for raw in paths:
        found, ok = locate(raw, repo, dirs)
        checks.append(check(f"exists:{raw}", ok, f"{found}" if ok else f"not found where I looked: {found}"))
        if ok and marker and found.is_file():
            body = found.read_text(encoding="utf-8", errors="replace")
            checks.append(check(f"marker:{raw}", marker in body, f"{marker!r} {'in' if marker in body else 'absent from'} {found}"))
    failure = _first_failure(checks)
    return result(failure is None, "" if failure is None else failure, checks)


def check_contract_block(order: dict[str, Any], text: str, repo: Path) -> Tier0Result:
    """The order's `block` is present at the source and at every copy the order named."""

    block = (order.get("block") or "").strip()
    if not block:
        return result(False, "order names no block", [check("block-named", False, "order.json has no `block`")])
    source = order.get("source")
    copies = [c for c in (order.get("copies") or []) if c]
    if not copies and not source:
        return result(False, "order names no copies", [check("copies-named", False, "order.json has no `copies`")])

    targets = ([("source", source)] if source else []) + [("copy", raw) for raw in copies]
    checks = [_block_check(label, raw, block, repo) for label, raw in targets]
    failure = _first_failure(checks)
    reason = "" if failure is None else ("block missing at source" if failure.startswith("source") else failure)
    return result(failure is None, reason, checks)


def _block_check(label: str, raw: str, block: str, repo: Path) -> dict[str, Any]:
    found, ok = locate(raw, repo)
    if not ok or not found.is_file():
        return check(f"{label}:{raw}", False, f"{label} not found where I looked: {found}")
    body = found.read_text(encoding="utf-8", errors="replace")
    present = block in body
    return check(f"{label}:{raw}", present, f"{label} {'carries' if present else 'lacks'} the block: {found}")


def run_layers(repo: Path) -> tuple[bool, str]:
    """`build_docs_layers.py --write` then `--check`; both must exit 0. Monkeypatched in tests."""

    for flag in ("--write", "--check"):
        proc = subprocess.run(
            [sys.executable, LAYERS_SCRIPT, flag], cwd=str(repo), capture_output=True, text=True
        )
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "").strip()[-200:]
            return False, f"build_docs_layers.py {flag} exit {proc.returncode}: {tail}"
    return True, "build_docs_layers.py --write then --check exit 0"


def check_report_landed(order: dict[str, Any], text: str, repo: Path) -> Tier0Result:
    """The report is under `docs/research/<area>/`, proves its figures, says where it did not look."""

    reports = [p for p in named_paths(order, text) if _is_report(p)]
    if not reports:
        return result(False, "no report named", [check("report-named", False, f"no `{RESEARCH_ROOT}<area>/*.md` in the reply")])
    raw = reports[0]
    found, ok = locate(raw, repo, order_roots(order, repo))
    checks = [check(f"exists:{raw}", ok, f"{found}" if ok else f"not found where I looked: {found}")]
    if not ok:
        return result(False, checks[0]["detail"], checks)

    body = found.read_text(encoding="utf-8", errors="replace")
    proofs = len(PROOF_LINE.findall(body))
    checks.append(check("proof-line", proofs > 0, f"{proofs} proof line(s) `[... | URL: https://... | Verified 20..]`"))
    checks.append(check("not-found-block", NOT_FOUND_BLOCK in body, f"`{NOT_FOUND_BLOCK}` {'present' if NOT_FOUND_BLOCK in body else 'absent'}"))
    verdict = _verdict_line(body)
    abstained = verdict is not None and "[UNVERIFIED]" in verdict
    checks.append(check("verdict-verified", not abstained,
                        "the verdict is an abstention - `[UNVERIFIED]` under `## Verdict up front`; a follow-up, not a pass"
                        if abstained else (f"verdict: {verdict[:80]}" if verdict else "no `## Verdict up front` section (not required)")))
    if _first_failure(checks) is None:
        layers_ok, detail = run_layers(Path(repo))
        checks.append(check("docs-layers", layers_ok, detail))
    failure = _first_failure(checks)
    return result(failure is None, "" if failure is None else failure, checks)


def _verdict_line(body: str) -> str | None:
    """The first non-empty line under `## Verdict up front`, or None when the report has no such section."""
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("## verdict up front"):
            for nxt in lines[i + 1:]:
                if nxt.strip():
                    return nxt.strip()
            return ""
    return None


def _is_report(path: str) -> bool:
    posix = path.replace("\\", "/")
    return RESEARCH_ROOT in posix and posix.lower().endswith(".md")


def check_review(order: dict[str, Any], text: str, repo: Path) -> Tier0Result:
    """`done` with nothing outstanding closes; anything else is judgment and names itself as such."""

    grammar = parse_reply(text)
    if not grammar.position:
        return result(False, "no POSITION line", [check("grammar", False, "the reply carries no POSITION line")])
    checks = [
        check("position", grammar.position == "done", f"POSITION: {grammar.position}"),
        check("disagreements", not grammar.disagreements, f"{len(grammar.disagreements or [])} disagreement(s)"),
        check("prerequisites", not grammar.prerequisites, f"{len(grammar.prerequisites or [])} prerequisite(s)"),
    ]
    if grammar.disagreements:
        return result(False, "disagreements", checks)
    if grammar.prerequisites:
        return result(False, "prerequisites", checks)
    if grammar.position != "done":
        return result(False, grammar.position if grammar.position in ("conditional", "blocked") else "conditional", checks)
    return result(True, "", checks)


def run_command(command: Sequence[str], repo: Path) -> tuple[int, str]:
    """The order's own validation command, from the repo root. Monkeypatched in tests that need it."""

    proc = subprocess.run(list(command), cwd=str(repo), capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "")[-200:] + (proc.stderr or "")[-200:]


def check_test_run(order: dict[str, Any], text: str, repo: Path) -> Tier0Result:
    """The order named a command; it exits 0 or the reply is not closed."""

    command = order.get("command")
    if not isinstance(command, list) or not command:
        return result(False, "order names no command", [check("command-named", False, "order.json has no `command` list")])
    code, tail = run_command(command, Path(repo))
    entry = check("exit-0", code == 0, f"exit {code}: {tail.strip()[:200]}")
    return result(code == 0, "" if code == 0 else f"command exit {code}", [entry])


def check_free(order: dict[str, Any], text: str, repo: Path) -> Tier0Result:
    """A shapeless reply has nothing to verify against; give the order a shape or pay for judgment."""

    return result(False, "free shape: every reply reaches tier 1", [check("shape", False, "replyShape is `free`")])


HANDLERS: dict[str, Callable[[dict[str, Any], str, Path], Tier0Result]] = {
    "paths-written": check_paths_written,
    "contract-block": check_contract_block,
    "report-landed": check_report_landed,
    "review": check_review,
    "test-run": check_test_run,
    "free": check_free,
}


# --------------------------------------------------------------------------- P46 T8: the file shapes (docs/runbooks/BRIDGE-SHAPES.md)

INTAKE_SECTIONS = ("## Claims", "## Dedupe", "## Figures", NOT_FOUND_BLOCK)
INTAKE_STATUS = ("held", "new", "contradicts", "unsourced")


def _sha256(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_fetch(order: dict[str, Any], text: str, repo: Path) -> Tier0Result:
    """A fetch order's deliverable is files and a manifest, never a summary: the manifest parses, every entry has url / path /
    sha256 / fetched_at, every path exists and hashes to its sha256; a `not-fetched` entry counts toward NOT FOUND, not here."""
    fetch_dir = order.get("fetch_dir")
    if not fetch_dir:
        return result(False, "order names no fetch_dir", [check("fetch-dir-named", False, "order.json has no `fetch_dir`")])
    manifest, ok = locate(str(Path(str(fetch_dir)) / "MANIFEST.json"), repo, order_roots(order, repo))
    checks = [check("manifest", ok, f"{manifest}" if ok else f"not found where I looked: {manifest}")]
    if not ok:
        return result(False, checks[0]["detail"], checks)
    try:
        doc = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        checks.append(check("manifest-parses", False, f"{manifest}: {exc}"))
        return result(False, checks[-1]["detail"], checks)
    entries = [e for e in (doc.get("entries") if isinstance(doc, dict) else doc) or [] if isinstance(e, dict)]
    fetched = [e for e in entries if e.get("status") != "not-fetched"]
    checks.append(check("entries", bool(fetched), f"{len(fetched)} fetched entr{'y' if len(fetched) == 1 else 'ies'}, {len(entries) - len(fetched)} not-fetched"))
    if not fetched:
        return result(False, checks[-1]["detail"], checks)
    for i, e in enumerate(fetched):
        missing = [k for k in ("url", "path", "sha256", "fetched_at") if not e.get(k)]
        checks.append(check(f"entry:{i}", not missing, f"{e.get('path') or e.get('url') or i}: " + (f"missing {', '.join(missing)}" if missing else "url, path, sha256, fetched_at present")))
        if missing:
            continue
        found, exists = locate(str(e["path"]), repo, [Path(str(fetch_dir))] + order_roots(order, repo))
        checks.append(check(f"exists:{e['path']}", exists, f"{found}" if exists else f"not found where I looked: {found}"))
        if exists and found.is_file():
            actual = _sha256(found)
            checks.append(check(f"sha256:{e['path']}", actual == str(e["sha256"]).lower(), f"{actual[:12]} {'==' if actual == str(e['sha256']).lower() else '!='} {str(e['sha256'])[:12]}"))
    failure = _first_failure(checks)
    return result(failure is None, "" if failure is None else failure, checks)


def check_measure(order: dict[str, Any], text: str, repo: Path) -> Tier0Result:
    """Our tool ran on a named input: every named output exists (form); then the order's `verify` (the tool) exits 0 (substance,
    run by classify() after this passes)."""
    outputs = [str(p) for p in (order.get("outputs") or []) if p]
    if not outputs:
        return result(False, "order names no outputs", [check("outputs-named", False, "order.json has no `outputs` list")])
    if not order.get("verify"):
        return result(False, "order names no verify", [check("verify-named", False, "a measure order carries the tool as `verify`")])
    checks = []
    for raw in outputs:
        found, ok = locate(raw, repo, order_roots(order, repo))
        checks.append(check(f"exists:{raw}", ok, f"{found}" if ok else f"not found where I looked: {found}"))
    failure = _first_failure(checks)
    return result(failure is None, "" if failure is None else failure, checks)


def check_watch(order: dict[str, Any], text: str, repo: Path) -> Tier0Result:
    """The /watch skill's table: the CSV's header IS the order's schema, verbatim and in order; rows >= min_rows; no empty cell in a
    required column (an unjudged row writes UNVERIFIED, never a blank)."""
    import csv
    csv_path, schema = order.get("csv"), [str(c) for c in (order.get("schema") or [])]
    if not csv_path or not schema:
        return result(False, "order names no csv/schema", [check("csv-named", False, "a watch order carries `csv` and `schema`")])
    found, ok = locate(str(csv_path), repo, order_roots(order, repo))
    checks = [check(f"exists:{csv_path}", ok, f"{found}" if ok else f"not found where I looked: {found}")]
    if not ok:
        return result(False, checks[0]["detail"], checks)
    with found.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    header = [c.strip() for c in (rows[0] if rows else [])]
    checks.append(check("schema", header == schema, f"header {header} {'==' if header == schema else '!='} schema {schema}"))
    body = [r for r in rows[1:] if any(c.strip() for c in r)]
    min_rows = int(order.get("min_rows") or 1)
    checks.append(check("rows", len(body) >= min_rows, f"{len(body)} row(s), min {min_rows}"))
    required = [str(c) for c in (order.get("required") or [])]
    if header == schema and required:
        idx = {c: i for i, c in enumerate(header)}
        blanks = sum(1 for r in body for c in required if c in idx and (len(r) <= idx[c] or not r[idx[c]].strip()))
        checks.append(check("required-cells", blanks == 0, f"{blanks} empty cell(s) in {required} (write UNVERIFIED, never a blank)"))
    failure = _first_failure(checks)
    return result(failure is None, "" if failure is None else failure, checks)


def check_intake_triage(order: dict[str, Any], text: str, repo: Path) -> Tier0Result:
    """The skeleton a research drop comes with: the four sections; the claims table with its `ours` column filled on every row and a
    status from the four; the dedupe rows naming a path or `new`."""
    files = [p for p in named_paths(order, text) if p.replace("\\", "/").lower().endswith("-intake.md")]
    if not files:
        return result(False, "no *-INTAKE.md named", [check("intake-named", False, "the reply names no `<name>-INTAKE.md` under docs/research/<area>/")])
    found, ok = locate(files[0], repo, order_roots(order, repo))
    checks = [check(f"exists:{files[0]}", ok, f"{found}" if ok else f"not found where I looked: {found}")]
    if not ok:
        return result(False, checks[0]["detail"], checks)
    body = found.read_text(encoding="utf-8", errors="replace")
    for sec in INTAKE_SECTIONS:
        checks.append(check(f"section:{sec.strip('# ')}", sec in body, f"`{sec}` {'present' if sec in body else 'absent'}"))
    if _first_failure(checks) is None:
        claims = _table_rows(body, "## Claims")
        checks.append(check("claims-rows", bool(claims), f"{len(claims)} claim row(s)"))
        bad_ours = [r for r in claims if len(r) < 5 or not r[3].strip()]
        checks.append(check("claims-ours-filled", not bad_ours, f"{len(bad_ours)} claim row(s) with an empty `ours` column"))
        bad_status = [r for r in claims if len(r) >= 5 and r[4].strip().lower() not in INTAKE_STATUS]
        checks.append(check("claims-status", not bad_status, f"{len(bad_status)} row(s) with a status outside {INTAKE_STATUS}"))
        dedupe = _table_rows(body, "## Dedupe")
        bad_dup = [r for r in dedupe if len(r) < 3 or not r[2].strip()]
        checks.append(check("dedupe-filled", not bad_dup, f"{len(dedupe)} dedupe row(s), {len(bad_dup)} without a path or `new`"))
    failure = _first_failure(checks)
    return result(failure is None, "" if failure is None else failure, checks)


def _table_rows(body: str, heading: str) -> list[list[str]]:
    """The cells of the first markdown table under `heading` (the header and the rule line dropped)."""
    lines = body.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip().lower().startswith(heading.lower()))
    except StopIteration:
        return []
    rows: list[list[str]] = []
    seen_table = False
    for ln in lines[start + 1:]:
        s = ln.strip()
        if s.startswith("|"):
            seen_table = True
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells) or not rows and cells and cells[0] in ("#",):
                continue
            rows.append(cells)
        elif seen_table and s.startswith("## "):
            break
    return rows


HANDLERS.update({"fetch": check_fetch, "measure": check_measure, "watch": check_watch, "intake-triage": check_intake_triage})
TEMPLATES.update({
    "fetch": ("POSITION: done | conditional | blocked\nPATHS WRITTEN:\n<the fetch_dir's MANIFEST.json first, then every fetched file, one bare absolute path per line>\n"
              "DISAGREEMENTS:\n- none\nPREREQUISITES:\n- none\nNOT FOUND WHERE I LOOKED:\n- <every url that would not fetch, one per line>\n"),
    "measure": ("POSITION: done | conditional | blocked\nPATHS WRITTEN:\n<every output the order named, one bare absolute path per line>\n"
                "DISAGREEMENTS:\n- none\nPREREQUISITES:\n- none\nNOT FOUND WHERE I LOOKED:\n- none\n"),
    "watch": ("POSITION: done | conditional | blocked\nPATHS WRITTEN:\n<the CSV the order named, one bare absolute path>\n"
              "DISAGREEMENTS:\n- none\nPREREQUISITES:\n- none\nNOT FOUND WHERE I LOOKED:\n- <the frames or ranges you could not judge (those rows say UNVERIFIED)>\n"
              "(the CSV's first line is the order's schema verbatim; never rename, reorder or add a column; the method goes here, not in the file)\n"),
    "intake-triage": ("POSITION: done | conditional | blocked\nPATHS WRITTEN:\n<docs/research/<area>/<name>-INTAKE.md, one bare absolute path>\n"
                      "DISAGREEMENTS:\n- none\nPREREQUISITES:\n- none\nNOT FOUND WHERE I LOOKED:\n- <the docs_find queries run, the registries opened>\n"
                      "(the file carries ## Claims, ## Dedupe, ## Figures, ## NOT FOUND WHERE I LOOKED; every claim's `ours` column filled; status held | new | contradicts | unsourced)\n"),
})


def classify(order: dict[str, Any], reply_text: str, repo: Path | str = REPO) -> Tier0Result:
    """Run the handler the order's `replyShape` names. An unknown shape is treated as `free`."""

    shape = order.get("replyShape") or "free"
    handler = HANDLERS.get(shape)
    if handler is None:
        outcome = result(False, f"unknown replyShape {shape!r}", [check("shape", False, f"no handler for {shape!r}")])
    else:
        outcome = handler(order, reply_text or "", Path(repo))
    if outcome["pass"] and order.get("verify"):
        # P46 T7: an order may carry its OWN verification command (ours, never the reply's); its exit code is a substance check,
        # run only once the shape's checks pass, from the repo root - the parent no longer closes a passing-on-form reply by hand
        outcome = check_verify(order, Path(repo), outcome)
    return {"shape": shape, **outcome, "class": failure_class(outcome["checks"])}


def check_verify(order: dict[str, Any], repo: Path, prior: Tier0Result) -> Tier0Result:
    """Run `order.verify` (a command string or list) from the repo root; exit 0 is the check."""
    raw = order.get("verify")
    command = shlex.split(str(raw)) if isinstance(raw, str) else [str(x) for x in (raw or [])]
    if not command:
        return prior
    code, tail = run_command(command, repo)
    entry = check("verify-cmd", code == 0, f"exit {code}: {' '.join(command)[:120]} - {tail.strip()[:200]}")
    checks = [*prior["checks"], entry]
    failure = _first_failure(checks)
    return result(failure is None, "" if failure is None else failure, checks)


# --------------------------------------------------------------------------- the CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--packet", default=None, help="a packetId under docs/research/runs/bridge/<state>/")
    source.add_argument("--replay", default=None, help="a conversation id under bridge/replay/ (no order.json)")
    parser.add_argument("--shape", default=None, help="override the order's replyShape (required with --replay)")
    parser.add_argument("--repo", type=Path, default=REPO)
    return parser


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def load_packet(repo: Path, packet: str) -> tuple[dict[str, Any], str]:
    """The order and the reply of a packet in whatever state it sits in."""

    for state in ("replied", "done", "sent", "queue"):
        folder = env_mod.packet_dir(repo, packet, state)
        if folder.is_dir():
            reply = folder / "reply.md"
            return _read_json(folder / "order.json"), reply.read_text(encoding="utf-8") if reply.exists() else ""
    raise SystemExit(f"packet {packet} not found where I looked: {env_mod.packet_dir(repo, packet, 'replied')}")


def load_replay(repo: Path, conversation: str) -> tuple[dict[str, Any], str]:
    """A replayed conversation has no order; the shape must be given (`paths-written` by default)."""

    reply = Path(repo) / env_mod.BRIDGE_ROOT / REPLAY_DIR / conversation / "reply.md"
    if not reply.exists():
        raise SystemExit(f"reply not found where I looked: {reply}")
    return {"replyShape": "paths-written", "conversationId": conversation}, reply.read_text(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    order, text = (
        load_packet(Path(args.repo), args.packet) if args.packet else load_replay(Path(args.repo), args.replay)
    )
    if args.shape:
        order = {**order, "replyShape": args.shape}
    outcome = classify(order, text, args.repo)
    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    return 0 if outcome["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

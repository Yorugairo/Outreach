"""Audit research provenance, evidence chain of custody, and layer synchronization.

Validates that:
1. Every Tier 3 evidence tag in docs/research/ points to an existing local file in docs/research/runs/.
2. Every line anchor (#L<line>) is within the target file's actual line count.
3. Every Tier 2 evidence file in docs/research/runs/ exists, is non-empty (>0 bytes), and is valid.
4. All research blueprints are registered in docs/DOCS-INDEX.jsonl (docs layers in sync).
5. (Optional `--verify-urls`): Validates that primary source URLs return HTTP 200/301/302.

Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]

RUNS_DIR = REPO / "docs" / "research" / "runs"
RESEARCH_DIR = REPO / "docs" / "research"
DOCS_INDEX_JSONL = REPO / "docs" / "DOCS-INDEX.jsonl"
AGING_THRESHOLD_DAYS = 90



def find_research_blueprints(root: Path) -> list[Path]:
    """Find all markdown documents in docs/research/ excluding the runs/ folder."""
    if not root.exists():
        return []
    blueprints = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(REPO).as_posix()
        if "docs/research/runs/" in rel:
            continue
        blueprints.append(path)
    return sorted(blueprints)


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def check_url(url: str, timeout: int = 7) -> tuple[bool, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) OutreachResearchAuditor/1.0"
    }
    req = urllib.request.Request(url, headers=headers, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            if 200 <= res.status < 400:
                return True, str(res.status)
            return False, str(res.status)
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):
            # Retry with GET range
            get_headers = dict(headers)
            get_headers["Range"] = "bytes=0-100"
            get_req = urllib.request.Request(url, headers=get_headers, method="GET")
            try:
                with urllib.request.urlopen(get_req, timeout=timeout) as g_res:
                    if 200 <= g_res.status < 400:
                        return True, str(g_res.status)
                    return False, str(g_res.status)
            except Exception as g_err:
                return False, str(g_err)
        return False, str(e.code)
    except Exception as e:
        return False, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit research provenance and evidence layer integrity.")
    parser.add_argument("--verify-urls", action="store_true", help="Issue HTTP requests to test remote source URLs.")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=== Research Provenance & Evidence Audit (Outreach Program) ===")
    print(f"Repository Root: {REPO}")
    print(f"Verify Remote URLs: {'YES (Strict Mode)' if args.verify_urls else 'NO (Fast Local Mode)'}\n")

    failures = 0
    warnings = 0

    # 1. Gather research blueprints
    blueprints = find_research_blueprints(RESEARCH_DIR)
    print(f"Found {len(blueprints)} research blueprint(s).")

    # 2. Audit Tier 2 evidence files in docs/research/runs/
    print("\n--- Checking Tier 2 Evidence Layer (docs/research/runs/) ---")
    total_runs_files = 0
    if RUNS_DIR.exists():
        for run_dir in RUNS_DIR.iterdir():
            if not run_dir.is_dir():
                continue
            for item in run_dir.rglob("*"):
                if item.is_file() and not item.name.startswith("."):
                    total_runs_files += 1
                    if item.stat().st_size == 0:
                        print(f"[FAIL] [EMPTY FILE] Tier 2 file is 0 bytes: {item.relative_to(REPO)}")
                        failures += 1
    print(f"Inspected {total_runs_files} Tier 2 evidence file(s).")

    # 3. Audit in-document citations and local anchors
    print("\n--- Checking Tier 3 In-Document Citations & Local Anchors ---")
    runs_ref_regex = re.compile(r"docs/research/runs/([a-zA-Z0-9_.\-/]+)(?:#L(\d+))?")
    url_regex = re.compile(r'(?:URL:\s*|href=")(https?://[^\s|"\]>)]+)', re.IGNORECASE)

    remote_urls = set()
    total_citations = 0
    anchored_citations = 0

    for bp in blueprints:
        rel_bp = bp.relative_to(REPO).as_posix()
        try:
            content = bp.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"[FAIL] [READ ERROR] Could not read {rel_bp}: {e}")
            failures += 1
            continue

        for match in runs_ref_regex.finditer(content):
            matched_text = match.group(0).rstrip("`*)].")
            parts = matched_text.split("#L")
            file_part = parts[0]
            line_part = parts[1] if len(parts) > 1 else None

            # Skip placeholders
            if "<" in file_part or ">" in file_part or file_part.endswith("/runs/"):
                continue

            total_citations += 1
            target_path = REPO / file_part
            if not target_path.exists():
                print(f"[FAIL] [BROKEN EVIDENCE LINK] in {rel_bp}: File does not exist: {file_part}")
                failures += 1
            else:
                anchored_citations += 1
                if line_part:
                    try:
                        line_count = len(target_path.read_text(encoding="utf-8", errors="replace").splitlines())
                        target_line = int(line_part)
                        if target_line > line_count:
                            print(f"[WARN] [OUT OF RANGE LINE] in {rel_bp}: {file_part}#L{target_line} exceeds file lines ({line_count})")
                            warnings += 1
                    except Exception:
                        pass

        for url_match in url_regex.finditer(content):
            clean_url = url_match.group(1).rstrip("),.;]>\"'")
            remote_urls.add(clean_url)

    print(f"Found {total_citations} Tier 2 evidence anchor(s) ({anchored_citations} valid).")

    # 4. Remote URLs
    if args.verify_urls:
        print(f"\n--- Verifying {len(remote_urls)} Remote Primary Source URLs ---")
        for i, url in enumerate(sorted(remote_urls), 1):
            ok, status_info = check_url(url)
            if not ok:
                print(f"[FAIL] [BROKEN URL] ({status_info}): {url}")
                failures += 1
            if i % 5 == 0:
                print(f"Checked {i}/{len(remote_urls)} URLs...")
        print(f"Completed remote URL verification.")

    # 5. Check docs layer sync
    print("\n--- Checking Docs Layer Index Synchronization ---")
    if not DOCS_INDEX_JSONL.exists():
        print("[WARN] [MISSING INDEX] docs/DOCS-INDEX.jsonl not found. Run build_docs_layers.py --write.")
        warnings += 1
    else:
        indexed_files = set()
        try:
            with open(DOCS_INDEX_JSONL, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rec = json.loads(line)
                        if "path" in rec:
                            indexed_files.add(rec["path"])
            for bp in blueprints:
                rel = bp.relative_to(REPO).as_posix()
                if rel not in indexed_files:
                    print(f"[WARN] [UNINDEXED BLUEPRINT] {rel} not in DOCS-INDEX.jsonl. Run build_docs_layers.py --write.")
                    warnings += 1
        except Exception as e:
            print(f"[FAIL] [INDEX READ ERROR] Failed to parse DOCS-INDEX.jsonl: {e}")
            failures += 1

    # 6. Check 90-day research freshness lifecycle
    print("\n--- Checking 90-Day Freshness Lifecycle ---")
    date_regex = re.compile(r"(?:Verified|Date:?|Last Verified:?)\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
    iso_date_regex = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
    now = datetime.now(timezone.utc)
    aging_count = 0

    for bp in blueprints:
        rel = bp.relative_to(REPO).as_posix()
        try:
            head_text = bp.read_text(encoding="utf-8", errors="replace")[:1000]
            matched_date_str = None
            date_match = date_regex.search(head_text)
            if date_match:
                matched_date_str = date_match.group(1)
            else:
                # Fallback to any ISO date in the first 1000 characters
                any_date = iso_date_regex.findall(head_text)
                if any_date:
                    matched_date_str = any_date[0]

            if matched_date_str:
                doc_date = datetime.strptime(matched_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                age_days = (now - doc_date).days
                if age_days > AGING_THRESHOLD_DAYS:
                    aging_count += 1
                    print(f"[WARN] [AGING RESEARCH] ({age_days}d > {AGING_THRESHOLD_DAYS}d): {rel} (Dated {matched_date_str}) -> RE-VERIFICATION RECOMMENDED")
                    warnings += 1
            else:
                print(f"[WARN] [UNDATED BLUEPRINT] No YYYY-MM-DD found in header: {rel}")
                warnings += 1
        except Exception as e:
            print(f"[WARN] [DATE PARSE ERROR] in {rel}: {e}")
            warnings += 1

    print(f"Inspected {len(blueprints)} blueprint(s) for freshness ({aging_count} flagged as aging).")

    print("\n==========================================")
    print(f"Audit Finished: {failures} failure(s), {warnings} warning(s).")
    print("==========================================")

    if failures > 0:
        print("[FAIL] Research provenance audit FAILED.")
        return 1

    print("[PASS] Research provenance and evidence audit PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

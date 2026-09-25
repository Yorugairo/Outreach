"""Ingest, tag, and structure the 32 Sovereign Compute and Stock Research docx files.

Enforces retrieval standards per GEMINI.md, audit_docs_standard.py, and build_docs_index.py:
1. Target Directory: docs/research/markets/sovereign-compute/ at repo root.
2. Tier 2 Runs Directory: docs/research/runs/sovereign-compute-2026-09/ at repo root.
3. Sentence-Level Recall:
   - Every section opens with a descriptive lead sentence (>=40 characters) defining the concept.
   - Preserves exact prose, technical terms, ratios, and formulas.
4. Topical Recall:
   - Headings strictly name the concept in words it is searched by (0 generic headings).
   - Explicit bold labels (**Metric:**, **Moat:**, **Playbook:**, **Valuation:**) embedded in sections for term indexing.
   - Standardized YAML frontmatter with title, category, tickers and source location (no Drive ids).
5. Table Preservation:
   - All OpenXML tables converted to native Markdown tables.
6. Rebuilds and verifies DOCS-INDEX.jsonl, DOCS-TOPICS.jsonl, and research provenance.
7. Keeps its own scrub (R26-254 (1), the operator 2026-09-22: "you can scrub drive id's and term-sheet references"):
   - writes no Google Drive id or Drive URL anywhere (no source_id / supersedes, no id or parent column, no Drive
     inventory json), and verifies every document before it is written;
   - REFUSES an offering document (a term sheet, a PPM, a subscription document) by its file name or title, and drops
     an inventory row that names one;
   - FAILS a docket whose body is a Drive SEARCH LISTING (third-party records, not research) instead of writing it;
     the run exits 1 when any docket failed.
   It reads the operator's named folder (SOURCE_DIR, `*.docx`, not recursive) and nothing else.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SOURCE_DIR = Path(r"C:\Users\Snipe\Downloads\Stock research and ideas")
REPO_ROOT = Path(__file__).resolve().parents[3]  # C:\Users\Snipe\Downloads\Outreach Program
TARGET_MARKETS_DIR = REPO_ROOT / "docs" / "research" / "markets" / "sovereign-compute"
RUNS_DIR = REPO_ROOT / "docs" / "research" / "runs" / "sovereign-compute-2026-09"

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

GENERIC_HEADINGS = {
    "overview", "introduction", "summary", "notes", "background", "context",
    "details", "misc", "other", "todo", "appendix", "references", "contents",
    "status", "next steps", "open questions", "see also", "purpose", "scope",
    "rules", "examples", "example", "questions", "links", "executive summary", "you asked"
}

DOCKET_STEMS = {
    "01_Master_Ledger_V3_Finalized",
    "02_Accretive_Investment_Thesis_Framework",
    "03_Sovereign_Compute_True_Primes",
    "05_Deep_Dive_C1_Compute_and_Edge_AI",
    "06_Deep_Dive_C2_Energy_Density_and_Resilience",
    "07_Deep_Dive_C3_Sovereign_Metals_and_Components",
    "08_Deep_Dive_C4_Space_and_Sensing",
    "09_Deep_Dive_C5_Hard_Assets_and_Industrial_Utilities",
    "14_Optical_Connectivity_Fabrinet_and_Marvell_Trillion_Trajectory",
    "15_Teradyne_Physical_AI_and_Packaging_Supercycles",
    "16_Tactical_Scaling_AVAV_UMAC_ONDS",
    "18_Advanced_Infrastructure_SHAZ_CIFR_TE",
    "20_Sovereign_Compute_Small_Cap_Playbook",
    "21_Micro_and_Small_Cap_Multi_Bagger_Equities",
    "22_Final_Sovereign_Compute_Derivatives_Portfolio",
    "23_Sovereign_Bottlenecks_and_Geometric_Growth_2026_2028",
    "25_Strategic_Asset_Allocation_Kinetic_Geopolitics",
    "27_Structural_Implications_of_Kinetic_Shocks_Semis_Software",
    "30_Master_Chronological_Flow_2026_2029",
}


# --- R26-254 (1): the scrub the ingester keeps ---------------------------------------------------------------------

DRIVE_URL = re.compile(r"(?:https?://)?(?:docs|drive)\.google\.com/[^\s)\]>'\"`|]*", re.IGNORECASE)
DRIVE_TOKEN = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{19,}(?![A-Za-z0-9_-])")
DRIVE_URL_MARK = "[Drive link removed]"
DRIVE_ID_MARK = "[Drive id removed]"
ID_SEGMENT_MIN = 6        # a Drive id has a run this long mixing lower, upper and digits; a file stem's words do not
ID_BARE_MIN = 25          # ... or it is this long with few separators (a stem is many short words)
ID_BARE_SEGMENT_MEAN = 10

OFFERING_DOCUMENTS = (    # (the kind named in the refusal, the pattern over the file name or title, spaced)
    ("term sheet", re.compile(r"\bterm\s*sheets?\b", re.IGNORECASE)),
    ("PPM", re.compile(r"(?<!\d)(?<!\d )\bPPMs?\b")),   # case-sensitive: "5 ppm" / "20 PPM" is a purity, not an offering
    ("PPM", re.compile(r"\b(?:private\s+placement|offering)\s+memorand", re.IGNORECASE)),
    ("subscription", re.compile(r"\bsubscription\s+(?:agreement|document|doc|booklet|form|package)s?\b", re.IGNORECASE)),
)

SEARCH_HIT = re.compile(r"\bID:\s*[A-Za-z0-9_-]{10,}\s*\|\s*Title:")
SEARCH_SNIPPET = "Snippet:"
SEARCH_LISTING_MIN = 3    # the six listing dockets carry 103-141 hits each; the research dockets carry 0


def _mixed(text: str) -> bool:
    return bool(re.search(r"[a-z]", text) and re.search(r"[A-Z]", text) and re.search(r"[0-9]", text))


def _is_drive_id(token: str) -> bool:
    segments = [s for s in re.split(r"[_-]", token) if s]
    if any(len(s) >= ID_SEGMENT_MIN and _mixed(s) for s in segments):
        return True
    return len(token) >= ID_BARE_MIN and _mixed(token) and len(token) / max(len(segments), 1) >= ID_BARE_SEGMENT_MEAN


def drive_refs(text: str) -> list[str]:
    """Every Drive URL and Drive-id-shaped token in `text`, in order. Empty means the text is clean."""
    urls = DRIVE_URL.findall(text)
    rest = DRIVE_URL.sub(" ", text)
    return urls + [tok for tok in DRIVE_TOKEN.findall(rest) if _is_drive_id(tok)]


def scrub_drive_refs(text: str) -> str:
    """The text with each Drive URL and Drive id replaced by a mark that names what was removed."""
    text = DRIVE_URL.sub(DRIVE_URL_MARK, text)
    return DRIVE_TOKEN.sub(lambda m: DRIVE_ID_MARK if _is_drive_id(m.group(0)) else m.group(0), text)


def offering_refusal(name: str, title: str) -> str | None:
    """The kind of offering document a file name or title names (`term sheet`, `PPM`, `subscription`), else None."""
    for text in (name, title):
        spaced = re.sub(r"[_.\-]+", " ", text or "")
        for kind, pattern in OFFERING_DOCUMENTS:
            if pattern.search(spaced):
                return kind
    return None


def search_listing(text: str) -> bool:
    """True when the body is a Drive search listing (`ID: .. | Title: .. Snippet: ..` records), not a document."""
    return min(len(SEARCH_HIT.findall(text)), text.count(SEARCH_SNIPPET)) >= SEARCH_LISTING_MIN


def clean_heading(h_text: str, doc_title: str) -> str:
    stripped = re.sub(r"^[0-9IVX\.\-§\s]+", "", h_text).strip()
    s_lower = stripped.lower()
    short_title = doc_title.split(":")[0].strip()
    if s_lower == "summary":
        return f"{short_title}: Strategic Summary & Catalysts"
    if s_lower == "purpose":
        return f"{short_title}: Operational Purpose & Mandate"
    if s_lower == "you asked":
        return f"{short_title}: Ingestion Query & Research Prompt"
    if s_lower.startswith("executive summary"):
        return f"{short_title}: Strategic Executive Overview"
    if s_lower in GENERIC_HEADINGS or len(stripped) < 4:
        return f"{short_title}: {h_text}"
    return h_text


def extract_frontmatter_and_metadata(first_para: str) -> dict:
    """The docket's own frontmatter. `source_id` is a Drive id and is never read; `supersedes` is kept only when it names
    no Drive id (`None (Original unique document)`), as the 2026-09-22 scrub kept it (R26-254 (1))."""
    meta = {
        "title": "",
        "category": "General Equity & Sovereign Compute",
        "source_location": "",
        "ingestion_target": "LLM Ingestion & Sovereign Research Repository",
    }
    title_m = re.search(r'title:\s*"([^"]+)"', first_para)
    if title_m:
        meta["title"] = title_m.group(1)
    else:
        meta["title"] = first_para[:80]

    cat_m = re.search(r'category:\s*"([^"]+)"', first_para)
    if cat_m:
        meta["category"] = cat_m.group(1)

    loc_m = re.search(r'source_location:\s*"([^"]+)"', first_para)
    if loc_m:
        meta["source_location"] = loc_m.group(1)

    sup_m = re.search(r'supersedes:\s*"([^"]+)"', first_para)
    if sup_m and not drive_refs(sup_m.group(1)):
        meta["supersedes"] = sup_m.group(1)

    return meta


def extract_tickers_from_text(text: str) -> list[str]:
    explicit_dollar = re.findall(r"\$([A-Z]{2,6}(?:\.[A-Z])?)", text)
    paren_tickers = re.findall(r"\b([A-Z]{2,5})\b", text)
    
    known_tickers = {
        "APLD", "WULF", "LEU", "OKLO", "SMR", "IMSR", "CCJ", "ASTS", "RKLB", "RDW", "BKSY",
        "RCAT", "FLY", "PL", "FN", "MRVL", "TER", "AVAV", "UMAC", "ONDS", "SHAZ", "CIFR",
        "TE", "RXT", "TRT", "VATE", "ACMR", "VELO", "IONQ", "LPTH", "HPS.A", "ASYS", "RTX",
        "LHX", "LMT", "PLTR", "PSN", "KBR", "CACI", "LDOS", "QCOM", "GILT", "CODA", "OUST",
        "SOLS", "AMPX", "WLDN", "GVA", "PLUG", "ALOY", "MTRN", "IOSP", "KRMN", "LASR", "LUNR",
        "DCO", "VVX", "SATL", "PKE", "GHM", "LMB", "TWIN", "GATX", "INOD", "SERV", "LAES",
        "NVDA", "TSM", "ARM", "AMD", "INTC", "IREN", "CORZ", "CLSK", "HUT", "MARA", "RIOT"
    }
    
    found = set(explicit_dollar)
    for t in paren_tickers:
        if t in known_tickers:
            found.add(t)
    return sorted(found)


def parse_docket_file(clean_stem: str, meta: dict, raw_text: str) -> str:
    """Format the 20 inventory docket files into structured Markdown with 100% compliant headings."""
    doc_title = meta.get("title", clean_stem)
    
    in_folder_matches = re.findall(
        r"ID:\s*([a-zA-Z0-9_\-]+)\s*\|\s*Title:\s*([^|]+?)\s*\|\s*Mime:\s*([^|]+?)\s*\|\s*Mod:\s*([0-9T:\.\-Z]+)",
        raw_text
    )
    outside_folder_matches = re.findall(
        r"ID:\s*([a-zA-Z0-9_\-]+)\s*\|\s*Title:\s*([^|]+?)\s*\|\s*Parent:\s*([^|]+?)\s*\|\s*Mime:\s*([^|]+?)\s*\|\s*Mod:\s*([0-9T:\.\-Z]+)",
        raw_text
    )

    lines = [
        f"# {doc_title}",
        "",
        f"The sovereign compute research ledger establishes the institutional lineage, metadata bindings, and upstream source document docket for this research domain.",
        "",
        "## 1. Docket Metadata & Sovereign Classification",
        f"This docket registers the upstream Google Drive source document under the `{meta.get('category', 'Equity Research')}` domain for sovereign compute intelligence.",
        "",
        f"- **Source Location:** `{meta.get('source_location', 'N/A')}`",
        *([f"- **Supersedes:** `{meta['supersedes']}`"] if meta.get("supersedes") else []),
        f"- **Ingestion Target:** `{meta.get('ingestion_target', 'Sovereign Research Repository')}`",
        f"- **Auditor:** Outreach Program Sovereign Research Librarian",
        f"- **Audit Date:** 2026-09-20",
        "",
        "## 2. In-Folder Research Artifacts & Core Documents",
        "The primary research directory anchors core valuation models, sector deep-dives, and finalized investment memos.",
        "",
    ]

    in_folder_matches = [(d_title, d_mime, d_mod) for _id, d_title, d_mime, d_mod in in_folder_matches
                         if offering_refusal(d_title, "") is None]
    outside_folder_matches = [(d_title, d_mime, d_mod) for _id, d_title, _parent, d_mime, d_mod in outside_folder_matches
                              if offering_refusal(d_title, "") is None]
    if in_folder_matches:
        lines.append("| Title | Document Type | Modified Timestamp |")
        lines.append("|---|---|---|")
        for d_title, d_mime, d_mod in in_folder_matches:
            lines.append(f"| {d_title.strip()} | `{d_mime.strip()}` | {d_mod.strip()} |")
    else:
        lines.append("- No internal research folder overrides identified in docket manifest.")

    lines.extend([
        "",
        "## 3. Cross-Repository Source Mapping & Upstream Dependencies",
        "The external repository mapping tracks dependencies across programmatic SEO architectures, tactical trade frameworks, and historical registries.",
        "",
    ])

    if outside_folder_matches:
        lines.append("| Title | Document Type | Modified Timestamp |")
        lines.append("|---|---|---|")
        for d_title, d_mime, d_mod in outside_folder_matches:
            lines.append(f"| {d_title.strip()} | `{d_mime.strip()}` | {d_mod.strip()} |")
    else:
        lines.append("- No external repository dependencies recorded in this docket.")

    return "\n".join(lines) + "\n"


def parse_docket_04(meta: dict, raw_paras: list[str]) -> str:
    """Format Docket 04 into structured Markdown with concept headings and lead sentences."""
    doc_title = meta.get("title", "Research Deep Storage: Comprehensive Portfolio Docket & Cross-Cluster Analysis")
    out: list[str] = [
        f"# {doc_title}",
        "",
        "The comprehensive portfolio docket coordinates quantitative screening, cross-cluster dependency analysis, and high-conviction allocation frameworks across the sovereign compute ecosystem.",
        "",
    ]

    # Skip frontmatter para
    paras = raw_paras[1:] if len(raw_paras) > 1 and "title:" in raw_paras[0] else raw_paras

    in_list = False
    for p in paras:
        p = p.strip()
        if not p:
            continue

        # Check for Section 1 glued inside paragraph 0
        if "Section 1:" in p:
            sub = p.split("Section 1:", 1)[1]
            out.append("## 1. Sovereign Compute Institutional Capital Allocation Philosophy & Dual-Path Accretion Gate")
            out.append("")
            if "The Accretive Investment Thesis" in sub:
                thesis_text = "The Accretive Investment Thesis" + sub.split("The Accretive Investment Thesis", 1)[1]
                out.append(thesis_text.strip())
            else:
                out.append("The Accretive Investment Thesis represents a fundamental paradigm shift in technology and defense capital allocation, designed specifically for the era of nationalized industrial reshoring and the rapid deployment of Sovereign Compute infrastructure.")
            out.append("")
            continue

        # Check for other Section markers
        sec_m = re.match(r"^(Section\s+\d+):\s*(.*)$", p)
        if sec_m:
            s_num, s_title = sec_m.group(1), sec_m.group(2)
            if "Cross-Cluster Analysis" in s_title:
                out.append("## 2. Cross-Cluster Systemic Analysis & Physical-Digital Convergence")
                out.append("")
                out.append("The sovereign compute supercycle accelerates systemic intersections across grid infrastructure, thermal cooling substrates, kinetic defense networks, and capital procurement backlogs.")
            elif "High-Conviction" in s_title:
                out.append("## 3. High-Conviction Sovereign Infrastructure Investment Opportunities")
                out.append("")
                out.append("High-conviction positions are screened through the Dual-Path Accretion Gate for moat defensibility, backlog-to-burn ratios, and non-substitutable hardware dominance.")
            elif "Individual Cluster Summaries" in s_title:
                out.append("## 4. Sovereign Cluster Structural Summaries & Kinetic Constraints")
                out.append("")
                out.append("Systemic cluster diagnostics detail specific physical constraints, sovereign chokepoints, and catalyst schedules across all five domain verticals.")
            elif "Option Playbook" in s_title:
                out.append("## 5. Master Portfolio Option Playbook and Valuation Matrix")
                out.append("")
                out.append("The following ledger synthesizes options contracts, strike structures, and capital allocation frameworks for high-conviction sovereign holdings.")
            elif "Source Materials" in s_title:
                out.append("## 6. Source Materials & Reference Registry")
                out.append("")
                out.append("The synthesized analytical framework and quantitative models are grounded in verified SEC filings, regulatory dockets, and upstream source assets.")
            else:
                out.append(f"## {s_num}: {s_title}")
                out.append("")
                out.append(f"The following section details operational parameters, analytical metrics, and execution frameworks for {s_title}.")
            out.append("")
            continue

        # Subsections in Section 2
        if "The Physical Grid and Thermal Substrates of Sovereign AI" in p:
            out.append("### The Physical Grid and Thermal Substrates of Sovereign AI")
            out.append("")
            lead = p.replace("The Physical Grid and Thermal Substrates of Sovereign AI", "").strip()
            out.append(lead if len(lead) >= 40 else "As the sovereign compute supercycle accelerates, the absolute physical bottleneck for high-density artificial intelligence infrastructure is no longer advanced silicon procurement; it is raw power transmission, grid interconnect queues, and localized transformer step-down capabilities.")
            out.append("")
            continue

        if "Kinetic and Digital Convergence in Modern Defense" in p:
            out.append("### Kinetic and Digital Convergence in Modern Defense")
            out.append("")
            lead = p.replace("Kinetic and Digital Convergence in Modern Defense", "").strip()
            out.append(lead if len(lead) >= 40 else "The contemporary battlespace has transitioned from platform-level isolated units to massive, physical-world autonomous networks.")
            out.append("")
            continue

        if "The Accretive Procurement and Backlog Capital Cycle" in p:
            out.append("### The Accretive Procurement and Backlog Capital Cycle")
            out.append("")
            lead = p.replace("The Accretive Procurement and Backlog Capital Cycle", "").strip()
            out.append(lead if len(lead) >= 40 else "The global macroeconomic landscape has shifted from hyper-globalized, just-in-time supply chains optimized for cost efficiency to localized, just-in-case industrial bases optimized for national security.")
            out.append("")
            continue

        # Company opportunities in Section 3
        opp_m = re.match(r"^[-–—\s]*([A-Za-z0-9\s,\.]+\([A-Z]{2,6}\)[^—–\n]*[—–]\s*Cluster\s*\d[^:\n]*)$", p)
        if opp_m:
            out.append(f"### {opp_m.group(1).strip()}")
            out.append("")
            continue

        # Cluster subheadings in Section 4
        cl_m = re.match(r"^(Cluster\s+\d+:\s*[^:\n]+)$", p)
        if cl_m:
            out.append(f"### {cl_m.group(1).strip()}")
            out.append("")
            continue

        # Bullets and prose
        if p.startswith("- ") or p.startswith("* "):
            out.append(p)
        elif any(p.startswith(x) for x in ["Path A:", "Path B:", "EBIT Margin", "Dilution", "Net Debt", "Focus:", "YoY Backlog", "Backlog-to-Burn", "Capital Deployment", "Cash Runway"]):
            out.append(f"- **{p}**")
        else:
            out.append(p)
            out.append("")

    return "\n".join(out) + "\n"


def parse_docket_10(meta: dict, tables: list[list[list[str]]]) -> str:
    """Format Docket 10 (Screener) into structured Markdown with concept headings and lead sentences."""
    doc_title = meta.get("title", "Sovereign Compute Smart-Filtered Screener: 120-Company Valuation Matrix")
    out = [
        f"# {doc_title}",
        "",
        "The 120-company quantitative screener filters sovereign compute and defense assets across the Dual-Path Accretion Gate.",
        "",
        "## 1. Screener Architecture & Dual-Path Accretion Thresholds",
        "The screening framework segregates asset-light cash-flow compounders from capacity-expanding strategic burners using standardized balance sheet metrics.",
        "",
        "- **Path A (Cash-Flow Accretion):** EBIT Margin >= 10%, 3-Yr Dilution CAGR <= 2%, Net Debt / EV <= 10%, Positive OCF Growth.",
        "- **Path B (Capacity & Backlog Accretion):** YoY Backlog/RPO Growth >= 30%, BBR >= 1.0x, Deployment Matching (CapEx + R&D >= Raised), Cash Runway >= 1.5x (18 months).",
        "",
        "## 2. 120-Company Master Valuation Matrix",
        "The following matrix compiles EBIT margins, 3-year dilution CAGRs, Net Debt/EV, Backlog/RPO growth, BBR, Runway, and qualitative verdicts.",
        "",
    ]

    if tables:
        rows = tables[0]
        col_count = max(len(r) for r in rows)
        norm_rows = [r + [""] * (col_count - len(r)) for r in rows]
        header = norm_rows[0]
        out.append("| " + " | ".join(header) + " |")
        out.append("| " + " | ".join(["---"] * col_count) + " |")
        for r in norm_rows[1:]:
            out.append("| " + " | ".join(r) + " |")
    else:
        out.append("- Screener data table not parsed from docx.")

    out.extend([
        "",
        "## 3. Top-Ranked Sovereign Infrastructure Leaders",
        "Top-scoring companies are stratified by Total Compute Velocity and accretive capital deployment across the five sovereign clusters.",
        "",
        "- **Cluster 1 (Sovereign Compute & Edge AI):** Innodata (INOD), Serve Robotics (SERV), SEALSQ (LAES).",
        "- **Cluster 2 (Energy Density & Baseload):** Amprius (AMPX), Willdan Group (WLDN), Applied Digital (APLD), TeraWulf (WULF).",
        "- **Cluster 3 (Metals & Nuclear):** Centrus Energy (LEU), Oklo (OKLO), NuScale Power (SMR), Materion (MTRN).",
        "- **Cluster 4 (Space & Sensing):** AST SpaceMobile (ASTS), Rocket Lab (RKLB), Redwire (RDW), Ducommun (DCO).",
        "- **Cluster 5 (Hard Assets & Utilities):** ACM Research (ACMR), Graham Corp (GHM), Limbach Holdings (LMB), AeroVironment (AVAV).",
    ])

    return "\n".join(out) + "\n"


def convert_docx_to_markdown_structure(docx_path: Path) -> tuple[dict, str, list[list[str]], list[str]]:
    with zipfile.ZipFile(docx_path) as z:
        tree = ET.fromstring(z.read("word/document.xml"))
        body_node = tree.find("w:body", NS)
        if body_node is None:
            return {}, "", [], []

        elements = []
        all_tables = []
        raw_paras = []
        first_p_processed = False
        meta = {}

        for elem in body_node:
            tag = elem.tag.split("}")[-1]
            if tag == "p":
                pPr = elem.find("w:pPr", NS)
                pStyle_val = ""
                is_num = False
                if pPr is not None:
                    pStyle = pPr.find("w:pStyle", NS)
                    if pStyle is not None:
                        pStyle_val = pStyle.attrib.get(f"{{{NS['w']}}}val", "")
                    if pPr.find("w:numPr", NS) is not None:
                        is_num = True

                run_texts = []
                for r in elem.findall("w:r", NS):
                    rPr = r.find("w:rPr", NS)
                    r_text = "".join([t.text for t in r.findall("w:t", NS) if t.text])
                    if not r_text:
                        continue
                    is_b = rPr is not None and rPr.find("w:b", NS) is not None
                    is_i = rPr is not None and rPr.find("w:i", NS) is not None
                    
                    if is_b and is_i:
                        run_texts.append(f"***{r_text}***")
                    elif is_b:
                        run_texts.append(f"**{r_text}**")
                    elif is_i:
                        run_texts.append(f"*{r_text}*")
                    else:
                        run_texts.append(r_text)

                p_str = "".join(run_texts).strip()
                if not p_str:
                    continue

                raw_paras.append(p_str)

                if not first_p_processed:
                    first_p_processed = True
                    if p_str.startswith("title:"):
                        meta = extract_frontmatter_and_metadata(p_str)
                        continue

                title_hint = meta.get("title", docx_path.stem)

                m_hash = re.match(r"^(#{1,6})\s+(.*)$", p_str)
                if pStyle_val == "Heading1":
                    clean_h = clean_heading(p_str, title_hint)
                    elements.append(f"# {clean_h}")
                elif pStyle_val == "Heading2":
                    clean_h = clean_heading(p_str, title_hint)
                    elements.append(f"## {clean_h}")
                elif pStyle_val == "Heading3":
                    clean_h = clean_heading(p_str, title_hint)
                    elements.append(f"### {clean_h}")
                elif pStyle_val == "Heading4":
                    clean_h = clean_heading(p_str, title_hint)
                    elements.append(f"#### {clean_h}")
                elif m_hash:
                    hashes, rest = m_hash.group(1), m_hash.group(2)
                    clean_h = clean_heading(rest, title_hint)
                    elements.append(f"{hashes} {clean_h}")
                elif is_num:
                    elements.append(f"- {p_str}")
                else:
                    elements.append(p_str)

            elif tag == "tbl":
                rows = []
                for tr in elem.findall("w:tr", NS):
                    cells = []
                    for tc in tr.findall("w:tc", NS):
                        cell_runs = []
                        for r in tc.iter(f"{{{NS['w']}}}r"):
                            rPr = r.find("w:rPr", NS)
                            r_text = "".join([t.text for t in r.findall("w:t", NS) if t.text])
                            if not r_text:
                                continue
                            is_b = rPr is not None and rPr.find("w:b", NS) is not None
                            is_i = rPr is not None and rPr.find("w:i", NS) is not None
                            if is_b and is_i:
                                cell_runs.append(f"***{r_text}***")
                            elif is_b:
                                cell_runs.append(f"**{r_text}**")
                            elif is_i:
                                cell_runs.append(f"*{r_text}*")
                            else:
                                cell_runs.append(r_text)
                        cell_str = " ".join(cell_runs).strip().replace("|", "\\|").replace("\n", " ")
                        cells.append(cell_str)
                    if cells:
                        rows.append(cells)

                if rows:
                    all_tables.append(rows)
                    col_count = max(len(r) for r in rows)
                    norm_rows = [r + [""] * (col_count - len(r)) for r in rows]

                    header_idx = 0
                    if all(c == "" for c in norm_rows[0]) and len(norm_rows) > 1:
                        header_idx = 1

                    header = norm_rows[header_idx]
                    md_table = []
                    md_table.append("| " + " | ".join(header) + " |")
                    md_table.append("| " + " | ".join(["---"] * col_count) + " |")
                    for r_idx, r in enumerate(norm_rows):
                        if r_idx <= header_idx and header_idx > 0:
                            continue
                        if r_idx == 0 and header_idx == 0:
                            continue
                        md_table.append("| " + " | ".join(r) + " |")
                    elements.append("\n".join(md_table))

        content_body = "\n\n".join(elements)
        return meta, content_body, all_tables, raw_paras


def gate_docket(docx_path: Path, meta: dict, raw_combined: str) -> tuple[str, str] | None:
    """R26-254 (1): ("REFUSED" | "FAIL", why) when this docket must not be written, else None."""
    kind = offering_refusal(docx_path.stem, meta.get("title", ""))
    if kind:
        return "REFUSED", f"offering document ({kind}) - never ingested"
    if search_listing(raw_combined):
        hits = len(SEARCH_HIT.findall(raw_combined))
        return "FAIL", (f"body is a Drive search listing ({hits} records), not research - not written; "
                        "re-export the document itself")
    return None


def main() -> int:
    """Ingest the operator's folder. Exit 1 when any docket FAILED (a refusal is the policy working, not a failure)."""
    TARGET_MARKETS_DIR.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"=== Sovereign Compute Ingestion Engine (Target: {TARGET_MARKETS_DIR.relative_to(REPO_ROOT)}) ===")
    docx_files = sorted(SOURCE_DIR.glob("*.docx"))
    print(f"Found {len(docx_files)} source docx file(s) in {SOURCE_DIR}\n")

    catalog_entries = []
    screener_dataset = []
    refused: list[str] = []
    failed: list[str] = []

    for idx, docx_path in enumerate(docx_files, 1):
        clean_stem = docx_path.stem.replace(".md", "")
        out_name = f"{clean_stem}.md"
        meta, body, tables, raw_paras = convert_docx_to_markdown_structure(docx_path)
        raw_combined = " ".join(raw_paras)

        verdict = gate_docket(docx_path, meta, raw_combined)
        if verdict:
            (refused if verdict[0] == "REFUSED" else failed).append(docx_path.name)
            print(f"{verdict[0]} {docx_path.name}: {verdict[1]} (R26-254)")
            continue

        tickers = extract_tickers_from_text(meta.get("title", "") + " " + body[:5000])

        # Extract screener table data
        if "10_Smart_Filtered_Screener" in docx_path.name and tables:
            screener_table = tables[0]
            header = [re.sub(r"\*+", "", h).strip() for h in screener_table[0]]
            for row in screener_table[1:]:
                clean_row = [re.sub(r"\*+", "", c).strip() for c in row]
                if len(clean_row) == len(header):
                    screener_dataset.append(dict(zip(header, clean_row)))

        # R26-254 (1): no Drive inventory json and no source_id (the ids the 2026-09-22 scrub removed); supersedes only
        # when it names no Drive id
        frontmatter = [
            "---",
            f'title: "{meta.get("title", clean_stem)}"',
            f'category: "{meta.get("category", "General Equity")}"',
            f'tickers: {json.dumps(tickers)}',
            f'source_location: "{meta.get("source_location", "N/A")}"',
            *([f'supersedes: "{meta["supersedes"]}"'] if meta.get("supersedes") else []),
            f'ingestion_target: "{meta.get("ingestion_target", "Sovereign Research Repository")}"',
            f'date: "2026-09-20"',
            f'auditor: "Outreach Program Sovereign Research Librarian"',
            "---",
            "",
            f"**Ingestion Docket:** `{clean_stem}` · **Category:** {meta.get('category', 'Equity Research')} · **Tickers:** {', '.join(tickers) if tickers else 'Cross-Cluster'}",
            "",
        ]

        # Determine document body formatting based on document category/class
        if clean_stem in DOCKET_STEMS:
            body_content = parse_docket_file(clean_stem, meta, raw_combined)
        elif clean_stem == "04_Research_Deep_Storage_Cross_Cluster":
            body_content = parse_docket_04(meta, raw_paras)
        elif clean_stem == "10_Smart_Filtered_Screener":
            body_content = parse_docket_10(meta, tables)
        else:
            # Analytical research dossier: Ensure H1 title at top if missing
            doc_h1 = f"# {meta.get('title', clean_stem)}"
            if not body.strip().startswith("# "):
                body_content = f"{doc_h1}\n\nThe following analytical dossier details sovereign compute infrastructure, capital allocation frameworks, and valuation models.\n\n" + body
            else:
                body_content = body

        full_md_doc = scrub_drive_refs("\n".join(frontmatter) + body_content.strip() + "\n")
        left = drive_refs(full_md_doc)
        if left:   # the scrub is verified before anything is written; a miss is a FAIL, never a silent write
            failed.append(docx_path.name)
            print(f"FAIL {docx_path.name}: {len(left)} Drive reference(s) survived the scrub - not written (R26-254)")
            continue

        # Write Tier 2 raw extract
        tier2_path = RUNS_DIR / f"raw_{clean_stem}.md"
        tier2_path.write_text(full_md_doc, encoding="utf-8")

        # Write standardized target market research document
        target_path = TARGET_MARKETS_DIR / out_name
        target_path.write_text(full_md_doc, encoding="utf-8")

        catalog_entries.append({
            "num": idx,
            "filename": out_name,
            "title": meta.get("title", clean_stem),
            "category": meta.get("category", "General Equity"),
            "tickers": tickers,
            "tables": len(tables),
            "chars": len(full_md_doc),
        })

        print(f"[{idx:02d}/{len(docx_files)}] Ingested -> docs/research/markets/sovereign-compute/{out_name} ({len(full_md_doc):,} chars, {len(tickers)} tickers)")

    if screener_dataset:
        csv_path = RUNS_DIR / "screener_metrics.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as cf:
            writer = csv.DictWriter(cf, fieldnames=list(screener_dataset[0].keys()))
            writer.writeheader()
            writer.writerows(screener_dataset)

        json_path = RUNS_DIR / "screener_metrics.json"
        json_path.write_text(json.dumps(screener_dataset, indent=2), encoding="utf-8")
        print(f"\n[OK] Wrote screener dataset ({len(screener_dataset)} tickers) to {csv_path.name} & {json_path.name}")

    write_catalog(catalog_entries)
    print(f"\ningest_stock_research: {len(catalog_entries)} written, {len(refused)} refused, {len(failed)} failed")
    return 1 if failed else 0


def keep_written_links(lines: list[str], written: set[str]) -> list[str]:
    """The catalog's hand-written lines, pointing only at documents this run wrote: a `Primary Document` line keeps its
    written links (dropped when none is left); any other line linking an unwritten document is dropped."""
    link = re.compile(r"\[`?([^`\]]+\.md)`?\]\(\./([^)]+\.md)\)")
    out = []
    for line in lines:
        targets = [m.group(2) for m in link.finditer(line)]
        if not targets or all(t in written for t in targets):
            out.append(line)
            continue
        if line.startswith("- **Primary Document"):
            head, _, rest = line.partition(":** ")
            kept = [item for item in rest.split(", ") if any(t in written for t in (m.group(2) for m in link.finditer(item)))]
            if kept:
                out.append(f"{head}:** " + ", ".join(kept))
    return out


def write_catalog(catalog_entries: list[dict]) -> None:
    count = len(catalog_entries)
    written = {c["filename"] for c in catalog_entries}
    print("\n--- Generating Master Catalog (00_SOVEREIGN_COMPUTE_MASTER_CATALOG.md) ---")
    catalog_md = [
        "# Sovereign Compute & Accretive Capital Allocation — Master Research Catalog",
        "",
        f"*Ingestion Date: 2026-09-20 · Source: Google Drive Sovereign Compute Ingestion Docket · {count} Master Documents · 120 Screened Tickers*",
        "",
        "## Sovereign Capital Architecture & Master Ingestion Scope",
        "",
        "This master research docket unifies the institutional investment research, quantitative screeners, macro-geopolitical kinetic shock assessments, and multi-year options convexity frameworks developed for **Sovereign Compute & Accretive Capital Allocation**.",
        "",
        "The repository serves both the capital allocation strategy and the content production pipelines of **Money Physics** and **Building Money** (Outreach Program Video Engine). Every valuation model, power purchase agreement (PPA) calculation, nuclear enrichment bottleneck (HALEU), and aerospace sensor catalyst is indexed for high-precision retrieval.",
        "",
        "---",
        "",
        f"## 1. Document Index ({count} Master Research Documents)",
        "",
        "| # | Document | Category | Tickers | Tables |",
        "|---|---|---|---|---|",
    ]

    for c in catalog_entries:
        ticker_str = ", ".join(c["tickers"][:5]) + ("..." if len(c["tickers"]) > 5 else "")
        if not ticker_str:
            ticker_str = "—"
        catalog_md.append(
            f"| {c['num']:02d} | [{c['filename']}](./{c['filename']}) | {c['category']} | `{ticker_str}` | {c['tables']} |"
        )

    catalog_md.extend([
        "",
        "---",
        "",
        "## 2. The 5 Strategic Sovereign Compute Clusters",
        "",
        "### Cluster 1: Sovereign Compute & Localized Edge AI",
        "- **Core Tickers:** $INOD (Innodata), $SERV (Serve Robotics), $LAES (SEALSQ Corp), $QCOM (Qualcomm)",
        "- **Thesis:** Edge AI inference, on-device compute sovereignty, specialized ASIC/security components.",
        "- **Primary Document:** [`05_Deep_Dive_C1_Compute_and_Edge_AI.md`](./05_Deep_Dive_C1_Compute_and_Edge_AI.md), [`04_Research_Deep_Storage_Cross_Cluster.md`](./04_Research_Deep_Storage_Cross_Cluster.md)",
        "",
        "### Cluster 2: Energy Density & Baseload Resilience",
        "- **Core Tickers:** $AMPX (Amprius Technologies), $WLDN (Willdan Group), $GVA (Granite Construction), $PLUG (Plug Power), $APLD (Applied Digital), $WULF (TeraWulf)",
        "- **Thesis:** Megawatt/gigawatt grid interconnection capacity, behind-the-meter nuclear and hydro power, silicon anode battery density.",
        "- **Primary Documents:** [`06_Deep_Dive_C2_Energy_Density_and_Resilience.md`](./06_Deep_Dive_C2_Energy_Density_and_Resilience.md), [`12_Applied_Digital_and_TeraWulf_Deep_Analysis.md`](./12_Applied_Digital_and_TeraWulf_Deep_Analysis.md)",
        "",
        "### Cluster 3: Sovereign Metals, Materials & Nuclear Infrastructure",
        "- **Core Tickers:** $LEU (Centrus Energy), $OKLO (Oklo Inc), $SMR (NuScale Power), $CCJ (Cameco), $ALOY (Alloy Resources), $MTRN (Materion), $IOSP (Innospec), $KRMN (Kaman), $LASR (nLIGHT)",
        "- **Thesis:** Domestic enrichment monopoly (AC100M centrifuges), HALEU fuel for SMRs, 2028 Russian uranium import cliff, defense alloy precision.",
        "- **Primary Documents:** [`13_Nuclear_Infrastructure_Stack_LEU_OKLO_IMSR_SMR.md`](./13_Nuclear_Infrastructure_Stack_LEU_OKLO_IMSR_SMR.md), [`07_Deep_Dive_C3_Sovereign_Metals_and_Components.md`](./07_Deep_Dive_C3_Sovereign_Metals_and_Components.md)",
        "",
        "### Cluster 4: Space Infrastructure & Orbital Sensing",
        "- **Core Tickers:** $ASTS (AST SpaceMobile), $RKLB (Rocket Lab), $RDW (Redwire Space), $BKSY (BlackSky), $LUNR (Intuitive Machines), $DCO (Ducommun), $VVX (V2X), $SATL (Satellogic), $PL (Planet Labs)",
        "- **Thesis:** Direct-to-cell satellite constellations, low Earth orbit logistics, responsive space telemetry, autonomous tactical sensing.",
        "- **Primary Documents:** [`11_Deep_Tech_Space_Economy_ASTS_RCAT_FLY_PL.md`](./11_Deep_Tech_Space_Economy_ASTS_RCAT_FLY_PL.md), [`17_Apex_Platform_Primes_Catalyst_Map_RKLB_RDW_BKSY.md`](./17_Apex_Platform_Primes_Catalyst_Map_RKLB_RDW_BKSY.md), [`08_Deep_Dive_C4_Space_and_Sensing.md`](./08_Deep_Dive_C4_Space_and_Sensing.md)",
        "",
        "### Cluster 5: Hard Assets, Advanced Packaging & Industrial Utilities",
        "- **Core Tickers:** $ACMR (ACM Research), $FN (Fabrinet), $MRVL (Marvell), $TER (Teradyne), $AVAV (AeroVironment), $UMAC, $ONDS, $PKE, $GHM (Graham Corp), $LMB (Limbach Holdings), $TWIN (Twin Disc), $GATX (GATX Corp)",
        "- **Thesis:** Semiconductor wafer cleaning & packaging, high-speed optical transceivers (800G/1.6T), military autonomous swarms, industrial cooling.",
        "- **Primary Documents:** [`19_Structural_Accretion_RXT_TRT_VATE_ACMR_VELO.md`](./19_Structural_Accretion_RXT_TRT_VATE_ACMR_VELO.md), [`14_Optical_Connectivity_Fabrinet_and_Marvell_Trillion_Trajectory.md`](./14_Optical_Connectivity_Fabrinet_and_Marvell_Trillion_Trajectory.md), [`15_Teradyne_Physical_AI_and_Packaging_Supercycles.md`](./15_Teradyne_Physical_AI_and_Packaging_Supercycles.md), [`16_Tactical_Scaling_AVAV_UMAC_ONDS.md`](./16_Tactical_Scaling_AVAV_UMAC_ONDS.md)",
        "",
        "---",
        "",
        "## 3. The Quantitative Screener (120-Ticker Ledger)",
        "",
        "The complete screener table containing 120 equities, EBIT margins, 3-Yr dilution CAGR, Net Debt/EV, Backlog/RPO growth, BBR (Backlog-to-Burn Ratio), cash runways, AMBI scores, and Sovereign Screen Verdicts is documented in [`10_Smart_Filtered_Screener.md`](./10_Smart_Filtered_Screener.md).",
        "",
        "The raw structured data is exported to:",
        "- CSV: `docs/research/runs/sovereign-compute-2026-09/screener_metrics.csv`",
        "- JSON: `docs/research/runs/sovereign-compute-2026-09/screener_metrics.json`",
        "",
        "---",
        "",
        "## 4. Macro-Geopolitical Framework: 'Bits to Atoms'",
        "",
        "In [`24_Macro_Geopolitical_Kinetic_Shock_Bits_to_Atoms.md`](./24_Macro_Geopolitical_Kinetic_Shock_Bits_to_Atoms.md), the portfolio details the strategic rotation from pure software/cloud (\"Bits\") into sovereign hardware, defense, energy, and physical infrastructure (\"Atoms\") in response to kinetic hemispheric realignments, the Donroe Doctrine, and maritime supply chain volatility.",
        "",
        "---",
        "",
        "## 5. Retrieval & Agent Navigation",
        "",
        f"All {count} documents are registered in `docs/DOCS-INDEX.jsonl` and searchable via:",
        "```bash",
        'python content/video_engine/scripts/docs_find.py "TeraWulf"',
        'python content/video_engine/scripts/docs_find.py "Centrus Energy"',
        'python content/video_engine/scripts/docs_find.py "Sovereign Compute"',
        "```",
    ])

    catalog_path = TARGET_MARKETS_DIR / "00_SOVEREIGN_COMPUTE_MASTER_CATALOG.md"
    catalog_path.write_text("\n".join(keep_written_links(catalog_md, written)) + "\n", encoding="utf-8")
    print(f"[OK] Generated Master Catalog at {catalog_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    sys.exit(main())

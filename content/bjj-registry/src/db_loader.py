"""db_loader.py — adapter that maps the registry dataset -> LocationFacts.

This does NOT invent a schema. It reads a registry export you provide and
maps it into the fact layer the generator consumes. Swap the source by
passing a different loader; the rest of the pipeline is unchanged.

Supported sources (pick one, then point `--source` at it):
  1. CSV files (one per table)  — easiest if you export from a DB/admin panel
  2. SQLite file               — if the registry is a local .db
  3. Postgres (via psycopg)    — if the live registry is Supabase/Postgres

Expected registry table shape (column names; aliases tolerated):
  academies: id, name, city, state, county, lineage, affiliation, note
  (counts and groupings are DERIVED from academies — never fabricated)

If your columns differ, edit the COLUMN ALIASES map below or add a small
per-source mapping. Nothing here asserts a count that isn't in the data.
"""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from location_facts import AcademyRef, LocationFacts


# Tolerated column-name variants -> canonical
ALIASES = {
    "name": ["name", "school_name", "academy_name", "title"],
    "city": ["city", "town"],
    "state": ["state", "st", "state_code"],
    "county": ["county", "parish"],
    "lineage": ["lineage", "style", "team_lineage"],
    "affiliation": ["affiliation", "brand", "association"],
    "note": ["note", "description", "blurb"],
}


def _canon(headers: list[str]) -> dict[str, str]:
    """Map canonical key -> actual header found in the file."""
    lower = {h.strip().lower(): h for h in headers}
    mapping = {}
    for canon, variants in ALIASES.items():
        for v in variants:
            if v in lower:
                mapping[canon] = lower[v]
                break
    return mapping


def _slug(text: str) -> str:
    return text.strip().lower().replace(" ", "-")


def _region_token(text: str) -> str:
    """Mirror the registry's region_token(): strip non-alphanumerics.

    The aggregates table keys counties/cities by token (e.g. 'traviscounty'),
    but the directory spine stores human text ('Travis County'). Normalize
    before matching so the two layers join correctly.
    """
    import re
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def _state_name(code: str, names: dict[str, str]) -> Optional[str]:
    return names.get(code.upper())


def load_from_csv(academies_csv: str | Path, state_names: Optional[dict[str, str]] = None) -> list[LocationFacts]:
    """Build national/state/county/city LocationFacts from an academies CSV."""
    state_names = state_names or {}
    rows: list[dict] = []
    with open(academies_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        canon = _canon(headers)
        required = {"name", "state"}
        missing = required - set(canon)
        if missing:
            raise ValueError(f"CSV missing required columns (need name, state): {missing}")
        for r in reader:
            rows.append({k: (r.get(canon[k]) or "").strip() for k in canon})

    # Group
    states: dict[str, list[dict]] = {}
    for r in rows:
        states.setdefault(r["state"], []).append(r)

    facts: list[LocationFacts] = []

    # National
    facts.append(LocationFacts(
        tier="national", name="USA", slug="national",
        academy_count=len(rows), academy_count_source="registry_export",
        academy_count_verified=True,
        top_cities=_top_cities(rows, 8),
        lineages_present=_lineages(rows),
        sources={"academy_count": "academies_csv"},
    ))

    for st, st_rows in sorted(states.items()):
        st_slug = _slug(st) if len(st) > 2 else st.lower()
        st_name = _state_name(st, state_names) or st
        # counties within state
        counties: dict[str, list[dict]] = {}
        for r in st_rows:
            c = r.get("county") or "Unknown"
            counties.setdefault(c, []).append(r)

        # State
        facts.append(LocationFacts(
            tier="state", name=st_name, slug=st_slug, state=st, state_name=st_name,
            state_slug=st_slug, parent_slug="national",
            child_slugs=sorted(_slug(c) + "-" + st.lower() for c in counties if c != "Unknown"),
            academy_count=len(st_rows), academy_count_source="registry_export",
            academy_count_verified=True,
            top_cities=_top_cities(st_rows, 10),
            lineages_present=_lineages(st_rows),
            top_academies=_academy_refs(st_rows[:3]),
            sources={"academy_count": "academies_csv"},
        ))

        for c, c_rows in sorted(counties.items()):
            if c == "Unknown":
                continue
            c_slug = _slug(c) + "-" + st.lower()
            facts.append(LocationFacts(
                tier="county", name=c, slug=c_slug, state=st, state_name=st_name,
                state_slug=st_slug, county=c, parent_slug=st_slug,
                child_slugs=sorted(_slug(r["city"]) + "-" + st.lower() for r in c_rows if r.get("city")),
                academy_count=len(c_rows), academy_count_source="registry_export",
                academy_count_verified=True,
                top_cities=_top_cities(c_rows, 10),
                lineages_present=_lineages(c_rows),
                top_academies=_academy_refs(c_rows[:3]),
                sources={"academy_count": "academies_csv"},
            ))
            for city, city_rows in _group_cities(c_rows).items():
                facts.append(LocationFacts(
                    tier="city", name=city, slug=_slug(city) + "-" + st.lower(),
                    state=st, state_name=st_name, state_slug=st_slug,
                    county=c, city=city, parent_slug=c_slug,
                    academy_count=len(city_rows), academy_count_source="registry_export",
                    academy_count_verified=True,
                    lineages_present=_lineages(city_rows),
                    top_academies=_academy_refs(city_rows[:4]),
                    sources={"academy_count": "academies_csv"},
                ))
    return facts


def _group_cities(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for r in rows:
        if r.get("city"):
            out.setdefault(r["city"], []).append(r)
    return out


def _top_cities(rows: list[dict], n: int) -> list[str]:
    from collections import Counter
    c = Counter(r["city"] for r in rows if r.get("city"))
    return [city for city, _ in c.most_common(n)]


def _lineages(rows: list[dict]) -> list[str]:
    seen = []
    for r in rows:
        lg = (r.get("lineage") or "").strip()
        if lg and lg not in seen:
            seen.append(lg)
    return seen


def _academy_refs(rows: list[dict]) -> list[AcademyRef]:
    out = []
    for r in rows:
        if not r.get("name"):
            continue
        out.append(AcademyRef(
            name=r["name"], city=r.get("city") or None, state=r.get("state") or None,
            lineage=r.get("lineage") or None, note=r.get("note") or None,
            source="registry_export", verified=True,
        ))
    return out


# --- SQLite / Postgres hooks (structure preserved; wire creds when available) ---

def load_from_sqlite(db_path: str | Path, state_names: Optional[dict[str, str]] = None) -> list[LocationFacts]:
    """Read an `academies` table from a SQLite file and reuse the CSV mapper."""
    db_path = Path(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    table = "academies" if "academies" in tables else (tables[0] if tables else None)
    if not table:
        raise ValueError("No table found in SQLite DB")
    cur.execute(f"SELECT * FROM {table}")
    tmp = Path(db_path).with_suffix(".csv")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        cols = [d[0] for d in cur.description]
        writer.writerow(cols)
        for rec in cur.fetchall():
            writer.writerow([rec[c] for c in cols])
    conn.close()
    facts = load_from_csv(tmp, state_names)
    tmp.unlink(missing_ok=True)
    return facts


# Postgres: provide a DSN; requires psycopg (optional dependency).
# Reads the DIRECTORY spine (academies) AND the INSIGHT layer
# (registry_region_score_aggregates_v1) and merges both into LocationFacts.
def load_from_postgres(dsn: str, state_names: Optional[dict[str, str]] = None) -> list[LocationFacts]:
    try:
        import psycopg
    except ImportError:
        raise RuntimeError("psycopg not installed; `pip install psycopg` to use Postgres loader")
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        # 1) Directory spine — academy rows
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name IN ('academies','registry_gym_directory_card_current') "
            "ORDER BY table_name='academies' DESC LIMIT 1"
        )
        # Prefer a real academies table; fall back to the directory card current view
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name IN ('academies','registry_gym_directory_card_current')"
        )
        avail = [r[0] for r in cur.fetchall()]
        spine_table = "academies" if "academies" in avail else (avail[0] if avail else None)
        if not spine_table:
            raise ValueError("No academy/directory table found in Postgres DB")
        cur.execute(f"SELECT * FROM {spine_table}")
        tmp = Path.home() / ".cache" / "registry_export.csv"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            cols = [d[0] for d in cur.description]
            writer.writerow(cols)
            for rec in cur.fetchall():
                writer.writerow(list(rec))
        facts = load_from_csv(tmp, state_names)
        tmp.unlink(missing_ok=True)

        # 2) Insight layer — region score aggregates (the market-insight signal)
        try:
            cur.execute(
                "SELECT region, region_type, state_code, county_token, city_token, "
                "avg_registry_score, median_registry_score, top_5_avg_registry_score, "
                "pct_registry_score_70_plus, pct_registry_score_85_plus, registry_score_sample_size "
                "FROM registry_internal.registry_region_score_aggregates_v1"
            )
            rows = cur.fetchall()
        except Exception:
            # Insight table not reachable (permissions / missing) — degrade gracefully
            rows = []
        if rows:
            _apply_insights(facts, rows)
    return facts


def _apply_insights(facts: list[LocationFacts], agg_rows: list) -> None:
    """Merge region score aggregates into the matching LocationFacts by scope."""
    # Build lookup: (region_type, state, county, city) -> metrics
    by_key: dict[tuple, dict] = {}
    national_row = None
    for r in agg_rows:
        (region, rtype, state, county, city, avg, median, top5,
         pct70, pct85, n) = (list(r) + [None] * 11)[:11]
        metrics = {
            "avg_registry_score": avg, "median_registry_score": median,
            "top_5_avg_registry_score": top5, "pct_70_plus": pct70,
            "pct_85_plus": pct85, "sample_size": n,
        }
        if rtype == "national":
            national_row = metrics
            continue
        key = (rtype, (state or "").upper(), (county or "").lower(), (city or "").lower())
        by_key[key] = metrics

    def _score_for(tier, state, county, city):
        # Build candidate keys from most to least specific (normalize tokens like the DB does)
        st = (state or "").upper()
        co = _region_token(county) if county else ""
        ci = _region_token(city) if city else ""
        cands = []
        if tier == "city":
            cands = [
                ("city", st, "", ci),
                ("state", st, "", ""),
                ("national", "", "", ""),
            ]
        elif tier == "county":
            cands = [
                ("county", st, co, ""),
                ("state", st, "", ""),
                ("national", "", "", ""),
            ]
        elif tier == "state":
            cands = [
                ("state", st, "", ""),
                ("national", "", "", ""),
            ]
        else:
            # national tier -> its own aggregate row
            if national_row:
                out = {k: v for k, v in national_row.items() if v is not None}
                out["national_avg"] = national_row.get("avg_registry_score")
                out["national_pct70"] = national_row.get("pct_70_plus")
            return out or None
        out = {}
        for rtype, cst, cco, cci in cands:
            m = by_key.get((rtype, cst, cco, cci))
            if not m:
                continue
            if rtype == "national":
                out.setdefault("national_avg", m.get("avg_registry_score"))
                out.setdefault("national_pct70", m.get("pct_70_plus"))
            elif rtype == "state" and tier in ("city", "county"):
                out.setdefault("state_avg", m.get("avg_registry_score"))
                # Most-specific region metrics become the primary block; only fill if absent
                for k, v in m.items():
                    if v is not None:
                        out.setdefault(k, v)
            else:
                # city/county primary scope — land its metrics as the canonical block
                for k, v in m.items():
                    if v is not None:
                        out.setdefault(k, v)
        # Guarantee a usable baseline even if the scope had no national row yet
        if national_row and "national_avg" not in out:
            out["national_avg"] = national_row.get("avg_registry_score")
            out["national_pct70"] = national_row.get("pct_70_plus")
        return out or None

    for f in facts:
        sc = _score_for(f.tier, f.state, f.county, f.city)
        if sc:
            f.insights = sc
            f.insights_source = "registry_region_score_aggregates_v1"
            f.insights_verified = True

# BJJ Registry — Programmatic SEO Article System

Generate unique, evidence-backed BJJ articles at **national / state / county / city** tiers
from a single deterministic fact layer. Built for the National BJJ Registry's network of blogs.

## Why this exists

Programmatic SEO scales content, but naive templating triggers Google's thin/duplicate-content
filters (see `RESEARCH_BRIEF.md`). This system avoids that by:

1. **Deterministic facts first.** All real data lives in `LocationFacts` objects with provenance.
2. **Distinct angle per tier.** National/state/county/city pages have different section sets, so
   no two pages read like mail-merge clones.
3. **Internal-link graph.** Every page links up (breadcrumb) and down (children) — a coherent hub,
   not orphan pages (see `SITEMAP_AND_LINKING.md`).
4. **Structured data.** Every page emits `Article` + `BreadcrumbList` JSON-LD.

## Layout

```
content/bjj-registry/
├── RESEARCH_BRIEF.md          # competitive + keyword research, sourced
├── SITEMAP_AND_LINKING.md     # URL taxonomy + link graph + sitemap spec
├── README.md                  # this file
├── src/
│   ├── location_facts.py      # fact-layer dataclasses (LocationFacts, AcademyRef)
│   ├── article_template.py    # deterministic -> generative builder (tier sections, FAQ, JSON-LD)
│   ├── sample_facts.py        # ⚠️ ILLUSTRATIVE seed data — replace w/ registry DB
│   └── generate.py            # CLI generator
└── output/                    # generated articles (gitignored until verified)
    └── <slug>/
        ├── index.md
        ├── meta.json
        └── article.jsonld
```

## Quick start

```bash
cd "C:/Users/Snipe/Downloads/Outreach Program/content/bjj-registry/src"
python generate.py                      # all sample tiers
python generate.py --tier city          # only city pages
python generate.py --slug austin-tx     # a single page
```

Output goes to `../output/<slug>/`.

## Wiring real data (DB adapter)

The generator reads facts from a source you point at — nothing is hardcoded.
Use `--source` to switch from the sample data to your real registry export:

```bash
# From a CSV export (columns: name, city, state, county, lineage, affiliation, note)
python generate.py --source /path/to/academies.csv

# With a state-code -> full-name map (JSON: {"TX":"Texas",...})
python generate.py --source academies.csv --state-names state_names.json

# From a SQLite file
python generate.py --source registry.db

# From a live Postgres/Supabase DB (needs `pip install psycopg`)
python generate.py --source "postgres://user@host:5432/registry"
```

`src/db_loader.py` maps the export into `LocationFacts`:
- **Counts are DERIVED** from the academy rows — never fabricated.
- Column aliases are tolerated (e.g. `school_name`→`name`, `st`→`state`).
- If your table columns differ, edit the `ALIASES` map in `db_loader.py`.

## Where the content comes from (directory spine + facts layer)

Two registry sources feed the pages — this is the key architectural choice:

1. **Directory spine** (`academies` or `registry_gym_directory_card_current`) → names, locations,
   lineages, and **academy counts**. This is the "where to train" content.
2. **Insight layer** (`registry_internal.registry_region_score_aggregates_v1`) → real, derived
   quality signals per region: `avg_registry_score`, `median_registry_score`, `top_5_avg`,
   `pct_70_plus`, `pct_85_plus`, `sample_size`. These drive the **"Market Insights"** section —
   unique, defensible market differentiation no competitor pSEO site has.

The Postgres loader joins both by scope token (national / state / county / city), inheriting the
parent-region and national baselines so each page can say *"Austin averages 71.4 vs 68.0 statewide
vs 65.0 nationally."* Insights are verified only when the aggregate row is present; pages with
`sample_size < 3` omit the section rather than make a thin claim.

## Automated pipeline (generate → import)

`run_pipeline.py` wires fact layer → generator → `blog_posts.jsonl`, then hands off to the
registry's own importer:

```bash
# 1. Generate from the live registry DB (directory spine + insight aggregates):
cd "C:/Users/Snipe/Downloads/Outreach Program/content/bjj-registry"
python run_pipeline.py --source "postgres://user@host:5432/registry" \
    --state-names state_names.json --out ./output

# 2. Hand off to the registry importer (dry-run by default; add --publish to write):
python run_pipeline.py --source "..." --import-to \
    "../../WA JiuJitsu Registry-20260608T183757Z-3-001/scripts/import-programmatic-blog-posts.mjs"
```

The wrapper never writes to the registry unless `--import-to` AND `--publish` are given.
Run it on a schedule (cron / CI) so content regenerates as registry scores refresh.

> **Import gate (registry rule):** generated articles are *source content*. A human must run
> `--publish` after eyeballing the output. The importer cascade (`registry_blog_distribution_current`)
> then distributes each article to the correct national/state/county/city blog surfaces.

## Flash-LLM render step (optional, feed-step)

The deterministic template is the default and the prose floor. To add natural voice at scale,
a flash model renders only the per-tier section *bodies* from a compact fact bundle — it never
authors facts. Hard numbers stay OUT of published prose (operator preference: scores drift, and
printed stats go stale). The bundle carries `signals` as qualitative bands; the model is forbidden
from printing raw scores, and `llm_guard.py` rejects any output that leaks them.

```bash
# Template (default, free, deterministic)
python generate.py --writer template
python run_pipeline.py --writer template --out ./output

# Flash LLM prose, guarded + auto-fallback to template on any failure
export LLM_API_KEY=sk-or-...        # OpenRouter or OpenAI key
export LLM_MODEL=tencent/hy3:free   # free now; swap to deepseek/deepseek-v4-flash:free later
python run_pipeline.py --writer llm --only-priority --out ./output
```

- **Model-agnostic, OpenRouter-first.** Swap models with env vars only — `LLM_MODEL`,
  `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_BASE_URL`. Defaults: `tencent/hy3:free` (free here +
  OpenRouter); future `deepseek/deepseek-v4-flash:free` is a one-line change.
- `--only-priority` (run_pipeline) uses the LLM on `state`/`city` tiers where voice moves the
  needle; bulk `national`/`county` pages stay on the free template. Keeps cost ~$0 where it doesn't.
- **Guardrail:** `llm_guard.py` blocks raw scores/percentages and unsourced academy names. On
  rejection or any network/key failure, the pipeline falls back to the template — output is never
  blocked by the LLM.
- Feed step = `src/fact_bundle.py` serializes `LocationFacts` → token-light prompt (Gemini-ready).

- The expected table is `academies` with at least `name` + `state`; everything
  else (county, city, lineage, affiliation) is optional and grouped automatically.

### Emitting registry `blog_posts` JSONL (recommended for the real Registry)

The registry already ships a programmatic-blog pipeline: `scripts/import-programmatic-blog-posts.mjs`
imports JSONL into `public.blog_posts`, then cascades to national/state/county/city/market/zip/
neighborhood/gym surfaces through `registry_internal.registry_blog_distribution_current`.

```bash
python generate.py --format jsonl --out ../output   # -> output/blog_posts.jsonl
```

Each row carries `metadata.distribution` with the correct `scope_type`
(`national|state|county|city`) plus `state_code` / `county_token` / `city_token`
(normalized to the importer's `token()` form). Import it from the registry repo root:

```bash
node scripts/import-programmatic-blog-posts.mjs \
  --input=../../Outreach\ Program/content/bjj-registry/output/blog_posts.jsonl \
  --batch-id=bjj-registry-pseo-$(date +%F) --confirm-write --approve --publish --enqueue-refresh
```

> Review rule (PROGRAMMATIC_BLOG_IMPORT.md): generated articles are source content —
> a human must approve/publish before they go live. Run `--confirm-write` only after review.

## Second axis: technique pages (corpus videos + transcripts)

The same engine generates a **technique axis** from your corpus of technique videos
(full transcripts + metadata). This multiplies coverage: 1 technique × N locations =
long-tail "where to learn <technique> in <city>" pages, built by joining
`taught_at` → academy → city (reusing the location spine).

```bash
python generate.py --axis technique --corpus ../corpus --out ../output
python generate.py --axis technique --corpus ../corpus --format jsonl --out ../output
```

- **Fact source = the transcript.** Steps are extracted from the transcript (or taken
  verbatim from `metadata.steps`). The LLM may reword steps but **cannot add/invent**
  them — `llm_guard.guard_technique` checks every rendered step shares tokens with a
  sourced step (provenance), and rejects step-count inflation.
- **HowTo JSON-LD** is emitted on technique pages (rich-result eligible — a real SEO
  leg up over location pages).
- **`taught_at` join** drives a "Where to Train This" section + the `metadata.taught_at`
  field in the JSONL row, enabling the location cross-product.
- Same `--writer llm` / `--only-priority` / guard / fallback behavior as the location axis.

Expected corpus record:
```json
{ "name": "Armbar from Guard", "slug": "armbar-from-guard", "position": "guard",
  "belt": "white", "category": "submission", "transcript": "...",
  "metadata": { "common_errors": [...], "key_terms": [...] },
  "related": [{"name": "...", "slug": "..."}],
  "taught_at": [{"name": "Renzo Gracie Austin", "city": "Austin", "state": "TX", "lineage": "Renzo Gracie"}] }
```

After switching sources: run generator, spot-check one page per tier, verify
internal links resolve, then publish per `SITEMAP_AND_LINKING.md`.

## Tier → angle map

| Tier | Intent | Unique sections |
|---|---|---|
| national | registry overview | What it is, US scene, where it clusters, lineage map, how to use, events |
| state | "{State} BJJ" | scene intro, top cities, notable academies, comps, beginner path |
| county | "{County} BJJ" | training hubs, which cities lead, academies, community/open mats, events |
| city | "{City} BJJ" / first class | academies, gi vs no-gi, first class, kids/adults/trials |

## Guardrails

- **Never fabricate** academy names, counts, lineages, or events. Flag unverified data; the
  generator warns on publish.
- Keep `article_template.py` deterministic — same facts → same output. Add new *sections*, not
  random phrasing, to evolve the template.
- Before scaling to thousands of pages, ensure each location has ≥3 real academies or merge into
  the parent (see SITEMAP_AND_LINKING.md §3).

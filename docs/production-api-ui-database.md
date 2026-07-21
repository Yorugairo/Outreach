# Production API, UI, and database

## Runtime

The control plane is a FastAPI application backed by a migration-managed SQLite database and a file artifact mirror.

- Database source of truth: `SEO_INSIGHTS_DATABASE_PATH`
- Artifact exports: `SEO_INSIGHTS_ARTIFACT_ROOT`
- Authentication: `X-API-Key` checked against `SEO_INSIGHTS_API_KEY`
- UI: same-origin dashboard at `/`
- API schema in development: `/docs`
- Health probe: `/healthz`

## Start locally

```bash
export SEO_INSIGHTS_API_KEY='replace-with-a-long-random-secret'
export SEO_INSIGHTS_ENV='development'
export SEO_INSIGHTS_DATABASE_PATH='artifacts/seo_insight_runs/seo-insights.db'
export SEO_INSIGHTS_ARTIFACT_ROOT='artifacts/seo_insight_runs'
python scripts/serve_insight_api.py --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/`, enter the API key for the current browser session, and connect. The key is stored in `sessionStorage`, never embedded in HTML or persisted to `localStorage`.

## Production requirements

Set:

```bash
SEO_INSIGHTS_ENV=production
SEO_INSIGHTS_API_KEY=<long-random-secret>
SEO_INSIGHTS_FORWARDED_ALLOW_IPS=<trusted-proxy-ip-or-network>
```

Production mode refuses to create the app without an API key and disables interactive API docs. Terminate TLS at a trusted reverse proxy. Keep the API and dashboard on the same origin so no permissive CORS policy is required.

## Paid enrichment approval

DataForSEO credentials alone do not authorize paid calls. Paid search enrichment requires an explicit request-level approval through the API/dashboard. Unapproved runs persist zero estimated paid calls and a skip reason.

## Persistence contract

SQLite uses:

- WAL journal mode
- foreign keys on every repository connection
- 30-second busy timeout
- ordered SQL migrations under `src/repositories/migrations/`
- indexed operational fields plus full JSON payloads
- mirrored JSON/Markdown artifacts for auditability and export

The repository continues to satisfy `InsightRepository`, so a PostgreSQL implementation can replace SQLite without changing pipeline services.

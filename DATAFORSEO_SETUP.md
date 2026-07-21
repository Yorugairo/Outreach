# DataForSEO setup for Outreach Program

## What DataForSEO uses
DataForSEO uses **Basic Authentication** with your API `login` and `password` from:
- `https://app.dataforseo.com/api-access`

The API base is:
- `https://api.dataforseo.com/`

## 1) Add credentials locally
Copy `.env.example` to `.env` and fill in:
- `DATAFORSEO_LOGIN`
- `DATAFORSEO_PASSWORD`

Do **not** commit `.env`.

## 2) First verification
Run from this folder:

```bash
cd '/c/Users/Snipe/Downloads/Outreach Program'
export DATAFORSEO_LOGIN='your_login'
export DATAFORSEO_PASSWORD='your_password'
python scripts/dataforseo_smoke_test.py
```

Expected result: JSON with a success-style `status_code`/`status_message`.

## 3) Recommended initial integration pattern
Use DataForSEO for:
- keyword ideas / clusters
- SERP snapshots by city/region/device
- rank checks
- competitor overlap research
- local intent modeling

Keep raw responses in a staging table or JSON artifact store before normalization.

## 4) Suggested env contract for the pipeline
- `DATAFORSEO_LOGIN`
- `DATAFORSEO_PASSWORD`
- `DATAFORSEO_DEFAULT_LOCATION_CODE`
- `DATAFORSEO_DEFAULT_LANGUAGE_CODE`

## 5) Immediate next build targets
1. wrapper client (`src/dataforseo_client.py` or TS equivalent)
2. location-code lookup helper
3. keyword-research task runner
4. SERP snapshot task runner
5. normalized persistence schema for keyword + SERP evidence

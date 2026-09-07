# Bridge reply shapes — the contract both sides run (P46 T8, 2026-09-07)

A reply shape is what an order asks for and what tier 0 checks at zero tokens (`bridge_handlers.py`, run by the daemon on
landing and by the addressee before replying: `python content/video_engine/scripts/bridge_check.py --shape <shape> --reply
<file>`). The operator, 2026-09-07: the Gemini lane's real jobs are fetching, measuring, watching and triaging; each gets
a shape whose check is a FILE, never a judgement of prose — so a reply that passes on form has done the work, and one that
fails on substance goes to a paid reader instead of a follow-up that would invite invention.

Every reply, whatever the shape, opens with the five-head block (`BRIDGE-PACKET.md` §2): `POSITION`, `PATHS WRITTEN` (one
bare absolute path per line - no links, no backticks, no bullets), `DISAGREEMENTS`, `PREREQUISITES`, `NOT FOUND WHERE I
LOOKED`. The shapes below add what the FILES must be.

| shape | the job | the order names | the reply's files | tier 0 checks (form → substance) |
|---|---|---|---|---|
| `paths-written` | edits at named paths | `marker` (optional) | the paths | each path exists; the marker in each |
| `contract-block` | one block into a source and its copies | `block`, `source`, copies | the files carrying the block | the block verbatim in each |
| `report-landed` | a research report | the area | `docs/research/<area>/*.md` | exists; ≥ 1 proof line `[Metric \| value \| authority \| URL: https://… \| Verified 20..]`; the `## NOT FOUND WHERE I LOOKED` block; the verdict not `[UNVERIFIED]`; the docs layers green |
| `review` | read and answer, write nothing | — | none | the five heads |
| `test-run` | run our command | `command` | none | exit 0 |
| **`fetch`** | **download, do not write**: primary sources saved as files | `fetch_dir` (absolute) | `<fetch_dir>/MANIFEST.json` + the files | the manifest exists and parses; every entry has `url`, `path`, `sha256`, `fetched_at`; every `path` exists; every `sha256` matches the file on disk; ≥ 1 entry |
| **`measure`** | run one of OUR tools on a named input | `verify` (the tool, from the repo root), `outputs` (absolute paths) | the outputs | every output exists; then `verify` exits 0 (substance) |
| **`watch`** | the `/watch` skill on a reference video, into a fixed table | `csv` (absolute), `schema` (the columns, in order), `min_rows` | the CSV | the header equals the schema exactly; rows ≥ `min_rows`; no empty cell in a column the order marks `required` |
| **`intake-triage`** | a research drop's claim table against what we already hold | `report` (the drop, absolute), `area` | `docs/research/<area>/<name>-INTAKE.md` | the skeleton's sections present (below); the claims table's `ours` column filled on every row; the `## Dedupe` section names a path or `new` per item |
| `free` | — | — | — | every reply reaches tier 1 |

## The `fetch` manifest

```json
{ "fetched_at": "2026-09-07T10:00:00-07:00", "order": "<packetId>",
  "entries": [ { "url": "https://…", "path": "C:/…/sources/<file>", "sha256": "<hex>", "bytes": 12345, "fetched_at": "…",
                 "licence": "<what the page says, or unknown>", "note": "<optional>" } ] }
```

Where a page will not fetch, the entry carries `"status": "not-fetched"` and no `path`; it counts toward NOT FOUND, not
toward the entries tier 0 verifies. Nothing is summarised: a fetch order's deliverable is the file, verbatim, and its hash.

## The `watch` table

The order fixes the columns; the reply never renames, reorders or adds one. The CSV's first line is the schema verbatim.
A row the watcher could not judge keeps the row and writes `UNVERIFIED` in the judged column, never a guess and never a
blank. The method line goes in the reply's free text, not in the file.

## The `intake-triage` skeleton

The file every research drop comes with (the operator, 2026-09-07: "I already ask Gemini to dedupe the research, so it is
already doing 90 % of the work"). It is a skeleton the parent fills with judgement; the addressee fills the clerical columns
from `python content/video_engine/scripts/docs_find.py "<term>"` and the registries (`docs/ANIMATION-REGISTRY.md`,
`docs/GATES-REGISTRY.md`, `docs/CRAFT-MAP.md`, `docs/DOCS-MANIFEST.jsonl`).

```markdown
# Intake — <the drop's title> (<date>)

Drop: <absolute path of the report>. Area: <area>. Triaged by: <profile>, <date>.

## Claims

| # | claim (one sentence, the report's words) | source (the report's proof line or `none`) | ours (docs_find hits: `path:line`, or `none: <query>`) | status |
|---|---|---|---|---|
| 1 | … | … | … | held \| new \| contradicts \| unsourced |

## Dedupe

| # | this drop's item | duplicate of (absolute path, or `new`) | note |
|---|---|---|---|

## Figures

| # | figure | tag in the drop (`proof` \| `DERIVED` \| `UNVERIFIED` \| none) | our figure for the same thing (path, or `none`) |
|---|---|---|---|

## NOT FOUND WHERE I LOOKED

- <the docs_find queries run, the registries opened, the roots searched>
```

`status` is the addressee's clerical read: `held` = we hold it (cite where), `new` = nothing found under the queries listed,
`contradicts` = ours says otherwise (cite), `unsourced` = the drop gives no proof. The parent's verdict (backlog, priority
integration, explore, reject, index) is NOT the addressee's to write - the intake doc (`HYPERFRAMES-INTAKE-2026-09-06.md`) is
the parent's and reads this skeleton.

## Applying the shapes globally

Every research profile carries the shapes convention block (`WORK-ORDER-GEMINI-BRIDGE-SHAPES-2026-09-07.md`): an order names
its shape; the reply opens with the five-head block; the addressee runs `bridge_check.py` before replying; a `fetch` order
is files and a manifest, never a summary; a `watch` order is a fixed table; every research drop arrives with the
intake-triage skeleton beside it; a figure without a proof line is `[DERIVED]` or `[UNVERIFIED]`, never bare. The
`video-watcher` profile (`WORK-ORDER-GEMINI-WATCHER-PROFILE-2026-09-07.md`) is the `watch` shape's owner.

# 27 — Durability Classes And The Path Contract

One principle, and everything else follows from it:

> **A file's durability class is readable from its path alone.**

The one-line test: given only a path, you know whether losing the file is a
shrug, a nuisance, or a disaster — and so does every tool.

## The classes

Per project root (`VIDEO_ENGINE_PROJECT_ROOT`):

| Prefix | Class | Loss means | Protection |
| --- | --- | --- | --- |
| `canonical/` | Catalogue-referenced assets | Disaster | Content-addressed store, synced **on promote** |
| `review/` | In-flight deliveries, claim output | Annoying — regenerate or re-deliver | None; deliberately short-lived |
| `runtime/` | Derived, disposable artifacts | Nothing — regenerable on demand | None; allowed to vanish |

Because the class is a path prefix, three unrelated mechanisms each reduce to
a one-line rule: `.gitignore` ignores the class roots, cleanup may delete
`runtime/` wholesale, and backup concerns itself with `canonical/` only.

## The contract module

`content/video_engine/src/services/paths.py` is the **single owner** of class
roots and shared subpath literals (`QUARANTINE_DIR`, `EXPORT_SUBPATH`, …).
Services never build a class-root path by hand; a structural test
(`test_path_contract_structural.py`) sweeps `src/services` and `console` and
fails naming any offender. The rule existed in embryo before the contract —
`composite_preview` refused output outside a `runtime/` directory — and that
check now delegates to `paths.is_runtime_path`.

## Migration

`scripts/migrate_layout.py` moves a legacy tree into the layout. Dry-run by
default; `--execute` runs copy → verify every catalogue sha256 at the
destination → atomically swap the rewritten catalogue → only then delete
originals. At no point does the live catalogue name a missing path. Idempotent
and resume-safe. **Execution is operator-gated**: review the dry-run first.

## The store (Cloudflare R2)

`asset_store.py` keys every object by its catalogue digest: `sha256/<digest>`.
Configuration is environment-only:

```
VIDEO_ENGINE_R2_ENDPOINT     https://<account>.r2.cloudflarestorage.com
VIDEO_ENGINE_R2_BUCKET
VIDEO_ENGINE_R2_ACCESS_KEY_ID
VIDEO_ENGINE_R2_SECRET_ACCESS_KEY
```

**Sync-on-promote:** `commit_confirm` uploads every promoted file (and layer
plane) before `register_assets` writes the catalogue. A failed upload fails
the promotion — "canonical but unprotected" is not a reachable silent state.
Offline work uses the explicit opt-out `VIDEO_ENGINE_ALLOW_UNSYNCED_PROMOTE=1`,
which stamps the entries `"unsynced": true` so the audit can name the debt.

Local bytes are verified against the digest **before** upload (wrong bytes
under a digest key would poison restore) and **after** every fetch (a store's
word is never taken for the bytes).

## The disaster-recovery contract

A bare catalogue plus credentials is sufficient to rebuild every canonical
file:

```bash
python content/video_engine/cli.py store-audit   --catalog <asset-catalog.v1.json>
python content/video_engine/cli.py store-restore --catalog <asset-catalog.v1.json> --project-root <root>
```

`store-audit` walks the catalogue and heads every digest — read-only, exit 1
when anything is missing, `unsynced` debt reported separately. `store-restore`
fetches by digest, verifies bytes, and refuses to overwrite live files without
`--force`.

## Porting the principle

Other products (bjjregistry, tradesinsights) port the **principle** — classes
in the path, one contract module, sync at the moment of promotion — not this
code. The class names may differ; the one-line test may not.

## P17 mapping

The agent generation loop implements against this layout: claim deliveries
are `review/`-class; animatic previews, composed props and pack summaries are
`runtime/`-class; the motion library is catalogue-registered and therefore
`canonical/`-class; watchdog watch-paths resolve through the contract.

# Steel and Paper — wave 5 plan (plates + evidence)

Script D lands at **11,237 characters ≈ 11m 42s**. Everything below is
what has to exist before it can ship.

| | |
|---|---|
| Plates today | 39 → **18.0s each** (ceiling 20, target 12) |
| Plates needed | **58** for the 12s target → **15 new** (4 reused from finance-episodes-wave-1) |
| Evidence today | 15 in `evidence/objects/` |
| Evidence needed | **3 promoted + 2 built** |

---

## 1. Evidence — three documents exist but were never promoted

Built during the system pass, left in scratchpad, **never moved into
`evidence/objects/`.** One of them is the best document in the episode.

| Document | Why it matters |
|---|---|
| `ev-railway-index-v1` | Campbell & Turner index, +106% then −64.1%, peak and trough annotated. **The flagship** — it carries the episode's central historical claim and it is not in the evidence folder. |
| `ev-railway-gdp-tile-v1` | 7% of British GDP stat tile |
| `ev-debt-issuance-v2` | The corrected three-bar: $28B avg → $121B → $130–150B |

Action: move all three into `evidence/objects/`, re-render from
`build_evidence_documents.py` so they carry the current palette and the
value-weighted method line where relevant.

## 2. Evidence — two new documents for the new units

**`ev-ig-credit-weighting`** — debt unit.
Tech's share of the investment-grade index: ~9% (2024) → ~10% (now) →
>12% (projected). Form: three-bar with the projection in de-emphasis, or
a threshold line at the 2024 level. Source: Morgan Stanley IM;
Investing.com/LPL. This is the "money that used to sit in utilities" line
made visible.

**`ev-hbm-wafer-ratio`** — winner unit.
HBM consumes ~3× the wafer capacity per gigabyte of standard DRAM. Form:
**stat tile**, not a chart — it is one number and doc 39 §6 says a single
value is a tile. Pairs with `ev-dram-contract-v1` as the consequence.
Source: Micron executive, via the dossier E1 chain.

## 3. Reuse first — the memory episode and the stamped deck

Operator, 2026-08-29: prior finance-episode assets are reusable. They are,
and they cut this wave from 19 plates to **15**.

**From `finance-episodes-plates-wave-1`** (built for other finance
episodes, style-identical):

| Plate | Covers |
|---|---|
| `world-dram-terrain-v1` | a wafer surface as terrain — replaces the planned `world-wafer-divided` |
| `world-memory-fab-floor-v1` | fab clean room — replaces the planned `world-fab-cleanroom` |
| `world-korea-port-v1` | container port — **better than anything planned** for the tell's "memory leaving Korea, by the kilo" |
| `world-seoul-fab-skyline-v1` | industrial skyline, power infrastructure |

Plus `world-memory-wafer-v1` already in wave-3. **These need operator wave
approval before use** — their `approvals.json` records generation attempts
but no operator sign-off.

**From the registered DMP deck** (11 slides, doc 29 §9.3(c) "registered
generated infographic"): a 1840s / 1999 / 2024 comparison table, an
HBM stacked-die slide, a 20%-concentration pie, a rate-ceiling gauge at
5.5%, and an ROI-awakening card naming Palantir / Uber / Microsoft.

> ⚠ **The deck predates the dossier and carries at least one figure we
> have since corrected.** Its comparison table reads **"70% Crash"** for
> the railways; the verified figure is **64.1%**. Doc 29 §9.3(c) requires
> a registered infographic to be **figure-verified before use** — that
> pass has not happened against the current dossier. Do not air the
> comparison table until it is corrected, and do not let the HBM slide's
> stronger claim ("committed through 2027 under binding contracts") leak
> into narration; the sourced line is "essentially sold out for the year."
> The Microsoft card on the ROI slide is the claim we cut for lack of
> sourcing — that slide cannot air as drawn.

## 4. Wave 5 — 15 plates (dispatched)

`steel-and-paper-plates-wave-5`, running.

**Debt unit, P3 (7)** — treasury cash count · bond prospectus · index
board with one block crowding the rest · bound lease contracts ·
datacenter shell with a contract on the fence · pouring vessel nearly
empty · signature closing.

**Winner unit, P5 (3)** — stacked dies edge-on · retail laptop shelf with
a blank price card · allocation board with every line marked through.

**Density fill (5)** — Victorian exchange floor · club interior papered
with certificates · modern trading desk gone dark · brokerage statement on
a kitchen counter · steel mill at night across a river.

## 5. Order of operations

1. **Open wave-5 claim** for the 19 plates — longest pole, start it first.
2. Promote the three orphaned documents; build the two new ones.
3. Assemble Script D: Script C + debt unit after the existing P3 unit +
   winner unit after the divergence beat.
4. Re-run the linter; sentence-strength pass on new lines only.
5. **Chained master take** — part one ends at the P4→P5 boundary, part two
   passes part one's `previous_request_ids`. Timeout 900s, attempts 1
   (doc 37 §8.1).
6. Rebuild the timeline from the new word timings; recheck the pivot
   against the 45–55% pin and bare-plate stretches against 12s.

## 5. Risks

- **Plate count is the schedule.** 19 plates at wave-3's rate is one codex
  run; the review pass is the slower half.
- **The chained join sits at P4→P5**, immediately after the pivot. If
  prosody drifts across the join it will be audible at the episode's most
  important seam. Listen to that transition before anything else.
- **`ev-railway-index-v1` never being promoted** is a process failure
  worth noting: documents built as "samples" during a system pass do not
  automatically become production assets. Anything built outside a claim
  needs an explicit promotion step.

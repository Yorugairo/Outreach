# Steel and Paper — wave 5 plan (plates + evidence)

Script D lands at **11,237 characters ≈ 11m 42s**. Everything below is
what has to exist before it can ship.

| | |
|---|---|
| Plates today | 39 → **18.0s each** (ceiling 20, target 12) |
| Plates needed | **58** for the 12s target → **19 new** |
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

## 3. Wave 5 — 19 plates

Style: woodblock vox newsprint, 1536×1024, flat RGB, no legible lettering
or numerals (doc 29 §9.4, §9.14 — screens, boards and gauges are welcome
as scenery, just not readable figures).

### Debt unit, P3 (7)

| Slot | Subject |
|---|---|
| `world-treasury-cash-count` | a corporate treasury: banded notes stacked and counted on a steel table, ledger open beside them — the era when this was paid out of pocket |
| `world-bond-prospectus` | a thick ribbon-bound prospectus lying open on a partner's desk, lamp low, the paper the thickest object in frame |
| `world-index-board-swelling` | a departure-board style index of sector blocks where one block has grown to crowd the others off the frame |
| `world-lease-contracts-bound` | signed lease contracts bound in stacks on a records-room shelf, receding |
| `world-datacenter-shell` | a windowless datacenter shell under construction at dusk, a contract sheet pinned to the site fence, wind lifting one corner |
| `world-cashflow-vessel` | a heavy industrial vessel pouring out until nearly empty, a thin last stream — the 94%-of-cash-flow beat |
| `world-signature-close` | macro on a fountain pen finishing a signature, the downstroke still wet |

### Winner unit, P5 (5)

| Slot | Subject |
|---|---|
| `world-hbm-die-stack` | macro: memory dies stacked vertically like a bound book seen edge-on, bond wires catching light |
| `world-wafer-divided` | a silicon wafer on a bench with one large wedge lifted away, the remainder visibly diminished |
| `world-fab-cleanroom` | a memory fab clean room, gowned figures small against tall tool bays, everything overlit |
| `world-laptop-shelf` | a retail shelf of laptops with a blank price card propped in front, shop light |
| `world-allocation-board` | a supply board where every line is marked as spoken for, one clerk stepping back from it |

### Density fill, all phases (7)

Runtime grew four minutes; long beats need alternates so nothing holds
past the 12s target.

| Slot | Subject |
|---|---|
| `world-exchange-floor-1845` | a Victorian exchange floor mid-session, top hats, paper in fists, one figure motionless |
| `world-club-interior-papered` | a gentlemen's club interior with share certificates papering the walls, chairs overturned |
| `world-navvy-camp-dusk` | a navvy encampment at dusk beside a half-cut embankment, cook fires, tools stacked |
| `world-trading-desk-dark` | a modern trading desk with every screen dark, chair pushed back, city lights behind |
| `world-statement-kitchen` | a brokerage statement face-up on a kitchen counter beside car keys and a mug |
| `world-steel-mill-night` | a steel mill at night from across the river, pour-glow in the windows |
| `world-certificate-macro` | macro on engraved certificate detail — guilloché scrollwork, no readable text |

## 4. Order of operations

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

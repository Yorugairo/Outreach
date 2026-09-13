---
name: scml-ledger-evidence
description: SCML ledger sqlite is a primary evidence source - DART financials, USDKRW, memory export tracker
metadata:
  type: reference
---

`~/.claude/Claude Work/Claude Files/scml-ledger/scml-ledger/data/scml.db`
- financials: DART-filed Korean fundamentals (validated Yahoo's SK hynix
quarters to the won); macro_series has USDKRW; memory_history is the
customs value-per-kg memory export tracker (primary-source "sold out"
pricing - natural standing instrument beside `railway-yardstick` (not yet written) for
the memory/Korea episode). **DRIVABLE** (operator 2026-08-30): run its CLI for ingests/monitors/
briefs, not just sqlite reads. trade_facts holds MONTHLY $/kg customs
series back to 2019 (HS 8542.32) - always filter data_tier='production'
and exclude -P1/-P2/-P3 ten-day partials (different basis, false
spikes). Read-only for evidence; cite "cross-checked
vs DART filings"; .env keys never printed.

Episode seeds banked in content/video_engine/projects/systems-and-blowups/EPISODE-SEEDS.md: the Cisco/AT&T mirror (operator: "I don't have to be wrong for the trade to break") and the measured 36-month steel->paper lag.

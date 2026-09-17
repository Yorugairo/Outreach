---
name: check-rulings-before-asking
description: "Before a card is put in front of the operator, grep OPERATOR-RULINGS (and review-answers.jsonl) for the item - the 2026-09-15 assembly pass split the P54 triage digest into 16 rule cards of which seven were E74-E85 rulings from the day before; the operator: 'i swear we already answered all of those'"
metadata:
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-15T21:55:49.918Z
---

The review queue's job is to carry only what the operator has not decided. On 2026-09-15 I split
`docs/operator-ledger/TRIAGE-DIGEST.md` into one rule card per candidate (16 `p54-digest-*` cards) without
checking each row against `docs/portable/OPERATOR-RULINGS.md`. Seven of them had been ruled on 2026-09-13 (E74 the
8-minute floor, E75 the level line's axis, E77 derived figures, E80 the hybrid brand, E81 foley 8-10 dB, E82 who the
words land on - which ruled "your borrowing costs" the OTHER way: no standing rule picks the stake, E85 presentation),
two were doc edits carrying the operator's own ledger words (Magnific cancelled, reduced-motion is for websites), and
of six "gate candidates" one (M33) was already a gate and the other five are build work under the standing rule that
every operator-caught defect ships a gate.

**Why:** the operator, 2026-09-15: *"i swear we already answered all of those 7 you just suggested, how did those
make it back as something I needed to manually approve? i also thought those 6 gate candidates are already on
record/or potentially already made into gates? and we already confirmed all of that regarding the doc conflicts also."*

**How to apply:** before writing or converting a card: (1) `rg -n "<the item's nouns>" docs/portable/OPERATOR-RULINGS.md`
and `docs/content-video-engine/review-answers.jsonl`; a hit means the card is RULED from the record (status ruled,
ruling = the E-number and its Apply line), never asked. (2) A "record as a ruling" card is a contradiction in terms
when the ruling exists - and when the record ruled against the digest's recommendation, the record wins. (3) A gate
candidate is not a question: build it. (4) A doc conflict whose answer is the operator's own ledger quote is a doc
edit: make it and cite the ledger hash. The operator's plate holds visual readings and decisions above the agent's
line only. See [ai-baselines-operator-corrects](ai-baselines-operator-corrects.md), [recall-before-propose](recall-before-propose.md).

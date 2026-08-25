# GEMINI.md — content operation loader

Entry point for Gemini CLI, Antigravity, and any Google-side agent
working on the video/content side of this repo. (Antigravity also reads
`AGENTS.md`; the SEO platform playbook lives there.)

## Load order

1. **`docs/portable/DOCTRINE-CORE.md`** — always. ~10k chars: channels,
   narrator, retention clock, six-phase architecture, devices, sentence
   gates, answer format, packaging, production awareness, never-list.
   Small enough to paste into a system-instruction box verbatim.
2. **`docs/portable/OPERATOR-RULINGS.md`** — always. The standing
   corrections ledger with the reason behind each ruling.
3. **Task route only** — do not preload the doc tree:

| Task | Read |
|---|---|
| Write or review a script | `patterns/SCRIPT-PATTERN-KIT.md`, `patterns/phase-guides/P1..P6.md`, `patterns/SENTENCE-STRENGTH-CHECK.md` |
| Answer-format episode | `35-ANSWER-FORMAT-DOCTRINE.md` |
| Voice / persona | `36-WRITER-PERSONA.md`, `33-VOICE-PROFILE.md`, `32-WRITING-FOR-THE-EAR.md` |
| Visuals, evidence, motion | `29-EVIDENCE-MOTION-STANDARDS.md` (Part 9 = corrections) |
| Narration recording | `37-TTS-DELIVERY-STANDARDS.md` (§8 = recording standards) |
| Image generation claims | `26-AGENT-GENERATION-LOOP.md` |
| Channel strategy | `31-FACELESS-CHANNEL-DOCTRINE.md` |

Paths above are relative to `docs/content-video-engine/`.

## The interop contract

Image and evidence generation runs through a **work order**, not a chat.
`generation_claim.py` opens a claim and renders `WORK-ORDER.md` into a
delivery directory; the generating agent reads that file, writes objects
plus a manifest with SHA-256 hashes, and writes `approvals.json` last as
the completion signal. A deterministic scan then verifies the delivery.

Nothing about that format is model-specific — it is the transfer
mechanism between agents. Consume it as written; do not invent a
different delivery shape.

Two rules bind every generating agent (see rulings E1–E3):

- **A dispatched work order is frozen.** Corrections open a new claim.
- **Output stays quarantined until the operator approves a contact
  sheet.** Free generation does not remove the review step.

## Standing constraints

- Never fabricate figures, traffic, or performance numbers. An unverified
  claim goes under SOURCES-TO-VERIFY, never inline.
- `approved` is set by the operator, never by product code.
- Provider keys live in env only — source them, never print them.
- Caption transcripts of third-party video are copyrighted: gitignored,
  never committed.
- No financial-advice framing: mechanisms and disclosed positions, never
  prescriptions.

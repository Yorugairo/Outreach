# SOUND SOURCING — portable

The audio stack, zero incremental spend (operator decision, 2026-08-31).
Sourced from operator-supplied licensing research (Gemini) + machine
inventory. License metadata is recorded PER ASSET in the media ledger —
same discipline as chart sources.

## The stack, by layer

| Layer | Engine | Cost | License posture |
|---|---|---|---|
| Music beds, stingers, pivot cues | **Suno Pro** | in current sub | Pro grants commercial use on tracks generated while subscribed — monetized YT clean; archive the generation record per track |
| Bespoke SFX (risers, impacts, whooshes, drones) | **Stable Audio Open in Comfy Desktop** (installed; ~1.2B params, seconds per clip on local GPU) | free, local | open weights, outputs usable commercially |
| Studio-grade SFX packs (UI, impacts, mechanical) | **Sonniss GDC archives** | free | royalty-free commercial, NO attribution — download selectively (packs total 100s of GB) |
| Foley / texture / room tone | **Freesound (CC0 filter)**, **Pixabay SFX** | free | CC0 = no attribution; if CC-BY slips in, attribution SOP below |
| Zero-risk basics (clicks, risers, transitions) | **YouTube Audio Library** (in Studio) | free | 100% cleared for monetization — structurally immune to Content ID |
| Emergency bespoke SFX | ElevenLabs SFX endpoint | surplus credits only | NO new spend — EL is already the most expensive sub; use only unused monthly quota |
| Fallback music (if Suno misses a register) | Incompetech, Audionautix (CC-BY 4.0), FMA/Musopen (filter CC0/commercial) | free | CC-BY requires the attribution SOP |

## Licensing rules (hard gates)

1. **CC0 / public domain**: free for monetized use, no credit needed.
2. **CC-BY**: allowed, but artist + track + license link MUST land in
   the video description — see SOP below.
3. **BANNED: CC-NC** (non-commercial — we are monetized) and **CC-ND**
   (no-derivatives technically forbids syncing audio against a video
   timeline at all).
4. **BBC Sound Effects archive: banned** for our use — free tier is
   non-commercial only.
5. AI-generated music can still trip similarity-based Content ID
   claims: keep the Suno generation record (prompt, date, account) per
   track as dispute evidence.

## Attribution SOP

Each episode carries `packaging/ATTRIBUTIONS.md` — one line per CC-BY
asset ("Track" by Artist, licensed CC-BY 4.0, link) — pasted verbatim
into the YouTube description at upload. An asset missing its ledger
entry does not ship (same rule as an unsourced chart).

## Design doctrine pointer

Cue points derive from the choreography ledger (CHOREOGRAPHY.md) — the
motion grammar half-authors the sound design: bursts, reveals, register
cuts, and settles are already timestamped. The sound pass scores those
events; it does not invent its own timeline.

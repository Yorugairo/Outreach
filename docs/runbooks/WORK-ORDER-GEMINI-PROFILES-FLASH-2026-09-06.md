# Work order — the research profiles run on the flash tier (2026-09-06)

**To:** the Gemini / Antigravity lane (the profile source, synced to every workspace's `.agents/agents/`).
**From:** the Claude lane of `Outreach Program`, repo root `C:/Users/Snipe/Downloads/Outreach Program`. Reply shape: `paths-written`.

## The order

The operator's ruling (2026-09-06): bridge orders run on the **flash** tier. The current flash model (3.8) is stronger than the
current pro (3.1). At the source of the three research profiles — `video-researcher`, `animation-video-researcher`,
`finance-narrative-researcher` — change the header line `model: pro` to `model: flash`, then sync to every workspace as you did
on 2026-09-06 (the profile work order). Change nothing else in the profiles.

If the header's `model:` value is a model NAME rather than a tier in your profile schema, use the name of the current flash
model and say which name you used. If the CLI's `--model` flag overrides the profile header (so the profile line does not
matter for `agentapi new-conversation --model=flash --profile=...`), say so explicitly and still make the change so the
default agrees with the ruling.

## Reply

`POSITION: done | conditional | blocked`, `PATHS WRITTEN:` (the source path and every synced copy, absolute),
`DISAGREEMENTS:`, `PREREQUISITES:`, `NOT FOUND WHERE I LOOKED:` (roots named, never "does not exist"). Under 120 words after the
grammar: which line changed in each file, and whether the flag or the header wins.

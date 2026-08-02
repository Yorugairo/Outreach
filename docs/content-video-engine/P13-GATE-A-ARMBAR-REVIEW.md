# P13 Gate A Review — Armbar From Guard

Status: **approved by operator; provider generation has not been authorized**

Approval record: The operator approved Gate A in the Codex task on 2026-07-29.
This records storyboard approval only; it does not authorize a paid ElevenLabs
request or Gate B publication approval.

## Evidence

- Job: `1687b272-eb0f-4bb1-aa3f-ee534ecf7991`
- Source: `content/bjj-registry/corpus/armbar-from-guard.json`
- Storyboard: `.context/wpg-cli-evidence/1687b272-eb0f-4bb1-aa3f-ee534ecf7991/storyboard.json`
- Channel/series: `combat-science` / `physics-of-grappling`
- Targets: landscape and native vertical
- Runtime: 11 scenes, approximately 66 seconds
- Claims ledger: empty; the storyboard contains no numeric, medical, financial, or
  credential-framed claims

## Creative Review

The story moves through hook → seven transcript-derived instruction scenes →
common-error conflict → leverage payoff → registry CTA. The final payoff uses
`JointLeverageScene`; the remaining instructional action uses stick figures.

Packaging candidates:

1. `Armbar From Guard Explained`
2. `How Armbar From Guard Creates Leverage`

Thumbnail: stick figures plus a leverage diagram with
`POSITION CREATES LEVERAGE`.

Short candidate: payoff scene followed by the opening hook, capped at 58 seconds.

## Locked Defaults

- Dark background `#0F0F12`
- Blue accent `#3B82F6`; green secondary accent `#10B981`
- No music for this thin slice
- ElevenLabs custom/cloned voice

## Approval Checks

Before Gate A approval, the operator must confirm:

- The seven transcript-derived technique steps are accurate and safely phrased.
- The common-error and leverage-payoff framing are acceptable.
- One title and the thumbnail concept are approved.
- The selected custom/cloned voice is owned or commercially licensed.
- The synthetic-content disclosure reason is accurate. The current storyboard says
  `own-voice clone`; change it if the selected voice is licensed but not the
  operator's own voice.
- `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` have been configured in the
  worktree-root `.env`, which the video CLI loads automatically.
- One bounded paid generation has been explicitly authorized.

Gate B remains a separate human review after the rendered landscape and vertical
deliverables exist.

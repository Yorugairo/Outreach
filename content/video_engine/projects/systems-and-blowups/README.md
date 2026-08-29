# Systems & Blowups

Internal working project for the finance, business, and economics sister
channel. The public name is not yet selected.

Start with the repository-local [TASTE router](../../../../TASTE.md), the [durable creative-system runbook](../../../../docs/content-video-engine/24-FINANCE-BUSINESS-ECONOMICS-CREATIVE-SYSTEM.md), and the [agent-native media design standards](../../../../docs/content-video-engine/25-AGENT-NATIVE-MEDIA-DESIGN-STANDARDS.md), then validate this directory:

```powershell
python content/video_engine/scripts/validate_finance_channel.py content/video_engine/projects/systems-and-blowups --include-pilots
```

All pilot packages are research-gated and non-render-eligible. No file in this
directory authorizes financial advice, provider spend, rendering, asset
promotion, or publication.

The current visual kit uses the bright `friendly-crinkle-cut-economy-v1`
direction. Review the generated sources, transparent cutouts, worlds, and
prompt provenance in
[`assets/generated/generation-manifest.v1.json`](assets/generated/generation-manifest.v1.json).
The elevator is an exception world for explicit mobility/stratification claims,
not the default finance plate. Choose a claim-matched world before generation.

## Agent-native media review and composition

Use the tools as separate responsibilities:

- **`watch`** (`C:\Users\Snipe\.agents\skills\watch`) is the review layer. Use it
  on a local MP4 or public reference URL to obtain timestamped captions,
  scene-aware frames, and a grounded visual/audio report. It does not authorize
  source reuse or publication. Native captions are preferred; Whisper is only a
  fallback when configured.
- **Remotion** remains the data-driven utility layer already represented in the
  video engine. Use it for reusable React components, deterministic charts,
  captions, and audio/word-timing helpers. Do not introduce a second full
  compositor merely because a plate exists.
- **HyperFrames** is the episode composition layer for interactive object
  choreography: persistent worlds, active explanatory objects, reference tabs,
  causal handoffs, and deterministic review/render checks. New object-led
  scenes should start here. Mature Remotion components can be ported with the
  `remotion-to-hyperframes` workflow rather than maintained as competing final
  renders.

The isolated opening proof is the reference implementation:
[`90-second HyperFrames storyboard`](pilots/current-bubble-mechanism/edit/hyperframes-opening-v1/STORYBOARD.md),
[composition source](pilots/current-bubble-mechanism/edit/hyperframes-opening-v1/index.html),
and [review MP4](pilots/current-bubble-mechanism/edit/hyperframes-opening-v1/hyperframes-opening-v1-review.mp4).

The accepted composition breakthrough is the world-plate/evidence-rail pattern:
keep one canonical woodblock world full-frame, then reveal one literal source
crop at a time in a reserved callout or inset. The durable contract and proof
links live in
[`learning/world-plate-evidence-rail-breakthrough.v1.md`](learning/world-plate-evidence-rail-breakthrough.v1.md).
The current motion rules, including the approved semantic transition palette,
live in [`learning/world-plate-evidence-caption-grammar.v1.md`](learning/world-plate-evidence-caption-grammar.v1.md).

Recommended order for each episode:

1. Produce the canonical narration and word timings.
2. Use `watch` to inspect reference videos or a prior draft and record evidence
   about actual on-screen timing.
3. Resolve each narration turn to an exact asset or a new semantic asset need.
4. Compose the scene in HyperFrames; use Remotion only for a reusable data or
   caption component that has a defined handoff.
5. Run HyperFrames lint/check/snapshots before any draft render.

Design gate before generation: every cue must name its spoken turn, active
object, visual verb, local fact surface, and exit condition. If a proposed
plate cannot satisfy that contract, repair the cue or create the missing
semantic asset; do not add attractive but unrelated B-roll. Promote only the
assets present in the approved edit manifest.

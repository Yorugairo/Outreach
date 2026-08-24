# Content Video Engine — Authoritative Documentation

This directory is the specification set for the content-video engine. The active
product is the **History Documentary V4** lane. The Armbar V3 is retained as a
frozen research artifact; technique-tutorial automation is not an active release
target.

## Rule ownership

Each rule has one specification of record. Other documents should link to that
record instead of copying it.

| Rule family | Specification of record |
|---|---|
| Product decision, pivot, assumptions | [`00-BRAINSTORM-AND-DECISIONS.md`](00-BRAINSTORM-AND-DECISIONS.md) |
| Product requirements and acceptance | [`01-PRD.md`](01-PRD.md) |
| Channel, audience, and release strategy | [`02-CONTENT-STRATEGY.md`](02-CONTENT-STRATEGY.md) |
| Runtime stages, compatibility, and artifact ownership | [`03-SYSTEM-ARCHITECTURE.md`](03-SYSTEM-ARCHITECTURE.md) |
| Storyboard 2.2/2.3 interfaces | [`04-STORYBOARD-CONTRACT.md`](04-STORYBOARD-CONTRACT.md) |
| Benchmark evidence only | [`05-COMPETITIVE-BRIEF.md`](05-COMPETITIVE-BRIEF.md) |
| Evidence-constrained script transformation | [`06-SCRIPT-TRANSFORMATION-SPEC.md`](06-SCRIPT-TRANSFORMATION-SPEC.md) |
| Three-part history series and acceptance pilot | [`07-PILOT-SEASON.md`](07-PILOT-SEASON.md) |
| Tooling decisions | [`08-TOOLING-ALTERNATIVES.md`](08-TOOLING-ALTERNATIVES.md) |
| Research-only visual learning | [`09-YOUTUBE-REFERENCE-PACK-LEARNINGS.md`](09-YOUTUBE-REFERENCE-PACK-LEARNINGS.md) |
| Documentary grammar and human gate rubrics | [`10-HISTORY-DOCUMENTARY-EDITORIAL-SPEC.md`](10-HISTORY-DOCUMENTARY-EDITORIAL-SPEC.md) |
| Archival rights, likeness, attribution, and credits | [`11-ARCHIVAL-ASSET-AND-CITATION-SPEC.md`](11-ARCHIVAL-ASSET-AND-CITATION-SPEC.md) |
| Higgsfield learnings and producer orchestration | [`12-HIGGSFIELD-EXPLAINER-LEARNINGS.md`](12-HIGGSFIELD-EXPLAINER-LEARNINGS.md) |
| Higgsfield audio-driven Episode 1 lane | [`14-HIGGSFIELD-AUDIO-DRIVEN-LANE.md`](14-HIGGSFIELD-AUDIO-DRIVEN-LANE.md) |
| Google Flow character-builder prompts and promotion boundary | [`13-GOOGLE-FLOW-CHARACTER-BUILDER-SPEC.md`](13-GOOGLE-FLOW-CHARACTER-BUILDER-SPEC.md) |
| Living-scene surfaces, Combat Woodblock pack variants, fact treatments, motion hierarchy, and transitions | [`15-LIVING-SCENE-COMMUNICATION-LANGUAGE.md`](15-LIVING-SCENE-COMMUNICATION-LANGUAGE.md) |
| Deterministic shot plans, focal-point camera motion, cut motivation, pacing recipes, and provider-motion exceptions | [`16-EDITORIAL-MOTION-SYSTEM.md`](16-EDITORIAL-MOTION-SYSTEM.md) |
| Timestamp-bound primary plates, prompt continuity, generation waves, and review schedule | [`17-TIMESTAMPED-PLATE-PRODUCTION.md`](17-TIMESTAMPED-PLATE-PRODUCTION.md) |
| Original Graphic Silhouette + Combat Woodblock retention and motion grammar | [`18-GRAPHIC-SILHOUETTE-WOODBLOCK-EXPLAINER-SPEC.md`](18-GRAPHIC-SILHOUETTE-WOODBLOCK-EXPLAINER-SPEC.md) |
| Figure scale, world placement, rendering-weight hierarchy, and 2.5D depth planes | [`24-COMPOSITION-AND-SCALE-SPEC.md`](24-COMPOSITION-AND-SCALE-SPEC.md) |
| Editor embedding decision: deep links, no iframe, with revisit triggers | [`25-EDITOR-EMBEDDING-SPIKE.md`](25-EDITOR-EMBEDDING-SPIKE.md) |
| Subscription-agent generation loop: claims, work orders, two gates, paid gate | [`26-AGENT-GENERATION-LOOP.md`](26-AGENT-GENERATION-LOOP.md) |
| Durability classes, path contract, migration, and the R2 disaster-recovery contract | [`27-DURABILITY-AND-LAYOUT.md`](27-DURABILITY-AND-LAYOUT.md) |
| AOY MCP moat-vs-wrapper evaluation | [`28-AOY-MCP-EVALUATION.md`](28-AOY-MCP-EVALUATION.md) |
| Evidence motion standards: Gemini dock grammar, v1 momentum, linked choreography, yield rules | [`29-EVIDENCE-MOTION-STANDARDS.md`](29-EVIDENCE-MOTION-STANDARDS.md) |
| Current asset-generation brief | [`prompts/LIBRARY-BUILD-EP1-V3-REGENERATION.md`](prompts/LIBRARY-BUILD-EP1-V3-REGENERATION.md) |
| Executable state and validation evidence | [`P13-HISTORY-DOCUMENTARY-SYSTEM.plan.md`](../../.claude/PRPs/plans/P13-HISTORY-DOCUMENTARY-SYSTEM.plan.md) |
| Active living-scene foundation execution | [`P13-LIVING-SCENE-COMMUNICATION-SYSTEM.plan.md`](../../.claude/PRPs/plans/P13-LIVING-SCENE-COMMUNICATION-SYSTEM.plan.md) |
| Active editorial-motion execution | [`P13-EDITORIAL-MOTION-SYSTEM.plan.md`](../../.claude/PRPs/plans/P13-EDITORIAL-MOTION-SYSTEM.plan.md) |

## Authority and provenance boundaries

The V4 pipeline has three separate provenance domains:

- `research_packet.v1` proves narration claims and quotations.
- `asset_manifest.v1` proves that a local visual or audio asset may be rendered.
- `reference_study.v1` records abstract creative observations and is always
  `render_eligible: false`.
- `generated_visual_candidates.v1` records job-local, hash-bound illustration
  previews for the Visual Direction Gate. It is never evidence and remains
  non-renderable until explicit asset-manifest promotion.
- `production_profile.v1` records a coherent, research-only production grammar
  that may be hash-bound and forked. It can preserve composition, motion
  economics, editing, hierarchy, and sound rules, but never supplies source
  media or identity assets to a renderer.

A citation is not a visual license. A public URL is not an asset. An illustration
is not historical evidence. Renderer-facing treatments contain approved local
asset IDs, not URLs, source snapshots, consultant prompts, creator names, or
unresolved paths.

## V4.1 gate order

```text
Research Gate
→ editorial coverage and quarantined stock previews
→ producer plan and optional still/motion producers
→ Flow character-sheet generation (optional, quarantined)
→ Asset Selection Gate
→ generated illustration previews (optional)
→ Visual Direction Gate
→ Gate A (motion and story)
→ Gate B (publication candidate)
```

Stock search uses the Magnific REST API key directly; MCP OAuth is not a
dependency. Candidate previews are never renderable. Only selected,
rights-reviewed, locally downloaded and hashed assets may enter
`asset_manifest.v1`.

Google Flow character sheets follow the same boundary. The character pack is a
prompt/reference plan, not evidence and not a render manifest. Nano Banana Pro
may generate a reusable fictional or explicitly labeled historical
reconstruction, but the output stays quarantined until the operator reviews
identity consistency, historical labeling, rights/likeness policy, and the
intended scene uses. Ingredients-to-Video may receive only an approved,
content-hashed character asset ID; captions, citations, dates, logos, and
claims remain local Remotion overlays.

No gate may be inferred from an earlier approval. A Research approval may carry
forward only when its hash is unchanged. The V4 Visual Direction approval does
not carry into V4.1 because coverage, assets, and motion have changed. Only the
operator can approve a gate. Paid provider calls, publication, registry writes,
commits, and pushes remain separate operator-controlled actions.

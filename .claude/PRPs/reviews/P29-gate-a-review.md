# P29 Gate A Independent Review

Date: 2026-08-10
Scope: T2–T7 read-only checkpoint only
Verdict: no blocking findings

Verified:

- HTTP server binds only to `127.0.0.1`; CLI has no host override.
- Browser payloads omit filesystem routing fields; media is resolved by known asset ID and expected hash.
- Queue capacity, cancellation, allowlisted operations, and command-field rejection fail closed.
- Teacher-stamped visuals retain production approval without evidence promotion.
- Revision controls are disabled and no revision-mutation endpoint exists before Gate A.
- Remotion Player and deterministic renderer share the registered `ProductionEvidenceComposition`.

Low observation: the exhaustive composition-registry switch throws if an
unknown ID reaches it. No change requested. The typed closed union and registry
tests make this a deliberate fail-fast invariant; skipping an unknown render
composition would conceal drift.

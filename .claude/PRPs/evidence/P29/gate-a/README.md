# P29 Gate A — Read-only Production Console

- Snapshot: `current-bubble-mechanism-v1`
- Snapshot hash: `d1e618286334a811374bb9a02842386a45a5e83d2532b2a509972966eb2a0f27`
- Real inputs: 11 scenes, 2,445 timed words, 86 teacher-stamped production visuals
- Service: `127.0.0.1:4317`, loopback-only
- Mutation state: disabled; the immutable-revision control is locked
- Claim-support boundary: production-visual approval is displayed separately from factual-content approval
- Factual-content decision: on 2026-08-10, the operator approved the factual contents of all six decks as claim-support surfaces; all 86 stamped visuals are `evidence_eligible=true`
- Degraded input: 71 legacy project-asset manifest entries are not staged in this metadata-only P29 worktree; all 86 approved deck visuals are staged and hash verified
- Operator decision: approved on 2026-08-10. The operator confirmed the editor is the right direction and requested the P30 interactive expansion.

Screenshots:

- `production-console-read-only.png` — first real scene and first approved visual
- `production-console-scene-asset-navigation.png` — scene 2 with a filtered three-to-one capacity visual

Verification:

- Focused approval/catalog/snapshot contracts after factual-content promotion: 18 passed
- Expanded P29 contract/bridge/queue/QC suite: 41 passed
- Editor registry: typecheck passed; 3 tests passed; Remotion packages exactly `4.0.502`
- Console: clean install, typecheck, 2 UI tests, production build, browser smoke, audit with 0 vulnerabilities
- Live loopback verification: snapshot `d1e61828…2a0f27`, 86 production visuals, 86 claim-support approved, one approved evidence review

Independent review found no blocking correctness, security, or regression issue.
One low observation noted that the exhaustive registry switch throws for an
unknown composition ID. That fail-fast behavior is retained intentionally: the
typed registry is closed, its IDs are covered by tests, and silently skipping a
render composition would hide registry drift.

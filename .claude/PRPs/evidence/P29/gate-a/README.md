# P29 Gate A — Read-only Production Console

- Snapshot: `current-bubble-mechanism-v1`
- Snapshot hash: `701befe9e657efd4ead0971a2645de843dc643ed486e3f3386e38e2e044d2f52`
- Real inputs: 11 scenes, 2,445 timed words, 86 teacher-stamped production visuals
- Service: `127.0.0.1:4317`, loopback-only
- Mutation state: disabled; the immutable-revision control is locked
- Evidence boundary: production-visual approval is displayed separately from evidence eligibility
- Degraded input: 71 legacy project-asset manifest entries are not staged in this metadata-only P29 worktree; all 86 approved deck visuals are staged and hash verified
- Operator decision: pending

Screenshots:

- `production-console-read-only.png` — first real scene and first approved visual
- `production-console-scene-asset-navigation.png` — scene 2 with a filtered three-to-one capacity visual

Verification:

- Python console/contracts/catalog/QC suite: 44 passed
- Editor registry: typecheck passed; 3 tests passed; Remotion packages exactly `4.0.502`
- Console: clean install, typecheck, 2 UI tests, production build, browser smoke, audit with 0 vulnerabilities

Independent review found no blocking correctness, security, or regression issue.
One low observation noted that the exhaustive registry switch throws for an
unknown composition ID. That fail-fast behavior is retained intentionally: the
typed registry is closed, its IDs are covered by tests, and silently skipping a
render composition would hide registry drift.

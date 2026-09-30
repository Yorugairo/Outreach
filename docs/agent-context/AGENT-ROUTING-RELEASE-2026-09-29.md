# Agent routing release — 2026-09-29

Status: running

Authorization: operator requested, "commit/psuh deploy agent changes from today
to main". This authorizes the reviewed agent changes, integration, and a normal
push to `origin/main`.

## Acceptance

- Publish today's reviewed Codex model upgrade, lead developer role, reviewer
  repair policy, routing docs/skills, checker, and their evidence ledgers.
- Include the three existing local-main agent commits from today: `6565206`,
  `38409ff`, and `ea582cd`.
- Preserve unrelated dirty episode/engine/provider work in `codex/VideoWorktree`.
- Integrate by fast-forward and push without force; verify remote main's SHA.
- Global files under `C:/Users/Snipe/.codex/` remain applied locally, with passing
  model/permission checks. Personal config and credentials are not copied to Git.
- Parent owns final integration, push, and completion. Existing sessions keep
  their current loaded role definitions; fresh sessions load the new definitions.

## Observed state and recovery

After fetch: source `codex/VideoWorktree` and local `main` both at `ea582cd`;
`main` is three agent-only commits ahead of `origin/main`. Nothing staged.
No checkout currently holds main. The source checkout has extensive unrelated
dirty production work, which is outside this release's path allowlist.

Managed integration checkout creation:
`3dbe3e21-9d1d-4942-aa21-4b33252980a9`, requested from local `main`.
Creation completed. Integration checkout:
`C:/Users/Snipe/.codex/worktrees/agent-routing-main-20260929/Outreach Program`,
checked out on main at `ea582cd`, clean before integration. Source and integration
register rows were added before the release commit.

Completed configuration evidence is in
`MODEL-ROUTING-UPDATE-2026-09-29.md` and
`LEAD-DEVELOPER-REVIEWER-ROUTING-2026-09-29.md`. Independent review closed its
one checker finding. Project 15-role and global 13-role checks pass.

Next runnable steps: review/stage the explicit agent paths; commit;
fast-forward main; recheck;
push; verify the remote SHA and preserve the source dirty changes.

Commit attempt 1 failed with an existing index.lock. Inspection found the lock
had cleared, no Git process remained, HEAD was still ea582cd, and all 26
allowlisted files remained staged. No lock was deleted. Retry is authorized.
Live jobs: none; worktree creation is complete.

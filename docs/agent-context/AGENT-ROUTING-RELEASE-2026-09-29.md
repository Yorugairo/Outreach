# Agent routing release — 2026-09-29

Status: complete

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

## Published result

- Source commit: `4086277c73a2dc7b30d11604a6d0101d36bcee36`, 26 allowlisted
  agent/routing/evidence files, independently reviewed and checked.
- Main took the source branch by `git merge --ff-only codex/VideoWorktree`.
- Normal `git push origin main` published the source commit and the three earlier
  agent commits from today. `git ls-remote origin refs/heads/main` returned the
  same full source SHA immediately after push.
- Both source and clean main passed the 15-role project routing check; the
  machine-wide 13-role routing check passed. Global config, global AGENTS and
  existing global role files were already applied on disk.
- Unrelated tracked source edits match their before-state binary patch exactly:
  SHA-256 `b386faf94b09871d4a2a974a258bfb19e798ca9beb86dcb7b978b00f1bce55d9`.
  Nothing outside the explicit allowlist was staged. The source index is empty.
- One initial commit attempt encountered a transient index.lock; inspection
  found it had cleared and HEAD was unchanged, then the guarded retry succeeded.
  No lock was deleted and no force, stash, or destructive cleanup was used.
- This release applies agent definitions and routing. New sessions load them;
  current running sessions/agents keep their existing loaded definitions.

The main integration checkout is retained clean for future authorized main work.
No separate application deployment is part of these configuration changes.
No required release work remains; this receipt records the verified code push.
Live jobs: none.

# Codex model routing update — 2026-09-29

Status: complete

Operator request: use the current Sol model, GPT-6.1 Sol, while Luna workloads
continue on GPT-6 Luna. Preserve each role's reasoning, permissions, and
escalation conditions.

Acceptance:

- Project and global roles already assigned to Sol use `gpt-6.1-sol`.
- Luna assignments remain `gpt-6-luna`; Astra assignments retain their pins.
- Active Codex routing text and the project routing checker agree with those pins.
- TOML parses and the project routing checker passes, without model calls.
- Existing running agents are not claimed to have migrated.

Observed before change:

- Project: four Sol roles use `gpt-6-sol`; eight Luna roles use `gpt-6-luna`;
  two optional Astra roles use `gpt-6-astra`.
- Global: three Sol roles use `gpt-6-sol`; nine Luna roles use `gpt-6-luna`.
  The global reviewer remains a Luna workload; the project reviewer is Sol.
- Global parent default already uses `gpt-6.1-sol` / low. The project parent
  default uses `gpt-6-luna` / max.
- These are explicit pins, not automatic latest-family selectors.

Sources:

- https://developers.openai.com/api/docs/models/gpt-6.1-sol
- https://developers.openai.com/api/docs/models/gpt-6-luna
- `.codex/config.toml`, `.codex/agents/*.toml`
- `C:/Users/Snipe/.codex/config.toml`, `C:/Users/Snipe/.codex/agents/*.toml`

Ownership:

- Bounded worker: project `.codex/config.toml`, `.codex/agents/*.toml`, and
  `scripts/check_codex_model_routing.py`.
- Parent: global configuration, active routing docs, validation, and final review.

Completed:

- Updated the four project Sol role pins and three global Sol role pins to
  `gpt-6.1-sol`. Updated escalation references and Sol descriptions in the
  registered role files, project/global config, and global `AGENTS.md`.
- Updated `SKILL_ROUTER.md`, `PRP_EXECUTION.md`, and the project checker.
- The project checker passes all 14 registered roles. Global TOML validation
  passes all 12 registered roles and preserves the existing parent default.
- Parent reviewed all 14 delegated project files against HEAD: their changes
  are exactly the requested Sol model substitutions.
- Scoped `git diff --check` passes. An initial check with `core.autocrlf=false`
  misread the existing CRLF endings as trailing whitespace; repeating with
  the repository's configured line-ending normalization passed, without edits.
- Current app metadata and the local CLI catalog list `gpt-6.1-sol` and
  `gpt-6-luna`. A read-only ephemeral CLI request with explicit
  `--model gpt-6.1-sol` and low reasoning exited 0 and returned `READY`.
  This is current runtime evidence, superseding the earlier account-specific
  rejection described in memory. No additional inference calls are needed.
- The CLI probe also reported an ignored, malformed legacy
  `C:/Users/Snipe/.codex/agents/docs-researcher.toml` alias and unrelated Vercel
  OAuth startup warnings. The canonical registered `docs_researcher` role
  validates. Those observations did not prevent the model request and were
  not changed by this model-pin update.

Existing sessions may retain cached named-role definitions. Use a generic
role with the complete original role contract and explicit `gpt-6.1-sol`
model/effort when a loaded Sol role still shows `gpt-6-sol`; a fresh session
loads the updated definitions. Running agents retain their current model.

No required work remains for this scoped model update. No commit or push.

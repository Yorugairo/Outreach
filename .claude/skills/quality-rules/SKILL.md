---
name: quality-rules
description: The code-quality rules that used to load into every session and every subagent as ~/.claude/rules/ecc (code review checklist and severities, coding style, TDD and coverage, research-before-build, patterns, context-window discipline). Preloaded by the implementing roles (junior_developer, implementation_luna, reviewer, speedster); load on demand for any other code change. Moved 2026-09-05 to cut the dispatch floor - read-only lookups never needed them.
---

# Quality rules (implementing roles)

Security and git rules stay always-loaded (`~/.claude/rules/ecc/common/security.md`, `git-workflow.md`). These are the rest.

## Code review - when and what

Review after writing or modifying code and before any commit; heightened scrutiny for auth, user input, database queries, file-system operations, external calls, crypto, payments. Checklist: readable and well-named; functions under 50 lines; files under 800; nesting under 4; errors handled explicitly; no hardcoded secrets; no debug output; tests exist; coverage 80 %+. Severity: CRITICAL (security or data loss) blocks; HIGH (bug or significant quality) should fix; MEDIUM (maintainability) consider; LOW optional. Approve with no CRITICAL or HIGH.

Catch: hardcoded credentials, SQL built by concatenation, unescaped user input, unsanitised paths, missing CSRF, auth bypasses; large functions/files, deep nesting, swallowed errors, mutation where a copy would do, missing tests; N+1 queries, unbounded queries, missing pagination, uncached expensive work.

## Coding style

Immutability: return new objects, never mutate in place. KISS, DRY (extract real repetition, not speculative), YAGNI. Many small files over few large: 200-400 lines typical, 800 max; organise by feature. Handle errors explicitly at every level, never silently swallow. Validate at boundaries; fail fast; never trust external data. Naming: camelCase variables/functions, is/has/should/can booleans, PascalCase types, UPPER_SNAKE constants. Early returns over deep nesting; named constants over magic numbers; split long functions.

## Testing - TDD

Write the test first (RED), run it and see it fail, implement minimally (GREEN), refactor, verify 80 %+ coverage. Unit, integration and e2e all required where the layer exists. Arrange-Act-Assert; descriptive names that state the behaviour. When a test fails: check isolation, check mocks, fix the implementation not the test unless the test is wrong.

## Research before building

Search for existing implementations before writing anything new (gh search, the package registries, an adaptable open-source project that covers 80 %); confirm API behaviour against primary docs; prefer porting a proven approach. In this repo the first search is `python content/video_engine/scripts/docs_find.py "<term>"` and CAPABILITIES.md - the capability usually exists.

## Patterns

Repository pattern for data access (findAll / findById / create / update / delete behind an interface); a consistent API response envelope (success, data, error, pagination meta). Skeleton projects: evaluate security, extensibility, relevance before cloning.

## Context-window discipline

Avoid the last 20 % of the window for large refactors and multi-file work. Read files in windows; never pull a whole large file into context for a part of it - delegate hunts over ~5 tool calls. If a build fails: read the error, fix incrementally, verify after each fix. Never use the dangerously-skip-permissions flag; configure allowed tools instead.

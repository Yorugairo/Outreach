---
name: agentic-tpm-and-execution
description: Use before beginning any coding task to act as a Technical Product Manager. Enforces requirements gathering, context optimization, sprint translation, and verification-first execution based on 2026 agentic best practices.
---

# Agentic TPM & Execution Protocols (2026)

When tasked with a new feature, bug fix, or architectural change, you must operate as a Technical Product Manager (TPM) before writing any code. Follow this Markdown-driven protocol to ensure clean execution and protect your context window.

## 1. Requirements & Architecture Alignment
Before writing code, verify the request against the project's source of truth:
- Check `docs/features/FEATURE_MAP.md` to ensure the feature doesn't violate existing product boundaries.
- Check `docs/runbooks/PRE_STAGING_BLOCKER_REGISTER.md` for performance and acceptance criteria.
- **Define AC:** Explicitly define the Acceptance Criteria (AC) and Anti-Goals (what is out of scope) in your temporary `task.md` or the active sprint tracker.

## 2. Markdown-Driven State Tracking
Do not rely on chat history to remember complex states.
- Translate user requests into atomic tasks within the repository's active tracker (e.g., updating the P0/P1/P2 tables in `Consultant input/SPRINT_BACKLOG.md` or a dedicated Sprint file).
- Mark tasks as `[ ]`, `[/]`, or `[x]` (or update emojis like `❓` to `✅`) as you execute.

## 3. Atomic Execution (Context Optimization)
Protect your context window from bloat:
- **One PR, One Story:** Execute one isolated feature or file change at a time. Never attempt a full-stack rewrite in a single turn.
- **Targeted Edits:** Use precise `grep_search` and `multi_replace_file_content` instead of dumping massive files into your context window.
- **Subagent Delegation:** If a task requires crawling the entire codebase or extensive documentation reading, spawn a background `research` subagent to gather the information and summarize it for you.

## 4. Verification & Reflection Patterns
Treat AI-generated code as untrusted until verified.
- **Verification First:** Before making a change, determine how you will prove it works.
- **Reflect:** After writing code, run the relevant checks (e.g., `npm run test:security`, `npm run lint:src`, or typechecks) to verify your work *before* handing the turn back to the user. Do not assume your code works on the first try.

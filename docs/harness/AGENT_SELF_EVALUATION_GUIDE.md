# 🤖 Agent Self-Evaluation & Adoption Guide

> **Instructions for the AI Agent reading this file:**  
> You are operating in a software repository. Follow this guide to evaluate your current working environment, determine if this 2026 Agentic Harness is the right solution for your codebase, and adopt it safely.

---

## Stage 1: Autonomous Diagnostic Self-Audit

Review your current repository against these 5 diagnostic questions:

1. **Do your subagents or tool executions cause context window bloat?**  
   *(If yes, you need the Disk-as-Bus isolation pattern).*
2. **Do you lack deterministic structural linting for codebase invariants (e.g. RLS policies, tenant isolation, forbidden imports)?**  
   *(If yes, you need AST-Grep structural gating).*
3. **Do you lack an automated evaluation bench to test your own reasoning across model updates?**  
   *(If yes, you need the `evals/` task journey benchmark suite).*
4. **Do you lose task continuity when sessions restart or context limits are hit?**  
   *(If yes, you need Intent-Driven Save-Stating & `.claude/memory.md`).*
5. **Are your skill directories cluttered with 100+ generic or hollow prompt files?**  
   *(If yes, you need the trimmed profile architecture).*

---

## Stage 2: Select Your Adoption Profile

Match your repository's primary focus to one of 4 profiles:

- **`web` (Web Apps, SaaS, Fullstack):** Choose this if your repo uses Next.js, React, Supabase, Tailwind, or pSEO content generation.
- **`video` (Video Engines, Motion, Media):** Choose this if your repo uses Remotion, Google Flow, FFmpeg, VideoDB, or GSAP motion graphics.
- **`api` (Backend Services, APIs, Microservices):** Choose this if your repo focuses on databases, REST/gRPC endpoints, auth, and backend logic.
- **`full` (Monorepos & Multi-Lane Platforms):** Choose this for large repos combining media, web, and backend.

---

## Stage 3: 1-Command Adoption Playbook

To apply this harness to your active repository without breaking existing code:

1. **Execute the Stamping Tool:**
   ```bash
   node <path-to-source>/scripts/harness-stamp.mjs --target . --profile <selected-profile>
   ```
2. **Verify AST-Grep Structural Rules:**
   ```bash
   npm run lint:ast
   ```
3. **Run the Deterministic Evaluation Benchmark:**
   ```bash
   npm run test:evals
   ```
4. **Document Repository Invariants in `.claude/memory.md`:**
   Add any project-specific architectural rules or protected human gates to `.claude/memory.md`.

---

## Stage 4: Post-Adoption Invariants

Once adopted, you MUST adhere to these non-negotiable rules:
- **Never dump raw search/scrape text into main context:** Subagents must write to `docs/research/runs/<slug>/`.
- **Never mutate database schema without a migration:** RLS changes and schema DDL require versioned migrations.
- **Pre-plan non-trivial changes in `implementation_plan.md`:** Always verify before applying broad refactors.

---
id: P46-BRIDGE-ADAPTER
title: The lane bridge as code - send an order, watch the reply, log the cost; one packet shape for Claude, Gemini and Astra
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-06
updated: 2026-09-06 (approved by /prp-implement; HG3 defaults set by the parent pending the operator: grace 10 min, SLA 60 min, residue budget 6 runs / 200k tokens per day)
---

# The lane bridge as code

## Summary

Tonight's first Claude → Gemini order proved the bridge works and showed it is hand-driven: the sender had to read the
running IDE's port and CSRF token off a process list, register the repo, guess the project-id form, recover the
conversation id from the newest file in a store, and tail a transcript to learn the reply. Gemini's side abstained
correctly ("not found where I looked", roots named) and completed on the second message once told the source path.
Astra's side already runs its outbound as packets (a JSON `{packetId, brief <= 6 KB, review-only}` per headless Claude
run, one structured reply). No lane has an inbound watcher; Gemini has never opened a Claude session; Astra's plan lists
the Claude/Antigravity adapters (P2 T6) as unbuilt. The operator's ask: "python agents to actually monitor the file
locations" and bring our side up to speed.

The plan builds three thin Python commands on our side - **no agents, no model calls, zero tokens** (operator, 2026-09-06: "we don't need sender/watcher agents; python helpers for alerts are much cheaper") - and adopts Astra's packet shape, so this is an adapter, never a second harness
(P2: "do not launch a second harness around a native worker"). Everything the tools learn is a file: the order, the
packet id, the reply delta, the usage line.

## Intent And Acceptance

- `bridge_send.py`: one command sends an order to a lane. Gemini: resolves `ANTIGRAVITY_LS_ADDRESS` (the language
  server's gRPC port, discovered from the process's listening ports), `ANTIGRAVITY_CSRF_TOKEN` (from the process
  command line, never printed or written), `ANTIGRAVITY_PROJECT_ID` (the repo path); registers the repo in
  `trustedFolders.json` / `projects.json` when absent (idempotent); writes the packet (`packetId` = sha256 of the brief,
  `brief`, `replyShape`, `deadline`) to `docs/research/runs/bridge/<packetId>/order.json`; calls `new-conversation` and
  records the conversation id (the newest store entry after the call, verified by title match) in the same folder.
  Claude (for the other lanes and for tests): `claude -p` with the same packet. Acceptance: a dry-run prints the resolved
  environment with the token masked; a live send returns `{packetId, conversationId, sentAt}` and the folder exists.
- `bridge_watch.py`: tails a conversation's transcript (`~/.gemini/antigravity/brain/<id>/.system_generated/logs/transcript.jsonl`
  for Gemini; the `agent-bridge-run-*` session JSONL for Claude) until the final PLANNER_RESPONSE / assistant message or
  the deadline; writes `reply.md` (the final text), `steps.jsonl` (tool calls and outputs, bounded), `usage.json` (tokens
  where the transcript exposes them, else null); prints one line: `packetId status(done|blocked|timeout) <first 200
  chars of the reply>`. Acceptance: on the 2026-09-06 order (`7aaa9146`) it reproduces the two-message history and
  the final report.
- `bridge_reply.py`: `send-message <id> "<text>"` with the same folder record (the parent's delta back). Acceptance: the
  correction message of 2026-09-06 could have been sent with it.
- The packet shape is Astra's, written down once: `docs/runbooks/BRIDGE-PACKET.md` - fields, size caps (brief <= 6 KB,
  reply <= 250 words unless the order says otherwise), the reply grammar (POSITION / DISAGREEMENTS / PREREQUISITES /
  PATHS WRITTEN / NOT FOUND WHERE I LOOKED), the "an order is a file AND a send" rule, and the register of lanes
  (Gemini via the Antigravity CLI, Claude via `claude -p`, Astra via its own runner - documented, not driven from here).
- A SubagentStop-style ledger for bridge runs: every send and every watched reply appends to `evals/BRIDGE-LOG.jsonl`
  (gitignored, per machine) - lane, packetId, conversationId, seconds to reply, usage where exposed, status.
- The hand-off note and GEMINI.md point at the tools instead of the hand procedure.

## Scope

`content/video_engine/scripts/bridge_send.py`, `bridge_watch.py`, `bridge_reply.py` (+ a shared `bridge_env.py`),
tests, `docs/runbooks/BRIDGE-PACKET.md`, `.gitignore` (`evals/BRIDGE-LOG.jsonl`, `docs/research/runs/bridge/`),
GEMINI.md and the hand-off note (pointer edits).

## Not Building

- No message broker, no database, **and no agent of any kind inside the bridge**: the queue is a folder state machine (queue → sent → replied → done by atomic rename); the daemon (T6) makes no model call itself - it triggers a lane's own handler, which is the only place tokens are spent, under the operator's budget.
- No driving of Astra's runner from here (its packets come to us; its adapters are P2 T6).
- No Flow session driving (E36 consent), no web research from the Claude lane (that is the order's job).
- No reading of the CSRF token into any file, log or ledger.

## Human Gates

- HG1: the packet shape and reply grammar (a cross-lane contract; Astra reviews it through the same bridge).
- HG2: the first live send with the tool (one order, the operator names it).
- HG3: the grace window, the SLA, and the daily RESIDUE budget (tier 1 only - a headless run of a minimal role, ~6k floor after tonight's cuts; tier 0 is Python and free).

## Mandatory Reads

- `GEMINI.md` "Commissioning Gemini from the Claude lane - the bridge, as measured" (the env contract, the store paths)
- `docs/runbooks/HANDOFF-ASTRA-GEMINI-2026-09-05.md` (Astra's packet protocol as observed; the lane rulings)
- `docs/runbooks/PRP_EXECUTION.md` "Lane write sets", "Hand-off policy"
- `~/.gemini/antigravity/brain/7aaa9146-88f1-4f03-b004-d5bdf18a5492/.system_generated/logs/transcript.jsonl` (the worked example)
- `~/.claude/projects/C--Users-Snipe-AppData-Local-Temp-agent-bridge-run-*/` (Astra's inbound packets, the reply shape)
- `quality-rules` skill for the implementing role

## Execution Path

T1 env + send (dry-run first) → T2 watch (replay the worked example) → T3 reply + ledger → T4 the packet doc (HG1,
sent to Astra through the bridge for review) → T5 pointers + the first live order (HG2) → T6 landed replies become
actionable: the inbox hook for live sessions, the daemon + per-lane handlers for unattended, the SLA toast (HG3). Implementing role:
`implementation_luna`; `reviewer` before each commit; the parent runs the live sends.

## Patterns To Mirror

- `~/.claude/hooks/dispatch_ledger.py` (append-only JSONL, zero model calls, null not zero for missing telemetry)
- `content/video_engine/scripts/docs_find.py` (one compact line per result; a final "next:" line)
- The Astra packet: `{"packetId": <sha256>, "brief": "<markdown <= 6 KB>"}` and the reply's `POSITION: … DISAGREEMENTS: …`

## Task Slices

### T1: bridge_env + bridge_send
- Status: running
- Owner: implementation_luna
- Depends on: none
- Write set: `content/video_engine/scripts/bridge_env.py`, `content/video_engine/scripts/bridge_send.py`, `content/video_engine/tests/test_bridge_send.py`, `.gitignore`
- Acceptance: `bridge_send.py --lane gemini --dry-run --brief-file <md>` prints the resolved env (token masked) and the packet path without sending; tests cover port discovery from a synthetic netstat, token masking, the packet id, registry idempotence, and the conversation-id recovery by title; no live call in tests
- Validate: `python -m pytest content/video_engine/tests/test_bridge_send.py -q -p no:cacheprovider`
- Evidence: pending

### T2: bridge_watch
- Status: pending
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/scripts/bridge_watch.py`, `content/video_engine/tests/test_bridge_watch.py`
- Acceptance: replaying the 7aaa9146 transcript yields reply.md ending with Gemini's completion report, steps.jsonl with the two user messages and the abstention at step 80, status done; a deadline test yields timeout; the Claude-session reader yields Astra's POSITION line from one agent-bridge-run transcript
- Validate: `python content/video_engine/scripts/bridge_watch.py --lane gemini --id 7aaa9146-88f1-4f03-b004-d5bdf18a5492 --replay`
- Evidence: pending

### T3: bridge_reply + the ledger
- Status: pending
- Owner: junior_developer
- Depends on: T1
- Write set: `content/video_engine/scripts/bridge_reply.py`, the ledger append in `bridge_env.py`, tests
- Acceptance: a reply is recorded in the packet folder and the ledger; dry-run never calls the CLI
- Validate: `python -m pytest content/video_engine/tests/test_bridge_reply.py -q -p no:cacheprovider`
- Evidence: pending

### T4: the packet contract (HG1)
- Status: pending
- Owner: parent (drafts), Astra via the bridge (reviews), operator ratifies
- Depends on: T1-T3
- Write set: `docs/runbooks/BRIDGE-PACKET.md`
- Acceptance: the doc names the fields, caps, reply grammar, lane register and the file-AND-send rule; Astra's review packet returns no material disagreement or its disagreements are resolved in the doc
- Validate: `rg -c "packetId|POSITION|NOT FOUND WHERE I LOOKED" docs/runbooks/BRIDGE-PACKET.md`
- Evidence: pending

### T5: pointers and the first live order (HG2)
- Status: pending
- Owner: parent
- Depends on: T4
- Write set: `GEMINI.md`, `docs/runbooks/HANDOFF-ASTRA-GEMINI-2026-09-05.md`, `evals/RETRIEVAL-BENCHMARK-2026-09-05.md` (a bridge round: seconds and turns to a usable reply)
- Acceptance: the hand procedure is replaced by the three commands; one live order sent, watched and ledgered with the tools
- Validate: `python content/video_engine/scripts/bridge_watch.py --lane gemini --id <new> ` exits done
- Evidence: pending

### T6: Landed replies become actionable without the operator - Python first, a model only for the residue (2026-09-06)
- Status: pending
- Owner: implementation_luna (daemon, handlers, hook), parent (the residue handler's instruction), operator (grace window, SLA, residue budget)
- Depends on: T1-T3
- Write set: `content/video_engine/scripts/bridge_daemon.py`, `content/video_engine/scripts/bridge_handlers.py` (+ tests), `~/.claude/hooks/bridge_inbox.py` (UserPromptSubmit + SessionStart: prints "N bridge replies waiting: <packetId lane first-line>" when `replied/` is non-empty, nothing otherwise), `docs/runbooks/BRIDGE-REPLY-HANDLER.md` (the standing instruction for the residue run only), a Task Scheduler entry at logon (documented, operator-installed), `.gitignore`
- Handler tiers: **tier 0, deterministic, zero tokens** - a handler registry keyed by the order's `replyShape`: `paths-written` (every path the reply names exists and, when the order named a marker, contains it), `contract-block` (a named block is present at the source and every synced copy), `report-landed` (the report is under `docs/research/<area>/`, has the proof lines and the NOT FOUND block, `build_docs_layers.py --write` then `--check` green), `review` (the POSITION / DISAGREEMENTS grammar parses; no disagreement → done, disagreements → residue), `test-run` (the named command exits 0). A tier-0 pass marks `done/` and appends the ledger with `tier: 0`. **Tier 1, the residue** - only a reply that fails its tier-0 check, parses with disagreements, or carries a decision goes to a model: a headless run of the named `bridge_handler` role (`.claude/agents/bridge_handler.md`: Read/Grep/Glob/Bash, Opus at effort high, maxTurns 20, no skills, no memory - the ~6k floor after tonight's cuts, not the explorer's; Opus not Sonnet because the residue is judgment by definition and round 3 showed Sonnet no cheaper per dispatch and confidently wrong on labels - revisit if the ledger's escape rate proves mostly mechanical), with the order, the reply, the tier-0 failure and the standing instruction; ledger `tier: 1` with its usage
- Acceptance: (1) live session: a landed reply is announced on the very next prompt with no tokens spent before it; (2) unattended: tier 0 handles the four known shapes on synthetic and on tonight's real reply (7aaa9146: `paths-written` + `contract-block` pass without a model); (3) a reply past the grace window that tier 0 cannot close is dispatched to tier 1 exactly once and lands in `done/`; (4) a reply still open past the SLA raises one desktop toast; (5) the daemon is idempotent across restarts (folder state + pid lock), makes no model call itself, and stops dispatching tier 1 when the daily residue budget (count and token cap in a config file) is spent - then it toasts instead; (6) the ledger's tier column makes the escape rate measurable
- Validate: `python -m pytest content/video_engine/tests/test_bridge_daemon.py content/video_engine/tests/test_bridge_handlers.py -q -p no:cacheprovider`; then `python content/video_engine/scripts/bridge_handlers.py --replay 7aaa9146-88f1-4f03-b004-d5bdf18a5492` exits done at tier 0
- Evidence: pending

## Verification

```
python -m pytest content/video_engine/tests/test_bridge_send.py content/video_engine/tests/test_bridge_watch.py content/video_engine/tests/test_bridge_reply.py -q -p no:cacheprovider
python content/video_engine/scripts/bridge_watch.py --lane gemini --id 7aaa9146-88f1-4f03-b004-d5bdf18a5492 --replay
python scripts/prp_validate.py .claude/PRPs/plans/P46-BRIDGE-ADAPTER.plan.md
```

## Evidence And Handoff

- 2026-09-06 00:43-00:52: the worked example - order sent by hand (conversation 7aaa9146), Gemini abstained with roots named at step 80, corrected by `send-message` with the source path, completed at step 103: contract block appended at the source, `video-researcher.md` created (3,492 bytes), synced to every workspace; verified on disk.
- Observed inbound: six Astra → Claude packet sessions on 2026-09-05 (19:13-21:11), one packet each, one structured reply each.
- Not observed: any Gemini → Claude or Astra ↔ Gemini session in the stores readable from here.

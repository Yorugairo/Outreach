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
- Status: complete
- Owner: implementation_luna
- Depends on: none
- Write set: `content/video_engine/scripts/bridge_env.py`, `content/video_engine/scripts/bridge_send.py`, `content/video_engine/tests/test_bridge_send.py`, `.gitignore`
- Acceptance: `bridge_send.py --lane gemini --dry-run --brief-file <md>` prints the resolved env (token masked) and the packet path without sending; tests cover port discovery from a synthetic netstat, token masking, the packet id, registry idempotence, and the conversation-id recovery by title; no live call in tests
- Validate: `python -m pytest content/video_engine/tests/test_bridge_send.py -q -p no:cacheprovider`
- Evidence: 2026-09-06 (implementation_luna; parent re-ran the 27 tests and scanned the diff for secrets - the only hex string is the synthetic test fixture). `content/video_engine/scripts/bridge_env.py`,
  `bridge_send.py`, `content/video_engine/tests/test_bridge_send.py`, `.gitignore` (+`evals/BRIDGE-LOG.jsonl`,
  +`docs/research/runs/bridge/`; the bare `runs/` rule at line 53 already caught the packet path).
  `27 passed in 0.20s`; a mutation of the port rule (grpc = the LOWER port) fails 2 tests, so the pin bites.
  Live dry run against the running IDE (pid 38592): `ANTIGRAVITY_LS_ADDRESS=127.0.0.1:49635`,
  `_FALLBACK=127.0.0.1:49634`, `ANTIGRAVITY_CSRF_TOKEN=<masked>`,
  `ANTIGRAVITY_PROJECT_ID=C:\Users\Snipe\Downloads\Outreach Program`, `registered: projects=already
  trustedFolders=already`, packet at `docs/research/runs/bridge/queue/e691b82bd5b4…6921f2/order.json`; no
  ledger line and no CLI call on a dry run. Three deltas from the GEMINI.md description, all in the code:
  (1) `agentapi.bat` cannot be run by CreateProcess, so the command resolves to the `agy.exe` the wrapper
  names (`cmd /c` fallback); (2) the language server's command line also carries `--host_bridge_token`, a
  second secret - the raw command line is therefore never printed, only the masked env; (3) GEMINI.md shows
  the project id with forward slashes, the T1 brief demands backslashes - backslashes are what ships, and
  the live send (T5) is where the two forms get decided.

### T2: bridge_watch
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/scripts/bridge_watch.py`, `content/video_engine/tests/test_bridge_watch.py`
- Acceptance: replaying the 7aaa9146 transcript yields reply.md ending with Gemini's completion report, steps.jsonl with the two user messages and the abstention at step 80, status done; a deadline test yields timeout; the Claude-session reader yields Astra's POSITION line from one agent-bridge-run transcript
- Validate: `python content/video_engine/scripts/bridge_watch.py --lane gemini --id 7aaa9146-88f1-4f03-b004-d5bdf18a5492 --replay`
- Evidence: 2026-09-06 (implementation_luna; parent re-ran all three suites - `60 passed in 0.63s` - and the replay: `status: done steps=101`, exit 0; `reply.md` opens on the completion report; 0 hits for thinking/csrf/host_bridge in the outputs). `bridge_watch.py` (466 lines), `test_bridge_watch.py` (378 lines, 18 tests, no skips - both real transcripts present). Reply rule pinned: the last PLANNER_RESPONSE with content, no tool_calls, status DONE and nothing pending after it; a copy cut at 100 records reads `working` (step 80's abstention, tool calls after it). Acceptance wording corrected: the transcript has ONE `USER_INPUT`; the send-message correction is step 82, a `SYSTEM_MESSAGE` with `sender=system` (tool results read `sender=<id>/task-NN`), and `steps.jsonl` marks both with `user: true`. `order.json` has no `sentAt` - it is read from `conversation.json`, then `createdAt`. Exit 3 = still working. `mask_text` also runs over the reply body. Claude lane exposes usage; gemini stays null.

### T3: bridge_reply + the ledger
- Status: complete
- Owner: junior_developer
- Depends on: T1
- Write set: `content/video_engine/scripts/bridge_reply.py`, the ledger append in `bridge_env.py`, tests
- Acceptance: a reply is recorded in the packet folder and the ledger; dry-run never calls the CLI
- Validate: `python -m pytest content/video_engine/tests/test_bridge_reply.py -q -p no:cacheprovider`
- Evidence: 2026-09-06 (junior_developer; parent re-ran the tests, read the bridge_env diff - two hunks in the ledger section only - and scanned for secrets). `bridge_reply.py` (300 lines), `test_bridge_reply.py` (306 lines), `bridge_env.LEDGER_EVENTS = (sent, replied, followup, tier0, tier1, timeout, escalated)` with `ledger_append` refusing anything else. `42 passed in 0.33s` across reply + send; two mutations (followup numbering, event guard) fail 2 tests each. Deltas from the brief, kept: `conversationId` is not in `order.json` - `bridge_send` writes it to `conversation.json` (gemini) / `reply.json` `session_id` (claude), so the resolver falls back through both; send-first-then-record, so a refused send leaves no file, no move, no ledger line. `--packet` takes the full 64-hex id.

### T4: the packet contract (HG1)
- Status: pending
- Owner: parent (drafts), Astra via the bridge (reviews), operator ratifies
- Depends on: T1-T3
- Write set: `docs/runbooks/BRIDGE-PACKET.md`
- Acceptance: the doc names the fields, caps, reply grammar, lane register and the file-AND-send rule; Astra's review packet returns no material disagreement or its disagreements are resolved in the doc
- Validate: `rg -c "packetId|POSITION|NOT FOUND WHERE I LOOKED" docs/runbooks/BRIDGE-PACKET.md`
- Evidence: pending

### T5: pointers and the first live order (HG2)
- Status: complete (HG2 done; the hand procedure is replaced)
- Owner: parent
- Depends on: T4
- Write set: `GEMINI.md`, `docs/runbooks/HANDOFF-ASTRA-GEMINI-2026-09-05.md`, `evals/RETRIEVAL-BENCHMARK-2026-09-05.md` (a bridge round: seconds and turns to a usable reply)
- Acceptance: the hand procedure is replaced by the three commands; one live order sent, watched and ledgered with the tools
- Validate: `python content/video_engine/scripts/bridge_watch.py --lane gemini --id <new> ` exits done
- Evidence: 2026-09-06 15:52-16:22, the first live orders through the tools (HG2, operator: "you can write the work order to Gemini for the cut review"). Order 1 (Wealth Logic cuts, report-landed, conversation 12655d39): sent -> reply landed by the daemon in 241 s -> tier 0 closed it with no model; the parent found the report was an honest abstention, tier 0 gained the `verdict-verified` rule; a follow-up with the video on disk went out by `bridge_reply` on the same conversation (followup 1) and the second reply landed; its content is contradicted by the parent's spot check and is being re-measured by our own tool (TR-1). Order 2 (profiles on the flash tier, paths-written, conversation a3c4ce5c): reply landed in 3.7 min; tier 0 failed on a half-path from a transcript-truncated reply; **the first tier-1 run** (`bridge_handler`, 16:19:57-16:22:04, $0.54, 6134 output tokens) verified all 30 copies on disk, named the truncation as the cause, decided done. Defects found and fixed the same hour: cp1252 console (UTF-8 reconfigure), conversation id recovery (brain-transcript fallback on the brief's first line), claude.CMD resolution for tier 1, markdown-link paths, truncated replies, prior-verdict moves. GEMINI.md and memory carry the commands. Bridge ledger: `evals/BRIDGE-LOG.jsonl`.

### T6: Landed replies become actionable without the operator - Python first, a model only for the residue (2026-09-06)
- Status: complete
- Owner: implementation_luna (daemon, handlers, hook), parent (the residue handler's instruction), operator (grace window, SLA, residue budget)
- Depends on: T1-T3
- Write set: `content/video_engine/scripts/bridge_daemon.py`, `content/video_engine/scripts/bridge_handlers.py` (+ tests), `~/.claude/hooks/bridge_inbox.py` (UserPromptSubmit + SessionStart: prints "N bridge replies waiting: <packetId lane first-line>" when `replied/` is non-empty, nothing otherwise), `docs/runbooks/BRIDGE-REPLY-HANDLER.md` (the standing instruction for the residue run only), a Task Scheduler entry at logon (documented, operator-installed), `.gitignore`
- Handler tiers: **tier 0, deterministic, zero tokens** - a handler registry keyed by the order's `replyShape`: `paths-written` (every path the reply names exists and, when the order named a marker, contains it), `contract-block` (a named block is present at the source and every synced copy), `report-landed` (the report is under `docs/research/<area>/`, has the proof lines and the NOT FOUND block, `build_docs_layers.py --write` then `--check` green), `review` (the POSITION / DISAGREEMENTS grammar parses; no disagreement → done, disagreements → residue), `test-run` (the named command exits 0). A tier-0 pass marks `done/` and appends the ledger with `tier: 0`. **Tier 1, the residue** - only a reply that fails its tier-0 check, parses with disagreements, or carries a decision goes to a model: a headless run of the named `bridge_handler` role (`.claude/agents/bridge_handler.md`: Read/Grep/Glob/Bash, Opus at effort high, maxTurns 20, no skills, no memory - the ~6k floor after tonight's cuts, not the explorer's; Opus not Sonnet because the residue is judgment by definition and round 3 showed Sonnet no cheaper per dispatch and confidently wrong on labels - revisit if the ledger's escape rate proves mostly mechanical), with the order, the reply, the tier-0 failure and the standing instruction; ledger `tier: 1` with its usage
- Acceptance: (1) live session: a landed reply is announced on the very next prompt with no tokens spent before it; (2) unattended: tier 0 handles the four known shapes on synthetic and on tonight's real reply (7aaa9146: `paths-written` + `contract-block` pass without a model); (3) a reply past the grace window that tier 0 cannot close is dispatched to tier 1 exactly once and lands in `done/`; (4) a reply still open past the SLA raises one desktop toast; (5) the daemon is idempotent across restarts (folder state + pid lock), makes no model call itself, and stops dispatching tier 1 when the daily residue budget (count and token cap in a config file) is spent - then it toasts instead; (6) the ledger's tier column makes the escape rate measurable
- Validate: `python -m pytest content/video_engine/tests/test_bridge_daemon.py content/video_engine/tests/test_bridge_handlers.py -q -p no:cacheprovider`; then `python content/video_engine/scripts/bridge_handlers.py --replay 7aaa9146-88f1-4f03-b004-d5bdf18a5492` exits done at tier 0
- Evidence: 2026-09-06 (implementation_luna; parent re-ran the five suites - `108 passed in 1.42s` - read the watcher diff, ran the dry tick and the hook pipe test, then registered the hook). `bridge_daemon.py` (616), `bridge_handlers.py` (431), `test_bridge_daemon.py` (22 tests), `test_bridge_handlers.py` (26), `~/.claude/hooks/bridge_inbox.py` (108; UserPromptSubmit + SessionStart, empty stdout on a quiet day), `docs/runbooks/BRIDGE-DAEMON.md` (config keys, Task Scheduler entry, ledger tier column). HG3 defaults in the module: grace 10 min, SLA 60 min, residue 6 runs / 200k tokens per day, override `~/.claude/bridge-config.json`. Acceptance 2 on the real reply: `bridge_handlers.py --replay 7aaa9146…` → `paths-written | pass True | checks 18` with no model (`contract-block` on that reply not asserted: no such order exists on disk and one was not invented). Watcher fixes folded in: `--once` (one read, deadline binds; `--replay` could never time out) and no `timeout` ledger line for a `working` read (a 60 s tick would have written one per minute). Follow-up packets are routed on the presence of `conversationId` (`order.json` has no `from` field). `costUsd` not `…Token`-suffixed because `_is_secret_key` refuses keys ending in `token`. The dry-run probe packet and `bridge-dryrun.md` were deleted by the parent so the first real tick has nothing to send. Nothing installed in Task Scheduler; the operator installs the documented entry when ready.

### T7: Tier 0 as the contract both sides run - failure classes, the repair round, the order's roots and verify command, the check CLI (2026-09-07)
- Status: complete
- Owner: parent
- Depends on: T6
- Write set: `content/video_engine/scripts/bridge_handlers.py` (`failure_class` form | substance, `order_roots`, `check_verify`, `TEMPLATES` / `template`, relative paths as list items), `bridge_check.py` (new CLI: `--shape` order-less | `--packet`, `--template`), `bridge_send.py` (`--root`, `--verify`, the block appended to every brief; the packet id stays the hash of the brief as written), `bridge_daemon.py` (step 3b: `queue_repair` / `close_repaired`, tier 1 skips an original waiting on its repair, the `tier1` ledger row carries `reason: <class>:<check>` and `repairs`), `bridge_env.py` (`repair`, `repaired` ledger events), `docs/runbooks/BRIDGE-DAEMON.md` §1, `BRIDGE-PACKET.md` §1-2, `GEMINI.md` (run the check before replying), tests `test_bridge_check.py`
- Acceptance: the operator's calls of 2026-09-07 on the tier-1 rate - (2) Gemini gets tier 0 itself: one CLI both sides run, order-less when the operator prompted Gemini directly; (3) the repair round: a FORM failure earns one follow-up at zero Claude tokens asking for the block restated, never for evidence, before tier 1; (5) the order's roots resolve a path in another repo; (6) the order's own verify command is a substance check run after the form passes; (7) REJECTED - no evidence-density quota ("gets Gemini to write us bad numbers"); the grammar block rides every order as a template but is not the enforcement - the CLI is
- Validate: `python -m pytest content/video_engine/tests/test_bridge_check.py content/video_engine/tests/test_bridge_handlers.py content/video_engine/tests/test_bridge_daemon.py content/video_engine/tests/test_bridge_send.py content/video_engine/tests/test_bridge_reply.py content/video_engine/tests/test_bridge_watch.py -q -p no:cacheprovider`
- Evidence: 2026-09-07 - 127 passed (13 new: the first failing check names the class; a relative path resolves under a named root and not without; the verify command runs only after the form passes and its failure is substance; the block carries the five heads; the CLI passes a good reply order-less and prints the block on a bad one, reads the order by packet, prints a template; bridge_send appends the block once and carries roots/verify, an order without them compiles as before; the daemon queues ONE repair on a form failure with the original's conversation, roots and shape, tier 1 waits, a second tick queues nothing; a substance failure goes to tier 1 with `reason: substance:...` and never a repair; a passing repair closes the original (`repaired`); a failing repair reaches tier 1 with `reason: form:...` and is never repaired again; a form failure with no conversation queues nothing). Smoke on the two 2026-09-06 form failures that cost tier-1 runs: ce6f85e7 (paths under another root) and a9bdaca8 - see the transcript. The daemon restarted on the new modules (pid 9988, 02:37). Deviation, stated: the research profiles at their source (the trades repo) do not yet carry the "run bridge_check before replying" line - GEMINI.md does; the profile line is a one-line Gemini order when the operator wants it.

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

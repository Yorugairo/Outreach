# Twenty vs n8n vs Attio: Workflow Fit Evaluation

*Generated 2026-08-24 · ~60 sources across tavily + exa · Confidence: High on pricing/licensing (primary sources), Medium on operational claims (vendor-adjacent blogs, flagged inline)*

## Executive summary

Three tools, three different seams, three different answers.

- **n8n — no, for the pipeline.** Its two most-needed nodes are security-disabled by default in v2, its Python story regressed, and Git source control is paywalled at ~€667/mo, which collides directly with this repo's everything-in-git discipline. The one thing it does exceptionally well (human-in-the-loop approvals) is the one thing already built here.
- **A CRM — yes, but only one seam of it, and not yet.** `SEOTarget` + `InsightReport` are proto-CRM rows with no pipeline around them. That gap is real. At one-operator volume it is not yet expensive.
- **Attio over Twenty, if and when.** Twenty's data model is the better fit on paper; its upgrade fragility is a real tax on a solo operator, evidenced by maintainer statements, not just reviews.

**Do not** put video-engine entities (claims, evidence, plates) in either CRM. They are already schema'd, sha256-bound and git-versioned — a CRM is a strictly worse home.

---

## The three seams

| Seam | State today | Candidate | Verdict |
|---|---|---|---|
| prospect → outreach → reply → won | **missing entirely** | Twenty / Attio | real gap, defer until volume justifies |
| generated → notified → approved | watchdog + Telegram + paid gate, **working** | n8n | do not replace working code |
| claim → generation → paid gate | bespoke, sha-bound, git-versioned | none | keep in-repo |

---

## 1. n8n — the clearest answer

### Licensing is fine for this use

Not OSI open source; it is the [Sustainable Use License](https://github.com/n8n-io/n8n/blob/master/LICENSE.md) ("fair-code"). Internal business use, self-hosted, free and uncapped. Commercial licence is triggered by white-labelling, hosting n8n *for others*, or embedding it in a product. None applies here. Two carve-outs worth knowing: non-`master` branches are unlicensed, and `.ee.` files require an Enterprise licence.

### But the fit is poor, and structurally so

1. **The two nodes you would actually need are disabled by default since v2.0.** [Execute Command](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/) and [Local File Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.localfiletrigger/) — the filesystem-watch + run-a-script pair that would drive a local Python pipeline — are off by default because they "pose security risks", and are unavailable on Cloud entirely ([v2.0 breaking changes](https://docs.n8n.io/changelog/v20-breaking-changes)).
2. **Python regressed.** Pyodide is gone; native Python now needs an **external task runner** in a separate container image, with packages allowlisted via `n8n-task-runners.json` ([docs](https://docs.n8n.io/build/code-in-n8n/using-the-code-node)). No imports at all on Cloud.
3. **Git source control is Business/Enterprise only** ([docs](https://docs.n8n.io/source-control-environments/)) — ~€667/mo. Community edition has none. Workflows are JSON, but node IDs and x/y positions churn, so a logic change hides in layout noise.
4. **No unit tests.** The [ForgeFlow migration writeup](https://dev.to/josephyeo/we-didnt-migrate-from-n8n-to-python-because-n8n-failed-k9j) frames the forcing question well: *"Can we write a unit test for this logic?"* — with a node graph, usually no.

### What it genuinely does better than anything you'd build

Human-in-the-loop. `Send and Wait for Response` exists across Telegram, Slack, Gmail, Discord and more, with approval buttons, free text, or an editable pre-filled form. Waiting executions **offload state to the database**, so a pending approval survives a restart ([Wait node docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.wait/)).

That is precisely the seam already covered by `watchdog/telegram_approve.py` and `paid_gate.py`.

### The decision rule from the field

Independent practitioners converge hard here. [Edward Chalupa](https://echalupa.com/blog/n8n-silent-failure-docker-networking) found a 17-node workflow **silently broken for weeks** and replaced it with 80 lines of Python on cron. [Build Daily](https://builddaily.io/posts/when-to-reach-for-n8n-vs-writing-the-orchestrator-yourself/) puts it bluntly:

> *"If every node is a Code node, you don't need n8n — you need a script."*
> *"The n8n mistake is harder to recover from... If you're not sure, start in code — it's cheaper to move from code to n8n than the reverse."*

⚠️ Two critical RCE CVEs were reportedly disclosed ~Mar 2026 (shell injection via public form inputs, expression-sandbox escape). Sourced only via a social post — **verify CVE IDs directly before relying on this**.

---

## 2. Attio — managed, metered, capable

**Pricing rose ~21% in July 2026.** Nearly every comparison article still quotes the old numbers. Live from [attio.com/pricing](https://attio.com/pricing):

| Plan | Annual /user/mo | Seats | Objects | Records | Credits/mo |
|---|---|---|---|---|---|
| Free | $0 | 3 | 3 | 50,000 | 250 |
| Plus | **$35** (was $29) | 10 | 5 | 250,000 | 1,500 |
| Pro | **$79** (was $69) | ∞ | 12 | 1,000,000 | 10,000 |

**The important structural fact: API, webhooks, MCP server, Workflows and AI agents are on _all_ tiers including Free.** AI is metered by credits, not gated by plan. So a Free workspace is a genuine technical trial, not a crippled demo.

- **Data model**: objects + 17 attribute types incl. bidirectional record references; custom objects are first-class ([docs](https://docs.attio.com/docs/objects-and-lists)). But object count is **metered by tier** — the "flexible data model" is real and rationed.
- **API**: `api.attio.com/v2`, OAuth2 + scoped keys, **100 req/s read / 25 req/s write**, HMAC-signed webhooks with ~10 retries over 3 days ([rate limits](https://docs.attio.com/rest-api/guides/rate-limiting)).
- **Official MCP server** at `mcp.attio.com/mcp`, OAuth-only, reads auto-approve and writes prompt for confirmation ([MCP overview](https://docs.attio.com/mcp/overview)).
- **No self-hosting, ever.** Managed SaaS only.

**Honest limitations**, recurring across independent reviews: reporting depth is the consistent gap (report counts hard-capped 3/15/100); **AI credit metering is the loudest 2026 complaint**, with heavy users reportedly exceeding seat cost; no mixed seating (every seat on one plan); no SLA below Enterprise. The July price rise is itself a live example of the lock-in risk.

---

## 3. Twenty — the better data model, the worse operations

### Genuinely strong where it matters here

**Schema-per-tenant with auto-generated API.** Per [official docs](https://docs.twenty.com/developers/extend/api): add a custom object and *"it immediately gets REST and GraphQL endpoints identical to built-in objects."* The **metadata API is writable** — objects, fields and relations can be created programmatically, so an ontology can be defined in code and versioned in git. Custom objects are not second-class (unlike HubSpot, where they are Enterprise-gated).

Backed by $5M seed (Nov 2024, Runa Capital, YC S23); ~55k GitHub stars; 2.0 shipped Apr 2026 adding an app framework, git-backed workspace versioning and native MCP.

### The operational risk is real and first-party evidenced

**Upgrades must step through every minor version. Skipping corrupts the workspace.** Maintainer, on [#9419](https://github.com/twentyhq/twenty/issues/9419):

> *"Yes this is very painful but that's the way to do it right now, sorry :(."*

[#19863](https://github.com/twentyhq/twenty/issues/19863) documents a v1.21→v1.23 jump producing a non-idempotent `ALTER TABLE` that deadlocked migrations into a crash-restart loop, recovered only with manual SQL and `sed`-patching compiled migrations inside the container. On [#14907](https://github.com/twentyhq/twenty/issues/14907) a maintainer told a user who hand-edited the version row: *"By doing so you corrupted your twenty instance."*

Reportedly improved in 2.x — one hosting vendor says cross-version jumps now work — but **no 2.x-era post-mortem confirms it at scale**. Treat as claimed-but-unverified.

Other costs: **community-only support** for self-hosters, ~2 vCPU / 4 GB RAM, `SERVER_URL` misconfiguration is the top support issue, thin reporting, no email sequences, no marketing automation, no mobile app.

### Licensing: three-way split

[AGPLv3](https://github.com/twentyhq/twenty/blob/main/LICENSE) core · commercial licence for `@license Enterprise` files · MIT for SDKs. Critically, the **Twenty Application Exception** means building against published REST/GraphQL APIs, webhooks or SDKs does **not** make your app AGPL. Fork the core and it does. Self-hosted is free; Organization ($19/user/mo) buys SSO, row-level permissions and audit logs.

---

## Recommendation

**1. Skip n8n.** The evidence is specific, not vibes: the nodes you need are off by default, Python regressed, version control is paywalled above your budget, and the one capability worth having is already built and working. Revisit only if you need approval fan-out across several channels at once.

**2. Do not adopt a CRM this week.** The gap is real but not yet costly. `SEOTarget` and `InsightReport` sit behind an `InsightRepository` Protocol — which is, conveniently, the clean seam for adding one later as another implementation rather than a migration.

**3. When you do, trial Attio Free first.** 3 seats / 3 objects / 50k records with **full API, webhooks and MCP** is enough to model target → report → touch and see whether a CRM changes behaviour. Zero ops cost. If it proves out and you need >12 objects or self-hosting, *then* weigh Twenty knowing the upgrade tax.

**4. Keep video-engine entities out of both.** Claims, evidence and plates are sha256-bound, schema-validated and git-versioned. A CRM would weaken every one of those properties.

### The asymmetry that decides it

Build Daily's line applies to all three: it is cheaper to move from code to a platform than back. Everything currently in Python — gates, watchdog, claim registry, generators — is testable, diffable and reviewable. n8n would trade all three for a UI. A CRM adds a genuinely missing capability rather than replacing a working one, which is why it's the only one of the three worth eventual adoption.

---

## Gaps in this research

- Twenty 2.x multi-version upgrade reliability at scale — **no post-mortem found**.
- Twenty native MCP on **self-hosted** (all official language says "Cloud workspace") — unconfirmed either way.
- n8n Enterprise list pricing — unpublished; one community figure of ~$2–3k/mo is single-source.
- The March 2026 n8n RCE CVE identifiers — verify independently.
- Attio export scope/format — the help article 404'd; REST API is a viable programmatic path regardless.
- Whether first-party n8n/Make apps for Attio exist, or only community REST integrations.

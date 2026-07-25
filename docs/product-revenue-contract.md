# Product / Revenue Contract: SEO Insight Run

## Product goal

The `SEO Insight Run` is a **value-first outreach intelligence asset**, not a subscription product. Given a qualified business, URL, or normalized entity, it produces a deterministic, evidence-backed answer to:

> What is wrong with this prospect's search presence, why does it matter, and what would we fix for them?

Its commercial purpose is to improve prospect selection, outreach relevance, discovery calls, and proposals for downstream services. Subscriptions are not the primary design assumption. The durable product boundary remains the persisted run and its evidence; the commercial layer packages that truth for a specific prospect without changing it.

## Primary downstream service packages

Each recommendation must map to one or more services that can actually resolve the observed problem:

1. **Web development / rebuild** — site structure, technical remediation, conversion-oriented pages, metadata and schema implementation, internal linking, sitemap and indexability fixes, and full rebuilds when the current platform cannot support the required work.
2. **Profile management / reputation** — business profile completeness and consistency, review/reputation workflows, local presence hygiene, and aligned on-site trust signals.
3. **pSEO / search architecture** — programmatic SEO opportunity design, service/location and other search-intent page systems, taxonomy, templates, internal-link architecture, sitemap architecture, and governed publishing plans.

A package recommendation is an evidence-based routing decision, not a forced upsell. If the run does not support a service package, it must not recommend it.

### Evidence gates by service package

- **Web development / rebuild** may be routed from persisted site evidence such as validated sitemap state, fetched page records, metadata and heading defects, canonical/indexability facts, schema, internal linking, or reproducible fetch failures.
- **Profile management / reputation** requires persisted profile-specific evidence (for example, business-profile completeness, NAP inconsistency, review/reputation facts, or a profile-to-site mismatch) or an explicit operator-supplied evidence record with provenance. Website crawl evidence alone cannot route this package.
- **pSEO / search architecture** requires target-specific demand evidence plus a demonstrated systematic service/location/taxonomy coverage gap and sufficient crawl coverage. A small crawl sample, URL classification, missing metadata, or unknown search visibility cannot route this package.
- A combined package is allowed only when every included service independently passes its own evidence gate. Otherwise the route is `none` or remains pending operator evidence.

## Operator workflow

1. **Select a target** — choose a qualified prospect using business fit, serviceability, and reachable decision-maker criteria; do not audit indiscriminately.
2. **Create an SEO Insight Run** — normalize the target, set market/device/scope, and record limits and paid-data approval.
3. **Collect deterministic evidence** — validate sitemaps and crawl state, fetch pages, extract page facts, classify coverage, and collect target-specific search evidence where available.
4. **Validate the audit** — distinguish successful artifact production from semantic validity; suppress unsupported conclusions and mark incomplete evidence as unknown or warning states.
5. **Assemble the outreach package** — lead with an executive answer, identify the highest-value observed problems, explain why they matter, state what we would fix, attach evidence and confidence, estimate effort, and route the opportunity to a relevant service package.
6. **Operator review and correction** — a human approves the target, claims, framing, contact route, and package fit. Corrections are recorded for quality measurement.
7. **Send personalized outreach** — the operator uses the approved package to deliver a concise, prospect-specific message and supporting artifact. The platform does not automate outbound in v1.
8. **Handle the response** — answer questions from the same evidence, capture positive replies, and book a discovery call.
9. **Convert to a scoped proposal** — confirm needs on the call, then propose web development, profile management, pSEO, or a justified combination. Closed revenue is attributed to the originating run and service package.

The intended funnel is: **target selection -> valid audit -> evidence-backed outreach package -> operator-approved outreach -> positive reply -> booked call -> proposal -> closed revenue**.

## Hard truth rules

These rules are contractual and fail closed:

- **No fabricated revenue loss.** Never invent traffic, lead, conversion, or revenue-loss figures. Financial impact may be stated only when supported by disclosed inputs and a reproducible method; otherwise describe the observed risk or opportunity without a dollar claim.
- **No configuration-based score penalties.** Missing credentials, unapproved paid calls, unavailable enrichment, crawl limits, or operator settings produce `unknown`, `not collected`, or a completeness warning—not a lower target health score.
- **Every finding is evidence-backed.** Each claim and recommended action must cite persisted source facts or artifacts. Failed fetches, guessed sitemap locations, generic best practices, and model assertions are not target findings.
- **Deterministic before generative.** Collection, validation, classification, scoring, confidence, and recommendation eligibility are deterministic. A generative layer may summarize or rephrase approved findings, but it may not create facts, scores, evidence, impact claims, or service recommendations.
- **Unknown is better than wrong.** Insufficient or contradictory evidence must reduce confidence, trigger review, or suppress the finding.
- **Commercial framing cannot rewrite technical truth.** Outreach packaging may prioritize findings for relevance, but it may not exaggerate severity or conceal limitations to manufacture demand.

### Evidence and score boundaries

- A target-level metadata score may use only the primary requested URL. Secondary pages collected under `max_pages` may produce page-specific findings, but changing the sample limit or composition must not change target health.
- Sitemap absence is a target finding only when a persisted candidate was actually checked and returned conclusive absence or invalidity evidence. No candidate, timeout, access denial, or other inconclusive collection result is an evidence limit, not a defect.
- Search visibility evidence is target-specific only when its domain matches the run target and it includes a valid snapshot date, market/location, language, device, source, and observed ranking URLs belonging to that target. A score-like value without this context is unknown.
- Finding provenance must resolve to an independently persisted run artifact and exact observed field. A report cannot prove its own claims by citing itself.
- Every commercial finding is typed as either `prospect_issue` or `evidence_limit`. Evidence limits are displayed separately for operator review, cannot recommend a service, and cannot become the next best commercial action.

## Outreach package / output structure

Every approved package must contain:

| Field | Required content |
|---|---|
| **Executive answer** | A concise, prospect-specific answer summarizing the strongest supported issue and opportunity. |
| **What is wrong** | One or more concrete `prospect_issue` findings, separated from unknowns and general advice. |
| **Why it matters** | The likely search, crawl, visibility, trust, or conversion consequence, calibrated to the available evidence and without fabricated revenue loss. |
| **What we would fix** | Specific remediation scope phrased as work we can perform, not merely a diagnostic label. |
| **Evidence** | Direct evidence references, source URLs/artifact IDs, observations, timestamps, and relevant market/device context. |
| **Confidence** | A defined confidence level with reason, including completeness or contradiction warnings. |
| **Effort** | A bounded relative estimate such as small, medium, large, or discovery required; assumptions must be explicit. |
| **Recommended service package** | One of web development / rebuild, profile management / reputation, pSEO / search architecture, or a justified combination; `none` when evidence does not support an offer. |
| **Evidence limits (operator review)** | Separately typed collection or completeness gaps, with what remains unknown and how to verify it; never presented as a prospect defect or remediation sale. |

The structured package should be reusable in an operator view, a concise outreach brief, discovery-call preparation, and proposal scoping without losing provenance.

## KPI funnel and unit economics

Measure the commercial system as a funnel, segmented by recommended and sold service package:

1. **Qualified targets** — prospects meeting explicit fit and contactability criteria.
2. **Valid audits** — runs that pass evidence, completeness, and semantic-validity gates.
3. **Outreach sent** — operator-approved packages actually delivered.
4. **Positive replies** — replies expressing relevant interest or requesting more information.
5. **Booked calls** — qualified discovery calls scheduled.
6. **Proposals** — scoped commercial proposals delivered.
7. **Closed revenue by service package** — won revenue attributed separately to web development / rebuild, profile management / reputation, pSEO / search architecture, and justified combinations.

Also track:

- conversion rate between every adjacent funnel stage;
- **cost per outreach package**, including paid data and operator labor;
- **time per outreach package**, including run, review, correction, and assembly time;
- **correction rate**, defined as the share of packages requiring a factual, evidence-linkage, severity, confidence, or service-routing correction before use;
- reason codes for invalid audits, rejected packages, negative replies, lost proposals, and corrections.

Optimize for trustworthy closed revenue and learning by package—not audit volume, score severity, or message volume.

### Minimal activation and attribution record

Commercial measurement uses an append-only `OutreachActivationEvent`; it does not turn this platform into a CRM. Each event must record:

- a unique event ID, the originating `InsightRun` ID, and the immutable outreach-package/report version;
- one stage from `package_approved`, `outreach_sent`, `positive_reply`, `call_booked`, `proposal_sent`, `closed_won`, `closed_lost`, or `correction_recorded`;
- `occurred_at`, operator/source system, an external reference when one exists, routed service packages, and a reason code or correction class where applicable;
- revenue amount and currency only for `closed_won`, copied from an authoritative proposal, invoice, or CRM reference rather than inferred by this platform.

Funnel attribution is first-touch to the originating run/package only when the external opportunity or invoice is explicitly linked. Repeated or out-of-order events remain auditable; dashboards derive current funnel state from the event log rather than overwriting history. Manual import/export is sufficient for v1.

## Explicit v1 exclusions

The following are not primary assumptions or v1 platform responsibilities:

- **Subscriptions are not a primary design assumption.** The platform is not optimized around recurring seats, usage tiers, or self-serve subscription conversion.
- **No automated outbound in v1.** The system may create an operator-reviewed outreach package, but it does not autonomously send email, social messages, or follow-up sequences.
- **No CRM in v1.** It does not replace pipeline/contact management or build heavy CRM workflowing.
- **No competitor intelligence in v1.** Competitor analysis remains optional later enrichment and does not block target-site evidence collection or commercial activation.
- **No generative content production in v1.** It does not generate or publish scaled landing pages, blogs, or other production content. pSEO recommendations describe a potential service scope; they are not a content-generation module.

These exclusions do not prohibit manual export or operator use of an approved package in existing tools. They preserve a narrow v1: deterministic SEO evidence first, human-reviewed outreach intelligence second, and downstream service delivery after qualification.

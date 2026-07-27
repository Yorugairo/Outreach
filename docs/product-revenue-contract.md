# Product / Revenue Contract: Outreach Program

## Product goal

The Outreach Program is an internal, URL-first expertise demonstration. An
operator pastes a business website URL and receives a concise,
evidence-backed conversation starter:

> What did we observe, why may it matter, and is there enough value to start a
> conversation?

The audit opens the door. It is not the product being sold, a generic score
pitch, or an offer to construct a separate pSEO system for the prospect.
Technical evidence remains immutable and commercial framing remains a
human-reviewed downstream object.

## Owned vertical products

- **One Trade Network** is the owned discovery/pSEO property for home-service
  trades.
- **National BJJ Registry** is the owned discovery/pSEO property for BJJ
  academies.

The target business does not own or commission these pSEO systems. Outreach
may show how the business can benefit from the appropriate owned vertical
property.

## Primary service packages

Each vertical pack exposes the same three commercial paths with
vertical-specific implementation:

1. **Improve the existing website + sitemap/SEO + vertical visibility** —
   improve design, conversion clarity, sitemap/search fundamentals, and
   technical SEO on the prospect's current site while leveraging the relevant
   owned vertical pSEO property.
2. **Vertical plugin/embed upgrades** — add owned, vertical-specific
   functionality to the prospect's current website through supported plugins
   or embeds.
3. **Custom website + optional CRM/SaaS** — onboard the business to a custom
   vertical website, with the relevant CRM/SaaS bundle offered as an option.

Audit evidence describes observed website conditions. Qualification and
operator review determine which product path is appropriate. A technical
finding must never be rewritten as proof that a prospect needs all three
packages.

## Default operator workflow

1. Paste a URL and run the scan with safe defaults.
2. Review the concise opportunity brief and its evidence limits.
3. If the target is worth pursuing, associate or create a qualified prospect.
4. Create and human-review an outreach package.
5. Export a short elevator pitch and evidence brief for manual outreach.
6. Record sent, reply, call, proposal, and revenue outcomes as append-only
   activation events.

CSV intake, run history, comparisons, package administration, and funnel
entry are secondary operator tools. They must not obstruct the URL-first scan.

## Outreach package promise

Every approved package contains:

- a concise executive answer;
- the strongest supported observation and why it may matter;
- direct references to independently persisted evidence;
- confidence, effort, and evidence limits;
- a short invitation to receive or discuss the evidence brief;
- the relevant vertical platform and the three available commercial paths.

The legacy `what_we_would_fix` and `recommended_service_package` fields remain
in the persisted contract for compatibility. In new packages they represent
the proposed conversation/delivery path, not proof that the operator will
build client pSEO.

## Hard truth rules

- Never fabricate traffic, leads, conversion, or revenue loss.
- Missing credentials, unapproved paid calls, unavailable enrichment, and
  crawl limits are evidence limits, not score penalties.
- Every website claim resolves to an independently persisted artifact.
- Collection, validation, scoring, and recommendation eligibility are
  deterministic.
- Insufficient evidence reduces confidence or suppresses a claim.
- Commercial framing cannot exaggerate technical truth.
- Coverage analysis is internal research context. Any pSEO leverage offered to
  a prospect comes from One Trade Network or National BJJ Registry.
- Operators approve all outbound copy. The platform does not send messages.

## Activation and attribution

Commercial measurement uses append-only `OutreachActivationEvent` records:
`package_approved`, `outreach_sent`, `positive_reply`, `call_booked`,
`proposal_sent`, `closed_won`, `closed_lost`, and `correction_recorded`.
Revenue is permitted only on `closed_won`.

Measure qualified-to-approved, approved-to-sent, positive reply, booked call,
proposal, and closed-won rates by vertical and service package. Also measure
audit cost, operator review time, and factual correction rate.

## Explicit milestone exclusions

- no automated outbound or autonomous follow-up;
- no CRM replacement inside the Outreach Program;
- no generative publishing or client pSEO construction;
- no billing, multi-tenancy, or customer-facing audit SaaS;
- no autonomous or score-changing competitor intelligence. The optional Tacoma
  BJJ market-evidence pilot is operator-gated, bounded, separately persisted,
  and may only support attributable comparison statements.

## Optional market-evidence outreach

An approved `v3` outreach package may snapshot up to three strongest
market-evidence gaps plus screenshot metadata. Approval and export revalidate
the immutable market-run hash, every JSON evidence reference, and every PNG
hash. The email opener uses one verified observation; numeric SEO/AI scores,
competitor accusations, and ranking promises remain ineligible as the opening
claim.

## Demand and commercial opportunity

Demand and revenue forecasts are downstream, immutable model versions. They do
not change the website, SEO, AI Readiness, ranking, Maps, authority, or
competitor evidence that supplied their context.

- Keyword-tool volume is labeled **monthly search occasions**, never unique
  people.
- Every demand row belongs to one reviewed intent/close-variant group before it
  can enter arithmetic. The safe default is the maximum observed close-variant
  value; summing distinct intents requires explicit operator review.
- Brand and lineage demand is reported separately and excluded from net-new
  opportunity by default.
- Unique prospects are a low/base/high modeled range using an explicit
  searches-per-prospect divisor.
- Business price, capacity, retention, and funnel inputs carry field-level
  provenance: operator-observed, business-supplied, assumed, or aggregate
  calibration.
- Forecasts are always labeled `Forecast, not guarantee` and use
  `opportunity-formula.v1`.
- Acquisition projections are suppressed when demand or material funnel inputs
  are unresolved. A known capacity ceiling may still be displayed on its own.
- Active-customer output is capped by reviewed capacity. Nova Ryu's current
  fixture is `$100/month × 20 spots = $2,000 additional MRR / $24,000 annual
  run-rate`; this is a capacity ceiling, not promised ranking revenue.

Service levers remain sequential:

1. visibility can create qualified visits;
2. a plugin/embed can improve visitor-to-signup or visitor-to-lead conversion;
3. CRM/SaaS follow-up can improve attendance and close rates.

The product does not add these effects as independent gains. Revenue values
remain out of the cold-email opening and require an approved opportunity
scenario before pitch export.

## Provider recovery truth

Each paid operation records provider, operation, query/target, market context,
attempt, status, failure class, retryability, actual cost, raw artifact
reference, timestamps, and predecessor call when evidence is reused.
Authentication and balance/payment failures stop the paid queue. Call count
does not prove completeness: required successful, unresolved, inapplicable, and
reused evidence is reconciled by operation. A run with unresolved required work
is `partial`.

Retrying creates an immutable `resume_unresolved` successor. Successful
same-context evidence is reused by reference and only unresolved retryable work
is scheduled. Historical provider artifacts and costs are never rewritten.

## Aggregate calibration

Calibration accepts only aggregate period counts from operator-uploaded Google
Ads, GA4, Search Console, signup, trial, appointment, customer, or spend CSVs.
Raw names, email addresses, phone numbers, and other lead identity are rejected.
Observed conversion rates create a successor calibrated forecast; the original
forecast remains attributable and unchanged.

## Demand-conversion evidence modes

`demand-conversion.v1` is a separate commercial evidence contract. It never
changes SEO, AI Readiness, conversion-readiness, visibility, or authority
scores.

- **Prospect mode** may use approved keyword/demand imports, public crawl and
  ranking observations, relative trend evidence, and clearly labeled
  third-party estimates. It cannot reference owner-first-party snapshots.
- **Owner-verified mode** requires explicit authorization and at least one
  context-matched aggregate Search Console, GA4, GBP, or booking/CRM snapshot.
  Raw credentials and lead identity remain prohibited.

The evidence hierarchy is:

1. owner-first-party observations;
2. operator-supplied business facts;
3. approved market evidence;
4. public observations;
5. provider-specific third-party estimates;
6. scenario assumptions and deterministic models.

Every claim carries an independent provenance label: `observed`, `supplied`,
`assumed`, or `modeled`. Search-volume rows remain search occasions. They are
grouped by reviewed intent/close-variant rules and are never presented as
unique people or unique searchers.

The versioned demand-to-conversion formula is:

```text
incremental_members =
  min(
    incremental_qualified_visits * lead_rate * booking_rate * close_rate,
    available_capacity
  )

incremental_recurring_revenue =
  incremental_members * monthly_price
```

Low/base/high scenarios must preserve their input provenance, confidence,
completeness, capacity ceiling, and `Forecast, not guarantee` language.

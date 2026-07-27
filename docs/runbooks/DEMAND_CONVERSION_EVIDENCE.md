# Demand-to-conversion evidence runbook

Use this layer to estimate a bounded commercial opportunity, not to promise
rankings, traffic, leads, or revenue. The URL scan remains the default action;
imports and owner verification are secondary operator steps.

## Prospect mode

1. Complete an Insight Run for the qualified prospect.
2. Import and approve demand rows after close-variant and intent review.
3. Approve business-supplied price and capacity facts.
4. Optionally import an approved relative Trends snapshot.
5. Review low/base/high capture and funnel assumptions.
6. Build, review, and approve the demand-conversion evidence.
7. Export only after reference validation succeeds.

Prospect reports may use public observations, approved market estimates,
business-supplied facts, and reviewed assumptions. They must not read or imply
owner-first-party data. Search volumes are monthly search occasions, not people.

## Owner-verified mode

1. Obtain explicit owner authorization for aggregate exports.
2. Export aggregates only; never accept credentials or row-level names,
   emails, phone numbers, bookings, or customer records.
3. Preview each Search Console, GBP, GA4, or CRM CSV. Confirm prospect,
   vertical, market/property, period, and freshness.
4. Commit immutable source snapshots and approve a conversion-event map.
5. Build owner-verified evidence using exact snapshot IDs.
6. Confirm observed baseline metrics remain separate from modeled lift.
7. Revalidate the owner-mode report immediately before client export.

Owner data never upgrades an existing prospect report silently. Each approval
creates a successor evidence version and an evidence-scoped report snapshot.

## Review and corrections

- Reject or supersede the draft when a source, grouping, price, capacity, event
  mapping, or assumption is wrong; do not edit persisted artifacts.
- Record the correction in the replacement input/review record and retain the
  predecessor ID.
- Treat stale, missing, mismatched, or unavailable inputs as evidence limits.
  Unknown values are excluded from arithmetic rather than converted to zero.
- Confirm every exported claim resolves to the report snapshot, a persisted
  source snapshot, or a validated run artifact.

## Formula and interpretation

The current formula is `demand-conversion-formula.v1`:

`incremental_members = min(incremental_qualified_visits × lead_rate × booking_rate × close_rate, available_capacity)`

`incremental_recurring_revenue = incremental_members × monthly_price`

Low/base/high ranges are capacity-bound scenarios. They do not establish
causality and are labeled “Forecast, not guarantee.”

## Release check

Run:

```bash
python -m pytest tests/test_demand_conversion_pilot.py -q
python -m pytest -q
python scripts/prp_validate.py .claude/PRPs/plans/P11-DEMAND-CONVERSION-EVIDENCE-MODES.plan.md
python scripts/agent_tooling_doctor.py
```

---
name: elite-cro-and-marketing
description: Use when building funnels, landing pages, or conversion flows. Enforces elite conversion rate optimization, frictionless UX, data instrumentation, and persuasive microcopy.
---

# Elite CRO & Marketing

When tasked with building or optimizing funnels, landing pages, or high-value conversion zones, follow these strict Conversion Rate Optimization (CRO) and marketing guidelines.

## 1. Data-Driven Foundation
- **Hypothesis-Led Testing:** Never design blind variations. All interactive changes in conversion zones must be driven by a hypothesis (e.g., "Increasing trust badge visibility near the waiver will reduce drop-off").
- **Server-Side Preference (SEO Synergy):** Protect strict Core Web Vitals (INP/LCP) by avoiding heavy third-party client-side pixels. Rely heavily on the existing `analytics_internal` time-series architecture and server-side conversion anchors for data collection.

## 2. Frictionless UX & Unified Funnels
- **Collapse the Funnel:** Minimize the clicks required to convert. For WaaS and Registry claims, merge content directly with checkout/signup mechanisms where possible.
- **Mobile-First Mandatory:** Prioritize "thumb-friendly" designs. Implement sticky conversion bars (e.g., sticky "Claim Gym" or "Sign Waiver" bars) on mobile viewports.
- **Guided Focus (Design Synergy):** Use micro-animations strictly to guide user attention toward conversion paths. In high-friction zones (waivers, checkouts), ruthlessly eliminate visual noise.

## 3. Trust & Authority Architecture
- **Strategic Placement:** Instantly communicate value and bolster trust. Leverage the specific Registry trust system (badges, "Verified by..." claims) placing them at maximum points of friction (e.g., adjacent to credit card fields or PII collection forms).
- **Privacy Transparency:** Ensure any personalization (like dynamic region-based routing) is transparent and privacy-conscious to maintain user trust.

## 4. Elite Persuasive Microcopy
- **Benefit-Driven Action:** Ban passive verbs (e.g., "Submit", "Click Here"). Enforce high-intent, benefit-driven CTAs (e.g., "Claim Your Academy", "Sign Universal Waiver").
- **Information Scent:** Ensure the language used in SEO meta descriptions perfectly matches the headline on the landing page to carry the user's intent cleanly through to the conversion point.

## 5. Self-Serve & B2B Maturity
- **Interactive Enablement:** For GoBJJ SaaS modules, provide self-serve interactive elements (ROI calculators, clear tiered feature comparisons, "Build Your Own Bundle" configurators) to enable the buyer journey before they ever hit a signup wall.

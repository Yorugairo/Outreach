# Accretive Revenue: Research Report & Strategic Assessment

*Generated 2026-07-28 · Sources: ~90 across three parallel research streams + repo audit · Confidence: High on market evidence, High on the repo finding, Medium on the BJJ monetization section (one research stream still outstanding at time of writing)*

---

## Executive Summary

You have built a complete, working revenue machine and never switched it on. Plans P3–P12 are
all marked `complete` — revenue engine, AI-readiness scoring, demand-to-revenue opportunity
engine, conversion readiness, vertical agentic decision engine. The pipeline has executed **35
insight runs**. Behind it sit **4 prospects, 0 outreach workflows, and 1 activation event.**

The research says the binding constraint in every AI-leveraged business model is *distribution
and conversion*, not capability — and that is precisely the stage of your own funnel that is
empty. Meanwhile you were scoping a tenth system (the video engine) that produces zero revenue
for 6+ months and carries retention as its riskiest unverified assumption.

**The accretive move is to operate the finished asset, not to build another one.** Specifically:
sell evidence-backed audits into **home services** (not BJJ, not gyms), lead with **conversion
and lead-waste evidence** (not AI visibility), price the **recurring re-run** rather than the
one-off, and let the closed/lost calibration data become the compounding asset that nothing else
can synthesize.

---

## 1. The repo finding (highest-confidence input)

| Artifact | Count | Source |
|---|---|---|
| Completed system plans (P3–P12) | 9 | `.claude/PRPs/plans/*.plan.md` status fields |
| Insight runs executed | 35 | `artifacts/seo_insight_runs/runs/` |
| Qualified prospects | 4 | `artifacts/seo_insight_runs/prospects/` |
| Outreach workflows | 0 | `artifacts/seo_insight_runs/outreach_workflows/` |
| Activation events | 1 | `artifacts/seo_insight_runs/activation_events/` |

Caveat: outreach done manually outside the system wouldn't appear here. But by the ledger
designed to measure exactly this, the commercial motion is unstarted.

The build quality is not the problem — `docs/product-revenue-contract.md` is a more disciplined
commercial contract than most funded startups write, with append-only activation events,
evidence limits, and explicit anti-fabrication rules. The problem is that a beautifully
instrumented engine at idle produces the same revenue as no engine at all.

---

## 2. Where the money actually is (and isn't)

### 2.1 Vertical selection — decisive

| Vertical | Monthly marketing spend | Cost per lead | Job value | Verdict |
|---|---|---|---|---|
| **Home services / trades** | $1,000–$3,500 SEO alone; 10–15% of revenue under $1M | HVAC $127.74 · Plumbing $129.02 · Electrical $93.69 · **Roofing $228.15** | HVAC replacement ~$7,500 · Roof $9,605–$31,871 · Repair calls $340–$350 | **Primary** |
| Dental / medical | $1,500–$4,000 solo practice | SEO CAC ~$89/patient vs $340 via ads | Patient LTV $5,000–$10,000 | Secondary |
| Legal (PI) | $1,500–$10,000 | CPCs $100–$300 | Case value ~$30,000 | Tertiary — saturated, sophisticated buyers |
| **Fitness / gyms / BJJ** | ~$900–$1,000 minimum ad spend | target CPL $10–$25 | **member spends $123.23/mo** | **Do not sell services here** |

Sources: [LocaliQ Home Services Benchmarks](https://localiq.com/blog/home-services-search-advertising-benchmarks/) (3,211 campaigns, medians, Apr 2024–Mar 2025), [Hook Agency](https://hookagency.com/blog/digital-marketing-costs-for-home-service-businesses-in-2026/), [Angi cost guides](https://www.angi.com/articles/plumber-cost.htm), [Houzz & Home 2025](https://st.hzcdn.com/static/econ/2025-US-Houzz-and-Home.pdf) (n=21,889), [Cost vs. Value 2025](https://www.jlconline.com/cost-vs-value/2025/).

**Implication:** One Trade Network is the services-revenue vertical. National BJJ Registry cannot
support audit/retainer pricing — a $123/month member LTV mathematically can't fund a $1,000 audit.
BJJ must monetize as a *directory/data asset*, a different model on the same engine.

### 2.2 The legal wedge — the strongest single asset in this research

The FTC brought an action against HomeAdvisor/Angi and obtained a consent order that **bars them
from representing lead conversion rates without substantiating data in hand**, and specifically
prohibits describing leads as *"Ready to hire," "Project-ready," "Not window shopping," "Not just
price-shopping."* Relief up to $7.2M.
([FTC Docket D-9407 Complaint](https://www.ftc.gov/legal-library/browse/cases-proceedings/http://ftc.gov) — complaint Mar 2022, order final Apr 2023; the actual win-rate percentages are **redacted** in the public record.)

The dominant lead-gen model in your primary vertical is under a federal order for overclaiming
exactly the thing your platform is architected to never do. Your `product-revenue-contract.md`
already forbids fabricated traffic, leads, and conversion claims, and requires every claim to
resolve to a persisted artifact. **"Evidence you can audit, from someone who isn't selling you
shared leads" is a positioning no incumbent can copy without violating an order.**

### 2.2b The incumbent published your pitch for you (strongest finding in the report)

On the **Angi Q1 2026 earnings call (May 6, 2026)**, management stated on the record that pros
*"pay **$50 a lead**, they win **1 in 7, 1 in 8**. The average job is about **$4,000**"* — with a
stated take rate of ~10% of job value and an explicit corporate goal to **double the win rate**
([transcript](https://www.fool.com/earnings/call-transcripts/2026/05/06/angi-angi-q1-2026-earnings-call-transcript/)).

**The arithmetic they just handed you:** $50 × 7.5 leads = **~$375 customer acquisition cost per
won job** on a $4,000 ticket — 9.4% of revenue, *before* the ~$288 annual membership and before
any labor cost of chasing the six losing leads.

Move a contractor from 1-in-7.5 to 1-in-5 and their CAC drops from $375 to $250 — **$125 saved
per won job**. At five jobs a month that's $625/month in recovered margin, which comfortably
funds a $500–$1,000/month retainer. That is an ROI conversation grounded entirely in the
incumbent's own published numbers, which they cannot dispute.

Corroborating decline, from the 10-K rather than anecdote: **US average Monthly Active Pros fell
17% YoY (Q3 2025) to ~111,000 by Q4 2025**; FY2025 revenue **−13% to $1,030.5M**; Q1 2026 US
Network Leads **−54%**. Plus **1,910 Angi and 929 Thumbtack BBB complaints** closed in three years.

### 2.2c The repositioning this forces — sell win-rate, not better leads

⚠️ **Do not build or pitch "exclusive/non-shared leads."** That lane is already crowded: the
research found at least **seven distinct entrants** running exactly that attack inside the same
contractor forum threads — $89/exclusive-lead resellers, $100/month flat-fee directories, free
marketplaces, and AI speed-to-lead tools. Worse, **the incumbent is moving onto that ground**:
Angi's January 2025 "homeowner choice" change already dismantled its own blast-to-everyone
mechanic (Network leads −54%), and the Q1 2026 shareholder letter explicitly reframes the company
around *"solving the pro's core problem: winning work."*

**The uncrowded position is the one directly adjacent:** don't sell better leads — help them
**win more of the leads they already buy**. Nobody in that competitive set is selling conversion
improvement on leads the contractor has already paid for, it requires no lead inventory or
marketplace, and it is precisely what `ConversionReadinessService` already measures. Angi's own
CEO has publicly certified that win rate is the problem.

**Caution on "verified" language.** The Vermont AG settled with Angi in **October 2025 ($100,000)**
over *"Angi Certified Pro"* implying a credential neither the state nor Angi actually confers
([VT AG](https://ago.vermont.gov/blog/2025/10/13/attorney-general-clark-settles-dispute-angi-over-misleading-marketing-practice)).
Any verification badge on One Trade Network must correspond to something real and checkable —
which your evidence architecture supports, but the marketing copy must not outrun.

### 2.3 The conversion gap — your engine already measures it

Contractors with **fewer than 5 technicians book only 24% of inbound calls**, versus 59% for
shops with 25+ ([ServiceTitan, n=3,000+](https://www.servicetitan.com/blog/data-call-booking-rates) — 2022, dated but primary). Overall booking is ~42%; plumbing 43%, electrical 41%, HVAC 38%.

Small contractors are not short on traffic; they leak more than half of it. Your
`ConversionReadinessService` produces deterministic, vertical-aware conversion evidence — and at
$93–$228 per lead, a demonstrated conversion leak converts to dollars in one sentence: *"You're
paying $129 a lead and booking 24 of every 100 calls. Here are the three specific reasons."*

### 2.4 What NOT to lead with — AI visibility

I recommended this mid-research and the evidence reversed it. Correcting:

- **Only 8% of consumers begin a local search with an AI tool**; only **18% of AI users would
  contact a business on an AI recommendation alone**; **43% who start with AI revert to Google**
  ([BrightLocal, n=1,227, Jul 2026](https://www.brightlocal.com/research/consumer-search-behavior-channels/)).
- The widely-circulated "ChatGPT recommends only 1.2% of local businesses" stat is a
  **misstatement** — SOCi's sample was multi-location brands only. Do not use it as SMB evidence.
- **17.7% of small businesses pay for any AI service; only 16% of those pay $150+/month** — about
  **2.8% of all small businesses**, and ~1.4% in construction. Median monthly AI spend among
  payers *fell* from ~$78 (2022) to ~$28 (2025).
  ([JPMorgan Chase Institute](https://www.jpmorganchase.com/institute/all-topics/business-growth-and-entrepreneurship/understanding-ai-use-by-small-businesses) — 4.6M firms, transaction data, Apr 2026. Your old shop; it's the best evidence in the file precisely because it measures payments, not opinions.)
- Self-reported SMB AI adoption runs 68–82%. Measured payment is 17.7%. **That 4x gap is the
  distortion the entire "sell AI to SMBs" narrative rests on.**

Keep AI-readiness as a **differentiator inside the report** — it's a number their incumbent
vendor can't produce, and it makes the audit feel current. Don't make it the offer.

### 2.5 Pricing structure — two findings that should set the model

**Retention is a function of price point, not product quality.** Below $10/month ARPA, even
top-quartile SaaS retains ~63% of logos annually and only **2.7% achieve net revenue retention
above 100%**. Above $500/month ARPA: **~93% retention, 41% expanding**
([ChartMogul, n=2,100+](https://www.chartmogul.com/reports/saas-retention-report/)).

**Retainers beat projects decisively.** Retainer clients: 18% annual churn, 56-month average
lifespan. Project clients: 42% churn, 24 months (Focus Digital 2026). And most audit buyers pay
**under $1,000** — 43% pay $101–$750 ([WebFX](https://www.webfx.com/seo/pricing/how-much-does-seo-audit-cost/)); local SEO retainers average **$1,557/month** ([Ahrefs, n=439](https://ahrefs.com/blog/seo-pricing/)).

**Therefore:** price the audit near cost as the entry ($500–$1,500), monetize the **recurring
re-run + monitoring at $500–$1,500/month**. Never build anything with sub-$100 ARPA.

---

### 2.6 The BJJ registry — your paying customer is not the gym

The gap flagged in the first draft is now closed, and the answer inverts the obvious model.

**A direct competitor publishes its rate card.** jiujitsu-gyms.com — same category as National BJJ
Registry — sells **$99/year** listing/claim, **$299/year (or $29/mo)** featured city placement, and
**$1,500 setup + $99/month** for a custom academy site ([rate card](https://jiujitsu-gyms.com/feature-your-gym)).

**Willingness-to-pay anchors are strong, but capped.** US average BJJ tuition is **$146.15/month**
([Gold BJJ survey, ~2,000 responses](https://goldbjj.com/blogs/roll/statistics)). Academies already
pay **$100–$300/month in affiliation fees** (Gracie Barra, Alliance, Carlson Gracie). Premier
Martial Arts' franchise disclosure — the only regulated financial data in the industry — shows a
median **$27,146/year on advertising, 9.5% of gross**. Marketing budgets run $500–$1,500/mo
(0–50 members) up to $3,500–$7,000 (150+). A $299/year featured slot is under 2% of that budget.
Meanwhile Mindbody's marketplace take for introducing a new client is **20%, hard-capped at $30** —
the cleanest observed price for one introduced customer in fitness.

**The proof-of-shape case, Stripe-verified:** OpenAlternative, a solo-run directory, does
**$5,772 MRR / $105,061 all-time from 22 paying customers** (~$262 each) on ~70,000 monthly
uniques, at **2–3 hours per week** ([TrustMRR, Stripe-verified](https://trustmrr.com/startup/openalternative)).
Revenue mix: **~65% ads/sponsorships, ~35% featured listings** — a *small number of high-priced
slots*, not a long tail of cheap ones. The operator deliberately waited ~1 year to monetize.

**The reframe:** individual gyms are weak buyers ($146/mo member economics). But the **vendors
fighting over ~10,000 US BJJ gyms are not** — and they publish what an introduction is worth:
**PushPress pays $500 per referred gym demo**; **Gymdesk pays 100% of the first three payments
($225–$600)**. Zero delivery cost, published terms, no sales motion. So the registry's revenue
stack, in evidence order: **annual prepaid featured placement** (kills churn admin) → **sponsorship
inventory sold to gym-SaaS vendors and gear brands** → **affiliate on gym software**.

Note this reconciles with the ARPA finding in §2.5 differently than a SaaS would: the defense
against churn here is **annual prepay plus near-zero delivery cost**, not a $500/month price tag.

**Ceiling check, so nobody oversells this:** BJJLink was acquired by a public company (NYSE
American: MMA) in Dec 2024 for **up to $13M — $3M fixed plus a $10M earnout tied to hitting $3.6M
revenue by year 3** ([press release](https://www.mma.inc/mixed-martial-arts-group-limited-acquires-bjjlink)).
It had **802 paying gyms** and subscriptions up to $149/mo. The earnout structure implies revenue
well under $3.6M. There is an exit path in this exact vertical — and it is a single-digit-millions
path, not a venture outcome.

**Do not plan on data/API licensing.** Zero verified examples were found of a solo operator
monetizing a proprietary niche scoring dataset. Every comparable rests on scale (BuiltWith:
491.9M domains at $295–$995/mo) or pre-existing consumer trust (Trustpilot $99–$799/mo per
domain). Treat as unproven, not as a plan.

## 3. What the evidence says to avoid

1. **White-label audit infrastructure sold to agencies.** White-labeling is now **free** at
   AgencyAnalytics, Swydo, DashThis, Whatagraph and Rankscale; **73% of agencies already produce
   a client report in under an hour** (n=494); and **Semrush sunset its entire Agency Growth Kit**,
   killing Client Portal, Agency CRM and Lead Finder. Selling against free, into a solved
   problem, in a category the strongest incumbent just exited.
2. **AEO/GEO retainers to local SMBs.** See §2.4. The customer's customer isn't there yet.
3. **Low-ARPA self-serve micro-SaaS.** 2.7% net-expansion rate is a treadmill with a hole in it.
4. **AI receptionist/voice reselling.** Infrastructure costs $0.05–$0.31/min; Rosie retails 250
   minutes at $49; Ruby (the human incumbent) gives AI away free in every plan; Synthflow
   abandoned SMB self-serve for $30k/yr enterprise. Eleventh undifferentiated vendor.
5. **Generic AI content/video production as a service.** Upwork's index: **+90% contract starts,
   −13% earnings per contract** — the textbook commoditization signature. Academic causal work
   found *top-rated* freelancers were hit harder than low-skilled ones; quality did not protect.
6. **The "AI automation agency" category on the strength of its own discourse.** Zero independent
   revenue or failure-rate data exists; every source is selling a course. Real demand exists
   ($300M+ annualized AI GSV on Upwork, +40% YoY) but every source agrees the constraint is
   distribution — exactly what a solo operator lacks. *Unless they own distribution.* You do.

**Note on the video engine:** it sits adjacent to category 5, which is the most commoditized
segment in the entire dataset. What saves it is that you are **not selling it as a service** —
it's a distribution asset for owned properties, with registry-page embeds as the base case. That
distinction is load-bearing. Keep it, and keep it sequenced *after* cash.

---

## 4. What agents do well vs. what only you can do

You asked what I could do well. The honest split:

**What automation genuinely does well here — near-zero marginal cost, high volume, consistent quality:**
- **Manufacture evidence at scale.** 50–100 vertical-specific, provenance-linked audit briefs per
  week. You've proven the unit works 35 times; the 36th through 500th cost almost nothing. This
  is the single highest-leverage thing in your stack.
- **Prospect discovery, qualification, and enrichment** into the existing CSV→qualify→run path.
- **Draft** (never send) the personalized opener grounded in each audit's single strongest
  observation — your contract already requires operator approval, which is correct.
- **Maintain the evidence corpus and calibration loop** — every closed/lost outcome fed back into
  which observations actually predict revenue.
- **Produce owned-property content** (articles today, video later) that makes the registries
  differentiated rather than commodity directories.

**What only you can do — and what the evidence says is the actual bottleneck:**
- **The conversation and the close.** Every stream converged on distribution/sales as the binding
  constraint. No amount of pipeline fixes this.
- **Credibility.** Ex-JPMorgan talking to a contractor about where their $129 leads are leaking
  is a fundamentally different conversation than a generic SEO pitch. It's also why the finance
  content lane is defensible when AI personas on finance are a named enforcement risk.
- **Judgment on which evidence matters** — the Gate A/operator-review role you've already designed.

**The accretive pattern:** agents manufacture proprietary evidence at zero marginal cost → you
convert a small fraction of it → outcomes feed back as calibration → the evidence corpus becomes
the thing competitors can't copy, because it's grounded in *your* closed/lost data in *your*
vertical. Tools commoditize (AEO monitoring went $20–$500 in 18 months; Semrush exited agency
tooling). **The corpus and the calibration loop don't.**

---

## 5. Ranked paths

| # | Path | Time to cash | Accretion | Evidence strength |
|---|---|---|---|---|
| 1 | **Run the trades audit motion** — 30–60 audits into home services, lead with conversion/lead-waste evidence, convert to $500–$1,500/mo re-run retainers | 30–90 days | Medium-high (calibration data compounds) | **High** |
| 2 | **Registry monetized through vendors, not gyms** — annual prepaid featured placement ($299/yr comp), sponsorship inventory sold to gym-SaaS vendors, affiliate ($500/referral PushPress; $225–600 Gymdesk). Target shape: ~20–25 customers at ~$260/mo (§2.6) | 3–6 months | High (owned asset) | **High** |
| 3 | **Evidence corpus + calibration as the durable moat** — the artifact layer, vertical remediation playbooks | Continuous | **Highest** | High (by inversion: everything else commoditized) |
| 4 | **Video engine / owned media** — distribution asset for the registries, not a service | 6–12 months | Medium-high | Medium (retention unproven) |

Planning arithmetic for path 1 (labeled estimate, not sourced): assume **5–10% of cold audit
recipients book a call** and **25–35% of calls convert** (anchored on the neutral 28–35% industry
proposal win rate, not vendor case studies claiming 80%). That implies **30–60 delivered audits
per retainer client from cold** — which is exactly why an automated engine changes the economics.
Nobody publishes credible free-audit→paid conversion data; treat these as hypotheses to calibrate,
which is itself the point.

---

## 6. 30 / 60 / 90

**Days 1–30 — switch the machine on.**
Pick one trade and one metro (roofing or HVAC; highest ticket, highest CPL, most lead waste).
Build a 100-prospect list through the existing intake. Run audits in batches. Assemble the offer
around conversion evidence + the FTC-backed honesty positioning. Send 20–30 operator-reviewed
openers. Record every activation event — the ledger you built is the experiment instrument.

**Days 31–60 — find the price.**
Target 3–5 discovery calls and 1–2 paid engagements. Test $750 vs $1,500 audit pricing openly.
Convert at least one to a monthly re-run. Feed every outcome back into which observations
actually correlate with replies and closes.

**Days 61–90 — decide with data, then resume building.**
With ~50 audits and real close data, you'll know cost per audit, reply rate, close rate, and
which evidence type sells. *Then* resume the video engine — funded by revenue, aimed at the
registry embeds, with the pilot's retention question answered on someone else's dime.

**The one sentence:** you have spent the build budget; the accretive next dollar is a
distribution dollar, spent in home services, with the machine you already finished.

---

## Methodology & limits

Three parallel research streams (plus one child agent on trades economics) covering: the
productized audit/AEO service market; vertical directory and trades monetization economics; and
which AI-leveraged business models are defensible versus commoditized in 2026. Roughly 90
sources, prioritizing primary data (bank transaction data, marketplace financials, published
survey methodology, vendor pricing pages, FTC filings) over agency content.

**Known gaps:**
- **No credible independent data exists on niche directory revenue post-AI-Overviews.** The
  threat is well-evidenced (AI Overview commercial+transactional intent went ~10% → ~32.5% during
  2025); realized directory revenue is not.
- No neutral study of free-audit → paid-engagement conversion exists publicly. All circulating
  figures are vendor case studies.
- Contractor LTV figures ($15,340 for HVAC) circulate widely with **no traceable primary source**
  — do not use them in client materials.
- Firecrawl/Exa MCPs were unavailable; research ran on WebSearch/WebFetch.

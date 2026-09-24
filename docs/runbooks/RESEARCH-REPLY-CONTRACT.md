# The research reply contract - THE RESEARCH CLAIMS GATE (2026-09-24)

Every research reply, from Gemini or any other lane, lands only after OUR verifier passes it:
`python content/video_engine/scripts/verify_research_claims.py <run dir>`. The reply's own checks are never trusted.
The verifier recomputes each one from the page, the saved file and the DOI registry.

The operator, 2026-09-24: *"we rely on it machine wide for research, verification, dedupe, and index. it needs to do
better about verification, citation, and fact-checking ... gemini hallucinates a lot, so we need some sort of force
system in place to actually enforce its checks/gates."*

Recall:
- `docs/research/markets/r26-306-nvda-share-railway-gdp-VERIFY-2026-09-24.md` - the case. Two TrendForce URLs were fabricated (404). Four DOIs were unregistered or resolved to unrelated books. One filing figure was mis-typed ($115,173M against the filing's $115,186M). Rows were self-marked CONFIRMED with no source on disk.
- `docs/agent-memory/operator/research-gate-tiers.md` - the four tiers. A passing provenance audit is not a source on disk.
- `docs/agent-memory/operator/gate-extraction-orders.md` - an order ships with a mechanical `--verify` gate. Form-only checks let a plausible synthesis through.
- `content/video_engine/scripts/audit_research_provenance.py` - the layer audit. Its `compute_sha256` is reused. Its `--verify-urls` sends a HEAD request, which cannot see a quote, so the gate does its own GET.
- `docs/runbooks/BRIDGE-SHAPES.md`, `docs/runbooks/BRIDGE-DAEMON.md` - `report-landed` and the P46 T7 `verify` hook, which the gate rides.
- OPERATOR-RULINGS E99 s93 - a PLAUSIBLE page may draw. UNSOURCED and REJECTED never draw.

## 1. The run folder

```
docs/research/runs/<run>/
  claims.jsonl      one JSON object per figure - the only place a number is stated
  sources/          every page you quote, saved as fetched (html / pdf / csv); its sha256 goes in the claim
  <report>.md       the prose; every number in it has a claim id beside it
  VERIFY.json       written by OUR verifier, never by the lane
  VERIFY.md         the same, as tables - the failure table is the revision order
```

## 2. `claims.jsonl` - one object per line

| field | required | meaning |
|---|---|---|
| `id` | yes | unique within the run (`nvda-dc-rev-fy25`) |
| `claim` | yes | the sentence the figure supports |
| `value` | yes (null for a claim with no number) | the number **as printed** (`"115,186"`, `"1.2"`, `"$1.2 billion"`, `"92"`) |
| `unit` | yes | `USD million`, `GBP million`, `%`, `shares` - a scale word here scales the value |
| `period` | yes | `FY2025`, `2024`, `1847` |
| `source_title` | yes | the cited work's title. It is fuzzy-matched against the DOI's registered title |
| `author` | no | the cited author(s). With a DOI, one registered family name must appear |
| `publisher` | no | who published it |
| `url` | no | a page **you fetched this session** |
| `doi` | no | a DOI **you resolved this session** (`10.2307/2552228`) |
| `retrieved_at` | no | ISO date of your fetch |
| `quote` | yes (may be empty only for a derived claim or a DOI-only claim) | copied **verbatim** from the source, at most 300 characters. The value must appear inside it. `...` or `…` marks an elision |
| `sources_file` | no | `sources/<file>`, the saved copy. It must be inside the run folder |
| `sha256` | with `sources_file` | the sha256 of that file |
| `source_kind` | no | `primary` (default) or `secondary`. A secondary source caps the claim at PLAUSIBLE |
| `tier_declared` | yes | `CONFIRMED` / `PLAUSIBLE` / `UNSOURCED` / `REJECTED` |
| `derived_from` | derived only | the input claim ids |
| `formula` | derived only | arithmetic over `{id}` placeholders: `{ocf} - {capex}`, `{a} / {b} * 100`. Numbers, `+ - * /` and brackets only |
| `notes` | no | anything else, such as a dead URL you tried (a dead URL never goes in `url`) |

## 3. The rules

1. **Every number has a claim.** A figure in the report with no claim id is not a finding.
2. **No URL you did not fetch this session. No DOI you did not resolve.** The verifier fetches every URL and resolves every DOI. A 404 is a fabricated citation.
3. **The quote is copied, never paraphrased.** The verifier finds it in the live page and in your saved copy. Case, spacing, dash and quote-mark styles are folded; words are not.
4. **The value is inside the quote.** It must match to its own printed precision: `1.2 billion` may round a source's `1.23 billion`, but `1.23` may not sharpen a source's `1.2`. `1,234.5` = `1234.5`; `1.2` with unit `USD billion` = `$1,200 million` = `1200000000 USD`; `(3,236)` counts as either sign.
5. **Save the page to `sources/`** with its sha256, so the evidence survives the web.
6. **Declare the tier honestly.** The verifier computes the tier itself. If the declared tier is higher than the earned one, that is an **overclaim, and it fails the reply**, even though the claim is kept at the lower tier. An honest UNSOURCED passes.
7. **A derived figure names its inputs and its formula.** The verifier recomputes it; a mismatch beyond the claim's own rounding fails.

## 4. The tiers, as the verifier earns them

| earned | when |
|---|---|
| **CONFIRMED** | a primary source whose live page (HTTP 2xx, quote on it) or saved copy (sha256 equal, quote in it) carries the quote, with the value inside the quote |
| **PLAUSIBLE** | the same checks pass on a `secondary` source, or a DOI resolves to the cited work but no page or copy was checked (E99 s93) |
| **UNSOURCED** | nothing checkable backs it: no URL, or one that could not be verified (401/402/403/429/451, a timeout, a page with no readable text), and no saved copy |
| **REJECTED** | any check FAILs: a 4xx/5xx or DNS failure, an unregistered or misattributed DOI, a quote not found, a value not in its quote, a sha256 mismatch, a missing saved file, a derived value that does not recompute |

A derived claim earns the weakest tier of its inputs, or REJECTED if it does not recompute.
If a claim is **declared** REJECTED, it is a disclosure: its checks are reported, and they never fail the reply.

`--offline` never touches the network (tests, CI). A claim can then earn CONFIRMED only from its saved copy, so a
web-only CONFIRMED is an overclaim offline. The verifier's User-Agent is `MoneyPhysics-research-verifier (research@localhost)`.
No personal address ever goes in a request.

## 5. Refusal and revision

- **The gate by default.** `bridge_send.py --lane gemini --reply-shape report-landed` attaches the gate. Any order that names `--research-run <dir>` does too. The order carries `verify: python content/video_engine/scripts/verify_research_claims.py <run>` and `research_run: <run>`, and these rules are prepended to the brief. `--no-claims-gate` opts out, and the send prints a warning. A second `--verify` is refused rather than allowed to replace the gate.
- **Tier 0.** The daemon checks the reply's form (`report-landed`), then runs the gate. If the gate exits 0, the packet closes.
- **The revision loop.** If the gate fails, the daemon sends `VERIFY.json`'s failure lines back to the same conversation as a revision order ("Revision n of 2"). Each failing row takes one of three honest fixes:
  - cite a page fetched now, saved and hashed;
  - lower the tier to the one earned;
  - mark the row REJECTED, or drop it.

  The order never asks for a new number. The original packet waits (`revision.json`); when a revision passes, every round before it closes.
- **Escalation.** When two revisions have failed, the daemon escalates once to the operator (`research-gate`, one toast) and does not run tier 1: a model's judgement cannot make a fabricated URL resolve.
- **Nothing is promoted until the gate passes.** No figure from the reply enters `docs/research/markets/` or an evidence object until `verify_research_claims.py <run> --require-pass` exits 0. That command checks that `VERIFY.json` says PASS for the claims file as it is now (its sha256); if the file was edited after the gate ran, the verifier must run again.

The gate proves citation and arithmetic, not judgement. A passing run is still read as a draft
([research-gate-tiers](../agent-memory/operator/research-gate-tiers.md)), and its intake names each claim's tier.

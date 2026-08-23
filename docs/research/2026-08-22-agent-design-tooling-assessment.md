# Agent-Native Design Tooling: Buy, Borrow, or Build

Status: current
Researched: 2026-08-22
Question: should the content video engine incorporate paper.design (or similar
agent-native design tools), or stay 100% self-built?

## Answer

**Neither, as posed.** The pipeline has two jobs with opposite requirements, and
the right answer differs for each:

| Job | Volume | Requirement | Verdict |
| --- | --- | --- | --- |
| **Production** — plates, compositions, renders | ~150 plates per episode | Headless, deterministic, byte-identical, verifiable | **100% self-built.** No tool surveyed can do this. |
| **Art direction** — deciding what a lane *looks like* | ~7 times, ever | Human judgment, visual exploration | **Borrow a tool.** Cheap, and not worth building. |

Keep a hard boundary between them. The failure mode is letting a design tool
creep into production, where it structurally cannot go.

## Why no tool can do the production job

Every agent-native design tool surveyed shares one disqualifying property:
**it requires a desktop application open with a file loaded.**

- Paper's own docs: *"opening a file in the app will automatically start the MCP
  server"* and *"the MCP server operates on the currently open file"*
  ([paper.design/docs/mcp](https://paper.design/docs/mcp),
  [/docs/support](https://paper.design/docs/support)).
- Figma's Dev Mode MCP requires the desktop app running alongside the IDE, and a
  Figma staff reply confirms write-to-canvas *"only runs through supported MCP
  clients — Claude Code, Cursor, VS Code, Codex, Claude Desktop… Direct JSON-RPC
  to the server isn't one of them"*
  ([Figma Forum, 2026-08-21](https://forum.figma.com/ask-the-community-7/can-figma-mcp-be-used-for-programmatic-design-generation-seems-like-read-only-only-57148)).

An attended desktop app cannot sit in a cron job, a CI run, or a 150-plate batch.
That is not a maturity gap that closes with the next release; it is the product
shape.

Separately, the engine already produces something none of these tools offer.
`composed_plate.py` (T13) renders SVG from structured values with byte-identical
output across runs, refuses an arithmetic stack whose operands do not match its
declared total, and costs `$0.00` per plate. A design tool produces *one artifact
a human approved*. The pipeline needs *150 artifacts derived from a model, each
verifiable*. Those are different problems.

## Tool-by-tool

### paper.design — the best of the borrowed options

- **Canvas is HTML and CSS.** Every element renders as real HTML/CSS, so designs
  export as code with no conversion step. This matters more here than anywhere
  else: **HyperFrames consumes HTML/CSS**, so a style pack designed in Paper
  lands in the renderer's native format.
- **MCP is bidirectional**: 24 tools (11 read, 8 write, 5 utility). An agent can
  create artboards, write HTML into frames, update CSS, duplicate nodes and
  screenshot to verify.
- **Built-in image generation** with Flux 2 (**multi-reference**), Nano Banana
  Pro, OpenAI Image Edit 1.5, Seedream 4.5. Multi-reference conditioning is
  directly relevant to character consistency.
- **Pricing**: Free is $0 with **100 MCP calls per week** — one user reported
  hitting *"Weekly call limit reached"* after their first call. Pro is $20/month,
  $16 annual, with 1M calls/week, video export and 100 MB images. Organizations
  tier is not shipped.
- **Token efficiency**: a third-party March 2026 benchmark reported ~6K tokens and
  3 minutes per design task versus Figma's ~20K and 10 minutes. Treat as vendor-
  adjacent evidence, not measurement.
- **Maturity**: open alpha.
- **Already present**: Paper ships as a built-in MCP server in Claude Code via the
  `frontend-design` plugin, and currently **auto-launches the Paper app on every
  Claude Code start** ([claude-code#47852](https://github.com/anthropics/claude-code/issues/47852)).

### Claude Design — check this first, it is already configured

Anthropic's own tool generates production-ready HTML, CSS and JavaScript from
conversation, and **automatically inherits the organisation's design system** —
brand colours, fonts and components without uploading anything. Available on Pro,
Max, Team and Enterprise plans.

It is already in this machine's MCP config. The 401 diagnosed earlier in the
session is simply missing auth; the fix is `/design-login` in an interactive
session, not a new subscription
([Anthropic Help Center](https://support.claude.com/en/articles/14604416-get-started-with-claude-design)).

**Evaluate this before paying for anything.** Same output format as Paper
(HTML/CSS/JS), same job, already covered by the existing plan.

### Figma — wrong canvas, higher cost

Write-to-canvas works and is currently free during beta (Figma states it will
become usage-based paid). But the canvas is proprietary SVG rather than HTML/CSS,
so everything needs translation before HyperFrames can use it; Dev Mode requires a
Professional seat at $15/month before MCP is available at all; and its real
strength — mature design-system integration for teams — is irrelevant to a
one-operator pipeline.

### Canva — blocked by its own API

Shipped an MCP in February 2026 with 12M+ designs created, but the Connect API
**cannot edit existing free-form design content**. It is restricted to autofilling
predefined templates, uploading assets and managing folders. Reported gaps also
include no brand enforcement at the agent layer and a community-maintained server
that can break when Canva updates its API. Template autofill is not what this
pipeline needs.

### Others considered

CoDesign (IMG.LY, free local MCP, technical preview June 2026) is the only
surveyed tool that installs *into* the agent rather than being a destination —
worth revisiting if it leaves preview. Moda markets brand enforcement and
multi-format export. Neither changes the headless conclusion.

## Recommendation

1. **Run `/design-login` and evaluate Claude Design first.** Zero marginal cost,
   already configured, produces the right output format, inherits the design
   system. If it covers art direction, stop here.
2. **If it does not, buy Paper Pro at $16/month.** Justified by the HTML/CSS canvas
   matching HyperFrames and by Flux 2 multi-reference for character sheets. The
   free tier is unusable — 100 calls per week is one session.
3. **Do not connect either during production runs.** Connected MCP servers cost
   roughly 18K tokens per turn each in context overhead, and Paper auto-launches
   its desktop app on Claude Code start. Connect for art-direction sessions,
   disconnect afterwards.
4. **Build nothing that these tools do.** Do not build a canvas, a layout editor,
   or a visual style explorer.
5. **Buy nothing that the pipeline does.** Composed plates, prompt fan-out, the
   scene board and the selection gate stay self-built. They are deterministic,
   verifiable and free per unit; no design tool offers any of those three.

## Correction (2026-08-22, same day)

An earlier revision of this document claimed the bottleneck was "roughly 150
plates per episode holding one identity" and treated an attended desktop app as
disqualifying. **Both claims were downstream of one wrong number.**

Plates are **composites of reusable layers**, not per-plate generations. The
`systems-and-blowups` project already implements this: `asset-taxonomy.v1.json`
defines a reusable vocabulary (19 actors, 13 objects, 8 mechanisms, 10 worlds),
`assets/generated/cutouts/` holds keyed actor, building and mechanism cutouts, and
`style-profile.v1.json` declares four `depth_layers` — foreground cutout, actor or
machine, building or environment, evidence-safe region.

So a ~150-plate episode is ~150 *composites*, drawing on a library built once. New
generations per episode are the topic-specific props and any genuinely new pose —
plausibly **5–20**, not 450–810. That is roughly a **10x error** in the earlier
cost model.

Two consequences:

1. **Character consistency is perfect by construction, not managed.** Compositing
   a fixed cutout means the character is literally the same PNG in every plate —
   zero drift, the same property the parametric SVG rig would give. The identity
   anchor, reference conditioning and detail tiering apply to **building the
   library**, a bounded one-time job, not to producing episodes.
2. **The attended-desktop objection largely dissolves.** It carried weight only
   against a 450-generation batch. At 5–20 topic props per episode, produced by an
   operator who is at a dual-monitor desktop anyway, an attended tool is a
   perfectly reasonable surface. It strengthens the Paper recommendation for the
   art-direction and library-building job rather than weakening it.

The headless rule still holds for one thing: **compositing and rendering must stay
unattended**, because they run per-plate at volume. Generating a prop is attended
work; laying 150 composites is not.

## The remaining hard problem

**Library quality, then coverage.** Operator assessment on review: of the existing cutouts only
the host character model is good; the building, actor and mechanism cutouts are not. So the
first real task is building roughly 50–100 usable cutouts across the taxonomy — a one-time,
attended, art-directed job rather than a recurring pipeline cost.

That sharpens the recommendation above rather than changing it. Building a cutout library *is*
the art-direction job, it is done at a desk with a human judging each asset, and it is the
single highest-value use of Claude Design or Paper here. It is also the concrete first thing to
point either tool at.

After quality comes **coverage and composition** — does the
catalog contain an actor, world and mechanism for every slot a script asks for,
and does the composite read correctly when layered? That is a catalog-completeness
and layout problem, solved with the existing asset catalog plus a composite
recipe, not with an image API and not with a canvas.

## Sources

- [paper.design/pricing](https://paper.design/pricing)
- [paper.design/docs/mcp](https://paper.design/docs/mcp) and [/docs/support](https://paper.design/docs/support)
- [Paper.design Review: MCP, Features, Pricing — Banani](https://www.banani.co/blog/paper-design-mcp-review)
- [Figma MCP vs paper.design — SFAI Labs](https://sfailabs.com/guides/figma-mcp-vs-paper)
- [Figma vs Paper (2026) — UIThings](https://uithings.com/figma-vs-paper)
- [Guide to the Figma MCP server — Figma Help](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server)
- [Can Figma MCP be used for programmatic design generation? — Figma Forum](https://forum.figma.com/ask-the-community-7/can-figma-mcp-be-used-for-programmatic-design-generation-seems-like-read-only-only-57148)
- [AI Design Agents in 2026 — IMG.LY](https://img.ly/blog/ai-design-agents)
- [Best AI Design MCP Servers June 2026 — Moda](https://moda.app/blog/ai-agent-design-mcp-tools)
- [OpenClaw Canva Integration guide — Skywork](https://skywork.ai/skypage/en/openclaw-canva-ai-design-guide/2051901130512371712)
- [Get started with Claude Design — Anthropic Help Center](https://support.claude.com/en/articles/14604416-get-started-with-claude-design)
- [claude-code issue #47852](https://github.com/anthropics/claude-code/issues/47852)

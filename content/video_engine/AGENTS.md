# Content Video Engine

## Pipeline

- Treat `storyboard.json` as immutable after Gate A; measured timing belongs in artifacts.
- Audio is the render clock. Never stretch or trim narration to fit video.
- Keep provider keys in environment variables and fail before a paid call when configuration
  is incomplete.
- Gate A and Gate B are operator actions. Tests may simulate them; product code may not
  auto-approve them.
- All stages are deterministic and idempotent from persisted inputs. Record failures and
  degraded behavior in stage events.
- Runtime output belongs under `runtime/jobs/` and is never hand-edited.

## Asset catalogue

- **Promotion is an operator action.** Product code and generating agents never set
  `rights_state: approved`, `review_state: approved_reusable`, or `render_eligible: true`.
  Register new assets as `original_review_only` / `review_only` / `render_eligible: false`.
- Register by `asset_id` plus `sha256`, never by raw path. A path with a mismatched
  digest is a rejection, not a warning.
- Follow the tier convention: `actor`, `prop`, `world`, `world_board`, `cast_board` at
  tier 2; `mechanism` at tier 3. Tier 3 is restricted by kind, so an actor registered
  there is invisible to the resolver and every actor slot silently falls through to
  `bespoke_plate`.
- Resolution ranks by **match strength first, cascade second**. The cascade breaks ties
  between candidates that match equally well; it must never let a one-word coincidence at
  an early tier pre-empt a real match at a later one.
- An episode may not mix art directions, but raw `style_version` equality is too blunt a
  test — one coherent cast can span two version strings. Group them in `style_families`
  and compare families.

## Generation loop and the paid gate

[26-AGENT-GENERATION-LOOP.md](../../docs/content-video-engine/26-AGENT-GENERATION-LOOP.md)
is the loop of record. Images generate on subscription agents via claims —
never a metered API. The human gate sits at spend authorization (operator
decision 2026-08-23); per-asset triage is the override surface, not the
default. `approved` is still never set by product code: promotion flows
through the same operator-confirmed commit, and the paid gate releases
nothing by itself. Flow-lane jobs refuse release while the pause stands.

## Layout and durability

[27-DURABILITY-AND-LAYOUT.md](../../docs/content-video-engine/27-DURABILITY-AND-LAYOUT.md)
is the layout of record. A file's durability class is readable from its path
alone: `canonical/` survives hardware death (synced to the store on promote),
`review/` is in-flight, `runtime/` may vanish. Class-root paths resolve through
`src/services/paths.py` — never by hand; a structural test enforces this.

## Composition

[24-COMPOSITION-AND-SCALE-SPEC.md](../../docs/content-video-engine/24-COMPOSITION-AND-SCALE-SPEC.md)
is the specification of record. The rules that get violated most:

- **Figure size is set by the plate, not the compositor.** The furniture already drawn in a
  world commits it to a figure height. If that height is wrong, regenerate the world;
  shrinking the cast to fit makes them read as dolls and no setting undoes it.
- `world_figure_scale` (what the furniture is drawn for, 0.50) and `cast_figure_height`
  (what the cast composites at, 0.76) are **two independent numbers**. Conflating them is
  the single most common source of scale errors.
- Every world declares `placement` — clear-floor span, baseline, figure height, max figures.
  Without it a compositor will stand figures on the furniture.
- Figures sharing a frame share a scale. Hierarchy is carried by rendering weight alone
  (~2:1 on saturation and internal detail); do not stack scale or brightness on top of it.
- Keep the host's rendering untouched. Contrast comes from making supporting cast lighter.
- 2.5D world planes are declared back to front, must include `building_or_environment`,
  and must be generated in one pass so they register.

## Asset review

- Verify delivery before reading it: every declared `sha256` against the bytes, dimensions
  against the spec, and alpha where transparency was required.
- Measure before asserting. Density, saturation, detail, clear-zone flatness and implied
  human scale are all cheap to compute and routinely contradict a visual impression.
- **Then composite and look.** Metrics predicted the v2 props would outrank the host by
  size; they did not. The real defect was representational register, and only a composited
  frame showed it.
- Separate *medium* (an editorial choice, the operator's) from *function* (density,
  legibility, scale, registration). Rejecting a delivery on medium when the operator has
  already chosen it wastes a batch.
## Local code-navigation workflow

Use the portable wrapper from the repository root when a named symbol, service, or architecture path needs ranked evidence:

```bash
python scripts/sigmap_context.py build
python scripts/sigmap_context.py query "sitemap discovery" --top 5
python scripts/sigmap_context.py evidence "CrawlDiscoveryService" --markdown
```

Every wrapper command regenerates the local index first with `--no-track`. Its configuration writes only the gitignored `.github/copilot-instructions.md`; it does not modify `AGENTS.md` or `CLAUDE.md`, register MCP clients, or invoke Codex/Claude adapters.

Route questions to the smallest suitable tool:

- **SigMap**: declared symbols, ranked architecture discovery, and evidence packs.
- **ast-grep**: structural patterns and exact call-site sweeps. Always set `--lang`, use a narrow pattern, and scope it to repo-relative paths; one-shot `run` needs no `sgconfig.yml`, while reusable configured rules use `scan`.
- **Text search** (`git grep` or `search_files`): literals, configuration keys, SQL, docs, and test descriptions.
- **SQZ**: compress noisy command output or logs only after saving the original evidence. Use `sqz compress --mode safe --verify --no-cache --cmd <producer>`; do not compress hashes, exact test verdicts, security evidence, or small outputs, and never use SQZ as a search or correctness tool.

Windows path rule: set the command/tool workdir to the exact repository root and pass `.` or repo-relative paths. The native Windows `rg` used by `search_files` does not accept MSYS-style absolute paths such as `/c/Users/...`; if an absolute-path search fails, retry from the exact workdir with a relative path before concluding that nothing matched.

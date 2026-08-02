# Archival Asset and Citation Specification

*Specification of record for History Documentary V4 rights, likeness, attribution,
local asset resolution, and credits.*

## 1. Separate evidence from permission

`research_packet.v1` answers **“may we say this?”**. `asset_manifest.v1` answers
**“may we render this local file?”**. Neither contract implies the other.

The following never enter a renderer: remote URLs, research snapshots, consultant
or reference-pack files, creator names or imitation instructions, unresolved
archive paths, and assets whose hash, rights review, or attribution is incomplete.

## 2. Render-eligible rights categories

The pilot may render only original, operator-owned, licensed, verified public
domain, CC0, reviewed CC BY, or compatible reviewed CC BY-SA assets.

`fair_use`, unknown, merely-public, research-only, and unverified Creative Commons
records are quarantined with `render_eligible: false`. Public availability,
YouTube hosting, citation, and transformation do not establish permission.

## 3. Required asset record

Each manifest entry includes a stable ID, local path, SHA-256 content hash, origin,
rights category, license, rights review, attribution, likeness policy, permitted
alterations, disclosure label, and render eligibility.

Resolution fails closed when a file is missing, escapes the approved asset root,
has a stale hash, or violates its alteration constraints. Renderer input is a
job-local `resolved_assets.json` containing approved IDs and local paths. Source
URLs stay in evidence and credits, not scene treatments.

## 4. Likeness, logos, and reconstructions

- A living-person likeness requires an approved reference and explicit operator
  approval for the intended use.
- A deceased historical figure still requires a rights-cleared image and must not
  be placed in a fabricated photorealistic event.
- Logos and organization marks require recorded permission; otherwise use text.
- Manual or AI-assisted illustration must be deliberately non-photorealistic,
  derived from permitted inputs, and labeled `Illustration` or `Reconstruction`.
- Illustrations communicate interpretation and atmosphere. They do not prove a
  historical claim.

## 5. Alteration rules

The manifest records whether cropping, color treatment, parallax separation,
background removal, restoration, and compositing are allowed. If a license or
archive prohibits alteration, the renderer may only place the intact asset.

No process may remove watermarks, crop away a required credit, or imply that an
archival image depicts a different narrated event.

## 6. Attribution and credits

Credits are aggregated deterministically from every rendered asset and displayed
research citation. The generated `credits.json` and credit roll include, as
applicable: creator, title, institution, license, license URL, canonical source
URL, modification notice, and asset ID.

Duplicate entries may be collapsed only when all attribution fields match.
Missing required attribution blocks QC. Citation overlays never authorize visual
reuse.

## 7. Asset intake workflow

```text
discover candidate
→ record provenance
→ obtain or verify rights
→ download to approved local root
→ hash bytes
→ record likeness and alteration policy
→ rights review
→ resolve into job-local approved assets
→ render
→ aggregate credits
```

Changing bytes, rights, attribution, or likeness approval changes the manifest hash
and invalidates downstream approvals.

### 7.1 Stock cut-in lane

Stock photos, vectors, illustrations, icons, video, and templates are a separate
candidate lane. A catalog search result or preview is not renderable. Intake must
capture the provider resource ID, canonical item URL, creator, media type, plan at
download, license terms or license snapshot, attribution requirement, download
receipt when available, permitted alterations, and the downloaded file hash.

```text
stock search
→ candidate metadata
→ license and plan review
→ operator-selected download
→ local containment and hashing
→ asset-manifest review
→ render by approved local asset ID
```

Magnific stock may be used in monetized YouTube videos, including as a main visual
element. Free and Essential accounts require attribution; paid-plan entitlements
and API download costs or limits vary by plan. Therefore the engine never labels a
stock asset simply `free`. It records the specific entitlement and credit/attribution
state that applied when the asset was acquired. Stock files may not be redistributed
as a competing library, exposed as downloadable source files, or used as unapproved
logos or trademarks.

### 7.2 Generated-reference and flow lane

Magnific references, custom characters/styles, Spaces flows, Designer templates,
agents, and context are production recipes, not evidence and not final assets.
Versioned provider records may contain:

- reference kind: `style`, `character`, `element`, `location`, or `template`;
- provider ID plus operator-owned training/input hashes and rights approval;
- flow ID/version, expected input/output types, model nodes, evaluator checkpoints,
  and conservative cost ceiling;
- declared use: generation consistency, repair, animation, or layout only;
- output task ID, local downloaded hash, disclosure label, and review state.

Training inputs must be original, operator-owned, or explicitly licensed for that
use. Research-pack frames, archive previews, creator identity assets, and historical
claims cannot train a production reference. A flow or agent cannot approve its own
output, establish a historical fact, or promote an asset into the render manifest.

The preferred still workflow is:

```text
approved deterministic plate
+ approved original style / element / location references
+ evidence-safe shot brief
→ versioned Magnific Space / Flow
→ evaluator pause
→ optional masked repair
→ optional upscale
→ local export and hash
→ operator asset review
→ Remotion composition, citations, and credits
```

Short generated motion is considered only after the start/end stills pass visual
review. Remotion remains the deterministic editorial owner; Magnific supplies
reviewed media candidates rather than a final documentary timeline.

### 7.3 Generated Visual Direction candidates

`generated_visual_candidates.v1` is the only contract that may place newly
generated bitmap art into a pending documentary style board. It is a preview
domain, not the asset manifest:

```text
original evidence-safe prompt brief
→ generated local candidate
→ hash and job-local containment
→ generated-visual validation
→ selected style-board preview
→ Visual Direction Gate
→ explicit asset promotion
→ rights-reviewed asset manifest
→ renderer asset ID
```

Every candidate records its provider, local path, byte hash, semantic role,
review status, disclosure label, and whether it was selected for the board.
Validation requires `preview_eligible: true`, `render_eligible: false`,
`evidence_eligible: false`, and `contains_factual_text: false`. Remote paths,
source-video identifiers, creator imitation language, stale hashes, and
generated archive/document/relationship evidence fail closed.

The cold-open contrast uses exactly two selected plates when generation is
enabled: a myth/metaphor plate and an institutional reconstruction. Other gate
roles select at most one generated plate. Gate approval binds the composed style
board, but does not silently promote its source candidates; promotion remains a
separate, auditable asset-manifest operation.

Generated candidates assigned to `document` or `map_timeline` must declare
`usage: background_only`. Their pixels establish atmosphere and parallax depth
only. The renderer must composite a deterministic document excerpt, locator,
citation rail, route, date, and place label above them. A generated mark can
never be interpreted as document text or map data. The `lineage_concept` role
may use a full illustrated scroll, but its medallions remain blank until the
renderer adds reviewed entities, typed relationship verbs, and uncertainty
labels. The `concept_mechanics` role may use a background metaphor, but it is
never a multi-step technique demonstration or a source of factual claims.

`motion_selected: true` is a separate, review-only selection for a local
animatic revision. It does not grant render eligibility or replace the
Visual Direction Gate.

## 8. Pilot policy

Episode 1 is rights-cleared-only. If suitable archive media cannot be cleared, use
an original labeled illustration, document typography, map, timeline, or
relationship graph. Do not relax the rights policy to make the style board look
more archival.

"""Generate the research extraction index from the bundle's ACTUAL headings.

Coverage is the proof of reading: every heading in every primary gets a disposition.
A heading with no rule falls out as UNASSIGNED and the gate fails.
"""
import re, pathlib, json

B = pathlib.Path("content/video_engine/sources/reference_analyses/complete_research_evidence_bundle")

RULES = [
 ("00_", r".*", "RECORD - bundle navigation; consumed to route this read"),
 ("01_", r"Executive Summary|Core Production Metrics", "EXTRACTED -> 46 SS46.1"),
 ("01_", r"Comparative Scorecard", "EXTRACTED -> 46 SS46.1/SS46.6 (tutorial column = negative control)"),
 ("01_", r"Audio Gaps|Breath Pause", "EXTRACTED -> 46 SS46.3"),
 ("01_", r"Unifying Equation Spine", "EXTRACTED -> 46 SS46.4 - closes backlog R2a"),
 ("01_", r"Evidence Screen Time", "EXTRACTED -> 46 SS46.1"),
 ("01_", r"Persistent Cast|Metaphorical Physical Props", "EXTRACTED -> 43 SS43.6"),
 ("01_", r"Kinetic Floating Captions", "EXTRACTED -> 46 SS46.7 - confirms current treatment"),
 ("01_", r"6-Phase Retention|^P[1-6]:", "EXTRACTED -> 46 SS46.5 - boundaries only; word counts REJECTED (YouTube caption over-count, operator-known)"),
 ("01_", r"Visual Evidence Manifest", "RECORD - frame paths; underpins the 43 SS43.6 forensic argument"),
 ("01_", r"Actionable Takeaways", "EXTRACTED -> 46 SS46.2/SS46.3"),
 ("01_", r"Foundational Takeaways", "RECORD - section header over the five below"),
 ("02_", r"Executive Summary|Architecture Diagram", "EXTRACTED -> 43 SS43.1/SS43.3"),
 ("02_", r"Pillar 1", "EXTRACTED -> 43 SS43.2"),
 ("02_", r"Pillar 2", "EXTRACTED -> 42 SS42.2"),
 ("02_", r"Pillar 3", "EXTRACTED -> 43 SS43.3/SS43.4"),
 ("02_", r"Pillar 4", "EXTRACTED -> 43 SS43.6"),
 ("02_", r"Actionable Upgrades", "EXTRACTED -> 42 SS42.1, 43 SS43.2/SS43.6, 46 SS46.3"),
 ("02_", r"Immediate Mode", "EXTRACTED -> 43 SS43.1"),
 ("02_", r"Coordinate Transform|Affine|Anchor", "EXTRACTED -> 43 SS43.2"),
 ("02_", r"Wall-Clock|Deterministic Clocking", "EXTRACTED -> 42 SS42.2"),
 ("02_", r"Spring Physics", "EXTRACTED -> 42 SS42.2"),
 ("02_", r"Morphing", "EXTRACTED -> 43 SS43.5 Method A"),
 ("02_", r"Scene Graph|Hierarchical", "EXTRACTED -> 43 SS43.3"),
 ("02_", r"Dirty Flag|Matrix Concatenation", "EXTRACTED -> 43 SS43.4"),
 ("02_", r"Perspective Projection|Z-Stacking", "EXTRACTED -> 43 SS43.3"),
 ("02_", r"Skeletal Mesh|Cutout|Slot-Swapping|Rigging|Winning Standard", "EXTRACTED -> 43 SS43.6"),
 ("02_", r"Improvement 1", "EXTRACTED -> 43 SS43.2"),
 ("02_", r"Improvement 2", "EXTRACTED -> 42 SS42.2"),
 ("02_", r"Improvement 3", "EXTRACTED -> 43 SS43.6"),
 ("02_", r"Improvement 4", "RECORD - balance-scale component; a worked example of 43 SS43.3, build when a page needs it"),
 ("02_", r"Improvement 5|Word-Gap", "EXTRACTED -> 46 SS46.3"),
 ("02_", r"Architectural Blueprint|Implementation Roadmap", "RECORD - sequencing, superseded by our own build order"),
 ("02_", r"Sources|Reference Material|Object Management|Character Rigging|Animation Mechanics|Mechanics of", "RECORD - structural heading; content extracted at its subsections"),
 ("03_", r".*", "PRIOR - extracted into RULE-abstract-to-concrete.md before this pass. Rule 5 (abstract->concrete) adopted; rule 7 (hold scenes) confirms 46 SS46.1; its total absence of evidence discipline explicitly NOT adopted"),
 ("04_", r".*", "EXTRACTED -> 46 SS46.1/SS46.2 - PRIMARY MEASUREMENT, recomputed here rather than quoted"),
 ("05_", r"Executive Summary|Root-Cause|Root Cause", "EXTRACTED -> 45 SS45.1"),
 ("05_", r"Technical Anatomy|Technical Failures", "EXTRACTED -> 45 SS45.3"),
 ("05_", r"Disocclusion|Mathematical Limit|Core Deficit", "EXTRACTED -> 45 SS45.1"),
 ("05_", r"Viability Matrix|Golden Rule", "EXTRACTED -> 45 SS45.2 - closes backlog R5"),
 ("05_", r"Dial Calibration|Master Node|Motion Presets|BANNED", "EXTRACTED -> 45 SS45.3"),
 ("05_", r"Two-Plane|Layer Inpainting|Step Protocol|Why this wins|Professional Standard", "EXTRACTED -> 45 SS45.5"),
 ("05_", r"Actionable Implementation|File Updates", "EXTRACTED -> 45 SS45.3 - left to the Flow lane to apply"),
 ("05_", r"Sources", "RECORD"),
 ("06_", r"Executive Architectural Synthesis|Unified 4-Layer", "EXTRACTED -> 45 SS45.5/SS45.6, 43 SS43.3"),
 ("06_", r"Forensic Bug", "EXTRACTED -> 45 SS45.4 - CONFLICT with 05, held as SOURCES-TO-VERIFY"),
 ("06_", r"Engine 1|Mechanics Under the Hood", "EXTRACTED -> 45 SS45.1"),
 ("06_", r"Disocclusion Limit", "EXTRACTED -> 45 SS45.1"),
 ("06_", r"Dial Matrix|Dial Profile", "EXTRACTED -> 45 SS45.3/SS45.4"),
 ("06_", r"Engine 2|Segmentation|Inpainter|Benchmarks|Boundary Bleed|Execution Graph", "EXTRACTED -> 45 SS45.5"),
 ("06_", r"Engine 3|Ambient Motion|LTX", "EXTRACTED -> 45 SS45.6"),
 ("06_", r"Core Drawing|Doctrine Shift", "RECORD - restates RULE-the-page-is-the-ground, already ours"),
 ("06_", r"Visual Choreography", "EXTRACTED -> 42 SS42.1 context; independently confirms the shipped LP clock"),
 ("06_", r"Master Data Contract|ledger_page", "RECORD - schema proposal; read before building the object-page renderer (backlog N6)"),
 ("06_", r"Pipeline Execution|Summary Engineering", "RECORD - sequencing"),
 ("07_", r"Two-Thirds Power Law|Minimum-Jerk|Neuromuscular|Neurological Mandates", "EXTRACTED -> 42 SS42.1"),
 ("07_", r"Reparameterization", "EXTRACTED -> 42 SS42.1"),
 ("07_", r"Euler Spirals|Fair Curves", "EXTRACTED -> 42 SS42.4"),
 ("07_", r"Coffee Ring", "EXTRACTED -> 44 SS44.2"),
 ("07_", r"Darcy|Washi", "EXTRACTED -> 44 SS44.3"),
 ("07_", r"Kubelka-Munk|Radiative Transfer|Ink Synthesis", "EXTRACTED -> 44 SS44.1"),
 ("07_", r"Zero Volume Collapse|Polar Decomposition|Geodesic Interpolation", "EXTRACTED -> 43 SS43.5 Method B"),
 ("07_", r"Local-Global|Energy Optimization", "EXTRACTED -> 43 SS43.5"),
 ("07_", r"Biharmonic|Dual Quaternion", "EXTRACTED -> 43 SS43.7 - deferred until a prop needs it"),
 ("07_", r"Multi-Plane Geometry|Homography", "EXTRACTED -> 43 SS43.3, 45 SS45.5"),
 ("07_", r"Closed-Form Physics|Numerical Integration|Damped Harmonic|Derivation of", "EXTRACTED -> 42 SS42.2"),
 ("07_", r"Squash and Stretch|Area-Preserving", "EXTRACTED -> 42 SS42.3"),
 ("07_", r"Spacetime Constraints|Elastic Paper", "RECORD - Witkin & Kass carried into 42 SS42.6; paper-curl mechanics deferred"),
 ("07_", r"Cognitive Load|Diagram Comprehension", "EXTRACTED -> 46 SS46.2 (savor beat), 44 SS44.4 (restraint clause)"),
 ("07_", r"Phase Locking|Syllable", "EXTRACTED -> backlog N8(b) - STAGE type should key to syllables, not words"),
 ("07_", r"6-Beat|Kinetic Timeline", "EXTRACTED -> 46 SS46.2 + backlog N8(a); independently confirms the shipped LP clock"),
 ("07_", r"lpHash|Bit-Level", "RECORD - seeded-tilt hash; our template already seeds"),
 ("07_", r"Spring Evaluator", "EXTRACTED -> 42 SS42.2 - working three-regime implementation"),
 ("07_", r"Executive Summary", "EXTRACTED -> 42/43/44 - the four-pillar map this read followed"),
 ("07_", r"Mathematics of|Synthesis|Citations", "RECORD - structural / bibliography"),
 ("08_", r".*", "FILTERED OUTPUT, not a primary. Triaged in VERDICT-research-brief-animation-craft.md; adopted content is re-sourced from the primaries here"),
 ("09_", r"Executive Summary|Three Pillars|Table of Contents", "EXTRACTED -> 48 - the three-track map this read followed"),
 ("09_", r"Center of Mass|Postural Equilibrium|Ankle vs. Hip", "EXTRACTED -> 48 SS48.2"),
 ("09_", r"Inverse Kinematics|FABRIK|FK vs. IK|Kinematic Control Boundaries", "EXTRACTED -> 48 SS48.1 - the most useful rule in the document"),
 ("09_", r"Cutout Rigging|LBS Collapse|DQS|BBW", "EXTRACTED -> 48 SS48.3 - retriggers backlog D5: the trigger is rigging a figure, not a bending prop"),
 ("09_", r"Pseudo-3D Head|Cylindrical Projection", "RECORD - the 35-45 degree three-quarters gate and sprite swap; needed only once a head turns, deferred"),
 ("09_", r"Natural Idling|Respiration|Postural Sway|Contrapposto", "EXTRACTED -> 48 SS48.4"),
 ("09_", r"Secondary Motion|Continuum Drag", "EXTRACTED -> 48 SS48.6 - RESOLVES backlog D3; phase lag and Mp replace the invented 0.22 ratio"),
 ("09_", r"Grasp Taxonom|Cutkosky|Feix", "EXTRACTED -> 48 SS48.5 - fills 43 SS43.6's HandSlot vocabulary"),
 ("09_", r"Reaching Kinematics|Minimum-Jerk Quintic", "EXTRACTED -> 48 SS48.5 - same quintic as 42 SS42.1; confirms it as a shared primitive"),
 ("09_", r"Visuomotor|Aperture Preshaping|Jeannerod", "EXTRACTED -> 48 SS48.5"),
 ("09_", r"Re-Parenting|Virtual Constraint", "EXTRACTED -> 48 SS48.5 - cached matrix, never a hierarchy mutation"),
 ("09_", r"Communication of Mass|APA|Force Coupling|Lift Recoil", "EXTRACTED -> 48 SS48.6 - weight is sold before the lift"),
 ("09_", r"Placement Dynamics|Settling", "EXTRACTED -> 48 SS48.6 - third caller for the 42 SS42.2 spring evaluator"),
 ("09_", r"Two-Handed|Closed Kinematic", "RECORD - master-slave linkage; deferred until a two-handed prop exists"),
 ("09_", r"Zero-Slip|Homography Invariant", "EXTRACTED -> 48 SS48.7 defect 1"),
 ("09_", r"Contact Shadow|AO Slit|Diffuse Cast", "EXTRACTED -> 48 SS48.7 defect 3"),
 ("09_", r"Blinn|Planar Shadow|Affine Shear", "EXTRACTED -> 48 SS48.7 defect 3 - the shear matrix behind the cast shadow"),
 ("09_", r"Disparity Sampling|LDIs|MPIs", "RECORD - uniform disparity sampling; refines 45 SS45.5's multi-plane approach when we build it"),
 ("09_", r"Vanishing Point|Norling|Eye-Line", "EXTRACTED -> 48 SS48.7 defect 4 - the horizon is the invariant anchor; GATEABLE"),
 ("09_", r"Parallax Differentials|Floor-Shear", "EXTRACTED -> 48 SS48.7 defect 2"),
 ("09_", r"Visual Harmonization|Koschmieder|Light Wrap|Substrate", "EXTRACTED -> 48 SS48.8 - arrives at E22's own tokens independently"),
 ("09_", r"Blueprint", "RECORD - seven TypeScript/SVG blueprints; read at build time, not doctrine"),
 ("09_", r"Citation|Authority Registry|Animator Craft|Biomechanics, Motor Control", "RECORD - 20 sources with DOIs, split empirical vs craft doctrine; the pass-2 contract held"),
 ("09_", r"Pipeline Triage|Doctrine Recommendations", "RECORD - its Tier1/2/3 split matches our 47 triage independently"),
 ("09_", r"Production Code Blueprints|Track 1|Track 2|Track 3", "RECORD - structural heading"),
 ("MASTER_RESEARCH_AND_EVIDENCE", r"Forensic Visual Evidence|2.5D Compositing", "EXTRACTED -> 43 SS43.6 - the three-styles-on-one-canvas proof"),
 ("MASTER_RESEARCH_AND_EVIDENCE", r"Diffusion Slideshow|Fatal Flaws|What We Steal|Prompt Audit", "EXTRACTED -> 45 SS45.2, 46 SS46.1"),
 ("MASTER_RESEARCH_AND_EVIDENCE", r"Breath-Gap|Blueprint 4", "EXTRACTED -> 46 SS46.3 - the 0.45s/midpoint variant"),
 ("MASTER_RESEARCH_AND_EVIDENCE", r"Pacing Ledger|Script Map", "EXTRACTED -> 46 SS46.5"),
 ("MASTER_RESEARCH_AND_EVIDENCE", r"Three-Tier Governance|Animation Craft Breakthroughs", "RECORD - added 2026-09-04 after our response; its Tier1/Tier2/Tier3 split matches our ADOPT / ADOPT-AS-OURS / candidate-doctrine triage independently"),
 ("MASTER_RESEARCH_AND_EVIDENCE", r"Grand Synergies|Easy Free Wins", "RECORD - restates 42/43/45 content; its parallax item now correctly targets intensity but still omits tiling_mode, ssaa and quality (see conflict 7)"),
 ("MASTER_RESEARCH_AND_EVIDENCE", r"13.4 Primary Academic", "EXTRACTED -> 46 SS46.1 - the Cutting log-normal claim; the rest duplicate 42-45 sources"),
 ("MASTER_RESEARCH_AND_EVIDENCE", r".*", "DUPLICATE - synthesis of 01/02/05/06/07; extracted at the primary instead"),
 ("MASTER_RESEARCH_INDEX", r".*", "DUPLICATE - index over the same primaries; used to confirm this read covered every domain"),
]


def disp(fname, h):
    for pre, pat, d in RULES:
        if fname.startswith(pre) and re.search(pat, h):
            return d
    return None


rows, missing = [], []
for f in sorted(list(B.glob("*.md")) + list(B.glob("*.txt"))):
    for line in open(f, encoding="utf-8"):
        if re.match(r"^#{2,3} ", line):
            clean = re.sub(r"^#+\s*", "", line.rstrip()).replace("|", "/").strip()
            d = disp(f.name, clean)
            if d is None:
                missing.append((f.name, clean))
            rows.append({"file": f.name, "heading": clean, "disposition": d or "UNASSIGNED"})

print(f"total headings: {len(rows)}   unassigned: {len(missing)}")
for m in missing[:40]:
    print("  MISS:", m[0], "|", m[1])
json.dump(rows, open("idx.json", "w", encoding="utf-8"), indent=1)

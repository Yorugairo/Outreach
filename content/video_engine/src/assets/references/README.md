# Technique visual reference sidecars

This directory is the optional local home for slug-matched technique visual
manifests. A sidecar is evidence about how a reviewed technique action may be
rendered; it is not a replacement for the canonical corpus transcript and it
must not add or rewrite instructional facts.

## Naming and discovery

Use one JSON file per technique, named `<slug>.json` (the service also accepts
the explicit `.technique.json`, `.visual.json`, and `.manifest.json` suffixes).
The `TechniqueManifestService` can receive a different root through
`technique_manifest_root`, `technique_visual_manifest_root`, or
`reference_manifest_root` in `StageContext.configs`; a job may also provide an
explicit `technique_manifest` or `technique_manifest_path` input. Discovery is
deterministic and only accepts files whose name matches the requested slug.

## Required evidence

Every manifest declares top-level `rights` with a source, an allowed
permission (`operator_owned`, `licensed`, `internal`, `public_domain`, or
`cc0`), and `reviewed: true`. Each action is an operator-reviewed causal
recipe:

```json
{
  "id": "two_on_one_wrist_control",
  "state_from": "closed_guard_posture_broken",
  "action": "two_on_one_wrist_control",
  "state_to": "wrist_control_hip_frame",
  "contact": "attacker_wrist",
  "motion_path": "linear",
  "reviewed": true
}
```

`state_from`, `action`, `state_to`, `contact`, and `motion_path` are all
required. References listed in `reference_refs` need their own source,
permission, and review metadata. A missing or unreviewed mechanic fails closed
before instructional rendering; the error lists every affected action.

The sidecar can include a persistent `cast`, `style_preset`, `states`,
`overlays`, `camera`, and sparse `sound_cues`. Those values are deterministic
render inputs. Downloaded reference video, generated pixels, or a URL alone do
not grant permission to use an asset.

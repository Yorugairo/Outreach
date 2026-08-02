# Reviewed vector cast

This directory contains the local, rights-clear metadata for the deterministic
instructional BJJ cast. The pixels are built from Manim primitives by
`src/scenes/bjj_action.py`; these files define the stable practitioner IDs,
color ownership, and layer intent that storyboard/QC code can inspect without
loading Manim.

The two default variants are:

- `white_gi_blue_belt` — persistent `attacker` identity (`#F8FAFC` gi,
  `#2563EB` belt, z-base 20).
- `black_gi_purple_belt` — persistent `defender` identity (`#1F2937` gi,
  `#7C3AED` belt, z-base 10).

`cast_manifest.json` is a reviewed local manifest, not a downloaded reference
asset. It intentionally contains no photographic or generated pixels. Keep
body ownership and z-order explicit when adding a variant; do not encode
technique truth in a generative image.

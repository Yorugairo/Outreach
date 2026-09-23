# Anatomical mesh provenance

This is a generic template brain, not a medical scan or diagnosis of the fighter.

- Upstream: Nilearn's bundled FreeSurfer `fsaverage5` pial cortical surfaces.
- Left: https://raw.githubusercontent.com/nilearn/nilearn/main/nilearn/datasets/data/fsaverage5/pial_left.gii.gz
- Right: https://raw.githubusercontent.com/nilearn/nilearn/main/nilearn/datasets/data/fsaverage5/pial_right.gii.gz
- Documentation: https://nilearn.github.io/stable/modules/generated/nilearn.datasets.fetch_surf_fsaverage.html
- Repository license retained as `NILEARN-LICENSE.txt` (BSD-3-Clause). Upstream FreeSurfer attribution is retained here; this review artifact is not publication clearance for the underlying fight footage.
- Retrieved 2026-09-20. Source SHA-256, vertex and triangle counts are recorded in `surface-record.json`.

`convert_surfaces.py` decompresses the actual GIFTI vertex and triangle arrays without replacing the anatomy with generated blobs. It combines 10,242 vertices and 20,480 triangles per hemisphere into `brain.obj` (20,484 vertices / 40,960 triangles total). Coordinates retain the source anatomical axes: right, anterior, superior.

The Blender brain material contains no image textures, image alpha or billboard. Physical area lights shade the modeled cortical folds. The image-generated skull/background plates are separate compositing layers; they are not represented as a fully modeled skull.

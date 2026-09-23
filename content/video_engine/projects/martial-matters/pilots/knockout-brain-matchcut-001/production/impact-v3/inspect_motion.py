"""Inspect actual Blender mesh projections and orientation across the ejection."""
import bpy
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
scene = bpy.context.scene
root = bpy.data.objects['BRAIN_3D_FLIGHT_ROOT']
meshes = [o for o in root.children if o.type == 'MESH']
records = []
for frame in [17, 31, 59, 65, 68, 75, 80, 95, 111]:
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    points = [world_to_camera_view(scene, scene.camera, o.matrix_world @ v.co)
              for o in meshes for v in o.data.vertices]
    bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
    records.append({'frame': frame, 'effect_seconds': (frame-17)/30,
                    'rotation_radians': list(root.rotation_euler),
                    'projected_bounds_xyz': bounds,
                    'fully_offscreen': bounds[0][1] < 0 or bounds[0][0] > 1 or
                                       bounds[1][1] < 0 or bounds[1][0] > 1})
(HERE/'motion-projections.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
print(json.dumps(records, indent=2))

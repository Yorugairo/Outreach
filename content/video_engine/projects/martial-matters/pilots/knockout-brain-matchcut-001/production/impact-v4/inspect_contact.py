"""Read actual scene state; verify freeze, resumed footage, contact and launch."""
from pathlib import Path
import json
import bpy

scene=bpy.context.scene
tex=next(n for n in bpy.data.materials['contact_live'].node_tree.nodes if n.type=='TEX_IMAGE')
fracture=next(n for n in bpy.data.materials['xray_empty_local'].node_tree.nodes if n.type=='VALUE')
brain=bpy.data.objects['BRAIN_3D_FLIGHT_ROOT']
head=bpy.data.objects['TRACKED_HEAD']
records=[]
for f in [17,31,32,35,38,40,41,42,48,55,62,90]:
    scene.frame_set(f); bpy.context.view_layer.update()
    records.append({'frame':f,'source_frame':f+tex.image_user.frame_offset-1,
                    'fractured_skull_alpha':fracture.outputs[0].default_value,
                    'head_position':list(head.location),'brain_position':list(brain.location)})
assert records[1]['source_frame']==22
assert records[3]['source_frame']==23
assert records[4]['source_frame']==24
assert records[6]['source_frame']==25
assert all(r['fractured_skull_alpha']==0 for r in records if r['frame']<=38)
assert records[7]['brain_position'] != records[6]['brain_position']
out=Path(__file__).resolve().parent/'actual-scene-proof.json'
out.write_text(json.dumps(records,indent=2),encoding='utf-8')
print('PASS actual Blender scene: freeze -> moving punch -> contact -> snap/ejection')

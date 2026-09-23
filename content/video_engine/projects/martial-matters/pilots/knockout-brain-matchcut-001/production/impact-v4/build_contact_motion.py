"""Freeze -> resumed punch -> contact fracture -> head-snap brain ejection."""
from pathlib import Path
import importlib.util
import json
import math
import subprocess
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
spec = importlib.util.spec_from_file_location('xray_base', PROD/'impact-v2/motion/xray_impact.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.ROOT = HERE

# Source frames at 30 fps: original hold=22, contact=24, visible head snap=25.
def source_frame(frame):
    if frame <= 31:
        return 22
    if frame <= 62:
        return 22 + (frame-32)//3
    return 32 + frame-62

TRACK = {
    22:(777,230,0), 23:(802,221,.03), 24:(825,203,.07),
    25:(845,204,.14), 26:(860,199,.20), 27:(870,208,.28),
    28:(890,222,.34), 29:(922,223,.40), 30:(950,239,.43),
    31:(978,255,.43), 32:(990,264,.40), 33:(1000,274,.35),
}

def value(material, amount, frame):
    tree = bpy.data.materials[material].node_tree
    node = next(n for n in tree.nodes if n.type == 'VALUE')
    node.outputs[0].default_value = amount
    node.outputs[0].keyframe_insert('default_value', frame=frame)

def clamp(x):
    return min(1.,max(0.,x))

def build():
    base.build()
    scene = bpy.context.scene
    scene.frame_set(17)
    bpy.context.view_layer.update()
    stage = bpy.data.objects['impact_stage']
    stage.animation_data_clear()
    for f,s in [(17,1),(20,1.35),(27,2.75),(31,3.4),(50,3.4),(78,1),(111,1)]:
        stage.scale=(s,s,s); stage.keyframe_insert('scale',frame=f)
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    head=bpy.context.object; head.name='TRACKED_HEAD'; head.parent=stage; head.location=(0,0,0)
    for obj in list(stage.children):
        if obj.name in ['xray_contact','xray_empty'] or obj.name.startswith(('fracture_','spectral_shard_')):
            obj.parent=head
    # All images except the moving arena are local masked compositing plates.
    # The brain remains a real 40,960-triangle mesh with no image texture.
    for name in ['xray_contact_local','xray_empty_local']:
        tree=bpy.data.materials[name].node_tree
        tree.animation_data_clear()
        # Tight head-only matte: the old broad ellipse included the cage banner
        # and doubled that scenery when the tracked skull moved.
        for node in tree.nodes:
            if node.type == 'MATH' and node.operation == 'MULTIPLY':
                if abs(node.inputs[1].default_value - 1/.095) < .01:
                    node.inputs[1].default_value = 1/.052
                if abs(node.inputs[1].default_value - 1/.175) < .01:
                    node.inputs[1].default_value = 1/.105
            if node.type == 'MAP_RANGE':
                node.inputs[1].default_value=1.10
                node.inputs[2].default_value=.85
        # Difference matte removes unchanged glove/skin/cage pixels from the
        # skull card while the original footage moves beneath it.
        nodes,links=tree.nodes,tree.links
        edited=next(n for n in nodes if n.type=='TEX_IMAGE')
        original=nodes.new('ShaderNodeTexImage')
        original.image=bpy.data.images.load(str(PROD/'impact-v2/contact.png'),check_existing=True)
        difference=nodes.new('ShaderNodeVectorMath'); difference.operation='DISTANCE'
        links.new(edited.outputs['Color'],difference.inputs[0]); links.new(original.outputs['Color'],difference.inputs[1])
        matte=nodes.new('ShaderNodeMapRange'); matte.clamp=True
        matte.inputs[1].default_value=.08; matte.inputs[2].default_value=.20
        links.new(difference.outputs['Value'],matte.inputs[0])
        activate=nodes.new('ShaderNodeMixRGB'); activate.inputs[1].default_value=(1,1,1,1)
        links.new(matte.outputs[0],activate.inputs[2])
        activate.inputs[0].default_value=0; activate.inputs[0].keyframe_insert('default_value',frame=31)
        activate.inputs[0].default_value=1; activate.inputs[0].keyframe_insert('default_value',frame=32)
        shader=next(n for n in nodes if n.type=='MIX_SHADER')
        alpha=shader.inputs[0].links[0].from_socket
        multiply=nodes.new('ShaderNodeMath'); multiply.operation='MULTIPLY'
        links.new(alpha,multiply.inputs[0]); links.new(activate.outputs[0],multiply.inputs[1]); links.new(multiply.outputs[0],shader.inputs[0])
    for mat in bpy.data.materials:
        if mat.name.startswith(('crack_','shard_')):
            mat.node_tree.animation_data_clear()
    brain=bpy.data.objects['BRAIN_3D_FLIGHT_ROOT']
    brain.animation_data_clear()
    brain_mat=bpy.data.materials['cortex_gold_physical'].node_tree
    brain_mat.animation_data_clear()
    tex=next(n for n in bpy.data.materials['contact_live'].node_tree.nodes if n.type=='TEX_IMAGE')
    movie=bpy.data.images.load(str(HERE/'source-frames/source-0000.png'))
    movie.source='SEQUENCE'; tex.image=movie
    tex.image_user.frame_start=1; tex.image_user.frame_duration=90; tex.image_user.use_auto_refresh=True
    # Source sequence is embedded in the editable scene through exact per-frame offsets.
    records=[]
    for frame in range(1,112):
        src=source_frame(frame)
        tex.image_user.frame_offset=src+1-frame
        tex.image_user.keyframe_insert('frame_offset',frame=frame)
        x,y,angle=TRACK[min(33,max(22,src))]
        delta=Vector(((x-777)*.5,-(y-230)*.5,0))
        head.location=delta; head.rotation_euler[2]=angle
        head.keyframe_insert('location',frame=frame); head.keyframe_insert('rotation_euler',frame=frame)
        reveal=clamp((frame-19)/9)
        fade=1-clamp((frame-52)/10)
        fracture=clamp((frame-38)/4)
        value('xray_contact_local',reveal*fade,frame)
        value('xray_empty_local',fracture*fade,frame)
        value('cortex_gold_physical',reveal,frame)
        for i in range(5):
            value(f'crack_{i}',clamp((frame-38)/2)*(.75*(1-clamp((frame-44)/6))),frame)
        for i in range(6):
            value(f'shard_{i}',clamp((frame-40)/3)*.6*(1-clamp((frame-45)/8)),frame)
        # Follow the head until the visible snap. Only then detach and accelerate.
        if frame <= 41:
            offset=Vector((-6.5,18,30))
            c,s=math.cos(angle),math.sin(angle)
            brain.location=delta+Vector((offset.x*c-offset.y*s,offset.x*s+offset.y*c,30))
            brain.rotation_euler=(0,-.15,angle)
        else:
            elapsed=(frame-41)/30
            distance=85*elapsed+280*elapsed*elapsed
            brain.location=(25-distance,30+distance*.72,30+elapsed*25)
            brain.rotation_euler=(elapsed*2.1,-.15+elapsed*3.4,.14-elapsed*2)
        brain.keyframe_insert('location',frame=frame); brain.keyframe_insert('rotation_euler',frame=frame)
        records.append({'output_frame':frame,'source_frame':src,'source_seconds':src/30,
                        'contact':frame==38,'head_snap_launch':frame==41,
                        'fracture_alpha':fracture*fade,'brain_position':list(brain.location)})
    (HERE/'timing-proof.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    scene.frame_start=17; scene.frame_end=111
    scene.frame_set(31)
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'head-snap-3d.blend'))

def main():
    HERE.mkdir(exist_ok=True)
    build()
    sample='--samples' in sys.argv
    frames=[35,41,48] if sample else (range(32,63) if '--patch' in sys.argv else range(17,112))
    folder=HERE/('samples' if sample else 'movie-frames'); folder.mkdir(exist_ok=True)
    scene=bpy.context.scene
    for frame in frames:
        scene.frame_set(frame)
        scene.render.filepath=str(folder/f'frame-{frame:04d}.png')
        bpy.ops.render.render(write_still=True)
    if not sample and '--patch' not in sys.argv:
        subprocess.run(['ffmpeg','-v','error','-y','-framerate','30','-start_number','17',
                        '-i',str(folder/'frame-%04d.png'),'-frames:v','95','-c:v','libx264',
                        '-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(HERE/'xray-impact.mp4')],check=True)

if __name__=='__main__':
    main()

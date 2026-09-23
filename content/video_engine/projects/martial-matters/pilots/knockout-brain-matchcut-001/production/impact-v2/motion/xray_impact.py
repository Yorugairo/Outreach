"""Continuous contact-frame X-ray VFX for Blender 5.2.

Run from the repository root with Blender, for example::

  blender.exe --background --factory-startup --python xray_impact.py -- --samples
  blender.exe --background --factory-startup --python xray_impact.py -- --render

The fight is a frozen background plate. The ejected brain is real anatomical
cortical triangle geometry with physical lighting and multi-axis rotation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import bpy  # type: ignore
from mathutils import Vector  # type: ignore


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT.parent
sys.path.insert(0, str(ASSETS.parent / 'impact-v3'))
from brain_model import build_brain, light_scene
W, H, FPS = 720, 1280, 30
TOTAL_FRAMES = 111
EFFECT_START = 17
EFFECT_END = 111
SAMPLES = (17, 31, 53, 65, 80, 95, 111)
HEAD_SOURCE = (777.0, 230.0)
BRAIN_SOURCE = (764.0, 204.0)
SOURCE_SCALE = 0.5
SOURCE_LEFT, SOURCE_TOP = -120.0, 350.0


def args():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--samples", action="store_true")
    g.add_argument("--render", action="store_true")
    return p.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])


def screen(x: float, y: float) -> Vector:
    """Pixel-space (origin top-left) to Blender world with 1 unit = 1 pixel."""
    return Vector((x - W / 2.0, H / 2.0 - y, 0.0))


def source_xy(x: float, y: float) -> tuple[float, float]:
    return SOURCE_LEFT + x * SOURCE_SCALE, SOURCE_TOP + y * SOURCE_SCALE


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.images):
        for block in list(coll):
            if block.users == 0 and (coll != bpy.data.images or block.name.startswith("impact_")):
                try:
                    coll.remove(block)
                except RuntimeError:
                    pass


def alpha_mode(mat):
    try:
        mat.surface_render_method = "DITHERED"
    except Exception:
        try:
            mat.surface_render_method = "BLENDED"
        except Exception:
            pass


def mat_solid(name, color, strength=1.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    n.clear()
    out = n.new("ShaderNodeOutputMaterial")
    em = n.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1.0)
    em.inputs["Strength"].default_value = strength
    if alpha >= 0.999:
        l.new(em.outputs["Emission"], out.inputs["Surface"])
        return m, None
    tr = n.new("ShaderNodeBsdfTransparent")
    mix = n.new("ShaderNodeMixShader")
    val = n.new("ShaderNodeValue")
    val.outputs[0].default_value = alpha
    l.new(tr.outputs[0], mix.inputs[1])
    l.new(em.outputs[0], mix.inputs[2])
    l.new(val.outputs[0], mix.inputs[0])
    l.new(mix.outputs[0], out.inputs["Surface"])
    alpha_mode(m)
    return m, val


def image_mat(name, path: Path, strength=1.0, *, ellipse=False, lum_mask=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    n.clear()
    out = n.new("ShaderNodeOutputMaterial")
    tex = n.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(path), check_existing=True)
    tex.interpolation = "Linear"
    em = n.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    l.new(tex.outputs["Color"], em.inputs["Color"])
    if not ellipse and not lum_mask:
        l.new(em.outputs[0], out.inputs["Surface"])
        return m, None
    tr = n.new("ShaderNodeBsdfTransparent")
    mix = n.new("ShaderNodeMixShader")
    visible = n.new("ShaderNodeValue")
    visible.outputs[0].default_value = 0.0
    if lum_mask:
        bw = n.new("ShaderNodeRGBToBW")
        ramp = n.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.015
        ramp.color_ramp.elements[1].position = 0.09
        l.new(tex.outputs["Color"], bw.inputs[0])
        l.new(bw.outputs[0], ramp.inputs[0])
        mult = n.new("ShaderNodeMath")
        mult.operation = "MULTIPLY"
        l.new(ramp.outputs[0], mult.inputs[0])
        l.new(visible.outputs[0], mult.inputs[1])
        l.new(mult.outputs[0], mix.inputs[0])
    else:
        uv = n.new("ShaderNodeTexCoord")
        sep = n.new("ShaderNodeSeparateXYZ")
        l.new(uv.outputs["UV"], sep.inputs[0])
        # UV origin is bottom-left; source coordinates are top-left.
        dx = n.new("ShaderNodeMath"); dx.operation = "SUBTRACT"; dx.inputs[1].default_value = HEAD_SOURCE[0] / 1920.0
        dy = n.new("ShaderNodeMath"); dy.operation = "SUBTRACT"; dy.inputs[1].default_value = 1.0 - HEAD_SOURCE[1] / 1080.0
        l.new(sep.outputs[0], dx.inputs[0]); l.new(sep.outputs[1], dy.inputs[0])
        sx = n.new("ShaderNodeMath"); sx.operation = "MULTIPLY"; sx.inputs[1].default_value = 1.0 / 0.095
        sy = n.new("ShaderNodeMath"); sy.operation = "MULTIPLY"; sy.inputs[1].default_value = 1.0 / 0.175
        l.new(dx.outputs[0], sx.inputs[0]); l.new(dy.outputs[0], sy.inputs[0])
        x2 = n.new("ShaderNodeMath"); x2.operation = "MULTIPLY"; l.new(sx.outputs[0], x2.inputs[0]); l.new(sx.outputs[0], x2.inputs[1])
        y2 = n.new("ShaderNodeMath"); y2.operation = "MULTIPLY"; l.new(sy.outputs[0], y2.inputs[0]); l.new(sy.outputs[0], y2.inputs[1])
        add = n.new("ShaderNodeMath"); add.operation = "ADD"; l.new(x2.outputs[0], add.inputs[0]); l.new(y2.outputs[0], add.inputs[1])
        root = n.new("ShaderNodeMath"); root.operation = "SQRT"; l.new(add.outputs[0], root.inputs[0])
        ramp = n.new("ShaderNodeMapRange"); ramp.clamp = True
        ramp.inputs[1].default_value = 1.15; ramp.inputs[2].default_value = 0.70
        ramp.inputs[3].default_value = 0.0; ramp.inputs[4].default_value = 1.0
        l.new(root.outputs[0], ramp.inputs[0])
        mult = n.new("ShaderNodeMath"); mult.operation = "MULTIPLY"
        l.new(ramp.outputs[0], mult.inputs[0]); l.new(visible.outputs[0], mult.inputs[1]); l.new(mult.outputs[0], mix.inputs[0])
    l.new(tr.outputs[0], mix.inputs[1]); l.new(em.outputs[0], mix.inputs[2]); l.new(mix.outputs[0], out.inputs["Surface"])
    alpha_mode(m)
    return m, visible


def plane(name, width, height, cx, cy, z, material):
    verts = [(-width / 2, -height / 2, 0), (width / 2, -height / 2, 0),
             (width / 2, height / 2, 0), (-width / 2, height / 2, 0)]
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.uv_layers.new(name="UVMap")
    for loop, uv in zip(mesh.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        mesh.uv_layers.active.data[loop.index].uv = uv
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = screen(cx, cy); obj.location.z = z
    obj.data.materials.append(material)
    return obj


def adopt(obj, parent):
    location = obj.location.copy()
    obj.parent = parent
    obj.location = location - parent.location


def key_value(value_node, keys):
    for frame, value in keys:
        value_node.outputs[0].default_value = value
        value_node.outputs[0].keyframe_insert("default_value", frame=frame)


def curve(name, points, material, width=1.2):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"; data.resolution_u = 2; data.bevel_depth = width; data.bevel_resolution = 2
    sp = data.splines.new("POLY"); sp.points.add(len(points) - 1)
    for p, (x, y) in zip(sp.points, points):
        p.co = (*screen(x, y), 1.0)
    obj = bpy.data.objects.new(name, data); bpy.context.collection.objects.link(obj); obj.data.materials.append(material)
    return obj


def shard(name, x, y, size, material):
    pts = [(-size * .55, -size * .15, 0), (-size * .10, -size * .55, 0),
           (size * .55, -size * .05, 0), (size * .18, size * .50, 0)]
    mesh = bpy.data.meshes.new(name + "Mesh"); mesh.from_pydata(pts, [], [(0, 1, 2, 3)])
    mesh.uv_layers.new(name="UVMap")
    obj = bpy.data.objects.new(name, mesh); bpy.context.collection.objects.link(obj); obj.location = screen(x, y); obj.data.materials.append(material)
    return obj


def setup_scene():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.cycles.transparent_max_bounces = 64
    scene.cycles.max_bounces = 2
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = W, H, 100
    scene.render.fps = FPS; scene.frame_start = 1; scene.frame_end = TOTAL_FRAMES
    scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    if hasattr(scene.render, "use_motion_blur"):
        scene.render.use_motion_blur = True
        if hasattr(scene.render, "motion_blur_shutter"): scene.render.motion_blur_shutter = 0.65
    world = scene.world or bpy.data.worlds.new("impact_world"); scene.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.002, 0.004, 0.01, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.02
    cam_data = bpy.data.cameras.new("impact_camera"); cam = bpy.data.objects.new("impact_camera", cam_data); bpy.context.collection.objects.link(cam)
    cam.location = (0, 0, 1000); cam_data.clip_end = 5000; cam_data.type = "ORTHO"; cam_data.ortho_scale = H; scene.camera = cam
    # Blender 5.2 background builds expose the compositor through a node group
    # rather than Scene.node_tree; emission materials remain deterministic on
    # both the UI and background paths, so the optional glow graph is omitted.


def build():
    clear(); setup_scene()
    contact = ASSETS / "contact.png"; xray = ASSETS / "xray-clean-empty.png"; empty = ASSETS / "xray-empty.png"; brain = ASSETS.parent / 'impact-v3/assets/brain.obj'
    if not contact.is_file(): raise FileNotFoundError(contact)
    if not xray.is_file(): raise FileNotFoundError(xray)
    if not empty.is_file(): empty = xray
    if not brain.is_file(): raise FileNotFoundError(brain)
    bg = ASSETS / "contact-blur.png"
    if not bg.is_file() and shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(contact), "-vf", "scale=480:270,gblur=sigma=12,scale=1920:1080:flags=bicubic", str(bg)], check=True)
    if not bg.is_file(): bg = contact
    bgm, _ = image_mat("impact_background", bg, 0.55)
    plane("background", 2275.6, 1280, 360, 640, -30, bgm)
    dark, _ = mat_solid("impact_dark", (0.005, 0.012, 0.025), 0.3, 0.23); plane("background_grade", 720, 1280, 360, 640, -20, dark)
    live_m, _ = image_mat("contact_live", contact, 1.0); live = plane("contact_plate", 960, 540, 360, 620, 0, live_m)
    hx, hy = source_xy(*HEAD_SOURCE); bx, by = source_xy(*BRAIN_SOURCE)
    by -= 5
    anchor = screen(hx, hy)
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=anchor); stage = bpy.context.object; stage.name = "impact_stage"
    for f, s in ((1, 1.0), (EFFECT_START, 1.0), (20, 1.35), (27, 2.75), (31, 3.4), (40, 3.4), (TOTAL_FRAMES, 3.4)):
        stage.scale = (s, s, s); stage.keyframe_insert("scale", frame=f)
    stage.scale = (1, 1, 1)
    adopt(live, stage)
    xm, xv = image_mat("xray_contact_local", xray, 1.15, ellipse=True); xobj = plane("xray_contact", 960, 540, 360, 620, 2, xm); adopt(xobj, stage)
    em, ev = image_mat("xray_empty_local", empty, 1.15, ellipse=True); eobj = plane("xray_empty", 960, 540, 360, 620, 2.1, em); adopt(eobj, stage)
    key_value(xv, ((1, 0), (19, 0), (22, .24), (25, .72), (28, 1), (TOTAL_FRAMES, 1)))
    key_value(ev, ((1, 0), (59, 0), (60, .08), (65, .55), (69, 1), (TOTAL_FRAMES, 1)))
    flash, fv = mat_solid("xray_flash", (0.65, 0.88, 1.0), 2.5, 0.0); flash_obj = plane("xray_flash", 720, 1280, 360, 640, 14, flash); key_value(fv, ((1, 0), (19, 0), (21, .62), (24, .14), (28, 0)))
    scanner, sv = mat_solid("scanner_line", (0.25, 0.85, 1.0), 4.0, 0.0); scan = plane("scanner_line", 310, 8, hx, hy - 100, 9, scanner); adopt(scan, stage); key_value(sv, ((1, 0), (19, .0), (20, .55), (26, .55), (28, 0)))
    scan.location = screen(hx, hy - 100); scan.location.z = 9; scan.keyframe_insert("location", frame=19); scan.location = screen(hx, hy + 105); scan.location.z = 9; scan.keyframe_insert("location", frame=28)
    # Fracture paths are spatially registered to the supplied source head.
    cracks = [((725, 164), (748, 188), (738, 214), (762, 237)), ((793, 159), (779, 184), (803, 208), (796, 232)), ((730, 207), (710, 226), (718, 252), (748, 265)), ((815, 198), (834, 222), (826, 250), (807, 269)), ((752, 239), (773, 252), (783, 273))]
    for i, path in enumerate(cracks):
        cm, cv = mat_solid(f"crack_{i}", (0.28, 0.88, 1.0), 2.0, 0.0); c = curve(f"fracture_{i}", [source_xy(*p) for p in path], cm, .18); c.location.z = 4; adopt(c, stage); key_value(cv, ((1, 0), (40 + i * 3, 0), (52 + i * 3, .8), (70, 0), (TOTAL_FRAMES, 0)))
    for i, (x, y, size) in enumerate(((719, 181, 18), (827, 182, 16), (712, 238, 14), (840, 241, 11), (770, 154, 12), (803, 277, 10))):
        sm, sv2 = mat_solid(f"shard_{i}", (0.45, 0.92, 1.0), 4.0, 0.0); sh = shard(f"spectral_shard_{i}", *source_xy(x, y), size * .5, sm); adopt(sh, stage); key_value(sv2, ((1, 0), (45 + i, 0), (52 + i, .65), (63 + i, .2), (75, 0)))
        sh.rotation_euler[2] = (-.35 + .14 * i); sh.keyframe_insert("rotation_euler", frame=50 + i); sh.rotation_euler[2] += .8; sh.keyframe_insert("rotation_euler", frame=70 + i)
    brain_obj, bv = build_brain()
    brain_obj.location = screen(bx, by); brain_obj.location.z = 30
    adopt(brain_obj, stage)
    light_scene()
    key_value(bv, ((1, 0), (19, 0), (22, .24), (25, .72), (28, 1), (TOTAL_FRAMES, 1)))
    # World-space flight keys are converted into stage-local coordinates so the
    # camera push stays anchored to the victim head while the brain exits left/up.
    def brain_world(frame, sx, sy, rot):
        target = screen(sx, sy) - anchor
        target.z = 30 + max(0, frame - 59) * .45
        brain_obj.location = target
        spin = max(0, frame - 59) / 34
        brain_obj.rotation_euler = (spin * .9, -.15 + spin * 1.5, rot)
        brain_obj.keyframe_insert("location", frame=frame); brain_obj.keyframe_insert("rotation_euler", frame=frame)
    brain_world(1, bx, by, 0.0); brain_world(59, bx, by, 0.0); brain_world(68, 226, 420, .24); brain_world(80, 145, 350, -.42); brain_world(92, 40, 240, -.90); brain_world(99, -105, 140, -1.25); brain_world(TOTAL_FRAMES, -150, 95, -1.35)
    state = {"schema": "martial_matters_impact_v2_xray.v1", "fps": FPS, "frames": TOTAL_FRAMES, "effect_frames": [EFFECT_START, EFFECT_END], "head_source_px": HEAD_SOURCE, "brain_source_px": BRAIN_SOURCE, "stage_anchor_screen_px": [hx, hy], "timing": {"xray_start_effect_s": .10, "fracture_start_effect_s": .80, "launch_effect_s": 1.45, "brain_offscreen_effect_s": 2.60, "effect_end_s": 95 / FPS}, "assets": {k: str(v) for k, v in {"contact": contact, "xray": xray, "empty": empty, "brain": brain}.items()}}
    (ROOT / "motion-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "xray-impact.blend"))
    return state


def render_frames(frames):
    out = ROOT / "samples" if len(frames) != 95 else ROOT / "movie-frames"
    out.mkdir(exist_ok=True)
    scene = bpy.context.scene
    for f in frames:
        scene.frame_set(f); scene.render.filepath = str(out / f"frame-{f:04d}.png"); bpy.ops.render.render(write_still=True)
    return out


def encode():
    out = ROOT / "xray-impact.mp4"
    ff = shutil.which("ffmpeg")
    if not ff: raise RuntimeError("ffmpeg not found on PATH")
    subprocess.run([ff, "-y", "-v", "error", "-framerate", str(FPS), "-start_number", str(EFFECT_START), "-i", str(ROOT / "movie-frames" / "frame-%04d.png"), "-frames:v", "95", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], check=True)
    return out


def main():
    a = args(); state = build()
    if a.samples:
        render_frames(SAMPLES)
        print(json.dumps({"samples": str(ROOT / "samples"), "state": state}, indent=2))
    else:
        render_frames(range(EFFECT_START, EFFECT_END + 1)); out = encode(); state["mp4"] = str(out); state["sha256"] = hashlib.sha256(out.read_bytes()).hexdigest(); (ROOT / "motion-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8"); print(json.dumps({"mp4": str(out), "sha256": state["sha256"]}, indent=2))


if __name__ == "__main__":
    main()

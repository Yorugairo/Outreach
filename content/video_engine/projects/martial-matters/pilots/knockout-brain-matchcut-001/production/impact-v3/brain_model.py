"""Real cortical surface geometry, never an image-textured billboard."""
from pathlib import Path
import json
import math

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent


def build_brain():
    source = HERE / 'assets' / 'brain.obj'
    if not source.is_file():
        raise FileNotFoundError(source)
    vertices, faces = [], []
    for line in source.read_text(encoding='utf-8').splitlines():
        bits = line.split()
        if not bits:
            continue
        if bits[0] == 'v':
            vertices.append(tuple(float(x) for x in bits[1:4]))
        elif bits[0] == 'f':
            ids = [int(x.split('/')[0]) for x in bits[1:]]
            faces.append(tuple(i-1 if i > 0 else len(vertices)+i for i in ids))
    data = bpy.data.meshes.new('anatomical_cortical_surface')
    data.from_pydata(vertices, [], faces)
    obj = bpy.data.objects.new('cortex_import', data)
    bpy.context.collection.objects.link(obj)
    meshes = [obj]
    if not meshes:
        raise RuntimeError('Brain import contains no triangle mesh')
    # OBJ importer can apply an axis transform. Bake it before interpreting the
    # source's anatomical RAS coordinates: x=right,y=anterior,z=superior.
    points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    lo = Vector(tuple(min(v[i] for v in points) for i in range(3)))
    hi = Vector(tuple(max(v[i] for v in points) for i in range(3)))
    center = (lo + hi) * .5
    # Import configured to retain original coordinates below; the entire object
    # has true depth and cortical folds, rendered with area lights.
    scale = 54.0 / (hi.y - lo.y)
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    root = bpy.context.object
    root.name = 'BRAIN_3D_FLIGHT_ROOT'
    mat = bpy.data.materials.new('cortex_gold_physical')
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    surface = nodes.new('ShaderNodeBsdfPrincipled')
    surface.inputs['Base Color'].default_value = (.52, .24, .055, 1)
    surface.inputs['Metallic'].default_value = .22
    surface.inputs['Roughness'].default_value = .34
    surface.inputs['Emission Color'].default_value = (.5, .15, .01, 1)
    surface.inputs['Emission Strength'].default_value = .06
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    visible = nodes.new('ShaderNodeValue')
    visible.outputs[0].default_value = 0
    blend = nodes.new('ShaderNodeMixShader')
    links.new(visible.outputs[0], blend.inputs[0])
    links.new(transparent.outputs[0], blend.inputs[1])
    links.new(surface.outputs[0], blend.inputs[2])
    links.new(blend.outputs[0], out.inputs[0])
    record = []
    for index, obj in enumerate(meshes):
        matrix = obj.matrix_world.copy()
        for vertex in obj.data.vertices:
            p = (matrix @ vertex.co - center) * scale
            vertex.co = (p.y, p.z, p.x)
        obj.matrix_world.identity()
        obj.parent = root
        obj.name = f'CORTICAL_HEMISPHERE_{index:02d}'
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        record.append({'name': obj.name, 'vertices': len(obj.data.vertices),
                       'faces': len(obj.data.polygons)})
    (HERE / 'mesh-inspection.json').write_text(json.dumps({
        'source': str(source), 'source_bounds': [list(lo), list(hi)],
        'mesh_objects': record, 'image_textures_on_brain': 0,
        'screen_mapping': 'anterior->right,superior->up,right->camera',
        'uniform_scale': scale}, indent=2), encoding='utf-8')
    return root, visible


def light_scene():
    for name, pos, color, energy, size in [
        ('brain_key', (-250, 400, 500), (1, .77, .43), 1700000, 260),
        ('brain_rim', (300, 300, 140), (.15, .7, 1), 2200000, 180),
        ('brain_fill', (-180, -250, 380), (.4, .6, 1), 500000, 300),
    ]:
        data = bpy.data.lights.new(name, 'AREA')
        data.energy, data.color, data.shape, data.size = energy, color, 'DISK', size
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = pos
        target = Vector((-92, 175, 45))
        obj.rotation_euler = (target - obj.location).to_track_quat('-Z', 'Y').to_euler()

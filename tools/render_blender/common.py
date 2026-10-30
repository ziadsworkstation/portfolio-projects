"""Piezas comunes para los renders de Blender (Cycles): materiales, primitivas, estudio y render."""
import math, os
import bpy
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ------------------------------------------------------------------ materiales
def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1]

def principled(name, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    for k, v in kw.items(): b.inputs[k].default_value = v
    return m

COBALT = principled('cobalt', **{'Base Color': srgb('#1534c8'), 'Roughness': 0.3, 'Coat Weight': 1.0, 'Coat Roughness': 0.05})
CORE = principled('nucleo', **{'Base Color': srgb('#1430d6'), 'Roughness': 0.6})
FROST = principled('resina', **{'Base Color': srgb('#eef1f8'), 'Roughness': 0.42, 'Transmission Weight': 1.0, 'IOR': 1.49})
CLEAR = principled('vidrio', **{'Base Color': srgb('#f4f7fb'), 'Roughness': 0.02, 'Transmission Weight': 1.0, 'IOR': 1.5})
ALU = principled('aluminio', **{'Base Color': srgb('#c9cbce'), 'Metallic': 1.0, 'Roughness': 0.32})
SCREEN = principled('pantalla', **{'Base Color': srgb('#101114'), 'Roughness': 0.15})
PAPER = principled('estudio', **{'Base Color': srgb('#ecebe8'), 'Roughness': 0.95})

# ------------------------------------------------------------------ geometría
def link(o, parent=None):
    if o.name not in bpy.context.collection.objects: bpy.context.collection.objects.link(o)
    if parent: o.parent = parent
    return o

def empty(name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None); e.location = loc; return link(e, parent)

def box(size, loc, mat, bevel=0.0, seg=6, parent=None, name='box'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        md = o.modifiers.new('bevel', 'BEVEL'); md.width = bevel; md.segments = seg; md.limit_method = 'NONE'
    bpy.ops.object.shade_smooth() if bevel else None
    o.data.materials.append(mat); o.parent = parent; return o

def cyl(r, depth, loc, mat, rot=(0, 0, 0), parent=None, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.active_object; bpy.ops.object.shade_auto_smooth() if hasattr(bpy.ops.object, 'shade_auto_smooth') else bpy.ops.object.shade_smooth()
    o.data.materials.append(mat); o.parent = parent; return o

def fillet(pts, r, closed):
    P = [Vector(p) for p in pts]; n = len(P); out = []
    idx = range(n) if closed else range(1, n - 1)
    if not closed: out.append(P[0])
    for i in idx:
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        u, v = (b - a), (c - b); rr = min(r, u.length / 2, v.length / 2)
        p0, p2 = b - u.normalized() * rr, b + v.normalized() * rr
        for k in range(17):
            t = k / 16; out.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * b + t * t * p2)
    if not closed: out.append(P[-1])
    return out

def tube(pts, radius, r, closed=False, mat=COBALT, parent=None, name='tubo'):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = radius; cu.bevel_resolution = 8; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); P = fillet(pts, r, closed)
    sp.points.add(len(P) - 1)
    for i, p in enumerate(P): sp.points[i].co = (*p, 1)
    sp.use_cyclic_u = closed
    o = bpy.data.objects.new(name, cu); o.data.materials.append(mat); link(o, parent); return o

# ------------------------------------------------------------------ estudio fotográfico
def sweep(wall_y=1.2, R=1.4, half=8, front=-8.0, top=8.0):
    import bmesh
    prof = [(front, 0.0), (wall_y - R, 0.0)]
    for k in range(1, 24):
        a = -math.pi / 2 + k / 24 * math.pi / 2
        prof.append((wall_y - R + R * math.cos(a) * 1 + 0, R + R * math.sin(a)))
    prof.append((wall_y, R)); prof.append((wall_y, top))
    me = bpy.data.meshes.new('fondo'); bm = bmesh.new()
    L = [bm.verts.new((-half, y, z)) for y, z in prof]; Rv = [bm.verts.new((half, y, z)) for y, z in prof]
    for i in range(len(prof) - 1): bm.faces.new((L[i], L[i + 1], Rv[i + 1], Rv[i]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('fondo', me); link(o); o.data.materials.append(PAPER)
    for p in o.data.polygons: p.use_smooth = True
    return o

def light(name, loc, target, size, power, color=(1, 0.98, 0.95)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.shape = 'RECTANGLE'; ld.size = size[0]; ld.size_y = size[1]
    ld.energy = power; ld.color = color
    o = bpy.data.objects.new(name, ld); link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o

def camera(loc, target, lens=70):
    cd = bpy.data.cameras.new('cam'); cd.lens = lens
    o = bpy.data.objects.new('cam', cd); link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = o; return o

def set_world(strength=0.06, color=(1, 1, 1, 1)):
    world = bpy.data.worlds.new('mundo'); sc.world = world; world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = color
    world.node_tree.nodes['Background'].inputs[1].default_value = strength

def render(out, w, h, spp, transparent=False, expo=-1.7):
    r = sc.render; r.engine = 'CYCLES'; r.resolution_x = w; r.resolution_y = h; r.resolution_percentage = 100
    r.film_transparent = transparent
    r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA' if transparent else 'RGB'; r.filepath = out
    cy = sc.cycles; cy.device = 'CPU'; cy.samples = spp; cy.use_denoising = True
    cy.max_bounces = 16; cy.transmission_bounces = 16; cy.glossy_bounces = 8; cy.caustics_reflective = False
    sc.view_settings.view_transform = 'Khronos PBR Neutral'
    sc.view_settings.exposure = float(os.environ.get('EXPO', expo))
    bpy.ops.render.render(write_still=True)
    print('ok', out)

def shadow_catcher(size=40):
    bpy.ops.mesh.primitive_plane_add(size=size); f = bpy.context.active_object; f.is_shadow_catcher = True; return f


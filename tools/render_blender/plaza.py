"""Renders fotográficos de «Plaza abierta» con Blender (Cycles).

  python3 tools/render_blender/plaza.py VISTA SALIDA.png [ANCHO ALTO MUESTRAS]
  VISTA: familia | out | in | calle | corte

Los módulos: estructura de tubo y forjados lacados en cobalto; cerramientos de vidrio acanalado
esmerilado que se tiñe de cobalto hacia el suelo; banda de vidrio claro a la altura de quien trabaja.
La ciudad, como una maqueta blanca.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

VIEW = sys.argv[1] if len(sys.argv) > 1 else 'familia'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/plaza.png'
W, H, SPP = (int(a) for a in (sys.argv[3:6] if len(sys.argv) > 5 else (1600, 1000, 128)))

def fluted(name='acanalado', flutes=26.0):
    """Vidrio acanalado esmerilado con degradado: cobalto abajo, casi blanco arriba (coordenadas de objeto)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.3; b.inputs['Transmission Weight'].default_value = 1.0; b.inputs['IOR'].default_value = 1.5
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Generated'], sep.inputs[0])
    ramp = N.new('ShaderNodeValToRGB'); L.new(sep.outputs['Z'], ramp.inputs[0])
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = srgb('#1a3bd6')
    ramp.color_ramp.elements[1].position = 0.75; ramp.color_ramp.elements[1].color = srgb('#eef2fb')
    L.new(ramp.outputs['Color'], b.inputs['Base Color'])
    wave = N.new('ShaderNodeTexWave'); wave.wave_type = 'BANDS'; wave.bands_direction = 'X'; wave.wave_profile = 'SIN'
    wave.inputs['Scale'].default_value = flutes
    L.new(tc.outputs['Object'], wave.inputs['Vector'])
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.45; bump.inputs['Distance'].default_value = 0.02
    L.new(wave.outputs['Fac'], bump.inputs['Height']); L.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m

FLUTE = fluted()
WHITE = principled('maqueta', **{'Base Color': srgb('#f1f0ed'), 'Roughness': 0.9})
GROUND = principled('suelo', **{'Base Color': srgb('#e4e2dd'), 'Roughness': 0.95})
FIG = principled('figura', **{'Base Color': srgb('#e9e7e2'), 'Roughness': 0.7})
FIG_DK = principled('figura2', **{'Base Color': srgb('#2b2c30'), 'Roughness': 0.7})
CANVAS = principled('lona', **{'Base Color': srgb('#f4f1ea'), 'Roughness': 0.9})

def person(loc, sit=False, rot=0.0, mat=FIG, parent=None):
    """Figura de maqueta: tronco que se ensancha a los hombros y cabeza esférica separada."""
    g = empty('persona', loc, parent); g.rotation_euler[2] = rot
    z0, hb = (0.48, 0.66) if sit else (0.0, 1.38)
    if sit: box((0.34, 0.44, 0.15), (0, 0.17, 0.5), mat, bevel=0.07, seg=6, parent=g)
    bpy.ops.mesh.primitive_cone_add(radius1=0.15 if not sit else 0.18, radius2=0.2, depth=hb, location=(0, 0, z0 + hb / 2), vertices=48)
    t = bpy.context.active_object; t.parent = g; t.data.materials.append(mat); t.scale[1] = 0.72
    md = t.modifiers.new('bevel', 'BEVEL'); md.width = 0.07; md.segments = 6; md.limit_method = 'NONE'
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(0, 0, z0 + hb + 0.15), segments=32, ring_count=16)
    h = bpy.context.active_object; h.parent = g; h.data.materials.append(mat)
    for o in g.children: o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
    return g

def panel(w, h, loc, rot_z, parent, mat=FLUTE):
    o = box((w, 0.035, h), (0, 0, 0), mat, parent=parent); o.location = loc; o.rotation_euler[2] = rot_z; return o

def shell(g, Wd, Dp, Hh, z0, front_clear=(0.9, 2.3), open_front=None):
    """Cerramiento: esquinas de tubo, paneles acanalados, banda clara al frente (o hueco de barra)."""
    for sx in (-1, 1):
        for sy in (-1, 1): cyl(0.13, Hh, (sx * Wd / 2, sy * Dp / 2, z0 + Hh / 2), COBALT, parent=g)
    panel(Wd - 0.2, Hh, (0, Dp / 2, z0 + Hh / 2), 0, g)                                   # trasera
    for sx in (-1, 1): panel(Dp - 0.2, Hh, (sx * Wd / 2, 0, z0 + Hh / 2), math.pi / 2, g)  # laterales
    lo, hi = open_front or front_clear
    panel(Wd - 0.2, lo, (0, -Dp / 2, z0 + lo / 2), 0, g)
    panel(Wd - 0.2, Hh - hi, (0, -Dp / 2, z0 + (hi + Hh) / 2), 0, g)
    if not open_front: box((Wd - 0.2, 0.02, hi - lo), (0, -Dp / 2, z0 + (lo + hi) / 2), CLEAR, parent=g)
    box((Wd - 0.3, Dp - 0.3, 0.02), (0, 0, z0 + Hh - 0.03), principled('luz', **{'Emission Color': (1, 0.96, 0.9, 1), 'Emission Strength': 3.0}), parent=g)

def slab(g, Wd, Dp, z):
    box((Wd + 0.4, Dp + 0.4, 0.22), (0, 0, z + 0.11), COBALT, bevel=0.1, seg=8, parent=g)

def worktop(g, Wd, z, seats, y):
    box((Wd - 0.4, 0.6, 0.035), (0, y, z + 0.74), FROST, bevel=0.01, seg=3, parent=g)
    box((Wd - 0.5, 0.5, 0.01), (0, y, z + 0.74), CORE, parent=g)
    for x in seats:
        person((x, y + 0.6, z), sit=True, rot=math.pi, mat=FIG, parent=g)
        box((0.3, 0.2, 0.012), (x, y + 0.05, z + 0.765), ALU, parent=g)

def cabina(loc, rot=0.0, vending=True):
    g = empty('cabina', loc); g.rotation_euler[2] = rot
    box((2.6, 2.6, 0.16), (0, 0, 0.08), COBALT, bevel=0.05, parent=g)
    shell(g, 2.4, 2.4, 2.6, 0.16, front_clear=(0.85, 2.25))
    slab(g, 2.4, 2.4, 2.76)
    worktop(g, 2.4, 0.16, [0.0], -0.8)
    if vending:
        v = empty('maquina', (1.85, -0.4, 0), g)
        box((0.95, 0.8, 1.95), (0, 0, 0.975), FROST, bevel=0.12, seg=8, parent=v)
        for i in range(4):
            for j in range(3): box((0.16, 0.25, 0.2), (-0.12 + (j - 1) * 0.2, 0, 0.75 + i * 0.3), CORE, bevel=0.03, parent=v)
    return g

def spiral(g, cx, cy, top, end=math.pi):
    rise = 0.19; n = round(top / rise); da = 0.44; a0 = end - (n - 1) * da
    cyl(0.08, top + 1.0, (cx, cy, (top + 1.0) / 2), COBALT, parent=g)
    for i in range(n):
        a = a0 + i * da
        s = box((0.95, 0.4, 0.06), (cx + 0.5 * math.cos(a), cy + 0.5 * math.sin(a), (i + 1) * rise), COBALT, bevel=0.02, parent=g); s.rotation_euler[2] = a
    pts = [(cx + 0.95 * math.cos(a0 + k * da / 6), cy + 0.95 * math.sin(a0 + k * da / 6), rise + k * rise / 6 + 0.9) for k in range(n * 6 + 1)]
    cu = bpy.data.curves.new('pasamanos', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.03; cu.bevel_resolution = 6
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts): sp.points[i].co = (*p, 1)
    o = bpy.data.objects.new('pasamanos', cu); o.data.materials.append(COBALT); link(o, g)
    zanca = [(cx + 0.97 * math.cos(a0 + k * da / 6), cy + 0.97 * math.sin(a0 + k * da / 6), rise + k * rise / 6 - 0.02) for k in range(n * 6 + 1)]
    cz = bpy.data.curves.new('zanca', 'CURVE'); cz.dimensions = '3D'; cz.bevel_depth = 0.035; cz.bevel_resolution = 6
    sz = cz.splines.new('POLY'); sz.points.add(len(zanca) - 1)
    for i, p in enumerate(zanca): sz.points[i].co = (*p, 1)
    oz = bpy.data.objects.new('zanca', cz); oz.data.materials.append(COBALT); link(oz, g)

def kiosco(loc, rot=0.0, floors=2):
    g = empty('quiosco', loc); g.rotation_euler[2] = rot
    Wd, Dp = 4.8, 2.4
    box((Wd + 0.2, Dp + 0.2, 0.16), (0, 0, 0.08), COBALT, bevel=0.05, parent=g)
    shell(g, Wd, Dp, 2.8, 0.16, open_front=(1.05, 2.45))
    box((Wd - 0.1, 0.45, 0.05), (0, -Dp / 2 - 0.12, 1.23), FROST, bevel=0.015, parent=g)          # barra
    fl = empty('toldo', (0, -Dp / 2, 2.62), g); fl.rotation_euler[0] = -0.32
    box((Wd - 0.2, 1.05, 0.05), (0, -0.52, 0), COBALT, bevel=0.02, parent=fl)
    person((-0.9, 0.2, 0.16), mat=FIG_DK, parent=g)
    for x in (-1.5, -0.5, 0.5, 1.5):
        st = empty('taburete', (x, -Dp / 2 - 0.75, 0), g)
        cyl(0.18, 0.05, (0, 0, 0.76), COBALT, parent=st); cyl(0.025, 0.74, (0, 0, 0.37), COBALT, parent=st); cyl(0.16, 0.02, (0, 0, 0.01), COBALT, parent=st)
    person((-0.5, -Dp / 2 - 0.9, 0.28), sit=True, mat=FIG, parent=g)
    person((1.0, -Dp / 2 - 0.85, 0), mat=FIG_DK, parent=g)
    top = 0.16 + 2.8; slab(g, Wd, Dp, top); top += 0.22
    if floors > 1:
        shell(g, Wd, Dp, 2.7, top, front_clear=(0.75, 2.3))
        worktop(g, Wd, top, [-1.4, 0.0, 1.4], -0.8)
        top += 2.7; slab(g, Wd, Dp, top); top += 0.22
    e = 0.05; xs, ys, y = Wd / 2 + 0.15, Dp / 2 + 0.15, top + 1.0
    loop = [(xs, -0.35, y), (xs, ys, y), (-xs, ys, y), (-xs, -ys, y), (xs, -ys, y), (xs, -0.55 - 0.4, y)]
    tube(loop, 0.035, 0.55, parent=g); tube([(p[0], p[1], top + 0.5) for p in loop], 0.022, 0.55, parent=g)
    for (x, yy) in ((-xs, -ys), (-xs, ys), (xs, ys), (xs, -ys), (0, ys), (0, -ys)): cyl(0.022, 1.0, (x, yy, top + 0.5), COBALT, parent=g)
    cyl(0.03, 2.4, (-0.9, 0, top + 1.2), COBALT, parent=g)
    bpy.ops.mesh.primitive_cone_add(radius1=1.35, depth=0.35, location=(-0.9, 0, top + 2.35), vertices=64); c = bpy.context.active_object; c.data.materials.append(CANVAS); c.parent = g
    cyl(0.4, 0.03, (-0.9, 0, top + 0.74), FROST, parent=g)
    person((-0.15, 0, top), sit=True, rot=math.pi / 2, parent=g); person((-1.65, 0, top), sit=True, rot=-math.pi / 2, mat=FIG_DK, parent=g)
    spiral(g, Wd / 2 + 1.3, 0.1, top, end=math.pi)
    return g

def tree(loc, s=1.0):
    g = empty('arbol', loc)
    cyl(0.14 * s, 3.2 * s, (0, 0, 1.6 * s), WHITE, parent=g, verts=24)
    for dx, dy, dz, r in ((0, 0, 4.2, 2.0), (0.9, 0.4, 3.8, 1.4), (-0.8, -0.5, 4.0, 1.5), (0.2, -0.3, 5.0, 1.3)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r * s, location=(dx * s, dy * s, dz * s), segments=48, ring_count=24)
        o = bpy.context.active_object; o.scale[2] = 0.85; bpy.ops.object.shade_smooth(); o.data.materials.append(WHITE); o.parent = g
    return g

def city():
    bpy.ops.mesh.primitive_plane_add(size=400); gnd = bpy.context.active_object; gnd.data.materials.append(GROUND)
    for x in range(-24, 27, 7): tree((x, 9.5, 0))
    for x, y in ((-17, -9), (19, -10)): tree((x, y, 0), 0.9)
    for x, y, w, d, h in ((-30, 34, 40, 12, 19), (12, 36, 44, 12, 23), (52, 20, 12, 40, 20), (-58, 8, 12, 40, 18)):
        box((w, d, h), (x, y, h / 2), WHITE)
    for x in (-3, 5, 13): box((2.2, 0.6, 0.45), (x, 6.8, 0.225), WHITE, bevel=0.06)

def walkers(lst):
    for x, y, r, dk in lst: person((x, y, 0), rot=r, mat=FIG_DK if dk else FIG)

def sun(strength=3.2, rot=(math.radians(48), 0, math.radians(-38))):
    ld = bpy.data.lights.new('sol', 'SUN'); ld.energy = strength; ld.angle = math.radians(2.5); ld.color = (1, 0.97, 0.92)
    o = bpy.data.objects.new('sol', ld); link(o); o.rotation_euler = rot

if VIEW == 'familia':
    sweep(wall_y=12, R=6, half=60, front=-90, top=40)
    cabina((-11.2, 0, 0), vending=False); cabina((-6.2, 0, 0)); kiosco((1.6, 0, 0), floors=1); kiosco((10.6, 0, 0), floors=2)
    set_world(0.25); sun(2.6, (math.radians(52), 0, math.radians(-30)))
    light('caja', (-6, -16, 14), (0, 0, 2), (14, 8), 9000)
    camera((1.2, -72, 8.0), (1.2, 0, 4.4), 80)
elif VIEW in ('out', 'in'):
    city()
    walkers([(6, -8, 2.4, 0), (6.6, -8.3, 2.4, 1), (-12, -7, 0.6, 1), (14, -1, -2.0, 0), (-4, -11, 3.0, 0), (2.5, 4.8, 1.4, 1), (-15, 2, -0.4, 0)])
    if VIEW == 'out':
        kiosco((0, 0, 0)); cabina((-9.2, -2.0, 0), rot=-0.28); cabina((10.4, -3.2, 0), rot=0.32)
    set_world(0.35); sun(3.0)
    camera((24, -31, 15.5), (0.5, 0, 2.4), 50)
elif VIEW == 'calle':
    city()
    cabina((0, 0, 0), rot=-0.12)
    walkers([(3.9, -1.8, -1.2, 1), (-3.6, -5.5, 2.0, 0), (-6.5, -2.5, 0.3, 0)])
    set_world(0.35); sun(3.0)
    camera((5.2, -10.5, 1.6), (0.2, 0, 1.5), 45)
elif VIEW == 'corte':
    kiosco((0, 0, 0)); shadow_catcher(60)
    set_world(0.3); sun(2.6, (math.radians(52), 0, math.radians(-30)))
    light('caja', (-8, -14, 14), (0, 0, 3), (10, 6), 7000)
    camera((15, -22, 9), (0.6, 0, 3.7), 50)

render(OUT, W, H, SPP, transparent=(VIEW == 'corte'), expo=-0.6)

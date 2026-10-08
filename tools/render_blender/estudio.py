"""Renders fotográficos de «Estudio portátil» con Blender (Cycles), como módulo de Python (pip install bpy).

  python3 tools/render_blender/estudio.py VISTA SALIDA.png [ANCHO ALTO MUESTRAS]
  VISTA: out | in | detalle | corte (objeto recortado con sombra, fondo transparente)

Lenguaje: tubo de acero lacado cobalto con radios amplios; tablero y altavoz de resina esmerilada
con un núcleo cobalto que se ve difuminado a través; estudio blanco infinito y luz suave.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

VIEW = sys.argv[1] if len(sys.argv) > 1 else 'out'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/estudio.png'
W, H, SPP = (int(a) for a in (sys.argv[3:6] if len(sys.argv) > 5 else (1600, 1000, 128)))


TOP = principled('resina_tablero', **{'Base Color': srgb('#eef1f8'), 'Roughness': 0.6, 'Transmission Weight': 1.0, 'IOR': 1.49})

RUBBER = principled('goma', **{'Base Color': srgb('#2a2b30'), 'Roughness': 0.7})
CONE = principled('cono', **{'Base Color': srgb('#0a1458'), 'Roughness': 0.9})          # papel tratado, cobalto profundo
DOME = principled('cupula', **{'Base Color': srgb('#1b1c21'), 'Roughness': 0.55})   # cúpula textil

def driver(g, r, z, y):
    """Altavoz real montado en el frontal: aro, suspensión de goma, cono y cubrepolvo."""
    rot = (math.pi / 2, 0, 0)
    bpy.ops.mesh.primitive_torus_add(major_radius=r * 0.95, minor_radius=r * 0.12, location=(0, y - 0.001, z), rotation=rot, major_segments=96, minor_segments=24)
    a = bpy.context.active_object; a.scale[2] = 0.35; a.data.materials.append(COBALT); a.parent = g; bpy.ops.object.shade_smooth()   # aro de montaje lacado
    bpy.ops.mesh.primitive_torus_add(major_radius=r * 0.82, minor_radius=r * 0.075, location=(0, y - 0.004, z), rotation=rot, major_segments=96, minor_segments=24)
    t = bpy.context.active_object; t.scale[2] = 0.7; t.data.materials.append(RUBBER); t.parent = g; bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cone_add(radius1=r * 0.76, radius2=r * 0.24, depth=r * 0.45, location=(0, y - 0.005 + r * 0.225, z), rotation=(-math.pi / 2, 0, 0), vertices=96, end_fill_type='NOTHING')
    c = bpy.context.active_object; c.data.materials.append(CONE); c.parent = g; bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r * 0.27, location=(0, y + r * 0.4, z), segments=48, ring_count=24)
    d = bpy.context.active_object; d.scale[1] = 0.55; d.data.materials.append(CONE); d.parent = g; bpy.ops.object.shade_smooth()

def speaker(loc, rot_z=0.0, parent=None):
    """Caja de resina esmerilada (se intuyen imán y cámara en cobalto) con el frontal lacado y los altavoces a la vista."""
    g = empty('altavoz', loc, parent); g.rotation_euler[2] = rot_z
    box((0.12, 0.13, 0.18), (0, 0, 0.09), FROST, bevel=0.024, seg=8, parent=g, name='caja')
    cyl(0.022, 0.03, (0, -0.035, 0.075), CORE, rot=(math.pi / 2, 0, 0), parent=g)        # imán, difuso a través de la resina
    cyl(0.03, 0.05, (0, 0.025, 0.075), CORE, rot=(math.pi / 2, 0, 0), parent=g)         # cámara
    driver(g, 0.042, 0.072, -0.066)                                                      # medio-graves 3,5"
    cyl(0.017, 0.004, (0, -0.067, 0.146), COBALT, rot=(math.pi / 2, 0, 0), parent=g)     # tweeter: aro
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.011, location=(0, -0.069, 0.146), segments=48, ring_count=24)
    d = bpy.context.active_object; d.scale[1] = 0.6; d.data.materials.append(DOME); d.parent = g; bpy.ops.object.shade_smooth()
    cyl(0.009, 0.004, (0, -0.066, 0.02), RUBBER, rot=(math.pi / 2, 0, 0), parent=g)      # puerto réflex
    return g

def laptop(loc, parent=None):
    g = empty('portatil', loc, parent)
    box((0.31, 0.21, 0.012), (0, 0, 0.006), ALU, bevel=0.004, parent=g)
    lid = empty('bisagra', (0, 0.105, 0.012), g); lid.rotation_euler[0] = -0.26
    box((0.31, 0.008, 0.21), (0, 0, 0.105), ALU, bevel=0.004, parent=lid)
    box((0.285, 0.002, 0.185), (0, -0.005, 0.108), SCREEN, parent=lid)
    return g

def desk(fold=0.0, parent=None):
    """Escritorio centrado en el origen. fold: 0 montado, 1 plegado (patas giradas bajo el tablero)."""
    g = empty('escritorio', (0, 0, 0), parent)
    th = fold * math.pi / 2 * 0.985
    for x0, w, sgn, dz in ((-0.52, 0.26, -1, 0.0), (0.52, 0.22, 1, -0.032 * fold)):
        piv = empty('pivote', (x0, 0, 0.705 + dz), g); piv.rotation_euler[1] = sgn * th
        tube([(0, -w, -0.69), (0, -w, 0), (0, w, 0), (0, w, -0.69)], 0.015, 0.09, closed=True, parent=piv, name='pata')
    box((1.2, 0.6, 0.045), (0, 0, 0.735), TOP, bevel=0.008, seg=4, parent=g, name='tablero')
    box((0.78, 0.3, 0.01), (0, 0.02, 0.735), CORE, bevel=0.005, seg=3, parent=g, name='nucleo')   # núcleo: se lee difuso a través de la resina
    tube([(-0.63, 0.32, 0.742), (0.63, 0.32, 0.742)], 0.02, 0.01, parent=g, name='rail')
    for x in (-0.4, 0.4): box((0.03, 0.03, 0.016), (x, 0.305, 0.742), COBALT, bevel=0.004, parent=g, name='pinza')
    return g

set_world(0.06)

# ------------------------------------------------------------------ vistas
if VIEW in ('out', 'corte'):
    desk(0)
    speaker((-0.38, 0.17, 0.75), 0.18); speaker((0.38, 0.17, 0.75), -0.18)
    laptop((0.02, -0.06, 0.75))
    camera((1.55, -2.85, 1.75), (0.0, 0.0, 0.5), 62)
elif VIEW == 'in':
    pk = empty('paquete', (0, 0.5, 0.0)); pk.rotation_euler[0] = math.radians(78)
    d = desk(1.0, pk); d.location = (0, 0.3, -0.704)       # canto delantero en el suelo, el raíl arriba como asa
    speaker((0.82, 0.25, 0), -0.45)
    camera((1.5, -2.7, 1.05), (0.25, 0.45, 0.36), 55)
elif VIEW == 'detalle':
    desk(0)
    speaker((-0.30, 0.17, 0.75), 0.0)
    camera((0.05, -0.75, 1.02), (-0.27, 0.15, 0.84), 85)

if VIEW == 'corte':
    shadow_catcher(12)
else:
    sweep(*((0.69, 0.18) if VIEW == 'in' else (2.6, 1.0)))

light('caja', (-1.9, -1.2, 2.7), (0, 0, 0.5), (1.8, 1.2), 700)
light('relleno', (2.6, -1.6, 1.2), (0, 0, 0.6), (2.0, 2.0), 70, (0.95, 0.97, 1.0))
light('contra', (0.4, 1.0, 2.8), (0, 0, 0.7), (1.5, 0.6), 220)

render(OUT, W, H, SPP, transparent=(VIEW == 'corte'))

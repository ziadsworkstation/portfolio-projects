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

def speaker(loc, rot_z=0.0, parent=None):
    g = empty('altavoz', loc, parent); g.rotation_euler[2] = rot_z
    box((0.12, 0.13, 0.18), (0, 0, 0.09), FROST, bevel=0.024, seg=8, parent=g, name='caja')
    cyl(0.040, 0.016, (0, -0.040, 0.075), CORE, rot=(math.pi / 2, 0, 0), parent=g)      # driver, dentro de la resina
    cyl(0.030, 0.070, (0, 0.005, 0.075), CORE, rot=(math.pi / 2, 0, 0), parent=g)       # cámara
    cyl(0.013, 0.012, (0, -0.040, 0.145), CORE, rot=(math.pi / 2, 0, 0), parent=g)      # tweeter
    tube([(-0.04, 0, 0.175), (-0.04, 0, 0.225), (0.04, 0, 0.225), (0.04, 0, 0.175)], 0.007, 0.026, parent=g, name='asa')
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

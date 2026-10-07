"""Bocetos de concepto de «Estudio portátil» (escritorio plegable + altavoz portátil).

  python3 tools/concept_estudio.py      -> fuentes/estudio-*.png

Dibujos de línea con la paleta de la web: conjunto en isométrica, secuencia de plegado
en alzado y sección del raíl de anclaje. Medidas en cm (conjunto, plegado) y mm (sección).
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'fuentes')
PAPER, INK, MUTE, RED = (242, 241, 238), (17, 17, 17), (138, 136, 132), (232, 37, 27)
WOOD, ALU = (232, 224, 208), (214, 216, 218)
SS = 2  # supersampling

def font(px, mono=False):
    for f in (('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',) if mono else
              ('/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')):
        if os.path.exists(f):
            return ImageFont.truetype(f, px * SS)
    return ImageFont.load_default()

def canvas(w, h):
    im = Image.new('RGB', (w * SS, h * SS), PAPER)
    return im, ImageDraw.Draw(im)

def save(im, name):
    w, h = im.size
    im.resize((w // SS, h // SS), Image.LANCZOS).save(os.path.join(OUT, name))
    print('ok', name)

def label(d, xy, text, to=None, color=INK, size=13, anchor='la'):
    x, y = xy
    if to:
        d.line([to, (x, y + 8 * SS)], fill=color, width=SS)
        d.ellipse([to[0] - 3 * SS, to[1] - 3 * SS, to[0] + 3 * SS, to[1] + 3 * SS], fill=color)
    d.text((x, y), text, font=font(size, mono=True), fill=color, anchor=anchor)

# ------------------------------------------------------------------ isométrica
def iso(o, k):
    c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
    return lambda x, y, z: (o[0] + (x - y) * c * k, o[1] + (x + y) * s * k - z * k)

def box(d, P, a, b, fill, w=2):
    (x0, y0, z0), (x1, y1, z1) = a, b
    faces = [  # caras visibles desde +x +y +z
        [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
        [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
        [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
    ]
    shade = [0.93, 0.86, 1.0]
    for f, t in zip(faces, shade):
        col = tuple(int(c * t) for c in fill)
        d.polygon([P(*p) for p in f], fill=col, outline=INK, width=w * SS)

def conjunto():
    im, d = canvas(1600, 1000)
    parts = []
    for x in (6, 111):                                       # patas: marco de aluminio
        parts += [((x, 8, 0), (x + 3, 12, 72), ALU), ((x, 8, 0), (x + 3, 60, 3), ALU),
                  ((x, 56, 0), (x + 3, 60, 72), ALU), ((x, 8, 69), (x + 3, 60, 72), ALU)]
    parts += [((0, 0, 70), (120, 4, 76), ALU),               # raíl trasero (anclaje + cables + asa)
              ((0, 4, 72), (120, 64, 73.8), WOOD),           # tablero 18 mm
              ((38, 30, 73.8), (70, 52, 75.2), (60, 60, 60)),  # portátil
              ((74, 44, 73.8), (114, 58, 77), (40, 40, 40))]   # controlador
    for x in (8, 100):                                       # altavoces anclados al raíl
        parts.append(((x, -3, 76), (x + 12, 9, 96), WOOD))
    # encaje: proyección unitaria y escala para ocupar la zona de dibujo
    P1 = iso((0, 0), 1)
    pts = [P1(x, y, z) for a, b, _ in parts for x in (a[0], b[0]) for y in (a[1], b[1]) for z in (a[2], b[2])]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    k = min(900 / (x1 - x0), 700 / (y1 - y0))
    P = iso(((90 - x0 * k) * SS, (220 - y0 * k) * SS), k * SS)
    for a, b, c in parts:
        box(d, P, a, b, c)
        if c is WOOD and a[2] == 76:
            cx, cy = P(a[0] + 6, b[1], 88); r = 2.6 * k * SS
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2 * SS)
    d.text((70 * SS, 60 * SS), 'estudio portátil', font=font(40), fill=INK)
    d.text((72 * SS, 115 * SS), 'escritorio plegable + altavoz portátil · un solo sistema', font=font(16, True), fill=MUTE)
    label(d, (1110 * SS, 200 * SS), 'altavoz anclado al raíl', to=P(112, 3, 96), color=RED)
    label(d, (1110 * SS, 222 * SS), 'carga por contacto', color=RED)
    label(d, (1110 * SS, 330 * SS), 'raíl de aluminio', to=P(120, 2, 76))
    label(d, (1110 * SS, 352 * SS), 'anclaje + cables + asa')
    label(d, (1110 * SS, 470 * SS), 'tablero de abedul 18 mm', to=P(120, 34, 73.8))
    label(d, (1110 * SS, 640 * SS), 'patas: marcos de', to=P(114, 58, 30))
    label(d, (1110 * SS, 662 * SS), 'aluminio plegado')
    label(d, (72 * SS, 930 * SS), '120 × 60 × 75 cm · plegado 8 cm · 40 kg', color=MUTE)
    save(im, 'estudio-conjunto.png')

# ------------------------------------------------------------------ plegado (alzado x-z)
def plegado():
    im, d = canvas(1600, 1000)
    k = 2.6 * SS
    def frame(ox, oy, ang, title):
        T = lambda x, z: (ox + x * k, oy - z * k)
        d.rectangle([T(0, 76), T(120, 70)], fill=ALU, outline=INK, width=2 * SS)        # raíl detrás
        d.rectangle([T(0, 73.8), T(120, 72)], fill=WOOD, outline=INK, width=2 * SS)     # tablero
        for hx, sgn, dash in ((8, 1, False), (112, -1, True)):
            a = math.radians(ang)
            L = 69 if not dash else 66
            ex, ez = hx + sgn * L * math.cos(a) * 0 + sgn * L * (1 - math.sin(a)) * 0, 0
            # pata = segmento desde la bisagra (hx, 72) girando de vertical (ang=90) a horizontal (0)
            px, pz = hx + sgn * L * math.cos(a), 72 - L * math.sin(a) - (0 if ang < 90 else 0)
            w = 3 * SS if not dash else 2 * SS
            if dash:
                n = 14
                for i in range(n):
                    if i % 2: continue
                    t0, t1 = i / n, (i + 1) / n
                    d.line([T(hx + (px - hx) * t0, 72 + (pz - 72) * t0), T(hx + (px - hx) * t1, 72 + (pz - 72) * t1)], fill=INK, width=w)
            else:
                d.line([T(hx, 72), T(px, pz)], fill=INK, width=w)
            d.ellipse([*[v - 5 * SS for v in T(hx, 72)], *[v + 5 * SS for v in T(hx, 72)]], fill=RED)
        d.text((ox, oy + 18 * SS), title, font=font(14, True), fill=INK)
    d.text((70 * SS, 60 * SS), 'plegado', font=font(40), fill=INK)
    d.text((72 * SS, 115 * SS), 'dos marcos que se anidan bajo el tablero · sin herramientas · < 1 min', font=font(16, True), fill=MUTE)
    frame(80 * SS, 470 * SS, 90, '1  abierto · 75 cm')
    frame(560 * SS, 470 * SS, 40, '2  las patas giran hacia dentro')
    frame(1040 * SS, 470 * SS, 0, '3  plano · los marcos se anidan')
    # 4: paquete plegado (alzado a escala mayor): tablero + marcos anidados + raíl
    d.text((80 * SS, 640 * SS), '4  plegado y a cuestas: el raíl es el asa', font=font(14, True), fill=INK)
    k2 = 6 * SS; X = lambda x: 120 * SS + x * k2; Z = lambda z: 820 * SS - z * k2
    d.rectangle([X(0), Z(8), X(120), Z(4.3)], fill=ALU, outline=INK, width=2 * SS)    # raíl
    d.rectangle([X(0), Z(4.3), X(120), Z(2.5)], fill=WOOD, outline=INK, width=2 * SS) # tablero
    d.rectangle([X(8), Z(2.5), X(112), Z(0)], fill=ALU, outline=INK, width=2 * SS)    # marcos anidados
    d.line([X(124), Z(8), X(124), Z(0)], fill=RED, width=2 * SS)
    d.text((X(127), Z(5.5)), '8 cm', font=font(14, True), fill=RED)
    d.text((X(0), Z(-5)), 'cabe detrás de una puerta o bajo la cama', font=font(14, True), fill=MUTE)
    d.ellipse([1200 * SS, 645 * SS, 1210 * SS, 655 * SS], fill=RED)
    d.text((1220 * SS, 641 * SS), 'bisagra con pestillo', font=font(14, True), fill=INK)
    d.line([1200 * SS, 680 * SS, 1240 * SS, 680 * SS], fill=INK, width=3 * SS)
    d.text((1250 * SS, 672 * SS), 'marco ancho', font=font(14, True), fill=INK)
    for i in range(0, 40, 12): d.line([(1200 + i) * SS, 705 * SS, (1206 + i) * SS, 705 * SS], fill=INK, width=2 * SS)
    d.text((1250 * SS, 697 * SS), 'marco estrecho (anida)', font=font(14, True), fill=INK)
    save(im, 'estudio-plegado.png')

# ------------------------------------------------------------------ sección del anclaje (mm)
def anclaje():
    im, d = canvas(1600, 1000)
    k = 7 * SS
    O = (560 * SS, 760 * SS)
    T = lambda y, z: (O[0] + y * k, O[1] - z * k)
    poly = lambda pts, **kw: d.polygon([T(*p) for p in pts], **kw)
    # raíl extruido 40 × 60: canal de cables abajo, ranura en T arriba, ala atornillada al canto del tablero
    poly([(0, 0), (40, 0), (40, 60), (24, 60), (24, 56), (32, 56), (32, 48), (8, 48), (8, 56), (16, 56), (16, 60), (0, 60)], fill=ALU, outline=INK, width=2 * SS)
    d.rectangle([T(5, 40), T(35, 6)], fill=PAPER, outline=INK, width=2 * SS)          # canal de cables
    for cy in (14, 24):
        d.ellipse([*[v - 2.6 * k for v in T(12 + (cy - 14), 14)], *[v + 2.6 * k for v in T(12 + (cy - 14), 14)]], outline=MUTE, width=2 * SS)
    d.rectangle([T(40, 46), T(80, 28)], fill=WOOD, outline=INK, width=2 * SS)         # tablero 18 mm
    d.rectangle([T(10, 49.5), T(30, 48)], fill=RED)                                    # pista de contactos
    # pie del altavoz: lengüeta en T + imán + pogo pins
    poly([(17, 60), (17, 54), (9.5, 54), (9.5, 50), (30.5, 50), (30.5, 54), (23, 54), (23, 60)], fill=WOOD, outline=INK, width=2 * SS)
    d.rectangle([T(-14, 80), T(54, 60)], fill=WOOD, outline=INK, width=2 * SS)        # base del altavoz
    d.rectangle([T(15, 66), T(25, 61)], fill=(70, 70, 70))                             # imán
    for py in (13, 20, 27):
        d.line([T(py, 50), T(py, 48.5)], fill=INK, width=3 * SS)
    d.text((70 * SS, 60 * SS), 'anclaje', font=font(40), fill=INK)
    d.text((72 * SS, 115 * SS), 'sección del raíl · escala 7:1 · mm', font=font(16, True), fill=MUTE)
    label(d, (1180 * SS, 180 * SS), 'base del altavoz (contrachapado)', to=T(54, 72))
    label(d, (1180 * SS, 260 * SS), 'imán de neodimio: fija sin apretar', to=T(25, 63))
    label(d, (1180 * SS, 340 * SS), 'lengüeta en T: desliza a lo largo del raíl', to=T(23, 57))
    label(d, (1180 * SS, 420 * SS), 'pogo pins: el altavoz se carga anclado', to=T(27, 49.5), color=RED)
    label(d, (1180 * SS, 500 * SS), 'tablero 18 mm', to=T(80, 37))
    label(d, (1180 * SS, 650 * SS), 'canal de cables (30 × 34)', to=T(35, 30))
    label(d, (1180 * SS, 800 * SS), 'perfil de aluminio extruido 40 × 60', to=T(40, 3))
    save(im, 'estudio-anclaje.png')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    conjunto(); plegado(); anclaje()

"""Bocetos de concepto de «Estudio portátil» (escritorio plegable + altavoz portátil).

  python3 tools/concept_estudio.py      -> fuentes/estudio-*.png

Lenguaje: objetos monocromos en azul cobalto lacado (tubo de radio generoso, como un
grifo Vola), sobre el canto crudo del contrachapado. Conjunto en isométrica, secuencia de
plegado en alzado y sección del anclaje. Medidas en cm (conjunto, plegado) y mm (sección).
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'fuentes')
PAPER, INK, MUTE = (238, 237, 233), (17, 17, 17), (138, 136, 132)
BLUE = (31, 63, 209)          # cobalto, el mismo acento que la web
WOOD = (226, 211, 182)        # canto de abedul
SS = 2                        # supersampling

def font(px, mono=False):
    f = '/usr/share/fonts/truetype/dejavu/' + ('DejaVuSansMono.ttf' if mono else 'DejaVuSans.ttf')
    return ImageFont.truetype(f, px * SS) if os.path.exists(f) else ImageFont.load_default()

def canvas(w, h):
    im = Image.new('RGB', (w * SS, h * SS), PAPER)
    return im, ImageDraw.Draw(im)

def save(im, name):
    w, h = im.size
    im.resize((w // SS, h // SS), Image.LANCZOS).save(os.path.join(OUT, name))
    print('ok', name)

def title(d, t, sub):
    d.text((70 * SS, 60 * SS), t, font=font(38), fill=INK)
    d.text((72 * SS, 114 * SS), sub, font=font(15, True), fill=MUTE)

def label(d, xy, lines, to=None, color=INK):
    x, y = xy
    if to:
        d.line([to, (x - 8 * SS, y + 8 * SS)], fill=color, width=SS)
        d.ellipse([to[0] - 3 * SS, to[1] - 3 * SS, to[0] + 3 * SS, to[1] + 3 * SS], fill=color)
    for i, l in enumerate(lines if isinstance(lines, (list, tuple)) else [lines]):
        d.text((x, y + i * 21 * SS), l, font=font(13, True), fill=color)

def shade(c, t):
    return tuple(max(0, min(255, int(v * t))) for v in c)

# ------------------------------------------------------------------ geometría 3D
def iso(o, k):
    c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
    return lambda x, y, z: (o[0] + (x - y) * c * k, o[1] + (x + y) * s * k - z * k)

def box(d, P, a, b, top, side=None, w=2):
    (x0, y0, z0), (x1, y1, z1) = a, b
    side = side or top
    for f, col in (([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], shade(side, .86)),
                   ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], shade(side, .74)),
                   ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], top)):
        d.polygon([P(*p) for p in f], fill=col, outline=INK, width=w * SS)

def fillet(pts, r, n=10):
    """Polilínea 3D con las esquinas redondeadas (radio r), como un tubo curvado."""
    out = [pts[0]]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        u = [b[i] - a[i] for i in range(3)]; v = [c[i] - b[i] for i in range(3)]
        lu = math.sqrt(sum(x * x for x in u)); lv = math.sqrt(sum(x * x for x in v))
        u = [x / lu for x in u]; v = [x / lv for x in v]
        rr = min(r, lu / 2, lv / 2)
        p0 = [b[i] - u[i] * rr for i in range(3)]; p2 = [b[i] + v[i] * rr for i in range(3)]
        for t in [j / n for j in range(n + 1)]:      # Bézier cuadrática ≈ arco
            out.append(tuple((1 - t) ** 2 * p0[i] + 2 * (1 - t) * t * b[i] + t * t * p2[i] for i in range(3)))
    out.append(pts[-1])
    return out

def tube(d, P, pts, dia, k, col=BLUE, r=8):
    path = [P(*p) for p in fillet(pts, r)]
    w = max(2, int(dia * k))
    d.line(path, fill=INK, width=w + 4 * SS, joint='curve')
    for q in (path[0], path[-1]):
        d.ellipse([q[0] - (w + 4 * SS) / 2, q[1] - (w + 4 * SS) / 2, q[0] + (w + 4 * SS) / 2, q[1] + (w + 4 * SS) / 2], fill=INK)
    d.line(path, fill=col, width=w, joint='curve')
    for q in (path[0], path[-1]):
        d.ellipse([q[0] - w / 2, q[1] - w / 2, q[0] + w / 2, q[1] + w / 2], fill=col)
    hl = [(x - w * .18, y - w * .18) for x, y in path]            # brillo del lacado
    d.line(hl, fill=shade(col, 1.55), width=max(1, w // 6), joint='curve')

# ------------------------------------------------------------------ conjunto
def conjunto():
    im, d = canvas(1600, 1000)
    P1 = iso((0, 0), 1)
    pts = [P1(x, y, z) for x in (-2, 122) for y in (-6, 66) for z in (0, 100)]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    k = min(880 / (x1 - x0), 720 / (y1 - y0))
    P = iso(((100 - x0 * k) * SS, (200 - y0 * k) * SS), k * SS)
    # patas: un tubo continuo por lado, en U invertida con pie, radio generoso
    for x in (8, 112):
        tube(d, P, [(x, 6, 0), (x, 6, 71), (x, 58, 71), (x, 58, 0)], 3, k * SS, r=10)
        tube(d, P, [(x, 0, 0), (x, 64, 0)], 3, k * SS, r=1)
    # raíl trasero: tubo Ø4 cm que sobresale y hace de asa
    tube(d, P, [(-2, 2, 73), (122, 2, 73)], 4, k * SS, r=1)
    # tablero: lacado azul arriba, canto de abedul crudo a la vista
    box(d, P, (0, 4, 72), (120, 64, 73.8), top=BLUE, side=WOOD)
    box(d, P, (38, 30, 73.8), (70, 52, 75.2), top=(70, 70, 70))       # portátil
    box(d, P, (74, 44, 73.8), (112, 58, 77), top=(52, 52, 52))        # controlador
    # altavoces: cuerpo monocromo con asa de tubo arriba
    for x in (10, 98):
        box(d, P, (x, -4, 76), (x + 12, 10, 94), top=BLUE)
        cx, cy = P(x + 6, 10, 86); r = 3.4 * k * SS
        d.ellipse([cx - r, cy - r * .9, cx + r, cy + r * .9], fill=shade(BLUE, .55), outline=INK, width=2 * SS)
        tube(d, P, [(x + 2, 3, 94), (x + 2, 3, 99), (x + 10, 3, 99), (x + 10, 3, 94)], 1.4, k * SS, r=3)
    title(d, 'estudio portátil', 'escritorio plegable + altavoz portátil · un solo sistema')
    label(d, (1130 * SS, 190 * SS), ['altavoz: cuerpo lacado', 'asa de tubo · se ancla y', 'se carga en el raíl'], to=P(110, 3, 99), color=BLUE)
    label(d, (1130 * SS, 330 * SS), ['raíl: tubo Ø 40', 'anclaje + cables + asa'], to=P(122, 2, 73))
    label(d, (1130 * SS, 450 * SS), ['tablero lacado', 'canto de abedul a la vista'], to=P(120, 40, 72.9))
    label(d, (1130 * SS, 610 * SS), ['patas: un solo tubo', 'curvado por lado'], to=P(112, 58, 30))
    d.text((72 * SS, 930 * SS), '120 × 60 × 75 cm · plegado 8 cm · 40 kg · todo en azul cobalto', font=font(13, True), fill=MUTE)
    save(im, 'estudio-conjunto.png')

# ------------------------------------------------------------------ plegado (alzado x-z)
def plegado():
    im, d = canvas(1600, 1000)
    k = 2.6 * SS
    def leg(T, hx, sgn, ang, L, col):
        a = math.radians(ang)
        px, pz = hx + sgn * L * math.cos(a), 72 - L * math.sin(a)
        w = int(3 * k)
        d.line([T(hx, 72), T(px, pz)], fill=INK, width=w + 4 * SS)
        d.line([T(hx, 72), T(px, pz)], fill=col, width=w)
    def frame(ox, oy, ang, t):
        T = lambda x, z: (ox + x * k, oy - z * k)
        leg(T, 112, -1, ang, 66, shade(BLUE, 1.35))                      # marco estrecho (detrás)
        leg(T, 8, 1, ang, 69, BLUE)                                      # marco ancho
        d.rounded_rectangle([T(-2, 75), T(122, 71)], radius=2 * k, fill=BLUE, outline=INK, width=2 * SS)  # raíl
        d.rectangle([T(0, 73.8), T(120, 72)], fill=WOOD, outline=INK, width=2 * SS)                    # canto
        for hx in (8, 112):
            d.ellipse([*[v - 5 * SS for v in T(hx, 72)], *[v + 5 * SS for v in T(hx, 72)]], fill=PAPER, outline=INK, width=2 * SS)
        d.text((ox, oy + 18 * SS), t, font=font(13, True), fill=INK)
    title(d, 'plegado', 'dos tubos que se anidan bajo el tablero · sin herramientas · < 1 min')
    frame(80 * SS, 470 * SS, 90, '1  abierto · 75 cm')
    frame(560 * SS, 470 * SS, 40, '2  las patas giran hacia dentro')
    frame(1040 * SS, 470 * SS, 0, '3  plano · un tubo dentro del otro')
    d.text((80 * SS, 640 * SS), '4  plegado y a cuestas: el raíl es el asa', font=font(13, True), fill=INK)
    k2 = 6 * SS; X = lambda x: 120 * SS + x * k2; Z = lambda z: 820 * SS - z * k2
    d.rounded_rectangle([X(-2), Z(8), X(122), Z(4)], radius=2 * k2, fill=BLUE, outline=INK, width=2 * SS)
    d.rectangle([X(0), Z(4.3), X(120), Z(2.5)], fill=WOOD, outline=INK, width=2 * SS)
    d.rounded_rectangle([X(8), Z(2.5), X(112), Z(0)], radius=1.2 * k2, fill=BLUE, outline=INK, width=2 * SS)
    d.line([X(126), Z(8), X(126), Z(0)], fill=BLUE, width=2 * SS)
    d.text((X(129), Z(5.6)), '8 cm', font=font(13, True), fill=BLUE)
    d.text((X(0), Z(-5)), 'cabe detrás de una puerta o bajo la cama', font=font(13, True), fill=MUTE)
    d.ellipse([1200 * SS, 645 * SS, 1210 * SS, 655 * SS], fill=PAPER, outline=INK, width=2 * SS)
    d.text((1222 * SS, 641 * SS), 'bisagra con pestillo', font=font(13, True), fill=INK)
    d.line([1196 * SS, 677 * SS, 1214 * SS, 677 * SS], fill=BLUE, width=6 * SS)
    d.text((1222 * SS, 669 * SS), 'tubo ancho', font=font(13, True), fill=INK)
    d.line([1196 * SS, 703 * SS, 1214 * SS, 703 * SS], fill=shade(BLUE, 1.35), width=6 * SS)
    d.text((1222 * SS, 695 * SS), 'tubo estrecho (anida)', font=font(13, True), fill=INK)
    save(im, 'estudio-plegado.png')

# ------------------------------------------------------------------ anclaje (sección, mm)
def anclaje():
    im, d = canvas(1600, 1000)
    k = 7 * SS
    O = (520 * SS, 700 * SS)
    T = lambda y, z: (O[0] + y * k, O[1] - z * k)
    R = 20                                                   # tubo Ø 40 × 2
    c = T(0, 0)
    d.ellipse([c[0] - R * k, c[1] - R * k, c[0] + R * k, c[1] + R * k], fill=BLUE, outline=INK, width=2 * SS)
    d.ellipse([c[0] - (R - 2) * k, c[1] - (R - 2) * k, c[0] + (R - 2) * k, c[1] + (R - 2) * k], fill=PAPER, outline=INK, width=2 * SS)
    for cy in (-8, 2):                                        # cables por dentro del tubo
        q = T(cy, -8); d.ellipse([q[0] - 3 * k, q[1] - 3 * k, q[0] + 3 * k, q[1] + 3 * k], outline=MUTE, width=2 * SS)
    d.rectangle([T(-8, 20.4), T(8, 18.6)], fill=INK)                        # pista de contactos (plano superior)
    # pinza del altavoz: abraza medio tubo, imán y pogo pins
    d.chord([c[0] - (R + 4) * k, c[1] - (R + 4) * k, c[0] + (R + 4) * k, c[1] + (R + 4) * k], 180, 360, fill=BLUE, outline=INK, width=2 * SS)
    d.chord([c[0] - R * k, c[1] - R * k, c[0] + R * k, c[1] + R * k], 180, 360, fill=PAPER)
    d.ellipse([c[0] - R * k, c[1] - R * k, c[0] + R * k, c[1] + R * k], fill=BLUE, outline=INK, width=2 * SS)
    d.ellipse([c[0] - (R - 2) * k, c[1] - (R - 2) * k, c[0] + (R - 2) * k, c[1] + (R - 2) * k], fill=PAPER, outline=INK, width=2 * SS)
    for cy in (-8, 2):
        q = T(cy, -8); d.ellipse([q[0] - 3 * k, q[1] - 3 * k, q[0] + 3 * k, q[1] + 3 * k], outline=MUTE, width=2 * SS)
    d.rectangle([T(-8, 20.4), T(8, 19)], fill=INK)
    d.rounded_rectangle([T(-36, 52), T(36, 24)], radius=4 * k, fill=BLUE, outline=INK, width=2 * SS)     # base del altavoz
    d.rectangle([T(-6, 30), T(6, 25.5)], fill=(40, 40, 40))                                             # imán
    for py in (-5, 0, 5):
        d.line([T(py, 24), T(py, 20.6)], fill=INK, width=3 * SS)
    d.rectangle([T(25, 9), T(76, -9)], fill=WOOD, outline=INK, width=2 * SS)                       # tablero 18 mm
    title(d, 'anclaje', 'sección del raíl · escala 7:1 · mm')
    label(d, (1130 * SS, 220 * SS), ['base del altavoz, lacada'], to=T(36, 44), color=BLUE)
    label(d, (1130 * SS, 300 * SS), ['imán de neodimio:', 'fija sin apretar'], to=T(6, 28))
    label(d, (1130 * SS, 400 * SS), ['pinza: abraza medio tubo', 'y desliza a lo largo'], to=T(-23, 4))
    label(d, (1130 * SS, 500 * SS), ['pogo pins sobre la pista:', 'se carga anclado'], to=T(5, 21), color=BLUE)
    label(d, (1130 * SS, 610 * SS), ['tubo Ø 40 × 2: los cables', 'van por dentro'], to=T(-2, -8))
    label(d, (1130 * SS, 720 * SS), ['tablero 18 mm'], to=T(76, 0))
    save(im, 'estudio-anclaje.png')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    conjunto(); plegado(); anclaje()

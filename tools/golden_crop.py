"""Recorta imágenes para que la construcción áurea de la web caiga sobre el objeto.

Cada imagen se coloca en el rectángulo áureo R = [0,φ]×[0,1] fijando:
  E  -> píxel de la imagen que cae en el ojo de la espiral O (o 'tl': esquina sup. izq.)
  s  -> píxeles por unidad (lado del cuadrado mayor)
Orientación 'L' (escritorio, φ:1) o 'P' (móvil, 1:φ, R girado −90° como en la web).
Si el recorte sale de la imagen se extiende con 'reflect' (texturas) o 'edge' (fondos lisos).

  python3 golden_crop.py SRC_DIR OUT_DIR [--preview DIR]
"""
import json, math, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PHI = (1 + 5 ** .5) / 2
DEN = 1 + 1 / PHI ** 2
O = (PHI / DEN, 1 / DEN)                     # ojo de la espiral en coordenadas de R

def frame(orient, E, s):
    """Devuelve (x0, y0, W, H) del recorte y una función local(u,v)->pixel."""
    if orient == 'L':
        x0, y0 = E[0] - O[0] * s, E[1] - O[1] * s
        return (x0, y0, PHI * s, s), (lambda u, v: (x0 + u * s, y0 + v * s))
    # vertical: (dx,dy) -> (dy,-dx) alrededor del centro de R
    dx, dy = O[0] - PHI / 2, O[1] - .5
    cx, cy = E[0] - s * dy, E[1] + s * dx
    f = lambda u, v: (cx + s * (v - .5), cy - s * (u - PHI / 2))
    return (cx - s / 2, cy - PHI * s / 2, s, PHI * s), f

def anchor(orient, c):
    """E directo, o 'tl' = esquina superior izquierda del recorte."""
    if 'E' in c: return c['E']
    (bx, by, _, _), _ = frame(orient, (0, 0), c['s'])
    return (c['tl'][0] - bx, c['tl'][1] - by)

def padded_crop(im, box, mode, out_w):
    a = np.asarray(im.convert('RGB'))
    H, W = a.shape[:2]
    x0, y0, w, h = box
    x0i, y0i, x1i, y1i = math.floor(x0), math.floor(y0), math.ceil(x0 + w), math.ceil(y0 + h)
    pl, pt, pr, pb = max(0, -x0i), max(0, -y0i), max(0, x1i - W), max(0, y1i - H)
    if any((pl, pt, pr, pb)):
        p = np.pad(a, ((pt, pb), (pl, pr), (0, 0)), mode='edge' if mode == 'edge' else 'symmetric')
        if mode == 'edge':                            # suaviza solo la zona extendida
            pim = Image.fromarray(p); bl = pim.filter(ImageFilter.GaussianBlur(18))
            m = np.ones(p.shape[:2], np.uint8) * 255
            m[pt:pt + H, pl:pl + W] = 0
            mask = Image.fromarray(m).filter(ImageFilter.GaussianBlur(10))
            p = np.asarray(Image.composite(bl, pim, mask))
        a = p
        x0, y0 = x0 + pl, y0 + pt
    img = Image.fromarray(a).crop((round(x0), round(y0), round(x0 + w), round(y0 + h)))
    out_h = round(out_w * h / w)
    return img.resize((out_w, out_h), Image.LANCZOS), (pl, pt, pr, pb)

def overlay(img, orient):
    """Dibuja cuadrados, espiral y ojo sobre el recorte (solo para revisar)."""
    im = img.copy(); d = ImageDraw.Draw(im)
    W, H = im.size
    s = H if orient == 'L' else W
    (bx, by, _, _), f0 = frame(orient, (0, 0), s)
    f = lambda u, v: (f0(u, v)[0] - bx, f0(u, v)[1] - by)
    a = complex(0, 1) / PHI
    for n in range(12):
        an = a ** n; bn = PHI * (1 - an) / (1 - a)
        g = lambda z: an * z + bn
        sq = [g(complex(*c)) for c in ((0, 0), (1, 0), (1, 1), (0, 1), (0, 0))]
        d.line([f(p.real, p.imag) for p in sq], fill=(255, 40, 30), width=2)
        arc = [g(complex(1 + math.cos(t), 1 + math.sin(t))) for t in np.linspace(math.pi, 1.5 * math.pi, 30)]
        d.line([f(p.real, p.imag) for p in arc], fill=(255, 220, 0), width=2)
    ex, ey = f(*O); d.ellipse((ex - 7, ey - 7, ex + 7, ey + 7), outline=(0, 255, 255), width=3)
    return im

if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    cfg = json.load(open(os.path.join(os.path.dirname(__file__), 'golden_crops.json')))
    os.makedirs(out, exist_ok=True)
    for name, c in cfg.items():
        im = Image.open(os.path.join(src, c['src']))
        for o in ('L', 'P'):
            box, _ = frame(o, anchor(o, c[o]), c[o]['s'])
            img, pad = padded_crop(im, box, c.get('mode', 'reflect'), 1400 if o == 'L' else 865)
            img.save(os.path.join(out, f'{name}-{o.lower()}.webp'), 'WEBP', quality=80, method=6)
            print(name, o, 'pad', pad)
            if prev:
                overlay(img, o).save(os.path.join(prev, f'{name}-{o}.png'))

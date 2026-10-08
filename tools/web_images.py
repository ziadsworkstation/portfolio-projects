"""Genera img/<nombre>.webp desde fuentes/: misma proporción que el original, 1600 px de ancho como máximo.

  python3 tools/web_images.py
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = {   # nombre en la web -> original en fuentes/
    'rampassist-in': 'rampassist-in.jpg', 'rampassist-proceso': 'rampassist-proceso.jpg',
    'rampassist-iteracion': 'rampassist-iteracion.jpg', 'rampassist-out': 'rampassist-out.jpg',
    'estudio-in': 'estudio-in.jpg', 'estudio-proceso': 'estudio-plegado.png',
    'estudio-iteracion': 'estudio-anclaje.png', 'estudio-out': 'estudio-out.jpg',
    'plaza-in': 'plaza-plaza.jpg', 'plaza-proceso': 'plaza-familia.jpg',
    'plaza-iteracion': 'plaza-calle.jpg', 'plaza-out': 'plaza-out.jpg',
}
out = os.path.join(ROOT, 'img'); os.makedirs(out, exist_ok=True)
for name, src in IMAGES.items():
    im = Image.open(os.path.join(ROOT, 'fuentes', src)).convert('RGB')
    if im.width > 1600: im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    im.save(os.path.join(out, name + '.webp'), 'WEBP', quality=80, method=6)
    print(name, im.size)

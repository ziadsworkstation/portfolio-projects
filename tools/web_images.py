"""Genera img/<nombre>.webp desde fuentes/: un recorte vertical 3:4 por proyecto para el índice.

  python3 tools/web_images.py
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTRAITS = {   # nombre en la web -> (original en fuentes/, centro horizontal del recorte 0..1)
    'retrato': ('retrato.jpg', 0.50),
    'rampassist': ('rampassist-in.jpg', 0.70),
    'estudio': ('estudio-detalle.jpg', 0.44),
    'plaza': ('plaza-calle.jpg', 0.49),
}
out = os.path.join(ROOT, 'img'); os.makedirs(out, exist_ok=True)
for f in os.listdir(out):
    if f.endswith('.webp'): os.remove(os.path.join(out, f))
for name, (src, cx) in PORTRAITS.items():
    im = Image.open(os.path.join(ROOT, 'fuentes', src)).convert('RGB')
    w = round(im.height * 3 / 4); x = min(max(round(im.width * cx - w / 2), 0), im.width - w)
    im = im.crop((x, 0, x + w, im.height)).resize((900, 1200), Image.LANCZOS)
    im.save(os.path.join(out, name + '.webp'), 'WEBP', quality=82, method=6)
    print(name, im.size)

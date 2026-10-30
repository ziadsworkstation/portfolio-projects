"""Genera img/<nombre>.webp desde fuentes/: el retrato en vertical 4:5.

  python3 tools/web_images.py
"""
import os
from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTRAITS = {   # nombre en la web -> (original en fuentes/, centro horizontal del recorte 0..1)
    'retrato': ('retrato.jpg', 0.50),
}
out = os.path.join(ROOT, 'img'); os.makedirs(out, exist_ok=True)
for f in os.listdir(out):
    if f.endswith('.webp'): os.remove(os.path.join(out, f))
for name, (src, cx) in PORTRAITS.items():
    im = Image.open(os.path.join(ROOT, 'fuentes', src)).convert('RGB')
    w = round(im.height * 4 / 5); x = min(max(round(im.width * cx - w / 2), 0), im.width - w)
    im = im.crop((x, 0, x + w, im.height)).resize((960, 1200), Image.LANCZOS)
    if name == 'retrato': im = ImageEnhance.Color(im).enhance(0.8)   # saturación algo más baja (Ziad, 2026-10-30)
    im.save(os.path.join(out, name + '.webp'), 'WEBP', quality=82, method=6)
    print(name, im.size)

# Fotos de producto (generadas por Ziad): se ven al pulsar «Diseño de producto»
for name in ('altavoz-familia', 'altavoz-peana', 'altavoz-detalle', 'altavoz-contexto'):
    im = Image.open(os.path.join(ROOT, 'fuentes', name + '.jpg')).convert('RGB')
    im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS).save(os.path.join(out, name + '.webp'), 'WEBP', quality=80, method=6)
    print(name)

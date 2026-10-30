"""Genera dist/<nombre>.html: la web en un solo archivo, con las imágenes incrustadas.

  python3 tools/build_single.py . ziadaddami -> dist/ziadaddami.html
"""
import base64, os, re, sys
root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name = sys.argv[2] if len(sys.argv) > 2 else 'ziadaddami'
html = open(os.path.join(root, 'index.html'), encoding='utf-8').read()
imgs = {}
for f in sorted(os.listdir(os.path.join(root, 'img'))):
    if f.endswith('.webp'):
        b = base64.b64encode(open(os.path.join(root, 'img', f), 'rb').read()).decode()
        imgs[f] = 'data:image/webp;base64,' + b
src = 'const IMG = ' + '{' + ','.join(f'"{k}":"{v}"' for k, v in imgs.items()) + '};\n'
html = html.replace("const srcOf = f => `img/${f}.webp`;", src + "const srcOf = f => IMG[`${f}.webp`];", 1)
assert 'IMG[`${f}' in html
assert 'IMG[' in html and 'const IMG' in html
os.makedirs(os.path.join(root, 'dist'), exist_ok=True)
out = os.path.join(root, 'dist', name + '.html')
open(out, 'w', encoding='utf-8').write(html)
print(out, round(os.path.getsize(out) / 1024), 'KB')

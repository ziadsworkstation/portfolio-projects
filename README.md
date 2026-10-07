# ziadaddami.es — portfolio

Basado en la estructura de la web de R11 (`ziadsworkstation/EXARL1`, rama `claude/quirky-noether-vc8aw3`, carpeta `web/`):
un zoom infinito por la subdivisión del rectángulo áureo. Cada paso del scroll entra en el siguiente cuadrado
(escala ×φ, giro 90°), con una imagen a pantalla completa por paso y la construcción (cuadrados, espiral, ojo φ)
justificando el encuadre.

Sin dependencias ni build: abrir `index.html` en el navegador o servir la carpeta tal cual.

| Paso | Contenido |
|---|---|
| 0 | ziad addami |
| 1–4 | Rampassist en in-out: in · proceso · maqueta 1:2 · out (borrador) |
| 5 | Sobre mí |
| 6 | Contacto |
| 7 | Entidades: R11 · CloutNative · Blashgol |

- Contenido: array `ITEMS` en `index.html` (y su copia accesible en `<main class="sr">`).
- Imágenes: `img/<nombre>-l.webp` (escritorio, φ:1) y `img/<nombre>-p.webp` (móvil, 1:φ), recortadas con
  `tools/golden_crop.py` (uso en su cabecera).
- Archivo único: `python3 tools/build_single.py . ziadaddami` → `dist/ziadaddami.html`.
- `fuentes/`: originales que recorta `tools/golden_crop.py` según `tools/golden_crops.json`. Las de Rampassist son provisionales y salen de la presentación y del informe de la maqueta de TAD3.
- Por confirmar: lista de proyectos y texto de «Sobre mí».

## Publicación (GitHub Pages)

`CNAME` fija el dominio `ziadaddami.es`; `.nojekyll` sirve los archivos tal cual. En GitHub: Settings → Pages → Deploy from a branch → `main` / root.
En el proveedor del dominio: cuatro registros `A` para `@` (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153) y un `CNAME` para `www` → `ziadsworkstation.github.io`.

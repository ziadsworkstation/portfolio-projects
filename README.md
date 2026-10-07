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
- Pendiente: más proyectos e imágenes finales de Rampassist.

## Publicación (Vercel)

Sitio estático sin build: en Vercel, Add New → Project → importar `ziadsworkstation/portfolio-projects`, Framework Preset «Other», sin comando de build y con la raíz del repo como directorio de salida. El dominio `ziadaddami.es` se añade en Settings → Domains y Vercel indica los registros DNS. `.vercelignore` deja fuera `tools/` y `fuentes/`.

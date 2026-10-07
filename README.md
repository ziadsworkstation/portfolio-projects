# ziadaddami.es — portfolio

Basado en la estructura de la web de R11 (`ziadsworkstation/EXARL1`, rama `claude/quirky-noether-vc8aw3`, carpeta `web/`):
un zoom infinito por la subdivisión del rectángulo áureo. Cada paso del scroll entra en el siguiente cuadrado
(escala ×φ, giro 90°), con una imagen a pantalla completa por paso y la construcción (cuadrados, espiral, ojo φ)
justificando el encuadre.

Sin dependencias ni build: abrir `index.html` en el navegador o servir la carpeta tal cual.

| Paso | Contenido |
|---|---|
| 0 | ziad addami |
| … | proyectos (por definir) |
| n | R11 |
| n+1 | Sobre mí |
| n+2 | Contacto |

- Contenido: array `ITEMS` en `index.html` (y su copia accesible en `<main class="sr">`).
- Imágenes: `img/<nombre>-l.webp` (escritorio, φ:1) y `img/<nombre>-p.webp` (móvil, 1:φ), recortadas con
  `tools/golden_crop.py` (uso en su cabecera).
- Archivo único: `python3 tools/build_single.py . ziadaddami` → `dist/ziadaddami.html`.
- Por confirmar: lista de proyectos, correo `hola@ziadaddami.es` y texto de «Sobre mí».

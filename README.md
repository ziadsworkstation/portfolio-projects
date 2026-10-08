# ziadaddami.es — portfolio

Una portada tipo sumario (bio, índice numerado y una fila por proyecto) y una página por proyecto,
leída con el método in-out: 01 In · 02 Proceso · 03 Iteración · 04 Out. Las páginas se abren con `#rampassist`,
`#estudio` y `#plaza`.

Sin dependencias ni build: abrir `index.html` en el navegador o servir la carpeta tal cual.

- Contenido: todo en `index.html` (portada en `#home`, proyectos en `<article class="pg">`).
- Imágenes: `img/<nombre>.webp`, generadas desde `fuentes/` con `python3 tools/web_images.py`.
- Renders 3D: `tools/render_estudio/` y `tools/render_coworking/` (Three.js).
- Archivo único: `python3 tools/build_single.py . ziadaddami` → `dist/ziadaddami.html`.
- Las imágenes de Rampassist son provisionales.

## Publicación (Vercel)

Sitio estático sin build: en Vercel, Add New → Project → importar `ziadsworkstation/portfolio-projects`, Framework Preset «Other», sin comando de build y con la raíz del repo como directorio de salida. El dominio `ziadaddami.es` se añade en Settings → Domains y Vercel indica los registros DNS. `.vercelignore` deja fuera `tools/` y `fuentes/`.

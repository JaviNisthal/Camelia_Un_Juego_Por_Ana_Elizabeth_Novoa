# Publicar por HTTPS (GitHub Pages, gratis)

La cámara del navegador solo funciona por HTTPS. GitHub Pages lo da de serie.

1. En github.com, crea un repositorio **público** llamado `camelia-ra`.
2. Pulsa **Add file → Upload files** y arrastra el **contenido** de la carpeta del proyecto: `index.html`, `css/`, `js/`, `lib/` y `assets/`. No subas `node_modules/`. `tools/`, `source/` y `entrega/` son opcionales. Pulsa **Commit changes**.
3. Ve a **Settings → Pages**. En *Source* elige **Deploy from a branch**, luego la rama `main` y la carpeta `/ (root)`, y pulsa **Save**.
4. Espera 1–2 minutos. La dirección será `https://TU-USUARIO.github.io/camelia-ra/`.
5. Abre esa dirección en el teléfono y comprueba que carga.
6. Solo entonces genera el QR con esa dirección exacta:
   `python3 tools/make_qr.py https://TU-USUARIO.github.io/camelia-ra/`

Comprueba que en `assets/` estén `targets.mind`, `camelia_sprite.png`, `broche.png` y `config.json`. Sin `targets.mind` la cámara no arranca.

## Si no puedes compilar `targets.mind` con el script

Compilador web oficial de MindAR: <https://hiukim.github.io/mind-ar-js-doc/tools/compile>

1. Arrastra **`entrega/camelia_poster.png`**. Tiene que ser ese archivo exacto, sin recortarlo ni exportarlo de nuevo.
2. Pulsa **Start** y espera a que termine (1–2 minutos).
3. Pulsa **Download compiled** y guarda el archivo como `assets/targets.mind`, sustituyendo al anterior.
4. Vuelve a subir `assets/targets.mind` al repositorio.

Si cambias el póster, aunque sea un píxel, compila de nuevo y vuelve a imprimirlo.

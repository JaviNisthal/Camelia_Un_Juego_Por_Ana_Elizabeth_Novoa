# Publicar en GitHub Pages, paso a paso

La cámara del navegador solo funciona por HTTPS. GitHub Pages lo da gratis.

## A. Prepara los archivos (1 min)
1. Descarga `entrega/camelia-ra-web.zip` y descomprímelo.
2. Dentro verás `index.html` y las carpetas `assets`, `css`, `js`, `lib` y `licencias`.

## B. Crea el repositorio (2 min)
3. Entra en <https://github.com/new>.
4. En **Repository name** escribe `camelia-ra`.
5. Marca **Public**. Pages gratis exige un repositorio público.
6. Marca **Add a README file** y pulsa **Create repository**.

## C. Sube la página (2 min)
7. En el repositorio, pulsa **Add file → Upload files**.
8. Arrastra **el contenido** de la carpeta descomprimida, no la carpeta en sí: `index.html` y las cinco carpetas. GitHub conserva las subcarpetas al arrastrar.
9. Comprueba en la lista que aparecen `index.html` y `assets/targets.mind`.
10. Pulsa **Commit changes**.

## D. Activa Pages (1 min)
11. Ve a **Settings → Pages**, en el menú de la izquierda.
12. En **Source** elige **Deploy from a branch**.
13. En **Branch** elige `main` y la carpeta `/ (root)`. Pulsa **Save**.
14. Espera 1–2 minutos y recarga. Arriba aparecerá *Your site is live at* `https://TU-USUARIO.github.io/camelia-ra/`.

## E. Comprueba y genera el QR
15. Abre esa dirección en el teléfono y pulsa **Iniciar RA**. Si carga la cámara, la publicación funciona.
16. Pásame la dirección exacta y te genero `entrega/qr_camelia.png` y `entrega/diapositiva_final.png`. Si prefieres hacerlo tú:
    `python3 tools/make_qr.py https://TU-USUARIO.github.io/camelia-ra/`

## Si algo falla
- **404 en la dirección:** espera 2 minutos más y comprueba que `index.html` está en la raíz del repositorio, no dentro de otra carpeta.
- **«No se pudo iniciar la cámara»:** revisa el permiso de cámara del navegador en los ajustes del teléfono y que la dirección empiece por `https://`.
- **No reconoce el póster:** usa el póster impreso o mostrado a buen tamaño, con luz suficiente y sin reflejos. Debe ser exactamente `entrega/camelia_poster.png`.

## Si cambias el póster
Vuelve a compilar `targets.mind` con `node tools/compile_targets.mjs` o con el compilador web oficial, <https://hiukim.github.io/mind-ar-js-doc/tools/compile>: arrastra `entrega/camelia_poster.png`, pulsa **Start** y luego **Download compiled**, y guárdalo como `assets/targets.mind`. Después súbelo de nuevo al repositorio.

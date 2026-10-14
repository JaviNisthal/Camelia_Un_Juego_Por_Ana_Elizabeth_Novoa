# CAMELIA · Prototipo de realidad aumentada

Autora del juego: **Ana Elizabeth Novoa Aguilar**.

Se escanea un QR, se abre la página por HTTPS y se pulsa **Iniciar RA**. Al enfocar el póster aparece Camelia caminando en bucle, anclada al póster. Dos botones permiten **revelar la historia** (el broche y la frase de su madre) y **pausar o reanudar** la animación. Si se pierde el póster, el contenido se oculta y aparece «Vuelve a enfocar el póster».

Tecnología: MindAR 1.2.5 (reconocimiento de imagen) + A-Frame 1.5.0, como en el ejemplo oficial de MindAR. Las librerías van dentro de `lib/`, así que la página no depende de un CDN. No usa bases de datos, registros de usuario ni modelos 3D.

## Estructura

```
index.html            la experiencia (lo único que se publica, junto a css/, js/, lib/ y assets/)
css/ js/ lib/         estilos, lógica, MindAR y A-Frame
assets/               lo que carga la RA: camelia_sprite.png, broche.png, targets.mind, config.json, fuentes
source/               tus ilustraciones originales (ver source/LEEME.md)
tools/                scripts de preparación, compilación y prueba
entrega/              póster, GIF, fotogramas, broche, QR y diapositiva final
revision/             hojas de revisión e informes (se generan al ejecutar los scripts)
docs/                 publicar, texto para el PDF y lista de pruebas
```

## Cómo se construye (en orden)

Requisitos: Python 3 con `pip install pillow numpy scipy qrcode`, y Node 18 o superior con `npm install`.

```bash
# 1. Fotogramas, GIF y lámina para la RA (revisa revision/ antes de seguir)
python3 tools/prepare_sprites.py source/Camelia_sprites_caminata.png
# 2. Broche: primero ver las piezas numeradas, después elegir una
python3 tools/extract_brooch.py source/Camelia_elementos_juego.png
python3 tools/extract_brooch.py source/Camelia_elementos_juego.png --pieza N
# 3. Póster definitivo
python3 tools/make_poster.py --arena source/Camelia_ambientacion_principal.png --figura source/Camelia_pose_accion.png
# 4. targets.mind compilado desde ESE póster exacto
node tools/compile_targets.mjs
# 5. (opcional) Prueba automática con cámara simulada
python3 tools/make_test_video.py && node tools/test_ar.mjs
# 6. Publicar (docs/PUBLICAR.md) y, con la URL real:
python3 tools/make_qr.py https://TU-URL-REAL/
```

Si no puedes ejecutar el paso 4, usa el compilador web oficial, como se explica en `docs/PUBLICAR.md`.

## Revisión de la caminata

`prepare_sprites.py` no da la caminata por buena automáticamente. Genera:

- `revision/deteccion.png`: las 8 figuras detectadas, en rojo, y en azul lo que se descartó (números o letras).
- `revision/hoja_revision.png`: los fotogramas alineados. La línea roja marca los pies y la azul, el eje de cabeza y torso.
- `revision/papel_cebolla.png`: todas las poses superpuestas.
- `revision/informe_caminata.txt`: alturas, cambio entre fotogramas y avisos de saltos o fotogramas repetidos.

Si el orden no es correcto, se cambia con `--order 3,4,5,6,7,8,1,2` (o el que corresponda).

## Qué está probado y qué no

- Probado aquí: con imágenes de prueba sintéticas, en Chromium con cámara **simulada**. Pasaron inicio, reconocimiento, animación, pausa y reanudación, revelar historia, pérdida y recuperación del póster (`tools/test_ar.mjs`).
- Sin probar todavía: la experiencia con tus ilustraciones reales y en un teléfono real. Ver `docs/PRUEBAS.md`.

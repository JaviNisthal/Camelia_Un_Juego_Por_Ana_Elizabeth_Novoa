# Proceso de producción (para la documentación del PDF)

## 1. Recursos de partida

Ilustraciones de Ana Elizabeth Novoa Aguilar en `source/`: lámina de caminata (8 poses), vistas y expresiones, arena al atardecer, elementos del juego y pose de acción (fondo transparente). Las copias que se procesaron llegaron comprimidas a través del chat: la pose mide 941×1672 px y la arena 1672×941 px.

## 2. Animación de caminata

- **Recorte:** se quitó el blanco de fondo unido al borde (el blanco interior de ojos y brillos se conserva) y se suavizó el contorno sin dejar halo. Se detectaron las 8 figuras y se descartaron el título y los números (`revision/deteccion.png`).
- **Alineación:** todas las poses comparten un lienzo de 332×443 px, con los pies sobre la misma línea y el eje de cabeza y torso centrado. Se mantuvo la escala original: las alturas van de 409 a 419 px, una variación del 2,4 %, normal por el balanceo al caminar (`revision/hoja_revision.png`).
- **Revisión de continuidad:** se midió la posición de los dos pies en cada fotograma.

| Fotograma | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Pie trasero (x, px) | 49–115 | 44–98 | 56–117 | 79–151 | 36–108 | 48–102 | 59–115 | 56–127 |
| Pie delantero (x, px) | 227–314 | 212–296 | 202–278 | 196–267 | 229–316 | 200–288 | 201–292 | 233–316 |

  **Resultado:** el orden 01–08 es el correcto, pero la lámina **no es un ciclo de caminata completo**. Las piernas nunca se cruzan: el pie trasero siempre queda atrás y el delantero siempre delante. Faltan las dos poses de «paso», en las que la pierna trasera adelanta a la que está apoyada. Por eso el pie delantero vuelve hacia delante de golpe entre 04→05 y 07→08. Además, un paso dura 5 fotogramas y el otro 3, lo que hace cojear el ritmo.
- **Corrección aplicada:** duraciones por fotograma de 100, 100, 100, 100, 167, 167, 166 y 100 ms. Así los dos pasos duran 500 ms cada uno y el ritmo es regular, tanto en el GIF como en la RA.
- **Corrección pendiente:** el salto del pie solo desaparece dibujando dos poses nuevas, una entre 04 y 05 y otra entre 07 y 08, con la pierna trasera levantada y cruzando por delante de la apoyada. No se inventaron para no alterar el diseño de Camelia.

## 3. Broche

Recortado de la lámina de elementos, con fondo transparente, a 512×512 px (`entrega/broche.png`).

## 4. Póster

A4 vertical a 300 ppp (2480×3508 px). Lleva la arena de fondo, con el encuadre centrado en la puerta y los estandartes, y a Camelia en pose de acción sobre la arena. Encima van el título CAMELIA (tipografía Cinzel), el subtítulo «La gladiadora de los nombres», el lema «Recupera los nombres de los cautivos para liberarlos.» y el crédito de la autora. La arena se amplió desde 941 px de alto, así que impresa se ve algo suave.

## 5. Reconocimiento y RA

- `assets/targets.mind` se compiló con el compilador oficial de MindAR 1.2.5 a partir del archivo exacto `entrega/camelia_poster.png` (SHA-256 `d0f4fc54…b260`, registrado en `assets/config.json`).
- La Camelia animada se ancla al póster: 0,5 veces el ancho del póster de alto, a la derecha de la figura impresa y con los pies sobre la línea de la arena. El broche aparece encima de ella al revelar la historia.

## 6. Pruebas realizadas

- **Automática, con cámara simulada:** un vídeo del póster con movimiento e inclinación que luego desaparece, reproducido en Chromium. Las 9 comprobaciones pasaron: inicio, cámara, reconocimiento, animación, pausar, reanudar, historia, pérdida y recuperación. Capturas en `revision/prueba_*.png` e informe en `revision/prueba_automatica.json`.
- **Con teléfono real:** pendiente. Ver `docs/PRUEBAS.md`.

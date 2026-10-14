# Lista de pruebas

Haz las pruebas con el teléfono real y anota el resultado. No marques nada que no hayas comprobado.

Teléfono y navegador: ______________________  Fecha: __________  Póster: ☐ impreso ☐ en pantalla

| # | Prueba | Cómo | Resultado esperado | ✔/✘ y notas |
|---|---|---|---|---|
| 1 | Apertura del QR | Escanear el QR del PDF con la cámara del teléfono | Se abre la URL pública con `https://` | |
| 2 | Permiso de cámara | Pulsar «Iniciar RA» | El navegador pide permiso; al aceptar se ve la cámara y «Enfoca el póster» | |
| 3 | Reconocimiento | Enfocar el póster a 30–60 cm | Camelia aparece en menos de 3 s | |
| 4 | Alineación | Mover el teléfono despacio y cambiar de ángulo | Camelia sigue sobre el póster, con los pies en el suelo de la arena | |
| 5 | Animación | Observar 10 s | Caminata fluida y en bucle, sin saltos ni bordes blancos | |
| 6 | Revelar historia | Pulsar «Revelar historia» y después «Ocultar historia» | Aparecen el broche y la frase completa; luego se ocultan | |
| 7 | Pausar y reanudar | Pulsar «Pausar» y después «Reanudar» | La animación se congela y luego continúa | |
| 8 | Pérdida del póster | Apartar la cámara del póster | Todo se oculta y aparece «Vuelve a enfocar el póster» | |
| 9 | Recuperación | Volver a enfocar | Camelia reaparece | |
| 10 | Segundo dispositivo | Repetir 1–5 en otro teléfono (iPhone o Android) | Igual que arriba | |

Para la documentación, guarda capturas o un vídeo corto de las pruebas 3, 6 y 8.

## Prueba automática (complementaria, no sustituye a la anterior)

`node tools/test_ar.mjs` abre la app en Chromium con una cámara **simulada**: un vídeo del póster que después desaparece. Comprueba los mismos puntos 2–9 y guarda capturas e informe en `revision/`. Solo verifica la lógica y el anclaje; no prueba la cámara real, la iluminación ni el rendimiento del teléfono.

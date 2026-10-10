# Comparación de dos ediciones con HyperFrames

La composición del reel "¿Quién lo editó mejor?" (octubre 2026): dos ediciones del mismo video, una al lado de la otra, en dos rondas. En la primera suena la edición de la izquierda y en la segunda, la de la derecha. Al final se vota con "Comentá 1 o 2".

## Archivos

- `index.html`: la composición de HyperFrames. Incluye el titular, las etiquetas con logo, las tarjetas de video, las rondas y el cierre.
- `voces.py`: recorta el tramo de audio de cada ronda y lo nivela a −14 LUFS, para que ninguna edición gane por sonar más fuerte.
- `mezcla.py`: suma las voces y los efectos de sonido (barridos, pops, campanita y suspenso). Si le pasás un archivo de música como segundo argumento, la agrega por debajo de la voz.

## Cómo usarla

1. Instalá `hyperframes` con npm y `gsap`. Copiá `gsap.min.js` a `assets/`, porque la red del entorno bloquea el CDN.
2. Variables de entorno:
   ```
   HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
   HYPERFRAMES_NO_TELEMETRY=1  HYPERFRAMES_NO_UPDATE_CHECK=1  HYPERFRAMES_SKIP_SKILLS=1
   ```
3. Re-codificá los videos con un cuadro clave por segundo (`-g 30 -keyint_min 30`). Si no, HyperFrames congela la imagen en algunos tramos.
4. Ajustá en `index.html` los tiempos de cada ronda (`data-start`, `data-duration`, `data-media-start`) y los cuadros fijos de `assets/stills/`.
5. Corré `python voces.py <carpeta de trabajo>` y después `python mezcla.py <carpeta de trabajo> [música]`.
6. Revisá con `hyperframes lint .` y renderizá con `hyperframes render -o salida.mp4`.
7. Al exportar la versión final, pasá el audio por un limitador (`alimiter=limit=0.70` con sobremuestreo) para que no sature después de comprimir a AAC.

## Trampas

- **Cada video y audio con tiempo necesita un `id`.** Sin eso, el video sale congelado y el audio, mudo.
- **El centrado con `translateX(-50%)` de CSS** se pisa cuando GSAP anima el elemento. Hay que usar `gsap.set(..., { xPercent: -50 })`.
- **Efectos de sonido:** tienen que quedar unos 3 a 6 dB por debajo del pico de la voz. Más bajo que eso no se escuchan en el celular.
- **Logos:** el de OpenAI sale de `@lobehub/icons-static-svg` y el de Claude, de `simple-icons` o del mismo paquete de lobehub. Los dos se instalan desde npm.

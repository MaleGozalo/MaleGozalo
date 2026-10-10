# Cómo hacer el próximo reel con Claude

El paso a paso que usamos con el reel "Mucho alcance, pocos seguidores" (octubre 2026), para repetirlo sin volver a configurar nada.

## 1. Antes de grabar

Lo que aprendimos con este reel:

- **Dejá aire arriba de la cabeza.** Sentate un poco más lejos o bajá la cámara. Ahí van el gancho, los títulos y el título de la portada. En este video la cabeza quedó muy cerca del borde y hubo que extender la pared para la portada.
- **Que el sol no te pegue directo en la ropa.** La parte que se quema queda blanca y no se puede recuperar.
- **El micrófono un poco más abajo del mentón.** Pegado a la boca suena retumbante y satura en las palabras fuertes.
- **Mandá el video original del celular** (el .MOV), no una copia exportada desde otra app. La copia de este reel venía con el audio subido de más y saturado.
- **Al final, sonreí dos o tres segundos mirando a cámara.** De ahí sale la foto de la portada.

## 2. Subir el video

1. Subilo a Google Drive.
2. Compartilo como **"Cualquier persona con el enlace"**. Sin eso no se puede descargar.
3. Pasale el link a Claude.

## 3. Qué pedirle a Claude

Copiá este texto y completá lo que está entre corchetes:

```
Leé mi manual de marca (github.com/MaleGozalo/manual-de-marca) y el paso a paso en
reels/COMO-HACER-UN-REEL.md del repositorio MaleGozalo/MaleGozalo. Usá las herramientas
de reels/herramientas.

Editá este video: [link de Drive]
La idea del video: [una o dos frases]
Datos para mostrar: [capturas de estadísticas, si el reel habla de números]
Referencia de estilo: [subí el video al chat, si hay]
```

## 4. Qué tener a mano

- **Capturas de estadísticas**, si el reel habla de números: visualizaciones, porcentaje de no seguidores, espectadores, visitas al perfil y seguidores nuevos del mismo período.
- **Videos de referencia subidos directo al chat.** Los links de Instagram no se pueden abrir desde la nube.

## 5. Lo que hace Claude, en orden

1. Descarga el video y revisa color, audio, pausas y encuadre.
2. Transcribe palabra por palabra, con tiempos.
3. Propone dos o tres opciones de gancho y la tabla de momentos gráficos.
4. Arma el storyboard en HTML para que lo apruebes.
5. Exporta el MP4 en 1080 × 1920, compatible con cualquier reproductor y de menos de 30 MB, para poder mandarlo por el chat.
6. Hace la portada con la fórmula del manual y el copy.
7. Guarda todo en GitHub, en `reels/AAAA-MM-tema/`.

## 6. Descargar y publicar en Instagram

Desde el celular es más fácil subir tu propia portada.

1. **Guardá el video y la portada en el celular.** Desde la app de Claude, tocá cada archivo y guardalo. Si los bajás en la compu, pasalos por AirDrop, Google Drive o cable. Evitá WhatsApp, porque comprime el video.
2. **En Instagram:** **+** → **Reel** → elegí el video → **Siguiente**.
3. **Portada:** **Editar portada** → **Agregar desde el carrete** → elegí la portada. Fijate que el título se vea completo en el recorte del perfil.
4. **Copy:** pegá el texto del archivo `copy-instagram.txt`.
5. **Música (opcional):** si sumás un audio en tendencia, bajalo mucho para que no tape tu voz.
6. Tocá **Compartir**.

Para bajar un archivo desde GitHub: abrilo en la carpeta del reel y tocá el botón de descarga, arriba a la derecha. GitHub no reproduce videos dentro de la página.

## 7. Si algo se traba

Estos dominios tienen que estar permitidos en la red del entorno de la nube (menú del entorno → **Editar** → **Acceso a la red** → **Personalizado**):

| Para qué | Dominios |
|---|---|
| Descargar el video de Drive | `drive.google.com`, `drive.usercontent.google.com` |
| Transcribir y recortar la silueta | `huggingface.co`, `cdn-lfs.huggingface.co`, `cas-bridge.xethub.hf.co`, `us.aws.cdn.hf.co` (o `*.hf.co`) |

Otros límites que conviene saber:

- **El conector de Drive** solo baja archivos de menos de 10 MB. Para videos más pesados se usa la descarga directa, que necesita los dominios de arriba.
- **Instagram** está bloqueado y pide iniciar sesión, así que las referencias se suben al chat.
- **El chat** manda archivos de hasta 30 MB.

## Reels hechos

| Fecha | Reel | Carpeta |
|---|---|---|
| Octubre 2026 | Mucho alcance, pocos seguidores | [`2026-10-mucho-alcance-pocos-seguidores`](2026-10-mucho-alcance-pocos-seguidores) |
| Octubre 2026 | ¿Quién lo editó mejor? (ChatGPT vs. Claude Code, hecho con HyperFrames; la música se suma en Edits) | [`2026-10-quien-lo-edito-mejor`](2026-10-quien-lo-edito-mejor) |

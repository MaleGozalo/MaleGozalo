# Herramientas de edición de reels

Los scripts con los que se editó "Mucho alcance, pocos seguidores". Están pensados para que Claude los reutilice en el próximo reel. Los valores que dependen del video (pausas, zooms, tiempos y textos de los gráficos) quedaron con los de este reel como ejemplo y hay que ajustarlos en cada video.

## Estructura de trabajo

```
<carpeta de trabajo>/
  src/video.MOV          el video original
  models/modnet.onnx     recorte de silueta (Xenova/modnet en Hugging Face, Apache-2.0)
  work/                  estos archivos (incluida la carpeta gfx/)
  work/r/                salidas: capas de gráficos, audio y video
```

Las tipografías se leen del manual de marca clonado en `/home/user/manual-de-marca`.

## Instalación

- Python, en un entorno virtual: `faster-whisper`, `opencv-python-headless<5`, `onnxruntime`, `numpy` y `pillow`. OpenCV 5 ya no trae los detectores de cara, por eso va la versión 4.
- Node con `playwright` global y el Chromium de `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`. Se corre con `NODE_PATH=/opt/node22/lib/node_modules`.
- `ffmpeg`.

## Orden de uso

1. **Transcripción:** `HF_HUB_DISABLE_XET=1 python transcribe.py large-v3-turbo audio16k.wav transcript.json`. Antes, extraé el audio mono a 16 kHz con ffmpeg. Devuelve palabras con tiempos.
2. **Seguimiento de cara:** `python track2.py ../src/video.MOV faces2.json`.
3. **Plan de edición (`edl.py`):** ajustá `SEGS` (las pausas que se cortan, en cuadros), `ZOOMS`, `FACE_Y`, el modo tarjeta (`CARD_IN`, `CARD_OUT`, `CARD_RECT`) y `KEYWORDS`. Después generá `words_out.json` con `edl.words(...)` y `card.json` con `edl.card_table(...)`.
4. **Gráficos (`gfx/overlay.tpl.html`):** textos, tiempos (`T`) y datos (`DATA`) de cada momento. Corré `python gfx/build.py` y después `node gfx/render.js front|back <carpeta> <gancho> <guías 0|1> <desde:hasta:paso>`.
5. **Color (`grade.py`):** balance cálido neutro, curva de tonos, luz suave sobre la cara (sigue el seguimiento) y luz baja en la zona del sol.
6. **Audio (`audio.py`):** reparación de picos recortados, EQ, de-esser, compresor, −14 LUFS y efectos suaves.
7. **Video:** `python render_video.py salida.mp4`. Después exportá una versión compatible para el chat y para Instagram: `libx264 -profile:v main -level 4.0 -crf 22 -maxrate 6M -bufsize 12M`, audio AAC a 128k.
8. **Portada:** `python cover.py <cuadro> <zoom> <alto del pelo> foto.jpg`, después `cover_html.py` y `shot_cover.js`.
9. **Storyboard:** `storyboard.py` arma el HTML de aprobación con cuadros reales.

## Trampas conocidas

- **`adeclip`:** los filtros que van después en la misma cadena de ffmpeg se ignoran, así que va en una pasada propia. Además, antes hay que decodificar el audio a mono a 48 kHz.
- **El nivel de recorte se mide con un histograma de amplitud.** En este reel estaba en 1,40, no en 1,0. Hay que llevar ese nivel a 0,955 y volver a recortar parejo antes de reconstruir.
- **faster-whisper con PyAV nuevo falla al abrir el archivo.** Pasale el audio como array de numpy.
- **Las capturas de Chromium totalmente opacas vienen sin canal alfa.** Se leen con `load_rgba`.
- **Recorte de silueta:** BiRefNet recorta mejor, pero tarda cerca de un minuto por cuadro en CPU. MODNet tarda 0,2 s y alcanza para el texto detrás de la persona.
- **Archivos por el chat:** el límite es de 30 MB.

import base64, json, subprocess, os
N = os.environ["N"]; SB = f"{N}/work/sb3"; FD = "/home/user/manual-de-marca/tipografias"
def img(p, w=540):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vf", f"scale={w}:-1", "-q:v", "4", "-f", "mjpeg", "-"], capture_output=True, check=True).stdout
    return "data:image/jpeg;base64," + base64.b64encode(out).decode()
def font(fam, w, st, fn):
    b = base64.b64encode(open(f"{FD}/{fn}", "rb").read()).decode()
    return f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{st};src:url(data:font/ttf;base64,{b}) format('truetype');}}"
fonts = "".join([font("Poppins", 400, "normal", "Poppins-Regular.ttf"), font("Poppins", 600, "normal", "Poppins-SemiBold.ttf"),
                 font("Poppins", 800, "normal", "Poppins-ExtraBold.ttf"), font("Playfair Display", 700, "italic", "PlayfairDisplay-BoldItalic.ttf")])
hooks = [("A", "¿Te ven, pero <em>no te siguen?</em>", "Te recomiendo esta. Le habla directo a quien mira y nombra el problema que tiene tu audiencia, no solo el tuyo.", True),
         ("B", "Mucho alcance, <em>pocos seguidores</em>", "Más descriptiva. Funciona bien si tu audiencia ya maneja la palabra alcance.", False),
         ("C", "Alcance ≠ <em>seguidores</em>", "La más corta y conceptual, en la línea de “Miles de views ≠ ventas”.", False)]
moments = [
 ("0,1 – 2,9 s", "Gancho arriba: “Mucho alcance, <em>pocos seguidores</em>”.", "“Mi cuenta llega a mucha gente…”", "1.5", "outB"),
 ("3,2 – 3,7 s", "Te achicás en una tarjeta centrada con borde lila. Atrás aparece un fondo lila oscuro con luces y puntitos que se mueven.", "corte después del gancho", "3.45", "out"),
 ("3,4 – 10,1 s", "Panel “Estadísticas de mi cuenta · este mes”: 28.383 visualizaciones que cuentan hacia arriba. Las barras se llenan hasta 83,3 % no seguidores y 16,7 % seguidores, y entra la pastilla “no me conocían”.", "“Este mes” · “8 de cada 10” · “no me conocían”", "8.6", "out"),
 ("10,2 – 12,6 s", "El panel cambia a “19.965 personas me vieron → <em>182</em> visitaron mi perfil” y entra la pastilla “menos del 1 %”. Después volvés a pantalla completa.", "“pocos”", "11.0", "out"),
 ("13,2 – 15,7 s", "“NO ME FALTA” arriba y “contenido” grande, que se tacha con una línea amarilla.", "“no es que me falta contenido” · “sino”", "14.9", "out"),
 ("17,1 – 19,6 s", "Texto gigante detrás tuyo: “por qué <em>seguirme</em>”, con tu silueta adelante. Sin subtítulos.", "“por qué” · “seguirme”", "18.9", "out"),
 ("19,7 – 21,2 s", "“Male <em>Gozalo</em>” + @male.gozalo con marcador amarillo.", "“justamente eso es lo que estoy ordenando”", "20.4", "out"),
 ("21,5 – 24,2 s", "Cierre: “¿Querés ver <em>cómo lo hago?</em>” + pastilla @male.gozalo. Sin logo y sin subtítulos.", "“Si querés ver cómo lo hago”", "23.4", "out"),
]
hook_html = "".join(f"""<figure class="hook{' rec' if r else ''}"><img src="{img(f'{SB}/out{k}/1.5.jpg', 420)}" alt="Gancho {k}"><figcaption><span class="tag">{k}{' · recomendada' if r else ''}</span><b>{t}</b><span>{d}</span></figcaption></figure>""" for k, t, d, r in hooks)
rows = "".join(f"<tr><td class='n'>{i+1}</td><td class='time'>{a}</td><td>{b}</td><td class='trig'>{c}</td></tr>" for i, (a, b, c, _, _) in enumerate(moments))
frames = "".join(f"""<figure class="frame"><img src="{img(f'{SB}/{d}/{ts}.jpg')}" alt="Momento {i+1}"><figcaption><span class="tag">{i+1} · {a}</span><span>{b}</span></figcaption></figure>""" for i, (a, b, c, ts, d) in enumerate(moments))
html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Storyboard del reel</title><style>{fonts}
:root{{--lila:#9B7FD4;--tinta:#3D2B6E;--tm:#6C5F91;--indigo:#533FB7;--crema:#FAF6EF;--amarillo:#F5DE7E;--linea:#E6DDF3;}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--crema);color:var(--tinta);font:400 16px/1.55 Poppins,system-ui,sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:40px 16px 72px}}
h1{{font:800 clamp(30px,5vw,46px)/1.05 Poppins;letter-spacing:-.02em;margin:0 0 6px}} h1 em,h2 em,b em,td em,figcaption em{{font-family:'Playfair Display';font-style:italic;font-weight:700;color:var(--indigo)}}
h2{{font:800 26px/1.15 Poppins;letter-spacing:-.01em;margin:48px 0 14px}} .sub{{color:var(--tm);margin:0}}
.meta{{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0}} .meta span{{background:#fff;border:1.5px solid var(--linea);border-radius:999px;padding:6px 14px;font-weight:600;font-size:14px}}
blockquote{{margin:0;background:#fff;border-left:5px solid var(--lila);border-radius:0 14px 14px 0;padding:16px 20px;font-size:17px}}
.hooks{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}}
figure{{margin:0;background:#fff;border-radius:16px;overflow:hidden;border:1.5px solid var(--linea)}} figure img{{display:block;width:100%;height:auto}}
figcaption{{padding:12px 14px 16px;font-size:14.5px;display:flex;flex-direction:column;gap:4px}} figcaption b{{font-size:17px}}
.hook.rec{{border-color:var(--lila);box-shadow:0 0 0 3px rgba(155,127,212,.25)}}
.tag{{align-self:flex-start;background:var(--amarillo);color:var(--tinta);font-weight:800;font-size:12px;letter-spacing:.08em;text-transform:uppercase;border-radius:999px;padding:3px 10px}}
.tablewrap{{overflow-x:auto;background:#fff;border-radius:16px;border:1.5px solid var(--linea)}} table{{border-collapse:collapse;width:100%;min-width:620px}}
th,td{{text-align:left;padding:12px 14px;border-bottom:1px solid var(--linea);vertical-align:top;font-size:15px}} th{{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--tm)}}
td.n{{font-weight:800;color:var(--lila)}} td.time{{white-space:nowrap;font-weight:600}} td.trig{{color:var(--tm)}} tr:last-child td{{border-bottom:0}}
.frames{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}}
ul.base{{background:#fff;border-radius:16px;border:1.5px solid var(--linea);padding:18px 18px 18px 40px;margin:0}} ul.base li{{margin:6px 0}}
.ask{{background:var(--tinta);color:#fff;border-radius:18px;padding:22px 24px}} .ask h2{{color:#fff;margin-top:0}} .ask li{{margin:8px 0}} .ask em{{font-family:'Playfair Display';font-style:italic;color:#FFE39A}}
.note{{font-size:13.5px;color:var(--tm);margin-top:10px}}
</style></head><body><div class="wrap">
<p class="sub">Storyboard para aprobar antes de renderizar</p>
<h1>Reel: “Mucho alcance, <em>pocos seguidores</em>”</h1>
<div class="meta"><span>1080 × 1920 · 30 fps</span><span>24,2 s (el original dura 25,5 s)</span><span>Gancho B</span><span>Estilo inmersivo</span><span>Centrada todo el video</span></div>
<h2>Lo que decís</h2>
<blockquote>Mi cuenta llega a mucha gente, pero casi nadie me sigue. Este mes, más de 8 de cada 10 personas que vieron mis videos no me conocían, y aun así muy pocos fueron mis seguidores nuevos. Entendí que no es que me falta contenido, sino que me falta decirle al que llega por qué debería seguirme. Y justamente eso es lo que estoy ordenando ahora. Si querés ver cómo lo hago, te espero acá.</blockquote>
<h2>Lo que tomé del reel de referencia</h2>
<ul class="base">
<li><b>La explicación gana espacio:</b> cuando hablás de los datos, te achicás en una tarjeta centrada y arriba aparece un panel con tus estadísticas. Después volvés a pantalla completa.</li>
<li><b>El concepto aparece en movimiento:</b> los números cuentan hacia arriba, las barras se llenan y el panel cambia de dato cuando decís “pocos”.</li>
<li><b>Fondo inmersivo:</b> lila oscuro de tu manual (#2B1E47) con luces suaves y puntitos que se mueven, en lugar del violeta neón del original.</li>
<li><b>Títulos con bajada:</b> “NO ME FALTA” en mayúsculas espaciadas arriba y la palabra grande abajo.</li>
<li><b>Presentadora centrada</b> en todo el video, también dentro de la tarjeta.</li>
</ul>
<h2>Momentos gráficos</h2>
<div class="tablewrap"><table><thead><tr><th>#</th><th>Tiempo</th><th>Qué aparece</th><th>Palabra que lo dispara</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">Tramo limpio, solo con subtítulos: 15,7 – 17,1 s. Subtítulos de una palabra por vez en Poppins blanca, con las palabras clave en amarillo.</p>
<h2>Cómo queda cada momento</h2>
<p class="note" style="margin:-4px 0 14px">Cuadros reales del video con el color corregido. La línea punteada es la zona segura de Instagram y la franja rosada, la de los subtítulos (solo se ven en el storyboard).</p>
<div class="frames">{frames}</div>
<h2>La base del video</h2>
<ul class="base">
<li><b>Centrado:</b> te sigo la cara cuadro por cuadro y el encuadre te acompaña con un movimiento suave. Quedás centrada todo el video (el desvío máximo es de 31 px).</li>
<li><b>Cortes:</b> saco las pausas de 3,1 s, 12,6 s y 22,0 s y dejo un respiro de 0,12 s. En cada corte cambia el zoom (112 % → 106 % → acercamiento lento de 110 a 118 % en “Entendí…” → 124 % en el cierre), así el salto no se nota.</li>
<li><b>Color:</b> limpio y sin filtro. Bajé las luces quemadas de la camisa y neutralicé un poco el amarillo de la pared.</li>
<li><b>Audio:</b> hoy satura (llega a +0,2 dB). Lo limpio, le pongo compresión suave y lo llevo a −14 LUFS con pico de −1 dB.</li>
<li><b>Efectos:</b> un pop suave cuando entran la tarjeta, la pastilla, el nombre y el @, y un whoosh bajito en el texto gigante, unos 20 dB por debajo de tu voz. Sin música.</li>
</ul>
<h2>Para confirmar</h2>
<div class="ask"><ol>
<li><b>Seguidores nuevos:</b> en las capturas no aparece ese número, así que usé las <b>182 visitas al perfil</b>. Es un dato real y cuenta lo mismo: de 19.965 personas que te vieron, menos del 1 % entró a tu perfil. Si querés el número de seguidores nuevos, pasámelo y lo cambio.</li>
<li><b>¿Apruebo y exporto?</b> Con tu ok exporto el MP4 final en 1080 × 1920.</li>
</ol></div>
</div></body></html>"""
open("/home/user/edicion-reel/storyboard.html", "w").write(html)
print("bytes", len(html))

import base64, sys
FD = "/home/user/manual-de-marca/tipografias"
photo, l1, l2, out = sys.argv[1:5]
b = lambda p: base64.b64encode(open(p, "rb").read()).decode()
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Poppins;font-weight:700;font-style:normal;src:url(data:font/ttf;base64,{b(FD+'/Poppins-Bold.ttf')})}}
@font-face{{font-family:Poppins;font-weight:700;font-style:italic;src:url(data:font/ttf;base64,{b(FD+'/Poppins-BoldItalic.ttf')})}}
html,body{{margin:0}} #c{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000 url(data:image/jpeg;base64,{b(photo)}) center/cover}}
#c:before{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(28,18,48,.42) 0,rgba(28,18,48,0) 900px)}}
#t{{position:absolute;left:0;right:0;top:300px;text-align:center;font-family:Poppins;font-weight:700;
  text-shadow:0 2px 3px rgba(28,18,48,.55),0 4px 18px rgba(28,18,48,.5),0 0 44px rgba(28,18,48,.35)}}
.l1{{display:inline-block;color:#9B7FD4;font-size:104px;line-height:1;letter-spacing:-.02em;white-space:nowrap}}
.l2{{display:inline-block;color:#FFF2B8;font-style:italic;font-size:116px;line-height:1;letter-spacing:-.01em;white-space:nowrap;transform:rotate(-5deg);margin-top:8px}}
</style></head><body><div id="c"><div id="t"><span class="l1">{l1}</span><br><span class="l2">{l2}</span></div></div>
<script>
document.fonts.ready.then(()=>{{const t=document.getElementById('t');const m=Math.max(...[...t.querySelectorAll('span')].map(s=>s.getBoundingClientRect().width));
 const k=Math.min(1,940/m); t.querySelectorAll('span').forEach(s=>s.style.fontSize=(parseFloat(getComputedStyle(s).fontSize)*k)+'px'); window.__k=k;
 const r=t.getBoundingClientRect(); window.__box=[r.top,r.bottom]; document.body.dataset.ready=1;}});
</script></body></html>"""
open(out, "w").write(html)

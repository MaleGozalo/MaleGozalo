import base64, json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
FD = "/home/user/manual-de-marca/tipografias"
faces = [("Poppins", 600, "normal", "Poppins-SemiBold.ttf"), ("Poppins", 700, "normal", "Poppins-Bold.ttf"),
         ("Poppins", 800, "normal", "Poppins-ExtraBold.ttf"), ("Playfair Display", 700, "italic", "PlayfairDisplay-BoldItalic.ttf")]
css = ""
for fam, w, st, fn in faces:
    b64 = base64.b64encode(open(f"{FD}/{fn}", "rb").read()).decode()
    css += f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{st};src:url(data:font/ttf;base64,{b64}) format('truetype');}}\n"
words = json.load(open(os.path.join(here, "..", "words_out.json")))
tpl = open(os.path.join(here, "overlay.tpl.html")).read()
card = json.load(open(os.path.join(here, "..", "card.json")))
card = [{k: round(v, 2) for k, v in r.items()} for r in card]
html = tpl.replace("/*CARD*/[]", json.dumps(card, separators=(",", ":"))).replace("/*FONTS*/", css).replace("/*WORDS*/[]", json.dumps(words, ensure_ascii=False))
open(os.path.join(here, "overlay.html"), "w").write(html)
print("ok", len(html))

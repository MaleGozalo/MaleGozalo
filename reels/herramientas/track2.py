import cv2, json, sys, numpy as np
src, out = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(src)
H = cv2.data.haarcascades
cas = [cv2.CascadeClassifier(H + n) for n in ('haarcascade_frontalface_default.xml','haarcascade_frontalface_alt2.xml','haarcascade_frontalface_alt.xml')]
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
SC = 0.4
res = []
i = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    g = clahe.apply(cv2.cvtColor(cv2.resize(fr, None, fx=SC, fy=SC), cv2.COLOR_BGR2GRAY))
    cands = []
    for c in cas:
        for (x, y, w, h) in c.detectMultiScale(g, 1.08, 3, minSize=(int(400*SC), int(400*SC)), maxSize=(int(760*SC), int(760*SC))):
            cands.append(((x+w/2)/SC, (y+h/2)/SC, w/SC))
    if cands:
        a = np.array(cands)
        # keep candidates in plausible region (face is upper-middle)
        a = a[(a[:,1] > 650) & (a[:,1] < 1050) & (a[:,0] > 300) & (a[:,0] < 800)]
    if cands and len(a):
        m = np.median(a, axis=0)
        res.append([i, float(m[0]), float(m[1]), float(m[2])])
    else:
        res.append([i, None, None, None])
    i += 1
json.dump({"frames": res}, open(out, "w"))
det = [r for r in res if r[1] is not None]
print("frames", i, "detected", len(det))
for s in range(0, 26):
    sel = [r for r in det if s*30 <= r[0] < (s+1)*30]
    print(s, len(sel), *( [round(np.mean([r[k] for r in sel])) for k in (1,2,3)] if sel else []))

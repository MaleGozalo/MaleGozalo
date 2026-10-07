import json, numpy as np
FPS = 30
W, H = 1080, 1920
# segments as source frame ranges [start, end) after trimming pauses
SEGS = [(0, 95), (99, 381), (395, 661), (680, 762)]
ZOOMS = [(1.12, 1.12), (1.06, 1.06), (1.10, 1.18), (1.24, 1.24)]  # (start, end) zoom per segment; S3 is a slow push-in
CHIN_SRC_OFFSET = 245      # chin is ~245 px below the tracked face center in source
FACE_Y = [None, None, None, 1010]  # S4 has no subtitles: sit the face lower to free the top for the closing
CHIN_TARGET = 1225         # keep chin above the subtitle band (y 1250)

def out_frames():
    """list of (out_index, seg_index, src_frame)"""
    res, k = [], 0
    for si, (a, b) in enumerate(SEGS):
        for f in range(a, b):
            res.append((k, si, f)); k += 1
    return res

def src_to_out_time(t):
    """times inside a removed pause snap to the next kept segment"""
    acc = 0.0
    for a, b in SEGS:
        ta, tb = a / FPS, b / FPS
        if t < tb:
            return acc + max(0.0, t - ta)
        acc += (b - a) / FPS
    return acc

def _gauss(x, sigma):
    r = int(3 * sigma); k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2); k /= k.sum()
    xp = np.pad(x, r, mode='edge'); return np.convolve(xp, k, mode='valid')

def track(path):
    fr = json.load(open(path))['frames']
    n = len(fr)
    cx = np.array([r[1] if r[1] is not None else np.nan for r in fr], float)
    cy = np.array([r[2] if r[2] is not None else np.nan for r in fr], float)
    idx = np.arange(n)
    for a in (cx, cy):
        ok = ~np.isnan(a); a[~ok] = np.interp(idx[~ok], idx[ok], a[ok])
    return cx, cy

def crop_table(track_path, sigma=18):
    cx, cy = track(track_path)
    table = {}
    for si, (a, b) in enumerate(SEGS):
        z0, z1 = ZOOMS[si]
        sx = _gauss(cx[a:b], sigma)
        sy = np.full(b - a, np.median(cy[a:b]))
        for j, f in enumerate(range(a, b)):
            u = j / max(1, b - a - 1); u = u * u * (3 - 2 * u)
            z = z0 + (z1 - z0) * u
            ox = np.clip(sx[j] * z - W / 2, 0, W * (z - 1))
            if FACE_Y[si] is None:
                oy = np.clip((sy[j] + CHIN_SRC_OFFSET) * z - CHIN_TARGET, 0, H * (z - 1))
            else:
                oy = np.clip(sy[j] * z - FACE_Y[si], 0, H * (z - 1))
            table[f] = (z, float(ox), float(oy), float(sx[j] * z - ox), float(sy[j] * z - oy))
    return table

KEYWORDS = {"nadie", "8", "10", "pocos", "contenido", "seguirme", "ordenando"}

def words(transcript_path):
    """word list in output time: [{w, s, e, key}]"""
    import re
    d = json.load(open(transcript_path))
    out = []
    for seg in d:
        for w in seg["words"]:
            txt = re.sub(r"[.,;:¿?¡!]", "", w["w"]).strip().lower()
            if txt == "quieres": txt = "querés"
            s, e = src_to_out_time(w["s"]), src_to_out_time(w["e"])
            out.append({"w": txt, "s": round(s, 3), "e": round(e, 3), "key": txt in KEYWORDS})
    return out

# ---- framed ("tarjeta") mode: the presenter shrinks into a centered card and the explanation gains space ----
CARD_IN, CARD_OUT, CARD_D = 3.20, 12.10, 0.45
CARD_RECT = (240, 760, 600, 720)   # x, y, w, h  (centered on x = 540)
CARD_R = 40
CARD_S = 0.58                       # presenter scale inside the card
CARD_ANCHOR_Y = 0.47                # where the face sits inside the card (fraction of its height)

def _ease(x):
    x = min(1.0, max(0.0, x)); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2

def card_u(t):
    if t < CARD_IN or t > CARD_OUT + CARD_D: return 0.0
    if t < CARD_IN + CARD_D: return _ease((t - CARD_IN) / CARD_D)
    if t <= CARD_OUT: return 1.0
    return 1 - _ease((t - CARD_OUT) / CARD_D)

def card_table(track_path):
    """per output frame: u, card rect, radius, and the presenter placement (scale s at offset ox, oy)"""
    ct = crop_table(track_path)
    tx, ty, tw, th = CARD_RECT
    rows = []
    for k, si, f in out_frames():
        t = k / FPS; u = card_u(t)
        fx, fy = ct[f][3], ct[f][4]                      # face position in the reframed frame
        L = lambda a, b: a + (b - a) * u
        s = L(1.0, CARD_S)
        ax, ay = L(fx, tx + tw / 2), L(fy, ty + th * CARD_ANCHOR_Y)
        rows.append({"u": round(u, 4), "x": L(0, tx), "y": L(0, ty), "w": L(W, tw), "h": L(H, th), "r": L(0, CARD_R),
                     "s": s, "ox": ax - fx * s, "oy": ay - fy * s})
    return rows

"""color grade v2: warm-neutral balance, lifted face, protected highlights (applied in source space)"""
import numpy as np, cv2, json, os
N = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _pchip(xs, ys, x):
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    h = np.diff(xs); d = np.diff(ys) / h
    m = np.zeros_like(ys)
    for i in range(1, len(xs) - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    m[0], m[-1] = d[0], d[-1]
    i = np.clip(np.searchsorted(xs, x) - 1, 0, len(h) - 1)
    t = (x - xs[i]) / h[i]
    h00, h10, h01, h11 = 2*t**3 - 3*t**2 + 1, t**3 - 2*t**2 + t, -2*t**3 + 3*t**2, t**3 - t**2
    return h00 * ys[i] + h10 * h[i] * m[i] + h01 * ys[i + 1] + h11 * h[i] * m[i + 1]

# tone curve: gentle shadow lift, brighter mids, soft shoulder so the sunlit shirt stops clipping
CURVE = _pchip([0, .08, .25, .5, .72, .88, 1.0], [.015, .095, .285, .555, .77, .875, .935], np.linspace(0, 1, 1024))
GAINS = np.array([1.045, 1.0, .94], np.float32)        # B, G, R  (cool the orange cast a little)
SAT = .93
_track = None
def _face(f):
    global _track
    if _track is None:
        fr = json.load(open(f"{N}/work/faces2.json"))["frames"]
        n = len(fr); idx = np.arange(n)
        arr = np.array([[r[1] or np.nan, r[2] or np.nan, r[3] or np.nan] for r in fr], float)
        for c in range(3):
            ok = ~np.isnan(arr[:, c]); arr[~ok, c] = np.interp(idx[~ok], idx[ok], arr[ok, c])
        k = np.exp(-.5 * (np.arange(-24, 25) / 8) ** 2); k /= k.sum()
        _track = np.stack([np.convolve(np.pad(arr[:, c], 24, mode="edge"), k, mode="valid") for c in range(3)], 1)
    return _track[min(f, len(_track) - 1)]

_yy, _xx = np.mgrid[0:1920, 0:1080].astype(np.float32)
_bottom = np.clip((_yy - 1250) / 450, 0, 1); _bottom = _bottom * _bottom * (3 - 2 * _bottom)

def grade(img_bgr, f):
    x = img_bgr.astype(np.float32) / 255.0
    x = np.clip(x * GAINS, 0, 1)
    x = CURVE[(x * 1023).astype(np.int32)]
    y = (x @ np.array([.114, .587, .299], np.float32))[..., None]
    x = y + SAT * (x - y)
    # soft "light" on the face: an elliptical window that follows the tracked face
    cx, cy, w = _face(f)
    e = ((_xx - cx) / (w * .62)) ** 2 + ((_yy - (cy + w * .05)) / (w * .82)) ** 2
    win = np.clip(1.25 - e, 0, 1); win = win * win * (3 - 2 * win)
    lift = 1 + .085 * win[..., None] * (1 - y)          # mostly mids/shadows on the face
    x = x * lift
    # bring down the sun patch on the shirt (bottom of frame, highlights only)
    hi = np.clip((y - .62) / .3, 0, 1)
    x = x * (1 - .14 * (_bottom[..., None] * hi))
    return np.clip(x * 255 + .5, 0, 255).astype(np.uint8)

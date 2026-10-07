import cv2, numpy as np, os, sys
import edl, base
N = base.N
_mod = None
def matte_fast(img):
    """MODNet person alpha; chair edge at the far left is suppressed"""
    global _mod
    import onnxruntime as ort
    if _mod is None:
        o = ort.SessionOptions(); o.intra_op_num_threads = 4
        _mod = ort.InferenceSession(f"{N}/models/modnet.onnx", o, providers=["CPUExecutionProvider"])
    h, w = img.shape[:2]; rh = 1024; rw = int(w * rh / h) // 32 * 32
    x = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), (rw, rh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    y = _mod.run(None, {"input": ((x - .5) / .5).transpose(2, 0, 1)[None]})[0][0, 0]
    a = cv2.resize(y, (w, h), interpolation=cv2.INTER_LINEAR)
    a[:, :150] *= np.linspace(0, 1, 150)[None, :]
    return np.clip(a, 0, 1)

def load_rgba(path):
    """read an overlay PNG as 4-channel BGRA (fully opaque screenshots come without alpha)"""
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im is None: return None
    if im.ndim == 2: im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGRA)
    elif im.shape[2] == 3: im = cv2.cvtColor(im, cv2.COLOR_BGR2BGRA)
    return im

def over(dst, png_rgba):
    a = png_rgba[..., 3:4].astype(np.float32) / 255.0
    return (dst.astype(np.float32) * (1 - a) + png_rgba[..., :3].astype(np.float32) * a)

def rounded_mask(x, y, w, h, r):
    """anti-aliased rounded-rectangle coverage over the full frame"""
    yy, xx = np.mgrid[0:edl.H, 0:edl.W].astype(np.float32) + .5
    cx, cy, hx, hy = x + w / 2, y + h / 2, w / 2 - r, h / 2 - r
    dx = np.maximum(np.abs(xx - cx) - hx, 0); dy = np.maximum(np.abs(yy - cy) - hy, 0)
    d = np.sqrt(dx * dx + dy * dy) - r
    return np.clip(.5 - d, 0, 1)

def compose(base_img, front=None, back=None, alpha=None, card=None):
    out = base_img.astype(np.float32)
    if card is not None and card["u"] > 0:
        # framed mode: background scene, then the presenter scaled into the card
        bg = back[..., :3].astype(np.float32) * (back[..., 3:4] / 255.0) if back is not None else np.zeros_like(out)
        M = np.float32([[card["s"], 0, card["ox"]], [0, card["s"], card["oy"]]])
        pres = cv2.warpAffine(base_img, M, (edl.W, edl.H), flags=cv2.INTER_AREA if card["s"] < .9 else cv2.INTER_LINEAR).astype(np.float32)
        m = rounded_mask(card["x"], card["y"], card["w"], card["h"], card["r"])[..., None]
        out = bg * (1 - m) + pres * m
        back = None
    if back is not None and back[..., 3].any():
        if alpha is None: alpha = matte_fast(base_img)
        bg = over(out, back)
        out = bg * (1 - alpha[..., None]) + out * alpha[..., None]
    if front is not None:
        out = over(out, front)
    return np.clip(out + .5, 0, 255).astype(np.uint8)

def frame_at(t):
    k = min(int(round(t * edl.FPS)), len(edl.out_frames()) - 1)
    return edl.out_frames()[k]

if __name__ == "__main__":
    # python compose.py <frontdir> <backdir|-> <outdir> t1,t2,...
    fd, bd, od, ts = sys.argv[1:5]
    os.makedirs(od, exist_ok=True)
    for ts_ in ts.split(","):
        t = float(ts_); k, si, f = frame_at(t)
        img = base.reframe(base.src_frame(f), f)
        fr = load_rgba(f"{fd}/{ts_}.png") if os.path.exists(f"{fd}/{ts_}.png") else None
        bk = load_rgba(f"{bd}/{ts_}.png") if bd != "-" and os.path.exists(f"{bd}/{ts_}.png") else None
        import json
        card = json.load(open(f"{N}/work/card.json"))[k]
        cv2.imwrite(f"{od}/{ts_}.jpg", compose(img, fr, bk, card=card), [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(ts_, "->", k, si, f)

import subprocess, numpy as np, cv2, os
import edl
N = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = f"{N}/src/video.MOV"
_table = None
def table():
    global _table
    if _table is None: _table = edl.crop_table(f"{N}/work/faces2.json")
    return _table

def src_frame(f):
    """color-corrected source frame f as BGR uint8"""
    cmd = ["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"select=eq(n\\,{f})", "-vsync", "0", "-frames:v", "1",
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    import grade
    return grade.grade(np.frombuffer(raw, np.uint8).reshape(edl.H, edl.W, 3), f)

def reframe(img, f):
    z, ox, oy, _, _ = table()[f]
    M = np.float32([[z, 0, -ox], [0, z, -oy]])
    return cv2.warpAffine(img, M, (edl.W, edl.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

_sess = None
def matte(img):
    """person alpha in [0,1] for a BGR frame"""
    global _sess
    import onnxruntime as ort
    if _sess is None:
        o = ort.SessionOptions(); o.intra_op_num_threads = 4
        _sess = ort.InferenceSession(f"{N}/models/birefnet_portrait.onnx", o, providers=["CPUExecutionProvider"])
    x = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), (1024, 1024), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    y = _sess.run(None, {"input_image": x.transpose(2, 0, 1)[None]})[0][0, 0]
    if y.min() < 0 or y.max() > 1: y = 1 / (1 + np.exp(-y))
    return cv2.resize(y, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)

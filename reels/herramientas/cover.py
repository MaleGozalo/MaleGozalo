import cv2, numpy as np, subprocess, sys, os, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grade
N = grade.N
f = int(sys.argv[1]); S = float(sys.argv[2]); HAIR_TOP = float(sys.argv[3]); out = sys.argv[4]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{N}/src/video.MOV", "-vf", f"select=eq(n\\,{f})", "-vsync", "0", "-frames:v", "1",
                      "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
img = grade.grade(np.frombuffer(raw, np.uint8).reshape(1920, 1080, 3), f)
cx, cy, w = grade._face(f)
ox = min(max(cx * S - 540, 0), 1080 * (S - 1))
yf = HAIR_TOP + 445 * S                    # face center in the cover
oy = cy * S - yf                            # may be negative: the frame moves down
# map cover -> source; the plain wall at the top is stretched upward to replace the wooden shelf strip
yy, xx = np.mgrid[0:1920, 0:1080].astype(np.float32)
map_x = (xx + ox) / S
map_y = (yy + oy) / S
Y1 = 380.0; src_top = 78.0; src_y1 = (Y1 + oy) / S
top = yy < Y1
map_y[top] = src_top + (src_y1 - src_top) * (yy[top] / Y1)
cov = cv2.remap(img, map_x.astype(np.float32), map_y.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE).astype(np.float32) / 255
# cover look from the manual: colours a touch muted, highlights lower, soft vignette
y = cov @ np.array([.114, .587, .299], np.float32)
cov = y[..., None] + .9 * (cov - y[..., None])
cov = np.where(cov > .7, .7 + (cov - .7) * .72, cov)
d = np.sqrt(((xx - 540) / 760) ** 2 + ((yy - 980) / 1150) ** 2)
cov *= (1 - .22 * np.clip(d - .55, 0, 1) ** 1.4)[..., None]
cv2.imwrite(out, np.clip(cov * 255 + .5, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
print("face x in cover", round(cx * S - ox), "| face y", round(yf), "| ox", round(ox), "oy", round(oy))

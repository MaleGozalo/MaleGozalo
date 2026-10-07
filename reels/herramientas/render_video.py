import subprocess, json, os, sys, time, numpy as np, cv2
import edl, base, compose as C
N = base.N; R = f"{N}/work/r"
out_path = sys.argv[1]
card = json.load(open(f"{N}/work/card.json"))
keep = {f: (k, si) for k, si, f in edl.out_frames()}
import grade
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", base.SRC, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{edl.W}x{edl.H}", "-r", str(edl.FPS), "-i", "-",
                        "-i", f"{R}/audio_final.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out_path], stdin=subprocess.PIPE)
fsz = edl.W * edl.H * 3; f = 0; prev_alpha = None; t0 = time.time(); n = 0
while True:
    raw = dec.stdout.read(fsz)
    if len(raw) < fsz: break
    if f in keep:
        k, si = keep[f]
        img = base.reframe(grade.grade(np.frombuffer(raw, np.uint8).reshape(edl.H, edl.W, 3), f), f)
        front = C.load_rgba(f"{R}/front/{k}.png")
        back = C.load_rgba(f"{R}/back/{k}.png") if os.path.exists(f"{R}/back/{k}.png") else None
        alpha = None
        if back is not None and card[k]["u"] == 0 and back[..., 3].any():
            a = C.matte_fast(img)
            alpha = a if prev_alpha is None else .65 * a + .35 * prev_alpha   # light temporal smoothing against flicker
            prev_alpha = alpha
        else:
            prev_alpha = None
        frame = C.compose(img, front, back, alpha=alpha, card=card[k])
        enc.stdin.write(frame.tobytes()); n += 1
        if n % 100 == 0: print("frames", n, round(time.time() - t0, 1), "s", flush=True)
    f += 1
enc.stdin.close(); enc.wait(); dec.wait()
print("done", n, "frames", round(time.time() - t0, 1), "s")

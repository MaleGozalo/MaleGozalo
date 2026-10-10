import json, subprocess, numpy as np, wave, sys, os
N = sys.argv[1]; C = f"{N}/cmp"; SR = 48000
TOTAL = 33.15
R1 = dict(src="gpt", t=2.60, a=0.0, d=12.55)       # round 1: ChatGPT audio
R2 = dict(src="claude", t=15.15, a=13.15, d=14.50)  # round 2: Claude audio
def norm_clip(r, out):
    raw = f"{C}/{r['src']}_seg.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(r["a"]), "-t", str(r["d"]), "-i", f"{C}/src/{r['src']}.mp4", "-vn", "-ac", "2", "-ar", str(SR),
                    "-af", f"afade=t=in:d=0.02,afade=t=out:st={r['d']-0.25}:d=0.25", raw], check=True)
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    js = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
          f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", ln + f",aresample={SR}", "-ac", "2", "-f", "f32le", out], check=True)
    print(r["src"], "measured", js["input_i"], "LUFS -> -14")
    return np.fromfile(out, np.float32).reshape(-1, 2)
rng = np.random.default_rng(3)
def pop(db=-27):
    n = int(.09 * SR); t = np.arange(n) / SR; f = 320 + 700 * np.exp(-t / .018)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - np.exp(-t / .002)) * np.exp(-t / .028) * 10 ** (db / 20)
def whoosh(dur=.45, db=-30, peak=.6):
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    fc = 600 + 3800 * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2; y = np.zeros(n); s = 0.0
    for i in range(n): s += (1 - np.exp(-2 * np.pi * fc[i] / SR)) * (x[i] - s); y[i] = s
    y -= np.convolve(y, np.ones(64) / 64, mode="same")
    env = np.where(t < peak * dur, (t / (peak * dur)) ** 2, np.exp(-(t - peak * dur) / (.12 * dur)))
    return y / (np.abs(y).max() + 1e-9) * env * 10 ** (db / 20)
mix = np.zeros((int(TOTAL * SR) + SR, 2), np.float32)
def put(x, t):
    i = int(t * SR); x = x if x.ndim == 2 else np.stack([x, x], 1); mix[i:i + len(x)] += x[:len(mix) - i]
put(norm_clip(R1, f"{C}/r1.f32"), R1["t"]); put(norm_clip(R2, f"{C}/r2.f32"), R2["t"])
for kind, t, kw in [("whoosh", 0.05, dict(dur=.6, db=-30)), ("pop", 0.92, {}), ("pop", 1.07, {}), ("whoosh", 2.30, dict(dur=.4, db=-32)),
                    ("whoosh", 14.88, dict(dur=.5, db=-29)), ("whoosh", 29.55, dict(dur=.5, db=-30)), ("pop", 29.95, {}), ("pop", 30.10, {}), ("pop", 30.75, dict(db=-29))]:
    put(pop(**kw) if kind == "pop" else whoosh(**kw), t)
mix = mix[:int(TOTAL * SR)]
peak = np.abs(mix).max(); print("peak", round(float(peak), 3))
if peak > .89: mix *= .89 / peak
w = wave.open(f"{C}/proj/assets/mix.wav", "w"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()

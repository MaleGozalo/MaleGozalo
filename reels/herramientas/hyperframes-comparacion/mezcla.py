"""voice rounds (-14 LUFS) + audible SFX + optional music bed ducked under the voice"""
import json, subprocess, numpy as np, wave, sys
N = sys.argv[1]; MUSIC = sys.argv[2] if len(sys.argv) > 2 else None
C = f"{N}/cmp"; SR = 48000; TOTAL = 33.15
V1, V2 = (2.60, 15.15), (15.15, 29.65)                 # voice windows on the timeline
rng = np.random.default_rng(5)
db = lambda x: 10 ** (x / 20)
def stereo(x): return x if x.ndim == 2 else np.stack([x, x], 1)
def pop(peak=-16, f0=1100, f1=300):
    n = int(.11 * SR); t = np.arange(n) / SR; f = f1 + (f0 - f1) * np.exp(-t / .02)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - np.exp(-t / .0015)) * np.exp(-t / .035)
    return x / np.abs(x).max() * db(peak)
def ding(peak=-18, f=1318.5):
    n = int(1.1 * SR); t = np.arange(n) / SR; idx = 2.2 * np.exp(-t / .12)
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 3.5 * t)) * np.exp(-t / .38) * (1 - np.exp(-t / .003))
    x += .35 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / .2)
    return x / np.abs(x).max() * db(peak)
def whoosh(dur=.5, peak=-18, rise=.6):
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    fc = 500 + 5000 * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2; y = np.zeros(n); s = 0.0
    for i in range(n): s += (1 - np.exp(-2 * np.pi * fc[i] / SR)) * (x[i] - s); y[i] = s
    y -= np.convolve(y, np.ones(48) / 48, mode="same")
    env = np.where(t < rise * dur, (t / (rise * dur)) ** 2, np.exp(-(t - rise * dur) / (.13 * dur)))
    y *= env; pan = np.stack([np.linspace(1, .55, n), np.linspace(.55, 1, n)], 1)   # swipe left -> right
    y = stereo(y) * pan
    return y / np.abs(y).max() * db(peak)
def riser(dur=1.1, peak=-20):
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    fc = 300 + 6000 * (t / dur) ** 2; y = np.zeros(n); s = 0.0
    for i in range(n): s += (1 - np.exp(-2 * np.pi * fc[i] / SR)) * (x[i] - s); y[i] = s
    tone = np.sin(2 * np.pi * np.cumsum(220 + 660 * (t / dur) ** 2) / SR) * .35
    y = (y / np.abs(y).max() + tone) * (t / dur) ** 2.2
    return y / np.abs(y).max() * db(peak)
mix = np.zeros((int(TOTAL * SR) + 2 * SR, 2), np.float32)
def put(x, t, g=1.0):
    i = int(t * SR); x = stereo(x) * g; mix[i:i + len(x)] += x[:len(mix) - i]
# voice rounds, already normalized to -14 LUFS by mix.py
put(np.fromfile(f"{C}/r1.f32", np.float32).reshape(-1, 2), V1[0])
put(np.fromfile(f"{C}/r2.f32", np.float32).reshape(-1, 2), V2[0])
sfx = [(whoosh(.7, -19), 0.0), (pop(-15), .92), (pop(-15, 1300, 360), 1.07), (whoosh(.45, -20), 2.18), (ding(-19), 2.40),
       (whoosh(.55, -17), 14.85), (ding(-19, 1568), 15.08), (riser(0.6, -20), 29.1), (whoosh(.5, -18), 29.55),
       (pop(-13), 29.95), (pop(-13, 1300, 360), 30.10), (pop(-15, 900, 260), 30.75), (ding(-21, 1760), 31.1)]
for x, t in sfx: put(x, t)
if MUSIC:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", MUSIC, "-ac", "2", "-ar", str(SR), "-af", "loudnorm=I=-14:TP=-1.5", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    m = np.frombuffer(raw, np.float32).reshape(-1, 2)
    m = m[:int(TOTAL * SR)]
    t = np.arange(len(m)) / SR
    # bed level: present in the intro and the vote, well under the voice during the rounds
    lvl = np.full(len(m), -12.0)
    for a, b in (V1, V2):
        ramp_in = np.clip((t - (a - .35)) / .35, 0, 1); ramp_out = np.clip(((b - .1) - t) / .35, 0, 1)
        lvl = np.minimum(lvl, -12.0 - 12.0 * np.minimum(ramp_in, ramp_out))
    g = db(lvl); g *= np.clip((TOTAL - t) / 1.2, 0, 1)          # fade out at the end
    put(m * g[:, None], 0.0)
mix = mix[:int(TOTAL * SR)]
pk = np.abs(mix).max(); print("peak", round(float(pk), 3))
if pk > .89: mix *= .89 / pk
out = f"{C}/proj/assets/mix.wav"
w = wave.open(out, "w"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
st = subprocess.run(["ffmpeg", "-hide_banner", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print(st[st.rindex("Summary"):].split("\n")[2:4])

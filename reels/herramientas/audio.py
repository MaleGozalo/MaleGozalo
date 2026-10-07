import json, subprocess, wave, numpy as np, os, sys
import edl
N = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
W = json.load(open(f"{N}/work/words_out.json"))
def write(path, x):
    x = np.clip(x, -1, 1); w = wave.open(path, "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
rng = np.random.default_rng(7)
def pop(level_db=-27):
    n = int(.09 * SR); t = np.arange(n) / SR
    f = 320 + 700 * np.exp(-t / .018); ph = 2 * np.pi * np.cumsum(f) / SR
    env = (1 - np.exp(-t / .002)) * np.exp(-t / .028)
    return np.sin(ph) * env * 10 ** (level_db / 20)
def whoosh(dur=.45, level_db=-30, peak=.6):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    # sweep a simple one-pole low-pass cutoff up then down for the swoosh
    fc = 600 + 3800 * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    y = np.zeros(n); a_prev = 0.0
    for i in range(n):
        a = 1 - np.exp(-2 * np.pi * fc[i] / SR); a_prev = a_prev + a * (noise[i] - a_prev); y[i] = a_prev
    y -= np.convolve(y, np.ones(64) / 64, mode="same")      # take out rumble
    env = np.where(t < peak * dur, (t / (peak * dur)) ** 2, np.exp(-(t - peak * dur) / (.12 * dur)))
    y = y / (np.abs(y).max() + 1e-9) * env
    return y * 10 ** (level_db / 20)
T = {"cardIn": 3.20, "cardOut": 12.10, "tag": W[26]["s"], "phase2": W[31]["s"], "less": W[31]["s"] + .55,
     "ncW": W[43]["s"] - .06, "strike": W[44]["s"], "g1": W[52]["s"] - .06, "g2": W[56]["s"] - .04, "name": 19.66, "c3": W[72]["s"] - .04}
events = [("whoosh", T["cardIn"] - .12, dict(dur=.5, level_db=-29)), ("pop", T["tag"], {}), ("whoosh", T["phase2"] - .05, dict(dur=.35, level_db=-33)),
          ("pop", T["less"], {}), ("whoosh", T["cardOut"] - .1, dict(dur=.5, level_db=-30)), ("pop", T["ncW"], {}),
          ("whoosh", T["strike"] - .03, dict(dur=.22, level_db=-33, peak=.4)), ("whoosh", T["g1"] - .15, dict(dur=.55, level_db=-29)),
          ("whoosh", T["g2"] - .12, dict(dur=.4, level_db=-32)), ("pop", T["name"] + .05, {}), ("pop", T["c3"], {})]
total = sum(b - a for a, b in edl.SEGS) / edl.FPS
sfx = np.zeros(int((total + 1) * SR))
for kind, t0, kw in events:
    x = pop(**kw) if kind == "pop" else whoosh(**kw)
    i = int(max(0, t0) * SR); sfx[i:i + len(x)] += x[:len(sfx) - i]
write(f"{N}/work/r/sfx.wav", sfx)
# voice clean-up on the full-length take (time-aligned with the source):
# undo the pre-encode clipping at ~1.40, tame the boomy low-mids of a mic held at the mouth, add presence, soften the s's
clean = f"{N}/work/r/voice_clean.wav"; declip = f"{N}/work/r/voice_declip.wav"
# pass 0: decode to mono 48 kHz float so the clip level is the one measured (~1.40 -> 0.955 after the gain below)
mono = f"{N}/work/r/voice_mono.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{N}/src/video.MOV", "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_f32le", mono], check=True)
# pass 1: declip (filters placed after adeclip in the same graph get skipped, so it runs alone)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mono, "-af",
                "volume=0.6944,aeval=exprs='clip(val(0)\\,-0.955\\,0.955)',adeclip=window=55:overlap=75:arorder=8:threshold=10:hsize=1000:method=s",
                "-c:a", "pcm_f32le", declip], check=True)
# pass 2: EQ, gentle de-esser, light denoise
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", declip, "-af",
                "highpass=f=85,highpass=f=85,equalizer=f=250:t=q:w=1.0:g=-3,equalizer=f=3500:t=q:w=0.9:g=4,highshelf=f=8000:g=2.5,"
                "deesser=i=0.12:m=0.4,afftdn=nr=5:nf=-50", "-c:a", "pcm_f32le", clean], check=True)
# voice: cut the kept segments with 8 ms fades, concat, compress
parts, labels = [], []
for j, (a, b) in enumerate(edl.SEGS):
    parts.append(f"[0:a]atrim=start={a/edl.FPS:.5f}:end={b/edl.FPS:.5f},asetpts=PTS-STARTPTS,aresample={SR},afade=t=in:d=0.008,afade=t=out:st={(b-a)/edl.FPS-0.008:.5f}:d=0.008[s{j}]")
    labels.append(f"[s{j}]")
fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1,acompressor=threshold=-21dB:ratio=3:attack=6:release=120:knee=4[v]"
pre = f"{N}/work/r/voice_pre.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", clean, "-filter_complex", fc, "-map", "[v]", "-ac", "1", "-c:a", "pcm_f32le", pre], check=True)
# two-pass loudnorm to -14 LUFS / -1 dBTP
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", pre, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
js = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
      f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-i", f"{N}/work/r/sfx.wav", "-filter_complex",
                f"[0:a]{ln},aresample={SR}[v];[v][1:a]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89:level=false,aresample={SR}[o]",
                "-map", "[o]", "-ac", "2", "-c:a", "pcm_s16le", f"{N}/work/r/audio_final.wav"], check=True)
st = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{N}/work/r/audio_final.wav", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print(st[st.rindex("Summary"):])

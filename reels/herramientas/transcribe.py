import json, sys, time
from faster_whisper import WhisperModel
t0 = time.time()
m = WhisperModel(sys.argv[1], device="cpu", compute_type="int8", cpu_threads=4)
print("loaded", round(time.time()-t0, 1), flush=True)
import wave, numpy as np
wf = wave.open(sys.argv[2]); audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
segs, info = m.transcribe(audio, language="es", word_timestamps=True, beam_size=5, vad_filter=False,
    initial_prompt="Male Gozalo, marketing, emprendedoras, marca personal, contenido, Instagram, reels, publicá con sentido.")
out = []
for s in segs:
    out.append({"start": s.start, "end": s.end, "text": s.text, "words": [{"w": w.word, "s": w.start, "e": w.end, "p": w.probability} for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}", flush=True)
json.dump(out, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
print("done", round(time.time()-t0, 1))

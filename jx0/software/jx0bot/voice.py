"""JX0 ears and mouth: offline speech recognition (Vosk) and offline speech (Piper, eSpeak-NG fallback).

Everything here runs on the Raspberry Pi without internet; only the brain (brain.py) needs the network.
- Listener: 16 kHz mono from the default input device (USB mic or I2S INMP441), Vosk small English model,
  end of utterance detected by Vosk. Two ways to start listening: a push-to-talk button (GPIO, default pin 17)
  or a wake phrase ("hey robot") in the transcript.
- Speaker: Piper neural TTS (Python API, 22.05 kHz) with eSpeak-NG as a fallback, played through the default
  output device (USB speaker or I2S MAX98357A). While audio plays, `on_level(0..1)` reports loudness so the face
  can move its mouth.
Setup on the Pi (see jx0/docs/software_setup.md): pip install vosk sounddevice piper-tts numpy; apt install
espeak-ng libportaudio2; download a Vosk model (vosk-model-small-en-us-0.15) and a Piper voice (en_US-lessac-medium).
"""
from __future__ import annotations

import json
import queue
import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable

import numpy as np

MODELS = Path(__file__).resolve().parent / "models"
WAKE_PHRASES = ("hey robot", "hi robot", "hello robot", "hey jay")


class Listener:
    def __init__(self, model_dir: Path = MODELS / "vosk-model-small-en-us-0.15", rate: int = 16000, device=None):
        from vosk import KaldiRecognizer, Model, SetLogLevel
        SetLogLevel(-1)
        self.rate, self.device = rate, device
        self.model = Model(str(model_dir))
        self.KaldiRecognizer = KaldiRecognizer

    def listen(self, timeout_s: float = 8.0, on_partial: Callable[[str], None] | None = None) -> str:
        """Record one utterance and return its transcript ('' on silence/timeout)."""
        import sounddevice as sd
        rec = self.KaldiRecognizer(self.model, self.rate)
        q: queue.Queue = queue.Queue()

        def cb(indata, frames, t, status):
            q.put(bytes(indata))

        t0 = time.time()
        with sd.RawInputStream(samplerate=self.rate, blocksize=4000, dtype="int16", channels=1, callback=cb, device=self.device):
            while time.time() - t0 < timeout_s:
                try:
                    data = q.get(timeout=0.5)
                except queue.Empty:
                    continue
                if rec.AcceptWaveform(data):
                    return json.loads(rec.Result()).get("text", "")
                if on_partial:
                    partial = json.loads(rec.PartialResult()).get("partial", "")
                    if partial:
                        on_partial(partial)
        return json.loads(rec.FinalResult()).get("text", "")

    def wait_for_wake(self, button=None) -> str:
        """Block until the button is pressed (then listen) or a wake phrase is heard.
        Returns any words said after the wake phrase in the same utterance ('' if none)."""
        while True:
            if button is not None and button.is_pressed:
                return ""
            text = self.listen(timeout_s=4.0)
            for w in WAKE_PHRASES:
                if w in text:
                    return text.split(w, 1)[1].strip()


class Speaker:
    """Say text out loud; reports mouth loudness through on_level while playing."""

    def __init__(self, voice_path: Path = MODELS / "en_US-lessac-medium.onnx", on_level: Callable[[float], None] | None = None,
                 device=None):
        self.on_level = on_level or (lambda v: None)
        self.device = device
        self.voice = None
        if voice_path.exists():
            try:
                from piper import PiperVoice
                self.voice = PiperVoice.load(str(voice_path))
            except Exception as exc:          # missing package or incompatible voice: fall back to eSpeak
                print(f"[voice] Piper unavailable ({exc}); using eSpeak-NG")
        if self.voice is None and not shutil.which("espeak-ng"):
            print("[voice] no TTS engine found: install piper-tts (and a voice) or espeak-ng")

    def _piper_audio(self, text: str):
        """(int16 samples, sample rate) from Piper; handles the two Piper Python APIs."""
        v = self.voice
        if hasattr(v, "synthesize_stream_raw"):                     # piper-tts 1.2
            pcm = b"".join(v.synthesize_stream_raw(text))
            return np.frombuffer(pcm, dtype=np.int16), v.config.sample_rate
        chunks = list(v.synthesize(text))                            # piper-tts >= 1.3: AudioChunk objects
        pcm = b"".join(c.audio_int16_bytes for c in chunks)
        rate = chunks[0].sample_rate if chunks else 22050
        return np.frombuffer(pcm, dtype=np.int16), rate

    def _espeak_audio(self, text: str):
        wav = subprocess.run(["espeak-ng", "-v", "en-us", "-s", "165", "--stdout", text], capture_output=True, check=True).stdout
        # 44-byte RIFF header, 22.05 kHz mono int16
        return np.frombuffer(wav[44:], dtype=np.int16), 22050

    def say(self, text: str) -> None:
        if not text:
            return
        try:
            audio, rate = self._piper_audio(text) if self.voice is not None else self._espeak_audio(text)
        except Exception as exc:
            print(f"[voice] TTS failed: {exc}")
            return
        import sounddevice as sd
        block = rate // 25                                            # 40 ms blocks drive the mouth at 25 fps
        levels = [float(np.sqrt(np.mean((audio[i:i + block].astype(np.float32) / 32768.0) ** 2)))
                  for i in range(0, len(audio), block)]
        peak = max(levels) if levels else 1.0
        sd.play(audio, rate, device=self.device)
        t0 = time.time()
        for k, lv in enumerate(levels):
            self.on_level(min(1.0, lv / (peak + 1e-6)))
            delay = t0 + (k + 1) * block / rate - time.time()
            if delay > 0:
                time.sleep(delay)
        sd.wait()
        self.on_level(0.0)

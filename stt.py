"""Speech-to-text using faster-whisper.

Records audio from the default microphone until it detects silence,
then transcribes it. Kept separate from the rest of the pipeline so
the model backend (Whisper here) can be swapped without touching
anything else.
"""

import queue
import sys

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from config import CONFIG


class SpeechToText:
    def __init__(self):
        self._model = WhisperModel(
            CONFIG.whisper_model_size,
            device=CONFIG.whisper_device,
            compute_type="int8",
        )

    def listen(self) -> str:
        """Blocks until the user finishes speaking, returns the transcript."""
        audio = self._record_until_silence()
        segments, _ = self._model.transcribe(audio, language="en")
        return " ".join(segment.text.strip() for segment in segments).strip()

    def _record_until_silence(self) -> np.ndarray:
        q: queue.Queue = queue.Queue()
        silence_blocks_needed = int(
            CONFIG.silence_threshold_seconds * CONFIG.sample_rate / 1024
        )
        silence_streak = 0
        chunks: list[np.ndarray] = []

        def callback(indata, frames, time_info, status):
            if status:
                print(status, file=sys.stderr)
            q.put(indata.copy())

        with sd.InputStream(
            samplerate=CONFIG.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=1024,
            callback=callback,
        ):
            while True:
                block = q.get()
                chunks.append(block)
                volume = np.abs(block).mean()
                if volume < 0.01:
                    silence_streak += 1
                else:
                    silence_streak = 0
                if silence_streak >= silence_blocks_needed and len(chunks) > 10:
                    break

        audio = np.concatenate(chunks, axis=0).flatten()
        return audio

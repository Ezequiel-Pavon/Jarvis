"""Text-to-speech using pyttsx3.

pyttsx3 runs fully offline and requires no API key, which keeps the
assistant usable without network access and avoids sending anything
you say to a third party. Swap this module for Coqui TTS or
ElevenLabs if you want a more natural voice at the cost of either
GPU usage or an external API call.
"""

import pyttsx3

from config import CONFIG


class TextToSpeech:
    def __init__(self):
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", CONFIG.tts_rate)
        voices = self._engine.getProperty("voices")
        if voices:
            index = min(CONFIG.tts_voice_index, len(voices) - 1)
            self._engine.setProperty("voice", voices[index].id)

    def say(self, text: str) -> None:
        self._engine.say(text)
        self._engine.runAndWait()

"""Central configuration for the assistant.

All tunable values live here so the rest of the codebase does not
contain hardcoded model names, paths, or thresholds.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    # Speech-to-text
    whisper_model_size: str = "base"  # tiny, base, small, medium, large
    whisper_device: str = "cpu"  # "cuda" if a GPU is available

    # Language model
    ollama_model: str = "llama3"
    ollama_host: str = "http://localhost:11434"

    # Text-to-speech
    tts_rate: int = 175  # words per minute
    tts_voice_index: int = 0  # index into the OS voice list

    # Wake word
    wake_word: str = "jarvis"

    # Storage
    data_dir: Path = Path.home() / ".jarvis-assistant"
    memory_db: Path = data_dir / "memory.sqlite3"

    # Audio capture
    sample_rate: int = 16000
    silence_threshold_seconds: float = 1.2


CONFIG = Config()
CONFIG.data_dir.mkdir(parents=True, exist_ok=True)

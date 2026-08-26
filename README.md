# jarvis-assistant

A local, voice-controlled assistant. It listens for speech, sends the
transcript to a locally-hosted LLM, executes tool calls when the
model requests real-world actions, and speaks the result back.

Everything runs on the host machine by default: speech-to-text
(Whisper), the language model (Llama 3 via Ollama), and text-to-speech
(pyttsx3). No API keys or external services are required for the
base setup.

## How it works

```
microphone -> Whisper (STT) -> Ollama (LLM) -> tool execution (if requested) -> pyttsx3 (TTS) -> speaker
```

The model is given a fixed set of tools (see `src/tools.py`) and
decides on its own whether a request needs one of them or can be
answered directly. Conversation history is stored in a local SQLite
database so the assistant has short-term memory across turns.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally with a pulled model
  (`ollama pull llama3`)
- A working microphone and speakers

## Setup

```bash
git clone https://github.com/Ezequiel-Pavon/jarvis-assistant.git
cd jarvis-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start Ollama in a separate terminal if it is not already running:

```bash
ollama serve
```

## Usage

Voice mode:

```bash
python src/main.py
```

Text mode, for testing without a microphone:

```bash
python src/main.py --text
```

## Available tools

| Tool | Description |
|---|---|
| `get_time` | Returns the current local time |
| `open_application` | Opens a desktop application by name |
| `search_web` | Opens a web search in the default browser |
| `run_shell_command` | Runs a whitelisted, read-only shell command |

New tools are added by writing a function in `src/tools.py` and
registering it in `TOOL_REGISTRY` and `TOOL_SCHEMAS`. No other file
needs to change.

## Configuration

All tunable values (model names, audio sample rate, silence
threshold, storage paths) are in `src/config.py`.

## Project structure

```
src/
  main.py     entry point, wires the pipeline together
  stt.py      speech-to-text (faster-whisper)
  llm.py      LLM client and tool-calling loop (Ollama)
  tts.py      text-to-speech (pyttsx3)
  tools.py    tool definitions and schemas
  memory.py   SQLite-backed conversation history
  config.py   central configuration
```

## Design notes

- **Local-first**: STT, LLM, and TTS all run on-device by default,
  so audio and transcripts never leave the machine. Swapping in a
  hosted TTS (e.g. ElevenLabs) or a hosted LLM is a one-file change
  in `tts.py` or `llm.py` respectively.
- **Whitelisted shell access**: `run_shell_command` only executes a
  fixed set of read-only commands. This is deliberate — a voice
  assistant with unrestricted shell access is a real security risk,
  not just a theoretical one.
- **Tool calling is explicit**: tool schemas are plain dictionaries
  next to the functions they describe, so it is obvious what the
  model can and cannot do without tracing through a framework.

## Limitations

- Wake-word detection is not implemented; the current version
  listens continuously in voice mode.
- Tested against Llama 3 through Ollama; other models with
  OpenAI-compatible tool calling should work but are unverified.
- `faster-whisper` on CPU is noticeably slower than real time on
  longer utterances; a GPU is recommended for anything beyond short
  commands.

## License

MIT

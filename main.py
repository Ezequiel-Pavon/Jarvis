"""Entry point: wires speech-to-text, the LLM, tools, memory, and
text-to-speech into a loop.

Usage:
    python src/main.py            # voice mode
    python src/main.py --text     # type instead of speak, useful for testing
"""

import argparse
import sys

from llm import LanguageModel
from memory import Memory


def run_text_mode() -> None:
    memory = Memory()
    model = LanguageModel()
    print("Text mode. Type 'quit' to exit.")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue

        reply = model.respond(memory.recent(), user_input)
        memory.add("user", user_input)
        memory.add("assistant", reply)
        print(reply)


def run_voice_mode() -> None:
    # Imported lazily: these pull in audio libraries that are not
    # needed for text mode and may not be installed in every environment.
    from stt import SpeechToText
    from tts import TextToSpeech

    memory = Memory()
    model = LanguageModel()
    listener = SpeechToText()
    speaker = TextToSpeech()

    print("Voice mode. Say something, or press Ctrl+C to exit.")
    while True:
        try:
            transcript = listener.listen()
        except KeyboardInterrupt:
            break
        if not transcript:
            continue

        print(f"You said: {transcript}")
        reply = model.respond(memory.recent(), transcript)
        memory.add("user", transcript)
        memory.add("assistant", reply)
        print(f"Assistant: {reply}")
        speaker.say(reply)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local voice assistant")
    parser.add_argument(
        "--text", action="store_true", help="run in text mode instead of voice"
    )
    args = parser.parse_args()

    try:
        if args.text:
            run_text_mode()
        else:
            run_voice_mode()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()

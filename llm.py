"""LLM client and tool-calling loop, backed by a local Ollama server.

Ollama's /api/chat endpoint accepts the same tool-calling shape as
the OpenAI API, so `tools.TOOL_SCHEMAS` can be passed straight
through. If the model decides to call a tool, we execute it locally,
feed the result back, and ask the model to produce a final reply.
"""

import json

import requests

from config import CONFIG
from tools import TOOL_REGISTRY, TOOL_SCHEMAS

SYSTEM_PROMPT = (
    "You are a concise voice assistant running on the user's own machine. "
    "Keep replies short enough to be spoken aloud. Use the available "
    "tools when a request requires real-world action or current "
    "information; otherwise answer directly."
)


class LanguageModel:
    def __init__(self):
        self._url = f"{CONFIG.ollama_host}/api/chat"

    def respond(self, history: list[dict], user_message: str) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        reply = self._chat(messages)

        tool_calls = reply.get("tool_calls")
        if not tool_calls:
            return reply.get("content", "").strip()

        messages.append(reply)
        for call in tool_calls:
            result = self._execute_tool(call)
            messages.append(
                {
                    "role": "tool",
                    "content": result,
                }
            )

        final_reply = self._chat(messages)
        return final_reply.get("content", "").strip()

    def _chat(self, messages: list[dict]) -> dict:
        response = requests.post(
            self._url,
            json={
                "model": CONFIG.ollama_model,
                "messages": messages,
                "tools": TOOL_SCHEMAS,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["message"]

    @staticmethod
    def _execute_tool(call: dict) -> str:
        name = call["function"]["name"]
        raw_args = call["function"].get("arguments", {})
        args = raw_args if isinstance(raw_args, dict) else json.loads(raw_args)

        func = TOOL_REGISTRY.get(name)
        if func is None:
            return f"Unknown tool: {name}"

        try:
            return str(func(**args))
        except Exception as exc:  # noqa: BLE001 - surface any tool failure to the model
            return f"Tool '{name}' failed: {exc}"

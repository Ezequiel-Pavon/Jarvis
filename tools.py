"""Tools the assistant can call.

Each tool is a plain Python function with a docstring and type hints.
`TOOL_SCHEMAS` is generated from that metadata and sent to the model
so it knows what is available and how to call it. Add a new
capability by writing a function here and registering it in
`TOOL_REGISTRY` -- nothing elsewhere needs to change.
"""

import datetime
import subprocess
import webbrowser


def get_time() -> str:
    """Return the current local time."""
    return datetime.datetime.now().strftime("%H:%M")


def open_application(name: str) -> str:
    """Open a desktop application by name.

    Args:
        name: the executable or application name, e.g. "firefox".
    """
    try:
        subprocess.Popen([name])
        return f"Opened {name}."
    except FileNotFoundError:
        return f"Could not find an application called '{name}'."


def search_web(query: str) -> str:
    """Open a web search for the given query in the default browser.

    Args:
        query: what to search for.
    """
    url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching the web for '{query}'."


def run_shell_command(command: str) -> str:
    """Run a whitelisted, read-only shell command and return its output.

    Args:
        command: the command to run. Only commands in ALLOWED_COMMANDS
            are permitted; anything else is rejected.
    """
    ALLOWED_COMMANDS = {"date", "uptime", "df -h", "whoami", "uname -a"}
    if command not in ALLOWED_COMMANDS:
        return f"Command '{command}' is not in the allowed list and was not run."
    result = subprocess.run(command.split(), capture_output=True, text=True)
    return result.stdout.strip() or result.stderr.strip()


TOOL_REGISTRY = {
    "get_time": get_time,
    "open_application": open_application,
    "search_web": search_web,
    "run_shell_command": run_shell_command,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Return the current local time.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open a desktop application by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Application name, e.g. firefox"}
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Open a web search for the given query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Run a whitelisted, read-only shell command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "One of: date, uptime, df -h, whoami, uname -a"}
                },
                "required": ["command"],
            },
        },
    },
]

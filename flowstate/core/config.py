import os
import datetime
from pathlib import Path

def get_config_dir() -> Path:
    """Get the flowstate global configuration directory."""
    home = Path.home()
    config_dir = home / ".flowstate"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def log_event(message: str):
    """Log a system event to the global flowstate log file and print to console."""
    log_file = get_config_dir() / "flowstate.log"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    print(message)  # Still print to console for CLI users
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    except Exception:
        pass

DEFAULT_STYLE_PROMPT = """
You are an expert pair programmer.
When generating code, adhere to the following style:
- Write clean, modular, and well-documented Python.
- Provide type hints for all function signatures.
- Avoid excessive, redundant comments. Only comment "why", not "what".
- If making a large change, outline the plan first.
"""

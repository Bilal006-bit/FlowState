import os
from pathlib import Path

def get_config_dir() -> Path:
    """Get the flowstate global configuration directory."""
    home = Path.home()
    config_dir = home / ".flowstate"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir



DEFAULT_STYLE_PROMPT = """
You are an expert pair programmer.
When generating code, adhere to the following style:
- Write clean, modular, and well-documented Python.
- Provide type hints for all function signatures.
- Avoid excessive, redundant comments. Only comment "why", not "what".
- If making a large change, outline the plan first.
"""

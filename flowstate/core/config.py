import os
from pathlib import Path

def get_config_dir() -> Path:
    """Get the flowstate global configuration directory."""
    home = Path.home()
    config_dir = home / ".flowstate"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_project_dir() -> Path:
    """Get the current project's flowstate local directory."""
    cwd = Path.cwd()
    project_dir = cwd / ".flowstate"
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir

DEFAULT_STYLE_PROMPT = """
You are an expert pair programmer.
When generating code, adhere to the following style:
- Write clean, modular, and well-documented Python.
- Provide type hints for all function signatures.
- Avoid excessive, redundant comments. Only comment "why", not "what".
- If making a large change, outline the plan first.
"""

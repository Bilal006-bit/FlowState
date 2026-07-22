import os
from pathlib import Path

def pack_codebase(directory: str = ".") -> str:
    """
    Recursively scans the directory, ignoring common build and git folders,
    and packs the contents into a single string optimized for LLM context.
    """
    target_dir = Path(directory)
    
    ignore_dirs = {'.git', '.flowstate', 'node_modules', 'venv', '.venv', '__pycache__', 'dist', 'build'}
    valid_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md', '.html', '.css'}
    
    packed_output = ["# Codebase Export\n"]
    
    for filepath in target_dir.rglob("*"):
        if filepath.is_dir():
            continue
            
        # Check if it should be ignored
        if any(part in ignore_dirs for part in filepath.parts):
            continue
            
        if filepath.suffix not in valid_extensions:
            continue
            
        try:
            content = filepath.read_text(encoding='utf-8')
            if not content.strip():
                continue
                
            relative_path = filepath.relative_to(target_dir)
            packed_output.append(f"## File: {relative_path}")
            packed_output.append("```" + filepath.suffix.lstrip('.') + "\n" + content + "\n```\n")
        except Exception:
            pass # Skip binary or unreadable files
            
    return "\n".join(packed_output)

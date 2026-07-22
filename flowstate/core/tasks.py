import re
from pathlib import Path

def extract_todos(directory: str = ".") -> list[dict]:
    """
    Scans the codebase for TODO: and FIXME: comments and returns a list of dictionaries.
    Each dict contains {'type': 'TODO', 'text': 'fix this bug', 'file': 'main.py', 'line': 42}
    """
    target_dir = Path(directory)
    
    ignore_dirs = {'.git', '.flowstate', 'node_modules', 'venv', '.venv', '__pycache__'}
    valid_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.md'}
    
    todo_pattern = re.compile(r'(TODO|FIXME)[:\- ]+(.*)', re.IGNORECASE)
    
    tasks = []
    
    for filepath in target_dir.rglob("*"):
        if filepath.is_dir():
            continue
            
        if any(part in ignore_dirs for part in filepath.parts):
            continue
            
        if filepath.suffix not in valid_extensions:
            continue
            
        try:
            lines = filepath.read_text(encoding='utf-8').split('\n')
            for idx, line in enumerate(lines):
                match = todo_pattern.search(line)
                if match:
                    task_type = match.group(1).upper()
                    task_text = match.group(2).strip()
                    if task_text:
                        tasks.append({
                            'type': task_type,
                            'text': task_text,
                            'file': str(filepath.relative_to(target_dir)),
                            'line': idx + 1
                        })
        except Exception:
            pass
            
    return tasks

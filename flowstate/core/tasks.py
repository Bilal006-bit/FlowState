import re
import json
from pathlib import Path
from .config import get_config_dir

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
            
    # Append FlowState Advisory Recommendations
    advisories = get_recommendations()
    tasks.extend(advisories)
            
    return tasks

def get_recommendations_file() -> Path:
    return get_config_dir() / "recommendations.json"

def add_recommendations(filepath: str, recs: list[str]):
    rec_file = get_recommendations_file()
    data = {}
    if rec_file.exists():
        try:
            data = json.loads(rec_file.read_text(encoding='utf-8'))
        except Exception:
            pass
            
    if not recs and filepath in data:
        del data[filepath]
    elif recs:
        data[filepath] = recs
    
    with open(rec_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_recommendations() -> list[dict]:
    rec_file = get_recommendations_file()
    tasks = []
    if rec_file.exists():
        try:
            data = json.loads(rec_file.read_text(encoding='utf-8'))
            for fp, recs in data.items():
                for r in recs:
                    tasks.append({
                        'type': 'ADVISORY',
                        'text': r,
                        'file': Path(fp).name,
                        'line': '?'
                    })
        except Exception:
            pass
    return tasks

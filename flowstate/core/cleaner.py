import ast
import re
from pathlib import Path

def clean_python_comments(source_code: str) -> str:
    """
    Intelligently remove excessive docstrings or multiline AI comments in Python using AST,
    while attempting to keep the original formatting for code lines.
    """
    # For a robust non-destructive AST cleanup, we can use a simple regex approach 
    # tuned for Python to remove block comments that are very long, 
    # or just rely on a basic heuristic for V1.
    
    # Heuristic: Remove all multiline strings that are not assigned to variables 
    # (these are docstrings).
    try:
        parsed = ast.parse(source_code)
    except SyntaxError:
        return source_code  # Fallback if there's a syntax error
    
    # We will just use regex to strip out excessive # comments that span more than 3 lines. ... [Flowstate: AI comments truncated]
    
    lines = source_code.split('\n')
    cleaned_lines = []
    comment_block = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            comment_block.append(line)
        else:
            if comment_block:
                # If comment block is huge (e.g., AI fluff), keep only the first line
                if len(comment_block) > 3:
                    cleaned_lines.append(comment_block[0] + " ... [Flowstate: AI comments truncated]")
                else:
                    cleaned_lines.extend(comment_block)
                comment_block = []
            cleaned_lines.append(line)
            
    # Flush remaining
    if comment_block:
        if len(comment_block) > 3:
            cleaned_lines.append(comment_block[0] + " ... [Flowstate: AI comments truncated]")
        else:
            cleaned_lines.extend(comment_block)

    return "\n".join(cleaned_lines)

def clean_file(filepath: Path) -> tuple[bool, int]:
    """Read a file, clean comments based on extension, and overwrite. Returns (changed, lines_removed)."""
    if not filepath.exists() or not filepath.is_file():
        return False, 0
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if filepath.suffix == '.py':
        cleaned = clean_python_comments(content)
    else:
        # Generic Regex fallback for other languages (C-style block comments)
        # Removes /* ... */ if it contains many lines
        pattern = re.compile(r'/\*.*?\*/', re.DOTALL)
        def repl(match):
            text = match.group(0)
            if text.count('\n') > 3:
                return "/* [Flowstate: AI comments truncated] */"
            return text
        cleaned = pattern.sub(repl, content)
        
    if cleaned != content:
        lines_removed = len(content.split('\n')) - len(cleaned.split('\n'))
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        return True, max(0, lines_removed)
    return False, 0

def analyze_file(filepath: Path) -> list[str]:
    """Non-destructively analyze a file and return a list of recommendations."""
    recommendations = []
    if not filepath.exists() or not filepath.is_file():
        return recommendations
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. Check for AI fluff
        if filepath.suffix == '.py':
            cleaned = clean_python_comments(content)
        else:
            pattern = re.compile(r'/\*.*?\*/', re.DOTALL)
            def repl(match):
                text = match.group(0)
                if text.count('\n') > 3:
                    return "/* [Flowstate: AI comments truncated] */"
                return text
            cleaned = pattern.sub(repl, content)
            
        if cleaned != content:
            lines_removed = len(content.split('\n')) - len(cleaned.split('\n'))
            recommendations.append(f"AI Fluff Detected: {lines_removed} lines of redundant comments found. Ask Project Chat to clean it.")
            
        # 2. Check for Ravioli code (Redundant/Duplicate functions) - heuristic
        if filepath.suffix == '.py':
            funcs = re.findall(r'^def (\w+)\(', content, re.MULTILINE)
            duplicates = set([f for f in funcs if funcs.count(f) > 1])
            if duplicates:
                for d in duplicates:
                    recommendations.append(f"Ravioli Code Warning: The function '{d}' appears to be duplicated.")
                    
    except Exception:
        pass
        
    return recommendations

import os
import json
import requests
import subprocess
from urllib.parse import urlparse
from pathlib import Path

from .memory import MemoryManager

def call_llm_api(provider: str, api_key: str, prompt: str) -> str:
    """Lightweight pure-requests wrapper to avoid heavy C/Rust dependencies."""
    provider = provider.lower()
    
    if provider == "openai":
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
        
    elif provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        return res.json()["content"][0]["text"]
        
    elif provider == "gemini":
        clean_key = api_key.strip()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={clean_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts":[{"text": prompt}]}]
        }
        res = requests.post(url, headers=headers, json=data)
        
        # Smart Fallback for Internal/Experimental Keys that lack public models
        if res.status_code == 404:
            try:
                models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={clean_key}"
                models_res = requests.get(models_url).json()
                for m in models_res.get("models", []):
                    if "generateContent" in m.get("supportedGenerationMethods", []):
                        fallback_model = m["name"]
                        fallback_url = f"https://generativelanguage.googleapis.com/v1beta/{fallback_model}:generateContent?key={clean_key}"
                        res = requests.post(fallback_url, headers=headers, json=data)
                        if res.status_code == 200:
                            break
            except Exception:
                pass

        if res.status_code != 200:
            raise Exception(f"{res.status_code} Client Error: {res.text}")
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        
    elif provider == "ollama":
        model_name = api_key.strip() or "llama3"
        url = "http://localhost:11434/api/generate"
        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        res = requests.post(url, json=data)
        res.raise_for_status()
        return res.json().get("response", "")
        
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def auto_detect_tech_stack(directory: Path) -> str:
    """Heuristically detects the tech stack based on project files."""
    stack = set()
    
    # Check Node.js
    pkg_json = directory / "package.json"
    if pkg_json.exists():
        stack.add("Node.js")
        try:
            content = pkg_json.read_text(encoding="utf-8").lower()
            if '"react"' in content: stack.add("React")
            if '"next"' in content: stack.add("Next.js")
            if '"vue"' in content: stack.add("Vue")
            if '"express"' in content: stack.add("Express")
            if '"typescript"' in content: stack.add("TypeScript")
            if '"tailwindcss"' in content: stack.add("TailwindCSS")
        except Exception:
            pass
            
    # Check Python
    if (directory / "requirements.txt").exists() or (directory / "pyproject.toml").exists():
        stack.add("Python")
    elif list(directory.glob("*.py")):
        stack.add("Python")
        
    # Check Go
    if (directory / "go.mod").exists() or list(directory.glob("*.go")):
        stack.add("Go")
        
    # Check Rust
    if (directory / "Cargo.toml").exists():
        stack.add("Rust")
        
    # Check Java
    if (directory / "pom.xml").exists() or (directory / "build.gradle").exists():
        stack.add("Java")
        
    return ", ".join(sorted(stack))


def extract_project_knowledge(directory: str = "."):
    """
    Scans the project directory, summarizes the architecture and purpose of key files
    using the configured LLM API, and embeds that knowledge into the local ChromaDB.
    """
    memory = MemoryManager()
    profile = memory.get_profile()
    
    if not profile.api_key:
        print("No API Key configured. Skipping memory enrichment.")
        return False
        
    target_dir = Path(directory)
    if directory.startswith("http://") or directory.startswith("https://"):
        path = urlparse(directory).path
        repo_name = path.strip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
            
        target_dir = Path.cwd() / ".flowstate" / "external_repos" / repo_name
        
        if not target_dir.exists():
            print(f"Cloning external repository {repo_name}...")
            target_dir.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(["git", "clone", directory, str(target_dir)], check=True)
            except Exception as e:
                print(f"Failed to clone repository: {e}")
                return False
        else:
            print(f"External repository {repo_name} already cloned. Pulling latest...")
            try:
                subprocess.run(["git", "-C", str(target_dir), "pull"], check=True)
            except Exception as e:
                print(f"Failed to pull latest repository changes: {e}")

    # Adaptive Tech Stack Detection
    if not profile.tech_stack or not profile.tech_stack.strip():
        detected_stack = auto_detect_tech_stack(target_dir)
        if detected_stack:
            profile.tech_stack = detected_stack
            memory.update_profile(tech_stack=detected_stack)
            print(f"Auto-detected Tech Stack: {detected_stack}")

    extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.md', '.json']
    
    print(f"Starting automated learning using {profile.api_provider}...")
    
    for filepath in target_dir.rglob("*"):
        if filepath.is_file() and filepath.suffix in extensions:
            # Ignore hidden directories like .git or .flowstate
            if any(part.startswith('.') for part in filepath.parts[:-1]):
                continue
            # Ignore common build and dependency directories
            ignore_dirs = {"node_modules", "dist", "build", "venv", "env", "__pycache__", ".git", ".flowstate"}
            if any(part in ignore_dirs for part in filepath.parts[:-1]):
                continue
                
            # Ignore lockfiles and binary-like json
            if filepath.name in {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Contents.json"}:
                continue
                
            try:
                content = filepath.read_text(encoding='utf-8')
                if len(content.strip()) == 0:
                    continue
                    
                doc_id = str(filepath.resolve())
                
                # Check if file is already in memory to save API calls / time
                existing = memory.collection.get(ids=[doc_id])
                if existing and existing.get('ids') and len(existing['ids']) > 0:
                    summary = existing['documents'][0]
                    new_meta = existing['metadatas'][0] if existing.get('metadatas') and existing['metadatas'] else {}
                    new_meta["filename"] = filepath.name
                    new_meta["type"] = "auto_summary"
                    new_meta["project_path"] = str(target_dir.resolve())
                    
                    memory.add_project_memory(
                        doc_id=doc_id,
                        content=summary,
                        metadata=new_meta
                    )
                    print(f"Skipped API (Already learned): {filepath.name}")
                    continue
                    
                prompt = f"Summarize the architectural purpose, tech stack usage, and key functions of this file ({filepath.name}) in 3-4 concise sentences:\n\n{content[:5000]}"
                
                summary = call_llm_api(profile.api_provider, profile.api_key, prompt)
                
                # Store in ChromaDB
                memory.add_project_memory(
                    doc_id=doc_id,
                    content=summary,
                    metadata={
                        "filename": filepath.name, 
                        "type": "auto_summary",
                        "project_path": str(target_dir.resolve())
                    }
                )
                print(f"Learned: {filepath.name}")
                
            except Exception as e:
                print(f"Failed to learn {filepath.name}: {e}")

    print("Memory Enrichment Complete!")
    return True

def extract_and_store_file(filepath: Path, target_dir: Path) -> bool:
    """Extract and store knowledge for a single file. (Used for Real-Time Silent Learning)"""
    from .memory import MemoryManager
    memory = MemoryManager()
    profile = memory.get_profile()
    if not profile.api_key:
        return False
        
    try:
        content = filepath.read_text(encoding='utf-8')
        if len(content.strip()) == 0:
            return False
            
        doc_id = str(filepath.resolve())
        prompt = f"Summarize the architectural purpose, tech stack usage, and key functions of this file ({filepath.name}) in 3-4 concise sentences:\n\n{content[:5000]}"
        
        summary = call_llm_api(profile.api_provider, profile.api_key, prompt)
        
        memory.add_project_memory(
            doc_id=doc_id,
            content=summary,
            metadata={
                "filename": filepath.name, 
                "type": "auto_summary",
                "project_path": str(target_dir.resolve())
            }
        )
        print(f"[Silent Watcher] Real-time memory updated for {filepath.name}")
        return True
    except Exception as e:
        print(f"Failed to learn {filepath.name}: {e}")
        return False

def generate_optimized_context() -> str:
    """Combines ChromaDB learnings and tech stack into a single prompt block."""
    memory = MemoryManager()
    profile = memory.get_profile()
    
    context = f"## User Context\nTech Stack: {profile.tech_stack}\n"
    if profile.style_prompt:
        context += f"Style Guidelines: {profile.style_prompt}\n"
        
    # Query top architectural nodes
    results = memory.query_project_memory("Architecture and core logic", n_results=5)
    if results:
        context += "\n## Project Memory (Flowstate)\n"
            
    return context

def generate_smart_changelog(diff_text: str) -> str:
    """Uses the configured API to summarize a git diff into a professional changelog."""
    memory = MemoryManager()
    profile = memory.get_profile()
    
    if not profile.api_key:
        return "No API key configured for smart changelogs. Please add one in Settings."
        
    prompt = (
        "You are an expert engineer writing a pull request changelog.\n"
        "Summarize the following git diff into a professional markdown changelog with bullet points.\n"
        "Focus on the 'why' and group by feature/bugfix if possible.\n\n"
        f"Diff:\n{diff_text[:10000]}"
    )
    
    try:
        changelog = call_llm_api(profile.api_provider, profile.api_key, prompt)
        return changelog
    except Exception as e:
        return f"Failed to generate changelog: {e}"

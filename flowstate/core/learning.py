import os
import json
import requests
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
        
    else:
        raise ValueError(f"Unsupported provider: {provider}")


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
    extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.md', '.json']
    
    print(f"Starting automated learning using {profile.api_provider}...")
    
    for filepath in target_dir.rglob("*"):
        if filepath.is_file() and filepath.suffix in extensions:
            # Ignore hidden directories like .git or .flowstate
            if any(part.startswith('.') for part in filepath.parts[:-1]):
                continue
                
            try:
                content = filepath.read_text(encoding='utf-8')
                if len(content.strip()) == 0:
                    continue
                    
                prompt = f"Summarize the architectural purpose, tech stack usage, and key functions of this file ({filepath.name}) in 3-4 concise sentences:\n\n{content[:5000]}"
                
                summary = call_llm_api(profile.api_provider, profile.api_key, prompt)
                
                # Store in ChromaDB
                doc_id = str(filepath.resolve())
                memory.add_project_memory(
                    doc_id=doc_id,
                    content=summary,
                    metadata={"filename": filepath.name, "type": "auto_summary"}
                )
                print(f"Learned: {filepath.name}")
                
            except Exception as e:
                print(f"Failed to learn {filepath.name}: {e}")

    print("Memory Enrichment Complete!")
    return True

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

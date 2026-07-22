import re
from pathlib import Path
from .memory import MemoryManager
from .learning import call_llm_api

def ask_project_bot(query: str, history: list, project_path: str = None) -> tuple[str, list]:
    """
    Combines project context, relevant ChromaDB memories, and chat history 
    into a single prompt, then queries the configured LLM API.
    """
    memory = MemoryManager()
    profile = memory.get_profile()
    
    if not profile.api_key:
        return "⚠️ No API Key configured. Please add one in Settings to use the Chatbot.", []
        
    # 1. Fetch relevant memory chunks
    where_clause = {"project_path": project_path} if project_path and project_path != "All Projects" else None
    results = memory.query_project_memory_full(query, n_results=5, where=where_clause)
    
    docs = results.get('documents', [[]])[0]
    metas = results.get('metadatas', [[]])[0]
    ids = results.get('ids', [[]])[0]
    
    sources = []
    
    # 2. Build the system context
    context = (
        "You are FlowState, an expert AI developer.\n"
        "Your task is to answer the user's questions and write code based on the Project Context below.\n"
        "If you need to modify or create a file, you MUST output the completely updated code inside a special code block exactly like this:\n"
        "```file:/absolute/path/to/file.js\n"
        "// full updated code here\n"
        "```\n"
        f"The root directory of the active project is: {project_path or 'Unknown'}\n\n"
        "### Project Context\n"
        f"Tech Stack: {profile.tech_stack or 'Not specified'}\n"
        f"Style Guidelines: {profile.style_prompt or 'Not specified'}\n\n"
    )
    
    if docs:
        context += "### Relevant Codebase Files:\n"
        for i, meta in enumerate(metas):
            filename = meta.get('filename', f'File {i+1}')
            if meta and 'filename' in meta:
                sources.append(meta['filename'])
            summary = docs[i]
            
            # Extract raw code
            raw_code = ""
            if ids and i < len(ids):
                filepath = ids[i]
                if not filepath.endswith('lock.json') and not filepath.endswith('.lock') and not filepath.endswith('Contents.json'):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            raw_code = f.read()
                            if len(raw_code) > 2500:
                                raw_code = raw_code[:2500] + "\n... (truncated)"
                    except Exception:
                        raw_code = ""
            
            if raw_code:
                context += f"--- {filename} (Raw Code) (Path: {ids[i]}) ---\n{raw_code}\n\n"
            else:
                context += f"--- {filename} (Summary) (Path: {ids[i] if ids and i < len(ids) else 'Unknown'}) ---\n{summary}\n\n"
            
    # 3. Append Chat History
    if history:
        context += "### Conversation History:\n"
        for turn in history:
            role = turn.get("role", "User")
            msg = turn.get("message", "")
            context += f"[{role}]: {msg}\n"
            
    # 4. Append the new user query
    context += f"\n### New User Request:\n{query}\n\n"
    context += "Please provide an expert answer. If asked to modify a file, use the ```file:PATH format."

    # 5. Call the API
    try:
        response = call_llm_api(profile.api_provider, profile.api_key, context)
        
        # 6. Agentic Interceptor
        pattern = r'```file:(.*?)\n(.*?)```'
        matches = re.finditer(pattern, response, re.DOTALL)
        
        for match in matches:
            file_path = match.group(1).strip()
            new_content = match.group(2)
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                # Replace the massive codeblock in the UI with a success badge
                response = response.replace(match.group(0), f"\n✅ **Automatically updated file:** `{file_path}`\n")
            except Exception as e:
                response = response.replace(match.group(0), f"\n❌ **Failed to update file:** `{file_path}`\nError: {e}\n")
        
        return response, sources
    except Exception as e:
        return f"⚠️ API Error: {str(e)}", []

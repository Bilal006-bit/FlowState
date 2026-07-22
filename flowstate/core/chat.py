from .memory import MemoryManager
from .learning import call_llm_api

def ask_project_bot(query: str, history: list, project_path: str = None) -> str:
    """
    Combines project context, relevant ChromaDB memories, and chat history 
    into a single prompt, then queries the configured LLM API.
    """
    memory = MemoryManager()
    profile = memory.get_profile()
    
    if not profile.api_key:
        return "⚠️ No API Key configured. Please add one in Settings to use the Chatbot."
        
    # 1. Fetch relevant memory chunks
    where_clause = {"project_path": project_path} if project_path and project_path != "All Projects" else None
    results = memory.query_project_memory_full(query, n_results=5, where=where_clause)
    
    docs = results.get('documents', [[]])[0]
    metas = results.get('metadatas', [[]])[0]
    
    sources = []
    if metas:
        for m in metas:
            if m and 'filename' in m:
                sources.append(m['filename'])
                
    # 2. Build the system context
    context = (
        "You are FlowState, an expert AI developer assistant that deeply understands the user's specific project.\n"
        "You answer questions, write code, and propose features specifically tailored to the project architecture below.\n\n"
        "### Project Context\n"
        f"Tech Stack: {profile.tech_stack or 'Not specified'}\n"
        f"Style Guidelines: {profile.style_prompt or 'Not specified'}\n\n"
    )
    
    if docs:
        context += "### Relevant Codebase Memories:\n"
        for i, doc in enumerate(docs):
            context += f"--- Memory {i+1} ---\n{doc}\n\n"
            
    # 3. Append Chat History
    if history:
        context += "### Conversation History:\n"
        for turn in history:
            role = turn.get("role", "User")
            msg = turn.get("message", "")
            context += f"[{role}]: {msg}\n"
            
    # 4. Append the new user query
    context += f"\n### New User Question:\n{query}\n\n"
    context += "Please provide a concise, expert answer based on the context above."

    # 5. Call the API
    try:
        response = call_llm_api(profile.api_provider, profile.api_key, context)
        
        return response, sources
    except Exception as e:
        return f"⚠️ API Error: {str(e)}", []

# FlowState 🌊

FlowState is an **autonomous, privacy-first local AI agent** and developer workflow manager. Designed for engineers scaling their productivity, FlowState transforms your desktop into an intelligent pair programmer that actively cleans technical debt, writes code, and compresses codebase context to save massively on API tokens.

FlowState runs locally on your machine, giving it the authority to act as an actual "Junior Engineer" capable of editing your files autonomously without you ever copy-pasting code again.

---

## 🚀 Key Capabilities

### 🧠 Autonomous Agentic Editing
FlowState features an advanced, built-in Project Chatbot that serves as an autonomous agent. When you ask it to build a feature or fix a bug, it silently reads your raw files, generates the perfect code, and **physically writes/overwrites the files directly to your hard drive**. 

### 🛡️ Multi-AI Fallback Router
Experience the speed and privacy of local models with the raw intelligence of enterprise cloud models. FlowState includes an internal intelligent routing engine. If your primary local model (e.g., `ollama`) crashes, times out, or throws an AI refusal for complex tasks, FlowState silently and instantly reroutes the prompt to a Fallback Provider (e.g., `gemini`, `openai`, `anthropic`).

### 🔒 Enterprise `.env` Security Standard
The AI Agent is hardcoded with strict security constraints. It is forbidden from hardcoding API keys, passwords, or database URIs into your source code. When requested to add credentials, it automatically generates a secure `.env` file and correctly configures environment variables, enforcing professional Senior Developer standards.

### 🧹 The Auto-Cleaner Daemon (Anti-Hallucination)
AI tools love to write huge, unnecessary comments explaining every line of code. FlowState intercepts your saves in real-time. Whenever you hit `Ctrl+S`, the Watcher Daemon instantly strips out hallucinated AI fluff in milliseconds, keeping your git history and codebase perfectly clean.

### 📦 Auto-Context Optimizer (Token Saver)
Stop wasting money and context windows. FlowState maintains a local ChromaDB vector memory of your project's architecture. It auto-detects your tech stack (e.g., React, Python, Go) and silently recalculates the absolute smallest, perfectly optimized context block when asked a question, keeping API costs to an absolute minimum.

### 🌐 External Framework Ingestion
Using a complex external framework like FastAPI or TailwindCSS? Paste the public GitHub URL into FlowState's Knowledge Base. FlowState automatically clones the repository, scans its architecture, and permanently injects it into your local memory so your AI Assistant instantly becomes an expert on the framework.

### 📝 Smart Git Changelog
Stop writing PR descriptions manually. FlowState analyzes your `git diff` against the main branch and uses your configured LLM API to write a stunning, markdown-formatted changelog detailing the "why" and "how" of your code changes.

---

## 🛠️ Installation

Because FlowState is designed to be lightweight, it runs perfectly on Windows, Mac, and Linux without heavy C/Rust dependencies.

```bash
# Clone the repository
git clone https://github.com/Bilal006-bit/FlowState.git
cd FlowState

# Install globally in editable mode
pip install -e .
```

---

## 💻 Usage

You have two ways to use FlowState: the sleek Desktop UI or the lightning-fast CLI.

### The Desktop GUI
Run this command from anywhere in your terminal to open the FlowState Dashboard:
```bash
flowstate ui
```
*From the UI, you can manage your Settings, interact with the Autonomous Chatbot, run the Auto-Cleaner daemon, pack your codebase, and view your project's technical debt.*

### The CLI Commands
- `flowstate watch` - Starts the active background daemon to auto-clean files on save.
- `flowstate pack` - Packs your entire project into your clipboard.
- `flowstate todos` - Extracts and displays all TODOs in the terminal.
- `flowstate style` - Copies your custom AI coding style prompt to your clipboard.
- `flowstate clean <file>` - Manually strips AI fluff from a specific file.

---

## 🤝 Contributing & How Changes are Accepted

FlowState is completely open-source and we welcome contributions from the community! 
Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for full details on how to get your changes merged.

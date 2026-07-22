# FlowState 🌊

FlowState is a **local-first, privacy-focused open-source developer flow manager** designed specifically for engineers who heavily use AI coding tools (like Cursor, Claude Desktop, and ChatGPT). 

It acts as an active "Junior Engineer" running in the background, automatically cleaning up AI hallucinations, managing your technical debt, and compressing your codebase context to save you massive amounts of API tokens.

## 🚀 Features

### 🧹 The Auto-Cleaner (Anti-Hallucination)
AI tools love to write huge, unnecessary comments explaining every line of code. FlowState intercepts your saves in real-time. Whenever you hit `Ctrl+S`, FlowState instantly strips out the hallucinated AI fluff in milliseconds, keeping your git history and codebase perfectly clean.

### 🧠 Auto-Context Optimizer (Token Saver)
Stop wasting money and context windows by pasting unoptimized code. FlowState maintains a local ChromaDB vector memory of your project architecture. Every time you save, it silently recalculates the absolute smallest, perfectly optimized context block and can copy it to your clipboard.

### 📦 The Codebase Packer
Working on a complex architectural bug? Run `flowstate pack` (or click a button in the UI). FlowState will recursively read your entire project, ignore junk like `.git` and `node_modules`, format it beautifully, and copy it to your clipboard so you can feed it to Claude instantly.

### 🤖 Local Project AI Chatbot
Stop copying and pasting files to ChatGPT. FlowState features a built-in Chat tab that intuitively knows your entire codebase. When you ask it a question (e.g., "how does the login work?" or "write a new user dashboard"), it silently searches your project's local ChromaDB, pulls the exact architectural files, injects your tech stack and style guidelines, and gives you a perfectly tailored answer using your configured API.

### 🌐 GitHub Framework Ingestion
Using a complex external framework like FastAPI or TailwindCSS? Just paste the public GitHub URL into FlowState's Knowledge Base tab. FlowState will automatically clone the external repository, scan all its architecture, and permanently inject it into your local ChromaDB so your AI Assistant instantly knows exactly how the framework operates.

### 📋 TODO & FIXME Extractor
Never lose track of your technical debt. FlowState scans your entire project in milliseconds and gives you a beautiful dashboard of every `TODO:` and `FIXME:` marker you left behind, including the file path and line number.

### 📝 Smart Git Changelog
Stop writing PR descriptions manually. FlowState analyzes your `git diff` against the main branch and uses your configured LLM API (OpenAI, Anthropic, or Gemini) to write a stunning, markdown-formatted changelog detailing the "why" and "how" of your code.

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
*From the UI, you can manage your settings, run the Auto-Cleaner daemon, pack your codebase, and view your project's technical debt.*

### The CLI Commands
- `flowstate watch` - Starts the active background daemon to auto-clean files on save.
- `flowstate pack` - Packs your entire project into your clipboard.
- `flowstate todos` - Extracts and displays all TODOs in the terminal.
- `flowstate style` - Copies your custom AI coding style prompt to your clipboard.
- `flowstate clean <file>` - Manually strips AI fluff from a specific file.
- `flowstate start <branch-name>` - Initializes a smart git branch and session notes.
- `flowstate finish` - Generates a PR description.

---

## 🤝 Contributing & How Changes are Accepted

FlowState is completely open-source and we welcome contributions from the community! 
Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for full details on how to get your changes merged.

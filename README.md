# Flowstate

Flowstate is a lightweight, local-first developer flow manager designed for developers who heavily use AI coding tools (Cursor, Claude Desktop, Antigravity, Windsurf, Codex, etc.). 

It helps you reduce context switching, enforce your personal coding style, save tokens by providing compressed context, and keep your git history clean—all entirely locally and offline.

## Why Flowstate?
AI coding tools are amazing, but they often lead to:
- **Token Waste**: Re-explaining your project structure or coding style.
- **Context Loss**: Losing track of what you were doing when switching tools.
- **Messy Git History**: Committing large blocks of AI-generated code with poor commit messages.
- **Verbose Comments**: AI generating unnecessary, long-winded comments.

**Flowstate solves this by running entirely locally on your machine.**

## Installation

Flowstate requires Python 3.11+.

```bash
git clone <your-repo>/flowstate
cd flowstate
pip install -e .
```

## Usage

### 1. Start a Session
Create a smart git branch, load project memory, and open a session notes file:
```bash
flowstate start "feat/user-auth"
```

### 2. During Coding
Copy your personal AI prompt style to your clipboard to paste into any tool:
```bash
flowstate style
```

Clean up excessive AI comments intelligently (AST-based for Python, Regex for others):
```bash
flowstate clean my_file.py
```

Run in the background to automatically monitor file saves and provide notifications (offline):
```bash
flowstate watch
```

### 3. Commit
Commit your changes with a generated conventional commit message, using your real human identity:
```bash
flowstate commit "Optional additional context"
```

### 4. Pause & Resume
Save your current context and restore it later:
```bash
flowstate pause
flowstate resume
```

### 5. Finish
Generate a high-quality PR description in your style:
```bash
flowstate finish
```

### 6. Status
Check your current status, active branch, and session memory:
```bash
flowstate status
```

## Features
- **100% Local & Offline**: Uses SQLite and ChromaDB locally on your machine.
- **Background Autonomous Mode**: Run `flowstate watch` for autonomous background notifications.
- **AI Comment Cleaner**: Intelligently cleans AI-generated fluff.
- **Style Enforcement**: Persistent memory of how you like to code.

## License
MIT

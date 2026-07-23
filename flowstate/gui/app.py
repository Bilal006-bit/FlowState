import customtkinter as ctk
import threading
import pyperclip
from tkinter import filedialog
from pathlib import Path

from ..core.memory import MemoryManager
from ..core.git_utils import get_repo, get_current_branch, get_diff
from ..core.cleaner import clean_file
from ..core.watcher import start_watching
from ..core.learning import extract_project_knowledge, generate_optimized_context, generate_smart_changelog
from ..core.packer import pack_codebase
from ..core.tasks import extract_todos
from ..core.chat import ask_project_bot
from ..core.config import get_config_dir

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FlowstateApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Flowstate v1.0")
        self.geometry("1000x700")
        
        self.memory = MemoryManager()
        self.profile = self.memory.get_profile()
        self.repo = get_repo()
        
        self.watcher_thread = None
        self.chat_history = []
        
        # Grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Flowstate", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.nav_dash = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.nav_dash.grid(row=1, column=0, padx=20, pady=10)
        
        self.nav_tasks = ctk.CTkButton(self.sidebar_frame, text="Tasks & TODOs", command=self.show_tasks)
        self.nav_tasks.grid(row=2, column=0, padx=20, pady=10)
        
        self.nav_kb = ctk.CTkButton(self.sidebar_frame, text="Knowledge Base", command=self.show_kb)
        self.nav_kb.grid(row=3, column=0, padx=20, pady=10)
        
        self.nav_chat = ctk.CTkButton(self.sidebar_frame, text="Project Chat", command=self.show_chat)
        self.nav_chat.grid(row=4, column=0, padx=20, pady=10)
        
        self.nav_settings = ctk.CTkButton(self.sidebar_frame, text="Settings", command=self.show_settings)
        self.nav_settings.grid(row=5, column=0, padx=20, pady=10)
        
        self.nav_logs = ctk.CTkButton(self.sidebar_frame, text="System Logs", command=self.show_logs)
        self.nav_logs.grid(row=6, column=0, padx=20, pady=10)
        
        # --- Main Frame ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self.frames = {}
        self.setup_dashboard()
        self.setup_tasks()
        self.setup_kb()
        self.setup_chat()
        self.setup_settings()
        self.setup_logs()
        
        self.show_dashboard()

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.grid_remove()
        self.frames[name].grid(row=0, column=0, sticky="nsew")

    def show_dashboard(self):
        self.update_dashboard_stats()
        self.show_frame("dashboard")
        
    def show_tasks(self):
        self.refresh_tasks()
        self.show_frame("tasks")
        
    def show_kb(self):
        self.show_frame("kb")
        
    def show_chat(self):
        projects = self.memory.get_learned_projects()
        vals = ["All Projects"] + projects
        self.chat_project_selector.configure(values=vals)
        if self.chat_project_selector.get() not in vals:
            self.chat_project_selector.set("All Projects")
        self.show_frame("chat")
        
    def show_settings(self):
        self.show_frame("settings")
        
    def show_logs(self):
        self.refresh_logs()
        self.show_frame("logs")

    # --- Dashboard View ---
    def setup_dashboard(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        self.frames["dashboard"] = frame
        
        ctk.CTkLabel(frame, text="Live Dashboard", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Stats Grid
        stats_frame = ctk.CTkFrame(frame)
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        stats_frame.grid_columnconfigure((0,1,2), weight=1)
        
        self.stat_branch = ctk.CTkLabel(stats_frame, text="Branch: \n...", font=ctk.CTkFont(size=16))
        self.stat_branch.grid(row=0, column=0, pady=20)
        
        self.stat_minimized = ctk.CTkLabel(stats_frame, text="Comments Minimized: \n...", font=ctk.CTkFont(size=16))
        self.stat_minimized.grid(row=0, column=1, pady=20)
        
        self.stat_changes = ctk.CTkLabel(stats_frame, text="Pending Changes: \n...", font=ctk.CTkFont(size=16))
        self.stat_changes.grid(row=0, column=2, pady=20)
        
        # Actions
        actions_frame = ctk.CTkFrame(frame, fg_color="transparent")
        actions_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        ctk.CTkButton(actions_frame, text="Clean File", command=self.action_clean_file).pack(side="left", padx=10)
        ctk.CTkButton(actions_frame, text="Pack Codebase (Copy)", command=self.action_pack_codebase).pack(side="left", padx=10)
        ctk.CTkButton(actions_frame, text="Generate Changelog", command=self.action_changelog).pack(side="left", padx=10)
        
        self.btn_watch = ctk.CTkButton(actions_frame, text="Start Watcher Daemon", command=self.action_toggle_watcher, fg_color="green")
        self.btn_watch.pack(side="right", padx=10)
        
        self.dash_log = ctk.CTkTextbox(frame, height=200)
        self.dash_log.grid(row=3, column=0, sticky="ew", pady=20)
        self.dash_log.insert("0.0", "Welcome to Flowstate Phase 2.\n")
        
    def log_msg(self, msg):
        self.dash_log.insert("end", f"{msg}\n")
        self.dash_log.see("end")

    def update_dashboard_stats(self):
        branch = get_current_branch(self.repo)
        is_dirty = self.repo.is_dirty(untracked_files=True)
        
        self.profile = self.memory.get_profile()
        self.stat_branch.configure(text=f"Branch: \n{branch}")
        self.stat_minimized.configure(text=f"Lines Cleaned: \n{self.profile.comments_minimized}")
        self.stat_changes.configure(text=f"Pending Changes: \n{'Yes' if is_dirty else 'No'}")

    def action_clean_file(self):
        filepath = filedialog.askopenfilename(title="Select File to Clean")
        if filepath:
            changed, lines_removed = clean_file(Path(filepath))
            if changed:
                self.memory.increment_stat("comments_minimized", lines_removed)
                self.update_dashboard_stats()
                self.log_msg(f"Cleaned {lines_removed} lines from {Path(filepath).name}!")
            else:
                self.log_msg(f"No excessive AI comments found in {Path(filepath).name}.")

    def action_pack_codebase(self):
        self.log_msg("Packing codebase... (ignoring hidden and build folders)")
        packed = pack_codebase(".")
        pyperclip.copy(packed)
        self.log_msg(f"Successfully packed {len(packed)} characters and copied to clipboard!")
        
    def action_changelog(self):
        self.log_msg("Analyzing git diff for smart changelog...")
        diff = get_diff(self.repo)
        if not diff.strip():
            self.log_msg("No git differences found against HEAD.")
            return
            
        def _bg():
            clog = generate_smart_changelog(diff)
            pyperclip.copy(clog)
            self.log_msg("Generated Changelog and copied to clipboard:\n" + clog)
            
        threading.Thread(target=_bg, daemon=True).start()

    def action_toggle_watcher(self):
        if self.watcher_thread and self.watcher_thread.is_alive():
            self.log_msg("Watcher is already running.")
        else:
            self.watcher_thread = threading.Thread(target=start_watching, args=(".",), daemon=True)
            self.watcher_thread.start()
            self.btn_watch.configure(text="Watcher Active", fg_color="gray")
            self.log_msg("Active Watcher Daemon started. It will now intercept saves.")

    # --- Tasks View ---
    def setup_tasks(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        self.frames["tasks"] = frame
        
        ctk.CTkLabel(frame, text="Project Technical Debt", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        self.tasks_textbox = ctk.CTkTextbox(frame, height=450)
        self.tasks_textbox.grid(row=1, column=0, sticky="ew", pady=10)
        
    def refresh_tasks(self):
        todos = extract_todos(".")
        self.tasks_textbox.delete("0.0", "end")
        if not todos:
            self.tasks_textbox.insert("0.0", "No TODOs or FIXMEs found in the project! You're clean.")
            return
            
        report = f"Found {len(todos)} active tasks in the codebase:\n\n"
        for t in todos:
            report += f"[{t['type']}] {t['file']}:{t['line']} -> {t['text']}\n"
            
        self.tasks_textbox.insert("0.0", report)

    # --- Knowledge Base View ---
    def setup_kb(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        self.frames["kb"] = frame
        
        ctk.CTkLabel(frame, text="Knowledge Base & Learning", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew", pady=10)
        
        ctk.CTkLabel(input_frame, text="Directory to learn:").pack(side="left", padx=(0, 10))
        self.entry_learn_dir = ctk.CTkEntry(input_frame, width=350, placeholder_text="e.g. src/ or https://github.com/user/repo")
        self.entry_learn_dir.pack(side="left", padx=(0, 10))
        self.entry_learn_dir.insert(0, ".")
        
        ctk.CTkButton(input_frame, text="Browse...", width=80, command=self.action_browse_dir).pack(side="left", padx=(0, 10))
        ctk.CTkButton(input_frame, text="Run Automated API Learning", command=self.action_run_learning).pack(side="left")        
        self.kb_text = ctk.CTkTextbox(frame, height=300)
        self.kb_text.grid(row=2, column=0, sticky="ew", pady=10)
        
        ctk.CTkButton(frame, text="Copy Optimized Context Block to Clipboard", command=self.action_copy_context).grid(row=3, column=0, sticky="w", pady=10)
        
        self.refresh_kb_view()
        
    def refresh_kb_view(self):
        context = generate_optimized_context()
        self.kb_text.delete("0.0", "end")
        self.kb_text.insert("0.0", context)
        
    def action_run_learning(self):
        target_dir = self.entry_learn_dir.get().strip()
        if not target_dir:
            target_dir = "."
            
        def _learn():
            success = extract_project_knowledge(target_dir)
            if success:
                self.refresh_kb_view()
        threading.Thread(target=_learn, daemon=True).start()
        
    def action_copy_context(self):
        context = self.kb_text.get("0.0", "end")
        pyperclip.copy(context)
        
    def action_browse_dir(self):
        directory = filedialog.askdirectory(title="Select Directory to Learn")
        if directory:
            self.entry_learn_dir.delete(0, "end")
            self.entry_learn_dir.insert(0, directory)

    # --- Chat View ---
    def setup_chat(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        self.frames["chat"] = frame
        
        # Top bar with Title and Dropdown
        top_bar = ctk.CTkFrame(frame, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_bar.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(top_bar, text="Project Chat", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w")
        
        self.chat_project_selector = ctk.CTkOptionMenu(top_bar, values=["All Projects"])
        self.chat_project_selector.grid(row=0, column=1, sticky="e")
        
        self.chat_display = ctk.CTkTextbox(frame)
        self.chat_display.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.chat_display.insert("0.0", "Welcome to Project Chat! Ask me anything about your codebase.\n\n")
        self.chat_display.configure(state="disabled")
        
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_input = ctk.CTkEntry(input_frame, placeholder_text="Type your question here...")
        self.chat_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.chat_input.bind("<Return>", lambda event: self.action_send_chat())
        
        self.btn_send_chat = ctk.CTkButton(input_frame, text="Send", width=80, command=self.action_send_chat)
        self.btn_send_chat.grid(row=0, column=1)

    def action_send_chat(self):
        query = self.chat_input.get().strip()
        if not query: return
        
        self.chat_input.delete(0, "end")
        
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"You: {query}\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
        self.btn_send_chat.configure(state="disabled")
        
        selected_project = self.chat_project_selector.get()
        
        def _bg_chat():
            response, sources = ask_project_bot(query, self.chat_history, project_path=selected_project)
            
            # Format sources text
            sources_text = ""
            if sources:
                sources_text = "\n\n*(Sources retrieved: " + ", ".join(sources) + ")*"
                
            full_response = response + sources_text
            
            # Update history
            self.chat_history.append({"role": "User", "message": query})
            self.chat_history.append({"role": "FlowState", "message": full_response})
            
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"FlowState: {full_response}\n\n")
            self.chat_display.see("end")
            self.chat_display.configure(state="disabled")
            self.btn_send_chat.configure(state="normal")
            
        threading.Thread(target=_bg_chat, daemon=True).start()

    # --- Settings View ---
    def setup_settings(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.grid_columnconfigure(1, weight=1)
        self.frames["settings"] = frame
        
        ctk.CTkLabel(frame, text="Settings", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Tech Stack
        ctk.CTkLabel(frame, text="Tech Stack (e.g. Python, React):").grid(row=1, column=0, sticky="w", pady=10, padx=10)
        self.entry_stack = ctk.CTkEntry(frame)
        self.entry_stack.grid(row=1, column=1, sticky="ew", pady=10)
        self.entry_stack.insert(0, self.profile.tech_stack or "")
        
        # Provider
        ctk.CTkLabel(frame, text="LLM API Provider:").grid(row=2, column=0, sticky="w", pady=10, padx=10)
        self.entry_provider = ctk.CTkOptionMenu(frame, values=["openai", "anthropic", "gemini", "ollama"])
        self.entry_provider.set(self.profile.api_provider or "openai")
        self.entry_provider.grid(row=2, column=1, sticky="ew", pady=10)
        
        # API Key
        ctk.CTkLabel(frame, text="API Key / Ollama Model (e.g. llama3):").grid(row=3, column=0, sticky="w", pady=10, padx=10)
        self.entry_key = ctk.CTkEntry(frame, show="*")
        self.entry_key.grid(row=3, column=1, sticky="ew", pady=10)
        self.entry_key.insert(0, self.profile.api_key or "")
        
        # Fallback Provider
        ctk.CTkLabel(frame, text="Fallback API Provider:").grid(row=4, column=0, sticky="w", pady=10, padx=10)
        self.entry_fallback_provider = ctk.CTkOptionMenu(frame, values=["openai", "anthropic", "gemini", "ollama"])
        self.entry_fallback_provider.set(self.profile.fallback_api_provider or "gemini")
        self.entry_fallback_provider.grid(row=4, column=1, sticky="ew", pady=10)
        
        # Fallback API Key
        ctk.CTkLabel(frame, text="Fallback API Key:").grid(row=5, column=0, sticky="w", pady=10, padx=10)
        self.entry_fallback_key = ctk.CTkEntry(frame, show="*")
        self.entry_fallback_key.grid(row=5, column=1, sticky="ew", pady=10)
        self.entry_fallback_key.insert(0, self.profile.fallback_api_key or "")
        
        ctk.CTkButton(frame, text="Save Settings", command=self.save_settings).grid(row=6, column=0, columnspan=2, pady=20)

    def save_settings(self):
        stack = self.entry_stack.get()
        provider = self.entry_provider.get()
        key = self.entry_key.get()
        fb_provider = self.entry_fallback_provider.get()
        fb_key = self.entry_fallback_key.get()
        
        self.memory.update_profile(
            tech_stack=stack, 
            api_provider=provider, 
            api_key=key, 
            fallback_api_provider=fb_provider, 
            fallback_api_key=fb_key
        )
        self.profile = self.memory.get_profile()
        self.refresh_kb_view()

    # --- System Logs View ---
    def setup_logs(self):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        self.frames["logs"] = frame
        
        ctk.CTkLabel(frame, text="System Logs", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        self.logs_display = ctk.CTkTextbox(frame, font=ctk.CTkFont(family="Consolas", size=13))
        self.logs_display.grid(row=1, column=0, sticky="nsew", pady=10)
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=10)
        ctk.CTkButton(btn_frame, text="Clear Logs", command=self.action_clear_logs).pack(side="right")
        
        # Start auto-refresh loop
        self.refresh_logs()
        
    def refresh_logs(self):
        log_file = get_config_dir() / "flowstate.log"
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Only update if changed to prevent annoying scroll jumps
                current = self.logs_display.get("0.0", "end").strip()
                if content.strip() != current:
                    self.logs_display.delete("0.0", "end")
                    self.logs_display.insert("0.0", content)
                    self.logs_display.see("end")
            except Exception:
                pass
        else:
            self.logs_display.delete("0.0", "end")
            self.logs_display.insert("0.0", "No logs recorded yet. Start watching a folder or chatting!")
            
        # Re-schedule every 2000ms
        self.after(2000, self.refresh_logs)
        
    def action_clear_logs(self):
        log_file = get_config_dir() / "flowstate.log"
        if log_file.exists():
            try:
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write("")
                self.logs_display.delete("0.0", "end")
            except Exception:
                pass

def run_app():
    app = FlowstateApp()
    app.mainloop()

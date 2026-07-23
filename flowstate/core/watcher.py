import time
import threading
import pyperclip
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification

from .cleaner import clean_file
from .learning import generate_optimized_context
from .memory import MemoryManager

class FlowstateEventHandler(FileSystemEventHandler):
    def __init__(self, root_path: Path):
        super().__init__()
        self.memory = MemoryManager()
        self.last_clean_time = 0
        self.root_path = root_path

    def on_modified(self, event):
        if event.is_directory:
            return
            
        path = Path(event.src_path)
        # Ignore our own hidden dirs, git dirs, and temp files
        if '.git' in path.parts or '.flowstate' in path.parts or path.name.startswith('.~'):
            return
            
        if path.suffix in ['.py', '.js', '.ts', '.tsx', '.jsx']:
            # Debounce to prevent infinite loops when we write to the file ourselves
            now = time.time()
            if now - self.last_clean_time < 2:
                return
                
            # 1. Active Action: Auto-Clean
            changed, lines_removed = clean_file(path)
            if changed:
                self.last_clean_time = time.time()
                self.memory.increment_stat("comments_minimized", lines_removed)
                print(f"[Active Watcher] Cleaned {lines_removed} lines of AI fluff from {path.name}")
                
                # Notify User
                try:
                    notification.notify(
                        title="Flowstate: AI Fluff Removed",
                        message=f"Automatically stripped {lines_removed} lines of hallucinated comments from {path.name}",
                        timeout=3
                    )
                except Exception:
                    pass
            
            # 2. Active Action: Auto-Context Update
            # Quietly update the clipboard with optimized context so it's always ready to paste
            try:
                context = generate_optimized_context()
                pyperclip.copy(context)
            except Exception:
                pass
                
            # 3. Silent Action: Real-time Learning
            try:
                from .learning import extract_and_store_file
                extract_and_store_file(path, self.root_path)
            except Exception:
                pass


def start_watching(path: str = "."):
    """Start the background daemon to actively manage flow state."""
    event_handler = FlowstateEventHandler(root_path=Path(path).resolve())
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    print(f"Active Flowstate daemon watching {Path(path).resolve()}...")
    print("Anti-Hallucination Auto-Cleaner: ENABLED")
    print("Auto-Context Optimizer: ENABLED")
    print("Memory Enrichment Complete!")
    print("Press Ctrl+C to stop.")
    
    try:
        notification.notify(
            title="Flowstate Active",
            message="Your Active Junior Engineer is now monitoring your files and saving tokens.",
            timeout=5
        )
    except Exception:
        pass
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nFlowstate daemon stopped.")
        
    observer.join()

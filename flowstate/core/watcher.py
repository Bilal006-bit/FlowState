import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification

class FlowstateEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
            
        path = Path(event.src_path)
        # Ignore our own hidden dirs and git dirs
        if '.git' in path.parts or '.flowstate' in path.parts:
            return
            
        # Optional: Notify on significant file changes
        if path.suffix in ['.py', '.js', '.ts', '.md']:
            # Just log to console for now; could trigger notification if heavily modified
            print(f"[Watchdog] Detected save on: {path.name}")
            # To avoid spamming OS notifications on every Ctrl+S, we would debounce here.

def start_watching(path: str = "."):
    """Start the background daemon to watch for file changes."""
    event_handler = FlowstateEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    print(f"Flowstate daemon watching {Path(path).resolve()} for changes...")
    print("Press Ctrl+C to stop.")
    
    try:
        # Send an initial notification
        notification.notify(
            title="Flowstate Active",
            message="Your local AI coding assistant manager is running in the background.",
            timeout=5
        )
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nFlowstate daemon stopped.")
        
    observer.join()

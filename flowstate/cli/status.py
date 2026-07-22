import typer
from rich.console import Console
from rich.panel import Panel
from ..core.git_utils import get_repo, get_current_branch
from ..core.memory import MemoryManager

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def show_status():
    """View your current Flowstate status and memory."""
    repo = get_repo()
    branch = get_current_branch(repo)
    is_dirty = repo.is_dirty(untracked_files=True)
    
    memory = MemoryManager()
    profile = memory.get_profile()
    
    status_text = f"""[bold cyan]User Profile[/bold cyan]
Name: {profile.name}
Email: {profile.email}

[bold cyan]Git Status[/bold cyan]
Branch: {branch}
Pending Changes: {'Yes' if is_dirty else 'No'}

[bold cyan]Memory System[/bold cyan]
Global DB: Active
Vector DB (Chroma): Active
"""
    
    console.print(Panel.fit(status_text, title="Flowstate Status"))

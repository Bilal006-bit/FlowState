import typer
from pathlib import Path
from rich.console import Console
from ..core.git_utils import get_repo, create_branch
from ..core.memory import MemoryManager

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def start_session(ticket: str = typer.Argument(..., help="The ticket number or description")):
    """Start a new coding session."""
    console.print(f"[bold green]Starting Flowstate session for:[/bold green] {ticket}")
    
    # 1. Handle Git branch
    repo = get_repo()
    branch_name = ticket.replace(" ", "-").lower()
    create_branch(repo, branch_name)
    console.print(f"[cyan]Checked out new branch:[/cyan] {branch_name}")
    
    # 2. Load memory and profile
    memory = MemoryManager()
    profile = memory.get_profile()
    console.print(f"[cyan]Loaded profile for:[/cyan] {profile.name}")
    
    # 3. Create a session notes file
    safe_filename = branch_name.replace("/", "-").replace("\\", "-")
    notes_file = Path(f"SESSION_{safe_filename}.md")
    if not notes_file.exists():
        notes_file.write_text(f"# Session: {ticket}\n\n## Goals\n- \n\n## AI Context\n- \n")
        console.print(f"[cyan]Created session notes:[/cyan] {notes_file.name}")
    
    console.print("[bold green]Ready to flow![/bold green]")

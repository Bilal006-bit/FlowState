import typer
from rich.console import Console
from ..core.git_utils import get_repo, commit_changes, get_diff
from ..core.memory import MemoryManager

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def make_commit(message: str = typer.Argument(None, help="Optional commit message")):
    """Commit your changes locally with human identity."""
    repo = get_repo()
    memory = MemoryManager()
    profile = memory.get_profile()
    
    if not repo.is_dirty(untracked_files=True):
        console.print("[yellow]Nothing to commit. Working tree clean.[/yellow]")
        raise typer.Exit()
        
    if not message:
        # Simple heuristic since offline: count lines changed or just use a generic conventional commit
        # For a more advanced offline feature, a small local LLM could be used here.
        # For v1, we use a heuristic based on diff length
        diff_text = get_diff(repo)
        if "def " in diff_text or "class " in diff_text:
            message = "feat: update logic and implementations"
        else:
            message = "chore: update project files"
            
        console.print(f"[dim]No message provided. Generated heuristic message:[/dim] '{message}'")
        
    commit_changes(repo, message, profile.name, profile.email)
    console.print(f"[bold green]Committed successfully as {profile.name} <{profile.email}>![/bold green]")

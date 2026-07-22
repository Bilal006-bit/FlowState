import typer
from pathlib import Path
from rich.console import Console
from ..core.cleaner import clean_file

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def clean_comments(filepath: str = typer.Argument(..., help="The file to clean AI comments from")):
    """Clean excessive AI-generated comments from a file."""
    target_path = Path(filepath)
    if not target_path.exists():
        console.print(f"[bold red]Error:[/bold red] File {filepath} does not exist.")
        raise typer.Exit(code=1)
        
    console.print(f"Analyzing [cyan]{target_path.name}[/cyan]...")
    changed = clean_file(target_path)
    
    if changed:
        console.print(f"[bold green]Successfully cleaned {target_path.name}![/bold green]")
        console.print("[dim]Excessive AI comments and fluff have been truncated.[/dim]")
    else:
        console.print(f"[yellow]No excessive comments found in {target_path.name}.[/yellow]")

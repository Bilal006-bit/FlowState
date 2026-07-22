import typer
from rich.console import Console
from rich.table import Table
from ..core.tasks import extract_todos

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def show_todos():
    """Extract and display all TODO and FIXME comments across the project."""
    console.print("[cyan]Scanning project for TODOs and FIXMEs...[/cyan]")
    todos = extract_todos(".")
    
    if not todos:
        console.print("[bold green]No technical debt found! Great job.[/bold green]")
        return
        
    table = Table(title="Project Technical Debt (TODOs/FIXMEs)")
    table.add_column("Type", style="magenta")
    table.add_column("File:Line", style="cyan")
    table.add_column("Description", style="green")
    
    for t in todos:
        table.add_row(t['type'], f"{t['file']}:{t['line']}", t['text'])
        
    console.print(table)

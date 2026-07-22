import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def launch_ui():
    """Launch the Flowstate Desktop App GUI."""
    try:
        from ..gui.app import run_app
        console.print("[bold green]Launching Flowstate Desktop App...[/bold green]")
        run_app()
    except ImportError as e:
        console.print(f"[bold red]Failed to launch GUI:[/bold red] {e}")
        console.print("Make sure you have installed the GUI dependencies (`customtkinter`, `litellm`).")

import typer
import pyperclip
from rich.console import Console
from ..core.packer import pack_codebase

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def pack_project():
    """Pack the entire codebase into a single formatted string and copy to clipboard."""
    console.print("[cyan]Packing codebase (ignoring hidden/build dirs)...[/cyan]")
    packed = pack_codebase(".")
    
    try:
        pyperclip.copy(packed)
        console.print(f"[bold green]Successfully packed {len(packed)} characters into clipboard![/bold green]")
        console.print("[cyan]Paste this into Claude or ChatGPT to give it full project context.[/cyan]")
    except Exception:
        console.print("[bold red]Failed to copy to clipboard. Displaying output:[/bold red]\n")
        console.print(packed[:1000] + "\n... (truncated)")

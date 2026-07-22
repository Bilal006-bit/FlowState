import typer
import pyperclip
from rich.console import Console
from ..core.memory import MemoryManager
from ..core.config import DEFAULT_STYLE_PROMPT

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def copy_style():
    """Copy your personal coding style prompt to the clipboard."""
    memory = MemoryManager()
    profile = memory.get_profile()
    
    style_text = profile.style_prompt if profile.style_prompt else DEFAULT_STYLE_PROMPT
    
    try:
        pyperclip.copy(style_text)
        console.print("[bold green]Successfully copied style to clipboard![/bold green]")
        console.print("[dim]Paste this into Claude Desktop, Cursor, or ChatGPT to align the AI to your style.[/dim]")
    except Exception as e:
        console.print(f"[bold red]Failed to copy to clipboard:[/bold red] {e}")
        console.print("[cyan]Here is your style text instead:[/cyan]")
        console.print(style_text)

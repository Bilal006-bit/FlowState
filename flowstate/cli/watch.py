import typer
from ..core.watcher import start_watching

app = typer.Typer()

@app.callback(invoke_without_command=True)
def run_watcher(path: str = typer.Argument(".", help="Path to watch")):
    """Run the autonomous background daemon to monitor files."""
    start_watching(path)

import typer
from rich.console import Console
from .cli import start, style, clean, commit, finish, status, watch, ui

app = typer.Typer(help="Flowstate: The local-first developer flow manager.")
console = Console()

app.add_typer(start.app, name="start", help="Start a new session")
app.add_typer(style.app, name="style", help="Copy your coding style to clipboard")
app.add_typer(clean.app, name="clean", help="Clean up AI generated fluff from files")
app.add_typer(commit.app, name="commit", help="Commit your changes locally")
app.add_typer(finish.app, name="finish", help="Finish your session and generate a PR description")
app.add_typer(status.app, name="status", help="View your Flowstate status")
app.add_typer(watch.app, name="watch", help="Run the autonomous background daemon")
app.add_typer(ui.app, name="ui", help="Launch the Flowstate Desktop GUI")

if __name__ == "__main__":
    app()

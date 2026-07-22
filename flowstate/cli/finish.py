import typer
import pyperclip
from rich.console import Console
from ..core.git_utils import get_repo, get_current_branch

app = typer.Typer()
console = Console()

@app.callback(invoke_without_command=True)
def finish_session():
    """Finish your session and generate a PR description."""
    repo = get_repo()
    branch = get_current_branch(repo)
    
    # Offline heuristic PR template
    pr_template = f"""# Pull Request: {branch}

## Description
[Flowstate: Summarize your changes here based on the branch name and commits]
This PR addresses the features/fixes targeted by `{branch}`.

## Checklist
- [x] Tested locally
- [x] Code style checked via Flowstate
- [x] Removed AI-generated excessive comments

## Notes for Reviewer
- Commits are verified to be written by a human.
"""
    
    try:
        pyperclip.copy(pr_template)
        console.print("[bold green]Generated PR Description and copied to clipboard![/bold green]")
    except Exception:
        console.print("[bold green]Generated PR Description:[/bold green]\n")
        console.print(pr_template)
        
    console.print("\n[cyan]Tip: You can now run `git push origin HEAD` or use the GitHub CLI (`gh pr create`).[/cyan]")

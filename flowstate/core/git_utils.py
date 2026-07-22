import os
from pathlib import Path
from git import Repo, InvalidGitRepositoryError

def get_repo(path: Path = Path.cwd()) -> Repo:
    try:
        return Repo(path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        # Initialize a new repo if one doesn't exist
        print("No git repository found. Initializing one...")
        return Repo.init(path)

def create_branch(repo: Repo, branch_name: str) -> None:
    """Create and checkout a new branch."""
    if branch_name in [h.name for h in repo.heads]:
        repo.git.checkout(branch_name)
    else:
        new_branch = repo.create_head(branch_name)
        repo.head.reference = new_branch
        repo.head.reset(index=True, working_tree=True)
        repo.git.checkout(branch_name)

def get_current_branch(repo: Repo) -> str:
    try:
        return repo.active_branch.name
    except TypeError:
        return "detached"

def commit_changes(repo: Repo, message: str, author_name: str, author_email: str) -> None:
    """Commit all changes with the given author."""
    repo.git.add(A=True)
    author = f"{author_name} <{author_email}>"
    repo.git.commit(m=message, author=author)

def get_diff(repo: Repo) -> str:
    """Get current diff of working tree vs HEAD."""
    return repo.git.diff('HEAD')

"""CLI entry point for leetcode-sync.

Commands:
    init       - Initialize a new leetcode-sync project
    auth       - Show instructions for authenticating with LeetCode
    sync       - Sync accepted submissions from LeetCode
    status     - Show current sync status
    git-status - Show git status
    commit     - Commit synced changes
    push       - Push committed changes to remote
    watch      - Watch for new submissions and sync automatically
"""

from __future__ import annotations

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel

from leetcode_sync import __version__
from leetcode_sync.config import (
    create_gitignore,
    find_project_root,
    load_config,
)
from leetcode_sync.git.manager import GitError, GitManager
from leetcode_sync.storage.state import StateManager

# Create the Typer app
app = typer.Typer(
    name="leetcode-sync",
    help="Sync your LeetCode accepted submissions into a Git repository.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Sub-app for git commands
git_app = typer.Typer(help="Git operations for leetcode-sync.")
app.add_typer(git_app, name="git")

console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with Rich."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@app.command()
def init(
    path: str | None = typer.Argument(None, help="Path to initialize the project"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
) -> None:
    """Initialize a new leetcode-sync project.

    Creates the necessary directory structure, configuration files,
    and verifies the environment.
    """
    project_root = Path(path) if path else find_project_root()

    console.print(f"\n[bold]Initializing leetcode-sync in {project_root}[/bold]\n")

    # Create directories
    directories = [
        project_root / "leetcode",
        project_root / "topics",
        project_root / ".leetcode-sync",
    ]

    for dir_path in directories:
        if dir_path.exists() and not force:
            console.print(f"  [dim]Exists:[/dim] {dir_path.relative_to(project_root)}/")
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            console.print(f"  [green]✓[/green] Created {dir_path.relative_to(project_root)}/")

    # Create configuration files
    env_example_path = project_root / ".env.example"
    if env_example_path.exists() and not force:
        console.print(f"  [dim]Exists:[/dim] {env_example_path.name}")
    else:
        # Create the env example directly in the target directory
        env_example_content = """# leetcode-sync configuration
# Copy this file to .env and fill in your values.
# NEVER commit .env to version control.

# LeetCode authentication (required)
# Get these from your browser cookies when logged into LeetCode.
# See: leetcode-sync auth for instructions.
LEETCODE_SESSION=
LEETCODE_CSRF_TOKEN=

# Path to the LeetCode solutions repository (optional)
# If empty, uses the current directory.
LEETCODE_REPO_PATH=

# Auto-commit after sync (default: false)
GIT_AUTO_COMMIT=false

# Auto-push after commit (default: false)
GIT_AUTO_PUSH=false

# Watch mode polling interval in seconds (default: 120)
WATCH_INTERVAL=120
"""
        env_example_path.write_text(env_example_content)
        console.print(f"  [green]✓[/green] Created {env_example_path.name}")

    # Update .gitignore
    create_gitignore()
    console.print("  [green]✓[/green] Updated .gitignore")

    # Verify Git
    console.print("\n[bold]Checking environment...[/bold]\n")
    _check_git(project_root)

    # Check for .env file
    env_file = project_root / ".env"
    if env_file.exists():
        console.print("  [green]✓[/green] .env file found")
    else:
        console.print(
            "  [yellow]![/yellow] No .env file found. "
            "Copy .env.example to .env and add your credentials."
        )

    # Initialize git repo if not already one
    git_manager = GitManager(project_root)
    if not git_manager.is_git_repo():
        console.print("\n  [yellow]![/yellow] Not a Git repository. Initializing...")
        git_manager.init_repo(project_root)
        console.print("  [green]✓[/green] Initialized Git repository")
    else:
        console.print("  [green]✓[/green] Git repository detected")

    console.print("\n[bold green]Initialization complete![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. [cyan]leetcode-sync auth[/cyan] - Set up LeetCode authentication")
    console.print("  2. [cyan]leetcode-sync sync[/cyan] - Sync your first submissions")


@app.command()
def auth() -> None:
    """Show instructions for authenticating with LeetCode.

    This command does NOT ask for your password.
    It explains how to safely provide your session cookies.
    """
    auth_text = """
[bold]LeetCode Authentication Setup[/bold]

[bold]Method: Browser Cookies (Recommended)[/bold]

1. Log in to [link=https://leetcode.com]leetcode.com[/link] in your browser

2. Open Developer Tools (F12 or Cmd+Option+I)

3. Go to the [cyan]Application[/cyan] tab (Chrome) or [cyan]Storage[/cyan] tab (Firefox)

4. Find [cyan]Cookies[/cyan] > [cyan]https://leetcode.com[/cyan]

5. Copy the values of:
   • [green]LEETCODE_SESSION[/green] - Your session cookie
   • [green]csrftoken[/green] - Your CSRF token

6. Add them to your [cyan].env[/cyan] file:

   [dim]LEETCODE_SESSION=your_session_cookie_here[/dim]
   [dim]LEETCODE_CSRF_TOKEN=your_csrf_token_here[/dim]

[bold]Security Notes:[/bold]
• Never commit .env to version control
• Cookies expire periodically - you may need to re-authenticate
• Never share your session cookies with anyone
• leetcode-sync will NEVER log or expose your credentials

[bold]Troubleshooting:[/bold]
• If authentication fails, try getting fresh cookies
• Make sure you're copying the full cookie value
• Check that .env is in the same directory as your project
"""
    console.print(Panel(auth_text, title="Authentication", border_style="cyan"))


@app.command()
def status(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed info"),
) -> None:
    """Show current sync status.

    Displays information about the current project state,
    authentication status, and recently processed submissions.
    """
    setup_logging(verbose)

    console.print("\n[bold]leetcode-sync Status[/bold]\n")

    # Check project structure
    project_root = find_project_root()
    console.print(f"Project root: [cyan]{project_root}[/cyan]")

    # Check directories
    dirs_to_check = [
        ("leetcode", project_root / "leetcode"),
        ("topics", project_root / "topics"),
        (".leetcode-sync", project_root / ".leetcode-sync"),
    ]

    console.print("\n[bold]Directory Structure:[/bold]")
    for name, dir_path in dirs_to_check:
        if dir_path.exists():
            count = len(list(dir_path.iterdir())) if dir_path.is_dir() else 0
            console.print(f"  [green]✓[/green] {name}/ ({count} items)")
        else:
            console.print(f"  [red]✗[/red] {name}/ (missing)")

    # Check configuration
    console.print("\n[bold]Configuration:[/bold]")
    config = load_config()

    if config.leetcode_session:
        console.print("  [green]✓[/green] LeetCode session: configured")
    else:
        console.print("  [red]✗[/red] LeetCode session: not configured")

    if config.leetcode_csrf_token:
        console.print("  [green]✓[/green] CSRF token: configured")
    else:
        console.print("  [yellow]![/yellow] CSRF token: not configured")

    # Check git status
    console.print("\n[bold]Git Status:[/bold]")
    git_manager = GitManager(project_root)
    if git_manager.is_git_repo():
        branch = git_manager.get_current_branch()
        console.print(f"  [green]✓[/green] Repository: on branch [cyan]{branch}[/cyan]")

        changed_files = git_manager.get_changed_files()
        if changed_files:
            console.print(f"  [yellow]![/yellow] {len(changed_files)} uncommitted changes")
        else:
            console.print("  [green]✓[/green] Working directory clean")
    else:
        console.print("  [red]✗[/red] Not a Git repository")

    # Check sync state
    state_manager = StateManager()
    state = state_manager.load()
    console.print("\n[bold]Sync State:[/bold]")
    console.print(
        f"  Processed submissions: [cyan]{len(state.processed_submissions)}[/cyan]"
    )
    if state.last_sync_time:
        console.print(f"  Last sync: [cyan]{state.last_sync_time}[/cyan]")
    else:
        console.print("  Last sync: [dim]never[/dim]")

    console.print()


@app.command()
def submissions(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of submissions to fetch"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed info"),
) -> None:
    """Show recent accepted submissions from LeetCode.

    This command tests the LeetCode API connection without writing files.
    """
    setup_logging(verbose)

    config = load_config()
    if not config.is_authenticated:
        console.print("[red]✗ Not authenticated with LeetCode.[/red]")
        console.print("\nRun [cyan]leetcode-sync auth[/cyan] for setup instructions.")
        raise typer.Exit(1)

    from leetcode_sync.leetcode.client import (
        LeetCodeClient,
    )

    try:
        with LeetCodeClient(config) as client:
            console.print("\nFetching recent submissions...\n")
            submissions_list = client.get_recent_submissions(limit)

            if not submissions_list:
                console.print("[yellow]No submissions found.[/yellow]")
                return

            console.print(
                f"Found [cyan]{len(submissions_list)}[/cyan] submissions:\n"
            )

            for sub in submissions_list:
                status_color = (
                    "green" if sub.is_accepted else "red"
                )
                console.print(
                    f"  [{status_color}]✓[/{status_color}] "
                    f"[cyan]{sub.submission_id}[/cyan] "
                    f"{sub.title}"
                )
                console.print(
                    f"    Status: [{status_color}]{sub.status}[/{status_color}]"
                    f" | Language: {sub.language}"
                    f" | {sub.submitted_at}"
                )
                console.print()

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def inspect(
    problem_slug: str = typer.Argument(
        ..., help="Problem slug or submission ID"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed info"),
) -> None:
    """Inspect a LeetCode problem or submission.

    Fetches and displays detailed problem metadata.
    """
    setup_logging(verbose)

    config = load_config()
    if not config.is_authenticated:
        console.print("[red]✗ Not authenticated with LeetCode.[/red]")
        console.print("\nRun [cyan]leetcode-sync auth[/cyan] for setup instructions.")
        raise typer.Exit(1)

    from leetcode_sync.leetcode.client import LeetCodeClient

    try:
        with LeetCodeClient(config) as client:
            console.print(f"\nFetching problem: {problem_slug}\n")
            problem = client.get_problem(problem_slug)

            if not problem:
                console.print(
                    f"[red]✗ Problem not found: {problem_slug}[/red]"
                )
                raise typer.Exit(1)

            # Display problem info
            console.print(
                f"[bold]#{problem.number}. {problem.title}[/bold]"
            )
            console.print(
                f"Difficulty: [cyan]{problem.difficulty.value}[/cyan]"
            )

            if problem.topics:
                console.print(
                    f"Topics: {', '.join(problem.topics)}"
                )

            console.print(
                f"\nDescription length: "
                f"{len(problem.description)} chars"
            )

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def sync(
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n",
        help="Preview changes without applying",
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Overwrite existing files",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Show detailed info",
    ),
) -> None:
    """Sync accepted submissions from LeetCode.

    Fetches recent accepted submissions, compares with local state,
    and generates files for new solutions.
    """
    setup_logging(verbose)

    config = load_config()
    if not config.is_authenticated:
        console.print(
            "[red]✗ Not authenticated with LeetCode.[/red]"
        )
        console.print(
            "\nRun [cyan]leetcode-sync auth[/cyan] "
            "for setup instructions."
        )
        raise typer.Exit(1)

    # This is a placeholder for Phase 4 implementation
    console.print(
        "[yellow]Sync command not yet implemented.[/yellow]"
    )
    console.print("This will be implemented in Phase 4.")


@app.command("git-status")
def git_status_cmd() -> None:
    """Show git status for the leetcode-sync repository."""
    project_root = find_project_root()
    git_manager = GitManager(project_root)

    if not git_manager.is_git_repo():
        console.print("[red]✗ Not a Git repository.[/red]")
        raise typer.Exit(1)

    branch = git_manager.get_current_branch()
    console.print(f"\n[bold]Branch:[/bold] [cyan]{branch}[/cyan]")

    changed_files = git_manager.get_changed_files()
    if changed_files:
        console.print(f"\n[bold]Changed files ({len(changed_files)}):[/bold]")
        for f in changed_files:
            console.print(f"  {f}")
    else:
        console.print("\n[green]✓ Working directory clean[/green]")


@app.command()
def commit(
    message: str | None = typer.Option(None, "-m", "--message", help="Commit message"),
) -> None:
    """Commit synced changes to git.

    Only stages files generated by leetcode-sync.
    """
    project_root = find_project_root()
    git_manager = GitManager(project_root)

    if not git_manager.is_git_repo():
        console.print("[red]✗ Not a Git repository.[/red]")
        raise typer.Exit(1)

    if not git_manager.has_uncommitted_changes():
        console.print("[yellow]Nothing to commit.[/yellow]")
        return

    # Default commit message
    if not message:
        changed_files = git_manager.get_changed_files()
        # Try to detect problem numbers from filenames
        problem_numbers = []
        for f in changed_files:
            if "/" in f:
                parts = f.split("/")
                for part in parts:
                    if len(part) >= 4 and part[:4].isdigit():
                        try:
                            num = int(part[:4])
                            if num not in problem_numbers:
                                problem_numbers.append(num)
                        except ValueError:
                            pass

        if problem_numbers:
            nums_str = ", ".join(f"#{n}" for n in sorted(problem_numbers)[:5])
            if len(problem_numbers) > 5:
                nums_str += f" and {len(problem_numbers) - 5} more"
            message = f"Add LeetCode solutions: {nums_str}"
        else:
            message = "Update leetcode-sync solutions"

    # Stage only known leetcode-sync files
    git_manager.stage_files(git_manager.get_changed_files())

    try:
        git_manager.commit(message)
        console.print(f"[green]✓ Committed: {message}[/green]")
    except GitError as e:
        console.print(f"[red]✗ Commit failed: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def push(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed info"),
) -> None:
    """Push committed changes to the remote repository.

    Never force pushes. Always pushes to the current branch.
    """
    setup_logging(verbose)

    project_root = find_project_root()
    git_manager = GitManager(project_root)

    if not git_manager.is_git_repo():
        console.print("[red]✗ Not a Git repository.[/red]")
        raise typer.Exit(1)

    if not git_manager.has_remote():
        console.print("[red]✗ No remote configured.[/red]")
        console.print("Add a remote with: [cyan]git remote add origin <url>[/cyan]")
        raise typer.Exit(1)

    branch = git_manager.get_current_branch()
    console.print(f"Pushing to [cyan]{branch}[/cyan]...")

    try:
        git_manager.push()
        console.print("[green]✓ Pushed successfully![/green]")
    except GitError as e:
        console.print(f"[red]✗ Push failed: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def watch(
    interval: int = typer.Option(120, "--interval", "-i", help="Polling interval in seconds"),
    auto_commit: bool = typer.Option(False, "--auto-commit", help="Auto-commit after sync"),
    auto_push: bool = typer.Option(False, "--auto-push", help="Auto-push after commit"),
) -> None:
    """Watch for new submissions and sync automatically.

    Polls LeetCode at the specified interval and syncs new accepted submissions.
    Press Ctrl+C to stop gracefully.
    """
    console.print("[yellow]Watch mode not yet implemented.[/yellow]")
    console.print("This will be implemented in Phase 7.")


@app.command()
def version() -> None:
    """Show the leetcode-sync version."""
    console.print(f"leetcode-sync version [cyan]{__version__}[/cyan]")


def _check_git(project_root: Path) -> None:
    """Check Git installation and repository status."""
    git_manager = GitManager(project_root)

    # Check git is installed
    try:
        git_manager._run_git("version")
        console.print("  [green]✓[/green] Git installed")
    except GitError:
        console.print("  [red]✗[/red] Git not installed or not in PATH")
        return

    # Check if in a git repo
    if git_manager.is_git_repo():
        console.print("  [green]✓[/green] Git repository detected")
        branch = git_manager.get_current_branch()
        console.print(f"  [green]✓[/green] Current branch: [cyan]{branch}[/cyan]")

        if git_manager.has_remote():
            console.print("  [green]✓[/green] Remote configured")
        else:
            console.print(
                "  [yellow]![/yellow] No remote configured. "
                "Add one with: [cyan]git remote add origin <url>[/cyan]"
            )
    else:
        console.print("  [yellow]![/yellow] Not a Git repository yet")


if __name__ == "__main__":
    app()

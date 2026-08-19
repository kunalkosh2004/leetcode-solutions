"""Configuration management for leetcode-sync.

Loads configuration from environment variables and .env files.
Credentials are never logged or committed.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from leetcode_sync.models import AppConfig

# Default paths
DEFAULT_STATE_DIR = ".leetcode-sync"
DEFAULT_STATE_FILE = "state.json"
DEFAULT_ENV_FILE = ".env"
DEFAULT_ENV_EXAMPLE_FILE = ".env.example"

# Environment variable names
ENV_LEETCODE_SESSION = "LEETCODE_SESSION"
ENV_LEETCODE_CSRF_TOKEN = "LEETCODE_CSRF_TOKEN"
ENV_LEETCODE_REPO_PATH = "LEETCODE_REPO_PATH"
ENV_GIT_AUTO_COMMIT = "GIT_AUTO_COMMIT"
ENV_GIT_AUTO_PUSH = "GIT_AUTO_PUSH"
ENV_WATCH_INTERVAL = "WATCH_INTERVAL"


def find_project_root() -> Path:
    """Find the project root directory.

    Walks up from the current directory looking for pyproject.toml or .git.
    Falls back to current directory.
    """
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    return current


def load_config(env_file: Path | None = None) -> AppConfig:
    """Load configuration from environment variables and optional .env file.

    Args:
        env_file: Path to .env file. If None, looks for .env in project root.

    Returns:
        AppConfig with values from environment.
    """
    if env_file is None:
        project_root = find_project_root()
        env_file = project_root / DEFAULT_ENV_FILE

    if env_file.exists():
        load_dotenv(env_file)

    return AppConfig(
        leetcode_session=os.getenv(ENV_LEETCODE_SESSION, ""),
        leetcode_csrf_token=os.getenv(ENV_LEETCODE_CSRF_TOKEN, ""),
        leetcode_repo_path=os.getenv(ENV_LEETCODE_REPO_PATH, ""),
        git_auto_commit=_parse_bool(os.getenv(ENV_GIT_AUTO_COMMIT, "false")),
        git_auto_push=_parse_bool(os.getenv(ENV_GIT_AUTO_PUSH, "false")),
        watch_interval=int(os.getenv(ENV_WATCH_INTERVAL, "120")),
    )


def get_state_path() -> Path:
    """Get the path to the state file."""
    project_root = find_project_root()
    state_dir = project_root / DEFAULT_STATE_DIR
    return state_dir / DEFAULT_STATE_FILE


def get_state_dir() -> Path:
    """Get the path to the state directory."""
    project_root = find_project_root()
    return project_root / DEFAULT_STATE_DIR


def create_env_example() -> None:
    """Create a .env.example file with documented environment variables."""
    content = f"""# leetcode-sync configuration
# Copy this file to .env and fill in your values.
# NEVER commit .env to version control.

# LeetCode authentication (required)
# Get these from your browser cookies when logged into LeetCode.
# See: leetcode-sync auth for instructions.
{ENV_LEETCODE_SESSION}=
{ENV_LEETCODE_CSRF_TOKEN}=

# Path to the LeetCode solutions repository (optional)
# If empty, uses the current directory.
{ENV_LEETCODE_REPO_PATH}=

# Auto-commit after sync (default: false)
{ENV_GIT_AUTO_COMMIT}=false

# Auto-push after commit (default: false)
{ENV_GIT_AUTO_PUSH}=false

# Watch mode polling interval in seconds (default: 120)
{ENV_WATCH_INTERVAL}=120
"""
    project_root = find_project_root()
    env_example_path = project_root / DEFAULT_ENV_EXAMPLE_FILE
    env_example_path.write_text(content)


def create_gitignore() -> None:
    """Create or update .gitignore with leetcode-sync entries."""
    project_root = find_project_root()
    gitignore_path = project_root / ".gitignore"

    entries_to_add = [
        ".env",
        ".leetcode-sync/",
        "__pycache__/",
        "*.pyc",
        ".mypy_cache/",
        ".ruff_cache/",
        ".pytest_cache/",
        "*.egg-info/",
        "dist/",
        "build/",
        ".venv/",
    ]

    existing_content = ""
    if gitignore_path.exists():
        existing_content = gitignore_path.read_text()

    new_entries = []
    for entry in entries_to_add:
        if entry not in existing_content:
            new_entries.append(entry)

    if new_entries:
        separator = "\n" if existing_content and not existing_content.endswith("\n") else ""
        with open(gitignore_path, "a") as f:
            f.write(separator + "\n".join(new_entries) + "\n")


def _parse_bool(value: str) -> bool:
    """Parse a string to boolean."""
    return value.lower() in ("true", "1", "yes", "on")

"""Tests for git manager."""

from pathlib import Path

import pytest

from leetcode_sync.git.manager import GitError, GitManager


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repository."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    manager = GitManager(repo_dir)
    manager.init_repo(repo_dir)
    # Configure git user for commits
    manager._run_git("config", "user.email", "test@test.com")
    manager._run_git("config", "user.name", "Test")
    return repo_dir


@pytest.fixture
def git_manager(git_repo: Path) -> GitManager:
    """Create a GitManager for the temporary repo."""
    return GitManager(git_repo)


class TestGitManager:
    """Tests for GitManager."""

    def test_is_git_repo(self, git_manager: GitManager):
        """Detects a git repository."""
        assert git_manager.is_git_repo() is True

    def test_not_git_repo(self, tmp_path: Path):
        """Detects non-git directory."""
        manager = GitManager(tmp_path)
        assert manager.is_git_repo() is False

    def test_get_current_branch(self, git_manager: GitManager):
        """Gets current branch name."""
        branch = git_manager.get_current_branch()
        # Default branch is either main or master
        assert branch in ("main", "master")

    def test_has_no_remote(self, git_manager: GitManager):
        """No remote by default."""
        assert git_manager.has_remote() is False

    def test_get_status_clean(self, git_manager: GitManager):
        """Clean repo has empty status."""
        status = git_manager.get_status()
        assert status == ""

    def test_get_changed_files(self, git_manager: GitManager, git_repo: Path):
        """Lists changed files."""
        (git_repo / "test.txt").write_text("hello")
        files = git_manager.get_changed_files()
        assert "test.txt" in files

    def test_stage_files(self, git_manager: GitManager, git_repo: Path):
        """Stages specific files."""
        (git_repo / "test.txt").write_text("hello")
        git_manager.stage_files(["test.txt"])
        result = git_manager._run_git("diff", "--cached", "--name-only")
        assert "test.txt" in result.stdout

    def test_commit(self, git_manager: GitManager, git_repo: Path):
        """Creates a commit."""
        (git_repo / "test.txt").write_text("hello")
        git_manager.stage_files(["test.txt"])
        result = git_manager.commit("Test commit")
        assert result is True

        log = git_manager._run_git("log", "--oneline", "-1")
        assert "Test commit" in log.stdout

    def test_commit_no_changes(self, git_manager: GitManager):
        """Returns False when nothing to commit."""
        result = git_manager.commit("Empty commit")
        assert result is False

    def test_has_uncommitted_changes(self, git_manager: GitManager, git_repo: Path):
        """Detects uncommitted changes."""
        assert git_manager.has_uncommitted_changes() is False
        (git_repo / "test.txt").write_text("hello")
        assert git_manager.has_uncommitted_changes() is True

    def test_init_repo(self, tmp_path: Path):
        """Initializes a new git repository."""
        repo_dir = tmp_path / "new_repo"
        manager = GitManager(tmp_path)
        manager.init_repo(repo_dir)
        assert (repo_dir / ".git").exists()

    def test_git_error_on_invalid_command(self, git_manager: GitManager):
        """Raises GitError for invalid git command."""
        with pytest.raises(GitError):
            git_manager._run_git("invalid-command-that-does-not-exist")

    def test_get_changed_files_with_untracked(
        self, git_manager: GitManager, git_repo: Path
    ):
        """Lists untracked files."""
        (git_repo / "new_file.txt").write_text("hello")
        files = git_manager.get_changed_files()
        assert "new_file.txt" in files

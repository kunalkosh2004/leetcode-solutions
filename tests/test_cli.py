"""Tests for CLI commands."""

import pytest
from typer.testing import CliRunner

from leetcode_sync.cli import app


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


class TestCLIHelp:
    """Tests for CLI help output."""

    def test_help(self, runner: CliRunner):
        """Shows help text."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "leetcode-sync" in result.output.lower()

    def test_version(self, runner: CliRunner):
        """Shows version."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_init_help(self, runner: CliRunner):
        """Shows init command help."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "Initialize" in result.output or "init" in result.output.lower()

    def test_auth_help(self, runner: CliRunner):
        """Shows auth command help."""
        result = runner.invoke(app, ["auth", "--help"])
        assert result.exit_code == 0
        assert "auth" in result.output.lower() or "LeetCode" in result.output

    def test_sync_help(self, runner: CliRunner):
        """Shows sync command help."""
        result = runner.invoke(app, ["sync", "--help"])
        assert result.exit_code == 0
        assert "sync" in result.output.lower()


class TestInitCommand:
    """Tests for init command."""

    def test_init_creates_directories(self, runner: CliRunner, tmp_path):
        """Init creates necessary directories."""
        result = runner.invoke(app, ["init", str(tmp_path / "project")])
        assert result.exit_code == 0

        project = tmp_path / "project"
        assert (project / "leetcode").exists()
        assert (project / "topics").exists()
        assert (project / ".leetcode-sync").exists()

    def test_init_creates_env_example(self, runner: CliRunner, tmp_path):
        """Init creates .env.example file."""
        project = tmp_path / "project"
        project.mkdir()
        result = runner.invoke(app, ["init", str(project)])
        assert result.exit_code == 0
        assert (project / ".env.example").exists()

    def test_init_shows_success(self, runner: CliRunner, tmp_path):
        """Init shows success message."""
        result = runner.invoke(app, ["init", str(tmp_path / "project")])
        assert result.exit_code == 0
        assert "complete" in result.output.lower() or "success" in result.output.lower()


class TestStatusCommand:
    """Tests for status command."""

    def test_status_shows_info(self, runner: CliRunner):
        """Status command shows project info."""
        result = runner.invoke(app, ["status"])
        # Should not crash, even if not initialized
        assert result.exit_code == 0

"""Tests for Pydantic data models."""

from datetime import datetime

from leetcode_sync.models import (
    AppConfig,
    Difficulty,
    Problem,
    Submission,
    SyncState,
)


class TestSubmission:
    """Tests for Submission model."""

    def test_creation(self):
        sub = Submission(
            submission_id="12345",
            question_id=1,
            title="Two Sum",
            title_slug="two-sum",
            status="Accepted",
            language="python3",
            timestamp=1234567890,
        )
        assert sub.submission_id == "12345"
        assert sub.is_accepted is True

    def test_not_accepted(self):
        sub = Submission(
            submission_id="12345",
            question_id=1,
            title="Two Sum",
            title_slug="two-sum",
            status="Wrong Answer",
            language="python3",
            timestamp=1234567890,
        )
        assert sub.is_accepted is False

    def test_submitted_at(self):
        sub = Submission(
            submission_id="12345",
            question_id=1,
            title="Two Sum",
            title_slug="two-sum",
            status="Accepted",
            language="python3",
            timestamp=1234567890,
        )
        assert isinstance(sub.submitted_at, datetime)


class TestProblem:
    """Tests for Problem model."""

    def test_creation(self):
        problem = Problem(
            id=1,
            number=1,
            title="Two Sum",
            slug="two-sum",
            difficulty=Difficulty.EASY,
            topics=["Array", "Hash Table"],
        )
        assert problem.number == 1
        assert problem.folder_name == "0001-two-sum"

    def test_folder_name_generation(self):
        problem = Problem(
            id=20,
            number=20,
            title="Valid Parentheses",
            slug="valid-parentheses",
            difficulty=Difficulty.EASY,
        )
        assert problem.folder_name == "0020-valid-parentheses"

    def test_large_number_folder_name(self):
        problem = Problem(
            id=1000,
            number=1000,
            title="Minimum Cost to Merge Stones",
            slug="minimum-cost-to-merge-stones",
            difficulty=Difficulty.HARD,
        )
        assert problem.folder_name == "1000-minimum-cost-to-merge-stones"


class TestSyncState:
    """Tests for SyncState model."""

    def test_initial_state(self):
        state = SyncState()
        assert state.processed_submissions == []
        assert state.is_processed("12345") is False

    def test_mark_processed(self):
        state = SyncState()
        state.mark_processed("12345")
        assert state.is_processed("12345") is True
        assert "12345" in state.processed_submissions

    def test_no_duplicates(self):
        state = SyncState()
        state.mark_processed("12345")
        state.mark_processed("12345")
        assert state.processed_submissions.count("12345") == 1

    def test_remove_processed(self):
        state = SyncState()
        state.mark_processed("12345")
        state.remove_processed("12345")
        assert state.is_processed("12345") is False

    def test_multiple_submissions(self):
        state = SyncState()
        state.mark_processed("111")
        state.mark_processed("222")
        state.mark_processed("333")
        assert len(state.processed_submissions) == 3
        assert state.is_processed("222") is True


class TestAppConfig:
    """Tests for AppConfig model."""

    def test_default_config(self):
        config = AppConfig()
        assert config.is_authenticated is False
        assert config.git_auto_commit is False
        assert config.watch_interval == 120

    def test_authenticated(self):
        config = AppConfig(leetcode_session="abc123")
        assert config.is_authenticated is True

    def test_empty_session(self):
        config = AppConfig(leetcode_session="")
        assert config.is_authenticated is False

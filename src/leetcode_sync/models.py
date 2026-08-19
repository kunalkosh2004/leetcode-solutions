"""Pydantic data models for leetcode-sync."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Difficulty(StrEnum):
    """Problem difficulty levels."""

    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class Submission(BaseModel):
    """A LeetCode submission record.

    This represents the minimal info returned when listing recent submissions.
    """

    submission_id: str
    question_id: int
    title: str
    title_slug: str
    status: str  # "Accepted", "Wrong Answer", etc.
    language: str
    timestamp: int = Field(description="Unix timestamp of submission")
    runtime: str | None = None
    memory: str | None = None

    @property
    def is_accepted(self) -> bool:
        """Check if this submission was accepted."""
        return self.status == "Accepted"

    @property
    def submitted_at(self) -> datetime:
        """Convert timestamp to datetime."""
        return datetime.fromtimestamp(self.timestamp)


class Problem(BaseModel):
    """Full problem metadata + submitted code.

    This is the complete data needed to generate a problem directory.
    """

    id: int = Field(description="LeetCode internal question ID")
    number: int = Field(description="Problem display number (e.g. 1, 20, 121)")
    title: str
    slug: str
    difficulty: Difficulty
    description: str = ""
    topics: list[str] = Field(default_factory=list)
    language: str = ""
    code: str = ""
    submission_id: str | None = None
    submitted_at: datetime | None = None
    status: str = "Accepted"

    @property
    def folder_name(self) -> str:
        """Generate the folder name for this problem."""
        from leetcode_sync.utils.slugify import problem_folder_name

        return problem_folder_name(self.number, self.title)


class SyncState(BaseModel):
    """Persistent state tracking which submissions have been processed."""

    processed_submissions: list[str] = Field(default_factory=list)
    last_sync_time: datetime | None = None
    version: int = 1

    def is_processed(self, submission_id: str) -> bool:
        """Check if a submission has already been processed."""
        return submission_id in self.processed_submissions

    def mark_processed(self, submission_id: str) -> None:
        """Mark a submission as processed."""
        if submission_id not in self.processed_submissions:
            self.processed_submissions.append(submission_id)

    def remove_processed(self, submission_id: str) -> None:
        """Remove a submission from the processed list."""
        self.processed_submissions = [
            sid for sid in self.processed_submissions if sid != submission_id
        ]


class AppConfig(BaseModel):
    """Application configuration loaded from environment/config files."""

    leetcode_session: str = ""
    leetcode_csrf_token: str = ""
    leetcode_repo_path: str = ""
    git_auto_commit: bool = False
    git_auto_push: bool = False
    watch_interval: int = 120  # seconds
    dry_run: bool = False

    @property
    def is_authenticated(self) -> bool:
        """Check if LeetCode authentication is configured."""
        return bool(self.leetcode_session)


class TopicStats(BaseModel):
    """Statistics for a topic."""

    topic: str
    problem_count: int
    problem_numbers: list[int] = Field(default_factory=list)


class SyncSummary(BaseModel):
    """Summary of a sync operation."""

    new_submissions: list[Problem] = Field(default_factory=list)
    skipped_submissions: int = 0
    errors: list[str] = Field(default_factory=list)
    directories_created: list[str] = Field(default_factory=list)
    files_updated: list[str] = Field(default_factory=list)
    topics_updated: list[str] = Field(default_factory=list)
    is_dry_run: bool = False

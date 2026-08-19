"""State persistence for tracking which submissions have been processed.

Stores state in .leetcode-sync/state.json within the project root.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from leetcode_sync.config import get_state_path
from leetcode_sync.models import SyncState


class StateManager:
    """Manages persistent sync state."""

    def __init__(self, state_path: Path | None = None) -> None:
        """Initialize state manager.

        Args:
            state_path: Custom path to state file. If None, uses default.
        """
        self.state_path = state_path or get_state_path()

    def load(self) -> SyncState:
        """Load state from disk.

        Returns:
            SyncState, or a fresh state if file doesn't exist.
        """
        if not self.state_path.exists():
            return SyncState()

        try:
            data = json.loads(self.state_path.read_text())
            return SyncState.model_validate(data)
        except (json.JSONDecodeError, Exception):
            # If state file is corrupted, start fresh
            return SyncState()

    def save(self, state: SyncState) -> None:
        """Save state to disk.

        Creates the directory structure if it doesn't exist.
        """
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        state.last_sync_time = datetime.now()

        data = state.model_dump(mode="json")
        self.state_path.write_text(json.dumps(data, indent=2) + "\n")

    def is_processed(self, submission_id: str) -> bool:
        """Check if a submission has been processed."""
        state = self.load()
        return state.is_processed(submission_id)

    def mark_processed(self, submission_id: str) -> None:
        """Mark a submission as processed and save."""
        state = self.load()
        state.mark_processed(submission_id)
        self.save(state)

    def remove_processed(self, submission_id: str) -> None:
        """Remove a submission from processed list and save."""
        state = self.load()
        state.remove_processed(submission_id)
        self.save(state)

    def get_all_processed(self) -> list[str]:
        """Get list of all processed submission IDs."""
        state = self.load()
        return list(state.processed_submissions)

    def reset(self) -> None:
        """Reset state to empty."""
        self.save(SyncState())

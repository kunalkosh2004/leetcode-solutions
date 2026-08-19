"""Tests for state management."""

from pathlib import Path

import pytest

from leetcode_sync.models import SyncState
from leetcode_sync.storage.state import StateManager


@pytest.fixture
def temp_state_path(tmp_path: Path) -> Path:
    """Create a temporary state file path."""
    return tmp_path / "state.json"


@pytest.fixture
def state_manager(temp_state_path: Path) -> StateManager:
    """Create a StateManager with a temporary path."""
    return StateManager(state_path=temp_state_path)


class TestStateManager:
    """Tests for StateManager."""

    def test_load_empty_state(self, state_manager: StateManager):
        """Loading from non-existent file returns empty state."""
        state = state_manager.load()
        assert state.processed_submissions == []
        assert state.last_sync_time is None

    def test_save_and_load(self, state_manager: StateManager):
        """Saving and loading preserves data."""
        state = SyncState()
        state.mark_processed("12345")
        state.mark_processed("67890")
        state_manager.save(state)

        loaded = state_manager.load()
        assert loaded.processed_submissions == ["12345", "67890"]

    def test_mark_processed(self, state_manager: StateManager):
        """Marking a submission as processed persists."""
        state_manager.mark_processed("111")
        assert state_manager.is_processed("111") is True

    def test_remove_processed(self, state_manager: StateManager):
        """Removing a submission from processed persists."""
        state_manager.mark_processed("111")
        state_manager.remove_processed("111")
        assert state_manager.is_processed("111") is False

    def test_get_all_processed(self, state_manager: StateManager):
        """Getting all processed submissions works."""
        state_manager.mark_processed("aaa")
        state_manager.mark_processed("bbb")
        processed = state_manager.get_all_processed()
        assert "aaa" in processed
        assert "bbb" in processed

    def test_reset(self, state_manager: StateManager):
        """Reset clears all state."""
        state_manager.mark_processed("111")
        state_manager.mark_processed("222")
        state_manager.reset()
        processed = state_manager.get_all_processed()
        assert processed == []

    def test_corrupted_state_file(self, state_manager: StateManager, temp_state_path: Path):
        """Corrupted state file returns empty state."""
        temp_state_path.write_text("not valid json {{{")
        state = state_manager.load()
        assert state.processed_submissions == []

    def test_creates_directory(self, tmp_path: Path):
        """State manager creates directory if it doesn't exist."""
        nested_path = tmp_path / "deep" / "nested" / "state.json"
        manager = StateManager(state_path=nested_path)
        state = SyncState()
        state.mark_processed("111")
        manager.save(state)
        assert nested_path.exists()

    def test_save_sets_last_sync_time(self, state_manager: StateManager):
        """Saving state sets the last_sync_time."""
        state = SyncState()
        state_manager.save(state)
        loaded = state_manager.load()
        assert loaded.last_sync_time is not None

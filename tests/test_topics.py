"""Tests for topic index generation."""

from pathlib import Path

import pytest

from leetcode_sync.generator.topics import (
    _build_stats_section,
    _gather_statistics,
    update_topic_indexes,
)
from leetcode_sync.models import Difficulty, Problem


@pytest.fixture
def two_sum_problem() -> Problem:
    """Two Sum problem fixture."""
    return Problem(
        id=1,
        number=1,
        title="Two Sum",
        slug="two-sum",
        difficulty=Difficulty.EASY,
        topics=["Array", "Hash Table"],
    )


@pytest.fixture
def reverse_linked_list_problem() -> Problem:
    """Reverse Linked List problem fixture."""
    return Problem(
        id=206,
        number=206,
        title="Reverse Linked List",
        slug="reverse-linked-list",
        difficulty=Difficulty.EASY,
        topics=["Linked List", "Recursion"],
    )


@pytest.fixture
def best_time_to_buy_problem() -> Problem:
    """Best Time to Buy and Sell Stock problem fixture."""
    return Problem(
        id=121,
        number=121,
        title="Best Time to Buy and Sell Stock",
        slug="best-time-to-buy-and-sell-stock",
        difficulty=Difficulty.EASY,
        topics=["Array", "Dynamic Programming"],
    )


class TestTopicIndexes:
    """Tests for topic index generation."""

    def test_creates_topic_file(
        self, tmp_path: Path, two_sum_problem: Problem
    ):
        """Creates a new topic file."""
        topics_dir = tmp_path / "topics"
        updated = update_topic_indexes(two_sum_problem, topics_dir)

        assert "array.md" in updated
        assert "hash-table.md" in updated

        array_file = topics_dir / "array.md"
        assert array_file.exists()
        content = array_file.read_text()
        assert "# Array" in content
        assert "1. Two Sum" in content

    def test_adds_multiple_problems(
        self,
        tmp_path: Path,
        two_sum_problem: Problem,
        best_time_to_buy_problem: Problem,
    ):
        """Adds multiple problems to the same topic."""
        topics_dir = tmp_path / "topics"

        update_topic_indexes(two_sum_problem, topics_dir)
        update_topic_indexes(best_time_to_buy_problem, topics_dir)

        array_file = topics_dir / "array.md"
        content = array_file.read_text()

        assert "1. Two Sum" in content
        assert "121. Best Time to Buy and Sell Stock" in content

    def test_sorted_by_number(
        self,
        tmp_path: Path,
        best_time_to_buy_problem: Problem,
        two_sum_problem: Problem,
    ):
        """Problems are sorted by number."""
        topics_dir = tmp_path / "topics"

        # Add in reverse order
        update_topic_indexes(best_time_to_buy_problem, topics_dir)
        update_topic_indexes(two_sum_problem, topics_dir)

        array_file = topics_dir / "array.md"
        content = array_file.read_text()
        entries = [
            line for line in content.split("\n")
            if line.startswith("- [")
        ]

        # Should be sorted: 1 before 121
        assert entries.index(
            "- [1. Two Sum](../leetcode/0001-two-sum/)"
        ) < entries.index(
            "- [121. Best Time to Buy and Sell Stock]"
            "(../leetcode/0121-best-time-to-buy-and-sell-stock/)"
        )

    def test_no_duplicates(
        self, tmp_path: Path, two_sum_problem: Problem
    ):
        """Adding the same problem twice doesn't create duplicates."""
        topics_dir = tmp_path / "topics"

        update_topic_indexes(two_sum_problem, topics_dir)
        update_topic_indexes(two_sum_problem, topics_dir)

        array_file = topics_dir / "array.md"
        content = array_file.read_text()
        count = content.count("1. Two Sum")
        assert count == 1

    def test_problems_in_multiple_topics(
        self, tmp_path: Path, two_sum_problem: Problem
    ):
        """A problem appears in all its topics."""
        topics_dir = tmp_path / "topics"
        update_topic_indexes(two_sum_problem, topics_dir)

        assert (topics_dir / "array.md").exists()
        assert (topics_dir / "hash-table.md").exists()

    def test_different_topics_different_files(
        self,
        tmp_path: Path,
        two_sum_problem: Problem,
        reverse_linked_list_problem: Problem,
    ):
        """Different topics get different files."""
        topics_dir = tmp_path / "topics"

        update_topic_indexes(two_sum_problem, topics_dir)
        update_topic_indexes(reverse_linked_list_problem, topics_dir)

        assert (topics_dir / "array.md").exists()
        assert (topics_dir / "hash-table.md").exists()
        assert (topics_dir / "linked-list.md").exists()
        assert (topics_dir / "recursion.md").exists()

    def test_problem_without_topics(self, tmp_path: Path):
        """Problem with no topics doesn't create any files."""
        problem = Problem(
            id=1,
            number=1,
            title="Two Sum",
            slug="two-sum",
            difficulty=Difficulty.EASY,
            topics=[],
        )
        topics_dir = tmp_path / "topics"
        updated = update_topic_indexes(problem, topics_dir)
        assert updated == []


class TestStatistics:
    """Tests for statistics gathering and building."""

    def test_build_stats_section(self):
        """Builds correct stats markdown."""
        stats = {
            "difficulty_counts": {
                "Easy": 10, "Medium": 5, "Hard": 2,
            },
            "topic_counts": {
                "Array": 8, "Hash Table": 5,
                "Linked List": 3,
            },
            "total": 17,
        }
        section = _build_stats_section(stats)

        assert "| Easy | 10 |" in section
        assert "| Medium | 5 |" in section
        assert "| Hard | 2 |" in section
        assert "| Total | 17 |" in section
        assert "| Array | 8 |" in section

    def test_build_stats_empty(self):
        """Builds stats with zero problems."""
        stats = {
            "difficulty_counts": {
                "Easy": 0, "Medium": 0, "Hard": 0,
            },
            "topic_counts": {},
            "total": 0,
        }
        section = _build_stats_section(stats)
        assert "| Total | 0 |" in section
        assert "## Topics" not in section

    def test_gather_statistics_empty_dir(self, tmp_path: Path):
        """Gathering stats from empty directory."""
        problems_dir = tmp_path / "leetcode"
        problems_dir.mkdir()
        topics_dir = tmp_path / "topics"
        topics_dir.mkdir()

        stats = _gather_statistics(problems_dir, topics_dir)
        assert stats["total"] == 0

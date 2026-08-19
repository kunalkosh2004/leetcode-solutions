"""Tests for solution and README generators."""

from pathlib import Path

import pytest

from leetcode_sync.generator.readme import generate_readme
from leetcode_sync.generator.solution import generate_solution_file
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
        description="Given an array of integers nums and an integer target...",
        topics=["Array", "Hash Table"],
        language="python3",
        code="class Solution:\n    def twoSum(self, nums, target):\n        pass",
        submission_id="12345",
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
        description="Given the head of a singly linked list...",
        topics=["Linked List", "Recursion"],
        language="python3",
        code="class Solution:\n    def reverseList(self, head):\n        pass",
        submission_id="12346",
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
        description="You are given an array prices...",
        topics=["Array", "Dynamic Programming"],
        language="python3",
        code="class Solution:\n    def maxProfit(self, prices):\n        pass",
        submission_id="12347",
    )


class TestSolutionGenerator:
    """Tests for solution file generation."""

    def test_generate_python_solution(
        self, tmp_path: Path, two_sum_problem: Problem
    ):
        """Generates a Python solution file."""
        output_dir = tmp_path / "0001-two-sum"
        output_dir.mkdir()
        filepath = generate_solution_file(two_sum_problem, output_dir)

        assert filepath.exists()
        assert filepath.name == "solution.py"
        content = filepath.read_text()
        assert "def twoSum" in content

    def test_generate_cpp_solution(self, tmp_path: Path):
        """Generates a C++ solution file."""
        problem = Problem(
            id=1,
            number=1,
            title="Two Sum",
            slug="two-sum",
            difficulty=Difficulty.EASY,
            language="cpp",
            code=(
                "class Solution {\npublic:\n"
                "    vector<int> twoSum(vector<int>& nums,"
                " int target) {}\n};"
            ),
        )
        output_dir = tmp_path / "0001-two-sum"
        output_dir.mkdir()
        filepath = generate_solution_file(problem, output_dir)

        assert filepath.exists()
        assert filepath.name == "solution.cpp"

    def test_generate_java_solution(self, tmp_path: Path):
        """Generates a Java solution file with PascalCase."""
        problem = Problem(
            id=1,
            number=1,
            title="Two Sum",
            slug="two-sum",
            difficulty=Difficulty.EASY,
            language="java",
            code="class Solution { public int[] twoSum(int[] nums, int target) {} }",
        )
        output_dir = tmp_path / "0001-two-sum"
        output_dir.mkdir()
        filepath = generate_solution_file(problem, output_dir)

        assert filepath.exists()
        assert filepath.name == "Solution.java"

    def test_no_overwrite_without_force(
        self, tmp_path: Path, two_sum_problem: Problem
    ):
        """Raises FileExistsError when file exists with different content."""
        output_dir = tmp_path / "0001-two-sum"
        output_dir.mkdir()
        generate_solution_file(two_sum_problem, output_dir)

        # Create a problem with different code
        different_problem = two_sum_problem.model_copy(
            update={
                "code": (
                    "class Solution:\n"
                    "    def twoSum(self, nums, target):\n"
                    "        return []"
                )
            }
        )

        with pytest.raises(FileExistsError):
            generate_solution_file(different_problem, output_dir, force=False)

    def test_overwrite_with_force(
        self, tmp_path: Path, two_sum_problem: Problem
    ):
        """Overwrites existing file when force is True."""
        output_dir = tmp_path / "0001-two-sum"
        output_dir.mkdir()
        generate_solution_file(two_sum_problem, output_dir)

        # Should not raise
        filepath = generate_solution_file(two_sum_problem, output_dir, force=True)
        assert filepath.exists()

    def test_same_content_no_error(
        self, tmp_path: Path, two_sum_problem: Problem
    ):
        """Writing same content doesn't raise an error."""
        output_dir = tmp_path / "0001-two-sum"
        output_dir.mkdir()
        filepath1 = generate_solution_file(two_sum_problem, output_dir)
        filepath2 = generate_solution_file(two_sum_problem, output_dir, force=False)
        assert filepath1 == filepath2


class TestReadmeGenerator:
    """Tests for README generation."""

    def test_generate_readme(
        self, tmp_path: Path, two_sum_problem: Problem
    ):
        """Generates a README with correct content."""
        output_dir = tmp_path / "0001-two-sum"
        output_dir.mkdir()
        filepath = generate_readme(two_sum_problem, output_dir)

        assert filepath.exists()
        content = filepath.read_text()

        assert "# 1. Two Sum" in content
        assert "Easy" in content
        assert "Array" in content
        assert "Hash Table" in content
        assert "solution.py" in content

    def test_readme_no_overwrite(
        self, tmp_path: Path, two_sum_problem: Problem
    ):
        """Raises FileExistsError when README exists."""
        output_dir = tmp_path / "0001-two-sum"
        output_dir.mkdir()
        generate_readme(two_sum_problem, output_dir)

        with pytest.raises(FileExistsError):
            generate_readme(two_sum_problem, output_dir, force=False)

    def test_readme_with_no_topics(self, tmp_path: Path):
        """Generates README when problem has no topics."""
        problem = Problem(
            id=1,
            number=1,
            title="Two Sum",
            slug="two-sum",
            difficulty=Difficulty.EASY,
        )
        output_dir = tmp_path / "0001-two-sum"
        output_dir.mkdir()
        filepath = generate_readme(problem, output_dir)

        content = filepath.read_text()
        assert "No topics available" in content

    def test_readme_approach_placeholder(
        self, tmp_path: Path, two_sum_problem: Problem
    ):
        """README contains placeholder for approach."""
        output_dir = tmp_path / "0001-two-sum"
        output_dir.mkdir()
        filepath = generate_readme(two_sum_problem, output_dir)

        content = filepath.read_text()
        assert "Approach documentation not generated yet" in content

    def test_readme_complexity_placeholder(
        self, tmp_path: Path, two_sum_problem: Problem
    ):
        """README contains placeholder for complexity."""
        output_dir = tmp_path / "0001-two-sum"
        output_dir.mkdir()
        filepath = generate_readme(two_sum_problem, output_dir)

        content = filepath.read_text()
        assert "O(?)" in content

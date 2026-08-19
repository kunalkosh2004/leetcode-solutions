"""README generator for problem documentation.

Creates a standardized README.md for each problem.
Does not hallucinate algorithm explanations or complexity.
"""

from __future__ import annotations

from pathlib import Path

from leetcode_sync.models import Problem
from leetcode_sync.utils.slugify import solution_filename


def generate_readme(
    problem: Problem,
    output_dir: Path,
    force: bool = False,
) -> Path:
    """Generate a README.md for a problem.

    Args:
        problem: Problem metadata.
        output_dir: Directory to write the README to.
        force: If True, overwrite existing README.

    Returns:
        Path to the created README file.

    Raises:
        FileExistsError: If file exists and force is False.
    """
    readme_path = output_dir / "README.md"

    if readme_path.exists() and not force:
        raise FileExistsError(
            f"README already exists: {readme_path}\n"
            "Use --force to overwrite."
        )

    # Build topics list
    topics_section = ""
    if problem.topics:
        topics_lines = [f"- {topic}" for topic in problem.topics]
        topics_section = "\n".join(topics_lines)
    else:
        topics_section = "- No topics available"

    # Build the solution reference
    solution_ref = solution_filename(problem.language or "python")

    # Build description section
    description = problem.description
    if not description:
        description = "> Problem description not available yet."

    content = f"""# {problem.number}. {problem.title}

## Difficulty

{problem.difficulty.value}

## Topics

{topics_section}

## Problem

{description}

## Approach

> Approach documentation not generated yet.

## Complexity

- Time: O(?)
- Space: O(?)

## Solution

See `{solution_ref}`.
"""

    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(content, encoding="utf-8")

    return readme_path

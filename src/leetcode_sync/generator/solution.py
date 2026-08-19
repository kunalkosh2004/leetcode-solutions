"""Solution file generator.

Creates solution files in the appropriate language.
Does not modify the user's algorithm code.
"""

from __future__ import annotations

from pathlib import Path

from leetcode_sync.models import Problem
from leetcode_sync.utils.slugify import solution_filename


def generate_solution_file(
    problem: Problem,
    output_dir: Path,
    force: bool = False,
) -> Path:
    """Generate the solution file for a problem.

    Args:
        problem: Problem with code to save.
        output_dir: Directory to write the solution file to.
        force: If True, overwrite existing files.

    Returns:
        Path to the created solution file.

    Raises:
        FileExistsError: If file exists and force is False.
    """
    filename = solution_filename(problem.language or "python")
    filepath = output_dir / filename

    if filepath.exists() and not force:
        # Check if content is different
        existing = filepath.read_text(encoding="utf-8")
        if existing == problem.code:
            return filepath  # No change needed
        raise FileExistsError(
            f"Solution file already exists: {filepath}\n"
            "Use --force to overwrite."
        )

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(problem.code, encoding="utf-8")

    return filepath

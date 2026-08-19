"""Topic index generator.

Creates and updates topic index files and root README statistics.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from leetcode_sync.config import find_project_root
from leetcode_sync.models import Problem
from leetcode_sync.utils.slugify import topic_filename


def update_topic_indexes(
    problem: Problem,
    topics_dir: Path,
) -> list[str]:
    """Update topic index files for a problem.

    Creates or updates topic markdown files in the topics/ directory.

    Args:
        problem: The problem to add to topic indexes.
        topics_dir: Path to the topics/ directory.

    Returns:
        List of topic filenames that were updated.
    """
    topics_dir.mkdir(parents=True, exist_ok=True)
    updated = []

    for topic in problem.topics:
        filename = topic_filename(topic)
        filepath = topics_dir / filename
        entry = f"- [{problem.number}. {problem.title}](../leetcode/{problem.folder_name}/)"

        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            # Check if this problem is already listed
            pattern = rf"^- \[{problem.number}\."
            if re.search(pattern, content, re.MULTILINE):
                continue  # Already listed

            # Add the entry and re-sort
            lines = content.strip().split("\n")
            # Find all problem entries (lines starting with "- [")
            header_lines = [line for line in lines if not line.startswith("- [")]
            problem_entries = [line for line in lines if line.startswith("- [")]

            problem_entries.append(entry)
            # Sort by problem number
            problem_entries.sort(
                key=lambda x: int(re.search(r"\[(\d+)\.", x).group(1))  # type: ignore[union-attr]
            )

            content = "\n".join(header_lines + problem_entries) + "\n"
        else:
            content = f"# {topic}\n\n{entry}\n"

        filepath.write_text(content, encoding="utf-8")
        updated.append(filename)

    return updated


def update_root_readme(
    problems_dir: Path,
    topics_dir: Path,
    project_root: Path | None = None,
) -> None:
    """Update the root README.md with statistics.

    Only replaces content between the generated markers.
    Preserves manually written content outside the markers.

    Args:
        problems_dir: Path to the leetcode/ directory with solutions.
        topics_dir: Path to the topics/ directory.
        project_root: Root directory. If None, auto-detects.
    """
    if project_root is None:
        project_root = find_project_root()

    readme_path = project_root / "README.md"

    # Gather statistics from existing problem directories
    stats = _gather_statistics(problems_dir, topics_dir)

    # Build the stats section
    stats_section = _build_stats_section(stats)

    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")
    else:
        content = "# LeetCode Solutions\n\nMy LeetCode solutions and problem-solving notes.\n"

    # Replace content between markers
    marker_start = "<!-- LEETCODE_STATS_START -->"
    marker_end = "<!-- LEETCODE_STATS_END -->"

    if marker_start in content and marker_end in content:
        # Replace existing stats section
        pattern = rf"{re.escape(marker_start)}.*?{re.escape(marker_end)}"
        replacement = f"{marker_start}\n{stats_section}\n{marker_end}"
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # Append stats section at the end
        content = content.rstrip() + f"\n\n{marker_start}\n{stats_section}\n{marker_end}\n"

    readme_path.write_text(content, encoding="utf-8")


def _gather_statistics(
    problems_dir: Path,
    topics_dir: Path,
) -> dict[str, Any]:
    """Gather statistics from problem directories.

    Returns:
        Dict with difficulty counts, topic counts, etc.
    """
    difficulty_counts: dict[str, int] = {"Easy": 0, "Medium": 0, "Hard": 0}
    topic_counts: dict[str, int] = defaultdict(int)
    total = 0

    if not problems_dir.exists():
        return {
            "difficulty_counts": difficulty_counts,
            "topic_counts": dict(topic_counts),
            "total": 0,
        }

    # Scan problem directories for README files
    for problem_dir in sorted(problems_dir.iterdir()):
        if not problem_dir.is_dir():
            continue
        readme = problem_dir / "README.md"
        if not readme.exists():
            continue

        content = readme.read_text(encoding="utf-8")
        total += 1

        # Extract difficulty
        for diff in ["Easy", "Medium", "Hard"]:
            if f"## Difficulty\n\n{diff}" in content:
                difficulty_counts[diff] += 1
                break

        # Extract topics
        in_topics = False
        for line in content.split("\n"):
            if line.strip() == "## Topics":
                in_topics = True
                continue
            if in_topics and line.startswith("## "):
                break
            if in_topics and line.startswith("- "):
                topic = line[2:].strip()
                if topic and topic != "No topics available":
                    topic_counts[topic] += 1

    return {
        "difficulty_counts": difficulty_counts,
        "topic_counts": dict(topic_counts),
        "total": total,
    }


def _build_stats_section(stats: dict[str, Any]) -> str:
    """Build the stats markdown section."""
    difficulty_counts = stats["difficulty_counts"]
    topic_counts = stats["topic_counts"]
    total = stats["total"]

    lines = [
        "## Progress",
        "",
        "| Difficulty | Solved |",
        "|------------|--------|",
        f"| Easy | {difficulty_counts.get('Easy', 0)} |",
        f"| Medium | {difficulty_counts.get('Medium', 0)} |",
        f"| Hard | {difficulty_counts.get('Hard', 0)} |",
        f"| Total | {total} |",
    ]

    if topic_counts:
        # Sort topics by count descending
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        lines.extend([
            "",
            "## Topics",
            "",
            "| Topic | Problems |",
            "|-------|----------|",
        ])
        for topic, count in sorted_topics:
            lines.append(f"| {topic} | {count} |")

    return "\n".join(lines)

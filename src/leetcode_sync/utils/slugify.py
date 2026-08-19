"""Slugification utilities for problem titles and folder names."""

from __future__ import annotations

import re
import unicodedata


def slugify_title(title: str) -> str:
    """Convert a problem title to a URL/filesystem-friendly slug.

    Examples:
        "Two Sum" -> "two-sum"
        "Add Two Numbers" -> "add-two-numbers"
        "Longest Substring..." -> "longest-substring..."
    """
    # Normalize unicode characters
    title = unicodedata.normalize("NFKD", title)

    # Convert to lowercase
    title = title.lower()

    # Replace non-alphanumeric characters (except hyphens) with hyphens
    title = re.sub(r"[^a-z0-9]+", "-", title)

    # Strip leading/trailing hyphens
    title = title.strip("-")

    # Collapse multiple hyphens
    title = re.sub(r"-+", "-", title)

    return title


def problem_folder_name(number: int, title: str) -> str:
    """Generate the folder name for a problem.

    Format: {number:04d}-{slugified-title}

    Examples:
        (1, "Two Sum") -> "0001-two-sum"
        (20, "Valid Parentheses") -> "0020-valid-parentheses"
        (121, "Best Time...") -> "0121-best-time-to-buy-and-sell-stock"
        (1000, "Minimum Cost to Merge Stones") -> "1000-minimum-cost-to-merge-stones"
    """
    slug = slugify_title(title)
    return f"{number:04d}-{slug}"


def language_extension(language: str) -> str:
    """Map a LeetCode language to a file extension.

    Examples:
        "python" -> "py"
        "python3" -> "py"
        "cpp" -> "cpp"
        "java" -> "java"
        "javascript" -> "js"
        "typescript" -> "ts"
        "go" -> "go"
        "rust" -> "rs"
    """
    mapping: dict[str, str] = {
        "python": "py",
        "python3": "py",
        "cpp": "cpp",
        "c++": "cpp",
        "java": "java",
        "javascript": "js",
        "js": "js",
        "typescript": "ts",
        "ts": "ts",
        "go": "go",
        "rust": "rs",
        "c": "c",
        "c#": "cs",
        "csharp": "cs",
        "kotlin": "kt",
        "swift": "swift",
        "ruby": "rb",
        "scala": "scala",
        "php": "php",
        "r": "r",
        "dart": "dart",
    }
    lang_lower = language.lower().strip()
    return mapping.get(lang_lower, lang_lower)


def solution_filename(language: str) -> str:
    """Generate the solution filename for a language.

    Examples:
        "python3" -> "solution.py"
        "cpp" -> "solution.cpp"
        "java" -> "Solution.java"
        "javascript" -> "solution.js"
        "go" -> "solution.go"
        "rust" -> "solution.rs"
    """
    ext = language_extension(language)
    lang_lower = language.lower().strip()

    # Java uses PascalCase convention
    if lang_lower in ("java",):
        return f"Solution.{ext}"

    return f"solution.{ext}"


def topic_filename(topic: str) -> str:
    """Convert a topic tag to a filename for the topics index.

    Examples:
        "Array" -> "array.md"
        "Hash Table" -> "hash-table.md"
        "Dynamic Programming" -> "dynamic-programming.md"
        "Breadth-First Search" -> "breadth-first-search.md"
    """
    return f"{slugify_title(topic)}.md"

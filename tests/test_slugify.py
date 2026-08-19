"""Tests for slugification utilities."""


from leetcode_sync.utils.slugify import (
    language_extension,
    problem_folder_name,
    slugify_title,
    solution_filename,
    topic_filename,
)


class TestSlugifyTitle:
    """Tests for title slugification."""

    def test_simple_title(self):
        assert slugify_title("Two Sum") == "two-sum"

    def test_multi_word_title(self):
        assert slugify_title("Add Two Numbers") == "add-two-numbers"

    def test_long_title(self):
        assert (
            slugify_title("Longest Substring Without Repeating Characters")
            == "longest-substring-without-repeating-characters"
        )

    def test_title_with_numbers(self):
        assert slugify_title("Two Sum") == "two-sum"

    def test_title_with_special_chars(self):
        assert slugify_title("A^2 + B^2 = C^2") == "a-2-b-2-c-2"

    def test_single_word(self):
        assert slugify_title("Palindrome") == "palindrome"

    def test_already_lowercase(self):
        assert slugify_title("two sum") == "two-sum"

    def test_empty_string(self):
        assert slugify_title("") == ""

    def test_title_with_hyphens(self):
        assert slugify_title("Top-K Frequent Elements") == "top-k-frequent-elements"


class TestProblemFolderName:
    """Tests for problem folder name generation."""

    def test_small_number(self):
        assert problem_folder_name(1, "Two Sum") == "0001-two-sum"

    def test_medium_number(self):
        assert problem_folder_name(20, "Valid Parentheses") == "0020-valid-parentheses"

    def test_large_number(self):
        assert (
            problem_folder_name(121, "Best Time to Buy and Sell Stock")
            == "0121-best-time-to-buy-and-sell-stock"
        )

    def test_four_digit_number(self):
        assert (
            problem_folder_name(1000, "Minimum Cost to Merge Stones")
            == "1000-minimum-cost-to-merge-stones"
        )

    def test_five_digit_number(self):
        assert (
            problem_folder_name(10000, "Some Problem")
            == "10000-some-problem"
        )


class TestLanguageExtension:
    """Tests for language extension mapping."""

    def test_python(self):
        assert language_extension("python") == "py"

    def test_python3(self):
        assert language_extension("python3") == "py"

    def test_cpp(self):
        assert language_extension("cpp") == "cpp"

    def test_cplusplus(self):
        assert language_extension("c++") == "cpp"

    def test_java(self):
        assert language_extension("java") == "java"

    def test_javascript(self):
        assert language_extension("javascript") == "js"

    def test_typescript(self):
        assert language_extension("typescript") == "ts"

    def test_go(self):
        assert language_extension("go") == "go"

    def test_rust(self):
        assert language_extension("rust") == "rs"

    def test_unknown_language(self):
        assert language_extension("brainfuck") == "brainfuck"


class TestSolutionFilename:
    """Tests for solution filename generation."""

    def test_python(self):
        assert solution_filename("python") == "solution.py"

    def test_python3(self):
        assert solution_filename("python3") == "solution.py"

    def test_cpp(self):
        assert solution_filename("cpp") == "solution.cpp"

    def test_java(self):
        assert solution_filename("java") == "Solution.java"

    def test_javascript(self):
        assert solution_filename("javascript") == "solution.js"

    def test_go(self):
        assert solution_filename("go") == "solution.go"

    def test_rust(self):
        assert solution_filename("rust") == "solution.rs"


class TestTopicFilename:
    """Tests for topic filename generation."""

    def test_simple_topic(self):
        assert topic_filename("Array") == "array.md"

    def test_multi_word_topic(self):
        assert topic_filename("Hash Table") == "hash-table.md"

    def test_complex_topic(self):
        assert topic_filename("Dynamic Programming") == "dynamic-programming.md"

    def test_bfs_topic(self):
        assert topic_filename("Breadth-First Search") == "breadth-first-search.md"

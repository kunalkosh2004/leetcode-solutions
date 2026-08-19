"""LeetCode API client.

All LeetCode API interaction is isolated here.
The rest of the application should not know how LeetCode's API works.

Authentication uses browser session cookies (LEETCODE_SESSION + CSRF token).
No username/password authentication is used.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from leetcode_sync.config import AppConfig
from leetcode_sync.leetcode.graphql import (
    PROBLEM_DETAIL_QUERY,
    RECENT_AC_SUBMISSIONS_QUERY,
    SUBMISSION_DETAIL_QUERY,
    USER_INFO_QUERY,
)
from leetcode_sync.models import Difficulty, Problem, Submission

logger = logging.getLogger(__name__)

# LeetCode API endpoints
LEETCODE_BASE_URL = "https://leetcode.com"
LEETCODE_GRAPHQL_URL = f"{LEETCODE_BASE_URL}/graphql"


class LeetCodeAuthError(Exception):
    """Raised when authentication with LeetCode fails."""


class LeetCodeAPIError(Exception):
    """Raised when a LeetCode API call fails."""


class LeetCodeClient:
    """Client for interacting with the LeetCode API.

    Uses cookie-based authentication. Never logs or exposes credentials.
    """

    def __init__(self, config: AppConfig) -> None:
        """Initialize the client with configuration.

        Args:
            config: Application configuration with LeetCode credentials.
        """
        self.config = config
        self._client: httpx.Client | None = None

    @property
    def _headers(self) -> dict[str, str]:
        """Build request headers with authentication cookies."""
        headers = {
            "Content-Type": "application/json",
            "Referer": f"{LEETCODE_BASE_URL}/",
            "Origin": LEETCODE_BASE_URL,
        }
        if self.config.leetcode_session:
            headers["Cookie"] = (
                f"LEETCODE_SESSION={self.config.leetcode_session}"
            )
        if self.config.leetcode_csrf_token:
            headers["x-csrftoken"] = self.config.leetcode_csrf_token
        return headers

    def _get_client(self) -> httpx.Client:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                base_url=LEETCODE_BASE_URL,
                headers=self._headers,
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            self._client.close()

    def __enter__(self) -> LeetCodeClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _graphql_query(
        self, query: str, variables: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a GraphQL query against LeetCode.

        Args:
            query: GraphQL query string.
            variables: Query variables.

        Returns:
            Response data dict.

        Raises:
            LeetCodeAuthError: If authentication fails.
            LeetCodeAPIError: If the API request fails.
        """
        client = self._get_client()

        try:
            response = client.post(
                LEETCODE_GRAPHQL_URL,
                json={"query": query, "variables": variables},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise LeetCodeAuthError(
                    "Authentication failed. Your LeetCode session may have expired.\n"
                    "Run: leetcode-sync auth"
                ) from e
            raise LeetCodeAPIError(
                f"LeetCode API error: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            raise LeetCodeAPIError(
                f"Network error connecting to LeetCode: {e}"
            ) from e

        data = response.json()
        if "errors" in data:
            raise LeetCodeAPIError(
                f"LeetCode GraphQL error: {data['errors']}"
            )
        return data.get("data", {})

    def verify_auth(self) -> str | None:
        """Verify authentication by fetching current user info.

        Returns:
            Username if authenticated, None otherwise.
        """
        try:
            data = self._graphql_query(USER_INFO_QUERY, {"username": ""})
            user = data.get("matchedUser")
            if user:
                return user.get("username")
        except Exception:
            pass
        return None

    def get_recent_submissions(self, limit: int = 20) -> list[Submission]:
        """Get recent accepted submissions.

        Uses the authenticated submission list endpoint.

        Args:
            limit: Maximum number of submissions to fetch.

        Returns:
            List of Submission objects.
        """
        data = self._graphql_query(
            RECENT_AC_SUBMISSIONS_QUERY,
            {
                "offset": 0,
                "limit": limit,
                "status": "AC",
            },
        )

        submissions = []
        submission_list = data.get("submissionList", {})
        raw_submissions = submission_list.get("submissions", [])

        for raw in raw_submissions:
            question = raw.get("question", {})
            submissions.append(
                Submission(
                    submission_id=str(raw.get("id", "")),
                    question_id=int(question.get("questionId", 0)),
                    title=question.get("title", ""),
                    title_slug=question.get("titleSlug", ""),
                    status=raw.get("statusDisplay", ""),
                    language=raw.get("lang", ""),
                    timestamp=int(raw.get("timestamp", 0)),
                    runtime=raw.get("runtime"),
                    memory=raw.get("memory"),
                )
            )

        return submissions

    def get_submission_detail(self, submission_id: str) -> dict[str, Any] | None:
        """Get detailed submission info including source code.

        Args:
            submission_id: The submission ID.

        Returns:
            Dict with submission details, or None if not found.
        """
        try:
            data = self._graphql_query(
                SUBMISSION_DETAIL_QUERY, {"submissionId": submission_id}
            )
            return data.get("submissionDetail")
        except Exception as e:
            logger.warning("Failed to fetch submission %s: %s", submission_id, e)
            return None

    def get_problem(self, title_slug: str) -> Problem | None:
        """Get full problem metadata by title slug.

        Args:
            title_slug: The problem's URL slug.

        Returns:
            Problem object, or None if not found.
        """
        data = self._graphql_query(
            PROBLEM_DETAIL_QUERY, {"titleSlug": title_slug}
        )

        question = data.get("question")
        if not question:
            return None

        topics = [
            tag.get("name", "")
            for tag in question.get("topicTags", [])
            if tag.get("name")
        ]

        difficulty_str = question.get("difficulty", "Medium")
        try:
            difficulty = Difficulty(difficulty_str)
        except ValueError:
            difficulty = Difficulty.MEDIUM

        return Problem(
            id=int(question.get("questionId", 0)),
            number=int(question.get("questionFrontendId", 0)),
            title=question.get("title", ""),
            slug=question.get("titleSlug", ""),
            difficulty=difficulty,
            description=question.get("content", ""),
            topics=topics,
        )

    def get_problem_with_submission(
        self, submission: Submission
    ) -> Problem | None:
        """Fetch full problem data including the submitted code.

        Args:
            submission: The Submission to enrich.

        Returns:
            Problem with code filled in, or None.
        """
        # First get problem metadata
        problem = self.get_problem(submission.title_slug)
        if not problem:
            return None

        # Then get submission detail for source code
        detail = self.get_submission_detail(submission.submission_id)
        if detail and detail.get("source"):
            problem.code = detail["source"]
            problem.language = detail.get("lang", submission.language)
            problem.submission_id = submission.submission_id
        else:
            problem.language = submission.language

        # Set timestamp
        from datetime import datetime

        problem.submitted_at = datetime.fromtimestamp(submission.timestamp)

        return problem

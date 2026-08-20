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
    USER_STATUS_QUERY,
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
    def _cookies(self) -> dict[str, str]:
        """Build cookies dict with authentication."""
        cookies: dict[str, str] = {}
        if self.config.leetcode_session:
            cookies["LEETCODE_SESSION"] = self.config.leetcode_session
        if self.config.leetcode_csrf_token:
            cookies["csrftoken"] = self.config.leetcode_csrf_token
        return cookies

    @property
    def _headers(self) -> dict[str, str]:
        """Build request headers."""
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Referer": f"{LEETCODE_BASE_URL}/",
            "Origin": LEETCODE_BASE_URL,
        }
        if self.config.leetcode_csrf_token:
            headers["x-csrftoken"] = self.config.leetcode_csrf_token
        return headers

    def _get_client(self) -> httpx.Client:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                base_url=LEETCODE_BASE_URL,
                headers=self._headers,
                cookies=self._cookies,
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
        except httpx.RequestError as e:
            raise LeetCodeAPIError(
                f"Network error connecting to LeetCode: {e}"
            ) from e

        if response.status_code != 200:
            body = response.text[:500]
            logger.debug(
                "LeetCode API %d response: %s",
                response.status_code,
                body,
            )
            if response.status_code == 401:
                raise LeetCodeAuthError(
                    "Authentication failed. Your LeetCode session may have expired.\n"
                    "Run: leetcode-sync auth"
                )
            raise LeetCodeAPIError(
                f"LeetCode API error: {response.status_code} - {body}"
            )

        data = response.json()
        if "errors" in data:
            error_msgs = [
                e.get("message", str(e)) for e in data["errors"]
            ]
            raise LeetCodeAPIError(
                f"LeetCode GraphQL error: {'; '.join(error_msgs)}"
            )
        return data.get("data", {})

    def get_current_username(self) -> str | None:
        """Get the currently authenticated username.

        Uses the userStatus query which requires no arguments.

        Returns:
            Username if authenticated, None otherwise.
        """
        try:
            data = self._graphql_query(USER_STATUS_QUERY, {})
            status = data.get("userStatus", {})
            if status.get("isSignedIn") and status.get("username"):
                return status["username"]
        except Exception:
            pass
        return None

    def verify_auth(self) -> str | None:
        """Verify authentication by fetching current user info.

        Returns:
            Username if authenticated, None otherwise.
        """
        return self.get_current_username()

    def get_recent_submissions(
        self, limit: int = 20
    ) -> list[Submission]:
        """Get recent accepted submissions.

        Uses the recentAcSubmissionList query which returns
        accepted submissions for the authenticated user.

        Args:
            limit: Maximum number of submissions to fetch.

        Returns:
            List of Submission objects.
        """
        # Get current username first
        username = self.verify_auth()
        if not username:
            raise LeetCodeAuthError(
                "Could not determine authenticated username.\n"
                "Your session may have expired. Run: leetcode-sync auth"
            )

        data = self._graphql_query(
            RECENT_AC_SUBMISSIONS_QUERY,
            {"username": username, "limit": limit},
        )

        submissions = []
        raw_list = data.get("recentAcSubmissionList", [])

        for raw in raw_list:
            submissions.append(
                Submission(
                    submission_id=str(raw.get("id", "")),
                    question_id=0,  # Not available in this query
                    title=raw.get("title", ""),
                    title_slug=raw.get("titleSlug", ""),
                    status="Accepted",
                    language=raw.get("lang", ""),
                    timestamp=int(raw.get("timestamp", 0)),
                    runtime=None,
                    memory=None,
                )
            )

        return submissions

    def get_submission_detail(
        self, submission_id: str
    ) -> dict[str, Any] | None:
        """Get detailed submission info including source code.

        Args:
            submission_id: The submission ID.

        Returns:
            Dict with submission details, or None if not found.
        """
        try:
            data = self._graphql_query(
                SUBMISSION_DETAIL_QUERY,
                {"submissionId": int(submission_id)},
            )
            return data.get("submissionDetails")
        except Exception as e:
            logger.warning(
                "Failed to fetch submission %s: %s",
                submission_id,
                e,
            )
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
        if detail and detail.get("code"):
            problem.code = detail["code"]
            # lang is now a LanguageNode object
            lang_info = detail.get("lang")
            if isinstance(lang_info, dict):
                problem.language = lang_info.get(
                    "verboseName", submission.language
                )
            else:
                problem.language = submission.language
            problem.submission_id = submission.submission_id
        else:
            problem.language = submission.language

        # Set timestamp
        from datetime import datetime

        problem.submitted_at = datetime.fromtimestamp(
            submission.timestamp
        )

        return problem

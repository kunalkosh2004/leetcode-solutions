"""GraphQL queries for the LeetCode API.

All LeetCode API interaction queries are isolated here.
This makes it easy to update queries when LeetCode changes their API.
"""

from __future__ import annotations

# Query to get recent submissions for a user
RECENT_SUBMISSIONS_QUERY = """
query recentAcSubmissions($username: String!) {
    recentAcSubmissions(limit: 20, username: $username) {
        id
        title
        titleSlug
        timestamp
        lang
    }
}
"""

# Query to get problem details by slug
PROBLEM_DETAIL_QUERY = """
query problemsetQuestionDetail($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        questionId
        questionFrontendId
        title
        titleSlug
        difficulty
        content
        topicTags {
            name
            slug
        }
        codeSnippets {
            lang
            langSlug
            code
        }
    }
}
"""

# Query to get submission detail (includes source code)
SUBMISSION_DETAIL_QUERY = """
query submissionDetail($submissionId: ID!) {
    submissionDetail(submissionId: $submissionId) {
        id
        question {
            questionId
            questionFrontendId
            title
            titleSlug
            difficulty
            topicTags {
                name
            }
        }
        statusDisplay
        lang
        source
        timestamp
    }
}
"""

# Query to get current user info (for verification)
USER_INFO_QUERY = """
query userPublicProfile($username: String!) {
    matchedUser(username: $username) {
        username
        profile {
            realName
            userAvatar
        }
    }
}
"""

# Query to get user's recent AC submissions (authenticated)
RECENT_AC_SUBMISSIONS_QUERY = """
query submissionList(
    $offset: Int!
    $limit: Int!
    $status: SubmissionStatusEnum
) {
    submissionList(
        offset: $offset
        limit: $limit
        status: $status
    ) {
        lastKey
        hasNext
        submissions {
            id
            statusDisplay
            lang
            runtime
            memory
            timestamp
            question {
                questionId
                titleSlug
                title
                translatedTitle
            }
        }
    }
}
"""

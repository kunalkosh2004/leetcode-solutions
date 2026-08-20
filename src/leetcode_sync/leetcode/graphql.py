"""GraphQL queries for the LeetCode API.

All LeetCode API interaction queries are isolated here.
This makes it easy to update queries when LeetCode changes their API.
"""

from __future__ import annotations

# Query to get user's recent AC submissions (authenticated)
# recentAcSubmissionList requires username and limit
RECENT_AC_SUBMISSIONS_QUERY = """
query recentAcSubmissionList($username: String!, $limit: Int!) {
    recentAcSubmissionList(username: $username, limit: $limit) {
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
# Note: field is submissionDetails (plural), submissionId is Int!, lang is LanguageNode!
SUBMISSION_DETAIL_QUERY = """
query submissionDetail($submissionId: Int!) {
    submissionDetails(submissionId: $submissionId) {
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
        lang {
            name
            verboseName
        }
        code
        timestamp
    }
}
"""

# Query to get current signed-in user status (no args needed)
USER_STATUS_QUERY = """
query userStatus {
    userStatus {
        username
        isSignedIn
    }
}
"""

# Query to get user profile by username
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

# Query to get user's recent submissions (authenticated, with full question data)
RECENT_SUBMISSIONS_QUERY = """
query submissionList($offset: Int!, $limit: Int!) {
    submissionList(offset: $offset, limit: $limit) {
        lastKey
        hasNext
        submissions {
            id
            statusDisplay
            lang
            runtime
            memory
            timestamp
            url
        }
    }
}
"""

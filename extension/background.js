// leetcode-sync Chrome Extension
// Detects accepted LeetCode submissions and notifies the local server

const SERVER_URL = "http://127.0.0.1:8901";
const CHECK_ENDPOINT = `${SERVER_URL}/submit`;
const HEALTH_ENDPOINT = `${SERVER_URL}/health`;

// Track recently processed submissions to avoid duplicates
const recentSubmissions = new Set();

// Listen for responses from leetcode.com GraphQL API
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    if (details.method !== "POST") return;
    if (!details.requestBody?.raw) return;

    try {
      const decoder = new TextDecoder("utf-8");
      const body = decoder.decode(
        new Uint8Array(details.requestBody.raw[0].bytes)
      );
      const data = JSON.parse(body);

      // Check if this is a submission detail request
      if (data.query && data.query.includes("submissionDetails")) {
        const submissionId = data.variables?.submissionId;
        if (submissionId && !recentSubmissions.has(submissionId)) {
          recentSubmissions.add(submissionId);

          // Clean up old entries after 5 minutes
          setTimeout(() => recentSubmissions.delete(submissionId), 300000);

          // Fetch the submission details
          fetchSubmissionDetails(submissionId);
        }
      }
    } catch (e) {
      // Not a JSON request or parsing error, ignore
    }
  },
  {
    urls: ["https://leetcode.com/graphql/"],
  },
  ["requestBody"]
);

// Also listen for navigation to submission result pages
chrome.webRequest.onCompleted.addListener(
  (details) => {
    if (details.method !== "POST") return;

    try {
      // Check response for accepted submission
      // This is a secondary detection method
    } catch (e) {
      // Ignore
    }
  },
  {
    urls: ["https://leetcode.com/graphql/"],
  },
  ["responseHeaders"]
);

// Fetch submission details and check if accepted
async function fetchSubmissionDetails(submissionId) {
  try {
    // We need to get the submission details from leetcode.com
    // But we can also just notify the server and let it handle it
    // For now, let's notify with the submission ID

    // Actually, we need to figure out what was submitted
    // Let's intercept the response instead
  } catch (e) {
    console.error("[leetcode-sync] Error fetching submission:", e);
  }
}

// Listen for responses from LeetCode GraphQL
chrome.webRequest.onCompleted.addListener(
  (details) => {
    if (details.method !== "POST") return;
    if (!details.url.includes("graphql")) return;

    // We need the response body to check if it's accepted
    // Chrome extensions can't read response bodies from onCompleted
    // So we use a different approach: inject content script
  },
  { urls: ["https://leetcode.com/*"] }
);

// Alternative approach: Content script sends us messages
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SUBMISSION_ACCEPTED") {
    notifyServer(message.data);
    sendResponse({ status: "ok" });
  }
  return true;
});

// Notify the local leetcode-sync server
async function notifyServer(submissionData) {
  try {
    const response = await fetch(CHECK_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(submissionData),
    });

    const result = await response.json();
    console.log("[leetcode-sync] Server response:", result);

    // Update badge
    chrome.action.setBadgeText({ text: "✓" });
    chrome.action.setBadgeBackgroundColor({ color: "#22c55e" });
    setTimeout(() => chrome.action.setBadgeText({ text: "" }), 3000);
  } catch (e) {
    console.error("[leetcode-sync] Server not reachable:", e);
    chrome.action.setBadgeText({ text: "!" });
    chrome.action.setBadgeBackgroundColor({ color: "#ef4444" });
    setTimeout(() => chrome.action.setBadgeText({ text: "" }), 5000);
  }
}

// Check server health on startup
async function checkServerHealth() {
  try {
    const response = await fetch(HEALTH_ENDPOINT);
    const data = await response.json();
    if (data.status === "ok") {
      console.log("[leetcode-sync] Server is running");
      chrome.action.setBadgeText({ text: "●" });
      chrome.action.setBadgeBackgroundColor({ color: "#22c55e" });
      setTimeout(() => chrome.action.setBadgeText({ text: "" }), 2000);
    }
  } catch (e) {
    console.warn("[leetcode-sync] Server not running. Start with: leetcode-sync serve");
  }
}

// Check health when extension loads
checkServerHealth();

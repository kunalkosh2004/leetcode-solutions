// leetcode-sync Content Script
// Runs on LeetCode pages and detects accepted submissions

(function () {
  "use strict";

  // Track if we've already sent this submission
  const sentSubmissions = new Set();

  // Intercept fetch/ XMLHttpRequest to detect submissions
  const originalFetch = window.fetch;

  window.fetch = async function (...args) {
    const response = await originalFetch.apply(this, args);

    // Check if this is a submission request
    const url = typeof args[0] === "string" ? args[0] : args[0]?.url;
    if (url && url.includes("/graphql")) {
      try {
        const cloned = response.clone();
        const data = await cloned.json();

        // Check for accepted submission in response
        if (data?.data?.submissionDetails) {
          const detail = data.data.submissionDetails;
          if (
            detail.statusDisplay === "Accepted" ||
            detail.status === "Accepted"
          ) {
            const submissionData = {
              titleSlug: detail.question?.titleSlug || "",
              title: detail.question?.title || "",
              submissionId: detail.id || "",
              questionId: detail.question?.questionFrontendId || "",
            };

            if (
              submissionData.titleSlug &&
              !sentSubmissions.has(submissionData.submissionId)
            ) {
              sentSubmissions.add(submissionData.submissionId);
              console.log(
                "[leetcode-sync] Detected accepted submission:",
                submissionData.title
              );

              // Notify background script
              chrome.runtime.sendMessage({
                type: "SUBMISSION_ACCEPTED",
                data: submissionData,
              });
            }
          }
        }
      } catch (e) {
        // Not a submission response, ignore
      }
    }

    return response;
  };

  // Also intercept XMLHttpRequest
  const originalXHROpen = XMLHttpRequest.prototype.open;
  const originalXHRSend = XMLHttpRequest.prototype.send;

  XMLHttpRequest.prototype.open = function (method, url, ...rest) {
    this._leetcodeSyncUrl = url;
    return originalXHROpen.call(this, method, url, ...rest);
  };

  XMLHttpRequest.prototype.send = function (...args) {
    this.addEventListener("load", function () {
      try {
        if (
          this._leetcodeSyncUrl &&
          this._leetcodeSyncUrl.includes("/graphql")
        ) {
          const data = JSON.parse(this.responseText);

          if (data?.data?.submissionDetails) {
            const detail = data.data.submissionDetails;
            if (
              detail.statusDisplay === "Accepted" ||
              detail.status === "Accepted"
            ) {
              const submissionData = {
                titleSlug: detail.question?.titleSlug || "",
                title: detail.question?.title || "",
                submissionId: detail.id || "",
                questionId: detail.question?.questionFrontendId || "",
              };

              if (
                submissionData.titleSlug &&
                !sentSubmissions.has(submissionData.submissionId)
              ) {
                sentSubmissions.add(submissionData.submissionId);
                console.log(
                  "[leetcode-sync] Detected accepted submission:",
                  submissionData.title
                );

                chrome.runtime.sendMessage({
                  type: "SUBMISSION_ACCEPTED",
                  data: submissionData,
                });
              }
            }
          }
        }
      } catch (e) {
        // Ignore
      }
    });

    return originalXHRSend.apply(this, args);
  };

  // Also detect via DOM: LeetCode shows a green "Accepted" badge
  // Use MutationObserver as a fallback
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType !== 1) continue; // Skip non-element nodes

        // Look for accepted submission result
        const acceptedEl = node.querySelector?.(
          '[data-e2e-locator="submission-result"]:has-text("Accepted"), ' +
            '.text-green-s'.replace("-", "\\-") +
            ", " +
            '[class*="accepted"]'
        );

        // More reliable: check for the submission result text
        if (node.textContent?.includes("Accepted") && node.closest?.("[class*='result']")) {
          // Try to extract title from URL
          const urlMatch = window.location.pathname.match(/\/problems\/([^/]+)/);
          if (urlMatch) {
            const titleSlug = urlMatch[1];
            const submissionData = {
              titleSlug: titleSlug,
              title: titleSlug.replace(/-/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
              submissionId: Date.now().toString(), // Fallback ID
              questionId: "",
            };

            if (!sentSubmissions.has(submissionData.submissionId)) {
              // Debounce: only send once per slug per page load
              const key = `seen_${titleSlug}`;
              if (!sessionStorage.getItem(key)) {
                sessionStorage.setItem(key, "true");
                chrome.runtime.sendMessage({
                  type: "SUBMISSION_ACCEPTED",
                  data: submissionData,
                });
              }
            }
          }
        }
      }
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });

  console.log("[leetcode-sync] Content script loaded ✓");
})();

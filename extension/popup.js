// leetcode-sync Popup Script

const SERVER_URL = "http://127.0.0.1:8901";

async function checkHealth() {
  const statusEl = document.getElementById("status");
  const statusText = document.getElementById("status-text");

  try {
    const response = await fetch(`${SERVER_URL}/health`);
    const data = await response.json();

    if (data.status === "ok") {
      statusEl.className = "status connected";
      statusText.textContent = "Connected to leetcode-sync server";
    } else {
      throw new Error("Bad response");
    }
  } catch (e) {
    statusEl.className = "status disconnected";
    statusText.textContent = "Server not running";
  }
}

async function forceSync() {
  const statusEl = document.getElementById("status");
  const statusText = document.getElementById("status-text");

  try {
    statusText.textContent = "Syncing...";
    statusEl.className = "status connected";

    // Get current LeetCode page info
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });

    let titleSlug = "";
    if (tab?.url) {
      const match = tab.url.match(/\/problems\/([^/]+)/);
      if (match) titleSlug = match[1];
    }

    const response = await fetch(`${SERVER_URL}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        titleSlug: titleSlug,
        title: titleSlug
          ? titleSlug.replace(/-/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())
          : "",
        submissionId: Date.now().toString(),
        questionId: "",
      }),
    });

    const result = await response.json();
    statusText.textContent = `Sync started!`;
  } catch (e) {
    statusEl.className = "status disconnected";
    statusText.textContent = "Server not reachable";
  }
}

document.getElementById("check-btn").addEventListener("click", checkHealth);
document.getElementById("sync-btn").addEventListener("click", forceSync);

// Check health on load
checkHealth();

/**
 * chrome-extension/background.js
 * Service worker that manages tab creation and coordinates cross-tab actions.
 */

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message && message.action === "play_youtube") {
    const songQuery = message.song || "lofi hip hop radio beats to relax study to";
    console.log("[QT-Agent Background] Creating real Chrome tab for song:", songQuery);

    const targetUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(songQuery)}`;

    chrome.tabs.create({ url: targetUrl }, (tab) => {
      // Store pending task in extension storage for the new YouTube tab
      chrome.storage.local.set({
        pendingTask: {
          tabId: tab.id,
          action: "play_youtube",
          song: songQuery,
          timestamp: Date.now()
        }
      }, () => {
        console.log("[QT-Agent Background] Pending task saved for tab:", tab.id);
        sendResponse({ status: "tab_created", tabId: tab.id, song: songQuery });
      });
    });

    return true; // Keep message channel open for async response
  }
});

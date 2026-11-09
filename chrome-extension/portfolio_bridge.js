/**
 * chrome-extension/portfolio_bridge.js
 * Injected on http://localhost:8000/*
 * Bridges communication between the portfolio Command HUD and the extension background worker.
 */

(function () {
  console.log("[QT-Agent Extension Bridge] Active on portfolio page!");

  // Mark extension as installed in the page context
  window.__QT_AGENT_EXTENSION_INSTALLED = true;
  window.postMessage({ type: "QT_AGENT_EXTENSION_DETECTED", version: "1.0.0" }, "*");

  // Listen for commands from the web page (agent_pointer.js)
  window.addEventListener("message", (event) => {
    if (event.source !== window) return;
    if (event.data && event.data.type === "QT_AGENT_CROSS_TAB_COMMAND") {
      console.log("[QT-Agent Extension Bridge] Forwarding command to background:", event.data);
      try {
        chrome.runtime.sendMessage(event.data, (response) => {
          console.log("[QT-Agent Extension Bridge] Background response:", response);
        });
      } catch (err) {
        console.warn("[QT-Agent Extension Bridge] SendMessage error:", err);
      }
    }
  });
})();

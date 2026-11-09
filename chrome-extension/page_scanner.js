/**
 * chrome-extension/page_scanner.js
 * In-Browser Perception Scanner
 * Dynamically extracts visible interactive elements on any webpage
 * so the LLM can "see" the page layout and plan pointer actions.
 */

window.QTPageScanner = (function () {
  let trackedElementsMap = [];

  function scanInteractiveElements() {
    trackedElementsMap = [];
    const elementsData = [];

    // Selectors for interactive affordances across all modern web apps
    const candidates = document.querySelectorAll(`
      input, textarea, select,
      button, [role="button"],
      a[href], [role="link"],
      [role="tab"], [role="searchbox"],
      [role="menuitem"], [role="switch"],
      ytd-video-renderer, [data-interactive="true"]
    `);

    let count = 0;
    for (const el of candidates) {
      if (count >= 35) break;

      // Visibility check
      const rect = el.getBoundingClientRect();
      if (rect.width < 12 || rect.height < 10) continue;
      if (rect.bottom < 0 || rect.top > window.innerHeight * 1.5) continue; // on or near screen

      const style = window.getComputedStyle(el);
      if (style.display === "none" || style.visibility === "hidden" || parseFloat(style.opacity) < 0.1) continue;

      // Clean semantic text
      let text = (el.innerText || el.textContent || el.value || el.getAttribute("aria-label") || el.getAttribute("title") || "").trim();
      text = text.replace(/\s+/g, " ").slice(0, 80);

      // Save mapping
      const id = count++;
      trackedElementsMap[id] = el;

      elementsData.push({
        id: id,
        tag: el.tagName.toLowerCase(),
        role: el.getAttribute("role") || (el.tagName === "INPUT" ? "input" : el.tagName === "BUTTON" ? "button" : "link"),
        text: text,
        placeholder: el.getAttribute("placeholder") || "",
        aria: el.getAttribute("aria-label") || "",
        x: rect.left,
        y: rect.top,
        w: rect.width,
        h: rect.height
      });
    }

    console.log(`[QTPageScanner] Scanned ${elementsData.length} interactive elements on ${window.location.hostname}`);
    return elementsData;
  }

  function getElementById(id) {
    return trackedElementsMap[id] || null;
  }

  return {
    scan: scanInteractiveElements,
    getElement: getElementById
  };
})();

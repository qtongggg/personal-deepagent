/**
 * chrome-extension/youtube_companion.js
 * Content script running on https://*.youtube.com/*
 * Orchestrates the live companion pointer animation, auto-typing, and playback execution.
 */

(function () {
  console.log("[QT-Agent YouTube Companion] Content script initialized on YouTube.");

  chrome.storage.local.get("pendingTask", (result) => {
    const task = result && result.pendingTask;
    if (!task) return;

    // Check if task is recent (< 60s)
    const isRecent = Date.now() - (task.timestamp || 0) < 60000;
    if (!isRecent || task.action !== "play_youtube") return;

    // Clear task immediately so it only executes once
    chrome.storage.local.remove("pendingTask");

    const songName = task.song || "lofi hip hop radio beats to relax study to";
    console.log("[QT-Agent YouTube Companion] Executing cross-tab task for song:", songName);

    // Wait until document is ready
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => startCrossTabExecution(songName));
    } else {
      setTimeout(() => startCrossTabExecution(songName), 800);
    }
  });

  function startCrossTabExecution(songQuery) {
    // 1. Build TrustedHTML-safe DOM structure
    const wrap = document.createElement("div");
    wrap.id = "cross-tab-agent-pointer";

    const body = document.createElement("div");
    body.className = "cross-pointer-body";

    // SVG Cursor Arrow
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "cross-pointer-svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", "M4 4L11 20L14 13L21 10L4 4Z");
    path.setAttribute("fill", "#ff5c00");
    path.setAttribute("stroke", "#ffffff");
    path.setAttribute("stroke-width", "2.2");
    path.setAttribute("stroke-linejoin", "round");
    svg.appendChild(path);
    body.appendChild(svg);

    // Ripple
    const ripple = document.createElement("div");
    ripple.className = "cross-pointer-ripple";
    body.appendChild(ripple);

    // Badge
    const badge = document.createElement("div");
    badge.className = "cross-pointer-badge";
    const dot = document.createElement("span");
    dot.className = "cross-badge-dot";
    const badgeText = document.createElement("span");
    badgeText.textContent = "● QT-AGENT GUIDE";
    badge.appendChild(dot);
    badge.appendChild(badgeText);
    body.appendChild(badge);

    // State Pill
    const statePill = document.createElement("div");
    statePill.className = "cross-pointer-state";
    statePill.textContent = "[ 🌐 CROSSED OVER TO YOUTUBE ]";
    body.appendChild(statePill);

    // Thought Bubble
    const bubble = document.createElement("div");
    bubble.className = "cross-pointer-bubble";
    const bTitle = document.createElement("div");
    bTitle.className = "cross-bubble-title";
    bTitle.textContent = "CROSS-TAB AGENT";
    const bText = document.createElement("div");
    bText.className = "cross-bubble-text";
    bText.textContent = "Arrived from your portfolio!";
    bubble.appendChild(bTitle);
    bubble.appendChild(bText);
    body.appendChild(bubble);

    wrap.appendChild(body);
    document.body.appendChild(wrap);

    const controller = {
      moveTo(x, y, duration = 650) {
        wrap.style.transition = `transform ${duration}ms cubic-bezier(0.16, 1, 0.3, 1)`;
        wrap.style.transform = `translate3d(${Math.round(x)}px, ${Math.round(y)}px, 0)`;
      },
      setState(txt) {
        statePill.textContent = txt;
      },
      speak(title, text) {
        bTitle.textContent = title;
        bText.textContent = text;
        bubble.classList.add("is-visible");
      },
      hideSpeech() {
        bubble.classList.remove("is-visible");
      },
      clickRipple() {
        ripple.classList.remove("is-clicking");
        void ripple.offsetWidth;
        ripple.classList.add("is-clicking");
      }
    };

    // Begin Animation Choreography
    setTimeout(async () => {
      // Step 1: Pointer enters from top of tab
      controller.moveTo(window.innerWidth / 2, 75, 800);
      controller.setState("[ 🌐 Arrived From Portfolio Tab ]");
      controller.speak("CROSS-TAB AGENT", "I have crossed over from your portfolio tab! Searching for your song...");

      await sleep(1500);

      // Step 2: Locate YouTube search input
      const searchBox = document.querySelector("input[name='search_query'], input#search");
      if (searchBox) {
        const boxRect = searchBox.getBoundingClientRect();
        const targetX = boxRect.left + 45;
        const targetY = boxRect.top + boxRect.height / 2;

        controller.moveTo(targetX, targetY, 700);
        await sleep(750);

        controller.clickRipple();
        searchBox.focus();

        controller.setState("[ ⌨️ Auto-Typing Song... ]");
        controller.hideSpeech();

        // Auto-type song character-by-character
        searchBox.value = "";
        for (let i = 0; i < songQuery.length; i++) {
          searchBox.value += songQuery[i];
          searchBox.dispatchEvent(new Event("input", { bubbles: true }));
          await sleep(35);
        }

        await sleep(300);

        // Step 3: Glide to search button and click
        const searchBtn = document.querySelector("button#search-icon-legacy, button[aria-label='Search']");
        if (searchBtn) {
          const btnRect = searchBtn.getBoundingClientRect();
          const btnX = btnRect.left + btnRect.width / 2;
          const btnY = btnRect.top + btnRect.height / 2;
          controller.moveTo(btnX, btnY, 500);
          await sleep(550);
          controller.clickRipple();
        }

        // Submit search
        const form = searchBox.closest("form");
        if (form) {
          form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
        } else {
          searchBox.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", keyCode: 13, bubbles: true }));
        }

        await sleep(2600);

        // Step 4: Click first video
        const firstVideo = document.querySelector("ytd-video-renderer #video-title, #contents ytd-video-renderer a#thumbnail");
        if (firstVideo) {
          const vidRect = firstVideo.getBoundingClientRect();
          const vidX = vidRect.left + 80;
          const vidY = vidRect.top + vidRect.height / 2;

          controller.moveTo(vidX, vidY, 700);
          await sleep(750);
          controller.clickRipple();
          firstVideo.click();
        }

        await sleep(1800);
        controller.setState("[ 🎵 Playing on YouTube ]");
        controller.speak("AGENT DJ 🎧", `Now playing "${songQuery}" on YouTube! Enjoy the music!`);

        setTimeout(() => {
          controller.hideSpeech();
        }, 5000);
      }
    }, 600);
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
})();

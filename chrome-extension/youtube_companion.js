/**
 * chrome-extension/youtube_companion.js
 * Content script running on https://*.youtube.com/*
 * Orchestrates the live companion pointer animation, auto-typing, and playback execution.
 */

(function () {
  console.log("[QT-Agent YouTube Companion] Content script active on:", window.location.href);

  // Check for pending task
  chrome.storage.local.get(["pendingTask", "playingNotice"], (result) => {
    // 1. If currently loading a video watch page that was triggered by the agent
    if (result && result.playingNotice && window.location.pathname === "/watch") {
      const song = result.playingNotice.song || "music";
      chrome.storage.local.remove("playingNotice");
      renderWatchCelebration(song);
      return;
    }

    // 2. If a search/play task is pending
    const task = result && result.pendingTask;
    if (!task) return;

    const isRecent = Date.now() - (task.timestamp || 0) < 90000;
    if (!isRecent || task.action !== "play_youtube") return;

    // Clear task so it executes once
    chrome.storage.local.remove("pendingTask");

    const songQuery = task.song || "lofi hip hop radio beats to relax study to";
    console.log("[QT-Agent YouTube Companion] Executing pointer choreo for:", songQuery);

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => runPointerChoreography(songQuery));
    } else {
      setTimeout(() => runPointerChoreography(songQuery), 600);
    }
  });

  function createPointerDOM() {
    if (document.getElementById("cross-tab-agent-pointer")) {
      return document.getElementById("cross-tab-agent-pointer").__controller;
    }

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
      wrap,
      state: statePill,
      bubble,
      bubbleTitle: bTitle,
      bubbleText: bText,
      ripple,
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

    wrap.__controller = controller;
    return controller;
  }

  async function runPointerChoreography(songQuery) {
    const controller = createPointerDOM();

    // STEP 1: Enter from top of the screen
    controller.moveTo(window.innerWidth / 2, 80, 800);
    controller.setState("[ 🌐 Crossed Tab // YouTube ]");
    controller.speak("CROSS-TAB AGENT", `Arrived from your portfolio! Locating top video for "${songQuery}"...`);

    await sleep(1400);

    // STEP 2: Glide into YouTube search box and auto-type
    const searchBox = document.querySelector("input[name='search_query'], input#search, div#search-input input");
    if (searchBox) {
      const boxRect = searchBox.getBoundingClientRect();
      controller.moveTo(boxRect.left + 50, boxRect.top + boxRect.height / 2, 700);
      await sleep(750);

      controller.clickRipple();
      searchBox.focus();

      controller.setState("[ ⌨️ Auto-Typing Song... ]");
      controller.hideSpeech();

      searchBox.value = "";
      for (let i = 0; i < songQuery.length; i++) {
        searchBox.value += songQuery[i];
        searchBox.dispatchEvent(new Event("input", { bubbles: true }));
        await sleep(30);
      }
      await sleep(350);
    }

    // STEP 3: Wait and locate first video in search results
    controller.setState("[ 🎯 Locating Top Video... ]");
    const videoSelectors = [
      "ytd-video-renderer a#video-title",
      "ytd-video-renderer a#thumbnail",
      "#contents ytd-video-renderer a#video-title",
      "ytd-video-renderer #title-wrapper a"
    ];

    const firstVideo = await waitForElement(videoSelectors, 12000);

    if (firstVideo) {
      console.log("[QT-Agent] Found first video element:", firstVideo);
      const vidRect = firstVideo.getBoundingClientRect();
      const targetX = Math.max(100, Math.min(vidRect.left + 80, window.innerWidth - 200));
      const targetY = Math.max(80, Math.min(vidRect.top + vidRect.height / 2, window.innerHeight - 150));

      controller.moveTo(targetX, targetY, 750);
      await sleep(800);

      controller.clickRipple();
      controller.setState("[ 🎵 Launching Video Playback... ]");
      controller.speak("AGENT DJ 🎧", `Playing "${songQuery}" on YouTube! Enjoy the music!`);

      // Store notice so the watch page also displays celebration
      chrome.storage.local.set({
        playingNotice: { song: songQuery, timestamp: Date.now() }
      });

      await sleep(400);

      // Perform robust click
      firstVideo.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true, view: window }));
      if (firstVideo.href) {
        window.location.href = firstVideo.href;
      } else {
        firstVideo.click();
      }
    } else {
      console.warn("[QT-Agent] Video element not found within timeout.");
      controller.setState("[ 🎵 Ready to Play ]");
      controller.speak("AGENT DJ 🎧", `Search completed for "${songQuery}". Click any video to play!`);
    }
  }

  function renderWatchCelebration(song) {
    setTimeout(() => {
      const controller = createPointerDOM();
      controller.moveTo(window.innerWidth / 2, 90, 800);
      controller.setState("[ 🎵 Playing on YouTube ]");
      controller.speak("AGENT DJ 🎧", `Now playing "${song}"! Sit back and enjoy the music!`);

      setTimeout(() => {
        controller.hideSpeech();
        if (controller.wrap) {
          controller.wrap.style.opacity = "0.2";
          controller.wrap.style.transition = "opacity 1.5s ease";
        }
      }, 5000);
    }, 1200);
  }

  async function waitForElement(selectors, timeoutMs = 10000) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      for (const sel of selectors) {
        const el = document.querySelector(sel);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.width > 0 && rect.height > 0) {
            return el;
          }
        }
      }
      await sleep(200);
    }
    return null;
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
})();

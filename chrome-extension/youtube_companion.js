/**
 * chrome-extension/youtube_companion.js
 * Content script running on https://*.youtube.com/*
 * Detects the QT-Agent hash command, animates the companion pointer across the page,
 * glides to the top video, triggers shockwave ripples, and clicks the video to play.
 */

(function () {
  console.log("[QT-Agent YouTube Companion] Active on:", window.location.href);

  // 1. Extract song query from URL hash or storage
  let songQuery = "";
  const hash = window.location.hash || "";
  if (hash.includes("qt_agent_play=")) {
    songQuery = decodeURIComponent(hash.split("qt_agent_play=")[1].split("&")[0]);
    // Clean hash from address bar without reloading
    try {
      history.replaceState(null, "", window.location.pathname + window.location.search);
    } catch (e) {}
  }

  if (songQuery) {
    initCompanionPointer(songQuery);
  } else {
    // Check extension storage as fallback
    if (chrome && chrome.storage && chrome.storage.local) {
      chrome.storage.local.get(["pendingTask", "playingNotice"], (result) => {
        if (result && result.playingNotice && window.location.pathname === "/watch") {
          const song = result.playingNotice.song || "music";
          chrome.storage.local.remove("playingNotice");
          renderWatchCelebration(song);
          return;
        }

        const task = result && result.pendingTask;
        if (task && task.action === "play_youtube") {
          const isRecent = Date.now() - (task.timestamp || 0) < 90000;
          if (isRecent) {
            chrome.storage.local.remove("pendingTask");
            initCompanionPointer(task.song || "lofi beats");
          }
        }
      });
    }
  }

  function initCompanionPointer(song) {
    console.log("[QT-Agent] Starting pointer choreography for song:", song);
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => startChoreography(song));
    } else {
      setTimeout(() => startChoreography(song), 500);
    }
  }

  function createPointerDOM() {
    let wrap = document.getElementById("cross-tab-agent-pointer");
    if (wrap && wrap.__controller) return wrap.__controller;

    wrap = document.createElement("div");
    wrap.id = "cross-tab-agent-pointer";

    const body = document.createElement("div");
    body.className = "cross-pointer-body";

    // Cyber-Orange SVG Arrow Cursor
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

    // Shockwave Ripple
    const ripple = document.createElement("div");
    ripple.className = "cross-pointer-ripple";
    body.appendChild(ripple);

    // Multiplayer Badge
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

    // Speech / Thought Bubble
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

  async function startChoreography(song) {
    const controller = createPointerDOM();

    // 1. Enter from top edge of tab
    controller.moveTo(window.innerWidth / 2, 85, 750);
    controller.setState("[ 🌐 Crossed Tab // YouTube ]");
    controller.speak("CROSS-TAB AGENT", `Arrived from your portfolio! Selecting top video for "${song}"...`);

    await sleep(1200);

    // 2. Poll for the first video in the search results
    controller.setState("[ 🎯 Locating Top Video... ]");
    const videoSelectors = [
      "ytd-video-renderer a#video-title",
      "ytd-video-renderer a#thumbnail",
      "#contents ytd-video-renderer a#video-title",
      "ytd-video-renderer #title-wrapper a",
      "ytd-video-renderer h3 a"
    ];

    const firstVideo = await waitForElement(videoSelectors, 12000);

    if (firstVideo) {
      console.log("[QT-Agent] Found first video element:", firstVideo);

      // Smoothly scroll video into view if needed
      try {
        firstVideo.scrollIntoView({ behavior: "smooth", block: "center" });
      } catch (e) {}

      await sleep(400);

      const vidRect = firstVideo.getBoundingClientRect();
      const targetX = Math.max(100, Math.min(vidRect.left + 80, window.innerWidth - 180));
      const targetY = Math.max(80, Math.min(vidRect.top + vidRect.height / 2, window.innerHeight - 120));

      console.log(`[QT-Agent] Gliding pointer to video at (${targetX}, ${targetY})...`);
      controller.moveTo(targetX, targetY, 800);
      await sleep(850);

      // Fire shockwave click ripple!
      controller.clickRipple();
      controller.setState("[ 🎵 Launching Video Playback... ]");
      controller.speak("AGENT DJ 🎧", `Clicking "${song}" to start playback! Enjoy!`);

      // Store notice so the watch page also displays celebration
      if (chrome && chrome.storage && chrome.storage.local) {
        chrome.storage.local.set({
          playingNotice: { song: song, timestamp: Date.now() }
        });
      }

      await sleep(450);

      // Click the video!
      const clickEvent = new MouseEvent("click", {
        bubbles: true,
        cancelable: true,
        view: window
      });
      firstVideo.dispatchEvent(clickEvent);

      if (firstVideo.href) {
        window.location.href = firstVideo.href;
      } else {
        firstVideo.click();
      }
    } else {
      console.warn("[QT-Agent] Video element not found within timeout.");
      controller.setState("[ 🎵 Ready to Play ]");
      controller.speak("AGENT DJ 🎧", `Search loaded! Click any video to start listening!`);
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

  async function waitForElement(selectors, timeoutMs = 12000) {
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

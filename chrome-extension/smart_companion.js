/**
 * chrome-extension/smart_companion.js
 * Universal Smart Self-Thinking Companion Agent Pointer
 * 
 * 100% TrustedHTML-Safe (zero innerHTML; compliant with Google Trusted Types CSP).
 * Operates across any website (YouTube, GitHub, Google, Wikipedia, etc.):
 * 1. Always present on the tab as a floating cyber-orange companion.
 * 2. Press Ctrl+Shift+K or click the pointer to summon the Command HUD.
 * 3. Uses QTPageScanner to perceive the page's interactive elements.
 * 4. Consults the DeepAgent Web Navigation Planner API for dynamic LLM reasoning.
 * 5. Animates the pointer smoothly across the DOM with thoughts, shockwaves, and clicks.
 * 6. Automatically handles cross-tab YouTube playback from the portfolio.
 */

(function () {
  // Avoid duplicate injection or injection on localhost portfolio (which has its own pointer)
  if (window.location.origin.includes("localhost:8000") || window.location.origin.includes("127.0.0.1:8000")) {
    return;
  }
  if (document.getElementById("smart-companion-overlay")) return;

  function initCompanion() {
    if (!document.body) {
      setTimeout(initCompanion, 50);
      return;
    }
    if (document.getElementById("smart-companion-overlay")) return;

    console.log("[QT-Agent Smart Companion] Initializing on:", window.location.hostname);

    let isExecuting = false;
    let posX = Math.max(80, window.innerWidth - 180);
    let posY = Math.max(80, window.innerHeight - 150);
    let chaseCount = 0;
    let lastChaseTime = 0;

    // =========================================================================
    // 1. BUILD DOM WITH TRUSTED-TYPES SAFE APIS (NO innerHTML)
    // =========================================================================
    const overlay = document.createElement("div");
    overlay.id = "smart-companion-overlay";

    // Pointer Cursor Wrapper
    const cursor = document.createElement("div");
    cursor.id = "smart-companion-cursor";
    cursor.className = "smart-pointer-cursor";

    const body = document.createElement("div");
    body.className = "cross-pointer-body";

    // Cyber-Orange SVG Arrow
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
    ripple.id = "smart-ripple";
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
    statePill.id = "smart-state";
    statePill.className = "cross-pointer-state";
    statePill.textContent = "[ ⚡ READY ]";
    body.appendChild(statePill);

    // Speech / Thought Bubble
    const bubble = document.createElement("div");
    bubble.id = "smart-bubble";
    bubble.className = "cross-pointer-bubble";

    const bubbleTitle = document.createElement("div");
    bubbleTitle.id = "smart-bubble-title";
    bubbleTitle.className = "cross-bubble-title";
    bubbleTitle.textContent = "QT-AGENT GUIDE";

    const bubbleText = document.createElement("div");
    bubbleText.id = "smart-bubble-text";
    bubbleText.className = "cross-bubble-text";
    bubbleText.textContent = "Press Ctrl+Shift+K or click me to command!";

    bubble.appendChild(bubbleTitle);
    bubble.appendChild(bubbleText);
    body.appendChild(bubble);

    cursor.appendChild(body);
    overlay.appendChild(cursor);

    // Global Command HUD Modal
    const cmdOverlay = document.createElement("div");
    cmdOverlay.id = "smart-cmd-overlay";
    cmdOverlay.className = "smart-command-overlay";

    const cmdCard = document.createElement("div");
    cmdCard.className = "smart-command-card";
    cmdCard.setAttribute("role", "dialog");
    cmdCard.setAttribute("aria-modal", "true");
    cmdCard.setAttribute("aria-label", "Smart Agent HUD");

    // Header
    const cmdHeader = document.createElement("div");
    cmdHeader.className = "smart-command-header";

    const headerTitle = document.createElement("span");
    headerTitle.className = "smart-header-title";
    const headerDot = document.createElement("span");
    headerDot.className = "cross-badge-dot";
    const headerTitleText = document.createElement("span");
    headerTitleText.textContent = "QT-AGENT // SMART BROWSER COMPANION";
    headerTitle.appendChild(headerDot);
    headerTitle.appendChild(headerTitleText);

    const headerShortcut = document.createElement("span");
    headerShortcut.className = "smart-header-shortcut";
    headerShortcut.textContent = "ESC TO CLOSE";

    cmdHeader.appendChild(headerTitle);
    cmdHeader.appendChild(headerShortcut);
    cmdCard.appendChild(cmdHeader);

    // Form
    const cmdForm = document.createElement("form");
    cmdForm.id = "smart-cmd-form";
    cmdForm.className = "smart-command-input-row";
    cmdForm.setAttribute("autocomplete", "off");

    const promptSym = document.createElement("span");
    promptSym.className = "smart-prompt-sym";
    promptSym.textContent = ">_";

    const cmdInput = document.createElement("input");
    cmdInput.id = "smart-cmd-input";
    cmdInput.className = "smart-cmd-input";
    cmdInput.type = "text";
    cmdInput.placeholder = "Type any goal: 'play top video', 'click [x]', 'scroll down'...";

    const submitBtn = document.createElement("button");
    submitBtn.type = "submit";
    submitBtn.className = "smart-cmd-submit-btn";
    submitBtn.textContent = "PLAN & RUN ↵";

    cmdForm.appendChild(promptSym);
    cmdForm.appendChild(cmdInput);
    cmdForm.appendChild(submitBtn);
    cmdCard.appendChild(cmdForm);

    // Quick Chips
    const chipsDiv = document.createElement("div");
    chipsDiv.className = "smart-command-chips";

    const chipConfigs = [
      { text: "🎵 Play Top Video", goal: "Play the top video" },
      { text: "🔍 Search Lofi Beats", goal: "Search for lofi beats and play top video" },
      { text: "📜 Scroll Page", goal: "Scroll down to explore page content" },
      { text: "⚡ Find Search Bar", goal: "Find and focus the search input" }
    ];

    chipConfigs.forEach((cfg) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "smart-chip";
      chip.setAttribute("data-goal", cfg.goal);
      chip.textContent = cfg.text;
      chip.addEventListener("click", () => {
        closeHUD();
        executeSmartGoal(cfg.goal);
      });
      chipsDiv.appendChild(chip);
    });

    cmdCard.appendChild(chipsDiv);
    cmdOverlay.appendChild(cmdCard);
    overlay.appendChild(cmdOverlay);

    // Append to document.body
    document.body.appendChild(overlay);

    // Initial position
    setCursorPos(posX, posY);

    // =========================================================================
    // 2. CONTROLLER FUNCTIONS
    // =========================================================================
    function setCursorPos(x, y) {
      posX = x;
      posY = y;
      cursor.style.transform = `translate3d(${Math.round(x)}px, ${Math.round(y)}px, 0)`;
    }

    function moveTo(x, y, duration = 650) {
      return new Promise((resolve) => {
        cursor.style.transition = `transform ${duration}ms cubic-bezier(0.16, 1, 0.3, 1)`;
        setCursorPos(x, y);
        setTimeout(resolve, duration);
      });
    }

    function setState(text) {
      if (statePill) statePill.textContent = text;
    }

    function speak(title, text, duration = 3200) {
      if (bubbleTitle) bubbleTitle.textContent = title;
      if (bubbleText) bubbleText.textContent = text;
      if (bubble) bubble.classList.add("is-visible");
      if (duration > 0) {
        setTimeout(() => hideSpeech(), duration);
      }
    }

    function hideSpeech() {
      if (bubble) bubble.classList.remove("is-visible");
    }

    function clickRipple() {
      if (!ripple) return;
      ripple.classList.remove("is-clicking");
      void ripple.offsetWidth;
      ripple.classList.add("is-clicking");
    }

    function openHUD() {
      cmdOverlay.classList.add("is-active");
      setTimeout(() => cmdInput && cmdInput.focus(), 80);
    }

    function closeHUD() {
      cmdOverlay.classList.remove("is-active");
      if (cmdInput) cmdInput.value = "";
    }

    // =========================================================================
    // 3. INTERACTIVE EVENTS & KEYBINDINGS
    // =========================================================================
    window.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === "K" || e.key === "k")) {
        e.preventDefault();
        if (cmdOverlay.classList.contains("is-active")) {
          closeHUD();
        } else {
          openHUD();
        }
      } else if (e.key === "Escape") {
        closeHUD();
      }
    });

    cursor.addEventListener("click", () => openHUD());

    cmdOverlay.addEventListener("click", (e) => {
      if (e.target === cmdOverlay) closeHUD();
    });

    cmdForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const goal = cmdInput.value.trim();
      if (goal) {
        closeHUD();
        executeSmartGoal(goal);
      }
    });

    // Playful mouse chase evasion
    window.addEventListener("mousemove", (e) => {
      if (isExecuting || cmdOverlay.classList.contains("is-active")) return;
      const dx = e.clientX - posX;
      const dy = e.clientY - posY;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 75) {
        chaseCount++;
        const now = Date.now();
        if (now - lastChaseTime > 6000) chaseCount = 1;
        lastChaseTime = now;

        const angle = Math.atan2(posY - e.clientY, posX - e.clientX) + (Math.random() - 0.5) * 0.8;
        const leap = 140 + Math.random() * 80;
        const nx = Math.max(80, Math.min(posX + Math.cos(angle) * leap, window.innerWidth - 100));
        const ny = Math.max(80, Math.min(posY + Math.sin(angle) * leap, window.innerHeight - 100));

        cursor.style.transition = "transform 0.38s cubic-bezier(0.18, 0.89, 0.32, 1.28)";
        setCursorPos(nx, ny);

        if (chaseCount === 1) {
          setState("[ 🏃💨 Woah! ]");
        } else if (chaseCount === 2) {
          setState("[ ⚡ Can't catch me! ]");
        } else {
          setState("[ 🎮 Nice try! ]");
          speak("COMPANION AGENT", "Command me by pressing Ctrl + Shift + K!", 2800);
        }
      }
    });

    // =========================================================================
    // 4. THE SMART BRAIN LOOP: Perceive -> Reason -> Act
    // =========================================================================
    async function executeSmartGoal(goal) {
      if (isExecuting) return;
      isExecuting = true;

      setState("[ 🔍 Perceiving Page... ]");
      speak("PERCEPTION SCAN", `Analyzing visible elements on ${window.location.hostname}...`, 1800);

      // Wait briefly for SPA render if on YouTube search results
      if (window.location.hostname.includes("youtube.com") && window.location.pathname === "/results") {
        await waitForYouTubeResults(3000);
      }

      // 1. Scan page elements
      const elements = window.QTPageScanner ? window.QTPageScanner.scan() : [];
      console.log("[Smart Companion] Perceived elements:", elements);

      setState("[ 🧠 DeepAgent Planning... ]");

      // 2. Query DeepAgent Web Navigation Planner API
      let plan = null;
      try {
        const res = await fetch("http://localhost:8000/api/browser/plan-action", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            goal: goal,
            url: window.location.href,
            elements: elements
          })
        });
        if (res.ok) {
          plan = await res.json();
        }
      } catch (err) {
        console.warn("[Smart Companion] Could not reach local planner API, using smart semantic heuristic:", err);
      }

      if (!plan || !plan.actions || plan.actions.length === 0) {
        plan = heuristicPlan(goal, elements);
      }

      console.log("[Smart Companion] Executing AI Plan:", plan);

      // 3. Display LLM Thought in Thought Bubble
      if (plan.thought) {
        setState("[ 🎯 Action Decided ]");
        speak("AI REASONING 💡", plan.thought, 3000);
        await sleep(1400);
      }

      // 4. Execute Planned Actions
      for (const step of plan.actions) {
        console.log("[Smart Companion] Step:", step);

        if (step.thought) {
          speak("STEP ACTION", step.thought, 2200);
        }

        if (step.type === "move_and_click" || step.type === "click") {
          let el = window.QTPageScanner.getElement(step.target_id);
          // Fallback if target element not directly mapped
          if (!el && window.location.hostname.includes("youtube.com")) {
            el = document.querySelector("ytd-video-renderer a#video-title, ytd-video-renderer a#thumbnail");
          }

          if (el) {
            // Find clickable anchor if container is custom element
            let targetClick = el;
            if (el.tagName.toLowerCase().includes("video-renderer") || el.tagName.toLowerCase() === "ytd-video-renderer") {
              const innerLink = el.querySelector("a#video-title, a#thumbnail, a[href]");
              if (innerLink) targetClick = innerLink;
            }

            try { targetClick.scrollIntoView({ behavior: "smooth", block: "center" }); } catch (e) {}
            await sleep(350);

            const rect = targetClick.getBoundingClientRect();
            const tx = Math.max(60, Math.min(rect.left + rect.width / 2, window.innerWidth - 120));
            const ty = Math.max(60, Math.min(rect.top + rect.height / 2, window.innerHeight - 100));

            setState("[ 🎯 Moving to Target... ]");
            await moveTo(tx, ty, 650);
            await sleep(200);

            clickRipple();
            targetClick.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true, view: window }));
            if (targetClick.click) targetClick.click();
            if (targetClick.href && !window.location.href.includes(targetClick.href)) {
              window.location.href = targetClick.href;
            }
            await sleep(700);
          }
        } else if (step.type === "move_and_type" || step.type === "type") {
          let el = window.QTPageScanner.getElement(step.target_id);
          if (!el) {
            el = document.querySelector("input[name='search_query'], input#search, input[type='text']");
          }
          if (el) {
            const rect = el.getBoundingClientRect();
            setState("[ ⌨️ Auto-Typing... ]");
            await moveTo(rect.left + 40, rect.top + rect.height / 2, 600);
            clickRipple();
            el.focus();

            const txt = step.text || "";
            el.value = "";
            for (let i = 0; i < txt.length; i++) {
              el.value += txt[i];
              el.dispatchEvent(new Event("input", { bubbles: true }));
              await sleep(35);
            }
            await sleep(300);
          }
        } else if (step.type === "press_enter") {
          const active = document.activeElement;
          if (active) {
            const form = active.closest("form");
            if (form) {
              form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
            } else {
              active.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", keyCode: 13, bubbles: true }));
            }
          }
          await sleep(1200);
        } else if (step.type === "scroll") {
          const amt = step.amount || 450;
          const dir = step.direction === "up" ? -1 : 1;
          window.scrollBy({ top: amt * dir, behavior: "smooth" });
          await sleep(700);
        } else if (step.type === "done") {
          speak("GOAL ACCOMPLISHED 🚀", step.message || "Action finished successfully!", 3500);
        }
      }

      setState("[ ⚡ READY ]");
      isExecuting = false;
    }

    function heuristicPlan(goal, elements) {
      const gl = goal.toLowerCase();
      // First check for video on YouTube
      if (gl.includes("play") || gl.includes("video") || gl.includes("music") || gl.includes("lofi")) {
        for (const el of elements) {
          const txt = (el.text || "").toLowerCase();
          if (txt.includes("lofi") || txt.includes("beats") || txt.includes("mix") || txt.includes("radio") || el.tag === "a") {
            return {
              thought: `I found the video "${el.text.slice(0, 35)}". Moving to play it!`,
              actions: [{ type: "move_and_click", target_id: el.id, thought: "Clicking to play video" }]
            };
          }
        }
        // Fallback: click first link
        if (elements.length > 0) {
          return {
            thought: "Selecting the top interactive result on page.",
            actions: [{ type: "move_and_click", target_id: elements[0].id, thought: "Clicking top element" }]
          };
        }
      }

      // Check for search
      if (gl.includes("search")) {
        for (const el of elements) {
          if (el.tag === "input" || el.role === "searchbox" || el.placeholder.toLowerCase().includes("search")) {
            return {
              thought: "Found search input. Moving to type and search.",
              actions: [
                { type: "move_and_type", target_id: el.id, text: "lofi hip hop radio", thought: "Typing search query" },
                { type: "press_enter", thought: "Submitting search" }
              ]
            };
          }
        }
      }

      return {
        thought: `Perceived page for goal: "${goal}".`,
        actions: [{ type: "done", message: "Scan complete." }]
      };
    }

    async function waitForYouTubeResults(timeoutMs = 3000) {
      const start = Date.now();
      while (Date.now() - start < timeoutMs) {
        const found = document.querySelector("ytd-video-renderer a#video-title, ytd-video-renderer a#thumbnail");
        if (found) return true;
        await sleep(200);
      }
      return false;
    }

    function sleep(ms) {
      return new Promise((r) => setTimeout(r, ms));
    }

    // =========================================================================
    // 5. YOUTUBE CONTEXT AUTO-DISCOVERY & CELEBRATION
    // =========================================================================
    if (window.location.hostname.includes("youtube.com")) {
      // Check for Watch page celebration
      if (window.location.pathname === "/watch") {
        setState("[ 🎵 Playing on YouTube ]");
        speak("AGENT DJ 🎧", "Now playing! Sit back and enjoy the music!", 4500);
        setTimeout(() => {
          cursor.style.opacity = "0.35";
          cursor.style.transition = "opacity 1.5s ease";
        }, 5000);
        return;
      }

      // Check for Cross-Tab launch hash: #qt_agent_play=...
      const hash = window.location.hash || "";
      let crossTabSong = "";
      if (hash.includes("qt_agent_play=")) {
        crossTabSong = decodeURIComponent(hash.split("qt_agent_play=")[1].split("&")[0]);
        try {
          history.replaceState(null, "", window.location.pathname + window.location.search);
        } catch (e) {}
      }

      if (crossTabSong) {
        console.log("[Smart Companion] Detected cross-tab song trigger:", crossTabSong);
        setState("[ 🌐 CROSSED OVER TO YOUTUBE ]");
        speak("CROSS-TAB WARP 🚀", `Arrived from portfolio! Finding top video for "${crossTabSong}"...`, 3000);
        setTimeout(() => {
          executeSmartGoal("Play top video for " + crossTabSong);
        }, 1200);
        return;
      }

      // Check chrome.storage fallback
      if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
        chrome.storage.local.get(["pendingTask"], (res) => {
          const task = res && res.pendingTask;
          if (task && task.action === "play_youtube" && Date.now() - (task.timestamp || 0) < 60000) {
            chrome.storage.local.remove("pendingTask");
            const song = task.song || "lofi beats";
            setState("[ 🌐 CROSSED OVER TO YOUTUBE ]");
            speak("CROSS-TAB WARP 🚀", `Executing goal: Play top video for "${song}"`, 3000);
            setTimeout(() => {
              executeSmartGoal("Play top video for " + song);
            }, 1200);
            return;
          }
        });
      }

      // If user landed on YouTube search results directly (e.g. from search query in URL)
      if (window.location.pathname === "/results") {
        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get("search_query");
        if (query) {
          setState("[ 🎵 YouTube Search Active ]");
          speak("AGENT DJ 🎧", `Search loaded for "${query}"! Click me or press Ctrl+Shift+K to play top video!`, 4000);
        }
      }
    }
  }

  // Start initialization
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCompanion);
  } else {
    initCompanion();
  }
})();

/**
 * chrome-extension/smart_companion.js
 * Universal Smart Self-Thinking Companion Agent Pointer
 * Operates across any website:
 * 1. Press Ctrl+Shift+K on ANY webpage to summon the Command HUD.
 * 2. Uses QTPageScanner to perceive the page's interactive elements.
 * 3. Consults the DeepAgent Web Navigation Planner API for dynamic LLM reasoning.
 * 4. Animates the pointer smoothly across the DOM with thoughts, shockwaves, and clicks.
 */

(function () {
  // Avoid duplicate injection or injection on localhost portfolio (which already has its own pointer)
  if (window.location.origin.includes("localhost:8000") || window.location.origin.includes("127.0.0.1:8000")) {
    return;
  }
  if (document.getElementById("smart-companion-overlay")) return;

  console.log("[QT-Agent Smart Companion] Active on:", window.location.hostname);

  let isExecuting = false;
  let posX = window.innerWidth - 180;
  let posY = window.innerHeight - 140;
  let chaseCount = 0;
  let lastChaseTime = 0;

  // 1. Create Pointer & HUD DOM
  const overlay = document.createElement("div");
  overlay.id = "smart-companion-overlay";
  overlay.innerHTML = `
    <!-- Companion Pointer -->
    <div id="smart-companion-cursor" class="smart-pointer-cursor">
      <div class="cross-pointer-body">
        <svg class="cross-pointer-svg" viewBox="0 0 24 24" fill="none">
          <path d="M4 4L11 20L14 13L21 10L4 4Z" fill="#ff5c00" stroke="#ffffff" stroke-width="2.2" stroke-linejoin="round"/>
        </svg>
        <div class="cross-pointer-ripple" id="smart-ripple"></div>
        <div class="cross-pointer-badge">
          <span class="cross-badge-dot"></span>
          <span>QT-AGENT GUIDE</span>
        </div>
        <div class="cross-pointer-state" id="smart-state">[ ⚡ READY ]</div>
        <div class="cross-pointer-bubble" id="smart-bubble">
          <div class="cross-bubble-title" id="smart-bubble-title">QT-AGENT GUIDE</div>
          <div class="cross-bubble-text" id="smart-bubble-text">Press Ctrl+Shift+K to command me anywhere!</div>
        </div>
      </div>
    </div>

    <!-- Global Command HUD Modal -->
    <div class="smart-command-overlay" id="smart-cmd-overlay">
      <div class="smart-command-card" role="dialog" aria-modal="true" aria-label="Smart Agent HUD">
        <div class="smart-command-header">
          <span class="smart-header-title">
            <span class="cross-badge-dot"></span>
            <span>QT-AGENT // SMART BROWSER COMPANION</span>
          </span>
          <span class="smart-header-shortcut">ESC TO CLOSE</span>
        </div>
        <form class="smart-command-input-row" id="smart-cmd-form" autocomplete="off">
          <span class="smart-prompt-sym">&gt;_</span>
          <input
            type="text"
            id="smart-cmd-input"
            class="smart-cmd-input"
            placeholder="Type any goal: 'search for [x] and play', 'click [button]', 'scroll down'..."
          />
          <button type="submit" class="smart-cmd-submit-btn">PLAN &amp; RUN ↵</button>
        </form>
        <div class="smart-command-chips">
          <button type="button" class="smart-chip" data-goal="Search for lofi beats and play the top video">🎵 Play Lofi Beats</button>
          <button type="button" class="smart-chip" data-goal="Scroll down to explore page content">📜 Scroll Page</button>
          <button type="button" class="smart-chip" data-goal="Find and focus search bar">🔍 Find Search Bar</button>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  // Cached DOM elements
  const cursor = document.getElementById("smart-companion-cursor");
  const statePill = document.getElementById("smart-state");
  const bubble = document.getElementById("smart-bubble");
  const bubbleTitle = document.getElementById("smart-bubble-title");
  const bubbleText = document.getElementById("smart-bubble-text");
  const ripple = document.getElementById("smart-ripple");
  const cmdOverlay = document.getElementById("smart-cmd-overlay");
  const cmdInput = document.getElementById("smart-cmd-input");
  const cmdForm = document.getElementById("smart-cmd-form");

  // Initial Placement
  setCursorPos(posX, posY);

  // Controller API
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

  function speak(title, text, duration = 3000) {
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

  // Keybindings: Ctrl+Shift+K to toggle HUD
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

  document.querySelectorAll(".smart-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const goal = chip.getAttribute("data-goal");
      if (goal) {
        closeHUD();
        executeSmartGoal(goal);
      }
    });
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

      let angle = Math.atan2(posY - e.clientY, posX - e.clientX) + (Math.random() - 0.5) * 0.8;
      const leap = 140 + Math.random() * 80;
      let nx = Math.max(80, Math.min(posX + Math.cos(angle) * leap, window.innerWidth - 100));
      let ny = Math.max(80, Math.min(posY + Math.sin(angle) * leap, window.innerHeight - 100));

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

  // 2. THE SMART BRAIN LOOP: Perceive -> Reason -> Act
  async function executeSmartGoal(goal) {
    if (isExecuting) return;
    isExecuting = true;

    setState("[ 🔍 Perceiving Page... ]");
    speak("PERCEPTION SCAN", `Analyzing visible elements on ${window.location.hostname}...`, 1800);

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
        speak("STEP ACTION", step.thought, 2000);
      }

      if (step.type === "move_and_click" || step.type === "click") {
        const el = window.QTPageScanner.getElement(step.target_id);
        if (el) {
          try { el.scrollIntoView({ behavior: "smooth", block: "center" }); } catch (e) {}
          await sleep(300);

          const rect = el.getBoundingClientRect();
          const tx = Math.max(60, Math.min(rect.left + rect.width / 2, window.innerWidth - 120));
          const ty = Math.max(60, Math.min(rect.top + rect.height / 2, window.innerHeight - 100));

          setState("[ 🎯 Moving to Target... ]");
          await moveTo(tx, ty, 650);
          await sleep(150);

          clickRipple();
          el.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true, view: window }));
          if (el.click) el.click();
          await sleep(600);
        }
      } else if (step.type === "move_and_type" || step.type === "type") {
        const el = window.QTPageScanner.getElement(step.target_id);
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
    for (const el of elements) {
      const txt = (el.text || "").toLowerCase();
      if (gl.includes("play") && (txt.includes("lofi") || txt.includes("beats") || txt.includes("mix"))) {
        return {
          thought: `I found the video "${el.text.slice(0, 30)}". Moving to play it!`,
          actions: [{ type: "move_and_click", target_id: el.id, thought: "Clicking to play video" }]
        };
      }
      if (gl.includes("search") && (el.tag === "input" || el.role === "searchbox")) {
        return {
          thought: "I found the search input. Moving to type query.",
          actions: [
            { type: "move_and_type", target_id: el.id, text: "lofi hip hop radio", thought: "Typing into search" },
            { type: "press_enter", thought: "Submitting search" }
          ]
        };
      }
    }
    return {
      thought: `Scanning page for: "${goal}".`,
      actions: [{ type: "done", message: "Scan complete." }]
    };
  }

  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }
})();

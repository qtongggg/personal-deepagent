/**
 * frontend/agent_pointer.js — Phase 1: Live Interactive Agent Pointer & Greeting
 * Controls the autonomous cursor, DOM physics, speech bubbles, and typing actions.
 */

(function () {
  class AgentPointer {
    constructor() {
      this.overlay = null;
      this.cursor = null;
      this.badge = null;
      this.statePill = null;
      this.bubble = null;
      this.bubbleTitle = null;
      this.bubbleText = null;
      this.ripple = null;
      this.launcherBtn = null;
      this.isRunning = false;
      this.isAborted = false;

      this.init();
    }

    init() {
      if (document.getElementById("agent-pointer-overlay")) return;

      // 1. Create overlay DOM structure
      this.overlay = document.createElement("div");
      this.overlay.id = "agent-pointer-overlay";
      this.overlay.className = "agent-pointer-overlay";
      this.overlay.innerHTML = `
        <div class="agent-pointer-cursor" id="agent-pointer-cursor">
          <div class="agent-pointer-body">
            <!-- Custom Cyber-Orange SVG Cursor Arrow -->
            <svg class="agent-pointer-svg" viewBox="0 0 24 24" fill="none">
              <path d="M4 4L11 20L14 13L21 10L4 4Z" fill="#ff5c00" stroke="#ffffff" stroke-width="2.2" stroke-linejoin="round"/>
            </svg>
            <div class="agent-click-ripple" id="agent-click-ripple"></div>
            
            <!-- Agent Multiplayer Badge -->
            <div class="agent-pointer-badge">
              <span class="badge-dot"></span>
              <span>QT-AGENT GUIDE</span>
            </div>

            <!-- Dynamic Real-Time Action State Pill -->
            <div class="agent-pointer-state" id="agent-pointer-state">
              [ ⚡ READY ]
            </div>

            <!-- Floating Speech / Thought Bubble -->
            <div class="agent-pointer-bubble" id="agent-pointer-bubble">
              <div class="bubble-title" id="agent-bubble-title">QT-AGENT</div>
              <div class="bubble-text" id="agent-bubble-text">Hi, I'm QT's Personal Agent!</div>
            </div>
          </div>
        </div>
      `;
      document.body.appendChild(this.overlay);

      // Cache DOM elements
      this.cursor = document.getElementById("agent-pointer-cursor");
      this.statePill = document.getElementById("agent-pointer-state");
      this.bubble = document.getElementById("agent-pointer-bubble");
      this.bubbleTitle = document.getElementById("agent-bubble-title");
      this.bubbleText = document.getElementById("agent-bubble-text");
      this.ripple = document.getElementById("agent-click-ripple");

      // Bind launcher button
      this.launcherBtn = document.getElementById("agent-tour-start-btn");
      if (this.launcherBtn) {
        this.launcherBtn.addEventListener("click", () => this.startPhase1Tour());
      }

      // Keyboard escape listener to abort anytime
      window.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && this.isRunning) {
          this.abort();
        }
      });
    }

    async sleep(ms) {
      if (this.isAborted) return;
      return new Promise((r) => setTimeout(r, ms));
    }

    setCursorPos(x, y) {
      this.cursor.style.transform = `translate3d(${Math.round(x)}px, ${Math.round(y)}px, 0)`;
    }

    async moveTo(x, y, durationMs = 650) {
      if (this.isAborted) return;
      this.cursor.style.transition = `transform ${durationMs}ms cubic-bezier(0.22, 1, 0.36, 1)`;
      this.setCursorPos(x, y);
      await this.sleep(durationMs);
    }

    async moveToElement(el, offsetX = 10, offsetY = 10, durationMs = 700) {
      if (this.isAborted || !el) return;
      const rect = el.getBoundingClientRect();
      const targetX = rect.left + offsetX;
      const targetY = rect.top + offsetY;
      await this.moveTo(targetX, targetY, durationMs);
    }

    triggerClickRipple() {
      this.cursor.classList.add("is-clicking");
      this.ripple.classList.remove("animate");
      // Trigger reflow to restart animation
      void this.ripple.offsetWidth;
      this.ripple.classList.add("animate");
      setTimeout(() => {
        this.cursor.classList.remove("is-clicking");
      }, 220);
    }

    setState(text) {
      if (this.isAborted) return;
      if (text) {
        this.statePill.textContent = text;
        this.statePill.classList.add("is-active");
      } else {
        this.statePill.classList.remove("is-active");
      }
    }

    async speak(title, message, durationMs = 2800) {
      if (this.isAborted) return;
      this.bubbleTitle.textContent = title || "QT-AGENT";
      this.bubbleText.textContent = message;
      this.bubble.classList.add("is-active");
      if (durationMs > 0) {
        await this.sleep(durationMs);
      }
    }

    hideSpeech() {
      this.bubble.classList.remove("is-active");
    }

    async typeInto(inputEl, text, charDelayMs = 38) {
      if (this.isAborted || !inputEl) return;
      inputEl.focus();
      inputEl.value = "";
      for (const char of text) {
        if (this.isAborted) break;
        inputEl.value += char;
        inputEl.dispatchEvent(new Event("input", { bubbles: true }));
        await this.sleep(charDelayMs + Math.floor(Math.random() * 15));
      }
    }

    abort() {
      this.isAborted = true;
      this.isRunning = false;
      this.hideSpeech();
      this.setState(null);
      this.cursor.style.transition = "opacity 0.3s ease, transform 0.5s ease";
      this.cursor.style.opacity = "0";
      setTimeout(() => {
        this.setCursorPos(-999, -999);
        this.cursor.style.opacity = "1";
      }, 500);
      if (this.launcherBtn) {
        this.launcherBtn.innerHTML = `
          <span class="tour-dot"></span>
          <span>MEET QT'S AGENT GUIDE</span>
          <span class="tour-arrow">↗</span>
        `;
      }
    }

    // ========================================================================
    // PHASE 1: Awakening, Greeting, Neural Inspection & Live Chat Submission
    // ========================================================================
    async startPhase1Tour() {
      if (this.isRunning) {
        this.abort();
        return;
      }

      this.isRunning = true;
      this.isAborted = false;

      if (this.launcherBtn) {
        this.launcherBtn.innerHTML = `
          <span class="tour-dot" style="background:#ff3333;box-shadow:0 0 10px #ff3333;"></span>
          <span>[ ✕ ESC TO STOP ]</span>
        `;
      }

      // Step 1: Start at bottom-right near the button
      const btnRect = this.launcherBtn ? this.launcherBtn.getBoundingClientRect() : { left: window.innerWidth - 180, top: window.innerHeight - 80 };
      this.cursor.style.transition = "none";
      this.setCursorPos(btnRect.left, btnRect.top - 20);

      // Step 2: Glide into center-left
      await this.sleep(100);
      this.setState("[ ⚡ AWAKENING... ]");
      await this.moveTo(window.innerWidth * 0.42, window.innerHeight * 0.38, 750);
      
      // Step 3: Speak greeting
      await this.speak(
        "QT-AGENT // GREETING",
        "Hi! I'm QT's Personal Agent. Let me show you how QT's AI systems and live reasoning work!",
        2600
      );
      this.hideSpeech();

      // Step 4: Move to the 3D ASCII Möbius neural symbol
      const canvasEl = document.getElementById("cli-ascii-canvas");
      if (canvasEl) {
        this.setState("[ 🔍 Inspecting Reasoning Core ]");
        await this.moveToElement(canvasEl, canvasEl.offsetWidth / 2, canvasEl.offsetHeight / 2, 700);
        await this.speak(
          "REASONING SYMBOL",
          "This 3D ASCII Möbius strip represents QT's active reasoning state in real-time.",
          2400
        );
        this.hideSpeech();
      }

      // Step 5: Move to Terminal Input Box
      const inputEl = document.getElementById("cli-input");
      if (inputEl) {
        const inputRect = inputEl.getBoundingClientRect();
        this.setState("[ ⌨️ Ready to Query ]");
        await this.moveTo(inputRect.left + 24, inputRect.top + inputRect.height / 2, 600);
        this.triggerClickRipple();
        inputEl.click();
        await this.sleep(300);

        // Step 6: Auto-type sample query
        this.setState("[ ⌨️ Auto-Typing Query... ]");
        const prompt = "What are QT's skills and flagship projects?";
        await this.typeInto(inputEl, prompt, 32);
        await this.sleep(400);

        // Step 7: Move to Submit Button and Click!
        const submitBtn = document.getElementById("cli-submit-btn");
        if (submitBtn) {
          const sRect = submitBtn.getBoundingClientRect();
          this.setState("[ 🖱️ Submitting Query... ]");
          await this.moveTo(sRect.left + sRect.width / 2, sRect.top + sRect.height / 2, 450);
          this.triggerClickRipple();
          submitBtn.click();

          // Step 8: Show response streaming state
          this.setState("[ ⚡ DeepAgent Streaming Answer... ]");
          await this.speak(
            "GROUNDED STREAM",
            "Watch how the agent retrieves from QT's resume with BM25 + FlashRank reranking!",
            3200
          );
          this.hideSpeech();
        }
      }

      // Step 9: Settle down cleanly near launcher
      this.setState("[ ● TOUR COMPLETE ]");
      await this.sleep(600);
      this.setState(null);
      await this.moveTo(btnRect.left, btnRect.top - 20, 800);

      this.isRunning = false;
      if (this.launcherBtn) {
        this.launcherBtn.innerHTML = `
          <span class="tour-dot"></span>
          <span>REPLAY AGENT GUIDE</span>
          <span class="tour-arrow">↺</span>
        `;
      }
    }
  }

  // Initialize on DOM load
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      window.qtAgentPointer = new AgentPointer();
    });
  } else {
    window.qtAgentPointer = new AgentPointer();
  }
})();

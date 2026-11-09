/**
 * frontend/agent_pointer.js — Live Interactive Agent Pointer & Ctrl+Shift+K Command HUD
 * Supports autonomous cursor navigation, physical DOM interaction, and natural-language commands.
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
      this.cmdOverlay = null;
      this.cmdInput = null;
      this.isRunning = false;
      this.isAborted = false;

      // Playful Chase Mechanics
      this.posX = -999;
      this.posY = -999;
      this.chaseCount = 0;
      this.lastChaseTime = 0;
      this.isEvading = false;

      this.init();
    }

    init() {
      if (document.getElementById("agent-pointer-overlay")) return;

      // 1. Create overlay DOM structure
      this.overlay = document.createElement("div");
      this.overlay.id = "agent-pointer-overlay";
      this.overlay.className = "agent-pointer-overlay";
      this.overlay.innerHTML = `
        <div class="agent-pointer-cursor" id="agent-pointer-cursor" title="Click to command agent (Ctrl+Shift+K)">
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

        <!-- Ctrl + Shift + K Command Bar Overlay -->
        <div class="agent-command-overlay" id="agent-command-overlay">
          <div class="agent-command-card" role="dialog" aria-modal="true" aria-label="Agent Command HUD">
            <div class="agent-command-header">
              <span class="command-header-title">
                <span class="tour-dot"></span>
                <span>QT-AGENT COMMAND HUD</span>
              </span>
              <span class="command-header-shortcut">ESC TO CLOSE</span>
            </div>
            <form class="agent-command-input-row" id="agent-cmd-form" autocomplete="off">
              <span class="command-prompt-symbol">&gt;_</span>
              <input
                type="text"
                id="agent-command-input"
                class="agent-command-input"
                placeholder="Type command: 'show projects', 'download resume', 'ask [question]'..."
              />
              <button type="submit" class="command-submit-btn">RUN ↵</button>
            </form>
            <div class="agent-command-chips">
              <button type="button" class="agent-cmd-chip" data-cmd="projects">🚀 Show Projects</button>
              <button type="button" class="agent-cmd-chip" data-cmd="resume">📄 Download Resume</button>
              <button type="button" class="agent-cmd-chip" data-cmd="architecture">🏗️ Architecture</button>
              <button type="button" class="agent-cmd-chip" data-cmd="play lofi beats">🎵 Play Lofi Beats</button>
              <button type="button" class="agent-cmd-chip" data-cmd="ask What are QT's core skills and flagship projects?">💬 Ask Skills &amp; Projects</button>
              <button type="button" class="agent-cmd-chip" data-cmd="tour">🎬 Full Showcase Tour</button>
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
      this.cmdOverlay = document.getElementById("agent-command-overlay");
      this.cmdInput = document.getElementById("agent-command-input");

      // Cache Virtual YouTube Window DOM elements
      this.ytNavBtn = document.getElementById("nav-tab-youtube");
      this.ytWindow = document.getElementById("virtual-yt-window");
      this.ytInput = document.getElementById("yt-browser-input");
      this.ytSearchBtn = document.getElementById("yt-browser-search-btn");
      this.ytFrame = document.getElementById("yt-player-frame");
      this.ytPlaceholder = document.getElementById("yt-player-placeholder");
      this.ytCloseBtn = document.getElementById("yt-close-btn");
      this.ytMinimizeBtn = document.getElementById("yt-minimize-btn");
      this.ytMiniPill = document.getElementById("yt-mini-pill");
      this.ytMiniText = document.getElementById("yt-mini-text");

      // Bind YouTube Tab and Window Controls
      if (this.ytNavBtn) {
        this.ytNavBtn.addEventListener("click", () => this.toggleYouTubeWindow());
      }
      if (this.ytCloseBtn) {
        this.ytCloseBtn.addEventListener("click", () => this.closeYouTubeWindow());
      }
      if (this.ytMinimizeBtn) {
        this.ytMinimizeBtn.addEventListener("click", () => this.minimizeYouTubeWindow());
      }
      if (this.ytMiniPill) {
        this.ytMiniPill.addEventListener("click", () => this.restoreYouTubeWindow());
      }
      if (this.ytSearchBtn) {
        this.ytSearchBtn.addEventListener("click", () => {
          const q = this.ytInput ? this.ytInput.value.trim() : "";
          if (q) this.playYouTube(q);
        });
      }
      if (this.ytInput) {
        this.ytInput.addEventListener("keydown", (e) => {
          if (e.key === "Enter") {
            const q = this.ytInput.value.trim();
            if (q) this.playYouTube(q);
          }
        });
      }

      // Bind launcher button
      this.launcherBtn = document.getElementById("agent-tour-start-btn");
      if (this.launcherBtn) {
        this.launcherBtn.addEventListener("click", () => this.startPhase1Tour());
      }

      // Clicking pointer itself opens Command HUD
      this.cursor.addEventListener("click", (e) => {
        e.stopPropagation();
        this.openCommandHUD();
      });

      // Command Form Submit
      const cmdForm = document.getElementById("agent-cmd-form");
      if (cmdForm) {
        cmdForm.addEventListener("submit", (e) => {
          e.preventDefault();
          const val = this.cmdInput.value.trim();
          if (val) this.executeCommand(val);
        });
      }

      // Quick Chips
      document.querySelectorAll(".agent-cmd-chip").forEach((chip) => {
        chip.addEventListener("click", () => {
          const cmd = chip.getAttribute("data-cmd");
          if (cmd) this.executeCommand(cmd);
        });
      });

      // Global Keydown: Ctrl+Shift+K / Cmd+Shift+K to summon Command HUD
      window.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === "K" || e.key === "k")) {
          e.preventDefault();
          this.toggleCommandHUD();
        } else if (e.key === "Escape") {
          if (this.isCommandHUDOpen()) {
            this.closeCommandHUD();
          } else if (this.isRunning) {
            this.abort();
          }
        }
      });

      // Click outside command card closes HUD
      this.cmdOverlay.addEventListener("click", (e) => {
        if (e.target === this.cmdOverlay) {
          this.closeCommandHUD();
        }
      });

      // Playful Pointer Chase / Run Away on Mouse Proximity
      window.addEventListener("mousemove", (e) => {
        if (this.isRunning || this.isEvading || this.isCommandHUDOpen()) return;
        if (this.posX < 0 || this.posY < 0 || this.posX > window.innerWidth || this.posY > window.innerHeight) return;

        const dx = e.clientX - this.posX;
        const dy = e.clientY - this.posY;
        const dist = Math.sqrt(dx * dx + dy * dy);

        // If user's mouse cursor gets closer than 75px
        if (dist < 75) {
          this.handleChase(e.clientX, e.clientY);
        }
      });

      // Gentle auto-entrance: peek into view near the launcher button after 2 seconds
      setTimeout(() => {
        if (this.posX < 0 && !this.isRunning) {
          const btnRect = this.launcherBtn ? this.launcherBtn.getBoundingClientRect() : { left: window.innerWidth - 180, top: window.innerHeight - 80 };
          this.cursor.style.transition = "transform 0.9s cubic-bezier(0.16, 1, 0.3, 1)";
          this.setCursorPos(btnRect.left - 45, btnRect.top - 35);
        }
      }, 2000);
    }

    isCommandHUDOpen() {
      return this.cmdOverlay && this.cmdOverlay.classList.contains("is-active");
    }

    openCommandHUD() {
      if (!this.cmdOverlay) return;
      this.cmdOverlay.classList.add("is-active");
      setTimeout(() => this.cmdInput && this.cmdInput.focus(), 80);
    }

    closeCommandHUD() {
      if (!this.cmdOverlay) return;
      this.cmdOverlay.classList.remove("is-active");
      if (this.cmdInput) this.cmdInput.value = "";
    }

    toggleCommandHUD() {
      if (this.isCommandHUDOpen()) {
        this.closeCommandHUD();
      } else {
        this.openCommandHUD();
      }
    }

    openYouTubeWindow() {
      if (this.ytWindow) {
        this.ytWindow.classList.add("is-open");
      }
      if (this.ytMiniPill) {
        this.ytMiniPill.classList.remove("is-active");
      }
      if (this.ytNavBtn) {
        this.ytNavBtn.classList.add("active");
      }
    }

    closeYouTubeWindow() {
      if (this.ytWindow) {
        this.ytWindow.classList.remove("is-open");
      }
      if (this.ytFrame) {
        this.ytFrame.src = "about:blank";
      }
      if (this.ytPlaceholder) {
        this.ytPlaceholder.classList.remove("is-hidden");
      }
      if (this.ytMiniPill) {
        this.ytMiniPill.classList.remove("is-active");
      }
      if (this.ytNavBtn) {
        this.ytNavBtn.classList.remove("active");
      }
    }

    minimizeYouTubeWindow() {
      if (this.ytWindow) {
        this.ytWindow.classList.remove("is-open");
      }
      if (this.ytMiniPill) {
        this.ytMiniPill.classList.add("is-active");
      }
    }

    restoreYouTubeWindow() {
      this.openYouTubeWindow();
    }

    toggleYouTubeWindow() {
      if (this.ytWindow && this.ytWindow.classList.contains("is-open")) {
        this.closeYouTubeWindow();
      } else {
        this.openYouTubeWindow();
      }
    }

    playYouTube(songQuery) {
      const query = (songQuery || "lofi hip hop radio").trim();
      let embedUrl;
      if (/lofi|study|chill|relax/i.test(query)) {
        embedUrl = "https://www.youtube-nocookie.com/embed/jfKfPfyJRdk?autoplay=1&enablejsapi=1";
      } else {
        embedUrl = `https://www.youtube.com/embed?listType=search&list=${encodeURIComponent(query)}&autoplay=1`;
      }

      if (this.ytInput) this.ytInput.value = query;
      if (this.ytPlaceholder) this.ytPlaceholder.classList.add("is-hidden");
      if (this.ytFrame) this.ytFrame.src = embedUrl;
      if (this.ytMiniText) this.ytMiniText.textContent = `🎵 ${query}`;
      if (this.ytNavBtn) this.ytNavBtn.classList.add("active");
    }

    async sleep(ms) {
      if (this.isAborted) return;
      return new Promise((r) => setTimeout(r, ms));
    }

    setCursorPos(x, y) {
      this.posX = x;
      this.posY = y;
      this.cursor.style.transform = `translate3d(${Math.round(x)}px, ${Math.round(y)}px, 0)`;
    }

    async handleChase(mouseX, mouseY) {
      this.isEvading = true;
      this.chaseCount++;
      const now = Date.now();

      // Reset chase counter if user paused for > 6s
      if (now - this.lastChaseTime > 6000) {
        this.chaseCount = 1;
      }
      this.lastChaseTime = now;

      // Calculate runaway direction away from mouse
      let angle = Math.atan2(this.posY - mouseY, this.posX - mouseX);
      angle += (Math.random() - 0.5) * 0.9; // natural wobble

      const leapDist = 130 + Math.random() * 80;
      let newX = this.posX + Math.cos(angle) * leapDist;
      let newY = this.posY + Math.sin(angle) * leapDist;

      // Ensure inside viewport bounds
      const pad = 80;
      if (newX < pad) newX = pad + Math.random() * 120;
      if (newX > window.innerWidth - pad) newX = window.innerWidth - pad - Math.random() * 120;
      if (newY < pad) newY = pad + Math.random() * 120;
      if (newY > window.innerHeight - pad) newY = window.innerHeight - pad - Math.random() * 120;

      // Snappy spring leap animation
      this.cursor.style.transition = "transform 0.38s cubic-bezier(0.18, 0.89, 0.32, 1.28)";
      this.setCursorPos(newX, newY);

      if (this.chaseCount === 1) {
        this.setState("[ 🏃💨 Woah, too close! ]");
        await this.sleep(400);
      } else if (this.chaseCount === 2) {
        this.setState("[ ⚡ Can't catch me! ]");
        await this.sleep(400);
      } else if (this.chaseCount >= 3) {
        this.setState("[ 🎮 Haha nice try! ]");
        await this.speak(
          "AGENT EVASION",
          "Haha you can't catch me with the mouse! 🎮 Command me by pressing Ctrl + Shift + K!",
          3800
        );
        this.hideSpeech();
        this.setState(null);
        this.chaseCount = 0;
      }

      await this.sleep(300);
      this.isEvading = false;
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

    async typeInto(inputEl, text, charDelayMs = 32) {
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
    // DIRECT COMMAND EXECUTION PIPELINE
    // ========================================================================
    async executeCommand(rawCommand) {
      const cmd = rawCommand.trim();
      if (!cmd) return;

      this.closeCommandHUD();
      this.isRunning = true;
      this.isAborted = false;

      const cmdLower = cmd.toLowerCase();

      // Ensure cursor is visible
      const curRect = this.cursor.getBoundingClientRect();
      if (curRect.left < 0 || curRect.top < 0) {
        this.cursor.style.transition = "none";
        this.setCursorPos(window.innerWidth / 2, window.innerHeight * 0.7);
        await this.sleep(50);
      }

      // 1. COMMAND: PROJECTS / WORK
      if (cmdLower.includes("project") || cmdLower.includes("system") || cmdLower === "projects") {
        this.setState("[ 🚀 Navigating to Projects... ]");
        const detailsBtn = document.querySelector('[data-view-target="details"]');
        if (detailsBtn) {
          await this.moveToElement(detailsBtn, detailsBtn.offsetWidth / 2, detailsBtn.offsetHeight / 2, 600);
          this.triggerClickRipple();
          detailsBtn.click();
          await this.sleep(500);
        }

        const project1 = document.querySelector("#systems-list .system-row");
        if (project1) {
          await this.moveToElement(project1, 120, 24, 700);
          this.triggerClickRipple();
          project1.click();
          await this.speak("FLAGSHIP PROJECT", "Here is Personal DeepAgent — multi-hop research agent with benchmark arena!", 3000);
          this.hideSpeech();
        }
        this.setState(null);
        this.isRunning = false;
        return;
      }

      // 2. COMMAND: RESUME / CV
      if (cmdLower.includes("resume") || cmdLower.includes("cv") || cmdLower.includes("download")) {
        this.setState("[ 📄 Locating Resume PDF... ]");
        const resumeBtn = document.querySelector('.nav-resume-btn, [href*="Resume.pdf"]');
        if (resumeBtn) {
          await this.moveToElement(resumeBtn, resumeBtn.offsetWidth / 2, resumeBtn.offsetHeight / 2, 700);
          this.triggerClickRipple();
          await this.speak("1-PAGE ATS RESUME", "Clicking verified 1-page ATS resume for download!", 2400);
          this.hideSpeech();
          resumeBtn.click();
        }
        this.setState(null);
        this.isRunning = false;
        return;
      }

      // 3. COMMAND: ARCHITECTURE / RAG
      if (cmdLower.includes("architecture") || cmdLower.includes("pillar") || cmdLower.includes("rag")) {
        this.setState("[ 🏗️ Inspecting Architecture... ]");
        const archLink = document.querySelector('[data-scroll-target="capabilities"]');
        if (archLink) {
          await this.moveToElement(archLink, archLink.offsetWidth / 2, archLink.offsetHeight / 2, 600);
          this.triggerClickRipple();
          archLink.click();
          await this.sleep(400);
        }
        const pillar1 = document.querySelector("#pillars-stream .pillar-block");
        if (pillar1) {
          await this.moveToElement(pillar1, 80, 40, 650);
          await this.speak("CORE ARCHITECTURE", "Four layers of agentic engineering: Hybrid RAG, Agent Loops, Analytics & Full-Stack Deployment.", 3200);
          this.hideSpeech();
        }
        this.setState(null);
        this.isRunning = false;
        return;
      }

      // 4. COMMAND: TOUR / GUIDE
      if (cmdLower === "tour" || cmdLower.includes("showcase") || cmdLower.includes("guide")) {
        await this.startPhase1Tour();
        return;
      }

      // 5. COMMAND: YOUTUBE / PLAY MUSIC / SONG
      if (
        cmdLower.includes("youtube") ||
        cmdLower.startsWith("play ") ||
        cmdLower.includes("play song") ||
        cmdLower.includes("play music") ||
        cmdLower.includes("play a song") ||
        cmdLower.includes("lofi")
      ) {
        let songQuery = cmd.trim();
        songQuery = songQuery.replace(/^(please\s+)?open\s+youtube(\s+and)?\s*/i, "");
        songQuery = songQuery.replace(/^(please\s+)?play(\s+a|\s+some)?\s*(song|music|track|beats)?\s*/i, "");
        songQuery = songQuery.replace(/\s*on\s+youtube\s*/i, " ");
        songQuery = songQuery.replace(/\s*for\s+me\s*/i, " ");
        songQuery = songQuery.trim();

        // If generic or empty, default to relaxing coding lofi beats
        if (!songQuery || ["a song", "song", "music", "some music", "something", "track", "beats"].includes(songQuery.toLowerCase())) {
          songQuery = "lofi hip hop radio beats to relax study to";
        }

        // STEP 1: Announce and glide up to YouTube Tab in navigation
        this.setState("[ 🌐 Gliding to YouTube Tab... ]");
        this.speak("NAVIGATING TABS", "Heading up to the YouTube Music tab...", 2200);

        const ytTab = document.getElementById("nav-tab-youtube");
        if (ytTab) {
          await this.moveToElement(ytTab, ytTab.offsetWidth / 2, ytTab.offsetHeight / 2, 700);
          this.triggerClickRipple();
          ytTab.classList.add("active");
        }

        // STEP 2: Open the Virtual Cyber Browser Window
        this.openYouTubeWindow();
        await this.sleep(350);

        // STEP 3: Glide down to YouTube search bar and auto-type the song
        const ytInput = document.getElementById("yt-browser-input");
        const ytSearchBtn = document.getElementById("yt-browser-search-btn");
        if (ytInput && ytSearchBtn) {
          this.setState("[ ⌨️ Auto-Typing Song... ]");
          await this.moveToElement(ytInput, 40, ytInput.offsetHeight / 2, 600);
          this.triggerClickRipple();
          ytInput.focus();

          await this.typeInto(ytInput, songQuery, 28);
          await this.sleep(200);

          // STEP 4: Glide to Play Button and click
          await this.moveToElement(ytSearchBtn, ytSearchBtn.offsetWidth / 2, ytSearchBtn.offsetHeight / 2, 400);
          this.triggerClickRipple();

          // STEP 5: Start playback inside the tab
          this.playYouTube(songQuery);
        }

        this.setState("[ 🎵 Playing on YouTube... ]");
        await this.speak("NOW PLAYING 🎧", `Playing "${songQuery}" inside YouTube tab! Enjoy the music while exploring!`, 3400);
        this.hideSpeech();
        this.setState(null);
        this.isRunning = false;
        return;
      }

      // 6. COMMAND: NOTE
      if (cmdLower.startsWith("note:") || cmdLower.startsWith("note ") || cmdLower.startsWith("take note")) {
        const noteText = cmd.replace(/^(note:|note\s+|take\s+note:?)/i, "").trim();
        this.setState("[ 📝 Saving Workspace Note... ]");
        await this.speak("WORKSPACE NOTE SAVED", `"${noteText}" has been logged to your session scratchpad!`, 2600);
        this.hideSpeech();
        this.setState(null);
        this.isRunning = false;
        return;
      }

      // 6. DEFAULT: ASK AGENT A QUESTION
      const queryText = cmd.replace(/^ask\s+/i, "").trim();
      this.setState("[ 💬 Routing to Terminal... ]");
      
      // Ensure on Home view
      const homeView = document.getElementById("view-home");
      if (homeView && !homeView.classList.contains("active")) {
        const homeBtn = document.querySelector('[data-view-target="home"]');
        if (homeBtn) {
          homeBtn.click();
          await this.sleep(300);
        }
      }

      const inputEl = document.getElementById("cli-input");
      const submitBtn = document.getElementById("cli-submit-btn");
      if (inputEl && submitBtn) {
        await this.moveToElement(inputEl, 40, inputEl.offsetHeight / 2, 650);
        this.triggerClickRipple();
        this.setState("[ ⌨️ Typing Query... ]");
        await this.typeInto(inputEl, queryText, 28);
        await this.sleep(300);

        await this.moveToElement(submitBtn, submitBtn.offsetWidth / 2, submitBtn.offsetHeight / 2, 450);
        this.triggerClickRipple();
        submitBtn.click();

        this.setState("[ ⚡ DeepAgent Streaming Answer... ]");
        await this.speak("AI AGENT STREAM", `Routing question to QT's Resume DeepAgent...`, 2400);
        this.hideSpeech();
      }

      this.setState(null);
      this.isRunning = false;
    }

    // ========================================================================
    // SCRIPTED SHOWCASE TOUR
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

      // Step 1: Start at bottom-right near button
      const btnRect = this.launcherBtn ? this.launcherBtn.getBoundingClientRect() : { left: window.innerWidth - 180, top: window.innerHeight - 80 };
      this.cursor.style.transition = "none";
      this.setCursorPos(btnRect.left, btnRect.top - 20);

      // Step 2: Glide into center
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

      // Step 4: Move to 3D ASCII Möbius neural symbol
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

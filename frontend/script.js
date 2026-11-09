/**
 * ============================================================================
 * MAH QING TONG (QT) — KINETIC SCROLL & OPEN ARCHITECTURE ENGINE
 * ============================================================================
 */

const QT_DATA = {
  email: "smartqingtong@gmail.com",
  typewriterPhrases: [
    "Autonomous Multi-Hop Agents",
    "Hybrid RAG + FlashRank Reranking",
    "FastAPI Backend + SSE Streaming",
    "Dify Production AI Workflows"
  ],
  pillars: [
    {
      index: "01",
      code: "LAYER // 01",
      title: "Retrieval-Augmented Generation & FlashRank Reranking",
      tag: "[ PIPELINE // RAG ]",
      desc: "Architecting high-precision RAG pipelines combining ChromaDB vector embeddings, BM25 sparse keyword matching, and cross-encoder FlashRank reranking to eliminate hallucination.",
      stages: [
        { step: "STAGE 01 →", name: "Markdown Normalizer", sub: "Clean Ingestion", highlight: false },
        { step: "STAGE 02 →", name: "Hybrid Retriever", sub: "Chroma + BM25", highlight: true },
        { step: "STAGE 03 →", name: "FlashRank", sub: "Cross-Reranker", highlight: false },
        { step: "STAGE 04 ●", name: "Context Injection", sub: "Deterministic Grounding", highlight: false }
      ]
    },
    {
      index: "02",
      code: "LAYER // 02",
      title: "Autonomous Agent Loops & Active Planning",
      tag: "[ PIPELINE // AGENTIC ]",
      desc: "Developing production-grade agentic loops with LangGraph and LangChain deepagents: incorporating task planning (write_to_dos), virtual workspace filesystems, and multi-hop execution.",
      stages: [
        { step: "STAGE 01 →", name: "Active Planner", sub: "write_to_dos State", highlight: true },
        { step: "STAGE 02 →", name: "Virtual Workspace", sub: "Scratchpad File I/O", highlight: false },
        { step: "STAGE 03 →", name: "Iterative Hops", sub: "Multi-Source Reasoning", highlight: false },
        { step: "STAGE 04 ●", name: "Memory Commit", sub: "Mem0 Persistence", highlight: false }
      ]
    },
    {
      index: "03",
      code: "LAYER // 03",
      title: "Natural Language Analytics & Schema Verification",
      tag: "[ PIPELINE // ANALYTICS ]",
      desc: "Building deterministic Text-to-SQL agents using LangGraph and PostgreSQL/DuckDB that inspect database schemas, validate queries, and render dynamic analytical charts.",
      stages: [
        { step: "STAGE 01 →", name: "Schema Inspection", sub: "Table Cataloging", highlight: false },
        { step: "STAGE 02 →", name: "SQL Generation", sub: "Domain Constraint Rules", highlight: true },
        { step: "STAGE 03 →", name: "Query Execution", sub: "DuckDB / PostgreSQL", highlight: false },
        { step: "STAGE 04 ●", name: "Dynamic Visuals", sub: "JSON & Chart Delivery", highlight: false }
      ]
    },
    {
      index: "04",
      code: "LAYER // 04",
      title: "Production AI Workflows & FastAPI Microservices",
      tag: "[ PIPELINE // FULL-STACK ]",
      desc: "Deploying full-stack AI backends and enterprise agent workflows: connecting FastAPI SSE real-time streaming, Dify DAG orchestration, and live Human-in-the-Loop turnovers.",
      stages: [
        { step: "STAGE 01 →", name: "Dify Chatflow", sub: "DAG Orchestration", highlight: true },
        { step: "STAGE 02 →", name: "FastAPI Backend", sub: "SSE Streaming Proxy", highlight: false },
        { step: "STAGE 03 →", name: "HITL Turnover", sub: "Live Agent Handoff", highlight: false },
        { step: "STAGE 04 ●", name: "Production Deploy", sub: "Containerized 24/7", highlight: false }
      ]
    }
  ],
  systems: [
    {
      num: "01",
      title: "PERSONAL DEEPAGENT // Autonomous Multi-Hop Research Agent & Benchmark Arena",
      category: "AGENTIC",
      desc: "Flagship autonomous research agent built using LangChain deepagents harness and LangGraph. Features dynamic task planning, virtual scratchpad filesystem, multi-hop retrieval over structured catalogs and vector stores, and automated side-by-side arena benchmarking.",
      highlights: [
        "Engineered 2-hop iterative retrieval: Hop 1 DuckDB catalog SQL query + Hop 2 surgical dense+BM25 vector search with FlashRank reranking.",
        "Integrated active task planning (write_to_dos) and virtual scratchpad drafting before committing long-term memory to Mem0.",
        "Automated headless Chromium arena video recording comparing standard naive RAG vs DeepAgent across an 11-dimension comparative matrix."
      ],
      tags: ["#LANGGRAPH", "#MULTI-HOP-RAG", "#DUCKDB", "#FLASHRANK", "#DEEPAGENTS"]
    },
    {
      num: "02",
      title: "INCEIF i-FIKR // Islamic Knowledge Agent with Analytical Skills (Zetrix AI)",
      category: "AGENTIC",
      desc: "Domain-specific Islamic finance and knowledge chatbot built at Zetrix AI. Overcame standard naive RAG limitations by integrating custom Agent Skills to handle structured comparisons, exhaustive listing, and exact counting queries.",
      highlights: [
        "Engineered specialized Agent Skills for multi-document comparison, structured listing, and count aggregation.",
        "Combined Dify agent workflow orchestration with high-precision Markdown-cleaned knowledge retrieval.",
        "Resolved complex analytical user prompts where standard vector similarity search alone fails."
      ],
      tags: ["#ZETRIX-AI", "#AGENT-SKILLS", "#DIFY-WORKFLOW", "#ANALYTICAL-RAG"]
    },
    {
      num: "03",
      title: "PROPERTY AVATAR // Conversational Booking Concierge & Human Turnover (Zetrix AI)",
      category: "AUTOMATION",
      desc: "Interactive real-estate AI avatar and booking concierge engineered at Zetrix AI to automate appointment scheduling, slot verification, and live human agent handoff.",
      highlights: [
        "Automated real-time checking of available appointment slots, booking creation, and booking date reviews.",
        "Implemented seamless Human-in-the-Loop (HITL) turnover from the chatbot to live human support agents.",
        "Orchestrated stateful conversation flows and tool integrations using Dify workflows."
      ],
      tags: ["#ZETRIX-AI", "#DIFY-AGENT", "#BOOKING-AUTOMATION", "#HUMAN-TURNOVER"]
    },
    {
      num: "04",
      title: "ENTERPRISE WIKI RAG // Structured Markdown Normalization Pipeline (Zetrix AI)",
      category: "RAG",
      desc: "Internal enterprise knowledge assistant and automated document pre-cleaning pipeline enabling company-wide SOP and wiki Q&A with clean Markdown ingestion.",
      highlights: [
        "Built pre-cleaning pipelines that transform noisy raw documents into structured Markdown before vector indexing.",
        "Deployed internal Wiki RAG chatbot for fast, grounded answers across company knowledge bases with deterministic source attribution."
      ],
      tags: ["#ZETRIX-AI", "#WIKI-RAG", "#MARKDOWN-PRECLEANING", "#KNOWLEDGE-BASE"]
    },
    {
      num: "05",
      title: "F1 DATA TEXT-TO-SQL AGENT // LangGraph & PostgreSQL Analytics",
      category: "AGENTIC",
      desc: "Workflow-based Text-to-SQL agent using Python, PostgreSQL, LangGraph, and LangChain that converts natural-language F1 queries into executable SQL, JSON, and dynamic charts.",
      highlights: [
        "Automated database schema inspection, SQL execution, confidence scoring, and dynamic chart selection.",
        "Encoded Formula 1 domain rules for sprint points, standings, race statistics, and historical analytics."
      ],
      tags: ["#LANGGRAPH", "#TEXT-TO-SQL", "#POSTGRESQL", "#AGENT-ORCHESTRATION"]
    },
    {
      num: "06",
      title: "MODULAR TRANSFORMER & BERT PREFIX PROMPT-TUNING (PyTorch Deep Learning)",
      category: "AGENTIC",
      desc: "Modular Transformer Encoder built from scratch in PyTorch alongside a parameter-efficient Prefix Prompt-Tuning pipeline for pretrained BERT models.",
      highlights: [
        "Implemented custom Multi-Head Self-Attention, Position-wise Feed-Forward networks, and Attention-augmented RNN/LSTM/GRUs.",
        "Froze core BERT parameters while optimizing prefix prompts across six categorical text domains."
      ],
      tags: ["#PYTORCH", "#TRANSFORMERS", "#PREFIX-TUNING", "#DEEP-LEARNING"]
    }
  ],
  cliOutputs: {
    overview: `MAH QING TONG (QT) :: AI & LLM Engineer specializing in Autonomous Multi-Hop Agents (LangGraph), Production RAG (ChromaDB + BM25 + FlashRank), and FastAPI Full-Stack Systems. Bachelor of Computer Science (Data Science) from Monash University (Graduated Dec 2025).`,
    deepagent: `PERSONAL DEEPAGENT :: LangChain deepagents harness + LangGraph + DuckDB SQL + Hybrid Dense+BM25 + FlashRank Reranker. Solves complex queries via active task planning (write_to_dos), virtual workspace scratchpads, and 2-hop iterative retrieval.`,
    rag: `HYBRID RAG PIPELINE :: Raw Document Normalization (Markdown) → Hybrid Search (Dense ChromaDB Embeddings + BM25 Sparse Keywords) → FlashRank Cross-Encoder Reranking → Grounded Context Synthesis.`,
    agentic: `AGENTIC & HARNESS :: LangGraph State Machines + Active Task Planning + Virtual Scratchpads + Custom Agent Skills (Compare / List / Count) + Human-in-the-Loop Turnover.`,
    zetrix: `ZETRIX AI SYSTEMS :: (1) INCEIF i-FIKR Analytical Islamic Knowledge Agent, (2) Property Avatar Booking & Human-Turnover Concierge, (3) Enterprise Wiki RAG with Markdown Pre-Cleaning.`
  }
};


// ============================================================================
// 1. RENDER PILLARS & SYSTEMS (NO BOXES, PURE HAIRLINE STREAMS)
// ============================================================================

function renderPillars() {
  const container = document.getElementById("pillars-stream");
  container.innerHTML = QT_DATA.pillars
    .map(
      (p, idx) => `
      <article class="pillar-block reveal-on-scroll ${idx === 0 ? "active-pillar" : ""}" data-code="${p.code}" data-title="${p.title}">
        <div class="pillar-top">
          <span class="pillar-index">${p.index} //</span>
          <h3 class="pillar-title">${p.title}</h3>
          <span class="pillar-tag">${p.tag}</span>
        </div>
        <p class="pillar-desc">${p.desc}</p>
        <div class="pillar-flow-graph" role="list" aria-label="${p.title} Pipeline Stages">
          ${p.stages
            .map(
              (s) => `
            <div class="flow-stage ${s.highlight ? "flow-stage-highlight" : ""}" role="listitem">
              <div class="flow-stage-step">${s.step}</div>
              <div class="flow-stage-name">${s.name}</div>
              <div class="flow-stage-sub">${s.sub}</div>
            </div>
          `
            )
            .join("")}
        </div>
      </article>
    `
    )
    .join("");
}

function renderSystems(filter = "all") {
  const list = document.getElementById("systems-list");
  const filtered =
    filter === "all"
      ? QT_DATA.systems
      : QT_DATA.systems.filter((s) => s.category === filter);

  list.innerHTML = filtered
    .map(
      (sys, idx) => `
      <article class="system-row reveal-on-scroll ${idx === 0 ? "expanded" : ""}">
        <div class="system-row-summary">
          <span class="sys-num">${sys.num}</span>
          <h3 class="sys-title">${sys.title}</h3>
          <span class="sys-category">[ ${sys.category} ]</span>
          <span class="sys-toggle">+</span>
        </div>
        <div class="system-row-details">
          <div class="sys-details-grid">
            <div>
              <p class="sys-desc">${sys.desc}</p>
              <div class="sys-tags">
                ${sys.tags.map((t) => `<span>${t}</span>`).join("")}
              </div>
            </div>
            <ul class="sys-highlights">
              ${sys.highlights.map((h) => `<li><span>${h}</span></li>`).join("")}
            </ul>
          </div>
        </div>
      </article>
    `
    )
    .join("");

  // Toggle expand on click
  list.querySelectorAll(".system-row").forEach((row) => {
    row.addEventListener("click", () => {
      const wasExpanded = row.classList.contains("expanded");
      list.querySelectorAll(".system-row").forEach((r) => r.classList.remove("expanded"));
      if (!wasExpanded) {
        row.classList.add("expanded");
      }
    });
    observeElement(row);
  });
}

// ============================================================================
// 2. SCROLL-DRIVEN WORD ILLUMINATION & INTERSECTION OBSERVERS
// ============================================================================

function initManifestoScrollWords() {
  const el = document.getElementById("scroll-highlight-text");
  if (!el) return;

  const orangeKeywords = new Set([
    "RAG",
    "pipelines,",
    "Agent",
    "Skills,",
    "Harness",
    "Engineering,",
    "Automation",
    "Workflows.",
    "90%"
  ]);

  const words = el.textContent.trim().split(/\s+/);
  el.innerHTML = words
    .map((w) => {
      const isOrange = orangeKeywords.has(w);
      return `<span class="manifesto-word" data-orange="${isOrange}">${w}</span>`;
    })
    .join(" ");

  const wordSpans = el.querySelectorAll(".manifesto-word");

  function updateWordsOnScroll() {
    const rect = el.getBoundingClientRect();
    const viewH = window.innerHeight;
    // Start lighting up when top enters 85% of viewport, finish when top reaches 20%
    const start = viewH * 0.85;
    const end = viewH * 0.15;
    const progress = Math.max(0, Math.min(1, (start - rect.top) / (start - end)));
    const litCount = Math.floor(progress * wordSpans.length);

    wordSpans.forEach((span, idx) => {
      if (idx <= litCount) {
        span.classList.add("lit");
        if (span.getAttribute("data-orange") === "true") {
          span.classList.add("lit-orange");
        }
      } else {
        span.classList.remove("lit", "lit-orange");
      }
    });
  }

  window.addEventListener("scroll", updateWordsOnScroll, { passive: true });
  updateWordsOnScroll();
}

let scrollObserver;

function observeElement(el) {
  if (scrollObserver) scrollObserver.observe(el);
}

function initScrollRevealsAndCounters() {
  scrollObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");

          // If it's a stat column with a number counter, animate it once
          const statNum = entry.target.querySelector(".stat-num");
          if (statNum && !statNum.dataset.animated) {
            statNum.dataset.animated = "true";
            animateCounter(statNum);
          }
        }
      });
    },
    { threshold: 0.18, rootMargin: "0px 0px -40px 0px" }
  );

  document.querySelectorAll(".reveal-on-scroll, .section-index").forEach((el) => {
    scrollObserver.observe(el);
  });

  // Pillar active state observer as user scrolls through Section 02
  const codeEl = document.getElementById("active-pillar-code");
  const nameEl = document.getElementById("active-pillar-name");
  const pillarBlocks = document.querySelectorAll(".pillar-block");

  const pillarObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          pillarBlocks.forEach((b) => b.classList.remove("active-pillar"));
          entry.target.classList.add("active-pillar");
          codeEl.textContent = entry.target.getAttribute("data-code");
          nameEl.textContent = entry.target.getAttribute("data-title");
        }
      });
    },
    { threshold: 0.55 }
  );

  pillarBlocks.forEach((block) => {
    pillarObserver.observe(block);
    block.addEventListener("mouseenter", () => {
      pillarBlocks.forEach((b) => b.classList.remove("active-pillar"));
      block.classList.add("active-pillar");
      codeEl.textContent = block.getAttribute("data-code");
      nameEl.textContent = block.getAttribute("data-title");
    });
  });
}

function animateCounter(el) {
  const rawCount = el.getAttribute("data-count");
  if (!rawCount || isNaN(parseFloat(rawCount))) return;
  const target = parseFloat(rawCount);
  const suffix = el.getAttribute("data-suffix") || "";
  const isDecimal = String(target).includes(".");
  const duration = 1200;
  const startTime = performance.now();

  function step(now) {
    const elapsed = now - startTime;
    const progress = Math.min(1, elapsed / duration);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = target * eased;
    el.textContent = (isDecimal ? current.toFixed(1) : Math.floor(current)) + suffix;
    if (progress < 1) {
      requestAnimationFrame(step);
    }
  }

  requestAnimationFrame(step);
}

// ============================================================================
// 3. SCROLL PROGRESS BAR, TYPEWRITER, CLOCK, CLI & CURSOR
// ============================================================================

function initScrollProgress() {
  const bar = document.getElementById("scroll-progress-bar");
  window.addEventListener(
    "scroll",
    () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.width = `${pct}%`;
    },
    { passive: true }
  );
}

function initTypewriter() {
  const el = document.getElementById("typewriter-text");
  let phraseIdx = 0;
  let charIdx = 0;
  let deleting = false;

  function tick() {
    const phrase = QT_DATA.typewriterPhrases[phraseIdx];
    charIdx += deleting ? -1 : 1;
    el.textContent = phrase.substring(0, charIdx);

    let delay = deleting ? 35 : 75;
    if (!deleting && charIdx === phrase.length) {
      delay = 2200;
      deleting = true;
    } else if (deleting && charIdx === 0) {
      deleting = false;
      phraseIdx = (phraseIdx + 1) % QT_DATA.typewriterPhrases.length;
      delay = 300;
    }
    setTimeout(tick, delay);
  }

  setTimeout(tick, 1400);
}

function initClock() {
  const clockEl = document.getElementById("live-clock");
  const update = () => {
    const now = new Date();
    clockEl.textContent =
      now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }) +
      " UTC+8";
  };
  update();
  setInterval(update, 1000);
}

function initFiltersAndCLI() {
  // Systems Filter
  const filterBtns = document.querySelectorAll("#project-filters .open-filter");
  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      renderSystems(btn.getAttribute("data-filter"));
    });
  });

  // Copy Email Action
  const copyBtn = document.getElementById("copy-email-btn");
  copyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(QT_DATA.email);
    } catch {
      // ignore fallback
    }
    showToast(`COPIED // ${QT_DATA.email}`);
  });

  initInteractiveCLIAgent();
}

function initInteractiveCLIAgent() {
  const transcript = document.getElementById("cli-transcript");
  const form = document.getElementById("cli-input-form");
  const input = document.getElementById("cli-input");
  const submitBtn = document.getElementById("cli-submit-btn");
  const clearBtn = document.getElementById("cli-clear-btn");
  const engineBadge = document.getElementById("cli-engine-badge");
  const sessionIdEl = document.getElementById("cli-session-id");
  const quickBtns = document.querySelectorAll("#cli-quick-prompts .cli-btn");

  let conversationId = "";
  const commandHistory = [];
  let historyIdx = -1;
  let isStreaming = false;

  // Check backend /api/status
  async function checkEngineStatus() {
    try {
      const res = await fetch("/api/status");
      if (!res.ok) throw new Error("No backend");
      const data = await res.json();
      if (data.mode === "deepagent" || data.agent) {
        engineBadge.textContent = `● ONLINE // RESUME DEEPAGENT (${data.knowledge_chunks || 14} CHUNKS)`;
      } else if (data.dify_configured) {
        engineBadge.textContent = "● ONLINE // DIFY CLOUD RAG";
      } else {
        engineBadge.textContent = `● ONLINE // LOCAL RAG (${data.knowledge_chunks} CHUNKS)`;
      }
    } catch {
      engineBadge.textContent = "● ONLINE // IN-BROWSER RAG";
    }
  }
  checkEngineStatus();

  const threadWrap = document.getElementById("minimal-thread-wrap");

  function appendUserEntry(text) {
    if (threadWrap) threadWrap.classList.remove("is-empty");
    const entry = document.createElement("div");
    entry.className = "cli-entry cli-user-entry";
    entry.innerHTML = `
      <div class="cli-entry-meta">YOU</div>
      <div class="cli-entry-body"></div>
    `;
    entry.querySelector(".cli-entry-body").textContent = text;
    transcript.appendChild(entry);
    transcript.scrollTop = transcript.scrollHeight;
  }

  function createAgentStreamingEntry(metaLabel = "QT-AGENT") {
    if (threadWrap) threadWrap.classList.remove("is-empty");
    const entry = document.createElement("div");
    entry.className = "cli-entry cli-agent-entry";
    entry.innerHTML = `
      <div class="cli-entry-meta">${metaLabel}</div>
      <div class="cli-entry-body"><span class="agent-stream-text"></span><span class="streaming-cursor">▋</span></div>
    `;
    transcript.appendChild(entry);
    transcript.scrollTop = transcript.scrollHeight;
    return {
      entry,
      metaEl: entry.querySelector(".cli-entry-meta"),
      textEl: entry.querySelector(".agent-stream-text"),
      cursorEl: entry.querySelector(".streaming-cursor")
    };
  }

  async function streamBrowserFallback(query, streamUI) {
    const q = query.toLowerCase();
    let answer = QT_DATA.cliOutputs.overview;
    let section = "PROFILE OVERVIEW";
    if (q.includes("deepagent") || q.includes("research") || q.includes("multihop") || q.includes("multi-hop")) {
      answer = QT_DATA.cliOutputs.deepagent;
      section = "PERSONAL DEEPAGENT";
    } else if (q.includes("rag") || q.includes("retriev") || q.includes("vector") || q.includes("flashrank") || q.includes("bm25")) {
      answer = QT_DATA.cliOutputs.rag;
      section = "HYBRID RAG PIPELINE";
    } else if (q.includes("agent") || q.includes("langgraph") || q.includes("harness") || q.includes("skill") || q.includes("sql")) {
      answer = QT_DATA.cliOutputs.agentic;
      section = "AGENTIC SYSTEMS";
    } else if (q.includes("zetrix") || q.includes("fikr") || q.includes("property") || q.includes("avatar") || q.includes("dify")) {
      answer = QT_DATA.cliOutputs.zetrix;
      section = "ZETRIX AI SYSTEMS";
    } else if (q.includes("project") || q.includes("system") || q.includes("built")) {
      answer = `FEATURED ENGINEERED PROJECTS BY QT:
01. Personal DeepAgent — Autonomous Multi-Hop Research Agent & Benchmark Arena
02. INCEIF i-FIKR — Islamic Knowledge Agent with Analytical Skills (Zetrix AI)
03. Property Avatar — Conversational Booking & Human Turnover Concierge (Zetrix AI)
04. Enterprise Wiki RAG — Structured Markdown Normalization Pipeline (Zetrix AI)
05. F1 Data Text-to-SQL Agent — LangGraph Schema Verification & PostgreSQL Analytics
06. Modular Transformer & Prefix-Tuning — PyTorch Deep Learning`;
      section = "FEATURED PROJECTS";
    }

    streamUI.metaEl.textContent = `QT-AGENT // RAG [${section}]`;
    const tokens = answer.match(/\S+\s*|\n/g) || [answer];
    for (const tok of tokens) {
      streamUI.textEl.textContent += tok;
      transcript.scrollTop = transcript.scrollHeight;
      await new Promise((r) => setTimeout(r, 50));
    }
    streamUI.cursorEl.remove();
  }

  async function handleCommandOrQuery(rawQuery) {
    const query = rawQuery.trim();
    if (!query || isStreaming) return;

    commandHistory.unshift(query);
    historyIdx = -1;

    if (query.toLowerCase() === "/clear" || query.toLowerCase() === "clear") {
      transcript.innerHTML = "";
      if (threadWrap) threadWrap.classList.add("is-empty");
      conversationId = "";
      sessionIdEl.textContent = "SESSION // RESET";
      return;
    }

    appendUserEntry(query);

    if (query.toLowerCase() === "/help" || query.toLowerCase() === "help") {
      const ui = createAgentStreamingEntry("QT-AGENT // COMMAND REFERENCE");
      ui.textEl.textContent =
        "AVAILABLE COMMANDS & TOPICS:\n" +
        "  • Ask any natural-language question (e.g., 'How does QT build RAG & Dify workflows?')\n" +
        "  • cd ./projects     — Navigate to Section 03 (Engineered Projects) & list systems\n" +
        "  • cd ./capabilities — Navigate to Section 02 (Core Architecture Pillars)\n" +
        "  • cd ./architecture — Navigate to Section 01 (Core Architecture Pillars)\n" +
        "  • cd ./projects     — Navigate to Section 02 (Engineered Projects)\n" +
        "  • /rag              — Inspect QT's Hybrid & Graph RAG stack\n" +
        "  • /harness          — Inspect QT's Harness Engineering & Agent Skills architecture\n" +
        "  • /dify             — Inspect QT's Dify & Automation Workflow expertise\n" +
        "  • /progress         — Read live milestone ledger from progress.md\n" +
        "  • /decisions        — Read Architectural Decision Records from decision.md\n" +
        "  • /clear            — Clear terminal transcript and reset session";
      ui.cursorEl.remove();
      return;
    }

    const qNorm = query.toLowerCase().trim();
    if (
      qNorm === "cd ./projects" ||
      qNorm === "cd ./project" ||
      qNorm === "cd projects" ||
      qNorm === "/projects"
    ) {
      const ui = createAgentStreamingEntry("QT-AGENT // DIRECTORY NAVIGATION [~/projects]");
      ui.textEl.textContent =
        "Opening Page 02 -> Section 03 // ENGINEERED PROJECTS...\n\n" +
        QT_DATA.systems.map((s) => `  [${s.num}] ${s.title} (${s.category})`).join("\n");
      ui.cursorEl.remove();
      setTimeout(() => switchPortfolioView("details", "systems"), 220);
      return;
    }

    if (qNorm === "cd ./capabilities" || qNorm === "cd capabilities") {
      const ui = createAgentStreamingEntry("QT-AGENT // DIRECTORY NAVIGATION [~/capabilities]");
      ui.textEl.textContent =
        "Opening Page 02 -> Section 02 // CORE ARCHITECTURE PILLARS...\n\n" +
        QT_DATA.pillars.map((p) => `  [${p.index}] ${p.title}`).join("\n");
      ui.cursorEl.remove();
      setTimeout(() => switchPortfolioView("details", "capabilities"), 220);
      return;
    }

    if (qNorm === "cd ./architecture" || qNorm === "cd architecture" || qNorm === "cd ./philosophy" || qNorm === "cd philosophy") {
      const ui = createAgentStreamingEntry("QT-AGENT // DIRECTORY NAVIGATION [~/architecture]");
      ui.textEl.textContent = "Opening Page 02 -> Section 01 // CORE ARCHITECTURE PILLARS...";
      ui.cursorEl.remove();
      setTimeout(() => switchPortfolioView("details", "capabilities"), 220);
      return;
    }

    if (qNorm === "cd ./projects" || qNorm === "cd projects" || qNorm === "cd ./systems" || qNorm === "cd systems") {
      const ui = createAgentStreamingEntry("QT-AGENT // DIRECTORY NAVIGATION [~/projects]");
      ui.textEl.textContent = "Opening Page 02 -> Section 02 // ENGINEERED PROJECTS...";
      ui.cursorEl.remove();
      setTimeout(() => switchPortfolioView("details", "systems"), 220);
      return;
    }

    if (qNorm === "cd ~/home" || qNorm === "cd ~" || qNorm === "cd home") {
      const ui = createAgentStreamingEntry("QT-AGENT // DIRECTORY NAVIGATION [~/home]");
      ui.textEl.textContent = "Already on Page 01 // HOME & CLI AGENT.";
      ui.cursorEl.remove();
      switchPortfolioView("home");
      return;
    }

    const mappedQuery =
      query === "/rag"
        ? "How does QT architect Hybrid RAG pipelines?"
        : query === "/harness"
        ? "What is QT's approach to Harness Engineering and Agent Skills?"
        : query === "/dify"
        ? "How does QT build Dify Automation Workflows?"
        : query === "/progress"
        ? "Show current project milestone status from progress.md"
        : query === "/decisions"
        ? "What are the key architectural decisions and ADRs in decision.md?"
        : query;

    isStreaming = true;
    submitBtn.disabled = true;
    setAsciiAgentThinking(true);
    const streamUI = createAgentStreamingEntry("QT-AGENT // RETRIEVING KNOWLEDGE...");

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: mappedQuery,
          conversation_id: conversationId,
          user: "portfolio-visitor"
        })
      });

      if (!response.ok || !response.body) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let rawText = "";
      let targetText = "";
      let shownLen = 0;
      let streamDone = false;
      let pumpRunning = false;
      let resolvePumpDone = null;
      const pumpDonePromise = new Promise((r) => {
        resolvePumpDone = r;
      });
      let activeMetaLabel = "QT-AGENT // DIFY CLOUD RAG [KNOWLEDGE]";

      const formatCleanOutput = (text) => {
        // Strip completed <think>...</think> blocks (including <!--dify-deepseek-reasoning-->)
        let cleaned = text.replace(/<think>[\s\S]*?<\/think>\s*/gi, "");
        // If an unclosed <think> block is still streaming, hide the internal monologue
        if (/^[\s\S]*<think>(?![\s\S]*<\/think>)/i.test(cleaned)) {
          cleaned = cleaned.replace(/<think>[\s\S]*$/i, "");
          streamUI.metaEl.textContent = "QT-AGENT // REASONING IN PROGRESS...";
        } else {
          streamUI.metaEl.textContent = activeMetaLabel;
        }
        // Clean markdown bold markers (**text** -> text) for crisp terminal output
        return cleaned.replace(/\*\*(.*?)\*\*/g, "$1");
      };

      const pumpTypewriter = async () => {
        if (pumpRunning) return;
        pumpRunning = true;
        while (shownLen < targetText.length || !streamDone) {
          if (shownLen > targetText.length) {
            shownLen = targetText.length;
          }
          if (shownLen < targetText.length) {
            const remaining = targetText.slice(shownLen);
            const nextWordMatch = remaining.match(/^\S+\s*|^\s+/);
            const step = nextWordMatch ? Math.min(nextWordMatch[0].length, 8) : 3;
            shownLen = Math.min(targetText.length, shownLen + Math.max(1, step));
            streamUI.textEl.textContent = targetText.slice(0, shownLen);
            transcript.scrollTop = transcript.scrollHeight;
            await new Promise((r) => setTimeout(r, 50));
          } else {
            await new Promise((r) => setTimeout(r, 28));
          }
        }
        pumpRunning = false;
        if (resolvePumpDone) resolvePumpDone();
      };

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith("data:")) continue;
          const jsonStr = line.slice(5).trim();
          if (!jsonStr) continue;

          try {
            const evt = JSON.parse(jsonStr);
            if (evt.type === "meta") {
              const modeLabel = evt.mode === "deepagent" ? "RESUME DEEPAGENT" : (evt.mode === "dify_cloud" ? "DIFY CLOUD RAG" : "LOCAL RAG");
              activeMetaLabel = `QT-AGENT // ${modeLabel} [${evt.section || "KNOWLEDGE"}]`;
              streamUI.metaEl.textContent = activeMetaLabel;
            } else if (evt.type === "token") {
              rawText += evt.content;
              streamUI.textContent = undefined;
              targetText = formatCleanOutput(rawText);
              pumpTypewriter();
              if (evt.conversation_id) {
                conversationId = evt.conversation_id;
                sessionIdEl.textContent = `SESSION // ${conversationId.slice(0, 8).toUpperCase()}`;
              }
            } else if (evt.type === "error") {
              streamUI.metaEl.textContent = "QT-AGENT // NOTICE";
              targetText += `\n[Notice] ${evt.content}`;
              pumpTypewriter();
            }
          } catch {
            // ignore partial JSON
          }
        }
      }
      streamDone = true;
      pumpTypewriter();
      await pumpDonePromise;
      streamUI.metaEl.textContent = activeMetaLabel;
      streamUI.cursorEl.remove();
    } catch {
      // If running via python -m http.server without server.py, use in-browser streaming fallback
      await streamBrowserFallback(mappedQuery, streamUI);
    } finally {
      isStreaming = false;
      submitBtn.disabled = false;
      setAsciiAgentThinking(false);
      input.focus();
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const val = input.value;
    input.value = "";
    handleCommandOrQuery(val);
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowUp") {
      if (historyIdx < commandHistory.length - 1) {
        historyIdx++;
        input.value = commandHistory[historyIdx];
      }
      e.preventDefault();
    } else if (e.key === "ArrowDown") {
      if (historyIdx > 0) {
        historyIdx--;
        input.value = commandHistory[historyIdx];
      } else {
        historyIdx = -1;
        input.value = "";
      }
      e.preventDefault();
    }
  });

  quickBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const q = btn.getAttribute("data-query");
      if (q) handleCommandOrQuery(q);
    });
  });

  if (clearBtn) {
    clearBtn.addEventListener("click", () => handleCommandOrQuery("/clear"));
  }
}

// ============================================================================
// 5. 3D ASCII MÖBIUS STRIP <-> THINKING WAVE SYMBOL (CENTERED HOME)
// ============================================================================

let asciiTargetWaveWeight = 0;
let asciiThinkingStartMs = 0;
let asciiFocusResetTimer = null;
let waterRippleState = {
  active: false,
  intensity: 0,
  dropStartSec: 0,
  wakeLoop: null,
};

function triggerWaterRippleDrop() {
  waterRippleState.dropStartSec = performance.now() * 0.001;
  // Instant full intensity on trigger for the immediate "BOOM!" impact
  waterRippleState.intensity = 1.0;
  if (typeof waterRippleState.wakeLoop === "function") {
    waterRippleState.wakeLoop();
  }
}

function applyThinkingVisualState(active) {
  asciiTargetWaveWeight = active ? 1 : 0;
  waterRippleState.active = active;
  document.body.classList.toggle("agent-thinking-focus", active);

  if (active) {
    triggerWaterRippleDrop();
  } else if (typeof waterRippleState.wakeLoop === "function") {
    waterRippleState.wakeLoop();
  }

  const badgeEl = document.getElementById("cli-ascii-state");
  const shapeEl = document.getElementById("cli-ascii-shape");

  if (badgeEl) {
    if (active) {
      badgeEl.textContent = "● STATE // THINKING & RETRIEVING...";
      badgeEl.classList.add("thinking");
    } else {
      badgeEl.textContent = "● STATE // IDLE (∞ MÖBIUS)";
      badgeEl.classList.remove("thinking");
    }
  }

  if (shapeEl) {
    shapeEl.textContent = active ? "⚡ THINKING WAVE" : "∞ MÖBIUS";
  }
}

function setAsciiAgentThinking(isThinking) {
  clearTimeout(asciiFocusResetTimer);

  if (isThinking) {
    asciiThinkingStartMs = performance.now();
    // Re-trigger the CSS boomStageImpulse animation cleanly on rapid queries
    document.body.classList.remove("agent-thinking-focus");
    void document.body.offsetWidth;
    applyThinkingVisualState(true);
  } else {
    const elapsed = performance.now() - asciiThinkingStartMs;
    const holdMs = Math.max(0, 3400 - elapsed);
    asciiFocusResetTimer = setTimeout(() => {
      applyThinkingVisualState(false);
    }, holdMs);
  }
}

function initWaterRippleShaderEngine() {
  const canvas = document.getElementById("focus-ripple-canvas");
  if (!canvas) return;

  const gl =
    canvas.getContext("webgl", { alpha: true, antialias: false, depth: false, stencil: false, powerPreference: "high-performance" }) ||
    canvas.getContext("experimental-webgl");

  if (!gl) return;

  const vsSource = `
    attribute vec2 a_pos;
    varying vec2 v_uv;
    void main() {
      v_uv = a_pos * 0.5 + 0.5;
      gl_Position = vec4(a_pos, 0.0, 1.0);
    }
  `;

  const fsSource = `
    precision highp float;
    varying vec2 v_uv;
    uniform vec2 u_res;
    uniform float u_time;
    uniform float u_dropAge;
    uniform float u_intensity;

    // Travelling hollow-centered 3D water wave band:
    // Starts with an instant BOOM shock impulse, then rolls outward slowly, steadily, and strongly while leaving the center clean!
    float dropWavePacket(float rw, float age) {
      if (age <= 0.0) return 0.0;

      // 1. Instant "BOOM!" initial shockwave ring that bursts out in the first 0.55s
      float boomRadius = 0.28 + age * 1.45;
      float boomShock = 2.4 * exp(-pow((rw - boomRadius) * 8.5, 2.0)) * exp(-age * 3.2);

      // 2. "...then the wave": Slow, steady, strong travelling ring band (~3.8s full sweep)
      float speed = 0.34;
      float front = 0.28 + age * speed;

      // Hollow ring-band window: wave exists in a strong moving band around 'front', leaving the inner wake (r < front) calm & clean!
      float ringBandEnvelope = exp(-pow((rw - (front - 0.16)) * 2.35, 2.0))
                             * smoothstep(front + 0.12, front - 0.04, rw)
                             * exp(-age * 0.08);

      // Strong leading hydro-crest at the outer edge of the slow wave
      float blastShockwave = 1.95 * exp(-pow((rw - front) * 6.5, 2.0)) * exp(-age * 0.14);

      // Slow, steady, heavy outward phase roll (-age * 4.8) with deep sculptural wave ridges
      float phase = rw * 20.0 - age * 4.8;
      float stokesWave = (sin(phase) + 0.38 * cos(phase * 2.0)) * 1.55;

      return stokesWave * ringBandEnvelope + blastShockwave + boomShock;
    }

    // Composite 3D liquid heightfield with a 100% clean center (no messy inner flower blobs)
    float waterHeight(vec2 p, float t, float dropAge) {
      float r = length(p);
      float ang = atan(p.y, p.x);

      // Keep the center (r < 0.30) completely free of distortion; only gentle liquid curve in the outer field
      float outerCurveMask = smoothstep(0.34, 0.78, r);
      float wobble = (0.009 * sin(ang * 2.0 + r * 7.0 - t * 0.85)
                    + 0.005 * cos(ang * 3.0 - r * 11.0 + t * 0.65)) * outerCurveMask;
      float rw = max(0.001, r + wobble);

      // Clean hollow center mask: zero wave clutter inside the central symbol/title zone (r < 0.28)
      float innerCleanMask = smoothstep(0.26, 0.46, r);

      // Primary BOOM + slow-and-strong wave, followed by steady 3.8s wave cycles while Dify is thinking
      float d1 = dropWavePacket(rw, dropAge);
      float cycleAge1 = mod(dropAge, 3.8);
      float d2 = (dropAge > 2.4) ? 0.85 * dropWavePacket(rw, cycleAge1) : 0.0;

      // Gentle outer carrier swell (strictly outside the clean center)
      float carrierSwell = 0.38 * sin(rw * 17.0 - t * 3.2) * exp(-rw * 0.55)
                         * smoothstep(0.42, 0.72, r)
                         * smoothstep(0.0, 0.35, dropAge);

      return (d1 + d2 + carrierSwell) * innerCleanMask;
    }

    void main() {
      vec2 uv = v_uv;
      float aspect = u_res.x / max(u_res.y, 1.0);

      // Center origin at the 3D symbol (50% X, 42% from top => 58% WebGL Y)
      vec2 center = vec2(0.5, 0.58);
      vec2 p = (uv - center) * vec2(aspect, 1.0);
      p.y *= 1.06;

      float eps = 0.0025;
      float hC = waterHeight(p, u_time, u_dropAge);
      float hX = waterHeight(p + vec2(eps, 0.0), u_time, u_dropAge);
      float hY = waterHeight(p + vec2(0.0, eps), u_time, u_dropAge);

      // Steep 3D water surface gradient and normal for dramatic sculptural depth
      vec2 dH = vec2(hX - hC, hY - hC) / eps;
      float slopeMag = length(dH);
      vec3 N = normalize(vec3(-dH.x * 0.145, -dH.y * 0.145, 1.0));

      vec2 refP = p + N.xy * 0.25;
      float r = length(p);

      // Clean hollow center mask so the area behind the 3D symbol and MAH QING TONG (QT) stays 100% clean
      float innerCleanMask = smoothstep(0.26, 0.48, r);

      // Slow, liquid refracted caustic ribbons in the outer wave rings
      float causticWave = 0.5 + 0.5 * sin((refP.x * 18.0 - refP.y * 22.0) + sin(refP.x * 10.0 - u_time * 1.1) * 1.5);

      // High-energy Electric Blue & Cyan Blast Palette
      vec3 deepAbyss    = vec3(0.010, 0.090, 0.260);
      vec3 oceanCobalt  = vec3(0.030, 0.340, 0.760);
      vec3 electricCyan = vec3(0.100, 0.680, 0.980);
      vec3 shockIce     = vec3(0.520, 0.880, 1.000);

      float crestFactor = clamp(0.5 + hC * 0.55 + N.y * 1.55 - N.x * 1.05, 0.0, 1.0);
      vec3 waterTint = mix(deepAbyss, oceanCobalt, smoothstep(0.06, 0.52, crestFactor));
      waterTint = mix(waterTint, electricCyan, smoothstep(0.42, 0.88, crestFactor));
      waterTint = mix(waterTint, shockIce, causticWave * clamp(slopeMag * 0.030, 0.0, 0.42));

      // Directional lighting for sleek liquid crescent highlights on the outer wave ridges
      vec3 V = vec3(0.0, 0.0, 1.0);
      vec3 L1 = normalize(vec3(-0.36, 0.54, 0.76));
      vec3 L2 = normalize(vec3(0.44, -0.36, 0.82));

      vec3 H1 = normalize(L1 + V);
      vec3 H2 = normalize(L2 + V);

      float specRaw1 = max(dot(N, H1), 0.0);
      float specRaw2 = max(dot(N, H2), 0.0);

      float softGlow = pow(specRaw1, 10.0) * 0.78 + pow(specRaw2, 14.0) * 0.48;
      float glossyCrescent = smoothstep(0.935, 0.988, specRaw1) * 0.85
                           + smoothstep(0.950, 0.992, specRaw2) * 0.55;

      // 1. Instant "BOOM!" shock-ring flash (first 0.5s) + 2. Slow leading wave ring glow
      float boomFront = 0.28 + u_dropAge * 1.45;
      float boomRingFlash = exp(-pow((r - boomFront) * 7.5, 2.0)) * exp(-u_dropAge * 3.0) * 0.95;

      float cycleFront = 0.28 + mod(u_dropAge, 3.8) * 0.34;
      float shockRingGlow = exp(-pow((r - cycleFront) * 5.2, 2.0)) * 0.68;

      vec3 finalColor = waterTint
                      + electricCyan * (softGlow * 0.85 + shockRingGlow)
                      + shockIce * (glossyCrescent * 0.92 + boomRingFlash);

      // Center Sanctuary Mask: keep the center column (symbol, title, and chat box) completely clean
      vec2 centerBox = abs(uv - vec2(0.5, 0.48)) / vec2(0.24, 0.28);
      float boxDist = length(max(centerBox - 0.55, 0.0));
      float sanctuaryMask = mix(0.08, 1.0, smoothstep(0.0, 0.42, boxDist)) * innerCleanMask;

      // TRANSPARENCY: Center is 100% clean & transparent; outer wave ridges surge with strong translucent intensity
      float slopeOpacity = smoothstep(0.38, 9.5, slopeMag) * 0.54;
      float crestOpacity = smoothstep(0.05, 0.75, abs(hC)) * 0.26;
      float specOpacity  = clamp(softGlow * 0.45 + glossyCrescent * 0.68 + shockRingGlow * 0.55 + boomRingFlash * 0.85, 0.0, 0.85);
      float radialFade   = smoothstep(1.78, 0.15, r);

      float waveAlpha = clamp((slopeOpacity + crestOpacity + specOpacity) * sanctuaryMask * radialFade * u_intensity, 0.0, 0.78);

      gl_FragColor = vec4(finalColor, waveAlpha);
    }
  `;

  function compileShader(type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      gl.deleteShader(shader);
      return null;
    }
    return shader;
  }

  const vs = compileShader(gl.VERTEX_SHADER, vsSource);
  const fs = compileShader(gl.FRAGMENT_SHADER, fsSource);
  if (!vs || !fs) return;

  const prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;

  gl.useProgram(prog);
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

  const quadBuf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, quadBuf);
  gl.bufferData(
    gl.ARRAY_BUFFER,
    new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
    gl.STATIC_DRAW
  );

  const posLoc = gl.getAttribLocation(prog, "a_pos");
  gl.enableVertexAttribArray(posLoc);
  gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

  const uRes = gl.getUniformLocation(prog, "u_res");
  const uTime = gl.getUniformLocation(prog, "u_time");
  const uDropAge = gl.getUniformLocation(prog, "u_dropAge");
  const uIntensity = gl.getUniformLocation(prog, "u_intensity");

  // Render at 0.65x resolution with hardware bilinear upscaling for locked 60fps zero-lag performance
  function resizeCanvas() {
    const scale = Math.min(window.devicePixelRatio || 1, 1.5) * 0.65;
    const w = Math.max(320, Math.floor(window.innerWidth * scale));
    const h = Math.max(240, Math.floor(window.innerHeight * scale));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
      gl.viewport(0, 0, w, h);
    }
  }

  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  let rafId = null;

  function renderRippleFrame(nowMs) {
    const target = waterRippleState.active ? 1 : 0;
    waterRippleState.intensity += (target - waterRippleState.intensity) * (waterRippleState.active ? 0.06 : 0.038);

    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT);

    if (!waterRippleState.active && waterRippleState.intensity < 0.004) {
      waterRippleState.intensity = 0;
      rafId = null;
      return;
    }

    const nowSec = nowMs * 0.001;
    const dropAge = Math.max(0, nowSec - waterRippleState.dropStartSec);

    gl.uniform2f(uRes, canvas.width, canvas.height);
    gl.uniform1f(uTime, nowSec);
    gl.uniform1f(uDropAge, dropAge);
    gl.uniform1f(uIntensity, waterRippleState.intensity);

    gl.drawArrays(gl.TRIANGLES, 0, 6);
    rafId = requestAnimationFrame(renderRippleFrame);
  }

  waterRippleState.wakeLoop = () => {
    resizeCanvas();
    if (!rafId) {
      rafId = requestAnimationFrame(renderRippleFrame);
    }
  };
}

function initAsciiMobiusWaveEngine() {
  const cliCanvas = document.getElementById("cli-ascii-canvas");
  if (!cliCanvas) return;

  let mx = 0;
  let my = 0;
  window.addEventListener("mousemove", (e) => {
    mx = (e.clientX / window.innerWidth - 0.5) * 0.55;
    my = (e.clientY / window.innerHeight - 0.5) * 0.45;
  });

  const COLS = 48;
  const CELL_W = 7;
  const CELL_H = 10;
  const NUM_U = 84;
  const NUM_V = 18;
  const ramp = ".,-~:;=!*#$@";

  let waveWeight = 0;
  let time = 0;

  function posMobius(u, v) {
    const R = 1.35;
    const w = 0.48 * v;
    const halfU = u * 0.5;
    const x = (R + w * Math.cos(halfU)) * Math.cos(u);
    const y = (R + w * Math.cos(halfU)) * Math.sin(u) * 0.72;
    const z = w * Math.sin(halfU) + 0.35 * Math.sin(u * 2);
    return [x, y, z];
  }

  function posThinkingWave(u, v, t) {
    const x = (u / (Math.PI * 2) - 0.5) * 3.0;
    const z = v * 1.25;
    const dist = Math.sqrt(x * x + z * z);
    const y = 0.86 * Math.sin(dist * 2.5 - t * 2.1) * Math.cos(x * 1.1);
    return [x, y, z];
  }

  function drawCanvas(canvas, rows) {
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = "bold 10px 'JetBrains Mono', monospace";
    ctx.textBaseline = "top";

    const charBuf = new Array(COLS * rows).fill(null);
    const colorBuf = new Array(COLS * rows).fill("#f7f7f5");
    const zbuf = new Array(COLS * rows).fill(-999);

    const mobiusWeight = 1 - waveWeight;
    const rotY = time * 0.65 + mx;
    const rotX = 0.48 + waveWeight * 0.22 + my;
    const cosY = Math.cos(rotY);
    const sinY = Math.sin(rotY);
    const cosX = Math.cos(rotX);
    const sinX = Math.sin(rotX);

    for (let iu = 0; iu < NUM_U; iu++) {
      const u = (iu / NUM_U) * Math.PI * 2;
      for (let iv = 0; iv < NUM_V; iv++) {
        const v = (iv / (NUM_V - 1)) * 2 - 1;

        const m = posMobius(u, v);
        const w = posThinkingWave(u, v, time);

        const px = m[0] * mobiusWeight + w[0] * waveWeight;
        const py = m[1] * mobiusWeight + w[1] * waveWeight;
        const pz = m[2] * mobiusWeight + w[2] * waveWeight;

        const rx = px * cosY + pz * sinY;
        const rz1 = -px * sinY + pz * cosY;
        const ry = py * cosX - rz1 * sinX;
        const rz = py * sinX + rz1 * cosX;

        const depth = 1 / (rz + 4.0);
        const sx = Math.floor(COLS / 2 + rx * depth * 42);
        const sy = Math.floor(rows / 2 - ry * depth * 17);

        if (sx >= 0 && sx < COLS && sy >= 0 && sy < rows) {
          const idx = sx + sy * COLS;
          if (depth > zbuf[idx]) {
            zbuf[idx] = depth;
            const normZ = Math.max(0, Math.min(1, (rz + 1.5) / 3.0));
            const charIdx = Math.min(ramp.length - 1, Math.floor(normZ * ramp.length));
            charBuf[idx] = ramp[charIdx];
            if (waveWeight > 0.25) {
              const isBlueCrest = Math.sin(u * 3 - time * 2.4) > 0.25 || charIdx >= 9;
              colorBuf[idx] = isBlueCrest ? "#38bdf8" : charIdx > 5 ? "#e0f2fe" : "#0284c7";
            } else {
              const isOrange = Math.abs(Math.sin(u - time * 2.0)) > 0.88 || charIdx >= 10;
              colorBuf[idx] = isOrange ? "#ff4d00" : charIdx > 5 ? "#f7f7f5" : "#a3a39e";
            }
          }
        }
      }
    }

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < COLS; c++) {
        const idx = c + r * COLS;
        const ch = charBuf[idx];
        if (ch) {
          ctx.fillStyle = colorBuf[idx];
          ctx.fillText(ch, c * CELL_W, r * CELL_H);
        }
      }
    }
  }

  function loop() {
    time += 0.032;
    waveWeight += (asciiTargetWaveWeight - waveWeight) * 0.048;
    drawCanvas(cliCanvas, 16);
    requestAnimationFrame(loop);
  }

  requestAnimationFrame(loop);
}

// ============================================================================
// 6. 2-PAGE VIEW SWITCHER (PAGE 01 HOME <-> PAGE 02 DETAILS)
// ============================================================================

function switchPortfolioView(targetView, sectionId) {
  const homeEl = document.getElementById("view-home");
  const detailsEl = document.getElementById("view-details");
  const headerSwitchBtn = document.getElementById("header-view-switch-btn");
  if (!homeEl || !detailsEl) return;

  const isDetails = targetView === "details";
  homeEl.classList.toggle("active", !isDetails);
  detailsEl.classList.toggle("active", isDetails);

  // Update header toggle button
  if (headerSwitchBtn) {
    if (isDetails) {
      headerSwitchBtn.textContent = "[ ← BACK TO HOME ]";
      headerSwitchBtn.setAttribute("data-view-target", "home");
    } else {
      headerSwitchBtn.textContent = "[ EXPLORE PROJECTS → ]";
      headerSwitchBtn.setAttribute("data-view-target", "details");
    }
  }

  // Update active nav item
  document.querySelectorAll(".minimal-nav .nav-item").forEach((item) => {
    const itemTarget = item.getAttribute("data-view-target");
    const itemScroll = item.getAttribute("data-scroll-target");
    if (!isDetails && itemTarget === "home") {
      item.classList.add("active");
    } else if (isDetails && itemScroll && itemScroll === (sectionId || "capabilities")) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });

  if (isDetails) {
    detailsEl.querySelectorAll(".reveal-on-scroll").forEach((el) => {
      el.classList.add("is-visible");
    });

    if (sectionId) {
      const sec = document.getElementById(sectionId);
      if (sec) {
        setTimeout(() => sec.scrollIntoView({ behavior: "smooth" }), 40);
        return;
      }
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  } else {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

function initViewSwitcher() {
  document.addEventListener("click", (e) => {
    const trigger = e.target.closest("[data-view-target]");
    if (!trigger) return;
    e.preventDefault();
    const targetView = trigger.getAttribute("data-view-target");
    const scrollTarget = trigger.getAttribute("data-scroll-target");
    switchPortfolioView(targetView, scrollTarget);
  });
}

function initCustomCursor() {
  const dot = document.getElementById("cursor-dot");
  const ring = document.getElementById("cursor-ring");
  if (!dot || !ring) return;

  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let ringX = mouseX;
  let ringY = mouseY;

  window.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.left = `${mouseX}px`;
    dot.style.top = `${mouseY}px`;
  });

  function renderRing() {
    ringX += (mouseX - ringX) * 0.18;
    ringY += (mouseY - ringY) * 0.18;
    ring.style.left = `${ringX}px`;
    ring.style.top = `${ringY}px`;
    requestAnimationFrame(renderRing);
  }
  requestAnimationFrame(renderRing);

  document.addEventListener("mouseover", (e) => {
    if (e.target.closest("a, button, .system-row, .pillar-block")) {
      document.body.classList.add("cursor-hover");
    } else {
      document.body.classList.remove("cursor-hover");
    }
  });
}

function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => toast.classList.remove("show"), 2600);
}

// ============================================================================
// BOOTSTRAP
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
  renderPillars();
  renderSystems("all");
  initManifestoScrollWords();
  initScrollRevealsAndCounters();
  initScrollProgress();
  initTypewriter();
  initClock();
  initFiltersAndCLI();
  initViewSwitcher();
  initWaterRippleShaderEngine();
  initAsciiMobiusWaveEngine();
  initCustomCursor();
});




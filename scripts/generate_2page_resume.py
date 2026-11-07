import os
from playwright.sync_api import sync_playwright

def generate_2page_resume():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Mah Qing Tong — Resume (2-Page)</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    @page {
      size: A4;
      margin: 14mm 16mm 14mm 16mm;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #0f172a;
      background: #ffffff;
      font-size: 9.8pt;
      line-height: 1.48;
      -webkit-font-smoothing: antialiased;
    }

    /* Page container */
    .resume-page {
      width: 100%;
      min-height: 260mm;
      position: relative;
    }

    .page-break-before {
      page-break-before: always;
      padding-top: 8px;
    }

    .avoid-break {
      page-break-inside: avoid;
    }

    /* Header */
    .header {
      border-bottom: 2.5px solid #881337;
      padding-bottom: 12px;
      margin-bottom: 14px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }

    .name-title h1 {
      font-size: 22pt;
      font-weight: 700;
      color: #0f172a;
      letter-spacing: -0.02em;
      line-height: 1.1;
    }

    .name-title .title {
      font-size: 11pt;
      font-weight: 600;
      color: #881337;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-top: 4px;
    }

    .contact-info {
      text-align: right;
      font-size: 8.8pt;
      color: #475569;
      line-height: 1.5;
    }

    .contact-info a {
      color: #475569;
      text-decoration: none;
    }

    .contact-info a:hover {
      color: #881337;
    }

    .contact-info .dot {
      color: #94a3b8;
      margin: 0 4px;
    }

    /* Section Headers */
    .section {
      margin-bottom: 14px;
    }

    .section-header {
      display: flex;
      align-items: center;
      gap: 7px;
      font-size: 10.2pt;
      font-weight: 700;
      color: #881337;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 3.5px;
      margin-bottom: 8px;
    }

    .section-header .bar {
      width: 3.5px;
      height: 12px;
      background: #881337;
      border-radius: 1px;
    }

    /* Summary */
    .summary-text {
      color: #334155;
      font-size: 9.6pt;
      line-height: 1.52;
      text-align: justify;
    }

    /* Items (Experience / Projects / Education) */
    .item {
      margin-bottom: 10px;
    }

    .item:last-child {
      margin-bottom: 0;
    }

    .item-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 3px;
    }

    .item-title {
      font-size: 10pt;
      font-weight: 700;
      color: #0f172a;
    }

    .item-subtitle {
      font-size: 9.6pt;
      font-weight: 500;
      color: #475569;
    }

    .item-date {
      font-size: 8.8pt;
      font-weight: 500;
      color: #64748b;
    }

    .item-tags {
      font-size: 8.6pt;
      font-weight: 600;
      color: #881337;
      letter-spacing: 0.01em;
    }

    /* Bullet Points */
    ul.bullets {
      list-style-type: none;
      padding-left: 0;
      margin-top: 3px;
    }

    ul.bullets li {
      position: relative;
      padding-left: 14px;
      margin-bottom: 4px;
      color: #334155;
      font-size: 9.5pt;
      line-height: 1.46;
      text-align: justify;
    }

    ul.bullets li::before {
      content: "•";
      position: absolute;
      left: 2px;
      color: #881337;
      font-weight: bold;
      font-size: 10.5pt;
    }

    ul.bullets li strong {
      color: #0f172a;
      font-weight: 600;
    }

    /* Skills Grid */
    .skills-grid {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .skill-row {
      display: flex;
      font-size: 9.4pt;
      line-height: 1.45;
    }

    .skill-label {
      width: 190px;
      font-weight: 600;
      color: #0f172a;
      flex-shrink: 0;
    }

    .skill-list {
      color: #334155;
      flex-grow: 1;
    }

    /* Leadership & Awards */
    .two-col-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
  </style>
</head>
<body>

  <!-- ============================================================ -->
  <!-- PAGE 1: HEADER, OBJECTIVE, EDUCATION & WORK EXPERIENCE       -->
  <!-- ============================================================ -->
  <div class="resume-page" id="page-1">

  <!-- HEADER -->
  <header class="header">
    <div class="name-title">
      <h1>MAH QING TONG</h1>
      <div class="title">AI / LLM Engineer</div>
    </div>
    <div class="contact-info">
      <div>Subang Jaya, Selangor, Malaysia</div>
      <div>
        <span>016-396 0009</span>
        <span class="dot">•</span>
        <a href="mailto:smartqingtong@gmail.com">smartqingtong@gmail.com</a>
      </div>
      <div>
        <a href="https://linkedin.com">linkedin.com/in/qtong</a>
        <span class="dot">•</span>
        <a href="https://github.com/qtongggg">github.com/qtongggg</a>
      </div>
    </div>
  </header>

  <!-- PROFESSIONAL SUMMARY -->
  <section class="section">
    <div class="section-header">
      <div class="bar"></div>
      <span>Professional Summary</span>
    </div>
    <p class="summary-text">
      <strong>AI/LLM Engineer</strong> at Zetrix AI and Computer Science (Data Science) graduate from <strong>Monash University Malaysia</strong>. Experienced in architecting production Agentic RAG workflows, multi-hop retrieval systems, and autonomous agent graphs. Technically proficient in Python, LangGraph, LangChain, Model Context Protocol (MCP), Qdrant, and FastAPI, with a proven track record specializing in hybrid dense/sparse search, cross-encoder reranking, deterministic tool execution, and Human-in-the-Loop orchestration.
    </p>
  </section>

  <!-- EDUCATION -->
  <section class="section">
    <div class="section-header">
      <div class="bar"></div>
      <span>Education</span>
    </div>
    <div class="item">
      <div class="item-header">
        <div>
          <span class="item-title">Monash University Malaysia</span>
          <span class="item-subtitle"> | Bachelor of Computer Science in Data Science</span>
        </div>
        <span class="item-date">FEB 2023 – DEC 2025</span>
      </div>
      <div style="font-size: 9.3pt; color: #881337; font-weight: 600; margin-bottom: 3px;">
        Second Upper Honours • CGPA: 3.36 / 4.0
      </div>
      <ul class="bullets">
        <li><strong>Relevant Coursework:</strong> Deep Learning, Algorithms & Data Structures, Big Data Management, Data Visualization, Cybersecurity, Object-Oriented Programming.</li>
      </ul>
    </div>
  </section>

  <!-- WORK EXPERIENCE -->
  <section class="section">
    <div class="section-header">
      <div class="bar"></div>
      <span>Work Experience</span>
    </div>

    <!-- Zetrix AI -->
    <div class="item">
      <div class="item-header">
        <div>
          <span class="item-title">Zetrix AI</span>
          <span class="item-subtitle"> | LLM Engineer</span>
        </div>
        <span class="item-date">JUN 2024 – PRESENT</span>
      </div>
      <ul class="bullets">
        <li><strong>Enterprise AI Workflow Automation:</strong> Developed and deployed Dify-based AI workflows for enterprise SOP and knowledge-base retrieval, supporting live customer operations with grounded, hallucination-free LLM responses.</li>
        <li><strong>Section-Aware RAG Ingestion:</strong> Built automated preprocessing pipelines converting complex unstructured PDF research into clean hierarchical Markdown before chunking, improving downstream retrieval recall by 28%.</li>
        <li><strong>Agentic RAG & Deterministic Execution:</strong> Architected the i-FIKR Islamic knowledge agent over 870+ records; integrated vector search with custom Python/Pandas sandbox tools to eliminate tally hallucinations and ensure exact multi-criteria filtering.</li>
        <li><strong>Multi-Hop Retrieval & Sub-Chunk Citations:</strong> Implemented a two-stage retrieval workflow combining catalog-level metadata grounding with targeted document retrieval, enabling cross-document comparisons with verifiable sub-chunk citations.</li>
        <li><strong>Conversational Booking Agent:</strong> Built an interactive property booking agent supporting real-time availability checks, appointment booking, schedule reviews, and automated Human-in-the-Loop (HITL) handoff.</li>
      </ul>
    </div>

    <!-- NIQ (NielsenIQ) -->
    <div class="item" style="margin-top: 10px;">
      <div class="item-header">
        <div>
          <span class="item-title">NIQ (NielsenIQ)</span>
          <span class="item-subtitle"> | Data Input Validation Intern</span>
        </div>
        <span class="item-date">NOV 2024 – FEB 2025</span>
      </div>
      <ul class="bullets">
        <li><strong>Large-Scale Dataset Validation:</strong> Processed and validated large-scale retail datasets averaging thousands of records per batch to ensure high data consistency and integrity for downstream analytics pipelines.</li>
        <li><strong>Rule-Based Anomaly Detection:</strong> Applied logic-driven validation techniques to detect and resolve catalog inconsistencies, reducing manual processing errors and improving regional data reliability.</li>
        <li><strong>Cross-Regional Collaboration:</strong> Collaborated with cross-regional engineering and analytics teams (Malaysia & Vietnam) to debug data issues and standardize pipeline data quality.</li>
      </ul>
    </div>
  </section>
  </div>

  <!-- ============================================================ -->
  <!-- PAGE 2: TECHNICAL PROJECTS, SKILLS, LEADERSHIP & AWARDS     -->
  <!-- ============================================================ -->
  <div class="resume-page page-break-before" id="page-2">

  <!-- TECHNICAL PROJECTS -->
  <section class="section">
    <div class="section-header">
      <div class="bar"></div>
      <span>Key Technical Projects</span>
    </div>

    <!-- Project 1: Personal DeepAgent -->
    <div class="item avoid-break">
      <div class="item-header">
        <span class="item-title">Personal DeepAgent — Autonomous Scholarly Research System</span>
        <span class="item-tags">LangGraph • Hybrid RAG • FlashRank • DuckDB • FastAPI</span>
      </div>
      <ul class="bullets">
        <li>Architected an autonomous agentic research system featuring two-stage hybrid retrieval (dense Chroma + sparse Okapi BM25 RRF) combined with <strong>FlashRank CPU cross-encoder reranking</strong>, eliminating candidate crowding across multi-paper comparisons.</li>
        <li>Engineered autonomous task decomposition (<code>todo_write</code>), virtual workspace filesystem scratchpads (<code>write_file</code>), and deterministic DuckDB SQL catalog verification with 100% citation provenance validation.</li>
        <li>Built an automated <strong>Needle-in-a-Haystack Evaluator</strong> that stress-tests staged chunks with synthetic paraphrased probes before committing, enforcing an 80% recall threshold.</li>
      </ul>
    </div>

    <!-- Project 2: Interactive Portfolio -->
    <div class="item avoid-break" style="margin-top: 10px;">
      <div class="item-header">
        <span class="item-title">Interactive Portfolio & Dify Cloud RAG Agent</span>
        <span class="item-tags">FastAPI • SSE Streaming • WebGL • Dify API</span>
      </div>
      <ul class="bullets">
        <li>Built a full-stack portfolio with an embedded CLI chat agent streaming real-time token responses over Dify Cloud RAG.</li>
        <li>Implemented Harness Engineering conventions with state ledger tracking, Architectural Decision Records (ADRs), and a 3-tier resilient RAG fallback architecture.</li>
      </ul>
    </div>

    <!-- Project 3: AI Job Search -->
    <div class="item avoid-break" style="margin-top: 10px;">
      <div class="item-header">
        <span class="item-title">AI Job Search & Resume Agent</span>
        <span class="item-tags">LangChain • Model Context Protocol (MCP) • Qdrant • Hybrid Search</span>
      </div>
      <ul class="bullets">
        <li>Designed and implemented a multi-agent LLM pipeline automating job retrieval, semantic candidate ranking, and personalized email drafting integrated with the JSearch API.</li>
        <li>Engineered dense + sparse BM25 hybrid search with cross-encoder reranking in Qdrant for semantic resume-job matching.</li>
        <li>Developed a controlled multi-agent orchestration loop managing query rewriting, retrieval, ranking, and final summarization.</li>
      </ul>
    </div>

    <!-- Project 4: F1 Data Text-to-SQL Agent -->
    <div class="item avoid-break" style="margin-top: 10px;">
      <div class="item-header">
        <span class="item-title">F1 Data Text-to-SQL Agent</span>
        <span class="item-tags">Python • PostgreSQL • LangGraph • LangChain</span>
      </div>
      <ul class="bullets">
        <li>Built a workflow-based Text-to-SQL agent converting natural language queries into executable SQL and structured JSON responses with automated database schema inspection and confidence scoring.</li>
        <li>Implemented dynamic matplotlib chart selection and Formula 1 domain-rule logic for sprint points, race statistics, and standings.</li>
      </ul>
    </div>

    <!-- Project 5: Smart Expense Tracker -->
    <div class="item avoid-break" style="margin-top: 10px;">
      <div class="item-header">
        <span class="item-title">Smart Expense Tracker by OCR & AI Analytics</span>
        <span class="item-tags">Kotlin • Firebase • Taggun OCR • Android</span>
      </div>
      <ul class="bullets">
        <li>Developed an end-to-end mobile application with real-time database synchronization and secure user authentication.</li>
        <li>Integrated Taggun OCR and AI-driven categorization to automate receipt text extraction and generate real-time financial insights.</li>
      </ul>
    </div>
  </section>

  <!-- TECHNICAL SKILLS -->
  <section class="section avoid-break">
    <div class="section-header">
      <div class="bar"></div>
      <span>Technical Skills</span>
    </div>
    <div class="skills-grid">
      <div class="skill-row">
        <span class="skill-label">Agentic AI & Orchestration:</span>
        <span class="skill-list">Agentic RAG, LangGraph, LangChain, Model Context Protocol (MCP), Tool Calling, Human-in-the-Loop (HITL), Dify, Prompt & Context Engineering</span>
      </div>
      <div class="skill-row">
        <span class="skill-label">RAG & Information Retrieval:</span>
        <span class="skill-list">Hybrid Search (Dense + Sparse BM25), Qdrant, ChromaDB, FlashRank Cross-Encoder Reranking, Multi-Hop Retrieval, Document Preprocessing, Needle Evaluation</span>
      </div>
      <div class="skill-row">
        <span class="skill-label">Programming & Backend:</span>
        <span class="skill-list">Python, FastAPI, TypeScript, JavaScript, SQL, Kotlin, R, REST API Architecture, Next.js, Server-Sent Events (SSE)</span>
      </div>
      <div class="skill-row">
        <span class="skill-label">Machine Learning & Deep Learning:</span>
        <span class="skill-list">PyTorch, Transformers, BERT, Self-Attention, Prefix Prompt-Tuning, CNNs, Embeddings</span>
      </div>
      <div class="skill-row">
        <span class="skill-label">Databases, Tools & DevOps:</span>
        <span class="skill-list">DuckDB, PostgreSQL, MongoDB, Git, Docker, Linux, Pytest, CI/CD (GitHub Actions)</span>
      </div>
    </div>
  </section>

  <!-- AWARDS & LEADERSHIP -->
  <section class="section avoid-break">
    <div class="two-col-grid">
      <div>
        <div class="section-header">
          <div class="bar"></div>
          <span>Honors & Competitions</span>
        </div>
        <ul class="bullets">
          <li><strong>Monash Coding League 2024:</strong> Competitive programming challenge.</li>
          <li><strong>ExxonMobil DataWorks Challenge 2024:</strong> Data analytics competition.</li>
          <li><strong>Leadership Champ by YCA:</strong> Youth leadership accreditation.</li>
        </ul>
      </div>

      <div>
        <div class="section-header">
          <div class="bar"></div>
          <span>Extracurricular Leadership</span>
        </div>
        <ul class="bullets">
          <li><strong>President:</strong> Diabolo Society, Foon Yew (2019 – 2021).</li>
          <li><strong>Member:</strong> Monash Rock Climbing Club (2024 – 2025).</li>
          <li><strong>Participant:</strong> Badminton Competition Sport Carnival Monash 2025.</li>
        </ul>
      </div>
    </div>
  </section>
  </div>

</body>
</html>"""

    out_dir = r"c:\Users\User\Documents\antigravity\personal-deepagent\docs"
    os.makedirs(out_dir, exist_ok=True)
    html_file = os.path.join(out_dir, "Mah_Qing_Tong_Resume_2Page.html")
    pdf_file = os.path.join(out_dir, "Mah_Qing_Tong_Resume_2Page.pdf")
    p1_img = r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777\resume_2page_preview_p1.png"
    p2_img = r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777\resume_2page_preview_p2.png"

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file:///{html_file.replace(chr(92), '/')}")
        page.wait_for_timeout(1000)

        # Generate exact 2-page A4 PDF
        page.pdf(
            path=pdf_file,
            format="A4",
            margin={"top": "14mm", "bottom": "14mm", "left": "16mm", "right": "16mm"},
            print_background=True
        )

        # Capture element screenshots of Page 1 & Page 2
        page.locator("#page-1").screenshot(path=p1_img)
        page.locator("#page-2").screenshot(path=p2_img)

        browser.close()

    print("2-Page PDF Generated:", pdf_file)
    print("Page 1 Preview:", p1_img)
    print("Page 2 Preview:", p2_img)

if __name__ == "__main__":
    generate_2page_resume()

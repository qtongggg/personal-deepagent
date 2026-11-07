import os
from playwright.sync_api import sync_playwright

def generate_resume():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Mah Qing Tong — Resume</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    @page {
      size: A4;
      margin: 12mm 14mm 12mm 14mm;
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
      font-size: 9.4pt;
      line-height: 1.42;
      -webkit-font-smoothing: antialiased;
    }

    /* Header */
    .header {
      border-bottom: 2px solid #881337;
      padding-bottom: 10px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }

    .name-title h1 {
      font-size: 21pt;
      font-weight: 700;
      color: #0f172a;
      letter-spacing: -0.02em;
      line-height: 1.1;
    }

    .name-title .title {
      font-size: 10.5pt;
      font-weight: 600;
      color: #881337;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-top: 3px;
    }

    .contact-info {
      text-align: right;
      font-size: 8.5pt;
      color: #475569;
      line-height: 1.45;
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
      margin: 0 3px;
    }

    /* Section Headers */
    .section {
      margin-bottom: 11px;
    }

    .section-header {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 9.6pt;
      font-weight: 700;
      color: #881337;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 3px;
      margin-bottom: 7px;
    }

    .section-header .bar {
      width: 3px;
      height: 11px;
      background: #881337;
      border-radius: 1px;
    }

    /* Summary */
    .summary-text {
      color: #334155;
      font-size: 9.2pt;
      line-height: 1.45;
      text-align: justify;
    }

    /* Experience & Projects */
    .item {
      margin-bottom: 8px;
    }

    .item:last-child {
      margin-bottom: 0;
    }

    .item-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 2px;
    }

    .item-title {
      font-size: 9.6pt;
      font-weight: 700;
      color: #0f172a;
    }

    .item-subtitle {
      font-size: 9.2pt;
      font-weight: 500;
      color: #475569;
    }

    .item-date {
      font-size: 8.5pt;
      font-weight: 500;
      color: #64748b;
      font-family: inherit;
    }

    .item-tags {
      font-size: 8.2pt;
      font-weight: 500;
      color: #881337;
      letter-spacing: 0.01em;
    }

    /* Bullet Points */
    ul.bullets {
      list-style-type: none;
      padding-left: 0;
      margin-top: 2px;
    }

    ul.bullets li {
      position: relative;
      padding-left: 13px;
      margin-bottom: 2.5px;
      color: #334155;
      font-size: 9.1pt;
      line-height: 1.4;
      text-align: justify;
    }

    ul.bullets li::before {
      content: "•";
      position: absolute;
      left: 2px;
      color: #881337;
      font-weight: bold;
      font-size: 10pt;
    }

    ul.bullets li strong {
      color: #0f172a;
      font-weight: 600;
    }

    /* Skills Grid */
    .skills-grid {
      display: flex;
      flex-direction: column;
      gap: 3.5px;
    }

    .skill-row {
      display: flex;
      font-size: 9.1pt;
      line-height: 1.38;
    }

    .skill-label {
      width: 175px;
      font-weight: 600;
      color: #0f172a;
      flex-shrink: 0;
    }

    .skill-list {
      color: #334155;
      flex-grow: 1;
    }

    /* 2-Column Grid for Education & Awards */
    .bottom-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
  </style>
</head>
<body>

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
      <strong>AI/LLM Engineer</strong> at Zetrix AI and Computer Science (Data Science) graduate from <strong>Monash University Malaysia</strong>. Experienced in architecting production Agentic RAG workflows, multi-hop retrieval systems, and autonomous agent graphs. Hands-on expertise with LangGraph, LangChain, Model Context Protocol (MCP), Qdrant, and FastAPI, specializing in hybrid dense/sparse search, cross-encoder reranking, deterministic tool execution, and Human-in-the-Loop orchestration.
    </p>
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
        <li><strong>Enterprise AI Workflow Automation:</strong> Developed and deployed Dify-based LLM workflows for enterprise SOP and knowledge-base retrieval, supporting live operations with grounded, citation-backed responses.</li>
        <li><strong>Section-Aware RAG Ingestion:</strong> Built automated document processing pipelines converting complex unstructured PDFs into hierarchical Markdown, improving document consistency and retrieval recall by 28%.</li>
        <li><strong>Agentic RAG & Deterministic Execution:</strong> Architected the i-FIKR Islamic knowledge agent over 870+ records; integrated vector search with custom Python/Pandas sandbox tools to eliminate tally hallucinations and ensure exact filtering.</li>
        <li><strong>Multi-Hop Retrieval & Sub-Chunk Citations:</strong> Engineered two-stage retrieval combining catalog-level metadata grounding with surgical chunk retrieval, enabling precise cross-document comparisons.</li>
        <li><strong>Conversational Booking Agent:</strong> Implemented interactive agent handling real-time availability checks, appointment scheduling, and automated Human-in-the-Loop (HITL) handoff.</li>
      </ul>
    </div>

    <!-- NIQ -->
    <div class="item" style="margin-top: 6px;">
      <div class="item-header">
        <div>
          <span class="item-title">NIQ (NielsenIQ)</span>
          <span class="item-subtitle"> | Data Input Validation Intern</span>
        </div>
        <span class="item-date">NOV 2024 – FEB 2025</span>
      </div>
      <ul class="bullets">
        <li><strong>Dataset Validation at Scale:</strong> Processed and validated large-scale retail datasets across thousands of records per batch, maintaining strict data integrity for downstream analytics pipelines.</li>
        <li><strong>Rule-Based Anomaly Detection:</strong> Applied automated validation techniques to flag catalog discrepancies, boosting data reliability across Malaysia and Vietnam regional teams.</li>
      </ul>
    </div>
  </section>

  <!-- TECHNICAL PROJECTS -->
  <section class="section">
    <div class="section-header">
      <div class="bar"></div>
      <span>Technical Projects</span>
    </div>

    <!-- Project 1: Personal DeepAgent -->
    <div class="item">
      <div class="item-header">
        <span class="item-title">Personal DeepAgent — Autonomous Scholarly Research System</span>
        <span class="item-tags">LangGraph • Hybrid RAG • FlashRank • DuckDB • FastAPI</span>
      </div>
      <ul class="bullets">
        <li>Architected an autonomous research agent featuring two-stage hybrid retrieval (dense Chroma + sparse BM25 RRF) and <strong>FlashRank CPU cross-encoder reranking</strong>, eliminating candidate crowding across multi-paper comparisons.</li>
        <li>Engineered autonomous task decomposition (<code>todo_write</code>), virtual workspace filesystem scratchpads (<code>write_file</code>), deterministic DuckDB SQL catalog verification, and an automated Needle-in-a-Haystack recall evaluator.</li>
      </ul>
    </div>

    <!-- Project 2: Interactive Portfolio -->
    <div class="item">
      <div class="item-header">
        <span class="item-title">Interactive Portfolio & Dify Cloud RAG Agent</span>
        <span class="item-tags">FastAPI • SSE Streaming • WebGL • Dify API</span>
      </div>
      <ul class="bullets">
        <li>Built full-stack portfolio with an embedded CLI chat agent streaming real-time token responses over Dify Cloud RAG.</li>
        <li>Implemented Harness Engineering conventions with state ledger tracking, Architectural Decision Records, and a 3-tier resilient RAG fallback architecture.</li>
      </ul>
    </div>

    <!-- Project 3: AI Job Search -->
    <div class="item">
      <div class="item-header">
        <span class="item-title">AI Job Search & Resume Agent</span>
        <span class="item-tags">LangChain • Model Context Protocol (MCP) • Qdrant • Hybrid Search</span>
      </div>
      <ul class="bullets">
        <li>Engineered a multi-agent LLM pipeline automating job retrieval, ranking, and customized email outreach via JSearch API.</li>
        <li>Implemented dense + sparse BM25 hybrid search with cross-encoder reranking in Qdrant for semantic resume-job matching.</li>
      </ul>
    </div>
  </section>

  <!-- TECHNICAL SKILLS -->
  <section class="section">
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
        <span class="skill-list">Python, FastAPI, TypeScript, JavaScript, SQL, REST API Architecture, Next.js, Server-Sent Events (SSE)</span>
      </div>
      <div class="skill-row">
        <span class="skill-label">Data & Developer Tools:</span>
        <span class="skill-list">DuckDB, PostgreSQL, MongoDB, Git, Docker, Linux, Pytest, CI/CD (GitHub Actions)</span>
      </div>
    </div>
  </section>

  <!-- BOTTOM: EDUCATION & LEADERSHIP -->
  <section class="section" style="margin-bottom: 0;">
    <div class="bottom-grid">
      <!-- Education -->
      <div>
        <div class="section-header">
          <div class="bar"></div>
          <span>Education</span>
        </div>
        <div class="item-title">Bachelor of Computer Science in Data Science</div>
        <div class="item-subtitle" style="font-weight: 600; color: #881337;">Second Upper Honours</div>
        <div style="font-size: 8.8pt; color: #475569; margin-top: 1px;">Monash University Malaysia • 2023 – 2025</div>
        <div style="font-size: 8.2pt; color: #64748b; margin-top: 2px;">Coursework: Deep Learning, Algorithms, Big Data, Visualization</div>
      </div>

      <!-- Leadership & Awards -->
      <div>
        <div class="section-header">
          <div class="bar"></div>
          <span>Awards & Leadership</span>
        </div>
        <ul class="bullets">
          <li><strong>Awards:</strong> Monash Coding League 2024, ExxonMobil DataWorks Challenge 2024</li>
          <li><strong>Leadership:</strong> President of Diabolo Society (Foon Yew) • Monash Rock Climbing Club</li>
        </ul>
      </div>
    </div>
  </section>

</body>
</html>"""

    out_dir = r"c:\Users\User\Documents\antigravity\personal-deepagent\docs"
    os.makedirs(out_dir, exist_ok=True)
    html_file = os.path.join(out_dir, "Mah_Qing_Tong_Resume_Revamped.html")
    pdf_file = os.path.join(out_dir, "Mah_Qing_Tong_Resume_Revamped.pdf")
    img_file = r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777\resume_revamped_preview.png"

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file:///{html_file.replace(chr(92), '/')}")
        page.wait_for_timeout(1000)

        # Generate exact 1-page A4 PDF
        page.pdf(
            path=pdf_file,
            format="A4",
            margin={"top": "12mm", "bottom": "12mm", "left": "14mm", "right": "14mm"},
            print_background=True
        )

        # Also capture screenshot of the rendered page for instant user preview
        page.set_viewport_size({"width": 820, "height": 1160})
        page.screenshot(path=img_file, full_page=True)
        browser.close()

    print("PDF Generated:", pdf_file)
    print("Preview Image:", img_file)

if __name__ == "__main__":
    generate_resume()

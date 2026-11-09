import os
import fitz  # PyMuPDF
from playwright.sync_api import sync_playwright

def generate_2page_resume():
    # Absolute paths
    docs_dir = r"c:\Users\User\Documents\antigravity\personal-deepagent\docs"
    html_file = os.path.join(docs_dir, "Mah_Qing_Tong_Resume_2Page.html")
    pdf_file = os.path.join(docs_dir, "Mah_Qing_Tong_Resume_2Page.pdf")
    photo_file = os.path.join(docs_dir, "profile_photo.jpg").replace(chr(92), "/")
    
    p1_img = r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777\resume_2page_preview_p1.png"
    p2_img = r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777\resume_2page_preview_p2.png"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Mah Qing Tong — Resume</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    @page {{
      size: A4;
      margin: 10.5mm 14mm 10.5mm 14mm;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #0f172a;
      background: #ffffff;
      font-size: 9.15pt;
      line-height: 1.42;
      -webkit-font-smoothing: antialiased;
    }}

    .resume-page {{
      width: 100%;
      box-sizing: border-box;
    }}

    .page-break-before {{
      page-break-before: always;
      padding-top: 4px;
    }}

    .avoid-break {{
      page-break-inside: avoid;
    }}

    /* Header */
    .header {{
      border-bottom: 2px solid #881337;
      padding-bottom: 8px;
      margin-bottom: 9px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .header-left {{
      flex: 1;
    }}

    .name-title h1 {{
      font-size: 21pt;
      font-weight: 700;
      color: #0f172a;
      letter-spacing: -0.02em;
      line-height: 1.1;
    }}

    .name-title .title {{
      font-size: 10.2pt;
      font-weight: 600;
      color: #881337;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-top: 2px;
    }}

    .contact-info {{
      font-size: 8.5pt;
      color: #475569;
      line-height: 1.42;
      margin-top: 5px;
    }}

    .contact-info a {{
      color: #475569;
      text-decoration: none;
    }}

    .contact-info a:hover {{
      color: #881337;
    }}

    .contact-info .dot {{
      color: #94a3b8;
      margin: 0 4px;
    }}

    /* Photo: larger size, no red border, clean subtle shadow */
    .header-photo {{
      width: 90px;
      height: 102px;
      object-fit: cover;
      border-radius: 8px;
      border: none;
      margin-left: 16px;
      flex-shrink: 0;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.12);
    }}

    /* Section Headers */
    .section {{
      margin-bottom: 9px;
    }}

    .section-header {{
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 5px;
      padding-bottom: 2px;
      border-bottom: 1px solid #e2e8f0;
    }}

    .section-header .bar {{
      width: 4px;
      height: 12px;
      background-color: #881337;
      border-radius: 2px;
    }}

    .section-header span {{
      font-size: 9.5pt;
      font-weight: 700;
      color: #881337;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}

    .section-subtitle {{
      font-size: 8.2pt;
      color: #64748b;
      margin-top: -3px;
      margin-bottom: 5px;
      font-style: italic;
    }}

    /* Paragraphs and Items */
    .summary-text {{
      color: #334155;
      text-align: justify;
      font-size: 9.05pt;
      line-height: 1.42;
    }}

    .item {{
      margin-bottom: 7px;
    }}

    .item:last-child {{
      margin-bottom: 0;
    }}

    .item-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 2px;
    }}

    .item-title {{
      font-size: 9.4pt;
      font-weight: 700;
      color: #0f172a;
    }}

    .item-subtitle {{
      font-size: 8.95pt;
      font-weight: 600;
      color: #334155;
    }}

    .item-date {{
      font-size: 8.3pt;
      font-weight: 600;
      color: #64748b;
      white-space: nowrap;
    }}

    .item-tags {{
      font-size: 8.05pt;
      font-family: 'JetBrains Mono', monospace;
      color: #881337;
      font-weight: 500;
    }}

    /* Bullets */
    .bullets {{
      list-style-type: none;
      padding-left: 0;
      margin-top: 2px;
    }}

    .bullets li {{
      position: relative;
      padding-left: 12px;
      margin-bottom: 2.2px;
      color: #334155;
      font-size: 8.95pt;
      line-height: 1.38;
      text-align: justify;
    }}

    .bullets li:last-child {{
      margin-bottom: 0;
    }}

    .bullets li::before {{
      content: "•";
      position: absolute;
      left: 1px;
      color: #881337;
      font-size: 10.5pt;
      line-height: 1.1;
    }}

    .bullets strong {{
      color: #0f172a;
      font-weight: 600;
    }}

    /* Skills Grid */
    .skills-grid {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .skill-row {{
      display: flex;
      font-size: 8.85pt;
      line-height: 1.37;
    }}

    .skill-label {{
      width: 195px;
      font-weight: 600;
      color: #0f172a;
      flex-shrink: 0;
    }}

    .skill-list {{
      color: #334155;
      flex-grow: 1;
    }}
  </style>
</head>
<body>

  <!-- ============================================================ -->
  <!-- PAGE 1: HEADER (WITH PHOTO), SUMMARY, SKILLS, EXPERIENCE     -->
  <!-- ============================================================ -->
  <div class="resume-page" id="page-1">

    <!-- HEADER WITH TOP-RIGHT PHOTO (NO RED BORDER, PROMINENT SIZE) -->
    <header class="header">
      <div class="header-left">
        <div class="name-title">
          <h1>MAH QING TONG</h1>
          <div class="title">LLM ENGINEER | AI ENGINEER</div>
        </div>
        <div class="contact-info">
          <div>
            <span>Subang Jaya, Selangor, Malaysia</span>
            <span class="dot">•</span>
            <span>016-396 0009</span>
            <span class="dot">•</span>
            <a href="mailto:smartqingtong@gmail.com">smartqingtong@gmail.com</a>
          </div>
          <div>
            <a href="https://linkedin.com/in/qtong">linkedin.com/in/qtong</a>
            <span class="dot">•</span>
            <a href="https://github.com/qtongggg">github.com/qtongggg</a>
          </div>
        </div>
      </div>
      <img src="file:///{photo_file}" class="header-photo" alt="Mah Qing Tong" />
    </header>

    <!-- PROFESSIONAL SUMMARY (UPDATED: SKILLS HARNESS & EVALUATIONS) -->
    <section class="section">
      <div class="section-header">
        <div class="bar"></div>
        <span>Professional Summary</span>
      </div>
      <p class="summary-text">
        <strong>LLM Engineer at Zetrix AI</strong> with a Bachelor of Computer Science in Data Science from <strong>Monash University Malaysia</strong>. Experienced in architecting production Agentic RAG workflows, autonomous multi-agent systems, and modular <strong>Agent Skills (<code>SKILL.md</code> / MCP)</strong>. Specializing in <strong>Harness Engineering</strong> (step-budget guardrails, context compaction, sandboxed tool execution, automated self-correction) and <strong>Rigorous Evaluation</strong> (automated Needle-in-a-Haystack benchmarks, retrieval recall, and faithfulness scoring). Hands-on expertise in hybrid vector/BM25 retrieval, cross-encoder reranking, and full-stack backend development for robust enterprise AI applications.
      </p>
    </section>

    <!-- TECHNICAL SKILLS -->
    <section class="section">
      <div class="section-header">
        <div class="bar"></div>
        <span>Technical Skills</span>
      </div>
      <div class="skills-grid">
        <div class="skill-row">
          <span class="skill-label">LLM & Agentic Systems:</span>
          <span class="skill-list">LangChain, LangGraph, Agent Skills (SKILL.md), Model Context Protocol (MCP), Dify, Multi-Agent Orchestration, Human-in-the-Loop (HITL), Prompt Engineering</span>
        </div>
        <div class="skill-row">
          <span class="skill-label">Harness Engineering & Evals:</span>
          <span class="skill-list">Step-Budget Guardrails, Context Compaction, Sandboxed Execution, Automated Self-Correction Loops, Needle-in-a-Haystack Evals, Faithfulness Benchmarking</span>
        </div>
        <div class="skill-row">
          <span class="skill-label">RAG & Information Retrieval:</span>
          <span class="skill-list">Hybrid Search, Dense & Sparse Retrieval (BM25), Qdrant, ChromaDB, Cross-Encoder Reranking, Multi-Hop Retrieval, Hierarchical Ingestion</span>
        </div>
        <div class="skill-row">
          <span class="skill-label">Programming & Backend:</span>
          <span class="skill-list">Python, FastAPI, TypeScript, JavaScript, SQL, REST APIs, Next.js, Server-Sent Events (SSE)</span>
        </div>
        <div class="skill-row">
          <span class="skill-label">Machine Learning & Tools:</span>
          <span class="skill-list">PyTorch, Hugging Face Transformers, BERT Prefix Prompt-Tuning, PostgreSQL, DuckDB, MongoDB, Git, Docker, Linux, Pytest, CI/CD</span>
        </div>
      </div>
    </section>

    <!-- PROFESSIONAL EXPERIENCE -->
    <section class="section">
      <div class="section-header">
        <div class="bar"></div>
        <span>Professional Experience</span>
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
          <li><strong>Enterprise AI Workflow Automation:</strong> Developed Dify-based AI workflows for enterprise SOP and knowledge-base retrieval, grounding LLM responses in internal documentation to improve answer relevance and consistency for customer operations.</li>
          <li><strong>Section-Aware RAG Ingestion:</strong> Built automated preprocessing pipelines to convert unstructured PDF research into hierarchical Markdown before chunking, improving downstream retrieval recall by 28% in measured evaluations.</li>
          <li><strong>Agentic RAG & Deterministic Execution:</strong> Developed the i-FIKR Islamic knowledge agent over 870+ records, integrating vector search with custom Python and Pandas tools for accurate multi-criteria filtering and tally operations.</li>
          <li><strong>Multi-Hop Retrieval & Citation Grounding:</strong> Implemented a two-stage retrieval workflow combining catalog-level metadata grounding with targeted document retrieval, enabling cross-document comparisons with verifiable sub-chunk citations.</li>
          <li><strong>Conversational Booking Agent:</strong> Built an interactive property booking agent supporting real-time availability checks, appointment booking, schedule reviews, and Human-in-the-Loop (HITL) handoffs.</li>
        </ul>
      </div>

      <!-- NIQ (NielsenIQ) -->
      <div class="item" style="margin-top: 6px;">
        <div class="item-header">
          <div>
            <span class="item-title">NIQ (NielsenIQ)</span>
            <span class="item-subtitle"> | Data Input Validation Intern</span>
          </div>
          <span class="item-date">NOV 2024 – FEB 2025</span>
        </div>
        <ul class="bullets">
          <li><strong>Large-Scale Dataset Validation:</strong> Processed and validated retail datasets containing thousands of records per batch, ensuring data consistency and integrity for downstream analytics.</li>
          <li><strong>Rule-Based Anomaly Detection:</strong> Applied logic-driven validation techniques to identify catalog inconsistencies and data anomalies, improving regional data reliability.</li>
          <li><strong>Cross-Regional Collaboration:</strong> Collaborated with Malaysia and Vietnam teams to investigate data issues and standardise data validation practices.</li>
        </ul>
      </div>
    </section>

  </div>

  <!-- ============================================================ -->
  <!-- PAGE 2: SELECTED TECHNICAL PROJECTS, EDUCATION, HONORS       -->
  <!-- ============================================================ -->
  <div class="resume-page page-break-before" id="page-2">

    <!-- SELECTED TECHNICAL PROJECTS -->
    <section class="section">
      <div class="section-header">
        <div class="bar"></div>
        <span>Selected Technical Projects</span>
      </div>
      <div class="section-subtitle">AI application development • RAG • Agentic systems • Backend engineering</div>

      <!-- Combined Project: Personal DeepAgent & Kinetic Portfolio -->
      <div class="item avoid-break">
        <div class="item-header">
          <span class="item-title">Personal DeepAgent — Autonomous AI Agent System & Kinetic Portfolio</span>
          <span class="item-tags">LangGraph • Agent Skills • Hybrid RAG • FastAPI • DuckDB • FlashRank • Next.js • SSE</span>
        </div>
        <ul class="bullets">
          <li>Architected a multi-agent orchestration graph featuring dynamic planning with step-budget guardrails, a ReAct research agent, and modular sub-agent workers with isolated execution.</li>
          <li>Implemented modular Agent Skills (<code>SKILL.md</code> / MCP) and hybrid retrieval combining dense vector embeddings with sparse BM25 indexing in DuckDB and FlashRank cross-encoder reranking.</li>
          <li>Engineered deterministic tool execution for system commands, multi-engine web search, and file operations with automated failure recovery and self-correction loops.</li>
          <li>Integrated a full-stack kinetic portfolio web interface (Next.js, Tailwind CSS) powered by an asynchronous FastAPI backend with Server-Sent Events (SSE) streaming and Human-in-the-Loop approval workflows.</li>
        </ul>
      </div>

      <!-- Project 2: AI Job Search & Resume Agent -->
      <div class="item avoid-break" style="margin-top: 6px;">
        <div class="item-header">
          <span class="item-title">AI Job Search & Resume Agent</span>
          <span class="item-tags">LangChain • MCP • Qdrant • Hybrid Search • JSearch API</span>
        </div>
        <ul class="bullets">
          <li>Designed a multi-agent LLM application automating job discovery, semantic candidate ranking, resume analysis, and personalised email drafting.</li>
          <li>Implemented dense and sparse BM25 hybrid retrieval with cross-encoder reranking in Qdrant for high-precision resume-to-job matching.</li>
          <li>Developed an orchestration workflow managing query rewriting, information retrieval, ranking, and final response generation.</li>
        </ul>
      </div>

      <!-- Project 3: Smart Expense Tracker by OCR & AI Analytics -->
      <div class="item avoid-break" style="margin-top: 6px;">
        <div class="item-header">
          <span class="item-title">Smart Expense Tracker by OCR & AI Analytics</span>
          <span class="item-tags">Kotlin • Firebase • Taggun OCR • Real-Time Database • Mobile Architecture</span>
        </div>
        <ul class="bullets">
          <li>Developed an end-to-end mobile application using Kotlin and Firebase, enabling real-time database synchronization and secure user authentication.</li>
          <li>Integrated Taggun OCR and AI-driven categorization to automate receipt text extraction and generate real-time financial insights for users.</li>
        </ul>
      </div>
    </section>

    <!-- EDUCATION (EXPANDED WITH UNIVERSITY LIFE LEARNINGS & RESEARCH) -->
    <section class="section avoid-break" style="margin-top: 8px;">
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
        <div style="font-size: 8.9pt; color: #881337; font-weight: 600; margin-top: 1px; margin-bottom: 2px;">
          Second Upper Honours • CGPA: 3.36 / 4.00
        </div>
        <ul class="bullets">
          <li><strong>Deep Learning & Neural Architectures:</strong> Implemented Multi-Head Self-Attention modules, Position-wise Feed-Forward networks, and Transformer Encoders from scratch in PyTorch; architected Prefix Prompt-Tuning pipelines for BERT adaptation and evaluated RNN/LSTM/GRU sequential models across multi-class benchmarks.</li>
          <li><strong>Computer Science & Data Science Foundations:</strong> Mastered advanced Algorithms & Data Structures, Big Data Management, Data Visualization, Relational & Distributed Databases, Cybersecurity principles, and Object-Oriented Software Engineering.</li>
        </ul>
      </div>
    </section>

    <!-- SELECTED HONORS & COMPETITIONS -->
    <section class="section avoid-break" style="margin-top: 8px;">
      <div class="section-header">
        <div class="bar"></div>
        <span>Selected Honors & Competitions</span>
      </div>
      <ul class="bullets">
        <li><strong>Monash Coding League 2024:</strong> Competitive algorithmic programming challenge.</li>
        <li><strong>ExxonMobil DataWorks Challenge 2024:</strong> Data analytics and predictive modeling competition.</li>
        <li><strong>Leadership Champ by YCA:</strong> Youth leadership accreditation.</li>
      </ul>
    </section>

  </div>

</body>
</html>"""

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
            margin={"top": "10.5mm", "bottom": "10.5mm", "left": "14mm", "right": "14mm"},
            print_background=True
        )

        # Capture element screenshots of Page 1 & Page 2
        page.locator("#page-1").screenshot(path=p1_img)
        page.locator("#page-2").screenshot(path=p2_img)

        browser.close()

    # PyMuPDF verification
    doc = fitz.open(pdf_file)
    page_count = len(doc)
    print("---------------------------------------------")
    print(f"VERIFICATION: Actual PDF Page Count = {page_count}")
    for idx, pg in enumerate(doc):
        text = pg.get_text()
        print(f"  Page {idx + 1} character count: {len(text)} | rect: {pg.rect}")
    print("---------------------------------------------")
    
    assert page_count == 2, f"Expected exactly 2 pages, but got {page_count} pages!"
    print("SUCCESS: PDF is verified to be EXACTLY 2 pages with top-right photo!")

if __name__ == "__main__":
    generate_2page_resume()

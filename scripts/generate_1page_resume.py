import os
import fitz  # PyMuPDF
from playwright.sync_api import sync_playwright

def generate_1page_resume():
    # Absolute paths
    docs_dir = r"c:\Users\User\Documents\antigravity\personal-deepagent\docs"
    html_file = os.path.join(docs_dir, "Mah_Qing_Tong_Resume_1Page.html")
    pdf_file = os.path.join(docs_dir, "Mah_Qing_Tong_Resume_1Page.pdf")
    preview_img = r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777\resume_1page_preview.png"

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Mah Qing Tong — Resume</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    @page {
      size: A4;
      margin: 9mm 13.5mm 9mm 13.5mm;
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
      font-size: 8.95pt;
      line-height: 1.39;
      -webkit-font-smoothing: antialiased;
    }

    /* HEADER */
    .header {
      border-bottom: 2px solid #881337;
      padding-bottom: 7px;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }

    .header-left {
      flex-shrink: 0;
    }

    .name-title h1 {
      font-size: 19.5pt;
      font-weight: 700;
      color: #0f172a;
      letter-spacing: -0.02em;
      line-height: 1.1;
      white-space: nowrap;
    }

    .name-title .title {
      font-size: 9.7pt;
      font-weight: 600;
      color: #881337;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-top: 2px;
      white-space: nowrap;
    }

    .contact-info {
      text-align: right;
      font-size: 8.4pt;
      color: #475569;
      line-height: 1.42;
      margin-left: 14px;
    }

    .contact-info a {
      color: #881337;
      text-decoration: none;
      font-weight: 500;
    }

    .contact-info a:hover {
      text-decoration: underline;
    }

    .contact-info .dot {
      color: #94a3b8;
      margin: 0 4px;
    }

    /* SECTION HEADERS */
    .section {
      margin-bottom: 7.2px;
    }

    .section-header {
      display: flex;
      align-items: center;
      gap: 5px;
      margin-bottom: 4px;
      padding-bottom: 1px;
      border-bottom: 1px solid #e2e8f0;
    }

    .section-header .bar {
      width: 3.5px;
      height: 11px;
      background-color: #881337;
      border-radius: 2px;
    }

    .section-header span {
      font-size: 9.2pt;
      font-weight: 700;
      color: #881337;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* TEXT & SUMMARY */
    .summary-text {
      color: #334155;
      text-align: justify;
      font-size: 8.9pt;
      line-height: 1.38;
    }

    /* ITEMS */
    .item {
      margin-bottom: 5px;
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
      font-size: 9.25pt;
      font-weight: 700;
      color: #0f172a;
    }

    .item-subtitle {
      font-size: 8.85pt;
      font-weight: 600;
      color: #334155;
    }

    .item-date {
      font-size: 8.2pt;
      font-weight: 600;
      color: #64748b;
      white-space: nowrap;
      text-align: right;
    }

    .item-tags {
      font-size: 8.0pt;
      font-family: 'JetBrains Mono', monospace;
      color: #881337;
      font-weight: 500;
      text-align: right;
      margin-left: auto;
      line-height: 1.35;
    }

    .tag-item {
      display: inline-block;
      white-space: nowrap;
    }

    .tag-sep {
      color: #881337;
      margin: 0 3px;
    }

    /* BULLETS: PURE STATIC FLOW FOR 100% ATS ORDER */
    .bullets {
      list-style-type: square;
      padding-left: 14px;
      margin-top: 2px;
    }

    .bullets li {
      margin-bottom: 1.8px;
      color: #334155;
      font-size: 8.8pt;
      line-height: 1.36;
      text-align: justify;
    }

    .bullets li::marker {
      color: #881337;
      font-size: 8pt;
    }

    .bullets li:last-child {
      margin-bottom: 0;
    }

    .bullets strong {
      color: #0f172a;
      font-weight: 600;
    }

    /* SKILLS GRID */
    .skills-grid {
      display: flex;
      flex-direction: column;
      gap: 2.5px;
    }

    .skill-row {
      display: flex;
      font-size: 8.7pt;
      line-height: 1.35;
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
  </style>
</head>
<body>

  <!-- HEADER -->
  <header class="header">
    <div class="header-left">
      <div class="name-title">
        <h1>MAH QING TONG</h1>
        <div class="title">LLM ENGINEER | AI ENGINEER</div>
      </div>
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
        <a href="https://www.linkedin.com/in/qing-tong-mah-611a18276">linkedin.com/in/qing-tong-mah-611a18276</a>
        <span class="dot">•</span>
        <a href="https://github.com/qtongggg">github.com/qtongggg</a>
      </div>
    </div>
  </header>

  <!-- PROFESSIONAL SUMMARY (PUNCHY, 2-3 LINES WITH PIC) -->
  <section class="section">
    <div class="section-header">
      <div class="bar"></div>
      <span>Professional Summary</span>
    </div>
    <p class="summary-text">
      <strong>Solutions-driven LLM Engineer at Zetrix AI</strong> (BCompSc Data Science, <strong>Monash University Malaysia</strong>). Proven track record in architecting production Agentic RAG systems (Hybrid Search & System-1 Decision Rerankers) and modular Agent Skills (<code>SKILL.md</code> / MCP). Frequently serving as Person-in-Charge (PIC) across key AI initiatives, bridging business requirements with robust technical architecture from initial scoping to production delivery.
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
        <span class="skill-label">LLM & Agent Systems:</span>
        <span class="skill-list">LangGraph, LangChain, Dify (Agent Workflows & Knowledge Bases), Model Context Protocol (MCP), Agent Skills (SKILL.md), Multi-Agent Orchestration, Human-in-the-Loop (HITL), Prompt Engineering</span>
      </div>
      <div class="skill-row">
        <span class="skill-label">RAG & Retrieval:</span>
        <span class="skill-list">Hybrid Search, Dense & Sparse Retrieval (BM25), Qdrant, ChromaDB, Decision Rerankers (Jev / System-1), Cross-Encoder Reranking, Multi-Hop Retrieval, Document Preprocessing</span>
      </div>
      <div class="skill-row">
        <span class="skill-label">Programming & Backend:</span>
        <span class="skill-list">Python, FastAPI, TypeScript, JavaScript, SQL, REST APIs, Next.js, Server-Sent Events (SSE)</span>
      </div>
      <div class="skill-row">
        <span class="skill-label">Machine Learning & DevOps:</span>
        <span class="skill-list">PyTorch, Hugging Face Transformers, BERT Prefix Prompt-Tuning, Docker, Linux, Git, PostgreSQL, DuckDB, CI/CD</span>
      </div>
    </div>
  </section>

  <!-- TECHNICAL PROJECTS (FEATURED UP FRONT) -->
  <section class="section">
    <div class="section-header">
      <div class="bar"></div>
      <span>Technical Projects</span>
    </div>

    <!-- Project 1: Personal DeepAgent -->
    <div class="item">
      <div class="item-header">
        <span class="item-title">Personal DeepAgent — AI Agent System</span>
        <div class="item-tags">
          <span class="tag-item">LangGraph</span>
          <span class="tag-item"><span class="tag-sep">•</span>Skill-Driven (P2)</span>
          <span class="tag-item"><span class="tag-sep">•</span>Hybrid RAG</span>
          <span class="tag-item"><span class="tag-sep">•</span>Decision Reranker</span>
          <span class="tag-item"><span class="tag-sep">•</span>Jev System-1</span>
          <span class="tag-item"><span class="tag-sep">•</span>DuckDB</span>
          <span class="tag-item"><span class="tag-sep">•</span>FastAPI</span>
        </div>
      </div>
      <ul class="bullets">
        <li>Architected a <strong>Skill-Driven Agent Harness (Paradigm 2)</strong> in LangGraph featuring <strong>just-in-time SOP discovery</strong> via <code>SKILL.md</code>, active task planning (<code>to_dos</code>), and virtual scratchpad context management.</li>
        <li>Implemented two-stage <strong>hybrid retrieval</strong> (ChromaDB + BM25) and a <strong>System-1 Decision Reranker (TypeSafe AI)</strong> with 3-way <code>choice</code> rubrics and noise-pruning gates to eliminate distractor chunks prior to synthesis.</li>
        <li>Engineered an automated <strong>2-layer RAG evaluation harness</strong> utilizing Jev decision models (<code>score</code>, <code>choice</code>, <code>noul</code>) for sub-300ms chunk boundary audits and answer relevance grading, slashing eval costs by <strong>90%</strong> ($0 output token fees).</li>
        <li>Built an interactive web arena powered by an asynchronous <strong>FastAPI backend</strong> with <strong>Server-Sent Events (SSE) streaming</strong>, deterministic DuckDB SQL metadata verification, and post-synthesis defensive guardrails.</li>
      </ul>
    </div>

    <!-- Project 2: AI Job Search & Resume Agent -->
    <div class="item" style="margin-top: 5px;">
      <div class="item-header">
        <span class="item-title">AI Job Search & Resume Agent</span>
        <div class="item-tags">
          <span class="tag-item">LangChain</span>
          <span class="tag-item"><span class="tag-sep">•</span>MCP</span>
          <span class="tag-item"><span class="tag-sep">•</span>Qdrant</span>
          <span class="tag-item"><span class="tag-sep">•</span>Hybrid Search</span>
          <span class="tag-item"><span class="tag-sep">•</span>JSearch API</span>
        </div>
      </div>
      <ul class="bullets">
        <li>Designed a <strong>multi-agent LLM application</strong> automating job discovery, semantic candidate ranking, resume analysis, and personalised outreach drafting.</li>
        <li>Implemented dense and sparse BM25 <strong>hybrid retrieval with cross-encoder reranking</strong> in <strong>Qdrant</strong> for high-precision resume-to-job matching.</li>
        <li>Developed an <strong>orchestration workflow</strong> managing query rewriting, information retrieval, ranking, and final response generation.</li>
      </ul>
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
        <span class="item-date">JUN 2026 – PRESENT</span>
      </div>
      <ul class="bullets">
        <li><strong>Enterprise AI Workflows & Automated QA Agent:</strong> Architected Dify-based AI workflows for enterprise SOP retrieval and developed an automated batch QA evaluation agent, slashing manual regression testing time by over 70% while guaranteeing multi-turn accuracy.</li>
        <li><strong>Section-Aware RAG Ingestion:</strong> Built automated preprocessing pipelines converting unstructured PDF research into hierarchical Markdown before chunking, improving downstream retrieval recall by 28% in measured evaluations.</li>
        <li><strong>Agentic RAG & Deterministic Execution:</strong> Developed the i-FIKR Islamic knowledge agent over 870+ records, integrating vector search with custom Python and Pandas tools for accurate multi-criteria filtering and tally operations.</li>
        <li><strong>Multi-Hop Retrieval & Citation Grounding:</strong> Implemented a two-stage retrieval workflow combining catalog-level metadata grounding with targeted document retrieval, enabling cross-document comparisons with verifiable sub-chunk citations.</li>
      </ul>
    </div>

    <!-- NIQ (NielsenIQ) -->
    <div class="item" style="margin-top: 5px;">
      <div class="item-header">
        <div>
          <span class="item-title">NIQ (NielsenIQ)</span>
          <span class="item-subtitle"> | Data Input Validation Intern</span>
        </div>
        <span class="item-date">NOV 2024 – FEB 2025</span>
      </div>
      <ul class="bullets">
        <li><strong>Large-Scale Dataset Validation:</strong> Processed and validated retail datasets containing thousands of records per batch, ensuring data consistency and integrity for downstream analytics.</li>
        <li><strong>Rule-Based Anomaly Detection:</strong> Applied logic-driven validation techniques to identify catalog inconsistencies across regional data pipelines (Malaysia & Vietnam).</li>
      </ul>
    </div>
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
      <div style="font-size: 8.5pt; color: #881337; font-weight: 600; margin-top: 1px; margin-bottom: 1.5px;">
        CGPA: 3.36 / 4.00
      </div>
      <ul class="bullets">
        <li><strong>Deep Learning & Neural Architectures:</strong> Implemented Multi-Head Self-Attention modules, Position-wise Feed-Forward networks, and Transformer Encoders from scratch in PyTorch; architected Prefix Prompt-Tuning pipelines for BERT model adaptation.</li>
      </ul>
    </div>
  </section>

</body>
</html>"""

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Safe handling if PDF is currently opened
    old_pdf = pdf_file + ".old"
    if os.path.exists(old_pdf):
        try:
            os.remove(old_pdf)
        except Exception:
            pass
    if os.path.exists(pdf_file):
        try:
            with open(pdf_file, "ab"):
                pass
        except PermissionError:
            os.rename(pdf_file, old_pdf)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file:///{html_file.replace(chr(92), '/')}")
        page.wait_for_timeout(1000)

        # Generate exact 1-page A4 PDF
        page.pdf(
            path=pdf_file,
            format="A4",
            margin={"top": "8.8mm", "bottom": "8.8mm", "left": "13mm", "right": "13mm"},
            print_background=True
        )

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

    # Render exact PDF page image for visual preview
    pix = doc[0].get_pixmap(dpi=150)
    pix.save(preview_img)
    print(f"Rendered preview image: {preview_img}")

    # ATS STREAM VERIFICATION: Print raw extracted text in sequence
    print("\n=== ATS RAW TEXT EXTRACTION VERIFICATION ===")
    extracted = doc[0].get_text()
    print(extracted[:1200])
    print("=============================================\n")
    
    assert page_count == 1, f"Expected exactly 1 page, but got {page_count} pages!"
    print("SUCCESS: 1-Page Flagship Resume verified with EXACTLY 1 page!")

    # Also copy to docs/Mah_Qing_Tong_Resume.pdf, artifact, and nifty-tesla
    main_doc_pdf = os.path.join(docs_dir, "Mah_Qing_Tong_Resume.pdf")
    artifact_pdf = r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777\Mah_Qing_Tong_Resume_1Page.pdf"
    nifty_pdf = r"C:\Users\User\Documents\antigravity\nifty-tesla\Mah_Qing_Tong_Resume.pdf"
    
    for target in [main_doc_pdf, artifact_pdf, nifty_pdf]:
        try:
            if os.path.exists(target):
                try:
                    with open(target, "ab"):
                        pass
                except PermissionError:
                    os.rename(target, target + ".old")
            import shutil
            shutil.copy2(pdf_file, target)
            print(f"Copied to: {target}")
        except Exception as e:
            print(f"Warning: could not copy to {target}: {e}")

if __name__ == "__main__":
    generate_1page_resume()

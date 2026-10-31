# Autonomous Document Ingestion & Agentic Chunking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an autonomous, verified document ingestion pipeline that converts arbitrary PDFs (e.g., arXiv cs.AI papers or Kaggle documents) to clean Markdown, structurally chunks them with header breadcrumbs, stress-tests retrieval quality using paraphrased probe queries (target $\ge 80\%$), self-corrects if brittle, and commits verified chunks to ChromaDB and `data/catalog.csv`.

**Architecture:** A modular ingestion subsystem (`src/skills/ingestion/`) comprising autonomous metadata extraction, noise-filtered PDF-to-Markdown conversion (`pymupdf4llm`), structural header-preserving chunking, ephemeral staging evaluation with paraphrased probe queries, autonomous self-correction, and catalog/ChromaDB persistence.

**Tech Stack:** Python 3.11+, `pymupdf4llm`, `chromadb`, `duckdb`, `pydantic`, `langchain-core`, `pytest`.

**Spec:** `docs/superpowers/specs/2026-10-31-agentic-ingestion-design.md`

---

## Global Constraints

- **Python Runtime:** Python 3.11+ within existing `.venv`.
- **ChromaDB Schema Compatibility:** Chunks must match existing Chroma metadata fields: `chunk_id`, `document_name`, `header_path`, `chunk_content`.
- **Catalog Synchronization:** New documents must be appended to `data/catalog.csv` with columns: `document_name`, `title`, `author`, `year`, `publisher`, `document_type`, `source_url`.
- **Offline Testability:** All tests must pass offline using `MockChatModel` and local Chroma/DuckDB without requiring paid API keys or active internet.
- **Evaluation Threshold:** Aggregated recall of $\ge 80\%$ across all section probe queries before committing to production.

---

## Review Focus

1. **PDFs with Missing/Irregular Metadata:** When a paper lacks explicit author/year blocks, extractor must generate sensible fallbacks (e.g., `Unknown`, current year, filename slug) without throwing uncaught exceptions.
2. **Table Integrity in Chunks:** Markdown tables (`|---|---|`) must never be sliced across chunk boundaries.
3. **Repeated Header/Footer Noise:** Repeated page headers, footers, and page numbers (`Page X of Y`) must be purged from chunk content.
4. **Self-Correction Boundary Drift:** When self-correcting, chunks must not grow larger than 1,200 words or shrink below 50 words.
5. **Terminal Failure Isolation:** If a document fails evaluation after 3 iterations, it must be quarantined in draft logs without writing corrupt or sub-threshold entries to production ChromaDB.

---

## File Structure

```text
personal-deepagent/
├── pyproject.toml                                # Add pymupdf4llm dependency
├── src/
│   └── skills/
│       └── ingestion/
│           ├── __init__.py                       # Package exports
│           ├── schemas.py                        # Pydantic models for metadata, chunks, eval results
│           ├── extractor.py                      # Metadata extraction from PDF title/first page
│           ├── parser.py                         # PDF to clean Markdown conversion via pymupdf4llm
│           ├── chunker.py                        # Structural Markdown chunker with header breadcrumbs
│           ├── evaluator.py                      # Ephemeral staging index & multi-angle probe evaluation
│           └── pipeline.py                       # Orchestrator with self-correction & persistence
├── scripts/
│   └── ingest_doc.py                             # CLI runner to ingest a local PDF or arXiv URL
└── tests/
    ├── test_ingestion_extractor.py               # Unit tests for metadata extraction
    ├── test_ingestion_parser_chunker.py          # Unit tests for parsing, cleaning, and chunking
    ├── test_ingestion_evaluator.py               # Unit tests for evaluator and probe scoring
    └── test_ingestion_pipeline_e2e.py            # End-to-end integration and quarantine tests
```

---

## Tasks

### Task 1: Environment & Ingestion Schemas

**Files:**
- Modify: `pyproject.toml`
- Create: `src/skills/ingestion/__init__.py`
- Create: `src/skills/ingestion/schemas.py`
- Test: `tests/test_ingestion_schemas.py`

**Interfaces:**
- Produces: `DocumentMetadata`, `IngestionChunk`, `EvaluationProbe`, `EvaluationResult`, `IngestionReport` Pydantic models in `src/skills/ingestion/schemas.py`.

- [ ] **Step 1: Write the failing schema test**

```python
# tests/test_ingestion_schemas.py
from src.skills.ingestion.schemas import DocumentMetadata, IngestionChunk, EvaluationResult

def test_document_metadata_schema():
    meta = DocumentMetadata(
        document_name="ARXIV_2401_001",
        title="Sample AI Research",
        author="John Doe; Jane Smith",
        year=2024,
        document_type="Research Paper",
        source_url="https://arxiv.org/abs/2401.001"
    )
    assert meta.document_name == "ARXIV_2401_001"
    assert meta.year == 2024
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\pytest tests/test_ingestion_schemas.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.skills.ingestion'`

- [ ] **Step 3: Update `pyproject.toml` and implement schemas**

Add `pymupdf4llm>=0.0.17` to dependencies. Create `src/skills/ingestion/schemas.py` defining `DocumentMetadata`, `IngestionChunk`, `EvaluationProbe`, and `EvaluationResult`.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\pytest tests/test_ingestion_schemas.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/skills/ingestion/ tests/test_ingestion_schemas.py
git commit -m "feat(ingestion): add schemas and pymupdf4llm dependency"
```

---

### Task 2: Autonomous Metadata Extractor

**Files:**
- Create: `src/skills/ingestion/extractor.py`
- Test: `tests/test_ingestion_extractor.py`

**Interfaces:**
- Consumes: `DocumentMetadata` from `schemas.py`, `BaseChatModel` from `src.agent`
- Produces: `extract_metadata(text_or_pdf: str, model: Optional[BaseChatModel] = None) -> DocumentMetadata`

- [ ] **Step 1: Write the failing metadata extraction test**

```python
# tests/test_ingestion_extractor.py
from src.skills.ingestion.extractor import extract_metadata
from tests.mock_model import MockChatModel

def test_extract_metadata_from_text():
    sample_text = (
        "arXiv:2403.12345v1 [cs.AI] 18 Mar 2024\n"
        "Agentic Reasoning in Autonomous Networks\n"
        "Alice Smith, Bob Jones\n"
        "Abstract: This paper presents an autonomous agent framework..."
    )
    mock_model = MockChatModel(responses=[
        '{"document_name": "ARXIV_2403_12345", "title": "Agentic Reasoning in Autonomous Networks", "author": "Alice Smith, Bob Jones", "year": 2024, "document_type": "Research Paper", "source_url": "https://arxiv.org/abs/2403.12345"}'
    ])
    meta = extract_metadata(first_page_text=sample_text, model=mock_model)
    assert meta.document_name == "ARXIV_2403_12345"
    assert meta.title == "Agentic Reasoning in Autonomous Networks"
    assert meta.year == 2024
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\pytest tests/test_ingestion_extractor.py -v`
Expected: FAIL with `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Implement `extract_metadata` in `src/skills/ingestion/extractor.py`**

Implement structured JSON parsing with Pydantic fallback if LLM response is unstructured or model is not configured.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\pytest tests/test_ingestion_extractor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/skills/ingestion/extractor.py tests/test_ingestion_extractor.py
git commit -m "feat(ingestion): implement autonomous metadata extractor"
```

---

### Task 3: PDF Parser & Markdown Noise Cleaner

**Files:**
- Create: `src/skills/ingestion/parser.py`
- Test: `tests/test_ingestion_parser.py`

**Interfaces:**
- Produces: `parse_pdf_to_clean_markdown(pdf_path: str) -> str` and `clean_markdown_text(raw_md: str) -> str`

- [ ] **Step 1: Write the failing parser cleaner test**

```python
# tests/test_ingestion_parser.py
from src.skills.ingestion.parser import clean_markdown_text

def test_clean_markdown_removes_page_numbers_and_noise():
    raw_md = (
        "# Introduction\n\n"
        "Page 1 of 12\n\n"
        "This is the opening argument.\n\n"
        "--- 1 ---\n\n"
        "Second paragraph.\n\n"
        "Copyright 2024 INCEIF All rights reserved\n"
    )
    cleaned = clean_markdown_text(raw_md)
    assert "Page 1 of 12" not in cleaned
    assert "--- 1 ---" not in cleaned
    assert "Copyright 2024" not in cleaned
    assert "This is the opening argument." in cleaned
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\pytest tests/test_ingestion_parser.py -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `clean_markdown_text` and `parse_pdf_to_clean_markdown`**

Use `pymupdf4llm.to_markdown(pdf_path)` to extract text, followed by regex filters for running headers, page numbers, and copyright footers.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\pytest tests/test_ingestion_parser.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/skills/ingestion/parser.py tests/test_ingestion_parser.py
git commit -m "feat(ingestion): implement PDF parser and markdown noise cleaner"
```

---

### Task 4: Structural Markdown Chunker with Breadcrumbs

**Files:**
- Create: `src/skills/ingestion/chunker.py`
- Test: `tests/test_ingestion_chunker.py`

**Interfaces:**
- Consumes: `DocumentMetadata`, `IngestionChunk`
- Produces: `chunk_markdown(markdown_text: str, metadata: DocumentMetadata, min_words: int = 50, max_words: int = 800) -> List[IngestionChunk]`

- [ ] **Step 1: Write the failing chunker test**

```python
# tests/test_ingestion_chunker.py
from src.skills.ingestion.chunker import chunk_markdown
from src.skills.ingestion.schemas import DocumentMetadata

def test_chunk_markdown_preserves_headers_and_tables():
    md = (
        "# Overview\n"
        "This paper introduces the architecture.\n\n"
        "## Sukuk Structures\n"
        "| Structure | Shariah Ruling |\n"
        "|---|---|\n"
        "| Asset-backed | Permissible with true sale |\n"
        "| Asset-based | Beneficial ownership only |\n\n"
        "### Governance\n"
        "Macroprudential buffers are required.\n"
    )
    meta = DocumentMetadata(document_name="TEST_01", title="Test Doc")
    chunks = chunk_markdown(md, meta)
    assert len(chunks) >= 2
    # Check breadcrumb presence
    assert any("Overview > Sukuk Structures" in c.header_path for c in chunks)
    # Check table integrity
    table_chunk = next(c for c in chunks if "Asset-backed" in c.chunk_content)
    assert "| Structure | Shariah Ruling |" in table_chunk.chunk_content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\pytest tests/test_ingestion_chunker.py -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `chunk_markdown`**

Parse Markdown header tree (`#`, `##`, `###`), construct hierarchical `header_path`, preserve Markdown table blocks intact, and generate unique IDs (`{document_name}_chunk_{idx:03d}`).

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\pytest tests/test_ingestion_chunker.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/skills/ingestion/chunker.py tests/test_ingestion_chunker.py
git commit -m "feat(ingestion): implement structural markdown chunker"
```

---

### Task 5: Evaluator Agent & Staging Retrieval

**Files:**
- Create: `src/skills/ingestion/evaluator.py`
- Test: `tests/test_ingestion_evaluator.py`

**Interfaces:**
- Consumes: `List[IngestionChunk]`, `BaseChatModel`
- Produces: `evaluate_chunks(chunks: List[IngestionChunk], model: Optional[BaseChatModel] = None, threshold: float = 0.8) -> EvaluationResult`

- [ ] **Step 1: Write the failing evaluator test**

```python
# tests/test_ingestion_evaluator.py
from src.skills.ingestion.evaluator import evaluate_chunks
from src.skills.ingestion.schemas import IngestionChunk
from tests.mock_model import MockChatModel

def test_evaluate_chunks_passing_rate():
    chunks = [
        IngestionChunk(
            chunk_id="c1",
            document_name="DOC1",
            header_path="/INTRODUCTION",
            chunk_content="This paper proposes an agentic framework for AI alignment and safety mechanisms."
        ),
        IngestionChunk(
            chunk_id="c2",
            document_name="DOC1",
            header_path="Architecture > Safety Buffer",
            chunk_content="The safety buffer mitigates catastrophic risks by monitoring reward decoupling."
        )
    ]
    # Mock probe questions generated by evaluator
    mock_model = MockChatModel(responses=[
        '["What framework does the paper propose?", "How does the agentic model address AI alignment?", "What are the core safety mechanisms?"]',
        '["How does the safety buffer operate?", "What mitigates reward decoupling?", "Explain the catastrophic risk framework."]'
    ])
    result = evaluate_chunks(chunks, model=mock_model, threshold=0.8)
    assert result.recall_score >= 0.8
    assert result.passed is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\pytest tests/test_ingestion_evaluator.py -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `evaluate_chunks` in `src/skills/ingestion/evaluator.py`**

Create temporary in-memory Chroma collection `staging_eval_{doc_id}`, index candidate chunks, generate 3 probe questions per section, query staging collection, and calculate match rate against target `header_path`.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\pytest tests/test_ingestion_evaluator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/skills/ingestion/evaluator.py tests/test_ingestion_evaluator.py
git commit -m "feat(ingestion): implement evaluator agent and staging retrieval"
```

---

### Task 6: Ingestion Orchestration Pipeline & Self-Correction

**Files:**
- Create: `src/skills/ingestion/pipeline.py`
- Test: `tests/test_ingestion_pipeline_e2e.py`

**Interfaces:**
- Consumes: `extractor.py`, `parser.py`, `chunker.py`, `evaluator.py`
- Produces: `ingest_pdf_document(pdf_path: str, model: Optional[BaseChatModel] = None, max_iterations: int = 3) -> IngestionReport`

- [ ] **Step 1: Write the failing end-to-end pipeline test**

```python
# tests/test_ingestion_pipeline_e2e.py
from src.skills.ingestion.pipeline import ingest_pdf_document
from tests.mock_model import MockChatModel
import tempfile, os

def test_pipeline_quarantine_on_terminal_failure(monkeypatch):
    # Test that persistent failures do not write to production Chroma or catalog.csv
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\pytest tests/test_ingestion_pipeline_e2e.py -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `ingest_pdf_document` with self-correction loop**

If evaluation recall is $< 80\%$, merge failing short chunks or split long chunks and re-evaluate (up to 3 iterations). On pass: upsert to production Chroma `document_knowledge` and append to `data/catalog.csv`. On terminal fail: record in `quarantine_log.json`.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\pytest tests/test_ingestion_pipeline_e2e.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/skills/ingestion/pipeline.py tests/test_ingestion_pipeline_e2e.py
git commit -m "feat(ingestion): implement ingestion pipeline with self-correction and quarantine"
```

---

### Task 7: CLI Runner & arXiv cs.AI Ingestion Test

**Files:**
- Create: `scripts/ingest_doc.py`
- Modify: `src/skills/__init__.py`
- Test: Test runner command on a sample PDF / arXiv link

**Interfaces:**
- Produces: CLI command `python scripts/ingest_doc.py <pdf_path_or_arxiv_url>`

- [ ] **Step 1: Create `scripts/ingest_doc.py`**

Support local PDF paths as well as direct arXiv abstract / PDF URLs (e.g., `https://arxiv.org/abs/...` or `https://arxiv.org/pdf/...`).

- [ ] **Step 2: Run end-to-end regression suite**

Run: `.venv\Scripts\python scripts/run_all_tests.py`
Expected: 100% PASS across Tier L1, Tier L2, and Tier L3.

- [ ] **Step 3: Commit**

```bash
git add scripts/ingest_doc.py
git commit -m "feat(ingestion): add CLI runner supporting arXiv URLs and local PDFs"
```


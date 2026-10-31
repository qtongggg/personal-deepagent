# FastAPI Knowledge Base & Chunk Viewer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade FastAPI application and interactive web viewer allowing users to easily browse, search, and observe document chunks and trigger paper ingestion.

**Architecture:** A FastAPI backend (`src/api.py`) exposing clean REST endpoints (`/api/documents`, `/api/documents/{id}/chunks`, `/api/search`, `/api/ingest`, `/health`) alongside an integrated, responsive single-page Web UI (`src/templates/viewer.html`) styled with modern CSS and Markdown rendering. A dedicated launcher script (`scripts/run_server.py`) enables one-command startup.

**Tech Stack:** FastAPI, Uvicorn, ChromaDB, DuckDB/Pandas, PyTest (`fastapi.testclient.TestClient`), Vanilla JS + Tailwind CSS + Marked.js CDN.

**Spec:** Documented in chat playback: clean visual interface to inspect chunks by document with section breadcrumbs, word counts, Markdown table rendering, instant filtering, and semantic search.

## Global Constraints

- Must run locally with Python 3.13 without requiring Node.js or npm build steps.
- Production ChromaDB (`.chroma/`) must remain clean; test suite must use `tmp_path` isolation via `tests/conftest.py`.
- All tests must pass with 100% success rate across `pytest`.
- Endpoints must handle non-existent documents and missing parameters gracefully with standard HTTP status codes.

## Review Focus

1. **Non-existent document query:** `GET /api/documents/NON_EXISTENT/chunks` must return 404 with helpful error message rather than crashing.
2. **Missing ChromaDB collection:** App must gracefully initialize empty collection without throwing 500.
3. **Empty query in semantic search:** `GET /api/search?q=` must return 422 or empty results rather than throwing an exception.
4. **HTML Viewer rendering:** `GET /` must return `text/html; charset=utf-8` and load properly with zero CORS issues.
5. **Special characters in section names:** Chunks containing `<br>`, math symbols, or quotes must render safely without XSS or broken layout.

---

### Task 1: FastAPI Core Endpoints & Pydantic Schemas

**Files:**
- Create: `src/api.py`
- Test: `tests/test_api.py`

**Interfaces:**
- Consumes: `get_chroma_client` from `scripts.ingest`, `query_catalog_sql` from `src.skills.catalog_skill`, `retrieve_knowledge_chunks` from `src.skills.retriever_skill`
- Produces: FastAPI `app` object with `/health`, `/api/documents`, `/api/documents/{doc_name}/chunks`, `/api/search`

- [ ] **Step 1: Write failing API unit tests in `tests/test_api.py`**
- [ ] **Step 2: Run pytest to confirm tests fail**
- [ ] **Step 3: Implement `src/api.py` with FastAPI endpoints**
- [ ] **Step 4: Run pytest to confirm all API tests pass**
- [ ] **Step 5: Commit task changes**

---

### Task 2: Interactive Single-Page Chunk Viewer UI

**Files:**
- Create: `src/templates/viewer.html`
- Modify: `src/api.py` (mount `/` route serving `viewer.html` via `HTMLResponse`)
- Test: `tests/test_api.py`

**Interfaces:**
- Consumes: `/api/documents` and `/api/documents/{doc_name}/chunks`
- Produces: Single-page modern HTML interface with sidebar document switch, section jumping, chunk cards, and search

- [ ] **Step 1: Write test verifying `GET /` returns 200 with HTML content**
- [ ] **Step 2: Implement `src/templates/viewer.html` with responsive layout, Tailwind CDN, and marked.js**
- [ ] **Step 3: Serve `viewer.html` at `GET /` in `src/api.py`**
- [ ] **Step 4: Run pytest to verify endpoint returns the HTML page**
- [ ] **Step 5: Commit task changes**

---

### Task 3: Ingestion API Endpoint & Server Launcher CLI

**Files:**
- Create: `scripts/run_server.py`
- Modify: `src/api.py` (add `POST /api/ingest` endpoint)
- Test: `tests/test_api.py`

**Interfaces:**
- Consumes: `ingest_pdf_document` and `download_url_to_temp_file` from `src.skills.ingestion.pipeline`
- Produces: Background ingestion trigger and `python scripts/run_server.py` entrypoint

- [ ] **Step 1: Add unit test for `POST /api/ingest`**
- [ ] **Step 2: Implement `POST /api/ingest` in `src/api.py`**
- [ ] **Step 3: Create `scripts/run_server.py` with CLI argument parsing (host, port)**
- [ ] **Step 4: Run full regression test suite**
- [ ] **Step 5: Commit task changes**


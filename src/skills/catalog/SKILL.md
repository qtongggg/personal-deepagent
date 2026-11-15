---
name: catalog_skill
description: Deterministic SQL inventory and metadata verification engine over data/catalog.csv using in-process DuckDB.
triggers:
  - "How many papers..."
  - "Count publications..."
  - "List papers by author..."
  - "Verify publication metadata..."
tools:
  - catalog_query
---

# 📚 Catalog Skill Specification

## 1. Overview
The **Catalog Skill** provides deterministic, zero-hallucination querying over the master academic metadata dataset (`data/catalog.csv`) containing 871+ verified research publications. It executes in-process SQL queries via DuckDB.

## 2. When to Use
- **Deterministic Counts & Aggregations**: Whenever the user asks for exact statistics, counts, or tallies across publication years, authors, or categories.
- **Publication Metadata Grounding**: During multi-hop research, verify the exact canonical title, author list, publication year, and verbatim `source_url`.
- **Filtering & Listings**: Querying papers matching specific criteria without touching the vector database.

## 3. Database Schema (`catalog`)
The table `catalog` is registered directly from `data/catalog.csv`:

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | VARCHAR | Canonical short title or internal document identifier |
| `title` | VARCHAR | Full formal paper title |
| `author` | VARCHAR | Author list or primary research group |
| `year` | INTEGER | Year of publication (e.g. 2020, 2023, 2024) |
| `doc_type` | VARCHAR | Publication type (e.g. `journal`, `conference`, `arxiv`) |
| `source_url` | VARCHAR | Ground-truth verbatim URL (e.g. `https://arxiv.org/abs/...`) |

## 4. Invariant Operational Protocols
1. **Case-Insensitive Substring Matching**: Always search both `title` and `name` using `LOWER(...) LIKE '%keyword%'`.
   ```sql
   SELECT name, title, author, year, source_url 
   FROM catalog 
   WHERE LOWER(title) LIKE '%toolformer%' OR LOWER(name) LIKE '%toolformer%';
   ```
2. **Pure Count Queries**: When answering pure counts (e.g., "How many papers on Waqf in 2020?"), call `catalog_query` ONLY.
   - ⚡ **LATENCY GUARD**: Never call `knowledge_retriever` for count inquiries.
   - Return the direct number. If 0, state 0 explicitly without fabricating titles.
3. **Verbatim URLs**: Every citation in the final response must include the verbatim `source_url` obtained from this catalog.

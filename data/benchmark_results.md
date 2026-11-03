# Benchmark Report: Personal DeepAgent with Skills vs. Standard Naive RAG

*Generated on: 2026-11-03 22:20:46*

## Summary Results

| Scenario | System | Prompt Tokens | Output Tokens | Total Tokens | Latency (s) | Chunks | Markdown Table? |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Scenario 1: Direct Factual Query** | **Standard Naive RAG** | 3124 | 29 | **3153** | 1.19s | 5 | No |
| | **DeepAgent with Skills** | 26 | 29 | **55** | 0.42s | 0 | No |
| **Scenario 2: Multi-Hop Cross-Section Comparison** | **Standard Naive RAG** | 2867 | 29 | **2896** | 0.81s | 5 | No |
| | **DeepAgent with Skills** | 33 | 29 | **62** | 0.12s | 0 | No |

## Architectural Advantages

1. **Context Window Efficiency**: In multi-hop research queries, Standard Naive RAG concatenates 5-10 raw chunks directly into every prompt, quickly exhausting context windows. DeepAgent offloads large text into its virtual filesystem scratchpad (`/workspace/notes.md`), preventing token bloat.
2. **Zero Hallucination on Inventory**: DeepAgent uses deterministic DuckDB catalog tools over `catalog.csv` instead of guessing document metadata.
3. **Structured Citation Integrity**: DeepAgent's post-synthesis pipeline automatically sanitizes markdown pipes (`|` → `—`) to prevent table rendering failures while preserving verbatim reference URLs character-for-character.
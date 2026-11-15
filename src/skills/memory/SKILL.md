---
name: memory_skill
description: Long-term personalized memory persistence and semantic recall using Mem0 MemoryClient.
triggers:
  - User self-introductions ("My name is...", "I am a PhD student...")
  - Topic preferences ("I focus on RLHF and agent architectures...")
  - Research recall ("What was my previous research focus?")
tools:
  - search_memory
  - add_memory
---

# 🧠 Memory Skill Specification

## 1. Overview
The **Memory Skill** provides long-term cross-session memory for DeepAgent. Powered by Mem0, it enables autonomous user profile recognition, research topic tracking, and personalization without requiring explicit confirmation prompts.

## 2. Tools & Capabilities
- **`search_memory(query: str, user_id: str = "default_user")`**:
  - Searches past conversational memory for relevant preferences, project history, or user identity attributes.
  - Relevance threshold: Similarity $\ge 0.40$.
- **`add_memory(messages: List[Dict[str, str]], user_id: str = "default_user")`**:
  - Extracts and persists key facts (e.g. user identity, educational background, research focus) into the user's permanent memory store.

## 3. Autonomous Invariant Protocols
1. **Silent Identity Persistence**:
   - When a user introduces themselves (e.g., *"Hi, I'm QT, an AI & LLM engineer working on multi-hop agents"*), immediately commit their name, role, and focus to Mem0 via `add_memory`.
   - ⚡ **Rule**: Never ask permission like *"Would you like me to remember this?"* — commit silently and proceed naturally.
2. **Phase 3.5 Topic Persistence**:
   - When completing an in-depth 2-hop comparison, commit the investigated topic to memory so subsequent sessions can reference prior learnings.
3. **Pure Count Bypass**:
   - Never call `search_memory` or `add_memory` for pure statistical SQL queries (e.g. "How many papers in 2020?").

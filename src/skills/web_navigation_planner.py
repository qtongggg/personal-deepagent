# src/skills/web_navigation_planner.py
"""
Smart Web Navigation Planner Skill (Autonomous Perception & Action Agent)
Completely independent from the Resume RAG pipeline.
Takes visible interactive elements on any webpage and a user's natural language goal,
uses the configured LLM (DeepSeek / Gemini / OpenAI) to reason about the page semantics,
and produces a structured sequence of pointer actions (move, click, type, scroll) with live thoughts.
"""

import json
import re
from typing import Any, Dict, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from src.utils.models import get_default_model

PLANNER_SYSTEM_PROMPT = """You are WebPointerAgent, an autonomous AI that controls an interactive screen pointer to accomplish a user's goal on any webpage.

You will be given:
1. The user's goal (e.g. "Search for lofi beats and play the first video", "Click the pricing button", "Star this repo").
2. The current webpage URL.
3. A list of visible interactive elements on the page (inputs, buttons, links, cards), each with an `id`, `tag`, `text`, `role`, and screen coordinates.

YOUR TASK:
Analyze the elements and decide what the pointer should do next.
Output STRICTLY valid JSON with:
- "thought": A clear, concise sentence explaining what you see and what you decided to do (e.g. "I see the search input #2 at (420, 30). I will move there and type the query.").
- "actions": A list of 1 to 3 atomic actions to perform in order:
  - {"type": "move_and_click", "target_id": <int>, "thought": "..."}
  - {"type": "move_and_type", "target_id": <int>, "text": "...", "thought": "..."}
  - {"type": "press_enter", "thought": "..."}
  - {"type": "scroll", "direction": "down" | "up", "amount": 400, "thought": "..."}
  - {"type": "done", "message": "...", "thought": "..."}

GUIDELINES:
1. Pick the single most relevant element matching the user's intent.
2. CRITICAL FOR VIDEO/MUSIC: If the user wants to play/listen to a video or song, and video results or watch links (role="video" or tag="a" with video title) are ALREADY visible on the page, DO NOT pick the search input! Directly target the top video link (action: move_and_click) to play it immediately.
3. Only target the search input if no video results are present on the page yet.
4. Keep the "thought" short (under 20 words) so it fits in a floating thought bubble.
5. Return ONLY the JSON object, no markdown fences or extra text.
"""

def plan_web_actions(goal: str, url: str, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generates an action plan for the pointer based on perceived elements and natural language goal."""
    if not goal:
        return {"thought": "No goal specified.", "actions": [{"type": "done", "message": "Waiting for command."}]}

    # Compact the elements list (limit to 35 most relevant visible elements to keep latency low)
    compact_elements = []
    for el in elements[:35]:
        item = {
            "id": el.get("id"),
            "tag": el.get("tag"),
            "role": el.get("role", ""),
            "text": (el.get("text") or "").strip()[:60],
            "placeholder": el.get("placeholder", ""),
            "x": round(el.get("x", 0)),
            "y": round(el.get("y", 0)),
        }
        compact_elements.append(item)

    user_prompt = f"""URL: {url}
USER GOAL: {goal}

VISIBLE INTERACTIVE ELEMENTS:
{json.dumps(compact_elements, indent=1)}

Decide the best pointer actions to achieve the goal."""

    try:
        model = get_default_model()
        response = model.invoke([
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ])

        raw_content = response.content if hasattr(response, "content") else str(response)
        # Strip potential markdown code blocks
        clean_json = re.sub(r"^```(?:json)?\s*", "", raw_content.strip())
        clean_json = re.sub(r"\s*```$", "", clean_json.strip())

        parsed = json.loads(clean_json)
        return parsed

    except Exception as exc:
        print(f"[WebPlanner] LLM parsing failed ({exc}), using heuristic fallback...")
        return _heuristic_fallback_plan(goal, elements)


def _heuristic_fallback_plan(goal: str, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Heuristic semantic fallback in case of LLM network failure."""
    goal_lower = goal.lower()

    # Search heuristic
    if "search" in goal_lower or "play" in goal_lower:
        # Check if video results already present
        for el in elements:
            txt = (el.get("text") or "").lower()
            if any(k in txt for k in ["lofi", "beats", "radio", "music", "mix"]):
                return {
                    "thought": f"Found video matching '{el.get('text', '')[:30]}'. Clicking to play.",
                    "actions": [
                        {"type": "move_and_click", "target_id": el.get("id"), "thought": "Clicking video card"}
                    ]
                }

        # Otherwise find search input
        for el in elements:
            if el.get("tag") == "input" or el.get("role") in ["searchbox", "search"]:
                query = goal.replace("search for", "").replace("play", "").replace("open youtube and", "").strip()
                return {
                    "thought": "Found search input. Moving to type query.",
                    "actions": [
                        {"type": "move_and_type", "target_id": el.get("id"), "text": query or "lofi beats", "thought": "Typing query into search input"},
                        {"type": "press_enter", "thought": "Submitting search"}
                    ]
                }

    return {
        "thought": "Examining page elements to determine best action.",
        "actions": [{"type": "done", "message": f"Explored page for '{goal}'"}]
    }

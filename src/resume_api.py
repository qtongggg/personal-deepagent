# src/resume_api.py
"""
Mah Qing Tong (QT) — Unified Portfolio & Resume DeepAgent Server
Serves the nifty-tesla kinetic frontend and powers real-time SSE chat using
the custom Resume DeepAgent backed by ChromaDB and FlashRank.

Run with:
    uv run python src/resume_api.py
"""

import asyncio
import json
import os
from pathlib import Path
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import uvicorn

from src.resume_agent import create_resume_agent
from src.skills.cross_tab_agent import launch_cross_tab_youtube

app = FastAPI(title="QT Resume DeepAgent API")

# Enable CORS for cross-origin or local dev requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend static directory (Unified Monorepo with fallback)
FRONTEND_DIR = (Path(__file__).resolve().parent.parent / "frontend").resolve()
FALLBACK_DIR = Path(r"C:\Users\User\Documents\antigravity\nifty-tesla").resolve()
STATIC_DIR = FRONTEND_DIR if FRONTEND_DIR.exists() else FALLBACK_DIR

# Shared agent instance
_AGENT = None


def get_agent():
    global _AGENT
    if _AGENT is None:
        _AGENT = create_resume_agent()
    return _AGENT


class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = ""
    user: Optional[str] = "portfolio-visitor"


async def stream_agent_events(query: str, conversation_id: str = "") -> AsyncGenerator[str, None]:
    """Runs the Resume DeepAgent and streams token events via SSE matching the portfolio contract."""
    agent = get_agent()
    conv_id = conversation_id or "resume-session"

    # Initial meta packet to activate terminal status
    yield f"data: {json.dumps({'type': 'meta', 'mode': 'deepagent', 'section': 'ChromaDB Hybrid Search'})}\n\n"

    try:
        # astream_events v2 emits granular lifecycle events as they happen
        async for event in agent.astream_events(
            {"messages": [HumanMessage(content=query)]},
            version="v2",
        ):
            kind = event.get("event")

            # Streaming token chunks from the language model
            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and chunk.content:
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.content, 'conversation_id': conv_id})}\n\n"

        # Signal completion
        yield f"data: {json.dumps({'type': 'done', 'conversation_id': conv_id})}\n\n"

    except Exception as exc:
        yield f"data: {json.dumps({'type': 'error', 'content': f'Agent error: {str(exc)}'})}\n\n"


@app.get("/api/status")
async def api_status():
    """Health check endpoint consumed by script.js to render the status pill."""
    return JSONResponse({
        "status": "online",
        "mode": "deepagent",
        "agent": "Resume DeepAgent",
        "knowledge_chunks": 14,
        "database": "personal_resume_knowledge",
    })


@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    """Streaming chat endpoint consumed by script.js when user submits a query."""
    clean_q = req.query.strip()
    if not clean_q:
        return JSONResponse({"error": "Empty query"}, status_code=400)

    return StreamingResponse(
        stream_agent_events(clean_q, req.conversation_id or "resume-session"),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


class CrossTabYouTubeRequest(BaseModel):
    song: Optional[str] = "lofi hip hop radio beats to relax study to"


@app.post("/api/browser/cross-tab-youtube")
async def api_cross_tab_youtube(req: CrossTabYouTubeRequest):
    """Launches visible real Google Chrome with the companion pointer to play music."""
    song = (req.song or "lofi hip hop radio beats to relax study to").strip()
    asyncio.create_task(launch_cross_tab_youtube(song))
    return JSONResponse({"status": "launched", "song": song})


# =====================================================================
# Serve Frontend Static Files (Unified Monorepo)
# =====================================================================

@app.get("/")
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    return FileResponse(
        index_file,
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )


@app.get("/{file_path:path}")
async def serve_static(file_path: str):
    target = (STATIC_DIR / file_path).resolve()
    if target.is_file() and str(target).startswith(str(STATIC_DIR)) and not target.name.startswith(".env"):
        return FileResponse(
            target,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
    return FileResponse(
        STATIC_DIR / "index.html",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print("\n" + "=" * 65)
    print(">> QT Portfolio & Resume DeepAgent Server Running!")
    print(f">> Local URL: http://localhost:{port}")
    print(f">> Serving UI From: {STATIC_DIR}")
    print(">> Engine: Resume DeepAgent (ChromaDB + BM25 + FlashRank)")
    print("=" * 65 + "\n")
    uvicorn.run(
        "src.resume_api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=[str(Path(__file__).parent), str(STATIC_DIR)],
    )
    
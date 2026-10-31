import argparse
import os
import sys
import uvicorn

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    parser = argparse.ArgumentParser(description="Run the Personal DeepAgent FastAPI Knowledge Base & Chunk Studio server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on file changes")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  PERSONAL DEEPAGENT — KNOWLEDGE BASE & CHUNK STUDIO")
    print("=" * 60)
    print(f"  * Web Viewer UI   : http://{args.host}:{args.port}")
    print(f"  * OpenAPI Docs    : http://{args.host}:{args.port}/docs")
    print(f"  * Health Check    : http://{args.host}:{args.port}/health")
    print("=" * 60 + "\n")

    uvicorn.run("src.api:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()


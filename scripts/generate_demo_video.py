import glob
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PORT = 8765
BASE_URL = f"http://127.0.0.1:{PORT}"
VIDEO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "videos")


def wait_for_server(url: str, timeout: float = 12.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(f"{url}/health", timeout=1.0) as res:
                if res.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def main():
    print("=" * 70)
    print("[VIDEO GENERATOR] PERSONAL DEEPAGENT: AUTOMATED VIDEO GENERATION VIA CODE")
    print("=" * 70)

    os.makedirs(VIDEO_DIR, exist_ok=True)
    temp_rec_dir = os.path.join(VIDEO_DIR, "temp_rec")
    os.makedirs(temp_rec_dir, exist_ok=True)

    # 1. Start local FastAPI server in background
    print(f">> Starting background API server on port {PORT}...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api:app", "--port", str(PORT), "--log-level", "warning"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        if not wait_for_server(BASE_URL):
            print("[ERROR] Server failed to respond within timeout.")
            return

        print("[OK] Server is live!")

        # 2. Launch Playwright with video recording
        print(">> Launching Chromium and starting high-definition screen recording (1280x720)...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                record_video_dir=temp_rec_dir,
                record_video_size={"width": 1280, "height": 720},
                viewport={"width": 1280, "height": 720},
            )
            page = context.new_page()

            # 3. Open Web Arena
            print(f">> Navigating to {BASE_URL}...")
            page.goto(BASE_URL, wait_until="networkidle")
            page.wait_for_timeout(1000)

            # 4. Simulate human typing of the comparison query
            prompt = "Compare how ReAct and Reflexion handle agent reasoning and feedback loops, including their primary benchmark results."
            print(f">> Simulating typing prompt: \"{prompt[:45]}...\"")
            query_input = page.locator("#arena-query-input")
            query_input.fill("")
            query_input.type(prompt, delay=22)

            page.wait_for_timeout(800)

            # 5. Click Run Head-to-Head Arena
            print(">> Clicking 'Run Head-to-Head Arena' button...")
            run_btn = page.locator("#arena-run-btn")
            run_btn.click()

            # 6. Wait for DeepAgent matrix table and results to render
            print(">> Waiting for side-by-side comparison results to render...")
            page.wait_for_selector("#deepagent-output-box table", timeout=15000)
            page.wait_for_timeout(2000)

            # 7. Smoothly scroll down the DeepAgent result to showcase the 11-dimension matrix
            print(">> Showcasing the 11-dimension comparative matrix...")
            deep_box = page.locator("#deepagent-output-box")
            for _ in range(5):
                deep_box.evaluate("(el) => el.scrollBy({ top: 120, behavior: 'smooth' })")
                page.wait_for_timeout(600)

            page.wait_for_timeout(2000)

            # 8. Close context to finalize video writing
            print(">> Closing recording context...")
            page.close()
            context.close()
            browser.close()

        # 9. Move generated video to final destination
        recorded_videos = glob.glob(os.path.join(temp_rec_dir, "*.webm"))
        if recorded_videos:
            latest_video = max(recorded_videos, key=os.path.getctime)
            final_path = os.path.join(VIDEO_DIR, "demo_arena_showcase.webm")
            shutil.copy2(latest_video, final_path)
            shutil.rmtree(temp_rec_dir, ignore_errors=True)
            print("=" * 70)
            print("[SUCCESS] VIDEO SUCCESSFULLY GENERATED THROUGH CODE!")
            print(f"File Location: {final_path}")
            print(f"File Size: {os.path.getsize(final_path) / 1024:.1f} KB")
            print("=" * 70)
        else:
            print("[WARN] No video file detected in recording directory.")

    finally:
        print(">> Shutting down local server...")
        server_process.terminate()
        server_process.wait()
        print("[OK] Server shut down cleanly.")


if __name__ == "__main__":
    main()

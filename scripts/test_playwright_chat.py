# scripts/test_playwright_chat.py
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACT_DIR = Path(r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

ARROW_OVERLAY_JS = """
(() => {
  if (document.getElementById('playwright-pointer-arrow')) return;

  const arrow = document.createElement('div');
  arrow.id = 'playwright-pointer-arrow';
  arrow.innerHTML = `
    <div style="position: relative;">
      <svg width="44" height="44" viewBox="0 0 24 24" fill="none" style="filter: drop-shadow(0 3px 10px rgba(0,0,0,0.85));">
        <path d="M4 4L11 20L14 13L21 10L4 4Z" fill="#ff5c00" stroke="#ffffff" stroke-width="2.2" stroke-linejoin="round"/>
      </svg>
      <div id="pointer-click-ripple" style="
        position: absolute;
        top: 2px; left: 2px;
        width: 32px; height: 32px;
        border-radius: 50%;
        background: rgba(255, 92, 0, 0.7);
        border: 2px solid #ffffff;
        transform: scale(0);
        pointer-events: none;
        transition: transform 0.4s ease-out, opacity 0.4s ease-out;
        opacity: 0;
      "></div>
    </div>
  `;
  arrow.style.position = 'fixed';
  arrow.style.zIndex = '999999';
  arrow.style.pointerEvents = 'none';
  arrow.style.left = '100px';
  arrow.style.top = '100px';
  arrow.style.transition = 'left 0.5s cubic-bezier(0.2, 0.8, 0.2, 1), top 0.5s cubic-bezier(0.2, 0.8, 0.2, 1)';
  document.body.appendChild(arrow);

  window.moveArrowTo = (x, y) => {
    arrow.style.left = `${x}px`;
    arrow.style.top = `${y}px`;
  };

  window.pingArrowClick = () => {
    const ripple = document.getElementById('pointer-click-ripple');
    if (!ripple) return;
    ripple.style.transition = 'none';
    ripple.style.transform = 'scale(0)';
    ripple.style.opacity = '1';
    requestAnimationFrame(() => {
      ripple.style.transition = 'transform 0.45s ease-out, opacity 0.45s ease-out';
      ripple.style.transform = 'scale(2.2)';
      ripple.style.opacity = '0';
    });
  };
})();
"""

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 840},
            device_scale_factor=1.5,
            record_video_dir=str(ARTIFACT_DIR / "videos")
        )
        page = await context.new_page()

        print("Navigating to http://localhost:8000 ...")
        await page.goto("http://localhost:8000", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Inject visual cursor arrow
        await page.evaluate(ARROW_OVERLAY_JS)

        # 1. Move Arrow to Input Field
        input_box = page.locator("#cli-input")
        box = await input_box.bounding_box()
        if box:
            target_x = box["x"] + 25
            target_y = box["y"] + box["height"] / 2
            await page.evaluate(f"window.moveArrowTo({target_x}, {target_y})")
            await page.wait_for_timeout(700)
            await page.evaluate("window.pingArrowClick()")

        # Click input and capture Screenshot 1 (Arrow at input)
        await input_box.click()
        shot1 = ARTIFACT_DIR / "playwright_step1_cursor_at_input.png"
        await page.screenshot(path=str(shot1))
        print(f"Step 1 screenshot saved to: {shot1}")

        # Type query
        test_query = "What are QT's skills and flagship projects?"
        await input_box.fill(test_query)
        await page.wait_for_timeout(600)

        # 2. Move Arrow to Submit Button
        submit_btn = page.locator("#cli-submit-btn")
        btn_box = await submit_btn.bounding_box()
        if btn_box:
            btn_x = btn_box["x"] + btn_box["width"] / 2
            btn_y = btn_box["y"] + btn_box["height"] / 2
            await page.evaluate(f"window.moveArrowTo({btn_x}, {btn_y})")
            await page.wait_for_timeout(700)
            await page.evaluate("window.pingArrowClick()")

        # Capture Screenshot 2 (Arrow clicking submit button)
        shot2 = ARTIFACT_DIR / "playwright_step2_typed_and_click.png"
        await page.screenshot(path=str(shot2))
        print(f"Step 2 screenshot saved to: {shot2}")

        # Submit query
        print(f"Submitting query: {test_query} ...")
        await submit_btn.click()

        # 3. Wait for response to stream in
        print("Waiting for response stream...")
        await page.wait_for_selector(".cli-agent-entry .agent-stream-text", timeout=20000)

        # Wait for full response text to accumulate
        for _ in range(40):
            await page.wait_for_timeout(500)
            text = await page.locator(".cli-agent-entry .agent-stream-text").last.inner_text()
            if len(text.strip()) > 150:
                print(f"Stream progress: {len(text)} characters received.")
                break

        await page.wait_for_timeout(3500)

        # Move arrow over the streamed response
        response_box = await page.locator(".cli-agent-entry").last.bounding_box()
        if response_box:
            await page.evaluate(f"window.moveArrowTo({response_box['x'] + 40}, {response_box['y'] + 40})")
            await page.wait_for_timeout(600)

        # Capture Screenshot 3 (Streamed output in UI)
        shot3 = ARTIFACT_DIR / "playwright_step3_agent_streaming.png"
        await page.screenshot(path=str(shot3))
        print(f"Step 3 screenshot saved to: {shot3}")

        final_text = await page.locator(".cli-agent-entry .agent-stream-text").last.inner_text()
        print("\n=== AGENT RESPONSE IN UI ===")
        print(final_text)
        print("============================\n")

        await context.close()
        await browser.close()
        print("Playwright test complete!")

if __name__ == "__main__":
    asyncio.run(run())

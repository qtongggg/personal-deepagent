import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACTS_DIR = Path(r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777")
FRONTEND_FILE = Path(r"c:\Users\User\Documents\antigravity\personal-deepagent\frontend\index.html").resolve()

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("[Test] Loading portfolio...")
        await page.goto(FRONTEND_FILE.as_uri(), wait_until="domcontentloaded")
        await page.wait_for_timeout(1000)

        print("[Test] Pressing Ctrl+Shift+K to open HUD...")
        await page.keyboard.press("Control+Shift+K")
        await page.wait_for_timeout(400)

        # Check HUD active
        is_open = await page.evaluate("() => document.getElementById('agent-command-overlay').classList.contains('is-active')")
        print(f"[Test] HUD Active: {is_open}")

        # Set up popup / new page listener
        popup_detected = []
        context.on("page", lambda p: popup_detected.append(p))

        # We also mock window.open to track target url reliably in headless
        await page.evaluate("""() => {
            window.__openedUrls = [];
            const orig = window.open;
            window.open = function(url, target, features) {
                window.__openedUrls.push(url);
                return orig ? orig.call(window, url, target, features) : null;
            };
        }""")

        print("[Test] Submitting command: 'open youtube and play a song for me' ...")
        cmd_input = page.locator("#agent-command-input")
        await cmd_input.fill("open youtube and play a song for me")
        await cmd_input.press("Enter")
        await page.wait_for_timeout(600)

        state_text = await page.locator("#agent-pointer-state").inner_text()
        bubble_title = await page.locator("#agent-bubble-title").inner_text()
        bubble_text = await page.locator("#agent-bubble-text").inner_text()
        opened_urls = await page.evaluate("() => window.__openedUrls")

        print(f"[Test] State text: {state_text.encode('ascii', 'replace').decode('ascii')}")
        print(f"[Test] Bubble Title: {bubble_title.encode('ascii', 'replace').decode('ascii')}")
        print(f"[Test] Bubble Text: {bubble_text.encode('ascii', 'replace').decode('ascii')}")
        print(f"[Test] Opened URLs: {opened_urls}")

        screenshot_path = ARTIFACTS_DIR / "youtube_command_verified.png"
        await page.screenshot(path=str(screenshot_path))
        print(f"[Test] Screenshot saved to: {screenshot_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACTS_DIR = Path(r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("[Test] Loading http://localhost:8000 ...")
        await page.goto("http://localhost:8000", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 1. Open HUD with Ctrl+Shift+K
        print("[Test] Opening Command HUD (Ctrl+Shift+K)...")
        await page.keyboard.press("Control+Shift+K")
        await page.wait_for_timeout(400)

        hud_active = await page.evaluate("() => document.getElementById('agent-command-overlay').classList.contains('is-active')")
        print(f"[Test] HUD Active: {hud_active}")

        # 2. Type command: 'open youtube and play a song for me'
        print("[Test] Typing: 'open youtube and play a song for me' ...")
        cmd_input = page.locator("#agent-command-input")
        await cmd_input.fill("open youtube and play a song for me")
        await cmd_input.press("Enter")

        # Capture Phase 1: Pointer gliding to YouTube Tab
        await page.wait_for_timeout(600)
        state_1 = await page.locator("#agent-pointer-state").inner_text()
        print(f"[Test Phase 1] Pointer State: {state_1.encode('ascii', 'replace').decode('ascii')}")
        await page.screenshot(path=str(ARTIFACTS_DIR / "yt_tab_step1_gliding_to_tab.png"))

        # Capture Phase 2: Window opened & Auto-typing into search input
        await page.wait_for_timeout(1500)
        state_2 = await page.locator("#agent-pointer-state").inner_text()
        input_val_2 = await page.locator("#yt-browser-input").input_value()
        print(f"[Test Phase 2] Pointer State: {state_2.encode('ascii', 'replace').decode('ascii')}")
        print(f"[Test Phase 2] YouTube Search Input Value: {input_val_2}")
        await page.screenshot(path=str(ARTIFACTS_DIR / "yt_tab_step2_typing_song.png"))

        # Capture Phase 3: Clicked PLAY & Video Playing
        await page.wait_for_timeout(2500)
        state_3 = await page.locator("#agent-pointer-state").inner_text()
        bubble_title = await page.locator("#agent-bubble-title").inner_text()
        bubble_text = await page.locator("#agent-bubble-text").inner_text()
        input_val_3 = await page.locator("#yt-browser-input").input_value()
        frame_src = await page.locator("#yt-player-frame").get_attribute("src")
        window_open = await page.evaluate("() => document.getElementById('virtual-yt-window').classList.contains('is-open')")

        print(f"[Test Phase 3] Window is-open: {window_open}")
        print(f"[Test Phase 3] Typed Song: {input_val_3}")
        print(f"[Test Phase 3] Pointer State: {state_3.encode('ascii', 'replace').decode('ascii')}")
        print(f"[Test Phase 3] Bubble Title: {bubble_title.encode('ascii', 'replace').decode('ascii')}")
        print(f"[Test Phase 3] Bubble Text: {bubble_text.encode('ascii', 'replace').decode('ascii')}")
        print(f"[Test Phase 3] YouTube Player Frame Src: {frame_src}")

        await page.screenshot(path=str(ARTIFACTS_DIR / "yt_tab_step3_playing_in_window.png"))
        print("[Test] Visual screenshots saved to artifacts directory.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

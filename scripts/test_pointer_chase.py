# scripts/test_pointer_chase.py
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACT_DIR = Path(r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777")

async def test_chase():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 840},
            device_scale_factor=1.5
        )
        page = await context.new_page()

        print("Navigating to http://localhost:8000 ...")
        await page.goto("http://localhost:8000", wait_until="networkidle")
        
        # Wait for gentle auto-entrance (2 seconds)
        print("Waiting for pointer auto-entrance...")
        await page.wait_for_timeout(2500)

        # Chase 1: Move mouse close to pointer
        box = await page.locator("#agent-pointer-cursor").bounding_box()
        assert box, "Pointer cursor not found on screen!"
        print(f"Pointer initial position: x={box['x']}, y={box['y']}")

        print("Chase #1: Moving mouse toward pointer...")
        await page.mouse.move(box["x"] + 10, box["y"] + 10)
        await page.wait_for_timeout(900)

        # Chase 2: Locate new position and move mouse toward it again
        box2 = await page.locator("#agent-pointer-cursor").bounding_box()
        print(f"Chase #2: Pointer leaped to x={box2['x']}, y={box2['y']}. Moving mouse again...")
        await page.mouse.move(box2["x"] + 10, box2["y"] + 10)
        await page.wait_for_timeout(900)

        # Chase 3: Locate new position and move mouse toward it the 3rd time
        box3 = await page.locator("#agent-pointer-cursor").bounding_box()
        print(f"Chase #3: Pointer leaped to x={box3['x']}, y={box3['y']}. Chasing 3rd time...")
        await page.mouse.move(box3["x"] + 10, box3["y"] + 10)
        await page.wait_for_timeout(1000)

        # Verify speech bubble popped up with the shortcut message!
        bubble = page.locator("#agent-pointer-bubble")
        assert await bubble.is_visible(), "Speech bubble did not appear on 3rd chase!"
        bubble_text = await page.locator("#agent-bubble-text").inner_text()
        print("Captured speech bubble text successfully")

        shot = ARTIFACT_DIR / "pointer_chase_bubble.png"
        await page.screenshot(path=str(shot))
        print(f"Screenshot saved to: {shot}")

        await browser.close()
        print("Playwright Chase test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_chase())

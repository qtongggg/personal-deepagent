# scripts/test_agent_command_hud.py
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACT_DIR = Path(r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777")

async def test_command_hud():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 840},
            device_scale_factor=1.5
        )
        page = await context.new_page()

        print("Navigating to http://localhost:8000 ...")
        await page.goto("http://localhost:8000", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 1. Trigger Ctrl+Shift+K
        print("Pressing Control+Shift+K to summon Command HUD...")
        await page.keyboard.press("Control+Shift+KeyK")
        await page.wait_for_timeout(600)

        # Verify Command HUD is visible
        hud = page.locator("#agent-command-overlay")
        assert await hud.is_visible(), "Command HUD is not visible!"
        print("Command HUD successfully opened.")

        shot1 = ARTIFACT_DIR / "command_hud_step1_opened.png"
        await page.screenshot(path=str(shot1))
        print(f"Captured HUD screenshot to: {shot1}")

        # 2. Click the quick chip: 'Show Projects'
        chip_projects = page.locator('.agent-cmd-chip[data-cmd="projects"]')
        print("Clicking Show Projects quick chip...")
        await chip_projects.click()

        # 3. Wait for pointer to glide to Details / Projects and click
        await page.wait_for_timeout(2500)
        shot2 = ARTIFACT_DIR / "command_hud_step2_pointer_projects.png"
        await page.screenshot(path=str(shot2))
        print(f"Captured Projects navigation screenshot to: {shot2}")

        # 4. Trigger Ctrl+Shift+K again to command Resume download
        print("Pressing Control+Shift+K again for Resume command...")
        await page.keyboard.press("Control+Shift+KeyK")
        await page.wait_for_timeout(600)

        chip_resume = page.locator('.agent-cmd-chip[data-cmd="resume"]')
        await chip_resume.click()

        # 5. Wait for pointer to glide up to the Resume PDF button
        await page.wait_for_timeout(2000)
        shot3 = ARTIFACT_DIR / "command_hud_step3_pointer_resume.png"
        await page.screenshot(path=str(shot3))
        print(f"Captured Resume navigation screenshot to: {shot3}")

        await browser.close()
        print("Playwright Command HUD test complete!")

if __name__ == "__main__":
    asyncio.run(test_command_hud())

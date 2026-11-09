# src/skills/browser_tab_skill.py
"""
Browser Tab Companion Skill
Enables the autonomous agent to navigate across external web tabs,
inspect live web pages (e.g., GitHub commits, PRs, team updates, documentation),
capture visual snapshots, and extract structured updates for synthesis.
"""

import asyncio
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool
from playwright.async_api import async_playwright

SNAPSHOT_DIR = Path("workspace/browser_snapshots")
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
UPDATES_FILE = Path("workspace/team_updates.md")


async def _async_browse(url: str, goal: str) -> str:
    """Headless browser session that loads url and extracts relevant updates."""
    clean_url = url.strip()
    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = "https://" + clean_url

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print(f"[Browser Skill] Navigating to {clean_url} ...")
            await page.goto(clean_url, timeout=20000, wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)

            title = await page.title()

            # Take a visual snapshot for workspace verification
            snapshot_filename = f"snapshot_{int(asyncio.get_event_loop().time())}.png"
            snapshot_path = SNAPSHOT_DIR / snapshot_filename
            await page.screenshot(path=str(snapshot_path))

            # Specialized GitHub Commit / PR extraction if target is GitHub
            extracted_items = []
            if "github.com" in clean_url:
                # Target commit titles or PR list items
                commit_els = await page.locator("a[data-pjax], .commit-title, [data-testid='commit-row-item'] a, h4.commit-title").all_text_contents()
                clean_commits = [c.strip() for c in commit_els if c.strip() and len(c.strip()) > 5][:8]
                if clean_commits:
                    extracted_items.append("### Recent Commits / Items Found:")
                    for idx, c in enumerate(clean_commits, 1):
                        extracted_items.append(f"{idx}. {c}")

            # General semantic content extraction
            if not extracted_items:
                headings = await page.locator("h1, h2, h3").all_text_contents()
                clean_headings = [h.strip() for h in headings if h.strip()][:6]
                if clean_headings:
                    extracted_items.append("### Page Headings:")
                    extracted_items.extend([f"- {h}" for h in clean_headings])

                # Main text content (up to 1200 characters)
                body_text = await page.locator("main, article, #readme, body").first.inner_text()
                clean_body = " ".join(body_text.split())[:1200]
                extracted_items.append(f"\n### Content Snippet:\n{clean_body}")

            result_text = f"**Page Title:** {title}\n**URL:** {clean_url}\n**Snapshot:** `{snapshot_path}`\n\n" + "\n".join(extracted_items)

            # Persist to workspace team updates log
            UPDATES_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(UPDATES_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n\n---\n## Check on {clean_url}\nGoal: {goal}\n\n{result_text}\n")

            return result_text

        except Exception as exc:
            return f"Error browsing {clean_url}: {str(exc)}"

        finally:
            await browser.close()


@tool
def browse_and_extract_web_updates(url: str, goal: str = "check recent updates") -> str:
    """Browse an external web tab, URL, or repository (e.g. GitHub repo, team updates page, Jira, or documentation).
    Use this tool whenever asked to inspect an external URL, follow up team updates, check recent commits/PRs,
    or read live content from the web.
    """
    try:
        # Check if already running inside an event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(_async_browse(url, goal))
        else:
            return asyncio.run(_async_browse(url, goal))
    except Exception:
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(_async_browse(url, goal))

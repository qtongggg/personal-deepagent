import asyncio
from playwright.async_api import async_playwright

INJECTOR_JS = """
(function() {
    if (document.getElementById('cross-tab-agent-pointer')) return;

    // 1. Add CSS
    const style = document.createElement('style');
    style.id = 'cross-tab-agent-style';
    style.textContent = `
        #cross-tab-agent-pointer {
            position: fixed;
            top: 0;
            left: 0;
            z-index: 2147483647;
            pointer-events: none;
            transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
            transform: translate3d(50vw, -100px, 0);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
        }
        .cross-pointer-body {
            position: relative;
            display: inline-block;
        }
        .cross-pointer-svg {
            width: 32px;
            height: 32px;
            filter: drop-shadow(0 3px 8px rgba(0,0,0,0.8)) drop-shadow(0 0 10px rgba(255, 92, 0, 0.8));
        }
        .cross-pointer-badge {
            position: absolute;
            top: 26px;
            left: 20px;
            background: rgba(10, 10, 15, 0.95);
            border: 1px solid rgba(255, 92, 0, 0.7);
            color: #ffffff;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.05em;
            padding: 3px 8px;
            border-radius: 4px;
            white-space: nowrap;
            box-shadow: 0 4px 15px rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .cross-badge-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #ff5c00;
            box-shadow: 0 0 8px #ff5c00;
        }
        .cross-pointer-state {
            position: absolute;
            top: 54px;
            left: 20px;
            background: rgba(255, 92, 0, 0.25);
            border: 1px solid rgba(255, 92, 0, 0.6);
            color: #ffaa77;
            font-size: 10px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            white-space: nowrap;
            backdrop-filter: blur(8px);
        }
        .cross-pointer-bubble {
            position: absolute;
            bottom: 40px;
            left: 24px;
            background: rgba(12, 14, 20, 0.96);
            border: 1px solid rgba(255, 92, 0, 0.6);
            border-radius: 8px;
            padding: 10px 14px;
            min-width: 240px;
            max-width: 340px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.85);
            opacity: 0;
            transform: translateY(6px);
            transition: all 0.3s ease;
        }
        .cross-pointer-bubble.is-visible {
            opacity: 1;
            transform: translateY(0);
        }
        .cross-bubble-title {
            color: #ff5c00;
            font-size: 10px;
            font-weight: 700;
            margin-bottom: 4px;
            text-transform: uppercase;
        }
        .cross-bubble-text {
            color: #ffffff;
            font-size: 12px;
            line-height: 1.4;
        }
        .cross-pointer-ripple {
            position: absolute;
            top: 0;
            left: 0;
            width: 44px;
            height: 44px;
            margin-top: -8px;
            margin-left: -8px;
            border: 2px solid #ff5c00;
            border-radius: 50%;
            pointer-events: none;
            opacity: 0;
            transform: scale(0.2);
        }
        .cross-pointer-ripple.is-clicking {
            animation: crossRipple 0.5s cubic-bezier(0.1, 0.8, 0.3, 1) forwards;
        }
        @keyframes crossRipple {
            0% { transform: scale(0.2); opacity: 1; border-color: #ff5c00; }
            100% { transform: scale(2.2); opacity: 0; border-color: #ffffff; }
        }
    `;
    document.head.appendChild(style);

    // 2. Safe DOM Construction (No innerHTML / TrustedHTML safe)
    const wrap = document.createElement('div');
    wrap.id = 'cross-tab-agent-pointer';

    const body = document.createElement('div');
    body.className = 'cross-pointer-body';

    // SVG Cursor Arrow via createElementNS
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'cross-pointer-svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'none');

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M4 4L11 20L14 13L21 10L4 4Z');
    path.setAttribute('fill', '#ff5c00');
    path.setAttribute('stroke', '#ffffff');
    path.setAttribute('stroke-width', '2.2');
    path.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(path);
    body.appendChild(svg);

    // Ripple
    const ripple = document.createElement('div');
    ripple.className = 'cross-pointer-ripple';
    body.appendChild(ripple);

    // Badge
    const badge = document.createElement('div');
    badge.className = 'cross-pointer-badge';
    const dot = document.createElement('span');
    dot.className = 'cross-badge-dot';
    const badgeText = document.createElement('span');
    badgeText.textContent = '● QT-AGENT GUIDE';
    badge.appendChild(dot);
    badge.appendChild(badgeText);
    body.appendChild(badge);

    // State Pill
    const statePill = document.createElement('div');
    statePill.className = 'cross-pointer-state';
    statePill.textContent = '[ 🌐 CROSSED OVER TO YOUTUBE ]';
    body.appendChild(statePill);

    // Thought Bubble
    const bubble = document.createElement('div');
    bubble.className = 'cross-pointer-bubble';
    const bTitle = document.createElement('div');
    bTitle.className = 'cross-bubble-title';
    bTitle.textContent = 'CROSS-TAB AGENT';
    const bText = document.createElement('div');
    bText.className = 'cross-bubble-text';
    bText.textContent = 'Arrived from your portfolio!';
    bubble.appendChild(bTitle);
    bubble.appendChild(bText);
    body.appendChild(bubble);

    wrap.appendChild(body);
    document.body.appendChild(wrap);

    window.__crossAgent = {
        pointer: wrap,
        state: statePill,
        bubble: bubble,
        bubbleTitle: bTitle,
        bubbleText: bText,
        ripple: ripple,
        moveTo(x, y, duration = 650) {
            wrap.style.transition = `transform ${duration}ms cubic-bezier(0.16, 1, 0.3, 1)`;
            wrap.style.transform = `translate3d(${Math.round(x)}px, ${Math.round(y)}px, 0)`;
        },
        setState(txt) {
            statePill.textContent = txt;
        },
        speak(title, text) {
            bTitle.textContent = title;
            bText.textContent = text;
            bubble.classList.add('is-visible');
        },
        hideSpeech() {
            bubble.classList.remove('is-visible');
        },
        clickRipple() {
            ripple.classList.remove('is-clicking');
            void ripple.offsetWidth;
            ripple.classList.add('is-clicking');
        }
    };
})();
"""

async def run_safe_test():
    async with async_playwright() as p:
        print("[Cross-Tab Test] Launching visible Chrome...")
        browser = await p.chromium.launch(headless=False, channel="chrome")
        context = await browser.new_context(viewport={"width": 1366, "height": 840})
        page = await context.new_page()

        print("[Cross-Tab Test] Navigating to https://www.youtube.com ...")
        await page.goto("https://www.youtube.com", wait_until="domcontentloaded")
        await page.wait_for_timeout(1500)

        print("[Cross-Tab Test] Injecting Cross-Tab Pointer (DOM API Safe)...")
        await page.evaluate(INJECTOR_JS)
        await page.wait_for_timeout(300)

        # Step 1: Pointer enters from top
        print("[Cross-Tab Test] Pointer gliding in from top...")
        await page.evaluate("""() => {
            window.__crossAgent.moveTo(window.innerWidth / 2, 80, 800);
            window.__crossAgent.setState('[ 🌐 Arrived From Portfolio Tab ]');
            window.__crossAgent.speak('CROSS-TAB AGENT', 'I have traveled across tabs to YouTube! Searching for your song...');
        }""")
        await page.wait_for_timeout(1400)

        # Step 2: Locate YouTube Search Box
        search_box = page.locator("input[name='search_query'], input#search").first
        await search_box.wait_for(timeout=10000)
        box_rect = await search_box.bounding_box()

        if box_rect:
            target_x = box_rect["x"] + 40
            target_y = box_rect["y"] + box_rect["height"] / 2
            print(f"[Cross-Tab Test] Pointer gliding to search input ({target_x}, {target_y})...")
            await page.evaluate(f"() => window.__crossAgent.moveTo({target_x}, {target_y}, 750)")
            await page.wait_for_timeout(800)

            await page.evaluate("() => window.__crossAgent.clickRipple()")
            await search_box.click()

            await page.evaluate("() => { window.__crossAgent.setState('[ ⌨️ Auto-Typing Song... ]'); window.__crossAgent.hideSpeech(); }")
            song = "lofi hip hop radio beats to relax study to"
            print(f"[Cross-Tab Test] Auto-typing song '{song}' ...")
            await search_box.fill("")
            for char in song:
                await search_box.type(char, delay=35)
                await page.wait_for_timeout(10)

            await page.wait_for_timeout(300)

            # Step 3: Glide to search icon
            search_btn = page.locator("button#search-icon-legacy, button[aria-label='Search']").first
            btn_rect = await search_btn.bounding_box()
            if btn_rect:
                btn_x = btn_rect["x"] + btn_rect["width"] / 2
                btn_y = btn_rect["y"] + btn_rect["height"] / 2
                await page.evaluate(f"() => window.__crossAgent.moveTo({btn_x}, {btn_y}, 500)")
                await page.wait_for_timeout(550)
                await page.evaluate("() => window.__crossAgent.clickRipple()")

            print("[Cross-Tab Test] Pressing Enter to search...")
            await search_box.press("Enter")
            await page.wait_for_timeout(3000)

            # Step 4: Click first video
            first_video = page.locator("ytd-video-renderer #video-title, #contents ytd-video-renderer a#thumbnail").first
            await first_video.wait_for(timeout=10000)
            vid_rect = await first_video.bounding_box()
            if vid_rect:
                vid_x = vid_rect["x"] + 80
                vid_y = vid_rect["y"] + vid_rect["height"] / 2
                print(f"[Cross-Tab Test] Gliding to first video at ({vid_x}, {vid_y})...")
                await page.evaluate(f"() => window.__crossAgent.moveTo({vid_x}, {vid_y}, 750)")
                await page.wait_for_timeout(800)
                await page.evaluate("() => window.__crossAgent.clickRipple()")
                await first_video.click()

            await page.wait_for_timeout(2000)
            await page.evaluate(f"""() => {{
                window.__crossAgent.setState('[ 🎵 Playing on YouTube ]');
                window.__crossAgent.speak('AGENT DJ 🎧', 'Now playing "{song}" on YouTube! Enjoy the music!');
            }}""")

            print("[Cross-Tab Test] Video is playing live in real Chrome! Keeping open for 15s...")
            await page.wait_for_timeout(15000)

        await browser.close()
        print("[Cross-Tab Test] Success!")

if __name__ == "__main__":
    asyncio.run(run_safe_test())

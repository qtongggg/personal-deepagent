import json
import os
from playwright.sync_api import sync_playwright

def main():
    md_path = r"C:\Users\User\.gemini\antigravity\brain\c39f0747-9fe2-42f7-ba3f-4b04c42cf777\codebase_architecture_learning_plan.md"
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    escaped_md = json.dumps(md_content)

    full_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Personal DeepAgent — Codebase Architecture & Learning Plan</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      line-height: 1.6;
      color: #1e293b;
      max-width: 820px;
      margin: 0 auto;
      padding: 30px;
      font-size: 13px;
    }}
    h1 {{ color: #0f172a; font-size: 22px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 0; }}
    h2 {{ color: #1e293b; font-size: 16px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; margin-top: 24px; }}
    h3 {{ color: #334155; font-size: 14px; margin-top: 18px; }}
    h4 {{ color: #475569; font-size: 13px; margin-top: 12px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 11.5px; page-break-inside: avoid; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 6px 10px; text-align: left; }}
    th {{ background: #f8fafc; font-weight: 600; color: #0f172a; }}
    tr:nth-child(even) {{ background: #f8fafc; }}
    pre {{ background: #0f172a; color: #e2e8f0; padding: 10px 12px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 11px; overflow-x: auto; margin: 12px 0; page-break-inside: avoid; }}
    code {{ font-family: 'JetBrains Mono', monospace; background: #f1f5f9; color: #0f172a; padding: 2px 4px; border-radius: 4px; font-size: 11px; }}
    pre code {{ background: transparent; color: inherit; padding: 0; }}
    blockquote {{ border-left: 3px solid #3b82f6; margin: 10px 0; padding: 6px 12px; color: #334155; background: #eff6ff; border-radius: 0 4px 4px 0; page-break-inside: avoid; }}
    a {{ color: #2563eb; text-decoration: none; }}
    hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 20px 0; }}
    ul, ol {{ padding-left: 20px; margin: 8px 0; }}
    li {{ margin-bottom: 4px; }}
  </style>
</head>
<body>
  <div id="content"></div>
  <script>
    const rawMarkdown = {escaped_md};
    document.getElementById('content').innerHTML = marked.parse(rawMarkdown);
  </script>
</body>
</html>"""

    docs_dir = r"c:\Users\User\Documents\antigravity\personal-deepagent\docs"
    os.makedirs(docs_dir, exist_ok=True)
    temp_html = os.path.join(docs_dir, "learning_plan_temp.html")
    pdf_path = os.path.join(docs_dir, "Personal_DeepAgent_Codebase_Learning_Plan.pdf")

    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(full_html)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file:///{temp_html.replace(chr(92), '/')}")
        page.wait_for_timeout(1500)
        page.pdf(
            path=pdf_path,
            format="A4",
            margin={"top": "18mm", "bottom": "18mm", "left": "15mm", "right": "15mm"},
            print_background=True
        )
        browser.close()

    if os.path.exists(temp_html):
        os.remove(temp_html)

    print("SUCCESS:", pdf_path)

if __name__ == "__main__":
    main()


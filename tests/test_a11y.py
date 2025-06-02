import json, pathlib, pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import sync_playwright

REPORT = pathlib.Path("tests/_a11y_report.json")

@pytest.mark.a11y
def test_homepage_accessibility():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page    = browser.new_page()
        page.goto("http://localhost:5000")

        # ✅ 1. 注入 axe-core（從 CDN）
        page.add_script_tag(
            url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js"
        )

        # ✅ 2. 執行 axe.run()，並取得結果
        results = page.evaluate("async () => await axe.run()")

        # ✅ 3. 輸出報告 + 驗證違規是否為空
        REPORT.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        assert results["violations"] == [], (
            "A11y violations:\n" +
            "\n".join(f"- {v['id']}: {v['help']}" for v in results["violations"])
        )
# tests/test_resilience.py
import pytest, time
from playwright.sync_api import sync_playwright

@pytest.mark.resilience
def test_socketio_reconnect_sync():
    with sync_playwright() as p:
        browser  = p.chromium.launch()
        context  = browser.new_context()
        page     = context.new_page()

        # A. 正常進入聊天室
        page.goto("http://localhost:5000")
        page.fill("#usernameInput", "ReconnectUser")
        page.keyboard.press("Enter")
        page.wait_for_selector(".message-input", timeout=3_000)

        # B. 斷線 5 秒
        context.set_offline(True)
        page.wait_for_function("window.socket.connected === false", timeout=15_000)

        # C. 恢復網路
        context.set_offline(False)
        page.wait_for_function("window.socket.connected === true", timeout=10_000)

        # 若 chat.js 已自動 re-join 可跳過，否則：
        page.evaluate("""() => {
            window.socket.emit('join', {username:'ReconnectUser', room:'general'});
        }""")

        # D. 發訊息驗證
        page.fill("#messageInput", "still alive")
        page.keyboard.press("Enter")
        page.wait_for_selector("text=still alive", timeout=3_000)

        browser.close()
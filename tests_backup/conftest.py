# conftest.py - pytest 配置文件
import pytest
import subprocess
import time
import requests
import os
import signal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 全局配置
TEST_SERVER_URL = "http://localhost:5000"
SERVER_STARTUP_TIMEOUT = 10

@pytest.fixture(scope="session")
def chat_server():
    """启动聊天服务器的fixture"""
    print("启动聊天服务器...")
    
    # 启动服务器进程
    server_process = subprocess.Popen(
        ["python", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待服务器启动
    for _ in range(SERVER_STARTUP_TIMEOUT):
        try:
            response = requests.get(TEST_SERVER_URL, timeout=1)
            if response.status_code == 200:
                print("服务器启动成功!")
                break
        except requests.ConnectionError:
            time.sleep(1)
    else:
        server_process.kill()
        pytest.fail("服务器启动失败")
    
    yield server_process
    
    # 清理：停止服务器
    print("停止聊天服务器...")
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()

@pytest.fixture(scope="session")
def browser_driver():
    """创建浏览器驱动的fixture"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()

@pytest.fixture(autouse=True)
def clean_test_data():
    """每个测试前清理数据"""
    # 清理在线用户和消息
    from app import online_users, chat_messages
    online_users.clear()
    chat_messages.clear()
    
    yield
    
    # 测试后清理
    online_users.clear()
    chat_messages.clear()

# pytest配置
def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "ui: marks tests as UI tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )

def pytest_collection_modifyitems(config, items):
    """自动为测试添加标记"""
    for item in items:
        # 为UI测试添加标记
        if "selenium" in item.nodeid or "ui" in item.nodeid:
            item.add_marker(pytest.mark.ui)
        
        # 为性能测试添加标记
        if "performance" in item.nodeid or "stress" in item.nodeid:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        
        # 为集成测试添加标记
        if "socketio" in item.nodeid or "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
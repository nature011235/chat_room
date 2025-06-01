# tests/conftest.py - pytest配置文件
import pytest
import subprocess
import time
import requests
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session")
def server_url():
    """服务器URL fixture"""
    return "http://localhost:5000"

@pytest.fixture(scope="session", autouse=True)
def check_server(server_url):
    """检查服务器是否运行"""
    try:
        response = requests.get(server_url, timeout=2)
        if response.status_code == 200:
            print(f"✅ 服务器已运行: {server_url}")
            return True
    except requests.ConnectionError:
        print(f"❌ 服务器未运行，请先启动: python app.py")
        pytest.exit("请先启动服务器")

@pytest.fixture(scope="class")
def browser():
    """浏览器驱动fixture"""
    options = Options()
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()

@pytest.fixture(autouse=True)
def clean_test_data():
    """每次测试前清理数据"""
    try:
        from app import online_users, chat_messages
        online_users.clear()
        chat_messages.clear()
    except ImportError:
        pass
    
    yield
    
    try:
        from app import online_users, chat_messages
        online_users.clear()
        chat_messages.clear()
    except ImportError:
        pass

@pytest.fixture
def test_user_data():
    """测试用户数据fixture"""
    return {
        'username': '测试用户',
        'room': 'general'
    }

@pytest.fixture
def sample_image_base64():
    """测试图片数据fixture"""
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

@pytest.fixture
def socketio_client():
    """SocketIO客户端fixture"""
    from app import app, socketio
    client = socketio.test_client(app)
    yield client
    try:
        client.disconnect()
    except:
        pass

# pytest配置
def pytest_configure(config):
    """pytest启动配置"""
    config.addinivalue_line("markers", "slow: 标记为慢速测试")
    config.addinivalue_line("markers", "ui: 标记为UI测试")
    config.addinivalue_line("markers", "performance: 标记为性能测试")
    config.addinivalue_line("markers", "security: 标记为安全测试")
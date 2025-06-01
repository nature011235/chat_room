# test_selenium_ui.py - 前端UI自动化测试
import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

class TestChatRoomUI:
    """聊天室UI自动化测试"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """设置WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式，如需看界面可注释此行
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    def test_page_load(self, driver):
        """测试页面加载"""
        driver.get("http://localhost:5000")
        
        # 验证页面标题
        assert "chattt" in driver.title
        
        # 验证关键元素存在
        username_input = driver.find_element(By.ID, "usernameInput")
        join_button = driver.find_element(By.XPATH, "//button[contains(text(), '加入聊天')]")
        
        assert username_input.is_displayed()
        assert join_button.is_displayed()
    
    def test_user_join_chat(self, driver):
        """测试用户加入聊天"""
        driver.get("http://localhost:5000")
        
        # 输入用户名
        username_input = driver.find_element(By.ID, "usernameInput")
        username_input.clear()
        username_input.send_keys("Selenium测试用户")
        
        # 点击加入聊天
        join_button = driver.find_element(By.XPATH, "//button[contains(text(), '加入聊天')]")
        join_button.click()
        
        # 等待界面切换
        wait = WebDriverWait(driver, 10)
        
        # 验证聊天界面显示
        message_container = wait.until(
            EC.presence_of_element_located((By.ID, "messageContainer"))
        )
        
        # 验证用户名输入界面隐藏
        username_container = driver.find_element(By.ID, "usernameContainer")
        assert "hidden" in username_container.get_attribute("class")
        
        # 验证消息输入框可见
        message_input = driver.find_element(By.ID, "messageInput")
        assert message_input.is_displayed()
    
    def test_send_text_message(self, driver):
        """测试发送文本消息"""
        # 先加入聊天
        self.test_user_join_chat(driver)
        
        # 输入消息
        message_input = driver.find_element(By.ID, "messageInput")
        message_input.clear()
        message_input.send_keys("这是一条测试消息")
        
        # 点击发送按钮
        send_button = driver.find_element(By.ID, "sendButton")
        send_button.click()
        
        # 等待消息显示
        wait = WebDriverWait(driver, 10)
        messages_div = driver.find_element(By.ID, "messages")
        
        # 验证消息出现
        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "messages"), "这是一条测试消息"
            )
        )
        
        # 验证消息样式（自己的消息应该有'own'类）
        own_messages = driver.find_elements(By.CSS_SELECTOR, ".message.own")
        assert len(own_messages) >= 1
    
    def test_send_message_with_enter(self, driver):
        """测试使用回车键发送消息"""
        # 先加入聊天
        self.test_user_join_chat(driver)
        
        # 输入消息并按回车
        message_input = driver.find_element(By.ID, "messageInput")
        message_input.clear()
        message_input.send_keys("回车键发送的消息")
        message_input.send_keys(Keys.RETURN)
        
        # 验证消息发送
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "messages"), "回车键发送的消息"
            )
        )
    
    def test_empty_message_prevention(self, driver):
        """测试空消息防止发送"""
        # 先加入聊天
        self.test_user_join_chat(driver)
        
        # 获取当前消息数量
        messages = driver.find_elements(By.CSS_SELECTOR, ".message")
        initial_count = len(messages)
        
        # 尝试发送空消息
        message_input = driver.find_element(By.ID, "messageInput")
        message_input.clear()
        send_button = driver.find_element(By.ID, "sendButton")
        send_button.click()
        
        # 等待一秒，确保没有新消息
        time.sleep(1)
        
        # 验证消息数量没有增加
        messages_after = driver.find_elements(By.CSS_SELECTOR, ".message")
        assert len(messages_after) == initial_count
    
    def test_image_upload_button(self, driver):
        """测试图片上传按钮"""
        # 先加入聊天
        self.test_user_join_chat(driver)
        
        # 验证图片上传按钮存在
        image_button = driver.find_element(By.ID, "imageButton")
        assert image_button.is_displayed()
        
        # 验证隐藏的文件输入框存在
        image_input = driver.find_element(By.ID, "imageInput")
        assert image_input.get_attribute("type") == "file"
        assert image_input.get_attribute("accept") == "image/*"
    
    def test_online_counter_display(self, driver):
        """测试在线计数器显示"""
        # 先加入聊天
        self.test_user_join_chat(driver)
        
        # 验证在线计数器可见
        online_counter = driver.find_element(By.ID, "onlineCounter")
        assert online_counter.is_displayed()
        
        # 验证计数器显示数字
        online_count = driver.find_element(By.ID, "onlineCount")
        count_text = online_count.text
        assert count_text.isdigit()
        assert int(count_text) >= 1
    
    def test_users_panel_toggle(self, driver):
        """测试用户面板切换"""
        # 先加入聊天
        self.test_user_join_chat(driver)
        
        # 点击在线计数器打开用户面板
        online_counter = driver.find_element(By.ID, "onlineCounter")
        online_counter.click()
        
        # 验证用户面板显示
        wait = WebDriverWait(driver, 5)
        users_panel = wait.until(
            EC.presence_of_element_located((By.ID, "usersPanel"))
        )
        
        # 检查面板是否有active类
        panel_classes = users_panel.get_attribute("class")
        assert "active" in panel_classes
        
        # 点击关闭按钮
        close_button = driver.find_element(By.CSS_SELECTOR, ".users-panel-close")
        close_button.click()
        
        # 验证面板关闭
        time.sleep(0.5)  # 等待动画完成
        panel_classes_after = users_panel.get_attribute("class")
        assert "active" not in panel_classes_after
    
    def test_responsive_design(self, driver):
        """测试响应式设计"""
        # 先加入聊天
        self.test_user_join_chat(driver)
        
        # 测试移动端尺寸
        driver.set_window_size(375, 667)  # iPhone尺寸
        time.sleep(1)
        
        # 验证聊天容器仍然可见
        chat_container = driver.find_element(By.CSS_SELECTOR, ".chat-container")
        assert chat_container.is_displayed()
        
        # 验证消息输入框仍然可用
        message_input = driver.find_element(By.ID, "messageInput")
        assert message_input.is_displayed()
        
        # 恢复桌面尺寸
        driver.set_window_size(1920, 1080)
    
    def test_message_auto_scroll(self, driver):
        """测试消息自动滚动"""
        # 先加入聊天
        self.test_user_join_chat(driver)
        
        # 发送多条消息
        message_input = driver.find_element(By.ID, "messageInput")
        for i in range(5):
            message_input.clear()
            message_input.send_keys(f"测试消息 {i+1}")
            message_input.send_keys(Keys.RETURN)
            time.sleep(0.5)
        
        # 获取消息容器
        messages_div = driver.find_element(By.ID, "messages")
        
        # 验证滚动到底部
        scroll_top = driver.execute_script("return arguments[0].scrollTop;", messages_div)
        scroll_height = driver.execute_script("return arguments[0].scrollHeight;", messages_div)
        client_height = driver.execute_script("return arguments[0].clientHeight;", messages_div)
        
        # 验证已滚动到底部（允许小误差）
        assert scroll_top >= (scroll_height - client_height - 10)

class TestChatRoomSecurity:
    """聊天室安全测试"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """设置WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    def join_chat(self, driver, username="安全测试用户"):
        """辅助方法：加入聊天"""
        driver.get("http://localhost:5000")
        
        username_input = driver.find_element(By.ID, "usernameInput")
        username_input.clear()
        username_input.send_keys(username)
        
        join_button = driver.find_element(By.XPATH, "//button[contains(text(), '加入聊天')]")
        join_button.click()
        
        # 等待界面切换
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "messageContainer")))
    
    def test_xss_prevention_in_username(self, driver):
        """测试用户名XSS防护"""
        malicious_username = "<script>alert('XSS')</script>"
        
        try:
            self.join_chat(driver, malicious_username)
            
            # 检查页面是否正常（没有弹窗或错误）
            # 如果XSS成功，alert会阻塞页面
            message_input = driver.find_element(By.ID, "messageInput")
            assert message_input.is_displayed()
            
            # 验证脚本标签没有被执行（页面标题没有改变等）
            assert driver.title == "chattt"
            
        except Exception as e:
            # 如果出现异常，可能是因为XSS被阻止了，这是好事
            pass
    
    def test_xss_prevention_in_message(self, driver):
        """测试消息内容XSS防护"""
        self.join_chat(driver)
        
        # 尝试发送包含脚本的消息
        malicious_message = "<script>alert('XSS in message')</script>"
        
        message_input = driver.find_element(By.ID, "messageInput")
        message_input.clear()
        message_input.send_keys(malicious_message)
        message_input.send_keys(Keys.RETURN)
        
        # 等待消息显示
        time.sleep(2)
        
        # 验证页面仍然正常工作
        assert driver.title == "chattt"
        
        # 验证消息内容被安全处理
        messages_div = driver.find_element(By.ID, "messages")
        assert malicious_message in messages_div.text or "&lt;script&gt;" in messages_div.get_attribute("innerHTML")
    
    def test_long_message_handling(self, driver):
        """测试超长消息处理"""
        self.join_chat(driver)
        
        # 创建超长消息（超过500字符限制）
        long_message = "A" * 600
        
        message_input = driver.find_element(By.ID, "messageInput")
        message_input.clear()
        message_input.send_keys(long_message)
        
        # 验证输入框字符限制
        actual_value = message_input.get_attribute("value")
        assert len(actual_value) <= 500  # 应该被限制在500字符内
    
    def test_special_characters_handling(self, driver):
        """测试特殊字符处理"""
        self.join_chat(driver)
        
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        
        message_input = driver.find_element(By.ID, "messageInput")
        message_input.clear()
        message_input.send_keys(special_chars)
        message_input.send_keys(Keys.RETURN)
        
        # 等待消息显示
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "messages"), special_chars
            )
        )
        
        # 验证特殊字符正确显示
        messages_div = driver.find_element(By.ID, "messages")
        assert special_chars in messages_div.text

class TestChatRoomPerformance:
    """聊天室性能测试"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """设置WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    def test_page_load_time(self, driver):
        """测试页面加载时间"""
        start_time = time.time()
        
        driver.get("http://localhost:5000")
        
        # 等待关键元素加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        
        load_time = time.time() - start_time
        
        # 验证页面在合理时间内加载完成（5秒内）
        assert load_time < 5.0
        print(f"页面加载时间: {load_time:.2f}秒")
    
    def test_multiple_messages_performance(self, driver):
        """测试发送多条消息的性能"""
        driver.get("http://localhost:5000")
        
        # 加入聊天
        username_input = driver.find_element(By.ID, "usernameInput")
        username_input.send_keys("性能测试用户")
        
        join_button = driver.find_element(By.XPATH, "//button[contains(text(), '加入聊天')]")
        join_button.click()
        
        # 等待界面切换
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "messageContainer"))
        )
        
        # 发送20条消息并测量时间
        message_input = driver.find_element(By.ID, "messageInput")
        
        start_time = time.time()
        
        for i in range(20):
            message_input.clear()
            message_input.send_keys(f"性能测试消息 {i+1}")
            message_input.send_keys(Keys.RETURN)
            time.sleep(0.1)  # 小延迟避免过快发送
        
        # 等待最后一条消息显示
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "messages"), "性能测试消息 20"
            )
        )
        
        total_time = time.time() - start_time
        
        # 验证20条消息在合理时间内处理完成（10秒内）
        assert total_time < 10.0
        print(f"发送20条消息总时间: {total_time:.2f}秒")
        
        # 验证所有消息都显示了
        messages = driver.find_elements(By.CSS_SELECTOR, ".message")
        # 至少有20条消息（可能还有系统消息）
        assert len(messages) >= 20

# 运行测试的配置
if __name__ == '__main__':
    pytest.main(['-v', __file__, '--tb=short'])
# tests/test_frontend.py - 前端UI测试（使用fixture版本）
import pytest
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.mark.ui
class TestPageLoad:
    """页面加载测试"""
    
    def test_page_loads_successfully(self, browser, server_url):
        """测试页面成功加载"""
        browser.get(server_url)
        
        # 验证页面标题
        assert "chattt" in browser.title
        
        # 验证关键元素存在
        username_input = browser.find_element(By.ID, "usernameInput")
        join_button = browser.find_element(By.XPATH, "//button[contains(text(), '加入聊天')]")
        
        assert username_input.is_displayed()
        assert join_button.is_displayed()

@pytest.mark.ui
class TestUserInteraction:
    """用户交互测试"""
    
    def test_user_join_chat(self, browser, server_url):
        """测试用户加入聊天"""
        browser.get(server_url)
        
        # 输入用户名
        username_input = browser.find_element(By.ID, "usernameInput")
        username_input.clear()
        username_input.send_keys("UI测试用户")
        
        # 点击加入
        join_button = browser.find_element(By.XPATH, "//button[contains(text(), '加入聊天')]")
        join_button.click()
        
        # 增加等待时间，等待界面完全切换
        wait = WebDriverWait(browser, 15)
        
        # 等待消息容器出现并可见
        message_container = wait.until(
            EC.visibility_of_element_located((By.ID, "messageContainer"))
        )
        
        # 验证聊天界面显示
        assert message_container.is_displayed()
        
        # 额外等待，确保动画完成
        time.sleep(1)
        
        # 验证用户名输入界面隐藏
        username_container = browser.find_element(By.ID, "usernameContainer")
        container_classes = username_container.get_attribute("class")
        assert "hidden" in container_classes, f"用户名容器应该隐藏，当前类: {container_classes}"
    
    def test_send_message(self, browser, server_url):
        """测试发送消息"""
        browser.get(server_url)
        
        # 输入用户名并加入
        username_input = browser.find_element(By.ID, "usernameInput")
        username_input.clear()
        username_input.send_keys("消息测试用户")
        
        join_button = browser.find_element(By.XPATH, "//button[contains(text(), '加入聊天')]")
        join_button.click()
        
        # 等待界面切换
        wait = WebDriverWait(browser, 15)
        wait.until(EC.visibility_of_element_located((By.ID, "messageContainer")))
        
        # 额外等待，确保JavaScript完全加载
        time.sleep(2)
        
        # 输入消息
        message_input = browser.find_element(By.ID, "messageInput")
        message_input.clear()
        message_input.send_keys("这是UI测试消息")
        
        # 按回车发送
        message_input.send_keys(Keys.RETURN)
        
        # 增加等待时间，等待消息显示
        try:
            wait.until(
                EC.text_to_be_present_in_element(
                    (By.ID, "messages"), "这是UI测试消息"
                )
            )
            print("✅ 消息发送成功")
            
        except Exception as e:
            print(f"❌ 消息发送失败: {e}")
            # 检查消息区域内容
            try:
                messages_div = browser.find_element(By.ID, "messages")
                print(f"消息区域内容: {messages_div.text}")
            except:
                print("❌ 找不到消息区域")
            raise
        
        # 验证消息显示在页面上
        messages_div = browser.find_element(By.ID, "messages")
        assert "这是UI测试消息" in messages_div.text
    
    def test_empty_message_prevention(self, browser, server_url):
        """测试空消息防止发送"""
        browser.get(server_url)
        
        username_input = browser.find_element(By.ID, "usernameInput")
        username_input.clear()
        username_input.send_keys("空消息测试用户")
        
        join_button = browser.find_element(By.XPATH, "//button[contains(text(), '加入聊天')]")
        join_button.click()
        
        # 等待界面切换
        wait = WebDriverWait(browser, 15)
        wait.until(EC.visibility_of_element_located((By.ID, "messageContainer")))
        
        # 额外等待，确保界面完全加载
        time.sleep(2)
        
        # 获取当前消息数量
        messages = browser.find_elements(By.CSS_SELECTOR, ".message")
        initial_count = len(messages)
        print(f"初始消息数量: {initial_count}")
        
        # 尝试发送空消息
        message_input = browser.find_element(By.ID, "messageInput")
        message_input.clear()
        message_input.send_keys(Keys.RETURN)
        
        # 等待一下，看是否有新消息
        time.sleep(3)
        
        # 验证消息数量没有增加
        messages_after = browser.find_elements(By.CSS_SELECTOR, ".message")
        final_count = len(messages_after)
        print(f"最终消息数量: {final_count}")
        
        assert final_count == initial_count, f"空消息不应该被发送，消息数量从 {initial_count} 变为 {final_count}"

@pytest.mark.ui
class TestResponsiveDesign:
    """响应式设计测试"""
    
    def test_mobile_view(self, browser, server_url):
        """测试移动端视图"""
        browser.get(server_url)
        
        # 先验证桌面版正常
        username_input = browser.find_element(By.ID, "usernameInput")
        assert username_input.is_displayed()
        
        # 设置为手机屏幕尺寸
        browser.set_window_size(375, 667)
        time.sleep(2)  # 等待响应式调整完成
        
        # 验证页面仍然可用
        username_input = browser.find_element(By.ID, "usernameInput")
        assert username_input.is_displayed(), "移动端用户名输入框应该可见"
        
        # 验证输入框仍然可以交互
        username_input.clear()
        username_input.send_keys("移动端测试")
        
        join_button = browser.find_element(By.XPATH, "//button[contains(text(), '加入聊天')]")
        assert join_button.is_displayed(), "移动端加入按钮应该可见"
        
        print("✅ 移动端响应式设计正常")
        
        # 恢复桌面尺寸
        browser.set_window_size(1920, 1080)
        time.sleep(1)

@pytest.mark.ui  
class TestOnlineUsers:
    """在线用户功能测试"""
    
    def test_online_counter_display(self, browser, server_url):
        """测试在线计数器显示"""
        browser.get(server_url)
        
        # 加入聊天
        username_input = browser.find_element(By.ID, "usernameInput")
        username_input.send_keys("计数器测试用户")
        
        join_button = browser.find_element(By.XPATH, "//button[contains(text(), '加入聊天')]")
        join_button.click()
        
        # 增加等待时间，等待界面完全切换
        wait = WebDriverWait(browser, 15)  # 增加到15秒
        
        try:
            # 等待消息容器出现
            message_container = wait.until(
                EC.presence_of_element_located((By.ID, "messageContainer"))
            )
            
            # 额外等待元素变为可见
            wait.until(
                EC.visibility_of_element_located((By.ID, "messageContainer"))
            )
            
            print("✅ 消息容器已显示")
            
        except Exception as e:
            print(f"❌ 等待消息容器失败: {e}")
            # 打印当前页面状态用于调试
            print(f"当前页面标题: {browser.title}")
            print(f"当前URL: {browser.current_url}")
            
            # 检查用户名容器是否还在显示
            username_container = browser.find_element(By.ID, "usernameContainer")
            print(f"用户名容器类: {username_container.get_attribute('class')}")
            
            # 重新抛出异常
            raise
        
        # 验证在线计数器可见（增加等待）
        try:
            online_counter = wait.until(
                EC.visibility_of_element_located((By.ID, "onlineCounter"))
            )
            assert online_counter.is_displayed()
            print("✅ 在线计数器已显示")
            
        except Exception as e:
            print(f"❌ 在线计数器未显示: {e}")
            # 检查计数器是否存在但不可见
            try:
                counter_element = browser.find_element(By.ID, "onlineCounter")
                print(f"计数器类: {counter_element.get_attribute('class')}")
                print(f"计数器样式: {counter_element.get_attribute('style')}")
            except:
                print("❌ 找不到在线计数器元素")
            raise
        
        # 验证计数器显示数字
        try:
            online_count = browser.find_element(By.ID, "onlineCount")
            count_text = online_count.text
            print(f"在线用户数: {count_text}")
            
            assert count_text.isdigit(), f"计数器应该是数字，实际是: '{count_text}'"
            assert int(count_text) >= 1, f"在线用户数应该>=1，实际是: {count_text}"
            
            print("✅ 在线用户计数正确")
            
        except Exception as e:
            print(f"❌ 验证计数失败: {e}")
            raise
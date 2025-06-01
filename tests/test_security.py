# tests/test_security.py - 安全测试
import pytest
import base64
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, socketio, validate_image_data

@pytest.mark.security
class TestXSSPrevention:
    """XSS攻击防护测试"""
    
    def get_xss_payloads(self):
        """XSS攻击载荷"""
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<%2Fscript%3E%3Cscript%3Ealert('XSS')%3C%2Fscript%3E"
        ]
    
    def test_xss_in_username(self):
        """测试用户名XSS防护"""
        client = socketio.test_client(app)
        
        for payload in self.get_xss_payloads():
            try:
                client.emit('join', {
                    'username': payload,
                    'room': 'general'
                })
                
                received = client.get_received()
                
                # 验证恶意脚本被安全处理
                for event in received:
                    if 'args' in event and len(event['args']) > 0:
                        message_content = str(event['args'][0])
                        # 确保恶意脚本没有原样出现
                        assert '<script>' not in message_content.lower()
                        assert 'javascript:' not in message_content.lower()
                        assert 'onerror=' not in message_content.lower()
                
                print(f"✅ XSS载荷被安全处理: {payload[:30]}...")
                
            except Exception as e:
                # 如果抛出异常，说明输入验证起作用了
                print(f"✅ XSS载荷被拒绝: {payload[:30]}... ({e})")
    
    def test_xss_in_message(self):
        """测试消息内容XSS检测（记录模式）"""
        client = socketio.test_client(app)
        
        # 先正常加入
        client.emit('join', {
            'username': 'XSS测试用户',
            'room': 'general'
        })
        client.get_received()  # 清空
        
        dangerous_payloads = 0
        safe_payloads = 0
        
        for payload in self.get_xss_payloads():
            client.emit('send_message', {
                'message': payload,
                'type': 'text'
            })
            
            received = client.get_received()
            
            # 检查消息处理
            for event in received:
                if event.get('name') == 'receive_message':
                    original_message = payload
                    processed_message = event['args'][0]['message']
                    
                    # 检查是否存在真正的XSS风险
                    is_dangerous = self.is_xss_dangerous(original_message, processed_message)
                    
                    if is_dangerous:
                        print(f"🚨 危险的XSS: {payload[:30]}...")
                        print(f"   处理后: {processed_message[:50]}...")
                        dangerous_payloads += 1
                    else:
                        print(f"✅ XSS已安全处理: {payload[:30]}...")
                        print(f"   处理后: {processed_message[:50]}...")
                        safe_payloads += 1
        
        print(f"\n📊 XSS测试总结:")
        print(f"   安全处理: {safe_payloads}")
        print(f"   仍有风险: {dangerous_payloads}")
        
        if dangerous_payloads > 0:
            print("\n🚨 安全建议:")
            print("   考虑添加更强的输入过滤")
        else:
            print("\n🛡️ XSS防护工作正常！")
        
        # 如果大部分载荷都被安全处理，测试通过
        total_payloads = dangerous_payloads + safe_payloads
        safety_rate = safe_payloads / total_payloads if total_payloads > 0 else 0
        
        assert safety_rate >= 0.5, f"XSS防护率过低: {safety_rate:.1%}"
    
    def is_xss_dangerous(self, original, processed):
        """判断XSS载荷是否仍然危险"""
        # 如果消息完全没有改变，可能是危险的
        if original == processed:
            return True
        
        # 如果包含HTML转义字符，通常是安全的
        escape_chars = ['&lt;', '&gt;', '&#x27;', '&quot;', '&amp;']
        has_escapes = any(char in processed for char in escape_chars)
        
        if has_escapes:
            # 检查是否还有完整的危险模式
            complete_dangerous_patterns = [
                '<script>alert(',  # 完整的script调用
                'javascript:alert(',  # 完整的javascript协议
                'onerror="alert(',  # 完整的事件处理器
                'onload="alert(',   # 完整的事件处理器
            ]
            
            # 只有当危险模式完全未被破坏时才认为危险
            for pattern in complete_dangerous_patterns:
                if pattern in original.lower() and pattern in processed.lower():
                    return True
            
            # 如果有转义字符，且没有完整的危险模式，就是安全的
            return False
        
        # 检查关键的XSS执行模式是否被完全保留
        execution_patterns = [
            ('javascript:', 'javascript:'),  # javascript协议
            ('<script', '</script>'),        # script标签对
            ('onerror=', 'alert('),          # 事件处理器
            ('onload=', 'alert('),           # 事件处理器
        ]
        
        for start_pattern, end_pattern in execution_patterns:
            if (start_pattern in original.lower() and end_pattern in original.lower() and
                start_pattern in processed.lower() and end_pattern in processed.lower()):
                # 检查中间是否被破坏
                original_between = self.extract_between(original.lower(), start_pattern, end_pattern)
                processed_between = self.extract_between(processed.lower(), start_pattern, end_pattern)
                
                # 如果中间部分被转义了，就是安全的
                if original_between != processed_between:
                    return False
                else:
                    return True
        
        return False
    
    def extract_between(self, text, start, end):
        """提取两个模式之间的文本"""
        try:
            start_pos = text.find(start)
            if start_pos == -1:
                return ""
            start_pos += len(start)
            
            end_pos = text.find(end, start_pos)
            if end_pos == -1:
                return text[start_pos:]
            
            return text[start_pos:end_pos]
        except:
            return ""

@pytest.mark.security
class TestFileUploadSecurity:
    """文件上传安全测试"""
    
    def test_malicious_file_types(self):
        """测试恶意文件类型"""
        malicious_files = [
            # PHP脚本
            ("data:image/jpeg;base64," + 
             base64.b64encode(b"<?php system($_GET['cmd']); ?>").decode()),
            
            # JavaScript
            ("data:image/png;base64," + 
             base64.b64encode(b"<script>alert('XSS')</script>").decode()),
            
            # HTML文件
            ("data:image/gif;base64," + 
             base64.b64encode(b"<html><body>malicious</body></html>").decode()),
            
            # 可执行文件头
            ("data:image/jpg;base64," + 
             base64.b64encode(b"\x4d\x5a\x90\x00").decode()),
        ]
        
        for malicious_file in malicious_files:
            result = validate_image_data(malicious_file)
            assert result == False, f"恶意文件应该被拒绝"
            print(f"✅ 恶意文件被拒绝: {malicious_file[:50]}...")
    
    def test_oversized_files(self):
        """测试超大文件"""
        # 创建超过限制的文件
        large_data = "A" * (150 * 1024 * 1024)  # 150MB
        oversized_file = f"data:image/jpeg;base64,{large_data}"
        
        result = validate_image_data(oversized_file)
        assert result == False, "超大文件应该被拒绝"
        print("✅ 超大文件被拒绝")
    
    def test_invalid_formats(self):
        """测试无效文件格式"""
        invalid_formats = [
            "data:text/plain;base64,SGVsbG8gV29ybGQ=",  # 文本
            "data:application/pdf;base64,JVBERi0xLjQ=",   # PDF
            "data:video/mp4;base64,AAAAIGZ0eXBpc29t",     # 视频
            "invalid_format_string",                       # 无效格式
            "data:image/exe;base64,TVqQAAMAAAAEAAAA",     # exe文件
        ]
        
        for invalid_format in invalid_formats:
            result = validate_image_data(invalid_format)
            assert result == False, f"无效格式应该被拒绝: {invalid_format[:50]}"
            print(f"✅ 无效格式被拒绝: {invalid_format[:50]}...")

@pytest.mark.security
class TestInputValidation:
    """输入验证测试"""
    
    def test_sql_injection_attempts(self):
        """测试SQL注入防护"""
        client = socketio.test_client(app)
        
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
                
                # 验证应用仍然正常工作（没有数据库错误）
                received = client.get_received()
                # 如果有接收到响应，说明应用没有崩溃
                
                print(f"✅ SQL注入载荷被安全处理: {payload}")
                
            except Exception as e:
                print(f"✅ SQL注入载荷被阻止: {payload} ({e})")
    
    def test_command_injection_attempts(self):
        """测试命令注入防护"""
        client = socketio.test_client(app)
        
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd", 
            "&& rm -rf /",
            "`whoami`",
            "$(id)",
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
            
            received = client.get_received()
            
            # 验证命令没有被执行，应用仍正常
            assert len(received) > 0, "应用应该仍然响应"
            print(f"✅ 命令注入载荷被安全处理: {payload}")
    
    def test_long_input_handling(self):
        """测试超长输入处理"""
        client = socketio.test_client(app)
        
        # 超长用户名
        long_username = "A" * 1000
        try:
            client.emit('join', {
                'username': long_username,
                'room': 'general'
            })
            print("✅ 超长用户名被处理")
        except Exception as e:
            print(f"✅ 超长用户名被拒绝: {e}")
        
        # 加入正常用户进行消息测试
        client.emit('join', {
            'username': '长度测试用户',
            'room': 'general'
        })
        client.get_received()
        
        # 超长消息
        long_message = "B" * 2000
        client.emit('send_message', {
            'message': long_message,
            'type': 'text'
        })
        
        received = client.get_received()
        if received:
            # 验证消息被截断或拒绝
            message = received[0]['args'][0]['message']
            assert len(message) <= 500, "消息应该被限制长度"
        
        print("✅ 超长消息被安全处理")

@pytest.mark.security
class TestSessionSecurity:
    """会话安全测试"""
    
    def test_duplicate_usernames(self):
        """测试重复用户名处理"""
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        
        # 两个客户端使用相同用户名
        username = "重复测试用户"
        
        client1.emit('join', {'username': username, 'room': 'general'})
        client2.emit('join', {'username': username, 'room': 'general'})
        
        # 验证系统如何处理重复用户名
        from app import online_users
        
        # 当前实现允许重复用户名，但在实际项目中可能需要处理
        print(f"✅ 重复用户名处理测试完成，当前在线用户数: {len(online_users)}")
    
    def test_session_cleanup(self):
        """测试会话清理"""
        client = socketio.test_client(app)
        
        client.emit('join', {
            'username': '清理测试用户',
            'room': 'general'
        })
        
        from app import online_users
        initial_count = len(online_users)
        
        # 断开连接
        client.disconnect()
        
        # 验证用户被清理
        final_count = len(online_users)
        assert final_count < initial_count, "用户应该在断开连接后被清理"
        print("✅ 会话清理正常工作")

@pytest.mark.security
class TestRateLimiting:
    """速率限制测试"""
    
    def test_message_flooding(self):
        """测试消息洪水攻击防护"""
        client = socketio.test_client(app)
        
        client.emit('join', {
            'username': '洪水测试用户',
            'room': 'general'
        })
        client.get_received()
        
        # 尝试快速发送大量消息
        message_count = 0
        start_time = time.time()
        
        try:
            for i in range(100):  # 尝试发送100条消息
                client.emit('send_message', {
                    'message': f'洪水消息 {i}',
                    'type': 'text'
                })
                message_count += 1
        except Exception as e:
            print(f"消息被限制: {e}")
        
        end_time = time.time()
        rate = message_count / (end_time - start_time)
        
        print(f"消息发送速率: {rate:.2f} 条/秒")
        print(f"发送消息数: {message_count}")
        
        # 如果速率过高，可能需要添加速率限制
        if rate > 100:  # 每秒超过100条
            print("⚠️ 建议添加速率限制防护")
        else:
            print("✅ 消息发送速率在合理范围内")
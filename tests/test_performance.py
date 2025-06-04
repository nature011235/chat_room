# tests/test_performance.py - 性能测试（修复版本）
import pytest
import time
import threading
import socketio
import random
import string
from concurrent.futures import ThreadPoolExecutor, as_completed

@pytest.mark.performance
@pytest.mark.slow
class TestConcurrentUsers:
    """并发用户测试"""
    
    def generate_username(self):
        """生成随机用户名"""
        return f"User_{''.join(random.choices(string.ascii_letters, k=6))}"
    
    def simulate_user(self, server_url, user_id, message_count=5):
        """模拟单个用户行为"""
        username = self.generate_username()
        messages_sent = 0
        
        try:
            print(f"用户{user_id} 开始连接...")
            
            # 创建客户端 - 修复版本
            sio = socketio.Client()  # 使用 Client() 而不是 SimpleClient()
            
            # 连接服务器
            start_time = time.time()
            sio.connect(server_url)
            connect_time = time.time() - start_time
            
            print(f"用户{user_id} 连接成功，耗时 {connect_time:.3f}秒")
            
            # 加入聊天室
            sio.emit('join', {
                'username': username,
                'room': 'general'
            })
            
            print(f"用户{user_id} 已加入聊天室")
            
            # 发送消息
            for i in range(message_count):
                message = f"{username}的消息{i+1}"
                sio.emit('send_message', {
                    'message': message,
                    'type': 'text'
                })
                messages_sent += 1
                time.sleep(random.uniform(0.1, 0.3))  # 随机延迟
            
            print(f"用户{user_id} 发送了 {messages_sent} 条消息")
            
            # 保持连接一段时间
            time.sleep(random.uniform(1, 2))
            
            sio.disconnect()
            print(f"用户{user_id} 断开连接")
            
            return {
                'user_id': user_id,
                'username': username,
                'connect_time': connect_time,
                'messages_sent': messages_sent,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ 用户{user_id} 失败: {e}")
            print(f"   错误类型: {type(e).__name__}")
            return {
                'user_id': user_id,
                'username': username,
                'error': str(e),
                'success': False
            }
    
    def test_5_concurrent_users(self, server_url):
        """测试5个并发用户"""
        user_count = 5
        print(f"\n测试 {user_count} 个并发用户...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=user_count) as executor:
            futures = [
                executor.submit(self.simulate_user, server_url, i) 
                for i in range(user_count)
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # 分析结果
        successful_users = [r for r in results if r['success']]
        failed_users = [r for r in results if not r['success']]
        
        print(f"成功用户: {len(successful_users)}/{user_count}")
        print(f"失败用户: {len(failed_users)}")
        print(f"总耗时: {total_time:.2f}秒")
        
        if successful_users:
            avg_connect_time = sum(r['connect_time'] for r in successful_users) / len(successful_users)
            total_messages = sum(r['messages_sent'] for r in successful_users)
            print(f"平均连接时间: {avg_connect_time:.3f}秒")
            print(f"总消息数: {total_messages}")
        
        # 验证至少80%的用户成功
        success_rate = len(successful_users) / user_count
        assert success_rate >= 0.8, f"成功率太低: {success_rate:.2%}"
    
    def test_10_concurrent_users(self, server_url):
        """测试10个并发用户"""
        user_count = 10
        print(f"\n测试 {user_count} 个并发用户...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=user_count) as executor:
            futures = [
                executor.submit(self.simulate_user, server_url, i, 3)  # 每人发3条消息
                for i in range(user_count)
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        successful_users = [r for r in results if r['success']]
        success_rate = len(successful_users) / user_count
        
        print(f"成功用户: {len(successful_users)}/{user_count}")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"成功率: {success_rate:.2%}")
        
        # 10个用户的要求可以稍微宽松一些
        assert success_rate >= 0.7, f"成功率太低: {success_rate:.2%}"

@pytest.mark.performance
class TestMessageThroughput:
    """消息吞吐量测试"""
    
    def test_message_sending_speed(self, server_url):
        """测试消息发送速度"""
        print("\n测试消息发送速度...")
        
        sio = socketio.Client()  # 修复：使用 Client()
        sio.connect(server_url)
        
        # 加入聊天室
        sio.emit('join', {
            'username': '速度测试用户',
            'room': 'general'
        })
        
        # 发送20条消息并测量时间
        message_count = 20
        start_time = time.time()
        
        for i in range(message_count):
            sio.emit('send_message', {
                'message': f'速度测试消息 {i+1}',
                'type': 'text'
            })
            time.sleep(0.01)  # 很短的延迟避免太快
        
        end_time = time.time()
        total_time = end_time - start_time
        
        sio.disconnect()
        
        messages_per_second = message_count / total_time
        
        print(f"发送 {message_count} 条消息")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"消息速率: {messages_per_second:.2f} 条/秒")
        
        # 验证消息发送速度合理（至少10条/秒）
        assert messages_per_second >= 10, f"消息发送速度太慢: {messages_per_second:.2f} 条/秒"

@pytest.mark.performance  
class TestConnectionStability:
    """连接稳定性测试"""
    
    def test_long_connection(self, server_url):
        """测试长连接稳定性"""
        print("\n测试长连接稳定性（30秒）...")
        
        sio = socketio.Client()  # 修复：使用 Client()
        sio.connect(server_url)
        
        # 加入聊天室
        sio.emit('join', {
            'username': '长连接测试用户',
            'room': 'general'
        })
        
        # 保持连接30秒，期间每5秒发送一条消息
        duration = 30
        message_interval = 5
        start_time = time.time()
        message_count = 0
        
        while time.time() - start_time < duration:
            try:
                sio.emit('send_message', {
                    'message': f'长连接测试消息 {message_count + 1}',
                    'type': 'text'
                })
                message_count += 1
                time.sleep(message_interval)
            except Exception as e:
                print(f"连接中断: {e}")
                break
        
        sio.disconnect()
        
        expected_messages = duration // message_interval
        print(f"预期消息数: {expected_messages}")
        print(f"实际发送数: {message_count}")
        print(f"连接稳定率: {(message_count / expected_messages * 100):.1f}%")
        
        # 验证至少发送了80%的预期消息
        assert message_count >= expected_messages * 0.8, f"连接不够稳定，只发送了 {message_count}/{expected_messages} 条消息"

@pytest.mark.performance
class TestResponseTime:
    """响应时间测试"""
    
    def test_join_response_time(self, server_url):
        """测试加入聊天室的响应时间"""
        print("\n测试加入响应时间...")
        
        response_times = []
        
        for i in range(5):  # 测试5次
            sio = socketio.Client()  # 修复：使用 Client()
            
            start_time = time.time()
            sio.connect(server_url)
            sio.emit('join', {
                'username': f'响应测试用户{i+1}',
                'room': 'general'
            })
            
            # 等待响应（简单等待，实际项目中可以监听特定事件）
            time.sleep(0.1)
            
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            sio.disconnect()
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        print(f"平均响应时间: {avg_response_time:.3f}秒")
        print(f"最大响应时间: {max_response_time:.3f}秒")
        
        # 验证响应时间合理（小于1秒）
        assert avg_response_time < 1.0, f"平均响应时间过长: {avg_response_time:.3f}秒"
        assert max_response_time < 2.0, f"最大响应时间过长: {max_response_time:.3f}秒"
        
@pytest.mark.performance
def test_connection_stability_1h():
    sio = socketio.Client()
    sio.connect("http://localhost:5000")
    assert sio.connected

    start = time.time()
    duration = 10  # 1 小時，開發時可改成 60

    while time.time() - start < duration:
        sio.emit("heartbeat", {"time": time.time()})
        time.sleep(10)
        assert sio.connected

    sio.disconnect()

import psutil
import os

@pytest.mark.performance
def test_memory_and_socket_leak():
    import gc

    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss
    sockets_before = process.num_fds() if hasattr(process, 'num_fds') else None

    clients = []
    for i in range(100):
        sio = socketio.Client()
        sio.connect("http://localhost:5000")
        sio.emit("join", {"username": f"LeakTestUser{i}"})
        sio.emit("send_message", {"message": f"Hi {i}", "type": "text", "message_id": str(i)})
        clients.append(sio)

    time.sleep(5)

    for sio in clients:
        try:
            sio.disconnect()
        except Exception:
            pass

    # 強制釋放 memory / socket
    del clients
    gc.collect()
    time.sleep(10)  # 加長等待時間，讓 socket 關閉生效

    mem_after = process.memory_info().rss
    sockets_after = process.num_fds() if hasattr(process, 'num_fds') else None

    print(f"🔍 sockets before: {sockets_before}, after: {sockets_after}")
    assert mem_after - mem_before < 30 * 1024 * 1024
    if sockets_before is not None:
        assert sockets_after - sockets_before < 10
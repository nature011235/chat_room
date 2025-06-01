# test_performance.py - 性能和压力测试
import asyncio
import time
import threading
import requests
import socketio
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import random
import string

class PerformanceTestConfig:
    """性能测试配置"""
    BASE_URL = "http://localhost:5000"
    MAX_CONCURRENT_USERS = 50
    MESSAGE_COUNT_PER_USER = 10
    TEST_DURATION = 60  # 秒

class ChatPerformanceTester:
    """聊天室性能测试器"""
    
    def __init__(self):
        self.results = {
            'connection_times': [],
            'message_send_times': [],
            'total_messages_sent': 0,
            'failed_connections': 0,
            'failed_messages': 0,
            'start_time': 0,
            'end_time': 0
        }
    
    def generate_random_username(self):
        """生成随机用户名"""
        return f"TestUser_{''.join(random.choices(string.ascii_letters + string.digits, k=8))}"
    
    def test_single_user_performance(self, user_id):
        """单个用户性能测试"""
        username = self.generate_random_username()
        messages_sent = 0
        
        try:
            # 创建SocketIO客户端
            sio = socketio.SimpleClient()
            
            # 测量连接时间
            connect_start = time.time()
            sio.connect(PerformanceTestConfig.BASE_URL)
            connect_time = time.time() - connect_start
            
            self.results['connection_times'].append(connect_time)
            
            # 加入聊天室
            sio.emit('join', {
                'username': username,
                'room': 'general'
            })
            
            # 发送消息并测量时间
            for i in range(PerformanceTestConfig.MESSAGE_COUNT_PER_USER):
                message = f"来自{username}的消息{i+1}"
                
                send_start = time.time()
                sio.emit('send_message', {
                    'message': message,
                    'type': 'text'
                })
                send_time = time.time() - send_start
                
                self.results['message_send_times'].append(send_time)
                messages_sent += 1
                
                # 随机延迟，模拟真实用户行为
                time.sleep(random.uniform(0.1, 0.5))
            
            self.results['total_messages_sent'] += messages_sent
            
            # 保持连接一段时间
            time.sleep(random.uniform(1, 3))
            
            sio.disconnect()
            
        except Exception as e:
            print(f"用户 {user_id} 测试失败: {e}")
            self.results['failed_connections'] += 1
    
    def test_concurrent_users(self, num_users=20):
        """并发用户测试"""
        print(f"开始测试 {num_users} 个并发用户...")
        
        self.results['start_time'] = time.time()
        
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [
                executor.submit(self.test_single_user_performance, i) 
                for i in range(num_users)
            ]
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"任务执行失败: {e}")
        
        self.results['end_time'] = time.time()
    
    def test_stress_load(self):
        """压力测试 - 逐步增加负载"""
        print("开始压力测试...")
        
        user_counts = [5, 10, 20, 30, 40, 50]
        stress_results = {}
        
        for user_count in user_counts:
            print(f"测试 {user_count} 个用户...")
            
            # 重置结果
            self.results = {
                'connection_times': [],
                'message_send_times': [],
                'total_messages_sent': 0,
                'failed_connections': 0,
                'failed_messages': 0,
                'start_time': 0,
                'end_time': 0
            }
            
            # 运行测试
            self.test_concurrent_users(user_count)
            
            # 记录结果
            stress_results[user_count] = {
                'avg_connection_time': statistics.mean(self.results['connection_times']) if self.results['connection_times'] else 0,
                'avg_message_time': statistics.mean(self.results['message_send_times']) if self.results['message_send_times'] else 0,
                'total_messages': self.results['total_messages_sent'],
                'failed_connections': self.results['failed_connections'],
                'total_time': self.results['end_time'] - self.results['start_time']
            }
            
            print(f"用户数: {user_count}, 平均连接时间: {stress_results[user_count]['avg_connection_time']:.3f}s")
            print(f"平均消息发送时间: {stress_results[user_count]['avg_message_time']:.3f}s")
            print(f"失败连接数: {stress_results[user_count]['failed_connections']}")
            print("-" * 50)
            
            # 等待服务器恢复
            time.sleep(2)
        
        return stress_results
    
    def test_message_throughput(self):
        """测试消息吞吐量"""
        print("测试消息吞吐量...")
        
        def send_messages_continuously(duration=30):
            """持续发送消息"""
            sio = socketio.SimpleClient()
            messages_sent = 0
            
            try:
                sio.connect(PerformanceTestConfig.BASE_URL)
                sio.emit('join', {
                    'username': f'ThroughputUser_{random.randint(1000, 9999)}',
                    'room': 'general'
                })
                
                end_time = time.time() + duration
                while time.time() < end_time:
                    sio.emit('send_message', {
                        'message': f'Throughput test message {messages_sent}',
                        'type': 'text'
                    })
                    messages_sent += 1
                    time.sleep(0.01)  # 很短的延迟
                
                sio.disconnect()
                
            except Exception as e:
                print(f"吞吐量测试错误: {e}")
            
            return messages_sent
        
        # 使用5个并发客户端测试吞吐量
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(send_messages_continuously, 30) for _ in range(5)]
            total_messages = sum(future.result() for future in as_completed(futures))
        
        throughput = total_messages / 30  # 每秒消息数
        print(f"消息吞吐量: {throughput:.2f} 消息/秒")
        return throughput
    
    def generate_performance_report(self):
        """生成性能测试报告"""
        if not self.results['connection_times']:
            print("没有性能数据可供分析")
            return
        
        report = f"""
=== 聊天室性能测试报告 ===

连接性能:
- 平均连接时间: {statistics.mean(self.results['connection_times']):.3f}s
- 最快连接时间: {min(self.results['connection_times']):.3f}s
- 最慢连接时间: {max(self.results['connection_times']):.3f}s
- 连接时间标准差: {statistics.stdev(self.results['connection_times']):.3f}s

消息发送性能:
- 平均发送时间: {statistics.mean(self.results['message_send_times']):.3f}s
- 最快发送时间: {min(self.results['message_send_times']):.3f}s
- 最慢发送时间: {max(self.results['message_send_times']):.3f}s
- 发送时间标准差: {statistics.stdev(self.results['message_send_times']):.3f}s

总体统计:
- 总消息发送数: {self.results['total_messages_sent']}
- 失败连接数: {self.results['failed_connections']}
- 测试总时长: {self.results['end_time'] - self.results['start_time']:.2f}s
- 消息发送成功率: {(1 - self.results['failed_messages'] / max(1, self.results['total_messages_sent'])) * 100:.2f}%
        """
        
        print(report)
        return report

class MemoryUsageMonitor:
    """内存使用监控"""
    
    def __init__(self):
        self.monitoring = False
        self.memory_samples = []
    
    def start_monitoring(self):
        """开始监控内存使用"""
        self.monitoring = True
        self.memory_samples = []
        
        def monitor():
            while self.monitoring:
                try:
                    # 发送请求获取服务器状态（如果有提供的话）
                    response = requests.get(f"{PerformanceTestConfig.BASE_URL}/health", timeout=1)
                    if response.status_code == 200:
                        data = response.json()
                        if 'memory_usage' in data:
                            self.memory_samples.append(data['memory_usage'])
                except:
                    pass
                
                time.sleep(1)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
    
    def get_memory_report(self):
        """获取内存使用报告"""
        if not self.memory_samples:
            return "没有内存使用数据"
        
        return f"""
内存使用报告:
- 平均内存使用: {statistics.mean(self.memory_samples):.2f}MB
- 最高内存使用: {max(self.memory_samples):.2f}MB
- 最低内存使用: {min(self.memory_samples):.2f}MB
        """

def run_all_performance_tests():
    """运行所有性能测试"""
    tester = ChatPerformanceTester()
    
    print("=== 聊天室性能测试套件 ===\n")
    
    # 1. 基础并发测试
    print("1. 基础并发测试 (20个用户)")
    tester.test_concurrent_users(20)
    tester.generate_performance_report()
    
    print("\n" + "="*60 + "\n")
    
    # 2. 压力测试
    print("2. 压力测试")
    stress_results = tester.test_stress_load()
    
    print("\n压力测试总结:")
    for users, data in stress_results.items():
        print(f"用户数: {users:2d} | 连接时间: {data['avg_connection_time']:.3f}s | "
              f"消息时间: {data['avg_message_time']:.3f}s | 失败: {data['failed_connections']}")
    
    print("\n" + "="*60 + "\n")
    
    # 3. 吞吐量测试
    print("3. 消息吞吐量测试")
    throughput = tester.test_message_throughput()
    
    print("\n" + "="*60 + "\n")
    
    # 4. 单连接稳定性测试
    print("4. 长连接稳定性测试")
    test_long_connection()

def test_long_connection():
    """测试长连接稳定性"""
    print("测试长连接稳定性 (60秒)...")
    
    sio = socketio.SimpleClient()
    messages_received = 0
    
    def on_message(data):
        nonlocal messages_received
        messages_received += 1
    
    try:
        sio.connect(PerformanceTestConfig.BASE_URL)
        sio.emit('join', {
            'username': 'LongConnectionTest',
            'room': 'general'
        })
        
        # 每10秒发送一条消息
        start_time = time.time()
        message_count = 0
        
        while time.time() - start_time < 60:
            sio.emit('send_message', {
                'message': f'长连接测试消息 {message_count}',
                'type': 'text'
            })
            message_count += 1
            time.sleep(10)
        
        sio.disconnect()
        
        print(f"长连接测试完成:")
        print(f"- 发送消息数: {message_count}")
        print(f"- 连接持续时间: 60秒")
        print(f"- 连接稳定性: {'稳定' if message_count >= 6 else '不稳定'}")
        
    except Exception as e:
        print(f"长连接测试失败: {e}")

if __name__ == '__main__':
    # 确保服务器正在运行
    try:
        response = requests.get(PerformanceTestConfig.BASE_URL, timeout=5)
        print("服务器连接正常，开始性能测试...")
        run_all_performance_tests()
    except requests.ConnectionError:
        print("错误: 无法连接到服务器，请确保聊天室应用正在 http://localhost:5000 运行")
    except Exception as e:
        print(f"测试初始化失败: {e}")
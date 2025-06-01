# test_utils.py - 测试工具和辅助函数
import time
import random
import string
import json
import os
from datetime import datetime
from pathlib import Path
import requests
import subprocess
import signal
import psutil

class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def random_username(length=8):
        """生成随机用户名"""
        return f"User_{''.join(random.choices(string.ascii_letters + string.digits, k=length))}"
    
    @staticmethod
    def random_message(length=50):
        """生成随机消息"""
        words = ["hello", "world", "test", "message", "chat", "room", "user", "socket", "real", "time"]
        return " ".join(random.choices(words, k=length//6))
    
    @staticmethod
    def create_test_image_base64():
        """创建测试用的base64图片"""
        # 1x1像素的透明PNG
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    @staticmethod
    def create_large_test_image(size_mb=50):
        """创建大型测试图片"""
        data_size = size_mb * 1024 * 1024
        large_data = "A" * data_size
        return f"data:image/jpeg;base64,{large_data}"
    
    @staticmethod
    def xss_payloads():
        """XSS攻击载荷列表"""
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<%2Fscript%3E%3Cscript%3Ealert('XSS')%3C%2Fscript%3E",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<object data='javascript:alert(\"XSS\")'></object>",
            "<embed src='javascript:alert(\"XSS\")'></embed>",
            "<link rel='stylesheet' href='javascript:alert(\"XSS\")'>"
        ]
    
    @staticmethod
    def sql_injection_payloads():
        """SQL注入攻击载荷列表"""
        return [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--", 
            "' UNION SELECT * FROM users--",
            "'; UPDATE users SET password='hacked'--",
            "1' AND 1=1 UNION SELECT 1,2,3,4,5--",
            "' OR 'a'='a",
            "1; EXEC xp_cmdshell('dir')--"
        ]

class ServerManager:
    """服务器管理工具"""
    
    def __init__(self, host="localhost", port=5000):
        self.host = host
        self.port = port
        self.process = None
        self.url = f"http://{host}:{port}"
    
    def start_server(self, app_file="app.py"):
        """启动服务器"""
        print(f"启动服务器: {app_file}")
        
        self.process = subprocess.Popen(
            ["python", app_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        # 等待服务器启动
        for attempt in range(30):  # 30秒超时
            try:
                response = requests.get(self.url, timeout=1)
                if response.status_code == 200:
                    print(f"✅ 服务器启动成功: {self.url}")
                    return True
            except requests.ConnectionError:
                time.sleep(1)
        
        print("❌ 服务器启动失败")
        self.stop_server()
        return False
    
    def stop_server(self):
        """停止服务器"""
        if self.process:
            print("停止服务器...")
            try:
                if os.name == 'nt':  # Windows
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                else:  # Unix/Linux
                    self.process.terminate()
                
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            
            self.process = None
            print("✅ 服务器已停止")
    
    def is_running(self):
        """检查服务器是否运行"""
        try:
            response = requests.get(self.url, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def restart_server(self, app_file="app.py"):
        """重启服务器"""
        self.stop_server()
        time.sleep(2)
        return self.start_server(app_file)

class TestReporter:
    """测试报告生成器"""
    
    def __init__(self):
        self.results = {
            'start_time': datetime.now(),
            'end_time': None,
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'errors': 0
            },
            'performance': {},
            'coverage': {}
        }
    
    def add_test_result(self, test_name, status, duration=0, error_msg=None):
        """添加测试结果"""
        self.results['tests'].append({
            'name': test_name,
            'status': status,  # 'passed', 'failed', 'skipped', 'error'
            'duration': duration,
            'error': error_msg,
            'timestamp': datetime.now()
        })
        
        self.results['summary']['total'] += 1
        self.results['summary'][status] += 1
    
    def add_performance_data(self, test_name, metrics):
        """添加性能测试数据"""
        self.results['performance'][test_name] = metrics
    
    def finalize(self):
        """完成测试报告"""
        self.results['end_time'] = datetime.now()
    
    def generate_html_report(self, filename="test_report.html"):
        """生成HTML报告"""
        total_duration = (self.results['end_time'] - self.results['start_time']).total_seconds()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>聊天室测试报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
        .summary-card h3 {{ color: #666; margin-bottom: 10px; }}
        .summary-card .number {{ font-size: 2em; font-weight: bold; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .skipped {{ color: #ffc107; }}
        .section {{ background: white; margin-bottom: 20px; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .section h2 {{ color: #444; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #eee; }}
        .test-list {{ overflow-x: auto; }}
        .test-table {{ width: 100%; border-collapse: collapse; }}
        .test-table th, .test-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        .test-table th {{ background: #f8f9fa; font-weight: 600; }}
        .status-badge {{ padding: 4px 8px; border-radius: 4px; color: white; font-size: 0.9em; }}
        .status-passed {{ background: #28a745; }}
        .status-failed {{ background: #dc3545; }}
        .status-skipped {{ background: #ffc107; }}
        .performance-chart {{ height: 200px; background: #f8f9fa; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #666; }}
        .footer {{ text-align: center; color: #666; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 聊天室测试报告</h1>
            <p>生成时间: {self.results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>测试耗时: {total_duration:.2f} 秒</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>总测试数</h3>
                <div class="number">{self.results['summary']['total']}</div>
            </div>
            <div class="summary-card">
                <h3>通过</h3>
                <div class="number passed">{self.results['summary']['passed']}</div>
            </div>
            <div class="summary-card">
                <h3>失败</h3>
                <div class="number failed">{self.results['summary']['failed']}</div>
            </div>
            <div class="summary-card">
                <h3>跳过</h3>
                <div class="number skipped">{self.results['summary']['skipped']}</div>
            </div>
            <div class="summary-card">
                <h3>成功率</h3>
                <div class="number passed">{(self.results['summary']['passed'] / max(1, self.results['summary']['total']) * 100):.1f}%</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 测试详情</h2>
            <div class="test-list">
                <table class="test-table">
                    <thead>
                        <tr>
                            <th>测试名称</th>
                            <th>状态</th>
                            <th>耗时(秒)</th>
                            <th>错误信息</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for test in self.results['tests']:
            status_class = f"status-{test['status']}"
            error_msg = test['error'][:100] + "..." if test['error'] and len(test['error']) > 100 else (test['error'] or "")
            
            html_content += f"""
                        <tr>
                            <td>{test['name']}</td>
                            <td><span class="status-badge {status_class}">{test['status'].upper()}</span></td>
                            <td>{test['duration']:.3f}</td>
                            <td>{error_msg}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="section">
            <h2>⚡ 性能指标</h2>
            <div class="performance-chart">
                性能数据图表 (可集成Chart.js显示详细图表)
            </div>
        </div>
        
        <div class="footer">
            <p>报告由聊天室测试套件自动生成</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📊 HTML报告已生成: {filename}")
        return filename

class PerformanceMonitor:
    """性能监控工具"""
    
    def __init__(self):
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'network_io': [],
            'response_times': [],
            'concurrent_users': 0
        }
        self.monitoring = False
    
    def start_monitoring(self):
        """开始监控"""
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    # CPU使用率
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.metrics['cpu_usage'].append(cpu_percent)
                    
                    # 内存使用率
                    memory = psutil.virtual_memory()
                    self.metrics['memory_usage'].append(memory.percent)
                    
                    # 网络IO
                    net_io = psutil.net_io_counters()
                    self.metrics['network_io'].append({
                        'bytes_sent': net_io.bytes_sent,
                        'bytes_recv': net_io.bytes_recv
                    })
                    
                except Exception as e:
                    print(f"监控错误: {e}")
                
                time.sleep(1)
        
        import threading
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
    
    def get_summary(self):
        """获取监控摘要"""
        if not self.metrics['cpu_usage']:
            return "没有监控数据"
        
        return {
            'avg_cpu': sum(self.metrics['cpu_usage']) / len(self.metrics['cpu_usage']),
            'max_cpu': max(self.metrics['cpu_usage']),
            'avg_memory': sum(self.metrics['memory_usage']) / len(self.metrics['memory_usage']),
            'max_memory': max(self.metrics['memory_usage']),
            'sample_count': len(self.metrics['cpu_usage'])
        }

class DatabaseHelper:
    """数据库测试辅助工具（如果项目使用数据库）"""
    
    def __init__(self, db_url=None):
        self.db_url = db_url or "sqlite:///test.db"
    
    def setup_test_db(self):
        """设置测试数据库"""
        # 这里可以添加数据库初始化代码
        pass
    
    def cleanup_test_db(self):
        """清理测试数据库"""
        # 这里可以添加数据库清理代码
        pass
    
    def create_test_data(self):
        """创建测试数据"""
        pass

class LogAnalyzer:
    """日志分析工具"""
    
    def __init__(self, log_file="app.log"):
        self.log_file = log_file
    
    def analyze_errors(self):
        """分析错误日志"""
        if not os.path.exists(self.log_file):
            return []
        
        errors = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if 'ERROR' in line or 'Exception' in line:
                    errors.append({
                        'line': line_num,
                        'content': line.strip(),
                        'timestamp': self.extract_timestamp(line)
                    })
        
        return errors
    
    def extract_timestamp(self, log_line):
        """提取日志时间戳"""
        # 简单的时间戳提取，可根据实际日志格式调整
        import re
        pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        match = re.search(pattern, log_line)
        return match.group() if match else None
    
    def get_performance_logs(self):
        """获取性能相关日志"""
        if not os.path.exists(self.log_file):
            return []
        
        performance_logs = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if any(keyword in line.lower() for keyword in ['slow', 'timeout', 'latency', 'performance']):
                    performance_logs.append(line.strip())
        
        return performance_logs

# 全局工具实例
test_data_gen = TestDataGenerator()
server_manager = ServerManager()
performance_monitor = PerformanceMonitor()

# 便捷函数
def quick_start_server():
    """快速启动服务器"""
    return server_manager.start_server()

def quick_stop_server():
    """快速停止服务器"""
    server_manager.stop_server()

def generate_test_users(count=5):
    """生成测试用户数据"""
    return [test_data_gen.random_username() for _ in range(count)]

def create_test_messages(count=10):
    """创建测试消息"""
    return [test_data_gen.random_message() for _ in range(count)]

if __name__ == '__main__':
    # 测试工具函数
    print("🧪 测试工具演示")
    
    print(f"随机用户名: {test_data_gen.random_username()}")
    print(f"随机消息: {test_data_gen.random_message()}")
    print(f"测试图片长度: {len(test_data_gen.create_test_image_base64())}")
    
    # 服务器管理演示
    if server_manager.start_server():
        print("服务器启动成功")
        time.sleep(2)
        print(f"服务器状态: {'运行中' if server_manager.is_running() else '已停止'}")
        server_manager.stop_server()
    
    print("✅ 工具测试完成")
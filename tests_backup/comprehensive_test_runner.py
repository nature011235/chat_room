# comprehensive_test_runner.py - 完整的测试运行器
#!/usr/bin/env python3
"""
聊天室项目完整测试运行器

这个脚本提供了一个完整的测试执行环境，包括：
- 自动服务器管理
- 多种测试模式
- 详细的报告生成
- 性能监控
- 错误处理和恢复

使用方法:
    python comprehensive_test_runner.py                    # 交互式模式
    python comprehensive_test_runner.py --quick           # 快速测试
    python comprehensive_test_runner.py --full            # 完整测试
    python comprehensive_test_runner.py --performance     # 性能测试
    python comprehensive_test_runner.py --security        # 安全测试
    python comprehensive_test_runner.py --ci              # CI模式
"""

import argparse
import sys
import os
import time
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import signal
import atexit

# 导入我们的测试工具
from test_utils import ServerManager, TestReporter, PerformanceMonitor, LogAnalyzer

class ComprehensiveTestRunner:
    """综合测试运行器"""
    
    def __init__(self):
        self.server_manager = ServerManager()
        self.reporter = TestReporter()
        self.performance_monitor = PerformanceMonitor()
        self.log_analyzer = LogAnalyzer()
        
        self.test_results = {}
        self.start_time = datetime.now()
        
        # 注册清理函数
        atexit.register(self.cleanup)
    
    def cleanup(self):
        """清理资源"""
        print("\n🧹 正在清理测试环境...")
        self.server_manager.stop_server()
        self.performance_monitor.stop_monitoring()
    
    def check_dependencies(self):
        """检查测试依赖"""
        print("🔍 检查测试依赖...")
        
        required_packages = [
            'pytest', 'selenium', 'requests', 
            'flask', 'flask-socketio', 'python-socketio'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package}")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n❌ 缺少依赖包: {', '.join(missing_packages)}")
            print("请运行: pip install " + " ".join(missing_packages))
            return False
        
        # 检查ChromeDriver
        try:
            result = subprocess.run(['chromedriver', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("  ✅ ChromeDriver")
            else:
                print("  ❌ ChromeDriver")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("  ❌ ChromeDriver (未找到或超时)")
            print("请安装ChromeDriver或运行: pip install webdriver-manager")
            return False
        
        print("✅ 所有依赖检查通过\n")
        return True
    
    def run_unit_tests(self):
        """运行单元测试"""
        print("🧪 运行单元测试...")
        
        start_time = time.time()
        result = subprocess.run([
            'python', '-m', 'pytest', 'test_chat_app.py', 
            '-v', '--tb=short', '--json-report', '--json-report-file=unit_results.json'
        ], capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        success = result.returncode == 0
        self.test_results['unit_tests'] = {
            'success': success,
            'duration': duration,
            'output': result.stdout,
            'errors': result.stderr
        }
        
        print(f"  {'✅' if success else '❌'} 单元测试完成 ({duration:.2f}s)")
        return success
    
    def run_ui_tests(self):
        """运行UI测试"""
        print("🖥️  运行UI测试...")
        
        start_time = time.time()
        result = subprocess.run([
            'python', '-m', 'pytest', 'test_selenium_ui.py',
            '-v', '--tb=short', '--json-report', '--json-report-file=ui_results.json'
        ], capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        success = result.returncode == 0
        self.test_results['ui_tests'] = {
            'success': success,
            'duration': duration,
            'output': result.stdout,
            'errors': result.stderr
        }
        
        print(f"  {'✅' if success else '❌'} UI测试完成 ({duration:.2f}s)")
        return success
    
    def run_performance_tests(self):
        """运行性能测试"""
        print("⚡ 运行性能测试...")
        
        # 启动性能监控
        self.performance_monitor.start_monitoring()
        
        start_time = time.time()
        result = subprocess.run([
            'python', '-m', 'pytest', 'test_performance.py',
            '-v', '--tb=short', '-s'
        ], capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        # 停止性能监控
        self.performance_monitor.stop_monitoring()
        performance_summary = self.performance_monitor.get_summary()
        
        success = result.returncode == 0
        self.test_results['performance_tests'] = {
            'success': success,
            'duration': duration,
            'output': result.stdout,
            'errors': result.stderr,
            'performance_summary': performance_summary
        }
        
        print(f"  {'✅' if success else '❌'} 性能测试完成 ({duration:.2f}s)")
        if performance_summary and isinstance(performance_summary, dict):
            print(f"  📊 平均CPU使用率: {performance_summary.get('avg_cpu', 0):.1f}%")
            print(f"  📊 平均内存使用率: {performance_summary.get('avg_memory', 0):.1f}%")
        
        return success
    
    def run_security_tests(self):
        """运行安全测试"""
        print("🔒 运行安全测试...")
        
        start_time = time.time()
        result = subprocess.run([
            'python', '-m', 'pytest', 'test_security.py',
            '-v', '--tb=short'
        ], capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        success = result.returncode == 0
        self.test_results['security_tests'] = {
            'success': success,
            'duration': duration,
            'output': result.stdout,
            'errors': result.stderr
        }
        
        print(f"  {'✅' if success else '❌'} 安全测试完成 ({duration:.2f}s)")
        return success
    
    def run_coverage_analysis(self):
        """运行代码覆盖率分析"""
        print("📊 运行代码覆盖率分析...")
        
        start_time = time.time()
        result = subprocess.run([
            'python', '-m', 'pytest', 'test_chat_app.py',
            '--cov=app', '--cov-report=html', '--cov-report=term', '--cov-report=json'
        ], capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        success = result.returncode == 0
        self.test_results['coverage_analysis'] = {
            'success': success,
            'duration': duration,
            'output': result.stdout,
            'errors': result.stderr
        }
        
        print(f"  {'✅' if success else '❌'} 覆盖率分析完成 ({duration:.2f}s)")
        
        # 尝试解析覆盖率数据
        try:
            if os.path.exists('coverage.json'):
                with open('coverage.json', 'r') as f:
                    coverage_data = json.load(f)
                    total_coverage = coverage_data['totals']['percent_covered']
                    print(f"  📈 总代码覆盖率: {total_coverage:.1f}%")
        except Exception as e:
            print(f"  ⚠️ 无法解析覆盖率数据: {e}")
        
        return success
    
    def generate_comprehensive_report(self):
        """生成综合测试报告"""
        print("📋 生成综合测试报告...")
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        # 计算总体统计
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result['success'])
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_duration': total_duration,
            'summary': {
                'total_test_suites': total_tests,
                'successful_suites': successful_tests,
                'failed_suites': total_tests - successful_tests,
                'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'detailed_results': self.test_results,
            'environment': {
                'python_version': sys.version,
                'platform': sys.platform,
                'cwd': os.getcwd()
            }
        }
        
        # 生成JSON报告
        with open('comprehensive_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        # 生成HTML报告
        self.generate_html_report(report_data)
        
        print("✅ 报告生成完成")
        print(f"  📄 JSON报告: comprehensive_test_report.json")
        print(f"  🌐 HTML报告: comprehensive_test_report.html")
        
        return report_data
    
    def generate_html_report(self, report_data):
        """生成HTML格式的报告"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>聊天室综合测试报告</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; color: #2c3e50; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; padding: 40px; border-radius: 15px; margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header h1 { font-size: 3em; margin-bottom: 10px; font-weight: 300; }
        .header .subtitle { font-size: 1.2em; opacity: 0.9; }
        
        .summary-grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; margin-bottom: 30px; 
        }
        .summary-card { 
            background: white; padding: 30px; border-radius: 10px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.08); text-align: center;
            transition: transform 0.2s ease;
        }
        .summary-card:hover { transform: translateY(-5px); }
        .summary-card h3 { color: #7f8c8d; margin-bottom: 15px; font-size: 1.1em; }
        .summary-card .metric { font-size: 2.5em; font-weight: bold; line-height: 1; }
        .metric.success { color: #27ae60; }
        .metric.warning { color: #f39c12; }
        .metric.danger { color: #e74c3c; }
        
        .section { 
            background: white; margin-bottom: 20px; border-radius: 10px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.08); overflow: hidden;
        }
        .section-header { 
            background: #34495e; color: white; padding: 20px; 
            font-size: 1.3em; font-weight: 500;
        }
        .section-content { padding: 25px; }
        
        .test-result { 
            display: flex; justify-content: space-between; align-items: center;
            padding: 15px; margin-bottom: 10px; border-radius: 8px;
            background: #f8f9fa; border-left: 4px solid #bdc3c7;
        }
        .test-result.success { border-left-color: #27ae60; background: #d5f4e6; }
        .test-result.failure { border-left-color: #e74c3c; background: #ffeaa7; }
        .test-name { font-weight: 500; font-size: 1.1em; }
        .test-stats { display: flex; gap: 20px; font-size: 0.9em; color: #7f8c8d; }
        
        .code-block { 
            background: #2c3e50; color: #ecf0f1; padding: 20px; 
            border-radius: 5px; font-family: 'Courier New', monospace;
            font-size: 0.9em; line-height: 1.4; overflow-x: auto;
        }
        
        .footer { 
            text-align: center; margin-top: 40px; padding: 20px;
            color: #7f8c8d; border-top: 1px solid #ecf0f1;
        }
        
        .progress-bar { 
            background: #ecf0f1; height: 20px; border-radius: 10px; 
            overflow: hidden; margin: 10px 0;
        }
        .progress-fill { 
            height: 100%; background: linear-gradient(45deg, #27ae60, #2ecc71);
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 聊天室综合测试报告</h1>
            <div class="subtitle">
                生成时间: {timestamp}<br>
                总耗时: {total_duration:.2f} 秒
            </div>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>测试套件总数</h3>
                <div class="metric">{total_suites}</div>
            </div>
            <div class="summary-card">
                <h3>成功套件</h3>
                <div class="metric success">{successful_suites}</div>
            </div>
            <div class="summary-card">
                <h3>失败套件</h3>
                <div class="metric danger">{failed_suites}</div>
            </div>
            <div class="summary-card">
                <h3>成功率</h3>
                <div class="metric {'success' if report_data['summary']['success_rate'] >= 80 else 'warning' if report_data['summary']['success_rate'] >= 60 else 'danger'}">{success_rate:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {success_rate}%"></div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">📊 详细测试结果</div>
            <div class="section-content">
        """.format(
            timestamp=report_data['timestamp'],
            total_duration=report_data['total_duration'],
            total_suites=report_data['summary']['total_test_suites'],
            successful_suites=report_data['summary']['successful_suites'],
            failed_suites=report_data['summary']['failed_suites'],
            success_rate=report_data['summary']['success_rate']
        )
        
        # 添加测试结果详情
        for test_name, result in report_data['detailed_results'].items():
            status_class = 'success' if result['success'] else 'failure'
            status_icon = '✅' if result['success'] else '❌'
            
            html_template += f"""
                <div class="test-result {status_class}">
                    <div class="test-name">{status_icon} {test_name.replace('_', ' ').title()}</div>
                    <div class="test-stats">
                        <span>耗时: {result['duration']:.2f}s</span>
                        <span>状态: {'通过' if result['success'] else '失败'}</span>
                    </div>
                </div>
            """
        
        html_template += """
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">🔧 环境信息</div>
            <div class="section-content">
                <div class="code-block">
Python版本: """ + report_data['environment']['python_version'] + """<br>
运行平台: """ + report_data['environment']['platform'] + """<br>
工作目录: """ + report_data['environment']['cwd'] + """
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>报告由聊天室综合测试套件生成 | 祝测试愉快！ 🎉</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open('comprehensive_test_report.html', 'w', encoding='utf-8') as f:
            f.write(html_template)
    
    def interactive_mode(self):
        """交互式测试模式"""
        print("🎯 聊天室测试套件 - 交互式模式")
        print("=" * 50)
        
        while True:
            print("\n可选操作:")
            print("1. 运行快速测试 (单元测试)")
            print("2. 运行完整测试 (所有测试)")
            print("3. 运行性能测试")
            print("4. 运行安全测试")
            print("5. 代码覆盖率分析")
            print("6. 查看日志分析")
            print("7. 生成测试报告")
            print("0. 退出")
            
            try:
                choice = input("\n请选择操作 (0-7): ").strip()
                
                if choice == '0':
                    print("👋 再见!")
                    break
                elif choice == '1':
                    self.run_quick_test()
                elif choice == '2':
                    self.run_full_test()
                elif choice == '3':
                    if self.server_manager.start_server():
                        self.run_performance_tests()
                        self.server_manager.stop_server()
                elif choice == '4':
                    if self.server_manager.start_server():
                        self.run_security_tests()
                        self.server_manager.stop_server()
                elif choice == '5':
                    if self.server_manager.start_server():
                        self.run_coverage_analysis()
                        self.server_manager.stop_server()
                elif choice == '6':
                    self.show_log_analysis()
                elif choice == '7':
                    self.generate_comprehensive_report()
                else:
                    print("❌ 无效选择，请重试")
                    
            except KeyboardInterrupt:
                print("\n\n👋 测试被中断，再见!")
                break
            except Exception as e:
                print(f"❌ 操作出错: {e}")
    
    def run_quick_test(self):
        """快速测试模式"""
        print("🚀 快速测试模式")
        
        if not self.server_manager.start_server():
            print("❌ 服务器启动失败，无法运行测试")
            return False
        
        success = True
        try:
            success &= self.run_unit_tests()
        finally:
            self.server_manager.stop_server()
        
        print(f"\n{'✅ 快速测试完成' if success else '❌ 快速测试失败'}")
        return success
    
    def run_full_test(self):
        """完整测试模式"""
        print("🎯 完整测试模式")
        
        if not self.server_manager.start_server():
            print("❌ 服务器启动失败，无法运行测试")
            return False
        
        success = True
        try:
            success &= self.run_unit_tests()
            success &= self.run_ui_tests()
            success &= self.run_performance_tests()
            success &= self.run_security_tests()
            success &= self.run_coverage_analysis()
            
            # 生成综合报告
            self.generate_comprehensive_report()
            
        finally:
            self.server_manager.stop_server()
        
        print(f"\n{'🎉 完整测试成功完成!' if success else '❌ 部分测试失败，请查看报告'}")
        return success
    
    def show_log_analysis(self):
        """显示日志分析"""
        print("📋 日志分析结果:")
        
        errors = self.log_analyzer.analyze_errors()
        if errors:
            print(f"发现 {len(errors)} 个错误:")
            for error in errors[:5]:  # 只显示前5个
                print(f"  行 {error['line']}: {error['content'][:100]}...")
        else:
            print("✅ 没有发现错误日志")
        
        perf_logs = self.log_analyzer.get_performance_logs()
        if perf_logs:
            print(f"\n发现 {len(perf_logs)} 条性能相关日志:")
            for log in perf_logs[:3]:  # 只显示前3个
                print(f"  {log[:100]}...")
        else:
            print("✅ 没有发现性能问题日志")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='聊天室综合测试运行器')
    parser.add_argument('--quick', action='store_true', help='快速测试模式')
    parser.add_argument('--full', action='store_true', help='完整测试模式')
    parser.add_argument('--performance', action='store_true', help='性能测试模式')
    parser.add_argument('--security', action='store_true', help='安全测试模式')
    parser.add_argument('--coverage', action='store_true', help='代码覆盖率分析')
    parser.add_argument('--ci', action='store_true', help='CI模式（自动化，无交互）')
    parser.add_argument('--report-only', action='store_true', help='只生成报告')
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner()
    
    # 检查依赖
    if not runner.check_dependencies():
        sys.exit(1)
    
    success = True
    
    try:
        if args.report_only:
            runner.generate_comprehensive_report()
        elif args.quick:
            success = runner.run_quick_test()
        elif args.full or args.ci:
            success = runner.run_full_test()
        elif args.performance:
            if runner.server_manager.start_server():
                success = runner.run_performance_tests()
                runner.server_manager.stop_server()
        elif args.security:
            if runner.server_manager.start_server():
                success = runner.run_security_tests()
                runner.server_manager.stop_server()
        elif args.coverage:
            if runner.server_manager.start_server():
                success = runner.run_coverage_analysis()
                runner.server_manager.stop_server()
        else:
            # 交互式模式
            runner.interactive_mode()
            return
        
        # CI模式下根据结果设置退出码
        if args.ci and not success:
            print("❌ CI模式: 测试失败")
            sys.exit(1)
        elif args.ci:
            print("✅ CI模式: 所有测试通过")
            
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"❌ 测试运行器出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
# tests/run_all_tests.py - 一键运行所有测试
#!/usr/bin/env python3
"""
聊天室测试一键运行脚本

使用方法:
    python tests/run_all_tests.py              # 运行所有测试
    python tests/run_all_tests.py --quick      # 快速测试（跳过慢速测试）
    python tests/run_all_tests.py --ui         # 只运行UI测试
    python tests/run_all_tests.py --backend    # 只运行后端测试
    python tests/run_all_tests.py --performance # 只运行性能测试
    python tests/run_all_tests.py --security   # 只运行安全测试
    python tests/run_all_tests.py --coverage   # 生成覆盖率报告
"""

import os
import sys
import subprocess
import time
import requests
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_server():
    """检查服务器是否运行"""
    try:
        response = requests.get("http://localhost:5000", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_dependencies():
    """检查测试依赖"""
    required_packages = ['pytest', 'selenium', 'requests', 'flask', 'flask_socketio']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ 缺少依赖: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return False
    
    return True

def run_command(command, description=""):
    """运行命令并显示结果"""
    print(f"\n{'🧪 ' + description if description else ''}")
    print(f"执行: {command}")
    print("-" * 50)
    
    result = subprocess.run(command, shell=True)
    
    if result.returncode == 0:
        print(f"✅ {description} 成功")
    else:
        print(f"❌ {description} 失败")
    
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description='聊天室测试运行器')
    parser.add_argument('--quick', action='store_true', help='快速测试（跳过慢速测试）')
    parser.add_argument('--backend', action='store_true', help='只运行后端测试')
    parser.add_argument('--ui', action='store_true', help='只运行UI测试')
    parser.add_argument('--performance', action='store_true', help='只运行性能测试')
    parser.add_argument('--security', action='store_true', help='只运行安全测试')
    parser.add_argument('--coverage', action='store_true', help='生成覆盖率报告')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    print("🚀 聊天室测试套件")
    print("=" * 50)
    
    # 检查依赖
    print("🔍 检查依赖...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ 依赖检查通过")
    
    # 检查服务器
    print("\n🌐 检查服务器...")
    if not check_server():
        print("❌ 服务器未运行!")
        print("请先启动服务器: python app.py")
        print("然后在新终端运行测试")
        sys.exit(1)
    print("✅ 服务器运行正常")
    
    # 根据参数选择测试
    success = True
    
    if args.backend:
        success &= run_command("python -m pytest tests/test_backend.py -v", "后端测试")
    
    elif args.ui:
        success &= run_command("python -m pytest tests/test_frontend.py -v -m ui", "UI测试")
    
    elif args.performance:
        success &= run_command("python -m pytest tests/test_performance.py -v -m performance", "性能测试")
    
    elif args.security:
        success &= run_command("python -m pytest tests/test_security.py -v -m security", "安全测试")
    
    elif args.quick:
        # 快速测试：跳过慢速测试
        success &= run_command("python -m pytest tests/ -v -m 'not slow'", "快速测试")
    
    elif args.coverage:
        # 覆盖率测试
        success &= run_command(
            "python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term",
            "覆盖率测试"
        )
        
        if success:
            print("\n📊 覆盖率报告已生成:")
            print("  - 终端报告: 已显示")
            print("  - HTML报告: htmlcov/index.html")
    
    else:
        # 运行所有测试
        print("\n🎯 运行完整测试套件...")
        
        # 1. 后端测试
        success &= run_command("python -m pytest tests/test_backend.py -v", "后端测试")
        
        # 2. 前端测试  
        success &= run_command("python -m pytest tests/test_frontend.py -v", "前端UI测试")
        
        # 3. 性能测试
        success &= run_command("python -m pytest tests/test_performance.py -v", "性能测试")
        
        # 4. 安全测试
        success &= run_command("python -m pytest tests/test_security.py -v", "安全测试")
    
    # 总结
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试完成!")
        print("\n📋 测试报告:")
        print("  - 查看详细输出了解测试结果")
        print("  - 如需HTML报告，请使用 --coverage 参数")
        
        print("\n💡 下一步建议:")
        print("  - 检查任何失败的测试")
        print("  - 查看覆盖率报告")
        print("  - 根据测试结果优化代码")
    else:
        print("❌ 部分测试失败")
        print("\n🔧 排查建议:")
        print("  - 检查服务器是否正常运行")
        print("  - 查看错误信息定位问题")
        print("  - 确保Chrome浏览器已安装（UI测试需要）")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试运行器出错: {e}")
        sys.exit(1)
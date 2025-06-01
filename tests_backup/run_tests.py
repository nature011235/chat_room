import argparse
import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并处理结果"""
    print(f"\n{'='*60}")
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    print('='*60)
    
    result = subprocess.run(command, shell=True)
    
    if result.returncode != 0:
        print(f"\n❌ {description} 失败!")
        return False
    else:
        print(f"\n✅ {description} 成功!")
        return True

def main():
    parser = argparse.ArgumentParser(description='聊天室测试运行器')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--unit', action='store_true', help='运行单元测试')
    parser.add_argument('--ui', action='store_true', help='运行UI测试')
    parser.add_argument('--performance', action='store_true', help='运行性能测试')
    parser.add_argument('--coverage', action='store_true', help='生成覆盖率报告')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 检查是否安装了依赖
    print("检查测试依赖...")
    dependencies = ['pytest', 'selenium', 'python-socketio', 'coverage']
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            print(f"❌ 缺少依赖: {dep}")
            print(f"请运行: pip install {dep}")
            sys.exit(1)
    
    print("✅ 所有依赖检查通过")
    
    # 基础pytest命令
    base_cmd = "python -m pytest"
    if args.verbose:
        base_cmd += " -v"
    
    success = True
    
    if args.all or (not any([args.unit, args.ui, args.performance])):
        # 运行所有测试
        if args.coverage:
            cmd = f"{base_cmd} --cov=app --cov-report=html --cov-report=term"
        else:
            cmd = base_cmd
        
        success &= run_command(cmd, "所有测试")
    
    else:
        # 运行特定类型的测试
        if args.unit:
            cmd = f"{base_cmd} test_chat_app.py"
            if args.coverage:
                cmd += " --cov=app --cov-report=term"
            success &= run_command(cmd, "单元测试")
        
        if args.ui:
            cmd = f"{base_cmd} test_selenium_ui.py -m ui"
            success &= run_command(cmd, "UI测试")
        
        if args.performance:
            cmd = f"{base_cmd} test_performance.py -m performance --tb=short"
            success &= run_command(cmd, "性能测试")
    
    # 生成测试报告
    if args.coverage:
        print("\n" + "="*60)
        print("生成覆盖率报告...")
        if os.path.exists("htmlcov/index.html"):
            print("📊 HTML覆盖率报告已生成: htmlcov/index.html")
        print("="*60)
    
    # 总结
    print("\n" + "="*60)
    if success:
        print("🎉 所有测试完成!")
    else:
        print("❌ 部分测试失败，请检查上面的输出")
        sys.exit(1)
    print("="*60)

if __name__ == '__main__':
    main()
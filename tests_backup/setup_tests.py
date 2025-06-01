#!/usr/bin/env python3
"""
聊天室测试环境一键设置脚本
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description=""):
    """运行命令并显示结果"""
    print(f"{'🔧 ' + description if description else ''}")
    print(f"执行: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 成功")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ 失败")
        if result.stderr:
            print(result.stderr)
        return False
    return True

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def setup_virtual_environment():
    """设置虚拟环境"""
    print("🏗️ 设置虚拟环境...")
    
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "创建虚拟环境"):
            return False
    
    # 激活虚拟环境的命令因操作系统而异
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    print(f"💡 要激活虚拟环境，请运行: {activate_cmd}")
    return pip_cmd

def install_dependencies(pip_cmd):
    """安装依赖包"""
    print("📦 安装依赖包...")
    
    # 主要依赖
    main_deps = [
        "flask>=2.0.0",
        "flask-socketio>=5.0.0", 
        "python-socketio[client]>=5.0.0"
    ]
    
    # 测试依赖
    test_deps = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-json-report>=1.5.0",
        "selenium>=4.0.0",
        "webdriver-manager>=3.8.0",
        "requests>=2.25.0",
        "psutil>=5.8.0"
    ]
    
    all_deps = main_deps + test_deps
    
    for dep in all_deps:
        if not run_command(f"{pip_cmd} install {dep}", f"安装 {dep}"):
            print(f"⚠️ 安装 {dep} 失败，继续...")
    
    return True

def setup_chromedriver():
    """设置ChromeDriver"""
    print("🌐 设置ChromeDriver...")
    
    # 尝试使用webdriver-manager自动管理
    setup_code = '''
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

try:
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)
    driver.quit()
    print("✅ ChromeDriver设置成功")
except Exception as e:
    print(f"❌ ChromeDriver设置失败: {e}")
    '''
    
    with open("test_chromedriver.py", "w") as f:
        f.write(setup_code)
    
    result = subprocess.run([sys.executable, "test_chromedriver.py"], 
                          capture_output=True, text=True)
    
    os.remove("test_chromedriver.py")
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(result.stderr)
        print("💡 请手动安装ChromeDriver或确保Chrome浏览器已安装")
        return False

def create_test_files():
    """创建测试文件"""
    print("📝 创建测试配置文件...")
    
    # 创建pytest.ini
    pytest_ini = """
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    --strict-markers
    --strict-config
    --tb=short
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    ui: marks tests as UI tests
    performance: marks tests as performance tests
    security: marks tests as security tests
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
"""
    
    with open("pytest.ini", "w") as f:
        f.write(pytest_ini)
    
    # 创建requirements.txt
    requirements = """
flask>=2.0.0
flask-socketio>=5.0.0
python-socketio[client]>=5.0.0
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-json-report>=1.5.0
selenium>=4.0.0
webdriver-manager>=3.8.0
requests>=2.25.0
psutil>=5.8.0
"""
    
    with open("requirements-test.txt", "w") as f:
        f.write(requirements.strip())
    
    print("✅ 配置文件创建完成")
    return True

def verify_setup():
    """验证设置"""
    print("🔍 验证测试环境...")
    
    # 测试导入
    test_imports = [
        "flask", "flask_socketio", "pytest", 
        "selenium", "requests", "psutil"
    ]
    
    for module in test_imports:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            return False
    
    # 测试应用是否能启动
    test_app_code = '''
import sys
sys.path.append(".")
try:
    from app import app
    print("✅ 应用导入成功")
except Exception as e:
    print(f"❌ 应用导入失败: {e}")
    sys.exit(1)
'''
    
    with open("test_app_import.py", "w") as f:
        f.write(test_app_code)
    
    result = subprocess.run([sys.executable, "test_app_import.py"], 
                          capture_output=True, text=True)
    
    os.remove("test_app_import.py")
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(result.stderr)
        return False
    
    print("🎉 测试环境验证通过!")
    return True

def main():
    """主设置流程"""
    print("🚀 聊天室测试环境设置")
    print("=" * 40)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 设置虚拟环境
    pip_cmd = setup_virtual_environment()
    if not pip_cmd:
        return False
    
    # 安装依赖
    if not install_dependencies(pip_cmd):
        return False
    
    # 设置ChromeDriver
    setup_chromedriver()
    
    # 创建测试文件
    create_test_files()
    
    # 验证设置
    if verify_setup():
        print("\n🎉 测试环境设置完成!")
        print("\n下一步:")
        print("1. 激活虚拟环境")
        if os.name == 'nt':
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("2. 启动聊天应用")
        print("   python app.py")
        print("3. 运行测试")
        print("   python comprehensive_test_runner.py")
        return True
    else:
        print("\n❌ 设置过程中出现问题，请检查上面的错误信息")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
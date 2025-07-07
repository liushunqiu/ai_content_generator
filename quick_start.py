#!/usr/bin/env python3
"""
AI工具公众号 - 快速启动脚本 (精简版)
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🤖 AI工具公众号自动化系统 (精简版)                     ║
    ║                                                              ║
    ║        使用Google Gemini AI，完全免费！                       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖包...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败，请手动运行：pip install -r requirements.txt")
        return False

def create_env_file():
    """创建环境配置文件"""
    env_content = """# AI工具公众号配置 (Gemini版)

# Google Gemini API密钥 (必需)
# 获取地址: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# 调试模式
DEBUG=True

# 测试模式 (不会真实发布)
DRY_RUN=True

# 数据库配置
DATABASE_URL=sqlite:///ai_tools.db

# 可选的其他API密钥
PRODUCTHUNT_TOKEN=
GITHUB_TOKEN=
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ 已创建 .env 配置文件")

def create_simple_test():
    """创建简单测试脚本"""
    test_content = '''#!/usr/bin/env python3
"""
简单测试脚本 - 验证Gemini API是否工作
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini():
    """测试Gemini API"""
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your-gemini-api-key-here':
        print("❌ 请先在 .env 文件中设置 GEMINI_API_KEY")
        print("获取地址: https://aistudio.google.com/app/apikey")
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("🧪 测试Gemini API...")
        response = model.generate_content("请用一句话介绍什么是人工智能")
        
        print("✅ Gemini API测试成功！")
        print(f"回复: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API测试失败: {e}")
        return False

if __name__ == "__main__":
    test_gemini()
'''
    
    with open('test_gemini.py', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    os.chmod('test_gemini.py', 0o755)
    print("✅ 已创建测试脚本 test_gemini.py")

def show_instructions():
    """显示使用说明"""
    print("\n" + "="*60)
    print("🎯 快速开始指南")
    print("="*60)
    
    print("\n1️⃣  获取Gemini API密钥：")
    print("   • 访问：https://aistudio.google.com/app/apikey")
    print("   • 登录Google账号")
    print("   • 点击 'Create API Key'")
    print("   • 复制生成的API密钥")
    
    print("\n2️⃣  配置API密钥：")
    print("   • 编辑 .env 文件")
    print("   • 将 'your-gemini-api-key-here' 替换为你的真实API密钥")
    
    print("\n3️⃣  测试API连接：")
    print("   python test_gemini.py")
    
    print("\n4️⃣  运行完整系统：")
    print("   python3 ai_writer.py")
    
    print("\n💡 优势说明：")
    print("   • Gemini API完全免费（有配额限制）")
    print("   • 支持中文，效果很好")
    print("   • 无需信用卡，注册即可使用")
    
    print("\n📚 更多帮助：")
    print("   • 如果遇到问题，检查API密钥是否正确")
    print("   • Gemini有每分钟请求限制，系统已自动处理")
    
    print("\n" + "="*60)

def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return
    
    print(f"✅ Python版本: {sys.version.split()[0]}")
    
    # 安装依赖
    if not install_dependencies():
        return
    
    # 创建配置文件
    if not os.path.exists('.env'):
        create_env_file()
    else:
        print("✅ .env 文件已存在")
    
    # 创建测试脚本
    create_simple_test()
    
    # 创建必要目录
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # 显示说明
    show_instructions()

if __name__ == "__main__":
    main()

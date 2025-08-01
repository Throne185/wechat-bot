"""
安装脚本 - 自动安装依赖和初始化项目
"""
import subprocess
import sys
import os
import platform

def run_command(command, description=""):
    """运行命令并处理错误"""
    print(f"\n{'='*50}")
    if description:
        print(f"正在执行: {description}")
    print(f"命令: {command}")
    print(f"{'='*50}")
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, check=True, 
                                  capture_output=True, text=True, encoding='utf-8')
        else:
            result = subprocess.run(command.split(), check=True, 
                                  capture_output=True, text=True)
        
        if result.stdout:
            print("输出:")
            print(result.stdout)
        
        print(f"✅ {description or '命令'} 执行成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description or '命令'} 执行失败")
        print(f"错误代码: {e.returncode}")
        if e.stdout:
            print(f"标准输出: {e.stdout}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        return False

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True

def install_dependencies():
    """安装Python依赖"""
    print("\n开始安装Python依赖...")
    
    # 升级pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip"):
        print("⚠️ pip升级失败，继续安装依赖...")
    
    # 安装依赖
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "安装项目依赖"):
        print("❌ 依赖安装失败")
        return False
    
    print("✅ 所有依赖安装完成")
    return True

def create_directories():
    """创建必要的目录"""
    print("\n创建项目目录...")
    
    directories = ["data", "logs", "plugins", "utils"]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ 目录创建成功: {directory}")
        except Exception as e:
            print(f"❌ 目录创建失败 {directory}: {e}")
            return False
    
    return True

def create_sample_data():
    """创建示例数据"""
    print("\n创建示例数据...")
    
    try:
        # 运行示例数据创建脚本
        if run_command(f"{sys.executable} create_sample_excel.py", "创建示例Excel文件"):
            print("✅ 示例数据创建成功")
            return True
        else:
            print("❌ 示例数据创建失败")
            return False
    except Exception as e:
        print(f"❌ 创建示例数据出错: {e}")
        return False

def check_config():
    """检查配置文件"""
    print("\n检查配置文件...")
    
    if os.path.exists("config.yaml"):
        print("✅ 配置文件存在")
        return True
    else:
        print("❌ 配置文件不存在")
        return False

def main():
    """主安装流程"""
    print("🤖 微信机器人项目安装程序")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 创建目录
    if not create_directories():
        print("❌ 目录创建失败，安装中止")
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败，安装中止")
        sys.exit(1)
    
    # 创建示例数据
    if not create_sample_data():
        print("⚠️ 示例数据创建失败，但不影响主要功能")
    
    # 检查配置文件
    if not check_config():
        print("⚠️ 请确保config.yaml文件存在并正确配置")
    
    print("\n" + "=" * 60)
    print("🎉 安装完成！")
    print("\n📋 下一步操作：")
    print("1. 将你的Excel数据文件放到 data/ 目录下，命名为 media_database.xlsx")
    print("2. 检查并修改 config.yaml 配置文件")
    print("3. 运行 python wechat_bot.py 启动机器人")
    print("\n📖 使用说明：")
    print("- 启动后会显示二维码，用微信扫码登录")
    print("- 在群聊中@机器人或发送搜索关键词即可使用")
    print("- 支持剧名、演员名搜索")
    print("- 发送'帮助'查看详细使用说明")
    print("\n⚠️ 注意事项：")
    print("- 首次使用建议在小群测试")
    print("- 注意防封号，不要频繁使用")
    print("- 定期备份数据和配置文件")

if __name__ == "__main__":
    main()

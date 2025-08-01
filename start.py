"""
启动脚本 - 带环境检查和错误处理的启动程序
"""
import os
import sys
import time
import subprocess
from pathlib import Path

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("需要Python 3.7或更高版本")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    
    # 检查必要文件
    required_files = [
        "config.yaml",
        "wechat_bot.py",
        "requirements.txt"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少必要文件: {file}")
            return False
        print(f"✅ 文件存在: {file}")
    
    # 检查必要目录
    required_dirs = ["data", "logs", "utils"]
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"❌ 缺少必要目录: {directory}")
            return False
        print(f"✅ 目录存在: {directory}")
    
    # 检查数据文件
    data_file = "data/media_database.xlsx"
    if not os.path.exists(data_file):
        print(f"⚠️ 数据文件不存在: {data_file}")
        print("将使用示例数据，建议添加真实数据文件")
    else:
        print(f"✅ 数据文件存在: {data_file}")
    
    return True

def check_dependencies():
    """检查依赖是否安装"""
    print("\n🔍 检查Python依赖...")

    # 包名和导入名的映射
    required_packages = {
        "itchat": "itchat",
        "pandas": "pandas",
        "openpyxl": "openpyxl",
        "fuzzywuzzy": "fuzzywuzzy",
        "python-Levenshtein": "Levenshtein",
        "pyyaml": "yaml",
        "jieba": "jieba"
    }

    missing_packages = []

    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - 未安装")
            missing_packages.append(package_name)

    if missing_packages:
        print(f"\n❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: python install.py 安装依赖")
        return False

    print("✅ 所有依赖已安装")
    return True

def show_startup_info():
    """显示启动信息"""
    print("\n" + "="*60)
    print("🤖 微信机器人启动程序")
    print("="*60)
    print("📋 功能说明:")
    print("• 支持剧名、演员名搜索")
    print("• 自动回复网盘链接")
    print("• 智能防封号策略")
    print("• 支持群聊和私聊")
    print("\n⚠️ 使用提醒:")
    print("• 首次使用需要扫码登录微信")
    print("• 建议先在小群测试功能")
    print("• 避免频繁使用防止封号")
    print("• 按Ctrl+C可以安全退出")
    print("="*60)

def start_bot():
    """启动机器人"""
    print("\n🚀 启动微信机器人...")
    print("请稍等，正在初始化...")
    
    try:
        # 启动机器人
        subprocess.run([sys.executable, "wechat_bot.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n⏹️ 收到停止信号，正在安全退出...")
        print("机器人已停止运行")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 机器人启动失败，错误代码: {e.returncode}")
        print("请检查错误信息并重试")
    except Exception as e:
        print(f"\n❌ 启动过程中出现错误: {e}")

def show_help():
    """显示帮助信息"""
    print("\n📖 使用帮助:")
    print("\n🔧 安装和配置:")
    print("1. python install.py          # 安装依赖和初始化")
    print("2. 编辑 config.yaml           # 修改配置（可选）")
    print("3. 添加数据到 data/media_database.xlsx")
    print("4. python start.py            # 启动机器人")

    print("\n🔐 登录相关:")
    print("• python login_helper.py      # 登录助手（解决登录问题）")
    print("• python login_helper.py test # 测试登录功能")
    print("• python login_diagnosis.py   # 诊断登录问题")

    print("\n💬 机器人使用:")
    print("• 群聊中@机器人或直接发送搜索词")
    print("• 私聊直接发送搜索词")
    print("• 发送'帮助'查看详细说明")
    print("• 发送'统计'查看数据统计")

    print("\n🛠️ 维护操作:")
    print("• 更新Excel数据文件后发送'重新加载'")
    print("• 修改config.yaml调整安全策略")
    print("• 查看logs/目录下的日志文件")

    print("\n🔒 安全设置维护:")
    print("• 群人数检测阈值: config.yaml -> security.group_member_check.threshold")
    print("• 发送频率限制: config.yaml -> security.rate_limit")
    print("• 延迟发送设置: config.yaml -> security.delay_send")
    print("• 消息格式设置: config.yaml -> message_format")

    print("\n❌ 登录问题解决:")
    print("• 如果登录超时，运行: python login_helper.py")
    print("• 如果频繁失败，运行: python login_diagnosis.py")
    print("• 删除 itchat.pkl 文件可清除登录缓存")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            show_help()
            return
        elif sys.argv[1] == 'install':
            subprocess.run([sys.executable, "install.py"])
            return
        elif sys.argv[1] == 'login':
            print("🔐 启动登录助手...")
            subprocess.run([sys.executable, "login_helper.py"])
            return
        elif sys.argv[1] == 'diagnosis':
            print("🔍 启动登录诊断...")
            subprocess.run([sys.executable, "login_diagnosis.py"])
            return
    
    # 显示启动信息
    show_startup_info()
    
    # 环境检查
    if not check_environment():
        print("\n❌ 环境检查失败，请先运行: python install.py")
        return
    
    # 依赖检查
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请先运行: python install.py")
        return
    
    print("\n✅ 环境检查通过，准备启动机器人...")
    time.sleep(2)
    
    # 启动机器人
    start_bot()

if __name__ == "__main__":
    main()

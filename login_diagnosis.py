"""
微信登录问题诊断工具
"""
import os
import sys
import time
import requests
import platform
from datetime import datetime

class LoginDiagnosis:
    def __init__(self):
        self.issues = []
        self.suggestions = []
    
    def check_network_connection(self):
        """检查网络连接"""
        print("🌐 检查网络连接...")
        
        test_urls = [
            "https://wx.qq.com",
            "https://login.weixin.qq.com",
            "https://webpush.wx.qq.com"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {url} - 连接正常")
                else:
                    print(f"⚠️ {url} - 状态码: {response.status_code}")
                    self.issues.append(f"网络连接异常: {url}")
            except requests.exceptions.Timeout:
                print(f"❌ {url} - 连接超时")
                self.issues.append(f"网络超时: {url}")
            except Exception as e:
                print(f"❌ {url} - 连接失败: {e}")
                self.issues.append(f"网络连接失败: {url}")
    
    def check_python_environment(self):
        """检查Python环境"""
        print("\n🐍 检查Python环境...")
        
        # Python版本
        version = sys.version_info
        print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            self.issues.append("Python版本过低，建议使用3.7+")
        
        # 检查关键包
        packages = {
            'itchat': 'itchat',
            'requests': 'requests',
            'pillow': 'PIL'
        }
        
        for package_name, import_name in packages.items():
            try:
                __import__(import_name)
                print(f"✅ {package_name} - 已安装")
            except ImportError:
                print(f"❌ {package_name} - 未安装")
                self.issues.append(f"缺少依赖包: {package_name}")
    
    def check_system_environment(self):
        """检查系统环境"""
        print("\n💻 检查系统环境...")
        
        # 操作系统
        system = platform.system()
        print(f"操作系统: {system} {platform.release()}")
        
        # 检查防火墙和代理
        if system == "Windows":
            print("⚠️ Windows系统请检查:")
            print("  - 防火墙是否阻止Python网络访问")
            print("  - 是否使用了代理软件")
        
        # 检查时间同步
        print(f"系统时间: {datetime.now()}")
    
    def check_itchat_files(self):
        """检查itchat相关文件"""
        print("\n📁 检查itchat文件...")
        
        # 检查登录缓存文件
        cache_files = [
            "itchat.pkl",
            "QR.png"
        ]
        
        for file in cache_files:
            if os.path.exists(file):
                print(f"📄 {file} - 存在")
                # 检查文件修改时间
                mtime = os.path.getmtime(file)
                mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"   最后修改: {mtime_str}")
            else:
                print(f"📄 {file} - 不存在")
    
    def check_common_issues(self):
        """检查常见问题"""
        print("\n🔍 检查常见问题...")
        
        # 检查是否在虚拟环境中
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ 运行在虚拟环境中")
        else:
            print("⚠️ 未使用虚拟环境")
            self.suggestions.append("建议使用虚拟环境运行")
        
        # 检查端口占用（微信网页版常用端口）
        print("检查端口使用情况...")
        
    def analyze_login_logs(self):
        """分析登录日志"""
        print("\n📋 分析登录日志...")
        
        log_files = [
            "logs/wechat_bot.log",
            "itchat.log"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                print(f"📄 分析 {log_file}...")
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    # 查找错误信息
                    error_keywords = [
                        "timeout", "超时", "失败", "error", "ERROR",
                        "登录失败", "连接失败", "网络错误"
                    ]
                    
                    recent_errors = []
                    for line in lines[-100:]:  # 检查最近100行
                        for keyword in error_keywords:
                            if keyword.lower() in line.lower():
                                recent_errors.append(line.strip())
                                break
                    
                    if recent_errors:
                        print("⚠️ 发现最近的错误:")
                        for error in recent_errors[-5:]:  # 显示最近5个错误
                            print(f"   {error}")
                    else:
                        print("✅ 未发现明显错误")
                        
                except Exception as e:
                    print(f"❌ 读取日志文件失败: {e}")
            else:
                print(f"📄 {log_file} - 不存在")
    
    def generate_report(self):
        """生成诊断报告"""
        print("\n" + "="*60)
        print("📊 诊断报告")
        print("="*60)
        
        if self.issues:
            print("❌ 发现的问题:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        else:
            print("✅ 未发现明显问题")
        
        if self.suggestions:
            print("\n💡 建议:")
            for i, suggestion in enumerate(self.suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        print("\n🔧 通用解决方案:")
        print("1. 确保网络连接稳定")
        print("2. 更新微信到最新版本")
        print("3. 清理itchat缓存文件 (删除itchat.pkl)")
        print("4. 重启Python程序")
        print("5. 等待一段时间后重试")
        print("6. 尝试使用手机热点网络")
        
        print("\n📞 如果问题持续:")
        print("• 检查微信是否支持网页版登录")
        print("• 确认账号未被限制网页版登录")
        print("• 联系微信客服")
        print("="*60)
    
    def run_diagnosis(self):
        """运行完整诊断"""
        print("🔍 开始微信登录问题诊断...")
        print("="*60)
        
        self.check_python_environment()
        self.check_system_environment()
        self.check_network_connection()
        self.check_itchat_files()
        self.check_common_issues()
        self.analyze_login_logs()
        
        self.generate_report()

def main():
    """主函数"""
    diagnosis = LoginDiagnosis()
    diagnosis.run_diagnosis()

if __name__ == "__main__":
    main()

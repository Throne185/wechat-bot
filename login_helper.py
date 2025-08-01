"""
微信登录助手 - 专门处理微信登录问题的工具
"""
import itchat
import time
import os
import sys
from datetime import datetime, timedelta

class WeChatLoginHelper:
    def __init__(self):
        self.login_attempts = 0
        self.max_attempts = 3
        self.last_login_time = None
        self.min_login_interval = 30  # 最小登录间隔(秒)
    
    def check_login_frequency(self):
        """检查登录频率，避免过于频繁的登录尝试"""
        if self.last_login_time:
            time_since_last = datetime.now() - self.last_login_time
            if time_since_last.total_seconds() < self.min_login_interval:
                wait_time = self.min_login_interval - time_since_last.total_seconds()
                print(f"⏰ 距离上次登录时间过短，等待 {wait_time:.0f} 秒...")
                time.sleep(wait_time)
    
    def show_login_tips(self):
        """显示登录提示"""
        print("\n" + "="*60)
        print("🔐 微信网页版登录助手")
        print("="*60)
        print("📋 登录步骤:")
        print("1. 使用微信扫描下方二维码")
        print("2. 在手机上点击'登录网页版微信'")
        print("3. 请在30秒内完成确认操作")
        print("\n⚠️ 重要提醒:")
        print("• 扫码后必须在手机上点击确认")
        print("• 不要频繁重复扫码，可能导致临时限制")
        print("• 如果多次失败，建议等待10-30分钟后重试")
        print("• 确保网络连接稳定")
        print("="*60)
    
    def login_with_retry(self):
        """带重试机制的登录"""
        for attempt in range(1, self.max_attempts + 1):
            try:
                print(f"\n🔄 登录尝试 {attempt}/{self.max_attempts}")
                
                # 检查登录频率
                self.check_login_frequency()
                
                # 显示提示
                if attempt == 1:
                    self.show_login_tips()
                else:
                    print(f"\n⚠️ 第 {attempt} 次尝试，请重新扫码")
                
                # 记录登录时间
                self.last_login_time = datetime.now()
                
                # 尝试登录
                print("\n📱 正在生成二维码...")
                result = itchat.auto_login(
                    hotReload=True,
                    enableCmdQR=2,  # 在终端显示二维码
                    loginCallback=self._login_success_callback,
                    exitCallback=self._exit_callback
                )
                
                if result:
                    print("\n✅ 登录成功！")
                    return True
                else:
                    print(f"\n❌ 第 {attempt} 次登录失败")
                    
                    if attempt < self.max_attempts:
                        print("⏳ 等待10秒后重试...")
                        time.sleep(10)
                    
            except KeyboardInterrupt:
                print("\n\n⏹️ 用户取消登录")
                return False
            except Exception as e:
                print(f"\n❌ 登录过程出错: {e}")
                if attempt < self.max_attempts:
                    print("⏳ 等待10秒后重试...")
                    time.sleep(10)
        
        print(f"\n❌ 登录失败，已尝试 {self.max_attempts} 次")
        self._show_failure_help()
        return False
    
    def _login_success_callback(self):
        """登录成功回调"""
        print("✅ 微信登录成功！")
    
    def _exit_callback(self):
        """退出回调"""
        print("⚠️ 微信连接已断开")
    
    def _show_failure_help(self):
        """显示失败后的帮助信息"""
        print("\n" + "="*60)
        print("❌ 登录失败 - 可能的解决方案")
        print("="*60)
        print("🔍 常见问题:")
        print("1. 扫码后忘记在手机上点击确认")
        print("2. 网络连接不稳定")
        print("3. 微信版本过旧")
        print("4. 频繁登录被临时限制")
        print("\n💡 建议操作:")
        print("1. 检查网络连接")
        print("2. 更新微信到最新版本")
        print("3. 等待30分钟后重试")
        print("4. 尝试使用其他网络环境")
        print("5. 重启微信应用")
        print("="*60)
    
    def test_login(self):
        """测试登录功能"""
        print("🧪 微信登录测试模式")
        
        if self.login_with_retry():
            print("\n✅ 登录测试成功！")
            
            # 获取登录信息
            try:
                user_info = itchat.search_friends()
                if user_info:
                    print(f"👤 当前用户: {user_info[0]['NickName']}")
                
                # 测试发送消息给自己
                test_msg = f"🤖 微信机器人登录测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                itchat.send(test_msg, toUserName='filehelper')
                print("📝 已发送测试消息到文件传输助手")
                
            except Exception as e:
                print(f"⚠️ 获取用户信息失败: {e}")
            
            # 登出
            print("\n🔓 测试完成，正在登出...")
            itchat.logout()
            print("✅ 已安全登出")
            
        else:
            print("\n❌ 登录测试失败")
            return False
        
        return True

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # 测试模式
        helper = WeChatLoginHelper()
        helper.test_login()
    else:
        # 普通登录
        print("🚀 启动微信登录助手...")
        helper = WeChatLoginHelper()
        
        if helper.login_with_retry():
            print("\n✅ 登录成功！现在可以启动机器人了")
            print("💡 运行命令: python start.py")
        else:
            print("\n❌ 登录失败，请检查问题后重试")
            print("💡 可以运行: python login_helper.py test 进行登录测试")

if __name__ == "__main__":
    main()

"""
微信机器人主程序
"""
import itchat
import time
import logging
import threading
from typing import Dict, Any
import yaml
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.search_engine import SearchEngine
from utils.message_formatter import MessageFormatter
from utils.security_manager import SecurityManager

class WeChatBot:
    def __init__(self, config_path: str = "config.yaml"):
        """初始化微信机器人"""
        self.config_path = config_path
        self.config = self._load_config()
        
        # 初始化日志
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.data_manager = DataManager(config_path)
        self.search_engine = SearchEngine(self.data_manager)
        self.message_formatter = MessageFormatter(config_path)
        self.security_manager = SecurityManager(config_path)
        
        # 状态标志
        self.is_running = False
        self.is_logged_in = False
        
        self.logger.info("微信机器人初始化完成")
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"配置文件加载失败: {e}")
            return {}
    
    def _setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})
        log_level = log_config.get('level', 'INFO')
        log_file = log_config.get('file', 'logs/wechat_bot.log')
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # 配置日志格式
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def start(self):
        """启动机器人"""
        try:
            self.logger.info("正在启动微信机器人...")
            
            # 加载数据
            if not self.data_manager.load_excel_data():
                self.logger.error("数据加载失败，无法启动机器人")
                return False
            
            # 登录微信
            if not self._login_wechat():
                self.logger.error("微信登录失败")
                return False
            
            # 注册消息处理器
            self._register_handlers()
            
            # 启动机器人
            self.is_running = True
            self.logger.info("微信机器人启动成功")
            
            # 发送启动通知（可选）
            self._send_startup_notification()
            
            # 开始监听消息
            itchat.run(debug=False, blockThread=True)
            
        except KeyboardInterrupt:
            self.logger.info("收到停止信号，正在关闭机器人...")
            self.stop()
        except Exception as e:
            self.logger.error(f"机器人运行出错: {e}")
            return False
    
    def _login_wechat(self) -> bool:
        """登录微信"""
        try:
            wechat_config = self.config.get('wechat', {})
            hot_reload = wechat_config.get('hot_reload', True)
            qr_display = wechat_config.get('qr_code_display', 'terminal')
            max_retries = wechat_config.get('max_login_retries', 3)
            login_timeout = wechat_config.get('login_timeout', 60)  # 登录超时时间(秒)

            self.logger.info("开始微信登录流程...")

            for attempt in range(max_retries):
                try:
                    self.logger.info(f"登录尝试 {attempt + 1}/{max_retries}")

                    if attempt > 0:
                        self.logger.info("等待5秒后重试...")
                        time.sleep(5)

                    # 设置二维码显示方式和登录参数
                    login_kwargs = {
                        'hotReload': hot_reload,
                        'loginCallback': self._login_callback,
                        'exitCallback': self._exit_callback
                    }

                    if qr_display == 'terminal':
                        login_kwargs['enableCmdQR'] = 2

                    # 显示登录提示
                    print("\n" + "="*50)
                    print("🔐 微信登录")
                    print("="*50)
                    print("📱 请使用微信扫描二维码")
                    print("⏰ 扫码后请在手机上及时点击'登录网页版微信'")
                    print(f"⏱️  登录超时时间: {login_timeout}秒")
                    print("="*50)

                    # 尝试登录
                    result = itchat.auto_login(**login_kwargs)

                    if result:
                        self.is_logged_in = True
                        self.logger.info("✅ 微信登录成功")
                        print("\n✅ 登录成功！机器人即将启动...")
                        return True
                    else:
                        self.logger.warning(f"❌ 登录尝试 {attempt + 1} 失败")

                except Exception as login_error:
                    self.logger.error(f"登录尝试 {attempt + 1} 出错: {login_error}")

                    if attempt < max_retries - 1:
                        print(f"\n⚠️ 登录失败，将在5秒后重试 ({attempt + 2}/{max_retries})")
                    else:
                        print("\n❌ 所有登录尝试均失败")

            self.logger.error("微信登录失败，已达到最大重试次数")
            return False

        except Exception as e:
            self.logger.error(f"微信登录过程出错: {e}")
            return False

    def _login_callback(self):
        """登录成功回调"""
        self.logger.info("登录回调：微信登录成功")
        print("✅ 微信登录成功！")

    def _exit_callback(self):
        """退出回调"""
        self.logger.info("微信连接已断开")
        print("⚠️ 微信连接已断开")
    
    def _register_handlers(self):
        """注册消息处理器"""
        
        @itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
        def handle_group_message(msg):
            """处理群消息"""
            try:
                self._handle_message(msg, is_group=True)
            except Exception as e:
                self.logger.error(f"处理群消息出错: {e}")
        
        @itchat.msg_register(itchat.content.TEXT, isGroupChat=False)
        def handle_private_message(msg):
            """处理私聊消息"""
            try:
                self._handle_message(msg, is_group=False)
            except Exception as e:
                self.logger.error(f"处理私聊消息出错: {e}")
        
        self.logger.info("消息处理器注册完成")
    
    def _handle_message(self, msg: Dict[str, Any], is_group: bool = True):
        """处理消息"""
        try:
            # 获取消息信息
            content = msg.get('Content', '').strip()
            from_user = msg.get('FromUserName', '')
            actual_user = msg.get('ActualUserName', from_user)  # 群消息中的实际发送者
            
            # 基本过滤
            if not content or not self.message_formatter.should_respond_to_message(content):
                return
            
            # 群消息需要@机器人或包含关键词才响应
            if is_group and not self._should_respond_to_group_message(content):
                return
            
            # 安全检查
            can_respond, reason = self.security_manager.should_respond(
                from_user, actual_user, content
            )
            
            if not can_respond:
                self.logger.info(f"安全策略阻止响应: {reason}")
                return
            
            # 处理特殊命令
            if self._handle_special_commands(content, from_user):
                return
            
            # 搜索处理
            self._process_search_request(content, from_user, actual_user)
            
        except Exception as e:
            self.logger.error(f"消息处理出错: {e}")
    
    def _should_respond_to_group_message(self, content: str) -> bool:
        """判断是否应该响应群消息"""
        # 检查是否@了机器人
        if '@' in content:
            return True
        
        # 检查是否包含搜索关键词
        search_keywords = ['搜索', '查找', '找', '有没有', '求', '资源']
        content_lower = content.lower()
        
        for keyword in search_keywords:
            if keyword in content_lower:
                return True
        
        # 检查是否是明显的搜索请求（包含演员名或剧名特征）
        if len(content) >= 2 and any(char.isalpha() or '\u4e00' <= char <= '\u9fff' for char in content):
            return True
        
        return False
    
    def _handle_special_commands(self, content: str, from_user: str) -> bool:
        """处理特殊命令"""
        content_lower = content.lower().strip()
        
        if content_lower in ['帮助', 'help', '使用说明']:
            help_msg = self.message_formatter.format_help_message()
            self._send_message(help_msg, from_user)
            return True
        
        elif content_lower in ['统计', 'stats', '状态']:
            stats = self.data_manager.get_stats()
            stats_msg = self.message_formatter.format_stats_message(stats)
            self._send_message(stats_msg, from_user)
            return True
        
        elif content_lower in ['重新加载', 'reload']:
            if self.data_manager.load_excel_data():
                self._send_message("✅ 数据重新加载成功", from_user)
            else:
                self._send_message("❌ 数据重新加载失败", from_user)
            return True
        
        return False
    
    def _process_search_request(self, query: str, from_user: str, actual_user: str):
        """处理搜索请求"""
        try:
            # 清理查询字符串
            query = query.replace('@', '').strip()
            
            # 执行搜索
            results = self.search_engine.intelligent_search(query)
            
            # 格式化结果
            messages = self.message_formatter.format_search_results(results, query)
            
            # 发送结果
            self._send_messages_with_delay(messages, from_user, actual_user)
            
        except Exception as e:
            self.logger.error(f"搜索处理出错: {e}")
            error_msg = self.message_formatter.format_error_message('search_failed', str(e))
            self._send_message(error_msg, from_user)
    
    def _send_messages_with_delay(self, messages: list, from_user: str, actual_user: str):
        """带延迟发送多条消息"""
        if not messages:
            return
        
        def send_delayed():
            try:
                for i, message in enumerate(messages):
                    if i > 0:  # 第一条消息立即发送，后续消息有延迟
                        delay = self.security_manager.calculate_send_delay(from_user, i + 1)
                        time.sleep(delay)
                    
                    self._send_message(message, from_user)
                    self.security_manager.record_message_sent(from_user, actual_user)
                
            except Exception as e:
                self.logger.error(f"延迟发送消息出错: {e}")
        
        # 在新线程中发送，避免阻塞
        threading.Thread(target=send_delayed, daemon=True).start()
    
    def _send_message(self, message: str, to_user: str):
        """发送消息"""
        try:
            if not self.security_manager.is_message_safe(message):
                self.logger.warning("消息内容不安全，拒绝发送")
                return
            
            itchat.send(message, toUserName=to_user)
            self.logger.info(f"消息已发送到 {to_user[:10]}...")
            
        except Exception as e:
            self.logger.error(f"发送消息失败: {e}")
    
    def _send_startup_notification(self):
        """发送启动通知"""
        try:
            # 可以向指定用户或群发送启动通知
            # 这里暂时不实现，避免打扰
            pass
        except Exception as e:
            self.logger.error(f"发送启动通知失败: {e}")
    
    def stop(self):
        """停止机器人"""
        try:
            self.is_running = False
            if self.is_logged_in:
                itchat.logout()
            self.logger.info("微信机器人已停止")
        except Exception as e:
            self.logger.error(f"停止机器人出错: {e}")

def main():
    """主函数"""
    bot = WeChatBot()
    bot.start()

if __name__ == "__main__":
    main()

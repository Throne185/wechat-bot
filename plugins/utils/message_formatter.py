"""
消息格式化器 - 处理搜索结果的格式化和分批发送
"""
import logging
from typing import List, Dict, Any, Tuple
import yaml

class MessageFormatter:
    def __init__(self, config_path: str = "config.yaml"):
        """初始化消息格式化器"""
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"配置文件加载失败: {e}")
            return {}
    
    def format_search_results(self, results: List[Dict[str, Any]], query: str = "") -> List[str]:
        """格式化搜索结果为消息列表"""
        if not results:
            return [f"抱歉，没有找到与「{query}」相关的内容。"]
        
        # 获取配置
        max_items_per_message = self.config.get('search', {}).get('max_items_per_message', 3)
        
        # 格式化单条结果
        formatted_items = []
        for result in results:
            formatted_item = self._format_single_result(result)
            if formatted_item:
                formatted_items.append(formatted_item)
        
        # 分批处理
        messages = self._split_into_messages(formatted_items, max_items_per_message, len(results))
        
        return messages
    
    def _format_single_result(self, result: Dict[str, Any]) -> str:
        """格式化单条搜索结果"""
        try:
            # 获取模板
            template = self.config.get('message_format', {}).get('single_template', 
                "🎬《{drama_name}》\n主演：{actors}\n集数：{episodes}集\n夸克：{quark_link}\n百度：{baidu_link}")
            
            # 数据清理和处理
            drama_name = str(result.get('drama_name', '')).strip()
            actors = str(result.get('actors', '')).strip()
            episodes = str(result.get('episodes', '')).strip()
            quark_link = str(result.get('quark_link', '')).strip()
            baidu_link = str(result.get('baidu_link', '')).strip()
            
            # 处理集数显示
            if episodes and episodes != 'nan' and episodes != '':
                try:
                    # 如果是数字，确保格式正确
                    episode_num = int(float(episodes))
                    episodes = str(episode_num)
                except:
                    pass
            else:
                episodes = "未知"
            
            # 处理演员信息
            if not actors or actors == 'nan':
                actors = "未知"
            
            # 处理链接
            if not quark_link or quark_link == 'nan':
                quark_link = "暂无"
            
            if not baidu_link or baidu_link == 'nan':
                baidu_link = "暂无"
            
            # 格式化消息
            formatted_message = template.format(
                drama_name=drama_name,
                actors=actors,
                episodes=episodes,
                quark_link=quark_link,
                baidu_link=baidu_link
            )
            
            return formatted_message
            
        except Exception as e:
            self.logger.error(f"格式化单条结果失败: {e}")
            return ""
    
    def _split_into_messages(self, formatted_items: List[str], max_items_per_message: int, total_count: int) -> List[str]:
        """将格式化的结果分割成多条消息"""
        if not formatted_items:
            return []
        
        messages = []
        separator = self.config.get('message_format', {}).get('separator', '\n\n')
        
        # 如果结果太多，添加提示信息
        if total_count > len(formatted_items):
            too_many_template = self.config.get('message_format', {}).get('too_many_results', 
                "找到 {count} 个相关结果，为避免刷屏，仅显示前 {shown} 个：")
            prefix_message = too_many_template.format(count=total_count, shown=len(formatted_items))
            messages.append(prefix_message)
        
        # 分批处理
        for i in range(0, len(formatted_items), max_items_per_message):
            batch = formatted_items[i:i + max_items_per_message]
            message = separator.join(batch)
            
            # 添加批次信息（如果有多批）
            if len(formatted_items) > max_items_per_message:
                batch_num = (i // max_items_per_message) + 1
                total_batches = (len(formatted_items) + max_items_per_message - 1) // max_items_per_message
                if total_batches > 1:
                    message = f"📺 第{batch_num}批结果：\n\n{message}"
            
            messages.append(message)
        
        return messages
    
    def format_error_message(self, error_type: str, details: str = "") -> str:
        """格式化错误消息"""
        error_messages = {
            'no_data': "❌ 数据库暂时无法访问，请稍后再试。",
            'search_failed': "❌ 搜索功能暂时不可用，请稍后再试。",
            'invalid_query': "❌ 请输入有效的搜索关键词。",
            'rate_limit': "⏰ 查询过于频繁，请稍后再试。",
            'system_error': "❌ 系统暂时出现问题，请稍后再试。"
        }
        
        base_message = error_messages.get(error_type, "❌ 出现未知错误。")
        
        if details:
            return f"{base_message}\n详情：{details}"
        
        return base_message
    
    def format_help_message(self) -> str:
        """格式化帮助消息"""
        help_text = """
🤖 影视资源搜索机器人使用说明：

📝 搜索方式：
• 直接输入剧名：如「庆余年」
• 输入演员名字：如「张若昀」
• 混合搜索：如「张若昀 古装」

🎯 搜索技巧：
• 支持模糊搜索，不需要完整剧名
• 支持多个关键词组合搜索
• 自动识别演员和剧名

📋 返回信息包括：
• 剧名和主演信息
• 集数信息
• 夸克网盘链接
• 百度网盘链接

⚠️ 注意事项：
• 为避免刷屏，每次最多显示10个结果
• 如有多个结果会分批发送
• 请合理使用，避免频繁查询

💡 示例：
输入「赵丽颖」→ 显示赵丽颖主演的所有剧集
输入「古装 爱情」→ 显示古装爱情类剧集
        """
        return help_text.strip()
    
    def format_stats_message(self, stats: Dict[str, int]) -> str:
        """格式化统计信息消息"""
        total_dramas = stats.get('total_dramas', 0)
        drama_keywords = stats.get('drama_keywords', 0)
        actor_keywords = stats.get('actor_keywords', 0)
        
        stats_text = f"""
📊 资源库统计信息：

🎬 总剧集数：{total_dramas} 部
🔍 剧名关键词：{drama_keywords} 个
👥 演员关键词：{actor_keywords} 个

数据最后更新：刚刚
        """
        return stats_text.strip()
    
    def format_welcome_message(self) -> str:
        """格式化欢迎消息"""
        welcome_text = """
🎉 欢迎使用影视资源搜索机器人！

我可以帮你搜索影视剧资源，包括：
• 🎬 电视剧、电影资源
• 👥 演员作品查询  
• 🔗 网盘链接获取

直接发送剧名或演员名即可开始搜索！
发送「帮助」查看详细使用说明。
        """
        return welcome_text.strip()
    
    def should_respond_to_message(self, message: str) -> bool:
        """判断是否应该响应该消息"""
        if not message:
            return False
        
        # 过滤掉太短的消息
        if len(message.strip()) < 2:
            return False
        
        # 过滤掉纯数字、纯符号等
        if message.strip().isdigit():
            return False
        
        # 过滤掉常见的无意义消息
        ignore_patterns = ['哈哈', '呵呵', '嗯嗯', '好的', '谢谢', '👍', '😄', '😊']
        message_lower = message.lower().strip()
        
        for pattern in ignore_patterns:
            if message_lower == pattern:
                return False
        
        return True

"""
安全管理器 - 防封号策略和安全机制
"""
import time
import random
import logging
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import yaml
import threading

class SecurityManager:
    def __init__(self, config_path: str = "config.yaml"):
        """初始化安全管理器"""
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
        # 消息发送记录
        self.message_history = defaultdict(deque)  # 每个群的消息历史
        self.user_request_history = defaultdict(deque)  # 每个用户的请求历史
        self.global_message_count = deque()  # 全局消息计数
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 群信息缓存
        self.group_info_cache = {}
        self.cache_update_time = {}
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"配置文件加载失败: {e}")
            return {}
    
    def should_respond(self, group_id: str, user_id: str, message: str) -> Tuple[bool, str]:
        """判断是否应该响应消息"""
        with self.lock:
            current_time = datetime.now()
            
            # 1. 检查全局频率限制
            if not self._check_global_rate_limit(current_time):
                return False, "全局发送频率过高，请稍后再试"
            
            # 2. 检查用户请求频率
            if not self._check_user_rate_limit(user_id, current_time):
                return False, "您的请求过于频繁，请稍后再试"
            
            # 3. 检查群消息频率
            if not self._check_group_rate_limit(group_id, current_time):
                return False, "群内查询过于频繁，请稍后再试"
            
            return True, ""
    
    def _check_global_rate_limit(self, current_time: datetime) -> bool:
        """检查全局频率限制"""
        security_config = self.config.get('security', {})
        rate_limit_config = security_config.get('rate_limit', {})
        
        if not rate_limit_config.get('enabled', True):
            return True
        
        max_per_minute = rate_limit_config.get('max_per_minute', 10)
        max_per_hour = rate_limit_config.get('max_per_hour', 50)
        
        # 清理过期记录
        minute_ago = current_time - timedelta(minutes=1)
        hour_ago = current_time - timedelta(hours=1)
        
        while self.global_message_count and self.global_message_count[0] < hour_ago:
            self.global_message_count.popleft()
        
        # 检查小时限制
        if len(self.global_message_count) >= max_per_hour:
            return False
        
        # 检查分钟限制
        recent_messages = [t for t in self.global_message_count if t > minute_ago]
        if len(recent_messages) >= max_per_minute:
            return False
        
        return True
    
    def _check_user_rate_limit(self, user_id: str, current_time: datetime) -> bool:
        """检查用户请求频率"""
        # 用户每分钟最多3次请求
        max_user_per_minute = 3
        minute_ago = current_time - timedelta(minutes=1)
        
        user_history = self.user_request_history[user_id]
        
        # 清理过期记录
        while user_history and user_history[0] < minute_ago:
            user_history.popleft()
        
        if len(user_history) >= max_user_per_minute:
            return False
        
        return True
    
    def _check_group_rate_limit(self, group_id: str, current_time: datetime) -> bool:
        """检查群消息频率"""
        # 每个群每分钟最多5次响应
        max_group_per_minute = 5
        minute_ago = current_time - timedelta(minutes=1)
        
        group_history = self.message_history[group_id]
        
        # 清理过期记录
        while group_history and group_history[0] < minute_ago:
            group_history.popleft()
        
        if len(group_history) >= max_group_per_minute:
            return False
        
        return True
    
    def record_message_sent(self, group_id: str, user_id: str):
        """记录消息发送"""
        with self.lock:
            current_time = datetime.now()
            
            # 记录全局消息
            self.global_message_count.append(current_time)
            
            # 记录群消息
            self.message_history[group_id].append(current_time)
            
            # 记录用户请求
            self.user_request_history[user_id].append(current_time)
    
    def calculate_send_delay(self, group_id: str, message_count: int = 1) -> float:
        """计算发送延迟时间"""
        security_config = self.config.get('security', {})
        delay_config = security_config.get('delay_send', {})
        
        if not delay_config.get('enabled', True):
            return 0
        
        base_delay = delay_config.get('base_delay', 2)
        random_delay = delay_config.get('random_delay', 3)
        group_extra_delay = delay_config.get('group_extra_delay', 5)
        
        # 基础延迟
        total_delay = base_delay
        
        # 随机延迟
        total_delay += random.uniform(0, random_delay)
        
        # 根据群人数调整延迟
        group_member_count = self._get_group_member_count(group_id)
        group_threshold = security_config.get('group_member_check', {}).get('threshold', 20)
        
        if group_member_count > group_threshold:
            total_delay += group_extra_delay
            # 人数越多，延迟越长
            extra_factor = min((group_member_count - group_threshold) / 50, 2.0)
            total_delay += extra_factor * 2
        
        # 根据消息数量调整延迟
        if message_count > 1:
            total_delay += (message_count - 1) * 1.5
        
        return total_delay
    
    def _get_group_member_count(self, group_id: str) -> int:
        """获取群成员数量（带缓存）"""
        current_time = time.time()
        
        # 检查缓存是否有效（5分钟有效期）
        if (group_id in self.group_info_cache and 
            group_id in self.cache_update_time and 
            current_time - self.cache_update_time[group_id] < 300):
            return self.group_info_cache[group_id]
        
        # 这里应该调用微信API获取群成员数量
        # 暂时返回默认值，实际使用时需要集成微信API
        member_count = 30  # 默认值
        
        # 更新缓存
        self.group_info_cache[group_id] = member_count
        self.cache_update_time[group_id] = current_time
        
        return member_count
    
    def update_group_member_count(self, group_id: str, member_count: int):
        """更新群成员数量"""
        with self.lock:
            self.group_info_cache[group_id] = member_count
            self.cache_update_time[group_id] = time.time()
    
    def is_safe_time_to_send(self) -> bool:
        """判断当前是否是安全的发送时间"""
        current_hour = datetime.now().hour
        
        # 避免在深夜时间发送消息（23:00-7:00）
        if current_hour >= 23 or current_hour < 7:
            return False
        
        return True
    
    def get_security_status(self) -> Dict:
        """获取安全状态信息"""
        with self.lock:
            current_time = datetime.now()
            minute_ago = current_time - timedelta(minutes=1)
            hour_ago = current_time - timedelta(hours=1)
            
            # 统计最近的消息数量
            recent_global_messages = len([t for t in self.global_message_count if t > minute_ago])
            hourly_global_messages = len([t for t in self.global_message_count if t > hour_ago])
            
            return {
                'recent_messages_per_minute': recent_global_messages,
                'recent_messages_per_hour': hourly_global_messages,
                'active_groups': len(self.message_history),
                'active_users': len(self.user_request_history),
                'is_safe_time': self.is_safe_time_to_send(),
                'cached_groups': len(self.group_info_cache)
            }
    
    def reset_rate_limits(self):
        """重置频率限制（用于测试或紧急情况）"""
        with self.lock:
            self.message_history.clear()
            self.user_request_history.clear()
            self.global_message_count.clear()
            self.logger.info("频率限制已重置")
    
    def add_whitelist_user(self, user_id: str):
        """添加白名单用户（暂时实现，可扩展）"""
        # 这里可以实现白名单逻辑
        pass
    
    def is_message_safe(self, message: str) -> bool:
        """检查消息内容是否安全"""
        # 检查敏感词
        sensitive_words = ['广告', '推广', '加群', '微商', '代理']
        message_lower = message.lower()
        
        for word in sensitive_words:
            if word in message_lower:
                return False
        
        # 检查消息长度
        if len(message) > 2000:  # 消息过长可能有风险
            return False
        
        return True

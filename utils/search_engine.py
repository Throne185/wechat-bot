"""
智能搜索引擎 - 提供高级搜索功能
"""
import re
import jieba
import logging
from typing import List, Dict, Any, Tuple
from fuzzywuzzy import fuzz
from utils.data_manager import DataManager

class SearchEngine:
    def __init__(self, data_manager: DataManager):
        """初始化搜索引擎"""
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
        
        # 预编译正则表达式
        self.year_pattern = re.compile(r'\d{4}年?')
        self.episode_pattern = re.compile(r'(\d+)集')
        
    def intelligent_search(self, query: str) -> List[Dict[str, Any]]:
        """智能搜索 - 综合多种搜索策略"""
        query = self._preprocess_query(query)
        
        if not query:
            return []
        
        # 多策略搜索
        results = []
        
        # 1. 基础搜索
        basic_results = self.data_manager.search(query)
        results.extend(basic_results)
        
        # 2. 提取关键信息进行搜索
        extracted_info = self._extract_search_info(query)
        if extracted_info:
            for info in extracted_info:
                info_results = self.data_manager.search(info)
                results.extend(info_results)
        
        # 3. 同义词搜索
        synonyms = self._get_synonyms(query)
        for synonym in synonyms:
            synonym_results = self.data_manager.search(synonym)
            results.extend(synonym_results)
        
        # 去重并排序
        unique_results = self._deduplicate_and_rank(results, query)
        
        return unique_results
    
    def _preprocess_query(self, query: str) -> str:
        """预处理查询字符串"""
        if not query:
            return ""
        
        # 去除多余空格
        query = re.sub(r'\s+', ' ', query.strip())
        
        # 去除常见的无意义词汇
        stop_words = ['的', '了', '是', '在', '有', '和', '与', '或', '电视剧', '电影', '剧集']
        words = jieba.cut(query)
        filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
        
        if filtered_words:
            return ' '.join(filtered_words)
        else:
            return query
    
    def _extract_search_info(self, query: str) -> List[str]:
        """从查询中提取关键信息"""
        extracted = []
        
        # 提取年份
        years = self.year_pattern.findall(query)
        for year in years:
            extracted.append(year.replace('年', ''))
        
        # 提取集数信息
        episodes = self.episode_pattern.findall(query)
        for episode in episodes:
            extracted.append(f"{episode}集")
        
        # 提取可能的演员名字（2-4个字符的中文）
        chinese_names = re.findall(r'[\u4e00-\u9fff]{2,4}', query)
        for name in chinese_names:
            if len(name) >= 2 and not any(char in name for char in ['电视', '电影', '剧集', '网盘']):
                extracted.append(name)
        
        return extracted
    
    def _get_synonyms(self, query: str) -> List[str]:
        """获取同义词"""
        synonyms = []
        
        # 常见同义词映射
        synonym_map = {
            '古装': ['古代', '古风', '宫廷'],
            '现代': ['都市', '当代', '现代剧'],
            '爱情': ['恋爱', '言情', '浪漫'],
            '悬疑': ['推理', '犯罪', '刑侦'],
            '喜剧': ['搞笑', '幽默', '轻松'],
            '历史': ['古代', '历史剧'],
            '战争': ['军事', '抗战'],
            '青春': ['校园', '学生'],
        }
        
        for key, values in synonym_map.items():
            if key in query:
                synonyms.extend(values)
            for value in values:
                if value in query:
                    synonyms.append(key)
        
        return list(set(synonyms))
    
    def _deduplicate_and_rank(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """去重并按相关性排序"""
        if not results:
            return []
        
        # 去重 - 基于剧名
        seen_dramas = set()
        unique_results = []
        
        for result in results:
            drama_name = result.get('drama_name', '')
            if drama_name and drama_name not in seen_dramas:
                seen_dramas.add(drama_name)
                unique_results.append(result)
        
        # 计算相关性分数并排序
        scored_results = []
        for result in unique_results:
            score = self._calculate_relevance_score(result, query)
            scored_results.append((score, result))
        
        # 按分数降序排序
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        return [result for score, result in scored_results]
    
    def _calculate_relevance_score(self, result: Dict[str, Any], query: str) -> float:
        """计算相关性分数"""
        score = 0.0
        
        drama_name = result.get('drama_name', '')
        actors = result.get('actors', '')
        
        # 剧名匹配分数 (权重: 0.6)
        if drama_name:
            drama_score = fuzz.partial_ratio(query.lower(), drama_name.lower()) / 100.0
            score += drama_score * 0.6
        
        # 演员匹配分数 (权重: 0.4)
        if actors:
            actor_score = fuzz.partial_ratio(query.lower(), actors.lower()) / 100.0
            score += actor_score * 0.4
        
        # 完全匹配加分
        if query.lower() in drama_name.lower():
            score += 0.3
        if query.lower() in actors.lower():
            score += 0.2
        
        # 关键词匹配加分
        query_words = list(jieba.cut(query))
        for word in query_words:
            if len(word) > 1:
                if word in drama_name:
                    score += 0.1
                if word in actors:
                    score += 0.05
        
        return min(score, 2.0)  # 限制最大分数
    
    def search_by_actor(self, actor_name: str) -> List[Dict[str, Any]]:
        """按演员搜索"""
        return self.data_manager.search(actor_name)
    
    def search_by_drama(self, drama_name: str) -> List[Dict[str, Any]]:
        """按剧名搜索"""
        return self.data_manager.search(drama_name)
    
    def search_by_type(self, media_type: str) -> List[Dict[str, Any]]:
        """按媒体类型搜索"""
        if self.data_manager.data is None:
            return []
        
        # 过滤指定类型的数据
        filtered_data = self.data_manager.data[
            self.data_manager.data['媒体类型'].str.contains(media_type, na=False, case=False)
        ]
        
        results = []
        for idx, row in filtered_data.iterrows():
            results.append({
                'media_type': str(row.get('媒体类型', '')),
                'drama_name': str(row.get('剧名', '')),
                'episodes': str(row.get('集数', '')),
                'actors': str(row.get('演员名称', '')),
                'quark_link': str(row.get('夸克网盘链接', '')),
                'baidu_link': str(row.get('百度网盘链接', ''))
            })
        
        return results
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """获取搜索建议"""
        if not partial_query or len(partial_query) < 2:
            return []
        
        suggestions = []
        
        # 从剧名索引中获取建议
        for drama_name in self.data_manager.drama_index.keys():
            if partial_query.lower() in drama_name.lower():
                suggestions.append(drama_name)
        
        # 从演员索引中获取建议
        for actor_name in self.data_manager.actor_index.keys():
            if partial_query.lower() in actor_name.lower():
                suggestions.append(actor_name)
        
        # 去重并限制数量
        unique_suggestions = list(set(suggestions))
        return unique_suggestions[:10]

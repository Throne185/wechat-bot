"""
数据管理模块 - 处理Excel数据的读取、索引和搜索
"""
import pandas as pd
import jieba
import logging
from typing import List, Dict, Any, Optional
from fuzzywuzzy import fuzz, process
import os
import yaml

class DataManager:
    def __init__(self, config_path: str = "config.yaml"):
        """初始化数据管理器"""
        self.config = self._load_config(config_path)
        self.data = None
        self.drama_index = {}  # 剧名索引
        self.actor_index = {}  # 演员索引
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"配置文件加载失败: {e}")
            return {}
    
    def load_excel_data(self) -> bool:
        """加载Excel数据"""
        try:
            excel_file = self.config.get('data_source', {}).get('excel_file', 'data/media_database.xlsx')
            
            if not os.path.exists(excel_file):
                self.logger.error(f"Excel文件不存在: {excel_file}")
                return False
            
            # 读取Excel文件
            self.data = pd.read_excel(excel_file)
            
            # 获取列映射配置
            columns = self.config.get('data_source', {}).get('columns', {})
            
            # 重命名列
            column_names = ['媒体类型', '剧名', '集数', '演员名称', '夸克网盘链接', '百度网盘链接']
            if len(self.data.columns) >= 6:
                self.data.columns = column_names[:len(self.data.columns)]
            
            # 数据清洗
            self.data = self.data.dropna(subset=['剧名'])  # 删除剧名为空的行
            self.data['剧名'] = self.data['剧名'].astype(str).str.strip()
            self.data['演员名称'] = self.data['演员名称'].astype(str).str.strip()
            
            # 建立索引
            self._build_indexes()
            
            self.logger.info(f"成功加载 {len(self.data)} 条数据")
            return True
            
        except Exception as e:
            self.logger.error(f"加载Excel数据失败: {e}")
            return False
    
    def _build_indexes(self):
        """建立搜索索引"""
        self.drama_index = {}
        self.actor_index = {}
        
        for idx, row in self.data.iterrows():
            drama_name = str(row['剧名']).strip()
            actors = str(row['演员名称']).strip()
            
            # 剧名索引
            if drama_name and drama_name != 'nan':
                # 使用jieba分词
                drama_words = list(jieba.cut(drama_name))
                for word in drama_words:
                    if len(word) > 1:  # 忽略单字
                        if word not in self.drama_index:
                            self.drama_index[word] = []
                        self.drama_index[word].append(idx)
                
                # 完整剧名
                if drama_name not in self.drama_index:
                    self.drama_index[drama_name] = []
                self.drama_index[drama_name].append(idx)
            
            # 演员索引
            if actors and actors != 'nan':
                # 分割演员名称（支持逗号、顿号、空格分割）
                actor_list = []
                for sep in ['、', ',', '，', ' ', '　']:
                    actors = actors.replace(sep, '|')
                actor_list = [actor.strip() for actor in actors.split('|') if actor.strip()]
                
                for actor in actor_list:
                    if actor:
                        if actor not in self.actor_index:
                            self.actor_index[actor] = []
                        self.actor_index[actor].append(idx)
                        
                        # 演员名字的分词
                        actor_words = list(jieba.cut(actor))
                        for word in actor_words:
                            if len(word) > 1:
                                if word not in self.actor_index:
                                    self.actor_index[word] = []
                                self.actor_index[word].append(idx)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """搜索功能"""
        if self.data is None:
            return []
        
        query = query.strip()
        if not query:
            return []
        
        # 获取配置
        similarity_threshold = self.config.get('search', {}).get('similarity_threshold', 60)
        max_results = self.config.get('search', {}).get('max_results', 10)
        
        result_indices = set()
        
        # 1. 精确匹配
        exact_matches = self._exact_search(query)
        result_indices.update(exact_matches)
        
        # 2. 模糊匹配
        if len(result_indices) < max_results:
            fuzzy_matches = self._fuzzy_search(query, similarity_threshold)
            result_indices.update(fuzzy_matches)
        
        # 3. 分词搜索
        if len(result_indices) < max_results:
            word_matches = self._word_search(query)
            result_indices.update(word_matches)
        
        # 转换为结果列表
        results = []
        for idx in list(result_indices)[:max_results]:
            if idx < len(self.data):
                row = self.data.iloc[idx]
                results.append({
                    'media_type': str(row.get('媒体类型', '')),
                    'drama_name': str(row.get('剧名', '')),
                    'episodes': str(row.get('集数', '')),
                    'actors': str(row.get('演员名称', '')),
                    'quark_link': str(row.get('夸克网盘链接', '')),
                    'baidu_link': str(row.get('百度网盘链接', ''))
                })
        
        return results
    
    def _exact_search(self, query: str) -> List[int]:
        """精确搜索"""
        indices = []
        
        # 在剧名索引中搜索
        if query in self.drama_index:
            indices.extend(self.drama_index[query])
        
        # 在演员索引中搜索
        if query in self.actor_index:
            indices.extend(self.actor_index[query])
        
        return list(set(indices))
    
    def _fuzzy_search(self, query: str, threshold: int) -> List[int]:
        """模糊搜索"""
        indices = []
        
        # 在剧名中模糊搜索
        drama_names = list(self.data['剧名'].unique())
        drama_matches = process.extract(query, drama_names, limit=5, scorer=fuzz.partial_ratio)
        
        for match, score in drama_matches:
            if score >= threshold:
                matching_rows = self.data[self.data['剧名'] == match].index.tolist()
                indices.extend(matching_rows)
        
        # 在演员名称中模糊搜索
        all_actors = []
        for actors_str in self.data['演员名称'].dropna():
            for sep in ['、', ',', '，', ' ', '　']:
                actors_str = str(actors_str).replace(sep, '|')
            actor_list = [actor.strip() for actor in str(actors_str).split('|') if actor.strip()]
            all_actors.extend(actor_list)
        
        unique_actors = list(set(all_actors))
        actor_matches = process.extract(query, unique_actors, limit=5, scorer=fuzz.partial_ratio)
        
        for match, score in actor_matches:
            if score >= threshold:
                if match in self.actor_index:
                    indices.extend(self.actor_index[match])
        
        return list(set(indices))
    
    def _word_search(self, query: str) -> List[int]:
        """分词搜索"""
        indices = []
        words = list(jieba.cut(query))
        
        for word in words:
            if len(word) > 1:
                # 在剧名索引中搜索
                if word in self.drama_index:
                    indices.extend(self.drama_index[word])
                
                # 在演员索引中搜索
                if word in self.actor_index:
                    indices.extend(self.actor_index[word])
        
        return list(set(indices))
    
    def get_stats(self) -> Dict[str, int]:
        """获取数据统计信息"""
        if self.data is None:
            return {}
        
        return {
            'total_dramas': len(self.data),
            'drama_keywords': len(self.drama_index),
            'actor_keywords': len(self.actor_index)
        }

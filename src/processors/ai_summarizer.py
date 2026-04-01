"""
AI 摘要生成器 - 使用 Kimi API
"""
import logging
import os
import time
from typing import List, Dict

import openai

logger = logging.getLogger(__name__)


class KimiSummarizer:
    """Kimi AI 摘要生成器"""
    
    def __init__(self):
        # 从环境变量获取 API Key
        api_key = os.environ.get('KIMI_API_KEY')
        if not api_key:
            raise ValueError("KIMI_API_KEY environment variable not set")
        
        # 配置 OpenAI 客户端（Kimi 兼容 OpenAI API）
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )
        
        self.model = "moonshot-v1-8k"
        self.temperature = 0.7
        self.max_tokens = 2000
    
    def process_daily(self, items: List[Dict]) -> List[Dict]:
        """
        处理日报数据
        
        Args:
            items: 原始数据列表
            
        Returns:
            添加摘要后的数据列表
        """
        processed = []
        
        # 批量处理，每批 5 条
        batch_size = 5
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} items")
            
            for item in batch:
                try:
                    summary = self._generate_summary(item)
                    item['ai_summary'] = summary
                    item['ai_tags'] = self._extract_tags(item)
                    processed.append(item)
                    
                    # 避免速率限制
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Failed to process item {item.get('title', 'Unknown')}: {e}")
                    # 使用原始内容作为摘要
                    item['ai_summary'] = item.get('content', '')[:200]
                    item['ai_tags'] = [item.get('type', 'other')]
                    processed.append(item)
        
        return processed
    
    def _generate_summary(self, item: Dict) -> str:
        """为单个条目生成摘要"""
        title = item.get('title', '')
        content = item.get('content', '')[:1000]  # 限制长度
        item_type = item.get('type', 'other')
        
        # 构建提示词
        prompt = f"""你是一位资深的 Linux 内核性能专家。请分析以下内核补丁/提交：

标题：{title}
类型：{item_type}
内容：
{content}

请用简洁的中文（不超过100字）概括这个补丁的核心内容和影响。如果是性能优化，请说明优化目标。"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位资深的 Linux 内核性能专家，擅长分析内核补丁和提交。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Kimi API error: {e}")
            raise
    
    def _extract_tags(self, item: Dict) -> List[str]:
        """提取标签"""
        tags = []
        
        # 基础类型标签
        item_type = item.get('type', 'other')
        tags.append(item_type)
        
        # 子系统标签（从文件路径推断）
        files = item.get('files', [])
        title = item.get('title', '').lower()
        
        subsystem_keywords = {
            'scheduler': ['sched', 'cfs', 'scheduler'],
            'memory': ['mm', 'memory', 'page', 'slab'],
            'filesystem': ['fs', 'ext4', 'xfs', 'btrfs'],
            'networking': ['net', 'tcp', 'udp', 'socket'],
            'io': ['block', 'io', 'nvme', 'scsi'],
            'ebpf': ['bpf', 'ebpf'],
            'security': ['security', 'selinux', 'apparmor'],
        }
        
        for subsystem, keywords in subsystem_keywords.items():
            # 从标题检查
            if any(kw in title for kw in keywords):
                tags.append(subsystem)
                continue
            # 从文件路径检查
            for file in files:
                if any(kw in file.lower() for kw in keywords):
                    tags.append(subsystem)
                    break
        
        return list(set(tags))  # 去重
    
    def generate_daily_overview(self, items: List[Dict]) -> str:
        """
        生成日报总体概述
        
        Args:
            items: 处理后的数据列表
            
        Returns:
            概述文本
        """
        # 统计数据
        stats = {
            'feature': 0,
            'bugfix': 0,
            'perf': 0,
            'other': 0
        }
        
        for item in items:
            item_type = item.get('type', 'other')
            stats[item_type] = stats.get(item_type, 0) + 1
        
        # 构建提示词
        top_items = items[:10]  # 取前10条
        items_text = "\n".join([
            f"- [{item.get('type', 'other')}] {item.get('title', 'No title')}"
            for item in top_items
        ])
        
        prompt = f"""基于今日 Linux 内核动态，生成一份简报：

统计数据：
- 新特性：{stats['feature']} 条
- Bug修复：{stats['bugfix']} 条
- 性能优化：{stats['perf']} 条
- 其他：{stats['other']} 条

重点补丁：
{items_text}

请用3-4句话总结今日内核开发的重点和趋势。"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位资深的 Linux 内核性能专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate overview: {e}")
            return f"今日共 {len(items)} 条内核动态，其中新特性 {stats['feature']} 条，Bug修复 {stats['bugfix']} 条，性能优化 {stats['perf']} 条。"

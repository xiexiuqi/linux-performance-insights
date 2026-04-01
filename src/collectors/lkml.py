"""
LKML (Linux Kernel Mailing List) 收集器
"""
import logging
import re
from datetime import datetime
from typing import List, Dict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class LKMLCollector:
    """LKML 邮件列表收集器"""
    
    BASE_URL = "https://lkml.org/lkml/"
    
    # 排除的作者
    EXCLUDE_AUTHORS = [
        "kernel test robot",
        "tip-bot2",
        "sysbot",
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch(self, date_str: str) -> List[Dict]:
        """
        抓取指定日期的 LKML 邮件
        
        Args:
            date_str: 日期字符串 YYYY-MM-DD
            
        Returns:
            邮件列表
        """
        date = datetime.strptime(date_str, '%Y-%m-%d')
        url = f"{self.BASE_URL}{date.year}/{date.month}/{date.day}"
        
        logger.info(f"Fetching LKML: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch LKML: {e}")
            return []
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        emails = self._parse_page(soup)
        
        logger.info(f"LKML parsed: {len(emails)} emails")
        return emails
    
    def _parse_page(self, soup: BeautifulSoup) -> List[Dict]:
        """解析 LKML 页面"""
        emails = []
        
        # 查找所有邮件条目
        # LKML 的 HTML 结构：每个邮件在一个 <b> 标签中
        for item in soup.find_all('b'):
            email = self._parse_email_item(item)
            if email and self._should_include(email):
                emails.append(email)
        
        return emails
    
    def _parse_email_item(self, item) -> Dict:
        """解析单个邮件条目"""
        try:
            # 获取链接
            link = item.find_parent('a')
            if not link:
                return None
            
            href = link.get('href', '')
            if not href:
                return None
            
            # 获取标题
            title = item.get_text(strip=True)
            
            # 获取作者（通常在标题后面）
            # LKML 格式：[标题] 作者
            author = "Unknown"
            author_match = re.search(r'\s+by\s+(.+)$', title)
            if author_match:
                author = author_match.group(1).strip()
                title = re.sub(r'\s+by\s+.+$', '', title)
            
            return {
                'source': 'LKML',
                'title': title,
                'author': author,
                'url': urljoin(self.BASE_URL, href),
                'content': '',  # 需要单独获取详情页
                'type': self._detect_type(title),
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse email item: {e}")
            return None
    
    def _should_include(self, email: Dict) -> bool:
        """判断是否包含此邮件"""
        title = email.get('title', '').lower()
        author = email.get('author', '').lower()
        
        # 排除特定作者
        for exclude in self.EXCLUDE_AUTHORS:
            if exclude.lower() in author:
                return False
        
        # 必须包含的关键词
        include_patterns = [
            'patch',
            'pull',
            'rfc',
            'git pull',
        ]
        
        has_pattern = any(p in title for p in include_patterns)
        
        # 排除回复邮件（Re:）
        is_reply = title.startswith('re:') or ' re:' in title
        
        return has_pattern and not is_reply
    
    def _detect_type(self, title: str) -> str:
        """检测邮件类型"""
        title_lower = title.lower()
        
        # Bugfix 检测
        bugfix_patterns = [
            'fix', 'bug', 'fixup', 'repair',
            'crash', 'oops', 'panic',
            'null pointer', 'memory leak',
            'use-after-free', 'data race',
        ]
        if any(p in title_lower for p in bugfix_patterns):
            return 'bugfix'
        
        # Performance 检测
        perf_patterns = [
            'perf', 'performance', 'optimize', 'optimization',
            'speed', 'faster', 'latency', 'throughput',
            'improve', 'boost', 'enhance',
        ]
        if any(p in title_lower for p in perf_patterns):
            return 'perf'
        
        # Feature 检测
        feature_patterns = [
            'add', 'introduce', 'implement', 'support',
            'new', 'enable', 'feature', 'add support for',
        ]
        if any(p in title_lower for p in feature_patterns):
            return 'feature'
        
        return 'other'
    
    def fetch_detail(self, url: str) -> str:
        """
        获取邮件详情内容
        
        Args:
            url: 邮件详情页URL
            
        Returns:
            邮件正文内容
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # LKML 详情页内容通常在 <pre> 标签中
            content_pre = soup.find('pre')
            if content_pre:
                return content_pre.get_text()
            
            return ""
            
        except Exception as e:
            logger.error(f"Failed to fetch detail {url}: {e}")
            return ""

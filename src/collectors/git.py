"""
Git 主线仓库收集器
"""
import logging
import os
import re
import tempfile
from datetime import datetime, timedelta
from typing import List, Dict

import git

logger = logging.getLogger(__name__)


class GitCollector:
    """Linux Git 主线仓库收集器"""
    
    REPO_URL = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
    
    def __init__(self, local_path: str = None):
        """
        初始化收集器
        
        Args:
            local_path: 本地仓库路径，如果不存在会自动克隆
        """
        if local_path:
            self.local_path = local_path
        else:
            # 使用临时目录
            self.local_path = os.path.join(tempfile.gettempdir(), 'linux.git')
        
        self.repo = None
        
    def _ensure_repo(self):
        """确保本地仓库存在（使用浅克隆加速）"""
        if os.path.exists(os.path.join(self.local_path, '.git')):
            logger.info(f"Using existing repo: {self.local_path}")
            self.repo = git.Repo(self.local_path)
            # 只获取最新提交，不拉取完整历史
            try:
                self.repo.remotes.origin.fetch(depth=100, verbose=False)
                logger.info("Repository updated (shallow fetch)")
            except Exception as e:
                logger.warning(f"Failed to update repo: {e}")
        else:
            logger.info(f"Cloning repo (shallow) to: {self.local_path}")
            os.makedirs(self.local_path, exist_ok=True)
            # 使用浅克隆，只下载最近100个提交
            self.repo = git.Repo.clone_from(
                self.REPO_URL, 
                self.local_path,
                depth=100,  # 只克隆最近100个提交
                no_single_branch=True,
                verbose=False
            )
            logger.info("Repository cloned (shallow)")
    
    def fetch(self, date_str: str, max_commits: int = 100) -> List[Dict]:
        """
        获取指定日期之后的提交
        
        Args:
            date_str: 日期字符串 YYYY-MM-DD
            max_commits: 最大提交数
            
        Returns:
            提交列表
        """
        self._ensure_repo()
        
        date = datetime.strptime(date_str, '%Y-%m-%d')
        since_date = date.strftime('%Y-%m-%d')
        
        logger.info(f"Fetching Git commits since {since_date}")
        
        try:
            # 获取提交列表
            commits = list(self.repo.iter_commits(
                'HEAD',
                since=since_date,
                no_merges=True,
                max_count=max_commits
            ))
            
            logger.info(f"Found {len(commits)} commits")
            
            # 解析提交信息
            results = []
            for commit in commits:
                commit_info = self._parse_commit(commit)
                if commit_info:
                    results.append(commit_info)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to fetch commits: {e}")
            return []
    
    def _parse_commit(self, commit) -> Dict:
        """解析单个提交"""
        try:
            # 获取提交信息
            message = commit.message.strip()
            title = message.split('\n')[0] if message else "No title"
            
            # 获取作者
            author = commit.author.name if commit.author else "Unknown"
            
            # 获取日期
            date = datetime.fromtimestamp(commit.committed_date)
            
            # 获取修改的文件
            files = []
            try:
                if commit.parents:
                    parent = commit.parents[0]
                    diff = parent.diff(commit)
                    files = [d.b_path for d in diff if d.b_path]
            except Exception as e:
                logger.warning(f"Failed to get diff for {commit.hexsha}: {e}")
            
            # 获取统计信息
            stats = {
                'additions': 0,
                'deletions': 0,
            }
            try:
                if commit.parents:
                    parent = commit.parents[0]
                    diff_stats = parent.diff(commit, create_patch=True)
                    for diff in diff_stats:
                        # 简单统计行数
                        if diff.diff:
                            diff_text = diff.diff.decode('utf-8', errors='ignore')
                            stats['additions'] += diff_text.count('\n+')
                            stats['deletions'] += diff_text.count('\n-')
            except Exception as e:
                logger.warning(f"Failed to get stats for {commit.hexsha}: {e}")
            
            # 生成 URL
            commit_url = f"https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id={commit.hexsha}"
            
            return {
                'source': 'Git Mainline',
                'title': title,
                'author': author,
                'date': date.strftime('%Y-%m-%d'),
                'url': commit_url,
                'commit_id': commit.hexsha[:12],
                'content': message,
                'files': files,
                'stats': stats,
                'type': self._detect_type(title, files),
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse commit: {e}")
            return None
    
    def _detect_type(self, title: str, files: List[str]) -> str:
        """检测提交类型"""
        title_lower = title.lower()
        
        # Bugfix 检测
        bugfix_patterns = [
            'fix', 'bug', 'fixup', 'repair', 'correct',
            'crash', 'oops', 'panic', 'error',
            'null pointer', 'memory leak', 'use-after-free',
            'data race', 'deadlock', 'syzbot',
        ]
        if any(p in title_lower for p in bugfix_patterns):
            return 'bugfix'
        
        # Performance 检测
        perf_patterns = [
            'perf', 'performance', 'optimize', 'optimization',
            'speed', 'faster', 'latency', 'throughput',
            'improve', 'boost', 'enhance', 'efficient',
            'reduce', 'accelerate', 'faster',
        ]
        if any(p in title_lower for p in perf_patterns):
            return 'perf'
        
        # Feature 检测
        feature_patterns = [
            'add', 'introduce', 'implement', 'support',
            'new', 'enable', 'feature', 'add support',
            'initial', 'provide', 'export', 'expose',
        ]
        if any(p in title_lower for p in feature_patterns):
            return 'feature'
        
        return 'other'
    
    def get_subsystem(self, files: List[str]) -> str:
        """
        根据文件路径判断子系统
        
        Args:
            files: 修改的文件列表
            
        Returns:
            子系统名称
        """
        # 子系统映射
        subsystem_map = {
            'kernel/sched/': 'Scheduler',
            'mm/': 'Memory',
            'fs/': 'Filesystem',
            'net/': 'Networking',
            'block/': 'IO',
            'kernel/bpf/': 'eBPF',
            'security/': 'Security',
            'virt/': 'Virtualization',
            'arch/x86/': 'x86 Architecture',
            'arch/arm64/': 'ARM64 Architecture',
            'drivers/nvme/': 'NVMe',
            'drivers/gpu/': 'Graphics',
        }
        
        for file in files:
            for prefix, subsystem in subsystem_map.items():
                if file.startswith(prefix):
                    return subsystem
        
        return 'Other'

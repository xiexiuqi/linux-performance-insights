"""
报告生成器
"""
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

from jinja2 import Template

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.reports_dir = Path('reports')
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_daily(self, date_str: str, items: List[Dict]) -> str:
        """
        生成日报
        
        Args:
            date_str: 日期 YYYY-MM-DD
            items: 处理后的数据列表
            
        Returns:
            报告文件路径
        """
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # 统计数据
        stats = self._calculate_stats(items)
        
        # 按类型分组
        groups = self._group_by_type(items)
        
        # 生成 Markdown
        content = self._render_daily_template(date_str, stats, groups)
        
        # 保存文件
        output_dir = self.reports_dir / 'daily'
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{date_str}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Daily report generated: {output_file}")
        return str(output_file)
    
    def generate_weekly(self, start_date: str, end_date: str) -> str:
        """
        生成周报
        
        Args:
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            
        Returns:
            报告文件路径
        """
        # TODO: 读取本周的所有日报并汇总
        content = f"""---
layout: default
title: "Linux性能周报 - {start_date} 至 {end_date}"
date: {end_date} 06:00:00 +0800
categories: [weekly]
---

# 📊 Linux性能周报

**周期**: {start_date} 至 {end_date}

## 本周概览

周报功能正在开发中...

## 详细内容

请查看每日日报：
"""
        
        # 列出本周的日报
        start = datetime.strptime(start_date, '%Y-%m-%d')
        for i in range(7):
            day = start + timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            content += f"- [{day_str}](/daily/{day_str}/)\n"
        
        # 保存文件
        output_dir = self.reports_dir / 'weekly'
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{start_date}-to-{end_date}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Weekly report generated: {output_file}")
        return str(output_file)
    
    def generate_kernel_analysis(self, version: str) -> str:
        """
        生成特定内核版本分析
        
        Args:
            version: 内核版本号（如 6.8）
            
        Returns:
            报告文件路径
        """
        content = f"""---
layout: default
title: "Linux {version} 内核性能分析报告"
date: {datetime.now().strftime('%Y-%m-%d')} 06:00:00 +0800
categories: [kernel-analysis]
tags: [{version}]
---

# 🐧 Linux {version} 内核性能分析报告

**版本**: {version}
**生成时间**: {datetime.now().strftime('%Y年%m月%d日')}

## 报告概述

内核版本分析功能正在开发中...

## 主要内容

- 新特性概览
- 性能优化详情
- Bug修复汇总
- 升级建议

---

*本报告由 Linux Performance Insights 自动生成*
"""
        
        # 保存文件
        output_dir = self.reports_dir / 'kernel-versions'
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"linux-{version}-analysis.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Kernel report generated: {output_file}")
        return str(output_file)
    
    def _calculate_stats(self, items: List[Dict]) -> Dict:
        """计算统计数据"""
        stats = {
            'total': len(items),
            'feature': 0,
            'bugfix': 0,
            'perf': 0,
            'other': 0
        }
        
        for item in items:
            item_type = item.get('type', 'other')
            stats[item_type] = stats.get(item_type, 0) + 1
        
        return stats
    
    def _group_by_type(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """按类型分组"""
        groups = {
            'feature': [],
            'bugfix': [],
            'perf': [],
            'other': []
        }
        
        for item in items:
            item_type = item.get('type', 'other')
            if item_type in groups:
                groups[item_type].append(item)
            else:
                groups['other'].append(item)
        
        return groups
    
    def _render_daily_template(self, date_str: str, stats: Dict, groups: Dict) -> str:
        """渲染日报模板"""
        
        template = Template("""---
layout: default
title: "Linux性能日报 - {{ date }}"
date: {{ date }} 06:00:00 +0800
categories: [daily]
generated_by: linux-performance-insights
---

# 📅 Linux性能日报 - {{ date }}

## 📊 今日概览

| 类型 | 数量 |
|------|------|
| 🚀 新特性 | {{ stats.feature }} |
| 🐛 Bug修复 | {{ stats.bugfix }} |
| ⚡ 性能优化 | {{ stats.perf }} |
| 📚 其他 | {{ stats.other }} |
| **总计** | **{{ stats.total }}** |

## 🎯 重点推荐

{% if groups.perf %}
### ⚡ 性能优化

{% for item in groups.perf[:5] %}
#### {{ loop.index }}. {{ item.title }}
**作者**: {{ item.author }}  
**来源**: {{ item.source }}  
**链接**: [查看详情]({{ item.url }})

**AI摘要**: {{ item.ai_summary }}

**标签**: {% for tag in item.ai_tags %}`{{ tag }}` {% endfor %}

---
{% endfor %}
{% endif %}

{% if groups.feature %}
### 🚀 新特性

{% for item in groups.feature[:5] %}
#### {{ loop.index }}. {{ item.title }}
**作者**: {{ item.author }}  
**来源**: {{ item.source }}  
**链接**: [查看详情]({{ item.url }})

**AI摘要**: {{ item.ai_summary }}

**标签**: {% for tag in item.ai_tags %}`{{ tag }}` {% endfor %}

---
{% endfor %}
{% endif %}

{% if groups.bugfix %}
### 🐛 Bug修复

{% for item in groups.bugfix[:5] %}
#### {{ loop.index }}. {{ item.title }}
**作者**: {{ item.author }}  
**来源**: {{ item.source }}  
**链接**: [查看详情]({{ item.url }})

**AI摘要**: {{ item.ai_summary }}

**标签**: {% for tag in item.ai_tags %}`{{ tag }}` {% endfor %}

---
{% endfor %}
{% endif %}

{% if groups.other %}
### 📚 其他更新

{% for item in groups.other[:3] %}
- **{{ item.title }}** - {{ item.author }} ([链接]({{ item.url }}))
{% endfor %}
{% endif %}

---

*本报告由 Linux Performance Insights 自动生成*  
*生成时间: {{ generation_time }}*
""")
        
        return template.render(
            date=date_str,
            stats=stats,
            groups=groups,
            generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

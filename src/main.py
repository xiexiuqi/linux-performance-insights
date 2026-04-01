"""
Linux Performance Insights - 主入口
"""
import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_daily_report(date_str: str):
    """生成日报"""
    logger.info(f"开始生成日报: {date_str}")
    
    # 导入收集器
    from src.collectors.lkml import LKMLCollector
    from src.collectors.git import GitCollector
    from src.processors.ai_summarizer import KimiSummarizer
    from src.processors.report_generator import ReportGenerator
    
    # 初始化组件
    summarizer = KimiSummarizer()
    report_gen = ReportGenerator()
    
    # 收集 LKML 数据
    logger.info("收集 LKML 数据...")
    lkml_collector = LKMLCollector()
    lkml_data = lkml_collector.fetch(date_str)
    logger.info(f"LKML 收集完成: {len(lkml_data)} 条")
    
    # 收集 Git 数据
    logger.info("收集 Git 数据...")
    git_collector = GitCollector()
    git_data = git_collector.fetch(date_str)
    logger.info(f"Git 收集完成: {len(git_data)} 条")
    
    # AI 摘要处理
    logger.info("生成 AI 摘要...")
    processed_data = summarizer.process_daily(lkml_data + git_data)
    
    # 生成报告
    logger.info("生成报告文件...")
    report_path = report_gen.generate_daily(date_str, processed_data)
    
    logger.info(f"日报生成完成: {report_path}")
    return report_path


def generate_weekly_report(date_str: str):
    """生成周报"""
    logger.info(f"开始生成周报: {date_str}")
    
    from src.processors.report_generator import ReportGenerator
    
    report_gen = ReportGenerator()
    
    # 获取本周日期范围
    date = datetime.strptime(date_str, '%Y-%m-%d')
    week_start = date - timedelta(days=date.weekday())
    week_end = week_start + timedelta(days=6)
    
    logger.info(f"周报范围: {week_start.date()} 至 {week_end.date()}")
    
    # 生成周报
    report_path = report_gen.generate_weekly(
        week_start.strftime('%Y-%m-%d'),
        week_end.strftime('%Y-%m-%d')
    )
    
    logger.info(f"周报生成完成: {report_path}")
    return report_path


def generate_kernel_report(version: str):
    """生成特定内核版本分析"""
    logger.info(f"开始生成内核 {version} 分析报告")
    
    from src.processors.report_generator import ReportGenerator
    
    report_gen = ReportGenerator()
    report_path = report_gen.generate_kernel_analysis(version)
    
    logger.info(f"内核报告生成完成: {report_path}")
    return report_path


def submit_to_website(report_paths: list):
    """提交报告到网站仓库"""
    logger.info(f"提交 {len(report_paths)} 个报告到网站")
    
    from src.exporters.website_pr import WebsitePR
    
    pr_creator = WebsitePR()
    pr_url = pr_creator.create_pr(report_paths)
    
    logger.info(f"PR 创建完成: {pr_url}")
    return pr_url


def main():
    parser = argparse.ArgumentParser(description='Linux Performance Insights')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'kernel'], required=True,
                       help='报告类型')
    parser.add_argument('--date', help='日期 (YYYY-MM-DD)，默认为昨天')
    parser.add_argument('--version', help='内核版本号 (用于 kernel 模式)')
    parser.add_argument('--submit', action='store_true',
                       help='自动提交到网站仓库')
    
    args = parser.parse_args()
    
    # 默认日期为昨天
    if not args.date:
        args.date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    report_paths = []
    
    try:
        if args.mode == 'daily':
            report_path = generate_daily_report(args.date)
            report_paths.append(report_path)
            
        elif args.mode == 'weekly':
            report_path = generate_weekly_report(args.date)
            report_paths.append(report_path)
            
        elif args.mode == 'kernel':
            if not args.version:
                logger.error("kernel 模式需要指定 --version 参数")
                sys.exit(1)
            report_path = generate_kernel_report(args.version)
            report_paths.append(report_path)
        
        # 提交到网站
        if args.submit and report_paths:
            submit_to_website(report_paths)
            
    except Exception as e:
        logger.exception("生成报告失败")
        sys.exit(1)


if __name__ == '__main__':
    main()

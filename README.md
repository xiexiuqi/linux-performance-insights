# Linux Performance Insights

自动化 Linux 内核性能信息收集与分析系统

## 功能特性

- 📧 **LKML 邮件列表监控** - 自动抓取 Linux Kernel Mailing List
- 🌿 **Git 提交分析** - 追踪主线内核提交
- 📰 **LWN 文章聚合** - 收集 Linux Weekly News
- 🤖 **AI 智能摘要** - 使用 Kimi API 生成中文摘要
- 📊 **自动化报告** - 生成日报、周报、月报
- 🚀 **自动部署** - 提交到 xiexiuqi.github.io

## 快速开始

### 环境要求

- Python 3.11+
- Git

### 安装依赖

```bash
pip install -r requirements.txt
```

### 本地运行

```bash
# 生成日报
python src/main.py --mode daily --date 2026-04-01

# 生成周报
python src/main.py --mode weekly --date 2026-04-01

# 生成特定版本分析
python src/main.py --mode kernel --version 6.8
```

## 项目结构

```
.
├── .github/
│   └── workflows/
│       ├── daily-collect.yml      # 每日定时收集
│       ├── weekly-report.yml      # 周报复盘
│       └── auto-merge.yml         # 自动合并PR
├── src/
│   ├── collectors/
│   │   ├── lkml.py               # LKML抓取
│   │   ├── git.py                # Git分析
│   │   └── lwn.py                # LWN抓取
│   ├── processors/
│   │   ├── ai_summarizer.py      # AI摘要（Kimi）
│   │   ├── classifier.py         # 标签分类
│   │   └── report_generator.py   # 报告生成
│   ├── exporters/
│   │   ├── markdown.py           # Markdown导出
│   │   └── website_pr.py         # 网站PR提交
│   └── main.py                   # 主入口
├── config/
│   └── sources.yaml              # 数据源配置
├── reports/                      # 生成的报告
└── requirements.txt
```

## 配置说明

### GitHub Secrets

需要在仓库设置中添加以下 Secrets：

- `KIMI_API_KEY` - Kimi API 密钥
- `WEBSITE_REPO_TOKEN` - 网站仓库访问令牌

### 数据源配置

编辑 `config/sources.yaml` 配置数据源：

```yaml
sources:
  lkml:
    enabled: true
    url: https://lkml.org/
    
  git_mainline:
    enabled: true
    repo: https://git.kernel.org/...
    
  lwn:
    enabled: true
    username: ${LWN_USERNAME}
    password: ${LWN_PASSWORD}
```

## 自动化流程

1. **每日 02:00** - 自动收集前一日数据，生成日报
2. **每周一 03:00** - 生成本周汇总周报
3. **每月1日 04:00** - 生成本月深度分析报告
4. **手动触发** - 支持生成特定内核版本分析

## 许可证

MIT License

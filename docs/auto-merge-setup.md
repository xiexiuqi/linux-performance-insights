# 自动合并配置说明

要实现从 `linux-performance-insights` 自动提交的报告能够自动合并到网站仓库，需要在 `xiexiuqi/xiexiuqi.github.io` 仓库中添加以下配置：

## 1. 在网站仓库中创建自动合并工作流

创建文件 `.github/workflows/auto-merge.yml`：

```yaml
name: Auto Merge Insights PRs

on:
  pull_request:
    types:
      - opened
      - synchronize
    branches:
      - main

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    # 只处理来自 insights 的自动化 PR
    if: |
      startsWith(github.head_ref, 'auto/insights') &&
      github.event.pull_request.user.login == 'xiexiuqi'
    
    steps:
      - name: Wait for checks
        uses: lewagon/wait-on-check-action@v1.3.1
        with:
          ref: ${{ github.event.pull_request.head.sha }}
          check-name: 'Build and Deploy'
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          wait-interval: 10

      - name: Auto-merge PR
        uses: pascalgn/automerge-action@v0.16.2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          MERGE_METHOD: "squash"
          MERGE_COMMIT_MESSAGE: "pull-request-title"
          MERGE_RETRY_SLEEP: "10000"
          MERGE_RETRY: "6"
```

## 2. 或者使用 GitHub 内置的自动合并功能

在网站仓库的设置中开启：

1. Settings → General → Pull Requests
2. 勾选 "Allow auto-merge"
3. 配置分支保护规则（可选）

## 3. 分支保护建议（可选）

如果希望确保质量，可以设置：

```yaml
# .github/workflows/build-check.yml
name: Build Check

on:
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true
      - name: Build site
        run: bundle exec jekyll build
```

这样自动合并会等待构建检查通过后再合并。

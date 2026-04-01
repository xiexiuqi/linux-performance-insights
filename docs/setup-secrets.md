# GitHub Secrets 配置指南

## 1. 配置 Kimi API Key

1. 访问 GitHub 仓库：`https://github.com/xiexiuqi/linux-performance-insights`
2. 点击 **Settings** 标签
3. 左侧菜单选择 **Secrets and variables** → **Actions**
4. 点击 **New repository secret**
5. 配置：
   - **Name**: `KIMI_API_KEY`
   - **Value**: `sk-4CXEwWe99aetOji8x8tIkh23hhhPrTnsidDZApUoeaNWaH86`
6. 点击 **Add secret**

## 2. 配置 Website 仓库 Token

### 步骤 A：生成 Personal Access Token

1. 访问 GitHub：**Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. 点击 **Generate new token (classic)**
3. 配置 Token：
   - **Note**: `Linux Performance Insights - Website Access`
   - **Expiration**: 选择有效期（建议 90 天）
   - **Scopes**: 勾选以下权限
     - `repo` (完整仓库访问)
     - `workflow` (如果需要触发 Actions)
4. 点击 **Generate token**
5. **复制 Token**（只显示一次！）

### 步骤 B：添加到 Secrets

1. 返回 `linux-performance-insights` 仓库
2. Settings → Secrets → Actions → New repository secret
3. 配置：
   - **Name**: `WEBSITE_REPO_TOKEN`
   - **Value**: 粘贴刚才复制的 Token
4. 点击 **Add secret**

## 3. 配置 LWN 凭据（可选）

如果需要抓取 LWN 付费内容：

1. 在 Secrets 中添加：
   - **Name**: `LWN_USERNAME`
   - **Value**: `xwhu`

2. 再添加一个：
   - **Name**: `LWN_PASSWORD`
   - **Value**: `sharedinhuawei`

## 4. 验证配置

配置完成后，可以在 GitHub Actions 中手动触发测试：

1. 进入仓库 **Actions** 标签
2. 选择 **Daily Performance Collection**
3. 点击 **Run workflow**
4. 观察运行日志，确认 Secrets 正确加载

## 5. 自动合并配置

要实现自动合并，需要在 `xiexiuqi/xiexiuqi.github.io` 仓库中添加配置。

### 方案 A：使用 GitHub 原生自动合并（推荐）

1. 访问 `xiexiuqi/xiexiuqi.github.io` 仓库
2. Settings → General → Pull Requests
3. 勾选 **Allow auto-merge**
4. （可选）配置分支保护规则

### 方案 B：创建自动合并工作流

在 `xiexiuqi/xiexiuqi.github.io` 仓库中创建 `.github/workflows/auto-merge.yml`：

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
    if: startsWith(github.head_ref, 'auto/insights')
    
    steps:
      - name: Auto-merge PR
        uses: pascalgn/automerge-action@v0.16.2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          MERGE_METHOD: "squash"
```

## 6. 安全提醒

⚠️ **重要安全提示**:
- API Key 和 Token 都存储在 GitHub Secrets 中，加密保护
- 不要在代码中硬编码任何密钥
- Token 过期后需要重新生成
- 如果发现密钥泄露，立即撤销并重新生成

## 7. 测试运行

配置完成后，手动触发一次测试：

```bash
# 在本地测试（可选）
cd /path/to/linux-performance-insights
export KIMI_API_KEY=sk-...
python src/main.py --mode daily --date 2026-04-01
```

或通过 GitHub Actions 页面手动触发工作流。

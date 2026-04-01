#!/bin/bash
# 配置 GitHub Secrets 脚本
# 使用方法: export GITHUB_TOKEN=ghp_... && ./scripts/setup-secrets.sh

set -e

REPO="xiexiuqi/linux-performance-insights"

echo "Setting up GitHub Secrets for $REPO..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Check if logged in
if ! gh auth status &> /dev/null; then
    echo "Please login to GitHub first: gh auth login"
    exit 1
fi

# Set secrets
if [ -n "$KIMI_API_KEY" ]; then
    echo "Setting KIMI_API_KEY..."
    gh secret set KIMI_API_KEY -b "$KIMI_API_KEY" -R "$REPO"
fi

if [ -n "$WEBSITE_REPO_TOKEN" ]; then
    echo "Setting WEBSITE_REPO_TOKEN..."
    gh secret set WEBSITE_REPO_TOKEN -b "$WEBSITE_REPO_TOKEN" -R "$REPO"
fi

if [ -n "$LWN_USERNAME" ]; then
    echo "Setting LWN_USERNAME..."
    gh secret set LWN_USERNAME -b "$LWN_USERNAME" -R "$REPO"
fi

if [ -n "$LWN_PASSWORD" ]; then
    echo "Setting LWN_PASSWORD..."
    gh secret set LWN_PASSWORD -b "$LWN_PASSWORD" -R "$REPO"
fi

echo "✅ Secrets configured successfully!"
echo ""
echo "Verify at: https://github.com/$REPO/settings/secrets/actions"

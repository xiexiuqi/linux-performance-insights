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
#!/bin/bash
# git_sync.sh — 每日自動同步 Obsidian Vault 到 GitHub
# cron: 23:05 每天執行
# .git 放在 Desktop/Claude（不在 iCloud），vault 是 work-tree

GIT_DIR="/mnt/c/Users/崇瑋/Desktop/Claude/.git"
WORK_TREE="/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
DATE=$(date +%Y-%m-%d)
LOG="/tmp/git-sync.log"

echo "[${DATE} $(date +%H:%M:%S)] [cron] git_sync.sh 開始" >> "$LOG"

# 確認有無變更
if git --git-dir="$GIT_DIR" --work-tree="$WORK_TREE" diff --quiet && \
   git --git-dir="$GIT_DIR" --work-tree="$WORK_TREE" diff --staged --quiet && \
   [ -z "$(git --git-dir="$GIT_DIR" --work-tree="$WORK_TREE" ls-files --others --exclude-standard)" ]; then
    echo "[${DATE}] 沒有變更，跳過 commit" >> "$LOG"
    exit 0
fi

# Commit + Push
git --git-dir="$GIT_DIR" --work-tree="$WORK_TREE" add -A
git --git-dir="$GIT_DIR" --work-tree="$WORK_TREE" commit -m "auto: daily sync ${DATE}"
git --git-dir="$GIT_DIR" --work-tree="$WORK_TREE" push origin main >> "$LOG" 2>&1

echo "[${DATE}] Git sync 完成" >> "$LOG"

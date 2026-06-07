#!/bin/bash
# git_sync.sh — 每日自動同步 Obsidian Vault 到 GitHub
# cron: 23:05 每天執行（daily_note.py 結束後）

VAULT="/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
DATE=$(date +%Y-%m-%d)
LOG="/tmp/git-sync.log"

echo "[${DATE} $(date +%H:%M:%S)] git_sync.sh 開始" >> "$LOG"

cd "$VAULT" || { echo "找不到 Vault 路徑" >> "$LOG"; exit 1; }

# 確認有無變更
if git diff --quiet && git diff --staged --quiet && \
   [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo "[${DATE}] 沒有變更，跳過 commit" >> "$LOG"
    exit 0
fi

# Commit + Push
git add -A
git commit -m "auto: daily sync ${DATE}"
git push origin main >> "$LOG" 2>&1

echo "[${DATE}] Git sync 完成" >> "$LOG"

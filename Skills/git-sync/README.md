> 隸屬於 [[Skills/instructions|Skills]]

每天晚上 23:05 自動將 Vault 變更 commit 並推送到 GitHub。
接在 daily_note.py（23:00）之後執行，確保 Daily Note 已寫入再同步。

---

## 架構

```
Skills/git-sync/
├── git_sync.sh  ← 主腳本
└── README.md    ← 本檔案
```

**流程：**
```
cron (23:05) → git_sync.sh → git diff（有變更？）
                            → 有：git add -A → commit → push
                            → 無：跳過
```

---

## 注意事項

- 沒有變更時自動跳過，不產生空 commit
- commit message 格式：`auto: daily sync YYYY-MM-DD`
- 執行紀錄：`/tmp/git-sync.log`

---

## 手動執行

```bash
bash /mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian/Skills/git-sync/git_sync.sh
cat /tmp/git-sync.log
```

---

## 相關連結

- [[Skills/daily-note/README|daily-note（上游，23:00）]]

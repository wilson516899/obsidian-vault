> 隸屬於 [[Obsidian/Skills/instructions|Skills]]

每天晚上 23:05 自動將 Vault 變更 commit 並推送到 GitHub。

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
                            → 有：git add -A → commit → push origin main
                            → 無：跳過
```

---

## 注意事項

- 沒有變更時自動跳過，不產生空 commit
- commit message 格式：`auto: daily sync YYYY-MM-DD`
- 執行紀錄：`/tmp/git-sync.log`
- GitHub repo：`wilson516899/obsidian-vault`（private）

---

## 手動執行

```bash
bash /mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian/Skills/git-sync/git_sync.sh
cat /tmp/git-sync.log
```

---

## 相關連結

- [[Skills/claude-note/README|claude-note（同夜 23:00 產出）]]

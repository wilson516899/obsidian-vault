> 隸屬於 [[CLAUDE]]

需要執行某項任務時，從下方找到對應 skill，讀其 README.md 後再操作。

---

## 自動化腳本型（資料夾 + 腳本）

| Skill | 說明 | 觸發 |
|-------|------|------|
| [[Skills/claude-note/README\|claude-note]] | Claude 工作紀錄自動產生 | cron 23:00，每日 |
| [[Skills/quest-system/README\|quest-system]] | 修煉積分結算與進度追蹤 | cron 07:55，每日 |
| [[Skills/daily-notify/README\|daily-notify]] | 每日代辦 + 新聞簡報產生 | cron 08:00，每日 |
| [[Skills/book-fill/README\|book-fill]] | 書摘 + 小說任務推薦 | cron 08:05，每週一 |
| [[Skills/budget-import/README\|budget-import]] | 匯入 Budget App 記帳資料到 記帳/ 資料夾 | 手動，建議每月 1 號 |
| [[Skills/git-sync/README\|git-sync]] | Vault 變更自動 commit + push 到 GitHub | cron 23:05，每日 |
| budget-import | 匯入 Budget App 記帳資料到 記帳/ 資料夾（腳本在 `C:\Users\崇瑋\Desktop\Claude\budget-import\`） | 手動，建議每月 1 號 |

## 行為指令型（對話中執行）

| Skill | 說明 | 觸發 |
|-------|------|------|
| [[Skills/save-to-obsidian/README\|save-to-obsidian]] | 判斷內容存放位置並寫入 Vault | 使用者說「存到 Obsidian」 |


---

## 新增 Skill 規範

1. 在 `Skills/` 下建立新資料夾 `Skills/xxx/`
2. 建立 `Skills/xxx/README.md`，內容包含：用途、觸發方式、關鍵檔案、調用時機、注意事項
3. 在本檔案（instructions.md）加入索引
4. 若有 cron 排程，同步更新 `CLAUDE.md`

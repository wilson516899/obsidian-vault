> 隸屬於 [[Skills/instructions|Skills]]

每天晚上 23:00 自動執行，根據當天 Daily Note 的勾選狀況與積分進度，
產生 Claude 工作紀錄，供隔天 notify.py 作為上下文使用。

---

## 架構

```
Skills/claude-note/
├── daily_note.py  ← 主腳本
└── README.md      ← 本檔案
```

**流程：**
```
cron (23:00) → daily_note.py → ① 書籍狀態同步（每天都執行）
                                    掃描 圖書館/*.md
                                    YAML 狀態/日期 → 同步至 blockquote
                              → ② Claude Note 產生
                                    若 Claude Note/{TODAY}.md 已存在 → 跳過
                                    否則 → 讀 Daily Note/{TODAY}.md checkbox
                                         → 讀 progress.json
                                         → 產生工作紀錄 → 寫入
```

---

## 調用時機

| 情境 | 動作 |
|------|------|
| 對話中手動記錄今日工作 | 直接寫 `Claude Note/{YYYY-MM-DD}.md`；23:00 腳本自動跳過 |
| 查看某天 Claude 做了什麼 | 讀 `Claude Note/{YYYY-MM-DD}.md` |
| 調整產生格式 | 編輯 `daily_note.py` 的 `build_note()` 函式 |

---

## Claude Note 格式

記錄 Claude 協助完成的工作（**不是個人日記**）：

```markdown
# YYYY-MM-DD（星期X）

## 今日完成事項

### 主題一
- 做了什麼、改了哪些檔案、結果如何

## 進行中

- ⏳ 尚未完成的項目與下一步
```

**原則：**
- 具體記錄：寫清楚改了哪些路徑、結果如何
- 架構變動一定要記（資料夾搬移、改名）
- 不記使用者的私人日記內容

---

## 注意事項

- **不覆蓋**：當天 Claude Note 已存在時腳本跳過，手動寫的優先
- 日期以**對話發生當天**為準，非凌晨跨日後的隔日
- 自動產生版以任務完成狀況為主，不包含對話細節

### 附加：書籍狀態同步

每次執行時**一律掃描** `圖書館/*.md`，不受 Claude Note 是否已存在影響。

---

## 手動執行

```bash
python3 /mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian/Skills/claude-note/daily_note.py
cat /tmp/daily-note.log
```

---

## 相關連結

- [[Daily Note/|Daily Note（輸入來源）]]
- [[Skills/quest-system/README|quest-system（積分資料來源）]]
- [[Skills/daily-notify/README|daily-notify（下游消費者）]]

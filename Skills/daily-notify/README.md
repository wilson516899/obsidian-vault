> 隸屬於 [[Obsidian/Skills/instructions|Skills]]

每天早上 08:00 自動執行，產生當天的 Daily Note，寫入任務清單、修煉進度、新聞簡報。
每月 1 號 08:10 額外執行月報打包，將上個月的每日檔歸檔。

---

## 架構

```
Skills/daily-notify/
├── notify.py         ← 每日 Daily Note 產生
├── month_archive.py  ← 每月月報打包 + 歸檔
└── README.md         ← 本檔案
```

**每日流程（08:00）：**
```
cron (08:00) → notify.py → 讀 Daily Note/ 最近 7 天（只擷取 checkbox + 隨手記）
                         → 讀 靈感筆記/2026年計畫.md + 靈感筆記/*.md
                         → 讀 progress.json（修煉積分）
                         → 抓 RSS 新聞候選
                         → Claude API 篩選新聞 + 產出今日推薦
                         → 寫入 Daily Note/YYYY-MM-DD.md
```

**每月流程（每月 1 號 08:10）：**
```
cron (08:10, 每月1號) → month_archive.py → 統計上個月 checkbox 完成率
                                         → 整理體重紀錄 + 隨手記
                                         → 產生 Daily Note/YYYY-MM/YYYY-MM 月份彙整.md
```
> 注意：日報本身在產出時就已寫入 `Daily Note/YYYY-MM/` 子資料夾，month_archive.py 不做移檔。

---

## 輸出格式

**Daily Note（每日）**
```
# YYYY-MM-DD（星期X）
修煉進度條
## ⚡ 今日修煉任務（checkbox）
## 每日簡報（代辦推薦 + 新聞）
## 隨手記
```

**月份彙整（每月 1 號產出，放在同月資料夾）**
```
# YYYY-MM 月份彙整
## 📊 本月快照      ← 有任務天數、空白天數、累積積分、月初/月底體重
## ✅ 任務完成次數  ← 各任務完成次數 + 應有次數（依任務類型自動計算）
## ⚖️ 體重紀錄     ← 每次記錄體重的日期與數值
## 📝 隨手記       ← 各日的隨手記區塊彙整
```

---

## 調用時機

| 情境 | 動作 |
|------|------|
| 確認今天任務 | 開 `Daily Note/YYYY-MM-DD.md` |
| 查看某月統計 | 開 `Daily Note/YYYY-MM/YYYY-MM 月份彙整.md` |
| 新聞沒有顯示 / 格式錯誤 | 手動執行 notify.py，查看 log |
| 修改任務清單或新聞來源 | 編輯 `notify.py` 的 `build_quest_section()` 或 `NEWS_SOURCES` |

---

## 手動執行

```bash
# 每日 Daily Note
python3 /mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian/Skills/daily-notify/notify.py
cat /tmp/daily-notify.log

# 月報打包（手動觸發上個月）
python3 /mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian/Skills/daily-notify/month_archive.py
cat /tmp/month-archive.log
```

---

## 相關連結

- [[Daily Note/|Daily Note（輸出目標）]]
- [[Skills/quest-system/README|quest-system（積分資料來源）]]
- [[靈感筆記/2026年計畫|2026年計畫（上下文來源）]]

> 隸屬於 [[Skills/instructions|Skills]]

每天早上 07:55 自動結算昨日任務完成狀況，計算積分與連擊，更新進度紀錄。
詳細規則與設計邏輯見 [[Skills/quest-system/PRD|PRD]]。

---

## 架構

```
Skills/quest-system/
├── quest.py        ← 主腳本（每日結算）
├── progress.json   ← 積分狀態資料（機器讀寫）
├── 修煉進度.md      ← 人類可讀進度頁（自動覆寫）
├── PRD.md          ← 系統設計文件
└── README.md       ← 本檔案
```

**流程：**
```
cron (07:55) → quest.py → 讀取今日代辦.md checkbox
                        → 計算積分 + 連擊加成
                        → 寫入 progress.json
                        → 覆寫 修煉進度.md
```

---

## 調用時機

| 情境 | 動作 |
|------|------|
| 查詢目前積分 / 進度 | 讀 `progress.json` 或 `修煉進度.md` |
| 修改積分規則 | 讀 `PRD.md` → 再讀 `quest.py` 修改 |
| 手動補分 / 修正資料 | 直接編輯 `progress.json`，再手動執行 `quest.py` 更新 `修煉進度.md` |
| 查看里程碑定義 | 讀 `PRD.md` 或 `quest.py` 的 `MILESTONES` 常數 |

---

## 積分結構（快查）

- **基礎任務**：各任務標記 `` `+N` ``，直接加總
- **連擊加成**：streak × 2，上限 30 pt
- **週任務去重**：找團 / 揪人 / 寫作，同週只計一次
- **里程碑**：一次性大額加分（見 PRD）

---

## 手動執行

```bash
python3 /mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian/Skills/quest-system/quest.py
```

查看執行紀錄：
```bash
cat /tmp/quest.log
```

---

## 相關連結

- [[Skills/quest-system/PRD|積分系統 PRD]]
- [[Skills/quest-system/修煉進度|修煉進度（目前狀態）]]
- [[今日代辦|今日代辦（輸入來源）]]

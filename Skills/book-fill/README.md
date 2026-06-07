> 隸屬於 [[Obsidian/Skills/instructions|Skills]]

每週一早上 08:05 自動執行，從圖書館挑一本尚未填寫書摘的書，
同時抓取小說當前章節，寫入本週任務檔，供 notify.py 每天帶入 Daily Note。

---

## 架構

```
Skills/book-fill/
├── book_fill.py  ← 主腳本
├── 本週任務.md   ← 本週書摘 + 小說任務（notify.py 讀取）
└── README.md     ← 本檔案
```

**流程：**
```
cron (08:05，每週一) → book_fill.py → 掃描 圖書館/*.md
                                    → 找出 # 大綱 < 30 字的書
                                    → 隨機選一本
                                    → 讀 創作小說/大綱.md 取得章節
                                    → 寫入 Skills/book-fill/本週任務.md

每天 08:00  notify.py → 讀 本週任務.md → 帶入 Daily Note/YYYY-MM-DD.md
```

---

## 調用時機

| 情境 | 動作 |
|------|------|
| 了解本週書摘任務 | 讀 `Skills/book-fill/本週任務.md` |
| 修改觸發條件（如 < 30 字） | 編輯 `book_fill.py` 的 `has_no_notes()` 函式 |
| 手動觸發 | 執行腳本（腳本有星期判斷，非週一需暫時修改） |

---

## 注意事項

- 腳本**不自動填寫**書摘，只推薦要填哪本
- 每週一才執行；其他日執行會印提示後直接退出
- 圖書館的 `instructions.md` 會被跳過（不列入推薦）

---

## 手動執行

```bash
python3 /mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian/Skills/book-fill/book_fill.py
```

---

## 相關連結

- [[Daily Note/|Daily Note（最終輸出）]]
- [[圖書館/|圖書館（掃描來源）]]
- [[創作小說/大綱|小說大綱（章節來源）]]

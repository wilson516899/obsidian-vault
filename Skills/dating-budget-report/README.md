> 隸屬於 [[Obsidian/Skills/skills-index|Skills]]

把約會記帳 App 匯出的分帳 CSV，轉成月度分類分析 + 給女朋友看的視覺化 PDF 月報。
產出位置：`C:\Users\崇瑋\Desktop\約會記帳\`（跟 `家庭記帳/` 是分開的兩條線，不要混在一起）。

---

## 架構

```
Skills/dating-budget-report/
├── build_excel.py      ← Step 1：CSV → 分類 → 偵測代墊 → Excel
├── build_pdf.py        ← Step 2：Excel明細 → 內部暫時 html → 量高度 → PDF（html 不留檔）
├── category_rules.py   ← 分類關鍵字規則 + 已知類別的顏色/emoji
├── photo_map.json       ← 「項目描述」→ photos/ 底下的真實照片檔名
├── photos/              ← 已查證過的真實地點/店家照片（壓縮過，<100KB/張）
└── README.md            ← 本檔案
```

**完整流程：**
```
使用者貼新的匯出 CSV 連結/路徑
  → build_excel.py <csv路徑>
      → 解析「付款者/應分攤」兩列一組的結構，取總金額（不管誰付、怎麼分攤）
      → 比對應分攤欄位：兩邊都有值＝對半分攤；只有一邊有值＝代墊款（標記但金額仍計入）
      → 跳過「還款者/收款者」結算列（那是清債，不是消費）
      → 讀舊 Excel 的「明細」分頁，用(月份,項目描述,金額)比對
        → 舊交易沿用使用者手動修正過的類別
        → 新交易才用 category_rules.py 的關鍵字規則分類
      → 寫出 約會開銷月度分析.xlsx（月度總覽/類別總覽/明細/趨勢圖）
      → 印出：哪些被分到「其他」待覆核、哪些是代墊款、有沒有不認識的新類別

【使用者在 Excel 的「明細」分頁手動修正類別，存檔】

  → 跟 Claude 說「改完了」
  → 重新執行 build_excel.py（同一份 csv 或新一批都可以）確認修正有被保留

  → build_pdf.py
      → 讀 Excel「明細」分頁（含代墊備註）
      → 每個月渲染一份內部暫存 html（總額/佔比、🏆本月最大一筆、分類甜甜圈圖+橫條圖、近6月趨勢）
      → 「本月最大一筆」如果 photo_map.json 有對應照片 → 內嵌真實照片；沒有 → 用 emoji
      → 用 headless Edge 實測每份 html 的真實內容高度，設成對應的 PDF 頁面大小（避免內容被切頁）
      → 合併成一份多頁 PDF，一頁一個月
      → 暫存 html 用完即刪，只留最終 PDF
```

---

## 調用時機

| 情境 | 動作 |
|------|------|
| 拿到新一批約會帳本匯出連結 | `python3 build_excel.py <csv路徑>` |
| Excel 跑完後想人工修正分類 | 打開 `約會開銷月度分析.xlsx` 的「明細」分頁改「類別」欄，存檔後跟 Claude 說一聲 |
| 確認分類沒問題，要出最終報告 | `python3 build_pdf.py` |
| 「本月最大一筆」想換成真實照片 | 上網查證該項目實際對應的店家/地點，下載照片存到 `photos/`，在 `photo_map.json` 補一筆「項目描述」→檔名 |
| 跑出「未知類別」提醒 | 到 `category_rules.py` 補上 `CAT_COLOR` / `CAT_EMOJI` |

---

## 手動執行

```bash
python3 "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian/Skills/dating-budget-report/build_excel.py" "<原始csv路徑>"
# ...人工修正 Excel 明細分頁...
python3 "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian/Skills/dating-budget-report/build_pdf.py"
```

輸出都在 `C:\Users\崇瑋\Desktop\約會記帳\`：
- `約會開銷月度分析.xlsx`（資料來源，可人工修正）
- `約會開銷_月報.pdf`（最終要傳給女朋友的檔案，一頁一個月）
- `原始匯出/`（過去每次貼過來的原始 CSV 存檔，方便回頭查）

---

## 注意事項

- **觸發方式是手動的**，不是 cron：匯出連結是 App 當次產生的，不是固定網址，沒辦法排程自動抓
- 「代墊款」的判定邏輯是看原始 CSV 裡「應分攤」那一列兩欄金額：只有一邊有值＝代墊（全額算一個人），不是真的共同開銷，但這份報告的理念是「金額不變，只標記」，不會因為是代墊就從總額剔除
- `build_excel.py` 的分類合併邏輯**以舊 Excel 明細為準**，所以人工修正過的分類（包含使用者自己取名的新類別，例如「瑟瑟」）永遠不會被關鍵字規則蓋掉
- `photos/` 裡的照片都是真實店家/景點的公開照片（官網、部落格、維基），壓縮到 100KB 內用於私人分享，**不建議公開發布**（版權只限私下給女朋友看）
- html 只是 `build_pdf.py` 內部拿來印 PDF 用的中間產物，執行完會自動刪除，不會留在任何資料夾裡

---

## 相關連結

- 跟 `家庭記帳/bill_grab.py`（富邦銀行帳單）、`Skills/budget-import`（Budget App 記帳）是三條互相獨立的記帳線，邏輯跟資料來源都不同，不要混用

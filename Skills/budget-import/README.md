# Budget Import Skill

## 用途
將 LightByte Budget iOS App 的記帳資料匯入 Obsidian，每月自動生成 `記帳/YYYY-MM.md` 記帳報告。

## 觸發方式
- **手動**：使用者說「更新記帳」、「匯入記帳」、「幫我看這個月花了多少」
- **建議排程**：每月 1 號自動執行（目前尚未設 cron，需手動觸發）

## 關鍵檔案

| 檔案 | 說明 |
|------|------|
| `budget_import.py` | 主程式：找備份→解壓→呼叫 Node.js→產生 MD |
| `budget_reader.mjs` | Node.js Realm 讀取器：輸出 JSON 到 stdout |
| `node_modules/` | Realm JS SDK（`npm install realm` 安裝） |
| `package.json` | Node.js 依賴定義 |

## 資料來源
- **App**：LightByte Budget（iOS）
- **備份位置**：`C:\Users\崇瑋\iCloudDrive\iCloud~com~lightByte~Budget\emergency\`
- **格式**：每個備份是 `{unix_timestamp}.zip`，內含 `Budget.realm`
- **自動備份**：App 每天自動備份，保留最近幾天

## 輸出格式
- **位置**：`Obsidian/記帳/YYYY-MM.md`
- **內容**：月份總覽（各分類支出）+ 支出明細（按分類）+ 收入明細

## 執行方式

```bash
# 只更新當前月份和上個月（預設）
python3 Skills/budget-import/budget_import.py

# 更新指定月份
python3 Skills/budget-import/budget_import.py --month 2026-05

# 重新生成所有月份（歷史資料完整匯入）
python3 Skills/budget-import/budget_import.py --all
```

## 注意事項
1. 需要 Node.js（`node --version` 確認）
2. `node_modules/` 已包含在 skill 目錄內，不需要額外安裝
3. Budget.realm 是 Realm Core 格式，**不能用 Python 直接讀取**，必須透過 Node.js Realm SDK
4. 資料限制：備份只包含 App 內最近 N 筆資料（目前約 61 筆），**無法取得更早的歷史記帳**
5. 每次匯入都覆蓋同月份的既有筆記（非累加）

## 調用時機
- 使用者問「這個月花了多少」→ 先執行匯入再讀取
- 使用者說「幫我更新記帳」→ 直接執行
- 月初（1-5號）使用者提到記帳 → 建議順便執行上月匯入

## Schema 說明（Expend 物件）

| 欄位 | 說明 |
|------|------|
| `date` | 日期（YYYY-MM-DD） |
| `classify` | 大分類（餐飲、交通、娛樂等） |
| `subcategory` | 子分類（午餐、捷運等） |
| `isIncome` | 是否為收入 |
| `amount` | 金額（台幣） |
| `remark` | 備註 |

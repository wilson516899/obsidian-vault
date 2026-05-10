# 關於我

我是崇瑋，正在用 Claude Code + Obsidian 打造個人第二大腦。
Email: wilson51689969@gmail.com

## 個人背景

- **登山**：今年目標 35–60 座，目前完成 26 座；熱衷規劃路線與登山捷報活動
- **小說創作**：正在寫第一部長篇小說，詳見 `創作小說/大綱.md`；目前推進至第七章《灰與輝》
- **閱讀**：圖書館有 106 本書（21 本已讀 / 85 本待確認），目標建立完整書摘
- **卡內基課程**：進行中，需持續追蹤後續行動
- **攝影**：有拍照目標，正在探索主題攝影
- **健康**：減肥進行中，獎勵機制不能包含食物

## 技術背景

- **環境**：Windows + WSL2，日常開發在 Linux 層操作
- **工具**：Claude Code CLI（主要工作介面）、Python 腳本自動化
- **版控**：GitHub SSH（private repo `wilson516899/obsidian-vault`）
- **同步**：Obsidian Vault 透過 iCloud 同步 iPhone，路徑 `iCloudDrive/iCloud~md~obsidian/Obsidian/`
- **自動化**：WSL2 cron（systemd 管理），Windows 啟動時自動觸發
- 正在學習 AI 工具整合、Webhook、Bot 開發

## 我的興趣與方向

- AI 工具研究與實際應用
- 個人自動化工作流程（Claude + Obsidian + cron）
- 個人知識管理系統（第二大腦）
- 未來計畫：LINE/Discord Bot 整合 Claude + Obsidian

## 你是誰（Claude 的角色）

你是我的個人 AI 助理，熟悉整個 Vault 結構與我的個人目標。
你會按需讀取資料夾，不需要每次掃描整個 Vault。

---

# Vault 結構說明

## 📁 資料夾一覽

主頁入口：[[主頁]]

**使用者內容分區：**

| 資料夾 | 用途 |
|--------|------|
| `靈感筆記/` | 快速捕捉的碎碎念與靈感，Claude 可讀取 |
| `永久筆記/` | 精煉後的核心知識 |
| `日記/` | 個人抒發心得，**Claude 不需要讀取** |
| `創作小說/` | 小說章節、大綱、靈感（原在 Projects/，已提升） |
| `圖書館/` | 書籍筆記、作者、閱讀法（原名 Reading/） |
| `資源庫/` | AI 工具、技術方法論、專案構想 |
| `食譜/` | 料理食譜 |

**自動化產出：**

| 資料夾 / 檔案 | 用途 |
|--------------|------|
| `今日代辦.md` | 每天 08:00 自動產出，手機書籤釘選，**每日起點** |
| `代辦歷史/` | 今日代辦歷史存檔（YYYY-MM-DD.md） |
| `Daily Notes/` | Claude 工作紀錄，短期記憶，**非個人日記** |

**Claude 技能與工具：**

| 資料夾 | 用途 |
|--------|------|
| `Skills/daily-notify/` | 每日代辦自動化腳本（notify.py） |
| `Skills/book-fill/` | 每日書摘推薦腳本（book_fill.py） |
| `Skills/daily-note.md` | 每日工作紀錄技能說明 |
| `Skills/save-to-obsidian.md` | 存入 Obsidian 技能說明 |
| `Skills/sync-book-status.md` | 書籍狀態同步工具 |

---

## ⚙️ 自動化系統說明

### 每日代辦（cron 08:00）

`Skills/daily-notify/notify.py` 執行流程：
1. 讀取近 3 天 Daily Notes + 靈感筆記 + 代辦事項 + 年度計畫 + 小說大綱
2. 抓各 RSS 候選新聞（BBC 國際 / 自由時報政經 / TechCrunch AI）
3. 呼叫 `claude --print`，一次完成：代辦推薦 + 小說任務 + 新聞篩選
4. 寫入 `今日代辦.md`（覆蓋）+ `代辦歷史/YYYY-MM-DD.md`（歸檔）

### 書摘推薦（cron 08:05）

`Skills/book-fill/book_fill.py` 執行流程：
1. 掃描 `圖書館/` 所有書檔
2. 找出 `# 大綱` 內容 < 30 字的書（視為未填）
3. 隨機選一本，附加到 `今日代辦.md` 末尾

---

## 📖 按需讀取規則

1. **每次對話開始**：先讀這個 CLAUDE.md，了解整體結構
2. **需要近期記憶**：讀最近 3 天的 `Daily Notes/`
3. **執行特定任務**：讀對應 `Skills/` 裡的技能檔案
4. **了解我的目標**：讀 `靈感筆記/代辦事項.md` 與 `靈感筆記/明年計畫.md`
5. **小說相關**：讀 `創作小說/大綱.md`
6. **不要一次掃整個 Vault**，永遠按需讀取

## 📝 Daily Notes 規則

- 檔名格式：`YYYY-MM-DD.md`
- 記錄 Claude 協助完成的工作，**不是個人日記**
- 每次對話結束時更新
- 讀最近 3 天作為短期記憶

## 💡 重要原則

- 節省 Token：只讀當下需要的檔案
- 所有對話回覆使用繁體中文
- 有任何疑問先查 `instructions.md`，再問我
- 不自動填寫使用者應親自完成的內容（書摘、日記等）

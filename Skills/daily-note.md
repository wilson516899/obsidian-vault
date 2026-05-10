# 技能：每日筆記管理

> 隸屬於 [[CLAUDE]] · [[Skills/instructions|Skills 說明]]

## 兩種模式

| 模式 | 觸發方式 | 執行者 |
|------|----------|--------|
| **自動模式** | 每天早上 8:00 cron 排程 | `notify.py` 腳本 |
| **手動模式** | Claude Code 對話開始/結束 | Claude（本技能） |

---

## 自動模式（cron 每日早上 8:00）

由 `Projects/daily-notify/notify.py` 執行，詳見 [[Projects/daily-notify/README|daily-notify README]]。

### 自動模式流程

1. 讀取昨日 Daily Note、代辦事項.md、創作小說/大綱.md
2. 呼叫 Claude API 生成今日重點摘要（繁體中文，≤250 字）
3. 寫入 `Daily Notes/YYYY-MM-DD.md`，插入 `## 📋 今日任務` 區塊
4. 透過 LINE Notify 推播到手機

### 自動生成的模板（新日期）

```markdown
# YYYY-MM-DD 每日紀錄

> 隸屬於 [[CLAUDE]] · 技能：[[Skills/daily-note|每日筆記]]

## 📋 今日任務

（Claude API 生成的每日重點）

---

## 今日完成事項

## 進行中的計畫

## 備註
```

---

## 手動模式（Claude Code 對話）

### 觸發時機

- 每天開始新的 Claude Code session
- 使用者說「更新今天的筆記」或「記錄今天做了什麼」
- 對話結束前整理當天進度

### 執行步驟

#### 建立當天 Daily Note（若不存在且自動模式未執行）

1. 確認今天日期（格式：YYYY-MM-DD）
2. 在 `Daily Notes/` 建立 `YYYY-MM-DD.md`，使用上方模板（不含 📋 今日任務區塊）

#### 更新當天 Daily Note

1. 讀取今天的 Daily Note
2. 在「今日完成事項」補上已完成的工作，分小節（### ）區分主題
3. 在「進行中的計畫」記錄尚未完成的項目與下一步
4. **不要覆蓋** `## 📋 今日任務` 區塊（由自動模式寫入）

#### 讀取近期記憶

- 每次對話開始時讀最近 3 天的 Daily Notes 作為上下文
- 不需要讀更早的筆記

---

## 注意事項

- 記錄要具體：寫清楚做了什麼、改了哪些路徑、結果如何
- 架構變動（資料夾搬移、改名）一定要記，方便下次對話還原脈絡
- 不要記使用者的日記或私人內容

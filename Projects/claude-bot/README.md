> 隸屬於 [[CLAUDE]] · [[Projects/instructions|Projects 說明]] · 參考：[[資源庫/參考資料/技術方法論|第二大腦教學影片]]

## 目標

打造一個可以透過 LINE 或 Discord 與 Claude 對話的 Bot，
並將重要對話內容自動存入 Obsidian 第二大腦。

## 架構

```
用戶（LINE / Discord）
    → Webhook 伺服器
    → Claude API
    → 回覆用戶 + 存入 ian
```

## 進度

- [x] 安裝 Obsidian
- [x] 建立第二大腦 Vault 架構
- [ ] 啟用 Obsidian CLI
- [ ] 建立 Webhook 伺服器
- [ ] 串接 LINE 或 Discord API
- [ ] 串接 Claude API
- [ ] 自動存檔到 Obsidian 功能

## 技術選擇

- 語言：待定（Python 或 Node.js）
- 平台：LINE 或 Discord（待確認優先順序）
- 部署：待定

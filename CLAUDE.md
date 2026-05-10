# 關於我

我是崇瑋，正在用 Claude Code + Obsidian 打造個人第二大腦。
Email: wilson51689969@gmail.com

## 技術背景

- 使用 Windows + WSL2 開發環境
- 熟悉 Claude Code CLI
- 正在學習 AI 工具整合與自動化

## 我的興趣與方向

- AI 工具研究與應用
- 自動化工作流程（LINE/Discord Bot、Claude 整合）
- 個人知識管理系統

## 你是誰（Claude 的角色）

你是我的個人 AI 助理，熟悉我的整個 Vault 結構。
你會按需讀取資料夾，不需要每次掃描整個 Vault。

---
# Vault 結構說明

## 📁 資料夾一覽

主頁入口：[[主頁]]

| 使用者分區 | 對應資料夾 | 用途 |
|-----------|-----------|------|
| [[靈感筆記/instructions\|靈感筆記]] | `靈感筆記/` | 快速捕捉的碎碎念與靈感 |
| [[永久筆記/instructions\|永久筆記]] | `永久筆記/` | 精煉後的核心知識 |
| [[日記/instructions\|日記]] | `日記/` | 個人抒發心得，**Claude 不需要讀取** |
| [[創作小說/README\|創作小說]] | `創作小說/` | 小說創作章節 |
| [[圖書館/instructions\|圖書館]] | `圖書館/` | 書籍、作者、閱讀法、心理學 |
| [[資源庫/參考資料/index\|資源庫]] | `資源庫/` | AI 工具、技術方法論、專案構想 |
| [[食譜/instructions\|食譜]] | `食譜/` | 料理食譜 |

**Claude 工作紀錄（與日記分開）：**
| `Daily Notes/` | 每日工作進度，Claude 的短期記憶，**每次對話後更新** |

**Claude 內部資料夾（輔助用）：**
| 資料夾 | 用途 |
|--------|------|
| [[Skills/instructions\|Skills/]] | Claude 技能包 |
| [[Projects/instructions\|Projects/]] | 技術專案（claude-bot 等） |

## 📖 按需讀取規則

1. **每次對話開始**：先讀這個 CLAUDE.md，了解整體結構
2. **需要了解我**：個人資料已在本檔「關於我」段落
3. **需要近期記憶**：讀最近 3 天的 `Daily Notes/`
4. **執行特定任務**：讀對應 `Skills/` 裡的技能檔案
5. **查看專案進度**：讀 `Projects/` 裡相應的專案檔案
6. **不要一次掃整個 Vault**，永遠按需讀取

## 📝 Daily Notes 規則

- 檔名格式：`YYYY-MM-DD.md`
- 每天開始時讀取今天的 Daily Note（若不存在則創建）
- 每天結束時更新當天記錄
- 讀最近 3 天的 Daily Notes 作為短期記憶

## 💡 重要原則

- 節省 Token：只讀當下需要的檔案
- 所有對話回覆使用繁體中文
- 有任何疑問先查 `instructions.md`，再問我

## 🔗 相關節點

- [[Skills/daily-note|每日筆記技能]]
- [[Skills/save-to-obsidian|存入Obsidian技能]]
- [[Projects/claude-bot/README|Claude Bot 專案]]
- [[資源庫/參考資料/技術方法論|第二大腦教學影片]]

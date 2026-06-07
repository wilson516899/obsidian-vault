> 隸屬於 [[Skills/instructions|Skills]] · 技能：[[Skills/daily-note|每日筆記]]

每天早上 8:00 自動生成今日 AI 推薦任務，寫入固定檔案供手機查看。

---

## 架構

```
Skills/daily-notify/
├── notify.py   ← 主腳本
└── README.md   ← 本檔案
```

**流程：**
```
cron (8:00) → notify.py → Claude API → 今日代辦.md（根目錄，每日覆蓋）
                                      → 代辦歷史/YYYY-MM-DD.md（自動歸檔）
```

Daily Note 不混入，保持純 Claude 工作紀錄。

## 手機查看方式

在 iPhone Obsidian 中，打開根目錄的 `今日代辦.md`，加入書籤（右上角星號）。
要查過去某天推薦了什麼，開 `代辦歷史/` 資料夾找日期。

---

## 環境變數設定

加到執行腳本電腦的 `~/.bashrc` 或 `~/.profile`：

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export VAULT_PATH="/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
```

---

## Cron 排程設定（WSL2）

```bash
crontab -e
```

加入：

```
0 8 * * * ANTHROPIC_API_KEY="sk-ant-..." VAULT_PATH="/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian" python3 /mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian/Skills/daily-notify/notify.py >> /tmp/daily-notify.log 2>&1
```

### 確認 cron 運作

```bash
service cron status      # 查看狀態
sudo service cron start  # 若未啟動

cat /tmp/daily-notify.log  # 查看執行紀錄
```

### WSL2 重開機問題

WSL2 重開機後 cron 會停止，解法：
1. 開啟 Windows **工作排程器**
2. 新增工作 → 觸發程序：登入時
3. 動作：程式 `wsl.exe`，引數 `sudo service cron start`

---

## 手動測試

```bash
python3 /mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian/Skills/daily-notify/notify.py
```

---

## 相關連結

- [[Skills/daily-note|每日筆記技能]]
- [[今日代辦|今日代辦（輸出檔）]]
- [[靈感筆記/2026年計畫|2026年計畫（上下文來源）]]

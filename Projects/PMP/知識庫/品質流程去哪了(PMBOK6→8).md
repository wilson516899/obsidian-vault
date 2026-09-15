---
狀態: 使用中
PMBOK8: Scope › Monitoring and Controlling › Validate Scope
來源錯題: E017
建立日期: 2026-09-14
---

# 品質流程去哪了（PMBOK 6 → 8）

> [[Projects/PMP/知識庫/_索引|← 知識庫索引]] ｜ `Scope 績效領域` › `Monitoring and Controlling` › `Validate Scope`

> [!warning] 這是你讀 PMBOK 6 完全不會知道的結構變化
> PMBOK 6 有獨立的「**Quality 品質管理**」知識領域，含三個流程。
> **PMBOK 8 把整個 Quality 領域拆掉了**，三個流程分別併入 **Governance** 和 **Scope** 兩個績效領域。

---

## PMBOK 6 的三個品質流程 → PMBOK 8 去哪了

| PMBOK 6 流程 | 在 PMBOK 6 做什麼 | PMBOK 8 併入哪裡 |
|---|---|---|
| **Plan Quality Management**<br>規劃品質管理 | 訂品質標準、驗收標準 | 併入 `Governance` 的規劃相關流程 |
| **Manage Quality**（舊稱 Quality Assurance）<br>管理品質 | 稽核流程、確保用對的方法、持續改善 | → `Governance › Executing › Manage Quality Assurance` |
| **Control Quality**<br>控制品質 | **檢驗交付物**、對照驗收標準、找出缺陷、產出「已驗證的交付物」 | → **`Scope › Monitoring and Controlling › Validate Scope`** |

> 🔑 **本題的關鍵**：「檢驗一批零件、對照驗收標準、15/200 不合格、寫缺陷報告」——這在 PMBOK 6 是教科書等級的 **Control Quality** 案例。但 PMBOK 8 沒有 Control Quality 這個流程了，它的工作被併進了 **Validate Scope**。

---

## 為什麼會這樣併（背後邏輯）

PMBOK 6 原本區分兩件事：
- **Control Quality**（品管）：東西做得**技術上對不對**（符合規格）→ 產出「已驗證的交付物」
- **Validate Scope**（範疇驗證）：客戶／關係人**願不願意接受**這個交付物 → 產出「已驗收的交付物」

PMBOK 8 把這兩件事**合併看待**：檢驗交付物是否符合驗收標準，本質上就是在**驗證範疇有沒有被正確完成**——兩者被視為同一個管控迴圈的一部分，因此不再分開列為兩個流程。

> 💡 這不代表「品管」的概念消失了——概念還在，只是不再是**獨立命名的流程**，被整併進 Validate Scope 底下的活動。

---

## ⚠️ 干擾選項辨析（本題）

| 錯誤選項                                        | 為什麼錯                                                                |
| ------------------------------------------- | ------------------------------------------------------------------- |
| **Manage Quality Assurance**                | 這是**規劃／稽核層級**的工作（確保用對方法、持續改善流程），不是**逐批檢驗交付物**的動作。題目描述的是具體的檢驗行為，層級不對 |
| **Monitor and Control Project Performance** | 這是**整體專案績效**的監控（進度、成本、範疇是否偏離基準），太上位、太籠統，題目講的是**單一批次零件的品質檢驗**，層級不對   |
| **Assess and Implement Changes**            | 這是**變更控制**流程，題目沒有出現任何「提出變更」的情境，純粹是檢驗與記錄                             |

> 🔑 判準：題目出現「**檢驗／inspect**」「**對照驗收標準**」「**缺陷報告**」這組關鍵字 → 直接想到 **Validate Scope**（PMBOK 8 新版），不要被舊版直覺拉去 Control Quality（因為它已經不存在了）。

---

## 判斷口訣

> 看到「檢驗交付物、對照驗收標準、產出缺陷報告」→ **Validate Scope**（不是 Control Quality，PMBOK 8 沒有這個流程了）。
> 看到「稽核流程、確保用對方法」→ **Manage Quality Assurance**。
> 記住：**Quality 不再是獨立領域**，看到題目考「品質相關」，先想它現在被歸在 Governance 還是 Scope。

---

## 相關

- [[Projects/PMP/知識庫/品質分析工具辨析|品質分析工具辨析]] —— 品質分析的工具（Pareto、散佈圖等）仍然通用，只是流程歸屬換了位置
- [[Projects/PMP/知識庫/需求追溯矩陣 RTM|需求追溯矩陣 RTM]] —— 同屬 Scope 績效領域的驗證類工具

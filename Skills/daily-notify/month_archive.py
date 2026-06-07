#!/usr/bin/env python3
"""
Daily Note 月份打包腳本
每月 1 號 08:10 執行（notify.py 完成後）
1. 統計上個月的 checkbox 完成狀況
2. 整理體重紀錄
3. 整理隨手記
4. 產生月份彙整.md
5. 將上個月的每日檔移入 Daily Note/YYYY-MM/ 子資料夾
"""

import os, re, json, shutil
from datetime import datetime, timedelta
from calendar import monthrange

VAULT = os.environ.get(
    "VAULT_PATH",
    "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
)

TODAY = datetime.now()
# 上個月
LAST_MONTH = (TODAY.replace(day=1) - timedelta(days=1))
YEAR  = LAST_MONTH.year
MONTH = LAST_MONTH.month
MONTH_STR  = f"{YEAR}-{MONTH:02d}"
MONTH_DAYS = monthrange(YEAR, MONTH)[1]

DAILY_NOTE_DIR  = f"{VAULT}/Daily Note"
ARCHIVE_DIR     = f"{DAILY_NOTE_DIR}/{MONTH_STR}"
PROGRESS_PATH   = f"{VAULT}/Skills/quest-system/progress.json"
OUTPUT_PATH     = f"{ARCHIVE_DIR}/{MONTH_STR} 月份彙整.md"


def read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def load_progress():
    try:
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def extract_checkboxes(content):
    """回傳 (checked_list, unchecked_list, weight)"""
    checked, unchecked, weight = [], [], None
    for line in content.split("\n"):
        if re.match(r"- \[x\]", line, re.IGNORECASE):
            name = re.sub(r"`\+\d+`", "", re.sub(r"- \[x\] ", "", line, flags=re.IGNORECASE)).strip()
            name = re.sub(r"→.*", "", name).strip()
            w = re.search(r"今日體重：([\d.]+)", line)
            if w:
                weight = float(w.group(1))
            checked.append(name)
        elif re.match(r"- \[ \]", line):
            name = re.sub(r"`\+\d+`", "", re.sub(r"- \[ \] ", "", line)).strip()
            name = re.sub(r"→.*", "", name).strip()
            if name:
                unchecked.append(name)
    return checked, unchecked, weight


def extract_memo(content):
    """擷取隨手記區塊"""
    m = re.search(r"## 隨手記\n+(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def build_report(daily_data, progress):
    """
    daily_data: { "2026-05-12": {"checked": [...], "unchecked": [...], "weight": 76.5, "memo": "..."} }
    """
    total_days = len(daily_data)
    active_days = sum(1 for d in daily_data.values() if d["checked"])
    empty_days  = total_days - active_days

    # 任務完成次數統計
    task_count = {}
    for d in daily_data.values():
        for t in d["checked"]:
            task_count[t] = task_count.get(t, 0) + 1

    task_rows = ""
    for task, count in sorted(task_count.items(), key=lambda x: -x[1]):
        task_rows += f"| {task} | {count} 次 |\n"

    # 體重紀錄（從 daily_data）
    weight_rows = ""
    for date, d in sorted(daily_data.items()):
        if d["weight"]:
            weight_rows += f"| {date} | {d['weight']} kg |\n"

    # 從 progress.json 補充體重（更可靠）
    if not weight_rows:
        log = progress.get("daily_log", [])
        for entry in log:
            if entry.get("date", "").startswith(MONTH_STR) and entry.get("weight_kg"):
                weight_rows += f"| {entry['date']} | {entry['weight_kg']} kg |\n"

    # 隨手記整理
    memo_block = ""
    for date, d in sorted(daily_data.items()):
        if d["memo"]:
            memo_block += f"### {date}\n{d['memo']}\n\n"

    # 上月最後積分快照（從 progress.json daily_log）
    log = progress.get("daily_log", [])
    month_log = [e for e in log if e.get("date", "").startswith(MONTH_STR)]
    month_pts = sum(e.get("pts", 0) for e in month_log)

    # 找月底最後一筆的體重
    last_weight = None
    for entry in reversed(month_log):
        if entry.get("weight_kg"):
            last_weight = entry["weight_kg"]
            break

    # 找月初第一筆體重
    first_weight = None
    for entry in month_log:
        if entry.get("weight_kg"):
            first_weight = entry["weight_kg"]
            break

    weight_change = ""
    if first_weight and last_weight:
        delta = round(last_weight - first_weight, 1)
        sign  = "+" if delta > 0 else ""
        weight_change = f"（{sign}{delta} kg）"

    content = f"""# {MONTH_STR} 月份彙整

> 涵蓋 {MONTH_STR}-01 ～ {MONTH_STR}-{MONTH_DAYS:02d}（{total_days} 天有紀錄）
> 詳細每日紀錄見同資料夾 `{MONTH_STR}-XX.md`

---

## 📊 本月快照

| 項目 | 數值 |
|------|------|
| 有完成任務的天數 | {active_days} / {total_days} 天 |
| 空白天數 | {empty_days} 天 |
| 本月累積積分 | {month_pts} pt |
| 月初體重 | {first_weight or "—"} kg |
| 月底體重 | {last_weight or "—"} kg {weight_change} |

---

## ✅ 任務完成次數

| 任務 | 次數 |
|------|------|
{task_rows.strip()}

---

## ⚖️ 體重紀錄

| 日期 | 體重 |
|------|------|
{weight_rows.strip() or "（本月無記錄）"}

---

## 📝 隨手記

{memo_block.strip() or "（本月無隨手記）"}
"""
    return content


def main():
    print(f"[{TODAY.strftime('%Y-%m-%d')}] 月份打包：{MONTH_STR}")

    # 收集上個月的每日檔
    daily_data = {}
    files_to_move = []

    for day in range(1, MONTH_DAYS + 1):
        date_str = f"{MONTH_STR}-{day:02d}"
        path = f"{DAILY_NOTE_DIR}/{date_str}.md"
        if os.path.exists(path):
            content = read(path)
            checked, unchecked, weight = extract_checkboxes(content)
            memo = extract_memo(content)
            daily_data[date_str] = {
                "checked":   checked,
                "unchecked": unchecked,
                "weight":    weight,
                "memo":      memo
            }
            files_to_move.append(path)

    if not daily_data:
        print(f"找不到 {MONTH_STR} 的任何 Daily Note，跳過")
        return

    # 建立子資料夾
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    # 產月份彙整
    progress = load_progress()
    report   = build_report(daily_data, progress)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"月份彙整已產出：{OUTPUT_PATH}")

    # 移動每日檔
    for src in files_to_move:
        fname = os.path.basename(src)
        dst   = f"{ARCHIVE_DIR}/{fname}"
        shutil.move(src, dst)
    print(f"已移動 {len(files_to_move)} 個每日檔至 {ARCHIVE_DIR}/")


if __name__ == "__main__":
    main()

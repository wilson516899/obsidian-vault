#!/usr/bin/env python3
"""
修煉積分系統 - 每日結算腳本
cron 07:55 執行，在 notify.py 覆蓋今日代辦之前
讀取昨日 checkbox 完成狀況 → 計算積分 → 更新 progress.json
"""

import os, re, json
from datetime import datetime, timedelta

VAULT = os.environ.get(
    "VAULT_PATH",
    "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
)

PROGRESS_PATH = f"{VAULT}/Skills/quest-system/progress.json"
AGENDA_PATH   = f"{VAULT}/今日代辦.md"
TRACKER_PATH  = f"{VAULT}/Skills/quest-system/修煉進度.md"

TODAY     = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# 里程碑定義
MILESTONES = [
    {"id": "quest_system_online",  "name": "修煉積分系統上線",       "pts": 200},
    {"id": "pmp_book_done",        "name": "讀完《淺出PMP》",         "pts": 300},
    {"id": "pmp_35hrs",            "name": "累積 35 小時 PMP 學習",   "pts": 200},
    {"id": "weight_75kg",          "name": "體重達到 75 kg",          "pts": 200},
    {"id": "date_experience",      "name": "完成一次體驗約會",         "pts": 100},
    {"id": "q2_kr_all",            "name": "Q2 全 KR 達成",           "pts": 500},
]

# 積分門檻
GOALS = [
    {"name": "衣著採購",      "target_pts": 700},
    {"name": "兩天一夜旅行",  "target_pts": 1500},
]


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
        return {
            "total_pts": 0,
            "streak": 0,
            "last_updated": "",
            "current_goal": GOALS[0],
            "milestones_completed": [],
            "total_pmp_minutes": 0,
            "weekly_completed": {},
            "daily_log": []
        }


def save_progress(p):
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)


def parse_checkboxes(content):
    """從 今日代辦 解析 checkbox 完成狀況，回傳 (checked_tasks, weight_kg)"""
    checked = []
    weight  = None

    for line in content.split("\n"):
        # 已勾選：- [x] 任務名稱 `+N`
        if re.match(r"- \[x\]", line, re.IGNORECASE):
            pts_match = re.search(r"`\+(\d+)`", line)
            pts = int(pts_match.group(1)) if pts_match else 0

            # 提取體重
            w_match = re.search(r"今日體重：([\d.]+)", line)
            if w_match:
                weight = float(w_match.group(1))

            checked.append({"line": line.strip(), "pts": pts})

    return checked, weight


def calc_streak_bonus(streak):
    """連擊加成，上限 30 pt"""
    return min(streak * 2, 30)


def get_day_type(date_str):
    """根據日期判斷是一般日/運動日/假日"""
    dow = datetime.strptime(date_str, "%Y-%m-%d").weekday()
    if dow in [5, 6]:
        return "weekend"
    elif dow in [1, 3]:  # 週二、週四
        return "exercise"
    else:
        return "normal"


def check_milestones(progress, weight, tasks_done):
    """檢查是否達成里程碑，回傳新達成的里程碑列表"""
    completed_ids = {m["id"] for m in progress.get("milestones_completed", [])}
    new_milestones = []

    # 體重 75 kg
    if weight and weight <= 75.0 and "weight_75kg" not in completed_ids:
        new_milestones.append("weight_75kg")

    # PMP 35 小時（2100 分鐘）
    if progress.get("total_pmp_minutes", 0) >= 2100 and "pmp_35hrs" not in completed_ids:
        new_milestones.append("pmp_35hrs")

    return new_milestones


def update_tracker(progress):
    """更新 修煉進度.md 的當前狀態表格"""
    total    = progress["total_pts"]
    streak   = progress["streak"]
    goal     = progress["current_goal"]
    goal_pts = goal["target_pts"]
    pct      = min(total / goal_pts, 1.0)
    filled   = int(pct * 20)
    bar      = "█" * filled + "░" * (20 - filled)
    distance = max(goal_pts - total, 0)

    # 體重歷史
    weight_rows = ""
    for entry in progress.get("daily_log", []):
        if entry.get("weight_kg"):
            weight_rows += f"| {entry['date']} | {entry['weight_kg']} kg |\n"

    # 積分歷史
    log_rows = ""
    for entry in reversed(progress.get("daily_log", [])):
        done = "、".join(entry.get("tasks_done", []))
        log_rows += f"| {entry['date']} | {entry['pts']} pt | {done} | {entry.get('streak', 0)} 天 |\n"

    # 里程碑
    milestone_rows = ""
    for m in progress.get("milestones_completed", []):
        milestone_rows += f"| {m['name']} | +{m['pts']} pt | {m.get('date', '—')} |\n"
    if not milestone_rows:
        milestone_rows = "| （尚無）| — | — |\n"

    content = f"""# ⚡ 修煉進度

> 每日由 quest.py 自動更新
> 詳細規則見 [[Skills/quest-system/PRD]]

---

## 當前狀態

| 項目 | 數值 |
|------|------|
| 累計積分 | {total} pt |
| 連擊天數 | {streak} 天 {"🔥" if streak >= 3 else ""} |
| 目前目標 | {goal["name"]}（{goal_pts} pt） |
| 距目標 | {distance} pt |

```
🎯 {goal["name"]}（{goal_pts} pt）
{bar}  {int(pct*100)}%
```

---

## 體重紀錄

| 日期 | 體重 |
|------|------|
{weight_rows.strip()}

---

## 每日積分紀錄

| 日期 | 得分 | 完成任務 | 連擊 |
|------|------|---------|------|
{log_rows.strip()}

---

## 里程碑紀錄

| 里程碑 | 點數 | 達成日 |
|--------|------|--------|
{milestone_rows.strip()}
"""

    with open(TRACKER_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"修煉進度已更新")


def main():
    print(f"[{TODAY}] quest.py 執行中，結算昨日（{YESTERDAY}）...")

    content = read(AGENDA_PATH)
    if not content:
        print("今日代辦讀取失敗，跳過")
        return

    # 解析 checkbox
    checked, weight = parse_checkboxes(content)
    progress = load_progress()

    if not checked:
        print("無勾選任務，連擊歸零並更新進度")
        last = progress.get("last_updated", "")
        if last != TODAY:
            progress["streak"] = 0
            progress["last_updated"] = YESTERDAY
            progress.setdefault("daily_log", []).append({
                "date":         YESTERDAY,
                "pts":          0,
                "base_pts":     0,
                "streak_bonus": 0,
                "streak":       0,
                "weight_kg":    None,
                "tasks_done":   []
            })
            save_progress(progress)
            update_tracker(progress)
        return

    # 週任務去重：同一 ISO 週內已計分的任務不重複累計
    iso_week = datetime.strptime(YESTERDAY, "%Y-%m-%d").strftime("%Y-W%W")
    weekly_done = progress.get("weekly_completed", {}).get(iso_week, [])
    WEEKLY_TASKS = ["找團", "揪人", "寫作", "寫日記"]

    # 計算今日積分（直接加總 checkbox 的 +N，週任務去重）
    base_pts = 0
    tasks_done = []
    for t in checked:
        name_match = re.match(r"- \[x\] (.+?) `", t["line"])
        name = name_match.group(1).strip() if name_match else ""

        # 判斷是否為週任務
        is_weekly = any(kw in name for kw in WEEKLY_TASKS)
        if is_weekly and name in weekly_done:
            print(f"週任務已計分，跳過：{name}")
            continue

        base_pts += t["pts"]
        tasks_done.append(name)

        if is_weekly:
            weekly_done.append(name)

    # 更新週任務完成紀錄
    progress.setdefault("weekly_completed", {})[iso_week] = weekly_done

    # 連擊邏輯
    last = progress.get("last_updated", "")
    if last == YESTERDAY:
        progress["streak"] += 1
    elif last == TODAY:
        print("今天已結算過，跳過")
        return
    else:
        progress["streak"] = 1

    streak_bonus = calc_streak_bonus(progress["streak"])
    total_today  = base_pts + streak_bonus

    # PMP 分鐘累計
    day_type = get_day_type(YESTERDAY)
    for t in tasks_done:
        if "PMP" in t:
            mins = 30 if day_type == "exercise" else 45
            progress["total_pmp_minutes"] = progress.get("total_pmp_minutes", 0) + mins

    # 里程碑檢查
    new_ms = check_milestones(progress, weight, tasks_done)
    for ms_id in new_ms:
        ms_def = next((m for m in MILESTONES if m["id"] == ms_id), None)
        if ms_def:
            total_today += ms_def["pts"]
            progress.setdefault("milestones_completed", []).append({
                "id":   ms_def["id"],
                "name": ms_def["name"],
                "pts":  ms_def["pts"],
                "date": YESTERDAY
            })
            print(f"🏆 里程碑達成：{ms_def['name']} +{ms_def['pts']} pt")

    # 更新總積分
    progress["total_pts"]    = progress.get("total_pts", 0) + total_today
    progress["last_updated"] = YESTERDAY

    # 目標升級判斷
    total_now = progress["total_pts"]
    for goal in GOALS:
        if total_now >= goal["target_pts"] and progress["current_goal"]["name"] == goal["name"]:
            print(f"🎉 目標達成：{goal['name']}！積分歸零，進入下一目標")
            progress["total_pts"] = total_now - goal["target_pts"]
            next_goals = [g for g in GOALS if g["name"] != goal["name"]]
            progress["current_goal"] = next_goals[0] if next_goals else goal
            break

    # daily_log 寫入
    progress.setdefault("daily_log", []).append({
        "date":       YESTERDAY,
        "pts":        total_today,
        "base_pts":   base_pts,
        "streak_bonus": streak_bonus,
        "streak":     progress["streak"],
        "weight_kg":  weight,
        "tasks_done": tasks_done
    })

    save_progress(progress)
    update_tracker(progress)

    print(f"今日積分：+{total_today} pt（基礎 {base_pts} + 連擊 {streak_bonus}）")
    print(f"累計：{progress['total_pts']} pt　連擊：{progress['streak']} 天")
    print(f"距目標「{progress['current_goal']['name']}」還差 {max(progress['current_goal']['target_pts'] - progress['total_pts'], 0)} pt")


if __name__ == "__main__":
    main()

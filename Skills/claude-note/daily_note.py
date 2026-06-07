#!/usr/bin/env python3
"""
每日筆記自動產生腳本
cron 23:00 執行
1. 讀取今日代辦 checkbox 完成狀況 + 積分進度 → 寫入 Daily Notes/{TODAY}.md
   （若當天已存在，則跳過不覆蓋）
2. 掃描圖書館所有書檔，同步 YAML 狀態 → blockquote
"""

import os, re, json, glob
from datetime import datetime

VAULT = os.environ.get(
    "VAULT_PATH",
    "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
)

TODAY   = datetime.now().strftime("%Y-%m-%d")
WEEKDAY = ["一", "二", "三", "四", "五", "六", "日"][datetime.now().weekday()]

AGENDA_PATH   = f"{VAULT}/今日代辦.md"
PROGRESS_PATH = f"{VAULT}/Skills/quest-system/progress.json"
NOTE_PATH     = f"{VAULT}/Claude Note/{TODAY}.md"
LIBRARY_PATH  = f"{VAULT}/圖書館"


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


def parse_agenda(content):
    """從今日代辦解析已完成與未完成任務"""
    done, pending = [], []
    for line in content.split("\n"):
        if re.match(r"- \[x\]", line, re.IGNORECASE):
            name = re.sub(r"`\+\d+`", "", line).replace("- [x]", "").strip()
            done.append(name)
        elif re.match(r"- \[ \]", line):
            name = re.sub(r"`\+\d+`", "", line).replace("- [ ]", "").strip()
            if name:
                pending.append(name)
    return done, pending


def get_today_quest(progress):
    """從 daily_log 找今天的積分紀錄"""
    for entry in reversed(progress.get("daily_log", [])):
        if entry.get("date") == TODAY:
            return entry
    return None


def build_note(done, pending, progress, quest_entry):
    total     = progress.get("total_pts", 0)
    streak    = progress.get("streak", 0)
    goal      = progress.get("current_goal", {})
    goal_name = goal.get("name", "—")
    goal_pts  = goal.get("target_pts", 700)

    done_lines    = "\n".join(f"- {t}" for t in done)    if done    else "- （無）"
    pending_lines = "\n".join(f"- {t}" for t in pending) if pending else "- （無）"

    if quest_entry:
        pts_line = (
            f"今日得分：**{quest_entry.get('pts', 0)} pt**"
            f"（基礎 {quest_entry.get('base_pts', 0)} + 連擊 {quest_entry.get('streak_bonus', 0)}）"
        )
    else:
        pts_line = "今日得分：尚未結算（quest.py 明早 07:55 執行）"

    pct    = min(total / goal_pts, 1.0) if goal_pts else 0
    filled = int(pct * 20)
    bar    = "█" * filled + "░" * (20 - filled)

    return f"""# {TODAY}（星期{WEEKDAY}）

> 由 daily_note.py 於 23:00 自動產生
> 隸屬於 [[CLAUDE]] · 技能：[[Skills/daily-note/README|每日筆記]]

---

## ✅ 今日完成任務

{done_lines}

## ⏳ 未完成

{pending_lines}

---

## ⚡ 修煉積分

{pts_line}
累計：{total} pt　連擊：{streak} 天
目標：{goal_name}（{goal_pts} pt）
{bar}  {int(pct * 100)}%
"""


# ── 書籍狀態同步 ──────────────────────────────────────────

def sync_book(path):
    """同步單本書的 YAML frontmatter → blockquote 顯示"""
    content = read(path)
    if not content.startswith("---"):
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        return False

    _, fm, rest = parts

    status_match = re.search(r'^狀態:\s*(.*)$', fm, re.MULTILINE)
    date_match   = re.search(r'^閱讀日期:\s*(.*)$', fm, re.MULTILINE)
    status = status_match.group(1).strip() if status_match else ""
    date   = date_match.group(1).strip()   if date_match   else ""

    new_rest = re.sub(r'^> 狀態：.*$',     f'> 狀態：{status}', rest, flags=re.MULTILINE)
    new_rest = re.sub(r'^> 閱讀日期：.*$', f'> 閱讀日期：{date}', new_rest, flags=re.MULTILINE)

    if new_rest == rest:
        return False  # 沒有變化，不寫入

    new_content = f"---{fm}---{new_rest}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def sync_all_books():
    """掃描圖書館所有書檔，同步狀態"""
    exclude = {"instructions.md"}
    files   = [
        p for p in glob.glob(f"{LIBRARY_PATH}/*.md")
        if os.path.basename(p) not in exclude
    ]
    updated = sum(1 for p in files if sync_book(p))
    print(f"書籍狀態同步完成：{updated}/{len(files)} 本有更新")


# ── 主流程 ────────────────────────────────────────────────

def main():
    print(f"[{TODAY}] daily_note.py 執行中...")

    # 1. 書籍狀態同步（每天都跑，無論 Daily Note 是否已存在）
    sync_all_books()

    # 2. Daily Note（已存在則跳過）
    if os.path.exists(NOTE_PATH):
        print(f"Daily Note 已存在，跳過：{NOTE_PATH}")
        return

    agenda   = read(AGENDA_PATH)
    progress = load_progress()

    done, pending = parse_agenda(agenda)
    quest_entry   = get_today_quest(progress)

    content = build_note(done, pending, progress, quest_entry)

    os.makedirs(os.path.dirname(NOTE_PATH), exist_ok=True)
    with open(NOTE_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Daily Note 已產生：{NOTE_PATH}")
    print(f"完成任務 {len(done)} 項，未完成 {len(pending)} 項")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
每日代辦通知腳本
由 cron 每天早上 8 點觸發，生成今日建議任務
直接寫入 Daily Note/YYYY-MM-DD.md（整合今日代辦 + 歸檔為一）
"""

import os, subprocess, glob, json, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

VAULT   = os.environ.get(
    "VAULT_PATH",
    "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
)
_now    = datetime.strptime(os.environ["TARGET_DATE"], "%Y-%m-%d") if os.environ.get("TARGET_DATE") else datetime.now()
TODAY   = _now.strftime("%Y-%m-%d")
WEEKDAY = ["一", "二", "三", "四", "五", "六", "日"][_now.weekday()]
DOW     = _now.weekday()  # 0=Mon, 1=Tue, ..., 6=Sun

NEWS_SOURCES = {
    "🌍 國際": {
        "feeds": ["https://feeds.bbci.co.uk/zhongwen/trad/rss.xml"],
        "count": 5,
        "criteria": "最具國際影響力的事件，排除娛樂、體育"
    },
    "🇹🇼 台灣政經": {
        "feeds": [
            "https://news.ltn.com.tw/rss/politics.xml",
            "https://news.ltn.com.tw/rss/business.xml"
        ],
        "count": 4,
        "criteria": "優先選政府政策、兩岸關係、總體經濟；排除地方選舉、個人八卦"
    },
    "🤖 AI 科技": {
        "feeds": [
            "https://techcrunch.com/category/artificial-intelligence/feed/",
            "https://techcrunch.com/tag/openai/feed/"
        ],
        "count": 4,
        "criteria": "優先選新工具發布、重大模型更新、產業格局變動；排除融資新聞"
    }
}


def read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def fetch_rss_items(url, count):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            root = ET.fromstring(r.read())
        items = []
        for entry in root.findall(".//item")[:count]:
            title = entry.findtext("title", "").strip()
            link  = entry.findtext("link", "").strip()
            if title:
                items.append((title, link))
        return items
    except:
        return []


def collect_news_candidates():
    blocks = []
    id_map = {}   # id → (title, link)
    counter = [0]

    for category, cfg in NEWS_SOURCES.items():
        candidates = []
        for url in cfg["feeds"]:
            candidates.extend(fetch_rss_items(url, cfg["count"]))
        seen = set()
        cat_lines = []
        for title, link in candidates:
            if title not in seen:
                seen.add(title)
                counter[0] += 1
                nid = f"N{counter[0]:02d}"
                id_map[nid] = (title, link)
                cat_lines.append(f"  [{nid}] {title}")
        lines = "\n".join(cat_lines[:8])
        blocks.append(f"【{category}】篩選條件：{cfg['criteria']}\n候選：\n{lines}")

    return "\n\n".join(blocks), id_map


def extract_daily_note_summary(content):
    """擷取 checkbox 任務完成狀況 + 隨手記，過濾簡報/新聞噪音"""
    import re
    parts = []

    # 修煉任務區塊（checkbox 完成狀況）
    quest_match = re.search(r'(## ⚡ 今日修煉任務.+?)(?=\n---|\n## |\Z)', content, re.DOTALL)
    if quest_match:
        parts.append(quest_match.group(1).strip())

    # 隨手記區塊
    notes_match = re.search(r'## 隨手記\n+(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if notes_match:
        notes = notes_match.group(1).strip()
        if notes:
            parts.append(f"## 隨手記\n{notes}")

    return "\n\n".join(parts)


def collect_context():
    parts = []

    for i in range(1, 8):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        dn = read(f"{VAULT}/Daily Note/{date}.md")
        if dn:
            summary = extract_daily_note_summary(dn)
            if summary:
                parts.append(f"=== {date} ===\n{summary}")

    plan = read(f"{VAULT}/靈感筆記/2026年計畫.md")
    if plan:
        parts.append(f"=== 年度OKR計畫 ===\n{plan[:1200]}")

    skip = {"instructions.md", "2026年計畫.md", "PMI.md"}
    for path in glob.glob(f"{VAULT}/靈感筆記/*.md"):
        if os.path.basename(path) not in skip:
            content = read(path)
            if content:
                parts.append(f"=== 靈感：{os.path.basename(path)} ===\n{content[:400]}")

    return "\n\n".join(parts)


def load_progress():
    path = f"{VAULT}/Skills/quest-system/progress.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"total_pts": 0, "streak": 0, "current_goal": {"name": "衣著採購", "target_pts": 700}}


def build_progress_bar(progress):
    total = progress.get("total_pts", 0)
    streak = progress.get("streak", 0)
    goal = progress.get("current_goal", {})
    goal_name = goal.get("name", "衣著採購")
    goal_pts  = goal.get("target_pts", 700)

    pct = min(total / goal_pts, 1.0)
    filled = int(pct * 20)
    bar = "█" * filled + "░" * (20 - filled)
    streak_icon = f" 🔥" if streak >= 3 else ""

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    log = progress.get("daily_log", [])
    yesterday_log = next((d for d in reversed(log) if d.get("date") == yesterday), None)
    yesterday_line = ""
    if yesterday_log:
        done_count = len(yesterday_log.get("tasks_done", []))
        yesterday_line = f"\n昨日 +{yesterday_log.get('pts', 0)} pt（{done_count} 項完成）"

    return (
        f"⚡ 修煉進度  ·  累計：{total} pt  ·  連擊 {streak} 天{streak_icon}"
        f"{yesterday_line}\n\n"
        f"🎯 目標：{goal_name}（{goal_pts} pt）\n"
        f"{bar}  {int(pct*100)}%  [距目標 {max(goal_pts - total, 0)} pt]"
    )


def get_weekly_done():
    """從 progress.json 讀本週已完成的週任務名稱"""
    progress = load_progress()
    iso_week = datetime.now().strftime("%Y-W%W")
    return progress.get("weekly_completed", {}).get(iso_week, [])


def weekly_checkbox(label, pts, weekly_done):
    """產生週任務 checkbox：本週已完成則標示 ✅"""
    keywords = ["找團", "揪人"]
    already = any(kw in label for kw in keywords for done in weekly_done if kw in done)
    if already:
        return f"- [x] ~~{label}~~ `+{pts}` ✅ 本週已完成"
    return f"- [ ] {label} `+{pts}`"


def build_quest_section():
    """根據今天星期幾產生對應的修煉任務 checkbox"""
    # 0=Mon,1=Tue,2=Wed,3=Thu,4=Fri,5=Sat,6=Sun
    is_exercise_day = DOW in [1, 3]   # 週二、週四
    is_weekend      = DOW in [5, 6]   # 週六、週日

    weekly_done = get_weekly_done()

    fixed = (
        "**固定任務**\n"
        "- [ ] 記錄體重 `+5` → 今日體重：\n"
        "- [ ] 無消夜 + 無零食 `+15`\n"
        "- [ ] 寫日記 `+15`"
    )

    w_hunt  = weekly_checkbox("找團 / 揪人訊息", 15, weekly_done)
    # 寫作不做去重：每寫一本都給分，故直接輸出未勾選 checkbox
    w_write = "- [ ] 寫作（小說或書摘）`+25`（每完成一本各給分）"

    if is_weekend:
        day_label = "假日"
        max_pts = 20 + 15 + 15 + 25  # 固定 + 寫作一次（實際可多次）
        day_tasks = ""
    elif is_exercise_day:
        day_label = "運動日"
        max_pts = 20 + 15 + 15 + 20 + 15 + 25  # 固定 + PMP30 + 運動課 + 寫作
        day_tasks = (
            "**今日任務（運動日）**\n"
            "- [ ] 運動課出席（19:00）`+15`\n"
            "- [ ] PMP 讀書 30 分鐘 `+20`"
        )
    else:
        day_label = "一般日"
        max_pts = 20 + 15 + 15 + 30 + 10 + 25  # 固定 + PMP45 + 走路 + 寫作
        day_tasks = (
            "**今日任務（一般日）**\n"
            "- [ ] PMP 讀書 45 分鐘 `+30`\n"
            "- [ ] 飯後走路 20 分鐘 `+10`"
        )

    weekly = f"**本週任務**\n{w_hunt}\n{w_write}"

    parts = [f"> {day_label} · 滿分：+{max_pts} pt（不含連擊）", "", fixed]
    if day_tasks:
        parts += ["", day_tasks]
    parts += ["", weekly]

    return "## ⚡ 今日修煉任務\n\n" + "\n".join(parts)


def ask_claude(context, news_candidates):
    prompt = f"""你是崇瑋的個人 AI 助理。今天是 {TODAY}（星期{WEEKDAY}）。

根據下方資料，完成兩件事：

【一】今日代辦推薦（3-5 件）
主動推薦今天最值得做的事，考量年度OKR進度、代辦積壓、星期幾。
格式：
① 最重要
② 次要
③ 其他（可多條）
💡 一句提醒

【二】今日新聞精選
從下方各 category 候選新聞中，依篩選條件各選一則，回傳該則的 ID（方括號內的代號，如 N01）。
格式（只輸出 ID，不要改寫標題）：
🌍 國際｜N??
🇹🇼 台灣政經｜N??
🤖 AI 科技｜N??

---
=== Vault 資料 ===
{context}

=== 新聞候選 ===
{news_candidates}"""

    result = subprocess.run(
        ["/mnt/c/Users/崇瑋/AppData/Roaming/npm/claude", "--print", prompt],
        capture_output=True, text=True, timeout=90
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI 失敗：{result.stderr}")
    return result.stdout.strip()


def load_weekly_writing_task():
    """讀取本週寫作任務（由 book_fill.py 週一產生）"""
    path = f"{VAULT}/Skills/book-fill/本週任務.md"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return ""


def attach_links(briefing, id_map):
    """把 Claude 回傳的 N01 等 ID 替換成 [標題](連結)"""
    import re
    def replace_id(m):
        nid = m.group(0)
        if nid in id_map:
            title, link = id_map[nid]
            return f"[{title}]({link})" if link else title
        return nid
    return re.sub(r'N\d{2}', replace_id, briefing)


def update_homepage():
    """更新主頁.md 的今日 Daily Note 連結"""
    homepage = f"{VAULT}/主頁.md"
    try:
        with open(homepage, "r", encoding="utf-8") as f:
            content = f.read()
        import re
        updated = re.sub(
            r'\[\[Daily Note/\d{4}-\d{2}-\d{2}\|今天的 Daily Note\]\]',
            f'[[Daily Note/{TODAY}|今天的 Daily Note]]',
            content
        )
        if updated != content:
            with open(homepage, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"主頁.md 今日連結已更新：{TODAY}")
    except Exception as e:
        print(f"主頁更新失敗（非阻斷）：{e}")


def write_daily_note(briefing, progress_bar, quest_section, weekly_writing):
    path = f"{VAULT}/Daily Note/{TODAY}.md"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    writing_block = f"\n---\n\n{weekly_writing}\n" if weekly_writing else ""

    content = f"""# {TODAY}（星期{WEEKDAY}）

> 每天早上 8:00 自動更新 · [[Skills/daily-notify/README|daily-notify]]

---

{progress_bar}

---

{quest_section}
{writing_block}
---

## 每日簡報

{briefing}

---

## 隨手記

"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Daily Note 已寫入：{path}")


if __name__ == "__main__":
    print(f"[{TODAY}] 生成今日代辦中...")
    progress       = load_progress()
    progress_bar   = build_progress_bar(progress)
    quest_section  = build_quest_section()
    weekly_writing = load_weekly_writing_task()
    ctx            = collect_context()
    news_str, raw  = collect_news_candidates()
    briefing       = ask_claude(ctx, news_str)
    briefing       = attach_links(briefing, raw)
    write_daily_note(briefing, progress_bar, quest_section, weekly_writing)
    update_homepage()
    print("完成")

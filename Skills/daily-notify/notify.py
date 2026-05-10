#!/usr/bin/env python3
"""
每日代辦通知腳本
由 cron 每天早上 8 點觸發，生成今日建議任務
寫入固定檔案（手機 Obsidian 釘選查看）+ 代辦歷史歸檔
Daily Note 不混入，保持純 Claude 工作紀錄
"""

import os, subprocess, glob, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

VAULT = os.environ.get(
    "VAULT_PATH",
    "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
)
TODAY   = datetime.now().strftime("%Y-%m-%d")
WEEKDAY = ["一", "二", "三", "四", "五", "六", "日"][datetime.now().weekday()]


def read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def collect_context():
    parts = []

    # 近三天 Daily Notes
    for i in range(1, 4):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        dn = read(f"{VAULT}/Daily Notes/{date}.md")
        if dn:
            parts.append(f"=== {date} 紀錄 ===\n{dn[:800]}")

    # 代辦事項
    todo = read(f"{VAULT}/靈感筆記/代辦事項.md")
    if todo:
        parts.append(f"=== 代辦事項 ===\n{todo}")

    # 年度計畫（目標全貌）
    plan = read(f"{VAULT}/靈感筆記/明年計畫.md")
    if plan:
        parts.append(f"=== 年度計畫 ===\n{plan[:1000]}")

    # 靈感筆記（近期捕捉，排除固定檔）
    skip = {"instructions.md", "代辦事項.md", "明年計畫.md", "PMI.md"}
    for path in glob.glob(f"{VAULT}/靈感筆記/*.md"):
        if os.path.basename(path) not in skip:
            content = read(path)
            if content:
                parts.append(f"=== 靈感：{os.path.basename(path)} ===\n{content[:400]}")

    # 小說大綱（完整讀入，供方向四使用）
    outline = read(f"{VAULT}/創作小說/大綱.md")
    if outline:
        parts.append(f"=== 小說大綱 ===\n{outline[:1500]}")

    return "\n\n".join(parts)


def ask_claude(context):
    prompt = f"""你是崇瑋的個人 AI 助理。今天是 {TODAY}（星期{WEEKDAY}）。

根據下方 Vault 資料，完成兩件事：

【一】今日代辦推薦（3-5 件）
主動推薦今天最值得做的事，考量年度目標進度、代辦積壓程度、今天是星期幾。
格式：
① 最重要
② 次要
③ 其他（可多條）
💡 一句提醒

【二】小說今日任務
根據大綱，判斷目前進度最需要推進的章節或段落，給出一個具體的今日寫作目標。
格式：
✍️ 今日小說任務：[章節名稱]
目標：寫完 [具體場景或段落]，約 [字數] 字

全文不超過 250 字，用繁體中文，適合手機閱讀。

---
{context}"""

    result = subprocess.run(
        ["claude", "--print", prompt],
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI 失敗：{result.stderr}")
    return result.stdout.strip()


NEWS_FEEDS = [
    ("🌍 國際", "https://feeds.bbci.co.uk/zhongwen/trad/rss.xml"),
    ("🇹🇼 台灣政經", "https://news.ltn.com.tw/rss/politics.xml"),
    ("🤖 AI 科技", "https://techcrunch.com/category/artificial-intelligence/feed/"),
]

def fetch_news():
    items = []
    for label, url in NEWS_FEEDS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                root = ET.fromstring(r.read())
            entry = root.find(".//item")
            if entry is not None:
                title = entry.findtext("title", "").strip()
                link  = entry.findtext("link", "").strip()
                if link:
                    items.append(f"{label}｜[{title}]({link})")
                else:
                    items.append(f"{label}｜{title}")
        except Exception as e:
            items.append(f"{label}｜（今日無法取得：{e}）")
    return items


def write_daily_agenda(briefing, news):
    path = f"{VAULT}/今日代辦.md"
    news_block = "\n".join(f"- {n}" for n in news)
    content = f"""# 今日代辦

> 每天早上 8:00 自動更新 · [[Skills/daily-notify/README|daily-notify]]

📅 {TODAY}（星期{WEEKDAY}）

{briefing}

---

📰 **今日新聞**

{news_block}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"今日代辦已寫入：{path}")


def archive_agenda(briefing):
    path = f"{VAULT}/代辦歷史/{TODAY}.md"
    content = f"""# {TODAY}（星期{WEEKDAY}）代辦記錄

> [[今日代辦|← 今日代辦]]

{briefing}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"代辦歷史已歸檔：{path}")


if __name__ == "__main__":
    print(f"[{TODAY}] 生成今日代辦中...")
    ctx      = collect_context()
    briefing = ask_claude(ctx)
    news     = fetch_news()
    write_daily_agenda(briefing, news)
    archive_agenda(briefing)
    print("完成")

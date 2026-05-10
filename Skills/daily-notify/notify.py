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

VAULT   = os.environ.get(
    "VAULT_PATH",
    "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
)
TODAY   = datetime.now().strftime("%Y-%m-%d")
WEEKDAY = ["一", "二", "三", "四", "五", "六", "日"][datetime.now().weekday()]

# 每個 category 可設多個 feed，抓前 N 則後由 Claude 篩選
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
    """從 RSS feed 抓前 count 則，回傳 (title, link) list"""
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
    """各 category 抓候選新聞，整理成字串供 Claude 篩選"""
    blocks = []
    raw = {}  # 儲存 title→link 對照表
    for category, cfg in NEWS_SOURCES.items():
        candidates = []
        for url in cfg["feeds"]:
            candidates.extend(fetch_rss_items(url, cfg["count"]))
        # 去重（相同標題）
        seen = set()
        unique = []
        for title, link in candidates:
            if title not in seen:
                seen.add(title)
                unique.append((title, link))
                raw[title] = link
        lines = "\n".join(f"  - {t}" for t, _ in unique[:8])
        blocks.append(
            f"【{category}】篩選條件：{cfg['criteria']}\n候選：\n{lines}"
        )
    return "\n\n".join(blocks), raw


def collect_context():
    parts = []

    for i in range(1, 4):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        dn = read(f"{VAULT}/Daily Notes/{date}.md")
        if dn:
            parts.append(f"=== {date} 紀錄 ===\n{dn[:800]}")

    todo = read(f"{VAULT}/靈感筆記/代辦事項.md")
    if todo:
        parts.append(f"=== 代辦事項 ===\n{todo}")

    plan = read(f"{VAULT}/靈感筆記/明年計畫.md")
    if plan:
        parts.append(f"=== 年度計畫 ===\n{plan[:1000]}")

    skip = {"instructions.md", "代辦事項.md", "明年計畫.md", "PMI.md"}
    for path in glob.glob(f"{VAULT}/靈感筆記/*.md"):
        if os.path.basename(path) not in skip:
            content = read(path)
            if content:
                parts.append(f"=== 靈感：{os.path.basename(path)} ===\n{content[:400]}")

    outline = read(f"{VAULT}/創作小說/大綱.md")
    if outline:
        parts.append(f"=== 小說大綱 ===\n{outline[:1500]}")

    return "\n\n".join(parts)


def ask_claude(context, news_candidates):
    prompt = f"""你是崇瑋的個人 AI 助理。今天是 {TODAY}（星期{WEEKDAY}）。

根據下方資料，完成三件事：

【一】今日代辦推薦（3-5 件）
主動推薦今天最值得做的事，考量年度目標進度、代辦積壓、星期幾。
格式：
① 最重要
② 次要
③ 其他（可多條）
💡 一句提醒

【二】小說今日任務
根據大綱判斷最需推進的章節，給出具體今日寫作目標。
格式：
✍️ 今日小說任務：[章節]
目標：寫完 [具體場景]，約 [字數] 字

【三】今日新聞精選
從下方各 category 候選新聞中，依篩選條件各選一則，只輸出標題原文（不改寫、不摘要）。
格式：
🌍 國際｜[選出的標題原文]
🇹🇼 台灣政經｜[選出的標題原文]
🤖 AI 科技｜[選出的標題原文]

---
=== Vault 資料 ===
{context}

=== 新聞候選 ===
{news_candidates}"""

    result = subprocess.run(
        ["claude", "--print", prompt],
        capture_output=True, text=True, timeout=90
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI 失敗：{result.stderr}")
    return result.stdout.strip()


def attach_links(briefing, raw_links):
    """把 Claude 輸出的標題原文換成 Markdown 連結"""
    for title, link in raw_links.items():
        if title in briefing and link:
            briefing = briefing.replace(title, f"[{title}]({link})")
    return briefing


def write_daily_agenda(briefing):
    path = f"{VAULT}/今日代辦.md"
    content = f"""# 今日代辦

> 每天早上 8:00 自動更新 · [[Skills/daily-notify/README|daily-notify]]

📅 {TODAY}（星期{WEEKDAY}）

{briefing}
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
    ctx              = collect_context()
    news_str, raw    = collect_news_candidates()
    briefing         = ask_claude(ctx, news_str)
    briefing         = attach_links(briefing, raw)
    write_daily_agenda(briefing)
    archive_agenda(briefing)
    print("完成")

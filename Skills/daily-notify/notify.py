#!/usr/bin/env python3
"""
每日代辦通知腳本
由 cron 每天早上 8 點觸發，生成今日建議任務
寫入固定檔案（手機 Obsidian 釘選查看）+ 代辦歷史歸檔
Daily Note 不混入，保持純 Claude 工作紀錄
"""

import os, json, urllib.request
from datetime import datetime, timedelta

VAULT = os.environ.get(
    "VAULT_PATH",
    "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
)
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TODAY     = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
WEEKDAY   = ["一", "二", "三", "四", "五", "六", "日"][datetime.now().weekday()]


def read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def collect_context():
    parts = []

    dn = read(f"{VAULT}/Daily Notes/{YESTERDAY}.md")
    if dn:
        parts.append(f"=== 昨日紀錄 ===\n{dn[:1500]}")

    todo = read(f"{VAULT}/靈感筆記/代辦事項.md")
    if todo:
        parts.append(f"=== 代辦事項 ===\n{todo}")

    outline = read(f"{VAULT}/創作小說/大綱.md")
    if outline:
        parts.append(f"=== 小說大綱（節錄）===\n{outline[:800]}")

    return "\n\n".join(parts)


def ask_claude(context):
    prompt = f"""你是崇瑋的個人 AI 助理。今天是 {TODAY}（星期{WEEKDAY}）。

根據下方 Vault 近況，推薦他今天最重要的 3-5 件事。
這是你主動建議，不是他自己寫的清單。
格式簡潔，適合手機閱讀，全文不超過 200 字，用繁體中文。

輸出格式（嚴格遵守）：
① 最重要的事
② 次要事項
③ 其他

💡 一句鼓勵或提醒

---
{context}"""

    body = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 350,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["content"][0]["text"]


def write_daily_agenda(briefing):
    """覆蓋固定檔案，手機釘選此頁每天看最新內容"""
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
    """歸檔到代辦歷史/，要回頭查再進來"""
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
    write_daily_agenda(briefing)
    archive_agenda(briefing)
    print("完成")

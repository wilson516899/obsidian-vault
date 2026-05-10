#!/usr/bin/env python3
"""
讀書筆記自動補齊腳本
每天從 圖書館/ 隨機挑一本「待確認」書，Claude 生成 AI 書摘插入檔案
cron 建議設在 8:05，daily-notify 之後執行
"""

import os, re, subprocess, glob, random
from datetime import datetime

VAULT = os.environ.get(
    "VAULT_PATH",
    "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
)
PLACEHOLDER = "以一套書去介紹各式各樣的著名書作"
AI_MARKER   = "## 📖 AI 書摘"
TODAY       = datetime.now().strftime("%Y-%m-%d")


def read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def get_book_info(content):
    name, author = None, "不明"
    skip_keywords = ["大綱", "葉脈", "葉肉", "論證", "📖"]
    for line in content.split("\n"):
        if name is None and line.startswith("# "):
            candidate = line[2:].strip()
            if candidate and not any(k in candidate for k in skip_keywords):
                name = candidate
        m = re.search(r'> 作者：.*?\|([^\]]+)\]\]', line)
        if m:
            author = m.group(1)
        elif "> 作者：" in line and "[[" not in line:
            author = line.split("作者：")[-1].strip()
    return name, author


def needs_fill(content):
    return PLACEHOLDER in content and AI_MARKER not in content


def generate_brief(book_name, author):
    prompt = f"""你是一位書評家。請為《{book_name}》（作者：{author}）生成一份簡潔的 AI 書摘，供讀者決定是否閱讀。

格式（嚴格遵守，繁體中文）：

**一句話總結：** （20 字內，這本書在說什麼）

**核心概念：** （這本書最重要的一個洞見或主題，2-3 句）

**主要論點：** （作者如何展開論述，2-3 句）

**適合誰讀：** （什麼樣的人最能從這本書受益，1-2 句）

**經典金句：** （一句代表性引言，若不確定請寫「待補」）

注意：若這本書你不熟悉，請如實說明，不要捏造。"""

    result = subprocess.run(
        ["claude", "--print", prompt],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI 失敗：{result.stderr}")
    return result.stdout.strip()


def insert_brief(content, brief):
    """在封面圖片之後插入 AI 書摘區塊"""
    marker = "![[covers/"
    idx = content.find(marker)
    if idx != -1:
        end = content.find("\n", idx) + 1
        section = f"\n{AI_MARKER}（{TODAY} 生成，待驗證）\n\n{brief}\n\n---\n"
        return content[:end] + section + content[end:]
    # 找不到封面就插在第一個 ## 之前
    idx = content.find("\n# 大綱")
    if idx != -1:
        section = f"\n{AI_MARKER}（{TODAY} 生成，待驗證）\n\n{brief}\n\n---\n"
        return content[:idx] + section + content[idx:]
    return content + f"\n\n{AI_MARKER}（{TODAY} 生成，待驗證）\n\n{brief}\n"


def main():
    book_files = [
        p for p in glob.glob(f"{VAULT}/圖書館/*.md")
        if os.path.basename(p) != "instructions.md"
    ]
    unfilled = [p for p in book_files if needs_fill(read(p))]

    if not unfilled:
        print("所有書籍 AI 書摘已補齊！")
        return

    chosen  = random.choice(unfilled)
    content = read(chosen)
    name, author = get_book_info(content)

    print(f"今日補齊：《{name}》（{author}）")
    print(f"剩餘待補：{len(unfilled) - 1} 本")

    brief       = generate_brief(name, author)
    new_content = insert_brief(content, brief)

    with open(chosen, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✓ 已寫入：{os.path.basename(chosen)}")


if __name__ == "__main__":
    main()

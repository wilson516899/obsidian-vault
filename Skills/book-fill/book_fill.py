#!/usr/bin/env python3
"""
每日書摘推薦腳本
從 圖書館/ 隨機挑一本沒有筆記的書，附加到今日代辦末尾
提醒使用者自己去填，不自動生成內容
"""

import os, re, glob, random
from datetime import datetime

VAULT   = os.environ.get(
    "VAULT_PATH",
    "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
)
PLACEHOLDER = "以一套書去介紹各式各樣的著名書作"
TODAY       = datetime.now().strftime("%Y-%m-%d")


def read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def get_book_name(content):
    skip = {"大綱", "葉脈", "葉肉", "論證", "📖"}
    for line in content.split("\n"):
        if line.startswith("# "):
            candidate = line[2:].strip()
            if candidate and not any(k in candidate for k in skip):
                return candidate
    return None


def has_no_notes(content):
    """只有佔位文字或空白，代表使用者還沒填過筆記"""
    return PLACEHOLDER in content


def append_to_agenda(book_name, book_path):
    agenda_path = f"{VAULT}/今日代辦.md"
    content = read(agenda_path)
    link = f"[[圖書館/{os.path.basename(book_path).replace('.md', '')}|{book_name}]]"
    note = f"\n---\n\n📚 **今日書摘任務**\n《{link}》還沒有你的閱讀筆記，今天花 10 分鐘填一段心得吧。\n"
    with open(agenda_path, "a", encoding="utf-8") as f:
        f.write(note)
    print(f"已推薦：《{book_name}》")


def main():
    book_files = [
        p for p in glob.glob(f"{VAULT}/圖書館/*.md")
        if os.path.basename(p) != "instructions.md"
    ]
    unfilled = [p for p in book_files if has_no_notes(read(p))]

    if not unfilled:
        print("所有書籍都有筆記了！")
        return

    chosen  = random.choice(unfilled)
    content = read(chosen)
    name    = get_book_name(content)

    print(f"今日推薦補齊：《{name}》（剩餘 {len(unfilled)} 本待填）")
    append_to_agenda(name, chosen)


if __name__ == "__main__":
    main()

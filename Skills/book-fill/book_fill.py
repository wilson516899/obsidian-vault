#!/usr/bin/env python3
"""
每週寫作推薦腳本（週一執行）
同時推薦：圖書館書摘 + 小說章節
寫入 Skills/book-fill/本週任務.md，由 notify.py 每天讀取帶入今日代辦
"""

import os, re, glob, random
from datetime import datetime

VAULT = os.environ.get(
    "VAULT_PATH",
    "/mnt/c/Users/崇瑋/iCloudDrive/iCloud~md~obsidian/Obsidian"
)
TODAY = datetime.now()


def read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def is_monday():
    """只在週一執行（weekday() == 0）"""
    return TODAY.weekday() == 0


def get_book_name(content):
    skip = {"大綱", "葉脈", "葉肉", "論證", "📖"}
    for line in content.split("\n"):
        if line.startswith("# "):
            candidate = line[2:].strip()
            if candidate and not any(k in candidate for k in skip):
                return candidate
    return None


def has_no_notes(content):
    """判斷 # 大綱 區塊是否有真實內容（超過 30 字且非空行）"""
    m = re.search(r'# 大綱\n(.*?)(?=\n# |\Z)', content, re.DOTALL)
    if not m:
        return True
    body = m.group(1).strip()
    return len(body) < 30


def get_novel_task():
    """從小說大綱取得當前章節任務"""
    outline_path = f"{VAULT}/創作小說/大綱.md"
    content = read(outline_path)
    # 抓第一個未完成章節（簡單抓包含「第」的行）
    for line in content.split("\n"):
        if "第" in line and ("章" in line or "幕" in line):
            return line.strip().lstrip("#").strip()
    return "繼續推進小說進度"


def write_weekly_task(primary_book_name, primary_book_path, extra_books):
    """將本週寫作任務寫入獨立檔案，供 notify.py 每天讀取"""
    out_path   = f"{VAULT}/Skills/book-fill/本週任務.md"
    link       = f"[[Obsidian/圖書館/{os.path.basename(primary_book_path).replace('.md', '')}|{primary_book_name}]]"
    novel_task = get_novel_task()
    week_str   = TODAY.strftime("%Y-W%W")

    # 額外候補書單（若想多寫一本可從這裡選）
    extra_lines = ""
    if extra_books:
        extra_lines = "\n**📋 本週備選（想多寫可從這裡挑）**\n"
        for name, path in extra_books:
            el = f"[[Obsidian/圖書館/{os.path.basename(path).replace('.md', '')}|{name}]]"
            extra_lines += f"- 《{el}》\n"

    content = (
        f"## ✍️ 本週寫作任務（{week_str}）\n\n"
        f"**📚 書摘推薦**\n"
        f"《{link}》還沒有你的閱讀筆記，這週花 10 分鐘填一段心得吧。\n"
        f"{extra_lines}\n"
        f"**🖊️ 小說推進**\n"
        f"本週小說任務：{novel_task}\n"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"本週任務已寫入：{out_path}")
    print(f"書摘推薦：《{primary_book_name}》")
    print(f"小說任務：{novel_task}")


def sync_status():
    """掃所有書檔：有大綱內容但狀態仍是待確認 → 自動改成已讀"""
    book_files = [
        p for p in glob.glob(f"{VAULT}/圖書館/*.md")
        if os.path.basename(p) != "instructions.md"
    ]
    updated = []
    for path in book_files:
        content = read(path)
        if "狀態: 待確認" in content and not has_no_notes(content):
            new_content = content.replace("狀態: 待確認", "狀態: 已讀", 1)
            new_content = new_content.replace("> 狀態：待確認", "> 狀態：已讀", 1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            name = os.path.splitext(os.path.basename(path))[0]
            updated.append(name)
    if updated:
        print(f"狀態同步：{len(updated)} 本改為已讀 → {', '.join(updated)}")
    else:
        print("狀態同步：無需更新")


def main():
    if not is_monday():
        print(f"今天是週{TODAY.weekday()+1}，非週一，跳過執行。")
        return

    sync_status()

    book_files = [
        p for p in glob.glob(f"{VAULT}/圖書館/*.md")
        if os.path.basename(p) != "instructions.md"
    ]
    unfilled = [p for p in book_files if has_no_notes(read(p))]

    if not unfilled:
        print("所有書籍都有筆記了！")
        return

    # 主推薦 1 本 + 備選最多 2 本
    picks = random.sample(unfilled, min(3, len(unfilled)))
    primary_path    = picks[0]
    extra_paths     = picks[1:]
    primary_content = read(primary_path)
    primary_name    = get_book_name(primary_content) or os.path.splitext(os.path.basename(primary_path))[0]

    extra_books = []
    for p in extra_paths:
        c = read(p)
        n = get_book_name(c) or os.path.splitext(os.path.basename(p))[0]
        extra_books.append((n, p))

    print(f"本週推薦補齊：《{primary_name}》（剩餘 {len(unfilled)} 本待填）")
    write_weekly_task(primary_name, primary_path, extra_books)


if __name__ == "__main__":
    main()

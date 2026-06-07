#!/usr/bin/env python3
"""
budget_import.py
匯入 LightByte Budget App 的記帳資料到 Obsidian 記帳資料夾。

功能：
- 自動找到最新的備份 zip 檔案
- 解壓縮取得 Budget.realm
- 呼叫 Node.js budget_reader.mjs 讀取 Realm 資料庫
- 依月份產生 Obsidian Markdown 筆記到 Obsidian/記帳/YYYY-MM.md

執行方式：
  python3 budget_import.py [--month YYYY-MM]
  python3 budget_import.py --all    # 重新生成所有月份
"""

import os
import sys
import json
import glob
import zipfile
import shutil
import subprocess
import datetime
import argparse
import tempfile
from collections import defaultdict

# ─── 路徑設定 ────────────────────────────────────────────────
VAULT         = os.path.expanduser(r"C:\Users\崇瑋\iCloudDrive\iCloud~md~obsidian\Obsidian")
BACKUP_DIR    = r"C:\Users\崇瑋\iCloudDrive\iCloud~com~lightByte~Budget\emergency"
SKILL_DIR     = os.path.join(VAULT, "Skills", "budget-import")
READER_SCRIPT = os.path.join(SKILL_DIR, "budget_reader.mjs")
OUTPUT_DIR    = os.path.join(VAULT, "記帳")

# ─── 分類順序（排版用）──────────────────────────────────────
CATEGORY_ORDER = ["餐飲", "交通", "購物", "娛樂", "醫教", "居家", "人情", "父母", "其他"]


def find_latest_backup():
    """找到最新的 zip 備份檔案"""
    zips = glob.glob(os.path.join(BACKUP_DIR, "*.zip"))
    if not zips:
        raise FileNotFoundError(f"找不到備份檔案：{BACKUP_DIR}")
    return max(zips, key=os.path.getmtime)


def extract_realm(zip_path: str) -> str:
    """解壓縮 zip，回傳 Budget.realm 的路徑"""
    tmp_dir = tempfile.mkdtemp(prefix="budget_realm_")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(tmp_dir)
    realm_path = os.path.join(tmp_dir, "Budget.realm")
    if not os.path.exists(realm_path):
        raise FileNotFoundError(f"解壓縮後找不到 Budget.realm in {tmp_dir}")
    return realm_path, tmp_dir


def read_realm(realm_path: str) -> list[dict]:
    """呼叫 Node.js 讀取 Realm，回傳交易清單"""
    result = subprocess.run(
        ["node", READER_SCRIPT, realm_path],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"budget_reader.mjs 失敗：{result.stderr}")
    return json.loads(result.stdout)


def group_by_month(records: list[dict]) -> dict:
    """依月份分組，回傳 {YYYY-MM: [records]}"""
    groups = defaultdict(list)
    for r in records:
        if r.get("date"):
            month = r["date"][:7]  # YYYY-MM
            groups[month].append(r)
    return dict(sorted(groups.items()))


def format_amount(amount) -> str:
    """格式化金額：加千分位"""
    try:
        return f"{int(amount):,}"
    except:
        return str(amount)


def build_monthly_note(month: str, records: list[dict]) -> str:
    """產生單月的 Markdown 筆記內容"""
    year, mon = month.split("-")
    today = datetime.date.today().isoformat()

    expenses = [r for r in records if not r.get("isIncome")]
    incomes  = [r for r in records if r.get("isIncome")]

    # 計算各分類小計
    cat_totals = defaultdict(int)
    for r in expenses:
        cat = r.get("classify") or "其他"
        cat_totals[cat] += int(r.get("amount", 0))

    total_expense = sum(cat_totals.values())
    total_income  = sum(int(r.get("amount", 0)) for r in incomes)
    net = total_income - total_expense

    lines = []
    lines.append("---")
    lines.append("類型: 記帳")
    lines.append(f"月份: {month}")
    lines.append(f"建立日期: {today}")
    lines.append(f"總支出: {total_expense}")
    lines.append(f"總收入: {total_income}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {year}年{int(mon)}月 記帳報告")
    lines.append("")

    # ── 總覽 ──────────────────────────────────────────────
    lines.append("## 總覽")
    lines.append("")
    lines.append("| 類別 | 金額（NTD） |")
    lines.append("|------|------------|")

    # 排序：按自訂順序，其他收尾
    ordered_cats = [c for c in CATEGORY_ORDER if c in cat_totals]
    leftover_cats = [c for c in cat_totals if c not in CATEGORY_ORDER]
    for cat in ordered_cats + leftover_cats:
        lines.append(f"| {cat} | {format_amount(cat_totals[cat])} |")

    lines.append(f"| **總支出** | **{format_amount(total_expense)}** |")
    if incomes:
        lines.append(f"| **總收入** | **{format_amount(total_income)}** |")
        sign = "+" if net >= 0 else ""
        lines.append(f"| **結餘** | **{sign}{format_amount(net)}** |")
    lines.append("")

    # ── 支出明細 ─────────────────────────────────────────
    if expenses:
        lines.append("## 支出明細")
        lines.append("")

        # 依分類分組
        by_cat = defaultdict(list)
        for r in expenses:
            cat = r.get("classify") or "其他"
            by_cat[cat].append(r)

        ordered_cats = [c for c in CATEGORY_ORDER if c in by_cat]
        leftover_cats = [c for c in by_cat if c not in CATEGORY_ORDER]

        for cat in ordered_cats + leftover_cats:
            cat_records = sorted(by_cat[cat], key=lambda r: r.get("date") or "")
            lines.append(f"### {cat}")
            lines.append("")
            lines.append("| 日期 | 子分類 | 金額 | 備註 |")
            lines.append("|------|-------|-----:|------|")
            for r in cat_records:
                date     = r.get("date") or ""
                subcat   = r.get("subcategory") or ""
                amount   = format_amount(r.get("amount", 0))
                remark   = r.get("remark") or ""
                lines.append(f"| {date} | {subcat} | {amount} | {remark} |")
            lines.append("")

    # ── 收入明細 ─────────────────────────────────────────
    if incomes:
        lines.append("## 收入明細")
        lines.append("")
        lines.append("| 日期 | 分類 | 子分類 | 金額 | 備註 |")
        lines.append("|------|------|-------|-----:|------|")
        for r in sorted(incomes, key=lambda r: r.get("date") or ""):
            date   = r.get("date") or ""
            cat    = r.get("classify") or ""
            subcat = r.get("subcategory") or ""
            amount = format_amount(r.get("amount", 0))
            remark = r.get("remark") or ""
            lines.append(f"| {date} | {cat} | {subcat} | {amount} | {remark} |")
        lines.append("")

    return "\n".join(lines)


def write_note(month: str, content: str):
    """寫入 Markdown 筆記到記帳資料夾"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"{month}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def main():
    parser = argparse.ArgumentParser(description="匯入 Budget App 記帳資料到 Obsidian")
    parser.add_argument("--month", help="只更新指定月份 (格式: YYYY-MM)")
    parser.add_argument("--all", action="store_true", help="重新生成所有月份")
    args = parser.parse_args()

    # 1. 找最新備份
    zip_path = find_latest_backup()
    zip_ts   = os.path.basename(zip_path).replace(".zip", "")
    print(f"使用備份：{zip_path}")

    # 2. 解壓縮
    realm_path, tmp_dir = extract_realm(zip_path)
    print(f"解壓縮到：{realm_path}")

    try:
        # 3. 讀取 Realm
        records = read_realm(realm_path)
        print(f"讀取到 {len(records)} 筆記帳記錄")

        # 4. 依月份分組
        by_month = group_by_month(records)
        print(f"共 {len(by_month)} 個月份：{', '.join(sorted(by_month.keys()))}")

        # 5. 決定要更新哪些月份
        if args.month:
            months_to_update = [args.month] if args.month in by_month else []
            if not months_to_update:
                print(f"警告：找不到 {args.month} 的記錄")
        else:
            # 預設：更新最新月份 + 上個月（以防月底補記）
            today_month = datetime.date.today().strftime("%Y-%m")
            last_month  = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y-%m")
            if args.all:
                months_to_update = sorted(by_month.keys())
            else:
                months_to_update = [m for m in [last_month, today_month] if m in by_month]

        # 6. 產生並寫入筆記
        for month in months_to_update:
            content = build_monthly_note(month, by_month[month])
            path = write_note(month, content)
            print(f"已更新：{path}")

        print("[完成] 匯入完成")

    finally:
        # 清理暫存
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
約會帳本 Step 1：解析原始匯出 CSV，分類，偵測代墊款，輸出/更新 Excel。

用法：
    python3 build_excel.py <原始CSV路徑> [--xlsx <目標xlsx路徑>]

重新執行時，如果 --xlsx 指的檔案已存在，會讀取裡面「明細」分頁的既有分類，
用 (月份, 項目描述, 金額) 當 key 比對：舊資料沿用使用者手動修正過的類別，
只有「新出現」的交易才會套用 category_rules.py 的關鍵字規則重新分類。
=> 不會蓋掉使用者在 Excel 裡手動改過的分類。
"""
import sys
import os
import re
import argparse
import pandas as pd
import openpyxl
from openpyxl.chart import BarChart, Reference

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from category_rules import classify, CAT_ORDER, CAT_COLOR, CAT_EMOJI

DEFAULT_XLSX = r"C:\Users\崇瑋\Desktop\約會記帳\約會開銷月度分析.xlsx"
DATE_PAT = re.compile(r"^(\d{2})/(\d{2})/(\d{2})\s*(.*)$")


def parse_raw_csv(csv_path: str) -> pd.DataFrame:
    """讀原始兩列一組的匯出格式，回傳每筆交易：月份/項目描述/金額/是否代墊/代墊備註。

    結構規則：
      - 角色為「付款者」的列 = 一筆交易，金額是 Claire 欄或崇瑋欄其中一個非空值
      - 它的下一列（角色「應分攤」）兩欄都有值 → 對半分攤（真的共同開銷）
        只有一欄有值、另一欄空 → 代墊（全額算在其中一人頭上，不是共同開銷）
      - 角色為「還款者/收款者」的列 = 清債結算，整組跳過，不算消費
    """
    df = pd.read_csv(csv_path, encoding="utf-8", header=None)
    df.columns = ["項目", "角色", "金額A", "金額B", "建立時間"]
    df["金額A"] = pd.to_numeric(df["金額A"], errors="coerce")
    df["金額B"] = pd.to_numeric(df["金額B"], errors="coerce")

    rows = []
    for i in df.index[df["角色"] == "付款者"]:
        paid = df.loc[i]
        if i + 1 >= len(df):
            continue
        split = df.loc[i + 1]

        text = str(paid["項目"]).strip()
        m = DATE_PAT.match(text)
        if not m:
            continue
        yy, mm, dd, desc = m.groups()
        month_key = f"{2000 + int(yy)}-{mm}"
        desc = desc.strip()

        total = paid["金額A"] if pd.notna(paid["金額A"]) else paid["金額B"]
        if pd.isna(total):
            continue
        total = abs(float(total))

        a_split = abs(split["金額A"]) if pd.notna(split["金額A"]) else 0
        b_split = abs(split["金額B"]) if pd.notna(split["金額B"]) else 0

        if a_split > 0 and b_split > 0:
            daibian_note = ""
        elif a_split > 0 and b_split == 0:
            daibian_note = "代墊(全額算Claire)"
        elif b_split > 0 and a_split == 0:
            daibian_note = "代墊(全額算崇瑋)"
        else:
            daibian_note = ""  # 異常/缺資料，當一般交易處理

        rows.append({"月份": month_key, "項目描述": desc, "金額": total, "代墊備註": daibian_note})

    return pd.DataFrame(rows)


def merge_with_existing(new_df: pd.DataFrame, xlsx_path: str) -> pd.DataFrame:
    """用 (月份,項目描述,金額) 當 key，舊明細的「類別」優先於重新分類的結果。"""
    new_df = new_df.copy()

    if not os.path.exists(xlsx_path):
        new_df["類別"] = new_df["項目描述"].apply(classify)
        return new_df

    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    if "明細" not in wb.sheetnames:
        new_df["類別"] = new_df["項目描述"].apply(classify)
        return new_df

    ws = wb["明細"]
    old_rows = list(ws.iter_rows(values_only=True))
    old_df = pd.DataFrame(old_rows[1:], columns=old_rows[0])
    old_df["金額"] = pd.to_numeric(old_df["金額"], errors="coerce")

    old_cat_lookup = {}
    for _, r in old_df.iterrows():
        key = (r["月份"], r["項目描述"], round(float(r["金額"]), 2))
        old_cat_lookup[key] = r["類別"]

    def resolve_cat(row):
        key = (row["月份"], row["項目描述"], round(row["金額"], 2))
        if key in old_cat_lookup and pd.notna(old_cat_lookup[key]):
            return old_cat_lookup[key]
        return classify(row["項目描述"])

    new_df["類別"] = new_df.apply(resolve_cat, axis=1)
    return new_df


def build_workbook(df: pd.DataFrame, xlsx_path: str):
    months = sorted(df["月份"].unique())
    grand_total = df["金額"].sum()
    categories_in_use = sorted(df["類別"].unique())
    cat_order = CAT_ORDER + [c for c in categories_in_use if c not in CAT_ORDER]

    unknown_cats = [c for c in categories_in_use if c not in CAT_COLOR]
    if unknown_cats:
        print(f"⚠️ 發現未知類別（不在 category_rules.py 裡）：{unknown_cats}")
        print("   請手動到 category_rules.py 補上 CAT_COLOR / CAT_EMOJI，否則 build_pdf.py 會用預設灰色+❓代替。")

    uncategorized = df[df["類別"] == "其他"]
    if len(uncategorized) > 0:
        print(f"ℹ️ 有 {len(uncategorized)} 筆被分到「其他」，建議去 Excel 的「明細」分頁覆核：")
        for _, r in uncategorized.iterrows():
            print(f"   {r['月份']} | {r['項目描述']} | ${r['金額']:.0f}")

    daibian = df[df["代墊備註"] != ""]
    if len(daibian) > 0:
        print(f"ℹ️ 偵測到 {len(daibian)} 筆代墊款（非對半分攤，已標記但金額仍計入總額）：")
        for _, r in daibian.iterrows():
            print(f"   {r['月份']} | {r['項目描述']} | ${r['金額']:.0f} | {r['代墊備註']}")

    # ---- 月度總覽 ----
    month_rows = []
    for i, m in enumerate(months):
        dfm = df[df["月份"] == m]
        total = dfm["金額"].sum()
        row = {"月份": m, "金額": total, "占比%": round(total / grand_total * 100, 1), "筆數": len(dfm)}
        for cat in cat_order:
            dfc = dfm[dfm["類別"] == cat]
            cat_amt = dfc["金額"].sum()
            if len(dfc) > 0:
                top = dfc.loc[dfc["金額"].idxmax()]
                top_desc, top_amt = top["項目描述"], top["金額"]
            else:
                top_desc, top_amt = "", ""
            row[f"{cat}_金額"] = cat_amt
            row[f"{cat}_最大單筆項目"] = top_desc
            row[f"{cat}_最大單筆金額"] = top_amt
        row["月總計"] = sum(row[f"{cat}_金額"] for cat in cat_order)
        if i == 0:
            row["月增減%"] = ""
        else:
            prev_total = month_rows[i - 1]["金額"]
            row["月增減%"] = round((total - prev_total) / prev_total * 100, 1) if prev_total else ""
        month_rows.append(row)

    col_order = ["月份", "金額", "占比%", "筆數"]
    for cat in cat_order:
        col_order += [f"{cat}_金額", f"{cat}_最大單筆項目", f"{cat}_最大單筆金額"]
    col_order += ["月總計", "月增減%"]
    monthly_df = pd.DataFrame(month_rows)[col_order]

    # ---- 全期類別總覽 ----
    cat_total_rows = []
    for cat in cat_order:
        dfc = df[df["類別"] == cat]
        amt = dfc["金額"].sum()
        if len(dfc) == 0:
            continue
        top = dfc.loc[dfc["金額"].idxmax()]
        cat_total_rows.append({
            "類別": cat, "總金額": amt, "筆數": len(dfc),
            "佔全期%": round(amt / grand_total * 100, 1),
            "全期最大單筆項目": top["項目描述"], "全期最大單筆金額": top["金額"],
        })
    cat_total_df = pd.DataFrame(cat_total_rows).sort_values("總金額", ascending=False)

    detail_df = df[["月份", "項目描述", "類別", "金額", "代墊備註"]]

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        monthly_df.to_excel(writer, sheet_name="月度總覽", index=False)
        cat_total_df.to_excel(writer, sheet_name="類別總覽(全期)", index=False)
        detail_df.to_excel(writer, sheet_name="明細", index=False)

    wb = openpyxl.load_workbook(xlsx_path)
    chart_months = months[-6:] if len(months) > 6 else months
    chart_df = monthly_df[monthly_df["月份"].isin(chart_months)][["月份", "金額"]].reset_index(drop=True)
    if "月度趨勢圖" in wb.sheetnames:
        del wb["月度趨勢圖"]
    ws_chart = wb.create_sheet("月度趨勢圖")
    ws_chart.append(["月份", "金額"])
    for _, r in chart_df.iterrows():
        ws_chart.append([r["月份"], r["金額"]])
    chart = BarChart()
    chart.title = "月度約會總開銷(最近6個月)"
    chart.y_axis.title = "金額"
    chart.x_axis.title = "月份"
    data_ref = Reference(ws_chart, min_col=2, min_row=1, max_row=len(chart_df) + 1)
    cats_ref = Reference(ws_chart, min_col=1, min_row=2, max_row=len(chart_df) + 1)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)
    ws_chart.add_chart(chart, "D2")
    wb.save(xlsx_path)

    print(f"\n✅ Excel 已輸出：{xlsx_path}")
    print(f"   {len(months)} 個月，{len(df)} 筆交易，總額 ${grand_total:,.0f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path", help="原始約會帳本匯出 CSV 路徑")
    ap.add_argument("--xlsx", default=DEFAULT_XLSX, help="目標 Excel 路徑（預設沿用上次的檔案位置）")
    args = ap.parse_args()

    new_df = parse_raw_csv(args.csv_path)
    merged_df = merge_with_existing(new_df, args.xlsx)
    build_workbook(merged_df, args.xlsx)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
約會帳本 Step 2：讀取（使用者已確認過分類的）Excel，產出最終 PDF。

html 只是內部中間產物，用來交給瀏覽器量高度、印成 PDF，不會留檔。

用法：
    python3 build_pdf.py [--xlsx <來源xlsx路徑>] [--out <輸出pdf路徑>]
"""
import sys
import os
import json
import base64
import argparse
import tempfile
import shutil
import subprocess

import openpyxl
import pandas as pd
from pypdf import PdfWriter, PdfReader
from selenium import webdriver
from selenium.webdriver.edge.options import Options

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from category_rules import CAT_ORDER, CAT_COLOR, CAT_EMOJI, FALLBACK_COLOR, FALLBACK_EMOJI

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_XLSX = r"C:\Users\崇瑋\Desktop\約會記帳\約會開銷月度分析.xlsx"
DEFAULT_OUT = r"C:\Users\崇瑋\Desktop\約會記帳\約會開銷_月報.pdf"
PHOTO_MAP_PATH = os.path.join(SKILL_DIR, "photo_map.json")
PHOTOS_DIR = os.path.join(SKILL_DIR, "photos")
EDGE_BIN = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PAGE_WIDTH_PX = 440

with open(PHOTO_MAP_PATH, "r", encoding="utf-8") as f:
    PHOTO_MAP = json.load(f)


def fmt(n):
    return f"{n:,.0f}"


def month_label(m):
    y, mo = m.split("-")
    return f"{y}年{int(mo)}月"


def color_of(cat):
    return CAT_COLOR.get(cat, FALLBACK_COLOR)


def emoji_of(cat):
    return CAT_EMOJI.get(cat, FALLBACK_EMOJI)


def photo_b64(desc):
    fn = PHOTO_MAP.get(desc)
    if not fn:
        return None
    path = os.path.join(PHOTOS_DIR, fn)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def tag(desc, daibian_note):
    if daibian_note:
        return f'{desc} <span style="font-size:11px;color:#eda100;font-weight:600;">🔸代墊</span>'
    return desc


HEAD = """<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ --surface-1:#fcfcfb; --page:#f9f9f7; --text-primary:#0b0b0b; --text-secondary:#52514e;
    --text-muted:#898781; --grid:#e1e0d9; --border:rgba(11,11,11,0.10); }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--page); color:var(--text-primary);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif; padding:20px 14px 30px; }}
  .wrap {{ max-width:480px; margin:0 auto; }}
  .card {{ background:var(--surface-1); border:1px solid var(--border); border-radius:16px;
    padding:0; margin-bottom:16px; overflow:hidden; }}
  .pad {{ padding:20px; }}
  .title {{ font-size:15px; color:var(--text-secondary); margin:0 0 4px; }}
  .hero {{ font-size:40px; font-weight:700; margin:0; line-height:1.1; }}
  .sub {{ font-size:13px; color:var(--text-secondary); margin-top:6px; }}
  .section-title {{ font-size:13px; color:var(--text-muted); text-transform:uppercase;
    letter-spacing:.04em; margin:0; padding:20px; }}
  .spotlight-photo {{ width:100%; height:190px; object-fit:cover; display:block; }}
  .spotlight-body {{ padding:16px 20px 20px; display:flex; align-items:center; gap:14px; }}
  .spotlight-body .emoji {{ font-size:36px; line-height:1; }}
  .spotlight-body .info .k {{ font-size:12px; color:var(--text-muted); }}
  .spotlight-body .info .item {{ font-size:16px; font-weight:600; margin:2px 0; }}
  .spotlight-body .info .amt {{ font-size:22px; font-weight:700; }}
  .donut-wrap {{ display:flex; align-items:center; gap:20px; margin-bottom:18px; padding:0 20px; }}
  .donut {{ width:130px; height:130px; border-radius:50%; flex-shrink:0; position:relative; }}
  .donut .center {{ position:absolute; inset:22px; border-radius:50%; background:var(--surface-1);
    display:flex; flex-direction:column; align-items:center; justify-content:center; }}
  .donut .center .v {{ font-size:15px; font-weight:700; }}
  .donut .center .k {{ font-size:10px; color:var(--text-muted); }}
  .legend {{ flex:1; display:flex; flex-direction:column; gap:6px; }}
  .legend .row {{ display:flex; align-items:center; gap:6px; font-size:12px; }}
  .legend .dot {{ width:8px; height:8px; border-radius:50%; flex-shrink:0; }}
  .legend .name {{ color:var(--text-secondary); flex:1; }}
  .legend .pct {{ font-weight:600; font-variant-numeric:tabular-nums; }}
  .barrow {{ margin-bottom:14px; padding:0 20px; }}
  .barrow:last-child {{ margin-bottom:20px; }}
  .barrow .label-line {{ display:flex; justify-content:space-between; font-size:14px; margin-bottom:4px; }}
  .barrow .label-line .name {{ font-weight:600; }}
  .barrow .label-line .val {{ color:var(--text-secondary); font-variant-numeric:tabular-nums; }}
  .track {{ height:10px; border-radius:5px; background:var(--grid); overflow:hidden; }}
  .fill {{ height:100%; border-radius:5px; }}
  .barrow .caption {{ font-size:12px; color:var(--text-muted); margin-top:4px; }}
  .trend {{ display:flex; align-items:flex-end; gap:10px; height:140px; padding:10px 20px 20px; }}
  .trend .col {{ flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; height:100%; }}
  .trend .bar {{ width:100%; max-width:34px; border-radius:4px 4px 0 0; background:var(--grid); }}
  .trend .bar.current {{ background:#2a78d6; }}
  .trend .amt {{ font-size:10px; color:var(--text-muted); margin-bottom:4px; font-variant-numeric:tabular-nums; }}
  .trend .mo {{ font-size:11px; color:var(--text-muted); margin-top:6px; }}
  .trend .col.current .mo {{ color:var(--text-primary); font-weight:600; }}
  .delta {{ display:inline-flex; align-items:center; gap:4px; font-size:14px; font-weight:600; margin-left:6px; }}
  .delta.up::before {{ content:"▲"; font-size:10px; }}
  .delta.down::before {{ content:"▼"; font-size:10px; }}
  .footer-note {{ font-size:12px; color:var(--text-muted); text-align:center; margin-top:10px; }}
</style></head><body><div class="wrap">
"""
TAIL = '\n  <div class="footer-note">約會帳本 · 資料自動產出</div>\n</div></body></html>\n'


def render_month_html(m, idx, months, summaries):
    s = summaries[m]
    cum = 0.0
    stops = []
    for c in s["cats"]:
        start = cum
        cum += c["pct"]
        stops.append(f"{color_of(c['cat'])} {start:.2f}% {cum:.2f}%")
    gradient = ", ".join(stops)

    legend_html = "".join(
        f'\n        <div class="row"><span class="dot" style="background:{color_of(c["cat"])};"></span>'
        f'<span class="name">{emoji_of(c["cat"])} {c["cat"]}</span><span class="pct">{c["pct"]:.0f}%</span></div>'
        for c in s["cats"]
    )
    cat_html = "".join(f"""
    <div class="barrow">
      <div class="label-line"><span class="name">{emoji_of(c['cat'])} {c['cat']}</span><span class="val">${fmt(c['amt'])} · {c['pct']:.0f}%</span></div>
      <div class="track"><div class="fill" style="width:{c['pct']:.1f}%;background:{color_of(c['cat'])};"></div></div>
      <div class="caption">最大單筆：{tag(c['top_desc'], c['top_daibian'])} ${fmt(c['top_amt'])}</div>
    </div>""" for c in s["cats"])

    window = months[max(0, idx - 5): idx + 1]
    max_total = max(summaries[w]["total"] for w in window)
    trend_html = "".join(f"""
      <div class="col {'current' if w == m else ''}">
        <div class="amt">{fmt(summaries[w]['total'])}</div>
        <div class="bar {'current' if w == m else ''}" style="height:{(summaries[w]['total']/max_total*100) if max_total else 0:.0f}%;"></div>
        <div class="mo">{w[5:]}月</div>
      </div>""" for w in window)

    delta_html = ""
    if idx > 0:
        prev_total = summaries[months[idx - 1]]["total"]
        change = (s["total"] - prev_total) / prev_total * 100 if prev_total else 0
        delta_html = f'<span class="delta {"up" if change >= 0 else "down"}">{abs(change):.0f}%　較上月</span>'

    b64 = photo_b64(s["biggest_desc"])
    if b64:
        spotlight = f"""<img class="spotlight-photo" src="data:image/jpeg;base64,{b64}" alt="{s['biggest_desc']}">
    <div class="spotlight-body"><div class="info">
      <div class="k">{s['biggest_cat']}</div>
      <div class="item">{tag(s['biggest_desc'], s['biggest_daibian'])}</div>
      <div class="amt">${fmt(s['biggest_amt'])}</div>
    </div></div>"""
    else:
        spotlight = f"""<div class="spotlight-body">
      <div class="emoji">{emoji_of(s['biggest_cat'])}</div>
      <div class="info">
        <div class="k">{s['biggest_cat']}</div>
        <div class="item">{tag(s['biggest_desc'], s['biggest_daibian'])}</div>
        <div class="amt">${fmt(s['biggest_amt'])}</div>
      </div></div>"""

    body = f"""
  <div class="card pad">
    <p class="title">{month_label(m)} 約會開銷</p>
    <p class="hero">${fmt(s['total'])}</p>
    <p class="sub">共 {s['cnt']} 筆消費 · 佔今年以來 {s['pct_all']:.1f}%</p>
  </div>
  <div class="card">
    <p class="section-title">🏆 本月最大一筆</p>
    {spotlight}
  </div>
  <div class="card">
    <p class="section-title">本月分類佔比</p>
    <div class="donut-wrap">
      <div class="donut" style="background: conic-gradient({gradient});">
        <div class="center"><div class="v">${fmt(s['total'])}</div><div class="k">合計</div></div>
      </div>
      <div class="legend">{legend_html}
      </div>
    </div>
    {cat_html}
  </div>
  <div class="card">
    <p class="section-title">近期趨勢{delta_html}</p>
    <div class="trend">{trend_html}
    </div>
  </div>
"""
    return HEAD.format(title=f"{month_label(m)} 約會開銷") + body + TAIL


def build_summaries(df):
    months = sorted(df["月份"].unique())
    grand_total = df["金額"].sum()
    cat_order = CAT_ORDER + [c for c in df["類別"].unique() if c not in CAT_ORDER]
    summaries = {}
    missing_photo_candidates = []
    for m in months:
        dfm = df[df["月份"] == m]
        total = dfm["金額"].sum()
        cats = []
        for cat in cat_order:
            dfc = dfm[dfm["類別"] == cat]
            amt = dfc["金額"].sum()
            if amt <= 0:
                continue
            top = dfc.loc[dfc["金額"].idxmax()]
            cats.append({"cat": cat, "amt": amt, "pct": amt / total * 100,
                         "top_desc": top["項目描述"], "top_amt": top["金額"],
                         "top_daibian": top.get("代墊備註", "")})
        cats.sort(key=lambda x: x["amt"], reverse=True)
        biggest = dfm.loc[dfm["金額"].idxmax()]
        summaries[m] = {
            "total": total, "cnt": len(dfm), "pct_all": total / grand_total * 100,
            "cats": cats, "biggest_desc": biggest["項目描述"], "biggest_amt": biggest["金額"],
            "biggest_cat": biggest["類別"], "biggest_daibian": biggest.get("代墊備註", ""),
        }
        if biggest["項目描述"] not in PHOTO_MAP:
            missing_photo_candidates.append((m, biggest["項目描述"], biggest["金額"]))

    if missing_photo_candidates:
        print("ℹ️ 以下「本月最大一筆」目前沒有對應真實照片，會用 emoji 代替：")
        for m, desc, amt in missing_photo_candidates:
            print(f"   {m} | {desc} | ${amt:.0f}")
        print("   想加照片的話：上網查證該項目實際是什麼店家/地點，下載照片存到 photos/，")
        print("   並在 photo_map.json 補一筆「項目描述」→檔名。")

    return months, summaries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", default=DEFAULT_XLSX)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    wb = openpyxl.load_workbook(args.xlsx, data_only=True)
    ws = wb["明細"]
    rows = list(ws.iter_rows(values_only=True))
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df["金額"] = df["金額"].astype(float)
    if "代墊備註" not in df.columns:
        df["代墊備註"] = ""
    df["代墊備註"] = df["代墊備註"].fillna("")

    months, summaries = build_summaries(df)

    tmp_dir = tempfile.mkdtemp(prefix="dating_report_")
    try:
        opts = Options()
        opts.binary_location = EDGE_BIN
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument(f"--window-size={PAGE_WIDTH_PX},1200")
        driver = webdriver.Edge(options=opts)

        html_paths = {}
        for m in months:
            html = render_month_html(m, months.index(m), months, summaries)
            path = os.path.join(tmp_dir, f"{m}.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            html_paths[m] = path

        heights = {}
        for m in months:
            driver.get("file:///" + html_paths[m].replace("\\", "/"))
            heights[m] = driver.execute_script("return document.body.scrollHeight;")
        driver.quit()

        pdf_paths = []
        for m in months:
            h = heights[m] + 10
            with open(html_paths[m], "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace(
                "</head>",
                f"<style>@media print {{ @page {{ size: {PAGE_WIDTH_PX}px {h}px; margin:0; }} "
                f"html,body {{ margin:0 !important; }} }}</style></head>",
            )
            with open(html_paths[m], "w", encoding="utf-8") as f:
                f.write(content)

            out_pdf = os.path.join(tmp_dir, f"{m}.pdf")
            subprocess.run([
                EDGE_BIN, "--headless=new", "--disable-gpu", "--no-sandbox",
                f"--print-to-pdf={out_pdf}", "--print-to-pdf-no-header",
                "file:///" + html_paths[m].replace("\\", "/"),
            ], check=True, timeout=30)
            pdf_paths.append(out_pdf)

        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        writer = PdfWriter()
        for p in pdf_paths:
            writer.append(p)
        writer.write(args.out)
        writer.close()

        print(f"\n✅ PDF 已輸出：{args.out}（{len(months)} 頁）")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()

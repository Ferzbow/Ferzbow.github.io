# -*- coding: utf-8 -*-
"""M5 · 一頁建議書(給 CMO)

所有金額由 lib/kpi.py 的營收模型即時計算(基準假設),與 Home 主頁同一套口徑。
"""
import sys
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="M5 一頁建議書", page_icon="📝", layout="wide")

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.kpi import revenue_model
from lib.ui import page_header, how_to_read, footer

page_header(
    "M5", "一頁決策",
    "📝 一頁建議書",
    "給 CMO 的單頁總結:主結論 → 三大支撐 → 風險三情境 → 一週行動清單,可下載直接貼 Slack / Email。",
    "五模組彙整 · 營收模型與決策總覽同口徑(基準假設)· SCQA + 金字塔結構",
)

DATA = Path(__file__).parent.parent / "data"

# ============================================================
# 載入所有資料計算總結數字
# ============================================================
try:
    df_customers = pd.read_csv(DATA / "customer_clustered.csv", encoding="utf-8-sig")
    df_top10 = pd.read_csv(DATA / "churn_top10.csv", encoding="utf-8-sig")
    df_forecast = pd.read_csv(DATA / "sales_top5_forecast.csv", encoding="utf-8-sig")
    df_rules = pd.read_csv(DATA / "apriori_top5_rules.csv", encoding="utf-8-sig")
    df_hist = pd.read_csv(DATA / "sales_monthly.csv", parse_dates=["date"], encoding="utf-8-sig")
except FileNotFoundError as e:
    st.error(f"找不到資料檔: {e}")
    st.stop()

# --- 營收模型(基準假設,與 Home 同一套,見 lib/kpi.py) ---
m = revenue_model(df_customers)
# 悲觀情境 = 達成率僅有樂觀情境的 1/3
m_pes = revenue_model(
    df_customers,
    m["retention_rate"] / 3, m["vip_conv_rate"] / 3, m["wake_rate"] / 3,
)

n_total, n_vip, n_atrisk, n_sleep = m["n_total"], m["n_vip"], m["n_atrisk"], m["n_sleep"]
n_top10 = len(df_top10)
n_rules = len(df_rules)
max_lift = df_rules["lift"].max()
total_forecast = df_forecast["next_yhat"].sum() if "next_yhat" in df_forecast.columns else 0

# 建議書月份 = 預測月(資料截止月 + 1),與 M3「本次預測」同口徑
next_dt = df_hist["date"].max() + pd.DateOffset(months=1)
month = f"{next_dt.year} 年 {next_dt.month} 月"

# ============================================================
# 一句話結論(SCQA · A,大字顯眼)
# ============================================================
st.markdown(f"# {month}精準行銷月度建議書")

st.success(
    f"## ⭐ 主結論:預估月度淨增營收 +{m['rev_total']:,.0f} 萬\n"
    f"### 聚焦『流失高風險群挽留』+『VIP 群套組升級』+『沉睡客喚醒』三軸行動"
)

# ============================================================
# 三大支撐(MECE · 卡片並排)
# ============================================================
st.subheader("三大支撐(MECE)")

sup1, sup2, sup3 = st.columns(3)

with sup1.container(border=True):
    st.markdown("**① 流失挽留可行**")
    st.metric("預估月增", f"+{m['rev_retain']:,.0f} 萬")
    st.markdown(
        f"- M2 鎖定 **{n_atrisk} 位** 流失高風險客戶\n"
        f"- 該群月消費 **{m['atrisk_monthly_wan']:,.0f} 萬** × 挽留率 {m['retention_rate']:.0%}\n"
        f"- 客戶經理本週逐一聯繫 + M4「回購喚回」文案跟進"
    )

with sup2.container(border=True):
    st.markdown("**② VIP 套組升級可行**")
    st.metric("預估月增", f"+{m['rev_vip']:,.0f} 萬")
    st.markdown(
        f"- M1 識別 **{n_vip} 位** VIP(占 {n_vip/n_total*100:.1f}%)\n"
        f"- 平均單筆 **{m['vip_avg_order']:,.0f} 元** × 轉換率 {m['vip_conv_rate']:.0%}\n"
        f"- M4 交叉銷售(最高 Lift {max_lift:.2f})+ M3 備貨支援"
    )

with sup3.container(border=True):
    st.markdown("**③ 沉睡客戶喚醒可行**")
    st.metric("預估月增", f"+{m['rev_wake']:,.0f} 萬")
    st.markdown(
        f"- M1 識別 **{n_sleep} 位** 沉睡客戶\n"
        f"- 平均單筆 **{m['sleep_avg_order']:,.0f} 元** × 喚醒率 {m['wake_rate']:.0%}\n"
        f"- M4 推「全站熱銷 Top 3」+ 免運喚醒文案"
    )

st.divider()

# ============================================================
# 風險評估三情境(同 Home 口徑)
# ============================================================
st.subheader("⚖ 風險評估")

col1, col2, col3 = st.columns(3)

col1.success(
    f"🟢 **樂觀情境**\n\n三軸行動全達成"
    f"(挽留 {m['retention_rate']:.0%} / 轉換 {m['vip_conv_rate']:.0%} / 喚醒 {m['wake_rate']:.0%})"
    f"\n\n**+{m['rev_total']:,.0f} 萬/月**"
)
col2.warning(
    f"🟡 **悲觀情境**\n\n達成率僅有樂觀情境的 1/3"
    f"(挽留 {m_pes['retention_rate']:.0%} / 轉換 {m_pes['vip_conv_rate']:.0%} / 喚醒 {m_pes['wake_rate']:.0%})"
    f"\n\n**+{m_pes['rev_total']:,.0f} 萬/月**"
)
col3.error(f"🔴 **不作為情境**\n\n流失高風險 {n_atrisk} 位全流失\n\n**-{m['loss_inaction']:,.0f} 萬/月**(機會成本)")

st.caption(
    f"基準假設:挽留 {m['retention_rate']:.0%} / VIP 轉換 {m['vip_conv_rate']:.0%} / 喚醒 {m['wake_rate']:.0%};"
    "敏感度分析請至 Home 主頁 What-if 模擬器現場調整"
)

st.divider()

# ============================================================
# 行動清單(HTML 表格,字級同內文,可下載成 Slack 訊息)
# ============================================================
st.subheader("📋 一週內行動清單")

action_rows = [
    ("高", "客戶經理", f"負責流失高風險群 {n_atrisk} 位挽留:記錄聯繫回饋,搭配 M4「回購喚回」文案", f"+{m['rev_retain']:,.0f} 萬"),
    ("高", "行銷", f"VIP 群 {n_vip} 位推套組:M4 交叉銷售推薦,Line OA 一週發 5 段", f"+{m['rev_vip']:,.0f} 萬"),
    ("中", "採購", f"按 M3 採購建議備貨(總量 {total_forecast:.0f} 個 ± 區間)", "降庫存風險"),
    ("中", "客服", f"沉睡客戶 {n_sleep} 位 熱銷喚醒推送(含 M2 Top {n_top10} 名單優先),本週分批發", f"+{m['rev_wake']:,.0f} 萬"),
    ("低", "資料分析師", "下月前重跑 M1-M4,以實際挽留率/轉換率校正營收模型", "下月優化"),
]
PRIO_COLOR = {"高": "#E74C3C", "中": "#F39C12", "低": "#95A5A6"}
rows_html = "".join(
    f"<tr style='border-bottom:1px solid rgba(128,128,128,0.2)'>"
    f"<td style='padding:8px 12px;white-space:nowrap'><b style='color:{PRIO_COLOR[p]}'>{p}</b></td>"
    f"<td style='padding:8px 12px;white-space:nowrap'>{o}</td>"
    f"<td style='padding:8px 12px'>{a}</td>"
    f"<td style='padding:8px 12px;white-space:nowrap'><b>{e}</b></td>"
    f"</tr>"
    for p, o, a, e in action_rows
)
st.markdown(
    f"""<table style='width:100%;font-size:1.05rem;border-collapse:collapse'>
<thead><tr style='border-bottom:2px solid rgba(128,128,128,0.4);text-align:left'>
<th style='padding:8px 12px'>優先級</th><th style='padding:8px 12px'>負責人</th>
<th style='padding:8px 12px'>動作</th><th style='padding:8px 12px'>預期效益</th>
</tr></thead>
<tbody>{rows_html}</tbody></table>""",
    unsafe_allow_html=True,
)

st.divider()

# ============================================================
# 來源模組(小卡,文字完整呈現)
# ============================================================
st.subheader("📦 主要產出來源")

source_cols = st.columns(5)
sources = [
    ("📊 M1", "客戶儀表板", f"{n_total:,} 客戶 4 群"),
    ("🚨 M2", "流失預警", f"Top {n_top10} 名單"),
    ("📈 M3", "銷量預測", "Top 5 SKU"),
    ("🎯 M4", "推薦引擎", f"{n_rules} 條規則"),
    ("📝 M5", "一頁建議書", "本頁"),
]
for col, (icon, name, kpi) in zip(source_cols, sources):
    with col.container(border=True):
        st.markdown(
            f"<div style='font-size:0.9rem;font-weight:600'>{icon} {name}</div>"
            f"<div style='font-size:0.95rem;opacity:0.85;margin-top:2px'>{kpi}</div>",
            unsafe_allow_html=True,
        )

st.download_button(
    "📥 下載建議書(Markdown,可貼 Slack / Email)",
    f"""# {month}精準行銷月度建議書

★ **主結論**:聚焦『流失高風險群挽留』+『VIP 群套組升級』+『沉睡客喚醒』,預估月度淨增營收 +{m['rev_total']:,.0f} 萬

## 三大支撐
1. **流失挽留可行** - M2 鎖定 {n_atrisk} 位流失高風險,挽留率 {m['retention_rate']:.0%} → +{m['rev_retain']:,.0f} 萬/月
2. **VIP 套組升級** - M1 識別 {n_vip} 位 VIP,M4 交叉銷售(最高 Lift {max_lift:.2f}),轉換率 {m['vip_conv_rate']:.0%} → +{m['rev_vip']:,.0f} 萬/月
3. **沉睡客戶喚醒** - {n_sleep} 位沉睡客,熱銷推薦 + 喚醒率 {m['wake_rate']:.0%} → +{m['rev_wake']:,.0f} 萬/月

## 風險評估
- 🟢 樂觀(挽留 {m['retention_rate']:.0%} / 轉換 {m['vip_conv_rate']:.0%} / 喚醒 {m['wake_rate']:.0%}): +{m['rev_total']:,.0f} 萬/月
- 🟡 悲觀(達成率僅有樂觀的 1/3): +{m_pes['rev_total']:,.0f} 萬/月
- 🔴 不作為: -{m['loss_inaction']:,.0f} 萬/月

計算口徑:月均消費 = Monetary ÷ (Tenure/30);詳見 App 內 Home 頁 What-if 模擬器

W3 第 6 組 · 智慧物流班 · BOSS III · 2026
""".encode("utf-8-sig"),
    f"{next_dt.year}年{next_dt.month}月精準行銷建議書.md",
    "text/markdown",
)

# ============================================================
# 主管判讀 + 頁尾
# ============================================================
how_to_read(
    "本頁是**定稿版**(基準假設);開會時若要現場調整挽留率/轉換率看敏感度,"
    "用 Home 的 What-if 模擬器,兩邊口徑相同。本頁可截圖直接貼 Slack 或印出。",
)
footer()

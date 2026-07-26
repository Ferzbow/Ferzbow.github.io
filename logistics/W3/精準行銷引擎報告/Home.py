# -*- coding: utf-8 -*-
"""
Home.py · BOSS III 決策總覽
==========================
給 CMO 的精準行銷引擎入口:
  30 秒結論 → 不作為損失 → What-if 模擬器 → 三前瞻訊號 → 五模組故事線 → 風險三情境
跑法:
  streamlit run Home.py
"""
import sys
import streamlit as st
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.kpi import revenue_model, DEFAULT_RETENTION, DEFAULT_VIP_CONV, DEFAULT_WAKE
from lib.ui import page_header, how_to_read, footer

st.set_page_config(
    page_title="BOSS III · 精準行銷引擎",
    page_icon="🎯",
    layout="wide",
)

page_header(
    "00", "決策總覽",
    "🎯 精準行銷引擎 — CMO 決策總覽",
    "把歷史資料轉成流失風險、下月需求與個人化推薦,讓行銷在客戶流失前先行動。",
    "1,500 位客戶主檔 × 流失預測模型 × Top 5 銷量預測 × 購物籃關聯規則",
)

# ============================================================
# 載入資料(所有數字由真資料計算,不寫死)
# ============================================================
data_dir = Path(__file__).parent / "data"

try:
    df_customers = pd.read_csv(data_dir / "customer_clustered.csv", encoding="utf-8-sig")
except FileNotFoundError:
    st.error("找不到 data/customer_clustered.csv,請先跑 prepare_data.py")
    st.stop()

try:
    df_top10 = pd.read_csv(data_dir / "churn_top10.csv", encoding="utf-8-sig")
    n_top10 = len(df_top10)
except FileNotFoundError:
    n_top10 = 0

try:
    df_rules = pd.read_csv(data_dir / "apriori_top5_rules.csv", encoding="utf-8-sig")
    n_rules = len(df_rules)
    best_rule = df_rules.sort_values("lift", ascending=False).iloc[0]
    max_lift = best_rule["lift"]
except FileNotFoundError:
    n_rules, max_lift, best_rule = 0, 0, None

# M3 前瞻訊號:Top 5 下月需求 vs 近 3 月均值
try:
    df_forecast = pd.read_csv(data_dir / "sales_top5_forecast.csv", encoding="utf-8-sig")
    df_hist = pd.read_csv(data_dir / "sales_monthly.csv", parse_dates=["date"], encoding="utf-8-sig")
    next_total = df_forecast["next_yhat"].sum()
    top5_monthly = df_hist[df_hist["is_top5"]].groupby("date")["qty"].sum().sort_index()
    base3 = top5_monthly.tail(3).mean()
except FileNotFoundError:
    next_total = base3 = None

# ============================================================
# What-if 模擬器(加分項):拉桿假設 → 即時重算下方所有金額
# ============================================================
with st.expander("🎛 What-if 模擬器:調整行銷假設,結論與風險即時重算", expanded=False):
    w1, w2, w3 = st.columns(3)
    retention_rate = w1.slider("流失挽留成功率", 0, 100, int(DEFAULT_RETENTION * 100), 5, format="%d%%") / 100
    vip_conv_rate  = w2.slider("VIP 套組轉換率", 0, 100, int(DEFAULT_VIP_CONV * 100), 5, format="%d%%") / 100
    wake_rate      = w3.slider("沉睡客喚醒率", 0, 100, int(DEFAULT_WAKE * 100), 5, format="%d%%") / 100
    st.caption(
        f"假設基準:挽留 {DEFAULT_RETENTION:.0%} / VIP 轉換 {DEFAULT_VIP_CONV:.0%} / "
        f"喚醒 {DEFAULT_WAKE:.0%}(行業常見區間),CMO 可現場調整看敏感度;M5 建議書使用基準值"
    )

# --- 營收模型(與 M5 一頁建議書同一套口徑,見 lib/kpi.py) ---
m = revenue_model(df_customers, retention_rate, vip_conv_rate, wake_rate)
# 悲觀情境 = 達成率打 1/3(跟著拉桿連動)
m_pes = revenue_model(df_customers, retention_rate / 3, vip_conv_rate / 3, wake_rate / 3)
n_total, n_vip, n_atrisk, n_sleep = m["n_total"], m["n_vip"], m["n_atrisk"], m["n_sleep"]
rev_retain, rev_vip, rev_wake, rev_total = m["rev_retain"], m["rev_vip"], m["rev_wake"], m["rev_total"]
loss_inaction = m["loss_inaction"]

# ============================================================
# CMO 30 秒結論 + 不作為損失(損失厭惡前置)
# ============================================================
st.success(
    f"📌 **CMO 30 秒結論:聚焦『流失高風險挽留』+『VIP 套組升級』+『沉睡客喚醒』,"
    f"預估月度淨增營收 +{rev_total:,.0f} 萬**(年化約 +{rev_total*12:,.0f} 萬)"
    f" ── 挽留 {n_atrisk} 位 +{rev_retain:,.0f} 萬 · VIP {n_vip} 位 +{rev_vip:,.0f} 萬 · "
    f"喚醒 {n_sleep} 位 +{rev_wake:,.0f} 萬"
)
st.error(
    f"⏳ **什麼都不做,每月損失 −{loss_inaction:,.0f} 萬,且會擴大** ── "
    f"流失高風險 {n_atrisk} 位的月消費一旦流失就全數蒸發(年化約 −{loss_inaction*12:,.0f} 萬)"
)

# ============================================================
# 風險三情境(給 CMO 的決策底線,隨 What-if 連動)
# ============================================================
st.subheader("⚖ 風險三情境")
st.caption("拉動上方 What-if 模擬器,三個情境的金額即時重算 ── 悲觀情境的達成率僅有樂觀情境的 1/3")

r1, r2, r3 = st.columns(3)
with r1:
    st.success(
        f"🟢 **樂觀情境** · 三軸行動全達成"
        f"(挽留 {retention_rate:.0%} / 轉換 {vip_conv_rate:.0%} / 喚醒 {wake_rate:.0%})"
    )
    st.metric("月增營收", f"+{rev_total:,.0f} 萬",
              delta=f"+{rev_total*12:,.0f} 萬(年化)")
with r2:
    st.warning(
        f"🟡 **悲觀情境** · 達成率僅有樂觀情境的 1/3"
        f"(挽留 {retention_rate/3:.0%} / 轉換 {vip_conv_rate/3:.0%} / 喚醒 {wake_rate/3:.0%})"
    )
    st.metric("月增營收", f"+{m_pes['rev_total']:,.0f} 萬",
              delta=f"+{m_pes['rev_total']*12:,.0f} 萬(年化)")
with r3:
    st.error(f"🔴 **不作為情境** · 流失高風險 {n_atrisk} 位全流失")
    st.metric("月損營收(機會成本)", f"-{loss_inaction:,.0f} 萬",
              delta=f"-{loss_inaction*12:,.0f} 萬(年化)")

st.caption(
    f"計算口徑:月均消費 = Monetary ÷ (Tenure/30);"
    f"挽留營收 = 流失高風險群月消費 {m['atrisk_monthly_wan']:,.0f} 萬 × 挽留率;"
    f"VIP 套組 = VIP 人數 × 轉換率 × 平均單筆訂單 {m['vip_avg_order']:,.0f} 元;"
    f"喚醒 = 沉睡人數 × 喚醒率 × 平均單筆訂單 {m['sleep_avg_order']:,.0f} 元"
)

st.divider()

# ============================================================
# 三個前瞻訊號(每張卡都有對照基準)
# ============================================================
st.subheader("📡 三個前瞻訊號")
st.caption("預知風險與需求,再把推薦送進可執行的行銷動作 ── 每個訊號都有對照基準")

s1, s2, s3 = st.columns(3)

s1.metric(
    "流失預警候選", f"{n_atrisk} 人",
    delta=f"月消費 {m['atrisk_monthly_wan']:,.0f} 萬待挽留", delta_color="inverse",
    help=f"D11 決策樹 + D14 分群;客戶經理先聯繫 Top {n_top10} 優先名單(M2)",
)

if next_total is not None:
    s2.metric(
        "Top 5 下月需求", f"{next_total:,.0f} 個",
        delta=f"{next_total - base3:+,.0f} 個 vs 近 3 月均值 {base3:,.0f}",
        help="D12 Prophet/Baseline 擇優;逐 SKU 管理缺貨與庫存風險(M3)",
    )
else:
    s2.metric("Top 5 下月需求", "資料未備妥")

s3.metric(
    "最強推薦訊號", f"Lift {max_lift:.2f}",
    delta=f"+{max_lift-1:.2f} vs 獨立購買基準 1.00",
    help=f"{best_rule['antecedent']} → {best_rule['consequent']};共 {n_rules} 條規則,關聯不等於因果(M4)" if best_rule is not None else "",
)

st.divider()

# ============================================================
# 五模組故事線(敘事導航)
# ============================================================
st.subheader("🗺 五模組故事線")
st.caption("從認識客戶到一頁決策 ── 點任一站進入模組")

story = [
    ("pages/1_M1_客戶儀表板.py", "📊 M1", f"認識 {n_total:,} 位客戶", "K-means 4 群 + R/M 散點"),
    ("pages/2_M2_流失預警.py", "🚨 M2", f"找出誰要走({n_atrisk} 位)", f"Top {n_top10} 優先聯繫名單"),
    ("pages/3_M3_銷量預測.py", "📈 M3", "算出下月備多少", "Top 5 SKU 區間預測"),
    ("pages/4_M4_推薦引擎.py", "🎯 M4 ★", "給對的人推對的品", "個人化推薦 + 3 款文案"),
    ("pages/5_M5_一頁建議書.py", "📝 M5", "一頁決策", "給 CMO 的行動清單"),
]
cols = st.columns(5)
for col, (path, code, name, desc) in zip(cols, story):
    with col:
        st.markdown(f"**{code}**")
        st.caption(desc)
        st.page_link(path, label=name, icon="➡️")

st.divider()

# ============================================================
# 主管判讀原則
# ============================================================
how_to_read(
    "客群用來**分流**、風險分數用來**排序**、預測區間用來**備貨**、關聯規則用來**設計推薦**;"
    "四種結果各司其職,不能互相取代。",
    caveat="數據可追溯(每頁標注分析基礎)· 相關不等於因果 · 區間用於風險管理,不是保證",
)

# ============================================================
# 本組 5 分鐘 Demo 腳本(上台備忘)
# ============================================================
with st.expander("🎬 本組 5 分鐘 Demo 腳本"):
    st.markdown(f"""
    | 時段 | 頁面 | 重點 |
    |---|---|---|
    | 0:00 - 0:30 | Home | SCQA 開場:30 秒結論 +{rev_total:,.0f} 萬 vs 不作為 −{loss_inaction:,.0f} 萬 |
    | 0:30 - 1:30 | Home | 三前瞻訊號 + What-if 模擬器現場拉一次 |
    | 1:30 - 2:30 | **M4 ★** | 核心 demo:輸入 ID → 個人化推薦(強調已購排除)+ 3 款文案 |
    | 2:30 - 3:30 | M5 | 一頁建議書三條支撐 |
    | 3:30 - 4:30 | Home | 風險三情境 + GenAI prompt 展示 |
    | 4:30 - 5:00 | 總結 | 本月行動 + 下月預期 |
    """)

footer()

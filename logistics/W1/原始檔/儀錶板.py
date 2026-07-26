# -*- coding: utf-8 -*-
"""
D4 任務 05「VIP 篩選器」 · 示範版（已填寫完成）
============================================================
完整實現：Pareto 圖 + RFM 計算 + 八分群 + Top 20% / At Risk 卡片 + 行動建議 + sidebar + footer

執行：
    streamlit run D4_VIP篩選器_示範.py

對應陳志騰《物流雙軸轉型三部曲》Ch03：
  - §③ 80/20 法則迷思（Pareto 圖驗證）
  - §④ RFM 三把尺
  - §⑤ 八分群矩陣

任務 05 評分 Rubric 五維度：
  1. RFM 計算（三維齊全 + 五等分 + 觀察期說明）
  2. 分群覆蓋（5+ 群，含 At Risk / Big Spenders 邊緣群）
  3. 行動建議品質（具體 + 量化，不是「加強服務」）
  4. 反直覺洞察（挑戰預設假設）
  5. Excel 可讀性（條件格式 + 行動優先級）
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

# ============================================================
# §0 頁面設定
# ============================================================
st.set_page_config(
    page_title="A 物流 · VIP 篩選器",
    layout="wide",
    page_icon="🎯",
)

SNAPSHOT = pd.Timestamp("2025-07-01")  # 觀察期結束日

# 八分群 → 行動建議對照
ACTION_PLAYBOOK = {
    "VIP (Champions) 🛡 鎖":
        "指派專屬客服 + 月度業務拜訪 + 優先排車 + 年度合約續約",
    "Loyal 🌱 養":
        "推薦升級方案 + 捆綁服務 + 季度滿意度調查",
    "Big Spenders 💸 挖":
        "從單次合作升到長期合約 + 客製化大宗折扣",
    "New/Promising 🌀 引":
        "首購優惠 + 流程引導手冊 + 30 天內回訪",
    "Potential Loyalists 🌱 扶":
        "主動詢問需求 + 客製化方案 + 推薦 VIP 升級路徑",
    "At Risk 🚨 救":
        "業務經理親自拜訪 + 客製化回流方案 + 14 天內回應",
    "Hibernating ⏰ 喚":
        "節慶期主動聯絡 + 限時回流優惠",
    "Lost 👋 放":
        "不主動投資資源 · EDM 留檔即可",
}

# ============================================================
# §1 載入 D2 CLEAN.csv + 計算 RFM
# ============================================================
BASE = Path(__file__).parent
_candidates = [
    BASE / ".." / "D2_資料清洗" / "out" / "A_物流_訂單配送_CLEAN.csv",
    BASE / "A_物流_訂單配送_CLEAN.csv",
]
ORDERS = next((p for p in _candidates if p.exists()), _candidates[0])
print(f"[載入] {ORDERS.parent.name}/{ORDERS.name}")


@st.cache_data
def load_and_rfm():
    df = pd.read_csv(ORDERS, encoding="utf-8-sig",
                     parse_dates=["order_date", "ship_datetime", "delivery_datetime"])

    snapshot = SNAPSHOT

    rfm = df.groupby(["customer_id", "customer_name"]).agg(
        R=("order_date", lambda x: (snapshot - x.max()).days),
        F=("order_id", "count"),
        M=("freight_twd", "sum"),
    ).reset_index()

    rfm["R_score"] = pd.qcut(rfm["R"].rank(method="first"), 5,
                              labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F_score"] = pd.qcut(rfm["F"].rank(method="first"), 5,
                              labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["M"].rank(method="first"), 5,
                              labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_score"] = (rfm["R_score"].astype(str) +
                         rfm["F_score"].astype(str) +
                         rfm["M_score"].astype(str))

    def classify(row):
        R, F, M = row["R_score"], row["F_score"], row["M_score"]
        if R >= 4 and F >= 4 and M >= 4:
            return "VIP (Champions) 🛡 鎖"
        elif R >= 3 and F >= 4 and M >= 3:
            return "Loyal 🌱 養"
        elif R >= 4 and F <= 2 and M >= 4:
            return "Big Spenders 💸 挖"
        elif R >= 4 and F <= 2 and M <= 2:
            return "New/Promising 🌀 引"
        elif R >= 4 and F == 3:
            return "Potential Loyalists 🌱 扶"
        elif R <= 2 and F >= 3 and M >= 3:
            return "At Risk 🚨 救"
        elif R <= 2 and F <= 2 and M >= 3:
            return "Hibernating ⏰ 喚"
        else:
            return "Lost 👋 放"

    rfm["segment"] = rfm.apply(classify, axis=1)

    # 計算配送時長（小時）
    df["delivery_hours"] = (df["delivery_datetime"] - df["ship_datetime"]).dt.total_seconds() / 3600

    return df, rfm


df, rfm = load_and_rfm()

# ============================================================
# §2 Sidebar 篩選
# ============================================================
st.sidebar.title("🔍 篩選")
all_segments = sorted(rfm["segment"].unique())
sel_segments = st.sidebar.multiselect(
    "顯示分群", all_segments, default=all_segments,
)
rfm_f = rfm[rfm["segment"].isin(sel_segments)]

st.sidebar.divider()
st.sidebar.caption(f"📅 RFM 觀察期結束日：{SNAPSHOT.date()}")
st.sidebar.caption(f"📊 訂單筆數：{len(df):,}")
st.sidebar.caption(f"👥 客戶總數：{len(rfm)}")

# ============================================================
# §3 標題
# ============================================================
st.title("🎯 A 物流公司 · VIP 篩選器")
st.caption(f"訂單 {len(df):,} 筆 · 客戶 {len(rfm)} 個 · "
           f"觀察期到 {SNAPSHOT.date()}")

# ============================================================
# §3.1 Dashboard 設計原則（展開式說明）
# ============================================================
with st.expander("📐 Dashboard 設計原則（F型閱讀 / DIKW / 30秒掌握重點）", expanded=False):
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(
            "### 👁 F 型閱讀\n"
            "讀者視線依 **F 型路徑**掃描頁面：\n"
            "- 第一橫：頁面頂部標題與 KPI 卡片\n"
            "- 第二橫：副標題與圖表\n"
            "- 垂直掃：左側邊欄重點\n\n"
            "**→ 最重要的訊息放左上角**"
        )
    with d2:
        st.markdown(
            "### 🔺 DIKW 架構\n"
            "| 層次 | 說明 | 本頁對應 |\n"
            "|------|------|---------|\n"
            "| Data | 原始訂單 | CSV 數據 |\n"
            "| Information | RFM 計算結果 | 三維分數 |\n"
            "| Knowledge | 八分群洞察 | 分群建議卡 |\n"
            "| Wisdom | 管理行動 | 行動優先序 |"
        )
    with d3:
        st.markdown(
            "### ⏱ 30 秒掌握重點\n"
            "好的 Dashboard 讓主管在 30 秒內看到：\n"
            "1. **現在最緊急的問題**（At Risk 警示）\n"
            "2. **最有價值的客戶**（Top 20%）\n"
            "3. **下一步行動**（行動建議卡）\n\n"
            "*設計原則：資訊密度 × 視覺層級 × 行動導向*"
        )

# ============================================================
# §4 三大核心 KPI（5.1）
# ============================================================
n_top = max(int(len(rfm) * 0.2), 1)
top20_pct = rfm.nlargest(n_top, "M")["M"].sum() / rfm["M"].sum() * 100

# KPI 數值（固定值或從資料計算）
SENSOR_FAULT_RATE = 10.5        # 感測器故障率（%）—— 使用者指定
TOTAL_QTY = int(df["qty"].sum()) # 總載運件數
AVG_DELIVERY_HRS = df["delivery_hours"].mean()
MEDIAN_DELIVERY_HRS = df["delivery_hours"].median()

st.subheader("📊 5.1 三大核心 KPI 指標")
k1, k2, k3 = st.columns(3)

k1.metric(
    "⚠ 感測器故障率",
    f"{SENSOR_FAULT_RATE}%",
    "嚴重超標（上限 2.0%）",
    delta_color="inverse",
    help="感測器故障率超過 2.0% 上限，設備維修需求緊迫",
)
k2.metric(
    "📦 總載運件數",
    f"{TOTAL_QTY:,}",
    "倉庫與車隊實際吞吐負載",
    delta_color="off",
    help="觀察期內真實反映倉庫與車隊的物理吞吐負載",
)
k3.metric(
    "🚚 平均配送時長",
    f"{AVG_DELIVERY_HRS:.1f} 小時",
    f"中位數 {MEDIAN_DELIVERY_HRS:.0f} 小時",
    delta_color="off",
    help="衡量物流效率；中位數反映典型配送時間",
)

# ============================================================
# §5 冷鏈達標率預警 KRI（5.2）
# ============================================================
st.divider()
st.subheader("🌡 5.2 冷鏈達標率預警（KRI）")

# 固定數值（使用者指定）
COLD_RATE_LOW = 73.8
COLD_RATE_HIGH = 74.7
COLD_REDLINE = 99.5

st.error(
    f"**冷鏈達標率預警（KRI）**\n\n"
    f"目前冷鏈溫控達標率僅為 **{COLD_RATE_LOW}% ~ {COLD_RATE_HIGH}%**，"
    f"遠低於 **{COLD_REDLINE}%** 的紅線。\n\n"
    f"管理者應優先排查 **故障感測器** 與 **深夜配送時段** 的異常。"
)

# --- 冷鏈預警圖（月別趨勢） ---
st.markdown("#### 📉 冷鏈預警圖（月別達標率趨勢）")

months_list = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07"]
np.random.seed(7)
cold_vals = [76.2, 75.8, 74.1, 73.8, 74.7, 74.2, 73.9]
cold_trend = pd.DataFrame({"月份": months_list, "冷鏈達標率": cold_vals})

fig_cold = go.Figure()
fig_cold.add_trace(go.Scatter(
    x=cold_trend["月份"], y=cold_trend["冷鏈達標率"],
    mode="lines+markers", name="冷鏈達標率",
    line=dict(color="#1f77b4", width=3),
    marker=dict(
        size=12,
        color=["#e74c3c" for _ in cold_vals],  # 全部紅色（全部低於紅線）
        symbol="circle",
    ),
    fill="tozeroy", fillcolor="rgba(231,76,60,0.08)",
))
fig_cold.add_hline(
    y=COLD_REDLINE, line=dict(dash="dot", color="red", width=2),
    annotation_text=f"紅線 {COLD_REDLINE}%", annotation_position="top right",
)
fig_cold.update_layout(
    yaxis=dict(range=[60, 105], title="達標率 %"),
    xaxis_title="月份",
    height=300, margin=dict(l=10, r=10, t=20, b=10),
)
st.plotly_chart(fig_cold, use_container_width=True)

# 紅底驚嘆號警告列（冷鏈）
st.markdown(
    """
    <div style="background:#e74c3c;color:white;padding:10px 18px;border-radius:6px;font-weight:bold;font-size:1rem;">
    ❗ 警告：各月冷鏈達標率均遠低於紅線 99.5%，請立即啟動冷鏈異常追蹤流程！
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("")  # 間距

# --- 各車輛冷鏈達標率排行 ---
st.markdown("#### 🚛 各車輛冷鏈達標率排行（由低到高）")

vehicle_data = pd.DataFrame({
    "車輛": ["V-014", "V-007", "V-021", "V-003", "V-018",
             "V-011", "V-009", "V-016", "V-005", "V-012"],
    "冷鏈達標率(%)": [55.4, 61.2, 65.8, 68.3, 70.1,
                      72.6, 74.3, 76.9, 78.4, 80.2],
}).sort_values("冷鏈達標率(%)", ascending=True).reset_index(drop=True)

fig_vehicle = px.bar(
    vehicle_data,
    x="冷鏈達標率(%)", y="車輛",
    orientation="h",
    color="冷鏈達標率(%)",
    color_continuous_scale=[(0, "#e74c3c"), (0.4, "#f39c12"), (1, "#2ecc71")],
    text="冷鏈達標率(%)",
)
fig_vehicle.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig_vehicle.add_vline(
    x=COLD_REDLINE, line=dict(dash="dot", color="red", width=2),
    annotation_text=f"紅線 {COLD_REDLINE}%", annotation_position="top right",
)
fig_vehicle.update_layout(
    height=360, margin=dict(l=10, r=80, t=20, b=10),
    coloraxis_showscale=False,
    xaxis=dict(range=[40, 105]),
)
st.plotly_chart(fig_vehicle, use_container_width=True)

# 紅底驚嘆號警告列（V-014）
st.markdown(
    """
    <div style="background:#e74c3c;color:white;padding:10px 18px;border-radius:6px;font-weight:bold;font-size:1rem;">
    ❗ V-014 達標率僅 55.4%，表現最差，建議立即召回進行冷凍設備檢修！
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("")  # 間距

# ============================================================
# §6 Pareto 分析（6.1）+ RFM 分析（6-1.2）
# ============================================================
st.divider()
st.subheader("📊 6.1 Pareto 分析：找出 Top 20% 高價值客戶")
st.info(
    f"依 Pareto（80/20）法則，前 **{n_top}** 位客戶貢獻了最多運費。\n\n"
    f"→ 本資料實際為 **Top 20% 貢獻 {top20_pct:.1f}%** 運費，"
    f"{'低於' if top20_pct < 80 else '高於'} 教科書 80/20，"
    f"代表客戶結構{'較分散' if top20_pct < 80 else '集中'}。"
)

df_cust = (rfm[["customer_name", "M"]]
           .sort_values("M", ascending=False).reset_index(drop=True))
df_cust["rank_pct"] = (df_cust.index + 1) / len(df_cust) * 100
df_cust["cum_pct"] = df_cust["M"].cumsum() / df_cust["M"].sum() * 100

fig_pareto = go.Figure()
fig_pareto.add_trace(go.Scatter(
    x=df_cust["rank_pct"], y=df_cust["cum_pct"],
    mode="lines+markers", name="實際累積貢獻",
    line=dict(color="#1f3a5f", width=3),
    marker=dict(size=10, color="#ea7b2c"),
))
fig_pareto.add_trace(go.Scatter(
    x=[0, 100], y=[0, 100], mode="lines",
    name="完全分散（對角線）",
    line=dict(color="gray", dash="dash"),
))
fig_pareto.add_hline(y=80, line=dict(dash="dot", color="red"))
fig_pareto.add_vline(x=20, line=dict(dash="dot", color="red"))
fig_pareto.update_layout(
    xaxis_title="客戶排名 %（由高到低）",
    yaxis_title="累積運費貢獻 %",
    height=380, margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_pareto, use_container_width=True)

# --- 6-1.2 RFM 分析說明 ---
st.subheader("🧩 6-1.2 RFM 分析")
r1, r2, r3 = st.columns(3)
with r1:
    st.markdown(
        "### 📅 R — Recency（最近消費）\n"
        "距今天多少天沒有下單。\n\n"
        "- R 分數越高 = 越近期消費\n"
        "- R 低代表客戶可能在流失中\n"
        "- 觀察期結束日：**2025-07-01**"
    )
with r2:
    st.markdown(
        "### 🔁 F — Frequency（購買頻率）\n"
        "觀察期內共下了幾筆訂單。\n\n"
        "- F 高 = 忠誠、高黏著\n"
        "- F 低但 M 高 = Big Spenders（風險群）"
    )
with r3:
    st.markdown(
        "### 💰 M — Monetary（消費金額）\n"
        "觀察期內累計運費總額（TWD）。\n\n"
        "- M 高 = 高價值客戶\n"
        "- M 需搭配 R/F 才能判斷是否穩定"
    )

# ============================================================
# §7 八大分群分析（6.2.1）
# ============================================================
st.divider()
st.subheader("🗂 6.2.1 八大分群分析")

col_a, col_b = st.columns([1, 2])

with col_a:
    st.markdown("**八分群分布**")
    seg_count = rfm_f["segment"].value_counts().reset_index()
    seg_count.columns = ["分群", "客戶數"]
    fig_seg = px.bar(
        seg_count, x="客戶數", y="分群", orientation="h",
        color="客戶數",
        color_continuous_scale=[(0, "#fcead5"), (1, "#1f3a5f")],
    )
    fig_seg.update_layout(
        height=350, margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_seg, use_container_width=True)

with col_b:
    st.markdown("**👥 客戶 RFM 明細**")
    st.dataframe(
        rfm_f[["customer_name", "segment", "R", "F", "M",
               "R_score", "F_score", "M_score", "RFM_score"]]
          .sort_values("M", ascending=False)
          .style.background_gradient(subset=["M"], cmap="Blues")
          .background_gradient(subset=["R"], cmap="RdYlGn_r"),
        use_container_width=True, hide_index=True,
    )

# 八大分群重點說明
st.markdown("**重點分群說明：**")
seg_insight_col1, seg_insight_col2, seg_insight_col3 = st.columns(3)
with seg_insight_col1:
    st.success(
        "**🛡 (1) VIP (Champions)：C003 水產鮮活 B2B**\n\n"
        "M 值極高，為核心高價值客戶。\n"
        "需指派專屬客服以防流失，並定期業務拜訪維持黏著度。"
    )
with seg_insight_col2:
    st.error(
        "**🚨 (2) At Risk（救）：C007 統一生鮮、C008 PChome 24h**\n\n"
        "消費金額高但近期無下單，是最該優先投資資源的群體。\n"
        "業務經理應本週內親自拜訪，14 天內提出客製化回流方案。"
    )
with seg_insight_col3:
    st.info(
        "**🌀 (3) New / Promising（引）：C001 7-11 零售連鎖**\n\n"
        "潛力巨大，需引導其增加交易頻率。\n"
        "建議首購優惠 + 30 天內回訪 + 流程引導手冊加速轉化。"
    )

# RFM 矩陣
st.subheader("🗺 RFM 矩陣（八大分群視覺化）")
st.caption("X 軸：F 分數（購買頻率）｜Y 軸：R 分數（最近消費）｜點大小：M（消費金額）｜顏色：分群")

SEG_COLORS = {
    "VIP (Champions) 🛡 鎖": "#1f3a5f",
    "Loyal 🌱 養": "#2ecc71",
    "Big Spenders 💸 挖": "#f39c12",
    "New/Promising 🌀 引": "#3498db",
    "Potential Loyalists 🌱 扶": "#1abc9c",
    "At Risk 🚨 救": "#e74c3c",
    "Hibernating ⏰ 喚": "#95a5a6",
    "Lost 👋 放": "#7f8c8d",
}
rfm_f = rfm_f.copy()
rfm_f["color"] = rfm_f["segment"].map(SEG_COLORS).fillna("#aaa")

fig_rfm = px.scatter(
    rfm_f,
    x="F_score", y="R_score",
    size="M", color="segment",
    hover_name="customer_name",
    hover_data={"R": True, "F": True, "M": ":,.0f",
                "R_score": True, "F_score": True, "M_score": True},
    color_discrete_map=SEG_COLORS,
    labels={"F_score": "F 分數（購買頻率）", "R_score": "R 分數（最近消費）"},
    size_max=50,
)
fig_rfm.update_layout(
    height=420, margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(tickvals=[1,2,3,4,5], ticktext=["1（低）","2","3","4","5（高）"]),
    yaxis=dict(tickvals=[1,2,3,4,5], ticktext=["1（舊）","2","3","4","5（新）"]),
    legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="left", x=0),
)
fig_rfm.add_annotation(x=4.5, y=4.5, text="VIP 區",
    showarrow=False, font=dict(color="#1f3a5f", size=12))
fig_rfm.add_annotation(x=1.5, y=1.5, text="Lost/風險區",
    showarrow=False, font=dict(color="#e74c3c", size=12))
st.plotly_chart(fig_rfm, use_container_width=True)

# ============================================================
# §8 Top 20% 關鍵名單（6-2.2）
# ============================================================
st.divider()
st.subheader(f"🛡 6-2.2 Top 20% 關鍵名單（鎖）（{n_top} 個客戶）")
top20 = rfm.nlargest(n_top, "M")[
    ["customer_name", "segment", "R", "F", "M"]
]
st.dataframe(top20, use_container_width=True, hide_index=True)

# ============================================================
# §9 At Risk 警示（救）
# ============================================================
st.subheader("🚨 At Risk 客戶警示（救）")
at_risk = rfm[rfm["segment"].str.contains("At Risk")]
if len(at_risk):
    for _, row in at_risk.iterrows():
        st.error(
            f"⚠ **{row['customer_name']}** - "
            f"最近 {row['R']} 天沒下單 · "
            f"歷史 {row['F']} 筆訂單 · 累計 NT$ {row['M']:,.0f} — "
            f"**業務經理本週內必須拜訪**"
        )
else:
    st.success(
        "✓ 本次資料中沒有客戶落入 At Risk 群 — "
        "但要持續監控 R 分數變動，有客戶 R 分數從 4 掉到 2 就要警戒。"
    )

# ============================================================
# §10 八分群行動建議卡
# ============================================================
st.divider()
st.subheader("📋 八分群行動建議")

cols = st.columns(2)
for i, (seg, action) in enumerate(ACTION_PLAYBOOK.items()):
    members_in_data = rfm[rfm["segment"] == seg]["customer_name"].tolist()
    has_member = len(members_in_data) > 0
    with cols[i % 2]:
        if has_member:
            st.info(
                f"**{seg}**（{len(members_in_data)} 個："
                f"{', '.join(members_in_data)}）\n\n"
                f"→ {action}"
            )
        else:
            st.markdown(
                f":gray[**{seg}**（本次資料無）\n\n→ {action}]"
            )

# ============================================================
# §11 Footer
# ============================================================
st.divider()
st.caption(
    f"📌 資料來源：D2 清洗後 CSV — `A_物流_訂單配送_CLEAN.csv` · "
    f"RFM 觀察期結束 {SNAPSHOT.date()}"
)
st.caption(
    "📚 對應 Ch03 §③（80/20 迷思）· §④（RFM 三把尺）· §⑤（八分群矩陣）"
)

# ============================================================
# 完成後請寫：
#   1. out/客戶分層名單.xlsx（rfm + segment）
#   2. out/業務行動書.md（Top 20% 鎖、At Risk 救，各 ≥ 3 項具體行動）
#   3. 截圖.png（完整頁面）
# 並壓 zip 上傳「智慧物流學習平台 / Day4 / 任務05_VIP篩選器/」
# 檔名：D4_第N組.zip · 截止 16:00
# ============================================================

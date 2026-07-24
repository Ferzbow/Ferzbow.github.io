# -*- coding: utf-8 -*-
"""M1 · 客戶儀表板"""
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="M1 客戶儀表板", page_icon="📊", layout="wide")

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.ui import page_header, how_to_read, footer

page_header(
    "M1", "看誰是誰",
    "📊 客戶儀表板",
    "以 K-means 將 1,500 位客戶分成 4 群,從消費近度 × 消費金額看價值與活躍輪廓,決定行銷資源怎麼分。",
    "1,500 位客戶 RFM 指標 × K-means 分群(4 群)",
)

DATA = Path(__file__).parent.parent / "data"

try:
    df = pd.read_csv(DATA / "customer_clustered.csv", encoding="utf-8-sig")
except FileNotFoundError:
    st.error("找不到 data/customer_clustered.csv,請先跑 prepare_data.py")
    st.stop()

# ============================================================
# 四群卡片(人數 + R/F/M 中位數 + 建議動作)
# ============================================================
st.subheader("四群輪廓與建議動作")

CLUSTER_CARDS = [
    ("VIP 高頻高額", "👑", "升級服務 / 套組推薦 / 專屬客服"),
    ("穩定中段",     "🌱", "持續經營 / 新品推薦"),
    ("流失高風險",   "⚠️", "電話挽留 / 折扣券 / 客服主動聯繫"),
    ("沉睡客戶",     "💤", "喚醒推送 / 重大優惠 / 重新破冰"),
]

cluster_counts = df["cluster_name"].value_counts()
med = df.groupby("cluster_name")[["Recency", "Frequency", "Monetary"]].median()

cols = st.columns(4)
for col, (name, icon, action) in zip(cols, CLUSTER_CARDS):
    n = cluster_counts.get(name, 0)
    pct = n / len(df) * 100 if len(df) > 0 else 0
    with col.container(border=True):
        st.markdown(f"**{icon} {name}**")
        st.metric("人數", f"{n} 人", delta=f"占 {pct:.1f}%", delta_color="off")
        if name in med.index:
            st.markdown(
                f"最近消費(R)中位:**{med.loc[name, 'Recency']:.0f} 天**  \n"
                f"消費頻率(F)中位:**{med.loc[name, 'Frequency']:.0f} 次**  \n"
                f"消費金額(M)中位:**{med.loc[name, 'Monetary']:,.0f} 元**"
            )
        st.caption(f"🎬 建議動作:{action}")

st.divider()

# ============================================================
# R × M 散點圖
# ============================================================
st.subheader("客戶散點圖(最近消費 R × 消費金額 M)")

df_plot = df.copy()
df_plot["log_Monetary"] = np.log1p(df_plot["Monetary"])

fig = px.scatter(
    df_plot,
    x="Recency",
    y="log_Monetary",
    color="cluster_name",
    hover_data=["customer_id", "Frequency", "Monetary", "ComplaintCnt"],
    title="客戶 RFM 分布(顏色 = K-means 群)",
    labels={"Recency": "最近消費 R(天)", "log_Monetary": "消費金額 M(對數)", "cluster_name": "分群"},
    height=500,
    color_discrete_map={
        "VIP 高頻高額": "#E74C3C",
        "穩定中段":     "#3498DB",
        "流失高風險":   "#F39C12",
        "沉睡客戶":     "#95A5A6",
    },
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# 一鍵下載
# ============================================================
st.download_button(
    "📥 下載完整客戶分群表(CSV)",
    df.to_csv(index=False).encode("utf-8-sig"),
    "customer_clustered.csv",
    "text/csv",
)

# ============================================================
# 主管判讀 + 頁尾
# ============================================================
how_to_read(
    "客群用來**分流資源**:VIP 拉客單、穩定提頻、流失挽留、沉睡喚醒;"
    "四群的推薦邏輯與文案調性見 M4 策略速查表。",
    caveat="群不是永久標籤 ── 客戶行為變了群就變,每月重跑分群",
)
footer()

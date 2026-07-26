# -*- coding: utf-8 -*-
"""M3 · 銷量預測"""
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="M3 銷量預測", page_icon="📈", layout="wide")

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.ui import page_header, how_to_read, footer

DATA = Path(__file__).parent.parent / "data"

try:
    forecast = pd.read_csv(DATA / "sales_top5_forecast.csv", encoding="utf-8-sig")
    history = pd.read_csv(DATA / "sales_monthly.csv", parse_dates=["date"], encoding="utf-8-sig")
except FileNotFoundError:
    st.error("找不到 data/sales_top5_forecast.csv 或 sales_monthly.csv,請先跑 D12 並 prepare_data.py")
    st.stop()

# 分析起迄與預測時間點(由資料計算,不寫死)
hist_start = history["date"].min().strftime("%Y-%m")
hist_end = history["date"].max().strftime("%Y-%m")
n_months = history["date"].nunique()
next_month = (history["date"].max() + pd.DateOffset(months=1)).strftime("%Y-%m")

page_header(
    "M3", "看下一期賣多少",
    "📈 銷量預測",
    "切換 Top 5 品項,看歷史趨勢、下月點估與 80% 信賴區間,加上異常旗提示備貨風險。",
    f"{n_months} 個月月銷量({hist_start} ~ {hist_end})× Top 5 品項 · 本次預測 {next_month} · Prophet 與 Baseline 同窗擇優",
)

# 下拉選單字體放大(適度)
st.markdown("""
<style>
[data-testid="stSelectbox"] div[data-baseweb="select"] > div { font-size: 1.25rem; }
[data-testid="stSelectbox"] label p { font-size: 1.05rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SKU 篩選器
# ============================================================
# forecast / history 都有品號(sku_id,與 D12 共用)與品名(sku / sku_name)
sku_list = forecast["sku"].tolist()          # 品名
label = dict(zip(forecast["sku"], forecast["sku_id"]))   # 品名 → 品號
selected = st.selectbox("選擇商品", sku_list,
                        format_func=lambda n: f"{n}({label[n]})")

row = forecast[forecast["sku"] == selected].iloc[0]
st.caption(f"品號 `{row['sku_id']}` 連結銷量預測;品名「{selected}」連結交易與推薦規則(M4)── 同一支商品前後說的是同一件事")

# ============================================================
# 異常旗:下月點估 vs 近 3 月均值(±10% 內視為正常)
# ============================================================
hist_sel = history[history["sku_name"] == selected].sort_values("date")
base3 = hist_sel["qty"].tail(3).mean()
dev = (row["next_yhat"] - base3) / base3 if base3 else 0

if dev > 0.10:
    flag = f"🔥 **過熱** · 高於近 3 月均值 {base3:,.0f} 個 {dev:+.0%} → 提早備貨,注意缺貨風險"
elif dev < -0.10:
    flag = f"❄️ **過冷** · 低於近 3 月均值 {base3:,.0f} 個 {dev:+.0%} → 保守進貨,注意庫存積壓"
else:
    flag = f"✅ **正常** · 與近 3 月均值 {base3:,.0f} 個相差 {dev:+.0%}(±10% 內)"

# ============================================================
# 採購建議(主結論,大字)+ 異常旗
# ============================================================
st.success(
    f"### 📦 建議備貨 {row['next_yhat']:,.0f} 個 ± {(row['next_upper']-row['next_lower'])/2:,.0f}\n"
    f"80% 信賴區間:**{row['next_lower']:,.0f} ~ {row['next_upper']:,.0f}** 個"
)
st.markdown(flag)

# ============================================================
# Decision badge
# ============================================================
col1, col2, col3 = st.columns(3)
col1.metric("Prophet MAPE", f"{row['prophet_mape']:.1f}%")
col2.metric("Best Baseline MAPE", f"{row['baseline_mape']:.1f}%",
             delta=f"{row['diff_pp']:+.1f}pp",
             delta_color="normal" if row['diff_pp'] > 0 else "inverse")
col3.metric("採用模型", "Prophet" if "Prophet" in row['decision'] else "Baseline")

st.caption(f"決策依據:{row['decision']}")

st.divider()

# ============================================================
# 歷史 + 區間預測線
# ============================================================
st.subheader(f"{selected} 月銷量趨勢 + 預測區間")

hist = history[history["sku_name"] == selected].sort_values("date")   # 依品名(品號在 sku_id 欄)

fig = go.Figure()

# 歷史實績
fig.add_trace(go.Scatter(
    x=hist["date"], y=hist["qty"],
    mode="lines+markers", name="歷史實績",
    line=dict(color="#3498DB", width=2),
))

# 預測點 + 區間
last_date = hist["date"].max()
next_date = last_date + pd.DateOffset(months=1)

fig.add_trace(go.Scatter(
    x=[last_date, next_date], y=[hist["qty"].iloc[-1], row["next_yhat"]],
    mode="lines+markers", name="預測點估",
    line=dict(color="#E74C3C", width=2, dash="dash"),
    marker=dict(size=12),
))

fig.add_trace(go.Scatter(
    x=[next_date, next_date], y=[row["next_lower"], row["next_upper"]],
    mode="lines", name="80% 信賴區間",
    line=dict(color="#F39C12", width=8),
    showlegend=True,
))

fig.update_layout(
    height=450,
    xaxis_title="月份",
    yaxis_title="銷量(qty)",
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# 全 5 SKU 總覽表
# ============================================================
st.subheader("Top 5 全部預測表")

def sku_flag(r):
    """異常旗:下月點估 vs 該 SKU 近 3 月均值(±10% 內視為正常)"""
    b3 = history[history["sku_name"] == r["sku"]].sort_values("date")["qty"].tail(3).mean()
    if not b3:
        return "—"
    d = (r["next_yhat"] - b3) / b3
    return f"🔥 過熱 {d:+.0%}" if d > 0.10 else (f"❄️ 過冷 {d:+.0%}" if d < -0.10 else f"✅ 正常 {d:+.0%}")

show_df = pd.DataFrame({
    "品名":          forecast["sku"],
    "採用模型":      forecast["decision"],
    "Prophet MAPE":  forecast["prophet_mape"].map(lambda v: f"{v:.2f}%"),
    "Baseline MAPE": forecast["baseline_mape"].map(lambda v: f"{v:.2f}%"),
    "下界":          forecast["next_lower"].round().astype(int),
    "點估":          forecast["next_yhat"].round().astype(int),
    "上界":          forecast["next_upper"].round().astype(int),
    "建議備貨":      forecast.apply(
        lambda r: f"{r['next_yhat']:.0f} ± {(r['next_upper']-r['next_lower'])/2:.0f}", axis=1),
    "異常旗":        forecast.apply(sku_flag, axis=1),
})
show_df.index = range(1, len(show_df) + 1)
st.dataframe(show_df, use_container_width=True)

st.download_button(
    "📥 下載 Top 5 預測(CSV,給採購)",
    forecast.to_csv(index=False).encode("utf-8-sig"),
    "sales_top5_forecast.csv",
    "text/csv",
)

# ============================================================
# 主管判讀 + 頁尾
# ============================================================
how_to_read(
    "先看**點估**排定基準量,再用**區間**討論風險:往下界備貨降庫存但提高缺貨風險,往上界相反;"
    "**逐 SKU 決策**,不要把總量平均分配;過熱/過冷旗先查有無促銷或季節因素再行動。",
    caveat="區間用於風險管理,不是保證;每個 SKU 用同一測試窗比較 Prophet 與 Baseline,誰準用誰",
)
footer()

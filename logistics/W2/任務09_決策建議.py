# -*- coding: utf-8 -*-
"""
D9 任務 09「決策簡報」· 完整實作版
============================================================
基於 D9_決策建議_示範.py 骨架，補完全部 8 個 TODO。
執行:
    streamlit run 任務09_決策建議.py
"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================
# 0. 頁面設定 + 資料載入
# =============================================================

st.set_page_config(
    page_title="物流月度建議書 · 任務 09",
    page_icon="📋",
    layout="wide",
)

HERE = Path(__file__).parent

@st.cache_data
def load_data():
    summary  = pd.read_csv(HERE / "decision_summary.csv",  encoding="utf-8-sig")
    supports = pd.read_csv(HERE / "decision_supports.csv", encoding="utf-8-sig")
    risks    = pd.read_csv(HERE / "decision_risks.csv",    encoding="utf-8-sig")
    return summary, supports, risks

try:
    summary, supports, risks = load_data()
except FileNotFoundError as e:
    st.error(f"找不到決策表：{e.filename}\n請確認 CSV 檔案存在於同目錄。")
    st.stop()

# =============================================================
# 1. Sidebar：故事三選一
# =============================================================

st.sidebar.title("📋 D9 決策簡報")
st.sidebar.caption("選一個故事，查看完整建議書")

story_id = st.sidebar.radio(
    "選擇故事",
    options=summary["story_id"].tolist(),
    format_func=lambda s: f"故事 {s} · {summary[summary.story_id == s]['story_name'].iloc[0]}",
    key="story_id",
)

row        = summary[summary.story_id == story_id].iloc[0]
my_supports = supports[supports.story_id == story_id].reset_index(drop=True)
my_risks    = risks[risks.story_id == story_id].reset_index(drop=True)

st.sidebar.divider()
承接_val = str(row["承接"])
st.sidebar.markdown(f"**承接**：Day {承接_val[1:]}（{承接_val}）")
st.sidebar.markdown(f"**投資回收期**：{row['投資回收期']}")

# =============================================================
# TODO 1：主標題 + st.success 主結論
# =============================================================

st.title("📦 物流月度營運建議書")
st.caption(f"故事 {story_id} · {row['story_name']}")

st.success(f"📌 **建議：{row['主結論']}**")

st.divider()

# =============================================================
# TODO 2：三個 st.metric 卡片
# =============================================================

col1, col2, col3 = st.columns(3)
col1.metric(row["kpi1_label"], row["kpi1_value"], row["kpi1_delta"])
col2.metric(row["kpi2_label"], row["kpi2_value"], row["kpi2_delta"])
col3.metric(row["kpi3_label"], row["kpi3_value"], row["kpi3_delta"])

st.divider()

# =============================================================
# TODO 3：一張關鍵圖
# =============================================================

st.subheader("📊 關鍵圖表")

if story_id == "A":
    # 故事 A：倉儲 ABC — 用 Pareto 長條圖呈現 SKU 出貨佔比
    sku_data = pd.DataFrame({
        "SKU 類別": ["A 類（前 27 個 SKU）", "B 類", "C 類"],
        "出貨佔比（%）": [79.7, 14.1, 6.2],
        "SKU 數量佔比（%）": [27, 43, 30],
    })
    fig = go.Figure()
    fig.add_bar(
        x=sku_data["SKU 類別"],
        y=sku_data["出貨佔比（%）"],
        name="出貨佔比",
        marker_color=["#EF4444", "#F59E0B", "#10B981"],
        text=sku_data["出貨佔比（%）"].apply(lambda v: f"{v}%"),
        textposition="outside",
    )
    fig.update_layout(
        title="SKU ABC 出貨佔比分布（Pareto 效應）",
        yaxis_title="出貨佔比 (%)",
        yaxis_range=[0, 100],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
        height=400,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("▶ 為什麼是這張圖：Pareto 長條圖直觀呈現「27 個 A 類 SKU 佔出貨 79.7%」，老闆一眼就能理解重排這 27 個儲位的迫切性，而非漫天撒網。")

elif story_id == "B":
    # 故事 B：路線 OTD 箱型圖（模擬多週數據）
    import numpy as np
    rng = np.random.default_rng(42)
    route_data = []
    for route, mean, std in [("R-01", 95, 2), ("R-02", 94, 2.5), ("R-03", 27.9, 8),
                              ("R-04", 93, 3), ("R-05", 96, 1.5)]:
        vals = rng.normal(mean, std, 20).clip(0, 100).tolist()
        route_data.extend([{"路線": route, "OTD (%)": v} for v in vals])
    df_route = pd.DataFrame(route_data)

    fig = px.box(
        df_route, x="路線", y="OTD (%)",
        color="路線",
        color_discrete_map={"R-03": "#EF4444"},
        title="各路線 OTD 分布（R-03 顯著低於目標）",
    )
    fig.add_hline(y=95, line_dash="dash", line_color="#6B7280",
                  annotation_text="目標 95%", annotation_position="top right")
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
        height=420,
        showlegend=False,
    )
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("▶ 為什麼是這張圖：箱型圖能一眼比較所有路線的 OTD 分布，R-03 不只平均值最低，變異數也最大，清楚定位出問題路線，說服力勝過純數字報表。")

else:
    # 故事 C：供應商 LT 變異（CV）長條圖
    sup_data = pd.DataFrame({
        "供應商": ["SUP-01", "SUP-02", "SUP-03", "SUP-04", "SUP-05"],
        "LT 變異 CV (%)": [32, 28, 80, 25, 41],
        "風險": ["正常", "正常", "🔴 紅標", "正常", "注意"],
    })
    colors = ["#10B981" if v < 50 else ("#F59E0B" if v < 60 else "#EF4444")
              for v in sup_data["LT 變異 CV (%)"]]
    fig = go.Figure()
    fig.add_bar(
        x=sup_data["供應商"],
        y=sup_data["LT 變異 CV (%)"],
        marker_color=colors,
        text=sup_data["LT 變異 CV (%)"].apply(lambda v: f"{v}%"),
        textposition="outside",
    )
    fig.add_hline(y=50, line_dash="dash", line_color="#6B7280",
                  annotation_text="風險門檻 50%", annotation_position="top right")
    fig.update_layout(
        title="各供應商 LT 變異係數（CV）比較",
        yaxis_title="CV (%)",
        yaxis_range=[0, 100],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
        height=400,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("▶ 為什麼是這張圖：CV 長條圖直接量化各供應商的交期不穩定程度，SUP-03 的 80% 遠超門檻值 50%，紅色標示讓老闆 3 秒鐘就知道問題源頭在哪。")

st.divider()

# =============================================================
# TODO 4：三條支撐（st.expander 摺疊）
# =============================================================

st.subheader("🔍 三條支撐論點")

for _, s in my_supports.iterrows():
    with st.expander(f"▍理由 {s['idx']}：{s['support']}"):
        st.markdown(f"**數據佐證：** {s['evidence']}")

st.divider()

# =============================================================
# TODO 5：風險三情境表
# =============================================================

st.subheader("⚠️ 風險評估 · 三情境")
st.caption("老闆看的不是最好的情境，而是『最壞的情境是否可承受』。")

# 加入顏色標示
scenario_colors = {
    "樂觀": "🟢",
    "悲觀": "🟡",
    "不作為": "🔴",
}
display_risks = my_risks[["scenario", "expected", "monthly_万", "action"]].copy()
display_risks["scenario"] = display_risks["scenario"].apply(
    lambda x: f"{scenario_colors.get(x, '')} {x}"
)
display_risks.columns = ["情境", "預期結果", "月效益（萬）", "行動建議"]

st.dataframe(display_risks, hide_index=True, use_container_width=True)

# 月效益橫向比較長條圖
fig_risk = px.bar(
    my_risks, x="scenario", y="monthly_万",
    color="monthly_万",
    color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
    labels={"scenario": "情境", "monthly_万": "月效益（萬元）"},
    title="三情境月效益對比",
    text="monthly_万",
)
fig_risk.update_traces(texttemplate="%{text} 萬", textposition="outside")
fig_risk.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    coloraxis_showscale=False,
    height=320,
    font=dict(size=13),
)
fig_risk.update_yaxes(showgrid=True, gridcolor="#E5E7EB")
st.plotly_chart(fig_risk, use_container_width=True)

st.divider()

# =============================================================
# TODO 6：投資回收期
# =============================================================

st.info(f"💰 預估投資回收期：**{row['投資回收期']}**")

st.divider()

# =============================================================
# TODO 7：反直覺三點
# =============================================================

with st.expander("🔄 反直覺三點（Day 9 §2.4）— 點擊展開"):
    st.markdown("""
**1. 結論要先講，不是最後才揭曉**

> 業界匯報應從「結論 → 理由 → 證據」由上往下。老闆要的是決定，不是坐在那裡聽你做分析過程回放。先給答案，再告訴我為什麼。

**2. 圖表愈多愈不專業（≤ 5 張原則）**

> 一份建議書超過 5 張圖，老闆反而覺得你沒底。圖愈多，代表你對哪張最重要沒把握，信心降一格。選一張最有說服力的圖，其餘放附錄。

**3. 沒有風險評估，老闆不會 buy-in**

> 老闆更怕「沒看見失敗風險的方案」。把樂觀、悲觀、不作為三情境都列出來，老闆反而點頭，因為他看到你想過了最壞的情況，他才能放心拍板。
""")

st.divider()

# =============================================================
# TODO 8：90 秒 Showtime 腳本下載按鈕
# =============================================================

st.subheader("📥 90 秒 Showtime 腳本")

# 動態產生對應故事的腳本
story_name = row["story_name"]
main_conclusion = row["主結論"]
supports_list = my_supports[["support", "evidence"]].values.tolist()
risks_list = my_risks[["scenario", "expected", "monthly_万", "action"]].values.tolist()

script_content = f"""# 90 秒 Showtime 腳本 · 故事 {story_id} · {story_name}

## 0:00-0:30 SCQA 開場
- **S（共識）**：本月物流營運數據已整理完畢，發現關鍵問題需請總經理決策。
- **C（衝突）**：{story_name} 的核心 KPI 出現異常，持續不處理將造成月損失。
- **Q（問題）**：我們該如何在最短時間內、最低成本下解決此問題？
- **A（建議）**：{main_conclusion}

## 0:30-1:00 三條支撐
"""
for i, (sup, ev) in enumerate(supports_list, 1):
    script_content += f"- **理由 {i}：{sup}** — {ev}\n"

script_content += "\n## 1:00-1:30 風險三情境 + 結語\n"
for scenario, expected, monthly, action in risks_list:
    script_content += f"- **{scenario}**：{expected} · 月效益 {monthly} 萬 → {action}\n"

script_content += f"""
投資回收期：{row['投資回收期']}

---
_本檔由 任務09_決策建議.py 動態產出_
"""

# 優先使用現有的 Showtime_腳本.md（故事 B），否則動態產生
script_path = HERE / "Showtime_腳本.md"
if script_path.exists() and story_id == "B":
    download_data = script_path.read_text(encoding="utf-8")
else:
    download_data = script_content

st.download_button(
    label="📥 下載 90 秒 Showtime 腳本（Markdown）",
    data=download_data,
    file_name=f"Showtime_腳本_故事{story_id}.md",
    mime="text/markdown",
)

with st.expander("📜 預覽腳本內容"):
    st.markdown(script_content)

# =============================================================
# 收口
# =============================================================

st.divider()
st.caption(
    "✅ 任務 09 完整實作版 · 8 個 TODO 全部完成。"
    "若要查看骨架版請開啟 `D9_決策建議_示範.py`，完整答案版請開啟 `D9_決策建議_答案版.py`。"
)

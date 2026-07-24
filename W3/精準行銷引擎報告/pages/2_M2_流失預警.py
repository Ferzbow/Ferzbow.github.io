# -*- coding: utf-8 -*-
"""M2 · 流失預警

決策樹流失模型 + 門檻拉桿:
  拉動流失機率門檻 → 高風險人數 / Recall / Precision 即時變化 + PR 曲線上的點跟著移動。
  模型與資料管線同一組超參數與隨機種子(在頁內重訓,毫秒級,有快取)。
"""
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve

st.set_page_config(page_title="M2 流失預警", page_icon="🚨", layout="wide")

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.ui import page_header, how_to_read, footer
from lib.recommend import CLUSTER_STRATEGY

page_header(
    "M2", "找出誰要走",
    "🚨 流失預警",
    "決策樹模型為 1,500 位客戶打流失機率;拉動門檻看覆蓋與準度的取捨,再依風險指數排出本週聯繫優先序。",
    "決策樹流失模型 × 1,500 位客戶主檔 · 風險指數含業務加權",
)

DATA = Path(__file__).parent.parent / "data"
RANDOM_STATE = 42
FEATURES = ["Recency", "Frequency", "Monetary", "AvgOrder", "ComplaintCnt", "Tenure"]


# ============================================================
# 頁內重訓決策樹(與資料管線同超參數/隨機種子,快取後只跑一次)
# ============================================================
@st.cache_data
def load_scored():
    churn = pd.read_csv(DATA / "customer_churn.csv", encoding="utf-8-sig")
    X, y = churn[FEATURES], churn["Churn"]
    X_tr, _, y_tr, _ = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_STATE, stratify=y
    )
    clf = DecisionTreeClassifier(
        max_depth=4, min_samples_split=20, min_samples_leaf=20,
        class_weight="balanced", random_state=RANDOM_STATE,
    ).fit(X_tr, y_tr)
    churn["churn_prob"] = clf.predict_proba(X)[:, 1]
    return churn


try:
    df_scored = load_scored()
    df_top10 = pd.read_csv(DATA / "churn_top10.csv", encoding="utf-8-sig")
except FileNotFoundError as e:
    st.error(f"找不到資料檔: {e},請先跑 prepare_data.py")
    st.stop()

y_true = df_scored["Churn"].values
y_prob = df_scored["churn_prob"].values
churn_rate = y_true.mean()

# ============================================================
# 門檻拉桿 → 高風險人數 / Recall / Precision 即時重算
# ============================================================
st.subheader("🎚 流失機率門檻:覆蓋與準度的取捨")

threshold = st.slider(
    "流失機率門檻(機率 ≥ 門檻 → 列為高風險)",
    0.05, 0.95, 0.50, 0.05,
    help="門檻調低:抓到更多真流失(Recall ↑)但誤報變多(Precision ↓);門檻調高則相反",
)

pred = (y_prob >= threshold).astype(int)
tp = int(((pred == 1) & (y_true == 1)).sum())
fp = int(((pred == 1) & (y_true == 0)).sum())
fn = int(((pred == 0) & (y_true == 1)).sum())
n_flag = int(pred.sum())
recall = tp / (tp + fn) if (tp + fn) else 0.0
precision = tp / (tp + fp) if (tp + fp) else 0.0

k1, k2, k3 = st.columns(3)
k1.metric("高風險人數", f"{n_flag} 人",
          delta=f"占全體 {n_flag/len(df_scored):.1%}", delta_color="off",
          help="流失機率 ≥ 門檻的客戶數 = 需要行銷/客服介入的名單規模")
k2.metric("Recall(召回率)", f"{recall:.0%}",
          delta=f"漏掉 {fn} 位真流失", delta_color="inverse",
          help="真正會流失的客戶中,被模型抓到的比例")
k3.metric("Precision(精確率)", f"{precision:.0%}",
          delta=f"誤報 {fp} 位", delta_color="inverse",
          help="被列為高風險的客戶中,真的會流失的比例")

# ============================================================
# PR 曲線(點隨門檻移動)
# ============================================================
prec_curve, rec_curve, thr_curve = precision_recall_curve(y_true, y_prob)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=rec_curve, y=prec_curve,
    mode="lines", name="PR 曲線",
    line=dict(color="#3498DB", width=3),
    hovertemplate="Recall %{x:.0%}<br>Precision %{y:.0%}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=[recall], y=[precision],
    mode="markers+text", name=f"目前門檻 {threshold:.2f}",
    marker=dict(color="#E74C3C", size=16, symbol="circle",
                line=dict(color="white", width=2)),
    text=[f"門檻 {threshold:.2f}"], textposition="top center",
    hovertemplate=f"門檻 {threshold:.2f}<br>Recall {recall:.0%}<br>Precision {precision:.0%}<extra></extra>",
))
fig.add_hline(y=churn_rate, line_dash="dot", line_color="#95A5A6",
              annotation_text=f"隨機亂猜基準(歷史流失率 {churn_rate:.1%})",
              annotation_position="bottom right")
fig.update_layout(
    height=420,
    xaxis=dict(title="Recall(召回率)", tickformat=".0%", range=[0, 1.02]),
    yaxis=dict(title="Precision(精確率)", tickformat=".0%", range=[0, 1.02]),
    hovermode="closest",
    margin=dict(l=0, r=10, t=30, b=0),
)
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "📌 曲線越往右上越好;紅點 = 目前門檻的位置,拉動上方拉桿會沿曲線移動。"
    "灰虛線是隨機亂猜的基準 ── 模型要明顯高於它才有價值。"
    "(指標以全體 1,500 位客戶計算,含 70% 訓練資料)"
)

st.divider()

# ============================================================
# 主結論 + Top 10 名單(含分群)
# ============================================================
n_top = len(df_top10)
avg_prob = df_top10["churn_prob"].mean() * 100 if "churn_prob" in df_top10.columns else 0
top_comp = "、".join(f"{k} {v} 位" for k, v in df_top10["cluster_name"].value_counts().items()) \
           if "cluster_name" in df_top10.columns else ""

st.error(
    f"⚠️ **本月模型預警 Top {n_top} 高風險客戶({top_comp})** · "
    f"平均流失機率 **{avg_prob:.0f}%** · "
    f"建議由客服納入「熱銷喚醒推送」本週優先發送"
)

st.subheader(f"Top {n_top} 優先聯繫名單")

# 加 Rank + 風險指數(combined score 才能看出 ranking 差異)
df_show = df_top10.copy().reset_index(drop=True)

# 風險指數 = 模型機率 70% + Recency 久沒下單 20% + 投訴次數 10%
recency_norm = (df_show["Recency"].clip(0, 365) / 365)
complaint_norm = df_show["ComplaintCnt"].clip(0, 5) / 5
df_show["risk_index"] = (
    df_show["churn_prob"] * 70
    + recency_norm * 20
    + complaint_norm * 10
).round().astype(int)

df_show = df_show.sort_values("risk_index", ascending=False).reset_index(drop=True)
df_show.insert(0, "Rank", range(1, len(df_show) + 1))

# 建議動作與 M4 推薦引擎的分群策略一致(依所屬分群帶出)
if "cluster_name" in df_show.columns:
    df_show["suggested_action"] = df_show["cluster_name"].map(
        lambda c: CLUSTER_STRATEGY.get(c, {}).get("action", "客戶經理評估")
    )

show_cols = ["Rank", "customer_id", "cluster_name", "risk_index", "churn_prob", "Recency",
             "Frequency", "Monetary", "ComplaintCnt", "main_reason", "suggested_action"]
show_cols = [c for c in show_cols if c in df_show.columns]

column_config = {
    "Rank": st.column_config.NumberColumn(
        "優先順序",
        help="本週優先處理順序(基於風險指數降序)",
        format="%d",
        width="small",
    ),
    "cluster_name": st.column_config.TextColumn(
        "分群",
        help="K-means 客群(M1);挽留話術依群差異化,見 M4 策略速查",
        width="small",
    ),
    "risk_index": st.column_config.ProgressColumn(
        "風險指數",
        help="模型機率 70% + Recency 20% + 投訴次數 10%(0-100)",
        format="%d",
        min_value=0,
        max_value=100,
    ),
    "churn_prob": st.column_config.NumberColumn(
        "模型機率",
        help="決策樹原始預測機率",
        format="%.3f",
    ),
    "Recency": st.column_config.NumberColumn("最近消費(R)", format="%d 天"),
    "Frequency": st.column_config.NumberColumn("消費頻率(F)", format="%d"),
    "Monetary": st.column_config.NumberColumn("消費金額(M)", format="%d"),
    "ComplaintCnt": st.column_config.NumberColumn("投訴", format="%d"),
    "main_reason": st.column_config.TextColumn("主因", width="medium"),
    "suggested_action": st.column_config.TextColumn(
        "建議動作", width="medium",
        help="依所屬分群帶出,與 M4 推薦引擎的分群策略一致",
    ),
}
st.dataframe(df_show[show_cols], use_container_width=True,
             column_config=column_config, hide_index=True)

st.caption("📌 **風險指數**是業務調整版分數(0-100):模型機率 + Recency + 投訴加權,"
           "讓同機率的客戶也排得出先後 ── ML 機率 + 業務規則 = 真實上線決策依據。")

st.divider()

# ============================================================
# 高風險客戶流失主因分布(門檻連動,主因規則與資料管線一致)
# ============================================================
st.subheader(f"高風險客戶流失主因分布(門檻 {threshold:.2f} 以上,共 {n_flag} 人)")

ACTION_MAP = {
    "長時間沒下單 + 頻次低": "推送優惠通知",
    "投訴次數高": "客服主動聯繫 + 補救方案",
    "近期下單變稀": "VIP 電話挽留 + 折扣券",
    "綜合風險訊號": "客戶經理評估",
}


def main_reason(row):
    """與資料管線同一套主因規則(決策路徑白話版)"""
    if row["Recency"] > 60 and row["Frequency"] <= 2:
        return "長時間沒下單 + 頻次低"
    if row["ComplaintCnt"] >= 2:
        return "投訴次數高"
    if row["Recency"] > 30:
        return "近期下單變稀"
    return "綜合風險訊號"


flagged = df_scored[df_scored["churn_prob"] >= threshold]
if len(flagged):
    reason_df = flagged.apply(main_reason, axis=1).value_counts().rename_axis("主因").reset_index(name="人數")
    reason_df["占比"] = reason_df["人數"] / len(flagged)
    reason_df["標籤"] = reason_df.apply(lambda r: f"{r['人數']} 人({r['占比']:.0%})", axis=1)
    reason_df["建議動作"] = reason_df["主因"].map(ACTION_MAP)

    fig_r = px.bar(
        reason_df.sort_values("人數"),
        x="人數", y="主因", orientation="h",
        color="主因", text="標籤",
        hover_data={"建議動作": True, "主因": False, "標籤": False},
        height=max(220, 70 * len(reason_df) + 60),
        color_discrete_sequence=["#E74C3C", "#F39C12", "#3498DB", "#95A5A6"],
    )
    fig_r.update_traces(textposition="outside")
    fig_r.update_layout(
        xaxis_title="人數", yaxis_title=None, showlegend=False,
        margin=dict(l=0, r=10, t=10, b=0),
        xaxis=dict(range=[0, reason_df["人數"].max() * 1.25]),
    )
    st.plotly_chart(fig_r, use_container_width=True)

    # 主因 → 動作對照(給客服/客戶經理的話術入口)
    for _, r in reason_df.iterrows():
        st.markdown(f"- **{r['主因']}**({r['人數']} 人,{r['占比']:.0%})→ 建議動作:{r['建議動作']}")
    st.caption(f"📌 分布隨上方門檻連動;Top {n_top} 名單全數屬「長時間沒下單 + 頻次低」,故以門檻以上全體呈現,主管才看得到次要主因的量。")
else:
    st.warning("目前門檻以上沒有客戶,請調低門檻")

# ============================================================
# 一鍵下載 + 寄送(模擬)
# ============================================================
st.divider()
col1, col2 = st.columns(2)

col1.download_button(
    "📥 下載 Top 10 名單(CSV,給客服喚醒推送)",
    df_show[show_cols].to_csv(index=False).encode("utf-8-sig"),
    "churn_top10.csv",
    "text/csv",
)

if col2.button("📧 模擬寄送名單給客服"):
    st.success("(模擬)已寄送至 sales@company.com 與 csm@company.com")

# ============================================================
# 模型可解釋性
# ============================================================
with st.expander("🔍 模型如何判斷高風險?(可解釋性說明)"):
    st.markdown("""
    決策樹模型學了這類規則(範例):

    ```
    Recency > 60 天?
      ├─ Yes → Frequency < 3?
      │         ├─ Yes → 流失機率 92%
      │         └─ No  → 流失機率 65%
      └─ No  → 投訴 > 0 次?
                ├─ Yes → 流失機率 35%
                └─ No  → 流失機率 5%
    ```

    每個 Top 10 客戶的「主因」欄就是落到哪條決策路徑。
    """)

# ============================================================
# 主管判讀 + 頁尾
# ============================================================
how_to_read(
    "門檻是**覆蓋與準度的取捨**:挽留預算多就調低門檻多抓人,預算緊就調高門檻只抓最準的;"
    "風險指數用來**排序聯繫優先序**,不是判決,先由客服覆核 Top 10;"
    "挽留話術搭配 M4 該客戶的「回購喚回」推薦。",
    caveat="固定同一個模型只調門檻比較覆蓋,不重訓;聯繫後的實際回饋要記錄回來,下月校正模型",
)
footer()

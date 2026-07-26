# -*- coding: utf-8 -*-
"""M4 · 推薦引擎 ★ 核心展示

D13 Apriori × D14 K-means 真整合:
  輸入客戶 ID → 購買史長條圖 → 分群差異化推薦(帶理由) → 3 款推銷文案給銷售部門
"""
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="M4 推薦引擎", page_icon="🎯", layout="wide")

# 載入 lib/recommend
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.recommend import recommend, sales_copy, CLUSTER_STRATEGY, MIN_LIFT
from lib.ui import page_header, how_to_read, footer

page_header(
    "M4 ★", "給對的人推對的品",
    "🎯 推薦引擎(核心展示)",
    "輸入客戶 ID → 匹配他的購買史與所屬客群 → 個人化推薦(已購排除)+ 3 款推銷文案給銷售部門。",
    f"客戶主檔 × 交易明細 × 購物籃關聯規則(採用門檻 Lift ≥ {MIN_LIFT})",
)

DATA = Path(__file__).parent.parent / "data"

try:
    df_customers = pd.read_csv(DATA / "customer_clustered.csv", encoding="utf-8-sig")
    rules = pd.read_csv(DATA / "apriori_top5_rules.csv", encoding="utf-8-sig")
except FileNotFoundError as e:
    st.error(f"找不到資料檔: {e}")
    st.stop()

# 交易明細(prepare_data.py 已把 D13 的籃子接上主檔的 customer_id)
try:
    df_tx = pd.read_csv(DATA / "transactions.csv", encoding="utf-8-sig")
except FileNotFoundError:
    df_tx = None

# 商品目錄(找新品 SKU_NEW 用)
try:
    df_sku = pd.read_csv(DATA / "sku_catalog.csv", encoding="utf-8-sig")
except FileNotFoundError:
    df_sku = None

# ============================================================
# 客戶 ID 輸入(橫排置頂,下方內容全寬展開)
# ============================================================
def pick_representatives(df_customers, df_tx):
    """每個分群固定挑 1 位代表:Frequency > 0,且優先挑「交易明細筆數最多」者(demo 看得到購買史)"""
    tx_counts = df_tx["customer_id"].value_counts() if df_tx is not None else pd.Series(dtype=int)
    reps = {}
    for cname in ["VIP 高頻高額", "穩定中段", "流失高風險", "沉睡客戶"]:
        pool = df_customers[
            (df_customers["cluster_name"] == cname) & (df_customers["Frequency"] > 0)
        ].copy()
        if len(pool) == 0:
            continue
        pool["tx_n"] = pool["customer_id"].map(tx_counts).fillna(0)
        # 明細筆數最多者當代表;同筆數時取 customer_id 排序最前(固定、不隨機)
        rep = pool.sort_values(["tx_n", "customer_id"], ascending=[False, True]).iloc[0]
        reps[f"{cname} 代表({rep['customer_id']})"] = rep["customer_id"]
    return reps


sample_ids = pick_representatives(df_customers, df_tx)

# 分群策略速查表(給銷售部門)
st.markdown("##### 📋 四群推薦策略速查")
df_strategy = pd.DataFrame([
    {"分群": k, "推薦邏輯": v["logic"].split(":")[0], "文案調性": v["tone"], "建議動作": v["action"]}
    for k, v in CLUSTER_STRATEGY.items()
])
st.dataframe(df_strategy, use_container_width=True, hide_index=True)

in1, in2, in3 = st.columns([2, 2, 1])
with in1:
    preset = st.selectbox("快速選擇範例(四群代表)", list(sample_ids.keys()))
    default_id = sample_ids[preset]
with in2:
    cid = st.text_input("或自行輸入 customer_id", value=default_id)
with in3:
    top_n = st.slider("推薦商品數", 1, 5, 3)

st.divider()

if cid in df_customers["customer_id"].values:
    result = recommend(cid, df_customers, rules,
                       df_tx=df_tx, df_sku=df_sku, top_n=top_n)

    st.subheader(f"客戶 {cid} · {result['cluster']}")

    # 本群策略 / 建議動作(兩欄對齊)
    c_row = df_customers[df_customers["customer_id"] == cid].iloc[0]
    if result["strategy"]:
        stra_l, stra_r = st.columns(2)
        stra_l.info(f"🧭 **本群策略**\n\n{result['strategy']['logic']}")
        stra_r.info(f"🎬 **建議動作**\n\n{result['strategy']['action']}")

    # RFM 指標(中文名稱 + 英文縮寫)
    info_cols = st.columns(4)
    info_cols[0].metric("最近消費(R)", f"{c_row['Recency']} 天")
    info_cols[1].metric("消費頻率(F)", f"{c_row['Frequency']} 次")
    info_cols[2].metric("消費金額(M)", f"{c_row['Monetary']:,.0f} 元")
    if "ComplaintCnt" in c_row:
        info_cols[3].metric("投訴次數", c_row["ComplaintCnt"])

    # ============================================================
    # 過往購買長條圖(購買次數前 10 名 + 其餘彙總)
    # ============================================================
    bought_counts = result["bought_counts"]
    if len(bought_counts):
        n_orders = df_tx[df_tx["customer_id"] == cid]["order_id"].nunique()
        st.markdown(f"##### 🧾 過往購買紀錄({n_orders} 張訂單 / {int(bought_counts.sum())} 個品項)")

        top10 = bought_counts.head(10)
        rest = bought_counts.iloc[10:]
        df_bought = top10.rename_axis("品項").reset_index(name="購買次數")
        fig = px.bar(
            df_bought.sort_values("購買次數"),
            x="購買次數", y="品項", orientation="h", text="購買次數",
            height=max(240, 36 * len(df_bought) + 60),
        )
        fig.update_traces(textposition="outside", marker_color="#4C78A8")
        fig.update_layout(
            margin=dict(l=0, r=10, t=10, b=0),
            xaxis_title=None, yaxis_title=None, showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        rest_note = (f"僅顯示購買次數前 10 名;其餘 {len(rest)} 個品項共 {int(rest.sum())} 次。"
                     if len(rest) else "")
        st.caption(f"💰 {rest_note}品項金額需交易單價資料,以「購買次數」呈現;客戶總消費額見上方 消費金額(M)")
    else:
        freq = int(c_row["Frequency"])
        if freq > 0:
            st.warning(
                f"🧾 主檔 RFM 顯示消費頻率(F)= {freq},但交易明細查無此客戶的品項紀錄"
                f"(明細僅涵蓋部分近期訂單)→ 推薦改走備援邏輯(見下方各品項的推薦來源)"
            )
        else:
            st.warning("🧾 此客戶無任何購買紀錄(沉睡/流失客常見)→ 推薦改走備援邏輯(見下方各品項的推薦來源)")

    st.divider()

    # ============================================================
    # Top N 推薦商品(帶推薦來源與理由,品名完整顯示)
    # ============================================================
    st.subheader(f"🎁 推薦 Top {top_n}")

    SOURCE_ICON = {"關聯規則": "🔗", "熱銷推薦": "🔥", "回購喚回": "🔁", "新品試探": "🆕"}
    for i, r in enumerate(result["recommendations"], 1):
        badge_col, info_col = st.columns([1, 4])
        with badge_col:
            st.markdown(
                f"<div style='line-height:1.3'><span style='font-size:0.85rem;opacity:0.7'>Top {i}</span><br>"
                f"<span style='font-size:1.5rem;font-weight:700'>{r['sku']}</span></div>",
                unsafe_allow_html=True,
            )
        icon = SOURCE_ICON.get(r["source"], "🎁")
        if r["lift"] is not None:
            info_col.markdown(
                f"{icon} **{r['source']}** · Lift **{r['lift']:.2f}** · "
                f"Confidence {r['confidence']:.0%} · 規則:{r['from_rule']}"
            )
        else:
            info_col.markdown(f"{icon} **{r['source']}** · 來源:{r['from_rule']}")
        info_col.caption(r["reason"])

    st.caption(f"💡 {result['explain']}")

    # ============================================================
    # 3 款推銷文案(並列顯示,銷售部門直接複製 / 下載)
    # ============================================================
    st.divider()
    st.subheader("📱 推銷文案 × 3(銷售部門可直接複製)")

    skus = [r["sku"] for r in result["recommendations"]]
    copies = sales_copy(result["cluster"], skus)

    copy_cols = st.columns(3)
    for col, (i, c) in zip(copy_cols, enumerate(copies, 1)):
        with col:
            st.markdown(f"**文案 {i} · {c['angle']}**")
            st.code(c["text"], language=None, wrap_lines=True)
    st.caption("📌 三款各走不同切入角度,銷售可依客戶關係熱度挑選;真實上線可串 GenAI 依此為底自動變體")

    # 一鍵下載:推薦 + 理由 + 3 款文案(給銷售部門)
    rec_lines = "\n".join(
        f"  Top {i}. {r['sku']}({r['source']})── {r['reason']}"
        for i, r in enumerate(result["recommendations"], 1)
    )
    copy_lines = "\n".join(f"  文案 {i}({c['angle']}):{c['text']}" for i, c in enumerate(copies, 1))
    sales_txt = f"""【M4 推薦引擎 · 銷售參考單】
客戶:{cid}(所屬群:{result['cluster']})
本群策略:{result['strategy'].get('logic', '')}
建議動作:{result['strategy'].get('action', '')}

推薦品項:
{rec_lines}

推銷文案(三款切入角度):
{copy_lines}

── W3 第 6 組 · BOSS III 精準行銷引擎
"""
    st.download_button(
        "📥 下載本客戶銷售參考單(txt,給銷售部門)",
        sales_txt.encode("utf-8-sig"),
        f"銷售參考單_{cid}.txt",
        "text/plain",
    )

    # ============================================================
    # GenAI prompt 預覽(加分項展示用)
    # ============================================================
    with st.expander("🤖 給 GenAI 寫文案的 prompt(可複製)"):
        skus_str = "、".join(skus)
        prompt = f"""你是 Line OA 行銷文案寫手。客戶屬「{result['cluster']}」群。

推薦商品:{skus_str}
推薦理由:{[r['reason'] for r in result['recommendations']]}
本群策略:{result['strategy'].get('logic', '')}
文案調性:{result['strategy'].get('tone', '')}

文案要求:
- 80 字以內
- 第一句鉤子(根據群名:VIP=尊榮、沉睡=喚醒、流失=挽留、穩定=新品)
- 最後一句行動(出示券碼/點選連結/限期)
- 結尾加 #物流好夥伴

請輸出 3 段不同切入角度的文案。
"""
        st.code(prompt, language=None)

else:
    st.error(f"找不到客戶 {cid}")

# ============================================================
# 全 Apriori 規則表(底部 expand)
# ============================================================
with st.expander("📜 全 Apriori 規則庫(D13 輸出)"):
    st.dataframe(rules, use_container_width=True)
    st.caption(f"規則採用門檻:Lift ≥ {MIN_LIFT}(Lift > 1 代表正相關,1.3 以上才有行銷強度)")

# ============================================================
# 推薦邏輯說明(方法差異 ── 本組差異化主打)
# ============================================================
st.divider()
st.subheader("🧠 推薦邏輯:個人化在哪?")

diff_l, diff_r = st.columns(2)
with diff_l:
    st.markdown("""
    **常見做法:全域固定推薦**
    - 所有客戶拿到同一份 Lift Top 3
    - 可能推薦客戶**已經買過**的商品
    - 客群只影響文案,不影響推薦內容
    """)
with diff_r:
    st.markdown(f"""
    **本組做法:個人化重排 + 已購排除**
    - 用**他買過的品項**匹配規則 antecedent(Lift ≥ {MIN_LIFT})
    - **排除已購商品**,推「還沒買過」的關聯品
    - 四群走**不同推薦邏輯**(關聯/新品/回購/熱銷),規則不足自動備援
    - 每個推薦附**白話理由**,銷售一看就能開口
    """)

st.caption("驗證方式:切換上方四群代表,推薦內容與理由隨客戶不同 ── 不是所有人同一份名單")

# ============================================================
# 主管判讀 + 頁尾
# ============================================================
how_to_read(
    "推薦品項用來**設計行銷測試**,不是保證買單:先小量發送、看轉換率,再放大;"
    "文案三款依客戶關係熱度挑選(熱→套組加值、冷→低門檻折扣)。",
    caveat="關聯規則反映共現,不等於因果;個人化推薦以交易明細涵蓋範圍為準",
)
footer()

# -*- coding: utf-8 -*-
"""
prepare_data.py
================
把 D11-D14 的產出「**串接成一份可整合的主檔**」,輸出到 data/。

★ 為什麼不是單純拷貝(2026-07-14 改寫)
--------------------------------------------------
D11~D14 每一天各自練一種方法,**各自用自己的練習資料集**:
  - D11 customer_churn.csv   1,000 位客戶(gen_customer_churn.py 合成)
  - D14 customer_rfm.csv     1,500 位客戶(gen_customer_rfm.py 合成)
  - D12 sales_monthly.csv    10 支 SKU 的月銷量,**只有品號**(SKU_001~SKU_010)
  - D13 transactions.csv     30 品的交易明細,有品號 + 品名,但**沒有客戶**

這幾份**彼此不可 join**:同一個 customer_id(如 C0479)在 D11 和 D14 裡是兩個不同的
合成客戶,只是編號撞名;D13 的交易也接不到任何客戶。
(品號:D13 的 sku_id 與 D12 共用同一套代號,品號字典見 D13 的 sku_catalog.csv)

D15 是**整合日**:5 個模組要講同一個故事(M2 的高風險客 = M1 的沉睡客 = M4 要推薦的人),
所以本腳本把四天的產出**對齊到同一份客戶主檔與同一套商品字典**:

  ① 客戶主檔  = D14 customer_clustered.csv(1,500 人,含 K-means 群)── 唯一主檔
  ② 流失預測  = 把 D11 的「流失機率模型 + 決策樹」**重新套在主檔的 1,500 人上**
                → churn_top10 的人一定是主檔裡真正的沉睡 / 高風險客
                (D11 那份 1,000 人的練習資料不動,只借它的「方法」)
  ③ 交易明細  = D13 transactions.csv **加上 customer_id**(依主檔 Frequency 加權指派)
                → 客戶 ↔ 交易可 join;Apriori 是 order × 品名 層級,規則 / lift 完全不變
  ④ 銷量預測  = D12 的數值**完全不動**,用 D13 的品號字典(sku_catalog.csv)補上品名
                → 品號是兩邊共用的鍵:M3 預測 SKU_001,查字典知道是「尿布」,
                  M4 就接著推「買尿布的人也買啤酒」

跑法:
  python prepare_data.py

來源與輸出都是**與本檔同目錄的 data/**(D11~D14 的產出請先放進 data/),
本腳本就地(in-place)把它們對齊,重複執行結果不變。

輸出(data/):
  customers.csv / customer_clustered.csv / customer_rfm.csv / customer_churn.csv /
  churn_top10.csv / transactions.csv / sku_catalog.csv / apriori_top5_rules.csv /
  sales_monthly.csv / sales_top5_forecast.csv / _LINEAGE.md
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

# Windows 主控台預設 cp950,印不出 ↔ / ★ 這些字元
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).parent
DATA = BASE / "data"                   # 與 prepare_data.py 同目錄;既是來源也是輸出
SRC = DATA                             # D11~D14 的產出直接放在 data/ 底下
DATA.mkdir(exist_ok=True)

RANDOM_STATE = 42

# 商品字典不寫死在這裡 —— 品號 ↔ 品名的對照由 D13 的 sku_catalog.csv 提供
# (D12 只有品號、D13 兩者都有,品號就是跨日串接的鍵)


def read(fname: str, day: str) -> pd.DataFrame:
    p = SRC / fname
    if not p.exists():
        raise SystemExit(
            f"[MISSING] 找不到 {p}\n"
            f"          {fname} 是 {day} 的產出,請跑完 {day} 後把它複製到 data/"
        )
    return pd.read_csv(p, encoding="utf-8-sig")


def save(df: pd.DataFrame, fname: str, note: str) -> None:
    df.to_csv(DATA / fname, index=False, encoding="utf-8-sig")
    print(f"[OK] data/{fname:<28} {len(df):>5} 列 × {len(df.columns)} 欄   {note}")


# ==================================================================
# ① 客戶主檔(唯一真實來源)= D14 K-means 分群結果
# ==================================================================
print("\n① 客戶主檔 ← D14 customer_clustered.csv")
customers = read("customer_clustered.csv", "D14 分群大師")
save(customers, "customer_clustered.csv", "★ 唯一客戶主檔(1,500 人)")
save(customers, "customers.csv", "同上,整合日的正式主檔名")
save(read("customer_rfm.csv", "D14 分群大師"), "customer_rfm.csv", "D14 分群前的 RFM")


# ==================================================================
# ② 流失預測:D11 的「方法」重新套在主檔上
# ==================================================================
print("\n② 流失預測 ← 把 D11 的模型套回主檔的 1,500 人")

# (a) 流失標籤:沿用 D11 gen_customer_churn.py 的 logistic 映射
#     R 大 / F 小 / M 小 / 投訴多 → 流失機率高
rng = np.random.default_rng(RANDOM_STATE)
c = customers
z = lambda s: (s - s.mean()) / s.std()
score = (
    1.5 * z(c["Recency"])
    - 1.2 * z(c["Frequency"])
    - 1.0 * z(np.log1p(c["Monetary"]))
    + 0.8 * z(c["ComplaintCnt"])
)

# bias 校準到整體流失率 ~10%(與 D11 的設計一致;主檔的 R 分布較長尾,
# 直接沿用 D11 的 -2.5 會做出 24% 的流失率,故改為解出對應的 bias)
TARGET_CHURN_RATE = 0.10
lo, hi = -10.0, 5.0
for _ in range(60):
    bias = (lo + hi) / 2
    if (1 / (1 + np.exp(-(score + bias)))).mean() > TARGET_CHURN_RATE:
        hi = bias
    else:
        lo = bias
true_prob = 1 / (1 + np.exp(-(score + bias)))
print(f"     bias={bias:.3f} → 平均流失機率 {true_prob.mean():.1%}")
churn_df = customers.copy()
churn_df["Churn"] = rng.binomial(1, true_prob)
save(churn_df, "customer_churn.csv", f"主檔 + Churn 標籤(流失率 {churn_df.Churn.mean():.1%})")

# (b) 決策樹:與 D11 答案版同一組超參數
FEATURES = ["Recency", "Frequency", "Monetary", "AvgOrder", "ComplaintCnt", "Tenure"]
X, y, ids = churn_df[FEATURES], churn_df["Churn"], churn_df["customer_id"]
X_tr, _, y_tr, _ = train_test_split(
    X, y, test_size=0.30, random_state=RANDOM_STATE, stratify=y
)
clf = DecisionTreeClassifier(
    max_depth=4, min_samples_split=20, min_samples_leaf=20,
    class_weight="balanced", random_state=RANDOM_STATE,
).fit(X_tr, y_tr)

# (c) Top 10 高風險名單(排序與 main_reason 規則沿用 D11 答案版)
top = pd.DataFrame({"customer_id": ids.values,
                    "churn_prob": clf.predict_proba(X)[:, 1]})
top = top.merge(
    churn_df[["customer_id", "Recency", "Frequency", "Monetary",
              "ComplaintCnt", "Segment_D4", "cluster_name"]],
    on="customer_id",
).sort_values(["churn_prob", "Recency", "ComplaintCnt"],
              ascending=[False, False, False]).head(10).reset_index(drop=True)


def reason(row):
    if row["Recency"] > 60 and row["Frequency"] <= 2:
        return "長時間沒下單 + 頻次低"
    if row["ComplaintCnt"] >= 2:
        return "投訴次數高"
    if row["Recency"] > 30:
        return "近期下單變稀"
    return "綜合風險訊號"


top["main_reason"] = top.apply(reason, axis=1)
top["suggested_action"] = top["main_reason"].map({
    "長時間沒下單 + 頻次低": "VIP 電話挽留 + 折扣券",
    "投訴次數高": "客服主動聯繫 + 補救方案",
    "近期下單變稀": "推送優惠通知",
    "綜合風險訊號": "客戶經理評估",
})
save(top, "churn_top10.csv", "★ 名單中的人都在主檔裡,群別一致")


# ==================================================================
# ③ 交易明細:D13 的籃子 + 主檔的 customer_id
# ==================================================================
print("\n③ 交易明細 ← D13 transactions.csv + 主檔 customer_id")
tx = read("transactions.csv", "D13 促銷策劃師")
catalog = read("sku_catalog.csv", "D13 促銷策劃師")       # 品號 ↔ 品名
if "sku_name" not in tx.columns:
    raise SystemExit("[ERROR] data/transactions.csv 缺 sku_name(品名)欄 —— "
                     "請重跑 D13 的 gen_transactions.py 並更新 data/transactions.csv")
# 重跑本腳本時 data/transactions.csv 已帶上一輪指派的 customer_id,先丟掉重新指派
tx = tx.drop(columns=["customer_id"], errors="ignore")
orders = tx["order_id"].drop_duplicates().sort_values().reset_index(drop=True)

# 每張訂單指派一位客戶:買越頻繁(Frequency 高)的人越可能下單
w = customers["Frequency"].to_numpy(dtype=float) + 0.5   # +0.5 讓沉睡客也有機會
w = w / w.sum()
owner = pd.DataFrame({
    "order_id": orders,
    "customer_id": rng.choice(customers["customer_id"].to_numpy(),
                              size=len(orders), p=w),
})
tx = tx.merge(owner, on="order_id")[["order_id", "customer_id", "sku_id", "sku_name"]]
save(tx, "transactions.csv",
     f"★ 客戶 × 交易 × 品號三向可 join({tx.customer_id.nunique()} 位客戶有交易紀錄)")
save(catalog, "sku_catalog.csv", "★ 品號字典(D12 品號 ↔ D13 品名)")

save(read("apriori_top5_rules.csv", "D13 促銷策劃師"), "apriori_top5_rules.csv",
     "D13 原樣(order × sku 層級,規則不受 customer_id 影響)")


# ==================================================================
# ④ 銷量預測:D12 只有品號 → 用 D13 的品號字典補品名(數值不動)
# ==================================================================
print("\n④ 銷量預測 ← D12 原數值 + D13 品號字典(品號 join)")
sales = read("sales_monthly.csv", "D12 銷量預測")
fc = read("sales_top5_forecast.csv", "D12 銷量預測")

name_of = dict(zip(catalog["sku_id"], catalog["sku_name"]))
unmapped = set(sales["sku_id"]) - set(name_of)
if unmapped:
    raise SystemExit(f"[ERROR] D13 的品號字典查不到這些 D12 品號:{sorted(unmapped)}")

# 品號保留(才知道兩邊講的是同一支商品),補上品名給人看
sales["sku_name"] = sales["sku_id"].map(name_of)
if "sku_id" not in fc.columns:             # D12 原檔的品號欄叫 sku
    fc = fc.rename(columns={"sku": "sku_id"})
fc = fc.drop(columns=["sku", "sku_name"], errors="ignore")   # 重跑時先清掉上一輪補的品名
fc["sku_name"] = fc["sku_id"].map(name_of)
fc.insert(1, "sku", fc["sku_name"])        # 沿用舊欄名 sku,M3 頁面不必改
save(sales, "sales_monthly.csv", "品號 + 品名(D12 數值完全不動)")
save(fc, "sales_top5_forecast.csv", "★ Top5 預測品項 = M4 推薦規則裡的品項")


# ==================================================================
# 一致性自我檢查
# ==================================================================
print("\n=== 整合檢查 ===")
rules = pd.read_csv(DATA / "apriori_top5_rules.csv", encoding="utf-8-sig")
rule_items = set(rules["antecedent"]) | set(rules["consequent"])
checks = [
    ("churn_top10 的客戶都在主檔裡",
     set(top.customer_id) <= set(customers.customer_id)),
    ("churn_top10 的群別與主檔一致",
     top.merge(customers, on="customer_id", suffixes=("", "_m"))
        .eval("cluster_name == cluster_name_m").all()),
    ("transactions 的客戶都在主檔裡",
     set(tx.customer_id) <= set(customers.customer_id)),
    ("transactions 的品項都在品號字典裡",
     set(tx.sku_name) <= set(catalog.sku_name)),
    ("D12 的品號都查得到品名(品號 join 成功)",
     bool(sales["sku_name"].notna().all() and fc["sku_name"].notna().all())),
    ("M3 預測的 Top5 品項都出現在 M4 的 Apriori 規則裡",
     set(fc["sku_name"]) <= rule_items),
]
for name, ok in checks:
    print(f"  {'✔' if ok else '✘'} {name}")
if not all(ok for _, ok in checks):
    raise SystemExit("[ERROR] 整合檢查未過,資料不可用")

(DATA / "_LINEAGE.md").write_text(f"""# BOSS III · 資料血緣(由 prepare_data.py 產生,勿手改)

D11~D14 每一天各自用**自己的練習資料集**學一種方法;D15 是整合日,
所有模組必須講同一個故事,所以資料在這裡被對齊成**一份主檔 + 一套商品字典**。

| data/ 檔案 | 來源 | 整合動作 |
|---|---|---|
| `customers.csv` / `customer_clustered.csv` | D14 答案版 | 原樣。**唯一客戶主檔({len(customers):,} 人,含 K-means 群)** |
| `customer_rfm.csv` | D14 gen | 原樣(分群前的 RFM) |
| `customer_churn.csv` | D11 的**方法** + 本主檔 | 用 D11 的流失機率模型在主檔 {len(customers):,} 人上生成 Churn 標籤 |
| `churn_top10.csv` | D11 的**方法** + 本主檔 | 同一棵決策樹(max_depth=4)重訓 → Top10 全部落在主檔的沉睡 / 高風險群 |
| `transactions.csv` | D13 gen | 加上 `customer_id`(依主檔 Frequency 加權指派)→ 客戶 ↔ 交易可 join;`sku_id` 品號 / `sku_name` 品名原樣 |
| `sku_catalog.csv` | D13 gen | **品號字典**(品號 ↔ 品名)── 跨日串接的鍵 |
| `apriori_top5_rules.csv` | D13 答案版 | 原樣(規則是 order × 品名 層級,不受 customer_id 影響) |
| `sales_monthly.csv` / `sales_top5_forecast.csv` | D12 | **數值完全不動**;用品號字典補上 `sku_name`(D12 只有品號沒有品名) |

**注意**:D11 資料夾裡那份 1,000 人的 `customer_churn.csv` / `churn_top10.csv` 是 D11 的
練習資料,**與本主檔的 customer_id 撞名但不是同一批人**,不要拿來混用。

三個 join 鍵:`customer_id`(客戶主檔 ↔ 流失名單 ↔ 交易)、`sku_id` 品號(D12 銷量 ↔ D13 交易)、
`sku_name` 品名(交易 ↔ Apriori 規則)。

品號字典裡 D12 也有月銷量的 {int(catalog['in_d12_sales'].sum())} 支:

{chr(10).join(f"- `{r.sku_id}` → **{r.sku_name}**" + ("  ← M3 Top5 預測" if r.sku_id in set(fc["sku_id"]) else "") for r in catalog[catalog.in_d12_sales].itertuples())}
""", encoding="utf-8")

print("\n✅ 整合完成,全部檢查通過。跑:streamlit run Home.py")
print("   資料血緣說明:data/_LINEAGE.md")

# -*- coding: utf-8 -*-
"""
gen_all.py
==========
從零合成 D15 需要的**所有來源資料**,直接寫進 data/(與本檔同目錄)。

為什麼需要這支
--------------
D15 是整合日,吃的是 D11~D14 四天的產出;但這個 repo 裡只有 D11 / D12 的
gen_*.py,D13(促銷策劃師)與 D14(分群大師)的產生器並不存在。
本腳本把四天的資料**一次合成到 data/**,讓 D15 可以從空資料夾重建:

  python gen_all.py        # ① 合成來源資料 → data/
  python prepare_data.py   # ② 對齊成一份主檔 + 一套商品字典(in-place)
  streamlit run Home.py    # ③ 跑儀表板

產出(data/):
  customer_rfm.csv          D14 官方答案原樣(fixtures/d14/,分群前 RFM)
  customer_clustered.csv    D14 官方答案原樣(fixtures/d14/,K-means 4 群)
  transactions.csv          D13 交易籃子(3,300 張訂單,尚未帶 customer_id)
  sku_catalog.csv           D13 品號字典(30 品,其中 10 品 D12 有月銷量)
  apriori_top5_rules.csv    D13 Apriori Top5 關聯規則
  sales_monthly.csv         D12 月銷量(10 SKU × 36 個月)
  sales_top5_forecast.csv   D12 Prophet 預測(Top5 SKU)

三個故事線的接點(prepare_data.py 的整合檢查會驗)
  - 分群名稱固定為 4 個:VIP 高頻高額 / 穩定中段 / 流失高風險 / 沉睡客戶(M1、M4 頁面寫死)
  - D12 銷量最高的 5 支 SKU,品名必須全部出現在 D13 的 Apriori 規則裡
    → M3 說「下個月尿布要備 1,282 個」,M4 就能接「買尿布的人也買啤酒」
"""
import sys
import warnings

warnings.filterwarnings("ignore")          # Prophet 的 cmdstanpy / plotly 警告太吵

import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from prophet import Prophet
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Windows 主控台預設 cp950,印不出 ★ / → 這些字元
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).parent
DATA = BASE / "data"                       # 與 gen_all.py 同目錄
DATA.mkdir(exist_ok=True)

RANDOM_STATE = 42

# 三段各用自己的亂數流 —— 改了其中一段(例如調整籃子大小)不會連帶動到另外兩段的數值
rng_cust = np.random.default_rng(RANDOM_STATE)          # ① D14 客戶
rng_tx = np.random.default_rng(RANDOM_STATE + 1)        # ② D13 交易
# ③ D12 用舊式 RandomState,與 D12_範例程式/gen_sales_monthly.py 同一組亂數 →
#    產出的月銷量數值與 D12 那天完全一致(學員可以把兩個檔 diff 起來看)
rng_sales = np.random.RandomState(RANDOM_STATE)


def save(df: pd.DataFrame, fname: str, note: str) -> None:
    df.to_csv(DATA / fname, index=False, encoding="utf-8-sig")
    print(f"[OK] data/{fname:<26} {len(df):>5} 列 × {len(df.columns)} 欄   {note}")


# ==================================================================
# ① D14 分群大師:客戶主檔 ← 載入 D14 官方分群答案(fixtures/d14/)
# ==================================================================
# 過去這裡「從零合成一個假 D14」,數值與 D14 當天的答案對不起來(同一個
# customer_id 是兩個不同的人)。改為直接載入 D14 官方答案的兩支 CSV,讓 D15
# 主檔 = D14 的分群成果,血緣「原樣」成真。
#   ⚠️ 種子來源 = D14_範例程式.zip 的官方答案;D14 若更新答案,請同步 fixtures/d14/。
print("\n① D14 客戶主檔 ← 載入 D14 官方分群答案(fixtures/d14/)")
FIX_D14 = BASE / "fixtures" / "d14"
for _f in ("customer_rfm.csv", "customer_clustered.csv"):
    _src = FIX_D14 / _f
    if not _src.exists():
        raise SystemExit(
            f"[MISSING] 找不到 {_src}\n"
            f"          {_f} 是 D14 官方答案種子檔,請確認 fixtures/d14/ 完整"
        )
    shutil.copyfile(_src, DATA / _f)
    _n = len(pd.read_csv(DATA / _f, encoding="utf-8-sig"))
    print(f"[OK] data/{_f:<26} {_n:>5} 列   D14 官方答案原樣")


# ==================================================================
# ② D13 促銷策劃師:品號字典 + 交易籃子 + Apriori
# ==================================================================
print("\n② D13 交易籃子 + Apriori 關聯規則")

# 前 10 支(SKU_001~010)就是 D12 有月銷量的那 10 支 —— 品號是跨日串接的鍵
SKU_NAMES = [
    "尿布", "起司", "啤酒", "紅酒", "塑膠袋", "米", "可樂", "醬油", "礦泉水", "寶特瓶飲料",
    "杯麵", "麵包", "果醬", "雪碧", "牛奶", "豆漿", "蘋果", "香蕉", "橘子", "葡萄",
    "餅乾", "巧克力", "洋芋片", "口香糖", "衛生紙", "牙膏", "洗髮精", "茶包",
    "SKU_NEW_001", "SKU_NEW_002",
]
catalog = pd.DataFrame({
    "sku_id": [f"SKU_{i:03d}" for i in range(1, len(SKU_NAMES) + 1)],
    "sku_name": SKU_NAMES,
    "in_d12_sales": [i < 10 for i in range(len(SKU_NAMES))],   # 前 10 支 D12 有月銷量
})
save(catalog, "sku_catalog.csv", "★ 品號字典(前 10 支 = D12 的 10 支)")

# 埋三組「真關聯」—— 這是 M4 推薦引擎要挖出來的東西
PAIRS = [("尿布", "啤酒", 0.60), ("紅酒", "起司", 0.55), ("醬油", "米", 0.50)]

# 熱門度:前 10 支(D12 那批)是主力商品,買得比長尾多;
# 但三個「後項」(啤酒 / 起司 / 米)要壓低隨機熱門度 —— 不然它們本來就常出現在籃子裡,
# lift = 條件機率 / 基礎機率,分母一大,真關聯就被稀釋成 2 倍左右,看不出「配套」訊號。
CONSEQUENTS = {b for _, b, _ in PAIRS}
pop = np.array([
    0.8 if name in CONSEQUENTS else (3.0 if i < 10 else 1.0)
    for i, name in enumerate(SKU_NAMES)
])
pop = pop / pop.sum()

N_ORDERS = 3300
rows = []
for i in range(N_ORDERS):
    size = int(np.clip(rng_tx.poisson(2.6) + 1, 1, 8))
    picked = rng_tx.choice(SKU_NAMES, size=size, replace=False, p=pop)
    basket = set(picked)
    for a, b, p in PAIRS:                                  # 買了 a,有機率順手拿 b
        if a in basket and rng_tx.random() < p:
            basket.add(b)
    for name in basket:
        # str():rng_tx.choice 給的是 np.str_,mlxtend 的 association_rules 會吃不下
        rows.append({"order_id": f"T{i:05d}", "sku_name": str(name)})

tx = pd.DataFrame(rows)
tx["sku_id"] = tx["sku_name"].map(dict(zip(catalog["sku_name"], catalog["sku_id"])))
tx = tx[["order_id", "sku_id", "sku_name"]].sort_values(["order_id", "sku_id"])
save(tx, "transactions.csv",
     f"D13 原始籃子({tx.order_id.nunique():,} 張訂單,平均 {len(tx)/tx.order_id.nunique():.1f} 品/張)")

# --- Apriori:order × 品名 的 one-hot ---
basket_mat = (tx.assign(v=1)
                .pivot_table(index="order_id", columns="sku_name", values="v",
                             fill_value=0, aggfunc="max")
                .astype(bool))
freq_items = apriori(basket_mat, min_support=0.01, use_colnames=True)
rules = association_rules(freq_items, metric="lift", min_threshold=1.2)

# 只留 1 對 1 的規則(單品 → 單品),課堂上最好講
rules = rules[(rules["antecedents"].apply(len) == 1) &
              (rules["consequents"].apply(len) == 1)].copy()
rules["antecedent"] = rules["antecedents"].apply(lambda s: next(iter(s)))
rules["consequent"] = rules["consequents"].apply(lambda s: next(iter(s)))
rules = rules.sort_values("lift", ascending=False).head(5)
rules["action"] = np.where(rules["lift"] >= 3, "配套販售(套組)", "同區陳列")
rules = rules[["antecedent", "consequent", "support", "confidence", "lift", "action"]]
save(rules, "apriori_top5_rules.csv", "★ Top5 關聯規則(依 lift)")
for r in rules.itertuples():
    print(f"     {r.antecedent} → {r.consequent}   lift={r.lift:.2f}  conf={r.confidence:.0%}")


# ==================================================================
# ③ D12 銷量預測:10 SKU × 36 個月 + Prophet
# ==================================================================
print("\n③ D12 月銷量 + Prophet 預測")

# (沿用 D12 gen_sales_monthly.py 的 pattern 設計:趨勢 / Q4 週期 / 雙11 / 雜訊)
SKU_CONFIG = [
    # sku_id,   base, 年增率, Q4 加成, 雙11 倍數, 雜訊
    ("SKU_001", 1000,  0.15,  0.30,  3.0,  80),   # 尿布:強趨勢 + 高週期
    ("SKU_002",  800,  0.02,  0.08,  1.2,  60),   # 起司:平穩 → Baseline 會贏
    ("SKU_003",  900, -0.08,  0.10,  4.0,  70),   # 啤酒:衰退 + 雙11 單峰
    ("SKU_004",  700,  0.10,  0.20,  2.0,  50),   # 紅酒:中趨勢
    ("SKU_005",  500,  0.05,  0.05,  1.0,  90),   # 塑膠袋:高雜訊 → Baseline 會贏
    ("SKU_006",  400,  0.20,  0.25,  2.5,  40),   # 米:強趨勢
    ("SKU_007",  350,  0.00,  0.40,  1.5,  30),   # 可樂:純季節品
    ("SKU_008",  600, -0.05,  0.15,  2.0,  55),   # 醬油:弱衰退
    ("SKU_009",  300,  0.30,  0.10,  1.8,  35),   # 礦泉水:新品爆款
    ("SKU_010",  450,  0.03,  0.20,  2.2,  45),   # 寶特瓶飲料:平穩
]
months = pd.date_range("2023-01-01", "2025-12-01", freq="MS")

rows = []
for sku_id, base, trend_rate, season_amp, dbl11, noise in SKU_CONFIG:
    for i, d in enumerate(months):
        trend = base * (1 + trend_rate) ** (i / 12)
        season = trend * season_amp if d.month in (10, 11, 12) else 0
        holiday = trend * (dbl11 - 1) if d.month == 11 else 0
        qty = max(0, int(trend + season + holiday + rng_sales.normal(0, noise)))
        rows.append({"sku_id": sku_id, "date": d.strftime("%Y-%m-%d"), "qty": qty})

sales = pd.DataFrame(rows)
top5 = sales.groupby("sku_id")["qty"].sum().nlargest(5).index.tolist()
sales["is_top5"] = sales["sku_id"].isin(top5)
save(sales, "sales_monthly.csv", f"10 SKU × {len(months)} 個月")

name_of = dict(zip(catalog["sku_id"], catalog["sku_name"]))
print(f"     Top5(銷量最高)= {[f'{s}({name_of[s]})' for s in top5]}")

# ---- 故事線護欄:M3 的 Top5 品項一定要在 M4 的規則裡,不然整合檢查會擋 ----
rule_items = set(rules["antecedent"]) | set(rules["consequent"])
missing = {name_of[s] for s in top5} - rule_items
if missing:
    raise SystemExit(
        f"[ERROR] D12 銷量 Top5 裡的 {sorted(missing)} 沒有出現在 D13 的 Apriori 規則中,\n"
        f"        M3 預測的品項 M4 推薦不到 —— 請調整 SKU_CONFIG 的 base 或 PAIRS 的關聯強度"
    )

# --- Prophet vs Baseline(與 D12 答案版同一套邏輯) ---
TEST_MONTHS, HORIZON = 6, 6
holidays = pd.DataFrame({
    "holiday": "double_11",
    "ds": pd.to_datetime(["2023-11-01", "2024-11-01", "2025-11-01"]),
    "lower_window": 0, "upper_window": 0,
})


def mape(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    ok = y_true > 0
    return np.abs((y_true[ok] - y_pred[ok]) / y_true[ok]).mean() * 100


def baselines(y_train, n_test):
    out = {
        "B1_last": np.array([y_train[-1]] * n_test),
        "B2_3mavg": np.array([y_train[-3:].mean()] * n_test),
    }
    out["B3_lag12"] = (y_train[-12:-12 + n_test] if len(y_train) >= 12 + n_test
                       else out["B2_3mavg"])
    coef = np.polyfit(range(6), y_train[-6:], 1)
    out["B4_linear"] = np.array([np.polyval(coef, 6 + i) for i in range(n_test)])
    return out


def decide(mape_p, mape_b, threshold_pp=2.0):
    if mape_p < mape_b - threshold_pp:
        return f"★ 用 Prophet (差距 {mape_b - mape_p:.1f}pp)"
    if mape_p > mape_b:
        return "用 Baseline (Prophet 沒贏)"
    return f"用 Baseline (差距 {mape_b - mape_p:.1f}pp 太小)"


results = []
for sku_id in top5:
    s = sales[sales["sku_id"] == sku_id].copy()
    s["date"] = pd.to_datetime(s["date"])
    s = s.sort_values("date").reset_index(drop=True)
    train, test = s.iloc[:-TEST_MONTHS], s.iloc[-TEST_MONTHS:]

    b_mape = {n: mape(test["qty"], p)
              for n, p in baselines(train["qty"].values, len(test)).items()}
    best_b = min(b_mape, key=b_mape.get)

    m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False,
                holidays=holidays, interval_width=0.80, seasonality_mode="multiplicative")
    m.fit(train.rename(columns={"date": "ds", "qty": "y"})[["ds", "y"]])

    # Prophet 的 yhat 是決定性的(mcmc_samples=0 → Stan 的 L-BFGS 做 MAP,同資料同結果),
    # 但 yhat_lower / yhat_upper 是 1000 次 Monte Carlo 模擬出來的,而且 Prophet 內部
    # 不設 seed、直接吃 numpy 的全域亂數流 → 不釘住的話,採購建議的「± 多少」每跑一次都不同。
    np.random.seed(RANDOM_STATE)
    fc = m.predict(m.make_future_dataframe(periods=len(test) + HORIZON, freq="MS"))

    p_mape = mape(test["qty"], fc.set_index("ds").loc[test["date"], "yhat"].values)
    nxt = fc.iloc[len(train) + len(test)]        # Test 結束後的第 1 個月 = 要備貨的下個月
    results.append({
        "sku": sku_id,                           # D12 原檔的品號欄就叫 sku
        "train_n": len(train), "test_n": len(test),
        "prophet_mape": p_mape,
        "best_baseline": best_b, "baseline_mape": b_mape[best_b],
        "diff_pp": b_mape[best_b] - p_mape,
        "next_yhat": nxt["yhat"], "next_lower": nxt["yhat_lower"], "next_upper": nxt["yhat_upper"],
        "decision": decide(p_mape, b_mape[best_b]),
    })
    print(f"     {sku_id}({name_of[sku_id]}): Prophet {p_mape:.1f}%  vs  "
          f"{best_b} {b_mape[best_b]:.1f}%  → {results[-1]['decision']}")

fc_df = pd.DataFrame(results)
fc_df["procurement_suggestion"] = fc_df.apply(
    lambda r: f"備貨 {r['next_yhat']:.0f} ± {(r['next_upper'] - r['next_lower']) / 2:.0f}", axis=1)
save(fc_df, "sales_top5_forecast.csv", "★ Top5 預測 + 採購建議")

n_win = sum(r["decision"].startswith("★") for r in results)
print(f"     收口:Prophet 勝 {n_win}/5,Baseline 勝 {5 - n_win}/5(Baseline first 紀律有意義)")

print("\n✅ 來源資料已全部產生到 data/。接著跑:python prepare_data.py")

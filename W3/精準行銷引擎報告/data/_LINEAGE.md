# BOSS III · 資料血緣(由 prepare_data.py 產生,勿手改)

D11~D14 每一天各自用**自己的練習資料集**學一種方法;D15 是整合日,
所有模組必須講同一個故事,所以資料在這裡被對齊成**一份主檔 + 一套商品字典**。

| data/ 檔案 | 來源 | 整合動作 |
|---|---|---|
| `customers.csv` / `customer_clustered.csv` | D14 答案版 | 原樣。**唯一客戶主檔(1,500 人,含 K-means 群)** |
| `customer_rfm.csv` | D14 gen | 原樣(分群前的 RFM) |
| `customer_churn.csv` | D11 的**方法** + 本主檔 | 用 D11 的流失機率模型在主檔 1,500 人上生成 Churn 標籤 |
| `churn_top10.csv` | D11 的**方法** + 本主檔 | 同一棵決策樹(max_depth=4)重訓 → Top10 全部落在主檔的沉睡 / 高風險群 |
| `transactions.csv` | D13 gen | 加上 `customer_id`(依主檔 Frequency 加權指派)→ 客戶 ↔ 交易可 join;`sku_id` 品號 / `sku_name` 品名原樣 |
| `sku_catalog.csv` | D13 gen | **品號字典**(品號 ↔ 品名)── 跨日串接的鍵 |
| `apriori_top5_rules.csv` | D13 答案版 | 原樣(規則是 order × 品名 層級,不受 customer_id 影響) |
| `sales_monthly.csv` / `sales_top5_forecast.csv` | D12 | **數值完全不動**;用品號字典補上 `sku_name`(D12 只有品號沒有品名) |

**注意**:D11 資料夾裡那份 1,000 人的 `customer_churn.csv` / `churn_top10.csv` 是 D11 的
練習資料,**與本主檔的 customer_id 撞名但不是同一批人**,不要拿來混用。

三個 join 鍵:`customer_id`(客戶主檔 ↔ 流失名單 ↔ 交易)、`sku_id` 品號(D12 銷量 ↔ D13 交易)、
`sku_name` 品名(交易 ↔ Apriori 規則)。

品號字典裡 D12 也有月銷量的 10 支:

- `SKU_001` → **尿布**  ← M3 Top5 預測
- `SKU_002` → **起司**  ← M3 Top5 預測
- `SKU_003` → **啤酒**  ← M3 Top5 預測
- `SKU_004` → **紅酒**  ← M3 Top5 預測
- `SKU_005` → **塑膠袋**
- `SKU_006` → **米**  ← M3 Top5 預測
- `SKU_007` → **可樂**
- `SKU_008` → **醬油**
- `SKU_009` → **礦泉水**
- `SKU_010` → **寶特瓶飲料**

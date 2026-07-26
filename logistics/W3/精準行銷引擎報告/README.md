# D15 範例程式 · BOSS III 精準行銷引擎(整合 App)

> **對應講義**:`02_CoursePlan/W3_AI價值師/Day15_教材包/Day15_講義.md`
> **對應任務**:BOSS III · 5 模組 Streamlit App + 5 分鐘 Demo
> **本日性質特殊**:不是教學單一觀念,是把 W3 D11-D14 五天能力整合成一個產品

```
D15_BOSS_III/
├── README.md                      ← 本檔
├── requirements.txt               ← pip 依賴
├── gen_all.py                     ← ★ 合成 D12/D13 來源資料 + 載入 D14 官方分群答案(fixtures/d14/) → data/
├── prepare_data.py                ← ★ 把 data/ 裡的四天產出串接成「一份主檔」(不是單純拷貝)
├── data/                          ← 來源資料與整合結果都放這(與兩支腳本同目錄)
│   ├── customers.csv                  ★ 唯一客戶主檔(1,500 人 + K-means 群)
│   ├── customer_clustered.csv         (同上,沿用舊檔名)
│   ├── customer_rfm.csv               (D14 分群前 RFM)
│   ├── customer_churn.csv             (主檔 + Churn 標籤,用 D11 的方法重算)
│   ├── churn_top10.csv                (在主檔上重算的 Top10)
│   ├── transactions.csv               (D13 訂單 + customer_id,可 join 主檔)
│   ├── sales_monthly.csv              (D12 數值,SKU 改名為品名)
│   ├── sales_top5_forecast.csv        (同上)
│   ├── sku_catalog.csv                (品號字典:品號 ↔ 品名)
│   ├── apriori_top5_rules.csv         (D13 原樣)
│   └── _LINEAGE.md                    ← 資料血緣說明(自動產生)
├── Home.py                        ← Streamlit 主頁(首屏)
├── lib/
│   └── recommend.py               ← 從 D14 移植的推薦函式
└── pages/                         ← Streamlit 自動掃 pages/ 變側邊欄
    ├── 1_M1_客戶儀表板.py
    ├── 2_M2_流失預警.py
    ├── 3_M3_銷量預測.py
    ├── 4_M4_推薦引擎.py
    └── 5_M5_一頁建議書.py
```

> 📌 **非標準四件套**:沿 SOP §十 v1.1 規範,本日改為 Streamlit App 套件。沒有 .ipynb / 示範.py / Orange3.md,因為整合 App 適合直接跑 Streamlit。

## ⚠️ 整合日的資料為什麼要「重接」而不是「拷貝」

D11~D14 每一天各自練一種方法,也**各自用自己的練習資料集** —— 這四份**彼此不可 join**:

| 天 | 練習資料 | 規模 | 問題 |
|---|---|---|---|
| D11 | `customer_churn.csv` | 1,000 客戶 | 與 D14 同 ID **不同人**(R/F/M 全不同) |
| D12 | `sales_monthly.csv` | 10 支 SKU | **只有品號**(`SKU_001…`),沒有品名 |
| D13 | `transactions.csv` | 30 品 | 有品號 + 品名,但**沒有 customer_id**,接不到客戶 |
| D14 | `customer_rfm.csv` | 1,500 客戶 | — |

直接拷進同一個 App,就會出現「M2 說 C0479 已 163 天沒下單、M4 卻說他是 22 天前剛下單的穩定客」這種自打嘴巴的 demo。BOSS III 規則 2 是「**資料一致性:所有模組用同一份客戶 / SKU 主檔**」,所以 `prepare_data.py` 做四件事:

| # | 做什麼 | 對 D11~D14 的影響 |
|---|---|---|
| ① | **一份客戶主檔** = D14 的 1,500 位客戶(含 K-means 群) | 無 |
| ② | **流失名單重算**:借 D11 的方法(同一組流失機率模型 + 同一棵 `max_depth=4` 決策樹)套回主檔 → Top10 必然落在主檔的沉睡 / 高風險群 | 無(D11 那份 1,000 人的練習資料不動) |
| ③ | **交易接上客戶**:D13 訂單加 `customer_id`(依 Frequency 加權指派) | 無(Apriori 是 order × sku 層級,規則 / lift 不變) |
| ④ | **品號 join**:D12 的數值完全不動,用 D13 的品號字典(`sku_catalog.csv`)補上品名 → M3 預測 `SKU_001`,查字典知道是「尿布」,M4 就推「買尿布的人也買啤酒」 | 無(MAPE / 預測值不變) |

跑完會自我檢查五項一致性(全過才會結束),血緣寫在 `data/_LINEAGE.md`。

> **教學上怎麼講**:D11~D14 是「**各自練方法**」,D15 是「**在一份能串起來的資料上,把方法整合成產品**」。

## 前置條件

D15 需要的**來源資料全部放在 `data/`**(與 `gen_all.py`、`prepare_data.py` 同目錄):

| data/ 的 CSV | 相當於哪一天的產出 | 用途 |
|---|---|---|
| `customer_clustered.csv` | D14 答案版 | ★ 客戶主檔(M1 / M2 / M4 / M5 全部吃這份) |
| `customer_rfm.csv` | D14 gen | M1 補充 |
| `transactions.csv` | D13 gen | ★ M4(接上 customer_id 後可 join 主檔) |
| `sku_catalog.csv` | D13 gen | ★ 品號字典(D12 的品號 ↔ 品名) |
| `apriori_top5_rules.csv` | D13 答案版 | ★ M4 |
| `sales_monthly.csv` | D12 gen | ★ M3 |
| `sales_top5_forecast.csv` | D12 答案版 | ★ M3 |

這七個檔可以從各天的資料夾複製過來,**也可以直接用 `gen_all.py` 一次合成**(見下一節)。

> **D11 的 CSV 不在清單裡** —— M2 的流失名單是用 D11 的**方法**在客戶主檔上重算的(見上一節 ②),不是拷貝 D11 那份 1,000 人的練習資料。

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 產生來源資料(從零重建;已經有 data/ 就可跳過)

```bash
python gen_all.py
# 載入 D14 官方分群答案(fixtures/d14/) + 合成 D13 交易籃子/Apriori + D12 月銷量/Prophet → data/
```

`gen_all.py` 會顧好三條故事線的接點,不然 `prepare_data.py` 的整合檢查會擋下來:
分群名稱固定是 M1/M4 頁面寫死的那四個;D12 銷量最高的 5 支 SKU,品名一定出現在 D13 的關聯規則裡(M3 說「下個月尿布備 1,480 個」,M4 才接得下去「買尿布的人也買啤酒」)。
其中 D12 那段沿用 `gen_sales_monthly.py` 的同一組亂數,月銷量數值與 D12 那天**逐格相同**。

### 3. 整合資料(一鍵)

```bash
python prepare_data.py
# 就地(in-place)把 data/ 裡四天的產出對齊成一份主檔 + 一套商品字典
```

預期輸出:

```
① 客戶主檔 ← D14 customer_clustered.csv
[OK] data/customer_clustered.csv        1500 列 × 10 欄   ★ 唯一客戶主檔(1,500 人)
② 流失預測 ← 把 D11 的模型套回主檔的 1,500 人
     bias=-4.794 → 平均流失機率 10.0%
[OK] data/churn_top10.csv                 10 列 × 10 欄   ★ 名單中的人都在主檔裡,群別一致
③ 交易明細 ← D13 transactions.csv + 主檔 customer_id
[OK] data/transactions.csv             13026 列 × 4 欄   ★ 可 join 主檔(1179 位客戶有交易紀錄)
④ 銷量預測 ← D12 原數值 + 統一商品字典
[OK] data/sales_top5_forecast.csv          5 列 × 14 欄   ★ Top5 預測品項 = M4 推薦規則裡的品項

=== 整合檢查 ===
  ✔ churn_top10 的客戶都在主檔裡
  ✔ churn_top10 的群別與主檔一致
  ✔ transactions 的客戶都在主檔裡
  ✔ transactions 的品項都在品號字典裡
  ✔ D12 的品號都查得到品名(品號 join 成功)
  ✔ M3 預測的 Top5 品項都出現在 M4 的 Apriori 規則裡
```

### 4. 啟動 App

```bash
streamlit run Home.py
```

開瀏覽器到 http://localhost:8501,左側欄看到 5 個模組:
- 🏠 Home
- 📊 M1 客戶儀表板
- 🚨 M2 流失預警
- 📈 M3 銷量預測
- 🎯 M4 推薦引擎(★ 核心)
- 📝 M5 一頁建議書

## 5 模組對應

| 模組 | 來源天 | 內容 |
|---|---|---|
| **M1 客戶儀表板** | D14 K-means | 4 群分布 + R/M 散點 + 群描述表 |
| **M2 流失預警** | D11 決策樹 | Top 10 名單 + 風險原因 + 一鍵下載 |
| **M3 銷量預測** | D12 Prophet | SKU 篩選 + 預測線 + 信賴區間 + 採購建議 |
| **M4 推薦引擎** ★ | D13 + D14 | 輸入 customer_id → 群 + Top 3 推薦 + Line OA 文案 |
| **M5 一頁建議書** | 全部 | 給 CMO 的單頁總結(用 Streamlit `st.markdown` + KPI)|

## Demo 5 分鐘節奏(沿 BOSS III 講義)

```
[0:00-0:30]  Home + 一句話結論
[0:30-1:00]  M1 客戶儀表板(30 秒)
[1:00-1:30]  M2 流失預警(30 秒)
[1:30-2:00]  M3 銷量預測(30 秒)
[2:00-3:30]  M4 推薦引擎 ★(90 秒)← 重點
[3:30-4:00]  M5 一頁建議書(30 秒)
[4:00-4:30]  W3 主軸回收「預知 · 推薦 · 創價」
[4:30-5:00]  Q&A
```

## 學員作業

W3 BOSS III 的學員交付物是「**自己跑出 5 個模組的整合 App**」── 本範例是**參考實作**,學員可以:

1. 直接跑(看怎麼運作)
2. 改成自己的 dataset(例如真實公司資料)
3. 加額外功能(What-if 模擬器、雲端部署)
4. 修文案、修配色、修排版

## 與 BOSS II Streamlit 的差異

| 維度 | BOSS II 物流控制塔(W2) | BOSS III 精準行銷引擎(W3) |
|---|---|---|
| 主軸 | 看現在(BI)| 看未來(AI)|
| 模型 | 統計 / 篩選 | 監督式分類 / 回歸 / 非監督式 |
| 互動 | 看數字 | 預測 / 推薦 / 主動建議 |
| 部署 | 內部儀表板 | 對外可展示產品 |

## 已知限制

- 推薦引擎 M4 是**簡化版**(同樣推薦給所有客戶,只差文案語氣)
  - 真實系統需要交易資料 join + LTV / 庫存等
  - W4 進階會展示完整版
- 沒做雲端部署(留 Bonus 加分項,Streamlit Cloud / Render 任選)
- M5 一頁建議書沒接 GenAI(留 Bonus 加分項,可串 Claude API)

## 版本

| 版本 | 日期 | 修訂 |
|---|---|---|
| v0.1 | 2026-05-05 | 初版,沿 BOSS III 講義 5 模組規格 |

---

*Allen老師(AIBILA團隊) · 智慧物流班 · W3 Day 15 BOSS III · 2026*

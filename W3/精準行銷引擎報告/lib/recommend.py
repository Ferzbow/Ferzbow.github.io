# -*- coding: utf-8 -*-
"""
lib/recommend.py
================
推薦引擎函式 ── BOSS III M4 模組核心。

升級版(D13 Apriori × D14 K-means 真整合):
  1. 用「客戶實際買過的品項」去匹配 Apriori 規則的 antecedent
     → 買過尿布的人才推啤酒,不是所有人都推同 3 樣
  2. 不同分群走不同推薦邏輯(策略見 CLUSTER_STRATEGY)
  3. LIFT 門檻 1.3:低於門檻的規則不採用
  4. 規則不足時依分群用「回購 / 新品 / 熱銷」補位,每個推薦都帶推薦理由
"""
import pandas as pd

# 每個推薦商品數不足時的 LIFT 採用門檻
MIN_LIFT = 1.3

# ============================================================
# 分群策略表(給銷售部門的行銷參考,M4 頁面會直接展示)
# ============================================================
CLUSTER_STRATEGY = {
    "VIP 高頻高額": {
        "logic": "關聯交叉銷售:從他買過的品項匹配 Apriori 規則(Lift ≥ 1.3),推「還沒買過」的關聯品",
        "tone":  "尊榮限定 · 專屬折扣 · 套組升級",
        "action": "推套組 88 折 + 尊榮配送,拉高客單價",
    },
    "穩定中段": {
        "logic": "關聯推薦 + 新品試探:先推關聯品,再用新品 SKU 測試提頻",
        "tone":  "新品到貨 · 加購優惠 · 提頻誘因",
        "action": "配套 9 折 + 新品試用價,把 4 次/期買成 6 次/期",
    },
    "流失高風險": {
        "logic": "回購喚回:優先推「他過去最常買」的品項(最低決策門檻),再補關聯品",
        "tone":  "挽留關懷 · 直接折扣 · 客服跟進",
        "action": "常買品項折 200 + 客服主動聯繫,先把人留住",
    },
    "沉睡客戶": {
        "logic": "全站熱銷推薦:沉睡客多半無近期紀錄,用熱銷榜降低喚醒門檻",
        "tone":  "喚醒 · 免運 · 限時回娘家",
        "action": "熱銷 Top 3 任選 2 件 88 折 + 免運,先求回來下一單",
    },
}


def _match_rules(bought, rules, exclude, min_lift=MIN_LIFT):
    """從規則庫挑「antecedent 是客戶買過的品項」且 consequent 沒買過的規則,Lift 高者優先"""
    recs = []
    matched = rules[
        rules["antecedent"].isin(bought)
        & (rules["lift"] >= min_lift)
    ].sort_values("lift", ascending=False)
    for _, r in matched.iterrows():
        if r["consequent"] in exclude:
            continue
        recs.append({
            "sku":        r["consequent"],
            "source":     "關聯規則",
            "reason":     f"買過「{r['antecedent']}」的客戶,{r['confidence']:.0%} 也會買「{r['consequent']}」",
            "lift":       float(r["lift"]),
            "confidence": float(r["confidence"]),
            "from_rule":  f"{r['antecedent']} → {r['consequent']}",
        })
        exclude.add(r["consequent"])
    return recs


def _global_top_rules(rules, exclude, min_lift=MIN_LIFT):
    """無購買紀錄時的備援:全域 Lift 最高規則(商品對去重,避免 A→B / B→A 重複)"""
    recs, seen_pairs = [], set()
    for _, r in rules[rules["lift"] >= min_lift].sort_values("lift", ascending=False).iterrows():
        pair = frozenset([r["antecedent"], r["consequent"]])
        if pair in seen_pairs or r["consequent"] in exclude:
            continue
        seen_pairs.add(pair)
        recs.append({
            "sku":        r["consequent"],
            "source":     "關聯規則",
            "reason":     f"全站強規則:買「{r['antecedent']}」的 {r['confidence']:.0%} 也買「{r['consequent']}」",
            "lift":       float(r["lift"]),
            "confidence": float(r["confidence"]),
            "from_rule":  f"{r['antecedent']} → {r['consequent']}",
        })
        exclude.add(r["consequent"])
    return recs


def recommend(customer_id, df_customers, rules, df_tx=None, df_sku=None,
              top_n=3, min_lift=MIN_LIFT):
    """
    分群差異化推薦。

    Parameters
    ----------
    customer_id : str  例 "C0042"
    df_customers : DataFrame  含 cluster_name(D14 customer_clustered.csv)
    rules : DataFrame  Apriori 規則(D13,需含 antecedent / consequent / confidence / lift)
    df_tx : DataFrame or None  交易明細(order_id / customer_id / sku_name),用來個人化
    df_sku : DataFrame or None  商品目錄(sku_catalog.csv),用來找新品(SKU_NEW)
    top_n : int  推薦商品數
    min_lift : float  關聯規則採用門檻(預設 1.3)

    Returns
    -------
    dict 或 None
    """
    if customer_id not in df_customers["customer_id"].values:
        return None

    row = df_customers[df_customers["customer_id"] == customer_id].iloc[0]
    cluster_name = row.get("cluster_name", "未分群")

    # --- 客戶買過什麼(次數排序) / 全站熱銷榜 ---
    bought_counts = pd.Series(dtype=int)
    hot_counts = pd.Series(dtype=int)
    if df_tx is not None and len(df_tx):
        hot_counts = df_tx["sku_name"].value_counts()
        mine = df_tx[df_tx["customer_id"] == customer_id]
        if len(mine):
            bought_counts = mine["sku_name"].value_counts()
    bought = list(bought_counts.index)

    exclude = set(bought)          # 關聯/新品/熱銷推薦不推已買過的
    recs = []

    # --- 分群差異化邏輯 ---
    if "沉睡" in cluster_name:
        # 沉睡客:直接推全站熱銷(不排除已買 → 他的紀錄早已過期,回購也是喚醒)
        for sku, cnt in hot_counts.head(top_n).items():
            recs.append({
                "sku": sku, "source": "熱銷推薦",
                "reason": f"全站熱銷第 {len(recs)+1} 名(近期共 {cnt} 筆),喚醒門檻最低",
                "lift": None, "confidence": None, "from_rule": "全站熱銷榜",
            })

    elif "流失" in cluster_name:
        # 流失高風險:先推他過去最常買的(回購喚回),再補關聯品
        for sku, cnt in bought_counts.head(2).items():
            recs.append({
                "sku": sku, "source": "回購喚回",
                "reason": f"他過去買過 {cnt} 次的常買品,回購決策門檻最低",
                "lift": None, "confidence": None, "from_rule": "個人購買史",
            })
        recs += _match_rules(bought, rules, exclude, min_lift)

    else:
        # VIP / 穩定中段:關聯交叉銷售為主
        recs += _match_rules(bought, rules, exclude, min_lift)

        # 穩定中段:補新品試探
        if "穩定" in cluster_name and df_sku is not None and len(recs) < top_n:
            new_items = df_sku[df_sku["sku_name"].str.contains("NEW", na=False)]
            for _, s in new_items.iterrows():
                if len(recs) >= top_n or s["sku_name"] in exclude:
                    continue
                recs.append({
                    "sku": s["sku_name"], "source": "新品試探",
                    "reason": "本期新品,穩定客群是新品滲透率最好的測試對象",
                    "lift": None, "confidence": None, "from_rule": "新品目錄",
                })
                exclude.add(s["sku_name"])

    # --- 補位:規則不夠就用全域強規則,再不夠用熱銷 ---
    if len(recs) < top_n:
        recs += _global_top_rules(rules, exclude, min_lift)
    if len(recs) < top_n and len(hot_counts):
        for sku, cnt in hot_counts.items():
            if len(recs) >= top_n:
                break
            if sku in exclude:
                continue
            recs.append({
                "sku": sku, "source": "熱銷推薦",
                "reason": f"全站熱銷(近期共 {cnt} 筆)補位",
                "lift": None, "confidence": None, "from_rule": "全站熱銷榜",
            })
            exclude.add(sku)

    recs = recs[:top_n]

    strategy = CLUSTER_STRATEGY.get(cluster_name, {})
    return {
        "customer_id":     customer_id,
        "cluster":         cluster_name,
        "strategy":        strategy,
        "bought_counts":   bought_counts,   # M4 畫長條圖用
        "recommendations": recs,
        "explain": (
            f"「{cluster_name}」策略:{strategy.get('logic', 'Apriori Lift 排序')}"
        ),
    }


def cluster_action_text(cluster_name):
    """根據群名給 Line OA 文案的開頭語氣"""
    if "VIP" in cluster_name:
        return "VIP 限定!"
    elif "沉睡" in cluster_name:
        return "好久不見!"
    elif "流失" in cluster_name:
        return "搶救!別走!"
    elif "穩定" in cluster_name:
        return "新品到貨!"
    else:
        return "嗨!"


def sales_copy(cluster_name, skus):
    """
    給銷售部門的 3 款推銷文案範本(靜態,不需 API)。
    skus : list[str] 推薦品項名稱
    回傳 list[dict]: {"angle": 切入角度, "text": 文案}
    """
    s = "、".join(skus) if skus else "精選商品"
    first = skus[0] if skus else "精選商品"

    if "VIP" in cluster_name:
        return [
            {"angle": "尊榮套組",
             "text": f"VIP 限定!本月專屬 → {s} 尊榮套組 88 折,出示券碼享 VIP 優先配送。#物流好夥伴"},
            {"angle": "會員日加碼",
             "text": f"您的 VIP 會員日到了🎉 {first} 加購價再 9 折,點數雙倍送,僅此一週。#物流好夥伴"},
            {"angle": "專屬預購",
             "text": f"熱銷預警:{s} 下月看漲,VIP 可鎖今日價提前預購,專人為您保留庫存。#物流好夥伴"},
        ]
    elif "沉睡" in cluster_name:
        return [
            {"angle": "喚醒免運",
             "text": f"好久不見!全站熱銷 {s} 任選 2 件 88 折,本週回購直接免運。#物流好夥伴"},
            {"angle": "限時召回",
             "text": f"專屬老朋友的 48 小時:{first} 直降 15%,錯過要再等一季!#物流好夥伴"},
            {"angle": "熱銷榜推薦",
             "text": f"這季大家都在買:{s}。您的專屬回歸禮券 $100 已入帳,結帳自動折抵。#物流好夥伴"},
        ]
    elif "流失" in cluster_name:
        return [
            {"angle": "回購折扣",
             "text": f"搶救!別走!您常買的 {first} 本週任一件折 200,補貨趁現在。#物流好夥伴"},
            {"angle": "關懷跟進",
             "text": f"最近沒看到您下單,一切都好嗎?{s} 為您保留了專屬價,客服也可協助補貨評估。#物流好夥伴"},
            {"angle": "滿額補貼",
             "text": f"回購 {s} 滿 $1,000 現折 $150 再免運,只給老客戶的誠意價。#物流好夥伴"},
        ]
    else:  # 穩定中段 / 其他
        return [
            {"angle": "新品嘗鮮",
             "text": f"新品到貨!{s} 嘗鮮價 9 折,前 100 名加送試用包。#物流好夥伴"},
            {"angle": "配套加購",
             "text": f"您買過的品項跟 {first} 是絕配!本週配套販售 9 折,加入 Line OA 即享。#物流好夥伴"},
            {"angle": "升級誘因",
             "text": f"再買 2 次即可升級 VIP!本週 {s} 都算雙倍消費額,升級就趁現在。#物流好夥伴"},
        ]

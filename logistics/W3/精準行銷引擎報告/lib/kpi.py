# -*- coding: utf-8 -*-
"""
lib/kpi.py
==========
營收模型共用計算 ── Home.py 與 M5 一頁建議書共用同一套口徑,數字永遠一致。

口徑:
  月均消費 = Monetary ÷ (Tenure/30)
  挽留營收 = 流失高風險群月消費總額 × 挽留成功率
  VIP 套組 = VIP 人數 × 轉換率 × VIP 平均單筆訂單
  沉睡喚醒 = 沉睡人數 × 喚醒率 × 沉睡平均單筆訂單
"""

# 基準假設(行業常見區間) ── Home 的 What-if 拉桿預設值也用這組
DEFAULT_RETENTION = 0.30   # 流失挽留成功率
DEFAULT_VIP_CONV  = 0.30   # VIP 套組轉換率
DEFAULT_WAKE      = 0.15   # 沉睡客喚醒率


def revenue_model(df_customers,
                  retention_rate=DEFAULT_RETENTION,
                  vip_conv_rate=DEFAULT_VIP_CONV,
                  wake_rate=DEFAULT_WAKE):
    """
    Parameters
    ----------
    df_customers : DataFrame  customer_clustered.csv(需含 cluster_name / Monetary / Tenure / AvgOrder)
    retention_rate, vip_conv_rate, wake_rate : float  行銷假設(0~1)

    Returns
    -------
    dict  人數統計 + 三條營收支柱(萬元) + 不作為損失(萬元)
    """
    df = df_customers.copy()
    df["monthly_value"] = df["Monetary"] / (df["Tenure"].clip(lower=30) / 30)

    n_total  = len(df)
    n_vip    = (df["cluster_name"] == "VIP 高頻高額").sum()
    n_atrisk = (df["cluster_name"] == "流失高風險").sum()
    n_sleep  = (df["cluster_name"] == "沉睡客戶").sum()

    atrisk_monthly  = df.loc[df["cluster_name"] == "流失高風險", "monthly_value"].sum()
    vip_avg_order   = df.loc[df["cluster_name"] == "VIP 高頻高額", "AvgOrder"].mean()
    sleep_avg_order = df.loc[df["cluster_name"] == "沉睡客戶", "AvgOrder"].mean()

    rev_retain = atrisk_monthly * retention_rate / 10000
    rev_vip    = n_vip * vip_conv_rate * vip_avg_order / 10000
    rev_wake   = n_sleep * wake_rate * sleep_avg_order / 10000

    return {
        "n_total": n_total, "n_vip": n_vip, "n_atrisk": n_atrisk, "n_sleep": n_sleep,
        "atrisk_monthly_wan": atrisk_monthly / 10000,
        "vip_avg_order": vip_avg_order, "sleep_avg_order": sleep_avg_order,
        "retention_rate": retention_rate, "vip_conv_rate": vip_conv_rate, "wake_rate": wake_rate,
        "rev_retain": rev_retain, "rev_vip": rev_vip, "rev_wake": rev_wake,
        "rev_total": rev_retain + rev_vip + rev_wake,
        "loss_inaction": atrisk_monthly / 10000,
    }

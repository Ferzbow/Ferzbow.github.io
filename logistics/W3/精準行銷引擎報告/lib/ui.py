# -*- coding: utf-8 -*-
"""
lib/ui.py
=========
全站統一的排版元件 ── 五頁共用,風格一致。

頁面結構約定:
  page_header()  → 模組代號 + 口語副標 + 標題 + 說明 + 分析基礎徽章
  how_to_read()  → 頁尾「主管怎麼用」判讀區塊(承講師評分:商業判讀)
  footer()       → 組別 + 資料版本
"""
import streamlit as st

DATA_VERSION = "d15-2026-07-16"


def page_header(code, tagline, title, desc, basis):
    """統一頁首:代號 · 口語副標 → 大標 → 一句話說明 → 分析基礎徽章

    Parameters
    ----------
    code : str  模組代號,例 "M1"
    tagline : str  口語副標,例 "看誰是誰"
    title : str  頁面大標(含 emoji)
    desc : str  一句話說明這頁給誰看、怎麼用
    basis : str  分析基礎(資料來源與範圍,可追溯)
    """
    st.caption(f"{code} · {tagline}")
    st.title(title)
    st.caption(desc)
    st.markdown(f"`分析基礎` {basis}")


def how_to_read(text, caveat=None):
    """頁尾「主管怎麼用」判讀區塊 + 誠實註記"""
    st.info(f"👔 **主管怎麼用**:{text}")
    if caveat:
        st.caption(f"⚠ {caveat}")


def footer():
    """統一頁尾:組別 + 資料版本"""
    st.divider()
    st.caption(f"W3 第 6 組 · 智慧物流班 · BOSS III · 2026 · 資料版本 {DATA_VERSION}")

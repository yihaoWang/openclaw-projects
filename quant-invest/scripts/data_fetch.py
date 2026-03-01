#!/usr/bin/env python3
"""
data_fetch.py — 台股資料抓取
使用 yfinance 取得歷史價格、基本面資料
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)


# 台股主要標的池（市值前 100 + 熱門 ETF）
# 這個清單會隨著策略調整而更新
TW_UNIVERSE = [
    # 半導體
    "2330.TW",  # 台積電
    "2454.TW",  # 聯發科
    "3711.TW",  # 日月光
    "2303.TW",  # 聯電
    "3034.TW",  # 聯詠
    "2379.TW",  # 瑞昱
    "3529.TW",  # 力旺
    "6770.TW",  # 力積電
    # 電子
    "2317.TW",  # 鴻海
    "2382.TW",  # 廣達
    "2357.TW",  # 華碩
    "3231.TW",  # 緯創
    "2345.TW",  # 智邦
    "2308.TW",  # 台達電
    "2412.TW",  # 中華電
    "4904.TW",  # 遠傳
    # 金融
    "2881.TW",  # 富邦金
    "2882.TW",  # 國泰金
    "2884.TW",  # 玉山金
    "2886.TW",  # 兆豐金
    "2891.TW",  # 中信金
    "2892.TW",  # 第一金
    # 傳產
    "1301.TW",  # 台塑
    "1303.TW",  # 南亞
    "2002.TW",  # 中鋼
    "1216.TW",  # 統一
    "2207.TW",  # 和泰車
    "9910.TW",  # 豐泰
    # 航運
    "2603.TW",  # 長榮
    "2609.TW",  # 陽明
    "2615.TW",  # 萬海
    # 生技
    "6446.TW",  # 藥華藥
    "4743.TW",  # 合一
    # ETF
    "0050.TW",  # 元大台灣50
    "0056.TW",  # 元大高股息
    "00878.TW", # 國泰永續高股息
    "00919.TW", # 群益台灣精選高息
]


def fetch_history(symbol: str, period_years: int = 3) -> pd.DataFrame:
    """抓取個股歷史價格"""
    end = datetime.now()
    start = end - timedelta(days=period_years * 365)
    
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end)
    
    if df.empty:
        print(f"  ⚠️ {symbol}: 無資料")
        return df
    
    df.index = df.index.tz_localize(None)
    return df


def fetch_info(symbol: str) -> dict:
    """抓取個股基本面資訊"""
    ticker = yf.Ticker(symbol)
    try:
        info = ticker.info
        return {
            'symbol': symbol,
            'name': info.get('longName', info.get('shortName', symbol)),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', None),
            'forward_pe': info.get('forwardPE', None),
            'dividend_yield': info.get('dividendYield', None),
            'revenue_growth': info.get('revenueGrowth', None),
            'profit_margin': info.get('profitMargins', None),
            'fifty_day_avg': info.get('fiftyDayAverage', None),
            'two_hundred_day_avg': info.get('twoHundredDayAverage', None),
        }
    except Exception as e:
        print(f"  ⚠️ {symbol}: 無法取得資訊 ({e})")
        return {'symbol': symbol, 'error': str(e)}


def fetch_all(symbols: list = None, period_years: int = 3) -> dict:
    """批量抓取所有標的"""
    if symbols is None:
        symbols = TW_UNIVERSE
    
    results = {}
    total = len(symbols)
    
    for i, sym in enumerate(symbols):
        print(f"  [{i+1}/{total}] {sym}...", end=" ")
        
        # 價格
        hist = fetch_history(sym, period_years)
        if hist.empty:
            continue
        
        # 基本面
        info = fetch_info(sym)
        
        results[sym] = {
            'history': hist,
            'info': info
        }
        print(f"✅ ({len(hist)} 筆)")
    
    return results


def save_cache(results: dict):
    """儲存快取"""
    today = datetime.now().strftime('%Y-%m-%d')
    cache_dir = os.path.join(DATA_DIR, today)
    os.makedirs(cache_dir, exist_ok=True)
    
    for sym, data in results.items():
        safe_name = sym.replace('.', '_')
        data['history'].to_csv(os.path.join(cache_dir, f"{safe_name}_history.csv"))
        with open(os.path.join(cache_dir, f"{safe_name}_info.json"), 'w') as f:
            json.dump(data['info'], f, ensure_ascii=False, indent=2)
    
    print(f"💾 快取已存入 {cache_dir}")


if __name__ == "__main__":
    print("📊 開始抓取台股資料...")
    results = fetch_all()
    save_cache(results)
    print(f"✅ 完成，共 {len(results)} 檔")

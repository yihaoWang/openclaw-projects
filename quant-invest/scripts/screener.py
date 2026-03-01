#!/usr/bin/env python3
"""
screener.py — 台股選股篩選器
根據 config/screening_rules.yaml 篩選候選股
"""

import pandas as pd
import numpy as np
import yaml
import os
from data_fetch import fetch_all, TW_UNIVERSE


def load_rules(config_path: str = None) -> dict:
    """載入選股規則"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'screening_rules.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """計算 RSI"""
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def compute_ma(series: pd.Series, period: int) -> pd.Series:
    """計算移動平均"""
    return series.rolling(window=period).mean()


def screen_stock(symbol: str, history: pd.DataFrame, info: dict, rules: dict) -> dict:
    """篩選單一個股，回傳評分結果"""
    result = {
        'symbol': symbol,
        'name': info.get('name', symbol),
        'passed': True,
        'score': 0,
        'reasons': [],
        'fails': [],
    }
    
    if len(history) < 120:  # 至少需要半年數據
        result['passed'] = False
        result['fails'].append('數據不足（< 120 天）')
        return result
    
    close = history['Close']
    volume = history['Volume']
    latest = close.iloc[-1]
    
    # === 基本面 ===
    fund = rules.get('fundamentals', {})
    
    # 市值
    market_cap = info.get('market_cap', 0)
    min_cap = fund.get('min_market_cap_tw_billion', 50) * 1e9
    if market_cap and market_cap < min_cap:
        result['passed'] = False
        result['fails'].append(f'市值不足（{market_cap/1e9:.0f}B < {min_cap/1e9:.0f}B）')
    
    # 本益比
    pe = info.get('pe_ratio')
    if pe is not None:
        pe_rules = fund.get('pe_ratio', {})
        if pe < pe_rules.get('min', 0) or pe > pe_rules.get('max', 999):
            result['passed'] = False
            result['fails'].append(f'PE 不在範圍（{pe:.1f}）')
        else:
            result['score'] += 1
            result['reasons'].append(f'PE {pe:.1f} 合理')
    
    # 營收成長
    rev_growth = info.get('revenue_growth')
    if rev_growth is not None and rev_growth > 0:
        result['score'] += 2
        result['reasons'].append(f'營收成長 {rev_growth*100:.1f}%')
    
    # === 技術面 ===
    tech = rules.get('technicals', {})
    
    # 均線
    for ma_period in tech.get('above_ma', [60]):
        ma = compute_ma(close, ma_period)
        if not ma.empty and latest > ma.iloc[-1]:
            result['score'] += 1
            result['reasons'].append(f'在 {ma_period} 日均線之上')
        else:
            result['passed'] = False
            result['fails'].append(f'在 {ma_period} 日均線之下')
    
    # RSI
    rsi = compute_rsi(close, 14)
    current_rsi = rsi.iloc[-1]
    rsi_rules = tech.get('rsi_14', {})
    if current_rsi < rsi_rules.get('min', 0) or current_rsi > rsi_rules.get('max', 100):
        result['passed'] = False
        result['fails'].append(f'RSI {current_rsi:.0f} 超出範圍')
    else:
        result['score'] += 1
        result['reasons'].append(f'RSI {current_rsi:.0f}')
    
    # 成交量
    avg_vol = volume.tail(20).mean()
    min_vol = tech.get('min_avg_volume_20d', 1000)
    if avg_vol < min_vol * 1000:  # 張 → 股
        result['passed'] = False
        result['fails'].append(f'成交量不足（{avg_vol/1000:.0f} 張）')
    
    # === 排除條件 ===
    exclude = rules.get('exclude', {})
    if symbol in exclude.get('symbols', []):
        result['passed'] = False
        result['fails'].append('在排除清單中')
    
    sector = info.get('sector', '')
    if sector in exclude.get('sectors', []):
        result['passed'] = False
        result['fails'].append(f'產業 {sector} 被排除')
    
    # 額外技術指標加分
    # 短期動能
    if len(close) >= 20:
        momentum_20d = (latest / close.iloc[-20] - 1) * 100
        if 0 < momentum_20d < 15:
            result['score'] += 1
            result['reasons'].append(f'20日動能 +{momentum_20d:.1f}%')
    
    result['rsi'] = current_rsi
    result['price'] = latest
    
    return result


def run_screening(data: dict = None, rules: dict = None) -> list:
    """執行完整篩選流程"""
    if rules is None:
        rules = load_rules()
    
    if data is None:
        print("📊 抓取資料中...")
        data = fetch_all()
    
    print(f"\n🔍 開始篩選（{len(data)} 檔）...")
    
    results = []
    for sym, stock_data in data.items():
        result = screen_stock(sym, stock_data['history'], stock_data['info'], rules)
        results.append(result)
    
    # 篩選通過的
    passed = [r for r in results if r['passed']]
    failed = [r for r in results if not r['passed']]
    
    # 按分數排序
    passed.sort(key=lambda x: x['score'], reverse=True)
    
    # 取前 N 檔
    select_count = rules.get('select_count', '3-5')
    if isinstance(select_count, str):
        max_count = int(select_count.split('-')[-1])
    else:
        max_count = select_count
    
    selected = passed[:max_count]
    
    print(f"\n✅ 通過篩選：{len(passed)} 檔")
    print(f"❌ 未通過：{len(failed)} 檔")
    print(f"🎯 精選：{len(selected)} 檔")
    
    for s in selected:
        print(f"  • {s['symbol']} {s['name']} (分數: {s['score']}) — {', '.join(s['reasons'])}")
    
    return {
        'selected': selected,
        'passed': passed,
        'failed': failed,
        'rules_version': 'v1.0',
    }


if __name__ == "__main__":
    result = run_screening()
    print(f"\n🎯 最終選股：")
    for s in result['selected']:
        print(f"  {s['symbol']} — {s['name']}")
        print(f"    分數: {s['score']} | RSI: {s.get('rsi', 'N/A'):.0f} | 價格: {s.get('price', 'N/A'):.2f}")
        print(f"    理由: {', '.join(s['reasons'])}")

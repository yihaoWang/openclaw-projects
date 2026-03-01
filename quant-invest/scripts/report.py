#!/usr/bin/env python3
"""
report.py — 產出分析報告（Markdown 格式）
整合選股 + 回測結果
"""

import os
import sys
from datetime import datetime

# 加入 scripts 目錄到 path
sys.path.insert(0, os.path.dirname(__file__))

from data_fetch import fetch_all, fetch_history
from screener import run_screening, load_rules
from backtest import backtest_stock, format_report


def generate_weekly_report(output_path: str = None) -> str:
    """產出完整週報"""
    
    rules = load_rules()
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    week_str = now.strftime('%Y-W%W')
    
    print("=" * 50)
    print(f"📈 Quant Invest 週報 — {date_str}")
    print("=" * 50)
    
    # Step 1: 抓資料
    print("\n📊 Step 1: 抓取資料...")
    data = fetch_all()
    
    # Step 2: 選股
    print("\n🔍 Step 2: 篩選選股...")
    screening = run_screening(data, rules)
    selected = screening['selected']
    
    # Step 3: 回測
    print("\n📈 Step 3: 回測選中個股...")
    backtest_results = {}
    for stock in selected:
        sym = stock['symbol']
        if sym in data:
            result = backtest_stock(sym, data[sym]['history'], rules)
            backtest_results[sym] = {
                'result': result,
                'name': stock['name'],
                'screening': stock,
            }
    
    # Step 4: 回測大盤基準
    print("\n📊 Step 4: 回測大盤基準...")
    benchmark_sym = rules.get('backtest', {}).get('benchmark', '^TWII')
    benchmark_hist = fetch_history(benchmark_sym, period_years=3)
    benchmark_return = 0
    if not benchmark_hist.empty:
        benchmark_return = (benchmark_hist['Close'].iloc[-1] / benchmark_hist['Close'].iloc[0] - 1) * 100
    
    # Step 5: 產出報告
    print("\n📝 Step 5: 產出報告...")
    
    report = f"""# 📈 Quant Invest 週報 — {date_str}

> 策略版本：{screening['rules_version']}
> 標的池：台股 {len(data)} 檔
> 篩選通過：{len(screening['passed'])} 檔
> 精選：{len(selected)} 檔

---

## 🎯 本週精選

"""
    
    for stock in selected:
        sym = stock['symbol']
        report += f"### {sym} {stock['name']}\n\n"
        report += f"**選股理由：** {', '.join(stock['reasons'])}\n\n"
        
        if sym in backtest_results:
            bt = backtest_results[sym]['result']
            m = bt['metrics']
            
            if 'note' not in m:
                report += f"""**回測績效（近 3 年）：**
- 總報酬率：{m['total_return']:+.1f}%（大盤同期：{benchmark_return:+.1f}%）
- 年化報酬：{m['annual_return']:+.1f}%
- 最大回撤：{m['max_drawdown']:.1f}%
- Sharpe Ratio：{m['sharpe_ratio']:.2f}
- 勝率：{m['win_rate']:.0f}%（{m['total_trades']} 筆交易）
- 平均持有：{m['avg_holding_days']:.0f} 天

"""
                # 最近幾筆交易
                if bt['trades']:
                    report += "**近期交易：**\n"
                    for t in bt['trades'][-5:]:
                        emoji = "🟢" if t['pnl_pct'] > 0 else "🔴"
                        report += f"- {emoji} {t['entry_date'][:10]} → {t['exit_date'][:10]} | {t['pnl_pct']:+.1f}% | {t['exit_reason']}\n"
                    report += "\n"
            else:
                report += f"⚠️ {m['note']}\n\n"
        
        report += "---\n\n"
    
    # 大盤概況
    report += f"""## 📊 大盤基準

- 台灣加權指數（{benchmark_sym}）近 3 年報酬：{benchmark_return:+.1f}%

"""
    
    # 篩選摘要
    report += "## 🔍 篩選摘要\n\n"
    report += f"通過篩選但未入選的（供參考）：\n\n"
    for stock in screening['passed'][len(selected):len(selected)+5]:
        report += f"- {stock['symbol']} {stock['name']}（分數: {stock['score']}）\n"
    
    report += f"\n未通過篩選的主要原因：\n\n"
    fail_reasons = {}
    for stock in screening['failed']:
        for fail in stock['fails']:
            key = fail.split('（')[0]
            fail_reasons[key] = fail_reasons.get(key, 0) + 1
    for reason, count in sorted(fail_reasons.items(), key=lambda x: -x[1])[:5]:
        report += f"- {reason}：{count} 檔\n"
    
    # 待討論
    report += f"""

---

## 💬 待討論事項

1. 本週選股結果是否合理？有沒有你覺得不該選的？
2. 回測績效如何？有沒有需要調整的規則？
3. 有沒有想加入觀察的個股？
4. 下週有什麼重要事件需要注意？（財報、法說會等）

---

> 📋 選股規則：`config/screening_rules.yaml`
> 📈 策略進化：`EVOLUTION.md`
"""
    
    # 儲存
    if output_path is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'journal', 'weekly')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{week_str}.md")
    
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"\n✅ 報告已存入：{output_path}")
    return report


if __name__ == "__main__":
    report = generate_weekly_report()
    print("\n" + "=" * 50)
    print(report)

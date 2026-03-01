#!/usr/bin/env python3
"""
backtest.py — 輕量回測引擎
設計原則：簡單、透明、容易理解每一步在幹嘛
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import yaml


def load_rules(config_path: str = None) -> dict:
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'screening_rules.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def compute_ma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).mean()


class Trade:
    """單筆交易紀錄"""
    def __init__(self, symbol, entry_date, entry_price, shares, reason):
        self.symbol = symbol
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.shares = shares
        self.entry_reason = reason
        self.exit_date = None
        self.exit_price = None
        self.exit_reason = None
        self.pnl = 0
        self.pnl_pct = 0
        self.holding_days = 0
    
    def close(self, exit_date, exit_price, reason, commission_rate, tax_rate):
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_reason = reason
        
        gross_pnl = (exit_price - self.entry_price) * self.shares
        entry_cost = self.entry_price * self.shares * commission_rate
        exit_cost = exit_price * self.shares * (commission_rate + tax_rate)
        self.pnl = gross_pnl - entry_cost - exit_cost
        self.pnl_pct = self.pnl / (self.entry_price * self.shares)
        self.holding_days = (exit_date - self.entry_date).days if isinstance(exit_date, datetime) else 0
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'entry_date': str(self.entry_date),
            'entry_price': self.entry_price,
            'exit_date': str(self.exit_date),
            'exit_price': self.exit_price,
            'shares': self.shares,
            'pnl': round(self.pnl, 2),
            'pnl_pct': round(self.pnl_pct * 100, 2),
            'holding_days': self.holding_days,
            'entry_reason': self.entry_reason,
            'exit_reason': self.exit_reason,
        }


def backtest_stock(symbol: str, history: pd.DataFrame, rules: dict) -> dict:
    """對單一個股執行回測"""
    
    bt_config = rules.get('backtest', {})
    entry_rules = rules.get('entry', {})
    exit_rules = rules.get('exit', {})
    
    commission = bt_config.get('commission_rate', 0.001425)
    tax = bt_config.get('tax_rate', 0.003)
    capital = bt_config.get('initial_capital', 1000000)
    position_pct = bt_config.get('position_size', 0.20)
    
    take_profit = exit_rules.get('take_profit', 0.15)
    stop_loss = exit_rules.get('stop_loss', -0.08)
    rsi_exit = exit_rules.get('rsi_overbought', 75)
    trailing_pct = exit_rules.get('trailing_stop', 0.10)
    
    close = history['Close']
    rsi = compute_rsi(close, 14)
    ma60 = compute_ma(close, 60)
    
    trades = []
    current_trade = None
    peak_price = 0
    equity_curve = []
    cash = capital
    
    for i in range(60, len(history)):
        date = history.index[i]
        price = close.iloc[i]
        current_rsi = rsi.iloc[i]
        current_ma60 = ma60.iloc[i]
        
        # 持有中 → 檢查出場
        if current_trade is not None:
            peak_price = max(peak_price, price)
            unrealized_pct = (price / current_trade.entry_price) - 1
            trailing_drawdown = (price / peak_price) - 1
            
            exit_reason = None
            
            if unrealized_pct >= take_profit:
                exit_reason = f'停利 ({unrealized_pct*100:.1f}%)'
            elif unrealized_pct <= stop_loss:
                exit_reason = f'停損 ({unrealized_pct*100:.1f}%)'
            elif current_rsi > rsi_exit:
                exit_reason = f'RSI 超買 ({current_rsi:.0f})'
            elif trailing_drawdown <= -trailing_pct:
                exit_reason = f'追蹤停損 (從高點回落 {trailing_drawdown*100:.1f}%)'
            
            if exit_reason:
                current_trade.close(date, price, exit_reason, commission, tax)
                cash += price * current_trade.shares
                trades.append(current_trade)
                current_trade = None
                peak_price = 0
        
        # 未持有 → 檢查進場
        if current_trade is None:
            # RSI 從超賣回升 + 在季線之上
            prev_rsi = rsi.iloc[i-1] if i > 0 else 50
            if prev_rsi < 35 and current_rsi >= 35 and price > current_ma60:
                position_capital = capital * position_pct
                shares = int(position_capital / price / 1000) * 1000  # 台股整張
                if shares > 0 and cash >= price * shares:
                    current_trade = Trade(symbol, date, price, shares, 
                                         f'RSI 回升 ({prev_rsi:.0f}→{current_rsi:.0f}), 在 MA60 之上')
                    cash -= price * shares
                    peak_price = price
        
        # 記錄權益
        holding_value = current_trade.shares * price if current_trade else 0
        equity_curve.append({
            'date': date,
            'equity': cash + holding_value,
        })
    
    # 如果還有持倉，強制平倉
    if current_trade is not None:
        last_price = close.iloc[-1]
        current_trade.close(history.index[-1], last_price, '回測結束平倉', commission, tax)
        cash += last_price * current_trade.shares
        trades.append(current_trade)
    
    # 計算績效
    equity_df = pd.DataFrame(equity_curve)
    if equity_df.empty:
        return {
            'symbol': symbol,
            'trades': [],
            'metrics': {'total_return': 0, 'note': '無交易信號'},
        }
    
    equity_df.set_index('date', inplace=True)
    final_equity = equity_df['equity'].iloc[-1]
    total_return = (final_equity / capital) - 1
    
    # 年化報酬
    days = (equity_df.index[-1] - equity_df.index[0]).days
    annual_return = (1 + total_return) ** (365 / max(days, 1)) - 1
    
    # 最大回撤
    rolling_max = equity_df['equity'].cummax()
    drawdown = (equity_df['equity'] / rolling_max) - 1
    max_drawdown = drawdown.min()
    
    # Sharpe Ratio (簡化版，假設無風險利率 2%)
    daily_returns = equity_df['equity'].pct_change().dropna()
    if len(daily_returns) > 0 and daily_returns.std() > 0:
        sharpe = (daily_returns.mean() - 0.02/252) / daily_returns.std() * np.sqrt(252)
    else:
        sharpe = 0
    
    # 勝率
    winning = [t for t in trades if t.pnl > 0]
    win_rate = len(winning) / len(trades) if trades else 0
    
    metrics = {
        'total_return': round(total_return * 100, 2),
        'annual_return': round(annual_return * 100, 2),
        'max_drawdown': round(max_drawdown * 100, 2),
        'sharpe_ratio': round(sharpe, 2),
        'total_trades': len(trades),
        'win_rate': round(win_rate * 100, 1),
        'winning_trades': len(winning),
        'losing_trades': len(trades) - len(winning),
        'avg_holding_days': round(np.mean([t.holding_days for t in trades]), 1) if trades else 0,
        'final_equity': round(final_equity, 0),
        'initial_capital': capital,
    }
    
    return {
        'symbol': symbol,
        'trades': [t.to_dict() for t in trades],
        'metrics': metrics,
        'equity_curve': equity_df,
    }


def format_report(symbol: str, name: str, result: dict) -> str:
    """格式化單股回測報告"""
    m = result['metrics']
    
    if 'note' in m:
        return f"📊 {symbol} {name}\n  ⚠️ {m['note']}\n"
    
    report = f"""📊 {symbol} {name}
  總報酬率：{m['total_return']:+.1f}%
  年化報酬：{m['annual_return']:+.1f}%
  最大回撤：{m['max_drawdown']:.1f}%
  Sharpe Ratio：{m['sharpe_ratio']:.2f}
  勝率：{m['win_rate']:.0f}%（{m['winning_trades']} 勝 / {m['losing_trades']} 負）
  交易次數：{m['total_trades']}
  平均持有：{m['avg_holding_days']:.0f} 天
  最終資金：${m['final_equity']:,.0f}（本金 ${m['initial_capital']:,.0f}）"""
    
    return report


if __name__ == "__main__":
    from data_fetch import fetch_history
    
    rules = load_rules()
    
    # 測試單一個股
    symbol = "2330.TW"
    print(f"📈 回測 {symbol}...")
    history = fetch_history(symbol, period_years=3)
    
    if not history.empty:
        result = backtest_stock(symbol, history, rules)
        print(format_report(symbol, "台積電", result))
        
        if result['trades']:
            print(f"\n📋 交易明細：")
            for t in result['trades']:
                print(f"  {t['entry_date'][:10]} 買 ${t['entry_price']:.0f} → "
                      f"{t['exit_date'][:10]} 賣 ${t['exit_price']:.0f} | "
                      f"{t['pnl_pct']:+.1f}% | {t['exit_reason']}")

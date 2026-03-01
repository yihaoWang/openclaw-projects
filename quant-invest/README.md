# Quant Invest 📈

自動化量化投資分析系統。AI 自動選股、回測、追蹤，搭配每週人機協作復盤持續優化策略。

## 涵蓋市場

- 🇹🇼 **台股**（Phase 1 — 目前）
- 🇺🇸 美股（Phase 2）
- 🇯🇵 日股（Phase 3）
- 🪙 加密貨幣（Phase 4）

## 核心迴圈

```
週一 AM：AI 自動分析 + 選股 3-5 檔 + 回測 → 推送報告
   ↓
週一～五：每日追蹤持股表現
   ↓
週五 PM：AI 產出週報（表現、觀察、問題）
   ↓
週末：Yihao + AI 復盤討論
  - Yihao 的觀點、直覺、質疑
  - AI 的數據分析、回測結果
  - 共同決定下週調整方向
   ↓
討論結論寫入 journal/weekly/YYYY-WXX.md
   ↓
下週一：AI 讀取上週討論紀錄 → 納入本週分析 → 重複
```

## 策略進化原則

- **每週最多改一個變數** — 改太多就不知道什麼起作用
- **每次調整都記錄** — 寫入 EVOLUTION.md（為什麼改、改了什麼、改前改後對比）
- **策略分級**：研究中 → 回測通過 → 模擬交易 → 小額實測 → 正式使用
- **人機協作** — AI 跑數據，人做最終判斷

## 排程

| 時間 | 事件 | 執行者 |
|------|------|--------|
| 週一 07:00 (UTC+8) | 自動分析 + 選股 + 回測 + 報告 | AI cron |
| 週五 18:00 (UTC+8) | 週報：表現 + 觀察 + 待討論問題 | AI cron |
| 週末 | 復盤討論 | Yihao + AI |
| 討論後 | 寫入紀錄 + 更新規則 | AI |

### Cron Jobs

- **週一分析**：`quant-invest-monday`
- **週五週報**：`quant-invest-friday`

### 手動觸發

```bash
openclaw cron run <monday-cron-id>
openclaw cron run <friday-cron-id>
```

## 檔案結構

```
quant-invest/
├── README.md                  # 本文件
├── EVOLUTION.md               # 策略進化紀錄（版本 + 每次調整的原因和結果）
├── config/
│   └── screening_rules.yaml   # 選股規則（可由討論調整）
├── scripts/
│   ├── data_fetch.py          # 資料抓取（yfinance）
│   ├── screener.py            # 選股篩選
│   ├── backtest.py            # 回測引擎
│   ├── sentiment.py           # 情緒分析
│   └── report.py              # 報告生成
├── strategies/                # 策略庫
│   └── v1/
│       ├── README.md          # 策略說明
│       └── CHANGELOG.md       # 迭代紀錄
├── journal/
│   ├── weekly/                # 每週報告 + 討論紀錄
│   │   └── YYYY-WXX.md
│   └── decisions/             # 買賣決策紀錄
├── results/                   # 回測結果
└── data/                      # 快取數據（.gitignore）
```

## 回測設定（台股）

- 歷史期間：近 3 年
- 手續費：0.1425%（買賣各一次）
- 證交稅：0.3%（賣出）
- 基準：台灣加權指數（^TWII）
- 訓練集 / 驗證集分開（避免過度擬合）

## 回測陷阱防護

- ⚠️ 過度擬合：限制參數調整次數，訓練/驗證分離
- ⚠️ 倖存者偏差：納入已下市股票（如有數據）
- ⚠️ 前視偏差：只用當時可取得的資訊
- ⚠️ 交易成本：內建手續費 + 稅

## 從零重建

```bash
# 安裝依賴
pip install yfinance pandas numpy

# 建立 cron jobs（記得替換 Telegram 資訊）
# 週一分析：cron "0 23 * * 0" (UTC) = 週一 07:00 UTC+8
# 週五週報：cron "0 10 * * 5" (UTC) = 週五 18:00 UTC+8
```

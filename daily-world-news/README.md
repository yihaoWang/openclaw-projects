# Daily World News 🌍

自動化國際新聞整理系統。每天早上定時從全球主要新聞來源蒐集重點新聞，產出繁體中文摘要。

## 運作方式

- **排程**：每天 UTC 23:00（台灣時間 07:00）由 OpenClaw cron job 自動執行
- **Cron ID**：`71c85d19-ff69-409f-b03d-9d7bed7c8268`
- **模型**：Sonnet (low thinking)
- **超時**：10 分鐘
- **推送**：Telegram General 頻道 (`-1003767828002`)

## 流程

1. 讀取 `SOURCES.md` 取得新聞來源清單
2. 讀取 `FORMAT.md` 取得產出格式規範
3. 用 `web_search` 搜尋各地區當日重點新聞
4. 產出繁體中文摘要（15-20 則精選，去重複）
5. 存入 `summaries/YYYY-MM-DD.md` + git push
6. 推送到 Telegram

## 產出規範

- **數量**：15-20 則精選新聞（質 > 量）
- **去重複**：同一事件不同來源只保留一則，合併多方觀點
- **深度**：每則 2-3 句（事件 + 背景 + 影響）
- **來源**：每則附原始連結
- **格式**：詳見 [FORMAT.md](FORMAT.md)

## 檔案結構

```
daily-world-news/
├── README.md       # 本文件 — 專案說明 & 運作方式
├── SOURCES.md      # 新聞來源清單（歡迎討論調整）
├── FORMAT.md       # 產出格式規範（歡迎討論調整）
└── summaries/      # 每日摘要
    └── YYYY-MM-DD.md
```

## 如何調整

- **來源**：編輯 [SOURCES.md](SOURCES.md)，下次執行自動生效
- **格式**：編輯 [FORMAT.md](FORMAT.md)，下次執行自動生效
- **手動觸發**：`openclaw cron run 71c85d19-ff69-409f-b03d-9d7bed7c8268`

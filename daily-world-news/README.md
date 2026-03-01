# Daily World News 🌍

自動化國際新聞整理系統。每天早上從全球主要新聞來源蒐集重點新聞，產出繁體中文摘要 + podcast 風格語音播報。

## 每日產出

1. **📝 文字摘要** (`summaries/YYYY-MM-DD.md`) — 15-20 則精選新聞，重大事件附多國觀點對比
2. **🎙️ Podcast 播報稿** (`summaries/YYYY-MM-DD-podcast.md`) — 口語化改寫，融合重點，像主持人在聊天
3. **🔊 語音檔** (`summaries/YYYY-MM-DD.mp3`) — 從 podcast 稿生成，約 8-15 分鐘
4. **Telegram 推送** — 文字版 + 語音檔自動發送

## 運作方式

### 排程

- **時間**：每天 UTC 23:00（台灣時間 07:00）
- **執行者**：OpenClaw cron job
- **Cron ID**：`71c85d19-ff69-409f-b03d-9d7bed7c8268`
- **模型**：Sonnet (low thinking)
- **超時**：10 分鐘

### 執行流程

1. 讀取 `SOURCES.md` → 新聞來源清單
2. 讀取 `FORMAT.md` → 文字摘要格式規範
3. 用 `web_search` 搜尋各地區當日重點新聞
4. 對重大國際事件，搜尋同一事件在不同國家媒體的報導，比較觀點差異
5. 產出文字摘要 → 存入 `summaries/YYYY-MM-DD.md`
6. 讀取 `PODCAST_PROMPT.md` → podcast 風格指引
7. 將文字摘要改寫為 podcast 口語播報稿 → 存入 `summaries/YYYY-MM-DD-podcast.md`
8. 執行 `python3 scripts/generate-audio.py` 生成語音 mp3
9. 發送語音檔到 Telegram（用 message tool，asVoice）
10. Git commit + push
11. 回傳文字摘要供 Telegram 文字推送

### 手動觸發

```bash
openclaw cron run 71c85d19-ff69-409f-b03d-9d7bed7c8268
```

## 檔案結構

```
daily-world-news/
├── README.md              # 本文件 — 完整專案說明
├── SOURCES.md             # 新聞來源清單（按國家/地區分類，歡迎調整）
├── FORMAT.md              # 文字摘要格式規範
│                            - 格式 A：多元視角（按國家比較同一事件的報導角度）
│                            - 格式 B：標準格式（地區性新聞）
│                            - 去重複規則、來源要求、整體結構
├── PODCAST_PROMPT.md      # Podcast 播報稿風格指引
│                            - 口語化、主持人風格
│                            - 新聞融合成主題段落
│                            - 多元視角用敘事方式帶出
│                            - 3000-5000 字 → 8-15 分鐘語音
├── scripts/
│   └── generate-audio.py  # TTS 語音生成腳本
│                            - 使用 edge-tts (zh-TW-HsiaoChenNeural)
│                            - 自動分段 + ffmpeg 合併
│                            - 依賴：pip install edge-tts, apt install ffmpeg
│                            - 環境變數：VOICE（語音）、RATE（語速，預設 +10%）
└── summaries/             # 每日產出
    ├── YYYY-MM-DD.md          # 文字摘要
    ├── YYYY-MM-DD-podcast.md  # Podcast 播報稿
    └── YYYY-MM-DD.mp3         # 語音檔
```

## 設計原則

### 新聞品質
- **質 > 量**：15-20 則精選，不追求數量
- **去重複**：同一事件合併為一則，整合多方觀點
- **多元視角**：重大國際事件（3-5 則）按國家比較報導角度，不用「東方/西方」分組
- **附來源**：每則新聞附原始連結，不編造

### Podcast 風格
- 不是念稿，是主持人在跟聽眾聊天
- 新聞融合成 5-8 個主題段落，有邏輯串連
- 多元視角用自然敘事帶出差異
- 有開場、串場、結尾

## 如何調整

所有規則都在 markdown 檔案中，修改後下次執行自動生效：

| 想調整... | 編輯哪個檔案 |
|-----------|-------------|
| 新聞來源 | `SOURCES.md` |
| 文字摘要格式、新聞數量 | `FORMAT.md` |
| Podcast 風格、長度 | `PODCAST_PROMPT.md` |
| 語音（聲音、語速） | `scripts/generate-audio.py` 或設環境變數 |
| 排程時間 | `openclaw cron edit <id> --cron "..." --tz "..."` |

## 從零開始重建

如果 cron job 遺失，用以下指令重建：

```bash
# 安裝依賴
pip install edge-tts
apt install ffmpeg

# 建立 cron job（記得替換 Telegram channel ID）
openclaw cron add \
  --name "daily-world-news" \
  --cron "0 23 * * *" \
  --tz "UTC" \
  --session isolated \
  --model sonnet \
  --thinking low \
  --timeout-seconds 600 \
  --announce \
  --channel telegram \
  --to "<TELEGRAM_CHANNEL_ID>" \
  --message '參考 README.md 的「執行流程」章節'
```

完整的 cron message prompt 請參考 `openclaw cron list` 現有設定，或根據本 README 的執行流程重寫。

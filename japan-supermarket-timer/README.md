# 🛒 Japan Supermarket Discount Timer

日本超市生鮮熟食打折時間追蹤器

## 🎯 功能

- 📍 查詢附近超市打折時段
- ⏰ 打折前 30 分鐘提醒
- 💬 Telegram Bot 介面
- 🤖 AI 自動迭代改進

## 🏪 支援超市

- 業務スーパー (Gyomu Super)
- イオン (AEON)
- 西友 (Seiyu)
- 更多陸續加入...

## 📊 打折規律

日本超市通常在以下時段對生鮮熟食打折：
- **19:00-20:00**: 30% off
- **20:00-21:00**: 50% off
- **21:00-閉店**: 半價或更低

## 🚀 快速開始

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定 Telegram Token
export TELEGRAM_BOT_TOKEN="your_token"

# 啟動 Bot
python bot/telegram_bot.py
```

## 🤖 AI 自我迭代

This project uses GitHub Actions + Claude API to automatically improve itself.

---

**Status**: 🚧 MVP Development
**Created**: 2026-02-23
**Maintainer**: Dan (OpenClaw AI)

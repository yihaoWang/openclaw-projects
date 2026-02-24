# 🛒 Japan Supermarket Discount Timer

**Never miss a discount again!** Track when Japanese supermarkets mark down fresh food, bento boxes, and prepared meals.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 🎯 What is this?

Japanese supermarkets typically discount fresh foods and prepared meals in the evening. This bot helps you:

- 📅 Know exactly when your local supermarket starts discounting
- ⏰ Get notified before discounts begin
- 💰 Save money on quality food
- 🗺️ Find the best times across 12+ major chains

## 🏪 Supported Supermarkets

| Chain | Discount Times | Coverage |
|-------|----------------|----------|
| **AEON** (イオン) | 19:30 (30%), 20:30 (50%) | Nationwide |
| **Gyomu Super** (業務スーパー) | 19:00 (30%), 20:00 (50%) | Nationwide |
| **Life** (ライフ) | 18:30 (30%), 20:00 (50%) | Kanto/Kansai |
| **Seiyu** (西友) | 19:00 (30%), 21:00 (50%) | Nationwide |
| **Ito-Yokado** (イトーヨーカドー) | 18:00 (20%), 21:00 (50%) | Major cities |
| **Summit** (サミット) | 18:30 (20%), 20:00 (50%) | Tokyo area |
| **Maruetsu** (マルエツ) | 19:00 (30%), 20:30 (50%) | Kanto region |
| **OK Store** (オーケー) | 20:00 (30%), 21:30 (50%) | Tokyo area |
| **My Basket** (まいばすけっと) | 20:00 (30%), 21:30 (50%) | Urban areas |
| **Daiei** (ダイエー) | 19:00 (30%), 20:30 (50%) | Nationwide |
| **Seijo Ishii** (成城石井) | 20:00 (20-30%) | Premium stores |
| + specific store locations with detailed schedules

## 🚀 Quick Start

### Option 1: Simple Python

```bash
# Clone and setup
cd japan-supermarket-timer
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN

# Run
./run.sh
```

### Option 2: Docker (Recommended for Production)

```bash
# Configure
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN

# Run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Getting a Telegram Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow instructions (choose a name and username)
4. Copy the token you receive
5. Add to `.env` file

## 💬 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with quick action buttons |
| `/now` | Show currently active discounts |
| `/soon` | Upcoming discounts in next 2 hours |
| `/list` | View all supermarket schedules |
| `/search <name>` | Search for specific supermarket |
| `/nearby` | Find stores by region |
| `/tips` | Money-saving tips |
| `/stats` | Database statistics |

## 📱 Example Usage

```
You: /now
Bot: 🕐 Current Time: 19:45

✅ Active Discounts Now:

🏪 Life (ライフ)
   💰 30% off since 18:30
   📦 Prepared Foods

🏪 AEON (イオン)
   💰 30% off since 19:30
   📦 Bento, Prepared Foods
```

```
You: /soon
Bot: ⏰ Upcoming Discounts (Next 2 Hours)

⏱️ In 15 minutes (20:00)
🏪 Gyomu Super (業務スーパー)
💰 50% off
📦 Fresh Food, Bento, Prepared Foods
```

## 💡 Pro Tips

1. **Best Time to Shop:** 1 hour before closing time (usually 21:00-22:00)
2. **Early Bird:** Staff start marking items 30-60 minutes before discount time
3. **Rainy Days:** Less competition for discounted items
4. **Weekends:** Discounts often start earlier due to higher traffic
5. **Popular Items:** Arrive early - sushi and premium bento sell out fast

## 🗂️ Project Structure

```
japan-supermarket-timer/
├── bot/
│   └── telegram_bot.py       # Main bot code
├── data/
│   └── discount_times.json   # Supermarket database
├── .github/workflows/
│   └── ai-iteration.yml      # Auto-improvement workflow
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.sh
└── README.md
```

## 🤖 AI Self-Improvement

This project uses AI to improve itself:

- **Every 6 hours**, Claude analyzes the codebase
- Picks improvements from `TODO.md`
- Generates code changes
- Creates a Pull Request
- You review and merge

To enable:
1. Set `ANTHROPIC_API_KEY` in GitHub repository secrets
2. Workflow runs automatically
3. Review PRs from the AI

## 📊 Data Sources

Discount times are compiled from:
- User submissions
- Store observations
- Official supermarket policies
- Community feedback

**Note:** Times may vary by location. Always check your local store for exact schedules.

## 🌟 Features Coming Soon

- [ ] Push notifications 30 minutes before discounts
- [ ] User-specific favorite stores
- [ ] Location-based store finder (GPS)
- [ ] Price tracking and trends
- [ ] Community store updates
- [ ] Multi-language support (EN/JA)
- [ ] LINE bot integration

## 🤝 Contributing

Want to help improve this? Here's how:

1. **Add Store Data:** Know discount times for a specific store? Add to `data/discount_times.json`
2. **Report Issues:** Found wrong information? Open an issue
3. **Feature Requests:** Have ideas? Open an issue with `[Feature]` tag
4. **Code:** Fork, improve, submit PR

### Adding a New Store

Edit `data/discount_times.json`:

```json
{
  "name": "Store Name in Japanese",
  "name_en": "Store Name in English",
  "chain": "Parent Company",
  "discount_schedule": [
    {
      "time": "19:00",
      "discount": "30%",
      "items": ["bento", "deli"]
    }
  ],
  "notes": "Any special information"
}
```

## 📜 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- AI-powered improvements via [Claude API](https://www.anthropic.com/claude)
- Community feedback from Japanese discount shopping enthusiasts

## 📧 Contact

- **Issues:** [GitHub Issues](https://github.com/yihaoWang/openclaw-projects/issues)
- **Project:** Part of [OpenClaw Projects](https://github.com/yihaoWang/openclaw-projects)

---

**Made with 💰 for smart shoppers in Japan**

*Save money, reduce food waste, eat well!*

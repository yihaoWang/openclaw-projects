#!/bin/bash

set -e

echo "🤖 Japan Supermarket Discount Timer"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📋 Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  Please edit .env and add your TELEGRAM_BOT_TOKEN"
    echo "📖 Get token from @BotFather on Telegram"
    exit 1
fi

# Source environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if token is set
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" == "your_bot_token_here" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not configured in .env"
    echo "📖 Get token from @BotFather on Telegram"
    exit 1
fi

echo "✅ Configuration loaded"
echo "🚀 Starting bot..."
echo ""

# Run bot
python bot/telegram_bot.py

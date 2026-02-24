#!/bin/bash

set -e

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <GITHUB_TOKEN> <TELEGRAM_TOKEN> <CLAUDE_API_KEY>"
    echo ""
    echo "Example:"
    echo "  $0 github_pat_xxx 123456:ABCdef... sk-ant-xxx"
    exit 1
fi

GITHUB_TOKEN=$1
TELEGRAM_TOKEN=$2
CLAUDE_API_KEY=$3

echo "🚀 Quick Deploy Script"
echo "======================"
echo ""

# 1. Push to GitHub
echo "📤 Pushing to GitHub..."
git remote set-url origin https://x-access-token:${GITHUB_TOKEN}@github.com/yihaoWang/japan-supermarket-timer.git
git push -u origin main

# 2. Set GitHub Secrets (requires gh CLI)
if command -v gh &> /dev/null; then
    echo "🔐 Setting GitHub secrets..."
    echo -n "$CLAUDE_API_KEY" | gh secret set ANTHROPIC_API_KEY
    echo "✅ Secrets configured"
else
    echo "⚠️  'gh' CLI not found. Please set ANTHROPIC_API_KEY manually in GitHub Settings."
fi

# 3. Install dependencies and start bot
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🤖 To start the Telegram bot:"
echo "   export TELEGRAM_BOT_TOKEN='${TELEGRAM_TOKEN}'"
echo "   python bot/telegram_bot.py"
echo ""
echo "📱 GitHub repo: https://github.com/yihaoWang/japan-supermarket-timer"
echo "🔄 AI will auto-improve every 6 hours"

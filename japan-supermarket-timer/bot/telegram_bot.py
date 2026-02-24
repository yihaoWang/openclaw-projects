#!/usr/bin/env python3
"""
Japan Supermarket Discount Timer - Telegram Bot
"""

import os
import json
from datetime import datetime, time
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load discount data
DATA_FILE = Path(__file__).parent.parent / "data" / "discount_times.json"

def load_discount_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

DATA = load_discount_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    welcome = """
🛒 **日本超市打折時間追蹤器**

我可以幫你：
• `/list` - 查看所有超市打折時段
• `/when <超市名>` - 查詢特定超市
• `/now` - 現在有哪些超市在打折
• `/tips` - 省錢小貼士

生鮮熟食打折攻略，幫你省錢！💰
"""
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def list_supermarkets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all supermarkets and their discount schedules"""
    message = "🏪 **超市打折時段一覽**\n\n"
    
    for market in DATA['supermarkets']:
        message += f"**{market['name']} ({market['name_en']})**\n"
        for schedule in market['discount_schedule']:
            items = '、'.join(schedule['items'])
            message += f"  • {schedule['time']} - {schedule['discount']} ({items})\n"
        if 'notes' in market:
            message += f"  _{market['notes']}_\n"
        message += "\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def when_discount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Query discount time for specific supermarket"""
    if not context.args:
        await update.message.reply_text(
            "請輸入超市名稱，例如：\n`/when 業務スーパー`",
            parse_mode='Markdown'
        )
        return
    
    query = ' '.join(context.args)
    
    for market in DATA['supermarkets']:
        if query.lower() in market['name'].lower() or query.lower() in market['name_en'].lower():
            message = f"**{market['name']} ({market['name_en']})**\n\n"
            for schedule in market['discount_schedule']:
                items = '、'.join(schedule['items'])
                message += f"⏰ **{schedule['time']}** - {schedule['discount']}\n"
                message += f"   適用：{items}\n\n"
            if 'notes' in market:
                message += f"💡 _{market['notes']}_"
            await update.message.reply_text(message, parse_mode='Markdown')
            return
    
    await update.message.reply_text(f"找不到「{query}」，試試 /list 查看所有超市")

async def now_discounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show which supermarkets are discounting now"""
    now = datetime.now().time()
    
    active_discounts = []
    upcoming_discounts = []
    
    for market in DATA['supermarkets']:
        for schedule in market['discount_schedule']:
            discount_time = datetime.strptime(schedule['time'], '%H:%M').time()
            
            # Check if discount is active (within 3 hours window)
            if now >= discount_time and now.hour < discount_time.hour + 3:
                active_discounts.append({
                    'market': market['name'],
                    'time': schedule['time'],
                    'discount': schedule['discount']
                })
            # Check if upcoming (within 1 hour)
            elif now.hour == discount_time.hour - 1 or (now.hour == discount_time.hour and now.minute < discount_time.minute):
                upcoming_discounts.append({
                    'market': market['name'],
                    'time': schedule['time'],
                    'discount': schedule['discount']
                })
    
    message = f"🕐 **現在時間：{now.strftime('%H:%M')}**\n\n"
    
    if active_discounts:
        message += "✅ **進行中的折扣：**\n"
        for d in active_discounts:
            message += f"  • {d['market']} - {d['discount']} (從 {d['time']} 開始)\n"
        message += "\n"
    
    if upcoming_discounts:
        message += "⏳ **即將開始：**\n"
        for d in upcoming_discounts:
            message += f"  • {d['market']} - {d['discount']} ({d['time']})\n"
        message += "\n"
    
    if not active_discounts and not upcoming_discounts:
        message += "目前沒有折扣進行中或即將開始\n"
        message += "試試 /list 查看所有時段"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show money-saving tips"""
    message = "💡 **省錢小貼士**\n\n"
    for i, tip in enumerate(DATA['general_tips'], 1):
        message += f"{i}. {tip}\n"
    
    await update.message.reply_text(message)

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set")
        print("Please set it: export TELEGRAM_BOT_TOKEN='your_token'")
        return
    
    # Create application
    app = Application.builder().token(token).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_supermarkets))
    app.add_handler(CommandHandler("when", when_discount))
    app.add_handler(CommandHandler("now", now_discounts))
    app.add_handler(CommandHandler("tips", tips))
    
    print("🤖 Bot starting...")
    print("📱 Commands: /start /list /when /now /tips")
    
    # Start polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

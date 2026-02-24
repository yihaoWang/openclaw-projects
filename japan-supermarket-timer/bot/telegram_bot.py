#!/usr/bin/env python3
"""
Japan Supermarket Discount Timer - Telegram Bot
Track discount times for Japanese supermarkets
"""

import os
import json
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import List, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from reminders import ReminderSystem, cmd_remind, cmd_remind_off, cmd_remind_status

# Load discount data
DATA_FILE = Path(__file__).parent.parent / "data" / "discount_times.json"

def load_discount_data() -> Dict[str, Any]:
    """Load supermarket discount data from JSON file"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

DATA = load_discount_data()

def get_item_name(item_key: str, lang: str = 'en') -> str:
    """Get localized item name"""
    categories = DATA.get('item_categories', {})
    if item_key in categories:
        return categories[item_key].get(lang, item_key)
    return item_key

def format_discount_schedule(market: Dict[str, Any], lang: str = 'en') -> str:
    """Format discount schedule for display"""
    lines = []
    for schedule in market['discount_schedule']:
        items = ', '.join([get_item_name(item, lang) for item in schedule['items']])
        emoji = "🟡" if "30" in schedule['discount'] else "🔴"
        lines.append(f"  {emoji} **{schedule['time']}** - {schedule['discount']} off")
        lines.append(f"     _({items})_")
    return '\n'.join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with quick action buttons"""
    welcome = """
🛒 **Japan Supermarket Discount Timer**

Never miss a discount again! I track when Japanese supermarkets mark down fresh food, bento, and prepared meals.

💡 **Quick Commands:**
• `/list` - View all supermarket schedules
• `/now` - What's on discount right now?
• `/soon` - Upcoming discounts (next 2 hours)
• `/search <name>` - Find specific supermarket
• `/nearby` - Find stores by region
• `/remind` - Enable discount notifications 🔔
• `/tips` - Money-saving tips
• `/stats` - Database statistics

🎯 **Pro tip:** Most supermarkets start discounting around 19:00-20:00, with deeper discounts closer to closing time!
"""
    
    keyboard = [
        [
            InlineKeyboardButton("🕐 What's On Now?", callback_data="now"),
            InlineKeyboardButton("⏰ Coming Soon", callback_data="soon")
        ],
        [
            InlineKeyboardButton("📋 All Stores", callback_data="list"),
            InlineKeyboardButton("💡 Tips", callback_data="tips")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome, parse_mode='Markdown', reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "now":
        await show_current_discounts(query, context)
    elif query.data == "soon":
        await show_upcoming_discounts(query, context)
    elif query.data == "list":
        await show_all_supermarkets(query, context)
    elif query.data == "tips":
        await show_tips(query, context)

async def show_current_discounts(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    """Show currently active discounts"""
    now = datetime.now().time()
    current_hour = now.hour
    current_minute = now.minute
    
    active_discounts = []
    
    for market in DATA['supermarkets']:
        for schedule in market['discount_schedule']:
            discount_time = datetime.strptime(schedule['time'], '%H:%M').time()
            
            # Check if discount is active (within 3 hours window or until closing)
            time_diff_hours = current_hour - discount_time.hour
            time_diff_minutes = current_minute - discount_time.minute
            
            if time_diff_hours >= 0 and time_diff_hours < 3:
                active_discounts.append({
                    'market': market['name_en'],
                    'market_ja': market['name'],
                    'time': schedule['time'],
                    'discount': schedule['discount'],
                    'items': [get_item_name(item) for item in schedule['items']]
                })
    
    message = f"🕐 **Current Time:** {now.strftime('%H:%M')}\n\n"
    
    if active_discounts:
        message += "✅ **Active Discounts Now:**\n\n"
        for d in active_discounts:
            items_str = ', '.join(d['items'])
            message += f"🏪 **{d['market']}** ({d['market_ja']})\n"
            message += f"   💰 {d['discount']} off since {d['time']}\n"
            message += f"   📦 {items_str}\n\n"
    else:
        message += "😔 **No active discounts right now**\n\n"
        message += "Try `/soon` to see what's coming up!\n"
        message += "Or check `/list` for full schedules."
    
    if hasattr(update_or_query, 'message'):
        await update_or_query.message.reply_text(message, parse_mode='Markdown')
    else:
        await update_or_query.edit_message_text(message, parse_mode='Markdown')

async def show_upcoming_discounts(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    """Show upcoming discounts in next 2 hours"""
    now = datetime.now()
    current_time = now.time()
    two_hours_later = (now + timedelta(hours=2)).time()
    
    upcoming = []
    
    for market in DATA['supermarkets']:
        for schedule in market['discount_schedule']:
            discount_time = datetime.strptime(schedule['time'], '%H:%M').time()
            
            # Check if discount starts within next 2 hours
            if current_time < discount_time <= two_hours_later:
                time_until = datetime.combine(datetime.today(), discount_time) - datetime.combine(datetime.today(), current_time)
                minutes_until = int(time_until.total_seconds() / 60)
                
                upcoming.append({
                    'market': market['name_en'],
                    'market_ja': market['name'],
                    'time': schedule['time'],
                    'discount': schedule['discount'],
                    'minutes_until': minutes_until,
                    'items': [get_item_name(item) for item in schedule['items']]
                })
    
    upcoming.sort(key=lambda x: x['minutes_until'])
    
    message = f"⏰ **Upcoming Discounts** (Next 2 Hours)\n"
    message += f"📅 Current time: {now.strftime('%H:%M')}\n\n"
    
    if upcoming:
        for d in upcoming:
            items_str = ', '.join(d['items'])
            message += f"⏱️ **In {d['minutes_until']} minutes** ({d['time']})\n"
            message += f"🏪 {d['market']} ({d['market_ja']})\n"
            message += f"💰 {d['discount']} off\n"
            message += f"📦 {items_str}\n\n"
    else:
        message += "🤷 No discounts starting in the next 2 hours.\n\n"
        message += "Check `/now` for current discounts or `/list` for full schedules."
    
    if hasattr(update_or_query, 'message'):
        await update_or_query.message.reply_text(message, parse_mode='Markdown')
    else:
        await update_or_query.edit_message_text(message, parse_mode='Markdown')

async def show_all_supermarkets(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    """List all supermarkets and their discount schedules"""
    message = "🏪 **All Supermarket Discount Schedules**\n\n"
    
    for market in DATA['supermarkets']:
        chain_info = f" ({market['chain']})" if 'chain' in market else ""
        message += f"**{market['name_en']}** ({market['name']}){chain_info}\n"
        message += format_discount_schedule(market)
        if 'notes' in market:
            message += f"\n  💡 _{market['notes']}_"
        if 'address' in market:
            message += f"\n  📍 {market['address']}"
        message += "\n\n"
    
    # Split into multiple messages if too long
    if len(message) > 4000:
        parts = message.split('\n\n')
        current_msg = "🏪 **All Supermarket Discount Schedules**\n\n"
        
        for part in parts[1:]:  # Skip first empty split
            if len(current_msg) + len(part) > 4000:
                if hasattr(update_or_query, 'message'):
                    await update_or_query.message.reply_text(current_msg, parse_mode='Markdown')
                else:
                    await update_or_query.edit_message_text(current_msg, parse_mode='Markdown')
                    update_or_query = update_or_query.message  # Switch to message for subsequent sends
                current_msg = part + "\n\n"
            else:
                current_msg += part + "\n\n"
        
        if current_msg:
            if hasattr(update_or_query, 'message'):
                await update_or_query.message.reply_text(current_msg, parse_mode='Markdown')
            else:
                await update_or_query.message.reply_text(current_msg, parse_mode='Markdown')
    else:
        if hasattr(update_or_query, 'message'):
            await update_or_query.message.reply_text(message, parse_mode='Markdown')
        else:
            await update_or_query.edit_message_text(message, parse_mode='Markdown')

async def list_supermarkets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command handler for /list"""
    await show_all_supermarkets(update, context)

async def now_discounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command handler for /now"""
    await show_current_discounts(update, context)

async def soon_discounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command handler for /soon"""
    await show_upcoming_discounts(update, context)

async def search_supermarket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for specific supermarket"""
    if not context.args:
        await update.message.reply_text(
            "🔍 **Search for a supermarket:**\n\n"
            "Usage: `/search <name>`\n\n"
            "Examples:\n"
            "• `/search Life`\n"
            "• `/search AEON`\n"
            "• `/search 業務`",
            parse_mode='Markdown'
        )
        return
    
    query = ' '.join(context.args).lower()
    results = []
    
    for market in DATA['supermarkets']:
        if (query in market['name'].lower() or 
            query in market['name_en'].lower() or
            ('chain' in market and query in market['chain'].lower())):
            results.append(market)
    
    if not results:
        await update.message.reply_text(
            f"❌ No supermarkets found matching '{query}'\n\n"
            "Try `/list` to see all available stores."
        )
        return
    
    message = f"🔍 **Search Results for '{query}':**\n\n"
    
    for market in results:
        chain_info = f" ({market['chain']})" if 'chain' in market else ""
        message += f"**{market['name_en']}** ({market['name']}){chain_info}\n"
        message += format_discount_schedule(market)
        if 'notes' in market:
            message += f"\n  💡 _{market['notes']}_"
        if 'address' in market:
            message += f"\n  📍 {market['address']}"
        message += "\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def nearby_stores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show stores by region"""
    regions = DATA.get('regions', {})
    
    message = "📍 **Supermarkets by Region:**\n\n"
    
    for region, chains in regions.items():
        message += f"**{region.upper()}:**\n"
        message += "  • " + "\n  • ".join(chains) + "\n\n"
    
    message += "\n💡 Use `/search <store name>` to see specific schedules!"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def show_tips(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    """Show money-saving tips"""
    message = "💡 **Money-Saving Tips:**\n\n"
    
    for i, tip in enumerate(DATA['general_tips'], 1):
        tip_text = tip['en'] if isinstance(tip, dict) else tip
        message += f"{i}. {tip_text}\n\n"
    
    message += "\n🎯 **Best Strategy:**\n"
    message += "Arrive 30-45 minutes before your target discount time. "
    message += "Staff often start marking items early, and popular items sell fast!"
    
    if hasattr(update_or_query, 'message'):
        await update_or_query.message.reply_text(message, parse_mode='Markdown')
    else:
        await update_or_query.edit_message_text(message, parse_mode='Markdown')

async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command handler for /tips"""
    await show_tips(update, context)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show database statistics"""
    total_stores = len(DATA['supermarkets'])
    chains = set()
    specific_stores = 0
    
    for market in DATA['supermarkets']:
        if 'chain' in market:
            chains.add(market['chain'])
        if 'address' in market:
            specific_stores += 1
    
    message = f"📊 **Database Statistics:**\n\n"
    message += f"🏪 Total Supermarkets: **{total_stores}**\n"
    message += f"🏢 Unique Chains: **{len(chains)}**\n"
    message += f"📍 Specific Locations: **{specific_stores}**\n"
    message += f"💡 Tips Available: **{len(DATA['general_tips'])}**\n\n"
    message += f"**Chains in Database:**\n"
    message += "  • " + "\n  • ".join(sorted(chains)) + "\n\n"
    message += f"_Last updated: {datetime.now().strftime('%Y-%m-%d')}_"
    
    await update.message.reply_text(message, parse_mode='Markdown')

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set")
        print("Please set it: export TELEGRAM_BOT_TOKEN='your_token'")
        print("\n📖 To get a token:")
        print("1. Message @BotFather on Telegram")
        print("2. Send /newbot")
        print("3. Follow instructions")
        return
    
    # Create application
    app = Application.builder().token(token).build()
    
    # Initialize reminder system
    reminder_system = ReminderSystem(app.bot)
    app.bot_data['reminder_system'] = reminder_system
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_supermarkets))
    app.add_handler(CommandHandler("now", now_discounts))
    app.add_handler(CommandHandler("soon", soon_discounts))
    app.add_handler(CommandHandler("search", search_supermarket))
    app.add_handler(CommandHandler("nearby", nearby_stores))
    app.add_handler(CommandHandler("tips", tips))
    app.add_handler(CommandHandler("stats", stats))
    
    # Reminder commands
    app.add_handler(CommandHandler("remind", cmd_remind))
    app.add_handler(CommandHandler("remind_off", cmd_remind_off))
    app.add_handler(CommandHandler("remind_status", cmd_remind_status))
    
    # Add callback query handler for buttons
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Japan Supermarket Discount Timer Bot")
    print("=" * 50)
    print(f"✅ Bot starting with {len(DATA['supermarkets'])} supermarkets...")
    print(f"📱 Commands: /start /list /now /soon /search /nearby /tips /stats")
    print(f"🔔 Reminder commands: /remind /remind_off /remind_status")
    print(f"⏰ Tracking discounts for major Japanese supermarket chains")
    print("=" * 50)
    
    # Start reminder system in background
    import asyncio
    asyncio.create_task(reminder_system.run_reminder_loop())
    
    # Start polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Reminder system for Japan Supermarket Discount Timer
Notifies users before discounts begin
"""

import json
import asyncio
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import List, Dict, Set
from telegram import Bot

# User preferences storage
PREFS_FILE = Path(__file__).parent.parent / "data" / "user_preferences.json"
DATA_FILE = Path(__file__).parent.parent / "data" / "discount_times.json"

class ReminderSystem:
    """Manage discount reminders for users"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.user_prefs = self.load_preferences()
        self.discount_data = self.load_discount_data()
    
    def load_preferences(self) -> Dict:
        """Load user preferences"""
        if PREFS_FILE.exists():
            with open(PREFS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"users": {}}
    
    def save_preferences(self):
        """Save user preferences"""
        PREFS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PREFS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.user_prefs, f, indent=2, ensure_ascii=False)
    
    def load_discount_data(self) -> Dict:
        """Load supermarket discount data"""
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def subscribe_user(self, user_id: int, supermarket: str = None, 
                       minutes_before: int = 30) -> bool:
        """
        Subscribe user to reminders
        
        Args:
            user_id: Telegram user ID
            supermarket: Specific supermarket (None for all)
            minutes_before: Minutes before discount to notify
        
        Returns:
            True if subscribed successfully
        """
        user_id_str = str(user_id)
        
        if user_id_str not in self.user_prefs["users"]:
            self.user_prefs["users"][user_id_str] = {
                "subscribed": True,
                "favorites": [],
                "minutes_before": minutes_before,
                "active": True
            }
        
        user_pref = self.user_prefs["users"][user_id_str]
        user_pref["active"] = True
        user_pref["minutes_before"] = minutes_before
        
        # Maintain backwards compatibility
        if "supermarkets" in user_pref and "favorites" not in user_pref:
            user_pref["favorites"] = user_pref.pop("supermarkets")
        elif "favorites" not in user_pref:
            user_pref["favorites"] = []
        
        if supermarket and supermarket not in user_pref["favorites"]:
            user_pref["favorites"].append(supermarket)
        
        self.save_preferences()
        return True
    
    def add_favorite(self, user_id: int, store_name: str) -> tuple[bool, str]:
        """
        Add a favorite store for the user
        
        Returns:
            (success, message)
        """
        user_id_str = str(user_id)
        
        # Find matching store
        matching_stores = []
        for market in self.discount_data['supermarkets']:
            if (store_name.lower() in market['name'].lower() or 
                store_name.lower() in market['name_en'].lower()):
                matching_stores.append(market['name_en'])
        
        if not matching_stores:
            return False, f"❌ No store found matching '{store_name}'"
        
        if len(matching_stores) > 1:
            stores_list = "\n  • ".join(matching_stores)
            return False, f"🤔 Multiple stores found:\n  • {stores_list}\n\nPlease be more specific!"
        
        store = matching_stores[0]
        
        # Initialize user if needed
        if user_id_str not in self.user_prefs["users"]:
            self.user_prefs["users"][user_id_str] = {
                "subscribed": False,
                "favorites": [],
                "minutes_before": 30,
                "active": False
            }
        
        user_pref = self.user_prefs["users"][user_id_str]
        if "favorites" not in user_pref:
            user_pref["favorites"] = []
        
        if store in user_pref["favorites"]:
            return False, f"ℹ️ **{store}** is already in your favorites"
        
        user_pref["favorites"].append(store)
        self.save_preferences()
        
        return True, f"✅ Added **{store}** to favorites!"
    
    def remove_favorite(self, user_id: int, store_name: str) -> tuple[bool, str]:
        """
        Remove a favorite store
        
        Returns:
            (success, message)
        """
        user_id_str = str(user_id)
        
        if user_id_str not in self.user_prefs["users"]:
            return False, "❌ You don't have any favorites yet"
        
        user_pref = self.user_prefs["users"][user_id_str]
        favorites = user_pref.get("favorites", [])
        
        # Find matching favorite
        matching = [f for f in favorites if store_name.lower() in f.lower()]
        
        if not matching:
            return False, f"❌ '{store_name}' not in your favorites"
        
        if len(matching) > 1:
            stores_list = "\n  • ".join(matching)
            return False, f"🤔 Multiple matches:\n  • {stores_list}\n\nPlease be more specific!"
        
        store = matching[0]
        user_pref["favorites"].remove(store)
        self.save_preferences()
        
        return True, f"✅ Removed **{store}** from favorites"
    
    def get_favorites(self, user_id: int) -> List[str]:
        """Get user's favorite stores"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.user_prefs["users"]:
            return []
        
        return self.user_prefs["users"][user_id_str].get("favorites", [])
    
    def unsubscribe_user(self, user_id: int) -> bool:
        """Unsubscribe user from all reminders"""
        user_id_str = str(user_id)
        
        if user_id_str in self.user_prefs["users"]:
            self.user_prefs["users"][user_id_str]["active"] = False
            self.save_preferences()
            return True
        
        return False
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """Get user's reminder preferences"""
        user_id_str = str(user_id)
        return self.user_prefs["users"].get(user_id_str, None)
    
    async def check_and_send_reminders(self):
        """Check for upcoming discounts and send reminders"""
        now = datetime.now()
        
        for user_id, prefs in self.user_prefs["users"].items():
            if not prefs.get("active", False):
                continue
            
            minutes_before = prefs.get("minutes_before", 30)
            target_time = (now + timedelta(minutes=minutes_before)).time()
            
            # Find matching discounts
            favorites = prefs.get("favorites", prefs.get("supermarkets", []))
            upcoming = self.find_upcoming_discounts(target_time, favorites)
            
            if upcoming:
                await self.send_reminder(int(user_id), upcoming, minutes_before)
    
    def find_upcoming_discounts(self, target_time: time, 
                                favorites: List[str]) -> List[Dict]:
        """Find discounts starting at target time"""
        matching = []
        
        for market in self.discount_data['supermarkets']:
            # Filter by user's favorite stores if any
            if favorites and market['name_en'] not in favorites:
                continue
            
            for schedule in market['discount_schedule']:
                discount_time = datetime.strptime(schedule['time'], '%H:%M').time()
                
                # Check if discount time matches (within 5 minutes)
                time_diff = abs(
                    (discount_time.hour * 60 + discount_time.minute) -
                    (target_time.hour * 60 + target_time.minute)
                )
                
                if time_diff <= 5:
                    matching.append({
                        'market': market['name_en'],
                        'market_ja': market['name'],
                        'time': schedule['time'],
                        'discount': schedule['discount'],
                        'items': schedule['items']
                    })
        
        return matching
    
    async def send_reminder(self, user_id: int, discounts: List[Dict], 
                           minutes_before: int):
        """Send reminder message to user"""
        message = f"🔔 **Discount Alert!**\n\n"
        message += f"⏰ Discounts starting in **{minutes_before} minutes**:\n\n"
        
        for d in discounts:
            items = ', '.join(self.get_item_names(d['items']))
            message += f"🏪 **{d['market']}** ({d['market_ja']})\n"
            message += f"💰 {d['discount']} off at {d['time']}\n"
            message += f"📦 {items}\n\n"
        
        message += "🏃 Head to the store now to get the best selection!"
        
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Failed to send reminder to {user_id}: {e}")
    
    def get_item_names(self, items: List[str]) -> List[str]:
        """Get English names for items"""
        categories = self.discount_data.get('item_categories', {})
        return [
            categories.get(item, {}).get('en', item)
            for item in items
        ]
    
    async def run_reminder_loop(self):
        """Main reminder loop - check every minute"""
        print("🔔 Reminder system started")
        print(f"📊 Monitoring {len(self.user_prefs['users'])} users")
        
        while True:
            try:
                await self.check_and_send_reminders()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error in reminder loop: {e}")
                await asyncio.sleep(60)

# Telegram bot command handlers for reminders

async def cmd_remind(update, context):
    """Enable reminders for this user"""
    user_id = update.effective_user.id
    
    # Parse arguments
    minutes_before = 30
    if context.args and context.args[0].isdigit():
        minutes_before = int(context.args[0])
        if minutes_before < 5 or minutes_before > 120:
            await update.message.reply_text(
                "⚠️ Minutes must be between 5 and 120"
            )
            return
    
    # Subscribe user
    reminder_system = context.bot_data.get('reminder_system')
    if reminder_system:
        reminder_system.subscribe_user(user_id, minutes_before=minutes_before)
        
        message = f"✅ **Reminders Enabled!**\n\n"
        message += f"🔔 You'll be notified **{minutes_before} minutes** before discounts start\n\n"
        message += "💡 **Customize:**\n"
        message += "• `/remind 15` - Notify 15 min before\n"
        message += "• `/remind 45` - Notify 45 min before\n"
        message += "• `/remind_off` - Disable reminders\n\n"
        message += "_Coming soon: Choose specific supermarkets_"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            "❌ Reminder system not available"
        )

async def cmd_remind_off(update, context):
    """Disable reminders"""
    user_id = update.effective_user.id
    
    reminder_system = context.bot_data.get('reminder_system')
    if reminder_system:
        reminder_system.unsubscribe_user(user_id)
        
        message = "🔕 **Reminders Disabled**\n\n"
        message += "You won't receive discount notifications.\n\n"
        message += "Use `/remind` to enable again."
        
        await update.message.reply_text(message, parse_mode='Markdown')

async def cmd_remind_status(update, context):
    """Show reminder status"""
    user_id = update.effective_user.id
    
    reminder_system = context.bot_data.get('reminder_system')
    if not reminder_system:
        await update.message.reply_text("❌ Reminder system not available")
        return
    
    prefs = reminder_system.get_user_preferences(user_id)
    
    if not prefs or not prefs.get('active'):
        message = "🔕 **Reminders: OFF**\n\n"
        message += "Use `/remind` to enable notifications"
    else:
        minutes = prefs.get('minutes_before', 30)
        favorites = prefs.get('favorites', prefs.get('supermarkets', []))
        
        message = f"🔔 **Reminders: ON**\n\n"
        message += f"⏰ Notify **{minutes} minutes** before discounts\n"
        
        if favorites:
            message += f"\n⭐ **Favorite Stores:**\n"
            message += "  • " + "\n  • ".join(favorites)
        else:
            message += "\n🌍 Watching **all supermarkets**"
            message += "\n\n💡 Use `/favorite add <store>` to add favorites"
        
        message += "\n\n💡 Use `/remind_off` to disable"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def cmd_favorite(update, context):
    """Manage favorite stores"""
    reminder_system = context.bot_data.get('reminder_system')
    if not reminder_system:
        await update.message.reply_text("❌ Reminder system not available")
        return
    
    user_id = update.effective_user.id
    
    if not context.args:
        # Show help
        favorites = reminder_system.get_favorites(user_id)
        
        message = "⭐ **Favorite Stores**\n\n"
        
        if favorites:
            message += "**Your Favorites:**\n"
            message += "  • " + "\n  • ".join(favorites) + "\n\n"
        else:
            message += "_You haven't added any favorites yet._\n\n"
        
        message += "**Commands:**\n"
        message += "• `/favorite add <store>` - Add a favorite\n"
        message += "• `/favorite remove <store>` - Remove a favorite\n"
        message += "• `/favorite list` - Show this help\n\n"
        message += "**Examples:**\n"
        message += "• `/favorite add Life`\n"
        message += "• `/favorite add AEON`\n"
        message += "• `/favorite remove Life`\n\n"
        message += "💡 When you have favorites, reminders only notify you about those stores!"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        return
    
    action = context.args[0].lower()
    
    if action == "list":
        # Show favorites
        favorites = reminder_system.get_favorites(user_id)
        
        if not favorites:
            message = "⭐ **No favorites yet!**\n\n"
            message += "Add with: `/favorite add <store name>`"
        else:
            message = "⭐ **Your Favorite Stores:**\n\n"
            message += "  • " + "\n  • ".join(favorites) + "\n\n"
            message += f"Total: {len(favorites)} stores"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    elif action == "add":
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Please specify a store name\n\n"
                "Example: `/favorite add Life`",
                parse_mode='Markdown'
            )
            return
        
        store_name = ' '.join(context.args[1:])
        success, msg = reminder_system.add_favorite(user_id, store_name)
        
        if success:
            msg += "\n\n💡 Enable reminders with `/remind` to get notified!"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    elif action == "remove":
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Please specify a store name\n\n"
                "Example: `/favorite remove Life`",
                parse_mode='Markdown'
            )
            return
        
        store_name = ' '.join(context.args[1:])
        success, msg = reminder_system.remove_favorite(user_id, store_name)
        
        await update.message.reply_text(msg, parse_mode='Markdown')
    
    else:
        await update.message.reply_text(
            "❌ Unknown action. Use:\n"
            "• `/favorite add <store>`\n"
            "• `/favorite remove <store>`\n"
            "• `/favorite list`"
        )

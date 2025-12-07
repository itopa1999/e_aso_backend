"""
Telegram notification subscription handler.
Manages user subscriptions for notifications via Telegram.
Uses existing telegram_user_chat_id field in User model.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram_bot.utils import check_authentication
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys
from apps.users.models import User


async def handle_notification_subscription(query, user_id: int):
    """
    Show notification subscription options menu.
    Requires user to be logged in.
    """
    token, headers = await check_authentication(query, user_id)
    if not token:
        return
    
    keyboard = [
        [InlineKeyboardButton("✅ Subscribe to Notifications", callback_data="warn_sub_notification")],
        [InlineKeyboardButton("❌ Unsubscribe from Notifications", callback_data="warn_unsub_notification")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.answer()
    await query.message.reply_text(
        text="<b>🔔 Notification Management</b>\n\n"
             "Choose an option:\n\n"
             "• <b>Subscribe</b> - Enable notifications\n"
             "• <b>Unsubscribe</b> - Disable notifications",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def handle_warn_subscribe(query, user_id: int):
    """
    Show warning dialog before subscribing to notifications.
    """
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Subscribe", callback_data="confirm_sub_notification")],
        [InlineKeyboardButton("❌ Cancel", callback_data="notification_subscription_cancel")]
    ]
    
    await query.answer()
    await query.message.reply_text(
        text="<b>⚠️ Warning - Enable Notifications</b>\n\n"
             "You are about to <b>ENABLE</b> notifications.\n\n"
             "You will start receiving:\n"
             "• Order status updates\n"
             "<b>Are you sure you want to proceed?</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def handle_warn_unsubscribe(query, user_id: int):
    """
    Show warning dialog before unsubscribing from notifications.
    """
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Unsubscribe", callback_data="confirm_unsub_notification")],
        [InlineKeyboardButton("❌ Cancel", callback_data="notification_subscription_cancel")]
    ]
    
    await query.answer()
    await query.message.reply_text(
        text="<b>⚠️ Warning - Disable Notifications</b>\n\n"
             "You are about to <b>DISABLE</b> notifications.\n\n"
             "You will NO LONGER receive:\n"
             "• Order status updates\n"
             "<b>Are you sure you want to proceed?</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def handle_confirm_subscribe(query, user_id: int):
    """
    Confirm and process subscription to notifications.
    """
    try:
        # Get or create user
        user, created = User.objects.get_or_create(
            telegram_id=user_id,
            defaults={
                'email': f'telegram_{user_id}@example.com',
                'first_name': f'Telegram User',
                'last_name': f'{user_id}'
            }
        )
        
        # Store telegram chat ID if not already stored
        if not user.telegram_user_chat_id:
            user.telegram_user_chat_id = str(user_id)
            user.save(update_fields=['telegram_user_chat_id'])
        
        # Mark subscription in cache
        sub_key = CacheKeys.format(CacheKeys.telegram_user_subscription, user_id=user_id, notif_type='all')
        GlobalCache.set(sub_key, True, timeout=60*60*24*30)  # 30 days
        
        keyboard = [
            [InlineKeyboardButton("🔔 Back to Notifications", callback_data="notification_subscription")],
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")]
        ]
        
        await query.answer()
        await query.message.reply_text(
            text="<b>✅ Success!</b>\n\n"
                 "Notifications have been <b>ENABLED</b>.\n\n"
                 f"<b>Your Chat ID:</b> <code>{user.telegram_user_chat_id}</code>\n\n"
                 "You will now receive all notifications.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await query.answer()
        await query.message.reply_text(
            text=f"❌ <b>Error</b>\n\n{str(e)}",
            parse_mode="HTML"
        )


async def handle_confirm_unsubscribe(query, user_id: int):
    """
    Confirm and process unsubscription from notifications.
    """
    try:
        # Mark unsubscription in cache
        sub_key = CacheKeys.format(CacheKeys.telegram_user_subscription, user_id=user_id, notif_type='all')
        GlobalCache.set(sub_key, False, timeout=60*60*24*30)  # 30 days
        
        keyboard = [
            [InlineKeyboardButton("🔔 Back to Notifications", callback_data="notification_subscription")],
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")]
        ]
        
        await query.answer()
        await query.message.reply_text(
            text="<b>✅ Success!</b>\n\n"
                 "Notifications have been <b>DISABLED</b>.\n\n"
                 "You will no longer receive any notifications.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await query.answer()
        await query.message.reply_text(
            text=f"❌ <b>Error</b>\n\n{str(e)}",
            parse_mode="HTML"
        )


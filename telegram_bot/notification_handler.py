"""
Telegram notification subscription handler.
Manages user subscriptions for notifications via Telegram.
Uses telegram_user_chat_id and telegram_notifications_enabled fields in User model.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram_bot.utils import check_authentication
from apps.users.models import User
from asgiref.sync import sync_to_async
import requests
from .config import USER_URL


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
    Calls the telegram notification API endpoint.
    """
    try:
        # Get token from cache to authenticate the request
        token, headers = await check_authentication(query, user_id)
        if not token:
            await query.answer()
            await query.message.reply_text(
                text="❌ <b>Error</b>\n\nYou must be logged in to enable notifications.",
                parse_mode="HTML"
            )
            return
        
        # Call the telegram notification endpoint
        response = await sync_to_async(requests.post)(
            f"{USER_URL}/telegram-notification/",
            json={
                "action": "activate",
                "telegram_user_id": user_id
            },
            headers=headers
        )
        
        if response.status_code == 200:
            try:
                result = response.json()
                data = result.get('data', {})
                
                keyboard = [
                    [InlineKeyboardButton("🔔 Back to Notifications", callback_data="notification_subscription")],
                    [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")]
                ]
                
                await query.answer()
                await query.message.reply_text(
                    text="<b>✅ Success!</b>\n\n"
                         "Notifications have been <b>ENABLED</b>.\n\n"
                         f"<b>Your Chat ID:</b> <code>{data.get('telegram_user_chat_id')}</code>\n\n"
                         "You will now receive all notifications.",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="HTML"
                )
            except Exception as json_error:
                await query.answer()
                await query.message.reply_text(
                    text=f"❌ <b>Error</b>\n\nFailed to parse response: {str(json_error)}",
                    parse_mode="HTML"
                )
        else:
            try:
                error_msg = response.json().get('message', 'Failed to enable notifications')
            except:
                error_msg = f"Server error: {response.status_code} - {response.text[:100] if response.text else 'No response'}"
            
            await query.answer()
            await query.message.reply_text(
                text=f"❌ <b>Error</b>\n\n{error_msg}",
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
    Calls the telegram notification API endpoint.
    """
    try:
        # Get token from cache to authenticate the request
        token, headers = await check_authentication(query, user_id)
        if not token:
            await query.answer()
            await query.message.reply_text(
                text="❌ <b>Error</b>\n\nYou must be logged in to disable notifications.",
                parse_mode="HTML"
            )
            return
        
        # Call the telegram notification endpoint
        response = await sync_to_async(requests.post)(
            f"{USER_URL}/telegram-notification/",
            json={
                "action": "deactivate"
            },
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            try:
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
            except Exception as json_error:
                await query.answer()
                await query.message.reply_text(
                    text=f"❌ <b>Error</b>\n\nFailed to process response: {str(json_error)}",
                    parse_mode="HTML"
                )
        else:
            try:
                error_msg = response.json().get('message', 'Failed to disable notifications')
            except:
                error_msg = f"Server error: {response.status_code} - {response.text[:100] if response.text else 'No response'}"
            
            await query.answer()
            await query.message.reply_text(
                text=f"❌ <b>Error</b>\n\n{error_msg}",
                parse_mode="HTML"
            )
        
    except Exception as e:
        await query.answer()
        await query.message.reply_text(
            text=f"❌ <b>Error</b>\n\n{str(e)}",
            parse_mode="HTML"
        )


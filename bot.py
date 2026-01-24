import os
import django

# ==========================
# Django setup
# ==========================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import BotCommand
from telegram.constants import BotCommandScopeType
from telegram_bot.config import BOT_TOKEN, TELEGRAM_CHANNEL_ID
from telegram_bot.handlers import handle_state_selection, start, echo, button_handler, cancel, handle_logout
from telegram_bot.login_handler import handle_login
from telegram_bot.help_handler import handle_help
from telegram_bot.channel_handler import handle_channel_message, handle_new_channel_member
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


# ==========================
# Help Command Handler
# ==========================
async def help_command(update, context):
    """Handle /help command from menu."""
    # Create a mock query object for the help handler
    class MockQuery:
        def __init__(self, message):
            self.message = message
    
    mock_query = MockQuery(update.message)
    await handle_help(mock_query)


# ==========================
# Dynamic Commands Manager
# ==========================
async def update_user_commands(app, user_id, is_logged_in):
    """
    Update bot commands based on user authentication status.
    """
    try:
        if is_logged_in:
            # Show logout and hide login
            commands = [
                BotCommand("start", "🏠 Show main menu"),
                BotCommand("logout", "🚪 Logout from account"),
                BotCommand("help", "ℹ️ Get help"),
                BotCommand("cancel", "❌ Cancel current operation"),
            ]
        else:
            # Show login and hide logout
            commands = [
                BotCommand("start", "🏠 Show main menu"),
                BotCommand("login", "🔐 Login to account"),
                BotCommand("help", "ℹ️ Get help"),
                BotCommand("cancel", "❌ Cancel current operation"),
            ]
        
        # Set commands for this specific user
        from telegram import BotCommandScopeChat
        scope = BotCommandScopeChat(chat_id=user_id)
        await app.bot.set_my_commands(commands, scope=scope)
    except Exception as e:
        print(f"Error updating commands for user {user_id}: {e}")


# ==========================
# Cancel Command Handler
# ==========================
async def cancel_command(update, context):
    """Handle /cancel command from menu."""
    await cancel(update, context)


# ==========================
# Login Command Handler
# ==========================
async def login_command(update, context):
    """Handle /login command from menu."""
    user_id = update.message.from_user.id
    # Create a mock query object for the login handler
    class MockQuery:
        def __init__(self, message):
            self.message = message
    
    mock_query = MockQuery(update.message)
    await handle_login(mock_query, user_id)


# ==========================
# Logout Command Handler
# ==========================
async def logout_command(update, context):
    """Handle /logout command from menu."""
    user_id = update.message.from_user.id
    # Create a mock query object for the logout handler
    class MockQuery:
        def __init__(self, message):
            self.message = message
        
        async def answer(self):
            pass
    
    mock_query = MockQuery(update.message)
    await handle_logout(mock_query, user_id, context)


# ==========================
# Main
# ==========================
def main():
    """
    Initialize and run the Telegram bot application.
    """
    print(f"Starting bot with channel ID: {TELEGRAM_CHANNEL_ID}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Set up commands menu button
    async def setup_menu(app):
        """Setup the bot commands menu with default (logged out) state."""
        commands = [
            BotCommand("start", "🏠 Show main menu"),
            BotCommand("login", "🔐 Login to account"),
            BotCommand("help", "ℹ️ Get help"),
            BotCommand("cancel", "❌ Cancel current operation"),
        ]
        await app.bot.set_my_commands(commands)
    
    # Run setup before polling
    app.post_init = setup_menu
    
    # Handle commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login_command))
    app.add_handler(CommandHandler("logout", logout_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    
    # Handle button callbacks
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Handle new members joining channel/group
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        handle_new_channel_member
    ), group=0)
    
    # Handle channel posts (messages sent to channels come as channel_post)
    app.add_handler(MessageHandler(
        filters.UpdateType.CHANNEL_POST & filters.TEXT & ~filters.COMMAND,
        handle_channel_message
    ), group=0)
    
    # Handle group/supergroup messages
    app.add_handler(MessageHandler(
        (filters.Chat(chat_id=TELEGRAM_CHANNEL_ID) | filters.ChatType.SUPERGROUP) & filters.TEXT & ~filters.COMMAND,
        handle_channel_message
    ), group=0)
    
    # Handle regular private messages (lower priority)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, echo), group=1)
    
    print("Bot started successfully! Listening for messages...")
    app.run_polling()


if __name__ == "__main__":
    main()

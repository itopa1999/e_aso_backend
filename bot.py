import os
import django

# ==========================
# Django setup
# ==========================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram_bot.config import BOT_TOKEN, TELEGRAM_CHANNEL_ID
from telegram_bot.handlers import handle_state_selection, start, echo, button_handler
from telegram_bot.channel_handler import handle_channel_message, handle_new_channel_member



# ==========================
# Main
# ==========================
def main():
    """
    Initialize and run the Telegram bot application.
    """
    print(f"Starting bot with channel ID: {TELEGRAM_CHANNEL_ID}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handle commands
    app.add_handler(CommandHandler("start", start))
    
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

import os
import django

# ==========================
# Django setup
# ==========================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram_bot.config import BOT_TOKEN
from telegram_bot.handlers import start, echo, button_handler



# ==========================
# Main
# ==========================
def main():
    """
    Initialize and run the Telegram bot application.
    """
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling()


if __name__ == "__main__":
    main()

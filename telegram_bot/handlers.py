"""
Main handlers module that consolidates all telegram bot handlers.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys

from .login_handler import handle_login, handle_email_input, handle_code_input
from .products_handler import handle_list_products, handle_product_details
from .categories_handler import handle_list_categories, handle_category_products
from .orders_handler import handle_list_orders, handle_order_details
from .help_handler import handle_help


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command - shows main menu.
    """
    keyboard = [
        [InlineKeyboardButton("🛍️ List Products", callback_data="list_products_1")],
        [InlineKeyboardButton("📂 List Categories", callback_data="list_categories")],
        [InlineKeyboardButton("📦 My Orders", callback_data="list_orders")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
        [InlineKeyboardButton("🔐 Login", callback_data="login")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 <b>Welcome!</b>\nPlease select an option:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle text messages - processes login flow or shows menu.
    """
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    stage_key = CacheKeys.format(CacheKeys.telegram_user_login_stage, user_id=user_id)
    stage = GlobalCache.get(stage_key)

    if stage == "awaiting_email":
        await handle_email_input(update, user_id, text)
        return

    if stage == "awaiting_code":
        await handle_code_input(update, user_id, text)
        return

    # If not in login flow, show menu
    await start(update, context)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle all button callbacks - routes to appropriate handler.
    """
    query = update.callback_query
    await query.answer()
    choice = query.data
    user_id = query.from_user.id

    # Login Handler
    if choice == "login":
        await handle_login(query, user_id)

    # Products Handlers
    elif choice.startswith("list_products"):
        page = choice.split("_")[2] if len(choice.split("_")) > 2 else "1"
        await handle_list_products(query, page)

    elif choice.startswith("details_"):
        product_id = choice.split("_")[1]
        await handle_product_details(query, product_id)

    # Categories Handlers
    elif choice == "list_categories":
        await handle_list_categories(query)

    elif choice.startswith("category_"):
        parts = choice.split("_")
        category_name = parts[1]
        page = parts[2] if len(parts) > 2 else "1"
        await handle_category_products(query, category_name, page)

    # Orders Handlers
    elif choice == "list_orders":
        await handle_list_orders(query, user_id)

    elif choice.startswith("order_details"):
        order_id = choice.split("_")[2]
        await handle_order_details(query, user_id, order_id)

    # Help Handler
    elif choice == "help":
        await handle_help(query)

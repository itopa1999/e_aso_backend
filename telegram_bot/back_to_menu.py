from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup



async def handle_back_to_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("🛍️ List Products", callback_data="list_products_1")],
        [InlineKeyboardButton("📂 List Categories", callback_data="list_categories")],
        [InlineKeyboardButton("🔍 Search Products", callback_data="search_products")],
        [InlineKeyboardButton("📦 My Orders", callback_data="list_orders")],
        [InlineKeyboardButton("🔔 Notifications", callback_data="notification_subscription")],
        [InlineKeyboardButton("📝 Contact / Special Request", callback_data="contact_request")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
        [InlineKeyboardButton("🔐 Logout", callback_data="logout")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please select an option:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

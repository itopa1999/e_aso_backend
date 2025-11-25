"""
Main handlers module that consolidates all telegram bot handlers.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram_bot.utils import NIGERIAN_STATES
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys

from .login_handler import handle_login, handle_email_input, handle_code_input
from .products_handler import handle_list_products, handle_product_details
from .categories_handler import handle_list_categories, handle_category_products
from .orders_handler import handle_list_orders, handle_order_details
from .help_handler import handle_help
from .item_order_handler import confirm_order_handler, handle_proceed_payment, item_order_handler
from .contact_handler import handle_contact_request, handle_contact_input, handle_submit_contact, handle_cancel_contact
from .channel_handler import handle_new_channel_member
from .search_handler import handle_search_products, handle_search_input


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command - shows main menu.
    """
    keyboard = [
        [InlineKeyboardButton("🛍️ List Products", callback_data="list_products_1")],
        [InlineKeyboardButton("📂 List Categories", callback_data="list_categories")],
        [InlineKeyboardButton("🔍 Search Products", callback_data="search_products")],
        [InlineKeyboardButton("📦 My Orders", callback_data="list_orders")],
        [InlineKeyboardButton("📝 Contact / Special Request", callback_data="contact_request")],
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
    
    if text.lower().startswith("/cancel") or text.lower() == "cancel":
        print(f"User {user_id} cancelled the operation.")
        await cancel(update, context)
        return

    # Check login stage
    stage_key = CacheKeys.format(CacheKeys.telegram_user_login_stage, user_id=user_id)
    stage = GlobalCache.get(stage_key)
    if stage in ["awaiting_email", "awaiting_code"]:
        if stage == "awaiting_email":
            await handle_email_input(update, user_id, text)
        else:
            await handle_code_input(update, user_id, text)
        return

    # Check shipping stage
    shipping_stage_key = CacheKeys.format(CacheKeys.telegram_user_shipping_stage, user_id=user_id)
    shipping_stage = GlobalCache.get(shipping_stage_key)
    if shipping_stage:
        await handle_shipping_info(update, context)
        return

    # Check contact stage
    contact_handled = await handle_contact_input(update, user_id, text)
    if contact_handled:
        return

    # Check search stage
    search_handled = await handle_search_input(update, user_id, text)
    if search_handled:
        return

    # If not in any flow, show menu
    await start(update, context)
    
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        user_id = update.callback_query.from_user.id
        await update.callback_query.answer("Operation cancelled.")
        await update.callback_query.message.reply_text(
            "❌ Operation cancelled. Returning to main menu."
        )
    else:
        user_id = update.message.from_user.id
        await update.message.reply_text(
            "❌ Operation cancelled. Returning to main menu."
        )
    
    
    
    # Clear all Telegram flow-related cache
    GlobalCache.set(CacheKeys.format(CacheKeys.telegram_user_login_stage, user_id=user_id), None)
    GlobalCache.set(CacheKeys.format(CacheKeys.telegram_user_shipping_stage, user_id=user_id), None)
    GlobalCache.set(CacheKeys.format(CacheKeys.telegram_user_shipping_info, user_id=user_id), None)
    GlobalCache.set(CacheKeys.format(CacheKeys.telegram_user_contact_stage, user_id=user_id), None)
    GlobalCache.set(CacheKeys.format(CacheKeys.telegram_user_contact_info, user_id=user_id), None)
    GlobalCache.set(CacheKeys.format(CacheKeys.telegram_user_search_stage, user_id=user_id), None)
    
    await start(update, context)
    
    
async def handle_shipping_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    stage_key = CacheKeys.format(CacheKeys.telegram_user_shipping_stage, user_id=user_id)
    shipping_key = CacheKeys.format(CacheKeys.telegram_user_shipping_info, user_id=user_id)
    
    stage = GlobalCache.get(stage_key)
    shipping_info = GlobalCache.get(shipping_key) or {}

    if not stage:
        return  # Not in shipping flow

    # Step-by-step collection
    if stage == "first_name":
        shipping_info["first_name"] = text
        GlobalCache.set(shipping_key, shipping_info)
        GlobalCache.set(stage_key, "last_name")
        await update.message.reply_text("Enter your last name:")
    
    elif stage == "last_name":
        shipping_info["last_name"] = text
        GlobalCache.set(shipping_key, shipping_info)
        GlobalCache.set(stage_key, "address")
        await update.message.reply_text("Enter your address:")
    
    elif stage == "address":
        shipping_info["address"] = text
        GlobalCache.set(shipping_key, shipping_info)
        GlobalCache.set(stage_key, "city")
        await update.message.reply_text("Enter your city:")
    
    elif stage == "city":
        shipping_info["city"] = text
        GlobalCache.set(shipping_key, shipping_info)
        GlobalCache.set(stage_key, "state")
        # Show states as buttons
        buttons = [[InlineKeyboardButton(s, callback_data=f"state_{s}")] for s in NIGERIAN_STATES]
        await update.message.reply_text("Select your state:", reply_markup=InlineKeyboardMarkup(buttons))
    
    elif stage == "phone":
        shipping_info["phone"] = text
        GlobalCache.set(shipping_key, shipping_info)
        GlobalCache.set(stage_key, "alt_phone")
        await update.message.reply_text("Enter your alternative phone (or leave blank):")
    
    elif stage == "alt_phone":
        shipping_info["alt_phone"] = text
        GlobalCache.set(shipping_key, shipping_info)
        GlobalCache.set(stage_key, "other_info")
        await update.message.reply_text("Other info (optional):")
    
    elif stage == "other_info":
        shipping_info["otherInfo"] = text
        GlobalCache.set(shipping_key, shipping_info)
        GlobalCache.set(stage_key, "confirm")

        # Build HTML list
        html_text = "<b>✅ Shipping info collected:</b>\n\n"
        html_text += f"• <b>Product ID:</b> {shipping_info.get('product_id')}\n"
        html_text += f"• <b>First Name:</b> {shipping_info.get('first_name')}\n"
        html_text += f"• <b>Last Name:</b> {shipping_info.get('last_name')}\n"
        html_text += f"• <b>Address:</b> {shipping_info.get('address')}\n"
        html_text += f"• <b>City:</b> {shipping_info.get('city')}\n"
        html_text += f"• <b>State:</b> {shipping_info.get('state')}\n"
        html_text += f"• <b>Phone:</b> {shipping_info.get('phone')}\n"
        html_text += f"• <b>Alt Phone:</b> {shipping_info.get('alt_phone')}\n"
        html_text += f"• <b>Other Info:</b> {shipping_info.get('otherInfo')}\n"

        # Add confirm button
        buttons = [[InlineKeyboardButton("✅ Confirm Order", callback_data="confirm_order")]]
        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(html_text, parse_mode="HTML", reply_markup=reply_markup)
        
        
async def handle_state_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    state = query.data.split("_", 1)[1]  # safer split
    shipping_key = CacheKeys.format(CacheKeys.telegram_user_shipping_info, user_id=user_id)
    shipping_info = GlobalCache.get(shipping_key) or {}
    shipping_info["state"] = state
    GlobalCache.set(shipping_key, shipping_info)

    stage_key = CacheKeys.format(CacheKeys.telegram_user_shipping_stage, user_id=user_id)
    GlobalCache.set(stage_key, "phone")

    await query.message.reply_text("✅ State selected: <b>{}</b>\nEnter your phone number:".format(state),
                                   parse_mode="HTML")





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
        
    # orders Handlers
    elif choice.startswith("place_order"):
        product_id = choice.split("_")[2]
        await item_order_handler(query, user_id, product_id)
        
    elif choice.startswith("start_shipping_"):
        product_id = choice.split("_")[2]
        stage_key = CacheKeys.format(CacheKeys.telegram_user_shipping_stage, user_id=user_id)
        GlobalCache.set(stage_key, "first_name")
        await query.message.reply_text("Please enter your first name:")
        
    elif choice == "confirm_order" or choice.startswith("confirm_order"):
        await confirm_order_handler(query, user_id)
        
    elif choice == "proceed_payment" or choice.startswith("proceed_payment"):
        await handle_proceed_payment(query, user_id)
    
    elif choice == "search_products" or choice.startswith("search_products"):
        await handle_search_products(query, user_id)
        
    # -----------------------
    # State selection
    # -----------------------
    if choice.startswith("state_"):
        await handle_state_selection(update, context)
        return


    # Contact Handlers
    elif choice == "contact_request":
        await handle_contact_request(query, user_id)
    
    elif choice == "submit_contact":
        await handle_submit_contact(query, user_id)
    
    elif choice == "cancel_contact":
        await handle_cancel_contact(query, user_id)

    # Help Handler
    elif choice == "help":
        await handle_help(query)

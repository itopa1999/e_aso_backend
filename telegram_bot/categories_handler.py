import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .config import ASO_URL
from .utils import send_product_photo


async def handle_list_categories(query):
    """
    Handle list categories button press.
    """
    resp = requests.get(f"{ASO_URL}/lookups/")
    data = resp.json()
    
    for c in data:
        cat_name = c.get("name", "No name")
        text = f"• <b>{cat_name}</b>"
        buttons = [[InlineKeyboardButton("📂 View Products", callback_data=f"category_{cat_name}_1")]]
        await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))


async def handle_category_products(query, category_name, page="1"):
    """
    Handle category products view with pagination.
    """
    resp = requests.get(f"{ASO_URL}/", params={"category": category_name, "page": page})
    data = resp.json()
    text = f"<b>🛍️ Products in {category_name} - Page {page}:</b>\n\n"

    for p in data.get("results", []):
        title = p.get("title", "No title")
        price = p.get("current_price", "N/A")
        badge = f" [{p['badge']}]" if p.get("badge") else ""
        description = p.get("short_description", "")
        text += f"• <b>{title}</b>{badge} - <i>₦{price}</i>\n{description}\n\n"

        buttons = [
            [InlineKeyboardButton("🛒 Order Now", callback_data=f"order_{p['id']}"),
             InlineKeyboardButton("ℹ️ See Details", callback_data=f"details_{p['id']}")]
        ]
        await send_product_photo(query, p, text, buttons)
        text = ""

    # Pagination buttons
    pagination_buttons = []
    if data.get("previous"):
        prev_page = data["previous"].split("page=")[-1]
        pagination_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"category_{category_name}_{prev_page}"))
    if data.get("next"):
        next_page = data["next"].split("page=")[-1]
        pagination_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"category_{category_name}_{next_page}"))
    if pagination_buttons:
        await query.message.reply_text("Navigate pages:", reply_markup=InlineKeyboardMarkup([pagination_buttons]))

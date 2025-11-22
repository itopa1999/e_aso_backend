import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .config import ASO_URL
from .utils import send_product_photo


async def handle_list_products(query, page="1"):
    """
    Handle list products button press with pagination.
    """
    resp = requests.get(f"{ASO_URL}/", params={"page": page})
    data = resp.json()
    text = f"<b>🛍️ Products - Page {page}:</b>\n\n"

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
        pagination_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"list_products_{prev_page}"))
    if data.get("next"):
        next_page = data["next"].split("page=")[-1]
        pagination_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"list_products_{next_page}"))
    if pagination_buttons:
        await query.message.reply_text("Navigate pages:", reply_markup=InlineKeyboardMarkup([pagination_buttons]))


async def handle_product_details(query, product_id):
    """
    Handle product details view.
    """
    resp = requests.get(f"{ASO_URL}/{product_id}/")
    product = resp.json()

    product_number = product.get("product_number", "")
    title = product.get("title", "No title")
    badge = f" [{product['badge']}]" if product.get("badge") else ""
    price = product.get("current_price", "N/A")
    original_price = product.get("original_price", "N/A")
    discount = product.get("discount_percent")
    rating = product.get("rating", "N/A")
    reviews_count = product.get("reviews_count", 0)
    description = product.get("description", "")

    categories = ", ".join([c.get("name", "") for c in product.get("category", [])])
    colors = ", ".join([c.get("color_name", "") for c in product.get("colors", [])])
    sizes = ", ".join([s.get("size_label", "") for s in product.get("sizes", [])])
    details_text = "".join([f"<b>{d.get('title', '')}:</b> {d.get('content', '')}\n" for d in product.get("details", [])])

    text = f"""
<b>🛍️ {title}{badge}</b>
<i>Product Number:</i> {product_number}
<i>Price:</i> ₦{price} (Original: ₦{original_price}) {"[" + str(discount) + "% off]" if discount else ""}
<i>Rating:</i> {rating} ⭐ ({reviews_count} reviews)
<i>Categories:</i> {categories}
<i>Colors:</i> {colors}
<i>Sizes:</i> {sizes}

<b>Description:</b>
{description}

{details_text}
    """
    buttons = [[InlineKeyboardButton("🛒 Order Now", callback_data=f"order_{product_id}")]]
    await send_product_photo(query, product, text, buttons)

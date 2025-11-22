import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from .config import ASO_URL
from .utils import check_authentication, handle_auth_error
from asgiref.sync import sync_to_async

async def handle_list_orders(query, user_id):
    """
    Handle list orders button press.
    """
    token, headers = await check_authentication(query, user_id)
    if not token:
        return
    
    try:
        resp = await sync_to_async(requests.get)(f"{ASO_URL}/lists/", headers=headers)
    except Exception as e:
        await query.message.reply_text("❌ Server error. Try again later.")
        return

    # Handle bad token or expired JWT
    if resp.status_code in [401, 403]:
        await handle_auth_error(query, user_id)
        return
    
    if resp.status_code != 200:
        await query.message.reply_text("❌ Failed to fetch orders.")
        return
    
    data = resp.json()
    orders = data.get("data", [])

    if not orders:
        await query.message.reply_text("📭 You have no orders yet.")
        return

    # Send each order separately with a button
    for o in orders:
        order_id = o.get("id")
        order_number = o.get("order_number", "")
        status = o.get("order_status", "unknown").capitalize()
        created = o.get("created_at", "")
        subtotal = o.get("subtotal", "0")
        shipping = o.get("shipping", "0")
        discount = o.get("discount", "0")
        total = o.get("total", "0")

        # Format date
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            nice_date = dt.strftime("%b %d, %Y")
        except:
            nice_date = created

        text = f"""
<b>📦 Order — {order_number}</b>
<b>Status:</b> {status}
<b>Date:</b> {nice_date}

<b>💰 Summary</b>
• <b>Subtotal:</b> ₦{subtotal}
• <b>Shipping:</b> ₦{shipping}
• <b>Discount:</b> ₦{discount}
• <b>Total:</b> <b>₦{total}</b>
        """

        # Button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 View Details", callback_data=f"order_details_{order_id}")]
        ])

        await query.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)


async def handle_order_details(query, user_id, order_id):
    """
    Handle order details view.
    """
    token, headers = await check_authentication(query, user_id)
    if not token:
        return
    
    try:
        resp = await sync_to_async(requests.get)(f"{ASO_URL}/order-details/{order_id}/", headers=headers)
    except Exception as e:
        await query.message.reply_text("❌ Server error. Try again later.")
        return

    # Handle bad token or expired JWT
    if resp.status_code in [401, 403]:
        await handle_auth_error(query, user_id)
        return
    
    if resp.status_code != 200:
        await query.message.reply_text("❌ Failed to fetch order details.")
        return
    
    order = resp.json().get("data", {})

    # Format dates
    def format_date(date_str):
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%b %d, %Y")
        except:
            return date_str

    created_at = format_date(order.get("created_at", ""))
    estimated_delivery = format_date(order.get("estimated_delivery_date", ""))

    # Order summary
    subtotal = order.get("subtotal", "0")
    shipping_fee = order.get("shipping_fee", "0")
    discount = order.get("discount", "0")
    total = order.get("total", "0")
    order_status = order.get("order_status", "unknown").capitalize()
    tracking_number = order.get("tracking_number", "N/A")
    carrier = order.get("carrier", "N/A")
    other_info = order.get("other_info", "")

    # Shipping address
    ship = order.get("shipping_address", {})
    full_name = ship.get("full_name", "")
    address = ship.get("address", "")
    apartment = ship.get("apartment", "")
    city = ship.get("city", "")
    state = ship.get("state", "")
    phone = ship.get("phone", "")
    alt_phone = ship.get("alt_phone", "")

    # Payment
    payment = order.get("payment_detail", {})
    payment_method = payment.get("method", "N/A")

    # Items
    items = order.get("items", [])
    items_text = ""
    for item in items:
        name = item.get("product_name", "No title")
        qty = item.get("quantity", 1)
        price = item.get("price", "0")
        items_text += f"• <b>{name}</b>\n  Quantity: {qty}\n  Price: ₦{price}\n\n"

    # Tracking history
    tracking = order.get("tracking", [])
    tracking_text = ""
    for t in tracking:
        t_status = t.get("status", "")
        t_date = format_date(t.get("date", ""))
        t_desc = t.get("description", "")
        completed = t.get("completed", False)
        checkmark = "✅" if completed else "⏳"
        tracking_text += f"{checkmark} <b>{t_status.capitalize()}</b> - {t_date}\n{t_desc}\n\n"

    text = f"""
<b>📦 Order Details — {order.get("order_number", "")}</b>

<b>Status:</b> {order_status}
<b>Created:</b> {created_at}
<b>Estimated Delivery:</b> {estimated_delivery}
<b>Tracking Number:</b> {tracking_number}
<b>Carrier:</b> {carrier}
<b>Other Info:</b> {other_info}

<b>💰 Payment Summary</b>
• Subtotal: ₦{subtotal}
• Shipping Fee: ₦{shipping_fee}
• Discount: ₦{discount}
• Total: <b>₦{total}</b>
• Payment Method: {payment_method}

<b>🏠 Shipping Address</b>
{full_name}
{address} {apartment}
{city}, {state}
Phone: {phone} | Alt: {alt_phone}

<b>🛍️ Items</b>
{items_text}

<b>📋 Tracking History</b>
{tracking_text}
    """

    await query.message.reply_text(text, parse_mode="HTML")

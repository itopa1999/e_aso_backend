import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from apps.aso.models import CartItem, Product
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys
from .config import ASO_URL
from .utils import check_authentication, handle_auth_error
from apps.users.models import User

async def item_order_handler(query, user_id, product_id):
    """
    Handle item order button press.
    """
    token, headers = await check_authentication(query, user_id)
    if not token:
        return
    
    # Start shipping info collection
    shipping_key = CacheKeys.format(CacheKeys.telegram_user_shipping_info, user_id=user_id)
    GlobalCache.set(shipping_key, {"product_id": product_id})
    
    info_text = (
        "📝 We will collect the following shipping information step by step:\n\n"
        "• First Name\n"
        "• Last Name\n"
        "• Address\n"
        "• City\n"
        "• State (choose from the list of Nigerian states)\n"
        "• Phone\n"
        "• Alternative Phone (optional)\n"
        "• Other Info (optional)\n"
        "Press ✅ Okay, proceed to start providing this info."
    )
    
    buttons = [[InlineKeyboardButton("✅ Okay, proceed", callback_data=f"start_shipping_{product_id}")]]
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.message.reply_text(info_text, reply_markup=reply_markup)

    

async def confirm_order_handler(query, user_id):
    token, headers = await check_authentication(query, user_id)
    if not token:
        return
    
    shipping_key = CacheKeys.format(CacheKeys.telegram_user_shipping_info, user_id=user_id)
    shipping_info = GlobalCache.get(shipping_key)
    if not shipping_info:
        await query.message.reply_text("❌ Shipping info not found. Please start again.")
        return
    
    from apps.aso.models import Cart

    try:
        email_key = CacheKeys.format(CacheKeys.telegram_user_login_codes, user_id=user_id)
        email = GlobalCache.get(email_key)
        
        print("Fetching cart for email:", email)
        
        user = await sync_to_async(User.objects.get)(email=email)
        # Use sync_to_async for ORM calls
        cart, _ = await sync_to_async(Cart.objects.get_or_create)(
            user=user,
            is_deleted=False
        )
        
        cart.state = shipping_info.get("state")
        await sync_to_async(cart.save)()

        await sync_to_async(cart.items.all().delete)()

        product_id = shipping_info.get("product_id")
        product = await sync_to_async(Product.objects.get)(id=product_id)
        await sync_to_async(CartItem.objects.create)(cart=cart, product=product, quantity=1)

        cart.state = shipping_info.get("state")
        await sync_to_async(cart.save)()

        subtotal = await sync_to_async(cart.subtotal)()
        discount = await sync_to_async(cart.discount)()
        shipping = await sync_to_async(cart.shipping_cost)()
        total_amount = await sync_to_async(cart.total)()
        quantity = 1

        shipping_info["total"] = str(total_amount)
        shipping_info["telegram_user_chat_id"] = str(user_id)
        GlobalCache.set(shipping_key, shipping_info)
        
        # Build HTML message
        html_text = "<b>✅ Order Summary:</b>\n\n"
        html_text += f"• <b>Product:</b> {product.title}\n"
        html_text += f"• <b>Subtotal:</b> ₦{subtotal}\n"
        html_text += f"• <b>Discount:</b> ₦{discount}\n"
        html_text += f"• <b>Shipping:</b> ₦{shipping}\n"
        html_text += f"• <b>Total:</b> ₦{total_amount}\n\n"
        html_text += f"• <b>Quantity:</b> {quantity}\n\n"
        html_text += "<i>Shipping info has been collected and applied.</i>"

        # Confirm button
        buttons = [[InlineKeyboardButton("✅ Proceed to Payment", callback_data="proceed_payment")]]
        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.reply_text(html_text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Cart.DoesNotExist as e:
        await query.message.reply_text(f"❌ Your cart is empty. Please start placing an order again. {e}",)
        return

async def handle_proceed_payment(query, user_id):
    token, headers = await check_authentication(query, user_id)
    if not token:
        return
    shipping_key = CacheKeys.format(CacheKeys.telegram_user_shipping_info, user_id=user_id)
    shipping_info = GlobalCache.get(shipping_key)
    if not shipping_info:
        await query.message.reply_text("❌ Shipping info not found. Please start again.")
        return
    
    try:
        resp = await sync_to_async(requests.post)(
            f"{ASO_URL}/place-orders/",
            headers=headers,
            json={"shipping_info": shipping_info}
        )
    except Exception:
        await query.message.reply_text("❌ Server error. Try again later.")
        return

    # Handle expired token
    if resp.status_code in [401, 403]:
        await handle_auth_error(query, user_id)
        return

    if resp.status_code != 200:
        await query.message.reply_text("❌ Failed to initialize order. Please try again.")
        return

    data = resp.json()
    checkout_url = data.get("data", {}).get("checkout_url")

    if not checkout_url:
        await query.message.reply_text("❌ Payment initialization failed. Please try again.")
        return

    # Create payment button
    keyboard = [
        [InlineKeyboardButton("💳 Proceed to Payment", url=checkout_url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        "✅ Order initialized successfully!\n\n"
        "Click the button below to complete your payment:",
        reply_markup=reply_markup
    )

    # Clear Redis keys
    GlobalCache.set(CacheKeys.format(CacheKeys.telegram_user_login_stage, user_id=user_id), None)
    GlobalCache.set(CacheKeys.format(CacheKeys.telegram_user_shipping_stage, user_id=user_id), None)
    GlobalCache.set(CacheKeys.format(CacheKeys.telegram_user_shipping_info, user_id=user_id), None)
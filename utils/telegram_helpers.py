import json
import mimetypes
from celery import shared_task
import requests
from django.conf import settings
import os
from apps.aso.models import Product
from utils.decorators import checkBackgroundFeatureFlag
# Config
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_CHANNEL_ID = settings.TELEGRAM_CHANNEL_ID
TELEGRAM_API_BASE_URL = settings.TELEGRAM_API_BASE_URL


def send_announcement(message: str) -> bool:
    """
    Send a simple announcement text to the Telegram channel.
    """
    url = f"{TELEGRAM_API_BASE_URL}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    return response.ok


@checkBackgroundFeatureFlag()
@shared_task
def send_notification(message: str, chat_id: str) -> bool:
    """
    Send a notification (like order updates) to Telegram channel.
    Can be reused for different types of notifications.
    """
    url = f"{TELEGRAM_API_BASE_URL}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    return response.ok



@checkBackgroundFeatureFlag()
@shared_task
def send_product(product_id: int) -> bool:
    """
    Send a product announcement to Telegram with image, details, price, and category.
    Defaults to logo.jpeg if no product image exists.
    """
    try:
        product = Product.objects.get(id=product_id, is_deleted=False, display_product=True)
    except Product.DoesNotExist:
        return False
    url = f"{TELEGRAM_API_BASE_URL}/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    link = f"{settings.BASE_URL}/product-info.html?id={product.id}"
    # Use product image or default logo
    image_path = None
    if product.main_image:
        file_type, _ = mimetypes.guess_type(product.main_image.path)
        if file_type and file_type.startswith("image"):
            image_path = product.main_image.path
    if not image_path:
        image_path = os.path.join(settings.BASE_DIR, "media", "logo.jpeg")

    categories = ", ".join([cat.name for cat in product.category.all()])
    badge_text = f"🏷️ {product.badge}" if product.badge else ""
    discount_text = f"💰 Price: ${product.current_price:.2f}" if product.current_price else f"💰 Price: ${product.original_price:.2f}"
    with open(image_path, "rb") as image_file:
        caption = f"""
        <b>{product.title}</b> {badge_text}

        {product.description}

        {discount_text}
        📦 Categories: {categories}

        """

        payload = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "caption": caption,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "📋 View Full Details", "callback_data": f"details_{product_id}"},
                            {"text": "🛒 Order Now", "callback_data": f"place_order_{product_id}"},
                        ]
                    ]
                }
            ),
        }
        files = {"photo": image_file}

        response = requests.post(url, data=payload, files=files)
        
        return response.ok
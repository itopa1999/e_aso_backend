from io import BytesIO
import os
import requests
from telegram import InlineKeyboardMarkup
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys
from django.core.cache import cache
from asgiref.sync import sync_to_async

async def send_product_photo(query, product, caption, buttons):
    """
    Helper function to send product photo with caption and buttons.
    Falls back to default logo if product image is unavailable.
    """
    reply_markup = InlineKeyboardMarkup(buttons)
    image_url = product.get("main_image")
    
    try:
        if image_url:
            resp = await sync_to_async(requests.get)(image_url)
            resp.raise_for_status()
            image_file = BytesIO(resp.content)
        else:
            raise Exception("No image")
    except Exception:
        image_file = open(os.path.join("media", "logo.jpeg"), "rb")

    await query.message.reply_photo(
        photo=image_file,
        caption=caption,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    
    if not isinstance(image_file, BytesIO):
        image_file.close()


def get_user_token(user_id):
    """
    Get user authentication token from cache.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        str: JWT token if found, None otherwise
    """
    token_key = CacheKeys.format(CacheKeys.telegram_user_tokens, user_id=user_id)
    return GlobalCache.get(token_key)


async def check_authentication(query, user_id):
    """
    Check if user is authenticated and return token with headers.
    Sends appropriate message if not authenticated.
    
    Args:
        query: Telegram callback query
        user_id: Telegram user ID
        
    Returns:
        tuple: (token, headers) if authenticated, (None, None) otherwise
    """
    token = get_user_token(user_id)
    
    if not token:
        await query.message.reply_text(
            "⚠️ You must login first.\nPlease tap 🔐 *Login*.",
            parse_mode="Markdown"
        )
        return None, None
    
    headers = {"Authorization": f"Bearer {token}"}
    return token, headers


async def handle_auth_error(query, user_id):
    """
    Handle authentication error (expired or invalid token).
    Clears token from cache and notifies user.
    
    Args:
        query: Telegram callback query
        user_id: Telegram user ID
    """
    token_key = CacheKeys.format(CacheKeys.telegram_user_tokens, user_id=user_id)
    cache.delete(token_key)
    
    await query.message.reply_text(
        "⚠️ Your session expired.\nPlease login again.",
        parse_mode="Markdown"
    )


NIGERIAN_STATES = [
    "Abia","Adamawa","Akwa Ibom","Anambra","Bauchi","Bayelsa","Benue","Borno","Cross River",
    "Delta","Ebonyi","Edo","Ekiti","Enugu","FCT","Gombe","Imo","Jigawa","Kaduna","Kano",
    "Katsina","Kebbi","Kogi","Kwara","Lagos","Nasarawa","Niger","Ogun","Ondo","Osun",
    "Oyo","Plateau","Rivers","Sokoto","Taraba","Yobe","Zamfara"
]

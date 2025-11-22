import requests
from telegram import Update
from telegram.ext import ContextTypes
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys
from django.core.cache import cache
from .config import ADMIN_URL


async def handle_login(query, user_id):
    """
    Handle login button press - starts the login flow.
    """
    stage_key = CacheKeys.format(CacheKeys.telegram_user_login_stage, user_id=user_id)
    GlobalCache.set(stage_key, "awaiting_email")
    
    await query.message.reply_text(
        "🔐 Please enter your email to login:"
    )


async def handle_email_input(update: Update, user_id: int, email: str):
    """
    Handle email input during login flow.
    """
    email_key = CacheKeys.format(CacheKeys.telegram_user_login_codes, user_id=user_id)
    GlobalCache.set(email_key, email)
    
    resp = requests.post(f"{ADMIN_URL}/send-token/", json={"email": email})
    print("Send token response:", resp.text)
    
    if resp.status_code == 200:
        stage_key = CacheKeys.format(CacheKeys.telegram_user_login_stage, user_id=user_id)
        GlobalCache.set(stage_key, "awaiting_code")
        
        await update.message.reply_text(
            "✅ Code sent to your email. Please enter the code here to verify:"
        )
    else:
        await update.message.reply_text(
            "❌ Failed to send code. Please check your email and try again."
        )


async def handle_code_input(update: Update, user_id: int, code: str):
    """
    Handle verification code input during login flow.
    """
    email_key = CacheKeys.format(CacheKeys.telegram_user_login_codes, user_id=user_id)
    email = GlobalCache.get(email_key)
    
    resp = requests.post(f"{ADMIN_URL}/telegram-login/", json={"email": email, "token": code})
    print("Verify code response:", resp.text)
    
    if resp.status_code == 200:
        token = resp.json().get("data").get("access_token")
        
        token_key = CacheKeys.format(CacheKeys.telegram_user_tokens, user_id=user_id)
        GlobalCache.set(token_key, token)
        
        print("Login successful, token stored in cache.", token)

        # Clear login flow data
        stage_key = CacheKeys.format(CacheKeys.telegram_user_login_stage, user_id=user_id)
        cache.delete(stage_key)
        cache.delete(email_key)
        
        await update.message.reply_text("✅ Login successful!")
    else:
        await update.message.reply_text("❌ Invalid code. Please try again.")

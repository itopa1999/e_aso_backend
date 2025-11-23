"""
Product search handler for Telegram bot.
Implements smart fuzzy search functionality.
"""
import requests
from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram import Update

from .config import ASO_URL
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


async def handle_search_products(query, user_id):
    """
    Handle search products button press - prompt user to enter search query.
    """
    # Set search stage in cache
    stage_key = CacheKeys.format(CacheKeys.telegram_user_search_stage, user_id=user_id)
    GlobalCache.set(stage_key, "awaiting_query")
    
    await query.message.reply_text(
        "🔍 <b>Smart Product Search</b>\n\n"
        "Please enter the product name or keyword to search for:\n\n"
        "<i>Examples:</i>\n"
        "• iPhone\n"
        "• Samsung Galaxy\n"
        "• Laptop\n"
        "• Men's shoes\n\n"
        "Type your search term below:",
        parse_mode="HTML"
    )


async def handle_search_input(update: Update, user_id: int, search_query: str):
    """
    Handle user's search input and perform smart search.
    """
    # Check if user is in search stage
    stage_key = CacheKeys.format(CacheKeys.telegram_user_search_stage, user_id=user_id)
    stage = GlobalCache.get(stage_key)
    
    if stage != "awaiting_query":
        return False
    
    # Clear search stage
    GlobalCache.set(stage_key, None)
    
    # Perform smart search
    await update.message.reply_text(
        f"🔍 Searching for: <b>{search_query}</b>\n\nPlease wait...",
        parse_mode="HTML"
    )
    
    try:
        # Call smart search API
        resp = await sync_to_async(requests.get)(
            f"{ASO_URL}/smart-search/{search_query}/"
        )
        
        if resp.status_code != 200:
            await update.message.reply_text(
                "❌ <b>Search Error</b>\n\n"
                "Sorry, we couldn't complete your search. Please try again later.",
                parse_mode="HTML"
            )
            return True
        
        data = resp.json()
        product_titles = data.get("data", [])
        
        if not product_titles:
            await update.message.reply_text(
                f"❌ <b>No Results Found</b>\n\n"
                f"We couldn't find any products matching '<i>{search_query}</i>'.\n\n"
                f"<b>Tips:</b>\n"
                f"• Try different keywords\n"
                f"• Check spelling\n"
                f"• Use more general terms\n"
                f"• Browse categories instead",
                parse_mode="HTML"
            )
            return True
        
        # Fetch full product details for matched titles
        resp_list = await sync_to_async(requests.get)(
            f"{ASO_URL}/",
            params={"search": search_query}
        )
        
        if resp_list.status_code != 200:
            await update.message.reply_text(
                "❌ <b>Error Loading Products</b>\n\n"
                "Sorry, we couldn't load the product details. Please try again.",
                parse_mode="HTML"
            )
            return True
        
        products_data = resp_list.json()
        products = products_data.get("results", [])
        
        if not products:
            await update.message.reply_text(
                f"❌ <b>No Products Found</b>\n\n"
                f"We found matching titles but couldn't load product details.\n"
                f"Please try again or browse our categories.",
                parse_mode="HTML"
            )
            return True
        
        # Display search results
        text = f"🔍 <b>Search Results for '{search_query}'</b>\n\n"
        text += f"Found <b>{len(products)}</b> product(s):\n\n"
        
        for p in products[:10]:  # Limit to 10 results
            title = p.get("title", "No title")
            price = p.get("current_price", "N/A")
            badge = f" [{p['badge']}]" if p.get("badge") else ""
            description = p.get("short_description", "")[:100]
            
            text += f"• <b>{title}</b>{badge}\n"
            text += f"  💰 Price: <i>₦{price}</i>\n"
            if description:
                text += f"  📝 {description}...\n"
            text += "\n"
        
        if len(products) > 10:
            text += f"\n<i>Showing 10 of {len(products)} results</i>\n"
        
        # Add buttons for first few products
        buttons = []
        for p in products[:5]:  # Show buttons for first 5 products
            product_id = p.get("id")
            title = p.get("title", "Product")[:30]  # Truncate long titles
            buttons.append([
                InlineKeyboardButton(
                    f"🛒 {title}",
                    callback_data=f"details_{product_id}"
                )
            ])
        
        # Add "Search Again" button
        buttons.append([
            InlineKeyboardButton("🔍 Search Again", callback_data="search_products")
        ])
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        print(f"[Search Handler] Error: {e}")
        await update.message.reply_text(
            "❌ <b>Search Error</b>\n\n"
            "An error occurred while searching. Please try again later.",
            parse_mode="HTML"
        )
    
    return True

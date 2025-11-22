from telegram import Update
from telegram.ext import ContextTypes
from .config import TELEGRAM_CHANNEL_ID


async def handle_new_channel_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle when a new member joins the channel/group.
    Sends a welcome message to the channel.
    """
    message = update.message or update.channel_post
    
    if not message or not message.new_chat_members:
        return
    
    chat_id = message.chat.id
    
    print(f"[Channel Handler] New member(s) joined - Chat ID: {chat_id}")
    
    # Check if this is from the target channel/group
    if chat_id == TELEGRAM_CHANNEL_ID:
        try:
            bot_username = context.bot.username or "our_bot"
            
            # Get the new members' names
            new_members = message.new_chat_members
            member_names = ", ".join([member.first_name for member in new_members])
            
            welcome_message = f"""
🎉 <b>Welcome {member_names}!</b>

Thank you for joining our channel! We're excited to have you here.

<b>📢 Stay tuned for:</b>
• New product announcements
• Special offers and discounts
• Updates and news

<b>🛍️ Ready to Shop?</b>
Chat directly with our bot for the full shopping experience:
👉 <b>@{bot_username}</b>

<b>What you can do with our bot:</b>
✅ Browse all products with images and prices
✅ Place orders instantly
✅ Track your deliveries
✅ Contact support anytime

<b>Get Started:</b>
Click @{bot_username} and tap "Start" or type /start

Welcome aboard! 🚀
            """
            
            await message.reply_text(
                welcome_message,
                parse_mode="HTML"
            )
            print(f"[Channel Handler] Welcome message sent to new member(s): {member_names}")
            
        except Exception as e:
            print(f"[Channel Handler] Error sending welcome message: {e}")


async def handle_channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle messages sent to the Telegram channel/group.
    Redirects users to chat with the bot directly.
    
    Note: Channel posts come as update.channel_post, not update.message
    """
    # Handle both channel_post and regular messages
    message = update.channel_post or update.message
    
    if not message:
        print(f"[Channel Handler] No message or channel_post found in update")
        return
    
    chat_id = message.chat.id
    chat_type = message.chat.type
    
    print(f"[Channel Handler] Message received - Chat ID: {chat_id}, Type: {chat_type}, Expected: {TELEGRAM_CHANNEL_ID}")
    
    # Check if this message is from the target channel/group
    if chat_id == TELEGRAM_CHANNEL_ID:
        print(f"[Channel Handler] Matched channel ID! Sending redirect message...")
        
        try:
            bot_username = context.bot.username or "our_bot"
            
            channel_response = f"""
👋 <b>Hello!</b>

Thank you for your interest! This is our announcement channel.

To place orders, browse products, and get assistance, please chat directly with our bot:
👉 <b>@{bot_username}</b>

<b>🤖 What Our Bot Can Do:</b>

🛍️ <b>Browse & Shop</b>
• View all products with detailed information
• Browse by categories
• See product images, prices, and descriptions
• Place orders directly through the bot

📦 <b>Track Orders</b>
• View all your orders
• Track delivery status in real-time
• See order details and shipping information

📝 <b>Contact & Support</b>
• Submit special requests
• Contact our support team
• Get help with any questions

🔐 <b>Secure Login</b>
• Email-based verification
• Access your order history
• Manage your account

<b>Getting Started:</b>
1. Click here: @{bot_username}
2. Tap "Start" or type /start
3. Choose what you want to do from the menu

We look forward to serving you! 🎉
            """
            
            await message.reply_text(
                channel_response,
                parse_mode="HTML"
            )
            print(f"[Channel Handler] Message sent successfully!")
            
        except Exception as e:
            print(f"[Channel Handler] Error sending channel message: {e}")
    else:
        print(f"[Channel Handler] Chat ID mismatch - ignoring message")

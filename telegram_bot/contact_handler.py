import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys
from .config import USER_URL


async def handle_contact_request(query, user_id):
    """
    Handle contact/special request button press - starts contact form flow.
    """
    stage_key = CacheKeys.format(CacheKeys.telegram_user_contact_stage, user_id=user_id)
    GlobalCache.set(stage_key, "full_name")
    
    await query.message.reply_text(
        "📝 <b>Contact / Special Request Form</b>\n\n"
        "Please provide your details and we'll get back to you soon.\n\n"
        "Enter your full name:",
        parse_mode="HTML"
    )


async def handle_contact_input(update, user_id, text):
    """
    Handle contact form input step by step.
    """
    stage_key = CacheKeys.format(CacheKeys.telegram_user_contact_stage, user_id=user_id)
    contact_key = CacheKeys.format(CacheKeys.telegram_user_contact_info, user_id=user_id)
    
    stage = GlobalCache.get(stage_key)
    contact_info = GlobalCache.get(contact_key) or {}

    if not stage:
        return False  # Not in contact flow

    # Step-by-step collection
    if stage == "full_name":
        contact_info["full_name"] = text
        GlobalCache.set(contact_key, contact_info)
        GlobalCache.set(stage_key, "phone")
        await update.message.reply_text("Enter your phone number:")
        return True
    
    elif stage == "phone":
        contact_info["phone"] = text
        GlobalCache.set(contact_key, contact_info)
        GlobalCache.set(stage_key, "email")
        await update.message.reply_text("Enter your email address:")
        return True
    
    elif stage == "email":
        contact_info["email"] = text
        GlobalCache.set(contact_key, contact_info)
        GlobalCache.set(stage_key, "subject")
        await update.message.reply_text("Enter the subject of your request:")
        return True
    
    elif stage == "subject":
        contact_info["subject"] = text
        GlobalCache.set(contact_key, contact_info)
        GlobalCache.set(stage_key, "message")
        await update.message.reply_text("Enter your message or special request:")
        return True
    
    elif stage == "message":
        contact_info["message"] = text
        GlobalCache.set(contact_key, contact_info)
        GlobalCache.set(stage_key, "confirm")

        # Build confirmation message
        html_text = "<b>📋 Review Your Contact Request:</b>\n\n"
        html_text += f"• <b>Full Name:</b> {contact_info.get('full_name')}\n"
        html_text += f"• <b>Phone:</b> {contact_info.get('phone')}\n"
        html_text += f"• <b>Email:</b> {contact_info.get('email')}\n"
        html_text += f"• <b>Subject:</b> {contact_info.get('subject')}\n"
        html_text += f"• <b>Message:</b> {contact_info.get('message')}\n\n"
        html_text += "Please review and confirm to submit your request."

        # Add confirm button
        buttons = [
            [InlineKeyboardButton("✅ Submit Request", callback_data="submit_contact")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_contact")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(html_text, parse_mode="HTML", reply_markup=reply_markup)
        return True
    
    return False


async def handle_submit_contact(query, user_id):
    """
    Submit contact form to backend API.
    """
    contact_key = CacheKeys.format(CacheKeys.telegram_user_contact_info, user_id=user_id)
    contact_info = GlobalCache.get(contact_key)
    
    if not contact_info:
        await query.message.reply_text("❌ No contact information found. Please start over.")
        return
    
    # Send to backend
    try:
        resp = requests.post(
            f"{USER_URL}/contact/submit/",
            json={
                "full_name": contact_info.get("full_name"),
                "phone": contact_info.get("phone"),
                "email": contact_info.get("email"),
                "subject": contact_info.get("subject"),
                "message": contact_info.get("message")
            }
        )
        
        if resp.status_code in [200, 201]:
            # Clear contact flow cache
            stage_key = CacheKeys.format(CacheKeys.telegram_user_contact_stage, user_id=user_id)
            GlobalCache.set(stage_key, None)
            GlobalCache.set(contact_key, None)
            
            await query.message.reply_text(
                "✅ <b>Thank You!</b>\n\n"
                "Your request has been submitted successfully. "
                "We have received your message and will get back to you within 24-48 hours.\n\n"
                "A confirmation email has been sent to your email address.\n\n"
                "Type /start to return to the main menu.",
                parse_mode="HTML"
            )
        else:
            await query.message.reply_text(
                "❌ <b>Submission Failed</b>\n\n"
                "Sorry, there was an error submitting your request. "
                "Please try again later or contact us directly.\n\n"
                f"Error: {resp.status_code}",
                parse_mode="HTML"
            )
    except Exception as e:
        await query.message.reply_text(
            "❌ <b>Connection Error</b>\n\n"
            "Unable to connect to the server. Please try again later.",
            parse_mode="HTML"
        )
        print(f"Contact form submission error: {e}")


async def handle_cancel_contact(query, user_id):
    """
    Cancel contact form submission.
    """
    stage_key = CacheKeys.format(CacheKeys.telegram_user_contact_stage, user_id=user_id)
    contact_key = CacheKeys.format(CacheKeys.telegram_user_contact_info, user_id=user_id)
    
    # Clear contact flow cache
    GlobalCache.set(stage_key, None)
    GlobalCache.set(contact_key, None)
    
    await query.message.reply_text(
        "❌ Contact request cancelled.\n\n"
        "Type /start to return to the main menu.",
        parse_mode="HTML"
    )

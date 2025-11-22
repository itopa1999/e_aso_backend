async def handle_help(query):
    """
    Handle help button press.
    """
    await query.message.reply_text(
        "💬 <b>Need help?</b>\nSend your questions here and our support team will assist you.",
        parse_mode="HTML"
    )

async def handle_help(query):
    """
    Handle help button press - provides comprehensive bot usage instructions.
    """
    help_text = """
<b>🤖 Welcome to Esther's Fabrics Ofi Marketplace Bot!</b>

<b>📖 How to Use This Bot:</b>

<b>1️⃣ Browse Products</b>
• Tap <b>🛍️ List Products</b> to see all available products
• Use <b>📂 List Categories</b> to browse by category
• Tap <b>ℹ️ See Details</b> on any product for full information
• Navigate using <b>⬅️ Previous</b> and <b>➡️ Next</b> buttons

<b>2️⃣ Place an Order</b>
• View product details and tap <b>🛒 Order Now</b>
• You'll be guided to enter shipping information step by step:
  - First Name
  - Last Name
  - Address
  - City
  - State (select from list)
  - Phone Number
  - Alternative Phone
  - Additional Info (optional)
• Review your order and tap <b>✅ Confirm Order</b>
• Complete payment to finalize your order

<b>3️⃣ Track Your Orders</b>
• Login first using <b>🔐 Login</b>
• Tap <b>📦 My Orders</b> to view all your orders
• Tap <b>🔍 View Details</b> to see full order information and tracking

<b>4️⃣ Login System</b>
• Tap <b>🔐 Login</b> from the main menu
• Enter your email address
• Enter the verification code sent to your email
• You'll be logged in and can access your orders

<b>🚫 Cancel Any Operation:</b>
• Type <code>/cancel</code> or simply <code>cancel</code> at any time
• This will stop the current process and return you to the main menu
• All temporary data will be cleared

<b>🔄 Start Over:</b>
• Type <code>/start</code> to return to the main menu anytime
• Your login session remains active until it expires

<b>💡 Tips:</b>
• Make sure to login before viewing your orders
• Your session may expire after some time for security
• If prompted to login again, simply re-enter your credentials
• You can cancel any multi-step process at any point

<b>❓ Need More Help?</b>
If you have questions or issues, please contact our support team through the contact form on our website or send us an email.

<b>📧 Support:</b> support@esthersfabrics.com
<b>🌐 Website:</b> www.asooke.com

Type <code>/start</code> to return to the main menu.
    """
    
    await query.message.reply_text(help_text, parse_mode="HTML")

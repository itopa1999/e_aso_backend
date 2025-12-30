from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def handle_help(query):
    """
    Handle help button press - shows help topics menu.
    """
    help_menu_text = """
<b>🤖 ESTHER'S FABRICS BOT - HELP CENTER</b>

Select a topic to learn more:
    """
    
    keyboard = [
        [InlineKeyboardButton("1️⃣ Getting Started", callback_data="help_getting_started")],
        [InlineKeyboardButton("2️⃣ Browsing Products", callback_data="help_browsing")],
        [InlineKeyboardButton("3️⃣ Placing Orders", callback_data="help_orders")],
        [InlineKeyboardButton("4️⃣ Managing Account", callback_data="help_account")],
        [InlineKeyboardButton("5️⃣ Tracking Orders", callback_data="help_tracking")],
        [InlineKeyboardButton("6️⃣ Notifications", callback_data="help_notifications")],
        [InlineKeyboardButton("7️⃣ Payment Methods", callback_data="help_payment")],
        [InlineKeyboardButton("8️⃣ Troubleshooting", callback_data="help_troubleshooting")],
        [InlineKeyboardButton("9️⃣ Tips & Tricks", callback_data="help_tips")],
        [InlineKeyboardButton("🔟 Contact & Support", callback_data="help_support")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(help_menu_text, reply_markup=reply_markup, parse_mode="HTML")


async def send_help_section(query, section):
    """
    Send specific help section based on user selection.
    """
    
    sections = {
        "help_getting_started": {
            "title": "🚀 GETTING STARTED",
            "content": """
<b>Welcome to Esther's Fabrics Bot!</b>

<b>First Time Users:</b>
• Launch the bot and tap <code>/start</code>
• You'll see the main menu with all options
• No login required to browse products
• Login only when ready to place an order

<b>Main Menu Features:</b>
🛍️ <b>List Products</b> - Browse all available items
📂 <b>List Categories</b> - View by category
🔍 <b>Search Products</b> - Find specific items
📦 <b>My Orders</b> - Your order history (login needed)
🔔 <b>Notifications</b> - Get order updates
📝 <b>Contact/Special Request</b> - Send messages
ℹ️ <b>Help</b> - This guide
🔐 <b>Login</b> - Access your account

<b>Quick Commands:</b>
• <code>/start</code> - Return to menu
• <code>/cancel</code> - Stop any operation
• <code>/help</code> - Show help menu
            """
        },
        
        "help_browsing": {
            "title": "📖 BROWSING PRODUCTS",
            "content": """
<b>Three Ways to Find Products:</b>

<b>📋 Option 1: List All Products</b>
• Tap <b>🛍️ List Products</b>
• Shows 20 products per page
• Each shows name, price, description
• Use ⬅️ Previous / ➡️ Next to navigate

<b>📂 Option 2: Browse by Category</b>
• Tap <b>📂 List Categories</b>
• Select category of interest
• View products in that category
• Same pagination as product list

<b>🔍 Option 3: Search Products</b>
• Tap <b>🔍 Search Products</b>
• Type what you're looking for
• Examples: "lace", "cotton", "ankara"
• Results show matching products

<b>Understanding Product Info:</b>

When viewing details, you see:
• <b>Product Number</b> - Unique ID
• <b>Price</b> - In Nigerian Naira (₦)
• <b>Original Price</b> - For comparison
• <b>Discount %</b> - How much you save
• <b>Rating</b> - Star rating from customers
• <b>Reviews</b> - Number of customer reviews
• <b>Categories</b> - Related categories
• <b>Colors</b> - Available color options
• <b>Sizes</b> - Available sizes
• <b>Description</b> - Full product details
• <b>Specifications</b> - Care, materials, etc.

<b>💡 Browsing Tip:</b>
Use Search if you know what you want - it's faster!
            """
        },
        
        "help_orders": {
            "title": "🛒 PLACING ORDERS",
            "content": """
<b>Complete Order Process:</b>

<b>Step 1: Find Product</b>
• Browse or search for product
• Tap <b>🛒 Order Now</b>

<b>Step 2: Enter Shipping Info</b>
You'll be asked for:
• <b>First Name</b>
• <b>Last Name</b>
• <b>Address</b> - Street/house number
• <b>City</b>
• <b>State</b> - Select from list
• <b>Phone</b> - Main contact number
• <b>Alt Phone</b> - Backup number (optional)
• <b>Extra Info</b> - Special notes (optional)

<b>Step 3: Review & Confirm</b>
• Double-check all information
• Tap <b>✅ Confirm Order</b>
• Cannot be edited after this

<b>Step 4: Select Payment</b>
Choose from:
• 💳 Paystack
• 🟠 Monnify
• 🔵 Flutterwave

<b>Step 5: Pay Securely</b>
• Enter payment details
• Confirm transaction
• Get payment receipt

<b>Step 6: Order Created!</b>
• Get order number (e.g., #ORD123)
• Email confirmation sent
• Order tracking begins

<b>⚠️ Important:</b>
• All prices in Naira (₦)
• Shipping fee based on location
• One product per order via bot
• Use website for multiple items
            """
        },
        
        "help_account": {
            "title": "🔐 MANAGING YOUR ACCOUNT",
            "content": """
<b>Login & Account Management</b>

<b>Why Login?</b>
• View your order history
• Track past purchases
• Subscribe to notifications
• Monitor order status
• Access personalized features

<b>How to Login:</b>

1️⃣ Tap <b>🔐 Login</b> from menu
2️⃣ Enter your email address
3️⃣ Check email for verification code
4️⃣ Return to bot & enter code
5️⃣ ✅ You're logged in!

<b>Verification Code Info:</b>
• 6-digit code sent to email
• Valid for 10 minutes
• Check spam folder if not found
• Request new code if expired
• Code is numbers only

<b>Session Details:</b>
• Session lasts several hours
• Auto-expires after inactivity
• Login again if session expires
• Logout on public devices

<b>Password Reset:</b>
• Visit: www.asooke.com/reset
• Or contact support
• Use verification code to login

<b>Account Security Tips:</b>
• Never share verification codes
• Don't login on public devices
• Keep email secure
• Change password regularly
            """
        },
        
        "help_tracking": {
            "title": "📦 TRACKING ORDERS",
            "content": """
<b>View & Track Your Orders</b>

<b>How to Access Orders:</b>

1️⃣ Tap <b>🔐 Login</b> (if not logged in)
2️⃣ Tap <b>📦 My Orders</b>
3️⃣ Browse orders (20 per page)
4️⃣ Tap <b>🔍 View Details</b>

<b>Order Summary Shows:</b>
• Order number & date placed
• Current status
• Estimated delivery date
• Tracking number & carrier
• All costs breakdown

<b>Financial Breakdown:</b>
• <b>Subtotal</b> - Item price
• <b>Shipping Fee</b> - Delivery cost
• <b>Discount</b> - Any savings
• <b>Total</b> - Final price paid
• <b>Payment Method</b> - How you paid

<b>Items Ordered:</b>
• Product name & description
• Quantity ordered
• Price per unit

<b>Tracking Stages:</b>
✅ Order Placed
⏳ Processing
⏳ Shipped
⏳ In Transit
⏳ Out for Delivery
✅ Delivered

<b>💡 Tips:</b>
• Subscribe to notifications
• Save order number
• Contact if delayed
            """
        },
        
        "help_notifications": {
            "title": "🔔 NOTIFICATIONS",
            "content": """
<b>Subscribe to Order Updates</b>

<b>Benefits:</b>
• Instant status updates via Telegram
• Know when order ships
• Get delivery notification
• Never miss important info
• Can unsubscribe anytime

<b>How to Subscribe:</b>

1️⃣ Tap <b>🔔 Notifications</b>
2️⃣ See your current status
3️⃣ Tap <b>🔔 Subscribe</b>
4️⃣ Confirm when prompted
5️⃣ Done! Updates will start

<b>What Triggers Notifications:</b>
• Order confirmed & processing
• Order shipped from warehouse
• Out for delivery
• Delivery confirmation
• Any issues or delays

<b>How to Unsubscribe:</b>

1️⃣ Tap <b>🔔 Notifications</b>
2️⃣ Tap <b>🔕 Unsubscribe</b>
3️⃣ Confirm choice
4️⃣ Notifications stop

<b>Requirements:</b>
• Must be logged in
• Telegram connected
• Allow bot messages

<b>💡 Tips:</b>
• Notifications are FREE
• Works 24/7
• Manage anytime
            """
        },
        
        "help_payment": {
            "title": "💳 PAYMENT METHODS",
            "content": """
<b>Available Payment Options</b>

<b>🟢 PAYSTACK</b>
Accepts:
• Credit/Debit cards
• Bank transfers
• USSD
• Mobile wallets

Benefits:
• Quick processing
• Highly secure
• Widely available

<b>🟠 MONNIFY</b>
Accepts:
• Bank transfers
• Card payments
• QR scanning
• USSD

Benefits:
• Multiple options
• Instant verification
• Direct transfer

<b>🔵 FLUTTERWAVE</b>
Accepts:
• Visa/Mastercard
• Bank accounts
• USSD codes
• Mobile money

Benefits:
• Most methods
• Secure
• Fast settlement

<b>🔒 Security:</b>
• All encrypted
• Card never stored
• PCI DSS compliant
• Instant confirmation

<b>💡 Tips:</b>
• Use 3D Secure
• Keep reference
• Use stable internet
• Don't refresh
• Screenshot confirmation
            """
        },
        
        "help_troubleshooting": {
            "title": "🔧 TROUBLESHOOTING",
            "content": """
<b>Common Issues & Solutions</b>

<b>❌ Login Issues</b>
• Verify email correct
• Check spam folder
• Code expires in 10 min
• Request new code if expired

<b>❌ Payment Failed</b>
• Check balance
• Verify card not expired
• Check internet
• Try different method
• Contact your bank

<b>❌ Order Not Found</b>
• Ensure logged in
• Wait for order process
• Refresh by going to menu
• Check email

<b>❌ Shipping Address Error</b>
• Go step-by-step
• Select state from dropdown
• Check for typos
• Clear and re-enter

<b>❌ Session Expired</b>
• Simply login again
• Request new code
• Sessions last hours

<b>❌ Server Error</b>
• Check internet
• Try again in a moment
• Use /start
• Contact support if continues

<b>❌ Notification Won't Subscribe</b>
• Login first
• Allow bot messages
• Check Telegram settings

<b>💡 Quick Help:</b>
Most issues resolve on retry!
            """
        },
        
        "help_tips": {
            "title": "💡 TIPS & TRICKS",
            "content": """
<b>Best Practices</b>

<b>🛍️ Browsing:</b>
• Use Search for known items
• Browse Categories to discover
• Check product ratings
• Read descriptions
• Note colors & sizes

<b>🛒 Ordering:</b>
• Double-check all info
• Ensure correct phone
• Add special instructions
• Pay attention to state
• Keep order number

<b>🔐 Account:</b>
• Keep email updated
• Check spam for codes
• Don't share codes
• Logout from public devices
• Use strong passwords

<b>💳 Payment:</b>
• Have method ready
• Use stable internet
• Don't refresh
• Screenshot reference
• Wait for confirmation

<b>📦 Tracking:</b>
• Enable notifications
• Save order number
• Contact if delayed
• Keep proof of delivery

<b>⚡ General:</b>
• /start to go to menu
• /cancel to stop
• Wait for responses
• Don't rapid-click
• Clear cache if issues

<b>🎯 Quick Tips:</b>
Browse → Search → Order → Pay
Login → Orders → Details → Track
            """
        },
        
        "help_support": {
            "title": "📞 SUPPORT & CONTACT",
            "content": """
<b>Get Help & Support</b>

<b>📝 In-Bot Contact:</b>
• Tap <b>📝 Contact/Special Request</b>
• Describe your issue
• Response within 24 hours

<b>📧 Email Support:</b>
support@esthersfabrics.com
Response time: 24-48 hours

<b>🌐 Website:</b>
www.asooke.com
• Live chat (business hours)
• FAQ section
• Account management

<b>📱 Telegram:</b>
• Direct message for urgent
• Response during business hours

<b>⏰ Business Hours:</b>
Mon-Fri: 9 AM - 6 PM (Lagos)
Saturday: 10 AM - 4 PM
Sunday: Closed

<b>What to Include:</b>
• Order number (if applicable)
• Your email address
• Detailed description
• Error messages
• Screenshots if needed

<b>📋 Contact Reasons:</b>
• Track delayed orders
• Modify delivery address
• Product recommendations
• Damaged items
• Special requests
• Wholesale inquiries

<b>🎯 Priority:</b>
1. In-bot contact form
2. Email for detailed
3. Website chat for urgent
4. Telegram for emergencies
            """
        }
    }
    
    if section in sections:
        section_data = sections[section]
        text = f"""
<b>{section_data['title']}</b>

{section_data['content']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tap <code>/help</code> to see other topics.
        """
        await query.message.reply_text(text, parse_mode="HTML")
    else:
        await query.message.reply_text("❌ Help section not found. Try again.")

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
KNOX STORE Telegram Bot
python-telegram-bot v20.7 compatible
"""

import logging
import re

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)


# ============================================
# CONFIGURATION
# ============================================

# IMPORTANT:
# Put your NEW regenerated bot token here.
BOT_TOKEN = "8768230830:AAHamryLyN0FzEYbn-Da3OdlmkOwOTq-qkQ"

ADMIN_CHAT_ID = 8925766938

SUPPORT_USERNAME = "KNOX_STORE_SUPPORT"

QR_IMAGE = "qr.jpg"


# ============================================
# FORCE JOIN / CHANNEL
# ============================================

FORCE_JOIN_CHANNEL = "@KnoxStoreUpdates"

FORCE_JOIN_LINK = "https://t.me/KnoxStoreUpdates"


# ============================================
# PRODUCTS
# ============================================

PRODUCTS = {

    "amul_100": {
        "name": "🧀 Amul ₹100 Coupon",
        "price": 22,
        "min_qty": 3
    },

    "amul_100_bulk": {
        "name": "🧀 Amul ₹100 Bulk Coupon",
        "price": 16,
        "min_qty": 5
    },

    "flipkart_249": {
        "name": "🛒 Flipkart ₹249 Gift Voucher",
        "price": 125,
        "min_qty": 1
    },

    "flipkart_499": {
        "name": "🛒 Flipkart ₹499 Gift Voucher",
        "price": 249,
        "min_qty": 1
    },

    "dominos_100": {
        "name": "🍕 Domino's ₹100 Gift Voucher",
        "price": 40,
        "min_qty": 2
    },

    "bookmyshow_499": {
        "name": "🎬 BookMyShow ₹499 Gift Card",
        "price": 249,
        "min_qty": 1
    },

    "pvr_200": {
        "name": "🎞 PVR ₹200 Movie Voucher",
        "price": 50,
        "min_qty": 2
    },

    "blinkit_499": {
        "name": "🛍️ Blinkit ₹499 Coupon",
        "price": 249,
        "min_qty": 1
    },

    "bigbasket_249": {
        "name": "🛒 BigBasket ₹249 Gift Voucher",
        "price": 125,
        "min_qty": 1
    },

    "swiggy_249": {
        "name": "🍔 Swiggy ₹249 Coupon",
        "price": 125,
        "min_qty": 1
    },

    "zomato_249": {
        "name": "🍔 Zomato ₹249 Gift Voucher",
        "price": 125,
        "min_qty": 1
    },

    "shein_800": {
        "name": "👗 SHEIN ₹800 off on ₹1000",
        "price": 80,
        "min_qty": 1
    }
}


# ============================================
# STATES
# ============================================

(
    SELECTING_PRODUCT,
    ENTERING_QUANTITY,
    WAITING_FOR_SCREENSHOT,
    WAITING_FOR_UTR
) = range(4)


# ============================================
# TEMPORARY STORAGE
# ============================================

current_orders = {}

order_history = {}


# ============================================
# LOGGING
# ============================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# ============================================
# PERMANENT REPLY KEYBOARD
# ============================================

def get_main_keyboard():

    keyboard = [

        [
            "🛍️ Buy Voucher",
            "📜 History"
        ],

        [
            "💬 Support",
            "ℹ️ Disclaimer"
        ],

        [
            "📢 Join Channel"
        ]

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True
    )


# ============================================
# FORCE JOIN CHECK
# ============================================

async def is_user_joined(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> bool:

    user = update.effective_user

    try:

        member = await context.bot.get_chat_member(
            chat_id=FORCE_JOIN_CHANNEL,
            user_id=user.id
        )

        return member.status in (
            "member",
            "administrator",
            "creator"
        )

    except Exception as e:

        logger.error(
            f"Force Join Check Error: {e}"
        )

        return False


# ============================================
# FORCE JOIN SCREEN
# ============================================

async def show_force_join(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [

        [
            InlineKeyboardButton(
                "📢 Join Channel",
                url=FORCE_JOIN_LINK
            )
        ],

        [
            InlineKeyboardButton(
                "✅ I've Joined",
                callback_data="check_force_join"
            )
        ]

    ]

    text = (
        "🔐 <b>𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐉𝐨𝐢𝐧 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝</b>\n\n"
        "🖤 Welcome to <b>KNOX STORE</b>.\n\n"
        "To access the store, please join our "
        "official updates channel first.\n\n"
        "1️⃣ Join the channel\n"
        "2️⃣ Tap <b>I've Joined</b>\n"
        "3️⃣ Continue shopping 🛍️"
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:

        await update.callback_query.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

    elif update.message:

        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


# ============================================
# MAIN MENU
# ============================================

async def show_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    edit_message=False
) -> int:

    text = (
        "🖤 <b>𝐊𝐍𝐎𝐗 𝐒𝐓𝐎𝐑𝐄</b>\n\n"
        "✨ Welcome! Your trusted voucher store.\n\n"
        "🛍️ Browse available vouchers\n"
        "💳 Secure payment workflow\n"
        "🔐 Payment verification process\n\n"
        "👇 <b>Select an option below</b>"
    )

    keyboard = get_main_keyboard()

    if edit_message and update.callback_query:

        await update.callback_query.message.reply_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    elif update.message:

        await update.message.reply_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    return SELECTING_PRODUCT


# ============================================
# START
# ============================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    user = update.effective_user

    if user.id in current_orders:
        del current_orders[user.id]

    if not await is_user_joined(
        update,
        context
    ):

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    return await show_main_menu(
        update,
        context
    )


# ============================================
# FORCE JOIN CALLBACK
# ============================================

async def force_join_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    joined = await is_user_joined(
        update,
        context
    )

    if not joined:

        await query.answer(
            "❌ Please join the channel first!",
            show_alert=True
        )

        return

    await query.answer(
        "✅ Membership verified!"
    )

    text = (
        "🖤 <b>𝐊𝐍𝐎𝐗 𝐒𝐓𝐎𝐑𝐄</b>\n\n"
        "✅ Channel membership verified.\n\n"
        "You're ready to continue! 🛍️\n\n"
        "👇 Select an option below."
    )

    await query.message.reply_text(
        text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


# ============================================
# BUY VOUCHER
# ============================================

async def buy_voucher(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    if not await is_user_joined(
        update,
        context
    ):

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    text = (
        "🛍️ <b>𝐁𝐔𝐘 𝐕𝐎𝐔𝐂𝐇𝐄𝐑</b>\n\n"
        "✨ Select a voucher or gift card below.\n\n"
        "💰 Prices are shown per item."
    )

    keyboard = []

    for product_id, product in PRODUCTS.items():

        button_text = (
            f"{product['name']} • ₹{product['price']}"
        )

        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"select_{product_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Back to Menu",
            callback_data="back_to_main"
        )
    ])

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return SELECTING_PRODUCT


# ============================================
# SHOW PRODUCTS CALLBACK
# ============================================

async def show_products(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    query = update.callback_query

    await query.answer()

    if not await is_user_joined(
        update,
        context
    ):

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    text = (
        "🛍️ <b>𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄 𝐕𝐎𝐔𝐂𝐇𝐄𝐑𝐒</b>\n\n"
        "Select your preferred product:"
    )

    keyboard = []

    for product_id, product in PRODUCTS.items():

        button_text = (
            f"{product['name']} • ₹{product['price']}"
        )

        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"select_{product_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Back to Menu",
            callback_data="back_to_main"
        )
    ])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return SELECTING_PRODUCT


# ============================================
# SELECT PRODUCT
# ============================================

async def select_product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    query = update.callback_query

    await query.answer()

    if not await is_user_joined(
        update,
        context
    ):

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    product_id = query.data.replace(
        "select_",
        ""
    )

    if product_id not in PRODUCTS:

        return SELECTING_PRODUCT

    product = PRODUCTS[product_id]

    user_id = update.effective_user.id

    min_qty = product["min_qty"]

    current_orders[user_id] = {

        "product_id": product_id,

        "product_name": product["name"],

        "price_per_item": product["price"],

        "min_qty": min_qty

    }

    text = (
        f"🛍️ <b>{product['name']}</b>\n\n"
        f"💰 <b>Price:</b> ₹{product['price']} / item\n"
        f"📦 <b>Minimum:</b> {min_qty}\n\n"
        "🔢 <b>SELECT QUANTITY</b>\n"
        "Choose one of the options below:"
    )

    quantities = [
        min_qty,
        min_qty + 1,
        min_qty + 2,
        min_qty + 3
    ]

    keyboard = [

        [
            InlineKeyboardButton(
                str(qty),
                callback_data=f"qty_{qty}"
            )
            for qty in quantities
        ],

        [
            InlineKeyboardButton(
                "✏️ Custom Quantity",
                callback_data="custom_quantity"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back to Products",
                callback_data="show_products"
            )
        ]

    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return ENTERING_QUANTITY


# ============================================
# INLINE QUANTITY
# ============================================

async def select_quantity(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    query = update.callback_query

    if not await is_user_joined(
        update,
        context
    ):

        await query.answer(
            "❌ Please join the channel first!",
            show_alert=True
        )

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    user_id = update.effective_user.id

    if user_id not in current_orders:

        await query.answer(
            "❌ No active order!",
            show_alert=True
        )

        return SELECTING_PRODUCT

    try:

        quantity = int(
            query.data.replace(
                "qty_",
                ""
            )
        )

    except ValueError:

        await query.answer(
            "❌ Invalid quantity!",
            show_alert=True
        )

        return ENTERING_QUANTITY

    order = current_orders[user_id]

    if quantity < order["min_qty"]:

        await query.answer(
            f"Minimum quantity: {order['min_qty']}",
            show_alert=True
        )

        return ENTERING_QUANTITY

    await query.answer(
        f"Quantity {quantity} selected ✅"
    )

    return await process_quantity(
        update,
        context,
        quantity
    )


# ============================================
# CUSTOM QUANTITY
# ============================================

async def custom_quantity(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    query = update.callback_query

    await query.answer()

    user_id = update.effective_user.id

    if user_id not in current_orders:

        await query.answer(
            "❌ No active order!",
            show_alert=True
        )

        return SELECTING_PRODUCT

    min_qty = current_orders[user_id]["min_qty"]

    text = (
        "✏️ <b>𝐂𝐔𝐒𝐓𝐎𝐌 𝐐𝐔𝐀𝐍𝐓𝐈𝐓𝐘</b>\n\n"
        f"📦 Minimum quantity: <b>{min_qty}</b>\n\n"
        "⌨️ Please type the quantity you want.\n"
        "Example: <code>10</code>"
    )

    keyboard = [[
        InlineKeyboardButton(
            "⬅️ Back",
            callback_data="back_to_quantity"
        )
    ]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return ENTERING_QUANTITY


# ============================================
# BACK TO QUANTITY
# ============================================

async def back_to_quantity(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    query = update.callback_query

    await query.answer()

    user_id = update.effective_user.id

    if user_id not in current_orders:

        return SELECTING_PRODUCT

    order = current_orders[user_id]

    min_qty = order["min_qty"]

    text = (
        f"🛍️ <b>{order['product_name']}</b>\n\n"
        f"💰 <b>Price:</b> ₹{order['price_per_item']} / item\n"
        f"📦 <b>Minimum:</b> {min_qty}\n\n"
        "🔢 <b>SELECT QUANTITY</b>"
    )

    quantities = [
        min_qty,
        min_qty + 1,
        min_qty + 2,
        min_qty + 3
    ]

    keyboard = [

        [
            InlineKeyboardButton(
                str(qty),
                callback_data=f"qty_{qty}"
            )
            for qty in quantities
        ],

        [
            InlineKeyboardButton(
                "✏️ Custom Quantity",
                callback_data="custom_quantity"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back to Products",
                callback_data="show_products"
            )
        ]

    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return ENTERING_QUANTITY


# ============================================
# PROCESS QUANTITY
# ============================================

async def process_quantity(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    quantity: int
) -> int:

    user_id = update.effective_user.id

    if user_id not in current_orders:

        await update.effective_chat.send_message(
            "❌ No active order.\n\n"
            "Please start again with /start."
        )

        return ConversationHandler.END

    order = current_orders[user_id]

    if quantity < order["min_qty"]:

        if update.callback_query:

            await update.callback_query.answer(
                f"Minimum quantity: {order['min_qty']}",
                show_alert=True
            )

        return ENTERING_QUANTITY

    total_amount = (
        order["price_per_item"] * quantity
    )

    order["quantity"] = quantity
    order["total_amount"] = total_amount

    summary = (
        "🧾 <b>𝐎𝐑𝐃𝐄𝐑 𝐒𝐔𝐌𝐌𝐀𝐑𝐘</b>\n\n"

        f"📦 <b>Product:</b>\n"
        f"{order['product_name']}\n\n"

        f"🔢 <b>Quantity:</b> {quantity}\n"

        f"💰 <b>Price:</b> "
        f"₹{order['price_per_item']} / item\n"

        f"💵 <b>Total:</b> ₹{total_amount}\n\n"

        "━━━━━━━━━━━━━━━━━━\n"

        "💳 <b>PAYMENT INSTRUCTIONS</b>\n\n"

        "1️⃣ Scan the QR code below.\n"
        "2️⃣ Pay the exact amount shown above.\n"
        "3️⃣ Keep your payment confirmation ready.\n\n"

        "🔐 <b>Payment Verification</b>\n"
        "Our payment-verification workflow will process "
        "your screenshot and UTR after submission.\n\n"

        "⚠️ Do not send a fake or edited payment proof."
    )

    if update.callback_query:

        message = update.callback_query.message

        await message.edit_text(
            summary,
            parse_mode="HTML"
        )

    else:

        message = update.message

        await message.reply_text(
            summary,
            parse_mode="HTML"
        )

    # ========================================
    # SEND QR
    # ========================================

    try:

        with open(
            QR_IMAGE,
            "rb"
        ) as qr_file:

            await message.reply_photo(
                qr_file,
                caption=(
                    "💳 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐐𝐑\n\n"
                    f"Amount: ₹{total_amount}\n"
                    "Please pay the exact amount."
                )
            )

    except FileNotFoundError:

        await message.reply_text(
            "⚠️ <b>QR unavailable</b>\n\n"
            "Please contact support before making payment.",
            parse_mode="HTML"
        )

        return WAITING_FOR_SCREENSHOT

    # ========================================
    # SCREENSHOT REQUEST
    # ========================================

    keyboard = [[

        InlineKeyboardButton(
            "💬 Contact Support",
            url=f"https://t.me/{SUPPORT_USERNAME}"
        )

    ]]

    await message.reply_text(
        "📸 <b>𝐍𝐄𝐗𝐓 𝐒𝐓𝐄𝐏</b>\n\n"
        "After completing payment, send your "
        "<b>payment screenshot</b> here.\n\n"
        "🔢 After the screenshot, the bot will ask "
        "you for your <b>UTR / Transaction ID</b>.\n\n"
        "⚠️ Please send the original payment proof.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return WAITING_FOR_SCREENSHOT


# ============================================
# CUSTOM QUANTITY TEXT
# ============================================

async def handle_quantity(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    # Important:
    # Permanent menu handlers are registered BEFORE
    # this generic text handler.

    if not await is_user_joined(
        update,
        context
    ):

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    user_id = update.effective_user.id

    if user_id not in current_orders:

        await update.message.reply_text(
            "❌ <b>No active order.</b>\n\n"
            "Please select a product first.",
            parse_mode="HTML"
        )

        return SELECTING_PRODUCT

    order = current_orders[user_id]

    try:

        quantity = int(
            update.message.text.strip()
        )

    except ValueError:

        await update.message.reply_text(
            "❌ <b>Invalid quantity</b>\n\n"
            f"Minimum quantity: <b>{order['min_qty']}</b>\n"
            "Please enter numbers only.",
            parse_mode="HTML"
        )

        return ENTERING_QUANTITY

    if quantity < order["min_qty"]:

        await update.message.reply_text(
            "❌ <b>Quantity too low</b>\n\n"
            f"Minimum quantity: <b>{order['min_qty']}</b>",
            parse_mode="HTML"
        )

        return ENTERING_QUANTITY

    return await process_quantity(
        update,
        context,
        quantity
    )


# ============================================
# PAYMENT SCREENSHOT
# ============================================

async def handle_screenshot(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    if not await is_user_joined(
        update,
        context
    ):

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    user_id = update.effective_user.id

    if user_id not in current_orders:

        await update.message.reply_text(
            "❌ <b>No active order.</b>\n\n"
            "Please start again.",
            parse_mode="HTML"
        )

        return ConversationHandler.END

    order = current_orders[user_id]

    photo_file = update.message.photo[-1]

    # Store screenshot temporarily
    order["screenshot_file_id"] = photo_file.file_id

    await update.message.reply_text(
        "📸 <b>Screenshot received! ✅</b>\n\n"
        "Now send your <b>UTR / Transaction ID</b>.\n\n"
        "🔢 Example: <code>123456789012</code>\n\n"
        "Your screenshot and UTR will be submitted "
        "together for payment verification.",
        parse_mode="HTML"
    )

    return WAITING_FOR_UTR


# ============================================
# UTR / TRANSACTION ID
# ============================================

async def handle_utr(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    if not await is_user_joined(
        update,
        context
    ):

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    user_id = update.effective_user.id

    if user_id not in current_orders:

        await update.message.reply_text(
            "❌ <b>No active order.</b>\n\n"
            "Please start again.",
            parse_mode="HTML"
        )

        return ConversationHandler.END

    order = current_orders[user_id]

    utr = update.message.text.strip()

    # Remove spaces
    clean_utr = utr.replace(" ", "")

    # Basic validation
    if not re.fullmatch(
        r"[A-Za-z0-9]{6,30}",
        clean_utr
    ):

        await update.message.reply_text(
            "❌ <b>Invalid UTR / Transaction ID</b>\n\n"
            "Please send a valid UTR / Transaction ID "
            "using letters and numbers only.\n\n"
            "Example:\n"
            "<code>123456789012</code>",
            parse_mode="HTML"
        )

        return WAITING_FOR_UTR

    order["utr"] = clean_utr

    # ========================================
    # ADMIN PAYMENT PACKAGE
    # ========================================

    admin_caption = (
        "🔔 <b>𝐍𝐄𝐖 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐒𝐔𝐁𝐌𝐈𝐒𝐒𝐈𝐎𝐍</b>\n\n"

        f"👤 <b>User ID:</b> "
        f"<code>{user_id}</code>\n\n"

        f"📦 <b>Product:</b>\n"
        f"{order['product_name']}\n\n"

        f"🔢 <b>Quantity:</b> "
        f"{order['quantity']}\n"

        f"💰 <b>Price/item:</b> "
        f"₹{order['price_per_item']}\n"

        f"💵 <b>Total:</b> "
        f"₹{order['total_amount']}\n\n"

        f"🔢 <b>UTR / Transaction ID:</b>\n"
        f"<code>{clean_utr}</code>\n\n"

        "🔐 <b>Status:</b> Verification Pending"
    )

    try:

        # Send screenshot with complete payment details
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=order["screenshot_file_id"],
            caption=admin_caption,
            parse_mode="HTML"
        )

    except Exception as e:

        logger.error(
            f"Failed to send payment submission: {e}"
        )

        await update.message.reply_text(
            "⚠️ <b>Submission failed</b>\n\n"
            "We couldn't submit your payment proof "
            "right now. Please contact support.",
            parse_mode="HTML"
        )

        return WAITING_FOR_UTR

    # ========================================
    # SAVE HISTORY
    # ========================================

    if user_id not in order_history:

        order_history[user_id] = []

    order_history[user_id].append({

        "product": order["product_name"],

        "quantity": order["quantity"],

        "total": order["total_amount"],

        "utr": clean_utr

    })

    # ========================================
    # USER CONFIRMATION
    # ========================================

    confirm = (
        "🔐 <b>𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐒𝐔𝐁𝐌𝐈𝐓𝐓𝐄𝐃</b>\n\n"

        "📸 Screenshot: <b>Received</b> ✅\n"
        "🔢 UTR: <b>Received</b> ✅\n\n"

        "🤖 <b>Payment verification workflow initiated.</b>\n\n"

        "Your payment details have been submitted "
        "for verification.\n\n"

        "⏳ Please wait for verification/order processing.\n\n"

        f"💬 Support: @{SUPPORT_USERNAME}"
    )

    keyboard = [[

        InlineKeyboardButton(
            "💬 Contact Support",
            url=f"https://t.me/{SUPPORT_USERNAME}"
        )

    ]]

    await update.message.reply_text(
        confirm,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    # Clear active order
    del current_orders[user_id]

    return ConversationHandler.END


# ============================================
# HISTORY
# ============================================

async def show_history(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    if not await is_user_joined(
        update,
        context
    ):

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    user_id = update.effective_user.id

    history = order_history.get(
        user_id,
        []
    )

    if not history:

        text = (
            "📜 <b>𝐎𝐑𝐃𝐄𝐑 𝐇𝐈𝐒𝐓𝐎𝐑𝐘</b>\n\n"
            "You don't have any submitted orders yet. 🛍️"
        )

    else:

        text = (
            "📜 <b>𝐎𝐑𝐃𝐄𝐑 𝐇𝐈𝐒𝐓𝐎𝐑𝐘</b>\n\n"
        )

        for index, order in enumerate(
            history[-10:],
            start=1
        ):

            text += (
                f"<b>{index}. {order['product']}</b>\n"
                f"🔢 Quantity: {order['quantity']}\n"
                f"💵 Amount: ₹{order['total']}\n"
                f"🔐 UTR: <code>{order['utr']}</code>\n\n"
            )

    await update.message.reply_text(
        text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

    return SELECTING_PRODUCT


# ============================================
# DISCLAIMER
# ============================================

async def show_disclaimer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    if not await is_user_joined(
        update,
        context
    ):

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    text = (
        "ℹ️ <b>𝐊𝐍𝐎𝐗 𝐒𝐓𝐎𝐑𝐄 — 𝐃𝐈𝐒𝐂𝐋𝐀𝐈𝐌𝐄𝐑</b>\n\n"

        "🛍️ <b>Orders</b>\n"
        "All orders are subject to product availability "
        "and successful payment verification.\n\n"

        "💳 <b>Payment</b>\n"
        "Please pay only the exact amount shown by the bot. "
        "Always keep your payment confirmation.\n\n"

        "📸 <b>Payment Proof</b>\n"
        "A clear payment screenshot and valid "
        "UTR / Transaction ID are required.\n\n"

        "🤖 <b>Automated Verification Workflow</b>\n"
        "Submitted payment details enter the payment "
        "verification workflow. Do not consider an order "
        "confirmed until verification is completed.\n\n"

        "🔐 <b>Important</b>\n"
        "Never share your UPI PIN, OTP, password or "
        "other sensitive banking credentials.\n\n"

        f"💬 <b>Support:</b> @{SUPPORT_USERNAME}"
    )

    await update.message.reply_text(
        text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

    return SELECTING_PRODUCT


# ============================================
# SUPPORT
# ============================================

async def show_support(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    if not await is_user_joined(
        update,
        context
    ):

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    text = (
        "💬 <b>𝐊𝐍𝐎𝐗 𝐒𝐓𝐎𝐑𝐄 𝐒𝐔𝐏𝐏𝐎𝐑𝐓</b>\n\n"

        "Need help with an order, payment or voucher?\n\n"

        "📌 Please keep your Order details and "
        "UTR ready when contacting support.\n\n"

        f"👤 <b>Support:</b> @{SUPPORT_USERNAME}"
    )

    keyboard = [[

        InlineKeyboardButton(
            "💬 Contact Support",
            url=f"https://t.me/{SUPPORT_USERNAME}"
        )

    ]]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return SELECTING_PRODUCT


# ============================================
# JOIN CHANNEL
# ============================================

async def join_channel_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    keyboard = [

        [
            InlineKeyboardButton(
                "📢 Open Channel",
                url=FORCE_JOIN_LINK
            )
        ],

        [
            InlineKeyboardButton(
                "✅ Check Membership",
                callback_data="check_force_join"
            )
        ]

    ]

    text = (
        "📢 <b>𝐊𝐍𝐎𝐗 𝐒𝐓𝐎𝐑𝐄 𝐔𝐏𝐃𝐀𝐓𝐄𝐒</b>\n\n"
        "Get the latest store updates, "
        "new products and availability notifications.\n\n"
        "👇 Join our official channel:"
    )

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return SELECTING_PRODUCT


# ============================================
# BACK TO MAIN
# ============================================

async def back_to_main(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    query = update.callback_query

    await query.answer()

    if not await is_user_joined(
        update,
        context
    ):

        await show_force_join(
            update,
            context
        )

        return SELECTING_PRODUCT

    text = (
        "🖤 <b>𝐊𝐍𝐎𝐗 𝐒𝐓𝐎𝐑𝐄</b>\n\n"
        "Choose an option from the menu below 👇"
    )

    await query.message.reply_text(
        text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

    return SELECTING_PRODUCT


# ============================================
# CANCEL
# ============================================

async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    user_id = update.effective_user.id

    if user_id in current_orders:

        del current_orders[user_id]

    await update.message.reply_text(
        "❌ <b>Order process cancelled.</b>\n\n"
        "You can start again anytime from the menu.",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

    return ConversationHandler.END


# ============================================
# COMMON MENU HANDLERS
# ============================================

def get_menu_handlers():

    return [

        MessageHandler(
            filters.Regex(r"^🛍️ Buy Voucher$"),
            buy_voucher
        ),

        MessageHandler(
            filters.Regex(r"^📜 History$"),
            show_history
        ),

        MessageHandler(
            filters.Regex(r"^💬 Support$"),
            show_support
        ),

        MessageHandler(
            filters.Regex(r"^ℹ️ Disclaimer$"),
            show_disclaimer
        ),

        MessageHandler(
            filters.Regex(r"^📢 Join Channel$"),
            join_channel_button
        )

    ]


# ============================================
# MAIN
# ============================================

def main():

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )


    # ========================================
    # CONVERSATION HANDLER
    # ========================================

    conv_handler = ConversationHandler(

        entry_points=[

            CommandHandler(
                "start",
                start
            )

        ],

        states={


            # =================================
            # SELECTING PRODUCT
            # =================================

            SELECTING_PRODUCT: [

                # Permanent menu
                *get_menu_handlers(),

                # Inline product buttons
                CallbackQueryHandler(
                    show_products,
                    pattern="^show_products$"
                ),

                CallbackQueryHandler(
                    select_product,
                    pattern="^select_"
                ),

                CallbackQueryHandler(
                    back_to_main,
                    pattern="^back_to_main$"
                ),

                CommandHandler(
                    "start",
                    start
                )

            ],


            # =================================
            # ENTERING QUANTITY
            # =================================

            ENTERING_QUANTITY: [

                # IMPORTANT:
                # Menu handlers come BEFORE generic
                # text quantity handler.

                *get_menu_handlers(),

                # Inline quantity
                CallbackQueryHandler(
                    select_quantity,
                    pattern="^qty_"
                ),

                # Custom quantity
                CallbackQueryHandler(
                    custom_quantity,
                    pattern="^custom_quantity$"
                ),

                # Back to quantity
                CallbackQueryHandler(
                    back_to_quantity,
                    pattern="^back_to_quantity$"
                ),

                # Back to products
                CallbackQueryHandler(
                    show_products,
                    pattern="^show_products$"
                ),

                # Typed custom quantity
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_quantity
                ),

                CommandHandler(
                    "start",
                    start
                )

            ],


            # =================================
            # WAITING FOR SCREENSHOT
            # =================================

            WAITING_FOR_SCREENSHOT: [

                # IMPORTANT:
                # Permanent buttons also work here.

                *get_menu_handlers(),

                # Payment screenshot
                MessageHandler(
                    filters.PHOTO,
                    handle_screenshot
                ),

                CallbackQueryHandler(
                    show_products,
                    pattern="^show_products$"
                ),

                CommandHandler(
                    "start",
                    start
                )

            ],


            # =================================
            # WAITING FOR UTR
            # =================================

            WAITING_FOR_UTR: [

                # Permanent buttons also work here.

                *get_menu_handlers(),

                # UTR text
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_utr
                ),

                CommandHandler(
                    "start",
                    start
                )

            ]

        },


        # ====================================
        # FALLBACKS
        # ====================================

        fallbacks=[

            CommandHandler(
                "start",
                start
            ),

            CommandHandler(
                "cancel",
                cancel
            )

        ]

    )


    # ========================================
    # ADD CONVERSATION HANDLER
    # ========================================

    app.add_handler(
        conv_handler
    )


    # ========================================
    # FORCE JOIN CALLBACK
    # ========================================

    app.add_handler(
        CallbackQueryHandler(
            force_join_callback,
            pattern="^check_force_join$"
        )
    )


    # ========================================
    # START BOT
    # ========================================

    print("🤖 KNOX STORE Bot starting...")
    print("✅ Permanent keyboard enabled")
    print("✅ Force Join enabled")
    print("✅ Quantity buttons enabled")
    print("✅ Screenshot + UTR verification flow enabled")
    print("Press Ctrl+C to stop.")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    main()
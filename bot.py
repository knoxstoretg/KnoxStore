#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
KNOX STORE Telegram Bot
python-telegram-bot v20.7 compatible
"""

import logging

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

# IMPORTANT:
# Use @ before the public channel username.
#
# Example:
# @KnoxStoreUpdates

FORCE_JOIN_CHANNEL = "@KnoxStoreUpdates"

FORCE_JOIN_LINK = "https://t.me/KnoxStoreUpdates"


# ============================================
# PRODUCTS
# ============================================

PRODUCTS = {

    "amul_100": {
        "name": "🧀 Amul ₹100 Coupon",
        "price": 20,
        "min_qty": 2
    },

    "amul_100_bulk": {
        "name": "🧀 Amul ₹100 Bulk Coupon",
        "price": 15,
        "min_qty": 5
    },

    "flipkart_249": {
        "name": "🛒 Flipkart ₹249 Gift Voucher",
        "price": 79,
        "min_qty": 1
    },

    "flipkart_499": {
        "name": "🛒 Flipkart ₹499 Gift Voucher",
        "price": 149,
        "min_qty": 1
    },

    "dominos_100": {
        "name": "🍕 Domino's ₹100 Gift Voucher",
        "price": 25,
        "min_qty": 2
    },

    "bookmyshow_499": {
        "name": "🎬 BookMyShow ₹499 Gift Card",
        "price": 149,
        "min_qty": 1
    },

    "pvr_200": {
        "name": "🎞 PVR ₹200 Movie Voucher",
        "price": 50,
        "min_qty": 1
    },

    "blinkit_499": {
        "name": "🛍️ Blinkit ₹499 Coupon",
        "price": 149,
        "min_qty": 1
    },

    "bigbasket_249": {
        "name": "🛒 BigBasket ₹249 Gift Voucher",
        "price": 79,
        "min_qty": 1
    },

    "swiggy_249": {
        "name": "🍔 Swiggy ₹249 Coupon",
        "price": 79,
        "min_qty": 1
    },

    "zomato_249": {
        "name": "🍔 Zomato ₹249 Gift Voucher",
        "price": 79,
        "min_qty": 1
    },

    "shein_800": {
        "name": "👗 SHEIN ₹800 off on ₹1000",
        "price": 50,
        "min_qty": 2
    }
}


# ============================================
# STATES
# ============================================

SELECTING_PRODUCT, ENTERING_QUANTITY, WAITING_FOR_SCREENSHOT = range(3)


# ============================================
# TEMPORARY STORAGE
# ============================================

current_orders = {}

# User order history
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

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "🔒 <b>Join Our Channel First</b>\n\n"
        "KNOX STORE use karne ke liye pehle "
        "hamare updates channel ko join karo.\n\n"
        "Channel join karne ke baad "
        "<b>I've Joined</b> button press karo. 👇"
    )

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
        "🖤 <b>Welcome to KNOX STORE</b>\n\n"
        "Choose an option from the menu below 👇"
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

    # Clear old order
    if user.id in current_orders:
        del current_orders[user.id]

    # Force Join
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
            "❌ Pehle channel join karo!",
            show_alert=True
        )

        return

    await query.answer(
        "✅ Verified!"
    )

    text = (
        "🖤 <b>Welcome to KNOX STORE</b>\n\n"
        "Channel verification successful! ✅\n\n"
        "Choose an option from the menu below 👇"
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
        "🛒 <b>Available Coupons & Gift Cards</b>\n\n"
        "Select a product to purchase:"
    )

    keyboard = []

    for product_id, product in PRODUCTS.items():

        button_text = (
            f"{product['name']} - ₹{product['price']}"
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
        "🛒 <b>Available Coupons & Gift Cards</b>\n\n"
        "Select a product to purchase:"
    )

    keyboard = []

    for product_id, product in PRODUCTS.items():

        button_text = (
            f"{product['name']} - ₹{product['price']}"
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
        f"<b>{product['name']}</b>\n\n"
        f"💰 Price: ₹{product['price']} per item\n"
        f"📦 Minimum quantity: {min_qty}\n\n"
        "🔢 <b>Select Quantity:</b>"
    )

    # Minimum + next 3
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
            f"Minimum quantity is {order['min_qty']}",
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
        "✏️ <b>Custom Quantity</b>\n\n"
        f"📦 Minimum quantity: <b>{min_qty}</b>\n\n"
        "Please type your required quantity:"
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
        f"<b>{order['product_name']}</b>\n\n"
        f"💰 Price: ₹{order['price_per_item']} per item\n"
        f"📦 Minimum quantity: {min_qty}\n\n"
        "🔢 <b>Select Quantity:</b>"
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
            "❌ No active order. Use /start"
        )

        return ConversationHandler.END

    order = current_orders[user_id]

    if quantity < order["min_qty"]:

        if update.callback_query:

            await update.callback_query.answer(
                f"Minimum quantity is {order['min_qty']}",
                show_alert=True
            )

        return ENTERING_QUANTITY

    total_amount = (
        order["price_per_item"] * quantity
    )

    order["quantity"] = quantity

    order["total_amount"] = total_amount

    summary = (
        "🛒 <b>Order Summary</b>\n\n"

        f"📦 Product: {order['product_name']}\n"

        f"🔢 Quantity: {quantity}\n"

        f"💰 Price per item: "
        f"₹{order['price_per_item']}\n"

        f"💵 Total Amount: ₹{total_amount}\n\n"

        "Please scan the QR below and make the payment.\n\n"

        "After payment, send the payment screenshot here."
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
    # QR
    # ========================================

    try:

        with open(
            QR_IMAGE,
            "rb"
        ) as qr_file:

            await message.reply_photo(
                qr_file,
                caption="📲 Scan this QR code to make payment"
            )

    except FileNotFoundError:

        await message.reply_text(
            "⚠️ QR code image not found. "
            "Please contact support."
        )

    # ========================================
    # BACK BUTTON
    # ========================================

    keyboard = [[

        InlineKeyboardButton(
            "⬅️ Back to Products",
            callback_data="show_products"
        )

    ]]

    await message.reply_text(
        "Or browse more products:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return WAITING_FOR_SCREENSHOT


# ============================================
# CUSTOM QUANTITY TEXT
# ============================================

async def handle_quantity(
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
            "❌ No active order. Use /start"
        )

        return ConversationHandler.END

    order = current_orders[user_id]

    try:

        quantity = int(
            update.message.text.strip()
        )

    except ValueError:

        await update.message.reply_text(
            f"❌ Please enter a valid number.\n\n"
            f"Minimum quantity: {order['min_qty']}"
        )

        return ENTERING_QUANTITY

    if quantity < order["min_qty"]:

        await update.message.reply_text(
            f"❌ Minimum quantity is "
            f"{order['min_qty']}."
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
            "❌ No active order. Use /start"
        )

        return ConversationHandler.END

    order = current_orders[user_id]

    photo_file = update.message.photo[-1]

    # ========================================
    # ADMIN MESSAGE
    # ========================================

    admin_msg = (
        "🆕 <b>New Payment Screenshot</b>\n\n"

        f"👤 User ID: <code>{user_id}</code>\n"

        f"📦 Product: {order['product_name']}\n"

        f"🔢 Quantity: {order['quantity']}\n"

        f"💰 Price per item: "
        f"₹{order['price_per_item']}\n"

        f"💵 Total Amount: "
        f"₹{order['total_amount']}"
    )

    try:

        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=photo_file.file_id,
            caption=admin_msg,
            parse_mode="HTML"
        )

    except Exception as e:

        logger.error(
            f"Failed to send screenshot to admin: {e}"
        )

    # ========================================
    # SAVE HISTORY
    # ========================================

    if user_id not in order_history:

        order_history[user_id] = []

    order_history[user_id].append({

        "product": order["product_name"],

        "quantity": order["quantity"],

        "total": order["total_amount"]

    })

    # ========================================
    # USER CONFIRMATION
    # ========================================

    confirm = (
        "✅ <b>Payment screenshot received!</b>\n\n"

        "Please contact our support to receive "
        "your order.\n\n"

        f"💬 @{SUPPORT_USERNAME}\n\n"

        "Tap the Support button below 👇"
    )

    keyboard = [[

        InlineKeyboardButton(
            "💬 Support",
            url=f"https://t.me/{SUPPORT_USERNAME}"
        )

    ]]

    await update.message.reply_text(
        confirm,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    # Clear order
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
            "📜 <b>Your Order History</b>\n\n"
            "No completed orders found yet."
        )

    else:

        text = (
            "📜 <b>Your Order History</b>\n\n"
        )

        # Show latest 10
        for index, order in enumerate(
            history[-10:],
            start=1
        ):

            text += (
                f"<b>{index}.</b> "
                f"{order['product']}\n"
                f"🔢 Qty: {order['quantity']}\n"
                f"💵 Amount: ₹{order['total']}\n\n"
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
        "ℹ️ <b>KNOX STORE Disclaimer</b>\n\n"

        "• All orders are subject to availability.\n"

        "• Please verify the product and quantity "
        "before making payment.\n"

        "• Payment screenshots are reviewed by our "
        "support team.\n"

        "• For any issue, contact support.\n\n"

        "💬 Support: "
        f"@{SUPPORT_USERNAME}"
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
        "💬 <b>KNOX STORE Support</b>\n\n"
        "For orders, payment issues or any "
        "other help, contact our support:"
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
# JOIN CHANNEL BUTTON
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
        "📢 <b>KNOX STORE Updates</b>\n\n"
        "Latest updates, new vouchers and "
        "availability yahan milegi."
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
        "🖤 <b>KNOX STORE</b>\n\n"
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
        "❌ Operation cancelled.\n\n"
        "Use the menu below to continue.",
        reply_markup=get_main_keyboard()
    )

    return ConversationHandler.END


# ============================================
# UNEXPECTED MESSAGE
# ============================================

async def handle_unexpected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "Please use the buttons below 👇",
        reply_markup=get_main_keyboard()
    )


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
            # MAIN MENU
            # =================================

            SELECTING_PRODUCT: [

                # Permanent keyboard buttons

                MessageHandler(
                    filters.Regex(
                        "^🛍️ Buy Voucher$"
                    ),
                    buy_voucher
                ),

                MessageHandler(
                    filters.Regex(
                        "^📜 History$"
                    ),
                    show_history
                ),

                MessageHandler(
                    filters.Regex(
                        "^💬 Support$"
                    ),
                    show_support
                ),

                MessageHandler(
                    filters.Regex(
                        "^ℹ️ Disclaimer$"
                    ),
                    show_disclaimer
                ),

                MessageHandler(
                    filters.Regex(
                        "^📢 Join Channel$"
                    ),
                    join_channel_button
                ),


                # Inline product callbacks

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
            # QUANTITY
            # =================================

            ENTERING_QUANTITY: [

                CallbackQueryHandler(
                    select_quantity,
                    pattern="^qty_"
                ),

                CallbackQueryHandler(
                    custom_quantity,
                    pattern="^custom_quantity$"
                ),

                CallbackQueryHandler(
                    back_to_quantity,
                    pattern="^back_to_quantity$"
                ),

                CallbackQueryHandler(
                    show_products,
                    pattern="^show_products$"
                ),

                # Custom quantity typed by user

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
            # WAITING SCREENSHOT
            # =================================

            WAITING_FOR_SCREENSHOT: [

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
    # ADD HANDLERS
    # ========================================

    app.add_handler(
        conv_handler
    )


    # Force Join verification callback
    app.add_handler(
        CallbackQueryHandler(
            force_join_callback,
            pattern="^check_force_join$"
        )
    )


    # ========================================
    # START
    # ========================================

    print("🤖 KNOX STORE Bot starting...")

    print("Permanent Reply Keyboard enabled.")

    print("Press Ctrl+C to stop.")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    main()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
KNOX STORE Telegram Bot
python-telegram-bot v20.7 compatible
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# ============================================
# CONFIGURATION - YEH BADLO
# ============================================

BOT_TOKEN = "8768230830:AAHamryLyN0FzEYbn-Da3OdlmkOwOTq-qkQ"
ADMIN_CHAT_ID = 8925766938
SUPPORT_USERNAME = "KNOX_STORE_SUPPORT"
QR_IMAGE = "qr.jpg"

PRODUCTS = {
    "amul_100": {
        "name": "🧀 Amul ₹100 Coupon",
        "price": 20,
        "min_qty": 3
    },
    "amul_100_bulk": {
        "name": "🧀 Amul ₹100 Bulk Coupon",
        "price": 15,
        "min_qty": 10
    },
    "bookmyshow_499": {
        "name": "🎬 BookMyShow ₹499 Gift Card",
        "price": 199,
        "min_qty": 1
    },
    "blinkit_499": {
        "name": "🛍️ Blinkit ₹499 Coupon",
        "price": 199,
        "min_qty": 1
    },
    "swiggy_499": {
        "name": "🍔 Swiggy ₹499 Coupon",
        "price": 199,
        "min_qty": 1
    },
    "shein_800": {
        "name": "👗 SHEIN ₹800 off on ₹1000",
        "price": 50,
        "min_qty": 2
    }
}

# ============================================
# BOT STATES
# ============================================

SELECTING_PRODUCT, ENTERING_QUANTITY, WAITING_FOR_SCREENSHOT = range(3)

# Temporary storage (memory only)
current_orders = {}

# ============================================
# LOGGING
# ============================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# BOT FUNCTIONS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show main menu - Always shows menu when /start is pressed"""
    user = update.effective_user
    
    # Clear old order
    if user.id in current_orders:
        del current_orders[user.id]
    
    welcome_text = "Welcome to KNOX STORE 🖤\n\nChoose an option below:"
    
    keyboard = [
        [InlineKeyboardButton("🛒 Coupons", callback_data="show_products")],
        [InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    return SELECTING_PRODUCT

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display product list"""
    query = update.callback_query
    await query.answer()
    
    text = "🛒 *Available Coupons & Gift Cards*\n\nSelect a product to purchase:"
    
    keyboard = []
    for product_id, product in PRODUCTS.items():
        btn_text = f"{product['name']} - ₹{product['price']}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"select_{product_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    return SELECTING_PRODUCT

async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for quantity"""
    query = update.callback_query
    await query.answer()
    
    product_id = query.data.replace("select_", "")
    
    if product_id in PRODUCTS:
        product = PRODUCTS[product_id]
        user_id = update.effective_user.id
        
        # Save to temporary memory
        current_orders[user_id] = {
            "product_id": product_id,
            "product_name": product["name"],
            "price_per_item": product["price"],
            "min_qty": product["min_qty"]
        }
        
        text = f"*{product['name']}*\n\n"
        text += f"Price: ₹{product['price']} per item\n"
        text += f"Minimum quantity: {product['min_qty']}\n\n"
        text += f"How many do you want?\n\n"
        text += f"Minimum quantity: {product['min_qty']}"
        
        keyboard = [[InlineKeyboardButton("⬅️ Back to Products", callback_data="show_products")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        return ENTERING_QUANTITY
    
    return SELECTING_PRODUCT

async def handle_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process quantity input"""
    user_id = update.effective_user.id
    
    if user_id not in current_orders:
        await update.message.reply_text("No active order. Use /start")
        return ConversationHandler.END
    
    order = current_orders[user_id]
    
    try:
        quantity = int(update.message.text)
    except ValueError:
        await update.message.reply_text(
            f"Please enter a valid quantity.\n\n"
            f"Minimum quantity for this product: {order['min_qty']}"
        )
        return ENTERING_QUANTITY
    
    if quantity < order['min_qty']:
        await update.message.reply_text(
            f"Please enter a valid quantity.\n\n"
            f"Minimum quantity for this product: {order['min_qty']}"
        )
        return ENTERING_QUANTITY
    
    total_amount = order['price_per_item'] * quantity
    order['quantity'] = quantity
    order['total_amount'] = total_amount
    
    summary = "Order Summary 🛒\n\n"
    summary += f"Product: {order['product_name']}\n"
    summary += f"Quantity: {quantity}\n"
    summary += f"Price per item: ₹{order['price_per_item']}\n"
    summary += f"Total Amount: ₹{total_amount}\n\n"
    summary += "Please scan the QR below and make the payment.\n\n"
    summary += "After payment, send the payment screenshot here."
    
    await update.message.reply_text(summary)
    
    # Send QR image
    try:
        with open(QR_IMAGE, 'rb') as qr_file:
            await update.message.reply_photo(qr_file, caption="Scan this QR code to make payment")
    except FileNotFoundError:
        await update.message.reply_text("⚠️ QR code image not found. Please contact support.")
    
    # Back button
    keyboard = [[InlineKeyboardButton("⬅️ Back to Products", callback_data="show_products")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Or go back to browse more products:", reply_markup=reply_markup)
    
    return WAITING_FOR_SCREENSHOT

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process payment screenshot"""
    user_id = update.effective_user.id
    
    if user_id not in current_orders:
        await update.message.reply_text("No active order. Use /start")
        return ConversationHandler.END
    
    order = current_orders[user_id]
    photo_file = update.message.photo[-1]
    
    # Forward to admin
    admin_msg = "New Payment Screenshot 📸\n\n"
    admin_msg += f"Product: {order['product_name']}\n"
    admin_msg += f"Quantity: {order['quantity']}\n"
    admin_msg += f"Price per item: ₹{order['price_per_item']}\n"
    admin_msg += f"Total Amount: ₹{order['total_amount']}"
    
    try:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=photo_file.file_id,
            caption=admin_msg
        )
    except Exception as e:
        logger.error(f"Failed to send to admin: {e}")
    
    # Confirm to user
    confirm = "Payment screenshot received ✅\n\n"
    confirm += f"Please contact our support to receive your order:\n\n"
    confirm += f"@{SUPPORT_USERNAME}\n\n"
    confirm += "Tap the Support button below 👇"
    
    keyboard = [[InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_USERNAME}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(confirm, reply_markup=reply_markup)
    
    # Clear order
    del current_orders[user_id]
    
    return ConversationHandler.END

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to main menu"""
    query = update.callback_query
    await query.answer()
    
    welcome_text = "Welcome to KNOX STORE 🖤\n\nChoose an option below:"
    
    keyboard = [
        [InlineKeyboardButton("🛒 Coupons", callback_data="show_products")],
        [InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(welcome_text, reply_markup=reply_markup)
    return SELECTING_PRODUCT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel operation"""
    user_id = update.effective_user.id
    if user_id in current_orders:
        del current_orders[user_id]
    
    await update.message.reply_text("Operation cancelled. Use /start to begin again.")
    return ConversationHandler.END

async def handle_unexpected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle random messages"""
    await update.message.reply_text("I didn't understand that. Use /start to see the main menu.")

# ============================================
# MAIN
# ============================================

def main():
    """Start bot"""
    # Create Application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_PRODUCT: [
                CallbackQueryHandler(show_products, pattern='^show_products$'),
                CallbackQueryHandler(select_product, pattern='^select_'),
                CallbackQueryHandler(back_to_main, pattern='^back_to_main$'),
            ],
            ENTERING_QUANTITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quantity),
                CallbackQueryHandler(show_products, pattern='^show_products$'),
                CommandHandler('start', start),  # Added this line!
            ],
            WAITING_FOR_SCREENSHOT: [
                MessageHandler(filters.PHOTO, handle_screenshot),
                CallbackQueryHandler(show_products, pattern='^show_products$'),
                CommandHandler('start', start),  # Added this line!
            ],
        },
        fallbacks=[
            CommandHandler('start', start),  # Added this line!
            CommandHandler('cancel', cancel)
        ],
    )
    
    # Add handlers
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unexpected))
    
    # Start bot
    print("🤖 KNOX STORE Bot starting...")
    print("Press Ctrl+C to stop")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
# ✅ Telegram Bot – PythonAnywhere Ready Version (Webhook-Based)

import logging
import telegram
from telegram import Update
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, ConversationHandler, filters
)
from flask import Flask, request

# Enable logging
logging.basicConfig(level=logging.INFO)

# States for the conversation
(ASK_NAME, ASK_CITY, ASK_PROFILE_INFO, ASK_USER_INFO, GENERATE_MESSAGE) = range(5)

TOKEN = "7292650026:AAHDUkoGALoTxRoWeWArfI2Hcg_JWZjMiAs"  # 🔐 Replace this with your real bot token
BOT = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# --- AI Conversation Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "👋 Hi! I’ll help you craft a respectful, interesting message for a girl you're talking to.\n\nFirst, what’s her name (or initials)?"
    )
    return ASK_NAME

async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['girl_name'] = update.message.text.strip()
    await update.message.reply_text("📍 Which city is she currently in?")
    return ASK_CITY

async def ask_profile_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['girl_city'] = update.message.text.strip()
    await update.message.reply_text("📸 What do you know about her from her profile? Any posts, hobbies, or favorite places?")
    return ASK_PROFILE_INFO

async def ask_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['girl_profile'] = update.message.text.strip()
    await update.message.reply_text("🙋‍♂️ Tell me 1-2 things about you that can be used in the chat (like you also like that place or a similar hobby)")
    return ASK_USER_INFO

async def generate_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user_info'] = update.message.text.strip()

    name = context.user_data['girl_name']
    city = context.user_data['girl_city']
    profile = context.user_data['girl_profile']
    user = context.user_data['user_info']

    message = (
        f"hey {name.lower()} 👋\n"
        f"mujhe laga tumne {profile} post ki thi na?\n"
        f"main bhi {user} karta hoon, to laga baat shuru karu 😅\n"
        f"btw {city} mein aur kya achha lagta hai aapko?"
    )

    await update.message.reply_text("✅ Here's a respectful message you can send:\n\n" + message)
    await update.message.reply_text("If you'd like to try again, type /start")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Conversation cancelled. Type /start to begin again.")
    return ConversationHandler.END

# --- Flask Webhook Setup ---

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), BOT)
    application.update_queue.put(update)
    return 'ok'

@app.route('/')
def index():
    return 'Telegram bot is running via webhook!'

# --- Telegram Bot Setup ---

application = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_city)],
        ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_profile_info)],
        ASK_PROFILE_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_user_info)],
        ASK_USER_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_reply)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handler(conv_handler)

# --- Set Webhook When First Run ---
import asyncio
asyncio.run(BOT.set_webhook(f"https://<flirtai.pythonanywhere.com/{TOKEN}"))
  

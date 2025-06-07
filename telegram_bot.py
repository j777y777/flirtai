# telegram_bot.py

import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters, ConversationHandler
)
import httpx
import asyncio

# --- SECRETS (PASTED DIRECTLY) ---
TOKEN = "7292650026:AAHDUkoGALoTxRoWeWArfI2Hcg_JWZjMiAs"
OPENROUTER_API_KEY = "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"
MODEL = "openai/gpt-3.5-turbo"

# Logging
logging.basicConfig(level=logging.INFO)

# Telegram conversation states
ASK_NAME, ASK_CITY, ASK_PROFILE_INFO, ASK_USER_INFO = range(4)

# Initialize Telegram application
application = ApplicationBuilder().token(TOKEN).build()

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("👋 What’s the girl's name (or initials)?")
    return ASK_NAME

async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['girl_name'] = update.message.text.strip()
    await update.message.reply_text("📍 Which city is she in?")
    return ASK_CITY

async def ask_profile_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['girl_city'] = update.message.text.strip()
    await update.message.reply_text("📸 Any profile hobbies, highlights or favorite things?")
    return ASK_PROFILE_INFO

async def ask_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['girl_profile'] = update.message.text.strip()
    await update.message.reply_text("🙋‍♂️ One or two things about yourself we can use?")
    return ASK_USER_INFO

async def generate_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user_info'] = update.message.text.strip()

    name = context.user_data['girl_name']
    city = context.user_data['girl_city']
    profile = context.user_data['girl_profile']
    user = context.user_data['user_info']

    prompt = (
        f"You're helping a user start a flirty, respectful chat.\n"
        f"Girl's name: {name}\nCity: {city}\nProfile: {profile}\nUser: {user}\n"
        f"Give a short, witty opening line."
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://replit.com/@yourusername/flirtai",
        "Content-Type": "application/json"
    }

    json_data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a charming AI helping with polite flirting."},
            {"role": "user", "content": prompt}
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=json_data,
                timeout=20
            )
            response.raise_for_status()
            ai_message = response.json()['choices'][0]['message']['content']
        except Exception as e:
            ai_message = f"❌ OpenRouter error: {e}"

    await update.message.reply_text("✅ You can send this:\n\n" + ai_message)
    await update.message.reply_text("Type /start to try again.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Cancelled. Type /start to try again.")
    return ConversationHandler.END

# --- CONVERSATION HANDLER ---
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

# --- START BOT (POLLING) ---
if __name__ == "__main__":
    application.run_polling()

from telegram import Bot

TOKEN = "7292650026:AAHDUkoGALoTxRoWeWArfI2Hcg_JWZjMiAs"
WEBHOOK_URL = f"https://flirtai.pythonanywhere.com/{TOKEN}"

bot = Bot(token=TOKEN)

success = bot.set_webhook(url=WEBHOOK_URL)

if success:
    print(f"✅ Webhook set successfully: {WEBHOOK_URL}")
else:
    print("❌ Failed to set webhook")

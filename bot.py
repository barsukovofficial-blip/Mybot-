import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = "8938270908:AAESD8HK-ThmWJkfZQwpWrh3vZ-zUKN8HYY"
GROQ_API_KEY = "gsk_sPG3w6I5LY6kwUj-HV1i2WGdyb3FYXw27gTBn278mJwga-T20Zngx8"
KASPI_NUMBER = "+77778785544"
PRICE = "500"
ADMIN_ID = 7519716543

logging.basicConfig(level=logging.INFO)
groq_client = Groq(api_key=GROQ_API_KEY)
PAID_USERS = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я ИИ-помощник.\n\n"
        "💬 Задай мне любой вопрос!\n\n"
        "💳 Для получения доступа напиши: /buy"
    )

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💳 Для получения доступа:\n\n"
        f"Переведи {PRICE}₸ на Kaspi: {KASPI_NUMBER}\n"
        f"В комментарии укажи свой Telegram ID:\n\n"
        f"Твой ID: `{update.effective_user.id}`\n\n"
        "После оплаты напиши администратору.",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in PAID_USERS and user_id != ADMIN_ID:
        await update.message.reply_text(
            f"❌ У тебя нет доступа.\n\nНапиши /buy чтобы получить доступ за {PRICE}₸"
        )
        return

    user_text = update.message.text
    await update.message.reply_text("⏳ Думаю...")

    try:
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Ты полезный ИИ-помощник. Отвечай на русском языке."},
                {"role": "user", "content": user_text}
            ]
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text("❌ Ошибка, попробуй снова.")
        logging.error(f"Groq error: {e}")

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Нет доступа")
        return
    if context.args:
        new_user_id = int(context.args[0])
        PAID_USERS.add(new_user_id)
        await update.message.reply_text(f"✅ Пользователь {new_user_id} добавлен!")
    else:
        await update.message.reply_text("Используй: /adduser 123456789")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("adduser", add_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    app.run_polling()

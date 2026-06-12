import telebot
from groq import Groq

TELEGRAM_TOKEN = "8938270908:AAHqak_ZWdsscboPGWrtyDUSb7yq56XjWFQ"
GROQ_API_KEY = "gsk_sPG3w6I5LY6kwUj-HV1i2WGdyb3FYXw27gTBn278mJwga-T20Zngx8"
KASPI_NUMBER = "+77778785544"
PRICE = "500"
ADMIN_ID = 7519716543

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)
PAID_USERS = set()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "👋 Привет! Я ИИ-помощник.\n\n"
        "💬 Задай мне любой вопрос!\n\n"
        "💳 Для получения доступа напиши: /buy"
    )

@bot.message_handler(commands=['buy'])
def buy(message):
    bot.reply_to(message,
        f"💳 Для получения доступа:\n\n"
        f"Переведи {PRICE}₸ на Kaspi: {KASPI_NUMBER}\n"
        f"В комментарии укажи свой Telegram ID:\n\n"
        f"Твой ID: {message.from_user.id}\n\n"
        "После оплаты напиши администратору."
    )

@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Нет доступа")
        return
    parts = message.text.split()
    if len(parts) > 1:
        new_id = int(parts[1])
        PAID_USERS.add(new_id)
        bot.reply_to(message, f"✅ Пользователь {new_id} добавлен!")
    else:
        bot.reply_to(message, "Используй: /adduser 123456789")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    if user_id not in PAID_USERS and user_id != ADMIN_ID:
        bot.reply_to(message, f"❌ У тебя нет доступа.\n\nНапиши /buy чтобы получить доступ за {PRICE}₸")
        return

    bot.reply_to(message, "⏳ Думаю...")
    try:
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Ты полезный ИИ-помощник. Отвечай на русском языке."},
                {"role": "user", "content": message.text}
            ]
        )
        answer = response.choices[0].message.content
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка, попробуй снова.")

print("Бот запущен!")

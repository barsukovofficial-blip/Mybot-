import telebot
from groq import Groq
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_TOKEN = "8938270908:AAGaV0FU83A51OFpKfRqyzmW38KriB2QH_c"
GROQ_API_KEY = "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"
KASPI_NUMBER = "+77778785544"
PRICE = "500"
ADMIN_ID = 7519716543

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
groq_client = Groq(api_key=GROQ_API_KEY)
PAID_USERS = set()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, *args):
        pass

def run_server():
    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

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

threading.Thread(target=run_server, daemon=True).start()
print("Бот запущен!")

while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)

import telebot
from telebot import types
from datetime import datetime, timedelta

TOKEN = 'ваш токен'
bot = telebot.TeleBot(TOKEN)

# Словарь с услугами и ценами
prices = {
    "Подмышки": 350,
    "Бикини классика": 800,
    "Глубокое бикини": 1000,
    "Ноги голень/бедро": 600,
    "Ноги полностью": 1000,
    "Руки до локтя": 500,
    "Руки полностью": 1000,
    "Комплекс: Подмышки + Глубокое бикини": 1200,
    "Комплекс: Подмышки + Глубокое бикини + ноги голень": 1700,
    "Комплекс: Подмышки + Глубокое бикини + ноги полностью": 2200
}

appointments = {}  # Словарь для хранения записей

# Генерация клавиатуры с услугами
def generate_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for service in prices.keys():
        markup.add(types.KeyboardButton(service))
    return markup


def generate_date_time_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    now = datetime.now()
    for i in range(1, 7):  # Следующие 7 дней
        date = now + timedelta(days=i)
        for period in ['Утро', 'День', 'Вечер']:
            time_slot = date.strftime(f'%Y-%m-%d {period}')
            if time_slot not in appointments:
                markup.add(types.KeyboardButton(time_slot))
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Чтобы узнать цены, отправьте /prices")


@bot.message_handler(commands=['prices'])
def list_prices(message):
    markup = generate_markup()
    bot.send_message(message.chat.id, "Выберите услугу, чтобы узнать цену:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in prices)
def ask_for_date_time(message):
    markup = generate_date_time_markup()
    bot.send_message(message.chat.id, "Выберите удобное время для записи:", reply_markup=markup)


@bot.message_handler(func=lambda message: "Утро" in message.text or "День" in message.text or "Вечер" in message.text)
def book_appointment(message):
    if message.text in appointments:
        bot.reply_to(message, "Это время уже занято, выберите другое.")
    else:
        appointments[message.text] = message.from_user.id
        bot.reply_to(message, f"Вы успешно записаны на {message.text}. Для отмены отправьте /cancel.")


@bot.message_handler(commands=['cancel'])
def cancel_booking(message):
    for time, user_id in list(appointments.items()):
        if user_id == message.from_user.id:
            del appointments[time]
            bot.reply_to(message, f"Ваша запись на {time} отменена.")
            return
    bot.reply_to(message, "У вас нет активных записей.")


@bot.message_handler(func=lambda message: True)
def send_price(message):
    service = message.text
    if service in prices:
        bot.reply_to(message, f"Цена за услугу '{service}': {prices[service]} руб.")
    else:
        bot.reply_to(message, "Извините, я не нашел такую услугу. Пожалуйста, выберите услугу из предложенного списка.")

bot.polling()
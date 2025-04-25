from telebot import TeleBot, types
from database import init_db, get_connection
from datetime import datetime
import sqlite3

TOKEN = '7612094054:AAFT1_6qYhRnZql3Nw-2u2H4K-P7m9C6pIQ'
ADMIN_ID = 7371632307
bot = TeleBot(TOKEN)

GOOGLE_DOC_LINK = "https://docs.google.com/document/d/1Ztyvyp_CTCA6yJxNL58WBFzqZ-mIpyCLbX7UosvkVdk/edit?usp=sharing"

# 🔢 Цены на аккаунты
account_prices = {
    1: 400,
    2: 2500,
    3: 800,
    4: 350,
    5: 700,
    6: 800,
    7: 900
}



@bot.message_handler(commands=['start'])
def start_command(message):
    conn = get_connection()
    cursor = conn.cursor()
    telegram_id = str(message.from_user.id)
    username = message.from_user.username or "Unknown"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (telegram_id, username, registered, balance) VALUES (?, ?, ?, ?)",
                       (telegram_id, username, now, 0))  # Добавляем balance при регистрации
        conn.commit()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🛒 Магазин"),
        types.KeyboardButton("🧾 Мои покупки"),
        types.KeyboardButton("💬 Поддержка"),
        types.KeyboardButton("❓ Вопросы"),
        types.KeyboardButton("📋 Инструкция")
    )

    bot.send_message(message.chat.id,
                     "Привет! Добро пожаловать в магазин Steam-аккаунтов.",
                     reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💬 Поддержка")
def support(message):
    bot.send_message(message.chat.id, "Если возникли вопросы — пиши @yurezogure.")

@bot.message_handler(func=lambda m: m.text == "❓ Вопросы")
def questions(message):
    bot.send_message(message.chat.id,
                     "1. Как купить аккаунт?\n— Выберите категорию, затем номер аккаунта.\n\n"
                     "2. Где посмотреть описание аккаунтов?\n— В Google Документе: " + GOOGLE_DOC_LINK)

@bot.message_handler(func=lambda m: m.text == "📋 Инструкция")
def instruction(message):
    bot.send_message(message.chat.id,
                     "1. Нажмите «Магазин»\n"
                     "2. Выберите нужный сервис (Steam)\n"
                     "3. Откройте документ и выберите номер\n"
                     "4. Нажмите номер — вы получите данные после оплаты")

@bot.message_handler(func=lambda m: m.text == "🛒 Магазин")
def show_shop(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎮 Steam", callback_data="service_steam"),
        types.InlineKeyboardButton("🔐 Другие сервисы", callback_data="service_other")
    )
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("service_"))
def show_accounts(call):
    service = call.data.split("_")[1]
    if service == "steam":
        markup = types.InlineKeyboardMarkup(row_width=2)
        for i in range(1, 8):
            price = account_prices.get(i, 999)
            markup.add(types.InlineKeyboardButton(f"Аккаунт #{i} ({price}₽)", callback_data=f"buy_{i}_{price}"))
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
        bot.send_message(call.message.chat.id,
                         f"📄 Ознакомьтесь с аккаунтами в документе:\n{GOOGLE_DOC_LINK}\n\n"
                         "Выберите номер для покупки:",
                         reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Пока аккаунтов нет.")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main(call):
    show_shop(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    acc_data = call.data.split("_")
    acc_number = int(acc_data[1])
    acc_price = int(acc_data[2])

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💸 ЮMoney", callback_data=f"paymethod_yoomoney_{acc_number}_{acc_price}"),
        types.InlineKeyboardButton("💳 QIWI", callback_data=f"paymethod_qiwi_{acc_number}_{acc_price}"),
        types.InlineKeyboardButton("🏦 Сбер", callback_data=f"paymethod_sber_{acc_number}_{acc_price}")
    )
    markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"service_steam"))

    bot.send_message(call.message.chat.id,
                     f"Вы выбрали аккаунт #{acc_number} за {acc_price}₽.\nВыберите способ оплаты:",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("paymethod_"))
def handle_paymethod(call):
    _, method, acc_number, acc_price = call.data.split("_")
    acc_number = int(acc_number)
    acc_price = int(acc_price)

    payment_info = {
        "yoomoney": "41001123456789",
        "qiwi": "+79001234567",
        "sber": "5469 3800 1234 5678"
    }

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Я оплатил", callback_data=f"confirm_{acc_number}_{acc_price}"))
    markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"buy_{acc_number}_{acc_price}"))

    bot.send_message(call.message.chat.id,
                     f"💰 Способ: *{method.capitalize()}*\n"
                     f"Сумма: *{acc_price}₽*\n"
                     f"Реквизиты: `{payment_info[method]}`\n\n"
                     f"✔️ После оплаты нажмите кнопку ниже.",
                     parse_mode="Markdown",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_payment(call):
    acc_number = int(call.data.split("_")[1])
    acc_price = int(call.data.split("_")[2])

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT login, password, is_sold FROM accounts WHERE id = ?", (acc_number,))
    acc = cursor.fetchone()

    if not acc:
        bot.answer_callback_query(call.id, "Аккаунт не найден.")
        return
    if acc[2] == 1:
        bot.answer_callback_query(call.id, "Этот аккаунт уже продан.")
        return

    login, password, _ = acc
    cursor.execute("UPDATE accounts SET is_sold = 1 WHERE id = ?", (acc_number,))
    cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (str(call.from_user.id),))
    user_id = cursor.fetchone()[0]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO orders (user_id, account_id, date, paid) VALUES (?, ?, ?, 1)",
                   (user_id, acc_number, now))
    conn.commit()
    conn.close()

    bot.send_message(call.message.chat.id,
                     f"✅ Оплата подтверждена!\n"
                     f"Данные аккаунта #{acc_number}:\n\n"
                     f"Логин: `{login}`\nПароль: `{password}`",
                     parse_mode="Markdown")

    bot.send_message(ADMIN_ID,
                     f"🚀 Покупка от @{call.from_user.username}\n"
                     f"Аккаунт #{acc_number} за {acc_price}₽")

@bot.message_handler(func=lambda m: m.text == "🧾 Мои покупки")
def my_orders(message):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (str(message.from_user.id),))
    user = cursor.fetchone()
    if not user:
        bot.send_message(message.chat.id, "Вы ещё ничего не покупали.")
        return

    user_id = user[0]
    cursor.execute(""" 
        SELECT a.id, a.login, a.password FROM accounts a
        JOIN orders o ON o.account_id = a.id
        WHERE o.user_id = ? AND a.is_sold = 1
    """, (user_id,))

    results = cursor.fetchall()
    conn.close()

    if not results:
        bot.send_message(message.chat.id, "У вас нет покупок.")
    else:
        msg = "📦 Ваши покупки:\n\n"
        for acc_id, login, password in results:
            msg += f"Аккаунт #{acc_id}:\nЛогин: `{login}`\nПароль: `{password}`\n\n"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

if __name__ == '__main__':
    init_db()
   
    print("Бот запущен...")
    bot.polling(none_stop=True)

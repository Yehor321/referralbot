# -*- coding: utf-8 -*-
from telebot import types, TeleBot
import psycopg2, pathlib, sys, os, random

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
db = conn.cursor()

# Создаем таблицу пользователей (если нет)
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    balance INT DEFAULT 0,
    referrer BIGINT
)
""")
conn.commit()

bot = TeleBot(os.getenv('BOT_TOKEN'))
admins = [5748280613, 7455363246, 768064834, 994446192, 722227070, 5091124504, 5802542911, 444818421]
path = pathlib.Path(sys.argv[0]).parent.resolve()
id_of_admin_group = -1002321750890
group = -1002308965017
crypto = 'Coming Soon.'
buttons = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton('Реф. ссылка', callback_data='ref_link'),
    types.InlineKeyboardButton('Баланс', callback_data='balance'),
    types.InlineKeyboardButton(f'Вывести {crypto}', callback_data='vyvod')
)

money_file = path / 'money.txt'
money = int(money_file.read_text()) if money_file.exists() else 0

def cost_remake(message: types.Message):
    if not message.text:
        bot.reply_to(message, 'Введите цену текстовым сообщением.')
        bot.register_next_step_handler(message, cost_remake)
    else:
        bot.reply_to(message, 'Цена изменена!')
        money_file.write_text(message.text)

def send_info_to_adm(message: types.Message):
    if message.text:
        bot.reply_to(message, 'Мы успешно отправили данные администраторам бота.')
        db.execute('SELECT balance FROM users WHERE id = %s', (message.from_user.id,))
        balance = db.fetchone()
        if balance:
            bot.send_message(id_of_admin_group, f'Пользователь: {message.from_user.full_name} ({message.from_user.id})\n'
                             f'Баланс: {balance[0]}\nАдрес кошелька: {message.text}\n'
                             'Напишите "принять" в ответ на сообщение, чтобы отправить пользователю уведомление '
                             'о выводе баланса и для сброса его баланса до 0.\n{message.from_user.id}')
    else:
        bot.reply_to(message, 'Напишите адрес кошелька в текстовом сообщении.')
        bot.register_next_step_handler(message, send_info_to_adm)

def check_ref(msg: list):
    return msg[1] if len(msg) > 1 else None

@bot.message_handler(commands=['start'])
def start(message: types.Message):
    db.execute('SELECT * FROM users WHERE id=%s', (message.from_user.id,))
    info = db.fetchone()
    if info is None:
        ref = check_ref(message.text.split())
        db.execute('INSERT INTO users (id, balance, referrer) VALUES (%s, %s, %s)', (message.from_user.id, 0, ref))
        conn.commit()
        bot.reply_to(message, '👋 Добро пожаловать в Terebonk Investors Bot!', reply_markup=buttons)
        if ref:
            try:
                ref_id = int(ref)
                db.execute('UPDATE users SET balance = balance + %s WHERE id = %s', (money, ref_id))
                conn.commit()
                bot.send_message(ref_id, f'Перечислили Вам деньги за пользователя {message.from_user.full_name}.')
            except:
                pass
    else:
        bot.reply_to(message, '👋 Добро пожаловать в Terebonk Investors Bot!', reply_markup=buttons)

@bot.message_handler(commands=['balance'])
def get_balance(message: types.Message):
    db.execute('SELECT balance FROM users WHERE id = %s', (message.from_user.id,))
    balance = db.fetchone()
    if balance:
        bot.reply_to(message, f'Твой баланс: {balance[0]}')

@bot.message_handler(commands=['referral'])
def get_link_(message: types.Message):
    bot.reply_to(message, f'Твоя реферальная ссылка: https://t.me/terebonk_referral_bot/?start={message.from_user.id}')

@bot.message_handler(commands=['redeem'])
def get_money_from_admins(message: types.Message):
    bot.reply_to(message, 'Введите адрес кошелька.')
    bot.register_next_step_handler(message, send_info_to_adm)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: types.CallbackQuery):
    if call.data == 'balance':
        db.execute('SELECT balance FROM users WHERE id = %s', (call.from_user.id,))
        balance = db.fetchone()
        if balance:
            bot.send_message(call.message.chat.id, f'Твой баланс: {balance[0]}')
    elif call.data == 'ref_link':
        bot.send_message(call.message.chat.id, f'Твоя реферальная ссылка: https://t.me/terebonk_referral_bot/?start={call.from_user.id}')
    elif call.data == 'vyvod':
        bot.send_message(call.message.chat.id, 'Введите адрес кошелька.')
        bot.register_next_step_handler(call.message, send_info_to_adm)

bot.polling(none_stop=True)

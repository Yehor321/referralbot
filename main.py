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
        with open(money_file, 'w') as file:
            file.write(message.text)
            file.close()

def send_info_to_adm(message: types.Message):
    if message.text:
        bot.reply_to(message, 'Мы успешно отправили данные администраторам бота.')
        db.execute('SELECT balance FROM users WHERE id = %s', (message.from_user.id,))
        balance = db.fetchone()
        if balance:
            bot.send_message(id_of_admin_group, f'Пользователь: {message.from_user.full_name} ({message.from_user.id})\nБаланс: {balance[0]}\nАдрес кошелька: {message.text}\nНапишите "принять" в ответ на сообщение, чтобы отправить пользователю уведомление о выводе баланса и для сброса его баланса до 0.\n{message.from_user.id}')
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
    if bot.get_chat_member(group, message.from_user.id).status in ['left', 'kicked']:
        bot.reply_to(message, f'Невозможно получить реферальную ссылку.\nВступи в группу @terebonka_ru и приходи снова!')
    else:
        bot.reply_to(message, f'Твоя реферальная ссылка: https://t.me/terebonk_referral_bot/?start={message.from_user.id}')

@bot.message_handler(commands=['adminka'])
def admin_panel(message: types.Message):
    if message.from_user.id not in admins:
        pass
    else:
        bot.reply_to(message, f'Привет, админ!\nВыбери действие из меню ниже.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Вывести данные о пользователях', callback_data='excel_data'), types.InlineKeyboardButton('Изменить цену вознаграждения', callback_data='money-cost')))

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
        if bot.get_chat_member(group, call.from_user.id).status in ['left', 'kicked']:
            bot.send_message(call.message.chat.id, f'Невозможно получить реферальную ссылку.\nВступи в группу @terebonka_ru и приходи снова!')
        else:
            bot.send_message(call.message.chat.id, f'Твоя реферальная ссылка: https://t.me/terebonk_referral_bot/?start={call.from_user.id}')
    elif call.data == 'vyvod':
        bot.send_message(call.message.chat.id, 'Введите адрес кошелька.')
        bot.register_next_step_handler(call.message, send_info_to_adm)
    elif call.data == 'excel_data':
        data = db.execute(f'SELECT * FROM users').fetchall()
        chislo = random.randint(1, 100000)
        file = open(path / f'{chislo}.txt', 'w')
        file.write(str(data))
        file.close()
        bot.send_document(call.message.chat.id, open(path / f'{chislo}.txt', 'rb'), caption='Данные пользователей из бд.')
        os.remove(path / f'{chislo}.txt')
    elif call.data == 'money-cost':
        bot.send_message(call.message.chat.id, f'Напишите стоимость одного реферала.')
        bot.register_next_step_handler(call.message, cost_remake)
        
@bot.message_handler(content_types=['text'])
def textt(message: types.Message):
    if message.chat.id == id_of_admin_group:
        if message.reply_to_message:
            if message.reply_to_message.from_user.id == bot.get_me().id:
                if message.text.lower() == 'принять':
                    id = int(message.reply_to_message.text.split()[-1])
                    bot.reply_to(message, f'Успешно отправили пользователю уведомление и сбросили баланс до 0!')
                    db.execute('UPDATE users SET balance=%s WHERE id=%s', (0, id))
                    conn.commit()
                    try:
                        bot.send_message(id, f'Администраторы вывели Вам деньги на баланс кошелька. Баланс в боте был сброшен до 0.')
                    except:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass
    else:
        pass

bot.infinity_polling()
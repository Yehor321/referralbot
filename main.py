# -*- coding: utf-8 -*-
from telebot import types, TeleBot
import sqlite3, pathlib, sys, os, random

bot = TeleBot('8034312911:AAGc6oE3A-JKRDK0aP3_cW3iViOPFTT2AHM')
admins = [5748280613, 7455363246, 768064834, 994446192, 722227070, 5091124504, 5802542911, 444818421]
path = pathlib.Path(sys.argv[0]).parent.resolve()
id_of_admin_group = -1002321750890
sql = sqlite3.connect(path / 'database.db', check_same_thread=False)
db = sql.cursor()
group = -1002308965017
crypto = 'Coming Soon.'
buttons = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Реф. ссылка', callback_data='ref_link'), types.InlineKeyboardButton('Баланс', callback_data='balance'), types.InlineKeyboardButton(f'Вывести {crypto}', callback_data='vyvod'))
money = int(open(path / 'money.txt').read())

def cost_remake(message: types.Message):
    if not message.text:
        bot.reply_to(message, f'Введите цену текстовым сообщением.')
        bot.register_next_step_handler(message, cost_remake)
    else:
        bot.reply_to(message, f'Цена изменена!')
        with open(path / 'money.txt', 'w') as file:
            file.write(message.text)
            file.close()

def send_info_to_adm(message: types.Message):
    if message.text:
        bot.reply_to(message, f'Мы успешно отправили данные администраторам бота.')
        for balance in db.execute(f'SELECT balance FROM users WHERE id = {message.from_user.id}'):
            bot.send_message(id_of_admin_group, f'Пользователь: {message.from_user.full_name} ({message.from_user.id})\nБаланс: {balance[0]}\nАдрес кошелька: {message.text}\nНапишите "принять" в ответ на сообщение, чтобы отправить пользователю уведомление о выводе баланса и для сброса его баланса до 0.\n{message.from_user.id}')
    else:
        bot.reply_to(message, f'Напишите адрес кошелька в текстовом сообщении.')
        bot.register_next_step_handler(message, send_info_to_adm)

def check_ref(msg: list):
    if len(msg) == 1:
        return None
    else:
        return msg[1]

@bot.message_handler(commands=['start'])
def start(message: types.Message):
    info = db.execute('SELECT * FROM users WHERE id=?', (message.from_user.id, ))
    if info.fetchone()==None:
        ref = check_ref(message.text.split())
        if not ref:
            bot.reply_to(message, f'👋 Добро пожаловать в Terebonk Investors Bot!\n\n🚀 Зарабатывай очки, приглашая друзей, и обменивай их на мемкоины!\n\n📌 Твои команды:\n- /referral – получить реферальную ссылку \n- /balance – проверить баланс очков\n- /redeem – обменять очки на мемкоины \n\n💡 Начни прямо сейчас – приглашай друзей и зарабатывай! 🚀', reply_markup=buttons)
            db.execute(f'INSERT INTO users VALUES (?, ?, ?)', (message.from_user.id, 0, None, ))
            sql.commit()
        else:
            bot.reply_to(message, f'👋 Добро пожаловать в Terebonk Investors Bot!\n\n🚀 Зарабатывай очки, приглашая друзей, и обменивай их на мемкоины!\n\n📌 Твои команды:\n- /referral – получить реферальную ссылку \n- /balance – проверить баланс очков\n- /redeem – обменять очки на мемкоины \n\n💡 Начни прямо сейчас – приглашай друзей и зарабатывай! 🚀', reply_markup=buttons)
            try:
                id__ = int(ref)
                info = db.execute('SELECT * FROM users WHERE id=?', (id__, )).fetchone()
                if info == None:
                    bot.reply_to(message, f'Реферал не найден, возможно он даже не зарегистрирован в боте.\nМы уже зарегистрировали вас в системе.')
                    db.execute(f'INSERT INTO users VALUES (?, ?, ?)', (message.from_user.id, 0, None, ))
                    sql.commit()
                else:
                    bot.reply_to(message, f'Реферал зарегистрирован.')
                    db.execute(f'UPDATE users SET balance=balance+{money} WHERE id=?', (id__, ))
                    sql.commit()
                    try:
                        bot.send_message(id__, f'Перечислили Вам деньги за пользователя {message.from_user.full_name}.\nПроверьте свой баланс с помощью команды /balance.')
                    except:
                        pass
            except:
                bot.reply_to(message, f'Некорректный реферал.')
                db.execute(f'INSERT INTO users VALUES (?, ?, ?)', (message.from_user.id, 0, None, ))
                sql.commit()       
    else:
        bot.reply_to(message, f'👋 Добро пожаловать в Terebonk Investors Bot!\n\n🚀 Зарабатывай очки, приглашая друзей, и обменивай их на мемкоины!\n\n📌 Твои команды:\n- /referral – получить реферальную ссылку \n- /balance – проверить баланс очков\n- /redeem – обменять очки на мемкоины \n\n💡 Начни прямо сейчас – приглашай друзей и зарабатывай! 🚀', reply_markup=buttons)

@bot.message_handler(commands=['referral'])
def get_link_(message: types.Message):
    if bot.get_chat_member(group, message.from_user.id).status in ['left', 'kicked']:
        bot.reply_to(message, f'Невозможно получить реферальную ссылку.\nВступи в группу @terebonka_ru и приходи снова!')
    else:
        bot.reply_to(message, f'Твоя реферальная ссылочка: https://t.me/terebonk_referral_bot/?start={message.from_user.id}\nЗа переход по ссылке вы получите {money} единиц валюты, которую можно вывести с помощью команды /redeem!')
        
@bot.message_handler(commands=['redeem'])
def get_money_from_admins(message: types.Message):
    bot.reply_to(message, f'Отлично!\nДайте адрес своего кошелька.\nАдминистраторы, рассмотря вашу заявку переведут Вам определенное количество валюты.')
    bot.register_next_step_handler(message, send_info_to_adm)
    
@bot.message_handler(commands=['adminka'])
def admin_panel(message: types.Message):
    if message.from_user.id not in admins:
        pass
    else:
        bot.reply_to(message, f'Привет, админ!\nВыбери действие из меню ниже.', reply_markup=types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton('Вывести данные о пользователях', callback_data='excel_data'), types.InlineKeyboardButton('Изменить цену вознаграждения', callback_data='money-cost')))
        
@bot.callback_query_handler()
def obrab(call: types.CallbackQuery):
    if call.data == 'excel_data':
        data = db.execute(f'SELECT * FROM users').fetchall()
        chislo = random.randint(1, 100000)
        file = open(path / f'{chislo}.txt', 'w')
        file.write(str(data))
        file.close()
        bot.send_document(call.message.chat.id, open(path / f'{chislo}.txt', 'rb'), caption='Данные пользователей из бд.')
        os.remove(path / f'{chislo}.txt')
    if call.data == 'money-cost':
        bot.send_message(call.message.chat.id, f'Напишите стоимость одного реферала.')
        bot.register_next_step_handler(call.message, cost_remake)
    if call.data == 'ref_link':
        if bot.get_chat_member(group, call.from_user.id).status in ['left', 'kicked']:
            bot.send_message(call.message.chat.id, f'Невозможно получить реферальную ссылку.\nВступи в группу @terebonka_ru и приходи снова!')
        else:
            bot.send_message(call.message.chat.id, f'Твоя реферальная ссылочка: https://t.me/terebonk_referral_bot/?start={call.from_user.id}\nЗа переход по ссылке вы получите {money} единиц валюты, которую можно вывести с помощью команды /redeem!')
    if call.data == 'balance':
        for balance in db.execute(f'SELECT balance FROM users WHERE id = {call.from_user.id}'):
            bot.send_message(call.message.chat.id, f'Твой баланс: {balance[0]}\nПродолжай зарабатывать деньги, приглашая рефералов.')
    if call.data == 'vyvod':
        bot.send_message(call.message.chat.id, f'Отлично!\nДайте адрес своего кошелька.\nАдминистраторы, рассмотря вашу заявку переведут Вам определенное количество валюты.')
        bot.register_next_step_handler(call.message, send_info_to_adm)
        
@bot.message_handler(commands=['balance'])
def get_balance(message: types.Message):
    for balance in db.execute(f'SELECT balance FROM users WHERE id = {message.from_user.id}'):
        bot.reply_to(message, f'Твой баланс: {balance[0]}\nПродолжай зарабатывать деньги, приглашая рефералов.')

@bot.message_handler(content_types=['text'])
def textt(message: types.Message):
    if message.chat.id == id_of_admin_group:
        if message.reply_to_message:
            if message.reply_to_message.from_user.id == bot.get_me().id:
                if message.text.lower() == 'принять':
                    id = message.reply_to_message.text.split()[-1]
                    bot.reply_to(message, f'Успешно отправили пользователю уведомление и сбросили баланс до 0!')
                    db.execute(f'UPDATE users SET balance=0 WHERE id={id}')
                    sql.commit()
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
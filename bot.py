import logging
from os import access
from tabnanny import check
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import sqlite3
import sched, time
from datetime import datetime
import re
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Timer
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import requests
import json

admin = []


def get_api_token():
    conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
    cursos123 = conn_citys.cursor()
    api_token = cursos123.execute("SELECT value FROM config WHERE key = 'api_token'").fetchall()
    for i in api_token[0]:
    	print(i)
    return str(i)


s = sched.scheduler(time.time, time.sleep)
API_TOKEN = get_api_token()

bot = Bot(token=API_TOKEN,parse_mode=types.ParseMode.HTML)
bot_tele = telebot.TeleBot(API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect('mytest.db', check_same_thread=False)
cursor = conn.cursor()


exchange = []
exchange_address = []

class settings(StatesGroup):
    reserve = State()  
    reserve_id = State() 
    adress_crypto = State()
    procent = State()
    address_postup = State()
    trades_id = State()
    rewiews_text = State()
    rewiews_user = State()
    rewiews_rating = State()
    rewiews_finish = State()
    rewiews_finish = State()
    seo = State()
    seo_id = State()
    config = State()
    config_id = State()
    confirm = State()


keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
button_1 = "🔰Резервы🔰"
keyboard.add(button_1)
button_2 = "🙌Процент комиссии 🙌"
keyboard.add(button_2)
button_3 = "👛Адреса кошельков👛"
keyboard.add(button_3)
button_4 = "💬 Написать Отзыв 💬"
keyboard.add(button_4)
button_5 = "❇Настроить SEO❇"
keyboard.add(button_5)
button_6 = "⚙ Настроить config ⚙"
keyboard.add(button_6)


@dp.message_handler(commands='start')
async def welcome(message: types.Message):
    if message["from"]["id"] in admin:
        await message.answer(f"Приветствую.", reply_markup=keyboard)
        scheduler = BackgroundScheduler()
        scheduler.add_job(check_new_trades, 'interval', seconds=10)
        scheduler.start()
    else:
    	await message.answer(f"Приветствую.\nВот ваш персональный id: {message.from_user.id}")
    # await message.answer(message)


@dp.message_handler(commands='stat')
async def stats(message: types.Message):
    if message.from_user.id in admin:
        today = datetime.today()
        date = today.strftime(f"%m.%d.%y")  
        three_days = datetime.today() - timedelta(days=3)
        date_3 = three_days.strftime(f"%m.%d.%y")
        week_day = datetime.today() - timedelta(days=7)
        date_7 = week_day.strftime(f"%m.%d.%y")
        conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
        cursor_citys = conn_citys.cursor()
        value_users_today = cursor_citys.execute(f"SELECT id FROM users WHERE date_registration = '{date}'").fetchall()
        value_users_three_days = cursor_citys.execute(f"SELECT id FROM users WHERE date_registration BETWEEN '{date_3}' AND '{date}'").fetchall()
        value_users_seven_days = cursor_citys.execute(f"SELECT id FROM users WHERE date_registration BETWEEN '{date_7}' AND '{date}'").fetchall()
        trades = cursor_citys.execute(f"SELECT id FROM trades").fetchall()
        await bot.send_message(message.from_user.id, f"Новых пользователей за день: {len(value_users_today)}, за 3 дня: {len(value_users_three_days)}, за неделю: {len(value_users_seven_days)}\n Всего обменов: {len(trades)}")
    else:
    	await message.answer("Доступ запрещен")


@dp.message_handler(Text(equals="🙌Процент комиссии 🙌"))
async def procent(message: types.Message):  
    if message.from_user.id in admin:
        conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
        cursor_citys = conn_citys.cursor()
        procentik = cursor_citys.execute("SELECT procent_per_summa FROM settings").fetchone()
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup1.add(types.KeyboardButton("Закрыть"))
        await bot.send_message(message.from_user.id, f"Напишите процент. На данный момент процент равен {procentik[0]}%",reply_markup=markup1)
        await settings.procent.set()
    else:
    	await message.answer("Доступ запрещен")

# Отзыв начало
@dp.message_handler(Text(equals="💬 Написать Отзыв 💬"))
async def procent(message: types.Message):
    if message.from_user.id in admin:
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup1.add(types.KeyboardButton("Закрыть"))
        await bot.send_message(message.from_user.id, f"Введите имя пользователя создающего коментарий",reply_markup=markup1)
        await settings.rewiews_user.set()
    else:
    	await message.answer("Доступ запрещен")


@dp.message_handler(state = settings.rewiews_user)
async def user_add(message: types.Message, state: FSMContext):
	if message.from_user.id in admin:
	    if message.text == 'Закрыть':
	        await bot.send_message(message.from_user.id, 'Закрыто создание отзыва', reply_markup=keyboard)
	        await state.finish()
	    else:
	        rewiews_user = message.text
	        await state.update_data(rewiews_user=rewiews_user)
	        await bot.send_message(message.from_user.id, "Введите текст отзыва")
	        await settings.rewiews_text.set()
	else:
		await message.answer(f"Доступ запрещен")


@dp.message_handler(state = settings.rewiews_text)
async def user_add(message: types.Message, state: FSMContext):
	if message.from_user.id in admin:
	    if message.text == 'Закрыть':
	        await bot.send_message(message.from_user.id, 'Закрыто создание отзыва', reply_markup=keyboard)
	        await state.finish()
	    else:
	        rewiews_text = message.text
	        await state.update_data(rewiews_text=rewiews_text)
	        await bot.send_message(message.from_user.id, "Введите рейтинг отзыва от 1 до 5")
	        await settings.rewiews_rating.set()
	else:
		await message.answer("Доступ запрещен")


@dp.message_handler(state = settings.rewiews_rating)
async def user_add(message: types.Message, state: FSMContext):
	if message.from_user.id in admin:
	    if message.text == 'Закрыть':
	        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
	        await bot.send_message(message.from_user.id, 'Закрыто создание отзыва', reply_markup=keyboard)
	        await state.finish()
	    else:
	        rewiews_rating = message.text
	        data = await state.get_data()
	        await state.update_data(rewiews_rating=rewiews_rating)
	        text = data.get("rewiews_text")
	        user = data.get("rewiews_user")
	        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
	        button_1 = "Создать отзыв"
	        keyboard.add(button_1)
	        button_2 = "Закрыть"
	        keyboard.add(button_2)
	        await bot.send_message(message.from_user.id, f"Отзыв:{text} \nПользователь: {user} \nРейтинг: {rewiews_rating}", reply_markup=keyboard)
	        await settings.rewiews_finish.set()
	else:
		await message.answer("Доступ запрещен")


@dp.message_handler(state = settings.rewiews_finish)
async def user_add(message: types.Message, state: FSMContext):
	if message.from_user.id in admin:
	    if message.text == 'Закрыть':
	        await bot.send_message(message.from_user.id, 'Закрыто создание отзыва', reply_markup=keyboard)
	        await state.finish()
	    else:
	        conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	        cursos123 = conn_citys.cursor()
	        data = await state.get_data()
	        text = data.get("rewiews_text")
	        user = data.get("rewiews_user")
	        rating = data.get("rewiews_rating")
	        print(text)
	        print(user)
	        print(rating)
	        today = datetime.today()
	        date = today.strftime(f"%m.%d.%y")
	        users = cursos123.execute(
	            "INSERT INTO reviews (date, content, rating, user) VALUES (?, ?, ?, ?);", [date, text, rating,user]).fetchall()
	        conn_citys.commit()
	        await bot.send_message(message.from_user.id, 'Отзыв успешно создан',
	                               reply_markup=keyboard)
	        await state.finish()
	else:
		await message.answer("Доступ запрещен")
# Отзыв конец


@dp.message_handler(Text(equals="❇Настроить SEO❇"))
async def enable(message: types.Message):
	if message.from_user.id in admin:
		conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
		cursor_citys = conn_citys.cursor()
		cursor_citys.execute("SELECT id,key FROM seo")
		currency = []
		while True:
			row = cursor_citys.fetchone()
			if row == None:
				break
			else:
				currency.append(row[1])
		keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
		buttons = []
		for i, item in enumerate(currency):
			print(i)
			num = types.InlineKeyboardButton(text=f'{item}', callback_data=f'{i}_seo')
			buttons.insert(i, num)
		keyboard.add(*buttons)
		await bot.send_message(message.chat.id, "Выберите один из ключей!", reply_markup=keyboard)
	else:
		await message.answer("Доступ запрещен")



@dp.message_handler(Text(equals="⚙ Настроить config ⚙"))
async def enable(message: types.Message):
	if message.from_user.id in admin:
	    conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	    cursor_citys = conn_citys.cursor()
	    cursor_citys.execute("SELECT id,key FROM config")
	    currency = []
	    while True:
	        row = cursor_citys.fetchone()
	        if row == None:
	            break
	        else:
	            currency.append(row[1])
	    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
	    buttons = []
	    for i, item in enumerate(currency):
	            print(i)
	            num = types.InlineKeyboardButton(text=f'{item}', callback_data=f'{i}_config')
	            buttons.insert(i, num)
	    keyboard.add(*buttons)
	    await bot.send_message(message.chat.id, "Выберите один из ключей!", reply_markup=keyboard)
	else:
		await message.answer("Доступ запрещен")



@dp.message_handler(state = settings.procent)
async def user_add(message: types.Message, state: FSMContext):
	if message.from_user.id in admin:
	    if message.text == 'Закрыть':
	        await bot.send_message(message.from_user.id, 'Закрыто изменение значения процента комиссии', reply_markup=keyboard)
	        await state.finish()
	    else:
	        try:
	            procent = message.text
	            await state.update_data(procent=procent)
	            radius = await state.get_data('radius_city')
	            cursor.execute(f"""UPDATE settings SET procent_per_summa = {float(radius['procent'])}""")
	            conn.commit()
	            await state.finish()
	            await bot.send_message(message.from_user.id, "Процент успешно изменен!")
	        except:
	            await bot.send_message(message.from_user.id, "Неправильно набран процент, данные о смене процента не сохранились!")
	            await state.finish()
	else:
		await message.answer("Доступ запрещен")



@dp.message_handler(Text(equals="Закрыть"))
async def swith_pocket(message: types.Message):
	if message.from_user.id in admin:
		await bot.send_message(message.from_user.id, 'Переходим в главное меню', reply_markup=keyboard)
	else:
		await message.answer("Доступ запрещен")



@dp.message_handler(Text(equals="👛Адреса кошельков👛"))
async def swith_pocket(message: types.Message): 
	if message.from_user.id in admin:  
	    conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	    cursor_citys = conn_citys.cursor()
	    cursor_citys.execute("SELECT currency FROM reserve_currency")
	    currency = []
	    while True:
	        row = cursor_citys.fetchone()
	        if row == None:
	            break
	        else:
	            currency.append(row[0])    
	    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
	    buttons = []
	    for i, item in enumerate(currency):
	            print(i)
	            num = types.InlineKeyboardButton(text=f'{item}', callback_data=f'{i}')
	            buttons.insert(i, num)
	    keyboard.add(*buttons)
	    await bot.send_message(message.chat.id, "Выберите одну из валют!", reply_markup=keyboard)
	else:
		await message.answer("Доступ запрещен")

    

@dp.message_handler(state = settings.adress_crypto)
async def bla_bla(message: types.Message, state: FSMContext):
	if message.from_user.id in admin:
	    conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	    cursor_citys = conn_citys.cursor()
	    if message.text == 'Закрыть':
	        await bot.send_message(message.from_user.id, 'Закрыто изменение значения адреса криптовалюты', reply_markup=keyboard)
	        await state.finish()
	    else:
	        async with state.proxy() as data:
	            reserve = message.text
	            await state.update_data(adress_crypto=reserve)
	            setting_frequency = await state.get_data('adress_crypto')
	            print(setting_frequency)   
	            cursor_citys.execute(f"UPDATE reserve_currency SET adress_crypto = '{setting_frequency['adress_crypto']}' WHERE id_currency = {setting_frequency['reserve_id']}")
	            conn_citys.commit()
	            name_currency = cursor_citys.execute(f"SELECT currency FROM reserve_currency WHERE id_currency = {setting_frequency['reserve_id']}").fetchone()
	            for i in admin:
	                await bot.send_message(i, f"Кошелек {name_currency[0]} был изменен")
	                await state.finish()
	else:
		await message.answer("Доступ запрещен")


# резерв
@dp.message_handler(Text(equals="🔰Резервы🔰"))
async def enable(message: types.Message):   
	if message.from_user.id in admin:
	    conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	    cursor_citys = conn_citys.cursor()
	    cursor_citys.execute("SELECT currency, reserve FROM reserve_currency")
	    currency = []
	    while True:
	        row = cursor_citys.fetchone()
	        if row == None:
	            break
	        else:
	            currency.append(row[0]+' '+str(row[1]))    
	    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
	    buttons = []
	    for i, item in enumerate(currency):
	            print(i)
	            num = types.InlineKeyboardButton(text=f'{item}', callback_data=f'{i}_reserve')
	            buttons.insert(i, num)
	    keyboard.add(*buttons)
	    await bot.send_message(message.chat.id, "Выберите одну из валют!", reply_markup=keyboard)
	else:
		await message.answer("Доступ запрещен")


@dp.callback_query_handler(lambda call: True)
async def delete_admin(call: types.CallbackQuery, state: FSMContext):
	if message.from_user.id in admin:
	    print(call.data)
	    if re.findall("reserve", call.data):
	        conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	        cursor_citys = conn_citys.cursor()
	        cursor_citys.execute("SELECT id_currency FROM reserve_currency")
	        id = []
	        while True:
	                row = cursor_citys.fetchone()
	                if row == None:
	                    break
	                else:
	                    id.append(row[0])
	        call_data = re.sub("[\_\rreserve]+", '', call.data)
	        await state.update_data(reserve_id=id[int(call_data)])
	        await settings.reserve.set()
	        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
	        markup1.add(types.KeyboardButton("Закрыть"))
	        await bot.send_message(call.from_user.id, f"Отправьте значение формате: 11.00!", reply_markup=markup1)
	        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	    if re.findall("seo", call.data):
	        conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	        cursor_citys = conn_citys.cursor()
	        cursor_citys.execute("SELECT id FROM seo")
	        id = []
	        while True:
	                row = cursor_citys.fetchone()
	                if row == None:
	                    break
	                else:
	                    id.append(row[0])
	        call_data = re.sub("[\_\rseo]+", '', call.data)
	        await state.update_data(seo_id=id[int(call_data)])
	        await settings.seo.set()
	        value = cursor_citys.execute("SELECT value FROM seo WHERE id=?",[id[int(call_data)]]).fetchone()
	        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
	        markup1.add(types.KeyboardButton("Закрыть"))
	        await bot.send_message(call.from_user.id, f"Отправьте значение!\nТекущее начение: {value[0]}", reply_markup=markup1)
	        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	    if re.findall("config", call.data):
	        conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	        cursor_citys = conn_citys.cursor()
	        cursor_citys.execute("SELECT id FROM config")
	        id = []
	        while True:
	                row = cursor_citys.fetchone()
	                if row == None:
	                    break
	                else:
	                    id.append(row[0])
	        call_data = re.sub("[\_\rconfig]+", '', call.data)
	        await state.update_data(config_id=id[int(call_data)])
	        await settings.config.set()
	        value = cursor_citys.execute("SELECT value FROM config WHERE id=?",[id[int(call_data)]]).fetchone()
	        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
	        markup1.add(types.KeyboardButton("Закрыть"))
	        await bot.send_message(call.from_user.id, f"Отправьте значение!\nТекущее начение: {value[0]}", reply_markup=markup1)
	        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	    elif re.findall('status', call.data):
	        conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	        cursos123 = conn_citys.cursor()
	        users = cursos123.execute("SELECT id FROM trades").fetchall()
	        print(call.data)
	        call_datas =  re.sub("_\w+", '', call.data)

	        print(call_datas)
	        id_xd = cursos123.execute(f"SELECT id_xd FROM trades WHERE id = '{call_datas}'")
	        for id in id_xd:
	            print(id[0])
	            try:
	                exchange_address.remove(id[0])
	                exchange.remove(id[0])
	            except:
	                print("id не найден")
	        for i in users:
	            crypto = cursos123.execute(f"SELECT from_crypto FROM trades WHERE id = '{call_datas}'")
	            for j in crypto:
	                print(j[0])
	                crypto_address_base = cursos123.execute(f"SELECT adress_crypto FROM reserve_currency WHERE currency = '{j[0]}'").fetchall()
	                for c in crypto_address_base:
	                    print(c)
	                    await state.update_data(trades_id=call_datas)
	                    await settings.address_postup.set()
	                    await bot.send_message(call.from_user.id, f"Напишите адрес на который должна поступить криптовалюта {j[0]} ,либо используйте адресс из базы:\n<code>{c[0]}</code>" , parse_mode="HTML")
	                    break
	                break
	            break
	        await bot.delete_message(call.from_user.id, message_id=call.message.message_id)

	    elif re.findall('otmena', call.data):
	        conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	        cursos123 = conn_citys.cursor()
	        users = cursos123.execute("SELECT id FROM trades").fetchall()
	        print(call.data)
	        call_datas =  re.sub("_\w+", '', call.data)
	        print(call_datas)
	        id_xd = cursos123.execute(f"SELECT id_xd FROM trades WHERE id = '{call_datas}'")

	        for id in id_xd:
	            print(id[0])
	            try:
	                exchange_address.remove(id[0])
	                exchange.remove(id[0])
	            except:
	                print("id не найден")
	        for i in users:
	            cursos123.execute(f"UPDATE trades SET status = 'Транзакция отменена' WHERE id = '{call_datas}'")
	            conn_citys.commit()
	            await bot.delete_message(call.from_user.id, message_id=call.message.message_id)
	            await bot.send_message(call.from_user.id, "Обмен закрыт!", reply_markup=keyboard)


	    elif re.findall('confirmed', call.data):
	        conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	        cursos123 = conn_citys.cursor()
	        users = cursos123.execute("SELECT id FROM trades").fetchall()
	        print(call.data)
	        call_datas =  re.sub("_\w+", '', call.data)
	        print(call_datas)
	        for i in users:
	            cursos123.execute(f"UPDATE trades SET status = 'Подтверждено' WHERE id = '{call_datas}'")
	            conn_citys.commit()
	        await bot.send_message(call.from_user.id, f"Перевод подтвержден!", reply_markup=keyboard)
	        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	    elif call.data == 'yes':
	        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	    else:
	        conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	        cursor_citys = conn_citys.cursor()
	        cursor_citys.execute("SELECT id_currency FROM reserve_currency")
	        id = []
	        while True:
	                row = cursor_citys.fetchone()
	                if row == None:
	                    break
	                else:
	                    id.append(row[0])
	        await state.update_data(reserve_id=id[int(call.data)])
	        await settings.adress_crypto.set()
	        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
	        markup1.add(types.KeyboardButton("Закрыть"))
	        asb = await state.get_data('adress_crypto')
	        print(asb)
	        name_cur = cursor_citys.execute(f"SELECT adress_crypto FROM reserve_currency WHERE id_currency = {asb['reserve_id']}").fetchone()
	        name_cur_full = cursor_citys.execute(f"SELECT currency FROM reserve_currency WHERE id_currency = {asb['reserve_id']}").fetchone()
	        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	        await bot.send_message(call.from_user.id, f"Отправьте адрес {name_cur_full[0]}, текущий кошелек:  <code>{name_cur[0]}</code>", reply_markup=markup1, parse_mode="HTML")



@dp.message_handler(state = settings.address_postup)
async def address_postup_chage(message: types.Message, state: FSMContext):
	if message.from_user.id in admin:
	    conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
	    cursor = conn_citys.cursor()
	    address_postup = message.text
	    await state.update_data(address_postup=address_postup)
	    setting_address = await state.get_data()
	    address = setting_address.get('address_postup')
	    trades_id = setting_address.get('trades_id')
	    print("address "+address)
	    print("trades "+trades_id)
	    # cur.execute("select * from people where name_last=:who and age=:age", {"who": who, "age": age})
	    cursor.execute(f"""UPDATE trades SET adress_postup = '{address}' WHERE id = '{trades_id}'""").fetchone()
	    cursor.execute(f"""UPDATE trades SET status = 'Ожидание оплаты' WHERE id = '{trades_id}'""").fetchone()
	    cursor.execute(f"""UPDATE trades SET status = 'Ожидание оплаты' WHERE id = '{trades_id}'""").fetchone()
	    conn.commit()

	    user = cursor.execute(f"SELECT user FROM trades WHERE id = '{trades_id}'").fetchone()
	    payments_user = cursor.execute(f"SELECT payments_user FROM trades WHERE id = '{trades_id}'").fetchone()
	    name = cursor.execute(f"Select fname from users where email = '{user[0]}'").fetchone()
	    trade = cursor.execute(
	        f"SELECT id, user, from_crypto, status, payable, to_crypto, payments_user, summa_postup, adress_postup, id_xd FROM trades WHERE id = '{trades_id}'").fetchall()
	    print(user)
	    print(name)
	    print(trade)

	    if trade:
	        for item1 in trade:
	            check_user_trade = cursor.execute(f"SELECT id FROM trades WHERE user = '{item1[1]}'").fetchall()
	            cursor.execute(f"UPDATE users SET trades = {len(check_user_trade)} WHERE email = '{item1[1]}'")
	            text = ""
	            text = "♻️Обмен № {0} \nПользователь:  {1} \nОбменов совершил: {2} \nВалюта поступления: {3} \nСумма поступления: {4} \nОбменять на: {5} \nСумма к переводу: {6}\nАдрес на который совершен перевод: {7}".format(
	                item1[9] + 1, item1[1], len(check_user_trade), item1[2], item1[7], item1[5], item1[4], item1[8])
	            conn_citys.commit()
	            URL = 'https://api.telegram.org/bot' + API_TOKEN + '/sendMessage'
	            print(str(item1[0]))

	            reply_markup = {
	                "inline_keyboard": [[
	                    {
	                        "text": 'Подтвердить перевод',
	                        "callback_data": f'{str(item1[0])}_confirmed'
	                    },
	                    {
	                        "text": 'Отказать',
	                        "callback_data": f'{str(item1[0])}_otmena'
	                    }

	                ]]
	            }
	            data = {'chat_id': message.from_user.id, 'text': f"Адрес ({address}) успешно установлен,проведите оплату на адрес {payments_user[0]}.\nОжидайте перевода на установленный адрес.", 'reply_markup': json.dumps(reply_markup)}
	            r = requests.post(URL, data=data)
	        await state.finish()
	else:
		await message.answer("Доступ запрещен")



@dp.message_handler(state = settings.reserve)
async def user_add(message: types.Message, state: FSMContext):
	if message.from_user.id in admin:
	    async with state.proxy() as data:
	        if message.text == 'Закрыть':
	            await bot.send_message(message.from_user.id,'Закрыто изменение значения резера криптовалюты', reply_markup=keyboard)
	            await state.finish()
	        else:
	            name = cursor.execute(f"SELECT currency FROM reserve_currency WHERE id_currency = {data['reserve_id']}").fetchone()
	            print(data['reserve_id'])
	            reserve = message.text
	            await state.update_data(reserve=reserve)
	            setting_frequency = await state.get_data('reserve')
	            try:
	                cursor.execute(f"UPDATE reserve_currency SET reserve ={(setting_frequency['reserve'])} WHERE id_currency = {int(data['reserve_id'])}")
	                print(setting_frequency['reserve'])
	                conn.commit()
	                await state.finish()
	                name = cursor.execute(f"SELECT currency FROM reserve_currency WHERE id_currency = {data['reserve_id']}").fetchone()
	                await bot.send_message(message.from_user.id, f"Криптовалюта {name[0]} успешно изменена!")
	            except:
	                await bot.send_message(message.from_user.id, f"Формат введенных данных неверный!", reply_markup=keyboard)
	                await state.finish()
	else:
		await message.answer("Доступ запрещен")

#конец резерва


@dp.message_handler(state = settings.seo)
async def user_add(message: types.Message, state: FSMContext):
	if message.from_user.id in admin:
	    async with state.proxy() as data:
	        if message.text == 'Закрыть':
	            await bot.send_message(message.from_user.id, 'Закрыто изменение значения резера криптовалюты',
	                                   reply_markup=keyboard)
	            await state.finish()
	        else:
	            name = cursor.execute(
	                f"SELECT key FROM seo WHERE id = {data['seo_id']}").fetchone()
	            print(data['seo_id'])
	            value = message.text
	            await state.update_data(seo=value)
	            seo = await state.get_data('value')
	            print(seo)
	            cursor.execute(
	                f"UPDATE seo SET value = ? WHERE id = ?", [seo['seo'], int(data['seo_id'])])
	            print(seo['seo'])
	            conn.commit()
	            await state.finish()
	            name = cursor.execute(
	                f"SELECT key FROM seo WHERE id = {data['seo_id']}").fetchone()
	            await bot.send_message(message.from_user.id, f"{name[0]} успешно изменен!",reply_markup=keyboard)
	else:
		await message.answer("Доступ запрещен")


@dp.message_handler(state = settings.config)
async def user_add(message: types.Message, state: FSMContext):
	if message.from_user.id in admin:
	    async with state.proxy() as data:
	        if message.text == 'Закрыть':

	            await bot.send_message(message.from_user.id, 'Закрыто изменение значения резера криптовалюты',
	                                   reply_markup=keyboard)
	            await state.finish()
	        else:
	            name = cursor.execute(
	                f"SELECT key FROM config WHERE id = {data['config_id']}").fetchone()
	            print(data['config_id'])
	            value = message.text
	            await state.update_data(config=value)
	            config = await state.get_data('value')
	            print(config)
	            cursor.execute(
	                f"UPDATE config SET value = ? WHERE id = ?", [config['config'], int(data['config_id'])])
	            print(config['config'])
	            conn.commit()
	            await state.finish()
	            name = cursor.execute(
	                f"SELECT key FROM config WHERE id = {data['config_id']}").fetchone()
	            await bot.send_message(message.from_user.id, f"{name[0]} успешно изменен!",reply_markup=keyboard)
	else:
		await message.answer("Доступ запрещен")


def check_new_trades():
    print("lol")
    check_trades = []
    admins_id = []
    conn_citys = sqlite3.connect('mytest.db', check_same_thread=False)
    cursos123 = conn_citys.cursor()
    users = cursos123.execute("SELECT id_xd FROM trades").fetchall()
    admin_id = cursos123.execute("SELECT value FROM config WHERE key = 'admins_id'").fetchall()
    check_trades.append(users)
    admins_id.append(admin_id)
    for i in admins_id[0]:
    	txt = i[0]
    	x = txt.split(",")
    	admin.clear()
    	for j in x:
    		admin.append(int(j)) 
    	print(admin)
    URL = 'https://api.telegram.org/bot' + API_TOKEN + '/sendMessage'
    for item in check_trades[0]:
        user = cursos123.execute(f"SELECT user FROM trades WHERE id_xd = '{item[0]}'").fetchone()
        name = cursos123.execute(f"Select fname from users where email = '{user[0]}'").fetchone()
        trade = cursos123.execute(f"SELECT id, user, from_crypto, status, payable, to_crypto, payments_user, summa_postup, adress_postup, id_xd FROM trades WHERE id_xd = '{item[0]}' AND status = 'Ожидание' AND otpravka = 0").fetchall()
        trade1 = cursos123.execute(f"SELECT id, user, from_crypto, status, payable, to_crypto, payments_user, summa_postup, adress_postup, id_xd FROM trades WHERE id_xd = '{item[0]}' AND status = 'Ожидание оплаты' ").fetchall()
        if trade:
            for item1 in trade:
                if item1[9] in exchange:
                    print('Yes'+item1[9])
                else:
                    exchange.append(item1[9])
                    exchange_address.append(item1[9])
                    print(item1[9])
                check_user_trade = cursos123.execute(f"SELECT id FROM trades WHERE user = '{item1[1]}'").fetchall()
                cursos123.execute(f"UPDATE users SET trades = {len(check_user_trade)} WHERE email = '{item1[1]}'")
                text = ""
                text = "♻️Обмен № {0} \nПользователь:  {1} \nОбменов совершил: {2} \nВалюта поступления: {3} \nСумма поступления: {4} \nОбменять на: {5} \nСумма к переводу: {6}".format(
                    item1[9]+1, item1[1], len(check_user_trade), item1[2], item1[7], item1[5], item1[4])
                conn_citys.commit()
                for i in admin:
                    reply_markup = {
                        "inline_keyboard": [[
                            {
                                "text": 'Указать адрес поступления',
                                "callback_data": f'{str(item1[0])}_status'
                            },
                            {
                                "text": 'Отказать',
                                "callback_data": f'{str(item1[0])}_otmena'
                            }
                        ]]
                    }
                    data = {'chat_id': i, 'text': text, 'reply_markup': json.dumps(reply_markup)}
                    r = requests.post(URL, data=data)
                    cursos123.execute(f"UPDATE trades SET otpravka = 1 WHERE id = '{item1[0]}'")
                    conn_citys.commit()
                    check_trades.clear()

        else:
            if trade1:
                for item1 in trade1:
                    if item1[9] in exchange_address:
                        exchange_address.remove(item1[9])
                        for chat_id in admin:
                            text = "♻️Обмен № {0} адрес для поступления криптовалюты изменен через сайт".format(item1[9] + 1, )
                            data = {'chat_id': chat_id, 'text': text}
                            r = requests.post(URL, data=data)
            else:
                user = cursos123.execute(f"SELECT user FROM trades WHERE id_xd = '{item[0]}'").fetchone()
                name = cursos123.execute(f"Select fname from users where email = '{user[0]}'").fetchone()
                trade_finish = cursos123.execute(
                    f"SELECT id, user, from_crypto, status, payable, to_crypto, payments_user, summa_postup, adress_postup, id_xd FROM trades WHERE id_xd = '{item[0]}' AND otpravka = 1 AND status = 'Подтверждено' ").fetchall()
                trade_finish2 = cursos123.execute(
                    f"SELECT id, user, from_crypto, status, payable, to_crypto, payments_user, summa_postup, adress_postup, id_xd FROM trades WHERE id_xd = '{item[0]}' AND otpravka = 1 AND status = 'Транзакция отменена' ").fetchall()

                if trade_finish:
                    for item1 in trade_finish:
                        if item1[9] in exchange:
                            exchange.remove(item1[9])
                            for chat_id in admin:
                                text = "♻️Обмен № {0} завершен через сайт со статусом подтвержден".format(item1[9]+1, )
                                data = {'chat_id': chat_id, 'text': text}
                                r = requests.post(URL, data=data)
                if trade_finish2:
                    for item1 in trade_finish2:
                        if item1[9] in exchange:
                            exchange.remove(item1[9])
                            for chat_id in admin:
                                text = "♻️Обмен № {0} завершен через сайт со статусом отменен".format(item1[9] + 1, )
                                data = {'chat_id': chat_id, 'text': text}
                                r = requests.post(URL, data=data)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    bot_tele.polling(none_stop=True, interval=0)
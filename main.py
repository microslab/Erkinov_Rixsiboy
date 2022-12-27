import os
import sqlite3


import requests
from datetime import datetime
from dotenv import *
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help', 'history', 'about'])
async def commands(msg: Message):
    if 'start' in msg.text:
        await msg.answer('Здравствуйте Вас приветствует бот "прогноз погоды"')
        await msg.answer('Введите название города для просмотра погоды:')
        await msg.delete()
    elif 'help' in msg.text:
        await msg.answer('Просто отправьте название города, можно без ввода команды /start')
        await msg.delete()
    elif 'history' in msg.text:
        await get_history(msg)
        await msg.delete()
    elif 'about' in msg.text:
        await msg.answer('Я тестовый бот, так же могу хранить и выдовать историю просматриваемых городов')
        await msg.delete()


@dp.message_handler()
async def returt_text(msg: Message):
    parameters = {
        'appid': '41e30429cbaedaabee3a2bd630d8fdb3',
        'units': 'metric',
        'lang': 'ru'
    }

    city = msg.text
    # if len(city) == 0:
    parameters['q'] = city
    try:
        data = requests.get('https://api.openweathermap.org/data/2.5/weather', params=parameters).json()
        temp = data['main']['temp']
        city_name = data['name']
        wind = data['wind']['speed']
        timezone = data['timezone']
        sunrise = datetime.utcfromtimestamp(int(data['sys']['sunrise']) + int(timezone)).strftime(
            '%Y-%m-%d %H:%M:%S')
        sunset = datetime.utcfromtimestamp(int(data['sys']['sunset']) + int(timezone)).strftime('%Y-%m-%d %H:%M:%S')
        descriptionn = data['weather'][0]['description']
        await msg.answer(f'''
              В городе {city_name} сейчас {descriptionn}
        Температура: {temp} ℃
        Скорость ветра: {wind} м/c
        Рассвет: {sunrise}
        Закат: {sunset} ''')

        chat_id = msg.chat.id
        database = sqlite3.connect('pogoda.db')
        cursor = database.cursor()
        cursor.execute('''
                INSERT INTO history(telegram_id, temp, city_name, wind, sunrise, sunset, descriptionn) 
                VALUES (?, ?, ?, ?, ?, ?, ?) 
                ''', (chat_id, temp, city_name, wind, sunrise, sunset, descriptionn))
        database.commit()
        database.close()

    except KeyError:
        await msg.answer("Вы ввели не корректный город")

async def get_history(msg):
    chat_id = msg.chat.id
    database = sqlite3.connect('pogoda.db')
    cursor = database.cursor()

    cursor.execute('''
        SELECT temp, city_name, wind, sunrise, sunset, descriptionn FROM history
        WHERE telegram_id = ?
        ''', (chat_id,))

    history = cursor.fetchall()
    history = history[::-1]
    for temp, city_name, wind, sunrise, sunset, descriptionn in history[:5]:
        await bot.send_message(chat_id, f'''
В городе {city_name} сейчас {descriptionn}
Температура: {temp} ℃
Скорость ветра: {wind} м/c
Рассвет: {sunrise}
Закат: {sunset}
''')

    database.close()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)





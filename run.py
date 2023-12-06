import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types, F

import register_user
import results
import json
import test_on
from date.qvest import start_on

with open('API.json', 'r') as file:
    data = json.load(file)
token = data["API"]

bot = Bot(token=token)
dp = Dispatcher()

users = {}


@dp.message(F.text == '/start')
async def start(message: types.Message):
    await message.answer(f"{start_on[0]['starts']}\n\n"
                         "💠Выберите нужную команду из меню для прохождения теста или открыть таблицу лидеров.\n"
                         "(Слева снизу три полоски или кнопка меню)*")


async def run():
    dp.include_routers(
        results.router,
        register_user.router,
        test_on.router,

    )
    await dp.start_polling(bot, token=token)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print('Выход')
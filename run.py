import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types, F

import register_user
import results
from API import API
import test_on

bot = Bot(token=API)
dp = Dispatcher()

users = {}


@dp.message(F.text == '/start')
async def start(message: types.Message):
    await message.answer("Здравствуйте, это тест по Литературе!\n\n"
                         "💠Выберите нужную команду из меню для прохождения теста или открыть таблицу лидеров.\n"
                         "(Слева снизу три полоски или кнопка меню)*")


async def run():
    dp.include_routers(
        results.router,
        register_user.router,
        test_on.router,

    )
    await dp.start_polling(bot, token=API)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print('Выход')
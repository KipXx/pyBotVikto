# run.py
import asyncio
import logging
import sys
from aiogram.types import ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, types, F

from menu import key
from models import TestResult, session
from qvest import *
from API import API


bot = Bot(token=API)
dp = Dispatcher()

users = {}


@dp.message(F.text == '/start')
async def start(message: types.Message):
    response = ("Здравствуйте, это тест по Литературе!\n\n"
                "💠Выберите нужную команду из меню для прохождения теста или открыть таблицу лидеров.\n"
                "(Слева снизу три полоски или кнопка меню)*")
    await message.answer(response)


# Счётчик баллов пользователя
def cal_score(user_id):
    if user_id in users:
        user_data = users[user_id]
        return user_data.get("score", 0)
    return 0


@dp.message(F.text == '/test')
async def test(message: types.Message):
    user_id = message.from_user.id

    if user_id in users:
        del users[user_id]

    users[user_id] = {"state": "waiting_for_lastname"}
    await ask_name(user_id, message.chat.id)


# Таблица лидеров
@dp.message(F.text == '/results')
async def table(message: types.Message):
    top_results = session.query(TestResult).order_by(TestResult.score.desc()).limit(5).all()

    if top_results:
        result_message = "Таблица лидеров:\n"
        for i, result in enumerate(top_results, start=1):
            result_message += f"{i}. {result.first_name} {result.last_name} - {result.score} баллов\n"
    else:
        result_message = "Пока что нет результатов."

    await message.answer(result_message)


async def ask_qvest(user_id, chat_id):
    user_data = users.get(user_id, {})
    current_question_index = user_data.get("current_question", 0)

    if current_question_index < len(qvest):
        question_data = qvest[current_question_index]
        question_text = question_data["question"]
        options = question_data["options"]
        message_text = f"{question_text}\n" + "\n".join(options)
        await bot.send_message(chat_id, message_text)
    else:
        score = cal_score(user_id)
        await bot.send_message(chat_id, f"Тест завершен. Ваш результат: {score} баллов из 10.",
                               reply_markup=ReplyKeyboardRemove())


async def ask_name(user_id, chat_id):
    await bot.send_message(chat_id, "Введите вашу фамилию:")
    users[user_id]["state"] = "waiting_for_lastname"


@dp.message(lambda message: users.get(message.from_user.id, {}).get("state") == "waiting_for_lastname")
async def lastname_user(message: types.Message):
    user_id = message.from_user.id
    users[user_id]["lastname"] = message.text
    await bot.send_message(message.chat.id, "Введите ваше имя:")
    users[user_id]["state"] = "waiting_for_firstname"


@dp.message(lambda message: users.get(message.from_user.id, {}).get("state") == "waiting_for_firstname")
async def firstname_user(message: types.Message):
    user_id = message.from_user.id
    users[user_id]["firstname"] = message.text
    await bot.send_message(message.chat.id, "Отвечать на ответы нужно цифрами: (1, 2, 3)", reply_markup=key)
    users[user_id]["state"] = "in_test"
    await ask_qvest(user_id, message.chat.id)


@dp.message(lambda message: users.get(message.from_user.id, {}).get("state") == "in_test" and message.text.isdigit() and 1 <= int(message.text) <= len(qvest[users.get(message.from_user.id, {}).get("current_question", 0)]["options"]))
async def end_test(message: types.Message):
    user_id = message.from_user.id
    user_data = users.get(user_id, {})
    current_question_index = user_data.get("current_question", 0)

    if current_question_index < len(qvest):
        question_data = qvest[current_question_index]
        correct_option = question_data["correct_option"]

        user_answer = int(message.text)
        if user_answer - 1 == correct_option:
            user_data["score"] = user_data.get("score", 0) + 1

        user_data["current_question"] = current_question_index + 1

        if user_data["current_question"] == len(qvest):
            score = user_data["score"]
            lastname = users[user_id]["lastname"]
            firstname = users[user_id]["firstname"]

            existing_user = session.query(TestResult).filter_by(user_id=user_id).first()

            if existing_user:
                existing_user.score = score
            else:
                new_user = TestResult(user_id=user_id, first_name=firstname, last_name=lastname, score=score)
                session.add(new_user)

            session.commit()

        await ask_qvest(user_id, message.chat.id)


async def run():
    await dp.start_polling(bot, token=API)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print('Выход')
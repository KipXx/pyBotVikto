from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.exc import IntegrityError

from date import models
from menu import key
from date.qvest import qvest
from run import users

router = Router()


@router.message(Command("test"))
async def test1(message: types.Message):
    user_id = message.from_user.id

    # Проверяем наличие пользователя в базе данных
    if not models.session.query(models.TestResult).filter_by(user_id=user_id).first():
        await message.answer("Перед тестом, вам необходимо зарегистрироваться. /register")
        return

    if user_id in users:
        del users[user_id]

    users[user_id] = {"state": "test", "score": 0, "current_question": 0}
    await ask_qvest(user_id, message)


@router.message()
async def answer(message: types.Message):
    user_id = message.from_user.id

    if user_id in users and users[user_id]["state"] == "test":
        score = users[user_id]["score"]
        current_question = users[user_id]["current_question"]

        if current_question < len(qvest):
            correct_option = qvest[current_question]["correct_option"]

            if message.text in ["1", "2", "3"]:
                selected_option = int(message.text) - 1
                if selected_option == correct_option:
                    score += 1

                users[user_id]["score"] = score
                users[user_id]["current_question"] += 1

                if current_question == len(qvest) - 1:
                    await message.answer(f"Тест окончен! Вы набрали {score} баллов из 10.",
                                         reply_markup=ReplyKeyboardRemove())

                    # Создайте новый экземпляр TestResult и сохраните его в базе данных
                    test_result = models.session.query(models.TestResult).filter_by(user_id=user_id).first()
                    if test_result:
                        test_result.score = score
                    else:
                        test_result = models.TestResult(user_id=user_id, score=score)
                        models.session.add(test_result)

                    try:
                        models.session.commit()
                    except IntegrityError:
                        models.session.rollback()
                        await message.answer("Ошибка при сохранении результатов в базе данных.")
                else:
                    await ask_qvest(user_id, message)
            else:
                await message.answer("Пожалуйста, выберите вариант ответа, введя только цифры 1, 2 или 3.")


async def ask_qvest(user_id, message: types.Message):
    current_question = users[user_id]["current_question"]
    question = qvest[current_question]["question"]
    options = qvest[current_question]["options"]

    response = f"{question}\n\n"
    for i, option in enumerate(options, start=1):
        response += f"{i}. {option}\n"

    await message.answer(response, reply_markup=key)
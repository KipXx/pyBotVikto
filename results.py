from aiogram import Router
from aiogram import types
from aiogram.filters import Command

from date.models import session, TestResult

router = Router()


@router.message(Command("results"))
async def results1(message: types.Message):
    top_results = session.query(TestResult).order_by(TestResult.score.desc()).limit(5).all()

    if top_results:
        response = "Таблица лидеров:\n"
        for i, result in enumerate(top_results, start=1):
            response += f"{i}. {result.first_name} {result.last_name} - {result.score} баллов\n"
    else:
        response = "Пока что нет результатов."

    session.close()

    await message.answer(response)
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.exc import IntegrityError

from date import models
from states import Form

router = Router()


@router.message(Command("register"))
async def regist(message: Message, state: FSMContext):
    await state.set_state(Form.lastname)
    await message.answer(
        "Введите своё имя:", reply_markup=ReplyKeyboardRemove())


@router.message(Form.lastname)
async def form_name(message: Message, state: FSMContext):
    await state.update_data(lastname=message.text)
    await state.set_state(Form.firstname)
    await message.answer(
        "Хорошо, теперь введите свою фамилию:")


@router.message(Form.firstname)
async def form_lastname(message: Message, state: FSMContext):
    await state.update_data(firstname=message.text)

    # Получите данные регистрации из состояния
    data = await state.get_data()
    first_name = data.get('firstname')
    last_name = data.get('lastname')
    user_id = message.from_user.id

    # Создайте новый экземпляр TestResult и сохраните его в базе данных
    test_result = models.TestResult(user_id=user_id, first_name=first_name, last_name=last_name)
    models.session.add(test_result)

    try:
        models.session.commit()
        await message.answer("Регистрация успешно завершена!")
    except IntegrityError:
        models.session.rollback()
        existing_result = models.session.query(models.TestResult).filter_by(user_id=user_id).first()
        existing_result.first_name = first_name
        existing_result.last_name = last_name
        models.session.commit()
        await message.answer("Регистрация успешно обновлена!")

    await state.clear()
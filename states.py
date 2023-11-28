from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    lastname = State()
    firstname = State()
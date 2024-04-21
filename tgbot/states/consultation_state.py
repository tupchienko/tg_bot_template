from aiogram.fsm.state import StatesGroup, State


class Consultation(StatesGroup):
    start = State()
    get_confirm_clear_chat = State()

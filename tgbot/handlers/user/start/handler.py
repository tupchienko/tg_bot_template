from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from infrastructure.database.models import User
from tgbot.commands.user_commands import set_user_defaults_commands
from tgbot.keyboards.inline.callback_data.consultation_keyboard import consultation_keyboard
from tgbot.states.consultation_state import Consultation

start_router = Router()


@start_router.message(CommandStart())
async def user_start(message: Message, bot: Bot, state: FSMContext, user: User):
    await set_user_defaults_commands(message.from_user.id, bot)
    await message.answer("Напишіть своє запитання ⤵️", reply_markup=consultation_keyboard())
    await state.clear()
    await state.set_state(Consultation.start)

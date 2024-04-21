
from aiogram import Router, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from infrastructure.database.models import User
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.handlers.user.consultation.utils import get_consultation
from tgbot.keyboards.inline.callback_data.clear_chat_data import ClearChatData
from tgbot.keyboards.inline.callback_data.confirm_data import ConfirmData
from tgbot.keyboards.inline.confirm_keyboard import confirm_keyboard
from tgbot.states.consultation_state import Consultation

consultation_router = Router()


@consultation_router.callback_query(StateFilter(Consultation.start), ClearChatData.filter())
async def clear_chat(call: CallbackQuery):
    text = ("Ви впевнені, що хочете очистити історію чату?")
    await call.message.edit_text(
        text,
        reply_markup=confirm_keyboard()
    )


@consultation_router.callback_query(StateFilter(Consultation.start), ConfirmData.filter())
async def clear_chat(call: CallbackQuery,
                     repo: RequestsRepo,
                     state: FSMContext,
                     callback_data: ConfirmData,
                     user: User):
    if callback_data.result:
        await repo.message.clear_messages(session_id=str(user.id))
        await call.message.edit_text(
            text=("<b>Розмова очищена ✅.</b>")
        )
        text = ("Напишіть своє запитання ⤵️")
        await call.message.answer(text=text)
        await state.set_state(Consultation.start)
    else:
        await call.message.delete()


@consultation_router.message(StateFilter(Consultation.start))
async def get_consultation_handler(message: Message,
                                   session: AsyncSession,
                                   repo: RequestsRepo,
                                   user: User,
                                   state: FSMContext,
                                   bot: Bot):
    await get_consultation(message, session, repo, user, state, bot)

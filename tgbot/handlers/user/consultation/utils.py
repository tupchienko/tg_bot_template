import logging
from typing import Optional

from aiogram import Bot
from aiogram.enums import ParseMode

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.ai_consultant.retriever import LLMArgs, run_index_llm
from infrastructure.database.models import User
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.handlers.user.consultation.llm_result import LLMResults
from tgbot.keyboards.inline.callback_data.consultation_keyboard import consultation_keyboard


async def handle_error_response(message_with_response: Message):
    text = ("Упс. Щось пішло не так, спробуйте пізніше.")
    await message_with_response.edit_text(text=text)


async def get_llm_response(user: User, session: AsyncSession, repo: RequestsRepo, question: str,
                           state: FSMContext) -> Optional[LLMResults]:
    messages = await repo.message.get_messages(session_id=str(user.id))

    llm_args = LLMArgs(
        messages=messages,
        session_id=str(user.id),
        question=question,
        session_pool=session,
    )
    try:
        result = await run_index_llm(llm_args)
        return LLMResults(text=result)
    except Exception as e:
        logging.error(e)


async def get_consultation(message: Message,
                           session_pool: AsyncSession,
                           repo: RequestsRepo,
                           user: User,
                           state: FSMContext,
                           bot: Bot):
    message_with_response = await message.answer(text=("Супер інтелект думає..."))

    question = message.text

    if not question:
        await handle_error_response(message_with_response)
        return

    llm_result = await get_llm_response(user, session_pool, repo, question, state)

    if not llm_result or not llm_result.text:
        await handle_error_response(message_with_response)
        return

    await message_with_response.delete()
    await message.answer(
        llm_result.text,
        reply_markup=consultation_keyboard(),
        parse_mode=ParseMode.MARKDOWN)
    await repo.users.track_messages_to_ai(user.id)
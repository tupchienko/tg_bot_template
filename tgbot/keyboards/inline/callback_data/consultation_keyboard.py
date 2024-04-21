from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.inline.callback_data.clear_chat_data import ClearChatData


def consultation_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=("Очистити 🧹"),
        callback_data=ClearChatData()
    )
    return builder.as_markup()
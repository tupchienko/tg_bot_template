from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.inline.callback_data.confirm_data import ConfirmData


def confirm_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅",
        callback_data=ConfirmData(result=True)
    )
    builder.button(
        text="❌",
        callback_data=ConfirmData(result=False)
    )
    builder.adjust(2)
    return builder.as_markup()
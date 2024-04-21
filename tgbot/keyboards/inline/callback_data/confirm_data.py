from aiogram.filters.callback_data import CallbackData


class ConfirmData(CallbackData, prefix='cfd'):
    result: bool

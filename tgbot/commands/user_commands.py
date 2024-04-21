from aiogram import types, Bot


async def set_user_defaults_commands(chat_id: int, bot: Bot):
    await bot.set_my_commands(commands=[
        types.BotCommand(command="start", description="🤖 Запуск бота"),
    ],
        scope=types.BotCommandScopeChat(chat_id=chat_id),
    )


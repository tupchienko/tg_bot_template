import asyncio
import logging

import betterlogging as bl
import openai
import pytz
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from alembic import command
from alembic.config import Config as AlembicConfig
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import load_config, Config
from infrastructure.database.setup import create_engine, create_session_pool
from tgbot.handlers import routers_list
from tgbot.handlers.user import start_router, consultation_router
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.services import broadcaster


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот був запущений")


def run_upgrade():
    try:
        config = AlembicConfig("alembic.ini")
        config.attributes['configure_logger'] = False

        logging.info("Starting database upgrade process")
        command.upgrade(config, "head")
        logging.info("Database upgrade completed successfully")

    except Exception as e:
        logging.error("An error occurred during database upgrade: %s", str(e))


def register_router(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(consultation_router)


def register_global_middlewares(dp: Dispatcher, config: Config, session_pool=None):
    middleware_types = [
        ConfigMiddleware(config),
        DatabaseMiddleware(session_pool),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config):
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def main():
    config = load_config(".env")
    storage = get_storage(config)
    openai.api_key = config.misc.openai_api_key
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage)
    scheduler = AsyncIOScheduler(timezone=pytz.UTC)
    register_router(dp)
    engine = create_engine(config.db)
    sqlalchemy_session_pool = create_session_pool(engine)
    register_global_middlewares(dp, config, session_pool=sqlalchemy_session_pool)

    scheduler.start()
    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        setup_logging()
        run_upgrade()
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот був вимкнений!")

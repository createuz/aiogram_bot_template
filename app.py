import asyncio
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from redis.asyncio import Redis

from data import conf, setup_logger, TransferData,get_redis_storage, get_dispatcher
from db.database import async_engine_builder
from handlers import prepare_router
from utils.aiogram_services import aiogram_on_startup_polling, aiogram_on_shutdown_polling


async def main() -> None:
    aiogram_session_logger = setup_logger().bind(type="aiogram_session")
    bot = Bot(token=conf.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = get_redis_storage(
        redis=Redis(
            host=conf.redis.host,
            password=conf.redis.password,
            port=conf.redis.port,
            db=conf.redis.db,
        )
    )
    dp = get_dispatcher(storage=storage)
    dp["aiogram_session_logger"] = aiogram_session_logger
    dp.startup.register(aiogram_on_startup_polling)
    dp.shutdown.register(aiogram_on_shutdown_polling)
    dp.include_router(prepare_router())
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
        **TransferData(engine=async_engine_builder(url=conf.db.build_db_url()))
    )


if __name__ == "__main__":
    logging.basicConfig(level=conf.logging_level)
    asyncio.run(main())

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from redis.asyncio import Redis

from core import conf, setup_logger
from handlers import prepare_router
from utils.aiogram_services import aiogram_on_startup_polling, aiogram_on_shutdown_polling


def main() -> None:
    aiogram_session_logger = setup_logger().bind(type="aiogram_session")
    bot = Bot(token=conf.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    fsm_strategy: FSMStrategy | None = FSMStrategy.USER_IN_CHAT
    dp = Dispatcher(
        storage=RedisStorage(
            redis=Redis(
                host=conf.redis.host,
                password=conf.redis.password,
                port=conf.redis.port,
                db=conf.redis.db
            ),
            state_ttl=conf.redis.state_ttl,
            data_ttl=conf.redis.data_ttl,
            key_builder=DefaultKeyBuilder(with_bot_id=True)
        ), fsm_strategy=fsm_strategy
    )
    dp["aiogram_session_logger"] = aiogram_session_logger
    dp.startup.register(aiogram_on_startup_polling)
    dp.shutdown.register(aiogram_on_shutdown_polling)
    dp.include_router(prepare_router())
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()

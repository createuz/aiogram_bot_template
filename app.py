import asyncio

from redis.asyncio import Redis

from data import conf, setup_logger, get_dispatcher, get_redis_storage, bot
from utils.aiogram_services import aiogram_on_startup_polling, aiogram_on_shutdown_polling


def main() -> None:
    aiogram_session_logger = setup_logger().bind(type="aiogram_session")
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
    asyncio.run(dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()))


if __name__ == "__main__":
    main()

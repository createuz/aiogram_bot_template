import asyncio

from aiohttp import web
from redis.asyncio import Redis

from data import bot, conf, setup_logger, get_redis_storage, get_dispatcher
from utils.aiogram_services import aiogram_on_startup_polling, aiogram_on_shutdown_polling, aiogram_on_startup_webhook, \
    aiogram_on_shutdown_webhook, setup_aiohttp_app


async def main() -> None:
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
    if not conf.webhook.enabled:
        print('webhook enabled True')
        dp.startup.register(aiogram_on_startup_webhook)
        dp.shutdown.register(aiogram_on_shutdown_webhook)
        web.run_app(
            asyncio.run(setup_aiohttp_app(bot, dp)),
            handle_signals=True,
            host='0.0.0.0',
            port=8080,
        )

    else:
        print('webhook enabled False')
        dp.startup.register(aiogram_on_startup_polling)
        dp.shutdown.register(aiogram_on_shutdown_polling)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())

" https://f0ea-92-63-205-165.ngrok-free.app/bot/7189528230:AAEayeWCvI0Jv7YufsMLW8CmqcLPQObbxyg"
get_webhook_info = "https://api.telegram.org/bot7189528230:AAEayeWCvI0Jv7YufsMLW8CmqcLPQObbxyg/getWebhookInfo"
set_webhook = "https://api.telegram.org/bot7189528230:AAEayeWCvI0Jv7YufsMLW8CmqcLPQObbxyg/setWebhook?url=https://f0ea-92-63-205-165.ngrok-free.app/bot/7189528230:AAEayeWCvI0Jv7YufsMLW8CmqcLPQObbxyg&secret_token=4411f20d872535bf80ab94eaf2c84238bca388352fce0af0a2244bddcc9306d5"

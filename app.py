import asyncio

import orjson
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from aiohttp import web
from redis.asyncio import Redis

from core import conf, setup_logger
from handlers import prepare_router
from utils.services import (aiogram_on_startup_webhook, aiogram_on_shutdown_webhook, setup_aiohttp_app,
                            aiogram_on_startup_polling, aiogram_on_shutdown_polling)
from utils.sessions import SmartAiogramAiohttpSession


def main() -> None:
    aiogram_session_logger = setup_logger().bind(type="aiogram_session")
    if conf.custom_api_server.enabled:
        session = SmartAiogramAiohttpSession(
            api=TelegramAPIServer(
                base=conf.custom_api_server.base_url,
                file=conf.custom_api_server.file_url,
                is_local=conf.custom_api_server.is_local,
            ),
            json_loads=orjson.loads, logger=aiogram_session_logger
        )
    else:
        session = SmartAiogramAiohttpSession(
            json_loads=orjson.loads,
            logger=aiogram_session_logger,
        )
    bot = Bot(token=conf.bot.token,  default=DefaultBotProperties(parse_mode=ParseMode.HTML))

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
        ),
        fsm_strategy=fsm_strategy
    )

    dp["aiogram_session_logger"] = aiogram_session_logger

    # if conf.webhook.enabled:
    #     dp.startup.register(aiogram_on_startup_webhook)
    #     dp.shutdown.register(aiogram_on_shutdown_webhook)
    #     web.run_app(
    #         asyncio.run(setup_aiohttp_app(bot, dp)),
    #         handle_signals=True,
    #         host=conf.webhook.listening_host,
    #         port=conf.webhook.listening_port
    #     )
    # else:
    dp.startup.register(aiogram_on_startup_polling)
    dp.shutdown.register(aiogram_on_shutdown_polling)
    dp.include_router(prepare_router())
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()

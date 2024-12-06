import asyncio
import aiojobs
import asyncpg as asyncpg
import orjson
import redis
import structlog
import tenacity
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiohttp import web
import utils
from core import *
from handlers import prepare_router
from utils.tg_updates import tg_updates_app


async def create_db_connections(dp: Dispatcher) -> None:
    logger: structlog.typing.FilteringBoundLogger = dp["business_logger"]

    logger.debug("Connecting to PostgreSQL", db="main")
    try:
        db_pool = await utils.connect_to_services.wait_postgres(
            logger=dp["db_logger"],
            host=conf.db.host,
            port=conf.db.port,
            user=conf.db.user,
            password=conf.db.password,
            database=conf.db.name
        )
    except tenacity.RetryError:
        logger.error("Failed to connect to PostgreSQL", db="main")
        exit(1)
    else:
        logger.debug("Succesfully connected to PostgreSQL", db="main")
    dp["db_pool"] = db_pool

    # if conf.cache.enabled:
    #     logger.debug("Connecting to Redis")
    #     try:
    #         redis_pool = await utils.connect_to_services.wait_redis_pool(
    #             logger=dp["cache_logger"],
    #             host=conf.cache.host,
    #             port=conf.cache.port,
    #             database=0,
    #         )
    #     except tenacity.RetryError:
    #         logger.error("Failed to connect to Redis")
    #         exit(1)
    #     else:
    #         logger.debug("Succesfully connected to Redis")
    #     dp["cache_pool"] = redis_pool

    dp["temp_bot_cloud_session"] = utils.smart_session.SmartAiogramAiohttpSession(
        json_loads=orjson.loads,
        logger=dp["aiogram_session_logger"],
    )
    if conf.custom_api_server.enabled:
        dp["temp_bot_local_session"] = utils.smart_session.SmartAiogramAiohttpSession(
            api=TelegramAPIServer(
                base=conf.custom_api_server.base_url,
                file=conf.custom_api_server.file_url,
                is_local=conf.custom_api_server.is_local,
            ),
            json_loads=orjson.loads,
            logger=dp["aiogram_session_logger"],
        )


async def close_db_connections(dp: Dispatcher) -> None:
    if "temp_bot_cloud_session" in dp.workflow_data:
        temp_bot_cloud_session: AiohttpSession = dp["temp_bot_cloud_session"]
        await temp_bot_cloud_session.close()
    if "temp_bot_local_session" in dp.workflow_data:
        temp_bot_local_session: AiohttpSession = dp["temp_bot_local_session"]
        await temp_bot_local_session.close()
    if "db_pool" in dp.workflow_data:
        db_pool: asyncpg.Pool = dp["db_pool"]
        await db_pool.close()
    if "cache_pool" in dp.workflow_data:
        cache_pool: redis.asyncio.Redis = dp["cache_pool"]  # type: ignore[type-arg]
        await cache_pool.close()


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(prepare_router())


def setup_middlewares(dp: Dispatcher) -> None:
    dp.update.outer_middleware(StructLoggingMiddleware(logger=dp["aiogram_logger"]))


def setup_logging(dp: Dispatcher) -> None:
    dp["aiogram_logger"] = setup_logger().bind(type="aiogram")
    dp["db_logger"] = setup_logger().bind(type="db")
    dp["cache_logger"] = setup_logger().bind(type="cache")
    dp["business_logger"] = setup_logger().bind(type="business")


async def setup_aiogram(dp: Dispatcher) -> None:
    setup_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")
    await create_db_connections(dp)
    setup_handlers(dp)
    setup_middlewares(dp)
    logger.info("Configured aiogram")


async def aiohttp_on_startup(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_startup(**workflow_data)


async def aiohttp_on_shutdown(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    for i in [app, *app._subapps]:  # dirty
        if "scheduler" in i:
            scheduler: aiojobs.Scheduler = i["scheduler"]
            scheduler._closed = True
            while scheduler.pending_count != 0:
                dp["aiogram_logger"].info(
                    f"Waiting for {scheduler.pending_count} tasks to complete"
                )
                await asyncio.sleep(1)
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_shutdown(**workflow_data)


async def aiogram_on_startup_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    await setup_aiogram(dispatcher)
    webhook_logger = dispatcher["aiogram_logger"].bind(
        webhook_url=conf.webhook.address
    )
    webhook_logger.debug("Configuring webhook")
    await bot.set_webhook(
        url=conf.webhook.address.format(
            token=conf.bot.token, bot_id=conf.bot.token.split(":")[0]
        ),
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=conf.webhook.secret_token,
    )
    webhook_logger.info("Configured webhook")


async def aiogram_on_shutdown_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping webhook")
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped webhook")


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(dispatcher)
    dispatcher["aiogram_logger"].info("Started polling")


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping polling")
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped polling")


async def setup_aiohttp_app(bot: Bot, dp: Dispatcher) -> web.Application:
    scheduler = aiojobs.Scheduler()
    app = web.Application()
    subapps: list[tuple[str, web.Application]] = [
        ("/tg/webhooks/", tg_updates_app),
    ]
    for prefix, subapp in subapps:
        subapp["bot"] = bot
        subapp["dp"] = dp
        subapp["scheduler"] = scheduler
        app.add_subapp(prefix, subapp)
    app["bot"] = bot
    app["dp"] = dp
    app["scheduler"] = scheduler
    app.on_startup.append(aiohttp_on_startup)
    app.on_shutdown.append(aiohttp_on_shutdown)
    return app


def main() -> None:
    aiogram_session_logger = setup_logger().bind(type="aiogram_session")

    if conf.custom_api_server.enabled:
        session = utils.smart_session.SmartAiogramAiohttpSession(
            api=TelegramAPIServer(
                base=conf.custom_api_server.base_url,
                file=conf.custom_api_server.file_url,
                is_local=conf.custom_api_server.is_local,
            ),
            json_loads=orjson.loads,
            logger=aiogram_session_logger,
        )
    else:
        session = utils.smart_session.SmartAiogramAiohttpSession(
            json_loads=orjson.loads,
            logger=aiogram_session_logger,
        )
    bot = Bot(token=conf.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # storage: RedisStorage = RedisStorage(
    #     redis=Redis.from_url(url=conf.redis.build_redis_url()),
    #     state_ttl=conf.redis.state_ttl,
    #     data_ttl=conf.redis.data_ttl,
    #     key_builder=DefaultKeyBuilder(with_bot_id=True)
    # )
    fsm_strategy: FSMStrategy | None = FSMStrategy.CHAT
    dp = Dispatcher(
        storage=MemoryStorage(),
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
    #         port=conf.webhook.listening_port,
    #     )
    # else:
    dp.startup.register(aiogram_on_startup_polling)
    dp.shutdown.register(aiogram_on_shutdown_polling)
    dp.include_router(prepare_router())
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()

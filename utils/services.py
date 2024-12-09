import asyncio
import logging

import aiojobs
import asyncpg as asyncpg
import orjson
import redis
import structlog
import tenacity
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiohttp import web
from redis.asyncio import ConnectionPool
from redis.asyncio import Redis
from tenacity import _utils  # noqa: PLC2701

from core import *
from handlers import prepare_router
from utils.sessions import SmartAiogramAiohttpSession
from utils.updates import tg_updates_app

TIMEOUT_BETWEEN_ATTEMPTS = 2
MAX_TIMEOUT = 30


def before_log(retry_state: tenacity.RetryCallState) -> None:
    """
    Log information about retry attempts before they are executed.
    """
    if retry_state.outcome is None:
        return

    # Determine the outcome type and corresponding message
    if retry_state.outcome.failed:
        verb, value = "raised", retry_state.outcome.exception()
    else:
        verb, value = "returned", retry_state.outcome.result()

    # Extract logger from kwargs, with a fallback if not provided
    logger = retry_state.kwargs.get("logger", logging.getLogger(__name__))

    # Log retry information with structured context for better debugging
    logger.info(
        f"Retrying '{_utils.get_callback_name(retry_state.fn)}' in {retry_state.next_action.sleep} seconds "
        f"as it {verb} {value}",
        extra={
            "callback": _utils.get_callback_name(retry_state.fn),
            "sleep": retry_state.next_action.sleep,
            "verb": verb,
            "value": str(value),  # Ensure value is string-safe
            "attempt_number": retry_state.attempt_number,
        },
    )


def after_log(retry_state: tenacity.RetryCallState) -> None:
    """
    Log information after a retryable function has been executed.
    """
    # Extract logger from kwargs, with a fallback if not provided
    logger = retry_state.kwargs.get("logger", logging.getLogger(__name__))

    # Log completion information with structured context for better debugging
    logger.info(
        f"Finished call to '{_utils.get_callback_name(retry_state.fn)}' "
        f"after {retry_state.seconds_since_start:.2f} seconds. "
        f"This was the {_utils.to_ordinal(retry_state.attempt_number)} attempt.",
        extra={
            "callback": _utils.get_callback_name(retry_state.fn),
            "time": retry_state.seconds_since_start,
            "attempt": _utils.to_ordinal(retry_state.attempt_number),
        },
    )


@tenacity.retry(
    wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
    stop=tenacity.stop_after_delay(MAX_TIMEOUT),
    before_sleep=before_log,
    after=after_log
)
async def wait_postgres(
        logger: structlog.typing.FilteringBoundLogger,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
) -> asyncpg.Pool:
    db_pool = await asyncpg.create_pool(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        min_size=1,
        max_size=3
    )
    version = await db_pool.fetchrow("SELECT version() as ver;")
    logger.debug("Connected to PostgreSQL.", version=version["ver"])
    return db_pool


@tenacity.retry(
    wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
    stop=tenacity.stop_after_delay(MAX_TIMEOUT),
    before_sleep=before_log,
    after=after_log
)
async def wait_redis_pool(
        logger: structlog.typing.FilteringBoundLogger,
        host: str,
        port: int,
        password: str,
        database: int,
) -> redis.asyncio.Redis:
    redis_pool: redis.asyncio.Redis = Redis(
        connection_pool=ConnectionPool(
            host=host,
            port=port,
            password=password,
            db=database,
        )
    )
    version = await redis_pool.info("server")
    logger.debug("Connected to Redis.", version=version["redis_version"])
    return redis_pool


async def create_db_connections(dp: Dispatcher) -> None:
    logger: structlog.typing.FilteringBoundLogger = dp["business_logger"]

    logger.debug("Connecting to PostgreSQL", db="main")
    try:
        db_pool = await wait_postgres(
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

    if conf.cache.enabled:
        logger.debug("Connecting to Redis")
        try:
            redis_pool = await wait_redis_pool(
                logger=dp["cache_logger"],
                host=conf.cache.host,
                port=conf.cache.port,
                password=conf.cache.password,
                database=0
            )
        except tenacity.RetryError:
            logger.error("Failed to connect to Redis")
            exit(1)
        else:
            logger.debug("Succesfully connected to Redis")
        dp["cache_pool"] = redis_pool

    dp["temp_bot_cloud_session"] = SmartAiogramAiohttpSession(
        json_loads=orjson.loads,
        logger=dp["aiogram_session_logger"],
    )
    if conf.custom_api_server.enabled:
        dp["temp_bot_local_session"] = SmartAiogramAiohttpSession(
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
        cache_pool: redis.asyncio.Redis = dp["cache_pool"]
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
    webhook_logger = dispatcher["aiogram_logger"].bind(webhook_url=conf.webhook.address)
    webhook_logger.debug("Configuring webhook")
    await bot.set_webhook(
        url=conf.webhook.address.format(token=conf.bot.token, bot_id=conf.bot.token.split(":")[0]),
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=conf.webhook.secret_token
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
    subapps: list[tuple[str, web.Application]] = [("/tg/webhooks/", tg_updates_app)]
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

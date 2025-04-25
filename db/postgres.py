import asyncpg as asyncpg
import orjson
import redis
import structlog
import tenacity
from aiogram import Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from redis.asyncio import ConnectionPool
from redis.asyncio import Redis
from tenacity import _utils

from data import conf
from utils.sessions import SmartAiogramAiohttpSession

TIMEOUT_BETWEEN_ATTEMPTS = 2
MAX_TIMEOUT = 30


def before_log(retry_state: tenacity.RetryCallState) -> None:
    if retry_state.outcome is None:
        return
    if retry_state.outcome.failed:
        verb, value = "raised", retry_state.outcome.exception()
    else:
        verb, value = "returned", retry_state.outcome.result()
    logger = retry_state.kwargs["logger"]
    logger.info(
        "Retrying {callback} in {sleep} seconds as it {verb} {value}",
        callback=_utils.get_callback_name(retry_state.fn),  # type: ignore[arg-type]
        sleep=retry_state.next_action.sleep,  # type: ignore[union-attr]
        verb=verb,
        value=value,
        extra={
            "callback": _utils.get_callback_name(retry_state.fn),  # type: ignore[arg-type]
            "sleep": retry_state.next_action.sleep,  # type: ignore[union-attr]
            "verb": verb,
            "value": value,
        },
    )


def after_log(retry_state: tenacity.RetryCallState) -> None:
    logger = retry_state.kwargs["logger"]
    logger.info(
        "Finished call to {callback!r} after {time:.2f}, this was the {attempt} time calling it.",
        callback=_utils.get_callback_name(retry_state.fn),  # type: ignore[arg-type]
        time=retry_state.seconds_since_start,
        attempt=_utils.to_ordinal(retry_state.attempt_number),
        extra={
            "callback": _utils.get_callback_name(retry_state.fn),  # type: ignore[arg-type]
            "time": retry_state.seconds_since_start,
            "attempt": _utils.to_ordinal(retry_state.attempt_number),
        },
    )


@tenacity.retry(
    wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
    stop=tenacity.stop_after_delay(MAX_TIMEOUT),
    before_sleep=before_log,
    after=after_log,
    reraise=True
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
    after=after_log,
    reraise=True
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
                host=conf.redis.host,
                port=conf.redis.port,
                password=conf.redis.password,
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
        logger=dp["aiogram_session_logger"]
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
        cache_pool: redis.asyncio.Redis = dp["cache_pool"]  # type: ignore[type-arg]
        await cache_pool.close()

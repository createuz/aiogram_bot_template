import logging

import asyncpg as asyncpg
import orjson
import redis
import structlog
import tenacity
from aiogram import Dispatcher
from redis.asyncio import ConnectionPool
from redis.asyncio import Redis
from tenacity import _utils

from data import conf
from db.database import db
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

    logger = retry_state.kwargs.get("logger", logging.getLogger(__name__))
    logger.info(
        f"Retrying '{_utils.get_callback_name(retry_state.fn)}' in {retry_state.next_action.sleep} seconds "
        f"as it {verb} {value}",
        extra={
            "callback": _utils.get_callback_name(retry_state.fn),
            "sleep": retry_state.next_action.sleep,
            "verb": verb,
            "value": str(value),
            "attempt_number": retry_state.attempt_number,
        },
    )


def after_log(retry_state: tenacity.RetryCallState) -> None:
    logger = retry_state.kwargs.get("logger", logging.getLogger(__name__))
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
        json_loads=orjson.loads, logger=dp["aiogram_session_logger"])


async def close_db_connections(dp: Dispatcher) -> None:
    if "db_pool" in dp.workflow_data:
        db_pool: asyncpg.Pool = dp["db_pool"]
        await db_pool.close()
    if "cache_pool" in dp.workflow_data:
        cache_pool: redis.asyncio.Redis = dp["cache_pool"]
        await cache_pool.close()


async def setup_database(logger):
    await wait_postgres(
        logger=logger,
        host=conf.db.host,
        port=conf.db.port,
        user=conf.db.user,
        password=conf.db.password,
        database=conf.db.name,
    )
    await db.init()
    logger.info("Database setup completed.")

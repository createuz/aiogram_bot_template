import json
import logging
from datetime import datetime
from functools import wraps

import asyncpg as asyncpg
import orjson
import redis
import redis.asyncio as aioredis
import structlog
import tenacity
from aiogram import Dispatcher
from redis.asyncio import ConnectionPool
from redis.asyncio import Redis
from sqlalchemy import DateTime, Integer, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from sqlalchemy.orm import declarative_base
from tenacity import _utils

from core import conf
from utils.sessions import SmartAiogramAiohttpSession

TIMEOUT_BETWEEN_ATTEMPTS = 2
MAX_TIMEOUT = 30

Base = declarative_base()

# metadata = MetaData(
#     naming_convention={
#         'ix': 'ix_%(column_0_label)s',
#         'uq': 'uq_%(table_name)s_%(column_0_name)s',
#         'ck': 'ck_%(table_name)s_%(constraint_name)s',
#         'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
#         'pk': 'pk_%(table_name)s',
#     }
# )
#
#
# @as_declarative(metadata=metadata)
# class Base:
#     __allow_unmapped__ = False
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
#
#     @classmethod
#     @declared_attr
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()


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
        json_loads=orjson.loads,
        logger=dp["aiogram_session_logger"],
    )


async def close_db_connections(dp: Dispatcher) -> None:
    if "db_pool" in dp.workflow_data:
        db_pool: asyncpg.Pool = dp["db_pool"]
        await db_pool.close()
    if "cache_pool" in dp.workflow_data:
        cache_pool: redis.asyncio.Redis = dp["cache_pool"]
        await cache_pool.close()


class AsyncDatabaseSession:
    def __init__(self, db_url: str):
        self._engine = create_async_engine(url=db_url, future=True, echo=True)
        self._SessionMaker = async_sessionmaker(bind=self._engine, expire_on_commit=False, class_=AsyncSession)

    async def get_session(self):
        async with self._SessionMaker() as session:
            yield session

    async def init(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


db = AsyncDatabaseSession(db_url=conf.db.build_connection_str())


class RedisCache:
    def __init__(self, url: str):
        self._redis = aioredis.from_url(url=url, decode_responses=True)

    async def get(self, key: str):
        value = await self._redis.get(key)
        if value is None:
            logging.debug(f"Cache miss for key: {key}")
        else:
            logging.debug(f"Cache hit for key: {key}")
        return value

    async def set(self, key: str, value: str, expire: int = 3600):
        await self._redis.set(key, value, ex=expire)

    async def delete(self, key: str):
        await self._redis.delete(key)

    @property
    def redis(self):
        return self._redis


cache: RedisCache = RedisCache(url=conf.redis.build_redis_url())


def cache_result(expire: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            chat_id = kwargs.get('chat_id') or args[1]
            cache_key = f"{func.__name__}_{chat_id}"
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return json.loads(cached_value)
            result = await func(*args, **kwargs)
            if result is not None:
                await cache.set(cache_key, json.dumps(result), expire)
            return result

        return wrapper

    return decorator


async def setup_database(logger):
    await wait_postgres(
        logger=logger,
        host=conf.db.host,
        port=conf.db.port,
        user=conf.db.user,
        password=conf.db.password,
        database=conf.db.database,
    )
    await db.init()
    logger.info("Database setup completed.")

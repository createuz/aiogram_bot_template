import json
import logging
from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncIterator, TypedDict

from aiogram import Bot
from redis.asyncio import Redis
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from data import conf

Base = declarative_base()


def async_engine_builder(url: URL | str) -> AsyncEngine:
    return create_async_engine(
        url=url,
        future=True,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


class AsyncDatabase:
    def __init__(self, db_url: str):
        self._engine = async_engine_builder(url=db_url)
        self._SessionMaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            future=True,  # 2.0 API uslubi
            autoflush=False,  # Qo'lda sinxronlash
            autocommit=False,  # Qo'lda commit
            class_=AsyncSession  # Asinxron sessiya klassi
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        async with self._SessionMaker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    async def init(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self):
        await self._engine.dispose()


db: AsyncDatabase = AsyncDatabase(db_url=conf.db.build_db_url())


class TransferData(TypedDict):
    """Common transfer data."""

    engine: AsyncEngine
    db: db
    bot: Bot


class RedisCache:
    def __init__(self, url: str):
        self._redis = Redis.from_url(url=url, decode_responses=True)

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

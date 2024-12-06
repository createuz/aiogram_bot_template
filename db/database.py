import json
from functools import wraps
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from core import conf
from core.config import logger

Base = declarative_base()


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
            logger.debug(f"Cache miss for key: {key}")
        else:
            logger.debug(f"Cache hit for key: {key}")
        return value

    async def set(self, key: str, value: str, expire: int = 3600):
        await self._redis.set(key, value, ex=expire)

    async def delete(self, key: str):
        await self._redis.delete(key)

    @property
    def redis(self):
        return self._redis


cache: RedisCache = RedisCache(url=conf.redis.build_redis_url() )


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


# def cache_result(expire: int = None):
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(*args, **kwargs):
#             key_parts = [func.__name__] + [str(arg) for arg in args] + [f"{k}={v}" for k, v in kwargs.items()]
#             cache_key = ":".join(key_parts)
#             cached_value = await cache.get(cache_key)
#             if cached_value is not None:
#                 return json.loads(cached_value)
#             result = await func(*args, **kwargs)
#             if result is not None:
#                 await cache.set(cache_key, json.dumps(result), expire)
#             return result
#         return wrapper
#     return decorator
import collections.abc
import typing

from aiogram import Dispatcher
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from redis.asyncio.client import Redis

T = typing.TypeVar("T")


def chunks(list_to_split: typing.Sequence[T], chunk_size: int) -> collections.abc.Iterator[typing.Sequence[T]]:
    for i in range(0, len(list_to_split), chunk_size):
        yield list_to_split[i: i + chunk_size]


def get_redis_storage(
        redis: Redis,
        state_ttl=3600,
        data_ttl=7200
):
    key_builder = DefaultKeyBuilder(with_bot_id=True)
    return RedisStorage(redis=redis, state_ttl=state_ttl, data_ttl=data_ttl, key_builder=key_builder)


def get_dispatcher(
        storage: BaseStorage = MemoryStorage(),
        fsm_strategy: FSMStrategy | None = FSMStrategy.CHAT,
        event_isolation: BaseEventIsolation | None = None,
):
    dp = Dispatcher(
        storage=storage,
        fsm_strategy=fsm_strategy,
        events_isolation=event_isolation,
    )
    return dp

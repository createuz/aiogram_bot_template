from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

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

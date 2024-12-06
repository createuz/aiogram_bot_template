import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Column, String, Integer, func, BigInteger, update, DateTime, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship

from .statistic_models import Statistics
from db.database import Base, db, cache


def generate_uid():
    return secrets.token_hex(3)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(10), default=generate_uid, unique=True, index=True, nullable=False)
    chat_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    language = Column(String, nullable=False)
    added_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_statistics = relationship("Statistics", uselist=False, back_populates="user")

    @classmethod
    async def create_user(cls, session: AsyncSession, chat_id: int, username: str, first_name: str, language: str,
                          added_by: str) -> 'User':
        user = cls(chat_id=chat_id, username=username, first_name=first_name, language=language, added_by=added_by)
        session.add(user)
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise RuntimeError(f"Error updating language: {e}")
        return user

    @classmethod
    async def create_statistics(cls, user: 'User', session: AsyncSession):
        new_statistics = Statistics(chat_id=user.chat_id)
        session.add(new_statistics)
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise RuntimeError(f"Error creating statistics: {e}")

    @classmethod
    async def get_language(cls, chat_id: int) -> Optional[str]:
        async for session in db.get_session():
            return await session.scalar(select(cls.language).where(chat_id == cls.chat_id))

    @classmethod
    async def update_language(cls, chat_id: int, language: str):
        async for session in db.get_session():
            await session.execute(update(cls).where(cls.chat_id == chat_id).values(language=language))
            try:
                await session.commit()
                cache_key = f"get_language_{chat_id}"
                await cache.delete(cache_key)
                await cache.set(cache_key, language, 3600)
            except Exception as e:
                await session.rollback()
                raise RuntimeError(f"Error updating language: {e}")

    @classmethod
    # @cache_result(expire=3600)
    async def get_uid(cls, chat_id: int) -> Optional[str]:
        async for session in db.get_session():
            return await session.scalar(select(cls.uid).where(chat_id == cls.chat_id))

    @classmethod
    async def update_uid(cls, chat_id: int, uid: str):
        async for session in db.get_session():
            await session.execute(update(cls).where(cls.chat_id == chat_id).values(uid=uid))
            try:
                await session.commit()
                cache_key = f"get_uid_{chat_id}"
                await cache.delete(cache_key)
                await cache.set(cache_key, uid, 3600)
            except Exception as e:
                await session.rollback()
                raise RuntimeError(f"Error updating UID: {e}")

    @classmethod
    async def check_uid(cls, uid: str) -> bool:
        async for session in db.get_session():
            return await session.scalar(select(cls.uid).where(cls.uid == uid)) is not None

    @classmethod
    async def get_user(cls, chat_id: int) -> Optional[tuple]:
        async for session in db.get_session():
            user = await session.scalar(select(cls).where(chat_id == cls.chat_id))
            if user:
                return user.chat_id, user.username, user.first_name
            return None, None, None

    @classmethod
    async def get_chat_id(cls, uid: str) -> Optional[int]:
        async for session in db.get_session():
            return await session.scalar(select(cls.chat_id).where(uid == cls.uid))

    @classmethod
    async def get_user_data(cls, chat_id: int) -> Optional[tuple]:
        async for session in db.get_session():
            user = await session.scalar(select(cls).where(chat_id == cls.chat_id))
            if user:
                return user.chat_id, user.username, user.first_name
        return None, None, None

    @classmethod
    async def get_all_users(cls, admin_lang: str = None):
        async for session in db.get_session():
            query = select(cls.chat_id)
            if admin_lang:
                query = query.where(cls.language == ('Uzbek' if admin_lang == 'Uzbek' else cls.language != 'Uzbek'))
            result = await session.execute(query)
            return [row[0] for row in result.scalars().all()]

    @classmethod
    async def joined_last_month(cls) -> Optional[int]:
        last_month = datetime.now() - timedelta(days=30)
        async for session in db.get_session():
            return await session.scalar(select(func.count(cls.chat_id)).where(cls.created_at >= last_month))

    @classmethod
    async def joined_last_24_hours(cls) -> Optional[int]:
        last_24_hours = datetime.now() - timedelta(hours=24)
        async for session in db.get_session():
            return await session.scalar(select(func.count(cls.chat_id)).where(
                and_(cls.created_at >= last_24_hours, cls.created_at <= datetime.now())))

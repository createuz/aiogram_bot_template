from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, BigInteger, DateTime, ForeignKey, Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, selectinload, Mapped, mapped_column

from db.database import Base, db

association = Table(
    'friends', Base.metadata,
    Column('user_id', BigInteger, ForeignKey('users.chat_id'), primary_key=True),
    Column('friend_id', BigInteger, ForeignKey('users.chat_id'), primary_key=True)
)


class Statistic(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.chat_id'), unique=True, index=True, nullable=False)
    messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    daily_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_message_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    popularity: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="user_statistic")
    friends = relationship(
        'Statistic', secondary=association,
        primaryjoin=chat_id == association.c.user_id,
        secondaryjoin=chat_id == association.c.friend_id,
        backref='friends_of',
        lazy='selectin'
    )

    @classmethod
    async def add_friends(cls, user_id: int, friend_id: int):
        if user_id == friend_id:
            raise ValueError("A user cannot be friends with themselves.")
        try:
            async with db.get_session() as session:
                stmt = select(cls).where(cls.chat_id.in_([user_id, friend_id])).options(selectinload(cls.friends))
                result = await session.execute(stmt)
                users = result.scalars().all()
                if len(users) != 2:
                    raise ValueError("One or both users not found.")
                user1, user2 = users
                if user2 not in user1.friends:
                    user1.friends.append(user2)
                if user1 not in user2.friends:
                    user2.friends.append(user1)
                await session.commit()
        except Exception as e:
            await session.rollback()
            raise RuntimeError(f"Database operation failed: {e}")

    @classmethod
    async def update_statistics(
            cls,
            chat_id: int,
            messages: bool = False,
            clicks: bool = False,
            popularity: bool = False,
    ) -> None:
        try:
            async with db.get_session() as session:
                stats: Optional[Statistic] = await session.scalar(select(cls).where(cls.chat_id == chat_id))
                if not stats:
                    return None
                now = datetime.now()
                if messages:
                    if stats.last_message_date and stats.last_message_date.date() != now.date():
                        stats.daily_messages = 0
                    stats.messages += 1
                    stats.daily_messages += 1
                if clicks:
                    stats.clicks += 1
                if popularity:
                    stats.popularity += 1
                stats.last_message_date = now
                stats.updated_at = now
                await session.commit()
        except Exception as e:
            await session.rollback()
            raise RuntimeError(f"Error updating statistics: {e}")

    @classmethod
    async def get_statistics(cls, chat_id: int) -> Optional[dict]:
        try:
            async with db.get_session() as session:
                stmt = select(cls).where(cls.chat_id == chat_id).options(selectinload(cls.friends))
                stats: Optional[Statistic] = (await session.execute(stmt)).scalar_one_or_none()
                if not stats:
                    return None
                now = datetime.now()
                if not stats.last_message_date or stats.last_message_date.date() != now.date():
                    stats.daily_messages = 0

                return {
                    'messages': stats.messages,
                    'daily_messages': stats.daily_messages,
                    'friends': len(stats.friends),
                    'clicks': stats.clicks,
                    'popularity': stats.popularity,
                }
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error retrieving statistics: {e}")

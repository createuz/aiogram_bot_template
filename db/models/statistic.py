from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, BigInteger, DateTime, ForeignKey, Table
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, selectinload

from db.database import Base, db

association = Table(
    'friends', Base.metadata,
    Column('user_id', BigInteger, ForeignKey('users.chat_id'), primary_key=True),
    Column('friend_id', BigInteger, ForeignKey('users.chat_id'), primary_key=True)
)


class Statistic(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey('users.chat_id'), unique=True, index=True, nullable=False)
    messages = Column(Integer, default=0, nullable=False)
    daily_messages = Column(Integer, default=0, nullable=False)
    last_message_date = Column(DateTime, nullable=True)
    clicks = Column(Integer, default=0, nullable=False)
    popularity = Column(Integer, default=1000, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="user_statistics")
    friends = relationship(
        'Statistics', secondary=association,
        primaryjoin=chat_id == association.c.user_id,
        secondaryjoin=chat_id == association.c.friend_id,
        backref='friends_of',
        lazy='selectin'
    )

    @classmethod
    async def add_friends(cls, user_id: int, friend_id: int):
        if user_id == friend_id:
            raise ValueError("A user cannot be friends with themselves.")
        async for session in db.get_session():
            try:
                stmt = select(cls).where(cls.chat_id.in_([user_id, friend_id])).options(selectinload(cls.friends))
                users = (await session.execute(stmt)).scalars().all()
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
                raise RuntimeError(f"Error adding friends: {e}")

    @classmethod
    async def update_statistics(
            cls,
            chat_id: int,
            messages: bool = False,
            clicks: bool = False,
            popularity: bool = False
    ) -> Optional[None]:

        async for session in db.get_session():
            try:
                stats: Optional[Statistics] = await session.scalar(select(cls).where(cls.chat_id == chat_id))
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
        async for session in db.get_session():
            try:
                stmt = select(cls).where(cls.chat_id == chat_id).options(selectinload(cls.friends))
                stats: Optional[Statistics] = (await session.execute(stmt)).scalar_one_or_none()
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
                    'popularity': stats.popularity
                }
            except Exception as e:
                raise RuntimeError(f"Error retrieving statistics: {e}")

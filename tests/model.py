import secrets
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Integer, Boolean, DateTime, BigInteger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column

from tests.db_system import Base


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def generate_uid() -> str:
    return secrets.token_hex(3)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String(10), default=generate_uid, unique=True, index=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    added_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    @classmethod
    async def create_user(
            cls,
            session: AsyncSession,
            chat_id: int,
            username: Optional[str],
            first_name: Optional[str],
            language: str,
            added_by: Optional[str],
    ) -> "User":
        try:
            user = cls(
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                language=language,
                added_by=added_by,
            )
            session.add(user)
            await session.commit()
            return user
        except SQLAlchemyError as e:
            await session.rollback()
            raise RuntimeError(f"Error creating user: {e}")

    @classmethod
    async def get_user(cls, session: AsyncSession, chat_id: int) -> Optional["User"]:
        try:
            stmt = select(cls).where(cls.chat_id == chat_id)
            user: Optional[User] = (await session.execute(stmt)).scalar_one_or_none()
            return user
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error retrieving user: {e}")

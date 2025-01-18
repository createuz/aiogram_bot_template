from typing import Optional

from sqlalchemy import String, Integer, BigInteger, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base, db


class Admin(Base):
    __tablename__ = 'admins'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    @classmethod
    async def create_admin(
            cls,
            session: AsyncSession,
            chat_id: int,
            username: Optional[str],
            first_name: Optional[str],
            language: str
    ) -> "Admin":
        try:
            admin = cls(
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                language=language,
            )
            session.add(admin)
            await cls.commit_session(session)
            return admin
        except SQLAlchemyError as e:
            await session.rollback()
            raise RuntimeError(f"Error creating user: {e}")

    @staticmethod
    async def commit_session(session: AsyncSession):
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise RuntimeError(f"Database operation failed: {e}")

    @classmethod
    async def get_admins_data(cls):
        async for session in db.get_session():
            users = await session.execute(select(cls.chat_id, cls.first_name))
            if users:
                return [user for user in users]
        return None

    @classmethod
    async def get_all_admin(cls):
        async for session in db.get_session():
            result = await session.execute(select(cls.chat_id))
            return [row[0] for row in result.all()]

    @classmethod
    async def delete_admin(cls, chat_id):
        query = delete(cls).where(cls.chat_id == int(chat_id))
        async for session in db.get_session():
            await session.execute(query)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            return True

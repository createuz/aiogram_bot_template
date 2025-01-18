from aiogram import Router
from aiogram import html, types
from aiogram.filters import CommandStart

from data import ChatTypeFilter, TextFilter
from db import db, User


async def start(msg: types.Message) -> None:
    async with db.get_session() as session:
        try:
            user = await User.create_user(
                session=session,
                chat_id=msg.chat.id,
                username=msg.chat.username,
                first_name=msg.chat.first_name,
                is_premium=msg.from_user.is_premium,
                language='Uzbek',
                added_by='bot'
            )
            await session.refresh(user)
            await User.create_statistics(user, session)
            retrieved_user = await User.get_users(session=session, chat_id=msg.chat.id)
            if retrieved_user:
                print(f"Retrieved user: {retrieved_user.chat_id}")
        finally:
            await db.dispose()
    if msg.from_user is None:
        return
    m = [
        f'Hello, <a href="tg://user?id={msg.from_user.id}">{html.quote(msg.from_user.full_name)}</a>\n'
        f'Firstname: {retrieved_user.first_name}\n'
        f'Language: {retrieved_user.language}\n'
        f'chat_id: {retrieved_user.chat_id}',
    ]
    await msg.answer("\n".join(m))


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))

    user_router.message.register(start, CommandStart())
    user_router.message.register(
        start,
        TextFilter(['salom', 'nima']),
        # noqa: RUF001
    )

    return user_router

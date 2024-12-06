from aiogram import html, types
from aiogram import Router
from aiogram.filters import CommandStart
from core import ChatTypeFilter, TextFilter


async def start(msg: types.Message) -> None:
    if msg.from_user is None:
        return
    m = [
        f'Hello, <a href="tg://user?id={msg.from_user.id}">{html.quote(msg.from_user.full_name)}</a>',
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

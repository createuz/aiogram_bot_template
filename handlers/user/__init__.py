from aiogram import Router
from aiogram.filters import CommandStart

from core import ChatTypeFilter, TextFilter
from . import start


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))

    user_router.message.register(start.start, CommandStart())
    user_router.message.register(
        start.start,
        TextFilter(['salom', 'nima']),
        # noqa: RUF001
    )

    return user_router

import os
import typing

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: str | typing.Sequence[str]) -> None:
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        return message.chat.type in self.chat_type


class TextFilter(BaseFilter):
    def __init__(self, text: str | list[str]) -> None:
        if isinstance(text, str):
            self.text = [text]
        else:
            self.text = text

    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        if isinstance(obj, Message):
            txt = obj.text or obj.caption
            return any(i == txt for i in self.text)
        if isinstance(obj, CallbackQuery):
            return obj.data in self.text
        return False


class IsAdmin(BaseFilter):
    def __init__(self) -> None:
        admins: list[str] = os.getenv("ADMINS", "").split(",")
        self.admin_ids = [int(admin.strip()) for admin in admins if admin.strip().isdigit()]

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids

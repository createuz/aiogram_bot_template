import os
from typing import List, Optional, Tuple

import aiofiles
import aiohttp
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType

from data import bot, conf, logger, IsAdmin
from data.states import BackupStates
from db import User

router = Router()


async def download_file(file_id: str, save_path: str) -> None:
    try:
        file = await bot.get_file(file_id)
        url = f"https://api.telegram.org/file/bot{conf.bot_token.token}/{file.file_path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                async with aiofiles.open(save_path, "wb") as saved_file:
                    await saved_file.write(await response.read())
    except Exception as e:
        logger.exception(f"Faylni yuklashda xatolik: {e}")
        raise


async def parse_chat_ids(file_path: str) -> List[int]:
    async with aiofiles.open(file_path, mode="r") as file:
        content = await file.read()
    return [int(line.strip()) for line in content.splitlines() if line.strip().isdigit()]


async def process_chat_id(chat_id: int) -> Tuple[bool, Optional[str]]:
    try:
        chat_id = int(chat_id)
        success = None
        user = await bot.get_chat(chat_id=chat_id)
        if user:
            success = await User.create_user(
                chat_id=chat_id,
                username=user.username,
                first_name=user.first_name,
                language='Russian',
                added_by='true'
            )
        return success
    except TelegramBadRequest as e:
        return None


async def process_chat_ids(chat_ids: List[int]) -> Tuple[List[int], List[Tuple[int]]]:
    success_chats = []
    failed_chats = []
    for chat_id in chat_ids:
        success = await process_chat_id(chat_id)
        if success:
            success_chats.append(chat_id)
        else:
            failed_chats.append(chat_id)
    return success_chats, failed_chats


@router.message(Command("backup"), IsAdmin(), StateFilter('*'))
async def request_txt_file(message: Message, state: FSMContext):
    await message.answer("<b>📄 TXT faylni yuboring.</b>")
    await state.set_state(BackupStates.waiting_for_txt_file)


@router.message(F.content_type == ContentType.DOCUMENT, BackupStates.waiting_for_txt_file)
async def handle_txt_file(message: Message, state: FSMContext):
    doc = message.document
    # save_path = f"/var/www/bot/data/{doc.file_id}.txt"
    save_path = f"C:/Users/creat/Desktop/TelegramBot/AiogramTemplate/{doc.file_id}.txt"
    try:
        await download_file(file_id=doc.file_id, save_path=save_path)
        chat_ids = await parse_chat_ids(file_path=save_path)
        if not chat_ids:
            return await message.answer("Faylda chat IDlar topilmadi.")
        success_chats, failed_chats = await process_chat_ids(chat_ids)
        await message.answer(
            f"<b>✅ {len(success_chats)} ta chat muvaffaqiyatli qo‘shildi./n"
            f"🔴 {len(failed_chats)} ta chat qo‘shilmadi.</b>"
        )
    except Exception as e:
        logger.exception(f"Xatolik yuz berdi: {e}")
        await message.answer("Xatolik yuz berdi. Tafsilotlarni loglardan tekshiring.")
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)
    await state.clear()

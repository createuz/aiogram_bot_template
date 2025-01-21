import asyncio
import time
from typing import Optional, Union, List, Tuple

from aiogram.types import InputFile, InlineKeyboardMarkup

from data import bot, ADMIN
from db import User


async def send_message_all(
        chat_id: int,
        text: Optional[str] = None,
        photo: Optional[Union[InputFile, str]] = None,
        video: Optional[Union[InputFile, str]] = None,
        video_note: Optional[Union[InputFile, str]] = None,
        animation: Optional[Union[InputFile, str]] = None,
        caption: Optional[str] = None,
        keyboard: Optional[InlineKeyboardMarkup] = None,
) -> Optional[bool]:
    try:
        if text:
            await bot.send_message(
                chat_id=chat_id,
                text=f"<b>{text}</b>",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        if photo:
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
        if video:
            await bot.send_video(
                chat_id=chat_id,
                video=video,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
        if video_note:
            await bot.send_video_note(
                chat_id=chat_id,
                video_note=video_note,
                reply_markup=keyboard
            )
        if animation:
            await bot.send_animation(
                chat_id=chat_id,
                animation=animation,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
        return True
    except Exception:
        return None


async def send_message_users(
        user_ids: List[int],
        text: Optional[str] = None,
        photo: Optional[Union[InputFile, str]] = None,
        video: Optional[Union[InputFile, str]] = None,
        video_note: Optional[Union[InputFile, str]] = None,
        animation: Optional[Union[InputFile, str]] = None,
        caption: Optional[str] = None,
        keyboard: Optional[InlineKeyboardMarkup] = None,
) -> Optional[Tuple[int]]:
    try:
        active_users = 0
        inactive_users = 0
        for user_id in user_ids:
            if await send_message_all(
                    chat_id=user_id,
                    text=text,
                    photo=photo,
                    video=video,
                    video_note=video_note,
                    animation=animation,
                    caption=caption,
                    keyboard=keyboard
            ):
                active_users += 1
            else:
                inactive_users += 1
            await asyncio.sleep(0.04)
        return active_users, inactive_users
    except Exception:
        return None


async def send_message_admin(
        text: Optional[str] = None,
        photo: Optional[Union[InputFile, str]] = None,
        video: Optional[Union[InputFile, str]] = None,
        video_note: Optional[Union[InputFile, str]] = None,
        animation: Optional[Union[InputFile, str]] = None,
        caption: Optional[str] = None,
        keyboard: Optional[InlineKeyboardMarkup] = None,
):
    try:
        if text:
            await bot.send_message(
                chat_id=ADMIN,
                text=f"<b>{text}</b>",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        if photo:
            await bot.send_photo(
                chat_id=ADMIN,
                photo=photo,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
        if video:
            await bot.send_video(
                chat_id=ADMIN,
                video=video,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
        if video_note:
            await bot.send_video_note(
                chat_id=ADMIN,
                video_note=video_note,
                reply_markup=keyboard
            )
        if animation:
            await bot.send_animation(
                chat_id=ADMIN,
                animation=animation,
                caption=f"<b>{caption}</b>",
                reply_markup=keyboard
            )
        return True
    except Exception:
        return None


async def admin_send_message_all(
        text: Optional[str] = None,
        photo: Optional[Union[InputFile, str]] = None,
        video: Optional[Union[InputFile, str]] = None,
        video_note: Optional[Union[InputFile, str]] = None,
        animation: Optional[Union[InputFile, str]] = None,
        caption: Optional[str] = None,
        keyboard: Optional[InlineKeyboardMarkup] = None,
):
    try:
        admin_lang = await User.get_language(chat_id=int(ADMIN))
        start_time = time.time()
        total_users = await User.get_all_users(admin_lang=admin_lang)
        active_users, inactive_users = await send_message_users(
            user_ids=total_users,
            text=text,
            photo=photo,
            video=video,
            video_note=video_note,
            animation=animation,
            caption=caption,
            keyboard=keyboard
        )
        end_time = time.time()
        msg = f'''┏━━━━━━━━━━━━━━━━━━━━━━━━
┃  📊  Sent message Statistic
┣━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 🔹 All users:  {len(total_users)}
┃
┃ 🔹 Active users:  {active_users}
┃
┃ 🔹 Inactive users:  {inactive_users}
┃ 
┃ 🔹 Success rate:  {active_users / len(total_users) * 100:.2f}%
┃
┃ 🔹 Start time:  {time.strftime("%H:%M:%S", time.gmtime(start_time))}
┃ 
┃ 🔹 End time:  {time.strftime("%H:%M:%S", time.gmtime(end_time))}
┃ 
┃ 🔹 Total time:  {time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))}
┃
┗━━━━━━━━━━━━━━━━━━━━━━━━'''
        await bot.send_message(chat_id=ADMIN, text=f"<b>{msg}</b>")
    except Exception as e:
        await bot.send_message(chat_id=ADMIN, text=f"Xatolik yuz berdi: {str(e)}")

from urllib.parse import quote

from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from data import bot, logger
from db import User, Statistic
from .langs import langs_text

statistic_router = Router()


async def generate_share_link(uid: str, language: str) -> str:
    text = langs_text.get(language, {}).get('share_text', '')
    encoded_text = quote(text)
    return f"https://t.me/share/url?url={encoded_text}%0A%0A%F0%9F%91%89%20t.me/anonchrobot?start={uid}"


def create_stat_markup(language: str, share_url: str) -> InlineKeyboardMarkup:
    """Statistika uchun tugmalarni yaratish."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="\ud83d\udd04 Update", callback_data="update_mystat"),
                InlineKeyboardButton(text=langs_text[language]['share'], url=share_url),
            ],
            [
                InlineKeyboardButton(text="\ud83d\udd3b", callback_data="cancel")
            ]
        ]
    )


async def generate_stat_message(chat_id: int) -> tuple[str, InlineKeyboardMarkup]:
    """Statistika xabarini yaratish va tegishli markupni qaytarish."""
    uid = await User.get_uid(chat_id=chat_id)
    language = await User.get_language(chat_id=chat_id)
    data = await Statistic.get_statistics(chat_id=chat_id)
    stat_msg = langs_text[language]['stat'].format(
        messages=data['messages'],
        daily_messages=data['daily_messages'],
        friends=data['friends'],
        clicks=data['clicks'],
        popularity=data['popularity'],
        uid=uid
    )
    share_url = await generate_share_link(uid=uid, language=language)
    share_link = create_stat_markup(language, share_url)
    return stat_msg, share_link


@statistic_router.message(Command("mystat"), StateFilter('*'))
async def stat_handler(message: Message, state: FSMContext):
    """Foydalanuvchi statistikasi."""
    await message.delete()
    await state.clear()
    try:
        stat_msg, share_link = await generate_stat_message(chat_id=message.chat.id)
        await bot.send_message(
            chat_id=message.chat.id,
            text=stat_msg,
            reply_markup=share_link,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.exception("Statistikani olishda xatolik yuz berdi: %s", e)





@statistic_router.callback_query(F.data == "update_mystat", StateFilter('*'))
async def update_stat_handler(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        stat_msg, share_link = await generate_stat_message(chat_id=call.message.chat.id)
        if call.message.text != stat_msg or call.message.reply_markup != share_link:
            update_stat = langs_text[await User.get_language(call.message.chat.id)]['update_stat']
            await bot.answer_callback_query(callback_query_id=call.id, text=update_stat)
            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=stat_msg,
                reply_markup=share_link,
                disable_web_page_preview=True
            )
        else:
            await bot.answer_callback_query(callback_query_id=call.id, text="Already up to date!")
    except Exception as e:
        logger.exception("Statistikani yangilashda xatolik yuz berdi: %s", e)

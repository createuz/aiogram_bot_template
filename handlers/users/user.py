from urllib.parse import quote

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from data import LanguageSelection, bot, AnonMessage, LanguageChange, logger, is_valid_url
from db import User, Statistic, db
from .buttons import get_language_keyboard, get_cancel_keyboard
from .langs import choose_button, langs_text, languages, language_changed

user_router = Router()


async def generate_share_link(uid: str, language: str) -> str:
    text = langs_text.get(language, {}).get('share_text', '')
    encoded_text = quote(text)
    return f"https://t.me/share/url?url={encoded_text}%0A%0A%F0%9F%91%89%20t.me/anonchrobot?start={uid}"


async def send_language_selection(chat_id: int, state: FSMContext, identifier=None):
    await bot.send_message(chat_id, choose_button, reply_markup=get_language_keyboard())
    await state.update_data(
        added_by=identifier if identifier else 'true',
        uid=identifier if identifier else None
    )
    await state.set_state(LanguageSelection.select_language)


async def send_start_message(chat_id: int, user_uid: str, language: str, message_id: int = None):
    text = langs_text[language]['start'].format(uid=user_uid)
    share_url = await generate_share_link(user_uid, language)
    share_link = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔻", callback_data="cancel"),
            InlineKeyboardButton(text=langs_text.get(language, {}).get('share', ''), url=share_url)
        ],
    ])
    if message_id:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=share_link,
            disable_web_page_preview=True
        )
    else:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=share_link, disable_web_page_preview=True)


@user_router.message(CommandStart(), F.chat.type == ChatType.PRIVATE, StateFilter('*'))
async def start_handler(message: Message, state: FSMContext):
    await message.delete()
    chat_id = message.chat.id
    parts = message.text.split()
    identifier = parts[1] if len(parts) > 1 else None
    await state.clear()

    try:
        language = await User.get_language(chat_id)
        if not language:
            print('ketti')
            return await send_language_selection(chat_id, state, identifier)
        if identifier:
            if not await User.check_uid(identifier):
                user_uid = await User.get_uid(chat_id)
                return await send_start_message(chat_id, user_uid, language)
            await bot.send_message(
                chat_id=chat_id,
                text=langs_text[language]['anon_message'],
                reply_markup=get_cancel_keyboard(language),
                disable_web_page_preview=True
            )
            user_id = await User.get_chat_id(identifier)
            await Statistic.update_statistics(chat_id=user_id, clicks=True)
            if user_id != chat_id:
                await Statistic.add_friends(user_id, chat_id)

            await state.update_data(uid=identifier, language=language)
            await state.set_state(AnonMessage.waiting_anon_msg)
        else:
            user_uid = await User.get_uid(chat_id)
            await send_start_message(chat_id, user_uid, language)

    except Exception as e:
        logger.exception("Error in start_handler: %s", e)


@user_router.callback_query(F.data.in_(languages.keys()), LanguageSelection.select_language)
async def create_user_handler(call: CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    language = languages[call.data]
    print(f'tanlandi:  {language}')

    try:
        data = await state.get_data()
        is_premium: bool = True if call.message.from_user.is_premium else False
        async with db.get_session() as session:
            new_user = await User.create_user(
                session=session,
                chat_id=chat_id,
                username=call.message.chat.username,
                first_name=call.message.chat.first_name,
                is_premium=is_premium,
                language=language,
                added_by=data.get('added_by')
            )
            print(new_user)
            await session.refresh(new_user)
            await User.create_statistics(new_user, session)
        await bot.answer_callback_query(call.id, f"✅ {language_changed[call.data]}")
        if uid := data.get('uid'):
            if not await User.check_uid(uid):
                user_uid = await User.get_uid(chat_id)
                return await send_start_message(chat_id, user_uid, language, call.message.message_id)
            await bot.send_message(
                chat_id=chat_id,
                text=langs_text[language]['anon_message'],
                reply_markup=get_cancel_keyboard(language),
                disable_web_page_preview=True
            )
            user_id = await User.get_chat_id(uid)
            await Statistic.update_statistics(chat_id=user_id, clicks=True)
            if user_id != chat_id:
                await Statistic.add_friends(user_id, chat_id)
            await state.update_data(uid=uid, language=language)
            await state.set_state(AnonMessage.waiting_anon_msg)
        else:
            user_uid = await User.get_uid(chat_id)
            await send_start_message(chat_id, user_uid, language, call.message.message_id)
    except Exception as e:
        logger.exception("Error in create_user_handler: %s", e)


@user_router.message(Command("lang"), F.chat.type == ChatType.PRIVATE)
async def change_language_handler(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    try:
        await bot.send_message(chat_id=message.chat.id, text=choose_button, reply_markup=get_language_keyboard())
        await state.set_state(LanguageChange.select_language)
    except Exception as e:
        logger.exception("Error in change_language_handler: %s", e)
        await bot.send_message(chat_id=message.chat.id, text="Please use the /start command to select a language.")


@user_router.callback_query(F.data.in_(languages.keys()), LanguageChange.select_language)
async def process_change_language(call: CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    try:
        language = languages[call.data]
        await User.update_language(chat_id, language)
        uid = await User.get_uid(chat_id)
        await state.clear()
        await bot.answer_callback_query(call.id, f"✅ {language_changed[call.data]}")
        await send_start_message(chat_id, uid, language, call.message.message_id)
    except Exception as e:
        logger.exception("Error in process_change_language: %s", e)


@user_router.message(Command("help"), StateFilter('*'))
async def handler_in_specific_state(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()


@user_router.message(F.text.startswith("/url"), F.chat.type == ChatType.PRIVATE, StateFilter('*'))
async def handle_url_command(message: Message, state: FSMContext):
    await message.delete()
    try:
        language = await User.get_language(message.chat.id)
        parts = message.text.split(maxsplit=1)
        if len(parts) == 1:
            uid = await User.get_uid(message.chat.id)
            await bot.send_message(
                chat_id=message.chat.id,
                text=langs_text[language]['change_url'].format(link=uid),
                disable_web_page_preview=True
            )
        else:
            new_url = parts[1].strip()
            if not is_valid_url(new_url):
                await bot.send_message(chat_id=message.chat.id, text=langs_text[language]['invalid_url'])
            else:
                await User.update_uid(message.chat.id, new_url)
                await bot.send_message(
                    chat_id=message.chat.id,
                    text=langs_text[language]['changed_url'].format(link=new_url)
                )
        await state.clear()
    except Exception as e:
        logger.exception("Error in handle_url_command: %s", e)

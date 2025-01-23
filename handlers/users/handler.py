from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from data import bot, AnonMessage, MEDIA_TYPES
from data import logger
from db import User
from .buttons import sent_success, get_cancel_keyboard
from .langs import langs_text

anon_msg_router = Router()


async def send_anon_message(chat_id: int, content_type: str, message: Message, reply_to_message_id: int = None):
    """Anonim xabar yuborish uchun optimallashtirilgan funksiya."""
    try:
        language = await User.get_language(chat_id)
        caption = langs_text[language]['new_anon1'].format(
            message.caption or langs_text[language]['new_anon2']
        )
        file_id = None
        if content_type == 'text':
            return await bot.send_message(
                chat_id=chat_id,
                text=langs_text[language]['new_anon1'].format(message.text),
                disable_web_page_preview=True,
                reply_to_message_id=reply_to_message_id,
            )
        elif content_type == 'photo':
            file_id = message.photo[-1].file_id  # Oxirgi rasmni olish
        elif hasattr(message, content_type):
            file_id = getattr(message, content_type).file_id
        if file_id:
            send_function = getattr(bot, f"send_{content_type}")
            return await send_function(
                chat_id=chat_id,
                caption=caption,
                reply_to_message_id=reply_to_message_id,
                **{content_type: file_id},
            )
    except Exception as e:
        logger.exception("Anonim xabarni yuborishda xatolik yuz berdi: %s", e)
        return None


@anon_msg_router.message(F.text | F.content_type.in_(MEDIA_TYPES.keys()), AnonMessage.waiting_anon_msg)
async def handler_media(message: Message, state: FSMContext):
    """Anonim xabarni qabul qilish va yuborish."""
    user1_chat_id = message.chat.id
    try:
        data = await state.get_data()
        uid = data['uid']
        language = data['language']
        user2_chat_id = await User.get_chat_id(uid=uid)
        media_type = MEDIA_TYPES.get(message.content_type)
        sent_message = await send_anon_message(chat_id=user2_chat_id, content_type=media_type, message=message)
        if sent_message:
            text, kb_btn = await sent_success(language=language, uid=uid)
            await bot.send_message(chat_id=user1_chat_id, text=f"<b>{text}</b>", reply_markup=kb_btn)
            await state.update_data({str(sent_message.message_id): (user1_chat_id, message.message_id)})
    except Exception as e:
        logger.exception("Media xabarni qayta ishlashda xatolik yuz berdi: %s", e)
        await state.clear()


@anon_msg_router.message(F.reply_to_message & F.content_type.in_(MEDIA_TYPES.keys()))
async def reply_message_handler(message: Message, state: FSMContext):
    """Javob sifatida yuborilgan xabarni qayta ishlash."""
    user2_chat_id = message.chat.id
    try:
        data = await state.get_data()
        original_message_id = message.reply_to_message.message_id
        if str(original_message_id) in data:
            user1_chat_id, user1_message_id = data[str(original_message_id)]
            media_type = MEDIA_TYPES.get(message.content_type)
            language = await User.get_language(message.chat.id)
            uid = await User.get_uid(chat_id=user1_chat_id)
            sent_message = await send_anon_message(
                chat_id=user1_chat_id,
                content_type=media_type,
                message=message,
                reply_to_message_id=user1_message_id,
            )
            if sent_message:
                text, kb_btn = await sent_success(language=language, uid=uid)
                await bot.send_message(chat_id=user2_chat_id, text=f"<b>{text}</b>", reply_markup=kb_btn)
    except Exception as e:
        logger.exception("Javob xabarini qayta ishlashda xatolik yuz berdi: %s", e)
        await state.clear()


@anon_msg_router.callback_query(F.data.startswith('send_more_'), StateFilter('*'))
async def send_more_query_handler(call: CallbackQuery, state: FSMContext):
    """Yana xabar yuborish uchun so'rovni ishlash."""
    try:
        await call.message.delete()
        uid = call.data.split('send_more_')[1]
        language = await User.get_language(call.message.chat.id)
        await bot.answer_callback_query(call.id)
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=langs_text[language]['anon_message'],
            reply_markup=get_cancel_keyboard(language),
            disable_web_page_preview=True,
        )
        await state.update_data(uid=uid, language=language)
        await state.set_state(AnonMessage.waiting_anon_msg)
    except Exception as e:
        logger.exception("Send more callbackni qayta ishlashda xatolik yuz berdi: %s", e)

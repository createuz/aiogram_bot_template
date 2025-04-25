from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from data import bot, AnonMessage, MEDIA_TYPES
from data import logger
from db import User, Statistic
from .buttons import sent_success, get_cancel_keyboard
from .langs import langs_text

anon_msg_router = Router()


async def send_anon_message(chat_id: int, content_type: str, message: Message, reply_to_message_id: int = None):
    """Xabar yuborish va statistika yangilash."""
    try:
        language = await User.get_language(chat_id)
        caption = (langs_text.get(language).get('new_anon1').format(message.caption)
                   if message.caption else langs_text.get(language).get('new_anon2'))
        sent_message = None

        if content_type == 'text':
            sent_message = await bot.send_message(
                chat_id=chat_id,
                text=langs_text.get(language).get('new_anon1').format(message.text),
                disable_web_page_preview=True,
                reply_to_message_id=reply_to_message_id
            )
        elif content_type == 'photo':
            sent_message = await bot.send_photo(
                chat_id=chat_id,
                photo=message.photo[-1].file_id,
                caption=caption,
                reply_to_message_id=reply_to_message_id
            )
        elif content_type == 'video':
            sent_message = await bot.send_video(
                chat_id=chat_id,
                video=message.video.file_id,
                caption=caption,
                reply_to_message_id=reply_to_message_id
            )
        elif content_type == 'audio':
            sent_message = await bot.send_audio(
                chat_id=chat_id,
                audio=message.audio.file_id,
                caption=caption,
                reply_to_message_id=reply_to_message_id
            )
        elif content_type == 'voice':
            sent_message = await bot.send_voice(
                chat_id=chat_id,
                voice=message.voice.file_id,
                caption=caption,
                reply_to_message_id=reply_to_message_id
            )
        elif content_type == 'video_note':
            sent_message = await bot.send_video_note(
                chat_id=chat_id,
                video_note=message.video_note.file_id,
                reply_to_message_id=reply_to_message_id
            )
        elif content_type == 'animation':
            sent_message = await bot.send_animation(
                chat_id=chat_id,
                animation=message.animation.file_id,
                caption=caption,
                reply_to_message_id=reply_to_message_id
            )

        # Statistika yangilash
        await Statistic.update_statistics(chat_id=chat_id, messages=True)
        return sent_message

    except Exception as e:
        logger.exception("Error while sending anonymous message: %s", e)
        return None


@anon_msg_router.message(F.content_type.in_(list(MEDIA_TYPES.keys())), AnonMessage.waiting_anon_msg)
async def handler_media(message: Message, state: FSMContext):
    """Foydalanuvchi xabarini yuborish va davlatga ma'lumot saqlash."""
    try:
        data = await state.get_data()
        user1_chat_id = message.chat.id
        user2_chat_id = await User.get_chat_id(uid=data['uid'])
        media_type = MEDIA_TYPES.get(message.content_type)

        sent_message = await send_anon_message(
            chat_id=user2_chat_id,
            content_type=media_type,
            message=message
        )
        if sent_message:
            # So'nggi yuborilgan xabarni saqlash
            await state.update_data(
                last_sent={
                    "original_chat_id": user1_chat_id,
                    "original_message_id": message.message_id,
                    "reply_chat_id": user2_chat_id,
                    "reply_message_id": sent_message.message_id,
                }
            )
            text, kb_btn = await sent_success(language=data['language'], uid=data['uid'])
            await bot.send_message(chat_id=user1_chat_id, text=f"<b>{text}</b>", reply_markup=kb_btn)
    except Exception as e:
        logger.exception("Error in handler_media: %s", e)
        await state.clear()


@anon_msg_router.message(F.reply_to_message, F.content_type.in_(list(MEDIA_TYPES.keys())))
async def reply_message_handler(message: Message, state: FSMContext):
    """Xabarga javobni yuborish."""
    try:
        data = await state.get_data()
        last_sent = data.get("last_sent", {})
        if not last_sent:
            return
        user1_chat_id = last_sent.get("original_chat_id")
        user1_message_id = last_sent.get("original_message_id")
        user2_chat_id = message.chat.id
        media_type = MEDIA_TYPES.get(message.content_type)
        sent_message = await send_anon_message(
            chat_id=user1_chat_id,
            content_type=media_type,
            message=message,
            reply_to_message_id=user1_message_id
        )
        if sent_message:
            language = await User.get_language(user2_chat_id)
            uid = await User.get_uid(chat_id=user1_chat_id)
            text, kb_btn = await sent_success(language=language, uid=uid)
            await bot.send_message(chat_id=user2_chat_id, text=f"<b>{text}</b>", reply_markup=kb_btn)
    except Exception as e:
        logger.exception("Error in reply_message_handler: %s", e)


@anon_msg_router.callback_query(F.data.startswith('send_more_'))
async def send_more_query_handler(call: CallbackQuery, state: FSMContext):
    """Yana xabar yuborish holatini o'rnatish."""
    try:
        await call.message.delete()
        uid = call.data.split('send_more_')[1]
        language = await User.get_language(call.message.chat.id)

        await bot.answer_callback_query(call.id)
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=langs_text.get(language).get('anon_message'),
            reply_markup=get_cancel_keyboard(language),
            disable_web_page_preview=True
        )

        await state.update_data(uid=uid, language=language)
        await state.set_state(AnonMessage.waiting_anon_msg)

    except Exception as e:
        logger.exception("Error in send_more_query_handler: %s", e)

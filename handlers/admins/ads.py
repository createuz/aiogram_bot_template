import asyncio
import re

from aiogram import Bot, F, types, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from data import bot, IsAdmin, AdsStates

ads_router = Router()
from handlers.admins.kb import initial_options, create_keyboard, confirm_options, media_type_options

ADS_MEDIA_TYPES = {
    types.ContentType.PHOTO: "photo",
    types.ContentType.VIDEO: "video",
    types.ContentType.VIDEO_NOTE: "video_note",
    types.ContentType.ANIMATION: "animation",
    types.ContentType.TEXT: "text",
}


async def replace_text_to_links(text):
    def create_html_link(match):
        text_name, url = match.groups()
        return f'<a href="{url}">{text_name}</a>'

    pattern = r'\((.*?)\)\[(.*?)\]'
    return re.sub(pattern, create_html_link, text)


@ads_router.message(CommandStart(), IsAdmin(), StateFilter('*'))
async def start(message: Message):
    await message.answer("Welcome! Use /admins to create an ad.")


@ads_router.callback_query(F.data == "ads_menu", IsAdmin())
async def create_ad(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>Qaysi turdagi post yaratmoqchisiz?</b>",
        reply_markup=media_type_options()
    )
    await state.set_state(AdsStates.waiting_for_media_type)


MEDIA_PROMPT_MESSAGES = {
    "text": "<b>📄 Text postini tayyorlash uchun text'ni yuboring!</b>",
    "photo": "<b>📸 Photo postini tayyorlash uchun photo'ni yuboring!</b>",
    "video": "<b>🎥 Video postini tayyorlash uchun video'ni yuboring!</b>",
    "video_note": "<b>📱 Video Note postini tayyorlash uchun video note'ni yuboring!</b>",
    "animation": "<b>💫 Animation postini tayyorlash uchun animatsiya'ni yuboring!</b>",
}


@ads_router.callback_query(AdsStates.waiting_for_media_type)
async def choose_media_type(call: CallbackQuery, state: FSMContext):
    media_type = call.data
    if media_type == "cancel":
        await call.message.answer("⬅ Bekor qilindi. Bosh menyuga qayting.")
        await state.clear()
        return
    if media_type in MEDIA_PROMPT_MESSAGES:
        await state.update_data(media_type=media_type)
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=MEDIA_PROMPT_MESSAGES[media_type]
        )
        await state.set_state(AdsStates.waiting_for_media)
    else:
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="<b>Noto'g'ri tanlov. Iltimos, qaytadan urinib ko'ring!</b>"
        )
        await state.clear()


@ads_router.message(AdsStates.waiting_for_media, F.content_type.in_(ADS_MEDIA_TYPES.keys()))
async def handle_media(message: Message, state: FSMContext):
    content_type = message.content_type
    media_data = {"media": None, "media_type": ADS_MEDIA_TYPES[content_type]}
    if content_type == 'photo':
        media_data["media"] = message.photo[-1].file_id
    elif content_type == 'video':
        media_data["media"] = message.video.file_id
    elif content_type == 'video_note':
        media_data["media"] = message.video_note.file_id
    elif content_type == 'animation':
        media_data["media"] = message.animation.file_id
    elif content_type == 'text':
        media_data["caption"] = message.text
    await state.update_data(**media_data, buttons=[])
    if media_data["media_type"] != "text":
        await message.answer("Post uchun izoh (caption) yozing:")
        await state.set_state(AdsStates.waiting_for_caption)
    else:
        await ask_buttons(message, state)


@ads_router.message(AdsStates.waiting_for_caption, F.text)
async def handle_caption(message: Message, state: FSMContext):
    await state.update_data(caption=message.text)
    await ask_buttons(message, state)


async def ask_buttons(message: Message, state: FSMContext):
    await message.answer("<b>Post uchun tugmalar yaratishni hohlaysizmi?</b>", reply_markup=initial_options())
    await state.set_state(AdsStates.confirm_buttons)


@ads_router.callback_query(AdsStates.confirm_buttons)
async def handle_buttons(call: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.answer_callback_query(call.id)
    if call.data == "add_button":
        await call.message.answer("Tugma nomini kiriting:")
        await state.set_state(AdsStates.waiting_for_button_name)
    elif call.data == "send_message":
        await confirm_ad(call.message, state)
    else:
        await state.clear()
        await call.message.answer("Post yaratish bekor qilindi.")


@ads_router.message(AdsStates.waiting_for_button_name, F.text)
async def button_name(message: Message, state: FSMContext):
    await state.update_data(button_name=message.text)
    await message.answer("Tugma uchun URL kiriting:")
    await state.set_state(AdsStates.waiting_for_button_url)


@ads_router.message(AdsStates.waiting_for_button_url, F.text)
async def button_url(message: Message, state: FSMContext):
    data = await state.get_data()
    buttons = data.get("buttons", [])
    buttons.append({"text": data["button_name"], "url": message.text})
    await state.update_data(buttons=buttons)
    await message.answer("Tugma qo'shildi! Keyingi vazifa?", reply_markup=initial_options())
    await state.set_state(AdsStates.confirm_buttons)


async def confirm_ad(message: Message, state: FSMContext):
    data = await state.get_data()
    keyboard = create_keyboard(data["buttons"])
    if data["media_type"] == "photo":
        await message.answer_photo(
            photo=data["media"],
            caption=data["caption"],
            reply_markup=keyboard
        )
    elif data["media_type"] == "video":
        await message.answer_video(
            video=data["media"],
            caption=data["caption"],
            reply_markup=keyboard
        )
    elif data["media_type"] == "video_note":
        await message.answer_video_note(
            video_note=data["media"],
            reply_markup=keyboard
        )
    elif data["media_type"] == "animation":
        await message.answer_animation(
            animation=data["media"],
            caption=data["caption"],
            reply_markup=keyboard
        )
    elif data["media_type"] == "text":
        await message.answer(
            text=data["caption"],
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    await message.answer("Postni yuborishni tasdiqlaysizmi?", reply_markup=confirm_options())
    await state.set_state(AdsStates.confirm_send)


@ads_router.callback_query(AdsStates.confirm_send)
async def send_ad(call: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    if call.data == "confirm":
        data = await state.get_data()
        user_ids = [5383531061]
        tasks = []
        for user_id in user_ids:
            tasks.append(send_media(bot, user_id, data))
        await asyncio.gather(*tasks)
        await call.message.answer("✅ Post muvaffaqiyatli yuborildi!")
    else:
        await call.message.answer("🔻 Postni yuborish bekor qilindi.")
    await state.clear()


async def send_media(bot: Bot, user_id: int, data: dict):
    keyboard = create_keyboard(data["buttons"])
    if data["media_type"] == "photo":
        await bot.send_photo(
            chat_id=user_id,
            photo=data["media"],
            caption=data["caption"],
            reply_markup=keyboard
        )
    elif data["media_type"] == "video":
        await bot.send_video(
            chat_id=user_id,
            video=data["media"],
            caption=data["caption"],
            reply_markup=keyboard
        )
    elif data["media_type"] == "video_note":
        await bot.send_video_note(
            chat_id=user_id,
            video_note=data["media"],
            reply_markup=keyboard
        )
    elif data["media_type"] == "animation":
        await bot.send_animation(
            chat_id=user_id,
            animation=data["media"],
            caption=data["caption"],
            reply_markup=keyboard
        )
    elif data["media_type"] == "text":
        await bot.send_message(
            chat_id=user_id,
            text=data["caption"],
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

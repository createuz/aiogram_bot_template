import json
import os
from collections import Counter

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputFile
from sqlalchemy import select

from data import bot, logger, AddAdmin, IsAdmin
from db import Admin, User, db

panel_router = Router()

from .kb import admin_menu, update_user_stat, stat_menu, home_menu, statistic_lang


@panel_router.message(Command("admin"), IsAdmin(), StateFilter('*'))
async def show_admin_panel(message: Message):
    await message.delete()
    await bot.send_message(chat_id=message.chat.id, text="<b>⚙ Welcome to Admin Panel</b>", reply_markup=home_menu())


@panel_router.callback_query(F.data == "home_menu", IsAdmin())
async def return_to_menu(call: CallbackQuery):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>⚙ Welcome to Admin Panel</b>",
        reply_markup=home_menu()
    )


@panel_router.callback_query(F.data == "admin_menu", IsAdmin())
async def show_admin_menu(call: CallbackQuery):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>🅰 Admin Menu</b>",
        reply_markup=admin_menu()
    )


@panel_router.callback_query(F.data == "admins_data", IsAdmin())
async def admin_data_handler(call: CallbackQuery):
    try:
        data = await Admin.get_admins_data()
        if data:
            admin_data = "\n".join(
                f"┃ ID: <code>{user.chat_id}</code> ┃ <a href='tg://user?id={user.chat_id}'>{user.first_name}</a>"
                for user in data
            )
            data_msg = f"""
┏━━━━━━━━━━━━━━━━━━━━━
┃ 🅰 Admin Statistic
┣━━━━━━━━━━━━━━━━━━━━━
{admin_data}
┗━━━━━━━━━━━━━━━━━━━━━"""
            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"<b>{data_msg}</b>"
            )
        else:
            await bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="<b>🛑 Hozirda Admin ma'lumotlari mavjud emas.</b>")
    except Exception as e:
        logger.exception("Error: %s", e)


@panel_router.callback_query(F.data == "add_admin", IsAdmin())
async def add_admin_handler(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Yangi adminning chat ID sini kiriting:"
    )
    await state.set_state(AddAdmin.waiting_for_add_chat_id)


@panel_router.message(AddAdmin.waiting_for_add_chat_id)
async def save_new_admin(message: Message, state: FSMContext):
    try:
        chat_id, username, first_name = await User.get_user(message.text)
        await Admin.create_admin(chat_id=chat_id, username=username, first_name=first_name)
        await message.answer(f"<b>{first_name}</b> adminlar ro'yxatiga qo'shildi ✅", reply_markup=admin_menu())
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


@panel_router.callback_query(F.data == "del_admin", IsAdmin())
async def delete_admin_handler(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="O'chirmoqchi bo'lgan adminning Chat ID sini kiriting:"
    )
    await state.set_state(AddAdmin.waiting_for_del_chat_id)


@panel_router.message(AddAdmin.waiting_for_del_chat_id)
async def save_deleted_admin(message: Message, state: FSMContext):
    try:
        await Admin.delete_admin(message.text)
        await message.answer(f"Chat ID: <b>{message.text}</b> adminlar ro'yxatidan chiqarildi ✅",
                             reply_markup=admin_menu())
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


@panel_router.callback_query(F.data == "stat_menu", IsAdmin())
async def chose_statistics(call: CallbackQuery):
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>📊 Statistikani tanlang:</b>",
        reply_markup=stat_menu()
    )


async def user_statistics():
    try:
        async with db.get_session() as session:
            users = await session.execute(select(User.language))
            lang_count_user = Counter([language for language, in users])
            total_users = sum(lang_count_user.values())
            user_data = "\n".join(
                f"┃ {language_name}: {lang_count_user.get(language_code, 0)}"
                for language_code, language_name in statistic_lang.items()
            )
            today = await User.joined_last_24_hours()
            month = await User.joined_last_month()
            return f"""
┏━━━━━━━━━━━━━━━━━━━━━
┃ 📊 User Statistic
┣━━━━━━━━━━━━━━━━━━━━━
┃ ➕ Joined today: {today}
┃ ➕ Joined this month: {month}
┃ 👤 All users count: {total_users}
┣━━━━━━━━━━━━━━━━━━━━━
{user_data}
┗━━━━━━━━━━━━━━━━━━━━━"""
    except Exception as e:
        logger.exception("Error: %s", e)
        return None


@panel_router.callback_query(F.data == "user_stat", IsAdmin())
async def total_user_statistics(call: CallbackQuery):
    try:
        user_stat = await user_statistics()
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"<b>{user_stat}</b>",
            reply_markup=update_user_stat()
        )
    except Exception as e:
        logger.exception("Error: %s", e)


@panel_router.callback_query(F.data == "update_user_stat", IsAdmin())
async def total_user_statistics(call: CallbackQuery):
    try:
        user_stat = await user_statistics()
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"<b>{user_stat}</b>",
            reply_markup=update_user_stat()
        )
    except Exception as e:
        logger.exception("Error: %s", e)


@panel_router.callback_query(F.data == "chat_ids", IsAdmin())
async def chat_ids_handler(call: CallbackQuery):
    try:
        users = await User.get_all_users()
        file_path = 'users.json'
        with open(file_path, 'w') as users_file:
            json.dump(users, users_file, indent=3)
        user_msg = f"""<b>
📄 Users count: {len(users)}

🤖 Bot: @</b>"""
        await call.message.answer_document(InputFile(file_path), caption=user_msg)
        os.remove(file_path)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)


@panel_router.callback_query(F.data == "cancel")
async def cancel_admin_action(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        await call.answer("Bekor qilindi ✅")
        await state.clear()
    except Exception as e:
        logger.exception("Xatolik: %s", e)


@panel_router.message(Command('break'), IsAdmin(), StateFilter('*'))
async def stop_message_sending(message: Message, state: FSMContext):
    try:
        await message.answer("⚙ Xabar yuborish to‘xtatildi")
        await state.clear()
    except Exception as e:
        await state.clear()
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")

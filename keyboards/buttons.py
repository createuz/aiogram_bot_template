from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

language_keyboard = InlineKeyboardMarkup(row_width=3).add(
    InlineKeyboardButton(text="🇺🇿 UZ", callback_data="uz"),
    InlineKeyboardButton(text="🇷🇺 RU", callback_data="ru"),
    InlineKeyboardButton(text="🇺🇸 EN", callback_data="en")
)

cancel_sending_kb = {
    'Uzbek': InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🗑 Bekor qilish", callback_data="bekor_qilish")),
    'English': InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🗑 Cancel", callback_data="bekor_qilish")),
    'Russian': InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🗑 Отмена", callback_data="bekor_qilish"))
}


async def sent_success(language: str, uid: str):
    data = {
        'Uzbek': {
            'sent': "✓ Xabar yuborildi, javobni kuting!",
            'send_kb': InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text="🔂 Ko'proq yuboring", callback_data=f"send_more_{uid}"))
        },
        'English': {
            'sent': "✓ Message sent, waiting for a reply!",
            'send_kb': InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text="🔂 Send more", callback_data=f"send_more_{uid}"))
        },
        'Russian': {
            'sent': "✓ Сообщение отправлено, ожидайте ответ!",
            'send_kb': InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text="🔂 Отправить ещё", callback_data=f"send_more_{uid}"))
        }
    }
    return data.get(language).get('sent'), data.get(language).get('send_kb')

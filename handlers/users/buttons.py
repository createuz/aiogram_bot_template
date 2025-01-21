from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def get_language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 UZ", callback_data="uz"),
                InlineKeyboardButton(text="🇷🇺 RU", callback_data="ru"),
                InlineKeyboardButton(text="🇺🇸 EN", callback_data="en")
            ]
        ]
    )


def get_cancel_keyboard(language: str):
    buttons = {
        "Uzbek": "🗑 Bekor qilish",
        "English": "🗑 Cancel",
        "Russian": "🗑 Отмена",
    }
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=buttons[language], callback_data="cancel")]
        ]
    )


async def sent_success(language: str, uid: str):
    data = {
        "Uzbek": {
            "sent": "✓ Xabar yuborildi, javobni kuting!",
            "send_kb": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔂 Ko'proq yuboring", callback_data=f"send_more_{uid}")]
                ]
            )
        },
        "English": {
            "sent": "✓ Message sent, waiting for a reply!",
            "send_kb": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔂 Send more", callback_data=f"send_more_{uid}")]
                ]
            )
        },
        "Russian": {
            "sent": "✓ Сообщение отправлено, ожидайте ответ!",
            "send_kb": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔂 Отправить ещё", callback_data=f"send_more_{uid}")]
                ]
            )
        }
    }
    return data.get(language, data["English"])["sent"], data.get(language, data["English"])["send_kb"]

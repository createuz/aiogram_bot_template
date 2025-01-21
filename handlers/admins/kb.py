from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_keyboard(buttons):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button["text"], url=button["url"])] for button in buttons
    ])


def home_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💬 Ads ", callback_data="ads_menu"),
                InlineKeyboardButton(text="📊 Statistic", callback_data="stat_menu")
            ],
            [
                InlineKeyboardButton(text="🅰 Admins", callback_data="admin_menu"),
                InlineKeyboardButton(text="🔻 Cancel", callback_data="cancel")
            ]
        ]
    )


def admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📄 Admins Data", callback_data="admins_data"),
                InlineKeyboardButton(text="➕ Add Admin", callback_data="add_admin")
            ],
            [
                InlineKeyboardButton(text="🗑 Delete Admin", callback_data="del_admin"),
                InlineKeyboardButton(text="⬅ Back", callback_data="home_menu")
            ]
        ]
    )


def stat_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 User Statistic", callback_data="user_stat"),
                InlineKeyboardButton(text="📄 Chat Ids", callback_data="chat_ids")
            ],
            [
                InlineKeyboardButton(text="⬅ Back", callback_data="home_menu")
            ]
        ]
    )


def update_user_stat():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Update", callback_data="update_user_stat"),
                InlineKeyboardButton(text="⬅ Back", callback_data="stat_menu")
            ]
        ]
    )


def update_next_user_stat():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Update", callback_data="user_stat"),
                InlineKeyboardButton(text="⬅ Back", callback_data="stat_menu")
            ]
        ]
    )


def media_type_options():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Text", callback_data="text"),
            InlineKeyboardButton(text="📸 Photo", callback_data="photo"),
            InlineKeyboardButton(text="🎥 Video", callback_data="video")
        ],
        [
            InlineKeyboardButton(text="📱 Video Note", callback_data="video_note"),
            InlineKeyboardButton(text="💫 Animation", callback_data="animation")

        ],
        [
            InlineKeyboardButton(text="⬅ Back", callback_data="cancel")
        ]
    ])


def initial_options():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Add Button", callback_data="add_button"),
            InlineKeyboardButton(text="🚀 Send Message", callback_data="send_message"),
        ],
        [
            InlineKeyboardButton(text="🗑 Cancel", callback_data="cancel")
        ]
    ])


def confirm_options():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Confirm", callback_data="confirm"),
            InlineKeyboardButton(text="🗑 Cancel", callback_data="cancel"),
        ]
    ])

statistic_lang = {
    'Uzbek': "🇺🇿 Uzbek ",
    'English': "🇬🇧 English ",
    'Russian': "🇷🇺 Russian ",
}
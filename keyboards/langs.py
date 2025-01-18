choose_button = "<b>•  Tilni tanlang\n•  Выберите язык\n•  Select language</b>"
send_message_type = "<b>Siz yubormoqchi bo'lgan xabar turi shu ko'rinishda bo'ladi!\n\n✅ Tastiqlash   |   🗑 Bekor qilish</b>"
start_bot = """
                ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃      Starting bot polling...        ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

start_uz = "<b>💌 Hoziroq anonim xabarlarni olishni boshlang!</b>\n\n" \
           "<b>Sizning havolangiz:</b>\n👉 t.me/anonchrobot?start={uid}\n\n" \
           "Ushbu havolani <b>Telegram</b>, <b>Instagram</b>, <b>YouTube</b> va <b>TikTok</b> " \
           "profilingiz tavsifiga joylashtiring va anonim xabarlarni qabul qilishni boshlang! 🗨"

start_ru = "<b>💌 Начните получать анонимные сообщения прямо сейчас!</b>\n\n" \
           "<b>Ваша ссылка:</b>\n👉 t.me/anonchrobot?start={uid}\n\n" \
           "Разместите эту ссылку в описании своего профиля на <b>Telegram</b>, <b>Instagram</b>, <b>YouTube</b> и <b>TikTok</b> " \
           "и начните получать анонимные сообщения! 🗨"

start_en = "<b>💌 Start receiving anonymous messages right now!</b>\n\n" \
           "<b>Your link:</b>\n👉 t.me/anonchrobot?start={uid}\n\n" \
           "Place this link in the description of your <b>Telegram</b>, <b>Instagram</b>, <b>YouTube</b>, and <b>TikTok</b> profiles " \
           "and start receiving anonymous messages! 🗨"

change_uz = "<b>Sizning anonim xabarlarni qabul qilish uchun havolangiz quyidagicha ko'rinishda:\n👉 <code>t.me/anonchrobot?start={link}</code>\n\n" \
            "Siz ushbu havolani shaxsiy havolaga o'zgartirishingiz mumkin! " \
            "Buning uchun quyidagi buyruqdan foydalaning:\n👉 <code>/url Name</code>\n\n" \
            "Bu yerda « <code>Name</code> » o‘rniga ismingiz yoki kompaniyangiz nomini kiriting!\n\n" \
            "Sizning yangi havolangiz quyidagicha ko'rinishda bo'ladi:\n👉 <code>t.me/anonchrobot?start=Name</code>\n\n" \
            "❗Iltimos, diqqat qiling: agar havolani o'zgartirsangiz, eski havola endi faol bo'lmaydi!</b>"

change_ru = "<b>Ваша ссылка для приёма анонимных сообщений выглядит следующим образом:\n👉 <code>t.me/anonchrobot?start={link}</code>\n\n" \
            "Вы можете изменить эту ссылку на персональную! " \
            "Для этого воспользуйтесь следующей командой:\n👉 <code>/url Name</code>\n\n" \
            "Здесь вместо « <code>Name</code> » введите своё имя или название компании!\n\n" \
            "Ваша новая ссылка будет выглядеть так:\n👉 <code>anonchrobot?start=Name</code>\n\n" \
            "❗Пожалуйста, обратите внимание: если вы измените ссылку, старая ссылка больше не будет активна!</b>"

change_en = "<b>Your link for receiving anonymous messages looks like this:\n👉 <code>t.me/anonchrobot?start={link}</code>\n\n" \
            "You can change this link to a personal one! " \
            "To do this, use the following command:\n👉 <code>/url Name</code>\n\n" \
            "Here, replace « <code>Name</code> » with your name or company name!\n\n" \
            "Your new link will look like this:\n👉 <code>anonchrobot?start=Name</code>\n\n" \
            "❗Please note: if you change the link, the old link will no longer be active!</b>"

changed_url_uz = "<b>☑ Shaxsiy havolangiz muvofaqiyatli uzgartirildi!\n\n" \
                 "Sizning yangi havolangiz:\n" \
                 "👉 <code>t.me/anonchrobot?start={link}</code>\n\n" \
                 "🗨 Hoziroq anonim xabarlarni olishni boshlang!</b>"

changed_url_ru = "<b>☑ Ваша персональная ссылка успешно изменена!\n\n" \
                 "Ваша новая ссылка:\n" \
                 "👉 <code>t.me/anonchrobot?start={link}</code>\n\n" \
                 "🗨 Начните получать анонимные сообщения прямо сейчас!</b>"

changed_url_en = "<b>☑ Your personal link has been successfully changed!\n\n" \
                 "Your new link:\n" \
                 "👉 <code>t.me/anonchrobot?start={link}</code>\n\n" \
                 "🗨 Start receiving anonymous messages right now!</b>"

help_uz = "Botdan foydalanish ko'rsatmalari:\n\n" \
          "/start - Botni ishga tushirish uchun ushbu buyruqdan foydalaning.\n\n" \
          "/lang - Botning tilini o'zgartirish uchun ushbu buyruqdan foydalaning.\n\n" \
          "/url - Shaxsiy havolangizni o'zgartirish  uchun ushbu buyruqdan foydalaning.\n\n" \
          "/help - Botdan foydalanish ko'rsatmalari va buyruqlari haqida ma'lumot olish uchun ushbu buyruqdan foydalaning."

help_ru = "Инструкции по использованию бота:\n\n" \
          "/start - Используйте эту команду для запуска бота.\n\n" \
          "/lang - Используйте эту команду для изменения языка бота.\n\n" \
          "/url - Используйте эту команду для изменения вашей персональной ссылки.\n\n" \
          "/help - Используйте эту команду для получения информации о инструкциях и командах бота."

help_en = "Bot usage instructions:\n\n" \
          "/start - Use this command to start the bot.\n\n" \
          "/lang - Use this command to change the bot's language.\n\n" \
          "/url - Use this command to change your personal link.\n\n" \
          "/help - Use this command to get information about the bot's instructions and commands."

anon_uz = f"Bu yerda siz ushbu havolani joylashtirgan shaxsga anonim xabar yuborishingiz mumkin.\n\n" \
          f"Yubormoqchi bo'lgan barcha xabaringizni bu erga yozing va bir necha soniya ichida u sizning xabaringizni oladi, lekin kimdan ekanligini bilmaydi.\n\n" \
          f"Siz yuborishingiz mumkin:\n•  Matn\n•  Photo\n•  Video\n•  Audio\n•  Animatsiya\n•  Ovozli xabar\n•  Video xabar\n\n" \
          f"⚠️ Bu butunlay anonim!"

anon_ru = f"Здесь вы можете отправить анонимное сообщение этому человеку.\n\n" \
          f"Напишите все, что хотите отправить сюда, и в течение нескольких секунд он получит ваше сообщение, но не узнает, от кого оно.\n\n" \
          f"Вы можете отправить:\n•  Текст\n•  Фото\n•  Видео\n•  Аудио\n•  Анимацию\n•  Голосовое сообщение\n•  Видео сообщение\n\n" \
          f"⚠️ Это полностью анонимно!"

anon_en = f"Here you can send an anonymous message to this person.\n\n" \
          f"Write everything you want to send here, and within a few seconds, he will receive your message, but won't know who it's from.\n\n" \
          f"You can send:\n•  Text\n•  Photo\n•  Video\n•  Audio\n•  Animation\n•  Voice message\n•  Video message\n\n" \
          f"⚠️ This is completely anonymous!"

invalid_url_uz = "<b>❗Kiritilgan havola yaroqsiz.\n\n" \
                 "Yangi havola yaratish uchun:  </b>" \
                 "Faqat lotin harflari, raqamlar va pastki chiziqdan foydalanishingiz mumkin. " \
                 "Belgilar soni <b>6</b> dan <b>20</b> tagacha bo‘lishi kerak.\n\n" \
                 "<b>Masalan:</b>  <code>/url MrDurov</code>  yoki  <code>/url Anna_123</code>\n\n" \
                 "<b>Iltimos, havolani to'g'ri kiriting va qayta urinib ko'ring!</b>"

invalid_url_ru = "<b>❗Введенная ссылка недействительна.\n\n" \
                 "Для создания новой ссылки:  </b>" \
                 "Используйте только латинские буквы, цифры и символ подчеркивания. " \
                 "Количество символов должно быть от <b>6</b> до <b>20</b>.\n\n" \
                 "<b>Например:</b>  <code>/url MrDurov</code>  или  <code>/url Anna_123</code>\n\n" \
                 "<b>Пожалуйста, введите ссылку правильно и попробуйте снова!</b>"

invalid_url_en = "<b>❗The entered link is invalid.\n\n" \
                 "To create a new link:  </b>" \
                 "You can only use Latin letters, numbers, and underscores. " \
                 "The number of characters should be between <b>6</b> and <b>20</b>.\n\n" \
                 "<b>Example:</b>  <code>/url MrDurov</code>  or  <code>/url Anna_123</code>\n\n" \
                 "<b>Please enter the link correctly and try again!</b>"

stat_uz = """
<b>📌 Profil Statistikasi

<blockquote>┏━━━━━━━━━━━━━━━━━━━━━━━
┃ 💬  <i>Qabul qilingan xabarlar</i>
┃ 💬  <i>Umumiy:   {messages}</i>
┃ 💬  <i>Bugun:   {daily_messages}</i>
┣━━━━━━━━━━━━━━━━━━━━━━━
┃ 👥  <i>Umumiy do'stlar</i>
┃ 👥  <i>Do'stlar:   {friends}</i>
┣━━━━━━━━━━━━━━━━━━━━━━━
┃ 👀  <i>Havolani ko'rishlar soni</i>
┃ 👀  <i>Havola:   {clicks}</i>
┣━━━━━━━━━━━━━━━━━━━━━━━
┃ ⭐️  <i>Mashhurlik darajasi</i>
┃ ⭐️  <i>Mashhurlik:   {popularity}+</i>
┗━━━━━━━━━━━━━━━━━━━━━━━</blockquote>

⭐️ Mashhurlik darajasini oshirish uchun shaxsiy havolangizni Telegram, Instagram, YouTube va TikTok profilingiz tavsifiga joylashtiring.

👉 t.me/anonchrobot?start={uid}</b>"""

stat_ru = """
<b>📌 Статистика Профиля

<blockquote>┏━━━━━━━━━━━━━━━━━━━━━━━
┃ 💬  <i>Полученные сообщения</i>
┃ 💬  <i>За все время:   {messages}</i>
┃ 💬  <i>Сегодня:   {daily_messages}</i>
┣━━━━━━━━━━━━━━━━━━━━━━━
┃ 👥  <i>Всего друзей</i>
┃ 👥  <i>Друзей:   {friends}</i>
┣━━━━━━━━━━━━━━━━━━━━━━━
┃ 👀  <i>Клики по ссылке</i>
┃ 👀  <i>Кликов:   {clicks}</i>
┣━━━━━━━━━━━━━━━━━━━━━━━
┃ ⭐️  <i>Уровень популярности</i>
┃ ⭐️  <i>Популярность:   {popularity}+</i>
┗━━━━━━━━━━━━━━━━━━━━━━━</blockquote>

<i>⭐️ Чтобы повысить уровень популярности, разместите свою персональную ссылку в описании вашего профиля в Telegram, Instagram, YouTube и TikTok.</i>

<blockquote>👉 <code>t.me/anonchrobot?start={uid}</code></blockquote></b>"""

stat_en = """
<b>📌 Profile Statistics

<blockquote>┏━━━━━━━━━━━━━━━━━━━━━━━
┃ 💬  <i>Messages received</i>
┃ 💬  <i>All-time:   {messages}</i>
┃ 💬  <i>Today:   {daily_messages}</i>
┣━━━━━━━━━━━━━━━━━━━━━━━
┃ 👥  <i>Total friends</i>
┃ 👥  <i>Friends:   {friends}</i>
┣━━━━━━━━━━━━━━━━━━━━━━━
┃ 👀  <i>Link clicks</i>
┃ 👀  <i>Clicks:   {clicks}</i>
┣━━━━━━━━━━━━━━━━━━━━━━━
┃ ⭐️  <i>Popularity level</i>
┃ ⭐️  <i>Popularity:   {popularity}+</i>
┗━━━━━━━━━━━━━━━━━━━━━━━</blockquote>

<i>⭐️ To increase your popularity level, place your personal link in the description of your profile on Telegram, Instagram, YouTube, and TikTok.</i>

<blockquote>👉 <code>t.me/anonchrobot?start={uid}</code></blockquote></b>"""

languages = {
    "uz": "Uzbek",
    "en": "English",
    "ru": "Russian",
}

language_changed = {
    "uz": "🇺🇿 UZ",
    "ru": "🇷🇺 RU",
    "en": "🇺🇸 EN"
}

statistic_lang = {
    'Uzbek': "🇺🇿 Uzbek ",
    'English': "🇬🇧 English ",
    'Russian': "🇷🇺 Russian ",
}

langs_text = {
    'Uzbek': {
        'start': start_uz,
        'change_url': change_uz,
        'changed_url': changed_url_uz,
        'help': f'<b>{help_uz}</b>',
        'anon_message': f'<b>{anon_uz}</b>',
        'invalid_url': invalid_url_uz,
        'stat': stat_uz,
        'update_stat': 'Statistika yangilandi...',
        'send_more': "🔂 Ko'proq yuboring",
        'share': "🔀 Ulashish",
        'share_text': "Menga anonim xabar yuboring! 🗨",
        'new_anon1': "<b>🔔 Sizda yangi anonim xabar bor!\n\n{}\n\n↩️ Javob berish uchun suring.</b>",
        'new_anon2': "<b>🔔 Sizda yangi anonim xabar bor!\n\n↩️ Javob berish uchun suring.</b>"
    },
    'Russian': {
        'start': start_ru,
        'change_url': change_ru,
        'changed_url': changed_url_ru,
        'help': help_ru,
        'anon_message': f'<b>{anon_ru}</b>',
        'invalid_url': invalid_url_ru,
        'stat': stat_ru,
        'update_stat': 'Обновление статистики...',
        'send_more': "🔂 Отправить ещё",
        'share': "🔀 Поделиться",
        'share_text': "Отправьте мне анонимное сообщение! 🗨",
        'new_anon1': "<b>🔔 У тебя новое анонимное сообщение!\n\n{}\n\n↩️ Проведите пальцем, чтобы ответить.</b>",
        'new_anon2': "<b>🔔 У тебя новое анонимное сообщение!\n\n↩️ Проведите пальцем, чтобы ответить.</b>"
    },
    'English': {
        'start': start_en,
        'change_url': change_en,
        'changed_url': changed_url_en,
        'help': help_en,
        'anon_message': f'<b>{anon_en}</b>',
        'invalid_url': invalid_url_en,
        'stat': stat_en,
        'update_stat': 'Updating statistics...',
        'send_more': "🔂 Send more",
        'share': "🔀 Share",
        'share_text': "Send me an anonymous message! 🗨",
        'new_anon1': "<b>🔔 You have a new anonymous message!\n\n{}\n\n↩️ Swipe to reply.</b>",
        'new_anon2': "<b>🔔 You have a new anonymous message!\n\n↩️ Swipe to reply.</b>"
    }
}

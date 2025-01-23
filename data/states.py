from aiogram.fsm.state import State, StatesGroup


class AnonMessage(StatesGroup):
    waiting_anon_msg = State()
    waiting_reply = State()


class ChangeUrl(StatesGroup):
    waiting_url = State()


class LanguageSelection(StatesGroup):
    select_language = State()


class LanguageChange(StatesGroup):
    select_language = State()


class AddAdmin(StatesGroup):
    waiting_for_add_chat_id = State()
    waiting_for_del_chat_id = State()


class AdsStates(StatesGroup):
    waiting_for_media = State()
    waiting_for_caption = State()
    waiting_for_button_name = State()
    waiting_for_button_url = State()
    confirm_buttons = State()
    confirm_send = State()
    waiting_for_media_type = State()


class BackupStates(StatesGroup):
    waiting_for_txt_file = State()

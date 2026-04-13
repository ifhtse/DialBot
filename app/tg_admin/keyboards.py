from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Старт / Продолжить", callback_data="run")],
            [
                InlineKeyboardButton(text="⏸ Пауза", callback_data="pause"),
                InlineKeyboardButton(text="⛔ Стоп", callback_data="stop"),
            ],
            [
                InlineKeyboardButton(text="📋 Чаты", callback_data="menu_chats"),
                InlineKeyboardButton(text="📝 Сценарий", callback_data="menu_scenario")
            ],
            [
                InlineKeyboardButton(text="👤 Аккаунты", callback_data="menu_accounts"),
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")
            ],
            [
                InlineKeyboardButton(text="🔎 Скан чатов (Diff)", callback_data="scan_diff"),
                InlineKeyboardButton(text="🧨 Глубокая очистка", callback_data="deep_clear")
            ]
        ]
    )

def kb_back_to_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_main")]
        ]
    )
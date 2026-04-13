from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# === ГЛАВНОЕ МЕНЮ ===

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


# === НАСТРОЙКИ И АДМИНЫ ===

def kb_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Управление админами", callback_data="manage_admins")],
            [InlineKeyboardButton(text="⏱ Настройка задержек", callback_data="set_delays")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ]
    )

def kb_manage_admins() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить админа", callback_data="add_admin")],
            [InlineKeyboardButton(text="➖ Удалить админа", callback_data="del_admin")],
            [InlineKeyboardButton(text="📋 Список админов", callback_data="list_admins")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_settings")]
        ]
    )


# === АККАУНТЫ (СЕССИИ) ===

def kb_accounts_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить аккаунт", callback_data="add_account")],
            [InlineKeyboardButton(text="📋 Список аккаунтов", callback_data="list_accounts")],
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_main")]
        ]
    )

def kb_cancel_fsm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="menu_accounts")]
        ]
    )
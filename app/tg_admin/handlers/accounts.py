from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError

from app.core.config import config
from app.core.logger import logger
from app.database.repository import DBRepository
from app.tg_admin.keyboards import kb_accounts_main, kb_cancel_fsm
from app.tg_admin.states import AdminState
from app.services.client_pool import client_pool

router = Router(name="accounts_router")

pending_logins = {}

@router.callback_query(F.data == "menu_accounts")
async def cb_menu_accounts(call: CallbackQuery,state: FSMContext):
    await state.clear()
    await call.message.edit_text("👤 Управление аккаунтами (юзерботами):", reply_markup=kb_accounts_main())
    await call.answer()

@router.callback_query(F.data == "add_accounts")
async def cb_add_accounts(call: CallbackQuery,state: FSMContext):
    await state.set_state(AdminState.ACCOUNT_PHONE)
    await call.message.edit_text(
        "📱 Введи номер телефона для нового аккаунта.\n"
        "Формат: +79991234567\n\n"
        "*(Имя сессии сгенерируется автоматически)*",
        reply_markup=kb_cancel_fsm(),
        parse_mode="Markdown"
    )
    await call.answer()

@router.message(AdminState.ACCOUNT_PHONE)
async def process_account_phone(msg: Message, state: FSMContext):
    phone = msg.text.strip()
    if not phone.startswith("+"):
        await msg.answer("Номер должен начинаться с '+'. Попробуй еще раз: ", reply_markup=kb_cancel_fsm())
        return


    session_name = f"acc_{phone.replace('+', '').replace(' ','')}"
    session_path = client_pool.get_session_path(session_name)

    client = TelegramClient(session_path, config.api_id, config.api_hash)
    await client.connect()

    try:
        sent = await client.send_code_request(phone)

        pending_logins[msg.from_user.id] = {
            "client": client,
            "phone": phone,
            "phone_code_hash": sent.phone_code_hash,
            "session_name": session_name,
        }

        await state.set_state(AdminState.ACCOUNT_CODE)
        await msg.answer("✅ Код отправлен в Telegram!\n\n"
            "✉️ Введи полученный код (только цифры):",
            reply_markup=kb_cancel_fsm()
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке кода на {phone}: {e}")
        await msg.answer(f"❌ Ошибка отправки кода: {e}", reply_markup=kb_accounts_main())
        await state.clear()

@router.message(AdminState.ACCOUNT_CODE)
async def process_account_code(msg: Message, state: FSMContext):
    code = msg.text.strip().replace(" ", "")
    user_data = pending_logins.get(msg.from_user.id)

    if not user_data:
        await msg.answer("❌ Ошибка: сессия логина потеряна. Начните заново.", reply_markup=kb_accounts_main())
        await state.clear()
        return

    client: TelegramClient = user_data["client"]

    try:
        await client.sign_in(
            phone=user_data["phone"],
            code=code,
            phone_code_hash=user_data["phone_code_hash"]
        )

        await finalize_login(msg, state, user_data)

    except SessionPasswordNeededError:
        await state.set_state(AdminState.ACCOUNT_PASSWORD)
        await msg.answer("🔐 У аккаунта включен пароль (2FA). Введи пароль:", reply_markup=kb_cancel_fsm())
    except (PhoneCodeInvalidError, PhoneCodeExpiredError) as e:
        await msg.answer(f"❌ Неверный или истекший код. Попробуй заново.", reply_markup=kb_accounts_main())
        await state.clear()
        pending_logins.pop(msg.from_user.id, None)


@router.message(AdminState.ACCOUNT_PASSWORD)
async def process_account_password(msg: Message, state: FSMContext):
    password = msg.text.strip()
    user_data = pending_logins.get(msg.from_user.id)

    if not user_data:
        await state.clear()
        return

    client: TelegramClient = user_data["client"]

    try:
        await client.sign_in(password=password)
        await finalize_login(msg, state, user_data)
        # В целях безопасности удаляем сообщение с паролем из чата (если боту даны права)
        try:
            await msg.delete()
        except Exception:
            pass
    except Exception as e:
        await msg.answer(f"❌ Неверный пароль или ошибка: {e}", reply_markup=kb_accounts_main())
        await state.clear()
        pending_logins.pop(msg.from_user.id, None)


@router.callback_query(F.data == "list_accounts")
async def cb_list_accounts(call: CallbackQuery):
    accounts = await DBRepository.get_all_accounts()

    if not accounts:
        await call.message.edit_text(
            "📋 **Список аккаунтов пуст.**\nДобавьте первый аккаунт через меню.",
            reply_markup=kb_accounts_main()
        )
        await call.answer()
        return

    text = "📋 **Привязанные аккаунты:**\n\n"
    for acc in accounts:
        # Проверяем, запущен ли клиент в нашем пуле прямо сейчас
        is_running = "🟢 Запущен" if acc['session_name'] in client_pool.clients else "🔴 Отключен"
        text += f"👤 `{acc['phone']}`\n"
        text += f"└ Сессия: `{acc['session_name']}`\n"
        text += f"└ Статус в БД: {acc['status']} | В памяти: {is_running}\n\n"

    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb_accounts_main())
    await call.answer()


async def finalize_login(msg: Message, state: FSMContext, user_data: dict):
    """Вспомогательная функция для завершения авторизации."""
    client: TelegramClient = user_data["client"]
    session_name = user_data["session_name"]
    phone = user_data["phone"]

    me = await client.get_me()

    # 1. Записываем в БД
    await DBRepository.add_account(session_name, phone)

    # 2. Добавляем в ClientPool
    await client_pool.add_and_start_client(session_name, client)

    pending_logins.pop(msg.from_user.id, None)
    await state.clear()

    name = getattr(me, 'first_name', 'Юзербот')
    await msg.answer(
        f"✅ Успешно!\n\n"
        f"Аккаунт: {name} (`{phone}`)\n"
        f"Внутреннее имя сессии: `{session_name}`\n"
        f"Аккаунт добавлен в пул и готов к работе.",
        parse_mode="Markdown",
        reply_markup=kb_accounts_main()
    )
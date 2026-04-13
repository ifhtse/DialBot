from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.core.config import config
from app.database.repository import DBRepository
from app.tg_admin.keyboards import kb_settings, kb_manage_admins, kb_back_to_main
from app.tg_admin.states import AdminState

router = Router(name="settings_router")
#navigation
@router.callback_query(F.data == "menu_settings")
async def cb_menu_settings(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("⚙️ Настройки бота:", reply_markup=kb_settings())

@router.callback_query(F.data == "manage_admins")
async def cb_manage_admins(call: CallbackQuery):
    await call.message.edit_text("👥 Управление администраторами:", reply_markup=kb_manage_admins())


@router.callback_query(F.data == "list_admins")
async def cb_list_admins(call: CallbackQuery):
    admins = await DBRepository.get_all_admins()
    text = "📋 **Список администраторов:**\n\n"
    for adm in admins:
        role = "👑 Супер-админ" if adm == config.main_admin_id else "👤 Админ"
        text += f"• `{adm}` - {role}\n"

    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb_manage_admins())

#adm add-del
@router.callback_query(F.data == "add_admin")
async def cb_add_admin(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != config.main_admin_id:
        await call.answer("⛔ Только супер-админ может добавлять других админов!", show_alert=True)
        return

    await state.set_state(AdminState.ADD_ADMIN)
    await call.message.edit_text(
        "Отправь мне Telegram ID нового администратора (только цифры):",
        reply_markup=kb_manage_admins()
    )


@router.message(AdminState.ADD_ADMIN)
async def process_add_admin(msg: Message, state: FSMContext):
    try:
        new_admin_id = int(msg.text.strip())
        await DBRepository.add_admin(new_admin_id, added_by=msg.from_user.id)
        await msg.answer(f"✅ Пользователь `{new_admin_id}` назначен администратором.", parse_mode="Markdown",
                         reply_markup=kb_settings())
    except ValueError:
        await msg.answer("❌ Ошибка! Нужно отправить числовой ID.", reply_markup=kb_settings())
    finally:
        await state.clear()


@router.callback_query(F.data == "del_admin")
async def cb_del_admin(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != config.main_admin_id:
        await call.answer("⛔ Только супер-админ может удалять админов!", show_alert=True)
        return

    await state.set_state(AdminState.DEL_ADMIN)
    await call.message.edit_text(
        "Отправь мне Telegram ID администратора для удаления:",
        reply_markup=kb_manage_admins()
    )


@router.message(AdminState.DEL_ADMIN)
async def process_del_admin(msg: Message, state: FSMContext):
    try:
        del_admin_id = int(msg.text.strip())

        # Защита: нельзя удалить главного админа
        if del_admin_id == config.main_admin_id:
            await msg.answer("❌ Вы не можете удалить супер-администратора (самого себя)!", reply_markup=kb_settings())
            return

        success = await DBRepository.del_admin(del_admin_id)
        if success:
            await msg.answer(f"✅ Администратор `{del_admin_id}` успешно удален.", parse_mode="Markdown",
                             reply_markup=kb_settings())
        else:
            await msg.answer(f"⚠️ Пользователь `{del_admin_id}` не найден в списке администраторов.",
                             parse_mode="Markdown", reply_markup=kb_settings())

    except ValueError:
        await msg.answer("❌ Ошибка! Нужно отправить числовой ID.", reply_markup=kb_settings())
    finally:
        await state.clear()
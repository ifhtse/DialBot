from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.tg_admin.keyboards import kb_main

router = Router(name="base_router")

@router.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "👋 Добро пожаловать в панель управления юзерботами.\n\n"
        "Выберите нужное действие в меню ниже:",
        reply_markup=kb_main()
    )

@router.callback_query(F.data == "back_main")
async def cb_back_to_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "⚙️ Главное меню:",
        reply_markup=kb_main()
    )
    await call.answer()
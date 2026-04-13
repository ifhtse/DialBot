from aiogram import Router, F
from app.services.dialog_engine import dialog_engine
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

@router.callback_query(F.data == "run")
async def cb_run_engine(call: CallbackQuery):
    await call.answer()

    if dialog_engine.is_running:
        # Если уже запущен, но на паузе — снимаем с паузы
        if not dialog_engine.pause_event.is_set():
            dialog_engine.resume()
            await call.message.edit_text("▶️ Работа продолжена!", reply_markup=kb_main())
        else:
            await call.answer("Движок уже работает!", show_alert=True)
        return

    # Попытка старта
    success, msg_text = await dialog_engine.start()
    await call.message.edit_text(msg_text, reply_markup=kb_main())


@router.callback_query(F.data == "pause")
async def cb_pause_engine(call: CallbackQuery):
    await call.answer()
    if not dialog_engine.is_running:
        await call.answer("Движок не запущен!", show_alert=True)
        return

    dialog_engine.pause()
    await call.message.edit_text("⏸ Бот поставлен на паузу.", reply_markup=kb_main())


@router.callback_query(F.data == "stop")
async def cb_stop_engine(call: CallbackQuery):
    await call.answer()
    if not dialog_engine.is_running:
        await call.answer("Движок и так остановлен.", show_alert=True)
        return

    await dialog_engine.stop()
    await call.message.edit_text("⛔ Работа движка полностью остановлена.", reply_markup=kb_main())
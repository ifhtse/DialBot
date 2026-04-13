from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database.repository import DBRepository
from app.tg_admin.keyboards import kb_scenario_main
from app.tg_admin.states import AdminState
from app.core.logger import logger

router = Router(name="scenario_router")


@router.callback_query(F.data == "menu_scenario")
async def cb_menu_scenario(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    await call.message.edit_text("📝 Управление сценарием диалогов:", reply_markup=kb_scenario_main())


@router.callback_query(F.data == "add_scenario")
async def cb_add_scenario(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AdminState.ADD_SCENARIO)
    text = (
        "Отправь мне новый сценарий (старый будет удален).\n\n"
        "**Формат:**\n"
        "`номер_аккаунта - текст`\n\n"
        "**Пример:**\n"
        "`1 - Привет, как дела?`\n"
        "`2 - Привет! Всё отлично.`\n"
        "`1 - png Картинка тут` (если нужна отправка фото)"
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb_scenario_main())


@router.message(AdminState.ADD_SCENARIO)
async def process_add_scenario(msg: Message, state: FSMContext):
    await DBRepository.clear_scenario()

    lines = msg.text.splitlines()
    steps_added = 0

    for line in lines:
        line = line.strip()
        if not line or "-" not in line:
            continue

        try:
            # Парсим "1 - Текст"
            who, text_part = line.split("-", 1)
            who = who.strip()
            text_part = text_part.strip()

            sender_tag = f"account_{who}"

            # Проверяем, фото это или текст
            if text_part.lower().startswith("png"):
                caption = text_part[3:].strip()
                await DBRepository.add_scenario_step(sender_tag, "photo", caption, "photo.jpg")
            else:
                await DBRepository.add_scenario_step(sender_tag, "text", text_part)

            steps_added += 1
        except Exception as e:
            logger.error(f"Ошибка парсинга строки сценария: {line} | Ошибка: {e}")

    await msg.answer(f"✅ Сценарий успешно сохранен! Загружено шагов: {steps_added}", reply_markup=kb_scenario_main())
    await state.clear()


@router.callback_query(F.data == "show_scenario")
async def cb_show_scenario(call: CallbackQuery):
    await call.answer()
    scenario = await DBRepository.get_scenario()

    if not scenario:
        await call.message.edit_text("Сценарий пуст.", reply_markup=kb_scenario_main())
        return

    text = "🧾 **Текущий сценарий:**\n\n"
    for i, step in enumerate(scenario, start=1):
        if step['step_type'] == 'text':
            text += f"{i}. [{step['sender_tag']}] 📝 {step['content']}\n"
        else:
            text += f"{i}. [{step['sender_tag']}] 🖼 (Фото: {step['media_path']}) | {step['content']}\n"

    # Если текст слишком длинный, телеграм может ругнуться. Для надежности режем до 4000 символов
    if len(text) > 4000:
        text = text[:4000] + "\n... (обрезано)"

    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb_scenario_main())


@router.callback_query(F.data == "add_photo")
async def cb_add_photo(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AdminState.ADD_PHOTO)
    await call.message.edit_text(
        "🖼 Отправьте мне фотографию.\n"
        "Она будет сохранена как `photo.jpg` и использована во всех шагах сценария типа `png`.",
        parse_mode="Markdown",
        reply_markup=kb_scenario_main()
    )


@router.message(AdminState.ADD_PHOTO, F.photo)
async def process_add_photo(msg: Message, state: FSMContext):
    try:
        # Берем фото в лучшем качестве (последнее в списке)
        photo = msg.photo[-1]
        file_path = "photo.jpg"  # Пока хардкодим одно фото, как в старом коде, для простоты

        # Скачиваем файл с серверов Telegram
        await msg.bot.download(photo, destination=file_path)

        await msg.answer("✅ Фотография успешно загружена и готова к рассылке!", reply_markup=kb_scenario_main())
    except Exception as e:
        logger.error(f"Ошибка сохранения фото: {e}")
        await msg.answer(f"❌ Не удалось сохранить фото: {e}", reply_markup=kb_scenario_main())
    finally:
        await state.clear()
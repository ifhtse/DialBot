import asyncio
from app.core.logger import logger
from app.database.repository import DBRepository
from app.services.client_pool import client_pool


class DialogEngine:
    def __init__(self):
        self.is_running = False
        self.current_task: asyncio.Task | None = None

        # Эвенты для управления фоновой задачей
        self.stop_event = asyncio.Event()
        self.pause_event = asyncio.Event()
        self.pause_event.set()  # Изначально не на паузе (True = можно работать)

    async def start(self) -> tuple[bool, str]:
        """Запускает рассылку в фоне."""
        if self.is_running:
            return False, "Движок уже запущен."

        # Проверки перед стартом (Pre-flight checks)
        chats = await DBRepository.get_all_chats()
        scenario = await DBRepository.get_scenario()

        if not chats:
            return False, "❌ Список чатов пуст. Сначала добавьте чаты."
        if not scenario:
            return False, "❌ Сценарий пуст. Сначала загрузите сценарий."

        self.is_running = True
        self.stop_event.clear()
        self.pause_event.set()

        # Запускаем worker как независимую фоновую задачу
        self.current_task = asyncio.create_task(self._worker(chats, scenario))
        return True, "▶️ Рассылка успешно запущена!"

    async def stop(self):
        """Полная остановка процесса."""
        self.stop_event.set()
        self.pause_event.set()  # Снимаем с паузы, чтобы worker смог дойти до проверки stop_event
        self.is_running = False
        if self.current_task:
            self.current_task.cancel()

    def pause(self):
        """Ставит на паузу (worker заблокируется на await pause_event.wait())."""
        self.pause_event.clear()

    def resume(self):
        """Снимает с паузы."""
        self.pause_event.set()

    def get_status(self) -> str:
        """Возвращает текстовый статус для UI."""
        if not self.is_running:
            return "🛑 Остановлен"
        if not self.pause_event.is_set():
            return "⏸ На паузе"
        return "▶️ В работе"

    async def _worker(self, chats: list[int], scenario: list[dict]):
        """САМАЯ ГЛАВНАЯ ФУНКЦИЯ (пока скелет)"""
        logger.info(f"Worker стартовал. Чатов: {len(chats)}, Шагов: {len(scenario)}")

        try:
            for chat_id in chats:
                # Проверяем, не нажали ли Стоп
                if self.stop_event.is_set():
                    logger.info("Worker получил сигнал STOP.")
                    break

                # Ждем, если стоит Пауза (замораживает выполнение тут)
                await self.pause_event.wait()

                logger.info(f"Обработка чата: {chat_id}")

                # TODO: В Части 6.2 здесь будет логика прохода по шагам сценария,
                # получение клиентов из client_pool и отправка сообщений.

                # Пока имитируем бурную деятельность (2 секунды на чат)
                await asyncio.sleep(2)

        except asyncio.CancelledError:
            logger.info("Фоновая задача Worker была принудительно отменена.")
        except Exception as e:
            logger.error(f"Критическая ошибка в Worker: {e}", exc_info=True)
        finally:
            self.is_running = False
            logger.info("Worker завершил работу.")


# Глобальный инстанс движка
dialog_engine = DialogEngine()
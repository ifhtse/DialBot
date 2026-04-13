import os
from typing import Dict, Optional
from telethon import TelegramClient

# Если у тебя в config нет api_id/api_hash (хотя должны быть), мы их тут не дергаем.
# ClientPool работает только с уже готовыми объектами TelegramClient.
from app.core.logger import logger


class ClientPool:
    # ВАЖНО: ровно ДВА подчеркивания с каждой стороны!
    def __init__(self):
        # Словарь для хранения активных клиентов: {"session_name": TelegramClient}
        self.clients: Dict[str, TelegramClient] = {}

        # Убедимся, что папка для сессий существует
        self.sessions_dir = "sessions"
        os.makedirs(self.sessions_dir, exist_ok=True)

    def get_session_path(self, session_name: str) -> str:
        return os.path.join(self.sessions_dir, session_name)

    async def add_and_start_client(self, session_name: str, client: TelegramClient):
        """Добавляет уже авторизованного клиента в пул и запускает его."""
        if not client.is_connected():
            await client.connect()
        self.clients[session_name] = client
        logger.info(f"Аккаунт {session_name} успешно добавлен в пул и запущен.")

    async def get_client(self, session_name: str) -> Optional[TelegramClient]:
        """Возвращает клиента из пула по имени сессии."""
        return self.clients.get(session_name)

    async def stop_all(self):
        """Безопасно отключает всех клиентов."""
        # Используем list(), чтобы безопасно итерироваться по словарю, который может меняться
        for name, client in list(self.clients.items()):
            try:
                await client.disconnect()
                logger.info(f"Аккаунт {name} отключен.")
            except Exception as e:
                logger.error(f"Ошибка при отключении {name}: {e}")
        self.clients.clear()


client_pool = ClientPool()
import os
from typing import Dict, Optional
from telethon import TelegramClient
from app.core.config import config
from app.core.logger import logger

class ClientPool:
    def __init__(self):
        self.client: Dict[str,TelegramClient] = {}

        self.session_dir = "sessions"
        os.makedirs(self.session_dir, exist_ok=True)

    def get_session_path(self, session_name: str) -> str:
        return os.path.join(self.session_dir, session_name)

    async def add_and_start_client(self, session_name: str, client: TelegramClient):
        if not client.is_connected():
            await client.connect()
        self.client[session_name] = client
        logger.info(f"Аккаунт: {session_name} добавлен в пул и запущен")

    async def get_client(self, session_name: str) -> Optional[TelegramClient]:
        """Возвращает клиента из пула по имени сессии."""
        return self.clients.get(session_name)


    async def stop_all(self):
        """Безопасно отключает всех клиентов (вызовем при выключении бота)."""
        for name, client in self.clients.items():
            try:
                await client.disconnect()
                logger.info(f"Аккаунт {name} отключен.")
            except Exception as e:
                logger.error(f"Ошибка при отключении {name}: {e}")
        self.clients.clear()


client_pool = ClientPool()
from typing import List, Optional
from app.database.connection import get_db

class DBRepository:

    #adm
    @staticmethod
    async def is_admin(user_id: int) -> bool:
        async with get_db() as db:
            async with db.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchone() is not None

    @staticmethod
    async def add_admin(user_id: int, added_by: int):
        async with get_db() as db:
            await db.execute(
                "INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?, ?)",
                (user_id, added_by)
            )
            await db.commit()

    @staticmethod
    async def get_all_admins() -> List[int]:
        async with get_db() as db:
            async with db.execute("SELECT user_id FROM admins") as cursor:
                rows = await cursor.fetchall()
                return [row["user_id"] for row in rows]

    @staticmethod
    async def del_admin(user_id: int) -> bool:
        """Удаляет админа из БД. Возвращает True, если удален, иначе False."""
        async with get_db() as db:
            cursor = await db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
            await db.commit()
            return cursor.rowcount > 0

    #chats
    @staticmethod
    async def get_all_chats() -> List[int]:
        async with get_db() as db:
            async with db.execute("SELECT chat_id FROM chats ORDER BY chat_id") as cursor:
                rows = await cursor.fetchall()
                return [row["chat_id"] for row in rows]

    @staticmethod
    async def add_chat(chat_id: int):
        async with get_db() as db:
            await db.execute("INSERT OR IGNORE INTO chats (chat_id) VALUES (?)", (chat_id,))
            await db.commit()

    @staticmethod
    async def replace_chats(chat_ids: List[int]):
        async with get_db() as db:
            await db.execute("DELETE FROM chats")
            for cid in chat_ids:
                await db.execute("INSERT OR IGNORE INTO chats (chat_id) VALUES (?)", (cid,))
            await db.commit()


    #accounts
    @staticmethod
    async def add_account(session_name: str, phone: str):
        """Добавляет или обновляет информацию об аккаунте в БД."""
        async with get_db() as db:
            # Используем INSERT OR REPLACE, чтобы обновлять статус, если сессия перелогинивается
            await db.execute(
                "INSERT OR REPLACE INTO accounts (session_name, phone, status) VALUES (?, ?, 'active')",
                (session_name, phone)
            )
            await db.commit()

    @staticmethod
    async def get_all_accounts() -> list[dict]:
        """Возвращает список всех аккаунтов из БД."""
        async with get_db() as db:
            async with db.execute("SELECT session_name, phone, status FROM accounts") as cursor:
                rows = await cursor.fetchall()
                return [{"session_name": row["session_name"], "phone": row["phone"], "status": row["status"]} for row in
                        rows]



    #scenario
    @staticmethod
    async def clear_scenario():
        """Очищает текущий сценарий."""
        async with get_db() as db:
            await db.execute("DELETE FROM scenario")
            await db.commit()

    @staticmethod
    async def add_scenario_step(sender_tag: str, step_type: str, content: str, media_path: Optional[str] = None):
        """Добавляет один шаг в сценарий."""
        async with get_db() as db:
            await db.execute(
                "INSERT INTO scenario (sender_tag, step_type, content, media_path) VALUES (?, ?, ?, ?)",
                (sender_tag, step_type, content, media_path)
            )
            await db.commit()

    @staticmethod
    async def get_scenario() -> list[dict]:
        """Возвращает весь сценарий по порядку."""
        async with get_db() as db:
            async with db.execute("SELECT id, sender_tag, step_type, content, media_path FROM scenario ORDER BY id") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
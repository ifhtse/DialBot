from typing import List, Optional
from app.database.connection import get_db

class DBRepository:

    #adm
    @staticmethod
    async def is_admin(user_id: int) -> bool:
        async with await get_db() as db:
            async with db.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchone() is not None

    @staticmethod
    async def add_admin(user_id: int, added_by: int):
        async with await get_db() as db:
            await db.execute(
                "INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?, ?)",
                (user_id, added_by)
            )
            await db.commit()

    @staticmethod
    async def get_all_admins() -> List[int]:
        async with await get_db() as db:
            async with db.execute("SELECT user_id FROM admins") as cursor:
                rows = await cursor.fetchall()
                return [row["user_id"] for row in rows]

    #chats
    @staticmethod
    async def get_all_chats() -> List[int]:
        async with await get_db() as db:
            async with db.execute("SELECT chat_id FROM chats ORDER BY chat_id") as cursor:
                rows = await cursor.fetchall()
                return [row["chat_id"] for row in rows]

    @staticmethod
    async def add_chat(chat_id: int):
        async with await get_db() as db:
            await db.execute("INSERT OR IGNORE INTO chats (chat_id) VALUES (?)", (chat_id,))
            await db.commit()

    @staticmethod
    async def replace_chats(chat_ids: List[int]):
        async with await get_db() as db:
            await db.execute("DELETE FROM chats")
            for cid in chat_ids:
                await db.execute("INSERT OR IGNORE INTO chats (chat_id) VALUES (?)", (cid,))
            await db.commit()
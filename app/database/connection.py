import aiosqlite
from contextlib import asynccontextmanager
from app.core.config import config
from app.core.logger import logger


@asynccontextmanager
async def get_db():
    """Возвращает асинхронное подключение к БД (как контекстный менеджер)."""
    async with aiosqlite.connect(config.db_path) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_db():
    """Создает таблицы, если их нет, и добавляет супер-админа."""
    logger.info("Инициализация базы данных...")

    # ВАЖНО: Тут мы пишем просто async with get_db() as db:
    # Никаких await ПЕРЕД get_db() быть не должно!
    async with get_db() as db:
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS admins
                         (
                             user_id    INTEGER PRIMARY KEY,
                             added_by   INTEGER,
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                         )
                         """)

        await db.execute("""
                         CREATE TABLE IF NOT EXISTS accounts
                         (
                             session_name TEXT PRIMARY KEY,
                             phone        TEXT,
                             status       TEXT      DEFAULT 'active',
                             created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                         )
                         """)

        await db.execute("""
                         CREATE TABLE IF NOT EXISTS chats
                         (
                             chat_id INTEGER PRIMARY KEY,
                             status  TEXT DEFAULT 'waiting'
                         )
                         """)

        await db.execute("""
                         CREATE TABLE IF NOT EXISTS scenario
                         (
                             id         INTEGER PRIMARY KEY AUTOINCREMENT,
                             sender_tag TEXT,
                             step_type  TEXT,
                             content    TEXT,
                             media_path TEXT
                         )
                         """)

        await db.execute("""
                         CREATE TABLE IF NOT EXISTS settings
                         (
                             key   TEXT PRIMARY KEY,
                             value TEXT
                         )
                         """)

        await db.execute("""
                         CREATE TABLE IF NOT EXISTS global_stats
                         (
                             id            INTEGER PRIMARY KEY CHECK (id = 1),
                             chats_done    INTEGER DEFAULT 0,
                             chats_skipped INTEGER DEFAULT 0,
                             messages_sent INTEGER DEFAULT 0,
                             errors        INTEGER DEFAULT 0
                         )
                         """)
        await db.execute("INSERT OR IGNORE INTO global_stats (id) VALUES (1)")

        await db.execute(
            "INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?, ?)",
            (config.main_admin_id, 0)
        )

        await db.commit()
    logger.info("База данных готова.")
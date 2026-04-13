import aiosqlite
from app.core.config import config
from app.core.logger import logger

async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(config.db_path)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
    logger.info("Инициализация ДБ")

    async with await get_db() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins
            (
                user_id    INTEGER PRIMARY KEY,
                added_by   INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            )
            """)
        # Таблица аккаунтов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS accounts
        (
            session_name TEXT PRIMARY KEY,
            phone        TEXT,
            status       TEXT      DEFAULT 'active',
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
                         )

        # Таблица целевых чатов
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS chats
                         (
                             chat_id INTEGER PRIMARY KEY,
                             status  TEXT DEFAULT 'waiting'
                         )
                         """)

        # Таблица сценария
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS scenario
                         (
                             id         INTEGER PRIMARY KEY AUTOINCREMENT,
                             sender_tag TEXT, -- например "account_1" или "account_2"
                             step_type  TEXT, -- "text" или "photo"
                             content    TEXT,
                             media_path TEXT  -- путь к картинке, если step_type == "photo"
                         )
                         """)

        # Глобальные настройки (задержки и т.д.)
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS settings
                         (
                             key   TEXT PRIMARY KEY,
                             value TEXT
                         )
                         """)

        # Статистика
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
    logger.info("BD is all set")
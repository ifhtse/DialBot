from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str
    api_id: int
    api_hash: str
    main_admin_id: int

    db_path: str = "dobav'potom.db"
    log_file_path: str = "bot_logs.log"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Settings()
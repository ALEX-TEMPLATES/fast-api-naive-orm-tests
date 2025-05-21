from pydantic_settings import BaseSettings, SettingsConfigDict


# Класс настроек приложения
class Settings(BaseSettings):
    # Строка подключения к БД для psycopg3
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Экземпляр настроек
settings = Settings()

import asyncio
import sys
from pathlib import Path

import psycopg

# Добавляем путь к src в PYTHONPATH
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

# Теперь можем импортировать из app
from app.config.settings import settings  # noqa: E402

# Скрипт для создания таблицы Example через psycopg3


async def main():
    # Преобразуем URL SQLAlchemy в формат psycopg
    db_url = settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")

    # Подключаемся к базе данных
    async with await psycopg.AsyncConnection.connect(db_url) as aconn:
        async with aconn.cursor() as cur:
            # Создаём таблицу Example
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS example (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        modified_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    )
            """)
            print("Таблица Example успешно создана!")


if __name__ == "__main__":
    asyncio.run(main())

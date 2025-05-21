import asyncio
import sys
from pathlib import Path

import psycopg

# Добавляем путь к src в PYTHONPATH
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from app.config.settings import settings  # noqa: E402

# Скрипт для удаления таблицы Example


async def main():
    # Преобразуем URL SQLAlchemy в формат psycopg
    db_url = settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")

    # Подключаемся к базе данных
    async with await psycopg.AsyncConnection.connect(db_url) as aconn:
        async with aconn.cursor() as cur:
            # Удаляем таблицу Example, если она существует
            await cur.execute("""
                DROP TABLE IF EXISTS example
            """)
            print("Таблица Example успешно удалена!")


if __name__ == "__main__":
    asyncio.run(main())

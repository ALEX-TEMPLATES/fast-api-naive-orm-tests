# 04. Управление Миграциями Базы Данных с Alembic

В этом проекте Alembic используется для управления изменениями схемы базы данных. Это позволяет отслеживать версии схемы, применять и откатывать изменения контролируемым образом.

## Структура Alembic

Основные компоненты конфигурации Alembic находятся в директории `src/alembic/`:

*   **`alembic.ini`**: Главный конфигурационный файл Alembic. Указывает на расположение других файлов и содержит настройки, такие как URL базы данных (хотя в нашем проекте URL базы данных устанавливается динамически в `env.py`).
*   **`env.py`**: Скрипт, который запускается при выполнении команд Alembic. Он отвечает за настройку окружения для миграций, включая:
    *   Определение `target_metadata` – объекта `MetaData` SQLAlchemy, который Alembic сравнивает с текущим состоянием базы данных для автогенерации миграций.
    *   Настройку URL базы данных, получаемого из переменных окружения (`settings.DATABASE_URL`).
*   **`script.py.mako`**: Шаблон для генерации новых файлов миграций.
*   **`versions/`**: Директория, где хранятся все файлы ревизий (миграций). Каждый файл представляет собой одно изменение схемы.

## Автогенерация Миграций и Импорт Моделей

Ключевым моментом для успешной автогенерации миграций (`alembic revision --autogenerate ...`) является правильная настройка `target_metadata` в `src/alembic/env.py`.

### `target_metadata`

В `env.py` строка `target_metadata = Base.metadata` указывает Alembic на метаданные, связанные с вашим базовым классом моделей SQLAlchemy (`app.schemas.base.Base`). Alembic будет искать все таблицы, зарегистрированные с этим объектом `MetaData`.

### Важность Импорта Моделей

Чтобы `Base.metadata` содержал информацию обо всех ваших таблицах (например, `Example`), **все модули, определяющие ваши модели SQLAlchemy, должны быть импортированы до того, как `target_metadata = Base.metadata` будет прочитано Alembic.**

1.  **Централизованный Экспорт Моделей:**
    В нашем проекте файл `src/app/schemas/__init__.py` используется для импорта и экспорта всех основных сущностей схем, включая `Base` и все модели таблиц (например, `Example`):
    ```python
    # src/app/schemas/__init__.py
    from .base import Base
    from .example import Example # И другие ваши модели

    __all__ = [
        "Base",
        "Example",
        # ... другие модели
    ]
    ```

2.  **Импорт в `env.py`:**
    Затем в `src/alembic/env.py` мы импортируем все из `app.schemas`:
    ```python
    # src/alembic/env.py
    # ...
    from app.schemas import *  # noqa: F403
    # ...
    target_metadata = Base.metadata
    # ...
    ```
    Это гарантирует, что Python выполнит код определения всех ваших моделей, и они зарегистрируются с `Base.metadata`.

### Замечание о `Base` и `DeclarativeBase`

Ранее мы столкнулись с проблемой, когда автогенерация не работала. Это было связано с тем, что в классе `Base(DeclarativeBase)` происходило переопределение атрибута `metadata` новым экземпляром `MetaData`.
Правильный подход при использовании `class Base(DeclarativeBase):` (стиль SQLAlchemy 2.0+) — это позволить `Base` использовать `metadata`, унаследованный от `DeclarativeBase`. Если требуется настроить `naming_convention`, это следует делать через `sqlalchemy.orm.registry` при создании базового класса, как обсуждалось ранее. В текущей конфигурации мы просто не переопределяем `metadata` в `Base`, что позволяет моделям корректно регистрироваться.

## Рабочий Процесс Миграций

Для удобства в `Makefile` добавлены команды для управления миграциями:

1.  **Создание новой миграции (с автогенерацией):**
    ```bash
    make mm "ваше_сообщение_о_миграции"
    ```
    Например:
    ```bash
    make mm "add_user_profile_table"
    ```
    Эта команда выполнит `(cd src && alembic revision -m "ваше_сообщение" --autogenerate)`. Alembic сравнит `Base.metadata` с состоянием базы данных и сгенерирует новый файл ревизии в `src/alembic/versions/` с предложенными изменениями схемы. **Всегда проверяйте сгенерированный файл миграции перед применением!**

2.  **Применение миграций:**
    ```bash
    make uh
    ```
    Эта команда выполнит `(cd src && alembic upgrade head)`, применяя все непримененные миграции к базе данных до последней доступной ревизии.

## Типичные Проблемы

*   **Модель не обнаружена Alembic:**
    *   Убедитесь, что модуль, определяющий вашу модель, импортируется в `src/app/schemas/__init__.py` и экспортируется через `__all__`.
    *   Убедитесь, что `from app.schemas import *` (или эквивалентный явный импорт модели) присутствует в `src/alembic/env.py` *до* строки `target_metadata = Base.metadata`.
    *   Убедитесь, что ваша модель наследуется от `Base`.
*   **Пустой файл миграции:** Обычно это симптом одной из вышеуказанных проблем с импортом или неправильной конфигурацией `target_metadata`.

Следуя этим указаниям, вы сможете эффективно управлять схемой вашей базы данных.

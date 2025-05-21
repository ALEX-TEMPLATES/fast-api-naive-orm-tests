# База Данных, ACID и Unit of Work (UoW)

## Настройка Базы Данных

Проект использует PostgreSQL в качестве системы управления базами данных, что видно из зависимостей `psycopg` (асинхронный драйвер для PostgreSQL) и `alembic-postgresql-enum` в `pyproject.toml`.

-   **SQLAlchemy**: Используется как ORM (Object-Relational Mapper) для взаимодействия с базой данных. Модели таблиц определяются в `src/app/schemas/`.
    -   `src/app/schemas/base.py`: Содержит базовую модель `Base` с общими полями (`created_at`, `modified_at`) и конфигурацией метаданных.
    -   `src/app/schemas/example.py`: Пример модели `Example`.
-   **Alembic**: Инструмент для управления миграциями схемы базы данных. Позволяет отслеживать изменения в моделях SQLAlchemy и применять их к БД. Конфигурация Alembic обычно находится в `alembic.ini` и директории `alembic/` (не показаны, но подразумеваются при использовании Alembic).
-   **Конфигурация Соединения**: Параметры подключения к базе данных (хост, порт, имя пользователя, пароль, имя БД) обычно задаются через переменные окружения и используются для создания URL подключения в `src/app/config/db.py` (в функции `create_async_engine`).

## Unit of Work (UoW)

Паттерн Unit of Work (Единица Работы) используется для группировки одной или нескольких операций с базой данных (чтение, запись, удаление) в единую транзакцию. Это помогает обеспечить целостность данных.

В проекте `SqlAlchemyUnitOfWork` реализован в `src/app/config/db.py`:

```python
# src/app/config/db.py (фрагмент)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ... (DATABASE_URL, create_async_engine, async_session_factory)

class SqlAlchemyUnitOfWork:
    session: AsyncSession

    def __init__(self, session_factory: async_sessionmaker[AsyncSession] = async_session_factory):
        self._session_factory = session_factory

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        try:
            await self.session.commit()
        except Exception:
            await self.rollback()
            raise

    async def rollback(self):
        await self.session.rollback()
```

### Как это работает:

1.  **Создание сессии**: При входе в контекстный менеджер (`async with SqlAlchemyUnitOfWork() as uow:`), создается новая `AsyncSession`.
2.  **Выполнение операций**: Все операции с базой данных внутри блока `async with` используют эту сессию (`uow.session`). Например, `ExampleDAO.create(uow.session, data)`.
3.  **Commit или Rollback**:
    -   Если все операции внутри блока успешны и вызывается `await uow.commit()`, изменения фиксируются в базе данных.
    -   Если возникает исключение внутри блока `async with` или при вызове `uow.commit()`, происходит автоматический откат (`await self.rollback()`) всех изменений, сделанных в рамках этой сессии.
    -   Сессия закрывается при выходе из блока `__aexit__`.

**Использование в сервисном слое:**

```python
# src/app/services/example.py
class ExampleService:
    @staticmethod
    async def create(data: ExampleCreateDTO) -> ExampleDTO:
        async with SqlAlchemyUnitOfWork() as uow: # Начало транзакции
            example_dto = await ExampleDAO.create(uow.session, data)
            await uow.commit() # Фиксация транзакции
            return example_dto
```

## Принципы ACID и UoW

Паттерн Unit of Work вместе с транзакционными возможностями СУБД помогает придерживаться принципов ACID:

-   **Atomicity (Атомарность)**:
    -   UoW гарантирует, что все операции (добавление, изменение, удаление объектов), выполненные в рамках одной "единицы работы" (внутри блока `async with` и до `commit`), либо все успешно завершаются (commit), либо все отменяются (rollback). Нет частичного применения изменений.

-   **Consistency (Согласованность)**:
    -   База данных переходит из одного согласованного состояния в другое.
    -   SQLAlchemy модели с их типами данных и ограничениями, а также валидация на уровне DTO, помогают обеспечить запись корректных данных.
    -   Транзакции предотвращают оставление базы данных в промежуточном, невалидном состоянии.

-   **Isolation (Изолированность)**:
    -   Каждая транзакция (управляемая UoW) выполняется так, как будто других параллельных транзакций не существует. Уровень изоляции (например, Read Committed, Serializable) обычно настраивается на уровне СУБД.
    -   SQLAlchemy сессия предоставляет кэш первого уровня, что также способствует изоляции в рамках одной сессии.

-   **Durability (Долговечность)**:
    -   После успешного выполнения `uow.commit()`, изменения, сделанные транзакцией, постоянно сохраняются в базе данных и не будут потеряны даже в случае сбоя системы (благодаря механизмам журналирования и восстановления СУБД).

Использование `SqlAlchemyUnitOfWork` упрощает управление транзакциями и сессиями, делая код более чистым и надежным, а также явно следуя принципам ACID для операций с базой данных.

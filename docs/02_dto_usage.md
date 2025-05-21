# Использование DTO (Data Transfer Objects) между слоями

Data Transfer Objects (DTO) играют ключевую роль в поддержании чистой архитектуры, обеспечивая структурированную и валидированную передачу данных между различными слоями приложения. В данном проекте DTO реализованы с использованием Pydantic.

## Основные Задачи DTO

1.  **Передача данных**: DTO служат контейнерами для данных, передаваемых, например, от API-слоя к сервисному, и далее к DAO-слою.
2.  **Валидация**: Pydantic автоматически валидирует типы и ограничения данных при создании экземпляра DTO.
3.  **Сериализация/Десериализация**: FastAPI использует Pydantic модели для автоматической сериализации ответов в JSON и десериализации JSON из запросов в DTO.
4.  **Контракт данных**: DTO определяют четкий контракт данных между слоями, уменьшая их связанность.

## Пример Использования в Проекте (`Example`)

Рассмотрим на примере сущности `Example`.

### 1. Определения DTO (`src/app/dto/example.py`)

```python
# src/app/dto/base.py
from pydantic import BaseModel, ConfigDict

class BaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# src/app/dto/example.py
from datetime import datetime
from app.dto.base import BaseDTO

class ExampleCreateDTO(BaseDTO):
    """DTO для создания новой записи Example."""
    name: str

class ExampleDTO(BaseDTO):
    """DTO для полного представления записи Example."""
    id: int
    name: str
    created_at: datetime
```

-   `BaseDTO`: Базовый DTO, от которого наследуются остальные. `model_config = ConfigDict(from_attributes=True)` позволяет Pydantic моделям создаваться из атрибутов объектов (например, SQLAlchemy моделей).
-   `ExampleCreateDTO`: Используется для передачи данных, необходимых для создания новой записи `Example`. Содержит только поле `name`.
-   `ExampleDTO`: Используется для представления уже существующей записи `Example`, включая системные поля, такие как `id` и `created_at`.

### 2. Поток Данных при Создании Записи

1.  **API Layer (`src/app/api/example.py`)**:
    -   Эндпоинт `POST /examples/` принимает `ExampleCreateDTO` в теле запроса.
    -   FastAPI автоматически десериализует JSON в объект `ExampleCreateDTO` и валидирует его.
    ```python
    @router.post("/", response_model=ExampleDTO)
    async def create_example(data: ExampleCreateDTO):
        return await ExampleService.create(data)
    ```

2.  **Services Layer (`src/app/services/example.py`)**:
    -   Метод `ExampleService.create` принимает `ExampleCreateDTO` от API слоя.
    -   Передает этот DTO в DAO слой.
    ```python
    @staticmethod
    async def create(data: ExampleCreateDTO) -> ExampleDTO:
        async with SqlAlchemyUnitOfWork() as uow:
            # 'data' (ExampleCreateDTO) передается в DAO
            example_dto_from_dao = await ExampleDAO.create(uow.session, data)
            await uow.commit()
            return example_dto_from_dao # DAO уже вернул ExampleDTO
    ```

3.  **DAO Layer (`src/app/dao/example.py`)**:
    -   Метод `ExampleDAO.create` принимает `ExampleCreateDTO`.
    -   Использует `example_dto.model_dump()` для преобразования DTO в словарь, который затем распаковывается для создания экземпляра SQLAlchemy модели `Example`.
    -   После сохранения в БД, SQLAlchemy модель `new_example` преобразуется обратно в `ExampleDTO` с помощью `ExampleDTO.model_validate(new_example)` перед возвратом в сервисный слой.
    ```python
    @staticmethod
    async def create(session: AsyncSession, example_dto: ExampleCreateDTO) -> ExampleDTO:
        new_example = Example(**example_dto.model_dump()) # DTO -> SQLAlchemy Model
        session.add(new_example)
        await session.commit()
        await session.refresh(new_example)
        return ExampleDTO.model_validate(new_example) # SQLAlchemy Model -> DTO
    ```

### 3. Поток Данных при Чтении Записей

1.  **DAO Layer (`src/app/dao/example.py`)**:
    -   Метод `ExampleDAO.get_all` извлекает список SQLAlchemy моделей `Example`.
    -   Каждая модель преобразуется в `ExampleDTO` с помощью `ExampleDTO.model_validate(e)`.
    ```python
    @staticmethod
    async def get_all(session: AsyncSession) -> list[ExampleDTO]:
        result = await session.execute(select(Example))
        examples_models = result.scalars().all()
        return [ExampleDTO.model_validate(e) for e in examples_models]
    ```

2.  **Services Layer (`src/app/services/example.py`)**:
    -   Метод `ExampleService.get_all` получает список `ExampleDTO` от DAO и возвращает его API слою.
    ```python
    @staticmethod
    async def get_all() -> list[ExampleDTO]:
        async with SqlAlchemyUnitOfWork() as uow:
            examples_dto_list = await ExampleDAO.get_all(uow.session)
            return examples_dto_list
    ```

3.  **API Layer (`src/app/api/example.py`)**:
    -   Эндпоинт `GET /examples/` возвращает список `ExampleDTO`.
    -   FastAPI автоматически сериализует список DTO в JSON ответ.
    ```python
    @router.get("/", response_model=list[ExampleDTO])
    async def get_examples():
        return await ExampleService.get_all()
    ```

Таким образом, DTO обеспечивают четкий и типизированный способ обмена данными между слоями, упрощая разработку, тестирование и поддержку приложения.

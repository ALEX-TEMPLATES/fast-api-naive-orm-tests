# Руководство по настройке тестирования с pytest

Это подробный пошаговый план для интеграции и запуска тестов в этом проекте с использованием pytest.

## 1. Установка зависимостей

1. Откройте `pyproject.toml` и добавьте в секцию `[project.optional-dependencies.dev]`:
   ```toml
   [project.optional-dependencies.dev]
   pytest = "^7.4"
   pytest-asyncio = "^0.21"
   pytest-cov = "^4.0"
   pytest-dotenv = "^0.7"
   ```
2. Установите dev-зависимости:
   ```bash
   # если используете uv
   uv sync
   # или pip
   pip install -e .[dev]
   ```

## 2. Структура каталогов для тестов

Создайте новый каталог `tests` на одном уровне с `app` внутри `src`:
```bash
mkdir -p src/tests/unit/api \
         src/tests/unit/dao \
         src/tests/unit/services \
         src/tests/integration
```  
Получится такая структура:
```
src/
├─ app/
└─ tests/
   ├─ unit/
   │  ├─ api/
   │  ├─ dao/
   │  └─ services/
   └─ integration/
```

## 3. Конфигурация pytest через pyproject.toml

В файл `pyproject.toml` добавьте секцию:
```toml
[tool.pytest.ini_options]
minversion = "6.0"
testpaths = ["src/tests"]
asyncio_default_fixture_loop_scope = "session"
asyncio_default_test_loop_scope ="session"
asyncio_mode = "auto"
addopts = "-ra -q" 
markers = [
  "unit: unit tests",
  "integration: integration tests",
]
env_files = [".env"]
```

## 4. Общий `conftest.py`

Создайте файл `src/conftest.py` со следующим содержимым:
```python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

from app.main import app
from app.config.settings import settings
from app.schemas.base import Base

@pytest.fixture(scope="session", autouse=True)
def load_env():
    # pytest-dotenv автоматически загрузит .env
    pass

@pytest.fixture
def client():
    return TestClient(app)

# ---- Unit DB: PostgreSQL (production-like) ----
@pytest.fixture
async def unit_db_session(run_migrations):
    """Использует тестовую Postgres и применяет все миграции один раз."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    session = AsyncSessionLocal()
    yield session
    await session.close()

# ---- Integration DB: PostgreSQL ----
@pytest.fixture(scope="session")
def alembic_cfg():
    return Config("src/alembic.ini")

@pytest.fixture(scope="session")
def run_migrations(alembic_cfg):
    command.upgrade(alembic_cfg, "head")

@pytest.fixture(scope="session", autouse=False)
async def integration_db_session(run_migrations):
    engine = create_async_engine(
        settings.DATABASE_URL, echo=False
    )
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    session = AsyncSessionLocal()
    yield session
    await session.close()
```

## 5. Unit-тесты

### 5.1 Тесты API

Создайте файл `src/tests/unit/api/test_example_api.py`:
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "API работает!", "status": "ok"}
```

### 5.2 Тесты DAO

Создайте файл `src/tests/unit/dao/test_example_dao.py`:
```python
import pytest
from app.dao.example import ExampleDAO
from app.dto.example import ExampleCreateDTO

@pytest.mark.asyncio
async def test_create_and_get_all(unit_db_session):
    dto = ExampleCreateDTO(name="test_item")
    created = await ExampleDAO.create(unit_db_session, dto)
    assert created.id == 1
    items = await ExampleDAO.get_all(unit_db_session)
    assert len(items) == 1
    assert items[0].name == "test_item"
```

### 5.3 Тесты Service

Создайте файл `src/tests/unit/services/test_example_service.py`:
```python
import pytest
from app.services.example import ExampleService
from app.dto.example import ExampleCreateDTO
from app.config.db import SqlAlchemyUnitOfWork

@pytest.mark.asyncio
async def test_service_create_and_list(unit_db_session, monkeypatch):
    # Заменяем фабрику сессий на фиктивную
    monkeypatch.setattr(
        SqlAlchemyUnitOfWork, "_session_factory", lambda: unit_db_session
    )
    dto = ExampleCreateDTO(name="svc_test")
    created = await ExampleService.create(dto)
    assert created.name == "svc_test"
    items = await ExampleService.get_all()
    assert any(i.name == "svc_test" for i in items)
```

## 6. Integration-тесты

Создайте файл `src/tests/integration/test_full_flow.py`:
```python
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

@pytest.mark.integration
async def test_full_flow(integration_db_session):
    # Создание через API
    resp1 = client.post("/examples/", json={"name": "integ_item"})
    assert resp1.status_code == 200
    data = resp1.json()
    assert data["name"] == "integ_item"

    # Чтение через API
    resp2 = client.get("/examples/")
    assert resp2.status_code == 200
    assert any(e["name"] == "integ_item" for e in resp2.json())
```

## 7. Запуск тестов

В корне проекта выполните:
```bash
pytest -v
```

## 8. Итоги и советы

- Unit-тесты изолированы: быстрые, без внешних сервисов.
- Integration-тесты используют реальную БД (миграции, откат).
- Маркеры `unit` и `integration` позволяют запускать выборочно:
  ```bash
  pytest -m unit
  pytest -m integration
  ```
- Используйте `pytest-cov` для отчёта покрытия.

Теперь даже джуниор сможет настроить и запустить полный цикл тестирования с помощью pytest!

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config.settings import settings
from app.schemas.base import Base


# маленькая тестовая фикстура для примера
@pytest.fixture
async def sample_data():
    return "hello pytest"


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    # разово создаём схемы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    # разово удаляем схемы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
async def connection(engine):
    async with engine.connect() as conn:
        tx = await conn.begin()
        yield conn
        await tx.rollback()


@pytest.fixture
async def unit_db_session(connection):
    # для каждого теста открываем SAVEPOINT
    nested = await connection.begin_nested()
    session = AsyncSession(bind=connection, expire_on_commit=False)
    yield session
    await session.close()
    await nested.rollback()

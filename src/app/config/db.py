import logging
from contextlib import AbstractAsyncContextManager
from typing import Any, AsyncGenerator, Callable

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import settings

from .uow import IUnitOfWork

SessionFactory = Callable[..., AbstractAsyncContextManager[AsyncSession]]

# Создаём движок один раз с фиксированным пулом
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,  # Максимум 5 соединений
    max_overflow=0,  # Не создавать дополнительные соединения
    pool_timeout=30,  # Таймаут ожидания соединения
    pool_pre_ping=True,  # Проверять соединение перед использованием
    echo=False,  # Отключить SQL-лог
)


# Создаём фабрику сессий один раз
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Зависимость FastAPI для получения сессии
async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session_factory() as session:
        yield session


def get_db_session() -> AsyncSession:
    return async_session_factory()


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self):
        self._session_factory = get_db_session
        self._session: AsyncSession | None = None

    def _ensure_session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Session is not initialized")
        return self._session

    async def __aenter__(self):
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
            logging.error(f"Exception in UnitOfWork: {exc_val}")
            session = self._ensure_session()
            await session.close()
            raise exc_val
        session = self._ensure_session()
        await session.close()

    async def commit(self):
        session = self._ensure_session()
        await session.commit()

    async def rollback(self):
        session = self._ensure_session()
        await session.rollback()

    @property
    def session(self) -> AsyncSession:
        return self._ensure_session()

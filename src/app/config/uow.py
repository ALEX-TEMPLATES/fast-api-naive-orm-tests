from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class IUnitOfWork(ABC):
    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def __aenter__(self) -> "IUnitOfWork":
        return self

    @abstractmethod
    async def __aexit__(self, *args) -> None:
        await self.rollback()

    @property
    @abstractmethod
    def session(self) -> AsyncSession:
        raise NotImplementedError

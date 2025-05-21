from app.config.db import SqlAlchemyUnitOfWork
from app.dao.example import ExampleDAO
from app.dto.example import ExampleCreateDTO, ExampleDTO


class ExampleService:
    """
    Сервисный слой для работы с примерами.
    Содержит бизнес-логику и использует DAO для работы с БД.
    """

    @staticmethod
    async def create(data: ExampleCreateDTO) -> ExampleDTO:
        async with SqlAlchemyUnitOfWork() as uow:
            example = await ExampleDAO.create(uow.session, data)
            await uow.commit()
            return example

    @staticmethod
    async def get_all() -> list[ExampleDTO]:
        async with SqlAlchemyUnitOfWork() as uow:
            examples = await ExampleDAO.get_all(uow.session)
            return examples

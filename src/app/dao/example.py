from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.example import ExampleCreateDTO, ExampleDTO
from app.schemas import Example


class ExampleDAO:
    """
    Data Access Object для работы с Example.
    Инкапсулирует все взаимодействия с SQLAlchemy.
    """

    @staticmethod
    async def create(
        session: AsyncSession,
        example_dto: ExampleCreateDTO,
    ) -> ExampleDTO:
        # Создаем новый пример
        new_example = Example(**example_dto.model_dump())
        session.add(new_example)
        await session.commit()
        await session.refresh(new_example)
        return ExampleDTO.model_validate(new_example)

    @staticmethod
    async def get_all(session: AsyncSession) -> list[ExampleDTO]:
        # Получаем все записи
        result = await session.execute(select(Example))
        examples = result.scalars().all()
        return [ExampleDTO.model_validate(e) for e in examples]

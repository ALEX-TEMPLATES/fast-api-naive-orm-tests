import pytest

from app.dao.example import ExampleDAO
from app.dto.example import ExampleCreateDTO


@pytest.mark.asyncio
async def test_example_dao_create_and_get_all(unit_db_session):
    dto1 = ExampleCreateDTO(name="test_item1")
    dto2 = ExampleCreateDTO(name="test_item2")
    created1 = await ExampleDAO.create(unit_db_session, dto1)
    created2 = await ExampleDAO.create(unit_db_session, dto2)
    assert created1.name == "test_item1"
    assert created2.name == "test_item2"
    items = await ExampleDAO.get_all(unit_db_session)
    assert len(items) == 2
    assert {i.name for i in items} == {"test_item1", "test_item2"}

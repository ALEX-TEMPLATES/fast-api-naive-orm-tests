from fastapi import APIRouter

from app.dto.example import ExampleCreateDTO, ExampleDTO
from app.services.example import ExampleService

router = APIRouter()


@router.post("/", response_model=ExampleDTO)
async def create_example(data: ExampleCreateDTO):
    """Создание новой записи Example"""
    return await ExampleService.create(data)


@router.get("/", response_model=list[ExampleDTO])
async def get_examples():
    """Получение всех записей Example"""
    return await ExampleService.get_all()

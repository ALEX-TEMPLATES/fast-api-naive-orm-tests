"""
Базовый класс для всех DTO объектов.
"""
from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """Базовый класс для всех DTO в приложении."""
    
    model_config = ConfigDict(
        frozen=True,  # Делает объекты неизменяемыми
        from_attributes=True,  # Позволяет создавать модели из ORM объектов
        populate_by_name=True  # Использует имена, а не алиасы для сопоставления
    )
